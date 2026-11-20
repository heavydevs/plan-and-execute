# Adaptive study protocol

Use this file only before planning. Read `ARTIFACT_WRITING.md` first. The goal is enough evidence to choose correct architecture, TODO boundaries, risks, and validation — not a research transcript.

## 1. Classify before broad repository inspection

Choose `simple`, `medium`, or `complex` from the request and immediately visible risk signals.

### Simple

Use when the change is direct, low-risk, locally scoped, and version/architecture uncertainty is unlikely to change the implementation. Internal/external study may be `none`; record one precise skip reason.

### Medium

Use when bounded repository discovery improves confidence. Automatically choose:

- `related_packages`: inspect the target package plus direct tests/dependencies; or
- `workspace_keywords`: search symbols/keywords across the workspace, then open only high-signal matches.

Use focused external research only for a material trigger such as version-sensitive behavior, unfamiliar API semantics, compatibility, security, or unclear external contract.

### Complex

Use when architecture, migration, security, compatibility, data integrity, ownership, or another high-impact uncertainty can materially change the plan.

Complex requests use two user choices (internal depth, then external depth), asked one per chat turn. Before asking either, read `STUDY_CHOICES.md`; it owns the question texts, the recommendation-marker rules, the clickable-choice host rules, and the already-specified shortcuts. Do not read it for `simple`/`medium` studies.

## 2. Search first, read second

Repository study:

1. locate candidate files/symbols/tests;
2. rank by likely effect on the request;
3. open focused files/ranges;
4. inspect direct dependencies/contracts/tests only when they can change planning;
5. widen scope only when discovered coupling justifies it.

Do not read the entire workspace merely because it is available.

External study:

- prefer primary/official docs, standards, release notes, papers, or authoritative technical sources;
- capture title/publisher/version/date/URL, `retrieved_at` vs `observed_at` when available, `reading_scope`, and the conclusion that changes the plan;
- preserve user-requested study breadth and original source attribution; do not silently narrow a broad study to a single blog or treat source count as semantic proof;
- do not paste articles or long quotes into study state.

### Reading and verification scopes

Record each external source's scope explicitly and separately:

- `discovery_only` (located URL/search hit only — never verified support);
- `abstract_only` (excerpt, title, abstract, or index only — never satisfies `verified_interface`);
- `inspected_section` (specific relevant primary sections inspected — verified support);
- `full_source` (complete primary source inspected — verified support);
- `inaccessible` (failed access attempt/paywall with explicit `access_error` — never verified support).

Distinguish `verified_source_fact`, `observed_repository_behavior`, and `proposed_design`. Only `inspected_section`/`full_source` sources may be `verified_source_fact`. Record `failed_access_attempts` and `unknowns` explicitly instead of substituting plausible facts or zero values. An `api_pricing` record cannot silently substitute for `subscription_quota` evidence; only an inspected `subscription_quota`/`account_capability` source counts as quota evidence.

`version_or_date` must contain an explicit date or version. A source without one (missing, `unknown`, `latest`, …) must declare `affects_cli_behavior` (`true`/`false`) or use `evidence_domain: "cli_interface"`; an undeclared undated source is rejected. A CLI-affecting undated source is flagged for refresh and cannot back a resolved question.

## 3. Record evidence, not process

Deduplicate shared external sources in a compact `source_register` by stable ID while giving each task its own concise `repository_applicability` and `implementation_consequence` without copying entire articles.

Every recommended change must bind to:

- a `material_question_id`;
- `repository_applicability` for the target repo/task;
- a concrete `falsification_condition`.

When provider documents contradict each other, record `status: "probe_required"` with a concrete `capability_probe` (`check`, `falsification_condition`, `conservative_fallback`, `changes_acceptance_silently: false`) rather than inventing a resolution. A contradicted question cannot be `resolved` or `assumed` unless `probe_verified: true` is backed by that `capability_probe` and a cited internal or `observed_repository_behavior` source recording the probe result.

Recommendation guards follow the recommendation's own `claim_type`: only a `capability_probe` recommendation inherits probe status; a `verified_interface`, `subscription_quota` or design recommendation is checked as a resolved claim even when its question is `probe_required`.

One internal source:

```json
{
  "id": "I001",
  "location": "src/auth/token.py:88-121",
  "finding": "Refresh tokens expire after 30 days and reuse the common token parser.",
  "planning_impact": "The refresh TODO must preserve the 30-day contract and modify the common parser path."
}
```

One external source:

```json
{
  "id": "E001",
  "title": "...",
  "publisher": "...",
  "url": "https://...",
  "version_or_date": "2026-08-20",
  "why_authoritative": "Official vendor documentation for the API used by this repository.",
  "finding": "The cursor becomes invalid after 24 hours.",
  "planning_impact": "Tests must cover cursor expiry and the retry path must not reuse expired cursors."
}
```

Do not record:

- search queries;
- dead ends that do not affect a decision;
- generic framework knowledge;
- verbose explanation of how the finding was discovered.

## 4. Material questions

A material question exists only when its answer can change architecture, requirement interpretation, task decomposition, compatibility, risk, or validation.

```json
{
  "id": "Q001",
  "question": "Does API v2 still accept the legacy cursor format?",
  "importance": "high",
  "status": "resolved",
  "resolution": "Vendor v2 rejects legacy cursors with HTTP 400.",
  "planning_impact": "Add a migration boundary before enabling v2 pagination.",
  "evidence_ids": ["E001"]
}
```

Do not turn curiosity into a material question. Resolve high-impact uncertainty before autostart.

## 5. Synthesis

Schema-v2 synthesis keeps only planning inputs:

- `planning_constraints`;
- `derived_requirements`;
- `risks`;
- `validation_implications`;
- `unresolved_questions`;
- `ready_for_planning`;
- `stopping_reason`.

Each list item is one atomic statement. Prefer path/symbol/source ids over repeating evidence text.

Stop by unresolved decision risk, never by an arbitrary source count. Stop when every high-impact question is `resolved` with verified evidence (at least one internal or `inspected_section`/`full_source` citation) or `probe_required` with a concrete implementation-time capability probe and conservative fallback, and additional evidence is unlikely to change:

- architecture/compatibility decision;
- requirement inventory;
- TODO/context boundaries;
- material risk;
- deterministic validation strategy.

`stopping_reason` states that saturation condition; it does not summarize the research session.

### Prepared reports and selective invalidation

When prepared research reports already exist, a task begins from its assigned report instead of restarting a broad literature survey. Refresh evidence only on explicit invalidation signals (`cli_version_change`, `provider_version_change`, `source_digest_change`, `model_contract_change`, `account_capability_change`, `contradicted_evidence`, `missing_date_or_version`), invalidating only affected recommendations and reports rather than the entire corpus. A signal must name its target (`provider` for `provider_version_change`; `source_ids` for `source_digest_change`/`missing_date_or_version`; `source_ids` or `material_question_id` for `contradicted_evidence`; or a `component`). Signals that match nothing are returned in `unmatched_signals`, never dropped.

A prepared report waives a medium request's focused research only when it names `source_ids`, and never for `security_sensitive` or `conflicting_evidence` triggers.

Prepared research establishes design/study input only; it is never proof of runtime implementation or independent-review completion. A report under `prepared-research/` is treated as `prepared_research` whatever `evidence_origin` says (`prepared_research`, `implementation`, `independent_review`), and `completed` needs a separate repository-relative `.json` receipt; the delivery gate verifies that receipt.

## 6. Review

A fresh study reviewer checks:

- selected depth matches complexity/user choice;
- all material questions are resolved or explicitly block planning;
- evidence is authoritative enough for the decision;
- synthesis follows evidence;
- no important version/security/compatibility issue is missing;
- unnecessary findings/process narration are omitted.

Review notes record concrete defects/evidence only.

## 7. Commands

Use the concise study controller:

```bash
python <skill-dir>/scripts/studyctl_concise.py validate --spec /tmp/study.json
python <skill-dir>/scripts/studyctl_concise.py attach --plan <plan-path> --spec /tmp/study.json
python <skill-dir>/scripts/studyctl_concise.py validate-plan --plan <plan-path>
python <skill-dir>/scripts/studyctl.py ledger-validate --ledger /tmp/ledger.json --json
python <skill-dir>/scripts/studyctl.py ledger-refresh --ledger /tmp/ledger.json --signals /tmp/signals.json --json
```

For a simple request with no broad study, the study still records the explicit selection/skip rationale required by schema v2; it should be very short.

## 8. Text budgets

`studyctl_concise.py` rejects oversized or high-confidence vague derived fields. Important ceilings:

- request summary 320 chars;
- rationale 280;
- signal 180;
- location 220;
- finding 320;
- planning impact 280;
- material question 240;
- synthesis item 260;
- stopping reason 280;
- review note 240.

These are maxima, not targets. Split multiple independent findings instead of writing one long paragraph. Never silently truncate evidence that changes a decision.
