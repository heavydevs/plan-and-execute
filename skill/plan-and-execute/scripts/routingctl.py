#!/usr/bin/env python3
"""Portable F/L model routing for plan-and-execute.

Plans persist provider-neutral model requirements:
- F1..F4 describe the required model-family capability.
- L1..L5 describe the required reasoning level inside that family.

Concrete provider/model/effort bindings live in MODEL_COMPATIBILITY.json/.md,
which the planning agent must build from current provider/CLI documentation.
Legacy tier/effort plans remain readable for backwards compatibility.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

PORTABLE_ROUTING_VERSION = "fl-v1"
MODEL_COMPATIBILITY_JSON = "MODEL_COMPATIBILITY.json"
MODEL_COMPATIBILITY_MD = "MODEL_COMPATIBILITY.md"

FAMILY_ORDER = ("F1", "F2", "F3", "F4")
LEVEL_ORDER = ("L1", "L2", "L3", "L4", "L5")
FAMILY_TO_TIER = {
    "F1": "economy",
    "F2": "standard",
    "F3": "strong",
    "F4": "max",
}
TIER_TO_FAMILY = {value: key for key, value in FAMILY_TO_TIER.items()}
LEVEL_TO_EFFORT = {
    "L1": "low",
    "L2": "medium",
    "L3": "high",
    "L4": "xhigh",
    "L5": "max",
}
EFFORT_TO_LEVEL = {value: key for key, value in LEVEL_TO_EFFORT.items()}

PORTABLE_PROVIDERS = ("codex", "claude", "gemini", "qwen", "muse")


class RoutingError(RuntimeError):
    pass


def _require_code(value: Any, allowed: tuple[str, ...], field: str) -> str:
    code = str(value or "").strip().upper()
    if code not in allowed:
        raise RoutingError(f"{field} must be one of {list(allowed)}, got {value!r}")
    return code


def _str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise RoutingError(f"{field} must be a non-empty list")
    result: list[str] = []
    for item in value:
        text = str(item or "").strip()
        if not text:
            raise RoutingError(f"{field} entries must be non-empty strings")
        result.append(text)
    return result


def normalize_compatibility(raw: Any) -> dict[str, Any]:
    """Validate/canonicalize a planner-produced live compatibility matrix."""
    if not isinstance(raw, dict):
        raise RoutingError(
            "model_compatibility is required for portable F/L plans and must be an object"
        )
    generated_at = str(raw.get("generated_at", "")).strip()
    if not generated_at:
        raise RoutingError("model_compatibility.generated_at is required")
    discovery = str(raw.get("discovery", "")).strip()
    if not discovery:
        raise RoutingError(
            "model_compatibility.discovery must summarize the live CLI/vendor-doc lookup"
        )
    providers_raw = raw.get("providers")
    if not isinstance(providers_raw, dict):
        raise RoutingError("model_compatibility.providers must be an object")

    missing = [provider for provider in PORTABLE_PROVIDERS if provider not in providers_raw]
    if missing:
        raise RoutingError(
            "model_compatibility must cover all portable providers: " + ", ".join(missing)
        )

    providers: dict[str, Any] = {}
    for provider in PORTABLE_PROVIDERS:
        value = providers_raw[provider]
        if not isinstance(value, dict):
            raise RoutingError(f"model_compatibility.providers.{provider} must be an object")
        checked_at = str(value.get("checked_at", generated_at)).strip()
        if not checked_at:
            raise RoutingError(
                f"model_compatibility.providers.{provider}.checked_at is required"
            )
        sources = _str_list(
            value.get("sources"),
            f"model_compatibility.providers.{provider}.sources",
        )
        families_raw = value.get("families")
        if not isinstance(families_raw, dict):
            raise RoutingError(
                f"model_compatibility.providers.{provider}.families must be an object"
            )
        families: dict[str, Any] = {}
        for family in FAMILY_ORDER:
            entry = families_raw.get(family)
            if not isinstance(entry, dict):
                raise RoutingError(
                    f"model_compatibility.providers.{provider}.families.{family} "
                    "must map the portable family to a current concrete model"
                )
            model = str(entry.get("model", "")).strip()
            if not model:
                raise RoutingError(
                    f"model_compatibility.providers.{provider}.families.{family}.model "
                    "must be non-empty"
                )
            levels_raw = entry.get("levels")
            if not isinstance(levels_raw, dict):
                raise RoutingError(
                    f"model_compatibility.providers.{provider}.families.{family}.levels "
                    "must be an object"
                )
            levels: dict[str, str] = {}
            for level in LEVEL_ORDER:
                native = str(levels_raw.get(level, "")).strip()
                if not native:
                    raise RoutingError(
                        f"{provider}/{family} must explicitly map {level}; "
                        "repeat/clamp the nearest supported native level when the provider "
                        "has fewer than five levels"
                    )
                levels[level] = native
            families[family] = {
                "model": model,
                "levels": levels,
            }
            note = str(entry.get("note", "")).strip()
            if note:
                families[family]["note"] = note
        providers[provider] = {
            "checked_at": checked_at,
            "sources": sources,
            "families": families,
        }
        display_name = str(value.get("display_name", "")).strip()
        if display_name:
            providers[provider]["display_name"] = display_name

    return {
        "schema_version": 1,
        "routing": PORTABLE_ROUTING_VERSION,
        "generated_at": generated_at,
        "discovery": discovery,
        "providers": providers,
    }


def render_compatibility_markdown(compatibility: dict[str, Any]) -> str:
    lines = [
        "# Model compatibility",
        "",
        (
            "This file is the concrete, replaceable binding for the portable F/L plan. "
            "TODOs must depend only on F1-F4 and L1-L5; do not copy concrete model ids "
            "back into task definitions."
        ),
        "",
        f"- Routing schema: `{PORTABLE_ROUTING_VERSION}`",
        f"- Generated/checked: `{compatibility['generated_at']}`",
        f"- Discovery: {compatibility['discovery']}",
        (
            "- Refresh rule: re-check the active provider/CLI and authoritative current "
            "provider documentation when planning, when changing provider, or when a "
            "recorded model/level is unavailable."
        ),
        "",
        "## Portable scale",
        "",
        "| Code | Meaning |",
        "|---|---|",
        "| `F1` | Economy/fast family for exploration and mechanical work |",
        "| `F2` | General coding family for ordinary bounded implementation |",
        "| `F3` | Strong family for difficult, subtle, or weakly verifiable work |",
        "| `F4` | Frontier family for long-horizon/high-risk escalation |",
        "| `L1` | Lowest supported reasoning/power level for the selected model |",
        "| `L2` | Low-to-medium reasoning level |",
        "| `L3` | Strong reasoning level |",
        "| `L4` | Extra-high reasoning level |",
        "| `L5` | Highest supported reasoning/power level; clamp when unavailable |",
        "",
        "## Current provider bindings",
        "",
        "| Provider | Family | Current model | L1 | L2 | L3 | L4 | L5 | Checked |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for provider in PORTABLE_PROVIDERS:
        data = compatibility["providers"][provider]
        name = data.get("display_name", provider)
        for family in FAMILY_ORDER:
            entry = data["families"][family]
            lv = entry["levels"]
            lines.append(
                f"| {name} | `{family}` | `{entry['model']}` | "
                f"`{lv['L1']}` | `{lv['L2']}` | `{lv['L3']}` | "
                f"`{lv['L4']}` | `{lv['L5']}` | `{data['checked_at']}` |"
            )
    lines.extend(["", "## Sources", ""])
    for provider in PORTABLE_PROVIDERS:
        data = compatibility["providers"][provider]
        lines.append(f"### {data.get('display_name', provider)}")
        lines.append("")
        lines.extend(f"- {source}" for source in data["sources"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _portable_task(raw: Any) -> bool:
    return isinstance(raw, dict) and (
        "model_family" in raw or "model_level" in raw
    )


def _manifest_is_portable(manifest: Any) -> bool:
    if not isinstance(manifest, dict):
        return False
    return any(
        isinstance(task, dict) and "model_family" in task
        for task in manifest.get("tasks", [])
    )


def configure_config(raw: dict[str, Any]) -> dict[str, Any]:
    """Add provider adapters/policy without imposing a stale concrete model catalog."""
    if not isinstance(raw, dict):
        raise RoutingError("orchestrator.config.json must contain an object")
    config = copy.deepcopy(raw)

    config.setdefault(
        "muse",
        {
            "command": "muse",
            "models": {tier: "default" for tier in ("economy", "standard", "strong", "max")},
            "approval_mode": "never",
            "max_effort_by_tier": {
                "economy": "medium",
                "standard": "high",
                "strong": "xhigh",
                "max": "max",
            },
            "extra_args": [],
        },
    )
    order = [str(item) for item in config.get("provider_order", [])]
    for provider in ("claude", "codex", "gemini", "qwen", "muse", "kimi", "trae"):
        if provider not in order and provider in config:
            order.append(provider)
    config["provider_order"] = order
    config["routing_policy"] = {
        "schema": PORTABLE_ROUTING_VERSION,
        "selection": "portable-family-level",
        "concrete_binding": MODEL_COMPATIBILITY_JSON,
    }
    return config


def _render_task_with_portable_route(
    original_render: Any,
    task: dict[str, Any],
    plan_id: str,
    work_root: str,
) -> str:
    if "model_family" not in task:
        return original_render(task, plan_id, work_root)

    synthetic = copy.deepcopy(task)
    family = _require_code(task.get("model_family"), FAMILY_ORDER, "model_family")
    level = _require_code(task.get("model_level"), LEVEL_ORDER, "model_level")
    synthetic["provider"] = "auto"
    synthetic["model_tier"] = FAMILY_TO_TIER[family]
    synthetic["reasoning_effort"] = LEVEL_TO_EFFORT[level]
    text = original_render(synthetic, plan_id, work_root)
    new = (
        f'model_family: "{family}"\n'
        f'model_level: "{level}"\n'
        f'model_compatibility_file: "{MODEL_COMPATIBILITY_MD}"\n'
    )
    # The concise renderer intentionally omits routing metadata. Insert the
    # portable contract after status. The legacy renderer is also supported.
    legacy = (
        'provider: "auto"\n'
        f'model_tier: "{FAMILY_TO_TIER[family]}"\n'
        f'reasoning_effort: "{LEVEL_TO_EFFORT[level]}"\n'
    )
    if legacy in text:
        text = text.replace(legacy, new, 1)
    else:
        status_line = f'status: "{task["status"]}"\n'
        text = text.replace(status_line, status_line + new, 1)
    reference = (Path(work_root) / plan_id / MODEL_COMPATIBILITY_MD).as_posix()
    marker = "## Isolation contract\n\n"
    portable_rule = (
        f"Portable model requirement: **{family}/{level}**. Concrete provider/model "
        f"bindings are external to this TODO and live in `{reference}`. The orchestrator "
        "must resolve or refresh that table before dispatch; do not pin a provider or "
        "concrete model in this task.\n\n"
    )
    return text.replace(marker, marker + portable_rule, 1)


def _render_plan_with_portable_route(original_render: Any, manifest: dict[str, Any]) -> str:
    text = original_render(manifest)
    if not _manifest_is_portable(manifest):
        return text
    reference = (
        Path(str(manifest.get("work_root", ".ai-work")))
        / str(manifest.get("plan_id", ""))
        / MODEL_COMPATIBILITY_MD
    ).as_posix()
    section = (
        "\n## Portable model-routing contract\n\n"
        "- TODOs declare only portable `F1`-`F4` model families and `L1`-`L5` "
        "reasoning levels.\n"
        f"- Concrete current mappings live in `{reference}` and may be refreshed "
        "without changing the TODO graph.\n"
        "- Changing Codex/Claude/Gemini/Qwen/Muse is a route resolution operation, "
        "not a replan, unless execution evidence changes the task itself.\n"
    )
    return text.rstrip() + "\n" + section


def install_current_model_catalog(planctl_module: Any) -> Any:
    """Install portable planning semantics on the concise plan controller."""
    if getattr(planctl_module, "_portable_fl_routing_installed", False):
        return planctl_module

    planctl_module.VALID_PROVIDERS = set(planctl_module.VALID_PROVIDERS) | {"muse"}

    original_default_config = planctl_module.default_config
    original_normalize_task = planctl_module.normalize_task
    original_render_task = planctl_module.render_task
    original_render_plan = planctl_module.render_plan
    original_create_plan = planctl_module.create_plan
    original_validate_plan = planctl_module.validate_plan

    def current_default_config() -> dict[str, Any]:
        return configure_config(original_default_config())

    def normalize_task(raw: Any, index: int, known_requirement_ids: set[str]) -> dict[str, Any]:
        if not _portable_task(raw):
            return original_normalize_task(raw, index, known_requirement_ids)
        if not isinstance(raw, dict):
            return original_normalize_task(raw, index, known_requirement_ids)

        forbidden = [
            key for key in ("provider", "model_tier", "reasoning_effort")
            if key in raw
        ]
        if forbidden:
            raise planctl_module.PlanError(
                "Portable F/L tasks must not pin legacy routing fields: "
                + ", ".join(forbidden)
            )
        try:
            family = _require_code(raw.get("model_family"), FAMILY_ORDER, "model_family")
            level = _require_code(raw.get("model_level"), LEVEL_ORDER, "model_level")
        except RoutingError as exc:
            raise planctl_module.PlanError(str(exc)) from exc

        translated = dict(raw)
        translated["provider"] = "auto"
        translated["model_tier"] = FAMILY_TO_TIER[family]
        translated["reasoning_effort"] = LEVEL_TO_EFFORT[level]
        task = original_normalize_task(translated, index, known_requirement_ids)
        task.pop("provider", None)
        task.pop("model_tier", None)
        task.pop("reasoning_effort", None)
        task["model_family"] = family
        task["model_level"] = level
        task["model_compatibility_file"] = MODEL_COMPATIBILITY_MD
        return task

    def render_task(task: dict[str, Any], plan_id: str, work_root: str = ".ai-work") -> str:
        return _render_task_with_portable_route(
            original_render_task, task, plan_id, work_root
        )

    def render_plan(manifest: dict[str, Any]) -> str:
        return _render_plan_with_portable_route(original_render_plan, manifest)

    def validate_plan(plan_dir: Path, manifest: dict[str, Any] | None = None) -> list[str]:
        errors = original_validate_plan(plan_dir, manifest)
        if manifest is None:
            try:
                _plan_dir, manifest = planctl_module.load_plan(plan_dir)
            except Exception:
                return errors
        if not _manifest_is_portable(manifest):
            return errors

        json_path = Path(plan_dir) / MODEL_COMPATIBILITY_JSON
        md_path = Path(plan_dir) / MODEL_COMPATIBILITY_MD
        if not json_path.is_file():
            errors.append(f"Missing {MODEL_COMPATIBILITY_JSON} for portable F/L plan")
            return errors
        if not md_path.is_file():
            errors.append(f"Missing {MODEL_COMPATIBILITY_MD} for portable F/L plan")
            return errors
        try:
            compatibility = normalize_compatibility(
                planctl_module.read_json(json_path)
            )
        except Exception as exc:
            errors.append(f"Invalid {MODEL_COMPATIBILITY_JSON}: {exc}")
            return errors
        try:
            if md_path.read_text(encoding="utf-8") != render_compatibility_markdown(compatibility):
                errors.append(
                    f"{MODEL_COMPATIBILITY_MD} does not match {MODEL_COMPATIBILITY_JSON}"
                )
        except OSError as exc:
            errors.append(f"Cannot read {MODEL_COMPATIBILITY_MD}: {exc}")

        if manifest.get("routing_schema") != PORTABLE_ROUTING_VERSION:
            errors.append(
                f"manifest routing_schema must be {PORTABLE_ROUTING_VERSION!r}"
            )
        if manifest.get("model_compatibility_file") != MODEL_COMPATIBILITY_MD:
            errors.append(
                f"manifest model_compatibility_file must be {MODEL_COMPATIBILITY_MD!r}"
            )
        for task in manifest.get("tasks", []):
            task_id = task.get("id", "?")
            try:
                _require_code(task.get("model_family"), FAMILY_ORDER, f"Task {task_id} model_family")
                _require_code(task.get("model_level"), LEVEL_ORDER, f"Task {task_id} model_level")
            except RoutingError as exc:
                errors.append(str(exc))
            for forbidden in ("provider", "model_tier", "reasoning_effort"):
                if forbidden in task:
                    errors.append(
                        f"Task {task_id}: portable manifest must not persist {forbidden}"
                    )
        return errors

    def create_plan(
        repo_root: Path,
        spec: dict[str, Any],
        work_root: str,
        plan_id: str | None,
        request_file: str | Path | None = None,
        move_request: bool = False,
    ) -> Path:
        raw_tasks = spec.get("tasks", []) if isinstance(spec, dict) else []
        portable = any(_portable_task(task) for task in raw_tasks if isinstance(task, dict))
        if not portable:
            return original_create_plan(
                repo_root, spec, work_root, plan_id, request_file, move_request
            )
        if any(
            isinstance(task, dict) and not _portable_task(task)
            for task in raw_tasks
        ):
            raise planctl_module.PlanError(
                "Do not mix portable F/L tasks and legacy provider/tier tasks in one plan"
            )
        try:
            compatibility = normalize_compatibility(spec.get("model_compatibility"))
        except RoutingError as exc:
            raise planctl_module.PlanError(str(exc)) from exc

        # The legacy creator performs an internal validation before this wrapper
        # can write the compatibility artifact. Use the original validator only
        # for that creation transaction, then enforce the portable validator.
        installed_validate = planctl_module.validate_plan
        planctl_module.validate_plan = original_validate_plan
        try:
            plan_dir = original_create_plan(
                repo_root, spec, work_root, plan_id, request_file, move_request
            )
        finally:
            planctl_module.validate_plan = installed_validate

        manifest = planctl_module.read_json(plan_dir / planctl_module.MANIFEST)
        manifest["routing_schema"] = PORTABLE_ROUTING_VERSION
        manifest["model_compatibility_file"] = MODEL_COMPATIBILITY_MD
        manifest["model_compatibility_data_file"] = MODEL_COMPATIBILITY_JSON
        manifest["model_compatibility_generated_at"] = compatibility["generated_at"]
        planctl_module.atomic_write_json(
            plan_dir / MODEL_COMPATIBILITY_JSON, compatibility
        )
        planctl_module.atomic_write_text(
            plan_dir / MODEL_COMPATIBILITY_MD,
            render_compatibility_markdown(compatibility),
        )
        planctl_module.save_manifest(plan_dir, manifest)
        planctl_module.atomic_write_text(
            plan_dir / "PLAN.md", render_plan(manifest)
        )
        errors = validate_plan(plan_dir, manifest)
        if errors:
            raise planctl_module.PlanError(
                "Portable plan validation failed after creation:\n- "
                + "\n- ".join(errors)
            )
        return plan_dir

    planctl_module.default_config = current_default_config
    planctl_module.normalize_task = normalize_task
    planctl_module.render_task = render_task
    planctl_module.render_plan = render_plan
    planctl_module.create_plan = create_plan
    planctl_module.validate_plan = validate_plan
    planctl_module._portable_fl_routing_installed = True
    return planctl_module


def _load_plan_compatibility(plan_dir: Any) -> dict[str, Any] | None:
    path = Path(plan_dir) / MODEL_COMPATIBILITY_JSON
    if not path.is_file():
        return None
    try:
        return normalize_compatibility(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError, RoutingError) as exc:
        raise RoutingError(f"Cannot load {MODEL_COMPATIBILITY_JSON}: {exc}") from exc


def install_runtime_model_catalog(run_module: Any) -> Any:
    """Resolve portable F/L tasks against the plan's current compatibility file."""
    if getattr(run_module, "_portable_fl_routing_installed", False):
        return run_module

    original_load_config = run_module.load_config
    original_choose_route = run_module.choose_route
    original_build_worker_command = run_module.build_worker_command
    original_build_summary_command = run_module.build_summary_command

    def current_load_config(plan_dir: Any) -> dict[str, Any]:
        config = configure_config(original_load_config(plan_dir))
        compatibility = _load_plan_compatibility(plan_dir)
        if compatibility is None:
            return config
        config["_portable_model_compatibility"] = compatibility
        for provider, provider_data in compatibility["providers"].items():
            provider_cfg = config.setdefault(provider, {})
            models = provider_cfg.setdefault("models", {})
            for family, tier in FAMILY_TO_TIER.items():
                models[tier] = provider_data["families"][family]["model"]
        return config

    def choose_route(
        task: dict[str, Any],
        config: dict[str, Any],
        override: str | None,
    ) -> dict[str, str]:
        if "model_family" not in task:
            return original_choose_route(task, config, override)
        compatibility = config.get("_portable_model_compatibility")
        if not isinstance(compatibility, dict):
            raise run_module.RunnerError(
                f"Portable task requires {MODEL_COMPATIBILITY_JSON}; "
                "refresh the current provider/model table before execution"
            )
        try:
            family = _require_code(task.get("model_family"), FAMILY_ORDER, "model_family")
            level = _require_code(task.get("model_level"), LEVEL_ORDER, "model_level")
        except RoutingError as exc:
            raise run_module.RunnerError(str(exc)) from exc

        synthetic = dict(task)
        synthetic["provider"] = "auto"
        synthetic["model_tier"] = FAMILY_TO_TIER[family]
        synthetic["reasoning_effort"] = LEVEL_TO_EFFORT[level]
        route = original_choose_route(synthetic, config, override)

        resolved_family = TIER_TO_FAMILY.get(route["tier"], family)
        resolved_level = EFFORT_TO_LEVEL.get(route["effort"], level)
        provider = route["provider"]
        try:
            entry = compatibility["providers"][provider]["families"][resolved_family]
            model = entry["model"]
            native_effort = entry["levels"][resolved_level]
        except (KeyError, TypeError) as exc:
            raise run_module.RunnerError(
                f"No current F/L binding for {provider} {resolved_family}/{resolved_level}; "
                f"refresh {MODEL_COMPATIBILITY_JSON} before retrying"
            ) from exc
        return {
            "provider": provider,
            "tier": route["tier"],
            "model": str(model),
            "effort": str(native_effort),
            "family": resolved_family,
            "level": resolved_level,
        }

    def build_worker_command(
        provider: str,
        route: dict[str, str],
        config: dict[str, Any],
        prompt: str,
        result_path: Path,
    ) -> list[str]:
        if provider != "muse":
            return original_build_worker_command(
                provider, route, config, prompt, result_path
            )
        provider_cfg = config[provider]
        prefix = run_module.command_prefix(provider_cfg.get("command", "muse"))
        command = prefix + ["exec", "--json"]
        approval_mode = str(provider_cfg.get("approval_mode", "never")).strip()
        if approval_mode:
            command.extend(["--approval-mode", approval_mode])
        command.extend(run_module.configured_model_args("--model", route["model"]))
        if route.get("effort") and route["effort"] != "default":
            command.extend(["--reasoning-effort", route["effort"]])
        extra_args = provider_cfg.get("extra_args", [])
        if not isinstance(extra_args, list) or not all(isinstance(item, str) for item in extra_args):
            raise run_module.RunnerError("muse.extra_args must be a list of strings")
        command.extend(extra_args)
        command.append(prompt)
        return command

    def build_summary_command(
        provider: str,
        route: dict[str, str],
        config: dict[str, Any],
        prompt: str,
        output_path: Path,
    ) -> list[str]:
        if provider != "muse":
            return original_build_summary_command(
                provider, route, config, prompt, output_path
            )
        provider_cfg = config[provider]
        prefix = run_module.command_prefix(provider_cfg.get("command", "muse"))
        command = prefix + ["exec", "--json", "--disable-write"]
        command.extend(run_module.configured_model_args("--model", route["model"]))
        if route.get("effort") and route["effort"] != "default":
            command.extend(["--reasoning-effort", route["effort"]])
        extra_args = provider_cfg.get("extra_args", [])
        if not isinstance(extra_args, list) or not all(isinstance(item, str) for item in extra_args):
            raise run_module.RunnerError("muse.extra_args must be a list of strings")
        command.extend(extra_args)
        command.append(prompt)
        return command

    run_module.load_config = current_load_config
    run_module.choose_route = choose_route
    run_module.build_worker_command = build_worker_command
    run_module.build_summary_command = build_summary_command
    run_module._portable_fl_routing_installed = True
    return run_module
