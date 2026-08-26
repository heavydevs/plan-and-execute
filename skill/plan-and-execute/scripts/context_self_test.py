#!/usr/bin/env python3
"""Deterministic tests for minimal global and scoped execution context."""

from __future__ import annotations

import copy
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import planctl  # noqa: E402
from self_test import sample_spec  # noqa: E402


def context_spec() -> dict:
    spec = sample_spec()
    spec["title"] = "Execution context sample"
    spec["summary"] = "Exercise universal and scoped context assignment across three tasks."
    spec["request_analysis"]["request_parts"].append(
        {"id": "P003", "text": "Document the marker contract without changing behavior"}
    )
    spec["requirements"].append(
        {
            "id": "R003",
            "text": "Document the marker contract without changing marker behavior",
            "source": "user",
            "priority": "must",
            "request_part_ids": ["P003"],
        }
    )
    spec["tasks"].append(
        {
            "id": 3,
            "title": "Document marker contract",
            "objective": "Document how the marker is created and verified.",
            "requirement_ids": ["R003"],
            "complexity": "low",
            "atomicity_rationale": "This task has one documentation outcome and one direct content check.",
            "dependencies": [2],
            "scope": {
                "in": ["Add a concise marker contract note"],
                "out": ["Do not change marker behavior"],
                "expected_files": ["MARKER.md"],
            },
            "implementation_guidance": [],
            "acceptance_criteria": ["MARKER.md describes creation and verification"],
            "validation_commands": ["test -f MARKER.md"],
            "provider": "auto",
            "model_tier": "economy",
            "reasoning_effort": "low",
        }
    )
    spec["execution_context"]["scoped"] = [
        {
            "id": "marker-write-contract",
            "title": "Marker write contract",
            "rationale": (
                "Only the creation and verification TODOs manipulate implemented.txt, so they "
                "share a narrow write contract that the documentation TODO must not load."
            ),
            "task_ids": [1, 2],
            "items": [
                {
                    "id": "C001",
                    "kind": "interface",
                    "text": "implemented.txt stores exactly one UTF-8 line ending with a newline.",
                    "necessity": (
                        "Both writer and verifier must agree on the byte-level marker contract "
                        "to avoid inconsistent implementation and validation."
                    ),
                    "source_refs": ["request:P001", "requirement:R002"],
                }
            ],
        }
    ]
    spec["plan_review"]["notes"].append(
        "Confirmed that CONTEXT.md contains only the universal file boundary and that the marker write contract is restricted to TODOs 001 and 002."
    )
    return spec


def create_repo(base: Path) -> Path:
    repo = base / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    return repo


def assert_rejected(spec: dict, expected: str) -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = create_repo(Path(temp))
        try:
            planctl.create_plan(repo, spec, ".ai-work", "invalid-context")
        except planctl.PlanError as exc:
            assert expected.casefold() in str(exc).casefold(), str(exc)
        else:
            raise AssertionError(f"Expected context rejection containing {expected!r}")


def test_global_and_scoped_context_are_minimal_and_mapped() -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = create_repo(Path(temp))
        plan_dir = planctl.create_plan(repo, context_spec(), ".ai-work", "context-map")
        _, manifest = planctl.load_plan(plan_dir)
        assert manifest["schema_version"] == 3
        assert not planctl.validate_plan(plan_dir, manifest)

        global_file = plan_dir / planctl.GLOBAL_CONTEXT_FILE
        scoped_file = plan_dir / "contexts" / "marker-write-contract.md"
        assert global_file.is_file() and scoped_file.is_file()
        assert len(global_file.read_text(encoding="utf-8")) <= planctl.MAX_CONTEXT_FILE_CHARS
        assert len(scoped_file.read_text(encoding="utf-8")) <= planctl.MAX_CONTEXT_FILE_CHARS

        tasks = {task["id"]: task for task in manifest["tasks"]}
        assert tasks["001"]["context_files"] == [
            "CONTEXT.md",
            "contexts/marker-write-contract.md",
        ]
        assert tasks["002"]["context_files"] == [
            "CONTEXT.md",
            "contexts/marker-write-contract.md",
        ]
        assert tasks["003"]["context_files"] == ["CONTEXT.md"]

        task_1 = (plan_dir / tasks["001"]["file"]).read_text(encoding="utf-8")
        task_3 = (plan_dir / tasks["003"]["file"]).read_text(encoding="utf-8")
        scoped_reference = ".ai-work/context-map/contexts/marker-write-contract.md"
        assert scoped_reference in task_1
        assert scoped_reference not in task_3
        assert "necessity" not in global_file.read_text(encoding="utf-8").casefold()
        assert "necessity" not in scoped_file.read_text(encoding="utf-8").casefold()


def test_context_omission_creates_no_files() -> None:
    spec = context_spec()
    spec["execution_context"] = {
        "global": {
            "decision": "omit",
            "rationale": (
                "Every TODO is self-contained and already carries its only non-obvious constraint, "
                "so any shared context file would duplicate task definitions."
            ),
            "items": [],
        },
        "scoped": [],
    }
    with tempfile.TemporaryDirectory() as temp:
        repo = create_repo(Path(temp))
        plan_dir = planctl.create_plan(repo, spec, ".ai-work", "context-omitted")
        _, manifest = planctl.load_plan(plan_dir)
        assert not (plan_dir / "CONTEXT.md").exists()
        assert not (plan_dir / "contexts").exists()
        assert all(task["context_files"] == [] for task in manifest["tasks"])
        assert not planctl.validate_plan(plan_dir, manifest)


def test_invalid_context_shapes_are_rejected() -> None:
    spec = context_spec()
    spec["execution_context"]["global"]["decision"] = "omit"
    assert_rejected(spec, "must be empty")

    spec = context_spec()
    spec["execution_context"]["scoped"][0]["task_ids"] = [1]
    assert_rejected(spec, "at least two")

    spec = context_spec()
    spec["execution_context"]["scoped"][0]["task_ids"] = [1, 2, 3]
    assert_rejected(spec, "belongs in execution_context.global")

    spec = context_spec()
    del spec["execution_context"]["global"]["items"][0]["source_refs"]
    assert_rejected(spec, "source_refs")

    spec = context_spec()
    spec["execution_context"]["scoped"][0]["items"][0]["text"] = (
        spec["execution_context"]["global"]["items"][0]["text"]
    )
    assert_rejected(spec, "duplicated across files")

    spec = context_spec()
    spec["execution_context"]["global"]["items"][0]["text"] = "x" * 281
    assert_rejected(spec, "280-character")


def test_context_tampering_and_leakage_are_detected() -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = create_repo(Path(temp))
        plan_dir = planctl.create_plan(repo, context_spec(), ".ai-work", "context-tamper")
        _, manifest = planctl.load_plan(plan_dir)
        global_file = plan_dir / "CONTEXT.md"
        global_file.write_text(global_file.read_text(encoding="utf-8") + "extra\n", encoding="utf-8")
        errors = planctl.validate_plan(plan_dir, manifest)
        assert any("does not match manifest" in error for error in errors)

    with tempfile.TemporaryDirectory() as temp:
        repo = create_repo(Path(temp))
        plan_dir = planctl.create_plan(repo, context_spec(), ".ai-work", "context-leak")
        _, manifest = planctl.load_plan(plan_dir)
        task = next(item for item in manifest["tasks"] if item["id"] == "003")
        task_path = plan_dir / task["file"]
        task_path.write_text(
            task_path.read_text(encoding="utf-8")
            + "\n` .ai-work/context-leak/contexts/marker-write-contract.md `\n".replace("` ", "`").replace(" `", "`"),
            encoding="utf-8",
        )
        errors = planctl.validate_plan(plan_dir, manifest)
        assert any("unassigned context" in error for error in errors)


def main() -> int:
    test_global_and_scoped_context_are_minimal_and_mapped()
    test_context_omission_creates_no_files()
    test_invalid_context_shapes_are_rejected()
    test_context_tampering_and_leakage_are_detected()
    print("All progressive execution-context self-tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
