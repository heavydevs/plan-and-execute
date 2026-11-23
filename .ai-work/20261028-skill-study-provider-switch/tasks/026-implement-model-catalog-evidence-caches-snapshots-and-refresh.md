---
task_id: "026"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "strong"
reasoning_effort: "high"
complexity: "high"
requirements: "R002, R003, R004, R005, R007, R032, R037, R038, R039, R042, R044"
dependencies: "001, 021"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 026 — Implement model catalog evidence, caches, snapshots and refresh

## Objective

Keep provider-scoped catalog evidence with independently aged facets and immutable attempt bindings; treat aliases and pricing changes as observable model-resolution events.

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
  - Read docs/research/20261028-skill-optimization/prepared-research/026-catalog-snapshots.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** — Implement revised contract 1
  - Represent requested id, observed resolved id, harness version and evidence digest separately for each attempt.
- [ ] **S003** — Implement revised contract 2
  - Version cache-write/read prices by model and billing mode; unknown cost never means free.
- [ ] **S004** — Implement revised contract 3
  - Test concurrent refresh and stale fallback without rewriting bindings of in-progress tasks.
- [ ] **S005** — Validate all assigned positive and negative cases
  - Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** — Record implementation evidence for independent review
  - Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Implement model catalog evidence, caches, snapshots and refresh

## Out of scope

- No new broad research phase or second-plan generation.
- Do not change installed copies, user-global settings or publish without permission.

## Expected files

- skill/plan-and-execute/scripts/model_catalog.py
- skill/plan-and-execute/scripts/model_catalogctl.py
- test/optimization/catalog_snapshots_self_test.py
- skill/plan-and-execute/references/MODEL_CATALOG.md
- docs/research/20261028-skill-optimization/implementation/026-receipt.json
- docs/research/20261028-skill-optimization/implementation/026-outcome.md

## Dependencies

- 001
- 021

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/research/20261028-skill-optimization/prepared-research/026-catalog-snapshots.md.
- Use only task 026 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/026-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance criteria

- Fresh facets produce no network/probe calls; expired or changed-version capability triggers only its required source.
- A failing refresh retains the last valid cache with a visible stale warning.
- Concurrent refreshes of different providers do not overwrite one another.
- An empty advanced tier lifts to a configured stronger tier or yields an explicit ineligible candidate.
- An in-progress task retains its model while pending tasks can rebase with an audit entry.
- An alias backend change invalidates the relevant candidate evidence while keeping the old attempt record intact.
- Failed partial refresh leaves valid prior facets readable with explicit age.
- An existing plan's catalog snapshot binding is unchanged when a newer catalog snapshot or policy version is published; config-snapshot inheritance is owned by 070.
- Unknown prices cannot win a cost comparison by being treated as zero.
- The v8 map is preserved: Opus 5.5 / Sol 6.2 xhigh at max, Fable 5.2 / Astra 6.2 absent from the tier map, Antigravity Claude capped at advanced, Gemini 4 Hydrogen/Neon preset ordered first, Carbon not routed.
- Prepared research is not proof of implementation or independent-review completion.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_026`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_026`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
