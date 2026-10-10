#!/usr/bin/env python3
"""Standard-library process-tree ownership, CPU accounting and bounded cleanup."""

from __future__ import annotations

import os
import json
import shutil
import signal
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path
from typing import Any

_GROUP_CPU_CENTISECONDS: dict[int, dict[int, int]] = {}
_CPU_LOCK = threading.RLock()


def _remember_group_cpu(group_id: int, pid: int, cpu_centiseconds: int) -> float:
    """Return monotonic process-group CPU time, retaining totals for exited children."""
    with _CPU_LOCK:
        observed = _GROUP_CPU_CENTISECONDS.setdefault(group_id, {})
        observed[pid] = max(observed.get(pid, 0), cpu_centiseconds)
        return sum(observed.values()) / 100


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
            members.append({"pid": pid, "state": fields[2], "elapsed": fields[3], "cpu_seconds": member_cpu})
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
                members.append({"pid": pid, "state": fields[0], "elapsed": "", "cpu_seconds": member_cpu})
        except (OSError, ValueError):
            continue
    if not members:
        return None
    return {"cpu_seconds": cpu_seconds, "processes": members}


_WINDOWS_API: Any = None


def _windows_api() -> Any:
    """Declare Win32 structures here so importing this module also works on POSIX."""
    global _WINDOWS_API
    if _WINDOWS_API is not None:
        return _WINDOWS_API
    import ctypes
    from ctypes import wintypes
    from types import SimpleNamespace

    class BasicLimits(ctypes.Structure):
        _fields_ = [("process_time", ctypes.c_longlong), ("job_time", ctypes.c_longlong),
                    ("flags", wintypes.DWORD), ("min_working_set", ctypes.c_size_t),
                    ("max_working_set", ctypes.c_size_t), ("active_limit", wintypes.DWORD),
                    ("affinity", ctypes.c_size_t), ("priority", wintypes.DWORD),
                    ("scheduling", wintypes.DWORD)]

    class IoCounters(ctypes.Structure):
        _fields_ = [(name, ctypes.c_ulonglong) for name in
                    ("read_ops", "write_ops", "other_ops", "read_bytes", "write_bytes", "other_bytes")]

    class ExtendedLimits(ctypes.Structure):
        _fields_ = [("basic", BasicLimits), ("io", IoCounters),
                    ("process_memory", ctypes.c_size_t), ("job_memory", ctypes.c_size_t),
                    ("peak_process_memory", ctypes.c_size_t), ("peak_job_memory", ctypes.c_size_t)]

    class Accounting(ctypes.Structure):
        _fields_ = [("user", ctypes.c_longlong), ("kernel", ctypes.c_longlong),
                    ("period_user", ctypes.c_longlong), ("period_kernel", ctypes.c_longlong),
                    ("faults", wintypes.DWORD), ("total", wintypes.DWORD),
                    ("active", wintypes.DWORD), ("terminated", wintypes.DWORD)]

    class ProcessEntry(ctypes.Structure):
        _fields_ = [("size", wintypes.DWORD), ("usage", wintypes.DWORD),
                    ("pid", wintypes.DWORD), ("heap", ctypes.c_size_t),
                    ("module", wintypes.DWORD), ("threads", wintypes.DWORD),
                    ("parent", wintypes.DWORD), ("priority", wintypes.LONG),
                    ("flags", wintypes.DWORD), ("exe", wintypes.WCHAR * 260)]

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    declarations = {
        "CreateJobObjectW": ([ctypes.c_void_p, wintypes.LPCWSTR], wintypes.HANDLE),
        "SetInformationJobObject": ([wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD], wintypes.BOOL),
        "QueryInformationJobObject": ([wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD, ctypes.c_void_p], wintypes.BOOL),
        "AssignProcessToJobObject": ([wintypes.HANDLE, wintypes.HANDLE], wintypes.BOOL),
        "TerminateJobObject": ([wintypes.HANDLE, wintypes.UINT], wintypes.BOOL),
        "CloseHandle": ([wintypes.HANDLE], wintypes.BOOL),
        "CreateEventW": ([ctypes.c_void_p, wintypes.BOOL, wintypes.BOOL, wintypes.LPCWSTR], wintypes.HANDLE),
        "OpenEventW": ([wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR], wintypes.HANDLE),
        "SetEvent": ([wintypes.HANDLE], wintypes.BOOL),
        "WaitForSingleObject": ([wintypes.HANDLE, wintypes.DWORD], wintypes.DWORD),
        "CreateToolhelp32Snapshot": ([wintypes.DWORD, wintypes.DWORD], wintypes.HANDLE),
        "Process32FirstW": ([wintypes.HANDLE, ctypes.POINTER(ProcessEntry)], wintypes.BOOL),
        "Process32NextW": ([wintypes.HANDLE, ctypes.POINTER(ProcessEntry)], wintypes.BOOL),
        "OpenProcess": ([wintypes.DWORD, wintypes.BOOL, wintypes.DWORD], wintypes.HANDLE),
        "GetProcessTimes": ([wintypes.HANDLE, ctypes.POINTER(wintypes.FILETIME),
                             ctypes.POINTER(wintypes.FILETIME), ctypes.POINTER(wintypes.FILETIME),
                             ctypes.POINTER(wintypes.FILETIME)], wintypes.BOOL),
        "TerminateProcess": ([wintypes.HANDLE, wintypes.UINT], wintypes.BOOL),
    }
    for name, (arguments, result) in declarations.items():
        function = getattr(kernel, name)
        function.argtypes, function.restype = arguments, result
    _WINDOWS_API = SimpleNamespace(ctypes=ctypes, wintypes=wintypes, kernel=kernel,
                                   ExtendedLimits=ExtendedLimits, Accounting=Accounting,
                                   ProcessEntry=ProcessEntry)
    return _WINDOWS_API


def _windows_pid_time(pid: int) -> tuple[int, float] | None:
    api = _windows_api()
    handle = api.kernel.OpenProcess(0x1000, False, pid)
    if not handle:
        return None
    values = [api.wintypes.FILETIME() for _ in range(4)]
    try:
        if not api.kernel.GetProcessTimes(handle, *(api.ctypes.byref(value) for value in values)):
            return None
        ticks = [(int(value.dwHighDateTime) << 32) | int(value.dwLowDateTime) for value in values]
        return ticks[0], (ticks[2] + ticks[3]) / 10_000_000
    finally:
        api.kernel.CloseHandle(handle)


def _windows_processes() -> dict[int, tuple[int, str]]:
    api = _windows_api()
    snapshot = api.kernel.CreateToolhelp32Snapshot(2, 0)
    if not snapshot or snapshot == api.ctypes.c_void_p(-1).value:
        return {}
    entry = api.ProcessEntry()
    entry.size = api.ctypes.sizeof(entry)
    result: dict[int, tuple[int, str]] = {}
    try:
        present = api.kernel.Process32FirstW(snapshot, api.ctypes.byref(entry))
        while present:
            result[int(entry.pid)] = (int(entry.parent), str(entry.exe))
            present = api.kernel.Process32NextW(snapshot, api.ctypes.byref(entry))
    finally:
        api.kernel.CloseHandle(snapshot)
    return result


def launch(command: Any, **options: Any) -> subprocess.Popen:
    """Launch an owned group; on Windows attach a waiting guard before releasing argv.

    A Job Object accounts for exited descendants and kills them on close. Hosts
    that refuse nested Job assignment retain PID identities and use tree cleanup.
    """
    if os.name != "nt":
        options.setdefault("start_new_session", True)
        owns_session = options["start_new_session"]
        if not owns_session:
            configured_env = options.pop("env", None)
            env = dict(os.environ if configured_env is None else configured_env)
            env["PAE_PROCESS_TREE_GUARD"] = json.dumps({"command": command,
                                                       "shell": bool(options.pop("shell", False)),
                                                       "executable": options.pop("executable", None)})
            process = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "_posix-guard"], env=env, **options)
        else:
            process = subprocess.Popen(command, **options)
        with _CPU_LOCK:
            _GROUP_CPU_CENTISECONDS.pop(process.pid, None)
        process._pae_owned_group = True
        process._pae_owned_session = owns_session
        process._pae_posix_lock = threading.RLock()
        process._pae_posix_known = {}
        process._pae_posix_cpu = {}
        process._pae_posix_exited_cpu = 0.0
        process._pae_posix_total = 0.0
        process._pae_posix_live = {}
        return process
    api = _windows_api()
    if isinstance(command, (list, tuple)) and command and not options.get("shell"):
        command = [shutil.which(str(command[0])) or command[0], *command[1:]]
    name = "Local\\PAE-process-" + uuid.uuid4().hex
    ready = api.kernel.CreateEventW(None, True, False, name)
    if not ready:
        raise OSError("Cannot create process-tree startup guard")
    configured_env = options.pop("env", None)
    env = dict(os.environ if configured_env is None else configured_env)
    spec = {"command": command, "shell": bool(options.pop("shell", False)),
            "executable": options.pop("executable", None)}
    env["PAE_PROCESS_TREE_GUARD"] = json.dumps(spec)
    job = api.kernel.CreateJobObjectW(None, None)
    if job:
        limits = api.ExtendedLimits()
        limits.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not api.kernel.SetInformationJobObject(job, 9, api.ctypes.byref(limits), api.ctypes.sizeof(limits)):
            api.kernel.CloseHandle(job)
            job = None
    process: subprocess.Popen | None = None
    try:
        process = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "_windows-guard", name], env=env, **options)
        process._pae_job_handle = None
        process._pae_tree_lock = threading.RLock()
        identity = _windows_pid_time(process.pid)
        process._pae_known_pids = {process.pid: identity[0]} if identity else {}
        process._pae_cpu_totals = {}
        if job and api.kernel.AssignProcessToJobObject(job, int(process._handle)):
            process._pae_job_handle = job
            job = None
        process._pae_tree_backend = "windows-job" if process._pae_job_handle else "windows-pid-fallback"
        if not api.kernel.SetEvent(ready):
            raise OSError("Cannot release process-tree startup guard")
        # Keep the named event alive until the guard interpreter has opened it.
        process._pae_ready_handle = ready
        ready = None
        return process
    except BaseException:
        if process is not None:
            process.kill()
            close(process)
        raise
    finally:
        if ready:
            api.kernel.CloseHandle(ready)
        if job:
            api.kernel.CloseHandle(job)


def _windows_tree_metrics(process: subprocess.Popen) -> dict[str, Any] | None:
    api = _windows_api()
    with process._pae_tree_lock:
        table = _windows_processes()
        known = process._pae_known_pids
        # Expand ancestry while exited parents remain known; verify creation time
        # before accounting or killing a PID that the OS may already have reused.
        changed = True
        while changed:
            changed = False
            for pid, (parent, _) in table.items():
                if parent not in known or pid == process.pid:
                    continue
                value = _windows_pid_time(pid)
                if value and known.get(pid) == value[0]:
                    continue
                parent_value = _windows_pid_time(parent)
                if (value and value[0] >= known[parent]
                        and (parent_value is None or parent_value[0] == known[parent])):
                    known[pid] = value[0]
                    changed = True
        members = []
        active = 0
        for pid, identity in list(known.items()):
            value = _windows_pid_time(pid)
            if not value or value[0] != identity:
                continue
            key = (pid, identity)
            process._pae_cpu_totals[key] = max(value[1], process._pae_cpu_totals.get(key, 0))
            if pid in table:
                active += 1
                if len(members) < 20:
                    members.append({"pid": pid, "state": "running", "cpu_seconds": value[1]})
        job = getattr(process, "_pae_job_handle", None)
        if job:
            accounting = api.Accounting()
            if api.kernel.QueryInformationJobObject(job, 1, api.ctypes.byref(accounting), api.ctypes.sizeof(accounting), None):
                return {"cpu_seconds": (accounting.user + accounting.kernel) / 10_000_000,
                        "active_processes": int(accounting.active), "processes": members,
                        "backend": "windows-job"}
        if not members:
            return None
        return {"cpu_seconds": sum(process._pae_cpu_totals.values()), "active_processes": active,
                "processes": members, "backend": "windows-pid-fallback"}


def metrics(process: subprocess.Popen) -> dict[str, Any] | None:
    """Cumulative tree CPU (including observed exited children), or unavailable."""
    if os.name == "nt":
        if not hasattr(process, "_pae_tree_lock"):
            process._pae_tree_lock = threading.RLock()
            identity = _windows_pid_time(process.pid)
            process._pae_known_pids = {process.pid: identity[0]} if identity else {}
            process._pae_cpu_totals = {}
        return _windows_tree_metrics(process)
    return _posix_tree_metrics(process)


def _posix_snapshot(timeout_seconds: float = 3) -> dict[int, dict[str, Any]] | None:
    deadline = time.monotonic() + timeout_seconds
    proc_root = Path("/proc")
    if proc_root.is_dir():
        try:
            ticks = max(1, int(os.sysconf("SC_CLK_TCK")))
            entries = list(proc_root.iterdir())
        except (OSError, ValueError):
            return None
        result = {}
        for entry in entries:
            if time.monotonic() >= deadline:
                break
            if not entry.name.isdigit():
                continue
            try:
                record = (entry / "stat").read_text(encoding="utf-8")
                close_at = record.rfind(")")
                fields = record[close_at + 2:].split()
                if close_at < 0 or len(fields) < 20:
                    continue
                result[int(entry.name)] = {
                    "parent": int(fields[1]), "group": int(fields[2]), "session": int(fields[3]),
                    "identity": fields[19], "state": fields[0],
                    "cpu": (int(fields[11]) + int(fields[12])) / ticks,
                    # Reaped-child time also detects CPU from short children
                    # that finish between samples without double-counting them
                    # in the retained own-CPU ledger below.
                    "reaped_cpu": (int(fields[13]) + int(fields[14])) / ticks,
                }
            except (OSError, ValueError):
                continue
        return result
    try:
        result = subprocess.run(["ps", "-e", "-o", "pid=", "-o", "ppid=", "-o", "pgid=", "-o", "sid=",
                                 "-o", "time=", "-o", "stat=", "-o", "lstart="],
                                capture_output=True, text=True, encoding="utf-8", errors="replace",
                                timeout=max(0.001, deadline - time.monotonic()), check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode:
        return None
    table = {}
    for line in result.stdout.splitlines():
        fields = line.split()
        if len(fields) < 11:
            continue
        try:
            table[int(fields[0])] = {"parent": int(fields[1]), "group": int(fields[2]), "session": int(fields[3]),
                                    "cpu": float(_parse_cpu_time(fields[4])), "reaped_cpu": 0.0,
                                    "state": fields[5], "identity": " ".join(fields[6:11])}
        except ValueError:
            continue
    return table


def _posix_tree_metrics(process: subprocess.Popen) -> dict[str, Any] | None:
    if not hasattr(process, "_pae_posix_lock"):
        process._pae_posix_lock = threading.RLock()
        process._pae_posix_known = {}
        process._pae_posix_cpu = {}
        process._pae_posix_exited_cpu = 0.0
        process._pae_posix_total = 0.0
        process._pae_posix_live = {}
    with process._pae_posix_lock:
        table = _posix_snapshot()
        if table is None:
            return None
        known = process._pae_posix_known
        owned_session = getattr(process, "_pae_owned_session", False)
        for pid, value in table.items():
            if pid == process.pid or value["group"] == process.pid or (owned_session and value["session"] == process.pid):
                known[pid] = value["identity"]
        changed = True
        while changed:
            changed = False
            for pid, value in table.items():
                parent = value["parent"]
                parent_value = table.get(parent)
                if pid not in known and parent in known and (parent_value is None or parent_value["identity"] == known[parent]):
                    known[pid] = value["identity"]
                    changed = True
        members = []
        live_identities = {}
        live_reaped = 0.0
        for key, cpu in list(process._pae_posix_cpu.items()):
            pid, identity = key
            if table.get(pid, {}).get("identity") != identity:
                process._pae_posix_exited_cpu += cpu
                del process._pae_posix_cpu[key]
        for pid, identity in list(known.items()):
            value = table.get(pid)
            if value is None or value["identity"] != identity:
                continue
            key = (pid, identity)
            process._pae_posix_cpu[key] = max(value["cpu"], process._pae_posix_cpu.get(key, 0))
            live_reaped += value.get("reaped_cpu", 0.0)
            if not value["state"].startswith("Z"):
                live_identities[pid] = identity
                if len(members) < 20:
                    members.append({"pid": pid, "state": value["state"], "cpu_seconds": value["cpu"]})
        process._pae_posix_live = live_identities
        # The lower bound from living processes + their reaped-child counters
        # catches very short children; the ledger retains observed exited CPU.
        living_cpu = sum(value["cpu"] for pid, value in table.items() if known.get(pid) == value["identity"])
        total = max(process._pae_posix_exited_cpu + sum(process._pae_posix_cpu.values()),
                    living_cpu + live_reaped, process._pae_posix_total)
        process._pae_posix_total = total
        return {"cpu_seconds": total, "active_processes": len(live_identities), "processes": members,
                "backend": "posix-tree"} if known else None


def _posix_pid_identities(pids: list[int], timeout_seconds: float) -> dict[int, str]:
    """Verify cached PIDs without waiting for a full system process enumeration."""
    deadline = time.monotonic() + timeout_seconds
    identities = {}
    proc_root = Path("/proc")
    if proc_root.is_dir():
        for pid in pids:
            if time.monotonic() >= deadline:
                break
            try:
                record = (proc_root / str(pid) / "stat").read_text(encoding="utf-8")
                close_at = record.rfind(")")
                fields = record[close_at + 2:].split()
                if close_at >= 0 and len(fields) >= 20:
                    identities[pid] = fields[19]
            except OSError:
                pass
        return identities
    if not pids:
        return identities
    try:
        result = subprocess.run(["ps", "-p", ",".join(map(str, pids)), "-o", "pid=", "-o", "lstart="],
                                capture_output=True, text=True, encoding="utf-8", errors="replace",
                                timeout=max(0.001, deadline - time.monotonic()), check=False)
    except (OSError, subprocess.TimeoutExpired):
        return identities
    if result.returncode == 0:
        for line in result.stdout.splitlines():
            fields = line.split()
            if len(fields) >= 6:
                try:
                    identities[int(fields[0])] = " ".join(fields[1:6])
                except ValueError:
                    pass
    return identities


def _terminate_posix(process: subprocess.Popen) -> None:
    deadline = time.monotonic() + 0.5
    # The primary group is owned by launch, so kill it before any query that
    # could block. Changed-group descendants use verified cached identities.
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    if process.poll() is None:
        process.kill()
    live = dict(getattr(process, "_pae_posix_live", {}))
    actual = _posix_pid_identities(list(live), min(0.15, max(0.001, deadline - time.monotonic())))
    for pid, identity in live.items():
        if time.monotonic() >= deadline:
            break
        if pid == os.getpid() or actual.get(pid) != identity:
            continue
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    remaining = deadline - time.monotonic()
    table = _posix_snapshot(timeout_seconds=min(0.2, remaining)) if remaining > 0 else None
    if table:
        known = dict(getattr(process, "_pae_posix_known", {}))
        owned_session = getattr(process, "_pae_owned_session", False)
        for pid, value in table.items():
            if time.monotonic() >= deadline:
                break
            owned = (value["group"] == process.pid or (owned_session and value["session"] == process.pid)
                     or known.get(pid) == value["identity"])
            if not owned or pid == os.getpid():
                continue
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    try:
        process.wait(timeout=max(0.001, deadline - time.monotonic()))
    except subprocess.TimeoutExpired:
        pass


def terminate(process: subprocess.Popen) -> None:
    """Stop owned descendants without an unbounded grace/reap wait."""
    if os.name == "nt":
        api = _windows_api()
        job = getattr(process, "_pae_job_handle", None)
        if job and api.kernel.TerminateJobObject(job, 124):
            try:
                process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                pass
            return
        metrics(process)
        known = dict(getattr(process, "_pae_known_pids", {}))
        for pid, identity in reversed(list(known.items())):
            handle = api.kernel.OpenProcess(0x1000 | 1, False, pid)
            if not handle:
                continue
            try:
                value = _windows_pid_time(pid)
                if value and value[0] == identity:
                    api.kernel.TerminateProcess(handle, 124)
            finally:
                api.kernel.CloseHandle(handle)
        if process.poll() is None:
            try:
                subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2, check=False)
            except (OSError, subprocess.TimeoutExpired):
                process.kill()
    else:
        _terminate_posix(process)
        return
    try:
        process.wait(timeout=1)
    except subprocess.TimeoutExpired:
        pass


def close(process: subprocess.Popen) -> None:
    """Release ownership after the caller drained its pipes; Job close stops leftovers."""
    if os.name == "nt":
        if (getattr(process, "_pae_tree_backend", None) == "windows-pid-fallback"
                and not getattr(process, "_pae_job_handle", None)):
            terminate(process)
        with getattr(process, "_pae_tree_lock", threading.RLock()):
            job = getattr(process, "_pae_job_handle", None)
            if job:
                _windows_api().kernel.CloseHandle(job)
                process._pae_job_handle = None
            ready = getattr(process, "_pae_ready_handle", None)
            if ready:
                _windows_api().kernel.CloseHandle(ready)
                process._pae_ready_handle = None
    else:
        if getattr(process, "_pae_owned_group", False):
            _terminate_posix(process)
        with _CPU_LOCK:
            _GROUP_CPU_CENTISECONDS.pop(process.pid, None)


def _windows_guard(name: str) -> int:
    api = _windows_api()
    ready = api.kernel.OpenEventW(0x100000, False, name)
    if not ready:
        return 125
    try:
        if api.kernel.WaitForSingleObject(ready, 30000) != 0:
            return 125
    finally:
        api.kernel.CloseHandle(ready)
    env = dict(os.environ)
    spec = json.loads(env.pop("PAE_PROCESS_TREE_GUARD"))
    options = {"env": env, "shell": spec["shell"]}
    if spec.get("executable"):
        options["executable"] = spec["executable"]
    try:
        child = subprocess.Popen(spec["command"], **options)
        return child.wait()
    except OSError as exc:
        print(f"[process-tree] command could not start: {exc}", file=sys.stderr, flush=True)
        return 127


def _posix_guard() -> int:
    os.setpgid(0, 0)
    env = dict(os.environ)
    spec = json.loads(env.pop("PAE_PROCESS_TREE_GUARD"))
    command = spec["command"]
    if spec["shell"]:
        command = [spec.get("executable") or "/bin/sh", "-c", *(command if isinstance(command, list) else [command])]
    elif isinstance(command, str):
        command = [command]
    try:
        os.execvpe(spec.get("executable") or command[0], command, env)
    except OSError as exc:
        print(f"[process-tree] command could not start: {exc}", file=sys.stderr, flush=True)
        return 127


if __name__ == "__main__" and len(sys.argv) == 3 and sys.argv[1] == "_windows-guard":
    raise SystemExit(_windows_guard(sys.argv[2]))
if __name__ == "__main__" and len(sys.argv) == 2 and sys.argv[1] == "_posix-guard":
    raise SystemExit(_posix_guard())
