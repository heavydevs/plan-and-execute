---
task_id: "005"
status: "pending"
requirements: "R007,R008,R009"
dependencies: "002,003"
allowed_related_task_reads: "none"
---

# 005 — Implement safe budgeted validation assistance

Objective: Provide gated, bounded, non-authoritative diagnostic advice without repository write access.

## Context

- None

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Implement and verify the bounded contract — Provide gated, bounded, non-authoritative diagnostic advice without repository write access.

## Scope

In: Provide gated, bounded, non-authoritative diagnostic advice without repository write access.
Out: No unrelated framework refactoring or changes to model pricing/catalog.
Files: `skill/plan-and-execute/scripts/assistant_triage.py`, `skill/plan-and-execute/scripts/assistant_triage_self_test.py`, `skill/plan-and-execute/scripts/run_isolated.py`

## Guidance

- Read docs/research/AUXILIARY_ROUTING.md for security and economic constraints.
- Use deterministic validations and record host-managed execution honestly.

## Acceptance

- Provide gated, bounded, non-authoritative diagnostic advice without repository write access.
- ASSISTANT validation passes; negative cases and limitations are recorded.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation ASSISTANT`
