#!/usr/bin/env python3
"""Current provider model catalog and evidence-based escalation ladders.

The skill chooses routes from task semantics and evidence. This module is the
single source of truth for concrete provider model ids, provider compatibility
guards (effort caps, models that accept no effort flag), and the ordered
escalation rungs the runner climbs from failure evidence. It does not impose
user budget ceilings or choose a route for the agent.
"""
from __future__ import annotations

import copy
from typing import Any

MODEL_MAP_VERSION = "2026-09-11-v3"

TIER_ORDER = ["economy", "standard", "strong", "max"]
EFFORT_ORDER = ["low", "medium", "high", "xhigh", "max"]

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
        # Astra low/medium supersedes Sol-high as the default hard-work family.
        # Keep effort separate from model tier so the agent can spend only the
        # reasoning depth justified by verifiability, risk, and failure evidence.
        "strong": "gpt-6-astra",
        "max": "gpt-6-astra",
    },
}

# Provider/model compatibility guards, not user budget ceilings.
CURRENT_EFFORT_CAPS: dict[str, dict[str, str]] = {
    "claude": {
        "economy": "medium",
        "standard": "max",
        "strong": "max",
        "max": "max",
    },
    "codex": {
        "economy": "max",
        "standard": "max",
        "strong": "max",
        "max": "max",
    },
}

# Models that reject or ignore an effort/reasoning parameter. The runner omits
# the flag for them instead of failing the dispatch.
MODELS_WITHOUT_EFFORT: dict[str, list[str]] = {
    "claude": ["haiku"],
    "codex": [],
}

# Ordered (tier, effort) rungs climbed from failure evidence. Rungs are chosen
# by verified cost per solved task, not price per token:
# - Claude: Haiku accepts no effort, so an economy failure moves straight to
#   Sonnet; Opus Medium is a valid first strong rung when validation is strong.
# - Codex: Astra Low dominates Terra High (OpenAI calibration), so the ladder
#   never spends a Terra High retry before an Astra Low attempt.
ESCALATION_LADDERS: dict[str, list[list[str]]] = {
    "claude": [
        ["economy", "low"],
        ["standard", "medium"],
        ["standard", "high"],
        ["strong", "medium"],
        ["strong", "high"],
        ["max", "high"],
        ["max", "xhigh"],
    ],
    "codex": [
        ["economy", "low"],
        ["economy", "medium"],
        ["standard", "medium"],
        ["strong", "low"],
        ["strong", "medium"],
        ["strong", "high"],
        ["max", "xhigh"],
    ],
}

# Generic ladder for optional providers whose catalog is user-configured.
DEFAULT_LADDER: list[list[str]] = [
    ["economy", "low"],
    ["standard", "medium"],
    ["standard", "high"],
    ["strong", "medium"],
    ["strong", "high"],
    ["max", "high"],
    ["max", "xhigh"],
]

# Failure classes a worker/orchestrator may record. Each class changes the next
# route differently; see `escalation_step`.
FAILURE_CLASSES = (
    "mechanical",      # detail/tool/test slip at an adequate capability: retry same rung, then +1
    "semantic",        # wrong understanding or reasoning gap: jump to the next stronger tier
    "environmental",   # toolchain/repository issue outside the worker's control: no route change
    "budget",          # turn/token budget exhausted: retry same rung, then +1
    "plan_defect",     # task boundary/requirement/dependency is wrong: block and replan
    "unknown",         # unclassified failure (no report, invalid report, non-zero exit): +1 rung
)


class RoutingError(RuntimeError):
    pass


def _index(values: list[str], value: str) -> int:
    try:
        return values.index(value)
    except ValueError:
        return 0


def configure_config(raw: dict[str, Any]) -> dict[str, Any]:
    """Return config with the current adaptive model catalog applied."""
    if not isinstance(raw, dict):
        raise RoutingError("orchestrator.config.json must contain an object")

    config = copy.deepcopy(raw)
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

        provider_cfg["models_without_effort"] = list(MODELS_WITHOUT_EFFORT[provider])
        provider_cfg["escalation_ladder"] = [list(rung) for rung in ESCALATION_LADDERS[provider]]

    # Replaces legacy routing-policy state, including any retired ceiling data.
    config["routing_policy"] = {
        "model_map_version": MODEL_MAP_VERSION,
        "selection": "adaptive",
        "escalation": "evidence",
    }
    return config


def model_supports_effort(provider_cfg: dict[str, Any], model: str) -> bool:
    """False when the concrete model rejects an effort/reasoning parameter."""
    blocked = provider_cfg.get("models_without_effort", [])
    if not isinstance(blocked, list):
        return True
    name = str(model or "").strip().lower()
    for item in blocked:
        token = str(item).strip().lower()
        if token and (name == token or name.startswith(token + "-")):
            return False
    return True


def provider_ladder(provider_cfg: dict[str, Any]) -> list[tuple[str, str]]:
    raw = provider_cfg.get("escalation_ladder")
    rungs: list[tuple[str, str]] = []
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                tier, effort = str(item[0]), str(item[1])
                if tier in TIER_ORDER and effort in EFFORT_ORDER:
                    rungs.append((tier, effort))
    return rungs or [tuple(rung) for rung in DEFAULT_LADDER]  # type: ignore[misc]


def _above(rung: tuple[str, str], base: tuple[str, str]) -> bool:
    tier_delta = _index(TIER_ORDER, rung[0]) - _index(TIER_ORDER, base[0])
    if tier_delta != 0:
        return tier_delta > 0
    return _index(EFFORT_ORDER, rung[1]) > _index(EFFORT_ORDER, base[1])


def route_rungs(provider_cfg: dict[str, Any], tier: str, effort: str) -> list[tuple[str, str]]:
    """Declared route first, then every ladder rung strictly above it."""
    base = (tier if tier in TIER_ORDER else "standard", effort if effort in EFFORT_ORDER else "medium")
    return [base] + [rung for rung in provider_ladder(provider_cfg) if _above(rung, base)]


def escalation_step(failure_classes: list[str], rungs: list[tuple[str, str]]) -> int:
    """Translate recorded failure evidence into a ladder position.

    mechanical/budget: the first failure at a rung repeats it; the second moves +1.
    semantic: jump to the first rung with a stronger tier than the current one.
    environmental: no route change.
    unknown: +1 rung (legacy count-based behaviour).
    plan_defect: no route change (the task is blocked for replanning instead).
    """
    top = max(0, len(rungs) - 1)
    return min(_uncapped_step(failure_classes, rungs), top)


def escalation_exhausted(failure_classes: list[str], rungs: list[tuple[str, str]]) -> bool:
    """True once the evidence asks for a rung above the ladder's top.

    The runner then blocks the task for replanning/human review instead of
    spending the remaining attempts at the strongest route.
    """
    return _uncapped_step(failure_classes, rungs) > max(0, len(rungs) - 1)


def _uncapped_step(failure_classes: list[str], rungs: list[tuple[str, str]]) -> int:
    step = 0
    repeat_streak = 0
    top = max(0, len(rungs) - 1)
    for raw in failure_classes:
        cls = str(raw or "unknown").strip().lower()
        if cls not in FAILURE_CLASSES:
            cls = "unknown"
        if cls in ("environmental", "plan_defect"):
            continue
        if cls in ("mechanical", "budget"):
            repeat_streak += 1
            if repeat_streak >= 2:
                step += 1
                repeat_streak = 0
            continue
        repeat_streak = 0
        if cls == "semantic":
            current_tier = rungs[min(step, top)][0]
            jump = step + 1
            while jump <= top and rungs[jump][0] == current_tier:
                jump += 1
            step = jump
            continue
        step += 1
    return step


# Leaf signals an agent (of any size) can name without judgment-heavy reasoning.
# `minimum_route` turns them into the cheapest credible tier/effort floor; the
# same table is printed in SKILL.md so a small root model routes consistently.
PRIMARY_SIGNALS: dict[str, tuple[str, str]] = {
    "deterministic_lookup": ("tool", "none"),
    "exploration": ("economy", "low"),
    "mechanical_edit": ("economy", "low"),
    "bounded_implementation": ("standard", "medium"),
    "subtle_debugging": ("strong", "medium"),
    "architecture_decision": ("strong", "high"),
    "cross_cutting_risk": ("strong", "high"),   # migration/security/concurrency/data integrity/distributed
    "silent_failure_costly": ("strong", "high"),
    "frontier_long_horizon": ("max", "high"),
    "repeated_strong_failure": ("max", "xhigh"),
}
MODIFIER_SIGNALS = ("weak_validation", "strong_validation", "implementation")
ROUTE_TIERS = ["tool", "economy", "standard", "strong", "max"]


def minimum_route(signals: list[str]) -> dict[str, str]:
    """Deterministic floor: the cheapest credible (tier, effort) for a leaf.

    Rules (mirrored in SKILL.md §4):
    - the strongest primary signal sets the base tier and effort;
    - `weak_validation` raises the tier one step (never above `strong` on its own)
      and the effort floor to `high`;
    - `strong_validation` lets `strong` start at `medium` and `standard` at `medium`;
    - `implementation` forbids `low`: a worker that must run validation needs at
      least `medium` unless the edit is mechanical with deterministic checks.
    Escalation above the floor comes only from failure evidence.
    """
    names = [str(item).strip().lower() for item in signals if str(item).strip()]
    unknown = [name for name in names if name not in PRIMARY_SIGNALS and name not in MODIFIER_SIGNALS]
    if unknown:
        raise RoutingError(f"unknown routing signals: {', '.join(sorted(unknown))}")
    primaries = [name for name in names if name in PRIMARY_SIGNALS]
    if not primaries:
        raise RoutingError("at least one primary signal is required")
    tier, effort = "tool", "none"
    for name in primaries:
        candidate_tier, candidate_effort = PRIMARY_SIGNALS[name]
        if ROUTE_TIERS.index(candidate_tier) > ROUTE_TIERS.index(tier):
            tier, effort = candidate_tier, candidate_effort
        elif candidate_tier == tier and candidate_effort != "none":
            if EFFORT_ORDER.index(candidate_effort) > EFFORT_ORDER.index(effort):
                effort = candidate_effort
    if tier == "tool":
        return {"tier": "tool", "effort": "none"}
    if "weak_validation" in names:
        if tier in ("economy", "standard"):
            tier = ROUTE_TIERS[ROUTE_TIERS.index(tier) + 1]
        if EFFORT_ORDER.index(effort) < EFFORT_ORDER.index("high"):
            effort = "high"
    elif "strong_validation" in names and tier in ("standard", "strong") and effort == "high":
        effort = "medium"
    if "implementation" in names and effort == "low":
        mechanical_and_checked = "mechanical_edit" in names and "strong_validation" in names
        if not mechanical_and_checked:
            effort = "medium"
    return {"tier": tier, "effort": effort}


def _cli() -> int:
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Deterministic routing helpers (no model tokens).")
    sub = parser.add_subparsers(dest="command", required=True)
    catalog = sub.add_parser("catalog", help="Print the current provider catalog and ladders as JSON")
    catalog.set_defaults(func=lambda args: print(json.dumps(configure_config({}), indent=2)))
    route = sub.add_parser("route", help="Print the minimum credible route for leaf signals")
    route.add_argument("--signals", required=True, help="comma-separated signals, e.g. bounded_implementation,weak_validation")
    route.set_defaults(func=lambda args: print(json.dumps(minimum_route(args.signals.split(",")))))
    args = parser.parse_args()
    args.func(args)
    return 0


def install_current_model_catalog(planctl_module: Any) -> Any:
    """Install the catalog once on a planctl module used by concise entrypoints."""
    if getattr(planctl_module, "_current_model_catalog_installed", False):
        return planctl_module
    original_default_config = planctl_module.default_config

    def current_default_config() -> dict[str, Any]:
        return configure_config(original_default_config())

    planctl_module.default_config = current_default_config
    planctl_module._current_model_catalog_installed = True
    return planctl_module


def install_runtime_model_catalog(run_module: Any) -> Any:
    """Normalize persisted legacy plan config after the runner loads it."""
    if getattr(run_module, "_current_model_catalog_installed", False):
        return run_module
    original_load_config = run_module.load_config

    def current_load_config(plan_dir: Any) -> dict[str, Any]:
        return configure_config(original_load_config(plan_dir))

    run_module.load_config = current_load_config
    run_module._current_model_catalog_installed = True
    return run_module


if __name__ == "__main__":
    raise SystemExit(_cli())
