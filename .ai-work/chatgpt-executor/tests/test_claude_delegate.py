#!/usr/bin/env python3
"""Offline negative tests only: NEVER model identity or independent-review evidence."""
from __future__ import annotations
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
from unittest.mock import patch

BRIDGE = Path(__file__).resolve().parents[3] / ".ai-work/chatgpt-executor/claude_delegate.py"
spec = importlib.util.spec_from_file_location("pae_claude_bridge", BRIDGE)
assert spec and spec.loader
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


def run(root, *command):
    p = subprocess.run(command, cwd=root, text=True, capture_output=True)
    assert p.returncode == 0, (command, p.stderr)
    return p.stdout.strip()


def save(root, path, data):
    p = root / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data) + "\n" if isinstance(data, dict) else str(data), encoding="utf-8")
    return p


def build(root, mode="review", task_id="015", large_manifest=False):
    run(root, "git", "init", "-q")
    run(root, "git", "config", "user.name", "Fixture")
    run(root, "git", "config", "user.email", "fixture@example.org")
    manifest = {"tasks": [{"id": task_id, "status": "pending"}]}
    if large_manifest:
        manifest["fixture_padding"] = "x" * 680_000
    save(root, ".ai-work/20261028-skill-study-provider-switch/manifest.json", manifest)
    save(root, "docs/plans/20261028-skill-optimization/TASK_INPUTS.json", {
        "tasks": [{"id": task_id, "work_type": "review_and_fix" if mode in {"review", "repair"} else "implementation",
                   "requires_independent_review": mode in {"review", "repair"}, "inputs": ["src/example.py"],
                   "write_scope": ["src/example.py"], "required_checks": [["python", "src/example.py"]]}]
    })
    save(root, ".ai-work/20261028-skill-study-provider-switch/tasks/" + task_id + "-fixture.md", "# Fixture\n")
    save(root, "docs/research/fixture.md", "# Evidence fixture\n")
    save(root, "src/example.py", "VALUE = 1\n")
    run(root, "git", "add", ".")
    run(root, "git", "commit", "-qm", "baseline")
    head = run(root, "git", "rev-parse", "HEAD")
    request = {
        "schema": "pae-claude-delegation/1",
        "attempt_id": "claude-test-offline-0001",
        "mode": mode,
        "task_id": task_id,
        "source_head": head,
        "escalation": {
            "reason": "review_finding" if mode == "repair" else "cross_cutting_high_risk",
            "evidence_ref": "docs/research/fixture.md",
            "summary": "A test-only evidence record justifies isolated delegated assessment.",
        },
    }
    save(root, b.REQUEST, request)
    run(root, "git", "add", b.REQUEST)
    run(root, "git", "commit", "-qm", "request-only")
    return request, run(root, "git", "rev-parse", "HEAD")


def test_review():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        # Real plan manifest exceeds the previous 600 KB parser limit.
        request, head = build(root, large_manifest=True)
        env = {"GITHUB_REPOSITORY": b.REPO, "GITHUB_REF": "refs/heads/" + b.BRANCH,
               "GITHUB_SHA": head}
        with patch.object(b, "ROOT", root), patch.dict(os.environ, env), patch.object(b, "OUT", root / b.OUT):
            b.preflight()
            assert (root / b.OUT / "prompt.txt").is_file()
            prompt_text = (root / b.OUT / "prompt.txt").read_text()
            assert "Reserve final turns for structured JSON" in prompt_text
            assert "Read only bounded relevant file regions" in prompt_text
            assert json.loads((root / b.OUT / "input.json").read_text())["request_commit"] == head
            with patch.dict(os.environ, {
                "CLAUDE_REVIEW_OUTPUT": json.dumps({
                    "reviewed_sha": head, "verdict": "changes_requested", "findings": [],
                    "limitations": ["Offline fixture, no model invocation"]
                }),
                "CLAUDE_REVIEW_SESSION": "fixture-not-real-session",
                "CLAUDE_REVIEW_CONCLUSION": "success",
            }):
                b.collect()
            report = json.loads((root / b.OUT / "result.json").read_text())
            assert report["original_gate_approved"] is False
            assert report["native_effort_observed"] is None
            assert report["session_id_reported_by_action"] == "fixture-not-real-session"
            with patch.dict(os.environ, {"GITHUB_SHA": "f" * 40}):
                try:
                    b.preflight()
                except b.BridgeError as err:
                    assert "SHA" in str(err)
                else:
                    raise AssertionError("mismatched HEAD accepted")
            # A request commit that edits code as well must be rejected before secret access.
            save(root, "src/example.py", "VALUE = 2\n")
            run(root, "git", "add", "src/example.py")
            run(root, "git", "commit", "-qm", "not request only")
            with patch.dict(os.environ, {"GITHUB_SHA": run(root, "git", "rev-parse", "HEAD")}):
                try:
                    b.preflight()
                except b.BridgeError:
                    pass
                else:
                    raise AssertionError("source mutation accepted in dispatch commit")


def test_implementation_scope():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _request, head = build(root, mode="implement", task_id="016")
        env = {"GITHUB_REPOSITORY": b.REPO, "GITHUB_REF": "refs/heads/" + b.BRANCH,
               "GITHUB_SHA": head}
        with patch.object(b, "ROOT", root), patch.dict(os.environ, env), patch.object(b, "OUT", root / b.OUT):
            b.preflight()
            save(root, "src/example.py", "VALUE = 3\n")
            diff = b.save_patch(["src/example.py"])
            assert diff["patch_bytes"] > 0
            assert diff["changed_files"] == ["src/example.py"]
            # A second changed, unassigned file blocks *all* patch publication.
            save(root, "src/outside.py", "VALUE = 'unauthorized'\n")
            try:
                b.save_patch(["src/example.py"])
            except b.BridgeError as err:
                assert "outside" in str(err)
            else:
                raise AssertionError("out-of-scope edit accepted")


def test_repair_scope_and_stop():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _request, head = build(root, mode="repair", task_id="015")
        env = {"GITHUB_REPOSITORY": b.REPO, "GITHUB_REF": "refs/heads/" + b.BRANCH,
               "GITHUB_SHA": head}
        with patch.object(b, "ROOT", root), patch.dict(os.environ, env), patch.object(b, "OUT", root / b.OUT):
            b.preflight()
            att = json.loads((root / b.OUT / "input.json").read_text())
            assert att["model_requested"] == "claude-sonnet-5-5"
            assert att["native_effort_requested"] == "high"
            prompt_text = (root / b.OUT / "prompt.txt").read_text()
            for required in ["skill/plan-and-execute/SKILL.md", "Never invoke agy",
                             "STRICT STOP RULE", "NEW independent Opus"]:
                assert required in prompt_text, required
            save(root, "src/example.py", "VALUE = 7\n")
            with patch.dict(os.environ, {
                "CLAUDE_IMPLEMENT_OUTPUT": json.dumps({
                    "status": "implemented", "summary": "Fixture only", "limitations": []
                }),
                "CLAUDE_IMPLEMENT_SESSION": "fixture-not-real-repair",
                "CLAUDE_IMPLEMENT_CONCLUSION": "success",
            }):
                b.collect()
            result = json.loads((root / b.OUT / "result.json").read_text())
            assert result["mode"] == "repair"
            assert result["model_requested"] == "claude-sonnet-5-5"
            assert result["original_gate_approved"] is False
            assert result["artifact"]["changed_files"] == ["src/example.py"]
            save(root, "src/not-allowed.py", "VALUE = 8\n")
            try:
                b.save_patch(["src/example.py"])
            except b.BridgeError:
                pass
            else:
                raise AssertionError("repair wrote outside scope")


if __name__ == "__main__":
    test_review()
    test_implementation_scope()
    test_repair_scope_and_stop()
    print("Claude delegation bridge: offline positive/negative/repair checks passed (NO live Claude run)")
