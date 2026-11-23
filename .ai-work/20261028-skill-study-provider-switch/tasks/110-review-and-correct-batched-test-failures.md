---
task_id: "110"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "max"
reasoning_effort: "xhigh"
complexity: "high"
requirements: "R057, R059"
dependencies: "109"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 110 — Independently review and correct batched failure-repair validation

## Objective

Independently review task 109's complete discovery, per-test artifacts, targeted reruns, final full gate and negative/failure safety.

## Requirements covered

- R057
- R059

## Complexity and atomicity

- Complexity: **high**
- Why this is one executable TODO: One coherent validation cycle feature or independent correction boundary with shared source/manifest/report contract.

## Context-isolation boundary

- Why one fresh worker context helps this whole TODO: Failure collection, rerun selectors and final acceptance depend on a single coherent state machine.
- Context that is genuinely shared by all subtasks:
- Current P057 report, affected validation sources and accepted prior receipts only.
- Concerns deliberately isolated into other TODOs:
- Do not preload unrelated task studies, old logs, user conversations or provider guides.

## Isolation contract

This task definition and the exact execution-context files listed below are the only planning artifacts assigned to this worker. Read the task definition first, then read every assigned context file. Do not discover or open any other context file, `PLAN.md`, `TODO.md`, `manifest.json`, `orchestrator.config.json`, result files, logs, or unrelated task definitions. You may read repository source, tests, build files, and runtime output relevant to this task.

Another task definition may be opened only when one of the explicitly allowed task ids above is necessary to resolve a blocked dependency, ambiguity, or validation conflict. Record the task id and reason in the completion report.

## Assigned execution context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Assigned validated learnings

- None

These files are concise, immutable artifacts produced only after another TODO passed deterministic validation. Read exactly the assigned files, never a previous worker transcript or an unassigned learning file.

## Resumable subtask checklist

- [ ] **S001** — Read actual 109 implementation
  - Inspect source, tests, P057 report and real 109 receipt/outcome hashes, not previous conversation.
- [ ] **S002** — Dispatch actual fresh reviewer
  - Run `python docs/plans/20261028-skill-optimization/support/review_dispatch.py --repo-root . --task 110` in the foreground (rerun on exit 75); use only its DISPATCH line and compact findings.
- [ ] **S003** — Audit correctness and safety
  - Challenge false-green partial/full, missing shards, stale success, flaky/unknown, skipped tests, unsafe continuation, log/attachment privacy and shell selectors.
- [ ] **S004** — Correct high/critical and retest
  - Fix within scope, rerun mapped functional regressions, require a fresh review on final hashes or keep pending.
- [ ] **S005** — Record genuine review evidence
  - Write 110 receipt/outcome with real findings/corrections, unsupported frameworks and cost limits.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Independently review task 109's complete discovery, per-test artifacts, targeted reruns, final full gate and negative/failure safety.

## Out of scope

- No parallel testing orchestrator, unsafe continuation, skipped failed tests, benchmark default or unapproved provider/global configuration changes.

## Expected files

- skill/plan-and-execute/scripts/test_failure_cycle.py
- skill/plan-and-execute/scripts/run_isolated.py
- skill/plan-and-execute/scripts/planctl.py
- skill/plan-and-execute/scripts/runner_contract.py
- skill/plan-and-execute/scripts/validatectl.py
- skill/plan-and-execute/scripts/jobctl.py
- skill/plan-and-execute/scripts/resource_watch.py
- skill/plan-and-execute/scripts/service_map.py
- skill/plan-and-execute/references/WORKFLOW.md
- skill/plan-and-execute/references/TEST_RESOURCE_MONITORING.md
- skill/plan-and-execute/references/PLAN_SPEC.md
- skill/plan-and-execute/references/TOKEN_EFFICIENCY.md
- docs/plans/20261028-skill-optimization/support/run_task_checks.py
- test/optimization/batch_test_failure_cycle_self_test.py
- docs/research/20261028-skill-optimization/implementation/110-receipt.json
- docs/research/20261028-skill-optimization/implementation/110-outcome.md

## Dependencies

- 109

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/research/20261028-skill-optimization/prepared-research/109-batched-test-failure-triage.md and docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261114_TEST_FAILURE_BATCH.md before code.
- Inspect source exactly; do not infer that newer features are already implemented.
- Inspect run_isolated.run_validation_commands, run_validation_jobs, finish_task_validation, validatectl.run, runner_contract.install_runner_contract and active plan run_task_checks.
- Reuse resource_watch, jobctl, service_map and native reporter results; record versioned per-test failures and artifacts securely, continue only safe independent tests, prefer case IDs to console text.
- Implement targeted rerun only for verified supported framework selectors, with impacted neighbors; never treat incomplete/0-selected/current-code mismatch as success; final full regression must run again.
- Preserve process ownership, model routing/cost and progress, platform/CI behavior and bounded prompts; do not fabricate full-book, test or reviewer evidence.
- Write tests for this feature's functional correctness and failures; do not add application load/benchmark tests unless independently asked.
- Review the distinction between complete task-mapped reruns and final global full-suite regression; unknown/zero impact selection and focused-only green never satisfy acceptance.
- Edits to support/run_task_checks.py stay fail-closed (nonzero if any declared check fails or did not run); record its hash in changed_artifacts and in 110's reviewed_inputs (code_fingerprint does not cover docs/).
- Review only via review_dispatch.py (synchronous; max route; writes dispatch evidence); fix blocking findings, rerun declared checks, re-dispatch if a reviewed file changed, copy its RECEIPT_REVIEWER fields into the receipt.
- Never launch background or asynchronous agents or processes: this headless session ends when you stop calling tools, so anything unfinished is lost.

## Acceptance criteria

- Actual independent fresh maximum-qualified reviewer and dispatch provenance pin exact final 109 code/test and receipt hashes.
- Review confirms all safely runnable suites collected after ordinary test failure, with valid per-test status/stack/log/E2E attribution and no false counts or hidden failed exit.
- Review verifies focused-only passes never bypass full required current-source regression, zero-selector and incomplete/old reporter outcomes are never green and new regressions restart bounded cycle.
- Unsafe continuation after compile/environment failure, flaky/order state, missing browser shards, concurrent owner, secret-bearing artifacts and prompt/selector injection are tested and blocked.
- No duplicate test supervisors, unauthorized provider/model charges, per-case AI polling or backward-compatibility regressions; genuine critical/high findings corrected and current-hash tests rerun.
- Reviewer evidence and mapped tests pass; otherwise 110 remains pending and cannot unlock 082.
- A frontier (Fable 5.2 / Astra 6.2) reviewer is accepted only with recorded repeated max-review failure; a reused review session or dispatch is rejected.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_110`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_110`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
