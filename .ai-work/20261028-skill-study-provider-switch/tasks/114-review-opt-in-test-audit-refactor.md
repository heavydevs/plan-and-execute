---
task_id: "114"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "max"
reasoning_effort: "xhigh"
complexity: "high"
requirements: "R058, R060"
dependencies: "113"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 114 — Independently review and correct test-audit authorization and ownership

## Objective

Independently challenge 113's consent, mixed-file test ownership, coverage and fail-closed mutation boundaries.

## Requirements covered

- R058
- R060

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
  - Run `python docs/plans/20261028-skill-optimization/support/review_dispatch.py --repo-root . --task 114` in the foreground (rerun on exit 75); use only its DISPATCH line and compact findings.
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

- Independent security/performance/correctness review of preceding implementation.

## Out of scope

- No automatic existing-project test refactor or forged edit consent.

## Expected files

- skill/plan-and-execute/SKILL.md
- skill/plan-and-execute/scripts/run_isolated.py
- skill/plan-and-execute/scripts/planctl.py
- skill/plan-and-execute/scripts/runner_contract.py
- skill/plan-and-execute/scripts/resource_watch.py
- skill/plan-and-execute/scripts/service_map.py
- skill/plan-and-execute/references/WORKFLOW.md
- skill/plan-and-execute/references/TEST_RESOURCE_MONITORING.md
- skill/plan-and-execute/references/TOKEN_EFFICIENCY.md
- skill/plan-and-execute/scripts/test_impact.py
- skill/plan-and-execute/scripts/test_audit.py
- skill/plan-and-execute/references/TEST_REVIEW_REFACTOR.md
- test/optimization/test_suite_refactor_scope_self_test.py
- docs/research/20261028-skill-optimization/implementation/114-receipt.json
- docs/research/20261028-skill-optimization/implementation/114-outcome.md

## Dependencies

- 113

## Allowed related task definitions

- None

## Implementation guidance

- Read implementation-ready `docs/research/20261028-skill-optimization/prepared-research/113-opt-in-test-suite-review-refactor.md` only for this task; its alternatives, algorithms and fixtures are mandatory.
- Invoke independent fresh maximum-qualified reviewer on final 113 diff/receipt, with genuine provider, model, effort and source hashes.
- Probe review-only write attempts, generic prompt activation, forged edit flag, old plan receipt, moved/mixed test file, concurrent owner and unsafe symlink.
- Verify unknown source/case provenance prevents edits and unrelated legacy sections remain byte-stable, including shared fixtures.
- Verify cheaper replacement preserves all expected checks, critical E2E and final full suite; investigate performance/security and prompt loading.
- Correct critical/high findings and re-review current final code; preserve genuine failure/limitation evidence.
- Review only via review_dispatch.py (synchronous; max route; writes dispatch evidence); fix blocking findings, rerun declared checks, re-dispatch if a reviewed file changed, copy its RECEIPT_REVIEWER fields into the receipt.
- Never launch background or asynchronous agents or processes: this headless session ends when you stop calling tools, so anything unfinished is lost.

## Acceptance criteria

- Real independent fresh reviewer with final 113 source/test/review receipt hashes and dispatch provenance.
- Generic requests, audit-only and forged flags cannot trigger refactoring or writes.
- Current-plan-only case ownership is enforced even inside mixed legacy test files.
- Legacy-suite migration requires explicitly authorized edit scope and preserves required coverage.
- Stale/ambiguous cases, path escape and concurrent edits fail closed; test evidence remains source-pinned.
- Real high/critical findings are corrected and re-reviewed without model simulation or fictitious time savings.
- A frontier (Fable 5.2 / Astra 6.2) reviewer is accepted only with recorded repeated max-review failure; a reused review session or dispatch is rejected.
- Every 2026-11-20 acceptance addition of task 113 has actual test evidence on the final reviewed hashes.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_114`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_114`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
