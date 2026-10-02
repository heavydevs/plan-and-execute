#!/usr/bin/env python3
"""Check that the uncommitted-hunk decision record covers the current working tree.

`check` compares docs/research/WORKTREE_AUDIT.json with `git diff` (default
three-line context) for the audited files: every current hunk needs a complete
keep entry, and every revert entry must no longer appear in the diff.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

DECISIONS = {"keep", "revert"}
EVIDENCE_KINDS = {"test", "rationale"}
REQUIRED_TEXT = ("file", "header", "purpose", "decision")


def repo_root() -> Path:
    output = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True
    ).stdout.strip()
    return Path(output)


def current_hunks(root: Path, files: list[str]) -> set[tuple[str, str]]:
    diff = subprocess.run(
        ["git", "-c", "core.quotepath=off", "diff", "--no-color", "--no-ext-diff", "-U3", "--", *files],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    ).stdout
    hunks: set[tuple[str, str]] = set()
    path = ""
    for line in diff.splitlines():
        if line.startswith("+++ "):
            path = line[4:].removeprefix("b/")
        elif line.startswith("@@ ") and path:
            hunks.add((path, line.rstrip()))
    return hunks


def entry_problems(index: int, entry: Any, files: set[str]) -> list[str]:
    if not isinstance(entry, dict):
        return [f"hunks[{index}] is not an object"]
    problems = [
        f"hunks[{index}].{key} is missing or empty"
        for key in REQUIRED_TEXT
        if not isinstance(entry.get(key), str) or not entry[key].strip()
    ]
    if entry.get("file") not in files:
        problems.append(f"hunks[{index}].file is not an audited file: {entry.get('file')!r}")
    if entry.get("decision") not in DECISIONS:
        problems.append(f"hunks[{index}].decision must be keep or revert")
    if not str(entry.get("header", "")).startswith("@@ "):
        problems.append(f"hunks[{index}].header is not a unified-diff hunk header")
    evidence = entry.get("evidence")
    if (
        not isinstance(evidence, dict)
        or evidence.get("kind") not in EVIDENCE_KINDS
        or not isinstance(evidence.get("detail"), str)
        or not evidence["detail"].strip()
    ):
        problems.append(f"hunks[{index}].evidence needs kind test|rationale and a detail")
    elif evidence["kind"] == "test" and not str(evidence.get("command", "")).strip():
        problems.append(f"hunks[{index}].evidence of kind test needs a command")
    return problems


def check(record_path: Path) -> list[str]:
    try:
        record = json.loads(record_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read record {record_path}: {exc}"]
    files = record.get("files")
    entries = record.get("hunks")
    if not isinstance(files, list) or not files or not all(isinstance(item, str) for item in files):
        return ["record.files must be a non-empty list of repository paths"]
    if not isinstance(entries, list):
        return ["record.hunks must be a list"]
    problems: list[str] = []
    recorded: dict[tuple[str, str], str] = {}
    for index, entry in enumerate(entries):
        issues = entry_problems(index, entry, set(files))
        problems.extend(issues)
        if issues:
            continue
        key = (entry["file"], entry["header"].rstrip())
        if key in recorded:
            problems.append(f"duplicate record for {key[0]} {key[1]}")
        recorded[key] = entry["decision"]
    live = current_hunks(repo_root(), files)
    for key in sorted(live - recorded.keys()):
        problems.append(f"unrecorded hunk: {key[0]} {key[1]}")
    for key, decision in sorted(recorded.items()):
        if decision == "keep" and key not in live:
            problems.append(f"keep hunk no longer in git diff: {key[0]} {key[1]}")
        elif decision == "revert" and key in live:
            problems.append(f"revert decision not applied: {key[0]} {key[1]}")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    check_parser = commands.add_parser("check", help="Validate the decision record against git diff")
    check_parser.add_argument("--record", default="docs/research/WORKTREE_AUDIT.json")
    args = parser.parse_args()
    record = Path(args.record)
    if not record.is_absolute():
        record = Path.cwd() / record
    problems = check(record)
    for problem in problems:
        print(f"FAIL {problem}")
    if problems:
        return 1
    print(f"Worktree audit record covers all current hunks: {record}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
