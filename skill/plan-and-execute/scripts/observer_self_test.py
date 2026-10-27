#!/usr/bin/env python3
"""Offline trust-boundary and quota-fallback tests. No paid provider invocation."""
from __future__ import annotations

import copy
import hashlib
import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import assistant_triage
import observer
import planctl
import routing_config
import validatectl
import workload_routing

ADVICE = {'suggested_class':'semantic','confidence':.8,'hypothesis':'The mapped test stopped progressing.', 'evidence_refs':['E1']}
PROMPT = assistant_triage.SYSTEM + '{"evidence":{"E1":"ERROR test blocked"}}'
SIGNATURE = hashlib.sha256(PROMPT.encode()).hexdigest()


def configuration():
    config = routing_config.merge(planctl.default_config(), routing_config.EXTRA_DEFAULTS)
    config['observer'] = {'enabled':True}
    section = workload_routing.antigravity_preset(['gemini-3.8-flash-medium','claude-opus-5-5-high'])
    # A distinct explicitly qualified monitoring profile tests same-host fallback.
    section = section.get('workload_routing', section)
    flash = copy.deepcopy(section['profiles']['agy-flash-monitor'])
    second = copy.deepcopy(flash)
    second.update(model='claude-opus-5-5-high', observed_models=['claude-opus-5-5-high'],
                  quota_pool='antigravity-claude-gpt', native_effort='high', max_effort='high')
    third = copy.deepcopy(flash)
    third.update(provider='claude', model='haiku', observed_models=['haiku'],
                 quota_pool='claude-api', native_effort='low', max_effort='low')
    section['profiles'].update(second=second, native_claude=third)
    section['routes']['log_monitoring']=['agy-flash-monitor','second','native_claude']
    config['workload_routing']=section
    routing_config.validate(config)
    return config


class ObserverTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name).resolve();self.path=self.root/'observer.json'
        self.config=configuration()

    def diagnose(self,invoke,signature=SIGNATURE):
        return observer.diagnose(self.config,PROMPT,{'E1'},signature,self.path,invoke=invoke)

    def test_disabled_and_no_profiles_do_not_dispatch(self):
        with patch.object(observer,'native_invoke') as invoke:
            self.config['observer']['enabled']=False
            self.assertEqual(self.diagnose(invoke)['reason'],'disabled')
            self.config['observer']['enabled']=True
            self.config['workload_routing']['enabled']=False
            self.assertEqual(self.diagnose(invoke)['reason'],'no_monitoring_profiles')
        invoke.assert_not_called();self.assertFalse(self.path.exists())

    def test_flash_first_even_with_claude_manager_preservation(self):
        seen=[]
        def invoke(config,route,prompt,refs,timeout):
            seen.append(route);return ADVICE
        result=self.diagnose(invoke)
        self.assertEqual(result['status'],'advice')
        self.assertEqual(seen[0]['model'],'gemini-3.8-flash-medium')
        self.assertFalse(result['authoritative'])
        self.assertEqual(self.diagnose(invoke)['reason'],'duplicate_evidence')
        self.assertEqual(self.diagnose(invoke,'1'*64)['reason'],'attempt_budget')
        self.assertEqual(len(seen),1)
        self.assertNotIn('ERROR test blocked',self.path.read_text())

    def test_quota_falls_to_other_family_same_host(self):
        seen=[]
        def invoke(config,route,prompt,refs,timeout):
            seen.append(route)
            if len(seen)==1:raise observer.Unavailable('quota',submitted=True)
            return ADVICE
        self.assertEqual(self.diagnose(invoke)['status'],'advice')
        self.assertEqual([r['provider'] for r in seen],['antigravity','antigravity'])
        self.assertNotEqual(seen[0]['quota_pool'],seen[1]['quota_pool'])
        self.assertEqual([r['tier'] for r in seen],['economy','economy'])

    def test_authentication_skips_entire_host(self):
        seen=[]
        def invoke(config,route,*args):
            seen.append(route['provider'])
            if route['provider']=='antigravity':raise observer.Unavailable('authentication')
            return ADVICE
        self.assertEqual(self.diagnose(invoke)['status'],'advice')
        self.assertEqual(seen,['antigravity','claude'])

    def test_invalid_advice_fallback_does_not_mutate_routes_or_approve(self):
        original=copy.deepcopy(self.config);seen=[]
        def invoke(config,route,*args):
            seen.append(route)
            return {'run':'rm -rf /','passed':True} if len(seen)==1 else ADVICE
        self.assertEqual(self.diagnose(invoke)['status'],'advice')
        self.assertEqual(self.config,original)
        self.assertEqual(len(seen),2)
        self.assertNotIn('rm -rf',self.path.read_text())

    def test_interruption_reservation_prevents_rebilling(self):
        def invoke(*args):raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):self.diagnose(invoke)
        self.assertEqual(self.diagnose(lambda *x:ADVICE)['reason'],'duplicate_evidence')
        self.assertEqual(observer.load_state(self.path)['requests'][0]['status'],'interrupted')

    def test_budget_timeout_and_corrupt_state_fail_closed(self):
        self.config['observer']['max_candidates']=1
        out=self.diagnose(lambda *x: (_ for _ in ()).throw(observer.Unavailable('timeout')))
        self.assertEqual(len(out['attempts']),1)
        self.path.write_text('{"version":1,"version":2}')
        with self.assertRaises(ValueError):self.diagnose(lambda *x:ADVICE)
        for field,value in [('enabled','yes'),('max_calls',0),('max_candidates',4),('timeout_seconds',True),('unknown',1)]:
            with self.assertRaises(observer.ObserverError):observer.validate({field:value})

    def test_no_live_model_or_implicit_billing_for_unsupported_adapter(self):
        route=observer.routes(self.config)[0]
        with patch.object(assistant_triage,'native_invoke') as invoke:
            with self.assertRaisesRegex(observer.Unavailable,'billing'):
                observer.native_invoke(self.config,{**route,'provider':'claude'},PROMPT,{'E1'},10)
            invoke.assert_not_called()
        with self.assertRaisesRegex(observer.Unavailable,'unsupported'):
            observer.native_invoke(self.config,{**route,'provider':'codex'},PROMPT,{'E1'},10)

    def test_environment_excludes_api_keys_and_code_injection_options(self):
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY':'secret','GOOGLE_API_KEY':'secret','NODE_OPTIONS':'-r exploit','AGY_CONFIG':'evil'}):
            env=observer.clean_environment(self.root,cached_auth=True)
        for key in ('ANTHROPIC_API_KEY','GOOGLE_API_KEY','NODE_OPTIONS','AGY_CONFIG'):
            self.assertNotIn(key,env)

    def test_startup_customizations_are_rejected_without_modification(self):
        observer.agy_startup_guard(self.root)
        folder=self.root/'.gemini/config';folder.mkdir(parents=True)
        f=folder/'hooks.json';f.write_text('{"h":{"SessionStart":[{"command":"unsafe"}]}}')
        with self.assertRaises(observer.Unavailable):observer.agy_startup_guard(self.root)
        self.assertIn('unsafe',f.read_text())
        f.write_text('{}');observer.agy_startup_guard(self.root)
        plugins=folder/'plugins';plugins.mkdir();(plugins/'sample').mkdir()
        with self.assertRaises(observer.Unavailable):observer.agy_startup_guard(self.root)

    def fake(self,mode):
        program=self.root/'fake.py'
        program.write_text('''import sys,json,os,time
from pathlib import Path
mode=sys.argv[1]
init={'cwd':os.getcwd(),'tools':[],'permission_mode':'request-review','model':'m','agent':'a'}
if mode=='tools':init['tools']=['run_command']
if mode=='wrong_model':init['model']='other'
if mode=='wrong_cwd':init['cwd']='/'
if mode=='malformed':print('not-json',flush=True)
else:print(json.dumps({'event':'init','init':init}),flush=True)
if mode=='blocked_input':time.sleep(30)
line=sys.stdin.readline()
if line:Path('received.txt').write_text(line)
if mode=='timeout':time.sleep(30)
if mode=='overflow':print('x'*40000,flush=True);time.sleep(30)
if mode=='tool_event':print(json.dumps({'event':'step_update','step_update':{'step_type':'tool'}}),flush=True)
result={'status':'SUCCESS','structured_output':{'suggested_class':'semantic','confidence':.8,'hypothesis':'The mapped test stopped progressing.','evidence_refs':['E1']}}
if mode=='quota':result={'status':'ERROR','response':'quota exceeded'}
print(json.dumps({'event':'result','result':result}),flush=True)
time.sleep(30)
''')
        return [sys.executable,'-u',str(program),mode]

    def stream(self,mode,timeout=2):
        return observer.agy_stream(self.fake(mode),PROMPT,self.root,dict(os.environ),'m','a',timeout)

    def test_blocked_input_pipe_does_not_escape_total_deadline(self):
        start=time.monotonic()
        with self.assertRaisesRegex(observer.Unavailable,'timeout'):
            observer.agy_stream(self.fake('blocked_input'),'x'*200000,self.root,dict(os.environ),'m','a',.5)
        self.assertLess(time.monotonic()-start,5)
        self.assertFalse((self.root/'received.txt').exists())

    def test_malformed_persisted_attempt_cannot_reset_observer_budget(self):
        self.path.write_text(json.dumps({'version':1,'requests':[{
            'signature':SIGNATURE,'status':'reserved','attempts':'unsafe','failure_counter':0}]}))
        with patch.object(observer,'native_invoke') as invoke:
            with self.assertRaises(observer.ObserverError):self.diagnose(invoke)
        invoke.assert_not_called()

    def test_real_stream_waits_for_verified_init_before_sending(self):
        self.assertEqual(self.stream('ok'),ADVICE)
        record=json.loads((self.root/'received.txt').read_text())
        self.assertEqual(record['message']['content'],PROMPT)

    def test_real_stream_unsafe_init_gets_no_evidence(self):
        for mode in ('tools','wrong_model','wrong_cwd','malformed'):
            with self.subTest(mode=mode),self.assertRaises(observer.Unavailable):self.stream(mode)
            self.assertFalse((self.root/'received.txt').exists())

    def test_real_stream_tool_attempt_and_overflow_fail_closed(self):
        for mode in ('tool_event','overflow','quota'):
            with self.subTest(mode=mode),self.assertRaises(observer.Unavailable):self.stream(mode)

    def test_real_stream_timeout_kills_owned_process(self):
        start=time.monotonic()
        with self.assertRaisesRegex(observer.Unavailable,'timeout'):self.stream('timeout',.4)
        self.assertLess(time.monotonic()-start,5)

    def test_plan_observer_stays_separate_from_manifest_and_existing_advisor(self):
        (self.root/'results').mkdir()
        task={'id':'001','functional_failures':1,'validation_stagnation':{'repeats':2},'last_error':'failed'}
        results=[{'passed':False,'command':'tests','output_tail':'ERROR blocked','exit_code':1}]
        with patch.object(observer,'native_invoke',return_value=ADVICE) as invoke:
            result=assistant_triage.triage(self.root,task,results,self.config)
        self.assertEqual(result['status'],'advice');invoke.assert_called_once()
        self.assertIn('Unverified',assistant_triage.hint(self.root,task,self.config))
        task['functional_failures']=2
        self.assertEqual(assistant_triage.hint(self.root,task,self.config),'')
        self.assertFalse((self.root/'manifest.json').exists())

    def test_standalone_advice_is_explicit_consumes_delta_and_preserves_result(self):
        import contextlib
        import io
        dest=validatectl.directory(self.root,'TEST',create=True)
        (dest/'run-1.log').write_text('ERROR blocked token=sk-secretvalue123\n')
        state={'status':'failed','receipt':{'run_id':'1','log':'run-1.log','exit_code':1}}
        validatectl.atomic(dest/'state.json',state)
        config_path=self.root/'observer-test.json';config_path.write_text(json.dumps(self.config))
        result=[]
        with patch.object(observer,'native_invoke',return_value=ADVICE) as invoke:
            for unused in range(2):
                text=io.StringIO()
                with contextlib.redirect_stdout(text):
                    code=validatectl.main(['advise','--repo-root',str(self.root),'--validation','TEST','--config',str(config_path)])
                self.assertEqual(code,0)
                result.append(json.loads(text.getvalue()))
            invoke.assert_called_once()
            self.assertNotIn('sk-secretvalue123',invoke.call_args.args[2])
        self.assertEqual(result[0]['status'],'advice')
        self.assertEqual(result[1]['reason'],'no_new_evidence')
        self.assertEqual(validatectl.read_json(dest/'state.json'),state)

    def test_symlink_state_is_not_written(self):
        outside=self.root/'outside';outside.write_text('keep')
        try:self.path.symlink_to(outside)
        except (OSError,NotImplementedError):self.skipTest('symlinks unavailable')
        with self.assertRaises(observer.ObserverError):self.diagnose(lambda *x:ADVICE)
        self.assertEqual(outside.read_text(),'keep')

if __name__=='__main__':unittest.main()
