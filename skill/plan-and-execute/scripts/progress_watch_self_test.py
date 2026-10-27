#!/usr/bin/env python3
"""Idle progress, bounded probes, independent ceilings and real owned-tree cleanup."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import process_tree

# Tight-timing child fixtures use -S: all child imports are stdlib. Site hooks
# can exceed the idle window before a fixture starts; production argv is unchanged.
import progress_watch
import service_map


class Clock:
    now = 0.0

    def __call__(self):
        return self.now


def check_state():
    clock = Clock()
    state = progress_watch.ProgressState(5, clock=clock)
    state.observe_output("heartbeat 2026-10-10T10:10:10Z pid=12 duration=2ms\n")
    clock.now = 4
    state.observe_output("heartbeat 2026-10-10T10:10:14Z pid=99 duration=4ms\n")
    assert state.snapshot()["idle_seconds"] == 4
    state.observe_output("[resource-watch] resource=db state=healthy\n")
    assert state.snapshot()["progress_events"] == 1
    clock.now = 5
    assert state.reason() == "idle"
    state.progress("late output")
    assert state.reason() == "idle", "expiration must remain latched"

    clock.now = 0
    marker = progress_watch.ProgressState(5, progress_regex=r"^checkpoint", clock=clock)
    marker.observe_output("checkpoint\n")
    clock.now = 4
    marker.observe_output("checkpoint\n")
    clock.now = 6
    assert marker.reason() is None
    assert marker.snapshot()["last_progress_source"] == "regex"
    timestamp = progress_watch.ProgressState(5, progress_regex=r"^\d{4}-", clock=clock)
    timestamp.observe_output("2026-10-10T10:10:10Z\n")
    assert timestamp.last_progress_source == "regex"
    before = timestamp.progress_events
    timestamp.observe_output("[process-tree] 2026-10-10T10:10:10Z\n")
    assert timestamp.progress_events == before
    fragmented = progress_watch.ProgressState(5, clock=clock)
    fragmented.observe_output("waiting")
    before = fragmented.progress_events
    for _ in range(10):
        fragmented.observe_output("waiting")
    assert fragmented.progress_events == before
    fragmented.observe_output("x" * 600 + "first")
    fragmented.observe_output("x" * 600 + "second")
    assert fragmented.progress_events == before + 2
    normalized = progress_watch.ProgressState(5, clock=clock)
    normalized.observe_output("waiting 10:10:10 elapsed=1.2s\n")
    normalized.observe_output("waiting 10:10:14 elapsed=9.9s\n")
    assert normalized.progress_events == 1
    quiet = progress_watch.ProgressState(2, expected_quiet_seconds=8, clock=clock)
    clock.now = 12
    assert quiet.reason() is None
    clock.now = 14
    assert quiet.reason() == "idle"

    clock.now = 0
    hard = progress_watch.ProgressState(1, hard_seconds=3, clock=clock)
    clock.now = 2.9
    hard.progress("work")
    clock.now = 3
    assert hard.reason() == "hard"
    disabled = progress_watch.ProgressState(0, clock=clock)
    clock.now = 100000
    assert disabled.reason() is None
    with patch.object(progress_watch, "OUTPUT_FINGERPRINTS", 2):
        saturated = progress_watch.ProgressState(5, clock=clock)
        saturated.observe_output("one\ntwo\n")
        before = saturated.snapshot()["progress_events"]
        saturated.observe_output("three\n")
        assert saturated.snapshot()["progress_events"] == before + 1
        saturated.observe_output("three\n")
        assert saturated.snapshot()["progress_events"] == before + 1
        assert len(saturated._seen) == 2


def check_policy():
    valid = {"no_progress_timeout_seconds": 0, "validation_hard_timeout_seconds": 3600,
             "expected_quiet_seconds": 500, "progress_regex": r"step \d+",
             "progress_probe": {"command": ["python", "probe.py"], "mode": "increases"},
             "progress_files": ["reports/**/*.xml"]}
    assert not progress_watch.validate_policy(valid)
    for key, value in (("no_progress_timeout_seconds", True), ("expected_quiet_seconds", -1),
                       ("validation_hard_timeout_seconds", 604801), ("progress_regex", "["),
                       ("progress_files", ["../outside"]), ("progress_files", ["C:outside"]),
                       ("progress_files", ["/outside"]), ("progress_probe", {"command": "echo 1"}),
                       ("progress_probe", {"command": ["probe"], "every_seconds": False}),
                       ("progress_probe", {"command": ["probe"], "timeout_seconds": 0}),
                       ("progress_probe", {"command": ["probe"], "mode": "heartbeat"}),
                       ("progress_probe", {"command": ["probe"], "mode": []}),
                       ("progress_probe", {"command": ["probe"], "mode": {}}),
                       ("progress_regex", None), ("progress_probe", None), ("progress_files", None)):
        assert progress_watch.validate_policy({**valid, key: value}), (key, value)
    for command in (["probe", "--token=SECRET_VALUE"], ["probe", "--password", "SECRET_VALUE"],
                    ["probe", "https://user:SECRET_VALUE@example.com"], ["x" * 16385]):
        errors = progress_watch.validate_policy({"progress_probe": {"command": command}})
        assert errors and "SECRET_VALUE" not in " ".join(errors)
    data = {"inventory_reviewed": True, "resources": [], "validations": [{"id": "v", "command": ["test"],
            "resources": [], "progress_regex": "["}]}
    assert any("progress_regex" in error for error in service_map.validate_data(data))
    fingerprint = service_map.validation_fingerprint(data, "v")
    data["validations"][0]["command"] = ["different-test"]
    assert service_map.validation_fingerprint(data, "v") != fingerprint
    reordered = dict(reversed(list(data.items())))
    assert service_map.validation_fingerprint(reordered, "v") == service_map.validation_fingerprint(data, "v")


def check_observers(root: Path):
    clock = Clock()
    state = progress_watch.ProgressState(5, clock=clock)
    monitor = progress_watch.ProgressMonitor(Mock(), state, root,
                 {"command": ["probe"], "mode": "increases"}, ["**/*"])
    monitor._observe_probe("10")
    assert state.progress_events == 0
    monitor._observe_probe(None)
    monitor._observe_probe("nan")
    monitor._observe_probe("9")
    monitor._observe_probe("10")
    assert state.progress_events == 0
    monitor._observe_probe("11")
    assert state.last_progress_source == "probe"
    changes = progress_watch.ProgressMonitor(Mock(), state, root, {"command": ["probe"]})
    changes._observe_probe("ready pid=1")
    before = state.progress_events
    changes._observe_probe("ready pid=2")
    assert state.progress_events == before
    changes._observe_probe("step two")
    assert state.progress_events == before + 1
    before = state.progress_events
    changes._observe_probe(None)
    changes._observe_probe("")
    changes._observe_probe("2026-10-10T10:10:10Z")
    changes._observe_probe("step two")
    assert state.progress_events == before, "failed or empty samples must not change the baseline"

    output = root / "report.txt"
    output.write_text("base", encoding="utf-8")
    monitor._observe_files()
    before = state.progress_events
    ignored = root / ".ai-work" / "heartbeat.log"
    ignored.parent.mkdir()
    ignored.write_text("noise", encoding="utf-8")
    monitor._observe_files()
    assert state.progress_events == before
    output.write_text("growth", encoding="utf-8")
    monitor._observe_files()
    assert state.progress_events == before + 1
    before = state.progress_events
    output.write_text("", encoding="utf-8")
    monitor._observe_files()
    assert state.progress_events == before, "truncation must not count as growth"
    output.unlink()
    monitor._observe_files()
    assert state.progress_events == before
    output.write_text("replacement", encoding="utf-8")
    monitor._observe_files()
    assert state.progress_events == before + 1
    before = state.progress_events
    output.write_text("", encoding="utf-8")
    monitor._observe_files()
    assert state.progress_events == before
    output.write_text("x", encoding="utf-8")
    monitor._observe_files()
    assert state.progress_events == before + 1, "growth below a prior high-water mark still counts"
    before = state.progress_events
    output.unlink()
    monitor._observe_files()
    output.write_text("x", encoding="utf-8")
    monitor._observe_files()
    assert state.progress_events == before + 1, "recreation at the same size still counts"
    assert process_tree._remember_group_cpu(-99, 1, 25) == 0.25
    assert process_tree._remember_group_cpu(-99, 2, 40) == 0.65
    process_tree._GROUP_CPU_CENTISECONDS.pop(-99)


def check_posix_tree():
    process = Mock(spec=["pid"])
    process.pid = 100
    process._pae_owned_session = True

    def record(parent, group, session, identity, cpu, reaped=0):
        return {"parent": parent, "group": group, "session": session, "identity": identity,
                "cpu": cpu, "reaped_cpu": reaped, "state": "S"}

    root = record(1, 100, 100, "root", 0.1)
    child = record(100, 901, 902, "child", 0.25)
    unrelated = record(1, 903, 904, "other", 10)
    with patch.object(process_tree, "_posix_snapshot", return_value={100: root, 101: child, 102: unrelated}):
        metrics = process_tree._posix_tree_metrics(process)
        assert abs(metrics["cpu_seconds"] - 0.35) < 0.001
        assert {item["pid"] for item in metrics["processes"]} == {100, 101}
    root = record(1, 100, 100, "root", 0.2, 0.4)
    with patch.object(process_tree, "_posix_snapshot", return_value={100: root}):
        metrics = process_tree._posix_tree_metrics(process)
        assert abs(metrics["cpu_seconds"] - 0.6) < 0.001, metrics
    recycled = record(100, 100, 100, "new-child", 0.05)
    with patch.object(process_tree, "_posix_snapshot", return_value={100: root, 101: recycled}):
        metrics = process_tree._posix_tree_metrics(process)
        assert abs(metrics["cpu_seconds"] - 0.65) < 0.001, metrics


def check_windows_tree():
    process = SimpleNamespace(pid=100, _pae_tree_lock=threading.RLock(),
                              _pae_known_pids={100: 10}, _pae_cpu_totals={})
    table = {100: (1, "parent"), 101: (100, "child")}
    identities = {100: (10, 0.1), 101: (20, 0.25)}
    with patch.object(process_tree, "_windows_api", return_value=SimpleNamespace()), \
            patch.object(process_tree, "_windows_processes", side_effect=lambda: table), \
            patch.object(process_tree, "_windows_pid_time", side_effect=lambda pid: identities.get(pid)):
        metrics = process_tree._windows_tree_metrics(process)
        assert abs(metrics["cpu_seconds"] - 0.35) < 0.001
        assert metrics["backend"] == "windows-pid-fallback"
        identities[101] = (30, 0.05)
        metrics = process_tree._windows_tree_metrics(process)
        assert abs(metrics["cpu_seconds"] - 0.4) < 0.001, metrics
        assert process._pae_known_pids[101] == 30
        table[102] = (101, "grandchild")
        identities[102] = (40, 0.2)
        metrics = process_tree._windows_tree_metrics(process)
        assert abs(metrics["cpu_seconds"] - 0.6) < 0.001, metrics
        for pid in range(103, 128):
            table[pid] = (100, "child")
            identities[pid] = (pid, 0.01)
        metrics = process_tree._windows_tree_metrics(process)
        assert metrics["active_processes"] == 28 and len(metrics["processes"]) == 20


def check_probe_runtime(root: Path):
    state = progress_watch.ProgressState(5)
    monitor = progress_watch.ProgressMonitor(Mock(), state, root,
                                             {"command": [sys.executable, "-S", "-c", "print(10)"], "mode": "increases"})
    monitor._observe_probe(monitor._run_probe())
    assert state.progress_events == 0
    monitor.progress_probe["command"] = [sys.executable, "-S", "-c", "import sys; print(99); sys.exit(1)"]
    assert monitor._run_probe() is None
    monitor._observe_probe(None)
    assert state.progress_events == 0
    monitor.progress_probe["command"] = [sys.executable, "-S", "-c", "print('x'*65537)"]
    assert monitor._run_probe() is None
    monitor.progress_probe.update(command=[sys.executable, "-S", "-c", "import time; time.sleep(20)"], timeout_seconds=1)
    started = time.monotonic()
    assert monitor._run_probe() is None and time.monotonic() - started < 2.5
    assert state.progress_events == 0
    monitor.progress_probe.update(command=[sys.executable, "-S", "-c", "print(11)"], timeout_seconds=5)
    monitor._observe_probe(monitor._run_probe())
    assert state.progress_events == 1 and state.last_progress_source == "probe"

    counter = root / "batch-count.txt"
    counter.write_text("0", encoding="utf-8")
    stop = threading.Event()

    def advance():
        number = 0
        while not stop.wait(0.25):
            number += 1
            counter.write_text(str(number), encoding="utf-8")

    updater = threading.Thread(target=advance, daemon=True)
    updater.start()
    process = process_tree.launch([sys.executable, "-S", "-c", "import time; time.sleep(3.4)"])
    probe = [sys.executable, "-S", "-c", "import pathlib,sys; print(pathlib.Path(sys.argv[1]).read_text())", str(counter)]
    with patch.object(process_tree, "metrics", return_value=None):
        state = progress_watch.ProgressState(1.6, hard_seconds=6)
        monitor = progress_watch.ProgressMonitor(process, state, root,
                      {"command": probe, "mode": "increases", "every_seconds": 1}).start()
        try:
            process.wait(timeout=6)
            assert process.returncode == 0 and monitor.reason is None, state.snapshot()
            assert state.last_progress_source == "probe" and state.progress_events >= 2
        finally:
            stop.set()
            updater.join(timeout=1)
            monitor.close()
            process_tree.terminate(process)
            process_tree.close(process)


def check_processes(root: Path):
    # CPU from a silent child must keep the parent alive beyond its idle budget;
    # on Windows this exercises startup Job assignment and accounting of exits.
    busy = "import time; end=time.monotonic()+1.4\nwhile time.monotonic()<end: pass"
    command = "import subprocess,sys; p=subprocess.Popen([sys.executable,'-S','-c'," + repr(busy) + "]); p.wait()"
    process = process_tree.launch([sys.executable, "-S", "-c", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    state = progress_watch.ProgressState(0.65, hard_seconds=5)
    monitor = progress_watch.ProgressMonitor(process, state, root).start()
    try:
        process.communicate(timeout=6)
        assert process.returncode == 0, (process.returncode, monitor.reason, state.snapshot())
        assert monitor.reason is None
        metric = process_tree.metrics(process)
        if os.name == "nt":
            assert metric and metric["backend"] == "windows-job", metric
            assert metric["cpu_seconds"] > 0.3, metric
            assert metric["active_processes"] == 0
    finally:
        monitor.close()
        process_tree.terminate(process)
        process_tree.close(process)

    # A slow read-only progress probe cannot hold the hard-ceiling watchdog.
    process = process_tree.launch([sys.executable, "-S", "-c", "import time; time.sleep(20)"])
    state = progress_watch.ProgressState(0, hard_seconds=0.5)
    monitor = progress_watch.ProgressMonitor(process, state, root,
              {"command": [sys.executable, "-S", "-c", "import time; time.sleep(10)"], "timeout_seconds": 5}).start()
    started = time.monotonic()
    try:
        process.wait(timeout=3)
        assert time.monotonic() - started < 1.8
        assert monitor.reason == "hard", (monitor.reason, state.snapshot())
    finally:
        monitor.close()
        process_tree.close(process)

    # Deadline enforcement remains available when platform CPU metrics fail.
    process = process_tree.launch([sys.executable, "-S", "-c", "import time; time.sleep(20)"])
    with patch.object(process_tree, "metrics", return_value=None):
        state = progress_watch.ProgressState(0.4)
        monitor = progress_watch.ProgressMonitor(process, state, root).start()
        try:
            process.wait(timeout=3)
            assert monitor.reason == "idle"
        finally:
            monitor.close()
            process_tree.close(process)

    if os.name == "nt":
        # A host refusing nested Job assignment still starts the guarded argv,
        # observes CPU, and can terminate the retained PID tree.
        api = process_tree._windows_api()
        with patch.object(api.kernel, "AssignProcessToJobObject", return_value=False):
            process = process_tree.launch([sys.executable, "-S", "-c", "import time; time.sleep(20)"])
        try:
            time.sleep(0.35)
            metric = process_tree.metrics(process)
            assert metric and metric["backend"] == "windows-pid-fallback"
            process_tree.terminate(process)
            assert process.poll() is not None
        finally:
            process_tree.close(process)

        child_script = ("import subprocess,sys,time; child=subprocess.Popen([sys.executable,'-S','-c',"
                        "'import time; time.sleep(20)'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); "
                        "print(child.pid,flush=True); time.sleep(.5)")
        with patch.object(api.kernel, "AssignProcessToJobObject", return_value=False):
            process = process_tree.launch([sys.executable, "-S", "-c", child_script], stdout=subprocess.PIPE)
        child_pid = None
        try:
            child_pid = int(process.stdout.readline())
            metric = process_tree.metrics(process)
            assert child_pid in {member["pid"] for member in metric["processes"]}
            process.wait(timeout=3)
            assert process_tree._windows_pid_time(child_pid) is not None
            process_tree.close(process)
            deadline = time.monotonic() + 2
            while process_tree._windows_pid_time(child_pid) is not None and time.monotonic() < deadline:
                time.sleep(.05)
            assert process_tree._windows_pid_time(child_pid) is None, "fallback close must stop cached descendants"
        finally:
            process_tree.terminate(process)
            process_tree.close(process)
            if process.stdout is not None:
                process.stdout.close()


def check_watcher(root: Path):
    repo = root / "watcher"
    repo.mkdir()
    map_path = repo / ".ai-work" / "SERVICE_MAP.md"
    map_path.parent.mkdir()
    sources, _ = service_map.scan_inputs(repo)
    data = {"schema_version": 1, "inventory_reviewed": True,
            "snapshot": {"algorithm": service_map.ALGORITHM, "digest": service_map.aggregate(sources)},
            "resources": [], "validations": [{"id": "v", "command": [sys.executable, "-S", "-c", "import time; time.sleep(20)"], "resources": []}]}
    template = service_map.MAP_BEGIN + "\n```json\n{}\n```\n" + service_map.MAP_END
    map_path.write_text(service_map.replace_map_data(template, data), encoding="utf-8")
    watcher = str(Path(__file__).with_name("resource_watch.py"))
    env = {**os.environ, "PAE_VALIDATION_IDLE_SECONDS": "0.35", "PAE_VALIDATION_HARD_SECONDS": "0"}
    result = subprocess.run([sys.executable, watcher, "run", "--repo-root", str(repo), "--validation", "v"],
                            capture_output=True, text=True, encoding="utf-8", env=env, timeout=6)
    assert result.returncode == 124 and "validation_stalled=confirmed" in result.stderr, (result.returncode, result.stderr)
    assert result.stderr.count("validation_stalled=") == 1
    env["PAE_VALIDATION_IDLE_SECONDS"], env["PAE_VALIDATION_HARD_SECONDS"] = "0", "0.35"
    result = subprocess.run([sys.executable, watcher, "run", "--repo-root", str(repo), "--validation", "v"],
                            capture_output=True, text=True, encoding="utf-8", env=env, timeout=6)
    assert result.returncode == 126 and "validation_ceiling=hard" in result.stderr, (result.returncode, result.stderr)
    assert "validation_stalled=" not in result.stderr
    assert all(key in result.stderr for key in ("idle_seconds=", "last_progress_source=", "window=", "ceiling="))
    # A mapped health command may be much slower than the validation idle
    # budget; it must be cancelled by the independent timeout decision.
    data["resources"] = [{"id": "slow", "evidence": ["explicit local dependency"], "checks": [
        {"id": "wait", "command": [sys.executable, "-S", "-c", "import time; time.sleep(20)"],
         "timeout_seconds": 60, "every_seconds": 10, "startup_grace_seconds": 0}]}]
    data["validations"][0]["resources"] = ["slow"]
    map_path.write_text(service_map.replace_map_data(template, data), encoding="utf-8")
    env["PAE_VALIDATION_IDLE_SECONDS"], env["PAE_VALIDATION_HARD_SECONDS"] = "0.35", "0"
    started = time.monotonic()
    result = subprocess.run([sys.executable, watcher, "run", "--repo-root", str(repo), "--validation", "v"],
                            capture_output=True, text=True, encoding="utf-8", env=env, timeout=6)
    assert result.returncode == 124 and time.monotonic() - started < 3, (result.returncode, result.stderr)


def check_streaming(root: Path):
    repo = root / "streaming"
    repo.mkdir()
    map_path = repo / ".ai-work" / "SERVICE_MAP.md"
    map_path.parent.mkdir()
    sources, _ = service_map.scan_inputs(repo)
    data = {"schema_version": 1, "inventory_reviewed": True,
            "snapshot": {"algorithm": service_map.ALGORITHM, "digest": service_map.aggregate(sources)},
            "resources": [], "validations": [{"id": "v", "command": [], "resources": []}]}
    template = service_map.MAP_BEGIN + "\n```json\n{}\n```\n" + service_map.MAP_END
    scripts = str(Path(__file__).resolve().parent)
    # Disable CPU evidence in the watcher, so these cases prove output progress
    # independently of interpreter startup and the repeated printing itself.
    shim = ("import sys; sys.path.insert(0," + repr(scripts) + "); import resource_watch; "
            "resource_watch.process_tree.metrics=lambda process: None; "
            "sys.exit(resource_watch.main())")
    env = {**os.environ, "PAE_VALIDATION_IDLE_SECONDS": "0.6", "PAE_VALIDATION_HARD_SECONDS": "0"}
    cases = [
        ("for n in range(8): print('step'+str(n),end='',flush=True); time.sleep(.2)", 0),
        ("for n in range(20): print('waiting',end='',flush=True); time.sleep(.15)", 124),
        ("for n in range(20): print('waiting',flush=True); time.sleep(.15)", 124),
        ("for n in range(8):\n text=('step'+str(n)+'🐈').encode(); "
         "sys.stdout.buffer.write(text[:-2]); sys.stdout.buffer.flush(); time.sleep(.05); "
         "sys.stdout.buffer.write(text[-2:]); sys.stdout.buffer.flush(); time.sleep(.15)", 0),
    ]
    for script, expected in cases:
        data["validations"][0]["command"] = [sys.executable, "-S", "-c", "import sys,time\n" + script]
        map_path.write_text(service_map.replace_map_data(template, data), encoding="utf-8")
        result = subprocess.run([sys.executable, "-S", "-c", shim, "run", "--repo-root", str(repo), "--validation", "v"],
                                capture_output=True, text=True, encoding="utf-8", env=env, timeout=6)
        assert result.returncode == expected, (expected, result.returncode, result.stdout, result.stderr)
        if expected == 124:
            assert result.stderr.count("validation_stalled=") == 1
        if "encode()" in script:
            assert "🐈" in result.stdout and "�" not in result.stdout, result.stdout


def main():
    check_state()
    check_policy()
    check_posix_tree()
    check_windows_tree()
    with tempfile.TemporaryDirectory(prefix="pae-progress-") as temporary:
        root = Path(temporary)
        check_observers(root)
        check_processes(root)
        check_probe_runtime(root)
        check_watcher(root)
        check_streaming(root)
    print("progress_watch_self_test: ok (9 check groups)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
