# Dynamic model matrix contract

Read this only when an ORCHESTRATED plan is being created or its model catalog is being refreshed.

The durable plan must not bind TODOs to a concrete vendor model. TODOs store only two provider-neutral coordinates:

- `F1` -> cheapest credible model family for mechanical/exploratory work;
- `F2` -> normal implementation family;
- `F3` -> strong model family for difficult/high-risk engineering;
- `F4` -> frontier family for long-horizon or repeated hard failures;
- `L1` -> lowest useful reasoning/agent effort for that provider/model;
- `L2` -> normal economical effort;
- `L3` -> high effort;
- `L4` -> very high effort;
- `L5` -> highest currently supported effort worth exposing.

Higher `F` means more model capability/cost budget. Higher `L` means more reasoning/agent effort. These are logical coordinates, not model names. Adjacent levels may legitimately map to the same native setting when a provider exposes fewer effort controls.

## Live discovery is required

At planning time, build a fresh matrix instead of trusting model names embedded in this skill.

1. Discover which supported coding-agent CLIs are installed/usable: Claude Code, Codex, Gemini CLI/Antigravity-compatible CLI, Qwen Code, Muse Code, and any other runner adapter available to this skill.
2. Consult current first-party model/catalog/pricing documentation and the installed CLI's model/effort help when available.
3. When web/research access exists, consult a recent independent coding-agent benchmark appropriate to repository/terminal work. Prefer verified quality per completed task and cost per completed task over raw token price.
4. Assign each provider's current models to `F1`..`F4`. Repeating a model across adjacent F families is allowed when the provider has fewer distinct useful model families.
5. Map `L1`..`L5` to that provider's current native effort names. Repeating a native effort is allowed when the provider exposes fewer levels.
6. Record the evidence date and sources. Never copy a benchmark score into the durable TODO itself.

Do not make the current provider the plan's identity. New TODOs keep `provider: auto`; actual provider/model/effort is resolved when execution starts and is recorded only in attempt history/results.

## JSON spec

Write a temporary JSON spec and persist it with `modelmapctl.py` after `planctl_concise.py create`.

```json
{
  "researched_at": "2026-09-10T16:30:00-03:00",
  "research_mode": "live",
  "sources": [
    {"label": "Provider model catalog", "url": "https://provider.example/models"},
    {"label": "Recent coding-agent benchmark", "url": "https://benchmark.example/current"}
  ],
  "providers": {
    "codex": {
      "families": {
        "F1": "current-cheap-model",
        "F2": "current-standard-model",
        "F3": "current-strong-model",
        "F4": "current-frontier-model"
      },
      "levels": {
        "L1": "low",
        "L2": "medium",
        "L3": "high",
        "L4": "xhigh",
        "L5": "max"
      },
      "benchmark": "Why these families are currently efficient for coding-agent work.",
      "pricing": "Relevant subscription/API or per-task cost note.",
      "notes": "Provider-specific compatibility caveats only."
    }
  }
}
```

Supported matrix provider names include `claude`, `codex`, `gemini`, `qwen`, `muse`, `kimi`, and `trae`. At minimum include every provider that may realistically execute or resume this plan. For portability-sensitive work, include more than one usable provider whenever current evidence is available.

## Persist into the plan

```bash
python <skill-dir>/scripts/planctl_concise.py create --repo-root . --spec /tmp/plan-spec.json
python <skill-dir>/scripts/modelmapctl.py write --plan .ai-work/<plan-id> --spec /tmp/model-matrix.json
python <skill-dir>/scripts/modelmapctl.py validate --plan .ai-work/<plan-id>
```

The controller creates:

- `MODEL_MATRIX.json` — machine-readable runtime mapping;
- `MODEL_MATRIX.md` — the human-readable provider/F/L table;
- a short `PLAN.md` reference to the matrix;
- routing-policy metadata in `orchestrator.config.json`.

The runner reads the plan-local JSON at execution time. Switching from one supported provider to another therefore does not require rewriting TODOs: the same `F#/L#` route is re-resolved through the target provider's row.

## Refreshing an old plan

A long-lived/resumed plan may outlive a model release. Before consequential execution after a meaningful time gap, provider deprecation, pricing change, or benchmark change, re-run live discovery and overwrite the plan-local matrix through `modelmapctl.py write`. Do not change TODO F/L coordinates merely because model names changed.

If live research is unavailable, the runner may use its built-in conservative fallback catalog. Mark such a matrix `research_mode: fallback`; do not present it as current benchmark evidence.
