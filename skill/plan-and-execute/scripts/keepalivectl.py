#!/usr/bin/env python3
"""Keep a plan's runner alive: relaunch it when it died while runnable work remains.

watchdogctl stays strictly read-only; this is the only script that starts a runner. It relaunches only when no
runner holds a live lease and the plan has runnable work (a dead runner with an in_progress task, a ready pending
task, or an expired quota cooldown). Blocked tasks, silent live work and failed jobs are reported, never restarted.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import shlex
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Iterator
from xml.sax.saxutils import escape

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lifecyclectl
import planctl
import watchdogctl as watchdog

RESTART = {"runner_dead", "awaiting_next", "quota_resume_due"}
KEEPALIVE_DIR = ".ai-work/keepalive"
TASK_PREFIX = "PlanAndExecuteKeepalive-"
CREATE_NO_WINDOW = 0x08000000
CREATE_NEW_PROCESS_GROUP = 0x00000200
AVAILABILITY_PAUSE = 75
MAX_LOG_BYTES = 5 * 1024 * 1024
KEPT_LAUNCHES = 20


def console_python() -> str:
    """The runner needs a console interpreter: its children capture stdout, which pythonw.exe does not have."""
    executable = Path(sys.executable)
    if executable.name.lower() == "pythonw.exe":
        candidate = executable.with_name("python.exe")
        if candidate.exists():
            return str(candidate)
    return str(executable)


def plan_key(plan_dir: Path) -> str:
    return hashlib.sha256(str(plan_dir.resolve()).encode()).hexdigest()[:16]


def keepalive_directory(repo: Path) -> Path:
    return lifecyclectl.work_directory(repo, KEEPALIVE_DIR)


def read_state(directory: Path, key: str) -> dict[str, Any]:
    state = lifecyclectl.read_json_file(directory / f"{key}.json") or {}
    launches = [entry for entry in state.get("launches", [])
                if isinstance(entry, dict) and isinstance(entry.get("at"), (int, float))]
    return {"version": 1, "launches": launches}


def write_state(directory: Path, key: str, state: dict[str, Any]) -> None:
    state["launches"] = state["launches"][-KEPT_LAUNCHES:]
    planctl.atomic_write_json(directory / f"{key}.json", state)


@contextlib.contextmanager
def exclusive(path: Path, stale_seconds: float = 120) -> Iterator[bool]:
    """Best-effort mutex so two scheduler ticks cannot launch two runners (the runner lease is the final guard)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = None
    for _ in range(2):
        try:
            descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            try:
                if time.time() - path.stat().st_mtime <= stale_seconds:
                    break
                path.unlink()
            except FileNotFoundError:
                continue
            except OSError:
                break
    if descriptor is None:
        yield False
        return
    try:
        os.write(descriptor, str(os.getpid()).encode())
        os.close(descriptor)
        yield True
    finally:
        path.unlink(missing_ok=True)


def launch(argv: list[str], cwd: Path, log_path: Path) -> subprocess.Popen:
    """Start the runner detached with a hidden console that its children inherit (no stray cmd windows)."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if log_path.exists() and log_path.stat().st_size > MAX_LOG_BYTES:
        os.replace(log_path, log_path.with_suffix(".log.1"))
    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
    if os.name == "nt":
        flags = {"creationflags": CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP}
    else:
        flags = {"start_new_session": True}
    with log_path.open("ab") as log:
        return subprocess.Popen(argv, cwd=cwd, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                env=env, close_fds=True, **flags)


def runner_argv(plan_dir: Path, runner_args: list[str]) -> list[str]:
    runner = Path(__file__).resolve().with_name("run_concise.py")
    return [console_python(), str(runner), "--plan", str(plan_dir), *runner_args]


def check_plan(plan_dir: Path, manifest: dict[str, Any], args: argparse.Namespace,
               now: float) -> tuple[list[str], int]:
    plan_id = watchdog.token(manifest["plan_id"])
    repo = Path(manifest["repo_root"]).resolve()
    items = watchdog.collect_plan(plan_dir, manifest, now=now, home=Path.home())
    findings = [(item, watchdog.classify(item, now)) for item in items]
    lines = [watchdog.render(item, finding) for item, finding in findings
             if finding[0] and finding[0] not in RESTART]
    code = int(bool(lines))
    lease = lifecyclectl.read_lease(plan_dir)
    if lifecyclectl.lease_is_live(lease):
        if not args.quiet:
            lines.append(f"keepalive:ok {plan_id} runner_live pid={watchdog.token((lease or {}).get('pid'))}")
        return lines, code
    reasons = sorted({finding[0] for _, finding in findings if finding[0] in RESTART})
    if not reasons:
        blocked = any(task.get("status") == "blocked" for task in manifest.get("tasks", []))
        if not args.quiet:
            lines.append(f"keepalive:skip {plan_id} reason={'blocked' if blocked else 'nothing_runnable'}")
        return lines, code
    directory = keepalive_directory(repo)
    key = plan_key(plan_dir)
    if (directory / f"{key}.paused").exists():
        lines.append(f"keepalive:skip {plan_id} reason=paused")
        return lines, code
    state = read_state(directory, key)
    completed = sum(1 for task in manifest.get("tasks", []) if task.get("status") == "completed")
    window = args.within_minutes * 60
    recent = [entry for entry in state["launches"] if now - entry["at"] <= window]
    if len(recent) >= args.max_restarts and completed <= int(recent[0].get("completed", 0)):
        lines.append(f"ANOMALY:restart_loop:owner_inspect {plan_id}/plan launches={len(recent)} "
                     f"window={args.within_minutes}m completed={completed}")
        return lines, 1
    argv = runner_argv(plan_dir, args.runner_arg)
    if args.dry_run:
        lines.append(f"keepalive:would_launch {plan_id} reason={','.join(reasons)}")
        return lines, code
    with exclusive(directory / f"{key}.lock") as acquired:
        if not acquired:
            lines.append(f"keepalive:skip {plan_id} reason=locked")
            return lines, code
        # Re-check under the mutex: another tick may have started the runner a moment ago.
        if lifecyclectl.lease_is_live(lifecyclectl.read_lease(plan_dir)):
            lines.append(f"keepalive:skip {plan_id} reason=runner_started")
            return lines, code
        process = launch(argv, repo, directory / f"{key}-runner.log")
        state["launches"].append({"at": now, "completed": completed, "pid": process.pid})
        write_state(directory, key, state)
        deadline = time.time() + args.verify_seconds
        while process.poll() is None and time.time() < deadline:
            time.sleep(0.25)
        exit_code = process.poll()
    if exit_code in (None, 0):
        state_word = "launched" if exit_code is None else "launched_and_finished"
        lines.append(f"keepalive:{state_word} {plan_id} pid={process.pid} reason={','.join(reasons)}")
        return lines, code
    if exit_code == AVAILABILITY_PAUSE:
        lines.append(f"keepalive:skip {plan_id} reason=availability_pause")
        return lines, code
    lines.append(f"ANOMALY:launch_failed:owner_inspect {plan_id}/plan exit={exit_code}")
    return lines, 1


def check(args: argparse.Namespace) -> int:
    repo = lifecyclectl.resolve_repo_root(args.repo_root)
    candidates = ([planctl.load_plan(args.plan)] if args.plan else
                  lifecyclectl.scan_actionable_plans(repo, args.work_root))
    now = time.time()
    code = 0
    for plan_dir, manifest in candidates:
        lines, plan_code = check_plan(plan_dir, manifest, args, now)
        code |= plan_code
        for line in lines:
            print(line, flush=True)
    return code


def pause(args: argparse.Namespace, paused: bool) -> int:
    plan_dir, manifest = planctl.load_plan(args.plan)
    marker = keepalive_directory(Path(manifest["repo_root"]).resolve()) / f"{plan_key(plan_dir)}.paused"
    if paused:
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text("paused\n", encoding="utf-8")
    else:
        marker.unlink(missing_ok=True)
    print(f"keepalive:{'paused' if paused else 'resumed'} {watchdog.token(manifest['plan_id'])}")
    return 0


# --- OS scheduler -----------------------------------------------------------------------------------------------

def task_name(plan_dir: Path) -> str:
    return TASK_PREFIX + plan_key(plan_dir)[:8]


def scheduled_arguments(args: argparse.Namespace, plan_dir: Path, repo: Path) -> list[str]:
    arguments = [str(Path(__file__).resolve()), "check", "--repo-root", str(repo), "--plan", str(plan_dir), "--quiet"]
    for value in args.runner_arg:
        arguments.append(f"--runner-arg={value}")
    return arguments


def task_xml(command: str, arguments: list[str], workdir: Path, minutes: int, start: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo><Description>plan-and-execute runner keepalive</Description></RegistrationInfo>
  <Triggers>
    <TimeTrigger>
      <Repetition><Interval>PT{minutes}M</Interval><StopAtDurationEnd>false</StopAtDurationEnd></Repetition>
      <StartBoundary>{start}</StartBoundary>
      <Enabled>true</Enabled>
    </TimeTrigger>
  </Triggers>
  <Principals><Principal id="Author"><LogonType>InteractiveToken</LogonType><RunLevel>LeastPrivilege</RunLevel></Principal></Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <StartWhenAvailable>true</StartWhenAvailable>
    <ExecutionTimeLimit>PT10M</ExecutionTimeLimit>
    <Hidden>true</Hidden>
    <Enabled>true</Enabled>
  </Settings>
  <Actions Context="Author"><Exec>
    <Command>{escape(command)}</Command>
    <Arguments>{escape(subprocess.list2cmdline(arguments))}</Arguments>
    <WorkingDirectory>{escape(str(workdir))}</WorkingDirectory>
  </Exec></Actions>
</Task>
"""


def cron_line(minutes: int, arguments: list[str], log: Path) -> str:
    command = shlex.join([console_python(), *arguments])
    return f"*/{minutes} * * * * {command} >> {shlex.quote(str(log))} 2>&1"


def windowless_python() -> str:
    """pythonw.exe has no console, so the scheduled tick never flashes a window."""
    executable = Path(sys.executable)
    candidate = executable.with_name("pythonw.exe")
    return str(candidate if candidate.exists() else executable)


def schtasks(arguments: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(["schtasks", *arguments], capture_output=True, text=True,
                          creationflags=CREATE_NO_WINDOW if os.name == "nt" else 0)


def schedule(args: argparse.Namespace) -> int:
    plan_dir, manifest = planctl.load_plan(args.plan)
    repo = Path(manifest["repo_root"]).resolve()
    name = task_name(plan_dir)
    arguments = scheduled_arguments(args, plan_dir, repo)
    log = keepalive_directory(repo) / f"{plan_key(plan_dir)}-schedule.log"
    if args.action == "print" or os.name != "nt":
        if os.name == "nt":
            print(f"schtasks task={name} every={args.every}m command={subprocess.list2cmdline([windowless_python(), *arguments])}")
        else:
            print(cron_line(args.every, arguments, log))
        return 0
    if args.action == "status":
        result = schtasks(["/Query", "/TN", name])
        print(f"keepalive:schedule {name} {'present' if result.returncode == 0 else 'absent'}")
        return 0
    if args.action == "remove":
        result = schtasks(["/Delete", "/TN", name, "/F"])
        print(f"keepalive:schedule_removed {name}" if result.returncode == 0 else f"keepalive:schedule_absent {name}")
        return 0
    if not args.yes:
        print(f"keepalive: installing {name} creates a persistent OS task; repeat with --yes to confirm", file=sys.stderr)
        return 2
    start = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(time.time() + 60))
    xml = task_xml(windowless_python(), arguments, repo, args.every, start)
    with tempfile.TemporaryDirectory(prefix="pae-keepalive-") as temporary:
        path = Path(temporary) / "task.xml"
        path.write_bytes(b"\xff\xfe" + xml.encode("utf-16-le"))
        result = schtasks(["/Create", "/TN", name, "/XML", str(path), "/F"])
    if result.returncode != 0:
        print(f"ANOMALY:schedule_failed:owner_inspect {name} exit={result.returncode}")
        return 1
    print(f"keepalive:schedule_installed {name} every={args.every}m")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    def common(command: argparse.ArgumentParser, plan_required: bool) -> None:
        command.add_argument("--repo-root", default=".")
        command.add_argument("--work-root", default=".ai-work")
        command.add_argument("--plan", required=plan_required, help="plan directory")
        command.add_argument("--runner-arg", action="append", default=[],
                             help="extra run_concise.py argument; use --runner-arg=--no-cleanup")

    run = sub.add_parser("check", description="relaunch a dead runner when runnable work remains")
    common(run, False)
    run.add_argument("--quiet", action="store_true", help="omit ok/skip lines")
    run.add_argument("--dry-run", action="store_true", help="report what would be launched")
    run.add_argument("--max-restarts", type=int, default=3)
    run.add_argument("--within-minutes", type=int, default=180)
    run.add_argument("--verify-seconds", type=float, default=8)
    for name in ("pause", "resume"):
        common(sub.add_parser(name, description=f"{name} automatic relaunches for one plan"), True)
    sched = sub.add_parser("schedule", description="manage the OS scheduler entry (Windows schtasks; cron line elsewhere)")
    sched.add_argument("action", choices=["install", "remove", "status", "print"])
    common(sched, True)
    sched.add_argument("--every", type=int, default=20, help="minutes between ticks (default 20)")
    sched.add_argument("--yes", action="store_true", help="confirm creating the persistent OS task")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "check" and (args.max_restarts < 1 or args.within_minutes < 1 or args.verify_seconds < 0):
        parser.error("--max-restarts and --within-minutes must be positive")
    if args.command == "schedule" and not 1 <= args.every <= 1440:
        parser.error("--every must be 1..1440 minutes")
    try:
        if args.command == "check":
            return check(args)
        if args.command in {"pause", "resume"}:
            return pause(args, args.command == "pause")
        return schedule(args)
    except (OSError, ValueError, planctl.PlanError, lifecyclectl.LifecycleError) as exc:
        print(f"keepalive: invalid evidence ({type(exc).__name__})", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
