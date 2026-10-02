#!/usr/bin/env python3
"""Offline tests for the plan-local MODEL_MATRIX snapshot, refresh, diff and reclassify."""
from __future__ import annotations
import contextlib
import copy
import io
import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock
import model_catalog as mc
import model_catalogctl as mcc
import planctl

SCRIPTS = Path(__file__).resolve().parent
SPEC = SCRIPTS.parent / 'references' / 'plan-spec.example.json'
NOW = datetime(2026, 10, 1, 12, 0, tzinfo=timezone.utc)
TASK_FIELDS = ('model_tier', 'reasoning_effort', 'provider', 'status', 'complexity')


class Clock:
    def __init__(self, moment=NOW):
        self.moment = moment

    def __call__(self):
        return self.moment


class MatrixTests(unittest.TestCase):
    def setUp(self):
        # Short temp paths: LongPathsEnabled may be 0 on Windows hosts.
        self.tmp = Path(tempfile.mkdtemp(prefix='mm'))
        self.cache = self.tmp / 'c'
        env = mock.patch.dict(os.environ, {mcc.ENV_CACHE_DIR: str(self.cache)})
        env.start()
        self.addCleanup(env.stop)
        self.addCleanup(lambda: __import__('shutil').rmtree(self.tmp, ignore_errors=True))
        self.clock = Clock()
        self.store = mcc.CatalogStore(self.cache, now=self.clock)
        spec = json.loads(SPEC.read_text(encoding='utf-8'))
        repo = self.tmp / 'r'
        repo.mkdir()
        with self.clocked(self.clock):
            self.plan = planctl.create_plan(repo, spec, '.w', 'p')

    def clocked(self, clock):
        real = mcc.CatalogStore
        return mock.patch.object(mcc, 'CatalogStore', lambda root=None, **kw: real(root, now=clock, **kw))

    def manifest(self):
        return json.loads((self.plan / planctl.MANIFEST).read_text(encoding='utf-8'))

    def task_fields(self):
        return {t['id']: {k: t[k] for k in TASK_FIELDS} for t in self.manifest()['tasks']}

    def change_catalog(self):
        # A cached claude record moves haiku up to standard: tier mapping and digest change.
        record = mcc.bootstrap_record('claude', self.clock())
        record['models']['haiku']['tiers'] = ['economy', 'standard']
        record['models']['haiku']['quality']['rank'] = 1
        record['revision'] = 1
        record['catalog_version'] = 'claude-r1-test'
        self.store.write('claude', record)

    def set_status(self, task_id, status):
        plan_dir, manifest = planctl.load_plan(self.plan)
        planctl.find_task(manifest, task_id)['status'] = status
        planctl.save_manifest(plan_dir, manifest)

    # S001
    def test_created_at_plan_creation_with_digests(self):
        matrix, warning = mcc.load_matrix(self.plan)
        self.assertIsNone(warning)
        self.assertEqual(matrix['catalog_digest'], mc.digest(matrix['catalog']))
        self.assertEqual(matrix['matrix_digest'], mcc._matrix_digest(matrix))
        self.assertEqual(matrix['captured_at'], '2026-10-01T12:00:00Z')
        self.assertEqual([e['op'] for e in matrix['audit']], ['create'])
        self.assertEqual(sorted(matrix['tasks']), [t['id'] for t in self.manifest()['tasks']])
        md = (self.plan / mcc.MATRIX_MD).read_text(encoding='utf-8')
        self.assertIn(matrix['catalog_digest'], md)
        self.assertIn('## Tier matrix', md)
        events = [e['type'] for e in self.manifest()['events']]
        self.assertIn('model_matrix_created', events)
        self.assertEqual(planctl.validate_plan(self.plan), [])
        # Concrete model ids live only in the snapshot, never in manifest task fields (PAT001).
        for task in self.manifest()['tasks']:
            self.assertNotIn('model', task)
        # Economy floor: claude haiku; providers with an empty tier skip upward, never down.
        binding = matrix['tasks'][self.manifest()['tasks'][0]['id']]
        self.assertIn({'provider': 'claude', 'tier': 'economy', 'model': 'haiku'}, binding['candidates'])

    def test_skip_upward_never_downgrades(self):
        table = mcc._tier_table(mc.bootstrap_catalog())
        binding = mcc._bind_task({'model_tier': 'advanced', 'provider': 'claude'}, table, 'd', 'now')
        self.assertEqual(binding['candidates'], [{'provider': 'claude', 'tier': 'strong', 'model': 'claude-opus-5-5'}])
        binding = mcc._bind_task({'model_tier': 'max', 'provider': 'qwen'}, table, 'd', 'now')
        self.assertEqual(binding['candidates'], [])

    def test_crash_during_write_keeps_previous_snapshot(self):
        before = (self.plan / mcc.MATRIX_JSON).read_bytes()
        self.change_catalog()
        with mock.patch.object(mcc.os, 'replace', side_effect=OSError('simulated crash')):
            with self.assertRaises(OSError):
                mcc.matrix_refresh(self.store, self.plan)
        self.assertEqual((self.plan / mcc.MATRIX_JSON).read_bytes(), before)
        self.assertIsNone(mcc.load_matrix(self.plan)[1])
        self.assertEqual([p.name for p in self.plan.iterdir() if p.name.endswith('.tmp')], [])

    def test_plan_without_snapshot_stays_valid_and_is_not_backfilled(self):
        (self.plan / mcc.MATRIX_JSON).unlink()
        (self.plan / mcc.MATRIX_MD).unlink()
        self.assertEqual(planctl.validate_plan(self.plan), [])
        report = mcc.matrix_status(self.store, self.plan)
        self.assertFalse(report['snapshot'])
        mcc.matrix_diff(self.store, self.plan)
        self.assertFalse((self.plan / mcc.MATRIX_JSON).exists())
        result = mcc.matrix_refresh(self.store, self.plan)
        self.assertIsNone(result['old_digest'])
        self.assertTrue((self.plan / mcc.MATRIX_JSON).exists())

    def test_creation_failure_is_recorded_not_fatal(self):
        spec = json.loads(SPEC.read_text(encoding='utf-8'))
        repo = self.tmp / 'r2'
        repo.mkdir()
        with mock.patch.object(mcc, 'create_plan_matrix', side_effect=RuntimeError('boom')):
            plan = planctl.create_plan(repo, spec, '.w', 'q')
        self.assertFalse((plan / mcc.MATRIX_JSON).exists())
        manifest = json.loads((plan / planctl.MANIFEST).read_text(encoding='utf-8'))
        self.assertIn('model_matrix_skipped', [e['type'] for e in manifest['events']])

    # S002
    def test_refresh_rebases_pending_only_with_audit_and_identical_task_fields(self):
        ids = [t['id'] for t in self.manifest()['tasks']]
        self.set_status(ids[0], 'in_progress')
        before_tasks = json.dumps(self.manifest()['tasks'], sort_keys=True)
        old = mcc.load_matrix(self.plan)[0]
        self.change_catalog()
        self.clock.moment = NOW + timedelta(days=1)
        diff = mcc.matrix_diff(self.store, self.plan)
        self.assertTrue(diff['changed'])
        self.assertIn('standard', diff['tier_changes'])
        self.assertEqual(mcc.load_matrix(self.plan)[0], old, 'diff must not write')
        result = mcc.matrix_refresh(self.store, self.plan)
        self.assertEqual(json.dumps(self.manifest()['tasks'], sort_keys=True), before_tasks)
        new = mcc.load_matrix(self.plan)[0]
        self.assertNotEqual(new['catalog_digest'], old['catalog_digest'])
        self.assertEqual(new['audit'][:-1], old['audit'])
        self.assertEqual(new['audit'][-1]['op'], 'refresh')
        self.assertEqual((new['audit'][-1]['old_digest'], new['audit'][-1]['new_digest']),
                         (old['catalog_digest'], new['catalog_digest']))
        self.assertEqual(result['kept'], [ids[0]])
        self.assertEqual(result['rebased'], ids[1:])
        self.assertEqual(new['tasks'][ids[0]], old['tasks'][ids[0]])
        for task_id in ids[1:]:
            self.assertEqual(new['tasks'][task_id]['catalog_digest'], new['catalog_digest'])
        self.assertIn(old['catalog_digest'][:12], (self.plan / mcc.MATRIX_MD).read_text(encoding='utf-8'))

    def test_refresh_never_changes_floor(self):
        floors = {k: v['floor'] for k, v in mcc.load_matrix(self.plan)[0]['tasks'].items()}
        fields = self.task_fields()
        self.change_catalog()
        mcc.matrix_refresh(self.store, self.plan)
        self.assertEqual({k: v['floor'] for k, v in mcc.load_matrix(self.plan)[0]['tasks'].items()}, floors)
        self.assertEqual(self.task_fields(), fields)

    def test_stale_status_warns_and_exits_zero(self):
        fresh = mcc.matrix_status(self.store, self.plan)
        self.assertFalse(fresh['stale'])
        self.assertEqual(fresh['warnings'], [])
        out = io.StringIO()
        with self.clocked(Clock(NOW + timedelta(days=30))), contextlib.redirect_stdout(out):
            code = mcc.main(['status', '--plan', str(self.plan), '--cache-dir', str(self.cache)])
        self.assertEqual(code, 0)
        self.assertIn('warning:', out.getvalue())
        self.assertIn('days old', out.getvalue())

    def test_tampered_snapshot_is_reported(self):
        path = self.plan / mcc.MATRIX_JSON
        data = json.loads(path.read_text(encoding='utf-8'))
        data['tasks'][next(iter(data['tasks']))]['floor'] = 'max'
        path.write_text(json.dumps(data), encoding='utf-8')
        self.assertIn('digest mismatch', mcc.load_matrix(self.plan)[1])
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(mcc.main(['status', '--plan', str(self.plan), '--cache-dir', str(self.cache), '--json']), 0)

    def test_cli_refresh_and_diff(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(mcc.main(['diff', '--plan', str(self.plan), '--cache-dir', str(self.cache)]), 0)
            self.assertEqual(mcc.main(['refresh', '--plan', str(self.plan), '--cache-dir', str(self.cache)]), 0)
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            mcc.main(['refresh', '--cache-dir', str(self.cache)])

    # S003
    def test_reclassify_is_explicit_and_audited(self):
        ids = [t['id'] for t in self.manifest()['tasks']]
        old = mcc.load_matrix(self.plan)[0]
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = mcc.main(['reclassify', '--plan', str(self.plan), '--task', ids[1], '--tier', 'L4',
                             '--reason', 'harder than planned', '--cache-dir', str(self.cache)])
        self.assertEqual(code, 0)
        task = planctl.find_task(self.manifest(), ids[1])
        self.assertEqual(task['model_tier'], 'strong')
        self.assertIn('task_reclassified', [e['type'] for e in self.manifest()['events']])
        new = mcc.load_matrix(self.plan)[0]
        entry = new['audit'][-1]
        self.assertEqual((entry['op'], entry['task'], entry['old_floor'], entry['new_floor']),
                         ('reclassify', ids[1], 'economy', 'strong'))
        self.assertEqual(entry['old_digest'], entry['new_digest'])
        self.assertEqual(new['tasks'][ids[1]]['floor'], 'strong')
        self.assertEqual(new['tasks'][ids[0]], old['tasks'][ids[0]])
        # A later refresh keeps the reclassified floor.
        self.change_catalog()
        mcc.matrix_refresh(self.store, self.plan)
        self.assertEqual(mcc.load_matrix(self.plan)[0]['tasks'][ids[1]]['floor'], 'strong')

    def test_reclassify_rejects_running_tasks_and_missing_reason(self):
        ids = [t['id'] for t in self.manifest()['tasks']]
        self.set_status(ids[0], 'in_progress')
        before = (self.plan / mcc.MATRIX_JSON).read_bytes()
        with self.assertRaises(mcc.MatrixError):
            mcc.matrix_reclassify(self.store, self.plan, ids[0], 'strong', 'why')
        with self.assertRaises(mcc.MatrixError):
            mcc.matrix_reclassify(self.store, self.plan, ids[1], 'strong', '  ')
        self.assertEqual((self.plan / mcc.MATRIX_JSON).read_bytes(), before)

    def test_snapshot_has_no_secret_values(self):
        with mock.patch.dict(os.environ, {'ZAI_API_KEY': 'sk-secret-value-123'}):
            mcc.matrix_refresh(self.store, self.plan)
        for name in (mcc.MATRIX_JSON, mcc.MATRIX_MD):
            self.assertNotIn('sk-secret-value-123', (self.plan / name).read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main(verbosity=1)
