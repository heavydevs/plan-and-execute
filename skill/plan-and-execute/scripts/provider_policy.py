#!/usr/bin/env python3
"""Plan-scoped executor authorization, independent of the manager's model.

This is a dispatch policy for trusted adapters, not a sandbox or remote-model
attestation. Keep this module dependency-free: controllers and workers share it.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

FIELD = "execution_policy"
SNAPSHOT = "EXECUTION_POLICY.json"
POLICY_VERSION = 1
PLAN_SCHEMA_VERSION = 5
EXIT_POLICY = 6
PROVIDERS = frozenset({"claude", "codex", "antigravity", "gemini", "qwen", "kimi", "trae"})
TECHNICAL_PHASES = (
    "study", "planning", "plan_review", "design", "implementation",
    "test_authoring", "validation", "repair",
)
DEFAULTS = {
    "version": POLICY_VERSION,
    "manager_mode": "delegate_only",
    "scope": "all_technical_work",
    "on_unavailable": "pause",
}


class PolicyError(RuntimeError):
    """Fail closed without consuming a technical attempt or widening the policy."""


def normalize(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise PolicyError("execution_policy must be an object, not null or a provider string")
    unknown = set(raw) - (set(DEFAULTS) | {"allowed_providers"})
    if unknown:
        raise PolicyError(f"Unknown execution_policy fields: {', '.join(sorted(unknown))}")
    result = dict(DEFAULTS)
    for key, expected in DEFAULTS.items():
        value = raw.get(key, expected)
        if type(value) is not type(expected) or value != expected:
            raise PolicyError(f"execution_policy.{key} must be {expected!r}")
    allowed = raw.get("allowed_providers")
    if not isinstance(allowed, list) or not allowed:
        raise PolicyError("allowed_providers must be a non-empty list; empty never means unrestricted")
    if any(not isinstance(item, str) or item not in PROVIDERS for item in allowed):
        raise PolicyError("allowed_providers accepts exact executor IDs: " + ", ".join(sorted(PROVIDERS)))
    if len(set(allowed)) != len(allowed):
        raise PolicyError("allowed_providers must not contain duplicates")
    result["allowed_providers"] = sorted(allowed)
    return result


def from_document(document: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(document, dict):
        raise PolicyError("Policy-bearing document must be an object")
    return normalize(document[FIELD]) if FIELD in document else None


def from_csv(value: str) -> dict[str, Any]:
    if not isinstance(value, str) or not value.strip():
        raise PolicyError("An explicit provider list cannot be empty")
    return normalize({"allowed_providers": [part.strip().lower() for part in value.split(",")]})


def read_policy(path: str | Path) -> dict[str, Any]:
    try:
        return normalize(json.loads(Path(path).read_text(encoding="utf-8")))
    except (OSError, ValueError) as exc:
        raise PolicyError(f"Cannot read execution policy: {path}: {exc}") from exc


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True,
                                     separators=(",", ":")).encode()).hexdigest()


def reconcile(*policies: dict[str, Any] | None) -> dict[str, Any] | None:
    """No source (config, CLI, spec, prepared input) may override another."""
    selected = None
    for raw in policies:
        if raw is None:
            continue
        policy = normalize(raw)
        if selected is not None and policy != selected:
            raise PolicyError("Conflicting execution policies; resolve the user's authorization explicitly")
        selected = policy
    return selected


def attach(spec: dict[str, Any], policy: dict[str, Any] | None) -> dict[str, Any]:
    selected = reconcile(from_document(spec), policy)
    result = copy.deepcopy(spec)
    if selected is not None:
        result[FIELD] = selected
    return result


def require_provider(policy: dict[str, Any] | None, provider: Any, *, allow_auto: bool = False) -> None:
    if policy is None:
        return
    policy = normalize(policy)
    if allow_auto and provider == "auto":
        return
    if not isinstance(provider, str) or provider not in policy["allowed_providers"]:
        raise PolicyError(
            f"Executor {provider!r} is not authorized. Allowed: {', '.join(policy['allowed_providers'])}. "
            "The manager must delegate or pause; it must not perform technical work itself."
        )


def candidates(policy: dict[str, Any], requested: str, order: list[str], fallback: bool) -> list[str]:
    policy = normalize(policy)
    require_provider(policy, requested, allow_auto=True)
    allowed = policy["allowed_providers"]
    ordered = list(dict.fromkeys([item for item in order if item in allowed] + allowed))
    if requested == "auto":
        return ordered
    return [requested] + ([item for item in ordered if item != requested] if fallback else [])


def bind_config(config: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    policy = from_document(manifest)
    configured = from_document(config)
    if configured is not None and policy is None:
        raise PolicyError("Config cannot introduce or replace a plan policy; capture it in the plan first")
    reconcile(policy, configured)
    result = dict(config)
    if policy is not None:
        result[FIELD] = policy
    return result


def validate_routes(manifest: dict[str, Any]) -> None:
    policy = from_document(manifest)
    if policy is None:
        return

    def route_provider(route: Any, label: str) -> None:
        if not isinstance(route, dict):
            raise PolicyError(f"{label} must be a route object")
        require_provider(policy, route.get("provider"))

    tasks = manifest.get("tasks", [])
    if not isinstance(tasks, list):
        raise PolicyError("tasks must be a list")
    for task in tasks:
        if not isinstance(task, dict):
            raise PolicyError("Every governed task must be an object")
        require_provider(policy, task.get("provider", "auto"), allow_auto=True)
        design = task.get("design_route")
        if design is not None:
            if not isinstance(design, dict):
                raise PolicyError("design_route must be an object")
            require_provider(policy, design.get("provider", task.get("provider", "auto")), allow_auto=True)
        route = task.get("current_route")
        if route is not None:
            route_provider(route, "current_route")
        history = task.get("history", [])
        if not isinstance(history, list):
            raise PolicyError("Task history must be a list")
        for item in history:
            if not isinstance(item, dict):
                raise PolicyError("Task history entries must be objects")
            if item.get("route") is not None:
                route_provider(item["route"], "history route")
        phase = task.get("design_phase")
        if phase is not None:
            if not isinstance(phase, dict):
                raise PolicyError("design_phase must be an object")
            if phase.get("route") is not None:
                route_provider(phase["route"], "design phase route")
    provenance = manifest.get("planning_provenance")
    if provenance is not None:
        route_provider(provenance, "planning_provenance")


def seal(plan_dir: Path, manifest: dict[str, Any], sentinel: dict[str, Any]) -> None:
    policy = from_document(manifest)
    if policy is not None:
        (plan_dir / SNAPSHOT).write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        sentinel["execution_policy_sha256"] = digest(policy)


def verify_snapshot(plan_dir: Path, manifest: dict[str, Any]) -> None:
    policy = from_document(manifest)
    try:
        sentinel_path = plan_dir / ".orchestrator-plan"
        if sentinel_path.is_symlink():
            raise PolicyError("Policy sentinel must not be a symlink")
        sentinel = json.loads(sentinel_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise PolicyError(f"Cannot verify execution policy sentinel: {exc}") from exc
    if not isinstance(sentinel, dict):
        raise PolicyError("Policy sentinel must be an object")
    pinned = sentinel.get("execution_policy_sha256")
    snapshot = plan_dir / SNAPSHOT
    governed = policy is not None or pinned is not None or snapshot.exists() or snapshot.is_symlink()
    if not governed:
        if manifest.get("schema_version") == PLAN_SCHEMA_VERSION:
            raise PolicyError("Schema-5 plans must retain their execution policy")
        return
    if policy is None or manifest.get("schema_version") != PLAN_SCHEMA_VERSION:
        raise PolicyError("Execution policy was removed or its plan schema was downgraded")
    if sentinel.get("schema_version") != PLAN_SCHEMA_VERSION:
        raise PolicyError("Execution policy sentinel schema mismatch")
    if snapshot.is_symlink() or not snapshot.is_file():
        raise PolicyError("Execution policy snapshot is missing or is a symlink")
    if read_policy(snapshot) != policy or pinned != digest(policy):
        raise PolicyError("Execution policy differs from its pinned snapshot; refuse to continue")
    validate_routes(manifest)


def capsule(policy: dict[str, Any] | None) -> str:
    if policy is None:
        return ""
    policy = normalize(policy)
    return ("Executor policy: " + ",".join(policy["allowed_providers"]) +
            ". All technical work, including planning, tests and repairs, stays within this set. "
            "Do not invoke other AI providers or rewrite this policy.\n\n")


def validate_adapter(policy: dict[str, Any] | None, provider: str, command: list[str]) -> None:
    """Catch accidental known-CLI masquerading; custom adapters remain trusted."""
    require_provider(policy, provider)
    if policy is None or not command:
        return
    name = command[0].replace("\\", "/").rsplit("/", 1)[-1].lower()
    for suffix in (".exe", ".cmd", ".bat"):
        if name.endswith(suffix):
            name = name[:-len(suffix)]
    cli_names = {**{name: name for name in PROVIDERS}, "agy": "antigravity", "trae-cli": "trae"}
    actual = cli_names.get(name)
    if actual is not None and actual != provider:
        raise PolicyError(f"Configured {provider} adapter invokes the {actual} CLI")


def plan_notice(manifest: dict[str, Any]) -> str:
    policy = from_document(manifest)
    if policy is None:
        return ""
    return ("Manager: any model, dispatch/report only. Technical executors: "
            + ", ".join(policy["allowed_providers"])
            + ". Scope: study, planning, review, design, code, tests, validation and repairs. "
              "If none is available: pause. Authority: `EXECUTION_POLICY.json`.\n")


def manager_status(plan_dir: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    import planctl
    verify_snapshot(plan_dir, manifest)
    task = planctl.next_runnable_task(manifest)
    counts = {state: sum(t["status"] == state for t in manifest["tasks"])
              for state in ("pending", "in_progress", "completed", "blocked")}
    item = None
    if task:
        item = {key: task.get(key) for key in ("id", "file", "provider", "model_tier", "reasoning_effort")}
        item["last_failure_class"] = (task.get("failure_classes") or [None])[-1]
        item["last_error"] = str(task.get("last_error") or "")[:240]
    return {"plan": str(plan_dir), "state": manifest["state"], "execution_policy": from_document(manifest),
            "counts": counts, "next_task": item,
            "action": "dispatch_next" if task else ("handoff" if manifest["state"] == "completed" else "inspect_blocker")}


def main() -> int:
    import planctl
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="Capture the user's authorization before semantic planning")
    init.add_argument("--allowed-providers", required=True)
    init.add_argument("--out", required=True)
    show = sub.add_parser("show", help="Small manager-only status; no task bodies or transcript")
    show.add_argument("--plan", required=True)
    check = sub.add_parser("check", help="Check a technical executor without calling a model")
    check.add_argument("--policy", required=True)
    check.add_argument("--provider", required=True)
    args = parser.parse_args()
    try:
        if args.command == "init":
            policy = from_csv(args.allowed_providers)
            dest = Path(args.out).expanduser().absolute()
            if dest.is_symlink():
                raise PolicyError("Refuse to replace a symlink policy")
            if dest.exists():
                if read_policy(dest) != policy:
                    raise PolicyError("Policy already exists with different authorization; no implicit overwrite")
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                with dest.open("x", encoding="utf-8") as handle:
                    handle.write(json.dumps(policy, indent=2) + "\n")
            print(json.dumps({"policy": str(dest), "sha256": digest(policy), **policy}))
        elif args.command == "check":
            policy = read_policy(args.policy)
            require_provider(policy, args.provider)
            print(json.dumps({"allowed": True, "provider": args.provider, "policy_sha256": digest(policy)}))
        else:
            import planctl
            plan_dir, manifest = planctl.load_plan(args.plan)
            print(json.dumps(manager_status(plan_dir, manifest), ensure_ascii=False, separators=(",", ":")))
        return 0
    except (PolicyError, planctl.PlanError, OSError, ValueError) as exc:
        print(f"POLICY_PAUSED: {exc}", file=sys.stderr)
        return EXIT_POLICY


if __name__ == "__main__":
    raise SystemExit(main())
