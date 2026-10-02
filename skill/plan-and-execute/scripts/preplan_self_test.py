#!/usr/bin/env python3
"""Deterministic tests for oversized-request routing and primary-plan scaffolding."""

from __future__ import annotations

import io
import shutil
import subprocess
import sys
import tempfile
from argparse import Namespace
from contextlib import ExitStack, redirect_stdout
from pathlib import Path

import lifecyclectl
import planctl
import preplanctl


def extended_path(path: Path) -> Path:
    """Windows paths past MAX_PATH need the `\\\\?\\` prefix when LongPathsEnabled=0."""
    return Path("\\\\?\\" + str(path.resolve())) if sys.platform == "win32" else path


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


def test_deep_primary_plan_uses_relative_package_guidance_and_validates_by_cli() -> None:
    with tempfile.TemporaryDirectory() as temp, ExitStack() as cleanup:
        root = Path(temp)
        # Runs before TemporaryDirectory cleanup, which cannot remove >260-char
        # paths through an unprefixed root.
        cleanup.callback(shutil.rmtree, extended_path(root), ignore_errors=True)
        repository = root.joinpath(*(["deep_repository_path"] * 12))
        # Windows CreateProcess rejects cwd > MAX_PATH even with long paths on.
        # Keep only the process cwd short; package/plan paths still exceed 260.
        if sys.platform == "win32":
            while len(str(repository)) > 230 and repository != root:
                repository = repository.parent
        repository.mkdir(parents=True)
        subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
        # Process cwd stays unprefixed; file operations use the extended root.
        process_cwd, repository = repository, extended_path(repository)
        source = root / "large.md"
        large_source(source)
        package_id = "long-primary-package-identifier-for-guidance-validation-" * 2
        args = Namespace(
            repo_root=str(repository),
            work_root=planctl.WORK_ROOT_DEFAULT,
            file=str(source),
            force=True,
            soft_tokens=preplanctl.SOFT_TOKENS,
            hard_tokens=preplanctl.HARD_TOKENS,
            breadth_token_floor=preplanctl.BREADTH_TOKEN_FLOOR,
            breadth_headings=preplanctl.BREADTH_HEADINGS,
            package_id=package_id,
            target_fragment_tokens=preplanctl.TARGET_FRAGMENT_TOKENS,
            max_fragment_tokens=preplanctl.MAX_FRAGMENT_TOKENS,
        )
        with redirect_stdout(io.StringIO()):
            preplanctl.command_prepare(args)
        package = repository / preplanctl.PREPARED_ROOT / package_id
        assert len(str(package / "package.json")) > 260
        plan_dir = Path(preplanctl.read_json(package / "package.json")["primary_plan"])
        assert plan_dir.is_dir()
        assert plan_dir.name != f"primary-{package_id}"
        result = subprocess.run(
            [
                sys.executable,
                str(Path(__file__).with_name("planctl_concise.py")),
                "validate",
                "--plan",
                str(plan_dir),
            ],
            cwd=process_cwd,
            check=True,
            capture_output=True,
            text=True,
        )
        assert "VALID" in result.stdout
        manifest = preplanctl.read_json(plan_dir / "manifest.json")
        package_locator = f"PACKAGE_ROOT=.ai-work/prepared/{package_id}"
        assert manifest["execution_context"]["global"]["items"][0]["text"] == package_locator
        context_file = plan_dir / manifest["execution_context"]["global"]["file"]
        assert package_locator in context_file.read_text(encoding="utf-8")
        for task in manifest["tasks"]:
            guidance = "\n".join(task["implementation_guidance"])
            assert str(repository) not in guidance
            assert str(repository / ".ai-work" / "prepared" / package_id) not in guidance
            assert "$PACKAGE_ROOT" in guidance


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


def prepare_args(repository: Path, source: Path, package_id: str, **overrides: int) -> Namespace:
    values = {
        "repo_root": str(repository),
        "work_root": planctl.WORK_ROOT_DEFAULT,
        "file": str(source),
        "force": True,
        "soft_tokens": preplanctl.SOFT_TOKENS,
        "hard_tokens": preplanctl.HARD_TOKENS,
        "breadth_token_floor": preplanctl.BREADTH_TOKEN_FLOOR,
        "breadth_headings": preplanctl.BREADTH_HEADINGS,
        "package_id": package_id,
        "target_fragment_tokens": preplanctl.TARGET_FRAGMENT_TOKENS,
        "max_fragment_tokens": preplanctl.MAX_FRAGMENT_TOKENS,
    }
    values.update(overrides)
    return Namespace(**values)


def test_full_batches_of_long_heading_fragments_fit_guidance_budget() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        repository = repo(root)
        source = root / "large.md"
        source.write_text(
            "\n\n".join(
                f"## Parte {index}: requisitos detalhados de roteamento portavel do catalogo dinamico de provedores\n\n"
                + (f"Rule {index} keeps the provider catalog contract. " * 150)
                for index in range(1, 25)
            ),
            encoding="utf-8",
        )
        args = prepare_args(repository, source, "long-headings", target_fragment_tokens=1500, max_fragment_tokens=2000)
        with redirect_stdout(io.StringIO()):
            preplanctl.command_prepare(args)
        package = repository / preplanctl.PREPARED_ROOT / "long-headings"
        manifest = preplanctl.read_json(Path(preplanctl.read_json(package / "package.json")["primary_plan"]) / "manifest.json")
        digests = manifest["tasks"][:-3]
        assert any(len(task["scope"]["expected_files"]) == 1 and "F004" in " ".join(task["implementation_guidance"]) for task in digests)
        assert max(len(text) for task in manifest["tasks"] for text in task["implementation_guidance"]) <= 240


def test_failed_primary_plan_creation_removes_package_so_prepare_can_retry() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        repository = repo(root)
        source = root / "large.md"
        large_source(source)
        args = prepare_args(repository, source, "retry-test")
        package = repository / preplanctl.PREPARED_ROOT / "retry-test"
        original = preplanctl.create_primary_plan

        def failing(*_: object) -> Path:
            raise preplanctl.PreplanError("simulated plan creation failure")

        preplanctl.create_primary_plan = failing
        try:
            try:
                preplanctl.command_prepare(args)
            except preplanctl.PreplanError:
                pass
            else:
                raise AssertionError("prepare should propagate plan creation failure")
        finally:
            preplanctl.create_primary_plan = original
        assert not package.exists()
        with redirect_stdout(io.StringIO()):
            preplanctl.command_prepare(args)
        assert preplanctl.read_json(package / "package.json")["state"] == "primary_plan_created"


def test_repetitive_large_request_does_not_route_by_size_alone() -> None:
    with tempfile.TemporaryDirectory() as temp:
        source = Path(temp) / "log.md"
        source.write_text((chr(10) * 2).join(["ERROR connection retry failed for worker pool " * 40] * 400), encoding="utf-8")
        result = preplanctl.assess_source(source)
        assert result["raw_estimated_tokens"] >= preplanctl.HARD_TOKENS, result
        assert result["route"] == "final_plan", result


def test_dependency_dense_request_routes_to_primary_plan() -> None:
    with tempfile.TemporaryDirectory() as temp:
        source = Path(temp) / "deps.md"
        source.write_text(
            (chr(10) * 2).join(f"Rule {i} depends on rule {i - 1}. " + f"Detail {i} " * 150 for i in range(1, 60)),
            encoding="utf-8",
        )
        result = preplanctl.assess_source(source)
        assert result["route"] == "primary_plan", result
        assert any(r.startswith("dependency_density") for r in result["reasons"]), result


def test_batches_follow_top_level_section_cohesion() -> None:
    index = [
        {"id": f"F{n}", "estimated_tokens": 3000, "heading_path": [f"Part {1 if n <= 2 else 2}"]}
        for n in range(1, 5)
    ]
    batches = preplanctl.batch_fragments(index)
    assert [[f["id"] for f in b] for b in batches] == [["F1", "F2"], ["F3", "F4"]], batches


def main() -> int:
    test_small_request_routes_directly_to_final_plan()
    test_large_structured_request_routes_to_primary_plan_and_preserves_source()
    test_primary_plan_spec_is_valid_schema_v4_and_routes_stages_independently()
    test_deep_primary_plan_uses_relative_package_guidance_and_validates_by_cli()
    test_prepare_primary_plan_is_immediately_discoverable_by_lifecycle_resume()
    test_full_batches_of_long_heading_fragments_fit_guidance_budget()
    test_failed_primary_plan_creation_removes_package_so_prepare_can_retry()
    test_repetitive_large_request_does_not_route_by_size_alone()
    test_dependency_dense_request_routes_to_primary_plan()
    test_batches_follow_top_level_section_cohesion()
    print("All staged primary-planning self-tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
