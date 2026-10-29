# 064 - Economic Evaluation: research revision 2

Date: 2026-10-28. Feature: `F030`. Implementation TODO `064`; independent review TODO `065`. Product baseline: `0.11.0` / tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Prepared design evidence, not implemented code. Implementation and independent review remain pending.**

## Recommended direction

Evaluate quality-constrained cost with paired task-level experiments, versioned native usage and honest missing data; keep offline replay separate from evidence of real model performance.

This is a conditional engineering recommendation for this repository, not a proof of a global optimum or a measured saving on the user's workload.

## Change from the previous report

The revision adds the correct independent sampling unit, no-success/unknown-cost handling, failure censoring and price-version binding. Repeating deterministic fixtures no longer inflates claimed statistical evidence.

The previous report is retained under `docs/plans/20261028-skill-optimization/history/research-round-1/prepared-research/` for audit. New W-prefixed sources below are the current-round evidence; old E-prefixed sources remain background.

## Questions and repository evidence

- Measure success per validated cost, first-pass success, latency, retries and handoff overhead.
- Separate replay estimates from real-run evidence; test unknown costs and failure censoring.

**Baseline observations:**
- routing_telemetry whitelists fields and represents absent usage as null. Its inspected _number helper rejects negative/non-numeric values but does not explicitly reject positive infinity.
- The benchmark replays a fixed corpus and can repeat its records. Deterministic repetitions are not independent new real-world samples.
- Existing routing evaluation has separate acceptance gates and shadow/candidate concepts; preserve them rather than enabling learned selection from one synthetic success.

All listed file hashes matched the preserved 0.11.0 source in this revision. This is integrity checking, not a second full code audit.

| Code anchor | SHA-256 | Selected symbols / location |
|---|---|---|
| `skill/plan-and-execute/scripts/routing_telemetry.py` | `a7d8cb8b3190a3a0177f2854fd1340abbbca6a253176eaaff6d692f365dc753a` | _number:35; extract_usage:70; rollup:178 |
| `tools/routing_eval.py` | `01c496f4284a60435b554e42ec1ec32ad11d55e47d993b4fe1184bd3d0a47469` | PredeclarationError:54; _scripts:58; canonical_digest:66; _load:71 |
| `tools/skill_benchmark.py` | `d08520def6551a6db6db8194270c9cb55ca84832c87da95dd639c3af9d3f7c8b` | run_corpus:118; metrics:181; gate_segment:238 |

## Deeper analysis and competing approaches

### 1. Design analysis

The target is not the smallest token count. Predeclare a quality floor, security invariants, material cost gain and acceptable latency before looking at results. Compare baseline, deterministic optimization, lower effort, selective delegation and switching on the same held-out tasks. Separate task strata so average improvement cannot hide security or frontend regressions.

### 2. Design analysis

Repeated attempts on one task are correlated. Use paired resampling at the independent task/repository level and report unique tasks, attempts and runs separately. Replaying one deterministic scenario many times proves reproducibility, not a larger empirical sample. Keep route-training or calibration data disjoint from evaluation tasks.

### 3. Design analysis

Count all root, worker, retry, diagnosis, summary and coordination costs, including failures and timeouts. Missing usage or an unobservable provider bill remains unknown. Reject NaN, infinity, negative usage and incompatible currency/unit aggregation. With no validated results, cost per validated result is undefined or explicitly unbounded, never zero.

### 4. Design analysis

Billed and consumed tokens, cache writes/reads, plan credits and cash require separate fields and dated price evidence. Vendor APIs and CLIs may report different units. Compare observed invoice-compatible cost where available; clearly label modeled scenarios and do not claim that an offline routing replay measured real model intelligence or savings.

The analysis above is a repository design synthesis. The linked publications establish capabilities or bounded empirical observations, not this skill's future measured performance. Exact account behavior and installed-version compatibility remain implementation-time checks.

| Alternative | Benefit | Cost / failure risk | Disposition |
|---|---|---|---|
| Token count alone | Easy metric | Can reward poor quality and hidden retries | Reject |
| Average success/cost without pairing | Compact report | Confounding and false precision | Reject for acceptance |
| Paired held-out quality-constrained evaluation | Decision-relevant and auditable | Needs representative data and uncertainty | Recommended |
| Online learning immediately | Adaptive policy | Exploration spend and unsafe regressions | Shadow/offline calibration first |

## Ownership and scope boundary

This implementation owns its declared write scope and acceptance tests. Its following review checks the actual changed code; prepared research is not acceptance evidence.

Implementation may preserve an already-satisfied invariant with a regression test and a documented no-change rationale; do not add code solely to make every recommendation produce a diff.

## Implementation instructions

1. Reject NaN/infinite usage, latency and prices at all ingestion/aggregation seams; serialize strict JSON and retain unknown as null, not zero.
2. Attribute costs by actual backend/profile, worker kind and attempt. Include failed attempts, reviewers, handoffs and advisory calls in the denominator calculation.
3. Report unique tasks/cases separately from replay repetitions and real authenticated attempts. Do not use repeated identical fixture rows to narrow confidence intervals as though new evidence existed.
4. Predeclare acceptance, regression margins, workload strata, warm/cold cache conditions and abort criteria before collecting candidate results.
5. Enable automatic selection only after representative held-out outcome evaluation. Keep shadow evaluation and deterministic fallback available on sparse or stale evidence.
6. Resample by unique task or repository cluster and preserve pairing; repeated fixture replay cannot increase empirical sample size.
7. Predeclare quality/cost/latency gates and count failed, timed-out and auxiliary calls without favorable censoring.
8. Version billing units and reject non-finite usage; unknown cost and zero-success ratios cannot become apparent savings.

## Acceptance and counterexamples

- Non-finite numbers cannot produce a successful numeric rollup or invalid JSON.
- Missing cost remains unknown and is not silently compared as free.
- Failed attempts and diagnostic/handoff costs are included in cost per validated result.
- Repeating a fixed corpus changes replay count but not the claimed independent sample count.
- A candidate with lower apparent cost but worse critical acceptance cannot pass the quality gate.
- Duplicating deterministic replay rows does not narrow empirical confidence intervals.
- NaN, infinity and negative usage are rejected; missing values remain null.
- A zero-success arm cannot report zero cost per validated result.
- Cold/warm cache and subscription/API modes remain distinct in rollups.

## Cost, latency and quality decision

Report total cash, credits, tokens, latency and validated success with paired intervals; minimize cost only among policies meeting the predeclared quality and safety constraints.

Compare total cost per independently validated outcome against the current implementation and a simpler qualified single-worker baseline. Count failed attempts, reviews, cache writes/reads, advisory calls and tool/runtime overhead in their native units. Unknown prices, quotas or usage remain unknown, not zero. Preserve capability and security floors; no automatic rollout follows from fixture replay alone.

## Evidence used in this revision

- [W-COST] Anthropic, [Optimizing for cost and intelligence](https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence). Accessed 2026-10-28. Reading scope: Cost/context/delegation sections and coding measurement footnote inspected, including sample, hidden-test grading and paired intervals. Results are vendor-specific, not measured for this repository. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-BOOTSTRAP] SciPy, [Bootstrap confidence intervals](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-OTEL] OpenTelemetry, [GenAI token metrics](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-token-metrics.md). Accessed 2026-10-28. Reading scope: Official semantic-convention token metric definitions inspected; conventions are evolving and no SDK dependency is prescribed. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-OPENAI-CACHE] OpenAI, [Prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-CLAUDE-CACHE] Anthropic, [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-ROUTELLM] Ong et al. / ICLR, [RouteLLM: Learning to Route LLMs with Preference Data](https://arxiv.org/abs/2406.18665). Accessed 2026-10-28. Reading scope: Research abstract and version metadata inspected; benchmark percentages are not transferred to this codebase. Public source reading is not an independent code review or reproduction of vendor experiments.

Prior-round context: [E012], [E013], [E014], [E053], [E005]. See `SOURCE_REGISTER.md` for records; these were not all independently refreshed.

Search themes inspected in this round: Anthropic cost intelligence paired coding experiments bootstrap tasks; SciPy bootstrap paired confidence interval; OpenTelemetry GenAI cache write input output token metrics; RouteLLM query distribution.

## Unverified limits and refresh triggers

- No new paid model benchmark was performed. Literature improvements are not transferable percentages and current account pricing was not measured.
- No paid comparative model evaluation was conducted. Public vendor experiments motivate the evaluation design but do not establish this repository benefit.

No authenticated provider invocation, live quota/cost benchmark, independent model review, or Windows runtime test was performed in this research revision.

Refresh only evidence contradicted by the installed CLI, selected account/billing plan or changed code contract. Unknown required capability blocks that candidate; it does not justify widening permissions.
