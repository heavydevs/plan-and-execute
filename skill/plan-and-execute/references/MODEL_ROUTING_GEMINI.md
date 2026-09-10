# Gemini CLI model routing

Read only when the Gemini daily cache is missing/stale/invalid, or when Gemini will execute the current task. `PORTABLE_MODEL_ROUTING.md` owns F/L semantics and the cache-first rule.

## Dynamic discovery after a cache miss

Do not keep a hardcoded Gemini model table in this skill. Before live discovery, run `model_compatctl.py cache-status --provider gemini`. If today's cache is fresh, reuse it and do not query Gemini again merely because another plan is being created.

Only when the Gemini cache needs rebuilding:

1. inspect the installed `gemini` version and its current model/help surface;
2. inspect the current `/model` choices or equivalent CLI model configuration when available;
3. verify ambiguous aliases/model hierarchy against current official Gemini CLI documentation;
4. map F1-F4/L1-L5, write the provider-only result to Gemini's daily cache, and use it for the plan snapshot.

Prefer the fastest current family for F1, the normal general-coding family for F2, the strongest generally available reasoning/coding family for F3, and the strongest justified frontier/preview family for F4. The same concrete model may occupy adjacent F rows when Gemini exposes fewer useful families.

## L levels

Gemini's native thinking controls do not necessarily expose the same five-level ladder as other providers or the same controls in every CLI release/model. Map L1-L5 only to behavior actually supported by the current CLI/model. Repeat/clamp adjacent L values when necessary; never invent an effort flag.

The existing runner passes the selected concrete Gemini model through `--model`. If the current Gemini CLI does not provide a safe one-shot reasoning-effort override for headless execution, record the effective provider/model default for the relevant L entries rather than pretending a level was enforced.

## Execution

Provider/quota failure does not change the TODO's F/L requirement. Switching from Gemini to another provider checks that provider's independent daily cache and resolves the same F/L. A rejected/retired Gemini model means rebuild the Gemini compatibility cache; it is not by itself a reason to replan.
