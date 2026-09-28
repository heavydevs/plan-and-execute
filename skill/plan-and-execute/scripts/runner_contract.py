#!/usr/bin/env python3
"""Token-bounded prompts and handoffs for the strict isolated runner."""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


def _git_change_summary(repo_root: Path, limit: int = 4000) -> str:
    commands = (
        ["git", "status", "--short"],
        ["git", "diff", "HEAD", "--stat"],
    )
    parts: list[str] = []
    for command in commands:
        try:
            result = subprocess.run(
                command,
                cwd=repo_root,
                text=True,
                encoding="utf-8",
                errors="replace",
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                timeout=30,
            )
        except (OSError, subprocess.TimeoutExpired):
            continue
        if result.returncode == 0 and result.stdout.strip():
            parts.append(result.stdout.strip())
    text = "\n\n".join(parts)
    return text[:limit]


def install_runner_contract(run_isolated: Any) -> Any:
    if getattr(run_isolated, "_concise_runner_contract", False):
        return run_isolated

    planctl = run_isolated.planctl
    script_dir = Path(run_isolated.__file__).resolve().parent
    controller = script_dir / "planctl_concise.py"

    def worker_prompt(
        plan_dir: Path,
        manifest: dict[str, Any],
        task: dict[str, Any],
        route: dict[str, str],
    ) -> str:
        task_path = (plan_dir / task["file"]).resolve()
        schema_path = run_isolated.completion_schema_path().resolve()
        # Byte-stable rules first (shared prompt-cache prefix across TODOs and
        # sibling workers), stable paths next, per-task values last.
        return f"""Implement one isolated TODO. Keep context narrow and return only the required JSON report.

Rules:
1. Read the task first, then only its assigned context/learnings. Other task definitions require explicit allowlisting and a reported reason. Do not read other plan files, historical logs/results or unassigned `.ai-work` artifacts. Only the immediately preceding validation log may expand an insufficient latest-failure capsule. Read shared-pattern files only if appended by the runner.
2. Read/edit only source, tests, build files and runtime output needed for this TODO; preserve unrelated changes and stay within scope/acceptance. Do not edit plan/context/learning/pattern artifacts.
3. For `resource_watch.py` validation, consult only that command's `--map` service map. If this TODO changes test/build/CI/container/service discovery inputs, reconcile its resources/checks, preserve validation IDs and use the helper below with `stamp --confirm-reconciled`. Never hand-edit the hash index. New out-of-scope validation requires `plan_defect`.
4. Checkpoint this task's subtasks only with the controller below: `subtask-start`, `subtask-complete`, `subtask-reset`.
5. Run task validation before completion, including at low effort. Report exact context/learning files read and completed subtask IDs.
6. Publish learning only to predeclared future targets/topics with concrete evidence; omit generic advice.
7. Return one JSON object matching the schema below; bound summary, validation details, risks and follow-ups.
8. When blocked, report `failure_class`: `mechanical` (detail/tool slip), `semantic` (wrong approach), `environmental` (external toolchain/repository), `budget` (turn/token limit), or `plan_defect` (wrong requirement/boundary/dependency). The orchestrator owns the next route.

Subtask controller: `{controller}`
Report schema: `{schema_path}`
Repository: `{manifest['repo_root']}`
Task definition: `{task_path}`
Task: `{task['id']}`
Route: {route['provider']} / {route['model']} / {route['effort']}
Service map helper: {script_dir / 'service_map.py'}
""" + run_isolated.failure_context(task)

    original_validation = run_isolated.run_validation_commands

    def run_validation_commands(*args: Any, **kwargs: Any):
        passed, results, reason = original_validation(*args, **kwargs)
        for item in results:
            if isinstance(item, dict) and isinstance(item.get("output_tail"), str):
                tail = item["output_tail"]
                item["output_tail"] = tail[-800:] if len(tail) > 800 else tail
        if reason and len(reason) > 1500:
            reason = planctl.bounded_failure_reason(reason, 1500)
        return passed, results, reason

    def compose_summary_input(plan_dir: Path, manifest: dict[str, Any]) -> Path:
        tasks: list[dict[str, Any]] = []
        for task in manifest["tasks"]:
            validation = []
            for item in task.get("validation_results", []):
                if not isinstance(item, dict):
                    continue
                validation.append(
                    {
                        "command": item.get("command"),
                        "passed": item.get("passed"),
                        "exit_code": item.get("exit_code"),
                    }
                )
            tasks.append(
                {
                    "id": task.get("id"),
                    "title": task.get("title"),
                    "summary": task.get("completion_summary", ""),
                    "changed_files": task.get("changed_files", []),
                    "validation": validation,
                    "risks": task.get("completion_risks", []),
                    "follow_ups": task.get("completion_follow_ups", []),
                }
            )
        bundle = {
            "title": manifest["title"],
            "goal": manifest["summary"],
            "tasks": tasks,
            "repository_changes": _git_change_summary(Path(manifest["repo_root"])),
        }
        path = plan_dir / "SUMMARY_INPUT.json"
        planctl.atomic_write_json(path, bundle)
        return path

    def summary_prompt(
        plan_dir: Path,
        manifest: dict[str, Any],
        input_path: Path,
    ) -> str:
        del plan_dir, manifest
        return f"""Write a concise Markdown implementation handoff using only `{input_path}`.
Include: outcome, changed areas, deterministic validation, and only recorded remaining risks/follow-ups. Do not restate planning history, invent work, or quote raw logs. Return only the handoff Markdown."""

    run_isolated.worker_prompt = worker_prompt
    run_isolated.run_validation_commands = run_validation_commands
    run_isolated.compose_summary_input = compose_summary_input
    run_isolated.summary_prompt = summary_prompt
    run_isolated._concise_runner_contract = True
    return run_isolated
