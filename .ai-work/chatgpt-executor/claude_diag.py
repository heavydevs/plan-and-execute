#!/usr/bin/env python3
"""Publish only allowlisted failure metadata from a Claude Action JSON event log.

The raw event log may contain user prompts and credentials. Never output it,
upload it, interpolate it into workflow expressions, or include raw exception text.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import re

BASE = Path(".ai-work/chatgpt-executor/claude-artifacts")
STATUS = {"authentication_failed", "quota_or_rate_limit", "permission_denied", "model_unavailable", "runtime_failure", "unknown"}


def parse(path: Path) -> dict:
    fallback = {"schema": "pae-claude-diagnostic/1", "status": "unavailable", "category": "unknown", "http_status": None}
    try:
        if not path.is_file() or path.stat().st_size > 8_000_000:
            return fallback
        data = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError, UnicodeError):
        return fallback
    if isinstance(data, dict):
        data = data.get("messages", data.get("events", [data]))
    if not isinstance(data, list):
        return fallback
    for event in reversed(data):
        if not isinstance(event, dict) or event.get("type") != "result":
            continue
        error = event.get("is_error") is True
        status = event.get("api_error_status", event.get("error_status"))
        if type(status) is not int or not 100 <= status <= 599:
            status = None
        # Inputs for classification are never persisted or printed.
        raw = " ".join(str(event.get(key, "")) for key in ("error", "result", "terminal_reason")).lower()
        category = "unknown"
        if status == 401 or "authentication_failed" in raw or "failed to authenticate" in raw:
            category = "authentication_failed"
        elif status == 429 or "rate limit" in raw or "quota" in raw or "usage limit" in raw:
            category = "quota_or_rate_limit"
        elif status == 403 or "permission denied" in raw:
            category = "permission_denied"
        elif status == 404 or "model not available" in raw or "model_unavailable" in raw:
            category = "model_unavailable"
        elif error:
            category = "runtime_failure"
        assert category in STATUS
        return {
            "schema": "pae-claude-diagnostic/1",
            "status": "failed" if error else "completed",
            "category": category,
            "http_status": status,
            "is_error": error,
            "num_turns": event.get("num_turns") if type(event.get("num_turns")) is int else None,
            "model_usage_present": bool(event.get("modelUsage")),
            "note": "Only coarse allowlisted signals. No model output, token, prompt, secret, or raw error was preserved.",
        }
    return fallback


def main() -> None:
    temp = Path(os.environ.get("RUNNER_TEMP", "/tmp"))
    result = parse(temp / "claude-execution-output.json")
    BASE.mkdir(parents=True, exist_ok=True)
    (BASE / "diagnostic.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"diagnostic": result.get("status"), "category": result.get("category"),
                      "http_status": result.get("http_status")}))


if __name__ == "__main__":
    main()
