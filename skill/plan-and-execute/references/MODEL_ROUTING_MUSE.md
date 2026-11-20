# Muse Code model routing

Read only when Muse Code will execute the current work. `MODEL_ROUTING.md` owns provider-independent policy; `MODEL_CATALOG.md` owns the catalog schema.

## Status and evidence

Muse is an optional native provider (`harness: native`, adapter `muse`). It is never in the default `provider_order`: an environment without Muse configured, installed and available gets no Muse candidate and no behavior change. Bootstrap data is dated evidence, not placement. Model ids, prices and the effort vocabulary were re-verified on 2026-11-20 against Meta's developer docs (dev.meta.ai: muse-code, reasoning, pricing; `docs/research/model-refresh-20261120/other-providers.md`), not against an installed `muse` CLI. Muse Code (headless `muse exec`) defaults to `muse-spark-1.2`, so the runner always passes `--model`. Effort values are `minimal`..`max` (`none` returns HTTP 400); `xhigh` is not documented, so the catalog maps it to `max`, but the runner passes logical efforts through — do not pin `xhigh` on a Muse route.

## Catalog mapping

Concrete ids live in the bootstrap catalog (`scripts/model_catalog.py`, current `catalog_version`), and `provider_config_mapping("muse")` derives the provider's `models`, `max_effort_by_tier` and `models_without_effort` from it. This table must match it.

| Tier | Model | Starting effort | Effort cap |
|---|---|---|---|
| `economy` | `muse-ember-1.0` | `low` | `max` |
| `standard` | `muse-spark-1.3` | `medium` | `max` |
| `advanced` | `muse-wonder-1.0` (preview) | `medium` | `max` |

Evidence (Artificial Analysis Intelligence Index v5.0.1, list prices per 1M in / cached / out): Ember 36 at about $0.14/task ($0.10 / $0.004 / $0.50; $0.30 / $0.012 / $1.50 above 200K prompt tokens); Spark 1.3 37 at $2.39 ($1.25 / $0.15 / $4.25), deprecated by AA in favour of Wonder, so it moved from `advanced` to `standard`; Wonder 44 at $6.95 ($4 / $0.20 / $20; Wonder Full only on the Power/Maximum plans per a secondary source). `muse-spark-1.3-contributor` (prompts used for training) is never routed. `strong` and `max` have no Muse candidate. A model that the catalog marks `accepts_effort: false` gets no `--reasoning-effort` flag. Efforts above a configured cap are clamped. Model names are releases, not eternal defaults: treat them as updatable catalog data.

Muse is a candidate only when it is configured and a local eval confirms non-inferiority; it does not replace the standard or strong routes globally.

## Worker argv

```text
muse exec --json [--trust-workspace] [--disable-approval] [--model <id>] [--reasoning-effort <effort>] [extra_args...] <prompt>
```

Permission flags are opt-in provider config keys, both default `false`, and must be booleans (a string such as `"false"` is rejected, never treated as true):

| Config key | Flag | Mirrors |
|---|---|---|
| `muse.trust_workspace` | `--trust-workspace` | codex `sandbox`, antigravity `skip_permissions` |
| `muse.disable_approval` | `--disable-approval` | claude `permission_mode` |

With the defaults, argv contains neither flag. Enable them only when the worker must write and Muse's own protections would otherwise block it.

## Summary argv (read-only)

```text
muse exec --json --disable-write [--model <id>] [--reasoning-effort <effort>] [extra_args...] <prompt>
```

The summary always passes `--disable-write` and never the worker opt-in flags, regardless of config. It fails closed before spawning when read-only mode cannot be proven: `extra_args` containing `--trust-workspace` or `--disable-approval`, a malformed `extra_args`, or a command without `--disable-write`. The final-summary step then writes the deterministic summary instead of spawning Muse.

## Output envelope

Muse prints a JSON object or JSONL events. A worker's completion report is found by the shared defensive extractor: the report object, or a JSON string inside `result`/`message`/`content`, a fenced block, or any event of a JSONL stream. The summary reads the last event carrying one of `result`, `response`, `final_message`, `final_output`, `answer`, `text`, `message`, `content` or `output`; bookkeeping events such as usage or init are ignored. No parsable text means the deterministic summary is used.

## Credentials

Muse reads its own credentials. A profile may name environment variables by name only (`PROFILE` rules in `ROUTING_CONFIG.md`); secret values never appear in config, argv, catalog, snapshots, logs or reports.
