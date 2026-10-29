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
import subprocess
import sys
import tempfile
import time
import check_delivery as gate


def run(root: Path, task_id: str) -> int:
    entries = gate.catalog(root)
    gate.require(task_id in entries, "Unknown task")
    entry = entries[task_id]
    before = gate.code_fingerprint(root, entry)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S") + f"-{os.getpid()}"
    logs = gate.OUTPUT / "logs" / task_id / run_id
    gate.local(root, str(logs)).mkdir(parents=True, exist_ok=False)
    results = []
    for n, argv in enumerate(entry["required_checks"], 1):
        relative = str(logs / f"check-{n:02}.log")
        path = gate.local(root, relative)
        start = time.monotonic()
        with path.open("wb") as output:
            try:
                actual = list(argv)
                if actual[0] == "python":
                    actual[0] = sys.executable
                if os.name == "nt":
                    import shutil
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
    target = gate.local(root, str(gate.OUTPUT / f"{task_id}-checks.json"))
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
