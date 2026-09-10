#!/usr/bin/env python3
"""Portable model-family routing for plan-and-execute.

Plans persist provider-neutral capability coordinates (F1..F4 and L1..L5).
Concrete provider/model ids are resolved at execution time from a plan-local
MODEL_MATRIX.json when present, with a conservative built-in catalog only as a
fallback. This keeps durable plans portable across providers and model churn.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

MODEL_MAP_VERSION = "2026-09-10-portable-v1"
MODEL_MATRIX_JSON = "MODEL_MATRIX.json"
MODEL_MATRIX_MD = "MODEL_MATRIX.md"

# Portable model families. Higher F means more model capability/cost budget.
PORTABLE_FAMILY_TO_TIER = {
    "f1": "economy",
    "f2": "standard",
    "f3": "strong",
    "f4": "max",
}
TIER_TO_PORTABLE_FAMILY = {value: key for key, value in PORTABLE_FAMILY_TO_TIER.items()}

# Portable reasoning levels. Higher L means more reasoning/agent effort.
PORTABLE_LEVEL_TO_EFFORT = {
    "l1": "low",
    "l2": "medium",
    "l3": "high",
    "l4": "xhigh",
    "l5": "max",
}
EFFORT_TO_PORTABLE_LEVEL = {value: key for key, value in PORTABLE_LEVEL_TO_EFFORT.items()}

SUPPORTED_RUNTIME_PROVIDERS = (
    "claude",
    "codex",
    "gemini",
    "qwen",
    "muse",
    "kimi",
    "trae",
)

# These are fallbacks, not planning-time truth. New orchestrated plans should
# write a live-researched MODEL_MATRIX.json and the runner will override these.
CURRENT_MODELS: dict[str, dict[str, str]] = {
    "claude": {
        "economy": "haiku",
        "standard": "sonnet",
        "strong": "opus",
        "max": "claude-fable-5-1",
    },
    "codex": {
        "economy": "gpt-5.6-luna",
        "standard": "gpt-5.6-terra",
        "strong": "gpt-5.6-sol",
        "max": "gpt-6-astra",
    },
    # Provider catalogs change quickly; default lets the provider choose when a
    # fresh plan-local matrix was not generated.
    "gemini": {
        "economy": "default",
        "standard": "default",
        "strong": "default",
        "max": "default",
    },
    "qwen": {
        "economy": "default",
        "standard": "default",
        "strong": "default",
        "max": "default",
    },
    "muse": {
        "economy": "muse-spark-1.3",
        "standard": "muse-spark-1.3",
        "strong": "muse-spark-1.3",
        "max": "muse-spark-1.3",
    },
}

# Compatibility guards, not user budget ceilings. Muse currently exposes an
# xhigh route broadly; a live matrix may map L5 to a newer supported value.
CURRENT_EFFORT_CAPS: dict[str, dict[str, str]] = {
    "claude": {
        "economy": "medium",
        "standard": "max",
        "strong": "max",
        "max": "max",
    },
    "codex": {tier: "max" for tier in ("economy", "standard", "strong", "max")},
    "gemini": {tier: "max" for tier in ("economy", "standard", "strong", "max")},
    "qwen": {tier: "max" for tier in ("economy", "standard", "strong", "max")},
    "muse": {tier: "xhigh" for tier in ("economy", "standard", "strong", "max")},
}

PROVIDER_DEFAULTS: dict[str, dict[str, Any]] = {
    "muse": {
        "command": "muse",
        "extra_args": [],
        "disable_approval": True,
        "trust_workspace": True,
        "retry_exit_codes": [],
    }
}


class RoutingError(RuntimeError):
    pass


def _portable_key(value: Any) -> str:
    return str(value or "").strip().lower()


def family_to_tier(value: Any) -> str | None:
    return PORTABLE_FAMILY_TO_TIER.get(_portable_key(value))


def level_to_effort(value: Any) -> str | None:
    return PORTABLE_LEVEL_TO_EFFORT.get(_portable_key(value))


def _normalize_string_map(raw: Any, expected: tuple[str, ...], field: str) -> dict[str, str]:
    if not isinstance(raw, dict):
        raise RoutingError(f"{field} must be an object")
    normalized = {_portable_key(key): str(value).strip() for key, value in raw.items()}
    missing = [key for key in expected if not normalized.get(key)]
    if missing:
        raise RoutingError(f"{field} is missing: {', '.join(key.upper() for key in missing)}")
    return {key: normalized[key] for key in expected}


def validate_model_matrix(raw: Any) -> dict[str, Any]:
    """Validate and normalize a plan-local live model matrix."""
    if not isinstance(raw, dict):
        raise RoutingError("Model matrix must be a JSON object")
    providers_raw = raw.get("providers")
    if not isinstance(providers_raw, dict) or not providers_raw:
        raise RoutingError("Model matrix requires a non-empty providers object")

    researched_at = str(raw.get("researched_at", "")).strip()
    if not researched_at:
        raise RoutingError("Model matrix requires researched_at")
    research_mode = str(raw.get("research_mode", "live")).strip().lower() or "live"
    if research_mode not in {"live", "fallback"}:
        raise RoutingError("research_mode must be live or fallback")

    sources_raw = raw.get("sources", [])
    if not isinstance(sources_raw, list):
        raise RoutingError("sources must be a list")
    sources: list[dict[str, str]] = []
    for index, source in enumerate(sources_raw):
        if isinstance(source, str):
            text = source.strip()
            if not text:
                raise RoutingError(f"sources[{index}] must not be empty")
            sources.append({"label": text, "url": ""})
            continue
        if not isinstance(source, dict):
            raise RoutingError(f"sources[{index}] must be a string or object")
        label = str(source.get("label", "")).strip()
        url = str(source.get("url", "")).strip()
        if not label:
            raise RoutingError(f"sources[{index}].label is required")
        sources.append({"label": label, "url": url})
    if research_mode == "live" and not sources:
        raise RoutingError("A live model matrix requires at least one source")

    providers: dict[str, dict[str, Any]] = {}
    for raw_provider, entry in providers_raw.items():
        provider = _portable_key(raw_provider)
        if provider not in SUPPORTED_RUNTIME_PROVIDERS:
            raise RoutingError(f"Unsupported matrix provider: {provider!r}")
        if not isinstance(entry, dict):
            raise RoutingError(f"providers.{provider} must be an object")
        families = _normalize_string_map(
            entry.get("families"), tuple(PORTABLE_FAMILY_TO_TIER), f"providers.{provider}.families"
        )
        levels = _normalize_string_map(
            entry.get("levels"), tuple(PORTABLE_LEVEL_TO_EFFORT), f"providers.{provider}.levels"
        )
        providers[provider] = {
            "families": families,
            "levels": levels,
            "notes": str(entry.get("notes", "")).strip(),
            "pricing": str(entry.get("pricing", "")).strip(),
            "benchmark": str(entry.get("benchmark", "")).strip(),
        }

    return {
        "version": 1,
        "researched_at": researched_at,
        "research_mode": research_mode,
        "sources": sources,
        "providers": providers,
    }


def load_model_matrix(plan_dir: Any) -> dict[str, Any] | None:
    path = Path(plan_dir) / MODEL_MATRIX_JSON
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RoutingError(f"Invalid {MODEL_MATRIX_JSON}: {exc}") from exc
    return validate_model_matrix(raw)


def apply_model_matrix(config: dict[str, Any], matrix: dict[str, Any]) -> dict[str, Any]:
    """Overlay live plan-local F/L mappings onto provider runtime config."""
    result = copy.deepcopy(config)
    for provider, entry in matrix["providers"].items():
        provider_cfg = result.setdefault(provider, {})
        models = provider_cfg.setdefault("models", {})
        for family, model in entry["families"].items():
            models[PORTABLE_FAMILY_TO_TIER[family]] = model
        provider_cfg["portable_levels"] = dict(entry["levels"])
    result["_portable_model_matrix"] = matrix
    policy = result.setdefault("routing_policy", {})
    policy["model_matrix_file"] = MODEL_MATRIX_JSON
    policy["model_matrix_human_file"] = MODEL_MATRIX_MD
    policy["model_matrix_researched_at"] = matrix["researched_at"]
    return result


def configure_config(raw: dict[str, Any]) -> dict[str, Any]:
    """Return config with portable providers and conservative fallbacks applied."""
    if not isinstance(raw, dict):
        raise RoutingError("orchestrator.config.json must contain an object")

    config = copy.deepcopy(raw)
    for provider, defaults in PROVIDER_DEFAULTS.items():
        provider_cfg = config.setdefault(provider, {})
        if not isinstance(provider_cfg, dict):
            raise RoutingError(f"{provider} config must be an object")
        for key, value in defaults.items():
            provider_cfg.setdefault(key, copy.deepcopy(value))

    for provider, model_map in CURRENT_MODELS.items():
        provider_cfg = config.setdefault(provider, {})
        if not isinstance(provider_cfg, dict):
            raise RoutingError(f"{provider} config must be an object")
        models = provider_cfg.setdefault("models", {})
        if not isinstance(models, dict):
            raise RoutingError(f"{provider}.models must be an object")
        models.update(model_map)

        caps = provider_cfg.setdefault("max_effort_by_tier", {})
        if not isinstance(caps, dict):
            raise RoutingError(f"{provider}.max_effort_by_tier must be an object")
        caps.update(CURRENT_EFFORT_CAPS[provider])

    order = [str(item) for item in config.get("provider_order", []) if str(item).strip()]
    for provider in SUPPORTED_RUNTIME_PROVIDERS:
        if provider not in order:
            order.append(provider)
    config["provider_order"] = order

    # Replaces legacy routing-policy state, including retired ceiling data.
    config["routing_policy"] = {
        "model_map_version": MODEL_MAP_VERSION,
        "selection": "adaptive-portable",
        "portable_model_families": "F1-F4",
        "portable_reasoning_levels": "L1-L5",
        "model_matrix_file": MODEL_MATRIX_JSON,
        "model_matrix_human_file": MODEL_MATRIX_MD,
    }
    return config


def install_current_model_catalog(planctl_module: Any) -> Any:
    """Install portable plan vocabulary and fallback catalog on plan controllers."""
    if getattr(planctl_module, "_current_model_catalog_installed", False):
        return planctl_module

    planctl_module.VALID_PROVIDERS.add("muse")
    planctl_module.VALID_TIERS.update(PORTABLE_FAMILY_TO_TIER)
    planctl_module.VALID_EFFORTS.update(PORTABLE_LEVEL_TO_EFFORT)

    original_default_config = planctl_module.default_config

    def current_default_config() -> dict[str, Any]:
        return configure_config(original_default_config())

    planctl_module.default_config = current_default_config
    planctl_module._current_model_catalog_installed = True
    return planctl_module


def _portable_task_for_legacy_runner(task: dict[str, Any]) -> dict[str, Any]:
    translated = copy.deepcopy(task)
    tier = family_to_tier(task.get("model_tier"))
    effort = level_to_effort(task.get("reasoning_effort"))
    if tier:
        translated["model_tier"] = tier
    if effort:
        translated["reasoning_effort"] = effort
    # New plans intentionally remain provider-neutral.
    if _portable_key(task.get("model_tier")) in PORTABLE_FAMILY_TO_TIER:
        translated["provider"] = "auto"
    return translated


def install_runtime_model_catalog(run_module: Any) -> Any:
    """Resolve portable F/L routes against the current plan-local provider matrix."""
    if getattr(run_module, "_current_model_catalog_installed", False):
        return run_module

    original_load_config = run_module.load_config
    original_choose_route = run_module.choose_route
    original_build_worker_command = run_module.build_worker_command
    original_build_summary_command = run_module.build_summary_command

    def current_load_config(plan_dir: Any) -> dict[str, Any]:
        config = configure_config(original_load_config(plan_dir))
        matrix = load_model_matrix(plan_dir)
        return apply_model_matrix(config, matrix) if matrix else config

    def current_choose_route(
        task: dict[str, Any], config: dict[str, Any], override: str | None
    ) -> dict[str, str]:
        route = original_choose_route(_portable_task_for_legacy_runner(task), config, override)
        family = TIER_TO_PORTABLE_FAMILY.get(route.get("tier", ""))
        level = EFFORT_TO_PORTABLE_LEVEL.get(route.get("effort", ""))
        provider_cfg = config.get(route["provider"], {})
        if family:
            # A live matrix has already overlaid the provider's model map into
            # the legacy tier key used by the base runner.
            route["family"] = family.upper()
        if level:
            native = provider_cfg.get("portable_levels", {}).get(level)
            if native and native != "default":
                route["effort"] = str(native)
            route["level"] = level.upper()
        return route

    def muse_command(
        route: dict[str, str], config: dict[str, Any], prompt: str, *, read_only: bool
    ) -> list[str]:
        provider_cfg = config["muse"]
        prefix = run_module.command_prefix(provider_cfg.get("command", "muse"))
        extra_args = provider_cfg.get("extra_args", [])
        if not isinstance(extra_args, list) or not all(isinstance(item, str) for item in extra_args):
            raise run_module.RunnerError("muse.extra_args must be a list of strings")
        command = prefix + ["exec", "--json"]
        if provider_cfg.get("trust_workspace", True):
            command.append("--trust-workspace")
        if read_only:
            command.append("--disable-write")
        elif provider_cfg.get("disable_approval", True):
            # Keep Muse's sandbox active while avoiding an interactive approval
            # prompt inside this already-isolated headless worker process.
            command.append("--disable-approval")
        command.extend(run_module.configured_model_args("--model", route["model"]))
        effort = str(route.get("effort", "")).strip()
        if effort and effort != "default":
            command.extend(["--reasoning-effort", effort])
        command.extend(extra_args)
        command.append(prompt)
        return command

    def current_build_worker_command(
        provider: str,
        route: dict[str, str],
        config: dict[str, Any],
        prompt: str,
        result_path: Any,
    ) -> list[str]:
        if provider == "muse":
            return muse_command(route, config, prompt, read_only=False)
        return original_build_worker_command(provider, route, config, prompt, result_path)

    def current_build_summary_command(
        provider: str,
        route: dict[str, str],
        config: dict[str, Any],
        prompt: str,
        output_path: Any,
    ) -> list[str]:
        if provider == "muse":
            return muse_command(route, config, prompt, read_only=True)
        return original_build_summary_command(provider, route, config, prompt, output_path)

    run_module.load_config = current_load_config
    run_module.choose_route = current_choose_route
    run_module.build_worker_command = current_build_worker_command
    run_module.build_summary_command = current_build_summary_command
    run_module._current_model_catalog_installed = True
    return run_module
