#!/usr/bin/env python3
"""Regression tests for adaptive provider routing and lazy provider guidance."""
from __future__ import annotations

from pathlib import Path

import planctl
import routingctl

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent


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
    }


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


def test_provider_guidance_is_split_and_lazy() -> None:
    generic = (SKILL_DIR / "references" / "MODEL_ROUTING.md").read_text(encoding="utf-8")
    codex = (SKILL_DIR / "references" / "MODEL_ROUTING_CODEX.md").read_text(encoding="utf-8")
    claude = (SKILL_DIR / "references" / "MODEL_ROUTING_CLAUDE.md").read_text(encoding="utf-8")
    assert "exactly one" in generic
    assert "gpt-6-astra" in codex
    assert "Astra Low" in codex and "Astra Medium" in codex
    assert "Explore/Haiku" in claude
    assert "Opus High" in claude


def test_direct_mode_keeps_adaptive_routing() -> None:
    skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert "DIRECT exits the harness, not adaptive model routing" in skill
    assert "small task with no tests can deserve a stronger model" in skill
    assert "Do not preload both" in skill


def main() -> int:
    test_current_model_map()
    test_legacy_ceiling_state_is_replaced()
    test_catalog_installer_is_idempotent()
    test_no_user_routing_ceiling_contract()
    test_provider_guidance_is_split_and_lazy()
    test_direct_mode_keeps_adaptive_routing()
    print("All adaptive model-routing self-tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
