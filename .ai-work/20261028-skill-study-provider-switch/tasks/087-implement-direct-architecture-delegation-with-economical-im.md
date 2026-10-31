---
task_id: "087"
status: "pending"
requirements: "R046"
dependencies: "007,025,029,051,061,063"
allowed_related_task_reads: "none"
---

# 087 — Implement direct architecture delegation with economical implementation

Objective: For cohesive multi-file DIRECT work, inspect relevant files cheaply, delegate difficult architecture to a stronger model only when justified, then choose a qualified economical executor and monitored tests.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read evidence — Read docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261031.md, assigned prepared research and materially affected source files.
- [ ] **S002** Implement contract 1 — Inventory and read all materially relevant files with the current affordable model; forward only decision-relevant evidence to stronger context.
- [ ] **S003** Implement contract 2 — Classify architecture complexity independently of plan need; delegate high-risk architecture to a qualified stronger tier with durable design.
- [ ] **S004** Implement contract 3 — Return bounded implementation to the current or intermediate tier when testability and capability floors justify it; reroute expensive silent-failure work upward.
- [ ] **S005** Implement contract 4 — Run meaningful DIRECT tests through shared resource/log/progress watchers, optionally using a cheap, read-only event-triggered observer.
- [ ] **S006** Run tests — Implement test/optimization/direct_architecture_handoff_self_test.py and run mapped validation plus feature negative cases.
- [ ] **S007** Record implementation — Record real implementation and test evidence in docs/research/20261028-skill-optimization/implementation/087-receipt.json and docs/research/20261028-skill-optimization/implementation/087-outcome.md.

## Scope

In: DIRECT architecture handoff: economical file study, qualified strong design, economical implementation and mapped tests.
Out: No second plan or unrelated changes.; No installation, provider login, publishing or user-global configuration changes without permission.
Files: `skill/plan-and-execute/scripts/direct_route.py`, `skill/plan-and-execute/scripts/validatectl.py`, `skill/plan-and-execute/scripts/workload_routing.py`, `skill/plan-and-execute/references/ROUTING.md`, `skill/plan-and-execute/references/DELEGATION.md`, `skill/plan-and-execute/references/MODEL_ROUTING.md`, `skill/plan-and-execute/references/TEST_RESOURCE_MONITORING.md`, `test/optimization/direct_architecture_handoff_self_test.py`, `docs/research/20261028-skill-optimization/implementation/087-receipt.json`, `docs/research/20261028-skill-optimization/implementation/087-outcome.md`

## Guidance

- Read docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261031.md.
- Follow task 087 in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Preserve exact user intent, bounded context, security floors and real deterministic tests.
- Refresh only materially changed facts from assigned prepared reports 006, 028, 060, 062.
- Preserve evidence in docs/research/20261028-skill-optimization/implementation/087-receipt.json and docs/research/20261028-skill-optimization/implementation/087-outcome.md; do not mark a pending task done without validation.

## Acceptance

- A cohesive seven-file task stays DIRECT even when one difficult design decision needs a stronger architect.
- The inexpensive stage reads all relevant files; the architecture worker receives a precise evidence packet, not a duplicated source dump.
- The architect outputs a durable design; implementation can return to a lower qualified tier with acceptance checks.
- Stateful DIRECT validations use project resource mapping and log monitoring without creating a TODO plan.
- Compare complete validated cost (read, design, implementation, retries, reviews) to a single qualified model; preserve security floors.
- Implementation and review remain pending until actual execution evidence exists.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_087`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_087`
