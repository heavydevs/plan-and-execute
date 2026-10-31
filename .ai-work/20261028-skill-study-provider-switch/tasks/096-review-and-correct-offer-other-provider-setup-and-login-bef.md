---
task_id: "096"
status: "pending"
requirements: "R050"
dependencies: "095"
allowed_related_task_reads: "none"
---

# 096 — Review and correct offer other-provider setup and login before creating a plan

Objective: Independently review and correct offer other-provider setup and login before creating a plan using actual implementation and validation evidence.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read implementation — Review the actual code, test results and receipt from task 095, not a previous conversation.
- [ ] **S002** Independent review — Dispatch a real fresh maximum-qualified reviewer and preserve provider, model, effort and reviewed hashes.
- [ ] **S003** Correct high-risk defects — Correct critical/high findings or leave the task pending with evidence.
- [ ] **S004** Rerun regressions — Run test/optimization/provider_readiness_gate_self_test.py and all feature acceptance and negative cases through mapped validation.
- [ ] **S005** Record review — Record actual review/validation results in docs/research/20261028-skill-optimization/implementation/096-receipt.json and docs/research/20261028-skill-optimization/implementation/096-outcome.md.

## Scope

In: Review and correct offer other-provider setup and login before creating a plan
Out: No second plan or unrelated changes.; No installation, provider login, publishing or user-global configuration changes without permission.
Files: `skill/plan-and-execute/scripts/preplanctl.py`, `skill/plan-and-execute/scripts/configure.py`, `skill/plan-and-execute/scripts/model_catalogctl.py`, `skill/plan-and-execute/scripts/routingctl.py`, `skill/plan-and-execute/references/INTAKE.md`, `skill/plan-and-execute/references/ORCHESTRATION.md`, `skill/plan-and-execute/references/PLANNING_PROTOCOL.md`, `skill/plan-and-execute/references/ROUTING_CONFIG.md`, `test/optimization/provider_readiness_gate_self_test.py`, `docs/research/20261028-skill-optimization/implementation/096-receipt.json`, `docs/research/20261028-skill-optimization/implementation/096-outcome.md`

## Guidance

- Read docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261031.md.
- Follow task 096 in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Preserve exact user intent, bounded context, security floors and real deterministic tests.
- Use an actual fresh independent maximum-qualified reviewer; never fabricate model execution.
- Preserve evidence in docs/research/20261028-skill-optimization/implementation/096-receipt.json and docs/research/20261028-skill-optimization/implementation/096-outcome.md; do not mark a pending task done without validation.

## Acceptance

- Record a real fresh independent reviewer route and exact reviewed input hashes.
- Verify: Each discovered agent needing setup/login gets a separate named consent question only during new-plan preparation.
- Verify: Without consent no login, config mutation, token exposure or paid model call occurs.
- Verify: Ready agents are not re-prompted; declined and unsupported agents have explicit reasons.
- Verify: Existing-plan resume, running TODOs, DIRECT changes and shell commands never run this questionnaire.
- Verify: Unknown availability cannot silently widen a forbidden provider chain or lower capability.
- No unresolved critical/high finding or missing required reviewer may be marked complete.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_096`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_096`
