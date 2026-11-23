---
task_id: "086"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "max"
reasoning_effort: "xhigh"
complexity: "high"
requirements: "R001, R003, R004, R006, R008, R011, R012, R033, R034, R035, R036, R039, R040, R041, R042, R043, R044, R045, R046, R047, R048, R049, R050, R051, R052, R053, R054, R055, R056, R057, R058, R059, R060, R061, R062, R063, R064, R065, R066, R067, R068, R069, R070, R071, R072, R073"
dependencies: "085"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 086 — Final whole-skill implementation review and handoff

## Objective

Perform the final whole-skill maintenance review and report actual implementation acceptance, without publishing automatically.

## Requirements covered

- R001
- R003
- R004
- R006
- R008
- R011
- R012
- R033
- R034
- R035
- R036
- R039
- R040
- R041
- R042
- R043
- R044
- R045
- R046
- R047
- R048
- R049
- R050
- R051
- R052
- R053
- R054
- R055
- R056
- R057
- R058
- R059
- R060
- R061
- R062
- R063
- R064
- R065
- R066
- R067
- R068
- R069
- R070
- R071
- R072
- R073

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

- Final whole-skill implementation review and handoff

## Out of scope

- No new broad research phase or second-plan generation.
- Do not change installed copies, user-global settings or publish without permission.

## Expected files

- README.md
- README.pt-BR.md
- CHANGELOG.md
- tools/run-repo-checks.js
- docs/research/20261028-skill-optimization/implementation/086-receipt.json
- docs/research/20261028-skill-optimization/implementation/086-outcome.md

## Dependencies

- 085

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/research/20261028-skill-optimization/prepared-research/ARCHITECTURE_AND_SCOPE.md.
- Read docs/plans/20261028-skill-optimization/IMPLEMENTATION_INTEGRATION.md.
- Use only task 086 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/086-receipt.json.
- Review only via review_dispatch.py (synchronous; max route; writes dispatch evidence); fix blocking findings, rerun declared checks, re-dispatch if a reviewed file changed, copy its RECEIPT_REVIEWER fields into the receipt.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- If integration exposes a defect outside this write scope, reopen its owning TODO and correction review with native controllers; do not silently expand scope.
- Final whole-skill review verifies P061-P064, real source hashes, fail-safe wake, test defect detection and measured/unknown tokens.
- Review integrated P065 actual source/review receipts, aesthetic/keyboard/UX correctness, privacy and token costs on final source.
- Final review P066 coding conventions, approved exceptions, real code reuse and UX lazy activation on current code hash.
- Never launch background or asynchronous agents or processes: this headless session ends when you stop calling tools, so anything unfinished is lost.

## Acceptance criteria

- All implementation acceptance cases and required independent code reviews have current evidence.
- Final npm checks and actual package file lists pass or the task remains incomplete.
- The Portuguese final report distinguishes verified behavior, untested platforms and live-provider limitations.
- Current integration evidence covers changed contracts; historical task receipts remain immutable evidence of their recorded revisions.
- P053 final whole-skill review examines actual 101/102 validation/reviewer hashes and unsupported overnight conditions.
- New reviewed 103/104 twenty-minute timer and 105/106 sixth frontier-tier work have actual acceptance evidence.
- Final P056 review checks real 107/108 evidence, current design gate and two review lenses, without mandatory automated performance tests.
- P057 final whole-skill review validates actual 109/110 source hashes, all-failure reporting, focused rechecks and full current-source green suite.
- All P065 122/124/126 independent gates and global current-source acceptance evidence pass before final signoff.
- A frontier (Fable 5.2 / Astra 6.2) reviewer is accepted only with recorded repeated max-review failure; a reused review session or dispatch is rejected.
- The prepared report is input evidence, not proof that this implementation or its independent review has passed.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_086`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_086`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
