#!/usr/bin/env python3
"""Self-tests for the native Muse Code headless provider. No host CLI or network is used."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import model_catalog  # noqa: E402
import planctl  # noqa: E402
import routing_config  # noqa: E402
import run_isolated  # noqa: E402

MODEL = "muse-spark-1.3"
ROUTE = {"provider": "muse", "tier": "advanced", "model": MODEL, "effort": "medium"}


def sample_report() -> dict:
    return {
        "status": "completed",
        "summary": "Completed the Muse envelope test task.",
        "changed_files": ["sample.txt"],
        "validations": [],
        "risks": [],
        "follow_ups": [],
        "context_files_read": [],
        "learning_files_read": [],
        "completed_subtask_ids": ["S001"],
        "reusable_learnings": [],
        "related_task_reads": [],
        "blocked_reason": None,
    }


def worker(config: dict, route: dict | None = None) -> list[str]:
    return run_isolated.build_worker_command("muse", route or ROUTE, config, "PROMPT", Path("unused.json"))


def summary(config: dict, route: dict | None = None) -> list[str]:
    return run_isolated.build_summary_command("muse", route or ROUTE, config, "PROMPT", Path("unused.md"))


def test_default_worker_argv_has_no_permission_flags() -> None:
    config = planctl.default_config()
    assert config["muse"]["trust_workspace"] is False
    assert config["muse"]["disable_approval"] is False
    argv = worker(config)
    assert argv == ["muse", "exec", "--json", "--model", MODEL, "--reasoning-effort", "medium", "PROMPT"], argv
    assert "--trust-workspace" not in argv and "--disable-approval" not in argv


def test_opt_in_keys_add_flags_independently() -> None:
    config = planctl.default_config()
    config["muse"].update(trust_workspace=True, disable_approval=True)
    assert worker(config) == [
        "muse", "exec", "--json", "--trust-workspace", "--disable-approval",
        "--model", MODEL, "--reasoning-effort", "medium", "PROMPT",
    ]
    config["muse"].update(trust_workspace=True, disable_approval=False)
    assert worker(config) == [
        "muse", "exec", "--json", "--trust-workspace", "--model", MODEL, "--reasoning-effort", "medium", "PROMPT",
    ]
    config["muse"].update(trust_workspace=False, disable_approval=True)
    assert worker(config) == [
        "muse", "exec", "--json", "--disable-approval", "--model", MODEL, "--reasoning-effort", "medium", "PROMPT",
    ]


def test_opt_in_keys_must_be_booleans() -> None:
    for key in ("trust_workspace", "disable_approval"):
        for bad in ("false", "true", 1, None):
            config = copy.deepcopy(planctl.default_config())
            config["muse"][key] = bad
            try:
                routing_config.validate(config)
            except routing_config.ConfigError as exc:
                assert f"muse.{key}" in str(exc)
            else:
                raise AssertionError(f"muse.{key}={bad!r} must be rejected")


def test_catalog_drives_model_and_effort_mapping() -> None:
    catalog = model_catalog.bootstrap_catalog()
    entry = catalog["providers"]["muse"]["models"][MODEL]
    assert entry["tiers"] == ["advanced"]
    assert entry["capability"]["evidence"]["source"] == "bootstrap"
    mapping = model_catalog.provider_config_mapping("muse")
    assert mapping == {"models": {"advanced": MODEL}, "max_effort_by_tier": {"advanced": "high"}, "models_without_effort": []}
    assert model_catalog.provider_config_mapping("absent") == {"models": {}, "max_effort_by_tier": {}, "models_without_effort": []}
    config = planctl.default_config()
    assert config["muse"]["models"] == mapping["models"]
    assert config["muse"]["max_effort_by_tier"] == mapping["max_effort_by_tier"]

    # An effortless catalog model never receives a reasoning-effort flag.
    custom = copy.deepcopy(catalog)
    custom["providers"]["muse"]["models"][MODEL]["capability"].update(accepts_effort=False, max_effort=None)
    derived = model_catalog.provider_config_mapping("muse", custom)
    assert derived["models_without_effort"] == [MODEL] and derived["max_effort_by_tier"] == {}
    config["muse"].update(derived)
    assert worker(config) == ["muse", "exec", "--json", "--model", MODEL, "PROMPT"]


def test_unconfigured_muse_is_never_a_candidate() -> None:
    config = planctl.default_config()
    assert "muse" not in config["provider_order"]
    for tier in routing_config.TIER_ORDER:
        assert "muse" not in routing_config.provider_chain({"model_tier": tier}, config)
    with patch.object(run_isolated, "executable_available", lambda prefix: True):
        assert "muse" not in run_isolated.candidate_providers({"provider": "auto", "model_tier": "standard"}, config, None)
        assert run_isolated.summary_route(config)["provider"] != "muse"


def test_configured_muse_routes_to_catalog_model_with_capped_effort() -> None:
    config = planctl.default_config()
    config["provider_order"] = ["claude", "muse"]
    task = {"provider": "auto", "model_tier": "standard", "reasoning_effort": "medium", "functional_failures": 4}
    with patch.object(run_isolated, "executable_available", lambda prefix: True):
        route = run_isolated.choose_route(task, config, None)
        assert route["provider"] == "muse" and route["model"] == MODEL and route["tier"] == "advanced", route
        task.update(reasoning_effort="max")
        assert run_isolated.choose_route(task, config, None)["effort"] == "high"
    with patch.object(run_isolated, "executable_available", lambda prefix: prefix[0] != "muse"):
        assert run_isolated.candidate_providers({"provider": "auto", "model_tier": "standard"}, config, None) == ["claude"]


def test_worker_envelopes_yield_valid_report() -> None:
    report = sample_report()
    required = planctl.read_json(run_isolated.completion_schema_path())["required"]
    assert set(required) <= set(report)
    missing = Path(tempfile.gettempdir()) / "pae-muse-absent-result.json"
    envelopes = {
        "json": json.dumps({"type": "result", "is_error": False, "result": json.dumps(report), "usage": {"input_tokens": 3}}),
        "json-object": json.dumps({"result": report}),
        "jsonl": "\n".join(
            json.dumps(event)
            for event in (
                {"type": "system", "subtype": "init", "model": MODEL},
                {"type": "assistant", "message": {"content": [{"type": "text", "text": "Working."}]}},
                {"type": "result", "result": json.dumps(report)},
                {"type": "usage", "input_tokens": 3, "output_tokens": 4},
            )
        ),
        "jsonl-fenced": "\n".join(
            [json.dumps({"type": "assistant", "message": "```json\n" + json.dumps(report) + "\n```"}),
             json.dumps({"type": "usage", "input_tokens": 1})]
        ),
    }
    for name, stdout in envelopes.items():
        parsed = run_isolated.parse_provider_report("muse", stdout, missing)
        assert parsed is not None, name
        assert parsed["status"] == "completed" and parsed["completed_subtask_ids"] == ["S001"], name
        assert set(required) <= set(parsed), name
    assert run_isolated.parse_provider_report("muse", '{"type":"result","result":"no report"}', missing) is None


def test_summary_argv_is_read_only() -> None:
    config = planctl.default_config()
    config["muse"].update(trust_workspace=True, disable_approval=True)
    argv = summary(config)
    assert argv == ["muse", "exec", "--json", "--disable-write", "--model", MODEL, "--reasoning-effort", "medium", "PROMPT"], argv
    assert "--trust-workspace" not in argv and "--disable-approval" not in argv


def test_summary_fails_closed_without_provable_read_only() -> None:
    for widening in ("--trust-workspace", "--disable-approval"):
        config = planctl.default_config()
        config["muse"]["extra_args"] = [widening]
        try:
            summary(config)
        except run_isolated.RunnerError as exc:
            assert "read-only" in str(exc)
        else:
            raise AssertionError(f"{widening} in summary extra_args must fail closed")
    config = planctl.default_config()
    config["muse"]["extra_args"] = "--oops"
    try:
        summary(config)
    except run_isolated.RunnerError:
        pass
    else:
        raise AssertionError("malformed extra_args must fail closed")


def final_summary_fixture(config: dict, root: Path):
    plan_dir = root / "plan"
    (plan_dir / "logs").mkdir(parents=True)
    manifest = {"repo_root": str(root), "tasks": []}
    config["provider_order"] = ["muse"]
    config["summary"]["provider"] = "muse"
    return plan_dir, manifest


def test_final_summary_does_not_spawn_when_unprovable() -> None:
    config = planctl.default_config()
    config["muse"]["extra_args"] = ["--trust-workspace"]
    spawned: list[list[str]] = []
    with tempfile.TemporaryDirectory() as temp:
        plan_dir, manifest = final_summary_fixture(config, Path(temp))
        with patch.object(run_isolated, "executable_available", lambda prefix: True), \
                patch.object(run_isolated, "compose_summary_input", lambda *a: Path(temp) / "input.md"), \
                patch.object(run_isolated, "summary_prompt", lambda *a: "PROMPT"), \
                patch.object(planctl, "deterministic_summary", lambda manifest: "FALLBACK\n"), \
                patch.object(run_isolated, "run_process", lambda command, *a, **k: spawned.append(command) or (0, "", "")):
            text, _ = run_isolated.generate_final_summary(plan_dir, manifest, config, no_wait=True)
        assert text == "FALLBACK\n" and spawned == []


def test_final_summary_runs_read_only_and_reads_jsonl() -> None:
    config = planctl.default_config()
    spawned: list[list[str]] = []
    stdout = "\n".join(
        json.dumps(event)
        for event in ({"type": "init", "model": MODEL}, {"type": "result", "result": "All tasks finished."}, {"type": "usage"})
    )
    with tempfile.TemporaryDirectory() as temp:
        plan_dir, manifest = final_summary_fixture(config, Path(temp))
        with patch.object(run_isolated, "executable_available", lambda prefix: True), \
                patch.object(run_isolated, "compose_summary_input", lambda *a: Path(temp) / "input.md"), \
                patch.object(run_isolated, "summary_prompt", lambda *a: "PROMPT"), \
                patch.object(run_isolated, "run_process", lambda command, *a, **k: spawned.append(command) or (0, stdout, "")):
            text, _ = run_isolated.generate_final_summary(plan_dir, manifest, config, no_wait=True)
    assert text == "All tasks finished.\n", text
    assert len(spawned) == 1 and "--disable-write" in spawned[0]


def main() -> int:
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"muse provider self-test passed ({len(tests)} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
