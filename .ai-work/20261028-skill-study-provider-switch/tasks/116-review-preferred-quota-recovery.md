---
task_id: "116"
status: "pending"
requirements: "R061,R062"
dependencies: "115"
allowed_related_task_reads: "none"
---

# 116 — Independently review provider preference recovery and quota wake

**Objective:** Real fresh max reviewer on final 115 hashes; no simulated approval.

**Architecture:** read only [assigned study](../../../docs/research/20261028-skill-optimization/prepared-research/115-quota-auto-recovery.md) and actual affected source. No work is yet implemented.

## Checkpoints

- [ ] S001 — Inspect final prior source and evidence: Inspect final prior source and evidence using only task-specific research, current code and current acceptance evidence.
- [ ] S002 — Dispatch genuine independent model review: Dispatch genuine independent model review using only task-specific research, current code and current acceptance evidence.
- [ ] S003 — Probe adverse contract and security cases: Probe adverse contract and security cases using only task-specific research, current code and current acceptance evidence.
- [ ] S004 — Correct findings and revalidate current code: Correct findings and revalidate current code using only task-specific research, current code and current acceptance evidence.
- [ ] S005 — Record real approved evidence or stay pending: Record real approved evidence or stay pending using only task-specific research, current code and current acceptance evidence.

## Implementation and review contract

- Read docs/research/20261028-skill-optimization/prepared-research/115-quota-auto-recovery.md only for this task; architecture and negative cases are mandatory.
- Real fresh max reviewer on final 115 hashes; no simulated approval.
- Challenge dispatch order, no-preempt, all-unavailable, one-shot lease and stale generation.
- Probe billing/auth mismatch, unknown reset, unsupported host, duplicate timers and cancel.
- Correct high/critical defects; independently approve current code with source-bound logs.
- Use per-phase economic routing and indexed source scope; preserve capability floors and independent reviews.
- Produce actual receipt/outcome only after code, mapped checks and real review; no fabricated success.

## Acceptance

- Verified: Real fresh max reviewer on final 115 hashes; no simulated approval.
- Verified: Challenge dispatch order, no-preempt, all-unavailable, one-shot lease and stale generation.
- Verified: Probe billing/auth mismatch, unknown reset, unsupported host, duplicate timers and cancel.
- Verified: Correct high/critical defects; independently approve current code with source-bound logs.
- Real independent reviewer approves final code and all high/critical findings are closed.
- No unauthorized provider/legacy test edits, leaked secrets, duplicate scheduler or lost global validation gate.

## Validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_116`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_116`

Expected files: `skill/plan-and-execute/scripts/availability.py`, `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/planctl.py`, `skill/plan-and-execute/scripts/keepalivectl.py`, `skill/plan-and-execute/scripts/jobctl.py`, `skill/plan-and-execute/scripts/quota_resume.py`, `skill/plan-and-execute/references/QUOTA_RECOVERY.md`, `test/optimization/quota_recovery_self_test.py`, `docs/research/20261028-skill-optimization/implementation/116-receipt.json`, `docs/research/20261028-skill-optimization/implementation/116-outcome.md`.

**Pending:** only architectural specifications; no executed product tests or independent review.
