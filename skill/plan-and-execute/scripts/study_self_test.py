#!/usr/bin/env python3
"""Self-tests for the adaptive pre-plan study gate."""

from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import studyctl  # noqa: E402


INTERNAL_FINDING = (
    "The repository implements delivery retries in src/delivery.py and validates them in "
    "tests/test_delivery.py."
)
INTERNAL_IMPACT = (
    "Preserve the existing retry boundary and use the focused delivery test command."
)
CONSTRAINT = "Preserve the existing retry boundary."
DERIVED_REQUIREMENT = "Keep failed first attempts retryable."
RISK = "Changing retry state transitions could suppress legitimate retries."
VALIDATION_IMPLICATION = "Run the focused delivery retry tests."


def sample_spec() -> dict:
    return {
        "schema_version": 1,
        "request_summary": "Add idempotent delivery while preserving retry behavior.",
        "material_questions": [
            {
                "id": "Q001",
                "question": "Where is retry behavior defined and tested?",
                "importance": "high",
                "status": "resolved",
                "resolution": (
                    "Retry behavior is defined by the delivery service and its focused tests."
                ),
                "evidence_ids": ["I001"],
                "planning_impact": INTERNAL_IMPACT,
            }
        ],
        "internal_sources": [
            {
                "id": "I001",
                "kind": "implementation",
                "location": "src/delivery.py; tests/test_delivery.py",
                "finding": INTERNAL_FINDING,
                "planning_impact": INTERNAL_IMPACT,
            }
        ],
        "external_research": {
            "decision": "not_needed",
            "rationale": (
                "The requested behavior, compatibility boundary, and test convention are fully "
                "defined by repository code and tests."
            ),
            "trigger_assessment": {
                "user_requested": False,
                "unfamiliar_domain": False,
                "version_sensitive": False,
                "security_sensitive": False,
                "current_behavior": False,
                "repository_gap": False,
                "conflicting_evidence": False,
                "technology_selection": False,
                "high_risk": False,
            },
            "sources": [],
        },
        "synthesis": {
            "planning_constraints": [CONSTRAINT],
            "derived_requirements": [DERIVED_REQUIREMENT],
            "risks": [RISK],
            "validation_implications": [VALIDATION_IMPLICATION],
            "unresolved_questions": [],
            "stopping_reason": (
                "The repository evidence resolves the material question, no trigger requires "
                "external research, and further searching is unlikely to change task boundaries."
            ),
            "ready_for_planning": True,
        },
        "review": {
            "reviewer": "fresh study reviewer",
            "internal_coverage_sufficient": True,
            "external_decision_justified": True,
            "source_quality_sufficient": True,
            "findings_translated_to_plan": True,
            "contradictions_resolved": True,
            "notes": [
                "Confirmed that internal evidence resolves the material question and shapes the plan."
            ],
        },
    }


def external_spec() -> dict:
    spec = sample_spec()
    spec["external_research"]["decision"] = "required"
    spec["external_research"]["rationale"] = (
        "The request depends on a version-sensitive provider contract that is not defined in the "
        "repository."
    )
    spec["external_research"]["trigger_assessment"]["version_sensitive"] = True
    spec["external_research"]["sources"] = [
        {
            "id": "E001",
            "source_type": "official_documentation",
            "title": "Delivery API reference",
            "publisher": "Example Provider",
            "url": "https://example.com/docs/delivery-api",
            "version_or_date": "2026-08-01",
            "finding": "The provider accepts a stable idempotency key on delivery requests.",
            "planning_impact": "Pass the existing message id as the provider idempotency key.",
            "why_authoritative": "This is the provider's versioned official API documentation.",
        }
    ]
    spec["material_questions"][0]["evidence_ids"].append("E001")
    return spec


def sample_manifest() -> dict:
    return {
        "schema_version": 2,
        "plan_id": "study-test",
        "title": "Study gate test",
        "request_analysis": {
            "request_parts": [{"id": "P001", "text": "Add idempotent delivery"}],
            "repository_findings": [INTERNAL_FINDING],
            "research_decision": (
                "No external research is needed because repository evidence is sufficient."
            ),
            "research_findings": [],
            "assumptions": [],
            "risks": [RISK],
            "open_questions": [],
            "decomposition_strategy": "Separate persistence and service integration.",
        },
        "requirements": [
            {
                "id": "R001",
                "text": DERIVED_REQUIREMENT,
                "source": "repository",
                "priority": "must",
                "request_part_ids": ["P001"],
            }
        ],
        "global_constraints": [CONSTRAINT],
        "tasks": [
            {
                "id": "001",
                "acceptance_criteria": [VALIDATION_IMPLICATION],
                "implementation_guidance": [],
                "validation_commands": ["python -m pytest tests/test_delivery.py"],
            }
        ],
        "events": [],
    }


def create_fake_plan(root: Path, manifest: dict | None = None) -> Path:
    plan = root / ".ai-work" / "study-test"
    plan.mkdir(parents=True)
    current = manifest or sample_manifest()
    (plan / studyctl.SENTINEL).write_text(
        json.dumps({"plan_id": current["plan_id"]}) + "\n", encoding="utf-8"
    )
    (plan / studyctl.MANIFEST).write_text(
        json.dumps(current, indent=2) + "\n", encoding="utf-8"
    )
    return plan


def write_spec(path: Path, spec: dict) -> None:
    path.write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")


def assert_rejected(spec: dict, expected: str, *, require_ready: bool = True) -> None:
    try:
        studyctl.normalize_study(spec, require_ready=require_ready)
    except studyctl.StudyError as exc:
        assert expected.lower() in str(exc).lower(), str(exc)
    else:
        raise AssertionError(f"Study should have been rejected with {expected!r}")


def test_ready_internal_only_study() -> None:
    normalized = studyctl.normalize_study(sample_spec())
    assert normalized["synthesis"]["ready_for_planning"] is True
    assert normalized["external_research"]["decision"] == "not_needed"
    markdown = studyctl.render_study(normalized)
    assert "Adaptive pre-plan study" in markdown
    assert "Q001" in markdown and "I001" in markdown


def test_trigger_requires_research() -> None:
    spec = sample_spec()
    spec["external_research"]["trigger_assessment"]["user_requested"] = True
    assert_rejected(spec, "cannot be not_needed")

    spec = external_spec()
    spec["external_research"]["sources"] = []
    assert_rejected(spec, "must include authoritative sources")


def test_high_question_must_be_resolved() -> None:
    spec = sample_spec()
    spec["material_questions"][0]["status"] = "assumed"
    assert_rejected(spec, "must be resolved")


def test_blocked_study_can_be_recorded_but_not_started() -> None:
    spec = sample_spec()
    spec["external_research"]["decision"] = "blocked"
    spec["external_research"]["trigger_assessment"]["repository_gap"] = True
    spec["external_research"]["rationale"] = (
        "A required protocol specification is unavailable, so planning cannot safely continue."
    )
    spec["material_questions"][0]["status"] = "open"
    spec["material_questions"][0]["resolution"] = ""
    spec["material_questions"][0]["planning_impact"] = ""
    spec["material_questions"][0]["evidence_ids"] = []
    spec["synthesis"]["ready_for_planning"] = False
    spec["synthesis"]["unresolved_questions"] = [
        "Which protocol behavior is required by the unavailable specification?"
    ]
    for field in studyctl.REVIEW_CHECKS:
        spec["review"][field] = False
    normalized = studyctl.normalize_study(spec, require_ready=False)
    assert normalized["synthesis"]["ready_for_planning"] is False
    assert_rejected(spec, "not ready for planning")


def test_attach_and_validate_plan() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        spec_path = root / "study-spec.json"
        write_spec(spec_path, sample_spec())
        plan = create_fake_plan(root)
        metadata = studyctl.attach_study(spec_path, plan)
        assert metadata["ready_for_planning"] is True
        assert (plan / studyctl.STUDY_JSON).is_file()
        assert (plan / studyctl.STUDY_MD).is_file()
        validated = studyctl.validate_plan_study(plan)
        assert validated["sha256"] == metadata["sha256"]
        manifest = json.loads((plan / studyctl.MANIFEST).read_text(encoding="utf-8"))
        assert manifest["events"][-1]["type"] == "adaptive_study_attached"

        study_path = plan / studyctl.STUDY_JSON
        study_path.write_text(study_path.read_text(encoding="utf-8") + " ", encoding="utf-8")
        try:
            studyctl.validate_plan_study(plan)
        except studyctl.StudyError as exc:
            assert "hash" in str(exc).lower()
        else:
            raise AssertionError("Tampered study evidence should be rejected")


def test_plan_integration_is_enforced() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        spec_path = root / "study-spec.json"
        write_spec(spec_path, sample_spec())
        manifest = sample_manifest()
        manifest["global_constraints"] = []
        plan = create_fake_plan(root, manifest)
        try:
            studyctl.attach_study(spec_path, plan)
        except studyctl.StudyError as exc:
            assert "global_constraints" in str(exc)
        else:
            raise AssertionError("Missing plan integration should be rejected")


def test_external_source_is_preserved() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        spec = external_spec()
        external_finding = spec["external_research"]["sources"][0]["finding"]
        manifest = sample_manifest()
        manifest["request_analysis"]["research_decision"] = (
            "External research is required because the provider contract is version-sensitive."
        )
        manifest["request_analysis"]["research_findings"] = [external_finding]
        spec_path = root / "study-spec.json"
        write_spec(spec_path, spec)
        plan = create_fake_plan(root, manifest)
        metadata = studyctl.attach_study(spec_path, plan)
        assert metadata["external_source_count"] == 1
        raw = (plan / studyctl.STUDY_JSON).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == metadata["sha256"]


def main() -> int:
    test_ready_internal_only_study()
    test_trigger_requires_research()
    test_high_question_must_be_resolved()
    test_blocked_study_can_be_recorded_but_not_started()
    test_attach_and_validate_plan()
    test_plan_integration_is_enforced()
    test_external_source_is_preserved()
    print("All adaptive study gate self-tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
