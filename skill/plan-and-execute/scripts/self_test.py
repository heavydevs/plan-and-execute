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
        "plan_review": {
            "status": "approved",
            "reviewer": "fresh planning reviewer",
            "rounds": 1,
            "coverage_complete": True,
            "tasks_atomic": True,
            "dependencies_valid": True,
            "validations_sufficient": True,
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
                "scope": {
                    "in": ["Create the marker file"],
                    "out": ["No unrelated refactoring"],
                    "expected_files": ["implemented.txt"],
                },
                "acceptance_criteria": ["implemented.txt exists"],
                "validation_commands": ["test -f implemented.txt"],
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
                "dependencies": [1],
                "scope": {
                    "in": ["Check or update implemented.txt"],
                    "out": ["No unrelated files"],
                    "expected_files": ["implemented.txt"],
                },
                "acceptance_criteria": ["The marker contains implemented"],
                "validation_commands": ["grep -q implemented implemented.txt"],
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
if "--json-schema" in args:
    (root / "implemented.txt").write_text("implemented\n", encoding="utf-8")
    report = {
        "status": "completed",
        "summary": "Implemented the bounded task.",
        "changed_files": ["implemented.txt"],
        "validations": [{"command": "worker check", "passed": True, "details": "ok"}],
        "risks": [],
        "follow_ups": [],
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
        assert manifest["schema_version"] == 2
        assert not planctl.validate_plan(plan_dir, manifest)
        assert (plan_dir / "ANALYSIS.md").is_file()
        assert (plan_dir / "PLAN_REVIEW.md").is_file()
        audit = planctl.render_audit(manifest)
        assert "P001" in audit and "P002" in audit
        assert "R001" in audit and "R002" in audit
        assert "extreme: 0" in audit
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
            {"changed_files": ["implemented.txt"], "validation_results": []},
            "results/001.json",
        )
        assert planctl.next_runnable_task(manifest)["id"] == "002"
        planctl.claim_task(plan_dir, manifest, "002", route)
        planctl.complete_task(plan_dir, manifest, "002", {"changed_files": [], "validation_results": []}, None)
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


def test_autostart_rejects_open_questions() -> None:
    spec = sample_spec()
    spec["request_analysis"]["open_questions"] = ["Which incompatible API should be used?"]
    assert_plan_rejected(spec, "open_questions")


def test_route_escalation() -> None:
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
    for failures in range(5):
        task["functional_failures"] = failures
        routes.append(run_isolated.choose_route(task, config, None))
    assert routes[0]["tier"] == "economy" and routes[0]["effort"] == "low"
    assert routes[1]["tier"] == "economy" and routes[1]["effort"] == "medium"
    assert routes[2]["tier"] == "standard" and routes[2]["effort"] == "high"
    assert routes[3]["tier"] in {"strong", "max"}
    assert routes[4] == routes[3], "A single locked provider must stay at its highest route"

    task["provider"] = "auto"
    task["allow_provider_fallback"] = True
    task["functional_failures"] = 4
    switched = run_isolated.choose_route(task, config, None)
    assert switched["provider"] == "codex"


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
        config["claude"]["command"] = str(fake)
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
    test_symlink_work_root_rejected()
    test_end_to_end_runner()
    print("All plan-and-execute self-tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
