---
task_id: "109"
status: "pending"
requirements: "R057"
dependencies: "055,059,063,098,100,108"
allowed_related_task_reads: "none"
---

# 109 — Implement complete test-failure inventory, focused repair and final full-suite gate

Objective: Collect all safely runnable test failures with per-test stack/log/E2E evidence, rerun failures and impacted tests during repair, then require a full final current-source regression pass.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read source and research — Inspect P057 study, run_validation_commands/run_validation_jobs, validatectl, runner_contract, resource_watch, service map and run_task_checks's current fail-fast semantics.
- [ ] **S002** Implement safe full discovery — Separate fatal build/infra/dependency faults from ordinary test failure; continue independent safe test commands, preserve original nonzero exits, map and progress/timeout contracts.
- [ ] **S003** Build per-test failure manifest — Parse verified official JSON/JUnit reporters with stable case identity, root-cause grouping, per-test stack/log evidence and optional failure-only browser screenshots/traces under guarded paths.
- [ ] **S004** Implement bounded focused repair cycle — Persist current-source failure backlog; select exact failing tests and affected neighbors, avoid repeated passing unrelated tests, classify flaky/setup/environment and reject zero-selected false green.
- [ ] **S005** Require complete final green run — Once focused failures are fixed rerun every originally required mapped suite/job on final source; new failures restart bounded cycle, incomplete/stale reports cannot complete.
- [ ] **S006** Wire existing runtimes and docs — Integrate ORCHESTRATED and DIRECT/validate-or-fix, runner_contract and plan helper; document framework adapters and quotas without duplicate supervisor.
- [ ] **S007** Run adversarial functional checks — Create test/optimization/batch_test_failure_cycle_self_test.py; verify 100/7, multi-suite, compilation fail, E2E evidence, unknown selector, stale hash, crash, flaky and new regression.
- [ ] **S008** Record real receipt — Write 109 receipt/outcome with actual code/test hashes and check logs; leave pending without genuine success evidence.

## Scope

In: Collect all safely runnable test failures with per-test stack/log/E2E evidence, rerun failures and impacted tests during repair, then require a full final current-source regression pass.
Out: No second orchestrator, fake green, unrelated edits or unapproved provider/model calls.
Files: `skill/plan-and-execute/scripts/test_failure_cycle.py`, `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/planctl.py`, `skill/plan-and-execute/scripts/runner_contract.py`, `skill/plan-and-execute/scripts/validatectl.py`, `skill/plan-and-execute/scripts/jobctl.py`, `skill/plan-and-execute/scripts/resource_watch.py`, `skill/plan-and-execute/scripts/service_map.py`, `skill/plan-and-execute/references/WORKFLOW.md`, `skill/plan-and-execute/references/TEST_RESOURCE_MONITORING.md`, `skill/plan-and-execute/references/PLAN_SPEC.md`, `skill/plan-and-execute/references/TOKEN_EFFICIENCY.md`, `docs/plans/20261028-skill-optimization/support/run_task_checks.py`, `test/optimization/batch_test_failure_cycle_self_test.py`, `docs/research/20261028-skill-optimization/implementation/109-receipt.json`, `docs/research/20261028-skill-optimization/implementation/109-outcome.md`

## Guidance

- Read `docs/research/20261028-skill-optimization/prepared-research/109-batched-test-failure-triage.md` and `docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261114_TEST_FAILURE_BATCH.md` before code; inspect source exactly, don't infer newer features are already implemented.
- Inspect run_isolated.run_validation_commands, run_validation_jobs, finish_task_validation, validatectl.run, runner_contract.install_runner_contract and active plan run_task_checks.
- Reuse resource_watch, jobctl, service_map and native reporter results; record versioned per-test failures and artifacts securely, continue only safe independent tests, prefer case IDs to console text.
- Implement targeted rerun only for verified supported framework selectors, with impacted neighbors; never treat incomplete/0-selected/current-code mismatch as success; final full regression must run again.
- Preserve process ownership, model routing/cost and progress, platform/CI behavior and bounded prompts; do not fabricate full-book, test or reviewer evidence.
- Write tests for this feature's functional correctness and failures; do not add application load/benchmark tests unless independently asked.

## Acceptance

- First ordinary failed test does not prevent independent safe mapped suites collecting all failures; compilation, unhealthy resources, dependent/unsafe jobs stop or mark not_run, never green.
- Versioned source/map/command-scoped inventory uses valid native JSON/JUnit formats, stable test and parameter/browser/shard identities, accurate counts and complete-collection status; unknown/runner failure differs from passing.
- Every attributable failing case includes real stack/message, bounded logs and safe evidence paths; supported E2E screenshots/traces are associated when available and redacted/size-bounded before any agent input.
- Targeted repair reexecutes only known failed cases/root-cause clusters plus demonstrably impacted neighbors; source changes make prior passes diagnostic-only, selectors must be exact and nonempty or fall back safely.
- No task is accepted from focused-only passing results; all required original mapped commands and supervised jobs must pass together on the same current final source/config/resource fingerprint; new failures cause bounded further cycles.
- Flaky/retry, fixture/shared state, test order, parametrized/project, skipped/not-run, missing reporters/shards, crash and environment errors are recorded without silencing or false completion.
- Owned process/job lifecycle, concurrent plans, crash/resume, budget/cancellation, real progress and existing qualified routing work without a second orchestrator or model-per-test polling.
- 100-case/7-failure fixture proves no unrelated passing tests in focused loop, final all-case rerun and real nonzero failure propagation; test reports/secret/selector injection negatives are covered.
- Targeted framework adapters and fallback work for supported pytest, Playwright, Jest/Vitest and Gradle/JUnit/Maven; unsupported runners remain safe and honest.
- Actual implementation and functional validation receipts/hashes prove behavior, with unmeasured real-world cost saving identified as unknown.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_109`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_109`
