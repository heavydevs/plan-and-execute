#!/usr/bin/env python3
"""Runner route resolution from the plan MODEL_MATRIX snapshot (offline, no provider CLIs)."""
from __future__ import annotations
import argparse
import contextlib
import copy
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

import model_catalog as mc
import model_catalogctl as mcc
import planctl
import routing_config as cfg
import run_isolated as run
from self_test import sample_spec

SNAPSHOT = {'model_resolution': 'snapshot'}
ABSENT = 'kimi'  # a runner provider the bootstrap catalog does not cover


class SnapshotRunnerTests(unittest.TestCase):
    def setUp(self):
        # Short temp paths: LongPathsEnabled may be 0 on Windows hosts.
        self.tmp = Path(tempfile.mkdtemp(prefix='sr'))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.cache = self.tmp / 'c'
        env = mock.patch.dict(os.environ, {mcc.ENV_CACHE_DIR: str(self.cache)})
        env.start()
        self.addCleanup(env.stop)
        self.store = mcc.CatalogStore(self.cache)
        repo = self.tmp / 'r'
        repo.mkdir()
        spec = sample_spec()
        for task in spec['tasks']:
            task['model_tier'], task['provider'] = 'standard', 'auto'
        self.plan = planctl.create_plan(repo, spec, '.w', 'p')
        _, self.manifest = planctl.load_plan(self.plan)
        self.config = cfg.merge(planctl.default_config(), cfg.EXTRA_DEFAULTS)
        for provider in cfg.PROVIDERS:
            self.config[provider]['command'] = [sys.executable]
        self.config['stream_provider_output'] = False

    def task(self, task_id=None):
        _, manifest = planctl.load_plan(self.plan)
        return manifest['tasks'][0] if task_id is None else planctl.find_task(manifest, task_id)

    def ladder(self, task, config=None):
        return run.choose_route(task, config or self.config, None, check_availability=False)

    def change_catalog(self):
        record = mcc.bootstrap_record('claude', self.store.now())
        record['models']['haiku']['tiers'] = ['economy', 'standard']
        record['models']['haiku']['quality']['rank'] = 1
        record['revision'], record['catalog_version'] = 1, 'claude-r1-test'
        self.store.write('claude', record)

    def write_absent_provider(self, observed):
        record = mcc.bootstrap_record('claude', observed)
        record['provider'], record['catalog_version'] = ABSENT, 'kimi-test'
        for entry in record['models'].values():
            for facet in mc.FACETS:
                entry[facet]['observed_at'] = mcc._iso(observed)
        self.store.write(ABSENT, record)

    # S001
    def test_default_config_matches_pre_plan_ladder(self):
        task = self.task()
        variants = [{}, {'functional_failures': 1, 'failure_classes': ['semantic']},
                    {'functional_failures': 4, 'failure_classes': ['unknown'] * 4},
                    {'model_tier': 'economy', 'reasoning_effort': 'low'}, {'model_tier': 'max'}]
        self.change_catalog()
        mcc.matrix_refresh(self.store, self.plan)
        for extra in variants:
            probe = {**task, **extra}
            before = self.ladder(probe)
            after = run.resolve_snapshot_route(self.plan, probe, dict(before), self.config)
            self.assertEqual(after, before, extra)
            self.assertEqual(run.resume_provider_models(self.plan, self.config, ABSENT), {})
        matrix, _ = mcc.load_matrix(self.plan)
        self.assertNotIn('resume_provider', [e['op'] for e in matrix['audit']])

    def test_snapshot_binds_model_and_falls_back_to_ladder(self):
        config = {**self.config, **SNAPSHOT}
        task = self.task()
        route = self.ladder(task, config)
        resolved = run.resolve_snapshot_route(self.plan, task, route, config)
        matrix, _ = mcc.load_matrix(self.plan)
        self.assertEqual(resolved['model'], matrix['tiers'][route['tier']][route['provider']])
        self.assertEqual({k: v for k, v in resolved.items() if k != 'model'}, {k: v for k, v in route.items() if k != 'model'})
        (self.plan / mcc.MATRIX_JSON).unlink()
        self.assertEqual(run.resolve_snapshot_route(self.plan, task, route, config), route)

    def test_refresh_rebases_pending_and_keeps_in_progress_route(self):
        config = {**self.config, **SNAPSHOT}
        first, second = (t['id'] for t in self.manifest['tasks'][:2])
        route = {'provider': 'claude', 'tier': 'standard', 'model': 'cfg', 'effort': 'medium', 'requested_effort': 'medium'}
        old = run.resolve_snapshot_route(self.plan, self.task(second), route, config)['model']
        plan_dir, manifest = planctl.load_plan(self.plan)
        planctl.find_task(manifest, second)['status'] = 'in_progress'
        planctl.save_manifest(plan_dir, manifest)
        self.change_catalog()
        change = mcc.matrix_refresh(self.store, self.plan)
        self.assertIn(first, change['rebased'])
        self.assertIn(second, change['kept'])
        self.assertEqual(run.resolve_snapshot_route(self.plan, self.task(first), route, config)['model'], 'haiku')
        self.assertEqual(run.resolve_snapshot_route(self.plan, self.task(second), route, config)['model'], old)
        self.assertNotEqual(old, 'haiku')

    def test_worker_prompt_excludes_matrix_and_pricing(self):
        config = {**self.config, **SNAPSHOT}
        task = self.task()
        route = run.resolve_snapshot_route(self.plan, task, self.ladder(task, config), config)
        prompt = run.worker_prompt(self.plan, self.manifest, task, route)
        for needle in ('MODEL_MATRIX', 'economics', 'price', 'pricing', 'usd', 'cost'):
            self.assertNotIn(needle, prompt.lower() if needle.islower() else prompt)

    # S002
    def test_resume_provider_fresh_catalog_resolves_and_audits(self):
        config = {**self.config, **SNAPSHOT}
        self.write_absent_provider(self.store.now())
        models = run.resume_provider_models(self.plan, config, ABSENT, self.store)
        self.assertEqual(models[ABSENT]['standard'], 'claude-sonnet-5-5')
        matrix, warning = mcc.load_matrix(self.plan)
        self.assertIsNone(warning)
        entry = matrix['audit'][-1]
        self.assertEqual((entry['op'], entry['provider']), ('resume_provider', ABSENT))
        self.assertNotIn(ABSENT, matrix['catalog']['providers'])
        route = {'provider': ABSENT, 'tier': 'standard', 'model': 'cfg', 'effort': 'medium', 'requested_effort': 'medium'}
        self.assertEqual(run.resolve_snapshot_route(self.plan, self.task(), route, config, models)['model'], 'claude-sonnet-5-5')
        # A provider already in the snapshot needs no catalog lookup.
        self.assertEqual(run.resume_provider_models(self.plan, config, 'claude', self.store), {})

    def test_resume_provider_stale_or_missing_catalog_fails_with_guidance(self):
        config = {**self.config, **SNAPSHOT}
        before = (self.plan / mcc.MATRIX_JSON).read_bytes()
        manifest_before = (self.plan / planctl.MANIFEST).read_bytes()
        with self.assertRaisesRegex(run.RunnerError, r'missing.*refresh --provider kimi'):
            run.resume_provider_models(self.plan, config, ABSENT, self.store)
        self.write_absent_provider(self.store.now() - timedelta(days=400))
        with self.assertRaisesRegex(run.RunnerError, r'(stale|expired).*refresh --plan'):
            run.resume_provider_models(self.plan, config, ABSENT, self.store)
        self.assertEqual((self.plan / mcc.MATRIX_JSON).read_bytes(), before)
        self.assertEqual((self.plan / planctl.MANIFEST).read_bytes(), manifest_before)

    def test_stale_snapshot_warns_without_blocking(self):
        matrix, _ = mcc.load_matrix(self.plan)
        captured = mc._parse_time(matrix['captured_at'])
        self.assertIsNone(run.stale_snapshot_warning(self.plan, now=captured + timedelta(days=1)))
        later = captured + timedelta(days=matrix['stale_after_days'] + 5)
        self.assertIn('days old', run.stale_snapshot_warning(self.plan, now=later))
        args = argparse.Namespace(plan=self.plan, provider=None, dry_run=True, once=False, no_wait=True, no_cleanup=True)
        overlay = {'version': 2, **{p: {'command': [sys.executable]} for p in cfg.PROVIDERS}}
        (self.plan / planctl.CONFIG).write_text(json.dumps(overlay), encoding='utf-8')
        err, out = io.StringIO(), io.StringIO()
        with mock.patch.object(mcc, '_utc_now', lambda: later), contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
            self.assertEqual(run._run_plan(args), 0)
        self.assertIn('[resume] warning: MODEL_MATRIX snapshot', err.getvalue())
        self.assertIn('"route"', out.getvalue())

    # S003
    def execute_invalid_model(self, config):
        calls = []

        def fake_process(command, *args, **kwargs):
            calls.append(command)
            return 1, '', 'Error: invalid model: retired-model-id'

        seen = []

        def fake_refresh(plan_dir, provider):
            task = self.task(self.manifest['tasks'][0]['id'])
            seen.append((provider, task['status'], task['functional_failures'], list(task.get('failure_classes', []))))

        task = self.task()
        with mock.patch.object(run, 'run_process', fake_process), \
                mock.patch.object(run, 'refresh_model_snapshot', fake_refresh), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            outcome = run.execute_one_task(self.plan, self.manifest, config, task,
                                           provider_override=None, dry_run=False, no_wait=True)
        return outcome, calls, seen

    def test_invalid_model_refreshes_exactly_once_without_failure_evidence(self):
        outcome, calls, seen = self.execute_invalid_model({**self.config, **SNAPSHOT})
        self.assertFalse(outcome)
        self.assertEqual(len(calls), 2)
        self.assertEqual(len(seen), 1)
        self.assertEqual(seen[0][1:], ('pending', 0, []))
        task = self.task()
        events = [h['event'] for h in task['history']]
        self.assertIn('model_refresh', events)
        # Only the repeated rejection after the one refresh is recorded.
        self.assertEqual(task['failure_classes'], ['plan_defect'])

    def test_default_config_invalid_model_does_not_refresh(self):
        outcome, calls, seen = self.execute_invalid_model(self.config)
        self.assertFalse(outcome)
        self.assertEqual((len(calls), seen), (1, []))
        self.assertNotIn('model_refresh', [h['event'] for h in self.task()['history']])


if __name__ == '__main__':
    unittest.main(verbosity=1)
