---
task_id: "074"
status: "pending"
requirements: "R006,R012,R013,R015,R016,R024,R025,R026,R027,R028,R031,R034"
dependencies: "073"
allowed_related_task_reads: "none"
---

# 074 — Integrate coherent switching, budgets and availability

Objective: Persist provider-local progress so every eligible provider gets a budgeted attempt before exhaustion, with separate availability and design semantics.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Inspect assigned inputs — Record decisive source evidence without loading unrelated task history.
- [ ] **S002** Produce the bounded deliverable — Persist provider-local progress so every eligible provider gets a budgeted attempt before exhaustion, with separate availability and design semantics.
- [ ] **S003** Validate and checkpoint — Pass the mapped packet check and retain exact validation evidence.

## Scope

In: Integrate coherent switching, budgets and availability
Out: Do not implement unrelated optimization backlog items.
Files: `docs/research/20261028-skill-optimization/outputs/074-switch-dispatch-state.json`, `docs/research/20261028-skill-optimization/topics/074-switch-dispatch-state.md`, `skill/plan-and-execute/scripts/availability.py`, `skill/plan-and-execute/scripts/routing_config.py`, `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/planctl.py`, `skill/plan-and-execute/scripts/artifact_contract.py`, `skill/plan-and-execute/scripts/availability_self_test.py`, `skill/plan-and-execute/scripts/routing_config_self_test.py`, `skill/plan-and-execute/scripts/self_test.py`, `skill/plan-and-execute/scripts/lifecycle_self_test.py`

## Guidance

- Read docs/plans/20261028-skill-optimization/PROTOCOL.md and only the input paths listed in docs/plans/20261028-skill-optimization/TASK_INPUTS.json for task 074.
- Expected runtime paths are candidate ownership boundaries, not a mandate to edit every file; the approved ADR controls the minimal diff.

## Acceptance

- The first, second and third eligible providers are reached in the documented budget-eight scenario.
- Quota and missing providers pause or fall back without functional failures; disabled fallback never widens the chain.
- Reset, design, schema 1-4, missing failure_classes and version-1 full config snapshots have regression tests.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_074`
