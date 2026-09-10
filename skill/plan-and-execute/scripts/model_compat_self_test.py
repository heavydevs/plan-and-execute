#!/usr/bin/env python3
"""Self-tests for provider-scoped daily compatibility caching and refresh."""
from __future__ import annotations

from datetime import datetime, timedelta
import json
import os
import subprocess
import tempfile
from pathlib import Path

import model_compatctl
import routingctl
from model_routing_self_test import compatibility, portable_spec


def test_daily_cache_is_independent_per_provider() -> None:
    with tempfile.TemporaryDirectory() as temp:
        old_cache = os.environ.get(routingctl.MODEL_CACHE_DIR_ENV)
        os.environ[routingctl.MODEL_CACHE_DIR_ENV] = str(Path(temp) / "cache")
        try:
            assert model_compatctl.cache_status("codex")["status"] == "missing"
            assert model_compatctl.cache_status("claude")["status"] == "missing"

            codex_spec = Path(temp) / "codex.json"
            codex_spec.write_text(json.dumps(compatibility("codex")), encoding="utf-8")
            codex_path = model_compatctl.cache_write("codex", codex_spec)
            assert codex_path.name == "codex.json"
            codex_status = model_compatctl.cache_status("codex")
            assert codex_status["status"] == "fresh" and codex_status["fresh"]
            assert model_compatctl.cache_status("claude")["status"] == "missing"
            assert set(model_compatctl.cache_read("codex")["providers"]) == {"codex"}

            claude_spec = Path(temp) / "claude.json"
            claude_spec.write_text(json.dumps(compatibility("claude")), encoding="utf-8")
            claude_path = model_compatctl.cache_write("claude", claude_spec)
            assert claude_path.name == "claude.json"
            assert model_compatctl.cache_status("codex")["status"] == "fresh"
            assert model_compatctl.cache_status("claude")["status"] == "fresh"

            try:
                model_compatctl.cache_write("claude", codex_spec)
            except model_compatctl.CompatCtlError as exc:
                assert "exactly that provider" in str(exc)
            else:
                raise AssertionError("Provider cache must not accept another provider's binding")
        finally:
            if old_cache is None:
                os.environ.pop(routingctl.MODEL_CACHE_DIR_ENV, None)
            else:
                os.environ[routingctl.MODEL_CACHE_DIR_ENV] = old_cache


def test_stale_cache_is_detected_by_local_calendar_day() -> None:
    with tempfile.TemporaryDirectory() as temp:
        old_cache = os.environ.get(routingctl.MODEL_CACHE_DIR_ENV)
        os.environ[routingctl.MODEL_CACHE_DIR_ENV] = str(Path(temp) / "cache")
        try:
            stale_at = (datetime.now().astimezone() - timedelta(days=1)).isoformat(timespec="seconds")
            stale = routingctl.normalize_compatibility(compatibility("qwen", stale_at))
            path = routingctl.provider_cache_path("qwen")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(stale), encoding="utf-8")
            status = model_compatctl.cache_status("qwen")
            assert status["status"] == "stale"
            assert not status["fresh"]
            try:
                model_compatctl.cache_read("qwen")
            except model_compatctl.CompatCtlError as exc:
                assert "No fresh daily cache" in str(exc)
            else:
                raise AssertionError("Yesterday's provider cache must not be reused")
        finally:
            if old_cache is None:
                os.environ.pop(routingctl.MODEL_CACHE_DIR_ENV, None)
            else:
                os.environ[routingctl.MODEL_CACHE_DIR_ENV] = old_cache


def test_refresh_from_another_provider_cache_preserves_todo_fl() -> None:
    with tempfile.TemporaryDirectory() as temp:
        old_cache = os.environ.get(routingctl.MODEL_CACHE_DIR_ENV)
        os.environ[routingctl.MODEL_CACHE_DIR_ENV] = str(Path(temp) / "cache")
        try:
            base = Path(temp)
            repo = base / "repo"
            repo.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            plan_dir = model_compatctl.planctl.create_plan(
                repo, portable_spec("codex"), ".ai-work", "compat-refresh-test"
            )
            _path, before = model_compatctl.planctl.load_plan(plan_dir)
            before_task = json.loads(json.dumps(before["tasks"][0]))
            assert before["model_compatibility_providers"] == ["codex"]

            qwen = compatibility("qwen")
            qwen["providers"]["qwen"]["families"]["F2"]["model"] = "qwen-f2-new-current"
            qwen_spec = base / "qwen-fresh.json"
            qwen_spec.write_text(json.dumps(qwen), encoding="utf-8")
            model_compatctl.cache_write("qwen", qwen_spec)

            model_compatctl.refresh_plan(plan_dir, provider="qwen")
            _path, after = model_compatctl.planctl.load_plan(plan_dir)
            after_task = after["tasks"][0]
            assert after_task["model_family"] == before_task["model_family"] == "F2"
            assert after_task["model_level"] == before_task["model_level"] == "L2"
            assert after_task["objective"] == before_task["objective"]
            assert after["model_compatibility_providers"] == ["qwen"]

            binding = json.loads(
                (plan_dir / "MODEL_COMPATIBILITY.json").read_text(encoding="utf-8")
            )
            assert set(binding["providers"]) == {"qwen"}
            assert binding["providers"]["qwen"]["families"]["F2"]["model"] == "qwen-f2-new-current"
            rendered = (plan_dir / "MODEL_COMPATIBILITY.md").read_text(encoding="utf-8")
            assert "qwen-f2-new-current" in rendered
            assert any(
                event.get("type") == "model_compatibility_refreshed"
                and event.get("providers") == ["qwen"]
                for event in after["events"]
            )
            assert not model_compatctl.planctl.validate_plan(plan_dir, after)
        finally:
            if old_cache is None:
                os.environ.pop(routingctl.MODEL_CACHE_DIR_ENV, None)
            else:
                os.environ[routingctl.MODEL_CACHE_DIR_ENV] = old_cache


def main() -> int:
    test_daily_cache_is_independent_per_provider()
    test_stale_cache_is_detected_by_local_calendar_day()
    test_refresh_from_another_provider_cache_preserves_todo_fl()
    print("All model compatibility cache self-tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
