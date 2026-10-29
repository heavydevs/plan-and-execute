---
task_id: "006"
status: "pending"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "001"
allowed_related_task_reads: "none"
---

# 006 — Implement selective activation, intake and late promotion

Objective: Keep DIRECT as a zero-orchestration fast path, with explicit risk/promotion signals and evaluated activation; do not add a classifier call.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned research and pin applicable contracts — Read docs/research/20261028-skill-optimization/prepared-research/006-activation-intake.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** Implement revised contract 1 — Record bounded reason codes only in the selected workflow; a rejected implicit match creates no plan, ledger or study files.
- [ ] **S003** Implement revised contract 2 — Evaluate activation false positives, false negatives, extra tokens, latency and final correctness on distinct held-out prompts.
- [ ] **S004** Implement revised contract 3 — Separate routing mode from capability tier so a small risky fix can stay DIRECT with a qualified implementation route.
- [ ] **S005** Validate all assigned positive and negative cases — Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** Record implementation evidence for independent review — Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

## Scope

In: Implement selective activation, intake and late promotion
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/requestctl.py`, `skill/plan-and-execute/scripts/promotectl.py`, `skill/plan-and-execute/scripts/routing_self_test.py`, `test/optimization/activation_intake_self_test.py`, `skill/plan-and-execute/SKILL.md`, `skill/plan-and-execute/agents/openai.yaml`, `skill/plan-and-execute/references/ROUTING.md`, `skill/plan-and-execute/references/PROMOTION.md`, `skill/plan-and-execute/references/routing-evals.json`, `docs/research/20261028-skill-optimization/implementation/006-receipt.json`, `docs/research/20261028-skill-optimization/implementation/006-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/006-activation-intake.md.
- Use only task 006 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/006-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance

- A one-module feature touching seven files remains DIRECT and leaves no plan artifacts.
- A short security-sensitive fix remains direct when cohesive, but its model floor is not lowered.
- A promoted task includes only remaining outcomes and preserves the original worktree.
- Measure entrypoint bytes, referenced files actually loaded and routing false-positive/false-negative cases against baseline.
- A near-finished high-context task stays DIRECT without creating control files.
- A tiny security-sensitive edit can select a strong worker without forcing an orchestration plan.
- Promotion preserves changed files and validated outcomes and schedules only remaining work.
- Prepared research is not proof of implementation or independent-review completion.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_006`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_006`
