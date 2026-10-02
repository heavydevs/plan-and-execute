#!/usr/bin/env python3
"""Offline model catalog contract tests: schema, freshness policy, digest, bootstrap."""
from __future__ import annotations
import copy
import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
import model_catalog as mc

DOC = Path(__file__).resolve().parents[1] / 'references' / 'MODEL_CATALOG.md'


def reorder(value):
    if isinstance(value, dict):
        return {key: reorder(value[key]) for key in reversed(list(value))}
    if isinstance(value, list):
        return [reorder(item) for item in value]
    return value


class ModelCatalogTests(unittest.TestCase):
    def setUp(self):
        self.catalog = copy.deepcopy(mc.BOOTSTRAP_CATALOG)
        self.entry = self.catalog['providers']['claude']['models']['claude-opus-5-5']

    def assertRejected(self, path_fragment):
        with self.assertRaises(mc.CatalogError) as ctx:
            mc.validate(self.catalog)
        paths = [path for path, _ in ctx.exception.errors]
        self.assertTrue(any(path_fragment in path for path in paths), paths)
        return paths

    def test_bootstrap_validates_and_covers_both_providers(self):
        catalog = mc.bootstrap_catalog()
        self.assertEqual(set(catalog['providers']), {'claude', 'codex', 'muse', 'glm', 'deepseek'})
        def tiers_of(name):
            return {tier for entry in catalog['providers'][name]['models'].values() for tier in entry['tiers']}
        for name in ('claude', 'codex'):
            self.assertNotIn('advanced', tiers_of(name))
        self.assertEqual(tiers_of('claude') | tiers_of('codex'), {'economy', 'standard', 'strong', 'max'})
        self.assertEqual(tiers_of('muse'), {'advanced'})

    def test_round_trip_and_key_order_keep_digest(self):
        first = mc.digest(self.catalog)
        self.assertEqual(first, mc.digest(json.loads(json.dumps(self.catalog))))
        self.assertEqual(first, mc.digest(reorder(self.catalog)))
        self.assertEqual(first, mc.digest(mc.bootstrap_catalog()))
        self.assertRegex(first, r'^[0-9a-f]{64}$')

    def test_mapping_change_changes_digest(self):
        before = mc.digest(self.catalog)
        self.entry['tiers'] = ['max']
        self.assertNotEqual(before, mc.digest(self.catalog))

    def test_rejects_unknown_capability_with_path(self):
        self.entry['capability']['capabilities'].append('telepathy')
        self.assertRejected('$.providers.claude.models.claude-opus-5-5.capability.capabilities[4]')

    def test_rejects_negative_price_with_path(self):
        self.entry['economics']['input_per_mtok'] = -1
        self.assertRejected('$.providers.claude.models.claude-opus-5-5.economics.input_per_mtok')

    def test_rejects_missing_or_unknown_evidence_source(self):
        del self.entry['quality']['evidence']['source']
        self.assertRejected('claude-opus-5-5.quality.evidence.source')
        self.entry['quality']['evidence']['source'] = 'rumor'
        self.assertRejected('claude-opus-5-5.quality.evidence.source')

    def test_rejects_non_canonical_tiers(self):
        for tier in ('F3', 'l2', 'Strong', 'premium'):
            self.entry['tiers'] = [tier]
            self.assertRejected('claude-opus-5-5.tiers[0]')

    def test_rejects_unknown_fields_bad_timestamps_and_versions(self):
        self.entry['capability']['observed_at'] = '2026-09-30'
        self.entry['economics']['surge'] = 2
        self.catalog['schema_version'] = 99
        paths = self.assertRejected('capability.observed_at')
        self.assertIn('$.providers.claude.models.claude-opus-5-5.economics.surge', paths)
        self.assertIn('$.schema_version', paths)

    def test_defaults_are_pinned(self):
        self.assertEqual(mc.DEFAULT_FRESHNESS, {
            'capability': {'ttl_days': 7, 'grace_days': 3, 'warn_after_days': 5},
            'economics': {'ttl_days': 30, 'grace_days': 7, 'warn_after_days': 21},
            'quality': {'ttl_days': 30, 'grace_days': 14, 'warn_after_days': 21},
        })
        self.assertEqual(mc.FRESHNESS_POLICY_VERSION, '2026-10-01-v1')

    def test_freshness_states(self):
        observed = datetime(2026, 9, 30, tzinfo=timezone.utc)
        stamp = '2026-09-30T00:00:00Z'
        at = lambda days: observed + timedelta(days=days)
        self.assertEqual(mc.facet_freshness(stamp, 'capability', at(1)), 'fresh')
        self.assertEqual(mc.facet_freshness(stamp, 'capability', at(6)), 'warning')
        self.assertEqual(mc.facet_freshness(stamp, 'capability', at(9)), 'stale')
        self.assertEqual(mc.facet_freshness(stamp, 'capability', at(11)), 'expired')
        self.assertEqual(mc.facet_freshness(stamp, 'economics', at(9)), 'fresh')
        report = mc.catalog_freshness(self.catalog, now=at(9))
        self.assertEqual(report['codex']['gpt-6-astra'], {'capability': 'stale', 'economics': 'fresh', 'quality': 'fresh'})

    def test_override_merges_and_rejects_bad_values(self):
        policy = mc.freshness_policy({'capability': {'grace_days': 10}})
        self.assertEqual(policy['capability'], {'ttl_days': 7, 'grace_days': 10, 'warn_after_days': 5})
        self.assertEqual(policy['economics'], mc.DEFAULT_FRESHNESS['economics'])
        stamp = '2026-09-30T00:00:00Z'
        later = datetime(2026, 10, 11, tzinfo=timezone.utc)
        self.assertEqual(mc.facet_freshness(stamp, 'capability', later, policy), 'stale')
        for bad, path in (({'speed': {}}, 'freshness.speed'), ({'quality': {'ttl_days': -1}}, 'freshness.quality.ttl_days'),
                          ({'quality': {'warn_after_days': 99}}, 'freshness.quality.warn_after_days')):
            with self.assertRaises(mc.CatalogError) as ctx:
                mc.freshness_policy(bad)
            self.assertIn(path, [p for p, _ in ctx.exception.errors])

    def test_reference_documents_schema_and_defaults(self):
        text = DOC.read_text(encoding='utf-8')
        for token in ('schema_version', 'catalog_version', 'observed_at', 'evidence', mc.FRESHNESS_POLICY_VERSION,
                      *mc.CAPABILITY_NAMES, *mc.EVIDENCE_SOURCES):
            self.assertIn(token, text)
        for facet, rules in mc.DEFAULT_FRESHNESS.items():
            self.assertIn(f"| {facet} | {rules['ttl_days']} | {rules['grace_days']} | {rules['warn_after_days']} |", text)


if __name__ == '__main__':
    unittest.main()
