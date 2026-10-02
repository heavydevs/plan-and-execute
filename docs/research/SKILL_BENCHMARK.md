# Whole-skill quality/economy benchmark

Offline, reproducible benchmark for the whole plan-and-execute skill (request §82, F016, TODO 024). It replays a fixed workload corpus for the `main` and `candidate` routing arms, builds a native-unit scorecard and applies the non-inferiority gate predeclared in [`routing-eval/thresholds.json`](routing-eval/thresholds.json). It makes no provider calls and changes no defaults (HD012).

## Inputs

- **Corpus** — [`routing-eval/benchmark-corpus.json`](routing-eval/benchmark-corpus.json): 30 cases, three per category: `direct`, `orchestrated`, `large_request`, `stall_failure`, `resource_failure`, `provider_availability`, `tier_variant`, `delegation_variant`, `cache_warm`, `cache_cold`. Each case declares its segment, minimum acceptable route and, per arm, the executed route plus PAT003 attempt metadata (root, subagent, retry, diagnostic and summary kinds). The file holds no prompts, code or transcripts.
- **Thresholds** — read only from `thresholds.json`; the benchmark never redefines a margin.
- **Recorded telemetry (optional)** — `--telemetry main=PATH` / `--telemetry candidate=PATH` adds real-run `attempts.jsonl` records (PAT003 fields only; other keys are dropped). They are grouped by `task_id` into the `recorded` category of `--recorded-segment` (default `guarded`), so later live samples reuse the same aggregation.

## Metrics

All economic units stay native (tokens, credits, USD only when reported). Missing usage stays null and is never estimated.

- `validated_success_rate` — runs whose final root/retry attempt has `validation_pass=true`.
- `first_attempt_validated_success` — runs validated on the root attempt with `retry_count=0`.
- `attempts_per_validated` — attempts of every worker kind divided by validated runs.
- `cost_per_validated_result` — totals across root, subagent, retry, diagnostic and summary attempts (via `routing_telemetry.rollup`), divided by validated runs; `io_tokens` is input plus output tokens.
- `latency_p95` — nearest-rank p95 of the summed latency of each validated run.
- `floor_violations` — runs whose route is below the case minimum acceptable route.

## Gate

For each segment the benchmark evaluates `minimum_sample`, `regression_margin` (one-sided 95% Newcombe hybrid score lower bound of candidate minus main, margin 0.02 for validated success and 0.05 for first-attempt success), `under_routing_limit` and `material_gain` (≥15% reduction in `io_tokens` or credits, no other native unit or `attempts_per_validated` rising more than 5%, latency p95 rising at most 25%). The overall **verdict passes only when every segment is non-inferior**: sample, regression and under-routing checks pass, and inconclusive counts as fail. A segment is auto-route eligible only when it is non-inferior, shows a material gain and is listed in `safe_segments`.

The committed corpus runs each case twice (the `repetitions_per_case` minimum), so every segment is below 30 validated runs per arm. The verdict is therefore FAIL as inconclusive: offline fixtures cannot claim non-inferiority, and the main policy stays in place. The `delegation_variant` cases also move cost into extra subagent and summary attempts and their cache writes, which blocks the material-gain claim in `deterministic_low_blast` even though input+output tokens fall.

## Usage

```sh
python tools/skill_benchmark.py run                      # scorecard JSON on stdout
python tools/skill_benchmark.py report                   # refresh the section below
python tools/skill_benchmark.py report --check           # fail if the section is stale
python tools/skill_benchmark.py run --telemetry candidate=<plan>/telemetry/attempts.jsonl
python tools/skill_benchmark_self_test.py                # determinism, gate and report checks
```

## Scorecard

<!-- BEGIN GENERATED SCORECARD -->

- Corpus sha256: `2ede96b3501a474cdbb8f5cfc7b5dab3819121f2adc20d960a9e9c5d2e1566e4`
- Thresholds sha256: `502f0cdd0db653b950013a38474fb13867690cd5bba88bfbc1214f9699aed83c`
- Repetitions per case: 2; recorded attempts: main=0, candidate=0
- **Gate verdict: FAIL**; auto-route eligible segments: none

### Quality and economy by category

| Category | Arm | Cases | Validated rate | First-attempt | Attempts/validated | In+out tokens/validated | Cached/validated | Cache-write/validated | Latency p95 s | Floor violations |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| cache_cold | main | 6 | 1 | 1 | 1 | 21,375 | 0 | 10,000 | 112.5 | 0 |
| cache_cold | candidate | 6 | 1 | 1 | 1 | 13,750 | 0 | 7,500 | 63 | 0 |
| cache_warm | main | 6 | 1 | 1 | 1 | 19,125 | 11,250 | 625 | 97.5 | 0 |
| cache_warm | candidate | 6 | 1 | 1 | 1 | 12,375 | 7,500 | 625 | 57 | 0 |
| delegation_variant | main | 6 | 1 | 1 | 1 | 37,750 | 0 | 5,000 | 225 | 0 |
| delegation_variant | candidate | 6 | 1 | 1 | 3 | 28,000 | 0 | 10,000 | 177 | 0 |
| direct | main | 6 | 1 | 1 | 1 | 20,750 | 0 | 5,000 | 105 | 0 |
| direct | candidate | 6 | 1 | 1 | 1 | 13,125 | 0 | 5,000 | 60 | 0 |
| large_request | main | 6 | 1 | 1 | 2 | 93,625 | 0 | 15,000 | 480 | 0 |
| large_request | candidate | 6 | 1 | 1 | 2 | 83,625 | 0 | 15,000 | 465 | 0 |
| orchestrated | main | 6 | 1 | 1 | 3 | 75,750 | 0 | 10,000 | 502.5 | 0 |
| orchestrated | candidate | 6 | 1 | 1 | 3 | 75,750 | 0 | 10,000 | 502.5 | 0 |
| provider_availability | main | 6 | 1 | 0 | 2 | 32,250 | 0 | 5,000 | 217.5 | 0 |
| provider_availability | candidate | 6 | 1 | 1 | 1 | 32,250 | 0 | 5,000 | 210 | 0 |
| resource_failure | main | 6 | 1 | 0 | 3 | 49,000 | 0 | 10,000 | 300 | 0 |
| resource_failure | candidate | 6 | 1 | 0 | 3 | 49,000 | 0 | 10,000 | 300 | 0 |
| stall_failure | main | 6 | 1 | 0 | 2 | 37,375 | 0 | 10,000 | 570 | 0 |
| stall_failure | candidate | 6 | 1 | 0 | 2 | 37,375 | 0 | 10,000 | 570 | 0 |
| tier_variant | main | 6 | 1 | 1 | 1 | 31,000 | 0 | 5,000 | 195 | 0 |
| tier_variant | candidate | 6 | 1 | 1 | 1 | 25,250 | 0 | 5,000 | 165 | 0 |
| overall | main | 60 | 1 | 0.7 | 1.7 | 41,800 | 1,125 | 7,562.5 | 502.5 | 0 |
| overall | candidate | 60 | 1 | 0.8 | 1.8 | 37,050 | 750 | 7,812.5 | 502.5 | 0 |

### Cost by worker kind (overall totals)

| Arm | Kind | Attempts | Input | Cached | Cache-write | Output | Credits | USD |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | root | 60 | 1,533,750 | 67,500 | 333,750 | 231,000 | — | — |
| main | subagent | 6 | 135,000 | 0 | 30,000 | 22,500 | — | — |
| main | retry | 18 | 390,000 | 0 | 90,000 | 66,000 | — | — |
| main | diagnostic | 6 | 37,500 | 0 | 0 | 6,000 | — | — |
| main | summary | 12 | 75,000 | 0 | 0 | 11,250 | — | — |
| candidate | root | 60 | 1,372,500 | 45,000 | 348,750 | 211,500 | — | — |
| candidate | subagent | 12 | 195,000 | 0 | 60,000 | 34,500 | — | — |
| candidate | retry | 12 | 225,000 | 0 | 60,000 | 37,500 | — | — |
| candidate | diagnostic | 6 | 37,500 | 0 | 0 | 6,000 | — | — |
| candidate | summary | 18 | 90,000 | 0 | 0 | 13,500 | — | — |

### Gate by segment

| Segment | Minimum sample | Regression margin (lower bound) | Under-routing | Material gain | Safe | Non-inferior | Auto-route |
|---|---|---|---|---|---|---|---|
| deterministic_low_blast | inconclusive | fail (-0.1013) | fail (0 floor) | fail (io_tokens; shifted attempts_per_validated, cache_write_tokens) | yes | no | no |
| floor_locked | inconclusive | fail (-0.184) | fail (0 floor) | fail (none) | no | no | no |
| guarded | inconclusive | fail (-0.3108) | fail (0 floor) | pass (io_tokens) | no | no | no |
| resilience | inconclusive | fail (-0.1307) | fail (0 floor) | fail (none) | no | no | no |

<!-- END GENERATED SCORECARD -->
