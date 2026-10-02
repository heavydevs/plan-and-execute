#!/usr/bin/env python3
"""Fixture corpus and invariants for the deterministic delegation gate.

Covers tool / keep_root / delegate decisions, the coordination-overhead
threshold, depth>1 exception, fan-out, write-scope, token and output limits,
selector sticky consumption and TODO 015 rollup accounting. Asserts that no
fixture lowers a floor or routes to an unconfigured provider, that output is
byte-stable, and that `delegate` spawns no process and opens no socket.
"""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import routing_telemetry as rt  # noqa: E402
import routingctl  # noqa: E402

TIERS = routingctl.TIER_ORDER
EFFORTS = routingctl.EFFORT_ORDER
DOC = SCRIPTS.parent / "references" / "DELEGATION.md"

SONNET = {"provider": "claude", "model": "claude-sonnet-5-5", "tier": "standard", "effort": "medium"}
DISCOVERY = {"signals": ["exploration"], "providers": ["claude", "codex"], "agent_tier": "strong",
             "independent_units": 6, "read_only": True, "unit_tokens": 40000}

# Each fixture: request and the expected decision subset.
CORPUS: list[dict] = [
    {"id": "D01-tool", "request": {"signals": ["deterministic_lookup"], "providers": ["claude"], "agent_tier": "economy"},
     "expect": {"decision": "tool", "fan_out": 0, "route": None, "role": None, "reasons": ["deterministic_tool"]}},
    {"id": "D02-keep-high-affinity-sequential",
     "request": {"signals": ["bounded_implementation"], "providers": ["claude"], "agent_tier": "strong",
                 "write_scopes": [["src/a.py"]], "unit_tokens": 50000, "cache_affinity": "high"},
     "expect": {"decision": "keep_root", "fan_out": 0, "route": None, "reasons": ["high_affinity_sequential"]}},
    {"id": "D03-keep-sticky-route",
     "request": {"signals": ["bounded_implementation"], "providers": ["claude"], "agent_tier": "standard",
                 "independent_units": 2, "write_scopes": [["src/a.py"], ["src/b.py"]], "unit_tokens": 50000,
                 "cache_affinity": "high", "previous_route": SONNET},
     "expect": {"decision": "keep_root", "reasons": ["sticky_route"]}, "sticky_applied": True},
    {"id": "D04-delegate-read-only-discovery", "request": DISCOVERY,
     "expect": {"decision": "delegate", "fan_out": 4, "role": "scout", "reasons": ["fan_out_limit", "delegate"],
                "write_scopes": [[], [], [], []]},
     "route": ["claude", "haiku", "economy", "low"]},
    {"id": "D05-keep-coordination-overhead",
     "request": {**DISCOVERY, "unit_tokens": 8999},
     "expect": {"decision": "keep_root", "reasons": ["coordination_overhead"]}},
    {"id": "D06-delegate-at-overhead-threshold",
     "request": {**DISCOVERY, "independent_units": 2, "unit_tokens": 9000},
     "expect": {"decision": "delegate", "fan_out": 2, "reasons": ["delegate"]}},
    {"id": "D07-capability-gap-ignores-overhead",
     "request": {"signals": ["architecture_decision"], "providers": ["claude", "codex"], "agent_tier": "economy",
                 "read_only": True, "unit_tokens": 100},
     "expect": {"decision": "delegate", "fan_out": 1, "role": "analyst",
                "reasons": ["floor_above_agent_tier", "delegate"]},
     "route": ["claude", "claude-opus-5-5", "strong", "high"]},
    {"id": "D08-capability-gap-beats-affinity",
     "request": {"signals": ["cross_cutting_risk"], "providers": ["claude"], "agent_tier": "standard",
                 "write_scopes": [["db/migrate"]], "cache_affinity": "high", "previous_route": SONNET},
     "expect": {"decision": "delegate", "role": "implementer", "write_scopes": [["db/migrate"]]},
     "route": ["claude", "claude-opus-5-5", "strong", "high"]},
    {"id": "D09-keep-depth-limit",
     "request": {**DISCOVERY, "depth": 1},
     "expect": {"decision": "keep_root", "reasons": ["depth_limit"]}},
    {"id": "D10-depth-exception-read-only-gap",
     "request": {"signals": ["subtle_debugging"], "providers": ["claude"], "agent_tier": "standard", "depth": 1,
                 "independent_units": 3, "read_only": True, "unit_tokens": 20000},
     "expect": {"decision": "delegate", "fan_out": 1, "role": "analyst", "depth": {"current": 1, "worker": 2},
                "reasons": ["floor_above_agent_tier", "depth_exception_capability_gap", "fan_out_limit", "delegate"]}},
    {"id": "D11-depth-exception-denied-for-writer",
     "request": {"signals": ["subtle_debugging"], "providers": ["claude"], "agent_tier": "standard", "depth": 1,
                 "write_scopes": [["src/x.py"]]},
     "expect": {"decision": "delegate", "blocked": "depth_limit", "fan_out": 0, "route": None, "role": "debugger"}},
    {"id": "D12-depth-two-never-deeper",
     "request": {"signals": ["subtle_debugging"], "providers": ["claude"], "agent_tier": "standard", "depth": 2,
                 "read_only": True},
     "expect": {"decision": "delegate", "blocked": "depth_limit", "fan_out": 0}},
    {"id": "D13-write-fan-out-limit",
     "request": {"signals": ["bounded_implementation"], "providers": ["codex"], "agent_tier": "strong",
                 "independent_units": 3, "write_scopes": [["a"], ["b"], ["c"]], "unit_tokens": 30000},
     "expect": {"decision": "delegate", "fan_out": 2, "write_scopes": [["a"], ["b"]],
                "reasons": ["fan_out_limit", "delegate"]},
     "route": ["codex", "gpt-6.1-sol", "standard", "medium"]},
    {"id": "D14-write-scope-overlap-serializes",
     "request": {"signals": ["bounded_implementation"], "providers": ["claude"], "agent_tier": "strong",
                 "independent_units": 2, "write_scopes": [["src"], ["src/a.py", "docs"]], "unit_tokens": 30000},
     "expect": {"decision": "delegate", "fan_out": 1, "write_scopes": [["docs", "src", "src/a.py"]],
                "reasons": ["write_scope_overlap", "fan_out_limit", "delegate"]}},
    {"id": "D15-token-budget-limits-fan-out",
     "request": {**DISCOVERY, "token_budget": 100000},
     "expect": {"decision": "delegate", "fan_out": 2, "reasons": ["fan_out_limit", "token_budget_limit", "delegate"]}},
    {"id": "D16-token-budget-exhausted-keeps-root",
     "request": {**DISCOVERY, "token_budget": 42999},
     "expect": {"decision": "keep_root", "reasons": ["fan_out_limit", "token_budget_exhausted"]}},
    {"id": "D17-token-budget-exhausted-above-capability-blocks",
     "request": {"signals": ["architecture_decision"], "providers": ["claude"], "agent_tier": "economy",
                 "read_only": True, "token_budget": 1000},
     "expect": {"decision": "delegate", "blocked": "token_budget_exhausted", "fan_out": 0, "route": None}},
    {"id": "D18-worker-token-cap",
     "request": {**DISCOVERY, "independent_units": 1, "unit_tokens": 500000},
     "expect": {"decision": "delegate", "fan_out": 1, "reasons": ["worker_token_cap", "delegate"]}},
    {"id": "D19-unconfigured-tier-blocks-not-lowers",
     "request": {"signals": ["architecture_decision"], "providers": ["glm"], "agent_tier": "economy", "read_only": True},
     "expect": {"decision": "delegate", "blocked": "no_candidate", "fan_out": 0, "route": None}},
    {"id": "D20-provider-not-in-catalog-ignored",
     "request": {**DISCOVERY, "providers": ["acme", "codex"]},
     "expect": {"decision": "delegate", "fan_out": 4},
     "route": ["codex", "gpt-6-luna", "economy", "low"]},
]


def _records() -> list[dict]:
    """One attempt per worker kind with distinct native usage."""
    records = []
    task = {"id": "016", "task_class": "implementation", "validation_strength": "deterministic"}
    for index, kind in enumerate(rt.KINDS, start=1):
        stdout = json.dumps({"usage": {"input_tokens": 1000 * index, "cache_read_input_tokens": 500,
                                       "cache_creation_input_tokens": 10 * index, "output_tokens": 100 * index}})
        records.append(rt.build_record(task=task, route={"provider": "claude", "model": "m", "effort": "low"},
                                       profile={"name": "claude", "harness": "claude"}, kind=kind, stdout=stdout,
                                       outcome="completed", validation_pass=kind == "root"))
    return records


def _charged(index: int) -> int:
    return 1000 * index + 10 * index + 100 * index


def test_corpus() -> None:
    for fixture in CORPUS:
        result = routingctl.delegate_decision(fixture["request"])
        for key, value in fixture["expect"].items():
            actual = result[key]
            if isinstance(value, dict) and isinstance(actual, dict):
                actual = {k: actual[k] for k in value}
            assert actual == value, f"{fixture['id']}: {key}={actual!r}, expected {value!r}"
        if "route" in fixture:
            route = result["route"]
            assert [route["provider"], route["model"], route["tier"], route["effort"]] == fixture["route"], fixture["id"]
        if "sticky_applied" in fixture:
            assert result["sticky"]["applied"] is fixture["sticky_applied"], fixture["id"]


def test_invariants() -> None:
    for fixture in CORPUS:
        request = fixture["request"]
        result = routingctl.delegate_decision(request)
        floor = result["floor"]
        assert result["decision"] in ("tool", "keep_root", "delegate"), fixture["id"]
        assert result["schema"] == routingctl.DELEGATE_SCHEMA
        if result["decision"] != "delegate" or result["blocked"]:
            assert result["fan_out"] == 0 and result["route"] is None and result["write_scopes"] == [], fixture["id"]
        if result["decision"] == "tool":
            assert floor["tier"] == "tool" and result["sticky"] is None, fixture["id"]
            continue
        # Never keep work at root above its capability: that would lower the floor.
        gap = TIERS.index(floor["tier"]) > TIERS.index(routingctl.normalize_tier(request["agent_tier"]))
        if gap:
            assert result["decision"] == "delegate", fixture["id"]
        route = result["route"]
        if route is not None:
            assert TIERS.index(route["tier"]) >= TIERS.index(floor["tier"]), fixture["id"]
            assert EFFORTS.index(route["effort"]) >= EFFORTS.index(floor["effort"]), fixture["id"]
            assert route["provider"] in request["providers"], fixture["id"]
            limit = routingctl.MAX_FAN_OUT["read_only" if request.get("read_only") else "write"]
            assert 1 <= result["fan_out"] <= min(limit, request.get("independent_units", 1)), fixture["id"]
            assert len(result["write_scopes"]) == result["fan_out"], fixture["id"]
            assert result["depth"]["worker"] <= routingctl.EXCEPTION_DEPTH, fixture["id"]
            if result["depth"]["worker"] > routingctl.MAX_DEPTH:
                assert gap and request.get("read_only") and result["fan_out"] == 1, fixture["id"]
            budgets = result["budgets"]
            assert budgets["tokens_per_worker"] <= routingctl.MAX_WORKER_TOKENS
            remaining = result["accounting"]["remaining_tokens"]
            if remaining is not None:
                assert budgets["tokens_per_worker"] * result["fan_out"] <= remaining, fixture["id"]
        configured = set(request["providers"])
        for other in ("claude", "codex", "glm", "deepseek", "muse"):
            if other not in configured and result["route"] is not None:
                assert other not in json.dumps(result["route"]), fixture["id"]


def test_pinned_thresholds_and_doc() -> None:
    assert routingctl.COORDINATION_OVERHEAD_MAX == 0.25
    assert routingctl.WORKER_OVERHEAD_TOKENS == 3000
    assert routingctl.MAX_DEPTH == 1 and routingctl.EXCEPTION_DEPTH == 2
    assert routingctl.MAX_FAN_OUT == {"read_only": 4, "write": 2}
    assert routingctl.RESULT_MAX_BYTES == 4000 and routingctl.MAX_WORKER_TOKENS == 200_000
    text = DOC.read_text(encoding="utf-8")
    for needle in ("COORDINATION_OVERHEAD_MAX = 0.25", "WORKER_OVERHEAD_TOKENS = 3000", "MAX_DEPTH = 1",
                   "EXCEPTION_DEPTH = 2", "read_only: 4", "write: 2", "RESULT_MAX_BYTES = 4000",
                   "MAX_WORKER_TOKENS = 200000", "routingctl.py delegate", routingctl.DELEGATE_SCHEMA):
        assert needle in text, needle
    assert text.count("COORDINATION_OVERHEAD_MAX = 0.25") == 1, "threshold must be stated once"
    for role, contract in routingctl.DELEGATION_ROLES.items():
        assert f"`{role}`" in text, role
    for key in routingctl.RESULT_KEYS:
        assert f'"{key}"' in text, key
    assert "references/DELEGATION.md" in (SCRIPTS / "routingctl.py").read_text(encoding="utf-8")


def test_accounting_reads_rollup_for_every_kind() -> None:
    records = _records()
    rollup = rt.rollup(records)
    accounting = routingctl.delegation_accounting(rollup, 100000)
    assert accounting["source"] == "routing_telemetry.rollup"
    assert accounting["kinds"] == list(rt.KINDS) and list(accounting["by_kind"]) == list(rt.KINDS)
    expected = {kind: _charged(index) for index, kind in enumerate(rt.KINDS, start=1)}
    assert accounting["by_kind"] == expected
    assert accounting["spent_tokens"] == sum(expected.values())
    assert accounting["remaining_tokens"] == 100000 - sum(expected.values())
    # Dropping any one worker kind changes the spend: every kind is counted.
    for kind in rt.KINDS:
        partial = routingctl.delegation_accounting(rt.rollup([r for r in records if r["kind"] != kind]), None)
        assert partial["spent_tokens"] == accounting["spent_tokens"] - expected[kind], kind
    truncated = rt.rollup(records, max_bytes=10)
    assert truncated["truncated"] and not truncated["by_kind"]
    assert routingctl.delegation_accounting(truncated, None)["spent_tokens"] == accounting["spent_tokens"]
    tampered = json.loads(json.dumps(rollup))
    del tampered["by_kind"]["diagnostic"]
    try:
        routingctl.delegation_accounting(tampered, None)
    except routingctl.RoutingError:
        pass
    else:
        raise AssertionError("rollup missing a worker kind must be rejected")
    # Unreported usage is null, never estimated.
    empty = routingctl.delegation_accounting(rt.rollup([]), 5000)
    assert empty["spent_tokens"] is None and empty["remaining_tokens"] == 5000
    # Spend recorded in the rollup reduces fan-out.
    budget = sum(expected.values()) + 2 * 43000
    result = routingctl.delegate_decision({**DISCOVERY, "token_budget": budget, "rollup": rollup})
    assert result["fan_out"] == 2 and "token_budget_limit" in result["reasons"]


def test_worker_result_contract() -> None:
    scout = routingctl.delegate_decision(DISCOVERY)
    good = {"status": "done", "role": "scout", "summary": "found 3 call sites",
            "findings": [{"file": "a.py", "line": 3, "claim": "calls x"}], "changed_files": [],
            "validations": [], "blocked_reason": None}
    assert routingctl.check_worker_result(scout, 0, good) == []
    assert any("outside write scope" in p for p in routingctl.check_worker_result(scout, 0, {**good, "changed_files": ["a.py"]}))
    assert any("bytes" in p for p in routingctl.check_worker_result(
        scout, 0, {**good, "findings": [{"claim": "x" * 600}] * 8}))
    assert routingctl.check_worker_result(scout, 0, {**good, "extra": 1})
    assert routingctl.check_worker_result(scout, 0, {**good, "status": "blocked"})
    writer = routingctl.delegate_decision(CORPUS[12]["request"])
    edit = {**good, "role": "implementer", "changed_files": ["b/x.py"]}
    assert routingctl.check_worker_result(writer, 1, edit) == []
    assert routingctl.check_worker_result(writer, 0, edit)


def test_invalid_requests() -> None:
    bad = [
        [],
        {**DISCOVERY, "unexpected": 1},
        {**DISCOVERY, "agent_tier": "huge"},
        {**DISCOVERY, "independent_units": 0},
        {**DISCOVERY, "write_scopes": [["a"]]},
        {**DISCOVERY, "role": "implementer"},
        {"signals": ["bounded_implementation"], "providers": ["claude"], "agent_tier": "strong"},
        {"signals": ["bounded_implementation"], "providers": ["claude"], "agent_tier": "strong",
         "independent_units": 2, "write_scopes": [["a"]]},
        {**DISCOVERY, "rollup": {"by_kind": {}}},
        {**DISCOVERY, "depth": -1},
    ]
    for request in bad:
        try:
            routingctl.delegate_decision(request)
        except routingctl.RoutingError:
            continue
        raise AssertionError(f"request must be rejected: {request}")


def test_no_process_or_socket_during_delegate() -> None:
    def forbidden(*_args, **_kwargs):
        raise AssertionError("delegate must not spawn processes or open sockets")
    saved = (subprocess.Popen, subprocess.run, os.system, socket.socket, socket.create_connection)
    subprocess.Popen = subprocess.run = os.system = forbidden  # type: ignore[assignment]
    socket.socket = socket.create_connection = forbidden  # type: ignore[assignment,misc]
    try:
        for fixture in CORPUS:
            first = routingctl.delegate_json(fixture["request"])
            assert first == routingctl.delegate_json(fixture["request"]), fixture["id"]
    finally:
        subprocess.Popen, subprocess.run, os.system, socket.socket, socket.create_connection = saved


def test_cli_delegate() -> None:
    request = json.dumps(DISCOVERY)
    outputs = []
    for _ in range(2):
        proc = subprocess.run([sys.executable, str(SCRIPTS / "routingctl.py"), "delegate", "--request", "-"],
                              input=request, capture_output=True, text=True, encoding="utf-8", timeout=60)
        assert proc.returncode == 0, proc.stderr
        outputs.append(proc.stdout)
    assert outputs[0] == outputs[1]
    assert json.loads(outputs[0])["decision"] == "delegate"
    with tempfile.TemporaryDirectory(prefix="dlg") as tmp:
        plan = Path(tmp)
        for record in _records():
            assert rt.append_record(plan, record)
        proc = subprocess.run([sys.executable, str(SCRIPTS / "routingctl.py"), "delegate", "--request", "-",
                               "--telemetry", str(plan)], input=json.dumps({**DISCOVERY, "token_budget": 10 ** 6}),
                              capture_output=True, text=True, encoding="utf-8", timeout=60)
        assert proc.returncode == 0, proc.stderr
        accounting = json.loads(proc.stdout)["accounting"]
        assert accounting["source"] == "routing_telemetry.rollup"
        assert accounting["spent_tokens"] == sum(_charged(i) for i in range(1, len(rt.KINDS) + 1))


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"delegation self-test passed ({len(tests)} tests, {len(CORPUS)} fixtures).")
