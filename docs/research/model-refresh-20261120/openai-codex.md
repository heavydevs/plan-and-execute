# OpenAI Codex models: quality per credit by effort (2026-11-20)

Scope: which OpenAI model and reasoning effort gives the best verified quality per credit at each routing level, and whether `gpt-6.1-terra` still has a coding role. Baseline: `docs/research/MODEL_REFRESH_20261120.md` and the comments in `routingctl.py` (`CURRENT_MODELS["codex"]`, `ESCALATION_LADDERS`). No model calls were made for this report.

## Bottom line

- **Terra 6.1 no longer has a coding role.** Every independent agentic-coding source that measures both models (Artificial Analysis Coding Agent Index v2.1, Terminal-Bench 4.1, Vals Terminal-Bench 4.0, Vals Index v2.2) puts Sol 6.2 ahead of Terra 6.1 at the same or lower cost per task. At the efforts the router uses for Terra (medium/high), Sol 6.2 one step lower matches or beats it. Keep Terra only for visual/computer-use work, which is what OpenAI positions it for.
- **Sol 6.2 is the Codex workhorse from standard to max.** Use `xhigh` as the top Sol effort: it scores as well as `max` on the Coding Agent Index at 74% of the cost.
- **Astra 6.2 is a frontier rung at `high`/`xhigh`, never `low` and never `max`.** Astra `low` (the Codex default) is worse than Sol `low` at twice the cost. Astra `max` adds nothing over `xhigh` and costs 60% more.
- **No GPT-6.2 Terra or Luna exists.** Codex CLI 0.171.0, OpenAI's model docs and the 2026-11-17 launch post do not mention one.

## Pricing and Codex access (official unless marked)

| Model | API $/1M in / cached / out | Codex credits/1M in / cached / out | Plus msgs per 5 h |
| --- | --- | --- | --- |
| GPT-6 Luna | 0.10 / 0.01 / 0.50 | 2.5 / 0.25 / 12.5 | 350–3,000 |
| GPT-6.1 Terra | 1.00 / 0.05 / 5.00 | 25 / 1.25 / 125 | 35–285 |
| GPT-6.1 Sol | 2.00 / 0.10 / 10.00 | 50 / 2.5 / 250 | 15–160 |
| GPT-6.2 Sol | 2.00 / 0.10 / 10.00 | 50 / 2.5 / 250 | 17–180 |
| GPT-6 Astra | 10.00 / 1.00 / 50.00 (from credits) | 250 / 25 / 1,250 | 5–45 |
| GPT-6.2 Astra | 8.00 / 0.40 / 40.00 | 200 / 10 / 1,000 | 6–50 |

- Credits are exactly 25 per API dollar for every model, so API cost ratios equal credit ratios. Reasoning tokens bill as output. Effort has no per-message multiplier. It changes cost only through token volume.
- Speed multipliers (included usage / purchased credits): Fast is 2x/2x for the 6.2 models and 2.5x/2x for 6.1 Sol, Terra and 6.x. Ultrafast is 6x/3x for 6.2 Astra and Sol until 2027-02-28, then 6x. It is 8x/6x for 6 Astra and 6.1 Sol. Requests over 272K input tokens cost more (secondary sources).
- `codex debug models` on CLI 0.171.0 (run 2026-11-20) shows the following:
  - Sol 6.2 is "Fast, go-to model for coding and everyday work", with default effort `medium` and a 500K context window.
  - Astra 6.2 is "Our most capable model for complex coding and professional work", with default `low` and 272K context.
  - Terra 6.1 is "Efficient model that excels at visual understanding and computer use", with default `low`.
  - Sol 6.1 is "Previous generation". Luna is "Fast and affordable model for easier tasks", with default `medium`, and goes up to `max` with no `ultra`.
  - All other models accept `low..max` plus `ultra`.
  - **The catalog sets `default_service_tier: priority` (Fast, 2x usage) for Astra 6.2 and Terra 6.1.** The local `~/.codex/config.toml` pins `service_tier = "default"`. Keep that pin, or pass it on every dispatch.
- `ultra` means maximum reasoning plus automatic subagent delegation (OpenAI docs: "Ultra uses subagents"). Third-party reports measured 2.5x to 12x the tokens. Never route to it.
- OpenAI's model docs recommend Sol 6.2 for everyday coding and Astra for the hardest end-to-end work. They limit Terra to "clear writing and visual or screen-based work" and Luna to "specific, high-volume tasks with a known good result". They also say to start Luna at High.

## Head-to-head matrix

**A. Artificial Analysis Coding Agent Index v2.1** (independent, Codex harness, 322 tasks over FrontierCode-AA 2.0, Terminal-Bench 4.1 and SWE-Atlas-QnA-AA, 3 attempts each, released 2026-11-13). Cells show score · $/task at API list price · tokens/task (input + output) · minutes/task.

| Model | low | medium | high | xhigh | max |
| --- | --- | --- | --- | --- | --- |
| Luna 6 | unknown | unknown | unknown | unknown | 26 · $0.19 · 10.1M · 23.5 |
| Terra 6.1 | unknown | unknown | unknown | unknown | 49 · $1.53 · 14.4M · 28.1 |
| Sol 6.1 | unknown | unknown | unknown | unknown | 52 · $1.51 · 4.33M · 21.9 |
| Sol 6.2 | 37 · $0.33 · 1.31M · 7.2 | 45 · $0.57 · 2.28M · 8.4 | 47 · $0.76 · 2.96M · 10.6 | **50 · $0.90 · 3.26M · 12.6** | 49 · $1.22 · 4.25M · 17.5 |
| Astra 6.2 | 36 · $0.70 · 551K · 7.8 | 49 · $1.20 · 1.02M · 11.6 | 52 · $2.37 · 2.26M · 15.8 | 53 · $3.20 · 3.09M · 16.5 | 53 · $5.12 · 4.67M · 25.1 |

**B. Artificial Analysis Intelligence Index v5.0.1** (independent, general reasoning, not agentic coding). Cells show score · output tokens for the full run · output-token cost of that run (output tokens × output price). That last figure is a lower bound for relative comparison only. AA publishes $/task only at max: Luna $0.15, Terra $0.96, Sol 6.1 $1.27, Sol 6.2 $1.01, Astra 6.2 $4.00.

| Model | low | medium | high | xhigh | max |
| --- | --- | --- | --- | --- | --- |
| Luna 6 | 10 · 5.8M · $3 | 18 · 24.9M · $12 | 21 · 40.5M · $20 | 23 · 56.1M · $28 | 28 · 110M · $55 |
| Terra 6.1 | 29 · 7.2M · $36 | 38 · 13.6M · $68 | 42 · 20.6M · $103 | 45 · 34.7M · $174 | 51 · 99.4M · $497 |
| Sol 6.1 | 35 · 8.2M · $82 | 46 · 15.1M · $151 | 50 · 24.7M · $247 | 52 · 33.3M · $333 | 55 · 63.7M · $637 |
| Sol 6.2 | 41 · 7.2M · $72 | 53 · 14.6M · $146 | 55 · 22.7M · $227 | 56 · 33.3M · $333 | 57 · 60.9M · $609 |
| Astra 6.2 | 46 · 6.3M · $252 | 57 · 12.4M · $496 | 60 · 20.0M · $800 | 62 · 27.1M · $1,084 | 62 · 65.8M · $2,632 |

Time to first answer token at medium: Sol 6.2 3.4 s, Terra 5.3 s, Sol 6.1 5.4 s, Astra 3.9 s, Luna 6.2 s. At max: Sol 6.2 81 s, Terra 175 s, Astra 203 s.

**C. Other coding benchmarks** (effort as reported). Each row gives Luna / Terra 6.1 / Sol 6.1 / Sol 6.2 / Astra 6.2.

| Benchmark (source type) | Luna | Terra 6.1 | Sol 6.1 | Sol 6.2 | Astra 6.2 |
| --- | --- | --- | --- | --- | --- |
| Terminal-Bench 4.1, Codex, max (Snorkel board, independent), score; run tokens; run cost | 15.2%; 3.9B; $0.1K | 53.3%; 8.5B; $0.9K | 60.9%; 1.5B; $0.6K | 61.5%; 1.1B; $0.3K | 62.1%; 1.1B; $1.4K |
| Vals Terminal-Bench 4.0, mini-SWE-agent, effort n/s (independent), score; $/test | 13.6%; $0.35 | 49.5%; $2.16 | 55.1%; $1.72 | 60.6%; $1.13 | 63.1%; $4.69 |
| Vals Index v2.2, effort n/s (independent), score; $/test | 52.3%; $0.45 | 60.5%; $2.94 | 63.9%; $3.61 | 66.1%; $3.18 | 67.7%; $10.68 |
| FrontierCode 2.0, max (Cognition, rescored 2026-11-11), score; $/run | unknown | unknown (AA component 41) | unknown (AA component 42) | 43.8%; $1.29 | 44.2%; $5.97 |
| Bito replay, Codex, 8 hard sessions (independent), score; $/session | not run | not run | 73.4%; $2.06 (medium) | 67.3%; $1.22 (low) / 75.8%; $2.22 (high) | 69.1%; $4.86 (low) / 76.9%; $8.19 (high) |

Other sources:
- Bito output tokens per hard session were about 20K at low and 53K at high for Sol 6.2, and about 20K and 38K for Astra 6.2.
- I found no published figures for SWE-bench Pro, CursorBench or LiveCodeBench on any of these five models.
- On Agents' Last Exam, every figure is vendor-reported. Terra scores 57.6% at medium and 60.0% at max. Sol 6.2 scores 73.0% at max ($1.32/task). Astra 6.2 scores 77.6% at max ($4.47).

## Terra 6.1 vs Sol 6.2

**Break-even.** Cost per task is p_in·I + p_cache·C + p_out·O. Terra's price is exactly half of Sol's on all three components. Terra is therefore cheaper only when its total tokens per task stay below 2x Sol's at equal quality. The measured ratios:

| Comparison | Quality | Tokens per task (Terra / Sol) | Cost (Terra / Sol) |
| --- | --- | --- | --- |
| AA Coding Agent Index: Terra max vs Sol 6.2 xhigh | 49 vs 50 | 14.4M / 3.26M = 4.4x | $1.53 / $0.90 = 1.7x, and 2.2x the wall time |
| Terminal-Bench 4.1, both at max | 53.3% vs 61.5% | 8.5B / 1.1B = 7.7x | about 3x |
| Vals Terminal-Bench 4.0 | 49.5% vs 60.6% | not reported | $2.16 / $1.13 = 1.9x |
| Vals Index | 60.5% vs 66.1% | not reported | 0.92x |

On the Vals Index, Terra is 8% cheaper for 5.6 fewer points.

**Same effort vs lower Sol effort (Intelligence Index, output-token cost).** At the same effort the two models produce similar output volume (ratio 0.9–1.0 below max). Terra therefore costs about half as much but scores 12–15 points lower. Moving Sol 6.2 down one or more efforts settles the comparison:

| Sol 6.2 setting | Terra setting | Scores (Sol vs Terra) | Output cost (Sol vs Terra) |
| --- | --- | --- | --- |
| low | high | 41 vs 42 | $72 vs $103 (0.70x) |
| medium | xhigh | 53 vs 45 | $146 vs $174 |
| medium | max | 53 vs 51 | $146 vs $497 (0.29x) |

Terra `low` (29, $36) is the only Terra setting that no Sol 6.2 setting dominates on cost. At that point it competes with Luna, not Sol.

**Answer.** Yes. From Terra `high` upward, Sol 6.2 at a lower effort is at least as good and costs less. On the agentic coding indexes, Sol 6.2 `xhigh` beats Terra `max` while costing 41% less and taking less than half the time. For bounded implementation at medium, no head-to-head coding-agent measurement exists. The general index says Sol 6.2 `medium` costs about 2.1x Terra `medium` for 15 more points. A single retry or review-repair loop on Terra erases that gap.

Terra still has some positives:
- Nerdschalk's 9-run kits got 9/9 at every effort for about $0.07 a round.
- On Plus it allows roughly 2x Sol's message quota.

It also has a negative. Open issue openai/codex#61538 (2026-11-14) reports that Terra ends coding tasks prematurely at High.

## Sol 6.2 vs Sol 6.1

Sol 6.2 is better on Terminal-Bench 4.1 (+0.6), Vals Terminal-Bench 4.0 (+5.6), the Vals Index (+2.1), Bito (75.8% at high vs 73.4% for 6.1 at medium) and the Intelligence Index at every effort (+2 to +7, with fewer tokens).

Sol 6.2 is worse in two places:
- On the AA Coding Agent Index it is 3 points lower at max, driven by a 14-point drop on SWE-Atlas-QnA (codebase question answering, more key facts omitted).
- On the Vals Science Index it scores 57.8 vs 59.6.

User reports since 2026-11-17 add three concerns:
- early stopping and weaker instruction following (openai/codex#62195, 2026-11-18)
- over-refusal on authorized reverse engineering (#62517)
- overengineering at higher effort (Hacker News, via eesel)

The eesel review also found Sol 6.2 adding URLs that the tool never returned (7 of 14 order replies).

VentureBeat (2026-11-18) collected strongly negative early-tester verdicts, mostly about Astra. OpenAI has not posted a status incident or response. Keep Sol 6.1 as an alternate model for read-heavy review and Q&A, and as a different-model retry after Sol 6.2 stops early.

## Recommendations

| Level | Model + effort | Confidence | What would change it |
| --- | --- | --- | --- |
| Economy: exploration, extraction, mechanical with strong validation | **Luna `high`** for read-only and extraction work. **Sol 6.2 `low`** ($0.33/task, CAI 37) as soon as the task edits code. | Medium (Luna) / Medium (Sol low) | Luna scores 26 on CAI and 13–15% on Terminal-Bench, so it is unfit for agentic edits. A local replay showing Luna `medium` passing mechanical edits would move edits back to Luna. |
| Standard: bounded implementation | **Sol 6.2 `medium`**, replacing Terra `medium` | Medium-high | A head-to-head on the frozen routing-eval replay where Terra `medium` reaches equal pass@1 at less than 2x Sol's tokens. |
| Advanced | **Sol 6.2 `high`** (CAI 47, $0.76) | Medium | Evidence that `xhigh` is needed often. The gap is only 3 CAI points for 18% more cost. |
| Strong: subtle, high-risk | **Sol 6.2 `xhigh`** (CAI 50, $0.90). Alternate rung: **Sol 6.1 `max`** (CAI 52, $1.51) for review and Q&A-heavy work, or after a 6.2 early stop. | Medium | Confirmation that the 6.2 SWE-Atlas regression shows up in code review. If it does, make Sol 6.1 `xhigh/max` primary for review. |
| Max: very hard | **Sol 6.2 `xhigh`**, then **Sol 6.2 `max`** only for reasoning-depth failures. Frontier above max: **Astra 6.2 `high`** (CAI 52, $2.37), then `xhigh` (53, $3.20). Never Astra `low` or `max`. | Medium (Sol), medium-low (Astra) | An Astra `medium` replay. It matches Sol `max` on CAI (49 at $1.20 vs 49 at $1.22) at fewer tokens and less time, so it could replace Sol `max` as the last non-frontier rung. |

Changes this implies for `routingctl.py`, which this report does not apply:
- `standard: gpt-6.2-sol`, `strong/max: gpt-6.2-sol`
- the Codex ladder becomes economy low → standard medium → standard high → strong xhigh → max max
- pin `service_tier=default`
- keep `ultra` unrouted

## Limits

- **Small samples.** Bito ran 8 hard sessions per model. Nerdschalk ran 9 runs per effort with no Sol arm. The eesel review covered 77 support-style runs. CAI v2.1 has 322 tasks × 3 attempts, but only at the efforts AA chose. There are no per-effort CAI rows for Terra, Sol 6.1 or Luna.
- **Vendor claims.** Agents' Last Exam, FrontierCode "within 0.5 points at one fifth the cost", DeepSWE and Terra's OSWorld results are all OpenAI charts. Each plots the best effort per model.
- **Harness differences.** Codex vs mini-SWE-agent changes both absolute scores and token use. Vals does not state the effort it used.
- **Index drift.** Earlier AA figures for Terra (48 at max for $0.40; 41 at medium) predate v5.0.1. CAI v2.0 rows (Sol 6.1 at 54.1) are not comparable to v2.1.
- **Cost method.** Matrix B costs count output only. Agentic cost is dominated by cached input, which matrix A and the Terminal-Bench rows include.
- **Newness.** Sol 6.2 is three days old. Several regression reports have a single reporter and no OpenAI response.

## Sources (accessed 2026-11-20)

- Codex CLI 0.171.0 `codex debug models` (local, 2026-11-20)
- https://learn.chatgpt.com/docs/pricing (official credits, multipliers, quotas; no date stamp)
- https://learn.chatgpt.com/docs/models (official positioning, effort, ultra)
- https://community.openai.com/t/gpt-6-2-astra-and-sol-are-now-available/1417531 (official, 2026-11-17)
- https://openai.com/index/introducing-gpt-6-2-astra-sol/ (official, 2026-11-17; returned 403, figures via secondary coverage)
- https://artificialanalysis.ai/agents/coding-agents/comparisons/codex-vs-opencode (independent, CAI v2.1)
- https://artificialanalysis.ai/models/gpt-6-2-sol, …/gpt-6-2-astra, …/gpt-6-1-sol, …/gpt-6-1-terra, …/gpt-6-luna (independent)
- https://freakyjolly.com/coding-agent-index-v2-1-explained/ (secondary, CAI v2.1 components, 2026-11-13 release)
- https://snorkel.ai/leaderboard/terminal-bench/ (independent, Terminal-Bench 4.1)
- https://www.vals.ai/benchmarks/terminal-bench-4 and https://www.vals.ai/benchmarks/vals_index (independent, updated 2026-11-18)
- https://cognition.com/ (FrontierCode 2.0 top five; benchmark from 2026-10-27)
- https://kingy.ai/blog/gpt-6-2-astra-sol-benchmarks-pricing-reviews/ (secondary, 2026-11-17..19)
- https://bito.ai/blog/gpt-6-2-sol-astra-vs-claude-opus-fable-gpt-6-1-sol/ (independent replay, 2026-11-18)
- https://www.datacamp.com/blog/gpt-6-2-sol-vs-claude-opus-5-5 (secondary with vendor figures, 2026-11-18)
- https://www.datacamp.com/blog/gpt-6-1-terra (vendor figures, 2026-10-27)
- https://www.datacamp.com/blog/claude-haiku-5-5-vs-gpt-6-luna (2026-10-11)
- https://nerdschalk.com/gpt-6-1-terra-codex-reasoning-effort/ (independent, 2026-10-28)
- https://beam.ai/agentic-insights/gpt-6-1-terra-vs-sol (secondary, older AA figures, 2026-10-27)
- https://www.eesel.ai/blog/gpt-6-2-sol-review (independent, 77 runs, November 2026)
- https://venturebeat.com/technology/essentially-unusable-openai-launches-gpt-6-2-astra-and-sol-to-negative-reception-from-ai-power-users (2026-11-18)
- https://github.com/openai/codex/issues/62195 (2026-11-18), https://github.com/openai/codex/issues/62517 (2026-11-19), https://github.com/openai/codex/issues/62574 (2026-11-19), https://github.com/openai/codex/issues/61538 (2026-11-14)
- https://getnadir.com/blog/codex-pro-200-allowance-cut-october-29-credits-routing/ (secondary credit table, updated 2026-11-02)
- https://tokenkarma.app/blog/codex-sol-ultra-subagent-token-cost-2026/ and https://codex.danielvaughan.com/2026/07/27/gpt56-sol-ultra-mode-tradeoff-reasoning-budgets-subagent-cost-codex-cli/ (secondary, ultra token cost)
