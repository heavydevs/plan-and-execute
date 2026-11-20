# 014 — Implementation outcome: assigned context, learned facts and token budgets

Feature: `F005` · Implementation TODO `014` · Independent review pending in TODO `015`.

## Implemented contracts

1. **Learning provenance, trust classes, and invalidation (`planctl.py`, `artifact_contract.py`)**:
   - Defined explicit trust classes (`normative_contract`, `validated_learning`, `versioned_pattern`, `failed_attempt_hypothesis`). Only `validated_learning` may materialize into `learnings/<src>-to-<tgt>.md`.
   - Attached provenance fields to every materialized learning artifact: `trust_class`, `producer_task_id`, `consumer_task_ids`, `source_contract_digest`, `cited_file_digests`, `invalidation_rule`, and canonical `provenance_sha256`.
   - Added deterministic freshness checking (`check_learning_artifact_freshness`) and selective invalidation (`invalidate_stale_learnings`, CLI `planctl.py check-learnings [--invalidate-stale]`): changing a cited file or revising a source contract invalidates or flags only the affected learning before reuse (`claim_task` and `validate_plan`) without deleting unrelated knowledge.
   - Enforced policy-override guards (`detect_policy_override_note`) across learnings, context items, and hypotheses so malicious or unsupported notes cannot alter acceptance criteria, validation commands, permissions, sandbox, or provider/routing policy.
   - Enforced single-task exclusion from universal `CONTEXT.md` (`SINGLE_TASK_CONTEXT_PATTERN`) alongside existing character/item budgets.
2. **Failed-attempt hypothesis isolation (`planctl.py`, `artifact_contract.py`, `runner_contract.py`)**:
   - Stored failed-attempt hypotheses per task in `task["attempt_hypotheses"]` (`trust_class: "failed_attempt_hypothesis"`), strictly separated from `CONTEXT.md`, `contexts/*`, and `learning_artifacts`.
   - Added `record_attempt_hypothesis`, `mark_hypothesis_disproven`, `check_hypothesis_freshness`, `invalidate_stale_hypotheses`, `promote_hypothesis_to_learning`, and `validate_attempt_hypotheses`.
   - Open hypotheses invalidate automatically when cited evidence files, failure signatures, or task contracts change (`fail_task`, `revise_plan`).
   - Disproven hypotheses are explicitly labeled and bounded; they can never be promoted into validated learnings or appear in shared facts (`complete_task` and `validate_plan` reject leakage). Promoting an open hypothesis requires passing deterministic validation evidence.
3. **Context accounting receipts, offline metrics, and prompt prefix/suffix bounds (`planctl.py`, `runner_contract.py`)**:
   - Added `build_context_accounting_receipt` and `measure_plan_context_metrics` (CLI `planctl.py context-receipt --plan <dir> [--task <id>]`) reporting selected file IDs, trust classes, exact byte counts, inclusion reasons, stale-learning error counts, and versioned-pattern candidates for repeated learnings, without retaining raw prompt text or secrets.
   - Preserved `runner_contract.py`'s byte-stable static prompt prefix across task IDs and long prior failures (`prompt_cache_structure`, `bounded_task_suffix`, `write_context_accounting_receipt`), explicitly recording cache reuse as an observed host/model metric rather than a structural assertion.
4. **Documentation (`EXECUTION_CONTEXT.md`, `TOKEN_EFFICIENCY.md`)**:
   - Documented trust classes, provenance metadata, cited-file/contract invalidation, failed-attempt hypothesis separation, context accounting receipts, offline measurement, and structural prefix vs observed cache reuse while keeping `TOKEN_EFFICIENCY.md` within the 10,000-byte validator limit.

## Verification

- All 7 declared checks in `P1_TESTS_014` passed (`exit_code: 0`) under `resource_watch.py`, including the new `test/optimization/context_learning_self_test.py` covering AC01–AC08, CLI subcommands, and the non-proof rule for prepared research.
- Additional local sanity checks passed: `python skill/plan-and-execute/scripts/token_efficiency_self_test.py` and `node tools/validate-skill.js`.
- `.ai-work/SERVICE_MAP.md` was reconciled with `service_map.py stamp --confirm-reconciled` after adding `test/optimization/context_learning_self_test.py`, preserving all 320 validation IDs.

## Recorded limitations

- Live task-success rates and per-host prompt-cache hit rates require owner-authorized authenticated model runs and were not measured in this offline implementation pass.
- Independent max-capability code review has not been performed yet and remains gated by TODO `015`.
