---
task_id: "106"
status: "pending"
requirements: "R055"
dependencies: "105"
allowed_related_task_reads: "none"
---

# 106 — Independently review current model catalog, six-tier compatibility, cost and frontier routing

Objective: Independently review current model catalog, six-tier compatibility, cost and frontier routing.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Checkpoints

- [ ] **S001** Read task 105 actual diff, receipts, source hashes, official vendor evidence; do not trust proposed model IDs without installed CLI check.
- [ ] **S002** Use genuinely independent maximal qualified model reviewer; audit all providers, catalog freshness, tier monotonicity, six levels, subscription budgets and previous compatibility.
- [ ] **S003** Correct invalid IDs, unsupported effort flags, default frontier promotions, cost-accounting errors and any critical/high findings; rerun tests and record genuine independent review.

## Scope

Files: `skill/plan-and-execute/scripts/routingctl.py`, `skill/plan-and-execute/scripts/model_catalog.py`, `skill/plan-and-execute/scripts/model_catalogctl.py`, `skill/plan-and-execute/scripts/workload_routing.py`, `skill/plan-and-execute/scripts/routing_config.py`, `skill/plan-and-execute/scripts/availability.py`, `skill/plan-and-execute/references/MODEL_ROUTING.md`, `skill/plan-and-execute/references/MODEL_MAPPING.md`, `skill/plan-and-execute/references/MODEL_CATALOG.md`, `skill/plan-and-execute/references/ROUTING_CONFIG.md`, `skill/plan-and-execute/references/PLAN_SPEC.md`, `test/optimization/frontier_model_tier_self_test.py`.

In: Independently review current model catalog, six-tier compatibility, cost and frontier routing within one existing implementation plan.

Out: No additional plan, unauthorized provider execution, global host power modifications, parallel competing supervisor or publishing.

## Guidance

- Read `docs/research/20261028-skill-optimization/prepared-research/105-frontier-model-routing-20261112.md` and `docs/plans/20261028-skill-optimization/TASK_INPUTS.json` before work.
- Preserve existing artifacts/checkpoints and only modify declared scope, with actual tests and real independent reviewer on review tasks.
- Record actual receipts under `docs/research/20261028-skill-optimization/implementation/106-receipt.json` and outcomes under `docs/research/20261028-skill-optimization/implementation/106-outcome.md`.

## Acceptance

- Real independent review and source hashes captured; unresolved critical/high issues block integration.
- Legacy L1–L5 routes and old persisted configuration stable; L6 enabled paths select only exact observed compatible models.
- Fable 5.2, Astra and Carbon considered as eligible conditional candidates without inventing unavailable Antigravity variants.
- No unapproved paid API fallback or model tier escalation on environment, timeout, quota or weak evidence.
- Cross-provider eval and current-date sources documented with cost/uncertainty, full regressions passing.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_106`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_106`
