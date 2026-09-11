#!/usr/bin/env python3
"""Deterministic tests for versioned shared patterns and signatory invalidation."""

from __future__ import annotations

import json
import subprocess
import tempfile
from argparse import Namespace
from pathlib import Path

import patternctl
import planctl
from self_test import sample_spec


def create_repo(base: Path) -> Path:
    repo = base / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    return repo


def mark_completed(plan_dir: Path, manifest: dict, task_id: str) -> None:
    task = next(item for item in manifest["tasks"] if item["id"] == task_id)
    task["status"] = "completed"
    task["started_at"] = planctl.now_utc()
    task["completed_at"] = planctl.now_utc()
    for subtask in task["subtasks"]:
        subtask["status"] = "completed"
        subtask["started_at"] = planctl.now_utc()
        subtask["completed_at"] = planctl.now_utc()
    planctl.save_manifest(plan_dir, manifest)


def test_pattern_assignment_adoption_and_revision_invalidation() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        repo = create_repo(root)
        plan_dir = planctl.create_plan(repo, sample_spec(), ".ai-work", "patterns")
        spec_path = root / "patterns.json"
        spec_path.write_text(
            json.dumps(
                {
                    "patterns": [
                        {
                            "id": "PAT001",
                            "title": "Shared marker format",
                            "contract": ["Both TODOs treat implemented.txt as one UTF-8 marker line."],
                            "source_refs": ["R001", "R002"],
                            "rationale": "Creation and verification must agree on one marker representation.",
                            "signatories": ["001", "002"],
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        patternctl.command_init(Namespace(plan=str(plan_dir), spec=str(spec_path)))
        registry = patternctl.load_registry(plan_dir)
        assert registry["patterns"][0]["revision"] == 1
        assert (plan_dir / "patterns" / "assignments" / "001.md").is_file()

        _, manifest = planctl.load_plan(plan_dir)
        mark_completed(plan_dir, manifest, "001")
        patternctl.command_adopt(Namespace(plan=str(plan_dir), task="001"))
        registry = patternctl.load_registry(plan_dir)
        signatory = registry["patterns"][0]["signatories"][0]
        assert signatory["adopted_revision"] == 1

        contract_path = root / "contract-v2.json"
        contract_path.write_text(
            json.dumps({"contract": ["Both TODOs treat implemented.txt as one UTF-8 marker line ending with a newline."]}),
            encoding="utf-8",
        )
        patternctl.command_update(
            Namespace(
                plan=str(plan_dir),
                pattern="PAT001",
                contract_file=str(contract_path),
                reason="Validation requires an explicit trailing newline.",
                changed_by_task=None,
            )
        )
        registry = patternctl.load_registry(plan_dir)
        assert registry["patterns"][0]["revision"] == 2
        assert registry["patterns"][0]["signatories"][0]["adopted_revision"] is None
        _, manifest = planctl.load_plan(plan_dir)
        task_1 = next(item for item in manifest["tasks"] if item["id"] == "001")
        assert task_1["status"] == "pending"
        assert not patternctl.validate_registry(plan_dir, registry, manifest)


def test_completed_stale_signatory_is_rejected() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        repo = create_repo(root)
        plan_dir = planctl.create_plan(repo, sample_spec(), ".ai-work", "stale-pattern")
        spec_path = root / "patterns.json"
        spec_path.write_text(
            json.dumps(
                {
                    "patterns": [
                        {
                            "id": "PAT001",
                            "title": "Shared marker format",
                            "contract": ["Both TODOs use the same marker representation."],
                            "source_refs": ["R001", "R002"],
                            "rationale": "Two TODOs consume the same marker contract.",
                            "signatories": ["001", "002"],
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        patternctl.command_init(Namespace(plan=str(plan_dir), spec=str(spec_path)))
        _, manifest = planctl.load_plan(plan_dir)
        mark_completed(plan_dir, manifest, "001")
        registry = patternctl.load_registry(plan_dir)
        errors = patternctl.validate_registry(plan_dir, registry, planctl.load_plan(plan_dir)[1])
        assert any("completed TODO 001 is stale" in error for error in errors), errors


def main() -> int:
    test_pattern_assignment_adoption_and_revision_invalidation()
    test_completed_stale_signatory_is_rejected()
    print("All shared-pattern self-tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
