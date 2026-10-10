#!/usr/bin/env python3
"""Progress-aware idle budgets and independent, optional process lifetime ceilings."""

from __future__ import annotations

import hashlib
from collections import deque
import math
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Callable

import process_tree


ANSI_ESCAPE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
VOLATILE_PROGRESS = (
    re.compile(r"\b\d{4}-\d\d-\d\d[T ][0-9:.+-]+Z?\b"),
    re.compile(r"\b\d{1,2}:\d\d:\d\d(?:\.\d+)?(?:Z|[+-]\d\d:?\d\d)?\b"),
    re.compile(r"\b(?:pid|process)[=: ]+\d+\b", re.IGNORECASE),
    re.compile(r"\b\d+(?:\.\d+)?\s*(?:us|µs|ms|msec|s|seconds?|secs?)\b", re.IGNORECASE),
)
FILE_SKIP_PARTS = {".git", ".ai-work", ".agents", ".codex", "node_modules", "__pycache__", ".venv", "venv"}
PROBE_OUTPUT_BYTES = 65536
OUTPUT_FINGERPRINTS = 65536
FILE_FINGERPRINTS = 4096


def progress_line(value: str) -> str:
    """Normalize telemetry and ignore monitor output rather than counting its cadence."""
    result = ANSI_ESCAPE.sub("", value).strip()
    if result.startswith(("[resource-watch]", "[process-tree]")):
        return ""
    for pattern in VOLATILE_PROGRESS:
        result = pattern.sub("", result)
    return " ".join(result.split())


def safe_glob(value: Any) -> bool:
    if not isinstance(value, str) or not value or len(value) > 1024 or "\0" in value:
        return False
    normalized = value.replace("\\", "/")
    return not (PureWindowsPath(value).drive or PureWindowsPath(value).is_absolute()
                or PurePosixPath(normalized).is_absolute() or ".." in PurePosixPath(normalized).parts)


def validate_policy(data: dict[str, Any], *, idle_key: str = "no_progress_timeout_seconds") -> list[str]:
    errors = []
    for key, default, maximum in ((idle_key, 300, 7200), ("expected_quiet_seconds", 0, 7200),
                                  ("validation_hard_timeout_seconds", 0, 604800)):
        value = data.get(key, default)
        if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= maximum:
            errors.append(f"{key} must be 0..{maximum}")
    pattern = data.get("progress_regex")
    if "progress_regex" in data:
        if not isinstance(pattern, str) or not pattern or len(pattern) > 2048:
            errors.append("progress_regex must be a nonempty string of at most 2048 characters")
        else:
            try:
                re.compile(pattern)
            except re.error as exc:
                errors.append(f"invalid progress_regex: {exc}")
    probe = data.get("progress_probe")
    if "progress_probe" in data:
        if not isinstance(probe, dict):
            errors.append("progress_probe must be an object")
        else:
            unknown = set(probe) - {"command", "every_seconds", "timeout_seconds", "mode"}
            if unknown:
                errors.append("progress_probe has unsupported fields: " + ", ".join(sorted(unknown)))
            command = probe.get("command")
            if (not isinstance(command, list) or not command or len(command) > 128
                    or any(not isinstance(arg, str) or not arg or "\0" in arg for arg in command)):
                errors.append("progress_probe.command must be a nonempty argv array")
            elif sum(map(len, command)) > 16384:
                errors.append("progress_probe.command exceeds the 16384-character argv limit")
            elif any(re.search(r"^--?(?:password|passwd|token|secret|api[-_]key)(?:=|$)|[a-z][a-z0-9+.-]*://[^/\s:@]+:[^/\s@]+@", arg, re.IGNORECASE)
                     for arg in command):
                errors.append("progress_probe.command must keep credentials out of argv")
            for key, default, maximum in (("every_seconds", 20, 300), ("timeout_seconds", 5, 60)):
                value = probe.get(key, default)
                if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= maximum:
                    errors.append(f"progress_probe.{key} must be 1..{maximum}")
            if probe.get("mode", "changes") not in ("changes", "increases"):
                errors.append("progress_probe.mode must be changes or increases")
    files = data.get("progress_files")
    if "progress_files" in data and (not isinstance(files, list) or len(files) > 64 or any(not safe_glob(item) for item in files)):
        errors.append("progress_files must be at most 64 safe repository-relative globs")
    return errors


class ProgressState:
    def __init__(self, idle_seconds: float, hard_seconds: float = 0, expected_quiet_seconds: float = 0,
                 progress_regex: str | None = None, clock: Callable[[], float] = time.monotonic):
        for name, value in (("idle_seconds", idle_seconds), ("hard_seconds", hard_seconds),
                            ("expected_quiet_seconds", expected_quiet_seconds)):
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and nonnegative")
        self.clock = clock
        self.started_at = self.last_progress_at = clock()
        self.idle_seconds, self.hard_seconds = float(idle_seconds), float(hard_seconds)
        self.expected_quiet_seconds = float(expected_quiet_seconds)
        self.pattern = re.compile(progress_regex) if progress_regex else None
        self._lock = threading.RLock()
        self._seen: set[bytes] = set()
        self._seen_order: deque[bytes] = deque()
        self._reason: str | None = None
        self.last_progress_source = "start"
        self.progress_events = 0
        self.cpu_monitoring: bool | None = None
        self.cpu_backend = "pending"

    def progress(self, source: str) -> None:
        with self._lock:
            if self._reason is None:
                self.last_progress_at = self.clock()
                self.last_progress_source = source
                self.progress_events += 1

    def observe_output(self, line: str | bytes) -> None:
        if isinstance(line, bytes):
            line = line.decode("utf-8", "replace")
        with self._lock:
            # Readers may pass lines or blocks, including output without a final
            # newline. Distinct normalized text is retained for the whole run.
            for item in line.splitlines():
                raw = ANSI_ESCAPE.sub("", item)
                if raw.strip().startswith(("[resource-watch]", "[process-tree]")):
                    continue
                if self.pattern is not None and self.pattern.search(raw[:4096]):
                    self.progress("regex")
                normalized = progress_line(item)
                if not normalized:
                    continue
                key = hashlib.sha256(normalized.encode("utf-8", "replace")).digest()[:16]
                if key not in self._seen:
                    if len(self._seen_order) >= OUTPUT_FINGERPRINTS:
                        self._seen.discard(self._seen_order.popleft())
                    self._seen.add(key)
                    self._seen_order.append(key)
                    self.progress("output")

    def reason(self) -> str | None:
        with self._lock:
            now = self.clock()
            if self._reason is None:
                if self.hard_seconds and now - self.started_at >= self.hard_seconds:
                    self._reason = "hard"
                elif self.idle_seconds and now - self.last_progress_at >= max(self.idle_seconds, self.expected_quiet_seconds):
                    self._reason = "idle"
            return self._reason

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            now = self.clock()
            return {"elapsed_seconds": round(max(0, now - self.started_at), 3),
                    "idle_seconds": round(max(0, now - self.last_progress_at), 3),
                    "idle_timeout_seconds": self.idle_seconds, "hard_timeout_seconds": self.hard_seconds,
                    "expected_quiet_seconds": self.expected_quiet_seconds,
                    "last_progress_source": self.last_progress_source, "progress_events": self.progress_events,
                    "timeout_reason": self._reason, "cpu_monitoring": self.cpu_monitoring,
                    "cpu_backend": self.cpu_backend}


class ProgressMonitor:
    """A watchdog independent of CPU, file, probe and caller health-check latency."""
    def __init__(self, process: subprocess.Popen, state: ProgressState, cwd: Path,
                 progress_probe: dict[str, Any] | None = None, progress_files: list[str] | None = None):
        self.process, self.state, self.cwd = process, state, Path(cwd).resolve()
        self.progress_probe, self.progress_files = progress_probe, progress_files or []
        policy = {"progress_files": self.progress_files}
        if progress_probe is not None:
            policy["progress_probe"] = progress_probe
        errors = validate_policy(policy)
        if errors:
            raise ValueError("; ".join(errors))
        self.reason: str | None = None
        self.metrics: dict[str, Any] | None = None
        self._stop = threading.Event()
        self._threads: list[threading.Thread] = []
        self._tick_lock = threading.Lock()
        self._probe_process: subprocess.Popen | None = None
        self._cpu: float | None = None
        self._files: dict[str, tuple[int, int]] | None = None
        self._probe_value: str | float | None = None
        self._probe_baseline = False
        self._sample_seconds = min(1.0, max(0.05, state.idle_seconds / 4)) if state.idle_seconds else 1.0
        self._diagnostics: set[str] = set()

    def start(self) -> ProgressMonitor:
        if self._threads:
            return self
        for target in (self._watch, self._collect, self._probe):
            thread = threading.Thread(target=target, daemon=True)
            self._threads.append(thread)
            thread.start()
        return self

    def tick(self) -> str | None:
        with self._tick_lock:
            if self.reason is None:
                self.reason = self.state.reason()
                if self.reason:
                    # The deadline is latched before cleanup, so late output or
                    # a slow probe cannot change the reported timeout reason.
                    process_tree.terminate(self.process)
                    probe = self._probe_process
                    if probe is not None:
                        process_tree.terminate(probe)
            return self.reason

    def _watch(self) -> None:
        while not self._stop.wait(0.05):
            if self.tick():
                return

    def _collect(self) -> None:
        while not self._stop.is_set():
            try:
                value = process_tree.metrics(self.process)
                self.metrics = value
                self.state.cpu_monitoring = value is not None
                self.state.cpu_backend = str(value.get("backend", "posix-group")) if value else "unavailable"
                backend = self.state.cpu_backend
                if backend in {"unavailable", "windows-pid-fallback"} and backend not in self._diagnostics:
                    self._diagnostics.add(backend)
                    print(f"[process-tree] progress_cpu={backend} fallback=output,probe,files", file=sys.stderr, flush=True)
                if value is not None:
                    cpu = float(value["cpu_seconds"])
                    if self._cpu is not None and cpu > self._cpu + 0.001:
                        self.state.progress("cpu")
                    self._cpu = max(cpu, self._cpu or 0)
                self._observe_files()
            except (OSError, ValueError, KeyError, subprocess.SubprocessError):
                pass
            self._stop.wait(self._sample_seconds)

    def _file_snapshot(self) -> dict[str, tuple[int, int]]:
        result = {}
        for pattern in self.progress_files:
            normalized = pattern.replace("\\", "/")
            if normalized in {"**/*", "**"}:
                paths = self._walk_files()
            else:
                paths = self.cwd.glob(normalized)
            for path in paths:
                if self._stop.is_set():
                    return result
                try:
                    relative = path.relative_to(self.cwd)
                    if any(part.lower() in FILE_SKIP_PARTS for part in relative.parts):
                        continue
                    resolved = path.resolve()
                    resolved.relative_to(self.cwd)
                    current = self.cwd
                    if any((current := current / part).is_symlink() for part in relative.parts):
                        continue
                    if not path.is_file():
                        continue
                    metadata = path.stat()
                    result[relative.as_posix()] = metadata.st_size, metadata.st_mtime_ns
                    if len(result) >= FILE_FINGERPRINTS:
                        return result
                except (OSError, ValueError):
                    continue
        return result

    def _walk_files(self):
        for base, directories, files in os.walk(self.cwd, followlinks=False):
            directories[:] = [name for name in directories
                              if name.lower() not in FILE_SKIP_PARTS and not (Path(base) / name).is_symlink()]
            for name in files:
                yield Path(base) / name

    def _observe_files(self) -> None:
        if not self.progress_files:
            return
        current = self._file_snapshot()
        if self._files is not None:
            for path, (size, modified) in current.items():
                previous = self._files.get(path)
                if previous is None or size > previous[0] or (size >= previous[0] and modified > previous[1]):
                    self.state.progress("files")
                    break
        # Deletion and truncation do not renew the clock, but the next sample
        # must compare against their new baseline so a recreated or regrowing
        # artifact still provides evidence even below its former high-water mark.
        self._files = current

    def _run_probe(self) -> str | None:
        assert self.progress_probe is not None
        started = time.monotonic()
        process = None
        with tempfile.TemporaryFile() as output:
            try:
                process = process_tree.launch(self.progress_probe["command"], cwd=self.cwd,
                                              stdin=subprocess.DEVNULL, stdout=output, stderr=subprocess.DEVNULL,
                                              start_new_session=False)
                self._probe_process = process
                while process.poll() is None:
                    if self._stop.is_set() or self.reason or time.monotonic() - started >= self.progress_probe.get("timeout_seconds", 5):
                        process_tree.terminate(process)
                        return None
                    if os.fstat(output.fileno()).st_size > PROBE_OUTPUT_BYTES:
                        process_tree.terminate(process)
                        return None
                    self._stop.wait(0.05)
                if process.returncode != 0 or os.fstat(output.fileno()).st_size > PROBE_OUTPUT_BYTES:
                    return None
                output.seek(0)
                return output.read(PROBE_OUTPUT_BYTES).decode("utf-8", "replace")
            except (OSError, ValueError, subprocess.SubprocessError):
                return None
            finally:
                self._probe_process = None
                if process is not None:
                    process_tree.close(process)

    def _observe_probe(self, output: str | None) -> None:
        if output is None:
            return
        mode = (self.progress_probe or {}).get("mode", "changes")
        if mode == "increases":
            try:
                value: str | float = float(output.strip())
                if not math.isfinite(value):
                    return
            except ValueError:
                return
        else:
            normalized = "\n".join(filter(None, (progress_line(line) for line in output.splitlines())))
            if not normalized:
                return
            value = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        if self._probe_baseline and (value > self._probe_value if mode == "increases" else value != self._probe_value):
            self.state.progress("probe")
        self._probe_baseline = True
        self._probe_value = max(value, self._probe_value) if mode == "increases" and self._probe_value is not None else value

    def _probe(self) -> None:
        if not self.progress_probe:
            return
        due = time.monotonic()
        while not self._stop.is_set() and not self.reason:
            self._observe_probe(self._run_probe())
            due += self.progress_probe.get("every_seconds", 20)
            self._stop.wait(max(0, due - time.monotonic()))
            due = max(due, time.monotonic())

    def close(self) -> None:
        self._stop.set()
        probe = self._probe_process
        if probe is not None:
            process_tree.terminate(probe)
        for thread in self._threads:
            if thread is not threading.current_thread():
                thread.join(timeout=0.2)


def supervise(process: subprocess.Popen, state: ProgressState, cwd: Path,
              progress_probe: dict[str, Any] | None = None, progress_files: list[str] | None = None,
              on_tick: Callable[[ProgressMonitor], Any] | None = None) -> str | None:
    monitor = ProgressMonitor(process, state, cwd, progress_probe, progress_files).start()
    try:
        while process.poll() is None and not monitor.reason:
            if on_tick is not None:
                on_tick(monitor)
            time.sleep(0.05)
        return monitor.reason
    finally:
        monitor.close()
