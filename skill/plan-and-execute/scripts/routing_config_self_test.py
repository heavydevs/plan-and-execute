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
import configure
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

    def test_profiles_validate_and_layer(self):
        self.write(self.global_file, {'version': 2, 'profiles': {'gateway': {'harness': 'claude', 'base_url_env': 'GW_URL', 'token_env': 'GW_TOKEN'}}})
        self.write(self.plan_file, {'version': 2, 'profiles': {'gateway': {'token_env': 'PLAN_TOKEN'}}, 'kimi': {'profile': 'gateway'}})
        cfg = self.load()
        self.assertEqual(cfg['profiles']['gateway'], {'harness': 'claude', 'base_url_env': 'GW_URL', 'token_env': 'PLAN_TOKEN'})
        resolved = rc.resolve_profile('kimi', cfg)
        self.assertEqual((resolved['harness'], resolved['adapter'], resolved['command']), ('claude', 'claude', 'claude'))
        self.assertEqual((resolved['base_url_env'], resolved['token_env']), ('GW_URL', 'PLAN_TOKEN'))
        self.assertNotIn('profiles', rc.plan_overlay())

    def test_profile_and_harness_are_independent_axes(self):
        cfg = self.load()
        for provider in rc.PROVIDERS:
            implicit = rc.resolve_profile(provider, cfg)
            self.assertEqual((implicit['adapter'], implicit['command'], implicit['token_env']), (provider, cfg[provider]['command'], None))
        cfg['profiles'] = {'p': {'harness': 'codex', 'token_env': 'A_TOKEN'}}
        cfg['qwen']['profile'] = 'p'
        first = rc.resolve_profile('qwen', cfg)
        cfg['profiles']['p']['token_env'] = 'B_TOKEN'  # profile changes, harness does not
        second = rc.resolve_profile('qwen', cfg)
        self.assertEqual((first['adapter'], second['adapter']), ('codex', 'codex'))
        self.assertEqual((first['token_env'], second['token_env']), ('A_TOKEN', 'B_TOKEN'))
        cfg['profiles']['p']['harness'] = 'native'  # harness changes, credentials do not
        third = rc.resolve_profile('qwen', cfg)
        self.assertEqual((third['adapter'], third['command'], third['token_env']), ('qwen', 'qwen', 'B_TOKEN'))
        cfg['profiles']['p']['command'] = ['my-cli', '--flag']
        self.assertEqual(rc.resolve_profile('qwen', cfg)['command'], ['my-cli', '--flag'])

    def test_invalid_profiles_fail_closed_without_echoing_values(self):
        secret = 'sk-planted-SECRET-0001'
        invalid = [{'profiles': []}, {'profiles': {'Bad Name': {'harness': 'claude'}}},
                   {'profiles': {'p': {'harness': 'openai'}}}, {'profiles': {'p': {}}},
                   {'profiles': {'p': {'harness': 'claude', 'token': secret}}},
                   {'profiles': {'p': {'harness': 'claude', 'token_env': secret}}},
                   {'profiles': {'p': {'harness': 'claude', 'base_url_env': 'https://' + secret}}},
                   {'profiles': {'p': {'harness': 'claude', 'command': []}}},
                   {'claude': {'profile': 'missing'}}, {'claude': {'profile': 3}}]
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(rc.ConfigError) as caught:
                rc.validate(value)
            self.assertNotIn(secret, str(caught.exception))
        rc.validate({'claude': {'profile': 'later'}}, partial=True)
        rc.validate({'profiles': {'p': {'token_env': 'ONLY_TOKEN'}}}, partial=True)

    def test_show_never_prints_profile_secrets(self):
        secret = 'sk-planted-SECRET-0002'
        self.write(self.global_file, {'version': 2, 'profiles': {'gw': {'harness': 'claude', 'base_url_env': 'GW_URL', 'token_env': 'GW_TOKEN'}},
                                      'kimi': {'profile': 'gw'}})
        output = []
        with patch.dict(os.environ, {'GW_TOKEN': secret, 'GW_URL': 'https://' + secret}):
            configure.configure(self.global_file, show=True, discover_fn=lambda _: self.fail('show probes'), write=output.append)
        self.assertTrue(output)
        self.assertNotIn(secret, '\n'.join(output))
        self.write(self.global_file, {'version': 2, 'profiles': {'gw': {'harness': 'claude', 'api_key': secret}}})
        with self.assertRaises(rc.ConfigError) as caught:
            configure.configure(self.global_file, show=True, write=output.append)
        self.assertNotIn(secret, str(caught.exception) + '\n'.join(output))

    def test_empty_command_rejected_at_dispatch(self):
        with self.assertRaises(runner.RunnerError):
            runner.command_prefix([])


if __name__ == '__main__':
    unittest.main()
