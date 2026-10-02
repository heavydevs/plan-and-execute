#!/usr/bin/env python3
"""Self-tests for the GLM/Z.AI profile and Coding Plan economics. No host CLI or network is used."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import model_catalog  # noqa: E402
import routing_config  # noqa: E402
from routingctl import EFFORT_ORDER  # noqa: E402

CATALOG = model_catalog.bootstrap_catalog()
MODELS = CATALOG["providers"]["glm"]["models"]
PRO, FLASH = MODELS["glm-5.3"]["economics"], MODELS["glm-5.3-flash"]["economics"]


def test_profile_reuses_claude_harness_with_env_names_only() -> None:
    profile = routing_config.glm_profile()
    assert profile["harness"] == "claude"
    routing_config._profile("glm", profile, partial=False)
    config = {"claude": {"profile": "glm"}, "profiles": {"glm": profile}}
    resolved = routing_config.resolve_profile("claude", config)
    assert resolved["harness"] == "claude" and resolved["adapter"] == "claude", resolved
    for key in ("base_url_env", "token_env"):
        assert routing_config.ENV_NAME.fullmatch(resolved[key]), resolved
    assert "sk-" not in json.dumps(profile)
    try:
        routing_config._profile("glm", {**profile, "token": "sk-secret"}, partial=False)
    except routing_config.ConfigError as exc:
        assert "sk-secret" not in str(exc)
    else:
        raise AssertionError("a literal credential key must be rejected")


def test_default_profile_resolution_unchanged() -> None:
    assert routing_config.resolve_profile("claude", {"claude": {}})["base_url_env"] is None


def test_effort_map_covers_every_skill_effort() -> None:
    expected = {"low": "low", "medium": "high", "high": "high", "xhigh": "max", "max": "max"}
    for model in MODELS:
        got = {e: model_catalog.native_effort("glm", model, e, CATALOG) for e in EFFORT_ORDER}
        assert got == expected, (model, got)
        assert set(got.values()) <= {"low", "high", "max"}


def test_thinking_disabled_rejected() -> None:
    model_catalog.require_thinking("glm", "glm-5.3", True, CATALOG)
    for call in (lambda: model_catalog.require_thinking("glm", "glm-5.3", False, CATALOG),
                 lambda: routing_config.glm_profile(thinking=False)):
        try:
            call()
        except (model_catalog.CatalogError, routing_config.ConfigError):
            continue
        raise AssertionError("thinking-disabled GLM-5.3 must be rejected")


def test_credit_formula_matches_documented_multipliers() -> None:
    # Hand-computed from (in*mi + cached*mc + out*mo) / 10000 with the documented multipliers.
    assert model_catalog.credits(PRO, 1_000_000, 0, 0) == 690.0
    assert model_catalog.credits(PRO, 0, 1_000_000, 0) == 170.0
    assert model_catalog.credits(PRO, 0, 0, 1_000_000) == 2400.0
    assert model_catalog.credits(FLASH, 1_000_000, 0, 0) == 230.0
    assert model_catalog.credits(FLASH, 0, 1_000_000, 0) == 56.0
    assert model_catalog.credits(FLASH, 0, 0, 1_000_000) == 800.0
    mixed = model_catalog.credits(PRO, 100_000, 400_000, 50_000)
    assert abs(mixed - (100_000 * 6.9 + 400_000 * 1.7 + 50_000 * 24) / 10000) < 1e-9
    assert abs(mixed - 257.0) < 1e-9, mixed


def test_off_peak_halves_credits_and_cache_is_cheaper() -> None:
    peak = model_catalog.credits(PRO, 100_000, 400_000, 50_000)
    assert model_catalog.credits(PRO, 100_000, 400_000, 50_000, off_peak=True) == peak / 2
    assert model_catalog.credits(PRO, 0, 500_000, 0) < model_catalog.credits(PRO, 500_000, 0, 0)


def test_api_pricing_and_invalid_tokens() -> None:
    assert abs(model_catalog.api_cost_usd(PRO, 1_000_000, 1_000_000, 1_000_000) - (1.40 + 0.26 + 4.40)) < 1e-9
    assert abs(model_catalog.api_cost_usd(FLASH, 1_000_000, 1_000_000, 1_000_000) - (0.15 + 0.03 + 0.50)) < 1e-9
    for bad in (-1, 1.5, True):
        try:
            model_catalog.credits(PRO, bad, 0, 0)
        except model_catalog.CatalogError:
            continue
        raise AssertionError(f"{bad!r} tokens must be rejected")


def test_catalog_validates_and_tiers_fall_upward() -> None:
    model_catalog.validate(CATALOG)
    mapping = model_catalog.provider_config_mapping("glm", CATALOG)
    assert mapping["models"] == {"economy": "glm-5.3-flash", "standard": "glm-5.3-flash", "advanced": "glm-5.3"}
    assert "strong" not in mapping["models"] and "max" not in mapping["models"], "GLM never fills strong by name"
    assert model_catalog.provider_config_mapping("claude", CATALOG)["models"]["standard"] == "claude-sonnet-5-5"


def test_schema_rejects_bad_glm_metadata() -> None:
    for mutate in (
        lambda c: c["capability"]["effort_map"].pop("max"),
        lambda c: c["capability"].update(thinking="never"),
        lambda c: c["economics"]["plan_credits"].update(divisor=0),
        lambda c: c["economics"]["plan_credits"].update(off_peak_factor=2),
        lambda c: c["economics"].update(cached_input_per_mtok=-1),
    ):
        broken = copy.deepcopy(CATALOG)
        mutate(broken["providers"]["glm"]["models"]["glm-5.3"])
        try:
            model_catalog.validate(broken)
        except model_catalog.CatalogError:
            continue
        raise AssertionError("invalid GLM metadata accepted")


def main() -> None:
    for name, test in sorted(globals().items()):
        if name.startswith("test_") and callable(test):
            test()
    print("glm provider self-tests passed")


if __name__ == "__main__":
    main()
