#!/usr/bin/env python3
"""Small POSIX process-session lookup shared by validation cleanup paths."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

_GROUP_CPU_CENTISECONDS: dict[int, dict[int, int]] = {}


def _remember_group_cpu(group_id: int, pid: int, cpu_centiseconds: int) -> int:
    """Return monotonic process-group CPU time, retaining totals for exited children."""
    observed = _GROUP_CPU_CENTISECONDS.setdefault(group_id, {})
    observed[pid] = max(observed.get(pid, 0), cpu_centiseconds)
    return sum(observed.values()) // 100


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


def posix_group_metrics(group_id: int) -> dict[str, object] | None:
    """Return aggregate CPU time and a bounded process snapshot for one process group."""
    # Procfs retains sub-second CPU ticks and avoids rounding each short-lived
    # child separately; BSD/macOS systems fall through to `ps` below.
    proc_metrics = _proc_group_metrics(group_id)
    if proc_metrics is not None:
        return proc_metrics
    try:
        result = subprocess.run(
            ["ps", "-e", "-o", "pgid=", "-o", "pid=", "-o", "stat=", "-o", "etime=", "-o", "time=", "-o", "comm="],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=3,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return _proc_group_metrics(group_id)
    if result.returncode != 0:
        return _proc_group_metrics(group_id)
    cpu_seconds = 0
    members: list[dict[str, object]] = []
    for line in result.stdout.splitlines():
        fields = line.split(maxsplit=5)
        if len(fields) < 6:
            continue
        try:
            pgid, pid = int(fields[0]), int(fields[1])
        except ValueError:
            continue
        if pgid != group_id:
            continue
        member_cpu = _parse_cpu_time(fields[4])
        cpu_seconds = _remember_group_cpu(group_id, pid, member_cpu * 100)
        if len(members) < 20:
            members.append({"pid": pid, "state": fields[2], "elapsed": fields[3], "cpu_seconds": member_cpu, "command": fields[5][:80]})
    if not members:
        return None
    return {"cpu_seconds": cpu_seconds, "processes": members}


def _parse_cpu_time(value: str) -> int:
    value = value.split(".", 1)[0]
    days = 0
    if "-" in value:
        day_text, value = value.split("-", 1)
        try:
            days = int(day_text)
        except ValueError:
            return 0
    try:
        parts = [int(part) for part in value.split(":")]
    except ValueError:
        return 0
    seconds = 0
    for part in parts:
        seconds = seconds * 60 + part
    return days * 86400 + seconds


def _proc_group_metrics(group_id: int) -> dict[str, object] | None:
    proc_root = Path("/proc")
    if not proc_root.is_dir():
        return None
    try:
        ticks_per_second = int(os.sysconf("SC_CLK_TCK"))
        entries = list(proc_root.iterdir())
    except (OSError, ValueError):
        return None
    cpu_seconds = 0
    members: list[dict[str, object]] = []
    for entry in entries:
        if not entry.name.isdigit():
            continue
        try:
            record = (entry / "stat").read_text(encoding="utf-8")
            close = record.rfind(")")
            fields = record[close + 2 :].split()
            # After comm: state, ppid, pgrp, session, ..., utime, stime.
            if close < 0 or len(fields) < 13 or int(fields[2]) != group_id:
                continue
            pid = int(entry.name)
            member_ticks = int(fields[11]) + int(fields[12])
            member_centiseconds = member_ticks * 100 // max(1, ticks_per_second)
            cpu_seconds = _remember_group_cpu(group_id, pid, member_centiseconds)
            member_cpu = member_centiseconds // 100
            if len(members) < 20:
                comm = record[record.find("(") + 1 : close]
                members.append({"pid": pid, "state": fields[0], "elapsed": "", "cpu_seconds": member_cpu, "command": comm[:80]})
        except (OSError, ValueError):
            continue
    if not members:
        return None
    return {"cpu_seconds": cpu_seconds, "processes": members}
