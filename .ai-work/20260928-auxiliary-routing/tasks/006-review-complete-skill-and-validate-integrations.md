---
task_id: "006"
status: "completed"
requirements: "R010,R009"
dependencies: "001,002,003,004,005"
allowed_related_task_reads: "none"
---

# 006 — Review complete skill and validate integrations

Objective: Pass full regressions and skill budgets; document native-platform limits and package the updated skill.

## Context

- None

## Validated learnings

- None

## Checkpoints

- [x] **S001** Implement and verify the bounded contract — Pass full regressions and skill budgets; document native-platform limits and package the updated skill.

## Scope

In: Pass full regressions and skill budgets; document native-platform limits and package the updated skill.
Out: No unrelated framework refactoring or changes to model pricing/catalog.
Files: `skill/plan-and-execute/SKILL.md`, `skill/plan-and-execute/references`, `tools`, `test`, `README.md`, `README.pt-BR.md`, `skill/plan-and-execute/scripts/self_test.py`, `skill/plan-and-execute/scripts/assistant_triage.py`, `skill/plan-and-execute/scripts/assistant_triage_self_test.py`, `skill/plan-and-execute/scripts/configure.py`, `docs/research`, `CHANGELOG.md`, `.github/workflows`, `skill/plan-and-execute/scripts/runner_contract.py`, `skill/plan-and-execute/scripts/availability_self_test.py`

## Guidance

- Read docs/research/AUXILIARY_ROUTING.md for security and economic constraints.
- Use deterministic validations and record host-managed execution honestly.
- Test routing precedence, quota resume, bounded assistant failures and wizard cancellation.

## Acceptance

- Pass full regressions and skill budgets; document native-platform limits and package the updated skill.
- ALL validation passes; negative cases and limitations are recorded.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation ALL`
