#!/usr/bin/env python3
"""Self-tests for the DeepSeek profiles (claude + codex harnesses) and pricing. No host CLI or network is used."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import model_catalog  # noqa: E402
import planctl  # noqa: E402
import routing_config  # noqa: E402
import run_isolated  # noqa: E402
from routingctl import EFFORT_ORDER  # noqa: E402

CATALOG = model_catalog.bootstrap_catalog()
MODELS = CATALOG["providers"]["deepseek"]["models"]
FLASH, PRO = MODELS["deepseek-flash"], MODELS["deepseek-v4-pro"]
M = 1_000_000
# The codex harness writes its output schema beside the result path; one stable
# temp dir keeps it out of the cwd while argv comparisons stay deterministic.
RESULT_DIR = tempfile.TemporaryDirectory()
RESULT_PATH = Path(RESULT_DIR.name) / "unused.json"


def utc(hour: int, minute: int, second: int = 0) -> datetime:
    return datetime(2026, 10, 1, hour, minute, second, tzinfo=timezone.utc)


def argv(provider: str, config: dict) -> list[str]:
    model = "claude-sonnet-5-5" if provider == "claude" else "gpt-6.1-sol"
    route = {"provider": provider, "tier": "standard", "model": model, "effort": "medium"}
    return run_isolated.build_worker_command(provider, route, config, "PROMPT", RESULT_PATH)


def with_profile(harness: str) -> dict:
    config = planctl.default_config()
    config["profiles"] = {"deepseek": routing_config.deepseek_profile(harness)}
    config[harness]["profile"] = "deepseek"
    return config


def test_profiles_resolve_on_both_harnesses() -> None:
    for harness in ("claude", "codex"):
        profile = routing_config.deepseek_profile(harness)
        routing_config._profile("deepseek", profile, partial=False)
        resolved = routing_config.resolve_profile(harness, with_profile(harness))
        assert resolved["harness"] == harness and resolved["adapter"] == harness, resolved
        for key in ("base_url_env", "token_env"):
            assert routing_config.ENV_NAME.fullmatch(resolved[key]), resolved
        assert "sk-" not in json.dumps(profile)
        try:
            routing_config._profile("deepseek", {**profile, "token": "sk-secret"}, partial=False)
        except routing_config.ConfigError as exc:
            assert "sk-secret" not in str(exc)
        else:
            raise AssertionError("a literal credential key must be rejected")
    try:
        routing_config.deepseek_profile("native")
    except routing_config.ConfigError:
        pass
    else:
        raise AssertionError("deepseek has no native harness")


def test_profile_does_not_change_native_argv() -> None:
    for harness in ("claude", "codex"):
        baseline = argv(harness, planctl.default_config())
        defined_only = planctl.default_config()
        defined_only["profiles"] = {"deepseek": routing_config.deepseek_profile(harness)}
        assert argv(harness, defined_only) == baseline, "defining the profile must not alter native argv"
        # Using it composes the same harness adapter; the unrelated native harness stays byte-identical.
        used = with_profile(harness)
        other = "codex" if harness == "claude" else "claude"
        assert argv(other, used) == argv(other, planctl.default_config())
        assert argv(harness, used) == baseline, "profile reuses the harness adapter argv"


def test_credentials_reach_child_env_only() -> None:
    env = {"DEEPSEEK_ANTHROPIC_BASE_URL": "https://example.invalid/anthropic", "DEEPSEEK_API_KEY": "k-test"}
    child = run_isolated.spawn_env("claude", with_profile("claude"), env)
    assert child["ANTHROPIC_BASE_URL"] == env["DEEPSEEK_ANTHROPIC_BASE_URL"] and child["ANTHROPIC_AUTH_TOKEN"] == "k-test"
    assert run_isolated.spawn_env("claude", planctl.default_config(), {}) is None
    try:
        run_isolated.spawn_env("codex", with_profile("codex"), {})
    except run_isolated.RunnerError as exc:
        assert "DEEPSEEK_API_KEY" in str(exc) or "DEEPSEEK_OPENAI_BASE_URL" in str(exc)
    else:
        raise AssertionError("missing credentials must fail")


def test_effort_map_and_capability_difference() -> None:
    for model in MODELS:
        got = {e: model_catalog.native_effort("deepseek", model, e, CATALOG) for e in EFFORT_ORDER}
        assert got == {"low": "high", "medium": "high", "high": "high", "xhigh": "max", "max": "max"}, (model, got)
    assert "vision" in FLASH["capability"]["capabilities"]
    assert "vision" not in PRO["capability"]["capabilities"]
    for entry in MODELS.values():
        assert {"code", "reasoning", "tool_use", "long_context"} <= set(entry["capability"]["capabilities"])


def test_off_peak_window_boundaries() -> None:
    eco = FLASH["economics"]
    cases = [
        (utc(16, 29, 59), False), (utc(16, 30), True), (utc(23, 59), True),
        (utc(0, 0), True), (utc(0, 29, 59), True), (utc(0, 30), False), (utc(12, 0), False),
    ]
    for when, expected in cases:
        assert model_catalog.is_off_peak(eco, when) is expected, when
    # A non-UTC instant is converted before the window check.
    brt = timezone(timedelta(hours=-3))
    assert model_catalog.is_off_peak(eco, datetime(2026, 10, 1, 13, 30, tzinfo=brt)) is True
    assert model_catalog.is_off_peak(eco, datetime(2026, 10, 1, 13, 29, tzinfo=brt)) is False


def test_prices_on_both_sides_of_each_boundary() -> None:
    assert abs(model_catalog.api_cost_usd(FLASH["economics"], M, 0, 0, at=utc(16, 29, 59)) - 0.30) < 1e-9
    assert abs(model_catalog.api_cost_usd(FLASH["economics"], M, 0, 0, at=utc(16, 30)) - 0.15) < 1e-9
    assert abs(model_catalog.api_cost_usd(FLASH["economics"], 0, 0, M, at=utc(0, 29, 59)) - 0.60) < 1e-9
    assert abs(model_catalog.api_cost_usd(FLASH["economics"], 0, 0, M, at=utc(0, 30)) - 1.20) < 1e-9
    assert abs(model_catalog.api_cost_usd(PRO["economics"], M, 0, 0, at=utc(16, 29, 59)) - 1.32) < 1e-9
    assert abs(model_catalog.api_cost_usd(PRO["economics"], M, 0, 0, at=utc(16, 30)) - 0.66) < 1e-9
    # Without a timestamp the peak (list) rate applies.
    assert abs(model_catalog.api_cost_usd(PRO["economics"], M, 0, 0) - 1.32) < 1e-9


def test_cache_hit_vs_miss_matches_pricing_table() -> None:
    table = {  # model -> (miss, hit, out) as (off-peak, peak) per 1M tokens
        "deepseek-flash": ((0.15, 0.30), (0.003, 0.006), (0.60, 1.20)),
        "deepseek-v4-pro": ((0.66, 1.32), (0.022, 0.044), (1.98, 3.96)),
    }
    for model, (miss, hit, out) in table.items():
        eco = MODELS[model]["economics"]
        for index, when in ((0, utc(20, 0)), (1, utc(12, 0))):
            assert abs(model_catalog.api_cost_usd(eco, M, 0, 0, at=when) - miss[index]) < 1e-9, (model, "miss")
            assert abs(model_catalog.api_cost_usd(eco, 0, M, 0, at=when) - hit[index]) < 1e-9, (model, "hit")
            assert abs(model_catalog.api_cost_usd(eco, 0, 0, M, at=when) - out[index]) < 1e-9, (model, "out")
            assert model_catalog.api_cost_usd(eco, 0, M, 0, at=when) < model_catalog.api_cost_usd(eco, M, 0, 0, at=when)
    mixed = model_catalog.api_cost_usd(FLASH["economics"], 100_000, 900_000, 50_000, at=utc(12, 0))
    assert abs(mixed - (100_000 * 0.30 + 900_000 * 0.006 + 50_000 * 1.20) / M) < 1e-9


def test_catalog_validates_and_eligibility_by_capability() -> None:
    model_catalog.validate(CATALOG)
    mapping = model_catalog.provider_config_mapping("deepseek", CATALOG)
    assert mapping["models"] == {"economy": "deepseek-flash", "standard": "deepseek-flash", "advanced": "deepseek-v4-pro"}
    assert "strong" not in mapping["models"] and "max" not in mapping["models"]
    vision = [m for m, e in MODELS.items() if "vision" in e["capability"]["capabilities"]]
    assert vision == ["deepseek-flash"], vision
    assert model_catalog.provider_config_mapping("claude", CATALOG)["models"]["standard"] == "claude-sonnet-5-5"


def test_schema_rejects_bad_off_peak() -> None:
    for mutate in (
        lambda e: e["economics"]["off_peak"].pop("window_utc"),
        lambda e: e["economics"]["off_peak"]["window_utc"].update(start="25:00"),
        lambda e: e["economics"]["off_peak"]["window_utc"].update(end="16:30"),
        lambda e: e["economics"]["off_peak"].update(cached_input_per_mtok=-1),
        lambda e: e["economics"]["off_peak"].update(surprise=1),
        lambda e: e["capability"]["effort_map"].pop("max"),
    ):
        broken = copy.deepcopy(CATALOG)
        mutate(broken["providers"]["deepseek"]["models"]["deepseek-flash"])
        try:
            model_catalog.validate(broken)
        except model_catalog.CatalogError:
            continue
        raise AssertionError("invalid DeepSeek metadata accepted")


def test_thinking_is_optional() -> None:
    model_catalog.require_thinking("deepseek", "deepseek-flash", False, CATALOG)


def main() -> None:
    for name, test in sorted(globals().items()):
        if name.startswith("test_") and callable(test):
            test()
    print("deepseek provider self-tests passed")


if __name__ == "__main__":
    main()
