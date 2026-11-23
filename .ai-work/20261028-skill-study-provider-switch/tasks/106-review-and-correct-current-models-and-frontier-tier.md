---
task_id: "106"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "max"
reasoning_effort: "xhigh"
complexity: "high"
requirements: "R055"
dependencies: "105"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 106 — Review and correct updated model catalog and frontier routing

## Objective

Review and correct updated model catalog and frontier routing

## Requirements covered

- R055

## Complexity and atomicity

- Complexity: **high**
- Why this is one executable TODO: One feature or independent correction gate.

## Context-isolation boundary

- Why one fresh worker context helps this whole TODO: One reviewer context holds the 105 diff, the pinned v8 baseline and every negative case needed to approve or correct it.
- Context that is genuinely shared by all subtasks:
- Assigned P054/P055 research and task-specific evidence only.
- Concerns deliberately isolated into other TODOs:
- No unrelated transcript or duplicated orchestration

## Isolation contract

This task definition and the exact execution-context files listed below are the only planning artifacts assigned to this worker. Read the task definition first, then read every assigned context file. Do not discover or open any other context file, `PLAN.md`, `TODO.md`, `manifest.json`, `orchestrator.config.json`, result files, logs, or unrelated task definitions. You may read repository source, tests, build files, and runtime output relevant to this task.

Another task definition may be opened only when one of the explicitly allowed task ids above is necessary to resolve a blocked dependency, ambiguity, or validation conflict. Record the task id and reason in the completion report.

## Assigned execution context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Assigned validated learnings

- None

These files are concise, immutable artifacts produced only after another TODO passed deterministic validation. Read exactly the assigned files, never a previous worker transcript or an unassigned learning file.

## Resumable subtask checklist

- [ ] **S001** — Read the 105 diff and evidence
  - Read task 105 actual diff, receipts, source hashes and official vendor evidence; do not trust proposed model IDs without an installed CLI check.
- [ ] **S002** — Run an independent max-qualified review
  - Run `python docs/plans/20261028-skill-optimization/support/review_dispatch.py --repo-root . --task 106` in the foreground (rerun on exit 75); use only its DISPATCH line and compact findings. Focus: providers, catalog freshness, tier monotonicity, frontier gate, budgets.
- [ ] **S003** — Correct findings and rerun
  - Correct invalid IDs, unsupported effort flags, default frontier promotions, cost-accounting errors and any critical/high findings; rerun tests and record genuine independent review.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Review and correct updated model catalog and frontier routing

## Out of scope

- No second plan, OS policy changes or unauthorised provider charges

## Expected files

- skill/plan-and-execute/scripts/routingctl.py
- skill/plan-and-execute/scripts/model_catalog.py
- skill/plan-and-execute/scripts/model_catalogctl.py
- skill/plan-and-execute/scripts/workload_routing.py
- skill/plan-and-execute/scripts/routing_config.py
- skill/plan-and-execute/scripts/availability.py
- skill/plan-and-execute/references/MODEL_ROUTING.md
- skill/plan-and-execute/references/MODEL_MAPPING.md
- skill/plan-and-execute/references/MODEL_CATALOG.md
- skill/plan-and-execute/references/ROUTING_CONFIG.md
- skill/plan-and-execute/references/PLAN_SPEC.md
- test/optimization/frontier_model_tier_self_test.py
- skill/plan-and-execute/references/MODEL_ROUTING_CLAUDE.md
- skill/plan-and-execute/references/MODEL_ROUTING_CODEX.md
- skill/plan-and-execute/scripts/run_isolated.py
- docs/research/20261028-skill-optimization/implementation/106-receipt.json
- docs/research/20261028-skill-optimization/implementation/106-outcome.md

## Dependencies

- 105

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/research/20261028-skill-optimization/prepared-research/105-frontier-model-routing-20261112.md
- Follow tasks/106-review-and-correct-current-models-and-frontier-tier.md and TASK_INPUTS.json
- Review only via review_dispatch.py (synchronous; max route; writes dispatch evidence); fix blocking findings, rerun declared checks, re-dispatch if a reviewed file changed, copy its RECEIPT_REVIEWER fields into the receipt.
- Record actual receipts and outcomes, leave pending until verified.
- Never launch background or asynchronous agents or processes: this headless session ends when you stop calling tools, so anything unfinished is lost.

## Acceptance criteria

- Real independent review and source hashes captured; unresolved critical/high issues block integration.
- The 105 diff is verified against the pinned refresh baseline hash; files outside the 105 scope are unchanged.
- Every S003/S005 negative case is re-run: lift, ladder, selector, stagnation floor, planctl tiers, quota, implementation role, and Codex credit exhaustion -> Fable with no escalation.
- Legacy L1–L5 routes and old persisted configuration stable; L6 enabled paths select only exact observed compatible models.
- No unapproved paid API fallback or model tier escalation on environment, timeout, quota or weak evidence.
- A frontier (Fable 5.2 / Astra 6.2) reviewer is accepted only with recorded repeated max-review failure; a reused review session or dispatch is rejected.
- Every 2026-11-20 acceptance addition of task 105 has actual test evidence on the final reviewed hashes.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_106`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_106`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
