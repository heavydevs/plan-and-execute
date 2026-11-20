# 012 — Implementation outcome: requirements, task decomposition and schema-v4 state

Status: `completed` (implementation evidence only; independent review remains pending for TODO `013`).

## Summary of changes

- **`skill/plan-and-execute/scripts/planctl.py`**:
  - Added strict JSON decoding (`_unique_json_pairs`, `_reject_non_finite_json`, `parse_strict_json`) rejecting duplicate object keys and non-finite constants (`NaN`, `Infinity`, `-Infinity`), plus `allow_nan=False` in `atomic_write_json` and `canonical_json_sha256`.
  - Implemented single-writer locking (`plan_writer_lock`, `.plan-writer.lock` with stale-PID recovery) and optimistic concurrency (`generation` counter) across `create_plan`, `save_manifest`, `revise_plan`, and `recover_projections` so stale writers cannot overwrite newer generations.
  - Implemented staged plan creation (`create_plan`) and staged plan revision (`revise_plan`) that normalize and audit the full specification, task graph, requirement coverage, research metadata, and projections in a staging directory before publishing `manifest.json`. Failed revisions discard staging and leave the previous manifest and projections untouched.
  - Added `.projection-state.json` lag detection and `recover_projections` (`planctl_concise.py recover-projections`) to clean abandoned `.staging/` directories, rebuild all schema-v4 projections strictly from authoritative `manifest.json`, and remove obsolete projections from prior generations without marking any task complete or combining generations.
  - Implemented transitive DAG `task_contract_digest` / `compute_task_contract_digests`, selective invalidation on `revise_plan` (reopening changed tasks and their transitive dependents while preserving unrelated completed tasks), immutable `receipt_history` archival on revision/reset, and the single authoritative receipt-validity function `validate_receipt` (with `register_receipt_validator` extension hook for task `018`).
  - Added optional requirement `supersession_note`, optional `plan_mode` (`single_implementation` guard against active second-plan tasks), optional task `review_of` (rejecting orphan reviews and reviews missing a dependency on the reviewed task), and optional `research_metadata` (separating prepared research from execution status, validating report existence/hashes, requiring transformed research tasks to remain `pending` with subtasks referencing their assigned report, and rejecting prepared research as completion or independent-review proof).
  - Preserved legacy schema v1–v3 compatibility across `load_plan`, `validate_plan`, `save_manifest`, `recover_projections` (`legacy_preserved: True`), and `revise_plan` (explicitly refuses silent schema-4 rewrite).
  - Added CLI subcommands `revise`, `recover-projections`, and `validate-receipt`.
- **`skill/plan-and-execute/scripts/artifact_contract.py`**:
  - Wrapped `planctl.revise_plan` with concise derived-text preflight checks (`amendment` and requirement `supersession_note` budgets).
  - Rendered requirement `supersession_note` in concise `PLAN.md`.
  - Guarded schema-v4-only text checks (`context_boundary`, `subtasks`, `learning_targets`) and legacy schema-v1 skipping in `_validate_plan_text` / `validate_plan` so legacy schema v1–v3 plans remain readable and validatable without schema-4 rewrites.
- **`skill/plan-and-execute/references/PLAN_SPEC.md`** & **`skill/plan-and-execute/references/PLANNING_PROTOCOL.md`**:
  - Documented staged generations, `.plan-writer.lock`, `generation` CAS, `plan_revision` records, `recover-projections`, `contract_digest`, single receipt-validity function (`validate_receipt`), `supersession_note`, `plan_mode`, `research_metadata`, `review_of`, deterministic preflight + post-implementation review, and legacy schema v1–v3 preservation.
- **`test/optimization/plan_contract_self_test.py`**:
  - Added deterministic self-tests covering AC01–AC08 plus prepared-research non-proof, strict JSON negative cases, orphan review rejection, inconsistent subtask ID detection, crash injection before and after authority publication, stale writer rejection, legacy schema v1–v3 preservation, selective invalidation, receipt history, the `018` validator extension hook, and live repository `baseline_contracts` verification.

## Acceptance coverage

- **AC01**: Verified failed revisions (cycles, uncovered requirements, orphan/non-dependent reviews, vague derived text) remove staging and leave the prior manifest and task projections byte-identical and valid (`test_ac01_failed_revision_preserves_previous_manifest_and_projections`).
- **AC02**: Verified requirement coverage, explicit acceptance/validation checks, strict JSON rejection of duplicate keys and non-finite constants, canonical subtask ID enforcement, and `supersession_note` preservation (`test_ac02_coverage_strict_json_and_subtask_consistency`).
- **AC03**: Verified transformed research tasks stay `pending` with subtasks referencing their assigned report, and prepared research is rejected as completion or independent-review proof (`test_ac03_transformed_research_task_and_prepared_research_not_proof`).
- **AC04**: Verified schema v1–v3 workspaces remain readable/validatable and are not rewritten by `save_manifest`, `recover_projections`, or `revise_plan` (`test_ac04_legacy_schema_1_to_3_preserved_without_schema4_rewrite`).
- **AC05**: Verified active second-plan tasks and missing/stale research outputs are rejected in both unit fixtures and the live optimization plan via `baseline_contracts` (`test_ac05_no_second_plan_and_no_nonexistent_research_output`).
- **AC06**: Verified recovery after crashes both before authority publication (abandoned `.staging/`) and after `manifest.json` replacement before task/context rendering (`test_ac06_crash_before_and_after_authority_publication_and_recovery`).
- **AC07**: Verified stale writers holding an older generation are rejected by `save_manifest` and `revise_plan`, and stale dead-PID `.plan-writer.lock` files recover cleanly (`test_ac07_stale_plan_writer_rejected_and_writer_lock`).
- **AC08**: Verified changing one task's contract/scoped input invalidates that task and its transitive dependent while preserving unrelated completed tasks, keeping old receipts immutable in `receipt_history`, and validating through the single extensible `validate_receipt` function (`test_ac08_selective_invalidation_receipt_history_and_extension_hook`).

## Unmeasured limits

- Crash-consistency testing uses deterministic fault injection at the Python process boundary (`_after_authority_publish` / `_after_manifest_replace`), not OS power-loss or filesystem fsync fault injection.
- No live authenticated model invocation or independent code review (`013`) was performed in this task.
