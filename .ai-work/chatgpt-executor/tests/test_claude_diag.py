#!/usr/bin/env python3
"""Offline privacy regression for failed Claude Action evidence."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory

SCRIPT = Path(__file__).resolve().parents[1] / "claude_diag.py"
spec = importlib.util.spec_from_file_location("pae_claude_diag", SCRIPT)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def check():
    secret = "sk-ant-oat01-DO_NOT_LEAK"
    with TemporaryDirectory() as temp:
        file = Path(temp) / "session.json"
        for status, reason, category in [
            (401, f"Failed to authenticate: {secret}", "authentication_failed"),
            (429, f"rate limit reached {secret}", "quota_or_rate_limit"),
            (403, f"Permission denied {secret}", "permission_denied"),
            (None, f"unknown failure {secret}", "runtime_failure"),
        ]:
            file.write_text(json.dumps([
                {"type": "system", "model": "claude-opus-5-5"},
                {"type": "result", "is_error": True, "api_error_status": status, "result": reason, "num_turns": 1}
            ]), encoding="utf-8")
            result = mod.parse(file)
            assert result["category"] == category, result
            assert result["status"] == "failed"
            assert secret not in json.dumps(result)
            assert reason not in json.dumps(result)
        file.write_text("{not json", encoding="utf-8")
        assert mod.parse(file)["status"] == "unavailable"
        file.write_text(json.dumps([{"type":"result","is_error":False,"num_turns":5}]), encoding="utf-8")
        result=mod.parse(file)
        assert result["status"]=="completed"
        assert result["category"]=="unknown"
    print("Claude diagnostic privacy tests: PASS (offline; no Claude invoked)")


if __name__ == "__main__":
    check()
