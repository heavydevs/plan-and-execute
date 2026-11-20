# Task 003 Outcome — Review and correct source coverage implementation

## Independent review (actual dispatches)
- **Dispatch 1** reviewed task 002 as delivered (`baseline_contracts.py` 640c26…, `task_002_self_test.py` 8c0852…).
  - Reviewer: `claude` / `claude-opus-5-5` / `xhigh`, tier `max`, fresh read-only session `b6c3bd44-99ba-4090-906b-d43ec0f3551a`.
  - Result: `approved`, 0 blocking, 7 findings (F1–F3 medium, F4–F5 low, F6–F7 info).
  - Evidence: `reviews/003/dispatch-1.json`, `reviews/003/findings-1.json`.
- **Dispatch 2** re-reviewed the corrected files at their final hashes, plus the declared-check log.
  - Routing: a `codex` / `gpt-6.2-sol` attempt failed on `quota` (an availability fault, skipped), so the dispatch fell back to Claude.
  - Reviewer: `claude` / `claude-opus-5-5` / `xhigh`, tier `max`, fresh read-only session `33acc38c-0a60-4513-b1a0-89d7c700096e`.
  - Result: `approved`, 0 blocking, 7 findings (R2-1–R2-3 low, R2-4–R2-7 info).
  - Evidence: `reviews/003/dispatch-2.json`, `reviews/003/findings-2.json`.
  - The receipt's `reviewer` and `reviewed_inputs` blocks are copied from this dispatch's `RECEIPT_REVIEWER` line.

## Corrections (write scope: `test/optimization/` only)
- **F1 (medium).** `run_source_and_contract_coverage` compared each prepared report with its own hash, so that check could never fail.
  - It now looks up an independent pin: TASK_INPUTS `research_sha256` when the path is the task's `research_report`, otherwise INDEX `report_sha256`/`decision_sha256`, read through `check_delivery.load`.
  - It verifies that pin with `check_delivery.verified_files(text=True)`.
  - Unpinned reports are only checked for existence. The result now reports `prepared_reports_pinned` (76) and `prepared_reports_unpinned` (80).
- **F2 (medium).** Before `structural()` runs, the wrapper now rejects a `prepared_reports` that is missing, empty, non-string or duplicated, with `PreflightError`. Previously a missing key raised a bare `KeyError`.
- **F3 (medium).** Every fixture now asserts all three states, and its contract text must name the observed outcome:
  - the committed baseline invariant;
  - the observed `check_delivery.structural` outcome on the changed input;
  - the wrapper's outcome.
  The literal `assertTrue` calls were removed.
- **F4, F5, F6 (low/info).**
  - Overlap with `delivery_gate_self_test` is documented.
  - Two real byte-drift fixtures now run in a temporary copy of the plan inputs, so the repository is never written:
    - an INDEX-pinned report;
    - a report pinned only by TASK_INPUTS, which `structural()` accepts and the wrapper rejects.
  - The hard-coded "130 tasks" is replaced by the TASK_INPUTS count.
  - The module docstring now names the task 002/003 entry point.
- **F7 (info).** Hashes are recomputed, and each acceptance case is mapped to test names below.

## Verification
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_003` exited 0, `health=healthy`, run `20261120T065707-15636`, `inputs_unchanged=true`.
  - `check-01.log`: `python test/optimization/task_002_self_test.py`, 9 tests OK.
  - `check-02.log`: `python docs/plans/20261028-skill-optimization/support/delivery_gate_self_test.py`, 55 tests OK, 1 skipped (`test_symlink`: symlink creation is not permitted on this host).
- Mutation check (not a declared check). With the pre-003 self-comparing wrapper restored in memory, the new tests fail 3 times:
  - pinned count 0 ≠ 1;
  - a raw `KeyError` for the missing key;
  - `GateError` instead of `PreflightError` for the duplicate path.
- Before running, the service map was stale. The cause was this task's two test files plus other offline self-test changes already in the working tree. None of them needs a new resource or service. The map was stamped with `service_map.py stamp --confirm-reconciled`; no validation IDs, commands or resources changed.
- The `P1_003` receipt gate is run after this outcome is pinned.

## Acceptance mapping
**Task 003**
- AC01 (fresh reviewer and reviewed-input hashes): `dispatch-2.json` and the receipt's `reviewer` block.
- AC02 (no unresolved critical/high finding; tests behind the acceptance cases): `findings-1.json`, `findings-2.json`, `003-checks.json`, `check-01.log`, `check-02.log`.
- AC03 (a reused or fabricated review is rejected): `check-02.log` tests `test_fake_review_rejected`, `test_low_tier_review_rejected`, `test_reused_review_from_other_receipt_rejected`, `test_review_dispatch_session_claimed_by_other_receipt_rejected`, `test_review_dispatch_stale_reviewed_input_rejected`, `test_dispatch_naming_other_task_rejected`, `test_dispatch_outside_task_review_dir_rejected`, `test_dispatch_without_reviewed_hashes_rejected`.
- AC04 (frontier only after repeated max failure; reuse rejected): `check-02.log` tests `test_valid_frontier_review`, `test_frontier_without_evidence_rejected`, `test_frontier_single_failure_rejected`, `test_frontier_for_quota_rejected`, `test_frontier_for_availability_class_rejected`, `test_frontier_after_non_max_failures_rejected`, `test_frontier_for_implementation_rejected`, `test_frontier_wrong_model_rejected`, `test_frontier_reusing_failed_dispatch_rejected`.
- AC05 (task 002 acceptance evidence on the final reviewed hashes): every case below comes from `check-01.log` of the run on hashes a57463… and 5b111d….

**Task 002**
- AC01: all 9 tests run offline.
- AC02: `check_fixture` / `assert_contract` in every test.
- AC03: this receipt.
- AC04: `test_negative_unknown_sources_id_rejected`.
- AC05: `test_negative_report_hash_drift_rejected`, `test_negative_index_pinned_report_byte_drift_rejected`, `test_negative_task_inputs_pinned_report_byte_drift_rejected`.
- AC06: `test_negative_requirement_without_consumer_rejected`.
- AC07: `test_negative_task_without_prepared_report_rejected`.
- AC08: `test_negative_missing_082_review_gate_rejected`.
- Provider limitation: `test_missing_authenticated_provider_is_limitation_not_failure_or_fake_review`.

## Limitations and open items
- **R2-1.** The task 002 receipt, outcome and checks describe the pre-correction code. `P1_002` is now expected to report them as stale. They were not edited, because they are outside this task's write scope. This 003 receipt and run hold the current evidence.
- **R2-2.** AC07 is enforced by `baseline_contracts.run_source_and_contract_coverage`, which `task_002_self_test.py` runs. It is not enforced by `check_delivery.structural`/`check`, which still accept an empty `prepared_reports`. Changing `check_delivery.py` is outside this task's scope.
- **R2-3.** `task_001_self_test.py` was run directly, not through a watcher: `P1_TESTS_001` would rewrite task 001's check receipt. 6 of 7 tests pass. The one failure, `test_current_tree_preflight_passes_and_reports_inventory_drift`, asserts an inventory drift count of 131 but finds 140. That drift comes from repository files outside `test/optimization/` and is unrelated to this change; `run_preflight` still calls `_index_report_hashes(root)` with the same default loader.
- **R2-4, R2-5, R2-6 (info, optional).** Not applied: they are optional wording or fallback changes, and applying them would require a third paid review.
  - R2-4: the overlap note does not name `test_missing_132_review_gate`.
  - R2-5: the INDEX fallback is not used when `research_sha256` is absent.
  - R2-6: the wording of the TASK_INPUTS-pin fixture's baseline.
- Both reviewers had read-only file tools and did not recompute hashes; this receipt's hashes were computed by the worker.
- `dispatch-2.json` lists `claude-opus-5-5` and `claude-haiku-5-5` as observed models. The routed review model was `claude-opus-5-5`; the CLI also used Haiku for auxiliary work. A JSON receipt alone cannot prove model identity.
- The prepared report `ARCHITECTURE_AND_SCOPE.md` is input evidence only, not proof that this implementation or review passed.
- No live provider tests were run beyond the plan's declared review dispatch. Nothing was written to user-global configuration, and nothing was installed, published or committed.
