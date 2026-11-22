#!/usr/bin/env python3
"""Token-bounded prompts and handoffs for the strict isolated runner."""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from typing import Any

MAX_TASK_FAILURE_SUFFIX_CHARS = 1400
PREFIX_BOUNDARY_MARKER = "Subtask controller:"


def prompt_cache_structure(prompt: str) -> dict[str, Any]:
    """Inspect structural prompt prefix vs task-specific suffix without claiming observed cache hits."""
    if PREFIX_BOUNDARY_MARKER in prompt:
        prefix, tail = prompt.split(PREFIX_BOUNDARY_MARKER, 1)
        suffix = PREFIX_BOUNDARY_MARKER + tail
    else:
        prefix, suffix = prompt, ""
    prefix_bytes = prefix.encode("utf-8")
    suffix_bytes = suffix.encode("utf-8")
    return {
        "static_prefix_bytes": len(prefix_bytes),
        "static_prefix_sha256": hashlib.sha256(prefix_bytes).hexdigest(),
        "task_suffix_bytes": len(suffix_bytes),
        "task_suffix_sha256": hashlib.sha256(suffix_bytes).hexdigest(),
        "total_bytes": len(prefix_bytes) + len(suffix_bytes),
        "cache_reuse_mode": "observed_metric_not_structural_assertion",
        "cache_reuse_observed": None,
    }


def _bounded_hypothesis_lines(task: dict[str, Any], *, max_items: int = 2, max_item_chars: int = 160) -> list[str]:
    """Render task-local failed-attempt hypotheses clearly labeled as non-normative next-attempt data."""
    raw = task.get("attempt_hypotheses")
    if not isinstance(raw, list) or not raw:
        return []
    relevant = [
        item
        for item in raw
        if isinstance(item, dict) and item.get("status") in {"open", "disproven"}
    ]
    if not relevant:
        return []
    lines = ["Task-local failed-attempt hypotheses (non-normative; never treat as validated shared facts):"]
    for item in relevant[-max_items:]:
        status = str(item.get("status", "open"))
        label = "DISPROVEN hypothesis (do not repeat or promote)" if status == "disproven" else "UNVALIDATED hypothesis"
        text = str(item.get("hypothesis", "")).strip()
        if len(text) > max_item_chars:
            text = text[: max_item_chars - 3].rstrip() + "..."
        lines.append(f"- [{label}] {item.get('id', '?')}: {text}")
    return lines


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

    def bounded_task_suffix(task: dict[str, Any], *, max_chars: int = MAX_TASK_FAILURE_SUFFIX_CHARS) -> str:
        parts: list[str] = []
        base = run_isolated.failure_context(task)
        if base:
            parts.append(base.strip())
        hyp_lines = _bounded_hypothesis_lines(task)
        if hyp_lines:
            parts.append("\n".join(hyp_lines))
        if not parts:
            return ""
        combined = "\n" + "\n".join(parts) + "\n"
        if len(combined) > max_chars:
            combined = "\n" + planctl.bounded_failure_reason(combined.strip(), max(200, max_chars - 2)) + "\n"
        return combined

    def worker_prompt(
        plan_dir: Path,
        manifest: dict[str, Any],
        task: dict[str, Any],
        route: dict[str, str],
    ) -> str:
        # Record the actual assigned context whenever the production runner
        # prepares a worker prompt.  Direct helper calls are not the only path.
        write_context_accounting_receipt(plan_dir, manifest, task)
        task_path = (plan_dir / task["file"]).resolve()
        schema_path = run_isolated.completion_schema_path().resolve()
        job_guidance = ""
        if task.get("validation_jobs"):
            job_guidance = f"""\nSupervised validation jobs: {', '.join(task['validation_jobs'])}
Job controller: `{script_dir / 'jobctl.py'}`
Plan workspace: `{plan_dir}`
For these jobs, start each mapped ID using `start --plan <workspace> --id <ID> --validation <ID> --map <task-map>`. The runner launches and waits outside your process tree. Return the ordinary completed report after implementation, synchronous checks and job requests succeed; final acceptance belongs to the runner. Retest a terminal failed job with --restart. Use bounded jobctl waits only for a short status check; do not hold model context for a long job or invent detached polling loops.\n"""
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
9. For long execution or validation, refactor code to emit meaningful PROGRESS/ERROR before raising fixed timeouts; HEARTBEAT is not progress.
10. Never start background or async agents or detached processes that report back later; this headless session ends when you stop calling tools. Run long work synchronously or as a jobctl validation job.

Subtask controller: `{controller}`
Report schema: `{schema_path}`
Repository: `{manifest['repo_root']}`
Task definition: `{task_path}`
Task: `{task['id']}`
Route: {route['provider']} / {route['model']} / {route['effort']}
Service map helper: {script_dir / 'service_map.py'}
""" + job_guidance + bounded_task_suffix(task)

    def write_context_accounting_receipt(
        plan_dir: Path,
        manifest: dict[str, Any],
        task: dict[str, Any],
        *,
        pattern_files: list[str] | None = None,
    ) -> tuple[Path, dict[str, Any]]:
        receipt = planctl.build_context_accounting_receipt(
            plan_dir,
            manifest,
            task,
            pattern_files=pattern_files,
        )
        path = plan_dir / "results" / f"{task['id']}-context-receipt.json"
        planctl.atomic_write_json(path, receipt)
        # Preserve the preparation snapshot across later retries while keeping
        # the existing latest-receipt path stable for tooling and unit tests.
        next_attempt = max(1, int(task.get("attempts", 0)) + 1)
        snapshot = plan_dir / "results" / f"{task['id']}-attempt-{next_attempt}-context-receipt.json"
        planctl.atomic_write_json(snapshot, receipt)
        return path, receipt

    original_validation = run_isolated.run_validation_commands

    def run_validation_commands(*args: Any, **kwargs: Any):
        passed, results, reason = original_validation(*args, **kwargs)
        for item in results:
            if isinstance(item, dict) and isinstance(item.get("output_tail"), str):
                tail = item["output_tail"]
                item["output_tail"] = tail[-800:] if len(tail) > 800 else tail
        if reason and len(reason) > 1500:
            reason = planctl.bounded_failure_reason(reason, 1500)
        # Runner-owned sidecar, bound to actual validation log bytes. Workers'
        # self-reported validations never create this file, and planctl's
        # public `complete --report` command does not run this function.
        log = Path(args[2]) if len(args) >= 3 else Path(kwargs["log_path"])
        if log.is_file() and not log.is_symlink():
            proof = {
                "schema_version": 1,
                "log_sha256": planctl.file_sha256(log),
                "passed": passed is True,
                "checks": [
                    {"command": item.get("command"), "passed": item.get("passed") is True,
                     "exit_code": item.get("exit_code")}
                    for item in results if isinstance(item, dict)
                ],
            }
            planctl.atomic_write_json(Path(str(log) + ".runner-evidence.json"), proof)
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
    run_isolated.bounded_task_suffix = bounded_task_suffix
    run_isolated.prompt_cache_structure = prompt_cache_structure
    run_isolated.write_context_accounting_receipt = write_context_accounting_receipt
    run_isolated.run_validation_commands = run_validation_commands
    run_isolated.compose_summary_input = compose_summary_input
    run_isolated.summary_prompt = summary_prompt
    run_isolated._concise_runner_contract = True
    return run_isolated
