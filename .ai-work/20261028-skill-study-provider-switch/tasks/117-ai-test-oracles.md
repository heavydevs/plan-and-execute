---
task_id: "117"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "strong"
reasoning_effort: "high"
complexity: "high"
requirements: "R063, R064"
dependencies: "110, 112, 108, 114"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 117 — Implement contract-grounded AI test oracles and defect-detection checks

## Objective

Require independent expected-outcome contract, meaningful assertions, mapped risk, source and layer for each newly created/changed test.

## Requirements covered

- R063
- R064

## Complexity and atomicity

- Complexity: **high**
- Why this is one executable TODO: One shared runtime invariant and focused independent validation boundary.

## Context-isolation boundary

- Why one fresh worker context helps this whole TODO: Changes share one source/test contract that can be verified without reading unrelated tasks.
- Context that is genuinely shared by all subtasks:
- Only assigned research, relevant current source symbols and accepted dependency receipts.
- Concerns deliberately isolated into other TODOs:
- Do not load unrelated studies, historical transcripts, other provider guides or raw success logs.

## Isolation contract

This task definition and the exact execution-context files listed below are the only planning artifacts assigned to this worker. Read the task definition first, then read every assigned context file. Do not discover or open any other context file, `PLAN.md`, `TODO.md`, `manifest.json`, `orchestrator.config.json`, result files, logs, or unrelated task definitions. You may read repository source, tests, build files, and runtime output relevant to this task.

Another task definition may be opened only when one of the explicitly allowed task ids above is necessary to resolve a blocked dependency, ambiguity, or validation conflict. Record the task id and reason in the completion report.

## Assigned execution context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Assigned validated learnings

- None

These files are concise, immutable artifacts produced only after another TODO passed deterministic validation. Read exactly the assigned files, never a previous worker transcript or an unassigned learning file.

## Resumable subtask checklist

- [ ] **S001** — Inspect assigned architecture and relevant source symbols
  - Inspect assigned architecture and relevant source symbols using only task-specific research, current code and current acceptance evidence.
- [ ] **S002** — Implement bounded contract without duplicate framework
  - Implement bounded contract without duplicate framework using only task-specific research, current code and current acceptance evidence.
- [ ] **S003** — Integrate monitoring, permissions and route
  - Integrate monitoring, permissions and route using only task-specific research, current code and current acceptance evidence.
- [ ] **S004** — Execute adversarial focused validation
  - Execute adversarial focused validation using only task-specific research, current code and current acceptance evidence.
- [ ] **S005** — Record real product evidence or stay pending
  - Record real product evidence or stay pending using only task-specific research, current code and current acceptance evidence.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Implement contract-grounded AI test oracles and defect-detection checks

## Out of scope

- No second orchestrator, unrelated legacy test edits, runtime implementation in this planning amendment or paid model polling.

## Expected files

- skill/plan-and-execute/scripts/planctl.py
- skill/plan-and-execute/scripts/run_isolated.py
- skill/plan-and-execute/scripts/runner_contract.py
- skill/plan-and-execute/scripts/test_impact.py
- skill/plan-and-execute/scripts/test_failure_cycle.py
- skill/plan-and-execute/scripts/test_oracle.py
- skill/plan-and-execute/references/TEST_AUTHORING.md
- test/optimization/ai_test_quality_self_test.py
- docs/research/20261028-skill-optimization/implementation/117-receipt.json
- docs/research/20261028-skill-optimization/implementation/117-outcome.md

## Dependencies

- 110
- 112
- 108
- 114

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/research/20261028-skill-optimization/prepared-research/117-ai-test-oracle-quality.md only for this task; architecture and negative cases are mandatory.
- Require independent expected-outcome contract, meaningful assertions, mapped risk, source and layer for each newly created/changed test.
- Reuse 111 impact selector and 109 failure cycle; no duplicate runner; authorize legacy edits only via 113.
- Property/parameterized tests for field/rule matrices; risk-unique E2E for browser user journeys.
- Seeded defect or bounded incremental mutation proves critical oracles detect meaningful failures; no mandatory global mutation.
- Cover 45-field form, auth positive/negative, vacuous oracle, hallucinated API, flaky fixtures and repaired bug red/green.
- Use per-phase economic routing and indexed source scope; preserve capability floors and independent reviews.
- Produce actual receipt/outcome only after code, mapped checks and real review; no fabricated success.

## Acceptance criteria

- Verified: Require independent expected-outcome contract, meaningful assertions, mapped risk, source and layer for each newly created/changed test.
- Verified: Reuse 111 impact selector and 109 failure cycle; no duplicate runner; authorize legacy edits only via 113.
- Verified: Property/parameterized tests for field/rule matrices; risk-unique E2E for browser user journeys.
- Verified: Seeded defect or bounded incremental mutation proves critical oracles detect meaningful failures; no mandatory global mutation.
- Actual source-bound tests, negative fixtures and compact cost evidence establish behavior without inventing savings.
- No unauthorized provider/legacy test edits, leaked secrets, duplicate scheduler or lost global validation gate.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_117`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_117`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
