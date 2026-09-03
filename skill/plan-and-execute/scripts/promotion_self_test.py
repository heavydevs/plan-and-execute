#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().with_name("promotectl.py")


def run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


with tempfile.TemporaryDirectory(prefix="pae-promotion-test-") as temporary:
    root = Path(temporary)
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
    (root / "app.txt").write_text("base\n", encoding="utf-8")
    subprocess.run(["git", "add", "app.txt"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True)
    (root / "app.txt").write_text("base\nchanged\n", encoding="utf-8")

    spec = {
        "schema_version": 1,
        "original_goal": "Implement export workflow.",
        "completed_work": ["Added repository query."],
        "validated_results": ["unit repository tests => passed"],
        "decisions": ["Keep stable ids."],
        "relevant_code": ["app.txt: repository placeholder"],
        "remaining_outcomes": ["Add endpoint.", "Add delivery worker."],
        "blockers": [],
        "risks": ["Large exports may be slow."],
        "context_pressure": {"used_percentage": 82, "source": "claude-statusline"},
    }
    spec_path = root / "promotion.json"
    spec_path.write_text(json.dumps(spec), encoding="utf-8")

    valid = run("validate", "--spec", str(spec_path), "--json")
    assert valid.returncode == 0, valid.stderr + valid.stdout
    assert json.loads(valid.stdout)["remaining_outcomes"] == 2

    output = root / "handoff.md"
    rendered = run(
        "render", "--repo-root", str(root), "--spec", str(spec_path),
        "--output", str(output), "--json"
    )
    assert rendered.returncode == 0, rendered.stderr + rendered.stdout
    text = output.read_text(encoding="utf-8")
    assert "ONLY the remaining outcomes" in text
    assert "not retroactive TODOs" in text
    assert "Add endpoint." in text and "Add delivery worker." in text
    assert "app.txt" in text
    assert "provider/model_tier/reasoning_effort" in text

    bad = dict(spec)
    bad["remaining_outcomes"] = []
    bad_path = root / "bad.json"
    bad_path.write_text(json.dumps(bad), encoding="utf-8")
    rejected = run("validate", "--spec", str(bad_path), "--json")
    assert rejected.returncode == 2

    bad_pressure = dict(spec)
    bad_pressure["context_pressure"] = {"used_percentage": 120, "source": "bad"}
    bad_pressure_path = root / "bad-pressure.json"
    bad_pressure_path.write_text(json.dumps(bad_pressure), encoding="utf-8")
    rejected_pressure = run("validate", "--spec", str(bad_pressure_path), "--json")
    assert rejected_pressure.returncode == 2

print("promotion self-test passed.")
