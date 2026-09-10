# Portable F/L model routing

Use this reference while planning an ORCHESTRATED request and whenever a provider/model mapping must be refreshed.

## Purpose

A durable plan must not depend on a concrete provider, model id, or provider-specific effort name. Every executable TODO declares only:

- `model_family`: `F1`, `F2`, `F3`, or `F4`;
- `model_level`: `L1`, `L2`, `L3`, `L4`, or `L5`.

The planner separately creates `MODEL_COMPATIBILITY.json` and the rendered `MODEL_COMPATIBILITY.md`. Concrete provider/model names belong only in those replaceable compatibility artifacts and in actual execution-route history.

## Portable scale

| Family | Required capability |
|---|---|
| `F1` | Economy/fast model family: exploration, classification, mechanical work, cheap summaries |
| `F2` | General coding family: normal bounded implementation, debugging, tests |
| `F3` | Strong model family: subtle debugging, architecture, security, concurrency, migrations, weak verification |
| `F4` | Frontier model family: long-horizon/high-risk work or evidence-backed escalation beyond F3 |

`L` is independent from `F`. It means the reasoning/power level **inside the selected concrete model**, not a second model family:

| Level | Meaning |
|---|---|
| `L1` | Lowest supported useful reasoning level |
| `L2` | Low-to-medium reasoning |
| `L3` | Strong/high reasoning |
| `L4` | Extra-high reasoning |
| `L5` | Highest supported reasoning level |

If a provider exposes fewer than five native levels, map multiple adjacent L values to the same native level. Never invent an unsupported provider option.

## Build the compatibility table dynamically

Do this during planning, before `planctl_concise.py create`:

1. Inspect locally installed provider CLIs/configuration first when available (`--version`, model/help commands, provider model picker/config). Do not assume a model list remembered from this skill is current.
2. Check current authoritative provider documentation when model availability, aliases, reasoning levels, or CLI flags are not fully established locally.
3. Cover `codex`, `claude`, `gemini`, `qwen`, and `muse` even if only one provider will execute initially. This is what makes later provider switching cheap.
4. For each provider, map every `F1`-`F4` to a current concrete model. Reusing the same model for adjacent F classes is allowed when a provider has fewer model families.
5. For every provider/family row, map all `L1`-`L5` to actual native effort names. Clamp by repetition when the provider exposes fewer levels.
6. Record `checked_at` and one or more source references for every provider. Prefer an installed-CLI probe and official vendor documentation; use secondary sources only when primary documentation does not expose the needed CLI detail.
7. Put the result in top-level `model_compatibility` in the plan spec. The controller writes both compatibility artifacts into the plan workspace.

Required shape:

```json
{
  "model_compatibility": {
    "generated_at": "<ISO-8601 timestamp>",
    "discovery": "Live provider CLI/help and current vendor documentation checked during planning.",
    "providers": {
      "codex": {
        "checked_at": "<ISO-8601 timestamp>",
        "sources": ["<current source or local CLI probe>"],
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

Repeat the provider object for Claude, Gemini, Qwen, and Muse.

## Refresh and provider switching

`MODEL_COMPATIBILITY.json` is the machine-readable binding; `MODEL_COMPATIBILITY.md` is its human-readable table. TODO files explicitly reference the Markdown file.

Refresh the table without changing TODO F/L requirements when:

- execution starts in a later session and current model availability is uncertain;
- the user switches provider;
- a recorded model is unavailable/retired;
- the active CLI rejects a recorded effort level;
- current vendor documentation shows a materially changed model hierarchy.

Provider availability/quota failure does not change F/L. Resolve the same F/L against another compatible provider. Increase F or L only for technical/capability evidence, following `MODEL_ROUTING.md`.

## Provider references

For provider-specific discovery/CLI notes, load only what is needed:

- Codex: `MODEL_ROUTING_CODEX.md`
- Claude Code: `MODEL_ROUTING_CLAUDE.md`
- Gemini CLI: `MODEL_ROUTING_GEMINI.md`
- Qwen Code: `MODEL_ROUTING_QWEN.md`
- Muse Code / Muse Spark: `MODEL_ROUTING_MUSE.md`
