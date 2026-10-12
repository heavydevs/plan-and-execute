#!/usr/bin/env python3
"""Durable, detached command jobs; bounded waits never consume a model session."""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import json
import math
import os
import re
import secrets
import signal
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Any

import process_tree
from progress_watch import ProgressMonitor, ProgressState, validate_policy

VERSION = 1
MAX_RECORD_BYTES = 262144
ACTIVE = {"starting", "running"}
TERMINAL = {"succeeded", "failed", "stalled", "stopped"}
ENVIRONMENT_FAILURES = {
    "service_map_invalid", "validation_not_mapped", "probe_cleanup_unavailable",
    "health_check_failed", "toolchain_unavailable", "test_command_unavailable", "configuration_error",
}
SECRET_ARGUMENT = re.compile(
    r"(?i)(?:--?(?:api[-_]?key|access[-_]?token|refresh[-_]?token|password|passwd|secret|token)(?:[=\s]|$)"
    r"|(?:api[-_]?key|access[-_]?token|refresh[-_]?token|password|passwd|secret|token)\s*[:=]"
    r"|\b(?:Bearer|Basic)\s+\S+|\b(?:sk-[A-Za-z0-9_-]{12,}|gh[pousr]_[A-Za-z0-9]{12,}|AKIA[A-Z0-9]{16})"
    r"|[a-z][a-z0-9+.-]*://[^\s/:]+:[^\s/@]+@)"
)


class JobError(ValueError):
    pass


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def safe_id(value: str) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", value) is None:
        raise JobError("Invalid job id; use 1..64 letters, digits, underscores or hyphens")
    if value.split(".", 1)[0].upper() in {"CON", "PRN", "AUX", "NUL", *[f"COM{i}" for i in range(1, 10)], *[f"LPT{i}" for i in range(1, 10)]}:
        raise JobError("Reserved job id")
    return value


def checked_path(root: Path, *parts: str) -> Path:
    root = Path(os.path.abspath(root))
    current = Path(root.anchor)
    for part in (*root.parts[1:], *parts):
        current = current / part
        if current.is_symlink() or getattr(current, "is_junction", lambda: False)():
            raise JobError("Job paths must not be symlinks")
    return current


def job_dir(plan_dir: Path | str, job_id: str) -> Path:
    root = Path(plan_dir).expanduser()
    if not root.is_dir():
        raise JobError("Plan directory does not exist")
    return checked_path(root, "jobs", safe_id(job_id))


def read_record(path: Path) -> dict[str, Any]:
    if path.is_symlink():
        raise JobError("Job records must not be symlinks")
    try:
        for attempt in range(30):
            try:
                with path.open("rb") as source:
                    data = source.read(MAX_RECORD_BYTES + 1)
                break
            except PermissionError:
                # Atomic replacement can briefly deny a Windows reader access.
                # Retry access only; malformed JSON still fails immediately below.
                if attempt == 29:
                    raise
                time.sleep(0.01)
        if len(data) > MAX_RECORD_BYTES:
            raise ValueError("oversized")
        value = json.loads(data)
        if not isinstance(value, dict):
            raise ValueError("invalid")
        return value
    except FileNotFoundError:
        return {}
    except (OSError, ValueError) as exc:
        raise JobError("Invalid job record; preserve it before repairing") from exc


def write_record(path: Path, value: dict[str, Any]) -> None:
    checked_path(path.parent, path.name)
    descriptor, filename = tempfile.mkstemp(prefix=".record-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as output:
            json.dump(value, output, ensure_ascii=False, separators=(",", ":"))
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        for attempt in range(30):
            try:
                os.replace(filename, path)
                break
            except PermissionError:
                # Windows readers may briefly deny deletion sharing on the old record.
                if attempt == 29:
                    raise
                time.sleep(0.01)
    finally:
        Path(filename).unlink(missing_ok=True)


def pid_identity(pid: int) -> str | None:
    if pid <= 0:
        return None
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.GetProcessTimes.argtypes = [wintypes.HANDLE, *([ctypes.POINTER(wintypes.FILETIME)] * 4)]
        kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        handle = kernel.OpenProcess(0x1000, False, pid)
        if not handle:
            return None
        try:
            code = wintypes.DWORD()
            if not kernel.GetExitCodeProcess(handle, ctypes.byref(code)) or code.value != 259:
                return None
            times = [wintypes.FILETIME() for _ in range(4)]
            if kernel.GetProcessTimes(handle, *[ctypes.byref(item) for item in times]):
                return str((times[0].dwHighDateTime << 32) | times[0].dwLowDateTime)
            return None
        finally:
            kernel.CloseHandle(handle)
    return posix_pid_identity(pid)


def posix_pid_identity(pid: int) -> str | None:
    try:
        text = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8")
        fields = text[text.rfind(")") + 2:].split()
        return None if fields[0] == "Z" else fields[19]
    except (OSError, IndexError):
        try:
            output = subprocess.run(["ps", "-p", str(pid), "-o", "lstart=", "-o", "stat="],
                                    capture_output=True, text=True, encoding="utf-8", timeout=2, check=False)
            fields = output.stdout.split()
            return " ".join(fields[:-1]) if output.returncode == 0 and len(fields) >= 2 and not fields[-1].startswith("Z") else None
        except (OSError, subprocess.TimeoutExpired):
            return None


def owner_live(record: dict[str, Any], prefix: str) -> bool:
    pid, identity = record.get(prefix + "_pid"), record.get(prefix + "_identity")
    return type(pid) is int and isinstance(identity, str) and pid_identity(pid) == identity


@contextlib.contextmanager
def job_lock(directory: Path):
    """Kernel locks release on crashes; stale files never require unsafe lock stealing."""
    path = checked_path(directory, ".start-lock")
    descriptor = os.open(path, os.O_RDWR | os.O_CREAT, 0o600)
    deadline = time.monotonic() + 10
    acquired = False
    try:
        try:
            if os.fstat(descriptor).st_size == 0:
                os.write(descriptor, b"\0")
        except OSError:
            pass  # a concurrent starter already holds (and so wrote or locked) the byte
        while not acquired:
            try:
                if os.name == "nt":
                    import msvcrt
                    os.lseek(descriptor, 0, os.SEEK_SET)
                    msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
                acquired = True
            except OSError:
                if time.monotonic() >= deadline:
                    raise JobError("Job start is already in progress")
                time.sleep(0.05)
        yield
    finally:
        if acquired:
            if os.name == "nt":
                import msvcrt
                os.lseek(descriptor, 0, os.SEEK_SET)
                msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def current_run(directory: Path) -> tuple[Path, dict[str, Any]]:
    pointer = read_record(checked_path(directory, "current.json"))
    nonce = pointer.get("nonce")
    if not isinstance(nonce, str) or re.fullmatch(r"[a-f0-9]{32}", nonce) is None:
        raise JobError("Job has no valid current generation")
    return checked_path(directory, "runs", nonce), pointer


def status_job(plan_dir: Path | str, job_id: str) -> dict[str, Any]:
    directory = job_dir(plan_dir, job_id)
    if not directory.is_dir():
        raise JobError("Job has not been started")
    run, pointer = current_run(directory)
    request = read_record(checked_path(run, "request.json"))
    state = read_record(checked_path(run, "state.json"))
    if state and (state.get("nonce") != pointer["nonce"] or state.get("status") not in ACTIVE | TERMINAL):
        raise JobError("Invalid job state")
    record = state or {key: request.get(key) for key in ("version", "id", "nonce", "fingerprint", "argv", "cwd", "started_at", "idle_timeout_seconds", "hard_timeout_seconds", "validation_id", "map_path", "validation_fingerprint")}
    record = {**record, "status": record.get("status", "starting"), "log_path": str(run / "output.log")}
    if record["status"] in ACTIVE:
        launch = read_record(checked_path(run, "launch.json"))
        failure = read_record(checked_path(run, "launch-failure.json"))
        abandoned_start = (not state and not launch and request.get("dispatch_requested") is not True
                           and time.time() - float(request.get("started_unix", 0)) > 10)
        owner = state if state else launch or request
        prefix = "supervisor" if state or launch else "starter"
        if failure or abandoned_start or not owner_live(owner, prefix):
            record.update(status="failed", exit_code=1, reason="supervisor_start_failed" if failure or abandoned_start else "supervisor_lost")
        elif state:
            saved = float(state.get("observed_at", time.time()))
            record["idle_seconds"] = max(0.0, float(state.get("idle_seconds", 0)) + max(0.0, time.time() - saved))
    record["state"] = "ceiling" if record.get("reason") == "hard" else "lost" if record.get("reason") == "supervisor_lost" else record["status"]
    return record


def exit_code(record: dict[str, Any]) -> int:
    status = record.get("status")
    if status == "succeeded":
        return 0
    if status in ACTIVE:
        return 75
    if record.get("reason") == "hard":
        return 126
    if status == "stalled" or record.get("reason") == "idle":
        return 124
    return 1


def compact_status(record: dict[str, Any]) -> str:
    status = record.get("status")
    prefix = f"job={record.get('id', '?')}"
    if status in ACTIVE:
        idle = max(0, int(record.get("idle_seconds", 0)))
        return f"{prefix} running progressing idle={idle}s"
    if status == "succeeded":
        return f"{prefix} succeeded"
    if status == "stalled":
        return f"{prefix} stalled idle={max(0, int(record.get('idle_seconds', 0)))}s"
    return f"{prefix} failed code={record.get('exit_code', 1)} reason={record.get('reason', 'command')}"


def seconds(value: Any, field: str) -> float:
    if type(value) not in (float, int) or not math.isfinite(value) or not 0 <= value <= 604800:
        raise JobError(f"{field} must be finite and between 0 and 604800")
    return float(value)


def command_argv(argv: Any, field: str = "argv") -> list[str]:
    if not isinstance(argv, list) or not argv or len(argv) > 256 or any(not isinstance(arg, str) or "\0" in arg or len(arg) > 32768 for arg in argv) or not argv[0]:
        raise JobError(f"{field} must be a nonempty argv array")
    if any(SECRET_ARGUMENT.search(arg) for arg in argv):
        raise JobError("Credentials must be supplied through the environment, never job arguments")
    return list(argv)


def probe_config(value):
    if value is None:
        return None
    if isinstance(value, list):
        value = {"command": value}
    if not isinstance(value, dict) or set(value) - {"command", "every_seconds", "timeout_seconds", "mode"}:
        raise JobError("progress_probe must be an argv array or command probe object")
    result = {**value, "command": command_argv(value.get("command"), "progress_probe.command")}
    for field, upper in (("every_seconds", 300), ("timeout_seconds", 60)):
        if field in value and (type(value[field]) is not int or not 1 <= value[field] <= upper):
            raise JobError(f"progress_probe {field} must be an integer between 1 and {upper}")
    if value.get("mode", "changes") not in ("changes", "increases"):
        raise JobError("Invalid progress_probe mode")
    return result


def dispatcher_owner(plan_dir: Path | str, job_id: str, validation_id: str | None) -> tuple[int, str] | None:
    declared = os.environ.get("PAE_JOB_DISPATCH_PLAN")
    if declared is None:
        return None
    try:
        allowed = json.loads(os.environ.get("PAE_JOB_ALLOWED_IDS", "[]"))
        pid = int(os.environ.get("PAE_JOB_DISPATCH_PID", "0"))
    except (ValueError, TypeError):
        raise JobError("Invalid runner job dispatch context")
    if (Path(declared).resolve() != Path(plan_dir).expanduser().resolve() or not isinstance(allowed, list)
            or job_id not in allowed or validation_id != job_id):
        raise JobError("Runner dispatch permits only this plan's declared mapped validation jobs")
    identity = pid_identity(pid)
    if identity is None:
        raise JobError("Runner dispatcher is unavailable")
    return pid, identity


def launch_supervisor(run: Path, cwd: Path | str) -> bool:
    env = {key: value for key, value in os.environ.items() if key not in {"PAE_JOB_DISPATCH_PLAN", "PAE_JOB_ALLOWED_IDS", "PAE_JOB_DISPATCH_PID"}}
    env.update(PYTHONUTF8="1", PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    # Windows: a hidden console (CREATE_NO_WINDOW) is inherited by the supervisor's children; DETACHED_PROCESS has none, so every child .cmd/powershell opened its own visible window.
    detached = {"creationflags": subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {"start_new_session": True}
    try:
        process = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "_supervise", "--run", str(run)],
                                   stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                   close_fds=True, cwd=cwd, env=env, **detached)
        write_record(run / "launch.json", {"supervisor_pid": process.pid, "supervisor_identity": pid_identity(process.pid)})
        threading.Thread(target=process.wait, daemon=True).start()
        return True
    except OSError:
        write_record(run / "launch-failure.json", {"failed_at": now()})
        return False


def dispatch_jobs(plan_dir: Path | str, allowed_ids: list[str]) -> int:
    """Launch queued declared jobs from the runner, outside model-owned process trees."""
    if not isinstance(allowed_ids, (list, tuple)):
        raise JobError("Dispatcher requires an array of allowed job ids")
    identifiers = [safe_id(identifier) for identifier in allowed_ids]
    launched = 0
    for identifier in identifiers:
        directory = job_dir(plan_dir, identifier)
        if not directory.is_dir() or not (directory / "current.json").exists():
            continue
        with job_lock(directory):
            run, _ = current_run(directory)
            if any((run / filename).exists() for filename in ("state.json", "launch.json", "launch-failure.json")):
                continue
            request = read_record(run / "request.json")
            if request.get("dispatch_requested") is not True:
                continue
            if (request.get("id") != identifier or request.get("validation_id") != identifier
                    or request.get("starter_pid") != os.getpid() or request.get("starter_identity") != pid_identity(os.getpid())):
                continue
            if not request.get("map_path") or not request.get("validation_fingerprint"):
                write_record(run / "launch-failure.json", {"failed_at": now(), "reason": "missing_validation_pin"})
                continue
            command_argv(request.get("argv"))
            if launch_supervisor(run, request["cwd"]):
                launched += 1
    return launched


def start_job(plan_dir: Path | str, job_id: str, argv: list[str], cwd: Path | str,
              idle_seconds: float = 300, hard_seconds: float = 0, progress_probe=None,
              progress_files=None, progress_regex=None, *, restart: bool = False,
              expected_quiet_seconds: float = 0, validation_id: str | None = None,
              map_path: str | None = None, validation_fingerprint: str | None = None) -> dict[str, Any]:
    directory = job_dir(plan_dir, job_id)
    argv = command_argv(argv)
    cwd = Path(cwd).expanduser().resolve()
    if not cwd.is_dir():
        raise JobError("Job working directory does not exist")
    progress_probe = probe_config(progress_probe)
    if validation_id is not None:
        safe_id(validation_id)
    dispatcher = dispatcher_owner(plan_dir, job_id, validation_id)
    if validation_fingerprint is not None and (not isinstance(validation_fingerprint, str) or re.fullmatch(r"[a-f0-9]{64}", validation_fingerprint) is None):
        raise JobError("Invalid validation fingerprint")
    if map_path is not None:
        if not isinstance(map_path, str) or not Path(map_path).is_file():
            raise JobError("Mapped job requires an existing service map")
        map_path = str(Path(map_path).resolve())
    if dispatcher and (map_path is None or validation_fingerprint is None):
        raise JobError("Runner dispatch requires a mapped validation fingerprint")
    if progress_files is None:
        progress_files = []
    if not isinstance(progress_files, list) or any(not isinstance(path, (str, Path)) for path in progress_files):
        raise JobError("progress_files must be an array of file paths")
    if progress_regex is not None:
        if not isinstance(progress_regex, str) or len(progress_regex) > 2000:
            raise JobError("progress_regex must be a bounded regular expression")
        re.compile(progress_regex)
    sources = {"progress_files": [str(path) for path in progress_files]}
    if progress_probe is not None:
        sources["progress_probe"] = progress_probe
    if progress_regex is not None:
        sources["progress_regex"] = progress_regex
    source_errors = validate_policy(sources)
    if source_errors:
        raise JobError("Invalid progress sources; use a bounded probe and repository-relative file globs")
    options = {"argv": argv, "cwd": str(cwd), "idle_timeout_seconds": seconds(idle_seconds, "idle_seconds"),
               "hard_timeout_seconds": seconds(hard_seconds, "hard_seconds"), "progress_probe": progress_probe,
               "progress_files": [str(path) for path in progress_files], "progress_regex": progress_regex,
               "expected_quiet_seconds": seconds(expected_quiet_seconds, "expected_quiet_seconds"), "validation_id": validation_id,
               "map_path": map_path, "validation_fingerprint": validation_fingerprint}
    encoded = json.dumps(options, sort_keys=True, ensure_ascii=False).encode("utf-8")
    if len(encoded) > MAX_RECORD_BYTES // 2:
        raise JobError("Job arguments are too large")
    fingerprint = hashlib.sha256(encoded).hexdigest()
    directory.parent.mkdir(parents=True, exist_ok=True)
    try:
        directory.mkdir()
    except FileExistsError:
        if not directory.is_dir():
            raise JobError("Job directory is not a directory")
    with job_lock(directory):
        if (directory / "current.json").exists():
            old = status_job(plan_dir, job_id)
            if old["status"] in ACTIVE:
                if old.get("fingerprint") != fingerprint:
                    raise JobError("Active job already has different command or progress options")
                return old
            if not restart:
                raise JobError("Job already finished; use --restart to create a new generation")
        nonce = secrets.token_hex(16)
        run = checked_path(directory, "runs", nonce)
        run.parent.mkdir(exist_ok=True)
        run.mkdir()
        request = {"version": VERSION, "id": job_id, "nonce": nonce, "fingerprint": fingerprint,
                   "started_at": now(), "started_unix": time.time(), "starter_pid": os.getpid(), "starter_identity": pid_identity(os.getpid()), **options}
        if dispatcher:
            request.update(dispatch_requested=True, starter_pid=dispatcher[0], starter_identity=dispatcher[1])
        write_record(run / "request.json", request)
        write_record(directory / "current.json", {"version": VERSION, "nonce": nonce})
        if dispatcher:
            return status_job(plan_dir, job_id)
        if not launch_supervisor(run, cwd):
            return status_job(plan_dir, job_id)
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        result = status_job(plan_dir, job_id)
        if result["status"] != "starting":
            return result
        time.sleep(0.05)
    return result


def wait_job(plan_dir: Path | str, job_id: str, max_seconds: float = 60) -> dict[str, Any]:
    deadline = time.monotonic() + seconds(max_seconds, "max_seconds")
    while True:
        result = status_job(plan_dir, job_id)
        if result["status"] not in ACTIVE or time.monotonic() >= deadline:
            return result
        time.sleep(min(0.2, max(0, deadline - time.monotonic())))


def stop_job(plan_dir: Path | str, job_id: str) -> dict[str, Any]:
    directory = job_dir(plan_dir, job_id)
    if not directory.is_dir():
        raise JobError("Job has not been started")
    with job_lock(directory):
        result = status_job(plan_dir, job_id)
        if result["status"] not in ACTIVE:
            return result
        run, pointer = current_run(directory)
        write_record(checked_path(run, "stop.json"), {"nonce": pointer["nonce"], "requested_at": now()})
        if not any((run / filename).exists() for filename in ("state.json", "launch.json", "launch-failure.json")):
            # Queued runner requests have no supervisor to acknowledge a stop.
            # Holding the launch lock makes cancellation final before dispatch.
            result.update(status="stopped", state="stopped", exit_code=130, reason="stop", completed_at=now())
            write_record(checked_path(run, "state.json"), result)
            return result
    return wait_job(plan_dir, job_id, 5)


def supervise(run: Path) -> int:
    request = read_record(run / "request.json")
    nonce = request["nonce"]
    state = {key: request[key] for key in ("version", "id", "nonce", "fingerprint", "argv", "cwd", "started_at", "idle_timeout_seconds", "hard_timeout_seconds", "expected_quiet_seconds", "validation_id", "map_path", "validation_fingerprint")}
    state.update(status="starting", supervisor_pid=os.getpid(), supervisor_identity=pid_identity(os.getpid()))
    process = monitor = reader = None
    mapped = request.get("validation_id") is not None
    watcher_terminal = {}
    interrupted = threading.Event()
    if threading.current_thread() is threading.main_thread():
        signal.signal(signal.SIGTERM, lambda *_: interrupted.set())
        signal.signal(signal.SIGINT, lambda *_: interrupted.set())
    progress = ProgressState(0 if mapped else request["idle_timeout_seconds"], 0 if mapped else request["hard_timeout_seconds"],
                             expected_quiet_seconds=request.get("expected_quiet_seconds", 0), progress_regex=request.get("progress_regex"))

    def save():
        state.update(progress.snapshot(), updated_at=now(), observed_at=time.time())
        state.update(idle_timeout_seconds=request["idle_timeout_seconds"], hard_timeout_seconds=request["hard_timeout_seconds"])
        if watcher_terminal.get("failure_class") == "environmental":
            state.update(failure_class="environmental", environment_failure=watcher_terminal["environment_failure"])
        if state.get("reason") == "idle" and "idle_seconds" in watcher_terminal:
            state["idle_seconds"] = watcher_terminal["idle_seconds"]
        write_record(run / "state.json", state)

    def stopped():
        return interrupted.is_set() or read_record(run / "stop.json").get("nonce") == nonce

    save()
    try:
        with job_lock(run.parent.parent):
            if stopped():
                state.update(status="stopped", exit_code=130, reason="stop")
                return 0
            log = (run / "output.log").open("wb")
            try:
                env = dict(os.environ)
                if mapped:
                    env.update(PAE_VALIDATION_IDLE_SECONDS=str(request["idle_timeout_seconds"]), PAE_VALIDATION_HARD_SECONDS=str(request["hard_timeout_seconds"]))
                process = process_tree.launch(request["argv"], cwd=request["cwd"], stdin=subprocess.DEVNULL,
                                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
            except BaseException:
                log.close()
                raise
            state.update(status="running", pid=process.pid, process_identity=pid_identity(process.pid))
            save()
        assert process.stdout is not None

        def output_reader():
            pending = b""
            try:
                while True:
                    block = os.read(process.stdout.fileno(), 4096)
                    if not block:
                        break
                    log.write(block)
                    log.flush()
                    progress.observe_output(block)
                    if mapped:
                        pending += block
                        lines = pending.split(b"\n")
                        pending = lines.pop()[-8192:]
                        for line in lines:
                            if line.startswith(b"[resource-watch] environment_failure="):
                                match = re.match(rb"\[resource-watch\] environment_failure=([a-z_]{1,64})(?:\s|$)", line)
                                category = match[1].decode("ascii") if match else "reported"
                                watcher_terminal.update(failure_class="environmental", environment_failure=category if category in ENVIRONMENT_FAILURES else "reported")
                            elif line.startswith(b"[resource-watch] validation_ceiling=hard "):
                                watcher_terminal["reason"] = "hard"
                            elif line.startswith(b"[resource-watch] validation_stalled="):
                                watcher_terminal["reason"] = "idle"
                                match = re.search(rb"\bidle_seconds=(\d+)", line)
                                if match:
                                    watcher_terminal["idle_seconds"] = int(match[1])
            finally:
                process.stdout.close()

        reader = threading.Thread(target=output_reader, daemon=True)
        reader.start()
        monitor = ProgressMonitor(process, progress, Path(request["cwd"]), progress_probe=request.get("progress_probe"), progress_files=request.get("progress_files"))
        monitor.start()
        next_save = time.monotonic() + 1
        while process.poll() is None:
            if stopped():
                state.update(status="stopped", exit_code=130, reason="stop")
                process_tree.terminate(process)
                break
            if monitor.reason:
                reason = monitor.reason
                state.update(status="stalled" if reason == "idle" else "failed", exit_code=124 if reason == "idle" else 126, reason=reason)
                break
            if time.monotonic() >= next_save:
                save()
                next_save = time.monotonic() + 1
            time.sleep(0.1)
        # The command's runtime has ended. Cleanup and output draining have their
        # own bounds and must not retroactively expire a successful command.
        monitor.close()
        process_tree.terminate(process)
        reader.join(timeout=3)
        timeout_reason = monitor.reason or watcher_terminal.get("reason")
        if timeout_reason and state["status"] == "running":
            reason = timeout_reason
            state.update(status="stalled" if reason == "idle" else "failed", exit_code=124 if reason == "idle" else 126, reason=reason)
            if "idle_seconds" in watcher_terminal:
                state["watcher_idle_seconds"] = watcher_terminal["idle_seconds"]
        if state["status"] == "running":
            code = process.wait()
            state.update(status="succeeded" if code == 0 else "failed", exit_code=code, reason="launch" if code == 127 else "command")
        return 0
    except BaseException as exc:
        # Exception text and argv can contain credentials; the compact record carries only a category.
        state.update(status="failed", exit_code=127 if process is None else 1, reason="launch" if process is None else "supervisor_error", error_type=type(exc).__name__)
        return 1
    finally:
        if monitor is not None:
            monitor.close()
        if process is not None:
            process_tree.terminate(process)
            if reader is not None:
                reader.join(timeout=3)
            process_tree.close(process)
        if "log" in locals():
            if not mapped and state.get("reason") in {"idle", "hard"}:
                snapshot = progress.snapshot()
                source = snapshot["last_progress_source"]
                if source not in {"start", "output", "regex", "cpu", "probe", "files"}:
                    source = "unknown"
                line = (f"\n[job] timeout={state['reason']} idle_seconds={snapshot['idle_seconds']:g} "
                        f"last_progress_source={source} window_seconds={request['idle_timeout_seconds']:g} "
                        f"ceiling_seconds={request['hard_timeout_seconds']:g}\n")
                log.write(line.encode("utf-8"))
                log.flush()
            log.close()
        state["completed_at"] = now()
        save()


def mapped_start(args):
    import planctl
    import routing_config
    import service_map
    plan_dir, manifest = planctl.load_plan(args.plan)
    cwd = Path(manifest["repo_root"]).resolve()
    map_path = service_map.repo_path(cwd, args.map)
    _, data = service_map.load_map(map_path)
    fresh, _, truncated, _ = service_map.current_status(cwd, map_path, data)
    if not fresh or truncated or service_map.validate_data(data):
        raise JobError("Service map must be fresh and valid before starting a validation")
    validation = next((item for item in data["validations"] if item["id"] == args.validation), None)
    if validation is None:
        raise JobError("Validation is not declared in the service map")
    config = routing_config.load(planctl.default_config(), plan_dir / planctl.CONFIG)
    owners = [task for task in manifest.get("tasks", []) if args.id in task.get("validation_jobs", [])]
    active_owners = [task for task in owners if task.get("status") == "in_progress"]
    if len(active_owners) == 1:
        task = active_owners[0]
    elif len(owners) <= 1:
        task = owners[0] if owners else {}
    else:
        raise JobError("Validation job must have one unambiguous owning task")
    inherited_idle = task.get("validation_timeout_seconds", config.get("validation_timeout_seconds", 1800))
    idle = validation.get("no_progress_timeout_seconds", args.idle_seconds if args.idle_seconds is not None else inherited_idle)
    ceilings = [seconds(item, "hard_seconds") for item in (
        config.get("validation_hard_timeout_seconds", 0), task.get("validation_hard_timeout_seconds", 0),
        validation.get("validation_hard_timeout_seconds", 0), args.hard_seconds or 0)]
    enabled = [item for item in ceilings if item > 0]
    effective = {**validation, "no_progress_timeout_seconds": idle,
                 "validation_hard_timeout_seconds": min(enabled, default=0), "_map_path": str(map_path),
                 "_validation_fingerprint": service_map.validation_fingerprint(data, args.validation)}
    argv = [sys.executable, str(Path(__file__).with_name("resource_watch.py")), "run", "--repo-root", str(cwd), "--map", str(map_path), "--validation", args.validation]
    return cwd, argv, effective


def parser():
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    for name in ("start", "status", "wait", "stop"):
        command = commands.add_parser(name)
        command.add_argument("--plan", required=True)
        command.add_argument("--id", required=True)
        if name == "wait":
            command.add_argument("--max-seconds", type=float, default=60)
        if name == "start":
            command.add_argument("--cwd", default=None)
            command.add_argument("--idle-seconds", type=float, default=None)
            command.add_argument("--hard-seconds", type=float, default=None)
            command.add_argument("--progress-probe", default=None, help="JSON argv array")
            command.add_argument("--progress-file", action="append", default=None)
            command.add_argument("--progress-regex", default=None)
            command.add_argument("--restart", action="store_true")
            command.add_argument("--validation")
            command.add_argument("--map", default=".ai-work/SERVICE_MAP.md")
            command.add_argument("argv", nargs=argparse.REMAINDER)
    supervisor = commands.add_parser("_supervise", help=argparse.SUPPRESS)
    supervisor.add_argument("--run", required=True)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        if args.command == "_supervise":
            return supervise(Path(args.run))
        if args.command == "start":
            argv = args.argv[1:] if args.argv[:1] == ["--"] else args.argv
            mapped = {}
            if args.validation:
                if argv or args.cwd:
                    raise JobError("Mapped validation supplies the command and working directory")
                cwd, argv, mapped = mapped_start(args)
                if args.progress_probe is not None or args.progress_file is not None or args.progress_regex is not None:
                    raise JobError("Mapped validation progress sources are declared in the service map")
            else:
                cwd = args.cwd or os.getcwd()
            probe = json.loads(args.progress_probe) if args.progress_probe is not None else mapped.get("progress_probe")
            result = start_job(args.plan, args.id, argv, cwd,
                               idle_seconds=mapped["no_progress_timeout_seconds"] if args.validation else args.idle_seconds if args.idle_seconds is not None else 300,
                               hard_seconds=mapped["validation_hard_timeout_seconds"] if args.validation else args.hard_seconds if args.hard_seconds is not None else 0,
                               progress_probe=probe, progress_files=args.progress_file if args.progress_file is not None else mapped.get("progress_files"),
                               progress_regex=args.progress_regex if args.progress_regex is not None else mapped.get("progress_regex"),
                               restart=args.restart, expected_quiet_seconds=mapped.get("expected_quiet_seconds", 0), validation_id=args.validation,
                               map_path=mapped.get("_map_path"), validation_fingerprint=mapped.get("_validation_fingerprint"))
            print(compact_status(result))
            return 0 if result["status"] in ACTIVE | {"succeeded"} else exit_code(result)
        result = wait_job(args.plan, args.id, args.max_seconds) if args.command == "wait" else stop_job(args.plan, args.id) if args.command == "stop" else status_job(args.plan, args.id)
        print(compact_status(result))
        return exit_code(result)
    except (JobError, OSError, ValueError, re.error):
        # Avoid replaying raw arguments, paths or probe output in model-visible errors.
        print("job=error failed code=1 reason=invalid_request", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
