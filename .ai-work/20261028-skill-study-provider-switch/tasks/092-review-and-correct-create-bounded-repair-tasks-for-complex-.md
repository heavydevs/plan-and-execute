---
task_id: "092"
status: "pending"
requirements: "R048"
dependencies: "091"
allowed_related_task_reads: "none"
---

# 092 — Review and correct create bounded repair tasks for complex active-plan blockers

Objective: Independently review and correct create bounded repair tasks for complex active-plan blockers using actual implementation and validation evidence.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read implementation — Review the actual code, test results and receipt from task 091, not a previous conversation.
- [ ] **S002** Independent review — Run `python docs/plans/20261028-skill-optimization/support/review_dispatch.py --repo-root . --task 092` in the foreground (rerun on exit 75); use only its DISPATCH line and compact findings.
- [ ] **S003** Correct high-risk defects — Correct critical/high findings or leave the task pending with evidence.
- [ ] **S004** Rerun regressions — Run test/optimization/blocked_task_split_self_test.py and all feature acceptance and negative cases through mapped validation.
- [ ] **S005** Record review — Record actual review/validation results in docs/research/20261028-skill-optimization/implementation/092-receipt.json and docs/research/20261028-skill-optimization/implementation/092-outcome.md.

## Scope

In: Review and correct create bounded repair tasks for complex active-plan blockers
Out: No second plan or unrelated changes.; No installation, provider login, publishing or user-global configuration changes without permission.
Files: `skill/plan-and-execute/scripts/planctl.py`, `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/lifecyclectl.py`, `skill/plan-and-execute/scripts/runner_contract.py`, `skill/plan-and-execute/references/WORKFLOW.md`, `skill/plan-and-execute/references/PLAN_SPEC.md`, `skill/plan-and-execute/references/TEST_RESOURCE_MONITORING.md`, `test/optimization/blocked_task_split_self_test.py`, `docs/research/20261028-skill-optimization/implementation/092-receipt.json`, `docs/research/20261028-skill-optimization/implementation/092-outcome.md`

## Guidance

- Read docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261031.md.
- Follow task 092 in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Preserve exact user intent, bounded context, security floors and real deterministic tests.
- Review only via review_dispatch.py (synchronous; max route; writes dispatch evidence); fix blocking findings, rerun declared checks, re-dispatch if a reviewed file changed, copy its RECEIPT_REVIEWER fields into the receipt.
- Preserve evidence in docs/research/20261028-skill-optimization/implementation/092-receipt.json and docs/research/20261028-skill-optimization/implementation/092-outcome.md; do not mark a pending task done without validation.
- Never launch background or asynchronous agents or processes: this headless session ends when you stop calling tools, so anything unfinished is lost.

## Acceptance

- Record a real fresh independent reviewer route and exact reviewed input hashes.
- Verify: A complex reproducible blocker creates scoped repair/design TODOs and suspends the original task.
- Verify: A temporary outage, quota limit or simple patch does not add tasks or escalate architecture reasoning.
- Verify: Idempotency prevents recursive task explosion; leases, cycles and interrupted writes are handled.
- Verify: Original validated subtasks survive, and newly created tests must pass before unblocking.
- No unresolved critical/high finding or missing required reviewer may be marked complete.
- A frontier (Fable 5.2 / Astra 6.2) reviewer is accepted only with recorded repeated max-review failure; a reused review session or dispatch is rejected.
- Every 2026-11-20 acceptance addition of task 091 has actual test evidence on the final reviewed hashes.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_092`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_092`
