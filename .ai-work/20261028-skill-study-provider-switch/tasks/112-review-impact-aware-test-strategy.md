---
task_id: "112"
status: "pending"
requirements: "R058,R059"
dependencies: "111"
allowed_related_task_reads: "none"
---

# 112 — Independently review and correct test hierarchy and impact selector

Objective: Independently challenge 111 selection soundness, browser coverage, source fingerprints and plan-wide final suite.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Inspect current source and assigned research — Read relevant paths and exact runner/authorization interfaces; research never proves code implemented.
- [ ] **S002** Dispatch a fresh max-qualified review — Run `python docs/plans/20261028-skill-optimization/support/review_dispatch.py --repo-root . --task 112` in the foreground (rerun on exit 75); use only its DISPATCH line and compact findings.
- [ ] **S003** Audit routing, validation wiring and context — Audit routing, validation wiring and context boundaries of the final 111 code against the selection contract.
- [ ] **S004** Correct critical/high defects and rerun checks — Correct only critical/high defects, rerun functional, adversarial and negative checks and obtain approval on the final hashes.
- [ ] **S005** Record honest current-state evidence — Persist actual code/test hashes, check exits and real review provenance; otherwise remain pending.

## Scope

In: Independent security/performance/correctness review of preceding implementation.
Out: No unrequested legacy test edits, full-suite per every unrelated task or false green.
Files: `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/planctl.py`, `skill/plan-and-execute/scripts/runner_contract.py`, `skill/plan-and-execute/scripts/resource_watch.py`, `skill/plan-and-execute/scripts/service_map.py`, `skill/plan-and-execute/references/WORKFLOW.md`, `skill/plan-and-execute/references/TEST_RESOURCE_MONITORING.md`, `skill/plan-and-execute/references/TOKEN_EFFICIENCY.md`, `skill/plan-and-execute/scripts/test_impact.py`, `skill/plan-and-execute/references/TEST_STRATEGY.md`, `test/optimization/impact_aware_test_strategy_self_test.py`, `docs/research/20261028-skill-optimization/implementation/112-receipt.json`, `docs/research/20261028-skill-optimization/implementation/112-outcome.md`

## Guidance

- Read implementation-ready `docs/research/20261028-skill-optimization/prepared-research/111-impact-aware-test-design-and-selection.md` only for this task; its alternatives, algorithms and fixtures are mandatory.
- Use a genuinely independent fresh max-qualified review of real final 111 source/tests/receipt, recording provider, model, effort and reviewed hashes.
- Seed regressions outside naive graph, dynamic imports, changed auth/schema, zero selected, missing shards, shared test fixtures and stale caches.
- Review faithfully covered min/max/browser validation flows, no rigid E2E quota, actual mapped task suites vs final global suite, security/privacy and token efficiency.
- Correct every critical/high finding; rerun required current-code tests and obtain a fresh approval on final hashes. Never simulate a reviewer.
- Review only via review_dispatch.py (synchronous; max route; writes dispatch evidence); fix blocking findings, rerun declared checks, re-dispatch if a reviewed file changed, copy its RECEIPT_REVIEWER fields into the receipt.
- Never launch background or asynchronous agents or processes: this headless session ends when you stop calling tools, so anything unfinished is lost.

## Acceptance

- Real fresh independent reviewer and dispatch metadata match final 111 source/test hashes.
- Uncertain dependency graph, empty selection, changed auth, dynamic imports and shards cannot falsely pass.
- All behavior and critical browser flows retain credible coverage without unnecessary E2E copies.
- Mapped task validation and complete global plan-final gate remain mandatory and current-source bound.
- Security, performance, routing and token context reviewed; high/critical issues corrected and genuinely re-reviewed.
- A frontier (Fable 5.2 / Astra 6.2) reviewer is accepted only with recorded repeated max-review failure; a reused review session or dispatch is rejected.
- Every 2026-11-20 acceptance addition of task 111 has actual test evidence on the final reviewed hashes.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_112`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_112`
