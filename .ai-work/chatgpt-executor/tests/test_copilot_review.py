"""Read-only review adapter fixtures: no external model or fake live attestation."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ADAPTER = Path(__file__).resolve().parents[1] / 'copilot_review.py'
spec = importlib.util.spec_from_file_location('copilot_review_local', ADAPTER)
r = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(r)


def event(review=None, *, model=r.MODEL, effort=r.EFFORT, session='live-session-123456'):
    if review is None:
        review = {"verdict": "approved", "summary": "No demonstrated high-risk defect.", "findings": []}
    return '\n'.join([
        json.dumps({"type": "session.start", "data": {"sessionId": session,
                   "selectedModel": model, "reasoningEffort": effort, "copilotVersion": "1.0.99"}}),
        json.dumps({"type": "assistant.message", "data": {"content": json.dumps(review)}}),
    ])


class ReviewTests(unittest.TestCase):
    def test_good_authenticated_model_packet(self):
        review, identity = r.parse_cli_jsonl(event())
        self.assertEqual(identity['model'], r.MODEL)
        self.assertEqual(identity['native_effort'], r.EFFORT)
        self.assertEqual(review['verdict'], 'approved')
        self.assertEqual(identity['session_id'], 'live-session-123456')

    def test_reject_missing_or_wrong_session(self):
        for raw in ['{}', event(session='short'), event(model='other-model'), event(effort='low')]:
            with self.assertRaises(r.ReviewError):
                r.parse_cli_jsonl(raw)

    def test_reject_unstructured_and_contradictory_approval(self):
        with self.assertRaises(r.ReviewError):
            r.parse_cli_jsonl(event({'verdict':'approved','summary':'bad','findings':[
                {'id':'C1','severity':'critical','location':'source.py:8','title':'x',
                 'detail':'problem','fix':'repair'}]}))
        with self.assertRaises(r.ReviewError):
            r.parse_cli_jsonl(event({'verdict':'approved','summary':'bad','findings':'empty'}))

    def test_safe_failure_categories_do_not_echo_secrets(self):
        self.assertEqual(r.classify_cli_failure("error: unknown option '--bogus' token ghp_hidden"), "cli_argument_or_version")
        self.assertEqual(r.classify_cli_failure("Error 403 organization policy prevents using Copilot"), "copilot_policy_or_entitlement")
        self.assertEqual(r.classify_cli_failure("Unexpected upstream failure, token my-private-key"), "unclassified_cli_failure")

    def test_readonly_cli_flags_are_pinned(self):
        self.assertEqual(r.MODEL, 'claude-opus-5.5')
        self.assertEqual(r.EFFORT, 'xhigh')
        self.assertTrue(r.FORBIDDEN_SECRET.search('Authorization: Bearer abc'))


if __name__ == '__main__':
    unittest.main()
