#!/usr/bin/env python3
"""Create and validate a plan-local provider/model matrix.

The planner researches current provider catalogs/benchmarks, writes a compact JSON
spec, and this controller persists both a machine-readable MODEL_MATRIX.json and a
human-readable MODEL_MATRIX.md inside the durable plan workspace.
"""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import routingctl

CONFIG = "orchestrator.config.json"
PLAN_FILE = "PLAN.md"
SECTION_START = "<!-- portable-model-routing:start -->"
SECTION_END = "<!-- portable-model-routing:end -->"


class ModelMapError(RuntimeError):
    pass


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ModelMapError(f"Cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ModelMapError(f"Invalid JSON in {path}: {exc}") from exc


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def escape_cell(value: Any) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ").strip()


def render_markdown(matrix: dict[str, Any]) -> str:
    lines = [
        "# Model matrix\n",
        f"Researched at: `{matrix['researched_at']}`  ",
        f"Research mode: `{matrix['research_mode']}`\n",
        "Tasks persist only portable `F1`–`F4` model-family and `L1`–`L5` reasoning coordinates. "
        "This file records the concrete provider mapping current when the plan was created.\n",
        "| Provider | F1 | F2 | F3 | F4 | L1 | L2 | L3 | L4 | L5 |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for provider, entry in matrix["providers"].items():
        family_cells = [escape_cell(entry["families"][f"f{i}"]) for i in range(1, 5)]
        level_cells = [escape_cell(entry["levels"][f"l{i}"]) for i in range(1, 6)]
        lines.append("| " + " | ".join([provider, *family_cells, *level_cells]) + " |")
        details = [item for item in (entry.get("benchmark"), entry.get("pricing"), entry.get("notes")) if item]
        if details:
            lines.append(f"\n**{provider}:** " + " ".join(escape_cell(item) for item in details) + "\n")

    lines.append("\n## Sources\n")
    if matrix["sources"]:
        for source in matrix["sources"]:
            label = source["label"]
            url = source.get("url", "")
            lines.append(f"- [{label}]({url})" if url else f"- {label}")
    else:
        lines.append("- Built-in fallback catalog; refresh with live sources before consequential execution.")
    lines.append("")
    return "\n".join(lines)


def update_plan_reference(plan_dir: Path) -> None:
    plan_path = plan_dir / PLAN_FILE
    if not plan_path.is_file():
        return
    text = plan_path.read_text(encoding="utf-8")
    section = (
        f"{SECTION_START}\n"
        "## Portable model routing\n\n"
        "Executable TODOs use provider-neutral `F1`–`F4` model families and `L1`–`L5` reasoning levels. "
        f"Concrete current mappings are recorded in [{routingctl.MODEL_MATRIX_MD}]({routingctl.MODEL_MATRIX_MD}); "
        f"the runner reads `{routingctl.MODEL_MATRIX_JSON}` at execution time.\n"
        f"{SECTION_END}"
    )
    if SECTION_START in text and SECTION_END in text:
        before = text.split(SECTION_START, 1)[0].rstrip()
        after = text.split(SECTION_END, 1)[1].lstrip()
        updated = before + "\n\n" + section + ("\n\n" + after if after else "\n")
    else:
        updated = text.rstrip() + "\n\n" + section + "\n"
    atomic_write_text(plan_path, updated)


def update_config_reference(plan_dir: Path, matrix: dict[str, Any]) -> None:
    config_path = plan_dir / CONFIG
    if not config_path.is_file():
        raise ModelMapError(f"Plan config not found: {config_path}")
    config = read_json(config_path)
    if not isinstance(config, dict):
        raise ModelMapError(f"{CONFIG} must contain an object")
    policy = config.setdefault("routing_policy", {})
    if not isinstance(policy, dict):
        raise ModelMapError("routing_policy must be an object")
    policy.update(
        {
            "selection": "adaptive-portable",
            "model_matrix_file": routingctl.MODEL_MATRIX_JSON,
            "model_matrix_human_file": routingctl.MODEL_MATRIX_MD,
            "model_matrix_researched_at": matrix["researched_at"],
        }
    )
    atomic_write_json(config_path, config)


def write_matrix(plan_dir: Path, spec_path: Path) -> dict[str, Any]:
    if not plan_dir.is_dir():
        raise ModelMapError(f"Plan directory not found: {plan_dir}")
    try:
        matrix = routingctl.validate_model_matrix(read_json(spec_path))
    except routingctl.RoutingError as exc:
        raise ModelMapError(str(exc)) from exc
    atomic_write_json(plan_dir / routingctl.MODEL_MATRIX_JSON, matrix)
    atomic_write_text(plan_dir / routingctl.MODEL_MATRIX_MD, render_markdown(matrix))
    update_config_reference(plan_dir, matrix)
    update_plan_reference(plan_dir)
    return matrix


def validate_plan_matrix(plan_dir: Path) -> dict[str, Any]:
    try:
        matrix = routingctl.load_model_matrix(plan_dir)
    except routingctl.RoutingError as exc:
        raise ModelMapError(str(exc)) from exc
    if matrix is None:
        raise ModelMapError(f"{routingctl.MODEL_MATRIX_JSON} is missing")
    md_path = plan_dir / routingctl.MODEL_MATRIX_MD
    if not md_path.is_file():
        raise ModelMapError(f"{routingctl.MODEL_MATRIX_MD} is missing")
    if "| Provider | F1 | F2 | F3 | F4 | L1 | L2 | L3 | L4 | L5 |" not in md_path.read_text(encoding="utf-8"):
        raise ModelMapError(f"{routingctl.MODEL_MATRIX_MD} does not contain the portable route table")
    return matrix


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    write = sub.add_parser("write", help="Persist a researched model matrix into an existing plan")
    write.add_argument("--plan", required=True)
    write.add_argument("--spec", required=True)
    validate = sub.add_parser("validate", help="Validate the plan-local model matrix")
    validate.add_argument("--plan", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "write":
            matrix = write_matrix(Path(args.plan).resolve(), Path(args.spec).resolve())
        else:
            matrix = validate_plan_matrix(Path(args.plan).resolve())
    except ModelMapError as exc:
        print(f"modelmapctl: {exc}", file=__import__("sys").stderr)
        return 2
    print(json.dumps({"ok": True, "researched_at": matrix["researched_at"], "providers": sorted(matrix["providers"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
