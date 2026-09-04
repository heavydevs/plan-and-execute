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

SCHEMA_VERSION = 4
SUPPORTED_SCHEMA_VERSIONS = {1, 2, 3, 4}
SENTINEL = ".orchestrator-plan"
MANIFEST = "manifest.json"
CONFIG = "orchestrator.config.json"
WORK_ROOT_DEFAULT = ".ai-work"
REQUEST_FILE = "REQUEST.md"
GLOBAL_CONTEXT_FILE = "CONTEXT.md"
CONTEXT_DIRECTORY = "contexts"
LEARNING_DIRECTORY = "learnings"
VALID_PROVIDERS = {"auto", "claude", "codex", "gemini", "qwen", "kimi", "trae"}
VALID_TIERS = {"economy", "standard", "strong", "max"}
VALID_EFFORTS = {"low", "medium", "high", "xhigh", "max"}
VALID_STATUSES = {"pending", "in_progress", "completed", "blocked"}
VALID_SUBTASK_STATUSES = {"pending", "in_progress", "completed"}
VALID_COMPLEXITIES = {"low", "medium", "high", "extreme"}
VALID_REQUIREMENT_SOURCES = {"user", "repository", "research", "inferred"}
VALID_PRIORITIES = {"must", "should", "could"}
REQUIRED_REVIEW_CHECKS = (
    "coverage_complete",
    "tasks_atomic",
    "dependencies_valid",
    "validations_sufficient",
)
CONTEXT_REVIEW_CHECK = "contexts_minimal"
CONTEXT_BOUNDARY_REVIEW_CHECK = "context_boundaries_sound"
VALID_CONTEXT_DECISIONS = {"create", "omit"}
VALID_CONTEXT_KINDS = {"fact", "constraint", "decision", "interface", "validation"}
VALID_LEARNING_KINDS = {"code", "procedure", "decision", "pitfall", "validation"}
MAX_GLOBAL_CONTEXT_ITEMS = 8
MAX_SCOPED_CONTEXTS = 8
MAX_SCOPED_CONTEXT_ITEMS = 8
MAX_TOTAL_CONTEXT_ITEMS = 24
MAX_CONTEXT_TEXT_CHARS = 280
MAX_CONTEXT_NECESSITY_CHARS = 360
MAX_CONTEXT_RATIONALE_CHARS = 500
MAX_CONTEXT_SOURCE_REFS = 4
MAX_CONTEXT_SOURCE_REF_CHARS = 160
MAX_CONTEXT_FILE_CHARS = 3200
MAX_TASK_SHARED_CONTEXT_ITEMS = 8
MAX_TASK_BOUNDARY_TEXT_CHARS = 900
MAX_TASK_BOUNDARY_ITEM_CHARS = 240
MAX_SUBTASKS_PER_TASK = 24
MAX_SUBTASK_TITLE_CHARS = 180
MAX_SUBTASK_OBJECTIVE_CHARS = 600
MAX_LEARNING_TARGETS_PER_TASK = 12
MAX_LEARNING_TOPICS = 8
MAX_LEARNING_TOPIC_CHARS = 120
MAX_REUSABLE_LEARNINGS = 8
MAX_LEARNING_GUIDANCE_CHARS = 420
MAX_LEARNING_REFERENCES = 6
MAX_LEARNING_FILE_CHARS = 4200


class PlanError(RuntimeError):
    """Raised when a plan workspace is invalid or an operation is unsafe."""


def review_checks_for_schema(schema_version: Any) -> tuple[str, ...]:
    try:
        version = int(schema_version)
    except (TypeError, ValueError):
        version = 0
    checks = list(REQUIRED_REVIEW_CHECKS)
    if version >= 3:
        checks.append(CONTEXT_REVIEW_CHECK)
    if version >= 4:
        checks.append(CONTEXT_BOUNDARY_REVIEW_CHECK)
    return tuple(checks)


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


def normalize_subtask_id(value: Any, index: int | None = None) -> str:
    if value is None or not str(value).strip():
        if index is None:
            raise PlanError("Subtask id is required")
        return f"S{index + 1:03d}"
    text = str(value).strip().upper()
    if text.isdigit():
        return f"S{int(text):03d}"
    if re.fullmatch(r"S\d+", text):
        return f"S{int(text[1:]):03d}"
    if not re.fullmatch(r"[A-Z][A-Z0-9_-]{0,31}", text):
        raise PlanError(f"Invalid subtask id: {value!r}")
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
                f"requirements[{index}] must be an object with explicit request_part_ids in schema v2+"
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

def normalize_plan_review(raw: Any, schema_version: int = SCHEMA_VERSION) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise PlanError("plan_review must be an object produced by a separate plan-review pass")
    status = str(raw.get("status", "")).strip().lower()
    if status != "approved":
        raise PlanError("plan_review.status must be 'approved' before execution can start")
    rounds = int(raw.get("rounds", 0))
    if rounds < 1:
        raise PlanError("plan_review.rounds must be at least 1")
    checks: dict[str, bool] = {}
    for field in review_checks_for_schema(schema_version):
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


def ensure_context_line(
    value: Any,
    field: str,
    *,
    minimum: int = 1,
    maximum: int,
) -> str:
    text = ensure_text(value, field)
    if "\n" in text or "\r" in text:
        raise PlanError(f"{field} must be one concise line")
    if len(text) < minimum:
        raise PlanError(f"{field} is too shallow; provide a specific, evidence-backed statement")
    if len(text) > maximum:
        raise PlanError(f"{field} exceeds the {maximum}-character concision limit")
    if text.startswith(("#", "- ", "* ", "+ ")):
        raise PlanError(f"{field} must be plain text, not preformatted Markdown")
    return text


def normalize_context_item_id(value: Any, fallback: str, field: str) -> str:
    text = str(value or fallback).strip().upper()
    if not re.fullmatch(r"[A-Z][A-Z0-9_-]{0,23}", text):
        raise PlanError(f"{field} has an invalid context item id: {value!r}")
    return text


def normalize_context_item(raw: Any, field: str, fallback_id: str) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise PlanError(f"{field} must be an object")
    unknown = set(raw) - {"id", "kind", "text", "necessity", "source_refs"}
    if unknown:
        raise PlanError(f"{field} contains unsupported fields: {', '.join(sorted(unknown))}")
    item_id = normalize_context_item_id(raw.get("id"), fallback_id, field)
    kind = str(raw.get("kind", "")).strip().lower()
    if kind not in VALID_CONTEXT_KINDS:
        raise PlanError(
            f"{field}.kind must be one of {sorted(VALID_CONTEXT_KINDS)}"
        )
    text = ensure_context_line(
        raw.get("text"),
        f"{field}.text",
        minimum=15,
        maximum=MAX_CONTEXT_TEXT_CHARS,
    )
    necessity = ensure_context_line(
        raw.get("necessity"),
        f"{field}.necessity",
        minimum=30,
        maximum=MAX_CONTEXT_NECESSITY_CHARS,
    )
    raw_sources = ensure_list(raw.get("source_refs"), f"{field}.source_refs")
    if not raw_sources:
        raise PlanError(f"{field}.source_refs must ground the context item in evidence")
    if len(raw_sources) > MAX_CONTEXT_SOURCE_REFS:
        raise PlanError(
            f"{field}.source_refs may contain at most {MAX_CONTEXT_SOURCE_REFS} entries"
        )
    source_refs: list[str] = []
    seen_sources: set[str] = set()
    for index, source in enumerate(raw_sources):
        normalized = ensure_context_line(
            source,
            f"{field}.source_refs[{index}]",
            minimum=2,
            maximum=MAX_CONTEXT_SOURCE_REF_CHARS,
        )
        if "`" in normalized:
            raise PlanError(f"{field}.source_refs[{index}] must not contain backticks")
        folded = normalized.casefold()
        if folded in seen_sources:
            raise PlanError(f"{field}.source_refs contains a duplicate: {normalized!r}")
        seen_sources.add(folded)
        source_refs.append(normalized)
    return {
        "id": item_id,
        "kind": kind,
        "text": text,
        "necessity": necessity,
        "source_refs": source_refs,
    }


def normalize_execution_context(raw: Any, tasks: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise PlanError(
            "execution_context must explicitly decide whether concise shared context is needed"
        )
    unknown = set(raw) - {"global", "scoped"}
    if unknown:
        raise PlanError(
            "execution_context contains unsupported fields: " + ", ".join(sorted(unknown))
        )

    global_raw = raw.get("global")
    if not isinstance(global_raw, dict):
        raise PlanError("execution_context.global must be an object")
    unknown_global = set(global_raw) - {"decision", "rationale", "items", "file"}
    if unknown_global:
        raise PlanError(
            "execution_context.global contains unsupported fields: "
            + ", ".join(sorted(unknown_global))
        )
    decision = str(global_raw.get("decision", "")).strip().lower()
    if decision not in VALID_CONTEXT_DECISIONS:
        raise PlanError(
            f"execution_context.global.decision must be one of {sorted(VALID_CONTEXT_DECISIONS)}"
        )
    rationale = ensure_context_line(
        global_raw.get("rationale"),
        "execution_context.global.rationale",
        minimum=30,
        maximum=MAX_CONTEXT_RATIONALE_CHARS,
    )
    global_raw_items = ensure_list(
        global_raw.get("items"), "execution_context.global.items"
    )
    if decision == "omit" and global_raw_items:
        raise PlanError(
            "execution_context.global.items must be empty when the global context file is omitted"
        )
    if decision == "create" and not global_raw_items:
        raise PlanError(
            "execution_context.global.items must contain at least one universal item when CONTEXT.md is created"
        )
    if len(global_raw_items) > MAX_GLOBAL_CONTEXT_ITEMS:
        raise PlanError(
            f"CONTEXT.md may contain at most {MAX_GLOBAL_CONTEXT_ITEMS} items"
        )
    global_items = [
        normalize_context_item(item, f"execution_context.global.items[{index}]", f"G{index + 1:03d}")
        for index, item in enumerate(global_raw_items)
    ]
    global_item_ids = [item["id"] for item in global_items]
    if len(global_item_ids) != len(set(global_item_ids)):
        raise PlanError("execution_context.global.items contains duplicate ids")
    expected_global_file = GLOBAL_CONTEXT_FILE if decision == "create" else None
    if "file" in global_raw and global_raw.get("file") != expected_global_file:
        raise PlanError(
            f"execution_context.global.file must be {expected_global_file!r}"
        )

    task_ids = [str(task.get("id")) for task in tasks]
    known_task_ids = set(task_ids)
    scoped_raw = ensure_list(raw.get("scoped"), "execution_context.scoped")
    if len(scoped_raw) > MAX_SCOPED_CONTEXTS:
        raise PlanError(
            f"execution_context.scoped may contain at most {MAX_SCOPED_CONTEXTS} files"
        )
    scoped: list[dict[str, Any]] = []
    seen_context_ids: set[str] = set()
    all_texts: set[str] = set()
    for item in global_items:
        folded = item["text"].casefold()
        if folded in all_texts:
            raise PlanError(f"Duplicate context text: {item['text']!r}")
        all_texts.add(folded)

    for index, context_raw in enumerate(scoped_raw):
        field = f"execution_context.scoped[{index}]"
        if not isinstance(context_raw, dict):
            raise PlanError(f"{field} must be an object")
        unknown_scoped = set(context_raw) - {"id", "title", "rationale", "task_ids", "items", "file"}
        if unknown_scoped:
            raise PlanError(
                f"{field} contains unsupported fields: {', '.join(sorted(unknown_scoped))}"
            )
        context_id = str(context_raw.get("id", "")).strip().lower()
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,39}", context_id):
            raise PlanError(
                f"{field}.id must be a lowercase kebab-case file identifier"
            )
        if context_id in seen_context_ids:
            raise PlanError(f"Duplicate scoped context id: {context_id}")
        seen_context_ids.add(context_id)
        title = ensure_context_line(
            context_raw.get("title"), f"{field}.title", minimum=3, maximum=100
        )
        context_rationale = ensure_context_line(
            context_raw.get("rationale"),
            f"{field}.rationale",
            minimum=30,
            maximum=MAX_CONTEXT_RATIONALE_CHARS,
        )
        raw_task_ids = ensure_list(context_raw.get("task_ids"), f"{field}.task_ids")
        normalized_task_ids: list[str] = []
        seen_task_ids: set[str] = set()
        for task_value in raw_task_ids:
            task_id = normalize_task_id(task_value)
            if task_id not in known_task_ids:
                raise PlanError(f"{field} references unknown task {task_id}")
            if task_id in seen_task_ids:
                raise PlanError(f"{field}.task_ids contains duplicate task {task_id}")
            seen_task_ids.add(task_id)
            normalized_task_ids.append(task_id)
        if len(normalized_task_ids) < 2:
            raise PlanError(
                f"{field} must serve at least two TODOs; put single-task context in that task definition"
            )
        if set(normalized_task_ids) == known_task_ids:
            raise PlanError(
                f"{field} applies to every TODO and belongs in execution_context.global instead"
            )
        raw_items = ensure_list(context_raw.get("items"), f"{field}.items")
        if not raw_items:
            raise PlanError(f"{field}.items must not be empty")
        if len(raw_items) > MAX_SCOPED_CONTEXT_ITEMS:
            raise PlanError(
                f"{field}.items may contain at most {MAX_SCOPED_CONTEXT_ITEMS} items"
            )
        items = [
            normalize_context_item(value, f"{field}.items[{item_index}]", f"C{item_index + 1:03d}")
            for item_index, value in enumerate(raw_items)
        ]
        seen_item_ids: set[str] = set()
        for context_item in items:
            if context_item["id"] in seen_item_ids:
                raise PlanError(
                    f"{field}.items contains duplicate id {context_item['id']}"
                )
            seen_item_ids.add(context_item["id"])
            folded = context_item["text"].casefold()
            if folded in all_texts:
                raise PlanError(
                    f"Context text is duplicated across files: {context_item['text']!r}"
                )
            all_texts.add(folded)
        expected_file = f"{CONTEXT_DIRECTORY}/{context_id}.md"
        if "file" in context_raw and context_raw.get("file") != expected_file:
            raise PlanError(f"{field}.file must be {expected_file!r}")
        scoped.append(
            {
                "id": context_id,
                "title": title,
                "rationale": context_rationale,
                "task_ids": normalized_task_ids,
                "items": items,
                "file": expected_file,
            }
        )

    total_items = len(global_items) + sum(len(item["items"]) for item in scoped)
    if total_items > MAX_TOTAL_CONTEXT_ITEMS:
        raise PlanError(
            f"Execution context contains {total_items} items; maximum is {MAX_TOTAL_CONTEXT_ITEMS}"
        )
    normalized = {
        "global": {
            "decision": decision,
            "rationale": rationale,
            "items": global_items,
            "file": GLOBAL_CONTEXT_FILE if decision == "create" else None,
        },
        "scoped": scoped,
    }
    for context in [normalized["global"], *scoped]:
        if context.get("file"):
            content = (
                render_global_context(normalized)
                if context.get("file") == GLOBAL_CONTEXT_FILE
                else render_scoped_context(context)
            )
            if len(content) > MAX_CONTEXT_FILE_CHARS:
                raise PlanError(
                    f"Context file {context['file']} exceeds the {MAX_CONTEXT_FILE_CHARS}-character limit"
                )
    return normalized


def expected_task_context_files(
    tasks: list[dict[str, Any]], execution_context: dict[str, Any]
) -> dict[str, list[str]]:
    mapping = {str(task["id"]): [] for task in tasks}
    if execution_context["global"]["decision"] == "create":
        for task_id in mapping:
            mapping[task_id].append(GLOBAL_CONTEXT_FILE)
    for scoped in execution_context["scoped"]:
        for task_id in scoped["task_ids"]:
            mapping[task_id].append(scoped["file"])
    return mapping


def assign_context_files(
    tasks: list[dict[str, Any]], execution_context: dict[str, Any]
) -> None:
    mapping = expected_task_context_files(tasks, execution_context)
    for task in tasks:
        task["context_files"] = mapping[str(task["id"])]


def context_reference(work_root: str, plan_id: str, relative: str) -> str:
    return (Path(work_root) / plan_id / relative).as_posix()


def render_context_item(item: dict[str, Any]) -> str:
    sources = ", ".join(f"`{source}`" for source in item["source_refs"])
    label = "source" if len(item["source_refs"]) == 1 else "sources"
    return (
        f"- **{item['id']}** `{item['kind']}` — {item['text']} "
        f"_({label}: {sources})_"
    )


def render_global_context(execution_context: dict[str, Any]) -> str:
    items = execution_context["global"]["items"]
    return (
        "# Execution context\n\n"
        "Applies to every executable TODO. Treat only these items as shared invariants; "
        "they do not add scope.\n\n"
        + "\n".join(render_context_item(item) for item in items)
        + "\n"
    )


def render_scoped_context(context: dict[str, Any]) -> str:
    tasks = ", ".join(f"`{task_id}`" for task_id in context["task_ids"])
    return (
        f"# {context['title']}\n\n"
        f"Applies only to TODOs {tasks}. Do not use this file for other TODOs.\n\n"
        + "\n".join(render_context_item(item) for item in context["items"])
        + "\n"
    )


def render_execution_context_strategy(execution_context: dict[str, Any]) -> str:
    global_context = execution_context["global"]
    lines = [
        f"- Global context decision: **{global_context['decision']}**",
        f"- Rationale: {global_context['rationale']}",
    ]
    if global_context["decision"] == "create":
        lines.append(
            f"- `{GLOBAL_CONTEXT_FILE}`: {len(global_context['items'])} universal item(s)"
        )
    else:
        lines.append(f"- `{GLOBAL_CONTEXT_FILE}` is intentionally omitted.")
    if execution_context["scoped"]:
        lines.append("- Scoped context files:")
        for context in execution_context["scoped"]:
            tasks = ", ".join(context["task_ids"])
            lines.append(
                f"  - `{context['file']}` -> TODOs {tasks}: {context['rationale']}"
            )
    else:
        lines.append("- No scoped context files are needed.")
    return "\n".join(lines)


def write_context_artifacts(plan_dir: Path, execution_context: dict[str, Any]) -> None:
    if execution_context["global"]["decision"] == "create":
        atomic_write_text(plan_dir / GLOBAL_CONTEXT_FILE, render_global_context(execution_context))
    if execution_context["scoped"]:
        context_dir = plan_dir / CONTEXT_DIRECTORY
        context_dir.mkdir()
        for context in execution_context["scoped"]:
            atomic_write_text(plan_dir / context["file"], render_scoped_context(context))


def validate_context_artifacts(
    plan_dir: Path,
    manifest: dict[str, Any],
    tasks: list[dict[str, Any]],
) -> list[str]:
    errors: list[str] = []
    try:
        execution_context = normalize_execution_context(
            manifest.get("execution_context"), tasks
        )
    except PlanError as exc:
        return [str(exc)]
    if manifest.get("execution_context") != execution_context:
        errors.append("manifest execution_context is not in canonical normalized form")

    expected_contents: dict[str, str] = {}
    if execution_context["global"]["decision"] == "create":
        expected_contents[GLOBAL_CONTEXT_FILE] = render_global_context(execution_context)
    for context in execution_context["scoped"]:
        expected_contents[context["file"]] = render_scoped_context(context)

    global_path = plan_dir / GLOBAL_CONTEXT_FILE
    if execution_context["global"]["decision"] == "omit" and global_path.exists():
        errors.append(f"Unexpected {GLOBAL_CONTEXT_FILE}; the plan explicitly omitted global context")

    for relative, expected in expected_contents.items():
        path = plan_dir / relative
        if path.is_symlink() or not path.is_file():
            errors.append(f"Missing or invalid context file: {relative}")
            continue
        try:
            actual = path.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"Cannot read context file {relative}: {exc}")
            continue
        if actual != expected:
            errors.append(f"Context file does not match manifest rendering: {relative}")

    expected_scoped = {
        path for path in expected_contents if path.startswith(f"{CONTEXT_DIRECTORY}/")
    }
    context_dir = plan_dir / CONTEXT_DIRECTORY
    if expected_scoped:
        if context_dir.is_symlink() or not context_dir.is_dir():
            errors.append(f"Missing or invalid {CONTEXT_DIRECTORY}/ directory")
        else:
            actual_scoped: set[str] = set()
            for child in context_dir.iterdir():
                relative = child.relative_to(plan_dir).as_posix()
                if child.is_symlink() or not child.is_file():
                    errors.append(f"Unexpected non-file context artifact: {relative}")
                else:
                    actual_scoped.add(relative)
            for unexpected in sorted(actual_scoped - expected_scoped):
                errors.append(f"Unexpected scoped context file: {unexpected}")
    elif context_dir.exists():
        errors.append(f"Unexpected {CONTEXT_DIRECTORY}/ directory; no scoped context is defined")

    mapping = expected_task_context_files(tasks, execution_context)
    all_context_files = set(expected_contents)
    work_root = str(manifest.get("work_root", WORK_ROOT_DEFAULT))
    plan_id = str(manifest.get("plan_id", ""))
    for task in tasks:
        task_id = str(task.get("id", "?"))
        expected_files = mapping.get(task_id, [])
        actual_files = task.get("context_files")
        if actual_files != expected_files:
            errors.append(
                f"Task {task_id}: context_files must be exactly {expected_files!r}"
            )
        task_file = task.get("file")
        if not isinstance(task_file, str):
            continue
        task_path = plan_dir / task_file
        if not task_path.is_file():
            continue
        try:
            task_text = task_path.read_text(encoding="utf-8")
        except OSError:
            continue
        for relative in all_context_files:
            reference = context_reference(work_root, plan_id, relative)
            marker = f"`{reference}`"
            if relative in expected_files and marker not in task_text:
                errors.append(
                    f"Task {task_id}: definition does not reference assigned context {relative}"
                )
            if relative not in expected_files and marker in task_text:
                errors.append(
                    f"Task {task_id}: definition references unassigned context {relative}"
                )
    return errors


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False, newline="\n"
    ) as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
        tmp = Path(handle.name)
    os.replace(tmp, path)
    # os.replace() makes the rename atomic, while syncing the containing
    # directory makes the new name durable across a host crash where the
    # platform supports directory fsync.
    try:
        descriptor = os.open(path.parent, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    except OSError:
        pass
    finally:
        os.close(descriptor)


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
            "jitter_ratio": 0.1,
            "release_lease_while_waiting": True,
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
            "exclude_dynamic_system_prompt_sections": True,
            "max_budget_usd": 0,
            "max_turns": 0,
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
            "model_verbosity": "low",
            "model_reasoning_summary": "none",
            "max_effort_by_tier": {
                "economy": "medium",
                "standard": "high",
                "strong": "xhigh",
                "max": "xhigh",
            },
            "extra_args": [],
        },
        "gemini": {
            "command": "gemini",
            "models": {
                "economy": "default",
                "standard": "default",
                "strong": "default",
                "max": "default",
            },
            "approval_mode": "yolo",
            "summary_approval_mode": "plan",
            "disable_extensions": True,
            "max_effort_by_tier": {
                "economy": "medium",
                "standard": "high",
                "strong": "max",
                "max": "max",
            },
            "extra_args": [],
        },
        "qwen": {
            "command": "qwen",
            "models": {
                "economy": "default",
                "standard": "default",
                "strong": "default",
                "max": "default",
            },
            "approval_mode": "yolo",
            "safe_mode": True,
            "sandbox": False,
            "max_effort_by_tier": {
                "economy": "medium",
                "standard": "high",
                "strong": "max",
                "max": "max",
            },
            "extra_args": [],
        },
        "kimi": {
            "command": "kimi",
            "models": {
                "economy": "default",
                "standard": "default",
                "strong": "default",
                "max": "default",
            },
            "permission_mode": "auto",
            "summary_permission_mode": "plan",
            "retry_exit_codes": [75],
            "max_effort_by_tier": {
                "economy": "medium",
                "standard": "high",
                "strong": "max",
                "max": "max",
            },
            "extra_args": [],
        },
        "trae": {
            "command": "trae-cli",
            "models": {
                "economy": "default",
                "standard": "default",
                "strong": "default",
                "max": "default",
            },
            "model_provider": "",
            "max_effort_by_tier": {
                "economy": "medium",
                "standard": "high",
                "strong": "max",
                "max": "max",
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


def normalize_context_boundary(raw: Any, task_id: str) -> dict[str, Any]:
    field = f"Task {task_id} context_boundary"
    if not isinstance(raw, dict):
        raise PlanError(
            f"{field} must be an object that explains why the TODO deserves one fresh worker context"
        )
    shared_context = ensure_str_list(raw.get("shared_context"), f"{field}.shared_context")
    if not shared_context:
        raise PlanError(f"{field}.shared_context must contain at least one cohesive context item")
    if len(shared_context) > MAX_TASK_SHARED_CONTEXT_ITEMS:
        raise PlanError(
            f"{field}.shared_context may contain at most {MAX_TASK_SHARED_CONTEXT_ITEMS} items"
        )
    for item in shared_context:
        if len(item) > MAX_TASK_BOUNDARY_ITEM_CHARS:
            raise PlanError(
                f"{field}.shared_context items may not exceed {MAX_TASK_BOUNDARY_ITEM_CHARS} characters"
            )
    why_one_todo = ensure_text(raw.get("why_one_todo"), f"{field}.why_one_todo")
    if len(why_one_todo) < 40:
        raise PlanError(
            f"{field}.why_one_todo must substantively explain why retained context helps the whole TODO"
        )
    if len(why_one_todo) > MAX_TASK_BOUNDARY_TEXT_CHARS:
        raise PlanError(
            f"{field}.why_one_todo may not exceed {MAX_TASK_BOUNDARY_TEXT_CHARS} characters"
        )
    separate_from = ensure_str_list(raw.get("separate_from"), f"{field}.separate_from")
    if len(separate_from) > MAX_TASK_SHARED_CONTEXT_ITEMS:
        raise PlanError(
            f"{field}.separate_from may contain at most {MAX_TASK_SHARED_CONTEXT_ITEMS} items"
        )
    for item in separate_from:
        if len(item) > MAX_TASK_BOUNDARY_ITEM_CHARS:
            raise PlanError(
                f"{field}.separate_from items may not exceed {MAX_TASK_BOUNDARY_ITEM_CHARS} characters"
            )
    return {
        "shared_context": shared_context,
        "why_one_todo": why_one_todo,
        "separate_from": separate_from,
    }


def normalize_subtasks(raw: Any, task_id: str) -> list[dict[str, Any]]:
    items = ensure_list(raw, f"Task {task_id} subtasks")
    if not items:
        raise PlanError(f"Task {task_id} requires at least one resumable subtask")
    if len(items) > MAX_SUBTASKS_PER_TASK:
        raise PlanError(
            f"Task {task_id} may contain at most {MAX_SUBTASKS_PER_TASK} subtasks"
        )
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(items):
        if isinstance(item, str):
            raw_item: dict[str, Any] = {"title": item}
        elif isinstance(item, dict):
            raw_item = item
        else:
            raise PlanError(f"Task {task_id} subtasks[{index}] must be a string or object")
        subtask_id = normalize_subtask_id(raw_item.get("id"), index)
        if subtask_id in seen:
            raise PlanError(f"Task {task_id} contains duplicate subtask id {subtask_id}")
        seen.add(subtask_id)
        title = ensure_text(raw_item.get("title"), f"Task {task_id} subtask {subtask_id} title")
        if len(title) > MAX_SUBTASK_TITLE_CHARS:
            raise PlanError(
                f"Task {task_id} subtask {subtask_id} title may not exceed "
                f"{MAX_SUBTASK_TITLE_CHARS} characters"
            )
        objective = str(raw_item.get("objective", "")).strip()
        if len(objective) > MAX_SUBTASK_OBJECTIVE_CHARS:
            raise PlanError(
                f"Task {task_id} subtask {subtask_id} objective may not exceed "
                f"{MAX_SUBTASK_OBJECTIVE_CHARS} characters"
            )
        result.append(
            {
                "id": subtask_id,
                "title": title,
                "objective": objective,
                "required": bool(raw_item.get("required", True)),
                "status": "pending",
                "started_at": None,
                "completed_at": None,
                "history": [],
            }
        )
    if not any(item["required"] for item in result):
        raise PlanError(f"Task {task_id} must have at least one required subtask")
    return result


def normalize_learning_targets(raw: Any, task_id: str) -> list[dict[str, Any]]:
    items = ensure_list(raw, f"Task {task_id} learning_targets")
    if len(items) > MAX_LEARNING_TARGETS_PER_TASK:
        raise PlanError(
            f"Task {task_id} may declare at most {MAX_LEARNING_TARGETS_PER_TASK} learning targets"
        )
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise PlanError(f"Task {task_id} learning_targets[{index}] must be an object")
        target_id = normalize_task_id(item.get("task_id"))
        if target_id in seen:
            raise PlanError(f"Task {task_id} contains duplicate learning target {target_id}")
        seen.add(target_id)
        reason = ensure_text(
            item.get("reason"), f"Task {task_id} learning target {target_id} reason"
        )
        if len(reason) < 20 or len(reason) > MAX_TASK_BOUNDARY_TEXT_CHARS:
            raise PlanError(
                f"Task {task_id} learning target {target_id} reason must be 20-"
                f"{MAX_TASK_BOUNDARY_TEXT_CHARS} characters"
            )
        topics = ensure_str_list(
            item.get("topics"), f"Task {task_id} learning target {target_id} topics"
        )
        if not topics or len(topics) > MAX_LEARNING_TOPICS:
            raise PlanError(
                f"Task {task_id} learning target {target_id} must declare 1-"
                f"{MAX_LEARNING_TOPICS} topics"
            )
        for topic in topics:
            if len(topic) > MAX_LEARNING_TOPIC_CHARS:
                raise PlanError(
                    f"Task {task_id} learning target {target_id} topic may not exceed "
                    f"{MAX_LEARNING_TOPIC_CHARS} characters"
                )
        result.append({"task_id": target_id, "reason": reason, "topics": topics})
    return result


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

    context_boundary = normalize_context_boundary(raw.get("context_boundary"), task_id)
    subtasks = normalize_subtasks(raw.get("subtasks"), task_id)
    learning_targets = normalize_learning_targets(raw.get("learning_targets"), task_id)

    return {
        "id": task_id,
        "slug": slugify(title, f"task-{task_id}"),
        "title": title,
        "objective": objective,
        "requirement_ids": requirement_ids,
        "complexity": complexity,
        "atomicity_rationale": atomicity_rationale,
        "context_boundary": context_boundary,
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
        "subtasks": subtasks,
        "learning_targets": learning_targets,
        "learning_files": [],
        "published_learning_files": [],
        "max_attempts": max_attempts,
        "status": "pending",
        "attempts": 0,
        "functional_failures": 0,
        "rate_limit_events": 0,
        "contract_failures": 0,
        "last_failure_kind": None,
        "deferred_until": None,
        "current_route": None,
        "started_at": None,
        "completed_at": None,
        "last_error": None,
        "history": [],
        "changed_files": [],
        "validation_results": [],
        "attempt_metrics": [],
        "last_attempt_metrics": None,
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
    position = {task_id: index for index, task_id in enumerate(ids)}
    for task in tasks:
        for dep in task["dependencies"]:
            if dep not in known:
                raise PlanError(f"Task {task['id']} depends on unknown task {dep}")
            if dep == task["id"]:
                raise PlanError(f"Task {task['id']} cannot depend on itself")
        for related in task["related_task_reads"]:
            if related not in known:
                raise PlanError(f"Task {task['id']} references unknown related task {related}")
        for target in task.get("learning_targets", []):
            target_id = target.get("task_id") if isinstance(target, dict) else None
            if target_id not in known:
                raise PlanError(
                    f"Task {task['id']} references unknown learning target {target_id}"
                )
            if target_id == task["id"]:
                raise PlanError(f"Task {task['id']} cannot publish learning to itself")
            if position[target_id] <= position[task["id"]]:
                raise PlanError(
                    f"Task {task['id']} learning target {target_id} must be a later TODO; "
                    "learning edges are directional and must not reintroduce prior chat history"
                )
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
        f"- {field.replace('_', ' ')}: **pass**"
        for field in review_checks_for_schema(manifest.get("schema_version"))
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
    if int(manifest.get("schema_version", 0)) >= 3:
        context_strategy = render_execution_context_strategy(manifest["execution_context"])
    else:
        context_strategy = "- Legacy plan: no first-class execution-context strategy."
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

## Execution-context strategy

{context_strategy}

## Planning evidence

{f"- Original user-authored request: `{manifest['request_source']['file']}`" if manifest.get('request_source') else "- Original request source: agent conversation"}
- Full request/repository analysis: `ANALYSIS.md`
- Independent plan review: `PLAN_REVIEW.md`
- Every request part maps to at least one requirement.
- Every requirement maps to at least one executable TODO, and every TODO maps back to requirements.
- Executable TODOs may be low, medium, or high complexity; extreme work must be split before plan creation.
- Shared context is omitted by default and created only when the reviewer confirms it is minimal and materially useful.

## Execution policy

- Start automatically after validation: **{'yes' if manifest['autostart'] else 'no'}**
- Delete planning artifacts after successful summary: **{'yes' if manifest['cleanup_on_success'] else 'no'}**
- Default execution: sequential for write tasks; parallel only for read-only tasks or isolated worktrees.
- Each worker may read its assigned task definition and only the exact context files referenced there.
- Reading another task definition requires a blocked dependency, ambiguity, or validation conflict and must be recorded.

Plan id: `{manifest['plan_id']}`  
Created: `{manifest['created_at']}`
"""

def render_task(
    task: dict[str, Any],
    plan_id: str,
    work_root: str = WORK_ROOT_DEFAULT,
) -> str:
    dependency_text = ", ".join(task["dependencies"]) or "none"
    related_text = ", ".join(task["related_task_reads"]) or "none"
    related_files = task.get("related_task_files", [])
    expected = task["scope"]["expected_files"]
    context_files = task.get("context_files", [])
    learning_files = task.get("learning_files", [])
    context_references = [
        context_reference(work_root, plan_id, relative) for relative in context_files
    ]
    learning_references = [
        context_reference(work_root, plan_id, relative) for relative in learning_files
    ]
    context_frontmatter = ", ".join(context_files) or "none"
    learning_frontmatter = ", ".join(learning_files) or "none"
    context_markdown = markdown_list([f"`{item}`" for item in context_references])
    learning_markdown = markdown_list([f"`{item}`" for item in learning_references])
    boundary = task.get("context_boundary") if isinstance(task.get("context_boundary"), dict) else {}
    shared_context = boundary.get("shared_context", []) if isinstance(boundary, dict) else []
    separate_from = boundary.get("separate_from", []) if isinstance(boundary, dict) else []
    why_one_todo = str(boundary.get("why_one_todo", "Legacy task definition"))
    subtask_lines: list[str] = []
    for subtask in task.get("subtasks", []):
        marker = "[x]" if subtask.get("status") == "completed" else "[ ]"
        suffix = ""
        if subtask.get("status") == "in_progress":
            suffix = " _(in progress)_"
        elif not subtask.get("required", True):
            suffix = " _(optional)_"
        subtask_lines.append(
            f"- {marker} **{subtask.get('id', '?')}** — {subtask.get('title', '')}{suffix}"
        )
        objective = str(subtask.get("objective", "")).strip()
        if objective:
            subtask_lines.append(f"  - {objective}")
    subtasks_markdown = "\n".join(subtask_lines) or "- None (legacy task)"
    learning_targets = []
    for target in task.get("learning_targets", []):
        if isinstance(target, dict):
            topics = ", ".join(target.get("topics", [])) or "unspecified"
            learning_targets.append(
                f"**{target.get('task_id', '?')}** — {target.get('reason', '')} "
                f"(topics: {topics})"
            )
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
context_files: "{context_frontmatter}"
learning_files: "{learning_frontmatter}"
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

## Context-isolation boundary

- Why one fresh worker context helps this whole TODO: {why_one_todo}
- Context that is genuinely shared by all subtasks:
{markdown_list(shared_context)}
- Concerns deliberately isolated into other TODOs:
{markdown_list(separate_from)}

## Isolation contract

This task definition and the exact execution-context files listed below are the only planning artifacts assigned to this worker. Read the task definition first, then read every assigned context file. Do not discover or open any other context file, `PLAN.md`, `TODO.md`, `manifest.json`, `orchestrator.config.json`, result files, logs, or unrelated task definitions. You may read repository source, tests, build files, and runtime output relevant to this task.

Another task definition may be opened only when one of the explicitly allowed task ids above is necessary to resolve a blocked dependency, ambiguity, or validation conflict. Record the task id and reason in the completion report.

## Assigned execution context

{context_markdown}

## Assigned validated learnings

{learning_markdown}

These files are concise, immutable artifacts produced only after another TODO passed deterministic validation. Read exactly the assigned files, never a previous worker transcript or an unassigned learning file.

## Resumable subtask checklist

{subtasks_markdown}

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

{markdown_list(learning_targets)}

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

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
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
    manifest_path = plan_dir / MANIFEST
    if manifest_path.is_file():
        current = read_json(manifest_path)
        current_revision = max(0, int(current.get("revision", 0)))
        supplied_revision = max(0, int(manifest.get("revision", 0)))
        if current_revision != supplied_revision:
            raise PlanError(
                f"Plan mutation rejected: stale revision {supplied_revision}; current revision is {current_revision}"
            )
    lease_path = plan_dir / ".runner-lease.json"
    if lease_path.is_file():
        lease = read_json(lease_path)
        expected_nonce = os.environ.get("PAE_RUNNER_LEASE_NONCE")
        expected_epoch = os.environ.get("PAE_RUNNER_LEASE_EPOCH")
        if not expected_nonce or lease.get("nonce") != expected_nonce:
            raise PlanError("Plan mutation rejected: a different runner owns the live lease")
        if expected_epoch and str(lease.get("epoch")) != expected_epoch:
            raise PlanError("Plan mutation rejected: runner lease epoch is stale")
        if int(manifest.get("lease_epoch", 0)) > int(lease.get("epoch", 0)):
            raise PlanError("Plan mutation rejected: manifest belongs to a newer runner lease")
        manifest["lease_epoch"] = int(lease.get("epoch", 0))
    manifest["revision"] = max(0, int(manifest.get("revision", 0))) + 1
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
    atomic_write_json(manifest_path, manifest)
    atomic_write_text(plan_dir / "TODO.md", render_todo(manifest))
    plan_id = str(manifest.get("plan_id", ""))
    work_root = str(manifest.get("work_root", WORK_ROOT_DEFAULT))
    # Schema-v4 task definitions are live projections of authoritative child
    # state. Preserve the historical schema-v1-v3 behavior exactly: those
    # task files remain immutable after plan creation.
    if int(manifest.get("schema_version", 0)) >= 4 and plan_id:
        for task in manifest.get("tasks", []):
            path_value = task.get("file")
            if isinstance(path_value, str) and path_value:
                atomic_write_text(
                    plan_dir / path_value,
                    render_task(task, plan_id, work_root),
                )


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
    execution_context = normalize_execution_context(spec.get("execution_context"), tasks)
    assign_context_files(tasks, execution_context)
    plan_review = normalize_plan_review(spec.get("plan_review"), SCHEMA_VERSION)

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
    (plan_dir / LEARNING_DIRECTORY).mkdir()

    created = now_utc()
    for task in tasks:
        task["file"] = f"tasks/{task['id']}-{task['slug']}.md"
    task_file_by_id = {task["id"]: task["file"] for task in tasks}
    for task in tasks:
        task["related_task_files"] = [
            task_file_by_id[item] for item in task["related_task_reads"]
        ]

    manifest: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "plan_id": normalized_plan_id,
        "title": title,
        "summary": summary,
        "request_analysis": request_analysis,
        "requirements": requirements,
        "global_constraints": ensure_str_list(spec.get("global_constraints"), "global_constraints"),
        "execution_context": execution_context,
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
        "learning_artifacts": [],
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
    write_context_artifacts(plan_dir, execution_context)
    for task in tasks:
        atomic_write_text(
            plan_dir / task["file"],
            render_task(task, normalized_plan_id, Path(work_root).as_posix()),
        )
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

    if schema_version in {2, 3, 4}:
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
                request_part_coverage(analysis["request_parts"], normalized_requirements)
            except PlanError as exc:
                errors.append(str(exc))
        try:
            normalize_plan_review(manifest.get("plan_review"), int(schema_version))
        except (PlanError, TypeError, ValueError) as exc:
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

    if schema_version in {3, 4}:
        errors.extend(validate_context_artifacts(plan_dir, manifest, tasks))

    if schema_version == 4:
        errors.extend(validate_learning_artifacts(plan_dir, manifest, tasks))

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
        elif schema_version == 4:
            expected_task = render_task(
                task,
                str(manifest.get("plan_id", "")),
                str(manifest.get("work_root", WORK_ROOT_DEFAULT)),
            )
            try:
                if task_path.read_text(encoding="utf-8") != expected_task:
                    errors.append(
                        f"Task {task_id}: definition file does not match authoritative manifest state"
                    )
            except OSError as exc:
                errors.append(f"Task {task_id}: could not read definition file: {exc}")
        if not task.get("acceptance_criteria"):
            errors.append(f"Task {task_id}: missing acceptance criteria")
        if not task.get("validation_commands"):
            errors.append(f"Task {task_id}: missing validation commands")
        if schema_version == 4:
            try:
                normalize_context_boundary(task.get("context_boundary"), str(task_id))
            except PlanError as exc:
                errors.append(str(exc))
            subtasks = task.get("subtasks")
            if not isinstance(subtasks, list) or not subtasks:
                errors.append(f"Task {task_id}: missing resumable subtasks")
            else:
                ids: list[str] = []
                active: list[str] = []
                required: list[str] = []
                completed_required: list[str] = []
                for index, subtask in enumerate(subtasks):
                    if not isinstance(subtask, dict):
                        errors.append(f"Task {task_id}: subtask {index} must be an object")
                        continue
                    try:
                        subtask_id = normalize_subtask_id(subtask.get("id"), index)
                    except PlanError as exc:
                        errors.append(f"Task {task_id}: {exc}")
                        continue
                    ids.append(subtask_id)
                    status = subtask.get("status")
                    if status not in VALID_SUBTASK_STATUSES:
                        errors.append(
                            f"Task {task_id} subtask {subtask_id}: invalid status {status!r}"
                        )
                    if status == "in_progress":
                        active.append(subtask_id)
                    if subtask.get("required", True):
                        required.append(subtask_id)
                        if status == "completed":
                            completed_required.append(subtask_id)
                    title = subtask.get("title")
                    if not isinstance(title, str) or not title.strip():
                        errors.append(f"Task {task_id} subtask {subtask_id}: missing title")
                if len(ids) != len(set(ids)):
                    errors.append(f"Task {task_id}: duplicate subtask ids")
                if len(active) > 1:
                    errors.append(
                        f"Task {task_id}: more than one subtask is in progress: {', '.join(active)}"
                    )
                if active and task.get("status") != "in_progress":
                    errors.append(
                        f"Task {task_id}: subtask is in progress while parent status is {task.get('status')}"
                    )
                if task.get("status") == "completed" and set(required) != set(completed_required):
                    errors.append(
                        f"Task {task_id}: completed parent has incomplete required subtasks"
                    )
            try:
                normalize_learning_targets(task.get("learning_targets"), str(task_id))
            except PlanError as exc:
                errors.append(str(exc))
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
    if schema_version in {2, 3, 4}:
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
        if schema_version in {3, 4}:
            execution_context = manifest.get("execution_context", {})
            global_context = execution_context.get("global", {})
            scoped = execution_context.get("scoped", [])
            assigned_reads = sum(
                len(task.get("context_files", [])) for task in manifest.get("tasks", [])
            )
            lines.extend(
                [
                    "",
                    "## Progressive execution context",
                    "",
                    f"- Global decision: **{global_context.get('decision', 'missing')}**",
                    f"- Global items: {len(global_context.get('items', []))}",
                    f"- Scoped files: {len(scoped)}",
                    f"- Total task-to-context assignments: {assigned_reads}",
                    "- Context minimality review: **pass**",
                ]
            )
        if schema_version == 4:
            subtask_total = sum(
                len(task.get("subtasks", [])) for task in manifest.get("tasks", [])
            )
            learning_edges = sum(
                len(task.get("learning_targets", []))
                for task in manifest.get("tasks", [])
            )
            learning_files = len(manifest.get("learning_artifacts", []))
            lines.extend(
                [
                    "",
                    "## Context-isolated resumability",
                    "",
                    "- Context-boundary review: **pass**",
                    f"- Persisted subtasks: {subtask_total}",
                    f"- Predeclared learning edges: {learning_edges}",
                    f"- Validated learning artifacts materialized: {learning_files}",
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


def learning_source_ids(manifest: dict[str, Any], target_id: str) -> list[str]:
    """Return earlier tasks that may publish validated learnings to one target."""
    normalized = normalize_task_id(target_id)
    sources: list[str] = []
    for source in manifest.get("tasks", []):
        for relation in source.get("learning_targets", []):
            if isinstance(relation, dict) and relation.get("task_id") == normalized:
                sources.append(str(source.get("id")))
                break
    return sources


def next_runnable_task(manifest: dict[str, Any]) -> dict[str, Any] | None:
    completed = {task["id"] for task in manifest["tasks"] if task["status"] == "completed"}
    now = dt.datetime.now(dt.timezone.utc)
    for task in manifest["tasks"]:
        context_prerequisites = set(learning_source_ids(manifest, task["id"]))
        deferred_until = task.get("deferred_until")
        if deferred_until:
            try:
                deferred_time = dt.datetime.fromisoformat(str(deferred_until))
                if deferred_time.tzinfo is None:
                    deferred_time = deferred_time.replace(tzinfo=dt.timezone.utc)
                if deferred_time > now:
                    continue
            except ValueError:
                pass
        if (
            task["status"] == "pending"
            and set(task["dependencies"]).issubset(completed)
            and context_prerequisites.issubset(completed)
        ):
            return task
    return None


def append_event(manifest: dict[str, Any], event_type: str, **details: Any) -> None:
    manifest.setdefault("events", []).append({"at": now_utc(), "type": event_type, **details})


def find_subtask(task: dict[str, Any], subtask_id: str) -> dict[str, Any]:
    normalized = normalize_subtask_id(subtask_id)
    for subtask in task.get("subtasks", []):
        if subtask.get("id") == normalized:
            return subtask
    raise PlanError(f"Task {task.get('id', '?')} has no subtask {subtask_id}")


def completed_subtask_ids(task: dict[str, Any]) -> list[str]:
    return [
        str(subtask.get("id"))
        for subtask in task.get("subtasks", [])
        if subtask.get("status") == "completed"
    ]


def recover_in_progress_subtasks(task: dict[str, Any], reason: str) -> list[str]:
    recovered: list[str] = []
    for subtask in task.get("subtasks", []):
        if subtask.get("status") != "in_progress":
            continue
        subtask["status"] = "pending"
        subtask["started_at"] = None
        subtask.setdefault("history", []).append(
            {"at": now_utc(), "event": "recovered", "reason": reason[:500]}
        )
        recovered.append(str(subtask.get("id")))
    return recovered


def set_subtask_state(
    plan_dir: Path,
    manifest: dict[str, Any],
    task_id: str,
    subtask_id: str,
    state: str,
) -> dict[str, Any]:
    if state not in VALID_SUBTASK_STATUSES:
        raise PlanError(f"Invalid subtask state {state!r}")
    task = find_task(manifest, task_id)
    if not task.get("subtasks"):
        raise PlanError(f"Task {task['id']} is a legacy task without resumable subtasks")
    subtask = find_subtask(task, subtask_id)
    previous = str(subtask.get("status", "pending"))
    if state == "in_progress":
        if task.get("status") != "in_progress":
            raise PlanError(f"Task {task['id']} must be in progress before starting a subtask")
        if previous == "in_progress":
            return subtask
        if previous == "completed":
            raise PlanError(
                f"Subtask {subtask['id']} is completed; reset it explicitly before restarting"
            )
        active = [
            item.get("id")
            for item in task.get("subtasks", [])
            if item.get("status") == "in_progress" and item is not subtask
        ]
        if active:
            raise PlanError(
                f"Task {task['id']} already has in-progress subtask(s): {', '.join(active)}"
            )
        subtask["status"] = "in_progress"
        subtask["started_at"] = subtask.get("started_at") or now_utc()
        event = "started"
    elif state == "completed":
        if task.get("status") != "in_progress":
            raise PlanError(f"Task {task['id']} must be in progress before completing a subtask")
        if previous == "completed":
            return subtask
        if previous != "in_progress":
            raise PlanError(
                f"Subtask {subtask['id']} must be in progress before it can be completed"
            )
        subtask["status"] = "completed"
        subtask["completed_at"] = now_utc()
        event = "completed"
    else:
        if task.get("status") == "completed":
            raise PlanError(f"Completed task {task['id']} cannot reset subtask state")
        if previous == "pending":
            return subtask
        subtask["status"] = "pending"
        subtask["started_at"] = None
        subtask["completed_at"] = None
        event = "reset"
    subtask.setdefault("history", []).append(
        {"at": now_utc(), "event": event, "previous_status": previous}
    )
    task.setdefault("history", []).append(
        {"at": now_utc(), "event": f"subtask_{event}", "subtask_id": subtask["id"]}
    )
    append_event(
        manifest,
        f"subtask_{event}",
        task_id=task["id"],
        subtask_id=subtask["id"],
    )
    save_manifest(plan_dir, manifest)
    return subtask


def reconcile_reported_subtasks(task: dict[str, Any], report: dict[str, Any]) -> None:
    if not task.get("subtasks"):
        return
    raw_ids = report.get("completed_subtask_ids", [])
    if not isinstance(raw_ids, list):
        raise PlanError("completed_subtask_ids must be a list")
    reported = [normalize_subtask_id(item) for item in raw_ids]
    if len(reported) != len(set(reported)):
        raise PlanError("completed_subtask_ids must not contain duplicates")
    known = {str(item.get("id")) for item in task.get("subtasks", [])}
    unknown = sorted(set(reported) - known)
    if unknown:
        raise PlanError(
            f"Task {task['id']} report references unknown completed subtasks: {', '.join(unknown)}"
        )
    for subtask in task.get("subtasks", []):
        if subtask.get("id") in reported and subtask.get("status") != "completed":
            previous = str(subtask.get("status", "pending"))
            subtask["status"] = "completed"
            subtask["started_at"] = subtask.get("started_at") or now_utc()
            subtask["completed_at"] = now_utc()
            subtask.setdefault("history", []).append(
                {"at": now_utc(), "event": "completed_from_report", "previous_status": previous}
            )
    required = {
        str(item.get("id"))
        for item in task.get("subtasks", [])
        if item.get("required", True)
    }
    completed = set(completed_subtask_ids(task))
    missing = sorted(required - completed)
    if missing:
        raise PlanError(
            f"Task {task['id']} cannot complete; required subtasks remain: {', '.join(missing)}"
        )
    if set(reported) != completed:
        raise PlanError(
            f"Task {task['id']} report must list every completed subtask exactly; "
            f"expected {sorted(completed)!r}, received {sorted(set(reported))!r}"
        )


def declared_learning_target(task: dict[str, Any], target_id: str) -> dict[str, Any] | None:
    for target in task.get("learning_targets", []):
        if isinstance(target, dict) and target.get("task_id") == target_id:
            return target
    return None


def normalize_learning_reference(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PlanError(f"{field} must be a non-empty string")
    text = value.strip()
    if "\n" in text or "\r" in text or len(text) > 240:
        raise PlanError(f"{field} must be one line and at most 240 characters")
    lowered = text.lower().replace("\\", "/")
    if "/.ai-work/" in f"/{lowered}" or lowered.startswith(".ai-work/"):
        raise PlanError(f"{field} may not reference planning artifacts")
    return text


def normalize_reusable_learnings(
    task: dict[str, Any], report: dict[str, Any]
) -> list[dict[str, Any]]:
    raw = report.get("reusable_learnings", [])
    if not isinstance(raw, list):
        raise PlanError("reusable_learnings must be a list")
    if len(raw) > MAX_REUSABLE_LEARNINGS:
        raise PlanError(
            f"reusable_learnings may contain at most {MAX_REUSABLE_LEARNINGS} items"
        )
    declared = {
        str(item.get("task_id"))
        for item in task.get("learning_targets", [])
        if isinstance(item, dict)
    }
    result: list[dict[str, Any]] = []
    for index, item in enumerate(raw):
        field = f"reusable_learnings[{index}]"
        if not isinstance(item, dict):
            raise PlanError(f"{field} must be an object")
        kind = str(item.get("kind", "")).strip().lower()
        if kind not in VALID_LEARNING_KINDS:
            raise PlanError(f"{field}.kind must be one of {sorted(VALID_LEARNING_KINDS)}")
        guidance = ensure_text(item.get("guidance"), f"{field}.guidance")
        if len(guidance) < 35 or len(guidance) > MAX_LEARNING_GUIDANCE_CHARS:
            raise PlanError(
                f"{field}.guidance must be 35-{MAX_LEARNING_GUIDANCE_CHARS} characters"
            )
        references = ensure_list(item.get("references"), f"{field}.references")
        if not references or len(references) > MAX_LEARNING_REFERENCES:
            raise PlanError(
                f"{field}.references must contain 1-{MAX_LEARNING_REFERENCES} entries"
            )
        clean_references = [
            normalize_learning_reference(value, f"{field}.references[{ref_index}]")
            for ref_index, value in enumerate(references)
        ]
        target_values = ensure_list(item.get("target_task_ids"), f"{field}.target_task_ids")
        if not target_values:
            raise PlanError(f"{field}.target_task_ids must not be empty")
        target_ids = [normalize_task_id(value) for value in target_values]
        if len(target_ids) != len(set(target_ids)):
            raise PlanError(f"{field}.target_task_ids must not contain duplicates")
        undeclared = sorted(set(target_ids) - declared)
        if undeclared:
            raise PlanError(
                f"Task {task['id']} attempted to publish learning to undeclared target(s): "
                + ", ".join(undeclared)
            )
        result.append(
            {
                "kind": kind,
                "guidance": guidance,
                "references": clean_references,
                "target_task_ids": target_ids,
            }
        )
    return result


def learning_artifact_path(source_id: str, target_id: str) -> str:
    return f"{LEARNING_DIRECTORY}/{source_id}-to-{target_id}.md"


def render_learning_artifact(
    source_task: dict[str, Any],
    target_task: dict[str, Any],
    declaration: dict[str, Any],
    learnings: list[dict[str, Any]],
) -> str:
    lines = [
        f"# Validated learning — {source_task['id']} → {target_task['id']}",
        "",
        "This artifact contains only concise findings from a completed TODO that passed deterministic validation. It is not a worker transcript and must not be expanded with general history.",
        "",
        "## Applicability declared during planning",
        "",
        f"- Source TODO: **{source_task['id']} — {source_task['title']}**",
        f"- Target TODO: **{target_task['id']} — {target_task['title']}**",
        f"- Why similar: {declaration['reason']}",
        f"- Topics: {', '.join(declaration['topics'])}",
        "",
        "## Reusable findings",
        "",
    ]
    for index, learning in enumerate(learnings, start=1):
        lines.extend(
            [
                f"### {index}. {learning['kind']}",
                "",
                learning["guidance"],
                "",
                "References:",
                *[f"- `{reference}`" for reference in learning["references"]],
                "",
            ]
        )
    content = "\n".join(lines).rstrip() + "\n"
    if len(content) > MAX_LEARNING_FILE_CHARS:
        raise PlanError(
            f"Learning artifact {source_task['id']}->{target_task['id']} exceeds "
            f"{MAX_LEARNING_FILE_CHARS} characters; make the findings more concise"
        )
    return content


def materialize_learning_artifacts(
    plan_dir: Path,
    manifest: dict[str, Any],
    task: dict[str, Any],
    report: dict[str, Any],
) -> list[str]:
    learnings = normalize_reusable_learnings(task, report)
    if not learnings:
        return []

    by_target: dict[str, list[dict[str, Any]]] = {}
    for learning in learnings:
        for target_id in learning["target_task_ids"]:
            by_target.setdefault(target_id, []).append(learning)

    artifacts = manifest.setdefault("learning_artifacts", [])
    if not isinstance(artifacts, list):
        raise PlanError("manifest.learning_artifacts must be a list")

    existing_files = {
        str(item.get("file"))
        for item in artifacts
        if isinstance(item, dict) and item.get("file")
    }
    prepared: list[dict[str, Any]] = []
    for declaration in task.get("learning_targets", []):
        if not isinstance(declaration, dict):
            continue
        target_id = str(declaration.get("task_id", ""))
        target_learnings = by_target.get(target_id)
        if not target_learnings:
            continue
        target_task = find_task(manifest, target_id)
        if (
            target_task.get("status") != "pending"
            or int(target_task.get("attempts", 0)) != 0
            or target_task.get("started_at") is not None
        ):
            raise PlanError(
                f"Task {task['id']} cannot publish learning to TODO {target_id}: "
                "the target has already started, so changing its assigned context would be unsafe"
            )
        relative = learning_artifact_path(task["id"], target_id)
        if relative in existing_files or (plan_dir / relative).exists():
            raise PlanError(f"Learning artifact already exists: {relative}")
        artifact_items = [
            {
                "kind": learning["kind"],
                "guidance": learning["guidance"],
                "references": list(learning["references"]),
            }
            for learning in target_learnings
        ]
        content = render_learning_artifact(
            task,
            target_task,
            declaration,
            artifact_items,
        )
        prepared.append(
            {
                "target_task": target_task,
                "relative": relative,
                "content": content,
                "artifact": {
                    "source_task_id": task["id"],
                    "target_task_id": target_id,
                    "file": relative,
                    "reason": declaration["reason"],
                    "topics": list(declaration["topics"]),
                    "items": artifact_items,
                    "item_count": len(artifact_items),
                    "created_at": now_utc(),
                },
            }
        )

    # Every normalized learning must map to one of the task's declared targets.
    prepared_targets = {item["artifact"]["target_task_id"] for item in prepared}
    missing_targets = sorted(set(by_target) - prepared_targets)
    if missing_targets:
        raise PlanError(
            f"Task {task['id']} could not materialize declared learning target(s): "
            + ", ".join(missing_targets)
        )

    written: list[Path] = []
    try:
        for item in prepared:
            path = plan_dir / item["relative"]
            atomic_write_text(path, item["content"])
            written.append(path)
            item["artifact"]["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    except Exception:
        for path in written:
            try:
                path.unlink()
            except FileNotFoundError:
                pass
        raise

    created: list[str] = []
    for item in prepared:
        relative = item["relative"]
        artifacts.append(item["artifact"])
        target_files = item["target_task"].setdefault("learning_files", [])
        if relative not in target_files:
            target_files.append(relative)
        source_files = task.setdefault("published_learning_files", [])
        if relative not in source_files:
            source_files.append(relative)
        created.append(relative)
    return created


def validate_learning_artifacts(
    plan_dir: Path,
    manifest: dict[str, Any],
    tasks: list[dict[str, Any]],
) -> list[str]:
    errors: list[str] = []
    directory = plan_dir / LEARNING_DIRECTORY
    if not directory.is_dir() or directory.is_symlink():
        return [f"Missing or invalid {LEARNING_DIRECTORY}/ directory"]
    task_by_id = {str(task.get("id")): task for task in tasks}
    artifacts = manifest.get("learning_artifacts", [])
    if not isinstance(artifacts, list):
        return ["manifest.learning_artifacts must be a list"]
    expected_files: set[str] = set()
    expected_target_files: dict[str, list[str]] = {task_id: [] for task_id in task_by_id}
    expected_source_files: dict[str, list[str]] = {task_id: [] for task_id in task_by_id}
    for index, artifact in enumerate(artifacts):
        field = f"learning_artifacts[{index}]"
        if not isinstance(artifact, dict):
            errors.append(f"{field} must be an object")
            continue
        source_id = str(artifact.get("source_task_id", ""))
        target_id = str(artifact.get("target_task_id", ""))
        source = task_by_id.get(source_id)
        target = task_by_id.get(target_id)
        if source is None or target is None:
            errors.append(f"{field} references unknown source or target task")
            continue
        declaration = declared_learning_target(source, target_id)
        if declaration is None:
            errors.append(f"{field} is not backed by a declared learning target")
            continue
        if artifact.get("reason") != declaration.get("reason"):
            errors.append(f"{field}.reason does not match the planned learning relationship")
        if artifact.get("topics") != declaration.get("topics"):
            errors.append(f"{field}.topics do not match the planned learning relationship")
        items = artifact.get("items")
        if not isinstance(items, list) or not items:
            errors.append(f"{field}.items must be a non-empty list")
            continue
        if artifact.get("item_count") != len(items):
            errors.append(f"{field}.item_count does not match its items")
        clean_items: list[dict[str, Any]] = []
        for item_index, item in enumerate(items):
            item_field = f"{field}.items[{item_index}]"
            if not isinstance(item, dict):
                errors.append(f"{item_field} must be an object")
                continue
            kind = item.get("kind")
            guidance = item.get("guidance")
            references = item.get("references")
            if kind not in VALID_LEARNING_KINDS:
                errors.append(f"{item_field}.kind is invalid")
            if (
                not isinstance(guidance, str)
                or len(guidance.strip()) < 35
                or len(guidance.strip()) > MAX_LEARNING_GUIDANCE_CHARS
            ):
                errors.append(f"{item_field}.guidance is invalid")
            if not isinstance(references, list) or not references:
                errors.append(f"{item_field}.references must be a non-empty list")
                continue
            try:
                clean_references = [
                    normalize_learning_reference(value, f"{item_field}.references[{ref_index}]")
                    for ref_index, value in enumerate(references)
                ]
            except PlanError as exc:
                errors.append(str(exc))
                continue
            clean_items.append(
                {
                    "kind": kind,
                    "guidance": guidance.strip() if isinstance(guidance, str) else guidance,
                    "references": clean_references,
                }
            )
        expected_relative = learning_artifact_path(source_id, target_id)
        relative = artifact.get("file")
        if relative != expected_relative:
            errors.append(f"{field}.file must be {expected_relative}")
            continue
        if relative in expected_files:
            errors.append(f"Duplicate learning artifact file {relative}")
            continue
        expected_files.add(relative)
        expected_target_files[target_id].append(relative)
        expected_source_files[source_id].append(relative)
        path = plan_dir / relative
        if not path.is_file() or path.is_symlink():
            errors.append(f"Missing or invalid learning artifact {relative}")
            continue
        try:
            actual_content = path.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"Could not read learning artifact {relative}: {exc}")
            continue
        if len(actual_content) > MAX_LEARNING_FILE_CHARS:
            errors.append(f"Learning artifact {relative} exceeds the size limit")
        if len(clean_items) == len(items):
            try:
                expected_content = render_learning_artifact(
                    source,
                    target,
                    declaration,
                    clean_items,
                )
                if actual_content != expected_content:
                    errors.append(
                        f"Learning artifact {relative} does not match authoritative manifest state"
                    )
            except PlanError as exc:
                errors.append(str(exc))
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual_hash != artifact.get("sha256"):
            errors.append(f"Learning artifact {relative} hash mismatch")
    actual_files = {
        path.relative_to(plan_dir).as_posix()
        for path in directory.iterdir()
        if path.is_file()
    }
    unexpected = sorted(actual_files - expected_files)
    missing = sorted(expected_files - actual_files)
    if unexpected:
        errors.append("Unexpected learning artifacts: " + ", ".join(unexpected))
    if missing:
        errors.append("Missing learning artifacts: " + ", ".join(missing))
    for task_id, task in task_by_id.items():
        actual_target = task.get("learning_files", [])
        if actual_target != expected_target_files[task_id]:
            errors.append(
                f"Task {task_id}: learning_files mismatch; expected "
                f"{expected_target_files[task_id]!r}, received {actual_target!r}"
            )
        actual_source = task.get("published_learning_files", [])
        if actual_source != expected_source_files[task_id]:
            errors.append(
                f"Task {task_id}: published_learning_files mismatch; expected "
                f"{expected_source_files[task_id]!r}, received {actual_source!r}"
            )
    return errors


def remove_learning_artifacts_from_source(
    plan_dir: Path,
    manifest: dict[str, Any],
    task: dict[str, Any],
) -> list[str]:
    artifacts = manifest.get("learning_artifacts", [])
    if not isinstance(artifacts, list):
        raise PlanError("manifest.learning_artifacts must be a list")
    selected = [
        artifact
        for artifact in artifacts
        if isinstance(artifact, dict) and artifact.get("source_task_id") == task.get("id")
    ]
    if not selected:
        task["published_learning_files"] = []
        return []

    for artifact in selected:
        target = find_task(manifest, str(artifact.get("target_task_id", "")))
        if (
            target.get("status") != "pending"
            or int(target.get("attempts", 0)) != 0
            or target.get("started_at") is not None
        ):
            raise PlanError(
                f"Cannot reset completed task {task['id']}: learning artifact "
                f"{artifact.get('file')} has already become part of TODO {target['id']} execution"
            )

    removed: list[str] = []
    selected_files = {
        str(artifact.get("file"))
        for artifact in selected
        if isinstance(artifact.get("file"), str)
    }
    for relative in sorted(selected_files):
        path = plan_dir / checked_relative_path(relative, "learning artifact file")
        if path.is_symlink():
            raise PlanError(f"Refusing to remove symlinked learning artifact: {relative}")
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        removed.append(relative)

    manifest["learning_artifacts"] = [
        artifact
        for artifact in artifacts
        if not (
            isinstance(artifact, dict)
            and artifact.get("source_task_id") == task.get("id")
        )
    ]
    for target in manifest.get("tasks", []):
        target["learning_files"] = [
            relative
            for relative in target.get("learning_files", [])
            if relative not in selected_files
        ]
    task["published_learning_files"] = []
    return removed


def claim_task(plan_dir: Path, manifest: dict[str, Any], task_id: str, route: dict[str, Any] | None) -> dict[str, Any]:
    task = find_task(manifest, task_id)
    if task["status"] != "pending":
        raise PlanError(f"Task {task['id']} is not pending; current status: {task['status']}")
    completed = {item["id"] for item in manifest["tasks"] if item["status"] == "completed"}
    missing = [dep for dep in task["dependencies"] if dep not in completed]
    if missing:
        raise PlanError(f"Task {task['id']} has incomplete dependencies: {', '.join(missing)}")
    pending_learning_sources = [
        source_id
        for source_id in learning_source_ids(manifest, task["id"])
        if source_id not in completed
    ]
    if pending_learning_sources:
        raise PlanError(
            f"Task {task['id']} is waiting for declared learning source(s): "
            + ", ".join(pending_learning_sources)
        )
    task["status"] = "in_progress"
    task["deferred_until"] = None
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
    if isinstance(report, dict):
        reconcile_reported_subtasks(task, report)
        published_learning_files = materialize_learning_artifacts(
            plan_dir, manifest, task, report
        )
    else:
        published_learning_files = []
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
    task["last_failure_kind"] = None
    task["deferred_until"] = None
    task["changed_files"] = clean_files
    task["validation_results"] = report.get("validation_results", []) if isinstance(report, dict) else []
    runtime_metrics = report.get("runtime_metrics") if isinstance(report, dict) else None
    if isinstance(runtime_metrics, dict):
        task["last_attempt_metrics"] = runtime_metrics
        task.setdefault("attempt_metrics", []).append(runtime_metrics)
    task["result_file"] = result_file
    task["history"].append(
        {
            "at": now_utc(),
            "event": "completed",
            "result_file": result_file,
            "published_learning_files": published_learning_files,
        }
    )
    append_event(
        manifest,
        "task_completed",
        task_id=task["id"],
        published_learning_files=published_learning_files,
    )
    save_manifest(plan_dir, manifest)
    return task


def fail_task(
    plan_dir: Path,
    manifest: dict[str, Any],
    task_id: str,
    reason: str,
    *,
    rate_limited: bool = False,
    failure_kind: str | None = None,
    deferred_until: str | None = None,
    block: bool = False,
) -> dict[str, Any]:
    task = find_task(manifest, task_id)
    if task["status"] != "in_progress":
        raise PlanError(f"Task {task['id']} is not in progress")
    recovered_subtasks = recover_in_progress_subtasks(task, reason)
    kind = failure_kind or ("availability" if rate_limited else "capability")
    if kind == "availability":
        task["rate_limit_events"] += 1
        event = "availability_deferred" if deferred_until else "rate_limited"
    elif kind == "contract":
        task["contract_failures"] = int(task.get("contract_failures", 0)) + 1
        event = "contract_failed"
    else:
        if kind in {"capability", "validation"}:
            task["functional_failures"] += 1
        event = f"{kind}_failed"
    task["last_failure_kind"] = kind
    task["deferred_until"] = deferred_until
    task["last_error"] = reason.strip()[:4000]
    runtime_metrics = task.get("last_attempt_metrics")
    if isinstance(runtime_metrics, dict):
        recorded = task.setdefault("attempt_metrics", [])
        if not recorded or recorded[-1] != runtime_metrics:
            recorded.append(runtime_metrics)
    if block or kind in {"environment", "planning_invalidation"}:
        task["status"] = "blocked"
    elif kind in {"capability", "validation"} and task["functional_failures"] >= task["max_attempts"]:
        task["status"] = "blocked"
    else:
        task["status"] = "pending"
    task["history"].append(
        {
            "at": now_utc(),
            "event": event,
            "failure_kind": kind,
            "reason": task["last_error"],
            "recovered_subtasks": recovered_subtasks,
            "deferred_until": deferred_until,
        }
    )
    append_event(
        manifest,
        f"task_{event}",
        task_id=task["id"],
        reason=task["last_error"],
        failure_kind=kind,
        recovered_subtasks=recovered_subtasks,
        deferred_until=deferred_until,
    )
    save_manifest(plan_dir, manifest)
    return task


def reset_task(plan_dir: Path, manifest: dict[str, Any], task_id: str) -> dict[str, Any]:
    task = find_task(manifest, task_id)
    was_completed = task.get("status") == "completed"
    removed_learning_files = (
        remove_learning_artifacts_from_source(plan_dir, manifest, task)
        if was_completed
        else []
    )
    if was_completed:
        reset_subtasks: list[str] = []
        for subtask in task.get("subtasks", []):
            previous = str(subtask.get("status", "pending"))
            subtask["status"] = "pending"
            subtask["started_at"] = None
            subtask["completed_at"] = None
            subtask.setdefault("history", []).append(
                {"at": now_utc(), "event": "reset_with_parent", "previous_status": previous}
            )
            reset_subtasks.append(str(subtask.get("id")))
        recovered_subtasks = reset_subtasks
    else:
        recovered_subtasks = recover_in_progress_subtasks(task, "Parent task reset")
    task["status"] = "pending"
    task["last_error"] = None
    task["last_failure_kind"] = None
    task["deferred_until"] = None
    task["current_route"] = None
    task["completed_at"] = None
    task["result_file"] = None
    task["changed_files"] = []
    task["validation_results"] = []
    task["history"].append(
        {
            "at": now_utc(),
            "event": "reset",
            "recovered_subtasks": recovered_subtasks,
            "removed_learning_files": removed_learning_files,
        }
    )
    append_event(
        manifest,
        "task_reset",
        task_id=task["id"],
        recovered_subtasks=recovered_subtasks,
        removed_learning_files=removed_learning_files,
    )
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
    # Direct guarded cleanup must not leave a pointer to a deleted plan.
    active_pointer = Path(manifest["repo_root"]) / manifest["work_root"] / ".active-plan.json"
    if active_pointer.is_file() and not active_pointer.is_symlink():
        try:
            active_record = read_json(active_pointer)
        except PlanError:
            active_record = None
        if isinstance(active_record, dict) and active_record.get("plan_id") == manifest.get("plan_id"):
            try:
                active_pointer.unlink()
            except FileNotFoundError:
                pass
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


def command_subtask_start(args: argparse.Namespace) -> None:
    plan_dir, manifest = load_plan(args.plan)
    subtask = set_subtask_state(
        plan_dir,
        manifest,
        args.task,
        args.subtask,
        "in_progress",
    )
    print(json.dumps(subtask, ensure_ascii=False, indent=2))


def command_subtask_complete(args: argparse.Namespace) -> None:
    plan_dir, manifest = load_plan(args.plan)
    subtask = set_subtask_state(
        plan_dir,
        manifest,
        args.task,
        args.subtask,
        "completed",
    )
    print(json.dumps(subtask, ensure_ascii=False, indent=2))


def command_subtask_reset(args: argparse.Namespace) -> None:
    plan_dir, manifest = load_plan(args.plan)
    subtask = set_subtask_state(
        plan_dir,
        manifest,
        args.task,
        args.subtask,
        "pending",
    )
    print(json.dumps(subtask, ensure_ascii=False, indent=2))


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


def command_route_set(args: argparse.Namespace) -> None:
    plan_dir, manifest = load_plan(args.plan)
    task = find_task(manifest, args.task)
    if task.get("status") == "in_progress":
        raise PlanError("Cannot change route while the task is in progress; use runner --takeover")
    if args.provider:
        task["provider"] = args.provider
    if args.model_tier:
        task["model_tier"] = args.model_tier
    if args.effort:
        task["reasoning_effort"] = args.effort
    if args.unblock and task.get("status") == "blocked":
        task["status"] = "pending"
    task["deferred_until"] = None
    task["current_route"] = None
    append_event(
        manifest,
        "task_route_changed",
        task_id=task["id"],
        provider=task["provider"],
        model_tier=task["model_tier"],
        reasoning_effort=task["reasoning_effort"],
    )
    save_manifest(plan_dir, manifest)
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

    subtask_start = sub.add_parser(
        "subtask-start",
        help="Checkpoint one resumable subtask as in progress",
    )
    subtask_start.add_argument("--plan", required=True)
    subtask_start.add_argument("--task", required=True)
    subtask_start.add_argument("--subtask", required=True)
    subtask_start.set_defaults(func=command_subtask_start)

    subtask_complete = sub.add_parser(
        "subtask-complete",
        help="Checkpoint one resumable subtask as completed",
    )
    subtask_complete.add_argument("--plan", required=True)
    subtask_complete.add_argument("--task", required=True)
    subtask_complete.add_argument("--subtask", required=True)
    subtask_complete.set_defaults(func=command_subtask_complete)

    subtask_reset = sub.add_parser(
        "subtask-reset",
        help="Reset one resumable subtask to pending",
    )
    subtask_reset.add_argument("--plan", required=True)
    subtask_reset.add_argument("--task", required=True)
    subtask_reset.add_argument("--subtask", required=True)
    subtask_reset.set_defaults(func=command_subtask_reset)

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

    route_set = sub.add_parser("route-set", help="Persist a new provider/model route for a task")
    route_set.add_argument("--plan", required=True)
    route_set.add_argument("--task", required=True)
    route_set.add_argument("--provider", choices=sorted(VALID_PROVIDERS))
    route_set.add_argument("--model-tier", choices=sorted(VALID_TIERS))
    route_set.add_argument("--effort", choices=sorted(VALID_EFFORTS))
    route_set.add_argument("--unblock", action="store_true")
    route_set.set_defaults(func=command_route_set)


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
