#!/usr/bin/env python3
"""Focused self-tests for optional isolated-provider adapters."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import planctl  # noqa: E402
import run_isolated  # noqa: E402


def sample_route(model: str = "default") -> dict[str, str]:
    return {
        "provider": "test",
        "tier": "standard",
        "model": model,
        "effort": "medium",
    }


def sample_report() -> dict:
    return {
        "status": "completed",
        "summary": "Completed the isolated provider test task.",
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


def test_default_provider_policy() -> None:
    config = planctl.default_config()
    assert config["provider_order"] == ["claude", "codex"]
    assert set(config) >= {"claude", "codex", "antigravity", "gemini", "qwen", "kimi", "trae"}
    assert planctl.VALID_PROVIDERS == {
        "auto",
        "claude",
        "codex",
        "antigravity",
        "gemini",
        "qwen",
        "kimi",
        "trae",
        "muse",
    }


def test_worker_command_adapters() -> None:
    config = planctl.default_config()
    with tempfile.TemporaryDirectory() as temp:
        result_path = Path(temp) / "results" / "001.json"
        result_path.parent.mkdir(parents=True)
        commands = {
            provider: run_isolated.build_worker_command(
                provider,
                {**sample_route(), "provider": provider},
                config,
                "Implement only the assigned task.",
                result_path,
            )
            for provider in ("claude", "codex", "antigravity", "gemini", "qwen", "kimi", "trae")
        }

    agy = commands["antigravity"]
    assert agy[0] == "agy"
    assert "--dangerously-skip-permissions" in agy
    assert "--sandbox" not in agy, "workers must be able to run validation commands"
    assert agy[agy.index("--output-format") + 1] == "json"
    assert "--json-schema" in agy
    assert agy[agy.index("--effort") + 1] == "medium"
    assert agy[agy.index("--print-timeout") + 1] == "12h", "no runner limit -> long agy window"
    bounded = dict(config)
    bounded["task_timeout_seconds"] = 1800
    with tempfile.TemporaryDirectory() as temp:
        result_path = Path(temp) / "r.json"
        result_path.parent.mkdir(parents=True, exist_ok=True)
        timed = run_isolated.build_worker_command(
            "antigravity", {**sample_route(), "provider": "antigravity"}, bounded, "x", result_path
        )
        assert timed[timed.index("--print-timeout") + 1] == "1800s"
        explicit = dict(bounded)
        explicit["antigravity"] = {**config["antigravity"], "print_timeout": "45m"}
        fixed = run_isolated.build_worker_command(
            "antigravity", {**sample_route(), "provider": "antigravity"}, explicit, "x", result_path
        )
        assert fixed[fixed.index("--print-timeout") + 1] == "45m"
    assert agy[-2:] == ["-p", "Implement only the assigned task."]
    assert "--model" not in agy

    claude = commands["claude"]
    assert claude[0] == "claude"
    assert "--no-session-persistence" in claude
    assert "--json-schema" in claude

    codex = commands["codex"]
    assert codex[:3] == ["codex", "exec", "--ephemeral"]
    assert "--output-schema" in codex
    assert "--output-last-message" in codex

    gemini = commands["gemini"]
    assert gemini[0] == "gemini"
    assert gemini[gemini.index("--approval-mode") + 1] == "yolo"
    assert gemini[gemini.index("--output-format") + 1] == "json"
    assert "--prompt" in gemini
    assert "--model" not in gemini

    qwen = commands["qwen"]
    assert qwen[0] == "qwen"
    assert "--safe-mode" in qwen
    assert qwen[qwen.index("--output-format") + 1] == "json"
    assert "--json-schema" in qwen
    assert "--prompt" in qwen
    assert "--model" not in qwen

    kimi = commands["kimi"]
    assert kimi[0] == "kimi"
    assert kimi[kimi.index("--output-format") + 1] == "stream-json"
    assert "--auto" in kimi
    assert "--prompt" in kimi
    assert "--model" not in kimi
    for incompatible in ("--print", "--final-message-only", "--plan", "--yolo"):
        assert incompatible not in kimi

    trae = commands["trae"]
    assert trae[:2] == ["trae-cli", "run"]
    assert "--working-dir" in trae
    assert "--trajectory-file" in trae
    assert "--model" not in trae


PROVIDERS = ("claude", "codex", "antigravity", "gemini", "qwen", "kimi", "trae")

# Captured from the pre-profile adapters; unchanged configuration must keep these argv byte-identical.
GOLDEN_ARGV: dict[str, list[str]] = {
    "default/worker/claude": ["claude", "--print", "--no-session-persistence", "--output-format", "json", "--permission-mode", "auto", "--effort", "medium", "--json-schema", "<schema>", "PROMPT"],
    "default/summary/claude": ["claude", "--print", "--no-session-persistence", "--output-format", "text", "--permission-mode", "plan", "--effort", "medium", "PROMPT"],
    "default/worker/codex": ["codex", "exec", "--ephemeral", "--sandbox", "workspace-write", "-c", "model_reasoning_effort=\"medium\"", "--output-schema", "<tmp>/results/codex-output-schema.json", "--output-last-message", "<tmp>/results/007.json", "PROMPT"],
    "default/summary/codex": ["codex", "exec", "--ephemeral", "--sandbox", "read-only", "-c", "model_reasoning_effort=\"medium\"", "--output-last-message", "<tmp>/FINAL_SUMMARY.md", "PROMPT"],
    "default/worker/antigravity": ["agy", "--dangerously-skip-permissions", "--output-format", "json", "--json-schema", "<agy-schema>", "--effort", "medium", "--print-timeout", "12h", "-p", "PROMPT"],
    "default/summary/antigravity": ["agy", "--dangerously-skip-permissions", "--sandbox", "--output-format", "json", "--effort", "medium", "--print-timeout", "12h", "-p", "PROMPT"],
    "default/worker/gemini": ["gemini", "--approval-mode", "yolo", "--output-format", "json", "--extensions", "none", "--prompt", "PROMPT"],
    "default/summary/gemini": ["gemini", "--approval-mode", "plan", "--output-format", "json", "--extensions", "none", "--prompt", "PROMPT"],
    "default/worker/qwen": ["qwen", "--safe-mode", "--output-format", "json", "--approval-mode", "yolo", "--json-schema", "<schema>", "--prompt", "PROMPT"],
    "default/summary/qwen": ["qwen", "--safe-mode", "--approval-mode", "plan", "--output-format", "json", "--prompt", "PROMPT"],
    "default/worker/kimi": ["kimi", "--output-format", "stream-json", "--auto", "--prompt", "PROMPT"],
    "default/summary/kimi": ["kimi", "--output-format", "stream-json", "--plan", "--prompt", "PROMPT"],
    "default/worker/trae": ["trae-cli", "run", "PROMPT", "--working-dir", ".", "--trajectory-file", "<tmp>/logs/007-trae-trajectory.json"],
    "default/summary/trae": ["trae-cli", "run", "PROMPT", "--working-dir", ".", "--trajectory-file", "<tmp>/logs/final-summary-trae-trajectory.json"],
    "tuned/worker/claude": ["claude", "--print", "--no-session-persistence", "--output-format", "json", "--permission-mode", "auto", "--model", "m-1", "--effort", "high", "--max-turns", "7", "--max-budget-usd", "1.50", "--json-schema", "<schema>", "--verbose", "PROMPT"],
    "tuned/summary/claude": ["claude", "--print", "--no-session-persistence", "--output-format", "text", "--permission-mode", "plan", "--model", "m-1", "--effort", "high", "--verbose", "PROMPT"],
    "tuned/worker/codex": ["codex", "exec", "--ephemeral", "--sandbox", "workspace-write", "--model", "m-1", "-c", "model_reasoning_effort=\"high\"", "-c", "features.rollout_budget.enabled=true", "-c", "features.rollout_budget.limit_tokens=1000", "--output-schema", "<tmp>/results/codex-output-schema.json", "--output-last-message", "<tmp>/results/007.json", "--ignore-user-config", "-c", "x=1", "PROMPT"],
    "tuned/summary/codex": ["codex", "exec", "--ephemeral", "--sandbox", "read-only", "--model", "m-1", "-c", "model_reasoning_effort=\"high\"", "--output-last-message", "<tmp>/FINAL_SUMMARY.md", "--ignore-user-config", "-c", "x=1", "PROMPT"],
    "tuned/worker/antigravity": ["agy", "--dangerously-skip-permissions", "--sandbox", "--output-format", "json", "--json-schema", "<agy-schema>", "--model", "m-1", "--effort", "high", "--print-timeout", "45m", "-p", "PROMPT"],
    "tuned/summary/antigravity": ["agy", "--sandbox", "--output-format", "json", "--model", "m-1", "--effort", "high", "--print-timeout", "45m", "-p", "PROMPT"],
    "tuned/worker/gemini": ["gemini", "--approval-mode", "yolo", "--output-format", "json", "--model", "m-1", "--prompt", "PROMPT"],
    "tuned/summary/gemini": ["gemini", "--approval-mode", "plan", "--output-format", "json", "--model", "m-1", "--prompt", "PROMPT"],
    "tuned/worker/qwen": ["qwen", "--sandbox", "--output-format", "json", "--approval-mode", "yolo", "--json-schema", "<schema>", "--model", "m-1", "--prompt", "PROMPT"],
    "tuned/summary/qwen": ["qwen", "--approval-mode", "plan", "--output-format", "json", "--model", "m-1", "--prompt", "PROMPT"],
    "tuned/worker/kimi": ["kimi", "--output-format", "stream-json", "--yolo", "--model", "m-1", "--prompt", "PROMPT"],
    "tuned/summary/kimi": ["kimi", "--output-format", "stream-json", "--model", "m-1", "--prompt", "PROMPT"],
    "tuned/worker/trae": ["trae-cli", "run", "PROMPT", "--working-dir", ".", "--trajectory-file", "<tmp>/logs/007-trae-trajectory.json", "--provider", "openrouter", "--model", "m-1", "--max-steps", "9"],
    "tuned/summary/trae": ["trae-cli", "run", "PROMPT", "--working-dir", ".", "--trajectory-file", "<tmp>/logs/final-summary-trae-trajectory.json", "--provider", "openrouter", "--model", "m-1", "--max-steps", "9"],
}


def golden_configs() -> dict[str, tuple[dict, dict[str, str]]]:
    """Default and tuned configurations, each with the route used for every provider."""
    tuned = planctl.default_config()
    tuned["claude"].update(max_turns=7, max_budget_usd=1.5, extra_args=["--verbose"])
    tuned["codex"].update(rollout_token_budget=1000, ignore_user_config=True, extra_args=["-c", "x=1"])
    tuned["antigravity"].update(print_timeout="45m", sandbox=True, summary_skip_permissions=False)
    tuned["gemini"].update(disable_extensions=False, summary_approval_mode="plan")
    tuned["qwen"].update(safe_mode=False, sandbox=True)
    tuned["kimi"].update(permission_mode="yolo", summary_permission_mode="")
    tuned["trae"].update(model_provider="openrouter", extra_args=["--max-steps", "9"])
    tuned["task_timeout_seconds"] = 1800
    return {
        "default": (planctl.default_config(), sample_route()),
        "tuned": (tuned, {**sample_route("m-1"), "effort": "high"}),
    }


def golden_argv() -> dict[str, dict[str, list[str]]]:
    """Worker and summary argv per provider, with temp paths and schema text normalized."""
    schema = planctl.read_json(run_isolated.completion_schema_path())
    placeholders = {
        json.dumps(schema, ensure_ascii=False, separators=(",", ":")): "<schema>",
        run_isolated.antigravity_schema_text(schema): "<agy-schema>",
    }
    out: dict[str, dict[str, list[str]]] = {}
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        result_path = root / "results" / "007.json"
        result_path.parent.mkdir(parents=True)

        def normalize(command: list[str]) -> list[str]:
            return [
                placeholders.get(item) or item.replace(str(root), "<tmp>").replace("\\", "/")
                for item in command
            ]

        for name, (config, route) in golden_configs().items():
            for provider in PROVIDERS:
                provider_route = {**route, "provider": provider}
                out[f"{name}/worker/{provider}"] = normalize(
                    run_isolated.build_worker_command(provider, provider_route, config, "PROMPT", result_path)
                )
                out[f"{name}/summary/{provider}"] = normalize(
                    run_isolated.build_summary_command(provider, provider_route, config, "PROMPT", root / "FINAL_SUMMARY.md")
                )
    return out


def test_golden_argv_unchanged() -> None:
    with patch.dict("os.environ"):
        os.environ.pop("ANTHROPIC_API_KEY", None)
        actual = golden_argv()
    assert actual == GOLDEN_ARGV, [key for key in GOLDEN_ARGV if actual.get(key) != GOLDEN_ARGV[key]]


def test_profile_composes_existing_adapter() -> None:
    base = planctl.default_config()
    config = planctl.default_config()
    config["profiles"] = {"gw": {"harness": "claude", "command": "gw-claude", "token_env": "GW_TOKEN"}}
    config["kimi"]["profile"] = "gw"
    route = {**sample_route("kimi-model"), "provider": "kimi"}
    with tempfile.TemporaryDirectory() as temp:
        result_path = Path(temp) / "results" / "001.json"
        result_path.parent.mkdir(parents=True)
        summary_path = Path(temp) / "FINAL_SUMMARY.md"
        for provider in PROVIDERS:
            if provider == "kimi":
                continue
            other = {**sample_route(), "provider": provider}
            for build, path in ((run_isolated.build_worker_command, result_path), (run_isolated.build_summary_command, summary_path)):
                assert build(provider, other, config, "P", path) == build(provider, other, base, "P", path), provider

        worker = run_isolated.build_worker_command("kimi", route, config, "P", result_path)
        assert worker[0] == "gw-claude" and "--no-session-persistence" in worker and "--json-schema" in worker
        assert worker[worker.index("--model") + 1] == "kimi-model", "provider settings survive the harness swap"
        summary = run_isolated.build_summary_command("kimi", route, config, "P", summary_path)
        assert summary[summary.index("--permission-mode") + 1] == "plan", "claude harness keeps its read-only summary"

        config["profiles"]["gw"]["harness"] = "codex"  # harness changes; profile command/credentials do not
        worker = run_isolated.build_worker_command("kimi", route, config, "P", result_path)
        assert worker[:3] == ["gw-claude", "exec", "--ephemeral"] and "--output-schema" in worker
        summary = run_isolated.build_summary_command("kimi", route, config, "P", summary_path)
        assert summary[summary.index("--sandbox") + 1] == "read-only"
        del config["profiles"]["gw"]["command"]
        assert run_isolated.build_worker_command("kimi", route, config, "P", result_path)[0] == "codex"

        config["profiles"]["gw"]["harness"] = "native"
        worker = run_isolated.build_worker_command("kimi", route, config, "P", result_path)
        assert worker == run_isolated.build_worker_command("kimi", route, base, "P", result_path)

    unknown = {**base, "custom": {"profile": "x"}, "profiles": {"x": {"harness": "native"}}}
    try:
        run_isolated.build_summary_command("custom", {**sample_route(), "provider": "custom"}, unknown, "P", Path("s.md"))
    except run_isolated.RunnerError as exc:
        assert "Unsupported summary provider adapter" in str(exc)
    else:
        raise AssertionError("a summary adapter without a proven read-only mode must fail closed")


def test_profile_secrets_reach_child_env_only() -> None:
    secret = "sk-planted-SECRET-0003"
    config = planctl.default_config()
    config["profiles"] = {"gw": {"harness": "claude", "base_url_env": "GW_URL", "token_env": "GW_TOKEN"}}
    config["kimi"]["profile"] = "gw"
    assert run_isolated.spawn_env("claude", config, {}) is None, "profiles without env names inherit unchanged"
    try:
        run_isolated.spawn_env("kimi", config, {"GW_URL": "https://gw.example"})
    except run_isolated.RunnerError as exc:
        assert "GW_TOKEN" in str(exc)
    else:
        raise AssertionError("a missing credential variable must fail before spawning")
    environ = {"PATH": os.environ.get("PATH", ""), "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
               "GW_URL": "https://gw.example", "GW_TOKEN": secret}
    env = run_isolated.spawn_env("kimi", config, environ)
    assert env is not None and env["ANTHROPIC_AUTH_TOKEN"] == secret and env["ANTHROPIC_BASE_URL"] == "https://gw.example"
    # The child proves it received the mapped value without the value appearing in argv.
    probe = "import os,sys; print('child ok'); sys.exit(0 if os.environ['ANTHROPIC_AUTH_TOKEN'] == os.environ['GW_TOKEN'] else 3)"
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        result_path = root / "results" / "001.json"
        result_path.parent.mkdir(parents=True)
        command = run_isolated.build_worker_command("kimi", {**sample_route(), "provider": "kimi"}, config, "P", result_path)
        dry_run = json.dumps({"task": "001", "route": sample_route(), "command": run_isolated.redact_command(command)})
        code, stdout, stderr = run_isolated.run_process(
            [sys.executable, "-c", probe], root, root / "logs" / "001-attempt-1-kimi.log",
            timeout_seconds=60, stream_output=False, env=env,
        )
        assert code == 0 and "child ok" in stdout, (code, stderr)
        written = [path.read_text(encoding="utf-8") for path in root.rglob("*") if path.is_file()]
        assert written and all(secret not in text for text in [*written, dry_run, stdout, stderr])


def test_configured_models_are_forwarded() -> None:
    config = planctl.default_config()
    with tempfile.TemporaryDirectory() as temp:
        result_path = Path(temp) / "result.json"
        for provider in ("antigravity", "gemini", "qwen", "kimi", "trae"):
            command = run_isolated.build_worker_command(
                provider,
                {**sample_route("provider-model"), "provider": provider},
                config,
                "Do the task.",
                result_path,
            )
            assert command[command.index("--model") + 1] == "provider-model"


def test_provider_report_envelopes() -> None:
    report = sample_report()
    encoded = json.dumps(report)
    with tempfile.TemporaryDirectory() as temp:
        result_path = Path(temp) / "result.json"
        envelopes = {
            "claude": json.dumps({"type": "result", "structured_output": report}),
            "antigravity": json.dumps(
                {
                    "conversation_id": "abc",
                    "status": "SUCCESS",
                    "response": "done",
                    "structured_output": report,
                    "usage": {"input_tokens": 1, "output_tokens": 1},
                }
            ),
            "gemini": json.dumps({"response": encoded}),
            "qwen": json.dumps(
                [
                    {"type": "system", "subtype": "session_start"},
                    {"type": "result", "subtype": "success", "result": encoded},
                ]
            ),
            "kimi": "\n".join(
                [
                    json.dumps({"type": "tool", "content": "ignored"}),
                    json.dumps(
                        {
                            "type": "assistant",
                            "message": {
                                "role": "assistant",
                                "content": [{"type": "text", "text": encoded}],
                            },
                        }
                    ),
                ]
            ),
            "trae": encoded,
        }
        for provider, stdout in envelopes.items():
            parsed = run_isolated.parse_provider_report(provider, stdout, result_path)
            assert parsed == report, provider

        result_path.write_text(encoded, encoding="utf-8")
        parsed_codex = run_isolated.parse_provider_report("codex", "", result_path)
        assert parsed_codex == report

        fenced = f"Completed.\n\n```json\n{json.dumps(report, indent=2)}\n```\n"
        assert run_isolated.parse_provider_report("trae", fenced, Path(temp) / "missing.json") == report


def test_summary_envelopes_and_retry_codes() -> None:
    summary = "# Result\n\nEverything passed."
    kimi_stdout = json.dumps(
        {
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [{"type": "text", "text": summary}],
            },
        }
    )
    agy_stdout = json.dumps({"conversation_id": "abc", "status": "SUCCESS", "response": summary})
    with tempfile.TemporaryDirectory() as temp:
        output_path = Path(temp) / "summary.md"
        assert run_isolated.summary_stdout_text("kimi", kimi_stdout, output_path) == summary
        assert run_isolated.summary_stdout_text("antigravity", agy_stdout, output_path) == summary
        agy_summary = run_isolated.build_summary_command(
            "antigravity",
            {**sample_route(), "provider": "antigravity", "effort": "xhigh"},
            planctl.default_config(),
            "Summarize.",
            output_path,
        )
        assert "--sandbox" in agy_summary and "--dangerously-skip-permissions" in agy_summary
        assert agy_summary[agy_summary.index("--effort") + 1] == "xhigh", "clamping happens in choose_route, not the adapter"

    config = planctl.default_config()
    assert run_isolated.is_provider_availability_failure("kimi", 75, "transient", config)
    assert run_isolated.is_provider_availability_failure("gemini", 1, "HTTP 429", config)
    config["qwen"]["retry_exit_codes"] = [True]
    try:
        run_isolated.configured_retry_exit_codes("qwen", config)
    except run_isolated.RunnerError as exc:
        assert "list of integers" in str(exc)
    else:
        raise AssertionError("Expected invalid retry_exit_codes to be rejected")


def test_kimi_prompt_contract_and_redaction() -> None:
    config = planctl.default_config()
    with tempfile.TemporaryDirectory() as temp:
        result_path = Path(temp) / "result.json"
        worker = run_isolated.build_worker_command(
            "kimi",
            {**sample_route(), "provider": "kimi"},
            config,
            "You are a fresh, isolated implementation worker for one bounded task.\nSecret details.",
            result_path,
        )
        assert "--auto" in worker
        for incompatible in ("--yolo", "--plan"):
            assert incompatible not in worker
        redacted = run_isolated.redact_command(worker)
        assert "<prompt>" in redacted
        assert all("Secret details" not in item for item in redacted)

        summary = run_isolated.build_summary_command(
            "kimi",
            {**sample_route(), "provider": "kimi"},
            config,
            "You are a fresh, isolated final summarizer.\nSecret summary input.",
            Path(temp) / "summary.md",
        )
        assert "--plan" in summary
        for incompatible in ("--auto", "--yolo"):
            assert incompatible not in summary

        config["kimi"]["permission_mode"] = "interactive"
        try:
            run_isolated.build_worker_command(
                "kimi",
                {**sample_route(), "provider": "kimi"},
                config,
                "Do the task.",
                result_path,
            )
        except run_isolated.RunnerError as exc:
            assert "kimi.permission_mode" in str(exc)
        else:
            raise AssertionError("Expected invalid Kimi permission mode to be rejected")

        gemini_summary = run_isolated.build_summary_command(
            "gemini",
            {**sample_route(), "provider": "gemini"},
            config,
            "Summarize without edits.",
            Path(temp) / "gemini-summary.md",
        )
        assert gemini_summary[gemini_summary.index("--approval-mode") + 1] == "plan"


def test_codex_output_schema_is_api_compatible() -> None:
    canonical = planctl.read_json(run_isolated.completion_schema_path())
    assert "uniqueItems" in json.dumps(canonical), "canonical schema keeps the full dialect"

    derived = run_isolated.codex_output_schema(canonical)
    derived_text = json.dumps(derived)
    for keyword in run_isolated.CODEX_UNSUPPORTED_SCHEMA_KEYWORDS:
        assert keyword not in derived_text, f"codex schema must not carry {keyword}"
    assert "uniqueItems" in json.dumps(canonical), "derivation must not mutate the canonical schema"

    def assert_strict(node: object) -> None:
        if isinstance(node, dict):
            if node.get("type") == "object" and isinstance(node.get("properties"), dict):
                assert node.get("required") == list(node["properties"].keys()), (
                    "strict mode needs every property in required"
                )
                assert node.get("additionalProperties") is False
            for value in node.values():
                assert_strict(value)
        elif isinstance(node, list):
            for item in node:
                assert_strict(item)

    assert_strict(derived)
    assert set(derived["required"]) >= set(canonical["required"])
    assert "failure_class" in derived["required"] and "pattern_files_read" in derived["required"]

    config = planctl.default_config()
    with tempfile.TemporaryDirectory() as temp:
        result_path = Path(temp) / "results" / "001.json"
        result_path.parent.mkdir(parents=True)
        codex = run_isolated.build_worker_command(
            "codex", {**sample_route(), "provider": "codex"}, config, "x", result_path
        )
        schema_arg = Path(codex[codex.index("--output-schema") + 1])
        assert schema_arg.parent == result_path.parent
        assert schema_arg.name == run_isolated.CODEX_OUTPUT_SCHEMA_NAME
        assert planctl.read_json(schema_arg) == derived
        claude = run_isolated.build_worker_command(
            "claude", {**sample_route(), "provider": "claude"}, config, "x", result_path
        )
        assert "uniqueItems" in claude[claude.index("--json-schema") + 1], (
            "other providers keep the canonical schema"
        )

    duplicated = {
        **sample_report(),
        "context_files_read": ["CONTEXT.md", "CONTEXT.md", "scoped.md"],
        "completed_subtask_ids": ["S001", "S002", "S001"],
        "reusable_learnings": [
            {
                "kind": "procedure",
                "guidance": "Run the schema self-test after touching completion-report.schema.json.",
                "references": ["scripts/run_isolated.py", "scripts/run_isolated.py"],
                "target_task_ids": ["002", "002", "003"],
            }
        ],
    }
    parsed = run_isolated.parse_provider_report("codex", json.dumps(duplicated), Path("missing.json"))
    assert parsed is not None
    assert parsed["context_files_read"] == ["CONTEXT.md", "scoped.md"]
    assert parsed["completed_subtask_ids"] == ["S001", "S002"]
    assert parsed["reusable_learnings"][0]["references"] == ["scripts/run_isolated.py"]
    assert parsed["reusable_learnings"][0]["target_task_ids"] == ["002", "003"]
    assert parsed["changed_files"] == ["sample.txt"], "lists without a uniqueness contract are untouched"
    mixed = run_isolated.normalize_report({"completed_subtask_ids": ["S001", 1, "S001"]})
    assert mixed["completed_subtask_ids"] == ["S001", 1, "S001"], "non-string lists are left to planctl"


def test_context_report_ignores_extra_repository_reads() -> None:
    plan_dir = Path("C:/repo/.ai-work/plan-1")
    expected = ["CONTEXT.md", "contexts/a.md"]
    baseline = sorted(run_isolated._plan_relative_files(expected, plan_dir))

    def check(reported: object) -> bool:
        return run_isolated._plan_context_files(reported, plan_dir, expected, "tasks/001-x.md") == baseline

    assert check(["CONTEXT.md", "contexts/a.md"])
    assert check(["contexts/a.md", "CONTEXT.md", "CONTEXT.md"]), "order and repeats are not part of the assignment"
    assert check(
        [
            ".ai-work/plan-1/CONTEXT.md",
            ".ai-work/plan-1/contexts/a.md",
            ".ai-work/plan-1/patterns/assignments/001.md",
            "docs/architecture/x.md",
            ".ai-work/SERVICE_MAP.md",
        ]
    ), "repository docs and pattern reads are not context assignments"
    assert check(["C:\\repo\\.ai-work\\plan-1\\CONTEXT.md", "contexts\\a.md"]), "Windows separators are normalized"
    assert not check(["CONTEXT.md"]), "an assigned context that was not read is still a mismatch"
    assert not check(["CONTEXT.md", "contexts/a.md", "contexts/b.md"]), "an unassigned scoped context is still a mismatch"
    assert not check(None)


def test_refresh_manifest_keeps_external_edits() -> None:
    with tempfile.TemporaryDirectory() as raw:
        plan_dir = Path(raw)
        planctl.atomic_write_json(plan_dir / planctl.MANIFEST, {"tasks": [{"id": "001"}, {"id": "046"}], "updated_at": "later"})
        held = {"id": "001", "status": "in_progress"}
        stale = {"tasks": [held], "updated_at": "earlier"}
        run_isolated.refresh_manifest(plan_dir, stale)
        assert stale["tasks"][0] is held and "status" not in held, "a task the caller holds is refreshed in place"
        assert [task["id"] for task in stale["tasks"]] == ["001", "046"], "a task inserted while the worker ran survives"
        assert stale["updated_at"] == "later"


def main() -> int:
    test_context_report_ignores_extra_repository_reads()
    test_refresh_manifest_keeps_external_edits()
    test_default_provider_policy()
    # Bare adapter names must not depend on which CLIs this host has on PATH.
    with patch.object(run_isolated, "resolve_windows_shim", side_effect=lambda parts: parts):
        test_worker_command_adapters()
        test_configured_models_are_forwarded()
        test_golden_argv_unchanged()
        test_profile_composes_existing_adapter()
        test_profile_secrets_reach_child_env_only()
    test_provider_report_envelopes()
    test_summary_envelopes_and_retry_codes()
    test_kimi_prompt_contract_and_redaction()
    test_codex_output_schema_is_api_compatible()
    print("All provider-adapter self-tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
