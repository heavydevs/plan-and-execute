#!/usr/bin/env python3
"""Deterministic, fail-closed runner for ChatGPT-hosted PAE work.

Portable Python 3.10+ stdlib, no model API, no shell evaluation and no plan state writes.
Never represents a local code inspection as independent model review.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time
import uuid
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PLAN = ROOT / ".ai-work" / "20261028-skill-study-provider-switch"
TASK_INPUTS = ROOT / "docs/plans/20261028-skill-optimization/TASK_INPUTS.json"
RUN_ROOT = HERE / "runs"
MAP = ROOT / ".ai-work/SERVICE_MAP.md"
WATCH = ROOT / "skill/plan-and-execute/scripts/resource_watch.py"
REVIEW_DISPATCH = ROOT / "docs/plans/20261028-skill-optimization/support/review_dispatch.py"
ALLOWED_TASK = re.compile(r"^[0-9]{3}$")
ALLOWED_ID = re.compile(r"^P1_(?:TESTS_)?[0-9]{3}$")
MAX_LOG_BYTES = 5 * 1024 * 1024
DEFAULT_TIMEOUT = 600


class GateError(RuntimeError):
    pass


def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name("." + path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        with tmp.open("x", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def safe_path(value: str, *, must_exist: bool = True) -> Path:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise GateError("Invalid repository path")
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts or value.startswith("-"):
        raise GateError("Path outside repository denied")
    root = ROOT.resolve()
    current = root
    for part in candidate.parts:
        current = current / part
        if current.is_symlink():
            raise GateError("Symlink path denied: " + value)
    result = (root / candidate).resolve(strict=False)
    if not result.is_relative_to(root):
        raise GateError("Escaping path denied: " + value)
    if must_exist and not result.is_file():
        raise GateError("Missing required input: " + value)
    return result


def task_contract(task_id: str) -> dict[str, Any]:
    if not ALLOWED_TASK.fullmatch(task_id):
        raise GateError("Task id must be three decimal digits")
    doc = load(TASK_INPUTS)
    tasks = doc if isinstance(doc, list) else doc.get("tasks", [])
    task = next((t for t in tasks if str(t.get("id", "")).zfill(3) == task_id), None)
    if not isinstance(task, dict):
        raise GateError("Task not in assigned inputs: " + task_id)
    return task


def snapshot(task: dict[str, Any]) -> dict[str, str]:
    files: set[str] = set()
    for key in ("inputs", "write_scope"):
        for value in task.get(key, []):
            if isinstance(value, str):
                files.add(value)
    files.add("docs/plans/20261028-skill-optimization/TASK_INPUTS.json")
    result: dict[str, str] = {}
    for rel in sorted(files):
        path = safe_path(rel, must_exist=False)
        result[rel] = digest(path) if path.is_file() else "missing"
    return result


def git_head() -> str | None:
    try:
        result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                capture_output=True, text=True, timeout=10, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def source_status() -> dict[str, Any]:
    return {"repo_root": str(ROOT), "has_git_checkout": (ROOT / ".git").exists(),
            "git_head": git_head(), "plan_present": (PLAN / "manifest.json").is_file(),
            "task_inputs_present": TASK_INPUTS.is_file(), "resource_map_present": MAP.is_file(),
            "python": sys.version.split()[0], "codex_cli": shutil.which("codex") is not None,
            "claude_cli": shutil.which("claude") is not None,
            "github_actions": os.environ.get("GITHUB_ACTIONS") == "true"}


def task_status(task_id: str) -> dict[str, Any]:
    task = task_contract(task_id)
    info: dict[str, Any] = {"task_id": task_id, "kind": task.get("work_type"),
                             "review_of": task.get("review_of"), "requires_independent_review":
                             bool(task.get("requires_independent_review"))}
    if (PLAN / "manifest.json").is_file():
        plan = load(PLAN / "manifest.json")
        item = next((t for t in plan.get("tasks", []) if str(t.get("id", "")).zfill(3) == task_id), None)
        if item:
            info["status"] = item.get("status")
            info["checkpoints"] = [{"id": s.get("id"), "status": s.get("status")}
                                   for s in item.get("subtasks", [])]
    else:
        info["status"] = "unknown_no_checkout"
    return info


def make_run(task_id: str, stage: str) -> Path:
    rid = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:10]
    folder = RUN_ROOT / (task_id + "-" + stage + "-" + rid)
    folder.mkdir(parents=True, exist_ok=False)
    return folder


def exec_logged(argv: list[str], *, log: Path, timeout: int = DEFAULT_TIMEOUT) -> dict[str, Any]:
    """Always use explicit argv and process-group termination. No shell or indefinite buffers."""
    started = time.monotonic()
    log.parent.mkdir(parents=True, exist_ok=True)
    result: dict[str, Any] = {"argv": argv, "log": str(log.relative_to(ROOT)), "timeout_seconds": timeout}
    with log.open("xb") as out:
        if os.name == "nt":
            kwargs = {"creationflags": getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)}
        else:
            kwargs = {"start_new_session": True}
        try:
            process = subprocess.Popen(argv, cwd=ROOT, stdin=subprocess.DEVNULL,
                                       stdout=out, stderr=subprocess.STDOUT, shell=False, **kwargs)
            try:
                code = process.wait(timeout=timeout)
                result.update({"exit_code": code, "status": "passed" if code == 0 else "failed"})
            except subprocess.TimeoutExpired:
                if os.name == "nt":
                    process.kill()
                else:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                process.wait(timeout=20)
                result.update({"exit_code": None, "status": "timeout"})
        except OSError as exc:
            out.write(("Spawn error: " + str(exc) + "\n").encode("utf-8", errors="replace"))
            result.update({"exit_code": None, "status": "environment_error"})
    result.update({"duration_seconds": round(time.monotonic()-started, 3), "log_sha256": digest(log),
                   "log_bytes": log.stat().st_size})
    return result


def check_commands(task: dict[str, Any], mode: str) -> list[list[str]]:
    if mode == "targeted":
        checked: list[list[str]] = []
        for argv in task.get("required_checks", []):
            if not isinstance(argv, list) or len(argv) != 2 or argv[0] not in ("python", "node"):
                raise GateError("Unsupported declared check (no arbitrary shell allowed): " + repr(argv))
            safe_path(argv[1])
            checked.append(([sys.executable] if argv[0] == "python" else ["node"]) + [argv[1]])
        if not checked:
            raise GateError("Task has no declared targeted checks")
        return checked
    if mode == "watcher":
        if not MAP.is_file() or not WATCH.is_file():
            raise GateError("Resource watcher or its map is unavailable")
        return [[sys.executable, str(WATCH.relative_to(ROOT)), "run", "--repo-root", ".",
                 "--map", str(MAP.relative_to(ROOT)), "--validation", f"P1_{suffix}{task['id']}"]
                for suffix in ("TESTS_", "")]
    raise GateError("Unknown validation mode")


def run_checks(task_id: str, mode: str, timeout: int) -> dict[str, Any]:
    task = task_contract(task_id)
    commands = check_commands(task, mode)
    folder = make_run(task_id, mode)
    starting = snapshot(task)
    results: list[dict[str, Any]] = []
    for i, argv in enumerate(commands, 1):
        results.append(exec_logged(argv, log=folder / f"check-{i:02}.log", timeout=timeout))
        if results[-1]["status"] in ("timeout", "environment_error"):
            break
    ending = snapshot(task)
    same = starting == ending
    status = "passed" if same and len(results) == len(commands) and all(x["status"] == "passed" for x in results) else "failed"
    payload = {"schema": "chatgpt-executor/check-run/1", "task_id": task_id,
               "mode": mode, "status": status, "created_at": utc(), "head_sha": git_head(),
               "source_hashes": starting, "source_unchanged": same, "results": results,
               "checks_expected": len(commands), "checks_executed": len(results),
               "evidence_kind": "executed_local_checks", "not_independent_review": True}
    atomic_json(folder / "result.json", payload)
    return {"result_path": str((folder / "result.json").relative_to(ROOT)),
            "status": status, "checks_executed": len(results), "checks_expected": len(commands),
            "source_unchanged": same}


def review_packet(task_id: str) -> dict[str, Any]:
    task = task_contract(task_id)
    folder = make_run(task_id, "review-packet")
    payload = {"schema": "chatgpt-executor/review-packet/1", "task_id": task_id,
               "created_at": utc(), "head_sha": git_head(), "source_hashes": snapshot(task),
               "requires_independent_review": bool(task.get("requires_independent_review")),
               "review_of": task.get("review_of"),
               "prior_receipt": task.get("inputs", []),
               "required_checks": task.get("required_checks", []),
               "review_focus": ["Acceptance coverage", "Negative security tests", "Prompt injection and provenance",
                                "Filesystem/race boundaries", "Cost and token measurement", "Regression behavior"],
               "verdict": "not_reviewed", "reviewer": None,
               "independent_review_evidence": None,
               "not_independent_review": True}
    atomic_json(folder / "packet.json", payload)
    return {"packet_path": str((folder / "packet.json").relative_to(ROOT)),
            "verdict": "not_reviewed", "reviewer_available": bool(shutil.which("codex") or shutil.which("claude"))}


def dispatch_review(task_id: str, timeout: int) -> dict[str, Any]:
    task = task_contract(task_id)
    if not task.get("requires_independent_review"):
        raise GateError("No independent review was declared for this task")
    if not REVIEW_DISPATCH.is_file():
        raise GateError("Independent reviewer dispatcher missing")
    if not (shutil.which("codex") or shutil.which("claude")):
        raise GateError("INDEPENDENT_REVIEW_UNAVAILABLE: no authorized codex/claude CLI. Static checks cannot substitute.")
    folder = make_run(task_id, "dispatch")
    cmd = [sys.executable, str(REVIEW_DISPATCH.relative_to(ROOT)), "--repo-root", ".", "--task", task_id]
    result = exec_logged(cmd, log=folder / "dispatch.log", timeout=timeout)
    output = {"schema": "chatgpt-executor/dispatch-attempt/1", "task_id": task_id,
              "created_at": utc(), "result": result,
              "not_independent_review": result["status"] != "passed",
              "note": "Successful dispatcher output must separately satisfy original 015 receipt and review gate."}
    atomic_json(folder / "result.json", output)
    return {"result_path": str((folder / "result.json").relative_to(ROOT)),
            "status": result["status"], "exit_code": result["exit_code"]}


def gate(task_id: str, *, run_path: str | None, review_path: str | None) -> dict[str, Any]:
    """Non-mutating readiness gate: never sets task complete or creates a review receipt."""
    task = task_contract(task_id)
    reasons: list[str] = []
    if not run_path:
        reasons.append("missing_validation_evidence")
    else:
        run = load(safe_path(run_path))
        if run.get("schema") != "chatgpt-executor/check-run/1" or run.get("task_id") != task_id:
            reasons.append("invalid_validation_evidence")
        elif run.get("mode") != "watcher" or run.get("status") != "passed" or not run.get("source_unchanged"):
            reasons.append("validation_not_watcher_pass")
        elif run.get("source_hashes") != snapshot(task):
            reasons.append("validation_on_stale_sources")
        elif run.get("head_sha") != git_head():
            reasons.append("validation_on_different_commit")
    if task.get("requires_independent_review"):
        if not review_path:
            reasons.append("missing_independent_review")
        else:
            # A packet or self-review can never be upgraded to proof by passing its path.
            evidence = load(safe_path(review_path))
            if (evidence.get("schema") != "review-dispatch/1" or
                    evidence.get("task_id") != task_id or not evidence.get("session_id") or
                    evidence.get("model_tier") != "max" or not evidence.get("reviewed_inputs") or
                    evidence.get("exit_code") != 0):
                reasons.append("unverified_independent_review_record")
            else:
                reasons.append("independent_review_requires_original_delivery_gate")
    return {"task_id": task_id, "ready": not reasons, "reasons": reasons,
            "note": "This tool does not mark manifest status or replace the plan's delivery gate."}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    subs.add_parser("doctor")
    status = subs.add_parser("status"); status.add_argument("--task", default="015")
    run = subs.add_parser("run-checks"); run.add_argument("--task", required=True)
    run.add_argument("--mode", choices=["targeted", "watcher"], default="watcher")
    run.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    packet = subs.add_parser("review-packet"); packet.add_argument("--task", required=True)
    dispatch = subs.add_parser("dispatch-review"); dispatch.add_argument("--task", required=True)
    dispatch.add_argument("--timeout", type=int, default=3700)
    gate_parser = subs.add_parser("gate"); gate_parser.add_argument("--task", required=True)
    gate_parser.add_argument("--run-evidence"); gate_parser.add_argument("--review-evidence")
    subs.add_parser("self-test")
    args = parser.parse_args(argv)
    try:
        if args.command == "doctor":
            data = source_status()
        elif args.command == "status":
            data = task_status(args.task)
        elif args.command == "run-checks":
            if args.timeout < 5 or args.timeout > 7200:
                raise GateError("Timeout must be 5..7200 seconds")
            data = run_checks(args.task, args.mode, args.timeout)
        elif args.command == "review-packet":
            data = review_packet(args.task)
        elif args.command == "dispatch-review":
            data = dispatch_review(args.task, args.timeout)
        elif args.command == "gate":
            data = gate(args.task, run_path=args.run_evidence, review_path=args.review_evidence)
        else:
            from tests import test_taskctl
            data = test_taskctl.run()
        print(json.dumps(data, indent=2, ensure_ascii=False))
        if args.command == "gate":
            return 0 if data["ready"] else 2
        if args.command in ("run-checks", "dispatch-review"):
            return 0 if data["status"] == "passed" else 1
        return 0
    except (GateError, OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())