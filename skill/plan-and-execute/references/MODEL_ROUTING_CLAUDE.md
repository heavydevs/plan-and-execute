# Claude Code model routing

Read only when the Claude daily cache is missing/stale/invalid, or when Claude Code will execute the current task. `PORTABLE_MODEL_ROUTING.md` owns F/L semantics and the cache-first rule.

## Dynamic discovery after a cache miss

Do not keep a concrete Claude model table in this skill. Before any live lookup, run `model_compatctl.py cache-status --provider claude`. If today's cache is fresh, reuse it for the rest of the local calendar day.

Only when the Claude cache needs rebuilding, inspect the installed Claude Code version/model aliases and current official Anthropic documentation, map the current concrete families/effort levels, write the provider-only result to the Claude daily cache, and use it for the plan snapshot.

Map the cheapest exploration/mechanical family to F1, the normal general-coding family to F2, the strong reasoning/coding family to F3, and the strongest justified frontier family to F4. If Claude exposes fewer distinct useful families, the same model may occupy adjacent F rows.

## L levels

Map L1-L5 to the increasing effort values actually accepted by the selected current Claude model. Provider/model effort support can differ. When fewer than five effective levels exist, repeat/clamp adjacent L values; never invent an unsupported effort.

The isolated runner resolves F/L through a fresh compatibility binding, then passes the concrete model and native effort to Claude Code. A rejected model/effort means rebuild the Claude cache, not the TODO.

## Exploration

Use the cheapest credible current Claude exploration path for disposable repository discovery when it prevents a stronger worker from ingesting large irrelevant context. Keep exploration read-only, narrow the question first, and return a compact evidence map rather than transcripts/full files.

## Escalation

Raise L when evidence shows insufficient reasoning depth within a suitable family. Raise F when evidence shows a model-capability gap or when semantic risk/weak verification justifies starting stronger. Provider quota/availability failure keeps F/L unchanged and may fall back to Codex, Gemini, Qwen, or Muse after checking that provider's independent daily cache.
