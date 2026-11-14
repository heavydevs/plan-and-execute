---
task_id: "110"
status: "pending"
requirements: "R057"
dependencies: "109"
allowed_related_task_reads: "none"
---

# 110 — Independently review and correct batched failure-repair validation

Objective: Independently review task 109's complete discovery, per-test artifacts, targeted reruns, final full gate and negative/failure safety.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read actual 109 implementation — Inspect source, tests, P057 report and real 109 receipt/outcome hashes, not previous conversation.
- [ ] **S002** Dispatch actual fresh reviewer — Use authorized maximum-qualified independent reviewer; retain provider/model/effort/session, dispatch and reviewed source hashes.
- [ ] **S003** Audit correctness and safety — Challenge false-green partial/full, missing shards, stale success, flaky/unknown, skipped tests, unsafe continuation, log/attachment privacy and shell selectors.
- [ ] **S004** Correct high/critical and retest — Fix within scope, rerun mapped functional regressions, require a fresh review on final hashes or keep pending.
- [ ] **S005** Record genuine review evidence — Write 110 receipt/outcome with real findings/corrections, unsupported frameworks and cost limits.

## Scope

In: Independently review task 109's complete discovery, per-test artifacts, targeted reruns, final full gate and negative/failure safety.
Out: No second orchestrator, fake green, unrelated edits or unapproved provider/model calls.
Files: `skill/plan-and-execute/scripts/test_failure_cycle.py`, `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/planctl.py`, `skill/plan-and-execute/scripts/runner_contract.py`, `skill/plan-and-execute/scripts/validatectl.py`, `skill/plan-and-execute/scripts/jobctl.py`, `skill/plan-and-execute/scripts/resource_watch.py`, `skill/plan-and-execute/scripts/service_map.py`, `skill/plan-and-execute/references/WORKFLOW.md`, `skill/plan-and-execute/references/TEST_RESOURCE_MONITORING.md`, `skill/plan-and-execute/references/PLAN_SPEC.md`, `skill/plan-and-execute/references/TOKEN_EFFICIENCY.md`, `docs/plans/20261028-skill-optimization/support/run_task_checks.py`, `test/optimization/batch_test_failure_cycle_self_test.py`, `docs/research/20261028-skill-optimization/implementation/110-receipt.json`, `docs/research/20261028-skill-optimization/implementation/110-outcome.md`

## Guidance

- Read `docs/research/20261028-skill-optimization/prepared-research/109-batched-test-failure-triage.md` and `docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261114_TEST_FAILURE_BATCH.md` before code; inspect source exactly, don't infer newer features are already implemented.
- Inspect run_isolated.run_validation_commands, run_validation_jobs, finish_task_validation, validatectl.run, runner_contract.install_runner_contract and active plan run_task_checks.
- Reuse resource_watch, jobctl, service_map and native reporter results; record versioned per-test failures and artifacts securely, continue only safe independent tests, prefer case IDs to console text.
- Implement targeted rerun only for verified supported framework selectors, with impacted neighbors; never treat incomplete/0-selected/current-code mismatch as success; final full regression must run again.
- Preserve process ownership, model routing/cost and progress, platform/CI behavior and bounded prompts; do not fabricate full-book, test or reviewer evidence.
- Write tests for this feature's functional correctness and failures; do not add application load/benchmark tests unless independently asked.

## Acceptance

- Actual independent fresh maximum-qualified reviewer and dispatch provenance pin exact final 109 code/test and receipt hashes.
- Review confirms all safely runnable suites collected after ordinary test failure, with valid per-test status/stack/log/E2E attribution and no false counts or hidden failed exit.
- Review verifies focused-only passes never bypass full required current-source regression, zero-selector and incomplete/old reporter outcomes are never green and new regressions restart bounded cycle.
- Unsafe continuation after compile/environment failure, flaky/order state, missing browser shards, concurrent owner, secret-bearing artifacts and prompt/selector injection are tested and blocked.
- No duplicate test supervisors, unauthorized provider/model charges, per-case AI polling or backward-compatibility regressions; genuine critical/high findings corrected and current-hash tests rerun.
- Reviewer evidence and mapped tests pass; otherwise 110 remains pending and cannot unlock 082.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_110`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_110`
