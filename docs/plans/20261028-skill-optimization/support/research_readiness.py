#!/usr/bin/env python3
"""Read-only preparation checks, not product acceptance or reviewer authentication."""
from __future__ import annotations
import argparse
import json
import shutil
import os
import subprocess
import sys
from pathlib import Path
import check_delivery as gate

ROOT = Path(__file__).resolve().parents[4]


def ancestors(tasks: dict, task_id: str) -> set[str]:
    seen: set[str] = set()
    active: set[str] = set()
    def visit(tid: str) -> None:
        gate.require(tid in tasks, 'Unknown dependency')
        gate.require(tid not in active, 'Dependency cycle')
        if tid in seen:
            return
        active.add(tid)
        for child in tasks[tid]['dependencies']:
            visit(child)
        active.remove(tid)
        seen.add(tid)
    for dep in tasks[task_id]['dependencies']:
        visit(dep)
    return seen


def check(root: Path = ROOT, native: bool = True) -> dict:
    structural = gate.structural(root, native)
    spec = gate.load(root / gate.DOC / 'PLAN1_SPEC.json')
    entries = gate.catalog(root)
    tasks = {f"{t['id']:03}": t for t in spec['tasks']}
    index = gate.load(root / gate.PREP / 'INDEX.json')
    sources = {s['id']: s for s in gate.load(root / gate.PREP / 'SOURCES.json')['sources']}
    gate.require(index.get('research_revision') == 2, 'Research revision is not current')
    anchors = 0
    alternatives = 0
    for row in index['reports']:
        record = gate.load(gate.local(root, row['decision_record']))
        gate.require(record.get('research_revision') == 2, 'Unrevised topic')
        gate.require(record.get('revision_delta') and len(record.get('decision_analysis', [])) >= 4,
                     'Missing comparative design analysis')
        gate.require(len(record.get('alternatives', [])) >= 4, 'Missing competing options')
        gate.require(set(row['source_ids']) == set(record['source_ids']), 'Index source mismatch')
        fresh = record.get('current_source_ids', [])
        gate.require(len(set(fresh)) >= 2 and set(fresh) <= set(record['source_ids']), 'Missing fresh source links')
        gate.require(all(sources[s].get('research_round') == 2 and sources[s].get('web_references') for s in fresh),
                     'Current source lacks retrieval provenance')
        gate.require(record.get('unverified') and record.get('applicability_rule'), 'Missing evidence limits')
        for anchor in record.get('code_anchors', []):
            gate.require(gate.sha(gate.local(root, anchor['path'])) == anchor['sha256'], 'Baseline code anchor changed')
            anchors += 1
        alternatives += len(record['alternatives'])
    closures = {t: ancestors(tasks, t) for t in tasks}
    planned = {p for e in entries.values() for p in e['write_scope']}
    reviews = 0
    for tid, entry in entries.items():
        t = tasks[tid]
        expected = set(entry['write_scope']) | {entry['output'], entry['report']}
        gate.require(set(t['scope']['expected_files']) == expected, f'Scope/catalog mismatch: {tid}')
        input_contract = {i['path']: i for i in entry.get('input_contract', [])}
        gate.require(set(input_contract) == set(entry['inputs']), 'Missing explicit input availability contract')
        for path, contract in input_contract.items():
            gate.local(root, path)
            mode = contract.get('availability')
            if mode == 'existing_baseline_or_current_file':
                gate.require((root / path).is_file(), 'Missing current input: ' + path)
            elif mode == 'create_in_this_task':
                gate.require(path in entry['write_scope'], 'New input outside task write scope')
            elif mode == 'prerequisite_output':
                producer = contract.get('producer_task')
                gate.require(producer in closures[tid], 'Input producer is not a dependency')
                declared = set(entries[producer]['write_scope']) | {entries[producer]['output'], entries[producer]['report']}
                gate.require(path in declared, 'Input producer does not own output')
            else:
                raise gate.GateError('Unknown input availability state')
        for path in entry['write_scope']:
            gate.local(root, path)
            if not (root / path).exists():
                gate.require(path in entry.get('planned_new_files', []), f'Undeclared future path: {tid}/{path}')
        for command in entry['required_checks']:
            if command[0] in ('python', 'python3', 'node') and len(command) >= 2 and not command[1].startswith('-'):
                path = command[1]
                gate.require((root / path).is_file() or path in planned, f'Missing unowned check: {tid}/{path}')
        if entry['requires_independent_review']:
            reviews += 1
            gate.require(t['model_tier'] == 'max', 'Independent review floor lowered')
            if entry.get('review_of'):
                parent = entries[entry['review_of']]
                gate.require(set(entry['write_scope']) == set(parent['write_scope']), 'Reviewer cannot correct assigned code')
                gate.require(entry['required_checks'] == parent['required_checks'], 'Reviewer tests differ from implementation')
        for other in tasks:
            if other <= tid or tid in closures[other]:
                continue
            gate.require(not set(entry['write_scope']) & set(entries[other]['write_scope']),
                         f'Unordered shared-file writes: {tid}/{other}')
    gate.require(reviews == 43, 'Independent review count changed')
    gate.require('skill/plan-and-execute/scripts/run_isolated.py' not in entries['020']['write_scope'],
                 'Pure routing task absorbs runtime integration')
    gate.require(all(p.startswith('test/') for p in entries['068']['write_scope']), 'Fixture task absorbs runtime implementation')
    gate.require('package.json' in entries['066']['write_scope'] and
                 'skill/plan-and-execute/scripts/package.json' not in planned, 'Incorrect package contract location')
    gate.require(['python', 'test/optimization/integration_082_self_test.py'] in entries['082']['required_checks'],
                 'Integration lacks test-wiring regression')
    if native:
        manifest = gate.load(root / gate.CONTROL / 'manifest.json')
        gate.require(all(t['status'] == 'pending' and not t.get('attempts') for t in manifest['tasks']),
                     'Research preparation changed execution status')
        gate.require(not (root / gate.CONTROL / '.runner-lease.json').exists(), 'An active runner lease needs separate investigation')
        native_checks = [
            [sys.executable, 'skill/plan-and-execute/scripts/planctl_concise.py', 'validate', '--plan', str(gate.CONTROL)],
            [sys.executable, 'skill/plan-and-execute/scripts/studyctl_concise.py', 'validate-plan', '--plan', str(gate.CONTROL), '--json'],
        ]
        for argv in native_checks:
            result = subprocess.run(argv, cwd=root, capture_output=True, text=True, timeout=40,
                                    env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
            gate.require(result.returncode == 0, 'Native validation rejected preparation: ' + Path(argv[1]).name)
    return {
        **structural, 'research_revision': 2, 'native_validators_executed': native, 'alternatives_compared': alternatives,
        'baseline_anchor_checks': anchors, 'shared_write_conflicts': 0,
        'implementation_tasks': len(tasks), 'subtasks': sum(len(t['subtasks']) for t in tasks.values()),
        'independent_review_tasks': reviews, 'state': 'prepared_for_implementation',
        'runtime_qualification': 'Not established by these checks; needs allowed installed/authenticated providers and actual independent reviewers.',
        'product_tests': 'Future implementation acceptance was not run by this preparation checker.',
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, default=ROOT)
    parser.add_argument('--without-native', action='store_true')
    args = parser.parse_args()
    try:
        result = check(args.repo_root.resolve(), not args.without_native)
    except (gate.GateError, KeyError, TypeError, ValueError) as exc:
        print(json.dumps({'ready': False, 'error': str(exc)}))
        return 1
    result['ready'] = True
    result['provider_executables_present'] = {n: shutil.which(n) is not None for n in ('claude', 'codex', 'agy')}
    result['authentication_tested'] = False
    print(json.dumps(result, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
