---
task_id: "028"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "strong"
reasoning_effort: "high"
complexity: "high"
requirements: "R002, R003, R004, R005, R007, R032, R037, R038, R039, R042, R044"
dependencies: "001, 015"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 028 — Implement fresh workers, delegation gates and prompt-cache boundaries

## Objective

Use a measured delegation gate with explicit input revision and isolation boundaries; prefer one qualified context for sequential work and bounded fresh workers for independently useful tasks.

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
  - Read docs/research/20261028-skill-optimization/prepared-research/028-delegation.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** — Implement revised contract 1
  - Define the delegate-vs-single-qualified-model comparison as a fixture-backed decision record (cost fields, unknowns null) handed to 064; no live run (G002).
- [ ] **S003** — Implement revised contract 2
  - Pin worker base revision and uncommitted-input policy; verify isolated worktree starts from the intended source.
- [ ] **S004** — Implement revised contract 3
  - Bound in-memory output while preserving independently parsed final reports and owned diagnostic logs.
- [ ] **S005** — Validate all assigned positive and negative cases
  - Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** — Record implementation evidence for independent review
  - Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Implement fresh workers, delegation gates and prompt-cache boundaries

## Out of scope

- No new broad research phase or second-plan generation.
- Do not change installed copies, user-global settings or publish without permission.

## Expected files

- skill/plan-and-execute/scripts/run_isolated.py
- skill/plan-and-execute/scripts/runner_contract.py
- test/optimization/delegation_self_test.py
- skill/plan-and-execute/references/DELEGATION.md
- docs/research/20261028-skill-optimization/implementation/028-receipt.json
- docs/research/20261028-skill-optimization/implementation/028-outcome.md

## Dependencies

- 001
- 015

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/research/20261028-skill-optimization/prepared-research/028-delegation.md.
- Use only task 028 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/028-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance criteria

- A noisy fake CLI emits many megabytes without proportional memory growth or pipe deadlock.
- A final structured report remains recoverable after long tool output; missing or truncated envelopes fail visibly.
- Two delegated writers cannot silently claim the same source scope.
- Above-floor work cannot be retained on an underqualified worker merely to avoid coordination cost.
- Prefix hashes match across tasks for raw and production entrypoints.
- A worker based on the default branch rather than the pinned working revision is rejected.
- Concurrent writers never share an overlapping scope without serialization.
- Multi-megabyte output does not grow the diagnostic buffer without bound.
- Native fork support cannot silently claim fresh-context isolation.
- With an uncommitted tracked change in the parent checkout and no commit authorization, in-place execution preserves it; isolated-worktree mode carries the declared uncommitted inputs or refuses with a reason, never starting from HEAD.
- Prepared research is not proof of implementation or independent-review completion.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_028`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_028`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
