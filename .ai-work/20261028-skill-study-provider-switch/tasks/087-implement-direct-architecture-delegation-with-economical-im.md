---
task_id: "087"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "strong"
reasoning_effort: "high"
complexity: "high"
requirements: "R046"
dependencies: "007, 025, 029, 051, 061, 063, 081"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 087 — Implement direct architecture delegation with economical implementation

## Objective

For cohesive multi-file DIRECT work, inspect relevant files cheaply, delegate difficult architecture to a stronger model only when justified, then choose a qualified economical executor and monitored tests.

## Requirements covered

- R046

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
  - Inventory and read all materially relevant files with the current affordable model; forward only decision-relevant evidence to stronger context.
- [ ] **S003** — Implement contract 2
  - Extend PRIMARY_SIGNALS/minimum_route in routingctl.py with a DIRECT staged handoff (no parallel router); delegate high-risk architecture to a qualified stronger tier with durable design.
- [ ] **S004** — Implement contract 3
  - Return bounded implementation to the current or intermediate tier when testability and capability floors justify it; reroute expensive silent-failure work upward.
- [ ] **S005** — Implement contract 4
  - Run meaningful DIRECT tests through shared resource/log/progress watchers, optionally using a cheap, read-only event-triggered observer.
- [ ] **S006** — Run tests
  - Implement test/optimization/direct_architecture_handoff_self_test.py and run mapped validation plus feature negative cases.
- [ ] **S007** — Record implementation
  - Record real implementation and test evidence in docs/research/20261028-skill-optimization/implementation/087-receipt.json and docs/research/20261028-skill-optimization/implementation/087-outcome.md.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- DIRECT architecture handoff: economical file study, qualified strong design, economical implementation and mapped tests.

## Out of scope

- No second plan or unrelated changes.
- No installation, provider login, publishing or user-global configuration changes without permission.

## Expected files

- skill/plan-and-execute/scripts/validatectl.py
- skill/plan-and-execute/scripts/workload_routing.py
- skill/plan-and-execute/references/ROUTING.md
- skill/plan-and-execute/references/DELEGATION.md
- skill/plan-and-execute/references/MODEL_ROUTING.md
- skill/plan-and-execute/references/TEST_RESOURCE_MONITORING.md
- test/optimization/direct_architecture_handoff_self_test.py
- skill/plan-and-execute/scripts/routingctl.py
- docs/research/20261028-skill-optimization/implementation/087-receipt.json
- docs/research/20261028-skill-optimization/implementation/087-outcome.md

## Dependencies

- 007
- 025
- 029
- 051
- 061
- 063
- 081

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261031.md.
- Follow task 087 in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Preserve exact user intent, bounded context, security floors and real deterministic tests.
- Refresh only materially changed facts from assigned prepared reports 006, 028, 060, 062.
- Preserve evidence in docs/research/20261028-skill-optimization/implementation/087-receipt.json and docs/research/20261028-skill-optimization/implementation/087-outcome.md; do not mark a pending task done without validation.
- Architecture stage Codex > Claude (Sol 6.2 / Opus 5.5 high/xhigh); implementation stage Antigravity > Codex > Claude; unavailable providers are skipped without lowering the floor; frontier never serves DIRECT implementation.

## Acceptance criteria

- A cohesive seven-file task stays DIRECT even when one difficult design decision needs a stronger architect.
- The inexpensive stage reads all relevant files; the architecture worker receives a precise evidence packet, not a duplicated source dump.
- The architect outputs a durable design; implementation can return to a lower qualified tier with acceptance checks.
- Stateful DIRECT validations use project resource mapping and log monitoring without creating a TODO plan.
- Compare complete validated cost (read, design, implementation, retries, reviews) to a single qualified model; preserve security floors.
- Implementation and review remain pending until actual execution evidence exists.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_087`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_087`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
