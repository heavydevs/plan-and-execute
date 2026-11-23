---
task_id: "096"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "max"
reasoning_effort: "xhigh"
complexity: "high"
requirements: "R050"
dependencies: "095"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 096 — Review and correct offer other-provider setup and login before creating a plan

## Objective

Independently review and correct offer other-provider setup and login before creating a plan using actual implementation and validation evidence.

## Requirements covered

- R050

## Complexity and atomicity

- Complexity: **high**
- Why this is one executable TODO: One coherent outcome, focused tests and an independent review boundary.

## Context-isolation boundary

- Why one fresh worker context helps this whole TODO: Steps share one observable implementation or review outcome.
- Context that is genuinely shared by all subtasks:
- Only assigned contract and actual code evidence.
- Concerns deliberately isolated into other TODOs:
- Unrelated TODOs and old transcripts are excluded.

## Isolation contract

This task definition and the exact execution-context files listed below are the only planning artifacts assigned to this worker. Read the task definition first, then read every assigned context file. Do not discover or open any other context file, `PLAN.md`, `TODO.md`, `manifest.json`, `orchestrator.config.json`, result files, logs, or unrelated task definitions. You may read repository source, tests, build files, and runtime output relevant to this task.

Another task definition may be opened only when one of the explicitly allowed task ids above is necessary to resolve a blocked dependency, ambiguity, or validation conflict. Record the task id and reason in the completion report.

## Assigned execution context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Assigned validated learnings

- None

These files are concise, immutable artifacts produced only after another TODO passed deterministic validation. Read exactly the assigned files, never a previous worker transcript or an unassigned learning file.

## Resumable subtask checklist

- [ ] **S001** — Read implementation
  - Review the actual code, test results and receipt from task 095, not a previous conversation.
- [ ] **S002** — Independent review
  - Run `python docs/plans/20261028-skill-optimization/support/review_dispatch.py --repo-root . --task 096` in the foreground (rerun on exit 75); use only its DISPATCH line and compact findings.
- [ ] **S003** — Correct high-risk defects
  - Correct critical/high findings or leave the task pending with evidence.
- [ ] **S004** — Rerun regressions
  - Run test/optimization/provider_readiness_gate_self_test.py and all feature acceptance and negative cases through mapped validation.
- [ ] **S005** — Record review
  - Record actual review/validation results in docs/research/20261028-skill-optimization/implementation/096-receipt.json and docs/research/20261028-skill-optimization/implementation/096-outcome.md.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Review and correct offer other-provider setup and login before creating a plan

## Out of scope

- No second plan or unrelated changes.
- No installation, provider login, publishing or user-global configuration changes without permission.

## Expected files

- skill/plan-and-execute/scripts/preplanctl.py
- skill/plan-and-execute/scripts/configure.py
- skill/plan-and-execute/scripts/model_catalogctl.py
- skill/plan-and-execute/scripts/routingctl.py
- skill/plan-and-execute/references/INTAKE.md
- skill/plan-and-execute/references/ORCHESTRATION.md
- skill/plan-and-execute/references/PLANNING_PROTOCOL.md
- skill/plan-and-execute/references/ROUTING_CONFIG.md
- test/optimization/provider_readiness_gate_self_test.py
- docs/research/20261028-skill-optimization/implementation/096-receipt.json
- docs/research/20261028-skill-optimization/implementation/096-outcome.md

## Dependencies

- 095

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261031.md.
- Follow task 096 in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Preserve exact user intent, bounded context, security floors and real deterministic tests.
- Review only via review_dispatch.py (synchronous; max route; writes dispatch evidence); fix blocking findings, rerun declared checks, re-dispatch if a reviewed file changed, copy its RECEIPT_REVIEWER fields into the receipt.
- Preserve evidence in docs/research/20261028-skill-optimization/implementation/096-receipt.json and docs/research/20261028-skill-optimization/implementation/096-outcome.md; do not mark a pending task done without validation.
- Never launch background or asynchronous agents or processes: this headless session ends when you stop calling tools, so anything unfinished is lost.

## Acceptance criteria

- Record a real fresh independent reviewer route and exact reviewed input hashes.
- Verify: Each discovered agent needing setup/login gets a separate named consent question only during new-plan preparation.
- Verify: Without consent no login, config mutation, token exposure or paid model call occurs.
- Verify: Ready agents are not re-prompted; declined and unsupported agents have explicit reasons.
- Verify: Existing-plan resume, running TODOs, DIRECT changes and shell commands never run this questionnaire.
- Verify: Unknown availability cannot silently widen a forbidden provider chain or lower capability.
- No unresolved critical/high finding or missing required reviewer may be marked complete.
- A frontier (Fable 5.2 / Astra 6.2) reviewer is accepted only with recorded repeated max-review failure; a reused review session or dispatch is rejected.
- Every 2026-11-20 acceptance addition of task 095 has actual test evidence on the final reviewed hashes.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_096`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_096`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
