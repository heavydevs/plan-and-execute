# Tier routing and sequential configuration

Load for exact `configure`, per-plan routing changes or availability troubleshooting; not every TODO.

## Setup without a plan

From this repository: `node bin/plan-and-execute.js configure`. Installed updated package: `pae configure`. Python-only skill: `python <skill-dir>/scripts/configure.py`.

The UI-neutral `Question` has `id`, `prompt`, `choices`. A host may render it natively; the terminal shows one numbered question at a time. An answer validates and advances only the current question. `q`, EOF or interruption cancels without saving.

The wizard discovers seven coding CLIs: Claude, Codex, Antigravity, Gemini, Qwen, Kimi and Trae. It uses only non-generative documented `claude auth status` and `codex login status` probes. Other/custom wrappers require explicit authentication confirmation. Installed, authenticated, quota available and access to a concrete model are separate facts; no token-consuming test prompt is sent.

For each tier that has a configured model (economy, standard, advanced, strong, max): choose a primary, then each fallback in order. Configure concrete models/caps only for chosen routes. Assistant opt-in/provider is independent. Native advisory support is narrower than coding support: see `ASSISTANTS.md` before enabling it. Final preview and explicit confirmation precede an atomic, owner-only write. Concurrent edits and symlink destinations fail rather than overwrite.

```bash
pae configure --show --json
pae configure --dry-run
pae configure --plan .ai-work/<plan-id>
pae configure --config /path/to/orchestrator.config.json
```

`--show` prints only safe routing/model fields, not custom commands, extra arguments or credentials. `--dry-run` previews without saving. Do not configure global credentials here.

## Paths and precedence

Global destination: `PAE_CONFIG_PATH`, otherwise `$XDG_CONFIG_HOME/plan-and-execute/orchestrator.config.json` or `~/.config/plan-and-execute/orchestrator.config.json`; Windows uses `%APPDATA%/plan-and-execute/orchestrator.config.json`.

Runtime resolution: built-in defaults < global config < explicit plan overlay. Dictionaries merge recursively; lists replace. A per-plan `fallbacks: []` deliberately disables that tier's fallback. New plans write small version-2 overlays and inherit unspecified global fields. Legacy complete version-1 snapshots remain explicit and do not silently adopt new global routes. Inspect/migrate them deliberately with `configure --plan`; loading never rewrites user files.

```json
{
  "version": 2,
  "tier_routes": {
    "economy": {"primary": "antigravity", "fallbacks": ["claude"]},
    "standard": {"primary": "codex", "fallbacks": ["claude"]},
    "strong": {"primary": "claude", "fallbacks": ["codex"]},
    "max": {"primary": "codex", "fallbacks": ["claude"]}
  },
  "availability": {"cooldown_seconds": 300, "max_attempts_per_run": 7},
  "assistant": {"enabled": false, "provider": "antigravity"}
}
```

These are example preferences, not model quality rankings. Provider names are not model tiers. Concrete model IDs come from provider `models`; capability caps use `max_effort_by_tier`. Verify IDs with the installed provider CLI. Antigravity IDs embedding a reasoning mode omit separate `--effort`; explicit `models_without_effort` also wins. Invalid types, repeated providers, unknown tiers or impossible combinations fail before execution.

An explicit task/CLI provider is first; declared alternatives remain subject to `allow_provider_fallback`. A pinned provider plus fallback disabled never silently switches. Existing `provider_order` behavior remains when no tier-specific chain is present.

## Provider profiles and harnesses

Harness (which CLI adapter builds argv: `claude`, `codex` or `native` = the provider's own adapter) and profile (endpoint and credentials) are independent axes. A profile on a compatible API reuses an existing adapter; the provider keeps its own `models`, caps and `extra_args`.

```json
{
  "profiles": {"gateway": {"harness": "claude", "command": "claude", "base_url_env": "GW_BASE_URL", "token_env": "GW_TOKEN"}},
  "kimi": {"profile": "gateway"}
}
```

Allowed keys: `harness` (required), `command` (default: the adapter's configured command), `base_url_env`, `token_env`. Credentials are referenced only by environment-variable name; any other key, or a value that is not an env-var name, fails validation without echoing it. Values are read at spawn time and mapped to `ANTHROPIC_BASE_URL`/`ANTHROPIC_AUTH_TOKEN` (claude) or `OPENAI_BASE_URL`/`OPENAI_API_KEY` (codex); `native` only requires them to be set. A missing variable fails before spawning, naming the variable. Values never appear in config, `--show`, argv, logs or results. Providers without `profile` keep byte-identical argv. Summary adapters pin their read-only mode; an adapter without one fails closed.

## Auto-selection rollout (`routing.auto_select`)

```json
{"routing": {"auto_select": "off", "allowlist": [], "gate_dir": "docs/research/routing-eval"}}
```

- **`off` (default; also when `routing` is absent):** routes are exactly the provider ladder's.
- **`shadow`:** records the selector candidate next to each executed route in `telemetry/shadow.jsonl`. Routes do not change. This is the same as `routing_shadow: true`.
- **`on`:** also records the candidate, and executes it only when all of these hold:
  - the task's `routing_segment` is in `allowlist`;
  - that segment passes every predeclared gate;
  - it is the task's first implementation attempt (no recorded attempts or failures);
  - the candidate uses the provider the ladder already chose, and that provider has a model configured for the candidate tier.

  Effort is clamped by `max_effort_by_tier`. In every other case the ladder route runs, and the record's `auto.reason` says why: `segment_not_allowlisted`, `design_phase`, `ladder_owns_retry`, `no_candidate`, `provider_differs`, `no_configured_model` or `selector_error`. A selector or gate exception falls back the same way and is recorded. Retries always stay on the evidence ladder.

`allowlist` names corpus segment ids. It is only a request: the runner intersects it with the gate result (`routingctl.effective_allowlist`), so a segment that fails a gate is never auto-routed, even when listed. `gate_dir` (relative to the repo root) holds `thresholds.json` and the generated `SHADOW_REPORT.md`. `python scripts/routingctl.py gate --dir <gate_dir>` prints the per-segment verdicts.

A segment passes only when all of these hold:
- `minimum_sample`;
- `regression_margin`, using Newcombe lower bounds on matched runs (the first-attempt bound is derived conservatively from attempts and validated counts);
- `under_routing_limit`;
- `material_gain`, with no shift into another native unit or into attempts, and latency within the limit;
- it is listed in `safe_segments`.

Missing, unparsable or stale evidence (the report's thresholds digest differs) fails every segment. Thresholds are never tuned here. With the committed report, no segment passes, so `on` currently behaves like `shadow`.

## Concrete model resolution (`model_resolution`)

`config` (default) takes model ids from provider `models`. `snapshot` binds them from the plan's `MODEL_MATRIX.json` (`MODEL_CATALOG.md`), falling back to `models` when the snapshot has no entry; provider, tier and effort still come from the ladder. Any other value behaves as `config`.

## Availability versus difficulty

Authentication, credit/quota, capacity and missing CLI failures may try the next eligible provider on the same logical tier and requested effort. Clamp only unsupported effort against that provider's capability cap; do not translate availability into a stronger rung. Genuine mechanical/semantic/budget/plan failures keep the existing evidence-driven ladder. Cancellation, timeouts and invalid model/effort arguments are not indiscriminately rotated as quota.

`results/<task>-availability.json` persists phase-specific route intent, attempted candidates, events and provider cooldowns. Design and implementation have distinct intentions; design fallback cannot raise the implementation tier. The per-run dispatch cap bounds cycles. Exhausting all eligible routes returns a resumable pause (exit 75), not a busy retry loop; resuming during cooldown does not re-bill the same unavailable provider. Changed routing policy re-evaluates intent. It does not authorize changing the root chat model.

Pause/resume preserves partial code, completed subtasks and functional failure counts. For diagnostics inspect the latest small ledger, not prior conversations. Respect a live runner lease; never erase state just to force another attempt.
