#!/usr/bin/env python3
"""Deterministic plan-state manager for plan-and-execute.

The script intentionally uses only the Python standard library. It creates and
updates ephemeral planning workspaces without touching implementation files.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable

import requestctl

SCHEMA_VERSION = 2
SUPPORTED_SCHEMA_VERSIONS = {1, 2}
SENTINEL = ".orchestrator-plan"
MANIFEST = "manifest.json"
CONFIG = "orchestrator.config.json"
WORK_ROOT_DEFAULT = ".ai-work"
REQUEST_FILE = "REQUEST.md"
VALID_PROVIDERS = {"auto", "claude", "codex"}
VALID_TIERS = {"economy", "standard", "strong", "max"}
VALID_EFFORTS = {"low", "medium", "high", "xhigh", "max"}
VALID_STATUSES = {"pending", "in_progress", "completed", "blocked"}
VALID_COMPLEXITIES = {"low", "medium", "high", "extreme"}
VALID_REQUIREMENT_SOURCES = {"user", "repository", "research", "inferred"}
VALID_PRIORITIES = {"must", "should", "could"}
REQUIRED_REVIEW_CHECKS = (
    "coverage_complete",
    "tasks_atomic",
    "dependencies_valid",
    "validations_sufficient",
)


class PlanError(RuntimeError):
    """Raised when a plan workspace is invalid or an operation is unsafe."""


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def slugify(value: str, fallback: str = "plan") -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value[:64] or fallback


def normalize_task_id(value: Any) -> str:
    text = str(value).strip()
    if text.isdigit():
        return f"{int(text):03d}"
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,31}", text):
        raise PlanError(f"Invalid task id: {value!r}")
    return text


def normalize_request_part_id(value: Any, index: int | None = None) -> str:
    if value is None or not str(value).strip():
        if index is None:
            raise PlanError("Request-part id is required")
        return f"P{index + 1:03d}"
    text = str(value).strip().upper()
    if text.isdigit():
        return f"P{int(text):03d}"
    if re.fullmatch(r"P\d+", text):
        return f"P{int(text[1:]):03d}"
    if not re.fullmatch(r"[A-Z][A-Z0-9_-]{0,31}", text):
        raise PlanError(f"Invalid request-part id: {value!r}")
    return text


def normalize_requirement_id(value: Any, index: int | None = None) -> str:
    if value is None or not str(value).strip():
        if index is None:
            raise PlanError("Requirement id is required")
        return f"R{index + 1:03d}"
    text = str(value).strip().upper()
    if text.isdigit():
        return f"R{int(text):03d}"
    if re.fullmatch(r"R\d+", text):
        return f"R{int(text[1:]):03d}"
    if not re.fullmatch(r"[A-Z][A-Z0-9_-]{0,31}", text):
        raise PlanError(f"Invalid requirement id: {value!r}")
    return text


def ensure_text(value: Any, field: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise PlanError(f"{field} must be a non-empty string")
    return text


def normalize_request_parts(raw: Any) -> list[dict[str, str]]:
    items = ensure_list(raw, "request_analysis.request_parts")
    if not items:
        raise PlanError("request_analysis.request_parts must inventory every distinct requested outcome")
    normalized: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    seen_text: set[str] = set()
    for index, item in enumerate(items):
        if isinstance(item, str):
            request_part = {
                "id": normalize_request_part_id(None, index),
                "text": ensure_text(item, f"request_analysis.request_parts[{index}]"),
            }
        elif isinstance(item, dict):
            request_part = {
                "id": normalize_request_part_id(item.get("id"), index),
                "text": ensure_text(
                    item.get("text"), f"request_analysis.request_parts[{index}].text"
                ),
            }
        else:
            raise PlanError(
                f"request_analysis.request_parts[{index}] must be a string or object"
            )
        if request_part["id"] in seen_ids:
            raise PlanError(f"Duplicate request-part id: {request_part['id']}")
        folded = request_part["text"].casefold()
        if folded in seen_text:
            raise PlanError(f"Duplicate request-part text: {request_part['text']!r}")
        seen_ids.add(request_part["id"])
        seen_text.add(folded)
        normalized.append(request_part)
    return normalized


def normalize_requirements(
    raw: Any,
    known_request_part_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    items = ensure_list(raw, "requirements")
    if not items:
        raise PlanError("Plan spec requires a complete, non-empty requirements inventory")
    normalized: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_text: set[str] = set()
    for index, item in enumerate(items):
        if isinstance(item, str):
            raise PlanError(
                f"requirements[{index}] must be an object with explicit request_part_ids in schema v2"
            )
        elif isinstance(item, dict):
            requirement_id = normalize_requirement_id(item.get("id"), index)
            source = str(item.get("source", "user")).strip().lower()
            priority = str(item.get("priority", "must")).strip().lower()
            if source not in VALID_REQUIREMENT_SOURCES:
                raise PlanError(
                    f"Requirement {requirement_id}: invalid source {source!r}; "
                    f"expected one of {sorted(VALID_REQUIREMENT_SOURCES)}"
                )
            if priority not in VALID_PRIORITIES:
                raise PlanError(
                    f"Requirement {requirement_id}: invalid priority {priority!r}; "
                    f"expected one of {sorted(VALID_PRIORITIES)}"
                )
            request_part_ids = [
                normalize_request_part_id(value)
                for value in ensure_list(
                    item.get("request_part_ids"),
                    f"Requirement {requirement_id} request_part_ids",
                )
            ]
            requirement = {
                "id": requirement_id,
                "text": ensure_text(item.get("text"), f"Requirement {requirement_id} text"),
                "source": source,
                "priority": priority,
                "request_part_ids": request_part_ids,
            }
        else:
            raise PlanError(f"requirements[{index}] must be a string or object")
        if requirement["source"] == "user" and not requirement["request_part_ids"]:
            raise PlanError(
                f"Requirement {requirement['id']}: user-sourced requirements must map to at least "
                "one request_part_id"
            )
        if known_request_part_ids is not None:
            unknown_parts = sorted(
                set(requirement["request_part_ids"]) - known_request_part_ids
            )
            if unknown_parts:
                raise PlanError(
                    f"Requirement {requirement['id']} references unknown request parts: "
                    + ", ".join(unknown_parts)
                )
        if requirement["id"] in seen_ids:
            raise PlanError(f"Duplicate requirement id: {requirement['id']}")
        folded = requirement["text"].casefold()
        if folded in seen_text:
            raise PlanError(f"Duplicate requirement text: {requirement['text']!r}")
        seen_ids.add(requirement["id"])
        seen_text.add(folded)
        normalized.append(requirement)
    return normalized


def normalize_request_analysis(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise PlanError("request_analysis must be an object created after studying the request and repository")
    request_parts = normalize_request_parts(raw.get("request_parts"))
    repository_findings = ensure_str_list(
        raw.get("repository_findings"), "request_analysis.repository_findings"
    )
    if not repository_findings:
        raise PlanError(
            "request_analysis.repository_findings must record repository inspection, even for a greenfield repository"
        )
    return {
        "request_parts": request_parts,
        "repository_findings": repository_findings,
        "research_decision": ensure_text(
            raw.get("research_decision"), "request_analysis.research_decision"
        ),
        "research_findings": ensure_str_list(
            raw.get("research_findings"), "request_analysis.research_findings"
        ),
        "assumptions": ensure_str_list(raw.get("assumptions"), "request_analysis.assumptions"),
        "risks": ensure_str_list(raw.get("risks"), "request_analysis.risks"),
        "open_questions": ensure_str_list(
            raw.get("open_questions"), "request_analysis.open_questions"
        ),
        "decomposition_strategy": ensure_text(
            raw.get("decomposition_strategy"), "request_analysis.decomposition_strategy"
        ),
    }

def normalize_plan_review(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise PlanError("plan_review must be an object produced by a separate plan-review pass")
    status = str(raw.get("status", "")).strip().lower()
    if status != "approved":
        raise PlanError("plan_review.status must be 'approved' before execution can start")
    rounds = int(raw.get("rounds", 0))
    if rounds < 1:
        raise PlanError("plan_review.rounds must be at least 1")
    checks: dict[str, bool] = {}
    for field in REQUIRED_REVIEW_CHECKS:
        value = raw.get(field)
        if value is not True:
            raise PlanError(f"plan_review.{field} must be true")
        checks[field] = True
    unresolved = ensure_str_list(
        raw.get("unresolved_findings"), "plan_review.unresolved_findings"
    )
    if unresolved:
        raise PlanError("plan_review.unresolved_findings must be empty before autostart")
    notes = ensure_str_list(raw.get("notes"), "plan_review.notes")
    if not notes:
        raise PlanError("plan_review.notes must record what the reviewer checked")
    return {
        "status": status,
        "reviewer": ensure_text(raw.get("reviewer"), "plan_review.reviewer"),
        "rounds": rounds,
        **checks,
        "unresolved_findings": unresolved,
        "notes": notes,
    }


def ensure_list(value: Any, field: str) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise PlanError(f"{field} must be a list")
    return value


def ensure_str_list(value: Any, field: str) -> list[str]:
    items = ensure_list(value, field)
    result: list[str] = []
    for item in items:
        if not isinstance(item, str) or not item.strip():
            raise PlanError(f"Every item in {field} must be a non-empty string")
        result.append(item.strip())
    return result


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False, newline="\n"
    ) as handle:
        handle.write(content)
        tmp = Path(handle.name)
    os.replace(tmp, path)


def atomic_write_json(path: Path, data: Any) -> None:
    atomic_write_text(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PlanError(f"File not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise PlanError(f"Invalid JSON in {path}: {exc}") from exc


def markdown_list(items: Iterable[str], empty: str = "- None") -> str:
    materialized = list(items)
    return "\n".join(f"- {item}" for item in materialized) if materialized else empty


def absolute_lexical(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path.expanduser())))


def reject_symlink_components(root: Path, relative: Path, field: str) -> None:
    current = root
    for part in relative.parts:
        current = current / part
        if current.exists() and current.is_symlink():
            raise PlanError(f"{field} must not traverse a symlink: {current}")


def checked_relative_path(value: str, field: str) -> str:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise PlanError(f"{field} must contain repository-relative paths only: {value!r}")
    return path.as_posix()


def ensure_git_exclude(repo_root: Path, work_root: str) -> dict[str, Any] | None:
    """Hide ephemeral plans from git status without modifying tracked files."""
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--git-path", "info/exclude"],
            cwd=repo_root,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0 or not completed.stdout.strip():
        return None
    raw_path = Path(completed.stdout.strip())
    exclude_path = raw_path if raw_path.is_absolute() else repo_root / raw_path
    exclude_path = exclude_path.resolve()
    pattern = "/" + Path(work_root).as_posix().strip("/") + "/"
    marker_key = slugify(work_root, "ai-work")
    begin = f"# plan-and-execute begin: {marker_key}"
    end = f"# plan-and-execute end: {marker_key}"
    try:
        current = exclude_path.read_text(encoding="utf-8") if exclude_path.exists() else ""
    except OSError:
        return None
    if begin in current and end in current:
        return {
            "path": str(exclude_path),
            "pattern": pattern,
            "begin": begin,
            "end": end,
            "managed": True,
        }
    existing_patterns = {line.strip() for line in current.splitlines() if line.strip() and not line.lstrip().startswith("#")}
    if pattern in existing_patterns or pattern.lstrip("/") in existing_patterns:
        return {
            "path": str(exclude_path),
            "pattern": pattern,
            "begin": begin,
            "end": end,
            "managed": False,
        }
    block = f"{begin}\n{pattern}\n{end}\n"
    content = current
    if content and not content.endswith("\n"):
        content += "\n"
    content += block
    try:
        atomic_write_text(exclude_path, content)
    except OSError:
        return None
    return {
        "path": str(exclude_path),
        "pattern": pattern,
        "begin": begin,
        "end": end,
        "managed": True,
    }


def remove_git_exclude_entry(info: Any) -> None:
    if not isinstance(info, dict) or not info.get("managed"):
        return
    path_value = info.get("path")
    begin = info.get("begin")
    end = info.get("end")
    if not all(isinstance(item, str) and item for item in (path_value, begin, end)):
        return
    path = Path(path_value)
    try:
        current = path.read_text(encoding="utf-8")
    except OSError:
        return
    pattern = re.compile(
        rf"(?m)^\s*{re.escape(begin)}\s*\n.*?^\s*{re.escape(end)}\s*\n?",
        re.DOTALL,
    )
    updated, count = pattern.subn("", current, count=1)
    if count:
        try:
            atomic_write_text(path, updated)
        except OSError:
            return


def default_config() -> dict[str, Any]:
    return {
        "version": 1,
        "provider_order": ["claude", "codex"],
        "allow_provider_fallback": True,
        "strict_fresh_context": True,
        "auto_cleanup": True,
        "functional_failures_per_provider": 4,
        "task_timeout_seconds": 0,
        "validation_timeout_seconds": 1800,
        "stream_provider_output": True,
        "rate_limit": {
            "auto_wait": True,
            "wait_seconds": 300,
            "max_wait_cycles": 0,
        },
        "claude": {
            "command": "claude",
            "models": {
                "economy": "haiku",
                "standard": "sonnet",
                "strong": "opus",
                "max": "opus",
            },
            "permission_mode": "auto",
            "max_effort_by_tier": {
                "economy": "medium",
                "standard": "high",
                "strong": "max",
                "max": "max",
            },
            "extra_args": [],
        },
        "codex": {
            "command": "codex",
            "models": {
                "economy": "gpt-5.6-luna",
                "standard": "gpt-5.6-terra",
                "strong": "gpt-5.6",
                "max": "gpt-5.6",
            },
            "sandbox": "workspace-write",
            "ignore_user_config": False,
            "max_effort_by_tier": {
                "economy": "medium",
                "standard": "high",
                "strong": "xhigh",
                "max": "xhigh",
            },
            "extra_args": [],
        },
        "summary": {
            "provider": "auto",
            "model_tier": "economy",
            "reasoning_effort": "low",
        },
    }


def normalize_scope(raw: Any, field: str) -> dict[str, list[str]]:
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise PlanError(f"{field} must be an object")
    return {
        "in": ensure_str_list(raw.get("in"), f"{field}.in"),
        "out": ensure_str_list(raw.get("out"), f"{field}.out"),
        "expected_files": [
            checked_relative_path(item, f"{field}.expected_files")
            for item in ensure_str_list(raw.get("expected_files"), f"{field}.expected_files")
        ],
    }


def normalize_task(
    raw: Any,
    index: int,
    known_requirement_ids: set[str],
) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise PlanError(f"tasks[{index}] must be an object")
    task_id = normalize_task_id(raw.get("id", index + 1))
    title = str(raw.get("title", "")).strip()
    objective = str(raw.get("objective", "")).strip()
    if not title or not objective:
        raise PlanError(f"Task {task_id} requires title and objective")

    provider = str(raw.get("provider", "auto")).strip().lower()
    tier = str(raw.get("model_tier", "standard")).strip().lower()
    effort = str(raw.get("reasoning_effort", "medium")).strip().lower()
    complexity = str(raw.get("complexity", "")).strip().lower()
    if provider not in VALID_PROVIDERS:
        raise PlanError(f"Task {task_id}: invalid provider {provider!r}")
    if tier not in VALID_TIERS:
        raise PlanError(f"Task {task_id}: invalid model_tier {tier!r}")
    if effort not in VALID_EFFORTS:
        raise PlanError(f"Task {task_id}: invalid reasoning_effort {effort!r}")
    if complexity not in VALID_COMPLEXITIES:
        raise PlanError(
            f"Task {task_id}: complexity is required and must be one of {sorted(VALID_COMPLEXITIES)}"
        )
    if complexity == "extreme":
        raise PlanError(
            f"Task {task_id}: executable TODOs may not have extreme complexity; "
            "recursively split it into smaller independently verifiable TODOs"
        )

    requirement_ids = [
        normalize_requirement_id(item)
        for item in ensure_list(raw.get("requirement_ids"), f"Task {task_id} requirement_ids")
    ]
    if not requirement_ids:
        raise PlanError(f"Task {task_id} must cover at least one requirement id")
    unknown_requirements = sorted(set(requirement_ids) - known_requirement_ids)
    if unknown_requirements:
        raise PlanError(
            f"Task {task_id} references unknown requirements: {', '.join(unknown_requirements)}"
        )

    atomicity_rationale = ensure_text(
        raw.get("atomicity_rationale"), f"Task {task_id} atomicity_rationale"
    )
    if complexity == "high" and len(atomicity_rationale) < 40:
        raise PlanError(
            f"Task {task_id}: high-complexity work needs a substantive atomicity_rationale "
            "explaining why further splitting would harm independent implementation or validation"
        )

    dependencies = [
        normalize_task_id(item)
        for item in ensure_list(raw.get("dependencies"), f"Task {task_id} dependencies")
    ]
    related = [
        normalize_task_id(item)
        for item in ensure_list(raw.get("related_task_reads"), f"Task {task_id} related_task_reads")
    ]
    max_attempts = int(raw.get("max_attempts", 8))
    if max_attempts < 1 or max_attempts > 50:
        raise PlanError(f"Task {task_id}: max_attempts must be between 1 and 50")

    acceptance = ensure_str_list(raw.get("acceptance_criteria"), f"Task {task_id} acceptance_criteria")
    validations = ensure_str_list(raw.get("validation_commands"), f"Task {task_id} validation_commands")
    if not acceptance:
        raise PlanError(f"Task {task_id} requires at least one acceptance criterion")
    if not validations:
        raise PlanError(f"Task {task_id} requires at least one validation command")

    return {
        "id": task_id,
        "slug": slugify(title, f"task-{task_id}"),
        "title": title,
        "objective": objective,
        "requirement_ids": requirement_ids,
        "complexity": complexity,
        "atomicity_rationale": atomicity_rationale,
        "scope": normalize_scope(raw.get("scope"), f"Task {task_id} scope"),
        "dependencies": dependencies,
        "implementation_guidance": ensure_str_list(
            raw.get("implementation_guidance"), f"Task {task_id} implementation_guidance"
        ),
        "acceptance_criteria": acceptance,
        "validation_commands": validations,
        "provider": provider,
        "model_tier": tier,
        "reasoning_effort": effort,
        "allow_provider_fallback": bool(raw.get("allow_provider_fallback", True)),
        "related_task_reads": related,
        "max_attempts": max_attempts,
        "status": "pending",
        "attempts": 0,
        "functional_failures": 0,
        "rate_limit_events": 0,
        "current_route": None,
        "started_at": None,
        "completed_at": None,
        "last_error": None,
        "history": [],
        "changed_files": [],
        "validation_results": [],
        "result_file": None,
    }


def detect_cycles(tasks: list[dict[str, Any]]) -> None:
    graph = {task["id"]: task["dependencies"] for task in tasks}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visited:
            return
        if node in visiting:
            raise PlanError(f"Dependency cycle detected at task {node}")
        visiting.add(node)
        for dep in graph[node]:
            visit(dep)
        visiting.remove(node)
        visited.add(node)

    for task_id in graph:
        visit(task_id)


def validate_task_graph(tasks: list[dict[str, Any]]) -> None:
    ids = [task["id"] for task in tasks]
    if len(ids) != len(set(ids)):
        raise PlanError("Task ids must be unique")
    known = set(ids)
    for task in tasks:
        for dep in task["dependencies"]:
            if dep not in known:
                raise PlanError(f"Task {task['id']} depends on unknown task {dep}")
            if dep == task["id"]:
                raise PlanError(f"Task {task['id']} cannot depend on itself")
        for related in task["related_task_reads"]:
            if related not in known:
                raise PlanError(f"Task {task['id']} references unknown related task {related}")
    detect_cycles(tasks)


def request_part_coverage(
    request_parts: list[dict[str, str]],
    requirements: list[dict[str, Any]],
) -> dict[str, list[str]]:
    coverage = {request_part["id"]: [] for request_part in request_parts}
    known = set(coverage)
    for requirement in requirements:
        request_part_ids = requirement.get("request_part_ids", [])
        if not isinstance(request_part_ids, list):
            raise PlanError(
                f"Requirement {requirement.get('id', '?')} request_part_ids must be a list"
            )
        for request_part_id in request_part_ids:
            normalized = normalize_request_part_id(request_part_id)
            if normalized not in known:
                raise PlanError(
                    f"Requirement {requirement.get('id', '?')} references unknown request part {normalized}"
                )
            coverage[normalized].append(str(requirement.get("id", "?")))
    missing = [request_part_id for request_part_id, requirement_ids in coverage.items() if not requirement_ids]
    if missing:
        raise PlanError(
            "Request parts without requirement coverage: " + ", ".join(missing)
        )
    return coverage


def requirement_coverage(
    requirements: list[dict[str, Any]],
    tasks: list[dict[str, Any]],
) -> dict[str, list[str]]:
    coverage = {requirement["id"]: [] for requirement in requirements}
    known = set(coverage)
    for task in tasks:
        requirement_ids = task.get("requirement_ids", [])
        if not isinstance(requirement_ids, list) or not requirement_ids:
            raise PlanError(f"Task {task.get('id', '?')} must cover at least one requirement id")
        for requirement_id in requirement_ids:
            normalized = normalize_requirement_id(requirement_id)
            if normalized not in known:
                raise PlanError(
                    f"Task {task.get('id', '?')} references unknown requirement {normalized}"
                )
            coverage[normalized].append(str(task.get("id", "?")))
    missing = [requirement_id for requirement_id, task_ids in coverage.items() if not task_ids]
    if missing:
        raise PlanError(
            "Requirements without executable TODO coverage: " + ", ".join(missing)
        )
    return coverage


def render_request_part_list(request_parts: list[dict[str, str]]) -> str:
    return "\n".join(
        f"- **{item['id']}** {item['text']}" for item in request_parts
    )


def render_requirement_list(requirements: list[dict[str, Any]]) -> str:
    lines = []
    for item in requirements:
        request_parts = ", ".join(item.get("request_part_ids", [])) or "derived"
        lines.append(
            f"- **{item['id']}** [{item['priority']}; {item['source']}; request parts: {request_parts}] "
            f"{item['text']}"
        )
    return "\n".join(lines)

def render_analysis(manifest: dict[str, Any]) -> str:
    analysis = manifest["request_analysis"]
    request_source = manifest.get("request_source")
    if request_source:
        original_request = (
            f"The complete user-authored request is preserved in `{request_source['file']}` "
            f"(import mode: {request_source['import_mode']}; source name: "
            f"`{request_source['source_name']}`)."
        )
    else:
        original_request = "The request was supplied directly through the agent conversation."
    return f"""# Request and repository analysis — {manifest['title']}

## Original request

{original_request}

## Distinct request parts

{render_request_part_list(analysis['request_parts'])}

## Repository findings

{markdown_list(analysis['repository_findings'])}

## Research decision

{analysis['research_decision']}

## Research findings

{markdown_list(analysis['research_findings'])}

## Assumptions

{markdown_list(analysis['assumptions'])}

## Risks

{markdown_list(analysis['risks'])}

## Open questions

{markdown_list(analysis['open_questions'])}

## Decomposition strategy

{analysis['decomposition_strategy']}
"""


def render_plan_review(manifest: dict[str, Any]) -> str:
    review = manifest["plan_review"]
    checks = "\n".join(
        f"- {field.replace('_', ' ')}: **pass**" for field in REQUIRED_REVIEW_CHECKS
    )
    return f"""# Plan review — {manifest['title']}

- Status: **{review['status']}**
- Reviewer: **{review['reviewer']}**
- Review rounds: **{review['rounds']}**

## Quality checks

{checks}

## Review notes

{markdown_list(review['notes'])}

## Unresolved findings

{markdown_list(review['unresolved_findings'])}
"""


def render_plan(manifest: dict[str, Any]) -> str:
    request_parts = manifest["request_analysis"]["request_parts"]
    request_coverage = request_part_coverage(request_parts, manifest["requirements"])
    requirement_task_coverage = requirement_coverage(
        manifest["requirements"], manifest["tasks"]
    )
    request_coverage_lines = "\n".join(
        f"- **{request_part['id']}** -> {', '.join(request_coverage[request_part['id']])}"
        for request_part in request_parts
    )
    requirement_coverage_lines = "\n".join(
        f"- **{requirement['id']}** -> {', '.join(requirement_task_coverage[requirement['id']])}"
        for requirement in manifest["requirements"]
    )
    return f"""# {manifest['title']}

## Goal

{manifest['summary']}

## Request-parts inventory

{render_request_part_list(request_parts)}

## Request-part-to-requirement coverage

{request_coverage_lines}

## Requirements inventory

{render_requirement_list(manifest['requirements'])}

## Requirement-to-TODO coverage

{requirement_coverage_lines}

## Global constraints

{markdown_list(manifest['global_constraints'])}

## Planning evidence

{f"- Original user-authored request: `{manifest['request_source']['file']}`" if manifest.get('request_source') else "- Original request source: agent conversation"}
- Full request/repository analysis: `ANALYSIS.md`
- Independent plan review: `PLAN_REVIEW.md`
- Every request part maps to at least one requirement.
- Every requirement maps to at least one executable TODO, and every TODO maps back to requirements.
- Executable TODOs may be low, medium, or high complexity; extreme work must be split before plan creation.

## Execution policy

- Start automatically after validation: **{'yes' if manifest['autostart'] else 'no'}**
- Delete planning artifacts after successful summary: **{'yes' if manifest['cleanup_on_success'] else 'no'}**
- Default execution: sequential for write tasks; parallel only for read-only tasks or isolated worktrees.
- Each worker may read only its assigned task definition. Source files and test output relevant to that task are allowed.
- Reading another task definition requires a blocked dependency, ambiguity, or validation conflict and must be recorded.

Plan id: `{manifest['plan_id']}`  
Created: `{manifest['created_at']}`
"""

def render_task(task: dict[str, Any], plan_id: str) -> str:
    dependency_text = ", ".join(task["dependencies"]) or "none"
    related_text = ", ".join(task["related_task_reads"]) or "none"
    related_files = task.get("related_task_files", [])
    expected = task["scope"]["expected_files"]
    return f"""---
task_id: "{task['id']}"
plan_id: "{plan_id}"
status: "{task['status']}"
provider: "{task['provider']}"
model_tier: "{task['model_tier']}"
reasoning_effort: "{task['reasoning_effort']}"
complexity: "{task['complexity']}"
requirements: "{', '.join(task['requirement_ids'])}"
dependencies: "{dependency_text}"
allowed_related_task_reads: "{related_text}"
---

# {task['id']} — {task['title']}

## Objective

{task['objective']}

## Requirements covered

{markdown_list(task['requirement_ids'])}

## Complexity and atomicity

- Complexity: **{task['complexity']}**
- Why this is one executable TODO: {task['atomicity_rationale']}

## Isolation contract

This is the only planning definition file assigned to this worker. Do not open `PLAN.md`, `TODO.md`, `manifest.json`, `orchestrator.config.json`, result files, or any other file under this plan directory. You may read repository source, tests, build files, and runtime output that are relevant to this task.

Another task definition may be opened only when one of the explicitly allowed task ids above is necessary to resolve a blocked dependency, ambiguity, or validation conflict. Record the task id and reason in the completion report.

## In scope

{markdown_list(task['scope']['in'])}

## Out of scope

{markdown_list(task['scope']['out'])}

## Expected files

{markdown_list(expected)}

## Dependencies

{markdown_list(task['dependencies'])}

## Allowed related task definitions

{markdown_list(related_files)}

## Implementation guidance

{markdown_list(task['implementation_guidance'])}

## Acceptance criteria

{markdown_list(task['acceptance_criteria'])}

## Required validation

{chr(10).join(f'- `{command}`' for command in task['validation_commands'])}

## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, and any related task definition read with its reason. Do not edit planning files directly.
"""


def render_todo(manifest: dict[str, Any]) -> str:
    marker = {
        "pending": "[ ]",
        "in_progress": "[ ]",
        "completed": "[x]",
        "blocked": "[ ]",
    }
    lines = [f"# TODO — {manifest['title']}", ""]
    for task in manifest["tasks"]:
        suffix = ""
        if task["status"] == "in_progress":
            suffix = " _(in progress)_"
        elif task["status"] == "blocked":
            suffix = " _(blocked)_"
        lines.append(
            f"- {marker.get(task['status'], '[?]')} **{task['id']}** — {task['title']}{suffix}"
        )
    lines.append("")
    return "\n".join(lines)


def load_plan(plan_arg: str | Path) -> tuple[Path, dict[str, Any]]:
    raw = Path(plan_arg).expanduser()
    candidate = raw.parent if raw.name == MANIFEST else raw
    candidate = absolute_lexical(candidate)
    if candidate.is_symlink():
        raise PlanError("Plan directory must not be a symlink")
    sentinel = candidate / SENTINEL
    manifest_path = candidate / MANIFEST
    if not sentinel.is_file() or not manifest_path.is_file():
        raise PlanError(f"Not a valid plan workspace: {candidate}")
    sentinel_data = read_json(sentinel)
    manifest = read_json(manifest_path)
    if sentinel_data.get("plan_id") != manifest.get("plan_id"):
        raise PlanError("Plan sentinel and manifest do not match")
    repo_root = Path(manifest["repo_root"]).resolve()
    work_relative = Path(manifest["work_root"])
    reject_symlink_components(repo_root, work_relative, "Plan work root")
    expected_lexical = absolute_lexical(repo_root / work_relative / manifest["plan_id"])
    if expected_lexical != candidate:
        raise PlanError(f"Plan path mismatch: expected {expected_lexical}, got {candidate}")
    if expected_lexical.resolve() != candidate.resolve():
        raise PlanError("Plan path resolves outside its expected repository location")
    return candidate, manifest


def save_manifest(plan_dir: Path, manifest: dict[str, Any]) -> None:
    manifest["updated_at"] = now_utc()
    statuses = {task["status"] for task in manifest["tasks"]}
    if statuses == {"completed"}:
        manifest["state"] = "completed"
    elif "in_progress" in statuses:
        manifest["state"] = "running"
    elif "blocked" in statuses and not any(task["status"] == "pending" for task in manifest["tasks"]):
        manifest["state"] = "blocked"
    elif any(task["attempts"] > 0 for task in manifest["tasks"]):
        manifest["state"] = "running"
    else:
        manifest["state"] = "planned"
    atomic_write_json(plan_dir / MANIFEST, manifest)
    atomic_write_text(plan_dir / "TODO.md", render_todo(manifest))


def create_plan(
    repo_root: Path,
    spec: dict[str, Any],
    work_root: str,
    plan_id: str | None,
    request_file: str | Path | None = None,
    move_request: bool = False,
) -> Path:
    repo_root = repo_root.expanduser().resolve()
    if not repo_root.is_dir():
        raise PlanError(f"Repository root is not a directory: {repo_root}")
    if Path(work_root).is_absolute() or ".." in Path(work_root).parts:
        raise PlanError("work_root must be a repository-relative path")
    title = str(spec.get("title", "")).strip()
    summary = str(spec.get("summary", "")).strip()
    if not title or not summary:
        raise PlanError("Plan spec requires title and summary")

    request_analysis = normalize_request_analysis(spec.get("request_analysis"))
    known_request_part_ids = {
        item["id"] for item in request_analysis["request_parts"]
    }
    requirements = normalize_requirements(
        spec.get("requirements"), known_request_part_ids
    )
    request_part_coverage(request_analysis["request_parts"], requirements)
    known_requirement_ids = {item["id"] for item in requirements}
    plan_review = normalize_plan_review(spec.get("plan_review"))
    autostart = bool(spec.get("autostart", True))
    if autostart and request_analysis["open_questions"]:
        raise PlanError(
            "Autostart requires request_analysis.open_questions to be empty; "
            "resolve material questions through repository study, research, or explicit assumptions first"
        )

    raw_tasks = ensure_list(spec.get("tasks"), "tasks")
    if not raw_tasks:
        raise PlanError("Plan spec requires at least one task")
    tasks = [
        normalize_task(raw, index, known_requirement_ids)
        for index, raw in enumerate(raw_tasks)
    ]
    validate_task_graph(tasks)
    requirement_coverage(requirements, tasks)

    request_source_path: Path | None = None
    request_source: dict[str, Any] | None = None
    if request_file is not None:
        try:
            inspection = requestctl.inspect_request_file(request_file)
        except requestctl.RequestError as exc:
            raise PlanError(str(exc)) from exc
        if not inspection["ready"]:
            raise PlanError(
                "The request file has no meaningful user-authored instructions; "
                "fill it in and save it before creating the plan"
            )
        request_source_path = Path(inspection["path"])
        request_bytes = request_source_path.read_bytes()
        request_source = {
            "file": REQUEST_FILE,
            "source_name": request_source_path.name,
            "original_path": str(request_source_path),
            "import_mode": "move" if move_request else "copy",
            "source_removed": False,
            "sha256": hashlib.sha256(request_bytes).hexdigest(),
        }
    elif move_request:
        raise PlanError("--move-request requires --request-file")

    if plan_id:
        normalized_plan_id = slugify(plan_id)
    else:
        timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        normalized_plan_id = f"{timestamp}-{slugify(title)}"
    work_relative = Path(work_root)
    reject_symlink_components(repo_root, work_relative, "work_root")
    work_dir = repo_root / work_relative
    plan_dir = work_dir / normalized_plan_id
    if plan_dir.exists():
        raise PlanError(f"Plan directory already exists: {plan_dir}")
    plan_dir.mkdir(parents=True)
    (plan_dir / "tasks").mkdir()
    (plan_dir / "results").mkdir()
    (plan_dir / "logs").mkdir()

    created = now_utc()
    for task in tasks:
        task["file"] = f"tasks/{task['id']}-{task['slug']}.md"
    task_file_by_id = {task["id"]: task["file"] for task in tasks}
    for task in tasks:
        task["related_task_files"] = [task_file_by_id[item] for item in task["related_task_reads"]]

    manifest: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "plan_id": normalized_plan_id,
        "title": title,
        "summary": summary,
        "request_analysis": request_analysis,
        "requirements": requirements,
        "global_constraints": ensure_str_list(spec.get("global_constraints"), "global_constraints"),
        "plan_review": plan_review,
        "repo_root": str(repo_root),
        "work_root": Path(work_root).as_posix(),
        "state": "planned",
        "autostart": autostart,
        "cleanup_on_success": bool(spec.get("cleanup_on_success", True)),
        "language": str(spec.get("language", "auto")).strip() or "auto",
        "summary_status": "pending",
        "created_at": created,
        "updated_at": created,
        "tasks": tasks,
        "events": [{"at": created, "type": "plan_created"}],
    }
    if request_source is not None:
        manifest["request_source"] = request_source
        manifest["events"].append(
            {
                "at": created,
                "type": "request_imported",
                "file": REQUEST_FILE,
                "import_mode": request_source["import_mode"],
            }
        )
        shutil.copy2(request_source_path, plan_dir / REQUEST_FILE)

    atomic_write_json(
        plan_dir / SENTINEL,
        {"schema_version": SCHEMA_VERSION, "plan_id": normalized_plan_id, "repo_root": str(repo_root)},
    )
    atomic_write_text(plan_dir / "ANALYSIS.md", render_analysis(manifest))
    atomic_write_text(plan_dir / "PLAN.md", render_plan(manifest))
    atomic_write_text(plan_dir / "PLAN_REVIEW.md", render_plan_review(manifest))
    for task in tasks:
        atomic_write_text(plan_dir / task["file"], render_task(task, normalized_plan_id))
    atomic_write_json(plan_dir / CONFIG, default_config())
    save_manifest(plan_dir, manifest)
    errors = validate_plan(plan_dir, manifest)
    if errors:
        raise PlanError("Plan validation failed after creation:\n- " + "\n- ".join(errors))
    git_exclude = ensure_git_exclude(repo_root, work_root)
    if git_exclude:
        manifest["git_exclude"] = git_exclude
        save_manifest(plan_dir, manifest)
    if request_source_path is not None and move_request:
        destination = (plan_dir / REQUEST_FILE).resolve()
        if request_source_path.resolve() != destination:
            try:
                request_source_path.unlink()
                manifest["request_source"]["source_removed"] = True
                intake_directory = repo_root / work_relative / requestctl.INTAKE_DIRECTORY
                try:
                    if request_source_path.parent.resolve() == intake_directory.resolve():
                        request_source_path.parent.rmdir()
                except OSError:
                    pass
                append_event(manifest, "request_source_moved", file=REQUEST_FILE)
                save_manifest(plan_dir, manifest)
            except OSError as exc:
                manifest["request_source"]["move_error"] = str(exc)
                append_event(manifest, "request_source_move_failed", error=str(exc))
                save_manifest(plan_dir, manifest)
    return plan_dir


def validate_plan(plan_dir: Path, manifest: dict[str, Any] | None = None) -> list[str]:
    if manifest is None:
        plan_dir, manifest = load_plan(plan_dir)
    errors: list[str] = []
    schema_version = manifest.get("schema_version")
    if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        errors.append(f"Unsupported schema_version: {schema_version}")
    tasks = manifest.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        errors.append("Manifest must contain at least one task")
        return errors
    try:
        validate_task_graph(tasks)
    except PlanError as exc:
        errors.append(str(exc))

    if schema_version == 2:
        analysis: dict[str, Any] | None = None
        normalized_requirements: list[dict[str, Any]] = []
        try:
            analysis = normalize_request_analysis(manifest.get("request_analysis"))
            if manifest.get("autostart") and analysis["open_questions"]:
                errors.append("Autostart plan contains unresolved request_analysis.open_questions")
        except PlanError as exc:
            errors.append(str(exc))
        known_request_parts = (
            {item["id"] for item in analysis["request_parts"]}
            if analysis is not None
            else None
        )
        try:
            normalized_requirements = normalize_requirements(
                manifest.get("requirements"), known_request_parts
            )
        except PlanError as exc:
            errors.append(str(exc))
        if analysis is not None and normalized_requirements:
            try:
                request_part_coverage(
                    analysis["request_parts"], normalized_requirements
                )
            except PlanError as exc:
                errors.append(str(exc))
        try:
            normalize_plan_review(manifest.get("plan_review"))
        except PlanError as exc:
            errors.append(str(exc))

        known_requirements = {item["id"] for item in normalized_requirements}
        for task in tasks:
            task_id = task.get("id", "?")
            complexity = task.get("complexity")
            if complexity not in VALID_COMPLEXITIES:
                errors.append(f"Task {task_id}: invalid or missing complexity")
            elif complexity == "extreme":
                errors.append(
                    f"Task {task_id}: extreme complexity must be split into smaller executable TODOs"
                )
            rationale = task.get("atomicity_rationale")
            if not isinstance(rationale, str) or not rationale.strip():
                errors.append(f"Task {task_id}: missing atomicity_rationale")
            elif complexity == "high" and len(rationale.strip()) < 40:
                errors.append(f"Task {task_id}: high complexity atomicity_rationale is too shallow")
            requirement_ids = task.get("requirement_ids")
            if not isinstance(requirement_ids, list) or not requirement_ids:
                errors.append(f"Task {task_id}: missing requirement_ids")
            else:
                for value in requirement_ids:
                    try:
                        requirement_id = normalize_requirement_id(value)
                    except PlanError as exc:
                        errors.append(f"Task {task_id}: {exc}")
                        continue
                    if requirement_id not in known_requirements:
                        errors.append(f"Task {task_id}: unknown requirement {requirement_id}")
        if normalized_requirements:
            try:
                requirement_coverage(normalized_requirements, tasks)
            except PlanError as exc:
                errors.append(str(exc))
        for required_file in ("ANALYSIS.md", "PLAN_REVIEW.md"):
            if not (plan_dir / required_file).is_file():
                errors.append(f"Missing {required_file}")

    for task in tasks:
        task_id = task.get("id", "?")
        if task.get("status") not in VALID_STATUSES:
            errors.append(f"Task {task_id}: invalid status {task.get('status')!r}")
        path_value = task.get("file")
        if not isinstance(path_value, str):
            errors.append(f"Task {task_id}: missing task file")
            continue
        try:
            rel = checked_relative_path(path_value, f"Task {task_id} file")
        except PlanError as exc:
            errors.append(str(exc))
            continue
        task_path = plan_dir / rel
        if not task_path.is_file():
            errors.append(f"Task {task_id}: definition file missing: {rel}")
        if not task.get("acceptance_criteria"):
            errors.append(f"Task {task_id}: missing acceptance criteria")
        if not task.get("validation_commands"):
            errors.append(f"Task {task_id}: missing validation commands")
    request_source = manifest.get("request_source")
    if request_source is not None:
        if not isinstance(request_source, dict):
            errors.append("request_source must be an object")
        else:
            relative_request = request_source.get("file")
            if relative_request != REQUEST_FILE:
                errors.append(f"request_source.file must be {REQUEST_FILE}")
            request_path = plan_dir / REQUEST_FILE
            if not request_path.is_file() or request_path.is_symlink():
                errors.append(f"Missing or invalid {REQUEST_FILE}")
            else:
                expected_hash = request_source.get("sha256")
                actual_hash = hashlib.sha256(request_path.read_bytes()).hexdigest()
                if expected_hash != actual_hash:
                    errors.append(f"{REQUEST_FILE} hash does not match request_source.sha256")
                try:
                    if not requestctl.inspect_request_file(request_path)["ready"]:
                        errors.append(f"{REQUEST_FILE} contains no meaningful request")
                except requestctl.RequestError as exc:
                    errors.append(str(exc))
    if not (plan_dir / CONFIG).is_file():
        errors.append(f"Missing {CONFIG}")
    return errors


def render_audit(manifest: dict[str, Any]) -> str:
    schema_version = manifest.get("schema_version")
    lines = [
        f"# Plan quality audit — {manifest.get('title', 'unknown')}",
        "",
        f"- Schema: **{schema_version}**",
        f"- Tasks: **{len(manifest.get('tasks', []))}**",
    ]
    if schema_version == 2:
        request_parts = manifest.get("request_analysis", {}).get("request_parts", [])
        requirements = manifest.get("requirements", [])
        request_coverage = request_part_coverage(request_parts, requirements)
        requirement_task_coverage = requirement_coverage(
            requirements, manifest.get("tasks", [])
        )
        complexity_counts = {item: 0 for item in ("low", "medium", "high")}
        for task in manifest.get("tasks", []):
            complexity = task.get("complexity")
            if complexity in complexity_counts:
                complexity_counts[complexity] += 1
        lines.extend(
            [
                f"- Request parts: **{len(request_parts)}**",
                f"- Requirements: **{len(requirements)}**",
                f"- Review status: **{manifest.get('plan_review', {}).get('status', 'missing')}**",
                "",
                "## Request-part coverage",
                "",
            ]
        )
        for request_part in request_parts:
            lines.append(
                f"- **{request_part['id']}** -> {', '.join(request_coverage[request_part['id']])}"
            )
        lines.extend(["", "## Requirement coverage", ""])
        for requirement in requirements:
            lines.append(
                f"- **{requirement['id']}** -> "
                f"{', '.join(requirement_task_coverage[requirement['id']])}"
            )
        lines.extend(
            [
                "",
                "## Executable task complexity",
                "",
                f"- low: {complexity_counts['low']}",
                f"- medium: {complexity_counts['medium']}",
                f"- high: {complexity_counts['high']}",
                "- extreme: 0 (rejected by validation)",
            ]
        )
    else:
        lines.extend(["", "Legacy schema: plan quality traceability is not available."])
    return "\n".join(lines) + "\n"

def require_valid(plan_dir: Path, manifest: dict[str, Any]) -> None:
    errors = validate_plan(plan_dir, manifest)
    if errors:
        raise PlanError("Plan validation failed:\n- " + "\n- ".join(errors))


def find_task(manifest: dict[str, Any], task_id: str) -> dict[str, Any]:
    normalized = normalize_task_id(task_id)
    for task in manifest["tasks"]:
        if task["id"] == normalized:
            return task
    raise PlanError(f"Unknown task id: {task_id}")


def next_runnable_task(manifest: dict[str, Any]) -> dict[str, Any] | None:
    completed = {task["id"] for task in manifest["tasks"] if task["status"] == "completed"}
    for task in manifest["tasks"]:
        if task["status"] == "pending" and set(task["dependencies"]).issubset(completed):
            return task
    return None


def append_event(manifest: dict[str, Any], event_type: str, **details: Any) -> None:
    manifest.setdefault("events", []).append({"at": now_utc(), "type": event_type, **details})


def claim_task(plan_dir: Path, manifest: dict[str, Any], task_id: str, route: dict[str, Any] | None) -> dict[str, Any]:
    task = find_task(manifest, task_id)
    if task["status"] != "pending":
        raise PlanError(f"Task {task['id']} is not pending; current status: {task['status']}")
    completed = {item["id"] for item in manifest["tasks"] if item["status"] == "completed"}
    missing = [dep for dep in task["dependencies"] if dep not in completed]
    if missing:
        raise PlanError(f"Task {task['id']} has incomplete dependencies: {', '.join(missing)}")
    task["status"] = "in_progress"
    task["attempts"] += 1
    task["started_at"] = task["started_at"] or now_utc()
    task["current_route"] = route
    task["history"].append({"at": now_utc(), "event": "claimed", "route": route})
    append_event(manifest, "task_claimed", task_id=task["id"], route=route)
    save_manifest(plan_dir, manifest)
    return task


def complete_task(
    plan_dir: Path,
    manifest: dict[str, Any],
    task_id: str,
    report: dict[str, Any],
    result_file: str | None,
) -> dict[str, Any]:
    task = find_task(manifest, task_id)
    if task["status"] != "in_progress":
        raise PlanError(f"Task {task['id']} is not in progress")
    changed_files = report.get("changed_files", []) if isinstance(report, dict) else []
    if not isinstance(changed_files, list):
        changed_files = []
    clean_files: list[str] = []
    for item in changed_files:
        if isinstance(item, str) and item.strip():
            try:
                clean_files.append(checked_relative_path(item.strip(), "changed_files"))
            except PlanError:
                clean_files.append(item.strip())
    task["status"] = "completed"
    task["completed_at"] = now_utc()
    task["last_error"] = None
    task["changed_files"] = clean_files
    task["validation_results"] = report.get("validation_results", []) if isinstance(report, dict) else []
    task["result_file"] = result_file
    task["history"].append({"at": now_utc(), "event": "completed", "result_file": result_file})
    append_event(manifest, "task_completed", task_id=task["id"])
    save_manifest(plan_dir, manifest)
    return task


def fail_task(
    plan_dir: Path,
    manifest: dict[str, Any],
    task_id: str,
    reason: str,
    *,
    rate_limited: bool = False,
) -> dict[str, Any]:
    task = find_task(manifest, task_id)
    if task["status"] != "in_progress":
        raise PlanError(f"Task {task['id']} is not in progress")
    if rate_limited:
        task["rate_limit_events"] += 1
        event = "rate_limited"
    else:
        task["functional_failures"] += 1
        event = "failed"
    task["last_error"] = reason.strip()[:4000]
    if not rate_limited and task["functional_failures"] >= task["max_attempts"]:
        task["status"] = "blocked"
    else:
        task["status"] = "pending"
    task["history"].append({"at": now_utc(), "event": event, "reason": task["last_error"]})
    append_event(manifest, f"task_{event}", task_id=task["id"], reason=task["last_error"])
    save_manifest(plan_dir, manifest)
    return task


def reset_task(plan_dir: Path, manifest: dict[str, Any], task_id: str) -> dict[str, Any]:
    task = find_task(manifest, task_id)
    task["status"] = "pending"
    task["last_error"] = None
    task["current_route"] = None
    task["history"].append({"at": now_utc(), "event": "reset"})
    append_event(manifest, "task_reset", task_id=task["id"])
    save_manifest(plan_dir, manifest)
    return task


def mark_summary(plan_dir: Path, manifest: dict[str, Any], summary_file: str | None) -> None:
    if manifest.get("state") != "completed":
        raise PlanError("Cannot mark summary before every task is completed")
    manifest["summary_status"] = "generated"
    manifest["summary_file"] = summary_file
    manifest["summary_generated_at"] = now_utc()
    append_event(manifest, "summary_generated", summary_file=summary_file)
    save_manifest(plan_dir, manifest)


def deterministic_summary(manifest: dict[str, Any]) -> str:
    lines = [f"# Execution summary — {manifest['title']}", "", manifest["summary"], "", "## Completed tasks", ""]
    for task in manifest["tasks"]:
        files = ", ".join(task.get("changed_files") or []) or "not reported"
        lines.append(
            f"- **{task['id']} — {task['title']}**: {task['status']}; "
            f"attempts {task['attempts']}; functional failures {task['functional_failures']}; files: {files}."
        )
    lines.extend(["", "## Validation", ""])
    for task in manifest["tasks"]:
        commands = ", ".join(f"`{cmd}`" for cmd in task["validation_commands"])
        lines.append(f"- **{task['id']}**: {commands}")
    return "\n".join(lines) + "\n"


def cleanup_plan(plan_dir: Path, manifest: dict[str, Any], force: bool = False) -> None:
    if plan_dir.is_symlink():
        raise PlanError("Refusing to delete a symlinked plan directory")
    repo_root = Path(manifest["repo_root"]).resolve()
    work_relative = Path(manifest["work_root"])
    reject_symlink_components(repo_root, work_relative, "Plan work root")
    expected = absolute_lexical(repo_root / work_relative / manifest["plan_id"])
    if expected != absolute_lexical(plan_dir) or expected.resolve() != plan_dir.resolve():
        raise PlanError("Refusing cleanup because plan path does not match manifest")
    if not (plan_dir / SENTINEL).is_file():
        raise PlanError("Refusing cleanup without sentinel")
    if not force:
        if manifest.get("state") != "completed":
            raise PlanError("Refusing cleanup before all tasks are completed")
        if manifest.get("summary_status") != "generated":
            raise PlanError("Refusing cleanup before the final summary is generated")
    parent = plan_dir.parent
    shutil.rmtree(plan_dir)
    parent_removed = False
    try:
        parent.rmdir()
        parent_removed = True
    except OSError:
        pass
    if parent_removed:
        remove_git_exclude_entry(manifest.get("git_exclude"))


def parse_json_arg(value: str | None, default: Any) -> Any:
    if not value:
        return default
    candidate = Path(value)
    if candidate.is_file():
        return read_json(candidate)
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise PlanError(f"Expected JSON or a JSON file path: {value}") from exc


def command_create(args: argparse.Namespace) -> None:
    spec = read_json(Path(args.spec).expanduser().resolve())
    if not isinstance(spec, dict):
        raise PlanError("Plan spec root must be an object")
    plan_dir = create_plan(
        Path(args.repo_root),
        spec,
        args.work_root,
        args.plan_id,
        request_file=args.request_file,
        move_request=args.move_request,
    )
    print(plan_dir)


def command_validate(args: argparse.Namespace) -> None:
    plan_dir, manifest = load_plan(args.plan)
    errors = validate_plan(plan_dir, manifest)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
    print(f"VALID {plan_dir}")


def command_audit(args: argparse.Namespace) -> None:
    plan_dir, manifest = load_plan(args.plan)
    require_valid(plan_dir, manifest)
    print(render_audit(manifest), end="")


def command_status(args: argparse.Namespace) -> None:
    plan_dir, manifest = load_plan(args.plan)
    require_valid(plan_dir, manifest)
    if args.json:
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
    else:
        print(render_todo(manifest), end="")


def command_next(args: argparse.Namespace) -> None:
    plan_dir, manifest = load_plan(args.plan)
    require_valid(plan_dir, manifest)
    task = next_runnable_task(manifest)
    if task is None:
        raise SystemExit(3)
    payload = {**task, "absolute_file": str(plan_dir / task["file"]), "plan_dir": str(plan_dir)}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"{task['id']}\t{plan_dir / task['file']}")


def command_claim(args: argparse.Namespace) -> None:
    plan_dir, manifest = load_plan(args.plan)
    route = parse_json_arg(args.route, None)
    task = claim_task(plan_dir, manifest, args.task, route)
    print(json.dumps(task, ensure_ascii=False, indent=2))


def command_complete(args: argparse.Namespace) -> None:
    plan_dir, manifest = load_plan(args.plan)
    report = parse_json_arg(args.report, {})
    if not isinstance(report, dict):
        raise PlanError("Completion report must be a JSON object")
    result_file = args.result_file
    task = complete_task(plan_dir, manifest, args.task, report, result_file)
    print(json.dumps(task, ensure_ascii=False, indent=2))


def command_fail(args: argparse.Namespace) -> None:
    plan_dir, manifest = load_plan(args.plan)
    task = fail_task(plan_dir, manifest, args.task, args.reason, rate_limited=args.rate_limited)
    print(json.dumps(task, ensure_ascii=False, indent=2))


def command_reset(args: argparse.Namespace) -> None:
    plan_dir, manifest = load_plan(args.plan)
    task = reset_task(plan_dir, manifest, args.task)
    print(json.dumps(task, ensure_ascii=False, indent=2))


def command_summary(args: argparse.Namespace) -> None:
    _plan_dir, manifest = load_plan(args.plan)
    print(deterministic_summary(manifest), end="")


def command_mark_summary(args: argparse.Namespace) -> None:
    plan_dir, manifest = load_plan(args.plan)
    mark_summary(plan_dir, manifest, args.summary_file)
    print("SUMMARY_MARKED")


def command_cleanup(args: argparse.Namespace) -> None:
    plan_dir, manifest = load_plan(args.plan)
    cleanup_plan(plan_dir, manifest, force=args.force)
    print(f"CLEANED {plan_dir}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create", help="Create a plan workspace from a JSON spec")
    create.add_argument("--repo-root", default=".")
    create.add_argument("--spec", required=True)
    create.add_argument("--work-root", default=WORK_ROOT_DEFAULT)
    create.add_argument("--plan-id")
    create.add_argument(
        "--request-file",
        help="Preserve a validated user-authored request as REQUEST.md in the plan workspace",
    )
    create.add_argument(
        "--move-request",
        action="store_true",
        help="Remove the source request file after it is safely copied into the plan workspace",
    )
    create.set_defaults(func=command_create)

    validate = sub.add_parser("validate", help="Validate a plan workspace")
    validate.add_argument("--plan", required=True)
    validate.set_defaults(func=command_validate)

    audit = sub.add_parser("audit", help="Show requirement coverage and plan-quality evidence")
    audit.add_argument("--plan", required=True)
    audit.set_defaults(func=command_audit)

    status = sub.add_parser("status", help="Show plan status")
    status.add_argument("--plan", required=True)
    status.add_argument("--json", action="store_true")
    status.set_defaults(func=command_status)

    next_cmd = sub.add_parser("next", help="Return the next runnable task")
    next_cmd.add_argument("--plan", required=True)
    next_cmd.add_argument("--json", action="store_true")
    next_cmd.set_defaults(func=command_next)

    claim = sub.add_parser("claim", help="Mark a task in progress")
    claim.add_argument("--plan", required=True)
    claim.add_argument("--task", required=True)
    claim.add_argument("--route", help="JSON object or JSON file")
    claim.set_defaults(func=command_claim)

    complete = sub.add_parser("complete", help="Mark a task completed")
    complete.add_argument("--plan", required=True)
    complete.add_argument("--task", required=True)
    complete.add_argument("--report", help="JSON object or JSON file")
    complete.add_argument("--result-file")
    complete.set_defaults(func=command_complete)

    fail = sub.add_parser("fail", help="Return a task to pending or block it")
    fail.add_argument("--plan", required=True)
    fail.add_argument("--task", required=True)
    fail.add_argument("--reason", required=True)
    fail.add_argument("--rate-limited", action="store_true")
    fail.set_defaults(func=command_fail)

    reset = sub.add_parser("reset", help="Reset a task to pending")
    reset.add_argument("--plan", required=True)
    reset.add_argument("--task", required=True)
    reset.set_defaults(func=command_reset)

    summary = sub.add_parser("summary", help="Generate a deterministic summary")
    summary.add_argument("--plan", required=True)
    summary.set_defaults(func=command_summary)

    mark = sub.add_parser("mark-summary", help="Record that final summary was generated")
    mark.add_argument("--plan", required=True)
    mark.add_argument("--summary-file")
    mark.set_defaults(func=command_mark_summary)

    cleanup = sub.add_parser("cleanup", help="Safely delete planning artifacts only")
    cleanup.add_argument("--plan", required=True)
    cleanup.add_argument("--force", action="store_true")
    cleanup.set_defaults(func=command_cleanup)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
        return 0
    except PlanError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
