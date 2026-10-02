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
import hashlib
import itertools
import json
import math
from typing import Any

MODEL_MAP_VERSION = "2026-09-30-v6"

TIER_ORDER = ["economy", "standard", "advanced", "strong", "max"]
EFFORT_ORDER = ["low", "medium", "high", "xhigh", "max"]

# F1-F5 / L1-L5 are input aliases for the canonical tiers; only canonical
# names are ever persisted.
TIER_ALIASES: dict[str, str] = {
    f"{prefix}{rank}": tier
    for prefix in ("f", "l")
    for rank, tier in enumerate(TIER_ORDER, start=1)
}


def normalize_tier(value: Any) -> str:
    """Lower-case a tier name and map an F/L alias to its canonical tier."""
    name = str(value or "").strip().lower()
    return TIER_ALIASES.get(name, name)

CURRENT_MODELS: dict[str, dict[str, str]] = {
    "claude": {
        "economy": "haiku",
        "standard": "claude-sonnet-5-5",
        "strong": "claude-opus-5-5",
        "max": "claude-fable-5-1",
    },
    # Codex catalog (`codex debug models`, CLI 0.159.2, 2026-09-30): GPT-6 Astra
    # = "frontier intelligence for the most demanding work", GPT-6.1 Sol = "the
    # latest workhorse for coding and everyday work" (GPT-6 Sol is now the
    # previous generation), GPT-6 Luna = "fast and affordable, easier tasks".
    # The GPT-5.6 line is listed as "older" and there is no GPT-6 Terra, so
    # GPT-6.1 Sol takes the balanced standard slot. Keep effort separate from model tier so the agent spends
    # only the reasoning depth justified by verifiability, risk, and failure
    # evidence.
    "codex": {
        "economy": "gpt-6-luna",
        "standard": "gpt-6.1-sol",
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
# - Codex: Astra Low dominated the previous generation's High-effort standard
#   model (OpenAI calibration for GPT-5.6; no newer published numbers), so the
#   ladder never spends a Sol High retry before an Astra Low attempt.
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
                tier, effort = normalize_tier(item[0]), str(item[1])
                if tier in TIER_ORDER and effort in EFFORT_ORDER:
                    rungs.append((tier, effort))
    return rungs or [tuple(rung) for rung in DEFAULT_LADDER]  # type: ignore[misc]


def tier_has_candidate(provider_cfg: dict[str, Any], tier: str) -> bool:
    """False when the provider declares models but none for this tier.

    A provider config without a model map (legacy/unconfigured fixtures) keeps
    every tier, so older plans route exactly as before.
    """
    models = provider_cfg.get("models")
    if not isinstance(models, dict) or not models:
        return True
    return bool(str(models.get(tier, "") or "").strip())


def lift_tier(provider_cfg: dict[str, Any], tier: str) -> str:
    """Nearest tier at or above `tier` with a candidate; never a downgrade."""
    start = _index(TIER_ORDER, tier)
    for candidate in TIER_ORDER[start:]:
        if tier_has_candidate(provider_cfg, candidate):
            return candidate
    return TIER_ORDER[start]


def _above(rung: tuple[str, str], base: tuple[str, str]) -> bool:
    tier_delta = _index(TIER_ORDER, rung[0]) - _index(TIER_ORDER, base[0])
    if tier_delta != 0:
        return tier_delta > 0
    return _index(EFFORT_ORDER, rung[1]) > _index(EFFORT_ORDER, base[1])


def route_rungs(provider_cfg: dict[str, Any], tier: str, effort: str) -> list[tuple[str, str]]:
    """Declared route first, then every ladder rung strictly above it.

    Tiers without a configured candidate are skipped upward: the floor lifts
    to the next tier that has one, and empty ladder rungs are dropped.
    """
    tier = normalize_tier(tier)
    base_tier = lift_tier(provider_cfg, tier if tier in TIER_ORDER else "standard")
    base = (base_tier, effort if effort in EFFORT_ORDER else "medium")
    return [base] + [
        rung for rung in provider_ladder(provider_cfg)
        if _above(rung, base) and tier_has_candidate(provider_cfg, rung[0])
    ]


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
ROUTE_TIERS = ["tool", *TIER_ORDER]
# `weak_validation` lifts a cheap floor to the next legacy tier; `advanced` is
# never inferred from signals, so the lift keeps schema 1-4 floors unchanged.
WEAK_VALIDATION_LIFT = {"economy": "standard", "standard": "strong", "advanced": "strong"}


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
        tier = WEAK_VALIDATION_LIFT.get(tier, tier)
        if EFFORT_ORDER.index(effort) < EFFORT_ORDER.index("high"):
            effort = "high"
    elif "strong_validation" in names and tier in ("standard", "strong") and effort == "high":
        effort = "medium"
    if "implementation" in names and effort == "low":
        mechanical_and_checked = "mechanical_edit" in names and "strong_validation" in names
        if not mechanical_and_checked:
            effort = "medium"
    return {"tier": tier, "effort": effort}


# --- Deterministic candidate selector -------------------------------------
# minimum_route -> floor -> capability -> availability -> quality constraint
# -> target tier -> effective cost -> tie-break, plus sticky routing. Pure:
# no clock, network, process or model call; the catalog is passed in (default:
# the bootstrap catalog). Runner routes are unchanged; this is opt-in.
SELECT_SCHEMA = "route-select/1"
SELECT_REQUEST_KEYS = {
    "signals", "route", "providers", "required_capabilities", "availability", "tokens", "billing", "at",
    "previous_route", "cache_affinity", "last_failure_class", "min_quality_score",
}
AVAILABILITY_STATES = ("available", "outage", "quota_exhausted", "rate_limited", "cooldown", "auth_missing")
BILLING_MODES = ("api", "subscription")
CACHE_AFFINITY = ("none", "low", "high")
TOKEN_FIELDS = ("input_tokens", "cached_input_tokens", "cache_write_tokens", "output_tokens")
# Ranking key, in order. Unknown cash/quota sort after any known value.
TIE_BREAK = ("marginal_cash_cost", "quota_cost", "provider_order", "quality_rank_desc", "model_id")


def _round(value: float | None) -> float | None:
    return None if value is None else round(float(value), 10)


def _number(value: Any, name: str, *, upper: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0 or (upper is not None and value > upper):
        raise RoutingError(f"{name} must be a number in [0, {upper if upper is not None else 'inf'}]")
    return float(value)


def _select_floor(request: dict[str, Any]) -> dict[str, str]:
    if ("signals" in request) == ("route" in request):
        raise RoutingError("select needs exactly one of signals or route")
    if "signals" in request:
        signals = request["signals"]
        if not isinstance(signals, list):
            raise RoutingError("signals must be a list")
        return minimum_route(signals)
    route = request["route"]
    if not isinstance(route, dict):
        raise RoutingError("route must be an object with tier and effort")
    tier, effort = normalize_tier(route.get("tier")), str(route.get("effort") or "")
    if tier not in TIER_ORDER or effort not in EFFORT_ORDER:
        raise RoutingError(f"route needs a canonical tier and effort, got {route.get('tier')!r}/{route.get('effort')!r}")
    return {"tier": tier, "effort": effort}


def _select_request(request: Any) -> dict[str, Any]:
    if not isinstance(request, dict):
        raise RoutingError("select request must be an object")
    unknown = sorted(set(request) - SELECT_REQUEST_KEYS)
    if unknown:
        raise RoutingError(f"unknown select fields: {', '.join(unknown)}")
    providers = request.get("providers")
    if not isinstance(providers, list) or not providers or not all(isinstance(p, str) and p for p in providers):
        raise RoutingError("providers must be a non-empty list of configured provider ids in preference order")
    if len(set(providers)) != len(providers):
        raise RoutingError("providers must be unique")
    capabilities = request.get("required_capabilities", [])
    from model_catalog import CAPABILITY_NAMES
    if not isinstance(capabilities, list) or any(name not in CAPABILITY_NAMES for name in capabilities):
        raise RoutingError(f"required_capabilities must list names from {', '.join(CAPABILITY_NAMES)}")
    availability = request.get("availability", {})
    if not isinstance(availability, dict) or any(state not in AVAILABILITY_STATES for state in availability.values()):
        raise RoutingError(f"availability maps provider or provider/model to one of {', '.join(AVAILABILITY_STATES)}")
    tokens = request.get("tokens", {})
    if not isinstance(tokens, dict) or set(tokens) - set(TOKEN_FIELDS):
        raise RoutingError(f"tokens accepts only {', '.join(TOKEN_FIELDS)}")
    counts = {name: int(_number(tokens.get(name, 0), f"tokens.{name}")) for name in TOKEN_FIELDS}
    if counts["cached_input_tokens"] > counts["input_tokens"]:
        raise RoutingError("tokens.cached_input_tokens cannot exceed input_tokens")
    billing = request.get("billing", {})
    if not isinstance(billing, dict):
        raise RoutingError("billing must map provider ids to billing objects")
    for provider, body in billing.items():
        if not isinstance(body, dict) or body.get("mode") not in BILLING_MODES:
            raise RoutingError(f"billing.{provider}.mode must be one of {', '.join(BILLING_MODES)}")
        if set(body) - {"mode", "window_capacity", "window_used", "overage", "off_peak", "cache_write_multiplier"}:
            raise RoutingError(f"billing.{provider} has unknown fields")
        if body.get("overage", "block") not in ("block", "api"):
            raise RoutingError(f"billing.{provider}.overage must be block or api")
        if body.get("window_capacity") is not None and _number(body["window_capacity"], "window_capacity") == 0:
            raise RoutingError(f"billing.{provider}.window_capacity must be positive")
        _number(body.get("window_used", 0), f"billing.{provider}.window_used", upper=1)
        _number(body.get("cache_write_multiplier", 1), f"billing.{provider}.cache_write_multiplier")
    at = request.get("at")
    parsed_at = None
    if at is not None:
        from model_catalog import _parse_time
        parsed_at = _parse_time(at)
        if parsed_at is None:
            raise RoutingError("at must be a timezone-aware ISO-8601 timestamp")
    previous = request.get("previous_route")
    if previous is not None:
        if not isinstance(previous, dict) or not previous.get("provider") or not previous.get("model"):
            raise RoutingError("previous_route needs provider, model, tier and effort")
        previous = {"provider": str(previous["provider"]), "model": str(previous["model"]),
                    "tier": normalize_tier(previous.get("tier")), "effort": str(previous.get("effort") or "")}
        if previous["tier"] not in TIER_ORDER or previous["effort"] not in EFFORT_ORDER:
            raise RoutingError("previous_route needs a canonical tier and effort")
    affinity = request.get("cache_affinity", "none")
    if affinity not in CACHE_AFFINITY:
        raise RoutingError(f"cache_affinity must be one of {', '.join(CACHE_AFFINITY)}")
    failure = request.get("last_failure_class")
    if failure is not None and failure not in FAILURE_CLASSES:
        raise RoutingError(f"last_failure_class must be one of {', '.join(FAILURE_CLASSES)}")
    min_score = request.get("min_quality_score")
    if min_score is not None:
        min_score = _number(min_score, "min_quality_score", upper=1)
    return {
        "floor": _select_floor(request), "providers": list(providers), "capabilities": sorted(capabilities),
        "availability": dict(availability), "tokens": counts, "billing": billing, "at": parsed_at,
        "previous": previous, "affinity": affinity, "failure": failure, "min_score": min_score,
    }


def _api_cost(economics: dict[str, Any], tokens: dict[str, int], cached: int, write_multiplier: float, at: Any) -> float | None:
    """API USD: uncached*in + cached*cached + cache_write*in*multiplier + output*out (off-peak rates in window)."""
    from model_catalog import is_off_peak
    source = economics["off_peak"] if at is not None and economics.get("off_peak") and is_off_peak(economics, at) else economics
    input_rate, output_rate = source.get("input_per_mtok"), source.get("output_per_mtok")
    if input_rate is None or output_rate is None:
        return None
    cached_rate = source.get("cached_input_per_mtok")
    cached_rate = input_rate if cached_rate is None else cached_rate  # no cache discount when unknown
    uncached = tokens["input_tokens"] - cached
    total = (uncached * input_rate + cached * cached_rate + tokens["cache_write_tokens"] * input_rate * write_multiplier
             + tokens["output_tokens"] * output_rate)
    return total / 1_000_000


def _effective_cost(entry: dict[str, Any], billing: dict[str, Any] | None, tokens: dict[str, int], cache_hit: bool,
                    at: Any) -> dict[str, Any]:
    """API cash or subscription quota for one attempt; never converts a subscription into a token price."""
    from model_catalog import credits
    economics = entry["economics"]
    cached = tokens["cached_input_tokens"] if cache_hit else 0
    mode = (billing or {}).get("mode", "unknown")
    write_multiplier = float((billing or {}).get("cache_write_multiplier", 1))
    api = _api_cost(economics, tokens, cached, write_multiplier, at)
    cost: dict[str, Any] = {"billing": mode, "cache_hit": cache_hit, "marginal_cash_cost": None, "quota_cost": None,
                            "usage": None, "usage_unit": None, "exhausted": False}
    if mode == "api":
        cost.update(marginal_cash_cost=api, quota_cost=0.0, usage=api, usage_unit="usd")
    elif mode == "subscription":
        if economics.get("plan_credits"):
            usage = credits(economics, tokens["input_tokens"] - cached, cached, tokens["output_tokens"],
                            off_peak=bool(billing.get("off_peak")))
            unit = "credits"
        else:
            usage = float(tokens["input_tokens"] + tokens["cache_write_tokens"] + tokens["output_tokens"])
            unit = "tokens"
        capacity = billing.get("window_capacity")
        used = float(billing.get("window_used", 0))
        quota = usage / capacity if capacity else None
        exhausted = used >= 1 or (quota is not None and used + quota > 1)
        cash: float | None = 0.0
        if exhausted:
            cash = api if billing.get("overage") == "api" else None
        cost.update(marginal_cash_cost=cash, quota_cost=quota, usage=usage, usage_unit=unit,
                    exhausted=exhausted and billing.get("overage", "block") == "block")
    for key in ("marginal_cash_cost", "quota_cost", "usage"):
        cost[key] = _round(cost[key])
    return cost


def _candidate_id(candidate: dict[str, Any]) -> str:
    return f"{candidate['provider']}/{candidate['model']}@{candidate['tier']}"


def _rank_key(candidate: dict[str, Any]) -> tuple:
    cost = candidate["cost"]
    inf = float("inf")
    cash = inf if cost["marginal_cash_cost"] is None else cost["marginal_cash_cost"]
    quota = inf if cost["quota_cost"] is None else cost["quota_cost"]
    return (cash, quota, candidate["provider_order"], -(candidate["quality_rank"] or 0), candidate["model"])


def _stage(name: str, candidates: list[dict[str, Any]], reason_of) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    kept, dropped = [], []
    for candidate in candidates:
        reason = reason_of(candidate)
        if reason:
            dropped.append({"candidate": _candidate_id(candidate), "reason": reason})
        else:
            kept.append(candidate)
    return kept, {"stage": name, "kept": [_candidate_id(c) for c in kept], "dropped": dropped}


def select_route(request: Any, catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    """Pick the cheapest safe candidate at or above the deterministic floor.

    Floor first; capability/availability/quality filters remove candidates
    before any cost is compared; the lowest tier with an eligible candidate is
    the target (an outage tries a same-tier equivalent before lifting); then
    effective cost and the TIE_BREAK order decide. Sticky routing keeps an
    eligible previous route under high cache affinity unless a failure or a
    strictly cheaper alternative wins.
    """
    import model_catalog

    spec = _select_request(request)
    catalog = model_catalog.validate(catalog if catalog is not None else model_catalog.BOOTSTRAP_CATALOG)
    floor = spec["floor"]
    result: dict[str, Any] = {"schema": SELECT_SCHEMA, "floor": floor, "decision": "route", "route": None,
                              "sticky": {"applied": False, "reason": "no_previous_route", "cache_affinity": spec["affinity"]}}
    explanation: dict[str, Any] = {"catalog_version": catalog["catalog_version"], "providers": spec["providers"],
                                   "stages": [], "target_tier": None, "tier_lifted": False, "ranking": [],
                                   "tie_break": list(TIE_BREAK)}
    result["explanation"] = explanation
    if floor["tier"] == "tool":
        result["decision"] = "tool"
        return result

    previous = spec["previous"]
    candidates: list[dict[str, Any]] = []
    missing = []
    for order, provider in enumerate(spec["providers"]):
        body = catalog["providers"].get(provider)
        if body is None:
            missing.append(provider)
            continue
        for model_id in sorted(body["models"]):
            entry = body["models"][model_id]
            cache_hit = previous is None or (previous["provider"] == provider and previous["model"] == model_id)
            for tier in sorted(entry["tiers"], key=TIER_ORDER.index):
                candidates.append({
                    "provider": provider, "model": model_id, "tier": tier, "provider_order": order, "entry": entry,
                    "quality_rank": entry["quality"]["rank"],
                    "cost": _effective_cost(entry, spec["billing"].get(provider), spec["tokens"], cache_hit, spec["at"]),
                })
    explanation["providers_not_in_catalog"] = missing

    floor_index = TIER_ORDER.index(floor["tier"])

    def effort_reason(candidate: dict[str, Any], effort: str) -> str | None:
        capability = candidate["entry"]["capability"]
        cap = capability.get("max_effort")
        if capability["accepts_effort"] and cap and EFFORT_ORDER.index(effort) > EFFORT_ORDER.index(cap):
            return f"effort_above_max:{cap}"
        return None

    def capability_reason(candidate: dict[str, Any]) -> str | None:
        have = set(candidate["entry"]["capability"]["capabilities"])
        for name in spec["capabilities"]:
            if name not in have:
                return f"missing_capability:{name}"
        return effort_reason(candidate, floor["effort"])

    def availability_reason(candidate: dict[str, Any]) -> str | None:
        if not candidate["entry"]["capability"]["available"]:
            return "catalog_unavailable"
        for key in (f"{candidate['provider']}/{candidate['model']}", candidate["provider"]):
            state = spec["availability"].get(key)
            if state and state != "available":
                return state
        return "quota_window_exhausted" if candidate["cost"]["exhausted"] else None

    def quality_reason(candidate: dict[str, Any]) -> str | None:
        rank = candidate["quality_rank"]
        if rank is not None and rank < TIER_ORDER.index(candidate["tier"]) + 1:
            return f"quality_rank_below_tier:{rank}"
        score = candidate["entry"]["quality"]["score"]
        if spec["min_score"] is not None and (score is None or score < spec["min_score"]):
            return "quality_score_unknown" if score is None else f"quality_score_below_min:{score}"
        return None

    pool = candidates
    for name, reason_of in (
        ("floor", lambda c: "below_floor" if TIER_ORDER.index(c["tier"]) < floor_index else None),
        ("capability", capability_reason),
        ("availability", availability_reason),
        ("quality", quality_reason),
    ):
        pool, record = _stage(name, pool, reason_of)
        explanation["stages"].append(record)
    eligible = pool
    if not eligible:
        result["decision"] = "no_candidate"
        result["sticky"]["reason"] = "no_candidate" if previous else "no_previous_route"
        return result

    target = min((c["tier"] for c in eligible), key=TIER_ORDER.index)
    explanation["target_tier"] = target
    explanation["tier_lifted"] = target != floor["tier"]
    ranked, record = _stage("target_tier", eligible, lambda c: "above_target_tier" if c["tier"] != target else None)
    explanation["stages"].append(record)
    ranked.sort(key=_rank_key)
    explanation["ranking"] = [
        {"candidate": _candidate_id(c), "effective_cost": c["cost"],
         "key": [c["cost"]["marginal_cash_cost"], c["cost"]["quota_cost"], c["provider_order"],
                 -(c["quality_rank"] or 0), c["model"]]}
        for c in ranked
    ]
    chosen, effort = ranked[0], floor["effort"]

    sticky = result["sticky"]
    if previous is not None:
        match = next((c for c in eligible if c["provider"] == previous["provider"] and c["model"] == previous["model"]
                      and c["tier"] == previous["tier"]), None)
        if spec["failure"] not in (None, "environmental"):
            sticky["reason"] = f"failure:{spec['failure']}"
        elif match is None or EFFORT_ORDER.index(previous["effort"]) < EFFORT_ORDER.index(floor["effort"]) \
                or effort_reason(match, previous["effort"]):
            sticky["reason"] = "previous_route_ineligible"
        elif spec["affinity"] != "high":
            sticky["reason"] = f"cache_affinity_{spec['affinity']}"
        elif _rank_key(chosen)[:2] < _rank_key(match)[:2]:
            sticky["reason"] = "cheaper_alternative"
        else:
            sticky.update(applied=True, reason="cache_affinity_high")
            chosen, effort = match, previous["effort"]

    # Ladder over the chosen provider's eligible models: same rungs as route_rungs.
    tier_models: dict[str, str] = {}
    for candidate in sorted((c for c in eligible if c["provider"] == chosen["provider"]), key=_rank_key):
        tier_models.setdefault(candidate["tier"], candidate["model"])
    tier_models[chosen["tier"]] = chosen["model"]
    ladder_cfg = {"models": tier_models,
                  "escalation_ladder": ESCALATION_LADDERS.get(chosen["provider"], DEFAULT_LADDER)}
    capability = chosen["entry"]["capability"]
    result["route"] = {
        "provider": chosen["provider"], "model": chosen["model"], "tier": chosen["tier"], "effort": effort,
        "effort_flag": bool(capability["accepts_effort"]),
        "native_effort": (capability.get("effort_map") or {}).get(effort, effort),
        "effective_cost": chosen["cost"],
        "ladder": [{"tier": t, "effort": e, "model": tier_models[t]}
                   for t, e in route_rungs(ladder_cfg, chosen["tier"], effort)],
    }
    return result


def select_json(request: Any, catalog: dict[str, Any] | None = None) -> str:
    """Canonical, byte-stable JSON for a selection."""
    return json.dumps(select_route(request, catalog), sort_keys=True, indent=2, ensure_ascii=False)


def _select_cli(args: Any) -> None:
    import sys
    from pathlib import Path

    if args.request:
        text = sys.stdin.read() if args.request == "-" else Path(args.request).read_text(encoding="utf-8")
        request = json.loads(text)
    else:
        if not args.signals or not args.providers:
            raise SystemExit("select needs --request or both --signals and --providers")
        request = {"signals": args.signals.split(","), "providers": args.providers.split(",")}
    catalog = json.loads(Path(args.catalog).read_text(encoding="utf-8")) if args.catalog else None
    print(select_json(request, catalog))


# --- Delegation policy v2 ---------------------------------------------------
# Pure gate: task signals -> tool | keep_root | delegate, with role, route (via
# select_route, so floors and configured providers are inherited) and budgets.
# Thresholds are stated once in references/DELEGATION.md and pinned in
# delegation_self_test.py.
DELEGATE_SCHEMA = "delegation-decision/1"
DELEGATE_REQUEST_KEYS = {
    "signals", "providers", "agent_tier", "depth", "independent_units", "read_only", "write_scopes", "unit_tokens",
    "token_budget", "rollup", "role", "previous_route", "cache_affinity", "required_capabilities", "availability",
    "billing",
}
DELEGATION_ROLES: dict[str, dict[str, Any]] = {
    "scout": {"read_only": True, "purpose": "read-only discovery; returns located facts with file/line evidence"},
    "analyst": {"read_only": True, "purpose": "read-only decision or risk analysis; returns a recommendation"},
    "verifier": {"read_only": True, "purpose": "independent validation; runs checks and reports pass/fail evidence"},
    "implementer": {"read_only": False, "purpose": "bounded edit inside its write scope; runs its validation"},
    "debugger": {"read_only": False, "purpose": "reproduce, fix and validate a defect inside its write scope"},
}
MAX_DEPTH = 1                 # root (depth 0) spawns workers; workers do not spawn by default
EXCEPTION_DEPTH = 2           # capability-gap exception: one read-only worker, never deeper
MAX_FAN_OUT = {"read_only": 4, "write": 2}
BRIEF_MAX_TOKENS = 2000
RESULT_MAX_TOKENS = 1000
RESULT_MAX_BYTES = 4000
WORKER_OVERHEAD_TOKENS = BRIEF_MAX_TOKENS + RESULT_MAX_TOKENS
COORDINATION_OVERHEAD_MAX = 0.25  # overhead / (overhead + unit work) above this keeps the work at root
MAX_WORKER_TOKENS = 200_000
BUDGET_FIELDS = ("input_tokens", "cache_write_tokens", "output_tokens")  # cached reads reported, not charged
RESULT_KEYS = ("status", "role", "summary", "findings", "changed_files", "validations", "blocked_reason")
RESULT_LIMITS = {"summary_chars": 360, "findings": 8, "validations": 8, "changed_files": 50}


def _int_field(request: dict[str, Any], name: str, default: int | None, minimum: int) -> int | None:
    value = request.get(name, default)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise RoutingError(f"{name} must be an integer >= {minimum}")
    return value


def _scopes_overlap(scopes: list[list[str]]) -> bool:
    paths = [(index, path.strip("/").replace("\\", "/")) for index, scope in enumerate(scopes) for path in scope]
    for (i, a), (j, b) in itertools.combinations(paths, 2):
        if i != j and (a == b or a.startswith(b + "/") or b.startswith(a + "/")):
            return True
    return False


def _derive_role(names: list[str], read_only: bool) -> str:
    primaries = {name for name in names if name in PRIMARY_SIGNALS}
    if read_only:
        return "scout" if primaries <= {"exploration", "deterministic_lookup"} else "analyst"
    return "debugger" if "subtle_debugging" in primaries else "implementer"


def _delegate_request(request: Any) -> dict[str, Any]:
    if not isinstance(request, dict):
        raise RoutingError("delegate request must be an object")
    unknown = sorted(set(request) - DELEGATE_REQUEST_KEYS)
    if unknown:
        raise RoutingError(f"unknown delegate fields: {', '.join(unknown)}")
    signals = request.get("signals")
    if not isinstance(signals, list):
        raise RoutingError("signals must be a list")
    agent_tier = normalize_tier(request.get("agent_tier"))
    if agent_tier not in TIER_ORDER:
        raise RoutingError("agent_tier must be the canonical tier of the agent asking (root at depth 0)")
    read_only = request.get("read_only", False)
    if not isinstance(read_only, bool):
        raise RoutingError("read_only must be a boolean")
    units = _int_field(request, "independent_units", 1, 1)
    floor = minimum_route(signals)
    scopes = request.get("write_scopes")
    if read_only or floor["tier"] == "tool":
        if read_only and scopes:
            raise RoutingError("read_only work takes no write_scopes")
        scopes = [[] for _ in range(units)]
    elif not isinstance(scopes, list) or len(scopes) != units or not all(
            isinstance(scope, list) and scope and all(isinstance(p, str) and p.strip() for p in scope) for scope in scopes):
        raise RoutingError("write work needs write_scopes: one non-empty path list per independent unit")
    names = [str(item).strip().lower() for item in signals if str(item).strip()]
    role = request.get("role") or _derive_role(names, read_only)
    if role not in DELEGATION_ROLES:
        raise RoutingError(f"role must be one of {', '.join(DELEGATION_ROLES)}")
    if DELEGATION_ROLES[role]["read_only"] != read_only:
        raise RoutingError(f"role {role} requires read_only={DELEGATION_ROLES[role]['read_only']}")
    rollup = request.get("rollup")
    if rollup is not None and not (isinstance(rollup, dict) and isinstance(rollup.get("totals"), dict)):
        raise RoutingError("rollup must be a routing_telemetry rollup object")
    return {
        "floor": floor, "names": names, "agent_tier": agent_tier, "read_only": read_only,
        "depth": _int_field(request, "depth", 0, 0), "units": units, "scopes": scopes, "role": role,
        "unit_tokens": _int_field(request, "unit_tokens", 0, 0), "token_budget": _int_field(request, "token_budget", None, 0),
        "rollup": rollup,
    }


def delegation_accounting(rollup: dict[str, Any] | None, token_budget: int | None) -> dict[str, Any]:
    """Spent delegation tokens from the TODO 015 rollup, summed over every worker kind (native units)."""
    import routing_telemetry

    accounting: dict[str, Any] = {"source": None, "kinds": list(routing_telemetry.KINDS), "charged_fields": list(BUDGET_FIELDS),
                                  "by_kind": None, "spent_tokens": None, "token_budget": token_budget,
                                  "remaining_tokens": token_budget}
    if rollup is None:
        return accounting

    def charged(totals: dict[str, Any]) -> int | None:
        values = [totals.get(field) for field in BUDGET_FIELDS if isinstance(totals.get(field), (int, float))]
        return int(sum(values)) if values else None

    accounting["source"] = "routing_telemetry.rollup"
    totals = rollup["totals"]
    by_kind = rollup.get("by_kind") or {}
    if by_kind:
        if set(by_kind) != set(routing_telemetry.KINDS):
            raise RoutingError(f"rollup.by_kind must list exactly {', '.join(routing_telemetry.KINDS)}")
        if sum(int(by_kind[kind].get("attempts") or 0) for kind in routing_telemetry.KINDS) != int(totals.get("attempts") or 0):
            raise RoutingError("rollup has attempts outside the known worker kinds")
        accounting["by_kind"] = {kind: charged(by_kind[kind]) for kind in routing_telemetry.KINDS}
        spent_values = [value for value in accounting["by_kind"].values() if value is not None]
        spent = sum(spent_values) if spent_values else None
    else:  # truncated rollup: totals still cover every kind
        spent = charged(totals)
    accounting["spent_tokens"] = spent
    if token_budget is not None:
        accounting["remaining_tokens"] = max(0, token_budget - (spent or 0))
    return accounting


def delegate_decision(request: Any, catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    """Deterministic delegation gate; see references/DELEGATION.md for the rules."""
    spec = _delegate_request(request)
    floor, depth, units = spec["floor"], spec["depth"], spec["units"]
    accounting = delegation_accounting(spec["rollup"], spec["token_budget"])
    result: dict[str, Any] = {
        "schema": DELEGATE_SCHEMA, "decision": "tool", "reasons": [], "blocked": None, "floor": floor,
        "agent_tier": spec["agent_tier"], "role": None, "route": None, "sticky": None, "fan_out": 0,
        "depth": {"current": depth, "worker": None, "max": MAX_DEPTH, "exception_max": EXCEPTION_DEPTH},
        "budgets": None, "write_scopes": [], "accounting": accounting,
    }
    if floor["tier"] == "tool":
        result["reasons"].append("deterministic_tool")
        return result

    capability_gap = TIER_ORDER.index(floor["tier"]) > TIER_ORDER.index(spec["agent_tier"])
    select_request = {key: request[key] for key in ("providers", "previous_route", "cache_affinity",
                                                    "required_capabilities", "availability", "billing") if key in request}
    selection = select_route({"signals": request["signals"], **select_request}, catalog)
    result["sticky"] = selection["sticky"]
    reasons = result["reasons"]

    def keep(reason: str) -> dict[str, Any]:
        reasons.append(reason)
        result["decision"] = "keep_root"
        return result

    def block(reason: str) -> dict[str, Any]:
        reasons.append(reason)
        result.update(decision="delegate", blocked=reason, role=spec["role"])
        return result

    if capability_gap:
        reasons.append("floor_above_agent_tier")
    if depth >= MAX_DEPTH:
        exception = capability_gap and depth + 1 <= EXCEPTION_DEPTH and spec["read_only"]
        if not exception:
            return block("depth_limit") if capability_gap else keep("depth_limit")
        reasons.append("depth_exception_capability_gap")
    if not capability_gap:
        if selection["sticky"]["applied"]:
            return keep("sticky_route")
        if units == 1 and selection["sticky"]["cache_affinity"] == "high":
            return keep("high_affinity_sequential")
        overhead = WORKER_OVERHEAD_TOKENS / (WORKER_OVERHEAD_TOKENS + spec["unit_tokens"])
        if overhead > COORDINATION_OVERHEAD_MAX:
            return keep("coordination_overhead")
    if selection["decision"] != "route":
        return block("no_candidate") if capability_gap else keep("no_candidate")

    limit = MAX_FAN_OUT["read_only" if spec["read_only"] else "write"]
    if depth >= MAX_DEPTH:
        limit = 1
    scopes = spec["scopes"]
    if not spec["read_only"] and _scopes_overlap(scopes):
        reasons.append("write_scope_overlap")
        limit = 1
        scopes = [sorted({path for scope in scopes for path in scope})]
    fan_out = min(units, limit)
    if fan_out < units:
        reasons.append("fan_out_limit")
    tokens_per_worker = min(spec["unit_tokens"] + WORKER_OVERHEAD_TOKENS, MAX_WORKER_TOKENS)
    if tokens_per_worker < spec["unit_tokens"] + WORKER_OVERHEAD_TOKENS:
        reasons.append("worker_token_cap")
    remaining = accounting["remaining_tokens"]
    if remaining is not None and remaining // tokens_per_worker < fan_out:
        fan_out = remaining // tokens_per_worker
        if fan_out == 0:
            return block("token_budget_exhausted") if capability_gap else keep("token_budget_exhausted")
        reasons.append("token_budget_limit")
    route = selection["route"]
    reasons.append("delegate")
    result.update(
        decision="delegate", role=spec["role"], fan_out=fan_out,
        route={key: route[key] for key in ("provider", "model", "tier", "effort", "effort_flag", "native_effort")},
        budgets={"tokens_per_worker": tokens_per_worker, "brief_max_tokens": BRIEF_MAX_TOKENS,
                 "result_max_tokens": RESULT_MAX_TOKENS, "result_max_bytes": RESULT_MAX_BYTES},
        write_scopes=scopes[:fan_out],
    )
    result["depth"]["worker"] = depth + 1
    return result


def check_worker_result(decision: dict[str, Any], worker_index: int, report: Any) -> list[str]:
    """Problems with a worker's compact result against its role, write scope and output budget."""
    if not isinstance(report, dict):
        return ["result must be an object"]
    problems = []
    if set(report) != set(RESULT_KEYS):
        problems.append(f"result keys must be exactly {', '.join(RESULT_KEYS)}")
    if report.get("role") != decision.get("role"):
        problems.append("role mismatch")
    if report.get("status") not in ("done", "blocked"):
        problems.append("status must be done or blocked")
    if (report.get("status") == "blocked") != bool(report.get("blocked_reason")):
        problems.append("blocked_reason is required exactly when status is blocked")
    if len(str(report.get("summary") or "")) > RESULT_LIMITS["summary_chars"]:
        problems.append("summary too long")
    for key in ("findings", "validations", "changed_files"):
        if not isinstance(report.get(key), list) or len(report[key]) > RESULT_LIMITS[key]:
            problems.append(f"{key} must be a list of at most {RESULT_LIMITS[key]}")
    scopes = decision.get("write_scopes") or []
    scope = scopes[worker_index] if 0 <= worker_index < len(scopes) else []
    for path in report.get("changed_files") or []:
        norm = str(path).strip("/").replace("\\", "/")
        if not any(norm == s.strip("/") or norm.startswith(s.strip("/") + "/") for s in scope):
            problems.append(f"changed file outside write scope: {path}")
    if len(json.dumps(report, sort_keys=True, ensure_ascii=False).encode("utf-8")) > RESULT_MAX_BYTES:
        problems.append(f"result exceeds {RESULT_MAX_BYTES} bytes")
    return problems


def delegate_json(request: Any, catalog: dict[str, Any] | None = None) -> str:
    return json.dumps(delegate_decision(request, catalog), sort_keys=True, indent=2, ensure_ascii=False)


def _delegate_cli(args: Any) -> None:
    import sys
    from pathlib import Path

    text = sys.stdin.read() if args.request == "-" else Path(args.request).read_text(encoding="utf-8")
    request = json.loads(text)
    if args.telemetry:
        import routing_telemetry
        request["rollup"] = routing_telemetry.rollup(
            routing_telemetry.read_records(routing_telemetry.telemetry_path(Path(args.telemetry))))
    catalog = json.loads(Path(args.catalog).read_text(encoding="utf-8")) if args.catalog else None
    print(delegate_json(request, catalog))


# --- Conservative auto-routing rollout gate ---------------------------------
# Pure: predeclared thresholds.json plus the shadow report -> per-segment
# verdicts. A segment passes only when minimum_sample, regression_margin,
# under_routing_limit and material_gain all pass there and it is listed in
# safe_segments. Missing, stale or unparsable evidence fails; it never passes.
GATE_SCHEMA = "rollout-gate/1"
GATE_NAMES = ("minimum_sample", "regression_margin", "under_routing_limit", "material_gain", "safe_segment")
GATE_Z = 1.6448536269514722  # one-sided 95%
# Fixed by the predeclared rule texts in thresholds.json; not tunable here.
FIRST_ATTEMPT_MARGIN = 0.05
MATERIAL_SHIFT_MAX = 0.05
LATENCY_RISE_MAX = 0.25
GATE_REPORT = "SHADOW_REPORT.md"
GATE_THRESHOLDS = "thresholds.json"
COST_UNITS = {"input+output tokens": "io_tokens", "cached tokens": "cached_tokens",
              "cache-write tokens": "cache_write_tokens", "credits": "credits", "usd": "usd"}
_REPORT_SECTIONS = {
    "## Inputs": "inputs",
    "## Under- and over-routing per segment": "under",
    "## Failure-attributed under-routing and sample sufficiency": "sample",
    "## Cost model: cost per validated result": "cost",
    "## Cases": "cases",
}


class GateError(ValueError):
    """Unusable gate evidence; every segment fails."""


def canonical_sha256(data: Any) -> str:
    text = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _cell_number(value: str) -> float | None:
    text = value.strip()
    if text in ("", "n/a"):
        return None
    try:
        number = float(text)
    except ValueError as exc:
        raise GateError(f"report cell is not a number: {text[:40]}") from exc
    if not math.isfinite(number):
        raise GateError("report cell is not finite")
    return number


def _required(value: str) -> float:
    number = _cell_number(value)
    if number is None:
        raise GateError("report count cell is missing")
    return number


def parse_shadow_report(text: str) -> dict[str, Any]:
    """Normalize the generated SHADOW_REPORT.md tables into per-segment evidence."""
    tables: dict[str, list[dict[str, str]]] = {}
    section, header = None, None
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("## "):
            section, header = _REPORT_SECTIONS.get(line), None
            continue
        if section is None or not line.startswith("|"):
            if not line.startswith("|"):
                header = None
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if header is None:
            header = cells
        elif not all(set(cell) <= set("-:") for cell in cells):
            if len(cells) != len(header):
                raise GateError(f"report row width differs from its header in {section}")
            tables.setdefault(section, []).append(dict(zip(header, cells)))
    for name in ("inputs", "under", "sample", "cost", "cases"):
        if not tables.get(name):
            raise GateError(f"report table missing: {name}")
    digest = next((row["Canonical sha256"].strip("`") for row in tables["inputs"]
                   if row.get("Input", "").strip("`") == GATE_THRESHOLDS), None)
    segments: dict[str, dict[str, Any]] = {}
    for row in tables["under"]:
        segments[row["Segment"]] = {
            "cases": int(_required(row["Cases"])),
            "candidate_under": int(_required(row["Candidate under"])),
            "safe": row["Safe segment"] == "yes",
            "arms": {}, "categories": {},
        }
    for row in tables["sample"]:
        item = segments.get(row["Segment"])
        if item is None:
            raise GateError("sample table names an unknown segment")
        item["validated"] = {"main": int(_required(row["Validated main"])),
                             "candidate": int(_required(row["Validated candidate"]))}
        item["attributed_failures"] = int(_required(row["Attributed failures"]))
    for row in tables["cost"]:
        item = segments.get(row["Segment"])
        if item is None:
            raise GateError("cost table names an unknown segment")
        arm = {"attempts": _required(row["Attempts"]), "validated": _required(row["Validated"]),
               "latency": _cell_number(row["latency s"])}
        arm.update({key: _cell_number(row[column]) for column, key in COST_UNITS.items()})
        item["arms"][row["Arm"]] = arm
    for row in tables["cases"]:
        item = segments.get(row["Segment"])
        if item is not None:
            item["categories"][row["Category"]] = item["categories"].get(row["Category"], 0) + 1
    return {"thresholds_sha256": digest, "segments": segments}


def _wilson(successes: float, n: float) -> tuple[float, float]:
    if n <= 0:
        return 0.0, 1.0
    p, z2 = successes / n, GATE_Z * GATE_Z
    denominator = 1 + z2 / n
    centre = (p + z2 / (2 * n)) / denominator
    half = GATE_Z * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n)) / denominator
    return max(0.0, centre - half), min(1.0, centre + half)


def newcombe_lower(candidate: float, candidate_n: float, main: float, main_n: float) -> float:
    """One-sided 95% lower bound (Newcombe hybrid score) of candidate rate minus main rate."""
    p1, p2 = candidate / candidate_n, main / main_n
    low1, _ = _wilson(candidate, candidate_n)
    _, high2 = _wilson(main, main_n)
    return (p1 - p2) - math.sqrt((p1 - low1) ** 2 + (high2 - p2) ** 2)


def _rise(candidate: float | None, main: float | None) -> float | None:
    if candidate is None or main is None:
        return None
    if main == 0:
        return 0.0 if candidate == 0 else math.inf
    return (candidate - main) / main


def _verdict(passed: bool, detail: str) -> dict[str, Any]:
    return {"pass": bool(passed), "detail": detail}


def _segment_gates(name: str, item: dict[str, Any], thresholds: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rules = thresholds["thresholds"]
    main, candidate = item["arms"].get("main"), item["arms"].get("candidate")
    validated = item.get("validated")
    if main is None or candidate is None or validated is None:
        missing = _verdict(False, "segment evidence missing from report")
        gates = {gate: missing for gate in GATE_NAMES[:4]}
    else:
        sample = rules["minimum_sample"]["value"]
        cases = max(1, item["cases"])
        # Matched runs per arm; the smaller denominator widens every bound.
        runs = max(validated["main"], validated["candidate"], cases * sample["repetitions_per_case"])
        repetitions = min(main["attempts"], candidate["attempts"]) / cases
        thin = sorted(c for c, count in item["categories"].items() if count < sample["cases_per_category"])
        enough = (min(validated.values()) >= sample["validated_attempts_per_segment_per_arm"]
                  and not thin and repetitions >= sample["repetitions_per_case"])
        sample_gate = _verdict(enough, f"validated main={validated['main']} candidate={validated['candidate']} "
                                       f"need>={sample['validated_attempts_per_segment_per_arm']}; "
                                       f"repetitions={round(repetitions, 6)}; thin categories={','.join(thin) or 'none'}")
        margin = rules["regression_margin"]["value"]
        lower = newcombe_lower(validated["candidate"], runs, validated["main"], runs)
        # First-attempt: candidate lower bound 2V-A, main upper bound V (every retry may mark a failed first attempt).
        first_candidate = max(0.0, 2 * candidate["validated"] - candidate["attempts"])
        first_lower = newcombe_lower(min(first_candidate, runs), runs, min(main["validated"], runs), runs)
        regression = _verdict(lower >= -margin and first_lower >= -FIRST_ATTEMPT_MARGIN,
                              f"lower bound={round(lower, 6)} (>= -{margin}); "
                              f"first-attempt lower bound={round(first_lower, 6)} (>= -{FIRST_ATTEMPT_MARGIN})")
        limit = rules["under_routing_limit"]["value"]
        failures = item.get("attributed_failures", 0)
        rate, (_, upper) = failures / runs, _wilson(failures, runs)
        under = _verdict(item["candidate_under"] <= limit["floor_violation_max_count"]
                         and rate <= limit["attributed_failure_max_rate"]
                         and upper <= limit["attributed_failure_upper_bound_max"],
                         f"floor violations={item['candidate_under']}; attributed rate={round(rate, 6)}; "
                         f"upper bound={round(upper, 6)}")
        gain_needed = rules["material_gain"]["value"]
        rises = {key: _rise(candidate[key], main[key]) for key in COST_UNITS.values()}
        gain_unit = next((key for key in ("io_tokens", "credits")
                          if rises[key] is not None and -rises[key] >= gain_needed), None)
        shifted = sorted(key for key, value in rises.items()
                         if key != gain_unit and value is not None and value > MATERIAL_SHIFT_MAX)
        per_validated = _rise(candidate["attempts"] / candidate["validated"] if candidate["validated"] else None,
                              main["attempts"] / main["validated"] if main["validated"] else None)
        latency = _rise(candidate["latency"], main["latency"])
        gain = _verdict(gain_unit is not None and not shifted
                        and per_validated is not None and per_validated <= MATERIAL_SHIFT_MAX
                        and latency is not None and latency <= LATENCY_RISE_MAX,
                        f"gain unit={gain_unit or 'none'} (io_tokens change={None if rises['io_tokens'] is None else round(rises['io_tokens'], 6)}, "
                        f"need<=-{gain_needed}); shifted={','.join(shifted) or 'none'}; "
                        f"attempts per validated change={None if per_validated is None else round(per_validated, 6)}; "
                        f"latency change={None if latency is None else round(latency, 6)}")
        gates = {"minimum_sample": sample_gate, "regression_margin": regression,
                 "under_routing_limit": under, "material_gain": gain}
    listed = name in rules["safe_segments"]["value"]
    gates["safe_segment"] = _verdict(listed and item.get("safe", False),
                                     f"listed in safe_segments={listed}; report safe={item.get('safe', False)}")
    if not gates["minimum_sample"]["pass"]:
        # Inconclusive samples cannot pass any gate.
        for gate in ("regression_margin", "under_routing_limit", "material_gain"):
            if gates[gate]["pass"]:
                gates[gate] = _verdict(False, "inconclusive: minimum_sample failed; " + gates[gate]["detail"])
    return gates


def evaluate_gate(thresholds: Any, report: Any) -> dict[str, Any]:
    """Per-segment rollout verdicts; `allowlist` holds only segments passing every gate."""
    result: dict[str, Any] = {"schema": GATE_SCHEMA, "thresholds_sha256": None, "report_thresholds_sha256": None,
                              "fresh": False, "error": None, "segments": {}, "allowlist": []}
    try:
        if not isinstance(thresholds, dict) or thresholds.get("schema_version") != 1:
            raise GateError("thresholds.json schema_version must be 1")
        parsed = parse_shadow_report(report) if isinstance(report, str) else report
        if not isinstance(parsed, dict) or not isinstance(parsed.get("segments"), dict):
            raise GateError("report has no segments")
        result["thresholds_sha256"] = canonical_sha256(thresholds)
        result["report_thresholds_sha256"] = parsed.get("thresholds_sha256")
        result["fresh"] = result["thresholds_sha256"] == result["report_thresholds_sha256"]
        for name in sorted(parsed["segments"]):
            gates = _segment_gates(name, parsed["segments"][name], thresholds)
            if not result["fresh"]:
                gates = {gate: _verdict(False, "stale report: thresholds digest differs; " + verdict["detail"])
                         for gate, verdict in gates.items()}
            passed = all(gates[gate]["pass"] for gate in GATE_NAMES)
            result["segments"][name] = {"pass": passed, "gates": gates}
    except (GateError, KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
        result.update(error=f"{type(exc).__name__}: {exc}"[:240], segments={}, allowlist=[])
        return result
    result["allowlist"] = [name for name, item in result["segments"].items() if item["pass"]]
    return result


def load_gate(directory: Any) -> dict[str, Any]:
    """Evaluate the gate from a routing-eval directory; unreadable evidence yields an empty allowlist."""
    from pathlib import Path

    folder = Path(directory)
    try:
        thresholds = json.loads((folder / GATE_THRESHOLDS).read_text(encoding="utf-8"))
        report = (folder / GATE_REPORT).read_text(encoding="utf-8")
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {"schema": GATE_SCHEMA, "thresholds_sha256": None, "report_thresholds_sha256": None, "fresh": False,
                "error": f"{type(exc).__name__}: cannot read gate evidence", "segments": {}, "allowlist": []}
    return evaluate_gate(thresholds, report)


def effective_allowlist(requested: Any, gate: dict[str, Any]) -> list[str]:
    """Configured segments that also pass the gate; a failing segment is never auto-routed."""
    passing = set(gate.get("allowlist") or []) if not gate.get("error") else set()
    return [name for name in (requested or []) if isinstance(name, str) and name in passing]


def _gate_cli(args: Any) -> None:
    gate = load_gate(args.dir)
    print(json.dumps(gate, sort_keys=True, indent=2, ensure_ascii=False))


def _cli() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Deterministic routing helpers (no model tokens).")
    sub = parser.add_subparsers(dest="command", required=True)
    catalog = sub.add_parser("catalog", help="Print the current provider catalog and ladders as JSON")
    catalog.set_defaults(func=lambda args: print(json.dumps(configure_config({}), indent=2)))
    route = sub.add_parser("route", help="Print the minimum credible route for leaf signals")
    route.add_argument("--signals", required=True, help="comma-separated signals, e.g. bounded_implementation,weak_validation")
    route.set_defaults(func=lambda args: print(json.dumps(minimum_route(args.signals.split(",")))))
    select = sub.add_parser("select", help="Deterministic candidate selection with structured explanation (pure, opt-in)")
    select.add_argument("--request", help="select request JSON file, or - for stdin")
    select.add_argument("--signals", help="comma-separated signals (when no --request)")
    select.add_argument("--providers", help="comma-separated configured providers in preference order (when no --request)")
    select.add_argument("--catalog", help="catalog JSON file (default: bootstrap catalog)")
    select.set_defaults(func=_select_cli)
    delegate = sub.add_parser("delegate", help="Deterministic delegation decision: tool | keep_root | delegate (pure)")
    delegate.add_argument("--request", required=True, help="delegate request JSON file, or - for stdin")
    delegate.add_argument("--telemetry", help="plan directory whose attempt telemetry rollup feeds token accounting")
    delegate.add_argument("--catalog", help="catalog JSON file (default: bootstrap catalog)")
    delegate.set_defaults(func=_delegate_cli)
    gate = sub.add_parser("gate", help="Rollout gate verdicts per segment from thresholds.json and SHADOW_REPORT.md (pure)")
    gate.add_argument("--dir", default="docs/research/routing-eval", help="routing-eval directory")
    gate.set_defaults(func=_gate_cli)
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
    """Apply the current catalog to defaults, never to explicit loaded settings.

    The old post-load wrapper silently replaced user model names, effort caps
    and models_without_effort. Layering owns persisted configuration now.
    """
    install_current_model_catalog(run_module.planctl)
    run_module._current_model_catalog_installed = True
    return run_module


if __name__ == "__main__":
    raise SystemExit(_cli())
