#!/usr/bin/env python3
"""Offline routing contract tests: layering, rejection, legacy policy and dispatch."""
from __future__ import annotations
import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import planctl
import routing_config as rc
import routingctl
import run_isolated as runner


class RoutingConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.global_file = self.root / 'global.json'
        self.plan_file = self.root / 'orchestrator.config.json'
        self.write(self.global_file, {})
        self.write(self.plan_file, rc.plan_overlay())

    def write(self, path, obj):
        path.write_text(json.dumps(obj), encoding='utf-8')

    def load(self):
        return rc.load(planctl.default_config(), self.plan_file, global_config=self.global_file)

    def test_platform_paths(self):
        self.assertEqual(rc.global_path({'PAE_CONFIG_PATH': '/custom.json'}), Path('/custom.json'))
        self.assertEqual(rc.global_path({'XDG_CONFIG_HOME': '/xdg'}, home=Path('/home/me'), platform='posix'), Path('/xdg/plan-and-execute/orchestrator.config.json'))
        self.assertEqual(rc.global_path({'APPDATA': '/roaming'}, home=Path('/home/me'), platform='nt'), Path('/roaming/plan-and-execute/orchestrator.config.json'))

    def test_layers_and_partial_nested_override(self):
        global_cfg = {'version': 2, 'tier_routes': {'strong': {'primary': 'codex', 'fallbacks': ['claude', 'antigravity']}}, 'codex': {'models': {'strong': 'custom-model'}}, 'assistant': {'enabled': True}}
        self.write(self.global_file, global_cfg)
        self.write(self.plan_file, {'version': 2, 'tier_routes': {'strong': {'fallbacks': []}}, 'assistant': {'enabled': False}})
        cfg = self.load()
        self.assertEqual(cfg['codex']['models']['strong'], 'custom-model')
        self.assertEqual(cfg['tier_routes']['strong'], {'primary': 'codex', 'fallbacks': []})
        self.assertFalse(cfg['assistant']['enabled'])
        self.assertEqual(cfg['codex']['models']['economy'], planctl.default_config()['codex']['models']['economy'])
        self.assertEqual(rc.read(self.global_file), global_cfg, 'loading must not write or migrate user settings')

    def test_legacy_complete_snapshot_is_not_reinterpreted(self):
        old = planctl.default_config()
        old['codex']['models']['strong'] = 'my-pinned-model'
        self.write(self.global_file, {'version': 2, 'tier_routes': {'strong': {'primary': 'antigravity'}}, 'assistant': {'enabled': True}})
        self.write(self.plan_file, old)
        cfg = self.load()
        self.assertEqual(cfg['tier_routes'], {})
        self.assertFalse(cfg['assistant']['enabled'])
        self.assertEqual(cfg['codex']['models']['strong'], 'my-pinned-model')

    def test_independent_copies_no_catalog_rewrite(self):
        base = planctl.default_config()
        before = copy.deepcopy(base)
        cfg = rc.load(base, self.plan_file, global_config=self.global_file)
        cfg['claude']['models']['strong'] = 'different'
        cfg['assistant']['max_calls_per_task'] = 3
        self.assertEqual(base, before)
        self.assertEqual(self.load()['assistant']['max_calls_per_task'], 1)

    def test_new_plan_overlay_has_no_frozen_models(self):
        cfg = rc.plan_overlay()
        self.assertEqual(cfg['version'], 2)
        self.assertLess(len(json.dumps(cfg)), 300)
        self.assertNotIn('models', cfg['claude'])

    def test_effort_bearing_antigravity_model(self):
        model = 'claude-opus-4-6-thinking'
        self.write(self.global_file, {'antigravity': {'models': {'strong': model}}})
        cfg = self.load()
        self.assertFalse(routingctl.model_supports_effort(cfg['antigravity'], model))
        route = {'provider': 'antigravity', 'tier': 'strong', 'model': model, 'effort': 'high'}
        command = runner.build_worker_command('antigravity', route, cfg, 'bounded task', self.root / 'result.json')
        self.assertNotIn('--effort', command)
        self.assertIn(model, command)
        self.assertTrue(rc.embedded_effort_model('gemini-3.8-flash-low'))
        self.assertFalse(rc.embedded_effort_model('some-provider-high'))

    def test_per_tier_chains_explicit_and_opt_out(self):
        cfg = self.load()
        cfg['tier_routes'] = {'strong': {'primary': 'codex', 'fallbacks': ['antigravity', 'claude']}}
        task = {'model_tier': 'strong', 'provider': 'auto'}
        self.assertEqual(rc.provider_chain(task, cfg), ['codex', 'antigravity', 'claude'])
        self.assertEqual(rc.provider_chain(task, cfg, 'claude'), ['claude', 'codex', 'antigravity'])
        self.assertEqual(rc.provider_chain({**task, 'allow_provider_fallback': False}, cfg), ['codex'])
        cfg['allow_provider_fallback'] = False
        self.assertEqual(rc.provider_chain(task, cfg), ['codex'])
        with patch.object(runner, 'executable_available', return_value=True):
            self.assertEqual(runner.candidate_providers(task, cfg, None), ['codex'])

    def test_invalid_settings_fail_closed(self):
        invalid = [None, [], {'version': True}, {'version': 3}, {'tier_routes': []},
                   {'tier_routes': {'strong': {'primary': 'unknown'}}},
                   {'tier_routes': {'strong': {'primary': 'codex', 'fallbacks': ['codex']}}},
                   {'tier_routes': {'strong': {'primary': 'codex', 'fallbacks': ['claude', 'claude']}}},
                   {'provider_order': []}, {'provider_order': ['auto']}, {'allow_provider_fallback': 'false'},
                   {'claude': {'command': []}}, {'codex': {'models': {'standard': ''}}},
                   {'codex': {'models': {'invalid-tier': 'foo'}}}, {'codex': {'max_effort_by_tier': {'strong': 'extreme'}}},
                   {'assistant': {'enabled': 'yes'}}, {'assistant': {'max_calls_per_task': True}},
                   {'assistant': {'max_calls_per_task': 4}}, {'assistant': {'timeout_seconds': float('nan')}},
                   {'assistant': {'max_input_chars': 999999}}, {'assistant': {'skip_permissions': True}},
                   {'availability': {'cooldown_seconds': 0}}, {'availability': {'max_attempts_per_run': 0}},
                   {'antigravity': {'retry_exit_codes': [True]}},
                   {'antigravity': {'models': {'strong': 'claude-opus-4-6-thinking'}, 'extra_args': ['--effort=high']}}]
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(rc.ConfigError):
                rc.validate(value)

    def test_unreadable_malformed_and_oversized_files(self):
        for content in ('[]', '{', '{"assistant":{"timeout_seconds":NaN}}', 'x' * (rc.MAX_CONFIG_BYTES + 1)):
            self.global_file.write_text(content, encoding='utf-8')
            with self.assertRaises(rc.ConfigError):
                self.load()
        missing = self.root / 'absent.json'
        self.assertEqual(rc.read(missing, optional=True), {})
        with self.assertRaises(rc.ConfigError):
            rc.read(missing)
        with patch.dict(os.environ, {'PAE_CONFIG_PATH': str(missing)}):
            with self.assertRaises(runner.RunnerError):
                runner.load_config(self.root)

    def test_empty_command_rejected_at_dispatch(self):
        with self.assertRaises(runner.RunnerError):
            runner.command_prefix([])


if __name__ == '__main__':
    unittest.main()
