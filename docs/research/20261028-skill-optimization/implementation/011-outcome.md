# 011 — Review and correct adaptive internal and external study: outcome

Task `011` reviews task `010` (feature `F003`). The prepared report `prepared-research/010-adaptive-study.md` (LF sha256 `f837c59d…`, matching `TASK_INPUTS.json`) was used as input only. It does not prove that the implementation or its review passed.

## Independent review

All reviews ran through `review_dispatch.py` in the foreground. Each reviewer was fresh, read-only and max tier. Codex (`gpt-6.2-sol`) was cooled down for quota, so Claude reviewed.

| Dispatch | Reviewer | Session | Verdict | Blocking |
|---|---|---|---|---|
| `reviews/011/dispatch-1.json` (`5c5fca81…`) | claude / claude-opus-5-5 / xhigh | `d4e7920f-…` | changes_requested (13 findings) | 3 high |
| dispatch 2 | codex quota, then claude | — | no evidence written | — |
| `reviews/011/dispatch-3.json` (`0947e8c3…`) | claude / claude-opus-5-5 / xhigh | `15c28c29-6ba9-4ca7-ba39-86b56f430cee` | **approved** (9 findings) | 0 |

**Dispatch 2 failed because of a bug in the dispatch helper, not because of the code under review.** Its Claude reviewer was still running and its heartbeat was fresh, about 4 s old. `review_dispatch.py` `wait_attempt` still marked it `abandoned_no_heartbeat`. When `run.json` cannot be read for a moment (a Windows `os.replace` race), the helper uses `spawned_at` as the last heartbeat, which makes any reviewer older than 60 s look stale. The orphaned reviewer was stopped and dispatch 3 reran with the same brief. Dispatch 2 has no evidence and is not claimed.

Dispatch 3 reviewed the final hashes recorded in the receipt: `studyctl.py` `dc4b944c…`, `study_self_test.py` `d0e6c32d…`, `adaptive_study_self_test.py` `7121f82b…` and `ADAPTIVE_STUDY.md` `a345f363…`. These files did not change after the review.

## Corrections (dispatch-1 findings)

- **F01 (high, resolved).** Recommendation guards now follow the recommendation's own `claim_type`. Only `capability_probe` inherits `probe_required`, so a quota or verified-interface recommendation can no longer bypass the AC05/AC06 guards by linking to a probe question.
- **F02 (high, resolved).** `resolve_source_dating` now handles both study sources and the ledger `source_register`. It rejects an undated or placeholder `version_or_date` unless the source declares `affects_cli_behavior` or uses the `cli_interface` domain. This restores the strict v1/v2 contract, and every real repository value still passes.
- **F03 (high, resolved).** A contradicted question can no longer be `resolved` or `assumed` without `probe_verified`. `probe_verified` now needs a `capability_probe` and a cited internal or `observed_repository_behavior` source. `validate_ready_state` also rejects contradictions that have no probe.
- **F04 (medium, partly fixed).** The prepared-report waiver now requires `source_ids` and never applies to `security_sensitive` or `conflicting_evidence` triggers. Checking that the report file exists and that its hash matches is still deferred.
- **F05 (medium, partly fixed).** `evidence_origin` is now an enumerated field. A path under `prepared-research/` is forced to `prepared_research`. A receipt must be a separate relative `.json` path. Checking that the receipt exists is left to the delivery gate.
- **F06 (medium, resolved).** Untargeted signals raise `StudyError`. `unmatched_signals` is reported. Report-only matching now covers every signal kind.
- **F07 (medium, resolved).** A high-impact resolved question needs an internal or inspected citation, enforced both in the study ready state and in the ledger stopping rule. `abstract_only` sources can no longer be `verified_source_fact`.
- **F08 (medium, resolved).** Only an inspected quota or account source counts as quota evidence.
- **F09 (low, partly fixed).** Invalidated sources are now only the targeted ones. Per-product version matching is deferred.
- **F10 (low, resolved).** `research_revision` and `version_sensitive` are now type-checked.
- **F11 and F12 (low).** Deferred, not changed.
- **F13 (low).** This applies to the 010 receipt, which is outside this task's write scope. AC08-style non-proof coverage is listed under Acceptance below.

Each fix has a counterexample test: 6 new adaptive tests and 3 extended or new study tests. A mutation check, which restored the pre-fix F01 and F03 logic in a scratch copy, made the new F01 and F03 tests fail.

## Open non-blocking findings (dispatch 3; left pending)

- **M1 (medium).** An access date written into `version_or_date` (for example "Retrieved 2026-10-28") counts as a version, so CLI documentation dated that way is never flagged for refresh.
- **M2 (medium).** An external source labelled `observed_repository_behavior` can satisfy `probe_verified`, whatever its reading scope.
- **M3 (medium).** A recommendation does not inherit a `subscription_quota` claim from its question. Explicitly setting a `general` domain avoids the quota guard.
- **M4 (medium).** Ledger readiness ignores its own `invalidation_result`. `consumed_reports` also lists invalidated reports.
- **M5 (medium).** The 010 receipt and logs predate the corrections. Fresh 011 logs now cover the corrected suites.
- **L6–L9 (low).** These cover:
  - invalidation precision for reports that have linked recommendations;
  - the case-sensitive `prepared-research/` marker;
  - located-only guards applying only to `resolved` questions, and the waiver not being tied to a task;
  - render and `version_or_date` compatibility for previously attached plain-`studyctl.py` studies.

## Acceptance

- **AC01.** The reviewer's provider, model and effort, the fresh session and the reviewed-input hashes are recorded from `RECEIPT_REVIEWER` (dispatch 3).
- **AC02.** No critical or high finding remains open. The dispatch-1 highs F01–F03 are fixed and tested, and dispatch 3 has 0 blocking findings. The 010 acceptance cases AC01–AC07 and prepared-research non-proof are covered by the 17 adaptive tests and the extended study tests in the fresh 011 logs.
- **AC03.** `check_delivery.py` rejects a reused or fabricated review receipt: it checks the dispatch hash, session, task directory, reviewed-input hashes and claims by other receipts. `delivery_gate_self_test.py` passed (55 tests, 1 skipped), and so did `review_dispatch_self_test.py`, including its reused-session refusal test (14 tests, 1 skipped).
- **AC04.** The reviewer was max tier, not frontier. The gate accepts a frontier reviewer only after at least two recorded functional max-review failures, and rejects a reused session or dispatch. The frontier cases in `delivery_gate_self_test.py` passed.

## Validation

`resource_watch.py run --validation P1_TESTS_011` exited 0 and wrote `011-checks.json` with run `20261120T102111-14436`:

1. `python test/optimization/adaptive_study_self_test.py`: exit 0, 17/17 (`logs/011/20261120T102111-14436/check-01.log`).
2. `python skill/plan-and-execute/scripts/study_self_test.py`: exit 0 (`check-02.log`).
3. `python skill/plan-and-execute/scripts/artifact_concision_self_test.py`: exit 0 (`check-03.log`).

The service map was reconciled with `service_map.py stamp --confirm-reconciled`. The two test files changed content only, so there are no new resources or checks and the validation IDs are unchanged. `node tools/validate-skill.js` also exited 0.

## Limits

- No live authenticated provider probe or quota benchmark was run.
- The reviewer read the code and did not execute the tests. The test results come from this worker's resource-watch run.
- The dispatch-helper stale-heartbeat race lives in `review_dispatch.py`, outside this task's write scope, so it is not fixed here.
