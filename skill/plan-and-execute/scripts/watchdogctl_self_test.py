#!/usr/bin/env python3
"""Synthetic watchdog fixtures; no providers, services or background workers."""
from __future__ import annotations

import contextlib
import datetime as dt
import hashlib
import io
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

sys.dont_write_bytecode = True
import watchdogctl as watchdog
import jobctl
import lifecyclectl
import planctl


def iso(value: float) -> str:
    return dt.datetime.fromtimestamp(value, dt.timezone.utc).isoformat()


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def hashes(root: Path) -> dict[str, str]:
    return {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in root.rglob("*") if path.is_file()}


class WatchdogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="watchdog-test-")
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "repo"
        self.home = Path(self.temp.name) / "home"
        self.repo.mkdir()
        self.now = time.time()
        self.plan = self.repo / ".ai-work" / "synthetic-plan"
        self.plan.mkdir(parents=True)
        self.task = {"id": "001", "status": "in_progress", "dependencies": [],
                     "started_at": iso(self.now - 3600), "attempts": 1,
                     "task_idle_timeout_seconds": 600, "provider": "codex",
                     "current_route": {"provider": "codex"}, "history": [],
                     "validation_jobs": [], "last_error": None}
        self.manifest = {"schema_version": 4, "plan_id": self.plan.name,
                         "repo_root": str(self.repo), "work_root": ".ai-work",
                         "state": "running", "summary_status": "pending",
                         "updated_at": iso(self.now - 3600), "tasks": [self.task]}
        write(self.plan / planctl.SENTINEL, {"plan_id": self.plan.name})
        self.save()
        self.lease(True)
        self.addCleanup(patch.stopall)
        patch.object(Path, "home", return_value=self.home).start()
        patch.dict(os.environ, {"CODEX_HOME": str(self.home / ".codex"),
                                "CLAUDE_CONFIG_DIR": str(self.home / ".claude")}).start()

    def save(self) -> None:
        write(self.plan / planctl.MANIFEST, self.manifest)

    def lease(self, live: bool) -> None:
        write(self.plan / lifecyclectl.LEASE_FILE,
              {"schema_version": 1, "plan_id": self.plan.name, "nonce": "synthetic",
               "hostname": socket.gethostname(), "pid": os.getpid() if live else 99999999,
               "created_at": iso(self.now - 3600)})

    def args(self, command: str = "status", *extra: str):
        return watchdog.build_parser().parse_args(
            [command, "--repo-root", str(self.repo), "--plan", str(self.plan), *extra])

    def items(self):
        return watchdog.collect(self.args(), self.now)

    def snapshot(self, *extra: str) -> tuple[int, list[str]]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output), patch.object(watchdog.time, "time", return_value=self.now):
            code = watchdog.main(["status", "--repo-root", str(self.repo), "--plan", str(self.plan), *extra])
        return code, output.getvalue().splitlines()

    def assert_anomaly(self, name: str) -> str:
        code, lines = self.snapshot()
        self.assertEqual(code, 1)
        self.assertEqual(len(lines), 1)
        self.assertTrue(lines[0].startswith(f"ANOMALY:{name}:{watchdog.ACTIONS[name]} "), lines)
        return lines[0]

    def log(self, text: str, age: float = 5, name: str = "001-attempt-1-codex.log") -> Path:
        path = self.plan / "logs" / name
        path.parent.mkdir(exist_ok=True)
        path.write_text(text, encoding="utf-8")
        os.utime(path, (self.now - age, self.now - age))
        return path

    def cooldown(self, until: float) -> None:
        write(self.plan / "results" / "001-availability.json",
              {"version": 1, "cooldowns": {"codex": {"until": until, "reason": "quota"}},
               "phases": {}, "events": []})

    def session(self, provider: str = "codex", *, cwd: Path | None = None,
                event_age: float = 5, mtime_age: float = 3600) -> Path:
        if provider == "codex":
            path = self.home / ".codex" / "sessions" / "2026" / "10" / "12" / "rollout-synthetic.jsonl"
            header = {"type": "session_meta", "payload": {"cwd": str(cwd or self.repo)}}
        else:
            project = re.sub(r"[^A-Za-z0-9]", "-", str(self.repo))
            path = self.home / ".claude" / "projects" / project / "synthetic.jsonl"
            header = {"cwd": str(cwd or self.repo)}
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(header) + "\n" + json.dumps({"timestamp": iso(self.now - event_age)}) + "\n",
                        encoding="utf-8")
        os.utime(path, (self.now - mtime_age, self.now - mtime_age))
        return path

    def job(self, status: str, *, idle: float = 5, lost: bool = False) -> Path:
        nonce = "a" * 32
        directory = self.plan / "jobs" / "SYNTHETIC"
        run = directory / "runs" / nonce
        write(directory / "current.json", {"nonce": nonce})
        write(run / "request.json", {"nonce": nonce, "started_at": iso(self.now - 3600)})
        write(run / "state.json", {"nonce": nonce, "id": "SYNTHETIC", "status": status,
              "started_at": iso(self.now - 3600), "idle_timeout_seconds": 600,
              "idle_seconds": idle, "observed_at": self.now,
              "supervisor_pid": 99999999 if lost else os.getpid(),
              "supervisor_identity": "synthetic" if lost else jobctl.pid_identity(os.getpid())})
        self.task["status"] = "completed"
        self.manifest["state"] = "completed"
        # The undeclared synthetic job is still independently observable.
        self.save()
        return run

    def test_all_task_anomaly_classes_and_owner_actions(self) -> None:
        for name, status, reason, live in [
            ("blocked", "blocked", "synthetic", True),
            ("permission_blocked", "blocked", "permission denied", True),
            ("classifier_blocked", "blocked", "classifier requires review", True),
            ("runner_dead", "in_progress", None, False),
            ("silent", "in_progress", None, True),
            ("awaiting_next", "pending", None, False),
        ]:
            with self.subTest(name=name):
                self.task.update(status=status, last_error=reason)
                self.task["current_route"] = None
                self.save()
                self.lease(live)
                line = self.assert_anomaly(name)
                if watchdog.ACTIONS[name] == "resume":
                    self.assertIn("run_concise.py", line)
                    self.assertIn("--plan", line)
                    self.assertIn("--once", line)

    def test_cooldown_wait_due_and_live_runner(self) -> None:
        self.task["status"] = "pending"
        self.save()
        self.lease(False)
        self.cooldown(self.now + 600)
        code, lines = self.snapshot()
        self.assertEqual(code, 0)
        self.assertIn("cooldown_until=", lines[0])
        self.cooldown(self.now - 1)
        self.assert_anomaly("quota_resume_due")
        self.lease(True)
        self.assertEqual(self.snapshot("--quiet"), (0, []))

    def test_recent_log_progress_is_healthy_and_quiet(self) -> None:
        self.log("PROGRESS stage=validate done=2 seq=4\nHEARTBEAT\n")
        self.assertEqual(self.items()[0]["logs"].popitem()[1]["progress"], 4)
        self.assertEqual(self.snapshot("--quiet"), (0, []))
        self.assertTrue(self.snapshot()[1][0].endswith(" running"))

    def test_latest_attempt_and_claim_baseline(self) -> None:
        self.log("PROGRESS stage=execute done=9\n", name="001-attempt-1-codex.log")
        self.task["attempts"] = 2
        self.save()
        self.assert_anomaly("silent")
        self.task["history"] = [{"event": "claimed", "at": iso(self.now - 5)}]
        self.save()
        self.assertEqual(self.snapshot("--quiet"), (0, []))

    def test_codex_last_event_overrides_stale_mtime_and_filters_repo(self) -> None:
        path = self.session(cwd=self.repo.parent)
        self.assert_anomaly("silent")
        path.unlink()
        self.session()
        self.assertEqual(self.snapshot("--quiet"), (0, []))
        self.lease(False)
        self.assert_anomaly("runner_dead")

    def test_claude_session_and_old_session_exclusion(self) -> None:
        self.task["current_route"] = {"provider": "claude"}
        self.save()
        self.session("claude", event_age=7200, mtime_age=0)
        self.assert_anomaly("silent")
        self.session("claude")
        self.assertEqual(self.snapshot("--quiet"), (0, []))

    def test_job_failure_lost_supervisor_and_silence(self) -> None:
        for status, lost, idle, anomaly in [("failed", False, 0, "job_failed"),
                                           ("running", True, 0, "job_failed"),
                                           ("running", False, 3600, "silent")]:
            with self.subTest(status=status, lost=lost):
                self.job(status, lost=lost, idle=idle)
                self.assert_anomaly(anomaly)

    def test_status_is_read_only_including_lost_job(self) -> None:
        self.job("running", lost=True)
        before = hashes(self.repo)
        self.assert_anomaly("job_failed")
        self.assertEqual(hashes(self.repo), before)
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUTF8": "1"}
        result = subprocess.run([sys.executable, str(Path(watchdog.__file__)), "status",
                                 "--repo-root", str(self.repo), "--plan", str(self.plan)],
                                capture_output=True, text=True, env=env, timeout=15)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(hashes(self.repo), before)

    def test_idle_override_and_documented_fallback(self) -> None:
        self.task["task_idle_timeout_seconds"] = 7200
        self.save()
        self.assertEqual(self.snapshot("--quiet"), (0, []))
        self.task["task_idle_timeout_seconds"] = 0
        self.save()
        self.assertEqual(self.items()[0]["window"], watchdog.DEFAULT_IDLE_SECONDS)
        del self.task["task_idle_timeout_seconds"]
        write(self.plan / planctl.CONFIG, {"task_idle_timeout_seconds": 7200})
        self.save()
        self.assertEqual(self.snapshot("--quiet"), (0, []))

    def test_watch_dedupes_persistently_and_rearms_after_recovery(self) -> None:
        before = hashes(self.plan)
        args = self.args("watch", "--iterations", "1")
        output = io.StringIO()
        with contextlib.redirect_stdout(output), patch.object(watchdog.time, "time", return_value=self.now):
            self.assertEqual(watchdog.watch(args), 1)
            self.assertEqual(watchdog.watch(args), 1)
        self.assertEqual(len(output.getvalue().splitlines()), 1)
        self.assertEqual(hashes(self.plan), before)
        self.assertEqual(len(list((self.repo / ".ai-work" / "watchdog").glob("*.json"))), 1)
        items = self.items()
        lines, state, _ = watchdog.observe(items, {}, self.now)
        self.assertEqual(len(lines), 1)
        self.assertEqual(watchdog.observe(items, state, self.now + 300)[0], [])
        self.lease(False)
        changed, state, _ = watchdog.observe(self.items(), state, self.now + 300)
        self.assertIn("runner_dead", changed[0])
        self.lease(True)
        self.log("PROGRESS stage=execute done=1\n")
        lines, state, code = watchdog.observe(self.items(), state, self.now + 300)
        self.assertEqual((lines, code), ([], 0))
        lines, _, code = watchdog.observe(self.items(), state, self.now + 1000)
        self.assertEqual(code, 1)
        self.assertIn("silent", lines[0])

    def test_watch_resets_on_size_change_even_with_stale_mtime(self) -> None:
        path = self.log("PROGRESS stage=execute done=1\n", age=3600)
        _, state, _ = watchdog.observe(self.items(), {}, self.now)
        path.write_text("PROGRESS stage=execute done=2\nPROGRESS stage=execute done=3\n", encoding="utf-8")
        os.utime(path, (self.now - 3600, self.now - 3600))
        lines, _, code = watchdog.observe(self.items(), state, self.now + 300)
        self.assertEqual((lines, code), ([], 0))

    def test_disappearing_evidence_does_not_reset_silence(self) -> None:
        path = self.log("PROGRESS stage=execute done=1\n", age=3600)
        _, state, _ = watchdog.observe(self.items(), {}, self.now)
        path.unlink()
        lines, _, code = watchdog.observe(self.items(), state, self.now + 300)
        self.assertEqual((lines, code), ([], 1))

    def test_finite_watch_interval_and_healthy_silence(self) -> None:
        self.log("PROGRESS stage=execute done=1\n")
        output = io.StringIO()
        with contextlib.redirect_stdout(output), patch.object(watchdog.time, "sleep") as sleep:
            self.assertEqual(watchdog.watch(self.args("watch", "--iterations", "2", "--interval", "600")), 0)
        sleep.assert_called_once_with(600)
        self.assertEqual(output.getvalue(), "")

    def test_completed_validation_jobs_are_omitted(self) -> None:
        self.job("failed")
        self.task["validation_jobs"] = ["SYNTHETIC"]
        self.manifest["summary_status"] = "generated"
        self.save()
        self.assertEqual(self.snapshot("--quiet"), (0, []))

    def test_summary_pending_and_waiting_dependencies(self) -> None:
        self.task["status"] = "completed"
        self.save()
        self.lease(False)
        self.assert_anomaly("awaiting_next")
        self.task.update(status="pending", dependencies=["002"])
        self.save()
        self.assertEqual(self.snapshot("--quiet"), (0, []))

    def test_scan_multiple_plans_and_help_exit_contract(self) -> None:
        args = watchdog.build_parser().parse_args(["status", "--repo-root", str(self.repo)])
        self.assertEqual(len(watchdog.collect(args, self.now)), 1)
        self.assertEqual(watchdog.interval("300"), 300)
        self.assertEqual(watchdog.interval("600"), 600)
        for value in ("299", "601"):
            with self.assertRaises(Exception):
                watchdog.interval(value)
        self.assertIn("Exit codes: 0 healthy, 1 anomaly, 2", watchdog.build_parser().format_help())

    def test_invalid_ledger_returns_error_without_writing(self) -> None:
        write(self.plan / "results" / "001-availability.json", {"version": 0})
        before = hashes(self.repo)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(self.snapshot(), (2, []))
        self.assertEqual(hashes(self.repo), before)


if __name__ == "__main__":
    unittest.main()
