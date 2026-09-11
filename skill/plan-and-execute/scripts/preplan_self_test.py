#!/usr/bin/env python3
"""Deterministic tests for oversized-request routing and primary-plan scaffolding."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

import planctl
import preplanctl


def repo(base: Path) -> Path:
    path = base / "repo"
    path.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    return path


def test_small_request_routes_directly_to_final_plan() -> None:
    with tempfile.TemporaryDirectory() as temp:
        source = Path(temp) / "request.md"
        source.write_text("# Goal\n\nImplement one small validated endpoint.\n", encoding="utf-8")
        result = preplanctl.assess_source(source)
        assert result["route"] == "final_plan", result
        assert result["estimated_tokens"] < preplanctl.SOFT_TOKENS


def test_large_structured_request_routes_to_primary_plan_and_preserves_source() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        repository = repo(root)
        source = root / "large.md"
        sections = []
        for index in range(1, 41):
            sections.append(
                f"## {index}. Feature {index}\n\n"
                + (f"Requirement {index} must preserve contract-{index}. " * 260)
            )
        original = "\n\n".join(sections)
        source.write_text(original, encoding="utf-8")
        assessment = preplanctl.assess_source(source)
        assert assessment["route"] == "primary_plan", assessment
        package, metadata = preplanctl.create_package(repository, source, assessment)
        index = preplanctl.read_json(package / "SOURCE_INDEX.json")["fragments"]
        assert metadata["fragment_count"] == len(index) > 1
        for item in index:
            fragment_text = (package / item["path"]).read_text(encoding="utf-8")
            assert item["id"] in fragment_text
            assert item["source_text_sha256"] in fragment_text
        # Every distinctive requirement remains in at least one immutable fragment.
        joined = "\n".join((package / item["path"]).read_text(encoding="utf-8") for item in index)
        for index_no in (1, 7, 20, 40):
            assert f"Requirement {index_no} must preserve contract-{index_no}." in joined


def test_primary_plan_spec_is_valid_schema_v4_and_routes_stages_independently() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        repository = repo(root)
        source = root / "large.md"
        source.write_text(
            "\n\n".join(
                f"## {index}. Domain {index}\n\n" + (f"Domain rule {index}. " * 300)
                for index in range(1, 35)
            ),
            encoding="utf-8",
        )
        assessment = preplanctl.assess_source(source)
        package, metadata = preplanctl.create_package(repository, source, assessment)
        spec = preplanctl.make_primary_spec(repository, package, metadata)
        plan_dir = planctl.create_plan(repository, spec, ".ai-work", "primary-self-test")
        _, manifest = planctl.load_plan(plan_dir)
        assert not planctl.validate_plan(plan_dir, manifest)
        tiers = [task["model_tier"] for task in manifest["tasks"]]
        assert tiers[-3:] == ["standard", "strong", "economy"], tiers
        assert all(task["model_tier"] == "economy" for task in manifest["tasks"][:-3])
        assert manifest["cleanup_on_success"] is False
        assert all(not Path(path).is_absolute() for task in manifest["tasks"] for path in task["scope"]["expected_files"])


def main() -> int:
    test_small_request_routes_directly_to_final_plan()
    test_large_structured_request_routes_to_primary_plan_and_preserves_source()
    test_primary_plan_spec_is_valid_schema_v4_and_routes_stages_independently()
    print("All staged primary-planning self-tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
