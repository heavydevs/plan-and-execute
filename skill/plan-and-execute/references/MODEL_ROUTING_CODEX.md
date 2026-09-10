# Codex model routing

Read only when building/refreshing the Codex compatibility row or when Codex will execute the current task. `PORTABLE_MODEL_ROUTING.md` owns F/L semantics.

## Dynamic discovery

Do not keep a concrete Codex model table in this skill. Model generations, aliases, availability, and effort support change independently of the plan.

At planning time:

1. inspect the installed Codex CLI/version and current model configuration/help when available;
2. identify the current economical, general-coding, strong, and frontier choices actually available to the executing account/environment;
3. verify ambiguous model hierarchy and reasoning-effort support against current official OpenAI/Codex documentation;
4. write those concrete ids only into the plan's `MODEL_COMPATIBILITY.json`.

Map the current economical model to F1, the normal general-coding model to F2, the stronger reasoning/coding family to F3, and the strongest justified frontier family to F4. Reusing one model across adjacent F rows is valid when different reasoning levels are the real distinction.

## L levels

Map L1-L5 to the increasing reasoning-effort values actually accepted by the selected current model. Do not assume a remembered Codex effort ladder is valid for every model. If a model supports fewer levels, repeat/clamp adjacent L entries in the compatibility table.

The isolated runner resolves F/L first, then passes the concrete model and resolved native reasoning effort to Codex. A rejected model/effort means refresh compatibility; it does not by itself change the TODO.

## Routing behavior

For objectively verifiable work, prefer the lowest credible F/L and raise L before F when evidence shows insufficient reasoning depth within an otherwise suitable model family. Raise F when evidence suggests a capability/model-family gap. Skip lower routes for high-blast-radius or weakly verifiable decisions when failure would be expensive.

Provider quota/availability failure keeps the same F/L and may fall back to Claude, Gemini, Qwen, or Muse through the compatibility table.
