# DeepSeek routing (lazy reference)

Load only when `deepseek` is configured. Harness and provider profile are independent axes: DeepSeek reuses the `claude` (Anthropic API) or `codex` (Responses API) adapter; no separate runner exists.

## Profiles

`routing_config.deepseek_profile(harness)` returns env-var names only (never values):

| Harness | base_url_env | token_env |
|---|---|---|
| claude | `DEEPSEEK_ANTHROPIC_BASE_URL` | `DEEPSEEK_API_KEY` |
| codex | `DEEPSEEK_OPENAI_BASE_URL` | `DEEPSEEK_API_KEY` |

Register under `profiles.<name>` and select with `<claude|codex>.profile`. Values are read at spawn into the child env only. Defining or using a profile leaves argv of native claude/codex unchanged. Cache affinity is per harness; avoid switching harness or model mid-flow when a prefix is warm.

## Bootstrap catalog (dated 2026-10-01, evidence not placement)

| Model | Tiers (bootstrap) | Vision | Peak miss/hit/out | Off-peak miss/hit/out (USD per 1M) |
|---|---|---|---|---|
| `deepseek-flash` | economy, standard | yes | 0.30 / 0.006 / 1.20 | 0.15 / 0.003 / 0.60 |
| `deepseek-v4-pro` | advanced | no | 1.32 / 0.044 / 3.96 | 0.66 / 0.022 / 1.98 |

"Pro" is not a quality order; selector ranking uses verified outcomes. Both have 1M context, tools and JSON. Thinking is optional.

Effort map (skill to native): low/medium/high to `high`; xhigh/max to `max`.

## Pricing

`model_catalog.api_cost_usd(economics, uncached_in, cached_in, out, at=when)` uses base fields as peak rates and `economics.off_peak` inside its UTC daily window (start inclusive, end exclusive, may cross midnight). Without `at`, peak applies. Bootstrap window is 16:30-00:30 UTC; it is not in the request and is unverified, so refresh it. Never delay a run just to reach off-peak unless the user opted into deferred execution.
