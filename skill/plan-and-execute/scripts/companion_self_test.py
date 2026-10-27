#!/usr/bin/env python3
"""Companion progressive-loading and checkout entrypoint contracts (no provider calls)."""
from __future__ import annotations
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
COMPANION = ROOT / 'skill' / 'validate-or-fix'
MAIN = ROOT / 'skill' / 'plan-and-execute'

class CompanionTests(unittest.TestCase):
    def test_router_is_narrow_and_bounded(self):
        text = (COMPANION / 'SKILL.md').read_text(encoding='utf-8')
        self.assertLess(len(text), 6000)
        for required in ('name: validate-or-fix', 'DIRECT', 'OPERATIONS.md', 'ROUTING.md', 'no plan'):
            self.assertIn(required.lower(), text.lower())
        self.assertNotIn('ORCHESTRATION.md', text)
        self.assertNotIn('PLANNING_PROTOCOL.md', text)

    def test_source_contains_wrappers_not_a_duplicate_runtime(self):
        self.assertFalse((COMPANION / '_runtime').exists())
        for name in ('validatectl.py', 'service_map.py', 'workload_routing.py'):
            text = (COMPANION / 'scripts' / name).read_text(encoding='utf-8')
            self.assertLess(len(text), 1500)
            self.assertIn('runpy', text)

    def test_read_only_cli_entrypoints_do_not_create_planning_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in ('validatectl.py', 'service_map.py', 'workload_routing.py'):
                result = subprocess.run([sys.executable, str(COMPANION / 'scripts' / name), '--help'],
                    cwd=tmp, capture_output=True, text=True, timeout=15,
                    env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('usage:', result.stdout.lower())
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_legacy_and_concise_projection_keep_optional_workload(self):
        import planctl
        from self_test import sample_spec
        task = planctl.normalize_task({**sample_spec()['tasks'][0], 'workload': 'frontend_design'}, 0, {'R001', 'R002'})
        self.assertIn('workload: "frontend_design"', planctl.render_task(task, 'plan'))
        from planctl_concise import planctl as concise
        self.assertIn('workload: "frontend_design"', concise.render_task(task, 'plan'))
        del task['workload']
        self.assertNotIn('workload:', concise.render_task(task, 'plan'))

    def test_main_routes_to_companion_without_requiring_orchestration(self):
        text = (MAIN / 'SKILL.md').read_text(encoding='utf-8')
        section = text.split('### DIRECT EXIT', 1)[1].split('## 3.', 1)[0]
        self.assertIn('validate-or-fix', section)
        self.assertIn('never a plan', section)
        self.assertIn('Fast deterministic checks', section)
        self.assertLess(len(text), 7000)

if __name__ == '__main__':
    unittest.main()
