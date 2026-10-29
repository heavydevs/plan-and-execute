---
task_id: "058"
status: "pending"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "001,051"
allowed_related_task_reads: "none"
---

# 058 — Implement incremental log scanning, digest and artifact retention

Objective: Use identity-aware incremental log readers, provenance-preserving bounded digests and owner-scoped retention; never delete evidence merely because an agent has already read it.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned research and pin applicable contracts — Read docs/research/20261028-skill-optimization/prepared-research/058-log-lifecycle.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** Implement revised contract 1 — Bind log cursors to file identity/generation and handle rotation, truncation, split UTF-8 and partial lines explicitly.
- [ ] **S003** Implement revised contract 2 — Expose incomplete coverage, dropped groups and unreadable inputs; no-error is not healthy when coverage is incomplete.
- [ ] **S004** Implement revised contract 3 — Retain only owner-approved cleanup rules; never delete a user log because it was already read by an agent.
- [ ] **S005** Validate all assigned positive and negative cases — Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** Record implementation evidence for independent review — Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

## Scope

In: Implement incremental log scanning, digest and artifact retention
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/log_watch.py`, `skill/plan-and-execute/scripts/resource_watch.py`, `test/optimization/log_lifecycle_self_test.py`, `skill/plan-and-execute/references/TEST_RESOURCE_MONITORING.md`, `docs/research/20261028-skill-optimization/implementation/058-receipt.json`, `docs/research/20261028-skill-optimization/implementation/058-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/058-log-lifecycle.md.
- Use only task 058 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/058-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance

- An error split across two writes is detected once the line completes.
- An omitted interval yields a coverage-gap status, never a claim of no errors.
- Rotation/replacement does not inherit an unrelated offset silently.
- A planted credential at a truncation boundary is absent from model-facing excerpts.
- Cleanup preserves active/unresolved evidence and rejects unregistered paths and symlinks.
- Rename rotation and copy-truncate do not silently skip or duplicate complete records.
- A secret split across read chunks is removed before digest truncation.
- A truncated log with no observed error reports incomplete coverage.
- Cleanup refuses arbitrary external logs and preserves failure evidence.
- Prepared research is not proof of implementation or independent-review completion.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_058`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_058`
