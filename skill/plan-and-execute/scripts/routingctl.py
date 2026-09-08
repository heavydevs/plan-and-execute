#!/usr/bin/env python3
"""Configure current provider mappings and hard model/effort ceilings for a plan."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

import planctl

TIER_ORDER = ["economy", "standard", "strong", "max"]
EFFORT_ORDER = ["low", "medium", "high", "xhigh", "max"]
MODEL_MAP_VERSION = "2026-09-08"
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
}


class RoutingError(RuntimeError):
    pass


def _index(values: list[str], value: str, field: str) -> int:
    try:
        return values.index(value)
    except ValueError as exc:
        raise RoutingError(f"Invalid {field}: {value!r}; expected one of {values}") from exc


def _cap_effort(value: str, maximum: str) -> str:
    current = _index(EFFORT_ORDER, value, "effort")
    cap = _index(EFFORT_ORDER, maximum, "max effort")
    return EFFORT_ORDER[min(current, cap)]


def configure_config(
    raw: dict[str, Any],
    *,
    max_tier: str | None = None,
    max_effort: str | None = None,
    claude_ceiling_model: str | None = None,
    codex_ceiling_model: str | None = None,
    update_current_models: bool = True,
) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise RoutingError("orchestrator.config.json must contain an object")
    if max_tier is not None:
        _index(TIER_ORDER, max_tier, "max tier")
    if max_effort is not None:
        _index(EFFORT_ORDER, max_effort, "max effort")
    if (claude_ceiling_model or codex_ceiling_model) and max_tier is None:
        raise RoutingError("Provider-specific ceiling models require --max-tier")

    config = copy.deepcopy(raw)
    ceiling_overrides = {
        "claude": claude_ceiling_model,
        "codex": codex_ceiling_model,
    }

    for provider, current_map in CURRENT_MODELS.items():
        provider_cfg = config.setdefault(provider, {})
        if not isinstance(provider_cfg, dict):
            raise RoutingError(f"{provider} config must be an object")
        models = provider_cfg.setdefault("models", {})
        if not isinstance(models, dict):
            raise RoutingError(f"{provider}.models must be an object")

        if update_current_models:
            models.update(current_map)

        if max_tier is not None:
            ceiling_model = ceiling_overrides[provider] or str(models.get(max_tier, "")).strip()
            if not ceiling_model:
                raise RoutingError(f"No ceiling model configured for {provider}/{max_tier}")
            ceiling_index = TIER_ORDER.index(max_tier)
            models[max_tier] = ceiling_model
            # The runner may escalate the logical tier after failures. Collapsing every
            # higher tier to the ceiling model makes the ceiling hard without changing
            # the runner's portable escalation state machine.
            for tier in TIER_ORDER[ceiling_index + 1 :]:
                models[tier] = ceiling_model

        caps = provider_cfg.setdefault("max_effort_by_tier", {})
        if not isinstance(caps, dict):
            raise RoutingError(f"{provider}.max_effort_by_tier must be an object")
        if max_effort is not None:
            for tier in TIER_ORDER:
                existing = str(caps.get(tier, "max")).strip() or "max"
                caps[tier] = _cap_effort(existing, max_effort)

    config["routing_policy"] = {
        "model_map_version": MODEL_MAP_VERSION,
        "max_tier": max_tier,
        "max_effort": max_effort,
        "provider_ceiling_models": {
            key: value for key, value in ceiling_overrides.items() if value
        },
        "hard_ceiling": bool(max_tier or max_effort),
    }
    return config


def configure_plan(
    plan_dir: Path,
    **kwargs: Any,
) -> dict[str, Any]:
    config_path = plan_dir / planctl.CONFIG
    if not config_path.is_file():
        raise RoutingError(f"Plan config not found: {config_path}")
    raw = planctl.read_json(config_path)
    configured = configure_config(raw, **kwargs)
    planctl.atomic_write_json(config_path, configured)
    return configured


def _summary(config: dict[str, Any]) -> dict[str, Any]:
    return {
        "routing_policy": config.get("routing_policy", {}),
        "claude": {
            "models": config.get("claude", {}).get("models", {}),
            "max_effort_by_tier": config.get("claude", {}).get("max_effort_by_tier", {}),
        },
        "codex": {
            "models": config.get("codex", {}).get("models", {}),
            "max_effort_by_tier": config.get("codex", {}).get("max_effort_by_tier", {}),
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    configure = sub.add_parser("configure", help="Apply current model map and optional hard ceiling")
    configure.add_argument("--plan", required=True, type=Path)
    configure.add_argument("--max-tier", choices=TIER_ORDER)
    configure.add_argument("--max-effort", choices=EFFORT_ORDER)
    configure.add_argument("--claude-ceiling-model")
    configure.add_argument("--codex-ceiling-model")
    configure.add_argument(
        "--keep-model-map",
        action="store_true",
        help="Preserve provider model mappings and apply only the requested ceiling",
    )
    configure.add_argument("--json", action="store_true")

    show = sub.add_parser("show", help="Show effective routing configuration")
    show.add_argument("--plan", required=True, type=Path)
    show.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "configure":
            config = configure_plan(
                args.plan,
                max_tier=args.max_tier,
                max_effort=args.max_effort,
                claude_ceiling_model=args.claude_ceiling_model,
                codex_ceiling_model=args.codex_ceiling_model,
                update_current_models=not args.keep_model_map,
            )
        else:
            config_path = args.plan / planctl.CONFIG
            if not config_path.is_file():
                raise RoutingError(f"Plan config not found: {config_path}")
            config = planctl.read_json(config_path)
        summary = _summary(config)
        if getattr(args, "json", False):
            print(json.dumps(summary, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0
    except (RoutingError, planctl.PlanError, OSError, ValueError) as exc:
        print(f"routingctl: {exc}", file=__import__("sys").stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
