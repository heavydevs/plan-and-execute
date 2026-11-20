---
task_id: "104"
status: "pending"
requirements: "R054"
dependencies: "103"
allowed_related_task_reads: "none"
---

# 104 — Review and correct opt-in plan-scoped keepalive scheduler

Objective: Review and correct opt-in plan-scoped keepalive scheduler

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read final 103 evidence — Read fresh implementation receipt, task 103 source, exact hashes, OS test outputs and design P054.
- [ ] **S002** Dispatch qualified independent review — Run `python docs/plans/20261028-skill-optimization/support/review_dispatch.py --repo-root . --task 104` in the foreground (rerun on exit 75); use only its DISPATCH line and compact findings. Focus: thresholds, concurrent plans, Windows/Linux/macOS, unsupported hosts.
- [ ] **S003** Correct critical/high problems and rerun — Correct all critical/high problems and rerun lifecycle/recovery regressions; preserve strict no-duplicate-runner and no-credit-when-healthy invariants.
- [ ] **S004** Record real review receipt and limits — Record real review receipt and unresolved native physical-host limitations; never invent execution.

## Scope

In: Review and correct opt-in plan-scoped keepalive scheduler
Out: No second plan, OS policy changes or unauthorised provider charges
Files: `skill/plan-and-execute/scripts/keepalivectl.py`, `skill/plan-and-execute/scripts/keepalive_schedule.py`, `skill/plan-and-execute/scripts/lifecyclectl.py`, `skill/plan-and-execute/scripts/planctl.py`, `skill/plan-and-execute/references/WATCHDOG.md`, `skill/plan-and-execute/references/LIFECYCLE.md`, `test/optimization/keepalive_schedule_lifecycle_self_test.py`, `skill/plan-and-execute/scripts/run_concise.py`, `skill/plan-and-execute/references/INSTALLATION.md`, `skill/plan-and-execute/references/INSTALLATION.pt-BR.md`, `docs/research/20261028-skill-optimization/implementation/104-receipt.json`, `docs/research/20261028-skill-optimization/implementation/104-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/103-opt-in-keepalive-scheduler.md
- Follow tasks/104-review-and-correct-plan-keepalive-timer.md and TASK_INPUTS.json
- Review only via review_dispatch.py (synchronous; max route; writes dispatch evidence); fix blocking findings, rerun declared checks, re-dispatch if a reviewed file changed, copy its RECEIPT_REVIEWER fields into the receipt.
- Record actual receipts and outcomes, leave pending until verified.
- Never launch background or asynchronous agents or processes: this headless session ends when you stop calling tools, so anything unfinished is lost.

## Acceptance

- Actual independent fresh reviewer evidence and hashes, with all high/critical defects corrected.
- OS timer lifecycle and missing-plan self-removal tested under concurrent plans and hostile path/symlink conditions.
- No active worker/validation terminated or relaunched; power inhibitor remains separately lifetime-scoped.
- Threshold 5/6 boundary, 20-minute trigger and no healthy model calls verified.
- Windows/Linux/macOS mocks and available native checks pass, or task remains pending.
- A frontier (Fable 5.2 / Astra 6.2) reviewer is accepted only with recorded repeated max-review failure; a reused review session or dispatch is rejected.
- Every 2026-11-20 acceptance addition of task 103 has actual test evidence on the final reviewed hashes.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_104`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_104`
