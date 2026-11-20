# GLM / Z.AI model routing

Read only when GLM will execute the current work. `MODEL_ROUTING.md` owns provider-independent policy; `MODEL_CATALOG.md` owns the catalog schema.

## Harness and profile

GLM is a provider profile, not a new runner. Z.AI exposes Anthropic-compatible endpoints, so the `glm` profile reuses the existing `claude` harness (`routing_config.glm_profile()`):

```json
{"harness": "claude", "base_url_env": "ZAI_BASE_URL", "token_env": "ZAI_API_KEY"}
```

The profile names environment variables only. Values are read at spawn time and mapped to `ANTHROPIC_BASE_URL` / `ANTHROPIC_AUTH_TOKEN` for the child; they never appear in config, catalog, argv, snapshots, logs or reports. Argv of existing providers is unchanged. GLM is never in the default `provider_order`: unconfigured means no candidate.

## Catalog mapping (bootstrap evidence, not placement)

Catalog provider `glm` in the current bootstrap catalog (`scripts/model_catalog.py`); request s10.

| Model | Tiers | API in / cached / out (USD per 1M) | Plan multipliers in / cached / out |
|---|---|---|---|
| `glm-5.3-flash` | `economy` (multimodal) | 0.15 / 0.03 / 0.50 | 2.3 / 0.56 / 8 |
| `glm-5.3` | `standard` | 1.40 / 0.26 / 4.40 | 6.9 / 1.7 / 24 |

Re-verified 2026-11-20 (docs.z.ai; `docs/research/model-refresh-20261120/other-providers.md`): GLM-5.3 is still the newest model, ids and prices unchanged, 1M context, 128K output. Placement changed: Artificial Analysis Intelligence Index v5.0.1 puts Flash at 28 ($0.58/task, about 41 min per task) and GLM-5.3 at 32 ($5.01), so Flash is economy only and GLM-5.3 moved from `advanced` to `standard` (weaker than Kimi K3.1, Qwen4-Max and Muse Wonder; on a Coding Plan it is still a reasonable standard model). Requests for GLM-5.2/5.1 route to 5.3 and GLM-4.7 to Flash on Z.AI's side.

GLM never fills `strong` or `max` by name; promotion needs local eval evidence and a catalog change. An empty tier is skipped upward.

## Effort

Thinking is always on. The catalog `effort_map` carries the mapping; the runner does not hardcode it: `low->low`, `medium->high`, `high->high`, `xhigh->max`, `max->max`. A thinking-disabled GLM-5.3 config is rejected (`model_catalog.require_thinking`, `routing_config.glm_profile(thinking=False)`).

## Economics

Coding Plan cost is in credits, not USD:

```text
credits = (input*mi + cached_input*mc + output*mo) / 10000
off_peak_credits = credits * 0.5
```

Coding Plan peak is 06:00-10:00 UTC Monday to Friday; weekends are off-peak all day. The docs conflict on the off-peak factor (overview: 50% of standard; the 2026-07-30 notice: flagship 1x off-peak vs 3x peak, Flash 0.4x vs 1.2x, a 0.33 ratio). The catalog keeps 0.5, the smaller discount.

`input` counts uncached tokens; cached tokens bill at the lower cached multiplier, so cache hits reduce credits directly. Windows (5 h and weekly) are quota limits, not modeled here. Use `model_catalog.credits(...)` for the plan and `model_catalog.api_cost_usd(...)` for API pricing; do not delay a run to wait for off-peak.
