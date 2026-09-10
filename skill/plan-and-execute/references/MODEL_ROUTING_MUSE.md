# Muse Code / Muse Spark model routing

Read only when building/refreshing the Muse compatibility row or when Muse Code will execute the current task. `PORTABLE_MODEL_ROUTING.md` owns F/L semantics.

## Dynamic discovery

Muse Spark and Muse Code are evolving quickly, so do not preserve a concrete Muse Spark version or reasoning ladder as a durable skill constant. At planning time:

1. inspect `muse --version`, `muse --help`, and `muse exec --help` on the executing environment when available;
2. identify the currently available Muse Spark model ids/aliases and reasoning levels;
3. verify uncertain or gated behavior against current Meta/Muse documentation;
4. put the concrete result only in the plan's `MODEL_COMPATIBILITY.json`.

Map F1-F4 by actual current capability. Reusing the same Muse Spark model across multiple F families is valid when reasoning level or execution strategy is the practical differentiator.

## L levels

Muse Code exposes provider-specific reasoning-effort names. Map L1-L5 to the five increasing effective levels selected from the currently supported ladder. If the CLI advertises a level that the backend gates, downgrades, or rejects, record the effective supported level instead. Never assume a remembered Muse effort list is still valid.

## Headless adapter

The isolated runner supports Muse through `muse exec --json`, passes the compatibility-selected `--model`, and passes `--reasoning-effort` when the table resolves a concrete native effort. Worker execution uses unattended approval mode from `orchestrator.config.json`; summary execution disables writes.

Muse JSON/JSONL output uses the runner's generic nested-report parser, so the same completion-report schema remains valid across providers.

## Execution

A Muse model retirement, feature gate, or rejected effort level means refresh the compatibility table. It does not change the TODO graph or its F/L requirement. Provider/quota failure may resolve the same F/L through Codex, Claude, Gemini, or Qwen.
