#!/usr/bin/env python3
"""Validate, cache, render, and refresh portable F/L model compatibility bindings."""
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


def require_fresh(compatibility: dict[str, Any]) -> None:
    stale = [
        provider
        for provider in compatibility["providers"]
        if not routingctl.compatibility_provider_is_fresh(compatibility, provider)
    ]
    if stale:
        raise CompatCtlError(
            "Compatibility was not checked today in local time for: " + ", ".join(stale)
        )


def cache_status(provider: str) -> dict[str, Any]:
    try:
        return routingctl.compatibility_cache_status(provider)
    except routingctl.RoutingError as exc:
        raise CompatCtlError(str(exc)) from exc


def cache_read(provider: str) -> dict[str, Any]:
    try:
        compatibility = routingctl.load_cached_compatibility(provider, require_fresh=True)
    except routingctl.RoutingError as exc:
        raise CompatCtlError(str(exc)) from exc
    if compatibility is None:
        status = cache_status(provider)
        raise CompatCtlError(
            f"No fresh daily cache for {provider}: {status['status']}. "
            "Inspect this provider's installed CLI/current official documentation, then cache-write the new binding."
        )
    return compatibility


def cache_write(provider: str, spec_path: str | Path) -> Path:
    compatibility = validate_spec(spec_path)
    try:
        return routingctl.write_cached_compatibility(provider, compatibility)
    except routingctl.RoutingError as exc:
        raise CompatCtlError(str(exc)) from exc


def refresh_plan(
    plan_arg: str | Path,
    spec_path: str | Path | None = None,
    provider: str | None = None,
) -> Path:
    plan_dir, manifest = planctl.load_plan(plan_arg)
    if manifest.get("routing_schema") != routingctl.PORTABLE_ROUTING_VERSION:
        raise CompatCtlError(
            "Compatibility refresh is only valid for portable F/L plans; "
            "legacy provider/tier plans remain unchanged"
        )
    if (spec_path is None) == (provider is None):
        raise CompatCtlError("refresh requires exactly one of spec_path or provider")

    if provider is not None:
        compatibility = cache_read(provider)
    else:
        compatibility = validate_spec(spec_path)
        require_fresh(compatibility)

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
    manifest["model_compatibility_providers"] = list(compatibility["providers"])
    planctl.append_event(
        manifest,
        "model_compatibility_refreshed",
        generated_at=compatibility["generated_at"],
        providers=list(compatibility["providers"]),
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
        description="Manage portable model compatibility with one daily cache per provider."
    )
    sub = root.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="Validate a compatibility JSON/spec file")
    validate.add_argument("--spec", required=True)
    validate.add_argument("--json", action="store_true")

    render = sub.add_parser("render", help="Render a compatibility JSON/spec file as Markdown")
    render.add_argument("--spec", required=True)
    render.add_argument("--output")

    status = sub.add_parser(
        "cache-status",
        help="Report whether today's provider-specific compatibility cache can be reused",
    )
    status.add_argument("--provider", required=True, choices=routingctl.PORTABLE_PROVIDERS)
    status.add_argument("--json", action="store_true")

    read = sub.add_parser(
        "cache-read",
        help="Read today's provider-specific compatibility cache",
    )
    read.add_argument("--provider", required=True, choices=routingctl.PORTABLE_PROVIDERS)
    read.add_argument("--output")

    write = sub.add_parser(
        "cache-write",
        help="Validate and store today's compatibility for exactly one provider",
    )
    write.add_argument("--provider", required=True, choices=routingctl.PORTABLE_PROVIDERS)
    write.add_argument("--spec", required=True)
    write.add_argument("--json", action="store_true")

    refresh = sub.add_parser(
        "refresh",
        help="Replace a portable plan's binding without changing TODO F/L requirements",
    )
    refresh.add_argument("--plan", required=True)
    source = refresh.add_mutually_exclusive_group(required=True)
    source.add_argument("--spec")
    source.add_argument("--provider", choices=routingctl.PORTABLE_PROVIDERS)
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

        if args.command == "cache-status":
            status = cache_status(args.provider)
            if args.json:
                print(json.dumps(status, ensure_ascii=False))
            else:
                checked = f" checked_at={status['checked_at']}" if status.get("checked_at") else ""
                print(f"{args.provider}: {status['status']} ({status['path']}){checked}")
            return 0

        if args.command == "cache-read":
            compatibility = cache_read(args.provider)
            payload = json.dumps(compatibility, ensure_ascii=False, indent=2) + "\n"
            if args.output:
                output = Path(args.output).expanduser()
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(payload, encoding="utf-8")
                print(output)
            else:
                print(payload, end="")
            return 0

        if args.command == "cache-write":
            path = cache_write(args.provider, args.spec)
            payload = {"status": "cached", "provider": args.provider, "path": str(path)}
            if args.json:
                print(json.dumps(payload, ensure_ascii=False))
            else:
                print(f"Cached today's {args.provider} compatibility at {path}")
            return 0

        if args.command == "refresh":
            plan_dir = refresh_plan(args.plan, spec_path=args.spec, provider=args.provider)
            payload = {
                "status": "refreshed",
                "plan": str(plan_dir),
                "binding": routingctl.MODEL_COMPATIBILITY_JSON,
                "provider": args.provider,
            }
            if args.json:
                print(json.dumps(payload, ensure_ascii=False))
            else:
                print(
                    f"Refreshed {routingctl.MODEL_COMPATIBILITY_JSON} for {plan_dir}; "
                    "TODO F/L requirements were not changed."
                )
            return 0
    except (CompatCtlError, planctl.PlanError, routingctl.RoutingError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
