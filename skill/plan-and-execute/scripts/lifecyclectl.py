#!/usr/bin/env python3
"""Resumable workspace lifecycle for plan-and-execute.

This module owns active-plan discovery, interruption recovery, runner leases,
resume dispatch, and guarded cancellation. It intentionally uses only the
Python standard library and never deletes repository implementation changes.
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import json
import os
import secrets
import shutil
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Iterator

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import planctl  # noqa: E402

ACTIVE_FILE = ".active-plan.json"
LEASE_FILE = ".runner-lease.json"
LIFECYCLE_SCHEMA_VERSION = 1
DEFAULT_WORK_ROOT = ".ai-work"
REMOTE_LEASE_MAX_AGE_SECONDS = 24 * 60 * 60


class LifecycleError(RuntimeError):
    """Raised when lifecycle state is ambiguous, unsafe, or invalid."""


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def parse_time(value: Any) -> dt.datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def resolve_repo_root(value: str | Path) -> Path:
    root = Path(value).expanduser().resolve()
    if not root.is_dir():
        raise LifecycleError(f"Repository root is not a directory: {root}")
    return root


def checked_work_root(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise LifecycleError("work_root must be a repository-relative path")
    return path


def work_directory(repo_root: Path, work_root: str = DEFAULT_WORK_ROOT) -> Path:
    relative = checked_work_root(work_root)
    current = repo_root
    for part in relative.parts:
        current = current / part
        if current.exists() and current.is_symlink():
            raise LifecycleError(f"Lifecycle work root must not traverse a symlink: {current}")
    return repo_root / relative


def active_path(repo_root: Path, work_root: str = DEFAULT_WORK_ROOT) -> Path:
    return work_directory(repo_root, work_root) / ACTIVE_FILE


def lease_path(plan_dir: Path) -> Path:
    return plan_dir / LEASE_FILE


def plan_requires_attention(manifest: dict[str, Any]) -> bool:
    if manifest.get("state") != "completed":
        return True
    return manifest.get("summary_status") != "generated"


def task_counts(manifest: dict[str, Any]) -> dict[str, int]:
    result = {"pending": 0, "in_progress": 0, "completed": 0, "blocked": 0}
    for task in manifest.get("tasks", []):
        status = str(task.get("status", ""))
        if status in result:
            result[status] += 1
    return result


def read_json_file(path: Path) -> dict[str, Any] | None:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return raw if isinstance(raw, dict) else None


def unlink_if_present(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        return


def relative_plan_path(repo_root: Path, plan_dir: Path) -> str:
    try:
        return plan_dir.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError as exc:
        raise LifecycleError(f"Plan is outside the repository: {plan_dir}") from exc


def active_record(plan_dir: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    repo_root = Path(manifest["repo_root"]).resolve()
    return {
        "schema_version": LIFECYCLE_SCHEMA_VERSION,
        "plan_id": manifest["plan_id"],
        "plan_path": relative_plan_path(repo_root, plan_dir),
        "repo_root": str(repo_root),
        "activated_at": utc_now(),
        "updated_at": utc_now(),
    }


def write_active(plan_dir: Path, manifest: dict[str, Any]) -> Path:
    repo_root = Path(manifest["repo_root"]).resolve()
    path = active_path(repo_root, str(manifest.get("work_root", DEFAULT_WORK_ROOT)))
    path.parent.mkdir(parents=True, exist_ok=True)
    planctl.atomic_write_json(path, active_record(plan_dir, manifest))
    return path


def clear_active(plan_dir: str | Path | None = None, *, repo_root: str | Path | None = None,
                 work_root: str = DEFAULT_WORK_ROOT) -> bool:
    if plan_dir is not None:
        try:
            loaded_dir, manifest = planctl.load_plan(plan_dir)
            root = Path(manifest["repo_root"]).resolve()
            work_root = str(manifest.get("work_root", work_root))
            expected_id = manifest.get("plan_id")
        except planctl.PlanError:
            loaded_dir = Path(plan_dir).expanduser().resolve()
            root = resolve_repo_root(repo_root or loaded_dir.parent.parent)
            expected_id = loaded_dir.name
    elif repo_root is not None:
        root = resolve_repo_root(repo_root)
        expected_id = None
    else:
        raise LifecycleError("clear_active requires plan_dir or repo_root")

    path = active_path(root, work_root)
    if not path.exists():
        return False
    record = read_json_file(path)
    if expected_id is not None and record and record.get("plan_id") != expected_id:
        return False
    unlink_if_present(path)
    return True


def load_plan_candidate(path: Path, repo_root: Path) -> tuple[Path, dict[str, Any]] | None:
    try:
        plan_dir, manifest = planctl.load_plan(path)
    except planctl.PlanError:
        return None
    try:
        manifest_root = Path(manifest["repo_root"]).resolve()
    except (KeyError, TypeError):
        return None
    if manifest_root != repo_root.resolve():
        return None
    return plan_dir, manifest


def scan_actionable_plans(repo_root: Path, work_root: str = DEFAULT_WORK_ROOT) -> list[tuple[Path, dict[str, Any]]]:
    directory = work_directory(repo_root, work_root)
    if not directory.is_dir() or directory.is_symlink():
        return []
    candidates: list[tuple[Path, dict[str, Any]]] = []
    for child in sorted(directory.iterdir(), key=lambda item: item.name):
        if not child.is_dir() or child.is_symlink() or child.name == "intake":
            continue
        loaded = load_plan_candidate(child, repo_root)
        if loaded and plan_requires_attention(loaded[1]):
            candidates.append(loaded)
    return candidates


def _record_plan_path(record: dict[str, Any], repo_root: Path) -> Path | None:
    if record.get("schema_version") != LIFECYCLE_SCHEMA_VERSION:
        return None
    if Path(str(record.get("repo_root", ""))).expanduser().resolve() != repo_root.resolve():
        return None
    raw = record.get("plan_path")
    if not isinstance(raw, str) or not raw.strip():
        return None
    relative = Path(raw)
    if relative.is_absolute() or ".." in relative.parts:
        return None
    return repo_root / relative


def discover_active(repo_root: str | Path = ".", work_root: str = DEFAULT_WORK_ROOT,
                    *, repair: bool = True) -> tuple[Path, dict[str, Any]] | None:
    root = resolve_repo_root(repo_root)
    pointer = active_path(root, work_root)
    if pointer.is_symlink():
        raise LifecycleError(f"Active-plan pointer must not be a symlink: {pointer}")
    record = read_json_file(pointer) if pointer.is_file() else None
    if record:
        candidate_path = _record_plan_path(record, root)
        if candidate_path is not None:
            loaded = load_plan_candidate(candidate_path, root)
            if loaded and plan_requires_attention(loaded[1]):
                return loaded
        unlink_if_present(pointer)
    elif pointer.exists():
        raise LifecycleError(f"Invalid active-plan pointer: {pointer}")

    candidates = scan_actionable_plans(root, work_root)
    if not candidates:
        return None
    if len(candidates) > 1:
        paths = ", ".join(relative_plan_path(root, item[0]) for item in candidates)
        raise LifecycleError(
            "Multiple unfinished plans were found. Select or cancel one explicitly: " + paths
        )
    plan_dir, manifest = candidates[0]
    if repair:
        write_active(plan_dir, manifest)
    return plan_dir, manifest


def activate_plan(plan_arg: str | Path, *, force: bool = False) -> tuple[Path, dict[str, Any]]:
    plan_dir, manifest = planctl.load_plan(plan_arg)
    if not plan_requires_attention(manifest):
        clear_active(plan_dir)
        return plan_dir, manifest
    root = Path(manifest["repo_root"]).resolve()
    work_root = str(manifest.get("work_root", DEFAULT_WORK_ROOT))
    try:
        existing = discover_active(root, work_root, repair=False)
    except LifecycleError:
        if not force:
            raise
        existing = None
    if existing and existing[0] != plan_dir and not force:
        raise LifecycleError(
            f"Another unfinished plan is active: {relative_plan_path(root, existing[0])}"
        )
    write_active(plan_dir, manifest)
    return plan_dir, manifest


def pid_is_alive(pid: Any) -> bool:
    try:
        numeric = int(pid)
    except (TypeError, ValueError):
        return False
    if numeric <= 0:
        return False
    try:
        os.kill(numeric, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False

    # On Linux a terminated child remains visible to kill(pid, 0) while it is
    # a zombie waiting to be reaped. Treat that state as stopped so cancel can
    # clean lifecycle artifacts without requiring an unnecessary --force.
    proc_stat = Path(f"/proc/{numeric}/stat")
    if proc_stat.is_file():
        try:
            raw = proc_stat.read_text(encoding="utf-8", errors="replace")
        except OSError:
            raw = ""
        closing = raw.rfind(")")
        if closing >= 0:
            fields = raw[closing + 2 :].split()
            if fields and fields[0] == "Z":
                return False
    return True


def read_lease(plan_dir: Path) -> dict[str, Any] | None:
    path = lease_path(plan_dir)
    if path.is_symlink():
        raise LifecycleError(f"Runner lease must not be a symlink: {path}")
    return read_json_file(path) if path.is_file() else None


def lease_is_live(lease: dict[str, Any] | None) -> bool:
    if not lease:
        return False
    host = str(lease.get("hostname", ""))
    if host == socket.gethostname():
        return pid_is_alive(lease.get("pid"))
    created = parse_time(lease.get("created_at"))
    if created is None:
        return False
    age = (dt.datetime.now(dt.timezone.utc) - created).total_seconds()
    return age < REMOTE_LEASE_MAX_AGE_SECONDS


def acquire_lease(plan_arg: str | Path, *, force: bool = False) -> dict[str, Any]:
    plan_dir, manifest = planctl.load_plan(plan_arg)
    path = lease_path(plan_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    token = {
        "schema_version": LIFECYCLE_SCHEMA_VERSION,
        "plan_id": manifest["plan_id"],
        "pid": os.getpid(),
        "hostname": socket.gethostname(),
        "nonce": secrets.token_hex(16),
        "created_at": utc_now(),
    }
    for _ in range(3):
        try:
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            existing = read_lease(plan_dir)
            if lease_is_live(existing) and not force:
                raise LifecycleError(
                    f"Plan {manifest['plan_id']} is already running "
                    f"(host={existing.get('hostname')}, pid={existing.get('pid')})"
                )
            unlink_if_present(path)
            continue
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(token, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        return token
    raise LifecycleError(f"Could not acquire runner lease: {path}")


def release_lease(plan_arg: str | Path, token: dict[str, Any] | None) -> bool:
    plan_dir = Path(plan_arg).expanduser().resolve()
    path = lease_path(plan_dir)
    if not path.exists():
        return False
    current = read_json_file(path)
    if token and current and current.get("nonce") != token.get("nonce"):
        return False
    unlink_if_present(path)
    return True


@contextlib.contextmanager
def runner_lease(plan_arg: str | Path, *, force: bool = False) -> Iterator[dict[str, Any]]:
    plan_dir, _ = planctl.load_plan(plan_arg)
    token = acquire_lease(plan_dir, force=force)
    try:
        yield token
    finally:
        release_lease(plan_dir, token)


def recover_interrupted_tasks(plan_arg: str | Path, *, allow_live_lease: bool = False) -> int:
    plan_dir, manifest = planctl.load_plan(plan_arg)
    lease = read_lease(plan_dir)
    if lease_is_live(lease) and int(lease.get("pid", -1)) != os.getpid() and not allow_live_lease:
        raise LifecycleError(
            f"Cannot recover while another runner is live (pid={lease.get('pid')})"
        )
    recovered = 0
    for task in manifest.get("tasks", []):
        if task.get("status") != "in_progress":
            continue
        task["status"] = "pending"
        task["last_error"] = "Previous execution ended unexpectedly; recovered for resume."
        task.setdefault("history", []).append(
            {"at": planctl.now_utc(), "event": "recovered_after_interruption"}
        )
        recovered += 1
    if recovered:
        planctl.append_event(
            manifest,
            "execution_recovered",
            recovered_tasks=recovered,
            technical_failures_added=0,
        )
        planctl.save_manifest(plan_dir, manifest)
    return recovered


def status_payload(repo_root: str | Path = ".", work_root: str = DEFAULT_WORK_ROOT) -> dict[str, Any]:
    root = resolve_repo_root(repo_root)
    active = discover_active(root, work_root)
    if not active:
        return {
            "status": "idle",
            "repo_root": str(root),
            "active": False,
            "action": "create_request",
        }
    plan_dir, manifest = active
    lease = read_lease(plan_dir)
    live = lease_is_live(lease)
    return {
        "status": "running" if live else str(manifest.get("state", "planned")),
        "repo_root": str(root),
        "active": True,
        "action": "already_running" if live else "resume",
        "plan_id": manifest.get("plan_id"),
        "plan": str(plan_dir),
        "plan_relative": relative_plan_path(root, plan_dir),
        "summary_status": manifest.get("summary_status"),
        "tasks": task_counts(manifest),
        "runner": lease if live else None,
    }


def terminate_live_runner(plan_dir: Path, *, force: bool) -> dict[str, Any] | None:
    lease = read_lease(plan_dir)
    if not lease_is_live(lease):
        unlink_if_present(lease_path(plan_dir))
        return lease
    host = str(lease.get("hostname", ""))
    pid = int(lease.get("pid", -1))
    if host != socket.gethostname():
        if not force:
            raise LifecycleError(
                f"Runner appears live on another host ({host}); rerun cancel with --force only after verifying it stopped"
            )
        unlink_if_present(lease_path(plan_dir))
        return lease
    if pid == os.getpid():
        raise LifecycleError("Refusing to cancel the lifecycle process itself")
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        unlink_if_present(lease_path(plan_dir))
        return lease
    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline and pid_is_alive(pid):
        time.sleep(0.1)
    if pid_is_alive(pid):
        if not force:
            raise LifecycleError(
                f"Runner pid {pid} did not stop. Retry with --force to terminate it before cleanup"
            )
        kill_signal = getattr(signal, "SIGKILL", signal.SIGTERM)
        os.kill(pid, kill_signal)
        deadline = time.monotonic() + 3.0
        while time.monotonic() < deadline and pid_is_alive(pid):
            time.sleep(0.1)
        if pid_is_alive(pid):
            raise LifecycleError(f"Runner pid {pid} could not be terminated safely")
    unlink_if_present(lease_path(plan_dir))
    return lease


def remove_plan_workspace(plan_arg: str | Path) -> dict[str, Any]:
    plan_dir, manifest = planctl.load_plan(plan_arg)
    plan_id = str(manifest.get("plan_id"))
    root = Path(manifest["repo_root"]).resolve()
    work_root = str(manifest.get("work_root", DEFAULT_WORK_ROOT))
    clear_active(plan_dir)
    planctl.remove_git_exclude_entry(manifest.get("git_exclude"))
    shutil.rmtree(plan_dir)
    directory = work_directory(root, work_root)
    try:
        directory.rmdir()
    except OSError:
        pass
    return {"plan_id": plan_id, "plan": str(plan_dir)}


def all_recognized_plans(repo_root: Path, work_root: str) -> list[tuple[Path, dict[str, Any]]]:
    directory = work_directory(repo_root, work_root)
    if not directory.is_dir() or directory.is_symlink():
        return []
    result: list[tuple[Path, dict[str, Any]]] = []
    for child in sorted(directory.iterdir(), key=lambda item: item.name):
        if not child.is_dir() or child.is_symlink() or child.name == "intake":
            continue
        loaded = load_plan_candidate(child, repo_root)
        if loaded:
            result.append(loaded)
    return result


def remove_intake(repo_root: Path, work_root: str) -> bool:
    intake = work_directory(repo_root, work_root) / "intake"
    if not intake.exists():
        return False
    if intake.is_symlink() or not intake.is_dir():
        raise LifecycleError(f"Refusing to remove invalid intake path: {intake}")
    shutil.rmtree(intake)
    return True


def cancel_workspace(repo_root: str | Path = ".", work_root: str = DEFAULT_WORK_ROOT,
                     *, all_plans: bool = False, force: bool = False) -> dict[str, Any]:
    root = resolve_repo_root(repo_root)
    selected: list[tuple[Path, dict[str, Any]]]
    if all_plans:
        selected = all_recognized_plans(root, work_root)
    else:
        active = discover_active(root, work_root)
        selected = [active] if active else []
    removed: list[dict[str, Any]] = []
    for plan_dir, _ in selected:
        terminate_live_runner(plan_dir, force=force)
        removed.append(remove_plan_workspace(plan_dir))
    pointer_removed = clear_active(repo_root=root, work_root=work_root)
    intake_removed = remove_intake(root, work_root)
    directory = work_directory(root, work_root)
    try:
        directory.rmdir()
    except OSError:
        pass
    return {
        "status": "cancelled" if removed or pointer_removed or intake_removed else "idle",
        "repo_root": str(root),
        "plans_removed": removed,
        "active_pointer_removed": pointer_removed,
        "intake_removed": intake_removed,
        "implementation_changes_preserved": True,
    }


def resume_workspace(args: argparse.Namespace) -> int:
    root = resolve_repo_root(args.repo_root)
    active = discover_active(root, args.work_root)
    if not active:
        payload = {
            "status": "idle",
            "action": "create_request",
            "message": "No unfinished plan is active in this workspace.",
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2) if args.json else payload["message"])
        return 3
    plan_dir, _ = active
    command = [sys.executable, str(SCRIPT_DIR / "run_isolated.py"), "--plan", str(plan_dir)]
    if args.provider:
        command.extend(["--provider", args.provider])
    if args.once:
        command.append("--once")
    if args.no_wait:
        command.append("--no-wait")
    if args.no_cleanup:
        command.append("--no-cleanup")
    completed = subprocess.run(command, cwd=root)
    return int(completed.returncode)


def emit(payload: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    if payload.get("active"):
        tasks = payload.get("tasks", {})
        print(
            f"Active plan {payload.get('plan_id')} ({payload.get('status')}): "
            f"{tasks.get('completed', 0)} completed, {tasks.get('pending', 0)} pending, "
            f"{tasks.get('in_progress', 0)} in progress, {tasks.get('blocked', 0)} blocked"
        )
        print(payload.get("plan"))
    elif payload.get("status") == "idle":
        print("No unfinished implementation is active; create a new request.")
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    def common(item: argparse.ArgumentParser) -> None:
        item.add_argument("--repo-root", default=".")
        item.add_argument("--work-root", default=DEFAULT_WORK_ROOT)
        item.add_argument("--json", action="store_true")

    current = sub.add_parser("current", help="Show or repair the active implementation pointer")
    common(current)

    activate = sub.add_parser("activate", help="Mark a validated plan as the active implementation")
    activate.add_argument("--plan", required=True)
    activate.add_argument("--force", action="store_true")
    activate.add_argument("--json", action="store_true")

    recover = sub.add_parser("recover", help="Return interrupted in-progress tasks to pending")
    recover.add_argument("--plan", required=True)
    recover.add_argument("--json", action="store_true")

    deactivate = sub.add_parser("deactivate", help="Clear the active pointer for a finished plan")
    deactivate.add_argument("--plan", required=True)
    deactivate.add_argument("--json", action="store_true")

    resume = sub.add_parser("resume", help="Resume the active implementation with the strict runner")
    common(resume)
    resume.add_argument("--provider", choices=["claude", "codex"])
    resume.add_argument("--once", action="store_true")
    resume.add_argument("--no-wait", action="store_true")
    resume.add_argument("--no-cleanup", action="store_true")

    cancel = sub.add_parser("cancel", help="Cancel the active implementation and remove its plan state")
    common(cancel)
    cancel.add_argument("--all", action="store_true", dest="all_plans")
    cancel.add_argument("--force", action="store_true")

    reset = sub.add_parser("reset", help="Remove every recognized plan-and-execute workspace artifact")
    common(reset)
    reset.add_argument("--force", action="store_true")

    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "current":
            emit(status_payload(args.repo_root, args.work_root), args.json)
            return 0
        if args.command == "activate":
            plan_dir, manifest = activate_plan(args.plan, force=args.force)
            emit({
                "status": "active",
                "active": True,
                "plan": str(plan_dir),
                "plan_id": manifest["plan_id"],
                "tasks": task_counts(manifest),
            }, args.json)
            return 0
        if args.command == "recover":
            recovered = recover_interrupted_tasks(args.plan)
            emit({"status": "recovered", "recovered_tasks": recovered}, args.json)
            return 0
        if args.command == "deactivate":
            removed = clear_active(args.plan)
            emit({"status": "deactivated", "active_pointer_removed": removed}, args.json)
            return 0
        if args.command == "resume":
            return resume_workspace(args)
        if args.command == "cancel":
            payload = cancel_workspace(
                args.repo_root,
                args.work_root,
                all_plans=args.all_plans,
                force=args.force,
            )
            emit(payload, args.json)
            return 0
        if args.command == "reset":
            payload = cancel_workspace(
                args.repo_root,
                args.work_root,
                all_plans=True,
                force=args.force,
            )
            emit(payload, args.json)
            return 0
        raise LifecycleError(f"Unknown command: {args.command}")
    except (LifecycleError, planctl.PlanError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
