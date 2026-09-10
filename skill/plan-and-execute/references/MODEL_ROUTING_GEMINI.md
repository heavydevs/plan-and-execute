# Gemini CLI model routing

Read only when building/refeshing the compatibility row for Gemini or when Gemini will execute the current task. `PORTABLE_MODEL_ROUTING.md` owns F/L semantics.

## Dynamic discovery

Do not keep a hardcoded Gemini model table in this skill. At planning time:

1. inspect the installed `gemini` version and its current model/help surface;
2. inspect the current `/model` choices or equivalent CLI model configuration when available;
3. verify ambiguous aliases/model hierarchy against current official Gemini CLI documentation;
4. write the resulting concrete model ids into the plan's `MODEL_COMPATIBILITY.json` only.

Prefer the fastest current family for F1, the normal general-coding family for F2, the strongest generally available reasoning/coding family for F3, and the strongest justified frontier/preview family for F4. The same concrete model may occupy adjacent F rows when Gemini exposes fewer useful families.

## L levels

Gemini's native thinking controls do not necessarily expose the same five-level ladder as other providers or the same controls in every CLI release/model. Map L1-L5 only to behavior actually supported by the current CLI/model. Repeat/clamp adjacent L values when necessary; never invent an effort flag.

The existing runner passes the selected concrete Gemini model through `--model`. If the current Gemini CLI does not provide a safe one-shot reasoning-effort override for headless execution, record the effective provider/model default for the relevant L entries rather than pretending a level was enforced.

## Execution

Provider/quota failure does not change the TODO's F/L requirement. Switching from Gemini to another provider resolves the same F/L through `MODEL_COMPATIBILITY.json`. A rejected/retired Gemini model means refresh the compatibility table; it is not by itself a reason to replan.
