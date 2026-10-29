---
task_id: "034"
status: "pending"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "001,025,033"
allowed_related_task_reads: "none"
---

# 034 — Implement antigravity and legacy Gemini adapter

Objective: Treat Antigravity as a versioned multi-backend harness with account-scoped quotas and billing; derive effort from actual model capabilities and keep unproven read-only observation disabled.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned research and pin applicable contracts — Read docs/research/20261028-skill-optimization/prepared-research/034-antigravity.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** Implement revised contract 1 — Record the conflict between headless effort docs and the effort command; resolve with pinned-version capabilities, not an invented universal cap.
- [ ] **S003** Implement revised contract 2 — Separate partner-model quota from credit/cash and first-party coordination charges; never enable paid overages automatically.
- [ ] **S004** Implement revised contract 3 — Require proven read-only boundaries before any Antigravity observer; otherwise use deterministic monitoring only.
- [ ] **S005** Validate all assigned positive and negative cases — Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** Record implementation evidence for independent review — Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

## Scope

In: Implement antigravity and legacy Gemini adapter
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/routing_config.py`, `skill/plan-and-execute/scripts/workload_routing.py`, `test/optimization/antigravity_self_test.py`, `skill/plan-and-execute/references/INSTALLATION.md`, `skill/plan-and-execute/references/INSTALLATION.pt-BR.md`, `docs/research/20261028-skill-optimization/implementation/034-receipt.json`, `docs/research/20261028-skill-optimization/implementation/034-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/034-antigravity.md.
- Use only task 034 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/034-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance

- An embedded high slug receives no redundant effort flag and is not retried as a supposedly stronger identical dispatch.
- A model with lower effort support cannot satisfy a higher required route without explicit qualification.
- Separate configured pools have separate cooldowns; shared pools remain shared.
- Usage discovery failure leaves quota unknown and does not consume semantic attempts.
- Headless parser, conversation metadata and read-only restrictions have version-pinned fixtures.
- A documented but unavailable max variant is skipped with a capability reason.
- Embedded-effort aliases that yield identical dispatch are collapsed.
- A separate quota pool cannot bypass disabled paid-overage policy.
- Workspace-write sandbox support does not qualify a route as read-only.
- Prepared research is not proof of implementation or independent-review completion.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_034`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_034`
