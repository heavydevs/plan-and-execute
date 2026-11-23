---
task_id: "097"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "strong"
reasoning_effort: "high"
complexity: "high"
requirements: "R051"
dependencies: "007, 029, 061, 063, 067, 096, 073"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 097 — Implement make console, progress and end-user docs concise and precise

## Objective

Reduce redundant user-facing AI outputs, status messages and manuals while retaining correctness, exact technical detail, clear actions and user-selectable depth.

## Requirements covered

- R051

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
  - Define answer-first, literal, specific adult-professional language; do not confuse autism with reduced intelligence or uniform preferences.
- [ ] **S003** — Implement contract 2
  - Cut greetings, repeated recaps, filler, generic praise, unasked tangents and redundant progress without omitting important decisions.
- [ ] **S004** — Implement contract 3
  - Separate concise human output from full machine-readable JSON, diagnostics and logs; expose details/verbose on request.
- [ ] **S005** — Implement contract 4
  - Measure output tokens and repeated-text rate with accuracy, necessary caveats, actionability and accessibility on paired old/new scenarios; human comprehension is not_verified without consented user evidence.
- [ ] **S006** — Run tests
  - Implement test/optimization/concise_communication_self_test.py and run mapped validation plus feature negative cases.
- [ ] **S007** — Record implementation
  - Record real implementation and test evidence in docs/research/20261028-skill-optimization/implementation/097-receipt.json and docs/research/20261028-skill-optimization/implementation/097-outcome.md.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Reduce redundant user-facing AI outputs, status messages and manuals while retaining correctness, exact technical detail, clear actions and user-selectable depth.

## Out of scope

- No second plan or unrelated changes.
- No installation, provider login, publishing or user-global configuration changes without permission.

## Expected files

- skill/plan-and-execute/references/USER_COMMUNICATION.md
- skill/plan-and-execute/references/TOKEN_EFFICIENCY.md
- skill/plan-and-execute/references/ARTIFACT_WRITING.md
- skill/plan-and-execute/scripts/process_io.py
- skill/plan-and-execute/scripts/run_isolated.py
- skill/plan-and-execute/references/INSTALLATION.md
- skill/plan-and-execute/references/INSTALLATION.pt-BR.md
- skill/validate-or-fix/references/OPERATIONS.md
- test/optimization/concise_communication_self_test.py
- docs/research/20261028-skill-optimization/implementation/097-receipt.json
- docs/research/20261028-skill-optimization/implementation/097-outcome.md

## Dependencies

- 007
- 029
- 061
- 063
- 067
- 096
- 073

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261031.md.
- Follow task 097 in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Preserve exact user intent, bounded context, security floors and real deterministic tests.
- Refresh only materially changed facts from assigned prepared reports 006, 028, 060, 062.
- Preserve evidence in docs/research/20261028-skill-optimization/implementation/097-receipt.json and docs/research/20261028-skill-optimization/implementation/097-outcome.md; do not mark a pending task done without validation.

## Acceptance criteria

- A one-step command returns the result and necessary next action, not a verbose status essay.
- Technical answers lead with a precise answer and retain commands, constraints, risk and error explanation when material.
- Do not restate earlier concepts unless necessary for the present decision, apparent confusion or explicit user request.
- User-facing bytes/tokens fall without losing correct steps, safety warnings, machine output or diagnostic evidence.
- The tone respects adult autistic users, avoids overgeneralization and supports individual preference and detail expansion.
- Automated paired old/new scenarios show accuracy and completeness no worse; human comprehension is not_verified unless consented user evidence exists.
- Implementation and review remain pending until actual execution evidence exists.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_097`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_097`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
