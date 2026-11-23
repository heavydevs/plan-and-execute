---
task_id: "076"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "strong"
reasoning_effort: "high"
complexity: "high"
requirements: "R006, R017, R018, R019, R020, R021, R023, R029, R034"
dependencies: "061, 075"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 076 — Implement bounded deterministic handoff and sanitation

## Objective

Implement the assigned provider-switch contract from report068 and the original twelve-case acceptance matrix.

## Requirements covered

- R006
- R017
- R018
- R019
- R020
- R021
- R023
- R029
- R034

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
  - Validate paths, command evidence and subtask IDs; sanitize before byte-bounded truncation.
- [ ] **S003** — Implement change 2
  - Missing prior reports use deterministic evidence; no extra model call or transcript retention by default.
- [ ] **S004** — Implement change 3
  - Add regression tests for the corresponding original acceptance cases and preserve legacy behavior.
- [ ] **S005** — Apply revised runtime contract 1
  - Build a deterministic capsule from checked evidence; redact secrets before truncation and bound serialized UTF-8 bytes.
- [ ] **S006** — Apply revised runtime contract 2
  - Bind the capsule to source state, destination and next attempt; stale, missing or malformed evidence cannot approve or redirect execution.
- [ ] **S007** — Apply revised runtime contract 3
  - Keep previous-worker hypotheses unverified; additional paid summarization and native transcript retention remain disabled by default.
- [ ] **S008** — Run declared regression checks
  - Run the declared targeted tests through the resource watcher. Implement every assigned acceptance case and preserve failures and limitations.
- [ ] **S009** — Record acceptance evidence
  - Write the implementation receipt and outcome report with changed-file hashes, acceptance coverage and actual test logs. Leave unresolved work pending.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Implement bounded deterministic handoff and sanitation

## Out of scope

- No new broad research phase or second-plan generation.
- Do not change installed copies, user-global settings or publish without permission.

## Expected files

- skill/plan-and-execute/scripts/assistant_triage.py
- skill/plan-and-execute/scripts/run_isolated.py
- test/optimization/provider_switch_076_self_test.py
- skill/plan-and-execute/scripts/provider_handoff.py
- docs/research/20261028-skill-optimization/implementation/076-receipt.json
- docs/research/20261028-skill-optimization/implementation/076-outcome.md

## Dependencies

- 061
- 075

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/research/20261028-skill-optimization/prepared-research/068-provider-switch-handoff.md.
- Read docs/plans/20261028-skill-optimization/ACCEPTANCE_MATRIX.md.
- Use only task 076 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/076-receipt.json.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Use the normative blueprint in report068 for exact entry-rung, repeat, reset, byte-bound and budget semantics; record deviations before changing that contract.

## Acceptance criteria

- Validate paths, command evidence and subtask IDs; sanitize before byte-bounded truncation.
- Missing prior reports use deterministic evidence; no extra model call or transcript retention by default.
- The targeted contract is validated through the production run_concise composition.
- Build a deterministic capsule from checked evidence; redact secrets before truncation and bound serialized UTF-8 bytes.
- Bind the capsule to source state, destination and next attempt; stale, missing or malformed evidence cannot approve or redirect execution.
- Keep previous-worker hypotheses unverified; additional paid summarization and native transcript retention remain disabled by default.
- The prepared report is input evidence, not proof that this implementation or its independent review has passed.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_076`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_076`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
