# Qwen Code model routing

Read only when the Qwen daily cache is missing/stale/invalid, or when Qwen will execute the current task. `PORTABLE_MODEL_ROUTING.md` owns F/L semantics and the cache-first rule.

## Dynamic discovery after a cache miss

Do not hardcode Qwen model ids in the skill. Before live discovery, run `model_compatctl.py cache-status --provider qwen`. If today's cache is fresh, reuse it and skip new CLI/documentation research.

Only when Qwen's cache needs rebuilding, inspect the installed Qwen Code CLI/model picker/configuration and current official Qwen Code/provider documentation. Map the current provider-specific F/L binding, write it to Qwen's daily cache, and use it for the plan snapshot.

Map F1-F4 by actual current capability, not model-name age alone. Qwen Code can use Qwen and configured external model providers, so the compatibility entry must describe the concrete model that this installation/provider will actually invoke.

## L levels

Current Qwen Code can expose a provider-neutral reasoning-effort setting and map/clamp it per model/provider. When the installed version exposes `low`, `medium`, `high`, `xhigh`, and `max`, these naturally correspond to L1-L5. If the active provider/model supports fewer native levels, repeat/clamp L entries to the actual effective values.

Do not add an undocumented one-shot CLI flag merely to force effort. If the installed headless CLI does not expose a safe command-line override for `model.reasoningEffort`, record the effective configured/default value in the compatibility binding and rely on the current Qwen configuration rather than mutating repository settings as a hidden side effect.

## Execution

The runner already supports Qwen's headless JSON/schema output and concrete `--model` selection. Provider/quota failure keeps the same F/L requirement and may fall back to another provider after checking that provider's independent daily cache. A Qwen model/configuration mismatch requires rebuilding Qwen's cache, not plan reconstruction.
