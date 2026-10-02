# Muse Code model routing

Read only when Muse Code will execute the current work. `MODEL_ROUTING.md` owns provider-independent policy; `MODEL_CATALOG.md` owns the catalog schema.

## Status and evidence

Muse is an optional native provider (`harness: native`, adapter `muse`). It is never in the default `provider_order`: an environment without Muse configured, installed and available gets no Muse candidate and no behavior change. Bootstrap data is dated evidence, not placement. The model id, tier and effort vocabulary below come from the portable-routing request (PR #17 scope: `docs/requests/portable-model-routing-dynamic-provider-catalog.md` s2.4, s12, s78) and have **not** been verified against an installed `muse` CLI; refresh the catalog from the CLI before relying on them.

## Catalog mapping

Concrete ids live in the bootstrap catalog (`scripts/model_catalog.py`, current `catalog_version`), and `provider_config_mapping("muse")` derives the provider's `models`, `max_effort_by_tier` and `models_without_effort` from it. This table must match it.

| Tier | Model | Starting effort | Effort cap |
|---|---|---|---|
| `advanced` | `muse-spark-1.3` | `medium` | `high` |

Muse serves only `advanced`; every other tier is empty for it. An empty tier is skipped upward and never filled by invention or downgraded below the floor, so a `standard` floor reaches Muse at `advanced` and a `strong` floor has no Muse candidate. A model that the catalog marks `accepts_effort: false` gets no `--reasoning-effort` flag. Efforts above the cap are clamped (`xhigh`/`max` become `high`). `Muse Spark 1.3` is a release, not an eternal default: treat it as updatable catalog data.

Muse is a candidate for `advanced` work only when it is configured and a local eval confirms non-inferiority; it does not replace the standard or strong routes globally.

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
