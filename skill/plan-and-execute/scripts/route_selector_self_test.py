#!/usr/bin/env python3
"""Fixture corpus and invariants for the deterministic candidate selector.

Covers floors, capability, availability, quality, cache, subscription,
sticky routing and tie-break cases; asserts byte-identical repeated output,
ladder equivalence with only claude/codex configured, and that `select`
spawns no process and opens no socket.
"""
from __future__ import annotations

import copy
import itertools
import json
import os
import socket
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import model_catalog  # noqa: E402
import routingctl  # noqa: E402

TIERS = routingctl.TIER_ORDER
EFFORTS = routingctl.EFFORT_ORDER


def _synthetic_catalog() -> dict:
    """One provider `p` with same-cost models to exercise quality and tie-break stages."""
    def entry(tiers, rank, available=True):
        observed = "2026-10-01T00:00:00Z"
        evidence = {"source": "user", "ref": "selector fixture"}
        return {
            "tiers": tiers,
            "capability": {"available": available, "capabilities": ["code", "tool_use"], "accepts_effort": True,
                           "max_effort": "max", "observed_at": observed, "evidence": dict(evidence)},
            "economics": {"currency": "USD", "input_per_mtok": 1.0, "cached_input_per_mtok": 0.1,
                          "output_per_mtok": 2.0, "observed_at": observed, "evidence": dict(evidence)},
            "quality": {"rank": rank, "score": None, "observed_at": observed, "evidence": dict(evidence)},
        }
    return {"schema_version": 1, "catalog_version": "selector-fixture-v1", "providers": {"p": {"models": {
        "m-b": entry(["standard"], 2),
        "m-a": entry(["standard"], 2),
        "m-c": entry(["standard"], 3),
        "m-weak": entry(["standard"], 1),
        "m-strong": entry(["strong"], 4),
    }}}}


SYNTHETIC = _synthetic_catalog()
TOKENS = {"input_tokens": 200000, "cached_input_tokens": 150000, "output_tokens": 20000}
API = {"glm": {"mode": "api"}, "deepseek": {"mode": "api"}}

# Each fixture: request, optional catalog, expected floor and expected outcome subset.
CORPUS: list[dict] = [
    # --- floors
    {"id": "F01-floor-economy", "request": {"signals": ["exploration"], "providers": ["claude"]},
     "floor": ["economy", "low"], "expect": {"route": ["claude", "haiku", "economy", "low"], "effort_flag": False}},
    {"id": "F02-floor-standard-codex", "request": {"signals": ["bounded_implementation"], "providers": ["codex"]},
     "floor": ["standard", "medium"], "expect": {"route": ["codex", "gpt-6.1-sol", "standard", "medium"]}},
    {"id": "F03-floor-weak-validation", "request": {"signals": ["bounded_implementation", "weak_validation"], "providers": ["claude"]},
     "floor": ["strong", "high"], "expect": {"route": ["claude", "claude-opus-5-5", "strong", "high"]}},
    {"id": "F04-floor-tool", "request": {"signals": ["deterministic_lookup"], "providers": ["claude"]},
     "floor": ["tool", "none"], "expect": {"decision": "tool"}},
    {"id": "F05-empty-advanced-lifts", "request": {"route": {"tier": "advanced", "effort": "medium"}, "providers": ["claude"]},
     "floor": ["advanced", "medium"], "expect": {"route": ["claude", "claude-opus-5-5", "strong", "medium"], "tier_lifted": True}},
    {"id": "F06-advanced-muse", "request": {"route": {"tier": "advanced", "effort": "medium"}, "providers": ["claude", "muse"]},
     "floor": ["advanced", "medium"], "expect": {"route": ["muse", "muse-spark-1.3", "advanced", "medium"], "tier_lifted": False}},
    {"id": "F07-alias-tier", "request": {"route": {"tier": "L4", "effort": "medium"}, "providers": ["codex"]},
     "floor": ["strong", "medium"], "expect": {"route": ["codex", "gpt-6-astra", "strong", "medium"]}},
    # --- capability
    {"id": "F08-capability-vision", "request": {"signals": ["bounded_implementation"], "providers": ["claude", "deepseek"],
                                                "required_capabilities": ["vision"]},
     "floor": ["standard", "medium"], "expect": {"route": ["deepseek", "deepseek-flash", "standard", "medium"],
                                                 "dropped": {"claude/claude-sonnet-5-5@standard": "missing_capability:vision"}}},
    {"id": "F09-capability-effort-cap", "request": {"route": {"tier": "advanced", "effort": "xhigh"}, "providers": ["muse", "glm"]},
     "floor": ["advanced", "xhigh"], "expect": {"route": ["glm", "glm-5.3", "advanced", "xhigh"],
                                                "dropped": {"muse/muse-spark-1.3@advanced": "effort_above_max:high"}}},
    {"id": "F10-capability-none", "request": {"signals": ["bounded_implementation"], "providers": ["claude"],
                                              "required_capabilities": ["vision"]},
     "floor": ["standard", "medium"], "expect": {"decision": "no_candidate"}},
    # --- availability
    {"id": "F11-outage-same-tier", "request": {"signals": ["subtle_debugging"], "providers": ["claude", "codex"],
                                               "availability": {"claude": "outage"}},
     "floor": ["strong", "medium"], "expect": {"route": ["codex", "gpt-6-astra", "strong", "medium"], "tier_lifted": False,
                                               "dropped": {"claude/claude-opus-5-5@strong": "outage"}}},
    {"id": "F12-model-outage-equivalent-first", "request": {"signals": ["bounded_implementation"], "providers": ["claude", "codex"],
                                                            "availability": {"claude/claude-sonnet-5-5": "outage"}},
     "floor": ["standard", "medium"], "expect": {"route": ["codex", "gpt-6.1-sol", "standard", "medium"], "tier_lifted": False}},
    {"id": "F13-model-outage-lifts-last", "request": {"signals": ["bounded_implementation"], "providers": ["claude"],
                                                      "availability": {"claude/claude-sonnet-5-5": "quota_exhausted"}},
     "floor": ["standard", "medium"], "expect": {"route": ["claude", "claude-opus-5-5", "strong", "medium"], "tier_lifted": True}},
    {"id": "F14-unconfigured-provider-skipped", "request": {"route": {"tier": "advanced", "effort": "low"}, "providers": ["codex"]},
     "floor": ["advanced", "low"], "expect": {"route": ["codex", "gpt-6-astra", "strong", "low"], "tier_lifted": True}},
    # --- quality constraint and tie-break (synthetic catalog)
    {"id": "F15-quality-rank-below-tier", "catalog": "synthetic", "request": {"signals": ["bounded_implementation"], "providers": ["p"]},
     "floor": ["standard", "medium"], "expect": {"route": ["p", "m-c", "standard", "medium"],
                                                 "dropped": {"p/m-weak@standard": "quality_rank_below_tier:1"}}},
    {"id": "F16-tie-model-id", "catalog": "synthetic", "request": {"signals": ["bounded_implementation"], "providers": ["p"],
                                                                   "availability": {"p/m-c": "outage"}},
     "floor": ["standard", "medium"], "expect": {"route": ["p", "m-a", "standard", "medium"]}},
    {"id": "F17-min-quality-score-unknown", "catalog": "synthetic", "request": {"signals": ["bounded_implementation"], "providers": ["p"],
                                                                                "min_quality_score": 0.5},
     "floor": ["standard", "medium"], "expect": {"decision": "no_candidate"}},
    {"id": "F18-tie-provider-order-codex", "request": {"signals": ["bounded_implementation"], "providers": ["codex", "claude"]},
     "floor": ["standard", "medium"], "expect": {"route": ["codex", "gpt-6.1-sol", "standard", "medium"]}},
    {"id": "F19-tie-provider-order-claude", "request": {"signals": ["bounded_implementation"], "providers": ["claude", "codex"]},
     "floor": ["standard", "medium"], "expect": {"route": ["claude", "claude-sonnet-5-5", "standard", "medium"]}},
    # --- API economics with cache tokens
    {"id": "F20-api-cache-glm", "request": {"signals": ["bounded_implementation"], "providers": ["deepseek", "glm"],
                                            "billing": API, "tokens": TOKENS},
     "floor": ["standard", "medium"], "expect": {"route": ["glm", "glm-5.3-flash", "standard", "medium"], "cash": 0.022}},
    {"id": "F21-api-off-peak-deepseek", "request": {"signals": ["bounded_implementation"], "providers": ["deepseek", "glm"],
                                                    "billing": API, "tokens": TOKENS, "at": "2026-10-01T17:00:00Z"},
     "floor": ["standard", "medium"], "expect": {"route": ["deepseek", "deepseek-flash", "standard", "medium"], "cash": 0.01995}},
    {"id": "F22-cache-hit-only-on-previous", "request": {
        "signals": ["bounded_implementation"], "providers": ["glm", "deepseek"], "billing": API,
        "tokens": {"input_tokens": 200000, "cached_input_tokens": 190000, "output_tokens": 20000},
        "previous_route": {"provider": "deepseek", "model": "deepseek-flash", "tier": "standard", "effort": "medium"},
        "cache_affinity": "low"},
     "floor": ["standard", "medium"], "expect": {"route": ["deepseek", "deepseek-flash", "standard", "medium"],
                                                 "cash": 0.02814, "sticky": False}},
    {"id": "F23-cache-hit-shared-prefix", "request": {
        "signals": ["bounded_implementation"], "providers": ["glm", "deepseek"], "billing": API,
        "tokens": {"input_tokens": 200000, "cached_input_tokens": 190000, "output_tokens": 20000}},
     "floor": ["standard", "medium"], "expect": {"route": ["glm", "glm-5.3-flash", "standard", "medium"], "cash": 0.0172}},
    # --- subscription economics
    {"id": "F24-subscription-beats-api", "request": {
        "signals": ["bounded_implementation"], "providers": ["deepseek", "glm"], "tokens": TOKENS,
        "billing": {"deepseek": {"mode": "api"}, "glm": {"mode": "subscription", "window_capacity": 100000, "window_used": 0.2}}},
     "floor": ["standard", "medium"], "expect": {"route": ["glm", "glm-5.3-flash", "standard", "medium"], "cash": 0.0, "quota": 0.000359}},
    {"id": "F25-subscription-window-exhausted", "request": {
        "signals": ["bounded_implementation"], "providers": ["glm", "deepseek"], "tokens": TOKENS,
        "billing": {"deepseek": {"mode": "api"}, "glm": {"mode": "subscription", "window_capacity": 1000, "window_used": 0.99}}},
     "floor": ["standard", "medium"], "expect": {"route": ["deepseek", "deepseek-flash", "standard", "medium"],
                                                 "dropped": {"glm/glm-5.3-flash@standard": "quota_window_exhausted"}}},
    {"id": "F26-subscription-overage-api", "request": {
        "signals": ["bounded_implementation"], "providers": ["deepseek", "glm"], "tokens": TOKENS,
        "billing": {"deepseek": {"mode": "api"},
                    "glm": {"mode": "subscription", "window_capacity": 1000, "window_used": 0.99, "overage": "api"}}},
     "floor": ["standard", "medium"], "expect": {"route": ["glm", "glm-5.3-flash", "standard", "medium"], "cash": 0.022}},
    {"id": "F27-subscription-off-peak-credits", "request": {
        "signals": ["bounded_implementation"], "providers": ["glm"], "tokens": TOKENS,
        "billing": {"glm": {"mode": "subscription", "window_capacity": 100000, "off_peak": True}}},
     "floor": ["standard", "medium"], "expect": {"route": ["glm", "glm-5.3-flash", "standard", "medium"], "quota": 0.0001795}},
    # --- sticky routing / cache affinity
    {"id": "F28-sticky-high-affinity", "request": {
        "signals": ["bounded_implementation"], "providers": ["claude", "codex"], "cache_affinity": "high",
        "previous_route": {"provider": "codex", "model": "gpt-6.1-sol", "tier": "standard", "effort": "medium"}},
     "floor": ["standard", "medium"], "expect": {"route": ["codex", "gpt-6.1-sol", "standard", "medium"], "sticky": True}},
    {"id": "F29-sticky-broken-by-semantic-failure", "request": {
        "signals": ["bounded_implementation"], "providers": ["claude", "codex"], "cache_affinity": "high",
        "last_failure_class": "semantic",
        "previous_route": {"provider": "codex", "model": "gpt-6.1-sol", "tier": "standard", "effort": "medium"}},
     "floor": ["standard", "medium"], "expect": {"route": ["claude", "claude-sonnet-5-5", "standard", "medium"], "sticky": False,
                                                 "sticky_reason": "failure:semantic"}},
    {"id": "F30-sticky-below-floor", "request": {
        "signals": ["bounded_implementation"], "providers": ["claude", "codex"], "cache_affinity": "high",
        "previous_route": {"provider": "codex", "model": "gpt-6-luna", "tier": "economy", "effort": "low"}},
     "floor": ["standard", "medium"], "expect": {"route": ["claude", "claude-sonnet-5-5", "standard", "medium"], "sticky": False,
                                                 "sticky_reason": "previous_route_ineligible"}},
    {"id": "F31-sticky-above-floor", "request": {
        "signals": ["bounded_implementation"], "providers": ["claude", "codex"], "cache_affinity": "high",
        "previous_route": {"provider": "codex", "model": "gpt-6-astra", "tier": "strong", "effort": "medium"}},
     "floor": ["standard", "medium"], "expect": {"route": ["codex", "gpt-6-astra", "strong", "medium"], "sticky": True}},
    {"id": "F32-sticky-previous-outage", "request": {
        "signals": ["bounded_implementation"], "providers": ["claude", "codex"], "cache_affinity": "high",
        "availability": {"codex": "rate_limited"},
        "previous_route": {"provider": "codex", "model": "gpt-6.1-sol", "tier": "standard", "effort": "medium"}},
     "floor": ["standard", "medium"], "expect": {"route": ["claude", "claude-sonnet-5-5", "standard", "medium"], "sticky": False,
                                                 "sticky_reason": "previous_route_ineligible"}},
    {"id": "F33-sticky-cheaper-alternative", "request": {
        "signals": ["bounded_implementation"], "providers": ["glm", "deepseek"], "billing": API, "cache_affinity": "high",
        "tokens": {"input_tokens": 200000, "cached_input_tokens": 50000, "output_tokens": 20000},
        "previous_route": {"provider": "deepseek", "model": "deepseek-flash", "tier": "standard", "effort": "medium"}},
     "floor": ["standard", "medium"], "expect": {"route": ["glm", "glm-5.3-flash", "standard", "medium"], "sticky": False,
                                                 "sticky_reason": "cheaper_alternative"}},
    {"id": "F34-sticky-effort-below-floor", "request": {
        "signals": ["bounded_implementation", "weak_validation"], "providers": ["claude", "codex"], "cache_affinity": "high",
        "previous_route": {"provider": "codex", "model": "gpt-6-astra", "tier": "strong", "effort": "medium"}},
     "floor": ["strong", "high"], "expect": {"route": ["claude", "claude-opus-5-5", "strong", "high"], "sticky": False,
                                             "sticky_reason": "previous_route_ineligible"}},
]


def _catalog(fixture: dict) -> dict | None:
    return SYNTHETIC if fixture.get("catalog") == "synthetic" else None


def _close(actual, expected) -> bool:
    return actual is not None and abs(actual - expected) < 1e-9


def _ranked_ids(result: dict) -> set[str]:
    return {item["candidate"] for item in result["explanation"]["ranking"]}


def _dropped(result: dict) -> dict[str, str]:
    out = {}
    for stage in result["explanation"]["stages"]:
        for item in stage["dropped"]:
            out[item["candidate"]] = item["reason"]
    return out


def check_fixture(fixture: dict) -> dict:
    result = routingctl.select_route(copy.deepcopy(fixture["request"]), _catalog(fixture))
    fid, expect = fixture["id"], fixture["expect"]
    assert [result["floor"]["tier"], result["floor"]["effort"]] == fixture["floor"], (fid, result["floor"])
    assert result["decision"] == expect.get("decision", "route"), (fid, result["decision"])
    if result["decision"] == "route":
        route = result["route"]
        got = [route["provider"], route["model"], route["tier"], route["effort"]]
        assert got == expect["route"], (fid, got)
        floor_tier = routingctl.normalize_tier(fixture["floor"][0])
        # Never below the floor: tier and effort both at or above it.
        assert TIERS.index(route["tier"]) >= TIERS.index(floor_tier), fid
        assert EFFORTS.index(route["effort"]) >= EFFORTS.index(fixture["floor"][1]), fid
        if "effort_flag" in expect:
            assert route["effort_flag"] is expect["effort_flag"], fid
        if "tier_lifted" in expect:
            assert result["explanation"]["tier_lifted"] is expect["tier_lifted"], fid
        cost = route["effective_cost"]
        if "cash" in expect:
            assert _close(cost["marginal_cash_cost"], expect["cash"]), (fid, cost)
        if "quota" in expect:
            assert _close(cost["quota_cost"], expect["quota"]), (fid, cost)
        if "sticky" in expect:
            assert result["sticky"]["applied"] is expect["sticky"], (fid, result["sticky"])
        if "sticky_reason" in expect:
            assert result["sticky"]["reason"] == expect["sticky_reason"], (fid, result["sticky"])
        assert route["ladder"][0] == {"tier": route["tier"], "effort": route["effort"], "model": route["model"]}, fid
    dropped = _dropped(result)
    for candidate, reason in expect.get("dropped", {}).items():
        assert dropped.get(candidate) == reason, (fid, candidate, dropped.get(candidate))
    # Candidates removed before economics never reach cost ranking.
    assert not (set(dropped) & _ranked_ids(result)), fid
    return result


def test_corpus() -> None:
    ids = [fixture["id"] for fixture in CORPUS]
    assert len(ids) == len(set(ids))
    for fixture in CORPUS:
        check_fixture(fixture)


def test_capability_drops_never_ranked() -> None:
    for fixture in CORPUS:
        result = routingctl.select_route(copy.deepcopy(fixture["request"]), _catalog(fixture))
        stages = {stage["stage"]: stage for stage in result["explanation"]["stages"]}
        capability = {item["candidate"] for item in stages["capability"]["dropped"]} if "capability" in stages else set()
        assert not capability & _ranked_ids(result), fixture["id"]


def _corpus_bytes() -> bytes:
    return "\n".join(routingctl.select_json(copy.deepcopy(f["request"]), _catalog(f)) for f in CORPUS).encode("utf-8")


def test_byte_identical() -> None:
    first, second = _corpus_bytes(), _corpus_bytes()
    assert first == second
    # Request key order must not change output either.
    for fixture in CORPUS:
        reordered = dict(reversed(list(copy.deepcopy(fixture["request"]).items())))
        assert routingctl.select_json(reordered, _catalog(fixture)) == routingctl.select_json(fixture["request"], _catalog(fixture))


def _signal_sets() -> list[list[str]]:
    primaries = [name for name in routingctl.PRIMARY_SIGNALS if routingctl.PRIMARY_SIGNALS[name][0] != "tool"]
    sets = []
    for primary in primaries:
        for size in range(len(routingctl.MODIFIER_SIGNALS) + 1):
            for modifiers in itertools.combinations(routingctl.MODIFIER_SIGNALS, size):
                if "weak_validation" in modifiers and "strong_validation" in modifiers:
                    continue
                sets.append([primary, *modifiers])
    return sets


def test_ladder_equivalence_claude_codex() -> None:
    config = routingctl.configure_config({})
    for provider_list in (["claude"], ["codex"], ["claude", "codex"], ["codex", "claude"]):
        provider = provider_list[0]
        cfg = config[provider]
        floors = [{"tier": tier, "effort": effort} for tier in TIERS for effort in EFFORTS]
        floors += [routingctl.minimum_route(signals) for signals in _signal_sets()]
        for floor in floors:
            result = routingctl.select_route({"route": floor, "providers": provider_list})
            rungs = routingctl.route_rungs(cfg, floor["tier"], floor["effort"])
            expected = [{"tier": t, "effort": e, "model": cfg["models"][t]} for t, e in rungs]
            route = result["route"]
            assert route["provider"] == provider, (provider_list, floor)
            assert route["ladder"] == expected, (provider_list, floor, route["ladder"], expected)
            assert route["effort_flag"] is routingctl.model_supports_effort(cfg, route["model"]), (provider, floor)


def test_no_process_or_socket_during_select() -> None:
    def forbidden(*_args, **_kwargs):
        raise AssertionError("select must not spawn processes or open sockets")
    saved = (subprocess.Popen, subprocess.run, os.system, socket.socket, socket.create_connection)
    subprocess.Popen = subprocess.run = os.system = forbidden  # type: ignore[assignment]
    socket.socket = socket.create_connection = forbidden  # type: ignore[assignment,misc]
    try:
        for fixture in CORPUS:
            routingctl.select_json(copy.deepcopy(fixture["request"]), _catalog(fixture))
    finally:
        subprocess.Popen, subprocess.run, os.system, socket.socket, socket.create_connection = saved


def test_request_validation() -> None:
    bad = [
        {"providers": ["claude"]},
        {"signals": ["exploration"], "route": {"tier": "economy", "effort": "low"}, "providers": ["claude"]},
        {"signals": ["exploration"]},
        {"signals": ["exploration"], "providers": ["claude"], "unexpected": 1},
        {"signals": ["exploration"], "providers": ["claude"], "required_capabilities": ["telepathy"]},
        {"route": {"tier": "huge", "effort": "low"}, "providers": ["claude"]},
        {"signals": ["exploration"], "providers": ["claude"], "billing": {"claude": {"mode": "barter"}}},
        {"signals": ["exploration"], "providers": ["claude"], "cache_affinity": "sometimes"},
        {"signals": ["exploration"], "providers": ["claude", "claude"]},
    ]
    for request in bad:
        try:
            routingctl.select_route(request)
        except routingctl.RoutingError:
            continue
        raise AssertionError(f"request must be rejected: {request}")


def test_cli_select() -> None:
    request = json.dumps(CORPUS[1]["request"])
    outputs = []
    for _ in range(2):
        proc = subprocess.run([sys.executable, str(SCRIPTS / "routingctl.py"), "select", "--request", "-"],
                              input=request, capture_output=True, text=True, encoding="utf-8", timeout=60)
        assert proc.returncode == 0, proc.stderr
        outputs.append(proc.stdout)
    assert outputs[0] == outputs[1]
    assert json.loads(outputs[0])["route"]["model"] == "gpt-6.1-sol"
    proc = subprocess.run([sys.executable, str(SCRIPTS / "routingctl.py"), "select", "--signals", "exploration",
                           "--providers", "claude"], capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert proc.returncode == 0, proc.stderr
    assert json.loads(proc.stdout)["route"]["model"] == "haiku"


def test_catalog_is_bootstrap_by_default() -> None:
    result = routingctl.select_route({"signals": ["exploration"], "providers": ["claude"]})
    assert result["explanation"]["catalog_version"] == model_catalog.BOOTSTRAP_CATALOG["catalog_version"]


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"route selector self-test passed ({len(tests)} tests, {len(CORPUS)} fixtures).")
