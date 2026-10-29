---
task_id: "008"
status: "pending"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "001"
allowed_related_task_reads: "none"
---

# 008 — Implement oversized request fragmentation and prepared packages

Objective: Use content-addressed, lossless source fragments and obligation coverage; retain deterministic extraction and calibrate staging on working-set pressure.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned research and pin applicable contracts — Read docs/research/20261028-skill-optimization/prepared-research/008-primary-planning.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** Implement revised contract 1 — Hash raw source, extracted block stream and fragments; reject stale fragments at final consumption, not only during initial preparation.
- [ ] **S003** Implement revised contract 2 — Traverse nested tables in document order and bound ZIP/XML input; record unsupported source structures rather than silently omitting them.
- [ ] **S004** Implement revised contract 3 — Measure obligation recall and contradiction coverage against one-shot and staged baselines before changing token thresholds.
- [ ] **S005** Validate all assigned positive and negative cases — Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** Record implementation evidence for independent review — Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

## Scope

In: Implement oversized request fragmentation and prepared packages
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/preplanctl.py`, `skill/plan-and-execute/scripts/preplan_self_test.py`, `test/optimization/primary_planning_self_test.py`, `skill/plan-and-execute/references/PRIMARY_PLANNING.md`, `skill/plan-and-execute/references/PLANNING_INPUT_CONTRACT.md`, `docs/research/20261028-skill-optimization/implementation/008-receipt.json`, `docs/research/20261028-skill-optimization/implementation/008-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/008-primary-planning.md.
- Use only task 008 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/008-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance

- Mutating one byte of a fragment after coverage approval invalidates the package.
- A DOCX fixture with requirements in paragraphs and table cells preserves all obligations in source order.
- Duplicates, missing IDs, contradictory clauses and symlinks are rejected or explicitly recorded.
- An interrupted batch resumes from validated digests without processing completed raw fragments again.
- Permuting a requirement between beginning, middle and end does not change final requirement coverage.
- A same-size fragment rewrite with unchanged timestamp is rejected.
- Nested and merged table cells produce ordered, nonduplicated source anchors.
- A requirement appearing only in a table cannot disappear from the final coverage map.
- Large repeated blocks change routing estimates without deletion from authoritative evidence.
- Prepared research is not proof of implementation or independent-review completion.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_008`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_008`
