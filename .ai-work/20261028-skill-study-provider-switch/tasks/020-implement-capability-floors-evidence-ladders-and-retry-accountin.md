---
task_id: "020"
status: "pending"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "001,005"
allowed_related_task_reads: "none"
---

# 020 — Implement capability floors, evidence ladders and retry accounting

Objective: Define a pure effective-dispatch ladder that removes no-op rungs, retains failure-specific retry semantics and leaves provider switching to its dedicated integration tasks.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned research and pin applicable contracts — Read docs/research/20261028-skill-optimization/prepared-research/020-escalation.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** Implement revised contract 1 — Implement pure effective capability identities and collapse equivalent rungs without treating quota or request metadata as increased capability.
- [ ] **S003** Implement revised contract 2 — Test pure provider/phase-local classified transitions, unsupported tiers and aliases without changing live runner state.
- [ ] **S004** Implement revised contract 3 — Expose reusable primitives for 072-074 and preserve the legacy-disabled argv and replay fixtures.
- [ ] **S005** Validate all assigned positive and negative cases — Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** Record implementation evidence for independent review — Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

## Scope

In: Implement capability floors, evidence ladders and retry accounting
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/routingctl.py`, `test/optimization/escalation_self_test.py`, `skill/plan-and-execute/references/MODEL_ROUTING.md`, `docs/research/20261028-skill-optimization/implementation/020-receipt.json`, `docs/research/20261028-skill-optimization/implementation/020-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/020-escalation.md.
- Use only task 020 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/020-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- TODO 020 implements pure ladder primitives and fixtures only. Persisted phase/provider counters and reset semantics belong to 072; actual dispatch, quota handling and attempt reservation belong to 074.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance

- Pure ladder fixtures deduplicate resolved model/native-effort identities while preserving capability floors.
- Pure transitions distinguish provider-local functional evidence from quota and environmental outcomes.
- Legacy-disabled argv and routing fixtures remain unchanged; runtime integration is deferred to 072-074.
- Different tier labels resolving to the same model and effective effort produce one capability rung.
- An ignored effort argument does not count as increased capability.
- A quota or environment failure does not advance the functional ladder.
- The default disabled option preserves existing argv and routing fixtures.
- Changing only quota pool, request nonce or log path cannot create a new capability rung.
- Non-adjacent aliases for the same effective dispatch do not recreate a failed top attempt.
- Prepared research is not proof of implementation or independent-review completion.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_020`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_020`
