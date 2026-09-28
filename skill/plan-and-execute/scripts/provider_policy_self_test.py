#!/usr/bin/env python3
"""Focused regression tests for plan-scoped executor authorization."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import planctl
import provider_policy
import run_isolated


def expect_error(fn, text: str) -> None:
    try:
        fn()
    except provider_policy.PolicyError as exc:
        assert text in str(exc), (text, str(exc))
        return
    raise AssertionError(f"Expected PolicyError containing {text!r}")


def policy(*providers: str) -> dict:
    return provider_policy.normalize({"allowed_providers": list(providers)})


def test_normalization_and_conflicts() -> None:
    p = policy("codex", "claude")
    assert p["allowed_providers"] == ["claude", "codex"]
    assert p["manager_mode"] == "delegate_only"
    expect_error(lambda: provider_policy.normalize({"allowed_providers": []}), "non-empty")
    expect_error(lambda: provider_policy.normalize({"allowed_providers": ["unknown"]}), "exact executor IDs")
    expect_error(
        lambda: provider_policy.reconcile(policy("codex"), policy("claude")),
        "Conflicting execution policies",
    )


def test_provider_filter_and_fallback() -> None:
    p = policy("codex", "claude")
    assert provider_policy.candidates(p, "auto", ["gemini", "codex", "claude"], True) == ["codex", "claude"]
    assert provider_policy.candidates(p, "codex", ["claude", "codex"], False) == ["codex"]
    expect_error(lambda: provider_policy.candidates(p, "gemini", ["gemini", "codex"], True), "not authorized")


def test_routes_are_fail_closed() -> None:
    p = policy("codex", "claude")
    good = {
        provider_policy.FIELD: p,
        "tasks": [{
            "provider": "auto",
            "design_route": {"provider": "claude"},
            "current_route": {"provider": "codex"},
            "history": [{"route": {"provider": "claude"}}],
            "design_phase": {"route": {"provider": "claude"}},
        }],
        "planning_provenance": {"provider": "codex"},
    }
    provider_policy.validate_routes(good)
    bad = json.loads(json.dumps(good))
    bad["tasks"][0]["current_route"]["provider"] = "gemini"
    expect_error(lambda: provider_policy.validate_routes(bad), "not authorized")


def test_snapshot_pinning() -> None:
    p = policy("codex")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        plan = root / ".ai-work" / "p"
        plan.mkdir(parents=True)
        manifest = {
            "schema_version": provider_policy.PLAN_SCHEMA_VERSION,
            "plan_id": "p",
            "repo_root": str(root),
            "work_root": ".ai-work",
            provider_policy.FIELD: p,
            "tasks": [],
        }
        sentinel = {
            "schema_version": provider_policy.PLAN_SCHEMA_VERSION,
            "plan_id": "p",
            "repo_root": str(root),
        }
        provider_policy.seal(plan, manifest, sentinel)
        (plan / planctl.SENTINEL).write_text(json.dumps(sentinel), encoding="utf-8")
        provider_policy.verify_snapshot(plan, manifest)
        tampered = json.loads((plan / provider_policy.SNAPSHOT).read_text(encoding="utf-8"))
        tampered["allowed_providers"] = ["claude"]
        (plan / provider_policy.SNAPSHOT).write_text(json.dumps(tampered), encoding="utf-8")
        expect_error(lambda: provider_policy.verify_snapshot(plan, manifest), "differs from its pinned snapshot")


def test_config_cannot_widen_plan_policy() -> None:
    p = policy("codex")
    config = {provider_policy.FIELD: policy("claude")}
    expect_error(
        lambda: provider_policy.bind_config(config, {provider_policy.FIELD: p}),
        "Conflicting execution policies",
    )
    bound = provider_policy.bind_config({}, {provider_policy.FIELD: p})
    assert bound[provider_policy.FIELD] == p


def test_known_cli_masquerading_is_rejected() -> None:
    p = policy("codex")
    provider_policy.validate_adapter(p, "codex", ["codex"])
    expect_error(lambda: provider_policy.validate_adapter(p, "codex", ["claude"]), "invokes the claude CLI")


def test_runner_candidate_filter() -> None:
    p = policy("codex")
    config = planctl.default_config()
    config[provider_policy.FIELD] = p
    config["provider_order"] = ["claude", "codex"]
    task = {"provider": "auto", "allow_provider_fallback": True, "functional_failures": 0}
    original = run_isolated.executable_available
    try:
        run_isolated.executable_available = lambda prefix: True
        assert run_isolated.candidate_providers(task, config, None) == ["codex"]
    finally:
        run_isolated.executable_available = original


def main() -> int:
    test_normalization_and_conflicts()
    test_provider_filter_and_fallback()
    test_routes_are_fail_closed()
    test_snapshot_pinning()
    test_config_cannot_widen_plan_policy()
    test_known_cli_masquerading_is_rejected()
    test_runner_candidate_filter()
    print("provider-policy self-tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
