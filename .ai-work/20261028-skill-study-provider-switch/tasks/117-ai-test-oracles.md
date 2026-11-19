---
task_id: "117"
status: "pending"
requirements: "R063,R064"
dependencies: "110,112,108"
allowed_related_task_reads: "none"
---

# 117 — Implement contract-grounded AI test oracles and defect-detection checks

**Objective:** Require independent expected-outcome contract, meaningful assertions, mapped risk, source and layer for each newly created/changed test.

**Architecture:** read only [assigned study](../../../docs/research/20261028-skill-optimization/prepared-research/117-ai-test-oracle-quality.md) and actual affected source. No work is yet implemented.

## Checkpoints

- [ ] S001 — Inspect assigned architecture and relevant source symbols: Inspect assigned architecture and relevant source symbols using only task-specific research, current code and current acceptance evidence.
- [ ] S002 — Implement bounded contract without duplicate framework: Implement bounded contract without duplicate framework using only task-specific research, current code and current acceptance evidence.
- [ ] S003 — Integrate monitoring, permissions and route: Integrate monitoring, permissions and route using only task-specific research, current code and current acceptance evidence.
- [ ] S004 — Execute adversarial focused validation: Execute adversarial focused validation using only task-specific research, current code and current acceptance evidence.
- [ ] S005 — Record real product evidence or stay pending: Record real product evidence or stay pending using only task-specific research, current code and current acceptance evidence.

## Implementation and review contract

- Read docs/research/20261028-skill-optimization/prepared-research/117-ai-test-oracle-quality.md only for this task; architecture and negative cases are mandatory.
- Require independent expected-outcome contract, meaningful assertions, mapped risk, source and layer for each newly created/changed test.
- Reuse 111 impact selector and 109 failure cycle; no duplicate runner; authorize legacy edits only via 113.
- Property/parameterized tests for field/rule matrices; risk-unique E2E for browser user journeys.
- Seeded defect or bounded incremental mutation proves critical oracles detect meaningful failures; no mandatory global mutation.
- Cover 45-field form, auth positive/negative, vacuous oracle, hallucinated API, flaky fixtures and repaired bug red/green.
- Use per-phase economic routing and indexed source scope; preserve capability floors and independent reviews.
- Produce actual receipt/outcome only after code, mapped checks and real review; no fabricated success.

## Acceptance

- Verified: Require independent expected-outcome contract, meaningful assertions, mapped risk, source and layer for each newly created/changed test.
- Verified: Reuse 111 impact selector and 109 failure cycle; no duplicate runner; authorize legacy edits only via 113.
- Verified: Property/parameterized tests for field/rule matrices; risk-unique E2E for browser user journeys.
- Verified: Seeded defect or bounded incremental mutation proves critical oracles detect meaningful failures; no mandatory global mutation.
- Actual source-bound tests, negative fixtures and compact cost evidence establish behavior without inventing savings.
- No unauthorized provider/legacy test edits, leaked secrets, duplicate scheduler or lost global validation gate.

## Validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_117`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_117`

Expected files: `skill/plan-and-execute/scripts/planctl.py`, `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/runner_contract.py`, `skill/plan-and-execute/scripts/test_impact.py`, `skill/plan-and-execute/scripts/test_failure_cycle.py`, `skill/plan-and-execute/scripts/test_oracle.py`, `skill/plan-and-execute/references/TEST_AUTHORING.md`, `test/optimization/ai_test_quality_self_test.py`, `docs/research/20261028-skill-optimization/implementation/117-receipt.json`, `docs/research/20261028-skill-optimization/implementation/117-outcome.md`.

**Pending:** only architectural specifications; no executed product tests or independent review.
