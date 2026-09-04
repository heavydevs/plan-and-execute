#!/usr/bin/env python3
"""Regression tests for precise, concise derived planning artifacts."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from artifact_contract import install_plan_contract, install_study_contract  # noqa: E402

planctl = install_plan_contract()
import run_isolated  # noqa: E402
from runner_contract import install_runner_contract  # noqa: E402

install_runner_contract(run_isolated)


def sample_spec() -> dict:
    return {
        "title": "Create deterministic marker",
        "summary": "Create marker.txt with one validated content contract.",
        "language": "English",
        "request_analysis": {
            "request_parts": [
                {"id": "P001", "text": "Create marker.txt containing ready."},
                {"id": "P002", "text": "Validate the marker content."},
            ],
            "repository_findings": ["marker.txt does not exist in the fixture repository."],
            "research_decision": "External research is unnecessary for this local file contract.",
            "research_findings": [],
            "assumptions": ["The fixture provides a POSIX-compatible shell."],
            "risks": ["A broad cleanup command could delete the marker output."],
            "open_questions": [],
            "decomposition_strategy": "Use one TODO because file creation and its grep check share one file contract and failure boundary.",
        },
        "requirements": [
            {
                "id": "R001",
                "text": "marker.txt contains exactly the text ready followed by a newline.",
                "source": "user",
                "priority": "must",
                "request_part_ids": ["P001", "P002"],
            }
        ],
        "global_constraints": ["Do not modify repository files other than marker.txt."],
        "execution_context": {
            "global": {
                "decision": "omit",
                "rationale": "The single TODO owns every request-specific fact, so a shared context file would duplicate its task definition.",
                "items": [],
            },
            "scoped": [],
        },
        "plan_review": {
            "status": "approved",
            "reviewer": "fresh concise-plan reviewer",
            "rounds": 1,
            "coverage_complete": True,
            "tasks_atomic": True,
            "dependencies_valid": True,
            "validations_sufficient": True,
            "contexts_minimal": True,
            "context_boundaries_sound": True,
            "unresolved_findings": [],
            "notes": ["R001 maps to TODO 001 and the grep command proves its content contract."],
        },
        "autostart": True,
        "cleanup_on_success": True,
        "tasks": [
            {
                "id": 1,
                "title": "Create marker",
                "objective": "Create marker.txt containing ready and validate that exact content.",
                "requirement_ids": ["R001"],
                "complexity": "low",
                "atomicity_rationale": "One file write and one exact-content check share the same state and failure boundary.",
                "context_boundary": {
                    "shared_context": ["Creation and validation use the same marker.txt content contract."],
                    "why_one_todo": "One worker can create and validate the single file without a cross-task handoff.",
                    "separate_from": ["No unrelated repository behavior belongs in this TODO."],
                },
                "scope": {
                    "in": ["Create marker.txt with ready followed by a newline."],
                    "out": ["Do not edit other repository files."],
                    "expected_files": ["marker.txt"],
                },
                "dependencies": [],
                "implementation_guidance": ["Write the marker once; do not add a generator or dependency."],
                "acceptance_criteria": ["marker.txt contains ready followed by a newline."],
                "validation_commands": ["test \"$(cat marker.txt)\" = ready"],
                "subtasks": [
                    {
                        "id": "S001",
                        "title": "Write and check marker",
                        "objective": "marker.txt contains ready and the exact-content command exits zero.",
                    }
                ],
                "learning_targets": [],
                "provider": "auto",
                "model_tier": "economy",
                "reasoning_effort": "low",
            }
        ],
    }


def make_repo(base: Path, name: str) -> Path:
    repo = base / name
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
    (repo / ".gitignore").write_text("\n", encoding="utf-8")
    subprocess.run(["git", "add", ".gitignore"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=repo, check=True)
    return repo


def test_compact_projection_and_completion_memory() -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = make_repo(Path(temp), "repo")
        plan_dir = planctl.create_plan(repo, sample_spec(), ".ai-work", "concise")
        _plan_dir, manifest = planctl.load_plan(plan_dir)
        errors = planctl.validate_plan(plan_dir, manifest)
        assert not errors, errors

        task = manifest["tasks"][0]
        task_text = (plan_dir / task["file"]).read_text(encoding="utf-8")
        plan_text = (plan_dir / "PLAN.md").read_text(encoding="utf-8")
        assert len(task_text) < 2600, len(task_text)
        assert len(plan_text) < 2600, len(plan_text)
        for forbidden in (
            "## Complexity and atomicity",
            "## Isolation contract",
            "## Requirements covered",
            "## Completion report",
        ):
            assert forbidden not in task_text
        assert "## Requirements -> TODOs" in plan_text

        route = {"provider": "codex", "model": "test", "tier": "economy", "effort": "low"}
        prompt = run_isolated.worker_prompt(plan_dir, manifest, task, route)
        assert len(prompt) < 2600, len(prompt)
        assert "Compiled task packet:" in prompt
        assert "ANALYSIS.md" not in prompt
        assert "PLAN.md" not in prompt
        assert "TODO.md" not in prompt
        packets = list((plan_dir / "packets").glob(f"{task['id']}-r*.md"))
        assert len(packets) == 1
        packet_text = packets[0].read_text(encoding="utf-8")
        assert f"## Source: {task['file']}" in packet_text
        assert "SHA-256:" in packet_text
        assert task_text.rstrip() in packet_text

        marker = repo / "marker.txt"
        marker.write_text("ready\n", encoding="utf-8")
        planctl.claim_task(plan_dir, manifest, task["id"], route)
        planctl.set_subtask_state(plan_dir, manifest, task["id"], "S001", "in_progress")
        planctl.set_subtask_state(plan_dir, manifest, task["id"], "S001", "completed")
        report = {
            "status": "completed",
            "summary": "Created marker.txt with the exact requested content.",
            "changed_files": ["marker.txt"],
            "validations": [{"command": "test \"$(cat marker.txt)\" = ready", "passed": True, "details": "Exit 0."}],
            "validation_results": [
                {
                    "command": "test \"$(cat marker.txt)\" = ready",
                    "passed": True,
                    "exit_code": 0,
                    "output_tail": "SHOULD_NOT_REACH_SUMMARY" * 300,
                }
            ],
            "risks": [],
            "follow_ups": [],
            "context_files_read": [],
            "learning_files_read": [],
            "completed_subtask_ids": ["S001"],
            "reusable_learnings": [],
            "related_task_reads": [],
            "blocked_reason": None,
        }
        planctl.complete_task(plan_dir, manifest, task["id"], report, "results/001.json")
        assert task["completion_summary"] == report["summary"]

        summary_input = run_isolated.compose_summary_input(plan_dir, manifest)
        compact = summary_input.read_text(encoding="utf-8")
        assert "SHOULD_NOT_REACH_SUMMARY" not in compact
        assert len(compact) < 5000, len(compact)


def test_vague_and_oversized_derived_text_are_rejected() -> None:
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        vague = sample_spec()
        vague["requirements"][0]["text"] = "The marker shall be handled robustly as appropriate."
        try:
            planctl.create_plan(make_repo(base, "vague"), vague, ".ai-work", "vague")
        except planctl.PlanError as exc:
            assert "vague wording" in str(exc)
        else:
            raise AssertionError("Vague derived requirement must be rejected")

        oversized = sample_spec()
        oversized["tasks"][0]["objective"] = "x" * 321
        try:
            planctl.create_plan(make_repo(base, "long"), oversized, ".ai-work", "long")
        except planctl.PlanError as exc:
            assert "320-character" in str(exc)
        else:
            raise AssertionError("Oversized derived task objective must be rejected")


def test_study_example_meets_concise_contract() -> None:
    studyctl = install_study_contract()
    example = json.loads(
        (SCRIPT_DIR.parent / "references" / "study-spec.example.json").read_text(encoding="utf-8")
    )
    study = studyctl.normalize_study(example)
    rendered = studyctl.render_study(study)
    assert len(rendered) < 6500, len(rendered)
    assert "## Repository evidence" in rendered


def main() -> int:
    test_compact_projection_and_completion_memory()
    test_vague_and_oversized_derived_text_are_rejected()
    test_study_example_meets_concise_contract()
    print("All concise-artifact self-tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
