#!/usr/bin/env python3
"""Synthetic unit fixtures for the plan-local gate, not real reviewer attestations."""
from __future__ import annotations
import copy
import json
from pathlib import Path, PureWindowsPath
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
        self.report=(g.PREP/'decision.md').as_posix()
        self.code='test/optimization/unit.py'
        self.write(self.report, '# Decision\n')
        self.write(self.code, 'print("fixture passed")\n')
        self.e={'id':'006','kind':'implementation','work_type':'implementation',
                'requires_independent_review':False,'review_of':None,
                'prepared_reports':[self.report],'output':(g.OUTPUT/'006-receipt.json').as_posix(),
                'report':(g.OUTPUT/'006-outcome.md').as_posix(),'required_checks':[['python',self.code]],
                'write_scope':[self.code],'acceptance_ids':['AC01']}
        self.write_json(g.DOC/'TASK_INPUTS.json',{'schema_version':2,'tasks':[self.e]})
        self.write(self.e['report'],'# Fixture outcome\n')
        self.log=(g.OUTPUT/'fixture.log').as_posix();self.write(self.log,'fixture passed\n')
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
        p=self.root/'alias'
        try:p.symlink_to(self.root/self.report)
        except OSError as exc:self.skipTest(f'symlink creation not permitted on this host: {exc.__class__.__name__}')
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

    # Windows separators: str(PureWindowsPath) uses '\', which local() rejects; callers must pass as_posix().
    def windows_paths(self):
        return patch.multiple(g,DOC=PureWindowsPath(g.DOC.as_posix()),PREP=PureWindowsPath(g.PREP.as_posix()),
                              OUTPUT=PureWindowsPath(g.OUTPUT.as_posix()),CONTROL=PureWindowsPath(g.CONTROL.as_posix()))
    def test_windows_separator_paths_accepted(self):
        with self.windows_paths():
            self.assertIn('006',g.catalog(self.root))
            self.assertEqual(run_task_checks.run(self.root,'006'),0)
            self.packet['checks_sha256']=g.sha(self.root/g.OUTPUT.as_posix()/'006-checks.json');self.save()
            self.assertEqual(g.check(self.root,'006')['artifact_gate'],'passed')
    def test_backslash_value_still_rejected(self):
        with self.assertRaises(g.GateError):g.local(self.root,'docs\\plans\\x.json')

    # Reviewer gate: max, or evidence-backed frontier; unique, task-bound dispatches.
    def dispatch(self,name,session,task='006',inputs=None):
        path=(g.OUTPUT/'reviews'/task/name).as_posix()
        self.write_json(path,{'task_id':task,'session_id':session,
                              'reviewed_inputs':inputs if inputs is not None else [self.hashed(self.code)]})
        return {'session_id':session,'dispatch_evidence':path,'dispatch_sha256':g.sha(self.root/path)}
    def review(self,tier='max',model='claude-opus-5-5',escalation=None):
        self.e['requires_independent_review']=True
        self.write_json(g.DOC/'TASK_INPUTS.json',{'schema_version':2,'tasks':[self.e]})
        self.machine['input_fingerprint']=g.code_fingerprint(self.root,self.e)
        self.packet['reviewer']={'model_tier':tier,'fresh_context':True,'provider':'claude','model':model,
                                 'native_effort':'xhigh',**self.dispatch('dispatch.json','sess-review')}
        if escalation is not None:self.packet['reviewer']['escalation']=escalation
        self.packet.update({'reviewed_inputs':[self.hashed(self.code)],'verdict':'approved','findings':[]})
        self.machine_save()
    def failure(self,n,cls='semantic',cause='missed race in lock handoff',tier='max'):
        return {'model_tier':tier,'failure_class':cls,'cause':cause,**self.dispatch(f'failed-{n}.json',f'sess-max-{n}')}
    def frontier(self,**kw):
        failures=[self.failure(1,**kw),self.failure(2,**kw)]
        self.review('frontier','claude-fable-5-2',{'phase':'review','prior_max_failures':failures})
    def passes(self):self.assertEqual(g.check(self.root,'006')['artifact_gate'],'passed')
    def test_valid_max_review(self):self.review();self.passes()
    def test_valid_frontier_review(self):self.frontier();self.passes()
    def test_dispatch_outside_task_review_dir_rejected(self):
        self.review();rec=self.dispatch('dispatch.json','sess-review',task='008')
        self.packet['reviewer'].update(rec);self.save();self.reject()
    def test_dispatch_naming_other_task_rejected(self):
        self.review();path=self.packet['reviewer']['dispatch_evidence']
        self.write_json(path,{'task_id':'008','session_id':'sess-review','reviewed_inputs':[self.hashed(self.code)]})
        self.packet['reviewer']['dispatch_sha256']=g.sha(self.root/path);self.save();self.reject()
    def test_dispatch_without_reviewed_hashes_rejected(self):
        self.review();self.packet['reviewer'].update(self.dispatch('dispatch.json','sess-review',inputs=[]));self.save();self.reject()
    def test_reused_review_from_other_receipt_rejected(self):
        self.review();other=dict(self.e,id='008',output=(g.OUTPUT/'008-receipt.json').as_posix())
        self.write_json(g.DOC/'TASK_INPUTS.json',{'schema_version':2,'tasks':[self.e,other]})
        self.write_json(other['output'],{'reviewer':{'session_id':'sess-other','dispatch_sha256':self.packet['reviewer']['dispatch_sha256']}})
        self.reject()
        self.write_json(other['output'],{'reviewer':{'session_id':'sess-review','dispatch_sha256':'0'*64}})
        self.reject()
    def test_malformed_sibling_receipt_cannot_hide_reused_session(self):
        self.review()
        other=dict(self.e,id='008',output=(g.OUTPUT/'008-receipt.json').as_posix())
        self.write_json(g.DOC/'TASK_INPUTS.json',{'schema_version':2,'tasks':[self.e,other]})
        self.write(other['output'],'{"reviewer":{"session_id":"sess-review","session_id":"sess-another"}}')
        self.reject()
        self.write(other['output'],'{"reviewer":Infinity}')
        self.reject()
        (self.root/other['output']).unlink()
        # A missing, genuinely pending sibling task has no session to reuse.
        self.passes()
    def test_frontier_without_evidence_rejected(self):self.review('frontier','claude-fable-5-2');self.reject()
    def test_frontier_single_failure_rejected(self):
        self.review('frontier','gpt-6.2-astra',{'phase':'review','prior_max_failures':[self.failure(1)]});self.reject()
    def test_frontier_for_quota_rejected(self):self.frontier(cause='quota');self.reject()
    def test_frontier_for_availability_class_rejected(self):self.frontier(cls='environment');self.reject()
    def test_frontier_after_non_max_failures_rejected(self):self.frontier(tier='strong');self.reject()
    def test_frontier_for_implementation_rejected(self):
        self.frontier();self.packet['reviewer']['escalation']['phase']='implementation';self.save();self.reject()
    def test_frontier_wrong_model_rejected(self):
        self.frontier();self.packet['reviewer']['model']='claude-opus-5-5';self.save();self.reject()
    def test_frontier_reusing_failed_dispatch_rejected(self):
        self.frontier();f=self.packet['reviewer']['escalation']['prior_max_failures']
        f[1].update({k:f[0][k] for k in ('session_id','dispatch_evidence','dispatch_sha256')});self.save();self.reject()

    # review_dispatch.py evidence (fake provider executable, no model call) must satisfy check() as produced.
    def dispatched(self,**env):
        import review_dispatch_self_test as rt
        prev=dict(self.e,id='005',output=(g.OUTPUT/'005-receipt.json').as_posix(),report=(g.OUTPUT/'005-outcome.md').as_posix())
        self.e.update(requires_independent_review=True,review_of='005')
        self.write_json(g.DOC/'TASK_INPUTS.json',{'schema_version':2,'tasks':[prev,self.e]})
        self.write(prev['report'],'# Fixture 005 outcome\n')
        self.write_json(prev['output'],{'task_id':'005','changed_artifacts':[self.hashed(self.code)]})
        rt.write_plan(self.root,'006','005')
        out=rt.run_helper(self.root,'006',env={k:str(v) for k,v in env.items()})
        self.assertEqual(out.returncode,0,out.stderr)
        block=rt.receipt_block(out.stdout);evidence=g.load(self.root/block['reviewer']['dispatch_evidence'])
        findings=[dict(f,status='open') for f in g.load(self.root/evidence['findings_path'])['findings']]
        self.machine['input_fingerprint']=g.code_fingerprint(self.root,self.e)
        self.packet.update(reviewer=block['reviewer'],reviewed_inputs=block['reviewed_inputs'],verdict='approved',findings=findings)
        self.machine_save();return block
    def test_review_dispatch_evidence_accepted(self):
        block=self.dispatched();self.passes()
        self.assertEqual((block['reviewer']['model_tier'],block['reviewer']['fresh_context']),('max',True))
    def test_review_dispatch_open_blocking_finding_rejected(self):self.dispatched(FAKE_REVIEW_MODE='findings');self.reject()
    def test_review_dispatch_session_claimed_by_other_receipt_rejected(self):
        self.dispatched(FAKE_REVIEW_SESSION='sess-shared')
        other=dict(self.e,id='008',output=(g.OUTPUT/'008-receipt.json').as_posix())
        data=g.load(self.root/g.DOC/'TASK_INPUTS.json');data['tasks'].append(other)
        self.write_json(g.DOC/'TASK_INPUTS.json',data)
        self.write_json(other['output'],{'reviewer':{'session_id':'sess-shared','dispatch_sha256':'0'*64}})
        self.reject()
    def test_review_dispatch_stale_reviewed_input_rejected(self):
        self.dispatched();self.write(self.e['report'].replace('006','005'),'# changed after review\n');self.reject()


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
    def test_pinned_text_hash_ignores_crlf_only(self):
        # Pins are LF-blob hashes; a core.autocrlf=true checkout must still verify, any other byte change must not.
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);lf=b'# report\nline two\n';pin=g.hashlib.sha256(lf).hexdigest()
            (root/'r.md').write_bytes(lf.replace(b'\n',b'\r\n'))
            self.assertEqual(g.verified_files(root,[{'path':'r.md','sha256':pin}],'research',text=True),{'r.md'})
            with self.assertRaises(g.GateError):g.verified_files(root,[{'path':'r.md','sha256':pin}],'research')
            (root/'r.md').write_bytes(b'# report\r\nline 2\r\n')
            with self.assertRaises(g.GateError):g.verified_files(root,[{'path':'r.md','sha256':pin}],'research',text=True)
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
        def edit(d):next(t for t in d['tasks'] if t['id']==84)['title']='Create the second plan';return d
        self.changed('PLAN1_SPEC.json',edit)
    def test_missing_132_review_gate(self):
        def edit(d):t=next(t for t in d['tasks'] if t['id']==82);t['dependencies']=[x for x in t['dependencies'] if x!='132'];return d
        self.changed('PLAN1_SPEC.json',edit)
    def test_autostart_rejected(self):
        def edit(d):d['autostart']=True;return d
        self.changed('PLAN1_SPEC.json',edit)


if __name__=='__main__':unittest.main(verbosity=2)
