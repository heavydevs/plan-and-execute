#!/usr/bin/env python3
"""Self-test for guarded portable compatibility refreshes."""
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

import model_compatctl
from model_routing_self_test import compatibility, portable_spec


def test_refresh_changes_only_binding() -> None:
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        repo = base / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        plan_dir = model_compatctl.planctl.create_plan(
            repo, portable_spec(), ".ai-work", "compat-refresh-test"
        )
        _path, before = model_compatctl.planctl.load_plan(plan_dir)
        before_task = json.loads(json.dumps(before["tasks"][0]))

        refreshed = compatibility()
        refreshed["generated_at"] = "2026-09-10T00:30:00-03:00"
        refreshed["discovery"] = "Live provider model information was rechecked before switching provider."
        for provider in refreshed["providers"].values():
            provider["checked_at"] = refreshed["generated_at"]
        refreshed["providers"]["qwen"]["families"]["F2"]["model"] = "qwen-f2-new-current"
        spec_path = base / "compatibility.json"
        spec_path.write_text(json.dumps(refreshed), encoding="utf-8")

        model_compatctl.refresh_plan(plan_dir, spec_path)
        _path, after = model_compatctl.planctl.load_plan(plan_dir)
        after_task = after["tasks"][0]
        assert after_task["model_family"] == before_task["model_family"] == "F2"
        assert after_task["model_level"] == before_task["model_level"] == "L2"
        assert after_task["objective"] == before_task["objective"]
        assert after["model_compatibility_generated_at"] == refreshed["generated_at"]

        binding = json.loads(
            (plan_dir / "MODEL_COMPATIBILITY.json").read_text(encoding="utf-8")
        )
        assert binding["providers"]["qwen"]["families"]["F2"]["model"] == "qwen-f2-new-current"
        rendered = (plan_dir / "MODEL_COMPATIBILITY.md").read_text(encoding="utf-8")
        assert "qwen-f2-new-current" in rendered
        assert any(event.get("type") == "model_compatibility_refreshed" for event in after["events"])
        assert not model_compatctl.planctl.validate_plan(plan_dir, after)


def main() -> int:
    test_refresh_changes_only_binding()
    print("All model compatibility refresh self-tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
