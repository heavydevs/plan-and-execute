#!/usr/bin/env python3
"""Regression tests for portable F/L routing and dynamic provider model matrices."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import planctl
import routingctl
import modelmapctl

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent


def sample_matrix() -> dict:
    return {
        "researched_at": "2026-09-10T16:30:00-03:00",
        "research_mode": "live",
        "sources": [
            {"label": "Provider catalog", "url": "https://example.test/models"},
            {"label": "Coding benchmark", "url": "https://example.test/benchmark"},
        ],
        "providers": {
            "codex": {
                "families": {
                    "F1": "codex-cheap",
                    "F2": "codex-standard",
                    "F3": "codex-strong",
                    "F4": "codex-frontier",
                },
                "levels": {
                    "L1": "low",
                    "L2": "medium",
                    "L3": "high",
                    "L4": "xhigh",
                    "L5": "max",
                },
                "benchmark": "Current agent benchmark favors the frontier route for hard work.",
                "pricing": "Current coding-plan economics recorded at planning time.",
            },
            "muse": {
                "families": {
                    "F1": "muse-spark-current",
                    "F2": "muse-spark-current",
                    "F3": "muse-spark-current",
                    "F4": "muse-spark-current",
                },
                "levels": {
                    "L1": "low",
                    "L2": "medium",
                    "L3": "high",
                    "L4": "xhigh",
                    "L5": "xhigh",
                },
                "benchmark": "Current coding-agent evidence makes Muse a viable portable route.",
                "pricing": "Subscription/API economics recorded at planning time.",
            },
        },
    }


def test_portable_vocabulary_and_fallback_catalog() -> None:
    module = routingctl.install_current_model_catalog(planctl)
    assert {"f1", "f2", "f3", "f4"} <= module.VALID_TIERS
    assert {"l1", "l2", "l3", "l4", "l5"} <= module.VALID_EFFORTS
    assert "muse" in module.VALID_PROVIDERS

    configured = module.default_config()
    assert configured["codex"]["models"] == {
        "economy": "gpt-5.6-luna",
        "standard": "gpt-5.6-terra",
        "strong": "gpt-5.6-sol",
        "max": "gpt-6-astra",
    }
    assert configured["claude"]["models"] == {
        "economy": "haiku",
        "standard": "sonnet",
        "strong": "opus",
        "max": "claude-fable-5-1",
    }
    assert configured["muse"]["models"]["max"] == "muse-spark-1.3"
    assert configured["routing_policy"]["selection"] == "adaptive-portable"
    assert configured["routing_policy"]["portable_model_families"] == "F1-F4"
    assert configured["routing_policy"]["portable_reasoning_levels"] == "L1-L5"


def test_legacy_ceiling_state_is_replaced() -> None:
    legacy = planctl.default_config()
    legacy["codex"]["models"]["strong"] = "retired-model"
    legacy["codex"]["models"]["max"] = "retired-model"
    legacy["routing_policy"] = {
        "hard_ceiling": True,
        "max_tier": "strong",
        "max_effort": "high",
    }
    configured = routingctl.configure_config(legacy)
    assert configured["codex"]["models"]["strong"] == "gpt-5.6-sol"
    assert configured["codex"]["models"]["max"] == "gpt-6-astra"
    assert "hard_ceiling" not in configured["routing_policy"]
    assert "max_tier" not in configured["routing_policy"]
    assert "max_effort" not in configured["routing_policy"]


def test_matrix_validation_and_overlay() -> None:
    matrix = routingctl.validate_model_matrix(sample_matrix())
    assert matrix["providers"]["codex"]["families"]["f4"] == "codex-frontier"
    assert matrix["providers"]["muse"]["levels"]["l5"] == "xhigh"

    configured = routingctl.configure_config(planctl.default_config())
    overlaid = routingctl.apply_model_matrix(configured, matrix)
    assert overlaid["codex"]["models"]["economy"] == "codex-cheap"
    assert overlaid["codex"]["models"]["max"] == "codex-frontier"
    assert overlaid["muse"]["models"]["strong"] == "muse-spark-current"
    assert overlaid["muse"]["portable_levels"]["l5"] == "xhigh"
    assert overlaid["routing_policy"]["model_matrix_researched_at"] == matrix["researched_at"]


def test_live_matrix_requires_evidence() -> None:
    matrix = sample_matrix()
    matrix["sources"] = []
    try:
        routingctl.validate_model_matrix(matrix)
    except routingctl.RoutingError as exc:
        assert "at least one source" in str(exc)
    else:
        raise AssertionError("Expected a live matrix without sources to be rejected")


def test_modelmap_controller_persists_machine_and_human_files() -> None:
    with tempfile.TemporaryDirectory() as temp:
        plan_dir = Path(temp) / "plan"
        plan_dir.mkdir()
        (plan_dir / "orchestrator.config.json").write_text(
            json.dumps({"version": 1, "provider_order": ["codex"]}), encoding="utf-8"
        )
        (plan_dir / "PLAN.md").write_text("# Sample plan\n", encoding="utf-8")
        spec_path = Path(temp) / "matrix.json"
        spec_path.write_text(json.dumps(sample_matrix()), encoding="utf-8")

        written = modelmapctl.write_matrix(plan_dir, spec_path)
        validated = modelmapctl.validate_plan_matrix(plan_dir)
        assert validated == written
        assert (plan_dir / routingctl.MODEL_MATRIX_JSON).is_file()
        human = (plan_dir / routingctl.MODEL_MATRIX_MD).read_text(encoding="utf-8")
        assert "| Provider | F1 | F2 | F3 | F4 | L1 | L2 | L3 | L4 | L5 |" in human
        assert "codex-frontier" in human and "muse-spark-current" in human
        plan_text = (plan_dir / "PLAN.md").read_text(encoding="utf-8")
        assert "Portable model routing" in plan_text
        assert routingctl.MODEL_MATRIX_MD in plan_text


def test_catalog_installer_is_idempotent() -> None:
    module = routingctl.install_current_model_catalog(planctl)
    first = module.default_config()
    module = routingctl.install_current_model_catalog(module)
    second = module.default_config()
    assert first == second


def test_no_user_routing_ceiling_contract() -> None:
    paths = [
        SKILL_DIR / "SKILL.md",
        SKILL_DIR / "agents" / "openai.yaml",
        SKILL_DIR / "references" / "MODEL_ROUTING.md",
        SKILL_DIR / "references" / "TOKEN_EFFICIENCY.md",
    ]
    joined = "\n".join(path.read_text(encoding="utf-8") for path in paths).lower()
    for forbidden in ("hard ceiling", "--max-tier", "--max-effort", "provider_ceiling_models"):
        assert forbidden not in joined, forbidden


def test_provider_neutral_docs_cover_current_ecosystems() -> None:
    generic = (SKILL_DIR / "references" / "MODEL_ROUTING.md").read_text(encoding="utf-8")
    matrix = (SKILL_DIR / "references" / "MODEL_MATRIX.md").read_text(encoding="utf-8")
    skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    joined = "\n".join((generic, matrix, skill)).lower()
    assert "f1" in joined and "f4" in joined and "l1" in joined and "l5" in joined
    for provider in ("claude", "codex", "gemini", "qwen", "muse"):
        assert provider in joined, provider
    assert "provider-neutral" in joined
    assert "model_matrix.json" in joined
    assert "planning time" in joined


def test_direct_mode_keeps_adaptive_routing() -> None:
    skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert "DIRECT exits the harness, not adaptive model routing" in skill
    assert "small task with no tests can deserve a stronger model" in skill


def main() -> int:
    test_portable_vocabulary_and_fallback_catalog()
    test_legacy_ceiling_state_is_replaced()
    test_matrix_validation_and_overlay()
    test_live_matrix_requires_evidence()
    test_modelmap_controller_persists_machine_and_human_files()
    test_catalog_installer_is_idempotent()
    test_no_user_routing_ceiling_contract()
    test_provider_neutral_docs_cover_current_ecosystems()
    test_direct_mode_keeps_adaptive_routing()
    print("All portable model-routing self-tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
