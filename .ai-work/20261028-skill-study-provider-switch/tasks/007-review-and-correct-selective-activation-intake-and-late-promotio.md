---
task_id: "007"
status: "completed"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "006"
allowed_related_task_reads: "none"
---

# 007 — Review and correct selective activation, intake and late promotion

Objective: Review the actual implementation against the assigned prepared decision, correct blocking findings and re-run the targeted acceptance tests.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [x] **S001** Read assigned decision and pin baseline — Read docs/research/20261028-skill-optimization/prepared-research/006-activation-intake.md. Confirm source applicability; do not repeat broad research.
- [x] **S002** Dispatch the independent reviewer — Run `python docs/plans/20261028-skill-optimization/support/review_dispatch.py --repo-root . --task 007` in the foreground (rerun on exit 75); use only its DISPATCH line and compact findings.
- [x] **S003** Implement change 2 — Correct every blocking finding or leave the gate incomplete with a recorded reason.
- [x] **S004** Implement change 3 — Re-run declared checks after corrections and pin the final reviewed source state.
- [x] **S005** Run declared regression checks — Run the declared targeted tests through the resource watcher. Implement every assigned acceptance case and preserve failures and limitations.
- [x] **S006** Record acceptance evidence — Write the implementation receipt and outcome report with changed-file hashes, acceptance coverage and actual test logs. Leave unresolved work pending.

## Scope

In: Review and correct selective activation, intake and late promotion
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/requestctl.py`, `skill/plan-and-execute/scripts/promotectl.py`, `skill/plan-and-execute/scripts/routing_self_test.py`, `test/optimization/activation_intake_self_test.py`, `skill/plan-and-execute/SKILL.md`, `skill/plan-and-execute/agents/openai.yaml`, `skill/plan-and-execute/references/ROUTING.md`, `skill/plan-and-execute/references/PROMOTION.md`, `skill/plan-and-execute/references/routing-evals.json`, `docs/research/20261028-skill-optimization/implementation/007-receipt.json`, `docs/research/20261028-skill-optimization/implementation/007-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/006-activation-intake.md.
- Use only task 007 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/007-receipt.json.
- Review only via review_dispatch.py (synchronous; max route; writes dispatch evidence); fix blocking findings, rerun declared checks, re-dispatch if a reviewed file changed, copy its RECEIPT_REVIEWER fields into the receipt.
- Review the revision-2 alternatives, scope boundary and negative tests against the actual changed code; report unsupported cost/quality claims.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Never launch background or asynchronous agents or processes: this headless session ends when you stop calling tools, so anything unfinished is lost.

## Acceptance

- Actual fresh reviewer provider/model/effort and reviewed input hashes are recorded.
- No unresolved critical/high finding remains; the assigned acceptance cases have actual test evidence.
- A reused or fabricated review receipt is rejected.
- A frontier (Fable 5.2 / Astra 6.2) reviewer is accepted only with recorded repeated max-review failure; a reused review session or dispatch is rejected.
- Every 2026-11-20 acceptance addition of task 006 has actual test evidence on the final reviewed hashes.
- The prepared report is input evidence, not proof that this implementation or its independent review has passed.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_007`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_007`
