#!/usr/bin/env python3
"""Regression tests for adaptive provider routing, evidence-based escalation, and lazy provider guidance."""
from __future__ import annotations

import json
from pathlib import Path

import planctl
import routingctl

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REFERENCES = SKILL_DIR / "references"


def test_current_model_map() -> None:
    configured = routingctl.configure_config(planctl.default_config())
    assert configured["codex"]["models"] == {
        "economy": "gpt-6-luna",
        "standard": "gpt-6.1-sol",
        "strong": "gpt-6-astra",
        "max": "gpt-6-astra",
    }
    assert configured["claude"]["models"] == {
        "economy": "haiku",
        "standard": "claude-sonnet-5-5",
        "strong": "claude-opus-5-5",
        "max": "claude-fable-5-1",
    }
    assert configured["routing_policy"] == {
        "model_map_version": routingctl.MODEL_MAP_VERSION,
        "selection": "adaptive",
        "escalation": "evidence",
    }
    # planctl.default_config is itself catalog-backed: no second source of truth.
    assert planctl.default_config()["claude"]["models"]["max"] == "claude-fable-5-1"
    assert planctl.default_config()["codex"]["models"]["strong"] == "gpt-6-astra"
    assert planctl.default_config()["claude"]["models_without_effort"] == ["haiku"]
    assert routingctl.model_supports_effort(configured["claude"], "haiku") is False
    assert routingctl.model_supports_effort(configured["claude"], "sonnet") is True
    assert routingctl.model_supports_effort(configured["codex"], "gpt-6-luna") is True


def test_legacy_ceiling_state_is_replaced() -> None:
    legacy = planctl.default_config()
    legacy["codex"]["models"]["strong"] = "gpt-5.6-sol"
    legacy["codex"]["models"]["max"] = "gpt-5.6-sol"
    legacy["codex"]["max_effort_by_tier"]["max"] = "high"
    legacy["routing_policy"] = {
        "hard_ceiling": True,
        "max_tier": "strong",
        "max_effort": "high",
    }
    configured = routingctl.configure_config(legacy)
    assert configured["codex"]["models"]["strong"] == "gpt-6-astra"
    assert configured["codex"]["models"]["max"] == "gpt-6-astra"
    assert configured["codex"]["max_effort_by_tier"]["max"] == "max"
    assert "hard_ceiling" not in configured["routing_policy"]
    assert "max_tier" not in configured["routing_policy"]
    assert "max_effort" not in configured["routing_policy"]


def test_catalog_installer_is_idempotent() -> None:
    module = routingctl.install_current_model_catalog(planctl)
    first = module.default_config()
    module = routingctl.install_current_model_catalog(module)
    second = module.default_config()
    assert first == second
    assert second["codex"]["models"]["strong"] == "gpt-6-astra"


def test_escalation_ladders_follow_calibration() -> None:
    codex = routingctl.configure_config({})["codex"]
    rungs = routingctl.route_rungs(codex, "standard", "medium")
    # Codex never spends a Sol High retry before an Astra Low attempt.
    assert rungs[0] == ("standard", "medium")
    assert rungs[1] == ("strong", "low"), rungs
    assert ("standard", "high") not in rungs
    claude = routingctl.configure_config({})["claude"]
    rungs = routingctl.route_rungs(claude, "economy", "low")
    # Haiku accepts no effort, so the rung above economy/low is Sonnet Medium.
    assert rungs[1] == ("standard", "medium"), rungs
    # Evidence semantics.
    assert routingctl.escalation_step([], rungs) == 0
    assert routingctl.escalation_step(["mechanical"], rungs) == 0
    assert routingctl.escalation_step(["mechanical", "mechanical"], rungs) == 1
    assert routingctl.escalation_step(["environmental"] * 3, rungs) == 0
    assert rungs[routingctl.escalation_step(["semantic"], rungs)][0] == "standard"
    assert rungs[routingctl.escalation_step(["semantic", "semantic"], rungs)][0] == "strong"
    assert routingctl.escalation_step(["unknown"] * 50, rungs) == len(rungs) - 1


def _task_spec(**overrides: object) -> dict[str, object]:
    import copy
    import self_test

    raw = copy.deepcopy(self_test.sample_spec()["tasks"][0])
    raw.update(overrides)
    return raw


def test_five_tier_lattice_and_aliases() -> None:
    assert routingctl.TIER_ORDER == ["economy", "standard", "advanced", "strong", "max"]
    assert routingctl.ROUTE_TIERS == ["tool", *routingctl.TIER_ORDER]
    for rank, tier in enumerate(routingctl.TIER_ORDER, start=1):
        assert routingctl.normalize_tier(f"F{rank}") == tier
        assert routingctl.normalize_tier(f"l{rank}") == tier
    assert routingctl.normalize_tier(" Advanced ") == "advanced"
    assert routingctl.normalize_tier("F6") == "f6"
    # Aliases are accepted on input and persisted canonically.
    for alias, canonical in (("F3", "advanced"), ("L3", "advanced"), ("F1", "economy"), ("L5", "max"), ("strong", "strong")):
        task = planctl.normalize_task(_task_spec(model_tier=alias), 0, {"R001", "R002"})
        assert task["model_tier"] == canonical, (alias, task["model_tier"])
    design = planctl.normalize_task(
        _task_spec(complexity="high", design_route={"model_tier": "L4", "reasoning_effort": "high"}), 0, {"R001", "R002"}
    )
    assert design["design_route"]["model_tier"] == "strong", design["design_route"]
    try:
        planctl.normalize_task(_task_spec(model_tier="F6"), 0, {"R001", "R002"})
    except planctl.PlanError:
        pass
    else:
        raise AssertionError("F6 is not a tier alias")
    assert "advanced" in planctl.VALID_TIERS
    # Claude and Codex ladders carry no advanced rung unless configured.
    for provider in ("claude", "codex"):
        assert all(tier != "advanced" for tier, _ in routingctl.ESCALATION_LADDERS[provider])
        assert "advanced" not in routingctl.configure_config({})[provider]["models"]


def test_empty_tiers_are_skipped_upward() -> None:
    configured = routingctl.configure_config({})
    for provider in ("claude", "codex"):
        cfg = configured[provider]
        # Floor lookup: an advanced floor without a candidate lifts to strong.
        rungs = routingctl.route_rungs(cfg, "advanced", "medium")
        assert rungs[0] == ("strong", "medium"), (provider, rungs)
        assert all(tier != "advanced" for tier, _ in rungs)
        rungs = routingctl.route_rungs(cfg, "F3", "medium")
        assert rungs[0] == ("strong", "medium"), (provider, rungs)
        # Escalation from standard skips the empty advanced rung to strong.
        rungs = routingctl.route_rungs(cfg, "standard", "medium")
        step = routingctl.escalation_step(["semantic"], rungs)
        assert rungs[step][0] == "strong", (provider, rungs)
    # A configured advanced candidate becomes a rung between standard and strong.
    custom = {
        "models": {"economy": "e", "standard": "s", "advanced": "a", "strong": "x", "max": "m"},
        "escalation_ladder": [["standard", "medium"], ["F3", "medium"], ["strong", "medium"]],
    }
    rungs = routingctl.route_rungs(custom, "standard", "medium")
    assert rungs == [("standard", "medium"), ("advanced", "medium"), ("strong", "medium")], rungs
    assert routingctl.route_rungs(custom, "advanced", "medium")[0] == ("advanced", "medium")
    # Removing the advanced model skips it without downgrading below the floor.
    custom["models"].pop("advanced")
    rungs = routingctl.route_rungs(custom, "standard", "medium")
    assert rungs == [("standard", "medium"), ("strong", "medium")], rungs
    rungs = routingctl.route_rungs(custom, "advanced", "high")
    assert rungs[0] == ("strong", "high"), rungs


def test_legacy_schema_fixtures_route_unchanged() -> None:
    # Pre-advanced (schema 1-4) expectations for the built-in ladders.
    configured = routingctl.configure_config({})
    legacy = {
        ("claude", "economy", "low"): [("economy", "low"), ("standard", "medium"), ("standard", "high"),
                                       ("strong", "medium"), ("strong", "high"), ("max", "high"), ("max", "xhigh")],
        ("claude", "standard", "medium"): [("standard", "medium"), ("standard", "high"), ("strong", "medium"),
                                           ("strong", "high"), ("max", "high"), ("max", "xhigh")],
        ("codex", "standard", "medium"): [("standard", "medium"), ("strong", "low"), ("strong", "medium"),
                                          ("strong", "high"), ("max", "xhigh")],
        ("codex", "strong", "high"): [("strong", "high"), ("max", "xhigh")],
    }
    for (provider, tier, effort), expected in legacy.items():
        assert routingctl.route_rungs(configured[provider], tier, effort) == expected, (provider, tier, effort)
    # Provider configs without a model map (old fixtures) keep every ladder rung.
    assert routingctl.route_rungs({}, "standard", "medium") == [
        ("standard", "medium"), ("standard", "high"), ("strong", "medium"),
        ("strong", "high"), ("max", "high"), ("max", "xhigh"),
    ]
    assert routingctl.minimum_route(["bounded_implementation", "weak_validation"]) == {"tier": "strong", "effort": "high"}
    assert routingctl.minimum_route(["exploration", "weak_validation"]) == {"tier": "standard", "effort": "high"}
    for schema in (1, 2, 3, 4):
        for tier in ("economy", "standard", "strong", "max"):
            assert routingctl.normalize_tier(tier) == tier and tier in planctl.VALID_TIERS, (schema, tier)


def test_tier_eval_corpus() -> None:
    payload = json.loads((REFERENCES / "tier-evals.json").read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    cases = payload["cases"]
    ids = [case["id"] for case in cases]
    assert len(ids) == len(set(ids)), "tier eval ids must be unique"
    assert set(payload["signals"]["primary"]) == set(routingctl.PRIMARY_SIGNALS)
    assert set(payload["signals"]["modifiers"]) == set(routingctl.MODIFIER_SIGNALS)
    per_tier: dict[str, int] = {}
    near_misses = 0
    for case in cases:
        actual = routingctl.minimum_route(case["signals"])
        assert actual == case["expected"], f"{case['id']}: expected {case['expected']}, got {actual}"
        per_tier[actual["tier"]] = per_tier.get(actual["tier"], 0) + 1
        near_misses += bool(case.get("near_miss"))
    assert per_tier.get("tool", 0) >= 2 and per_tier.get("economy", 0) >= 5
    assert per_tier.get("standard", 0) >= 3 and per_tier.get("strong", 0) >= 6 and per_tier.get("max", 0) >= 2
    assert near_misses >= 8, "corpus needs near-miss leaves (small-but-risky and large-but-cheap)"
    # The user-facing guarantee: a small edit with weak validation and costly silent
    # failure is routed strong even when the root model is small.
    t009 = next(case for case in cases if case["id"] == "T009")
    assert t009["expected"]["tier"] == "strong"
    try:
        routingctl.minimum_route(["not_a_signal"])
    except routingctl.RoutingError:
        pass
    else:
        raise AssertionError("unknown signals must be rejected")


def test_no_user_routing_ceiling_contract() -> None:
    paths = [
        SKILL_DIR / "SKILL.md",
        SKILL_DIR / "agents" / "openai.yaml",
        REFERENCES / "MODEL_ROUTING.md",
        REFERENCES / "TOKEN_EFFICIENCY.md",
    ]
    joined = "\n".join(path.read_text(encoding="utf-8") for path in paths).lower()
    for forbidden in ("hard ceiling", "--max-tier", "--max-effort", "provider_ceiling_models"):
        assert forbidden not in joined, forbidden


def test_provider_guidance_is_split_and_lazy() -> None:
    generic = (REFERENCES / "MODEL_ROUTING.md").read_text(encoding="utf-8")
    codex = (REFERENCES / "MODEL_ROUTING_CODEX.md").read_text(encoding="utf-8")
    claude = (REFERENCES / "MODEL_ROUTING_CLAUDE.md").read_text(encoding="utf-8")
    assert "exactly one" in generic
    assert "gpt-6-astra" in codex
    assert "Astra Low" in codex and "Astra Medium" in codex
    assert "Explore/Haiku" in claude
    assert "Opus High" in claude


def test_elevation_mechanics_are_documented() -> None:
    generic = (REFERENCES / "MODEL_ROUTING.md").read_text(encoding="utf-8")
    codex = (REFERENCES / "MODEL_ROUTING_CODEX.md").read_text(encoding="utf-8")
    claude = (REFERENCES / "MODEL_ROUTING_CLAUDE.md").read_text(encoding="utf-8")
    skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    # Root model is never switched; hard leaves are delegated.
    assert "Never switch the root session" in generic
    assert "failure_class" in generic
    for needle in ("mechanical", "semantic", "environmental", "budget", "plan_defect"):
        assert needle in generic, needle
    # Claude: Explore inherits the session model; Haiku takes no effort flag.
    assert "inherits the main conversation" in claude
    assert 'model: "haiku"' in claude
    assert "opusplan" in claude and "CLAUDE_CODE_SUBAGENT_MODEL" in claude
    assert "no effort" in claude.lower()
    assert "isolation: worktree" in claude
    assert "subagentPromptCacheTtl" in claude
    # Codex: explicit spawn model/effort, plan-mode effort, subagent defaults.
    assert "spawn_agent" in codex and "plan_mode_reasoning_effort" in codex
    assert "agents.default_subagent_model" in codex
    assert "explorer" in codex and "worker" in codex
    # Entry point carries the leaf-signal table for small root models.
    for needle in ("silent_failure_costly", "weak_validation", "routingctl.py route", "delegate"):
        assert needle in skill, needle


def test_direct_mode_keeps_adaptive_routing() -> None:
    skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert "DIRECT exits the harness, not adaptive model routing" in skill
    assert "small task with no tests can deserve a stronger model" in skill
    assert "Do not preload other" in skill


def main() -> int:
    test_current_model_map()
    test_legacy_ceiling_state_is_replaced()
    test_catalog_installer_is_idempotent()
    test_escalation_ladders_follow_calibration()
    test_five_tier_lattice_and_aliases()
    test_empty_tiers_are_skipped_upward()
    test_legacy_schema_fixtures_route_unchanged()
    test_tier_eval_corpus()
    test_no_user_routing_ceiling_contract()
    test_provider_guidance_is_split_and_lazy()
    test_elevation_mechanics_are_documented()
    test_direct_mode_keeps_adaptive_routing()
    print("All adaptive model-routing self-tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
