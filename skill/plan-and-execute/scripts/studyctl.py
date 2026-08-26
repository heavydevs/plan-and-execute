#!/usr/bin/env python3
"""Validate and preserve adaptive pre-plan study evidence.

The study gate is intentionally independent from planctl.py so existing plan
schema versions remain compatible. A study is validated before requirements
and TODOs are drafted, then attached to a created plan to prove that its
findings were translated into constraints, requirements, risks, and task
validation.
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

SCHEMA_VERSION = 1
STUDY_JSON = "study.json"
STUDY_MD = "STUDY.md"
MANIFEST = "manifest.json"
SENTINEL = ".orchestrator-plan"

VALID_IMPORTANCE = {"low", "medium", "high"}
VALID_QUESTION_STATUS = {"resolved", "assumed", "open"}
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


def require_unique(items: Iterable[dict[str, Any]], field: str) -> None:
    seen: set[str] = set()
    for item in items:
        item_id = str(item["id"])
        if item_id in seen:
            raise StudyError(f"Duplicate {field} id: {item_id}")
        seen.add(item_id)


def normalize_internal_sources(raw: Any) -> list[dict[str, str]]:
    items = ensure_list(raw, "internal_sources")
    if not items:
        raise StudyError(
            "internal_sources must contain concrete repository evidence before planning"
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


def normalize_external_sources(raw: Any) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
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
        normalized.append(
            {
                "id": normalize_id(
                    data.get("id"), "E", f"external_research.sources[{index}].id"
                ),
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
                "version_or_date": ensure_text(
                    data.get("version_or_date"),
                    f"external_research.sources[{index}].version_or_date",
                    3,
                ),
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
            }
        )
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


def normalize_external_research(raw: Any) -> dict[str, Any]:
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


def normalize_questions(raw: Any, known_evidence_ids: set[str]) -> list[dict[str, Any]]:
    items = ensure_list(raw, "material_questions")
    if not items:
        raise StudyError(
            "material_questions must identify the decisions that the study needs to resolve"
        )
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
                f"material_questions[{index}].status must be resolved, assumed, or open"
            )
        evidence_ids = [
            ensure_text(value, f"material_questions[{index}].evidence_ids")
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
        normalized.append(
            {
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
        )
    require_unique(normalized, "material question")
    return normalized


def normalize_synthesis(raw: Any) -> dict[str, Any]:
    data = ensure_object(raw, "synthesis")
    normalized: dict[str, Any] = {}
    total_impacts = 0
    for field in SYNTHESIS_FIELDS:
        values = ensure_str_list(data.get(field), f"synthesis.{field}")
        normalized[field] = values
        total_impacts += len(values)
    if total_impacts == 0:
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


def normalize_study(raw: Any, *, require_ready: bool = True) -> dict[str, Any]:
    data = ensure_object(raw, "study spec")
    schema_version = data.get("schema_version", SCHEMA_VERSION)
    if schema_version != SCHEMA_VERSION:
        raise StudyError(
            f"Unsupported study schema_version {schema_version!r}; expected {SCHEMA_VERSION}"
        )

    internal_sources = normalize_internal_sources(data.get("internal_sources"))
    external_research = normalize_external_research(data.get("external_research"))
    evidence_ids = {item["id"] for item in internal_sources}
    evidence_ids.update(item["id"] for item in external_research["sources"])
    questions = normalize_questions(data.get("material_questions"), evidence_ids)
    synthesis = normalize_synthesis(data.get("synthesis"))
    review = normalize_review(data.get("review"))

    ready = synthesis["ready_for_planning"]
    open_questions = [item for item in questions if item["status"] == "open"]
    high_assumptions = [
        item
        for item in questions
        if item["importance"] == "high" and item["status"] == "assumed"
    ]
    if ready:
        if external_research["decision"] == "blocked":
            raise StudyError(
                "synthesis.ready_for_planning cannot be true while external research is blocked"
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

    return {
        "schema_version": SCHEMA_VERSION,
        "request_summary": ensure_text(
            data.get("request_summary"), "request_summary", 12
        ),
        "material_questions": questions,
        "internal_sources": internal_sources,
        "external_research": external_research,
        "synthesis": synthesis,
        "review": review,
    }


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
        questions.append(
            f"- **{item['id']}** [{item['importance']}; {item['status']}] "
            f"{item['question']}\n"
            f"  - Resolution: {item['resolution'] or 'Unresolved'}\n"
            f"  - Evidence: {evidence}\n"
            f"  - Planning impact: {item['planning_impact'] or 'Pending'}"
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
        external_sources.append(
            f"- **{item['id']}** [{item['source_type']}] "
            f"{item['publisher']} - {item['title']} ({item['version_or_date']})\n"
            f"  - URL: {item['url']}\n"
            f"  - Why authoritative: {item['why_authoritative']}\n"
            f"  - Finding: {item['finding']}\n"
            f"  - Planning impact: {item['planning_impact']}"
        )

    review = study["review"]
    checks = "\n".join(
        f"- {field.replace('_', ' ')}: **{'pass' if review[field] else 'fail'}**"
        for field in REVIEW_CHECKS
    )
    synthesis = study["synthesis"]
    return f"""# Adaptive pre-plan study

## Request summary

{study['request_summary']}

## Material questions

{chr(10).join(questions)}

## Internal repository evidence

{chr(10).join(internal)}

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
"""


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
        "schema_version": SCHEMA_VERSION,
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
    if metadata.get("schema_version") != SCHEMA_VERSION:
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
                    "ready_for_planning": study["synthesis"]["ready_for_planning"],
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
