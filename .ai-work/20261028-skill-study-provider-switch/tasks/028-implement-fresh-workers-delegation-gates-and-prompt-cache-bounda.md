---
task_id: "028"
status: "pending"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "001,015"
allowed_related_task_reads: "none"
---

# 028 — Implement fresh workers, delegation gates and prompt-cache boundaries

Objective: Use a measured delegation gate with explicit input revision and isolation boundaries; prefer one qualified context for sequential work and bounded fresh workers for independently useful tasks.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned research and pin applicable contracts — Read docs/research/20261028-skill-optimization/prepared-research/028-delegation.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** Implement revised contract 1 — Compare delegation with a single qualified model at lower effort on held-out tasks, including review and repair cost.
- [ ] **S003** Implement revised contract 2 — Pin worker base revision and uncommitted-input policy; verify isolated worktree starts from the intended source.
- [ ] **S004** Implement revised contract 3 — Bound in-memory output while preserving independently parsed final reports and owned diagnostic logs.
- [ ] **S005** Validate all assigned positive and negative cases — Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** Record implementation evidence for independent review — Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

## Scope

In: Implement fresh workers, delegation gates and prompt-cache boundaries
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/runner_contract.py`, `test/optimization/delegation_self_test.py`, `skill/plan-and-execute/references/DELEGATION.md`, `docs/research/20261028-skill-optimization/implementation/028-receipt.json`, `docs/research/20261028-skill-optimization/implementation/028-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/028-delegation.md.
- Use only task 028 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/028-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance

- A noisy fake CLI emits many megabytes without proportional memory growth or pipe deadlock.
- A final structured report remains recoverable after long tool output; missing or truncated envelopes fail visibly.
- Two delegated writers cannot silently claim the same source scope.
- Above-floor work cannot be retained on an underqualified worker merely to avoid coordination cost.
- Prefix hashes match across tasks for raw and production entrypoints.
- A worker based on the default branch rather than the pinned working revision is rejected.
- Concurrent writers never share an overlapping scope without serialization.
- Multi-megabyte output does not grow the diagnostic buffer without bound.
- Native fork support cannot silently claim fresh-context isolation.
- Prepared research is not proof of implementation or independent-review completion.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_028`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_028`
