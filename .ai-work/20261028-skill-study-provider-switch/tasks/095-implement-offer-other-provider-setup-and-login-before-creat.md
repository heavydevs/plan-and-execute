---
task_id: "095"
status: "pending"
requirements: "R050"
dependencies: "007,009,023,027,031,033,035,037,039,041,043,045,047"
allowed_related_task_reads: "none"
---

# 095 — Implement offer other-provider setup and login before creating a plan

Objective: Only at new ORCHESTRATED plan creation, discover alternate provider agents and separately ask permission for missing configuration or login; never prompt during DIRECT work or task execution.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read evidence — Read docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261031.md, assigned prepared research and materially affected source files.
- [ ] **S002** Implement contract 1 — Discover alternate provider agents, installed versions, config and auth readiness with bounded non-generative probes.
- [ ] **S003** Implement contract 2 — Classify ready, needs_config, needs_login, unsupported and unknown without exposing secrets.
- [ ] **S004** Implement contract 3 — Ask separately for each discovered agent needing setup/login before new-plan tasks are created; persist choices.
- [ ] **S005** Implement contract 4 — Exclude unavailable providers without capability downgrade; do not ask again on resume, task runs or simple requests.
- [ ] **S006** Run tests — Implement test/optimization/provider_readiness_gate_self_test.py and run mapped validation plus feature negative cases.
- [ ] **S007** Record implementation — Record real implementation and test evidence in docs/research/20261028-skill-optimization/implementation/095-receipt.json and docs/research/20261028-skill-optimization/implementation/095-outcome.md.

## Scope

In: Only at new ORCHESTRATED plan creation, discover alternate provider agents and separately ask permission for missing configuration or login; never prompt during DIRECT work or task execution.
Out: No second plan or unrelated changes.; No installation, provider login, publishing or user-global configuration changes without permission.
Files: `skill/plan-and-execute/scripts/preplanctl.py`, `skill/plan-and-execute/scripts/configure.py`, `skill/plan-and-execute/scripts/model_catalogctl.py`, `skill/plan-and-execute/scripts/routingctl.py`, `skill/plan-and-execute/references/INTAKE.md`, `skill/plan-and-execute/references/ORCHESTRATION.md`, `skill/plan-and-execute/references/PLANNING_PROTOCOL.md`, `skill/plan-and-execute/references/ROUTING_CONFIG.md`, `test/optimization/provider_readiness_gate_self_test.py`, `docs/research/20261028-skill-optimization/implementation/095-receipt.json`, `docs/research/20261028-skill-optimization/implementation/095-outcome.md`

## Guidance

- Read docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261031.md.
- Follow task 095 in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Preserve exact user intent, bounded context, security floors and real deterministic tests.
- Refresh only materially changed facts from assigned prepared reports 006, 028, 060, 062.
- Preserve evidence in docs/research/20261028-skill-optimization/implementation/095-receipt.json and docs/research/20261028-skill-optimization/implementation/095-outcome.md; do not mark a pending task done without validation.

## Acceptance

- Each discovered agent needing setup/login gets a separate named consent question only during new-plan preparation.
- Without consent no login, config mutation, token exposure or paid model call occurs.
- Ready agents are not re-prompted; declined and unsupported agents have explicit reasons.
- Existing-plan resume, running TODOs, DIRECT changes and shell commands never run this questionnaire.
- Unknown availability cannot silently widen a forbidden provider chain or lower capability.
- Implementation and review remain pending until actual execution evidence exists.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_095`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_095`
