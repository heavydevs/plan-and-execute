---
task_id: "030"
status: "pending"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "001,029"
allowed_related_task_reads: "none"
---

# 030 — Implement claude Code and Claude Agent SDK adapter

Objective: Keep the Claude CLI adapter as the compatibility reference, add versioned capability fixtures and least-privilege role profiles, and evaluate SDK/native workflows only behind an explicit adapter boundary.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned research and pin applicable contracts — Read docs/research/20261028-skill-optimization/prepared-research/030-claude.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** Implement revised contract 1 — Pin documented CLI capabilities by version and fail on unsupported security or structured-output options.
- [ ] **S003** Implement revised contract 2 — Test review tool inheritance and source-revision isolation rather than trusting a read-only prompt.
- [ ] **S004** Implement revised contract 3 — Compare SDK or native workflows with CLI execution only after lifecycle, billing and validation equivalence checks.
- [ ] **S005** Validate all assigned positive and negative cases — Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** Record implementation evidence for independent review — Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

## Scope

In: Implement claude Code and Claude Agent SDK adapter
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/provider_self_test.py`, `test/optimization/claude_self_test.py`, `skill/plan-and-execute/references/MODEL_ROUTING_CLAUDE.md`, `docs/research/20261028-skill-optimization/implementation/030-receipt.json`, `docs/research/20261028-skill-optimization/implementation/030-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/030-claude.md.
- Use only task 030 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/030-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance

- Default worker argv retains no-session-persistence and existing approved permission behavior.
- Summary mode cannot write a planted repository file or execute an unapproved mutating tool in a supported test environment.
- Invalid JSON, missing report fields, quota errors and semantic failures take different paths.
- A model alias mapped through another endpoint is reported with host and backend identity.
- Unknown usage is null and no secret environment values enter diagnostics.
- A partial max-turn result cannot complete a task.
- No-session-persistence does not trigger an automatic resume attempt.
- Unsupported permission restrictions fail closed without global settings changes.
- A restricted reviewer cannot invoke inherited write tools.
- Prepared research is not proof of implementation or independent-review completion.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_030`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_030`
