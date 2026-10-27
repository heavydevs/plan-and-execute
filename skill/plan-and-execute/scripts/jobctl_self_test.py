#!/usr/bin/env python3
"""Detached-job regression checks using local fake commands and no model calls."""
from __future__ import annotations

import concurrent.futures
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

import jobctl
import process_tree

SCRIPTS = Path(__file__).resolve().parent
ENV = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"}


class JobTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="pae-job-test-")
        self.root = Path(self.temp.name)
        self.plan = self.root / "plan"
        self.plan.mkdir()
        self.ids = []

    def tearDown(self):
        for job_id in self.ids:
            try:
                jobctl.stop_job(self.plan, job_id)
            except (jobctl.JobError, OSError):
                pass
        self.temp.cleanup()

    def start(self, job_id, code, **options):
        self.ids.append(job_id)
        return jobctl.start_job(self.plan, job_id, [sys.executable, "-u", "-c", code], self.root, **options)

    def terminal(self, job_id, timeout=10):
        record = jobctl.wait_job(self.plan, job_id, timeout)
        self.assertNotIn(record["status"], jobctl.ACTIVE, record)
        return record

    def cli(self, *arguments):
        # Bound the wait operation, not unrelated sitecustomize startup in the test harness.
        return subprocess.run([sys.executable, "-S", str(SCRIPTS / "jobctl.py"), *arguments],
                              env=ENV, capture_output=True, text=True, encoding="utf-8", timeout=15)

    def test_detached_job_survives_starter_exit_and_wait_does_not_stop(self):
        code = "import time; time.sleep(1.2); print('finished')"
        result = self.cli("start", "--plan", str(self.plan), "--id", "detached", "--cwd", str(self.root),
                          "--idle-seconds", "5", "--", sys.executable, "-u", "-c", code)
        self.ids.append("detached")
        self.assertEqual(result.returncode, 0, result.stderr)
        before = time.monotonic()
        waiting = self.cli("wait", "--plan", str(self.plan), "--id", "detached", "--max-seconds", "0.1")
        self.assertEqual(waiting.returncode, 75, waiting.stderr)
        self.assertLess(time.monotonic() - before, 1)
        self.assertEqual(len(waiting.stdout.splitlines()), 1)
        self.assertIn("running progressing idle=", waiting.stdout)
        record = self.terminal("detached")
        self.assertEqual(record["status"], "succeeded", record)
        self.assertTrue(Path(record["log_path"]).read_text(encoding="utf-8").endswith("finished\n"))

    def test_detached_job_survives_model_owned_process_tree_cleanup(self):
        import planctl
        import service_map
        self.ids.append("model-owned")
        self.plan = self.root / ".ai-work" / "model-plan"
        self.plan.mkdir(parents=True)
        (self.plan / planctl.SENTINEL).write_text(json.dumps({"plan_id": "model-plan"}), encoding="utf-8")
        (self.plan / planctl.MANIFEST).write_text(json.dumps({"plan_id": "model-plan", "repo_root": str(self.root), "work_root": ".ai-work"}), encoding="utf-8")
        (self.plan / planctl.CONFIG).write_text("{}", encoding="utf-8")
        signatures, _ = service_map.scan_inputs(self.root)
        data = {"schema_version": 1, "inventory_reviewed": True,
                "snapshot": {"algorithm": service_map.ALGORITHM, "digest": service_map.aggregate(signatures)},
                "resources": [], "toolchains": [], "validations": [{"id": "model-owned", "resources": [],
                "command": [sys.executable, "-c", "import time; time.sleep(1.5); print(42)"], "no_progress_timeout_seconds": 5}]}
        template = (SCRIPTS.parent / "assets" / "service-map-template.md").read_text(encoding="utf-8")
        (self.root / ".ai-work" / "SERVICE_MAP.md").write_text(service_map.replace_map_data(template, data), encoding="utf-8")
        code = ("import subprocess,sys; s=subprocess.run([sys.executable,sys.argv[1]+'/jobctl.py','start','--plan',sys.argv[2],'--id','model-owned','--validation','model-owned']); "
                "assert s.returncode==0,s")
        env = {**ENV, "PAE_JOB_DISPATCH_PLAN": str(self.plan), "PAE_JOB_ALLOWED_IDS": json.dumps(["model-owned"]), "PAE_JOB_DISPATCH_PID": str(os.getpid())}
        worker = process_tree.launch([sys.executable, "-c", code, str(SCRIPTS), str(self.plan), str(self.root)],
                                     env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            stdout, stderr = worker.communicate(timeout=10)
            self.assertEqual(worker.returncode, 0, stderr.decode("utf-8", "replace"))
            self.assertEqual(jobctl.dispatch_jobs(self.plan, ["model-owned"]), 1)
            self.assertEqual(jobctl.dispatch_jobs(self.plan, ["model-owned"]), 0)
        finally:
            process_tree.terminate(worker)
            process_tree.close(worker)
        record = self.terminal("model-owned")
        self.assertEqual(record["status"], "succeeded", record)

    def test_failure_output_stays_on_disk_and_status_is_one_line(self):
        self.start("failure", "import sys; print('PRIVATE-DIAGNOSTIC'); sys.exit(23)", idle_seconds=5)
        record = self.terminal("failure")
        self.assertEqual(record["exit_code"], 23)
        result = self.cli("status", "--plan", str(self.plan), "--id", "failure")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(len(result.stdout.splitlines()), 1)
        self.assertNotIn("PRIVATE-DIAGNOSTIC", result.stdout + result.stderr)
        self.assertIn("failed code=23", result.stdout)

    def test_idle_stop_preserves_partial_output(self):
        # The window must outlast interpreter start-up on a loaded host, or the job stalls before it prints.
        self.start("idle", "import time; print('first', flush=True); time.sleep(30)", idle_seconds=4)
        record = self.terminal("idle")
        self.assertEqual(record["status"], "stalled", record)
        self.assertEqual(jobctl.exit_code(record), 124)
        self.assertIn("first", Path(record["log_path"]).read_text(encoding="utf-8"))
        self.assertEqual(Path(record["log_path"]).read_text(encoding="utf-8").count("[job] timeout=idle "), 1)
        self.assertGreaterEqual(record["idle_seconds"], 3.5)

    def test_meaningful_output_can_outlive_old_absolute_window(self):
        code = "import time\nfor n in range(7):\n print('step', n, flush=True)\n time.sleep(0.2)\n"
        self.start("output", code, idle_seconds=0.7)
        record = self.terminal("output")
        self.assertEqual(record["status"], "succeeded", record)
        self.assertGreater(record["elapsed_seconds"], 1)
        self.assertGreater(record["progress_events"], 2)

    def test_repeated_output_does_not_mask_stall(self):
        code = "import time\nwhile True:\n print('same waiting message', flush=True)\n time.sleep(0.2)\n"
        self.start("repeat", code, idle_seconds=0.7)
        record = self.terminal("repeat")
        self.assertEqual(record["status"], "stalled", record)

    def test_optional_hard_ceiling_wins_despite_progress(self):
        code = "import time\nn=0\nwhile True:\n print('step', n, flush=True)\n n+=1\n time.sleep(0.1)\n"
        self.start("hard", code, idle_seconds=1, hard_seconds=0.7)
        record = self.terminal("hard")
        self.assertEqual(record["reason"], "hard", record)
        self.assertEqual(jobctl.exit_code(record), 126)
        self.assertEqual(Path(record["log_path"]).read_text(encoding="utf-8").count("[job] timeout=hard "), 1)

    def test_file_and_probe_progress(self):
        code = "from pathlib import Path\nimport time\nfor n in range(7):\n Path('counter.txt').write_text(str(n))\n time.sleep(0.2)\n"
        self.start("file", code, idle_seconds=0.8, progress_files=["counter.txt"])
        record = self.terminal("file")
        self.assertEqual(record["status"], "succeeded", record)
        (self.root / "counter.txt").unlink()
        probe = {"command": [sys.executable, "-c", "from pathlib import Path; p=Path('counter.txt'); print(p.read_text() if p.exists() else 'missing')"], "every_seconds": 1}
        slower = code.replace("time.sleep(0.2)", "time.sleep(0.5)")
        self.start("probe", slower, idle_seconds=1.8, progress_probe=probe)
        record = self.terminal("probe")
        self.assertEqual(record["status"], "succeeded", record)

    def test_concurrent_active_start_is_idempotent_and_restart_has_new_nonce(self):
        argv = [sys.executable, "-u", "-c", "import time; time.sleep(20)"]
        self.ids.append("concurrent")
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as workers:
            futures = [workers.submit(jobctl.start_job, self.plan, "concurrent", argv, self.root, 5) for _ in range(2)]
            records = [future.result(timeout=10) for future in futures]
        self.assertEqual(records[0]["nonce"], records[1]["nonce"])
        with self.assertRaises(jobctl.JobError):
            jobctl.start_job(self.plan, "concurrent", [sys.executable, "-c", "print('different')"], self.root)
        stopped = jobctl.stop_job(self.plan, "concurrent")
        self.assertEqual(stopped["status"], "stopped", stopped)
        with self.assertRaises(jobctl.JobError):
            jobctl.start_job(self.plan, "concurrent", argv, self.root, 5)
        old_run, _ = jobctl.current_run(jobctl.job_dir(self.plan, "concurrent"))
        fresh = jobctl.start_job(self.plan, "concurrent", argv, self.root, 5, restart=True)
        self.assertNotEqual(fresh["nonce"], stopped["nonce"])
        # Old stop requests cannot reach the new generation.
        jobctl.write_record(old_run / "stop.json", {"nonce": stopped["nonce"]})
        self.assertEqual(jobctl.status_job(self.plan, "concurrent")["status"], "running")

    def test_queued_dispatch_stop_is_final_without_launching_command(self):
        from unittest.mock import patch
        self.ids.append("queued")
        map_path = self.root / "map.json"
        map_path.write_text("{}", encoding="utf-8")
        env = {"PAE_JOB_DISPATCH_PLAN": str(self.plan), "PAE_JOB_ALLOWED_IDS": json.dumps(["queued"]),
               "PAE_JOB_DISPATCH_PID": str(os.getpid())}
        argv = [sys.executable, "-c", "from pathlib import Path; Path('must-not-run').touch()"]
        with patch.dict(os.environ, env):
            started = jobctl.start_job(self.plan, "queued", argv, self.root, validation_id="queued",
                                      map_path=str(map_path), validation_fingerprint="a" * 64)
        self.assertEqual(started["status"], "starting", started)
        run, _ = jobctl.current_run(jobctl.job_dir(self.plan, "queued"))
        request = jobctl.read_record(run / "request.json")
        request["started_unix"] = time.time() - 20
        jobctl.write_record(run / "request.json", request)
        self.assertEqual(jobctl.status_job(self.plan, "queued")["status"], "starting")
        with patch.object(jobctl, "pid_identity", return_value=None):
            self.assertEqual(jobctl.status_job(self.plan, "queued")["reason"], "supervisor_lost")
        before = time.monotonic()
        stopped = jobctl.stop_job(self.plan, "queued")
        self.assertLess(time.monotonic() - before, 1)
        self.assertEqual(stopped["status"], "stopped", stopped)
        self.assertEqual(jobctl.dispatch_jobs(self.plan, ["queued"]), 0)
        self.assertEqual(jobctl.status_job(self.plan, "queued")["status"], "stopped")
        self.assertEqual(jobctl.stop_job(self.plan, "queued")["nonce"], stopped["nonce"])
        self.assertFalse((self.root / "must-not-run").exists())
        with patch.dict(os.environ, env):
            with self.assertRaises(jobctl.JobError):
                jobctl.start_job(self.plan, "queued", argv, self.root, validation_id="queued",
                                 map_path=str(map_path), validation_fingerprint="a" * 64)
            fresh = jobctl.start_job(self.plan, "queued", argv, self.root, validation_id="queued",
                                    map_path=str(map_path), validation_fingerprint="a" * 64, restart=True)
        self.assertNotEqual(fresh["nonce"], stopped["nonce"])
        self.assertEqual(jobctl.stop_job(self.plan, "queued")["status"], "stopped")

    def test_completed_command_does_not_expire_during_tree_cleanup(self):
        from unittest.mock import patch
        self.ids.append("cleanup")
        supervisors = []
        real_terminate = process_tree.terminate
        delayed = False

        def launch(run, cwd):
            thread = threading.Thread(target=jobctl.supervise, args=(run,), name="test-supervisor")
            supervisors.append(thread)
            thread.start()
            return True

        def terminate(process):
            nonlocal delayed
            if not delayed and threading.current_thread().name == "test-supervisor" and process.poll() is not None:
                delayed = True
                time.sleep(1)
            return real_terminate(process)

        with patch.object(jobctl, "launch_supervisor", side_effect=launch), patch.object(process_tree, "terminate", side_effect=terminate):
            jobctl.start_job(self.plan, "cleanup", [sys.executable, "-u", "-c", "print('finished', flush=True)"], self.root,
                             idle_seconds=0.7)
            record = self.terminal("cleanup")
            supervisors[0].join(timeout=5)
        self.assertFalse(supervisors[0].is_alive())
        self.assertTrue(delayed)
        self.assertEqual(record["status"], "succeeded", record)
        self.assertNotIn("[job] timeout=", Path(record["log_path"]).read_text(encoding="utf-8"))

    def test_stop_kills_descendants(self):
        child = self.root / "child.py"
        child.write_text("from pathlib import Path\nimport os,time\nPath('child.pid').write_text(str(os.getpid()))\ntime.sleep(30)\n", encoding="utf-8")
        code = "import subprocess,sys,time\nsubprocess.Popen([sys.executable,'child.py'])\ntime.sleep(30)\n"
        self.start("tree", code, idle_seconds=5)
        deadline = time.monotonic() + 5
        while not (self.root / "child.pid").exists() and time.monotonic() < deadline:
            time.sleep(0.05)
        child_pid = int((self.root / "child.pid").read_text())
        identity = jobctl.pid_identity(child_pid)
        self.assertIsNotNone(identity)
        stopped = jobctl.stop_job(self.plan, "tree")
        self.assertEqual(stopped["status"], "stopped", stopped)
        self.assertNotEqual(jobctl.pid_identity(child_pid), identity)

    def test_missing_launch_and_stale_supervisor_are_failed_without_pid_kill(self):
        self.start("stale", "import time; time.sleep(20)", idle_seconds=5)
        run, _ = jobctl.current_run(jobctl.job_dir(self.plan, "stale"))
        original = jobctl.read_record(run / "state.json")
        # The supervisor updates frequently; patch identity observations rather than its record.
        from unittest.mock import patch
        real = jobctl.pid_identity
        supervisor_pid = original["supervisor_pid"]
        with patch.object(jobctl, "pid_identity", side_effect=lambda pid: "unrelated-generation" if pid == supervisor_pid else real(pid)):
            result = jobctl.status_job(self.plan, "stale")
            self.assertEqual(result["status"], "failed")
            self.assertEqual(result["reason"], "supervisor_lost")
            jobctl.stop_job(self.plan, "stale")
        self.assertEqual(jobctl.status_job(self.plan, "stale")["status"], "running")

    def test_abandoned_start_is_failed_even_when_starter_is_still_alive(self):
        directory = jobctl.job_dir(self.plan, "abandoned")
        run = directory / "runs" / ("a" * 32)
        run.mkdir(parents=True)
        jobctl.write_record(directory / "current.json", {"nonce": "a" * 32})
        jobctl.write_record(run / "request.json", {"id": "abandoned", "nonce": "a" * 32,
                            "starter_pid": os.getpid(), "starter_identity": jobctl.pid_identity(os.getpid()),
                            "started_unix": time.time() - 20})
        record = jobctl.status_job(self.plan, "abandoned")
        self.assertEqual(record["status"], "failed")
        self.assertEqual(record["reason"], "supervisor_start_failed")

    def test_posix_ps_identity_does_not_change_with_process_state(self):
        from unittest.mock import patch
        birth = "Sat Oct 10 12:00:00 2026"
        samples = [subprocess.CompletedProcess([], 0, birth + " S\n"), subprocess.CompletedProcess([], 0, birth + " R\n"), subprocess.CompletedProcess([], 0, birth + " Z\n")]
        with patch.object(Path, "read_text", side_effect=OSError()), patch.object(jobctl.subprocess, "run", side_effect=samples):
            self.assertEqual(jobctl.posix_pid_identity(123), birth)
            self.assertEqual(jobctl.posix_pid_identity(123), birth)
            self.assertIsNone(jobctl.posix_pid_identity(123))

    def test_record_read_retries_transient_sharing_but_preserves_corruption_refusal(self):
        from unittest.mock import patch
        record = self.root / "record.json"
        record.write_text('{"status":"running"}', encoding="utf-8")
        with record.open("rb") as readable:
            with patch.object(Path, "open", side_effect=[PermissionError("sharing"), readable]) as opening, patch.object(jobctl.time, "sleep"):
                self.assertEqual(jobctl.read_record(record), {"status": "running"})
                self.assertEqual(opening.call_count, 2)
        with patch.object(Path, "open", side_effect=PermissionError("denied")) as opening, patch.object(jobctl.time, "sleep"):
            with self.assertRaises(jobctl.JobError):
                jobctl.read_record(record)
            self.assertGreater(opening.call_count, 1)
            self.assertLessEqual(opening.call_count, 30)
        record.write_text("{", encoding="utf-8")
        with patch.object(Path, "open", autospec=True, side_effect=lambda path, *args, **kwargs: open(path, *args, **kwargs)) as opening:
            with self.assertRaises(jobctl.JobError):
                jobctl.read_record(record)
            self.assertEqual(opening.call_count, 1)

    def test_secret_args_bad_ids_invalid_limits_rejected_before_creation(self):
        for argv in (["tool", "--api-key", "do-not-save"], ["tool", "--token=do-not-save"], ["tool", "https://user:pass@example.test"]):
            with self.assertRaises(jobctl.JobError):
                jobctl.start_job(self.plan, "secret", argv, self.root)
        self.assertFalse((self.plan / "jobs").exists())
        for identifier in ("../escape", ".", "..", "bad/name", "CON", "NUL.txt"):
            with self.assertRaises(jobctl.JobError):
                self.start(identifier, "pass")
        for limit in (True, -1, float("nan"), float("inf")):
            with self.assertRaises(jobctl.JobError):
                self.start("limits", "pass", idle_seconds=limit)
        for mode in ([], {}, None, True, 'heartbeat'):
            with self.assertRaises(jobctl.JobError):
                self.start('probe-schema', 'pass', progress_probe={'command': [sys.executable, '-V'], 'mode': mode})
        invalid = self.cli('start', '--plan', str(self.plan), '--id', 'probe-schema',
                           '--progress-probe', json.dumps({'command': [sys.executable, '-V'], 'mode': []}),
                           '--', sys.executable, '-V')
        self.assertEqual(invalid.returncode, 1)
        self.assertNotIn('Traceback', invalid.stderr)
        self.assertFalse((self.plan / 'jobs').exists())

    def test_launch_failure_is_durable(self):
        self.ids.append("missing")
        jobctl.start_job(self.plan, "missing", [str(self.root / "not-installed")], self.root)
        record = self.terminal("missing")
        self.assertEqual(record["status"], "failed")
        self.assertEqual(record["exit_code"], 127)
        self.assertEqual(record["reason"], "launch")

    def test_mapped_validation_checks_freshness_and_publishes_timeout_reason(self):
        import planctl
        import service_map
        # Isolate input discovery when test temp roots live inside another Git
        # checkout, whose ignore rules can otherwise hide the fixture files.
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        self.plan = self.root / ".ai-work" / "mapped-plan"
        self.plan.mkdir(parents=True)
        (self.plan / planctl.SENTINEL).write_text(json.dumps({"plan_id": "mapped-plan"}), encoding="utf-8")
        (self.plan / planctl.MANIFEST).write_text(json.dumps({"plan_id": "mapped-plan", "repo_root": str(self.root), "work_root": ".ai-work"}), encoding="utf-8")
        (self.plan / planctl.CONFIG).write_text("{}\n", encoding="utf-8")
        source = self.root / "package.json"
        source.write_text("{}\n", encoding="utf-8")
        signatures, truncated = service_map.scan_inputs(self.root)
        self.assertFalse(truncated)
        data = {"schema_version": 1, "inventory_reviewed": True,
                "snapshot": {"algorithm": service_map.ALGORITHM, "digest": service_map.aggregate(signatures)},
                "toolchains": [], "resources": [], "validations": [
                    {"id": "VAL_IDLE", "command": [sys.executable, "-c", "import time; time.sleep(20)"],
                     "resources": [], "no_progress_timeout_seconds": 1},
                    {"id": "VAL_HARD", "command": [sys.executable, "-c", "import time; time.sleep(20)"],
                     "resources": [], "no_progress_timeout_seconds": 0, "validation_hard_timeout_seconds": 1},
                    {"id": "VAL_PIN", "command": [sys.executable, "-c", "import time; time.sleep(20)"],
                     "resources": [], "no_progress_timeout_seconds": 5}]}
        template = (SCRIPTS.parent / "assets" / "service-map-template.md").read_text(encoding="utf-8")
        map_path = self.root / ".ai-work" / "SERVICE_MAP.md"
        map_path.write_text(service_map.replace_map_data(template, data), encoding="utf-8")
        for identifier, reason, code in (("VAL_IDLE", "idle", 124), ("VAL_HARD", "hard", 126)):
            self.ids.append(identifier)
            started = self.cli("start", "--plan", str(self.plan), "--id", identifier, "--validation", identifier)
            self.assertEqual(started.returncode, 0, started.stderr)
            record = self.terminal(identifier)
            self.assertEqual(record["validation_id"], identifier)
            self.assertEqual(record["reason"], reason, record)
            self.assertEqual(jobctl.exit_code(record), code)
        self.ids.append("VAL_PIN")
        started = self.cli("start", "--plan", str(self.plan), "--id", "VAL_PIN", "--validation", "VAL_PIN")
        self.assertEqual(started.returncode, 0, started.stderr)
        pinned = jobctl.status_job(self.plan, "VAL_PIN")
        self.assertEqual(pinned["map_path"], str(map_path))
        self.assertEqual(pinned["validation_fingerprint"], service_map.validation_fingerprint(data, "VAL_PIN"))
        data["validations"][2]["command"] = [sys.executable, "-c", "import time; time.sleep(10)"]
        map_path.write_text(service_map.replace_map_data(template, data), encoding="utf-8")
        changed = self.cli("start", "--plan", str(self.plan), "--id", "VAL_PIN", "--validation", "VAL_PIN")
        self.assertEqual(changed.returncode, 1)
        self.assertEqual(jobctl.status_job(self.plan, "VAL_PIN")["nonce"], pinned["nonce"])
        jobctl.stop_job(self.plan, "VAL_PIN")
        source.write_text('{"changed":true}\n', encoding="utf-8")
        self.ids.append("stale-map")
        stale = self.cli("start", "--plan", str(self.plan), "--id", "stale-map", "--validation", "VAL_IDLE")
        self.assertEqual(stale.returncode, 1)
        self.assertFalse((self.plan / "jobs" / "stale-map").exists())

    def test_environmental_watcher_failure_survives_later_stalled_state(self):
        script = self.root / "fake_watcher.py"
        script.write_text("import sys,time\nprint('[resource-watch] environment_failure=health_check_failed details=PRIVATE-DIAGNOSTIC',flush=True)\ntime.sleep(2.5)\nprint('[resource-watch] validation_stalled=confirmed id=environment-job idle_seconds=300',flush=True)\nsys.exit(124)\n", encoding="utf-8")
        self.ids.append("environment-job")
        jobctl.start_job(self.plan, "environment-job", [sys.executable, str(script)], self.root, validation_id="environment-job")
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            observed = jobctl.status_job(self.plan, "environment-job")
            if observed.get("failure_class") == "environmental":
                break
            time.sleep(0.05)
        self.assertEqual(observed["status"], "running", observed)
        self.assertEqual(observed["environment_failure"], "health_check_failed")
        final = self.terminal("environment-job")
        self.assertEqual(final["status"], "stalled", final)
        self.assertEqual(final["failure_class"], "environmental")
        self.assertEqual(final["environment_failure"], "health_check_failed")
        self.assertEqual(final["idle_seconds"], 300)
        self.assertNotIn("PRIVATE-DIAGNOSTIC", json.dumps(final))
        self.assertNotIn("PRIVATE-DIAGNOSTIC", jobctl.compact_status(final))

    def test_dispatch_context_rejects_unlisted_and_unmapped_jobs(self):
        from unittest.mock import patch
        env = {"PAE_JOB_DISPATCH_PLAN": str(self.plan), "PAE_JOB_ALLOWED_IDS": json.dumps(["allowed"]), "PAE_JOB_DISPATCH_PID": str(os.getpid())}
        with patch.dict(os.environ, env):
            for identifier, validation in (("unlisted", "unlisted"), ("allowed", None), ("allowed", "other")):
                with self.assertRaises(jobctl.JobError):
                    jobctl.start_job(self.plan, identifier, [sys.executable, "-c", "pass"], self.root, validation_id=validation)
            with self.assertRaises(jobctl.JobError):
                jobctl.start_job(self.plan, "allowed", [sys.executable, "-c", "pass"], self.root, validation_id="allowed")
        self.assertFalse((self.plan / "jobs").exists())

    def test_mapped_omission_inherits_task_and_config_without_overriding_explicit_map(self):
        import argparse
        from unittest.mock import patch
        import planctl
        import routing_config
        import service_map
        from self_test import sample_spec
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        with patch.dict(os.environ, {"PAE_MODEL_CATALOG_CACHE": str(self.root / "catalog-cache")}):
            self.plan = planctl.create_plan(self.root, sample_spec(), ".ai-work", "budget-plan")
        _, manifest = planctl.load_plan(self.plan)
        manifest["tasks"][0]["validation_jobs"] = ["VAL_BUDGET"]
        manifest["tasks"][0]["validation_timeout_seconds"] = 9
        manifest["tasks"][0]["validation_hard_timeout_seconds"] = 8
        jobctl.write_record(self.plan / planctl.MANIFEST, manifest)
        jobctl.write_record(self.plan / planctl.CONFIG, {"version": 2, "validation_timeout_seconds": 7, "validation_hard_timeout_seconds": 6})
        empty = self.root / "empty-config.json"
        empty.write_text("{}", encoding="utf-8")
        data = {"validations": [{"id": "VAL_BUDGET", "command": [sys.executable, "-c", "pass"], "resources": []}], "resources": [], "toolchains": [], "snapshot": {}}
        args = argparse.Namespace(plan=str(self.plan), id="VAL_BUDGET", validation="VAL_BUDGET",
                                  map=".ai-work/SERVICE_MAP.md", idle_seconds=None, hard_seconds=None)
        with patch.dict(os.environ, {"PAE_CONFIG_PATH": str(empty)}), patch.object(service_map, "load_map", return_value=("", data)), patch.object(service_map, "current_status", return_value=(True, {}, False, [])), patch.object(service_map, "validate_data", return_value=[]):
            _, _, effective = jobctl.mapped_start(args)
            self.assertEqual(effective["no_progress_timeout_seconds"], 9)
            self.assertEqual(effective["validation_hard_timeout_seconds"], 6)
            args.idle_seconds, args.hard_seconds = 4, 3
            _, _, effective = jobctl.mapped_start(args)
            self.assertEqual(effective["no_progress_timeout_seconds"], 4)
            self.assertEqual(effective["validation_hard_timeout_seconds"], 3)
            data["validations"][0].update(no_progress_timeout_seconds=0, validation_hard_timeout_seconds=2)
            _, _, effective = jobctl.mapped_start(args)
            self.assertEqual(effective["no_progress_timeout_seconds"], 0)
            self.assertEqual(effective["validation_hard_timeout_seconds"], 2)
            data["validations"][0].pop("no_progress_timeout_seconds")
            args.idle_seconds = None
            manifest["tasks"][0].pop("validation_timeout_seconds")
            jobctl.write_record(self.plan / planctl.MANIFEST, manifest)
            _, _, effective = jobctl.mapped_start(args)
            self.assertEqual(effective["no_progress_timeout_seconds"], 7)


if __name__ == "__main__":
    unittest.main()
