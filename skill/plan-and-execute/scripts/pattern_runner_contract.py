#!/usr/bin/env python3
"""Install shared-pattern assignment/adoption hooks into the concise runner."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import patternctl


def install_pattern_runner_contract(run_isolated: Any) -> Any:
    if getattr(run_isolated, "_pattern_runner_contract", False):
        return run_isolated

    planctl = run_isolated.planctl
    original_prompt = run_isolated.worker_prompt
    original_execute = run_isolated.execute_one_task
    original_summary_input = run_isolated.compose_summary_input
    original_generate_summary = run_isolated.generate_final_summary

    def has_patterns(plan_dir: Path) -> bool:
        return (plan_dir / patternctl.REGISTRY_FILE).is_file()

    def assigned_pattern_files(plan_dir: Path, task_id: str) -> list[str]:
        if not has_patterns(plan_dir):
            return []
        registry = patternctl.load_registry(plan_dir)
        return [
            patternctl.pattern_filename(pattern)
            for pattern in patternctl.patterns_for_task(registry, task_id)
        ]

    def worker_prompt(
        plan_dir: Path,
        manifest: dict[str, Any],
        task: dict[str, Any],
        route: dict[str, str],
    ) -> str:
        base = original_prompt(plan_dir, manifest, task, route).replace(
            "Do not read other plan files, task definitions, logs, results, or `.ai-work` artifacts.",
            "Do not read other plan files, task definitions, logs, results, or unassigned `.ai-work` artifacts.",
        )
        pattern_files = assigned_pattern_files(plan_dir, task["id"])
        if not pattern_files:
            return base + "\nShared patterns: none. Report `pattern_files_read: []`.\n"
        assignment = f"{patternctl.ASSIGNMENT_DIR}/{task['id']}.md"
        rendered = "\n".join(f"- `{item}`" for item in pattern_files)
        return base + f"""

Shared pattern rules:
- Read `{assignment}` and then exactly these assigned normative pattern files:
{rendered}
- Treat their current revisions as acceptance inputs. Do not read unassigned patterns or edit pattern files/registry.
- If implementation evidence shows a shared contract must change, stop safely and report the concrete conflict in risks/follow-ups; the orchestrator owns pattern revision.
- Report `pattern_files_read` as exactly this ordered list: {json.dumps(pattern_files)}.
"""

    def execute_one_task(*args: Any, **kwargs: Any) -> bool:
        plan_dir = Path(args[0]) if args else Path(kwargs["plan_dir"])
        manifest = args[1] if len(args) > 1 else kwargs["manifest"]
        task = args[3] if len(args) > 3 else kwargs["task"]
        expected = assigned_pattern_files(plan_dir, task["id"])
        if has_patterns(plan_dir):
            registry = patternctl.load_registry(plan_dir)
            errors = patternctl.validate_registry(plan_dir, registry, manifest)
            if errors:
                raise run_isolated.RunnerError(
                    "Shared-pattern registry invalid before dispatch: " + "; ".join(errors)
                )

        completed = original_execute(*args, **kwargs)
        if not completed or kwargs.get("dry_run", False):
            return completed
        if not has_patterns(plan_dir):
            return completed

        refreshed = planctl.load_plan(plan_dir)[1]
        finished = planctl.find_task(refreshed, task["id"])
        result_file = finished.get("result_file")
        report: dict[str, Any] = {}
        if result_file:
            raw = planctl.read_json(plan_dir / result_file)
            if isinstance(raw, dict):
                report = raw
        reported = report.get("pattern_files_read", [])
        if reported != expected:
            planctl.reset_task(plan_dir, refreshed, task["id"])
            raise run_isolated.RunnerError(
                f"Worker pattern report mismatch for TODO {task['id']}: "
                f"expected {expected!r}, received {reported!r}; task reset"
            )

        patternctl.command_adopt(
            type("Args", (), {"plan": str(plan_dir), "task": task["id"]})()
        )
        refreshed = planctl.load_plan(plan_dir)[1]
        registry = patternctl.load_registry(plan_dir)
        errors = patternctl.validate_registry(plan_dir, registry, refreshed)
        if errors:
            planctl.reset_task(plan_dir, refreshed, task["id"])
            raise run_isolated.RunnerError(
                "Shared-pattern adoption validation failed: " + "; ".join(errors)
            )
        return True

    def compose_summary_input(plan_dir: Path, manifest: dict[str, Any]) -> Path:
        path = original_summary_input(plan_dir, manifest)
        if not has_patterns(plan_dir):
            return path
        data = planctl.read_json(path)
        if not isinstance(data, dict):
            return path
        registry = patternctl.load_registry(plan_dir)
        data["shared_patterns"] = [
            {
                "id": pattern["id"],
                "title": pattern["title"],
                "revision": pattern["revision"],
                "digest": pattern["digest"],
            }
            for pattern in registry["patterns"]
        ]
        planctl.atomic_write_json(path, data)
        return path

    def generate_final_summary(*args: Any, **kwargs: Any):
        plan_dir = Path(args[0]) if args else Path(kwargs["plan_dir"])
        manifest = args[1] if len(args) > 1 else kwargs["manifest"]
        if has_patterns(plan_dir):
            registry = patternctl.load_registry(plan_dir)
            errors = patternctl.validate_registry(plan_dir, registry, manifest)
            if errors:
                raise run_isolated.RunnerError(
                    "Cannot finalize with stale shared patterns: " + "; ".join(errors)
                )
        return original_generate_summary(*args, **kwargs)

    original_design_prompt = getattr(run_isolated, "design_prompt", None)
    if original_design_prompt is not None:

        def design_prompt(
            plan_dir: Path,
            manifest: dict[str, Any],
            task: dict[str, Any],
            route: dict[str, str],
        ) -> str:
            base = original_design_prompt(plan_dir, manifest, task, route)
            pattern_files = assigned_pattern_files(plan_dir, task["id"])
            if not pattern_files:
                return base
            rendered = "\n".join(f"- `{item}`" for item in pattern_files)
            return base + f"""
Shared patterns (read-only design constraints at their current revisions):
{rendered}
"""

        run_isolated.design_prompt = design_prompt

    run_isolated.worker_prompt = worker_prompt
    run_isolated.execute_one_task = execute_one_task
    run_isolated.compose_summary_input = compose_summary_input
    run_isolated.generate_final_summary = generate_final_summary
    run_isolated._pattern_runner_contract = True
    return run_isolated
