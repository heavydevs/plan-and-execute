#!/usr/bin/env python3
"""Deterministic tests for oversized-request routing and primary-plan scaffolding."""

from __future__ import annotations

import io
import subprocess
import tempfile
from argparse import Namespace
from contextlib import redirect_stdout
from pathlib import Path

import lifecyclectl
import planctl
import preplanctl


def repo(base: Path) -> Path:
    path = base / "repo"
    path.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    return path


def large_source(path: Path, sections: int = 40) -> str:
    content = "\n\n".join(
        f"## {index}. Feature {index}\n\n"
        + (f"Requirement {index} must preserve contract-{index}. " * 260)
        for index in range(1, sections + 1)
    )
    path.write_text(content, encoding="utf-8")
    return content


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
        original = large_source(source)
        assessment = preplanctl.assess_source(source)
        assert assessment["route"] == "primary_plan", assessment
        package, metadata = preplanctl.create_package(repository, source, assessment)
        index = preplanctl.read_json(package / "SOURCE_INDEX.json")["fragments"]
        assert metadata["fragment_count"] == len(index) > 1
        for item in index:
            fragment_text = (package / item["path"]).read_text(encoding="utf-8")
            assert item["id"] in fragment_text
            assert item["source_text_sha256"] in fragment_text
        joined = "\n".join((package / item["path"]).read_text(encoding="utf-8") for item in index)
        for index_no in (1, 7, 20, 40):
            assert f"Requirement {index_no} must preserve contract-{index_no}." in joined
        assert original.startswith("## 1. Feature 1")


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


def test_prepare_primary_plan_is_immediately_discoverable_by_lifecycle_resume() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        repository = repo(root)
        source = root / "large.md"
        large_source(source)
        args = Namespace(
            repo_root=str(repository),
            work_root=planctl.WORK_ROOT_DEFAULT,
            file=str(source),
            force=True,
            soft_tokens=preplanctl.SOFT_TOKENS,
            hard_tokens=preplanctl.HARD_TOKENS,
            breadth_token_floor=preplanctl.BREADTH_TOKEN_FLOOR,
            breadth_headings=preplanctl.BREADTH_HEADINGS,
            package_id="resume-test",
            target_fragment_tokens=preplanctl.TARGET_FRAGMENT_TOKENS,
            max_fragment_tokens=preplanctl.MAX_FRAGMENT_TOKENS,
        )
        with redirect_stdout(io.StringIO()):
            preplanctl.command_prepare(args)
        discovered = lifecyclectl.discover_active(repository)
        assert discovered is not None
        plan_dir, manifest = discovered
        assert manifest["plan_id"] == "primary-resume-test"
        assert plan_dir.name == "primary-resume-test"
        assert lifecyclectl.active_path(repository).is_file()
        record = lifecyclectl.read_json_file(lifecyclectl.active_path(repository))
        assert record and record["plan_id"] == "primary-resume-test"


def main() -> int:
    test_small_request_routes_directly_to_final_plan()
    test_large_structured_request_routes_to_primary_plan_and_preserves_source()
    test_primary_plan_spec_is_valid_schema_v4_and_routes_stages_independently()
    test_prepare_primary_plan_is_immediately_discoverable_by_lifecycle_resume()
    print("All staged primary-planning self-tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
