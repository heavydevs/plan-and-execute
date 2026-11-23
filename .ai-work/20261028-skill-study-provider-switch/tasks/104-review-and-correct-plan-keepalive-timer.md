---
task_id: "104"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "max"
reasoning_effort: "xhigh"
complexity: "high"
requirements: "R054"
dependencies: "103"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 104 — Review and correct opt-in plan-scoped keepalive scheduler

## Objective

Review and correct opt-in plan-scoped keepalive scheduler

## Requirements covered

- R054

## Complexity and atomicity

- Complexity: **high**
- Why this is one executable TODO: One feature or independent correction gate.

## Context-isolation boundary

- Why one fresh worker context helps this whole TODO: One reviewer context holds the final 103 diff, scheduler tests and ownership invariants needed to judge and correct them together.
- Context that is genuinely shared by all subtasks:
- Assigned P054/P055 research and task-specific evidence only.
- Concerns deliberately isolated into other TODOs:
- No unrelated transcript or duplicated orchestration

## Isolation contract

This task definition and the exact execution-context files listed below are the only planning artifacts assigned to this worker. Read the task definition first, then read every assigned context file. Do not discover or open any other context file, `PLAN.md`, `TODO.md`, `manifest.json`, `orchestrator.config.json`, result files, logs, or unrelated task definitions. You may read repository source, tests, build files, and runtime output relevant to this task.

Another task definition may be opened only when one of the explicitly allowed task ids above is necessary to resolve a blocked dependency, ambiguity, or validation conflict. Record the task id and reason in the completion report.

## Assigned execution context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Assigned validated learnings

- None

These files are concise, immutable artifacts produced only after another TODO passed deterministic validation. Read exactly the assigned files, never a previous worker transcript or an unassigned learning file.

## Resumable subtask checklist

- [ ] **S001** — Read final 103 evidence
  - Read fresh implementation receipt, task 103 source, exact hashes, OS test outputs and design P054.
- [ ] **S002** — Dispatch qualified independent review
  - Run `python docs/plans/20261028-skill-optimization/support/review_dispatch.py --repo-root . --task 104` in the foreground (rerun on exit 75); use only its DISPATCH line and compact findings. Focus: thresholds, concurrent plans, Windows/Linux/macOS, unsupported hosts.
- [ ] **S003** — Correct critical/high problems and rerun
  - Correct all critical/high problems and rerun lifecycle/recovery regressions; preserve strict no-duplicate-runner and no-credit-when-healthy invariants.
- [ ] **S004** — Record real review receipt and limits
  - Record real review receipt and unresolved native physical-host limitations; never invent execution.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Review and correct opt-in plan-scoped keepalive scheduler

## Out of scope

- No second plan, OS policy changes or unauthorised provider charges

## Expected files

- skill/plan-and-execute/scripts/keepalivectl.py
- skill/plan-and-execute/scripts/keepalive_schedule.py
- skill/plan-and-execute/scripts/lifecyclectl.py
- skill/plan-and-execute/scripts/planctl.py
- skill/plan-and-execute/references/WATCHDOG.md
- skill/plan-and-execute/references/LIFECYCLE.md
- test/optimization/keepalive_schedule_lifecycle_self_test.py
- skill/plan-and-execute/scripts/run_concise.py
- skill/plan-and-execute/references/INSTALLATION.md
- skill/plan-and-execute/references/INSTALLATION.pt-BR.md
- docs/research/20261028-skill-optimization/implementation/104-receipt.json
- docs/research/20261028-skill-optimization/implementation/104-outcome.md

## Dependencies

- 103

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/research/20261028-skill-optimization/prepared-research/103-opt-in-keepalive-scheduler.md
- Follow tasks/104-review-and-correct-plan-keepalive-timer.md and TASK_INPUTS.json
- Review only via review_dispatch.py (synchronous; max route; writes dispatch evidence); fix blocking findings, rerun declared checks, re-dispatch if a reviewed file changed, copy its RECEIPT_REVIEWER fields into the receipt.
- Record actual receipts and outcomes, leave pending until verified.
- Never launch background or asynchronous agents or processes: this headless session ends when you stop calling tools, so anything unfinished is lost.

## Acceptance criteria

- Actual independent fresh reviewer evidence and hashes, with all high/critical defects corrected.
- OS timer lifecycle and missing-plan self-removal tested under concurrent plans and hostile path/symlink conditions.
- No active worker/validation terminated or relaunched; power inhibitor remains separately lifetime-scoped.
- Threshold 5/6 boundary, 20-minute trigger and no healthy model calls verified.
- Windows/Linux/macOS mocks and available native checks pass, or task remains pending.
- A frontier (Fable 5.2 / Astra 6.2) reviewer is accepted only with recorded repeated max-review failure; a reused review session or dispatch is rejected.
- Every 2026-11-20 acceptance addition of task 103 has actual test evidence on the final reviewed hashes.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_104`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_104`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
