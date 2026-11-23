---
task_id: "001"
plan_id: "20261028-skill-study-provider-switch"
status: "completed"
provider: "auto"
model_tier: "standard"
reasoning_effort: "medium"
complexity: "medium"
requirements: "R001, R004, R010, R011, R039, R040, R042"
dependencies: "none"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 001 — Implement deterministic preflight and baseline fixtures

## Objective

Build offline preflight fixtures and baseline contracts without making a maximum-model planning review a global prerequisite.

## Requirements covered

- R001
- R004
- R010
- R011
- R039
- R040
- R042

## Complexity and atomicity

- Complexity: **medium**
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

- [x] **S001** — Read assigned decision and pin baseline
  - Read docs/research/20261028-skill-optimization/prepared-research/ARCHITECTURE_AND_SCOPE.md. Confirm source applicability; do not repeat broad research.
- [x] **S002** — Implement change 1
  - Implement only the deterministic preflight contract from ARCHITECTURE_AND_SCOPE.md using the pinned inventory and current task catalog; coverage checks belong to 002.
- [x] **S003** — Implement change 2
  - Add negative fixtures for stale hashes of pinned TASK_INPUTS prepared_reports/input_contract files, missing resources, unsupported CLI versions and broad context loading; report historical BASELINE_INVENTORY.json drift as drift, never a failure.
- [x] **S004** — Implement change 3
  - Keep missing authenticated providers as an explicit execution limitation, not a reason to fabricate review or fail local research preparation.
- [x] **S005** — Run declared regression checks
  - Run the declared targeted tests through the resource watcher. Implement every assigned acceptance case and preserve failures and limitations.
- [x] **S006** — Record acceptance evidence
  - Write the implementation receipt and outcome report with changed-file hashes, acceptance coverage and actual test logs. Leave unresolved work pending.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Implement deterministic preflight and baseline fixtures

## Out of scope

- No new broad research phase or second-plan generation.
- Do not change installed copies, user-global settings or publish without permission.

## Expected files

- test/optimization/baseline_contracts.py
- test/optimization/task_001_self_test.py
- docs/research/20261028-skill-optimization/implementation/001-receipt.json
- docs/research/20261028-skill-optimization/implementation/001-outcome.md

## Dependencies

- None

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/research/20261028-skill-optimization/prepared-research/ARCHITECTURE_AND_SCOPE.md.
- Use only task 001 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/001-receipt.json.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.

## Acceptance criteria

- Offline contract tests pass with no model call or user-global configuration write.
- Every fixture distinguishes historical baseline, current code and expected new behavior.
- Actual code changes and acceptance evidence are recorded.
- Preflight passes against the current tree with 131/188 inventory hashes changed and lists that drift instead of failing.
- The prepared report is input evidence, not proof that this implementation or its independent review has passed.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_001`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_001`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
