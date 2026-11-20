#!/usr/bin/env python3
"""Regression and acceptance self-tests for Tasks 012/013: plan contract and schema-v4 state.

Covers AC01..AC08 plus prepared-research non-proof, strict JSON, orphan reviews,
stale writers, crash recovery before/after authority publication, legacy schema v1-v3
preservation, selective invalidation, and the single receipt-validity function.
The `test_r0*` cases are the task-013 corrections of the independent review findings
(review completion, required revision generation, pre-generation upgrade, writer-lock
contention/takeover, on-disk scoped-input binding, carried digests, staged rollback).
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

OPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = OPT_DIR.parents[1]
SCRIPTS_DIR = REPO_ROOT / "skill" / "plan-and-execute" / "scripts"
for _path in (SCRIPTS_DIR, OPT_DIR):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

import baseline_contracts  # noqa: E402
from artifact_contract import install_plan_contract  # noqa: E402

planctl = install_plan_contract()


def make_repo(base: Path, name: str = "repo") -> Path:
    repo = base / name
    repo.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
    (repo / ".gitignore").write_text("\n", encoding="utf-8")
    subprocess.run(["git", "add", ".gitignore"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=repo, check=True)
    return repo


def three_task_spec(repo: Path | None = None) -> dict[str, Any]:
    scoped_digests: dict[str, str] = {}
    if repo is not None:
        src = repo / "src_a.txt"
        src.write_text("alpha-v1\n", encoding="utf-8")
        scoped_digests = {"src_a.txt": hashlib.sha256(src.read_bytes()).hexdigest()}
    return {
        "title": "Plan contract fixture",
        "summary": "Verify staged generations, selective invalidation, and recovery across three tasks.",
        "language": "English",
        "plan_mode": "single_implementation",
        "request_analysis": {
            "request_parts": [
                {"id": "P001", "text": "Implement component A with scoped input binding."},
                {"id": "P002", "text": "Implement component B depending on component A."},
                {"id": "P003", "text": "Implement independent component C."},
            ],
            "repository_findings": ["The fixture repository starts with no implementation modules."],
            "research_decision": "Local contract test requires no external research.",
            "research_findings": [],
            "assumptions": ["Python 3 executes all deterministic checks."],
            "risks": ["Partial projection writes could diverge from manifest authority."],
            "open_questions": [],
            "decomposition_strategy": "Separate A, dependent B, and independent C so invalidation stays scoped.",
        },
        "requirements": [
            {
                "id": "R001",
                "text": "Component A writes a.out matching the bound input contract.",
                "source": "user",
                "priority": "must",
                "request_part_ids": ["P001"],
            },
            {
                "id": "R002",
                "text": "Component B consumes a.out and writes b.out.",
                "source": "user",
                "priority": "must",
                "request_part_ids": ["P002"],
            },
            {
                "id": "R003",
                "text": "Component C writes c.out independently of A and B.",
                "source": "user",
                "priority": "must",
                "request_part_ids": ["P003"],
                "supersession_note": "Single implementation plan supersedes the earlier second-plan clause.",
            },
        ],
        "global_constraints": ["Do not modify files outside the fixture repository."],
        "execution_context": {
            "global": {
                "decision": "create",
                "rationale": "All three tasks share one output directory rule that must remain consistent across revisions.",
                "items": [
                    {
                        "id": "G001",
                        "kind": "constraint",
                        "text": "Every fixture output file uses UTF-8 text with LF line endings.",
                        "necessity": "All three fixture tasks write output files checked by deterministic tests.",
                        "source_refs": ["request:P001", "requirement:R001"],
                    }
                ],
            },
            "scoped": [
                {
                    "id": "ab-chain",
                    "title": "A to B interface",
                    "rationale": "Only tasks 001 and 002 share the a.out handoff format; task 003 is independent.",
                    "task_ids": ["001", "002"],
                    "items": [
                        {
                            "id": "C001",
                            "kind": "interface",
                            "text": "a.out stores one key-value line consumed by task 002.",
                            "necessity": "Tasks 001 and 002 must agree on the handoff format while task 003 stays isolated.",
                            "source_refs": ["requirement:R001", "requirement:R002"],
                        }
                    ],
                }
            ],
        },
        "plan_review": {
            "status": "approved",
            "reviewer": "fresh contract reviewer",
            "rounds": 1,
            "coverage_complete": True,
            "tasks_atomic": True,
            "dependencies_valid": True,
            "validations_sufficient": True,
            "contexts_minimal": True,
            "context_boundaries_sound": True,
            "unresolved_findings": [],
            "notes": ["All requirements map cleanly to isolated tasks with deterministic checks."],
        },
        "autostart": True,
        "cleanup_on_success": True,
        "tasks": [
            {
                "id": 1,
                "title": "Implement component A",
                "objective": "Write a.out derived from src_a.txt.",
                "requirement_ids": ["R001"],
                "complexity": "low",
                "atomicity_rationale": "Component A has one input contract and one verification check.",
                "context_boundary": {
                    "shared_context": ["Writing and validating a.out share one format contract."],
                    "why_one_todo": "One worker can produce and verify a.out without a cross-task handoff.",
                    "separate_from": ["Downstream B and independent C belong to separate TODOs."],
                },
                "scope": {"in": ["Write a.out"], "out": ["Do not edit c.out"], "expected_files": ["a.out"]},
                "dependencies": [],
                "implementation_guidance": ["Read src_a.txt and write deterministic UTF-8 text."],
                "acceptance_criteria": ["a.out exists with component A v1 output."],
                "validation_commands": ["python -c \"assert True\""],
                **({"scoped_inputs": ["src_a.txt"], "scoped_input_digests": scoped_digests} if scoped_digests else {}),
                "subtasks": [
                    {"id": "S001", "title": "Write a.out", "objective": "Create a.out matching R001."}
                ],
                "learning_targets": [],
                "provider": "auto",
                "model_tier": "economy",
                "reasoning_effort": "medium",
            },
            {
                "id": 2,
                "title": "Implement component B",
                "objective": "Read a.out and write b.out.",
                "requirement_ids": ["R002"],
                "complexity": "low",
                "atomicity_rationale": "Component B consumes a.out and validates b.out in one boundary.",
                "context_boundary": {
                    "shared_context": ["Reading a.out and validating b.out share one interface."],
                    "why_one_todo": "One worker can consume a.out and verify b.out in one isolated turn.",
                    "separate_from": ["Component A production and independent C remain separate."],
                },
                "scope": {"in": ["Write b.out"], "out": ["Do not edit c.out"], "expected_files": ["b.out"]},
                "dependencies": [1],
                "implementation_guidance": ["Consume a.out without modifying it."],
                "acceptance_criteria": ["b.out reflects a.out."],
                "validation_commands": ["python -c \"assert True\""],
                "subtasks": [
                    {"id": "S001", "title": "Write b.out", "objective": "Create b.out matching R002."}
                ],
                "learning_targets": [],
                "provider": "auto",
                "model_tier": "economy",
                "reasoning_effort": "medium",
            },
            {
                "id": 3,
                "title": "Implement component C",
                "objective": "Write c.out independently of components A and B.",
                "requirement_ids": ["R003"],
                "complexity": "low",
                "atomicity_rationale": "Component C has an independent output and check.",
                "context_boundary": {
                    "shared_context": ["Writing and verifying c.out share one independent file contract."],
                    "why_one_todo": "One worker can produce and verify c.out without A or B context.",
                    "separate_from": ["Components A and B remain isolated from component C."],
                },
                "scope": {"in": ["Write c.out"], "out": ["Do not touch a.out or b.out"], "expected_files": ["c.out"]},
                "dependencies": [],
                "implementation_guidance": ["Keep c.out independent of A and B."],
                "acceptance_criteria": ["c.out exists with component C output."],
                "validation_commands": ["python -c \"assert True\""],
                "subtasks": [
                    {"id": "S001", "title": "Write c.out", "objective": "Create c.out matching R003."}
                ],
                "learning_targets": [],
                "provider": "auto",
                "model_tier": "economy",
                "reasoning_effort": "medium",
            },
        ],
    }


def complete_one_task(plan_dir: Path, manifest: dict[str, Any], task_id: str, changed: list[str]) -> None:
    route = {"provider": "codex", "model": "fake", "tier": "economy", "effort": "medium"}
    planctl.claim_task(plan_dir, manifest, task_id, route)
    task = planctl.find_task(manifest, task_id)
    for sub in task["subtasks"]:
        planctl.set_subtask_state(plan_dir, manifest, task_id, sub["id"], "in_progress")
        planctl.set_subtask_state(plan_dir, manifest, task_id, sub["id"], "completed")
    report = {
        "status": "completed",
        "summary": f"Completed task {task_id} cleanly.",
        "changed_files": changed,
        "validations": [{"command": task["validation_commands"][0], "passed": True, "details": "Exit 0."}],
        "validation_results": [],
        "risks": [],
        "follow_ups": [],
        "context_files_read": list(task.get("context_files", [])),
        "learning_files_read": [],
        "completed_subtask_ids": [s["id"] for s in task["subtasks"]],
        "reusable_learnings": [],
        "related_task_reads": [],
        "blocked_reason": None,
    }
    planctl.complete_task(plan_dir, manifest, task_id, report, f"results/{task_id}.json")


def expect_plan_error(fn, expected_fragment: str) -> None:
    try:
        fn()
    except planctl.PlanError as exc:
        assert expected_fragment.casefold() in str(exc).casefold(), (
            f"Expected {expected_fragment!r} in PlanError, got: {exc}"
        )
    else:
        raise AssertionError(f"Expected PlanError containing {expected_fragment!r}")


def snapshot_plan_files(plan_dir: Path) -> dict[str, bytes]:
    out: dict[str, bytes] = {}
    for p in sorted(plan_dir.rglob("*")):
        if p.is_file():
            out[p.relative_to(plan_dir).as_posix()] = p.read_bytes()
    return out


def test_ac01_failed_revision_preserves_previous_manifest_and_projections() -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = make_repo(Path(temp), "ac01")
        spec = three_task_spec(repo)
        plan_dir = planctl.create_plan(repo, spec, ".ai-work", "ac01-plan")
        before = snapshot_plan_files(plan_dir)

        # 1) Cycle in dependencies
        cyclic = copy.deepcopy(spec)
        cyclic["tasks"][0]["dependencies"] = [2]
        expect_plan_error(
            lambda: planctl.revise_plan(plan_dir, cyclic, amendment="Introduce cycle", expected_generation=1),
            "cycle",
        )

        # 2) Uncovered requirement
        uncovered = copy.deepcopy(spec)
        uncovered["tasks"][2]["requirement_ids"] = ["R001"]
        expect_plan_error(
            lambda: planctl.revise_plan(plan_dir, uncovered, amendment="Drop R003 consumer", expected_generation=1),
            "without executable TODO coverage",
        )

        # 3) Orphan review (unknown reviewed task) and review missing dependency
        orphan = copy.deepcopy(spec)
        orphan["tasks"][2]["review_of"] = "999"
        expect_plan_error(
            lambda: planctl.revise_plan(plan_dir, orphan, amendment="Add orphan review", expected_generation=1),
            "orphan review",
        )
        missing_dep_review = copy.deepcopy(spec)
        missing_dep_review["tasks"][2]["review_of"] = "001"
        expect_plan_error(
            lambda: planctl.revise_plan(plan_dir, missing_dep_review, amendment="Review without dep", expected_generation=1),
            "must depend on it",
        )

        # 4) Vague derived text rejected by artifact_contract before staging activation
        vague = copy.deepcopy(spec)
        vague["tasks"][0]["acceptance_criteria"] = ["a.out works robustly as appropriate."]
        expect_plan_error(
            lambda: planctl.revise_plan(plan_dir, vague, amendment="Vague acceptance", expected_generation=1),
            "vague wording",
        )

        # Previous manifest and all projections remain untouched and readable.
        assert not (plan_dir / planctl.STAGING_DIRECTORY).exists()
        assert snapshot_plan_files(plan_dir) == before
        _, loaded = planctl.load_plan(plan_dir)
        assert loaded["generation"] == 1
        assert planctl.validate_plan(plan_dir, loaded) == []


def test_ac02_coverage_strict_json_and_subtask_consistency() -> None:
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        repo = make_repo(base, "ac02")
        spec = three_task_spec(repo)
        plan_dir = planctl.create_plan(repo, spec, ".ai-work", "ac02-plan")
        _, manifest = planctl.load_plan(plan_dir)
        assert planctl.validate_plan(plan_dir, manifest) == []
        plan_md = (plan_dir / "PLAN.md").read_text(encoding="utf-8")
        assert "superseded:" in plan_md and "R003" in plan_md

        # Missing acceptance / validation rejected
        no_acc = copy.deepcopy(spec)
        no_acc["tasks"][0]["acceptance_criteria"] = []
        expect_plan_error(
            lambda: planctl.create_plan(repo, no_acc, ".ai-work", "no-acc"),
            "acceptance criterion",
        )
        no_val = copy.deepcopy(spec)
        no_val["tasks"][0]["validation_commands"] = []
        expect_plan_error(
            lambda: planctl.create_plan(repo, no_val, ".ai-work", "no-val"),
            "validation command",
        )

        # Duplicate JSON keys and non-finite numbers rejected
        dup_path = base / "dup.json"
        dup_path.write_text('{"a": 1, "a": 2}\n', encoding="utf-8")
        expect_plan_error(lambda: planctl.read_json(dup_path), "Duplicate JSON key")
        nan_path = base / "nan.json"
        nan_path.write_text('{"x": NaN}\n', encoding="utf-8")
        expect_plan_error(lambda: planctl.read_json(nan_path), "Non-finite JSON")
        inf_path = base / "inf.json"
        inf_path.write_text('{"x": Infinity}\n', encoding="utf-8")
        expect_plan_error(lambda: planctl.read_json(inf_path), "Non-finite JSON")

        # Inconsistent (non-canonical) subtask ID in manifest detected by validate_plan
        bad_manifest = copy.deepcopy(manifest)
        bad_manifest["tasks"][0]["subtasks"][0]["id"] = "s1"
        errors = planctl.validate_plan(plan_dir, bad_manifest)
        assert any("inconsistent subtask id" in err for err in errors), errors

        # Valid post-implementation review task passes graph validation
        reviewed = copy.deepcopy(spec)
        reviewed["tasks"][2]["review_of"] = "001"
        reviewed["tasks"][2]["dependencies"] = [1]
        reviewed["tasks"][2]["requires_independent_review"] = True
        reviewed_dir = planctl.create_plan(repo, reviewed, ".ai-work", "ac02-review")
        assert planctl.validate_plan(reviewed_dir) == []


def test_ac03_transformed_research_task_and_prepared_research_not_proof() -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = make_repo(Path(temp), "ac03")
        report_rel = "docs/prepared/012-sample.md"
        report_file = repo / report_rel
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text("# Prepared research report\n\nPending implementation.\n", encoding="utf-8")
        report_sha = hashlib.sha256(report_file.read_bytes()).hexdigest()

        spec = three_task_spec(repo)
        spec["tasks"][0]["research_metadata"] = {
            "former_kind": "research",
            "prepared_report": report_rel,
            "prepared_report_sha256": report_sha,
            "research_status": "prepared",
            "implementation_status": "pending",
            "independent_review_status": "pending",
        }
        spec["tasks"][0]["subtasks"] = [
            {
                "id": "S001",
                "title": "Implement contract from assigned report",
                "objective": f"Read {report_rel} and implement component A from its recommendations.",
            }
        ]
        plan_dir = planctl.create_plan(repo, spec, ".ai-work", "ac03-plan")
        _, manifest = planctl.load_plan(plan_dir)
        task1 = planctl.find_task(manifest, "001")
        assert task1["status"] == "pending"
        assert all(sub["status"] == "pending" for sub in task1["subtasks"])
        assert report_rel in task1["subtasks"][0]["objective"]

        # Reject transformed research task whose subtasks omit the assigned report
        no_ref = copy.deepcopy(spec)
        no_ref["tasks"][0]["subtasks"][0]["objective"] = "Implement component A without citing report."
        expect_plan_error(
            lambda: planctl.create_plan(repo, no_ref, ".ai-work", "ac03-noref"),
            "assigned report",
        )

        # Reject spec claiming completed from prepared research
        claimed_done = copy.deepcopy(spec)
        claimed_done["tasks"][0]["status"] = "completed"
        expect_plan_error(
            lambda: planctl.create_plan(repo, claimed_done, ".ai-work", "ac03-done"),
            "cannot start as completed",
        )
        claimed_impl = copy.deepcopy(spec)
        claimed_impl["tasks"][0]["research_metadata"]["implementation_status"] = "completed"
        expect_plan_error(
            lambda: planctl.create_plan(repo, claimed_impl, ".ai-work", "ac03-impl"),
            "prepared research is not implementation completion",
        )
        claimed_rev = copy.deepcopy(spec)
        claimed_rev["tasks"][0]["research_metadata"]["independent_review_status"] = "approved"
        expect_plan_error(
            lambda: planctl.create_plan(repo, claimed_rev, ".ai-work", "ac03-rev"),
            "prepared research is not independent-review completion",
        )

        # Prepared research receipt is rejected by the single receipt-validity function
        fake_research_receipt = {
            "task_id": "001",
            "status": "completed",
            "evidence_kind": "prepared_research",
            "contract_digest": task1["contract_digest"],
        }
        verdict = planctl.validate_receipt(fake_research_receipt, task1, manifest=manifest)
        assert verdict["valid"] is False
        assert "prepared_research_is_not_completion_proof" in verdict["reasons"]

        # Pending independent review is also rejected
        pending_review_receipt = {
            "task_id": "001",
            "status": "completed",
            "contract_digest": task1["contract_digest"],
            "independent_review_status": "pending",
        }
        verdict_rev = planctl.validate_receipt(pending_review_receipt, task1, manifest=manifest)
        assert verdict_rev["valid"] is False
        assert "independent_review_pending" in verdict_rev["reasons"]

        # complete_task rejects a prepared-research report
        planctl.claim_task(plan_dir, manifest, "001", None)
        planctl.set_subtask_state(plan_dir, manifest, "001", "S001", "in_progress")
        planctl.set_subtask_state(plan_dir, manifest, "001", "S001", "completed")
        expect_plan_error(
            lambda: planctl.complete_task(
                plan_dir,
                manifest,
                "001",
                {
                    "status": "completed",
                    "summary": "Attempted completion with prepared research only.",
                    "evidence_kind": "prepared_research",
                    "changed_files": [],
                    "validations": [],
                    "risks": [],
                    "follow_ups": [],
                    "completed_subtask_ids": ["S001"],
                    "reusable_learnings": [],
                },
                None,
            ),
            "prepared research",
        )


def _create_legacy_plan(repo: Path, schema_version: int, plan_id: str) -> tuple[Path, Path, str]:
    plan_dir = repo / ".ai-work" / plan_id
    (plan_dir / "tasks").mkdir(parents=True)
    task_file = plan_dir / "tasks" / "001-legacy-task.md"
    legacy_markdown = f"# Legacy schema v{schema_version} task\n\nCustom hand-preserved legacy prose.\n"
    task_file.write_text(legacy_markdown, encoding="utf-8")
    planctl.atomic_write_json(
        plan_dir / planctl.SENTINEL,
        {"schema_version": schema_version, "plan_id": plan_id, "repo_root": str(repo.resolve())},
    )
    planctl.atomic_write_json(plan_dir / planctl.CONFIG, planctl.default_config())
    manifest: dict[str, Any] = {
        "schema_version": schema_version,
        "plan_id": plan_id,
        "title": f"Legacy v{schema_version} plan",
        "summary": "Legacy workspace for backward compatibility testing.",
        "repo_root": str(repo.resolve()),
        "work_root": ".ai-work",
        "state": "planned",
        "autostart": True,
        "cleanup_on_success": True,
        "created_at": planctl.now_utc(),
        "updated_at": planctl.now_utc(),
        "tasks": [
            {
                "id": "001",
                "slug": "legacy-task",
                "title": "Legacy task",
                "objective": "Run legacy task cleanly.",
                "dependencies": [],
                "related_task_reads": [],
                "scope": {"in": ["Legacy"], "out": [], "expected_files": []},
                "implementation_guidance": [],
                "acceptance_criteria": ["Legacy criterion holds."],
                "validation_commands": ["python -c \"assert True\""],
                "file": "tasks/001-legacy-task.md",
                "status": "pending",
                "attempts": 0,
                "functional_failures": 0,
                "history": [],
            }
        ],
    }
    if schema_version >= 2:
        manifest["request_analysis"] = {
            "request_parts": [{"id": "P001", "text": "Preserve legacy plan compatibility."}],
            "repository_findings": ["Legacy repository fixture."],
            "research_decision": "No research required for legacy fixture.",
            "research_findings": [],
            "assumptions": [],
            "risks": [],
            "open_questions": [],
            "decomposition_strategy": "Single legacy task.",
            "hard_decisions": [],
        }
        manifest["requirements"] = [
            {
                "id": "R001",
                "text": "Preserve legacy plan file format.",
                "source": "user",
                "priority": "must",
                "request_part_ids": ["P001"],
            }
        ]
        manifest["plan_review"] = {
            "status": "approved",
            "reviewer": "legacy reviewer",
            "rounds": 1,
            "coverage_complete": True,
            "tasks_atomic": True,
            "dependencies_valid": True,
            "validations_sufficient": True,
            **({"contexts_minimal": True} if schema_version >= 3 else {}),
            "unresolved_findings": [],
            "notes": ["Legacy review passed."],
        }
        manifest["tasks"][0]["complexity"] = "low"
        manifest["tasks"][0]["atomicity_rationale"] = "One legacy task."
        manifest["tasks"][0]["requirement_ids"] = ["R001"]
        (plan_dir / "ANALYSIS.md").write_text("# Legacy Analysis\n", encoding="utf-8")
        (plan_dir / "PLAN_REVIEW.md").write_text("# Legacy Review\n", encoding="utf-8")
    if schema_version >= 3:
        manifest["execution_context"] = {
            "global": {
                "decision": "omit",
                "rationale": "Single legacy task needs no shared execution context file.",
                "items": [],
                "file": None,
            },
            "scoped": [],
        }
        manifest["tasks"][0]["context_files"] = []
    planctl.atomic_write_json(plan_dir / planctl.MANIFEST, manifest)
    (plan_dir / "TODO.md").write_text(planctl.render_todo(manifest), encoding="utf-8")
    return plan_dir, task_file, legacy_markdown


def test_ac04_legacy_schema_1_to_3_preserved_without_schema4_rewrite() -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = make_repo(Path(temp), "ac04")
        for version in (1, 2, 3):
            plan_dir, task_file, original_md = _create_legacy_plan(repo, version, f"legacy-v{version}")
            _, manifest = planctl.load_plan(plan_dir)
            assert manifest["schema_version"] == version
            assert planctl.validate_plan(plan_dir, manifest) == []

            # save_manifest must NOT rewrite legacy task files or attach schema-4 projection state
            planctl.save_manifest(plan_dir, manifest)
            assert task_file.read_text(encoding="utf-8") == original_md
            assert not (plan_dir / planctl.PROJECTION_STATE_FILE).exists()
            assert "generation" not in planctl.read_json(plan_dir / planctl.MANIFEST)

            # recover_projections must preserve legacy files untouched
            rec = planctl.recover_projections(plan_dir)
            assert rec["legacy_preserved"] is True
            assert rec["rebuilt_files"] == []
            assert task_file.read_text(encoding="utf-8") == original_md

            # revise_plan must refuse to silently rewrite legacy schema 1-3 with schema-4 rules
            expect_plan_error(
                lambda pd=plan_dir: planctl.revise_plan(pd, three_task_spec(repo), amendment="Attempt legacy rewrite"),
                f"legacy schema-v{version}",
            )
            assert task_file.read_text(encoding="utf-8") == original_md


def test_ac05_no_second_plan_and_no_nonexistent_research_output() -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = make_repo(Path(temp), "ac05")
        spec = three_task_spec(repo)

        # Active task creating a second plan is rejected in single_implementation mode
        second_plan = copy.deepcopy(spec)
        second_plan["tasks"][2]["title"] = "Generate a second plan for implementation"
        expect_plan_error(
            lambda: planctl.create_plan(repo, second_plan, ".ai-work", "ac05-plan2"),
            "second plan",
        )

        # Task depending on a nonexistent research output is rejected
        missing_research = copy.deepcopy(spec)
        missing_research["tasks"][0]["research_metadata"] = {
            "former_kind": "research",
            "prepared_report": "docs/prepared/does-not-exist.md",
            "research_status": "prepared",
        }
        missing_research["tasks"][0]["subtasks"][0]["objective"] = (
            "Implement from docs/prepared/does-not-exist.md."
        )
        expect_plan_error(
            lambda: planctl.create_plan(repo, missing_research, ".ai-work", "ac05-missing-rep"),
            "nonexistent research output",
        )

        # Mismatched research report hash is rejected
        real_rep = repo / "docs" / "prepared" / "real.md"
        real_rep.parent.mkdir(parents=True, exist_ok=True)
        real_rep.write_text("# Real report\n", encoding="utf-8")
        stale_hash = copy.deepcopy(spec)
        stale_hash["tasks"][0]["research_metadata"] = {
            "former_kind": "research",
            "prepared_report": "docs/prepared/real.md",
            "prepared_report_sha256": "0" * 64,
            "research_status": "prepared",
        }
        stale_hash["tasks"][0]["subtasks"][0]["objective"] = "Implement from docs/prepared/real.md."
        expect_plan_error(
            lambda: planctl.create_plan(repo, stale_hash, ".ai-work", "ac05-stale-hash"),
            "hash mismatch",
        )

    # Also verify the live repository optimization plan satisfies AC05 & deterministic preflight.
    preflight = baseline_contracts.run_preflight(REPO_ROOT, task_id="012")
    assert preflight["status"] == "passed"
    assert preflight["independent_review_fabricated"] is False
    coverage = baseline_contracts.run_source_and_contract_coverage(REPO_ROOT, native=True)
    assert coverage["status"] == "passed"


def test_ac06_crash_before_and_after_authority_publication_and_recovery() -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = make_repo(Path(temp), "ac06")
        spec = three_task_spec(repo)
        plan_dir = planctl.create_plan(repo, spec, ".ai-work", "ac06-plan")

        # --- Case 1: Interruption BEFORE authority publication ---
        orphan_stage = plan_dir / planctl.STAGING_DIRECTORY / "gen-2-aborted"
        orphan_stage.mkdir(parents=True)
        (orphan_stage / "manifest.json").write_text('{"generation": 2}\n', encoding="utf-8")
        (orphan_stage / "TODO.md").write_text("# Aborted gen 2\n", encoding="utf-8")
        rec_before = planctl.recover_projections(plan_dir)
        assert not (plan_dir / planctl.STAGING_DIRECTORY).exists()
        assert rec_before["removed_staging_dirs"] == [".staging/gen-2-aborted"]
        assert rec_before["tasks_completed_changed"] is False
        _, m1 = planctl.load_plan(plan_dir)
        assert m1["generation"] == 1
        assert all(t["status"] == "pending" for t in m1["tasks"])
        assert planctl.validate_plan(plan_dir, m1) == []

        # --- Case 2: Interruption AFTER authority publication, BEFORE task rendering ---
        revised = copy.deepcopy(spec)
        revised["tasks"][0]["title"] = "Implement renamed component A v2"
        revised["tasks"][0]["acceptance_criteria"] = ["a.out exists with component A v2 output."]
        # Also remove scoped context in gen 2 to confirm stale context files are not combined across generations
        revised["execution_context"]["scoped"] = []

        old_task1_file = plan_dir / m1["tasks"][0]["file"]
        old_scoped_file = plan_dir / "contexts" / "ab-chain.md"
        assert old_task1_file.is_file() and old_scoped_file.is_file()

        def simulate_crash(_pd: Path, _staged: dict[str, Any]) -> None:
            raise RuntimeError("Simulated crash right after manifest.json replacement")

        try:
            planctl.revise_plan(
                plan_dir,
                revised,
                amendment="Rename component A and remove scoped context",
                expected_generation=1,
                _after_authority_publish=simulate_crash,
            )
        except RuntimeError as exc:
            assert "Simulated crash" in str(exc)
        else:
            raise AssertionError("Expected simulated crash after authority publication")

        # Authoritative manifest is now gen 2, while projections still lag at gen 1!
        _, m2 = planctl.load_plan(plan_dir)
        assert m2["generation"] == 2
        assert old_task1_file.is_file(), "Stale gen-1 task projection still sits on disk before recovery"
        new_task1_file = plan_dir / m2["tasks"][0]["file"]
        assert not new_task1_file.is_file(), "Gen-2 task projection was not yet rendered before crash"
        lag_errors = planctl.validate_plan(plan_dir, m2)
        assert any("lag authoritative manifest generation" in err for err in lag_errors), lag_errors

        # Recovery rebuilds consistent gen-2 projections, removes gen-1 stale files, never marks tasks complete
        rec_after = planctl.recover_projections(plan_dir)
        assert rec_after["projection_lag_detected"] is True
        assert rec_after["tasks_completed_changed"] is False
        assert not old_task1_file.exists(), "Recovery must not combine gen-1 and gen-2 task files"
        assert not old_scoped_file.exists(), "Recovery must remove stale gen-1 scoped context"
        assert new_task1_file.is_file()
        assert not (plan_dir / planctl.STAGING_DIRECTORY).exists()
        _, m2_after = planctl.load_plan(plan_dir)
        assert all(t["status"] == "pending" for t in m2_after["tasks"])
        assert planctl.validate_plan(plan_dir, m2_after) == []

        # --- Case 3: Crash during save_manifest (after manifest replace, before task rendering) ---
        m2_after["tasks"][0]["status"] = "in_progress"
        m2_after["tasks"][0]["attempts"] = 1
        try:
            planctl.save_manifest(plan_dir, m2_after, _after_manifest_replace=simulate_crash)
        except RuntimeError:
            pass
        else:
            raise AssertionError("Expected simulated crash in save_manifest")
        assert planctl.validate_plan(plan_dir) != []
        rec_save = planctl.recover_projections(plan_dir)
        assert rec_save["projection_lag_detected"] is True
        assert rec_save["tasks_completed_changed"] is False
        _, m3 = planctl.load_plan(plan_dir)
        assert m3["generation"] == 3
        assert m3["tasks"][0]["status"] == "in_progress"
        assert planctl.validate_plan(plan_dir, m3) == []


def test_ac07_stale_plan_writer_rejected_and_writer_lock() -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = make_repo(Path(temp), "ac07")
        spec = three_task_spec(repo)
        plan_dir = planctl.create_plan(repo, spec, ".ai-work", "ac07-plan")

        # Two writers read generation 1
        _, writer_a = planctl.load_plan(plan_dir)
        _, writer_b = planctl.load_plan(plan_dir)
        assert writer_a["generation"] == 1 and writer_b["generation"] == 1

        # Writer A advances authority to generation 2
        planctl.claim_task(plan_dir, writer_a, "001", None)
        _, current = planctl.load_plan(plan_dir)
        assert current["generation"] == 2

        # Stale writer B cannot overwrite generation 2 via save_manifest or revise_plan
        expect_plan_error(
            lambda: planctl.save_manifest(plan_dir, writer_b),
            "Stale plan writer",
        )
        expect_plan_error(
            lambda: planctl.revise_plan(plan_dir, spec, amendment="Stale revision", expected_generation=1),
            "Stale plan writer",
        )

        # Authority remains at generation 2 with writer A's state intact
        _, after = planctl.load_plan(plan_dir)
        assert after["generation"] == 2
        assert planctl.find_task(after, "001")["status"] == "in_progress"

        # Stale dead-PID writer lock is recovered cleanly
        lock_path = plan_dir / planctl.WRITER_LOCK_FILE
        lock_path.write_text(
            json.dumps({"pid": 99999999, "hostname": planctl.socket.gethostname(), "acquired_at": planctl.now_utc()}),
            encoding="utf-8",
        )
        with planctl.plan_writer_lock(plan_dir, timeout_seconds=1.0):
            assert lock_path.is_file()
        assert not lock_path.exists()


def test_ac08_selective_invalidation_receipt_history_and_extension_hook() -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = make_repo(Path(temp), "ac08")
        spec = three_task_spec(repo)
        plan_dir = planctl.create_plan(repo, spec, ".ai-work", "ac08-plan")
        _, manifest = planctl.load_plan(plan_dir)

        # Complete all three tasks (001, 002 -> depends on 001, 003 -> independent)
        complete_one_task(plan_dir, manifest, "001", ["a.out"])
        complete_one_task(plan_dir, manifest, "002", ["b.out"])
        complete_one_task(plan_dir, manifest, "003", ["c.out"])

        _, completed_manifest = planctl.load_plan(plan_dir)
        gen_before = completed_manifest["generation"]
        old_receipts = {
            tid: copy.deepcopy(planctl.find_task(completed_manifest, tid)["current_receipt"])
            for tid in ("001", "002", "003")
        }
        for tid in ("001", "002", "003"):
            t = planctl.find_task(completed_manifest, tid)
            res = planctl.validate_receipt(t["current_receipt"], t, manifest=completed_manifest)
            assert res["valid"] is True, res

        # Revise ONLY Task 001's contract (acceptance + scoped input hash)
        (repo / "src_a.txt").write_text("alpha-v2\n", encoding="utf-8")
        new_sha = hashlib.sha256((repo / "src_a.txt").read_bytes()).hexdigest()
        revised = copy.deepcopy(spec)
        revised["tasks"][0]["acceptance_criteria"] = ["a.out exists with component A v2 output."]
        revised["tasks"][0]["scoped_input_digests"] = {"src_a.txt": new_sha}

        rev_record = planctl.revise_plan(
            plan_dir,
            revised,
            amendment="Update component A acceptance and bound src_a.txt hash",
            expected_generation=gen_before,
        )
        assert rev_record["previous_generation"] == gen_before
        assert rev_record["generation"] == gen_before + 1
        assert rev_record["previous_spec_sha256"] != rev_record["new_spec_sha256"]
        assert set(rev_record["invalidated_tasks"]) == {"001", "002"}
        assert rev_record["preserved_completed_tasks"] == ["003"]

        _, after = planctl.load_plan(plan_dir)
        assert planctl.validate_plan(plan_dir, after) == []

        t1 = planctl.find_task(after, "001")
        t2 = planctl.find_task(after, "002")
        t3 = planctl.find_task(after, "003")

        # 001 and dependent 002 are reopened; old receipts preserved immutably in receipt_history
        assert t1["status"] == "pending" and t1["current_receipt"] is None
        assert t2["status"] == "pending" and t2["current_receipt"] is None
        assert len(t1["receipt_history"]) == 1
        assert len(t2["receipt_history"]) == 1
        assert t1["receipt_history"][0]["historical"] is True
        assert t1["receipt_history"][0]["contract_digest"] == old_receipts["001"]["contract_digest"]
        assert t1["receipt_history"][0]["superseded_by_generation"] == gen_before + 1
        assert t2["receipt_history"][0]["historical"] is True
        assert t2["receipt_history"][0]["contract_digest"] == old_receipts["002"]["contract_digest"]

        # Historical receipts are NOT valid as current receipts
        hist1 = planctl.validate_receipt(t1["receipt_history"][0], t1, manifest=after)
        assert hist1["valid"] is False
        assert "historical_receipt_not_current" in hist1["reasons"]
        assert "contract_digest_mismatch" in hist1["reasons"]

        # Unrelated completed task 003 stays completed and its receipt stays valid!
        assert t3["status"] == "completed"
        assert t3["contract_digest"] == old_receipts["003"]["contract_digest"]
        assert t3["receipt_history"] == []
        v3 = planctl.validate_receipt(t3["current_receipt"], t3, manifest=after)
        assert v3["valid"] is True, v3

        # Changing scoped input digest at check time invalidates receipt cleanly
        v3_drift = planctl.validate_receipt(
            t3["current_receipt"],
            t3,
            manifest=after,
            scoped_input_digests={"c_input.txt": "f" * 64},
        )
        assert v3_drift["valid"] is False
        assert "contract_digest_mismatch" in v3_drift["reasons"]

        # Extension hook for task 018 extends the single validate_receipt function cleanly
        def ext_validator(receipt: dict[str, Any], _task: dict[str, Any], _ctx: dict[str, Any]) -> list[str]:
            return [] if receipt.get("custom_token") == "ok" else ["missing_018_extension_token"]

        planctl.register_receipt_validator(ext_validator)
        try:
            v3_ext_fail = planctl.validate_receipt(t3["current_receipt"], t3, manifest=after)
            assert v3_ext_fail["valid"] is False
            assert "missing_018_extension_token" in v3_ext_fail["reasons"]
            with_token = {**t3["current_receipt"], "custom_token": "ok"}
            v3_ext_pass = planctl.validate_receipt(with_token, t3, manifest=after)
            assert v3_ext_pass["valid"] is True, v3_ext_pass
        finally:
            if ext_validator in planctl.RECEIPT_VALIDATOR_EXTENSIONS:
                planctl.RECEIPT_VALIDATOR_EXTENSIONS.remove(ext_validator)

        # CLI smoke check for validate-receipt and recover-projections via planctl_concise.py
        concise_cli = str(SCRIPTS_DIR / "planctl_concise.py")
        vr = subprocess.run(
            [sys.executable, concise_cli, "validate-receipt", "--plan", str(plan_dir), "--task", "003"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert vr.returncode == 0, vr.stderr
        assert json.loads(vr.stdout)["valid"] is True

        rp = subprocess.run(
            [sys.executable, concise_cli, "recover-projections", "--plan", str(plan_dir)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert rp.returncode == 0, rp.stderr
        assert json.loads(rp.stdout)["tasks_completed_changed"] is False


CONCISE_CLI = str(SCRIPTS_DIR / "planctl_concise.py")
VOLATILE_PLAN_FILES = {planctl.PROJECTION_STATE_FILE, planctl.WRITER_LOCK_FILE}


def run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, CONCISE_CLI, *args], capture_output=True, text=True, check=False)


def stable_snapshot(plan_dir: Path) -> dict[str, bytes]:
    return {
        rel: data
        for rel, data in snapshot_plan_files(plan_dir).items()
        if rel not in VOLATILE_PLAN_FILES and not rel.startswith(planctl.STAGING_DIRECTORY + "/")
    }


def run_python(code: str, *args: str, wait: bool = True):
    command = [sys.executable, "-c", code, str(SCRIPTS_DIR), *args]
    if wait:
        return subprocess.run(command, capture_output=True, text=True, check=False, timeout=120)
    return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def test_r01_review_task_completes_with_schema_valid_report() -> None:
    """F01: a requires_independent_review / review_of task completes through the runner path."""
    with tempfile.TemporaryDirectory() as temp:
        repo = make_repo(Path(temp), "r01")
        spec = three_task_spec(repo)
        spec["tasks"][2]["review_of"] = "001"
        spec["tasks"][2]["dependencies"] = [1]
        spec["tasks"][2]["requires_independent_review"] = True
        plan_dir = planctl.create_plan(repo, spec, ".ai-work", "r01-plan")
        _, manifest = planctl.load_plan(plan_dir)
        complete_one_task(plan_dir, manifest, "001", ["a.out"])
        # The report carries only completion-report.schema.json fields (no verdict field exists).
        complete_one_task(plan_dir, manifest, "003", ["review.json"])
        _, after = planctl.load_plan(plan_dir)
        review = planctl.find_task(after, "003")
        assert review["status"] == "completed"
        assert review["completion_summary"] == "Completed task 003 cleanly."
        receipt = review["current_receipt"]
        assert receipt["independent_review_gate"] == "declared_validation_commands"
        assert planctl.validate_receipt(receipt, review, manifest=after)["valid"] is True
        strict = planctl.validate_receipt(receipt, review, manifest=after, require_review_verdict=True)
        assert strict["valid"] is False and "independent_review_not_approved" in strict["reasons"]
        approved = planctl.validate_receipt({**receipt, "verdict": "approved"}, review, manifest=after,
                                            require_review_verdict=True)
        assert approved["valid"] is True, approved
        # An explicit non-approved verdict is never accepted, even without the strict flag.
        for bad in ({"verdict": "changes_requested"}, {"independent_review_status": "rejected"}):
            rejected = planctl.validate_receipt({**receipt, **bad}, review, manifest=after)
            assert rejected["valid"] is False and "independent_review_not_approved" in rejected["reasons"]
        cli = run_cli("validate-receipt", "--plan", str(plan_dir), "--task", "003", "--require-review-verdict")
        assert cli.returncode == 2 and "independent_review_not_approved" in cli.stdout, cli.stdout + cli.stderr
        assert run_cli("validate-receipt", "--plan", str(plan_dir), "--task", "003").returncode == 0


def test_r02_revise_requires_expected_generation() -> None:
    """F02: a revision without the generation it was written against is refused (API and CLI)."""
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        repo = make_repo(base, "r02")
        spec = three_task_spec(repo)
        plan_dir = planctl.create_plan(repo, spec, ".ai-work", "r02-plan")
        before = snapshot_plan_files(plan_dir)
        revised = copy.deepcopy(spec)
        revised["tasks"][2]["acceptance_criteria"] = ["c.out exists with component C v2 output."]
        expect_plan_error(
            lambda: planctl.revise_plan(plan_dir, revised, amendment="Revise C without a base generation"),
            "requires expected_generation",
        )
        spec_path = base / "revised.json"
        spec_path.write_text(json.dumps(revised), encoding="utf-8")
        cli = run_cli("revise", "--plan", str(plan_dir), "--spec", str(spec_path), "--amendment", "Revise C")
        assert cli.returncode == 2 and "--expected-generation" in cli.stderr, cli.stderr
        assert snapshot_plan_files(plan_dir) == before
        cli_ok = run_cli("revise", "--plan", str(plan_dir), "--spec", str(spec_path), "--amendment",
                         "Revise C acceptance", "--expected-generation", "1")
        assert cli_ok.returncode == 0, cli_ok.stderr
        assert json.loads(cli_ok.stdout)["generation"] == 2


def test_r03_pre_generation_manifest_upgrade() -> None:
    """F03: a schema-v4 manifest without a generation is upgraded explicitly, then guarded."""
    with tempfile.TemporaryDirectory() as temp:
        repo = make_repo(Path(temp), "r03")
        spec = three_task_spec(repo)
        for name in ("r03-recover", "r03-revise"):
            plan_dir = planctl.create_plan(repo, spec, ".ai-work", name)
            raw = planctl.read_json(plan_dir / planctl.MANIFEST)
            raw.pop("generation")
            planctl.atomic_write_json(plan_dir / planctl.MANIFEST, raw)
            (plan_dir / planctl.PROJECTION_STATE_FILE).unlink()
            expect_plan_error(
                lambda pd=plan_dir: planctl.revise_plan(pd, spec, amendment="Wrong base", expected_generation=1),
                "Stale plan writer",
            )
        recover_dir = repo / ".ai-work" / "r03-recover"
        rec = planctl.recover_projections(recover_dir)
        assert rec["generation_initialized"] is True and rec["projection_lag_detected"] is True
        assert rec["tasks_completed_changed"] is False
        _, upgraded = planctl.load_plan(recover_dir)
        assert upgraded["generation"] == 1
        assert any(e.get("type") == "generation_initialized" for e in upgraded["events"])
        assert planctl.validate_plan(recover_dir, upgraded) == []
        _, stale = planctl.load_plan(recover_dir)
        planctl.claim_task(recover_dir, upgraded, "001", None)
        expect_plan_error(lambda: planctl.save_manifest(recover_dir, stale), "Stale plan writer")
        assert planctl.recover_projections(recover_dir)["generation_initialized"] is False

        revise_dir = repo / ".ai-work" / "r03-revise"
        record = planctl.revise_plan(revise_dir, spec, amendment="Adopt generation counter", expected_generation=0)
        assert record["previous_generation"] == 0 and record["generation"] == 1
        assert record["invalidated_tasks"] == []


LOCK_WORKER = r"""
import sys, time
sys.path.insert(0, sys.argv[1])
import planctl
plan_dir, log_path, rounds = sys.argv[2], sys.argv[3], int(sys.argv[4])
from pathlib import Path
for _ in range(rounds):
    with planctl.plan_writer_lock(Path(plan_dir), timeout_seconds=60):
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(f"enter {planctl.os.getpid()}\n")
        time.sleep(0.02)
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(f"exit {planctl.os.getpid()}\n")
"""


def test_r04_writer_lock_contention_and_takeover() -> None:
    """F04: stale takeover is exclusive; live owners are not stolen by age; odd lock content is safe."""
    with tempfile.TemporaryDirectory() as temp:
        plan_dir = Path(temp) / "lock-plan"
        plan_dir.mkdir()
        lock_path = plan_dir / planctl.WRITER_LOCK_FILE
        host = planctl.socket.gethostname()
        old = planctl.time.time() - 3600

        def write_lock(payload: Any) -> None:
            lock_path.write_text(payload if isinstance(payload, str) else json.dumps(payload), encoding="utf-8")
            os.utime(lock_path, (old, old))

        sleeper = run_python("import time; time.sleep(60)", wait=False)
        try:
            token = planctl._process_start_token(sleeper.pid)
            write_lock({"pid": sleeper.pid, "hostname": host, "nonce": "live", "process_start": token})
            expect_plan_error(
                lambda: planctl.plan_writer_lock(plan_dir, timeout_seconds=0.3, stale_seconds=1).__enter__(),
                "held by another writer",
            )
            assert lock_path.is_file(), "A live same-host owner must not be stolen by age"
            if token is not None:
                write_lock({"pid": sleeper.pid, "hostname": host, "nonce": "reused", "process_start": token + "0"})
                with planctl.plan_writer_lock(plan_dir, timeout_seconds=2):
                    assert "reused" not in lock_path.read_text(encoding="utf-8")
                assert not lock_path.exists()
            write_lock({"pid": sleeper.pid, "hostname": host, "nonce": "legacy"})
            expect_plan_error(
                lambda: planctl.plan_writer_lock(plan_dir, timeout_seconds=0.3, stale_seconds=1).__enter__(),
                "held by another writer",
            )
        finally:
            sleeper.kill()
            sleeper.wait()
        with planctl.plan_writer_lock(plan_dir, timeout_seconds=2):
            assert "legacy" not in lock_path.read_text(encoding="utf-8")
        for odd in ("[1]", "not json", ""):
            write_lock(odd)
            with planctl.plan_writer_lock(plan_dir, timeout_seconds=2):
                pass
            assert not lock_path.exists()
        write_lock({"pid": os.getpid(), "hostname": host, "nonce": "own-leftover"})
        with planctl.plan_writer_lock(plan_dir, timeout_seconds=2):
            pass

        # A busy takeover guard makes waiters sleep and honour the timeout; a crashed
        # contender's guard is removed once it is old (N04).
        guard = lock_path.with_name(lock_path.name + ".takeover")
        write_lock({"pid": 99999999, "hostname": host, "nonce": "dead-guarded"})
        guard.write_text("busy-guard", encoding="utf-8")
        started = planctl.time.monotonic()
        expect_plan_error(
            lambda: planctl.plan_writer_lock(plan_dir, timeout_seconds=0.3).__enter__(),
            "could not be taken over",
        )
        assert planctl.time.monotonic() - started < 5
        os.utime(guard, (old, old))
        with planctl.plan_writer_lock(plan_dir, timeout_seconds=2):
            pass
        assert not guard.exists() and not list(plan_dir.glob("*.stale"))
        if os.name == "nt":
            # A stale lock that cannot be deleted (held open without delete sharing) must
            # not hang the writer past its timeout.
            write_lock({"pid": 99999999, "hostname": host, "nonce": "undeletable"})
            with open(lock_path, "rb"):
                expect_plan_error(
                    lambda: planctl.plan_writer_lock(plan_dir, timeout_seconds=0.3).__enter__(),
                    "could not be taken over",
                )
            with planctl.plan_writer_lock(plan_dir, timeout_seconds=2):
                pass

        # Several processes race to take over the same dead-owner lock and then contend.
        write_lock({"pid": 99999999, "hostname": host, "nonce": "dead"})
        log_path = Path(temp) / "lock.log"
        workers = [run_python(LOCK_WORKER, str(plan_dir), str(log_path), "6", wait=False) for _ in range(4)]
        for worker in workers:
            _out, err = worker.communicate(timeout=120)
            assert worker.returncode == 0, err
        events = log_path.read_text(encoding="utf-8").split()
        pairs = list(zip(events[0::2], events[1::2]))
        assert len(pairs) == 48, events
        for (enter, enter_pid), (exit_, exit_pid) in zip(pairs[0::2], pairs[1::2]):
            assert (enter, exit_) == ("enter", "exit") and enter_pid == exit_pid, events
        assert not lock_path.exists()
        assert not lock_path.with_name(lock_path.name + ".takeover").exists()


def test_r05_scoped_inputs_hashed_at_completion() -> None:
    """F05: completion and validate-receipt hash the declared scoped inputs on disk."""
    with tempfile.TemporaryDirectory() as temp:
        repo = make_repo(Path(temp), "r05")
        spec = three_task_spec(repo)
        plan_dir = planctl.create_plan(repo, spec, ".ai-work", "r05-plan")
        _, manifest = planctl.load_plan(plan_dir)
        source = repo / "src_a.txt"
        source.write_text("alpha-drifted\n", encoding="utf-8")
        expect_plan_error(lambda: complete_one_task(plan_dir, manifest, "001", ["a.out"]), "scoped_input_mismatch:src_a.txt")
        task = planctl.find_task(manifest, "001")
        assert task["status"] == "in_progress" and "completion_summary" not in task
        source.write_bytes(b"alpha-v1\r\n")  # CRLF checkout of the LF-pinned input still matches
        report = {"status": "completed", "summary": "Completed task 001 cleanly.", "changed_files": ["a.out"],
                  "validations": [], "risks": [], "follow_ups": [], "completed_subtask_ids": ["S001"],
                  "reusable_learnings": []}
        planctl.complete_task(plan_dir, manifest, "001", report, "results/001.json")
        _, after = planctl.load_plan(plan_dir)
        done = planctl.find_task(after, "001")
        assert done["current_receipt"]["scoped_input_digests"] == done["scoped_input_digests"]
        assert run_cli("validate-receipt", "--plan", str(plan_dir), "--task", "001").returncode == 0
        source.write_text("alpha-later-edit\n", encoding="utf-8")
        drift = run_cli("validate-receipt", "--plan", str(plan_dir), "--task", "001")
        assert drift.returncode == 2, drift.stdout
        reasons = json.loads(drift.stdout)["reasons"]
        assert "scoped_input_mismatch:src_a.txt" in reasons and "contract_digest_mismatch" in reasons
        source.unlink()
        assert "scoped_input_mismatch:src_a.txt" in run_cli("validate-receipt", "--plan", str(plan_dir),
                                                             "--task", "001").stdout


def test_r06_flag_digests_carried_forward() -> None:
    """F06: digests bound by --scoped-input-digests survive an unrelated later revision."""
    with tempfile.TemporaryDirectory() as temp:
        repo = make_repo(Path(temp), "r06")
        spec = three_task_spec(repo)
        c_input = repo / "c_input.txt"
        c_input.write_text("charlie\n", encoding="utf-8")
        c_sha = hashlib.sha256(c_input.read_bytes()).hexdigest()
        plan_dir = planctl.create_plan(repo, spec, ".ai-work", "r06-plan")
        _, manifest = planctl.load_plan(plan_dir)
        for tid, out in (("001", "a.out"), ("002", "b.out"), ("003", "c.out")):
            complete_one_task(plan_dir, manifest, tid, [out])
        gen = planctl.read_json(plan_dir / planctl.MANIFEST)["generation"]
        first = planctl.revise_plan(plan_dir, spec, amendment="Bind c_input.txt to task 003",
                                    expected_generation=gen, scoped_input_digests={"003": {"c_input.txt": c_sha}})
        assert first["invalidated_tasks"] == ["003"]
        _, manifest = planctl.load_plan(plan_dir)
        complete_one_task(plan_dir, manifest, "003", ["c.out"])
        revised = copy.deepcopy(spec)
        revised["tasks"][1]["acceptance_criteria"] = ["b.out reflects a.out with v2 formatting."]
        gen = planctl.read_json(plan_dir / planctl.MANIFEST)["generation"]
        second = planctl.revise_plan(plan_dir, revised, amendment="Change only B acceptance", expected_generation=gen)
        assert second["invalidated_tasks"] == ["002"], second
        assert sorted(second["preserved_completed_tasks"]) == ["001", "003"]
        assert second["carried_scoped_input_digests"] == ["003"]
        _, after = planctl.load_plan(plan_dir)
        t3 = planctl.find_task(after, "003")
        assert t3["status"] == "completed" and t3["scoped_input_digests"] == {"c_input.txt": c_sha}
        assert planctl.validate_receipt(t3["current_receipt"], t3, manifest=after)["valid"] is True

        # Spec-bound digests are owned by the spec: dropping the key unbinds them (N05).
        unbound = copy.deepcopy(revised)
        unbound["tasks"][0].pop("scoped_input_digests")
        third = planctl.revise_plan(plan_dir, unbound, amendment="Unbind src_a.txt from task 001",
                                    expected_generation=after["generation"])
        assert "001" in third["invalidated_tasks"] and third["carried_scoped_input_digests"] == ["003"]
        _, final = planctl.load_plan(plan_dir)
        assert "scoped_input_digests" not in planctl.find_task(final, "001")
        assert planctl.find_task(final, "003")["scoped_input_digests"] == {"c_input.txt": c_sha}


INTERRUPT_REVISION = r"""
import json, os, sys
sys.path.insert(0, sys.argv[1])
from artifact_contract import install_plan_contract
planctl = install_plan_contract()
spec = json.loads(open(sys.argv[3], encoding="utf-8").read())
planctl.revise_plan(sys.argv[2], spec, amendment="Interrupted before publication", expected_generation=1,
                    _before_authority_publish=lambda plan, staged: os._exit(17))
"""


def test_r07_staged_audit_rollback_and_interrupted_revision() -> None:
    """F07: the staged-audit rollback and a killed revision both leave the previous generation intact."""
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        repo = make_repo(base, "r07")
        spec = three_task_spec(repo)
        plan_dir = planctl.create_plan(repo, spec, ".ai-work", "r07-plan")
        before = snapshot_plan_files(plan_dir)
        revised = copy.deepcopy(spec)
        revised["tasks"][2]["acceptance_criteria"] = ["c.out exists with component C v2 output."]

        staged_seen: list[list[str]] = []
        original_validate = planctl.validate_plan

        def failing_staged_audit(pd: Any, manifest: dict[str, Any] | None = None) -> list[str]:
            if planctl.STAGING_DIRECTORY in Path(pd).parts:
                staged_seen.append(sorted(p.relative_to(pd).as_posix() for p in Path(pd).rglob("*") if p.is_file()))
                return ["injected staged audit failure"]
            return original_validate(pd, manifest)

        planctl.validate_plan = failing_staged_audit
        try:
            expect_plan_error(
                lambda: planctl.revise_plan(plan_dir, revised, amendment="Fail staged audit", expected_generation=1),
                "injected staged audit failure",
            )
        finally:
            planctl.validate_plan = original_validate
        assert staged_seen and {"manifest.json", "TODO.md", "PLAN.md"} <= set(staged_seen[0]), staged_seen
        assert any(name.startswith("tasks/") for name in staged_seen[0])
        assert snapshot_plan_files(plan_dir) == before
        assert not (plan_dir / planctl.STAGING_DIRECTORY).exists()

        spec_path = base / "revised.json"
        spec_path.write_text(json.dumps(revised), encoding="utf-8")
        killed = run_python(INTERRUPT_REVISION, str(plan_dir), str(spec_path))
        assert killed.returncode == 17, killed.stderr
        assert (plan_dir / planctl.STAGING_DIRECTORY).is_dir(), "A killed revision leaves its staging behind"
        assert (plan_dir / planctl.WRITER_LOCK_FILE).is_file(), "A killed revision leaves its lock behind"
        assert stable_snapshot(plan_dir) == stable_snapshot_from(before)
        rec = planctl.recover_projections(plan_dir)
        assert rec["removed_staging_dirs"] and rec["tasks_completed_changed"] is False
        assert rec["projection_lag_detected"] is False
        assert stable_snapshot(plan_dir) == stable_snapshot_from(before)
        assert not (plan_dir / planctl.STAGING_DIRECTORY).exists()
        assert planctl.read_json(plan_dir / planctl.MANIFEST)["generation"] == 1
        record = planctl.revise_plan(plan_dir, revised, amendment="Retry revision", expected_generation=1)
        assert record["generation"] == 2 and record["changed_tasks"] == ["003"]

        # Interrupted create_plan staging beside the plan directory is cleaned by recovery.
        leftover = plan_dir.parent / ".staging-r07-plan-0123abcd"
        leftover.mkdir()
        (leftover / "manifest.json").write_text("{}\n", encoding="utf-8")
        assert "../.staging-r07-plan-0123abcd" in planctl.recover_projections(plan_dir)["removed_staging_dirs"]
        assert not leftover.exists()


def test_r08_completion_binding_and_revision_carry_forward() -> None:
    """N01-N03: out-of-band contract edits, worker-reported failures and study_gate survival."""
    with tempfile.TemporaryDirectory() as temp:
        repo = make_repo(Path(temp), "r08")
        spec = three_task_spec(repo)
        plan_dir = planctl.create_plan(repo, spec, ".ai-work", "r08-plan")
        _, manifest = planctl.load_plan(plan_dir)
        complete_one_task(plan_dir, manifest, "001", ["a.out"])

        # N02: a contract edited outside `revise` binds the receipt to the executed contract.
        _, manifest = planctl.load_plan(plan_dir)
        stored = planctl.find_task(manifest, "003")["contract_digest"]
        planctl.find_task(manifest, "003")["acceptance_criteria"] = ["c.out exists with edited component C output."]
        planctl.save_manifest(plan_dir, manifest)
        _, manifest = planctl.load_plan(plan_dir)
        complete_one_task(plan_dir, manifest, "003", ["c.out"])
        _, after = planctl.load_plan(plan_dir)
        t3 = planctl.find_task(after, "003")
        assert t3["current_receipt"]["contract_digest"] == t3["contract_digest"] != stored
        assert planctl.validate_receipt(t3["current_receipt"], t3, manifest=after)["valid"] is True

        # N03: a non-gating failure the worker reports does not refuse runner-validated work.
        planctl.claim_task(plan_dir, after, "002", None)
        planctl.set_subtask_state(plan_dir, after, "002", "S001", "in_progress")
        planctl.set_subtask_state(plan_dir, after, "002", "S001", "completed")
        report = {
            "status": "completed", "summary": "Completed task 002 with one pre-existing failure noted.",
            "changed_files": ["b.out"],
            "validations": [{"command": "python unrelated_self_test.py", "passed": False, "details": "Pre-existing."}],
            "validation_results": [{"command": "python -c \"assert True\"", "passed": True, "exit_code": 0}],
            "risks": [], "follow_ups": [], "completed_subtask_ids": ["S001"], "reusable_learnings": [],
        }
        planctl.complete_task(plan_dir, after, "002", report, "results/002.json")
        _, done = planctl.load_plan(plan_dir)
        receipt = planctl.find_task(done, "002")["current_receipt"]
        assert receipt["worker_reported_failed_validations"] == ["python unrelated_self_test.py"]
        assert receipt["validations"] == [{"command": "python -c \"assert True\"", "passed": True, "exit_code": 0}]
        failed_runner = {**receipt, "validations": [{"command": "x", "passed": False}]}
        assert "failed_validation_in_receipt" in planctl.validate_receipt(
            failed_runner, planctl.find_task(done, "002"), manifest=done)["reasons"]

        # N01: manifest state the spec does not own (an attached study gate) survives revise.
        raw = planctl.read_json(plan_dir / planctl.MANIFEST)
        raw["study_gate"] = {"study_sha256": "a" * 64, "attached_at": planctl.now_utc()}
        planctl.atomic_write_json(plan_dir / planctl.MANIFEST, raw)
        revised = copy.deepcopy(spec)
        revised.pop("plan_mode")
        revised["tasks"][2]["acceptance_criteria"] = ["c.out exists with component C v3 output."]
        planctl.revise_plan(plan_dir, revised, amendment="Revise C and leave single mode",
                            expected_generation=raw["generation"])
        _, revised_manifest = planctl.load_plan(plan_dir)
        assert revised_manifest["study_gate"] == raw["study_gate"]
        assert "plan_mode" not in revised_manifest, "Spec-owned keys dropped from the spec are not carried"


def test_r09_rejected_completion_has_no_side_effects_and_edits_stay_visible() -> None:
    """Dispatch-3 F01-F03: no digest re-stamping of other tasks, no side effects, no generation drift."""
    with tempfile.TemporaryDirectory() as temp:
        repo = make_repo(Path(temp), "r09")
        spec = three_task_spec(repo)
        spec["tasks"][0]["learning_targets"] = [{
            "task_id": 2,
            "reason": "Task 002 consumes the a.out format that task 001 settles.",
            "topics": ["a.out format"],
        }]
        plan_dir = planctl.create_plan(repo, spec, ".ai-work", "r09-plan")
        _, manifest = planctl.load_plan(plan_dir)

        # F02: a receipt rejected for scoped-input drift publishes no learning and changes no subtask.
        (repo / "src_a.txt").write_text("alpha-drifted\n", encoding="utf-8")
        planctl.claim_task(plan_dir, manifest, "001", None)
        report = {
            "status": "completed", "summary": "Completed task 001 with one learning.", "changed_files": ["a.out"],
            "validations": [], "risks": [], "follow_ups": [], "completed_subtask_ids": ["S001"],
            "reusable_learnings": [{"kind": "decision", "guidance": "a.out stores exactly one key=value line per run.",
                                    "references": ["a.out"], "target_task_ids": ["002"]}],
        }
        expect_plan_error(lambda: planctl.complete_task(plan_dir, manifest, "001", report, None),
                          "scoped_input_mismatch:src_a.txt")
        task1 = planctl.find_task(manifest, "001")
        assert task1["subtasks"][0]["status"] == "pending"
        assert not manifest.get("learning_artifacts")
        assert not list((plan_dir / planctl.LEARNING_DIRECTORY).glob("*.md"))
        (repo / "src_a.txt").write_text("alpha-v1\n", encoding="utf-8")
        planctl.complete_task(plan_dir, manifest, "001", report, None)
        assert len(planctl.read_json(plan_dir / planctl.MANIFEST)["learning_artifacts"]) == 1

        # F01: an out-of-band edit of completed task 001 stays visible to revise after an
        # unrelated completion, so the stale receipt is reopened rather than re-bound.
        _, manifest = planctl.load_plan(plan_dir)
        stored_001 = planctl.find_task(manifest, "001")["contract_digest"]
        planctl.find_task(manifest, "001")["acceptance_criteria"] = ["a.out exists with hand-edited output."]
        planctl.save_manifest(plan_dir, manifest)
        _, manifest = planctl.load_plan(plan_dir)
        complete_one_task(plan_dir, manifest, "003", ["c.out"])
        assert planctl.find_task(planctl.read_json(plan_dir / planctl.MANIFEST), "001")["contract_digest"] == stored_001
        restated = copy.deepcopy(spec)
        restated["tasks"][0]["acceptance_criteria"] = ["a.out exists with hand-edited output."]
        gen = planctl.read_json(plan_dir / planctl.MANIFEST)["generation"]
        record = planctl.revise_plan(plan_dir, restated, amendment="Restate hand-edited A", expected_generation=gen)
        assert "001" in record["invalidated_tasks"] and "003" in record["preserved_completed_tasks"], record

        # F03: a failed manifest write leaves the caller's generation at the disk generation.
        _, manifest = planctl.load_plan(plan_dir)
        disk_gen = manifest["generation"]
        original_write = planctl.atomic_write_json

        def failing_write(path: Path, data: Any) -> None:
            if Path(path).name == planctl.MANIFEST:
                raise OSError("simulated sharing violation")
            original_write(path, data)

        planctl.atomic_write_json = failing_write
        try:
            try:
                planctl.save_manifest(plan_dir, manifest)
            except OSError:
                pass
            else:
                raise AssertionError("Expected the simulated manifest write failure")
        finally:
            planctl.atomic_write_json = original_write
        assert manifest["generation"] == disk_gen
        planctl.save_manifest(plan_dir, manifest)
        assert planctl.read_json(plan_dir / planctl.MANIFEST)["generation"] == disk_gen + 1


def stable_snapshot_from(snapshot: dict[str, bytes]) -> dict[str, bytes]:
    return {
        rel: data
        for rel, data in snapshot.items()
        if rel not in VOLATILE_PLAN_FILES and not rel.startswith(planctl.STAGING_DIRECTORY + "/")
    }


def main() -> int:
    test_ac01_failed_revision_preserves_previous_manifest_and_projections()
    test_ac02_coverage_strict_json_and_subtask_consistency()
    test_ac03_transformed_research_task_and_prepared_research_not_proof()
    test_ac04_legacy_schema_1_to_3_preserved_without_schema4_rewrite()
    test_ac05_no_second_plan_and_no_nonexistent_research_output()
    test_ac06_crash_before_and_after_authority_publication_and_recovery()
    test_ac07_stale_plan_writer_rejected_and_writer_lock()
    test_ac08_selective_invalidation_receipt_history_and_extension_hook()
    for test in (
        test_r01_review_task_completes_with_schema_valid_report,
        test_r02_revise_requires_expected_generation,
        test_r03_pre_generation_manifest_upgrade,
        test_r04_writer_lock_contention_and_takeover,
        test_r05_scoped_inputs_hashed_at_completion,
        test_r06_flag_digests_carried_forward,
        test_r07_staged_audit_rollback_and_interrupted_revision,
        test_r08_completion_binding_and_revision_carry_forward,
        test_r09_rejected_completion_has_no_side_effects_and_edits_stay_visible,
    ):
        print(f"PROGRESS {test.__name__}", flush=True)
        test()
    print("All plan-contract (012/013) self-tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
