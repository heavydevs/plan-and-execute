---
task_id: "002"
status: "completed"
requirements: "R002,R007,R008,R009,R032,R035,R038,R040"
dependencies: "001"
allowed_related_task_reads: "none"
---

# 002 — Implement source and contract coverage checks

Objective: Turn the prepared architecture inventory into executable source/contract coverage checks and baseline regression fixtures.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [x] **S001** Read assigned decision and pin baseline — Read docs/research/20261028-skill-optimization/prepared-research/ARCHITECTURE_AND_SCOPE.md. Confirm source applicability; do not repeat broad research.
- [x] **S002** Implement change 1 — Import check_delivery.structural and check_delivery.verified_files for source/contract coverage; do not reimplement them.
- [x] **S003** Implement change 2 — Add only the negative fixtures delivery_gate_self_test.py lacks: unknown SOURCES id, report hash drift, requirement without consumer, task without prepared_report, missing 082 review gate.
- [x] **S004** Implement change 3 — Keep missing authenticated providers as an explicit execution limitation, not a reason to fabricate review or fail local research preparation.
- [x] **S005** Run declared regression checks — Run the declared targeted tests through the resource watcher. Implement every assigned acceptance case and preserve failures and limitations.
- [x] **S006** Record acceptance evidence — Write the implementation receipt and outcome report with changed-file hashes, acceptance coverage and actual test logs. Leave unresolved work pending.

## Scope

In: Implement source and contract coverage checks
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `test/optimization/baseline_contracts.py`, `test/optimization/task_002_self_test.py`, `docs/research/20261028-skill-optimization/implementation/002-receipt.json`, `docs/research/20261028-skill-optimization/implementation/002-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/ARCHITECTURE_AND_SCOPE.md.
- Use only task 002 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/002-receipt.json.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.

## Acceptance

- Offline contract tests pass with no model call or user-global configuration write.
- Every fixture distinguishes historical baseline, current code and expected new behavior.
- Actual code changes and acceptance evidence are recorded.
- A report record citing an unknown SOURCES id is rejected.
- A prepared report whose hash drifted from its pinned INDEX/TASK_INPUTS hash is rejected.
- A requirement with no consuming task is rejected.
- A task entry without a prepared_report is rejected.
- A plan missing a required 082 review-gate dependency is rejected.
- The prepared report is input evidence, not proof that this implementation or its independent review has passed.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_002`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_002`
