#!/usr/bin/env python3
"""Small POSIX process-session lookup shared by validation cleanup paths."""

from __future__ import annotations

import subprocess
from pathlib import Path


def posix_session_processes(session_id: int) -> list[int] | None:
    """List PIDs in a session, using `ps` or Linux procfs; None means unavailable."""
    try:
        result = subprocess.run(
            ["ps", "-e", "-o", "pid=", "-o", "sid="],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=3,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        result = None
    if result is not None and result.returncode == 0:
        pids: list[int] = []
        for line in result.stdout.splitlines():
            fields = line.split()
            if len(fields) != 2:
                continue
            try:
                pid, sid = (int(value) for value in fields)
            except ValueError:
                continue
            if sid == session_id:
                pids.append(pid)
        if pids:
            return pids

    proc_root = Path("/proc")
    if not proc_root.is_dir():
        return None
    pids = []
    try:
        entries = list(proc_root.iterdir())
    except OSError:
        return None
    for entry in entries:
        if not entry.name.isdigit():
            continue
        try:
            record = (entry / "stat").read_text(encoding="utf-8")
            close = record.rfind(")")
            fields = record[close + 2 :].split()
            # After the command field: state, ppid, pgrp, session.
            if close >= 0 and len(fields) >= 4 and int(fields[3]) == session_id:
                pids.append(int(entry.name))
        except (OSError, ValueError):
            continue
    return pids
