---
task_id: "105"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "strong"
reasoning_effort: "high"
complexity: "high"
requirements: "R055"
dependencies: "021, 025, 027, 047, 081, 100"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 105 — Add the opt-in frontier tier L6/F6 on top of map 2026-11-20-v8

## Objective

Add an opt-in frontier tier (aliases L6/F6) above max for architecture and code review only, outside TIER_ORDER, without changing the v8 map, routes or argv while it is disabled.

## Requirements covered

- R055

## Complexity and atomicity

- Complexity: **high**
- Why this is one executable TODO: One feature or independent correction gate.

## Context-isolation boundary

- Why one fresh worker context helps this whole TODO: Frontier constants, the ladder_exhausted gate and every rejection path share one routing invariant that must be implemented and tested together.
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

- [ ] **S001** — Read the 2026-11-20 refresh and pin its baseline
  - Read docs/research/MODEL_REFRESH_20261120.md (it overrides prepared report 105 on conflict; report 105 stays hash-pinned and unedited); record a baseline hash of the uncommitted refresh files so 106 can separate the 105 diff.
- [ ] **S002** — Keep the v8 refresh byte-identical
  - Do not redo the refresh: CURRENT_MODELS, ESCALATION_LADDERS, MODEL_MAP_VERSION=2026-11-20-v8, bootstrap catalog and Gemini 4 preset stay byte-identical while L6 is off. Verify only observed ids: claude-fable-5-2, gpt-6.2-astra; Carbon is not listed.
- [ ] **S003** — Add FRONTIER_TIER outside TIER_ORDER
  - Add FRONTIER_TIER='frontier' (aliases l6/f6) outside TIER_ORDER plus an opt-in FRONTIER_MODELS with its own version, so apply_current_models, lift_tier, provider_ladder, selector min(eligible), the stagnation floor and planctl.VALID_TIERS never reach it.
- [ ] **S004** — Define frontier candidates, roles and order
  - Candidates: claude-fable-5-2 (high; xhigh only where measured), gpt-6.2-astra (high/xhigh, never ultra), gemini-4-carbon-* only if agy models lists it. Roles: architecture, code_review. Order Codex > Claude > Antigravity; Codex credit exhaustion skips to Fable.
- [ ] **S005** — Gate entry at ladder_exhausted with approval
  - Offer frontier only at the ladder_exhausted event (run_isolated.py) with a recorded task-scoped approval after >=2 semantic/plan_defect failures at the max/xhigh rung; environmental, budget, timeout_ceiling, quota and unknown never count.
- [ ] **S006** — Benchmark only after owner confirmation
  - Run benchmarks only after owner confirmation; Astra stays unmeasured; cite the secondary replay in MODEL_REFRESH_20261120.md and record cost/quality unknowns honestly.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Add the opt-in frontier tier L6/F6 on top of map 2026-11-20-v8

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
- docs/research/20261028-skill-optimization/implementation/105-receipt.json
- docs/research/20261028-skill-optimization/implementation/105-outcome.md

## Dependencies

- 021
- 025
- 027
- 047
- 081
- 100

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/research/MODEL_REFRESH_20261120.md first; docs/research/20261028-skill-optimization/prepared-research/105-frontier-model-routing-20261112.md is background and loses on conflict.
- Version floors: claude-fable-5-2 needs Claude Code >= 2.1.290; gpt-6.2-astra needs Codex >= 0.171.0; gemini-4-carbon-* is Ultra/Enterprise only and is not listed on this account.
- No PRIMARY_SIGNALS entry maps to frontier; frontier_long_horizon stays ('max','high'); Codex credit exhaustion is availability (skip to Fable, record no escalation).
- Touch run_isolated.py only in its ladder_exhausted/route-resolution branch; keep the ESCALATION_LADDERS comment saying frontier needs this task's explicit approval.
- Use only task 105 inputs, checks and write scope in TASK_INPUTS.json; record actual receipts/outcomes and leave the task pending until verified.

## Acceptance criteria

- The 2026-11-20 sources and the observed CLI ids (claude-fable-5-2, gpt-6.2-astra; no gemini-4-carbon-*) are recorded in the receipt.
- When every max candidate is unavailable the selector returns no_candidate, never frontier.
- A config escalation_ladder containing frontier or l6 is rejected.
- A plan spec with model_tier: frontier is rejected.
- A frontier route for workload implementation is rejected.
- With L6 disabled, routes, argv and the v8 map hash are identical to the recorded baseline.
- Effective top tier is max; frontier is never a ladder or switch rung and is never reached for implementation, quota, auth or environment outcomes.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_105`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_105`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
