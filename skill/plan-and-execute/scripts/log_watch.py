#!/usr/bin/env python3
"""Read only new, matching lines from a project log using a bounded cursor."""

from __future__ import annotations

import argparse
from collections import deque
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

import service_map


def cursor_for(root: Path, log_path: Path, pattern: str, log_id: str) -> Path:
    resource_id = os.environ.get("PAE_RESOURCE_WATCH_RESOURCE_ID", "manual")
    safe_parts = [re.sub(r"[^A-Za-z0-9_.-]", "_", value)[:80] for value in (resource_id, log_id)]
    fingerprint = hashlib.sha256(f"{log_path}\0{pattern}".encode("utf-8")).hexdigest()[:12]
    relative = Path(".ai-work/resource-watch/log-cursors") / ("-".join(safe_parts) + f"-{fingerprint}.json")
    return service_map.repo_path(root, relative.as_posix())


def load_cursor(path: Path) -> dict[str, Any]:
    if path.is_symlink():
        raise service_map.MapError(f"Refusing symlink cursor: {path}")
    if not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def save_cursor(path: Path, record: dict[str, Any], root: Path) -> None:
    service_map.repo_path(root, path.as_posix())
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise service_map.MapError("Refusing symlink cursor state")
    descriptor, raw_temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    temporary = Path(raw_temporary)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as output:
            json.dump(record, output, ensure_ascii=False, separators=(",", ":"))
            output.write("\n")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def scan(args: argparse.Namespace) -> int:
    root = Path(args.repo_root).resolve()
    log_path = Path(args.file).expanduser()
    if not log_path.is_absolute():
        log_path = root / log_path
    log_path = log_path.resolve(strict=True)
    if not log_path.is_file():
        raise service_map.MapError(f"Log is not a regular file: {log_path}")
    pattern = re.compile(args.pattern, re.IGNORECASE)
    cursor_path = cursor_for(root, log_path, args.pattern, args.id)
    previous = load_cursor(cursor_path)
    with log_path.open("rb") as source:
        metadata = os.fstat(source.fileno())
        identity = {"device": metadata.st_dev, "inode": metadata.st_ino}
        size = metadata.st_size
        same_file = (
            previous.get("path") == str(log_path)
            and previous.get("device") == identity["device"]
            and previous.get("inode") == identity["inode"]
            and isinstance(previous.get("offset"), int)
            and 0 <= previous["offset"] <= size
        )
        if same_file:
            start = previous["offset"]
        else:
            start = max(0, size - args.initial_tail_bytes)
        skipped = max(0, size - start - args.max_read_bytes)
        if skipped:
            start = size - args.max_read_bytes
        source.seek(start)
        content = source.read(args.max_read_bytes)
        end = source.tell()

    scan_start = start
    scan_content = content
    cursor_end = end
    if not same_file and start > 0:
        # A tail/rotated file may begin in the middle of an old line. Start at
        # the next complete line, or keep the cursor at `start` until one ends.
        first_newline = scan_content.find(b"\n")
        if first_newline < 0:
            scan_content = b""
            cursor_end = start
        else:
            scan_content = scan_content[first_newline + 1 :]
            scan_start = start + first_newline + 1
    if scan_content and not scan_content.endswith(b"\n"):
        # Do not classify half-written stack lines. Re-read this small pending
        # fragment at the next sample so patterns split across writes are found.
        last_newline = scan_content.rfind(b"\n")
        if last_newline < 0:
            scan_content = b""
            cursor_end = scan_start
        else:
            scan_content = scan_content[: last_newline + 1]
            cursor_end = scan_start + last_newline + 1

    lines = scan_content.decode("utf-8", errors="replace").splitlines()
    matches: deque[str] = deque(maxlen=args.max_matches)
    match_count = 0
    for line in lines:
        if pattern.search(line):
            match_count += 1
            matches.append(" ".join(line.split())[:500])
    save_cursor(cursor_path, {"path": str(log_path), **identity, "offset": cursor_end}, root)
    for line in matches:
        print(line)
    print(f"log-delta=read bytes={len(content)} matches={match_count} skipped_bytes={skipped}")
    if skipped:
        # The cursor advances after this sample, so fail visibly instead of
        # pretending the omitted interval was inspected. The raw source log is
        # still intact and can be reviewed directly if this happens.
        return 2
    return 1 if match_count else 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    command = commands.add_parser("scan", help="scan newly appended matching log lines")
    command.add_argument("--repo-root", default=".")
    command.add_argument("--file", required=True, help="project log path (absolute or relative to repo root)")
    command.add_argument("--id", required=True, help="stable health-check id")
    command.add_argument("--pattern", required=True, help="regular expression for relevant new lines")
    command.add_argument("--initial-tail-bytes", type=int, default=131072)
    command.add_argument("--max-read-bytes", type=int, default=1048576)
    command.add_argument("--max-matches", type=int, default=5)
    command.set_defaults(func=scan)
    return root


def main() -> int:
    args = parser().parse_args()
    if not 1024 <= args.initial_tail_bytes <= 10485760:
        print("log-watch error: initial-tail-bytes must be 1024..10485760", file=sys.stderr)
        return 2
    if not 1024 <= args.max_read_bytes <= 20971520:
        print("log-watch error: max-read-bytes must be 1024..20971520", file=sys.stderr)
        return 2
    if not 1 <= args.max_matches <= 100:
        print("log-watch error: max-matches must be 1..100", file=sys.stderr)
        return 2
    try:
        return int(args.func(args))
    except (OSError, ValueError, service_map.MapError, re.error) as exc:
        print(f"log-watch error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
