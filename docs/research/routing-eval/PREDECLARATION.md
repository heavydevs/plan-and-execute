# Routing eval predeclaration

The thresholds and corpus manifest in this directory were fixed on 2026-10-01, before any routing measurement. They implement the request's rule (§82) that enabling an optimization needs predeclared quality non-inferiority plus a material economic gain, never the best post-hoc result.

| File | Canonical sha256 |
|---|---|
| `thresholds.json` | `adba035e9de779f24e92d0bb0b00b296ddcd49a7ec5fbbd0207c45d2b40757b5` |
| `corpus-manifest.json` | `e0c03274a677cf6018939cbfbe1741710c3bdf1339df8f54b4b1cc7a020186bf` |

Digests are sha256 over canonical JSON (sorted keys, compact separators, UTF-8), so line endings and whitespace do not change them. `thresholds.json` also pins the corpus manifest digest.

## Thresholds

Metric names map to PAT003 attempt-telemetry fields (`skill/plan-and-execute/scripts/routing_telemetry.py`) in native units. They are never converted to USD.

| Threshold | Value | Why it is conservative |
|---|---|---|
| `regression_margin` | candidate − main validated success ≥ −0.02 on the one-sided 95% lower bound (first-attempt: −0.05) | Common margins are 5–10 points. Checking the bound instead of the point estimate means a run with too little data fails. |
| `under_routing_limit` | 0 floor violations; attributed-failure rate ≤ 0.02 with an upper bound ≤ 0.05 | One route below the floor fails the gate whatever the savings. |
| `material_gain` | ≥ 15% lower cost per validated result in tokens or credits; no other unit or attempts up by > 5%; p95 latency up by ≤ 25% | Sits above run-to-run variance and blocks savings that only move cost into another unit. |
| `minimum_sample` | ≥ 30 validated attempts per segment per arm, ≥ 3 cases per category, ≥ 2 matched repetitions | An inconclusive result counts as a fail, so missing data keeps the main policy. |
| `safe_segments` | `deterministic_low_blast` only | Deterministic validation catches a wrong route there before it ships. |

Each candidate passes or fails per segment. It passes only when every gate passes and the segment is listed as safe. Segments `floor_locked` and `resilience` can never be listed.

## Corpus

The corpus has 13 categories: the 10 workload classes in request §62, plus the TODO-017 categories for direct versus orchestrated work, large requests, and stall or resource failures. Each category names:

- its segment;
- its floor source, `routingctl.minimum_route`, called with explicit signals; the validator recomputes this floor;
- whether it is real, synthetic or mixed.

Comparison arms cover main versus candidate, the standard/advanced/strong tier bands, root-only versus delegated, and cold versus warm cache.

## Workflow

1. `python tools/routing_eval.py validate-predeclaration` checks the schema, the guard-rail bounds, the floors, the PAT003 fields, these digests and the measurement ledger. It prints the thresholds digest.
2. Before the first measurement, run `python tools/routing_eval.py record-measurement --run-id <id>`. It appends the current digests to `measurements.jsonl`. It does not run any measurement.
3. After that, any edit to either file fails validation. `seal`, which re-pins the manifest digest, is refused. A change needs a new predeclaration directory.
