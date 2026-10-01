# Tier routing and sequential configuration

Load for exact `configure`, per-plan routing changes or availability troubleshooting; not every TODO.

## Setup without a plan

From this repository: `node bin/plan-and-execute.js configure`. Installed updated package: `pae configure`. Python-only skill: `python <skill-dir>/scripts/configure.py`.

The UI-neutral `Question` has `id`, `prompt`, `choices`. A host may render it natively; the terminal shows one numbered question at a time. An answer validates and advances only the current question. `q`, EOF or interruption cancels without saving.

The wizard discovers seven coding CLIs: Claude, Codex, Antigravity, Gemini, Qwen, Kimi and Trae. It uses only non-generative documented `claude auth status` and `codex login status` probes. Other/custom wrappers require explicit authentication confirmation. Installed, authenticated, quota available and access to a concrete model are separate facts; no token-consuming test prompt is sent.

For economy, standard, strong and max: choose a primary, then each fallback in order. Configure concrete models/caps only for chosen routes. Assistant opt-in/provider is independent. Jev and Claude are supported advisory profiles; Jev is not a coding provider. See `ASSISTANTS.md`, then load only the selected provider guide before enabling or diagnosing advice. Final preview and explicit confirmation precede an atomic, owner-only write. Concurrent edits and symlink destinations fail rather than overwrite.

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
  "assistant": {"enabled": false, "provider": "jev"}
}
```

The Jev assistant line is an opt-in example, not a default activation; without explicit enablement no Jev request occurs. These are example preferences, not model quality rankings. Provider names are not model tiers. Concrete model IDs come from provider `models`; capability caps use `max_effort_by_tier`. Verify IDs with the installed provider CLI. Antigravity IDs embedding a reasoning mode omit separate `--effort`; explicit `models_without_effort` also wins. Invalid types, repeated providers, unknown tiers or impossible combinations fail before execution.

An explicit task/CLI provider is first; declared alternatives remain subject to `allow_provider_fallback`. A pinned provider plus fallback disabled never silently switches. Existing `provider_order` behavior remains when no tier-specific chain is present.

## Availability versus difficulty

Authentication, credit/quota, capacity and missing CLI failures may try the next eligible provider on the same logical tier and requested effort. Clamp only unsupported effort against that provider's capability cap; do not translate availability into a stronger rung. Genuine mechanical/semantic/budget/plan failures keep the existing evidence-driven ladder. Cancellation, timeouts and invalid model/effort arguments are not indiscriminately rotated as quota.

`results/<task>-availability.json` persists phase-specific route intent, attempted candidates, events and provider cooldowns. Design and implementation have distinct intentions; design fallback cannot raise the implementation tier. The per-run dispatch cap bounds cycles. Exhausting all eligible routes returns a resumable pause (exit 75), not a busy retry loop; resuming during cooldown does not re-bill the same unavailable provider. Changed routing policy re-evaluates intent. It does not authorize changing the root chat model.

Pause/resume preserves partial code, completed subtasks and functional failure counts. For diagnostics inspect the latest small ledger, not prior conversations. Respect a live runner lease; never erase state just to force another attempt.
