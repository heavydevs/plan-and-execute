---
task_id: "068"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "strong"
reasoning_effort: "high"
complexity: "high"
requirements: "R002, R003, R004, R005, R006, R007, R012, R013, R014, R015, R016, R017, R018, R019, R020, R021, R022, R023, R024, R025, R026, R027, R028, R029, R030, R031, R032, R034, R037, R038, R039, R042, R044"
dependencies: "001, 021, 023, 027, 049, 061, 065"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 068 — Implement provider-switch contract fixtures from the prepared decision

## Objective

Encode the prepared provider-switch decision as reusable configuration fixtures, baseline replay and expected outcomes; runtime changes belong to tasks070-080.

## Requirements covered

- R002
- R003
- R004
- R005
- R006
- R007
- R012
- R013
- R014
- R015
- R016
- R017
- R018
- R019
- R020
- R021
- R022
- R023
- R024
- R025
- R026
- R027
- R028
- R029
- R030
- R031
- R032
- R034
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
  - Read docs/research/20261028-skill-optimization/prepared-research/068-provider-switch-handoff.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** — Implement revised contract 1
  - Encode all twelve original acceptance cases as fixtures with separate legacy behavior and expected opt-in results.
- [ ] **S003** — Implement revised contract 2
  - Cover no-op aliases, unavailable providers, phase state, insufficient budgets and attempt-bound sanitized capsules in the fake-provider inputs.
- [ ] **S004** — Implement revised contract 3
  - Assign runtime expectations to owners070-080 and verify that this fixture task makes no runner or configuration implementation claim.
- [ ] **S005** — Validate all assigned positive and negative cases
  - Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** — Record implementation evidence for independent review
  - Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Implement provider-switch contract fixtures from the prepared decision

## Out of scope

- No new broad research phase or second-plan generation.
- Do not change installed copies, user-global settings or publish without permission.

## Expected files

- test/optimization/provider_switch_handoff_self_test.py
- test/optimization/provider_switch_cases.json
- docs/research/20261028-skill-optimization/implementation/068-receipt.json
- docs/research/20261028-skill-optimization/implementation/068-outcome.md

## Dependencies

- 001
- 021
- 023
- 027
- 049
- 061
- 065

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/research/20261028-skill-optimization/prepared-research/068-provider-switch-handoff.md.
- Use only task 068 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/068-receipt.json.
- Task068 owns contract fixtures only. Tasks070-080 implement runtime behavior; do not duplicate their changes here.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- TODO 068 encodes the decision below as twelve-case fixtures and compatibility expectations only. Runtime/config/state/prompt changes are owned by 070, 072, 074, 076, 078 and 080, each with its following independent review.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance criteria

- All twelve provider-switch acceptance cases have explicit inputs and expected outputs.
- Fixtures distinguish provider/phase identity, unavailable candidates, duplicate dispatches and bounded attempt reservation.
- Legacy replay remains separate from expected opt-in behavior; no runtime implementation is claimed by this fixture task.
- Each case in test/optimization/provider_switch_cases.json names its owner task (070-080).
- New fixtures cover the antigravity/codex/claude implementation chain and the codex/claude review chain.
- Codex out of credits is availability: no functional failure and no escalation.
- claude-fable-5-2, gpt-6.2-astra and gemini-4-carbon-* are never useful rungs.
- A03: in map v8 Claude strong and max are both claude-opus-5-5; a no-op is counted only when model and effort are equal.
- Prepared research is not proof of implementation or independent-review completion.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_068`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_068`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
