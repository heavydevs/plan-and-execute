---
task_id: "001"
plan_id: "20260928-auxiliary-routing"
status: "completed"
provider: "auto"
model_tier: "strong"
reasoning_effort: "high"
complexity: "medium"
requirements: "R001, R009"
dependencies: "none"
context_files: "none"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 001 — Refine collaboration requirements and acceptance

## Objective

Replace the draft with implementable acceptance contracts grounded in primary evidence.

## Requirements covered

- R001
- R009

## Complexity and atomicity

- Complexity: **medium**
- Why this is one executable TODO: Refine collaboration requirements and acceptance has one coherent contract and an independent REQUIREMENTS validation boundary.

## Context-isolation boundary

- Why one fresh worker context helps this whole TODO: Implementation and focused negative tests share the same invariant and dependency surface.
- Context that is genuinely shared by all subtasks:
- Replace the draft with implementable acceptance contracts grounded in primary evidence.
- Concerns deliberately isolated into other TODOs:
- Other tasks consume checked-in contracts, not this task conversation.

## Isolation contract

This task definition and the exact execution-context files listed below are the only planning artifacts assigned to this worker. Read the task definition first, then read every assigned context file. Do not discover or open any other context file, `PLAN.md`, `TODO.md`, `manifest.json`, `orchestrator.config.json`, result files, logs, or unrelated task definitions. You may read repository source, tests, build files, and runtime output relevant to this task.

Another task definition may be opened only when one of the explicitly allowed task ids above is necessary to resolve a blocked dependency, ambiguity, or validation conflict. Record the task id and reason in the completion report.

## Assigned execution context

- None

## Assigned validated learnings

- None

These files are concise, immutable artifacts produced only after another TODO passed deterministic validation. Read exactly the assigned files, never a previous worker transcript or an unassigned learning file.

## Resumable subtask checklist

- [x] **S001** — Implement and verify the bounded contract
  - Replace the draft with implementable acceptance contracts grounded in primary evidence.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Replace the draft with implementable acceptance contracts grounded in primary evidence.

## Out of scope

- No unrelated framework refactoring or changes to model pricing/catalog.

## Expected files

- docs/requests/auxiliary-model-assistants-and-tier-routing.md
- docs/research/AUXILIARY_ROUTING.md

## Dependencies

- None

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/research/AUXILIARY_ROUTING.md for security and economic constraints.
- Use deterministic validations and record host-managed execution honestly.

## Acceptance criteria

- Replace the draft with implementable acceptance contracts grounded in primary evidence.
- REQUIREMENTS validation passes; negative cases and limitations are recorded.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation REQUIREMENTS`

## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
