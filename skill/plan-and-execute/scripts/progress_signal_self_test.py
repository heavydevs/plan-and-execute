#!/usr/bin/env python3
"""Signal round trips, stable errors, bounded probes and advisory progress gaps."""

from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import progress_signal as signal
import progress_watch
import service_map


ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUTF8": "1"}
HERE = Path(__file__).resolve().parent


def rejects(call):
    try:
        call()
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def check_round_trip():
    examples = [
        ("PROGRESS", {"stage": "test", "done": 2, "total": 4, "attempt": 1}),
        ("PROGRESS", {"stage": "build", "done": 0, "seq": 8, "unit": "batch"}),
        ("ERROR", {"class": "semantic", "fp": "0123abcd", "stage": "test"}),
        ("HEARTBEAT", {}),
    ]
    for kind, fields in examples:
        output = io.StringIO()
        line = signal.emit_signal(kind, fields, stream=output)
        assert output.getvalue() == line + "\n"
        assert signal.parse_signal(line) == {"kind": kind, **fields}
        assert signal.format_signal(kind, fields) == line
    assert signal.parse_signal("ordinary log") is None
    for key in ("Bad", "bad-key", "key1", "", "kind"):
        rejects(lambda: signal.format_signal("HEARTBEAT", {key: "x"}))
        rejects(lambda: signal.parse_signal(f"HEARTBEAT {key}=x"))
    for line in ("PROGRESS stage=test done=-1", "PROGRESS stage=test done=1.5",
                 "PROGRESS done=1", "ERROR class=semantic stage=test fp=wrong",
                 "HEARTBEAT x=1 x=2", "HEARTBEAT payload=a=b", "HEARTBEAT broken",
                 "PROGRESS stage=bad-stage done=1", "PROGRESS stage=test done=1\nHEARTBEAT"):
        rejects(lambda: signal.parse_signal(line))
    for value in (True, -1, 1.5, "2"):
        rejects(lambda: signal.format_signal("PROGRESS", stage="test", done=value))
    rejects(lambda: signal.format_signal("OTHER"))


def check_fingerprint():
    pairs = [
        ('failed 12 at C:\\logs\\a.txt id=alpha hex=0xabc "payload-a"',
         'failed 99 at D:\\temp\\b.txt id=beta hex=0xdef "payload-b"'),
        ("failed /tmp/a.log request_id=synthetic-a 'one' 1.25",
         "FAILED /other/b.log request_id=synthetic-b 'two' 2.75"),
        ("uuid=12345678-1234-1234-1234-123456789abc address=deadbeef",
         "uuid=87654321-4321-4321-4321-abcdef123456 address=abcdefab"),
        ("cannot read logs/a.txt or logs\\a.txt", "cannot read tmp/b.txt or temp\\b.txt"),
    ]
    for left, right in pairs:
        fp = signal.fingerprint_error(left)
        assert fp == signal.fingerprint_error(right), (left, right)
        assert len(fp) == 8 and all(char in "0123456789abcdef" for char in fp)
    assert signal.fingerprint_error("connection refused") != signal.fingerprint_error("invalid schema")


def append(path: Path, kind: str, **fields):
    with path.open("a", encoding="utf-8") as output:
        signal.emit_signal(kind, fields, stream=output)


def probe_cli(path: Path):
    return subprocess.run([sys.executable, str(HERE / "progress_signal.py"), "probe", "--file", str(path)],
                          capture_output=True, text=True, encoding="utf-8", env=ENV, timeout=5)


def check_probe(root: Path):
    path = root / "probe.log"
    path.write_text("x" * (signal.TAIL_BYTES + 50) + "\n", encoding="utf-8")
    append(path, "PROGRESS", stage="test", done=7)
    append(path, "HEARTBEAT")
    append(path, "ERROR", **{"class": "semantic", "fp": "0123abcd", "stage": "test"})
    with path.open("a", encoding="utf-8") as output:
        output.write("PROGRESS stage=test done=invalid\nPROGRESS stage=test done=99")
    before = path.read_bytes()
    result = probe_cli(path)
    assert result.returncode == 0 and result.stdout == "7\n" and result.stderr == ""
    assert path.read_bytes() == before, "probe must be read-only"
    path.write_text("PROGRESS stage=test done=2 seq=11\nHEARTBEAT\n", encoding="utf-8")
    assert signal.probe_file(path) == 11
    assert signal.probe_file(path, tail_bytes=10) == 0
    path.write_text("HEARTBEAT\n", encoding="utf-8")
    assert probe_cli(path).stdout == "0\n"
    result = probe_cli(root / "missing.log")
    assert result.returncode == 2 and result.stdout == ""
    rejects(lambda: signal.probe_file(path, tail_bytes=signal.TAIL_BYTES + 1))


def check_progress(root: Path):
    # Exercise actual progress_watch probe execution and its increasing baseline
    # with a deterministic clock; no background process/CPU can mask stagnation.
    clock = SimpleNamespace(now=0.0)
    state = progress_watch.ProgressState(5, clock=lambda: clock.now)
    path = root / "progress.log"
    append(path, "PROGRESS", stage="test", done=0)
    monitor = progress_watch.ProgressMonitor(Mock(), state, root, {
        "command": [sys.executable, str(HERE / "progress_signal.py"), "probe", "--file", str(path)],
        "mode": "increases", "timeout_seconds": 5,
    })

    def sample():
        output = monitor._run_probe()
        assert output is not None
        monitor._observe_probe(output)

    sample()
    assert state.progress_events == 0
    for now, done in ((4, 1), (8, 2), (12, 3)):
        clock.now = now
        append(path, "PROGRESS", stage="test", done=done)
        sample()
        assert state.reason() is None and state.last_progress_at == now
    assert state.progress_events == 3 and state.last_progress_source == "probe"
    for now in (13, 14, 16):
        clock.now = now
        append(path, "HEARTBEAT")
        append(path, "PROGRESS", stage="test", done=3)
        sample()
        assert state.last_progress_at == 12 and state.progress_events == 3
    clock.now = 17
    assert state.reason() == "idle"
    # Existing normalized stdout behavior also remains intact for repeats.
    clock.now = 0
    output_state = progress_watch.ProgressState(5, clock=lambda: clock.now)
    output_state.observe_output("HEARTBEAT\n")
    clock.now = 4
    output_state.observe_output("HEARTBEAT\n")
    assert output_state.last_progress_at == 0
    output_state.observe_output(signal.format_signal("PROGRESS", stage="test", done=1))
    clock.now = 8
    output_state.observe_output(signal.format_signal("PROGRESS", stage="test", done=2))
    assert output_state.reason() is None and output_state.last_progress_at == 8
    clock.now = 12
    output_state.observe_output(signal.format_signal("PROGRESS", stage="test", done=2))
    assert output_state.last_progress_at == 8
    clock.now = 13
    assert output_state.reason() == "idle"


def check_gap(root: Path):
    fixture = root / "audit"
    fixture.mkdir()
    validation = {"id": "LONG", "command": [sys.executable, "-c", "pass"], "resources": []}
    data = {"schema_version": 1, "inventory_reviewed": True, "validations": [validation], "resources": []}
    for duration in (0, 300, 301, 604800):
        validation["expected_duration_seconds"] = duration
        assert not service_map.validate_data(data)
        assert bool(service_map.progress_gap_reason(validation)) == (duration > 300)
    for duration in (True, -1, 604801, 1.5, "600", None):
        validation["expected_duration_seconds"] = duration
        assert any("expected_duration_seconds" in error for error in service_map.validate_data(data))
    validation["expected_duration_seconds"] = 600
    map_path = fixture / "SERVICE_MAP.md"
    manifest_path = fixture / "manifest.json"
    # All map/manifest inputs here are synthetic fixtures, never another task.
    watcher = HERE / "resource_watch.py"
    command = f'"{sys.executable}" "{watcher}" run --repo-root . --map SERVICE_MAP.md --validation LONG'
    manifest_path.write_text(json.dumps({"tasks": [{"id": "synthetic", "validation_commands": [command, command],
                                                     "validation_jobs": ["LONG"]}]}), encoding="utf-8")

    def audit():
        signatures, incomplete = service_map.scan_inputs(fixture)
        assert not incomplete
        data["snapshot"] = {"algorithm": service_map.ALGORITHM, "digest": service_map.aggregate(signatures),
                            "source_count": len(signatures)}
        map_path.write_text(service_map.replace_map_data(service_map.MAP_BEGIN + "\n```json\n{}\n```\n" + service_map.MAP_END, data),
                            encoding="utf-8")
        return subprocess.run([sys.executable, str(HERE / "service_map.py"), "audit-plan", "--repo-root", str(fixture),
                               "--map", "SERVICE_MAP.md", "--plan", "manifest.json"],
                              capture_output=True, text=True, encoding="utf-8", env=ENV, timeout=10)

    result = audit()
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.count("progress-gap task=synthetic validation=LONG reason=") == 1
    assert "service-map-audit=passed" in result.stdout
    # Detached validations have the same advisory, independently of commands.
    manifest_path.write_text(json.dumps({"tasks": [{"id": "synthetic", "validation_jobs": ["LONG"]}]}), encoding="utf-8")
    assert audit().stdout.count("progress-gap task=synthetic validation=LONG reason=") == 1
    for key, value in (("progress_regex", "^PROGRESS"),
                       ("progress_probe", {"command": [sys.executable, "-c", "print(1)"], "mode": "increases"}),
                       ("progress_files", ["output/*.log"])):
        validation[key] = value
        result = audit()
        assert result.returncode == 0 and "progress-gap" not in result.stdout
        del validation[key]
    validation["progress_files"] = []
    assert "progress-gap" in audit().stdout, "an empty file list declares no progress evidence"
    del validation["progress_files"]
    for duration in (0, 300):
        validation["expected_duration_seconds"] = duration
        result = audit()
        assert result.returncode == 0 and "progress-gap" not in result.stdout
    del validation["expected_duration_seconds"]
    result = audit()
    assert result.returncode == 0 and "progress-gap" not in result.stdout


def main():
    check_round_trip()
    check_fingerprint()
    with tempfile.TemporaryDirectory(prefix="pae-progress-signal-") as directory:
        root = Path(directory)
        check_probe(root)
        check_progress(root)
        check_gap(root)
    print("progress_signal_self_test: ok (5 check groups)")


if __name__ == "__main__":
    main()
