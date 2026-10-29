---
task_id: "026"
status: "pending"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "001,021"
allowed_related_task_reads: "none"
---

# 026 — Implement model catalog evidence, caches, snapshots and refresh

Objective: Keep provider-scoped catalog evidence with independently aged facets and immutable attempt bindings; treat aliases and pricing changes as observable model-resolution events.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned research and pin applicable contracts — Read docs/research/20261028-skill-optimization/prepared-research/026-catalog-snapshots.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** Implement revised contract 1 — Represent requested id, observed resolved id, harness version and evidence digest separately for each attempt.
- [ ] **S003** Implement revised contract 2 — Version cache-write/read prices by model and billing mode; unknown cost never means free.
- [ ] **S004** Implement revised contract 3 — Test concurrent refresh and stale fallback without rewriting bindings of in-progress tasks.
- [ ] **S005** Validate all assigned positive and negative cases — Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** Record implementation evidence for independent review — Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

## Scope

In: Implement model catalog evidence, caches, snapshots and refresh
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/model_catalog.py`, `skill/plan-and-execute/scripts/model_catalogctl.py`, `test/optimization/catalog_snapshots_self_test.py`, `skill/plan-and-execute/references/MODEL_CATALOG.md`, `docs/research/20261028-skill-optimization/implementation/026-receipt.json`, `docs/research/20261028-skill-optimization/implementation/026-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/026-catalog-snapshots.md.
- Use only task 026 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/026-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance

- Fresh facets produce no network/probe calls; expired or changed-version capability triggers only its required source.
- A failing refresh retains the last valid cache with a visible stale warning.
- Concurrent refreshes of different providers do not overwrite one another.
- An empty advanced tier lifts to a configured stronger tier or yields an explicit ineligible candidate.
- An in-progress task retains its model while pending tasks can rebase with an audit entry.
- An alias backend change invalidates the relevant candidate evidence while keeping the old attempt record intact.
- Failed partial refresh leaves valid prior facets readable with explicit age.
- Legacy config snapshots do not inherit a newly enabled global switch policy.
- Unknown prices cannot win a cost comparison by being treated as zero.
- Prepared research is not proof of implementation or independent-review completion.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_026`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_026`
