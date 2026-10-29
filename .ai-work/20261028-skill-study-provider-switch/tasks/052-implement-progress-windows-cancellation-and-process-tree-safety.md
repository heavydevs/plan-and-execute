---
task_id: "052"
status: "pending"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "001,049"
allowed_related_task_reads: "none"
---

# 052 — Implement progress windows, cancellation and process-tree safety

Objective: Use separate liveness, semantic-progress and hard-limit clocks with bounded stream capture and owned process-tree cancellation on each supported operating system.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned research and pin applicable contracts — Read docs/research/20261028-skill-optimization/prepared-research/052-progress-processes.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** Implement revised contract 1 — Observe owned execution from launch; use five-minute policy only for extra instrumentation or diagnosis, not delayed evidence collection.
- [ ] **S003** Implement revised contract 2 — Separate heartbeat, CPU liveness, semantic progress and dependency health; retain independent hard budgets.
- [ ] **S004** Implement revised contract 3 — Drain streams concurrently with bounded memory and verify owned descendant termination before replacement.
- [ ] **S005** Validate all assigned positive and negative cases — Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** Record implementation evidence for independent review — Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

## Scope

In: Implement progress windows, cancellation and process-tree safety
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/progress_signal.py`, `skill/plan-and-execute/scripts/progress_watch.py`, `skill/plan-and-execute/scripts/process_tree.py`, `test/optimization/progress_processes_self_test.py`, `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/references/PROGRESS_TIMEOUTS.md`, `docs/research/20261028-skill-optimization/implementation/052-receipt.json`, `docs/research/20261028-skill-optimization/implementation/052-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/052-progress-processes.md.
- Use only task 052 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/052-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- TODO 052 owns progress/cancellation/output-buffer behavior, including the runner seam. TODO 054 builds supervised-job recovery on its accepted contract.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance

- Repeated heartbeat-only output does not keep a stalled command alive.
- Increasing completed-work counters renew idle time while a fixed hard ceiling still wins.
- Each command starts a new idle window; the validation set has no unintended aggregate timeout.
- A child scheduled to write later cannot escape timeout cleanup on supported Windows/POSIX runs.
- A CPU-busy infinite loop and a quiet but externally advancing operation produce distinct diagnostic evidence.
- Repeated heartbeat and constant progress counters cannot keep a stalled command alive indefinitely.
- A quiet but correctly progressing checkpointed job is not killed prematurely.
- A grandchild cannot write a delayed file after confirmed tree termination.
- Large stderr output cannot deadlock the reader or grow RAM without bound.
- Prepared research is not proof of implementation or independent-review completion.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_052`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_052`
