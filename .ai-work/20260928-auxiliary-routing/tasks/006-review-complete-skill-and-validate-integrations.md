---
task_id: "006"
plan_id: "20260928-auxiliary-routing"
status: "pending"
provider: "auto"
model_tier: "strong"
reasoning_effort: "high"
complexity: "high"
requirements: "R010, R009"
dependencies: "001, 002, 003, 004, 005"
context_files: "none"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 006 — Review complete skill and validate integrations

## Objective

Pass full regressions and skill budgets; document native-platform limits and package the updated skill.

## Requirements covered

- R010
- R009

## Complexity and atomicity

- Complexity: **high**
- Why this is one executable TODO: Review complete skill and validate integrations has one coherent contract and an independent ALL validation boundary.

## Context-isolation boundary

- Why one fresh worker context helps this whole TODO: Implementation and focused negative tests share the same invariant and dependency surface.
- Context that is genuinely shared by all subtasks:
- Pass full regressions and skill budgets; document native-platform limits and package the updated skill.
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

- [ ] **S001** — Implement and verify the bounded contract
  - Pass full regressions and skill budgets; document native-platform limits and package the updated skill.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Pass full regressions and skill budgets; document native-platform limits and package the updated skill.

## Out of scope

- No unrelated framework refactoring or changes to model pricing/catalog.

## Expected files

- skill/plan-and-execute/SKILL.md
- skill/plan-and-execute/references
- tools
- test
- README.md
- README.pt-BR.md

## Dependencies

- 001
- 002
- 003
- 004
- 005

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/research/AUXILIARY_ROUTING.md for security and economic constraints.
- Use deterministic validations and record host-managed execution honestly.
- Test routing precedence, quota resume, bounded assistant failures and wizard cancellation.

## Acceptance criteria

- Pass full regressions and skill budgets; document native-platform limits and package the updated skill.
- ALL validation passes; negative cases and limitations are recorded.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation ALL`

## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
