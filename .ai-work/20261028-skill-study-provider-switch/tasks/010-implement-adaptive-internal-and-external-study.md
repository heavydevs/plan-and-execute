---
task_id: "010"
status: "pending"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "001"
allowed_related_task_reads: "none"
---

# 010 — Implement adaptive internal and external study

Objective: Maintain a decision-oriented evidence ledger with explicit applicability and refresh triggers; stop research by unresolved decision risk, not source count.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned research and pin applicable contracts — Read docs/research/20261028-skill-optimization/prepared-research/010-adaptive-study.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** Implement revised contract 1 — Record discovery-only, abstract-only and inspected-section scopes separately; do not count inaccessible sources as verified support.
- [ ] **S003** Implement revised contract 2 — Attach every recommended change to a material question, repository applicability and a falsification condition.
- [ ] **S004** Implement revised contract 3 — Refresh evidence only on explicit invalidation signals; a task begins from its assigned report rather than restarting the literature survey.
- [ ] **S005** Validate all assigned positive and negative cases — Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** Record implementation evidence for independent review — Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

## Scope

In: Implement adaptive internal and external study
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/studyctl.py`, `skill/plan-and-execute/scripts/study_self_test.py`, `test/optimization/adaptive_study_self_test.py`, `skill/plan-and-execute/references/ADAPTIVE_STUDY.md`, `docs/research/20261028-skill-optimization/implementation/010-receipt.json`, `docs/research/20261028-skill-optimization/implementation/010-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/010-adaptive-study.md.
- Use only task 010 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/010-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance

- A source with no date/version is flagged for refresh when it affects CLI behavior.
- Two tasks sharing the same source retain different applicability notes without copying an entire article.
- A contradictory provider document yields a probe requirement, not an invented resolution.
- Known prepared reports are consumed without requiring another broad research phase.
- A source that was only located cannot satisfy a verified-interface claim.
- An API pricing record cannot silently substitute for subscription-quota evidence.
- A provider-version change invalidates only affected recommendations, not all 32 reports.
- Prepared research is not proof of implementation or independent-review completion.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_010`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_010`
