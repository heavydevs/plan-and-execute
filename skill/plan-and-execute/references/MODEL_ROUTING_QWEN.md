# Qwen Code model routing

Read only when building/refreshing the Qwen compatibility row or when Qwen will execute the current task. `PORTABLE_MODEL_ROUTING.md` owns F/L semantics.

## Dynamic discovery

Do not hardcode Qwen model ids in the skill. At planning time inspect the installed Qwen Code CLI/model picker/configuration and current official Qwen Code/provider documentation. Put concrete current ids only in the plan's replaceable `MODEL_COMPATIBILITY.json`.

Map F1-F4 by actual current capability, not model-name age alone. Qwen Code can use Qwen and configured external model providers, so the compatibility row must describe the concrete model that this installation/provider will actually invoke.

## L levels

Current Qwen Code has a provider-neutral reasoning-effort setting and maps/clamps it per model/provider. When the installed version exposes `low`, `medium`, `high`, `xhigh`, and `max`, these naturally correspond to L1-L5. If the active provider/model supports fewer native levels, repeat/clamp L entries to the actual effective values.

Do not add an undocumented one-shot CLI flag merely to force effort. If the installed headless CLI does not expose a safe command-line override for `model.reasoningEffort`, record the effective configured/default value in the compatibility table and rely on the current Qwen configuration rather than mutating repository settings as a hidden side effect.

## Execution

The runner already supports Qwen's headless JSON/schema output and concrete `--model` selection. Provider/quota failure keeps the same F/L requirement and may fall back to another provider. A Qwen model/configuration mismatch requires compatibility refresh, not plan reconstruction.
