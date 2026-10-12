#!/usr/bin/env python3
"""Read-only plan watchdog; only watch's observation cache is writable."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import socket
import sys
import time
from pathlib import Path
from typing import Any

# Even status imports must not create files in an installed skill or repository.
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import availability
import jobctl
import lifecyclectl
import planctl
import progress_signal

DEFAULT_IDLE_SECONDS = 1800
SESSION_TAIL_BYTES = 128 * 1024
ACTIONS = {
    "blocked": "inspect_blocker",
    "permission_blocked": "owner_resolve_permission",
    "classifier_blocked": "owner_review_classifier",
    "runner_dead": "resume",
    "silent": "inspect_progress",
    "awaiting_next": "resume",
    "quota_resume_due": "resume",
    "job_failed": "inspect_job",
}


def timestamp(value: Any) -> float | None:
    parsed = lifecyclectl.parse_time(value)
    return parsed.timestamp() if parsed else None


def positive_seconds(value: Any, fallback: float) -> float:
    if isinstance(value, bool):
        return fallback
    try:
        number = float(value)
    except (TypeError, ValueError):
        return fallback
    return number if math.isfinite(number) and number > 0 else fallback


def token(value: Any) -> str:
    """Keep output to one compact line; never print raw error/provider text."""
    return re.sub(r"[^A-Za-z0-9_.-]", "_", str(value))[:100] or "unknown"


def log_evidence(path: Path) -> dict[str, Any] | None:
    if path.is_symlink():
        raise ValueError("Log evidence must not be a symlink")
    try:
        stat = path.stat()
        counter = progress_signal.probe_file(path)
    except FileNotFoundError:
        return None
    return {"mtime": stat.st_mtime, "size": stat.st_size, "progress": counter}


def session_metadata(path: Path) -> tuple[float | None, str | None]:
    """Read only session header metadata and the last complete event timestamp.

    No messages, tool arguments or provider output are retained or surfaced.
    Codex rollout mtimes can lag on Windows, so they are not an event clock.
    """
    try:
        if path.is_symlink():
            return None, None
        with path.open("rb") as source:
            header = source.readline(SESSION_TAIL_BYTES)
            source.seek(0, 2)
            offset = max(0, source.tell() - SESSION_TAIL_BYTES)
            source.seek(offset)
            block = source.read(SESSION_TAIL_BYTES)
        if offset:
            block = block.partition(b"\n")[2]
        lines = block.split(b"\n")[:-1]
        first = json.loads(header)
        cwd = first.get("payload", {}).get("cwd") if first.get("type") == "session_meta" else first.get("cwd")
        for line in reversed(lines):
            try:
                record = json.loads(line)
            except ValueError:
                continue
            event_at = timestamp(record.get("timestamp"))
            if event_at is not None:
                return event_at, cwd or record.get("cwd")
        return None, cwd
    except (OSError, ValueError, TypeError, AttributeError):
        return None, None


def provider_evidence(repo: Path, provider: str, started: float, now: float,
                      home: Path) -> dict[str, float]:
    result: dict[str, float] = {}
    if provider == "codex":
        directory = Path(os.environ.get("CODEX_HOME", str(home / ".codex"))) / "sessions"
        paths = directory.glob("**/rollout-*.jsonl")
    elif provider == "claude":
        directory = Path(os.environ.get("CLAUDE_CONFIG_DIR", str(home / ".claude"))) / "projects"
        project = re.sub(r"[^A-Za-z0-9]", "-", str(repo))
        paths = (directory / project).glob("*.jsonl")
    else:
        return result
    for path in paths:
        event_at, cwd = session_metadata(path)
        if event_at is None or not started <= event_at <= now:
            continue
        # A different repository's active conversation is not worker evidence.
        if provider == "codex" and (not cwd or Path(cwd).resolve() != repo):
            continue
        if cwd and Path(cwd).resolve() != repo:
            continue
        result[str(path)] = event_at
    return result


def task_start(task: dict[str, Any], lease: dict[str, Any] | None,
               manifest: dict[str, Any]) -> float:
    claims = [timestamp(event.get("at")) for event in task.get("history", [])
              if event.get("event") in {"claimed", "design_claimed"}]
    return max([value for value in claims if value is not None] or
               [timestamp(task.get("started_at")) or
                timestamp((lease or {}).get("created_at")) or
                timestamp(manifest.get("updated_at")) or 0])


def collect_plan(plan_dir: Path, manifest: dict[str, Any], *, now: float,
                 home: Path) -> list[dict[str, Any]]:
    lease = lifecyclectl.read_lease(plan_dir)
    live = lifecyclectl.lease_is_live(lease)
    repo = Path(manifest["repo_root"]).resolve()
    tasks = manifest.get("tasks", [])
    ready = planctl.next_runnable_task(manifest)
    running = any(task.get("status") == "in_progress" for task in tasks)
    config = lifecyclectl.read_json_file(plan_dir / planctl.CONFIG) or {}
    items: list[dict[str, Any]] = []
    job_owners = {job_id: task for task in tasks
                  for job_id in task.get("validation_jobs", [])}
    for task in tasks:
        if task.get("status") == "completed":
            continue
        task_id = str(task["id"])
        if re.fullmatch(r"[A-Za-z0-9_-]{1,100}", task_id) is None:
            raise ValueError("Invalid watchdog task identifier")
        start = task_start(task, lease, manifest)
        logs: dict[str, Any] = {}
        attempt = int(task.get("attempts", 0))
        if task.get("status") == "in_progress":
            for path in (plan_dir / "logs").glob(f"{task_id}-*attempt-{attempt}-*.log"):
                evidence = log_evidence(path)
                if evidence:
                    logs[str(path)] = evidence
        provider = (task.get("current_route") or {}).get("provider", task.get("provider", ""))
        sessions = (provider_evidence(repo, provider, start, now, home)
                    if live and (lease or {}).get("hostname") == socket.gethostname()
                    and task.get("status") == "in_progress" else {})
        ledger = availability.read(plan_dir, task_id)
        cooldowns = [entry["until"] for entry in ledger["cooldowns"].values()]
        latest = max([start, *[value["mtime"] for value in logs.values()], *sessions.values()])
        items.append({
            "key": f"{token(manifest['plan_id'])}/{token(task_id)}", "plan": str(plan_dir),
            "status": task.get("status"), "live": live, "started": start,
            "window": positive_seconds(task.get("task_idle_timeout_seconds",
                       config.get("task_idle_timeout_seconds")), DEFAULT_IDLE_SECONDS),
            "latest": min(now, latest), "logs": logs, "sessions": sessions,
            "error": str(task.get("last_error") or ""),
            "ready": ready is not None and ready.get("id") == task_id,
            "running": running, "cooldowns": cooldowns,
        })
    jobs_dir = plan_dir / "jobs"
    if jobs_dir.is_symlink():
        raise ValueError("Jobs directory must not be a symlink")
    if jobs_dir.is_dir():
        for directory in sorted(jobs_dir.iterdir()):
            if not directory.is_dir():
                continue
            record = jobctl.status_job(plan_dir, directory.name)
            # Old terminal validations of completed TODOs no longer need attention.
            if (job_owners.get(directory.name, {}).get("status") == "completed"
                    and record.get("status") not in jobctl.ACTIVE):
                continue
            evidence = log_evidence(Path(record["log_path"]))
            start = timestamp(record.get("started_at")) or 0
            latest = max(start, now - max(0, float(record["idle_seconds"]))) if "idle_seconds" in record else start
            if evidence:
                latest = max(latest, evidence["mtime"])
            items.append({
                "key": f"{token(manifest['plan_id'])}/job-{token(directory.name)}",
                "plan": str(plan_dir), "status": record["status"], "job": True,
                "live": record["status"] in jobctl.ACTIVE, "started": start,
                "window": positive_seconds(record.get("idle_timeout_seconds"), DEFAULT_IDLE_SECONDS),
                "latest": min(now, latest), "logs": {record["log_path"]: evidence} if evidence else {},
                "sessions": {}, "reason": token(record.get("reason", record["status"])),
            })
    if not items:
        items.append({"key": f"{token(manifest['plan_id'])}/plan", "plan": str(plan_dir),
                      "status": "summary_pending" if manifest.get("summary_status") != "generated" else "completed",
                      "live": live, "logs": {}, "sessions": {}})
    return items


def collect(args: argparse.Namespace, now: float) -> list[dict[str, Any]]:
    repo = lifecyclectl.resolve_repo_root(args.repo_root)
    candidates = ([planctl.load_plan(args.plan)] if args.plan else
                  lifecyclectl.scan_actionable_plans(repo, args.work_root))
    return [item for directory, manifest in candidates
            for item in collect_plan(directory, manifest, now=now, home=Path.home())]


def classify(item: dict[str, Any], now: float) -> tuple[str | None, str]:
    status = item["status"]
    if item.get("job"):
        if status in {"failed", "stalled", "stopped"}:
            return "job_failed", f"state={token(status)} reason={item['reason']}"
        if status in jobctl.ACTIVE and now - item["latest"] >= item["window"]:
            return "silent", f"state={token(status)} window={item['window']:g}s"
        return None, f"job_{token(status)}"
    if status == "blocked":
        reason = item["error"].lower()
        if re.search(r"permission|approval|access.denied|permiss[aã]o|autoriz", reason):
            return "permission_blocked", "state=blocked reason=permission"
        if re.search(r"classif|classifier", reason):
            return "classifier_blocked", "state=blocked reason=classifier"
        return "blocked", "state=blocked"
    # An expired lease left after normal --once completion is not a dead runner.
    if status == "in_progress" and not item["live"]:
        return "runner_dead", "state=in_progress lease=not_live"
    if status == "in_progress":
        if now - item["latest"] >= item["window"]:
            return "silent", f"state=in_progress window={item['window']:g}s"
        return None, "running"
    cooldowns = item.get("cooldowns", [])
    if cooldowns:
        # The dispatch chain can resume as soon as any recorded route is due.
        due = min(cooldowns)
        if due > now:
            return None, f"cooldown_until={due:g}"
        if not item["live"] and item.get("ready"):
            return "quota_resume_due", "state=pending cooldown=due"
    if status == "summary_pending" and not item["live"]:
        return "awaiting_next", "state=summary_pending"
    if item.get("ready") and not item["live"] and not item.get("running"):
        return "awaiting_next", "state=pending"
    return None, "runner_wait" if item["live"] else token(status)


def render(item: dict[str, Any], finding: tuple[str | None, str]) -> str:
    anomaly, detail = finding
    if anomaly is None:
        return f"ok {item['key']} {detail}"
    if ACTIONS[anomaly] == "resume":
        import shlex
        import subprocess
        argv = ["python", str(Path(__file__).resolve().with_name("run_concise.py")),
                "--plan", item["plan"], "--once"]
        command = subprocess.list2cmdline(argv) if os.name == "nt" else shlex.join(argv)
        detail += " command=" + command.replace("\r", " ").replace("\n", " ")
    return f"ANOMALY:{anomaly}:{ACTIONS[anomaly]} {item['key']} {detail}"


def status(args: argparse.Namespace) -> int:
    now = time.time()
    anomalous = False
    for item in collect(args, now):
        finding = classify(item, now)
        anomalous |= finding[0] is not None
        if finding[0] is not None or not args.quiet:
            print(render(item, finding), flush=True)
    return int(anomalous)


def observe(items: list[dict[str, Any]], previous: dict[str, Any],
            now: float) -> tuple[list[str], dict[str, Any], int]:
    """Cache observed changes, not raw logs; stable anomalies do not repeat."""
    observations: dict[str, Any] = {}
    anomalies: dict[str, str] = {}
    lines: list[str] = []
    for raw in items:
        item = dict(raw)
        signature = {"started": item.get("started"), "logs": item["logs"], "sessions": item["sessions"]}
        old = previous.get("observations", {}).get(item["key"])
        last = item.get("latest", now)
        if old and old.get("signature", {}).get("started") == signature["started"]:
            last = max(last, old.get("latest", last))
            old_signature = old.get("signature", {})
            if any(old_signature.get(kind, {}).get(key) != value
                   for kind in ("logs", "sessions") for key, value in signature[kind].items()):
                last = now
        item["latest"] = last
        observations[item["key"]] = {"signature": signature, "latest": last}
        finding = classify(item, now)
        if finding[0] is not None:
            line = render(item, finding)
            anomalies[item["key"]] = line
            if previous.get("anomalies", {}).get(item["key"]) != line:
                lines.append(line)
    return lines, {"version": 1, "observations": observations, "anomalies": anomalies}, int(bool(anomalies))


def cache_path(args: argparse.Namespace) -> Path:
    repo = lifecyclectl.resolve_repo_root(args.repo_root)
    directory = lifecyclectl.work_directory(repo, ".ai-work/watchdog")
    selector = json.dumps([str(repo), args.work_root,
                           str(Path(args.plan).expanduser().resolve()) if args.plan else None])
    path = directory / (hashlib.sha256(selector.encode()).hexdigest()[:24] + ".json")
    if path.is_symlink():
        raise ValueError("Watchdog cache must not be a symlink")
    return path


def watch(args: argparse.Namespace) -> int:
    path = cache_path(args)
    previous = lifecyclectl.read_json_file(path) or {}
    if previous and (previous.get("version") != 1 or
                     not isinstance(previous.get("observations"), dict) or
                     not isinstance(previous.get("anomalies"), dict)):
        raise ValueError("Invalid watchdog cache")
    iteration = 0
    while True:
        now = time.time()
        lines, current, code = observe(collect(args, now), previous, now)
        for line in lines:
            print(line, flush=True)
        path.parent.mkdir(parents=True, exist_ok=True)
        planctl.atomic_write_json(path, current)
        previous = current
        iteration += 1
        if args.iterations and iteration >= args.iterations:
            return code
        time.sleep(args.interval)


def interval(value: str) -> int:
    number = int(value)
    if not 300 <= number <= 600:
        raise argparse.ArgumentTypeError("watch interval must be 300..600 seconds")
    return number


def build_parser() -> argparse.ArgumentParser:
    classes = ", ".join(f"{name}->{action}" for name, action in ACTIONS.items())
    help_text = ("One line per task/job: ok <plan>/<item> <state> or "
                 "ANOMALY:<class>:<action> <plan>/<item> <detail>. "
                 "Classes/actions: " + classes + ". Exit codes: 0 healthy, "
                 "1 anomaly, 2 invalid arguments/evidence. No plan or process changes. "
                 f"Default idle window: {DEFAULT_IDLE_SECONDS}s; positive per-item idle overrides it.")
    parser = argparse.ArgumentParser(description=__doc__, epilog=help_text)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("status", "watch"):
        command = sub.add_parser(name, description=help_text,
                                 help="snapshot" if name == "status" else "deduplicated anomaly polling")
        command.add_argument("--repo-root", default=".")
        command.add_argument("--work-root", default=".ai-work")
        command.add_argument("--plan", help="select one plan without scanning other plans")
        command.add_argument("--quiet", action="store_true", help="omit ok lines (watch always omits them)")
        if name == "watch":
            command.add_argument("--interval", type=interval, default=300, help="300..600 seconds; default 300")
            command.add_argument("--iterations", type=int, default=0, help="stop after N snapshots; 0 watches until interrupted")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "watch" and args.iterations < 0:
        parser.error("--iterations must be nonnegative")
    try:
        return status(args) if args.command == "status" else watch(args)
    except KeyboardInterrupt:
        return 0
    except (OSError, ValueError, planctl.PlanError, lifecyclectl.LifecycleError,
            availability.AvailabilityError) as exc:
        # Raw evidence can contain credentials; report only the failure type.
        print(f"watchdog: invalid evidence ({type(exc).__name__})", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
