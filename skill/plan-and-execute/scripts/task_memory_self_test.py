#!/usr/bin/env python3
"""Focused self-tests for schema-v4 context boundaries, subtasks, and learnings."""

from __future__ import annotations

import copy
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import lifecyclectl  # noqa: E402
import planctl  # noqa: E402
from self_test import sample_spec  # noqa: E402


def make_repo(root: Path, name: str) -> Path:
    repo = root / name
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    return repo


def expect_plan_error(callback, fragment: str) -> None:
    try:
        callback()
    except planctl.PlanError as exc:
        assert fragment in str(exc), str(exc)
    else:
        raise AssertionError(f"Expected PlanError containing {fragment!r}")


def test_context_boundary_and_task_projection() -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = make_repo(Path(temp), "boundary")
        spec = sample_spec()
        plan_dir = planctl.create_plan(repo, spec, ".ai-work", "boundary")
        _, manifest = planctl.load_plan(plan_dir)
        assert manifest["schema_version"] == 4
        task_text = (plan_dir / manifest["tasks"][0]["file"]).read_text(encoding="utf-8")
        assert "## Context-isolation boundary" in task_text
        assert "## Resumable subtask checklist" in task_text
        assert "**S001**" in task_text
        assert "learning_files: \"none\"" in task_text

        invalid = sample_spec()
        invalid["tasks"][0].pop("context_boundary")
        expect_plan_error(
            lambda: planctl.create_plan(repo, invalid, ".ai-work", "missing-boundary"),
            "context_boundary",
        )


def test_subtask_recovery_preserves_completed_checkpoints() -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = make_repo(Path(temp), "subtasks")
        spec = sample_spec()
        spec["tasks"][0]["subtasks"] = [
            {"id": "S001", "title": "Create marker"},
            {"id": "S002", "title": "Validate marker"},
        ]
        plan_dir = planctl.create_plan(repo, spec, ".ai-work", "subtask-recovery")
        _, manifest = planctl.load_plan(plan_dir)
        planctl.claim_task(plan_dir, manifest, "001", None)
        planctl.set_subtask_state(plan_dir, manifest, "001", "S001", "in_progress")
        planctl.set_subtask_state(plan_dir, manifest, "001", "S001", "completed")
        planctl.set_subtask_state(plan_dir, manifest, "001", "S002", "in_progress")

        assert lifecyclectl.recover_interrupted_tasks(plan_dir) == 1
        _, current = planctl.load_plan(plan_dir)
        task = planctl.find_task(current, "001")
        assert task["status"] == "pending"
        states = {item["id"]: item["status"] for item in task["subtasks"]}
        assert states == {"S001": "completed", "S002": "pending"}
        definition = (plan_dir / task["file"]).read_text(encoding="utf-8")
        assert "- [x] **S001**" in definition
        assert "- [ ] **S002**" in definition


def test_parent_completion_requires_every_required_subtask() -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = make_repo(Path(temp), "gate")
        spec = sample_spec()
        spec["tasks"][0]["subtasks"] = [
            {"id": "S001", "title": "Create marker"},
            {"id": "S002", "title": "Validate marker"},
        ]
        plan_dir = planctl.create_plan(repo, spec, ".ai-work", "completion-gate")
        _, manifest = planctl.load_plan(plan_dir)
        planctl.claim_task(plan_dir, manifest, "001", None)
        expect_plan_error(
            lambda: planctl.complete_task(
                plan_dir,
                manifest,
                "001",
                {
                    "changed_files": [],
                    "validation_results": [],
                    "completed_subtask_ids": ["S001"],
                    "reusable_learnings": [],
                },
                None,
            ),
            "required subtasks remain",
        )


def test_selective_learning_artifact_and_tamper_detection() -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = make_repo(Path(temp), "learning")
        spec = sample_spec()
        spec["tasks"][0]["learning_targets"] = [
            {
                "task_id": "002",
                "reason": (
                    "Both TODOs use the same marker-file convention, but the target needs only "
                    "the validated procedure rather than the source worker history."
                ),
                "topics": ["marker validation order", "missing-file diagnosis"],
            }
        ]
        plan_dir = planctl.create_plan(repo, spec, ".ai-work", "learning")
        _, manifest = planctl.load_plan(plan_dir)
        planctl.claim_task(plan_dir, manifest, "001", None)
        planctl.complete_task(
            plan_dir,
            manifest,
            "001",
            {
                "changed_files": ["implemented.txt"],
                "validation_results": [],
                "completed_subtask_ids": ["S001"],
                "reusable_learnings": [
                    {
                        "kind": "procedure",
                        "guidance": (
                            "Create the marker before checking its exact contents so a later TODO "
                            "can distinguish a missing-file failure from an incorrect-content failure."
                        ),
                        "references": ["implemented.txt", "test -f implemented.txt"],
                        "target_task_ids": ["002"],
                    }
                ],
            },
            None,
        )
        assert planctl.validate_plan(plan_dir, manifest) == []
        target = planctl.find_task(manifest, "002")
        assert target["learning_files"] == ["learnings/001-to-002.md"]
        learning_path = plan_dir / target["learning_files"][0]
        learning_text = learning_path.read_text(encoding="utf-8")
        assert "worker transcript" in learning_text
        assert "implemented.txt" in learning_text
        assert "PLAN.md" not in learning_text
        task_text = (plan_dir / target["file"]).read_text(encoding="utf-8")
        assert "learnings/001-to-002.md" in task_text

        learning_path.write_text(learning_text + "tampered\n", encoding="utf-8")
        errors = planctl.validate_plan(plan_dir, manifest)
        assert any("hash mismatch" in error for error in errors)


def test_learning_artifact_is_canonical_even_when_hash_is_rewritten() -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = make_repo(Path(temp), "canonical-learning")
        spec = sample_spec()
        spec["tasks"][0]["learning_targets"] = [
            {
                "task_id": "002",
                "reason": (
                    "The target reuses one validated marker procedure, but it must not inherit "
                    "the source worker's transcript or mutable execution state."
                ),
                "topics": ["marker creation order"],
            }
        ]
        plan_dir = planctl.create_plan(repo, spec, ".ai-work", "canonical-learning")
        _, manifest = planctl.load_plan(plan_dir)
        planctl.claim_task(plan_dir, manifest, "001", None)
        planctl.complete_task(
            plan_dir,
            manifest,
            "001",
            {
                "changed_files": ["implemented.txt"],
                "validation_results": [],
                "completed_subtask_ids": ["S001"],
                "reusable_learnings": [
                    {
                        "kind": "procedure",
                        "guidance": (
                            "Create implemented.txt before validating its contents so missing-file "
                            "and wrong-content failures remain distinguishable."
                        ),
                        "references": ["implemented.txt", "test -f implemented.txt"],
                        "target_task_ids": ["002"],
                    }
                ],
            },
            None,
        )
        artifact = manifest["learning_artifacts"][0]
        learning_path = plan_dir / artifact["file"]
        learning_path.write_text(
            learning_path.read_text(encoding="utf-8").replace(
                "Create implemented.txt before validating its contents",
                "Trust a previous chat transcript before validating contents",
            ),
            encoding="utf-8",
        )
        artifact["sha256"] = hashlib.sha256(learning_path.read_bytes()).hexdigest()
        errors = planctl.validate_plan(plan_dir, manifest)
        assert any("authoritative manifest state" in error for error in errors)


def test_source_reset_removes_unconsumed_learning_artifacts() -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = make_repo(Path(temp), "learning-reset")
        spec = sample_spec()
        spec["tasks"][0]["learning_targets"] = [
            {
                "task_id": "002",
                "reason": (
                    "The target needs the validated marker ordering only while the source result "
                    "remains authoritative and before target execution starts."
                ),
                "topics": ["marker ordering"],
            }
        ]
        plan_dir = planctl.create_plan(repo, spec, ".ai-work", "learning-reset")
        _, manifest = planctl.load_plan(plan_dir)
        planctl.claim_task(plan_dir, manifest, "001", None)
        planctl.complete_task(
            plan_dir,
            manifest,
            "001",
            {
                "changed_files": ["implemented.txt"],
                "validation_results": [],
                "completed_subtask_ids": ["S001"],
                "reusable_learnings": [
                    {
                        "kind": "procedure",
                        "guidance": (
                            "Create the marker before validating its contents and preserve the "
                            "exact failing command as evidence for the target TODO."
                        ),
                        "references": ["implemented.txt", "test -f implemented.txt"],
                        "target_task_ids": ["002"],
                    }
                ],
            },
            None,
        )
        learning_file = plan_dir / "learnings/001-to-002.md"
        assert learning_file.is_file()

        planctl.reset_task(plan_dir, manifest, "001")
        assert not learning_file.exists()
        assert manifest["learning_artifacts"] == []
        assert planctl.find_task(manifest, "001")["published_learning_files"] == []
        assert planctl.find_task(manifest, "002")["learning_files"] == []
        assert planctl.validate_plan(plan_dir, manifest) == []


def test_learning_source_is_a_context_prerequisite() -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = make_repo(Path(temp), "late-learning")
        spec = sample_spec()
        spec["tasks"][1]["dependencies"] = []
        spec["tasks"][0]["learning_targets"] = [
            {
                "task_id": "002",
                "reason": (
                    "The target may reuse the validated marker diagnosis only when that knowledge "
                    "was assigned before its first isolated execution attempt."
                ),
                "topics": ["marker diagnosis"],
            }
        ]
        plan_dir = planctl.create_plan(repo, spec, ".ai-work", "late-learning")
        _, manifest = planctl.load_plan(plan_dir)
        assert planctl.next_runnable_task(manifest)["id"] == "001"
        expect_plan_error(
            lambda: planctl.claim_task(plan_dir, manifest, "002", None),
            "waiting for declared learning source",
        )

        # Keep the materialization guard as defense in depth against externally
        # corrupted or hand-edited state that bypassed the scheduler.
        target = planctl.find_task(manifest, "002")
        target["attempts"] = 1
        target["started_at"] = planctl.now_utc()
        planctl.claim_task(plan_dir, manifest, "001", None)
        expect_plan_error(
            lambda: planctl.complete_task(
                plan_dir,
                manifest,
                "001",
                {
                    "changed_files": ["implemented.txt"],
                    "validation_results": [],
                    "completed_subtask_ids": ["S001"],
                    "reusable_learnings": [
                        {
                            "kind": "pitfall",
                            "guidance": (
                                "Distinguish missing marker files from incorrect content before "
                                "changing the implementation or rerunning downstream validation."
                            ),
                            "references": ["implemented.txt", "grep -q implemented implemented.txt"],
                            "target_task_ids": ["002"],
                        }
                    ],
                },
                None,
            ),
            "target has already started",
        )
        assert not (plan_dir / "learnings/001-to-002.md").exists()


def test_learning_must_target_a_predeclared_later_todo() -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = make_repo(Path(temp), "undeclared")
        spec = sample_spec()
        invalid_order = copy.deepcopy(spec)
        invalid_order["tasks"][1]["learning_targets"] = [
            {
                "task_id": "001",
                "reason": "This deliberately invalid edge points backward and would reintroduce history.",
                "topics": ["invalid backward edge"],
            }
        ]
        expect_plan_error(
            lambda: planctl.create_plan(repo, invalid_order, ".ai-work", "backward"),
            "must be a later TODO",
        )

        plan_dir = planctl.create_plan(repo, spec, ".ai-work", "undeclared")
        _, manifest = planctl.load_plan(plan_dir)
        planctl.claim_task(plan_dir, manifest, "001", None)
        expect_plan_error(
            lambda: planctl.complete_task(
                plan_dir,
                manifest,
                "001",
                {
                    "changed_files": [],
                    "validation_results": [],
                    "completed_subtask_ids": ["S001"],
                    "reusable_learnings": [
                        {
                            "kind": "pitfall",
                            "guidance": (
                                "This guidance is long enough to be structurally valid but its "
                                "target was not approved during planning."
                            ),
                            "references": ["implemented.txt"],
                            "target_task_ids": ["002"],
                        }
                    ],
                },
                None,
            ),
            "undeclared target",
        )



def test_legacy_task_definitions_remain_immutable_during_state_changes() -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = make_repo(Path(temp), "legacy-projection")
        plan_dir = planctl.create_plan(
            repo, sample_spec(), ".ai-work", "legacy-projection"
        )
        _, manifest = planctl.load_plan(plan_dir)
        task = planctl.find_task(manifest, "001")
        task_path = plan_dir / task["file"]
        original = task_path.read_text(encoding="utf-8")

        # Simulate a retained schema-v3 workspace. Older plans treated task
        # definitions as immutable artifacts while TODO.md and manifest.json
        # carried runtime state. Schema-v4 live projections must not alter that
        # compatibility contract.
        manifest["schema_version"] = 3
        planctl.save_manifest(plan_dir, manifest)
        planctl.claim_task(plan_dir, manifest, "001", None)
        planctl.fail_task(plan_dir, manifest, "001", "simulated legacy retry")

        assert task_path.read_text(encoding="utf-8") == original


def main() -> int:
    test_context_boundary_and_task_projection()
    test_subtask_recovery_preserves_completed_checkpoints()
    test_parent_completion_requires_every_required_subtask()
    test_selective_learning_artifact_and_tamper_detection()
    test_learning_artifact_is_canonical_even_when_hash_is_rewritten()
    test_source_reset_removes_unconsumed_learning_artifacts()
    test_learning_source_is_a_context_prerequisite()
    test_learning_must_target_a_predeclared_later_todo()
    test_legacy_task_definitions_remain_immutable_during_state_changes()
    print("All task-memory and context-boundary self-tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
