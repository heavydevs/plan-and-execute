#!/usr/bin/env python3
"""Regression tests for economical model mappings and hard routing ceilings."""
from __future__ import annotations

import routingctl
import planctl


def test_current_model_map() -> None:
    configured = routingctl.configure_config(planctl.default_config())
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


def test_strong_high_ceiling_collapses_expensive_routes() -> None:
    configured = routingctl.configure_config(
        planctl.default_config(), max_tier="strong", max_effort="high"
    )
    assert configured["codex"]["models"]["max"] == "gpt-5.6-sol"
    assert configured["claude"]["models"]["max"] == "opus"
    for provider in ("codex", "claude"):
        caps = configured[provider]["max_effort_by_tier"]
        assert all(routingctl.EFFORT_ORDER.index(value) <= routingctl.EFFORT_ORDER.index("high") for value in caps.values())
    assert configured["routing_policy"]["hard_ceiling"] is True
    assert configured["routing_policy"]["max_tier"] == "strong"
    assert configured["routing_policy"]["max_effort"] == "high"


def test_provider_override_still_caps_fallback_tier() -> None:
    configured = routingctl.configure_config(
        planctl.default_config(),
        max_tier="standard",
        max_effort="medium",
        codex_ceiling_model="custom-codex-standard",
        claude_ceiling_model="custom-claude-standard",
    )
    for tier in ("standard", "strong", "max"):
        assert configured["codex"]["models"][tier] == "custom-codex-standard"
        assert configured["claude"]["models"][tier] == "custom-claude-standard"
    assert configured["codex"]["models"]["economy"] == "gpt-5.6-luna"
    assert configured["claude"]["models"]["economy"] == "haiku"


def main() -> int:
    test_current_model_map()
    test_strong_high_ceiling_collapses_expensive_routes()
    test_provider_override_still_caps_fallback_tier()
    print("All economical routing ceiling self-tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
