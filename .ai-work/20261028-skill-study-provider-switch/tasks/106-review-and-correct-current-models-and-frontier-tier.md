---
task_id: "106"
status: "pending"
requirements: "R055"
dependencies: "105"
allowed_related_task_reads: "none"
---

# 106 — Review and correct updated model catalog and frontier routing

Objective: Review and correct updated model catalog and frontier routing

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read the 105 diff and evidence — Read task 105 actual diff, receipts, source hashes and official vendor evidence; do not trust proposed model IDs without an installed CLI check.
- [ ] **S002** Run an independent max-qualified review — Run `python docs/plans/20261028-skill-optimization/support/review_dispatch.py --repo-root . --task 106` in the foreground (rerun on exit 75); use only its DISPATCH line and compact findings. Focus: providers, catalog freshness, tier monotonicity, frontier gate, budgets.
- [ ] **S003** Correct findings and rerun — Correct invalid IDs, unsupported effort flags, default frontier promotions, cost-accounting errors and any critical/high findings; rerun tests and record genuine independent review.

## Scope

In: Review and correct updated model catalog and frontier routing
Out: No second plan, OS policy changes or unauthorised provider charges
Files: `skill/plan-and-execute/scripts/routingctl.py`, `skill/plan-and-execute/scripts/model_catalog.py`, `skill/plan-and-execute/scripts/model_catalogctl.py`, `skill/plan-and-execute/scripts/workload_routing.py`, `skill/plan-and-execute/scripts/routing_config.py`, `skill/plan-and-execute/scripts/availability.py`, `skill/plan-and-execute/references/MODEL_ROUTING.md`, `skill/plan-and-execute/references/MODEL_MAPPING.md`, `skill/plan-and-execute/references/MODEL_CATALOG.md`, `skill/plan-and-execute/references/ROUTING_CONFIG.md`, `skill/plan-and-execute/references/PLAN_SPEC.md`, `test/optimization/frontier_model_tier_self_test.py`, `skill/plan-and-execute/references/MODEL_ROUTING_CLAUDE.md`, `skill/plan-and-execute/references/MODEL_ROUTING_CODEX.md`, `skill/plan-and-execute/scripts/run_isolated.py`, `docs/research/20261028-skill-optimization/implementation/106-receipt.json`, `docs/research/20261028-skill-optimization/implementation/106-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/105-frontier-model-routing-20261112.md
- Follow tasks/106-review-and-correct-current-models-and-frontier-tier.md and TASK_INPUTS.json
- Review only via review_dispatch.py (synchronous; max route; writes dispatch evidence); fix blocking findings, rerun declared checks, re-dispatch if a reviewed file changed, copy its RECEIPT_REVIEWER fields into the receipt.
- Record actual receipts and outcomes, leave pending until verified.
- Never launch background or asynchronous agents or processes: this headless session ends when you stop calling tools, so anything unfinished is lost.

## Acceptance

- Real independent review and source hashes captured; unresolved critical/high issues block integration.
- The 105 diff is verified against the pinned refresh baseline hash; files outside the 105 scope are unchanged.
- Every S003/S005 negative case is re-run: lift, ladder, selector, stagnation floor, planctl tiers, quota, implementation role, and Codex credit exhaustion -> Fable with no escalation.
- Legacy L1–L5 routes and old persisted configuration stable; L6 enabled paths select only exact observed compatible models.
- No unapproved paid API fallback or model tier escalation on environment, timeout, quota or weak evidence.
- A frontier (Fable 5.2 / Astra 6.2) reviewer is accepted only with recorded repeated max-review failure; a reused review session or dispatch is rejected.
- Every 2026-11-20 acceptance addition of task 105 has actual test evidence on the final reviewed hashes.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_106`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_106`
