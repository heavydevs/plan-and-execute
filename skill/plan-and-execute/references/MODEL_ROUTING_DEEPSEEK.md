# DeepSeek routing (lazy reference)

Load only when `deepseek` is configured. Harness and provider profile are independent axes: DeepSeek reuses the `claude` (Anthropic API) or `codex` (Responses API) adapter; no separate runner exists.

## Profiles

`routing_config.deepseek_profile(harness)` returns env-var names only (never values):

| Harness | base_url_env | token_env |
|---|---|---|
| claude | `DEEPSEEK_ANTHROPIC_BASE_URL` | `DEEPSEEK_API_KEY` |
| codex | `DEEPSEEK_OPENAI_BASE_URL` | `DEEPSEEK_API_KEY` |

Register under `profiles.<name>` and select with `<claude|codex>.profile`. Values are read at spawn into the child env only. Defining or using a profile leaves argv of native claude/codex unchanged. Cache affinity is per harness; avoid switching harness or model mid-flow when a prefix is warm.

## Bootstrap catalog (re-verified 2026-11-20, evidence not placement)

| Model | Tiers (bootstrap) | Vision | Peak miss/hit/out | Off-peak miss/hit/out (USD per 1M) |
|---|---|---|---|---|
| `deepseek-flash` (V4.1-Flash-1017) | economy, standard | yes | 0.30 / 0.006 / 1.20 | 0.15 / 0.003 / 0.60 |
| `deepseek-v4-pro` | standard (fallback) | no | 1.32 / 0.044 / 3.96 | 0.66 / 0.022 / 1.98 |

"Pro" is not a quality order: Artificial Analysis Intelligence Index v5.0.1 puts V4 Pro at 23 ($1.77/task) below Flash at 33 (~$0.60), so V4 Pro was demoted from `advanced` to a `standard` fallback that only runs when Flash is unavailable or excluded. Both have 1M context, tools and JSON. Thinking is optional (`none` disables it). Since 2026-11-18 server-side search/fetch tool calls are not billed separately. `deepseek-v4-flash` remains a legacy alias of Flash.

Effort map (skill to native; native values are `low`, `high`, `max`): low to `low`; medium/high to `high`; xhigh/max to `max`.

## Pricing

`model_catalog.api_cost_usd(economics, uncached_in, cached_in, out, at=when)` uses base fields as peak rates and `economics.off_peak` inside its UTC daily window (start inclusive, end exclusive, may cross midnight). Without `at`, peak applies. Vendor peak (2026-11-20) is 01:00-04:00 and 06:00-10:00 UTC Monday to Friday, excluding Chinese public holidays; everything else is off-peak at half price. One daily window cannot express a weekday rule, so the catalog window is 10:00-01:00 UTC, the span that is off-peak every day; 04:00-06:00 UTC, weekends and holidays are priced at peak, which overstates cost (conservative). Never delay a run just to reach off-peak unless the user opted into deferred execution.
