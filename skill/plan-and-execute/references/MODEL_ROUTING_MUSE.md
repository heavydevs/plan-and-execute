# Muse Code / Muse Spark model routing

Read only when the Muse daily cache is missing/stale/invalid, or when Muse Code will execute the current task. `PORTABLE_MODEL_ROUTING.md` owns F/L semantics and the cache-first rule.

## Dynamic discovery after a cache miss

Muse Spark and Muse Code evolve quickly, so do not preserve a concrete Muse Spark version or reasoning ladder as a durable skill constant. Before live discovery, run `model_compatctl.py cache-status --provider muse`. If today's cache is fresh, reuse it for the rest of the local calendar day.

Only when Muse's cache needs rebuilding:

1. inspect `muse --version`, `muse --help`, and `muse exec --help` on the executing environment when available;
2. identify the currently available Muse Spark model ids/aliases and reasoning levels;
3. verify uncertain or gated behavior against current Meta/Muse documentation;
4. map F1-F4/L1-L5, write the provider-only result to Muse's daily cache, and use it for the plan snapshot.

Map F1-F4 by actual current capability. Reusing the same Muse Spark model across multiple F families is valid when reasoning level or execution strategy is the practical differentiator.

## L levels

Muse Code exposes provider-specific reasoning-effort names. Map L1-L5 to five increasing effective positions selected from the currently supported ladder. If the CLI advertises a level that the backend gates, downgrades, or rejects, record the effective supported level instead. Never assume a remembered Muse effort list is still valid.

## Headless adapter

The isolated runner supports Muse through `muse exec --json`, passes the compatibility-selected `--model`, and passes `--reasoning-effort` when the binding resolves a concrete native effort. Worker execution uses unattended approval mode from `orchestrator.config.json`; summary execution disables writes.

Muse JSON/JSONL output uses the runner's generic nested-report parser, so the same completion-report schema remains valid across providers.

## Execution

A Muse model retirement, feature gate, or rejected effort level means rebuild Muse's daily compatibility cache. It does not change the TODO graph or its F/L requirement. Provider/quota failure may resolve the same F/L through Codex, Claude, Gemini, or Qwen after checking that provider's independent daily cache.
