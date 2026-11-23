---
task_id: "089"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "strong"
reasoning_effort: "high"
complexity: "high"
requirements: "R047"
dependencies: "007, 063, 088"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 089 — Implement avoid skill loading for routine commands and trivial changes

## Objective

Reduce implicit plan-and-execute activation for simple commands and trivial edits through concise discovery metadata and host-level negative invocation tests.

## Requirements covered

- R047

## Complexity and atomicity

- Complexity: **high**
- Why this is one executable TODO: One coherent outcome, focused tests and an independent review boundary.

## Context-isolation boundary

- Why one fresh worker context helps this whole TODO: Steps share one observable implementation or review outcome.
- Context that is genuinely shared by all subtasks:
- Only assigned contract and actual code evidence.
- Concerns deliberately isolated into other TODOs:
- Unrelated TODOs and old transcripts are excluded.

## Isolation contract

This task definition and the exact execution-context files listed below are the only planning artifacts assigned to this worker. Read the task definition first, then read every assigned context file. Do not discover or open any other context file, `PLAN.md`, `TODO.md`, `manifest.json`, `orchestrator.config.json`, result files, logs, or unrelated task definitions. You may read repository source, tests, build files, and runtime output relevant to this task.

Another task definition may be opened only when one of the explicitly allowed task ids above is necessary to resolve a blocked dependency, ambiguity, or validation conflict. Record the task id and reason in the completion report.

## Assigned execution context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Assigned validated learnings

- None

These files are concise, immutable artifacts produced only after another TODO passed deterministic validation. Read exactly the assigned files, never a previous worker transcript or an unassigned learning file.

## Resumable subtask checklist

- [ ] **S001** — Read evidence
  - Read docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261031.md, assigned prepared research and materially affected source files.
- [ ] **S002** — Implement contract 1
  - Narrow host-visible skill description/trigger language without requiring the full instruction body for a negative decision.
- [ ] **S003** — Implement contract 2
  - Test negative activation for git status, one-file read, short shell commands and trivial edits, plus positive explicit plan invocations.
- [ ] **S004** — Implement contract 3
  - Measure false activation, missed activation and prompt bytes on deterministic eval fixtures; live host traces only with explicit owner confirmation (G002); do not add a paid classifier.
- [ ] **S005** — Run tests
  - Implement test/optimization/skill_activation_negatives_self_test.py and run mapped validation plus feature negative cases.
- [ ] **S006** — Record implementation
  - Record real implementation and test evidence in docs/research/20261028-skill-optimization/implementation/089-receipt.json and docs/research/20261028-skill-optimization/implementation/089-outcome.md.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Reduce implicit plan-and-execute activation for simple commands and trivial edits through concise discovery metadata and host-level negative invocation tests.

## Out of scope

- No second plan or unrelated changes.
- No installation, provider login, publishing or user-global configuration changes without permission.

## Expected files

- skill/plan-and-execute/SKILL.md
- skill/plan-and-execute/agents/openai.yaml
- skill/plan-and-execute/references/ROUTING.md
- skill/validate-or-fix/SKILL.md
- skill/plan-and-execute/references/routing-evals.json
- test/optimization/skill_activation_negatives_self_test.py
- docs/research/20261028-skill-optimization/implementation/089-receipt.json
- docs/research/20261028-skill-optimization/implementation/089-outcome.md

## Dependencies

- 007
- 063
- 088

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261031.md.
- Follow task 089 in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Preserve exact user intent, bounded context, security floors and real deterministic tests.
- Refresh only materially changed facts from assigned prepared reports 006, 028, 060, 062.
- Preserve evidence in docs/research/20261028-skill-optimization/implementation/089-receipt.json and docs/research/20261028-skill-optimization/implementation/089-outcome.md; do not mark a pending task done without validation.

## Acceptance criteria

- Simple shell commands, one-file reads and trivial edits do not implicitly load the full skill.
- Explicit plan/lifecycle commands and genuine multi-workstream jobs still activate.
- Tiny discoverable metadata cost is acknowledged; there is no claim of zero skill-related tokens.
- Deterministic positive/negative eval fixtures pass; live host traces run only with explicit owner confirmation (G002), and unavailable/no-quota hosts are recorded not_verified, not passed.
- Implementation and review remain pending until actual execution evidence exists.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_089`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_089`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
