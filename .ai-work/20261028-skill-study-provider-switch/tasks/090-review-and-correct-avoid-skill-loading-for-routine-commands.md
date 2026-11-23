---
task_id: "090"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "max"
reasoning_effort: "xhigh"
complexity: "high"
requirements: "R047"
dependencies: "089"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 090 — Review and correct avoid skill loading for routine commands and trivial changes

## Objective

Independently review and correct avoid skill loading for routine commands and trivial changes using actual implementation and validation evidence.

## Requirements covered

- R047

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
  - Review the actual code, test results and receipt from task 089, not a previous conversation.
- [ ] **S002** — Independent review
  - Run `python docs/plans/20261028-skill-optimization/support/review_dispatch.py --repo-root . --task 090` in the foreground (rerun on exit 75); use only its DISPATCH line and compact findings.
- [ ] **S003** — Correct high-risk defects
  - Correct critical/high findings or leave the task pending with evidence.
- [ ] **S004** — Rerun regressions
  - Run test/optimization/skill_activation_negatives_self_test.py and all feature acceptance and negative cases through mapped validation.
- [ ] **S005** — Record review
  - Record actual review/validation results in docs/research/20261028-skill-optimization/implementation/090-receipt.json and docs/research/20261028-skill-optimization/implementation/090-outcome.md.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Review and correct avoid skill loading for routine commands and trivial changes

## Out of scope

- No second plan or unrelated changes.
- No installation, provider login, publishing or user-global configuration changes without permission.

## Expected files

- skill/plan-and-execute/SKILL.md
- skill/plan-and-execute/agents/openai.yaml
- skill/plan-and-execute/references/ROUTING.md
- skill/validate-or-fix/SKILL.md
- skill/plan-and-execute/references/routing-evals.json
- test/optimization/skill_activation_negatives_self_test.py
- docs/research/20261028-skill-optimization/implementation/090-receipt.json
- docs/research/20261028-skill-optimization/implementation/090-outcome.md

## Dependencies

- 089

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261031.md.
- Follow task 090 in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Preserve exact user intent, bounded context, security floors and real deterministic tests.
- Review only via review_dispatch.py (synchronous; max route; writes dispatch evidence); fix blocking findings, rerun declared checks, re-dispatch if a reviewed file changed, copy its RECEIPT_REVIEWER fields into the receipt.
- Preserve evidence in docs/research/20261028-skill-optimization/implementation/090-receipt.json and docs/research/20261028-skill-optimization/implementation/090-outcome.md; do not mark a pending task done without validation.
- Never launch background or asynchronous agents or processes: this headless session ends when you stop calling tools, so anything unfinished is lost.

## Acceptance criteria

- Record a real fresh independent reviewer route and exact reviewed input hashes.
- Verify: Simple shell commands, one-file reads and trivial edits do not implicitly load the full skill.
- Verify: Explicit plan/lifecycle commands and genuine multi-workstream jobs still activate.
- Verify: Tiny discoverable metadata cost is acknowledged; there is no claim of zero skill-related tokens.
- Verify: Held-out host evaluations measure false positives/negatives and token impact, not keyword assertions alone.
- No unresolved critical/high finding or missing required reviewer may be marked complete.
- A frontier (Fable 5.2 / Astra 6.2) reviewer is accepted only with recorded repeated max-review failure; a reused review session or dispatch is rejected.
- Every 2026-11-20 acceptance addition of task 089 has actual test evidence on the final reviewed hashes.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_090`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_090`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
