---
task_id: "005"
status: "completed"
requirements: "R002,R003,R004,R039,R042,R044"
dependencies: "004"
allowed_related_task_reads: "none"
---

# 005 — Review and correct shared acceptance fixtures

Objective: Independently review task004 and correct fixture or context-selection defects before its acceptance.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [x] **S001** Read assigned decision and pin baseline — Read docs/research/20261028-skill-optimization/prepared-research/ARCHITECTURE_AND_SCOPE.md. Confirm source applicability; do not repeat broad research.
- [x] **S002** Dispatch the independent reviewer — Run `python docs/plans/20261028-skill-optimization/support/review_dispatch.py --repo-root . --task 005` in the foreground (rerun on exit 75); use only its DISPATCH line and compact findings.
- [x] **S003** Implement change 2 — Correct every blocking finding or leave the gate incomplete with a recorded reason.
- [x] **S004** Implement change 3 — Re-run declared checks after corrections and pin the final reviewed source state.
- [x] **S005** Run declared regression checks — Run the declared targeted tests through the resource watcher. Implement every assigned acceptance case and preserve failures and limitations.
- [x] **S006** Record acceptance evidence — Write the implementation receipt and outcome report with changed-file hashes, acceptance coverage and actual test logs. Leave unresolved work pending.

## Scope

In: Review and correct shared acceptance fixtures
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `test/optimization/shared_fixtures.py`, `test/optimization/task_004_self_test.py`, `docs/research/20261028-skill-optimization/implementation/005-receipt.json`, `docs/research/20261028-skill-optimization/implementation/005-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/ARCHITECTURE_AND_SCOPE.md.
- Use only task 005 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/005-receipt.json.
- Review only via review_dispatch.py (synchronous; max route; writes dispatch evidence); fix blocking findings, rerun declared checks, re-dispatch if a reviewed file changed, copy its RECEIPT_REVIEWER fields into the receipt.
- Reuse the predecessor tests; add a new test only for a concrete uncovered finding. Do not make gratuitous code changes for a clean review.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Never launch background or asynchronous agents or processes: this headless session ends when you stop calling tools, so anything unfinished is lost.

## Acceptance

- Actual fresh reviewer provider/model/effort and reviewed input hashes are recorded.
- No unresolved critical/high finding remains; the assigned acceptance cases have actual test evidence.
- A reused or fabricated review receipt is rejected.
- A frontier (Fable 5.2 / Astra 6.2) reviewer is accepted only with recorded repeated max-review failure; a reused review session or dispatch is rejected.
- Every 2026-11-20 acceptance addition of task 004 has actual test evidence on the final reviewed hashes.
- The prepared report is input evidence, not proof that this implementation or its independent review has passed.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_005`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_005`
