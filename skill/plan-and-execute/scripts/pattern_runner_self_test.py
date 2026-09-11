#!/usr/bin/env python3
"""Integration-style self-tests for automatic shared-pattern hooks in the concise runner."""

from __future__ import annotations

import json
import subprocess
import tempfile
from argparse import Namespace
from pathlib import Path
from types import SimpleNamespace

import patternctl
import planctl
from pattern_runner_contract import install_pattern_runner_contract
from self_test import sample_spec


class FakeRunnerError(RuntimeError):
    pass


def create_repo(base: Path) -> Path:
    repo = base / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    return repo


def mark_completed(plan_dir: Path, manifest: dict, task_id: str) -> dict:
    task = planctl.find_task(manifest, task_id)
    task["status"] = "completed"
    task["started_at"] = task.get("started_at") or planctl.now_utc()
    task["completed_at"] = planctl.now_utc()
    for subtask in task["subtasks"]:
        subtask["status"] = "completed"
        subtask["started_at"] = subtask.get("started_at") or planctl.now_utc()
        subtask["completed_at"] = planctl.now_utc()
    planctl.save_manifest(plan_dir, manifest)
    return task


def initialize_pattern(plan_dir: Path, root: Path) -> list[str]:
    spec = root / "patterns.json"
    spec.write_text(
        json.dumps(
            {
                "patterns": [
                    {
                        "id": "PAT001",
                        "title": "Shared marker format",
                        "contract": ["TODO 001 and TODO 002 use the same UTF-8 marker representation."],
                        "source_refs": ["R001", "R002"],
                        "rationale": "Both implementation leaves consume the same normative marker contract.",
                        "signatories": ["001", "002"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    patternctl.command_init(Namespace(plan=str(plan_dir), spec=str(spec)))
    registry = patternctl.load_registry(plan_dir)
    return [patternctl.pattern_filename(pattern) for pattern in patternctl.patterns_for_task(registry, "001")]


def fake_runner(expected_pattern_files: list[str]) -> SimpleNamespace:
    runner = SimpleNamespace()
    runner.planctl = planctl
    runner.RunnerError = FakeRunnerError

    def worker_prompt(plan_dir, manifest, task, route):
        del plan_dir, manifest, task, route
        return "BASE PROMPT\n"

    def execute_one_task(plan_dir, manifest, config, task, **kwargs):
        del config, kwargs
        completed = mark_completed(plan_dir, manifest, task["id"])
        result_path = plan_dir / "results" / f"{task['id']}-fake.json"
        result_path.parent.mkdir(parents=True, exist_ok=True)
        planctl.atomic_write_json(result_path, {"pattern_files_read": expected_pattern_files})
        completed["result_file"] = result_path.relative_to(plan_dir).as_posix()
        planctl.save_manifest(plan_dir, manifest)
        return True

    def compose_summary_input(plan_dir, manifest):
        del manifest
        path = plan_dir / "SUMMARY_INPUT.json"
        planctl.atomic_write_json(path, {"tasks": []})
        return path

    def generate_final_summary(*args, **kwargs):
        del args, kwargs
        return "ok", "FINAL_SUMMARY.md"

    runner.worker_prompt = worker_prompt
    runner.execute_one_task = execute_one_task
    runner.compose_summary_input = compose_summary_input
    runner.generate_final_summary = generate_final_summary
    return install_pattern_runner_contract(runner)


def test_runner_injects_patterns_and_adopts_after_validated_completion() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        repo = create_repo(root)
        plan_dir = planctl.create_plan(repo, sample_spec(), ".ai-work", "pattern-runner")
        expected = initialize_pattern(plan_dir, root)
        runner = fake_runner(expected)
        _, manifest = planctl.load_plan(plan_dir)
        task = planctl.find_task(manifest, "001")
        prompt = runner.worker_prompt(plan_dir, manifest, task, {"provider": "fake", "model": "fake", "effort": "low"})
        assert "Shared pattern rules" in prompt
        assert expected[0] in prompt
        assert "patterns/assignments/001.md" in prompt

        assert runner.execute_one_task(plan_dir, manifest, {}, task, dry_run=False, no_wait=True)
        registry = patternctl.load_registry(plan_dir)
        signatory = next(item for item in registry["patterns"][0]["signatories"] if item["task_id"] == "001")
        assert signatory["adopted_revision"] == 1
        assert signatory["adopted_digest"] == registry["patterns"][0]["digest"]


def test_runner_blocks_finalization_with_stale_completed_signatory() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        repo = create_repo(root)
        plan_dir = planctl.create_plan(repo, sample_spec(), ".ai-work", "pattern-finalize")
        expected = initialize_pattern(plan_dir, root)
        runner = fake_runner(expected)
        _, manifest = planctl.load_plan(plan_dir)
        mark_completed(plan_dir, manifest, "002")
        _, manifest = planctl.load_plan(plan_dir)
        try:
            runner.generate_final_summary(plan_dir, manifest, {}, no_wait=True)
        except FakeRunnerError as exc:
            assert "stale shared patterns" in str(exc)
        else:
            raise AssertionError("Finalization must reject a completed signatory with no current pattern adoption")


def main() -> int:
    test_runner_injects_patterns_and_adopts_after_validated_completion()
    test_runner_blocks_finalization_with_stale_completed_signatory()
    print("All shared-pattern runner integration self-tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
