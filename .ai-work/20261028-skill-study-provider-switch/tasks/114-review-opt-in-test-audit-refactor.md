---
task_id: "114"
status: "pending"
requirements: "R058,R060"
dependencies: "113"
allowed_related_task_reads: "none"
---

# 114 — Independently review and correct test-audit authorization and ownership

Objective: Independently challenge 113's consent, mixed-file test ownership, coverage and fail-closed mutation boundaries.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`
- Read the assigned implementation-ready architecture only when working on this task.

## Validated learnings

- None. Research is not product code or independent acceptance.

## Checkpoints

- [ ] **S001** Inspect current source and assigned research — Read relevant paths and exact runner/authorization interfaces; research never proves code implemented.
- [ ] **S002** Implement or independently audit core contract — Produce the stated deterministic implementation or genuine fresh independent code review.
- [ ] **S003** Wire guarded routing and selected validation — Preserve resource monitor, existing provider routing, task/global testing boundaries and on-demand context.
- [ ] **S004** Run functional, adversarial and negative checks — Exercise false-green, missing input, shared changes, authorization and current-source cases.
- [ ] **S005** Record honest current-state evidence — Persist actual code/test hashes, check exits and real review provenance; otherwise remain pending.

## Scope

**In:** Independent security/performance/correctness review of preceding implementation.

**Out:** No automatic existing-project test refactor or forged edit consent.

**Expected files:** `skill/plan-and-execute/SKILL.md`, `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/planctl.py`, `skill/plan-and-execute/scripts/runner_contract.py`, `skill/plan-and-execute/scripts/resource_watch.py`, `skill/plan-and-execute/scripts/service_map.py`, `skill/plan-and-execute/references/WORKFLOW.md`, `skill/plan-and-execute/references/TEST_RESOURCE_MONITORING.md`, `skill/plan-and-execute/references/TOKEN_EFFICIENCY.md`, `skill/plan-and-execute/scripts/test_impact.py`, `skill/plan-and-execute/scripts/test_audit.py`, `skill/plan-and-execute/references/TEST_REVIEW_REFACTOR.md`, `test/optimization/test_suite_refactor_scope_self_test.py`, `docs/research/20261028-skill-optimization/implementation/114-receipt.json`, `docs/research/20261028-skill-optimization/implementation/114-outcome.md`

## Implementation architecture and instructions

- Read implementation-ready `docs/research/20261028-skill-optimization/prepared-research/113-opt-in-test-suite-review-refactor.md` only for this task; its alternatives, algorithms and fixtures are mandatory.
- Invoke independent fresh maximum-qualified reviewer on final 113 diff/receipt, with genuine provider, model, effort and source hashes.
- Probe review-only write attempts, generic prompt activation, forged edit flag, old plan receipt, moved/mixed test file, concurrent owner and unsafe symlink.
- Verify unknown source/case provenance prevents edits and unrelated legacy sections remain byte-stable, including shared fixtures.
- Verify cheaper replacement preserves all expected checks, critical E2E and final full suite; investigate performance/security and prompt loading.
- Correct critical/high findings and re-review current final code; preserve genuine failure/limitation evidence.

## Acceptance criteria

- Real independent fresh reviewer with final 113 source/test/review receipt hashes and dispatch provenance.
- Generic requests, audit-only and forged flags cannot trigger refactoring or writes.
- Current-plan-only case ownership is enforced even inside mixed legacy test files.
- Legacy-suite migration requires explicitly authorized edit scope and preserves required coverage.
- Stale/ambiguous cases, path escape and concurrent edits fail closed; test evidence remains source-pinned.
- Real high/critical findings are corrected and re-reviewed without model simulation or fictitious time savings.

## Validate via owned watcher

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_114`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_114`

**State: pending.** No code, suite migration or independent model review is completed by preparing this task.
