---
task_id: "091"
status: "pending"
requirements: "R048"
dependencies: "019,021,049,053,057"
allowed_related_task_reads: "none"
---

# 091 — Implement create bounded repair tasks for complex active-plan blockers

Objective: When an active task is blocked by complex product bugs or flawed architecture, safely add focused design, repair and monitored validation TODOs without losing checkpoints.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read evidence — Read docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261031.md, assigned prepared research and materially affected source files.
- [ ] **S002** Implement contract 1 — Distinguish a reproducible complex architectural/product defect from resource outages, quotas, flakiness or a cheap local fix.
- [ ] **S003** Implement contract 2 — Insert one or more independent design, repair and validation TODOs using lease-safe replayable graph mutation.
- [ ] **S004** Implement contract 3 — Deduplicate blocker fingerprints, keep DAG and bounded expansion budgets, and preserve original task status.
- [ ] **S005** Implement contract 4 — Validate fixes with mapped health, resource and log monitoring before resuming blocked work.
- [ ] **S006** Run tests — Implement test/optimization/blocked_task_split_self_test.py and run mapped validation plus feature negative cases.
- [ ] **S007** Record implementation — Record real implementation and test evidence in docs/research/20261028-skill-optimization/implementation/091-receipt.json and docs/research/20261028-skill-optimization/implementation/091-outcome.md.

## Scope

In: When an active task is blocked by complex product bugs or flawed architecture, safely add focused design, repair and monitored validation TODOs without losing checkpoints.
Out: No second plan or unrelated changes.; No installation, provider login, publishing or user-global configuration changes without permission.
Files: `skill/plan-and-execute/scripts/planctl.py`, `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/lifecyclectl.py`, `skill/plan-and-execute/scripts/runner_contract.py`, `skill/plan-and-execute/references/WORKFLOW.md`, `skill/plan-and-execute/references/PLAN_SPEC.md`, `skill/plan-and-execute/references/TEST_RESOURCE_MONITORING.md`, `test/optimization/blocked_task_split_self_test.py`, `docs/research/20261028-skill-optimization/implementation/091-receipt.json`, `docs/research/20261028-skill-optimization/implementation/091-outcome.md`

## Guidance

- Read docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261031.md.
- Follow task 091 in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Preserve exact user intent, bounded context, security floors and real deterministic tests.
- Refresh only materially changed facts from assigned prepared reports 006, 028, 060, 062.
- Preserve evidence in docs/research/20261028-skill-optimization/implementation/091-receipt.json and docs/research/20261028-skill-optimization/implementation/091-outcome.md; do not mark a pending task done without validation.

## Acceptance

- A complex reproducible blocker creates scoped repair/design TODOs and suspends the original task.
- A temporary outage, quota limit or simple patch does not add tasks or escalate architecture reasoning.
- Idempotency prevents recursive task explosion; leases, cycles and interrupted writes are handled.
- Original validated subtasks survive, and newly created tests must pass before unblocking.
- Implementation and review remain pending until actual execution evidence exists.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_091`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_091`
