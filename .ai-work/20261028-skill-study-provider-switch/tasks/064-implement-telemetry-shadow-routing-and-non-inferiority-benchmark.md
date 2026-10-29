---
task_id: "064"
status: "pending"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "001,005"
allowed_related_task_reads: "none"
---

# 064 — Implement telemetry, shadow routing and non-inferiority benchmarks

Objective: Evaluate quality-constrained cost with paired task-level experiments, versioned native usage and honest missing data; keep offline replay separate from evidence of real model performance.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned research and pin applicable contracts — Read docs/research/20261028-skill-optimization/prepared-research/064-economic-evaluation.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** Implement revised contract 1 — Resample by unique task or repository cluster and preserve pairing; repeated fixture replay cannot increase empirical sample size.
- [ ] **S003** Implement revised contract 2 — Predeclare quality/cost/latency gates and count failed, timed-out and auxiliary calls without favorable censoring.
- [ ] **S004** Implement revised contract 3 — Version billing units and reject non-finite usage; unknown cost and zero-success ratios cannot become apparent savings.
- [ ] **S005** Validate all assigned positive and negative cases — Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** Record implementation evidence for independent review — Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

## Scope

In: Implement telemetry, shadow routing and non-inferiority benchmarks
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/routing_telemetry.py`, `tools/skill_benchmark.py`, `tools/routing_eval.py`, `test/optimization/economic_evaluation_self_test.py`, `docs/research/SKILL_BENCHMARK.md`, `docs/research/routing-eval/thresholds.json`, `docs/research/20261028-skill-optimization/implementation/064-receipt.json`, `docs/research/20261028-skill-optimization/implementation/064-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/064-economic-evaluation.md.
- Use only task 064 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/064-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance

- Non-finite numbers cannot produce a successful numeric rollup or invalid JSON.
- Missing cost remains unknown and is not silently compared as free.
- Failed attempts and diagnostic/handoff costs are included in cost per validated result.
- Repeating a fixed corpus changes replay count but not the claimed independent sample count.
- A candidate with lower apparent cost but worse critical acceptance cannot pass the quality gate.
- Duplicating deterministic replay rows does not narrow empirical confidence intervals.
- NaN, infinity and negative usage are rejected; missing values remain null.
- A zero-success arm cannot report zero cost per validated result.
- Cold/warm cache and subscription/API modes remain distinct in rollups.
- Prepared research is not proof of implementation or independent-review completion.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_064`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_064`
