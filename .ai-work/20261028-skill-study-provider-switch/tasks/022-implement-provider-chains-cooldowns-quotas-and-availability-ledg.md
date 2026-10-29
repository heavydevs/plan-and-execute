---
task_id: "022"
status: "pending"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "001,021"
allowed_related_task_reads: "none"
---

# 022 — Implement provider chains, cooldowns, quotas and availability ledgers

Objective: Use one coherent allowed-provider chain and a bounded availability policy with explicit quota scopes, combined retry budgets and non-secret route fingerprints.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned research and pin applicable contracts — Read docs/research/20261028-skill-optimization/prepared-research/022-availability.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** Implement revised contract 1 — Track quota scope and observation expiry independently from functional failure evidence and provider capability.
- [ ] **S003** Implement revised contract 2 — Document and cap the combined runner, CLI and SDK retry budget; report unobservable internal retries as unknown.
- [ ] **S004** Implement revised contract 3 — Include allowed-provider, privacy, workload, snapshot and effective-routing settings in the availability fingerprint.
- [ ] **S005** Validate all assigned positive and negative cases — Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** Record implementation evidence for independent review — Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

## Scope

In: Implement provider chains, cooldowns, quotas and availability ledgers
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/availability.py`, `skill/plan-and-execute/scripts/workload_routing.py`, `test/optimization/availability_self_test.py`, `skill/plan-and-execute/references/ROUTING_CONFIG.md`, `docs/research/20261028-skill-optimization/implementation/022-receipt.json`, `docs/research/20261028-skill-optimization/implementation/022-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/022-availability.md.
- Use only task 022 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/022-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- TODO 022 implements the availability contract and backward-compatible selector seam. The opt-in top-switch controller is integrated only by 074; disabled behavior must remain unchanged.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance

- Quota in one configured pool does not block another pool unless the configuration explicitly shares it.
- Availability failures leave functional failure counts and semantic ladder evidence unchanged.
- Fallback-disabled and CLI-pinned cases never widen the allowed chain.
- A changed route fingerprint invalidates cached intent while retaining unrelated valid cooldowns.
- Every eligible unavailable candidate yields a bounded, redacted reason; all-unavailable returns75 without a spin loop.
- Quota exhaustion in one configured pool leaves another observed-independent pool eligible.
- A fallback that violates required capabilities or data policy is rejected with a reason.
- SDK retry fixtures cannot multiply an unbounded runner wait.
- Availability pauses preserve subtasks without adding a functional failure.
- Prepared research is not proof of implementation or independent-review completion.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_022`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_022`
