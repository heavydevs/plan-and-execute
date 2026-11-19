---
task_id: "118"
status: "pending"
requirements: "R063,R064"
dependencies: "117"
allowed_related_task_reads: "none"
---

# 118 — Independently review AI test oracle quality and efficiency

**Objective:** Real fresh max review with 117 final hashes/dispatch evidence.

**Architecture:** read only [assigned study](../../../docs/research/20261028-skill-optimization/prepared-research/117-ai-test-oracle-quality.md) and actual affected source. No work is yet implemented.

## Checkpoints

- [ ] S001 — Inspect final prior source and evidence: Inspect final prior source and evidence using only task-specific research, current code and current acceptance evidence.
- [ ] S002 — Dispatch genuine independent model review: Dispatch genuine independent model review using only task-specific research, current code and current acceptance evidence.
- [ ] S003 — Probe adverse contract and security cases: Probe adverse contract and security cases using only task-specific research, current code and current acceptance evidence.
- [ ] S004 — Correct findings and revalidate current code: Correct findings and revalidate current code using only task-specific research, current code and current acceptance evidence.
- [ ] S005 — Record real approved evidence or stay pending: Record real approved evidence or stay pending using only task-specific research, current code and current acceptance evidence.

## Implementation and review contract

- Read docs/research/20261028-skill-optimization/prepared-research/117-ai-test-oracle-quality.md only for this task; architecture and negative cases are mandatory.
- Real fresh max review with 117 final hashes/dispatch evidence.
- Reject assert-true, mock-only auth, mutante surviving and regressions masked by changed expectations.
- Review representative browser coverage, risk, test timing, property cases and legacy edit consent.
- Correct all high/critical findings and rerun scoped suites before independent acceptance.
- Use per-phase economic routing and indexed source scope; preserve capability floors and independent reviews.
- Produce actual receipt/outcome only after code, mapped checks and real review; no fabricated success.

## Acceptance

- Verified: Real fresh max review with 117 final hashes/dispatch evidence.
- Verified: Reject assert-true, mock-only auth, mutante surviving and regressions masked by changed expectations.
- Verified: Review representative browser coverage, risk, test timing, property cases and legacy edit consent.
- Verified: Correct all high/critical findings and rerun scoped suites before independent acceptance.
- Real independent reviewer approves final code and all high/critical findings are closed.
- No unauthorized provider/legacy test edits, leaked secrets, duplicate scheduler or lost global validation gate.

## Validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_118`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_118`

Expected files: `skill/plan-and-execute/scripts/planctl.py`, `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/runner_contract.py`, `skill/plan-and-execute/scripts/test_impact.py`, `skill/plan-and-execute/scripts/test_failure_cycle.py`, `skill/plan-and-execute/scripts/test_oracle.py`, `skill/plan-and-execute/references/TEST_AUTHORING.md`, `test/optimization/ai_test_quality_self_test.py`, `docs/research/20261028-skill-optimization/implementation/118-receipt.json`, `docs/research/20261028-skill-optimization/implementation/118-outcome.md`.

**Pending:** only architectural specifications; no executed product tests or independent review.
