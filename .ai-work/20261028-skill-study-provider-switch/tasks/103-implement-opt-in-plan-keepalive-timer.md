---
task_id: "103"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "strong"
reasoning_effort: "high"
complexity: "high"
requirements: "R054"
dependencies: "019, 057, 092, 100, 102"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 103 — Implement opt-in plan-scoped 20-minute recovery scheduler

## Objective

Implement opt-in plan-scoped 20-minute recovery scheduler

## Requirements covered

- R054

## Complexity and atomicity

- Complexity: **high**
- Why this is one executable TODO: One feature or independent correction gate.

## Context-isolation boundary

- Why one fresh worker context helps this whole TODO: Scheduler adapters, the keepalive CLI and lifecycle cleanup share one plan-scoped ownership invariant and one test boundary.
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

- [ ] **S001** — Extend keepalivectl and isolate OS adapters
  - Extend keepalivectl.py (check/pause/resume/schedule, --yes, RESTART states, lock, --max-restarts); move OS adapters (schtasks XML, systemd-user, launchd, cron) into keepalive_schedule.py imported only by keepalivectl; one CLI, one XML source.
- [ ] **S002** — Offer scheduling once at the threshold
  - Offer scheduling exactly once for >=6 pending executable TODOs; consent stored plan-scoped, non-interactive default no, never prompt DIRECT.
- [ ] **S003** — Register exact per-plan scheduler entries
  - Register an exact per-plan host-scheduler entry (Windows Task Scheduler, Linux user systemd timer with safe cron fallback, macOS launchd where permitted) with unique ownership, no privilege escalation.
- [ ] **S004** — Resume only dead runnable work per tick
  - At each twenty-minute tick check runner lease and actual runnable state; only resume dead/awaiting/cooldown-due, never restart live, silent, blocked, permission-pending or validation-active work.
- [ ] **S005** — Unregister and self-clean without power changes
  - Unregister on success, cancel, reset or opt-out, plus safe self-clean on next tick if a plan vanished; release nothing power-related (101's finalizer still runs; power_inhibit.py is out of scope).
- [ ] **S006** — Validate boundaries, concurrency and cleanup
  - Validate all threshold boundaries, multi-plan concurrency, restart budget, OS mocks, crash and termination cleanup; real CI evidence only.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Implement opt-in plan-scoped 20-minute recovery scheduler

## Out of scope

- No second plan, OS policy changes or unauthorised provider charges

## Expected files

- skill/plan-and-execute/scripts/keepalivectl.py
- skill/plan-and-execute/scripts/keepalive_schedule.py
- skill/plan-and-execute/scripts/lifecyclectl.py
- skill/plan-and-execute/scripts/planctl.py
- skill/plan-and-execute/scripts/run_concise.py
- skill/plan-and-execute/references/WATCHDOG.md
- skill/plan-and-execute/references/LIFECYCLE.md
- skill/plan-and-execute/references/INSTALLATION.md
- skill/plan-and-execute/references/INSTALLATION.pt-BR.md
- test/optimization/keepalive_schedule_lifecycle_self_test.py
- docs/research/20261028-skill-optimization/implementation/103-receipt.json
- docs/research/20261028-skill-optimization/implementation/103-outcome.md

## Dependencies

- 019
- 057
- 092
- 100
- 102

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/research/20261028-skill-optimization/prepared-research/103-opt-in-keepalive-scheduler.md
- Follow tasks/103-implement-opt-in-plan-keepalive-timer.md and TASK_INPUTS.json
- Implement scoped behavior and run native/mocked deterministic tests
- Record actual receipts and outcomes, leave pending until verified.

## Acceptance criteria

- Plans with 0–5 pending executable tasks are not offered timer, 6+ are offered once; opt-in only; count review tasks where actually executable.
- Twenty-minute scheduled checks are deterministic and use no model tokens when healthy; no automatic session chat wake claims.
- Dead runnable runner is restarted at most once per tick with lock/lease and restart-loop budget; no restart of live/silent/blocked/quota-not-due runner.
- Native Windows Task Scheduler, Linux systemd-user timer (safe cron fallback), and macOS launchd conditional adapters install/remove only their plan-scoped jobs without modifying unrelated jobs.
- Terminal success/cancel/reset removes OS timer and owned metadata before plan control cleanup; missing plan next tick triggers safe self-removal; multiple plans isolated.
- When WSL, sandbox, guest VM or host limitations prevent reliable host scheduling, report unsupported instead of claiming wake capability.
- Sleep inhibition remains separate, continuous lease owned by task 101; no timer-powered wake guarantee, no global power settings or synthetic input.
- Mocked OS tests and real available platform smoke checks; independently reviewed task 104 required before integration 082.
- check --plan <missing> from the scheduled task deletes only PlanAndExecuteKeepalive-<plan_key> after confirming the plan directory is gone (not merely unreadable or unmounted) and exits 0.
- The Windows task stays InteractiveToken/LeastPrivilege without WakeToRun, and docs state that it runs only while the user is logged on.
- A runner launched by a tick survives the end of the scheduled action.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_103`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_103`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
