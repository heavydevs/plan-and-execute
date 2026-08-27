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



SIMPLE_PLAN_FINDING = (
    "Adaptive internal study was skipped because the request is direct, explicitly scoped, "
    "low-risk, and does not require broader repository discovery."
)
MEDIUM_PLAN_FINDING = (
    "Adaptive internal study used workspace keyword filtering and opened only high-signal "
    "implementation and test files related to the requested behavior."
)
COMPLEX_PLAN_FINDING = (
    "The user selected related-packages internal study for this complex request before "
    "planning began."
)


def v2_simple_spec() -> dict:
    return {
        "schema_version": 2,
        "request_summary": "Rename several explicit labels in known configuration targets.",
        "complexity_assessment": {
            "level": "simple",
            "rationale": (
                "The requested edits are explicit, routine, low-risk, and have no architectural "
                "or compatibility ambiguity even though there are several of them."
            ),
            "signals": [
                "Multiple independent direct edits do not create architectural complexity.",
                "No repository discovery or external contract is needed.",
            ],
        },
        "internal_study": {
            "selection_source": "automatic",
            "depth": "none",
            "rationale": (
                "Reading unrelated repository areas would add token cost without changing the implementation."
            ),
            "plan_finding": SIMPLE_PLAN_FINDING,
        },
        "material_questions": [],
        "internal_sources": [],
        "external_research": {
            "decision": "not_needed",
            "selection_source": "automatic",
            "depth": "none",
            "rationale": (
                "The request does not depend on changing external facts, versions, standards, or providers."
            ),
            "trigger_assessment": {field: False for field in studyctl.TRIGGER_FIELDS},
            "sources": [],
        },
        "synthesis": {
            "planning_constraints": [],
            "derived_requirements": [],
            "risks": [],
            "validation_implications": [],
            "unresolved_questions": [],
            "stopping_reason": (
                "Adaptive triage found no material question whose answer would improve the plan, so study stops before repository inspection."
            ),
            "ready_for_planning": True,
        },
        "review": {
            "reviewer": "adaptive triage self-check",
            **{field: True for field in studyctl.REVIEW_CHECKS},
            "notes": [
                "Confirmed that quantity alone was not treated as complexity and no study evidence is needed."
            ],
        },
    }


def v2_medium_spec() -> dict:
    spec = sample_spec()
    spec["schema_version"] = 2
    spec["complexity_assessment"] = {
        "level": "medium",
        "rationale": (
            "The change is bounded to one behavior but the owning implementation and focused regression tests must be discovered."
        ),
        "signals": [
            "One bounded domain requires code discovery.",
            "No cross-cutting architecture or migration choice is present.",
        ],
    }
    spec["internal_study"] = {
        "selection_source": "automatic",
        "depth": "workspace_keywords",
        "rationale": (
            "Search for retry symbols across the workspace, then open only the highest-signal implementation and test matches."
        ),
        "plan_finding": MEDIUM_PLAN_FINDING,
    }
    spec["external_research"].update(
        {
            "selection_source": "automatic",
            "depth": "none",
        }
    )
    return spec


def v2_complex_spec() -> dict:
    spec = v2_medium_spec()
    spec["complexity_assessment"] = {
        "level": "complex",
        "rationale": (
            "The request crosses multiple ownership boundaries and the user must choose how much repository and external context to spend tokens on."
        ),
        "signals": [
            "Multiple subsystems participate in one compatibility boundary.",
            "Task boundaries may change based on broader repository context.",
        ],
    }
    spec["internal_study"] = {
        "selection_source": "user",
        "depth": "related_packages",
        "rationale": (
            "The user selected the fixed related-packages option instead of a workspace-wide or full-project study."
        ),
        "plan_finding": COMPLEX_PLAN_FINDING,
    }
    spec["external_research"].update(
        {
            "selection_source": "user",
            "depth": "none",
            "decision": "not_needed",
            "rationale": (
                "The user selected the fixed no-external-study option after the request was classified as complex."
            ),
        }
    )
    return spec


def v2_simple_manifest() -> dict:
    manifest = sample_manifest()
    manifest["request_analysis"]["repository_findings"] = [SIMPLE_PLAN_FINDING]
    manifest["request_analysis"]["risks"] = []
    manifest["global_constraints"] = []
    manifest["requirements"] = [
        {
            "id": "R001",
            "text": "Apply the explicitly requested label changes.",
            "source": "user",
            "priority": "must",
            "request_part_ids": ["P001"],
        }
    ]
    manifest["tasks"][0]["acceptance_criteria"] = ["The explicit labels are updated."]
    return manifest


def test_v2_simple_fast_path_skips_study() -> None:
    normalized = studyctl.normalize_study(v2_simple_spec())
    assert normalized["complexity_assessment"]["level"] == "simple"
    assert normalized["internal_study"]["depth"] == "none"
    assert normalized["internal_sources"] == []
    assert normalized["material_questions"] == []
    assert normalized["external_research"]["depth"] == "none"
    assert normalized["synthesis"]["planning_constraints"] == []
    markdown = studyctl.render_study(normalized)
    assert "Adaptive study triage" in markdown
    assert "Internal depth: **none**" in markdown


def test_v2_quantity_does_not_force_deep_study() -> None:
    spec = v2_simple_spec()
    spec["complexity_assessment"]["signals"][0] = (
        "Twenty-five independent direct edits remain simple because none requires discovery or shared architectural reasoning."
    )
    normalized = studyctl.normalize_study(spec)
    assert normalized["complexity_assessment"]["level"] == "simple"
    assert normalized["internal_study"]["depth"] == "none"


def test_v2_medium_uses_automatic_focused_internal_study() -> None:
    normalized = studyctl.normalize_study(v2_medium_spec())
    assert normalized["complexity_assessment"]["level"] == "medium"
    assert normalized["internal_study"]["selection_source"] == "automatic"
    assert normalized["internal_study"]["depth"] == "workspace_keywords"
    assert len(normalized["internal_sources"]) == 1

    bad = v2_medium_spec()
    bad["internal_study"]["depth"] = "full_project"
    assert_rejected(bad, "medium requests must use")


def test_v2_medium_external_trigger_requires_focused_research() -> None:
    spec = v2_medium_spec()
    spec["external_research"]["trigger_assessment"]["version_sensitive"] = True
    assert_rejected(spec, "must perform focused research")

    spec["external_research"]["depth"] = "focused"
    spec["external_research"]["decision"] = "required"
    spec["external_research"]["rationale"] = (
        "The exact provider version changes the supported behavior, so focused official documentation is required."
    )
    spec["external_research"]["sources"] = external_spec()["external_research"]["sources"]
    spec["material_questions"][0]["evidence_ids"].append("E001")
    normalized = studyctl.normalize_study(spec)
    assert normalized["external_research"]["depth"] == "focused"


def test_v2_complex_requires_both_user_choices() -> None:
    spec = v2_complex_spec()
    normalized = studyctl.normalize_study(spec)
    assert normalized["internal_study"]["selection_source"] == "user"
    assert normalized["external_research"]["selection_source"] == "user"

    bad = v2_complex_spec()
    bad["internal_study"]["selection_source"] = "automatic"
    assert_rejected(bad, "complex requests must record the user's fixed-choice internal")

    bad = v2_complex_spec()
    bad["external_research"]["selection_source"] = "automatic"
    assert_rejected(bad, "complex requests must record the user's fixed-choice external")


def test_v2_simple_attach_preserves_skip_decision() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        spec_path = root / "study-spec.json"
        write_spec(spec_path, v2_simple_spec())
        plan = create_fake_plan(root, v2_simple_manifest())
        metadata = studyctl.attach_study(spec_path, plan)
        assert metadata["schema_version"] == 2
        assert metadata["complexity_level"] == "simple"
        assert metadata["internal_study_depth"] == "none"
        assert metadata["external_study_depth"] == "none"
        studyctl.validate_plan_study(plan)

        manifest = json.loads((plan / studyctl.MANIFEST).read_text(encoding="utf-8"))
        manifest["request_analysis"]["repository_findings"] = []
        (plan / studyctl.MANIFEST).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        try:
            studyctl.validate_plan_study(plan)
        except studyctl.StudyError as exc:
            assert "plan_finding" in str(exc)
        else:
            raise AssertionError("Missing adaptive skip finding should be rejected")

def main() -> int:
    test_ready_internal_only_study()
    test_trigger_requires_research()
    test_high_question_must_be_resolved()
    test_blocked_study_can_be_recorded_but_not_started()
    test_attach_and_validate_plan()
    test_plan_integration_is_enforced()
    test_external_source_is_preserved()
    test_v2_simple_fast_path_skips_study()
    test_v2_quantity_does_not_force_deep_study()
    test_v2_medium_uses_automatic_focused_internal_study()
    test_v2_medium_external_trigger_requires_focused_research()
    test_v2_complex_requires_both_user_choices()
    test_v2_simple_attach_preserves_skip_decision()
    print("All adaptive study gate self-tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
