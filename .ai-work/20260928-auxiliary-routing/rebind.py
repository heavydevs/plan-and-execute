#!/usr/bin/env python3
"""Rebind this retained checkout's plan paths; never change task progress."""
import argparse
import json
import sys
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--repo-root', default='.')
args = p.parse_args()
root = Path(args.repo_root).resolve()
plan = Path(__file__).resolve().parent
if not (root / '.git').exists() or plan != root / '.ai-work' / '20260928-auxiliary-routing':
    raise SystemExit('Run only from the intended Git checkout and retained plan directory.')
if (plan / '.runner-lease.json').exists():
    raise SystemExit('Resolve the runner lease through lifecyclectl before rebinding.')
sys.path.insert(0, str(root / 'skill/plan-and-execute/scripts'))
from planctl_concise import planctl
manifest = json.loads((plan / 'manifest.json').read_text(encoding='utf-8'))
sentinel = json.loads((plan / '.orchestrator-plan').read_text(encoding='utf-8'))
if manifest['plan_id'] != plan.name or sentinel['plan_id'] != plan.name:
    raise SystemExit('Plan identity mismatch.')
manifest['repo_root'] = str(root)
sentinel['repo_root'] = str(root)
planctl.atomic_write_json(plan / '.orchestrator-plan', sentinel)
planctl.save_manifest(plan, manifest)
errors = planctl.validate_plan(plan, manifest)
if errors:
    raise SystemExit('\n'.join(errors))
print('Retained plan rebound; task progress unchanged:', plan)
