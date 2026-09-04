#!/usr/bin/env python3
"""Self-tests for resumable lifecycle, leases, completion, and cancellation."""

from __future__ import annotations

import os
import signal
import socket
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import lifecyclectl  # noqa: E402
import planctl  # noqa: E402


def sample_spec(title: str = "Lifecycle sample") -> dict:
    return {
        "title": title,
        "summary": "Create and validate a resumable implementation marker.",
        "language": "English",
        "request_analysis": {
            "request_parts": [
                {"id": "P001", "text": "Create the implementation marker"},
                {"id": "P002", "text": "Validate its content"},
            ],
            "repository_findings": [
                "The temporary repository has no production files before the sample task."
            ],
            "research_decision": "External research is not needed for a local marker-file lifecycle test.",
            "research_findings": [],
            "assumptions": ["The test environment provides a POSIX-compatible shell."],
            "risks": ["Lifecycle cleanup must not delete implementation files."],
            "open_questions": [],
            "decomposition_strategy": "Use one bounded task so lifecycle state transitions remain explicit.",
        },
        "requirements": [
            {
                "id": "R001",
                "text": "Create implemented.txt with deterministic validation",
                "source": "user",
                "priority": "must",
                "request_part_ids": ["P001", "P002"],
            }
        ],
        "global_constraints": ["Preserve implementation files during lifecycle cleanup"],
        "execution_context": {
            "global": {
                "decision": "omit",
                "rationale": (
                    "The lifecycle fixture has one self-contained TODO, so a shared context file "
                    "would repeat information already present in that task definition."
                ),
                "items": [],
            },
            "scoped": [],
        },
        "plan_review": {
            "status": "approved",
            "reviewer": "fresh lifecycle test reviewer",
            "rounds": 1,
            "coverage_complete": True,
            "tasks_atomic": True,
            "dependencies_valid": True,
            "validations_sufficient": True,
            "contexts_minimal": True,
            "context_boundaries_sound": True,
            "unresolved_findings": [],
            "notes": ["The single task covers the complete sample requirement."],
        },
        "autostart": True,
        "cleanup_on_success": True,
        "tasks": [
            {
                "id": 1,
                "title": "Create implementation marker",
                "objective": "Create implemented.txt containing implemented.",
                "requirement_ids": ["R001"],
                "complexity": "low",
                "atomicity_rationale": "This task has one file outcome and one deterministic content check.",
                "context_boundary": {
                    "shared_context": [
                        "Creating the lifecycle marker and validating its contents share one file contract."
                    ],
                    "why_one_todo": (
                        "The fixture has one cohesive implementation outcome, so splitting creation from "
                        "its deterministic validation would add an artificial handoff without reducing context."
                    ),
                    "separate_from": [],
                },
                "scope": {
                    "in": ["Create implemented.txt"],
                    "out": ["No unrelated changes"],
                    "expected_files": ["implemented.txt"],
                },
                "dependencies": [],
                "implementation_guidance": [],
                "acceptance_criteria": ["implemented.txt contains implemented"],
                "validation_commands": ["grep -q implemented implemented.txt"],
                "subtasks": [
                    {
                        "id": "S001",
                        "title": "Create and validate the marker",
                        "objective": "implemented.txt contains implemented and the deterministic grep succeeds.",
                    }
                ],
                "provider": "auto",
                "model_tier": "economy",
                "reasoning_effort": "low",
            }
        ],
    }


def make_repo(base: Path, name: str = "repo") -> Path:
    repo = base / name
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    return repo


def create_plan(repo: Path, title: str = "Lifecycle sample") -> Path:
    return planctl.create_plan(repo, sample_spec(title), ".ai-work", None)


def complete_sample_plan(plan_dir: Path) -> None:
    _, manifest = planctl.load_plan(plan_dir)
    task = manifest["tasks"][0]
    route = {"provider": "claude", "model": "fake", "tier": "economy", "effort": "low"}
    planctl.claim_task(plan_dir, manifest, task["id"], route)
    planctl.complete_task(
        plan_dir,
        manifest,
        task["id"],
        {
            "changed_files": ["implemented.txt"],
            "validation_results": [],
            "completed_subtask_ids": ["S001"],
            "reusable_learnings": [],
        },
        None,
    )
    planctl.mark_summary(plan_dir, manifest, "FINAL_SUMMARY.md")


def test_idle_activate_and_pointer_repair() -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = make_repo(Path(temp))
        assert lifecyclectl.status_payload(repo)["status"] == "idle"
        plan_dir = create_plan(repo)
        lifecyclectl.activate_plan(plan_dir)
        status = lifecyclectl.status_payload(repo)
        assert status["active"] is True
        assert status["action"] == "resume"
        assert status["plan"] == str(plan_dir.resolve())

        pointer = repo / ".ai-work" / lifecyclectl.ACTIVE_FILE
        pointer.unlink()
        repaired = lifecyclectl.discover_active(repo)
        assert repaired is not None and repaired[0] == plan_dir.resolve()
        assert pointer.is_file(), "A unique unfinished plan should repair the active pointer"


def test_interrupted_task_recovery_does_not_count_failure() -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = make_repo(Path(temp))
        plan_dir = create_plan(repo)
        lifecyclectl.activate_plan(plan_dir)
        _, manifest = planctl.load_plan(plan_dir)
        route = {"provider": "codex", "model": "fake", "tier": "economy", "effort": "low"}
        planctl.claim_task(plan_dir, manifest, "001", route)
        task = planctl.find_task(manifest, "001")
        before_failures = task["functional_failures"]

        stale = {
            "schema_version": 1,
            "plan_id": manifest["plan_id"],
            "pid": 99999999,
            "hostname": socket.gethostname(),
            "nonce": "stale",
            "created_at": lifecyclectl.utc_now(),
        }
        planctl.atomic_write_json(plan_dir / lifecyclectl.LEASE_FILE, stale)
        recovered = lifecyclectl.recover_interrupted_tasks(plan_dir)
        assert recovered == 1
        _, current = planctl.load_plan(plan_dir)
        task = planctl.find_task(current, "001")
        assert task["status"] == "pending"
        assert task["functional_failures"] == before_failures
        assert task["attempts"] == 1
        assert any(item.get("event") == "recovered_after_interruption" for item in task["history"])


def test_atomic_lease_blocks_duplicate_runner_and_recovers_stale_lock() -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = make_repo(Path(temp))
        plan_dir = create_plan(repo)
        token = lifecyclectl.acquire_lease(plan_dir)
        try:
            try:
                lifecyclectl.acquire_lease(plan_dir)
            except lifecyclectl.LifecycleError as exc:
                assert "already running" in str(exc)
            else:
                raise AssertionError("A live lease must block a duplicate runner")
        finally:
            assert lifecyclectl.release_lease(plan_dir, token) is True

        stale = {
            "schema_version": 1,
            "plan_id": plan_dir.name,
            "pid": 99999999,
            "hostname": socket.gethostname(),
            "nonce": "dead-runner",
            "created_at": lifecyclectl.utc_now(),
        }
        planctl.atomic_write_json(plan_dir / lifecyclectl.LEASE_FILE, stale)
        replacement = lifecyclectl.acquire_lease(plan_dir)
        assert replacement["nonce"] != stale["nonce"]
        lifecyclectl.release_lease(plan_dir, replacement)


def test_completed_plan_does_not_block_new_request() -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = make_repo(Path(temp))
        plan_dir = create_plan(repo)
        lifecyclectl.activate_plan(plan_dir)
        (repo / "implemented.txt").write_text("implemented\n", encoding="utf-8")
        complete_sample_plan(plan_dir)
        status = lifecyclectl.status_payload(repo)
        assert status["status"] == "idle"
        assert status["action"] == "create_request"
        assert not (repo / ".ai-work" / lifecyclectl.ACTIVE_FILE).exists()
        assert plan_dir.exists(), "A retained completed plan is history, not active work"


def test_cancel_removes_plan_state_but_preserves_implementation() -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = make_repo(Path(temp))
        plan_dir = create_plan(repo)
        lifecyclectl.activate_plan(plan_dir)
        implementation = repo / "implemented.txt"
        implementation.write_text("partial implementation\n", encoding="utf-8")
        intake = repo / ".ai-work" / "intake"
        intake.mkdir(parents=True)
        (intake / "request.md").write_text("draft\n", encoding="utf-8")

        result = lifecyclectl.cancel_workspace(repo)
        assert result["implementation_changes_preserved"] is True
        assert not plan_dir.exists()
        assert implementation.read_text(encoding="utf-8") == "partial implementation\n"
        assert lifecyclectl.status_payload(repo)["status"] == "idle"
        assert not intake.exists()


def test_reset_removes_all_recognized_plans_only() -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = make_repo(Path(temp))
        first = create_plan(repo, "First lifecycle plan")
        second = planctl.create_plan(repo, sample_spec("Second lifecycle plan"), ".ai-work", "second-plan")
        unrelated = repo / ".ai-work" / "do-not-delete"
        unrelated.mkdir()
        (unrelated / "notes.txt").write_text("not a plan\n", encoding="utf-8")
        result = lifecyclectl.cancel_workspace(repo, all_plans=True)
        assert len(result["plans_removed"]) == 2
        assert not first.exists() and not second.exists()
        assert unrelated.is_dir(), "Reset must ignore directories without a valid plan sentinel"


def test_live_runner_is_stopped_by_cancel() -> None:
    if os.name == "nt":
        return
    with tempfile.TemporaryDirectory() as temp:
        repo = make_repo(Path(temp))
        plan_dir = create_plan(repo)
        lifecyclectl.activate_plan(plan_dir)
        runner_pid = 424242
        alive = {runner_pid: True}
        signals: list[int] = []
        original_kill = lifecyclectl.os.kill
        original_pid_is_alive = lifecyclectl.pid_is_alive

        def fake_kill(pid: int, signum: int) -> None:
            assert pid == runner_pid
            signals.append(signum)
            if signum != 0:
                alive[pid] = False

        def fake_pid_is_alive(pid: object) -> bool:
            return alive.get(int(pid), False)

        try:
            lease = {
                "schema_version": 1,
                "plan_id": plan_dir.name,
                "pid": runner_pid,
                "hostname": socket.gethostname(),
                "nonce": "cancel-test",
                "created_at": lifecyclectl.utc_now(),
            }
            planctl.atomic_write_json(plan_dir / lifecyclectl.LEASE_FILE, lease)
            lifecyclectl.os.kill = fake_kill
            lifecyclectl.pid_is_alive = fake_pid_is_alive
            result = lifecyclectl.cancel_workspace(repo)
            assert result["status"] == "cancelled"
            assert not plan_dir.exists()
            assert signal.SIGTERM in signals
        finally:
            lifecyclectl.os.kill = original_kill
            lifecyclectl.pid_is_alive = original_pid_is_alive


def main() -> int:
    test_idle_activate_and_pointer_repair()
    test_interrupted_task_recovery_does_not_count_failure()
    test_atomic_lease_blocks_duplicate_runner_and_recovers_stale_lock()
    test_completed_plan_does_not_block_new_request()
    test_cancel_removes_plan_state_but_preserves_implementation()
    test_reset_removes_all_recognized_plans_only()
    test_live_runner_is_stopped_by_cancel()
    print("All resumable lifecycle self-tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
