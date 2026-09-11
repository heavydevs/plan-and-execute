#!/usr/bin/env python3
"""Representative self-tests for the plan manager and isolated runner."""

from __future__ import annotations

import argparse
import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import planctl  # noqa: E402
import requestctl  # noqa: E402
import run_isolated  # noqa: E402


def sample_spec() -> dict:
    return {
        "title": "Implement sample feature",
        "summary": "Create two bounded changes and verify them.",
        "language": "English",
        "request_analysis": {
            "request_parts": [
                {"id": "P001", "text": "Create an implementation marker"},
                {"id": "P002", "text": "Verify the marker contains the requested value"},
            ],
            "repository_findings": [
                "The sample repository is intentionally minimal and has no existing implementation files."
            ],
            "research_decision": "No external research is needed for a local marker-file test.",
            "research_findings": [],
            "assumptions": ["The test environment provides POSIX shell commands."],
            "risks": ["A broad file edit could accidentally touch unrelated files."],
            "open_questions": [],
            "decomposition_strategy": (
                "Separate file creation from content verification so each outcome has one deterministic check."
            ),
        },
        "requirements": [
            {
                "id": "R001",
                "text": "Create implemented.txt without unrelated changes",
                "source": "user",
                "priority": "must",
                "request_part_ids": ["P001"],
            },
            {
                "id": "R002",
                "text": "Ensure implemented.txt contains the word implemented",
                "source": "user",
                "priority": "must",
                "request_part_ids": ["P002"],
            },
        ],
        "global_constraints": ["Do not edit unrelated files"],
        "execution_context": {
            "global": {
                "decision": "create",
                "rationale": (
                    "Both TODOs must preserve the same narrow file boundary, so one concise "
                    "shared invariant prevents inconsistent edits without repeating it in each task."
                ),
                "items": [
                    {
                        "id": "G001",
                        "kind": "constraint",
                        "text": "Only implemented.txt may be created or changed by this sample plan.",
                        "necessity": (
                            "Every TODO can modify the marker file, and each must avoid unrelated "
                            "working-tree changes throughout execution."
                        ),
                        "source_refs": ["request:P001", "global_constraints[0]"],
                    }
                ],
            },
            "scoped": [],
        },
        "plan_review": {
            "status": "approved",
            "reviewer": "fresh planning reviewer",
            "rounds": 1,
            "coverage_complete": True,
            "tasks_atomic": True,
            "dependencies_valid": True,
            "validations_sufficient": True,
            "contexts_minimal": True,
            "context_boundaries_sound": True,
            "unresolved_findings": [],
            "notes": [
                "Every requirement maps to a task and both tasks have independent validation."
            ],
        },
        "tasks": [
            {
                "id": 1,
                "title": "Create implementation marker",
                "objective": "Create implemented.txt in the repository root.",
                "requirement_ids": ["R001"],
                "complexity": "low",
                "atomicity_rationale": "This task has one file-creation outcome and one direct existence check.",
                "context_boundary": {
                    "shared_context": [
                        "Creating implemented.txt and proving its existence share one marker-file contract."
                    ],
                    "why_one_todo": (
                        "The file creation and its direct existence check are one cohesive outcome; "
                        "splitting them would create an artificial handoff without reducing context."
                    ),
                    "separate_from": [
                        "Marker content verification belongs to TODO 002 and needs no creation transcript."
                    ],
                },
                "scope": {
                    "in": ["Create the marker file"],
                    "out": ["No unrelated refactoring"],
                    "expected_files": ["implemented.txt"],
                },
                "acceptance_criteria": ["implemented.txt exists"],
                "validation_commands": ["test -f implemented.txt"],
                "subtasks": [
                    {
                        "id": "S001",
                        "title": "Create the bounded marker file",
                        "objective": "implemented.txt exists without unrelated repository changes.",
                    }
                ],
                "provider": "auto",
                "model_tier": "economy",
                "reasoning_effort": "low",
            },
            {
                "id": 2,
                "title": "Verify marker contents",
                "objective": "Ensure implemented.txt contains the expected word.",
                "requirement_ids": ["R002"],
                "complexity": "low",
                "atomicity_rationale": "This task has one content outcome and one deterministic grep check.",
                "context_boundary": {
                    "shared_context": [
                        "Correcting marker contents and running grep share one deterministic content contract."
                    ],
                    "why_one_todo": (
                        "The content correction and grep validation use the same file invariant, while the "
                        "worker needs only repository state rather than TODO 001 conversation history."
                    ),
                    "separate_from": [
                        "Initial marker creation belongs to TODO 001 and is already represented on disk."
                    ],
                },
                "dependencies": [1],
                "scope": {
                    "in": ["Check or update implemented.txt"],
                    "out": ["No unrelated files"],
                    "expected_files": ["implemented.txt"],
                },
                "acceptance_criteria": ["The marker contains implemented"],
                "validation_commands": ["grep -q implemented implemented.txt"],
                "subtasks": [
                    {
                        "id": "S001",
                        "title": "Verify and correct marker contents",
                        "objective": "implemented.txt contains the expected word and the grep check passes.",
                    }
                ],
                "provider": "auto",
                "model_tier": "economy",
                "reasoning_effort": "low",
            },
        ],
    }


def write_fake_claude(path: Path) -> None:
    script = r'''#!/usr/bin/env python3
import json
import pathlib
import sys

args = sys.argv[1:]
root = pathlib.Path.cwd()
prompt = args[-1] if args else ""
if "Design note path:" in prompt:
    note = prompt.split("Design note path:", 1)[1].splitlines()[0].strip()
    pathlib.Path(note).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(note).write_text("# Design\n\nApproach: create the file directly.\n", encoding="utf-8")
    report = {
        "status": "completed",
        "summary": "Design note written.",
        "changed_files": [],
        "validations": [],
        "risks": [],
        "follow_ups": [],
        "context_files_read": ["CONTEXT.md"],
        "learning_files_read": [],
        "completed_subtask_ids": [],
        "reusable_learnings": [],
        "related_task_reads": [],
        "blocked_reason": None
    }
    print(json.dumps({"type": "result", "structured_output": report}))
elif "--json-schema" in args:
    flag = root / "design-required.flag"
    required = flag.read_text(encoding="utf-8").strip() if flag.exists() else ""
    if required and "Design note:" not in prompt and (
        f"Task: `{required}`" in prompt or f"Task id: {required}" in prompt
    ):
        report = {
            "status": "blocked",
            "summary": "Missing design note.",
            "changed_files": [],
            "validations": [],
            "risks": [],
            "follow_ups": [],
            "context_files_read": ["CONTEXT.md"],
            "learning_files_read": [],
            "completed_subtask_ids": [],
            "reusable_learnings": [],
            "related_task_reads": [],
            "blocked_reason": "Design note was not provided",
            "failure_class": "plan_defect"
        }
        print(json.dumps({"type": "result", "structured_output": report}))
        raise SystemExit(0)
    (root / "implemented.txt").write_text("implemented\n", encoding="utf-8")
    report = {
        "status": "completed",
        "summary": "Implemented the bounded task.",
        "changed_files": ["implemented.txt"],
        "validations": [{"command": "worker check", "passed": True, "details": "ok"}],
        "risks": [],
        "follow_ups": [],
        "context_files_read": ["CONTEXT.md"],
        "learning_files_read": [],
        "completed_subtask_ids": ["S001"],
        "reusable_learnings": [],
        "related_task_reads": [],
        "blocked_reason": None
    }
    print(json.dumps({"type": "result", "structured_output": report}))
else:
    print("# Final summary\n\nAll sample tasks completed and validated.")
'''
    path.write_text(script, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def test_plan_state() -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = Path(temp) / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        spec = sample_spec()
        plan_dir = planctl.create_plan(repo, spec, ".ai-work", "state-test")
        loaded_dir, manifest = planctl.load_plan(plan_dir)
        assert loaded_dir == plan_dir.resolve()
        assert manifest["schema_version"] == 4
        assert not planctl.validate_plan(plan_dir, manifest)
        assert (plan_dir / "ANALYSIS.md").is_file()
        assert (plan_dir / "PLAN_REVIEW.md").is_file()
        assert (plan_dir / planctl.GLOBAL_CONTEXT_FILE).is_file()
        assert manifest["tasks"][0]["context_files"] == [planctl.GLOBAL_CONTEXT_FILE]
        assert manifest["tasks"][1]["context_files"] == [planctl.GLOBAL_CONTEXT_FILE]
        first_task_text = (plan_dir / manifest["tasks"][0]["file"]).read_text(encoding="utf-8")
        assert ".ai-work/state-test/CONTEXT.md" in first_task_text
        audit = planctl.render_audit(manifest)
        assert "P001" in audit and "P002" in audit
        assert "R001" in audit and "R002" in audit
        assert "extreme: 0" in audit
        assert "Global decision: **create**" in audit
        assert "Context minimality review: **pass**" in audit
        git_status = subprocess.run(
            ["git", "status", "--porcelain"], cwd=repo, check=True, text=True, stdout=subprocess.PIPE
        ).stdout
        assert ".ai-work" not in git_status, "Ephemeral plan must be hidden from git status"
        assert planctl.next_runnable_task(manifest)["id"] == "001"

        route = {"provider": "claude", "model": "haiku", "tier": "economy", "effort": "low"}
        planctl.claim_task(plan_dir, manifest, "001", route)
        planctl.fail_task(plan_dir, manifest, "001", "simulated failure")
        assert planctl.find_task(manifest, "001")["functional_failures"] == 1
        planctl.claim_task(plan_dir, manifest, "001", route)
        planctl.complete_task(
            plan_dir,
            manifest,
            "001",
            {
                "changed_files": ["implemented.txt"],
                "validation_results": [],
                "completed_subtask_ids": ["S001"],
                "reusable_learnings": [],
            },
            "results/001.json",
        )
        assert planctl.next_runnable_task(manifest)["id"] == "002"
        planctl.claim_task(plan_dir, manifest, "002", route)
        planctl.complete_task(
            plan_dir,
            manifest,
            "002",
            {
                "changed_files": [],
                "validation_results": [],
                "completed_subtask_ids": ["S001"],
                "reusable_learnings": [],
            },
            None,
        )
        assert manifest["state"] == "completed"
        planctl.mark_summary(plan_dir, manifest, "FINAL_SUMMARY.md")
        (repo / "implemented.txt").write_text("preserve me\n", encoding="utf-8")
        planctl.cleanup_plan(plan_dir, manifest)
        assert not plan_dir.exists()
        assert (repo / "implemented.txt").read_text(encoding="utf-8") == "preserve me\n"
        exclude_path = Path(subprocess.run(
            ["git", "rev-parse", "--git-path", "info/exclude"],
            cwd=repo, check=True, text=True, stdout=subprocess.PIPE
        ).stdout.strip())
        if not exclude_path.is_absolute():
            exclude_path = repo / exclude_path
        assert "plan-and-execute begin" not in exclude_path.read_text(encoding="utf-8")


def test_cycle_rejected() -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = Path(temp)
        spec = sample_spec()
        spec["tasks"][0]["dependencies"] = [2]
        try:
            planctl.create_plan(repo, spec, ".ai-work", "cycle-test")
        except planctl.PlanError as exc:
            assert "cycle" in str(exc).lower()
        else:
            raise AssertionError("Dependency cycle should have been rejected")



def assert_plan_rejected(spec: dict, expected: str) -> None:
    with tempfile.TemporaryDirectory() as temp:
        try:
            planctl.create_plan(Path(temp), spec, ".ai-work", "rejected")
        except planctl.PlanError as exc:
            assert expected.lower() in str(exc).lower(), str(exc)
        else:
            raise AssertionError(f"Plan should have been rejected with {expected!r}")


def test_requirement_coverage_required() -> None:
    spec = sample_spec()
    spec["requirements"].append(
        {
            "id": "R003",
            "text": "A requirement intentionally left uncovered",
            "source": "user",
            "priority": "must",
            "request_part_ids": ["P001"],
        }
    )
    assert_plan_rejected(spec, "without executable TODO coverage")


def test_request_part_coverage_required() -> None:
    spec = sample_spec()
    spec["requirements"][1]["request_part_ids"] = ["P001"]
    assert_plan_rejected(spec, "request parts without requirement coverage")

    spec = sample_spec()
    spec["requirements"][0]["request_part_ids"] = ["P999"]
    assert_plan_rejected(spec, "unknown request parts")


def test_user_requirement_requires_request_mapping() -> None:
    spec = sample_spec()
    spec["requirements"][0]["request_part_ids"] = []
    assert_plan_rejected(spec, "must map to at least one request_part_id")


def test_extreme_task_must_be_split() -> None:
    spec = sample_spec()
    spec["tasks"][0]["complexity"] = "extreme"
    assert_plan_rejected(spec, "extreme complexity")


def test_high_complexity_requires_atomicity_reason() -> None:
    spec = sample_spec()
    spec["tasks"][0]["complexity"] = "high"
    spec["tasks"][0]["atomicity_rationale"] = "Too short"
    assert_plan_rejected(spec, "substantive atomicity_rationale")


def test_analysis_and_review_are_mandatory() -> None:
    spec = sample_spec()
    spec.pop("request_analysis")
    assert_plan_rejected(spec, "request_analysis")

    spec = sample_spec()
    spec["plan_review"]["coverage_complete"] = False
    assert_plan_rejected(spec, "coverage_complete")

    spec = sample_spec()
    spec.pop("execution_context")
    assert_plan_rejected(spec, "execution_context")

    spec = sample_spec()
    spec["plan_review"]["contexts_minimal"] = False
    assert_plan_rejected(spec, "contexts_minimal")


def test_autostart_rejects_open_questions() -> None:
    spec = sample_spec()
    spec["request_analysis"]["open_questions"] = ["Which incompatible API should be used?"]
    assert_plan_rejected(spec, "open_questions")


def test_route_escalation() -> None:
    """Legacy manifests (no failure classes) still climb one rung per failure."""
    config = planctl.default_config()
    config["claude"]["command"] = sys.executable
    config["codex"]["command"] = sys.executable
    task = {
        "provider": "claude",
        "allow_provider_fallback": False,
        "model_tier": "economy",
        "reasoning_effort": "low",
        "functional_failures": 0,
    }
    routes = []
    for failures in range(8):
        task["functional_failures"] = failures
        routes.append(run_isolated.choose_route(task, config, None))
    assert routes[0]["tier"] == "economy" and routes[0]["effort"] == "low"
    # Haiku accepts no effort flag, so the first Claude rung above economy is Sonnet.
    assert routes[1]["tier"] == "standard" and routes[1]["effort"] == "medium"
    assert routes[2]["tier"] == "standard" and routes[2]["effort"] == "high"
    assert routes[3]["tier"] == "strong" and routes[3]["effort"] == "medium"
    assert routes[4]["tier"] == "strong" and routes[4]["effort"] == "high"
    assert routes[5]["tier"] == "max"
    assert routes[7] == routes[6], "A single locked provider must stay at its highest route"

    task["provider"] = "auto"
    task["allow_provider_fallback"] = True
    task["functional_failures"] = 4
    switched = run_isolated.choose_route(task, config, None)
    assert switched["provider"] == "codex"


def test_evidence_based_escalation() -> None:
    """Failure classes, not counts, decide the next rung."""
    config = planctl.default_config()
    config["claude"]["command"] = sys.executable
    config["codex"]["command"] = sys.executable
    base = {
        "provider": "codex",
        "allow_provider_fallback": False,
        "model_tier": "standard",
        "reasoning_effort": "medium",
    }

    def route(classes: list[str]) -> dict[str, str]:
        task = {**base, "functional_failures": len(classes), "failure_classes": classes}
        return run_isolated.choose_route(task, config, None)

    assert (route([])["tier"], route([])["effort"]) == ("standard", "medium")
    # one mechanical slip repeats the rung; the second moves one rung up
    assert (route(["mechanical"])["tier"], route(["mechanical"])["effort"]) == ("standard", "medium")
    two_mech = route(["mechanical", "mechanical"])
    assert (two_mech["tier"], two_mech["effort"]) == ("strong", "low"), two_mech
    # a semantic failure on Codex skips Terra High and jumps straight to Astra Low
    semantic = route(["semantic"])
    assert (semantic["tier"], semantic["effort"], semantic["model"]) == ("strong", "low", "gpt-6-astra")
    # environmental failures never change the route
    assert route(["environmental", "environmental"]) == route([])
    # a second semantic failure jumps to the next tier boundary again
    twice = route(["semantic", "semantic"])
    assert twice["tier"] == "max"
    # budget exhaustion behaves like mechanical: repeat, then climb
    assert route(["budget"]) == route([])
    assert route(["budget", "budget"])["tier"] == "strong"

    claude = {**base, "provider": "claude", "functional_failures": 1, "failure_classes": ["semantic"]}
    claude_route = run_isolated.choose_route(claude, config, None)
    assert (claude_route["tier"], claude_route["model"]) == ("strong", "opus")


def test_ladder_exhaustion_blocks_instead_of_burning_attempts() -> None:
    config = planctl.default_config()
    config["claude"]["command"] = sys.executable
    config["codex"]["command"] = sys.executable
    base = {
        "provider": "claude",
        "allow_provider_fallback": False,
        "model_tier": "strong",
        "reasoning_effort": "high",
    }
    # strong/high on Claude leaves two rungs above (Fable High, Fable XHigh).
    one = {**base, "functional_failures": 1, "failure_classes": ["semantic"]}
    assert not run_isolated.ladder_exhausted(one, config, None)
    assert run_isolated.choose_route(one, config, None)["tier"] == "max"
    # mechanical slips at the top tier still climb effort before giving up
    mech = {**base, "functional_failures": 3, "failure_classes": ["semantic", "mechanical", "mechanical"]}
    assert not run_isolated.ladder_exhausted(mech, config, None)
    assert run_isolated.choose_route(mech, config, None)["effort"] == "xhigh"
    # a semantic failure at the strongest tier has no stronger tier to jump to: replan
    two = {**base, "functional_failures": 2, "failure_classes": ["semantic", "semantic"]}
    assert run_isolated.ladder_exhausted(two, config, None)
    # with a fallback provider still available, the ladder is not exhausted yet
    fallback = {**two, "provider": "auto", "allow_provider_fallback": True}
    assert not run_isolated.ladder_exhausted(fallback, config, None)
    assert run_isolated.ladder_exhausted({**fallback, "functional_failures": 4}, config, None)

    with tempfile.TemporaryDirectory() as temp:
        repo = Path(temp) / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        plan_dir = planctl.create_plan(repo, sample_spec(), ".ai-work", "ladder-block")
        _, manifest = planctl.load_plan(plan_dir)
        task = planctl.block_task(plan_dir, manifest, manifest["tasks"][0]["id"], "ladder exhausted", event="ladder_exhausted")
        assert task["status"] == "blocked" and task["attempts"] == 0
        assert task["history"][-1]["event"] == "ladder_exhausted"


def test_failure_class_state_and_plan_defect_block() -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = Path(temp) / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        plan_dir = planctl.create_plan(repo, sample_spec(), ".ai-work", "failure-class-test")
        _, manifest = planctl.load_plan(plan_dir)
        task_id = manifest["tasks"][0]["id"]
        planctl.claim_task(plan_dir, manifest, task_id, {"provider": "claude", "tier": "standard", "model": "x", "effort": "medium"})
        task = planctl.fail_task(plan_dir, manifest, task_id, "wrong approach", failure_class="semantic")
        assert task["failure_classes"] == ["semantic"]
        assert task["status"] == "pending"
        assert task["history"][-1]["failure_class"] == "semantic"
        planctl.claim_task(plan_dir, manifest, task_id, None)
        rate = planctl.fail_task(plan_dir, manifest, task_id, "429 too many requests", rate_limited=True)
        assert rate["failure_classes"] == ["semantic"], "availability is never failure evidence"
        planctl.claim_task(plan_dir, manifest, task_id, None)
        blocked = planctl.fail_task(plan_dir, manifest, task_id, "task boundary wrong", failure_class="plan_defect")
        assert blocked["status"] == "blocked", "plan_defect must stop the task for replanning"
        try:
            planctl.normalize_failure_class("bogus")
        except planctl.PlanError:
            pass
        else:
            raise AssertionError("unknown failure classes must be rejected")


def test_hard_decisions_contract() -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = Path(temp) / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        spec = sample_spec()
        spec["request_analysis"]["hard_decisions"] = [
            {
                "id": "HD001",
                "decision": "Keep the marker file at the repository root.",
                "rationale": "Both validation commands resolve the path from the repository root.",
                "route_used": "strong/medium",
                "source_refs": ["P001"],
            },
            {
                "decision": "Write the marker in UTF-8 without a BOM.",
                "rationale": "grep -q must match the literal word.",
            },
        ]
        plan_dir = planctl.create_plan(repo, spec, ".ai-work", "hard-decisions")
        _, manifest = planctl.load_plan(plan_dir)
        decisions = manifest["request_analysis"]["hard_decisions"]
        assert [item["id"] for item in decisions] == ["HD001", "HD002"], decisions
        assert decisions[0]["route_used"] == "strong/medium"
        assert decisions[1]["route_used"] == "" and decisions[1]["source_refs"] == []
        analysis = (plan_dir / "ANALYSIS.md").read_text(encoding="utf-8")
        assert "## Hard decisions" in analysis and "HD001" in analysis and "[strong/medium]" in analysis
        assert not planctl.validate_plan(plan_dir, manifest)

        legacy = sample_spec()  # no hard_decisions key at all
        plan_dir = planctl.create_plan(repo, legacy, ".ai-work", "hard-decisions-absent")
        _, manifest = planctl.load_plan(plan_dir)
        assert manifest["request_analysis"]["hard_decisions"] == []
        assert "None (no decision-first pass was needed)" in (plan_dir / "ANALYSIS.md").read_text(encoding="utf-8")

        for bad, message in (
            ({"id": "X1", "decision": "d", "rationale": "r"}, "must look like HD001"),
            ({"decision": "d", "rationale": "r", "route_used": "turbo/high"}, "route_used"),
            ({"decision": "", "rationale": "r"}, "decision"),
        ):
            broken = sample_spec()
            broken["request_analysis"]["hard_decisions"] = [bad]
            try:
                planctl.create_plan(repo, broken, ".ai-work", "hard-decisions-bad")
            except planctl.PlanError as exc:
                assert message in str(exc), (message, str(exc))
            else:
                raise AssertionError(f"expected rejection for {bad}")


def test_design_route_contract() -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = Path(temp) / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        # design_route requires high complexity
        bad = sample_spec()
        bad["tasks"][0]["design_route"] = {"model_tier": "strong", "reasoning_effort": "medium"}
        bad["tasks"][0]["complexity"] = "medium"
        try:
            planctl.create_plan(repo, bad, ".ai-work", "design-bad")
        except planctl.PlanError as exc:
            assert "design_route" in str(exc)
        else:
            raise AssertionError("design_route on a medium TODO must be rejected")

        good = sample_spec()
        good["tasks"][0]["complexity"] = "high"
        good["tasks"][0]["atomicity_rationale"] = (
            "Design and implementation share one invariant and one validation boundary; splitting would duplicate context."
        )
        good["tasks"][0]["design_route"] = {"model_tier": "strong", "reasoning_effort": "medium"}
        plan_dir = planctl.create_plan(repo, good, ".ai-work", "design-good")
        _, manifest = planctl.load_plan(plan_dir)
        task = manifest["tasks"][0]
        assert task["design_route"] == {"model_tier": "strong", "reasoning_effort": "medium"}
        assert task["design_phase"]["status"] == "pending"
        assert run_isolated.needs_design_phase(task)
        design_view = run_isolated.design_route_task(task)
        assert design_view["model_tier"] == "strong"
        note = plan_dir / run_isolated.design_note_relative(task)
        note.parent.mkdir(parents=True, exist_ok=True)
        note.write_text("# Design\n\nApproach: reuse parser.\n", encoding="utf-8")
        planctl.complete_design_phase(plan_dir, manifest, task["id"], run_isolated.design_note_relative(task), {"provider": "claude"})
        _, manifest = planctl.load_plan(plan_dir)
        task = manifest["tasks"][0]
        assert not run_isolated.needs_design_phase(task)
        prompt = run_isolated.append_design_note("BASE", plan_dir, task)
        assert "Design note:" in prompt and str(note.resolve()) in prompt
        # reset drops the stale note so a rerun designs again
        planctl.reset_task(plan_dir, manifest, task["id"])
        _, manifest = planctl.load_plan(plan_dir)
        assert manifest["tasks"][0]["design_phase"]["status"] == "pending"
        assert not note.exists()


def test_effort_flag_omitted_for_effortless_models() -> None:
    config = planctl.default_config()
    with tempfile.TemporaryDirectory() as temp:
        result_path = Path(temp) / "results" / "001.json"
        result_path.parent.mkdir(parents=True)
        haiku = run_isolated.build_worker_command(
            "claude",
            {"provider": "claude", "tier": "economy", "model": "haiku", "effort": "low"},
            config,
            "prompt",
            result_path,
        )
        assert "--effort" not in haiku, haiku
        sonnet = run_isolated.build_worker_command(
            "claude",
            {"provider": "claude", "tier": "standard", "model": "sonnet", "effort": "medium"},
            config,
            "prompt",
            result_path,
        )
        assert "--effort" in sonnet and "--max-turns" not in sonnet
        config["claude"]["max_turns"] = 40
        bounded = run_isolated.build_worker_command(
            "claude",
            {"provider": "claude", "tier": "standard", "model": "sonnet", "effort": "medium"},
            config,
            "prompt",
            result_path,
        )
        assert bounded[bounded.index("--max-turns") + 1] == "40"
        assert "--max-budget-usd" not in bounded
        config["claude"]["max_budget_usd"] = 2.5
        capped = run_isolated.build_worker_command(
            "claude",
            {"provider": "claude", "tier": "standard", "model": "sonnet", "effort": "medium"},
            config,
            "prompt",
            result_path,
        )
        assert capped[capped.index("--max-budget-usd") + 1] == "2.50"
        assert run_isolated.classify_report_failure(None, "Budget limit reached") == "budget"
        assert run_isolated.classify_report_failure(None, '{"subtype":"error_max_turns"}') == "budget"
        config["codex"]["rollout_token_budget"] = 250000
        codex = run_isolated.build_worker_command(
            "codex",
            {"provider": "codex", "tier": "economy", "model": "gpt-5.6-luna", "effort": "low"},
            config,
            "prompt",
            result_path,
        )
        assert "features.rollout_budget.limit_tokens=250000" in codex
        assert 'model_reasoning_effort="low"' in codex
        summary = run_isolated.build_summary_command(
            "claude",
            {"provider": "claude", "tier": "economy", "model": "haiku", "effort": "low"},
            config,
            "prompt",
            result_path,
        )
        assert "--effort" not in summary
    assert run_isolated.classify_report_failure({"failure_class": "semantic"}, "") == "semantic"
    assert run_isolated.classify_report_failure(None, "stopped: max turns reached") == "budget"
    assert run_isolated.classify_report_failure({"failure_class": "nonsense"}, "boom") == "unknown"


def test_command_prefix_keeps_windows_paths() -> None:
    prefix = run_isolated.command_prefix(sys.executable)
    assert prefix == [sys.executable], prefix
    assert run_isolated.executable_available(prefix)
    quoted = run_isolated.command_prefix(f'"{sys.executable}" --flag')
    assert quoted == [sys.executable, "--flag"], quoted
    assert run_isolated.command_prefix(["a", "b"]) == ["a", "b"]
    if os.name != "nt":
        return
    # npm shims are .cmd files; CreateProcess cannot launch them by bare name.
    with tempfile.TemporaryDirectory() as temp:
        shim = Path(temp) / "pae-fake-cli.cmd"
        shim.write_text("@echo off\r\necho fake ok %*\r\n", encoding="utf-8")
        original = os.environ.get("PATH", "")
        os.environ["PATH"] = temp + os.pathsep + original
        try:
            resolved = run_isolated.command_prefix("pae-fake-cli --flag")
            assert resolved[0].lower().endswith("pae-fake-cli.cmd"), resolved
            assert resolved[1:] == ["--flag"]
            completed = subprocess.run(resolved, capture_output=True, text=True)
            assert completed.returncode == 0 and "fake ok --flag" in completed.stdout
            assert run_isolated.command_prefix(["pae-fake-cli"])[0].lower().endswith(".cmd")
        finally:
            os.environ["PATH"] = original


def test_symlink_work_root_rejected() -> None:
    if not hasattr(os, "symlink"):
        return
    with tempfile.TemporaryDirectory() as temp:
        repo = Path(temp) / "repo"
        outside = Path(temp) / "outside"
        repo.mkdir()
        outside.mkdir()
        try:
            os.symlink(outside, repo / ".ai-work", target_is_directory=True)
        except OSError:
            return
        try:
            planctl.create_plan(repo, sample_spec(), ".ai-work", "unsafe")
        except planctl.PlanError as exc:
            assert "symlink" in str(exc).lower()
        else:
            raise AssertionError("Symlinked work root should have been rejected")



def write_completed_request(path: Path, language: str = "en") -> None:
    template = requestctl.render_template(language)
    content = (
        "Implement a complete authentication migration with compatibility, automated tests, "
        "rollback guidance, and deterministic validation for every requested outcome."
    )
    template = template.replace(
        requestctl.REQUEST_START,
        requestctl.REQUEST_START + "\n\n" + content,
        1,
    )
    requestctl.atomic_write_text(path, template)


def test_request_intake_and_vscode_editor() -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = Path(temp) / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        draft, language = requestctl.create_request_file(repo, language="en")
        assert language == "en"
        assert draft.parent == repo / ".ai-work" / "intake"
        raw = draft.read_text(encoding="utf-8")
        assert requestctl.INSTRUCTIONS_START in raw
        assert requestctl.REQUEST_START in raw
        assert "Continue — I finished writing the request" in raw
        assert requestctl.inspect_request_file(draft)["ready"] is False
        assert requestctl.latest_request_file(repo) == draft

        command, editor = requestctl.choose_editor_command(
            draft,
            env={"VSCODE_PID": "123"},
            which=lambda executable: f"/fake/{executable}" if executable == "code" else None,
        )
        assert editor == "code"
        assert command == ["code", "--reuse-window", str(draft)]

        write_completed_request(draft)
        inspected = requestctl.inspect_request_file(draft)
        assert inspected["ready"] is True
        assert "authentication migration" in inspected["request_text"]


def test_request_copy_move_and_concise_todo() -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = Path(temp) / "copy-repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        source = Path(temp) / "requirements.md"
        write_completed_request(source)
        plan_dir = planctl.create_plan(
            repo,
            sample_spec(),
            ".ai-work",
            "copy-request",
            request_file=source,
        )
        assert source.is_file(), "External request files must be preserved by default"
        assert (plan_dir / planctl.REQUEST_FILE).is_file()
        _, manifest = planctl.load_plan(plan_dir)
        assert manifest["request_source"]["import_mode"] == "copy"
        assert manifest["request_source"]["source_removed"] is False
        assert not planctl.validate_plan(plan_dir, manifest)

        todo = (plan_dir / "TODO.md").read_text(encoding="utf-8")
        task_lines = [line for line in todo.splitlines() if line.startswith("- [")]
        assert task_lines == [
            "- [ ] **001** — Create implementation marker",
            "- [ ] **002** — Verify marker contents",
        ]
        lowered = todo.lower()
        for forbidden in (
            "provider",
            "model",
            "reasoning",
            "complexity",
            "requirements",
            "attempts",
            "tasks/",
        ):
            assert forbidden not in lowered

    with tempfile.TemporaryDirectory() as temp:
        repo = Path(temp) / "move-repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        draft, _ = requestctl.create_request_file(repo, language="pt-BR")
        write_completed_request(draft, "pt-BR")
        plan_dir = planctl.create_plan(
            repo,
            sample_spec(),
            ".ai-work",
            "move-request",
            request_file=draft,
            move_request=True,
        )
        assert not draft.exists(), "Generated intake drafts must move into the plan workspace"
        assert not (repo / ".ai-work" / "intake").exists()
        assert (plan_dir / planctl.REQUEST_FILE).is_file()
        _, manifest = planctl.load_plan(plan_dir)
        assert manifest["request_source"]["import_mode"] == "move"
        assert manifest["request_source"]["source_removed"] is True
        assert not planctl.validate_plan(plan_dir, manifest)

def test_end_to_end_runner() -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = Path(temp) / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        plan_dir = planctl.create_plan(repo, sample_spec(), ".ai-work", "runner-test")
        fake = Path(temp) / "fake-claude"
        write_fake_claude(fake)
        config = planctl.read_json(plan_dir / planctl.CONFIG)
        config["provider_order"] = ["claude"]
        config["allow_provider_fallback"] = False
        config["stream_provider_output"] = False
        config["rate_limit"]["auto_wait"] = False
        config["claude"]["command"] = [sys.executable, str(fake)]
        config["claude"]["models"] = {tier: "fake-model" for tier in run_isolated.TIER_ORDER}
        config["summary"]["provider"] = "claude"
        planctl.atomic_write_json(plan_dir / planctl.CONFIG, config)

        args = argparse.Namespace(
            plan=str(plan_dir),
            provider=None,
            once=False,
            dry_run=False,
            no_wait=True,
            no_cleanup=False,
        )
        result = run_isolated.run_plan(args)
        assert result == 0
        assert not plan_dir.exists(), "Successful runner should safely clean planning artifacts"
        assert (repo / "implemented.txt").read_text(encoding="utf-8") == "implemented\n"


def test_end_to_end_design_phase() -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = Path(temp) / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        # The fake worker refuses to implement without a design note, proving the
        # runner dispatches the design phase first and hands the note over.
        (repo / "design-required.flag").write_text("001\n", encoding="utf-8")
        spec = sample_spec()
        spec["tasks"][0]["complexity"] = "high"
        spec["tasks"][0]["atomicity_rationale"] = (
            "Design and implementation share one invariant and one validation boundary; splitting would duplicate context."
        )
        spec["tasks"][0]["design_route"] = {"model_tier": "strong", "reasoning_effort": "medium"}
        plan_dir = planctl.create_plan(repo, spec, ".ai-work", "design-runner-test")
        fake = Path(temp) / "fake-claude"
        write_fake_claude(fake)
        config = planctl.read_json(plan_dir / planctl.CONFIG)
        config["provider_order"] = ["claude"]
        config["allow_provider_fallback"] = False
        config["stream_provider_output"] = False
        config["rate_limit"]["auto_wait"] = False
        config["claude"]["command"] = [sys.executable, str(fake)]
        config["claude"]["models"] = {tier: f"fake-{tier}" for tier in run_isolated.TIER_ORDER}
        config["summary"]["provider"] = "claude"
        planctl.atomic_write_json(plan_dir / planctl.CONFIG, config)

        args = argparse.Namespace(
            plan=str(plan_dir),
            provider=None,
            once=False,
            dry_run=False,
            no_wait=True,
            no_cleanup=True,
        )
        result = run_isolated.run_plan(args)
        assert result == 0, result
        _, manifest = planctl.load_plan(plan_dir)
        first = manifest["tasks"][0]
        assert first["status"] == "completed"
        assert first["design_phase"]["status"] == "completed"
        assert first["design_phase"]["route"]["model"] == "fake-strong"
        assert first["attempts"] == 1, "the design attempt must not consume an implementation attempt"
        assert first["current_route"]["model"] == "fake-economy", "implementation keeps the task's own cheaper route"
        note = plan_dir / first["design_phase"]["note_file"]
        assert note.is_file() and "Approach" in note.read_text(encoding="utf-8")
        assert (repo / "implemented.txt").read_text(encoding="utf-8") == "implemented\n"
        logs = sorted(path.name for path in (plan_dir / "logs").iterdir())
        assert any("design-attempt" in name for name in logs), logs


def main() -> int:
    test_plan_state()
    test_cycle_rejected()
    test_requirement_coverage_required()
    test_request_part_coverage_required()
    test_user_requirement_requires_request_mapping()
    test_extreme_task_must_be_split()
    test_high_complexity_requires_atomicity_reason()
    test_analysis_and_review_are_mandatory()
    test_autostart_rejects_open_questions()
    test_route_escalation()
    test_evidence_based_escalation()
    test_ladder_exhaustion_blocks_instead_of_burning_attempts()
    test_failure_class_state_and_plan_defect_block()
    test_hard_decisions_contract()
    test_design_route_contract()
    test_effort_flag_omitted_for_effortless_models()
    test_command_prefix_keeps_windows_paths()
    test_symlink_work_root_rejected()
    test_request_intake_and_vscode_editor()
    test_request_copy_move_and_concise_todo()
    test_end_to_end_runner()
    test_end_to_end_design_phase()
    print("All plan-and-execute self-tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
