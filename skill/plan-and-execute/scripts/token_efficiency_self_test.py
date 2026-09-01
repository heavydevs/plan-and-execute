#!/usr/bin/env python3
"""Regression tests for lean instruction loading and safe successful cleanup."""

from __future__ import annotations

import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent

import lifecycle_self_test  # noqa: E402
import planctl  # noqa: E402


def test_instruction_surface_is_bounded() -> None:
    skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    agent_text = (SKILL_DIR / "agents" / "openai.yaml").read_text(encoding="utf-8")
    token_reference = SKILL_DIR / "references" / "TOKEN_EFFICIENCY.md"

    # Keep the always-loaded control plane substantially smaller than the former
    # ~25 KB entrypoint plus ~2.3 KB duplicated default prompt.
    assert len(skill_text) <= 14000, len(skill_text)
    assert len(agent_text) <= 1400, len(agent_text)
    assert token_reference.is_file()
    assert "load detailed references only for the current phase" in agent_text
    assert "TOKEN_EFFICIENCY.md" in skill_text


def test_cleanup_deletes_plan_only_and_preserves_product() -> None:
    with tempfile.TemporaryDirectory() as temp:
        repo = lifecycle_self_test.make_repo(Path(temp))
        plan_dir = lifecycle_self_test.create_plan(repo, "Successful cleanup regression")
        implementation = repo / "implemented.txt"
        implementation.write_text("implemented\n", encoding="utf-8")

        lifecycle_self_test.complete_sample_plan(plan_dir)
        _, manifest = planctl.load_plan(plan_dir)
        planctl.cleanup_plan(plan_dir, manifest)

        assert not plan_dir.exists(), "Successful cleanup must delete the plan workspace"
        assert implementation.is_file(), "Cleanup must preserve implementation output"
        assert implementation.read_text(encoding="utf-8") == "implemented\n"


def main() -> int:
    test_instruction_surface_is_bounded()
    test_cleanup_deletes_plan_only_and_preserves_product()
    print("All token-efficiency and cleanup self-tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
