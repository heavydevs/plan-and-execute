---
task_id: "105"
status: "pending"
requirements: "R055"
dependencies: "021,025,027,047,081"
allowed_related_task_reads: "none"
---

# 105 — Refresh every provider model mapping and add a sixth frontier capability tier above max

Objective: Refresh every provider model mapping and add a sixth frontier capability tier above max.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Checkpoints

- [ ] **S001** Read docs/research/20261028-skill-optimization/prepared-research/105-frontier-model-routing-20261112.md and original 020/024/026 studies; do not duplicate catalog machinery.
- [ ] **S002** Refresh official current models, exact installed CLI IDs and effort modes for Claude, Codex, Antigravity and every other configured provider; treat unavailable/unknown as explicit states.
- [ ] **S003** Introduce canonical frontier L6/F6 above economy, standard, advanced, strong, max; extend schema, selectors, workload matrices, escalation ladders, compatibility and docs without altering old L1–L5 task routes by default.
- [ ] **S004** Candidate examples conditioned on real availability and permissions: Claude Fable 5.2, OpenAI GPT-6 Astra, Google Antigravity Gemini 4 Carbon High; screen out access-limited Mythos and unverified IDs; evaluate Argon, Sol, Opus and other providers at proper lower tiers.
- [ ] **S005** Use isolated qualified frontier on truly extraordinary/high-risk or failed-max work, only when approved; never auto-escalate due to quota, environment, elapsed idle time or unknown rate; provider restrictions and accounting remain intact.
- [ ] **S006** Benchmark independently validated outcomes, including tokens/credits, subscription/API differentiation, actual cost, retries, latency and failures; record unknown or no live access, never invent quality rankings.
- [ ] **S007** Add schema and cross-provider regressions and bilingual model mapping, with exact evidence source dates.

## Scope

Files: `skill/plan-and-execute/scripts/routingctl.py`, `skill/plan-and-execute/scripts/model_catalog.py`, `skill/plan-and-execute/scripts/model_catalogctl.py`, `skill/plan-and-execute/scripts/workload_routing.py`, `skill/plan-and-execute/scripts/routing_config.py`, `skill/plan-and-execute/scripts/availability.py`, `skill/plan-and-execute/references/MODEL_ROUTING.md`, `skill/plan-and-execute/references/MODEL_MAPPING.md`, `skill/plan-and-execute/references/MODEL_CATALOG.md`, `skill/plan-and-execute/references/ROUTING_CONFIG.md`, `skill/plan-and-execute/references/PLAN_SPEC.md`, `test/optimization/frontier_model_tier_self_test.py`.

In: Refresh every provider model mapping and add a sixth frontier capability tier above max within one existing implementation plan.

Out: No additional plan, unauthorized provider execution, global host power modifications, parallel competing supervisor or publishing.

## Guidance

- Read `docs/research/20261028-skill-optimization/prepared-research/105-frontier-model-routing-20261112.md` and `docs/plans/20261028-skill-optimization/TASK_INPUTS.json` before work.
- Preserve existing artifacts/checkpoints and only modify declared scope, with actual tests and real independent reviewer on review tasks.
- Record actual receipts under `docs/research/20261028-skill-optimization/implementation/105-receipt.json` and outcomes under `docs/research/20261028-skill-optimization/implementation/105-outcome.md`.

## Acceptance

- All six tier names and L/F1–6 aliases validate, and legacy routing tests/argv output remain unchanged with new tier disabled.
- Current 2026-11-12 official catalog source links and exact observed CLI IDs/effort compatibility recorded; no hallucinated provider model IDs.
- Eligible Fable 5.2, Astra and Antigravity Gemini 4 Carbon can occupy frontier only when host and account actually list/authorize them; alternatives only where measured and admissible.
- No forced price conversion between API cash and subscription credits; unknown model cost is never zero.
- Frontier retries require semantic/architectural evidence or explicit opt-in and cannot bypass provider/permission/cost floors.
- Live account uncertainty and benchmark limitations explicitly reported, and independently reviewed task 106 is a mandatory integration gate.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_105`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_105`
