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
        "economy": "gpt-5.6-luna",
        "standard": "gpt-5.6-terra",
        "strong": "gpt-6-astra",
        "max": "gpt-6-astra",
    }
    assert configured["claude"]["models"] == {
        "economy": "haiku",
        "standard": "sonnet",
        "strong": "opus",
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
    assert routingctl.model_supports_effort(configured["codex"], "gpt-5.6-luna") is True


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
    # Codex never spends a Terra High retry before an Astra Low attempt.
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
    assert "Do not preload both" in skill


def main() -> int:
    test_current_model_map()
    test_legacy_ceiling_state_is_replaced()
    test_catalog_installer_is_idempotent()
    test_escalation_ladders_follow_calibration()
    test_tier_eval_corpus()
    test_no_user_routing_ceiling_contract()
    test_provider_guidance_is_split_and_lazy()
    test_elevation_mechanics_are_documented()
    test_direct_mode_keeps_adaptive_routing()
    print("All adaptive model-routing self-tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
