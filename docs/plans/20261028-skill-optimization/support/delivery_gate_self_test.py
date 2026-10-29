#!/usr/bin/env python3
"""Synthetic unit fixtures for the plan-local gate, not real reviewer attestations."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import check_delivery as g
import run_task_checks

ROOT=Path(__file__).resolve().parents[4]


class GateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.report=str(g.PREP/'decision.md')
        self.code='test/optimization/unit.py'
        self.write(self.report, '# Decision\n')
        self.write(self.code, 'print("fixture passed")\n')
        self.e={'id':'006','kind':'implementation','work_type':'implementation',
                'requires_independent_review':False,'review_of':None,
                'prepared_reports':[self.report],'output':str(g.OUTPUT/'006-receipt.json'),
                'report':str(g.OUTPUT/'006-outcome.md'),'required_checks':[['python',self.code]],
                'write_scope':[self.code],'acceptance_ids':['AC01']}
        self.write_json(g.DOC/'TASK_INPUTS.json',{'schema_version':2,'tasks':[self.e]})
        self.write(self.e['report'],'# Fixture outcome\n')
        self.log=str(g.OUTPUT/'fixture.log');self.write(self.log,'fixture passed\n')
        self.machine={'schema_version':1,'task_id':'006','input_fingerprint':g.code_fingerprint(self.root,self.e),
                      'inputs_unchanged':True,'checks':[{'argv':['python',self.code],'exit_code':0,
                                                       'log':self.log,'log_sha256':g.sha(self.root/self.log)}]}
        self.write_json(g.OUTPUT/'006-checks.json',self.machine)
        self.packet={'schema_version':2,'task_id':'006','kind':'implementation','status':'completed',
                     'summary':'Synthetic gate fixture only; no actual reviewer is asserted.',
                     'outcome_sha256':g.sha(self.root/self.e['report']),
                     'prepared_inputs':[self.hashed(self.report)],'changed_artifacts':[self.hashed(self.code)],
                     'checks_sha256':g.sha(self.root/g.OUTPUT/'006-checks.json'),
                     'acceptance_coverage':[{'id':'AC01','result':'passed','evidence':[self.log]}], 'limitations':['Synthetic fixture']}
        self.save()

    def write(self,name,text):
        p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text);return p
    def write_json(self,name,data):return self.write(name,json.dumps(data))
    def hashed(self,name):return {'path':name,'sha256':g.sha(self.root/name)}
    def save(self):self.write_json(self.e['output'],self.packet)
    def machine_save(self):
        self.write_json(g.OUTPUT/'006-checks.json',self.machine)
        self.packet['checks_sha256']=g.sha(self.root/g.OUTPUT/'006-checks.json');self.save()
    def reject(self):
        with self.assertRaises(g.GateError):g.check(self.root,'006')

    def test_valid_synthetic_gate_fixture(self):self.assertEqual(g.check(self.root,'006')['artifact_gate'],'passed')
    def test_justified_preservation(self):
        self.packet['changed_artifacts']=[];self.packet['no_changes_needed']=True
        self.packet['preservation_reason']='The tested fixture already satisfies its assigned contract; no unrelated edit is justified.'
        self.packet['preserved_artifacts']=[self.hashed(self.code)];self.save()
        self.assertEqual(g.check(self.root,'006')['artifact_gate'],'passed')
    def test_unjustified_no_change_rejected(self):
        self.packet['changed_artifacts']=[];self.save();self.reject()
    def test_report_without_receipt_rejected(self):(self.root/self.e['output']).unlink();self.reject()
    def test_report_is_not_code(self):self.packet['changed_artifacts']=[self.hashed(self.report)];self.save();self.reject()
    def test_incomplete_receipt(self):self.packet['status']='pending';self.save();self.reject()
    def test_changed_code_invalidates_checks(self):self.write(self.code,'print("different")\n');self.packet['changed_artifacts']=[self.hashed(self.code)];self.save();self.reject()
    def test_stale_report(self):self.write(self.report,'changed');self.reject()
    def test_failed_check(self):self.machine['checks'][0]['exit_code']=1;self.machine_save();self.reject()
    def test_bool_is_not_exit_code(self):self.machine['checks'][0]['exit_code']=False;self.machine_save();self.reject()
    def test_substituted_command(self):self.machine['checks'][0]['argv']=['echo','pass'];self.machine_save();self.reject()
    def test_missing_check(self):self.machine['checks']=[];self.machine_save();self.reject()
    def test_modified_log(self):self.write(self.log,'modified');self.reject()
    def test_secret_rejected(self):self.packet['summary']='Authorization: Bearer confidential-value';self.save();self.reject()
    def test_acceptance_missing(self):self.packet['acceptance_coverage']=[];self.save();self.reject()
    def test_acceptance_unpassed(self):self.packet['acceptance_coverage'][0]['result']='proposed';self.save();self.reject()
    def test_traversal(self):
        with self.assertRaises(g.GateError):g.local(self.root,'../outside')
    def test_absolute_path(self):
        with self.assertRaises(g.GateError):g.local(self.root,'/tmp/outside')
    def test_symlink(self):
        p=self.root/'alias';p.symlink_to(self.root/self.report)
        with self.assertRaises(g.GateError):g.local(self.root,'alias')
    def test_duplicate_json(self):
        p=self.write('duplicate.json','{"status":"pending","status":"completed"}')
        with self.assertRaises(g.GateError):g.load(p)
    def test_nonfinite_json(self):
        p=self.write('bad.json','{"cost":Infinity}')
        with self.assertRaises(g.GateError):g.load(p)
    def test_fake_review_rejected(self):
        self.e['requires_independent_review']=True
        self.write_json(g.DOC/'TASK_INPUTS.json',{'schema_version':2,'tasks':[self.e]})
        self.machine['input_fingerprint']=g.code_fingerprint(self.root,self.e)
        self.packet['reviewer']={'model_tier':'max','fresh_context':True,'provider':'host'}
        self.machine_save();self.reject()
    def test_low_tier_review_rejected(self):
        self.e['requires_independent_review']=True
        self.write_json(g.DOC/'TASK_INPUTS.json',{'schema_version':2,'tasks':[self.e]})
        self.machine['input_fingerprint']=g.code_fingerprint(self.root,self.e)
        self.packet['reviewer']={'model_tier':'standard','fresh_context':True,'provider':'claude'}
        self.machine_save();self.reject()
    def test_declared_runner_executes_real_fixture(self):
        self.assertEqual(run_task_checks.run(self.root,'006'),0)
        result=g.load(self.root/g.OUTPUT/'006-checks.json')
        self.assertEqual(result['checks'][0]['exit_code'],0)
        self.assertIn('fixture passed',(self.root/result['checks'][0]['log']).read_text())
    def test_declared_runner_records_failure(self):
        self.write(self.code,'raise SystemExit(7)\n')
        self.assertEqual(run_task_checks.run(self.root,'006'),1)
        self.assertEqual(g.load(self.root/g.OUTPUT/'006-checks.json')['checks'][0]['exit_code'],7)


class StructureTests(unittest.TestCase):
    def test_actual_prepared_plan(self):self.assertEqual(g.structural(ROOT,False)['prepared_research_reports'],32)
    def changed(self,name,transform):
        original=g.load
        def loader(path):
            value=original(path)
            return transform(copy.deepcopy(value)) if path.name==name else value
        with patch.object(g,'load',side_effect=loader),self.assertRaises(g.GateError):g.structural(ROOT,False)
    def test_unknown_source(self):
        def edit(d):d['reports'][0]['source_ids'].append('E999');return d
        self.changed('INDEX.json',edit)
    def test_stale_report_hash(self):
        def edit(d):d['reports'][0]['report_sha256']='0'*64;return d
        self.changed('INDEX.json',edit)
    def test_research_kind_rejected(self):
        def edit(d):d['tasks'][5]['kind']='research';return d
        self.changed('TASK_INPUTS.json',edit)
    def test_dependency_cycle_rejected(self):
        def edit(d):d['tasks'][0]['dependencies']=['086'];return d
        self.changed('PLAN1_SPEC.json',edit)
    def test_removed_review_rejected(self):
        def edit(d):d['tasks'][6]['requires_independent_review']=False;return d
        self.changed('TASK_INPUTS.json',edit)
    def test_no_second_plan_work(self):
        def edit(d):d['tasks'][83]['title']='Create the second plan';return d
        self.changed('PLAN1_SPEC.json',edit)
    def test_autostart_rejected(self):
        def edit(d):d['autostart']=True;return d
        self.changed('PLAN1_SPEC.json',edit)


if __name__=='__main__':unittest.main(verbosity=2)
