#!/usr/bin/env python3
"""Execute plan-and-execute tasks in fresh supported coding-agent processes.

Each provider call starts a new, non-persistent session. The only planning file
named in the worker prompt is the current task definition. State, retries,
validation, escalation, summarization, and cleanup are handled by this script.
"""

from __future__ import annotations

import argparse
import hashlib
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
import resource_watch  # noqa: E402
import lifecyclectl  # noqa: E402
import routingctl  # noqa: E402
import routing_config  # noqa: E402
import availability  # noqa: E402
import assistant_triage  # noqa: E402
import process_tree  # noqa: E402
import model_catalogctl  # noqa: E402
import routing_telemetry  # noqa: E402

TIER_ORDER = routingctl.TIER_ORDER
EFFORT_ORDER = routingctl.EFFORT_ORDER
MUSE_TRUST_WORKSPACE_FLAG = "--trust-workspace"
MUSE_DISABLE_APPROVAL_FLAG = "--disable-approval"
MUSE_READ_ONLY_FLAG = "--disable-write"
MUSE_WRITE_FLAGS = frozenset({MUSE_TRUST_WORKSPACE_FLAG, MUSE_DISABLE_APPROVAL_FLAG})
DESIGN_NOTE_MAX_CHARS = 6000
VALIDATION_FAILURE_CONTEXT_CHARS = 900
BUDGET_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        # Claude Code result envelope: {"type":"result","subtype":"error_max_turns"|
        # "error_max_budget_usd","is_error":true,...} — confirmed literal subtypes.
        r"error_max_turns",
        r"error_max_budget",
        r"max[ _-]?turns",
        r"maximum number of turns",
        r"turn limit",
        r"budget limit",
        # Codex rollout-budget enforcement (openai/codex#28707) aborts the turn
        # through an internal TurnAborted result; the exact surfaced wording is
        # not publicly documented, so match broadly and accept that an unmatched
        # phrasing falls back to "unknown" (safe: +1 rung) rather than "budget".
        r"rollout[ _-]?budget",
        r"turn[ _-]?abort",
        r"token budget (?:exceeded|exhausted|reached)",
        r"budget (?:exceeded|exhausted|reached)",
    )
]
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


def claude_bare_flags() -> list[str]:
    """Return `--bare` only when API-key credentials exist; bare mode rejects subscription OAuth logins."""
    return ["--bare"] if os.environ.get("ANTHROPIC_API_KEY") else []


def _plan_relative_files(files: Any, plan_dir: Path, task_file: Any = None) -> Any:
    """Normalize assigned-file names so repository-relative and plan-relative spellings compare equal.

    The task's own definition file is always read first, so it is never counted as an extra assignment.
    """
    if not isinstance(files, list):
        return files
    marker = plan_dir.name + "/"
    names = [item.split(marker, 1)[1] if isinstance(item, str) and marker in item else item for item in files]
    own = Path(str(task_file)).name if task_file else None
    return [item for item in names if not (own and isinstance(item, str) and Path(item).name == own)]


def _plan_context_files(files: Any, plan_dir: Path, expected: list[str], task_file: Any = None) -> Any:
    """Keep only plan context artifacts so extra repository reads never count as an assignment mismatch.

    Workers routinely list runbooks, docs, patterns and the service map next to their assigned context;
    only `CONTEXT.md`, `contexts/*` and the assigned names themselves are governed by the assignment check.
    The result is an ordered set: order and repeats are not part of the assignment.
    """
    if not isinstance(files, list):
        return files
    slashed = [item.replace("\\", "/") if isinstance(item, str) else item for item in files]
    names = _plan_relative_files(slashed, plan_dir, task_file)
    return sorted(
        {
            item
            for item in names
            if isinstance(item, str) and (item in expected or item == "CONTEXT.md" or item.startswith("contexts/"))
        }
    )


def refresh_manifest(plan_dir: Path, manifest: dict[str, Any]) -> None:
    """Re-read the manifest in place after a long-running worker.

    The worker checkpoints subtasks through the controller CLI and the operator may edit the plan meanwhile;
    saving the runner's older in-memory copy would silently discard both (a lost update).
    """
    fresh = planctl.read_json(plan_dir / planctl.MANIFEST)
    current = {item["id"]: item for item in manifest.get("tasks", [])}
    tasks: list[dict[str, Any]] = []
    for incoming in fresh.get("tasks", []):
        # Refresh each task dict in place: callers keep references to the task they are executing.
        existing = current.get(incoming["id"])
        if existing is None:
            tasks.append(incoming)
            continue
        existing.clear()
        existing.update(incoming)
        tasks.append(existing)
    fresh["tasks"] = tasks
    manifest.clear()
    manifest.update(fresh)


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
    try:
        return routing_config.load(planctl.default_config(), plan_dir / planctl.CONFIG)
    except routing_config.ConfigError as exc:
        raise RunnerError(str(exc)) from exc


def resolve_windows_shim(parts: list[str]) -> list[str]:
    """CreateProcess cannot launch npm-style `.cmd`/`.bat` shims (claude, codex, agy)
    by bare name; resolve them through PATH/PATHEXT so Popen gets the real file."""
    if os.name != "nt" or not parts:
        return parts
    first = parts[0]
    if os.path.sep in first or (os.path.altsep and os.path.altsep in first):
        return parts
    resolved = shutil.which(first)
    if resolved:
        return [resolved, *parts[1:]]
    return parts


def command_prefix(value: Any) -> list[str]:
    if isinstance(value, list) and value and all(isinstance(item, str) and item.strip() for item in value):
        return resolve_windows_shim(list(value))
    if isinstance(value, str) and value.strip():
        text = value.strip()
        if os.name != "nt":
            return shlex.split(text)
        # POSIX shlex strips backslashes from Windows paths; keep them and only
        # unwrap surrounding quotes.
        parts = shlex.split(text, posix=False)
        cleaned: list[str] = []
        for part in parts:
            if len(part) >= 2 and part[0] == part[-1] and part[0] in ("'", '"'):
                part = part[1:-1]
            cleaned.append(part)
        return resolve_windows_shim(cleaned)
    raise RunnerError(f"Invalid provider command: {value!r}")


def provider_profile(provider: str, config: dict[str, Any]) -> dict[str, Any]:
    try:
        return routing_config.resolve_profile(provider, config)
    except routing_config.ConfigError as exc:
        raise RunnerError(str(exc)) from exc


def provider_prefix(provider: str, config: dict[str, Any]) -> list[str]:
    return command_prefix(provider_profile(provider, config)["command"])


def spawn_env(provider: str, config: dict[str, Any], environ: Any = None) -> dict[str, str] | None:
    """Child env for a profile with credential references, read now (at spawn) and never persisted.

    Returns None (inherit unchanged) when the profile names no variables. Errors name the
    variable, never its value.
    """
    profile = provider_profile(provider, config)
    environ = os.environ if environ is None else environ
    targets = routing_config.HARNESS_ENV[profile["harness"]]
    overlay: dict[str, str] = {}
    for key in ("base_url_env", "token_env"):
        source = profile.get(key)
        if not source:
            continue
        value = environ.get(source)
        if not value:
            raise RunnerError(f"Profile {profile['name']} requires environment variable {source}")
        # `native` harnesses read their own variables; the check above only proves presence.
        if key in targets:
            overlay[targets[key]] = value
    if not profile.get("base_url_env") and not profile.get("token_env"):
        return None
    return {**environ, **overlay}


def antigravity_print_timeout(provider_cfg: dict[str, Any], config: dict[str, Any]) -> str:
    """agy kills a print-mode run after `--print-timeout` (default 5m).

    An explicit `antigravity.print_timeout` wins; otherwise follow the runner's
    `task_timeout_seconds` so the two limits never disagree, and fall back to a
    long window when the runner imposes no limit.
    """
    configured = str(provider_cfg.get("print_timeout", "") or "").strip()
    if configured and configured.lower() != "auto":
        return configured
    task_timeout = int(config.get("task_timeout_seconds", 0) or 0)
    return f"{task_timeout}s" if task_timeout > 0 else "12h"


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
    try:
        providers = routing_config.provider_chain(task, config, override)
    except routing_config.ConfigError as exc:
        raise RunnerError(str(exc)) from exc

    available: list[str] = []
    for provider in providers:
        prefix = provider_prefix(provider, config)
        if executable_available(prefix):
            available.append(provider)
    if not available:
        requested_text = requested if requested != "auto" else ", ".join(providers)
        raise RunnerError(f"No usable provider CLI found for: {requested_text}")
    return available


def choose_route(task: dict[str, Any], config: dict[str, Any], override: str | None, *, check_availability: bool = True) -> dict[str, str]:
    providers = (candidate_providers(task, config, override) if check_availability
                 else routing_config.provider_chain(task, config, override))
    failures_per_provider = max(1, int(config.get("functional_failures_per_provider", 4)))
    failures = int(task.get("functional_failures", 0))
    provider_slot = failures // failures_per_provider
    provider_index = min(provider_slot, len(providers) - 1)
    provider = providers[provider_index]

    provider_cfg = config[provider]
    rungs = routingctl.route_rungs(
        provider_cfg,
        str(task.get("model_tier", "standard")),
        str(task.get("reasoning_effort", "medium")),
    )
    # Failure evidence decides the rung (see routingctl.escalation_step). The
    # classes accumulate across providers, so a provider switch is a second
    # opinion at the equivalent logical rung, not a reset to the cheapest one.
    # Legacy manifests without recorded classes count one rung per failure.
    classes = task.get("failure_classes")
    if not isinstance(classes, list):
        classes = ["unknown"] * failures
    ladder_step = routingctl.escalation_step(classes, rungs)
    stagnation = task.get("validation_stagnation")
    if isinstance(stagnation, dict) and stagnation.get("triggered") is True:
        current = task.get("current_route") if isinstance(task.get("current_route"), dict) else {}
        current_tier = str(current.get("tier") or task.get("model_tier", "standard"))
        floor_tier = "max" if current_tier in {"strong", "max"} else "strong"
        floor_rank = TIER_ORDER.index(floor_tier)
        floor_step = next(
            (
                index for index, (candidate_tier, candidate_effort) in enumerate(rungs)
                if TIER_ORDER.index(candidate_tier) >= floor_rank
                and EFFORT_ORDER.index(candidate_effort) >= EFFORT_ORDER.index("medium")
            ),
            len(rungs) - 1,
        )
        ladder_step = max(ladder_step, floor_step)
    tier, effort = rungs[min(ladder_step, len(rungs) - 1)]
    requested_effort = effort
    effort = clamp_effort(provider_cfg, tier, effort)
    models = provider_cfg.get("models", {})
    model = str(models.get(tier, "")).strip()
    if not model:
        raise RunnerError(f"No model configured for {provider}/{tier}")
    return {"provider": provider, "tier": tier, "model": model, "effort": effort, "requested_effort": requested_effort}


# Plan snapshot resolution stays opt-in until the rollout gate. The config
# ladder still picks provider, tier and effort; `model_resolution: "snapshot"`
# only binds the concrete model id from the plan's MODEL_MATRIX.json, falling
# back to the configured ladder model when the snapshot has no entry. The
# snapshot path and catalog economics never reach the worker prompt.
INVALID_MODEL = re.compile(
    r"invalid model|unknown model|model[^\n]{0,80}(?:not found|does not exist|not available|not supported)", re.I
)


def snapshot_resolution(config: dict[str, Any]) -> bool:
    return config.get("model_resolution", "config") == "snapshot"


def resolve_snapshot_route(
    plan_dir: Path,
    task: dict[str, Any],
    route: dict[str, str],
    config: dict[str, Any],
    catalog_models: dict[str, dict[str, str]] | None = None,
) -> dict[str, str]:
    if not snapshot_resolution(config):
        return route
    matrix, _warning = model_catalogctl.load_matrix(plan_dir)
    provider, tier = route["provider"], route["tier"]
    current = task.get("current_route")
    if (task.get("status") == "in_progress" and isinstance(current, dict)
            and current.get("provider") == provider and current.get("tier") == tier and current.get("model")):
        return {**route, "model": str(current["model"])}
    if matrix is not None:
        # The task binding wins: refresh rebases pending tasks only, so an
        # in-progress binding keeps the model of the snapshot it started with.
        for candidate in matrix.get("tasks", {}).get(task["id"], {}).get("candidates", []):
            if candidate.get("provider") == provider and candidate.get("tier") == tier:
                return {**route, "model": candidate["model"]}
        model = matrix.get("tiers", {}).get(tier, {}).get(provider)
        if model:
            return {**route, "model": model}
    model = (catalog_models or {}).get(provider, {}).get(tier)
    return {**route, "model": model} if model else route


# Shadow routing stays observational until the rollout gate. With
# `routing_shadow: true` the runner asks the deterministic selector
# (routingctl.select_route) for a candidate next to each executed route and
# records both, with the selector's explanation, as plan-scoped telemetry
# (PAT004). The candidate never changes provider, model, effort or argv and
# never reaches the worker prompt.
SHADOW_RELATIVE = "telemetry/shadow.jsonl"
SHADOW_ROUTE_KEYS = ("provider", "model", "tier", "effort")


def auto_select_mode(config: dict[str, Any]) -> str:
    routing = config.get("routing")
    mode = routing.get("auto_select", "off") if isinstance(routing, dict) else "off"
    return mode if mode in routing_config.AUTO_SELECT_MODES else "off"


def shadow_enabled(config: dict[str, Any]) -> bool:
    return config.get("routing_shadow") is True or auto_select_mode(config) in ("shadow", "on")


def shadow_catalog_providers(providers: list[str], config: dict[str, Any]) -> list[str]:
    """Catalog provider ids for a config chain: a profile named after a catalog provider (glm, deepseek) wins."""
    import model_catalog

    known = model_catalog.BOOTSTRAP_CATALOG["providers"]
    out: list[str] = []
    for provider in providers:
        profile = (config.get(provider) or {}).get("profile")
        name = profile if isinstance(profile, str) and profile in known else provider
        if name not in out:
            out.append(name)
    return out


def shadow_candidate(
    task: dict[str, Any], route: dict[str, str], config: dict[str, Any], override: str | None = None,
    *, phase: str = "implementation",
) -> dict[str, Any]:
    """Pure: the selector's candidate for the task's declared route; never raises."""
    record: dict[str, Any] = {
        "task_id": str(task.get("id")) if task.get("id") is not None else None,
        "phase": phase,
        "executed": {key: route.get(key) for key in SHADOW_ROUTE_KEYS},
        "candidate": None,
        "decision": "error",
    }
    try:
        providers = shadow_catalog_providers(routing_config.provider_chain(task, config, override), config)
        request: dict[str, Any] = {"providers": providers}
        signals = task.get("routing_signals")
        if isinstance(signals, list) and signals:
            # Declared signals give the selector its own floor; otherwise it starts at the declared route.
            request["signals"] = [str(item) for item in signals]
        else:
            request["route"] = {"tier": routingctl.normalize_tier(task.get("model_tier", "standard")),
                                "effort": str(task.get("reasoning_effort", "medium"))}
        capabilities = task.get("required_capabilities")
        if isinstance(capabilities, list) and capabilities:
            request["required_capabilities"] = sorted(str(item) for item in capabilities)
        selection = routingctl.select_route(request)
    except Exception as exc:  # noqa: BLE001 - shadow must not stop execution
        record["error"] = type(exc).__name__
        return record
    chosen = selection.get("route")
    explanation = selection.get("explanation") or {}
    record.update(
        decision=selection.get("decision"),
        floor=selection.get("floor"),
        candidate={key: chosen.get(key) for key in SHADOW_ROUTE_KEYS} if chosen else None,
        explanation={
            "catalog_version": explanation.get("catalog_version"),
            "providers": explanation.get("providers"),
            "target_tier": explanation.get("target_tier"),
            "tier_lifted": explanation.get("tier_lifted"),
            "stages": [{"stage": stage.get("stage"), "kept": len(stage.get("kept", [])),
                        "dropped": sorted({item.get("reason") for item in stage.get("dropped", [])})}
                       for stage in explanation.get("stages", [])],
            "sticky": (selection.get("sticky") or {}).get("reason"),
        },
    )
    return record


def record_shadow(plan_dir: Path, record: dict[str, Any], repo_root: Path | None = None) -> bool:
    """Append one shadow record; failure never interrupts execution."""
    path = Path(plan_dir) / SHADOW_RELATIVE
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if repo_root is not None and not path.exists():
            import resource_watch
            resource_watch.register_artifact(Path(repo_root), path, "plan", Path(plan_dir).name, "keep")
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
        return True
    except Exception as exc:  # noqa: BLE001 - shadow telemetry is best-effort
        print(f"[shadow] not recorded: {type(exc).__name__}", file=sys.stderr)
        return False


# Conservative rollout: `routing.auto_select: on` applies the shadow candidate
# only for a task whose `routing_segment` is both in `routing.allowlist` and
# passing every predeclared gate (routingctl.load_gate over `routing.gate_dir`).
# Only a first implementation attempt on the provider the ladder already chose
# is eligible; retries stay on the evidence ladder. Any other case, including a
# selector exception, keeps the ladder route and records why.
DEFAULT_GATE_DIR = "docs/research/routing-eval"


def auto_route(
    plan_dir: Path,
    repo_root: Path,
    task: dict[str, Any],
    route: dict[str, str],
    config: dict[str, Any],
    shadow: dict[str, Any],
    *,
    phase: str = "implementation",
    catalog_models: dict[str, dict[str, str]] | None = None,
) -> tuple[dict[str, str], dict[str, Any]]:
    """Return (route, decision); the ladder route on any failed condition or error."""
    segment = task.get("routing_segment")
    decision: dict[str, Any] = {"mode": "on", "segment": segment if isinstance(segment, str) else None,
                                "applied": False, "reason": None, "allowlist": []}
    try:
        routing = config.get("routing") or {}
        gate_dir = Path(str(routing.get("gate_dir") or DEFAULT_GATE_DIR))
        requested = routing.get("allowlist") or []
        gate = routingctl.load_gate(gate_dir if gate_dir.is_absolute() else Path(repo_root) / gate_dir) if requested else {}
        allowlist = routingctl.effective_allowlist(requested, gate)
        decision["allowlist"] = allowlist
        if gate.get("error"):
            decision["gate_error"] = gate["error"]
        candidate = shadow.get("candidate")
        if not isinstance(segment, str) or segment not in allowlist:
            decision["reason"] = "segment_not_allowlisted"
        elif phase != "implementation":
            decision["reason"] = "design_phase"
        elif int(task.get("attempts") or 0) > 0 or task.get("functional_failures") or task.get("failure_classes"):
            decision["reason"] = "ladder_owns_retry"
        elif shadow.get("decision") == "error":
            decision.update(reason="selector_error", error=shadow.get("error"))
        elif shadow.get("decision") != "route" or not isinstance(candidate, dict):
            decision["reason"] = "no_candidate"
        elif candidate.get("provider") not in shadow_catalog_providers([route["provider"]], config):
            decision["reason"] = "provider_differs"
        else:
            provider_cfg = config[route["provider"]]
            tier = routingctl.normalize_tier(candidate["tier"])
            model = str(provider_cfg.get("models", {}).get(tier, "")).strip()
            if not model:
                decision["reason"] = "no_configured_model"
            else:
                requested_effort = str(candidate["effort"])
                selected = {**route, "tier": tier, "model": model,
                            "effort": clamp_effort(provider_cfg, tier, requested_effort),
                            "requested_effort": requested_effort}
                selected = resolve_snapshot_route(plan_dir, task, selected, config, catalog_models)
                decision.update(applied=True, reason="gate_passed")
                return selected, decision
    except Exception as exc:  # noqa: BLE001 - auto-routing falls back to the ladder
        decision.update(applied=False, reason="selector_error", error=type(exc).__name__)
    return route, decision


def resume_provider_models(
    plan_dir: Path, config: dict[str, Any], override: str | None, store: Any = None
) -> dict[str, dict[str, str]]:
    """HD002: `--provider X` absent from the snapshot resolves only from a fresh shared catalog.

    A fresh catalog is used in memory and recorded as a snapshot audit entry;
    a stale or missing one fails with refresh guidance. TODOs are never rewritten.
    """
    if not override or not snapshot_resolution(config):
        return {}
    matrix, _warning = model_catalogctl.load_matrix(plan_dir)
    if matrix is None or override in matrix["catalog"].get("providers", {}):
        return {}
    store = store or model_catalogctl.CatalogStore()
    record, _note = store.load(override)
    state = "missing"
    if record is not None:
        state = model_catalogctl.facet_states(record, store.now(), store.policy)["capability"]
    if state != "fresh":
        raise RunnerError(
            f"Provider {override} is not in this plan's MODEL_MATRIX snapshot and its shared catalog is {state}. "
            f"Run `model_catalogctl.py refresh --provider {override}` and then "
            f"`model_catalogctl.py refresh --plan {plan_dir}` before resuming; TODOs were not changed."
        )
    catalog, _notes = model_catalogctl.merged_catalog(store, override)
    models = model_catalogctl.mc.provider_config_mapping(override, catalog)["models"]
    model_catalogctl._audit(matrix, {
        "at": model_catalogctl._iso(store.now()), "op": "resume_provider", "provider": override,
        "old_digest": matrix["catalog_digest"], "new_digest": matrix["catalog_digest"],
        "provider_catalog_digest": model_catalogctl.mc.digest(catalog),
        "provider_catalog_version": record["catalog_version"],
    })
    model_catalogctl.write_matrix(plan_dir, matrix)
    return {override: models}


def stale_snapshot_warning(plan_dir: Path, now: Any = None) -> str | None:
    """Non-blocking resume warning for a snapshot older than its threshold."""
    matrix, _warning = model_catalogctl.load_matrix(plan_dir)
    if matrix is None:
        return None
    now = now or model_catalogctl._utc_now()
    age_days = (now - model_catalogctl.mc._parse_time(matrix["captured_at"])).total_seconds() / 86400
    if age_days <= matrix["stale_after_days"]:
        return None
    return (f"MODEL_MATRIX snapshot is {age_days:.1f} days old (threshold {matrix['stale_after_days']}); "
            "run `model_catalogctl.py diff --plan` / `refresh --plan` (non-blocking)")


def refresh_model_snapshot(plan_dir: Path, provider: str) -> None:
    """One-shot refresh after a confirmed invalid model id; never raises."""
    store = model_catalogctl.CatalogStore()
    try:
        model_catalogctl.refresh(store, provider, {}, version_fn=model_catalogctl.probe_cli_version, force=True)
        model_catalogctl.matrix_refresh(store, plan_dir)
    except (model_catalogctl.CacheError, OSError, ValueError) as exc:
        print(f"[model-refresh] {provider}: {str(exc)[:200]}", file=sys.stderr)


def release_for_model_refresh(plan_dir: Path, manifest: dict[str, Any], task_id: str, reason: str) -> None:
    """Return the claimed attempt to pending without recording failure evidence."""
    task = planctl.find_task(manifest, task_id)
    if task.get("status") != "in_progress":
        return
    recovered = planctl.recover_in_progress_subtasks(task, reason)
    task["status"] = "pending"
    task["last_error"] = planctl.bounded_failure_reason(reason)
    task["history"].append({"at": planctl.now_utc(), "event": "model_refresh", "recovered_subtasks": recovered})
    planctl.append_event(manifest, "task_model_refresh", task_id=task["id"])
    planctl.save_manifest(plan_dir, manifest)


def completion_schema_path() -> Path:
    path = SKILL_DIR / "references" / "completion-report.schema.json"
    if not path.is_file():
        raise RunnerError(f"Completion schema not found: {path}")
    return path


# Keywords the OpenAI structured-output validator rejects (`codex exec
# --output-schema` fails with `invalid_json_schema` before the worker starts).
CODEX_UNSUPPORTED_SCHEMA_KEYWORDS = frozenset({"uniqueItems", "$schema"})
CODEX_OUTPUT_SCHEMA_NAME = "codex-output-schema.json"

# Report lists the canonical schema declares `uniqueItems` on; providers whose
# schema dialect cannot enforce that get the same guarantee on ingestion.
REPORT_UNIQUE_LIST_FIELDS = (
    "context_files_read",
    "pattern_files_read",
    "learning_files_read",
    "completed_subtask_ids",
)
LEARNING_UNIQUE_LIST_FIELDS = ("references", "target_task_ids")


def codex_output_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of the completion schema accepted by Codex `--output-schema`.

    Strips keywords the API rejects and makes every object strict-compliant
    (all properties listed in `required`, `additionalProperties: false`), which
    is what OpenAI structured outputs demand; the canonical file stays untouched
    for providers that honor the full dialect.
    """

    def convert(node: Any, property_map: bool = False) -> Any:
        if isinstance(node, dict):
            if property_map:
                return {key: convert(value) for key, value in node.items()}
            out: dict[str, Any] = {}
            for key, value in node.items():
                if key in CODEX_UNSUPPORTED_SCHEMA_KEYWORDS:
                    continue
                out[key] = convert(value, property_map=(key == "properties"))
            if out.get("type") == "object" and isinstance(out.get("properties"), dict):
                out["required"] = list(out["properties"].keys())
                out["additionalProperties"] = False
            return out
        if isinstance(node, list):
            return [convert(item) for item in node]
        return node

    return convert(schema)


def write_codex_output_schema(schema: dict[str, Any], result_path: Path) -> Path:
    path = result_path.parent / CODEX_OUTPUT_SCHEMA_NAME
    path.parent.mkdir(parents=True, exist_ok=True)
    planctl.atomic_write_json(path, codex_output_schema(schema))
    return path


def unique_strings(items: Any) -> Any:
    if not isinstance(items, list) or not all(isinstance(item, str) for item in items):
        return items
    return list(dict.fromkeys(items))


def normalize_report(report: dict[str, Any]) -> dict[str, Any]:
    """Drop repeated entries from report lists that must be unique.

    Order is preserved so the first mention wins; non-string lists are left for
    planctl's own validation to reject.
    """
    for field in REPORT_UNIQUE_LIST_FIELDS:
        if field in report:
            report[field] = unique_strings(report[field])
    learnings = report.get("reusable_learnings")
    if isinstance(learnings, list):
        for entry in learnings:
            if isinstance(entry, dict):
                for field in LEARNING_UNIQUE_LIST_FIELDS:
                    if field in entry:
                        entry[field] = unique_strings(entry[field])
    return report


def worker_prompt(plan_dir: Path, manifest: dict[str, Any], task: dict[str, Any], route: dict[str, str]) -> str:
    repo_root = Path(manifest["repo_root"])
    task_file = (plan_dir / task["file"]).resolve()
    try:
        relative_task = task_file.relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        relative_task = str(task_file)
    # Static rules come first and stay byte-identical across tasks so provider
    # prompt caches can share the prefix; task-specific values are appended last.
    prompt = f"""You are a fresh, isolated implementation worker for one bounded task.

Mandatory isolation rules:
1. Read the assigned task definition first. It is the only task definition assigned to you.
2. Then read every file listed under `Assigned execution context`, followed by every file under `Assigned validated learnings`. Read no other context or learning file.
3. Do not open PLAN.md, TODO.md, manifest.json, orchestrator.config.json, result files, historical logs, or any unassigned task definition under the plan workspace. If the runner appends a latest-failure capsule, open only that immediately preceding validation log when the bounded excerpt is insufficient.
4. You may read and edit repository source, tests, build files, and runtime output needed for this task.
5. Existing changes in the working tree may belong to earlier completed tasks. Preserve them and do not broadly revert or reformat unrelated code.
6. Open another task definition only when the assigned definition explicitly permits its id and a dependency, ambiguity, or validation conflict makes it necessary. Report the id and reason.
7. Implement only this task, run its required validation commands, and avoid speculative work outside scope.
8. Do not edit any planning, context, or learning artifact. The orchestrator owns plan state. The only allowed planning-state write is invoking the dedicated subtask controller for this task.
9. Do not ask for conversational context. When blocked, stop safely and report the concrete blocker, and set `failure_class` (mechanical, semantic, environmental, budget, plan_defect) so the orchestrator can choose the next route from evidence.
10. Checkpoint resumable work with the subtask controller (`subtask-start` / `subtask-complete --plan <workspace> --task <id> --subtask <id>`), never by editing the checklist.
11. Report `context_files_read` and `learning_files_read` using the exact plan-relative names from task frontmatter; use empty lists when none are assigned.
12. Report every completed checklist id in `completed_subtask_ids`. Report reusable learnings only for predeclared downstream targets and only with concrete references.

Return only the completion report requested by the configured JSON schema. Use status "completed" only when the task is implemented and its required checks pass; otherwise use "blocked".

Subtask controller: {SCRIPT_DIR / 'planctl.py'}
Repository root: {repo_root}
Plan workspace: {plan_dir}
Assigned task definition: {relative_task}
Task id: {task['id']}
Attempt: {task['attempts'] + 1}
Route: {route['provider']} / {route['model']} / effort {route['effort']}
"""
    return prompt + failure_context(task, plan_dir)


def evidence_packet_path(log_path: Path) -> Path:
    """The FailureEvidencePacket sits beside its raw validation log under the plan workspace."""
    name = log_path.name
    stem = name[: -len("-validation.log")] if name.endswith("-validation.log") else log_path.stem
    return log_path.with_name(f"{stem}-evidence.json")


def load_evidence_packet(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return value if isinstance(value, dict) else {}


def previous_evidence_path(plan_dir: Path | None, task: dict[str, Any]) -> Path | None:
    latest_log = task.get("latest_validation_log")
    if plan_dir is None or not isinstance(latest_log, str) or not latest_log:
        return None
    return evidence_packet_path(plan_dir / latest_log)


def failure_context(task: dict[str, Any], plan_dir: Path | None = None) -> str:
    """Expose only the newest compact failure evidence; keep superseded logs on disk."""
    error = str(task.get("last_error") or "").strip()
    stagnation = task.get("validation_stagnation")
    if not error and not isinstance(stagnation, dict):
        return ""
    if len(error) > VALIDATION_FAILURE_CONTEXT_CHARS:
        error = error[-VALIDATION_FAILURE_CONTEXT_CHARS:]
    lines = ["\nLatest attempt evidence (older attempt logs are preserved but do not read them):"]
    if error:
        lines.append(f"- Latest failure: {error}")
    if isinstance(stagnation, dict):
        lines.append(
            f"- Repeated validation signature: {stagnation.get('signature', '')[:12]}; "
            f"repeats={stagnation.get('repeats', 1)}; "
            f"age={stagnation.get('elapsed_seconds', 0)}s; "
            f"latest-idle={stagnation.get('idle_seconds', 0)}s."
        )
        if stagnation.get("triggered") is True:
            lines.append("- Validation stagnation crossed five minutes; this worker was deliberately routed to a stronger model.")
    packet = load_evidence_packet(previous_evidence_path(plan_dir, task)).get("packet")
    if isinstance(packet, dict):
        lines.append(
            f"- Evidence packet: signature={str(packet.get('signature', ''))[:12]}; "
            f"block_scope={packet.get('block_scope', 'validation')}; "
            f"first_failure={str(packet.get('first_failure', ''))[:200]!r}; "
            f"new_lines={len(packet.get('latest_delta') or [])}; "
            f"already_reported_omitted={packet.get('omitted_seen_lines', 0)}."
        )
    latest_log = task.get("latest_validation_log")
    if isinstance(latest_log, str) and latest_log:
        lines.append(
            f"- Full log for the most recent failed validation, only if this excerpt is insufficient: "
            f"`{latest_log}`. Do not open older logs."
        )
    return "\n" + "\n".join(lines) + "\n"


ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
VOLATILE_FAILURE_PATTERNS = (
    re.compile(r"\b\d{4}-\d\d-\d\d[T ][0-9:.+-]+Z?\b"),
    re.compile(r"\b(?:pid|process)[=: ]+\d+\b", re.IGNORECASE),
    re.compile(r"\b\d+(?:\.\d+)?\s*(?:ms|msec|seconds?|secs?)\b", re.IGNORECASE),
    re.compile(r"\b[0-9a-f]{8}-[0-9a-f-]{27,}\b", re.IGNORECASE),
)


def validation_failure_fingerprint(results: list[dict[str, Any]]) -> str | None:
    """Hash stable failure evidence so the runner can detect a stuck validation across attempts."""
    failed = next((item for item in results if item.get("passed") is False), None)
    if not isinstance(failed, dict) or failed.get("failure_class") == "environmental":
        return None
    output = str(failed.get("output_tail") or "")
    stable_lines: list[str] = []
    stalled_marker = "validation_stalled=" in output
    for line in output.splitlines():
        if line.startswith("[resource-watch]"):
            continue
        cleaned = ANSI_ESCAPE_RE.sub("", line).strip()
        for pattern in VOLATILE_FAILURE_PATTERNS:
            cleaned = pattern.sub("<volatile>", cleaned)
        if cleaned:
            stable_lines.append(cleaned[:500])
    if stalled_marker:
        stable_lines.append("validation_stalled")
    payload = "\n".join((str(failed.get("command", "")), str(failed.get("exit_code", "")), *stable_lines[-16:]))
    return hashlib.sha256(payload.encode("utf-8", "replace")).hexdigest()


ADVISORY_FORBIDDEN_KEYS = frozenset({
    "failure_class", "orchestrator_status", "status_override", "completed", "completion",
    "next_route", "route", "validation_pass", "passed",
})


def diagnostic_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The diagnostic role sees the FailureEvidencePacket, not raw log windows."""
    shaped: list[dict[str, Any]] = []
    for item in results:
        packet = item.get("failure_evidence")
        if item.get("passed") is False and isinstance(packet, dict):
            item = {
                **item,
                "output_head": str(packet.get("first_failure", "")),
                "output_tail": "\n".join(str(line) for line in packet.get("latest_delta") or []),
            }
        shaped.append(item)
    return shaped


def validation_failure_class(results: list[dict[str, Any]], declared: Any = None) -> str:
    """Deterministic class from monitor evidence; advisory diagnosis is never an input."""
    classes = [item.get("failure_class") for item in results]
    if "environmental" in classes:
        return "environmental"
    if "semantic" in classes or any(item.get("validation_stalled") is True for item in results):
        return "semantic"
    worker = str(declared or "").strip().lower()
    return worker if worker in routingctl.FAILURE_CLASSES else "semantic"


def advisory_only(advice: dict[str, Any]) -> dict[str, Any]:
    """Diagnostic output is stored as advice; it can never set failure class, route or completion."""
    return {
        **{key: value for key, value in advice.items() if key not in ADVISORY_FORBIDDEN_KEYS},
        "advisory": True,
    }


def design_note_relative(task: dict[str, Any]) -> str:
    return f"tasks/{task['id']}.design.md"


def design_prompt(plan_dir: Path, manifest: dict[str, Any], task: dict[str, Any], route: dict[str, str]) -> str:
    """Two-phase leaf, phase 1: a stronger route designs; a cheaper route implements."""
    task_file = (plan_dir / task["file"]).resolve()
    note_path = (plan_dir / design_note_relative(task)).resolve()
    return f"""You are a fresh, isolated design worker for one bounded task. Design only; do not implement.

Rules:
1. Read the task definition first, then exactly the context and learning files it lists (and the shared-pattern files if the runner appends them). Read no other plan artifact.
2. Inspect repository code needed to design this task. Do not edit repository files.
3. Write one design note, at most {DESIGN_NOTE_MAX_CHARS} characters, to the note path below. The note must contain: approach; key decisions with one-line rationale; interfaces/data contracts to keep; ordered implementation steps mapped to the task's checkpoint ids; risks and the validation strategy. Reference paths/symbols instead of pasting code.
4. The note path is the only file you may write. Do not run the subtask controller.
5. Return the JSON completion report: status "completed" with a one-sentence summary when the note exists; otherwise "blocked" with the blocker and `failure_class`. Report `context_files_read` and `learning_files_read` exactly as listed in the task frontmatter and use `completed_subtask_ids: []`.

Repository root: {manifest['repo_root']}
Task definition: {task_file}
Design note path: {note_path}
Task id: {task['id']}
Route: {route['provider']} / {route['model']} / {route['effort']}
"""


def append_design_note(prompt: str, plan_dir: Path, task: dict[str, Any]) -> str:
    phase = task.get("design_phase") or {}
    note_file = phase.get("note_file") if phase.get("status") == "completed" else None
    if not note_file:
        return prompt
    note_path = (plan_dir / note_file).resolve()
    return prompt + (
        f"\nDesign note: `{note_path}` — read it right after the task definition; it fixes the approach, "
        "contracts, and step order for this task. Report it under `context_files_read` is NOT required.\n"
    )


def design_route_task(task: dict[str, Any]) -> dict[str, Any]:
    """A task-shaped view whose declared route is the design route."""
    design = task.get("design_route") or {}
    return {
        **task,
        "model_tier": design.get("model_tier", "strong"),
        "reasoning_effort": design.get("reasoning_effort", "medium"),
    }


def configured_model_args(flag: str, model: str) -> list[str]:
    return [] if not model or model == "default" else [flag, model]


def effort_args(provider_cfg: dict[str, Any], model: str, effort: str, *, style: str) -> list[str]:
    """Effort flag for one provider, omitted for models that accept none (e.g. Haiku)."""
    if not routingctl.model_supports_effort(provider_cfg, model):
        return []
    if style == "claude":
        return ["--effort", effort]
    if style == "codex":
        return ["-c", f'model_reasoning_effort="{effort}"']
    if style == "muse":
        return ["--reasoning-effort", effort]
    return []


def budget_args(provider: str, provider_cfg: dict[str, Any]) -> list[str]:
    """Optional per-worker budget guards (0/unset disables them)."""
    if provider == "claude":
        args: list[str] = []
        turns = int(provider_cfg.get("max_turns", 0) or 0)
        if turns > 0:
            args.extend(["--max-turns", str(turns)])
        budget = float(provider_cfg.get("max_budget_usd", 0) or 0)
        if budget > 0:
            args.extend(["--max-budget-usd", f"{budget:.2f}"])
        return args
    if provider == "codex":
        tokens = int(provider_cfg.get("rollout_token_budget", 0) or 0)
        if tokens > 0:
            return [
                "-c",
                "features.rollout_budget.enabled=true",
                "-c",
                f"features.rollout_budget.limit_tokens={tokens}",
            ]
    return []


def is_budget_exhausted(text: str) -> bool:
    return any(pattern.search(text) for pattern in BUDGET_PATTERNS)


def classify_report_failure(report: dict[str, Any] | None, text: str) -> str:
    """Map worker/report evidence to a routing failure class."""
    if isinstance(report, dict):
        declared = str(report.get("failure_class") or "").strip().lower()
        if declared in routingctl.FAILURE_CLASSES:
            return declared
    if is_budget_exhausted(text):
        return "budget"
    return "unknown"


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


def antigravity_schema_text(schema: dict[str, Any]) -> str:
    """Schema text for `agy --json-schema`: Gemini function declarations reject `null` in `enum`
    (INVALID_ARGUMENT "enum[n]: cannot be empty") and union types; optional fields stay optional."""

    def convert(node: Any, property_map: bool = False) -> Any:
        if isinstance(node, dict):
            if property_map:
                return {key: convert(value) for key, value in node.items()}
            out: dict[str, Any] = {}
            for key, value in node.items():
                if key == "enum" and isinstance(value, list):
                    out[key] = [item for item in value if item is not None]
                elif key == "type" and isinstance(value, list):
                    kept = [item for item in value if item != "null"]
                    out[key] = kept[0] if len(kept) == 1 else kept
                else:
                    out[key] = convert(value, property_map=(key == "properties"))
            return out
        if isinstance(node, list):
            return [convert(item) for item in node]
        return node

    return json.dumps(convert(schema), ensure_ascii=False, separators=(",", ":"))


def build_worker_command(
    provider: str,
    route: dict[str, str],
    config: dict[str, Any],
    prompt: str,
    result_path: Path,
) -> list[str]:
    provider_cfg = config[provider]
    # The profile picks the harness adapter; settings stay the provider's own.
    profile = provider_profile(provider, config)
    adapter = profile["adapter"]
    prefix = command_prefix(profile["command"])
    schema = planctl.read_json(completion_schema_path())
    schema_text = json.dumps(schema, ensure_ascii=False, separators=(",", ":"))
    extra_args = provider_cfg.get("extra_args", [])
    if not isinstance(extra_args, list) or not all(isinstance(item, str) for item in extra_args):
        raise RunnerError(f"{provider}.extra_args must be a list of strings")

    if adapter == "claude":
        command = prefix + claude_bare_flags() + [
            "--print",
            "--no-session-persistence",
            "--output-format",
            "json",
            "--permission-mode",
            str(provider_cfg.get("permission_mode", "auto")),
        ]
        command.extend(configured_model_args("--model", route["model"]))
        command.extend(effort_args(provider_cfg, route["model"], route["effort"], style="claude"))
        command.extend(budget_args(adapter, provider_cfg))
        command.extend(["--json-schema", schema_text])
        command.extend(extra_args)
        command.append(prompt)
        return command

    if adapter == "codex":
        command = prefix + [
            "exec",
            "--ephemeral",
            "--sandbox",
            str(provider_cfg.get("sandbox", "workspace-write")),
        ]
        command.extend(configured_model_args("--model", route["model"]))
        command.extend(effort_args(provider_cfg, route["model"], route["effort"], style="codex"))
        command.extend(budget_args(adapter, provider_cfg))
        command.extend(
            [
                "--output-schema",
                str(write_codex_output_schema(schema, result_path)),
                "--output-last-message",
                str(result_path),
            ]
        )
        if provider_cfg.get("ignore_user_config"):
            command.append("--ignore-user-config")
        command.extend(extra_args)
        command.append(prompt)
        return command

    if adapter == "antigravity":
        command = list(prefix)
        if provider_cfg.get("skip_permissions", True):
            command.append("--dangerously-skip-permissions")
        if provider_cfg.get("sandbox", False):
            command.append("--sandbox")
        command.extend(["--output-format", "json", "--json-schema", antigravity_schema_text(schema)])
        command.extend(configured_model_args("--model", route["model"]))
        command.extend(effort_args(provider_cfg, route["model"], route["effort"], style="claude"))
        command.extend(["--print-timeout", antigravity_print_timeout(provider_cfg, config)])
        command.extend(extra_args)
        command.extend(["-p", prompt])
        return command

    if adapter == "gemini":
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

    if adapter == "qwen":
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

    if adapter == "kimi":
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

    if adapter == "trae":
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

    if adapter == "muse":
        command = prefix + ["exec", "--json"]
        # Write authority is opt-in per provider config; both default to off.
        if provider_cfg.get("trust_workspace", False) is True:
            command.append(MUSE_TRUST_WORKSPACE_FLAG)
        if provider_cfg.get("disable_approval", False) is True:
            command.append(MUSE_DISABLE_APPROVAL_FLAG)
        command.extend(configured_model_args("--model", route["model"]))
        command.extend(effort_args(provider_cfg, route["model"], route["effort"], style="muse"))
        command.extend(extra_args)
        command.append(prompt)
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
    env: dict[str, str] | None = None,
) -> tuple[int, str, str]:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    stdout_lines: list[str] = []
    stderr_lines: list[str] = []
    # cmd.exe truncates a `.cmd` shim argument at its first newline (the worker then sees only the
    # prompt's last line), so newlines inside any argument become an ASCII separator on Windows shims.
    if os.name == "nt" and command and command[0].lower().endswith((".cmd", ".bat")):
        command = [" ;; ".join(line.strip() for line in part.splitlines() if line.strip()) if "\n" in part else part for part in command]
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
                env=env,
            )
        except FileNotFoundError:
            return 127, "", "Provider executable disappeared after preflight"
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
        if isinstance(value.get("status"), str) and value["status"] in {"completed", "blocked"} and isinstance(value.get("summary"), str):
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
            return normalize_report(report)
    return None


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
    return availability.classify(return_code, text, configured_retry_exit_codes(provider, config)) in {*availability.CATEGORIES, "configured_exit"}


def output_tail(text: str, length: int = 3000) -> str:
    stripped = text.strip()
    return stripped[-length:] if stripped else ""


def read_log_tail_since(path: Path, start_offset: int, limit_bytes: int = 12000) -> str:
    """Read only the bounded tail of one validation from its raw attempt log."""
    try:
        with path.open("rb") as source:
            end = source.seek(0, os.SEEK_END)
            start = max(start_offset, end - limit_bytes)
            source.seek(start)
            return source.read().decode("utf-8", errors="replace")
    except OSError:
        return ""


def validation_timeout_seconds(task: dict[str, Any], config: dict[str, Any]) -> int:
    configured = task.get("validation_timeout_seconds", config.get("validation_timeout_seconds", 1800))
    return max(0, int(configured))


def terminate_validation_tree(process: subprocess.Popen, grace_seconds: float = 2) -> None:
    """Allow graceful exit, then kill the entire validation session."""
    if os.name == "nt":
        try:
            process.send_signal(signal.CTRL_BREAK_EVENT)
        except (AttributeError, OSError):
            pass
    else:
        session_pids = process_tree.posix_session_processes(process.pid)
        if session_pids is None:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        else:
            for pid in session_pids:
                try:
                    os.kill(pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
    time.sleep(grace_seconds)
    if os.name == "nt":
        try:
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            pass
        # Covers unavailable taskkill and a shell that survived tree cleanup.
        if process.poll() is None:
            process.kill()
    else:
        session_pids = process_tree.posix_session_processes(process.pid)
        if session_pids is None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        else:
            for pid in session_pids:
                try:
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
    process.wait()


def run_validation_commands(
    repo_root: Path,
    commands: list[str],
    log_path: Path,
    timeout_seconds: int,
    *,
    evidence_path: Path | None = None,
    seen_lines: list[str] | None = None,
) -> tuple[bool, list[dict[str, Any]], str | None]:
    results: list[dict[str, Any]] = []
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("wb") as log:
        for command in commands:
            print(f"[validate] {command}", flush=True)
            log.write(f"$ {command}\n".encode("utf-8", errors="replace"))
            log.flush()
            output_start = log.tell()
            group_options = (
                {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
                if os.name == "nt" else {"start_new_session": True}
            )
            with subprocess.Popen(
                command,
                cwd=repo_root,
                shell=True,
                stdout=log,
                stderr=subprocess.STDOUT,
                **group_options,
            ) as process:
                try:
                    process.wait(timeout=timeout_seconds or None)
                    exit_code = process.returncode
                except subprocess.TimeoutExpired:
                    terminate_validation_tree(process)
                    log.flush()
                    log.seek(0, os.SEEK_END)
                    log.write(f"\nTimed out after {timeout_seconds} seconds\n".encode("utf-8"))
                    exit_code = 124
            log.flush()
            log.seek(0, os.SEEK_END)
            log.write(f"[exit {exit_code}]\n\n".encode("utf-8"))
            log.flush()
            output = read_log_tail_since(log_path, output_start)
            passed = exit_code == 0
            # Keep only a bounded first-failure window; raw logs stay on disk.
            with log_path.open("rb") as evidence_log:
                evidence_log.seek(output_start)
                first_window = evidence_log.read(1200).decode("utf-8", errors="replace")
            results.append(
                {
                    "command": command,
                    "passed": passed,
                    "exit_code": exit_code,
                    "output_tail": output_tail(output, 2000),
                    "output_head": first_window if not passed else "",
                    **assistant_triage.observations(output),
                    "failure_class": (
                        "environmental"
                        if "[resource-watch] environment_failure=" in output
                        else "semantic"
                        if "[resource-watch] validation_stalled=" in output
                        or "[resource-watch] semantic_failure=" in output
                        else None
                    ),
                    "validation_stalled": "[resource-watch] validation_stalled=" in output,
                    "validation_idle_seconds": max(
                        (int(value) for value in re.findall(r"validation_stalled=confirmed[^\n]*idle_seconds=(\d+)", output)),
                        default=0,
                    ),
                }
            )
            if not passed:
                failed = results[-1]
                built = resource_watch.build_failure_packet(
                    log_path,
                    start_offset=output_start,
                    command=command,
                    exit_code=exit_code,
                    signature=validation_failure_fingerprint([failed]),
                    process={"timed_out": "Timed out after" in output, "exit_code": exit_code},
                    resources={
                        "unhealthy_samples": failed.get("unhealthy_samples", 0),
                        "environment_failure": failed["failure_class"] == "environmental",
                    },
                    progress={
                        "validation_stalled": failed["validation_stalled"],
                        "idle_seconds": failed["validation_idle_seconds"],
                    },
                    seen=seen_lines,
                )
                failed["failure_evidence"] = built["packet"]
                if evidence_path is not None:
                    evidence_path.parent.mkdir(parents=True, exist_ok=True)
                    planctl.atomic_write_json(evidence_path, built)
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
    catalog_models: dict[str, dict[str, str]] | None = None,
) -> bool:
    repo_root = Path(manifest["repo_root"])
    dispatches = 0
    model_refreshed = False
    visited = {"design": set(), "implementation": set()}
    maximum = config.get("availability", {}).get("max_attempts_per_run", 7)
    while True:
        if dispatches >= maximum:
            raise availability.AvailabilityPaused(f"Task {task['id']} pending: availability dispatch budget reached; resume later")
        if not dry_run and ladder_exhausted(task, config, provider_override, check_availability=False):
            planctl.block_task(
                plan_dir,
                manifest,
                task["id"],
                "Escalation ladder exhausted on the last available provider; "
                "replan the TODO or repair the evidence before retrying.",
                event="ladder_exhausted",
            )
            print(f"[task {task['id']}] blocked: escalation ladder exhausted; replan", file=sys.stderr)
            return False
        phase = "design" if needs_design_phase(task) else "implementation"
        routing_task = design_route_task(task) if phase == "design" else task
        intent = choose_route(routing_task, config, provider_override, check_availability=False)
        route = availability.select(
            plan_dir, routing_task, config, intent, provider_override, phase, visited[phase],
            lambda provider: executable_available(provider_prefix(provider, config)),
            clamp_effort, persist=not dry_run,
        )
        route = resolve_snapshot_route(plan_dir, routing_task, route, config, catalog_models)
        shadow = shadow_candidate(routing_task, route, config, provider_override, phase=phase) if shadow_enabled(config) else None
        if shadow is not None and auto_select_mode(config) == "on":
            ladder = route
            route, shadow["auto"] = auto_route(
                plan_dir, repo_root, routing_task, route, config, shadow, phase=phase, catalog_models=catalog_models
            )
            if shadow["auto"]["applied"]:
                shadow["ladder"] = {key: ladder.get(key) for key in SHADOW_ROUTE_KEYS}
                shadow["executed"] = {key: route.get(key) for key in SHADOW_ROUTE_KEYS}
        if shadow is not None and not dry_run:
            record_shadow(plan_dir, shadow, repo_root)
        visited[phase].add(route["provider"])
        dispatches += 1
        if phase == "design":
            outcome = run_design_phase(
                plan_dir, manifest, config, task, provider_override=provider_override, dry_run=dry_run, route_override=route
            )
            if outcome == "rate_limited":
                task = planctl.find_task(manifest, task["id"])
                continue
            if outcome != "completed":
                return False
            task = planctl.find_task(manifest, task["id"])
            continue
        result_path = normalized_result_file(plan_dir, task, route)
        prompt = append_design_note(worker_prompt(plan_dir, manifest, task, route), plan_dir, task)
        prompt += assistant_triage.hint(plan_dir, task, config)
        command = build_worker_command(route["provider"], route, config, prompt, result_path)
        if dry_run:
            preview = {"task": task["id"], "route": route, "command": redact_command(command)}
            if shadow is not None:
                preview["shadow"] = shadow
            print(json.dumps(preview, indent=2))
            return False

        env = spawn_env(route["provider"], config)
        print(
            f"[task {task['id']}] {task['title']} — {route['provider']} / {route['model']} / {route['effort']}",
            flush=True,
        )
        claimed = planctl.claim_task(plan_dir, manifest, task["id"], route)
        attempt_number = claimed["attempts"]
        log_path = plan_dir / "logs" / f"{task['id']}-attempt-{attempt_number}-{route['provider']}.log"
        started = time.monotonic()
        try:
            return_code, stdout, stderr = run_process(
                command,
                repo_root,
                log_path,
                timeout_seconds=max(0, int(config.get("task_timeout_seconds", 0))),
                stream_output=bool(config.get("stream_provider_output", True)),
                env=env,
            )
        except KeyboardInterrupt:
            refresh_manifest(plan_dir, manifest)
            release_interrupted_task(plan_dir, manifest, task["id"])
            raise
        elapsed = time.monotonic() - started

        def record_attempt(outcome: str, failure_class: str | None = None, validation_pass: bool | None = None) -> None:
            try:
                profile = provider_profile(route["provider"], config)
                entry = routing_telemetry.build_record(
                    task=task, route=route, profile=profile, kind="retry" if attempt_number > 1 else "root",
                    stdout=stdout, latency_seconds=elapsed, outcome=outcome, failure_class=failure_class,
                    validation_pass=validation_pass, retry_count=max(0, attempt_number - 1),
                )
                routing_telemetry.append_record(plan_dir, entry, repo_root)
            except Exception as exc:  # noqa: BLE001 - telemetry must not stop execution
                print(f"[telemetry] not recorded: {type(exc).__name__}", file=sys.stderr)

        refresh_manifest(plan_dir, manifest)
        task = planctl.find_task(manifest, task["id"])

        combined = f"{stdout}\n{stderr}"
        if return_code in (130, 143, -2, -15):
            release_interrupted_task(plan_dir, manifest, task["id"])
            raise KeyboardInterrupt
        category = availability.classify(return_code, combined, configured_retry_exit_codes(route["provider"], config))
        if (category == "configuration" and not model_refreshed and snapshot_resolution(config)
                and INVALID_MODEL.search(combined[-16000:])):
            # A retired/renamed model id is a configuration event, not task
            # evidence: refresh the snapshot once and redispatch the same rung.
            model_refreshed = True
            release_for_model_refresh(plan_dir, manifest, task["id"], f"Invalid model {route['model']}; snapshot refreshed")
            refresh_model_snapshot(plan_dir, route["provider"])
            refresh_manifest(plan_dir, manifest)
            task = planctl.find_task(manifest, task["id"])
            visited[phase].discard(route["provider"])
            print(f"[task {task['id']}] invalid model {route['model']}; snapshot refreshed once, redispatching", file=sys.stderr)
            continue
        if category:
            record_attempt(category, "plan_defect" if category == "configuration" else None)
        if category == "configuration":
            planctl.fail_task(plan_dir, manifest, task["id"], "Provider rejected its arguments/model; repair configuration", failure_class="plan_defect")
            return False
        if category:
            availability.unavailable(plan_dir, task["id"], "implementation", route, category, config)
            planctl.fail_task(plan_dir, manifest, task["id"], f"Provider unavailable: {route['provider']}/{category}", rate_limited=True)
            task = planctl.find_task(manifest, task["id"])
            continue

        report = parse_provider_report(route["provider"], stdout, result_path)
        if return_code != 0:
            reason = f"Provider exited with {return_code}: {output_tail(combined)}"
            cls = classify_report_failure(report, combined)
            record_attempt("provider_error", cls)
            planctl.fail_task(plan_dir, manifest, task["id"], reason, failure_class=cls)
            print(f"[task {task['id']}] provider failure ({cls}); next route follows the evidence ladder", file=sys.stderr)
            return False
        if not report:
            reason = f"Provider returned no valid completion report. Output: {output_tail(combined)}"
            cls = classify_report_failure(None, combined)
            record_attempt("invalid_report", cls)
            planctl.fail_task(plan_dir, manifest, task["id"], reason, failure_class=cls)
            print(f"[task {task['id']}] invalid report ({cls}); next route follows the evidence ladder", file=sys.stderr)
            return False
        expected_context_files = list(task.get("context_files", []))
        reported_context_files = report.get("context_files_read")
        if _plan_context_files(
            reported_context_files, plan_dir, expected_context_files, task.get("file")
        ) != sorted(_plan_relative_files(expected_context_files, plan_dir)):
            record_attempt("report_mismatch")
            reason = (
                "Worker context report mismatch: expected "
                f"{expected_context_files!r}, received {reported_context_files!r}"
            )
            planctl.fail_task(plan_dir, manifest, task["id"], reason)
            print(f"[task {task['id']}] context assignment was not acknowledged", file=sys.stderr)
            return False
        expected_learning_files = list(task.get("learning_files", []))
        reported_learning_files = report.get("learning_files_read")
        if _plan_relative_files(reported_learning_files, plan_dir, task.get("file")) != _plan_relative_files(expected_learning_files, plan_dir):
            record_attempt("report_mismatch")
            reason = (
                "Worker learning report mismatch: expected "
                f"{expected_learning_files!r}, received {reported_learning_files!r}"
            )
            planctl.fail_task(plan_dir, manifest, task["id"], reason)
            print(f"[task {task['id']}] learning assignment was not acknowledged", file=sys.stderr)
            return False
        if report.get("status") != "completed":
            reason = str(report.get("blocked_reason") or report.get("summary") or "Worker reported blocked")
            if is_rate_limited(reason):
                availability.unavailable(plan_dir, task["id"], "implementation", route, "quota", config)
                planctl.fail_task(plan_dir, manifest, task["id"], "Worker reported provider quota exhaustion", rate_limited=True)
                task = planctl.find_task(manifest, task["id"])
                continue
            cls = classify_report_failure(report, reason)
            record_attempt("blocked", cls)
            planctl.fail_task(plan_dir, manifest, task["id"], reason, failure_class=cls)
            atomic = {**report, "orchestrator_status": "failed"}
            planctl.atomic_write_json(result_path, atomic)
            print(f"[task {task['id']}] blocked ({cls}): {reason}", file=sys.stderr)
            return False

        validation_log = plan_dir / "logs" / f"{task['id']}-attempt-{attempt_number}-validation.log"
        previous_owner = {key: os.environ.get(key) for key in ("PAE_ARTIFACT_SCOPE", "PAE_ARTIFACT_OWNER")}
        os.environ["PAE_ARTIFACT_SCOPE"], os.environ["PAE_ARTIFACT_OWNER"] = "task", str(task["id"])
        try:
            resource_watch.register_artifact(repo_root, validation_log)
            evidence_path = evidence_packet_path(validation_log)
            resource_watch.register_artifact(repo_root, evidence_path)
            previous_packet = load_evidence_packet(previous_evidence_path(plan_dir, task))
            passed, validation_results, validation_reason = run_validation_commands(
                repo_root,
                list(task["validation_commands"]),
                validation_log,
                validation_timeout_seconds(task, config),
                evidence_path=evidence_path,
                seen_lines=list(previous_packet.get("seen") or []),
            )
        finally:
            for key, value in previous_owner.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
        report["validation_results"] = validation_results
        reported_files = report.get("changed_files")
        if not isinstance(reported_files, list) or not reported_files:
            report["changed_files"] = git_changed_files(repo_root)
        if not passed:
            report["orchestrator_status"] = "validation_failed"
            planctl.atomic_write_json(result_path, report)
            # A worker that claimed completion but failed deterministic validation
            # misjudged the work: a reasoning gap (semantic) unless it declares a
            # narrower class itself.
            cls = validation_failure_class(validation_results, report.get("failure_class"))
            stalled_after_five = any(
                isinstance(item.get("validation_idle_seconds"), int)
                and item["validation_idle_seconds"] >= 300
                for item in validation_results
            )
            signature = validation_failure_fingerprint(validation_results)
            record_attempt("validation_failed", cls, False)
            planctl.fail_task(
                plan_dir,
                manifest,
                task["id"],
                validation_reason or "Validation failed",
                failure_class=cls,
                validation_signature=signature,
                validation_stalled=stalled_after_five,
                validation_idle_seconds=max(
                    (int(item.get("validation_idle_seconds", 0)) for item in validation_results),
                    default=0,
                ),
                validation_log=validation_log.relative_to(plan_dir).as_posix(),
            )
            advice_result = advisory_only(
                assistant_triage.triage(plan_dir, task, diagnostic_results(validation_results), config)
            )
            if advice_result.get("reason") != "not_eligible":
                report["assistant_triage"] = advice_result
                planctl.atomic_write_json(result_path, report)
                print(f"[task {task['id']}] advisory triage: {advice_result['status']}; "
                      f"{advice_result.get('reason', 'unverified advice saved')}", file=sys.stderr)
            print(f"[task {task['id']}] deterministic validation failed ({cls}); next route follows the evidence ladder", file=sys.stderr)
            return False

        report["orchestrator_status"] = "completed"
        record_attempt("completed", None, True)
        planctl.atomic_write_json(result_path, report)
        relative_result = result_path.relative_to(plan_dir).as_posix()
        try:
            planctl.complete_task(plan_dir, manifest, task["id"], report, relative_result)
            resource_watch.cleanup_artifacts(repo_root, "task", str(task["id"]))
        except planctl.PlanError as exc:
            # Optional worker metadata must not strand validated work in progress.
            # Keep required completion evidence so a retry cannot bypass its checks.
            print(f"[task {task['id']}] completion report rejected: {exc}; retrying without optional metadata", file=sys.stderr)
            report = {
                **report,
                "summary": report.get("summary") or f"Task {task['id']} completed and validated.",
                "risks": [],
                "follow_ups": [],
                "reusable_learnings": [],
            }
            planctl.atomic_write_json(result_path, report)
            try:
                planctl.complete_task(plan_dir, manifest, task["id"], report, relative_result)
            except planctl.PlanError as retry_exc:
                reason = f"Completion report rejected after metadata recovery: {retry_exc} (initial error: {exc})"
                report["orchestrator_status"] = "completion_failed"
                planctl.atomic_write_json(result_path, report)
                planctl.fail_task(plan_dir, manifest, task["id"], reason)
                print(f"[task {task['id']}] {reason}", file=sys.stderr)
                return False
        print(f"[task {task['id']}] completed and validated", flush=True)
        return True


def ladder_exhausted(task: dict[str, Any], config: dict[str, Any], override: str | None, *, check_availability: bool = True) -> bool:
    """True when failure evidence already climbed past the top rung on the last provider."""
    classes = task.get("failure_classes")
    if not isinstance(classes, list) or not classes:
        return False
    providers = (candidate_providers(task, config, override) if check_availability
                 else routing_config.provider_chain(task, config, override))
    failures_per_provider = max(1, int(config.get("functional_failures_per_provider", 4)))
    provider_slot = int(task.get("functional_failures", 0)) // failures_per_provider
    if provider_slot < len(providers) - 1:
        return False
    provider_cfg = config[providers[min(provider_slot, len(providers) - 1)]]
    rungs = routingctl.route_rungs(
        provider_cfg,
        str(task.get("model_tier", "standard")),
        str(task.get("reasoning_effort", "medium")),
    )
    return routingctl.escalation_exhausted(classes, rungs)


def needs_design_phase(task: dict[str, Any]) -> bool:
    if not task.get("design_route"):
        return False
    phase = task.get("design_phase") or {}
    return phase.get("status") != "completed"


def run_design_phase(
    plan_dir: Path,
    manifest: dict[str, Any],
    config: dict[str, Any],
    task: dict[str, Any],
    *,
    provider_override: str | None,
    dry_run: bool,
    route_override: dict[str, str] | None = None,
) -> str:
    """Phase 1 of a two-phase leaf. Returns completed | failed | rate_limited."""
    repo_root = Path(manifest["repo_root"])
    route = route_override or choose_route(design_route_task(task), config, provider_override)
    note_relative = design_note_relative(task)
    note_path = plan_dir / note_relative
    result_path = plan_dir / "results" / f"{task['id']}-design-attempt-{task['attempts'] + 1}-{route['provider']}.json"
    prompt = design_prompt(plan_dir, manifest, task, route)
    command = build_worker_command(route["provider"], route, config, prompt, result_path)
    if dry_run:
        print(json.dumps({"task": task["id"], "phase": "design", "route": route, "command": redact_command(command)}, indent=2))
        return "dry_run"
    env = spawn_env(route["provider"], config)
    print(f"[task {task['id']}] design phase — {route['provider']} / {route['model']} / {route['effort']}", flush=True)
    planctl.claim_task(plan_dir, manifest, task["id"], {**route, "phase": "design"})
    attempt_number = planctl.find_task(manifest, task["id"])["attempts"]
    log_path = plan_dir / "logs" / f"{task['id']}-design-attempt-{attempt_number}-{route['provider']}.log"
    try:
        return_code, stdout, stderr = run_process(
            command,
            repo_root,
            log_path,
            timeout_seconds=max(0, int(config.get("task_timeout_seconds", 0))),
            stream_output=bool(config.get("stream_provider_output", True)),
            env=env,
        )
    except KeyboardInterrupt:
        refresh_manifest(plan_dir, manifest)
        release_interrupted_task(plan_dir, manifest, task["id"])
        raise
    refresh_manifest(plan_dir, manifest)
    task = planctl.find_task(manifest, task["id"])
    combined = f"{stdout}\n{stderr}"
    if return_code in (130, 143, -2, -15):
        release_interrupted_task(plan_dir, manifest, task["id"])
        raise KeyboardInterrupt
    category = availability.classify(return_code, combined, configured_retry_exit_codes(route["provider"], config))
    if category == "configuration":
        planctl.fail_task(plan_dir, manifest, task["id"], "Design provider rejected its arguments/model; repair configuration", failure_class="plan_defect")
        return "failed"
    if category:
        availability.unavailable(plan_dir, task["id"], "design", route, category, config)
        planctl.fail_task(plan_dir, manifest, task["id"], f"Design provider unavailable: {route['provider']}/{category}", rate_limited=True)
        return "rate_limited"
    report = parse_provider_report(route["provider"], stdout, result_path)
    if report and report.get("status") != "completed" and is_rate_limited(str(report.get("blocked_reason", ""))):
        availability.unavailable(plan_dir, task["id"], "design", route, "quota", config)
        planctl.fail_task(plan_dir, manifest, task["id"], "Design worker reported quota exhaustion", rate_limited=True)
        return "rate_limited"
    note_text = note_path.read_text(encoding="utf-8").strip() if note_path.is_file() else ""
    if return_code != 0 or not report or report.get("status") != "completed" or not note_text:
        reason = (
            str((report or {}).get("blocked_reason") or "")
            or f"Design phase produced no usable note (exit {return_code}): {output_tail(combined)}"
        )
        cls = classify_report_failure(report, combined)
        planctl.fail_task(plan_dir, manifest, task["id"], reason, failure_class=cls)
        print(f"[task {task['id']}] design phase failed ({cls})", file=sys.stderr)
        return "failed"
    if len(note_text) > DESIGN_NOTE_MAX_CHARS:
        note_path.write_text(note_text[:DESIGN_NOTE_MAX_CHARS].rstrip() + "\n", encoding="utf-8")
    # The design attempt must not consume the implementation attempt: release
    # the claim so the implementation worker claims the task itself.
    planctl.release_design_claim(plan_dir, manifest, task["id"])
    planctl.complete_design_phase(plan_dir, manifest, task["id"], note_relative, route)
    print(f"[task {task['id']}] design note accepted: {note_relative}", flush=True)
    return "completed"


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
    profile = provider_profile(provider, config)
    adapter = profile["adapter"]
    prefix = command_prefix(profile["command"])
    extra_args = provider_cfg.get("extra_args", [])
    # Each adapter below pins its own read-only mode; an adapter without one fails closed before spawning.
    if adapter == "claude":
        command = prefix + claude_bare_flags() + [
            "--print",
            "--no-session-persistence",
            "--output-format",
            "text",
            "--permission-mode",
            "plan",
        ]
        command.extend(configured_model_args("--model", route["model"]))
        command.extend(effort_args(provider_cfg, route["model"], route["effort"], style="claude"))
        command.extend(extra_args)
        command.append(prompt)
        return command
    if adapter == "codex":
        command = prefix + [
            "exec",
            "--ephemeral",
            "--sandbox",
            "read-only",
        ]
        command.extend(configured_model_args("--model", route["model"]))
        command.extend(effort_args(provider_cfg, route["model"], route["effort"], style="codex"))
        command.extend(
            [
                "--output-last-message",
                str(output_path),
            ]
        )
        if provider_cfg.get("ignore_user_config"):
            command.append("--ignore-user-config")
        command.extend(extra_args)
        command.append(prompt)
        return command
    if adapter == "antigravity":
        command = list(prefix)
        if provider_cfg.get("summary_skip_permissions", True):
            command.append("--dangerously-skip-permissions")
        if provider_cfg.get("summary_sandbox", True):
            command.append("--sandbox")
        command.extend(["--output-format", "json"])
        command.extend(configured_model_args("--model", route["model"]))
        command.extend(effort_args(provider_cfg, route["model"], route["effort"], style="claude"))
        command.extend(["--print-timeout", antigravity_print_timeout(provider_cfg, config)])
        command.extend(extra_args)
        command.extend(["-p", prompt])
        return command
    if adapter == "gemini":
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
    if adapter == "qwen":
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
    if adapter == "kimi":
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
    if adapter == "trae":
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
    if adapter == "muse":
        if not isinstance(extra_args, list) or not all(isinstance(item, str) for item in extra_args):
            raise RunnerError(f"{provider}.extra_args must be a list of strings")
        widening = [item for item in extra_args if item in MUSE_WRITE_FLAGS]
        if widening:
            raise RunnerError(f"Muse summary is read-only; {widening[0]} cannot be passed to it")
        command = prefix + ["exec", "--json", MUSE_READ_ONLY_FLAG]
        command.extend(configured_model_args("--model", route["model"]))
        command.extend(effort_args(provider_cfg, route["model"], route["effort"], style="muse"))
        command.extend(extra_args)
        command.append(prompt)
        # Fail closed before spawning if the read-only flag is not provably in the argv.
        if MUSE_READ_ONLY_FLAG not in command[: len(command) - 1]:
            raise RunnerError("Muse summary requires --disable-write and it is absent; refusing to spawn")
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


MUSE_TEXT_KEYS = ("result", "response", "final_message", "final_output", "answer", "text", "message", "content", "output")


def muse_summary_text(stdout: str) -> str:
    """Last text-bearing event of a Muse JSON envelope or JSONL stream.

    Only named text keys are read: bookkeeping events (usage, init) carry no summary and
    their `type` strings must never be mistaken for one.
    """
    events: list[Any] = []
    try:
        events.append(json.loads(stdout))
    except json.JSONDecodeError:
        for line in stdout.splitlines():
            try:
                events.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                continue
    for event in reversed(events):
        if not isinstance(event, dict):
            continue
        for key in MUSE_TEXT_KEYS:
            if key in event:
                found = extract_text_output(event[key])
                if found:
                    return found
    return ""


def summary_stdout_text(provider: str, stdout: str, output_path: Path) -> str:
    if provider == "codex":
        return output_path.read_text(encoding="utf-8").strip() if output_path.is_file() else ""
    if provider == "muse":
        return muse_summary_text(stdout) if stdout.strip() else ""
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
    rate_cycle = 0
    try:
        route = summary_route(config)
        env = spawn_env(route["provider"], config)
    except RunnerError:
        fallback = planctl.deterministic_summary(manifest)
        planctl.atomic_write_text(output_path, fallback)
        return fallback, output_path.relative_to(plan_dir).as_posix()

    while True:
        try:
            command = build_summary_command(route["provider"], route, config, prompt, output_path)
        except RunnerError:
            # No provable read-only mode: nothing is spawned and the deterministic summary stands in.
            fallback = planctl.deterministic_summary(manifest)
            planctl.atomic_write_text(output_path, fallback)
            return fallback, output_path.relative_to(plan_dir).as_posix()
        log_path = plan_dir / "logs" / f"final-summary-{route['provider']}.log"
        print(f"[summary] {route['provider']} / {route['model']} / {route['effort']}", flush=True)
        return_code, stdout, stderr = run_process(
            command,
            Path(manifest["repo_root"]),
            log_path,
            timeout_seconds=max(0, int(config.get("task_timeout_seconds", 0))),
            stream_output=False,
            env=env,
        )
        combined = f"{stdout}\n{stderr}"
        if return_code != 0 and is_provider_availability_failure(
            route["provider"], return_code, combined, config
        ):
            if wait_after_rate_limit(config, rate_cycle, no_wait):
                rate_cycle += 1
                continue
        if return_code == 0:
            adapter = provider_profile(route["provider"], config)["adapter"]
            summary = summary_stdout_text(adapter, stdout, output_path)
            if summary and adapter != "codex":
                planctl.atomic_write_text(output_path, summary + "\n")
            if summary:
                return summary + "\n", output_path.relative_to(plan_dir).as_posix()
        fallback = planctl.deterministic_summary(manifest)
        planctl.atomic_write_text(output_path, fallback)
        return fallback, output_path.relative_to(plan_dir).as_posix()


def _run_plan(args: argparse.Namespace) -> int:
    plan_dir, manifest = planctl.load_plan(args.plan)
    planctl.require_valid(plan_dir, manifest)
    config = load_config(plan_dir)
    stale = stale_snapshot_warning(plan_dir)
    if stale:
        print(f"[resume] warning: {stale}", file=sys.stderr)
    catalog_models = resume_provider_models(plan_dir, config, args.provider)

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
            catalog_models=catalog_models,
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
                catalog_models=catalog_models,
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
            resource_watch.cleanup_artifacts(Path(manifest["repo_root"]), "plan", plan_dir.name)
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
    parser.add_argument(
        "--provider",
        choices=sorted(planctl.VALID_PROVIDERS - {"auto"}),
        help="Override task provider",
    )
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
    except availability.AvailabilityPaused as exc:
        print(f"PAUSED: {exc}", file=sys.stderr)
        return 75
    except (planctl.PlanError, RunnerError, availability.AvailabilityError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
