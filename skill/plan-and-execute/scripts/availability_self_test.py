#!/usr/bin/env python3
"""Availability regressions: actual fake CLI processes, no authenticated calls."""
from __future__ import annotations
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import availability as av
import planctl
import routing_config as cfg
import run_isolated as run
from self_test import sample_spec, write_fake_claude


class AvailabilityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'repo'
        self.root.mkdir()
        subprocess.run(['git', 'init', '-q'], cwd=self.root, check=True)
        self.plan = planctl.create_plan(self.root, sample_spec(), '.ai-work', 'availability')
        _, self.manifest = planctl.load_plan(self.plan)
        self.task = self.manifest['tasks'][0]
        self.config = cfg.merge(planctl.default_config(), cfg.EXTRA_DEFAULTS)
        self.config['stream_provider_output'] = False
        self.config['rate_limit']['auto_wait'] = False
        self.config['claude']['command'] = sys.executable
        self.config['codex']['command'] = sys.executable
        self.intent = {'provider': 'claude', 'tier': 'strong', 'effort': 'high', 'requested_effort': 'xhigh', 'model': 'example'}

    def select(self, *, visited=None, now=100, phase='implementation', intent=None, available=lambda p: True):
        return av.select(self.plan, self.task, self.config, intent or self.intent, None,
                         phase, visited or set(), available, run.clamp_effort, now=now)

    def prepare_processes(self, design=False):
        fail = Path(self.tmp.name) / 'unavailable.py'
        fail.write_text('import sys\nprint("quota exceeded", file=sys.stderr)\nsys.exit(1)\n')
        good = Path(self.tmp.name) / 'available.py'
        write_fake_claude(good)
        good.write_text(good.read_text().replace('elif "--json-schema" in args:', 'elif "--json-schema" in args or "--output-schema" in args:'))
        self.config['claude']['command'] = [sys.executable, str(fail)]
        self.config['codex']['command'] = [sys.executable, str(good)]
        if design:
            self.task['design_route'] = {'model_tier': 'strong', 'reasoning_effort': 'medium'}
            # A valid persisted task spec must declare high complexity for two phases.
            self.task['complexity'] = 'high'
            planctl.save_manifest(self.plan, self.manifest)

    def execute(self):
        return run.execute_one_task(self.plan, self.manifest, self.config, self.task,
                                    provider_override=None, dry_run=False, no_wait=True)

    def test_concise_entrypoint_preserves_explicit_model_and_effort_cap(self):
        config = {'version': 2, 'codex': {'models': {'strong': 'user-model'},
                  'models_without_effort': ['user-model'], 'max_effort_by_tier': {'strong':'medium'}}}
        (self.plan/planctl.CONFIG).write_text(json.dumps(config))
        code = "import sys; from pathlib import Path; import run_concise; c=run_concise.run_isolated.load_config(Path(sys.argv[1])); assert c['codex']['models']['strong']=='user-model'; assert c['codex']['max_effort_by_tier']['strong']=='medium'; assert c['codex']['models_without_effort']==['user-model']"
        subprocess.run([sys.executable, '-c', code, str(self.plan)], cwd=Path(__file__).parent, check=True)

    def test_categories_do_not_confuse_cancellation_budget_or_bad_arguments(self):
        for text, category in [('429 too many requests','quota'), ('login required','authentication'),
                               ('HTTP 503 service unavailable','capacity'), ('unknown option --effort; 429','configuration')]:
            self.assertEqual(av.classify(1, text, []), category)
        self.assertEqual(av.classify(75, '', [75]), 'configured_exit')
        for code in (0, 130, 143, -2, -15, 124):
            self.assertIsNone(av.classify(code, '429 quota exceeded', [code]))
        self.assertIsNone(av.classify(1, 'error_max_turns', []))

    def test_same_logical_rung_with_different_provider_ladders_and_caps(self):
        self.config['codex']['max_effort_by_tier']['strong'] = 'medium'
        first = self.select()
        av.unavailable(self.plan, self.task['id'], 'implementation', first, 'quota', self.config, now=100)
        second = self.select()
        self.assertEqual((second['provider'], second['tier'], second['requested_effort'], second['effort']), ('codex','strong','xhigh','medium'))
        self.assertEqual(self.task['functional_failures'], 0)
        self.assertEqual(self.task.get('failure_classes', []), [])

    def test_cooldown_survives_reload_then_expires(self):
        first = self.select()
        av.unavailable(self.plan, self.task['id'], 'implementation', first, 'authentication', self.config, now=100)
        self.assertEqual(self.select(now=101)['provider'], 'codex')
        self.assertEqual(self.select(now=401)['provider'], 'claude')
        self.assertNotIn('secret', json.dumps(av.read(self.plan, self.task['id'])))

    def test_whole_chain_pauses_and_pinned_provider_never_widens(self):
        self.task['provider'] = 'claude'
        self.task['allow_provider_fallback'] = False
        first = self.select()
        av.unavailable(self.plan, self.task['id'], 'implementation', first, 'quota', self.config, now=100)
        with self.assertRaises(av.AvailabilityPaused):
            self.select()
        self.assertEqual(self.task['status'], 'pending')

    def test_current_route_cannot_escalate_same_availability_sequence(self):
        first = self.select()
        self.task['current_route'] = first
        av.unavailable(self.plan, self.task['id'], 'implementation', first, 'quota', self.config, now=100)
        recomputed = {**self.intent, 'tier': 'max', 'requested_effort': 'max'}
        self.assertEqual(self.select(intent=recomputed)['tier'], 'strong')
        self.task['functional_failures'] = 1
        self.task['failure_classes'] = ['semantic']
        self.assertEqual(self.select(intent=recomputed)['tier'], 'max')

    def test_escalated_tier_uses_its_own_chain_and_phases_are_separate(self):
        self.config['tier_routes'] = {'strong': {'primary': 'antigravity', 'fallbacks': ['codex']}}
        self.assertEqual(self.select()['provider'], 'antigravity')
        self.select(phase='design', intent={**self.intent,'tier':'max'})
        state = av.read(self.plan, self.task['id'])
        self.assertEqual(set(state['phases']), {'design','implementation'})

    def test_dry_run_no_ledger_write_and_missing_cli_no_claim(self):
        with self.assertRaises(av.AvailabilityPaused):
            av.select(self.plan, self.task, self.config, self.intent, None, 'implementation', set(), lambda _:False, run.clamp_effort, persist=False)
        self.assertFalse((self.plan/'results'/f'{self.task["id"]}-availability.json').exists())
        self.assertEqual(self.task['attempts'], 0)

    def test_corrupt_ledger_fails_closed(self):
        path = self.plan/'results'/f'{self.task["id"]}-availability.json'
        for raw in ('[]', '{', '{"version":1,"cooldowns":{"claude":{"until":NaN}},"phases":{},"events":[]}'):
            path.write_text(raw)
            with self.assertRaises(av.AvailabilityError): self.select()

    def test_actual_subprocess_quota_then_fallback_success(self):
        self.prepare_processes()
        self.assertTrue(self.execute())
        self.assertEqual(self.task['status'], 'completed')
        self.assertEqual(self.task['functional_failures'], 0)
        self.assertEqual(self.task['rate_limit_events'], 1)
        self.assertEqual(self.task['current_route']['provider'], 'codex')
        self.assertEqual((self.root/'implemented.txt').read_text(), 'implemented\n')

    def test_design_fallback_also_preserves_implementation_route(self):
        self.prepare_processes(design=True)
        self.assertTrue(self.execute())
        self.assertEqual(self.task['design_phase']['route']['provider'], 'codex')
        self.assertEqual(self.task['design_phase']['route']['tier'], 'strong')
        self.assertEqual(self.task['current_route']['tier'], 'economy')
        self.assertEqual(self.task['functional_failures'], 0)

    def test_total_failure_bounded_and_resume_does_not_spin(self):
        self.prepare_processes()
        self.config['codex']['command'] = self.config['claude']['command']
        with patch.object(run, 'wait_after_rate_limit', side_effect=AssertionError('must not wait before fallback')):
            with self.assertRaises(av.AvailabilityPaused): self.execute()
            attempts = self.task['attempts']
            with self.assertRaises(av.AvailabilityPaused): self.execute()
        self.assertEqual(attempts, 2)
        self.assertEqual(self.task['attempts'], 2)
        self.assertEqual(self.task['functional_failures'], 0)
        self.assertEqual(self.task['status'], 'pending')

    def test_cancellation_preserves_pending_without_availability_or_technical_failure(self):
        with patch.object(run, 'run_process', return_value=(130, '', '')):
            with self.assertRaises(KeyboardInterrupt): self.execute()
        self.assertEqual(self.task['status'], 'pending')
        self.assertEqual(self.task['functional_failures'], 0)
        self.assertEqual(av.read(self.plan, self.task['id'])['events'], [])

    def test_bad_arguments_block_for_repair_without_model_rotation(self):
        with patch.object(run, 'run_process', return_value=(2, '', 'unknown option --effort')) as proc:
            self.assertFalse(self.execute())
        self.assertEqual(proc.call_count, 1)
        self.assertEqual(self.task['status'], 'blocked')
        self.assertEqual(self.task['failure_classes'], ['plan_defect'])

    def test_dispatch_budget_and_technical_provider_rotation(self):
        self.prepare_processes()
        self.config['availability']['max_attempts_per_run'] = 1
        with self.assertRaises(av.AvailabilityPaused): self.execute()
        self.assertEqual(self.task['attempts'], 1)
        self.task['functional_failures'] = 4
        self.task['failure_classes'] = ['mechanical'] * 4
        route = self.select(now=10**11)
        self.assertEqual(route['provider'], 'codex')


if __name__ == '__main__':
    unittest.main()
