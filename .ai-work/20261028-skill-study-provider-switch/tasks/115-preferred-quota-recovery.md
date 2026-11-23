---
task_id: "115"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "strong"
reasoning_effort: "high"
complexity: "high"
requirements: "R061, R062"
dependencies: "023, 055, 075, 100, 104, 106"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 115 — Implement preferred-provider priority restoration and durable quota resume

## Objective

Re-rank allowed providers by user preference before each new safe dispatch only.

## Requirements covered

- R061
- R062

## Complexity and atomicity

- Complexity: **high**
- Why this is one executable TODO: One shared runtime invariant and focused independent validation boundary.

## Context-isolation boundary

- Why one fresh worker context helps this whole TODO: Changes share one source/test contract that can be verified without reading unrelated tasks.
- Context that is genuinely shared by all subtasks:
- Only assigned research, relevant current source symbols and accepted dependency receipts.
- Concerns deliberately isolated into other TODOs:
- Do not load unrelated studies, historical transcripts, other provider guides or raw success logs.

## Isolation contract

This task definition and the exact execution-context files listed below are the only planning artifacts assigned to this worker. Read the task definition first, then read every assigned context file. Do not discover or open any other context file, `PLAN.md`, `TODO.md`, `manifest.json`, `orchestrator.config.json`, result files, logs, or unrelated task definitions. You may read repository source, tests, build files, and runtime output relevant to this task.

Another task definition may be opened only when one of the explicitly allowed task ids above is necessary to resolve a blocked dependency, ambiguity, or validation conflict. Record the task id and reason in the completion report.

## Assigned execution context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Assigned validated learnings

- None

These files are concise, immutable artifacts produced only after another TODO passed deterministic validation. Read exactly the assigned files, never a previous worker transcript or an unassigned learning file.

## Resumable subtask checklist

- [ ] **S001** — Inspect assigned architecture and relevant source symbols
  - Inspect assigned architecture and relevant source symbols using only task-specific research, current code and current acceptance evidence.
- [ ] **S002** — Implement bounded contract without duplicate framework
  - Implement bounded contract without duplicate framework using only task-specific research, current code and current acceptance evidence.
- [ ] **S003** — Integrate monitoring, permissions and route
  - Integrate monitoring, permissions and route using only task-specific research, current code and current acceptance evidence.
- [ ] **S004** — Execute adversarial focused validation
  - Execute adversarial focused validation using only task-specific research, current code and current acceptance evidence.
- [ ] **S005** — Record real product evidence or stay pending
  - Record real product evidence or stay pending using only task-specific research, current code and current acceptance evidence.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Implement preferred-provider priority restoration and durable quota resume

## Out of scope

- No second orchestrator, unrelated legacy test edits, runtime implementation in this planning amendment or paid model polling.

## Expected files

- skill/plan-and-execute/scripts/availability.py
- skill/plan-and-execute/scripts/run_isolated.py
- skill/plan-and-execute/scripts/planctl.py
- skill/plan-and-execute/scripts/keepalivectl.py
- skill/plan-and-execute/scripts/jobctl.py
- skill/plan-and-execute/scripts/quota_resume.py
- skill/plan-and-execute/references/QUOTA_RECOVERY.md
- test/optimization/quota_recovery_self_test.py
- docs/research/20261028-skill-optimization/implementation/115-receipt.json
- docs/research/20261028-skill-optimization/implementation/115-outcome.md

## Dependencies

- 023
- 055
- 075
- 100
- 104
- 106

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/research/20261028-skill-optimization/prepared-research/115-quota-auto-recovery.md only for this task; architecture and negative cases are mandatory.
- Re-rank allowed providers by user preference before each new safe dispatch only.
- Persist quota pool, retry-after and unknown reset; distinguish auth/billing/environment errors from quota.
- When every allowed provider is quota limited persist PAUSED_QUOTA and one fenced durable one-shot scheduled recheck; use existing scheduler, even for fewer than six tasks.
- Zero paid polling; bounded jitter/backoff; no preemption, duplicate work, secret/permission bypass or sleeping host guarantee.
- Cover A->B->A preference, no provider, multiple pools, scheduler missing, clock skew, cancel and crash/resume.
- Use per-phase economic routing and indexed source scope; preserve capability floors and independent reviews.
- Produce actual receipt/outcome only after code, mapped checks and real review; no fabricated success.
- Provider preference is per phase: implementation Antigravity > Codex > Claude; architecture and review Codex > Claude; re-rank only before a new safe dispatch.

## Acceptance criteria

- Verified: Re-rank allowed providers by user preference before each new safe dispatch only.
- Verified: Persist quota pool, retry-after and unknown reset; distinguish auth/billing/environment errors from quota.
- Verified: When every allowed provider is quota limited persist PAUSED_QUOTA and one fenced durable one-shot scheduled recheck; use existing scheduler, even for fewer than six tasks.
- Verified: Zero paid polling; bounded jitter/backoff; no preemption, duplicate work, secret/permission bypass or sleeping host guarantee.
- Actual source-bound tests, negative fixtures and compact cost evidence establish behavior without inventing savings.
- No unauthorized provider/legacy test edits, leaked secrets, duplicate scheduler or lost global validation gate.
- credits exhausted/depleted (matched by the availability.py quota regex) is class credits_exhausted: reset unknown, never paid-probed, restored only on an observed non-paid signal or operator action, never escalated to frontier.
- Fixture: with Codex exhausted, implementation goes to Antigravity and review to Claude Opus 5.5.
- Fixture: when Codex returns, only the next eligible dispatch goes back to Codex.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_115`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_115`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
