---
task_id: "115"
status: "pending"
requirements: "R061,R062"
dependencies: "023,055,075,100,104"
allowed_related_task_reads: "none"
---

# 115 — Implement preferred-provider priority restoration and durable quota resume

**Objective:** Re-rank allowed providers by user preference before each new safe dispatch only.

**Architecture:** read only [assigned study](../../../docs/research/20261028-skill-optimization/prepared-research/115-quota-auto-recovery.md) and actual affected source. No work is yet implemented.

## Checkpoints

- [ ] S001 — Inspect assigned architecture and relevant source symbols: Inspect assigned architecture and relevant source symbols using only task-specific research, current code and current acceptance evidence.
- [ ] S002 — Implement bounded contract without duplicate framework: Implement bounded contract without duplicate framework using only task-specific research, current code and current acceptance evidence.
- [ ] S003 — Integrate monitoring, permissions and route: Integrate monitoring, permissions and route using only task-specific research, current code and current acceptance evidence.
- [ ] S004 — Execute adversarial focused validation: Execute adversarial focused validation using only task-specific research, current code and current acceptance evidence.
- [ ] S005 — Record real product evidence or stay pending: Record real product evidence or stay pending using only task-specific research, current code and current acceptance evidence.

## Implementation and review contract

- Read docs/research/20261028-skill-optimization/prepared-research/115-quota-auto-recovery.md only for this task; architecture and negative cases are mandatory.
- Re-rank allowed providers by user preference before each new safe dispatch only.
- Persist quota pool, retry-after and unknown reset; distinguish auth/billing/environment errors from quota.
- When every allowed provider is quota limited persist PAUSED_QUOTA and one fenced durable one-shot scheduled recheck; use existing scheduler, even for fewer than six tasks.
- Zero paid polling; bounded jitter/backoff; no preemption, duplicate work, secret/permission bypass or sleeping host guarantee.
- Cover A->B->A preference, no provider, multiple pools, scheduler missing, clock skew, cancel and crash/resume.
- Use per-phase economic routing and indexed source scope; preserve capability floors and independent reviews.
- Produce actual receipt/outcome only after code, mapped checks and real review; no fabricated success.

## Acceptance

- Verified: Re-rank allowed providers by user preference before each new safe dispatch only.
- Verified: Persist quota pool, retry-after and unknown reset; distinguish auth/billing/environment errors from quota.
- Verified: When every allowed provider is quota limited persist PAUSED_QUOTA and one fenced durable one-shot scheduled recheck; use existing scheduler, even for fewer than six tasks.
- Verified: Zero paid polling; bounded jitter/backoff; no preemption, duplicate work, secret/permission bypass or sleeping host guarantee.
- Actual source-bound tests, negative fixtures and compact cost evidence establish behavior without inventing savings.
- No unauthorized provider/legacy test edits, leaked secrets, duplicate scheduler or lost global validation gate.

## Validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_115`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_115`

Expected files: `skill/plan-and-execute/scripts/availability.py`, `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/planctl.py`, `skill/plan-and-execute/scripts/keepalivectl.py`, `skill/plan-and-execute/scripts/jobctl.py`, `skill/plan-and-execute/scripts/quota_resume.py`, `skill/plan-and-execute/references/QUOTA_RECOVERY.md`, `test/optimization/quota_recovery_self_test.py`, `docs/research/20261028-skill-optimization/implementation/115-receipt.json`, `docs/research/20261028-skill-optimization/implementation/115-outcome.md`.

**Pending:** only architectural specifications; no executed product tests or independent review.
