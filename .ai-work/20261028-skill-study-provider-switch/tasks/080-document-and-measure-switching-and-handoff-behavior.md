---
task_id: "080"
status: "pending"
requirements: "R005,R006,R012,R028,R029,R031,R033,R034,R035,R037,R045"
dependencies: "079,065,067"
allowed_related_task_reads: "none"
---

# 080 — Document and measure switching and handoff behavior

Objective: Record metadata-only telemetry, update configuration help and synchronized documentation, and evaluate the old/new deterministic scenario matrix.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Inspect assigned inputs — Record decisive source evidence without loading unrelated task history.
- [ ] **S002** Produce the bounded deliverable — Record metadata-only telemetry, update configuration help and synchronized documentation, and evaluate the old/new deterministic scenario matrix.
- [ ] **S003** Validate and checkpoint — Pass the mapped packet check and retain exact validation evidence.

## Scope

In: Document and measure switching and handoff behavior
Out: Do not implement unrelated optimization backlog items.
Files: `docs/research/20261028-skill-optimization/outputs/080-switch-docs-telemetry.json`, `docs/research/20261028-skill-optimization/topics/080-switch-docs-telemetry.md`, `skill/plan-and-execute/scripts/routing_telemetry.py`, `skill/plan-and-execute/scripts/telemetry_self_test.py`, `skill/plan-and-execute/scripts/configure.py`, `skill/plan-and-execute/scripts/configure_self_test.py`, `skill/plan-and-execute/references/ROUTING_CONFIG.md`, `skill/plan-and-execute/references/MODEL_ROUTING.md`, `skill/plan-and-execute/references/WORKFLOW.md`, `skill/plan-and-execute/references/PLAN_SPEC.md`, `README.md`, `README.pt-BR.md`, `CHANGELOG.md`, `docs/RESEARCH_BASIS.md`, `tools/run-skill-self-test.js`, `.ai-work/SERVICE_MAP.md`

## Guidance

- Read docs/plans/20261028-skill-optimization/PROTOCOL.md and only the input paths listed in docs/plans/20261028-skill-optimization/TASK_INPUTS.json for task 080.
- Expected runtime paths are candidate ownership boundaries, not a mandate to edit every file; the approved ADR controls the minimal diff.

## Acceptance

- Report switch reason, source/destination, actual handoff cost or unknown, and post-switch validation outcome without secrets.
- All twelve source acceptance cases are mapped to tests; replay results are not presented as real quota or dollar savings.
- Run affected tests and npm ci, npm run check, npm pack --dry-run under the reconciled map; report all real exit results.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_080`
