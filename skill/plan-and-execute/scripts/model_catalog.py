#!/usr/bin/env python3
"""Provider-scoped model catalog contract: schema, freshness policy and digest.

A catalog is evidence, not placement. Each provider lists concrete models with
the canonical tiers they can serve plus three independently dated facets:
capability/availability, economics and quality. Every facet carries its own
`observed_at` timestamp and evidence source so freshness is judged per facet.

This module only validates, ages and fingerprints catalogs. It never fetches
data, never invents a model for an empty tier and never chooses a route.
See references/MODEL_CATALOG.md for the documented schema and defaults.
"""
from __future__ import annotations

import copy
import re
import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any

from routingctl import EFFORT_ORDER, TIER_ORDER

SCHEMA_VERSION = 1
FRESHNESS_POLICY_VERSION = "2026-10-01-v1"

FACETS = ("capability", "economics", "quality")
CAPABILITY_NAMES = ("code", "reasoning", "tool_use", "long_context", "vision")
EVIDENCE_SOURCES = ("bootstrap", "provider_cli", "provider_api", "provider_docs", "benchmark", "user")
CURRENCIES = ("USD",)
THINKING_MODES = ("always_on", "optional")

# Conservative defaults (HD004): availability drifts fastest, so it ages first.
# `warn_after_days` < `ttl_days`; a facet older than ttl is stale but usable
# until `ttl_days + grace_days`, after which it is expired.
DEFAULT_FRESHNESS: dict[str, dict[str, int]] = {
    "capability": {"ttl_days": 7, "grace_days": 3, "warn_after_days": 5},
    "economics": {"ttl_days": 30, "grace_days": 7, "warn_after_days": 21},
    "quality": {"ttl_days": 30, "grace_days": 14, "warn_after_days": 21},
}
FRESHNESS_STATES = ("fresh", "warning", "stale", "expired")


class CatalogError(ValueError):
    """Validation failure; `errors` lists `(field_path, message)` pairs."""

    def __init__(self, errors: list[tuple[str, str]]):
        self.errors = errors
        super().__init__("; ".join(f"{path}: {message}" for path, message in errors))


def _parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else None


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _check_keys(obj: dict, allowed: set[str], path: str, errors: list) -> None:
    for key in sorted(set(obj) - allowed):
        errors.append((f"{path}.{key}", "unknown field"))


def _check_facet_common(facet: dict, path: str, errors: list) -> None:
    if _parse_time(facet.get("observed_at")) is None:
        errors.append((f"{path}.observed_at", "required timezone-aware ISO-8601 timestamp"))
    evidence = facet.get("evidence")
    if not isinstance(evidence, dict):
        errors.append((f"{path}.evidence", "required object"))
        return
    _check_keys(evidence, {"source", "ref"}, f"{path}.evidence", errors)
    source = evidence.get("source")
    if not source:
        errors.append((f"{path}.evidence.source", "required"))
    elif source not in EVIDENCE_SOURCES:
        errors.append((f"{path}.evidence.source", f"unknown source {source!r}"))
    if "ref" in evidence and not isinstance(evidence["ref"], str):
        errors.append((f"{path}.evidence.ref", "must be a string"))


def _check_capability(facet: Any, path: str, errors: list) -> None:
    if not isinstance(facet, dict):
        errors.append((path, "required object"))
        return
    _check_keys(facet, {"available", "capabilities", "accepts_effort", "max_effort", "effort_map", "thinking", "observed_at", "evidence"}, path, errors)
    if not isinstance(facet.get("available"), bool):
        errors.append((f"{path}.available", "required boolean"))
    names = facet.get("capabilities")
    if not isinstance(names, list):
        errors.append((f"{path}.capabilities", "required list"))
    else:
        for index, name in enumerate(names):
            if name not in CAPABILITY_NAMES:
                errors.append((f"{path}.capabilities[{index}]", f"unknown capability {name!r}"))
        if len(set(map(str, names))) != len(names):
            errors.append((f"{path}.capabilities", "duplicate capability"))
    if not isinstance(facet.get("accepts_effort"), bool):
        errors.append((f"{path}.accepts_effort", "required boolean"))
    max_effort = facet.get("max_effort")
    if max_effort is not None and max_effort not in EFFORT_ORDER:
        errors.append((f"{path}.max_effort", f"unknown effort {max_effort!r}"))
    effort_map = facet.get("effort_map")
    if effort_map is not None:
        if not isinstance(effort_map, dict):
            errors.append((f"{path}.effort_map", "must be an object"))
        else:
            for logical, native in effort_map.items():
                if logical not in EFFORT_ORDER:
                    errors.append((f"{path}.effort_map.{logical}", "unknown logical effort"))
                elif not isinstance(native, str) or not native:
                    errors.append((f"{path}.effort_map.{logical}", "native effort must be a non-empty string"))
            missing = [e for e in EFFORT_ORDER if e not in effort_map]
            if missing:
                errors.append((f"{path}.effort_map", f"must map every skill effort; missing {', '.join(missing)}"))
    thinking = facet.get("thinking")
    if thinking is not None and thinking not in THINKING_MODES:
        errors.append((f"{path}.thinking", f"must be one of {', '.join(THINKING_MODES)}"))
    _check_facet_common(facet, path, errors)


def _check_plan_credits(plan: Any, path: str, errors: list) -> None:
    if not isinstance(plan, dict):
        errors.append((path, "must be an object"))
        return
    _check_keys(plan, {"unit", "input_multiplier", "cached_multiplier", "output_multiplier", "divisor", "off_peak_factor"}, path, errors)
    if plan.get("unit") != "credits":
        errors.append((f"{path}.unit", "must be 'credits'"))
    for key in ("input_multiplier", "cached_multiplier", "output_multiplier", "divisor"):
        value = plan.get(key)
        if not _is_number(value) or value < 0 or (key == "divisor" and value == 0):
            errors.append((f"{path}.{key}", "required non-negative number (divisor > 0)"))
    factor = plan.get("off_peak_factor")
    if not _is_number(factor) or not 0 < factor <= 1:
        errors.append((f"{path}.off_peak_factor", "required number in (0, 1]"))


def _clock_minutes(value: Any) -> int | None:
    if not isinstance(value, str) or not re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", value):
        return None
    return int(value[:2]) * 60 + int(value[3:])


def _check_off_peak(block: Any, path: str, errors: list) -> None:
    """Off-peak USD rates (base economics fields are the peak rates) plus a daily UTC window."""
    if not isinstance(block, dict):
        errors.append((path, "must be an object"))
        return
    _check_keys(block, {"input_per_mtok", "cached_input_per_mtok", "output_per_mtok", "window_utc"}, path, errors)
    for key in ("input_per_mtok", "cached_input_per_mtok", "output_per_mtok"):
        if not _is_number(block.get(key)) or block[key] < 0:
            errors.append((f"{path}.{key}", "required non-negative number"))
    window = block.get("window_utc")
    if not isinstance(window, dict):
        errors.append((f"{path}.window_utc", "required object with start and end (HH:MM)"))
        return
    _check_keys(window, {"start", "end"}, f"{path}.window_utc", errors)
    start, end = _clock_minutes(window.get("start")), _clock_minutes(window.get("end"))
    for key, value in (("start", start), ("end", end)):
        if value is None:
            errors.append((f"{path}.window_utc.{key}", "must be HH:MM (24h, UTC)"))
    if start is not None and start == end:
        errors.append((f"{path}.window_utc", "start and end must differ"))


def _check_economics(facet: Any, path: str, errors: list) -> None:
    if not isinstance(facet, dict):
        errors.append((path, "required object"))
        return
    _check_keys(facet, {"currency", "input_per_mtok", "output_per_mtok", "cached_input_per_mtok", "plan_credits", "off_peak", "observed_at", "evidence"}, path, errors)
    if facet.get("currency") not in CURRENCIES:
        errors.append((f"{path}.currency", f"must be one of {', '.join(CURRENCIES)}"))
    # null means unknown price: bootstrap data never invents numbers.
    for key in ("input_per_mtok", "output_per_mtok"):
        if key not in facet:
            errors.append((f"{path}.{key}", "required (number or null)"))
        elif facet[key] is not None and (not _is_number(facet[key]) or facet[key] < 0):
            errors.append((f"{path}.{key}", "must be a non-negative number or null"))
    cached = facet.get("cached_input_per_mtok")
    if cached is not None and (not _is_number(cached) or cached < 0):
        errors.append((f"{path}.cached_input_per_mtok", "must be a non-negative number or null"))
    if facet.get("plan_credits") is not None:
        _check_plan_credits(facet["plan_credits"], f"{path}.plan_credits", errors)
    if facet.get("off_peak") is not None:
        _check_off_peak(facet["off_peak"], f"{path}.off_peak", errors)
    _check_facet_common(facet, path, errors)


def _check_quality(facet: Any, path: str, errors: list) -> None:
    if not isinstance(facet, dict):
        errors.append((path, "required object"))
        return
    _check_keys(facet, {"rank", "score", "observed_at", "evidence"}, path, errors)
    rank = facet.get("rank")
    if rank is not None and (not isinstance(rank, int) or isinstance(rank, bool) or not 1 <= rank <= len(TIER_ORDER)):
        errors.append((f"{path}.rank", f"must be an integer 1-{len(TIER_ORDER)} or null"))
    score = facet.get("score")
    if score is not None and (not _is_number(score) or not 0 <= score <= 1):
        errors.append((f"{path}.score", "must be a number in [0, 1] or null"))
    _check_facet_common(facet, path, errors)


_FACET_CHECKS = {"capability": _check_capability, "economics": _check_economics, "quality": _check_quality}


def validate(catalog: Any) -> dict:
    """Return a deep copy of a valid catalog or raise CatalogError with field paths."""
    errors: list[tuple[str, str]] = []
    if not isinstance(catalog, dict):
        raise CatalogError([("$", "catalog must be an object")])
    _check_keys(catalog, {"schema_version", "catalog_version", "providers"}, "$", errors)
    if catalog.get("schema_version") != SCHEMA_VERSION:
        errors.append(("$.schema_version", f"must be {SCHEMA_VERSION}"))
    if not isinstance(catalog.get("catalog_version"), str) or not catalog.get("catalog_version"):
        errors.append(("$.catalog_version", "required non-empty string"))
    providers = catalog.get("providers")
    if not isinstance(providers, dict):
        errors.append(("$.providers", "required object"))
        providers = {}
    for provider, body in providers.items():
        ppath = f"$.providers.{provider}"
        if not isinstance(body, dict) or not isinstance(body.get("models"), dict):
            errors.append((f"{ppath}.models", "required object"))
            continue
        _check_keys(body, {"models"}, ppath, errors)
        for model_id, entry in body["models"].items():
            mpath = f"{ppath}.models.{model_id}"
            if not isinstance(entry, dict):
                errors.append((mpath, "required object"))
                continue
            _check_keys(entry, {"tiers", *FACETS}, mpath, errors)
            tiers = entry.get("tiers")
            if not isinstance(tiers, list) or not tiers:
                errors.append((f"{mpath}.tiers", "required non-empty list"))
            else:
                for index, tier in enumerate(tiers):
                    # Aliases (F1-F5/L1-L5) and case variants are input-only.
                    if tier not in TIER_ORDER:
                        errors.append((f"{mpath}.tiers[{index}]", f"non-canonical tier {tier!r}"))
                if len(set(map(str, tiers))) != len(tiers):
                    errors.append((f"{mpath}.tiers", "duplicate tier"))
            for facet in FACETS:
                _FACET_CHECKS[facet](entry.get(facet), f"{mpath}.{facet}", errors)
    if errors:
        raise CatalogError(errors)
    return copy.deepcopy(catalog)


def canonical_json(catalog: dict) -> str:
    return json.dumps(catalog, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(catalog: dict) -> str:
    """Deterministic sha256 over the validated catalog, independent of key order."""
    return hashlib.sha256(canonical_json(validate(catalog)).encode("utf-8")).hexdigest()


def freshness_policy(overrides: Any = None) -> dict[str, dict[str, int]]:
    """Merge per-facet overrides (e.g. config `model_catalog.freshness`) onto defaults."""
    policy = copy.deepcopy(DEFAULT_FRESHNESS)
    if overrides is None:
        return policy
    errors: list[tuple[str, str]] = []
    if not isinstance(overrides, dict):
        raise CatalogError([("freshness", "must be an object")])
    for facet, values in overrides.items():
        path = f"freshness.{facet}"
        if facet not in FACETS:
            errors.append((path, "unknown facet"))
            continue
        if not isinstance(values, dict):
            errors.append((path, "must be an object"))
            continue
        for key, value in values.items():
            if key not in policy[facet]:
                errors.append((f"{path}.{key}", "unknown field"))
            elif not isinstance(value, int) or isinstance(value, bool) or value < 0:
                errors.append((f"{path}.{key}", "must be a non-negative integer"))
            else:
                policy[facet][key] = value
    for facet, values in policy.items():
        if values["warn_after_days"] > values["ttl_days"]:
            errors.append((f"freshness.{facet}.warn_after_days", "must not exceed ttl_days"))
    if errors:
        raise CatalogError(errors)
    return policy


def facet_freshness(observed_at: str, facet: str, now: datetime, policy: dict | None = None) -> str:
    """Classify one facet as fresh, warning, stale (in grace) or expired."""
    rules = (policy or DEFAULT_FRESHNESS)[facet]
    observed = _parse_time(observed_at)
    if observed is None:
        return "expired"
    age = now - observed
    if age > timedelta(days=rules["ttl_days"] + rules["grace_days"]):
        return "expired"
    if age > timedelta(days=rules["ttl_days"]):
        return "stale"
    if age > timedelta(days=rules["warn_after_days"]):
        return "warning"
    return "fresh"


def catalog_freshness(catalog: dict, now: datetime | None = None, policy: dict | None = None) -> dict:
    """Return `{provider: {model: {facet: state}}}` for a validated catalog."""
    now = now or datetime.now(timezone.utc)
    report: dict[str, dict[str, dict[str, str]]] = {}
    for provider, body in validate(catalog)["providers"].items():
        for model_id, entry in body["models"].items():
            report.setdefault(provider, {})[model_id] = {
                facet: facet_freshness(entry[facet]["observed_at"], facet, now, policy) for facet in FACETS
            }
    return report


def _bootstrap_entry(tiers: list[str], capabilities: list[str], accepts_effort: bool, max_effort: str | None, rank: int, ref: str) -> dict:
    observed = "2026-09-30T00:00:00Z"
    evidence = {"source": "bootstrap", "ref": ref}
    return {
        "tiers": tiers,
        "capability": {"available": True, "capabilities": capabilities, "accepts_effort": accepts_effort,
                       "max_effort": max_effort, "observed_at": observed, "evidence": dict(evidence)},
        "economics": {"currency": "USD", "input_per_mtok": None, "output_per_mtok": None,
                      "observed_at": observed, "evidence": dict(evidence)},
        "quality": {"rank": rank, "score": None, "observed_at": observed, "evidence": dict(evidence)},
    }


def _glm_entry(tiers: list[str], rank: int, api: tuple[float, float, float], plan: tuple[float, float, float]) -> dict:
    entry = _bootstrap_entry(tiers, _FULL, True, "max", rank, _GLM_REF)
    entry["capability"]["effort_map"] = dict(GLM_EFFORT_MAP)
    entry["capability"]["thinking"] = "always_on"
    entry["economics"].update({
        "input_per_mtok": api[0], "cached_input_per_mtok": api[1], "output_per_mtok": api[2],
        "plan_credits": {"unit": "credits", "input_multiplier": plan[0], "cached_multiplier": plan[1],
                         "output_multiplier": plan[2], "divisor": GLM_CREDIT_DIVISOR,
                         "off_peak_factor": GLM_OFF_PEAK_FACTOR},
    })
    return entry


_FULL = ["code", "reasoning", "tool_use", "long_context"]
_DEEPSEEK_REF = ("docs/requests/portable-model-routing-dynamic-provider-catalog.md s11 (DeepSeek ids, 1M context, "
                 "peak/off-peak pricing per 1M tokens, 2026-10-01); the 16:30-00:30 UTC off-peak window is not in the "
                 "request and is unverified bootstrap evidence; tier placement is not a quality ranking")
DEEPSEEK_EFFORT_MAP = {"low": "high", "medium": "high", "high": "high", "xhigh": "max", "max": "max"}
DEEPSEEK_OFF_PEAK_WINDOW = {"start": "16:30", "end": "00:30"}
_CLAUDE_REF = "routingctl.py MODEL_MAP_VERSION 2026-09-30-v6"
_CODEX_REF = "codex debug models, CLI 0.159.2, 2026-09-30"
_GLM_REF = ("docs/requests/portable-model-routing-dynamic-provider-catalog.md s10 (Z.AI GLM-5.3 pricing and "
            "Coding Plan credit multipliers, 2026-10-01); tier placement is bootstrap evidence only")
GLM_EFFORT_MAP = {"low": "low", "medium": "high", "high": "high", "xhigh": "max", "max": "max"}
GLM_CREDIT_DIVISOR = 10000
GLM_OFF_PEAK_FACTOR = 0.5


def _deepseek_entry(tiers: list[str], rank: int, capabilities: list[str], peak: tuple[float, float, float],
                    off_peak: tuple[float, float, float]) -> dict:
    """`peak`/`off_peak` are (cache-miss input, cache-hit input, output) USD per 1M tokens."""
    entry = _bootstrap_entry(tiers, capabilities, True, "max", rank, _DEEPSEEK_REF)
    entry["capability"]["effort_map"] = dict(DEEPSEEK_EFFORT_MAP)
    entry["capability"]["thinking"] = "optional"
    entry["economics"].update({
        "input_per_mtok": peak[0], "cached_input_per_mtok": peak[1], "output_per_mtok": peak[2],
        "off_peak": {"input_per_mtok": off_peak[0], "cached_input_per_mtok": off_peak[1],
                     "output_per_mtok": off_peak[2], "window_utc": dict(DEEPSEEK_OFF_PEAK_WINDOW)},
    })
    return entry


_MUSE_REF = ("docs/requests/portable-model-routing-dynamic-provider-catalog.md s2.4/s12/s78; "
             "Muse Spark 1.3 id and effort vocabulary not yet verified against the muse CLI")

# Mirrors the 2026-09-30 provider evidence; the advanced tier is intentionally
# empty for Claude and Codex (skipped upward, never filled by invention).
BOOTSTRAP_CATALOG: dict = {
    "schema_version": SCHEMA_VERSION,
    "catalog_version": "2026-10-01-bootstrap-v4",
    "providers": {
        "claude": {"models": {
            "haiku": _bootstrap_entry(["economy"], ["code", "tool_use"], False, None, 1, _CLAUDE_REF),
            "claude-sonnet-5-5": _bootstrap_entry(["standard"], _FULL, True, "max", 2, _CLAUDE_REF),
            "claude-opus-5-5": _bootstrap_entry(["strong"], _FULL, True, "max", 4, _CLAUDE_REF),
            "claude-fable-5-1": _bootstrap_entry(["max"], _FULL, True, "max", 5, _CLAUDE_REF),
        }},
        "codex": {"models": {
            "gpt-6-luna": _bootstrap_entry(["economy"], ["code", "tool_use"], True, "max", 1, _CODEX_REF),
            "gpt-6.1-sol": _bootstrap_entry(["standard"], _FULL, True, "max", 2, _CODEX_REF),
            "gpt-6-astra": _bootstrap_entry(["strong", "max"], _FULL, True, "max", 5, _CODEX_REF),
        }},
        "muse": {"models": {
            "muse-spark-1.3": _bootstrap_entry(["advanced"], _FULL, True, "high", 3, _MUSE_REF),
        }},
        "glm": {"models": {
            "glm-5.3-flash": _glm_entry(["economy", "standard"], 2, (0.15, 0.03, 0.50), (2.3, 0.56, 8)),
            "glm-5.3": _glm_entry(["advanced"], 3, (1.40, 0.26, 4.40), (6.9, 1.7, 24)),
        }},
        "deepseek": {"models": {
            "deepseek-flash": _deepseek_entry(["economy", "standard"], 2, [*_FULL, "vision"],
                                              (0.30, 0.006, 1.20), (0.15, 0.003, 0.60)),
            "deepseek-v4-pro": _deepseek_entry(["advanced"], 3, _FULL,
                                               (1.32, 0.044, 3.96), (0.66, 0.022, 1.98)),
        }},
    },
}


def credits(economics: dict, input_tokens: int, cached_input_tokens: int, output_tokens: int, *, off_peak: bool = False) -> float:
    """Coding Plan credits: (in*mi + cached*mc + out*mo) / divisor, times the off-peak factor."""
    plan = economics.get("plan_credits")
    if not plan:
        raise CatalogError([("economics.plan_credits", "model has no plan credit formula")])
    for name, tokens in (("input_tokens", input_tokens), ("cached_input_tokens", cached_input_tokens), ("output_tokens", output_tokens)):
        if not isinstance(tokens, int) or isinstance(tokens, bool) or tokens < 0:
            raise CatalogError([(name, "must be a non-negative integer")])
    total = (input_tokens * plan["input_multiplier"] + cached_input_tokens * plan["cached_multiplier"]
             + output_tokens * plan["output_multiplier"]) / plan["divisor"]
    return total * plan["off_peak_factor"] if off_peak else total


def is_off_peak(economics: dict, at: datetime) -> bool:
    """True when `at` (converted to UTC; naive means UTC) is inside the daily window: start inclusive, end exclusive."""
    block = economics.get("off_peak")
    if not block:
        return False
    at = at.astimezone(timezone.utc) if at.tzinfo else at
    now = at.hour * 60 + at.minute
    start, end = _clock_minutes(block["window_utc"]["start"]), _clock_minutes(block["window_utc"]["end"])
    return start <= now < end if start < end else now >= start or now < end


def api_cost_usd(economics: dict, input_tokens: int, cached_input_tokens: int, output_tokens: int,
                 *, at: datetime | None = None) -> float:
    """API USD cost; `input_tokens` are uncached (cache-miss), cached ones bill at the cache-hit rate.

    With `at` and an `off_peak` block, off-peak rates apply inside the window; otherwise peak rates.
    """
    source = economics["off_peak"] if at is not None and is_off_peak(economics, at) else economics
    rates = (source.get("input_per_mtok"), source.get("cached_input_per_mtok"), source.get("output_per_mtok"))
    if any(rate is None for rate in rates):
        raise CatalogError([("economics", "unknown price; cannot compute cost")])
    return (input_tokens * rates[0] + cached_input_tokens * rates[1] + output_tokens * rates[2]) / 1_000_000


def native_effort(provider: str, model_id: str, effort: str, catalog: dict | None = None) -> str:
    """Map a skill effort to the model's native effort via catalog metadata; identity when no map exists."""
    if effort not in EFFORT_ORDER:
        raise CatalogError([("effort", f"unknown effort {effort!r}")])
    entry = validate(catalog if catalog is not None else BOOTSTRAP_CATALOG)["providers"].get(provider, {}).get("models", {}).get(model_id)
    if entry is None:
        raise CatalogError([("model", f"{provider}/{model_id} is not in the catalog")])
    return (entry["capability"].get("effort_map") or {}).get(effort, effort)


def require_thinking(provider: str, model_id: str, enabled: bool, catalog: dict | None = None) -> None:
    """Reject a config that disables thinking on a model whose thinking is always on."""
    entry = validate(catalog if catalog is not None else BOOTSTRAP_CATALOG)["providers"].get(provider, {}).get("models", {}).get(model_id)
    if entry is None:
        raise CatalogError([("model", f"{provider}/{model_id} is not in the catalog")])
    if not enabled and entry["capability"].get("thinking") == "always_on":
        raise CatalogError([("thinking", f"{model_id} has thinking always on; a thinking-disabled config is invalid")])


def bootstrap_catalog() -> dict:
    return validate(BOOTSTRAP_CATALOG)


def provider_config_mapping(provider: str, catalog: dict | None = None) -> dict:
    """Derive `{models, max_effort_by_tier, models_without_effort}` for one provider from a catalog.

    Per tier the best-ranked available model wins; tiers without a candidate stay absent so the
    router skips them upward. A provider missing from the catalog yields an empty mapping.
    """
    body = validate(catalog if catalog is not None else BOOTSTRAP_CATALOG)["providers"].get(provider)
    models: dict[str, str] = {}
    caps: dict[str, str] = {}
    no_effort: list[str] = []
    ranks: dict[str, int] = {}
    for model_id, entry in (body or {}).get("models", {}).items():
        capability = entry["capability"]
        if not capability["available"]:
            continue
        if not capability["accepts_effort"]:
            no_effort.append(model_id)
        rank = entry["quality"]["rank"] or len(TIER_ORDER)
        for tier in entry["tiers"]:
            if tier in models and ranks[tier] <= rank:
                continue
            models[tier] = model_id
            ranks[tier] = rank
            if capability["accepts_effort"] and capability["max_effort"]:
                caps[tier] = capability["max_effort"]
            else:
                caps.pop(tier, None)
    return {"models": models, "max_effort_by_tier": caps, "models_without_effort": no_effort}
