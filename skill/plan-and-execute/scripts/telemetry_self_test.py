#!/usr/bin/env python3
"""Self-test for metadata-only attempt telemetry and the bounded rollup."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import routing_telemetry as rt  # noqa: E402

SECRET_PROMPT = "PLANTED-PROMPT-STRING-do-not-persist"
PROFILE = {"name": "glm", "harness": "claude"}
ROUTE = {"provider": "claude", "model": "m-1", "effort": "medium"}
TASK = {"id": "015", "task_class": "implementation", "validation_strength": "deterministic"}


def make(kind: str, stdout: str = "", passed=None, retry=0):
    return rt.build_record(
        task=TASK, route=ROUTE, profile=PROFILE, kind=kind, stdout=stdout, latency_seconds=1.5,
        outcome="completed" if passed else "validation_failed", validation_pass=passed, retry_count=retry,
    )


def main() -> None:
    claude_env = json.dumps({
        "type": "result", "result": SECRET_PROMPT, "total_cost_usd": 0.25,
        "usage": {"input_tokens": 10, "cache_read_input_tokens": 4, "cache_creation_input_tokens": 2, "output_tokens": 7},
    })
    record = make("root", claude_env, True)
    assert record["input_tokens"] == 10 and record["cached_tokens"] == 4
    assert record["cache_write_tokens"] == 2 and record["output_tokens"] == 7 and record["usd"] == 0.25
    for field in ("profile", "harness", "model", "native_effort"):
        assert record[field], field
    assert record["profile"] == "glm" and record["harness"] == "claude" and record["native_effort"] == "medium"
    assert SECRET_PROMPT not in json.dumps(record)

    codex_env = '{"type":"turn.completed","usage":{"input_tokens":5,"cached_input_tokens":1,"output_tokens":3}}'
    codex = make("subagent", "noise\n" + codex_env, True)
    assert codex["input_tokens"] == 5 and codex["cached_tokens"] == 1 and codex["usd"] is None

    bare = make("diagnostic", "no json at all", None)
    assert all(bare[f] is None for f in rt.USAGE_FIELDS), "missing usage stays null"
    assert rt.extract_usage('{"usage":{"input_tokens":"x"}}')["input_tokens"] is None

    with tempfile.TemporaryDirectory() as tmp:
        plan = Path(tmp) / "plan"
        plan.mkdir()
        for item in (record, codex, bare, make("retry", claude_env, False, 1), make("summary", codex_env, None)):
            assert rt.append_record(plan, item)
        path = rt.telemetry_path(plan)
        assert SECRET_PROMPT not in path.read_text(encoding="utf-8")
        assert "skill" not in path.relative_to(plan).parts
        records = rt.read_records(path)
        assert len(records) == 5
        first = rt.rollup_json(records)
        assert first == rt.rollup_json(list(reversed(records))) == rt.rollup_json(records), "deterministic"
        out = json.loads(first)
        assert out["totals"]["attempts"] == 5 and out["totals"]["validated"] == 2
        assert set(out["by_kind"]) == set(rt.KINDS)
        assert out["totals"]["input_tokens"] == 10 + 5 + 10 + 5
        assert out["per_validated_result"]["input_tokens"] == 15.0
        assert out["totals"]["credits"] is None
        bound = 700
        small = rt.rollup_json(records * 20, bound)
        assert len(small) <= bound * 2 and json.loads(small)["truncated"] is True
        assert len(json.dumps(json.loads(small), sort_keys=True)) <= bound
        empty = json.loads(rt.rollup_json([]))
        assert empty["per_validated_result"]["input_tokens"] is None

    assert not (SCRIPT_DIR / "telemetry").exists()
    print("telemetry_self_test: ok")


if __name__ == "__main__":
    main()
