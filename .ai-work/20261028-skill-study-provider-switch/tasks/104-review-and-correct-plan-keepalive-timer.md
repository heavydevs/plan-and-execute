---
task_id: "104"
status: "pending"
requirements: "R054"
dependencies: "103"
allowed_related_task_reads: "none"
---

# 104 — Independently review and correct opt-in timer implementation, concurrency, OS ownership and cleanup

Objective: Independently review and correct opt-in timer implementation, concurrency, OS ownership and cleanup.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Checkpoints

- [ ] **S001** Read fresh implementation receipt, task 103 source, exact hashes, OS test outputs and design P054.
- [ ] **S002** Dispatch qualified independent review, record actual model/effort/inputs; verify thresholds, concurrent plans, Windows/Linux/macOS and unsupported environments.
- [ ] **S003** Correct all critical/high problems and rerun lifecycle/recovery regressions; preserve strict no-duplicate-runner and no-credit-when-healthy invariants.
- [ ] **S004** Record real review receipt and unresolved native physical-host limitations; never invent execution.

## Scope

Files: `skill/plan-and-execute/scripts/keepalivectl.py`, `skill/plan-and-execute/scripts/keepalive_schedule.py`, `skill/plan-and-execute/scripts/lifecyclectl.py`, `skill/plan-and-execute/scripts/planctl.py`, `skill/plan-and-execute/scripts/run_concise.py`, `skill/plan-and-execute/references/WATCHDOG.md`, `skill/plan-and-execute/references/LIFECYCLE.md`, `test/optimization/keepalive_schedule_lifecycle_self_test.py`.

In: Independently review and correct opt-in timer implementation, concurrency, OS ownership and cleanup within one existing implementation plan.

Out: No additional plan, unauthorized provider execution, global host power modifications, parallel competing supervisor or publishing.

## Guidance

- Read `docs/research/20261028-skill-optimization/prepared-research/103-opt-in-keepalive-scheduler.md` and `docs/plans/20261028-skill-optimization/TASK_INPUTS.json` before work.
- Preserve existing artifacts/checkpoints and only modify declared scope, with actual tests and real independent reviewer on review tasks.
- Record actual receipts under `docs/research/20261028-skill-optimization/implementation/104-receipt.json` and outcomes under `docs/research/20261028-skill-optimization/implementation/104-outcome.md`.

## Acceptance

- Actual independent fresh reviewer evidence and hashes, with all high/critical defects corrected.
- OS timer lifecycle and missing-plan self-removal tested under concurrent plans and hostile path/symlink conditions.
- No active worker/validation terminated or relaunched; power inhibitor remains separately lifetime-scoped.
- Threshold 5/6 boundary, 20-minute trigger and no healthy model calls verified.
- Windows/Linux/macOS mocks and available native checks pass, or task remains pending.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_104`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_104`
