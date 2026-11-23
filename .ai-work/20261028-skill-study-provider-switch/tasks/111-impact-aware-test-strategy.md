---
task_id: "111"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "strong"
reasoning_effort: "high"
complexity: "high"
requirements: "R058, R059"
dependencies: "055, 059, 063, 098, 100, 108"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 111 — Implement risk-layered test authoring and deterministic impact-scoped validation

## Objective

Choose faithful test levels and conservative impact-selected task validations; retain complete global regression on final plan source.

## Requirements covered

- R058
- R059

## Complexity and atomicity

- Complexity: **high**
- Why this is one executable TODO: One cohesive implementation contract or independent correction gate with a shared acceptance boundary.

## Context-isolation boundary

- Why one fresh worker context helps this whole TODO: Scope and review need one verified code/test fingerprint.
- Context that is genuinely shared by all subtasks:
- Assigned research, current affected source and accepted prerequisite receipts only.
- Concerns deliberately isolated into other TODOs:
- Do not preload unrelated studies, entire test suites, raw logs or provider documentation.

## Isolation contract

This task definition and the exact execution-context files listed below are the only planning artifacts assigned to this worker. Read the task definition first, then read every assigned context file. Do not discover or open any other context file, `PLAN.md`, `TODO.md`, `manifest.json`, `orchestrator.config.json`, result files, logs, or unrelated task definitions. You may read repository source, tests, build files, and runtime output relevant to this task.

Another task definition may be opened only when one of the explicitly allowed task ids above is necessary to resolve a blocked dependency, ambiguity, or validation conflict. Record the task id and reason in the completion report.

## Assigned execution context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Assigned validated learnings

- None

These files are concise, immutable artifacts produced only after another TODO passed deterministic validation. Read exactly the assigned files, never a previous worker transcript or an unassigned learning file.

## Resumable subtask checklist

- [ ] **S001** — Inspect current source and assigned research
  - Read relevant paths and exact runner/authorization interfaces; research never proves code implemented.
- [ ] **S002** — Implement or independently audit core contract
  - Produce the stated deterministic implementation or genuine fresh independent code review.
- [ ] **S003** — Wire guarded routing and selected validation
  - Preserve resource monitor, existing provider routing, task/global testing boundaries and on-demand context.
- [ ] **S004** — Run functional, adversarial and negative checks
  - Exercise false-green, missing input, shared changes, authorization and current-source cases.
- [ ] **S005** — Record honest current-state evidence
  - Persist actual code/test hashes, check exits and real review provenance; otherwise remain pending.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Implement architecture, policy, safe selectors and required guarded integration.

## Out of scope

- No unrequested legacy test edits, full-suite per every unrelated task or false green.

## Expected files

- skill/plan-and-execute/scripts/run_isolated.py
- skill/plan-and-execute/scripts/planctl.py
- skill/plan-and-execute/scripts/runner_contract.py
- skill/plan-and-execute/scripts/resource_watch.py
- skill/plan-and-execute/scripts/service_map.py
- skill/plan-and-execute/references/WORKFLOW.md
- skill/plan-and-execute/references/TEST_RESOURCE_MONITORING.md
- skill/plan-and-execute/references/TOKEN_EFFICIENCY.md
- skill/plan-and-execute/scripts/test_impact.py
- skill/plan-and-execute/references/TEST_STRATEGY.md
- test/optimization/impact_aware_test_strategy_self_test.py
- docs/research/20261028-skill-optimization/implementation/111-receipt.json
- docs/research/20261028-skill-optimization/implementation/111-outcome.md

## Dependencies

- 055
- 059
- 063
- 098
- 100
- 108

## Allowed related task definitions

- None

## Implementation guidance

- Read implementation-ready `docs/research/20261028-skill-optimization/prepared-research/111-impact-aware-test-design-and-selection.md` only for this task; its alternatives, algorithms and fixtures are mandatory.
- Read only the assigned 111 research and relevant current source; write a lazy TEST_STRATEGY.md reference, never inflate the default worker prompt.
- Per behavior and risk, choose the smallest trustworthy unit/component, contract, integration or real-browser test with assertions, test IDs and explicit unique E2E reasons.
- Cover all validation rules with parameterized unit/API tests. E2E cover minimum-valid success, maximum-meaningful success and representative UI errors plus unique high-risk client cases.
- Use native verified exact argv selectors, git diff including untracked files, reverse dependencies/ownership, shared schema/auth and source/map/config fingerprints in test_impact.py.
- Broaden selection for unknown/dynamic graph, shared fixtures, global config, schema/auth, missing tests/shards, stale hash or zero selected; no silent green.
- Complete all mapped impacted task suites on current source; P057 collects all safe failures and repairs targeted cases; full global repository suites run at final integration or earlier on risk/CI requirement.
- Reuse existing monitor, job and runner controls and current tier routing; cache deterministic graph and pass bounded reasons/evidence, not all raw logs.
- Adversarial tests must include 45-rule form, 1000 tests with 100 E2E, cross-cutting shared change, hidden regression, crash/resume, missing selectors and honest measured overhead.
- Expose a selection contract (exact argv, reasons, source/map fingerprint) for 109 to consume later; do not import or assume test_failure_cycle.py.

## Acceptance criteria

- Each behavior has coverage at the cheapest faithful level with all expected field-validation cases in parameterized unit/API tests.
- E2E cover critical min/max success and representative UI errors without one test per input combination or a rigid quota.
- Changed/new tests, reverse dependents, contracts and relevant real-user E2E selected with exact verified runner argv and reasons.
- Unknown/shared/dynamic dependencies, missing shards, zero selectors, stale source and global auth/schema changes trigger broader checks or block.
- Focused failures alone never finish a task; all selected mapped tests pass on current code, and global all-suite passes at final plan source.
- Resource watcher, cancellation, bounded worker context and true nonzero exits remain intact.
- Adversarial selector/quality fixtures prove no false-green regression and no fabricated performance/token saving.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_111`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_111`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
