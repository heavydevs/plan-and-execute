#!/usr/bin/env python3
"""Portable integration contracts for sliding validation clocks and durable handoff."""
from __future__ import annotations

import copy
import json
import os
import shlex
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import assistant_triage
import configure
import jobctl
import planctl
import routing_config
import routingctl
import run_isolated as runner
import service_map
from self_test import sample_spec


def command(code: str) -> str:
    if '\n' in code:
        code = f'exec({code!r})'
    argv = [sys.executable, '-u', '-c', code]
    return subprocess.list2cmdline(argv) if os.name == 'nt' else shlex.join(argv)


class RunnerProgressTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.log = self.root / '.ai-work' / 'validation.log'

    def validate(self, commands, idle=.3, hard=0):
        # Isolate output semantics from interpreter startup CPU and host scheduling.
        with patch.object(runner.process_tree, 'metrics', return_value=None):
            return runner.run_validation_commands(self.root, commands, self.log, idle, hard_timeout_seconds=hard)

    def test_completed_tests_keep_single_command_alive_beyond_idle(self):
        code = 'import time\nfor i in range(9):\n print("test class", i, "passed", flush=True); time.sleep(.1)'
        passed, results, reason = self.validate([command(code)])
        self.assertTrue(passed, reason)
        self.assertEqual(results[0]['exit_code'], 0)

    def test_each_command_in_set_starts_fresh(self):
        code = 'import time; time.sleep(.6)'
        passed, results, reason = self.validate([command(code), command(code)], idle=1)
        self.assertTrue(passed, reason)
        self.assertEqual(len(results), 2)

    def test_stall_after_completed_test_has_semantic_evidence(self):
        passed, results, reason = self.validate([command('import time; print("test 1 passed",flush=True); time.sleep(30)')])
        self.assertFalse(passed)
        self.assertEqual(results[0]['exit_code'], 124)
        self.assertTrue(results[0]['validation_stalled'])
        self.assertEqual(results[0]['failure_class'], 'semantic')
        self.assertTrue(results[0]['failure_evidence']['progress']['validation_stalled'])
        self.assertIn('last_progress_source=output', reason)

    def test_watch_telemetry_does_not_reset_command_idle(self):
        code = 'import time\nfor i in range(100):\n print("[resource-watch] cpu_seconds="+str(i),flush=True); time.sleep(.05)'
        passed, results, _ = self.validate([command(code)])
        self.assertFalse(passed)
        self.assertEqual(results[0]['exit_code'], 124)

    def test_hard_ceiling_is_separate_even_with_progress(self):
        code = 'import time\nfor i in range(100):\n print("test", i, "passed",flush=True); time.sleep(.05)'
        passed, results, _ = self.validate([command(code)], idle=.5, hard=.8)
        self.assertFalse(passed)
        self.assertEqual(results[0]['exit_code'], 126)
        self.assertFalse(results[0]['validation_stalled'])
        self.assertEqual(runner.validation_failure_class(results), 'timeout_ceiling')
        self.assertIsNone(runner.validation_failure_fingerprint(results))

    def test_timeout_kills_child_before_later_write_on_every_host(self):
        late = self.root / 'late.txt'
        child = f'from pathlib import Path; import time; time.sleep(1); Path({str(late)!r}).write_text("escaped")'
        parent = f'import subprocess,sys,time; subprocess.Popen([sys.executable,"-c",{child!r}]); time.sleep(30)'
        passed, results, _ = self.validate([command(parent)], idle=.3)
        self.assertFalse(passed)
        self.assertEqual(results[0]['exit_code'], 124)
        time.sleep(1.05)
        self.assertFalse(late.exists())

    def test_provider_idle_opt_in_default_and_repository_progress(self):
        log = self.root / '.ai-work' / 'worker.log'
        # Allow portable interpreter/Job Object startup while still running longer
        # than the idle window, with only repository writes as progress.
        code = 'from pathlib import Path; import time\nfor i in range(12):\n Path("result.txt").write_text(str(i)); time.sleep(.12)'
        with patch.object(runner.process_tree, 'metrics', return_value=None):
            code, _, err = runner.run_process([sys.executable, '-u', '-c', code], self.root, log,
                timeout_seconds=0, idle_timeout_seconds=1, stream_output=False)
        self.assertEqual(code, 0, err)
        code, _, _ = runner.run_process([sys.executable, '-c', 'import time; time.sleep(.35)'], self.root, log,
                                      timeout_seconds=0, stream_output=False)
        self.assertEqual(code, 0)

    def test_provider_idle_kill_and_legacy_hard_class(self):
        with patch.object(runner.process_tree, 'metrics', return_value=None):
            code, _, err = runner.run_process([sys.executable, '-c', 'import time; time.sleep(30)'],
                self.root, self.log, timeout_seconds=0, idle_timeout_seconds=.25, stream_output=False)
        self.assertEqual(code, 124)
        self.assertEqual(runner.classify_report_failure(None, err), 'semantic')
        self.assertEqual(runner.classify_report_failure(None, 'provider_ceiling=confirmed'), 'timeout_ceiling')

    def test_config_and_task_schema_bounds_and_migration(self):
        defaults = routing_config.merge(planctl.default_config(), routing_config.EXTRA_DEFAULTS)
        self.assertEqual(defaults['task_idle_timeout_seconds'], 0)
        self.assertEqual(defaults['validation_hard_timeout_seconds'], 0)
        self.assertEqual(defaults['assistant']['idle_timeout_seconds'], 0)
        self.assertEqual(runner.validation_timeout_seconds({}, {}), 1800)
        self.assertEqual(runner.validation_hard_timeout_seconds({'validation_hard_timeout_seconds': 300}, {'validation_hard_timeout_seconds': 200}), 200)
        for key in ('task_idle_timeout_seconds', 'validation_hard_timeout_seconds', 'validation_timeout_seconds'):
            for value in (0, 604800):
                routing_config.validate({key: value}, partial=True)
            for value in (True, -1, 604801, '1', float('nan')):
                with self.assertRaises(routing_config.ConfigError):
                    routing_config.validate({key: value}, partial=True)
        for value in (-1, 121, True):
            with self.assertRaises(routing_config.ConfigError):
                routing_config.validate({'assistant': {'idle_timeout_seconds': value}}, partial=True)
        raw = sample_spec()['tasks'][0]
        task = planctl.normalize_task({**raw, 'validation_commands': [], 'validation_jobs': ['VAL_BOOKS'],
                                      'validation_hard_timeout_seconds': 0, 'task_idle_timeout_seconds': 60}, 0, {'R001', 'R002'})
        self.assertEqual(task['validation_jobs'], ['VAL_BOOKS'])
        for values in (None, 'VAL_BOOKS', ['../job'], ['job', 'job'], [None], ['x'] * 33, ['_BOOKS'], ['CON'], ['NUL']):
            with self.assertRaises(planctl.PlanError):
                planctl.normalize_task({**raw, 'validation_jobs': values}, 0, {'R001', 'R002'})
        target = self.root / 'config.json'
        configured = {'validation_hard_timeout_seconds': 60, 'task_idle_timeout_seconds': 300,
                      'assistant': {'idle_timeout_seconds': 10}, 'validation_timeout_seconds': 0}
        configure.save(target, configured, None)
        self.assertEqual(json.loads(target.read_text()), configured)

    def test_service_map_checks_policy_even_with_invalid_resources(self):
        data = {'schema_version': 1, 'inventory_reviewed': True, 'resources': [],
                'validations': [{'id': 'VAL_BOOKS', 'command': ['python', '-V'],
                                 'resources': None, 'no_progress_timeout_seconds': True}]}
        errors = service_map.validate_data(data)
        self.assertTrue(any('resources' in error for error in errors), errors)
        self.assertTrue(any('no_progress_timeout_seconds' in error for error in errors), errors)

    def test_ceiling_blocks_without_escalation_or_stagnation(self):
        self.assertEqual(routingctl.escalation_step(['timeout_ceiling'], [('standard', 'medium'), ('strong', 'high')]), 0)
        task = {'id': '001', 'status': 'in_progress', 'subtasks': [], 'functional_failures': 0,
                'rate_limit_events': 0, 'max_attempts': 8, 'history': []}
        manifest = {'tasks': [task], 'events': []}
        with patch.object(planctl, 'save_manifest'):
            planctl.fail_task(self.root, manifest, '001', 'Explicit time ceiling reached', failure_class='timeout_ceiling')
        self.assertEqual(task['status'], 'blocked')
        self.assertNotIn('validation_stagnation', task)

    def test_resume_validation_checkpoint_does_not_dispatch_model(self):
        task = planctl.normalize_task({**sample_spec()['tasks'][0], 'validation_jobs': ['VAL_BOOKS']}, 0, {'R001', 'R002'})
        task['status'] = 'pending'
        task['attempts'] = 1
        plan = self.root / '.ai-work' / 'plan'
        checkpoint = runner.validation_checkpoint_path(plan, task)
        planctl.atomic_write_json(checkpoint, {'fingerprint': runner.validation_checkpoint_fingerprint(task),
            'report': {'status': 'completed'}, 'result_path': 'results/worker.json', 'attempt_number': 1})
        manifest = {'repo_root': str(self.root), 'tasks': [task]}
        with patch.object(planctl, 'save_manifest'), patch.object(runner, 'finish_task_validation', return_value=True) as finish, patch.object(runner, 'run_process') as model:
            self.assertTrue(runner.execute_one_task(plan, manifest, {}, task, provider_override=None, dry_run=False, no_wait=True))
        model.assert_not_called()
        finish.assert_called_once()
        self.assertEqual(task['attempts'], 1)

    def test_runner_waits_mapped_job_and_classifies_terminal(self):
        task = {'validation_jobs': ['VAL_BOOKS']}
        initial = {'state': 'running', 'validation_id': 'VAL_BOOKS'}
        terminal = {**initial, 'state': 'succeeded', 'exit_code': 0, 'idle_seconds': 2}
        evidence = self.root / 'packet.json'
        self.log.parent.mkdir(parents=True)
        with patch.object(jobctl, 'status_job', return_value=initial), patch.object(jobctl, 'wait_job', return_value=terminal) as waiter, patch.object(runner, 'job_evidence_current', return_value=True):
            passed, results, _ = runner.run_validation_jobs(self.root, task, self.log, evidence)
        self.assertTrue(passed)
        self.assertEqual(len(results), 1)
        waiter.assert_called_once()
        with patch.object(jobctl, 'status_job', return_value={**terminal, 'state': 'ceiling', 'exit_code': 126}):
            passed, results, _ = runner.run_validation_jobs(self.root, task, self.log, evidence)
        self.assertFalse(passed)
        self.assertEqual(results[0]['failure_class'], 'timeout_ceiling')

    def test_stale_or_unpinned_job_cannot_satisfy_acceptance(self):
        self.log.parent.mkdir(parents=True)
        succeeded = {'state': 'succeeded', 'validation_id': 'VAL_BOOKS', 'exit_code': 0}
        with patch.object(jobctl, 'status_job', return_value=succeeded):
            passed, results, _ = runner.run_validation_jobs(self.root, {'validation_jobs': ['VAL_BOOKS']}, self.log, self.root / 'packet.json')
        self.assertFalse(passed)
        self.assertEqual(results[0]['failure_class'], 'environmental')

    def test_detached_dependency_failure_remains_environmental_after_timeout(self):
        self.log.parent.mkdir(parents=True)
        for outcome, code in [('stalled', 124), ('ceiling', 126), ('failed', 1)]:
            with self.subTest(outcome=outcome):
                status = {'state': outcome, 'validation_id': 'VAL_BOOKS', 'exit_code': code,
                          'failure_class': 'environmental', 'environment_failure': 'health_check_failed'}
                with patch.object(jobctl, 'status_job', return_value=status):
                    passed, results, _ = runner.run_validation_jobs(self.root, {'validation_jobs': ['VAL_BOOKS']}, self.log, self.root / 'packet.json')
                self.assertFalse(passed)
                self.assertEqual(runner.validation_failure_class(results), 'environmental')
                self.assertIsNone(runner.validation_failure_fingerprint(results))
                self.assertEqual(results[0]['failure_evidence']['resources']['environment_failure'], 'health_check_failed')
                self.assertIn('environment_failure=health_check_failed', results[0]['output_tail'])

    def test_model_job_request_survives_worker_tree_and_pins_map(self):
        spec = sample_spec()
        spec['tasks'][0].update(validation_commands=[], validation_jobs=['VAL_BOOKS'])
        plan = planctl.create_plan(self.root, spec, '.ai-work', 'book-job')
        mapped = self.root / '.ai-work' / 'SERVICE_MAP.md'
        sources, _ = service_map.scan_inputs(self.root)
        data = {'schema_version': 1, 'inventory_reviewed': True, 'resources': [], 'toolchains': [],
                'snapshot': {'algorithm': service_map.ALGORITHM, 'digest': service_map.aggregate(sources)},
                'validations': [{'id': 'VAL_BOOKS', 'command': [sys.executable, '-c', 'import time; time.sleep(.6)'],
                                 'resources': [], 'no_progress_timeout_seconds': 2}]}
        template = service_map.MAP_BEGIN + '\n```json\n{}\n```\n' + service_map.MAP_END
        mapped.write_text(service_map.replace_map_data(template, data), encoding='utf-8')
        argv = [sys.executable, str(Path(jobctl.__file__)), 'start', '--plan', str(plan), '--id', 'VAL_BOOKS', '--validation', 'VAL_BOOKS']
        worker = f'import subprocess; raise SystemExit(subprocess.run({argv!r}).returncode)'
        code, _, error = runner.run_process([sys.executable, '-c', worker], self.root, self.log,
            timeout_seconds=0, stream_output=False, job_plan_dir=plan, validation_jobs=['VAL_BOOKS'])
        self.assertEqual(code, 0, error)
        status = jobctl.wait_job(plan, 'VAL_BOOKS', 5)
        self.assertEqual(status['state'], 'succeeded', status)
        self.assertTrue(runner.job_evidence_current(status, self.root))
        data['validations'][0]['command'] = [sys.executable, '-c', 'raise SystemExit(1)']
        mapped.write_text(service_map.replace_map_data(template, data), encoding='utf-8')
        self.assertFalse(runner.job_evidence_current(status, self.root))

    def test_assistant_idle_opt_in_remains_inside_fixed_advisory_budget(self):
        with patch.object(runner.process_tree, 'metrics', return_value=None):
            with self.assertRaisesRegex(assistant_triage.Skip, 'idle_timeout'):
                assistant_triage.bounded_process([sys.executable, '-c', 'import time; time.sleep(30)'],
                                                '', self.root, os.environ.copy(), 2, 100, idle_timeout=.25)


if __name__ == '__main__':
    unittest.main()
