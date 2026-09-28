---
task_id: "003"
status: "pending"
requirements: "R003,R004,R009"
dependencies: "002"
allowed_related_task_reads: "none"
---

# 003 — Implement resumable availability failover

Objective: Rotate unavailable providers at equivalent capability and pause boundedly without semantic escalation.

## Context

- None

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Implement and verify the bounded contract — Rotate unavailable providers at equivalent capability and pause boundedly without semantic escalation.

## Scope

In: Rotate unavailable providers at equivalent capability and pause boundedly without semantic escalation.
Out: No unrelated framework refactoring or changes to model pricing/catalog.
Files: `skill/plan-and-execute/scripts/availability.py`, `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/availability_self_test.py`

## Guidance

- Read docs/research/AUXILIARY_ROUTING.md for security and economic constraints.
- Use deterministic validations and record host-managed execution honestly.

## Acceptance

- Rotate unavailable providers at equivalent capability and pause boundedly without semantic escalation.
- AVAILABILITY validation passes; negative cases and limitations are recorded.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation AVAILABILITY`
