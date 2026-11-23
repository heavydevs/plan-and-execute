---
task_id: "080"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "strong"
reasoning_effort: "high"
complexity: "high"
requirements: "R005, R006, R012, R028, R029, R031, R033, R034, R035, R037, R045"
dependencies: "065, 079"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 080 — Complete provider-switch documentation, replay and cost evidence

## Objective

Implement the assigned provider-switch contract from report068 and the original twelve-case acceptance matrix.

## Requirements covered

- R005
- R006
- R012
- R028
- R029
- R031
- R033
- R034
- R035
- R037
- R045

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

- [ ] **S001** — Read assigned decision and pin baseline
  - Read docs/research/20261028-skill-optimization/prepared-research/068-provider-switch-handoff.md, docs/plans/20261028-skill-optimization/ACCEPTANCE_MATRIX.md. Confirm source applicability; do not repeat broad research.
- [ ] **S002** — Implement change 1
  - Run all twelve original acceptance cases and preserve disabled-mode compatibility.
- [ ] **S003** — Implement change 2
  - Report reachability and duplicate dispatches separately from unmeasured live quality/cost.
- [ ] **S004** — Implement change 3
  - Add regression tests for the corresponding original acceptance cases and preserve legacy behavior.
- [ ] **S005** — Apply revised runtime contract 1
  - Compare counterfactual dispatch counts on the original twelve cases; do not present replay as measured model quality or dollar savings.
- [ ] **S006** — Apply revised runtime contract 2
  - Document account-dependent quota, conditional effort capabilities, fallback-disabled behavior and unverified platforms.
- [ ] **S007** — Run declared regression checks
  - Run the declared targeted tests through the resource watcher. Implement every assigned acceptance case and preserve failures and limitations.
- [ ] **S008** — Record acceptance evidence
  - Write the implementation receipt and outcome report with changed-file hashes, acceptance coverage and actual test logs. Leave unresolved work pending.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Complete provider-switch documentation, replay and cost evidence

## Out of scope

- No new broad research phase or second-plan generation.
- Do not change installed copies, user-global settings or publish without permission.

## Expected files

- skill/plan-and-execute/scripts/routing_telemetry.py
- tools/skill_benchmark.py
- test/optimization/provider_switch_080_self_test.py
- skill/plan-and-execute/references/ROUTING_CONFIG.md
- skill/plan-and-execute/references/MODEL_ROUTING.md
- skill/plan-and-execute/references/WORKFLOW.md
- skill/plan-and-execute/references/PLAN_SPEC.md
- README.md
- README.pt-BR.md
- CHANGELOG.md
- docs/research/20261028-skill-optimization/implementation/080-receipt.json
- docs/research/20261028-skill-optimization/implementation/080-outcome.md

## Dependencies

- 065
- 079

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/research/20261028-skill-optimization/prepared-research/068-provider-switch-handoff.md.
- Read docs/plans/20261028-skill-optimization/ACCEPTANCE_MATRIX.md.
- Use only task 080 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/080-receipt.json.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Use the normative blueprint in report068 for exact entry-rung, repeat, reset, byte-bound and budget semantics; record deviations before changing that contract.
- Preserve the 2026-11-20 owner-preference section of MODEL_ROUTING.md; keep model facts consistent with MODEL_REFRESH_20261120.md (Fable/Astra above the tier map; bare haiku is Haiku 4.5 without effort; Codex ultra never routed).

## Acceptance criteria

- Run all twelve original acceptance cases and preserve disabled-mode compatibility.
- Report reachability and duplicate dispatches separately from unmeasured live quality/cost.
- The targeted contract is validated through the production run_concise composition.
- Compare counterfactual dispatch counts on the original twelve cases; do not present replay as measured model quality or dollar savings.
- Document account-dependent quota, conditional effort capabilities, fallback-disabled behavior and unverified platforms.
- The prepared report is input evidence, not proof that this implementation or its independent review has passed.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_080`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_080`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
