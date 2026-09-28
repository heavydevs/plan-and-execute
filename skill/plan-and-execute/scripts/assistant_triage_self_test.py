#!/usr/bin/env python3
"""Advisory safety/budget tests; native authenticated generation is not simulated."""
from __future__ import annotations
import copy
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import assistant_triage as a
import planctl
import routing_config
import run_isolated


class AssistantTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.plan = Path(self.tmp.name) / 'plan'
        (self.plan / 'results').mkdir(parents=True)
        self.config = routing_config.merge(planctl.default_config(), routing_config.EXTRA_DEFAULTS)
        self.config['assistant']['enabled'] = True
        self.config['assistant']['provider'] = 'claude'
        self.task = {'id': '001', 'functional_failures': 2, 'last_error': 'timeout',
                     'validation_stagnation': {'signature': 'a' * 64, 'repeats': 2}}
        self.results = [{'passed': False, 'command': 'npm test', 'exit_code': 1,
                         'output_tail': 'assert failed in connection pool', 'output_head': 'first failure'}]
        self.advice = {'suggested_class': 'environmental', 'confidence': .5,
                       'hypothesis': 'A dependency might be unavailable.', 'evidence_refs': ['E2']}
        self.invoke = Mock(return_value=self.advice)

    def call(self):
        return a.triage(self.plan, self.task, self.results, self.config, invoke=self.invoke)

    def test_disabled_success_and_first_failure_cost_nothing(self):
        self.config['assistant']['enabled'] = False
        self.assertEqual(self.call()['reason'], 'not_eligible')
        self.config['assistant']['enabled'] = True
        self.results[0]['passed'] = True
        self.assertEqual(self.call()['reason'], 'not_eligible')
        self.results[0]['passed'] = False
        self.task['validation_stagnation']['repeats'] = 1
        self.assertEqual(self.call()['reason'], 'not_eligible')
        self.invoke.assert_not_called()
        self.assertFalse(list((self.plan / 'results').iterdir()))

    def test_explicit_lint_type_and_syntax_diagnostics_skip(self):
        for command, output in [('ruff check .', 'F401 unused import'), ('npm test', 'error TS2345: bad argument'),
                                ('pytest', 'SyntaxError: unmatched bracket')]:
            self.results[0].update(command=command, output_tail=output)
            self.assertEqual(self.call()['reason'], 'not_eligible')
        self.invoke.assert_not_called()

    def test_repeat_once_and_survives_resume(self):
        before = copy.deepcopy(self.task)
        self.assertEqual(self.call()['status'], 'advice')
        self.assertEqual(self.call()['reason'], 'duplicate_evidence')
        self.invoke.assert_called_once()
        self.assertEqual(self.task, before)
        self.assertIn('Unverified', a.hint(self.plan, self.task, self.config))
        self.assertLess(len(a.hint(self.plan, self.task, self.config)), 700)
        self.task['functional_failures'] += 1
        self.assertEqual(a.hint(self.plan, self.task, self.config), '')

    def test_budget_applies_to_different_failure_signatures(self):
        self.call()
        self.task['validation_stagnation']['signature'] = 'b' * 64
        self.assertEqual(self.call()['reason'], 'attempt_budget')
        self.invoke.assert_called_once()

    def test_bad_output_timeout_and_interruption_consume_reservation(self):
        for failure in (ValueError('secret'), a.Skip('timeout'), KeyboardInterrupt()):
            with self.subTest(failure=type(failure).__name__):
                a.state_path(self.plan, '001').unlink(missing_ok=True)
                self.invoke.reset_mock()
                self.invoke.side_effect = failure
                if isinstance(failure, KeyboardInterrupt):
                    with self.assertRaises(KeyboardInterrupt):
                        self.call()
                else:
                    self.assertIn(self.call()['status'], ('skipped', 'invalid'))
                self.assertEqual(self.call()['reason'], 'duplicate_evidence')
                self.invoke.assert_called_once()
                self.assertNotIn('secret', a.state_path(self.plan, '001').read_text())

    def test_reserved_crash_cannot_repeat_or_corrupt_manifest(self):
        self.call()
        path = a.state_path(self.plan, '001')
        state = a.read_state(path)
        state['attempts'][0]['status'] = 'reserved'
        a.write_state(path, state)
        self.assertEqual(self.call()['reason'], 'duplicate_evidence')
        self.assertFalse((self.plan / 'manifest.json').exists())

    def test_resource_streaks_and_confirmed_stall_thresholds(self):
        output = '\n'.join(['[resource-watch] resource=db check=ping state=starting',
                            '[resource-watch] resource=db check=ping state=unhealthy',
                            '[resource-watch] resource=db check=ping state=healthy',
                            '[resource-watch] resource=db check=ping state=unhealthy'])
        self.assertEqual(a.observations(output), {'unhealthy_samples': 1})
        self.task['validation_stagnation']['repeats'] = 1
        self.results[0].update(a.observations(output))
        self.assertEqual(self.call()['reason'], 'not_eligible')
        self.results[0]['unhealthy_samples'] = 2
        self.assertEqual(self.call()['trigger'], 'unhealthy')
        a.state_path(self.plan, '001').unlink()
        self.results[0].update(unhealthy_samples=0, validation_stalled=True, validation_idle_seconds=299)
        self.assertEqual(self.call()['reason'], 'not_eligible')
        self.results[0]['validation_idle_seconds'] = 300
        self.assertEqual(self.call()['trigger'], 'stall')

    def test_evidence_redaction_and_total_prompt_limit(self):
        self.results[0].update(output_tail='Authorization: Bearer private-value\nAPI_KEY="secret-value"\n' + 'x'*15000,
                               command='https://user:pass@example.com?token=another-secret')
        prompt, refs, _ = a.evidence(self.task, self.results[0], 'repeated', 512)
        self.assertLessEqual(len(prompt), 512)
        self.assertIn('E2', refs)
        for secret in ('private-value', 'secret-value', 'another-secret', 'user:pass'):
            self.assertNotIn(secret, prompt)
        self.assertNotIn('PRIVATE KEY', a.redact('-----BEGIN PRIVATE KEY-----\nsecret'))
        self.assertNotIn('my-pass', a.redact('password=my-pass'))

    def test_strict_json_and_schema_reject_authority_and_unknown_refs(self):
        variants = [{**self.advice, 'status': 'completed'}, {**self.advice, 'confidence': True},
                    {**self.advice, 'confidence': float('nan')}, {**self.advice, 'suggested_class': 'success'},
                    {**self.advice, 'evidence_refs': ['../../../.env']}, {**self.advice, 'hypothesis': 'x'*601},
                    {**self.advice, 'evidence_refs': ['E2', 'E2']}]
        for value in variants:
            with self.assertRaises((ValueError, TypeError)):
                a.validate_advice(value, {'E1', 'E2'}, 2000)
        for raw in ('{"x":1,"x":2}', '{"x":NaN}', '```json\n{}\n```'):
            with self.assertRaises(ValueError):
                a.strict_json(raw)

    def test_unsafe_provider_and_missing_key_skip_without_call_or_budget(self):
        self.config['assistant']['provider'] = 'antigravity'
        with patch.object(a, 'native_invoke') as native:
            self.assertEqual(a.triage(self.plan, self.task, self.results, self.config)['reason'], 'unsupported_read_only_profile')
            self.config['assistant']['provider'] = 'claude'
            with patch.dict(os.environ, {}, clear=True):
                self.assertEqual(a.triage(self.plan, self.task, self.results, self.config)['reason'], 'explicit_anthropic_api_key_required')
            native.assert_not_called()
        self.assertFalse(list((self.plan / 'results').iterdir()))

    def test_profile_has_no_tools_hooks_mcp_worker_flags_or_secret_context(self):
        self.config['claude']['command'] = 'claude'
        self.config['claude']['extra_args'] = ['--dangerously-skip-permissions', '--resume', 'old']
        env = {'ANTHROPIC_API_KEY': 'key-not-in-prompt', 'AWS_SECRET_ACCESS_KEY': 'must-not-leak',
               'NODE_OPTIONS': '--require malicious.js', 'CLAUDE_CODE_OAUTH_TOKEN': 'oauth'}
        with patch.dict(os.environ, env, clear=True), patch.object(a.shutil, 'which', return_value='/usr/bin/claude'), \
                patch.object(a, 'bounded_process', return_value=' '.join(a.REQUIRED_FLAGS)):
            argv, child_env = a.native_profile(self.config, self.plan, {'E2'})
        self.assertEqual(argv[argv.index('--tools')+1], '')
        self.assertIn('--bare', argv)
        self.assertEqual(argv[argv.index('--mcp-config')+1], '{"mcpServers":{}}')
        self.assertNotIn('--dangerously-skip-permissions', argv)
        self.assertNotIn('--resume', argv)
        self.assertNotIn('AWS_SECRET_ACCESS_KEY', child_env)
        self.assertNotIn('NODE_OPTIONS', child_env)
        self.assertNotIn('CLAUDE_CODE_OAUTH_TOKEN', child_env)
        self.assertEqual(child_env['HOME'], str(self.plan))
        self.assertNotIn('key-not-in-prompt', json.dumps(argv))

    def test_unsupported_capability_and_wrapper_fail_closed(self):
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'key'}), patch.object(a.shutil, 'which', return_value='/usr/bin/claude'), \
                patch.object(a, 'bounded_process', return_value='--tools'):
            with self.assertRaises(a.Skip):
                a.native_profile(self.config, self.plan, {'E2'})
            self.config['claude']['command'] = ['python', 'untrusted.py']
            with self.assertRaises(a.Skip):
                a.native_profile(self.config, self.plan, {'E2'})

    def test_actual_process_capture_is_bounded_and_times_out(self):
        env = dict(os.environ)
        before = {p: p.read_bytes() for p in self.plan.rglob('*') if p.is_file()}
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            text = a.bounded_process([sys.executable, '-c', 'import sys; print(sys.stdin.read())'], 'hello', work, env, 2, 100)
            self.assertIn('hello', text)
            with self.assertRaisesRegex(a.Skip, 'output_limit'):
                a.bounded_process([sys.executable, '-c', 'print("x"*100000)'], '', work, env, 2, 100)
            started = time.monotonic()
            with self.assertRaisesRegex(a.Skip, 'timeout'):
                a.bounded_process([sys.executable, '-c', 'import time; time.sleep(10)'], '', work, env, .2, 100)
            self.assertLess(time.monotonic()-started, 4)
        self.assertEqual(before, {p: p.read_bytes() for p in self.plan.rglob('*') if p.is_file()})

    @unittest.skipIf(os.name == 'nt', 'POSIX process group contract')
    def test_timeout_kills_descendant_before_it_writes(self):
        marker = self.plan / 'must-not-appear'
        child = f'import time; from pathlib import Path; time.sleep(1); Path({str(marker)!r}).write_text("bad")'
        parent = f'import subprocess,sys,time; subprocess.Popen([sys.executable,"-c",{child!r}]); time.sleep(10)'
        with self.assertRaisesRegex(a.Skip, 'timeout'):
            a.bounded_process([sys.executable, '-c', parent], '', Path(self.tmp.name), dict(os.environ), .2, 100)
        time.sleep(1.1)
        self.assertFalse(marker.exists())

    def test_state_symlinks_lock_and_malformed_input_do_not_dispatch(self):
        path = a.state_path(self.plan, '001')
        lock = path.with_suffix('.lock')
        lock.write_text('busy')
        self.assertEqual(self.call()['status'], 'skipped')
        self.assertTrue(lock.exists())
        lock.unlink()
        path.write_text('not JSON')
        self.assertEqual(self.call()['status'], 'skipped')
        path.unlink()
        if os.name != 'nt':
            target = Path(self.tmp.name) / 'outside'
            target.write_text('untouched')
            path.symlink_to(target)
            self.assertEqual(self.call()['status'], 'skipped')
            self.assertEqual(target.read_text(), 'untouched')
        self.results[0]['unhealthy_samples'] = 'not an int'
        self.assertEqual(self.call()['status'], 'skipped')
        self.invoke.assert_not_called()

    def test_runner_keeps_deterministic_failure_authoritative(self):
        from self_test import sample_spec, write_fake_claude
        root = Path(self.tmp.name) / 'repository'
        root.mkdir()
        subprocess.run(['git', 'init', '-q'], cwd=root, check=True)
        plan = planctl.create_plan(root, sample_spec(), '.ai-work', 'advice-integration')
        _, manifest = planctl.load_plan(plan)
        task = manifest['tasks'][0]
        fake = Path(self.tmp.name) / 'worker.py'
        write_fake_claude(fake)
        config = copy.deepcopy(self.config)
        config['claude']['command'] = [sys.executable, str(fake)]
        config['stream_provider_output'] = False
        config['assistant']['unhealthy_threshold'] = 1
        results = [{**self.results[0], 'failure_class': 'semantic', 'unhealthy_samples': 1}]
        with patch.object(run_isolated, 'run_validation_commands', return_value=(False, results, 'assertion failed')), \
                patch.object(a, 'native_invoke', return_value=self.advice), \
                patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'unit-test-only'}):
            self.assertFalse(run_isolated.execute_one_task(plan, manifest, config, task,
                             provider_override=None, dry_run=False, no_wait=True))
        self.assertEqual(task['functional_failures'], 1)
        self.assertEqual(task['failure_classes'], ['semantic'])
        self.assertNotEqual(task['status'], 'completed')
        self.assertIn('environmental', a.hint(plan, task, config))

    def test_integration_validation_reads_bounded_first_and_last_evidence(self):
        program = 'print("first error"); print("x"*20000); print("last error")'
        import shlex
        command = shlex.join([sys.executable, '-c', program])
        command += ' && ' + shlex.join([sys.executable, '-c', 'raise SystemExit(1)'])
        passed, results, _ = run_isolated.run_validation_commands(self.plan, [command], self.plan/'validation.log', 5)
        self.assertFalse(passed)
        self.assertIn('first error', results[0]['output_head'])
        self.assertIn('last error', results[0]['output_tail'])
        self.assertLessEqual(len(results[0]['output_head']), 1200)
        self.assertLessEqual(len(results[0]['output_tail']), 2000)


if __name__ == '__main__':
    unittest.main()
