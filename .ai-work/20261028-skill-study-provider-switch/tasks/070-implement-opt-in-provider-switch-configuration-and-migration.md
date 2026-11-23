---
task_id: "070"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "strong"
reasoning_effort: "high"
complexity: "high"
requirements: "R006, R012, R013, R014, R015, R016, R017, R024, R025, R026, R027, R028, R030, R031, R037"
dependencies: "025, 047, 069"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 070 — Implement opt-in provider-switch configuration and migration

## Objective

Implement the assigned provider-switch contract from report068 and the original twelve-case acceptance matrix.

## Requirements covered

- R006
- R012
- R013
- R014
- R015
- R016
- R017
- R024
- R025
- R026
- R027
- R028
- R030
- R031
- R037

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
  - Strict mode/subkey validation and fingerprints; legacy default stays unchanged.
- [ ] **S003** — Implement change 2
  - Version1 full snapshots do not inherit global options; schema1-4 remain readable.
- [ ] **S004** — Implement change 3
  - Add regression tests for the corresponding original acceptance cases and preserve legacy behavior.
- [ ] **S005** — Apply revised runtime contract 1
  - Strictly validate provider_switch.mode and handoff subkeys; default legacy mode keeps previous behavior.
- [ ] **S006** — Apply revised runtime contract 2
  - Fingerprint every route-affecting option; full version1 config snapshots do not inherit new global settings.
- [ ] **S007** — Run declared regression checks
  - Run the declared targeted tests through the resource watcher. Implement every assigned acceptance case and preserve failures and limitations.
- [ ] **S008** — Record acceptance evidence
  - Write the implementation receipt and outcome report with changed-file hashes, acceptance coverage and actual test logs. Leave unresolved work pending.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Implement opt-in provider-switch configuration and migration

## Out of scope

- No new broad research phase or second-plan generation.
- Do not change installed copies, user-global settings or publish without permission.

## Expected files

- skill/plan-and-execute/scripts/routing_config.py
- skill/plan-and-execute/scripts/configure.py
- test/optimization/provider_switch_070_self_test.py
- skill/plan-and-execute/references/ROUTING_CONFIG.md
- skill/plan-and-execute/scripts/availability.py
- docs/research/20261028-skill-optimization/implementation/070-receipt.json
- docs/research/20261028-skill-optimization/implementation/070-outcome.md

## Dependencies

- 025
- 047
- 069

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/research/20261028-skill-optimization/prepared-research/068-provider-switch-handoff.md.
- Read docs/plans/20261028-skill-optimization/ACCEPTANCE_MATRIX.md.
- Use only task 070 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/070-receipt.json.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Use the normative blueprint in report068 for exact entry-rung, repeat, reset, byte-bound and budget semantics; record deviations before changing that contract.

## Acceptance criteria

- Strict mode/subkey validation and fingerprints; legacy default stays unchanged.
- Version1 full snapshots do not inherit global options; schema1-4 remain readable.
- The targeted contract is validated through the production run_concise composition.
- A05: the third provider of a strong chain is reachable at max_attempts=8, or a documented budget rule rejects the case.
- A06: ladder and dispatch use one chain derived from tier_routes when present, else provider_order.
- The prepared report is input evidence, not proof that this implementation or its independent review has passed.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_070`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_070`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
