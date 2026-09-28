---
task_id: "004"
status: "pending"
requirements: "R005,R006,R009"
dependencies: "002"
allowed_related_task_reads: "none"
---

# 004 — Implement sequential routing configuration wizard

Objective: Configure primary, ordered fallbacks, models and assistant using separate numbered questions.

## Context

- None

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Implement and verify the bounded contract — Configure primary, ordered fallbacks, models and assistant using separate numbered questions.

## Scope

In: Configure primary, ordered fallbacks, models and assistant using separate numbered questions.
Out: No unrelated framework refactoring or changes to model pricing/catalog.
Files: `skill/plan-and-execute/scripts/configure.py`, `bin/plan-and-execute.js`, `skill/plan-and-execute/scripts/configure_self_test.py`

## Guidance

- Read docs/research/AUXILIARY_ROUTING.md for security and economic constraints.
- Use deterministic validations and record host-managed execution honestly.

## Acceptance

- Configure primary, ordered fallbacks, models and assistant using separate numbered questions.
- CONFIGURE validation passes; negative cases and limitations are recorded.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation CONFIGURE`
