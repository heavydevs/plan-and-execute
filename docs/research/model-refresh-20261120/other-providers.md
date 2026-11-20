# Optional provider profiles: refresh of 2026-11-20

Scope: Z.AI GLM, DeepSeek, Meta Muse, Qwen, Kimi, Trae Agent and other notable cheap or open-weight coding models. No model calls were made. Evidence tags: **V** = vendor page fetched, **I** = independent (Artificial Analysis "AA", Vals), **S** = secondary blog or search summary. "unknown" means not found. AA Intelligence Index (IQ) is **v5.0.1**; the AA Coding Agent Index (CAI) is v2.1 as of 2026-11-14 (top score 58). Scores from different index versions are not comparable. Terminal-Bench (TB) 2.1, 3.0 and 4.0 are different benchmarks, so vendors' 80-90 figures on TB 2.1 must not be set against 40-67 on TB 4.0.

Bootstrap catalog `2026-11-20-bootstrap-v6` stamps every provider facet `2026-09-30`. That is 51 days old, so all three facets are past the expiry in the freshness policy (capability 10 days, economics 37, quality 44).

## Z.AI GLM

| Model id | Tier suggestion | Price per 1M (in / cached / out) | Evidence | Confidence |
| --- | --- | --- | --- | --- |
| `glm-5.3-flash` (2026-08-26) | economy | $0.15 / $0.03 / $0.50 (V) | AA IQ 28, $0.58 per index task, 41 min per task (slow), 1M context, multimodal, MIT weights (I) | medium |
| `glm-5.3` (2026-08-18) | demote: standard only for Coding Plan holders | $1.40 / $0.26 / $4.40 (V) | AA IQ 32 at $5.01 per task (I). Vendor TB 2.1 88.2 (S). No SWE-bench Pro for 5.3 | medium |
| `glm-5.3-flashx` | not needed | $0.37 / $0.075 / $1.25 (V) | unknown | low |

- Newest is still GLM-5.3. GLM-5.4 and GLM-6 are not released as of 2026-11-19 (S).
- `reasoning_effort` accepts `low`, `high`, `max`; default `max`. Thinking cannot be disabled on 5.3 or Flash (V, docs.z.ai). This matches `GLM_EFFORT_MAP` and `thinking: always_on`.
- Context is 1M, max output 128K. `glm-5.3` is text-only; `glm-5.3-flash` is multimodal (V).
- Coding Plan credits (V): the multipliers in the catalog match the docs (5.3 6.9/1.7/24; Flash 2.3/0.56/8; divisor 10,000). Lite $18/month (Pro $80, Max $168 per S): 2,000 credits per 5 hours and 10,000 per week. Lite/Pro/Max weekly credits are 10k/60k/140k.
- **Peak window:** Mon-Fri 14:00-18:00 SGT, which is 06:00-10:00 UTC. Weekends are off-peak all day. The catalog has no GLM window.
- **Conflict:** the overview page says off-peak is 50% of standard. The 2026-07-30 notice says flagship 1x off-peak vs 3x peak and Flash 0.4x vs 1.2x, which is a 0.33 ratio. The catalog uses `off_peak_factor` 0.5 and `GLM_OFF_PEAK_FACTOR` is unverified.
- Claude Code: base URL `https://api.z.ai/api/anthropic`, ids `glm-5.3` and `glm-5.3-flash[1m]`, `/effort` supported. Requests for GLM-5.2 and 5.1 route to 5.3, and GLM-4.7 routes to Flash (V). There is no first-party headless CLI, so the skill must go through Claude Code or Codex.

## DeepSeek

| Model id | Tier suggestion | Price per 1M peak (miss / hit / out); off-peak is half | Evidence | Confidence |
| --- | --- | --- | --- | --- |
| `deepseek-flash` = V4.1-Flash-1017 (2026-10-17) | economy and standard; promote | $0.30 / $0.006 / $1.20; off-peak $0.15 / $0.003 / $0.60 (V) | AA IQ 33 (max), 29 (high), about $0.60 per index task (I). Codex + Flash (max): CAI v2.0 47.3 at $0.39 per task, 2026-10-23 (S). TB 4.0 42.3 vendor, Claude Code harness (V). 1M context, vision, 552B total and 16B active, MIT | medium-high |
| `deepseek-v4-pro` = V4-Pro-0813 | demote to fallback or drop `advanced` | $1.32 / $0.044 / $3.96; off-peak $0.66 / $0.022 / $1.98 (V) | AA IQ 23 (max) at $1.77 per task (I): below Flash on both score and price. No vision | medium |

- **The catalog off-peak window is wrong.** It says 16:30-00:30 UTC daily. The vendor page says peak is 01:00-04:00 and 06:00-10:00 UTC, Mon-Fri, excluding Chinese public holidays. Everything else, including weekends and holidays, is off-peak. The schema's single daily `window_utc` cannot express this, so the schema needs a peak-list plus a weekday rule, or the economics should record peak-only rates.
- `DEEPSEEK_EFFORT_MAP` is stale. Native values are `low`, `high`, `max`, and `none` disables thinking. DeepSeek maps `minimal` and `low` to `low`, and `medium`, `high` and `xhigh` to `high`. The catalog maps skill `low` to `high`. Skill `xhigh` to `max` is a policy choice, not a vendor mapping.
- Ids `deepseek-flash` and `deepseek-v4-pro` are valid. `deepseek-v4-flash` still works as a legacy alias. V4.1 Pro is not released (S). Concurrency limits are 2,500 (Flash) and 500 (Pro).
- Since 2026-11-18, server-side search and fetch tool calls are no longer billed separately (V).
- No first-party CLI. Use the Anthropic endpoint `https://api.deepseek.com/anthropic` or the OpenAI endpoint `https://api.deepseek.com`.

## Meta Muse

| Model id | Tier suggestion | Price per 1M (in / cached / out) | Evidence | Confidence |
| --- | --- | --- | --- | --- |
| `muse-ember-1.0` (2026-11-09) | economy; add | $0.10 / $0.004 / $0.50, above 200K prompt $0.30 / $0.012 / $1.50 (V) | AA IQ 36, about $0.14 per task; CAI-AA 46 vs Haiku 5.5 37; TB 4.0 40.9 (Meta, mixed harnesses) (V). Haiku leads FrontierCode 2.0 34.9 vs 27.2 | medium |
| `muse-spark-1.3` (2026-09-02) | demote from advanced to standard or drop | $1.25 / $0.15 / $4.25 (V) | AA IQ 37 at $2.39 per task, and AA marks it deprecated in favour of Wonder (I). TB about 33 (S). Costs 17x Ember for a 1-point IQ gain | medium |
| `muse-wonder-1.0` (2026-10-12, preview) | advanced; add | $4.00 / $0.20 / $20.00 (V) | AA IQ 44 (max) at $6.95 per task. TB 4.0-AA 52.0 (Meta), Vals 49.5 (S). Wonder Full in Muse Code: CAI v2.0 58.9 (S) | medium |
| `muse-spark-1.3-contributor` | never route | $0.10 / $0.002 / $0.20; prompts used for training (V) | rate-limited to 150 RPM | high |

- **`muse-spark-1.3` ceiling is stale.** `max_effort` "high" is wrong: `max` works on Wonder, Spark 1.3 and Ember but not on contributor. The Spark default is `high`; Wonder and Ember default to `max`. `none` returns HTTP 400. Values are `minimal` to `max` (V). The catalog has no `effort_map` for Muse.
- **The CLI (Muse Code, launched 2026-08-06) defaults to `muse-spark-1.2`**, so the skill must pass `--model`. Headless is `muse exec "<prompt>"` with `--json`, `--prompt-file`, `--max-model-steps`, `--reasoning-effort`. Approval is `--approval-mode on-request|untrusted|never`; network is `--sandbox-network proxy-only|restricted|unrestricted`. `--yolo` disables both guards. CI auth is `META_API_KEY`. The binary is closed and no regions are listed.
- Wonder Full is only in Muse Code Power and Maximum plans (S, plans reported as $5/$15/$50/$200). Muse Spark Open (816B, 42B active) is open-weight but self-hosted only.

## Qwen

| Model id | Tier suggestion | Price per 1M (in / cached / out) | Evidence | Confidence |
| --- | --- | --- | --- | --- |
| `qwen4-max` (GA 2026-11-16) | add as optional standard or advanced | $1.50 / $0.075 / $4.50 (S, Singapore list) | AA IQ 43 at $3.27 per task (I). TB 4.0 48.5 vendor, 48.48 Vals (I). DeepSWE 75.7 vendor. Closed weights. 1M context | medium-low |

- Qwen Code v0.28.0 (2026-11-17) adds qwen4-max with a "native effort ladder". The exact values (low, medium, xhigh per one S) are unconfirmed. QwenCloud default is `high`, thinking on.
- Headless: `-p`, `-o text|json|stream-json`, `--approval-mode plan|default|auto-edit|auto|yolo`, `--sandbox` (yolo alone gives no sandbox), `-m` (V).
- The free OAuth tier ended 2026-04-15. The Coding Plan Pro is reported at $50/month with 6,000 requests per 5 hours (S). Smaller Qwen4 models are promised as open weights with no date.

## Kimi

| Model id | Tier suggestion | Price per 1M (in / cached / out) | Evidence | Confidence |
| --- | --- | --- | --- | --- |
| `kimi-k3.1-pro` (2026-10-23, weights 2026-11-04) | add as advanced | $2.00 / $0.20 / $10.00 (S; Alibaba Cloud lists $2/$10/$0.2) | AA IQ 46, the top open-weight, $3.68 per task, 30 tok/s (slow) (I). TB 4.0 65.7 vendor, 67.2 AA, 63.64 Vals. 2.8T total and 104B active, modified-MIT | medium-high |
| `kimi-k3.1-pro-highspeed` | optional | $4 / $0.20 / $20 (S) | 2-3x faster | low |

- Kimi Code CLI 2.7.0 (2026-11-19). Print mode is `kimi -p "<prompt>"` with `--output-format text|stream-json`. Print mode requests no approval and uses the `auto` policy. `--yolo` and `--auto` cannot combine with `--prompt`. No sandbox flag is documented. `-m` selects the model alias.
- Thinking cannot be disabled on K3.1 Pro; levels are `low`, `high`, `max` (default `high`) (V). Subscription-endpoint ids (`kimi-for-coding`, `k3.1-pro`) differ from platform ids (S).
- Plans (S): Moderato $19 and Allegretto $39 per month; the 1M context needs Allegretto or above (V).
- The AA chart showed "Kimi Code CLI K3" at about $3.18 per task (S, version unknown).

## Trae Agent

ByteDance's `trae-cli run` is an MIT research agent. It has `--provider`, `--model`, `--must-patch` and Docker flags, and no releases page. I found no November 2026 model news. Doubao-Seed-2.0-Code dates from 2026-02-14 (S). **Drop; do not add.**

## Others worth knowing

- **Mistral Large 4** (`mistral-large-4-0`, GA 2026-11-05): $0.70 / $0.07 / $2.10, 1M context, open weights, agentic-coding focus (V). I found no independent coding index. Confidence low. Watch, do not add.
- **Not routable:** MAI Code 2 and Flash (Copilot only), Cognition SWE-2 Flash, Cursor Composer 2.5 (Cursor only), ERNIE 5.5 Flash preview, Tencent Hy4 flash, SenseNova-Loop-9B (general 9B).

## Stale or missing bootstrap entries

| Item | Catalog says | Correct |
| --- | --- | --- |
| All facets | observed 2026-09-30 | expired; re-stamp after edits |
| DeepSeek off-peak window | 16:30-00:30 UTC daily | peak 01-04 and 06-10 UTC Mon-Fri excluding Chinese holidays; off-peak otherwise |
| `DEEPSEEK_EFFORT_MAP` `low` | `high` | `low` native exists |
| `deepseek-v4-pro` tier | advanced | AA IQ 23, below Flash 33 at 3x the cost |
| `muse-spark-1.3` `max_effort` | `high` | `max` supported (not contributor) |
| `muse-spark-1.3` tier | advanced | IQ 37; Wonder (44) is the advanced model |
| `_MUSE_REF` | ids unverified | id and effort vocabulary verified in dev.meta.ai |
| Muse CLI default | implied 1.3 | CLI defaults to `muse-spark-1.2`; pass `--model` |
| `glm-5.3-flash` capabilities | no vision | multimodal |
| `glm-5.3` tier | advanced | IQ 32 at $5.01 per task; weaker than Kimi, Qwen4-Max and Wonder |
| GLM off-peak factor | 0.5 | docs conflict: 0.5 (overview) vs 0.33 (notice) |
| Missing | none | `muse-ember-1.0`, `muse-wonder-1.0`, `kimi-k3.1-pro`, `qwen4-max` |

Model ids `glm-5.3`, `glm-5.3-flash`, `deepseek-flash`, `deepseek-v4-pro` and `muse-spark-1.3` are all still valid.

## Keep, demote, drop

| Provider | Verdict | Safe work level (confidence) |
| --- | --- | --- |
| DeepSeek Flash | keep and promote | economy and standard (medium-high) |
| Muse Ember | add | economy, sub-agent work (medium) |
| Kimi K3.1 Pro | add | advanced (medium-high); weak on speed |
| Muse Wonder | add as preview | advanced (medium); expensive |
| GLM Flash | keep | economy (medium); slow |
| Qwen4-Max | add as optional | standard or advanced (medium-low) |
| DeepSeek V4 Pro, GLM-5.3, Muse Spark 1.3 | demote or drop | dominated by cheaper models above |
| Trae Agent | drop | none |

None of these has a measured result in this repository. Treat the above as routing priors; the frozen routing-eval replay remains the gate.

## Sources (fetched 2026-11-20)

- https://docs.z.ai/guides/overview/pricing
- https://docs.z.ai/devpack/overview
- https://docs.z.ai/devpack/notice/usage-revision.md
- https://docs.z.ai/guides/llm/glm-5.3.md
- https://docs.z.ai/devpack/latest-model.md
- https://docs.z.ai/release-notes/new-released
- https://api-docs.deepseek.com/quick_start/pricing
- https://api-docs.deepseek.com/guides/thinking_mode
- https://api-docs.deepseek.com/news/news1017
- https://dev.meta.ai/docs/muse-code
- https://dev.meta.ai/docs/muse-code/permissions
- https://dev.meta.ai/docs/muse-code/configuration
- https://dev.meta.ai/docs/coding-agents
- https://dev.meta.ai/docs/pricing-rate-limits
- https://dev.meta.ai/docs/reasoning
- https://research.meta.ai/blog/muse-ember
- https://www.theregister.com/ai-and-ml/2026/08/06/meta-wants-to-get-inside-your-terminal-with-its-new-coding-agent/5283717
- https://www.kimi.com/code/docs/en/kimi-code/whats-new.html
- https://www.kimi.com/code/docs/en/kimi-code-cli/reference/kimi-command.html
- https://github.com/MoonshotAI/kimi-code/releases
- https://www.alibabacloud.com/help/en/model-studio/kimi-k3-1-pro
- https://github.com/QwenLM/qwen-code/releases
- https://qwenlm.github.io/qwen-code-docs/en/users/features/headless/
- https://www.datacamp.com/blog/qwen4-max (S)
- https://artificialanalysis.ai/models/glm-5-3, /glm-5-3-flash, /kimi-k3-1-pro, /deepseek-v4-pro, /deepseek-v4-1-flash-1017, /muse-spark-1-3, /muse-wonder, /qwen4-max (I)
- https://artificialanalysis.ai/agents/coding-agents/claude-code (CAI v2.1)
- https://cellcog.ai/blog/artificial-analysis-coding-agent-index/ (S, 2026-10-23)
- https://dev.to/piekwerk/coding-agent-index-v21-scores-fell-5-points-4-configs-tie-at-58-and-cost-per-task-spans-30x-1c1c (S, 2026-11-15)
- https://www.lindy.ai/blog/kimi-k3-1-pro (S)
- https://friendli.ai/blog/kimi-k3-glm-5.3-coding-agent-benchmark (S, 2026-08-24)
- https://www.nocode.mba/ai-release-tracker/2026/11 (S)
- https://docs.mistral.ai/models/mistral-large-4 (V)
- https://github.com/bytedance/trae-agent (V)
- https://www.meta.com/help/subscriptions/1021145227643680/ (S; Muse plans via search summary)
