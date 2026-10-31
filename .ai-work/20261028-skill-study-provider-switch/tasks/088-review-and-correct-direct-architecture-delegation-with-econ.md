---
task_id: "088"
status: "pending"
requirements: "R046"
dependencies: "087"
allowed_related_task_reads: "none"
---

# 088 — Review and correct direct architecture delegation with economical implementation

Objective: Independently review and correct direct architecture delegation with economical implementation using actual implementation and validation evidence.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read implementation — Review the actual code, test results and receipt from task 087, not a previous conversation.
- [ ] **S002** Independent review — Dispatch a real fresh maximum-qualified reviewer and preserve provider, model, effort and reviewed hashes.
- [ ] **S003** Correct high-risk defects — Correct critical/high findings or leave the task pending with evidence.
- [ ] **S004** Rerun regressions — Run test/optimization/direct_architecture_handoff_self_test.py and all feature acceptance and negative cases through mapped validation.
- [ ] **S005** Record review — Record actual review/validation results in docs/research/20261028-skill-optimization/implementation/088-receipt.json and docs/research/20261028-skill-optimization/implementation/088-outcome.md.

## Scope

In: Review and correct direct architecture delegation with economical implementation
Out: No second plan or unrelated changes.; No installation, provider login, publishing or user-global configuration changes without permission.
Files: `skill/plan-and-execute/scripts/direct_route.py`, `skill/plan-and-execute/scripts/validatectl.py`, `skill/plan-and-execute/scripts/workload_routing.py`, `skill/plan-and-execute/references/ROUTING.md`, `skill/plan-and-execute/references/DELEGATION.md`, `skill/plan-and-execute/references/MODEL_ROUTING.md`, `skill/plan-and-execute/references/TEST_RESOURCE_MONITORING.md`, `test/optimization/direct_architecture_handoff_self_test.py`, `docs/research/20261028-skill-optimization/implementation/088-receipt.json`, `docs/research/20261028-skill-optimization/implementation/088-outcome.md`

## Guidance

- Read docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261031.md.
- Follow task 088 in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Preserve exact user intent, bounded context, security floors and real deterministic tests.
- Use an actual fresh independent maximum-qualified reviewer; never fabricate model execution.
- Preserve evidence in docs/research/20261028-skill-optimization/implementation/088-receipt.json and docs/research/20261028-skill-optimization/implementation/088-outcome.md; do not mark a pending task done without validation.

## Acceptance

- Record a real fresh independent reviewer route and exact reviewed input hashes.
- Verify: A cohesive seven-file task stays DIRECT even when one difficult design decision needs a stronger architect.
- Verify: The inexpensive stage reads all relevant files; the architecture worker receives a precise evidence packet, not a duplicated source dump.
- Verify: The architect outputs a durable design; implementation can return to a lower qualified tier with acceptance checks.
- Verify: Stateful DIRECT validations use project resource mapping and log monitoring without creating a TODO plan.
- Verify: Compare complete validated cost (read, design, implementation, retries, reviews) to a single qualified model; preserve security floors.
- No unresolved critical/high finding or missing required reviewer may be marked complete.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_088`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_088`
