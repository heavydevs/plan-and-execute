#!/usr/bin/env python3
"""Offline Jev transport and integration tests; no authenticated request is sent."""
from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import Mock, patch

import assistant_jev as j
import assistant_triage as a
import planctl
import routing_config


class Response:
    def __init__(self, value):
        self.data = json.dumps(value).encode()
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self, size=-1): return self.data[:size]


def response(choice='environmental', confidence=.9, input_tokens=123):
    probs = {name: 0.0 for name in j.CLASSES}
    probs[choice] = confidence
    remainder = 1.0 - confidence
    if choice != 'unknown': probs['unknown'] += remainder
    else: probs['semantic'] += remainder
    return {
        'model': 'jev-1.13.0',
        'answers': {'failure_class': {'type': 'choice', 'choice': choice,
                                      'probabilities': probs, 'confidence': confidence}},
        'usage': {'input_tokens': input_tokens, 'output_tokens': 7},
    }


class JevTests(unittest.TestCase):
    def test_fixed_endpoint_choice_and_no_key_in_body(self):
        seen = {}
        def open_fn(req, timeout):
            seen['url'] = req.full_url
            seen['headers'] = dict(req.header_items())
            seen['payload'] = json.loads(req.data)
            seen['timeout'] = timeout
            return Response(response())
        result = j.invoke(state='bounded evidence', api_key='secret-key', open_fn=open_fn)
        self.assertEqual(seen['url'], j.API_URL)
        self.assertEqual(seen['payload']['model'], 'jev-1.13.0')
        self.assertEqual(seen['payload']['questions']['failure_class']['type'], 'choice')
        self.assertEqual(set(seen['payload']['questions']['failure_class']['criteria']), set(j.CLASSES))
        self.assertNotIn('secret-key', json.dumps(seen['payload']))
        self.assertEqual(result['choice'], 'environmental')
        self.assertEqual(result['input_tokens'], 123)

    def test_quota_rate_auth_redirect_and_network_fail_open(self):
        for code, reason in [(401, 'typesafe_auth_unavailable'), (402, 'typesafe_credit_or_access_unavailable'),
                             (403, 'typesafe_credit_or_access_unavailable'), (429, 'typesafe_capacity_unavailable'),
                             (529, 'typesafe_capacity_unavailable'), (302, 'redirect_rejected'),
                             (422, 'typesafe_request_rejected'), (500, 'typesafe_http_error')]:
            def fail(req, timeout, code=code):
                raise urllib.error.HTTPError(req.full_url, code, 'x', {}, io.BytesIO(b''))
            with self.subTest(code=code), self.assertRaisesRegex(j.JevUnavailable, reason):
                j.invoke(state='x', api_key='key', open_fn=fail)
        with self.assertRaisesRegex(j.JevUnavailable, 'typesafe_network_unavailable'):
            j.invoke(state='x', api_key='key', open_fn=lambda *x: (_ for _ in ()).throw(urllib.error.URLError('offline')))

    def test_malformed_probability_and_usage_are_rejected(self):
        bad = response(); bad['answers']['failure_class']['probabilities'] = {'semantic': 1.0}
        with self.assertRaisesRegex(j.JevUnavailable, 'invalid_response'):
            j.invoke(state='x', api_key='key', open_fn=lambda *_: Response(bad))
        bad = response(); bad['usage']['input_tokens'] = -1
        with self.assertRaisesRegex(j.JevUnavailable, 'invalid_response'):
            j.invoke(state='x', api_key='key', open_fn=lambda *_: Response(bad))

    def test_triage_missing_key_is_zero_call_zero_ledger(self):
        with tempfile.TemporaryDirectory() as d:
            plan = Path(d); (plan/'results').mkdir()
            cfg = routing_config.merge(planctl.default_config(), routing_config.EXTRA_DEFAULTS)
            cfg['assistant'].update(enabled=True, provider='jev')
            task = {'id':'001','functional_failures':2,'last_error':'x',
                    'validation_stagnation':{'signature':'a'*64,'repeats':2}}
            results = [{'passed':False,'command':'pytest','exit_code':1,'output_tail':'assert failed'}]
            with patch.dict(os.environ, {}, clear=True), patch.object(j, 'invoke') as call:
                out = a.triage(plan, task, results, cfg)
            self.assertEqual(out, {'status':'skipped','reason':'typesafe_api_key_required'})
            call.assert_not_called()
            self.assertEqual(list((plan/'results').iterdir()), [])

    def test_low_confidence_consumes_one_reserved_call_but_never_reaches_worker(self):
        with tempfile.TemporaryDirectory() as d:
            plan = Path(d); (plan/'results').mkdir()
            cfg = routing_config.merge(planctl.default_config(), routing_config.EXTRA_DEFAULTS)
            cfg['assistant'].update(enabled=True, provider='jev', jev_min_confidence=.6)
            task = {'id':'001','functional_failures':2,'last_error':'x',
                    'validation_stagnation':{'signature':'a'*64,'repeats':2}}
            results = [{'passed':False,'command':'pytest','exit_code':1,'output_tail':'ambiguous failure'}]
            fake = {'choice':'semantic','confidence':.4,'probabilities':{x:(.4 if x=='semantic' else .6 if x=='unknown' else 0) for x in j.CLASSES},
                    'model':'jev-1.13.0','input_tokens':77,'output_tokens':4}
            with patch.dict(os.environ, {'TYPESAFE_API_KEY':'unit-only'}, clear=True), patch.object(j, 'invoke', return_value=fake):
                out = a.triage(plan, task, results, cfg)
            self.assertEqual(out['status'], 'skipped')
            self.assertEqual(out['reason'], 'low_confidence')
            self.assertEqual(out['input_tokens'], 77)
            self.assertEqual(a.hint(plan, task, cfg), '')

    def test_plan_budget_bounds_many_tasks(self):
        with tempfile.TemporaryDirectory() as d:
            plan = Path(d); (plan/'results').mkdir()
            cfg = routing_config.merge(planctl.default_config(), routing_config.EXTRA_DEFAULTS)
            cfg['assistant'].update(enabled=True, provider='jev', max_calls_per_task=1, max_calls_per_plan=1)
            advice = {'suggested_class':'semantic','confidence':.9,'hypothesis':'bounded','evidence_refs':['E2']}
            invoke = Mock(return_value=advice)
            results = [{'passed':False,'command':'pytest','exit_code':1,'output_tail':'ambiguous failure'}]
            t1 = {'id':'001','functional_failures':2,'last_error':'x','validation_stagnation':{'signature':'a'*64,'repeats':2}}
            t2 = {'id':'002','functional_failures':2,'last_error':'x','validation_stagnation':{'signature':'b'*64,'repeats':2}}
            self.assertEqual(a.triage(plan,t1,results,cfg,invoke=invoke)['status'], 'advice')
            self.assertEqual(a.triage(plan,t2,results,cfg,invoke=invoke)['reason'], 'plan_attempt_budget')
            invoke.assert_called_once()


if __name__ == '__main__':
    unittest.main()
