---
task_id: "006"
plan_id: "20261028-skill-study-provider-switch"
status: "completed"
provider: "auto"
model_tier: "standard"
reasoning_effort: "high"
complexity: "medium"
requirements: "R002, R003, R004, R005, R007, R032, R037, R038, R039, R042, R044"
dependencies: "001"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 006 — Implement selective activation, intake and late promotion

## Objective

Keep DIRECT as a zero-orchestration fast path, with explicit risk/promotion signals and evaluated activation; do not add a classifier call.

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

- [x] **S001** — Read assigned research and pin applicable contracts
  - Read docs/research/20261028-skill-optimization/prepared-research/006-activation-intake.md. Verify the current source and only material version/account conflicts.
- [x] **S002** — Implement revised contract 1
  - Record bounded reason codes only in the selected workflow; a rejected implicit match creates no plan, ledger or study files.
- [x] **S003** — Implement revised contract 2
  - Measure entrypoint bytes and offline false-positive/false-negative rates on held-out routing-evals.json against baseline; live host loading/latency only with owner-confirmed authenticated runs, otherwise a recorded limitation.
- [x] **S004** — Implement revised contract 3
  - Separate routing mode from capability tier so a small risky fix can stay DIRECT with a qualified implementation route.
- [x] **S005** — Validate all assigned positive and negative cases
  - Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [x] **S006** — Record implementation evidence for independent review
  - Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Implement selective activation, intake and late promotion

## Out of scope

- No new broad research phase or second-plan generation.
- Do not change installed copies, user-global settings or publish without permission.

## Expected files

- skill/plan-and-execute/scripts/requestctl.py
- skill/plan-and-execute/scripts/promotectl.py
- skill/plan-and-execute/scripts/routing_self_test.py
- test/optimization/activation_intake_self_test.py
- skill/plan-and-execute/SKILL.md
- skill/plan-and-execute/agents/openai.yaml
- skill/plan-and-execute/references/ROUTING.md
- skill/plan-and-execute/references/PROMOTION.md
- skill/plan-and-execute/references/routing-evals.json
- docs/research/20261028-skill-optimization/implementation/006-receipt.json
- docs/research/20261028-skill-optimization/implementation/006-outcome.md

## Dependencies

- 001

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/research/20261028-skill-optimization/prepared-research/006-activation-intake.md.
- Use only task 006 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/006-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance criteria

- A one-module feature touching seven files remains DIRECT and leaves no plan artifacts.
- A short security-sensitive fix remains direct when cohesive, but its model floor is not lowered.
- A promoted task includes only remaining outcomes and preserves the original worktree.
- Entrypoint bytes and offline false-positive/false-negative rates on held-out routing-evals.json are measured against baseline; live host loading/latency needs owner-confirmed authenticated runs, else a recorded limitation.
- A near-finished high-context task stays DIRECT without creating control files.
- A tiny security-sensitive edit can select a strong worker without forcing an orchestration plan.
- Promotion preserves changed files and validated outcomes and schedules only remaining work.
- Prepared research is not proof of implementation or independent-review completion.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_006`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_006`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
