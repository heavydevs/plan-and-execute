#!/usr/bin/env python3
"""Run one mapped validation while sampling its declared resource health checks."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import queue
import re
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

import service_map
import process_tree


def stamp() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def excerpt(value: str, limit: int = 240) -> str:
    compact = " ".join(value.split())
    return compact[-limit:]


def evaluate_check(check: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    started = time.monotonic()
    process: subprocess.Popen[str] | None = None
    command = check["command"]
    if os.name != "nt":
        # The trampoline gives each probe its own process group but keeps it in
        # the runner's session, so both local timeout cleanup and the runner's
        # outer timeout can terminate it, including orphaned descendants.
        command = [sys.executable, str(Path(__file__).resolve()), "_probe-exec", *command]
    try:
        process = subprocess.Popen(
            command,
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        try:
            stdout, stderr = process.communicate(timeout=check.get("timeout_seconds", 5))
            output = (stdout or "") + (stderr or "")
            exit_code: int | None = process.returncode
            error = None
        except subprocess.TimeoutExpired as exc:
            _terminate_probe_tree(process)
            try:
                stdout, stderr = process.communicate(timeout=2)
            except subprocess.TimeoutExpired as cleanup_exc:
                stdout = service_map_decode(cleanup_exc.stdout or exc.stdout)
                stderr = service_map_decode(cleanup_exc.stderr or exc.stderr)
            output = service_map_decode(stdout) + service_map_decode(stderr)
            exit_code = None
            error = f"probe timed out after {check.get('timeout_seconds', 5)}s"
    except (OSError, ValueError) as exc:
        output, exit_code, error = "", None, f"probe could not start: {exc}"

    success_codes = check.get("success_exit_codes", [0])
    healthy = exit_code in success_codes
    healthy_regex = check.get("healthy_regex")
    unhealthy_regex = check.get("unhealthy_regex")
    if healthy_regex and re.search(healthy_regex, output, re.IGNORECASE) is None:
        healthy = False
    if unhealthy_regex and re.search(unhealthy_regex, output, re.IGNORECASE) is not None:
        healthy = False
    return {
        "state": "healthy" if healthy else "unhealthy",
        "exit_code": exit_code,
        "duration_seconds": round(time.monotonic() - started, 3),
        "excerpt": excerpt(output) if check.get("record_excerpt") is True else "",
        "error": error,
    }


def _terminate_probe_tree(process: subprocess.Popen[str]) -> None:
    """Stop a timed-out probe and descendants so repeated samples do not leak processes."""
    if os.name == "nt":
        try:
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            if process.poll() is None:
                process.kill()
    else:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            pass
        # The probe's parent may have exited while a descendant still holds
        # its pipes; its dedicated process group remains addressable by PID.
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    if process.poll() is None:
        process.kill()
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        pass


def probe_exec(command: list[str]) -> int:
    if not command:
        return 125
    if os.name != "nt":
        try:
            os.setpgid(0, 0)
        except OSError as exc:
            print(f"[resource-watch] probe process-group setup failed: {exc}", file=sys.stderr)
            return 125
    try:
        os.execvp(command[0], command)
    except OSError as exc:
        print(f"[resource-watch] probe command could not start: {exc}", file=sys.stderr)
        return 127


def service_map_decode(value: str | bytes | None) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value or ""


def run_validation(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    map_path = service_map.repo_path(repo_root, args.map)
    _, data = service_map.load_map(map_path)
    fresh, _, truncated, changed = service_map.current_status(repo_root, map_path, data)
    errors = service_map.validate_data(data)
    if not fresh or truncated or errors:
        details = "; ".join(errors[:4]) or "source snapshot is stale"
        if changed:
            details += "; changed inputs: " + ", ".join(changed[:8])
        print(f"[resource-watch] environment_failure=service_map_invalid details={details}", file=sys.stderr)
        return 125
    validations = {item["id"]: item for item in data["validations"]}
    validation = validations.get(args.validation)
    if validation is None:
        print(f"[resource-watch] environment_failure=validation_not_mapped id={args.validation}", file=sys.stderr)
        return 125
    resources = {item["id"]: item for item in data["resources"]}
    host_platform = service_map.current_platform()
    selected = [
        (resources[rid], check)
        for rid in validation["resources"]
        for check in resources[rid]["checks"]
        if check.get("platforms") is None or host_platform in check["platforms"]
    ]
    if selected and os.name != "nt":
        try:
            session_pids = process_tree.posix_session_processes(os.getsid(0))
            cleanup_available = session_pids is not None and os.getpid() in session_pids
        except OSError:
            cleanup_available = False
        if not cleanup_available:
            print(
                "[resource-watch] environment_failure=probe_cleanup_unavailable "
                "reason=no POSIX session process enumerator (ps or /proc)",
                file=sys.stderr,
                flush=True,
            )
            return 125
    check_states: dict[tuple[str, str], str] = {}
    start = time.monotonic()
    deadlines: dict[tuple[str, str], float] = { (resource["id"], check["id"]): start for resource, check in selected }
    intervals = { (resource["id"], check["id"]): check.get("every_seconds", 60) for resource, check in selected }
    grace = { (resource["id"], check["id"]): check.get("startup_grace_seconds", 60) for resource, check in selected }
    report_path = service_map.repo_path(repo_root, args.report) if args.report else None
    if report_path is None:
        safe_id = re.sub(r"[^A-Za-z0-9_.-]", "_", args.validation)
        report_path = repo_root / ".ai-work" / "resource-watch" / f"{dt.datetime.now().strftime('%Y%m%dT%H%M%S')}-{safe_id}.jsonl"
        report_path = service_map.repo_path(repo_root, report_path.as_posix())
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = report_path.open("a", encoding="utf-8")

    def sample(phase: str, pid: int, process_running: bool) -> None:
        nonlocal health_failure, environment_failure_reported
        now = time.monotonic()
        for resource, check in selected:
            key = (resource["id"], check["id"])
            if phase == "interval" and now < deadlines[key]:
                continue
            result = evaluate_check(check, repo_root)
            deadlines[key] = time.monotonic() + intervals[key]
            in_grace = (now - start) < grace[key] and phase != "final"
            state = result["state"]
            if state == "unhealthy" and in_grace:
                state = "starting"
            elif state == "unhealthy":
                health_failure = True
                if not environment_failure_reported:
                    print("[resource-watch] environment_failure=health_check_failed", file=sys.stderr, flush=True)
                    environment_failure_reported = True
            check_states[key] = state
            item = {
                "timestamp": stamp(),
                "validation": args.validation,
                "phase": phase,
                "test_pid": pid,
                "test_running": process_running,
                "resource": resource["id"],
                "check": check["id"],
                **result,
                "state": state,
            }
            report.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")
            report.flush()
            safe_excerpt = f" excerpt={result['excerpt']!r}" if result["excerpt"] else ""
            print(
                f"[resource-watch] time={item['timestamp']} validation={args.validation} "
                f"resource={resource['id']} check={check['id']} state={state}"
                f" duration={result['duration_seconds']}s{safe_excerpt}",
                flush=True,
            )
        if not selected and phase == "start":
            print(f"[resource-watch] validation={args.validation} resources=none (explicitly mapped)", flush=True)

    def record_test_process(phase: str, pid: int, running: bool) -> None:
        item = {
            "timestamp": stamp(),
            "validation": args.validation,
            "phase": phase,
            "kind": "test_process",
            "test_pid": pid,
            "test_running": running,
        }
        report.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")
        report.flush()
        print(
            f"[resource-watch] time={item['timestamp']} validation={args.validation} "
            f"test_pid={pid} test_process={'running' if running else 'exited'}",
            flush=True,
        )

    health_failure = False
    environment_failure_reported = False
    try:
        print(f"[resource-watch] validation={args.validation} report={report_path.relative_to(repo_root).as_posix()}", flush=True)
        try:
            process = subprocess.Popen(
                validation["command"],
                cwd=repo_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )
        except (OSError, ValueError) as exc:
            print(f"[resource-watch] environment_failure=test_command_unavailable error={exc}", file=sys.stderr)
            return 125

        assert process.stdout is not None
        output_queue: queue.Queue[str | None] = queue.Queue()

        def read_test_output() -> None:
            try:
                for line in process.stdout:
                    output_queue.put(line)
            finally:
                output_queue.put(None)

        reader = threading.Thread(target=read_test_output, daemon=True)
        reader.start()
        record_test_process("start", process.pid, True)
        sample("start", process.pid, True)
        next_process_sample = time.monotonic() + 60
        next_interval = min([*deadlines.values(), next_process_sample])
        output_finished = False
        while True:
            wait_for = max(0.05, min(0.5, next_interval - time.monotonic()))
            try:
                line = output_queue.get(timeout=wait_for)
                if line is None:
                    output_finished = True
                else:
                    sys.stdout.write(line)
                    sys.stdout.flush()
            except queue.Empty:
                pass
            now = time.monotonic()
            if now >= next_interval and process.poll() is None:
                if any(deadline <= now for deadline in deadlines.values()):
                    sample("interval", process.pid, True)
                if now >= next_process_sample:
                    record_test_process("interval", process.pid, True)
                    next_process_sample = time.monotonic() + 60
                next_interval = min([*deadlines.values(), next_process_sample], default=next_process_sample)
            if process.poll() is not None and output_finished:
                break
        reader.join(timeout=1)
        exit_code = process.wait()
        record_test_process("final", process.pid, False)
        health_state = "unhealthy" if health_failure else ("unobserved" if "starting" in check_states.values() else "healthy")
        print(f"[resource-watch] validation={args.validation} test_exit={exit_code} health={health_state}")
        if health_failure and exit_code == 0:
            return 125
        return exit_code
    finally:
        report.close()


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="run one mapped validation with periodic health sampling")
    run.add_argument("--repo-root", default=".")
    run.add_argument("--map", default=".ai-work/SERVICE_MAP.md")
    run.add_argument("--validation", required=True)
    run.add_argument("--report", help="optional repository-relative JSONL report path")
    run.set_defaults(func=run_validation)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        return int(args.func(args))
    except (service_map.MapError, OSError, KeyError, TypeError) as exc:
        print(f"[resource-watch] environment_failure=configuration_error error={exc}", file=sys.stderr)
        return 125


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "_probe-exec":
        raise SystemExit(probe_exec(sys.argv[2:]))
    raise SystemExit(main())
