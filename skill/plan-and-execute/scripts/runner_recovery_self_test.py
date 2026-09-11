#!/usr/bin/env python3
"""Failure/retry regressions using real plan state and simulated provider exits."""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch

from artifact_concision_self_test import make_repo, planctl, run_isolated, sample_spec

ROUTE = {"provider": "codex", "model": "test", "tier": "economy", "effort": "low"}


def worker_checkpoint(plan_dir: Path) -> None:
    # A worker/controller has its own manifest, separate from the runner's copy.
    _, state = planctl.load_plan(plan_dir)
    task = state["tasks"][0]
    planctl.set_subtask_state(plan_dir, state, task["id"], "S001", "in_progress")
    planctl.set_subtask_state(plan_dir, state, task["id"], "S001", "completed")
    planctl.set_subtask_state(plan_dir, state, task["id"], "S002", "in_progress")


def test_worker_checkpoints_survive_failed_or_interrupted_dispatch() -> None:
    for mode in ("failed", "invalid_report", "quota", "interrupted"):
        with tempfile.TemporaryDirectory() as temp:
            repo = make_repo(Path(temp), mode)
            spec = sample_spec()
            spec["tasks"][0]["subtasks"].append(
                {"id": "S002", "title": "Verify marker", "objective": "Check marker content."}
            )
            plan_dir = planctl.create_plan(repo, spec, ".ai-work", mode)
            _, manifest = planctl.load_plan(plan_dir)
            task = manifest["tasks"][0]

            def worker(*args, **kwargs):
                worker_checkpoint(plan_dir)
                if mode == "interrupted":
                    raise KeyboardInterrupt
                if mode == "quota":
                    return 1, "", "HTTP 429"
                if mode == "invalid_report":
                    return 0, "no completion JSON", ""
                return 1, "", "provider execution failed"

            with patch.object(run_isolated, "choose_route", return_value=ROUTE), patch.object(
                run_isolated, "run_process", side_effect=worker
            ), patch.object(run_isolated, "parse_provider_report", wraps=run_isolated.parse_provider_report) as parse:
                try:
                    completed = run_isolated.execute_one_task(
                        plan_dir, manifest, planctl.default_config(), task,
                        provider_override=None, dry_run=False, no_wait=True,
                    )
                except KeyboardInterrupt:
                    assert mode == "interrupted"
                except run_isolated.RunnerError as exc:
                    assert mode == "quota" and "Rate/usage limit" in str(exc)
                else:
                    assert mode in ("failed", "invalid_report") and not completed
                assert parse.call_count == (1 if mode == "invalid_report" else 0)

            _, stored = planctl.load_plan(plan_dir)
            current = stored["tasks"][0]
            assert current["status"] == "pending"
            assert current["subtasks"][0]["status"] == "completed", mode
            assert current["subtasks"][0]["completed_at"]
            assert current["subtasks"][1]["status"] == "pending", mode
            assert any(item["event"] == "subtask_completed" for item in current["history"])
            assert current["functional_failures"] == (1 if mode in ("failed", "invalid_report") else 0)
            assert manifest == stored, "Caller must use the refreshed durable state too"


def test_changed_attempt_is_not_overwritten() -> None:
    for mode in ("reset", "reclaimed", "interrupted"):
        with tempfile.TemporaryDirectory() as temp:
            repo = make_repo(Path(temp), mode)
            plan_dir = planctl.create_plan(repo, sample_spec(), ".ai-work", mode)
            _, manifest = planctl.load_plan(plan_dir)
            task = manifest["tasks"][0]

            def worker(*args, **kwargs):
                _, state = planctl.load_plan(plan_dir)
                planctl.reset_task(plan_dir, state, task["id"])
                if mode != "reset":
                    planctl.claim_task(plan_dir, state, task["id"], ROUTE)
                if mode == "interrupted":
                    raise KeyboardInterrupt
                return 1, "", "late result from old attempt"

            with patch.object(run_isolated, "choose_route", return_value=ROUTE), patch.object(
                run_isolated, "run_process", side_effect=worker
            ):
                try:
                    run_isolated.execute_one_task(
                        plan_dir, manifest, planctl.default_config(), task,
                        provider_override=None, dry_run=False, no_wait=True,
                    )
                except KeyboardInterrupt:
                    assert mode == "interrupted"
                except run_isolated.RunnerError as exc:
                    assert mode != "interrupted" and "refusing to overwrite" in str(exc)
                else:
                    raise AssertionError("A changed attempt must stop the old runner")
            _, state = planctl.load_plan(plan_dir)
            current = state["tasks"][0]
            assert current["status"] == ("pending" if mode == "reset" else "in_progress")
            assert current["functional_failures"] == 0
            assert current["last_error"] is None


def test_timeout_preserves_partial_output_as_validation_failure() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        for index, output in enumerate((b"partial output\xff", "partial output", None)):
            log = root / f"timeout-{index}.log"
            with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("check", 1, output=output)):
                passed, results, reason = run_isolated.run_validation_commands(root, ["check"], log, 1)
            assert not passed
            assert results[0]["exit_code"] == 124
            assert "Timed out after 1 seconds" in reason
            text = log.read_text(encoding="utf-8")
            assert "[exit 124]" in text
            if output:
                assert "partial output" in text


def main() -> int:
    test_worker_checkpoints_survive_failed_or_interrupted_dispatch()
    test_changed_attempt_is_not_overwritten()
    test_timeout_preserves_partial_output_as_validation_failure()
    print("All runner recovery self-tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
