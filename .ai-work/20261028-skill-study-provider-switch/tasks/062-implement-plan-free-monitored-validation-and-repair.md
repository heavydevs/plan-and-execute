---
task_id: "062"
status: "pending"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "001,051,061"
allowed_related_task_reads: "none"
---

# 062 — Implement plan-free monitored validation and repair

Objective: Keep validate-or-fix as a thin plan-free entrypoint into the shared monitoring and evidence engine, with explicit repair authorization and no hidden second orchestration state.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned research and pin applicable contracts — Read docs/research/20261028-skill-optimization/prepared-research/062-validate-or-fix.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** Implement revised contract 1 — Keep validate-only and repair authorization distinct; DIRECT monitoring creates no implementation TODO plan.
- [ ] **S003** Implement revised contract 2 — Reuse the same runtime state, map, classification and cancellation code instead of copying logic into the companion.
- [ ] **S004** Implement revised contract 3 — Pin standalone validation sessions to command/input/map generation and preserve unrelated plans and user logs.
- [ ] **S005** Validate all assigned positive and negative cases — Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** Record implementation evidence for independent review — Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

## Scope

In: Implement plan-free monitored validation and repair
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/validatectl.py`, `skill/plan-and-execute/scripts/companion_validation_self_test.py`, `test/optimization/validate_or_fix_self_test.py`, `skill/validate-or-fix/SKILL.md`, `skill/validate-or-fix/agents/openai.yaml`, `skill/validate-or-fix/scripts/validatectl.py`, `skill/validate-or-fix/scripts/service_map.py`, `skill/validate-or-fix/scripts/workload_routing.py`, `skill/validate-or-fix/references/ROUTING.md`, `skill/validate-or-fix/references/OPERATIONS.md`, `docs/research/20261028-skill-optimization/implementation/062-receipt.json`, `docs/research/20261028-skill-optimization/implementation/062-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/062-validate-or-fix.md.
- Use only task 062 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/062-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance

- A short passing command leaves no manifest, TODO or orchestration directory.
- A long mapped validation records progress and can diagnose a stall without creating a plan.
- A successful old receipt is rejected after source or command changes.
- A missing companion/shared implementation produces an actionable version error.
- A failed repair never overwrites a successful receipt or claims completion from a model narrative.
- Validate-only failure leaves source files unchanged.
- Standalone monitored validation creates no plan manifest or TODO checklist.
- A missing companion runtime dependency fails before test/model execution.
- Authorized repair obeys write scope and passes independent rerun before success.
- Prepared research is not proof of implementation or independent-review completion.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_062`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_062`
