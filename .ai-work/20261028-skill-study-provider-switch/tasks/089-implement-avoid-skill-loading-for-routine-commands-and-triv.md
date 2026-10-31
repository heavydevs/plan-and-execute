---
task_id: "089"
status: "pending"
requirements: "R047"
dependencies: "007,063"
allowed_related_task_reads: "none"
---

# 089 — Implement avoid skill loading for routine commands and trivial changes

Objective: Reduce implicit plan-and-execute activation for simple commands and trivial edits through concise discovery metadata and host-level negative invocation tests.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read evidence — Read docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261031.md, assigned prepared research and materially affected source files.
- [ ] **S002** Implement contract 1 — Narrow host-visible skill description/trigger language without requiring the full instruction body for a negative decision.
- [ ] **S003** Implement contract 2 — Test negative activation for git status, one-file read, short shell commands and trivial edits, plus positive explicit plan invocations.
- [ ] **S004** Implement contract 3 — Measure false activation, missed activation and prompt bytes on real host traces; do not add a paid classifier.
- [ ] **S005** Run tests — Implement test/optimization/skill_activation_negatives_self_test.py and run mapped validation plus feature negative cases.
- [ ] **S006** Record implementation — Record real implementation and test evidence in docs/research/20261028-skill-optimization/implementation/089-receipt.json and docs/research/20261028-skill-optimization/implementation/089-outcome.md.

## Scope

In: Reduce implicit plan-and-execute activation for simple commands and trivial edits through concise discovery metadata and host-level negative invocation tests.
Out: No second plan or unrelated changes.; No installation, provider login, publishing or user-global configuration changes without permission.
Files: `skill/plan-and-execute/SKILL.md`, `skill/plan-and-execute/agents/openai.yaml`, `skill/plan-and-execute/references/ROUTING.md`, `skill/validate-or-fix/SKILL.md`, `skill/plan-and-execute/references/routing-evals.json`, `test/optimization/skill_activation_negatives_self_test.py`, `docs/research/20261028-skill-optimization/implementation/089-receipt.json`, `docs/research/20261028-skill-optimization/implementation/089-outcome.md`

## Guidance

- Read docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261031.md.
- Follow task 089 in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Preserve exact user intent, bounded context, security floors and real deterministic tests.
- Refresh only materially changed facts from assigned prepared reports 006, 028, 060, 062.
- Preserve evidence in docs/research/20261028-skill-optimization/implementation/089-receipt.json and docs/research/20261028-skill-optimization/implementation/089-outcome.md; do not mark a pending task done without validation.

## Acceptance

- Simple shell commands, one-file reads and trivial edits do not implicitly load the full skill.
- Explicit plan/lifecycle commands and genuine multi-workstream jobs still activate.
- Tiny discoverable metadata cost is acknowledged; there is no claim of zero skill-related tokens.
- Held-out host evaluations measure false positives/negatives and token impact, not keyword assertions alone.
- Implementation and review remain pending until actual execution evidence exists.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_089`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_089`
