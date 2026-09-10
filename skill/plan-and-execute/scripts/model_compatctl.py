#!/usr/bin/env python3
"""Validate, render, and refresh portable F/L model compatibility bindings."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from artifact_contract import install_plan_contract  # noqa: E402
import routingctl  # noqa: E402

planctl = routingctl.install_current_model_catalog(install_plan_contract())


class CompatCtlError(RuntimeError):
    pass


def read_json(path: str | Path) -> Any:
    source = Path(path).expanduser()
    try:
        return json.loads(source.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CompatCtlError(f"File not found: {source}") from exc
    except json.JSONDecodeError as exc:
        raise CompatCtlError(f"Invalid JSON in {source}: {exc}") from exc


def extract_compatibility(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict) and "model_compatibility" in raw:
        raw = raw["model_compatibility"]
    try:
        return routingctl.normalize_compatibility(raw)
    except routingctl.RoutingError as exc:
        raise CompatCtlError(str(exc)) from exc


def validate_spec(path: str | Path) -> dict[str, Any]:
    return extract_compatibility(read_json(path))


def refresh_plan(plan_arg: str | Path, spec_path: str | Path) -> Path:
    plan_dir, manifest = planctl.load_plan(plan_arg)
    if manifest.get("routing_schema") != routingctl.PORTABLE_ROUTING_VERSION:
        raise CompatCtlError(
            "Compatibility refresh is only valid for portable F/L plans; "
            "legacy provider/tier plans remain unchanged"
        )
    compatibility = validate_spec(spec_path)

    planctl.atomic_write_json(
        plan_dir / routingctl.MODEL_COMPATIBILITY_JSON,
        compatibility,
    )
    planctl.atomic_write_text(
        plan_dir / routingctl.MODEL_COMPATIBILITY_MD,
        routingctl.render_compatibility_markdown(compatibility),
    )
    manifest["model_compatibility_file"] = routingctl.MODEL_COMPATIBILITY_MD
    manifest["model_compatibility_data_file"] = routingctl.MODEL_COMPATIBILITY_JSON
    manifest["model_compatibility_generated_at"] = compatibility["generated_at"]
    planctl.append_event(
        manifest,
        "model_compatibility_refreshed",
        generated_at=compatibility["generated_at"],
        providers=list(routingctl.PORTABLE_PROVIDERS),
    )
    planctl.save_manifest(plan_dir, manifest)
    errors = planctl.validate_plan(plan_dir, manifest)
    if errors:
        raise CompatCtlError(
            "Plan failed validation after compatibility refresh:\n- "
            + "\n- ".join(errors)
        )
    return plan_dir


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        description="Manage portable plan model compatibility without changing TODO F/L requirements."
    )
    sub = root.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="Validate a compatibility JSON/spec file")
    validate.add_argument("--spec", required=True)
    validate.add_argument("--json", action="store_true")

    render = sub.add_parser("render", help="Render a compatibility JSON/spec file as Markdown")
    render.add_argument("--spec", required=True)
    render.add_argument("--output")

    refresh = sub.add_parser(
        "refresh",
        help="Replace only a portable plan's concrete model bindings after live discovery",
    )
    refresh.add_argument("--plan", required=True)
    refresh.add_argument("--spec", required=True)
    refresh.add_argument("--json", action="store_true")
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "validate":
            compatibility = validate_spec(args.spec)
            if args.json:
                print(json.dumps(compatibility, ensure_ascii=False, indent=2))
            else:
                print("Compatibility spec is valid.")
            return 0

        if args.command == "render":
            compatibility = validate_spec(args.spec)
            rendered = routingctl.render_compatibility_markdown(compatibility)
            if args.output:
                output = Path(args.output).expanduser()
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(rendered, encoding="utf-8")
                print(output)
            else:
                print(rendered, end="")
            return 0

        if args.command == "refresh":
            plan_dir = refresh_plan(args.plan, args.spec)
            payload = {
                "status": "refreshed",
                "plan": str(plan_dir),
                "binding": routingctl.MODEL_COMPATIBILITY_JSON,
            }
            if args.json:
                print(json.dumps(payload, ensure_ascii=False))
            else:
                print(
                    f"Refreshed {routingctl.MODEL_COMPATIBILITY_JSON} for {plan_dir}; "
                    "TODO F/L requirements were not changed."
                )
            return 0
    except (CompatCtlError, planctl.PlanError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
