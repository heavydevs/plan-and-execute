#!/usr/bin/env python3
"""Focused self-tests for optional isolated-provider adapters."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

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


def main() -> int:
    test_default_provider_policy()
    test_worker_command_adapters()
    test_configured_models_are_forwarded()
    test_provider_report_envelopes()
    test_summary_envelopes_and_retry_codes()
    test_kimi_prompt_contract_and_redaction()
    test_codex_output_schema_is_api_compatible()
    print("All provider-adapter self-tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
