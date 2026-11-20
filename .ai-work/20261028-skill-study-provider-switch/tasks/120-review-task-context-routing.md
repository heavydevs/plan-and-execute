---
task_id: "120"
status: "pending"
requirements: "R064"
dependencies: "119"
allowed_related_task_reads: "none"
---

# 120 — Independently review task-wide economical routing and context safety

Objective: Real fresh max independent review pinned to 119 final source and actual dispatch.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Inspect final prior source and evidence — Inspect final prior source and evidence using only task-specific research, current code and current acceptance evidence.
- [ ] **S002** Dispatch genuine independent model review — Run `python docs/plans/20261028-skill-optimization/support/review_dispatch.py --repo-root . --task 120` in the foreground (rerun on exit 75); use only its DISPATCH line and compact findings.
- [ ] **S003** Probe adverse contract and security cases — Probe adverse contract and security cases using only task-specific research, current code and current acceptance evidence.
- [ ] **S004** Correct findings and revalidate current code — Correct findings and revalidate current code using only task-specific research, current code and current acceptance evidence.
- [ ] **S005** Record real approved evidence or stay pending — Record real approved evidence or stay pending using only task-specific research, current code and current acceptance evidence.

## Scope

In: Independently review task-wide economical routing and context safety
Out: No second orchestrator, unrelated legacy test edits, runtime implementation in this planning amendment or paid model polling.
Files: `skill/plan-and-execute/scripts/routingctl.py`, `skill/plan-and-execute/scripts/planctl.py`, `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/runner_contract.py`, `skill/plan-and-execute/scripts/task_context_router.py`, `skill/plan-and-execute/references/TASK_CONTEXT_ROUTING.md`, `test/optimization/route_aware_context_self_test.py`, `docs/research/20261028-skill-optimization/implementation/120-receipt.json`, `docs/research/20261028-skill-optimization/implementation/120-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/119-task-wide-lazy-routing.md only for this task; architecture and negative cases are mandatory.
- Real fresh max independent review pinned to 119 final source and actual dispatch.
- Probe every manifest task (currently 130) plus a future task, never hard-coding a count; cache unknown, changed source, stale contracts and prompt leaks.
- Check low-cost deterministic lookup, architecture high floor, max reviewer and restricted data path.
- Correct blocking findings; rerun mapped validation and report measured/unknown costs without imaginary savings.
- Use per-phase economic routing and indexed source scope; preserve capability floors and independent reviews.
- Produce actual receipt/outcome only after code, mapped checks and real review; no fabricated success.
- Review only via review_dispatch.py (synchronous; max route; writes dispatch evidence); fix blocking findings, rerun declared checks, re-dispatch if a reviewed file changed, copy its RECEIPT_REVIEWER fields into the receipt.
- Never launch background or asynchronous agents or processes: this headless session ends when you stop calling tools, so anything unfinished is lost.

## Acceptance

- Verified: Real fresh max independent review pinned to 119 final source and actual dispatch.
- Verified: Probe every manifest task (currently 130) plus a future task without a hard-coded count; cache unknown, changed source, stale contracts and prompt leaks.
- Verified: Check low-cost deterministic lookup, architecture high floor, max reviewer and restricted data path.
- Verified: Correct blocking findings; rerun mapped validation and report measured/unknown costs without imaginary savings.
- Real independent reviewer approves final code and all high/critical findings are closed.
- No unauthorized provider/legacy test edits, leaked secrets, duplicate scheduler or lost global validation gate.
- A frontier (Fable 5.2 / Astra 6.2) reviewer is accepted only with recorded repeated max-review failure; a reused review session or dispatch is rejected.
- Every 2026-11-20 acceptance addition of task 119 has actual test evidence on the final reviewed hashes.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_120`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_120`
