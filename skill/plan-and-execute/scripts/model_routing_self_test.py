#!/usr/bin/env python3
"""Regression tests for portable F/L model routing and live compatibility artifacts."""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from artifact_contract import install_plan_contract
import planctl
import routingctl
import run_isolated

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent


def compatibility() -> dict:
    native_levels = {
        "L1": "low",
        "L2": "medium",
        "L3": "high",
        "L4": "xhigh",
        "L5": "max",
    }
    providers = {}
    for provider in routingctl.PORTABLE_PROVIDERS:
        providers[provider] = {
            "checked_at": "2026-09-09T23:00:00-03:00",
            "sources": [f"{provider} --help", f"official {provider} model documentation"],
            "families": {
                family: {
                    "model": f"{provider}-{family.lower()}-current",
                    "levels": dict(native_levels),
                }
                for family in routingctl.FAMILY_ORDER
            },
        }
    return {
        "generated_at": "2026-09-09T23:00:00-03:00",
        "discovery": "Live CLI help and current vendor documentation checked for the self-test.",
        "providers": providers,
    }


def portable_spec() -> dict:
    return {
        "title": "Portable routing sample",
        "summary": "Create one bounded marker with a provider-neutral execution requirement.",
        "language": "English",
        "request_analysis": {
            "request_parts": [{"id": "P001", "text": "Create a portable marker"}],
            "repository_findings": ["The repository is empty and suitable for one marker-file test."],
            "research_decision": "Only live provider-model discovery is required for routing compatibility.",
            "research_findings": [],
            "assumptions": ["The test environment provides POSIX shell commands."],
            "risks": ["A concrete provider binding in the TODO would make later switching expensive."],
            "open_questions": [],
            "decomposition_strategy": "Use one TODO because file creation and its existence check share one validation boundary.",
        },
        "requirements": [
            {
                "id": "R001",
                "text": "Create implemented.txt without pinning the task to one AI provider",
                "source": "user",
                "priority": "must",
                "request_part_ids": ["P001"],
            }
        ],
        "global_constraints": ["Do not edit unrelated files"],
        "execution_context": {
            "global": {
                "decision": "omit",
                "rationale": "The single TODO already contains every non-obvious execution constraint, so shared context would duplicate task-local information.",
                "items": [],
            },
            "scoped": [],
        },
        "plan_review": {
            "status": "approved",
            "reviewer": "portable routing self-test reviewer",
            "rounds": 1,
            "coverage_complete": True,
            "tasks_atomic": True,
            "dependencies_valid": True,
            "validations_sufficient": True,
            "contexts_minimal": True,
            "context_boundaries_sound": True,
            "unresolved_findings": [],
            "notes": ["The one requirement maps to one independently validated portable task."],
        },
        "model_compatibility": compatibility(),
        "tasks": [
            {
                "id": 1,
                "title": "Create portable marker",
                "objective": "Create implemented.txt in the repository root.",
                "requirement_ids": ["R001"],
                "complexity": "low",
                "atomicity_rationale": "File creation and the direct existence check form one cohesive outcome.",
                "context_boundary": {
                    "shared_context": ["The marker creation and validation use the same repository-root path."],
                    "why_one_todo": "One worker can create and validate the single marker without a cross-task handoff or unrelated context.",
                    "separate_from": ["Provider/model selection is resolved outside the TODO through the compatibility table."],
                },
                "scope": {
                    "in": ["Create implemented.txt"],
                    "out": ["No unrelated refactoring"],
                    "expected_files": ["implemented.txt"],
                },
                "acceptance_criteria": ["implemented.txt exists"],
                "validation_commands": ["test -f implemented.txt"],
                "subtasks": [
                    {
                        "id": "S001",
                        "title": "Create the marker",
                        "objective": "implemented.txt exists without unrelated changes.",
                    }
                ],
                "learning_targets": [],
                "model_family": "F2",
                "model_level": "L2",
            }
        ],
    }


def test_scale_and_compatibility_contract() -> None:
    assert routingctl.FAMILY_ORDER == ("F1", "F2", "F3", "F4")
    assert routingctl.LEVEL_ORDER == ("L1", "L2", "L3", "L4", "L5")
    normalized = routingctl.normalize_compatibility(compatibility())
    assert set(normalized["providers"]) == set(routingctl.PORTABLE_PROVIDERS)
    assert normalized["providers"]["gemini"]["families"]["F2"]["model"] == "gemini-f2-current"
    assert normalized["providers"]["qwen"]["families"]["F3"]["levels"]["L4"] == "xhigh"
    assert normalized["providers"]["muse"]["families"]["F4"]["levels"]["L5"] == "max"
    markdown = routingctl.render_compatibility_markdown(normalized)
    assert "MODEL" not in markdown  # no placeholder/template row should leak into rendered output
    assert "`F4`" in markdown and "`max`" in markdown
    assert "muse-f4-current" in markdown


def test_missing_portable_provider_is_rejected() -> None:
    raw = compatibility()
    raw["providers"].pop("muse")
    try:
        routingctl.normalize_compatibility(raw)
    except routingctl.RoutingError as exc:
        assert "muse" in str(exc)
    else:
        raise AssertionError("Portable compatibility must cover Muse as well as other providers")


def test_config_adds_muse_without_overwriting_current_models() -> None:
    raw = planctl.default_config()
    raw["codex"]["models"]["standard"] = "locally-current-model"
    configured = routingctl.configure_config(raw)
    assert configured["codex"]["models"]["standard"] == "locally-current-model"
    assert configured["muse"]["command"] == "muse"
    assert {"gemini", "qwen", "muse"} <= set(configured["provider_order"])
    assert configured["routing_policy"] == {
        "schema": routingctl.PORTABLE_ROUTING_VERSION,
        "selection": "portable-family-level",
        "concrete_binding": routingctl.MODEL_COMPATIBILITY_JSON,
    }


def test_portable_plan_artifacts_and_provider_switching() -> None:
    portable_planctl = routingctl.install_current_model_catalog(install_plan_contract())
    routingctl.install_runtime_model_catalog(run_isolated)
    with tempfile.TemporaryDirectory() as temp:
        repo = Path(temp) / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        plan_dir = portable_planctl.create_plan(
            repo, portable_spec(), ".ai-work", "portable-routing-test"
        )
        _loaded, manifest = portable_planctl.load_plan(plan_dir)
        assert not portable_planctl.validate_plan(plan_dir, manifest)
        task = manifest["tasks"][0]
        assert task["model_family"] == "F2"
        assert task["model_level"] == "L2"
        for forbidden in ("provider", "model_tier", "reasoning_effort"):
            assert forbidden not in task
        assert (plan_dir / routingctl.MODEL_COMPATIBILITY_JSON).is_file()
        assert (plan_dir / routingctl.MODEL_COMPATIBILITY_MD).is_file()
        task_text = (plan_dir / task["file"]).read_text(encoding="utf-8")
        assert 'model_family: "F2"' in task_text
        assert 'model_level: "L2"' in task_text
        assert routingctl.MODEL_COMPATIBILITY_MD in task_text
        assert routingctl.MODEL_COMPATIBILITY_MD in (plan_dir / "PLAN.md").read_text(encoding="utf-8")

        config = run_isolated.load_config(plan_dir)
        for provider in routingctl.PORTABLE_PROVIDERS:
            config[provider]["command"] = sys.executable
        codex_route = run_isolated.choose_route(task, config, "codex")
        qwen_route = run_isolated.choose_route(task, config, "qwen")
        muse_route = run_isolated.choose_route(task, config, "muse")
        assert codex_route["family"] == qwen_route["family"] == muse_route["family"] == "F2"
        assert codex_route["level"] == qwen_route["level"] == muse_route["level"] == "L2"
        assert codex_route["model"] == "codex-f2-current"
        assert qwen_route["model"] == "qwen-f2-current"
        assert muse_route["model"] == "muse-f2-current"


def test_portable_task_rejects_legacy_route_fields() -> None:
    portable_planctl = routingctl.install_current_model_catalog(install_plan_contract())
    spec = portable_spec()
    spec["tasks"][0]["provider"] = "codex"
    with tempfile.TemporaryDirectory() as temp:
        try:
            portable_planctl.create_plan(Path(temp), spec, ".ai-work", "mixed-routing")
        except portable_planctl.PlanError as exc:
            assert "must not pin legacy routing fields" in str(exc)
        else:
            raise AssertionError("F/L TODOs must reject concrete legacy routing fields")


def test_docs_are_dynamic_and_cover_all_requested_providers() -> None:
    core = "\n".join(
        (SKILL_DIR / relative).read_text(encoding="utf-8")
        for relative in (
            "SKILL.md",
            "references/MODEL_ROUTING.md",
            "references/PORTABLE_MODEL_ROUTING.md",
            "references/ORCHESTRATION.md",
            "references/PLAN_SPEC.md",
        )
    )
    assert "model_family" in core and "model_level" in core
    assert "MODEL_COMPATIBILITY.json" in core and "MODEL_COMPATIBILITY.md" in core
    for provider_file in (
        "MODEL_ROUTING_CODEX.md",
        "MODEL_ROUTING_CLAUDE.md",
        "MODEL_ROUTING_GEMINI.md",
        "MODEL_ROUTING_QWEN.md",
        "MODEL_ROUTING_MUSE.md",
    ):
        assert (SKILL_DIR / "references" / provider_file).is_file(), provider_file
    for stale in ("gpt-5.6-luna", "gpt-5.6-terra", "gpt-6-astra", "claude-fable-5-1"):
        assert stale not in core.lower(), stale


def main() -> int:
    test_scale_and_compatibility_contract()
    test_missing_portable_provider_is_rejected()
    test_config_adds_muse_without_overwriting_current_models()
    test_portable_plan_artifacts_and_provider_switching()
    test_portable_task_rejects_legacy_route_fields()
    test_docs_are_dynamic_and_cover_all_requested_providers()
    print("All portable F/L model-routing self-tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
