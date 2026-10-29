---
task_id: "044"
status: "pending"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "001,035"
allowed_related_task_reads: "none"
---

# 044 — Implement gLM provider profiles

Objective: Resolve GLM backend identity independently of Claude role aliases, with isolated per-process profiles, explicit billing eligibility and measured workload capability.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned research and pin applicable contracts — Read docs/research/20261028-skill-optimization/prepared-research/044-glm.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** Implement revised contract 1 — Include endpoint/profile and resolved backend model in GLM route identity; collapse duplicate alias rungs.
- [ ] **S003** Implement revised contract 2 — Apply profile environment overlays only to child processes and never modify user-global settings.
- [ ] **S004** Implement revised contract 3 — Keep Coding Plan eligibility, quota and PAYG billing as separate explicit capabilities.
- [ ] **S005** Validate all assigned positive and negative cases — Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** Record implementation evidence for independent review — Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

## Scope

In: Implement gLM provider profiles
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/routing_config.py`, `skill/plan-and-execute/scripts/glm_provider_self_test.py`, `test/optimization/glm_self_test.py`, `skill/plan-and-execute/references/MODEL_ROUTING_GLM.md`, `docs/research/20261028-skill-optimization/implementation/044-receipt.json`, `docs/research/20261028-skill-optimization/implementation/044-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/044-glm.md.
- Use only task 044 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/044-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance

- An Opus alias mapped to GLM retains backend=GLM in route, telemetry and cooldown identity.
- Unknown/unsupported effort is rejected or mapped by an explicit tested rule, never silently upgraded.
- Two profiles using the same host but different quota pools do not contaminate one another.
- Secret values are absent from show/config receipts, logs and handoff packets.
- Version1 configuration snapshots preserve their original behavior.
- Opus and Sonnet aliases mapped to one GLM model do not count as a capability increase.
- Child profile settings cannot leak into another provider process.
- Coding Plan quota exhaustion cannot enable an API-paid route implicitly.
- Unknown native effort support causes an explicit skip rather than guessed equivalence.
- Prepared research is not proof of implementation or independent-review completion.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_044`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_044`
