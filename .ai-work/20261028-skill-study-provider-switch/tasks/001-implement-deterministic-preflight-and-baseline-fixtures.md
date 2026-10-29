---
task_id: "001"
status: "pending"
requirements: "R001,R004,R010,R011,R039,R040,R042"
dependencies: "none"
allowed_related_task_reads: "none"
---

# 001 — Implement deterministic preflight and baseline fixtures

Objective: Build offline preflight fixtures and baseline contracts without making a maximum-model planning review a global prerequisite.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned decision and pin baseline — Read docs/research/20261028-skill-optimization/prepared-research/ARCHITECTURE_AND_SCOPE.md. Confirm source applicability; do not repeat broad research.
- [ ] **S002** Implement change 1 — Implement the named deterministic contract from ARCHITECTURE_AND_SCOPE.md using the pinned inventory and current task catalog.
- [ ] **S003** Implement change 2 — Add negative fixtures for stale hashes, missing resources, unsupported CLI versions and accidental broad context loading.
- [ ] **S004** Implement change 3 — Keep missing authenticated providers as an explicit execution limitation, not a reason to fabricate review or fail local research preparation.
- [ ] **S005** Run declared regression checks — Run the declared targeted tests through the resource watcher. Implement every assigned acceptance case and preserve failures and limitations.
- [ ] **S006** Record acceptance evidence — Write the implementation receipt and outcome report with changed-file hashes, acceptance coverage and actual test logs. Leave unresolved work pending.

## Scope

In: Implement deterministic preflight and baseline fixtures
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `test/optimization/baseline_contracts.py`, `test/optimization/task_001_self_test.py`, `docs/research/20261028-skill-optimization/implementation/001-receipt.json`, `docs/research/20261028-skill-optimization/implementation/001-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/ARCHITECTURE_AND_SCOPE.md.
- Use only task 001 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/001-receipt.json.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.

## Acceptance

- Offline contract tests pass with no model call or user-global configuration write.
- Every fixture distinguishes historical baseline, current code and expected new behavior.
- Actual code changes and acceptance evidence are recorded.
- The prepared report is input evidence, not proof that this implementation or its independent review has passed.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_001`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_001`
