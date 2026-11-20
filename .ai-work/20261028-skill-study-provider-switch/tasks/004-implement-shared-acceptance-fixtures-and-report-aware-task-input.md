---
task_id: "004"
status: "completed"
requirements: "R002,R003,R004,R044"
dependencies: "001"
allowed_related_task_reads: "none"
---

# 004 — Implement shared acceptance fixtures and report-aware task inputs

Objective: Use the prepared inventory to implement shared fake-provider fixtures and bounded report-aware implementation inputs.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [x] **S001** Read assigned decision and pin baseline — Read docs/research/20261028-skill-optimization/prepared-research/ARCHITECTURE_AND_SCOPE.md. Confirm source applicability; do not repeat broad research.
- [x] **S002** Implement change 1 — Build one shared fake-provider fixture (claude/codex/antigravity argv; success, quota, auth and functional outcomes) that starts no subprocess and makes no network call.
- [x] **S003** Implement change 2 — Implement a report-aware loader that returns only the entry's prepared_reports/input_contract paths and rejects unlisted reports and the task's own not-yet-created files.
- [x] **S004** Implement change 3 — Add a credit-exhaustion fixture classified distinctly from auth and functional failures.
- [x] **S005** Run declared regression checks — Run the declared targeted tests through the resource watcher. Implement every assigned acceptance case and preserve failures and limitations.
- [x] **S006** Record acceptance evidence — Write the implementation receipt and outcome report with changed-file hashes, acceptance coverage and actual test logs. Leave unresolved work pending.

## Scope

In: Implement shared acceptance fixtures and report-aware task inputs
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `test/optimization/shared_fixtures.py`, `test/optimization/task_004_self_test.py`, `docs/research/20261028-skill-optimization/implementation/004-receipt.json`, `docs/research/20261028-skill-optimization/implementation/004-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/ARCHITECTURE_AND_SCOPE.md.
- Use only task 004 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/004-receipt.json.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.

## Acceptance

- One shared fake-provider fixture covers claude/codex/antigravity argv with success, quota, auth and functional outcomes and starts no subprocess or network call.
- The report-aware loader returns only the entry's prepared_reports/input_contract paths and rejects unlisted reports and the task's own not-yet-created files.
- A credit-exhaustion fixture is classified as availability, distinct from auth and functional failures.
- Offline contract tests pass with no model call or user-global configuration write.
- Actual code changes and acceptance evidence are recorded.
- The prepared report is input evidence, not proof that this implementation or its independent review has passed.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_004`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_004`
