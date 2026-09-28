---
task_id: "002"
status: "completed"
requirements: "R002,R006,R009"
dependencies: "001"
allowed_related_task_reads: "none"
---

# 002 — Implement layered tier routing configuration

Objective: Load validated global and plan overlays without freezing defaults or changing legacy snapshots.

## Context

- None

## Validated learnings

- None

## Checkpoints

- [x] **S001** Implement and verify the bounded contract — Load validated global and plan overlays without freezing defaults or changing legacy snapshots.

## Scope

In: Load validated global and plan overlays without freezing defaults or changing legacy snapshots.
Out: No unrelated framework refactoring or changes to model pricing/catalog.
Files: `skill/plan-and-execute/scripts/routing_config.py`, `skill/plan-and-execute/scripts/routing_config_self_test.py`, `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/planctl.py`

## Guidance

- Read docs/research/AUXILIARY_ROUTING.md for security and economic constraints.
- Use deterministic validations and record host-managed execution honestly.

## Acceptance

- Load validated global and plan overlays without freezing defaults or changing legacy snapshots.
- ROUTING_CONFIG validation passes; negative cases and limitations are recorded.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation ROUTING_CONFIG`
