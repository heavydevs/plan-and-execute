---
task_id: "012"
status: "pending"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "001,003,005"
allowed_related_task_reads: "none"
---

# 012 — Implement requirements, task decomposition and schema-v4 state

Objective: Use staged plan generations, a single authoritative manifest and recoverable projection rebuilds; avoid claiming a multi-file transaction from atomic rename alone.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned research and pin applicable contracts — Read docs/research/20261028-skill-optimization/prepared-research/012-plan-contract.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** Implement revised contract 1 — Publish plan revisions as validated generations and define recovery when projections lag the authoritative manifest.
- [ ] **S003** Implement revised contract 2 — Bind acceptance to task contract and scoped inputs; preserve old receipts as history rather than rewriting them as current.
- [ ] **S004** Implement revised contract 3 — Test interruption before and after authority publication; recovery must not mark tasks complete or combine generations.
- [ ] **S005** Validate all assigned positive and negative cases — Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** Record implementation evidence for independent review — Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

## Scope

In: Implement requirements, task decomposition and schema-v4 state
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/planctl.py`, `skill/plan-and-execute/scripts/artifact_contract.py`, `test/optimization/plan_contract_self_test.py`, `skill/plan-and-execute/references/PLAN_SPEC.md`, `skill/plan-and-execute/references/PLANNING_PROTOCOL.md`, `docs/research/20261028-skill-optimization/implementation/012-receipt.json`, `docs/research/20261028-skill-optimization/implementation/012-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/012-plan-contract.md.
- Use only task 012 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/012-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance

- A failed revision leaves the previous manifest and task projections readable.
- Every requirement has a consumer; every implementation has explicit acceptance and validation.
- A transformed research task remains pending, with subtasks instructing implementation from its assigned report.
- Legacy schema1-3 files are not silently rewritten using schema4 projection rules.
- No active task creates a second plan or depends on a nonexistent research output.
- A crash after manifest replacement but before task rendering rebuilds consistent projections.
- A stale plan writer cannot replace a newer generation.
- Changing one task contract invalidates its dependent outputs, not unrelated completed tasks.
- Prepared research is not proof of implementation or independent-review completion.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_012`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_012`
