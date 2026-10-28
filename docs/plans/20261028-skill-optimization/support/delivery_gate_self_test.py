#!/usr/bin/env python3
"""Synthetic fixtures only: these tests do not constitute any real model review."""
import contextlib
import copy
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
import check_delivery as gate

class EvidenceGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        (self.root/gate.DOC).mkdir(parents=True)
        self.entry={'id':'001','kind':'research','output':'output.json','report':'report.md','review_of':None}
        (self.root/'input.txt').write_text('synthetic evidence')
        (self.root/'report.md').write_text('Synthetic test report, not an executed research task.')
        self.artifact={'path':'input.txt','sha256':hashlib.sha256((self.root/'input.txt').read_bytes()).hexdigest()}
        source={'id':'E001','title':'Fixture title','publisher':'Fixture publisher','url':'https://example.com/source','accessed_at':'2026-10-28','source_type':'official_documentation','checked_version':'fixture','finding':'Fixture evidence.','verification_scope':'synthetic test only'}
        self.packet={'schema_version':1,'task_id':'001','kind':'research','status':'completed','summary':'Synthetic packet for validator test only.',
          'evidence':[{'classification':'verified','claim':'Fixture assertion.','source_refs':['E001']}],
          'sources':[source,{**source,'id':'E002'}],'verified_artifacts':[self.artifact],
          'alternatives':[{'id':name,'costs':None,'benefits':['fixture'],'risks':['fixture'],'source_refs':['E001']} for name in ('current_baseline','candidate')],
          'decision':'Fixture decision.','evaluation':{'case':'fixture'},'unknowns':[],'proposed_changes':[]}
    def persist(self):
        (self.root/gate.DOC/'TASK_INPUTS.json').write_text(json.dumps({'tasks':[self.entry]}))
        (self.root/'output.json').write_text(json.dumps(self.packet))
    def run_gate(self):
        self.persist()
        with contextlib.redirect_stdout(io.StringIO()): gate.check(self.root,'001')
    def test_valid_synthetic_research_packet(self): self.run_gate()
    def test_missing_deliverable_rejected(self):
        self.persist();(self.root/'output.json').unlink()
        with self.assertRaises(gate.GateError): gate.check(self.root,'001')
    def test_stale_hash_rejected(self):
        self.packet['verified_artifacts'][0]['sha256']='0'*64
        with self.assertRaises(gate.GateError): self.run_gate()
    def test_path_escape_rejected(self):
        with self.assertRaises(gate.GateError): gate.local(self.root,'../private.txt')
    def test_credential_rejected(self):
        self.packet['summary']='Authorization: Bearer PLANTED_TEST_TOKEN_ONLY'
        with self.assertRaises(gate.GateError): self.run_gate()
    def test_unresolved_source_rejected(self):
        self.packet['evidence'][0]['source_refs']=['E999']
        with self.assertRaises(gate.GateError): self.run_gate()
    def test_no_baseline_alternative_rejected(self):
        self.packet['alternatives']=self.packet['alternatives'][1:]
        with self.assertRaises(gate.GateError): self.run_gate()
    def test_real_review_requires_capability_evidence(self):
        self.entry['kind']='review';self.packet['kind']='review'
        self.packet.update(reviewer={'provider':'codex','model':'fixture-only','model_tier':'max','native_effort':'xhigh','fresh_context':True,'session_id':'fixture'},verdict='approved',findings=[],reviewed_inputs=[self.artifact])
        with self.assertRaises(gate.GateError): self.run_gate()
    def test_low_tier_review_rejected(self):
        self.entry['kind']='review';self.packet['kind']='review'
        self.packet['reviewer']={'model_tier':'standard','fresh_context':True}
        with self.assertRaises(gate.GateError): self.run_gate()
    def test_new_implementation_failure_rejected(self):
        self.entry['kind']='implementation';self.packet['kind']='implementation'
        self.packet['validation_results']=[{'command':'synthetic failing test','exit_code':1,'log_path':'input.txt'}]
        with self.assertRaises(gate.GateError): self.run_gate()
    def test_symlink_rejected(self):
        try: (self.root/'link').symlink_to(self.root/'input.txt')
        except OSError: self.skipTest('No symlink support')
        with self.assertRaises(gate.GateError): gate.local(self.root,'link')

if __name__=='__main__': unittest.main()
