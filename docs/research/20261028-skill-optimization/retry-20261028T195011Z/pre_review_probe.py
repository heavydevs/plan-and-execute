"""Build read-only evidence for the pending independent plan review.

No provider process is executed. Provider availability in the replay is a
synthetic fixture so the routing algorithm can be inspected without credentials.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--repo-root', required=True, type=Path)
parser.add_argument('--output-dir', required=True, type=Path)
args = parser.parse_args()
ROOT = args.repo_root.resolve()
OUT = args.output_dir.resolve()
OUT.mkdir(parents=True, exist_ok=True)
SCRIPTS = ROOT / 'skill/plan-and-execute/scripts'
sys.path.insert(0, str(SCRIPTS))
import run_concise
import availability
import planctl
import routing_config

run = run_concise.run_isolated
cfg = routing_config.merge(planctl.default_config(), routing_config.EXTRA_DEFAULTS)
custom = copy.deepcopy(cfg)
custom['tier_routes'] = {
    tier: {'primary': chain[0], 'fallbacks': chain[1:]}
    for tier, chain in {
        'economy': ['antigravity', 'codex', 'claude'],
        'standard': ['antigravity', 'codex', 'claude'],
        'advanced': ['antigravity', 'codex', 'claude'],
        'strong': ['codex', 'claude', 'antigravity'],
        'max': ['codex', 'claude'],
    }.items()
}
custom['claude']['models'] = {
    'economy': 'haiku', 'standard': 'claude-sonnet-5-5',
    'strong': 'claude-opus-5-5', 'max': 'claude-opus-5-5',
}
custom['codex']['models'] = {
    'economy': 'gpt-6-luna', 'standard': 'gpt-6.1-sol',
    'strong': 'gpt-6.1-sol', 'max': 'gpt-6.1-sol',
}
custom['antigravity']['models'] = {
    'economy': 'gemini-3.8-flash-medium',
    'standard': 'claude-sonnet-5-5-medium',
    'advanced': 'claude-sonnet-5-5-high',
    'strong': 'claude-opus-5-5-high', 'max': 'claude-opus-5-5-high',
}
custom['antigravity']['models_without_effort'] = list(custom['antigravity']['models'].values())
custom.setdefault('workload_routing', {})['enabled'] = False

cases = []
for fixture, config in [('defaults', cfg), ('user-equivalent-fixture', custom)]:
    for tier, effort, failure in [
        ('strong','high','unknown'), ('max','high','semantic'),
        ('standard','medium','unknown'), ('standard','medium','mechanical'),
        ('advanced','high','unknown'),
    ]:
        task = dict(id='001', provider='auto', model_tier=tier, reasoning_effort=effort,
                    functional_failures=0, failure_classes=[], max_attempts=8)
        case = dict(fixture=fixture, tier=tier, effort=effort, failure_class=failure,
                    attempts=[], declared_chain=routing_config.provider_chain(task, config))
        with tempfile.TemporaryDirectory(prefix='pae-replay-') as tmp:
            temp = Path(tmp)
            for i in range(8):
                try:
                    if run.ladder_exhausted(task, config, None, check_availability=False):
                        case['stop'] = 'ladder_exhausted'
                        break
                    intent = run.choose_route(task, config, None, check_availability=False)
                    route = availability.select(temp, task, config, intent, None,
                        'implementation', set(), lambda _: True, run.clamp_effort, persist=False)
                    argv = run.build_worker_command(route['provider'], route, config,
                        'DIAGNOSTIC FIXTURE ONLY - NOT EXECUTED', temp/'result.json')
                    normalized = [arg.replace(str(temp), '<temporary-fixture>') for arg in argv]
                    signature = hashlib.sha256(json.dumps(normalized, ensure_ascii=True,
                        separators=(',', ':')).encode()).hexdigest()
                    case['attempts'].append({
                        'attempt': i+1, 'intent_provider': intent['provider'],
                        'dispatch_provider': route['provider'], 'model': route['model'],
                        'tier': route['tier'], 'logical_effort': route['effort'],
                        'argv_sha256': signature, 'explicit_effort_flag': '--effort' in argv,
                    })
                except Exception as exc:
                    case['stop'] = type(exc).__name__ + ': ' + str(exc)
                    break
                task['functional_failures'] += 1
                task['failure_classes'].append(failure)
            else:
                case['stop'] = 'max_attempts'
        identities = [item['argv_sha256'] for item in case['attempts']]
        case['repeated_dispatches'] = len(identities) - len(set(identities))
        case['intent_dispatch_mismatches'] = sum(
            row['intent_provider'] != row['dispatch_provider'] for row in case['attempts'])
        case['unvisited_declared_providers'] = [p for p in case['declared_chain']
            if p not in {row['dispatch_provider'] for row in case['attempts']}]
        cases.append(case)

tracked = subprocess.check_output(['git','ls-files','-z'], cwd=ROOT).decode().split('\0')
tracked = [p for p in tracked if p]
source_files = [p for p in tracked if p.startswith(('skill/', 'bin/', 'lib/'))]
changed = []
for relative in source_files:
    baseline = subprocess.check_output(['git','show', 'HEAD:'+relative], cwd=ROOT)
    if (ROOT/relative).read_bytes() != baseline:
        changed.append(relative)
manifest = json.loads((ROOT/'.ai-work/20261028-skill-study-provider-switch/manifest.json').read_text())
tasks = {task['id']: task for task in manifest['tasks']}
def depends_on(task_id: str, wanted: str, stack: frozenset[str] = frozenset()) -> bool:
    if task_id in stack:
        raise ValueError('Dependency cycle')
    deps = tasks[task_id].get('dependencies', [])
    return wanted in deps or any(depends_on(dep, wanted, stack | {task_id}) for dep in deps)

files_read = [
    'skill/plan-and-execute/scripts/run_isolated.py',
    'skill/plan-and-execute/scripts/availability.py',
    'skill/plan-and-execute/scripts/routing_config.py',
    'skill/plan-and-execute/scripts/routingctl.py',
    'skill/plan-and-execute/scripts/workload_routing.py',
    'skill/plan-and-execute/scripts/runner_contract.py',
]
result = {
    'schema_version': 1,
    'status': 'preparatory_evidence_only',
    'independent_review': 'not_performed',
    'live_provider_calls': 0,
    'note': 'Model names are user-provided fixture labels, not verified available models. '
            'Command signatures are built but never executed. This is not a completed plan task.',
    'baseline_commit': subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
    'tracked_files': len(tracked), 'runtime_files_compared': len(source_files),
    'runtime_files_changed': changed,
    'task_counts': dict(Counter(t['status'] for t in tasks.values())),
    'tasks_transitively_waiting_for_001': sum(depends_on(t,'001') for t in tasks if t != '001'),
    'code_fingerprints': [{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in files_read],
    'cases': cases,
}
path=OUT/'pre-review-routing-probe.json'
path.write_text(json.dumps(result,indent=2)+'\n')
for case in cases:
    print(json.dumps({k:case[k] for k in ('fixture','tier','failure_class','stop','repeated_dispatches',
                                        'intent_dispatch_mismatches','unvisited_declared_providers')}))
print('RUNTIME_FILES_COMPARED',len(source_files),'CHANGED',len(changed))
print('ALL_OTHER_TASKS_DEPEND_ON_001',result['tasks_transitively_waiting_for_001'])
print('OUTPUT',path)
