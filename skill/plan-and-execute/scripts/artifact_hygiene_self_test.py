#!/usr/bin/env python3
"""Monitor artifact ownership, cleanup and clean skill-tree checks."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import resource_watch  # noqa: E402
import service_map  # noqa: E402

SKILL_ROOT = HERE.parent
REPO = SKILL_ROOT.parent.parent


def untracked_in_skill_tree() -> set[str]:
    out = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all", "--", "skill/plan-and-execute"],
        cwd=REPO, capture_output=True, text=True, check=False,
    ).stdout
    return {line[3:] for line in out.splitlines() if line.startswith("??") and "__pycache__" not in line}


def main() -> int:
    before = untracked_in_skill_tree()
    with tempfile.TemporaryDirectory() as raw:
        root = Path(raw)
        work = root / ".ai-work" / "resource-watch"
        work.mkdir(parents=True)
        service_map_file = root / ".ai-work" / "SERVICE_MAP.md"
        service_map_file.write_text("map", encoding="utf-8")

        def make(name: str, scope: str, owner: str, retention=None) -> Path:
            path = work / name
            path.write_text("x", encoding="utf-8")
            resource_watch.register_artifact(root, path, scope, owner, retention)
            return path

        task_a = make("a.jsonl", "task", "014")
        task_b = make("b.jsonl", "task", "015")
        plan_a = make("p.jsonl", "plan", "plan1")
        kept = make("k.jsonl", "task", "014", "keep")
        shared = make("s.jsonl", "project-shared", "")
        held = make("h.jsonl", "task", "014")

        resource_watch.cleanup_artifacts(root, "task", "014", held={str(held)})
        assert not task_a.exists(), "task artifact must be removed"
        assert task_b.exists() and plan_a.exists(), "other owners and scopes stay"
        assert kept.exists(), "retention keep must stay"
        assert held.exists(), "referenced artifact must stay"
        resource_watch.cleanup_artifacts(root, "project-shared", "")
        assert shared.exists(), "project-shared is never removed by cleanup"
        resource_watch.cleanup_artifacts(root, "plan", "plan1")
        assert not plan_a.exists()
        assert service_map_file.read_text(encoding="utf-8") == "map"

        try:
            resource_watch.register_artifact(root, root / "skill" / "plan-and-execute" / "x.log", "task", "1")
        except service_map.MapError:
            pass
        else:
            raise AssertionError("skill-tree artifact must be refused")

    after = untracked_in_skill_tree()
    assert after == before, f"new untracked files in skill tree: {sorted(after - before)}"
    print("artifact_hygiene_self_test: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
