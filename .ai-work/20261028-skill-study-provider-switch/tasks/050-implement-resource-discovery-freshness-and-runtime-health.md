---
task_id: "050"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "strong"
reasoning_effort: "high"
complexity: "high"
requirements: "R002, R003, R004, R005, R007, R032, R037, R038, R039, R042, R044"
dependencies: "001"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 050 — Implement resource discovery, freshness and runtime health

## Objective

Maintain a content-fingerprinted, least-privilege resource map with explicit readiness, health and progress roles; reconcile only relevant inventory inputs and fail unknown observations conservatively.

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
  - Read docs/research/20261028-skill-optimization/prepared-research/050-resource-map.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** — Implement revised contract 1
  - Separate startup readiness, runtime health and task progress in resource observations.
- [ ] **S003** — Implement revised contract 2
  - Reject stale content fingerprints and unsafe or unbounded probes; unknown observations never mean healthy.
- [ ] **S004** — Implement revised contract 3
  - Measure probe count and duration per validation and reuse only generation-valid scoped inventory.
- [ ] **S005** — Validate all assigned positive and negative cases
  - Run the declared regression commands and every assigned acceptance counterexample, plus run_task_checks.py --task 050 directly because resource_watch.py is under change. Preserve logs, hashes, failures and limits.
- [ ] **S006** — Record implementation evidence for independent review
  - Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Implement resource discovery, freshness and runtime health

## Out of scope

- No new broad research phase or second-plan generation.
- Do not change installed copies, user-global settings or publish without permission.

## Expected files

- skill/plan-and-execute/scripts/service_map.py
- skill/plan-and-execute/scripts/resource_watch.py
- test/optimization/resource_map_self_test.py
- skill/plan-and-execute/references/TEST_RESOURCE_MONITORING.md
- docs/research/20261028-skill-optimization/implementation/050-receipt.json
- docs/research/20261028-skill-optimization/implementation/050-outcome.md

## Dependencies

- 001

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/research/20261028-skill-optimization/prepared-research/050-resource-map.md.
- Use only task 050 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/050-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance criteria

- Removing a referenced test file or changing toolchain input makes the map stale/actionable.
- A service inside startup grace is not misclassified as unhealthy.
- An unresponsive health probe ends at its bounded timeout and does not stall the watcher.
- A semantic failing test with healthy dependencies differs from a dependency outage.
- Unrelated resources are not probed or read for a focused validation.
- An open port with an unready service blocks dependent validation without escalating the model.
- A same-size build configuration change invalidates the map.
- Probe timeout or permission denial is explicit unknown/environment evidence.
- A map probe cannot silently run a service repair command.
- Existing schema_version 1 maps (.ai-work/SERVICE_MAP.md, sha256-path-content-v2-streamed) stay valid; new readiness/health fields are optional.
- Prepared research is not proof of implementation or independent-review completion.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_050`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_050`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
