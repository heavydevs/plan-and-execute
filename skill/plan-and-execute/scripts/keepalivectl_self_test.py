#!/usr/bin/env python3
"""Synthetic keepalive fixtures; no providers, services, schedulers or real runners."""
from __future__ import annotations

import contextlib
import datetime as dt
import io
import json
import os
import socket
import sys
import tempfile
import time
import unittest
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.dont_write_bytecode = True
import keepalivectl as keepalive
import lifecyclectl
import planctl


def iso(value: float) -> str:
    return dt.datetime.fromtimestamp(value, dt.timezone.utc).isoformat()


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


class FakeProcess:
    pid = 4242

    def __init__(self, exit_code: int | None = None) -> None:
        self.exit_code = exit_code

    def poll(self) -> int | None:
        return self.exit_code


class KeepaliveTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="keepalive-test-")
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "repo"
        self.home = Path(self.temp.name) / "home"
        self.repo.mkdir()
        self.now = time.time()
        self.plan = self.repo / ".ai-work" / "synthetic-plan"
        self.plan.mkdir(parents=True)
        self.tasks = [
            {"id": "001", "status": "completed", "dependencies": [], "attempts": 1, "history": [],
             "validation_jobs": [], "last_error": None},
            {"id": "002", "status": "in_progress", "dependencies": ["001"], "attempts": 1,
             "started_at": iso(self.now - 3600), "provider": "claude", "current_route": {"provider": "claude"},
             "history": [], "validation_jobs": [], "last_error": None},
        ]
        self.manifest = {"schema_version": 4, "plan_id": self.plan.name, "repo_root": str(self.repo),
                         "work_root": ".ai-work", "state": "running", "summary_status": "pending",
                         "updated_at": iso(self.now - 3600), "tasks": self.tasks}
        write(self.plan / planctl.SENTINEL, {"plan_id": self.plan.name})
        self.save()
        self.lease(False)
        self.addCleanup(patch.stopall)
        patch.object(Path, "home", return_value=self.home).start()
        patch.dict(os.environ, {"CODEX_HOME": str(self.home / ".codex"),
                                "CLAUDE_CONFIG_DIR": str(self.home / ".claude")}).start()
        self.launcher = patch.object(keepalive, "launch", return_value=FakeProcess()).start()

    def save(self) -> None:
        write(self.plan / planctl.MANIFEST, self.manifest)

    def lease(self, live: bool) -> None:
        write(self.plan / lifecyclectl.LEASE_FILE,
              {"schema_version": 1, "plan_id": self.plan.name, "nonce": "synthetic",
               "hostname": socket.gethostname(), "pid": os.getpid() if live else 99999999,
               "created_at": iso(self.now - 3600)})

    def run_check(self, *extra: str) -> tuple[int, list[str]]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output), patch.object(keepalive.time, "time", return_value=self.now), \
                patch.object(keepalive.time, "sleep", lambda seconds: None):
            code = keepalive.main(["check", "--repo-root", str(self.repo), "--plan", str(self.plan),
                                   "--verify-seconds", "0", *extra])
        return code, output.getvalue().splitlines()

    def state(self) -> dict:
        return keepalive.read_state(keepalive.keepalive_directory(self.repo), keepalive.plan_key(self.plan))

    # --- decisions -----------------------------------------------------------------------------------------

    def test_live_runner_is_never_relaunched(self) -> None:
        self.lease(True)
        log = self.plan / "logs" / "002-attempt-1-claude.log"
        log.parent.mkdir(exist_ok=True)
        log.write_text("PROGRESS seq=1\n", encoding="utf-8")
        os.utime(log, (self.now - 5, self.now - 5))
        code, lines = self.run_check()
        self.assertEqual(code, 0)
        self.assertTrue(lines[0].startswith("keepalive:ok synthetic-plan runner_live"), lines)
        self.launcher.assert_not_called()

    def test_dead_runner_with_in_progress_task_is_relaunched_with_runner_args(self) -> None:
        code, lines = self.run_check("--runner-arg=--no-cleanup")
        self.assertEqual(code, 0, lines)
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0], "keepalive:launched synthetic-plan pid=4242 reason=runner_dead")
        argv, cwd, log = self.launcher.call_args.args
        self.assertEqual(Path(argv[1]).name, "run_concise.py")
        self.assertEqual(argv[2:], ["--plan", str(self.plan), "--no-cleanup"])
        self.assertEqual(cwd, self.repo.resolve())
        self.assertEqual(self.state()["launches"][0]["completed"], 1)

    def test_ready_pending_task_without_runner_is_relaunched(self) -> None:
        self.tasks[1].update(status="pending", started_at=None, current_route=None)
        self.save()
        code, lines = self.run_check()
        self.assertEqual(lines, ["keepalive:launched synthetic-plan pid=4242 reason=awaiting_next"])
        self.launcher.assert_called_once()

    def test_blocked_only_plan_is_reported_not_relaunched(self) -> None:
        self.tasks[1].update(status="blocked", last_error="needs a human decision")
        self.save()
        code, lines = self.run_check()
        self.assertEqual(code, 1)
        self.assertTrue(lines[0].startswith("ANOMALY:blocked:inspect_blocker "), lines)
        self.assertEqual(lines[1], "keepalive:skip synthetic-plan reason=blocked")
        self.launcher.assert_not_called()
        self.assertEqual(self.state()["launches"], [])

    def test_blocked_task_does_not_stop_relaunch_for_other_runnable_work(self) -> None:
        self.tasks.append({"id": "003", "status": "blocked", "dependencies": ["001"], "attempts": 1, "history": [],
                           "validation_jobs": [], "last_error": "needs a human decision"})
        self.save()
        code, lines = self.run_check()
        self.assertEqual(code, 1)
        self.assertTrue(any(line.startswith("ANOMALY:blocked:") for line in lines), lines)
        self.assertTrue(any(line.startswith("keepalive:launched ") for line in lines), lines)

    def test_completed_plan_with_generated_summary_is_left_alone(self) -> None:
        self.tasks[1]["status"] = "completed"
        self.manifest.update(state="completed", summary_status="generated")
        self.save()
        code, lines = self.run_check("--quiet")
        self.assertEqual((code, lines), (0, []))
        self.launcher.assert_not_called()

    def test_quota_cooldown_in_the_future_is_not_relaunched(self) -> None:
        self.tasks[1].update(status="pending", started_at=None, current_route=None)
        self.save()
        write(self.plan / "results" / "002-availability.json",
              {"version": 1, "cooldowns": {"claude": {"until": self.now + 1800, "reason": "quota"}},
               "phases": {}, "events": []})
        code, lines = self.run_check("--quiet")
        self.assertEqual((code, lines), (0, []))
        self.launcher.assert_not_called()

    def test_dry_run_reports_without_launching_or_writing_state(self) -> None:
        code, lines = self.run_check("--dry-run")
        self.assertEqual(lines, ["keepalive:would_launch synthetic-plan reason=runner_dead"])
        self.launcher.assert_not_called()
        self.assertFalse((keepalive.keepalive_directory(self.repo)).exists())

    # --- guards --------------------------------------------------------------------------------------------

    def test_restart_loop_without_progress_stops_relaunching(self) -> None:
        directory = keepalive.keepalive_directory(self.repo)
        key = keepalive.plan_key(self.plan)
        keepalive.write_state(directory, key, {"version": 1, "launches": [
            {"at": self.now - 600 * (3 - n), "completed": 1} for n in range(3)]})
        code, lines = self.run_check()
        self.assertEqual(code, 1)
        self.assertEqual(lines, ["ANOMALY:restart_loop:owner_inspect synthetic-plan/plan launches=3 window=180m completed=1"])
        self.launcher.assert_not_called()

    def test_progress_since_the_oldest_recent_launch_clears_the_loop_guard(self) -> None:
        directory = keepalive.keepalive_directory(self.repo)
        key = keepalive.plan_key(self.plan)
        keepalive.write_state(directory, key, {"version": 1, "launches": [
            {"at": self.now - 600 * (3 - n), "completed": 0} for n in range(3)]})
        code, lines = self.run_check()
        self.assertEqual(code, 0, lines)
        self.launcher.assert_called_once()

    def test_old_launches_outside_the_window_do_not_count(self) -> None:
        directory = keepalive.keepalive_directory(self.repo)
        key = keepalive.plan_key(self.plan)
        keepalive.write_state(directory, key, {"version": 1, "launches": [
            {"at": self.now - 3 * 3600 - 60 - n, "completed": 1} for n in range(5)]})
        code, lines = self.run_check()
        self.assertEqual(code, 0, lines)
        self.launcher.assert_called_once()

    def test_pause_and_resume_gate_relaunch(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            keepalive.main(["pause", "--plan", str(self.plan)])
        code, lines = self.run_check()
        self.assertEqual(lines, ["keepalive:skip synthetic-plan reason=paused"])
        self.launcher.assert_not_called()
        with contextlib.redirect_stdout(io.StringIO()):
            keepalive.main(["resume", "--plan", str(self.plan)])
        self.run_check()
        self.launcher.assert_called_once()

    def test_fresh_lock_blocks_a_second_tick(self) -> None:
        lock = keepalive.keepalive_directory(self.repo) / f"{keepalive.plan_key(self.plan)}.lock"
        lock.parent.mkdir(parents=True)
        lock.write_text("other", encoding="utf-8")
        code, lines = self.run_check()
        self.assertEqual(lines, ["keepalive:skip synthetic-plan reason=locked"])
        self.launcher.assert_not_called()
        self.assertTrue(lock.exists())

    def test_stale_lock_is_replaced_and_released_after_launch(self) -> None:
        lock = keepalive.keepalive_directory(self.repo) / f"{keepalive.plan_key(self.plan)}.lock"
        lock.parent.mkdir(parents=True)
        lock.write_text("other", encoding="utf-8")
        os.utime(lock, (self.now - 3600, self.now - 3600))
        code, lines = self.run_check()
        self.assertTrue(lines[0].startswith("keepalive:launched "), lines)
        self.assertFalse(lock.exists())

    # --- launch outcomes -----------------------------------------------------------------------------------

    def test_immediate_failure_is_an_anomaly_without_raw_output(self) -> None:
        self.launcher.return_value = FakeProcess(3)
        code, lines = self.run_check()
        self.assertEqual(code, 1)
        self.assertEqual(lines, ["ANOMALY:launch_failed:owner_inspect synthetic-plan/plan exit=3"])

    def test_availability_pause_exit_is_a_skip(self) -> None:
        self.launcher.return_value = FakeProcess(keepalive.AVAILABILITY_PAUSE)
        code, lines = self.run_check()
        self.assertEqual((code, lines), (0, ["keepalive:skip synthetic-plan reason=availability_pause"]))

    def test_clean_exit_is_reported_as_finished(self) -> None:
        self.launcher.return_value = FakeProcess(0)
        code, lines = self.run_check()
        self.assertEqual(lines, ["keepalive:launched_and_finished synthetic-plan pid=4242 reason=runner_dead"])

    def test_invalid_plan_exits_two(self) -> None:
        error = io.StringIO()
        with contextlib.redirect_stderr(error):
            code = keepalive.main(["check", "--repo-root", str(self.repo), "--plan", str(self.repo / "missing")])
        self.assertEqual(code, 2)
        self.assertIn("invalid evidence", error.getvalue())


class LaunchTests(unittest.TestCase):
    def test_launch_detaches_logs_and_passes_environment(self) -> None:
        with tempfile.TemporaryDirectory(prefix="keepalive-launch-") as temporary:
            root = Path(temporary)
            marker = root / "marker.txt"
            script = root / "child.py"
            script.write_text(
                "import os, sys\n"
                f"open({str(marker)!r}, 'w').write(os.environ.get('PYTHONUTF8', '') + ' ' + ' '.join(sys.argv[1:]))\n"
                "print('child-output')\n", encoding="utf-8")
            log = root / "logs" / "runner.log"
            process = keepalive.launch([sys.executable, str(script), "--plan", "x"], root, log)
            process.wait(timeout=30)
            self.assertEqual(marker.read_text(encoding="utf-8"), "1 --plan x")
            self.assertIn("child-output", log.read_text(encoding="utf-8"))

    def test_oversized_log_is_rotated(self) -> None:
        with tempfile.TemporaryDirectory(prefix="keepalive-rotate-") as temporary:
            root = Path(temporary)
            log = root / "runner.log"
            log.write_bytes(b"x" * (keepalive.MAX_LOG_BYTES + 1))
            process = keepalive.launch([sys.executable, "-c", "print('new')"], root, log)
            process.wait(timeout=30)
            self.assertTrue(log.with_suffix(".log.1").exists())
            self.assertEqual(log.read_text(encoding="utf-8").strip(), "new")

    def test_console_python_never_returns_pythonw(self) -> None:
        with tempfile.TemporaryDirectory(prefix="keepalive-python-") as temporary:
            (Path(temporary) / "pythonw.exe").write_text("", encoding="utf-8")
            (Path(temporary) / "python.exe").write_text("", encoding="utf-8")
            with patch.object(keepalive.sys, "executable", str(Path(temporary) / "pythonw.exe")):
                self.assertEqual(Path(keepalive.console_python()).name, "python.exe")
                self.assertEqual(Path(keepalive.windowless_python()).name, "pythonw.exe")


class ScheduleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="keepalive-schedule-")
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "repo"
        self.plan = self.repo / ".ai-work" / "plan-one"
        self.plan.mkdir(parents=True)
        manifest = {"schema_version": 4, "plan_id": "plan-one", "repo_root": str(self.repo), "work_root": ".ai-work",
                    "state": "running", "summary_status": "pending", "tasks": []}
        write(self.plan / planctl.SENTINEL, {"plan_id": "plan-one"})
        write(self.plan / planctl.MANIFEST, manifest)

    def schedule(self, *extra: str) -> tuple[int, str, str]:
        output, error = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            code = keepalive.main(["schedule", *extra, "--plan", str(self.plan)])
        return code, output.getvalue(), error.getvalue()

    def test_task_xml_is_hidden_repeats_and_escapes_arguments(self) -> None:
        xml = keepalive.task_xml(r"C:\Py thon\pythonw.exe", ["a&b.py", "check", "--plan", r"C:\x y\<p>"],
                                 Path(r"C:\repo"), 20, "2026-10-12T17:00:00")
        self.assertIn("<Interval>PT20M</Interval>", xml)
        self.assertIn("<Hidden>true</Hidden>", xml)
        self.assertIn("<MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>", xml)
        self.assertIn("a&amp;b.py", xml)
        self.assertIn("&lt;p&gt;", xml)
        self.assertNotIn("<p>", xml)

    def test_scheduled_arguments_forward_runner_args_in_equals_form(self) -> None:
        args = keepalive.build_parser().parse_args(
            ["schedule", "print", "--plan", str(self.plan), "--runner-arg=--no-cleanup"])
        arguments = keepalive.scheduled_arguments(args, self.plan.resolve(), self.repo.resolve())
        self.assertEqual(arguments[1], "check")
        self.assertIn("--quiet", arguments)
        self.assertIn("--runner-arg=--no-cleanup", arguments)

    def test_cron_line_runs_every_n_minutes_and_logs(self) -> None:
        line = keepalive.cron_line(20, ["/s/keepalivectl.py", "check", "--plan", "/p q"], Path("/l/keepalive.log"))
        self.assertTrue(line.startswith("*/20 * * * * "), line)
        self.assertIn("'/p q'", line)
        self.assertIn("keepalive.log", line)
        self.assertTrue(line.endswith("2>&1"), line)

    def test_install_requires_confirmation_and_creates_nothing(self) -> None:
        with patch.object(keepalive, "schtasks") as run, patch.object(keepalive, "os", SimpleNamespace(name="nt")):
            code, out, err = self.schedule("install")
        self.assertEqual(code, 2)
        self.assertIn("--yes", err)
        run.assert_not_called()

    def test_install_remove_status_call_schtasks_with_the_stable_task_name(self) -> None:
        name = keepalive.task_name(self.plan.resolve())
        calls: list[list[str]] = []

        def fake(arguments):
            calls.append(arguments)
            if arguments[0] == "/Create":
                data = Path(arguments[arguments.index("/XML") + 1]).read_bytes()
                self.assertEqual(data[:2], b"\xff\xfe")
                self.assertIn("PT20M", data[2:].decode("utf-16-le"))
            return MagicMock(returncode=0)

        with patch.object(keepalive, "schtasks", side_effect=fake), patch.object(keepalive, "os", SimpleNamespace(name="nt")):
            self.assertEqual(self.schedule("install", "--yes")[0], 0)
            self.assertIn(f"keepalive:schedule {name} present", self.schedule("status")[1])
            self.assertIn(f"keepalive:schedule_removed {name}", self.schedule("remove")[1])
        self.assertEqual([call[0] for call in calls], ["/Create", "/Query", "/Delete"])
        self.assertTrue(all(name in call for call in calls))

    def test_every_is_bounded(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            keepalive.main(["schedule", "print", "--plan", str(self.plan), "--every", "0"])


class AtomicWriteTests(unittest.TestCase):
    """A transient WinError 5/32 from os.replace once killed a runner; plan writes must retry."""

    def test_transient_permission_error_is_retried(self) -> None:
        with tempfile.TemporaryDirectory(prefix="keepalive-atomic-") as temporary:
            target = Path(temporary) / "manifest.json"
            real, calls = os.replace, {"count": 0}

            def flaky(source, destination):
                calls["count"] += 1
                if calls["count"] < 4:
                    raise PermissionError(5, "denied")
                return real(source, destination)

            with patch.object(planctl.os, "replace", flaky), patch.object(planctl.time, "sleep", lambda seconds: None):
                planctl.atomic_write_text(target, "ok")
            self.assertEqual((calls["count"], target.read_text(encoding="utf-8")), (4, "ok"))
            self.assertEqual([path.name for path in Path(temporary).iterdir()], ["manifest.json"])

    def test_persistent_denial_raises_and_leaves_no_temporary_file(self) -> None:
        with tempfile.TemporaryDirectory(prefix="keepalive-atomic-") as temporary:
            target = Path(temporary) / "manifest.json"

            def denied(source, destination):
                raise PermissionError(5, "denied")

            with patch.object(planctl.os, "replace", denied), patch.object(planctl.time, "sleep", lambda seconds: None):
                with self.assertRaises(PermissionError):
                    planctl.atomic_write_text(target, "never")
            self.assertEqual(list(Path(temporary).iterdir()), [])


if __name__ == "__main__":
    result = unittest.main(exit=False, verbosity=0).result
    if result.wasSuccessful():
        print("keepalive self-test passed")
    raise SystemExit(0 if result.wasSuccessful() else 1)
