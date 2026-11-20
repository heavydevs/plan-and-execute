---
task_id: "119"
status: "pending"
requirements: "R064"
dependencies: "015,029,065,090,098,112,116,118,114"
allowed_related_task_reads: "none"
---

# 119 — Enforce economical phase routing and minimal source-bound task context

Objective: Create deterministic context packet selected by phase, expected paths, actual source hashes and dependency receipts; add reason and size.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Inspect assigned architecture and relevant source symbols — Inspect assigned architecture and relevant source symbols using only task-specific research, current code and current acceptance evidence.
- [ ] **S002** Implement bounded contract without duplicate framework — Implement bounded contract without duplicate framework using only task-specific research, current code and current acceptance evidence.
- [ ] **S003** Integrate monitoring, permissions and route — Integrate monitoring, permissions and route using only task-specific research, current code and current acceptance evidence.
- [ ] **S004** Execute adversarial focused validation — Execute adversarial focused validation using only task-specific research, current code and current acceptance evidence.
- [ ] **S005** Record real product evidence or stay pending — Record real product evidence or stay pending using only task-specific research, current code and current acceptance evidence.

## Scope

In: Enforce economical phase routing and minimal source-bound task context
Out: No second orchestrator, unrelated legacy test edits, runtime implementation in this planning amendment or paid model polling.
Files: `skill/plan-and-execute/scripts/routingctl.py`, `skill/plan-and-execute/scripts/planctl.py`, `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/runner_contract.py`, `skill/plan-and-execute/scripts/task_context_router.py`, `skill/plan-and-execute/references/TASK_CONTEXT_ROUTING.md`, `test/optimization/route_aware_context_self_test.py`, `docs/research/20261028-skill-optimization/implementation/119-receipt.json`, `docs/research/20261028-skill-optimization/implementation/119-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/119-task-wide-lazy-routing.md only for this task; architecture and negative cases are mandatory.
- Create deterministic context packet selected by phase, expected paths, actual source hashes and dependency receipts; add reason and size.
- Enforce economy tool first, qualified model/effort floors, provider preference/data permissions and max independent review; reuse routingctl.
- Load only assigned research and references; avoid unrelated tasks, raw logs and full history; support targeted symbol reads.
- Stable short caching prefix only when provider supports it and actual cost/quality are measured; report unknown billing honestly.
- Gate every manifest task (currently 130) plus future ones, never hard-coding a count; stale evidence, unsafe scope, secrets and unknown dependency broaden with justification.
- Use per-phase economic routing and indexed source scope; preserve capability floors and independent reviews.
- Produce actual receipt/outcome only after code, mapped checks and real review; no fabricated success.

## Acceptance

- Verified: Create deterministic context packet selected by phase, expected paths, actual source hashes and dependency receipts; add reason and size.
- Verified: Enforce economy tool first, qualified model/effort floors, provider preference/data permissions and max independent review; reuse routingctl.
- Verified: Load only assigned research and references; avoid unrelated tasks, raw logs and full history; support targeted symbol reads.
- Verified: Stable short caching prefix only when provider supports it and actual cost/quality are measured; report unknown billing honestly.
- Actual source-bound tests, negative fixtures and compact cost evidence establish behavior without inventing savings.
- No unauthorized provider/legacy test edits, leaked secrets, duplicate scheduler or lost global validation gate.
- Negative case: the context packet never selects the frontier tier or overrides the phase provider chain; routingctl stays the only route source.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_119`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_119`
