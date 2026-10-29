---
task_id: "024"
status: "pending"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "001,023"
allowed_related_task_reads: "none"
---

# 024 — Implement workload routing for frontend, repair and monitoring

Objective: Route by measured workload capability and validation strength, with separate design, functional UI, monitoring and repair requirements rather than a universal model leaderboard.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned research and pin applicable contracts — Read docs/research/20261028-skill-optimization/prepared-research/024-workload-affinity.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** Implement revised contract 1 — Separate visual design, UI behavior, accessibility, observation and repair capabilities in workload evidence.
- [ ] **S003** Implement revised contract 2 — Use deterministic monitoring first; route only bounded novel ambiguity to a permitted observer.
- [ ] **S004** Implement revised contract 3 — Treat manager-quota preference as secondary to capability, privacy and validation floors; never infer effective effort from a family label.
- [ ] **S005** Validate all assigned positive and negative cases — Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** Record implementation evidence for independent review — Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

## Scope

In: Implement workload routing for frontend, repair and monitoring
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/workload_routing.py`, `skill/plan-and-execute/scripts/configure.py`, `test/optimization/workload_affinity_self_test.py`, `skill/plan-and-execute/references/MODEL_MAPPING.md`, `docs/research/20261028-skill-optimization/implementation/024-receipt.json`, `docs/research/20261028-skill-optimization/implementation/024-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/024-workload-affinity.md.
- Use only task 024 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/024-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance

- A preferred intermediate profile is excluded from a maximum-capability task when its validated range is lower.
- An observer profile cannot be selected for a source-writing task or gain write tools on fallback.
- Frontend evaluation detects broken keyboard navigation even when screenshots match.
- A depleted Gemini pool can use another configured pool without assuming all accounts have independent allocations.
- Unknown economics remains unknown; ties use stable policy instead of invented prices.
- A visual-only success cannot satisfy a task with keyboard and functional acceptance checks.
- A cheap observer route is never selected to implement an architecture-sensitive repair.
- A manager quota preference cannot lower the minimum effective capability.
- Unknown quota or cost values do not become zero-cost priority.
- Prepared research is not proof of implementation or independent-review completion.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_024`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_024`
