---
task_id: "116"
status: "pending"
requirements: "R061,R062"
dependencies: "115"
allowed_related_task_reads: "none"
---

# 116 — Independently review provider preference recovery and quota wake

Objective: Real fresh max reviewer on final 115 hashes; no simulated approval.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Inspect final prior source and evidence — Inspect final prior source and evidence using only task-specific research, current code and current acceptance evidence.
- [ ] **S002** Dispatch genuine independent model review — Run `python docs/plans/20261028-skill-optimization/support/review_dispatch.py --repo-root . --task 116` in the foreground (rerun on exit 75); use only its DISPATCH line and compact findings.
- [ ] **S003** Probe adverse contract and security cases — Probe adverse contract and security cases using only task-specific research, current code and current acceptance evidence.
- [ ] **S004** Correct findings and revalidate current code — Correct findings and revalidate current code using only task-specific research, current code and current acceptance evidence.
- [ ] **S005** Record real approved evidence or stay pending — Record real approved evidence or stay pending using only task-specific research, current code and current acceptance evidence.

## Scope

In: Independently review provider preference recovery and quota wake
Out: No second orchestrator, unrelated legacy test edits, runtime implementation in this planning amendment or paid model polling.
Files: `skill/plan-and-execute/scripts/availability.py`, `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/planctl.py`, `skill/plan-and-execute/scripts/keepalivectl.py`, `skill/plan-and-execute/scripts/jobctl.py`, `skill/plan-and-execute/scripts/quota_resume.py`, `skill/plan-and-execute/references/QUOTA_RECOVERY.md`, `test/optimization/quota_recovery_self_test.py`, `docs/research/20261028-skill-optimization/implementation/116-receipt.json`, `docs/research/20261028-skill-optimization/implementation/116-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/115-quota-auto-recovery.md only for this task; architecture and negative cases are mandatory.
- Real fresh max reviewer on final 115 hashes; no simulated approval.
- Challenge dispatch order, no-preempt, all-unavailable, one-shot lease and stale generation.
- Probe billing/auth mismatch, unknown reset, unsupported host, duplicate timers and cancel.
- Correct high/critical defects; independently approve current code with source-bound logs.
- Use per-phase economic routing and indexed source scope; preserve capability floors and independent reviews.
- Produce actual receipt/outcome only after code, mapped checks and real review; no fabricated success.
- Probe credits_exhausted classification, Codex-exhausted rerouting (implementation -> Antigravity, review -> Claude Opus 5.5) and return to Codex on the next eligible dispatch only.
- Review only via review_dispatch.py (synchronous; max route; writes dispatch evidence); fix blocking findings, rerun declared checks, re-dispatch if a reviewed file changed, copy its RECEIPT_REVIEWER fields into the receipt.
- Never launch background or asynchronous agents or processes: this headless session ends when you stop calling tools, so anything unfinished is lost.

## Acceptance

- Verified: Real fresh max reviewer on final 115 hashes; no simulated approval.
- Verified: Challenge dispatch order, no-preempt, all-unavailable, one-shot lease and stale generation.
- Verified: Probe billing/auth mismatch, unknown reset, unsupported host, duplicate timers and cancel.
- Verified: Correct high/critical defects; independently approve current code with source-bound logs.
- Real independent reviewer approves final code and all high/critical findings are closed.
- No unauthorized provider/legacy test edits, leaked secrets, duplicate scheduler or lost global validation gate.
- Verified: credits_exhausted classification and the Codex exhausted/returned rerouting fixtures pass on the final 115 code.
- A frontier (Fable 5.2 / Astra 6.2) reviewer is accepted only with recorded repeated max-review failure; a reused review session or dispatch is rejected.
- Every 2026-11-20 acceptance addition of task 115 has actual test evidence on the final reviewed hashes.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_116`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_116`
