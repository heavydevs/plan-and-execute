#!/usr/bin/env python3
"""Offline tests for the shared model catalog cache and provider-scoped refresh controller."""
from __future__ import annotations
import contextlib
import copy
import io
import json
import os
import shutil
import tempfile
import threading
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock
import model_catalog as mc
import model_catalogctl as mcc

SCRIPTS = Path(__file__).resolve().parent
DOC = SCRIPTS.parent / 'references' / 'MODEL_CATALOG.md'
NOW = datetime(2026, 10, 1, 12, 0, tzinfo=timezone.utc)


class Clock:
    def __init__(self, moment=NOW):
        self.moment = moment

    def __call__(self):
        return self.moment


class Counting:
    """Injectable source that counts calls and can fail or stall on demand."""

    def __init__(self, payload, fail=False, delay=0.0):
        self.payload, self.fail, self.delay, self.calls = payload, fail, delay, []

    def __call__(self, provider):
        self.calls.append(provider)
        if self.delay:
            time.sleep(self.delay)
        if self.fail:
            raise ConnectionError('listing unavailable')
        return copy.deepcopy(self.payload)


def provider_sources(provider, fail=False, delay=0.0):
    models = mc.bootstrap_catalog()['providers'][provider]['models']
    evidence = {'source': 'provider_cli', 'ref': 'test listing'}
    capability = {m: {'tiers': e['tiers'], 'capability': {**e['capability'], 'evidence': evidence}} for m, e in models.items()}
    for item in capability.values():
        item['capability'].pop('observed_at')
    economics = {m: {'currency': 'USD', 'input_per_mtok': 1.0, 'output_per_mtok': 2.0, 'evidence': evidence} for m in models}
    quality = {m: {'rank': e['quality']['rank'], 'score': None, 'evidence': evidence} for m, e in models.items()}
    return {'capability': Counting(capability, fail, delay), 'economics': Counting(economics, fail),
            'quality': Counting(quality, fail)}


class CatalogCtlTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='mcc'))
        self.clock = Clock()
        self.store = mcc.CatalogStore(self.tmp, now=self.clock, lock_timeout=2.0)
        self.version = lambda _p: '1.0.0'

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def seed(self, provider):
        result = mcc.refresh(self.store, provider, provider_sources(provider), version_fn=self.version)
        self.assertEqual(result['origin'], 'refreshed', result)
        return result

    # S001 — store, atomic writes and lock
    def test_default_cache_root_is_user_cache_outside_skill_tree(self):
        win = mcc.default_cache_root({'LOCALAPPDATA': r'C:\Users\u\AppData\Local'}, 'win32')
        self.assertEqual(win.parts[-2:], ('plan-and-execute', 'model-catalog'))
        self.assertIn('AppData', str(win))
        posix = mcc.default_cache_root({'XDG_CACHE_HOME': '/home/u/.cache'}, 'linux')
        self.assertEqual(posix, Path('/home/u/.cache/plan-and-execute/model-catalog'))
        self.assertEqual(mcc.default_cache_root({mcc.ENV_CACHE_DIR: str(self.tmp)}), self.tmp)
        real = mcc.default_cache_root().resolve()
        self.assertNotIn(SCRIPTS.parent.resolve(), [real, *real.parents])

    def test_rejects_path_like_provider_ids(self):
        for bad in ('../x', 'Claude', '', 'a/b'):
            with self.assertRaises(mcc.CacheError):
                self.store.path(bad)

    def test_refresh_of_one_provider_leaves_other_provider_bytes_unchanged(self):
        self.seed('claude')
        self.seed('codex')
        codex = self.store.path('codex')
        before, mtime = codex.read_bytes(), codex.stat().st_mtime_ns
        result = mcc.refresh(self.store, 'claude', provider_sources('claude'), version_fn=self.version, force=True)
        self.assertEqual(result['origin'], 'refreshed')
        self.assertEqual(codex.read_bytes(), before)
        self.assertEqual(codex.stat().st_mtime_ns, mtime)

    def test_crash_mid_write_keeps_previous_valid_catalog(self):
        self.seed('claude')
        path = self.store.path('claude')
        before = path.read_bytes()
        with mock.patch.object(mcc.os, 'replace', side_effect=OSError('power loss')):
            with self.assertRaises(OSError):
                mcc.refresh(self.store, 'claude', provider_sources('claude'), version_fn=self.version, force=True)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual([p.name for p in path.parent.iterdir() if p.name.endswith('.tmp')], [])
        self.assertFalse(path.with_name(mcc.LOCK_FILE).exists())
        record, warning = self.store.load('claude')
        self.assertIsNone(warning)
        self.assertEqual(record['provider'], 'claude')

    def test_orphan_temp_and_corrupt_cache_fall_back_safely(self):
        self.seed('claude')
        path = self.store.path('claude')
        (path.parent / '.catalog.json.orphan.tmp').write_text('{"half', encoding='utf-8')
        self.assertIsNotNone(self.store.load('claude')[0])
        path.write_text('{"cache_version": 1, "provi', encoding='utf-8')
        record, origin, warnings = mcc.effective_record(self.store, 'claude')
        self.assertEqual(origin, 'bootstrap')
        self.assertTrue(any('cache invalid' in w for w in warnings), warnings)
        self.assertEqual(record['models'], mc.bootstrap_catalog()['providers']['claude']['models'])
        self.assertFalse(mcc.validate_cache(self.store, 'claude')['valid'])

    def test_concurrent_refreshes_serialize_on_provider_lock(self):
        sources = provider_sources('claude', delay=0.2)
        results, errors = [], []

        def run():
            try:
                results.append(mcc.refresh(self.store, 'claude', sources, version_fn=self.version))
            except Exception as exc:  # pragma: no cover - surfaced below
                errors.append(exc)
        threads = [threading.Thread(target=run) for _ in range(3)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(errors, [])
        self.assertEqual(len(sources['capability'].calls), 1)
        self.assertEqual(sorted(r['origin'] for r in results), ['cache', 'cache', 'refreshed'])
        self.assertIsNone(self.store.load('claude')[1])

    def test_lock_timeout_and_stale_lock_recovery(self):
        store = mcc.CatalogStore(self.tmp, now=self.clock, lock_timeout=0.1, stale_lock_seconds=60)
        lock = store.path('claude').with_name(mcc.LOCK_FILE)
        lock.parent.mkdir(parents=True)
        lock.write_text('{}', encoding='utf-8')
        with self.assertRaises(mcc.LockTimeout):
            mcc.refresh(store, 'claude', provider_sources('claude'), version_fn=self.version)
        old = time.time() - 600
        os.utime(lock, (old, old))
        self.assertEqual(mcc.refresh(store, 'claude', provider_sources('claude'), version_fn=self.version)['origin'], 'refreshed')
        self.assertFalse(lock.exists())

    # S002 — refresh decisions
    def test_fresh_cache_makes_zero_source_calls(self):
        self.seed('claude')
        sources = provider_sources('claude')
        self.clock.moment = NOW + timedelta(days=1)
        result = mcc.refresh(self.store, 'claude', sources, version_fn=self.version)
        self.assertEqual(result['source_calls'], [])
        self.assertEqual(sum(len(s.calls) for s in sources.values()), 0)

    def test_one_expired_facet_calls_only_that_source(self):
        self.seed('claude')
        sources = provider_sources('claude')
        self.clock.moment = NOW + timedelta(days=8)  # capability ttl 7; economics/quality ttl 30
        result = mcc.refresh(self.store, 'claude', sources, version_fn=self.version)
        self.assertEqual(result['source_calls'], ['capability'])
        self.assertEqual((len(sources['capability'].calls), len(sources['economics'].calls), len(sources['quality'].calls)), (1, 0, 0))
        self.assertEqual(mcc.plan_refresh(self.store.load('claude')[0], self.clock.moment, self.store.policy, '1.0.0'), {})

    def test_cli_version_change_invalidates_only_capability(self):
        self.seed('claude')
        sources = provider_sources('claude')
        result = mcc.refresh(self.store, 'claude', sources, version_fn=lambda _p: '2.0.0')
        self.assertEqual(result['due'], {'capability': 'cli_version_changed'})
        self.assertEqual(result['source_calls'], ['capability'])
        self.assertEqual(self.store.load('claude')[0]['cli_version'], '2.0.0')

    def test_failing_source_returns_last_valid_with_nonblocking_stale_warning(self):
        self.seed('claude')
        before = self.store.path('claude').read_bytes()
        self.clock.moment = NOW + timedelta(days=60)
        result = mcc.refresh(self.store, 'claude', provider_sources('claude', fail=True), version_fn=self.version)
        self.assertEqual(result['origin'], 'cache')
        self.assertFalse(result['blocking'])
        self.assertTrue(any('stale' in w for w in result['warnings']), result['warnings'])
        self.assertEqual(self.store.path('claude').read_bytes(), before)
        report = mcc.status(self.store, 'claude')
        self.assertFalse(report['blocking'])
        self.assertEqual(report['providers']['claude']['origin'], 'cache')
        self.assertTrue(any('stale facets' in w for w in report['warnings']), report['warnings'])

    def test_failing_source_without_cache_uses_bootstrap_and_writes_nothing(self):
        result = mcc.refresh(self.store, 'codex', provider_sources('codex', fail=True), version_fn=self.version)
        self.assertEqual(result['origin'], 'bootstrap')
        self.assertFalse(result['blocking'])
        self.assertFalse(self.store.path('codex').exists())
        catalog, _ = mcc.merged_catalog(self.store, 'codex')
        self.assertEqual(catalog['providers']['codex'], mc.bootstrap_catalog()['providers']['codex'])

    def test_unknown_provider_without_cache_yields_no_candidate(self):
        result = mcc.refresh(self.store, 'gemini', {}, version_fn=self.version)
        self.assertEqual(result['origin'], 'none')
        catalog, _ = mcc.merged_catalog(self.store, 'gemini')
        self.assertEqual(catalog['providers'], {})

    def test_invalid_source_data_is_rejected_and_mapping_change_bumps_version(self):
        self.seed('claude')
        bad = provider_sources('claude')
        bad['capability'].payload['haiku']['tiers'] = ['F1']
        result = mcc.refresh(self.store, 'claude', bad, version_fn=self.version, force=True)
        self.assertTrue(any('invalid data' in w for w in result['warnings']))
        self.assertEqual(self.store.load('claude')[0]['models']['haiku']['tiers'], ['economy'])
        first = self.store.load('claude')[0]
        changed = provider_sources('claude')
        changed['capability'].payload['claude-sonnet-5-5']['tiers'] = ['standard', 'advanced']
        mcc.refresh(self.store, 'claude', changed, version_fn=self.version, force=True)
        second = self.store.load('claude')[0]
        self.assertEqual(second['revision'], first['revision'] + 1)
        self.assertNotEqual(second['catalog_version'], first['catalog_version'])
        self.assertTrue(second['provenance'][-1]['mapping_changed'])

    def test_new_model_gets_unknown_placeholders_not_invented_values(self):
        self.seed('claude')
        sources = provider_sources('claude')
        sources['capability'].payload['claude-new'] = copy.deepcopy(sources['capability'].payload['haiku'])
        del sources['economics'], sources['quality']
        mcc.refresh(self.store, 'claude', sources, version_fn=self.version, force=True)
        entry = self.store.load('claude')[0]['models']['claude-new']
        self.assertIsNone(entry['economics']['input_per_mtok'])
        self.assertIsNone(entry['quality']['rank'])
        self.assertEqual(entry['economics']['observed_at'], mcc.EPOCH)

    # S003 — controller commands
    def run_cli(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = mcc.main([*args, '--cache-dir', str(self.tmp)])
        return code, out.getvalue()

    def test_cli_commands_with_json(self):
        evidence = self.tmp / 'evidence.json'
        evidence.write_text(json.dumps({'models': mc.bootstrap_catalog()['providers']['claude']['models']}), encoding='utf-8')
        code, out = self.run_cli('refresh', '--provider', 'claude', '--from-file', str(evidence), '--cli-version', '9.9', '--json')
        self.assertEqual(code, 0, out)
        self.assertEqual(json.loads(out)['provider'], 'claude')
        code, out = self.run_cli('status', '--json')
        self.assertEqual(code, 0)
        report = json.loads(out)
        self.assertEqual(report['providers']['claude']['origin'], 'cache')
        self.assertEqual(report['providers']['codex']['origin'], 'bootstrap')
        code, out = self.run_cli('show', '--json')
        shown = json.loads(out)
        self.assertEqual(shown['digest'], mc.digest(shown['catalog']))
        self.assertEqual(self.run_cli('validate', '--json')[0], 0)
        target = self.tmp / 'snap.json'
        code, out = self.run_cli('snapshot', '--output', str(target), '--json')
        snap = json.loads(target.read_text(encoding='utf-8'))
        self.assertEqual(snap['digest'], mc.digest(snap['catalog']))
        self.assertEqual(json.loads(out)['digest'], snap['digest'])
        self.store.path('claude').write_text('nope', encoding='utf-8')
        self.assertEqual(self.run_cli('validate', '--json')[0], 1)

    def test_cli_refresh_without_source_is_nonblocking(self):
        code, out = self.run_cli('refresh', '--provider', 'codex', '--cli-version', '1', '--json')
        self.assertEqual(code, 0)
        result = json.loads(out)
        self.assertEqual(result['origin'], 'bootstrap')
        self.assertTrue(any('no capability source' in w for w in result['warnings']))

    def test_doc_describes_cache_and_commands(self):
        text = DOC.read_text(encoding='utf-8')
        for needle in ('model_catalogctl.py', mcc.ENV_CACHE_DIR, 'cli_version_changed', 'status', 'snapshot', 'bootstrap'):
            self.assertIn(needle, text)


if __name__ == '__main__':
    unittest.main(verbosity=1)
