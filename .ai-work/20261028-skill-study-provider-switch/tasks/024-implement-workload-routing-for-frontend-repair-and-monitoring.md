---
task_id: "024"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "strong"
reasoning_effort: "high"
complexity: "high"
requirements: "R002, R003, R004, R005, R007, R032, R037, R038, R039, R042, R044"
dependencies: "001, 023"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 024 — Implement workload routing for frontend, repair and monitoring

## Objective

Route by measured workload capability and validation strength, with separate design, functional UI, monitoring and repair requirements rather than a universal model leaderboard.

## Requirements covered

- R002
- R003
- R004
- R005
- R007
- R032
- R037
- R038
- R039
- R042
- R044

## Complexity and atomicity

- Complexity: **high**
- Why this is one executable TODO: One bounded implementation contract with its regression tests; source coupling requires a shared acceptance boundary, not an arbitrary file-count split.

## Context-isolation boundary

- Why one fresh worker context helps this whole TODO: This task owns one behavior or correction gate with independently checkable outcomes.
- Context that is genuinely shared by all subtasks:
- Read only the assigned decision, source targets and accepted prerequisite receipts.
- Concerns deliberately isolated into other TODOs:
- Do not load unrelated reports, provider guides or historical conversation transcripts.

## Isolation contract

This task definition and the exact execution-context files listed below are the only planning artifacts assigned to this worker. Read the task definition first, then read every assigned context file. Do not discover or open any other context file, `PLAN.md`, `TODO.md`, `manifest.json`, `orchestrator.config.json`, result files, logs, or unrelated task definitions. You may read repository source, tests, build files, and runtime output relevant to this task.

Another task definition may be opened only when one of the explicitly allowed task ids above is necessary to resolve a blocked dependency, ambiguity, or validation conflict. Record the task id and reason in the completion report.

## Assigned execution context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Assigned validated learnings

- None

These files are concise, immutable artifacts produced only after another TODO passed deterministic validation. Read exactly the assigned files, never a previous worker transcript or an unassigned learning file.

## Resumable subtask checklist

- [ ] **S001** — Read assigned research and pin applicable contracts
  - Read docs/research/20261028-skill-optimization/prepared-research/024-workload-affinity.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** — Implement revised contract 1
  - Separate visual design, UI behavior, accessibility, observation and repair capabilities in workload evidence.
- [ ] **S003** — Implement revised contract 2
  - Use deterministic monitoring first; route only bounded novel ambiguity to a permitted observer.
- [ ] **S004** — Implement revised contract 3
  - Treat manager-quota preference as secondary to capability, privacy and validation floors; never infer effective effort from a family label.
- [ ] **S005** — Validate all assigned positive and negative cases
  - Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** — Record implementation evidence for independent review
  - Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Implement workload routing for frontend, repair and monitoring

## Out of scope

- No new broad research phase or second-plan generation.
- Do not change installed copies, user-global settings or publish without permission.

## Expected files

- skill/plan-and-execute/scripts/workload_routing.py
- skill/plan-and-execute/scripts/configure.py
- test/optimization/workload_affinity_self_test.py
- skill/plan-and-execute/references/MODEL_MAPPING.md
- docs/research/20261028-skill-optimization/implementation/024-receipt.json
- docs/research/20261028-skill-optimization/implementation/024-outcome.md

## Dependencies

- 001
- 023

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/research/20261028-skill-optimization/prepared-research/024-workload-affinity.md.
- Use only task 024 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/024-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance criteria

- A preferred intermediate profile is excluded from a maximum-capability task when its validated range is lower.
- An observer profile cannot be selected for a source-writing task or gain write tools on fallback.
- Routing evidence marks a frontend task whose keyboard check fails as failed even when screenshots match; the browser harness belongs to 125.
- A depleted Gemini pool can use another configured pool without assuming all accounts have independent allocations.
- Unknown economics remains unknown; ties use stable policy instead of invented prices.
- A visual-only success cannot satisfy a task with keyboard and functional acceptance checks.
- A cheap observer route is never selected to implement an architecture-sensitive repair.
- A manager quota preference cannot lower the minimum effective capability.
- Unknown quota or cost values do not become zero-cost priority.
- Ties resolve Antigravity > Codex > Claude for implementation/repair and Codex > Claude for architecture/review.
- Fable 5.2, Astra 6.2 and gemini-4-carbon-* never appear in implementation, repair or monitoring routes.
- The v8 map is preserved: Opus 5.5 / Sol 6.2 xhigh at max, Fable 5.2 / Astra 6.2 absent from the tier map, Antigravity Claude capped at advanced, Gemini 4 Hydrogen/Neon preset ordered first, Carbon not routed.
- Prepared research is not proof of implementation or independent-review completion.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_024`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_024`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
