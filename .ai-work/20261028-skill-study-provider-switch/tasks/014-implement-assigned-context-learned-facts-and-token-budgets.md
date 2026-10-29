---
task_id: "014"
status: "pending"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "001,013"
allowed_related_task_reads: "none"
---

# 014 — Implement assigned context, learned facts and token budgets

Objective: Use provenance-bearing task context and directional learnings with explicit trust and cache boundaries, not an accumulating transcript or universal memory.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned research and pin applicable contracts — Read docs/research/20261028-skill-optimization/prepared-research/014-context-learning.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** Implement revised contract 1 — Assign each learning a trust class, producer, consumer set and source/contract digest.
- [ ] **S003** Implement revised contract 2 — Keep failed-attempt hypotheses separate from normative shared facts; invalidate them when their evidence changes.
- [ ] **S004** Implement revised contract 3 — Measure stale-learning errors and task success as well as context bytes; cache reuse is an observed metric, not a structural assertion.
- [ ] **S005** Validate all assigned positive and negative cases — Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** Record implementation evidence for independent review — Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

## Scope

In: Implement assigned context, learned facts and token budgets
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/planctl.py`, `skill/plan-and-execute/scripts/artifact_contract.py`, `skill/plan-and-execute/scripts/runner_contract.py`, `test/optimization/context_learning_self_test.py`, `skill/plan-and-execute/references/EXECUTION_CONTEXT.md`, `skill/plan-and-execute/references/TOKEN_EFFICIENCY.md`, `docs/research/20261028-skill-optimization/implementation/014-receipt.json`, `docs/research/20261028-skill-optimization/implementation/014-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/014-context-learning.md.
- Use only task 014 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/014-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance

- An unrelated task cannot receive a learning merely because it ran later.
- Changing a cited file invalidates or flags the learning before reuse.
- A malicious or unsupported note cannot alter acceptance, permissions or provider policy.
- The universal context contains only constraints needed by all tasks and remains within its existing budget.
- Byte-stable prefixes and bounded task suffixes survive different task IDs and prior failure lengths.
- A disproven hypothesis never appears as a validated shared fact.
- A source-contract change invalidates its learning without deleting unrelated knowledge.
- The static prefix remains stable while task-specific reports are loaded only for their assigned consumers.
- Prepared research is not proof of implementation or independent-review completion.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_014`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_014`
