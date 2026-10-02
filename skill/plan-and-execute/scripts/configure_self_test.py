#!/usr/bin/env python3
"""Setup contract tests. Mock status probes never authenticate or bill a model."""
import copy
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import configure as c


def defaults():
    return c.rc.merge(c.routingctl.install_current_model_catalog(c.planctl).default_config(), c.rc.EXTRA_DEFAULTS)


class SetupTests(unittest.TestCase):
    def test_discovery_never_generates_or_exposes_secrets(self):
        calls = []
        def probe(args, **kw):
            calls.append((args, kw))
            return subprocess.CompletedProcess(args, 0)
        # Host PATH may hold real claude/codex shims; keep bare names regardless.
        with patch('run_isolated.resolve_windows_shim', side_effect=lambda parts: parts):
            result = c.discover(defaults(), which=lambda _: '/bin/fake', probe=probe)
        self.assertEqual([x[0] for x in calls], [['claude', 'auth', 'status'], ['codex', 'login', 'status']])
        self.assertEqual(result['antigravity']['authentication'], 'unknown')
        self.assertTrue(all(x[1]['stdout'] == subprocess.DEVNULL and x[1]['timeout'] == 3 for x in calls))

    def test_timeout_auth_failure_missing_and_wrappers(self):
        def timeout(*args, **kw):
            raise subprocess.TimeoutExpired(args[0], 3)
        result = c.discover(defaults(), which=lambda _: True, probe=timeout)
        self.assertEqual(result['claude']['authentication'], 'unknown')
        result = c.discover(defaults(), which=lambda _: True, probe=lambda *a, **kw: subprocess.CompletedProcess(a, 1))
        self.assertEqual(result['codex']['authentication'], 'unauthenticated')
        cfg = defaults();cfg['claude']['command'] = ['custom-wrapper', 'claude']
        result = c.discover(cfg, which=lambda name: name == 'custom-wrapper', probe=lambda *a, **kw: self.fail('custom wrapper probed'))
        self.assertEqual(result['claude']['authentication'], 'unknown')
        self.assertFalse(result['codex']['installed'])

    def test_separate_questions_and_ordered_fallbacks(self):
        questions = []
        available = {p: {'installed': True, 'authentication': 'authenticated'} for p in ('claude', 'codex', 'antigravity')}
        def ask(q):
            questions.append(q)
            if q.id.endswith('.primary'): return 'codex'
            if '.fallback.1' in q.id: return 'antigravity'
            if '.fallback.2' in q.id: return 'claude'
            if q.id == 'assistant.enabled': return 'Sim'
            if q.id == 'assistant.provider': return 'claude'
            return q.choices[0]
        result = c.wizard(defaults(), available, ask)
        for route in result['tier_routes'].values():
            self.assertEqual(route, {'primary': 'codex', 'fallbacks': ['antigravity', 'claude']})
        ids = [q.id for q in questions]
        self.assertNotEqual(ids.index('assistant.enabled'), ids.index('assistant.provider'))
        self.assertTrue(all(q.as_dict()['id'] for q in questions))
        self.assertTrue(all(len(q.choices) == len(set(q.choices)) for q in questions))

    def test_unknown_requires_confirmation_failed_auth_not_offered(self):
        questions = []
        def ask(q):
            questions.append(q)
            return 'Sim' if q.id.startswith('auth.') else q.choices[0]
        statuses = {'antigravity': {'installed': True, 'authentication': 'unknown'},
                    'codex': {'installed': True, 'authentication': 'unauthenticated'}}
        cfg = c.wizard(defaults(), statuses, ask)
        self.assertEqual(questions[0].id, 'auth.antigravity')
        self.assertTrue(all(r['primary'] == 'antigravity' for r in cfg['tier_routes'].values()))
        self.assertFalse(any('codex' in q.choices for q in questions))
        with self.assertRaises(c.rc.ConfigError):
            c.wizard(defaults(), statuses, lambda q: 'Nao')

    def test_manual_model_and_embedded_effort(self):
        def ask(q):
            if q.id.endswith('.model'): return 'Outro ID'
            if q.id.endswith('.model_id'): return 'claude-opus-4-6-thinking'
            if q.id.endswith('.omit_effort'): self.fail('embedded ID should not add contradictory effort')
            return q.choices[0]
        cfg = c.wizard(defaults(), {'antigravity': {'installed': True, 'authentication': 'authenticated'}}, ask)
        self.assertIn('claude-opus-4-6-thinking', cfg['antigravity']['models_without_effort'])
        self.assertEqual(cfg['antigravity']['models']['max'], 'claude-opus-4-6-thinking')

    def test_bad_model_id(self):
        def ask(q):
            if q.id.endswith('.model'): return 'Outro ID'
            if q.id.endswith('.model_id'): return 'escape\x1b'
            return q.choices[0]
        with self.assertRaises(c.rc.ConfigError):
            c.wizard(defaults(), {'codex': {'installed': True, 'authentication': 'authenticated'}}, ask)

    def test_terminal_repeats_only_invalid_question_and_eof_cancels(self):
        answers = iter(['0', 'bad', '2']); seen = []
        self.assertEqual(c.terminal_ask(c.Question('p', 'provider?', ('a', 'b')), read=lambda _: next(answers), write=seen.append), 'b')
        self.assertEqual(seen.count('provider?'), 3)
        with self.assertRaises(c.Cancelled):
            c.terminal_ask(c.Question('p', 'p', ('a',)), read=lambda _: (_ for _ in ()).throw(EOFError()), write=lambda _: None)
        with self.assertRaises(c.rc.ConfigError):
            c.wizard(defaults(), {'codex': {'installed': True, 'authentication': 'authenticated'}}, lambda q: 'not-a-choice')

    def test_cancellation_dry_run_and_atomic_save_preserve_unrelated_settings(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'config.json'
            original = b'{"version":2,"task_timeout_seconds":123,"claude":{"extra_args":["custom"]}}\n'
            path.write_bytes(original)
            discovery = lambda _: {'codex': {'installed': True, 'authentication': 'authenticated'}}
            def ask(q):
                if q.id == 'save': return 'Nao'
                return q.choices[0]
            with self.assertRaises(c.Cancelled):
                c.configure(path, ask=ask, discover_fn=discovery, write=lambda _: None)
            self.assertEqual(path.read_bytes(), original)
            c.configure(path, ask=ask, discover_fn=discovery, dry_run=True, write=lambda _: None)
            self.assertEqual(path.read_bytes(), original)
            c.configure(path, ask=lambda q: 'Sim' if q.id == 'save' else q.choices[0], discover_fn=discovery, write=lambda _: None)
            saved = json.loads(path.read_text())
            self.assertEqual(saved['task_timeout_seconds'], 123)
            self.assertEqual(saved['claude']['extra_args'], ['custom'])
            self.assertFalse(path.with_name(path.name + '.configure.lock').exists())
            if os.name != 'nt': self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_concurrent_change_and_existing_lock_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'config.json';p.write_text('{}')
            with self.assertRaises(c.rc.ConfigError): c.save(p, {}, b'old')
            self.assertEqual(p.read_text(), '{}')
            lock = p.with_name(p.name + '.configure.lock');lock.write_text('other')
            with self.assertRaises(c.rc.ConfigError): c.save(p, {}, b'{}')
            self.assertEqual(lock.read_text(), 'other')

    @unittest.skipIf(os.name == 'nt', 'Symlink creation requires Windows privileges')
    def test_symlink_targets_and_parents_are_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); target = root / 'target';target.write_text('{}')
            (root / 'link').symlink_to(target)
            (root / 'dirlink').symlink_to(root, target_is_directory=True)
            for p in (root / 'link', root / 'dirlink' / 'new'):
                with self.assertRaises(c.rc.ConfigError): c.save(p, {}, None)
            self.assertEqual(target.read_text(), '{}')

    def test_show_never_probes_or_echoes_command_secrets_and_node_bridge(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'config.json'
            p.write_text(json.dumps({'codex': {'extra_args': ['SECRET-do-not-print']}}))
            output = []
            c.configure(p, show=True, discover_fn=lambda _: self.fail('show probes'), write=output.append)
            self.assertNotIn('SECRET', ''.join(output))
            cli = Path(__file__).resolve().parents[3] / 'bin' / 'plan-and-execute.js'
            r = subprocess.run(['node', str(cli), 'configure', '--show', '--json', '--config', str(p)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(json.loads(r.stdout)['path'], str(p))
            self.assertNotIn('SECRET', r.stdout)

    def test_profile_setup_and_doctor_report_names_only(self):
        secret = 'sk-never-print-this'
        env = {'ZAI_API_KEY': secret, 'ZAI_BASE_URL': 'https://secret.invalid'}
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'config.json'
            out = []
            self.assertEqual(c.doctor(p, env=env, which=lambda _: None)['configured'], [])
            c.set_profile(p, 'glm', write=out.append)
            c.set_profile(p, 'deepseek', 'codex', write=out.append)
            saved = json.loads(p.read_text())
            self.assertEqual(saved['profiles']['deepseek']['harness'], 'codex')
            with self.assertRaises(c.rc.ConfigError): c.set_profile(p, 'glm', 'codex', write=out.append)
            with self.assertRaises(c.rc.ConfigError): c.set_profile(p, 'nope', write=out.append)
            report = c.doctor(p, env=env, which=lambda _: '/bin/fake')
            text = json.dumps(report) + ''.join(out)
            self.assertNotIn(secret, text)
            self.assertNotIn('secret.invalid', text)
            self.assertEqual(report['configured'], ['deepseek', 'glm'])
            self.assertTrue(report['providers']['glm']['token_set'])
            self.assertFalse(report['providers']['deepseek']['token_set'])
            self.assertTrue(report['providers']['glm']['command_found'])
            self.assertEqual(c.summary(c.rc.merge(defaults(), saved))['profiles']['glm']['token_env'], 'ZAI_API_KEY')

    def test_missing_global_setup_destination_and_plan_validation(self):
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ, {'PAE_CONFIG_PATH': str(Path(d) / 'new.json')}):
            p = Path(d) / 'new.json'
            c.configure(p, show=True, write=lambda _: None)
            self.assertFalse(p.exists())
            with self.assertRaises(c.rc.ConfigError): c.configure(p, plan=True, show=True, write=lambda _: None)


if __name__ == '__main__':
    unittest.main()
