---
task_id: "120"
status: "pending"
requirements: "R064"
dependencies: "119"
allowed_related_task_reads: "none"
---

# 120 — Independently review task-wide economical routing and context safety

**Objective:** Real fresh max independent review pinned to 119 final source and actual dispatch.

**Architecture:** read only [assigned study](../../../docs/research/20261028-skill-optimization/prepared-research/119-task-wide-lazy-routing.md) and actual affected source. No work is yet implemented.

## Checkpoints

- [ ] S001 — Inspect final prior source and evidence: Inspect final prior source and evidence using only task-specific research, current code and current acceptance evidence.
- [ ] S002 — Dispatch genuine independent model review: Dispatch genuine independent model review using only task-specific research, current code and current acceptance evidence.
- [ ] S003 — Probe adverse contract and security cases: Probe adverse contract and security cases using only task-specific research, current code and current acceptance evidence.
- [ ] S004 — Correct findings and revalidate current code: Correct findings and revalidate current code using only task-specific research, current code and current acceptance evidence.
- [ ] S005 — Record real approved evidence or stay pending: Record real approved evidence or stay pending using only task-specific research, current code and current acceptance evidence.

## Implementation and review contract

- Read docs/research/20261028-skill-optimization/prepared-research/119-task-wide-lazy-routing.md only for this task; architecture and negative cases are mandatory.
- Real fresh max independent review pinned to 119 final source and actual dispatch.
- Probe all 120 current tasks and future task, cache unknown, changed source, stale contracts and prompt leaks.
- Check low-cost deterministic lookup, architecture high floor, max reviewer and restricted data path.
- Correct blocking findings; rerun mapped validation and report measured/unknown costs without imaginary savings.
- Use per-phase economic routing and indexed source scope; preserve capability floors and independent reviews.
- Produce actual receipt/outcome only after code, mapped checks and real review; no fabricated success.

## Acceptance

- Verified: Real fresh max independent review pinned to 119 final source and actual dispatch.
- Verified: Probe all 120 current tasks and future task, cache unknown, changed source, stale contracts and prompt leaks.
- Verified: Check low-cost deterministic lookup, architecture high floor, max reviewer and restricted data path.
- Verified: Correct blocking findings; rerun mapped validation and report measured/unknown costs without imaginary savings.
- Real independent reviewer approves final code and all high/critical findings are closed.
- No unauthorized provider/legacy test edits, leaked secrets, duplicate scheduler or lost global validation gate.

## Validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_120`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_120`

Expected files: `skill/plan-and-execute/scripts/routingctl.py`, `skill/plan-and-execute/scripts/planctl.py`, `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/runner_contract.py`, `skill/plan-and-execute/scripts/task_context_router.py`, `skill/plan-and-execute/references/TASK_CONTEXT_ROUTING.md`, `test/optimization/route_aware_context_self_test.py`, `docs/research/20261028-skill-optimization/implementation/120-receipt.json`, `docs/research/20261028-skill-optimization/implementation/120-outcome.md`.

**Pending:** only architectural specifications; no executed product tests or independent review.
