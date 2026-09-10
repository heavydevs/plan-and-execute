# Portable F/L model routing

Use this reference while planning an ORCHESTRATED request and whenever a provider/model mapping must be refreshed.

## Purpose

A durable plan must not depend on a concrete provider, model id, or provider-specific effort name. Every executable TODO declares only:

- `model_family`: `F1`, `F2`, `F3`, or `F4`;
- `model_level`: `L1`, `L2`, `L3`, `L4`, or `L5`.

Concrete provider/model names live only in replaceable compatibility data and actual execution-route history.

## Portable scale

| Family | Required capability |
|---|---|
| `F1` | Economy/fast model family: exploration, classification, mechanical work, cheap summaries |
| `F2` | General coding family: normal bounded implementation, debugging, tests |
| `F3` | Strong model family: subtle debugging, architecture, security, concurrency, migrations, weak verification |
| `F4` | Frontier model family: long-horizon/high-risk work or evidence-backed escalation beyond F3 |

`L` is independent from `F`. It means the reasoning/power level inside the selected concrete model.

| Level | Meaning |
|---|---|
| `L1` | Lowest supported useful reasoning level |
| `L2` | Low-to-medium reasoning |
| `L3` | Strong/high reasoning |
| `L4` | Extra-high reasoning |
| `L5` | Highest supported reasoning level |

If a provider exposes fewer than five native levels, map multiple adjacent L values to the same native level. Never invent an unsupported provider option.

## Provider-specific daily cache

Compatibility discovery is lazy and provider-scoped. Do **not** query every provider during each plan.

The shared user cache is:

```text
~/.plan-and-execute/cache/model-compatibility/
├── codex.json
├── claude.json
├── gemini.json
├── qwen.json
└── muse.json
```

Only files that have actually been needed need to exist. On Windows, `~` is the user's home directory.

A cache entry is valid for the provider's `checked_at` local calendar day. This means one live discovery per provider per day, not one discovery per plan and not one combined discovery covering every vendor.

Example:

- first Codex invocation today: `codex.json` missing/stale -> inspect Codex CLI + current OpenAI/Codex documentation, build the Codex-only mapping, cache it;
- second Codex invocation today: `codex.json` is fresh -> reuse it; do not query CLI/docs again merely because a new plan is being created;
- first Claude invocation today: `claude.json` missing/stale -> perform Claude-only discovery even if `codex.json` is already fresh;
- Gemini/Qwen/Muse follow the same independent rule.

Use the controller to check before doing external discovery:

```bash
python <skill-dir>/scripts/model_compatctl.py cache-status --provider codex --json
```

If status is `fresh`, read/reuse it:

```bash
python <skill-dir>/scripts/model_compatctl.py cache-read \
  --provider codex \
  --output /tmp/model-compatibility.json
```

If status is `missing`, `stale`, or `invalid`, inspect only that provider:

1. inspect its locally installed CLI/configuration first when available (`--version`, help/model picker/config);
2. check current authoritative provider documentation when model aliases, availability, reasoning levels, or CLI controls are not fully established locally;
3. map F1-F4 to current concrete models for that provider;
4. map L1-L5 to actual native effort controls, repeating/clamping when necessary;
5. record a current timezone-aware `checked_at` plus sources;
6. save a temporary provider-only compatibility JSON and write the cache:

```bash
python <skill-dir>/scripts/model_compatctl.py cache-write \
  --provider codex \
  --spec /tmp/model-compatibility.json \
  --json
```

Do not refresh another provider just for completeness.

## Provider-only compatibility shape

New planning flows normally carry exactly one provider: the provider currently being used. Older `fl-v1` plans containing several providers remain readable for backwards compatibility.

```json
{
  "model_compatibility": {
    "generated_at": "<ISO-8601 timestamp>",
    "discovery": "Fresh daily Codex compatibility loaded from cache, or rebuilt from current Codex CLI/docs.",
    "providers": {
      "codex": {
        "checked_at": "<ISO-8601 timestamp>",
        "sources": ["<current Codex CLI probe>", "<current official source>"],
        "families": {
          "F1": {"model": "<current id>", "levels": {"L1": "<native>", "L2": "<native>", "L3": "<native>", "L4": "<native>", "L5": "<native>"}},
          "F2": {"model": "<current id>", "levels": {"L1": "<native>", "L2": "<native>", "L3": "<native>", "L4": "<native>", "L5": "<native>"}},
          "F3": {"model": "<current id>", "levels": {"L1": "<native>", "L2": "<native>", "L3": "<native>", "L4": "<native>", "L5": "<native>"}},
          "F4": {"model": "<current id>", "levels": {"L1": "<native>", "L2": "<native>", "L3": "<native>", "L4": "<native>", "L5": "<native>"}}
        }
      }
    }
  }
}
```

Substitute `claude`, `gemini`, `qwen`, or `muse` when that is the current provider. Do not add unused provider objects.

## Plan artifacts

`MODEL_COMPATIBILITY.json` and `MODEL_COMPATIBILITY.md` are per-plan snapshots of the compatibility actually used to create/refresh that plan. A plan created under Codex therefore normally contains only the Codex mapping.

The task graph remains provider-neutral. Switching provider does not require changing any TODO's F/L.

To switch an existing plan:

1. check the new provider's daily cache;
2. if fresh, reuse it;
3. if absent/stale, perform live discovery only for that provider and cache it;
4. replace the plan snapshot without changing TODOs:

```bash
python <skill-dir>/scripts/model_compatctl.py refresh \
  --plan .ai-work/<plan-id> \
  --provider claude \
  --json
```

The runtime may also resolve a provider from its fresh user cache without embedding that provider into the TODO graph. A missing/stale cache must not silently fall back to yesterday's provider mapping.

Increase F or L only for technical/capability evidence. Provider quota/rate/capacity failure alone preserves F/L.

## Provider references

Load only the provider currently being checked:

- Codex: `MODEL_ROUTING_CODEX.md`
- Claude Code: `MODEL_ROUTING_CLAUDE.md`
- Gemini CLI: `MODEL_ROUTING_GEMINI.md`
- Qwen Code: `MODEL_ROUTING_QWEN.md`
- Muse Code / Muse Spark: `MODEL_ROUTING_MUSE.md`
