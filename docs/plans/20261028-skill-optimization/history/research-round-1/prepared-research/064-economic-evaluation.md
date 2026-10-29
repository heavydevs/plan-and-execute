# F030 / task 064 - Telemetry, shadow routing and non-inferiority benchmarks

Date: 2026-10-28. Product baseline: 0.11.0, tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Research prepared; implementation pending; independent review pending.** This report is an implementation input, not a completion receipt. No external reviewer is impersonated.

## Decision and scope

**Recommendation (engineering inference):** Strengthen telemetry and evaluation so savings mean lower total cost per validated outcome, not prettier replay statistics.

## Questions addressed

- Measure success per validated cost, first-pass success, latency, retries and handoff overhead.
- Separate replay estimates from real-run evidence; test unknown costs and failure censoring.

## Repository evidence

The following are static-code observations against the pinned baseline, not results from authenticated providers:

- routing_telemetry whitelists fields and represents absent usage as null. Its inspected _number helper rejects negative/non-numeric values but does not explicitly reject positive infinity.
- The benchmark replays a fixed corpus and can repeat its records. Deterministic repetitions are not independent new real-world samples.
- Existing routing evaluation has separate acceptance gates and shadow/candidate concepts; preserve them rather than enabling learned selection from one synthetic success.

### Read targets and integrity

- `skill/plan-and-execute/scripts/routing_telemetry.py` (SHA-256 `a7d8cb8b3190a3a0177f2854fd1340abbbca6a253176eaaff6d692f365dc753a`): `_number` L35-38; `extract_usage` L70-92; `rollup` L178-202
- `tools/routing_eval.py` (SHA-256 `01c496f4284a60435b554e42ec1ec32ad11d55e47d993b4fe1184bd3d0a47469`): `PredeclarationError` L54-55; `_scripts` L58-63; `canonical_digest` L66-68; `_load` L71-77
- `tools/skill_benchmark.py` (SHA-256 `d08520def6551a6db6db8194270c9cb55ca84832c87da95dd639c3af9d3f7c8b`): `run_corpus` L118-135; `metrics` L181-209; `gate_segment` L238-291

## External basis

- [E012] [FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance](https://arxiv.org/abs/2305.05176) - Chen, Zaharia and Zou / arXiv; accessed 2026-10-28.
- [E013] [RouteLLM: Learning to Route LLMs from Preference Data](https://arxiv.org/abs/2406.18665) - Ong et al. / arXiv; accessed 2026-10-28.
- [E014] [AutoMix: Automatically Mixing Language Models](https://arxiv.org/abs/2310.12963) - Aggarwal et al. / arXiv; accessed 2026-10-28.
- [E053] [Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices) - OpenAI; accessed 2026-10-28.
- [E005] [Evaluating skills](https://developers.openai.com/blog/eval-skills) - OpenAI; accessed 2026-10-28.

Consult only these entries in `SOURCE_REGISTER.md` for the checked finding and scope. Provider documentation establishes an interface, not this account's available quota or a universal ranking of model quality. The proposed design below combines that evidence with the repository observations; it is not a vendor guarantee.

## Alternatives and cost/quality tradeoffs

| Disposition | Approach | Tradeoff |
|---|---|---|
| current_baseline | Optimize input tokens or synthetic pass rate alone | Simple but ignores retries, reviewer cost and weak validation. |
| recommended | Native-unit complete accounting and unique-case evaluation | Makes the economic claim falsifiable without forcing a universal price model. |
| rejected | Train and enable a learned router immediately | Sparse workload evidence can under-route important tasks while looking economical. |

## Implementation instructions

1. Reject NaN/infinite usage, latency and prices at all ingestion/aggregation seams; serialize strict JSON and retain unknown as null, not zero.
2. Attribute costs by actual backend/profile, worker kind and attempt. Include failed attempts, reviewers, handoffs and advisory calls in the denominator calculation.
3. Report unique tasks/cases separately from replay repetitions and real authenticated attempts. Do not use repeated identical fixture rows to narrow confidence intervals as though new evidence existed.
4. Predeclare acceptance, regression margins, workload strata, warm/cold cache conditions and abort criteria before collecting candidate results.
5. Enable automatic selection only after representative held-out outcome evaluation. Keep shadow evaluation and deterministic fallback available on sparse or stale evidence.

## Acceptance tests to implement and run

- [ ] Non-finite numbers cannot produce a successful numeric rollup or invalid JSON.
- [ ] Missing cost remains unknown and is not silently compared as free.
- [ ] Failed attempts and diagnostic/handoff costs are included in cost per validated result.
- [ ] Repeating a fixed corpus changes replay count but not the claimed independent sample count.
- [ ] A candidate with lower apparent cost but worse critical acceptance cannot pass the quality gate.

These cases are proposed test obligations. A research report or a fake-provider fixture cannot establish production model performance. Record executed commands, exit codes, source state and logs in the task's implementation receipt.

## Economic evaluation

Use total observed cost divided by validated outcomes, with separate API cash, credits and unpriced usage. Report latency and quality alongside cost; replay estimates are explicitly not live savings.

## Rollout and compatibility

Use the existing small deterministic helpers and compose through `run_concise.py` where applicable. Preserve disabled-mode behavior, persisted schema compatibility and locally edited installed copies. Add a behavior-changing policy only behind an explicit tested option. Do not add a framework, a paid model call or a global setting merely to satisfy this report. If current code already satisfies a proposed invariant, keep it and add the missing regression evidence instead of duplicating the mechanism.

## Limits and unresolved verification

- No new paid model benchmark was performed. Literature improvements are not transferable percentages and current account pricing was not measured.
- No paid model benchmark, Windows live execution or independent maximum-model code review was performed during this research. Those are distinct future acceptance activities where applicable.

## Task handoff

Task **064** now implements this recommendation; task **065** reviews the resulting code and requires corrections before acceptance. Read this report, its JSON decision record and only the assigned source paths. Do not repeat broad research unless a material version mismatch invalidates a specific finding. No second plan is required.
