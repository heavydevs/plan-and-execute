#!/usr/bin/env python3
"""Deterministic plan-state manager for plan-and-execute.

The script intentionally uses only the Python standard library. It creates and
updates ephemeral planning workspaces without touching implementation files.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import copy
import ctypes
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator

import model_catalog
import model_catalogctl
import requestctl
import routingctl

SCHEMA_VERSION = 4
SUPPORTED_SCHEMA_VERSIONS = {1, 2, 3, 4}
SENTINEL = ".orchestrator-plan"
MANIFEST = "manifest.json"
CONFIG = "orchestrator.config.json"
WRITER_LOCK_FILE = ".plan-writer.lock"
PROJECTION_STATE_FILE = ".projection-state.json"
STAGING_DIRECTORY = ".staging"
WORK_ROOT_DEFAULT = ".ai-work"
REQUEST_FILE = "REQUEST.md"
GLOBAL_CONTEXT_FILE = "CONTEXT.md"
CONTEXT_DIRECTORY = "contexts"
LEARNING_DIRECTORY = "learnings"
VALID_PLAN_MODES = {"single_implementation", "standard"}
SECOND_PLAN_PATTERN = re.compile(
    r"\b(create|generate|produce|draft|build|write|prepare|author)\s+(a\s+|the\s+)?(second\s+plan|plan\s*2)\b",
    re.I,
)
MAX_SUPERSESSION_NOTE_CHARS = 320
MAX_AMENDMENT_CHARS = 400
WRITER_LOCK_GUARD_STALE_SECONDS = 10.0
SCOPED_DIGESTS_FROM_FLAG = "revise_flag"
# Top-level manifest keys rebuilt from the spec on `revise`; any other key is carried forward.
SPEC_OWNED_MANIFEST_KEYS = frozenset({
    "title", "summary", "plan_mode", "request_analysis", "requirements", "global_constraints",
    "execution_context", "plan_review", "autostart", "cleanup_on_success", "language", "spec_sha256",
})
_HELD_WRITER_LOCKS: dict[tuple[Path, int], int] = {}
_ACTIVE_WRITER_LOCK_NONCES: set[str] = set()
RECEIPT_VALIDATOR_EXTENSIONS: list[
    Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], list[str]]
] = []
VALID_PROVIDERS = {"auto", "claude", "codex", "antigravity", "gemini", "qwen", "kimi", "trae", "muse"}
VALID_TIERS = set(routingctl.TIER_ORDER)
VALID_EFFORTS = {"low", "medium", "high", "xhigh", "max"}
VALID_STATUSES = {"pending", "in_progress", "completed", "blocked"}
VALID_SUBTASK_STATUSES = {"pending", "in_progress", "completed"}
VALID_COMPLEXITIES = {"low", "medium", "high", "extreme"}
VALID_FAILURE_CLASSES = set(routingctl.FAILURE_CLASSES)
MAX_HARD_DECISIONS = 12
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
TRUST_CLASS_NORMATIVE = "normative_contract"
TRUST_CLASS_VALIDATED_LEARNING = "validated_learning"
TRUST_CLASS_VERSIONED_PATTERN = "versioned_pattern"
TRUST_CLASS_HYPOTHESIS = "failed_attempt_hypothesis"
VALID_LEARNING_TRUST_CLASSES = {TRUST_CLASS_VALIDATED_LEARNING}
VALID_HYPOTHESIS_STATUSES = {"open", "disproven", "invalidated", "promoted"}
MAX_ATTEMPT_HYPOTHESES = 8
MAX_HYPOTHESIS_CHARS = 280
MAX_HYPOTHESIS_REASON_CHARS = 240
MAX_HYPOTHESIS_REFS = 4
POLICY_OVERRIDE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "acceptance_or_validation_override",
        re.compile(
            r"\b(?:ignore|skip|bypass|override|relax|disable|waive|drop|remove)\s+"
            r"(?:[A-Za-z_-]+\s+){0,5}(?:acceptance(?:\s+criteria)?|validation(?:\s+commands?)?|required\s+checks?|delivery\s+gate)\b",
            re.I,
        ),
    ),
    (
        "unvalidated_completion_override",
        re.compile(
            r"\bmark\s+(?:the\s+)?task\s+(?:as\s+)?completed\s+without\s+(?:running\s+)?validation\b",
            re.I,
        ),
    ),
    (
        "premature_acceptance_override",
        re.compile(
            r"\b(?:acceptance(?:\s+criteria)?|validation|required\s+checks?|delivery\s+gate)\s+"
            r"(?:is|are|has|have)\s+(?:already\s+)?(?:satisfied|passed|complete|done)\b"
            r".{0,100}\b(?:report\s+completion|mark\s+(?:the\s+)?task|finish\s+now|complete\s+directly)\b",
            re.I,
        ),
    ),
    (
        "permission_or_sandbox_override",
        re.compile(
            r"(?:--dangerously-skip-permissions|"
            r"\b(?:skip_permissions|trust_workspace|disable_approval)\s*[:=]\s*true\b|"
            r"\b(?:approval_mode|permission_mode)\s*[:=]\s*(?:yolo|bypass|unrestricted)\b|"
            r"\b(?:disable|bypass|turn\s+off)\s+(?:the\s+)?(?:sandbox|permission(?:\s+checks?)?|approval(?:\s+gate)?)\b|"
            r"\b(?:widen|escalate|grant\s+(?:full|root|admin|unrestricted))\s+permissions?\b)",
            re.I,
        ),
    ),
    (
        "provider_policy_override",
        re.compile(
            r"(?:\b(?:override|bypass|change|modify|ignore|replace)\s+(?:the\s+)?(?:provider|routing|frontier)\s+(?:policy|order|ladder|gate)\b|"
            r"\b(?:set|switch|rewrite)\s+(?:provider_order|allow_provider_fallback)\b|"
            r"\bforce\s+provider\s*[:=]?\s*(?:claude|codex|antigravity|gemini|qwen|kimi|trae|muse|frontier)\b)",
            re.I,
        ),
    ),
)
SINGLE_TASK_CONTEXT_PATTERN = re.compile(
    r"\bonly\s+(?:for\s+)?(?:todo|task)\s+[A-Za-z0-9_-]{1,12}\b",
    re.I,
)
RECEIPT_SECRET_PATTERN = re.compile(
    r"(?:sk-[A-Za-z0-9_-]{12,}|Authorization\s*:\s*(?:Bearer|Basic)\s+[^\s<]+|ghp_[A-Za-z0-9]{20,})",
    re.I,
)
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
            if "supersession_note" in item and item.get("supersession_note") is not None:
                note = ensure_text(
                    item.get("supersession_note"),
                    f"Requirement {requirement_id} supersession_note",
                )
                if len(note) > MAX_SUPERSESSION_NOTE_CHARS:
                    raise PlanError(
                        f"Requirement {requirement_id} supersession_note exceeds "
                        f"{MAX_SUPERSESSION_NOTE_CHARS} characters"
                    )
                requirement["supersession_note"] = note
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


def normalize_hard_decisions(raw: Any) -> list[dict[str, Any]]:
    """Optional decision-first planning evidence: hard decisions resolved by a
    stronger route before the mechanical plan was written."""
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise PlanError("request_analysis.hard_decisions must be a list")
    if len(raw) > MAX_HARD_DECISIONS:
        raise PlanError(f"request_analysis.hard_decisions may hold at most {MAX_HARD_DECISIONS} items")
    decisions: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise PlanError(f"request_analysis.hard_decisions[{index}] must be an object")
        decision_id = str(item.get("id", "")).strip().upper() or f"HD{index + 1:03d}"
        if not re.fullmatch(r"HD\d{3}", decision_id):
            raise PlanError(f"request_analysis.hard_decisions[{index}].id must look like HD001")
        if decision_id in seen:
            raise PlanError(f"request_analysis.hard_decisions duplicates id {decision_id}")
        seen.add(decision_id)
        route_used = str(item.get("route_used", "")).strip().lower()
        if route_used:
            parts = route_used.split("/")
            if len(parts) == 2:
                parts[0] = routingctl.normalize_tier(parts[0])
                route_used = "/".join(parts)
            if len(parts) != 2 or parts[0] not in VALID_TIERS or parts[1] not in VALID_EFFORTS:
                raise PlanError(
                    f"request_analysis.hard_decisions[{index}].route_used must be '<tier>/<effort>'"
                )
        decisions.append(
            {
                "id": decision_id,
                "decision": ensure_text(item.get("decision"), f"hard_decisions[{index}].decision"),
                "rationale": ensure_text(item.get("rationale"), f"hard_decisions[{index}].rationale"),
                "route_used": route_used,
                "source_refs": ensure_str_list(item.get("source_refs"), f"hard_decisions[{index}].source_refs"),
            }
        )
    return decisions


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
        "hard_decisions": normalize_hard_decisions(raw.get("hard_decisions")),
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
    override_kind = detect_policy_override_note(text)
    if override_kind is not None:
        raise PlanError(
            f"{field}.text cannot alter acceptance, permissions, or provider policy ({override_kind})"
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
    for index, item in enumerate(global_items):
        if SINGLE_TASK_CONTEXT_PATTERN.search(item["text"]) or SINGLE_TASK_CONTEXT_PATTERN.search(item["necessity"]):
            raise PlanError(
                f"execution_context.global.items[{index}] applies to a single TODO and belongs in that task definition, not universal CONTEXT.md"
            )
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
        tmp = Path(handle.name)
    try:
        replace_with_retry(tmp, path)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


def replace_with_retry(source: Path, target: Path, attempts: int = 12) -> None:
    """os.replace denies access (WinError 5/32) while an editor, indexer or scanner briefly holds the target.

    A runner that died on that single transient error left its task in_progress for hours, so retry for a few seconds.
    """
    for attempt in range(attempts):
        try:
            os.replace(source, target)
            return
        except PermissionError:
            if attempt == attempts - 1:
                raise
            time.sleep(min(0.05 * 2 ** attempt, 1.0))


def _unique_json_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise PlanError(f"Duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _reject_non_finite_json(token: str) -> Any:
    raise PlanError(f"Non-finite JSON constant is not allowed: {token!r}")


def parse_strict_json(raw: str, source: str = "JSON") -> Any:
    try:
        return json.loads(
            raw,
            object_pairs_hook=_unique_json_pairs,
            parse_constant=_reject_non_finite_json,
        )
    except json.JSONDecodeError as exc:
        raise PlanError(f"Invalid JSON in {source}: {exc}") from exc


def atomic_write_json(path: Path, data: Any) -> None:
    try:
        serialized = json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    except ValueError as exc:
        raise PlanError(f"Cannot serialize non-finite JSON to {path}: {exc}") from exc
    atomic_write_text(path, serialized)


def read_json(path: Path) -> Any:
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise PlanError(f"File not found: {path}") from exc
    except OSError as exc:
        raise PlanError(f"Cannot read {path}: {exc}") from exc
    return parse_strict_json(raw, str(path))


def canonical_json_sha256(data: Any) -> str:
    try:
        encoded = json.dumps(
            data, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
        ).encode("utf-8")
    except ValueError as exc:
        raise PlanError(f"Cannot hash non-finite JSON payload: {exc}") from exc
    return hashlib.sha256(encoded).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _kernel32() -> Any:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)  # type: ignore[attr-defined]
    kernel32.OpenProcess.restype = ctypes.c_void_p
    kernel32.OpenProcess.argtypes = (ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong)
    kernel32.CloseHandle.argtypes = (ctypes.c_void_p,)
    kernel32.GetExitCodeProcess.argtypes = (ctypes.c_void_p, ctypes.c_void_p)
    kernel32.GetProcessTimes.argtypes = (ctypes.c_void_p,) * 5
    return kernel32


def _pid_is_alive(pid: int) -> bool:
    if not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0:
        return False
    if os.name == "nt":
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        ERROR_ACCESS_DENIED = 5
        STILL_ACTIVE = 259
        kernel32 = _kernel32()
        handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not handle:
            # A protected or elevated owner refuses the query but is still alive.
            return ctypes.get_last_error() == ERROR_ACCESS_DENIED  # type: ignore[attr-defined]
        try:
            exit_code = ctypes.c_ulong()
            if not kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                return True
            return exit_code.value == STILL_ACTIVE
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False


def _process_start_token(pid: int) -> str | None:
    """Opaque process creation-time token that tells a live lock owner from a reused PID."""
    if not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0:
        return None
    if os.name == "nt":
        kernel32 = _kernel32()
        handle = kernel32.OpenProcess(0x1000, False, pid)
        if not handle:
            return None
        try:
            times = [ctypes.c_ulonglong() for _ in range(4)]
            if not kernel32.GetProcessTimes(handle, *(ctypes.byref(item) for item in times)):
                return None
            return f"nt:{times[0].value}"
        finally:
            kernel32.CloseHandle(handle)
    try:
        with open(f"/proc/{pid}/stat", "rb") as handle_file:
            raw = handle_file.read().decode("ascii", "replace")
        # Field 22 (starttime); fields after the parenthesised command start at field 3.
        return f"proc:{raw.rsplit(')', 1)[1].split()[19]}"
    except (OSError, IndexError):
        return None


def _unlink_with_retry(path: Path, attempts: int = 20) -> bool:
    """Remove a lock/guard file; Windows may briefly deny deletion while a reader holds it open."""
    for attempt in range(attempts):
        try:
            path.unlink()
            return True
        except FileNotFoundError:
            return True
        except PermissionError:
            if attempt == attempts - 1:
                return False
            time.sleep(0.05)
    return False


def _writer_lock_is_stale(raw: str, age: float, stale_seconds: float) -> bool:
    try:
        info = json.loads(raw) if raw.strip() else None
    except ValueError:
        info = None
    if not isinstance(info, dict):
        # Torn, empty or foreign content: a writer finishes its payload within microseconds.
        return age >= 0.5
    owner_host = info.get("hostname")
    owner_pid = info.get("pid")
    if owner_host == socket.gethostname() and isinstance(owner_pid, int) and not isinstance(owner_pid, bool):
        if owner_pid == os.getpid():
            # This process cannot be waiting on itself: a lock left by a failed release is
            # stale unless another thread of this process holds that exact acquisition.
            return info.get("nonce") not in _ACTIVE_WRITER_LOCK_NONCES
        if not _pid_is_alive(owner_pid):
            return True
        recorded = info.get("process_start")
        if isinstance(recorded, str) and recorded:
            current = _process_start_token(owner_pid)
            return current is not None and current != recorded
        # A live same-host owner is never stolen by age alone (it may be a slow writer).
        return False
    return age >= stale_seconds


def _remove_stale_takeover_guard(guard: Path) -> None:
    """Drop a guard left by a crashed contender; rename-and-verify so a fresh guard survives."""
    try:
        observed = guard.read_text(encoding="utf-8")
        if time.time() - guard.stat().st_mtime < WRITER_LOCK_GUARD_STALE_SECONDS:
            return
    except (OSError, UnicodeError):
        return
    tombstone = guard.with_name(f"{guard.name}.{uuid.uuid4().hex}.stale")
    try:
        os.rename(guard, tombstone)
    except OSError:
        return
    try:
        if tombstone.read_text(encoding="utf-8") != observed:
            # A fresh guard replaced the stale one meanwhile: put it back without clobbering.
            try:
                os.link(tombstone, guard)
            except OSError:
                pass
    except (OSError, UnicodeError):
        pass
    _unlink_with_retry(tombstone)


def _take_over_stale_writer_lock(lock_path: Path, observed: str) -> bool:
    """Remove the inspected stale lock only if it is still that lock, under a takeover guard.

    Without the guard two contenders that both read the same stale lock could each remove
    it, and the slower one would delete the faster one's fresh lock. Returns True when the
    inspected lock is gone, False when the guard is busy or the lock could not be removed.
    """
    guard = lock_path.with_name(lock_path.name + ".takeover")
    token = uuid.uuid4().hex
    try:
        guard_fd = os.open(str(guard), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        _remove_stale_takeover_guard(guard)
        return False
    try:
        os.write(guard_fd, token.encode("ascii"))
    finally:
        os.close(guard_fd)
    try:
        try:
            current = lock_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return True
        if current != observed:
            return True
        return _unlink_with_retry(lock_path)
    finally:
        try:
            ours = guard.read_text(encoding="utf-8") == token
        except (OSError, UnicodeError):
            ours = False
        if ours:
            _unlink_with_retry(guard)


@contextmanager
def plan_writer_lock(
    plan_dir: Path,
    *,
    timeout_seconds: float = 5.0,
    stale_seconds: float = 300.0,
) -> Iterator[Path]:
    """Single-writer filesystem lock for one plan workspace (re-entrant per thread).

    The lock file is created with O_EXCL. A lock is stale when its same-host owner process
    is gone (or its PID was reused), when it is unreadable for more than 0.5 s, or when a
    lock from another host is older than ``stale_seconds``. Stale locks are taken over
    under a takeover guard so two contenders cannot both win.
    """
    lock_dir = plan_dir.resolve()
    lock_path = lock_dir / WRITER_LOCK_FILE
    key = (lock_dir, threading.get_ident())
    held = _HELD_WRITER_LOCKS.get(key, 0)
    if held > 0:
        _HELD_WRITER_LOCKS[key] = held + 1
        try:
            yield lock_path
        finally:
            _HELD_WRITER_LOCKS[key] -= 1
            if _HELD_WRITER_LOCKS[key] <= 0:
                _HELD_WRITER_LOCKS.pop(key, None)
        return

    deadline = time.monotonic() + max(0.0, float(timeout_seconds))
    nonce = uuid.uuid4().hex
    payload = json.dumps(
        {
            "pid": os.getpid(),
            "hostname": socket.gethostname(),
            "acquired_at": now_utc(),
            "nonce": nonce,
            "process_start": _process_start_token(os.getpid()),
        },
        ensure_ascii=False,
    ) + "\n"
    stale_but_kept = False
    while True:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            try:
                raw_lock = lock_path.read_text(encoding="utf-8")
                age = time.time() - lock_path.stat().st_mtime
            except FileNotFoundError:
                continue
            except (OSError, UnicodeError):
                # Unreadable right now (e.g. Windows sharing violation): wait and retry.
                raw_lock, age = None, 0.0
            stale_but_kept = False
            if raw_lock is not None and _writer_lock_is_stale(raw_lock, age, stale_seconds):
                if _take_over_stale_writer_lock(lock_path, raw_lock):
                    continue
                stale_but_kept = True
            if time.monotonic() >= deadline:
                if stale_but_kept:
                    raise PlanError(
                        f"Stale plan writer lock could not be taken over before the timeout: {lock_path}"
                    )
                raise PlanError(
                    f"Plan writer lock is held by another writer: {lock_path} "
                    "(remove it only after confirming its owner process has exited)"
                )
            time.sleep(0.05)
        else:
            try:
                os.write(fd, payload.encode("utf-8"))
            finally:
                os.close(fd)
            _HELD_WRITER_LOCKS[key] = 1
            _ACTIVE_WRITER_LOCK_NONCES.add(nonce)
            break
    try:
        yield lock_path
    finally:
        _HELD_WRITER_LOCKS.pop(key, None)
        _ACTIVE_WRITER_LOCK_NONCES.discard(nonce)
        try:
            still_ours = lock_path.read_text(encoding="utf-8") == payload
        except (OSError, UnicodeError):
            still_ours = True
        # Never raise from release: that would hide the caller's original error. A lock this
        # process failed to delete is recognised as its own leftover by the next acquisition.
        if still_ours and not _unlink_with_retry(lock_path):
            print(f"warning: could not remove plan writer lock {lock_path}", file=sys.stderr)


def markdown_list(items: Iterable[str], empty: str = "- None") -> str:
    materialized = list(items)
    return "\n".join(f"- {item}" for item in materialized) if materialized else empty


def absolute_lexical(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path.expanduser())))


def reject_symlink_components(root: Path, relative: Path, field: str) -> None:
    current = root
    for part in relative.parts:
        current = current / part
        # `exists()` is false for dangling links. Still reject them before any
        # later filesystem operation can follow a newly introduced target.
        if current.is_symlink():
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
    """Default orchestrator config.

    Concrete Claude/Codex model ids, effort caps, effort-less models, and
    escalation ladders come from `routingctl` (single catalog source); the
    values below are structural defaults that the catalog overlays.
    """
    return routingctl.configure_config({
        "version": 1,
        "provider_order": ["claude", "codex"],
        "allow_provider_fallback": True,
        "strict_fresh_context": True,
        "auto_cleanup": True,
        "functional_failures_per_provider": 4,
        "task_timeout_seconds": 0,
        "task_idle_timeout_seconds": 0,
        "validation_timeout_seconds": 1800,
        "validation_hard_timeout_seconds": 0,
        "stream_provider_output": True,
        "rate_limit": {
            "auto_wait": True,
            "wait_seconds": 300,
            "max_wait_cycles": 0,
        },
        "claude": {
            "command": "claude",
            "models": {},
            "permission_mode": "auto",
            "max_effort_by_tier": {},
            # 0 disables the flag. When set, `--max-turns` bounds one worker run;
            # exhaustion is recorded as a resumable `budget` failure, not a defect.
            "max_turns": 0,
            # 0 disables. When set, `--max-budget-usd` caps one worker run's API
            # spend (subagent spend counts); exhaustion is a resumable `budget` failure.
            "max_budget_usd": 0,
            "extra_args": [],
        },
        "codex": {
            "command": "codex",
            "models": {},
            "sandbox": "workspace-write",
            "ignore_user_config": False,
            "max_effort_by_tier": {},
            # 0 disables the override. When set, enables Codex rollout budget
            # tracking for one worker run (features.rollout_budget.*).
            "rollout_token_budget": 0,
            "extra_args": [],
        },
        "antigravity": {
            # Google Antigravity CLI (`agy`), successor of the Gemini CLI. Headless
            # contract: -p <prompt> --output-format json --json-schema <schema>
            # --model <slug> --effort low|medium|high --print-timeout <duration>.
            "command": "agy",
            "models": {
                "economy": "default",
                "standard": "default",
                "strong": "default",
                "max": "default",
            },
            "skip_permissions": True,
            "summary_skip_permissions": True,
            "sandbox": False,
            "summary_sandbox": True,
            # agy kills a print-mode run after 5 minutes by default. "auto" follows
            # task_timeout_seconds (or 12h when the runner has no limit).
            "print_timeout": "auto",
            "retry_exit_codes": [],
            "max_effort_by_tier": {
                "economy": "high",
                "standard": "high",
                "strong": "high",
                "max": "high",
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
        "muse": {
            # Muse Code native harness (`muse exec --json`). Models, effort caps and
            # effortless models come from the bootstrap catalog; the permission
            # opt-ins stay off until a provider config enables them.
            "command": "muse",
            **model_catalog.provider_config_mapping("muse"),
            "trust_workspace": False,
            "disable_approval": False,
            "retry_exit_codes": [],
            "extra_args": [],
        },
        "summary": {
            "provider": "auto",
            "model_tier": "economy",
            "reasoning_effort": "low",
        },
    })


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


def normalize_design_route(raw: Any, task_id: str, complexity: str) -> dict[str, str] | None:
    """Optional two-phase leaf: a stronger design pass before implementation.

    Allowed only for `high` complexity TODOs. The design worker reads the task
    definition plus assigned context and writes a bounded design note; the
    implementation worker then runs at the task's own (usually cheaper) route.
    """
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise PlanError(f"Task {task_id}: design_route must be an object with model_tier and reasoning_effort")
    if complexity != "high":
        raise PlanError(
            f"Task {task_id}: design_route is only allowed on high-complexity TODOs; "
            "route lower-complexity leaves directly"
        )
    tier = routingctl.normalize_tier(raw.get("model_tier", "strong"))
    effort = str(raw.get("reasoning_effort", "medium")).strip().lower()
    if tier not in VALID_TIERS:
        raise PlanError(f"Task {task_id}: design_route.model_tier {tier!r} is invalid")
    if effort not in VALID_EFFORTS:
        raise PlanError(f"Task {task_id}: design_route.reasoning_effort {effort!r} is invalid")
    if effort == "low":
        raise PlanError(f"Task {task_id}: design_route.reasoning_effort may not be low; design is reasoning work")
    return {"model_tier": tier, "reasoning_effort": effort}


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


def valid_validation_job_id(value: Any) -> bool:
    return (
        isinstance(value, str)
        and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", value) is not None
        and value.upper() not in {"CON", "PRN", "AUX", "NUL", *[f"COM{i}" for i in range(1, 10)], *[f"LPT{i}" for i in range(1, 10)]}
    )


def normalize_scoped_input_digests(raw: Any, field: str) -> dict[str, str]:
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise PlanError(f"{field} must be an object mapping repository-relative paths to SHA-256 digests")
    normalized: dict[str, str] = {}
    for key, value in raw.items():
        rel = checked_relative_path(ensure_text(key, f"{field} key"), field)
        digest = ensure_text(value, f"{field}[{rel}]").lower()
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise PlanError(f"{field}[{rel}] must be a 64-character lowercase hex SHA-256 digest")
        normalized[rel] = digest
    return normalized


def normalize_research_metadata(
    raw: Any,
    task_id: str,
    subtasks: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if raw is None:
        return None
    field = f"Task {task_id} research_metadata"
    if not isinstance(raw, dict):
        raise PlanError(f"{field} must be an object")
    allowed = {
        "former_kind",
        "prepared_report",
        "prepared_report_sha256",
        "source_reports",
        "research_status",
        "implementation_status",
        "independent_review_status",
    }
    unknown = set(raw) - allowed
    if unknown:
        raise PlanError(f"{field} contains unsupported fields: {', '.join(sorted(unknown))}")
    result: dict[str, Any] = {}
    if raw.get("former_kind") is not None:
        former_kind = str(raw["former_kind"]).strip().lower()
        if former_kind not in {"research", "implementation", "review"}:
            raise PlanError(f"{field}.former_kind is invalid: {former_kind!r}")
        result["former_kind"] = former_kind
    if raw.get("prepared_report") is not None:
        result["prepared_report"] = checked_relative_path(
            ensure_text(raw["prepared_report"], f"{field}.prepared_report"),
            f"{field}.prepared_report",
        )
    if raw.get("prepared_report_sha256") is not None:
        digest = ensure_text(raw["prepared_report_sha256"], f"{field}.prepared_report_sha256").lower()
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise PlanError(f"{field}.prepared_report_sha256 must be a 64-character hex SHA-256")
        result["prepared_report_sha256"] = digest
    if raw.get("source_reports") is not None:
        result["source_reports"] = [
            checked_relative_path(item, f"{field}.source_reports")
            for item in ensure_str_list(raw["source_reports"], f"{field}.source_reports")
        ]
    if raw.get("research_status") is not None:
        rstatus = str(raw["research_status"]).strip().lower()
        if rstatus not in {"prepared", "none", "refreshed"}:
            raise PlanError(f"{field}.research_status is invalid: {rstatus!r}")
        result["research_status"] = rstatus
    if raw.get("implementation_status") is not None:
        istatus = str(raw["implementation_status"]).strip().lower()
        if istatus != "pending":
            raise PlanError(
                f"{field}.implementation_status must be 'pending' on a new or transformed task; "
                "prepared research is not implementation completion"
            )
        result["implementation_status"] = istatus
    if raw.get("independent_review_status") is not None:
        rev_status = str(raw["independent_review_status"]).strip().lower()
        if rev_status != "pending":
            raise PlanError(
                f"{field}.independent_review_status must be 'pending' on a new or transformed task; "
                "prepared research is not independent-review completion"
            )
        result["independent_review_status"] = rev_status
    if result.get("former_kind") == "research":
        report_path = result.get("prepared_report")
        if not report_path:
            raise PlanError(
                f"Task {task_id}: transformed research task requires research_metadata.prepared_report"
            )
        subtask_texts = " ".join(
            f"{item.get('title', '')} {item.get('objective', '')}" for item in subtasks
        )
        if report_path not in subtask_texts:
            raise PlanError(
                f"Task {task_id}: transformed research task subtasks must instruct implementation "
                f"from its assigned report {report_path!r}"
            )
    return result


def normalize_task(
    raw: Any,
    index: int,
    known_requirement_ids: set[str],
) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise PlanError(f"tasks[{index}] must be an object")
    task_id = normalize_task_id(raw.get("id", index + 1))
    raw_status = str(raw.get("status", "")).strip().lower()
    if raw_status == "completed":
        raise PlanError(
            f"Task {task_id}: spec tasks cannot start as completed; prepared research or spec metadata "
            "is not proof of implementation completion"
        )
    title = str(raw.get("title", "")).strip()
    objective = str(raw.get("objective", "")).strip()
    if not title or not objective:
        raise PlanError(f"Task {task_id} requires title and objective")

    provider = str(raw.get("provider", "auto")).strip().lower()
    tier = routingctl.normalize_tier(raw.get("model_tier", "standard"))
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
    timeout_override = {}
    for key in ("validation_timeout_seconds", "validation_hard_timeout_seconds", "task_idle_timeout_seconds"):
        if key in raw:
            timeout = raw[key]
            if type(timeout) is not int or not 0 <= timeout <= 604800:
                raise PlanError(f"Task {task_id}: {key} must be an integer in 0..604800")
            timeout_override[key] = timeout
    if "validation_jobs" in raw and not isinstance(raw["validation_jobs"], list):
        raise PlanError(f"Task {task_id}: validation_jobs must be an array")
    jobs = ensure_str_list(raw.get("validation_jobs"), f"Task {task_id} validation_jobs")
    if len(jobs) > 32 or len(jobs) != len(set(jobs)) or any(not valid_validation_job_id(job) for job in jobs):
        raise PlanError(f"Task {task_id}: validation_jobs must contain at most 32 distinct safe job IDs")
    if not acceptance:
        raise PlanError(f"Task {task_id} requires at least one acceptance criterion")
    if not validations and not jobs:
        raise PlanError(f"Task {task_id} requires at least one validation command or job")

    context_boundary = normalize_context_boundary(raw.get("context_boundary"), task_id)
    subtasks = normalize_subtasks(raw.get("subtasks"), task_id)
    learning_targets = normalize_learning_targets(raw.get("learning_targets"), task_id)
    design_route = normalize_design_route(raw.get("design_route"), task_id, complexity)
    review_of = (
        normalize_task_id(raw["review_of"])
        if "review_of" in raw and raw["review_of"] is not None
        else None
    )
    scoped_inputs = [
        checked_relative_path(item, f"Task {task_id} scoped_inputs")
        for item in ensure_str_list(raw.get("scoped_inputs"), f"Task {task_id} scoped_inputs")
    ]
    scoped_input_digests = normalize_scoped_input_digests(
        raw.get("scoped_input_digests"), f"Task {task_id} scoped_input_digests"
    )
    research_metadata = normalize_research_metadata(raw.get("research_metadata"), task_id, subtasks)
    from workload_routing import WORKLOADS
    workload = raw.get("workload", "implementation")
    if workload not in WORKLOADS:
        raise PlanError(f"Task {task_id}: unsupported workload {workload!r}")

    return {
        "id": task_id,
        "slug": slugify(title, f"task-{task_id}"),
        "title": title,
        "objective": objective,
        "requirement_ids": requirement_ids,
        "complexity": complexity,
        **({"workload": workload} if "workload" in raw else {}),
        "atomicity_rationale": atomicity_rationale,
        "context_boundary": context_boundary,
        "scope": normalize_scope(raw.get("scope"), f"Task {task_id} scope"),
        "dependencies": dependencies,
        "implementation_guidance": ensure_str_list(
            raw.get("implementation_guidance"), f"Task {task_id} implementation_guidance"
        ),
        "acceptance_criteria": acceptance,
        "validation_commands": validations,
        **({"validation_jobs": jobs} if jobs else {}),
        **timeout_override,
        **({"review_of": review_of} if review_of is not None else {}),
        **(
            {"requires_independent_review": bool(raw["requires_independent_review"])}
            if "requires_independent_review" in raw
            else {}
        ),
        **({"scoped_inputs": scoped_inputs} if scoped_inputs else {}),
        **({"scoped_input_digests": scoped_input_digests} if scoped_input_digests else {}),
        **({"research_metadata": research_metadata} if research_metadata is not None else {}),
        "provider": provider,
        "model_tier": tier,
        "reasoning_effort": effort,
        "design_route": design_route,
        "design_phase": (
            {"status": "pending", "note_file": None, "route": None, "completed_at": None}
            if design_route
            else None
        ),
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
        "failure_classes": [],
        "rate_limit_events": 0,
        "current_route": None,
        "started_at": None,
        "completed_at": None,
        "last_error": None,
        "history": [],
        "changed_files": [],
        "validation_results": [],
        "result_file": None,
        "current_receipt": None,
        "receipt_history": [],
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
        review_of = task.get("review_of")
        if review_of is not None:
            review_target = normalize_task_id(review_of)
            if review_target == task["id"]:
                raise PlanError(f"Task {task['id']} cannot review itself")
            if review_target not in known:
                raise PlanError(
                    f"Task {task['id']} is an orphan review referencing unknown task {review_target}"
                )
            if review_target not in task["dependencies"]:
                raise PlanError(
                    f"Task {task['id']} reviews task {review_target} and must depend on it"
                )
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
        note = f" _(superseded: {item['supersession_note']})_" if item.get("supersession_note") else ""
        lines.append(
            f"- **{item['id']}** [{item['priority']}; {item['source']}; request parts: {request_parts}] "
            f"{item['text']}{note}"
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

## Hard decisions

{render_hard_decisions(analysis.get('hard_decisions', []))}

## Decomposition strategy

{analysis['decomposition_strategy']}
"""


def render_hard_decisions(items: list[dict[str, Any]]) -> str:
    if not items:
        return "- None (no decision-first pass was needed)"
    lines = []
    for item in items:
        route = f" [{item['route_used']}]" if item.get("route_used") else ""
        refs = f" (refs: {', '.join(item['source_refs'])})" if item.get("source_refs") else ""
        lines.append(f"- **{item['id']}**{route} {item['decision']} — {item['rationale']}{refs}")
    return "\n".join(lines)


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
    workload_line = f'workload: "{task["workload"]}"\n' if task.get("workload") else ""
    return f"""---
task_id: "{task['id']}"
plan_id: "{plan_id}"
status: "{task['status']}"
provider: "{task['provider']}"
model_tier: "{task['model_tier']}"
reasoning_effort: "{task['reasoning_effort']}"
{workload_line}complexity: "{task['complexity']}"
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
{chr(10).join(f'- Supervised job `{job}`: start through `jobctl.py` and return; the runner waits outside model context.' for job in task.get('validation_jobs', []))}

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


def task_contract_payload(
    task: dict[str, Any],
    *,
    dependency_digests: dict[str, str] | None = None,
    scoped_input_digests: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Canonical contract projection of a task (excludes mutable runtime state)."""
    deps = [str(dep) for dep in task.get("dependencies", [])]
    dep_contracts = {
        dep: dependency_digests[dep]
        for dep in sorted(deps)
        if dependency_digests and dep in dependency_digests
    }
    raw_scoped = (
        scoped_input_digests
        if scoped_input_digests is not None
        else task.get("scoped_input_digests")
    )
    scoped_map = (
        {str(k): str(v) for k, v in sorted(raw_scoped.items())}
        if isinstance(raw_scoped, dict)
        else {}
    )
    rm = task.get("research_metadata") if isinstance(task.get("research_metadata"), dict) else None
    research_contract = (
        {
            "former_kind": rm.get("former_kind"),
            "prepared_report": rm.get("prepared_report"),
            "prepared_report_sha256": rm.get("prepared_report_sha256"),
            "source_reports": sorted(str(x) for x in rm.get("source_reports", [])),
        }
        if rm is not None
        else None
    )
    subtasks_contract = [
        {
            "id": str(sub.get("id", "")),
            "title": str(sub.get("title", "")),
            "objective": str(sub.get("objective", "")),
            "required": bool(sub.get("required", True)),
        }
        for sub in task.get("subtasks", [])
        if isinstance(sub, dict)
    ]
    return {
        "id": str(task.get("id", "")),
        "objective": str(task.get("objective", "")),
        "requirement_ids": list(task.get("requirement_ids", [])),
        "acceptance_criteria": list(task.get("acceptance_criteria", [])),
        "validation_commands": list(task.get("validation_commands", [])),
        "validation_jobs": list(task.get("validation_jobs", [])),
        "dependencies": deps,
        "dependency_contracts": dep_contracts,
        "scope": task.get("scope", {}),
        "context_files": list(task.get("context_files", [])),
        "scoped_inputs": sorted(str(x) for x in task.get("scoped_inputs", [])),
        "scoped_input_digests": scoped_map,
        "review_of": task.get("review_of"),
        "requires_independent_review": bool(task.get("requires_independent_review", False)),
        "research_contract": research_contract,
        "subtasks": subtasks_contract,
    }


def task_contract_digest(
    task: dict[str, Any],
    *,
    dependency_digests: dict[str, str] | None = None,
    scoped_input_digests: dict[str, str] | None = None,
) -> str:
    return canonical_json_sha256(
        task_contract_payload(
            task,
            dependency_digests=dependency_digests,
            scoped_input_digests=scoped_input_digests,
        )
    )


def compute_task_contract_digests(
    tasks: list[dict[str, Any]],
    *,
    scoped_input_digests_by_task: dict[str, dict[str, str]] | None = None,
) -> dict[str, str]:
    """Compute transitive contract digests over the task DAG."""
    by_id = {str(task["id"]): task for task in tasks}
    digests: dict[str, str] = {}
    visiting: set[str] = set()

    def compute(tid: str) -> str:
        if tid in digests:
            return digests[tid]
        if tid in visiting:
            raise PlanError(f"Dependency cycle detected at task {tid}")
        visiting.add(tid)
        task = by_id[tid]
        dep_map: dict[str, str] = {}
        for dep in task.get("dependencies", []):
            dep_id = str(dep)
            if dep_id in by_id:
                dep_map[dep_id] = compute(dep_id)
        visiting.remove(tid)
        override = (
            scoped_input_digests_by_task.get(tid)
            if scoped_input_digests_by_task is not None
            else None
        )
        digests[tid] = task_contract_digest(
            task,
            dependency_digests=dep_map,
            scoped_input_digests=override,
        )
        return digests[tid]

    for task in tasks:
        compute(str(task["id"]))
    return digests


def assign_task_contract_digests(
    tasks: list[dict[str, Any]],
    *,
    scoped_input_digests_by_task: dict[str, dict[str, str]] | None = None,
) -> dict[str, str]:
    digests = compute_task_contract_digests(
        tasks, scoped_input_digests_by_task=scoped_input_digests_by_task
    )
    for task in tasks:
        task["contract_digest"] = digests[str(task["id"])]
    return digests


def register_receipt_validator(
    validator: Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], list[str]],
) -> None:
    """Register an extension hook on the single receipt-validity function.

    Task 012 owns `validate_receipt`; later tasks (such as 018) extend it here
    rather than introducing a second receipt-validity function.
    """
    if validator not in RECEIPT_VALIDATOR_EXTENSIONS:
        RECEIPT_VALIDATOR_EXTENSIONS.append(validator)


def validate_receipt(
    receipt: Any,
    task: dict[str, Any],
    *,
    manifest: dict[str, Any] | None = None,
    scoped_input_digests: dict[str, str] | None = None,
    dependency_digests: dict[str, str] | None = None,
    expected_contract_digest: str | None = None,
    extra_validators: Iterable[
        Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], list[str]]
    ] | None = None,
    require_review_verdict: bool = False,
) -> dict[str, Any]:
    """Single authoritative receipt-validity function (owned by 012, extensible by 018).

    An explicit pending or non-approved review verdict always invalidates a receipt. A
    missing verdict is rejected only with ``require_review_verdict=True``: the runner's
    completion report schema cannot carry one, so a review task's own approval is gated by
    its declared validation commands (the delivery gate that verifies the reviewer
    dispatch) and by its dependency on the reviewed task.
    """
    task_id = str(task.get("id", ""))
    resolved_scoped = (
        dict(scoped_input_digests)
        if scoped_input_digests is not None
        else dict(task.get("scoped_input_digests") or {})
    )
    if expected_contract_digest is not None:
        expected = expected_contract_digest
    elif manifest is not None and isinstance(manifest.get("tasks"), list):
        overrides = {task_id: resolved_scoped} if scoped_input_digests is not None else None
        expected = compute_task_contract_digests(
            manifest["tasks"], scoped_input_digests_by_task=overrides
        ).get(task_id) or task_contract_digest(task, scoped_input_digests=resolved_scoped)
    elif dependency_digests is not None or scoped_input_digests is not None:
        expected = task_contract_digest(
            task,
            dependency_digests=dependency_digests,
            scoped_input_digests=resolved_scoped,
        )
    else:
        expected = str(task.get("contract_digest") or task_contract_digest(task))

    reasons: list[str] = []
    actual_digest = None
    if not isinstance(receipt, dict) or not receipt:
        return {
            "valid": False,
            "task_id": task_id,
            "expected_contract_digest": expected,
            "actual_contract_digest": None,
            "reasons": ["missing_or_invalid_receipt"],
        }

    if str(receipt.get("task_id", "")) != task_id:
        reasons.append(f"task_id_mismatch:{receipt.get('task_id')!r}")

    evidence_kind = str(receipt.get("evidence_kind", "")).strip().lower()
    source_kind = str(receipt.get("source", "")).strip().lower()
    if (
        evidence_kind == "prepared_research"
        or source_kind == "prepared_research"
        or receipt.get("prepared_research_only") is True
    ):
        reasons.append("prepared_research_is_not_completion_proof")

    if (
        receipt.get("historical") is True
        or receipt.get("superseded_by_generation") is not None
        or receipt.get("superseded_at") is not None
    ):
        reasons.append("historical_receipt_not_current")

    status = str(receipt.get("status", "")).strip().lower()
    if status != "completed":
        reasons.append(f"receipt_status_not_completed:{status or 'missing'}")

    actual_digest = receipt.get("contract_digest")
    if not isinstance(actual_digest, str) or not actual_digest.strip():
        reasons.append("missing_contract_digest")
    elif actual_digest != expected:
        reasons.append("contract_digest_mismatch")

    if resolved_scoped:
        receipt_inputs = receipt.get("scoped_input_digests")
        if not isinstance(receipt_inputs, dict):
            reasons.append("missing_scoped_input_digests")
        else:
            for rel, expected_sha in sorted(resolved_scoped.items()):
                if receipt_inputs.get(rel) != expected_sha:
                    reasons.append(f"scoped_input_mismatch:{rel}")

    if "acceptance_criteria" in receipt and receipt["acceptance_criteria"] != task.get("acceptance_criteria"):
        reasons.append("acceptance_criteria_mismatch")
    if "validation_commands" in receipt and receipt["validation_commands"] != task.get("validation_commands"):
        reasons.append("validation_commands_mismatch")
    if "validations" in receipt:
        validations = receipt["validations"]
        if not isinstance(validations, list):
            reasons.append("invalid_validations_field")
        elif any(isinstance(v, dict) and v.get("passed") is not True for v in validations):
            reasons.append("failed_validation_in_receipt")

    needs_review = bool(task.get("requires_independent_review") or receipt.get("requires_independent_review"))
    review_status = str(receipt.get("independent_review_status", "")).strip().lower()
    verdict = str(receipt.get("verdict", "")).strip().lower()
    if review_status == "pending" or verdict == "pending":
        reasons.append("independent_review_pending")
    elif (verdict and verdict != "approved") or (review_status and review_status != "approved"):
        reasons.append("independent_review_not_approved")
    elif needs_review and require_review_verdict and "approved" not in (verdict, review_status):
        reasons.append("independent_review_not_approved")

    context = {
        "manifest": manifest,
        "expected_contract_digest": expected,
        "scoped_input_digests": resolved_scoped,
        "dependency_digests": dependency_digests,
    }
    validators = list(RECEIPT_VALIDATOR_EXTENSIONS)
    if extra_validators is not None:
        validators.extend(extra_validators)
    for validator in validators:
        extra = validator(receipt, task, context)
        if extra:
            reasons.extend(str(item) for item in extra if str(item).strip())

    return {
        "valid": len(reasons) == 0,
        "task_id": task_id,
        "expected_contract_digest": expected,
        "actual_contract_digest": actual_digest if isinstance(actual_digest, str) else None,
        "reasons": reasons,
    }


def build_task_receipt(
    manifest: dict[str, Any],
    task: dict[str, Any],
    report: dict[str, Any] | None,
    result_file: str | None,
) -> dict[str, Any]:
    digest = task.get("contract_digest") or compute_task_contract_digests(manifest.get("tasks", [])).get(
        task["id"]
    )
    receipt: dict[str, Any] = {
        "schema_version": 1,
        "task_id": task["id"],
        "generation": manifest.get("generation"),
        "contract_digest": digest,
        "status": "completed",
        "historical": False,
        "completed_at": task.get("completed_at") or now_utc(),
        "result_file": result_file,
        "changed_files": list(task.get("changed_files", [])),
        "acceptance_criteria": list(task.get("acceptance_criteria", [])),
        "validation_commands": list(task.get("validation_commands", [])),
        "scoped_input_digests": dict(task.get("scoped_input_digests") or {}),
    }
    if isinstance(report, dict):
        # The runner's own validation results are authoritative; a worker's self-reported
        # checks (which may include non-gating, pre-existing failures) are kept for audit only.
        runner_results = report.get("validation_results")
        if isinstance(runner_results, list) and runner_results:
            receipt["validations"] = [
                {
                    "command": str(item.get("command", "")),
                    "passed": item.get("passed") is True,
                    **({"exit_code": item["exit_code"]} if "exit_code" in item else {}),
                }
                for item in runner_results
                if isinstance(item, dict)
            ]
        worker_checks = report.get("validations")
        if isinstance(worker_checks, list):
            failed = [
                str(item.get("command", ""))
                for item in worker_checks
                if isinstance(item, dict) and item.get("passed") is not True
            ]
            if failed:
                receipt["worker_reported_failed_validations"] = failed
        if report.get("verdict") is not None:
            receipt["verdict"] = report["verdict"]
        if report.get("independent_review_status") is not None:
            receipt["independent_review_status"] = report["independent_review_status"]
    if (
        task.get("requires_independent_review")
        and "verdict" not in receipt
        and "independent_review_status" not in receipt
    ):
        receipt["independent_review_gate"] = "declared_validation_commands"
    return receipt


def observe_scoped_input_digests(repo_root: Path, declared: dict[str, str]) -> dict[str, str]:
    """Hash each declared scoped input on disk; a CRLF checkout of an LF-pinned file still matches."""
    observed: dict[str, str] = {}
    for rel, expected in sorted(declared.items()):
        target = repo_root / rel
        if target.is_symlink() or not target.is_file():
            observed[rel] = "missing"
            continue
        actual = file_sha256(target)
        if actual != expected and lf_sha256(target) == expected:
            actual = expected
        observed[rel] = actual
    return observed


def validate_research_and_plan_mode(
    repo_root: Path | None,
    manifest: dict[str, Any],
    tasks: list[dict[str, Any]],
) -> list[str]:
    errors: list[str] = []
    plan_mode = manifest.get("plan_mode")
    if plan_mode is not None and plan_mode not in VALID_PLAN_MODES:
        errors.append(f"Unsupported plan_mode: {plan_mode!r}")

    has_second_plan_supersession = any(
        isinstance(req, dict)
        and isinstance(req.get("supersession_note"), str)
        and bool(re.search(r"(second\s+plan|plan\s*2|two[- ]plan)", req["supersession_note"], re.I))
        for req in manifest.get("requirements", [])
    )
    enforce_single_plan = plan_mode == "single_implementation" or has_second_plan_supersession

    root_dir = repo_root.resolve() if repo_root is not None and repo_root.is_dir() else None
    for task in tasks:
        task_id = str(task.get("id", "?"))
        if enforce_single_plan and task.get("status") in {"pending", "in_progress"}:
            combined = f"{task.get('title', '')} {task.get('objective', '')}"
            if SECOND_PLAN_PATTERN.search(combined):
                errors.append(
                    f"Task {task_id}: active task schedules creating a second plan in single_implementation mode"
                )
        rm = task.get("research_metadata")
        if rm is None:
            continue
        if not isinstance(rm, dict):
            errors.append(f"Task {task_id}: research_metadata must be an object")
            continue
        report_paths: list[str] = []
        prepared_report = rm.get("prepared_report")
        if prepared_report is not None:
            if not isinstance(prepared_report, str) or not prepared_report.strip():
                errors.append(f"Task {task_id}: research_metadata.prepared_report must be a path")
            else:
                report_paths.append(prepared_report)
        source_reports = rm.get("source_reports")
        if source_reports is not None:
            if not isinstance(source_reports, list):
                errors.append(f"Task {task_id}: research_metadata.source_reports must be a list")
            else:
                for item in source_reports:
                    if isinstance(item, str) and item.strip():
                        report_paths.append(item.strip())
                    else:
                        errors.append(f"Task {task_id}: invalid source_reports entry")
        if rm.get("former_kind") == "research":
            if not prepared_report:
                errors.append(
                    f"Task {task_id}: transformed research task requires research_metadata.prepared_report"
                )
            else:
                subtask_texts = " ".join(
                    f"{sub.get('title', '')} {sub.get('objective', '')}"
                    for sub in task.get("subtasks", [])
                    if isinstance(sub, dict)
                )
                if prepared_report not in subtask_texts:
                    errors.append(
                        f"Task {task_id}: transformed research task subtasks must reference assigned report {prepared_report}"
                    )
            if (
                task.get("status") == "completed"
                and not task.get("current_receipt")
                and not task.get("result_file")
                and int(task.get("attempts", 0)) == 0
            ):
                errors.append(
                    f"Task {task_id}: prepared research is not proof of implementation completion"
                )
        if root_dir is not None:
            for rel in dict.fromkeys(report_paths):
                try:
                    clean_rel = checked_relative_path(rel, f"Task {task_id} research report")
                    reject_symlink_components(root_dir, Path(clean_rel), f"Task {task_id} research report")
                except PlanError as exc:
                    errors.append(str(exc))
                    continue
                target = root_dir / clean_rel
                if not target.is_file():
                    errors.append(
                        f"Task {task_id}: depends on nonexistent research output: {clean_rel}"
                    )
                elif rel == prepared_report and rm.get("prepared_report_sha256"):
                    expected_sha = str(rm["prepared_report_sha256"]).lower()
                    if file_sha256(target) != expected_sha and lf_sha256(target) != expected_sha:
                        errors.append(
                            f"Task {task_id}: prepared_report hash mismatch for {clean_rel}"
                        )
    return errors


def _write_projection_state(plan_dir: Path, manifest: dict[str, Any]) -> None:
    if int(manifest.get("schema_version", 0) or 0) < 4:
        return
    generation = manifest.get("generation")
    if not isinstance(generation, int) or isinstance(generation, bool):
        return
    manifest_path = plan_dir / MANIFEST
    manifest_hash = file_sha256(manifest_path) if manifest_path.is_file() else None
    atomic_write_json(
        plan_dir / PROJECTION_STATE_FILE,
        {
            "schema_version": int(manifest["schema_version"]),
            "generation": generation,
            "manifest_sha256": manifest_hash,
            "status": "synced",
            "updated_at": now_utc(),
        },
    )


def _sync_context_projections(plan_dir: Path, execution_context: dict[str, Any]) -> tuple[list[str], list[str]]:
    rebuilt: list[str] = []
    removed: list[str] = []
    global_path = plan_dir / GLOBAL_CONTEXT_FILE
    if execution_context["global"]["decision"] == "create":
        atomic_write_text(global_path, render_global_context(execution_context))
        rebuilt.append(GLOBAL_CONTEXT_FILE)
    elif global_path.exists() and not global_path.is_symlink():
        global_path.unlink()
        removed.append(GLOBAL_CONTEXT_FILE)

    context_dir = plan_dir / CONTEXT_DIRECTORY
    expected_scoped: dict[str, dict[str, Any]] = {
        ctx["file"]: ctx for ctx in execution_context.get("scoped", [])
    }
    if expected_scoped:
        context_dir.mkdir(exist_ok=True)
        for rel, ctx in expected_scoped.items():
            atomic_write_text(plan_dir / rel, render_scoped_context(ctx))
            rebuilt.append(rel)
        for child in list(context_dir.iterdir()):
            rel = child.relative_to(plan_dir).as_posix()
            if rel not in expected_scoped and not child.is_symlink() and child.is_file():
                child.unlink()
                removed.append(rel)
    elif context_dir.is_dir() and not context_dir.is_symlink():
        for child in list(context_dir.iterdir()):
            rel = child.relative_to(plan_dir).as_posix()
            if child.is_file() and not child.is_symlink():
                child.unlink()
                removed.append(rel)
        try:
            context_dir.rmdir()
        except OSError:
            pass
    return rebuilt, removed


def _sync_projections_unlocked(
    plan_dir: Path,
    manifest: dict[str, Any],
    *,
    full: bool = True,
) -> dict[str, Any]:
    rebuilt: list[str] = []
    removed_stale: list[str] = []
    schema_version = int(manifest.get("schema_version", 0) or 0)
    if schema_version < 4:
        return {
            "schema_version": schema_version,
            "generation": manifest.get("generation"),
            "legacy_preserved": True,
            "rebuilt_files": [],
            "removed_stale_files": [],
        }
    plan_id = str(manifest.get("plan_id", ""))
    work_root = str(manifest.get("work_root", WORK_ROOT_DEFAULT))

    atomic_write_text(plan_dir / "TODO.md", render_todo(manifest))
    rebuilt.append("TODO.md")
    if full:
        atomic_write_text(plan_dir / "ANALYSIS.md", render_analysis(manifest))
        atomic_write_text(plan_dir / "PLAN.md", render_plan(manifest))
        atomic_write_text(plan_dir / "PLAN_REVIEW.md", render_plan_review(manifest))
        rebuilt.extend(["ANALYSIS.md", "PLAN.md", "PLAN_REVIEW.md"])
        if isinstance(manifest.get("execution_context"), dict):
            ctx_rebuilt, ctx_removed = _sync_context_projections(plan_dir, manifest["execution_context"])
            rebuilt.extend(ctx_rebuilt)
            removed_stale.extend(ctx_removed)

    tasks_dir = plan_dir / "tasks"
    tasks_dir.mkdir(exist_ok=True)
    expected_task_files: set[str] = set()
    if plan_id:
        for task in manifest.get("tasks", []):
            path_value = task.get("file")
            if isinstance(path_value, str) and path_value:
                expected_task_files.add(path_value)
                atomic_write_text(
                    plan_dir / path_value,
                    render_task(task, plan_id, work_root),
                )
                rebuilt.append(path_value)
    if full and tasks_dir.is_dir():
        for child in list(tasks_dir.iterdir()):
            if child.is_symlink() or not child.is_file():
                continue
            if child.name.endswith(".design.md"):
                continue
            rel = child.relative_to(plan_dir).as_posix()
            if rel not in expected_task_files and child.suffix == ".md":
                child.unlink()
                removed_stale.append(rel)

    if full:
        learnings_dir = plan_dir / LEARNING_DIRECTORY
        learnings_dir.mkdir(exist_ok=True)
        artifacts = manifest.get("learning_artifacts", [])
        expected_learnings = {
            str(item.get("file"))
            for item in artifacts
            if isinstance(item, dict) and isinstance(item.get("file"), str)
        }
        task_by_id = {str(t.get("id")): t for t in manifest.get("tasks", [])}
        for artifact in artifacts if isinstance(artifacts, list) else []:
            if not isinstance(artifact, dict):
                continue
            rel = artifact.get("file")
            if not isinstance(rel, str):
                continue
            target_path = plan_dir / rel
            if not target_path.is_file():
                source = task_by_id.get(str(artifact.get("source_task_id", "")))
                target = task_by_id.get(str(artifact.get("target_task_id", "")))
                if source and target:
                    declaration = declared_learning_target(source, str(target.get("id", "")))
                    if declaration and isinstance(artifact.get("items"), list):
                        content = render_learning_artifact(source, target, declaration, artifact["items"])
                        atomic_write_text(target_path, content)
                        rebuilt.append(rel)
        for child in list(learnings_dir.iterdir()):
            if child.is_symlink() or not child.is_file():
                continue
            rel = child.relative_to(plan_dir).as_posix()
            if rel not in expected_learnings:
                child.unlink()
                removed_stale.append(rel)

    _write_projection_state(plan_dir, manifest)
    return {
        "schema_version": schema_version,
        "generation": manifest.get("generation"),
        "legacy_preserved": False,
        "rebuilt_files": rebuilt,
        "removed_stale_files": removed_stale,
    }


def sync_projections(plan_dir: str | Path) -> dict[str, Any]:
    plan_path, manifest = load_plan(plan_dir)
    with plan_writer_lock(plan_path):
        plan_path, manifest = load_plan(plan_path)
        return _sync_projections_unlocked(plan_path, manifest, full=True)


def _task_statuses_on_disk(plan_dir: Path) -> dict[str, Any]:
    disk = read_json(plan_dir / MANIFEST)
    return {str(t.get("id")): t.get("status") for t in disk.get("tasks", []) if isinstance(t, dict)}


def recover_projections(plan_dir: str | Path) -> dict[str, Any]:
    """Recover projections strictly from authoritative manifest.json without mutating task status.

    A schema-v4 manifest written before generation counters existed is upgraded once here
    (generation 1, recorded as a ``generation_initialized`` event); this is the explicit
    migration that enables stale-writer checks and lag detection for such plans.
    """
    plan_path, manifest = load_plan(plan_dir)
    with plan_writer_lock(plan_path):
        plan_path, manifest = load_plan(plan_path)
        schema_version = int(manifest.get("schema_version", 0) or 0)
        if schema_version < 4:
            return {
                "schema_version": schema_version,
                "generation": manifest.get("generation"),
                "legacy_preserved": True,
                "projection_lag_detected": False,
                "removed_staging_dirs": [],
                "rebuilt_files": [],
                "removed_stale_files": [],
                "tasks_completed_changed": False,
                "generation_initialized": False,
            }
        before_statuses = _task_statuses_on_disk(plan_path)
        generation_initialized = False
        if not isinstance(manifest.get("generation"), int) or isinstance(manifest.get("generation"), bool):
            manifest["generation"] = 1
            append_event(manifest, "generation_initialized", generation=1)
            atomic_write_json(plan_path / MANIFEST, manifest)
            generation_initialized = True
        removed_staging: list[str] = []
        plan_id = str(manifest.get("plan_id", ""))
        create_staging = re.compile(rf"\.staging-{re.escape(plan_id)}-[0-9a-f]{{8}}") if plan_id else None
        if create_staging is not None and plan_path.parent.is_dir():
            # Leftovers of an interrupted create_plan live beside the plan directory.
            for child in list(plan_path.parent.iterdir()):
                if create_staging.fullmatch(child.name) and child.is_dir() and not child.is_symlink():
                    shutil.rmtree(child)
                    removed_staging.append(f"../{child.name}")
        staging_root = plan_path / STAGING_DIRECTORY
        if staging_root.is_dir() and not staging_root.is_symlink():
            for child in list(staging_root.iterdir()):
                rel = child.relative_to(plan_path).as_posix()
                if child.is_dir() and not child.is_symlink():
                    shutil.rmtree(child)
                    removed_staging.append(rel)
                elif child.is_file() and not child.is_symlink():
                    child.unlink()
                    removed_staging.append(rel)
            try:
                staging_root.rmdir()
            except OSError:
                pass

        proj_state_path = plan_path / PROJECTION_STATE_FILE
        lag_detected = False
        if isinstance(manifest.get("generation"), int):
            if not proj_state_path.is_file():
                lag_detected = True
            else:
                try:
                    proj_state = read_json(proj_state_path)
                    if proj_state.get("generation") != manifest.get("generation"):
                        lag_detected = True
                except PlanError:
                    lag_detected = True

        result = _sync_projections_unlocked(plan_path, manifest, full=True)
        return {
            **result,
            "projection_lag_detected": lag_detected,
            "removed_staging_dirs": removed_staging,
            "tasks_completed_changed": before_statuses != _task_statuses_on_disk(plan_path),
            "generation_initialized": generation_initialized,
        }


def save_manifest(
    plan_dir: Path,
    manifest: dict[str, Any],
    *,
    expected_generation: int | None = None,
    bump_generation: bool = True,
    _after_manifest_replace: Callable[[Path, dict[str, Any]], None] | None = None,
) -> None:
    with plan_writer_lock(plan_dir):
        manifest_path = plan_dir / MANIFEST
        schema_version = int(manifest.get("schema_version", 0) or 0)
        had_generation = "generation" in manifest
        previous_generation = manifest.get("generation")
        if manifest_path.is_file():
            disk_manifest = read_json(manifest_path)
            disk_gen = disk_manifest.get("generation")
            if isinstance(disk_gen, int) and not isinstance(disk_gen, bool):
                mem_gen = expected_generation if expected_generation is not None else manifest.get("generation")
                if mem_gen is None or isinstance(mem_gen, bool) or int(mem_gen) != disk_gen:
                    raise PlanError(
                        f"Stale plan writer: writer generation {mem_gen!r} cannot overwrite "
                        f"authoritative manifest generation {disk_gen}"
                    )
                if bump_generation and schema_version >= 4:
                    manifest["generation"] = disk_gen + 1
            elif expected_generation is not None:
                raise PlanError(
                    f"Stale plan writer: expected generation {expected_generation}, "
                    "but authoritative manifest has no generation counter"
                )
        elif schema_version >= 4 and "generation" not in manifest:
            manifest["generation"] = 1

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

        try:
            atomic_write_json(manifest_path, manifest)
        except BaseException:
            # The authority was not replaced: keep the caller's view at the disk generation.
            if had_generation:
                manifest["generation"] = previous_generation
            else:
                manifest.pop("generation", None)
            raise
        if _after_manifest_replace is not None:
            _after_manifest_replace(plan_dir, manifest)
        atomic_write_text(plan_dir / "TODO.md", render_todo(manifest))
        plan_id = str(manifest.get("plan_id", ""))
        work_root = str(manifest.get("work_root", WORK_ROOT_DEFAULT))
        # Schema-v4 task definitions are live projections of authoritative child
        # state. Preserve the historical schema-v1-v3 behavior exactly: those
        # task files remain immutable after plan creation.
        if schema_version >= 4 and plan_id:
            for task in manifest.get("tasks", []):
                path_value = task.get("file")
                if isinstance(path_value, str) and path_value:
                    atomic_write_text(
                        plan_dir / path_value,
                        render_task(task, plan_id, work_root),
                    )
            _write_projection_state(plan_dir, manifest)


def _normalize_spec_bundle(
    spec: dict[str, Any],
    repo_root: Path | None = None,
) -> dict[str, Any]:
    title = str(spec.get("title", "")).strip()
    summary = str(spec.get("summary", "")).strip()
    if not title or not summary:
        raise PlanError("Plan spec requires title and summary")

    plan_mode = spec.get("plan_mode")
    if plan_mode is not None:
        plan_mode = str(plan_mode).strip().lower()
        if plan_mode not in VALID_PLAN_MODES:
            raise PlanError(
                f"Invalid plan_mode {plan_mode!r}; expected one of {sorted(VALID_PLAN_MODES)}"
            )

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
    global_constraints = ensure_str_list(spec.get("global_constraints"), "global_constraints")

    for task in tasks:
        task["file"] = f"tasks/{task['id']}-{task['slug']}.md"
    task_file_by_id = {task["id"]: task["file"] for task in tasks}
    for task in tasks:
        task["related_task_files"] = [
            task_file_by_id[item] for item in task["related_task_reads"]
        ]
    assign_task_contract_digests(tasks)

    temp_manifest: dict[str, Any] = {
        "plan_mode": plan_mode,
        "requirements": requirements,
        "tasks": tasks,
    }
    research_errors = validate_research_and_plan_mode(repo_root, temp_manifest, tasks)
    if research_errors:
        raise PlanError("Plan contract validation failed:\n- " + "\n- ".join(research_errors))

    return {
        "title": title,
        "summary": summary,
        "plan_mode": plan_mode,
        "request_analysis": request_analysis,
        "requirements": requirements,
        "global_constraints": global_constraints,
        "execution_context": execution_context,
        "plan_review": plan_review,
        "autostart": autostart,
        "cleanup_on_success": bool(spec.get("cleanup_on_success", True)),
        "language": str(spec.get("language", "auto")).strip() or "auto",
        "tasks": tasks,
        "spec_sha256": canonical_json_sha256(spec),
    }


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

    bundle = _normalize_spec_bundle(spec, repo_root=repo_root)
    tasks = bundle["tasks"]
    execution_context = bundle["execution_context"]

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
        normalized_plan_id = f"{timestamp}-{slugify(bundle['title'])}"
    work_relative = Path(work_root)
    reject_symlink_components(repo_root, work_relative, "work_root")
    work_dir = repo_root / work_relative
    plan_dir = work_dir / normalized_plan_id
    if plan_dir.exists():
        raise PlanError(f"Plan directory already exists: {plan_dir}")
    work_dir.mkdir(parents=True, exist_ok=True)

    staging_dir = work_dir / f".staging-{normalized_plan_id}-{uuid.uuid4().hex[:8]}"
    created = now_utc()
    manifest: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "generation": 1,
        "revision": 0,
        "spec_sha256": bundle["spec_sha256"],
        "plan_id": normalized_plan_id,
        "title": bundle["title"],
        "summary": bundle["summary"],
        **({"plan_mode": bundle["plan_mode"]} if bundle["plan_mode"] is not None else {}),
        "request_analysis": bundle["request_analysis"],
        "requirements": bundle["requirements"],
        "global_constraints": bundle["global_constraints"],
        "execution_context": execution_context,
        "plan_review": bundle["plan_review"],
        "repo_root": str(repo_root),
        "work_root": Path(work_root).as_posix(),
        "state": "planned",
        "autostart": bundle["autostart"],
        "cleanup_on_success": bundle["cleanup_on_success"],
        "language": bundle["language"],
        "summary_status": "pending",
        "created_at": created,
        "updated_at": created,
        "tasks": tasks,
        "learning_artifacts": [],
        "revisions": [],
        "events": [{"at": created, "type": "plan_created", "generation": 1}],
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

    try:
        staging_dir.mkdir(parents=True)
        (staging_dir / "tasks").mkdir()
        (staging_dir / "results").mkdir()
        (staging_dir / "logs").mkdir()
        (staging_dir / LEARNING_DIRECTORY).mkdir()
        if request_source_path is not None:
            shutil.copy2(request_source_path, staging_dir / REQUEST_FILE)
        atomic_write_json(
            staging_dir / SENTINEL,
            {"schema_version": SCHEMA_VERSION, "plan_id": normalized_plan_id, "repo_root": str(repo_root)},
        )
        atomic_write_text(staging_dir / "ANALYSIS.md", render_analysis(manifest))
        atomic_write_text(staging_dir / "PLAN.md", render_plan(manifest))
        atomic_write_text(staging_dir / "PLAN_REVIEW.md", render_plan_review(manifest))
        write_context_artifacts(staging_dir, execution_context)
        for task in tasks:
            atomic_write_text(
                staging_dir / task["file"],
                render_task(task, normalized_plan_id, Path(work_root).as_posix()),
            )
        from routing_config import plan_overlay
        atomic_write_json(staging_dir / CONFIG, plan_overlay())
        # Plans stay valid without a snapshot, so a catalog failure is recorded, not fatal.
        try:
            matrix = model_catalogctl.create_plan_matrix(model_catalogctl.CatalogStore(), staging_dir, manifest)
            manifest["events"].append(
                {"at": created, "type": "model_matrix_created", "catalog_digest": matrix["catalog_digest"]}
            )
        except Exception as exc:  # noqa: BLE001
            manifest["events"].append(
                {"at": created, "type": "model_matrix_skipped", "error": f"{exc.__class__.__name__}: {str(exc)[:200]}"}
            )
        atomic_write_json(staging_dir / MANIFEST, manifest)
        atomic_write_text(staging_dir / "TODO.md", render_todo(manifest))
        _write_projection_state(staging_dir, manifest)
        errors = validate_plan(staging_dir, manifest)
        if errors:
            raise PlanError("Plan validation failed after creation:\n- " + "\n- ".join(errors))
        if plan_dir.exists():
            raise PlanError(f"Plan directory already exists: {plan_dir}")
        replace_with_retry(staging_dir, plan_dir)
    except BaseException:
        shutil.rmtree(staging_dir, ignore_errors=True)
        raise

    git_exclude = ensure_git_exclude(repo_root, work_root)
    if git_exclude:
        manifest["git_exclude"] = git_exclude
        save_manifest(plan_dir, manifest, bump_generation=False)
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
                save_manifest(plan_dir, manifest, bump_generation=False)
            except OSError as exc:
                manifest["request_source"]["move_error"] = str(exc)
                append_event(manifest, "request_source_move_failed", error=str(exc))
                save_manifest(plan_dir, manifest, bump_generation=False)
    return plan_dir


def _archive_task_receipt(
    old_task: dict[str, Any],
    manifest: dict[str, Any],
    *,
    superseded_by_generation: int | None,
    reason: str,
) -> dict[str, Any]:
    existing = old_task.get("current_receipt")
    if isinstance(existing, dict) and existing:
        archived = dict(existing)
    else:
        archived = {
            "schema_version": 1,
            "task_id": old_task.get("id"),
            "generation": manifest.get("generation"),
            "contract_digest": old_task.get("contract_digest"),
            "status": old_task.get("status"),
            "completed_at": old_task.get("completed_at"),
            "result_file": old_task.get("result_file"),
            "changed_files": list(old_task.get("changed_files", [])),
            "acceptance_criteria": list(old_task.get("acceptance_criteria", [])),
            "validation_commands": list(old_task.get("validation_commands", [])),
            "scoped_input_digests": dict(old_task.get("scoped_input_digests") or {}),
        }
    archived["historical"] = True
    archived["superseded_at"] = now_utc()
    archived["superseded_by_generation"] = superseded_by_generation
    archived["invalidation_reason"] = reason
    return archived


def revise_plan(
    plan_dir: str | Path,
    spec: dict[str, Any],
    *,
    amendment: str,
    expected_generation: int | None = None,
    task_id_mapping: dict[str, str] | None = None,
    scoped_input_digests: dict[str, dict[str, str]] | None = None,
    _before_authority_publish: Callable[[Path, dict[str, Any]], None] | None = None,
    _after_authority_publish: Callable[[Path, dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    """Revise a schema-v4 plan in a staged generation before publishing authority.

    ``expected_generation`` is required: it is the manifest generation the spec was written
    against (0 for a schema-v4 manifest that predates generation counters), so a writer
    holding an older view can never replace a newer generation.
    """
    plan_path, current = load_plan(plan_dir)
    with plan_writer_lock(plan_path):
        plan_path, current = load_plan(plan_path)
        schema_version = int(current.get("schema_version", 0) or 0)
        if schema_version < 4:
            raise PlanError(
                f"Cannot revise legacy schema-v{schema_version} plan using schema-v4 generation rules; "
                "migrate explicitly first"
            )
        disk_generation = current.get("generation")
        current_gen = disk_generation if isinstance(disk_generation, int) and not isinstance(disk_generation, bool) else 0
        if expected_generation is None or isinstance(expected_generation, bool):
            raise PlanError(
                "Plan revision requires expected_generation: the manifest generation the spec was written "
                f"against (authoritative manifest is at generation {current_gen})"
            )
        try:
            expected_gen = int(expected_generation)
        except (TypeError, ValueError) as exc:
            raise PlanError(f"expected_generation must be an integer, received {expected_generation!r}") from exc
        if expected_gen != current_gen:
            raise PlanError(
                f"Stale plan writer: expected generation {expected_generation}, "
                f"but authoritative manifest is at generation {current_gen}"
            )
        amendment_text = ensure_text(amendment, "amendment")
        if len(amendment_text) > MAX_AMENDMENT_CHARS:
            raise PlanError(f"amendment exceeds {MAX_AMENDMENT_CHARS} characters")

        repo_root = Path(current["repo_root"]).resolve()
        bundle = _normalize_spec_bundle(spec, repo_root=repo_root)
        new_tasks = bundle["tasks"]
        raw_spec_tasks = spec.get("tasks") if isinstance(spec.get("tasks"), list) else []
        digests_from_spec = {
            new_tasks[index]["id"]
            for index, raw in enumerate(raw_spec_tasks[: len(new_tasks)])
            if isinstance(raw, dict) and "scoped_input_digests" in raw
        }
        digests_from_flag: set[str] = set()
        if scoped_input_digests:
            for tid, digest_map in scoped_input_digests.items():
                nt = next((t for t in new_tasks if t["id"] == normalize_task_id(tid)), None)
                if nt is not None:
                    nt["scoped_input_digests"] = normalize_scoped_input_digests(
                        digest_map, f"Task {nt['id']} scoped_input_digests"
                    )
                    nt["scoped_input_digests_source"] = SCOPED_DIGESTS_FROM_FLAG
                    digests_from_flag.add(nt["id"])

        old_tasks = current.get("tasks", [])
        old_by_id = {str(t["id"]): t for t in old_tasks}
        old_digests = compute_task_contract_digests(old_tasks)
        new_by_id = {str(t["id"]): t for t in new_tasks}

        normalized_mapping: dict[str, str] = {}
        if task_id_mapping is not None:
            if not isinstance(task_id_mapping, dict):
                raise PlanError("task_id_mapping must be an object mapping old task IDs to new task IDs")
            for old_raw, new_raw in task_id_mapping.items():
                oid = normalize_task_id(old_raw)
                nid = normalize_task_id(new_raw)
                if oid not in old_by_id:
                    raise PlanError(f"task_id_mapping references unknown previous task {oid}")
                if nid not in new_by_id:
                    raise PlanError(f"task_id_mapping references unknown new task {nid}")
                normalized_mapping[oid] = nid
        for oid in old_by_id:
            if oid not in normalized_mapping and oid in new_by_id:
                normalized_mapping[oid] = oid
        reverse_mapping: dict[str, str] = {}
        for oid, nid in normalized_mapping.items():
            if nid in reverse_mapping:
                raise PlanError(f"task_id_mapping maps multiple previous tasks onto {nid}")
            reverse_mapping[nid] = oid

        # Digests bound by an earlier --scoped-input-digests flag are not in the spec; carry
        # them forward so an unrelated revision does not change (and reopen) this task.
        # Spec-bound digests are owned by the spec: omitting them there unbinds them.
        carried_scoped_digests: list[str] = []
        for nt in new_tasks:
            if nt["id"] in digests_from_spec or nt["id"] in digests_from_flag:
                continue
            previous_task = old_by_id.get(reverse_mapping.get(nt["id"], "")) or {}
            previous_digests = previous_task.get("scoped_input_digests") or {}
            if (
                previous_digests
                and previous_task.get("scoped_input_digests_source") == SCOPED_DIGESTS_FROM_FLAG
                and not nt.get("scoped_input_digests")
            ):
                nt["scoped_input_digests"] = dict(previous_digests)
                nt["scoped_input_digests_source"] = SCOPED_DIGESTS_FROM_FLAG
                carried_scoped_digests.append(nt["id"])
        if digests_from_flag or carried_scoped_digests:
            assign_task_contract_digests(new_tasks)

        next_gen = current_gen + 1
        next_revision = int(current.get("revision") or 0) + 1
        now = now_utc()

        changed_tasks: list[str] = []
        changed_details: dict[str, dict[str, Any]] = {}
        invalidated_tasks: list[str] = []
        preserved_completed_tasks: list[str] = []

        for nt in new_tasks:
            nid = nt["id"]
            oid = reverse_mapping.get(nid)
            old_task = old_by_id.get(oid) if oid is not None else None
            if old_task is None:
                changed_tasks.append(nid)
                changed_details[nid] = {"change": "added"}
                continue

            nt["receipt_history"] = [dict(item) for item in old_task.get("receipt_history", []) if isinstance(item, dict)]
            old_digest = str(old_task.get("contract_digest") or old_digests.get(old_task["id"], ""))
            new_digest = str(nt["contract_digest"])
            contract_changed = old_digest != new_digest

            # Also ensure transformed research tasks without valid execution evidence stay pending.
            is_transformed_research = (
                isinstance(nt.get("research_metadata"), dict)
                and nt["research_metadata"].get("former_kind") == "research"
            )

            if contract_changed:
                diff_flags: list[str] = []
                if old_task.get("acceptance_criteria") != nt.get("acceptance_criteria"):
                    diff_flags.append("acceptance_criteria")
                if old_task.get("validation_commands") != nt.get("validation_commands"):
                    diff_flags.append("validation_commands")
                if old_task.get("dependencies") != nt.get("dependencies"):
                    diff_flags.append("dependencies")
                if (old_task.get("scoped_input_digests") or {}) != (nt.get("scoped_input_digests") or {}):
                    diff_flags.append("scoped_inputs")
                if old_task.get("objective") != nt.get("objective"):
                    diff_flags.append("objective")
                if not diff_flags:
                    diff_flags.append("dependency_or_contract_digest")
                changed_tasks.append(nid)
                changed_details[nid] = {
                    "previous_task_id": old_task["id"],
                    "previous_contract_digest": old_digest,
                    "new_contract_digest": new_digest,
                    "changed_fields": diff_flags,
                }
                nt["history"] = list(old_task.get("history", []))
                nt["attempts"] = int(old_task.get("attempts", 0))
                if old_task.get("attempt_hypotheses"):
                    carried_hyps: list[dict[str, Any]] = []
                    for hyp in old_task.get("attempt_hypotheses", []):
                        if not isinstance(hyp, dict):
                            continue
                        copied_hyp = copy.deepcopy(hyp)
                        if copied_hyp.get("status") == "open":
                            copied_hyp["status"] = "invalidated"
                            copied_hyp["invalidated_reason"] = "source_contract_changed"
                            copied_hyp["updated_at"] = now
                        carried_hyps.append(copied_hyp)
                    if carried_hyps:
                        nt["attempt_hypotheses"] = carried_hyps
                if old_task.get("status") == "completed":
                    archived = _archive_task_receipt(
                        old_task,
                        current,
                        superseded_by_generation=next_gen,
                        reason=f"Contract changed ({', '.join(diff_flags)}) in revision {next_revision}",
                    )
                    nt["receipt_history"].append(archived)
                    nt["current_receipt"] = None
                    nt["status"] = "pending"
                    nt["history"].append(
                        {
                            "at": now,
                            "event": "invalidated_by_revision",
                            "revision": next_revision,
                            "generation": next_gen,
                            "changed_fields": diff_flags,
                            "previous_contract_digest": old_digest,
                            "new_contract_digest": new_digest,
                        }
                    )
                    invalidated_tasks.append(nid)
                else:
                    nt["status"] = "pending"
                    nt["current_receipt"] = None
                    nt["history"].append(
                        {
                            "at": now,
                            "event": "revised_pending",
                            "revision": next_revision,
                            "generation": next_gen,
                            "changed_fields": diff_flags,
                        }
                    )
            else:
                # Contract unchanged: preserve runtime progress and immutable completed evidence.
                old_sub_by_id = {
                    str(s.get("id")): s for s in old_task.get("subtasks", []) if isinstance(s, dict)
                }
                for sub in nt["subtasks"]:
                    prev_sub = old_sub_by_id.get(sub["id"])
                    if prev_sub:
                        sub["status"] = prev_sub.get("status", "pending")
                        sub["started_at"] = prev_sub.get("started_at")
                        sub["completed_at"] = prev_sub.get("completed_at")
                        sub["history"] = list(prev_sub.get("history", []))
                for field in (
                    "status",
                    "attempts",
                    "functional_failures",
                    "failure_classes",
                    "rate_limit_events",
                    "current_route",
                    "started_at",
                    "completed_at",
                    "last_error",
                    "history",
                    "changed_files",
                    "validation_results",
                    "result_file",
                    "completion_summary",
                    "completion_risks",
                    "completion_follow_ups",
                    "attempt_hypotheses",
                ):
                    if field in old_task:
                        value = old_task[field]
                        nt[field] = copy.deepcopy(value) if isinstance(value, (list, dict)) else value
                if nt.get("design_route") == old_task.get("design_route") and "design_phase" in old_task:
                    nt["design_phase"] = dict(old_task["design_phase"]) if isinstance(old_task["design_phase"], dict) else old_task["design_phase"]
                if nt["status"] == "completed":
                    if is_transformed_research and not old_task.get("current_receipt") and not old_task.get("result_file") and int(old_task.get("attempts", 0)) == 0:
                        nt["status"] = "pending"
                        nt["current_receipt"] = None
                    else:
                        preserved_receipt = (
                            dict(old_task["current_receipt"])
                            if isinstance(old_task.get("current_receipt"), dict)
                            else build_task_receipt(current, nt, None, nt.get("result_file"))
                        )
                        preserved_receipt["contract_digest"] = new_digest
                        nt["current_receipt"] = preserved_receipt
                        preserved_completed_tasks.append(nid)

        # Preserve learning artifacts only for non-invalidated completed sources with matching
        # source contract digests and valid targets; record invalidated learnings without deleting
        # unrelated preserved knowledge.
        preserved_learnings: list[dict[str, Any]] = []
        invalidated_learnings: list[dict[str, Any]] = []
        invalidated_set = set(invalidated_tasks)
        for artifact in current.get("learning_artifacts", []):
            if not isinstance(artifact, dict):
                continue
            orig_src_id = str(artifact.get("source_task_id", ""))
            orig_tgt_id = str(artifact.get("target_task_id", ""))
            src_id = normalized_mapping.get(orig_src_id)
            tgt_id = normalized_mapping.get(orig_tgt_id)
            drop_reason: str | None = None
            src_task = new_by_id.get(src_id) if src_id else None
            tgt_task = new_by_id.get(tgt_id) if tgt_id else None
            if not src_id or not tgt_id:
                drop_reason = "source_or_target_removed"
            elif src_id in invalidated_set:
                drop_reason = "source_contract_changed"
            elif not src_task or not tgt_task or src_task.get("status") != "completed":
                drop_reason = "source_not_completed"
            elif (
                artifact.get("source_contract_digest")
                and src_task.get("contract_digest")
                and artifact.get("source_contract_digest") != src_task.get("contract_digest")
            ):
                drop_reason = "source_contract_digest_mismatch"
            else:
                declaration = declared_learning_target(src_task, tgt_id)
                if declaration is None:
                    drop_reason = "learning_target_removed"
                elif (
                    artifact.get("reason") != declaration.get("reason")
                    or artifact.get("topics") != declaration.get("topics")
                ):
                    drop_reason = "learning_target_declaration_changed"
            if drop_reason is not None:
                invalidated_learnings.append(
                    {
                        "file": artifact.get("file"),
                        "producer_task_id": artifact.get("producer_task_id") or orig_src_id,
                        "consumer_task_ids": list(artifact.get("consumer_task_ids") or ([orig_tgt_id] if orig_tgt_id else [])),
                        "source_contract_digest": artifact.get("source_contract_digest"),
                        "reason": drop_reason,
                        "invalidated_at": now,
                        "revision": next_revision,
                    }
                )
                continue
            copied_art = copy.deepcopy(artifact)
            copied_art["source_task_id"] = src_id
            copied_art["target_task_id"] = tgt_id
            copied_art["producer_task_id"] = src_id
            copied_art["consumer_task_ids"] = [tgt_id]
            copied_art["file"] = learning_artifact_path(src_id, tgt_id)
            if copied_art.get("source_contract_digest") is None and src_task.get("contract_digest"):
                copied_art["source_contract_digest"] = src_task["contract_digest"]
            if copied_art.get("provenance_sha256") is not None and (src_id != orig_src_id or tgt_id != orig_tgt_id):
                copied_art["provenance_sha256"] = learning_provenance_sha256(copied_art)
            preserved_learnings.append(copied_art)
            src_task.setdefault("published_learning_files", []).append(copied_art["file"])
            tgt_task.setdefault("learning_files", []).append(copied_art["file"])

        previous_spec_sha256 = str(
            current.get("spec_sha256")
            or canonical_json_sha256(
                {
                    "title": current.get("title"),
                    "summary": current.get("summary"),
                    "requirements": current.get("requirements"),
                    "tasks": [task_contract_payload(t) for t in old_tasks],
                }
            )
        )
        revision_record: dict[str, Any] = {
            "revision": next_revision,
            "generation": next_gen,
            "previous_generation": current_gen,
            "previous_spec_sha256": previous_spec_sha256,
            "new_spec_sha256": bundle["spec_sha256"],
            "amendment": amendment_text,
            "task_id_mapping": normalized_mapping,
            "changed_tasks": changed_tasks,
            "changed_details": changed_details,
            "invalidated_tasks": invalidated_tasks,
            "invalidated_learnings": invalidated_learnings,
            "preserved_completed_tasks": preserved_completed_tasks,
            "carried_scoped_input_digests": carried_scoped_digests,
            "created_at": now,
        }

        prior_invalidated_learnings = [
            copy.deepcopy(item)
            for item in current.get("invalidated_learnings", [])
            if isinstance(item, dict)
        ]
        all_invalidated_learnings = [*prior_invalidated_learnings, *invalidated_learnings]

        staged_manifest: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "generation": next_gen,
            "revision": next_revision,
            "spec_sha256": bundle["spec_sha256"],
            "plan_id": current["plan_id"],
            "title": bundle["title"],
            "summary": bundle["summary"],
            **({"plan_mode": bundle["plan_mode"]} if bundle["plan_mode"] is not None else {}),
            "request_analysis": bundle["request_analysis"],
            "requirements": bundle["requirements"],
            "global_constraints": bundle["global_constraints"],
            "execution_context": bundle["execution_context"],
            "plan_review": bundle["plan_review"],
            "repo_root": current["repo_root"],
            "work_root": current["work_root"],
            "state": "planned",
            "autostart": bundle["autostart"],
            "cleanup_on_success": bundle["cleanup_on_success"],
            "language": bundle["language"],
            "summary_status": "pending",
            "created_at": current["created_at"],
            "updated_at": now,
            "tasks": new_tasks,
            "learning_artifacts": preserved_learnings,
            **({"invalidated_learnings": all_invalidated_learnings} if all_invalidated_learnings else {}),
            "revisions": [*list(current.get("revisions", [])), revision_record],
            "events": [
                *list(current.get("events", [])),
                {
                    "at": now,
                    "type": "plan_revised",
                    "revision": next_revision,
                    "generation": next_gen,
                    "previous_generation": current_gen,
                    "invalidated_tasks": invalidated_tasks,
                    "invalidated_learnings": [item.get("file") for item in invalidated_learnings],
                    "preserved_completed_tasks": preserved_completed_tasks,
                },
            ],
        }
        # Keep manifest state the spec does not own (request_source, git_exclude, an attached
        # study_gate, ...); spec-owned keys absent from the new spec are dropped on purpose.
        for key, value in current.items():
            if key not in staged_manifest and key not in SPEC_OWNED_MANIFEST_KEYS:
                staged_manifest[key] = copy.deepcopy(value)

        statuses = {t["status"] for t in new_tasks}
        if statuses == {"completed"}:
            staged_manifest["state"] = "completed"
        elif "in_progress" in statuses:
            staged_manifest["state"] = "running"
        elif "blocked" in statuses and not any(t["status"] == "pending" for t in new_tasks):
            staged_manifest["state"] = "blocked"
        elif any(t["attempts"] > 0 for t in new_tasks):
            staged_manifest["state"] = "running"
        else:
            staged_manifest["state"] = "planned"

        staging_dir = plan_path / STAGING_DIRECTORY / f"gen-{next_gen}-{uuid.uuid4().hex[:8]}"
        try:
            staging_dir.mkdir(parents=True)
            (staging_dir / "tasks").mkdir()
            (staging_dir / LEARNING_DIRECTORY).mkdir()
            for fname in (SENTINEL, CONFIG, REQUEST_FILE):
                src = plan_path / fname
                if src.is_file() and not src.is_symlink():
                    shutil.copy2(src, staging_dir / fname)
            for art in preserved_learnings:
                src_art = plan_path / art["file"]
                if src_art.is_file() and not src_art.is_symlink():
                    shutil.copy2(src_art, staging_dir / art["file"])
            atomic_write_json(staging_dir / MANIFEST, staged_manifest)
            _sync_projections_unlocked(staging_dir, staged_manifest, full=True)
            errors = validate_plan(staging_dir, staged_manifest)
            if errors:
                raise PlanError("Staged plan revision failed validation:\n- " + "\n- ".join(errors))
            if _before_authority_publish is not None:
                _before_authority_publish(plan_path, staged_manifest)
        except BaseException:
            shutil.rmtree(staging_dir, ignore_errors=True)
            try:
                (plan_path / STAGING_DIRECTORY).rmdir()
            except OSError:
                pass
            raise

        # Single authority publication: replace manifest.json only after staged audit passed.
        atomic_write_json(plan_path / MANIFEST, staged_manifest)
        if _after_authority_publish is not None:
            _after_authority_publish(plan_path, staged_manifest)

        # Render live projections strictly from the newly published authority.
        _sync_projections_unlocked(plan_path, staged_manifest, full=True)
        shutil.rmtree(staging_dir, ignore_errors=True)
        try:
            (plan_path / STAGING_DIRECTORY).rmdir()
        except OSError:
            pass
        return revision_record

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
        errors.extend(validate_attempt_hypotheses(manifest, tasks))
        generation = manifest.get("generation")
        if generation is not None:
            if type(generation) is not int or generation < 1:
                errors.append(f"Invalid manifest generation: {generation!r}")
            else:
                proj_path = plan_dir / PROJECTION_STATE_FILE
                if proj_path.is_file() and not proj_path.is_symlink():
                    try:
                        proj_state = read_json(proj_path)
                        if proj_state.get("generation") != generation:
                            errors.append(
                                f"Projections lag authoritative manifest generation {generation} "
                                f"(projection state is {proj_state.get('generation')!r}); run recover-projections"
                            )
                    except PlanError as exc:
                        errors.append(f"Invalid {PROJECTION_STATE_FILE}: {exc}")
                todo_path = plan_dir / "TODO.md"
                if not todo_path.is_file():
                    errors.append("Missing TODO.md projection")
                else:
                    try:
                        if todo_path.read_text(encoding="utf-8") != render_todo(manifest):
                            errors.append("TODO.md projection does not match authoritative manifest state")
                    except OSError as exc:
                        errors.append(f"Could not read TODO.md: {exc}")
        tasks_dir = plan_dir / "tasks"
        if tasks_dir.is_dir() and not tasks_dir.is_symlink():
            expected_task_files = {
                t.get("file") for t in tasks if isinstance(t.get("file"), str) and t.get("file")
            }
            for child in tasks_dir.iterdir():
                if child.is_symlink() or not child.is_file():
                    continue
                if child.suffix != ".md" or child.name.endswith(".design.md"):
                    continue
                rel = child.relative_to(plan_dir).as_posix()
                if rel not in expected_task_files:
                    errors.append(
                        f"Stale or mixed-generation task projection file: {rel}"
                    )
        repo_root_value = manifest.get("repo_root")
        repo_root_path = Path(repo_root_value) if isinstance(repo_root_value, str) and repo_root_value else None
        errors.extend(validate_research_and_plan_mode(repo_root_path, manifest, tasks))

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
        if not task.get("validation_commands") and not task.get("validation_jobs"):
            errors.append(f"Task {task_id}: missing validation commands")
        for key in ("validation_timeout_seconds", "validation_hard_timeout_seconds", "task_idle_timeout_seconds"):
            if key in task and (type(task[key]) is not int or not 0 <= task[key] <= 604800):
                errors.append(f"Task {task_id}: invalid {key}")
        jobs = task.get("validation_jobs", [])
        if not isinstance(jobs, list) or len(jobs) > 32 or any(not valid_validation_job_id(job) for job in jobs) or len(jobs) != len(set(jobs)):
            errors.append(f"Task {task_id}: invalid validation_jobs")
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
                    if subtask.get("id") != subtask_id:
                        errors.append(
                            f"Task {task_id}: inconsistent subtask id {subtask.get('id')!r} (expected canonical {subtask_id!r})"
                        )
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
    for task in manifest["tasks"]:
        context_prerequisites = set(learning_source_ids(manifest, task["id"]))
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


def detect_policy_override_note(text: str) -> str | None:
    """Return the matched policy-override category if a note tries to alter acceptance, permissions or provider policy."""
    if not isinstance(text, str) or not text.strip():
        return None
    for label, pattern in POLICY_OVERRIDE_PATTERNS:
        if pattern.search(text):
            return label
    return None


def extract_cited_repo_files(references: Iterable[str], repo_root: Path | None) -> dict[str, str]:
    """Hash repository-relative files cited in learning/hypothesis references when present on disk."""
    if repo_root is None or not repo_root.is_dir():
        return {}
    root = repo_root.resolve()
    digests: dict[str, str] = {}
    for raw in references:
        if not isinstance(raw, str):
            continue
        candidate = raw.strip().strip("`")
        if not candidate or any(ch.isspace() for ch in candidate) or candidate.startswith("-"):
            continue
        candidate = candidate.split("::", 1)[0]
        # Strip both line anchors (#L12) and symbol anchors (#Class.method).
        # Otherwise ordinary source references silently lose their change fingerprint.
        candidate = candidate.split("#", 1)[0]
        candidate = re.sub(r":\d+(?:-\d+)?$", "", candidate)
        candidate = candidate.replace("\\", "/")
        if not candidate or candidate.startswith("/") or candidate.startswith(".ai-work/"):
            continue
        rel_path = Path(candidate)
        if rel_path.is_absolute() or ".." in rel_path.parts or not rel_path.parts:
            continue
        try:
            reject_symlink_components(root, rel_path, "cited reference")
        except PlanError:
            continue
        target = root / rel_path
        if not target.is_file():
            continue
        try:
            if not target.resolve().is_relative_to(root):
                continue
            digests[rel_path.as_posix()] = file_sha256(target)
        except OSError:
            continue
    return digests


def explicit_learning_source_file(reference: Any, *, require_plain_file: bool = False) -> str | None:
    """Return an explicitly anchored source filename, not an arbitrary evidence ID/command.

    File#symbol and file::symbol are authoritative source citations. A missing
    file must never silently become an unhashed, apparently valid learning.
    Plain evidence IDs and shell commands are still allowed as non-file refs.
    """
    if not isinstance(reference, str):
        return None
    text = reference.strip().strip("`")
    if any(ch.isspace() for ch in text) or "://" in text:
        return None
    anchored = "::" in text or "#" in text or bool(re.search(r":\d+(?:-\d+)?$", text))
    candidate = text.split("::", 1)[0].split("#", 1)[0].replace("\\", "/")
    candidate = re.sub(r":\d+(?:-\d+)?$", "", candidate)
    if not candidate:
        return None
    # Canonicalise a single harmless leading ./ so evidence pins and source keys agree.
    if candidate.startswith("./"):
        candidate = candidate[2:]
    if not candidate:
        return None
    if candidate.startswith("/") or ".." in Path(candidate).parts:
        # Unsafe file-looking paths must remain recognizable as file claims.
        # The materializer rejects their missing digest, and freshness checks
        # mark legacy artifacts stale; returning None would silently bypass both.
        return candidate if (anchored or require_plain_file) else None
    if anchored:
        # Anchored code references can target suffixless files such as Makefile.
        return candidate if re.fullmatch(r"[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*", candidate) else None
    if not require_plain_file:
        return None
    # Plain code references cite sources too. Otherwise "src/missing.py" silently
    # publishes an unfingerprinted learning which never becomes stale.
    if not re.fullmatch(r"[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*", candidate):
        return None
    # Extension allowlists are unsafe for provenance: source languages and
    # configuration formats are open-ended (Avro, protobuf, custom DSLs, etc.).
    # Preserve bare evidence IDs without a dot or separator as non-file refs.
    source_name = Path(candidate).name
    known_suffixless_sources = {"Dockerfile", "Makefile", "Jenkinsfile", "Gemfile", "Rakefile", "Justfile"}
    return candidate if ("/" in candidate or Path(source_name).suffix
                         or source_name in known_suffixless_sources) else None



def learning_provenance_sha256(artifact: dict[str, Any]) -> str:
    payload = {
        "trust_class": artifact.get("trust_class", TRUST_CLASS_VALIDATED_LEARNING),
        "producer_task_id": artifact.get("producer_task_id") or artifact.get("source_task_id"),
        "consumer_task_ids": list(
            artifact.get("consumer_task_ids")
            or ([artifact.get("target_task_id")] if artifact.get("target_task_id") else [])
        ),
        "source_contract_digest": artifact.get("source_contract_digest"),
        "cited_file_digests": dict(sorted((artifact.get("cited_file_digests") or {}).items())),
        "invalidation_rule": artifact.get("invalidation_rule") or {},
        "items": artifact.get("items") or [],
    }
    return canonical_json_sha256(payload)


def check_learning_artifact_freshness(
    artifact: dict[str, Any],
    manifest: dict[str, Any],
    repo_root: Path | None = None,
    *,
    plan_dir: Path | None = None,
) -> dict[str, Any]:
    """Evaluate provenance and cited inputs; also verify the learning file when a plan directory is supplied."""
    stale_reasons: list[str] = []
    changed_files: list[str] = []
    # v4 promises verified, directional provenance. Legacy manifests retain
    # their historic validation contract but must not weaken the current one.
    strict_provenance = int(manifest.get("schema_version", 0) or 0) >= 4
    trust_class = artifact.get("trust_class")
    if strict_provenance and trust_class != TRUST_CLASS_VALIDATED_LEARNING:
        stale_reasons.append("missing_or_invalid_trust_class")
    elif trust_class is not None and trust_class not in VALID_LEARNING_TRUST_CLASSES:
        stale_reasons.append(f"invalid_trust_class:{trust_class}")

    producer_id = str(artifact.get("producer_task_id") or artifact.get("source_task_id") or "")
    target_id = str(artifact.get("target_task_id") or "")
    if strict_provenance and (
        not artifact.get("producer_task_id")
        or artifact.get("producer_task_id") != artifact.get("source_task_id")
    ):
        stale_reasons.append("producer_task_id_missing_or_mismatch")
    consumers = artifact.get("consumer_task_ids")
    if strict_provenance and consumers != [target_id]:
        stale_reasons.append("consumer_set_mismatch")
    elif consumers is not None and (not isinstance(consumers, list) or target_id not in consumers):
        stale_reasons.append("consumer_set_mismatch")

    tasks = manifest.get("tasks", []) if isinstance(manifest.get("tasks"), list) else []
    task_by_id = {str(t.get("id")): t for t in tasks if isinstance(t, dict)}
    producer = task_by_id.get(producer_id)
    recorded_contract = artifact.get("source_contract_digest")
    if strict_provenance and (
        not isinstance(recorded_contract, str) or not re.fullmatch(r"[0-9a-f]{64}", recorded_contract)
    ):
        stale_reasons.append("source_contract_digest_missing_or_invalid")
    if producer is None:
        stale_reasons.append(f"missing_producer:{producer_id}")
    elif recorded_contract:
        current_digests = compute_task_contract_digests(tasks) if tasks else {}
        current_contract = current_digests.get(producer_id) or producer.get("contract_digest")
        if strict_provenance and not current_contract:
            stale_reasons.append("source_contract_digest_unverifiable")
        elif current_contract and current_contract != recorded_contract:
            stale_reasons.append(f"source_contract_changed:{producer_id}")

    recorded_prov = artifact.get("provenance_sha256")
    if strict_provenance and (
        not isinstance(recorded_prov, str) or not re.fullmatch(r"[0-9a-f]{64}", recorded_prov)
    ):
        stale_reasons.append("provenance_hash_missing_or_invalid")
    elif recorded_prov is not None and recorded_prov != learning_provenance_sha256(artifact):
        stale_reasons.append("provenance_hash_mismatch")

    if strict_provenance:
        rule = artifact.get("invalidation_rule")
        if not isinstance(rule, dict) or any(
            rule.get(name) is not True
            for name in ("on_source_contract_change", "on_source_reset", "on_cited_file_change")
        ) or rule.get("scope") != "assigned_consumers_only":
            stale_reasons.append("invalidation_rule_missing_or_invalid")

    # The rendered Markdown is consumed by the next worker. Checking only its
    # manifest provenance lets a modified learning file bypass claim-time checks.
    if plan_dir is not None:
        expected_relative = learning_artifact_path(producer_id, target_id)
        if artifact.get("file") != expected_relative:
            stale_reasons.append("learning_file_path_mismatch")
        else:
            file_path = plan_dir / expected_relative
            try:
                reject_symlink_components(plan_dir, Path(expected_relative), "learning artifact")
                if file_path.is_symlink() or not file_path.is_file():
                    stale_reasons.append("learning_file_missing_or_symlink")
                else:
                    expected_sha = artifact.get("sha256")
                    if not isinstance(expected_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_sha):
                        stale_reasons.append("learning_file_sha256_missing")
                    elif file_sha256(file_path) != expected_sha:
                        stale_reasons.append("learning_file_changed")
            except (OSError, PlanError):
                stale_reasons.append("learning_file_unreadable_or_unsafe")

    resolved_root = repo_root
    if resolved_root is None and isinstance(manifest.get("repo_root"), str) and manifest.get("repo_root"):
        candidate_root = Path(manifest["repo_root"])
        if candidate_root.is_dir():
            resolved_root = candidate_root.resolve()
    cited_digests = artifact.get("cited_file_digests")
    if strict_provenance:
        if not isinstance(cited_digests, dict) or any(
            not isinstance(rel, str) or not isinstance(digest, str)
            or not re.fullmatch(r"[0-9a-f]{64}", digest)
            for rel, digest in cited_digests.items()
        ):
            stale_reasons.append("cited_file_digests_missing_or_invalid")
        else:
            for item in artifact.get("items") or []:
                if not isinstance(item, dict):
                    continue
                for ref in item.get("references") or []:
                    source = explicit_learning_source_file(
                        ref, require_plain_file=True
                    )
                    if source is not None and source not in cited_digests:
                        stale_reasons.append(f"cited_file_digest_missing:{source}")
    if isinstance(cited_digests, dict) and cited_digests and resolved_root is None:
        stale_reasons.append("cited_repo_root_unavailable")
    if isinstance(cited_digests, dict) and cited_digests and resolved_root is not None:
        for rel, expected_sha in sorted(cited_digests.items()):
            rel_path = Path(rel)
            if rel_path.is_absolute() or ".." in rel_path.parts:
                stale_reasons.append(f"cited_file_unsafe:{rel}")
                changed_files.append(rel)
                continue
            try:
                reject_symlink_components(resolved_root, rel_path, "cited reference")
            except PlanError:
                stale_reasons.append(f"cited_file_unsafe:{rel}")
                changed_files.append(rel)
                continue
            target = resolved_root / rel_path
            if target.is_symlink() or not target.is_file():
                stale_reasons.append(f"cited_file_missing:{rel}")
                changed_files.append(rel)
                continue
            try:
                actual_sha = file_sha256(target)
                if actual_sha != expected_sha and lf_sha256(target) != expected_sha:
                    stale_reasons.append(f"cited_file_changed:{rel}")
                    changed_files.append(rel)
            except OSError:
                stale_reasons.append(f"cited_file_unreadable:{rel}")
                changed_files.append(rel)

    return {
        "file": artifact.get("file"),
        "producer_task_id": producer_id,
        "consumer_task_ids": list(consumers) if isinstance(consumers, list) else ([target_id] if target_id else []),
        "trust_class": trust_class or TRUST_CLASS_VALIDATED_LEARNING,
        "source_contract_digest": recorded_contract,
        "fresh": len(stale_reasons) == 0,
        "stale_reasons": stale_reasons,
        "changed_files": changed_files,
    }


def invalidate_stale_learnings(
    plan_dir: Path,
    manifest: dict[str, Any],
    *,
    task_id: str | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Invalidate stale learnings without deleting unrelated valid learnings."""
    artifacts = manifest.get("learning_artifacts", [])
    if not isinstance(artifacts, list):
        raise PlanError("manifest.learning_artifacts must be a list")
    normalized_filter = normalize_task_id(task_id) if task_id is not None else None
    kept: list[dict[str, Any]] = []
    invalidated: list[dict[str, Any]] = []
    stale_files: set[str] = set()
    now = now_utc()

    for artifact in artifacts:
        if not isinstance(artifact, dict):
            continue
        target_id = str(artifact.get("target_task_id", ""))
        if normalized_filter is not None and target_id != normalized_filter:
            kept.append(artifact)
            continue
        status = check_learning_artifact_freshness(artifact, manifest, repo_root=repo_root, plan_dir=plan_dir)
        if status["fresh"]:
            kept.append(artifact)
            continue
        relative = str(artifact.get("file", ""))
        if relative:
            # Stale metadata is untrusted input at deletion time. Never unlink
            # an arbitrary file supplied by a corrupted/malicious manifest.
            expected = learning_artifact_path(status["producer_task_id"], target_id)
            if relative != expected:
                raise PlanError(f"Refusing to remove learning artifact with unexpected path: {relative}")
            checked = checked_relative_path(relative, "learning artifact file")
            reject_symlink_components(plan_dir, Path(checked), "learning artifact")
            path = plan_dir / checked
            if path.is_symlink():
                raise PlanError(f"Refusing to remove symlinked learning artifact: {relative}")
            stale_files.add(relative)
        record = {
            "file": relative,
            "producer_task_id": status["producer_task_id"],
            "consumer_task_ids": status["consumer_task_ids"],
            "source_contract_digest": status["source_contract_digest"],
            "stale_reasons": status["stale_reasons"],
            "changed_files": status["changed_files"],
            "invalidated_at": now,
        }
        invalidated.append(record)

    if invalidated:
        # Validate every removal target before deleting the first file.
        # A later malicious entry must not leave a partially erased plan.
        for relative in sorted(stale_files):
            checked = checked_relative_path(relative, "learning artifact file")
            reject_symlink_components(plan_dir, Path(checked), "learning artifact")
            path = plan_dir / checked
            if path.is_symlink():
                raise PlanError(f"Refusing to remove symlinked learning artifact: {relative}")
        for relative in sorted(stale_files):
            path = plan_dir / relative
            reject_symlink_components(plan_dir, Path(relative), "learning artifact")
            if path.is_symlink():
                raise PlanError(f"Refusing to remove symlinked learning artifact: {relative}")
            try:
                path.unlink()
            except FileNotFoundError:
                pass
        manifest["learning_artifacts"] = kept
        manifest.setdefault("invalidated_learnings", []).extend(invalidated)
        for task in manifest.get("tasks", []):
            task["learning_files"] = [
                rel for rel in task.get("learning_files", []) if rel not in stale_files
            ]
            task["published_learning_files"] = [
                rel for rel in task.get("published_learning_files", []) if rel not in stale_files
            ]
        append_event(
            manifest,
            "learnings_invalidated",
            files=sorted(stale_files),
            count=len(invalidated),
        )
        save_manifest(plan_dir, manifest)

    return {
        "invalidated_count": len(invalidated),
        "invalidated": invalidated,
        "preserved_files": [str(item.get("file")) for item in kept if isinstance(item, dict)],
    }


def normalize_learning_reference(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PlanError(f"{field} must be a non-empty string")
    text = value.strip()
    if "\n" in text or "\r" in text or len(text) > 240:
        raise PlanError(f"{field} must be one line and at most 240 characters")
    lowered = text.lower().replace("\\", "/")
    if "/.ai-work/" in f"/{lowered}" or lowered.startswith(".ai-work/"):
        raise PlanError(f"{field} may not reference planning artifacts")
    if "`" in text or "<" in text or ">" in text:
        raise PlanError(f"{field} must not contain Markdown/HTML delimiters")
    override_kind = detect_policy_override_note(text)
    if override_kind is not None:
        raise PlanError(f"{field} cannot alter acceptance, permissions, or provider policy ({override_kind})")
    return text


def comparable_hypothesis_text(value: Any) -> str:
    """Ignore punctuation/spacing disguises when barring disproven claims."""
    return " ".join(re.findall(r"\w+", str(value).casefold()))


HYPOTHESIS_SIMILARITY_STOPWORDS = frozenset({
    "a", "an", "and", "are", "as", "at", "be", "been", "before", "by", "did", "do",
    "does", "for", "from", "had", "has", "have", "in", "into", "is", "it", "its",
    "not", "of", "on", "or", "should", "that", "the", "their", "then", "this", "to",
    "was", "were", "what", "when", "which", "while", "with", "without", "would",
})


def repeats_disproven_hypothesis(disproven_text: str, guidance_text: str) -> bool:
    """Conservative deterministic overlap guard, not semantic entailment or fact checking.

    Matching lengthy content claims with reordered words prevents trivially
    rephrased disproven hypotheses from being laundered as validated learnings.
    It may flag same-topic claims; callers must confirm before publishing.
    """
    if not disproven_text:
        return False
    if disproven_text == guidance_text or disproven_text in guidance_text:
        return True
    source = set(disproven_text.split()) - HYPOTHESIS_SIMILARITY_STOPWORDS
    target = set(guidance_text.split()) - HYPOTHESIS_SIMILARITY_STOPWORDS
    if len(source) < 5 or len(target) < 5:
        return False
    shared = len(source & target)
    return shared >= 4 and shared / min(len(source), len(target)) >= 0.70 and shared / max(len(source), len(target)) >= 0.50


def normalize_reusable_learnings(
    task: dict[str, Any], report: dict[str, Any], *, authorized_promotion_id: str | None = None
) -> list[dict[str, Any]]:
    raw = report.get("reusable_learnings", [])
    if not isinstance(raw, list):
        raise PlanError("reusable_learnings must be a list")
    if len(raw) > MAX_REUSABLE_LEARNINGS:
        raise PlanError(
            f"reusable_learnings may contain at most {MAX_REUSABLE_LEARNINGS} items"
        )
    if raw:
        val_results = report.get("validation_results")
        if isinstance(val_results, list) and any(
            isinstance(item, dict) and item.get("passed") is False for item in val_results
        ):
            raise PlanError(
                f"Task {task['id']} cannot publish reusable learnings when deterministic validation failed"
            )
        if not isinstance(val_results, list) or not val_results or not all(
            isinstance(item, dict) and item.get("passed") is True
            and item.get("exit_code") == 0 and str(item.get("command", "")).strip()
            for item in val_results
        ):
            raise PlanError(
                f"Task {task['id']} cannot publish validated reusable learnings without passing deterministic validation results"
            )
    declared = {
        str(item.get("task_id"))
        for item in task.get("learning_targets", [])
        if isinstance(item, dict)
    }
    disproven_hypotheses = {
        str(h.get("id")): comparable_hypothesis_text(h.get("hypothesis", ""))
        for h in task.get("attempt_hypotheses", [])
        if isinstance(h, dict) and h.get("status") == "disproven"
    }
    invalidated_hypotheses = {
        str(h.get("id"))
        for h in task.get("attempt_hypotheses", [])
        if isinstance(h, dict) and h.get("status") == "invalidated"
    }
    result: list[dict[str, Any]] = []
    for index, item in enumerate(raw):
        field = f"reusable_learnings[{index}]"
        if not isinstance(item, dict):
            raise PlanError(f"{field} must be an object")
        trust_class = str(item.get("trust_class") or TRUST_CLASS_VALIDATED_LEARNING).strip().lower()
        if trust_class not in VALID_LEARNING_TRUST_CLASSES:
            raise PlanError(
                f"{field}.trust_class must be {TRUST_CLASS_VALIDATED_LEARNING!r}; received {trust_class!r}"
            )
        if item.get("disproven") is True or str(item.get("hypothesis_status", "")).strip().lower() in {"disproven", "unvalidated", "invalidated"}:
            raise PlanError(
                f"{field}: a disproven or unvalidated hypothesis cannot be published as a validated learning"
            )
        promoted_from = item.get("promoted_from_hypothesis")
        if promoted_from is not None:
            pid = normalize_hypothesis_id(promoted_from)
            if authorized_promotion_id != pid or str(promoted_from).strip().upper() != pid:
                raise PlanError(
                    f"{field}.promoted_from_hypothesis requires canonical ID and the verified promotion API"
                )
            matching = next(
                (h for h in task.get("attempt_hypotheses", [])
                 if isinstance(h, dict) and h.get("id") == pid), None
            )
            if matching is None or matching.get("status") != "open":
                raise PlanError(f"{field}: promotion requires an existing open hypothesis {pid}")
            if pid in disproven_hypotheses:
                raise PlanError(
                    f"{field}: disproven hypothesis {pid} cannot be published as a validated learning"
                )
            if pid in invalidated_hypotheses:
                raise PlanError(
                    f"{field}: invalidated hypothesis {pid} cannot be published as a validated learning"
                )
        kind = str(item.get("kind", "")).strip().lower()
        if kind not in VALID_LEARNING_KINDS:
            raise PlanError(f"{field}.kind must be one of {sorted(VALID_LEARNING_KINDS)}")
        guidance = ensure_text(item.get("guidance"), f"{field}.guidance")
        if len(guidance) < 35 or len(guidance) > MAX_LEARNING_GUIDANCE_CHARS:
            raise PlanError(
                f"{field}.guidance must be 35-{MAX_LEARNING_GUIDANCE_CHARS} characters"
            )
        # Materialized guidance is rendered into Markdown without an escaping
        # envelope. Never allow it to introduce trusted-looking headers, HTML,
        # code fences, or separate paragraphs inside a validated artifact.
        if any(marker in guidance for marker in ("\n", "\r", "`", "<", ">")) or re.match(
            r"^\s*(?:#{1,6}\s+|[-*+]\s+|>\s+)", guidance
        ):
            raise PlanError(f"{field}.guidance must be plain single-line text without Markdown/HTML delimiters")
        override_kind = detect_policy_override_note(guidance)
        if override_kind is not None:
            raise PlanError(
                f"{field}.guidance cannot alter acceptance, permissions, or provider policy ({override_kind})"
            )
        folded_guidance = comparable_hypothesis_text(guidance)
        for hyp_id, disproven_text in disproven_hypotheses.items():
            if repeats_disproven_hypothesis(disproven_text, folded_guidance):
                raise PlanError(
                    f"{field}.guidance repeats disproven hypothesis {hyp_id}; disproven hypotheses never appear as validated shared facts"
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
        entry: dict[str, Any] = {
            "kind": kind,
            "trust_class": TRUST_CLASS_VALIDATED_LEARNING,
            "guidance": guidance,
            "references": clean_references,
            "target_task_ids": target_ids,
        }
        if promoted_from is not None:
            entry["promoted_from_hypothesis"] = pid
        result.append(entry)
    return result


def learning_artifact_path(source_id: str, target_id: str) -> str:
    return f"{LEARNING_DIRECTORY}/{source_id}-to-{target_id}.md"


def render_learning_artifact(
    source_task: dict[str, Any],
    target_task: dict[str, Any],
    declaration: dict[str, Any],
    learnings: list[dict[str, Any]],
) -> str:
    contract_digest = str(source_task.get("contract_digest") or "unpinned")[:12]
    lines = [
        f"# Validated learning — {source_task['id']} → {target_task['id']}",
        "",
        "This artifact contains only concise findings from a completed TODO that passed deterministic validation. It is not a worker transcript and must not be expanded with general history.",
        "",
        "## Applicability declared during planning",
        "",
        f"- Trust class: `{TRUST_CLASS_VALIDATED_LEARNING}`",
        f"- Source TODO: **{source_task['id']} — {source_task['title']}**",
        f"- Target TODO: **{target_task['id']} — {target_task['title']}**",
        f"- Source contract digest: `{contract_digest}`",
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
                *([f"Promoted from verified task-local hypothesis: `{learning['promoted_from_hypothesis']}`", ""]
                  if learning.get("promoted_from_hypothesis") else []),
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
    *,
    source_contract_digest: str | None = None,
    authorized_promotion_id: str | None = None,
) -> list[str]:
    learnings = normalize_reusable_learnings(task, report, authorized_promotion_id=authorized_promotion_id)
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
    resolved_contract_digest = (
        source_contract_digest
        or task.get("contract_digest")
        or compute_task_contract_digests(manifest.get("tasks", [])).get(task["id"])
    )
    render_source = {**task, "contract_digest": resolved_contract_digest} if resolved_contract_digest else task
    repo_root_value = manifest.get("repo_root")
    repo_root_path = Path(repo_root_value) if isinstance(repo_root_value, str) and repo_root_value else None

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
                **({"promoted_from_hypothesis": learning["promoted_from_hypothesis"]}
                   if learning.get("promoted_from_hypothesis") else {}),
            }
            for learning in target_learnings
        ]
        all_refs = [ref for item in artifact_items for ref in item["references"]]
        cited_file_digests = extract_cited_repo_files(all_refs, repo_root_path)
        # An explicit file#symbol or file::symbol citation is a claimed code
        # anchor, not an optional hint. Missing/unsafe sources fail closed.
        for learning in target_learnings:
            for reference in learning["references"]:
                source = explicit_learning_source_file(
                    reference, require_plain_file=True
                )
                if source is not None and source not in cited_file_digests:
                    raise PlanError(f"Learning source reference missing or unsafe: {reference}")
        invalidation_rule = {
            "on_source_contract_change": True,
            "on_source_reset": True,
            "on_cited_file_change": True,
            "scope": "assigned_consumers_only",
        }
        content = render_learning_artifact(
            render_source,
            target_task,
            declaration,
            artifact_items,
        )
        artifact_record: dict[str, Any] = {
            "trust_class": TRUST_CLASS_VALIDATED_LEARNING,
            "producer_task_id": task["id"],
            "consumer_task_ids": [target_id],
            "source_task_id": task["id"],
            "target_task_id": target_id,
            "source_contract_digest": resolved_contract_digest,
            "cited_file_digests": cited_file_digests,
            "invalidation_rule": invalidation_rule,
            "file": relative,
            "reason": declaration["reason"],
            "topics": list(declaration["topics"]),
            "items": artifact_items,
            "item_count": len(artifact_items),
            "created_at": now_utc(),
        }
        artifact_record["provenance_sha256"] = learning_provenance_sha256(artifact_record)
        prepared.append(
            {
                "target_task": target_task,
                "relative": relative,
                "content": content,
                "artifact": artifact_record,
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

    # A canonical learning path can still escape when `learnings/` is a
    # symlink. Preflight every destination before writing any artifact.
    for item in prepared:
        relative = checked_relative_path(item["relative"], "learning artifact file")
        expected = learning_artifact_path(task["id"], item["artifact"]["target_task_id"])
        if relative != expected:
            raise PlanError(f"Refusing to write learning artifact with unexpected path: {relative}")
        reject_symlink_components(plan_dir, Path(relative), "learning artifact")

    written: list[Path] = []
    try:
        for item in prepared:
            path = plan_dir / item["relative"]
            reject_symlink_components(plan_dir, Path(item["relative"]), "learning artifact")
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
        trust_class = artifact.get("trust_class")
        if trust_class is not None and trust_class not in VALID_LEARNING_TRUST_CLASSES:
            errors.append(f"{field}.trust_class must be {TRUST_CLASS_VALIDATED_LEARNING!r}")
        if artifact.get("producer_task_id") is not None and str(artifact.get("producer_task_id")) != source_id:
            errors.append(f"{field}.producer_task_id does not match source_task_id")
        consumers = artifact.get("consumer_task_ids")
        if consumers is not None and (not isinstance(consumers, list) or consumers != [target_id]):
            errors.append(f"{field}.consumer_task_ids does not match assigned consumer {target_id!r}")
        if int(manifest.get("schema_version", 0) or 0) >= 4:
            for required_field in (
                "trust_class", "producer_task_id", "consumer_task_ids", "source_contract_digest",
                "cited_file_digests", "invalidation_rule", "provenance_sha256",
            ):
                if required_field not in artifact or artifact[required_field] is None:
                    errors.append(f"{field}.{required_field} is required for provenance")
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
            elif detect_policy_override_note(guidance) is not None:
                errors.append(f"{item_field}.guidance cannot alter acceptance, permissions, or provider policy")
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
                    **({"promoted_from_hypothesis": item["promoted_from_hypothesis"]}
                       if item.get("promoted_from_hypothesis") else {}),
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
        if artifact.get("provenance_sha256") is not None and artifact.get("provenance_sha256") != learning_provenance_sha256(artifact):
            errors.append(f"Learning artifact {relative} provenance hash mismatch")
        if (
            target.get("status") == "pending"
            and int(target.get("attempts", 0)) == 0
            and target.get("started_at") is None
        ):
            freshness = check_learning_artifact_freshness(artifact, manifest, plan_dir=plan_dir)
            if not freshness["fresh"]:
                errors.append(
                    f"Learning artifact {relative} is stale before reuse: {', '.join(freshness['stale_reasons'])}"
                )
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


def normalize_hypothesis_id(value: Any, index: int | None = None) -> str:
    if value is None or not str(value).strip():
        if index is None:
            raise PlanError("Hypothesis id is required")
        return f"H{index + 1:03d}"
    text = str(value).strip().upper()
    if text.isdigit():
        return f"H{int(text):03d}"
    if re.fullmatch(r"H\d+", text):
        return f"H{int(text[1:]):03d}"
    if not re.fullmatch(r"[A-Z][A-Z0-9_-]{0,23}", text):
        raise PlanError(f"Invalid hypothesis id: {value!r}")
    return text


def normalize_attempt_hypothesis(
    raw: Any,
    task: dict[str, Any],
    *,
    index: int = 0,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    field = f"Task {task.get('id', '?')} attempt_hypotheses[{index}]"
    if not isinstance(raw, dict):
        raise PlanError(f"{field} must be an object")
    hyp_id = normalize_hypothesis_id(raw.get("id"), index)
    trust_class = str(raw.get("trust_class") or TRUST_CLASS_HYPOTHESIS).strip().lower()
    if trust_class != TRUST_CLASS_HYPOTHESIS:
        raise PlanError(
            f"{field}.trust_class must be {TRUST_CLASS_HYPOTHESIS!r}; failed-attempt hypotheses stay separate from normative shared facts"
        )
    status = str(raw.get("status") or "open").strip().lower()
    if status not in VALID_HYPOTHESIS_STATUSES:
        raise PlanError(f"{field}.status must be one of {sorted(VALID_HYPOTHESIS_STATUSES)}")
    text = ensure_context_line(
        raw.get("hypothesis"),
        f"{field}.hypothesis",
        minimum=15,
        maximum=MAX_HYPOTHESIS_CHARS,
    )
    override_kind = detect_policy_override_note(text)
    if override_kind is not None:
        raise PlanError(
            f"{field}.hypothesis cannot alter acceptance, permissions, or provider policy ({override_kind})"
        )
    refs_raw = ensure_list(raw.get("evidence_refs"), f"{field}.evidence_refs")
    if not refs_raw or len(refs_raw) > MAX_HYPOTHESIS_REFS:
        raise PlanError(f"{field}.evidence_refs must contain 1-{MAX_HYPOTHESIS_REFS} entries")
    evidence_refs = [
        normalize_learning_reference(ref, f"{field}.evidence_refs[{idx}]")
        for idx, ref in enumerate(refs_raw)
    ]
    evidence_digests = (
        dict(raw["evidence_digests"])
        if isinstance(raw.get("evidence_digests"), dict)
        else extract_cited_repo_files(evidence_refs, repo_root)
    )
    disproven_reason = raw.get("disproven_reason")
    if status == "disproven":
        disproven_reason = ensure_context_line(
            disproven_reason,
            f"{field}.disproven_reason",
            minimum=10,
            maximum=MAX_HYPOTHESIS_REASON_CHARS,
        )
    elif disproven_reason is not None:
        disproven_reason = ensure_context_line(
            disproven_reason,
            f"{field}.disproven_reason",
            minimum=1,
            maximum=MAX_HYPOTHESIS_REASON_CHARS,
        )
    invalidated_reason = raw.get("invalidated_reason")
    if invalidated_reason is not None:
        invalidated_reason = ensure_context_line(
            invalidated_reason,
            f"{field}.invalidated_reason",
            minimum=1,
            maximum=MAX_HYPOTHESIS_REASON_CHARS,
        )
    now = now_utc()
    return {
        "id": hyp_id,
        "trust_class": TRUST_CLASS_HYPOTHESIS,
        "status": status,
        "attempt": int(raw.get("attempt", task.get("attempts", 0)) or 0),
        "producer_task_id": str(task.get("id", "")),
        "hypothesis": text,
        "evidence_refs": evidence_refs,
        "evidence_digests": evidence_digests,
        "failure_signature": raw.get("failure_signature")
        if raw.get("failure_signature") is not None
        else (
            (task.get("validation_stagnation") or {}).get("signature")
            if isinstance(task.get("validation_stagnation"), dict)
            else None
        ),
        "source_contract_digest": str(raw.get("source_contract_digest") or task.get("contract_digest") or ""),
        "disproven_reason": disproven_reason,
        "invalidated_reason": invalidated_reason,
        "created_at": str(raw.get("created_at") or now),
        "updated_at": str(raw.get("updated_at") or now),
    }


def check_hypothesis_freshness(
    hypothesis: dict[str, Any],
    task: dict[str, Any],
    repo_root: Path | None = None,
) -> list[str]:
    """Return invalidation reasons when a failed-attempt hypothesis's evidence changed."""
    reasons: list[str] = []
    recorded_contract = str(hypothesis.get("source_contract_digest") or "")
    current_contract = str(task.get("contract_digest") or "")
    if recorded_contract and current_contract and recorded_contract != current_contract:
        reasons.append("source_contract_changed")
    recorded_sig = hypothesis.get("failure_signature")
    stagnation = task.get("validation_stagnation")
    current_sig = stagnation.get("signature") if isinstance(stagnation, dict) else None
    if recorded_sig and current_sig and recorded_sig != current_sig:
        reasons.append("failure_signature_changed")
    evidence_digests = hypothesis.get("evidence_digests")
    # File#symbol and file::symbol are explicit file claims.  A missing
    # fingerprint is stale even if extraction returned no existing files.
    for reference in hypothesis.get("evidence_refs") or []:
        source = explicit_learning_source_file(reference, require_plain_file=True)
        if source is not None and (
            not isinstance(evidence_digests, dict) or source not in evidence_digests
        ):
            reasons.append(f"evidence_digest_missing:{source}")
    if isinstance(evidence_digests, dict) and evidence_digests:
        if repo_root is None or not repo_root.is_dir():
            reasons.append("evidence_repo_root_unavailable")
        else:
            root = repo_root.resolve()
            for rel, expected_sha in sorted(evidence_digests.items()):
                rel_path = Path(rel)
                if rel_path.is_absolute() or ".." in rel_path.parts:
                    reasons.append(f"evidence_unsafe:{rel}")
                    continue
                try:
                    reject_symlink_components(root, rel_path, "hypothesis evidence")
                except PlanError:
                    reasons.append(f"evidence_unsafe:{rel}")
                    continue
                target = root / rel_path
                if target.is_symlink() or not target.is_file():
                    reasons.append(f"evidence_missing:{rel}")
                    continue
                try:
                    actual_sha = file_sha256(target)
                    if actual_sha != expected_sha and lf_sha256(target) != expected_sha:
                        reasons.append(f"evidence_changed:{rel}")
                except OSError:
                    reasons.append(f"evidence_unreadable:{rel}")
    return reasons


def invalidate_stale_hypotheses(
    plan_dir: Path | None,
    manifest: dict[str, Any],
    task_id: str,
    *,
    repo_root: Path | None = None,
    save: bool = True,
) -> list[str]:
    """Invalidate open failed-attempt hypotheses whose underlying evidence or contract changed."""
    task = find_task(manifest, task_id)
    resolved_root = repo_root
    if resolved_root is None and isinstance(manifest.get("repo_root"), str) and manifest.get("repo_root"):
        candidate = Path(manifest["repo_root"])
        if candidate.is_dir():
            resolved_root = candidate.resolve()
    invalidated_ids: list[str] = []
    now = now_utc()
    for hyp in task.get("attempt_hypotheses", []):
        if not isinstance(hyp, dict) or hyp.get("status") != "open":
            continue
        reasons = check_hypothesis_freshness(hyp, task, repo_root=resolved_root)
        if reasons:
            hyp["status"] = "invalidated"
            hyp["invalidated_reason"] = "; ".join(reasons)[:MAX_HYPOTHESIS_REASON_CHARS]
            hyp["updated_at"] = now
            invalidated_ids.append(str(hyp.get("id", "?")))
    if invalidated_ids and save and plan_dir is not None:
        append_event(
            manifest,
            "hypotheses_invalidated",
            task_id=task["id"],
            hypothesis_ids=invalidated_ids,
        )
        save_manifest(plan_dir, manifest)
    return invalidated_ids


def record_attempt_hypothesis(
    plan_dir: Path,
    manifest: dict[str, Any],
    task_id: str,
    hypothesis: str,
    evidence_refs: list[str],
    *,
    status: str = "open",
    disproven_reason: str | None = None,
    failure_signature: str | None = None,
    save: bool = True,
) -> dict[str, Any]:
    """Record a bounded, task-local failed-attempt hypothesis separate from shared normative facts."""
    task = find_task(manifest, task_id)
    repo_root_value = manifest.get("repo_root")
    repo_root = Path(repo_root_value) if isinstance(repo_root_value, str) and repo_root_value else None
    existing = task.setdefault("attempt_hypotheses", [])
    used_nums = [
        int(m.group(1))
        for item in existing
        if isinstance(item, dict) and (m := re.fullmatch(r"H(\d+)", str(item.get("id", ""))))
    ]
    next_id = f"H{(max(used_nums, default=0) + 1):03d}"
    entry = normalize_attempt_hypothesis(
        {
            "id": next_id,
            "trust_class": TRUST_CLASS_HYPOTHESIS,
            "status": status,
            "hypothesis": hypothesis,
            "evidence_refs": evidence_refs,
            "disproven_reason": disproven_reason,
            "failure_signature": failure_signature,
        },
        task,
        index=len(existing),
        repo_root=repo_root,
    )
    existing.append(entry)
    if len(existing) > MAX_ATTEMPT_HYPOTHESES:
        # Keep disproven hypotheses when possible so they stay explicitly blocked from promotion;
        # evict oldest invalidated/open entries first.
        while len(existing) > MAX_ATTEMPT_HYPOTHESES:
            evict_idx = next(
                (idx for idx, item in enumerate(existing) if item.get("status") != "disproven"),
                0,
            )
            existing.pop(evict_idx)
    append_event(
        manifest,
        "attempt_hypothesis_recorded",
        task_id=task["id"],
        hypothesis_id=entry["id"],
        status=entry["status"],
    )
    if save:
        save_manifest(plan_dir, manifest)
    return entry


def mark_hypothesis_disproven(
    plan_dir: Path,
    manifest: dict[str, Any],
    task_id: str,
    hypothesis_id: str,
    reason: str,
) -> dict[str, Any]:
    task = find_task(manifest, task_id)
    normalized_id = normalize_hypothesis_id(hypothesis_id)
    clean_reason = ensure_context_line(
        reason,
        f"Task {task['id']} hypothesis {normalized_id} disproven_reason",
        minimum=10,
        maximum=MAX_HYPOTHESIS_REASON_CHARS,
    )
    for hyp in task.get("attempt_hypotheses", []):
        if isinstance(hyp, dict) and hyp.get("id") == normalized_id:
            if hyp.get("status") == "promoted":
                raise PlanError(f"Hypothesis {normalized_id} was already promoted")
            hyp["status"] = "disproven"
            hyp["disproven_reason"] = clean_reason
            hyp["updated_at"] = now_utc()
            append_event(
                manifest,
                "attempt_hypothesis_disproven",
                task_id=task["id"],
                hypothesis_id=normalized_id,
            )
            save_manifest(plan_dir, manifest)
            return hyp
    raise PlanError(f"Task {task['id']} has no hypothesis {normalized_id}")


def promote_hypothesis_to_learning(
    plan_dir: Path,
    manifest: dict[str, Any],
    task_id: str,
    hypothesis_id: str,
    *,
    kind: str,
    target_task_ids: list[str],
    deterministic_evidence: list[dict[str, Any]],
    guidance: str | None = None,
) -> dict[str, Any]:
    """Promote an open failed-attempt hypothesis to a reusable learning only after deterministic proof."""
    task = find_task(manifest, task_id)
    normalized_id = normalize_hypothesis_id(hypothesis_id)
    invalidate_stale_hypotheses(plan_dir, manifest, task["id"], save=False)
    target_hyp = next(
        (
            item
            for item in task.get("attempt_hypotheses", [])
            if isinstance(item, dict) and item.get("id") == normalized_id
        ),
        None,
    )
    if target_hyp is None:
        raise PlanError(f"Task {task['id']} has no hypothesis {normalized_id}")
    if target_hyp.get("status") == "disproven":
        raise PlanError(
            f"Disproven hypothesis {normalized_id} cannot be promoted into a validated shared fact"
        )
    if target_hyp.get("status") == "invalidated":
        raise PlanError(
            f"Invalidated hypothesis {normalized_id} cannot be promoted; underlying evidence changed "
            f"({target_hyp.get('invalidated_reason') or 'stale'})"
        )
    if target_hyp.get("status") != "open":
        raise PlanError(f"Hypothesis {normalized_id} is not open and cannot be promoted again")
    if not isinstance(deterministic_evidence, list) or not deterministic_evidence:
        raise PlanError(
            "Promoting a failed-attempt hypothesis into a reusable fact requires passing deterministic validation evidence"
        )
    # A caller-provided list is not execution evidence.  Bind promotion to the
    # runner-owned receipt of a completed task before trusting the passed flags.
    receipt = task.get("current_receipt")
    if task.get("status") != "completed" or not isinstance(receipt, dict):
        raise PlanError("Cannot promote hypothesis without a completed task and authoritative validation receipt")
    verdict = validate_receipt(receipt, task, manifest=manifest)
    if not verdict["valid"]:
        raise PlanError("Cannot promote hypothesis with an invalid task validation receipt")
    authoritative = task.get("validation_results")
    if not isinstance(authoritative, list) or not authoritative:
        raise PlanError("Cannot promote hypothesis without runner validation results")
    receipt_checks = receipt.get("validations")
    if not isinstance(receipt_checks, list) or not receipt_checks:
        raise PlanError("Cannot promote hypothesis without validation checks recorded in receipt")
    for check in deterministic_evidence:
        if not isinstance(check, dict) or not any(
            isinstance(saved, dict)
            and saved.get("command") == check.get("command")
            and saved.get("passed") is True
            and saved.get("exit_code") == 0
            for saved in authoritative
        ):
            raise PlanError("Promotion evidence was not observed by the completed task runner")
        if not any(
            isinstance(saved, dict)
            and saved.get("command") == check.get("command")
            and saved.get("passed") is True
            and saved.get("exit_code") == 0
            for saved in receipt_checks
        ):
            raise PlanError("Promotion evidence is absent from the authoritative task receipt")
    has_passing_check = False
    for check in deterministic_evidence:
        if not isinstance(check, dict):
            raise PlanError("Every deterministic_evidence entry must be an object")
        if check.get("passed") is not True or int(check.get("exit_code", 1)) != 0:
            raise PlanError(
                "Cannot promote hypothesis with failing or incomplete deterministic validation evidence"
            )
        if not str(check.get("command", "")).strip():
            raise PlanError("Deterministic validation evidence must record the executed command")
        has_passing_check = True
    if not has_passing_check:
        raise PlanError("Promoting a hypothesis requires at least one passing deterministic check")

    # Do not accept a CLI `complete --report` with caller-authored `passed: true`
    # as runner proof. Only the concise runner writes a deterministic
    # log-bound sidecar for this exact attempt after executing commands.
    attempt = int(task.get("attempts", 0))
    log_name = f"{task['id']}-attempt-{attempt}-validation.log"
    log_path = plan_dir / "logs" / log_name
    proof_path = Path(str(log_path) + ".runner-evidence.json")
    relative_log = checked_relative_path(log_path.relative_to(plan_dir).as_posix(), "validation log")
    relative_proof = checked_relative_path(proof_path.relative_to(plan_dir).as_posix(), "runner proof")
    for rel in (relative_log, relative_proof):
        reject_symlink_components(plan_dir, Path(rel), "runner validation evidence")
    if not log_path.is_file() or not proof_path.is_file():
        raise PlanError("Cannot promote without genuine runner validation log and proof")
    proof = read_json(proof_path)
    if (not isinstance(proof, dict) or proof.get("schema_version") != 2
        or proof.get("passed") is not True
        or proof.get("task_id") != task["id"]
        or proof.get("attempt") != attempt
        or proof.get("contract_digest") != receipt.get("contract_digest")
        or proof.get("log_sha256") != file_sha256(log_path)
        or receipt.get("runner_proof_sha256") != file_sha256(proof_path)
        or not isinstance(proof.get("checks"), list)):
        raise PlanError("Cannot promote with forged, stale or mismatched runner validation proof")
    for check in deterministic_evidence:
        if not any(
            item.get("command") == check.get("command")
            and item.get("passed") is True
            and item.get("exit_code") == 0
            for item in proof["checks"] if isinstance(item, dict)
        ):
            raise PlanError("Promotion evidence was not executed in the runner validation log")

    promoted_guidance = guidance if guidance is not None else str(target_hyp["hypothesis"])
    candidate_report = {
        "validation_results": deterministic_evidence,
        "reusable_learnings": [
            {
                "kind": kind,
                "trust_class": TRUST_CLASS_VALIDATED_LEARNING,
                "guidance": promoted_guidance,
                "references": list(target_hyp["evidence_refs"]),
                "target_task_ids": list(target_task_ids),
                "promoted_from_hypothesis": normalized_id,
            }
        ],
    }
    normalized_items = normalize_reusable_learnings(
        task, candidate_report, authorized_promotion_id=normalized_id
    )
    # Materialize directional, digest-pinned artifacts BEFORE declaring
    # the hypothesis promoted. An already published learning cannot be
    # replaced silently after task completion.
    published = materialize_learning_artifacts(
        plan_dir, manifest, task, candidate_report, authorized_promotion_id=normalized_id
    )
    if len(published) != len(normalized_items[0]["target_task_ids"]):
        raise PlanError("Hypothesis promotion did not publish every assigned learning")
    target_hyp["status"] = "promoted"
    target_hyp["updated_at"] = now_utc()
    append_event(
        manifest,
        "attempt_hypothesis_promoted",
        task_id=task["id"],
        hypothesis_id=normalized_id,
        target_task_ids=normalized_items[0]["target_task_ids"],
    )
    save_manifest(plan_dir, manifest)
    return normalized_items[0]


def validate_attempt_hypotheses(
    manifest: dict[str, Any],
    tasks: list[dict[str, Any]],
) -> list[str]:
    errors: list[str] = []
    disproven_texts: list[tuple[str, str, str]] = []
    for task in tasks:
        task_id = str(task.get("id", "?"))
        raw_hyps = task.get("attempt_hypotheses", [])
        if raw_hyps is None:
            continue
        if not isinstance(raw_hyps, list):
            errors.append(f"Task {task_id}: attempt_hypotheses must be a list")
            continue
        if len(raw_hyps) > MAX_ATTEMPT_HYPOTHESES:
            errors.append(f"Task {task_id}: attempt_hypotheses exceeds {MAX_ATTEMPT_HYPOTHESES}")
        seen_ids: set[str] = set()
        for idx, raw in enumerate(raw_hyps):
            try:
                norm = normalize_attempt_hypothesis(raw, task, index=idx)
            except PlanError as exc:
                errors.append(str(exc))
                continue
            if norm["id"] in seen_ids:
                errors.append(f"Task {task_id}: duplicate hypothesis id {norm['id']}")
            seen_ids.add(norm["id"])
            if norm["status"] == "disproven":
                disproven_texts.append((task_id, norm["id"], comparable_hypothesis_text(norm["hypothesis"])))

    if disproven_texts:
        # Ensure no disproven hypothesis appears in validated shared learnings or execution context.
        for artifact in manifest.get("learning_artifacts", []):
            if not isinstance(artifact, dict):
                continue
            for item in artifact.get("items", []):
                if not isinstance(item, dict):
                    continue
                folded = comparable_hypothesis_text(item.get("guidance", ""))
                for tid, hid, disproven_text in disproven_texts:
                    if repeats_disproven_hypothesis(disproven_text, folded):
                        errors.append(
                            f"Disproven hypothesis {tid}/{hid} leaked into validated learning {artifact.get('file')}"
                        )
        ec = manifest.get("execution_context") or {}
        if isinstance(ec, dict):
            ctx_items = list((ec.get("global") or {}).get("items", []))
            for scoped in ec.get("scoped", []):
                if isinstance(scoped, dict):
                    ctx_items.extend(scoped.get("items", []))
            for ctx_item in ctx_items:
                if not isinstance(ctx_item, dict):
                    continue
                folded = comparable_hypothesis_text(ctx_item.get("text", ""))
                for tid, hid, disproven_text in disproven_texts:
                    if repeats_disproven_hypothesis(disproven_text, folded):
                        errors.append(
                            f"Disproven hypothesis {tid}/{hid} leaked into normative execution_context"
                        )
    return errors


def build_context_accounting_receipt(
    plan_dir: Path,
    manifest: dict[str, Any],
    task: dict[str, Any],
    *,
    pattern_files: Iterable[str] | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Build a compact context accounting receipt: file IDs, byte counts and inclusion reasons, with no prompts or secrets."""
    selected: list[dict[str, Any]] = []
    universal_bytes = 0
    scoped_bytes = 0
    learning_bytes = 0
    pattern_bytes = 0
    stale_errors: list[str] = []

    def add_entry(
        entry_id: str,
        rel_path: str,
        trust_class: str,
        reason: str,
        *,
        fresh: bool = True,
        stale_reasons: list[str] | None = None,
    ) -> int:
        if not isinstance(rel_path, str) or not rel_path.strip():
            raise PlanError("Accounting entry path must be nonempty and repository-relative")
        safe_path = checked_relative_path(rel_path, "context accounting file")
        reject_symlink_components(plan_dir, Path(safe_path), "context accounting file")
        target = plan_dir / safe_path
        size = target.stat().st_size if target.is_file() and not target.is_symlink() else 0
        selected.append(
            {
                "id": entry_id,
                "path": rel_path,
                "trust_class": trust_class,
                "bytes": size,
                "reason": reason,
                "fresh": fresh,
                "stale_reasons": list(stale_reasons or []),
            }
        )
        return size

    task_file = task.get("file")
    if isinstance(task_file, str) and task_file:
        add_entry(
            f"task:{task['id']}",
            task_file,
            TRUST_CLASS_NORMATIVE,
            "assigned_task_definition",
        )

    for rel in task.get("context_files", []):
        if rel == GLOBAL_CONTEXT_FILE:
            universal_bytes += add_entry(
                "context:global",
                rel,
                TRUST_CLASS_NORMATIVE,
                "universal_constraint",
            )
        else:
            slug = Path(rel).stem
            scoped_bytes += add_entry(
                f"context:scoped:{slug}",
                rel,
                TRUST_CLASS_NORMATIVE,
                "assigned_scoped_context",
            )

    artifact_by_file = {
        str(item.get("file")): item
        for item in manifest.get("learning_artifacts", [])
        if isinstance(item, dict) and item.get("file")
    }
    for rel in task.get("learning_files", []):
        artifact = artifact_by_file.get(rel)
        if artifact is not None:
            freshness = check_learning_artifact_freshness(artifact, manifest, repo_root=repo_root, plan_dir=plan_dir)
            reasons = list(freshness["stale_reasons"])
            if (
                artifact.get("target_task_id") != task["id"]
                or artifact.get("consumer_task_ids") != [task["id"]]
                or str(artifact.get("source_task_id", "")) not in learning_source_ids(manifest, task["id"])
            ):
                reasons.append("learning_not_assigned_to_task")
            is_fresh = not reasons
            if not is_fresh:
                stale_errors.extend(f"{rel}:{r}" for r in reasons)
        else:
            is_fresh = False
            reasons = ["missing_manifest_learning_record"]
            stale_errors.append(f"{rel}:missing_manifest_learning_record")
        stem = Path(rel).stem
        learning_bytes += add_entry(
            f"learning:{stem}",
            rel,
            TRUST_CLASS_VALIDATED_LEARNING,
            "validated_directional_learning",
            fresh=is_fresh,
            stale_reasons=reasons,
        )

    for rel in pattern_files or []:
        if not isinstance(rel, str) or not rel.strip():
            continue
        stem = Path(rel).stem
        pattern_bytes += add_entry(
            f"pattern:{stem}",
            rel,
            TRUST_CLASS_VERSIONED_PATTERN,
            "versioned_shared_pattern",
        )

    total_bytes = sum(item["bytes"] for item in selected)
    receipt = {
        "schema_version": 1,
        "task_id": str(task.get("id", "")),
        "selected_files": selected,
        "total_context_bytes": total_bytes,
        "universal_context_bytes": universal_bytes,
        "scoped_context_bytes": scoped_bytes,
        "learning_bytes": learning_bytes,
        "pattern_bytes": pattern_bytes,
        "stale_learning_count": len(stale_errors),
        "stale_learning_errors": stale_errors,
        "contains_prompt_text": False,
        "contains_secrets": False,
        "cache_reuse": {
            "mode": "observed_metric_not_structural_assertion",
            "observed": False,
            "note": "Prompt prefix stability is structural; actual cache reuse must be observed per host/model.",
        },
    }
    if RECEIPT_SECRET_PATTERN.search(json.dumps(receipt, ensure_ascii=True)):
        raise PlanError("Context accounting receipt rejected due to possible unredacted secret")
    return receipt


def measure_plan_context_metrics(
    plan_dir: Path,
    manifest: dict[str, Any],
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Measure context bytes, universal budget compliance and stale-learning errors offline."""
    tasks = manifest.get("tasks", []) if isinstance(manifest.get("tasks"), list) else []
    per_task_bytes: dict[str, int] = {}
    stale_errors: list[str] = []
    for task in tasks:
        if not isinstance(task, dict):
            continue
        rcpt = build_context_accounting_receipt(plan_dir, manifest, task, repo_root=repo_root)
        per_task_bytes[str(task["id"])] = rcpt["total_context_bytes"]
        stale_errors.extend(f"{task['id']}:{err}" for err in rcpt["stale_learning_errors"])

    global_path = plan_dir / GLOBAL_CONTEXT_FILE
    universal_bytes = global_path.stat().st_size if global_path.is_file() and not global_path.is_symlink() else 0
    universal_chars = len(global_path.read_text(encoding="utf-8")) if global_path.is_file() and not global_path.is_symlink() else 0

    guidance_consumers: dict[str, set[str]] = {}
    for artifact in manifest.get("learning_artifacts", []):
        if not isinstance(artifact, dict):
            continue
        tgt = str(artifact.get("target_task_id", ""))
        for item in artifact.get("items", []):
            if isinstance(item, dict) and isinstance(item.get("guidance"), str):
                guidance_consumers.setdefault(item["guidance"].strip().casefold(), set()).add(tgt)
    repeated_for_pattern = [
        {"guidance_preview": text[:120], "consumer_count": len(consumers), "consumers": sorted(consumers)}
        for text, consumers in sorted(guidance_consumers.items())
        if len(consumers) >= 2
    ]

    disproven_count = sum(
        1
        for task in tasks
        if isinstance(task, dict)
        for hyp in task.get("attempt_hypotheses", [])
        if isinstance(hyp, dict) and hyp.get("status") == "disproven"
    )
    hyp_errors = validate_attempt_hypotheses(manifest, tasks)
    disproven_leaked = sum(1 for err in hyp_errors if "leaked into" in err)

    return {
        "schema_version": 1,
        "measurement_scope": "offline_deterministic",
        "task_count": len(tasks),
        "universal_context_bytes": universal_bytes,
        "universal_context_chars": universal_chars,
        "universal_context_budget_chars": MAX_CONTEXT_FILE_CHARS,
        "universal_within_budget": universal_chars <= MAX_CONTEXT_FILE_CHARS,
        "total_assigned_context_bytes": sum(per_task_bytes.values()),
        "per_task_bytes": per_task_bytes,
        "stale_learning_error_count": len(stale_errors),
        "stale_learning_errors": stale_errors,
        "repeated_learning_candidates_for_pattern": repeated_for_pattern,
        "disproven_hypotheses_count": disproven_count,
        "disproven_leaked_to_shared_facts": disproven_leaked,
        "live_task_success_measured": False,
        "live_measurement_limitation": (
            "Live task-success and host prompt-cache reuse require owner-authorized authenticated model runs "
            "and are recorded as an unmeasured offline limitation."
        ),
        "cache_reuse_observed": None,
    }


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

    # Manifest records are not an unlink allowlist. Check *all* targets,
    # canonical names, and symlink components before deleting any artifact.
    # This prevents a corrupted manifest from erasing other plan files and
    # keeps a reset from partially removing good learnings on preflight error.
    selected_files: set[str] = set()
    for artifact in selected:
        target_id = str(artifact.get("target_task_id", ""))
        target = find_task(manifest, target_id)
        if (
            target.get("status") != "pending"
            or int(target.get("attempts", 0)) != 0
            or target.get("started_at") is not None
        ):
            raise PlanError(
                f"Cannot reset completed task {task['id']}: learning artifact "
                f"{artifact.get('file')} has already become part of TODO {target['id']} execution"
            )
        relative = artifact.get("file")
        expected = learning_artifact_path(str(task["id"]), target_id)
        if not isinstance(relative, str) or relative != expected:
            raise PlanError(f"Refusing to remove learning artifact with unexpected path: {relative!r}")
        checked = checked_relative_path(relative, "learning artifact file")
        reject_symlink_components(plan_dir, Path(checked), "learning artifact")
        selected_files.add(checked)

    removed: list[str] = []
    for relative in sorted(selected_files):
        path = plan_dir / relative
        reject_symlink_components(plan_dir, Path(relative), "learning artifact")
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
    if task.get("learning_files"):
        artifact_by_file = {
            str(item.get("file")): item
            for item in manifest.get("learning_artifacts", [])
            if isinstance(item, dict) and item.get("file")
        }
        stale_msgs: list[str] = []
        # Only stale *source bytes* are safe for automatic retry invalidation.
        # Modified learning Markdown or forged provenance must remain a hard error.
        retry_source_changes_only = True
        for rel in task.get("learning_files", []):
            artifact = artifact_by_file.get(rel)
            if artifact is None:
                retry_source_changes_only = False
                stale_msgs.append(f"{rel} (missing manifest provenance)")
                continue
            # A fresh artifact for somebody else is not authorized for this task.
            # Check the directional edge before a worker can read the learning.
            if (
                artifact.get("target_task_id") != task["id"]
                or artifact.get("consumer_task_ids") != [task["id"]]
                or str(artifact.get("source_task_id", "")) not in learning_source_ids(manifest, task["id"])
            ):
                retry_source_changes_only = False
                stale_msgs.append(f"{rel} (learning not assigned to task {task['id']})")
                continue
            freshness = check_learning_artifact_freshness(artifact, manifest, plan_dir=plan_dir)
            if not freshness["fresh"]:
                if not freshness["stale_reasons"] or not all(
                    reason.startswith("cited_file_changed:") for reason in freshness["stale_reasons"]
                ):
                    retry_source_changes_only = False
                stale_msgs.append(f"{rel} ({', '.join(freshness['stale_reasons'])})")
        if stale_msgs and retry_source_changes_only and int(task.get("attempts", 0)) > 0:
            # On retry the consumer may have edited a cited file itself. Never
            # reuse the old learning or require a manual repair just to resume.
            # The invalidator preflights every deletion and preserves an audit
            # record; unauthorized/missing records still fail closed below.
            invalidate_stale_learnings(plan_dir, manifest, task_id=task["id"])
            return claim_task(plan_dir, manifest, task_id, route)
        if stale_msgs:
            raise PlanError(
                f"Task {task['id']} cannot reuse stale learning(s): {'; '.join(stale_msgs)}; "
                "recheck cited files or run check-learnings --invalidate-stale first"
            )
    task["status"] = "in_progress"
    task["attempts"] += 1
    task["started_at"] = task["started_at"] or now_utc()
    task["current_route"] = route
    task["history"].append({"at": now_utc(), "event": "claimed", "route": route})
    append_event(manifest, "task_claimed", task_id=task["id"], route=route)
    save_manifest(plan_dir, manifest)
    return task


def require_runner_proof_for_learnings(
    plan_dir: Path, manifest: dict[str, Any], task: dict[str, Any],
    report: dict[str, Any], runner_proof_sha256: str | None,
) -> None:
    """Untrusted completion JSON is never sufficient to publish a validated fact.

    The runner supplies the digest of its log-bound evidence in a separate Python
    argument. The public complete CLI does not accept that argument.
    """
    if not report.get("reusable_learnings"):
        return
    if not isinstance(runner_proof_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", runner_proof_sha256):
        raise PlanError("Validated reusable learnings require genuine runner validation proof")
    attempt = int(task.get("attempts", 0))
    log_name = f"{task['id']}-attempt-{attempt}-validation.log"
    log_rel = checked_relative_path(f"logs/{log_name}", "learning validation log")
    proof_rel = checked_relative_path(f"{log_rel}.runner-evidence.json", "learning runner proof")
    for relative in (log_rel, proof_rel):
        reject_symlink_components(plan_dir, Path(relative), "learning runner proof")
    log_path, proof_path = plan_dir / log_rel, plan_dir / proof_rel
    if not log_path.is_file() or not proof_path.is_file() or proof_path.is_symlink() or log_path.is_symlink():
        raise PlanError("Validated reusable learnings require genuine runner validation log and proof")
    try:
        proof = read_json(proof_path)
    except (OSError, ValueError) as exc:
        raise PlanError("Learning runner proof is missing or unreadable") from exc
    digest = compute_task_contract_digests(manifest.get("tasks", [])).get(task["id"])
    if (not isinstance(proof, dict)
        or proof.get("schema_version") != 2
        or proof.get("task_id") != task["id"]
        or proof.get("attempt") != attempt
        or proof.get("contract_digest") != digest
        or proof.get("passed") is not True
        or proof.get("log_sha256") != file_sha256(log_path)
        or file_sha256(proof_path) != runner_proof_sha256):
        raise PlanError("Learning runner proof does not match the completed attempt")
    actual_checks = proof.get("checks")
    report_checks = report.get("validation_results")
    if not isinstance(actual_checks, list) or not isinstance(report_checks, list) or not actual_checks:
        raise PlanError("Learning runner proof is missing observed validation results")
    for check in report_checks:
        if (not isinstance(check, dict) or check.get("passed") is not True
            or type(check.get("exit_code")) is not int or check.get("exit_code") != 0
            or not any(isinstance(observed, dict)
                       and observed.get("command") == check.get("command")
                       and observed.get("passed") is True
                       and type(observed.get("exit_code")) is int
                       and observed.get("exit_code") == 0
                       for observed in actual_checks)):
            raise PlanError("Learning validation results are not supported by the runner proof")
    for command in task.get("validation_commands", []):
        if not any(isinstance(observed, dict) and observed.get("command") == command
                   and observed.get("passed") is True and observed.get("exit_code") == 0
                   for observed in actual_checks):
            raise PlanError("Learning runner proof does not cover declared validation commands")


def complete_task(
    plan_dir: Path,
    manifest: dict[str, Any],
    task_id: str,
    report: dict[str, Any],
    result_file: str | None,
    *,
    runner_proof_sha256: str | None = None,
) -> dict[str, Any]:
    task = find_task(manifest, task_id)
    if runner_proof_sha256 is not None and not re.fullmatch(r"[0-9a-f]{64}", runner_proof_sha256):
        raise PlanError("Runner proof digest must be a canonical SHA-256 hash")
    if task["status"] != "in_progress":
        raise PlanError(f"Task {task['id']} is not in progress")
    if isinstance(report, dict):
        evidence_kind = str(report.get("evidence_kind", "")).strip().lower()
        source_kind = str(report.get("source", "")).strip().lower()
        if (
            evidence_kind == "prepared_research"
            or source_kind == "prepared_research"
            or report.get("prepared_research_only") is True
        ):
            raise PlanError(
                f"Task {task['id']}: prepared research is not proof of implementation or independent-review completion"
            )
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
    completed_at = now_utc()
    receipt: dict[str, Any] | None = None
    executed_digest: str | None = None
    if int(manifest.get("schema_version", 0) or 0) >= 4:
        # Validate the receipt before any side effect (subtask reconciliation, learning
        # files), so a rejected completion leaves nothing behind for a later save.
        # Bind it to the contract actually executed: a contract edited outside `revise`
        # must not make every later completion fail with a digest mismatch. Only this
        # task's stored digest is refreshed; other tasks keep theirs, so `revise` still
        # sees their out-of-band edits as contract changes.
        executed_digest = compute_task_contract_digests(manifest.get("tasks", [])).get(task["id"])
        candidate_task = {
            **task,
            "contract_digest": executed_digest,
            "completed_at": completed_at,
            "changed_files": clean_files,
        }
        declared_inputs = dict(task.get("scoped_input_digests") or {})
        if declared_inputs:
            # Bind the receipt to the scoped inputs actually on disk, not to the plan's own claim.
            candidate_task["scoped_input_digests"] = observe_scoped_input_digests(
                Path(str(manifest.get("repo_root") or ".")), declared_inputs
            )
        receipt = build_task_receipt(
            manifest, candidate_task, report if isinstance(report, dict) else None, result_file
        )
        if runner_proof_sha256 is not None:
            # Only the trusted runner process passes this separate keyword.
            # A bare `planctl complete --report` cannot bind a fabricated
            # sidecar to the completion receipt via worker-supplied JSON.
            receipt["runner_proof_sha256"] = runner_proof_sha256
        verdict = validate_receipt(receipt, task, manifest=manifest)
        if not verdict["valid"]:
            raise PlanError(
                f"Task {task['id']} completion receipt failed validity check: {', '.join(verdict['reasons'])}"
            )
    if isinstance(report, dict):
        require_runner_proof_for_learnings(plan_dir, manifest, task, report, runner_proof_sha256)
        reconcile_reported_subtasks(task, report)
        published_learning_files = materialize_learning_artifacts(
            plan_dir,
            manifest,
            task,
            report,
            source_contract_digest=executed_digest,
        )
    else:
        published_learning_files = []
    if executed_digest:
        task["contract_digest"] = executed_digest
    task["status"] = "completed"
    task["completed_at"] = completed_at
    task["last_error"] = None
    task.pop("validation_stagnation", None)
    task.pop("latest_validation_log", None)
    task["changed_files"] = clean_files
    task["validation_results"] = report.get("validation_results", []) if isinstance(report, dict) else []
    task["result_file"] = result_file
    if receipt is not None:
        task["current_receipt"] = receipt
        task.setdefault("receipt_history", [])
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


def normalize_failure_class(value: Any) -> str:
    cls = str(value or "unknown").strip().lower()
    if cls not in VALID_FAILURE_CLASSES:
        raise PlanError(
            f"failure_class must be one of {sorted(VALID_FAILURE_CLASSES)}; received {cls!r}"
        )
    return cls


def bounded_failure_reason(value: str, limit: int = 1800) -> str:
    text = value.strip()
    if len(text) <= limit:
        return text
    head_size = min(420, limit // 3)
    tail_size = max(0, limit - head_size - 24)
    return text[:head_size].rstrip() + "\n[… middle omitted …]\n" + text[-tail_size:].lstrip()


def fail_task(
    plan_dir: Path,
    manifest: dict[str, Any],
    task_id: str,
    reason: str,
    *,
    rate_limited: bool = False,
    failure_class: str | None = None,
    validation_signature: str | None = None,
    validation_stalled: bool = False,
    validation_idle_seconds: int = 0,
    validation_log: str | None = None,
    hypothesis: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Record a failed attempt.

    `failure_class` is evidence for the next route (see routingctl.escalation_step):
    mechanical/budget repeat the rung once, semantic jumps a tier, environmental
    keeps the route, plan_defect blocks the task for replanning, unknown climbs one rung.
    Rate-limit/availability events are never failure evidence.
    """
    task = find_task(manifest, task_id)
    if task["status"] != "in_progress":
        raise PlanError(f"Task {task['id']} is not in progress")
    recovered_subtasks = recover_in_progress_subtasks(task, reason)
    cls = None
    if rate_limited:
        task["rate_limit_events"] += 1
        event = "rate_limited"
    else:
        cls = normalize_failure_class(failure_class)
        task["functional_failures"] += 1
        task.setdefault("failure_classes", []).append(cls)
        event = "failed"
    now = now_utc()
    task["last_error"] = bounded_failure_reason(reason)
    recorded_reason = task["last_error"]
    if not rate_limited:
        if validation_signature:
            if validation_log:
                task["latest_validation_log"] = validation_log
            previous = task.get("validation_stagnation")
            same_signature = isinstance(previous, dict) and previous.get("signature") == validation_signature
            first_at = previous.get("first_at") if same_signature else now
            repeats = int(previous.get("repeats", 0)) + 1 if same_signature else 1
            try:
                first_time = dt.datetime.fromisoformat(str(first_at))
                elapsed = max(0, int((dt.datetime.fromisoformat(now) - first_time).total_seconds()))
            except (TypeError, ValueError):
                first_at, elapsed = now, 0
            triggered = bool(validation_stalled or elapsed >= 300 or (same_signature and previous.get("triggered") is True))
            task["validation_stagnation"] = {
                "signature": validation_signature,
                "first_at": first_at,
                "last_at": now,
                "repeats": repeats,
                "elapsed_seconds": elapsed,
                "idle_seconds": max(0, int(validation_idle_seconds)),
                "triggered": triggered,
            }
            if repeats > 1:
                recorded_reason = (
                    f"Repeated validation signature {validation_signature[:12]} "
                    f"(repeat {repeats}; persisted {elapsed}s); latest excerpt is in last_error."
                )
        else:
            task.pop("validation_stagnation", None)
            task.pop("latest_validation_log", None)
    if not rate_limited and task.get("attempt_hypotheses"):
        invalidate_stale_hypotheses(plan_dir, manifest, task["id"], save=False)
    if not rate_limited and hypothesis is None and validation_signature:
        hypothesis = {
            "hypothesis": (
                "The failed deterministic validation with signature "
                + str(validation_signature)[:12]
                + " may indicate an unverified implementation or environment mismatch."
            ),
            "evidence_refs": ["VALIDATION-" + str(validation_signature)[:16]],
            "failure_signature": validation_signature,
        }
    if not rate_limited and isinstance(hypothesis, dict):
        record_attempt_hypothesis(
            plan_dir,
            manifest,
            task["id"],
            str(hypothesis.get("hypothesis", "")),
            list(hypothesis.get("evidence_refs") or []),
            status=str(hypothesis.get("status") or "open"),
            disproven_reason=hypothesis.get("disproven_reason"),
            failure_signature=hypothesis.get("failure_signature") or validation_signature,
            save=False,
        )
    if not rate_limited and (
        task["functional_failures"] >= task["max_attempts"] or cls in {"plan_defect", "timeout_ceiling"}
    ):
        task["status"] = "blocked"
    else:
        task["status"] = "pending"
    task["history"].append(
        {
            "at": now_utc(),
            "event": event,
            "failure_class": cls,
            "reason": recorded_reason,
            "recovered_subtasks": recovered_subtasks,
        }
    )
    append_event(
        manifest,
        f"task_{event}",
        task_id=task["id"],
        failure_class=cls,
        reason=recorded_reason,
        recovered_subtasks=recovered_subtasks,
    )
    save_manifest(plan_dir, manifest)
    return task


def block_task(plan_dir: Path, manifest: dict[str, Any], task_id: str, reason: str, *, event: str = "blocked") -> dict[str, Any]:
    """Block a pending task without counting a new attempt (e.g. ladder exhausted)."""
    task = find_task(manifest, task_id)
    if task["status"] not in ("pending", "in_progress"):
        raise PlanError(f"Task {task['id']} cannot be blocked from status {task['status']}")
    if task["status"] == "in_progress":
        recover_in_progress_subtasks(task, reason)
    task["status"] = "blocked"
    task["last_error"] = reason.strip()[:4000]
    task["history"].append({"at": now_utc(), "event": event, "reason": task["last_error"]})
    append_event(manifest, f"task_{event}", task_id=task["id"], reason=task["last_error"])
    save_manifest(plan_dir, manifest)
    return task


def release_design_claim(plan_dir: Path, manifest: dict[str, Any], task_id: str) -> dict[str, Any]:
    """Return a task claimed for its design phase to pending without spending an attempt."""
    task = find_task(manifest, task_id)
    if task["status"] != "in_progress":
        raise PlanError(f"Task {task['id']} is not in progress")
    task["status"] = "pending"
    task["attempts"] = max(0, int(task.get("attempts", 1)) - 1)
    task["current_route"] = None
    task["last_error"] = None
    save_manifest(plan_dir, manifest)
    return task


def complete_design_phase(
    plan_dir: Path,
    manifest: dict[str, Any],
    task_id: str,
    note_file: str,
    route: dict[str, Any] | None,
) -> dict[str, Any]:
    """Persist that a two-phase leaf's design note exists and was accepted."""
    task = find_task(manifest, task_id)
    if not task.get("design_route"):
        raise PlanError(f"Task {task['id']} has no design_route")
    task["design_phase"] = {
        "status": "completed",
        "note_file": note_file,
        "route": route,
        "completed_at": now_utc(),
    }
    task["history"].append(
        {"at": now_utc(), "event": "design_completed", "note_file": note_file, "route": route}
    )
    append_event(manifest, "task_design_completed", task_id=task["id"], note_file=note_file, route=route)
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
    if was_completed and int(manifest.get("schema_version", 0) or 0) >= 4:
        if task.get("current_receipt") or task.get("result_file") or task.get("completed_at"):
            next_gen = (
                int(manifest["generation"]) + 1
                if isinstance(manifest.get("generation"), int) and not isinstance(manifest.get("generation"), bool)
                else None
            )
            archived = _archive_task_receipt(
                task,
                manifest,
                superseded_by_generation=next_gen,
                reason="Parent task explicitly reset",
            )
            task.setdefault("receipt_history", []).append(archived)
        task["current_receipt"] = None
    task["status"] = "pending"
    task["last_error"] = None
    task["current_route"] = None
    task["completed_at"] = None
    task["result_file"] = None
    task["changed_files"] = []
    task["validation_results"] = []
    if task.get("design_route"):
        previous_note = (task.get("design_phase") or {}).get("note_file")
        if previous_note:
            note_path = plan_dir / previous_note
            if note_path.is_file():
                note_path.unlink()
        task["design_phase"] = {"status": "pending", "note_file": None, "route": None, "completed_at": None}
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
        commands = ", ".join([
            *[f"`{cmd}`" for cmd in task["validation_commands"]],
            *[f"supervised job `{job}`" for job in task.get("validation_jobs", [])],
        ])
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
    jobs_root = plan_dir / "jobs"
    if jobs_root.exists():
        import jobctl
        for job_dir in jobs_root.iterdir():
            if not job_dir.is_dir():
                raise PlanError("Refusing cleanup with an invalid job workspace")
            try:
                state = jobctl.status_job(plan_dir, job_dir.name)
            except jobctl.JobError as exc:
                raise PlanError("Refusing cleanup with unknown job ownership") from exc
            if state.get("state") in {"starting", "running", "lost"} or (state.get("reason") == "supervisor_start_failed" and state.get("pid")):
                raise PlanError("Refusing cleanup with a live or unowned supervised job; preserve evidence and stop it first")
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
    return parse_strict_json(value, "CLI argument")


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


def command_revise(args: argparse.Namespace) -> None:
    spec = read_json(Path(args.spec).expanduser().resolve())
    if not isinstance(spec, dict):
        raise PlanError("Plan spec root must be an object")
    mapping = parse_json_arg(args.task_id_mapping, None)
    scoped = parse_json_arg(args.scoped_input_digests, None)
    record = revise_plan(
        args.plan,
        spec,
        amendment=args.amendment,
        expected_generation=args.expected_generation,
        task_id_mapping=mapping,
        scoped_input_digests=scoped,
    )
    print(json.dumps(record, ensure_ascii=False, indent=2))


def command_recover_projections(args: argparse.Namespace) -> None:
    result = recover_projections(args.plan)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def command_validate_receipt(args: argparse.Namespace) -> None:
    _plan_dir, manifest = load_plan(args.plan)
    task = find_task(manifest, args.task)
    receipt = parse_json_arg(args.receipt, None) if args.receipt else task.get("current_receipt")
    scoped = parse_json_arg(args.scoped_input_digests, None)
    declared = dict(task.get("scoped_input_digests") or {})
    if scoped is None and declared:
        # Default to the inputs as they are now, so drift since completion is visible.
        scoped = observe_scoped_input_digests(Path(str(manifest.get("repo_root") or ".")), declared)
    result = validate_receipt(
        receipt,
        task,
        manifest=manifest,
        scoped_input_digests=scoped,
        require_review_verdict=bool(getattr(args, "require_review_verdict", False)),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["valid"]:
        raise SystemExit(2)


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
    task = fail_task(
        plan_dir,
        manifest,
        args.task,
        args.reason,
        rate_limited=args.rate_limited,
        failure_class=getattr(args, "failure_class", None),
    )
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


def command_check_learnings(args: argparse.Namespace) -> None:
    plan_dir, manifest = load_plan(args.plan)
    if args.invalidate_stale:
        result = invalidate_stale_learnings(plan_dir, manifest, task_id=args.task)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    artifacts = manifest.get("learning_artifacts", [])
    task_filter = normalize_task_id(args.task) if args.task else None
    checks = [
        check_learning_artifact_freshness(artifact, manifest, plan_dir=plan_dir)
        for artifact in artifacts
        if isinstance(artifact, dict)
        and (task_filter is None or str(artifact.get("target_task_id", "")) == task_filter)
    ]
    stale = [item for item in checks if not item["fresh"]]
    payload = {"checked": len(checks), "stale_count": len(stale), "learnings": checks}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if stale:
        raise SystemExit(2)


def command_context_receipt(args: argparse.Namespace) -> None:
    plan_dir, manifest = load_plan(args.plan)
    if args.task:
        task = find_task(manifest, args.task)
        payload = build_context_accounting_receipt(plan_dir, manifest, task)
    else:
        payload = measure_plan_context_metrics(plan_dir, manifest)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def command_hypothesis_record(args: argparse.Namespace) -> None:
    plan_dir, manifest = load_plan(args.plan)
    entry = record_attempt_hypothesis(plan_dir, manifest, args.task, args.text, args.reference)
    print(json.dumps(entry, ensure_ascii=False, indent=2))


def command_hypothesis_disprove(args: argparse.Namespace) -> None:
    plan_dir, manifest = load_plan(args.plan)
    entry = mark_hypothesis_disproven(plan_dir, manifest, args.task, args.hypothesis_id, args.reason)
    print(json.dumps(entry, ensure_ascii=False, indent=2))


def command_hypothesis_promote(args: argparse.Namespace) -> None:
    plan_dir, manifest = load_plan(args.plan)
    evidence = parse_json_arg(args.evidence, None)
    item = promote_hypothesis_to_learning(
        plan_dir, manifest, args.task, args.hypothesis_id,
        kind=args.kind, target_task_ids=args.target, deterministic_evidence=evidence,
        guidance=args.guidance,
    )
    print(json.dumps(item, ensure_ascii=False, indent=2))


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

    revise = sub.add_parser(
        "revise",
        help="Stage, validate, and publish a new plan generation with selective invalidation",
    )
    revise.add_argument("--plan", required=True)
    revise.add_argument("--spec", required=True)
    revise.add_argument("--amendment", required=True)
    revise.add_argument(
        "--expected-generation",
        type=int,
        required=True,
        help="Manifest generation the spec was written against (0 for a manifest without one)",
    )
    revise.add_argument("--task-id-mapping", help="Optional JSON object/file mapping old->new task IDs")
    revise.add_argument("--scoped-input-digests", help="Optional JSON object/file mapping task_id->{path: sha256}")
    revise.set_defaults(func=command_revise)

    recover = sub.add_parser(
        "recover-projections",
        help="Rebuild schema-v4 projections strictly from authoritative manifest.json and clean staging",
    )
    recover.add_argument("--plan", required=True)
    recover.set_defaults(func=command_recover_projections)

    validate_rcpt = sub.add_parser(
        "validate-receipt",
        help="Validate a task completion receipt against task contract digest and scoped inputs",
    )
    validate_rcpt.add_argument("--plan", required=True)
    validate_rcpt.add_argument("--task", required=True)
    validate_rcpt.add_argument("--receipt", help="Optional receipt JSON object or file (defaults to task current_receipt)")
    validate_rcpt.add_argument(
        "--scoped-input-digests",
        help="Optional JSON object/file of current scoped input hashes (default: hash the declared inputs on disk)",
    )
    validate_rcpt.add_argument(
        "--require-review-verdict",
        action="store_true",
        help="Reject a requires_independent_review receipt that records no approved verdict",
    )
    validate_rcpt.set_defaults(func=command_validate_receipt)

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
    fail.add_argument(
        "--failure-class",
        choices=sorted(VALID_FAILURE_CLASSES),
        default=None,
        help="Evidence for the next route: mechanical, semantic, environmental, budget, plan_defect, unknown",
    )
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

    check_learnings = sub.add_parser(
        "check-learnings",
        help="Check learning provenance and cited-file freshness, optionally invalidating stale entries",
    )
    check_learnings.add_argument("--plan", required=True)
    check_learnings.add_argument("--task", help="Optional target task id filter")
    check_learnings.add_argument(
        "--invalidate-stale",
        action="store_true",
        help="Remove stale learnings without deleting unrelated fresh learnings",
    )
    check_learnings.set_defaults(func=command_check_learnings)

    context_receipt = sub.add_parser(
        "context-receipt",
        help="Emit compact context accounting receipt for one task or offline plan context metrics",
    )
    context_receipt.add_argument("--plan", required=True)
    context_receipt.add_argument("--task", help="Optional task id; omit for plan-level offline metrics")
    context_receipt.set_defaults(func=command_context_receipt)

    hyp_record = sub.add_parser("hypothesis-record", help="Record task-local unvalidated diagnosis")
    hyp_record.add_argument("--plan", required=True)
    hyp_record.add_argument("--task", required=True)
    hyp_record.add_argument("--text", required=True)
    hyp_record.add_argument("--reference", action="append", required=True)
    hyp_record.set_defaults(func=command_hypothesis_record)

    hyp_disprove = sub.add_parser("hypothesis-disprove", help="Mark failed-attempt hypothesis disproven")
    hyp_disprove.add_argument("--plan", required=True)
    hyp_disprove.add_argument("--task", required=True)
    hyp_disprove.add_argument("--hypothesis-id", required=True)
    hyp_disprove.add_argument("--reason", required=True)
    hyp_disprove.set_defaults(func=command_hypothesis_disprove)

    hyp_promote = sub.add_parser("hypothesis-promote", help="Publish only with verified runner validation proof")
    hyp_promote.add_argument("--plan", required=True)
    hyp_promote.add_argument("--task", required=True)
    hyp_promote.add_argument("--hypothesis-id", required=True)
    hyp_promote.add_argument("--kind", required=True, choices=sorted(VALID_LEARNING_KINDS))
    hyp_promote.add_argument("--target", action="append", required=True)
    hyp_promote.add_argument("--evidence", required=True, help="JSON list or file of checked runner validation results")
    hyp_promote.add_argument("--guidance")
    hyp_promote.set_defaults(func=command_hypothesis_promote)

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
