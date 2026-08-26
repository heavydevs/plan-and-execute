#!/usr/bin/env python3
"""Execute plan-and-execute tasks in fresh Claude Code or Codex processes.

Each provider call starts a new, non-persistent session. The only planning file
named in the worker prompt is the current task definition. State, retries,
validation, escalation, summarization, and cleanup are handled by this script.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, IO

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

import planctl  # noqa: E402
import lifecyclectl  # noqa: E402

TIER_ORDER = ["economy", "standard", "strong", "max"]
EFFORT_ORDER = ["low", "medium", "high", "xhigh", "max"]
RATE_LIMIT_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\b429\b",
        r"rate[ -]?limit",
        r"usage limit",
        r"quota exceeded",
        r"insufficient_quota",
        r"too many requests",
        r"credits? (?:exhausted|depleted|used|limit)",
        r"capacity limit",
    )
]


class RunnerError(RuntimeError):
    """Raised for runner-specific failures."""


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for key, value in base.items():
        if isinstance(value, dict):
            merged[key] = deep_merge(value, {})
        elif isinstance(value, list):
            merged[key] = list(value)
        else:
            merged[key] = value
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(plan_dir: Path) -> dict[str, Any]:
    raw = planctl.read_json(plan_dir / planctl.CONFIG)
    if not isinstance(raw, dict):
        raise RunnerError(f"{planctl.CONFIG} must contain a JSON object")
    return deep_merge(planctl.default_config(), raw)


def command_prefix(value: Any) -> list[str]:
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return list(value)
    if isinstance(value, str) and value.strip():
        return shlex.split(value)
    raise RunnerError(f"Invalid provider command: {value!r}")


def executable_available(prefix: list[str]) -> bool:
    first = prefix[0]
    if os.path.sep in first or (os.path.altsep and os.path.altsep in first):
        return Path(first).expanduser().is_file()
    return shutil.which(first) is not None


def clamp_index(values: list[str], value: str) -> int:
    try:
        return values.index(value)
    except ValueError:
        return 0


def clamp_effort(provider_cfg: dict[str, Any], tier: str, effort: str) -> str:
    caps = provider_cfg.get("max_effort_by_tier", {})
    cap = str(caps.get(tier, "max"))
    effort_index = clamp_index(EFFORT_ORDER, effort)
    cap_index = clamp_index(EFFORT_ORDER, cap)
    return EFFORT_ORDER[min(effort_index, cap_index)]


def candidate_providers(task: dict[str, Any], config: dict[str, Any], override: str | None) -> list[str]:
    requested = override or task.get("provider", "auto")
    order = [str(item) for item in config.get("provider_order", ["claude", "codex"])]
    order = [item for item in order if item in {"claude", "codex"}]
    if not order:
        order = ["claude", "codex"]

    if requested in {"claude", "codex"}:
        providers = [requested]
        allow_fallback = bool(task.get("allow_provider_fallback", True)) and bool(
            config.get("allow_provider_fallback", True)
        )
        if allow_fallback:
            providers.extend(item for item in order if item != requested)
    else:
        providers = order

    available: list[str] = []
    for provider in providers:
        prefix = command_prefix(config[provider].get("command", provider))
        if executable_available(prefix):
            available.append(provider)
    if not available:
        requested_text = requested if requested != "auto" else ", ".join(providers)
        raise RunnerError(f"No usable provider CLI found for: {requested_text}")
    return available


def choose_route(task: dict[str, Any], config: dict[str, Any], override: str | None) -> dict[str, str]:
    providers = candidate_providers(task, config, override)
    failures_per_provider = max(1, int(config.get("functional_failures_per_provider", 4)))
    failures = int(task.get("functional_failures", 0))
    provider_slot = failures // failures_per_provider
    provider_index = min(provider_slot, len(providers) - 1)
    provider = providers[provider_index]
    if provider_slot >= len(providers):
        step = failures_per_provider - 1
    else:
        step = failures % failures_per_provider

    base_tier_index = clamp_index(TIER_ORDER, str(task.get("model_tier", "standard")))
    base_effort_index = clamp_index(EFFORT_ORDER, str(task.get("reasoning_effort", "medium")))
    if step == 0:
        tier_index = base_tier_index
        effort_index = base_effort_index
    elif step == 1:
        tier_index = base_tier_index
        effort_index = base_effort_index + 1
    elif step == 2:
        tier_index = base_tier_index + 1
        effort_index = max(base_effort_index + 1, clamp_index(EFFORT_ORDER, "high"))
    else:
        tier_index = base_tier_index + 2
        effort_index = max(base_effort_index + 2, clamp_index(EFFORT_ORDER, "xhigh"))

    tier = TIER_ORDER[min(tier_index, len(TIER_ORDER) - 1)]
    effort = EFFORT_ORDER[min(effort_index, len(EFFORT_ORDER) - 1)]
    provider_cfg = config[provider]
    effort = clamp_effort(provider_cfg, tier, effort)
    models = provider_cfg.get("models", {})
    model = str(models.get(tier, "")).strip()
    if not model:
        raise RunnerError(f"No model configured for {provider}/{tier}")
    return {"provider": provider, "tier": tier, "model": model, "effort": effort}


def completion_schema_path() -> Path:
    path = SKILL_DIR / "references" / "completion-report.schema.json"
    if not path.is_file():
        raise RunnerError(f"Completion schema not found: {path}")
    return path


def worker_prompt(plan_dir: Path, manifest: dict[str, Any], task: dict[str, Any], route: dict[str, str]) -> str:
    repo_root = Path(manifest["repo_root"])
    task_file = (plan_dir / task["file"]).resolve()
    try:
        relative_task = task_file.relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        relative_task = str(task_file)
    return f"""You are a fresh, isolated implementation worker for one bounded task.

Repository root: {repo_root}
Assigned task definition: {relative_task}
Task id: {task['id']}
Attempt: {task['attempts'] + 1}
Route: {route['provider']} / {route['model']} / effort {route['effort']}

Mandatory isolation rules:
1. Read the assigned task definition first. It is the only task definition assigned to you.
2. Then read every file listed under `Assigned execution context` in that task definition. Read no other context file.
3. Do not open PLAN.md, TODO.md, manifest.json, orchestrator.config.json, result files, logs, or any unassigned task definition under {plan_dir}.
4. You may read and edit repository source, tests, build files, and runtime output needed for this task.
5. Existing changes in the working tree may belong to earlier completed tasks. Preserve them and do not broadly revert or reformat unrelated code.
6. Open another task definition only when the assigned definition explicitly permits its id and a dependency, ambiguity, or validation conflict makes it necessary. Report the id and reason.
7. Implement only this task, run its required validation commands, and avoid speculative work outside scope.
8. Do not edit any planning or context artifact. The orchestrator owns plan state.
9. Do not ask for conversational context. When blocked, stop safely and report the concrete blocker.
10. Report `context_files_read` using the plan-relative names from the task frontmatter, such as `CONTEXT.md` or `contexts/topic.md`; use an empty list when none are assigned.

Return only the completion report requested by the configured JSON schema. Use status "completed" only when the task is implemented and its required checks pass; otherwise use "blocked".
"""


def build_worker_command(
    provider: str,
    route: dict[str, str],
    config: dict[str, Any],
    prompt: str,
    result_path: Path,
) -> list[str]:
    provider_cfg = config[provider]
    prefix = command_prefix(provider_cfg.get("command", provider))
    schema_path = completion_schema_path()
    extra_args = provider_cfg.get("extra_args", [])
    if not isinstance(extra_args, list) or not all(isinstance(item, str) for item in extra_args):
        raise RunnerError(f"{provider}.extra_args must be a list of strings")

    if provider == "claude":
        schema_text = json.dumps(planctl.read_json(schema_path), ensure_ascii=False, separators=(",", ":"))
        command = prefix + [
            "--bare",
            "--print",
            "--no-session-persistence",
            "--output-format",
            "json",
            "--permission-mode",
            str(provider_cfg.get("permission_mode", "auto")),
            "--model",
            route["model"],
            "--effort",
            route["effort"],
            "--json-schema",
            schema_text,
        ]
        command.extend(extra_args)
        command.append(prompt)
        return command

    command = prefix + [
        "exec",
        "--ephemeral",
        "--sandbox",
        str(provider_cfg.get("sandbox", "workspace-write")),
        "--model",
        route["model"],
        "-c",
        f'model_reasoning_effort="{route["effort"]}"',
        "--output-schema",
        str(schema_path),
        "--output-last-message",
        str(result_path),
    ]
    if provider_cfg.get("ignore_user_config"):
        command.append("--ignore-user-config")
    command.extend(extra_args)
    command.append(prompt)
    return command


def pump_stream(
    stream: IO[str],
    buffer: list[str],
    log: IO[str],
    prefix: str,
    show: bool,
) -> None:
    try:
        for line in iter(stream.readline, ""):
            buffer.append(line)
            log.write(f"{prefix}{line}")
            log.flush()
            if show:
                print(f"{prefix}{line}", end="", flush=True)
    finally:
        stream.close()


def run_process(
    command: list[str],
    cwd: Path,
    log_path: Path,
    *,
    timeout_seconds: int,
    stream_output: bool,
) -> tuple[int, str, str]:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    stdout_lines: list[str] = []
    stderr_lines: list[str] = []
    with log_path.open("w", encoding="utf-8", newline="\n") as log:
        log.write("COMMAND: " + shlex.join(command[:-1] + ["<prompt>"]) + "\n\n")
        log.flush()
        try:
            process = subprocess.Popen(
                command,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )
        except OSError as exc:
            raise RunnerError(f"Failed to start provider process: {exc}") from exc
        assert process.stdout is not None
        assert process.stderr is not None
        stdout_thread = threading.Thread(
            target=pump_stream,
            args=(process.stdout, stdout_lines, log, "[stdout] ", stream_output),
            daemon=True,
        )
        stderr_thread = threading.Thread(
            target=pump_stream,
            args=(process.stderr, stderr_lines, log, "[stderr] ", stream_output),
            daemon=True,
        )
        stdout_thread.start()
        stderr_thread.start()
        try:
            return_code = process.wait(timeout=timeout_seconds or None)
        except subprocess.TimeoutExpired:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            return_code = 124
            stderr_lines.append(f"Provider timed out after {timeout_seconds} seconds\n")
        except KeyboardInterrupt:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            raise
        finally:
            stdout_thread.join(timeout=5)
            stderr_thread.join(timeout=5)
    return return_code, "".join(stdout_lines), "".join(stderr_lines)


def extract_report(value: Any) -> dict[str, Any] | None:
    if isinstance(value, dict):
        if value.get("status") in {"completed", "blocked"} and isinstance(value.get("summary"), str):
            return value
        for key in ("structured_output", "output", "result", "message", "content"):
            if key in value:
                found = extract_report(value[key])
                if found:
                    return found
        for nested in value.values():
            found = extract_report(nested)
            if found:
                return found
    elif isinstance(value, list):
        for item in value:
            found = extract_report(item)
            if found:
                return found
    elif isinstance(value, str):
        text = value.strip()
        if text.startswith("{"):
            try:
                return extract_report(json.loads(text))
            except json.JSONDecodeError:
                return None
    return None


def parse_provider_report(provider: str, stdout: str, result_path: Path) -> dict[str, Any] | None:
    candidates: list[Any] = []
    if result_path.is_file():
        try:
            candidates.append(json.loads(result_path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            candidates.append(result_path.read_text(encoding="utf-8"))
    if stdout.strip():
        try:
            candidates.append(json.loads(stdout))
        except json.JSONDecodeError:
            for line in reversed(stdout.splitlines()):
                line = line.strip()
                if line.startswith("{"):
                    try:
                        candidates.append(json.loads(line))
                        break
                    except json.JSONDecodeError:
                        continue
    for candidate in candidates:
        report = extract_report(candidate)
        if report:
            return report
    return None


def is_rate_limited(text: str) -> bool:
    return any(pattern.search(text) for pattern in RATE_LIMIT_PATTERNS)


def output_tail(text: str, length: int = 3000) -> str:
    stripped = text.strip()
    return stripped[-length:] if stripped else ""


def run_validation_commands(
    repo_root: Path,
    commands: list[str],
    log_path: Path,
    timeout_seconds: int,
) -> tuple[bool, list[dict[str, Any]], str | None]:
    results: list[dict[str, Any]] = []
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8", newline="\n") as log:
        for command in commands:
            print(f"[validate] {command}", flush=True)
            log.write(f"$ {command}\n")
            try:
                completed = subprocess.run(
                    command,
                    cwd=repo_root,
                    shell=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    timeout=timeout_seconds or None,
                )
                output = completed.stdout or ""
                exit_code = completed.returncode
            except subprocess.TimeoutExpired as exc:
                output = (exc.stdout or "") + f"\nTimed out after {timeout_seconds} seconds"
                exit_code = 124
            log.write(output)
            if output and not output.endswith("\n"):
                log.write("\n")
            log.write(f"[exit {exit_code}]\n\n")
            passed = exit_code == 0
            results.append(
                {
                    "command": command,
                    "passed": passed,
                    "exit_code": exit_code,
                    "output_tail": output_tail(output, 2000),
                }
            )
            if not passed:
                reason = f"Validation failed: {command} (exit {exit_code})\n{output_tail(output)}"
                return False, results, reason
    return True, results, None


def git_changed_files(repo_root: Path) -> list[str]:
    commands = [
        ["git", "diff", "--name-only"],
        ["git", "diff", "--cached", "--name-only"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    ]
    files: set[str] = set()
    for command in commands:
        try:
            completed = subprocess.run(
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
        if completed.returncode == 0:
            files.update(line.strip() for line in completed.stdout.splitlines() if line.strip())
    return sorted(files)


def release_interrupted_task(plan_dir: Path, manifest: dict[str, Any], task_id: str) -> None:
    task = planctl.find_task(manifest, task_id)
    if task.get("status") == "in_progress":
        task["status"] = "pending"
        task["last_error"] = "Execution interrupted; safe to resume."
        task["history"].append({"at": planctl.now_utc(), "event": "interrupted"})
        planctl.append_event(manifest, "task_interrupted", task_id=task["id"])
        planctl.save_manifest(plan_dir, manifest)


def wait_after_rate_limit(config: dict[str, Any], cycle: int, no_wait: bool) -> bool:
    rate_cfg = config.get("rate_limit", {})
    if no_wait or not rate_cfg.get("auto_wait", True):
        return False
    max_cycles = int(rate_cfg.get("max_wait_cycles", 0))
    if max_cycles > 0 and cycle >= max_cycles:
        return False
    base = max(1, int(rate_cfg.get("wait_seconds", 300)))
    seconds = min(base * (2 ** min(cycle, 4)), 3600)
    print(f"[rate-limit] Provider unavailable. Retrying automatically in {seconds} seconds. Ctrl+C keeps the plan resumable.")
    time.sleep(seconds)
    return True


def normalized_result_file(plan_dir: Path, task: dict[str, Any], route: dict[str, str]) -> Path:
    name = f"{task['id']}-attempt-{task['attempts'] + 1}-{route['provider']}.json"
    return plan_dir / "results" / name


def execute_one_task(
    plan_dir: Path,
    manifest: dict[str, Any],
    config: dict[str, Any],
    task: dict[str, Any],
    *,
    provider_override: str | None,
    dry_run: bool,
    no_wait: bool,
) -> bool:
    repo_root = Path(manifest["repo_root"])
    rate_cycle = 0
    while True:
        route = choose_route(task, config, provider_override)
        result_path = normalized_result_file(plan_dir, task, route)
        prompt = worker_prompt(plan_dir, manifest, task, route)
        command = build_worker_command(route["provider"], route, config, prompt, result_path)
        if dry_run:
            print(json.dumps({"task": task["id"], "route": route, "command": command[:-1] + ["<prompt>"]}, indent=2))
            return False

        print(
            f"[task {task['id']}] {task['title']} — {route['provider']} / {route['model']} / {route['effort']}",
            flush=True,
        )
        claimed = planctl.claim_task(plan_dir, manifest, task["id"], route)
        attempt_number = claimed["attempts"]
        log_path = plan_dir / "logs" / f"{task['id']}-attempt-{attempt_number}-{route['provider']}.log"
        try:
            return_code, stdout, stderr = run_process(
                command,
                repo_root,
                log_path,
                timeout_seconds=max(0, int(config.get("task_timeout_seconds", 0))),
                stream_output=bool(config.get("stream_provider_output", True)),
            )
        except KeyboardInterrupt:
            release_interrupted_task(plan_dir, manifest, task["id"])
            raise

        combined = f"{stdout}\n{stderr}"
        if return_code != 0 and is_rate_limited(combined):
            planctl.fail_task(
                plan_dir,
                manifest,
                task["id"],
                f"Provider rate/usage limit (exit {return_code}): {output_tail(combined)}",
                rate_limited=True,
            )
            task = planctl.find_task(manifest, task["id"])
            if wait_after_rate_limit(config, rate_cycle, no_wait):
                rate_cycle += 1
                continue
            raise RunnerError(f"Rate/usage limit stopped task {task['id']}; rerun the command to resume")

        report = parse_provider_report(route["provider"], stdout, result_path)
        if return_code != 0:
            reason = f"Provider exited with {return_code}: {output_tail(combined)}"
            planctl.fail_task(plan_dir, manifest, task["id"], reason)
            print(f"[task {task['id']}] provider failure; route will escalate on retry", file=sys.stderr)
            return False
        if not report:
            reason = f"Provider returned no valid completion report. Output: {output_tail(combined)}"
            planctl.fail_task(plan_dir, manifest, task["id"], reason)
            print(f"[task {task['id']}] invalid report; route will escalate on retry", file=sys.stderr)
            return False
        expected_context_files = list(task.get("context_files", []))
        reported_context_files = report.get("context_files_read")
        if reported_context_files != expected_context_files:
            reason = (
                "Worker context report mismatch: expected "
                f"{expected_context_files!r}, received {reported_context_files!r}"
            )
            planctl.fail_task(plan_dir, manifest, task["id"], reason)
            print(f"[task {task['id']}] context assignment was not acknowledged", file=sys.stderr)
            return False
        if report.get("status") != "completed":
            reason = str(report.get("blocked_reason") or report.get("summary") or "Worker reported blocked")
            if is_rate_limited(reason):
                planctl.fail_task(plan_dir, manifest, task["id"], reason, rate_limited=True)
                task = planctl.find_task(manifest, task["id"])
                if wait_after_rate_limit(config, rate_cycle, no_wait):
                    rate_cycle += 1
                    continue
                raise RunnerError(f"Rate/usage limit stopped task {task['id']}; rerun the command to resume")
            planctl.fail_task(plan_dir, manifest, task["id"], reason)
            atomic = {**report, "orchestrator_status": "failed"}
            planctl.atomic_write_json(result_path, atomic)
            print(f"[task {task['id']}] blocked: {reason}", file=sys.stderr)
            return False

        validation_log = plan_dir / "logs" / f"{task['id']}-attempt-{attempt_number}-validation.log"
        passed, validation_results, validation_reason = run_validation_commands(
            repo_root,
            list(task["validation_commands"]),
            validation_log,
            max(0, int(config.get("validation_timeout_seconds", 1800))),
        )
        report["validation_results"] = validation_results
        reported_files = report.get("changed_files")
        if not isinstance(reported_files, list) or not reported_files:
            report["changed_files"] = git_changed_files(repo_root)
        if not passed:
            report["orchestrator_status"] = "validation_failed"
            planctl.atomic_write_json(result_path, report)
            planctl.fail_task(plan_dir, manifest, task["id"], validation_reason or "Validation failed")
            print(f"[task {task['id']}] deterministic validation failed; route will escalate", file=sys.stderr)
            return False

        report["orchestrator_status"] = "completed"
        planctl.atomic_write_json(result_path, report)
        relative_result = result_path.relative_to(plan_dir).as_posix()
        planctl.complete_task(plan_dir, manifest, task["id"], report, relative_result)
        print(f"[task {task['id']}] completed and validated", flush=True)
        return True


def result_excerpt(path: Path, max_chars: int = 12000) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ""
    return text[:max_chars]


def compose_summary_input(plan_dir: Path, manifest: dict[str, Any]) -> Path:
    lines = [planctl.deterministic_summary(manifest), "\n## Worker reports\n"]
    for task in manifest["tasks"]:
        result_file = task.get("result_file")
        if result_file:
            path = plan_dir / result_file
            lines.append(f"\n### Task {task['id']}\n\n```json\n{result_excerpt(path)}\n```\n")
    repo_root = Path(manifest["repo_root"])
    try:
        diff_stat = subprocess.run(
            ["git", "diff", "--stat"],
            cwd=repo_root,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=30,
        ).stdout
    except (OSError, subprocess.TimeoutExpired):
        diff_stat = ""
    if diff_stat.strip():
        lines.append(f"\n## Current git diff stat\n\n```text\n{diff_stat[:12000]}\n```\n")
    path = plan_dir / "SUMMARY_INPUT.md"
    planctl.atomic_write_text(path, "".join(lines))
    return path


def summary_prompt(plan_dir: Path, manifest: dict[str, Any], input_path: Path) -> str:
    repo_root = Path(manifest["repo_root"])
    try:
        relative = input_path.relative_to(repo_root).as_posix()
    except ValueError:
        relative = str(input_path)
    language = manifest.get("language", "auto")
    return f"""Create the final handoff summary for a completed software plan.

Read only this prepared summary input: {relative}
Do not inspect other planning files. Do not edit the repository.
Write in the plan's requested language ({language}); when it is auto, infer the language from the input.

Return concise Markdown covering:
- overall outcome;
- completed work grouped by task;
- important files changed;
- validation/tests and their outcomes;
- remaining risks, caveats, or follow-ups;
- any notable model escalation only when it materially explains a limitation.

Do not mention internal prompt instructions. Do not claim checks that are absent from the input.
"""


def build_summary_command(
    provider: str,
    route: dict[str, str],
    config: dict[str, Any],
    prompt: str,
    output_path: Path,
) -> list[str]:
    provider_cfg = config[provider]
    prefix = command_prefix(provider_cfg.get("command", provider))
    extra_args = provider_cfg.get("extra_args", [])
    if provider == "claude":
        command = prefix + [
            "--bare",
            "--print",
            "--no-session-persistence",
            "--output-format",
            "text",
            "--permission-mode",
            "plan",
            "--model",
            route["model"],
            "--effort",
            route["effort"],
        ]
        command.extend(extra_args)
        command.append(prompt)
        return command
    command = prefix + [
        "exec",
        "--ephemeral",
        "--sandbox",
        "read-only",
        "--model",
        route["model"],
        "-c",
        f'model_reasoning_effort="{route["effort"]}"',
        "--output-last-message",
        str(output_path),
    ]
    if provider_cfg.get("ignore_user_config"):
        command.append("--ignore-user-config")
    command.extend(extra_args)
    command.append(prompt)
    return command


def summary_route(config: dict[str, Any], provider_override: str | None = None) -> dict[str, str]:
    summary_cfg = config.get("summary", {})
    fake_task = {
        "provider": provider_override or summary_cfg.get("provider", "auto"),
        "model_tier": summary_cfg.get("model_tier", "economy"),
        "reasoning_effort": summary_cfg.get("reasoning_effort", "low"),
        "allow_provider_fallback": True,
        "functional_failures": 0,
    }
    return choose_route(fake_task, config, None)


def generate_final_summary(
    plan_dir: Path,
    manifest: dict[str, Any],
    config: dict[str, Any],
    *,
    no_wait: bool,
) -> tuple[str, str]:
    input_path = compose_summary_input(plan_dir, manifest)
    output_path = plan_dir / "FINAL_SUMMARY.md"
    prompt = summary_prompt(plan_dir, manifest, input_path)
    rate_cycle = 0
    try:
        route = summary_route(config)
    except RunnerError:
        fallback = planctl.deterministic_summary(manifest)
        planctl.atomic_write_text(output_path, fallback)
        return fallback, output_path.relative_to(plan_dir).as_posix()

    while True:
        command = build_summary_command(route["provider"], route, config, prompt, output_path)
        log_path = plan_dir / "logs" / f"final-summary-{route['provider']}.log"
        print(f"[summary] {route['provider']} / {route['model']} / {route['effort']}", flush=True)
        return_code, stdout, stderr = run_process(
            command,
            Path(manifest["repo_root"]),
            log_path,
            timeout_seconds=max(0, int(config.get("task_timeout_seconds", 0))),
            stream_output=False,
        )
        combined = f"{stdout}\n{stderr}"
        if return_code != 0 and is_rate_limited(combined):
            if wait_after_rate_limit(config, rate_cycle, no_wait):
                rate_cycle += 1
                continue
        if return_code == 0:
            if route["provider"] == "claude":
                summary = stdout.strip()
                if summary:
                    planctl.atomic_write_text(output_path, summary + "\n")
            else:
                summary = output_path.read_text(encoding="utf-8").strip() if output_path.is_file() else ""
            if summary:
                return summary + "\n", output_path.relative_to(plan_dir).as_posix()
        fallback = planctl.deterministic_summary(manifest)
        planctl.atomic_write_text(output_path, fallback)
        return fallback, output_path.relative_to(plan_dir).as_posix()


def _run_plan(args: argparse.Namespace) -> int:
    plan_dir, manifest = planctl.load_plan(args.plan)
    planctl.require_valid(plan_dir, manifest)
    config = load_config(plan_dir)

    if args.dry_run:
        task = planctl.next_runnable_task(manifest)
        if not task:
            print("No runnable pending task")
            return 0
        execute_one_task(
            plan_dir,
            manifest,
            config,
            task,
            provider_override=args.provider,
            dry_run=True,
            no_wait=True,
        )
        return 0

    completed_this_run = 0
    try:
        while True:
            task = planctl.next_runnable_task(manifest)
            if task is None:
                break
            execute_one_task(
                plan_dir,
                manifest,
                config,
                task,
                provider_override=args.provider,
                dry_run=False,
                no_wait=args.no_wait,
            )
            completed_this_run += 1
            if args.once:
                break
    except KeyboardInterrupt:
        print("\nExecution interrupted. Plan state was kept for a later resume.", file=sys.stderr)
        return 130

    plan_dir, manifest = planctl.load_plan(plan_dir)
    if args.once and manifest.get("state") != "completed":
        print(planctl.render_todo(manifest), end="")
        return 0

    if manifest.get("state") == "completed":
        summary, summary_file = generate_final_summary(plan_dir, manifest, config, no_wait=args.no_wait)
        planctl.mark_summary(plan_dir, manifest, summary_file)
        print("\n" + summary, end="")
        should_cleanup = (
            not args.no_cleanup
            and bool(config.get("auto_cleanup", True))
            and bool(manifest.get("cleanup_on_success", True))
        )
        # Terminal work must never block the next default invocation, even when
        # the completed plan is intentionally retained for inspection.
        lifecyclectl.clear_active(plan_dir)
        if should_cleanup:
            planctl.cleanup_plan(plan_dir, manifest)
            print("\n[cleanup] Planning artifacts deleted; implementation files were preserved.")
        else:
            print(f"\n[plan] Planning artifacts retained at {plan_dir}")
        return 0

    blocked = [task for task in manifest["tasks"] if task["status"] == "blocked"]
    if blocked:
        print(planctl.render_todo(manifest), end="", file=sys.stderr)
        return 4
    if completed_this_run == 0:
        print("No runnable task. Check dependencies and task states.", file=sys.stderr)
        print(planctl.render_todo(manifest), end="", file=sys.stderr)
        return 3
    return 0



def run_plan(args: argparse.Namespace) -> int:
    """Run or resume a plan under an atomic lease."""
    plan_dir, _ = planctl.load_plan(args.plan)
    lifecyclectl.activate_plan(plan_dir)
    with lifecyclectl.runner_lease(plan_dir):
        recovered = lifecyclectl.recover_interrupted_tasks(
            plan_dir,
            allow_live_lease=True,
        )
        if recovered:
            print(
                f"[resume] Recovered {recovered} interrupted task(s); "
                "partial repository changes were preserved.",
                flush=True,
            )
        return _run_plan(args)


def _interrupt_on_signal(signum: int, frame: object) -> None:
    del signum, frame
    raise KeyboardInterrupt


def install_signal_handlers() -> None:
    if hasattr(signal, "SIGTERM"):
        try:
            signal.signal(signal.SIGTERM, _interrupt_on_signal)
        except (OSError, ValueError):
            pass

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, help="Path to the plan workspace")
    parser.add_argument("--provider", choices=["claude", "codex"], help="Override task provider")
    parser.add_argument("--once", action="store_true", help="Execute at most one task")
    parser.add_argument("--dry-run", action="store_true", help="Print the next provider command without executing")
    parser.add_argument("--no-wait", action="store_true", help="Do not wait and retry on rate/usage limits")
    parser.add_argument("--no-cleanup", action="store_true", help="Keep planning artifacts after success")
    return parser


def main() -> int:
    install_signal_handlers()
    args = build_parser().parse_args()
    try:
        return run_plan(args)
    except (planctl.PlanError, RunnerError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
