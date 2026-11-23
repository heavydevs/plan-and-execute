---
task_id: "064"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "strong"
reasoning_effort: "high"
complexity: "high"
requirements: "R002, R003, R004, R005, R007, R032, R037, R038, R039, R042, R044"
dependencies: "001, 005"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 064 — Implement telemetry, shadow routing and non-inferiority benchmarks

## Objective

Evaluate quality-constrained cost with paired task-level experiments, versioned native usage and honest missing data; keep offline replay separate from evidence of real model performance.

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
  - Read docs/research/20261028-skill-optimization/prepared-research/064-economic-evaluation.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** — Implement revised contract 1
  - Resample by unique task or repository cluster and preserve pairing; repeated fixture replay cannot increase empirical sample size.
- [ ] **S003** — Implement revised contract 2
  - Predeclare quality/cost/latency gates and count failed, timed-out and auxiliary calls without favorable censoring.
- [ ] **S004** — Implement revised contract 3
  - Version billing units and reject non-finite usage; unknown cost and zero-success ratios cannot become apparent savings.
- [ ] **S005** — Validate all assigned positive and negative cases
  - Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** — Record implementation evidence for independent review
  - Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Implement telemetry, shadow routing and non-inferiority benchmarks

## Out of scope

- No new broad research phase or second-plan generation.
- Do not change installed copies, user-global settings or publish without permission.

## Expected files

- skill/plan-and-execute/scripts/routing_telemetry.py
- tools/skill_benchmark.py
- tools/routing_eval.py
- test/optimization/economic_evaluation_self_test.py
- docs/research/SKILL_BENCHMARK.md
- docs/research/routing-eval/thresholds.json
- docs/research/20261028-skill-optimization/implementation/064-receipt.json
- docs/research/20261028-skill-optimization/implementation/064-outcome.md

## Dependencies

- 001
- 005

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/research/20261028-skill-optimization/prepared-research/064-economic-evaluation.md.
- Use only task 064 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/064-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance criteria

- Non-finite numbers cannot produce a successful numeric rollup or invalid JSON.
- Missing cost remains unknown and is not silently compared as free.
- Failed attempts and diagnostic/handoff costs are included in cost per validated result.
- Repeating a fixed corpus changes replay count but not the claimed independent sample count.
- A candidate with lower apparent cost but worse critical acceptance cannot pass the quality gate.
- Duplicating deterministic replay rows does not narrow empirical confidence intervals.
- NaN, infinity and negative usage are rejected; missing values remain null.
- A zero-success arm cannot report zero cost per validated result.
- Cold/warm cache and subscription/API modes remain distinct in rollups.
- If docs/research/routing-eval/measurements.jsonl exists, thresholds.json stays byte-identical; otherwise any edit updates predeclared_on and the regenerated SHADOW_REPORT digest.
- Prepared research is not proof of implementation or independent-review completion.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_064`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_064`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
