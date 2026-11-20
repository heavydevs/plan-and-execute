# Anthropic Claude via Claude Code: model x effort quality per credit (2026-11-20)

Scope: Haiku 5.5, Sonnet 5.5, Opus 5.5, Fable 5.2 (plus Mythos 5.2) in Claude Code 2.1.329 (`claude --version`, local). No model calls were made. Labels: **V** = vendor (Anthropic), **I** = independent measurement (Artificial Analysis, Bito, Zapier), **S** = secondary blog or search summary, not checked at the primary page.

## 1. Facts that change the baseline

- Nothing newer than Fable 5.2 is generally available. Mythos 5.2 (`claude-mythos-5-2`) has the same specs and price as Fable 5.2 but is limited to organizations verified through Anthropic's Cyber/Life Sciences programs (V, models overview, 2026-11-20). Not routable for this owner.
- **Minimum Claude Code versions (V, Claude Code model-config page and help article, fetched 2026-11-20): Opus 5.5 2.1.280, Sonnet 5.5 2.1.284, Haiku 5.5 2.1.293, Fable 5.2 2.1.321.** The owner's ">= 2.1.290" for Fable 5.2 is not supported: the changelog adds Fable 5.2 in 2.1.321, and the baseline's HTTP 400 on 2.1.283 is consistent. The baseline note that the `haiku` alias still gave Haiku 4.5 is probably an artifact of 2.1.283 (< 2.1.293); the docs say `haiku` is Haiku 5.5 on the Anthropic API. Re-check on 2.1.329, or keep pinning `claude-haiku-5-5`.
- **Effort defaults differ by surface.** API defaults: Fable 5.2 `high`, Opus 5.5 `medium`, Sonnet 5.5 `high`, Haiku 5.5 `medium` (V, effort page). Claude Code defaults all four to `medium` (V, model-config page). Anthropic says "start at `high`" for Fable 5.2 on the API; in Claude Code you must set it yourself. Resolution order: `CLAUDE_CODE_EFFORT_LEVEL` env, then in-session pick, then `--effort`, then settings. A top-level `effortLevel` setting does not apply to Opus 5.5. `max` is session-only. Subagents on another model use that model's saved or default effort. A safety-flagged Fable request can silently re-run on Opus 5 or Opus 4.8, so log the model that actually answered.
- **Prices per MTok (V, pricing page).** Fable 5.2 $8 in / $40 out, cache read $0.20, fast mode $16/$80 (2.5x speed). Opus 5.5 $4/$20, cache read $0.20, fast $8/$40. Sonnet 5.5 $2/$10, cache read $0.10. Haiku 5.5 $0.10/$0.50 up to 100K prompt tokens, **$0.50/$2.50 above 100K**, cache read $0.01/$0.05. Batch is 50% off. Opus, Sonnet and Fable have a flat price across the full 1M window; Haiku does not. All four: 1M context, 128K max output, adaptive thinking (always on for Fable and Opus). Haiku's tokenizer yields about 30% more tokens than Haiku 4.5.
- **Subscriptions (V, help center).** Pro and Max have a 5-hour and a weekly limit shared by Claude and Claude Code. Fable is included only on Max/Ultra and premium Team/Enterprise seats, capped at 50% of the weekly limit, and it drains that pool faster than other models. On Pro and standard seats Fable runs on pay-as-you-go usage credits from the start; the Fable 5.2 launch-week inclusion on Pro ended 2026-11-16 (GitHub #111240, S/user report). In non-interactive `-p` mode Fable bills credits without asking. The help pages disagree on whether a separate Fable weekly limit exists; plan for the 50% cap. Opus 5.5 has been the default model on all plans since 2.1.280. Monthly API credits on Max/Ultra/Team cannot be spent in Claude Code.
- **Complaints since 2026-11-15 (S, GitHub issues, all unconfirmed):** #110418 reports 67% of a Max 20x weekly meter used overnight by parallel high-effort Fable 5.2 builders/reviewers on CLI 2.1.311 (below the 2.1.321 minimum; there was an overload incident on 2026-11-16); #110944 reports false safeguard flags on ordinary messages; #110879 and #108821 report false "task complete" and verdict flipping; #108640 reports a 200K window on old bundled CLIs. Anthropic separately acknowledged limit-metering bugs and issued a free reset valid to 2026-12-10 (S). No confirmed Opus 5.5, Sonnet 5.5 or Haiku 5.5 regression found.

## 2. Matrix A: Coding Agent Index v2.1, Claude Code harness (I, Artificial Analysis, 2026-11-14)

Cell: index score / cost per task (list-price API, not subscription) / time per task / tokens per task. Source: https://artificialanalysis.ai/agents/coding-agents/comparisons/claude-code-vs-opencode (read 2026-11-20; token column from the same page). Scores within about 2 points are a tie (four configs tie near 58).

| Model | low | medium | high | xhigh | max |
| --- | --- | --- | --- | --- | --- |
| Haiku 5.5 | unknown | unknown | unknown | unknown | 30 / $2.25 / 1.3 h / 12.4M |
| Sonnet 5.5 | unknown | unknown | unknown | unknown | 56 / $11.40 / 1.4 h / 26.4M |
| Opus 5.5 | unknown | unknown | unknown | unknown | 58 / $12.61 / 1.1 h / 15.9M |
| Fable 5.2 | 48 / $2.49 / 13.4 min / 1.64M | 53 / $2.89 / 15.1 min / 1.9M | 58 / $7.51 / 31.3 min / 5.12M | 58 / $15.47 / 53.3 min / 9.75M | 56 / $44.22 / 2.2 h / 24M |

Fable 5.2 max times out on 16% of FrontierCode and 13% of SWE-Atlas attempts (xhigh: 1% and 0%). Opus 5.5 max fell back to another model in about 9% of attempts. Fable 5.1 max: 52 / $11.70.

## 3. Matrix B: Intelligence Index v5.0.1 per effort (I, Artificial Analysis model pages, read 2026-11-20)

Cell: score / minutes per task / output tokens per index run / **derived output-token spend** (M tokens x list output price, so $ per full index run, output only, excludes input and cache; Haiku assumed under the 100K tier, so its figure is a floor). Pages: https://artificialanalysis.ai/models/claude-opus-5-5, .../claude-sonnet-5-5, .../claude-fable-5-2, .../claude-haiku-5-5. Cost per task is published only at max: Opus $10.04, Sonnet $10.02, Fable $26.54, Haiku $0.41. This is a general-intelligence index, not agentic coding; use it for effort curves only.

| Model | low | medium | high | xhigh | max |
| --- | --- | --- | --- | --- | --- |
| Haiku 5.5 | 19 / 2.2 / 29.9M / $15 | 25 / 4.0 / 52.7M / $26 | 30 / 6.5 / 89.8M / $45 | 35 / 9.5 / 151M / $76 | 36 / 15.0 / 298M / $149 |
| Sonnet 5.5 | 26 / 2.6 / 21.3M / $213 | 31 / 3.8 / 29.4M / $294 | 42 / 7.1 / 54.7M / $547 | 50 / 14.5 / 111M / $1,110 | 55 / 32.9 / 335M / $3,350 |
| Opus 5.5 | 35 / 3.1 / 21.1M / $422 | 48 / 6.9 / 42.5M / $850 | 52 / 9.4 / 56.1M / $1,122 | 57 / 16.1 / 101M / $2,020 | 59 / 25.7 / 218M / $4,360 |
| Fable 5.2 | 54 / 5.5 / 34.9M / $1,396 | 56 / 6.5 / 41M / $1,640 | 62 / 15.2 / 85.3M / $3,412 | 62 / 24.5 / 144M / $5,760 | 65 / 41.5 / 275M / $11,000 |

## 4. Matrix C: other effort-level evidence

| Model / effort | Metric | Cost / tokens | Source |
| --- | --- | --- | --- |
| Opus 5.5 medium vs max | FrontierCode 1.1: 54.6% vs 54.4% (medium = max); CursorBench 4.0: 52.5% medium, 57.8% max | medium about one fifth of GPT-6 Astra cost | V, https://www.anthropic.com/claude-opus-5-5 (2026-09-22; SE +/-2-5 pts) |
| Opus 5.5 low..max, one small game task | no quality score; output tokens 3.4K / 6.3K / 12.4K / 32.4K / 160K | $0.17 / $0.26 / $0.35 / $0.82 / $5.33 (3 runs, CC 2.1.295); total tokens 129K / 133K / 223K / 472K / 2.5M (1 run) | S, https://tokensave.app/blog/claude-opus-5-5-effort (2026-10-09, upd. 10-23) |
| Opus 5.5 low..max, AutomationBench | 23.3 / 28.6 / 32.0 / 34.4 / 40.0% | $1.62 / $2.33 / $2.57 / $3.17 / $4.22 per task | S, via https://zapier.com/benchmarks/claude-opus5_5-report (not fetched) |
| Sonnet 5.5 | Terminal-Bench 4.0 70.6%; FrontierCode 1.1 52.1% xhigh vs 46.2% max | Anthropic: Medium beats Sonnet 5's best at under 1/10 cost; max over-edits and times out | V, https://www.anthropic.com/claude-sonnet-5-5 (2026-09-28) |
| Haiku 5.5 | Terminal-Bench 4.0 39.2% (AA harness 33%); FrontierCode 1.1 46.4%; not recommended for complex agentic coding | one report: about 20% TB at medium (S, unverified) | V, https://www.anthropic.com/claude-haiku-5-5 (2026-10-07) |
| Fable 5.2 | FrontierCode 2.0: 49.1% xhigh, 45.3% high vs Opus 5.5 45.5% | high about equals Opus max at about half the cost; Low matches Opus top HLE at under 1/10 cost | V, https://www.anthropic.com/claude-fable-and-mythos-5-2 (2026-11-09, edited 11-11) |
| Bito replay, all at medium, Claude Code, 8 hard sessions each | hard-session / overall: Opus 84.1 / 85.0; Fable 81.0 / 83.1; Sonnet 68.3 / 65.7; Haiku 66.5 / 67.4 | $5.40, $8.13, $1.28, $0.69 per hard session; 19.0, 14.9, 8.6, 8.1 min | I, https://bito.ai/blog/gpt-6-2-sol-astra-vs-claude-opus-fable-gpt-6-1-sol/ (2026-11-18) |

## 5. Haiku 5.5 vs Sonnet 5.5

Evidence is split by task type. On agentic coding, Sonnet wins clearly: Terminal-Bench 4.0 70.6% vs 39.2% (V), Coding Agent Index at max 56 vs 30 (I). Haiku at max cost $2.25 per task for 30 points, about the price of Fable 5.2 at medium for 53; the over-100K surcharge (5x input) removes much of Haiku's price edge in agent loops, where prompts routinely exceed 100K. On bounded sessions in Bito's replay (medium, n=8) Haiku matched Sonnet (66.5 vs 68.3 hard, 67.4 vs 65.7 overall) at about half the cost, and on the Intelligence Index Haiku high (30, $45 spend) equals Sonnet medium (31, $294). Verdict: Sonnet 5.5 is worth about 2x per session for implementation that must pass tests unattended (use `medium`, `high` for multi-file or intermittent bugs; Anthropic and the CC default say medium for well-specified work; avoid `max`, which scored below `xhigh` on FrontierCode and cost 26M tokens in the AA run). Haiku is worth it for read-only discovery, summaries, status and classification. Anthropic warns that at `low` Haiku is likelier to skip a search or a check in long agent prompts, so use **Haiku `medium`** for exploration whose misses are costly, and `low` only for short, checkable tool tasks. The baseline's "Haiku low" rung is too aggressive for exploration. Confidence: medium.

## 6. Opus 5.5 effort

Opus gains are steep to `medium`/`high` and flat after: Intelligence Index 35 > 48 > 52 > 57 > 59 while output spend goes 422 > 850 > 1,122 > 2,020 > 4,360 (B). Anthropic's own FrontierCode shows medium equal to max (V); CursorBench shows +5 points for max (V). On the one small task, max burned 20x the output tokens of medium (S). Recommendations: `medium` is the default and the right standard-to-advanced setting; `high` for strong subtle/high-risk work (about +4 points for +30% spend); `xhigh` only when a medium or high attempt failed review (+5 points for +80%); `max` is dominated and should be a last resort for Opus (4,360 spend, 15.9M tokens per coding task, about 9% fallbacks).

## 7. When Fable 5.2 is justified

Surprising result: above Opus `high`, Fable is the cheaper way to buy quality. Intelligence Index: Fable low (54, $1,396) beats Opus high (52, $1,122) and Fable medium (56, $1,640) beats Opus xhigh (57, $2,020 spend) within a point at 19% less; Fable high (62, $3,412) is above Opus max (59, $4,360) at 22% less. On the Coding Agent Index Fable high ties Opus max at 58 for $7.51 vs $12.61 and 5.1M vs 15.9M tokens. Counter-evidence: Bito's replay put Opus medium above Fable medium (84.1 vs 81.0, $5.40 vs $8.13; 8 sessions, differences inside noise); Opus lower efforts were never measured on the Coding Agent Index; Fable carries subscription friction (credits on Pro, 50% weekly cap, safety fallbacks, 30-day retention, false-positive reports, 2.1.321 minimum). So the owner's policy (Opus ceiling, Fable for extreme architecture/code review or after repeated Opus failure) is defensible for credit safety, but the evidence says that when Opus needs `xhigh` or `max`, run Fable `high` instead; never Fable `max` (2.2 h, $44, times out). Start Fable at `high`; `xhigh` adds no measured gain on the coding index at 2x cost; `medium` is a reasonable review setting (Fable at medium needs "finish the whole task" prompting, per V). Confidence: medium (one independent coding index, n small).

## 8. Recommendation per work level

| Level | Model / effort | Confidence | What would change it |
| --- | --- | --- | --- |
| Economy exploration | Haiku 5.5 `medium` (`low` for short mechanical reads) | medium | A routing-eval miss rate at `low`; prompts regularly over 100K tokens (then Sonnet `low`) |
| Standard bounded implementation | Sonnet 5.5 `medium` | medium | Failed validation then Sonnet `high`; Bito-style replay showing Haiku parity on this repo |
| Advanced | Opus 5.5 `medium` (Sonnet `high` if cost-bound) | medium | AA publishing Opus lower efforts on the coding index |
| Strong, subtle or high-risk | Opus 5.5 `high` | medium-high | A review failure then `xhigh`; Fable `medium` if Fable credits are plentiful |
| Max, very hard | Opus 5.5 `xhigh` first; on second failure Fable 5.2 `high` | medium | Opus `high` or `xhigh` measured on the coding index; Fable credit exhaustion on a Max plan |
| Frontier (owner policy) | Fable 5.2 `high` (`xhigh` for long unattended work with measured gain) | medium | A confirmed Fable regression (#110879, #108821) or false-flag fallbacks |

Operational notes: pass `--effort` explicitly (the env var wins over it); pin full model IDs; require Claude Code >= 2.1.321 before routing Fable; treat Fable `-p` runs as credit spend; run the frozen replay as the acceptance gate, since the best independent data (AA, Bito) covers few efforts per model and should be treated as direction.

## Sources (read 2026-11-20)

- https://platform.claude.com/docs/en/models/overview ; .../models/fable-5-2/overview ; .../models/haiku-5-5/overview (V)
- https://platform.claude.com/docs/en/about-claude/pricing ; .../build-with-claude/effort ; .../prompt-engineering/prompting-claude-fable-5-2 ; .../release-notes/overview (V)
- https://code.claude.com/docs/en/model-config ; https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md (V)
- https://support.claude.com/en/articles/15424964-claude-fable-models-on-your-plan ; .../11145838-use-claude-code-with-your-pro-or-max-plan ; .../11049741-what-is-the-max-plan (V)
- https://www.anthropic.com/claude-fable-and-mythos-5-2 (2026-11-09) ; /claude-opus-5-5 (2026-09-22) ; /claude-sonnet-5-5 (2026-09-28) ; /claude-haiku-5-5 (2026-10-07) (V)
- https://artificialanalysis.ai/agents/coding-agents/comparisons/claude-code-vs-opencode ; https://freakyjolly.com/coding-agent-index-v2-1-explained/ ; https://dev.to/piekwerk/coding-agent-index-v21-scores-fell-5-points-4-configs-tie-at-58-and-cost-per-task-spans-30x-1c1c (I/S, v2.1 2026-11-14)
- https://artificialanalysis.ai/models/claude-opus-5-5 ; /claude-sonnet-5-5 ; /claude-fable-5-2 ; /claude-haiku-5-5 (I, Intelligence Index v5.0.1)
- https://bito.ai/blog/gpt-6-2-sol-astra-vs-claude-opus-fable-gpt-6-1-sol/ (I, 2026-11-18) ; https://tokensave.app/blog/claude-opus-5-5-effort (S) ; https://kingy.ai/blog/claude-sonnet-5-5-effort-levels/ (S, 2026-10-05)
- https://github.com/anthropics/claude-code/issues/110418, /111240, /110944, /110879 (S, 2026-11-16..19)
