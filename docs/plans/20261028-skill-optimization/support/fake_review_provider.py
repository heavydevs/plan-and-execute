#!/usr/bin/env python3
"""Fake `claude`/`codex` reviewer CLI for review_dispatch tests: no network, no model call.

Emits the real output shapes: Claude `--print --output-format json` result envelope (session_id,
usage, total_cost_usd, modelUsage, structured_output) and Codex `exec --json` JSONL events
(thread.started thread_id, turn.completed usage) plus the `--output-last-message` file.

Behaviour comes from the environment: FAKE_REVIEW_MODE_<PROVIDER> (or FAKE_REVIEW_MODE) is one of
approve, findings, quota, auth, garbage, nosession, error, sleep:<seconds>[:<mode>];
FAKE_REVIEW_SESSION fixes the session id; FAKE_REVIEW_ARGV_LOG appends each argv as one JSON line.
"""
from __future__ import annotations

import json
import os
import sys
import time
import uuid


def flag(argv: list[str], name: str) -> str | None:
    return argv[argv.index(name) + 1] if name in argv and argv.index(name) + 1 < len(argv) else None


def review(mode: str) -> dict:
    if mode == "findings":
        return {"verdict": "changes_requested", "summary": "One blocking defect.",
                "findings": [{"id": "F01", "severity": "high", "location": "test/optimization/unit.py:1",
                              "title": "Fixture defect", "detail": "Synthetic blocking finding.", "fix": "Fix it."},
                             {"id": "F02", "severity": "low", "location": "test/optimization/unit.py:1",
                              "title": "Nit", "detail": "Synthetic minor finding.", "fix": ""}]}
    return {"verdict": "approved", "summary": "No blocking defect.", "findings": []}


def main() -> int:
    argv = sys.argv[1:]
    provider = "codex" if argv[:1] == ["exec"] else "claude"
    log = os.environ.get("FAKE_REVIEW_ARGV_LOG")
    if log:
        with open(log, "a", encoding="utf-8") as handle:
            handle.write(json.dumps({"provider": provider, "argv": argv}) + "\n")
    mode = os.environ.get(f"FAKE_REVIEW_MODE_{provider.upper()}") or os.environ.get("FAKE_REVIEW_MODE", "approve")
    if mode.startswith("sleep:"):
        parts = mode.split(":")
        time.sleep(float(parts[1]))
        mode = parts[2] if len(parts) > 2 else "approve"
    session = os.environ.get("FAKE_REVIEW_SESSION") or str(uuid.uuid4())
    if mode == "quota":
        message = ("ERROR: Your workspace is out of credits. Ask your workspace owner to refill in order to continue."
                   if provider == "codex" else "API Error: 429 usage limit reached")
        print(message, file=sys.stderr)
        return 1
    if mode == "auth":
        print("Not authenticated. Please log in.", file=sys.stderr)
        return 1
    if mode == "error":
        print("internal failure", file=sys.stderr)
        return 2
    body = review(mode)
    model = flag(argv, "--model") or "default"
    if provider == "claude":
        if mode == "garbage":
            print("not json at all")
            return 0
        envelope = {"type": "result", "subtype": "success", "is_error": False, "duration_ms": 1200,
                    "num_turns": 3, "result": json.dumps(body), "stop_reason": "end_turn",
                    "session_id": None if mode == "nosession" else session, "total_cost_usd": 0.0123,
                    "usage": {"input_tokens": 12, "cache_creation_input_tokens": 300, "cache_read_input_tokens": 900,
                              "output_tokens": 150},
                    "modelUsage": {model: {"inputTokens": 12, "outputTokens": 150, "costUSD": 0.0123}},
                    "permission_denials": [], "terminal_reason": "completed", "structured_output": body}
        if mode == "nosession":
            envelope.pop("session_id")
        print(json.dumps(envelope))
        return 0
    events = []
    if mode != "nosession":
        events.append({"type": "thread.started", "thread_id": session})
    events += [{"type": "turn.started"},
               {"type": "item.completed", "item": {"id": "item_0", "type": "agent_message",
                                                     "text": "not json" if mode == "garbage" else json.dumps(body)}},
               {"type": "turn.completed", "usage": {"input_tokens": 40, "cached_input_tokens": 10, "output_tokens": 60}}]
    for event in events:
        print(json.dumps(event))
    last = flag(argv, "--output-last-message") or flag(argv, "-o")
    if last:
        with open(last, "w", encoding="utf-8") as handle:
            handle.write("not json" if mode == "garbage" else json.dumps(body))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
