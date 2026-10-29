---
task_id: "054"
status: "pending"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "001,049,053"
allowed_related_task_reads: "none"
---

# 054 — Implement durable supervised jobs and validation handoff

Objective: Make supervised validation jobs idempotent, generation-bound state machines that resume validation without redispatching the implementation model and reconcile uncertain job outcomes before restart.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned research and pin applicable contracts — Read docs/research/20261028-skill-optimization/prepared-research/054-supervised-jobs.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** Implement revised contract 1 — Bind job evidence to task, attempt, command and source/map generation; stale success cannot satisfy acceptance.
- [ ] **S003** Implement revised contract 2 — Test the launch-before-record crash window and reconcile ownership before redispatch.
- [ ] **S004** Implement revised contract 3 — Resume pending validation from its implementation checkpoint without invoking the model again.
- [ ] **S005** Validate all assigned positive and negative cases — Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** Record implementation evidence for independent review — Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

## Scope

In: Implement durable supervised jobs and validation handoff
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/jobctl.py`, `skill/plan-and-execute/scripts/run_isolated.py`, `test/optimization/supervised_jobs_self_test.py`, `skill/plan-and-execute/references/PROGRESS_TIMEOUTS.md`, `docs/research/20261028-skill-optimization/implementation/054-receipt.json`, `docs/research/20261028-skill-optimization/implementation/054-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/054-supervised-jobs.md.
- Use only task 054 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/054-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance

- Two start requests for the same pinned live job create only one process.
- A completed validation checkpoint resumes without redispatching the model.
- A succeeded job with changed source/map/command is rejected as stale.
- Wait timeout leaves the live job intact and returns its state, not a false failure.
- Crash/cancel tests preserve receipts or explicitly report uncertainty rather than inventing completion.
- Crash after process launch does not produce a second writer during recovery.
- A successful receipt with an outdated map/input digest is rejected.
- Validation-only resume performs zero model dispatches.
- Cleanup cannot delete state while an owned job termination remains uncertain.
- Prepared research is not proof of implementation or independent-review completion.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_054`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_054`
