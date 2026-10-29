---
task_id: "042"
status: "pending"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "001,041"
allowed_related_task_reads: "none"
---

# 042 — Implement muse Code adapter and session protocol

Objective: Use Muse explicit headless session/event contracts, enforce checkout isolation for parallel writers and reconcile cooperative cancellation before replacement workers.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned research and pin applicable contracts — Read docs/research/20261028-skill-optimization/prepared-research/042-muse.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** Implement revised contract 1 — Require explicit isolation or serialization for Muse writers and verify the pinned source revision.
- [ ] **S003** Implement revised contract 2 — Wait for terminal cancellation evidence before replacement or cleanup; uncertain state remains recoverable.
- [ ] **S004** Implement revised contract 3 — Use exact headless session ids and versioned event schemas, never interactive resume in unattended execution.
- [ ] **S005** Validate all assigned positive and negative cases — Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** Record implementation evidence for independent review — Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

## Scope

In: Implement muse Code adapter and session protocol
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/muse_provider_self_test.py`, `test/optimization/muse_self_test.py`, `skill/plan-and-execute/references/MODEL_ROUTING_MUSE.md`, `docs/research/20261028-skill-optimization/implementation/042-receipt.json`, `docs/research/20261028-skill-optimization/implementation/042-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/042-muse.md.
- Use only task 042 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/042-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance

- A fixture for an unrelated muse executable is rejected before any task starts.
- No-session-log and resume options are not combined incompatibly.
- Two children sharing a checkout cannot be mistaken for isolated parallel writers.
- Read-only summary and implementation command paths have different tested authority.
- Large or malformed JSONL cannot cause unbounded memory or false completion.
- A rejected isolation request cannot run in the shared checkout.
- A cancelled child still writing blocks replacement until terminal reconciliation.
- Interactive muse resume is not selected for a headless recovery.
- An unrelated child log cannot be imported as task evidence.
- Prepared research is not proof of implementation or independent-review completion.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_042`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_042`
