---
task_id: "016"
status: "pending"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "001,015"
allowed_related_task_reads: "none"
---

# 016 — Implement versioned shared contracts and selective invalidation

Objective: Keep a small versioned pattern registry with conditional writes and precise consumer invalidation; distinguish semantic changes from formatting edits.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned research and pin applicable contracts — Read docs/research/20261028-skill-optimization/prepared-research/016-shared-patterns.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** Implement revised contract 1 — Require an expected canonical digest and serialize writes using the lifecycle ownership contract.
- [ ] **S003** Implement revised contract 2 — Separate formatting-only changes from semantic revisions; only changed normative contracts reopen stale accepted signatories.
- [ ] **S004** Implement revised contract 3 — Deliver the current pattern and bounded delta, not its full revision history, to each assigned consumer.
- [ ] **S005** Validate all assigned positive and negative cases — Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** Record implementation evidence for independent review — Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

## Scope

In: Implement versioned shared contracts and selective invalidation
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/patternctl.py`, `skill/plan-and-execute/scripts/pattern_runner_contract.py`, `test/optimization/shared_patterns_self_test.py`, `skill/plan-and-execute/references/SHARED_PATTERNS.md`, `docs/research/20261028-skill-optimization/implementation/016-receipt.json`, `docs/research/20261028-skill-optimization/implementation/016-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/016-shared-patterns.md.
- Use only task 016 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/016-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance

- Two writers using the same starting revision cannot both silently succeed.
- An unaffected completed task remains completed after an unrelated pattern change.
- A stale completed signatory is reopened exactly once with a reason.
- Malformed or escaping pattern paths cannot be read or deleted.
- A worker receives only assigned current contracts, not the entire registry/history.
- Two writers with the same starting digest cannot both overwrite the registry.
- A formatting-only change does not reopen completed consumers.
- A semantic revision reopens exactly its stale signatories and preserves their prior evidence as history.
- Prepared research is not proof of implementation or independent-review completion.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_016`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_016`
