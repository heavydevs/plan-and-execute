---
task_id: "113"
status: "pending"
requirements: "R058,R060"
dependencies: "110,112"
allowed_related_task_reads: "none"
---

# 113 — Implement opt-in legacy or current-plan test audit and guarded refactoring

Objective: Create audit-only-by-default and user-authorized refactoring for legacy or provably plan-created/modified test cases.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Inspect current source and assigned research — Read relevant paths and exact runner/authorization interfaces; research never proves code implemented.
- [ ] **S002** Implement or independently audit core contract — Produce the stated deterministic implementation or genuine fresh independent code review.
- [ ] **S003** Wire guarded routing and selected validation — Preserve resource monitor, existing provider routing, task/global testing boundaries and on-demand context.
- [ ] **S004** Run functional, adversarial and negative checks — Exercise false-green, missing input, shared changes, authorization and current-source cases.
- [ ] **S005** Record honest current-state evidence — Persist actual code/test hashes, check exits and real review provenance; otherwise remain pending.

## Scope

In: Implement architecture, policy, safe selectors and required guarded integration.
Out: No automatic existing-project test refactor or forged edit consent.
Files: `skill/plan-and-execute/SKILL.md`, `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/planctl.py`, `skill/plan-and-execute/scripts/runner_contract.py`, `skill/plan-and-execute/scripts/resource_watch.py`, `skill/plan-and-execute/scripts/service_map.py`, `skill/plan-and-execute/references/WORKFLOW.md`, `skill/plan-and-execute/references/TEST_RESOURCE_MONITORING.md`, `skill/plan-and-execute/references/TOKEN_EFFICIENCY.md`, `skill/plan-and-execute/scripts/test_impact.py`, `skill/plan-and-execute/scripts/test_audit.py`, `skill/plan-and-execute/references/TEST_REVIEW_REFACTOR.md`, `test/optimization/test_suite_refactor_scope_self_test.py`, `docs/research/20261028-skill-optimization/implementation/113-receipt.json`, `docs/research/20261028-skill-optimization/implementation/113-outcome.md`

## Guidance

- Read implementation-ready `docs/research/20261028-skill-optimization/prepared-research/113-opt-in-test-suite-review-refactor.md` only for this task; its alternatives, algorithms and fixtures are mandatory.
- Read only assigned 113 architecture, 111 selection contract, and current plan provenance; lazily load TEST_REVIEW_REFACTOR.md only on explicit user review/refactor request.
- Mode A repository tests: inspect or refactor legacy test suite only after explicit user request; audit-only by default; modifying tests needs separately explicit edit permission.
- Mode B current-plan tests: review only on explicit request; prove individual test-case ownership using original git base, task receipts, diffs and code hashes; mixed legacy files preserve unowned test-case ranges.
- Implement deterministic test_audit.py inventory and bounded reports for duplicate expensive E2E, brittle selectors, gaps, flaky fixtures and direct/indirect coverage; unknown is not classified as safe.
- Untrusted CLI flags, model prompts or source comments cannot confer edit authorization; stale ownership, mixed shared fixtures, symlink/traversal, concurrent plan or unknown case boundaries fail closed.
- Before removing scoped redundant E2E, add equivalent smaller unit/contract/integration coverage, run old+new tests, retain unique browser/security behaviors, preserve rollback and full final gate.
- No production-code edits, disabled tests, assertion weakening, bypassed CI, unsanctioned repository-wide test migration or separate test orchestrator.
- Reuse existing impact selector, P057 failure cycle, watcher and model routes; bounded per-case findings and actual timing/token evidence only.

## Acceptance

- Ordinary feature work never activates a legacy test suite audit/refactor.
- Existing repository test review/refactor requires explicit user intent; audit_only cannot modify tests.
- Current-plan-only review uses reliable task-proven case ownership and is audit-only unless edits are expressly authorized.
- Current-plan edits preserve unrelated legacy cases in mixed files byte-for-byte; unknown provenance blocks writes.
- Symlink/traversal, stale hashes, forged flags, concurrent plan or out-of-scope fixtures fail closed.
- Equivalent cheaper tests must pass before removal of redundant scoped E2E; unique UI/security flows and final regression remain.
- No production-code, skip/quarantine or CI weakening; precise case report and genuine before/after measurements provided.
- 500-legacy-E2E no-op, scoped mixed-file, read-only review, permission spoof and rollback fixture cases pass.
- node tools/validate-skill.js passes.
- SKILL.md stays <= 7167 normalized characters (baseline 6826 x 1.05) with at most one lazy pointer line.
- TOKEN_EFFICIENCY.md stays <= 10000 characters (currently 9975); 113 detail lives in TEST_REVIEW_REFACTOR.md.
- The orchestrator enforces audit-only and ownership limits: test files are hashed before/after and any change outside the authorized case set is rolled back and rejected.
- A fixture where a full-access unsandboxed worker writes outside the authorized case set anyway is rolled back and rejected.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_113`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_113`
