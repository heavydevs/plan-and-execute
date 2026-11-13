---
task_id: "103"
status: "pending"
requirements: "R054"
dependencies: "019,057,092,100,102"
allowed_related_task_reads: "none"
---

# 103 — Implement opt-in per-plan twenty-minute recovery timer and exact owned scheduler cleanup

Objective: Implement opt-in per-plan twenty-minute recovery timer and exact owned scheduler cleanup.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Checkpoints

- [ ] **S001** Read docs/research/20261028-skill-optimization/prepared-research/103-opt-in-keepalive-scheduler.md and existing keepalivectl/watchdog/lifecycle logic; use it rather than a second orchestration skill.
- [ ] **S002** Offer scheduling exactly once for >=6 pending executable TODOs; consent stored plan-scoped, non-interactive default no, never prompt DIRECT.
- [ ] **S003** Register an exact per-plan host-scheduler entry (Windows Task Scheduler, Linux user systemd timer with safe cron fallback, macOS launchd where permitted) with unique ownership, no privilege escalation.
- [ ] **S004** At each twenty-minute tick check runner lease and actual runnable state; only resume dead/awaiting/cooldown-due, never restart live, silent, blocked, permission-pending or validation-active work.
- [ ] **S005** Unregister on success, cancel, reset or opt-out, plus safe self-clean on next tick if a plan vanished; release host power inhibitor as separate finalizer.
- [ ] **S006** Validate all threshold boundaries, multi-plan concurrency, restart budget, OS mocks, crash and termination cleanup; real CI evidence only.

## Scope

Files: `skill/plan-and-execute/scripts/keepalivectl.py`, `skill/plan-and-execute/scripts/keepalive_schedule.py`, `skill/plan-and-execute/scripts/lifecyclectl.py`, `skill/plan-and-execute/scripts/planctl.py`, `skill/plan-and-execute/scripts/run_concise.py`, `skill/plan-and-execute/references/WATCHDOG.md`, `skill/plan-and-execute/references/LIFECYCLE.md`, `skill/plan-and-execute/references/INSTALLATION.md`, `skill/plan-and-execute/references/INSTALLATION.pt-BR.md`, `test/optimization/keepalive_schedule_lifecycle_self_test.py`.

In: Implement opt-in per-plan twenty-minute recovery timer and exact owned scheduler cleanup within one existing implementation plan.

Out: No additional plan, unauthorized provider execution, global host power modifications, parallel competing supervisor or publishing.

## Guidance

- Read `docs/research/20261028-skill-optimization/prepared-research/103-opt-in-keepalive-scheduler.md` and `docs/plans/20261028-skill-optimization/TASK_INPUTS.json` before work.
- Preserve existing artifacts/checkpoints and only modify declared scope, with actual tests and real independent reviewer on review tasks.
- Record actual receipts under `docs/research/20261028-skill-optimization/implementation/103-receipt.json` and outcomes under `docs/research/20261028-skill-optimization/implementation/103-outcome.md`.

## Acceptance

- Plans with 0–5 pending executable tasks are not offered timer, 6+ are offered once; opt-in only; count review tasks where actually executable.
- Twenty-minute scheduled checks are deterministic and use no model tokens when healthy; no automatic session chat wake claims.
- Dead runnable runner is restarted at most once per tick with lock/lease and restart-loop budget; no restart of live/silent/blocked/quota-not-due runner.
- Native Windows Task Scheduler, Linux systemd-user timer (safe cron fallback), and macOS launchd conditional adapters install/remove only their plan-scoped jobs without modifying unrelated jobs.
- Terminal success/cancel/reset removes OS timer and owned metadata before plan control cleanup; missing plan next tick triggers safe self-removal; multiple plans isolated.
- When WSL, sandbox, guest VM or host limitations prevent reliable host scheduling, report unsupported instead of claiming wake capability.
- Sleep inhibition remains separate, continuous lease owned by task 101; no timer-powered wake guarantee, no global power settings or synthetic input.
- Mocked OS tests and real available platform smoke checks; independently reviewed task 104 required before integration 082.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_103`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_103`
