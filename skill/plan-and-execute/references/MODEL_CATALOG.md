# Model catalog contract

`scripts/model_catalog.py` validates, ages and fingerprints provider-scoped model catalogs. A catalog is evidence, not placement: it never fetches data, never invents a model for an empty tier and never chooses a route. TODO and route fields keep only provider, canonical tier and effort; concrete model ids resolve at attempt time.

## Schema (`schema_version` 1)

```json
{
  "schema_version": 1,
  "catalog_version": "2026-10-01-bootstrap-v1",
  "providers": {
    "<provider>": {
      "models": {
        "<model id>": {
          "tiers": ["strong"],
          "capability": {"available": true, "capabilities": ["code"], "accepts_effort": true,
                         "max_effort": "max", "observed_at": "<ISO-8601 with zone>", "evidence": {"source": "provider_cli", "ref": "..."}},
          "economics": {"currency": "USD", "input_per_mtok": 3.0, "output_per_mtok": 15.0, "observed_at": "...", "evidence": {"source": "provider_docs"}},
          "quality": {"rank": 4, "score": null, "observed_at": "...", "evidence": {"source": "benchmark"}}
        }
      }
    }
  }
}
```

Rules (violations raise `CatalogError` with one `(field path, message)` per problem, e.g. `$.providers.claude.models.haiku.economics.input_per_mtok`):

- `tiers`: non-empty, unique, canonical only — `economy`, `standard`, `advanced`, `strong`, `max`. F1-F5/L1-L5 aliases and case variants are input-only and rejected here.
- `capability.capabilities`: unique names from `code`, `reasoning`, `tool_use`, `long_context`, `vision`. `max_effort` is null or one of `low|medium|high|xhigh|max`. Optional `effort_map` maps every skill effort to the provider's native value; optional `thinking` declares the thinking mode.
- `economics`: `currency` is `USD`; prices per million tokens are non-negative numbers or `null` (unknown); unpublished prices stay `null`, not guesses. Optional: `cached_input_per_mtok`, `plan_credits` (credit multipliers, divisor and off-peak factor; see `MODEL_ROUTING_GLM.md`) and `off_peak` (rates plus a daily `window_utc`; see `MODEL_ROUTING_DEEPSEEK.md`).
- `quality`: `rank` is null or 1-5; `score` is null or in [0, 1].
- Every facet requires `observed_at` (timezone-aware) and `evidence.source` from `bootstrap`, `provider_cli`, `provider_api`, `provider_docs`, `benchmark`, `user`; `evidence.ref` is an optional string.
- Unknown fields are rejected at every level.

## Freshness policy (`2026-10-01-v1`)

Each facet ages independently. With age = now − `observed_at`: `fresh` while age ≤ warn, `warning` while age ≤ ttl, `stale` (still usable, in grace) while age ≤ ttl + grace, then `expired`. A missing or unparsable timestamp is `expired`.

| facet | ttl_days | grace_days | warn_after_days |
|---|---|---|---|
| capability | 7 | 3 | 5 |
| economics | 30 | 7 | 21 |
| quality | 30 | 14 | 21 |

Defaults are conservative: availability drifts fastest, so it ages first. `freshness_policy(overrides)` merges a per-facet config object such as `{"capability": {"grace_days": 10}}`; unknown facets/fields, negative values or `warn_after_days > ttl_days` are rejected with a `freshness.<facet>.<field>` path. The self-test pins this table.

## Digest and versioning

`digest(catalog)` is the sha256 of the validated catalog serialized with sorted keys and compact separators, so it is stable across runs, JSON round-trips and key order. Any mapping change alters the digest; such a change must also bump `catalog_version` and be recorded in provenance.

## Bootstrap

`bootstrap_catalog()` returns the embedded dated evidence (`catalog_version` in `scripts/model_catalog.py`) for `claude` (haiku, claude-sonnet-5-5, claude-opus-5-5, claude-fable-5-1), `codex` (gpt-6-luna, gpt-6.1-sol, gpt-6-astra for strong and max), and the opt-in `muse`, `glm` and `deepseek` entries described in their provider guides. The `advanced` tier is intentionally empty for Claude and Codex: an empty tier is skipped upward, never filled by invention and never downgraded below the floor.

## Shared cache and refresh controller

`scripts/model_catalogctl.py status|show|refresh|validate|snapshot [--json]` manages one cache file per provider at `<cache root>/<provider>/catalog.json`. The cache root is outside the skill tree: `%LOCALAPPDATA%\plan-and-execute\model-catalog` on Windows, `$XDG_CACHE_HOME/plan-and-execute/model-catalog` (default `~/.cache`) elsewhere, overridable with `PAE_MODEL_CATALOG_CACHE` or `--cache-dir`.

- Writes: validated record, temp file in the same directory, fsync, then atomic `os.replace`, all under the provider's exclusive `.lock` (stale after 120 s). Refreshing one provider never touches another provider's file; a crash before replace leaves the previous valid catalog readable, and orphan temp files are ignored.
- Record: `cache_version`, `provider`, `revision`, `catalog_version`, `cli_version`, `freshness_policy_version`, `written_at`, `models` (the schema above) and capped `provenance`. A tier-mapping change bumps `revision` and `catalog_version` and appends a provenance entry with the provider digest.
- Refresh decisions: a fresh cache makes zero source calls. A facet whose worst model state is `stale` or `expired` calls only that facet's source; a changed provider CLI version marks only `capability` due (`cli_version_changed`); `--force` refreshes every facet. Sources are injectable callables returning `{model id: facet}` (capability also carries `tiers`); `refresh --from-file` uses a JSON evidence file `{"models": {...}}`. A model newly listed by capability gets `null` economics/quality with an epoch timestamp, never invented values.
- Fallback: failing, missing or invalid sources are non-blocking. The result reports a stale warning and keeps the last valid cache; without a cache the bootstrap catalog is used and nothing is written. Unknown providers with no cache yield no candidate.
- `status` reports origin (`cache`/`bootstrap`/`none`) and worst per-facet state with non-blocking stale warnings; `show` prints the merged catalog and digest; `validate` exits 1 for an unusable cache file; `snapshot` emits the merged catalog with `digest` and `captured_at` (optionally `--output`).

## Plan-local snapshot (`MODEL_MATRIX.json`)

`planctl create` pins the merged catalog in `<plan>/MODEL_MATRIX.json` (authoritative) and renders `MODEL_MATRIX.md`; a catalog failure records `model_matrix_skipped` and the plan stays valid. Each task binds per-provider candidates for its floor, skipping empty tiers upward. The runner uses those bindings only with `model_resolution: "snapshot"` (default `config`: concrete ids come from provider `models`); an in-progress task keeps the model it started with.

- `status --plan` reports age; a snapshot older than `stale_after_days` (default: capability ttl) only warns, also on resume. `diff --plan` previews `would_rebase` without writing.
- `refresh --plan` re-snapshots and rebases **pending** tasks only, appending an old->new digest audit entry (last 50 kept). It never changes a floor or the manifest.
- `reclassify --plan --task --tier [--effort] --reason` is the only floor change: pending/blocked tasks, recorded as a manifest `task_reclassified` event and audit entry.
- Snapshot mode, invalid model id: the runner refreshes the provider cache and plan snapshot once, returns the task to pending without failure evidence and redispatches the same rung; a second rejection is a `plan_defect`. Resuming on a provider absent from the snapshot requires its fresh shared cache, otherwise the runner stops with refresh guidance and leaves TODOs unchanged.
- Cleanup deletes the snapshot with the plan directory; the shared cache survives.
