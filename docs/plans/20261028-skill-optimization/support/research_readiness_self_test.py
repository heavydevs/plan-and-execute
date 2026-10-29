#!/usr/bin/env python3
"""Negative preparation-gate fixtures. They never dispatch a provider."""
from __future__ import annotations
import copy
from pathlib import Path
import unittest
from unittest.mock import patch
import research_readiness as r

class ReadinessTests(unittest.TestCase):
    def altered(self, name, edit, expected=True):
        original = r.gate.load
        def loader(path):
            data = original(path)
            if Path(path).name == name:
                data = edit(copy.deepcopy(data))
            return data
        with patch.object(r.gate, 'load', side_effect=loader):
            if expected:
                with self.assertRaises((r.gate.GateError, KeyError)):
                    r.check(native=False)
            else:
                return r.check(native=False)

    def test_real_prepared_plan(self):
        self.assertEqual(r.check()['implementation_tasks'], 86)
    def test_old_revision_rejected(self):
        def edit(x): x['research_revision']=1;return x
        self.altered('INDEX.json',edit)
    def test_missing_current_sources_rejected(self):
        def edit(x): x['current_source_ids']=[];return x
        self.altered('006-activation-intake.json',edit)
    def test_analysis_missing_rejected(self):
        def edit(x): x['decision_analysis']=[];return x
        self.altered('006-activation-intake.json',edit)
    def test_one_alternative_rejected(self):
        def edit(x): x['alternatives']=x['alternatives'][:1];return x
        self.altered('006-activation-intake.json',edit)
    def test_fresh_source_without_provenance_rejected(self):
        def edit(x):
            for s in x['sources']:
                if s['id'].startswith('W-'):s['web_references']=[]
            return x
        self.altered('SOURCES.json',edit)
    def test_missing_uncertainty_rejected(self):
        def edit(x):x['unverified']=[];return x
        self.altered('006-activation-intake.json',edit)
    def test_changed_baseline_anchor_rejected(self):
        def edit(x):x['code_anchors'][0]['sha256']='0'*64;return x
        self.altered('006-activation-intake.json',edit)
    def test_scope_catalog_disagreement_rejected(self):
        def edit(x):x['tasks'][5]['write_scope'].append('unowned.py');return x
        self.altered('TASK_INPUTS.json',edit)
    def test_missing_future_check_rejected(self):
        def edit(x):x['tasks'][5]['required_checks']=[['python','test/missing_unowned_test.py']];return x
        self.altered('TASK_INPUTS.json',edit)
    def test_review_checks_cannot_differ(self):
        def edit(x):x['tasks'][6]['required_checks']=[['python','test/optimization/task_001_self_test.py']];return x
        self.altered('TASK_INPUTS.json',edit)
    def test_unknown_current_source_rejected(self):
        def edit(x):x['current_source_ids'].append('W-NONEXISTENT');return x
        self.altered('006-activation-intake.json',edit)
    def test_missing_input_contract_rejected(self):
        def edit(x):x['tasks'][5]['input_contract']=[];return x
        self.altered('TASK_INPUTS.json',edit)
    def test_undeclared_input_producer_rejected(self):
        def edit(x):
            for c in x['tasks'][6]['input_contract']:
                if c['availability']=='prerequisite_output':c['producer_task']='086'
            return x
        self.altered('TASK_INPUTS.json',edit)
    def test_dag_cycle_rejected(self):
        tasks={'001':{'dependencies':['002']},'002':{'dependencies':['001']}}
        with self.assertRaises(r.gate.GateError):r.ancestors(tasks,'001')
    def test_dag_transitive_dependencies(self):
        tasks={'001':{'dependencies':[]},'002':{'dependencies':['001']},'003':{'dependencies':['002']}}
        self.assertEqual(r.ancestors(tasks,'003'),{'001','002'})
    def test_plan_does_not_claim_product_acceptance(self):
        result=r.check()
        self.assertEqual(result['implementation'],'not performed by this check')
        self.assertEqual(result['independent_reviews'],'not performed by this check')

if __name__=='__main__':unittest.main(verbosity=2)
