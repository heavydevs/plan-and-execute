#!/usr/bin/env python3
"""Run only the selected task's declared argv, under the outer resource watcher.

This does not implement the task, dispatch an LLM, mark a task complete, or approve
its receipt. Do not run it during research preparation: its new tests do not yet
exist. Full stdout/stderr is spooled to owned files rather than held in memory.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
import check_delivery as gate


def load_packet(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def stable(packet: dict) -> dict:
    """Outcome-defining projection of a checks packet; excludes run_id, durations and log paths."""
    checks = packet.get("checks")
    return {"schema_version": packet.get("schema_version"), "task_id": packet.get("task_id"),
            "input_fingerprint": packet.get("input_fingerprint"), "inputs_unchanged": packet.get("inputs_unchanged"),
            "checks": [{"argv": c.get("argv"), "exit_code": c.get("exit_code")} for c in checks] if isinstance(checks, list) else None}


def run(root: Path, task_id: str) -> int:
    entries = gate.catalog(root)
    gate.require(task_id in entries, "Unknown task")
    entry = entries[task_id]
    before = gate.code_fingerprint(root, entry)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S") + f"-{os.getpid()}-{uuid.uuid4().hex[:10]}"
    logs = gate.OUTPUT / "logs" / task_id / run_id
    gate.local(root, logs.as_posix()).mkdir(parents=True, exist_ok=False)
    results = []
    for n, argv in enumerate(entry["required_checks"], 1):
        relative = (logs / f"check-{n:02}.log").as_posix()
        path = gate.local(root, relative)
        start = time.monotonic()
        with path.open("wb") as output:
            try:
                actual = list(argv)
                if actual[0] == "python":
                    actual[0] = sys.executable
                if os.name == "nt":
                    actual[0] = shutil.which(actual[0]) or actual[0]
                completed = subprocess.run(actual, cwd=root, stdout=output, stderr=subprocess.STDOUT, check=False)
                code = completed.returncode
            except OSError as exc:
                output.write(f"execution_error={type(exc).__name__}\n".encode())
                code = 127
        results.append({"argv": argv, "exit_code": code, "duration_seconds": round(time.monotonic()-start, 3),
                        "log": relative, "log_sha256": gate.sha(path)})
        print(f"PROGRESS stage=declared_checks done={n} total={len(entry['required_checks'])}", flush=True)
        if code:
            break
    after = gate.code_fingerprint(root, entry)
    packet = {"schema_version": 1, "task_id": task_id, "input_fingerprint": before,
              "inputs_unchanged": before == after, "run_id": run_id, "checks": results}
    target = gate.local(root, (gate.OUTPUT / f"{task_id}-checks.json").as_posix())
    if target.is_file() and stable(load_packet(target)) == stable(packet):
        # Idempotent: identical task, input fingerprint and check outcomes keep the existing
        # file byte for byte, so a receipt that already binds its sha256 stays valid when the
        # runner re-runs this step. Volatile fields (run_id, durations, log paths) never decide.
        shutil.rmtree(gate.local(root, logs.as_posix()), ignore_errors=True)
    else:
        descriptor, tmp = tempfile.mkstemp(prefix=".checks-", dir=target.parent)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as out:
                json.dump(packet, out, indent=2); out.write("\n")
            os.replace(tmp, target)
        finally:
            Path(tmp).unlink(missing_ok=True)
    good = before == after and len(results) == len(entry["required_checks"]) and all(x["exit_code"] == 0 for x in results)
    return 0 if good else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[4]))
    parser.add_argument("--task", required=True)
    args = parser.parse_args()
    try:
        return run(Path(args.repo_root).resolve(), args.task)
    except (gate.GateError, OSError, KeyError, TypeError, ValueError) as exc:
        print(f"CHECKS REJECTED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
