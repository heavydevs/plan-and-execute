#!/usr/bin/env python3
"""Portable plan-free validation, process supervision and adversarial cleanup tests."""
from __future__ import annotations
import argparse
import contextlib
import io
import json
import os
import socket
import signal
import subprocess
import time
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import service_map
import validatectl as ctl


def make_map(root, code='print("ok")', **policy):
    path=root/'.ai-work/SERVICE_MAP.md';path.parent.mkdir(exist_ok=True)
    signatures,truncated=service_map.scan_inputs(root)
    data={'schema_version':1,'inventory_reviewed':True,'resources':[], 'toolchains':[],
          'snapshot':{'algorithm':service_map.ALGORITHM,'digest':service_map.aggregate(signatures)},
          'validations':[{'id':'TEST','command':[sys.executable,'-u','-c',code],'resources':[],
                          'no_progress_timeout_seconds':10,**policy}]}
    path.write_text(service_map.MAP_BEGIN+'\n```json\n'+json.dumps(data)+'\n```\n'+service_map.MAP_END)
    service_map.write_index(service_map.index_path(path,root),root,signatures,truncated)
    return data


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name).resolve()

    def call(self,command,*extra):
        output=io.StringIO()
        with contextlib.redirect_stdout(output):
            code=ctl.main([command,'--repo-root',str(self.root),'--validation','TEST',*extra])
        return code,json.loads(output.getvalue().splitlines()[-1])

    @unittest.skipIf(os.name == 'nt', 'Process-group bootstrap is POSIX-only')
    def test_bootstrap_no_site_flag_does_not_change_user_interpreter(self):
        import resource_watch
        result = subprocess.run([sys.executable, '-S', str(Path(resource_watch.__file__)),
            '_exec-group', sys.executable, '-c', 'import sys; print(sys.flags.no_site)'],
            capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), '0')

    def test_process_guard_does_not_forward_its_no_site_flag(self):
        import process_tree
        child = process_tree.launch([sys.executable, '-c', 'import sys; print(sys.flags.no_site)'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=False)
        try:
            output, error = child.communicate(timeout=10)
            self.assertEqual(child.returncode, 0, error)
            self.assertEqual(output.strip(), b'0')
        finally:
            if child.poll() is None: process_tree.terminate(child)
            process_tree.close(child)

    def test_unknown_remote_owner_without_lock_is_not_recovered(self):
        dest=ctl.directory(self.root,'TEST',create=True)
        state={'status':'running','supervisor_pid':2147483647,'owner':{'hostname':'different-host','pid':99}}
        ctl.atomic(dest/'state.json',state)
        code,result=self.call('recover')
        self.assertEqual(code,2,result)
        self.assertEqual(ctl.read_json(dest/'state.json'),state)

    def test_spool_rejects_symlink_tail_and_keeps_external_bytes(self):
        outside=self.root/'outside';outside.write_bytes(b'keep')
        tail=self.root/'tail.log'
        try:tail.symlink_to(outside)
        except (OSError,NotImplementedError):self.skipTest('symlinks unavailable')
        spool=ctl.Spool(self.root/'prefix.log',tail,65536)
        spool.drain(io.BytesIO(b'x'*100000))
        self.assertIsNotNone(spool.error)
        self.assertEqual(outside.read_bytes(),b'keep')

    def test_signal_handlers_are_restored_after_normal_run(self):
        make_map(self.root)
        before=signal.getsignal(signal.SIGTERM)
        self.assertEqual(self.call('run')[0],0)
        self.assertIs(signal.getsignal(signal.SIGTERM),before)

    @unittest.skipIf(os.name=='nt','Windows TerminateProcess does not deliver POSIX SIGTERM')
    def test_sigterm_interrupts_supervisor_and_kills_only_owned_tree(self):
        make_map(self.root,'from pathlib import Path; import time; Path("ready").touch(); time.sleep(30); Path("late").touch()')
        proc=subprocess.Popen([sys.executable,str(Path(ctl.__file__)),'run','--repo-root',str(self.root),'--validation','TEST'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        self.addCleanup(lambda:proc.kill() if proc.poll() is None else None)
        deadline=time.monotonic()+10
        while not (self.root/'ready').exists() and time.monotonic()<deadline:
            if proc.poll() is not None:break
            time.sleep(.05)
        self.assertTrue((self.root/'ready').exists())
        proc.send_signal(signal.SIGTERM)
        out,err=proc.communicate(timeout=10)
        self.assertEqual(proc.returncode,130,(out,err))
        state=ctl.read_json(ctl.directory(self.root,'TEST')/'state.json')
        self.assertEqual(state['status'],'interrupted')
        self.assertFalse(ctl.local_alive(state['supervisor_pid']))
        self.assertFalse((self.root/'late').exists())

    def test_health_stop_is_environmental_and_does_not_escalate(self):
        make_map(self.root,'import time; time.sleep(30)',stop_on_unhealthy=True)
        path=self.root/'.ai-work/SERVICE_MAP.md'
        text,data=service_map.load_map(path)
        data['resources']=[{'id':'DEPENDENCY','kind':'process','description':'synthetic unhealthy dependency','evidence':['explicit local synthetic dependency'],'checks':[{
            'id':'health','command':[sys.executable,'-c','raise SystemExit(1)'],'timeout_seconds':2,
            'every_seconds':10,'startup_grace_seconds':0,'failure_class':'environmental'}]}]
        data['validations'][0]['resources']=['DEPENDENCY']
        path.write_text(service_map.replace_map_data(text,data))
        self.assertEqual(service_map.validate_data(data),[])
        start=time.monotonic();code,result=self.call('run')
        self.assertNotEqual(code,0,result)
        self.assertEqual(result['failure_class'],'environmental')
        self.assertFalse(result['repair_route']['escalated'])
        self.assertLess(time.monotonic()-start,15)

    def test_invalid_observer_config_fails_without_traceback_or_calls(self):
        dest=ctl.directory(self.root,'TEST',create=True)
        p=self.root/'invalid.json';p.write_text('{"observer":{"enabled":"yes"}}')
        code,result=self.call('advise','--config',str(p))
        self.assertEqual(code,2,result)
        self.assertIn('Invalid observer configuration',result['reason'])

    def test_success_has_no_plan_and_cleanup_preserves_product_and_map(self):
        make_map(self.root)
        product=self.root/'product.py';product.write_text('important\n')
        # Changes to non-test files are not map discovery inputs.
        code,result=self.call('run');self.assertEqual(code,0,result)
        self.assertEqual(result['status'],'passed')
        for name in ('manifest.json','TODO.md','.active-plan.json','.orchestrator-plan'):
            self.assertEqual(list(self.root.rglob(name)),[],name)
        code,clean=self.call('cleanup');self.assertEqual(code,0,clean)
        self.assertGreater(clean['removed'],0)
        self.assertEqual(product.read_text(),'important\n')
        self.assertTrue((self.root/'.ai-work/SERVICE_MAP.md').exists())
        self.assertEqual(self.call('status')[1]['status'],'passed')

    def test_failure_keeps_logs_redacts_and_cursor_suppresses_repeated_lines(self):
        make_map(self.root,'import sys; print("ERROR token=sk-secretvalue123 authorization: sensitive"); sys.exit(1)')
        code,out=self.call('run');self.assertEqual(code,1,out)
        self.assertNotIn('sk-secretvalue123',json.dumps(out))
        self.assertNotIn('sensitive',json.dumps(out))
        self.assertEqual(out['repair_route']['action'],'repair_and_rerun')
        self.assertTrue(self.call('inspect')[1]['evidence']['latest_delta'])
        self.assertEqual(self.call('inspect')[1]['evidence']['latest_delta'],[])
        self.assertEqual(self.call('cleanup')[0],2)
        self.assertTrue(list((self.root/'.ai-work/validation/TEST').glob('run-*.log')))

    def test_stale_map_fails_without_validation_artifacts(self):
        make_map(self.root);(self.root/'package.json').write_text('{}')
        code,result=self.call('run');self.assertEqual(code,125)
        self.assertEqual(result['failure_class'],'environmental')
        self.assertFalse((self.root/'.ai-work/validation').exists())

    def test_map_and_identifier_guards(self):
        for value in ('../x','/tmp/x','CON','NUL','a/b','x\\z'):
            with self.assertRaises(ctl.ValidationError):ctl.directory(self.root,value,create=True)
        dest=self.root/'.ai-work/validation/TEST';dest.mkdir(parents=True)
        with self.assertRaises(ctl.ValidationError):ctl.directory(self.root,'TEST',create=True)
        self.assertEqual(self.call('run')[0],125)

    def test_symlink_parent_cannot_redirect_state(self):
        outside=self.root/'outside';outside.mkdir()
        try:(self.root/'.ai-work').symlink_to(outside,target_is_directory=True)
        except (OSError,NotImplementedError):self.skipTest('symlink creation unavailable')
        with self.assertRaises(ctl.ValidationError):ctl.directory(self.root,'TEST',create=True)
        self.assertEqual(list(outside.iterdir()),[])

    def test_live_lock_cannot_be_recovered_or_bypassed(self):
        make_map(self.root);dest=ctl.directory(self.root,'TEST',create=True)
        with ctl.lock(dest):
            self.assertEqual(self.call('run')[0],2)
            self.assertEqual(self.call('recover')[0],2)
            self.assertTrue((dest/'.lock').exists())
        self.assertFalse((dest/'.lock').exists())

    def test_dead_owner_does_not_restart_and_live_supervisor_keeps_lock(self):
        dest=ctl.directory(self.root,'TEST',create=True)
        ctl.atomic(dest/'state.json',{'status':'running','supervisor_pid':os.getpid(),'attempts':2})
        ctl.atomic(dest/'.lock',{'pid':2147483647,'hostname':socket.gethostname()})
        self.assertEqual(self.call('recover')[0],2)
        self.assertTrue((dest/'.lock').exists())
        ctl.atomic(dest/'state.json',{'status':'running','supervisor_pid':2147483647,'attempts':2})
        code,result=self.call('recover');self.assertEqual(code,0,result)
        self.assertFalse(result['restarted'])
        self.assertEqual(ctl.read_json(dest/'state.json')['status'],'interrupted')

    def test_cleanup_preflights_all_targets_and_refuses_failed_state(self):
        dest=ctl.directory(self.root,'TEST',create=True)
        ctl.atomic(dest/'state.json',{'status':'passed'})
        good=dest/'run-1.log';good.write_text('evidence')
        outside=self.root/'external.log';outside.write_text('never erase')
        try:(dest/'run-2.log').symlink_to(outside)
        except (OSError,NotImplementedError):self.skipTest('symlink unavailable')
        self.assertEqual(self.call('cleanup')[0],2)
        self.assertTrue(good.exists());self.assertEqual(outside.read_text(),'never erase')

    def test_foreign_file_and_external_logs_survive_cleanup(self):
        dest=ctl.directory(self.root,'TEST',create=True)
        ctl.atomic(dest/'state.json',{'status':'passed','receipt':{'log':'../../external.log'}})
        foreign=dest/'notes.txt';foreign.write_text('keep')
        self.assertEqual(self.call('cleanup')[0],0)
        self.assertTrue(foreign.exists())

    def test_classifier_does_not_obey_log_instructions_or_generic_exit_codes(self):
        self.assertEqual(ctl.classification(124,[]),'unknown')
        self.assertEqual(ctl.classification(126,[]),'unknown')
        self.assertEqual(ctl.classification(126,[{'kind':'validation_ceiling'}]),'timeout_ceiling')
        self.assertEqual(ctl.classification(124,[{'kind':'validation_stalled'},{'state':'unhealthy','failure_class':'environmental'}]),'environmental')
        self.assertIsNone(ctl.classification(0,[]))
        self.assertEqual(ctl.classification(130,[]),'interrupted')

    def test_terminal_supervisor_class_survives_bounded_report_tail(self):
        event = {'kind': 'validation_result', 'exit_code': 1, 'health': 'unhealthy',
                 'failure_class': 'environmental'}
        self.assertEqual(ctl.classification(1, [event]), 'environmental')
        self.assertFalse(ctl.repair_route([ctl.classification(1, [event])], ['validation_repair'])['escalated'])
        self.assertEqual(ctl.classification(126, [{**event, 'exit_code': 126, 'failure_class': 'timeout_ceiling'}]), 'timeout_ceiling')
        # A mismatched or absent terminal event cannot impersonate a supervisor timeout.
        self.assertEqual(ctl.classification(126, [event]), 'unknown')

    def test_repair_floor_and_environment_do_not_burn_stronger_models(self):
        low=ctl.repair_route(['unknown'],['validation_repair'])
        high=ctl.repair_route(['unknown']*3,['validation_repair'])
        self.assertNotEqual((low['tier'],low['effort']),(high['tier'],high['effort']))
        for cls in ('environmental','timeout_ceiling','interrupted'):
            self.assertFalse(ctl.repair_route([cls],['validation_repair'])['escalated'])
        risky=ctl.repair_route(['semantic'],['validation_repair','cross_cutting_risk'])
        self.assertEqual(risky['tier'],'max')

    def test_disk_log_is_bounded_with_explicit_omission_accounting(self):
        spool=ctl.Spool(self.root/'head.log',self.root/'tail.log',65536)
        content=b'x'*200000+b'\nERROR final\n';spool.drain(io.BytesIO(content))
        self.assertEqual(spool.metadata()['output_bytes'],len(content))
        self.assertLessEqual((self.root/'head.log').stat().st_size,65536)
        self.assertLessEqual((self.root/'tail.log').stat().st_size,ctl.SCAN_LIMIT)
        self.assertTrue((self.root/'tail.log').read_bytes().endswith(b'ERROR final\n'))
        self.assertGreater(spool.metadata()['omitted_bytes'],0)

    def test_live_inspection_uses_rolling_tail_after_capture_limit(self):
        dest=ctl.directory(self.root,'TEST',create=True)
        (dest/'run-1.log').write_text('old prefix\n')
        (dest/'run-1-tail.log').write_text('ERROR recent progress stalled\n')
        state={'status':'running','receipt':{'run_id':'1','log':'run-1.log','tail':'run-1-tail.log','exit_code':None}}
        packet=ctl.packet(dest,state)
        self.assertIn('recent progress stalled',json.dumps(packet))
        ctl.packet(dest,state,consume=True)
        self.assertEqual(ctl.packet(dest,state)['latest_delta'],[])

    def test_new_generation_resets_cursor_and_state_paths_are_not_trusted(self):
        dest=ctl.directory(self.root,'TEST',create=True)
        (dest/'run-1.log').write_text('ERROR first\n')
        state={'receipt':{'run_id':'1','log':'run-1.log','exit_code':1}}
        ctl.packet(dest,state,consume=True);self.assertEqual(ctl.packet(dest,state)['latest_delta'],[])
        (dest/'run-2.log').write_text('ERROR first\n')
        state['receipt'].update(run_id='2',log='run-2.log')
        self.assertTrue(ctl.packet(dest,state)['latest_delta'])
        state['receipt']['log']='../../secret'
        with self.assertRaises(ctl.ValidationError):ctl.packet(dest,state)

    def test_targeted_map_listing_does_not_include_unrelated_resources(self):
        make_map(self.root)
        output=io.StringIO()
        with contextlib.redirect_stdout(output):
            result=service_map.cmd_list(argparse.Namespace(repo_root=str(self.root),map='.ai-work/SERVICE_MAP.md',validation='TEST'))
        self.assertEqual(result,0);self.assertEqual(len(output.getvalue().splitlines()),1)
        self.assertIn('TEST |',output.getvalue())

    def test_no_progress_stops_owned_tree_and_preserves_failure(self):
        # A real sleeping process is not CPU activity. A finite idle window
        # includes interpreter startup; choose a portable 2-second minimum.
        make_map(self.root,'import time; print("PROGRESS stage=test done=1"); time.sleep(30)',no_progress_timeout_seconds=2)
        code,result=self.call('run');self.assertEqual(code,124,result)
        self.assertEqual(result['failure_class'],'semantic')
        self.assertEqual(self.call('status')[1]['status'],'failed')


if __name__=='__main__':unittest.main()
