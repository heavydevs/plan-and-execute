# 010 — Adaptive Internal and External Study: Implementation Outcome

Task: `010` (Feature `F003`). Independent review remains pending in TODO `011`.

## Summary of Implemented Changes

Implemented the decision-oriented adaptive study evidence ledger, reading-scope separation, domain/contradiction guards, and signal-driven selective invalidation in `studyctl.py`, documented the revised protocol in `ADAPTIVE_STUDY.md`, extended `study_self_test.py`, and added the Task `010` acceptance and counterexample suite in `test/optimization/adaptive_study_self_test.py`.

### Changed Project Artifacts

- `skill/plan-and-execute/scripts/studyctl.py`:
  - Added explicit reading/verification scopes (`discovery_only`, `abstract_only`, `inspected_section`, `full_source`, `inaccessible`), `summarize_reading_scopes`, and verified-support enforcement (`counts_as_verified_support`). Inaccessible, abstract-only, and located-only sources cannot satisfy `verified_interface` claims, and inaccessible/discovery-only sources never count as verified support.
  - Added date/version detection (`has_explicit_version_or_date`), separate `retrieved_at` vs `observed_at` ISO dates, and `collect_refresh_flags` flagging undated/unversioned sources that affect CLI behavior (`missing_date_or_version_for_cli_behavior`).
  - Added domain-boundary enforcement rejecting `api_pricing` records as silent substitutes for `subscription_quota` claims.
  - Added `probe_required` question status, `normalize_capability_probe`, `resolve_contradiction_requirement`, and contradiction guards so contradictory provider docs yield a concrete capability probe and conservative fallback instead of an invented resolution.
  - Added compact reusable evidence ledger support (`normalize_evidence_ledger`, `deduplicate_source_register`, `normalize_evidence_records`, `normalize_recommendations`, `task_applicability_view`, `normalize_failed_access_attempts`, `normalize_unknowns`, `render_evidence_ledger`) binding every recommended change to a `material_question_id`, concise `repository_applicability`, and `falsification_condition`, while preventing full-article copies (`MAX_SOURCE_SUMMARY_CHARS = 480`).
  - Added `normalize_prepared_reports`, `validate_completion_claim`, `evaluate_invalidation`, `plan_research_action`, and `evaluate_stopping_condition` so tasks consume known prepared reports without restarting broad research, invalidate only affected recommendations/reports on explicit signals, stop by unresolved decision risk rather than source count, preserve user-requested broad study breadth, and reject prepared research as proof of implementation or independent-review completion.
  - Added CLI commands `ledger-validate`, `ledger-render`, and `ledger-refresh` while preserving all existing schema v1/v2 `validate`, `render`, `attach`, and `validate-plan` contracts and `studyctl_concise.py` compatibility.
- `skill/plan-and-execute/references/ADAPTIVE_STUDY.md`:
  - Documented reading/verification scopes, domain boundaries, compact deduplicated `source_register` with per-task applicability, recommendation falsification conditions, contradiction capability probes, decision-risk stopping rule, prepared-report consumption with explicit invalidation signals, and the new `studyctl.py` ledger commands.
- `skill/plan-and-execute/scripts/study_self_test.py`:
  - Preserved all 13 existing v1/v2 study gate tests and added regression tests for reading scopes, contradiction capability probes, prepared-report consumption, and prepared-research completion-proof rejection.
- `test/optimization/adaptive_study_self_test.py`:
  - Added 11 deterministic acceptance and counterexample tests covering `AC01` through `AC07`, prepared-research non-proof, recommendation contract enforcement, stopping by decision risk (not source count), broad-study breadth preservation, and CLI ledger commands.

## Acceptance Coverage

- **AC01** (`passed`): `test_ac01_undated_cli_source_flagged_for_refresh` verifies undated CLI-affecting sources emit `missing_date_or_version_for_cli_behavior` refresh flags and block readiness, while dated CLI sources and undated non-CLI sources are handled accurately.
- **AC02** (`passed`): `test_ac02_shared_source_distinct_task_applicability_without_article_copy` verifies stable-ID deduplication in `source_register`, distinct per-task applicability notes for tasks `010` and `022` via `task_applicability_view`, rejection of full-article summaries (`> 480` chars), and rejection of conflicting duplicate source IDs.
- **AC03** (`passed`): `test_ac03_contradictory_provider_doc_yields_probe_not_invented_resolution` verifies contradictory provider docs reject `status="resolved"` and require `status="probe_required"` with a concrete `capability_probe` and conservative fallback.
- **AC04** (`passed`): `test_ac04_prepared_reports_consumed_without_broad_research` and `test_v2_prepared_reports_avoid_restarting_research` verify known prepared reports are consumed directly with `requires_broad_research=False`.
- **AC05** (`passed`): `test_ac05_located_only_and_inaccessible_sources_cannot_verify_interface` verifies `discovery_only`, `abstract_only`, `inspected_section`, and `inaccessible` are tracked separately and `discovery_only`/`abstract_only`/`inaccessible` sources are rejected for `verified_interface` and verified-support claims.
- **AC06** (`passed`): `test_ac06_api_pricing_cannot_substitute_for_subscription_quota` verifies `api_pricing` records cannot satisfy `subscription_quota` questions or recommendations, while genuine `subscription_quota` sources or `probe_required` probes are accepted.
- **AC07** (`passed`): `test_ac07_provider_version_change_invalidates_only_affected_of_32_reports` verifies a `provider_version_change` signal for `codex` across 32 reports invalidates only the 2 affected Codex reports/recommendations (`R016`, `R024`) and preserves the other 30 reports with `requires_broad_research=False`.
- **Prepared-research non-proof** (`passed`): `test_prepared_research_not_proof_of_implementation_or_review` verifies prepared research reports cannot mark `implementation_status="completed"` or `independent_review_status="completed"` without verified receipts.

## Validation Receipts

Executed via `resource_watch.py` (`P1_TESTS_010` -> `docs/research/20261028-skill-optimization/implementation/010-checks.json`):

1. `python test/optimization/adaptive_study_self_test.py` — exit `0` (`docs/research/20261028-skill-optimization/implementation/logs/010/20261120T095239-18232/check-01.log`)
2. `python skill/plan-and-execute/scripts/study_self_test.py` — exit `0` (`docs/research/20261028-skill-optimization/implementation/logs/010/20261120T095239-18232/check-02.log`)
3. `python skill/plan-and-execute/scripts/artifact_concision_self_test.py` — exit `0` (`docs/research/20261028-skill-optimization/implementation/logs/010/20261120T095239-18232/check-03.log`)

Additionally verified `node tools/validate-skill.js` (exit `0`) and reconciled `.ai-work/SERVICE_MAP.md` for the two modified/added Task `010` test files via `service_map.py stamp --confirm-reconciled`.

## Unmeasured Limits

- No live authenticated provider invocation or live account subscription-quota benchmark was executed in this task.
- Vendor cost/intelligence publications referenced in prepared research `010-adaptive-study.md` remain bounded external evidence, not measured savings on this repository.
- Independent fresh-context max-capability code review is pending in TODO `011`.
