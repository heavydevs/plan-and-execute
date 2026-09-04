#!/usr/bin/env python3
"""Execute plan-and-execute tasks in fresh supported coding-agent processes.

Each provider call starts a new, non-persistent session. The only planning file
named in the worker prompt is the current task definition. State, retries,
validation, escalation, summarization, and cleanup are handled by this script.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import random
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
        r"(?:http|error|status|code)[^\n]{0,24}\b429\b",
        r"(?:exceeded|hit|reached|due to|error:?)[^\n]{0,32}rate[ -]?limit",
        r"usage limit (?:exceeded|reached)",
        r"quota (?:is )?exceeded",
        r"insufficient_quota",
        r"too many requests",
        r"credits? (?:exhausted|depleted|used|limit)",
        r"capacity limit",
    )
]

ENVIRONMENT_FAILURE_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"command not found",
        r"no such file or directory",
        r"permission denied",
        r"authentication (?:failed|required)",
        r"not authenticated",
        r"invalid api key",
        r"no space left on device",
        r"read-only file system",
        r"network is unreachable",
        r"connection refused",
    )
]

DEFERRED_EXIT_CODE = 75
_CAPABILITY_CACHE: dict[str, dict[str, Any]] = {}


class RunnerError(RuntimeError):
    """Raised for runner-specific failures."""


def refresh_manifest(plan_dir: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    """Refresh a caller-held manifest without invalidating existing references."""
    _, current = planctl.load_plan(plan_dir)
    manifest.clear()
    manifest.update(current)
    return manifest


def classify_provider_failure(
    provider: str,
    return_code: int,
    stderr: str,
    stdout: str,
    config: dict[str, Any],
) -> str:
    """Classify failures before deciding whether model escalation is useful."""
    diagnostic = stderr.strip() or stdout.strip()
    if return_code in configured_retry_exit_codes(provider, config) or is_rate_limited(diagnostic):
        return "availability"
    if any(pattern.search(diagnostic) for pattern in ENVIRONMENT_FAILURE_PATTERNS):
        return "environment"
    return "capability"


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


def probe_provider(provider: str, config: dict[str, Any]) -> dict[str, Any]:
    provider_cfg = config[provider]
    prefix = command_prefix(provider_cfg.get("command", provider))
    cache_key = json.dumps([provider, prefix], ensure_ascii=False)
    if cache_key in _CAPABILITY_CACHE:
        return dict(_CAPABILITY_CACHE[cache_key])
    version = "unknown"
    help_text = ""
    try:
        completed = subprocess.run(
            prefix + ["--version"],
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=5,
        )
        first_line = (completed.stdout or "").strip().splitlines()
        if completed.returncode == 0 and first_line:
            version = first_line[0][:160]
    except (OSError, subprocess.TimeoutExpired):
        pass
    try:
        completed = subprocess.run(
            prefix + ["--help"],
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=5,
        )
        if completed.returncode == 0:
            help_text = completed.stdout or ""
    except (OSError, subprocess.TimeoutExpired):
        pass
    feature_flags = {
        "--bare": "bare",
        "--json-schema": "json_schema",
        "--output-schema": "output_schema",
        "--exclude-dynamic-system-prompt-sections": "exclude_dynamic_system_prompt_sections",
        "--max-budget-usd": "budget",
        "--json": "json_events",
        "--output-format": "structured_output",
        "--trajectory-file": "trajectory",
    }
    features = sorted(name for flag, name in feature_flags.items() if flag in help_text)
    result = {
        "command": prefix[0],
        "version": version,
        "features": features,
        "probed_at": planctl.now_utc(),
    }
    _CAPABILITY_CACHE[cache_key] = result
    return dict(result)


def record_provider_capabilities(
    plan_dir: Path,
    manifest: dict[str, Any],
    provider: str,
    capabilities: dict[str, Any],
) -> None:
    recorded = manifest.setdefault("provider_capabilities", {})
    comparable = {key: value for key, value in capabilities.items() if key != "probed_at"}
    previous = recorded.get(provider)
    previous_comparable = (
        {key: value for key, value in previous.items() if key != "probed_at"}
        if isinstance(previous, dict)
        else None
    )
    if previous_comparable == comparable:
        return
    recorded[provider] = capabilities
    planctl.append_event(manifest, "provider_capabilities_recorded", provider=provider)
    planctl.save_manifest(plan_dir, manifest)


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
    supported = planctl.VALID_PROVIDERS - {"auto"}
    order = [item for item in order if item in supported]
    if not order:
        order = ["claude", "codex"]

    if requested in supported:
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


def compile_task_packet(
    plan_dir: Path,
    manifest: dict[str, Any],
    task: dict[str, Any],
) -> Path:
    """Compile all assigned plan context into one immutable, provenance-marked read."""
    sections: list[str] = [
        "# Compiled execution packet",
        "",
        f"Plan revision: {manifest.get('revision', 0)}",
        f"Task id: {task['id']}",
        "",
    ]
    assigned = [task["file"], *task.get("context_files", []), *task.get("learning_files", [])]
    for relative in assigned:
        clean = planctl.checked_relative_path(str(relative), "task packet source")
        path = plan_dir / clean
        if path.is_symlink() or not path.is_file():
            raise RunnerError(f"Assigned task packet source is missing or unsafe: {relative}")
        content = path.read_text(encoding="utf-8")
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        sections.extend(
            [
                f"## Source: {clean}",
                f"SHA-256: `{digest}`",
                "",
                content.rstrip(),
                "",
            ]
        )
    packet_content = "\n".join(sections).rstrip() + "\n"
    packet_digest = hashlib.sha256(packet_content.encode("utf-8")).hexdigest()[:12]
    packet = plan_dir / "packets" / (
        f"{task['id']}-r{manifest.get('revision', 0)}-{packet_digest}.md"
    )
    if packet.is_file():
        if packet.read_text(encoding="utf-8") != packet_content:
            raise RunnerError(f"Compiled task packet hash collision: {packet}")
    else:
        planctl.atomic_write_text(packet, packet_content)
    return packet


def worker_prompt(plan_dir: Path, manifest: dict[str, Any], task: dict[str, Any], route: dict[str, str]) -> str:
    repo_root = Path(manifest["repo_root"])
    task_file = compile_task_packet(plan_dir, manifest, task).resolve()
    try:
        relative_task = task_file.relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        relative_task = str(task_file)
    return f"""You are a fresh, isolated implementation worker for one bounded task.

Stable execution contract:
1. Read only the assigned compiled packet; it contains the task capsule and every assigned context and validated learning.
2. Do not read plan manifests, plan summaries, logs, results, or unassigned task capsules.
3. You may inspect and edit repository source, tests, build files, and runtime output required by the task.
4. Preserve pre-existing work. Do not broadly revert, reformat, or modify anything outside scope.
5. Implement only the assigned task and run every required validation command.
6. Planning artifacts are orchestrator-owned. Update subtask state only through the supplied controller commands.
7. If blocked, stop safely and report the concrete blocker; never request missing chat history.
8. Report exact assigned context/learning paths, completed subtask ids, and only validated reusable learnings for declared targets.
9. Return only the JSON completion report. Use `completed` only after implementation and required checks pass.

Dynamic task envelope:
- Repository root: {repo_root}
- Compiled task packet: {relative_task}
- Task id: {task['id']}
- Attempt: {task['attempts'] + 1}
- Route: {route['provider']} / {route['model']} / effort {route['effort']}
- Forbidden planning workspace: {plan_dir}
- Start checkpoint: `python {SCRIPT_DIR / 'planctl.py'} subtask-start --plan {plan_dir} --task {task['id']} --subtask <id>`
- Complete checkpoint: `python {SCRIPT_DIR / 'planctl.py'} subtask-complete --plan {plan_dir} --task {task['id']} --subtask <id>`
"""


def configured_model_args(flag: str, model: str) -> list[str]:
    return [] if not model or model == "default" else [flag, model]


def redact_command(command: list[str]) -> list[str]:
    """Hide embedded worker prompts regardless of provider argument ordering."""
    redacted: list[str] = []
    for item in command:
        text = str(item)
        if (
            "\n" in text
            or text.startswith("You are a fresh, isolated implementation worker")
            or text.startswith("You are a fresh, isolated final summarizer")
        ):
            redacted.append("<prompt>")
        else:
            redacted.append(text)
    return redacted


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
    schema = planctl.read_json(schema_path)
    schema_text = json.dumps(schema, ensure_ascii=False, separators=(",", ":"))
    extra_args = provider_cfg.get("extra_args", [])
    if not isinstance(extra_args, list) or not all(isinstance(item, str) for item in extra_args):
        raise RunnerError(f"{provider}.extra_args must be a list of strings")

    if provider == "claude":
        command = prefix + [
            "--bare",
            "--print",
            "--no-session-persistence",
            "--output-format",
            "json",
            "--permission-mode",
            str(provider_cfg.get("permission_mode", "auto")),
        ]
        if (
            provider_cfg.get("exclude_dynamic_system_prompt_sections", True)
            and provider_cfg.get("_supports_exclude_dynamic_system_prompt_sections", False)
        ):
            command.append("--exclude-dynamic-system-prompt-sections")
        max_budget_usd = float(provider_cfg.get("max_budget_usd", 0) or 0)
        if max_budget_usd > 0:
            command.extend(["--max-budget-usd", str(max_budget_usd)])
        max_turns = int(provider_cfg.get("max_turns", 0) or 0)
        if max_turns > 0:
            command.extend(["--max-turns", str(max_turns)])
        command.extend(configured_model_args("--model", route["model"]))
        command.extend(["--effort", route["effort"], "--json-schema", schema_text])
        command.extend(extra_args)
        command.append(prompt)
        return command

    if provider == "codex":
        command = prefix + [
            "exec",
            "--ephemeral",
            "--json",
            "--sandbox",
            str(provider_cfg.get("sandbox", "workspace-write")),
        ]
        command.extend(configured_model_args("--model", route["model"]))
        command.extend(
            [
                "-c",
                f'model_reasoning_effort="{route["effort"]}"',
                "-c",
                f'model_verbosity="{provider_cfg.get("model_verbosity", "low")}"',
                "-c",
                f'model_reasoning_summary="{provider_cfg.get("model_reasoning_summary", "none")}"',
                "--output-schema",
                str(schema_path),
                "--output-last-message",
                str(result_path),
            ]
        )
        if provider_cfg.get("ignore_user_config"):
            command.append("--ignore-user-config")
        command.extend(extra_args)
        command.append(prompt)
        return command

    if provider == "gemini":
        command = prefix + [
            "--approval-mode",
            str(provider_cfg.get("approval_mode", "yolo")),
            "--output-format",
            "json",
        ]
        if provider_cfg.get("disable_extensions", True):
            command.extend(["--extensions", "none"])
        command.extend(configured_model_args("--model", route["model"]))
        command.extend(extra_args)
        command.extend(["--prompt", prompt])
        return command

    if provider == "qwen":
        command = prefix
        if provider_cfg.get("safe_mode", True):
            command.append("--safe-mode")
        if provider_cfg.get("sandbox", False):
            command.append("--sandbox")
        command.extend([
            "--output-format",
            "json",
            "--approval-mode",
            str(provider_cfg.get("approval_mode", "yolo")),
            "--json-schema",
            schema_text,
        ])
        command.extend(configured_model_args("--model", route["model"]))
        command.extend(extra_args)
        command.extend(["--prompt", prompt])
        return command

    if provider == "kimi":
        command = prefix + [
            "--output-format",
            "stream-json",
        ]
        permission_mode = str(provider_cfg.get("permission_mode", "auto")).strip()
        if permission_mode:
            if permission_mode not in {"auto", "plan", "yolo"}:
                raise RunnerError(
                    "kimi.permission_mode must be auto, plan, yolo, or an empty string"
                )
            command.append(f"--{permission_mode}")
        command.extend(configured_model_args("--model", route["model"]))
        command.extend(extra_args)
        command.extend(["--prompt", prompt])
        return command

    if provider == "trae":
        trajectory_path = result_path.parent.parent / "logs" / (
            result_path.stem + "-trae-trajectory.json"
        )
        command = prefix + [
            "run",
            prompt,
            "--working-dir",
            ".",
            "--trajectory-file",
            str(trajectory_path),
        ]
        model_provider = str(provider_cfg.get("model_provider", "")).strip()
        if model_provider:
            command.extend(["--provider", model_provider])
        command.extend(configured_model_args("--model", route["model"]))
        command.extend(extra_args)
        return command

    raise RunnerError(f"Unsupported provider adapter: {provider}")


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
        log.write("COMMAND: " + shlex.join(redact_command(command)) + "\n\n")
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


def decode_json_candidates(text: str, *, maximum: int = 200) -> list[Any]:
    """Decode full JSON, JSONL, fenced JSON, and embedded JSON objects defensively."""
    stripped = text.strip()
    if not stripped:
        return []
    values: list[Any] = []
    fingerprints: set[str] = set()

    def add(value: Any) -> None:
        try:
            fingerprint = json.dumps(value, ensure_ascii=False, sort_keys=True)
        except (TypeError, ValueError):
            fingerprint = repr(value)
        if fingerprint not in fingerprints:
            fingerprints.add(fingerprint)
            values.append(value)

    try:
        add(json.loads(stripped))
    except json.JSONDecodeError:
        pass

    for match in re.finditer(r"```(?:json)?\s*([\s\S]*?)```", stripped, re.IGNORECASE):
        try:
            add(json.loads(match.group(1).strip()))
        except json.JSONDecodeError:
            continue

    for line in reversed(stripped.splitlines()):
        candidate = line.strip()
        if not candidate.startswith(("{", "[")):
            continue
        try:
            add(json.loads(candidate))
        except json.JSONDecodeError:
            continue
        if len(values) >= maximum:
            return values

    decoder = json.JSONDecoder()
    starts = [index for index, char in enumerate(stripped) if char in "{["]
    for start in reversed(starts[-maximum:]):
        try:
            value, _end = decoder.raw_decode(stripped[start:])
        except json.JSONDecodeError:
            continue
        add(value)
        if len(values) >= maximum:
            break
    return values


def extract_report(value: Any) -> dict[str, Any] | None:
    if isinstance(value, dict):
        if value.get("status") in {"completed", "blocked"} and isinstance(value.get("summary"), str):
            return value
        for key in (
            "structured_output",
            "output",
            "result",
            "response",
            "message",
            "content",
            "answer",
            "final_message",
            "final_output",
            "data",
        ):
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
        for candidate in decode_json_candidates(text):
            if candidate == value:
                continue
            found = extract_report(candidate)
            if found:
                return found
    return None


def parse_provider_report(provider: str, stdout: str, result_path: Path) -> dict[str, Any] | None:
    candidates: list[Any] = []
    if result_path.is_file():
        result_text = result_path.read_text(encoding="utf-8")
        candidates.extend(decode_json_candidates(result_text))
        candidates.append(result_text)
    if stdout.strip():
        candidates.extend(decode_json_candidates(stdout))
        candidates.append(stdout)
    for candidate in candidates:
        report = extract_report(candidate)
        if report:
            return report
    return None


def provider_metrics(provider: str, stdout: str) -> dict[str, Any]:
    """Extract only host-reported usage fields; never ask the worker to repeat them."""
    metrics: dict[str, Any] = {"provider": provider, "captured_at": planctl.now_utc()}
    for candidate in decode_json_candidates(stdout):
        if not isinstance(candidate, dict):
            continue
        usage = candidate.get("usage")
        if isinstance(usage, dict):
            for key in (
                "input_tokens",
                "cached_input_tokens",
                "cache_creation_input_tokens",
                "cache_read_input_tokens",
                "output_tokens",
                "reasoning_output_tokens",
            ):
                value = usage.get(key)
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    metrics[key] = value
        for source, target in (
            ("total_cost_usd", "cost_usd"),
            ("duration_ms", "duration_ms"),
            ("duration_api_ms", "api_duration_ms"),
            ("num_turns", "turns"),
        ):
            value = candidate.get(source)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                metrics[target] = value
    return metrics


def is_rate_limited(text: str) -> bool:
    return any(pattern.search(text) for pattern in RATE_LIMIT_PATTERNS)


def configured_retry_exit_codes(provider: str, config: dict[str, Any]) -> set[int]:
    provider_cfg = config.get(provider, {})
    raw = provider_cfg.get("retry_exit_codes", []) if isinstance(provider_cfg, dict) else []
    if not isinstance(raw, list) or any(isinstance(item, bool) or not isinstance(item, int) for item in raw):
        raise RunnerError(f"{provider}.retry_exit_codes must be a list of integers")
    return set(raw)


def is_provider_availability_failure(
    provider: str,
    return_code: int,
    text: str,
    config: dict[str, Any],
) -> bool:
    return return_code in configured_retry_exit_codes(provider, config) or is_rate_limited(text)


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


def _file_fingerprint(repo_root: Path, relative: str) -> str:
    path = repo_root / relative
    try:
        if path.is_symlink():
            return "symlink:" + os.readlink(path)
        if not path.exists():
            return "missing"
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return "sha256:" + digest.hexdigest()
    except OSError as exc:
        return f"error:{type(exc).__name__}"


def git_change_snapshot(repo_root: Path) -> dict[str, str]:
    """Fingerprint dirty paths so one attempt is not credited with older work."""
    return {
        relative: _file_fingerprint(repo_root, relative)
        for relative in git_changed_files(repo_root)
    }


def files_changed_since(repo_root: Path, before: dict[str, str]) -> list[str]:
    after = git_change_snapshot(repo_root)
    return sorted(
        relative
        for relative in set(before) | set(after)
        if before.get(relative) != after.get(relative)
    )


def release_interrupted_task(plan_dir: Path, manifest: dict[str, Any], task_id: str) -> None:
    # Subtask checkpoints are written by child planctl processes while the
    # provider is running. Always reload before applying an interruption so a
    # stale parent snapshot cannot erase completed child checkpoints.
    refresh_manifest(plan_dir, manifest)
    task = planctl.find_task(manifest, task_id)
    if task.get("status") == "in_progress":
        recovered_subtasks = planctl.recover_in_progress_subtasks(
            task, "Execution interrupted; safe to resume."
        )
        task["status"] = "pending"
        task["last_error"] = "Execution interrupted; safe to resume."
        task["history"].append(
            {
                "at": planctl.now_utc(),
                "event": "interrupted",
                "recovered_subtasks": recovered_subtasks,
            }
        )
        planctl.append_event(
            manifest,
            "task_interrupted",
            task_id=task["id"],
            recovered_subtasks=recovered_subtasks,
        )
        planctl.save_manifest(plan_dir, manifest)


def deferred_retry_at(config: dict[str, Any], cycle: int) -> str:
    rate_cfg = config.get("rate_limit", {})
    base = max(1, int(rate_cfg.get("wait_seconds", 300)))
    seconds = min(base * (2 ** min(cycle, 4)), 3600)
    jitter_ratio = max(0.0, min(float(rate_cfg.get("jitter_ratio", 0.1)), 0.5))
    seconds += random.uniform(0, seconds * jitter_ratio)
    retry_at = dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=seconds)
    return retry_at.replace(microsecond=0).isoformat()


def seconds_until(timestamp: str) -> float:
    try:
        target = dt.datetime.fromisoformat(timestamp)
    except ValueError:
        return 0.0
    if target.tzinfo is None:
        target = target.replace(tzinfo=dt.timezone.utc)
    return max(0.0, (target - dt.datetime.now(dt.timezone.utc)).total_seconds())


def deferred_tasks(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        task
        for task in manifest.get("tasks", [])
        if task.get("status") == "pending" and task.get("deferred_until")
    ]


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
    while True:
        route = choose_route(task, config, provider_override)
        capabilities = probe_provider(route["provider"], config)
        if not dry_run:
            record_provider_capabilities(plan_dir, manifest, route["provider"], capabilities)
        if route["provider"] == "claude":
            config["claude"]["_supports_exclude_dynamic_system_prompt_sections"] = (
                "exclude_dynamic_system_prompt_sections" in capabilities.get("features", [])
            )
        result_path = normalized_result_file(plan_dir, task, route)
        prompt = worker_prompt(plan_dir, manifest, task, route)
        command = build_worker_command(route["provider"], route, config, prompt, result_path)
        if dry_run:
            print(json.dumps({"task": task["id"], "route": route, "capabilities": capabilities, "command": redact_command(command)}, indent=2))
            return False

        print(
            f"[task {task['id']}] {task['title']} — {route['provider']} / {route['model']} / {route['effort']}",
            flush=True,
        )
        before_changes = git_change_snapshot(repo_root)
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
        # Child checkpoint commands may have advanced the plan while the
        # provider was running. Never apply a result to the pre-launch copy.
        refresh_manifest(plan_dir, manifest)
        task = planctl.find_task(manifest, task["id"])
        metrics = provider_metrics(route["provider"], stdout)
        metrics.update({"model": route["model"], "effort": route["effort"], "attempt": attempt_number})
        task["last_attempt_metrics"] = metrics
        if return_code != 0 and classify_provider_failure(
            route["provider"], return_code, stderr, stdout, config
        ) == "availability":
            retry_at = deferred_retry_at(config, int(task.get("rate_limit_events", 0)))
            planctl.fail_task(
                plan_dir,
                manifest,
                task["id"],
                f"Provider rate/usage limit (exit {return_code}): {output_tail(combined)}",
                rate_limited=True,
                failure_kind="availability",
                deferred_until=retry_at,
            )
            print(
                f"[availability] Task {task['id']} deferred until {retry_at}; runner lease will be released.",
                file=sys.stderr,
            )
            return False

        report = parse_provider_report(route["provider"], stdout, result_path)
        if return_code != 0:
            failure_kind = classify_provider_failure(
                route["provider"], return_code, stderr, stdout, config
            )
            reason = f"Provider exited with {return_code}: {output_tail(combined)}"
            planctl.fail_task(
                plan_dir,
                manifest,
                task["id"],
                reason,
                failure_kind=failure_kind,
                block=failure_kind == "environment",
            )
            action = "blocked for environment repair" if failure_kind == "environment" else "route will escalate on retry"
            print(f"[task {task['id']}] {failure_kind} failure; {action}", file=sys.stderr)
            return False
        if not report:
            reason = f"Provider returned no valid completion report. Output: {output_tail(combined)}"
            planctl.fail_task(
                plan_dir, manifest, task["id"], reason, failure_kind="contract", block=True
            )
            print(f"[task {task['id']}] invalid report; blocked without model escalation", file=sys.stderr)
            return False
        expected_context_files = list(task.get("context_files", []))
        reported_context_files = report.get("context_files_read")
        if reported_context_files != expected_context_files:
            reason = (
                "Worker context report mismatch: expected "
                f"{expected_context_files!r}, received {reported_context_files!r}"
            )
            planctl.fail_task(
                plan_dir, manifest, task["id"], reason, failure_kind="contract", block=True
            )
            print(f"[task {task['id']}] context assignment was not acknowledged", file=sys.stderr)
            return False
        expected_learning_files = list(task.get("learning_files", []))
        reported_learning_files = report.get("learning_files_read")
        if reported_learning_files != expected_learning_files:
            reason = (
                "Worker learning report mismatch: expected "
                f"{expected_learning_files!r}, received {reported_learning_files!r}"
            )
            planctl.fail_task(
                plan_dir, manifest, task["id"], reason, failure_kind="contract", block=True
            )
            print(f"[task {task['id']}] learning assignment was not acknowledged", file=sys.stderr)
            return False
        if report.get("status") != "completed":
            reason = str(report.get("blocked_reason") or report.get("summary") or "Worker reported blocked")
            if is_rate_limited(reason):
                retry_at = deferred_retry_at(config, int(task.get("rate_limit_events", 0)))
                planctl.fail_task(
                    plan_dir,
                    manifest,
                    task["id"],
                    reason,
                    rate_limited=True,
                    failure_kind="availability",
                    deferred_until=retry_at,
                )
                print(f"[availability] Task {task['id']} deferred until {retry_at}.", file=sys.stderr)
                return False
            planctl.fail_task(plan_dir, manifest, task["id"], reason, failure_kind="capability")
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
        report["changed_files"] = files_changed_since(repo_root, before_changes)
        report["runtime_metrics"] = metrics
        if not passed:
            report["orchestrator_status"] = "validation_failed"
            planctl.atomic_write_json(result_path, report)
            planctl.fail_task(
                plan_dir,
                manifest,
                task["id"],
                validation_reason or "Validation failed",
                failure_kind="validation",
            )
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
        ]
        command.extend(configured_model_args("--model", route["model"]))
        command.extend(["--effort", route["effort"]])
        command.extend(extra_args)
        command.append(prompt)
        return command
    if provider == "codex":
        command = prefix + [
            "exec",
            "--ephemeral",
            "--sandbox",
            "read-only",
        ]
        command.extend(configured_model_args("--model", route["model"]))
        command.extend(
            [
                "-c",
                f'model_reasoning_effort="{route["effort"]}"',
                "--output-last-message",
                str(output_path),
            ]
        )
        if provider_cfg.get("ignore_user_config"):
            command.append("--ignore-user-config")
        command.extend(extra_args)
        command.append(prompt)
        return command
    if provider == "gemini":
        command = prefix + [
            "--approval-mode",
            str(provider_cfg.get("summary_approval_mode", "default")),
            "--output-format",
            "json",
        ]
        if provider_cfg.get("disable_extensions", True):
            command.extend(["--extensions", "none"])
        command.extend(configured_model_args("--model", route["model"]))
        command.extend(extra_args)
        command.extend(["--prompt", prompt])
        return command
    if provider == "qwen":
        command = prefix
        if provider_cfg.get("safe_mode", True):
            command.append("--safe-mode")
        command.extend([
            "--approval-mode",
            "plan",
            "--output-format",
            "json",
        ])
        command.extend(configured_model_args("--model", route["model"]))
        command.extend(extra_args)
        command.extend(["--prompt", prompt])
        return command
    if provider == "kimi":
        command = prefix + [
            "--output-format",
            "stream-json",
        ]
        permission_mode = str(
            provider_cfg.get("summary_permission_mode", "plan")
        ).strip()
        if permission_mode:
            if permission_mode not in {"auto", "plan", "yolo"}:
                raise RunnerError(
                    "kimi.summary_permission_mode must be auto, plan, yolo, or an empty string"
                )
            command.append(f"--{permission_mode}")
        command.extend(configured_model_args("--model", route["model"]))
        command.extend(extra_args)
        command.extend(["--prompt", prompt])
        return command
    if provider == "trae":
        trajectory_path = output_path.parent / "logs" / "final-summary-trae-trajectory.json"
        command = prefix + [
            "run",
            prompt,
            "--working-dir",
            ".",
            "--trajectory-file",
            str(trajectory_path),
        ]
        model_provider = str(provider_cfg.get("model_provider", "")).strip()
        if model_provider:
            command.extend(["--provider", model_provider])
        command.extend(configured_model_args("--model", route["model"]))
        command.extend(extra_args)
        return command
    raise RunnerError(f"Unsupported summary provider adapter: {provider}")


def extract_text_output(value: Any) -> str:
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return ""
        if text.startswith(("{", "[")):
            try:
                nested = json.loads(text)
            except json.JSONDecodeError:
                return text
            found = extract_text_output(nested)
            return found or text
        return text
    if isinstance(value, list):
        for item in reversed(value):
            found = extract_text_output(item)
            if found:
                return found
        return ""
    if isinstance(value, dict):
        for key in (
            "response",
            "result",
            "final_message",
            "final_output",
            "answer",
            "content",
            "message",
            "output",
            "text",
        ):
            if key in value:
                found = extract_text_output(value[key])
                if found:
                    return found
        for nested in reversed(list(value.values())):
            found = extract_text_output(nested)
            if found:
                return found
    return ""


def summary_stdout_text(provider: str, stdout: str, output_path: Path) -> str:
    if provider == "codex":
        return output_path.read_text(encoding="utf-8").strip() if output_path.is_file() else ""
    if not stdout.strip():
        return ""
    try:
        return extract_text_output(json.loads(stdout))
    except json.JSONDecodeError:
        for line in reversed(stdout.splitlines()):
            candidate = line.strip()
            if not candidate:
                continue
            try:
                found = extract_text_output(json.loads(candidate))
            except json.JSONDecodeError:
                continue
            if found:
                return found
        return stdout.strip()


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
    try:
        route = summary_route(config)
    except RunnerError:
        fallback = planctl.deterministic_summary(manifest)
        planctl.atomic_write_text(output_path, fallback)
        return fallback, output_path.relative_to(plan_dir).as_posix()

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
    if return_code == 0:
        summary = summary_stdout_text(route["provider"], stdout, output_path)
        if summary and route["provider"] != "codex":
            planctl.atomic_write_text(output_path, summary + "\n")
        if summary:
            return summary + "\n", output_path.relative_to(plan_dir).as_posix()
    # Summary generation is optional presentation work. Never hold a completed
    # plan open or spend stronger-model retries when the deterministic summary
    # already contains the authoritative result.
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
            completed = execute_one_task(
                plan_dir,
                manifest,
                config,
                task,
                provider_override=args.provider,
                dry_run=False,
                no_wait=args.no_wait,
            )
            if completed:
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
    waiting = deferred_tasks(manifest)
    if waiting:
        earliest = min(str(task["deferred_until"]) for task in waiting)
        print(
            f"Provider availability deferred {len(waiting)} task(s); next retry at {earliest}.",
            file=sys.stderr,
        )
        return DEFERRED_EXIT_CODE
    if completed_this_run == 0:
        print("No runnable task. Check dependencies and task states.", file=sys.stderr)
        print(planctl.render_todo(manifest), end="", file=sys.stderr)
        return 3
    return 0



def run_plan(args: argparse.Namespace) -> int:
    """Run or resume a plan under an atomic lease."""
    plan_dir, _ = planctl.load_plan(args.plan)
    lifecyclectl.activate_plan(plan_dir)
    with lifecyclectl.runner_lease(plan_dir, force=bool(getattr(args, "takeover", False))):
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
    parser.add_argument(
        "--provider",
        choices=sorted(planctl.VALID_PROVIDERS - {"auto"}),
        help="Override task provider",
    )
    parser.add_argument("--once", action="store_true", help="Execute at most one task")
    parser.add_argument("--dry-run", action="store_true", help="Print the next provider command without executing")
    parser.add_argument("--no-wait", action="store_true", help="Do not wait and retry on rate/usage limits")
    parser.add_argument(
        "--takeover",
        action="store_true",
        help="Fence an older runner lease and take over with the selected provider",
    )
    parser.add_argument("--no-cleanup", action="store_true", help="Keep planning artifacts after success")
    return parser


def main() -> int:
    install_signal_handlers()
    args = build_parser().parse_args()
    try:
        wait_cycle = 0
        while True:
            result = run_plan(args)
            if result != DEFERRED_EXIT_CODE or args.no_wait:
                return result
            plan_dir, manifest = planctl.load_plan(args.plan)
            config = load_config(plan_dir)
            rate_cfg = config.get("rate_limit", {})
            if not rate_cfg.get("auto_wait", True):
                return result
            max_cycles = int(rate_cfg.get("max_wait_cycles", 0))
            if max_cycles > 0 and wait_cycle >= max_cycles:
                return result
            waiting = deferred_tasks(manifest)
            if not waiting:
                continue
            retry_at = min(str(task["deferred_until"]) for task in waiting)
            delay = seconds_until(retry_at)
            print(
                f"[supervisor] Retrying in {int(delay)} seconds. The runner lease is free; "
                "another provider may take over safely.",
                flush=True,
            )
            try:
                time.sleep(delay)
            except KeyboardInterrupt:
                print("\nDeferred retry stopped; the plan remains resumable.", file=sys.stderr)
                return 130
            wait_cycle += 1
    except (planctl.PlanError, RunnerError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
