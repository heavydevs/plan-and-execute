#!/usr/bin/env python3
"""Acceptance and counterexample regression tests for Task 010 adaptive study ledger."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = REPO_ROOT / "skill" / "plan-and-execute" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import studyctl  # noqa: E402


def base_ledger() -> dict:
    return {
        "schema_version": 1,
        "ledger_id": "adaptive-study-010-test",
        "prepared_reports": [
            {
                "report_id": "010",
                "task_id": "010",
                "path": "docs/research/20261028-skill-optimization/prepared-research/010-adaptive-study.md",
                "research_revision": 2,
                "source_ids": ["W-COST", "W-CONTEXT", "W-BOOK"],
                "implementation_status": "pending",
                "independent_review_status": "pending",
                "affected_providers": [],
                "affected_components": ["studyctl.py"],
                "version_sensitive": False,
            },
            {
                "report_id": "022",
                "task_id": "022",
                "path": "docs/research/20261028-skill-optimization/prepared-research/022-provider-chains.md",
                "research_revision": 2,
                "source_ids": ["W-COST"],
                "implementation_status": "pending",
                "independent_review_status": "pending",
                "affected_providers": ["claude"],
                "affected_components": ["availability.py"],
                "version_sensitive": True,
            },
        ],
        "source_register": [
            {
                "id": "W-COST",
                "source_type": "official_documentation",
                "title": "Optimizing for cost and intelligence",
                "publisher": "Anthropic",
                "url": "https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence",
                "version_or_date": "2026-10-28",
                "retrieved_at": "2026-10-28",
                "observed_at": "2026-10-28",
                "reading_scope": "inspected_section",
                "evidence_domain": "api_pricing",
                "affects_cli_behavior": False,
                "provider": "claude",
                "provider_version": "2026-10",
                "summary": "Cost/context/delegation sections inspected; vendor-specific API token observations, not local subscription measurements.",
                "why_authoritative": "Official vendor documentation with methodology footnotes.",
            },
            {
                "id": "W-CONTEXT",
                "source_type": "official_documentation",
                "title": "Effective context engineering for AI agents",
                "publisher": "Anthropic",
                "url": "https://www.anthropic.com/research/effective-context-engineering-for-ai-agents",
                "version_or_date": "2026-10-28",
                "retrieved_at": "2026-10-28",
                "observed_at": "2026-10-28",
                "reading_scope": "inspected_section",
                "evidence_domain": "architecture",
                "affects_cli_behavior": False,
                "summary": "Primary sections inspected on bounded retrieval and context compaction.",
                "why_authoritative": "Primary engineering guidance from Anthropic research.",
            },
            {
                "id": "W-BOOK",
                "source_type": "authoritative_other",
                "title": "AI Engineering supporting resources",
                "publisher": "Chip Huyen",
                "url": "https://github.com/chiphuyen/aie-book",
                "version_or_date": "2026-10-28",
                "retrieved_at": "2026-10-28",
                "reading_scope": "abstract_only",
                "evidence_domain": "general",
                "affects_cli_behavior": False,
                "summary": "Author-maintained public index and excerpts inspected; full paid book not read.",
                "why_authoritative": "Author-maintained repository index for AI Engineering.",
            },
        ],
        "failed_access_attempts": [
            {
                "source_id": "W-BOOK-FULL",
                "url": "https://example.invalid/paid-ai-engineering-book",
                "attempted_at": "2026-10-28",
                "reason": "Commercial paid book unavailable in public session.",
                "unknown_impact": "Full chapter case studies remain uninspected.",
            }
        ],
        "unknowns": [
            {
                "id": "U001",
                "topic": "Live subscription quota reset windows for Codex and Claude CLI accounts",
                "domain": "subscription_quota",
                "reason": "No authenticated live account probe executed in research revision 2.",
                "conservative_fallback": "Keep subscription quota unknown rather than estimating from API pricing.",
            }
        ],
        "material_questions": [
            {
                "id": "Q001",
                "task_id": "010",
                "question": "How should adaptive study separate reading scopes and refresh evidence?",
                "importance": "high",
                "status": "resolved",
                "claim_type": "design_recommendation",
                "evidence_domain": "architecture",
                "evidence_ids": ["W-CONTEXT", "W-COST"],
                "resolution": "Track discovery-only, abstract-only, inspected-section, and inaccessible scopes separately and refresh only on explicit invalidation signals.",
                "planning_impact": "Implement structured evidence ledger and selective invalidation in studyctl.py.",
            },
            {
                "id": "Q002",
                "task_id": "022",
                "question": "Does API token pricing predict CLI subscription quota behavior?",
                "importance": "high",
                "status": "probe_required",
                "claim_type": "subscription_quota",
                "evidence_domain": "subscription_quota",
                "evidence_ids": ["W-COST"],
                "resolution": "",
                "planning_impact": "Keep subscription quota as unknown and verify with runtime account probe.",
                "capability_probe": {
                    "check": "Observe actual CLI rate-limit headers or cooldown errors on the target account.",
                    "falsification_condition": "Account returns quota exhaustion before API-equivalent token estimate.",
                    "conservative_fallback": "Treat subscription quota as unknown and fail over on observed rate limits.",
                    "changes_acceptance_silently": False,
                },
            },
        ],
        "evidence_records": [
            {
                "id": "EV001",
                "task_id": "010",
                "material_question_id": "Q001",
                "source_id": "W-COST",
                "evidence_kind": "verified_source_fact",
                "evidence_domain": "api_pricing",
                "claim_type": "api_pricing",
                "repository_applicability": "For task 010, W-COST motivates keeping cost comparisons in native units and avoiding unmeasured savings claims.",
                "confidence": "medium",
                "implementation_consequence": "Record vendor benchmarks as bounded evidence, not repository-measured savings.",
                "version_sensitive": False,
            },
            {
                "id": "EV002",
                "task_id": "022",
                "material_question_id": "Q002",
                "source_id": "W-COST",
                "evidence_kind": "verified_source_fact",
                "evidence_domain": "api_pricing",
                "claim_type": "api_pricing",
                "repository_applicability": "For task 022, W-COST covers API pricing only and does NOT measure subscription CLI quota windows.",
                "confidence": "low",
                "implementation_consequence": "Do not infer Codex/Claude subscription cooldown thresholds from API pricing tables.",
                "version_sensitive": True,
            },
        ],
        "recommendations": [
            {
                "id": "REC001",
                "task_id": "010",
                "report_id": "010",
                "material_question_id": "Q001",
                "evidence_record_ids": ["EV001"],
                "source_ids": ["W-CONTEXT", "W-COST"],
                "evidence_kind": "proposed_design",
                "claim_type": "design_recommendation",
                "evidence_domain": "architecture",
                "change": "Add decision-oriented evidence ledger with separate reading scopes and selective invalidation.",
                "repository_applicability": "Applies directly to skill/plan-and-execute/scripts/studyctl.py and ADAPTIVE_STUDY.md.",
                "confidence": "high",
                "implementation_consequence": "Enforce scope separation, domain guards, and signal-driven refresh in studyctl.py.",
                "falsification_condition": "Fails if a located-only source passes verified_interface or an undated CLI source is unflagged.",
                "version_sensitive": False,
                "affects_cli_behavior": False,
                "affected_components": ["studyctl.py"],
            }
        ],
    }


def assert_raises_study_error(fn, expected_substring: str) -> None:
    try:
        fn()
    except studyctl.StudyError as exc:
        assert expected_substring.lower() in str(exc).lower(), (
            f"Expected {expected_substring!r} in StudyError, got: {exc}"
        )
    else:
        raise AssertionError(f"Expected StudyError containing {expected_substring!r}")


def test_ac01_undated_cli_source_flagged_for_refresh() -> None:
    """AC01: A source with no date/version is flagged for refresh when it affects CLI behavior."""
    ledger = base_ledger()
    ledger["source_register"].append(
        {
            "id": "S-CLI-UNDATED",
            "source_type": "official_documentation",
            "title": "Provider CLI flags overview",
            "publisher": "Example CLI",
            "url": "https://example.com/docs/cli-flags",
            "version_or_date": "",
            "reading_scope": "inspected_section",
            "evidence_domain": "cli_interface",
            "affects_cli_behavior": True,
            "provider": "codex",
            "summary": "Describes --output-schema CLI behavior without stating CLI version or publication date.",
            "why_authoritative": "Official provider CLI guide.",
        }
    )
    ledger["material_questions"].append(
        {
            "id": "Q003",
            "task_id": "032",
            "question": "Does the installed CLI accept --output-schema on Windows?",
            "importance": "high",
            "status": "resolved",
            "claim_type": "verified_interface",
            "evidence_domain": "cli_interface",
            "affects_cli_behavior": True,
            "evidence_ids": ["S-CLI-UNDATED"],
            "resolution": "Undated guide states --output-schema is accepted on CLI invocations.",
            "planning_impact": "Pass --output-schema directly in runner invocations.",
        }
    )
    normalized = studyctl.normalize_evidence_ledger(ledger, require_ready=False)
    flagged = {f["source_id"]: f for f in normalized["refresh_flags"]}
    assert "S-CLI-UNDATED" in flagged, normalized["refresh_flags"]
    assert flagged["S-CLI-UNDATED"]["affects_cli_behavior"] is True
    assert "missing_date_or_version_for_cli_behavior" in flagged["S-CLI-UNDATED"]["reasons"]
    # Stopping condition blocks readiness until refreshed because Q003 relies on the flagged CLI source
    assert normalized["stopping_evaluation"]["ready"] is False
    assert_raises_study_error(
        lambda: studyctl.normalize_evidence_ledger(ledger, require_ready=True),
        "refresh",
    )

    # Positive control: dated/versioned CLI source is NOT flagged
    dated_ledger = copy.deepcopy(ledger)
    dated_ledger["source_register"][-1]["version_or_date"] = "codex-cli 0.42.0 (2026-10-28)"
    dated_norm = studyctl.normalize_evidence_ledger(dated_ledger, require_ready=True)
    assert dated_norm["refresh_flags"] == []
    assert dated_norm["stopping_evaluation"]["ready"] is True

    # Negative control: undated conceptual source that does NOT affect CLI behavior is NOT flagged
    non_cli = base_ledger()
    non_cli["source_register"].append(
        {
            "id": "S-CONCEPT-UNDATED",
            "source_type": "authoritative_other",
            "title": "Conceptual decomposition essay",
            "publisher": "Engineering Notes",
            "url": "https://example.com/essays/decomposition",
            "version_or_date": "undated",
            "reading_scope": "inspected_section",
            "evidence_domain": "architecture",
            "affects_cli_behavior": False,
            "summary": "General decomposition heuristics unrelated to CLI flags or versions.",
            "why_authoritative": "Authoritative engineering essay.",
        }
    )
    non_cli_norm = studyctl.normalize_evidence_ledger(non_cli, require_ready=True)
    assert non_cli_norm["refresh_flags"] == []


def test_ac02_shared_source_distinct_task_applicability_without_article_copy() -> None:
    """AC02: Two tasks sharing the same source retain different applicability notes without copying an entire article."""
    ledger = base_ledger()
    # Add an identical duplicate of W-COST to confirm stable-ID deduplication
    ledger["source_register"].append(copy.deepcopy(ledger["source_register"][0]))
    normalized = studyctl.normalize_evidence_ledger(ledger, require_ready=True)
    w_cost_entries = [s for s in normalized["source_register"] if s["id"] == "W-COST"]
    assert len(w_cost_entries) == 1, "Shared source must be deduplicated by stable ID"

    view = studyctl.task_applicability_view(normalized, "W-COST")
    assert set(view.keys()) == {"010", "022"}
    note_010 = view["010"][0]["repository_applicability"]
    note_022 = view["022"][0]["repository_applicability"]
    assert note_010 != note_022
    assert "native units" in note_010
    assert "subscription CLI quota" in note_022

    # Counterexample: pasting an entire article (> MAX_SOURCE_SUMMARY_CHARS) is rejected
    pasted = base_ledger()
    pasted["source_register"][0]["summary"] = "Full copied article paragraph. " * 40
    assert_raises_study_error(
        lambda: studyctl.normalize_evidence_ledger(pasted),
        "copying an entire article",
    )

    # Counterexample: conflicting duplicate definitions for the same stable source ID are rejected
    conflicting = base_ledger()
    dup = copy.deepcopy(conflicting["source_register"][0])
    dup["version_or_date"] = "2025-01-01"
    conflicting["source_register"].append(dup)
    assert_raises_study_error(
        lambda: studyctl.normalize_evidence_ledger(conflicting),
        "conflicting duplicate",
    )


def test_ac03_contradictory_provider_doc_yields_probe_not_invented_resolution() -> None:
    """AC03: A contradictory provider document yields a probe requirement, not an invented resolution."""
    ledger = base_ledger()
    ledger["source_register"].extend(
        [
            {
                "id": "E-CLI-DOC-A",
                "source_type": "official_documentation",
                "title": "Provider CLI flags reference",
                "publisher": "Provider X",
                "url": "https://provider-x.example/docs/cli-flags",
                "version_or_date": "2026-10-20",
                "reading_scope": "inspected_section",
                "evidence_domain": "cli_interface",
                "affects_cli_behavior": True,
                "provider": "codex",
                "provider_version": "0.10.0",
                "summary": "Reference states --json-schema accepts a file path argument.",
                "why_authoritative": "Official CLI reference.",
            },
            {
                "id": "E-CLI-DOC-B",
                "source_type": "official_documentation",
                "title": "Provider CLI changelog",
                "publisher": "Provider X",
                "url": "https://provider-x.example/docs/changelog",
                "version_or_date": "2026-10-26",
                "reading_scope": "inspected_section",
                "evidence_domain": "cli_interface",
                "affects_cli_behavior": True,
                "provider": "codex",
                "provider_version": "0.10.0",
                "summary": "Changelog states --json-schema accepts inline JSON only and rejects paths.",
                "why_authoritative": "Official CLI changelog.",
            },
        ]
    )

    # Counterexample: invented resolution on contradicted provider docs MUST be rejected
    invented = copy.deepcopy(ledger)
    invented["material_questions"].append(
        {
            "id": "Q004",
            "task_id": "032",
            "question": "Does Provider X --json-schema accept a file path or inline JSON?",
            "importance": "high",
            "status": "resolved",
            "claim_type": "verified_interface",
            "evidence_domain": "cli_interface",
            "evidence_ids": ["E-CLI-DOC-A", "E-CLI-DOC-B"],
            "contradictions": [
                {
                    "source_ids": ["E-CLI-DOC-A", "E-CLI-DOC-B"],
                    "conflict": "Reference states file path while changelog states inline JSON only.",
                }
            ],
            "resolution": "Assume file path works because the main reference page lists it.",
            "planning_impact": "Pass file path to --json-schema.",
        }
    )
    assert_raises_study_error(
        lambda: studyctl.normalize_evidence_ledger(invented),
        "probe_required",
    )

    # Positive case: helper produces deterministic probe requirement and ledger accepts it
    probe_req = studyctl.resolve_contradiction_requirement(
        "Q004",
        ["E-CLI-DOC-A", "E-CLI-DOC-B"],
        "Reference states file path while changelog states inline JSON only.",
        probe_check="Run installed Provider X CLI --help and fixture schema dry-run.",
        falsification_condition="CLI exits non-zero when passed a temporary schema file path.",
        conservative_fallback="Fall back to prompt-embedded schema validation until CLI flag is verified.",
    )
    assert probe_req["status"] == "probe_required"
    assert probe_req["invented_resolution_allowed"] is False

    valid = copy.deepcopy(ledger)
    valid["material_questions"].append(
        {
            "id": "Q004",
            "task_id": "032",
            "question": "Does Provider X --json-schema accept a file path or inline JSON?",
            "importance": "high",
            "status": probe_req["status"],
            "claim_type": "capability_probe",
            "evidence_domain": "cli_interface",
            "evidence_ids": ["E-CLI-DOC-A", "E-CLI-DOC-B"],
            "contradictions": probe_req["contradictions"],
            "capability_probe": probe_req["capability_probe"],
        }
    )
    normalized = studyctl.normalize_evidence_ledger(valid, require_ready=True)
    probe_q_ids = {p["question_id"] for p in normalized["probe_requirements"]}
    assert "Q004" in probe_q_ids
    assert normalized["stopping_evaluation"]["ready"] is True


def test_ac04_prepared_reports_consumed_without_broad_research() -> None:
    """AC04: Known prepared reports are consumed without requiring another broad research phase."""
    ledger = studyctl.normalize_evidence_ledger(base_ledger(), require_ready=True)
    plan = studyctl.plan_research_action(ledger, signals=[])
    assert plan["action"] == "consume_prepared_reports"
    assert plan["requires_broad_research"] is False
    assert set(plan["consumed_reports"]) == {"010", "022"}
    assert plan["refresh_targets"] == []
    assert set(plan["preserved_report_ids"]) == {"010", "022"}


def test_ac05_located_only_and_inaccessible_sources_cannot_verify_interface() -> None:
    """AC05: A source that was only located cannot satisfy a verified-interface claim; scopes stay separate."""
    ledger = base_ledger()
    ledger["source_register"].extend(
        [
            {
                "id": "S-LOCATED",
                "source_type": "official_documentation",
                "title": "Antigravity CLI reference",
                "publisher": "Google",
                "url": "https://example.com/antigravity/cli",
                "version_or_date": "2026-10-28",
                "reading_scope": "discovery_only",
                "evidence_domain": "cli_interface",
                "affects_cli_behavior": True,
                "summary": "URL located in search results only; page body not inspected.",
                "why_authoritative": "Official docs URL found via search.",
            },
            {
                "id": "S-PAYWALL",
                "source_type": "research_paper",
                "title": "Restricted benchmark paper",
                "publisher": "Journal X",
                "url": "https://example.com/paywalled-paper",
                "version_or_date": "2026-10-01",
                "reading_scope": "inaccessible",
                "access_error": "HTTP 403 paywall prevented inspecting full text.",
                "evidence_domain": "general",
                "summary": "Inaccessible source recorded for transparency; not verified support.",
                "why_authoritative": "Peer-reviewed venue (uninspected due to paywall).",
            },
        ]
    )
    normalized = studyctl.normalize_evidence_ledger(ledger, require_ready=True)
    scopes = normalized["reading_scope_summary"]
    assert scopes["discovery_only"] == ["S-LOCATED"]
    assert scopes["abstract_only"] == ["W-BOOK"]
    assert set(scopes["inspected_section"]) == {"W-COST", "W-CONTEXT"}
    assert scopes["inaccessible"] == ["S-PAYWALL"]
    assert "S-LOCATED" not in scopes["verified_support_ids"]
    assert "S-PAYWALL" not in scopes["verified_support_ids"]
    assert "W-BOOK" not in scopes["verified_support_ids"]

    # Counterexample 1: located-only (discovery_only) source CANNOT satisfy verified_interface
    bad_located = copy.deepcopy(ledger)
    bad_located["material_questions"].append(
        {
            "id": "Q005",
            "task_id": "034",
            "question": "What exact flags does Antigravity CLI support in headless mode?",
            "importance": "high",
            "status": "resolved",
            "claim_type": "verified_interface",
            "evidence_domain": "cli_interface",
            "evidence_ids": ["S-LOCATED"],
            "resolution": "Claimed headless flags from search snippet without inspecting docs.",
            "planning_impact": "Invoke unverified CLI flags directly.",
        }
    )
    assert_raises_study_error(
        lambda: studyctl.normalize_evidence_ledger(bad_located),
        "verified_interface",
    )

    # Counterexample 2: abstract_only source CANNOT satisfy verified_interface
    bad_abstract = copy.deepcopy(ledger)
    bad_abstract["material_questions"].append(
        {
            "id": "Q006",
            "task_id": "034",
            "question": "Does the interface contract guarantee deterministic JSON output?",
            "importance": "high",
            "status": "resolved",
            "claim_type": "verified_interface",
            "evidence_domain": "cli_interface",
            "evidence_ids": ["W-BOOK"],
            "resolution": "Inferred interface schema behavior from a public index page.",
            "planning_impact": "Skip runtime JSON validation.",
        }
    )
    assert_raises_study_error(
        lambda: studyctl.normalize_evidence_ledger(bad_abstract),
        "verified_interface",
    )

    # Counterexample 3: inaccessible source CANNOT count as verified support for any resolved question
    bad_inaccessible = copy.deepcopy(ledger)
    bad_inaccessible["material_questions"].append(
        {
            "id": "Q007",
            "task_id": "010",
            "question": "Does the paywalled benchmark justify dropping retries?",
            "importance": "medium",
            "status": "resolved",
            "evidence_ids": ["S-PAYWALL"],
            "resolution": "Assumed paywalled benchmark confirms zero retries are optimal.",
            "planning_impact": "Disable retry logic globally.",
        }
    )
    assert_raises_study_error(
        lambda: studyctl.normalize_evidence_ledger(bad_inaccessible),
        "inaccessible or discovery_only",
    )


def test_ac06_api_pricing_cannot_substitute_for_subscription_quota() -> None:
    """AC06: An API pricing record cannot silently substitute for subscription-quota evidence."""
    # Counterexample 1: material question claiming subscription_quota resolved from api_pricing source
    bad_q = base_ledger()
    bad_q["material_questions"][1]["status"] = "resolved"
    bad_q["material_questions"][1]["resolution"] = (
        "Estimated subscription quota limit directly from API per-token price table."
    )
    bad_q["material_questions"][1].pop("capability_probe", None)
    assert_raises_study_error(
        lambda: studyctl.normalize_evidence_ledger(bad_q),
        "api_pricing record cannot silently substitute for subscription_quota",
    )

    # Counterexample 2: recommendation with subscription_quota domain backed only by api_pricing source
    bad_rec = base_ledger()
    bad_rec["recommendations"].append(
        {
            "id": "REC-QUOTA-BAD",
            "task_id": "022",
            "report_id": "022",
            "material_question_id": "Q001",
            "source_ids": ["W-COST"],
            "evidence_kind": "proposed_design",
            "claim_type": "subscription_quota",
            "evidence_domain": "subscription_quota",
            "change": "Set fixed Codex Pro daily quota cap from API token pricing.",
            "repository_applicability": "Applies to availability.py cooldown budget.",
            "confidence": "medium",
            "implementation_consequence": "Hardcode subscription quota threshold from API price.",
            "falsification_condition": "Fails if subscription quota resets independently of API prices.",
        }
    )
    assert_raises_study_error(
        lambda: studyctl.normalize_evidence_ledger(bad_rec),
        "api_pricing record cannot silently substitute for subscription_quota",
    )

    # Positive case: genuine subscription_quota / account_capability source IS accepted
    good = base_ledger()
    good["source_register"].append(
        {
            "id": "S-SUB-QUOTA",
            "source_type": "official_documentation",
            "title": "Provider subscription quota policy",
            "publisher": "Provider Y",
            "url": "https://provider-y.example/docs/subscription-limits",
            "version_or_date": "2026-10-28",
            "reading_scope": "inspected_section",
            "evidence_domain": "subscription_quota",
            "provider": "claude",
            "summary": "Documents rolling 5-hour subscription usage window separate from API billing.",
            "why_authoritative": "Official subscription plan documentation.",
        }
    )
    good["material_questions"][1]["status"] = "resolved"
    good["material_questions"][1]["evidence_ids"] = ["S-SUB-QUOTA"]
    good["material_questions"][1]["resolution"] = (
        "Official subscription policy defines a rolling 5-hour usage window separate from API pricing."
    )
    good["material_questions"][1].pop("capability_probe", None)
    normalized = studyctl.normalize_evidence_ledger(good, require_ready=True)
    assert normalized["material_questions"][1]["status"] == "resolved"


def test_ac07_provider_version_change_invalidates_only_affected_of_32_reports() -> None:
    """AC07: A provider-version change invalidates only affected recommendations, not all 32 reports."""
    prepared_reports = []
    source_register = [
        {
            "id": "S-CORE",
            "source_type": "official_documentation",
            "title": "Core engineering architecture notes",
            "publisher": "Anthropic",
            "url": "https://www.anthropic.com/research/effective-context-engineering-for-ai-agents",
            "version_or_date": "2026-10-28",
            "reading_scope": "inspected_section",
            "evidence_domain": "architecture",
            "summary": "Provider-agnostic context and workflow design principles.",
            "why_authoritative": "Primary architecture publication.",
        },
        {
            "id": "S-CODEX-CLI",
            "source_type": "official_documentation",
            "title": "Codex CLI interface reference",
            "publisher": "OpenAI",
            "url": "https://developers.openai.com/codex/cli",
            "version_or_date": "codex 0.10.0 (2026-10-28)",
            "reading_scope": "inspected_section",
            "evidence_domain": "cli_interface",
            "affects_cli_behavior": True,
            "provider": "codex",
            "provider_version": "0.10.0",
            "summary": "Documents Codex CLI 0.10.0 non-interactive schema flags.",
            "why_authoritative": "Official Codex CLI documentation.",
        },
        {
            "id": "S-CLAUDE-CLI",
            "source_type": "official_documentation",
            "title": "Claude Code CLI reference",
            "publisher": "Anthropic",
            "url": "https://docs.anthropic.com/en/docs/claude-code",
            "version_or_date": "claude 2.1.0 (2026-10-28)",
            "reading_scope": "inspected_section",
            "evidence_domain": "cli_interface",
            "affects_cli_behavior": True,
            "provider": "claude",
            "provider_version": "2.1.0",
            "summary": "Documents Claude Code 2.1.0 headless execution flags.",
            "why_authoritative": "Official Claude Code CLI documentation.",
        },
    ]
    questions = []
    recommendations = []

    codex_report_ids = {"R016", "R024"}
    claude_report_ids = {"R015"}

    for idx in range(1, 33):
        rid = f"R{idx:03d}"
        tid = f"{idx * 2:03d}"
        if rid in codex_report_ids:
            sid = "S-CODEX-CLI"
            provider = "codex"
            pver = "0.10.0"
            domain = "cli_interface"
            ver_sens = True
            affects_cli = True
        elif rid in claude_report_ids:
            sid = "S-CLAUDE-CLI"
            provider = "claude"
            pver = "2.1.0"
            domain = "cli_interface"
            ver_sens = True
            affects_cli = True
        else:
            sid = "S-CORE"
            provider = ""
            pver = ""
            domain = "architecture"
            ver_sens = False
            affects_cli = False

        prepared_reports.append(
            {
                "report_id": rid,
                "task_id": tid,
                "path": f"docs/research/20261028-skill-optimization/prepared-research/{rid.lower()}.md",
                "research_revision": 2,
                "source_ids": [sid],
                "implementation_status": "pending",
                "independent_review_status": "pending",
                "affected_providers": [provider] if provider else [],
                "version_sensitive": ver_sens,
            }
        )
        qid = f"Q{idx:03d}"
        questions.append(
            {
                "id": qid,
                "task_id": tid,
                "question": f"What contract governs topic {rid}?",
                "importance": "high",
                "status": "resolved",
                "evidence_domain": domain,
                "evidence_ids": [sid],
                "resolution": f"Contract for {rid} follows inspected source {sid}.",
                "planning_impact": f"Apply verified contract for {rid}.",
            }
        )
        recommendations.append(
            {
                "id": f"REC{idx:03d}",
                "task_id": tid,
                "report_id": rid,
                "material_question_id": qid,
                "source_ids": [sid],
                "evidence_kind": "proposed_design",
                "claim_type": "design_recommendation",
                "evidence_domain": domain,
                "change": f"Implement contract update for report {rid}.",
                "repository_applicability": f"Applies to module owned by task {tid} for {rid}.",
                "confidence": "high",
                "implementation_consequence": f"Update handler and regression tests for {rid}.",
                "falsification_condition": f"Fails if regression suite for {rid} rejects expected contract.",
                "version_sensitive": ver_sens,
                "affects_cli_behavior": affects_cli,
                "provider": provider,
                "provider_version": pver,
            }
        )

    ledger = studyctl.normalize_evidence_ledger(
        {
            "schema_version": 1,
            "ledger_id": "corpus-32-reports",
            "prepared_reports": prepared_reports,
            "source_register": source_register,
            "material_questions": questions,
            "recommendations": recommendations,
        },
        require_ready=True,
    )
    assert len(ledger["prepared_reports"]) == 32
    assert len(ledger["recommendations"]) == 32

    result = studyctl.evaluate_invalidation(
        ledger,
        [
            {
                "signal": "provider_version_change",
                "provider": "codex",
                "previous_version": "0.10.0",
                "current_version": "0.11.0",
                "reason": "Codex CLI 0.11.0 changed schema flag syntax.",
            }
        ],
    )
    assert result["action"] == "targeted_refresh"
    assert result["requires_broad_research"] is False
    assert result["invalidated_report_ids"] == ["R016", "R024"]
    assert len(result["preserved_report_ids"]) == 30
    assert "R015" in result["preserved_report_ids"]  # Claude report unaffected
    assert result["invalidated_recommendation_ids"] == ["REC016", "REC024"]
    assert len(result["preserved_recommendation_ids"]) == 30
    assert result["invalidated_source_ids"] == ["S-CODEX-CLI"]


def test_prepared_research_not_proof_of_implementation_or_review() -> None:
    """Prepared research is never proof of implementation or independent-review completion."""
    report = {
        "report_id": "010",
        "task_id": "010",
        "path": "docs/research/20261028-skill-optimization/prepared-research/010-adaptive-study.md",
        "research_revision": 2,
        "source_ids": ["W-COST"],
        "implementation_status": "pending",
        "independent_review_status": "pending",
        "evidence_origin": "prepared_research",
    }
    status = studyctl.validate_completion_claim(report)
    assert status["study_input_ready"] is True
    assert status["implementation_proven"] is False
    assert status["independent_review_proven"] is False

    assert_raises_study_error(
        lambda: studyctl.validate_completion_claim(report, claim_implementation_done=True),
        "not proof of implementation",
    )
    assert_raises_study_error(
        lambda: studyctl.validate_completion_claim(report, claim_review_done=True),
        "not proof of independent-review",
    )

    bad_impl = base_ledger()
    bad_impl["prepared_reports"][0]["implementation_status"] = "completed"
    assert_raises_study_error(
        lambda: studyctl.normalize_evidence_ledger(bad_impl),
        "not proof of implementation",
    )

    bad_review = base_ledger()
    bad_review["prepared_reports"][0]["independent_review_status"] = "completed"
    assert_raises_study_error(
        lambda: studyctl.normalize_evidence_ledger(bad_review),
        "not proof of independent-review",
    )


def test_recommendation_contract_and_stopping_by_decision_risk_not_source_count() -> None:
    """Every recommendation binds to question, applicability, and falsification; stopping ignores source count."""
    missing_falsification = base_ledger()
    missing_falsification["recommendations"][0]["falsification_condition"] = ""
    assert_raises_study_error(
        lambda: studyctl.normalize_evidence_ledger(missing_falsification),
        "falsification_condition",
    )

    missing_applicability = base_ledger()
    missing_applicability["recommendations"][0]["repository_applicability"] = ""
    assert_raises_study_error(
        lambda: studyctl.normalize_evidence_ledger(missing_applicability),
        "repository_applicability",
    )

    missing_question = base_ledger()
    missing_question["recommendations"][0]["material_question_id"] = "Q999"
    assert_raises_study_error(
        lambda: studyctl.normalize_evidence_ledger(missing_question),
        "unknown material_question_id",
    )

    # Even with 10 verified sources, one open high-impact question blocks stopping
    many_sources = base_ledger()
    for i in range(1, 11):
        many_sources["source_register"].append(
            {
                "id": f"S{i:03d}",
                "source_type": "official_documentation",
                "title": f"Extra official doc {i}",
                "publisher": "Vendor",
                "url": f"https://example.com/docs/{i}",
                "version_or_date": "2026-10-28",
                "reading_scope": "inspected_section",
                "evidence_domain": "general",
                "summary": f"Verified supporting reference {i} unrelated to open question Q099.",
                "why_authoritative": "Official documentation.",
            }
        )
    many_sources["material_questions"].append(
        {
            "id": "Q099",
            "task_id": "010",
            "question": "Does Windows path quoting break worker invocations?",
            "importance": "high",
            "status": "open",
            "evidence_ids": [],
        }
    )
    norm = studyctl.normalize_evidence_ledger(many_sources, require_ready=False)
    assert norm["stopping_evaluation"]["source_count"] >= 12
    assert norm["stopping_evaluation"]["source_count_is_proof"] is False
    assert norm["stopping_evaluation"]["ready"] is False
    assert any("Q099" in msg for msg in norm["stopping_evaluation"]["blocking_reasons"])


def test_broad_study_cannot_silently_narrow_to_single_blog() -> None:
    """Instruction 5: Preserve user-requested broad study breadth."""
    spec = {
        "schema_version": 2,
        "request_summary": "Compare multi-provider routing and caching contracts across CLI providers.",
        "complexity_assessment": {
            "level": "complex",
            "rationale": "Cross-provider routing contracts affect security, compatibility, and validation boundaries.",
            "signals": ["Multiple providers have distinct CLI schemas and auth boundaries."],
        },
        "internal_study": {
            "selection_source": "user",
            "depth": "related_packages",
            "rationale": "User selected related packages to inspect existing routing adapters.",
            "plan_finding": "Inspected routing adapters and study controller contracts in the skill scripts.",
        },
        "internal_sources": [
            {
                "id": "I001",
                "kind": "implementation",
                "location": "skill/plan-and-execute/scripts/studyctl.py",
                "finding": "studyctl validates and attaches adaptive study evidence to plans.",
                "planning_impact": "Extend studyctl with decision-oriented evidence ledger support.",
            }
        ],
        "material_questions": [
            {
                "id": "Q001",
                "question": "How should external sources be evaluated across providers?",
                "importance": "high",
                "status": "resolved",
                "evidence_ids": ["I001", "E001"],
                "resolution": "Use primary docs and separate reading scopes.",
                "planning_impact": "Enforce scope tracking in studyctl.",
            }
        ],
        "external_research": {
            "decision": "required",
            "selection_source": "user",
            "depth": "broad",
            "rationale": "User requested broad external research across multiple primary sources.",
            "trigger_assessment": {
                **{field: False for field in studyctl.TRIGGER_FIELDS},
                "user_requested": True,
            },
            "sources": [
                {
                    "id": "E001",
                    "source_type": "authoritative_other",
                    "is_blog": True,
                    "title": "Single opinion blog post",
                    "publisher": "Random Blog",
                    "url": "https://blog.example.com/agents",
                    "version_or_date": "2026-10-01",
                    "finding": "One author prefers using three sources per topic.",
                    "planning_impact": "Use arbitrary source count as stopping rule.",
                    "why_authoritative": "Popular practitioner blog post on agent workflows.",
                }
            ],
        },
        "synthesis": {
            "planning_constraints": ["Preserve user-requested broad study scope."],
            "derived_requirements": [],
            "risks": [],
            "validation_implications": [],
            "unresolved_questions": [],
            "stopping_reason": "Single blog post does not satisfy user-requested broad study.",
            "ready_for_planning": True,
        },
        "review": {
            "reviewer": "fresh study reviewer",
            **{field: True for field in studyctl.REVIEW_CHECKS},
            "notes": ["Checking broad study breadth preservation."],
        },
    }
    assert_raises_study_error(
        lambda: studyctl.normalize_study(spec),
        "single blog",
    )


def test_cli_ledger_commands() -> None:
    """Verify studyctl.py CLI ledger-validate, ledger-render, and ledger-refresh end-to-end."""
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        ledger_path = root / "ledger.json"
        signals_path = root / "signals.json"
        md_path = root / "LEDGER.md"
        ledger_path.write_text(json.dumps(base_ledger(), indent=2), encoding="utf-8")
        signals_path.write_text(
            json.dumps(
                {
                    "signals": [
                        {
                            "signal": "source_digest_change",
                            "source_id": "W-CONTEXT",
                            "reason": "Primary Anthropic context article updated its retrieval section.",
                        }
                    ]
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        script = str(SCRIPT_DIR / "studyctl.py")

        val = subprocess.run(
            [sys.executable, script, "ledger-validate", "--ledger", str(ledger_path), "--require-ready", "--json"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert val.returncode == 0, val.stderr or val.stdout
        val_data = json.loads(val.stdout)
        assert val_data["valid"] is True
        assert val_data["ready"] is True
        assert val_data["stopping_basis"] == "unresolved_decision_risk"

        rend = subprocess.run(
            [sys.executable, script, "ledger-render", "--ledger", str(ledger_path), "--output", str(md_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert rend.returncode == 0, rend.stderr or rend.stdout
        rendered = md_path.read_text(encoding="utf-8")
        assert "Shared source register" in rendered
        assert "Capability probe requirements" in rendered

        ref = subprocess.run(
            [sys.executable, script, "ledger-refresh", "--ledger", str(ledger_path), "--signals", str(signals_path), "--json"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert ref.returncode == 0, ref.stderr or ref.stdout
        ref_data = json.loads(ref.stdout)
        assert ref_data["action"] == "targeted_refresh"
        assert ref_data["requires_broad_research"] is False
        assert ref_data["invalidated_recommendation_ids"] == ["REC001"]
        assert ref_data["invalidated_report_ids"] == ["010"]
        assert ref_data["preserved_report_ids"] == ["022"]


def test_review_f01_recommendation_guards_apply_on_probe_required_questions() -> None:
    """Review 011 F01: a probe_required question cannot exempt a non-probe recommendation."""
    quota = base_ledger()
    quota["recommendations"].append(
        {
            "id": "REC-QUOTA-PROBEQ",
            "task_id": "022",
            "material_question_id": "Q002",
            "source_ids": ["W-COST"],
            "claim_type": "subscription_quota",
            "evidence_domain": "subscription_quota",
            "change": "Hardcode the subscription quota from the API price table.",
            "repository_applicability": "Applies to availability.py cooldown budget.",
            "implementation_consequence": "Fixed quota threshold derived from API prices.",
            "falsification_condition": "Fails if subscription quota resets independently of API prices.",
        }
    )
    assert_raises_study_error(
        lambda: studyctl.normalize_evidence_ledger(quota),
        "api_pricing record cannot silently substitute for subscription_quota",
    )

    interface = base_ledger()
    interface["source_register"].append(
        {
            "id": "S-LOCATED",
            "source_type": "official_documentation",
            "title": "Provider CLI reference",
            "publisher": "Provider",
            "url": "https://example.com/cli",
            "version_or_date": "2026-10-28",
            "reading_scope": "discovery_only",
            "evidence_domain": "cli_interface",
            "summary": "URL located in search results only; page body not inspected.",
        }
    )
    interface["recommendations"].append(
        {
            "id": "REC-IFACE-PROBEQ",
            "task_id": "022",
            "material_question_id": "Q002",
            "source_ids": ["S-LOCATED"],
            "claim_type": "verified_interface",
            "evidence_domain": "cli_interface",
            "change": "Invoke the located CLI flag directly in runner argv.",
            "repository_applicability": "Applies to run_isolated.py argv builders.",
            "implementation_consequence": "Unverified flag shipped in the runner.",
            "falsification_condition": "Fails if the installed CLI rejects the flag.",
        }
    )
    assert_raises_study_error(
        lambda: studyctl.normalize_evidence_ledger(interface), "verified_interface"
    )

    # Positive control: a capability_probe recommendation on the probe question stays valid.
    probe = base_ledger()
    probe["recommendations"].append(
        {
            "id": "REC-PROBE",
            "task_id": "022",
            "material_question_id": "Q002",
            "source_ids": ["W-COST"],
            "claim_type": "capability_probe",
            "evidence_domain": "subscription_quota",
            "change": "Probe CLI cooldown errors before relying on any quota number.",
            "repository_applicability": "Applies to availability.py cooldown classification.",
            "implementation_consequence": "Quota stays unknown until an observed cooldown is recorded.",
            "falsification_condition": "Fails if the account exposes no observable rate-limit signal.",
        }
    )
    assert studyctl.normalize_evidence_ledger(probe, require_ready=True)["stopping_evaluation"]["ready"]


def test_review_f02_undated_unlabelled_register_source_rejected() -> None:
    """Review 011 F02: an undated source must declare affects_cli_behavior."""
    for value in ("", "unknown", "latest"):
        ledger = base_ledger()
        source = ledger["source_register"][1]
        source["version_or_date"] = value
        source.pop("affects_cli_behavior")
        assert_raises_study_error(
            lambda: studyctl.normalize_evidence_ledger(ledger), "explicit version or date"
        )


def test_review_f03_contradiction_needs_probe_evidence() -> None:
    """Review 011 F03: no 'assumed' escape and no bare probe_verified flag."""
    ledger = base_ledger()
    ledger["internal_sources"] = [
        {
            "id": "I001",
            "kind": "tests",
            "location": "test/fixtures/provider_x_schema_probe.log",
            "finding": "Installed Provider X CLI accepted a schema file path in the fixture run.",
            "planning_impact": "Pass the schema as a file path; keep inline fallback.",
        }
    ]
    contradiction = [
        {"source_ids": ["W-COST", "W-CONTEXT"], "conflict": "The two documents disagree on the schema flag."}
    ]
    assumed = copy.deepcopy(ledger)
    assumed["material_questions"].append(
        {
            "id": "Q010",
            "question": "Which schema flag form does Provider X accept?",
            "importance": "medium",
            "status": "assumed",
            "evidence_ids": ["W-COST", "W-CONTEXT"],
            "contradictions": contradiction,
            "resolution": "Assume the file path form works as the reference says.",
            "planning_impact": "Pass a file path to the schema flag.",
        }
    )
    assert_raises_study_error(lambda: studyctl.normalize_evidence_ledger(assumed), "probe_required")

    bare = copy.deepcopy(assumed)
    bare["material_questions"][-1].update({"status": "resolved", "importance": "high", "probe_verified": True})
    assert_raises_study_error(lambda: studyctl.normalize_evidence_ledger(bare), "probe_verified requires")

    observed = copy.deepcopy(bare)
    observed["material_questions"][-1]["evidence_ids"] = ["I001", "W-COST", "W-CONTEXT"]
    observed["material_questions"][-1]["capability_probe"] = {
        "check": "Run the installed Provider X CLI with a fixture schema file.",
        "falsification_condition": "CLI exits non-zero when passed a schema file path.",
        "conservative_fallback": "Embed the schema inline until the flag is verified.",
    }
    norm = studyctl.normalize_evidence_ledger(observed, require_ready=True)
    assert norm["stopping_evaluation"]["ready"] is True


def test_review_f05_f10_prepared_report_fields_are_strict() -> None:
    """Review 011 F05/F10: origin cannot bypass non-proof; receipts and types are checked."""
    relabelled = base_ledger()
    relabelled["prepared_reports"][0].update(
        {"evidence_origin": "implementation", "implementation_status": "completed"}
    )
    assert_raises_study_error(
        lambda: studyctl.normalize_evidence_ledger(relabelled), "not proof of implementation"
    )
    unknown_origin = base_ledger()
    unknown_origin["prepared_reports"][0]["evidence_origin"] = "trust_me"
    assert_raises_study_error(lambda: studyctl.normalize_evidence_ledger(unknown_origin), "evidence_origin")
    self_receipt = base_ledger()
    self_receipt["prepared_reports"][0].update(
        {
            "implementation_status": "completed",
            "implementation_receipt": self_receipt["prepared_reports"][0]["path"],
        }
    )
    assert_raises_study_error(
        lambda: studyctl.normalize_evidence_ledger(self_receipt), "not proof of implementation"
    )
    with_receipt = base_ledger()
    with_receipt["prepared_reports"][0].update(
        {
            "implementation_status": "completed",
            "implementation_receipt": "docs/research/20261028-skill-optimization/implementation/010-receipt.json",
        }
    )
    studyctl.normalize_evidence_ledger(with_receipt)

    bad_revision = base_ledger()
    bad_revision["prepared_reports"][0]["research_revision"] = "two"
    assert_raises_study_error(lambda: studyctl.normalize_evidence_ledger(bad_revision), "research_revision")
    bad_flag = base_ledger()
    bad_flag["recommendations"][0]["version_sensitive"] = "false"
    assert_raises_study_error(lambda: studyctl.normalize_evidence_ledger(bad_flag), "version_sensitive")


def test_review_f06_f09_invalidation_targets_and_attribution() -> None:
    """Review 011 F06/F09: untargeted signals fail; unmatched signals and sources are exact."""
    ledger = studyctl.normalize_evidence_ledger(base_ledger(), require_ready=True)
    for signal in (
        {"signal": "provider_version_change", "reason": "Some provider changed its version."},
        {"signal": "source_digest_change", "reason": "Some source digest changed."},
        {"signal": "contradicted_evidence", "reason": "Some evidence was contradicted."},
    ):
        assert_raises_study_error(lambda: studyctl.evaluate_invalidation(ledger, [signal]), "must name")

    result = studyctl.evaluate_invalidation(
        ledger,
        [
            {"signal": "source_digest_change", "source_id": "W-CONTEXT", "reason": "Context article updated."},
            {"signal": "provider_version_change", "provider": "gemini", "reason": "Gemini CLI version bump."},
        ],
    )
    assert result["invalidated_recommendation_ids"] == ["REC001"]
    assert result["invalidated_source_ids"] == ["W-CONTEXT"], result["invalidated_source_ids"]
    assert [s["provider"] for s in result["unmatched_signals"]] == ["gemini"]

    # A model-contract change now reaches a version-sensitive report without recommendations.
    contract = studyctl.evaluate_invalidation(
        ledger,
        [{"signal": "model_contract_change", "provider": "claude", "reason": "Claude model contract changed."}],
    )
    assert contract["invalidated_report_ids"] == ["022"], contract
    assert contract["unmatched_signals"] == []


def test_review_f08_unread_quota_source_cannot_back_api_pricing() -> None:
    """Review 011 F08: only an inspected quota source counts as subscription-quota evidence."""
    ledger = base_ledger()
    ledger["source_register"].append(
        {
            "id": "S-QUOTA-LOCATED",
            "source_type": "official_documentation",
            "title": "Subscription limits",
            "publisher": "Provider Y",
            "url": "https://provider-y.example/docs/limits",
            "version_or_date": "2026-10-28",
            "reading_scope": "discovery_only",
            "evidence_domain": "subscription_quota",
            "affects_cli_behavior": False,
            "summary": "URL located in search results; body not inspected.",
        }
    )
    question = ledger["material_questions"][1]
    question.update(
        {
            "status": "resolved",
            "evidence_ids": ["W-COST", "S-QUOTA-LOCATED"],
            "resolution": "Quota equals the API price table, per a located limits page.",
        }
    )
    question.pop("capability_probe")
    assert_raises_study_error(
        lambda: studyctl.normalize_evidence_ledger(ledger),
        "api_pricing record cannot silently substitute for subscription_quota",
    )


def main() -> int:
    tests = [
        test_ac01_undated_cli_source_flagged_for_refresh,
        test_ac02_shared_source_distinct_task_applicability_without_article_copy,
        test_ac03_contradictory_provider_doc_yields_probe_not_invented_resolution,
        test_ac04_prepared_reports_consumed_without_broad_research,
        test_ac05_located_only_and_inaccessible_sources_cannot_verify_interface,
        test_ac06_api_pricing_cannot_substitute_for_subscription_quota,
        test_ac07_provider_version_change_invalidates_only_affected_of_32_reports,
        test_prepared_research_not_proof_of_implementation_or_review,
        test_recommendation_contract_and_stopping_by_decision_risk_not_source_count,
        test_broad_study_cannot_silently_narrow_to_single_blog,
        test_cli_ledger_commands,
        test_review_f01_recommendation_guards_apply_on_probe_required_questions,
        test_review_f02_undated_unlabelled_register_source_rejected,
        test_review_f03_contradiction_needs_probe_evidence,
        test_review_f05_f10_prepared_report_fields_are_strict,
        test_review_f06_f09_invalidation_targets_and_attribution,
        test_review_f08_unread_quota_source_cannot_back_api_pricing,
    ]
    for idx, test in enumerate(tests, 1):
        test()
        print(f"PROGRESS stage=adaptive_study_self_test done={idx} total={len(tests)} case={test.__name__}", flush=True)
    print(f"All {len(tests)} adaptive study acceptance and counterexample tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
