---
task_id: "083"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "max"
reasoning_effort: "xhigh"
complexity: "high"
requirements: "R001, R003, R004, R005, R039, R041, R042, R043, R044"
dependencies: "082"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 083 — Review and correct end-to-end integration

## Objective

Review and repair cross-feature integration defects with actual max-capability review evidence.

## Requirements covered

- R001
- R003
- R004
- R005
- R039
- R041
- R042
- R043
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

- [ ] **S001** — Read assigned decision and pin baseline
  - Read docs/research/20261028-skill-optimization/prepared-research/ARCHITECTURE_AND_SCOPE.md, docs/plans/20261028-skill-optimization/IMPLEMENTATION_INTEGRATION.md. Confirm source applicability; do not repeat broad research.
- [ ] **S002** — Implement change 1
  - Check integration against every prepared decision and original provider-switch acceptance case; do not create another plan.
- [ ] **S003** — Implement change 2
  - Correct regressions and report exact test commands, logs, package manifests and unsupported platforms.
- [ ] **S004** — Implement change 3
  - Preserve implementation and research evidence; do not install, commit, push or publish without permission.
- [ ] **S005** — Run declared regression checks
  - Run the declared targeted tests through the resource watcher. Implement every assigned acceptance case and preserve failures and limitations.
- [ ] **S006** — Record acceptance evidence
  - Write the implementation receipt and outcome report with changed-file hashes, acceptance coverage and actual test logs. Leave unresolved work pending.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Review and correct end-to-end integration

## Out of scope

- No new broad research phase or second-plan generation.
- Do not change installed copies, user-global settings or publish without permission.

## Expected files

- README.md
- README.pt-BR.md
- CHANGELOG.md
- tools/run-repo-checks.js
- tools/run-skill-self-test.js
- test/optimization/integration_082_self_test.py
- docs/research/20261028-skill-optimization/implementation/083-receipt.json
- docs/research/20261028-skill-optimization/implementation/083-outcome.md

## Dependencies

- 082

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/research/20261028-skill-optimization/prepared-research/ARCHITECTURE_AND_SCOPE.md.
- Read docs/plans/20261028-skill-optimization/IMPLEMENTATION_INTEGRATION.md.
- Use only task 083 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/083-receipt.json.
- Review only via review_dispatch.py (synchronous; max route; writes dispatch evidence); fix blocking findings, rerun declared checks, re-dispatch if a reviewed file changed, copy its RECEIPT_REVIEWER fields into the receipt.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- If integration exposes a defect outside this write scope, reopen its owning TODO and correction review with native controllers; do not silently expand scope.
- Never launch background or asynchronous agents or processes: this headless session ends when you stop calling tools, so anything unfinished is lost.

## Acceptance criteria

- All implementation acceptance cases and required independent code reviews have current evidence.
- Final npm checks and actual package file lists pass or the task remains incomplete.
- The Portuguese final report distinguishes verified behavior, untested platforms and live-provider limitations.
- Current integration evidence covers changed contracts; historical task receipts remain immutable evidence of their recorded revisions.
- A frontier (Fable 5.2 / Astra 6.2) reviewer is accepted only with recorded repeated max-review failure; a reused review session or dispatch is rejected.
- Every 2026-11-20 acceptance addition of task 082 has actual test evidence on the final reviewed hashes.
- The prepared report is input evidence, not proof that this implementation or its independent review has passed.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_083`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_083`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
