#!/usr/bin/env python3
"""Create a compact, durable handoff when direct work is promoted to orchestration."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
MAX_GOAL_CHARS = 1600
MAX_LIST_ITEMS = 24
MAX_TOTAL_ITEMS = 48
MAX_HANDOFF_CHARS = 24000
MAX_ITEM_CHARS = 420
MAX_SOURCE_CHARS = 120
MAX_GIT_LINES = 80
MAX_GIT_CHARS = 6000


class PromotionError(RuntimeError):
    pass


def _text(value: Any, field: str, maximum: int = MAX_ITEM_CHARS) -> str:
    text = str(value or "").strip()
    if not text:
        raise PromotionError(f"{field} must be non-empty")
    if len(text) > maximum:
        raise PromotionError(f"{field} exceeds {maximum} characters")
    return text


def _list(value: Any, field: str, *, required: bool = False) -> list[str]:
    if value is None:
        value = []
    if not isinstance(value, list):
        raise PromotionError(f"{field} must be a list")
    if len(value) > MAX_LIST_ITEMS:
        raise PromotionError(f"{field} exceeds {MAX_LIST_ITEMS} items")
    items = [_text(item, f"{field}[{index}]") for index, item in enumerate(value)]
    if required and not items:
        raise PromotionError(f"{field} must contain at least one item")
    if len({item.casefold() for item in items}) != len(items):
        raise PromotionError(f"{field} contains duplicate items")
    return items


def normalize_spec(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise PromotionError("promotion spec must be a JSON object")
    version = raw.get("schema_version", SCHEMA_VERSION)
    if version != SCHEMA_VERSION:
        raise PromotionError(f"unsupported schema_version: {version}")

    pressure_raw = raw.get("context_pressure")
    pressure = None
    if pressure_raw is not None:
        if not isinstance(pressure_raw, dict):
            raise PromotionError("context_pressure must be an object")
        used = pressure_raw.get("used_percentage")
        if used is not None:
            if isinstance(used, bool) or not isinstance(used, (int, float)):
                raise PromotionError("context_pressure.used_percentage must be numeric")
            if used < 0 or used > 100:
                raise PromotionError("context_pressure.used_percentage must be between 0 and 100")
        source = pressure_raw.get("source")
        pressure = {
            "used_percentage": used,
            "source": _text(source, "context_pressure.source", MAX_SOURCE_CHARS) if source else None,
        }
        if used is None and pressure["source"] is None:
            pressure = None

    normalized = {
        "schema_version": SCHEMA_VERSION,
        "original_goal": _text(raw.get("original_goal"), "original_goal", MAX_GOAL_CHARS),
        "completed_work": _list(raw.get("completed_work"), "completed_work"),
        "validated_results": _list(raw.get("validated_results"), "validated_results"),
        "decisions": _list(raw.get("decisions"), "decisions"),
        "relevant_code": _list(raw.get("relevant_code"), "relevant_code"),
        "remaining_outcomes": _list(raw.get("remaining_outcomes"), "remaining_outcomes", required=True),
        "blockers": _list(raw.get("blockers"), "blockers"),
        "risks": _list(raw.get("risks"), "risks"),
        "context_pressure": pressure,
    }
    total_items = sum(
        len(normalized[field])
        for field in (
            "completed_work", "validated_results", "decisions", "relevant_code",
            "remaining_outcomes", "blockers", "risks"
        )
    )
    if total_items > MAX_TOTAL_ITEMS:
        raise PromotionError(f"promotion handoff exceeds {MAX_TOTAL_ITEMS} total list items")
    return normalized


def load_spec(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PromotionError(f"spec not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise PromotionError(f"invalid JSON in {path}: {exc}") from exc
    return normalize_spec(raw)


def _bounded(text: str) -> str:
    lines = text.splitlines()[:MAX_GIT_LINES]
    result = "\n".join(line[:300] for line in lines).strip()
    if len(result) > MAX_GIT_CHARS:
        result = result[:MAX_GIT_CHARS].rstrip() + "\n..."
    return result


def _git(repo_root: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    if result.returncode != 0:
        return ""
    return _bounded(result.stdout)


def git_snapshot(repo_root: Path) -> dict[str, str]:
    return {
        "branch": _git(repo_root, "branch", "--show-current"),
        "head": _git(repo_root, "rev-parse", "--short=12", "HEAD"),
        "status": _git(repo_root, "status", "--short"),
        "diff_stat": _git(repo_root, "diff", "--stat"),
        "cached_diff_stat": _git(repo_root, "diff", "--cached", "--stat"),
    }


def _section(title: str, items: list[str]) -> str:
    if not items:
        return f"## {title}\n\n- None recorded.\n"
    return f"## {title}\n\n" + "\n".join(f"- {item}" for item in items) + "\n"


def render_markdown(spec: dict[str, Any], snapshot: dict[str, str]) -> str:
    parts = [
        "# Plan-and-execute promotion handoff\n",
        "## Execution directive\n\n"
        "Plan and execute ONLY the remaining outcomes below. Completed work, validated results, decisions, "
        "relevant code, and repository state are evidence/current context, not retroactive TODOs. Preserve existing "
        "implementation changes unless a remaining outcome requires modifying them. Re-enter adaptive study only "
        "to the depth that can materially change the remaining plan.\n",
        f"## Original goal\n\n{spec['original_goal']}\n",
        _section("Completed work", spec["completed_work"]),
        _section("Validated results", spec["validated_results"]),
        _section("Active decisions and invariants", spec["decisions"]),
        _section("Relevant code", spec["relevant_code"]),
        _section("Remaining outcomes", spec["remaining_outcomes"]),
        _section("Blockers", spec["blockers"]),
        _section("Risks", spec["risks"]),
    ]

    pressure = spec.get("context_pressure")
    if pressure:
        used = pressure.get("used_percentage")
        source = pressure.get("source") or "host"
        detail = f"{used:g}% from {source}" if used is not None else f"reported by {source}"
        parts.append(
            "## Context pressure at promotion\n\n"
            f"- {detail}. This is a promotion signal only, not a requirement to split otherwise cohesive work.\n"
        )

    repo_lines = []
    if snapshot.get("branch"):
        repo_lines.append(f"Branch: `{snapshot['branch']}`")
    if snapshot.get("head"):
        repo_lines.append(f"HEAD: `{snapshot['head']}`")
    for key, label in (
        ("status", "Working tree status"),
        ("diff_stat", "Unstaged diff stat"),
        ("cached_diff_stat", "Staged diff stat"),
    ):
        value = snapshot.get(key, "")
        if value:
            repo_lines.append(f"{label}:\n```text\n{value}\n```")
    if not repo_lines:
        repo_lines.append("Git metadata unavailable; inspect the repository directly before planning.")
    parts.append("## Repository snapshot\n\n" + "\n\n".join(repo_lines) + "\n")

    parts.append(
        "## Planning constraint\n\n"
        "Create the durable TODO checklist, task-definition files, per-TODO provider/model_tier/reasoning_effort, "
        "resumable subtasks, and deterministic validations for the remaining outcomes only. After activation, "
        "normal lifecycle recovery must allow another compatible provider to resume without this chat history.\n"
    )
    rendered = "\n".join(parts).rstrip() + "\n"
    if len(rendered) > MAX_HANDOFF_CHARS:
        raise PromotionError(
            f"rendered promotion handoff exceeds {MAX_HANDOFF_CHARS} characters; compact the snapshot"
        )
    return rendered


def write_atomic(output: Path, text: str) -> None:
    output = output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and output.is_symlink():
        raise PromotionError(f"refusing to replace symlink: {output}")
    fd, temporary = tempfile.mkstemp(prefix=f".{output.name}.", dir=str(output.parent), text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(temporary, output)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def command_validate(args: argparse.Namespace) -> dict[str, Any]:
    spec = load_spec(Path(args.spec))
    return {
        "status": "valid",
        "schema_version": spec["schema_version"],
        "remaining_outcomes": len(spec["remaining_outcomes"]),
    }


def command_render(args: argparse.Namespace) -> dict[str, Any]:
    spec = load_spec(Path(args.spec))
    repo_root = Path(args.repo_root).expanduser().resolve()
    if not repo_root.is_dir():
        raise PromotionError(f"repo root is not a directory: {repo_root}")
    snapshot = {} if args.no_git else git_snapshot(repo_root)
    text = render_markdown(spec, snapshot)
    if args.output:
        output = Path(args.output)
    else:
        fd, temporary = tempfile.mkstemp(prefix="pae-promotion-request-", suffix=".md")
        os.close(fd)
        output = Path(temporary)
    write_atomic(output, text)
    return {
        "status": "rendered",
        "path": str(output.expanduser().resolve()),
        "remaining_outcomes": len(spec["remaining_outcomes"]),
        "git_evidence": any(snapshot.values()),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate")
    validate.add_argument("--spec", required=True)
    validate.add_argument("--json", action="store_true")

    render = subparsers.add_parser("render")
    render.add_argument("--repo-root", default=".")
    render.add_argument("--spec", required=True)
    render.add_argument("--output")
    render.add_argument("--no-git", action="store_true")
    render.add_argument("--json", action="store_true")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "validate":
            result = command_validate(args)
        else:
            result = command_render(args)
    except PromotionError as exc:
        if getattr(args, "json", False):
            print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False))
        else:
            print(f"Error: {exc}", file=sys.stderr)
        return 2
    if getattr(args, "json", False):
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result["status"] == "valid":
            print(f"Promotion spec valid ({result['remaining_outcomes']} remaining outcomes).")
        else:
            print(result["path"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
