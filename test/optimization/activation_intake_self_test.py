#!/usr/bin/env python3
"""Offline acceptance and regression tests for selective activation, intake, and late promotion (TODOs 006/007).

DIRECT/lifecycle acceptance runs the actual `requestctl.py evaluate-route` CLI inside a temporary
repository and compares a recursive file snapshot, and asserts on prompt-level cue extraction rather
than only on hand-set flags.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "skill" / "plan-and-execute" / "scripts"
EVALS_PATH = REPO_ROOT / "skill" / "plan-and-execute" / "references" / "routing-evals.json"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import promotectl  # noqa: E402
import requestctl  # noqa: E402

SEVEN_FILE_PROMPT = "Implement a cohesive invoice CRUD and filtering feature touching 7 related files in one module with focused tests."
SECURITY_PROMPT = "Fix the 2-line JWT signature verification bypass in auth middleware and add a regression test."
NEAR_FINISHED_PROMPT = "Context is 92% full but only one tiny cohesive test fix remains; do not promote."
LOG_PROMPT = "Inspect this 40,000-line repetitive CI failure log to locate the single failing assertion and fix the off-by-one bug."


def _make_git_repo(root: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
    (root / "app.py").write_text("def handler():\n    return 1\n", encoding="utf-8")
    subprocess.run(["git", "add", "app.py"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "initial"], cwd=root, check=True)


def _snapshot(root: Path) -> dict[str, str]:
    """Every file under root (including .git) with its content hash."""
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _cli(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "requestctl.py"), *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def _route_in_repo(prompt: str, *extra: str) -> dict:
    """Run the actual evaluate-route CLI with cwd inside a fresh git repo; assert it changes no file."""
    with tempfile.TemporaryDirectory(prefix="pae-007-route-") as tmp:
        repo = Path(tmp)
        _make_git_repo(repo)
        before = _snapshot(repo)
        proc = _cli(["evaluate-route", "--prompt", prompt, *extra, "--json"], cwd=repo)
        assert proc.returncode == 0, proc.stderr
        assert _snapshot(repo) == before, "evaluate-route must not create or change any file"
        assert not (repo / ".ai-work").exists()
        return json.loads(proc.stdout)


def _assert_no_persistence(decision: dict) -> None:
    assert decision["persist_plan"] is False, decision
    assert decision["persisted_reason_codes"] == [], decision
    assert decision["classifier_call"] is False
    assert "references/ORCHESTRATION.md" not in decision["load_references"]
    assert "references/PROMOTION.md" not in decision["load_references"]


def test_seven_file_feature_stays_direct_with_no_artifacts() -> None:
    signals = requestctl.extract_prompt_signals(SEVEN_FILE_PROMPT)
    assert signals["estimated_working_set"] == 7, signals
    assert signals["cohesive_single_outcome"] is True
    assert signals["independent_workstreams"] == 1 and not signals["explicit_invocation"]

    decision = _route_in_repo(SEVEN_FILE_PROMPT)
    assert decision["route"] == "direct", decision
    _assert_no_persistence(decision)
    assert decision["load_references"] == []
    assert "COHESIVE_BOUNDED_WORK" in decision["reason_codes"]
    assert "FILE_COUNT_WEAK_SIGNAL" in decision["reason_codes"]
    assert decision["estimated_working_set"]["count"] == 7
    assert len(decision["reason_codes"]) <= requestctl.MAX_REASON_CODES
    assert "created_artifacts" not in decision, "hard-coded artifact claims were removed"


def test_small_security_fix_stays_direct_with_strong_capability() -> None:
    signals = requestctl.extract_prompt_signals(SECURITY_PROMPT)
    assert signals["security_sensitive"] is True, signals
    decision = _route_in_repo(SECURITY_PROMPT)
    assert decision["route"] == "direct", decision
    _assert_no_persistence(decision)
    assert "DIRECT_WITH_STRONG_CAPABILITY" in decision["reason_codes"]
    assert decision["capability_route"] == {"tier": "strong", "effort": "high"}, decision

    for weak in (False, True):
        flagged = requestctl.evaluate_activation(security_sensitive=True, weak_validation=weak, estimated_working_set=1)
        assert flagged["route"] == "direct"
        assert flagged["capability_route"] == {"tier": "strong", "effort": "high"}, flagged

    # A caller override may raise the floor but can never drop the security/risk floor (review M3).
    for override in (["mechanical_edit"], ["bounded_implementation"], ["deterministic_lookup"]):
        overridden = requestctl.evaluate_activation(security_sensitive=True, capability_signals=override)
        assert overridden["capability_route"]["tier"] == "strong", (override, overridden)
        assert overridden["capability_route"]["effort"] == "high", (override, overridden)
    risky = requestctl.evaluate_activation(cross_cutting_risk=True, capability_signals=["mechanical_edit"])
    assert risky["capability_route"]["tier"] == "strong", risky
    raised = requestctl.evaluate_activation(capability_signals=["silent_failure_costly"])
    assert raised["capability_route"]["tier"] == "strong"

    with tempfile.TemporaryDirectory(prefix="pae-007-spec-") as tmp:
        spec = Path(tmp) / "spec.json"
        spec.write_text(json.dumps({"security_sensitive": True, "capability_signals": ["mechanical_edit"]}), encoding="utf-8")
        proc = _cli(["evaluate-route", "--spec", str(spec), "--json"])
        assert proc.returncode == 0, proc.stderr
        assert json.loads(proc.stdout)["capability_route"] == {"tier": "strong", "effort": "high"}
        spec.write_text(json.dumps({"prompt": "x", "created_artifacts": []}), encoding="utf-8")
        bad = _cli(["evaluate-route", "--spec", str(spec), "--json"])
        assert bad.returncode == 2 and "Unknown route evaluation fields" in bad.stderr, bad.stderr
        assert "Traceback" not in bad.stderr
        spec.write_text(json.dumps({"capability_signals": ["not_a_signal"]}), encoding="utf-8")
        unknown = _cli(["evaluate-route", "--spec", str(spec), "--json"])
        assert unknown.returncode == 2 and "Traceback" not in unknown.stderr, unknown.stderr


def test_near_finished_high_context_stays_direct_and_blocks_promotion() -> None:
    signals = requestctl.extract_prompt_signals(NEAR_FINISHED_PROMPT)
    assert signals["nearly_finished"] is True and signals["already_direct"] is True, signals
    assert signals["context_used_percentage"] == 92
    decision = _route_in_repo(NEAR_FINISHED_PROMPT)
    assert decision["route"] == "direct", decision
    _assert_no_persistence(decision)
    assert "NEAR_FINISHED_HIGH_CONTEXT" in decision["reason_codes"]

    base_spec = {
        "schema_version": 1,
        "original_goal": "Finish small parser fix.",
        "completed_work": ["Updated parser."],
        "validated_results": [],
        "decisions": [],
        "relevant_code": ["parser.py"],
        "remaining_outcomes": ["Fix one assertion."],
        "nearly_finished": True,
        "cohesive_remaining": True,
        "context_pressure": {"used_percentage": 92, "source": "host"},
    }
    for codes in ([], ["DURABLE_RESUME_VALUE"], ["CROSS_CUTTING_RISK"]):
        try:
            promotectl.normalize_spec({**base_spec, "reason_codes": codes})
        except promotectl.PromotionError as exc:
            assert "stay DIRECT" in str(exc)
        else:
            raise AssertionError(f"nearly_finished cohesive promotion should be rejected: {codes}")
    # An explicit user request may still promote (review M4).
    promotectl.normalize_spec({**base_spec, "reason_codes": ["EXPLICIT_INVOCATION", "LATE_PROMOTION_REMAINING_WORK"]})


def test_requestctl_and_promotectl_agree_on_promotion() -> None:
    """When requestctl says promote, the matching handoff validates; when it keeps DIRECT, it is rejected."""
    base_spec = {
        "schema_version": 1,
        "original_goal": "Ship export feature.",
        "completed_work": ["Updated handler."],
        "relevant_code": ["app.py"],
    }
    for nearly, cohesive, count, explicit in itertools.product((True, False), (True, False), (1, 2), (True, False)):
        outcomes = [f"Outcome {index}" for index in range(count)]
        decision = requestctl.evaluate_activation(
            explicit_invocation=explicit,
            already_direct=True,
            nearly_finished=nearly,
            cohesive_single_outcome=cohesive,
            independent_workstreams=1 if cohesive else 2,
            durable_resume_value=True,
            remaining_outcomes=outcomes,
        )
        codes = ["EXPLICIT_INVOCATION"] if explicit else []
        codes += ["LATE_PROMOTION_REMAINING_WORK", "DURABLE_RESUME_VALUE"]
        spec = {**base_spec, "remaining_outcomes": outcomes, "nearly_finished": nearly,
                "cohesive_remaining": cohesive, "reason_codes": codes}
        try:
            promotectl.normalize_spec(spec)
            accepted = True
        except promotectl.PromotionError:
            accepted = False
        assert (decision["route"] == "promote") == accepted, (nearly, cohesive, count, explicit, decision["route"])
        assert decision["route"] in {"promote", "direct"}


def test_lifecycle_commands_and_skill_mentions_stay_outside_semantic_routing() -> None:
    for prompt, verb in (
        ("$plan-and-execute status", "status"),
        ("/plan-and-execute resume", "resume"),
        ("Run pae current to show the active implementation.", "current"),
        ("pae configure", "configure"),
        ("Resume the active plan-and-execute implementation from its persisted TODO state.", "resume"),
    ):
        signals = requestctl.extract_prompt_signals(prompt)
        assert signals["lifecycle_command"] == verb, (prompt, signals)
        assert signals["explicit_invocation"] is False, prompt
        decision = requestctl.evaluate_activation(**signals)
        assert decision["route"] == "lifecycle", (prompt, decision)
        _assert_no_persistence(decision)
        assert decision["load_references"] == []
        assert decision["reason_codes"] == ["LIFECYCLE_COMMAND"]
        assert decision["capability_route"] == {"tier": "tool", "effort": "none"}
    cli = _route_in_repo("$plan-and-execute status")
    assert cli["route"] == "lifecycle" and cli["persisted_reason_codes"] == []

    for prompt in (
        "Fix the typo in the usage text printed by bin/plan-and-execute.js.",
        "Update skill/plan-and-execute/SKILL.md wording for the DIRECT exit.",
    ):
        signals = requestctl.extract_prompt_signals(prompt)
        assert signals["explicit_invocation"] is False and signals["lifecycle_command"] is None, (prompt, signals)
        assert requestctl.evaluate_activation(**signals)["route"] == "direct", prompt

    for prompt in ("Use plan-and-execute to migrate billing.", "$plan-and-execute add audit export"):
        signals = requestctl.extract_prompt_signals(prompt)
        assert signals["explicit_invocation"] is True, (prompt, signals)
        decision = requestctl.evaluate_activation(**signals)
        assert decision["route"] == "orchestrated" and decision["persist_plan"] is True
        assert decision["persisted_reason_codes"][0] == "EXPLICIT_INVOCATION"


def test_repetitive_log_and_validate_or_fix_pointer() -> None:
    signals = requestctl.extract_prompt_signals(LOG_PROMPT)
    assert signals["repetitive_log"] is True, signals
    log_case = _route_in_repo(LOG_PROMPT)
    assert log_case["route"] == "direct"
    assert "REPETITIVE_OR_LARGE_LOG" in log_case["reason_codes"]
    _assert_no_persistence(log_case)

    vof = requestctl.evaluate_activation(needs_validate_or_fix=True, remaining_outcomes=["Run mapped integration suite"])
    assert vof["route"] == "direct"
    assert vof["validate_or_fix"] is True
    _assert_no_persistence(vof)
    assert vof["load_references"] == ["references/VALIDATION_WORKLOADS.md"]
    assert "VALIDATE_OR_FIX_EXIT" in vof["reason_codes"]


def test_explicit_and_unrelated_workstreams_record_bounded_reasons() -> None:
    explicit = requestctl.evaluate_activation(explicit_invocation=True, remaining_outcomes=["Execute requested plan"])
    assert explicit["route"] == "orchestrated"
    assert explicit["persist_plan"] is True
    assert explicit["reason_codes"] == ["EXPLICIT_INVOCATION"]
    assert explicit["persisted_reason_codes"] == ["EXPLICIT_INVOCATION"]
    assert explicit["load_references"] == ["references/ORCHESTRATION.md"]

    prompt = "Implement unrelated person and store CRUDs with separate business rules, controllers, services and tests."
    signals = requestctl.extract_prompt_signals(prompt)
    assert signals["independent_workstreams"] == 2 and signals["cohesive_single_outcome"] is False
    multi = requestctl.evaluate_activation(**signals)
    assert multi["route"] == "orchestrated"
    assert multi["persist_plan"] is True
    assert "INDEPENDENT_WORKSTREAMS" in multi["reason_codes"]
    assert multi["persisted_reason_codes"] == multi["reason_codes"]

    every = requestctl.evaluate_activation(
        explicit_invocation=True, already_direct=True, independent_workstreams=3, needs_broad_study=True,
        cross_cutting_risk=True, durable_resume_value=True, isolation_value=True,
    )
    assert len(every["reason_codes"]) == requestctl.MAX_REASON_CODES
    assert every["reason_codes"][:2] == ["EXPLICIT_INVOCATION", "LATE_PROMOTION_REMAINING_WORK"]


def _section(markdown: str, title: str) -> list[str]:
    match = re.search(rf"^## {re.escape(title)}\n\n(.*?)(?=^## |\Z)", markdown, re.S | re.M)
    assert match, f"missing section {title}"
    return [line[2:] for line in match.group(1).splitlines() if line.startswith("- ")]


def test_late_promotion_preserves_worktree_and_schedules_remaining_only() -> None:
    promo_route = requestctl.evaluate_activation(
        already_direct=True,
        independent_workstreams=2,
        cohesive_single_outcome=False,
        context_used_percentage=80,
        remaining_outcomes=["Add HTTP endpoint", "Add async worker"],
    )
    assert promo_route["route"] == "promote"
    assert promo_route["persist_plan"] is True
    assert "LATE_PROMOTION_REMAINING_WORK" in promo_route["reason_codes"]
    assert "HIGH_CONTEXT_SUBSTANTIAL_WORK" in promo_route["reason_codes"]
    assert promo_route["load_references"] == ["references/PROMOTION.md"]

    with tempfile.TemporaryDirectory(prefix="pae-007-promo-") as tmp:
        repo = Path(tmp) / "repo"
        repo.mkdir()
        _make_git_repo(repo)
        modified_content = "def handler():\n    return 42\n"
        (repo / "app.py").write_text(modified_content, encoding="utf-8")
        (repo / "test_done.py").write_text("assert True\n", encoding="utf-8")
        before = _snapshot(repo)

        spec = {
            "schema_version": 1,
            "original_goal": "Ship export feature.",
            "completed_work": ["Updated handler return value in app.py."],
            "validated_results": ["python test_done.py => passed"],
            "decisions": ["Keep handler signature compatible."],
            "relevant_code": ["app.py:handler"],
            "remaining_outcomes": ["Add HTTP export route.", "Add async delivery worker."],
            "blockers": [],
            "risks": ["Large exports can time out synchronously."],
            "reason_codes": ["LATE_PROMOTION_REMAINING_WORK", "INDEPENDENT_WORKSTREAMS"],
            "estimated_working_set": ["app.py", "routes.py", "worker.py"],
            "evidence_pointers": ["app.py:handler", "test_done.py"],
            "context_pressure": {"used_percentage": 80, "source": "host"},
        }
        spec_path = Path(tmp) / "promo.json"
        spec_path.write_text(json.dumps(spec), encoding="utf-8")
        handoff_path = Path(tmp) / "handoff.md"

        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "promotectl.py"),
                "render",
                "--repo-root",
                str(repo),
                "--spec",
                str(spec_path),
                "--output",
                str(handoff_path),
                "--json",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        assert proc.returncode == 0, proc.stderr + proc.stdout
        assert _snapshot(repo) == before, "promotion must not change the worktree or the git index"
        assert (repo / "app.py").read_text(encoding="utf-8") == modified_content

        rendered = handoff_path.read_text(encoding="utf-8")
        assert "ONLY the remaining outcomes" in rendered
        assert "not retroactive TODOs" in rendered
        assert _section(rendered, "Remaining outcomes") == spec["remaining_outcomes"]
        assert _section(rendered, "Completed work") == spec["completed_work"]
        for done in spec["completed_work"] + spec["validated_results"]:
            assert done not in _section(rendered, "Remaining outcomes")
        assert "## Promotion reason codes" in rendered
        assert "LATE_PROMOTION_REMAINING_WORK" in rendered
        assert _section(rendered, "Source evidence pointers") == spec["evidence_pointers"]

        for field, value in (
            ("evidence_pointers", ["transcript.jsonl:line1"]),
            ("decisions", ["User: please keep the old API", "Assistant: ok, keeping it"]),
            ("risks", ["user: what about timeouts?\nassistant: we retry"]),
            ("remaining_outcomes", ["Assistant: next I will add the route"]),
        ):
            try:
                promotectl.normalize_spec({**spec, field: value})
            except promotectl.PromotionError as exc:
                assert "source evidence pointers" in str(exc), exc
            else:
                raise AssertionError(f"transcript copy in {field} must be rejected")
        try:
            promotectl.normalize_spec({**spec, "original_goal": "Conversation history: user asked for exports"})
        except promotectl.PromotionError as exc:
            assert "original_goal" in str(exc)
        else:
            raise AssertionError("transcript copy in original_goal must be rejected")


def test_corpus_metrics_and_cli_without_classifier_call() -> None:
    payload = json.loads(EVALS_PATH.read_text(encoding="utf-8"))
    protocol = payload["held_out_protocol"]
    report = requestctl.evaluate_routing_corpus(payload["cases"], protocol=protocol)
    assert report["metric"] == "offline_cue_extractor_proxy"
    assert report["held_out_integrity"]["status"] == "frozen", report["held_out_integrity"]
    assert report["entrypoint_bytes"]["SKILL.md"] <= 7000
    held = report["held_out"]
    assert set(held) == set(requestctl.ROUTING_ALTERNATIVES)
    assert held["selective_cue_proxy"]["total"] >= 12
    assert held["selective_cue_proxy"]["false_positive_rate"] <= protocol["ceilings"]["max_false_positive_rate"]
    assert held["selective_cue_proxy"]["false_negative_rate"] <= protocol["ceilings"]["max_false_negative_rate"]
    assert held["all_direct"]["false_negative_rate"] == 1.0
    cost = report["expected_cost_model"]
    assert cost["status"] == "costs_unmeasured" and cost["paid_classifier"] == "unmeasured"
    assert cost["c_unneeded_plan"] is None and cost["c_recovery"] is None
    assert set(cost["held_out_probabilities"]) == set(requestctl.ROUTING_ALTERNATIVES)
    assert report["live_host_evaluation"]["status"] == "unmeasured_limitation"

    # A changed cue table must invalidate the held-out claim instead of silently re-scoring it.
    stale = requestctl.evaluate_routing_corpus(payload["cases"], protocol={**protocol, "cue_table_sha256": "0" * 64})
    assert stale["held_out_integrity"]["status"] == "stale_cue_table"
    assert requestctl.evaluate_routing_corpus(payload["cases"])["held_out_integrity"]["status"] == "unrecorded"

    cli_eval = _cli(["eval-corpus", "--json"])
    assert cli_eval.returncode == 0, cli_eval.stderr
    eval_data = json.loads(cli_eval.stdout)
    assert eval_data["held_out_integrity"]["status"] == "frozen"
    assert eval_data["held_out"]["selective_cue_proxy"] == held["selective_cue_proxy"]


def main() -> int:
    tests = [
        test_seven_file_feature_stays_direct_with_no_artifacts,
        test_small_security_fix_stays_direct_with_strong_capability,
        test_near_finished_high_context_stays_direct_and_blocks_promotion,
        test_requestctl_and_promotectl_agree_on_promotion,
        test_lifecycle_commands_and_skill_mentions_stay_outside_semantic_routing,
        test_repetitive_log_and_validate_or_fix_pointer,
        test_explicit_and_unrelated_workstreams_record_bounded_reasons,
        test_late_promotion_preserves_worktree_and_schedules_remaining_only,
        test_corpus_metrics_and_cli_without_classifier_call,
    ]
    for test in tests:
        test()
        print(f"PROGRESS {test.__name__} passed", flush=True)
    print(f"activation_intake_self_test passed ({len(tests)} acceptance groups).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
