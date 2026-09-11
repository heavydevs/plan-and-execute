#!/usr/bin/env python3
"""Manage versioned shared pattern contracts for a plan-and-execute workspace."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

import planctl

PATTERN_DIR = "patterns"
REGISTRY_FILE = "patterns/registry.json"
ASSIGNMENT_DIR = "patterns/assignments"
SCHEMA_VERSION = 1


class PatternError(RuntimeError):
    pass


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PatternError(f"Cannot read JSON {path}: {exc}") from exc


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def slugify(value: str, fallback: str = "pattern") -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value[:56] or fallback


def normalize_pattern_id(value: Any) -> str:
    text = str(value or "").strip().upper()
    if not re.fullmatch(r"PAT[A-Z0-9_-]{1,28}", text):
        raise PatternError(f"Invalid pattern id {value!r}; use PAT... stable ids")
    return text


def normalize_contract(value: Any, field: str = "contract") -> list[str]:
    if not isinstance(value, list) or not value:
        raise PatternError(f"{field} must be a non-empty list")
    result: list[str] = []
    for index, item in enumerate(value):
        text = str(item or "").strip()
        if not text:
            raise PatternError(f"{field}[{index}] must be non-empty")
        if len(text) > 500:
            raise PatternError(f"{field}[{index}] exceeds 500 characters")
        result.append(text)
    return result


def pattern_digest(title: str, contract: list[str], source_refs: list[str]) -> str:
    payload = json.dumps(
        {"title": title, "contract": contract, "source_refs": source_refs},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def pattern_filename(pattern: dict[str, Any]) -> str:
    return f"{PATTERN_DIR}/{pattern['id']}-{pattern['slug']}.md"


def registry_path(plan_dir: Path) -> Path:
    return plan_dir / REGISTRY_FILE


def load_registry(plan_dir: Path) -> dict[str, Any]:
    path = registry_path(plan_dir)
    if not path.is_file():
        raise PatternError(f"Pattern registry not initialized: {path}")
    data = read_json(path)
    if not isinstance(data, dict) or data.get("schema_version") != SCHEMA_VERSION:
        raise PatternError("Unsupported or invalid pattern registry")
    if not isinstance(data.get("patterns"), list):
        raise PatternError("Pattern registry requires patterns[]")
    return data


def known_tasks(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(task["id"]): task for task in manifest.get("tasks", [])}


def normalize_initial_pattern(raw: Any, tasks: dict[str, dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise PatternError("Every pattern must be an object")
    pattern_id = normalize_pattern_id(raw.get("id"))
    title = str(raw.get("title", "")).strip()
    rationale = str(raw.get("rationale", "")).strip()
    if not title or not rationale:
        raise PatternError(f"{pattern_id}: title and rationale are required")
    contract = normalize_contract(raw.get("contract"), f"{pattern_id}.contract")
    source_refs = [str(item).strip() for item in raw.get("source_refs", []) if str(item).strip()]
    signatory_ids = [planctl.normalize_task_id(item) for item in raw.get("signatories", [])]
    if len(signatory_ids) < 2:
        raise PatternError(f"{pattern_id}: a shared pattern requires at least two signatory TODOs")
    if len(signatory_ids) != len(set(signatory_ids)):
        raise PatternError(f"{pattern_id}: duplicate signatories")
    unknown = sorted(set(signatory_ids) - set(tasks))
    if unknown:
        raise PatternError(f"{pattern_id}: unknown signatory TODOs: {', '.join(unknown)}")
    digest = pattern_digest(title, contract, source_refs)
    created = now_utc()
    return {
        "id": pattern_id,
        "slug": slugify(title),
        "title": title,
        "revision": 1,
        "digest": digest,
        "contract": contract,
        "source_refs": source_refs,
        "rationale": rationale,
        "signatories": [
            {
                "task_id": task_id,
                "adopted_revision": None,
                "adopted_digest": None,
                "adopted_at": None,
            }
            for task_id in signatory_ids
        ],
        "history": [
            {
                "revision": 1,
                "digest": digest,
                "at": created,
                "reason": "Initial final-plan pattern contract",
                "changed_by_task": None,
            }
        ],
    }


def render_pattern(pattern: dict[str, Any]) -> str:
    sources = ", ".join(f"`{item}`" for item in pattern["source_refs"]) or "None recorded"
    contract = "\n".join(f"- {item}" for item in pattern["contract"])
    signatories = [
        "| TODO | Adopted revision | Current? |",
        "|---|---:|---|",
    ]
    for signatory in pattern["signatories"]:
        adopted = signatory["adopted_revision"]
        current = adopted == pattern["revision"]
        signatories.append(
            f"| `{signatory['task_id']}` | {adopted if adopted is not None else '—'} | {'yes' if current else 'no'} |"
        )
    history = "\n".join(
        f"- r{entry['revision']} `{entry['digest'][:12]}` — {entry['reason']}"
        + (f" (task `{entry['changed_by_task']}`)" if entry.get("changed_by_task") else "")
        for entry in pattern["history"]
    )
    return (
        f"# {pattern['id']} — {pattern['title']}\n\n"
        f"- Current revision: **{pattern['revision']}**\n"
        f"- Digest: `{pattern['digest']}`\n"
        f"- Sources: {sources}\n"
        f"- Why shared: {pattern['rationale']}\n\n"
        "## Normative contract\n\n"
        f"{contract}\n\n"
        "## Signatories\n\n"
        + "\n".join(signatories)
        + "\n\n## Revision history\n\n"
        + history
        + "\n"
    )


def patterns_for_task(registry: dict[str, Any], task_id: str) -> list[dict[str, Any]]:
    return [
        pattern
        for pattern in registry["patterns"]
        if any(item["task_id"] == task_id for item in pattern["signatories"])
    ]


def render_assignment(plan_dir: Path, registry: dict[str, Any], task_id: str) -> str:
    patterns = patterns_for_task(registry, task_id)
    lines = [
        f"# Shared pattern assignment — TODO {task_id}",
        "",
        "Read exactly the pattern files below before implementation. Treat their current revisions as normative acceptance inputs. Do not edit pattern Markdown directly; propose/update contracts through `patternctl.py`.",
        "",
    ]
    if not patterns:
        lines.append("- No shared patterns assigned.")
    else:
        for pattern in patterns:
            signatory = next(item for item in pattern["signatories"] if item["task_id"] == task_id)
            lines.append(
                f"- **{pattern['id']} r{pattern['revision']}** — `{pattern_filename(pattern)}`; adopted: "
                f"{signatory['adopted_revision'] if signatory['adopted_revision'] is not None else 'not yet'}"
            )
    lines.append("")
    return "\n".join(lines)


def write_projections(plan_dir: Path, registry: dict[str, Any], manifest: dict[str, Any]) -> None:
    pattern_root = plan_dir / PATTERN_DIR
    pattern_root.mkdir(exist_ok=True)
    assignment_root = plan_dir / ASSIGNMENT_DIR
    assignment_root.mkdir(parents=True, exist_ok=True)

    expected_pattern_files: set[Path] = set()
    for pattern in registry["patterns"]:
        path = plan_dir / pattern_filename(pattern)
        expected_pattern_files.add(path)
        path.write_text(render_pattern(pattern), encoding="utf-8")

    task_ids = set(known_tasks(manifest))
    for task_id in task_ids:
        path = assignment_root / f"{task_id}.md"
        path.write_text(render_assignment(plan_dir, registry, task_id), encoding="utf-8")

    for child in pattern_root.glob("PAT*.md"):
        if child not in expected_pattern_files:
            child.unlink()
    for child in assignment_root.glob("*.md"):
        if child.stem not in task_ids:
            child.unlink()


def validate_registry(plan_dir: Path, registry: dict[str, Any], manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    tasks = known_tasks(manifest)
    seen: set[str] = set()
    for pattern in registry.get("patterns", []):
        try:
            pattern_id = normalize_pattern_id(pattern.get("id"))
        except PatternError as exc:
            errors.append(str(exc))
            continue
        if pattern_id in seen:
            errors.append(f"Duplicate pattern id {pattern_id}")
            continue
        seen.add(pattern_id)
        revision = pattern.get("revision")
        if not isinstance(revision, int) or revision < 1:
            errors.append(f"{pattern_id}: invalid revision")
            continue
        contract = pattern.get("contract")
        try:
            normalized_contract = normalize_contract(contract, f"{pattern_id}.contract")
        except PatternError as exc:
            errors.append(str(exc))
            continue
        source_refs = pattern.get("source_refs", [])
        if not isinstance(source_refs, list):
            errors.append(f"{pattern_id}: source_refs must be a list")
            continue
        expected_digest = pattern_digest(pattern.get("title", ""), normalized_contract, source_refs)
        if pattern.get("digest") != expected_digest:
            errors.append(f"{pattern_id}: digest does not match current contract")
        signatories = pattern.get("signatories")
        if not isinstance(signatories, list) or len(signatories) < 2:
            errors.append(f"{pattern_id}: requires at least two signatories")
            continue
        signatory_ids: list[str] = []
        for signatory in signatories:
            task_id = str(signatory.get("task_id", "")) if isinstance(signatory, dict) else ""
            signatory_ids.append(task_id)
            if task_id not in tasks:
                errors.append(f"{pattern_id}: unknown signatory {task_id}")
                continue
            adopted = signatory.get("adopted_revision")
            if adopted is not None and (not isinstance(adopted, int) or adopted < 1 or adopted > revision):
                errors.append(f"{pattern_id}: invalid adopted revision for TODO {task_id}")
            if tasks[task_id].get("status") == "completed" and adopted != revision:
                errors.append(
                    f"{pattern_id}: completed TODO {task_id} is stale at revision {adopted}; current is {revision}"
                )
        if len(signatory_ids) != len(set(signatory_ids)):
            errors.append(f"{pattern_id}: duplicate signatories")
        path = plan_dir / pattern_filename(pattern)
        if not path.is_file():
            errors.append(f"{pattern_id}: missing pattern file {path.relative_to(plan_dir)}")
        else:
            expected = render_pattern(pattern)
            if path.read_text(encoding="utf-8") != expected:
                errors.append(f"{pattern_id}: pattern file is not the registry projection")
    for task_id in tasks:
        path = plan_dir / ASSIGNMENT_DIR / f"{task_id}.md"
        if not path.is_file():
            errors.append(f"TODO {task_id}: missing pattern assignment projection")
        elif path.read_text(encoding="utf-8") != render_assignment(plan_dir, registry, task_id):
            errors.append(f"TODO {task_id}: pattern assignment projection is stale")
    return errors


def command_init(args: argparse.Namespace) -> None:
    plan_dir, manifest = planctl.load_plan(args.plan)
    planctl.require_valid(plan_dir, manifest)
    if registry_path(plan_dir).exists():
        raise PatternError("Pattern registry already exists")
    spec = read_json(Path(args.spec).expanduser().resolve())
    raw_patterns = spec.get("patterns") if isinstance(spec, dict) else None
    if not isinstance(raw_patterns, list):
        raise PatternError("Pattern spec must contain patterns[]")
    tasks = known_tasks(manifest)
    patterns = [normalize_initial_pattern(raw, tasks) for raw in raw_patterns]
    ids = [pattern["id"] for pattern in patterns]
    if len(ids) != len(set(ids)):
        raise PatternError("Pattern ids must be unique")
    registry = {
        "schema_version": SCHEMA_VERSION,
        "plan_id": manifest["plan_id"],
        "created_at": now_utc(),
        "updated_at": now_utc(),
        "patterns": patterns,
    }
    write_json(registry_path(plan_dir), registry)
    write_projections(plan_dir, registry, manifest)
    errors = validate_registry(plan_dir, registry, manifest)
    if errors:
        raise PatternError("Pattern validation failed: " + "; ".join(errors))
    print(registry_path(plan_dir))


def command_assignment(args: argparse.Namespace) -> None:
    plan_dir, manifest = planctl.load_plan(args.plan)
    registry = load_registry(plan_dir)
    task_id = planctl.normalize_task_id(args.task)
    if task_id not in known_tasks(manifest):
        raise PatternError(f"Unknown TODO {task_id}")
    patterns = patterns_for_task(registry, task_id)
    payload = {
        "task_id": task_id,
        "assignment_file": str(plan_dir / ASSIGNMENT_DIR / f"{task_id}.md"),
        "patterns": [
            {
                "id": pattern["id"],
                "revision": pattern["revision"],
                "digest": pattern["digest"],
                "file": str(plan_dir / pattern_filename(pattern)),
            }
            for pattern in patterns
        ],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def command_adopt(args: argparse.Namespace) -> None:
    plan_dir, manifest = planctl.load_plan(args.plan)
    registry = load_registry(plan_dir)
    task_id = planctl.normalize_task_id(args.task)
    tasks = known_tasks(manifest)
    if task_id not in tasks:
        raise PatternError(f"Unknown TODO {task_id}")
    if tasks[task_id].get("status") != "completed":
        raise PatternError(f"TODO {task_id} must be completed before pattern adoption is recorded")
    changed = False
    for pattern in patterns_for_task(registry, task_id):
        signatory = next(item for item in pattern["signatories"] if item["task_id"] == task_id)
        signatory["adopted_revision"] = pattern["revision"]
        signatory["adopted_digest"] = pattern["digest"]
        signatory["adopted_at"] = now_utc()
        changed = True
    if changed:
        registry["updated_at"] = now_utc()
        write_json(registry_path(plan_dir), registry)
        write_projections(plan_dir, registry, manifest)
    print(json.dumps({"task_id": task_id, "patterns_adopted": [p["id"] for p in patterns_for_task(registry, task_id)]}, ensure_ascii=False, indent=2))


def load_contract_file(path: Path) -> list[str]:
    data = read_json(path)
    if isinstance(data, list):
        return normalize_contract(data)
    if isinstance(data, dict):
        return normalize_contract(data.get("contract"))
    raise PatternError("Contract file must be a JSON array or object with contract[]")


def command_update(args: argparse.Namespace) -> None:
    plan_dir, manifest = planctl.load_plan(args.plan)
    registry = load_registry(plan_dir)
    pattern_id = normalize_pattern_id(args.pattern)
    pattern = next((item for item in registry["patterns"] if item["id"] == pattern_id), None)
    if pattern is None:
        raise PatternError(f"Unknown pattern {pattern_id}")
    changed_by = planctl.normalize_task_id(args.changed_by_task) if args.changed_by_task else None
    tasks = known_tasks(manifest)
    if changed_by is not None and changed_by not in tasks:
        raise PatternError(f"Unknown changed-by TODO {changed_by}")

    affected_ids = [item["task_id"] for item in pattern["signatories"]]
    active_conflicts = [
        task_id
        for task_id in affected_ids
        if task_id != changed_by and tasks[task_id].get("status") == "in_progress"
    ]
    if active_conflicts:
        raise PatternError(
            "Cannot revise a pattern while other signatories execute a stale revision: "
            + ", ".join(active_conflicts)
        )

    contract = load_contract_file(Path(args.contract_file).expanduser().resolve())
    new_digest = pattern_digest(pattern["title"], contract, pattern["source_refs"])
    if new_digest == pattern["digest"]:
        raise PatternError(f"{pattern_id}: contract is unchanged")
    old_revision = pattern["revision"]
    pattern["revision"] = old_revision + 1
    pattern["contract"] = contract
    pattern["digest"] = new_digest
    pattern["history"].append(
        {
            "revision": pattern["revision"],
            "digest": new_digest,
            "at": now_utc(),
            "reason": str(args.reason).strip(),
            "changed_by_task": changed_by,
        }
    )

    reset_tasks: list[str] = []
    for signatory in pattern["signatories"]:
        task_id = signatory["task_id"]
        if task_id == changed_by:
            continue
        adopted = signatory.get("adopted_revision")
        if adopted is not None and adopted < pattern["revision"] and tasks[task_id].get("status") == "completed":
            planctl.reset_task(plan_dir, manifest, task_id)
            tasks = known_tasks(manifest)
            reset_tasks.append(task_id)
        if adopted is not None and adopted < pattern["revision"]:
            signatory["adopted_revision"] = None
            signatory["adopted_digest"] = None
            signatory["adopted_at"] = None

    if changed_by is not None:
        signatory = next((item for item in pattern["signatories"] if item["task_id"] == changed_by), None)
        if signatory is not None and signatory.get("adopted_revision") != pattern["revision"]:
            signatory["adopted_revision"] = None
            signatory["adopted_digest"] = None
            signatory["adopted_at"] = None

    registry["updated_at"] = now_utc()
    write_json(registry_path(plan_dir), registry)
    write_projections(plan_dir, registry, manifest)
    print(json.dumps({"pattern": pattern_id, "old_revision": old_revision, "new_revision": pattern["revision"], "reset_completed_signatories": reset_tasks}, ensure_ascii=False, indent=2))


def command_validate(args: argparse.Namespace) -> None:
    plan_dir, manifest = planctl.load_plan(args.plan)
    registry = load_registry(plan_dir)
    errors = validate_registry(plan_dir, registry, manifest)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
    print(f"VALID {registry_path(plan_dir)}")


def command_status(args: argparse.Namespace) -> None:
    plan_dir, manifest = planctl.load_plan(args.plan)
    registry = load_registry(plan_dir)
    payload = {
        "plan_id": manifest["plan_id"],
        "patterns": [
            {
                "id": pattern["id"],
                "revision": pattern["revision"],
                "signatories": pattern["signatories"],
            }
            for pattern in registry["patterns"]
        ],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Create a versioned shared-pattern registry")
    init.add_argument("--plan", required=True)
    init.add_argument("--spec", required=True)
    init.set_defaults(func=command_init)

    assignment = sub.add_parser("assignment", help="Return exact pattern files assigned to one TODO")
    assignment.add_argument("--plan", required=True)
    assignment.add_argument("--task", required=True)
    assignment.set_defaults(func=command_assignment)

    adopt = sub.add_parser("adopt", help="Sign current pattern revisions after TODO completion")
    adopt.add_argument("--plan", required=True)
    adopt.add_argument("--task", required=True)
    adopt.set_defaults(func=command_adopt)

    update = sub.add_parser("update", help="Create a new pattern revision and invalidate stale completed signatories")
    update.add_argument("--plan", required=True)
    update.add_argument("--pattern", required=True)
    update.add_argument("--contract-file", required=True)
    update.add_argument("--reason", required=True)
    update.add_argument("--changed-by-task")
    update.set_defaults(func=command_update)

    validate = sub.add_parser("validate", help="Validate pattern registry, projections and completed signatures")
    validate.add_argument("--plan", required=True)
    validate.set_defaults(func=command_validate)

    status = sub.add_parser("status", help="Show pattern revisions and signatory adoption state")
    status.add_argument("--plan", required=True)
    status.set_defaults(func=command_status)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
        return 0
    except (PatternError, planctl.PlanError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
