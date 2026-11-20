#!/usr/bin/env python3
"""Validate and preserve adaptive pre-plan study evidence.

The study gate is intentionally independent from planctl.py so existing plan
schema versions remain compatible. New studies first classify request complexity
and may skip evidence collection entirely, perform bounded discovery, or honor
user-selected complex-study depth. The validated decision and any findings are
then attached to the plan.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse

SCHEMA_VERSION = 2
SUPPORTED_SCHEMA_VERSIONS = {1, 2}
EVIDENCE_LEDGER_SCHEMA_VERSION = 1
STUDY_JSON = "study.json"
STUDY_MD = "STUDY.md"
MANIFEST = "manifest.json"
SENTINEL = ".orchestrator-plan"

VALID_IMPORTANCE = {"low", "medium", "high"}
VALID_QUESTION_STATUS = {"resolved", "assumed", "open", "probe_required"}
VALID_READING_SCOPES = {
    "discovery_only",
    "abstract_only",
    "inspected_section",
    "full_source",
    "inaccessible",
}
VERIFIED_READING_SCOPES = {"inspected_section", "full_source"}
UNVERIFIED_READING_SCOPES = {"discovery_only", "abstract_only", "inaccessible"}
VALID_EVIDENCE_KINDS = {
    "verified_source_fact",
    "observed_repository_behavior",
    "proposed_design",
}
VALID_CONFIDENCE_LEVELS = {"high", "medium", "low", "unknown"}
VALID_EVIDENCE_DOMAINS = {
    "cli_interface",
    "api_pricing",
    "subscription_quota",
    "account_capability",
    "model_catalog",
    "architecture",
    "security",
    "routing",
    "validation",
    "general",
}
VALID_CLAIM_TYPES = {
    "verified_interface",
    "subscription_quota",
    "api_pricing",
    "behavior_observation",
    "design_recommendation",
    "capability_probe",
}
VALID_INVALIDATION_SIGNALS = {
    "cli_version_change",
    "provider_version_change",
    "source_digest_change",
    "model_contract_change",
    "account_capability_change",
    "contradicted_evidence",
    "missing_date_or_version",
}
VALID_REPORT_STATUSES = {"pending", "in_progress", "completed"}
VALID_EVIDENCE_ORIGINS = {"prepared_research", "implementation", "independent_review"}
PREPARED_RESEARCH_PATH_MARKER = "prepared-research/"
PREPARED_REPORT_WAIVER_EXCLUDED_TRIGGERS = ("security_sensitive", "conflicting_evidence")
# Signal kinds that match nothing unless they name a concrete target.
SIGNAL_REQUIRED_TARGETS = {
    "provider_version_change": ("provider",),
    "source_digest_change": ("source_ids",),
    "missing_date_or_version": ("source_ids",),
    "contradicted_evidence": ("source_ids", "material_question_id"),
}
UNDATED_VERSION_PLACEHOLDERS = {
    "",
    "unknown",
    "undated",
    "unversioned",
    "none",
    "n/a",
    "na",
    "latest",
    "current",
    "tbd",
    "unspecified",
}
MAX_SOURCE_SUMMARY_CHARS = 480
VERSION_OR_DATE_PATTERN = re.compile(
    r"(?:\b(?:19|20)\d{2}(?:-\d{2}(?:-\d{2})?|-Q[1-4])?\b|\bv?\d+\.\d+(?:\.\d+)?(?:[-+][A-Za-z0-9._-]+)?\b|\bv\d+\b)",
    re.I,
)
VALID_INTERNAL_KINDS = {
    "instructions",
    "architecture",
    "implementation",
    "tests",
    "build",
    "schema",
    "interface",
    "ci",
    "history",
    "other",
}
VALID_COMPLEXITY_LEVELS = {"simple", "medium", "complex"}
VALID_INTERNAL_SELECTION_SOURCES = {"automatic", "user"}
VALID_INTERNAL_DEPTHS = {"none", "related_packages", "workspace_keywords", "full_project"}
VALID_EXTERNAL_SELECTION_SOURCES = {"automatic", "user"}
VALID_EXTERNAL_DEPTHS = {"none", "focused", "broad"}
VALID_EXTERNAL_DECISIONS = {"required", "not_needed", "blocked"}
VALID_EXTERNAL_SOURCE_TYPES = {
    "official_documentation",
    "standard",
    "research_paper",
    "vendor_advisory",
    "authoritative_other",
}
TRIGGER_FIELDS = (
    "user_requested",
    "unfamiliar_domain",
    "version_sensitive",
    "security_sensitive",
    "current_behavior",
    "repository_gap",
    "conflicting_evidence",
    "technology_selection",
    "high_risk",
)
REVIEW_CHECKS = (
    "internal_coverage_sufficient",
    "external_decision_justified",
    "source_quality_sufficient",
    "findings_translated_to_plan",
    "contradictions_resolved",
)
SYNTHESIS_FIELDS = (
    "planning_constraints",
    "derived_requirements",
    "risks",
    "validation_implications",
)


class StudyError(RuntimeError):
    """Raised when study evidence or its plan attachment is invalid."""


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def ensure_text(value: Any, field: str, minimum: int = 1) -> str:
    if not isinstance(value, str) or not value.strip():
        raise StudyError(f"{field} must be a non-empty string")
    text = value.strip()
    if len(text) < minimum:
        raise StudyError(f"{field} must contain at least {minimum} characters")
    return text


def ensure_list(value: Any, field: str) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise StudyError(f"{field} must be a list")
    return value


def ensure_str_list(value: Any, field: str) -> list[str]:
    result: list[str] = []
    for index, item in enumerate(ensure_list(value, field)):
        result.append(ensure_text(item, f"{field}[{index}]"))
    return result


def ensure_object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise StudyError(f"{field} must be an object")
    return value


def normalize_id(value: Any, prefix: str, field: str) -> str:
    text = ensure_text(value, field).upper()
    pattern = rf"{re.escape(prefix)}[0-9]{{3,}}"
    if not re.fullmatch(pattern, text):
        raise StudyError(f"{field} must match {prefix} followed by at least three digits")
    return text


def normalize_source_id(value: Any, field: str) -> str:
    text = ensure_text(value, field).upper()
    if not re.fullmatch(r"[A-Z][A-Z0-9_-]{1,31}", text):
        raise StudyError(
            f"{field} must be a stable source identifier (2-32 chars of A-Z, 0-9, _, -)"
        )
    return text


def normalize_optional_iso_date(value: Any, field: str) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if not text:
        return ""
    try:
        dt.date.fromisoformat(text)
    except ValueError as exc:
        raise StudyError(f"{field} must be an ISO date (YYYY-MM-DD): {text!r}") from exc
    return text


def has_explicit_version_or_date(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    text = value.strip()
    if text.casefold() in UNDATED_VERSION_PLACEHOLDERS:
        return False
    return bool(VERSION_OR_DATE_PATTERN.search(text))


def resolve_source_dating(
    data: dict[str, Any], field: str, evidence_domain: str
) -> tuple[str, bool, bool]:
    """Return (version_or_date, has_version_or_date, affects_cli_behavior) for one source.

    A source without an explicit version or date must say whether it affects CLI
    behavior; otherwise an unlabelled undated source could silently skip refresh.
    """
    raw_version = str(data.get("version_or_date") or "").strip()
    has_version = has_explicit_version_or_date(raw_version)
    affects_cli = data.get("affects_cli_behavior")
    if affects_cli is not None and not isinstance(affects_cli, bool):
        raise StudyError(f"{field}.affects_cli_behavior must be true or false")
    declared = isinstance(affects_cli, bool) or evidence_domain == "cli_interface"
    if not has_version and not declared:
        raise StudyError(
            f"{field}.version_or_date must record an explicit version or date; an undated "
            "source must declare affects_cli_behavior (true or false) so CLI-affecting "
            "evidence is flagged for refresh"
        )
    affects_cli_behavior = bool(affects_cli) or evidence_domain == "cli_interface"
    return (raw_version or "unknown"), has_version, affects_cli_behavior


def normalize_reading_scope(
    value: Any, field: str, *, default: str | None = None
) -> str:
    if value is None or (isinstance(value, str) and not value.strip()):
        if default is not None:
            return default
        raise StudyError(
            f"{field} must be one of " + ", ".join(sorted(VALID_READING_SCOPES))
        )
    scope = ensure_text(value, field).lower()
    if scope not in VALID_READING_SCOPES:
        raise StudyError(
            f"{field} must be one of " + ", ".join(sorted(VALID_READING_SCOPES))
        )
    return scope


def normalize_evidence_domain(
    value: Any, field: str, *, default: str = "general"
) -> str:
    if value is None or (isinstance(value, str) and not value.strip()):
        return default
    domain = ensure_text(value, field).lower()
    if domain not in VALID_EVIDENCE_DOMAINS:
        raise StudyError(
            f"{field} must be one of " + ", ".join(sorted(VALID_EVIDENCE_DOMAINS))
        )
    return domain


def normalize_claim_type(value: Any, field: str, *, default: str = "") -> str:
    if value is None or (isinstance(value, str) and not value.strip()):
        return default
    claim_type = ensure_text(value, field).lower()
    if claim_type not in VALID_CLAIM_TYPES:
        raise StudyError(
            f"{field} must be one of " + ", ".join(sorted(VALID_CLAIM_TYPES))
        )
    return claim_type


def normalize_evidence_kind(
    value: Any, field: str, *, default: str | None = None
) -> str:
    if value is None or (isinstance(value, str) and not value.strip()):
        if default is not None:
            return default
        raise StudyError(
            f"{field} must be one of " + ", ".join(sorted(VALID_EVIDENCE_KINDS))
        )
    kind = ensure_text(value, field).lower()
    if kind not in VALID_EVIDENCE_KINDS:
        raise StudyError(
            f"{field} must be one of " + ", ".join(sorted(VALID_EVIDENCE_KINDS))
        )
    return kind


def normalize_confidence(
    value: Any, field: str, *, default: str | None = None
) -> str:
    if value is None or (isinstance(value, str) and not value.strip()):
        if default is not None:
            return default
        raise StudyError(
            f"{field} must be one of " + ", ".join(sorted(VALID_CONFIDENCE_LEVELS))
        )
    confidence = ensure_text(value, field).lower()
    if confidence not in VALID_CONFIDENCE_LEVELS:
        raise StudyError(
            f"{field} must be one of " + ", ".join(sorted(VALID_CONFIDENCE_LEVELS))
        )
    return confidence


def normalize_capability_probe(raw: Any, field: str) -> dict[str, Any]:
    data = ensure_object(raw, field)
    changes_silently = data.get("changes_acceptance_silently", False)
    if not isinstance(changes_silently, bool):
        raise StudyError(f"{field}.changes_acceptance_silently must be true or false")
    if changes_silently:
        raise StudyError(
            f"{field}: an unresolved issue or capability probe cannot silently change acceptance"
        )
    return {
        "check": ensure_text(data.get("check"), f"{field}.check", 8),
        "falsification_condition": ensure_text(
            data.get("falsification_condition"),
            f"{field}.falsification_condition",
            8,
        ),
        "conservative_fallback": ensure_text(
            data.get("conservative_fallback"),
            f"{field}.conservative_fallback",
            8,
        ),
        "changes_acceptance_silently": False,
    }


def summarize_reading_scopes(
    sources: Iterable[dict[str, Any]],
    failed_access_attempts: Iterable[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    buckets: dict[str, list[str]] = {
        "discovery_only": [],
        "abstract_only": [],
        "inspected_section": [],
        "full_source": [],
        "inaccessible": [],
    }
    verified_ids: list[str] = []
    unverified_ids: list[str] = []
    for source in sources:
        scope = source.get("reading_scope", "inspected_section")
        source_id = str(source["id"])
        if scope in buckets:
            buckets[scope].append(source_id)
        if scope in VERIFIED_READING_SCOPES:
            verified_ids.append(source_id)
        else:
            unverified_ids.append(source_id)
    return {
        **buckets,
        "verified_support_ids": verified_ids,
        "unverified_source_ids": unverified_ids,
        "failed_access_count": len(list(failed_access_attempts or [])),
    }


def collect_refresh_flags(sources: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    flags: list[dict[str, Any]] = []
    for source in sources:
        if source.get("refresh_required"):
            flags.append(
                {
                    "source_id": str(source["id"]),
                    "signal": "missing_date_or_version",
                    "affects_cli_behavior": bool(source.get("affects_cli_behavior")),
                    "reasons": list(source.get("refresh_reasons") or []),
                }
            )
    return flags


def require_unique(items: Iterable[dict[str, Any]], field: str) -> None:
    seen: set[str] = set()
    for item in items:
        item_id = str(item["id"])
        if item_id in seen:
            raise StudyError(f"Duplicate {field} id: {item_id}")
        seen.add(item_id)


def normalize_internal_sources(raw: Any, *, required: bool = True) -> list[dict[str, str]]:
    items = ensure_list(raw, "internal_sources")
    if required and not items:
        raise StudyError(
            "internal_sources must contain concrete repository evidence for the selected study depth"
        )
    normalized: list[dict[str, str]] = []
    for index, item in enumerate(items):
        data = ensure_object(item, f"internal_sources[{index}]")
        kind = ensure_text(data.get("kind"), f"internal_sources[{index}].kind").lower()
        if kind not in VALID_INTERNAL_KINDS:
            raise StudyError(
                f"internal_sources[{index}].kind must be one of "
                + ", ".join(sorted(VALID_INTERNAL_KINDS))
            )
        normalized.append(
            {
                "id": normalize_id(data.get("id"), "I", f"internal_sources[{index}].id"),
                "kind": kind,
                "location": ensure_text(
                    data.get("location"), f"internal_sources[{index}].location", 3
                ),
                "finding": ensure_text(
                    data.get("finding"), f"internal_sources[{index}].finding", 12
                ),
                "planning_impact": ensure_text(
                    data.get("planning_impact"),
                    f"internal_sources[{index}].planning_impact",
                    12,
                ),
            }
        )
    require_unique(normalized, "internal source")
    return normalized


def normalize_complexity_assessment(raw: Any) -> dict[str, Any]:
    data = ensure_object(raw, "complexity_assessment")
    level = ensure_text(data.get("level"), "complexity_assessment.level").lower()
    if level not in VALID_COMPLEXITY_LEVELS:
        raise StudyError(
            "complexity_assessment.level must be simple, medium, or complex"
        )
    signals = ensure_str_list(data.get("signals"), "complexity_assessment.signals")
    if not signals:
        raise StudyError(
            "complexity_assessment.signals must record concrete complexity or simplicity signals"
        )
    return {
        "level": level,
        "rationale": ensure_text(
            data.get("rationale"), "complexity_assessment.rationale", 24
        ),
        "signals": signals,
    }


def normalize_internal_study(raw: Any, complexity_level: str) -> dict[str, str]:
    data = ensure_object(raw, "internal_study")
    selection_source = ensure_text(
        data.get("selection_source"), "internal_study.selection_source"
    ).lower()
    if selection_source not in VALID_INTERNAL_SELECTION_SOURCES:
        raise StudyError(
            "internal_study.selection_source must be automatic or user"
        )
    depth = ensure_text(data.get("depth"), "internal_study.depth").lower()
    if depth not in VALID_INTERNAL_DEPTHS:
        raise StudyError(
            "internal_study.depth must be none, related_packages, workspace_keywords, or full_project"
        )

    if complexity_level == "simple":
        if selection_source != "automatic" or depth != "none":
            raise StudyError(
                "simple requests must use automatic internal study depth none; classify as medium if discovery is needed"
            )
    elif complexity_level == "medium":
        if selection_source != "automatic":
            raise StudyError(
                "medium requests choose internal study automatically without asking the user"
            )
        if depth not in {"related_packages", "workspace_keywords"}:
            raise StudyError(
                "medium requests must use related_packages or workspace_keywords internal study"
            )
    elif complexity_level == "complex":
        if selection_source != "user":
            raise StudyError(
                "complex requests must record the user's fixed-choice internal study selection"
            )
        if depth not in {"related_packages", "workspace_keywords", "full_project"}:
            raise StudyError(
                "complex requests must use one of the three fixed internal study choices"
            )

    return {
        "selection_source": selection_source,
        "depth": depth,
        "rationale": ensure_text(data.get("rationale"), "internal_study.rationale", 24),
        "plan_finding": ensure_text(
            data.get("plan_finding"), "internal_study.plan_finding", 24
        ),
    }


def normalize_external_sources(raw: Any) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(ensure_list(raw, "external_research.sources")):
        data = ensure_object(item, f"external_research.sources[{index}]")
        source_type = ensure_text(
            data.get("source_type"), f"external_research.sources[{index}].source_type"
        ).lower()
        if source_type not in VALID_EXTERNAL_SOURCE_TYPES:
            raise StudyError(
                f"external_research.sources[{index}].source_type must be one of "
                + ", ".join(sorted(VALID_EXTERNAL_SOURCE_TYPES))
            )
        url = ensure_text(data.get("url"), f"external_research.sources[{index}].url")
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise StudyError(
                f"external_research.sources[{index}].url must be an absolute HTTPS URL"
            )
        raw_id = ensure_text(data.get("id"), f"external_research.sources[{index}].id").upper()
        if re.fullmatch(r"E[0-9]{3,}", raw_id) or re.fullmatch(
            r"(?:W-[A-Z0-9_-]{2,}|S[0-9]{3,})", raw_id
        ):
            source_id = raw_id
        else:
            raise StudyError(
                f"external_research.sources[{index}].id must match E001+, S001+, or W-* register id"
            )
        reading_scope = normalize_reading_scope(
            data.get("reading_scope"),
            f"external_research.sources[{index}].reading_scope",
            default="inspected_section",
        )
        evidence_domain = normalize_evidence_domain(
            data.get("evidence_domain"),
            f"external_research.sources[{index}].evidence_domain",
            default="general",
        )
        version_or_date, has_version, affects_cli_behavior = resolve_source_dating(
            data, f"external_research.sources[{index}]", evidence_domain
        )
        default_kind = (
            "verified_source_fact"
            if reading_scope in VERIFIED_READING_SCOPES
            else "proposed_design"
        )
        evidence_kind = normalize_evidence_kind(
            data.get("evidence_kind"),
            f"external_research.sources[{index}].evidence_kind",
            default=default_kind,
        )
        if evidence_kind == "verified_source_fact" and reading_scope in UNVERIFIED_READING_SCOPES:
            raise StudyError(
                f"external_research.sources[{index}] cannot mark a {reading_scope} source as verified_source_fact"
            )
        access_error = str(data.get("access_error") or "").strip()
        if reading_scope == "inaccessible" and not access_error:
            raise StudyError(
                f"external_research.sources[{index}].access_error must record why the source was inaccessible"
            )
        retrieved_at = normalize_optional_iso_date(
            data.get("retrieved_at"),
            f"external_research.sources[{index}].retrieved_at",
        )
        observed_at = normalize_optional_iso_date(
            data.get("observed_at"),
            f"external_research.sources[{index}].observed_at",
        )
        refresh_required = bool(affects_cli_behavior and not has_version)
        refresh_reasons = (
            ["missing_date_or_version_for_cli_behavior"] if refresh_required else []
        )
        entry: dict[str, Any] = {
            "id": source_id,
            "source_type": source_type,
            "title": ensure_text(
                data.get("title"), f"external_research.sources[{index}].title", 3
            ),
            "publisher": ensure_text(
                data.get("publisher"),
                f"external_research.sources[{index}].publisher",
                2,
            ),
            "url": url,
            "version_or_date": version_or_date,
            "finding": ensure_text(
                data.get("finding"),
                f"external_research.sources[{index}].finding",
                12,
            ),
            "planning_impact": ensure_text(
                data.get("planning_impact"),
                f"external_research.sources[{index}].planning_impact",
                12,
            ),
            "why_authoritative": ensure_text(
                data.get("why_authoritative"),
                f"external_research.sources[{index}].why_authoritative",
                12,
            ),
            "reading_scope": reading_scope,
            "counts_as_verified_support": reading_scope in VERIFIED_READING_SCOPES,
            "evidence_domain": evidence_domain,
            "evidence_kind": evidence_kind,
            "affects_cli_behavior": affects_cli_behavior,
            "has_version_or_date": has_version,
            "refresh_required": refresh_required,
            "refresh_reasons": refresh_reasons,
        }
        if retrieved_at:
            entry["retrieved_at"] = retrieved_at
        if observed_at:
            entry["observed_at"] = observed_at
        if access_error:
            entry["access_error"] = access_error
        for optional_str in ("provider", "provider_version", "digest", "source_register_id"):
            val = str(data.get(optional_str) or "").strip()
            if val:
                entry[optional_str] = val.lower() if optional_str == "provider" else val
        if isinstance(data.get("is_blog"), bool):
            entry["is_blog"] = data["is_blog"]
        normalized.append(entry)
    require_unique(normalized, "external source")
    return normalized


def normalize_trigger_assessment(raw: Any) -> dict[str, bool]:
    data = ensure_object(raw, "external_research.trigger_assessment")
    missing = [field for field in TRIGGER_FIELDS if field not in data]
    if missing:
        raise StudyError(
            "external_research.trigger_assessment must explicitly evaluate: "
            + ", ".join(missing)
        )
    unexpected = sorted(set(data) - set(TRIGGER_FIELDS))
    if unexpected:
        raise StudyError(
            "external_research.trigger_assessment contains unknown fields: "
            + ", ".join(unexpected)
        )
    normalized: dict[str, bool] = {}
    for field in TRIGGER_FIELDS:
        value = data[field]
        if not isinstance(value, bool):
            raise StudyError(
                f"external_research.trigger_assessment.{field} must be true or false"
            )
        normalized[field] = value
    return normalized


def normalize_external_research_v1(raw: Any) -> dict[str, Any]:
    data = ensure_object(raw, "external_research")
    decision = ensure_text(data.get("decision"), "external_research.decision").lower()
    if decision not in VALID_EXTERNAL_DECISIONS:
        raise StudyError(
            "external_research.decision must be required, not_needed, or blocked"
        )
    triggers = normalize_trigger_assessment(data.get("trigger_assessment"))
    sources = normalize_external_sources(data.get("sources"))
    triggered = [field for field, value in triggers.items() if value]
    rationale = ensure_text(data.get("rationale"), "external_research.rationale", 24)

    if decision == "not_needed":
        if triggered:
            raise StudyError(
                "external research cannot be not_needed while triggers are true: "
                + ", ".join(triggered)
            )
        if sources:
            raise StudyError(
                "external_research.sources must be empty when decision is not_needed"
            )
    elif decision == "required":
        if not triggered:
            raise StudyError(
                "external research marked required must identify at least one trigger"
            )
        if not sources:
            raise StudyError(
                "external research marked required must include authoritative sources"
            )
    elif decision == "blocked":
        if not triggered:
            raise StudyError(
                "blocked external research must identify at least one trigger"
            )

    return {
        "decision": decision,
        "rationale": rationale,
        "trigger_assessment": triggers,
        "sources": sources,
    }


def normalize_external_research_v2(
    raw: Any,
    complexity_level: str,
    *,
    has_prepared_reports: bool = False,
) -> dict[str, Any]:
    data = ensure_object(raw, "external_research")
    decision = ensure_text(data.get("decision"), "external_research.decision").lower()
    if decision not in VALID_EXTERNAL_DECISIONS:
        raise StudyError(
            "external_research.decision must be required, not_needed, or blocked"
        )
    selection_source = ensure_text(
        data.get("selection_source"), "external_research.selection_source"
    ).lower()
    if selection_source not in VALID_EXTERNAL_SELECTION_SOURCES:
        raise StudyError(
            "external_research.selection_source must be automatic or user"
        )
    depth = ensure_text(data.get("depth"), "external_research.depth").lower()
    if depth not in VALID_EXTERNAL_DEPTHS:
        raise StudyError("external_research.depth must be none, focused, or broad")

    triggers = normalize_trigger_assessment(data.get("trigger_assessment"))
    sources = normalize_external_sources(data.get("sources"))
    triggered = [field for field, value in triggers.items() if value]
    rationale = ensure_text(data.get("rationale"), "external_research.rationale", 24)
    narrowed_from_broad = data.get("narrowed_from_broad", False)
    if not isinstance(narrowed_from_broad, bool):
        raise StudyError("external_research.narrowed_from_broad must be true or false")
    if narrowed_from_broad:
        raise StudyError(
            "user-requested broad external research cannot be silently narrowed"
        )

    if complexity_level == "simple":
        if selection_source != "automatic" or depth != "none":
            raise StudyError(
                "simple requests must skip external study automatically; classify as medium if external verification is material"
            )
        if triggered:
            raise StudyError(
                "simple requests cannot keep external-research triggers true; classify as medium or complex"
            )
    elif complexity_level == "medium":
        if selection_source == "automatic" and depth not in {"none", "focused"}:
            raise StudyError(
                "automatic external study for medium requests may be none or focused only"
            )
        # A prepared report replaces focused research only for triggers it can answer;
        # security-sensitive or conflicting evidence always needs a fresh focused check.
        waiver_excluded = [
            field for field in PREPARED_REPORT_WAIVER_EXCLUDED_TRIGGERS if triggers[field]
        ]
        if (
            selection_source == "automatic"
            and triggered
            and depth == "none"
            and (not has_prepared_reports or waiver_excluded)
        ):
            raise StudyError(
                "medium requests with external triggers must perform focused research"
            )
        if depth == "broad" and selection_source != "user":
            raise StudyError(
                "broad external research for a medium request requires an explicit user choice"
            )
    elif complexity_level == "complex":
        if selection_source != "user":
            raise StudyError(
                "complex requests must record the user's fixed-choice external study selection"
            )

    if depth == "none":
        if decision != "not_needed":
            raise StudyError(
                "external_research.decision must be not_needed when depth is none"
            )
        if sources:
            raise StudyError(
                "external_research.sources must be empty when depth is none"
            )
    else:
        if decision == "not_needed":
            raise StudyError(
                "external research with focused or broad depth cannot be marked not_needed"
            )
        if decision == "required" and not sources:
            raise StudyError(
                "external research marked required must include authoritative sources"
            )
        if decision == "required" and not triggered and selection_source != "user":
            raise StudyError(
                "automatic external research marked required must identify at least one trigger"
            )
        if (
            depth == "broad"
            and decision == "required"
            and len(sources) == 1
            and (
                sources[0]["source_type"] == "authoritative_other"
                or sources[0].get("is_blog") is True
            )
        ):
            raise StudyError(
                "broad external research cannot be silently narrowed to a single blog or non-primary source"
            )

    if decision == "blocked" and not triggered and selection_source != "user":
        raise StudyError(
            "blocked automatic external research must identify at least one trigger"
        )

    return {
        "decision": decision,
        "selection_source": selection_source,
        "depth": depth,
        "rationale": rationale,
        "trigger_assessment": triggers,
        "sources": sources,
        "reading_scope_summary": summarize_reading_scopes(sources),
        "refresh_flags": collect_refresh_flags(sources),
    }


def _validate_claim_and_source_alignment(
    *,
    field: str,
    claim_type: str,
    evidence_domain: str,
    status: str,
    evidence_ids: list[str],
    source_index: dict[str, dict[str, Any]],
    affects_cli_behavior: bool = False,
) -> None:
    external_cited = [
        source_index[eid]
        for eid in evidence_ids
        if eid in source_index and source_index[eid].get("_source_origin") == "external"
    ]
    internal_cited = [
        source_index[eid]
        for eid in evidence_ids
        if eid in source_index and source_index[eid].get("_source_origin") == "internal"
    ]

    if affects_cli_behavior or evidence_domain == "cli_interface":
        for src in external_cited:
            src["affects_cli_behavior"] = True
            if not src.get("has_version_or_date", True):
                src["refresh_required"] = True
                reasons = src.setdefault("refresh_reasons", [])
                if "missing_date_or_version_for_cli_behavior" not in reasons:
                    reasons.append("missing_date_or_version_for_cli_behavior")

    if claim_type == "verified_interface" and status == "resolved":
        has_verified_external = any(
            src.get("reading_scope") in VERIFIED_READING_SCOPES for src in external_cited
        )
        if not internal_cited and not has_verified_external:
            scopes = sorted({str(src.get("reading_scope", "unknown")) for src in external_cited})
            raise StudyError(
                f"{field}: a source with reading_scope {', '.join(scopes) or 'none'} "
                "cannot satisfy a verified_interface claim; inspect the primary section or add a capability probe"
            )

    if status == "resolved" and external_cited and not internal_cited:
        if all(
            src.get("reading_scope") in {"discovery_only", "inaccessible"}
            for src in external_cited
        ):
            raise StudyError(
                f"{field}: inaccessible or discovery_only sources cannot count as verified support"
            )

    if (
        claim_type == "subscription_quota" or evidence_domain == "subscription_quota"
    ) and status in {"resolved", "assumed"}:
        # Only an inspected quota/account source counts; a located or unread quota
        # page next to an api_pricing record is still an api_pricing substitution.
        has_quota_evidence = any(
            src.get("evidence_domain") in {"subscription_quota", "account_capability"}
            and src.get("reading_scope") in VERIFIED_READING_SCOPES
            for src in external_cited
        )
        has_api_pricing_only = any(
            src.get("evidence_domain") == "api_pricing" for src in external_cited
        )
        if has_api_pricing_only and not has_quota_evidence:
            raise StudyError(
                f"{field}: an api_pricing record cannot silently substitute for subscription_quota evidence; "
                "record an unknown or capability probe instead"
            )
        if external_cited and not has_quota_evidence and not internal_cited:
            raise StudyError(
                f"{field}: subscription_quota claims require subscription_quota/account_capability evidence "
                "or status='probe_required'"
            )


def normalize_questions(
    raw: Any,
    known_evidence_ids: set[str],
    *,
    required: bool = True,
    source_index: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    items = ensure_list(raw, "material_questions")
    if required and not items:
        raise StudyError(
            "material_questions must identify the decisions that the study needs to resolve"
        )
    sources_by_id = source_index or {}
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(items):
        data = ensure_object(item, f"material_questions[{index}]")
        importance = ensure_text(
            data.get("importance"), f"material_questions[{index}].importance"
        ).lower()
        status = ensure_text(
            data.get("status"), f"material_questions[{index}].status"
        ).lower()
        if importance not in VALID_IMPORTANCE:
            raise StudyError(
                f"material_questions[{index}].importance must be low, medium, or high"
            )
        if status not in VALID_QUESTION_STATUS:
            raise StudyError(
                f"material_questions[{index}].status must be resolved, assumed, open, or probe_required"
            )
        evidence_ids = [
            ensure_text(value, f"material_questions[{index}].evidence_ids").upper()
            for value in ensure_list(
                data.get("evidence_ids"), f"material_questions[{index}].evidence_ids"
            )
        ]
        unknown = sorted(set(evidence_ids) - known_evidence_ids)
        if unknown:
            raise StudyError(
                f"material_questions[{index}] references unknown evidence ids: "
                + ", ".join(unknown)
            )
        if status in {"resolved", "assumed"} and not evidence_ids:
            raise StudyError(
                f"material_questions[{index}] must cite evidence when resolved or assumed"
            )
        resolution = str(data.get("resolution") or "").strip()
        planning_impact = str(data.get("planning_impact") or "").strip()
        if status in {"resolved", "assumed"}:
            resolution = ensure_text(
                resolution, f"material_questions[{index}].resolution", 12
            )
            planning_impact = ensure_text(
                planning_impact, f"material_questions[{index}].planning_impact", 12
            )
        claim_type = normalize_claim_type(
            data.get("claim_type"), f"material_questions[{index}].claim_type", default=""
        )
        evidence_domain = normalize_evidence_domain(
            data.get("evidence_domain"),
            f"material_questions[{index}].evidence_domain",
            default="general",
        )
        affects_cli = data.get("affects_cli_behavior")
        if affects_cli is None:
            affects_cli_behavior = evidence_domain == "cli_interface"
        elif isinstance(affects_cli, bool):
            affects_cli_behavior = affects_cli or evidence_domain == "cli_interface"
        else:
            raise StudyError(
                f"material_questions[{index}].affects_cli_behavior must be true or false"
            )
        contradictions: list[dict[str, Any]] = []
        for c_idx, raw_conflict in enumerate(
            ensure_list(data.get("contradictions"), f"material_questions[{index}].contradictions")
        ):
            conflict_obj = ensure_object(
                raw_conflict, f"material_questions[{index}].contradictions[{c_idx}]"
            )
            c_sources = [
                ensure_text(
                    s, f"material_questions[{index}].contradictions[{c_idx}].source_ids"
                ).upper()
                for s in ensure_list(
                    conflict_obj.get("source_ids"),
                    f"material_questions[{index}].contradictions[{c_idx}].source_ids",
                )
            ]
            if len(set(c_sources)) < 2:
                raise StudyError(
                    f"material_questions[{index}].contradictions[{c_idx}].source_ids must name at least two distinct sources"
                )
            unknown_conflict = sorted(set(c_sources) - known_evidence_ids)
            if unknown_conflict:
                raise StudyError(
                    f"material_questions[{index}].contradictions[{c_idx}] references unknown sources: "
                    + ", ".join(unknown_conflict)
                )
            contradictions.append(
                {
                    "source_ids": c_sources,
                    "conflict": ensure_text(
                        conflict_obj.get("conflict"),
                        f"material_questions[{index}].contradictions[{c_idx}].conflict",
                        12,
                    ),
                }
            )
        probe_verified = data.get("probe_verified", False)
        if not isinstance(probe_verified, bool):
            raise StudyError(
                f"material_questions[{index}].probe_verified must be true or false"
            )
        if contradictions and status in {"resolved", "assumed"} and not probe_verified:
            raise StudyError(
                f"material_questions[{index}]: contradictory provider documents require status='probe_required' "
                "with a capability_probe, not an invented resolution"
            )
        capability_probe = None
        if data.get("capability_probe") is not None:
            capability_probe = normalize_capability_probe(
                data.get("capability_probe"),
                f"material_questions[{index}].capability_probe",
            )
        if probe_verified:
            # A verified probe is an observation, not a self-declared flag: it needs the
            # probe definition and a cited repository/runtime observation of its result.
            observed = [
                eid
                for eid in evidence_ids
                if sources_by_id.get(eid, {}).get("_source_origin") == "internal"
                or sources_by_id.get(eid, {}).get("evidence_kind") == "observed_repository_behavior"
            ]
            if capability_probe is None or not observed:
                raise StudyError(
                    f"material_questions[{index}].probe_verified requires a capability_probe and at least one "
                    "cited internal or observed_repository_behavior evidence id recording the probe result"
                )
        if status == "probe_required":
            if capability_probe is None:
                raise StudyError(
                    f"material_questions[{index}] with status='probe_required' must define a concrete capability_probe"
                )
            if not planning_impact:
                planning_impact = (
                    f"Run capability probe before relying on contract: {capability_probe['check']}"
                )
        _validate_claim_and_source_alignment(
            field=f"material_questions[{index}]",
            claim_type=claim_type,
            evidence_domain=evidence_domain,
            status=status,
            evidence_ids=evidence_ids,
            source_index=sources_by_id,
            affects_cli_behavior=affects_cli_behavior,
        )
        entry: dict[str, Any] = {
            "id": normalize_id(
                data.get("id"), "Q", f"material_questions[{index}].id"
            ),
            "question": ensure_text(
                data.get("question"), f"material_questions[{index}].question", 8
            ),
            "importance": importance,
            "status": status,
            "resolution": resolution,
            "evidence_ids": evidence_ids,
            "planning_impact": planning_impact,
        }
        if claim_type:
            entry["claim_type"] = claim_type
        if data.get("evidence_domain") is not None:
            entry["evidence_domain"] = evidence_domain
        if affects_cli_behavior:
            entry["affects_cli_behavior"] = True
        if capability_probe is not None:
            entry["capability_probe"] = capability_probe
        if contradictions:
            entry["contradictions"] = contradictions
        if probe_verified:
            entry["probe_verified"] = True
        task_id = str(data.get("task_id") or "").strip()
        if task_id:
            entry["task_id"] = task_id
        normalized.append(entry)
    require_unique(normalized, "material question")
    return normalized


def normalize_synthesis(raw: Any, *, allow_empty_impacts: bool = False) -> dict[str, Any]:
    data = ensure_object(raw, "synthesis")
    normalized: dict[str, Any] = {}
    total_impacts = 0
    for field in SYNTHESIS_FIELDS:
        values = ensure_str_list(data.get(field), f"synthesis.{field}")
        normalized[field] = values
        total_impacts += len(values)
    if total_impacts == 0 and not allow_empty_impacts:
        raise StudyError(
            "synthesis must translate evidence into at least one planning impact"
        )
    normalized["unresolved_questions"] = ensure_str_list(
        data.get("unresolved_questions"), "synthesis.unresolved_questions"
    )
    normalized["stopping_reason"] = ensure_text(
        data.get("stopping_reason"), "synthesis.stopping_reason", 24
    )
    ready = data.get("ready_for_planning")
    if not isinstance(ready, bool):
        raise StudyError("synthesis.ready_for_planning must be true or false")
    normalized["ready_for_planning"] = ready
    return normalized


def normalize_review(raw: Any) -> dict[str, Any]:
    data = ensure_object(raw, "review")
    normalized: dict[str, Any] = {
        "reviewer": ensure_text(data.get("reviewer"), "review.reviewer", 4)
    }
    for field in REVIEW_CHECKS:
        value = data.get(field)
        if not isinstance(value, bool):
            raise StudyError(f"review.{field} must be true or false")
        normalized[field] = value
    notes = ensure_str_list(data.get("notes"), "review.notes")
    if not notes:
        raise StudyError("review.notes must record what the reviewer checked")
    normalized["notes"] = notes
    return normalized


def unresolved_contradiction_ids(questions: Iterable[dict[str, Any]]) -> list[str]:
    """Contradicted questions that neither require a probe nor record a verified one."""
    return [
        q["id"]
        for q in questions
        if q.get("contradictions")
        and q["status"] != "probe_required"
        and not q.get("probe_verified")
    ]


def high_resolved_without_verified_evidence(
    questions: Iterable[dict[str, Any]], unverified_ids: set[str]
) -> list[str]:
    """High-impact resolved questions whose every citation is an unverified reading scope."""
    return [
        q["id"]
        for q in questions
        if q["importance"] == "high"
        and q["status"] == "resolved"
        and q.get("evidence_ids")
        and all(eid in unverified_ids for eid in q["evidence_ids"])
    ]


def validate_ready_state(
    questions: list[dict[str, Any]],
    external_research: dict[str, Any],
    synthesis: dict[str, Any],
    review: dict[str, Any],
    *,
    require_ready: bool,
) -> None:
    ready = synthesis["ready_for_planning"]
    open_questions = [item for item in questions if item["status"] == "open"]
    high_assumptions = [
        item
        for item in questions
        if item["importance"] == "high" and item["status"] == "assumed"
    ]
    sources = external_research.get("sources") or []
    verified_external = [
        item for item in sources if item.get("counts_as_verified_support", True)
    ]
    refresh_flagged_ids = {
        str(item["id"]) for item in sources if item.get("refresh_required")
    }
    if ready:
        if external_research["decision"] == "blocked":
            raise StudyError(
                "synthesis.ready_for_planning cannot be true while external research is blocked"
            )
        if external_research["decision"] == "required" and sources and not verified_external:
            raise StudyError(
                "external research marked required cannot be ready when no source counts as verified support"
            )
        if open_questions:
            raise StudyError(
                "ready study contains open material questions: "
                + ", ".join(item["id"] for item in open_questions)
            )
        if high_assumptions:
            raise StudyError(
                "high-importance questions must be resolved before planning: "
                + ", ".join(item["id"] for item in high_assumptions)
            )
        flagged_resolved = [
            item["id"]
            for item in questions
            if item["status"] == "resolved"
            and any(eid in refresh_flagged_ids for eid in item.get("evidence_ids", []))
        ]
        if flagged_resolved:
            raise StudyError(
                "ready study relies on undated CLI-affecting sources flagged for refresh in questions: "
                + ", ".join(flagged_resolved)
            )
        contradicted = unresolved_contradiction_ids(questions)
        if contradicted:
            raise StudyError(
                "ready study contains contradicted questions without a capability probe: "
                + ", ".join(contradicted)
            )
        unverified_ids = {
            str(item["id"]) for item in sources if not item.get("counts_as_verified_support", True)
        }
        weak = high_resolved_without_verified_evidence(questions, unverified_ids)
        if weak:
            raise StudyError(
                "high-importance questions are resolved without internal or inspected evidence: "
                + ", ".join(weak)
            )
        if synthesis["unresolved_questions"]:
            raise StudyError(
                "ready study must have an empty synthesis.unresolved_questions list"
            )
        failed_checks = [field for field in REVIEW_CHECKS if not review[field]]
        if failed_checks:
            raise StudyError(
                "ready study requires all review checks to pass: "
                + ", ".join(failed_checks)
            )
    else:
        if not synthesis["unresolved_questions"] and external_research["decision"] != "blocked":
            raise StudyError(
                "a not-ready study must record unresolved questions or blocked research"
            )

    if require_ready and not ready:
        raise StudyError(
            "study is valid but not ready for planning; resolve the recorded gaps first"
        )


def _build_source_index(
    internal_sources: list[dict[str, Any]],
    external_sources: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for item in internal_sources:
        copy = dict(item)
        copy["_source_origin"] = "internal"
        index[item["id"]] = copy
    for item in external_sources:
        item["_source_origin"] = "external"
        index[item["id"]] = item
    return index


def _strip_internal_markers(sources: list[dict[str, Any]]) -> None:
    for item in sources:
        item.pop("_source_origin", None)


def normalize_study_v1(data: dict[str, Any], *, require_ready: bool) -> dict[str, Any]:
    internal_sources = normalize_internal_sources(data.get("internal_sources"), required=True)
    external_research = normalize_external_research_v1(data.get("external_research"))
    source_index = _build_source_index(internal_sources, external_research["sources"])
    evidence_ids = set(source_index)
    questions = normalize_questions(
        data.get("material_questions"),
        evidence_ids,
        required=True,
        source_index=source_index,
    )
    _strip_internal_markers(external_research["sources"])
    synthesis = normalize_synthesis(data.get("synthesis"), allow_empty_impacts=False)
    review = normalize_review(data.get("review"))
    validate_ready_state(
        questions,
        external_research,
        synthesis,
        review,
        require_ready=require_ready,
    )
    return {
        "schema_version": 1,
        "request_summary": ensure_text(data.get("request_summary"), "request_summary", 12),
        "material_questions": questions,
        "internal_sources": internal_sources,
        "external_research": external_research,
        "synthesis": synthesis,
        "review": review,
    }


def normalize_study_v2(data: dict[str, Any], *, require_ready: bool) -> dict[str, Any]:
    complexity = normalize_complexity_assessment(data.get("complexity_assessment"))
    internal_study = normalize_internal_study(data.get("internal_study"), complexity["level"])
    internal_required = internal_study["depth"] != "none"
    internal_sources = normalize_internal_sources(
        data.get("internal_sources"), required=internal_required
    )
    if internal_study["depth"] == "none" and internal_sources:
        raise StudyError(
            "internal_sources must be empty when internal_study.depth is none"
        )

    prepared_reports = normalize_prepared_reports(data.get("prepared_reports"))
    failed_access_attempts = normalize_failed_access_attempts(
        data.get("failed_access_attempts")
    )
    unknowns = normalize_unknowns(data.get("unknowns"))
    external_research = normalize_external_research_v2(
        data.get("external_research"),
        complexity["level"],
        has_prepared_reports=any(report["source_ids"] for report in prepared_reports),
    )
    source_index = _build_source_index(internal_sources, external_research["sources"])
    evidence_ids = set(source_index)
    fast_path = (
        complexity["level"] == "simple"
        and internal_study["depth"] == "none"
        and external_research["depth"] == "none"
    )
    questions = normalize_questions(
        data.get("material_questions"),
        evidence_ids,
        required=not fast_path,
        source_index=source_index,
    )
    _strip_internal_markers(external_research["sources"])
    external_research["reading_scope_summary"] = summarize_reading_scopes(
        external_research["sources"], failed_access_attempts
    )
    external_research["refresh_flags"] = collect_refresh_flags(
        external_research["sources"]
    )
    synthesis = normalize_synthesis(
        data.get("synthesis"), allow_empty_impacts=fast_path
    )
    review = normalize_review(data.get("review"))
    validate_ready_state(
        questions,
        external_research,
        synthesis,
        review,
        require_ready=require_ready,
    )

    result: dict[str, Any] = {
        "schema_version": 2,
        "request_summary": ensure_text(data.get("request_summary"), "request_summary", 12),
        "complexity_assessment": complexity,
        "internal_study": internal_study,
        "material_questions": questions,
        "internal_sources": internal_sources,
        "external_research": external_research,
        "synthesis": synthesis,
        "review": review,
    }
    if prepared_reports:
        result["prepared_reports"] = prepared_reports
    if failed_access_attempts:
        result["failed_access_attempts"] = failed_access_attempts
    if unknowns:
        result["unknowns"] = unknowns
    if data.get("evidence_ledger") is not None:
        result["evidence_ledger"] = normalize_evidence_ledger(
            data["evidence_ledger"], require_ready=require_ready
        )
    return result


def validate_completion_claim(
    report: dict[str, Any],
    *,
    claim_implementation_done: bool = False,
    claim_review_done: bool = False,
) -> dict[str, Any]:
    """Prepared research is design input, never proof of implementation or independent review.

    The rule applies whatever ``evidence_origin`` says when the report lives under
    ``prepared-research/``. A receipt must be a separate repository-relative JSON
    path; whether that file exists and is genuine is verified by the delivery gate.
    """
    origin = str(report.get("evidence_origin") or "prepared_research").strip().lower()
    if origin not in VALID_EVIDENCE_ORIGINS:
        raise StudyError(
            "evidence_origin must be one of " + ", ".join(sorted(VALID_EVIDENCE_ORIGINS))
        )
    path = str(report.get("path") or "").strip().replace("\\", "/")
    if PREPARED_RESEARCH_PATH_MARKER in path:
        origin = "prepared_research"
    impl_receipt = str(report.get("implementation_receipt") or "").strip()
    review_receipt = str(report.get("review_receipt") or "").strip()
    impl_status = str(report.get("implementation_status") or "pending").strip().lower()
    review_status = str(report.get("independent_review_status") or "pending").strip().lower()
    if origin == "prepared_research":
        if (claim_implementation_done or impl_status == "completed") and not _receipt_path_ok(
            impl_receipt, path
        ):
            raise StudyError(
                "Prepared research is not proof of implementation completion; "
                "provide verified implementation receipt and runtime test evidence"
            )
        if (claim_review_done or review_status == "completed") and not _receipt_path_ok(
            review_receipt, path
        ):
            raise StudyError(
                "Prepared research is not proof of independent-review completion; "
                "provide a verified fresh-context independent review receipt"
            )
    return {
        "study_input_ready": True,
        "implementation_proven": bool(
            impl_status == "completed" and _receipt_path_ok(impl_receipt, path)
        ),
        "independent_review_proven": bool(
            review_status == "completed" and _receipt_path_ok(review_receipt, path)
        ),
    }


def _receipt_path_ok(receipt: str, report_path: str) -> bool:
    """A receipt is a relative JSON path distinct from, and outside, prepared research."""
    name = receipt.strip().replace("\\", "/")
    if not name or not name.lower().endswith(".json"):
        return False
    if name.startswith("/") or re.match(r"^[A-Za-z]:", name) or ".." in name.split("/"):
        return False
    return PREPARED_RESEARCH_PATH_MARKER not in name and name != report_path


def _ensure_bool(value: Any, field: str, default: bool = False) -> bool:
    if value is None:
        return default
    if not isinstance(value, bool):
        raise StudyError(f"{field} must be true or false")
    return value


def normalize_prepared_report(raw: Any, index: int = 0) -> dict[str, Any]:
    data = ensure_object(raw, f"prepared_reports[{index}]")
    report_id = ensure_text(
        data.get("report_id") or data.get("task_id"),
        f"prepared_reports[{index}].report_id",
        1,
    )
    task_id = ensure_text(
        data.get("task_id") or report_id, f"prepared_reports[{index}].task_id", 1
    )
    path = ensure_text(data.get("path"), f"prepared_reports[{index}].path", 3)
    sha256 = str(data.get("sha256") or "").strip()
    if sha256 and not re.fullmatch(r"[0-9a-fA-F]{64}", sha256):
        raise StudyError(f"prepared_reports[{index}].sha256 must be a 64-char hex digest")
    impl_status = ensure_text(
        data.get("implementation_status", "pending"),
        f"prepared_reports[{index}].implementation_status",
    ).lower()
    review_status = ensure_text(
        data.get("independent_review_status", "pending"),
        f"prepared_reports[{index}].independent_review_status",
    ).lower()
    if impl_status not in VALID_REPORT_STATUSES:
        raise StudyError(
            f"prepared_reports[{index}].implementation_status must be pending, in_progress, or completed"
        )
    if review_status not in VALID_REPORT_STATUSES:
        raise StudyError(
            f"prepared_reports[{index}].independent_review_status must be pending, in_progress, or completed"
        )
    origin = ensure_text(
        data.get("evidence_origin", "prepared_research"),
        f"prepared_reports[{index}].evidence_origin",
    ).lower()
    if origin not in VALID_EVIDENCE_ORIGINS:
        raise StudyError(
            f"prepared_reports[{index}].evidence_origin must be one of "
            + ", ".join(sorted(VALID_EVIDENCE_ORIGINS))
        )
    if PREPARED_RESEARCH_PATH_MARKER in path.replace("\\", "/"):
        origin = "prepared_research"
    revision = data.get("research_revision", 2)
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 1:
        raise StudyError(f"prepared_reports[{index}].research_revision must be a positive integer")
    record: dict[str, Any] = {
        "report_id": report_id,
        "task_id": task_id,
        "path": path,
        "research_revision": revision,
        "source_ids": [
            normalize_source_id(sid, f"prepared_reports[{index}].source_ids")
            for sid in ensure_list(
                data.get("source_ids"), f"prepared_reports[{index}].source_ids"
            )
        ],
        "implementation_status": impl_status,
        "independent_review_status": review_status,
        "evidence_origin": origin,
        "affected_providers": [
            p.lower()
            for p in ensure_str_list(
                data.get("affected_providers"),
                f"prepared_reports[{index}].affected_providers",
            )
        ],
        "affected_components": ensure_str_list(
            data.get("affected_components"),
            f"prepared_reports[{index}].affected_components",
        ),
        "version_sensitive": _ensure_bool(data.get("version_sensitive"), f"prepared_reports[{index}].version_sensitive"),
    }
    if sha256:
        record["sha256"] = sha256.lower()
    for opt in ("implementation_receipt", "review_receipt", "feature_id"):
        val = str(data.get(opt) or "").strip()
        if val:
            record[opt] = val
    validate_completion_claim(record)
    return record


def normalize_prepared_reports(raw: Any) -> list[dict[str, Any]]:
    items = ensure_list(raw, "prepared_reports")
    normalized = [normalize_prepared_report(item, idx) for idx, item in enumerate(items)]
    seen: set[str] = set()
    for item in normalized:
        rid = item["report_id"]
        if rid in seen:
            raise StudyError(f"Duplicate prepared report id: {rid}")
        seen.add(rid)
    return normalized


def normalize_failed_access_attempts(raw: Any) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for idx, item in enumerate(ensure_list(raw, "failed_access_attempts")):
        data = ensure_object(item, f"failed_access_attempts[{idx}]")
        entry: dict[str, Any] = {
            "url": ensure_text(data.get("url"), f"failed_access_attempts[{idx}].url", 4),
            "attempted_at": normalize_optional_iso_date(
                data.get("attempted_at"),
                f"failed_access_attempts[{idx}].attempted_at",
            )
            or "unknown",
            "reason": ensure_text(
                data.get("reason"), f"failed_access_attempts[{idx}].reason", 6
            ),
            "unknown_impact": ensure_text(
                data.get("unknown_impact"),
                f"failed_access_attempts[{idx}].unknown_impact",
                8,
            ),
        }
        source_id = str(data.get("source_id") or "").strip()
        if source_id:
            entry["source_id"] = normalize_source_id(
                source_id, f"failed_access_attempts[{idx}].source_id"
            )
        normalized.append(entry)
    return normalized


def normalize_unknowns(raw: Any) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for idx, item in enumerate(ensure_list(raw, "unknowns")):
        data = ensure_object(item, f"unknowns[{idx}]")
        normalized.append(
            {
                "id": normalize_id(data.get("id"), "U", f"unknowns[{idx}].id"),
                "topic": ensure_text(data.get("topic"), f"unknowns[{idx}].topic", 6),
                "domain": normalize_evidence_domain(
                    data.get("domain"), f"unknowns[{idx}].domain", default="general"
                ),
                "reason": ensure_text(data.get("reason"), f"unknowns[{idx}].reason", 8),
                "conservative_fallback": ensure_text(
                    data.get("conservative_fallback"),
                    f"unknowns[{idx}].conservative_fallback",
                    8,
                ),
            }
        )
    require_unique(normalized, "unknown")
    return normalized


def deduplicate_source_register(raw: Any) -> list[dict[str, Any]]:
    """Deduplicate identical shared external source entries by stable ID; reject conflicts."""
    items = ensure_list(raw, "source_register")
    by_id: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for idx, item in enumerate(items):
        data = ensure_object(item, f"source_register[{idx}]")
        source_id = normalize_source_id(data.get("id"), f"source_register[{idx}].id")
        source_type = ensure_text(
            data.get("source_type", "official_documentation"),
            f"source_register[{idx}].source_type",
        ).lower()
        if source_type not in VALID_EXTERNAL_SOURCE_TYPES:
            raise StudyError(
                f"source_register[{idx}].source_type must be one of "
                + ", ".join(sorted(VALID_EXTERNAL_SOURCE_TYPES))
            )
        url = ensure_text(data.get("url"), f"source_register[{idx}].url")
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise StudyError(
                f"source_register[{idx}].url must be an absolute HTTPS URL"
            )
        summary = ensure_text(data.get("summary"), f"source_register[{idx}].summary", 12)
        if len(summary) > MAX_SOURCE_SUMMARY_CHARS:
            raise StudyError(
                f"source_register[{idx}].summary exceeds {MAX_SOURCE_SUMMARY_CHARS} characters; "
                "store a compact factual note instead of copying an entire article"
            )
        reading_scope = normalize_reading_scope(
            data.get("reading_scope"),
            f"source_register[{idx}].reading_scope",
            default=None,
        )
        evidence_domain = normalize_evidence_domain(
            data.get("evidence_domain"),
            f"source_register[{idx}].evidence_domain",
            default="general",
        )
        version_or_date, has_version, affects_cli_behavior = resolve_source_dating(
            data, f"source_register[{idx}]", evidence_domain
        )
        access_error = str(data.get("access_error") or "").strip()
        if reading_scope == "inaccessible" and not access_error:
            raise StudyError(
                f"source_register[{idx}].access_error must explain why the source was inaccessible"
            )
        retrieved_at = normalize_optional_iso_date(
            data.get("retrieved_at"), f"source_register[{idx}].retrieved_at"
        )
        observed_at = normalize_optional_iso_date(
            data.get("observed_at"), f"source_register[{idx}].observed_at"
        )
        refresh_required = bool(affects_cli_behavior and not has_version)
        refresh_reasons = (
            ["missing_date_or_version_for_cli_behavior"] if refresh_required else []
        )
        normalized_entry: dict[str, Any] = {
            "id": source_id,
            "source_type": source_type,
            "title": ensure_text(data.get("title"), f"source_register[{idx}].title", 3),
            "publisher": ensure_text(
                data.get("publisher"), f"source_register[{idx}].publisher", 2
            ),
            "url": url,
            "version_or_date": version_or_date,
            "has_version_or_date": has_version,
            "retrieved_at": retrieved_at,
            "observed_at": observed_at,
            "reading_scope": reading_scope,
            "counts_as_verified_support": reading_scope in VERIFIED_READING_SCOPES,
            "evidence_domain": evidence_domain,
            "affects_cli_behavior": affects_cli_behavior,
            "provider": str(data.get("provider") or "").strip().lower(),
            "provider_version": str(data.get("provider_version") or "").strip(),
            "digest": str(data.get("digest") or "").strip(),
            "summary": summary,
            "why_authoritative": ensure_text(
                data.get("why_authoritative", "Authoritative external reference."),
                f"source_register[{idx}].why_authoritative",
                8,
            ),
            "refresh_required": refresh_required,
            "refresh_reasons": refresh_reasons,
        }
        if access_error:
            normalized_entry["access_error"] = access_error
        if source_id in by_id:
            if by_id[source_id] != normalized_entry:
                raise StudyError(
                    f"Conflicting duplicate source_register entry for {source_id}"
                )
            continue
        by_id[source_id] = normalized_entry
        order.append(source_id)
    return [by_id[sid] for sid in order]


def normalize_evidence_records(
    raw: Any,
    source_map: dict[str, dict[str, Any]],
    question_ids: set[str],
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for idx, item in enumerate(ensure_list(raw, "evidence_records")):
        data = ensure_object(item, f"evidence_records[{idx}]")
        rec_id = normalize_source_id(data.get("id"), f"evidence_records[{idx}].id")
        task_id = ensure_text(data.get("task_id"), f"evidence_records[{idx}].task_id", 1)
        question_id = normalize_id(
            data.get("material_question_id"),
            "Q",
            f"evidence_records[{idx}].material_question_id",
        )
        if question_id not in question_ids:
            raise StudyError(
                f"evidence_records[{idx}] references unknown material_question_id: {question_id}"
            )
        source_id = normalize_source_id(
            data.get("source_id"), f"evidence_records[{idx}].source_id"
        )
        if source_id not in source_map:
            raise StudyError(
                f"evidence_records[{idx}] references unknown source_id: {source_id}"
            )
        source = source_map[source_id]
        evidence_kind = normalize_evidence_kind(
            data.get("evidence_kind"), f"evidence_records[{idx}].evidence_kind"
        )
        if (
            source.get("_source_origin") == "external"
            and evidence_kind == "verified_source_fact"
            and source.get("reading_scope") in UNVERIFIED_READING_SCOPES
        ):
            raise StudyError(
                f"evidence_records[{idx}] cannot mark {source['reading_scope']} source {source_id} as verified_source_fact"
            )
        evidence_domain = normalize_evidence_domain(
            data.get("evidence_domain"),
            f"evidence_records[{idx}].evidence_domain",
            default=str(source.get("evidence_domain") or "general"),
        )
        claim_type = normalize_claim_type(
            data.get("claim_type"), f"evidence_records[{idx}].claim_type", default=""
        )
        affects_cli = data.get("affects_cli_behavior")
        if affects_cli is None:
            affects_cli_behavior = bool(
                source.get("affects_cli_behavior") or evidence_domain == "cli_interface"
            )
        elif isinstance(affects_cli, bool):
            affects_cli_behavior = affects_cli or evidence_domain == "cli_interface"
        else:
            raise StudyError(
                f"evidence_records[{idx}].affects_cli_behavior must be true or false"
            )
        status = "probe_required" if claim_type == "capability_probe" else "resolved"
        _validate_claim_and_source_alignment(
            field=f"evidence_records[{idx}]",
            claim_type=claim_type,
            evidence_domain=evidence_domain,
            status=status,
            evidence_ids=[source_id],
            source_index=source_map,
            affects_cli_behavior=affects_cli_behavior,
        )
        applicability = ensure_text(
            data.get("repository_applicability"),
            f"evidence_records[{idx}].repository_applicability",
            12,
        )
        if len(applicability) > 400:
            raise StudyError(
                f"evidence_records[{idx}].repository_applicability exceeds 400 characters; keep applicability concise"
            )
        consequence = ensure_text(
            data.get("implementation_consequence"),
            f"evidence_records[{idx}].implementation_consequence",
            12,
        )
        confidence = normalize_confidence(
            data.get("confidence"), f"evidence_records[{idx}].confidence"
        )
        normalized.append(
            {
                "id": rec_id,
                "task_id": task_id,
                "material_question_id": question_id,
                "source_id": source_id,
                "version_or_date": str(
                    data.get("version_or_date") or source.get("version_or_date") or "unknown"
                ).strip(),
                "retrieved_at": str(
                    data.get("retrieved_at") or source.get("retrieved_at") or ""
                ).strip(),
                "observed_at": str(
                    data.get("observed_at") or source.get("observed_at") or ""
                ).strip(),
                "reading_scope": str(source.get("reading_scope") or "inspected_section"),
                "evidence_kind": evidence_kind,
                "evidence_domain": evidence_domain,
                "claim_type": claim_type,
                "repository_applicability": applicability,
                "confidence": confidence,
                "implementation_consequence": consequence,
                "version_sensitive": _ensure_bool(data.get("version_sensitive"), f"evidence_records[{idx}].version_sensitive"),
                "affects_cli_behavior": affects_cli_behavior,
                "provider": str(
                    data.get("provider") or source.get("provider") or ""
                ).strip().lower(),
                "provider_version": str(
                    data.get("provider_version") or source.get("provider_version") or ""
                ).strip(),
            }
        )
    require_unique(normalized, "evidence record")
    return normalized


def normalize_recommendations(
    raw: Any,
    source_map: dict[str, dict[str, Any]],
    question_map: dict[str, dict[str, Any]],
    evidence_record_map: dict[str, dict[str, Any]],
    report_ids: set[str],
) -> list[dict[str, Any]]:
    """Every recommended change must bind to a material question, applicability, and falsification condition."""
    normalized: list[dict[str, Any]] = []
    for idx, item in enumerate(ensure_list(raw, "recommendations")):
        data = ensure_object(item, f"recommendations[{idx}]")
        rec_id = normalize_source_id(data.get("id"), f"recommendations[{idx}].id")
        question_id = normalize_id(
            data.get("material_question_id"),
            "Q",
            f"recommendations[{idx}].material_question_id",
        )
        if question_id not in question_map:
            raise StudyError(
                f"recommendations[{idx}] references unknown material_question_id: {question_id}"
            )
        question = question_map[question_id]
        ev_rec_ids = [
            normalize_source_id(val, f"recommendations[{idx}].evidence_record_ids")
            for val in ensure_list(
                data.get("evidence_record_ids"),
                f"recommendations[{idx}].evidence_record_ids",
            )
        ]
        unknown_ev = sorted(set(ev_rec_ids) - set(evidence_record_map))
        if unknown_ev:
            raise StudyError(
                f"recommendations[{idx}] references unknown evidence_record_ids: "
                + ", ".join(unknown_ev)
            )
        explicit_source_ids = [
            normalize_source_id(val, f"recommendations[{idx}].source_ids")
            for val in ensure_list(
                data.get("source_ids"), f"recommendations[{idx}].source_ids"
            )
        ]
        source_ids = list(dict.fromkeys(
            explicit_source_ids
            + [evidence_record_map[eid]["source_id"] for eid in ev_rec_ids]
        ))
        unknown_sources = sorted(set(source_ids) - set(source_map))
        if unknown_sources:
            raise StudyError(
                f"recommendations[{idx}] references unknown source_ids: "
                + ", ".join(unknown_sources)
            )
        if not source_ids:
            raise StudyError(
                f"recommendations[{idx}] must cite at least one source_id or evidence_record_id"
            )
        evidence_kind = normalize_evidence_kind(
            data.get("evidence_kind", "proposed_design"),
            f"recommendations[{idx}].evidence_kind",
        )
        claim_type = normalize_claim_type(
            data.get("claim_type", "design_recommendation"),
            f"recommendations[{idx}].claim_type",
        )
        evidence_domain = normalize_evidence_domain(
            data.get("evidence_domain"),
            f"recommendations[{idx}].evidence_domain",
            default=str(question.get("evidence_domain") or "general"),
        )
        affects_cli = data.get("affects_cli_behavior")
        if affects_cli is None:
            affects_cli_behavior = bool(
                evidence_domain == "cli_interface"
                or question.get("affects_cli_behavior")
                or any(source_map[sid].get("affects_cli_behavior") for sid in source_ids)
            )
        elif isinstance(affects_cli, bool):
            affects_cli_behavior = affects_cli or evidence_domain == "cli_interface"
        else:
            raise StudyError(
                f"recommendations[{idx}].affects_cli_behavior must be true or false"
            )
        if (
            question.get("contradictions")
            and not question.get("probe_verified")
            and claim_type != "capability_probe"
        ):
            raise StudyError(
                f"recommendations[{idx}] targets contradicted question {question_id} "
                "and must use claim_type='capability_probe' rather than an invented resolution"
            )
        # Guards follow the recommendation's own claim: only a capability_probe may lean
        # on the linked question's probe status; any other claim (verified_interface,
        # subscription_quota, design change) is checked as a resolved claim.
        check_status = "probe_required" if claim_type == "capability_probe" else "resolved"
        _validate_claim_and_source_alignment(
            field=f"recommendations[{idx}]",
            claim_type=claim_type,
            evidence_domain=evidence_domain,
            status=check_status,
            evidence_ids=source_ids,
            source_index=source_map,
            affects_cli_behavior=affects_cli_behavior,
        )
        report_id = str(data.get("report_id") or "").strip()
        if report_id and report_ids and report_id not in report_ids:
            raise StudyError(
                f"recommendations[{idx}] references unknown prepared report_id: {report_id}"
            )
        provider = str(data.get("provider") or "").strip().lower()
        if not provider:
            providers = {
                str(source_map[sid].get("provider") or "").strip().lower()
                for sid in source_ids
                if str(source_map[sid].get("provider") or "").strip()
            }
            if len(providers) == 1:
                provider = next(iter(providers))
        provider_version = str(data.get("provider_version") or "").strip()
        if not provider_version:
            versions = {
                str(source_map[sid].get("provider_version") or "").strip()
                for sid in source_ids
                if str(source_map[sid].get("provider_version") or "").strip()
            }
            if len(versions) == 1:
                provider_version = next(iter(versions))
        normalized.append(
            {
                "id": rec_id,
                "task_id": str(data.get("task_id") or question.get("task_id") or "").strip(),
                "report_id": report_id,
                "material_question_id": question_id,
                "evidence_record_ids": ev_rec_ids,
                "source_ids": source_ids,
                "evidence_kind": evidence_kind,
                "claim_type": claim_type,
                "evidence_domain": evidence_domain,
                "change": ensure_text(
                    data.get("change"), f"recommendations[{idx}].change", 12
                ),
                "repository_applicability": ensure_text(
                    data.get("repository_applicability"),
                    f"recommendations[{idx}].repository_applicability",
                    12,
                ),
                "confidence": normalize_confidence(
                    data.get("confidence", "medium"),
                    f"recommendations[{idx}].confidence",
                ),
                "implementation_consequence": ensure_text(
                    data.get("implementation_consequence"),
                    f"recommendations[{idx}].implementation_consequence",
                    12,
                ),
                "falsification_condition": ensure_text(
                    data.get("falsification_condition"),
                    f"recommendations[{idx}].falsification_condition",
                    12,
                ),
                "version_sensitive": _ensure_bool(data.get("version_sensitive"), f"recommendations[{idx}].version_sensitive"),
                "affects_cli_behavior": affects_cli_behavior,
                "provider": provider,
                "provider_version": provider_version,
                "affected_components": ensure_str_list(
                    data.get("affected_components"),
                    f"recommendations[{idx}].affected_components",
                ),
                "conservative_fallback": str(
                    data.get("conservative_fallback") or ""
                ).strip(),
            }
        )
    require_unique(normalized, "recommendation")
    return normalized


def normalize_invalidation_signal(raw: Any, index: int = 0) -> dict[str, Any]:
    data = ensure_object(raw, f"invalidation_signals[{index}]")
    signal = ensure_text(
        data.get("signal"), f"invalidation_signals[{index}].signal"
    ).lower()
    if signal not in VALID_INVALIDATION_SIGNALS:
        raise StudyError(
            f"invalidation_signals[{index}].signal must be one of "
            + ", ".join(sorted(VALID_INVALIDATION_SIGNALS))
        )
    source_ids = [
        normalize_source_id(val, f"invalidation_signals[{index}].source_ids")
        for val in ensure_list(
            data.get("source_ids"), f"invalidation_signals[{index}].source_ids"
        )
    ]
    single_source = str(data.get("source_id") or "").strip()
    if single_source:
        sid = normalize_source_id(single_source, f"invalidation_signals[{index}].source_id")
        if sid not in source_ids:
            source_ids.append(sid)
    normalized = {
        "signal": signal,
        "provider": str(data.get("provider") or "").strip().lower(),
        "previous_version": str(data.get("previous_version") or "").strip(),
        "current_version": str(data.get("current_version") or "").strip(),
        "source_ids": source_ids,
        "component": str(data.get("component") or "").strip(),
        "material_question_id": str(data.get("material_question_id") or "").strip().upper(),
        "reason": ensure_text(
            data.get("reason"), f"invalidation_signals[{index}].reason", 8
        ),
    }
    targets = SIGNAL_REQUIRED_TARGETS.get(signal)
    if targets and not normalized["component"] and not any(normalized[t] for t in targets):
        raise StudyError(
            f"invalidation_signals[{index}] ({signal}) must name "
            + " or ".join(targets)
            + " (or a component); an untargeted refresh signal cannot be dropped silently"
        )
    return normalized


def resolve_contradiction_requirement(
    question_id: str,
    source_ids: list[str],
    conflict: str,
    *,
    probe_check: str,
    falsification_condition: str,
    conservative_fallback: str,
) -> dict[str, Any]:
    """Produce a deterministic capability-probe requirement for contradictory provider docs."""
    unique_sources = list(dict.fromkeys(normalize_source_id(s, "source_ids") for s in source_ids))
    if len(unique_sources) < 2:
        raise StudyError("Contradiction requires at least two distinct source IDs")
    return {
        "question_id": normalize_id(question_id, "Q", "question_id"),
        "status": "probe_required",
        "invented_resolution_allowed": False,
        "contradictions": [
            {
                "source_ids": unique_sources,
                "conflict": ensure_text(conflict, "conflict", 12),
            }
        ],
        "capability_probe": normalize_capability_probe(
            {
                "check": probe_check,
                "falsification_condition": falsification_condition,
                "conservative_fallback": conservative_fallback,
                "changes_acceptance_silently": False,
            },
            "capability_probe",
        ),
    }


def evaluate_stopping_condition(ledger: dict[str, Any]) -> dict[str, Any]:
    """Stop research by unresolved decision risk, never by source count."""
    blocking: list[str] = []
    probe_requirements: list[dict[str, Any]] = []
    refresh_flags = list(ledger.get("refresh_flags") or [])
    refresh_flagged_ids = {flag["source_id"] for flag in refresh_flags}

    for q in ledger.get("material_questions", []):
        if q["status"] == "open" and q["importance"] == "high":
            blocking.append(f"high-impact open question {q['id']}: {q['question']}")
        elif q["status"] == "assumed" and q["importance"] == "high":
            blocking.append(f"high-impact unverified assumption {q['id']}: {q['question']}")
        elif q["status"] == "probe_required":
            probe_requirements.append(
                {
                    "question_id": q["id"],
                    "question": q["question"],
                    "capability_probe": q["capability_probe"],
                    "contradictions": q.get("contradictions", []),
                }
            )
        if q.get("contradictions") and q["status"] != "probe_required" and not q.get("probe_verified"):
            blocking.append(f"unresolved contradiction on {q['id']}")
        if q["status"] == "resolved" and any(
            eid in refresh_flagged_ids for eid in q.get("evidence_ids", [])
        ):
            blocking.append(
                f"question {q['id']} relies on CLI-affecting source flagged for date/version refresh"
            )

    scope_summary = ledger.get("reading_scope_summary") or {}
    unverified_ids = set(scope_summary.get("unverified_source_ids", []))
    for qid in high_resolved_without_verified_evidence(
        ledger.get("material_questions", []), unverified_ids
    ):
        blocking.append(
            f"high-impact question {qid} is resolved without internal or inspected evidence"
        )
    return {
        "ready": len(blocking) == 0,
        "stopping_basis": "unresolved_decision_risk",
        "source_count_is_proof": False,
        "source_count": len(ledger.get("source_register", [])),
        "verified_source_count": len(scope_summary.get("verified_support_ids", [])),
        "blocking_reasons": blocking,
        "probe_requirements": probe_requirements,
        "refresh_flags": refresh_flags,
    }


def task_applicability_view(
    ledger: dict[str, Any], source_id: str
) -> dict[str, list[dict[str, Any]]]:
    """Return distinct per-task applicability notes referencing one deduplicated source."""
    target = normalize_source_id(source_id, "source_id")
    by_task: dict[str, list[dict[str, Any]]] = {}
    for record in ledger.get("evidence_records", []):
        if record["source_id"] == target:
            by_task.setdefault(record["task_id"], []).append(
                {
                    "record_id": record["id"],
                    "material_question_id": record["material_question_id"],
                    "repository_applicability": record["repository_applicability"],
                    "implementation_consequence": record["implementation_consequence"],
                    "confidence": record["confidence"],
                }
            )
    return by_task


def evaluate_invalidation(
    ledger: dict[str, Any], signals: Iterable[dict[str, Any]]
) -> dict[str, Any]:
    """Selectively invalidate only affected recommendations and reports on explicit signals."""
    normalized_signals = [
        normalize_invalidation_signal(sig, idx) for idx, sig in enumerate(signals)
    ]
    sources_by_id = {s["id"]: s for s in ledger.get("source_register", [])}
    reports_by_id = {r["report_id"]: r for r in ledger.get("prepared_reports", [])}

    invalidated_recs: list[str] = []
    preserved_recs: list[str] = []
    reasons_by_rec: dict[str, list[str]] = {}
    invalidated_sources: set[str] = set()
    invalidated_reports: set[str] = set()
    matched_signal_indexes: set[int] = set()

    for rec in ledger.get("recommendations", []):
        matched_reasons: list[str] = []
        rec_sources = [sources_by_id[sid] for sid in rec["source_ids"] if sid in sources_by_id]
        rec_providers = {
            p
            for p in ([rec.get("provider", "")] + [s.get("provider", "") for s in rec_sources])
            if p
        }
        rec_versions = {
            v
            for v in (
                [rec.get("provider_version", "")]
                + [s.get("provider_version", "") for s in rec_sources]
            )
            if v
        }
        for sig_index, sig in enumerate(normalized_signals):
            kind = sig["signal"]
            matched = False
            if kind == "provider_version_change":
                if sig["provider"] and sig["provider"] in rec_providers:
                    version_match = (
                        rec.get("version_sensitive")
                        or rec.get("affects_cli_behavior")
                        or rec.get("evidence_domain")
                        in {"cli_interface", "model_catalog", "account_capability"}
                        or (
                            sig["previous_version"]
                            and sig["previous_version"] in rec_versions
                        )
                        or (
                            sig["current_version"]
                            and bool(rec_versions)
                            and sig["current_version"] not in rec_versions
                        )
                    )
                    if version_match:
                        matched = True
            elif kind == "cli_version_change":
                provider_ok = not sig["provider"] or sig["provider"] in rec_providers
                if provider_ok and (
                    rec.get("affects_cli_behavior")
                    or rec.get("evidence_domain") == "cli_interface"
                    or rec.get("version_sensitive")
                ):
                    matched = True
            elif kind == "model_contract_change":
                provider_ok = not sig["provider"] or sig["provider"] in rec_providers
                if provider_ok and (
                    rec.get("evidence_domain")
                    in {"model_catalog", "routing", "cli_interface"}
                    or rec.get("version_sensitive")
                ):
                    matched = True
            elif kind == "account_capability_change":
                provider_ok = not sig["provider"] or sig["provider"] in rec_providers
                if provider_ok and (
                    rec.get("evidence_domain")
                    in {"subscription_quota", "account_capability"}
                    or rec.get("version_sensitive")
                ):
                    matched = True
            elif kind == "source_digest_change":
                if set(sig["source_ids"]) & set(rec["source_ids"]):
                    matched = True
            elif kind == "contradicted_evidence":
                if (
                    sig["material_question_id"]
                    and sig["material_question_id"] == rec["material_question_id"]
                ) or (set(sig["source_ids"]) & set(rec["source_ids"])):
                    matched = True
            elif kind == "missing_date_or_version":
                if rec.get("affects_cli_behavior") and any(
                    not s.get("has_version_or_date", True) for s in rec_sources
                ):
                    matched = True
            if sig["component"] and sig["component"] in rec.get("affected_components", []):
                matched = True
            if matched:
                matched_signal_indexes.add(sig_index)
                matched_reasons.append(f"{kind}: {sig['reason']}")
                for sid in rec["source_ids"]:
                    src = sources_by_id.get(sid)
                    if not src:
                        continue
                    if sig["source_ids"]:
                        affected = sid in sig["source_ids"]
                    elif sig["provider"]:
                        affected = src.get("provider") == sig["provider"]
                    else:
                        affected = True
                    if affected:
                        invalidated_sources.add(sid)
        if matched_reasons:
            invalidated_recs.append(rec["id"])
            reasons_by_rec[rec["id"]] = matched_reasons
            if rec.get("report_id"):
                invalidated_reports.add(rec["report_id"])
        else:
            preserved_recs.append(rec["id"])

    # Also match prepared reports that have no recommendations yet if a signal directly names their source_ids
    for report_id, report in reports_by_id.items():
        if report_id in invalidated_reports:
            continue
        has_linked_recs = any(
            rec.get("report_id") == report_id for rec in ledger.get("recommendations", [])
        )
        if has_linked_recs:
            continue
        report_sources = set(report.get("source_ids", []))
        for sig_index, sig in enumerate(normalized_signals):
            shared_sources = set(sig["source_ids"]) & report_sources
            if sig["signal"] in {
                "source_digest_change",
                "contradicted_evidence",
                "missing_date_or_version",
            } and shared_sources:
                matched = True
                invalidated_sources.update(shared_sources)
            elif sig["signal"] in {
                "provider_version_change",
                "cli_version_change",
                "model_contract_change",
                "account_capability_change",
            }:
                matched = bool(
                    sig["provider"]
                    and sig["provider"] in report.get("affected_providers", [])
                    and report.get("version_sensitive")
                )
            else:
                matched = False
            if sig["component"] and sig["component"] in report.get("affected_components", []):
                matched = True
            if matched:
                matched_signal_indexes.add(sig_index)
                invalidated_reports.add(report_id)

    preserved_reports = sorted(set(reports_by_id) - invalidated_reports)
    unmatched = [
        sig for index, sig in enumerate(normalized_signals) if index not in matched_signal_indexes
    ]
    return {
        "signals": normalized_signals,
        "action": "targeted_refresh" if (invalidated_recs or invalidated_reports) else "consume_prepared_reports",
        "requires_broad_research": False,
        "invalidated_recommendation_ids": sorted(invalidated_recs),
        "preserved_recommendation_ids": sorted(preserved_recs),
        "invalidated_report_ids": sorted(invalidated_reports),
        "preserved_report_ids": preserved_reports,
        "invalidated_source_ids": sorted(invalidated_sources),
        "reasons_by_recommendation": reasons_by_rec,
        # Explicit signals that matched nothing are surfaced, never silently dropped.
        "unmatched_signals": unmatched,
    }


def plan_research_action(
    ledger: dict[str, Any], signals: Iterable[dict[str, Any]] | None = None
) -> dict[str, Any]:
    """Decide whether a task consumes prepared reports directly or runs targeted delta refresh."""
    active_signals = list(signals or [])
    for flag in ledger.get("refresh_flags", []):
        active_signals.append(
            {
                "signal": "missing_date_or_version",
                "source_ids": [flag["source_id"]],
                "reason": "CLI-affecting source lacks an explicit date or version.",
            }
        )
    invalidation = evaluate_invalidation(ledger, active_signals)
    return {
        "action": invalidation["action"],
        "requires_broad_research": False,
        "consumed_reports": [
            r["report_id"] for r in ledger.get("prepared_reports", [])
        ],
        "refresh_targets": invalidation["invalidated_recommendation_ids"],
        "invalidated_report_ids": invalidation["invalidated_report_ids"],
        "preserved_report_ids": invalidation["preserved_report_ids"],
        "invalidated_source_ids": invalidation["invalidated_source_ids"],
        "probe_requirements": evaluate_stopping_condition(ledger)["probe_requirements"],
    }


def normalize_evidence_ledger(
    raw: Any, *, require_ready: bool = False
) -> dict[str, Any]:
    data = ensure_object(raw, "evidence_ledger")
    schema_version = data.get("schema_version", EVIDENCE_LEDGER_SCHEMA_VERSION)
    if schema_version != EVIDENCE_LEDGER_SCHEMA_VERSION:
        raise StudyError(
            f"Unsupported evidence_ledger schema_version {schema_version!r}; "
            f"expected {EVIDENCE_LEDGER_SCHEMA_VERSION}"
        )
    ledger_id = ensure_text(
        data.get("ledger_id", "default-evidence-ledger"),
        "evidence_ledger.ledger_id",
        3,
    )
    prepared_reports = normalize_prepared_reports(data.get("prepared_reports"))
    report_ids = {r["report_id"] for r in prepared_reports}
    internal_sources = normalize_internal_sources(
        data.get("internal_sources"), required=False
    )
    source_register = deduplicate_source_register(data.get("source_register"))
    failed_access_attempts = normalize_failed_access_attempts(
        data.get("failed_access_attempts")
    )
    unknowns = normalize_unknowns(data.get("unknowns"))

    source_map: dict[str, dict[str, Any]] = {}
    for item in internal_sources:
        copy = dict(item)
        copy["_source_origin"] = "internal"
        copy["reading_scope"] = "inspected_section"
        copy["counts_as_verified_support"] = True
        source_map[item["id"]] = copy
    for item in source_register:
        item["_source_origin"] = "external"
        source_map[item["id"]] = item

    questions = normalize_questions(
        data.get("material_questions"),
        set(source_map),
        required=False,
        source_index=source_map,
    )
    question_map = {q["id"]: q for q in questions}
    evidence_records = normalize_evidence_records(
        data.get("evidence_records"), source_map, set(question_map)
    )
    evidence_record_map = {r["id"]: r for r in evidence_records}
    recommendations = normalize_recommendations(
        data.get("recommendations"),
        source_map,
        question_map,
        evidence_record_map,
        report_ids,
    )
    _strip_internal_markers(source_register)

    reading_scope_summary = summarize_reading_scopes(
        source_register, failed_access_attempts
    )
    refresh_flags = collect_refresh_flags(source_register)
    signals = [
        normalize_invalidation_signal(sig, idx)
        for idx, sig in enumerate(
            ensure_list(
                data.get("invalidation_signals"),
                "evidence_ledger.invalidation_signals",
            )
        )
    ]

    ledger: dict[str, Any] = {
        "schema_version": EVIDENCE_LEDGER_SCHEMA_VERSION,
        "ledger_id": ledger_id,
        "prepared_reports": prepared_reports,
        "internal_sources": internal_sources,
        "source_register": source_register,
        "failed_access_attempts": failed_access_attempts,
        "unknowns": unknowns,
        "material_questions": questions,
        "evidence_records": evidence_records,
        "recommendations": recommendations,
        "reading_scope_summary": reading_scope_summary,
        "refresh_flags": refresh_flags,
        "invalidation_signals": signals,
    }
    stopping = evaluate_stopping_condition(ledger)
    ledger["stopping_evaluation"] = stopping
    ledger["probe_requirements"] = stopping["probe_requirements"]
    if signals:
        ledger["invalidation_result"] = evaluate_invalidation(ledger, signals)
    if require_ready and not stopping["ready"]:
        raise StudyError(
            "evidence ledger is not ready; unresolved decision risk remains: "
            + "; ".join(stopping["blocking_reasons"])
        )
    return ledger


def render_evidence_ledger(ledger: dict[str, Any]) -> str:
    scopes = ledger["reading_scope_summary"]
    stopping = ledger["stopping_evaluation"]
    lines = [
        f"# Evidence ledger — {ledger['ledger_id']}",
        "",
        f"- Stopping basis: **{stopping['stopping_basis']}** (source count is proof: **no**)",
        f"- Ready: **{'yes' if stopping['ready'] else 'no'}**",
        f"- Reading scopes: inspected_section={len(scopes['inspected_section'])}, "
        f"full_source={len(scopes['full_source'])}, abstract_only={len(scopes['abstract_only'])}, "
        f"discovery_only={len(scopes['discovery_only'])}, inaccessible={len(scopes['inaccessible'])}",
    ]
    if ledger["prepared_reports"]:
        lines.extend(["", "## Prepared reports", ""])
        for report in ledger["prepared_reports"]:
            lines.append(
                f"- **{report['report_id']}** (task `{report['task_id']}`, rev {report['research_revision']}): "
                f"`{report['path']}` — impl={report['implementation_status']}, review={report['independent_review_status']}"
            )
    if ledger["source_register"]:
        lines.extend(["", "## Shared source register", ""])
        for src in ledger["source_register"]:
            flag = " **[REFRESH REQUIRED]**" if src["refresh_required"] else ""
            lines.append(
                f"- **{src['id']}** [{src['reading_scope']}; {src['evidence_domain']}; {src['version_or_date']}]{flag} "
                f"{src['publisher']} - {src['title']}: {src['summary']}"
            )
    if ledger["evidence_records"]:
        lines.extend(["", "## Task evidence records", ""])
        for rec in ledger["evidence_records"]:
            lines.append(
                f"- **{rec['id']}** (task `{rec['task_id']}`, `{rec['material_question_id']}`, source `{rec['source_id']}`, "
                f"{rec['evidence_kind']}, confidence={rec['confidence']}): {rec['repository_applicability']} -> {rec['implementation_consequence']}"
            )
    if ledger["recommendations"]:
        lines.extend(["", "## Recommendations", ""])
        for rec in ledger["recommendations"]:
            lines.append(
                f"- **{rec['id']}** (`{rec['material_question_id']}`, sources={','.join(rec['source_ids'])}): {rec['change']}\n"
                f"  - Applicability: {rec['repository_applicability']}\n"
                f"  - Falsification: {rec['falsification_condition']}"
            )
    if ledger["probe_requirements"]:
        lines.extend(["", "## Capability probe requirements", ""])
        for req in ledger["probe_requirements"]:
            probe = req["capability_probe"]
            lines.append(
                f"- **{req['question_id']}**: check `{probe['check']}` | fallback: {probe['conservative_fallback']}"
            )
    if ledger["refresh_flags"]:
        lines.extend(["", "## Refresh flags", ""])
        for flag in ledger["refresh_flags"]:
            lines.append(
                f"- **{flag['source_id']}** ({flag['signal']}): {', '.join(flag['reasons'])}"
            )
    if ledger["unknowns"]:
        lines.extend(["", "## Explicit unknowns", ""])
        for unk in ledger["unknowns"]:
            lines.append(
                f"- **{unk['id']}** [{unk['domain']}] {unk['topic']} — {unk['reason']} (fallback: {unk['conservative_fallback']})"
            )
    if ledger["failed_access_attempts"]:
        lines.extend(["", "## Failed access attempts", ""])
        for fail in ledger["failed_access_attempts"]:
            lines.append(
                f"- `{fail['url']}` ({fail['attempted_at']}): {fail['reason']} — impact: {fail['unknown_impact']}"
            )
    return "\n".join(lines).rstrip() + "\n"


def normalize_study(raw: Any, *, require_ready: bool = True) -> dict[str, Any]:
    data = ensure_object(raw, "study spec")
    schema_version = data.get("schema_version", 1)
    if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        raise StudyError(
            f"Unsupported study schema_version {schema_version!r}; expected one of {sorted(SUPPORTED_SCHEMA_VERSIONS)}"
        )
    if schema_version == 1:
        return normalize_study_v1(data, require_ready=require_ready)
    return normalize_study_v2(data, require_ready=require_ready)


def read_json(path: Path, field: str) -> Any:
    if path.is_symlink():
        raise StudyError(f"{field} must not be a symbolic link: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise StudyError(f"{field} not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise StudyError(f"Invalid JSON in {path}: {exc}") from exc
    except OSError as exc:
        raise StudyError(f"Cannot read {field} {path}: {exc}") from exc


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False, newline="\n"
    ) as handle:
        handle.write(content)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def canonical_json_bytes(data: Any) -> bytes:
    return (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def markdown_list(items: Iterable[str], empty: str = "- None") -> str:
    values = list(items)
    if not values:
        return empty
    return "\n".join(f"- {value}" for value in values)


def render_study(study: dict[str, Any]) -> str:
    external = study["external_research"]
    true_triggers = [
        field for field, value in external["trigger_assessment"].items() if value
    ]
    questions = []
    for item in study["material_questions"]:
        evidence = ", ".join(item["evidence_ids"]) or "none"
        probe_line = ""
        if item.get("capability_probe"):
            probe = item["capability_probe"]
            probe_line = (
                f"\n  - Capability probe: {probe['check']} "
                f"(fallback: {probe['conservative_fallback']})"
            )
        questions.append(
            f"- **{item['id']}** [{item['importance']}; {item['status']}] "
            f"{item['question']}\n"
            f"  - Resolution: {item['resolution'] or 'Unresolved'}\n"
            f"  - Evidence: {evidence}\n"
            f"  - Planning impact: {item['planning_impact'] or 'Pending'}"
            f"{probe_line}"
        )

    internal = []
    for item in study["internal_sources"]:
        internal.append(
            f"- **{item['id']}** [{item['kind']}] `{item['location']}`\n"
            f"  - Finding: {item['finding']}\n"
            f"  - Planning impact: {item['planning_impact']}"
        )

    external_sources = []
    for item in external["sources"]:
        scope = item.get("reading_scope", "inspected_section")
        refresh_badge = " **[REFRESH REQUIRED]**" if item.get("refresh_required") else ""
        external_sources.append(
            f"- **{item['id']}** [{item['source_type']}; {scope}] "
            f"{item['publisher']} - {item['title']} ({item['version_or_date']}){refresh_badge}\n"
            f"  - URL: {item['url']}\n"
            f"  - Why authoritative: {item['why_authoritative']}\n"
            f"  - Finding: {item['finding']}\n"
            f"  - Planning impact: {item['planning_impact']}"
        )

    extra_sections: list[str] = []
    if study.get("prepared_reports"):
        reports = [
            f"{r['report_id']} (`{r['path']}`, impl={r['implementation_status']}, review={r['independent_review_status']})"
            for r in study["prepared_reports"]
        ]
        extra_sections.append("## Prepared reports\n\n" + markdown_list(reports))
    if study.get("failed_access_attempts"):
        fails = [
            f"`{f['url']}` ({f['attempted_at']}): {f['reason']} — {f['unknown_impact']}"
            for f in study["failed_access_attempts"]
        ]
        extra_sections.append("## Failed access attempts\n\n" + markdown_list(fails))
    if study.get("unknowns"):
        unks = [
            f"**{u['id']}** [{u['domain']}] {u['topic']} — {u['reason']} (fallback: {u['conservative_fallback']})"
            for u in study["unknowns"]
        ]
        extra_sections.append("## Explicit unknowns\n\n" + markdown_list(unks))
    extra_block = ("\n\n" + "\n\n".join(extra_sections) + "\n") if extra_sections else ""

    review = study["review"]
    checks = "\n".join(
        f"- {field.replace('_', ' ')}: **{'pass' if review[field] else 'fail'}**"
        for field in REVIEW_CHECKS
    )
    synthesis = study["synthesis"]

    adaptive = ""
    if study["schema_version"] >= 2:
        complexity = study["complexity_assessment"]
        internal_study = study["internal_study"]
        adaptive = f"""## Adaptive study triage

- Complexity: **{complexity['level']}**
- Complexity rationale: {complexity['rationale']}
- Complexity signals: {', '.join(complexity['signals'])}
- Internal selection source: **{internal_study['selection_source']}**
- Internal depth: **{internal_study['depth']}**
- Internal rationale: {internal_study['rationale']}
- Plan finding: {internal_study['plan_finding']}
- External selection source: **{external['selection_source']}**
- External depth: **{external['depth']}**

"""

    return f"""# Adaptive pre-plan study

## Request summary

{study['request_summary']}

{adaptive}## Material questions

{chr(10).join(questions) if questions else '- None'}

## Internal repository evidence

{chr(10).join(internal) if internal else '- None'}

## External research decision

- Decision: **{external['decision']}**
- Triggered conditions: {', '.join(true_triggers) or 'none'}
- Rationale: {external['rationale']}

## External sources

{chr(10).join(external_sources) if external_sources else '- None'}

## Planning constraints

{markdown_list(synthesis['planning_constraints'])}

## Derived requirements

{markdown_list(synthesis['derived_requirements'])}

## Risks

{markdown_list(synthesis['risks'])}

## Validation implications

{markdown_list(synthesis['validation_implications'])}

## Unresolved questions

{markdown_list(synthesis['unresolved_questions'])}

## Study stopping rule

{synthesis['stopping_reason']}

Ready for planning: **{'yes' if synthesis['ready_for_planning'] else 'no'}**

## Independent study review

- Reviewer: **{review['reviewer']}**
{checks}

### Review notes

{markdown_list(review['notes'])}
{extra_block}"""


def load_plan(plan_arg: str | Path) -> tuple[Path, dict[str, Any]]:
    raw = Path(plan_arg).expanduser()
    plan_dir = raw.parent if raw.name == MANIFEST else raw
    plan_dir = Path(os.path.abspath(os.fspath(plan_dir)))
    if plan_dir.is_symlink():
        raise StudyError("plan directory must not be a symbolic link")
    if not (plan_dir / SENTINEL).is_file() or not (plan_dir / MANIFEST).is_file():
        raise StudyError(f"not a plan-and-execute workspace: {plan_dir}")
    manifest = read_json(plan_dir / MANIFEST, "plan manifest")
    sentinel = read_json(plan_dir / SENTINEL, "plan sentinel")
    if manifest.get("plan_id") != sentinel.get("plan_id"):
        raise StudyError("plan sentinel and manifest do not match")
    return plan_dir, manifest


def find_exact_strings(values: Any) -> set[str]:
    if not isinstance(values, list):
        return set()
    return {str(value).strip() for value in values if isinstance(value, str) and value.strip()}


def verify_plan_integration(study: dict[str, Any], manifest: dict[str, Any]) -> None:
    analysis = manifest.get("request_analysis")
    if not isinstance(analysis, dict):
        raise StudyError("plan manifest has no request_analysis object")

    repository_findings = find_exact_strings(analysis.get("repository_findings"))
    if study["schema_version"] >= 2:
        plan_finding = study["internal_study"]["plan_finding"]
        if plan_finding not in repository_findings:
            raise StudyError(
                "plan request_analysis.repository_findings must copy internal_study.plan_finding exactly"
            )
    missing_internal = [
        item["id"]
        for item in study["internal_sources"]
        if item["finding"] not in repository_findings
    ]
    if missing_internal:
        raise StudyError(
            "plan request_analysis.repository_findings must copy every internal study finding "
            "exactly; missing: "
            + ", ".join(missing_internal)
        )

    research_findings = find_exact_strings(analysis.get("research_findings"))
    missing_external = [
        item["id"]
        for item in study["external_research"]["sources"]
        if item["finding"] not in research_findings
    ]
    if missing_external:
        raise StudyError(
            "plan request_analysis.research_findings must copy every external finding exactly; "
            "missing: "
            + ", ".join(missing_external)
        )

    decision = study["external_research"]["decision"]
    research_decision = str(analysis.get("research_decision") or "").strip()
    if not research_decision:
        raise StudyError("plan request_analysis.research_decision is missing")
    if decision == "not_needed" and research_findings:
        raise StudyError(
            "plan research_findings must be empty when external research was not needed"
        )

    constraints = find_exact_strings(manifest.get("global_constraints"))
    missing_constraints = [
        value
        for value in study["synthesis"]["planning_constraints"]
        if value not in constraints
    ]
    if missing_constraints:
        raise StudyError(
            "plan global_constraints must copy every synthesized planning constraint exactly; "
            "missing: "
            + " | ".join(missing_constraints)
        )

    requirement_texts = {
        str(item.get("text") or "").strip()
        for item in manifest.get("requirements", [])
        if isinstance(item, dict)
    }
    missing_requirements = [
        value
        for value in study["synthesis"]["derived_requirements"]
        if value not in requirement_texts
    ]
    if missing_requirements:
        raise StudyError(
            "plan requirements must copy every synthesized derived requirement exactly; missing: "
            + " | ".join(missing_requirements)
        )

    risks = find_exact_strings(analysis.get("risks"))
    missing_risks = [
        value for value in study["synthesis"]["risks"] if value not in risks
    ]
    if missing_risks:
        raise StudyError(
            "plan request_analysis.risks must copy every synthesized risk exactly; missing: "
            + " | ".join(missing_risks)
        )

    task_text: list[str] = []
    for task in manifest.get("tasks", []):
        if not isinstance(task, dict):
            continue
        for field in ("acceptance_criteria", "implementation_guidance", "validation_commands"):
            values = task.get(field)
            if isinstance(values, list):
                task_text.extend(str(value).strip() for value in values if str(value).strip())
    task_blob = "\n".join(task_text).casefold()
    missing_validation = [
        value
        for value in study["synthesis"]["validation_implications"]
        if value.casefold() not in task_blob
    ]
    if missing_validation:
        raise StudyError(
            "at least one task acceptance criterion, implementation note, or validation command "
            "must contain every synthesized validation implication; missing: "
            + " | ".join(missing_validation)
        )


def attach_study(spec_path: Path, plan_arg: str | Path) -> dict[str, Any]:
    study = normalize_study(read_json(spec_path, "study spec"), require_ready=True)
    plan_dir, manifest = load_plan(plan_arg)
    verify_plan_integration(study, manifest)

    json_bytes = canonical_json_bytes(study)
    digest = hashlib.sha256(json_bytes).hexdigest()
    atomic_write_text(plan_dir / STUDY_JSON, json_bytes.decode("utf-8"))
    atomic_write_text(plan_dir / STUDY_MD, render_study(study))

    metadata = {
        "schema_version": study["schema_version"],
        "json_file": STUDY_JSON,
        "markdown_file": STUDY_MD,
        "sha256": digest,
        "attached_at": now_utc(),
        "ready_for_planning": True,
        "external_research_decision": study["external_research"]["decision"],
        "material_question_count": len(study["material_questions"]),
        "internal_source_count": len(study["internal_sources"]),
        "external_source_count": len(study["external_research"]["sources"]),
    }
    if study["schema_version"] >= 2:
        metadata.update(
            {
                "complexity_level": study["complexity_assessment"]["level"],
                "internal_study_depth": study["internal_study"]["depth"],
                "external_study_depth": study["external_research"]["depth"],
            }
        )
    manifest["study_gate"] = metadata
    events = manifest.setdefault("events", [])
    if isinstance(events, list):
        events.append(
            {
                "at": metadata["attached_at"],
                "type": "adaptive_study_attached",
                "sha256": digest,
            }
        )
    atomic_write_text(plan_dir / MANIFEST, canonical_json_bytes(manifest).decode("utf-8"))
    validate_plan_study(plan_dir)
    return metadata


def validate_plan_study(plan_arg: str | Path) -> dict[str, Any]:
    plan_dir, manifest = load_plan(plan_arg)
    metadata = manifest.get("study_gate")
    if not isinstance(metadata, dict):
        raise StudyError("plan manifest has no attached study_gate metadata")
    metadata_schema = metadata.get("schema_version")
    if metadata_schema not in SUPPORTED_SCHEMA_VERSIONS:
        raise StudyError("plan study_gate schema version is invalid")
    if metadata.get("json_file") != STUDY_JSON or metadata.get("markdown_file") != STUDY_MD:
        raise StudyError("plan study_gate file names are invalid")

    json_path = plan_dir / STUDY_JSON
    markdown_path = plan_dir / STUDY_MD
    if json_path.is_symlink() or markdown_path.is_symlink():
        raise StudyError("study files must not be symbolic links")
    if not json_path.is_file() or not markdown_path.is_file():
        raise StudyError("attached study.json or STUDY.md is missing")

    raw_bytes = json_path.read_bytes()
    digest = hashlib.sha256(raw_bytes).hexdigest()
    if digest != metadata.get("sha256"):
        raise StudyError("study.json hash does not match manifest study_gate.sha256")
    study = normalize_study(json.loads(raw_bytes.decode("utf-8")), require_ready=True)
    if study["schema_version"] != metadata_schema:
        raise StudyError("manifest study_gate schema version is stale")
    expected_markdown = render_study(study)
    if markdown_path.read_text(encoding="utf-8") != expected_markdown:
        raise StudyError("STUDY.md does not match the canonical study.json rendering")
    verify_plan_integration(study, manifest)
    if metadata.get("external_research_decision") != study["external_research"]["decision"]:
        raise StudyError("manifest study_gate external research decision is stale")
    expected_counts = {
        "material_question_count": len(study["material_questions"]),
        "internal_source_count": len(study["internal_sources"]),
        "external_source_count": len(study["external_research"]["sources"]),
    }
    for field, expected in expected_counts.items():
        if metadata.get(field) != expected:
            raise StudyError(f"manifest study_gate {field} is stale")
    if study["schema_version"] >= 2:
        expected_strategy = {
            "complexity_level": study["complexity_assessment"]["level"],
            "internal_study_depth": study["internal_study"]["depth"],
            "external_study_depth": study["external_research"]["depth"],
        }
        for field, expected in expected_strategy.items():
            if metadata.get(field) != expected:
                raise StudyError(f"manifest study_gate {field} is stale")
    if metadata.get("ready_for_planning") is not True:
        raise StudyError("manifest study_gate is not ready for planning")
    return metadata


def print_result(data: Any, as_json: bool) -> None:
    if as_json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    elif isinstance(data, dict):
        for key, value in data.items():
            print(f"{key}: {value}")
    else:
        print(data)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate and attach adaptive pre-plan study evidence."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="Validate a study specification")
    validate.add_argument("--spec", required=True)
    validate.add_argument("--allow-not-ready", action="store_true")
    validate.add_argument("--json", action="store_true")

    render = subparsers.add_parser("render", help="Render a study specification as Markdown")
    render.add_argument("--spec", required=True)
    render.add_argument("--output")
    render.add_argument("--allow-not-ready", action="store_true")

    attach = subparsers.add_parser("attach", help="Attach validated study evidence to a plan")
    attach.add_argument("--spec", required=True)
    attach.add_argument("--plan", required=True)
    attach.add_argument("--json", action="store_true")

    validate_plan = subparsers.add_parser(
        "validate-plan", help="Validate a plan's attached study gate"
    )
    validate_plan.add_argument("--plan", required=True)
    validate_plan.add_argument("--json", action="store_true")

    ledger_validate = subparsers.add_parser(
        "ledger-validate", help="Validate a decision-oriented evidence ledger"
    )
    ledger_validate.add_argument("--ledger", required=True)
    ledger_validate.add_argument("--require-ready", action="store_true")
    ledger_validate.add_argument("--json", action="store_true")

    ledger_render = subparsers.add_parser(
        "ledger-render", help="Render an evidence ledger as Markdown"
    )
    ledger_render.add_argument("--ledger", required=True)
    ledger_render.add_argument("--output")
    ledger_render.add_argument("--require-ready", action="store_true")

    ledger_refresh = subparsers.add_parser(
        "ledger-refresh",
        help="Evaluate selective invalidation for an evidence ledger given explicit signals",
    )
    ledger_refresh.add_argument("--ledger", required=True)
    ledger_refresh.add_argument("--signals", required=True)
    ledger_refresh.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            study = normalize_study(
                read_json(Path(args.spec), "study spec"),
                require_ready=not args.allow_not_ready,
            )
            print_result(
                {
                    "valid": True,
                    "schema_version": study["schema_version"],
                    "ready_for_planning": study["synthesis"]["ready_for_planning"],
                    "complexity_level": study.get("complexity_assessment", {}).get("level", "legacy"),
                    "internal_study_depth": study.get("internal_study", {}).get("depth", "legacy"),
                    "external_study_depth": study["external_research"].get("depth", "legacy"),
                    "external_research_decision": study["external_research"]["decision"],
                    "material_questions": len(study["material_questions"]),
                    "internal_sources": len(study["internal_sources"]),
                    "external_sources": len(study["external_research"]["sources"]),
                },
                args.json,
            )
        elif args.command == "render":
            study = normalize_study(
                read_json(Path(args.spec), "study spec"),
                require_ready=not args.allow_not_ready,
            )
            content = render_study(study)
            if args.output:
                atomic_write_text(Path(args.output), content)
            else:
                print(content, end="")
        elif args.command == "attach":
            metadata = attach_study(Path(args.spec), args.plan)
            print_result(metadata, args.json)
        elif args.command == "validate-plan":
            metadata = validate_plan_study(args.plan)
            print_result({"valid": True, **metadata}, args.json)
        elif args.command == "ledger-validate":
            ledger = normalize_evidence_ledger(
                read_json(Path(args.ledger), "evidence ledger"),
                require_ready=args.require_ready,
            )
            stopping = ledger["stopping_evaluation"]
            print_result(
                {
                    "valid": True,
                    "ledger_id": ledger["ledger_id"],
                    "ready": stopping["ready"],
                    "stopping_basis": stopping["stopping_basis"],
                    "prepared_reports": len(ledger["prepared_reports"]),
                    "source_register_count": len(ledger["source_register"]),
                    "verified_support_count": stopping["verified_source_count"],
                    "recommendation_count": len(ledger["recommendations"]),
                    "probe_requirement_count": len(ledger["probe_requirements"]),
                    "refresh_flag_count": len(ledger["refresh_flags"]),
                },
                args.json,
            )
        elif args.command == "ledger-render":
            ledger = normalize_evidence_ledger(
                read_json(Path(args.ledger), "evidence ledger"),
                require_ready=args.require_ready,
            )
            content = render_evidence_ledger(ledger)
            if args.output:
                atomic_write_text(Path(args.output), content)
            else:
                print(content, end="")
        elif args.command == "ledger-refresh":
            ledger = normalize_evidence_ledger(
                read_json(Path(args.ledger), "evidence ledger"),
                require_ready=False,
            )
            raw_signals = read_json(Path(args.signals), "invalidation signals")
            signal_list = (
                raw_signals.get("signals", [])
                if isinstance(raw_signals, dict)
                else raw_signals
            )
            result = evaluate_invalidation(ledger, signal_list)
            print_result({"valid": True, **result}, args.json)
        else:
            parser.error(f"Unknown command: {args.command}")
    except StudyError as exc:
        if getattr(args, "json", False):
            print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False))
        else:
            print(f"studyctl: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
