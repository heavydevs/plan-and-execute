# Google Antigravity (agy CLI 1.5.13): quality per credit, 2026-11-20

Scope: which model and thinking level to use per work level, and where Carbon, Argon, Flash 3.8 and the in-Antigravity Claude and GPT-OSS models fit. Owner order: Antigravity, then Codex, then Claude. Status: a routing decision from mostly secondary evidence. No model calls were made. Local facts: `agy --version` is 1.5.13. `agy models` lists Neon and Hydrogen (low..xhigh), Argon (low..high), Orchestrator (Neon) and (Argon), Flash 3.8 (low..high), Claude Opus 5.5 and Sonnet 5.5 (low..high), and `gpt-oss-120b-medium`. It has no Carbon and no Orchestrator (Carbon).

## 1. Matrix

Cell format: **II** = Artificial Analysis (AA) Intelligence Index v5.0.1 | **$/task** = cost per Index task at current list prices | output tokens for the whole Index run | speed. This index is mixed reasoning and knowledge work, not coding. "unk" means not found. Coding evidence is in the second table, because AA's Coding Agent Index (CAI) is published only at one level per model.

| Model | low | medium | high | xhigh |
| --- | --- | --- | --- | --- |
| Hydrogen ($1.50/$7.50) | II 27 / $0.29 / 20.3M / 157 t/s [2,3] | II 41 / $0.80 / 54.4M / 159 t/s [2,3] | II 51 / $1.87 / 110M / 161 t/s [2,3] | II 54 / $3.16 / 304M / 164 t/s [2,3] |
| Neon ($3/$15) | II 44 / $0.75 / unk / ~100 t/s [1,4] | II 55 / $1.90 / unk / ~100 t/s [1,4] | II 60 / $3.74 / unk / 101 t/s [1,4] | II 61 / $6.44 / 283M / 110 t/s [1,4] |
| Argon ($2/$10, then $4/$20 on 12-01) | unk | II 48 / $4.31 now, $8.63 after / unk / 66 t/s [1,4] | II 50 / $4.97 now, $9.95 after / 113M / 66 t/s [1,4] | not offered |
| Carbon (Ultra only; $2/$10, then $4/$20) | II 54 / $3.59 now, $7.19 after / unk / 48-66 t/s [4] | II 58 / $3.29 now, $6.59 after / unk [1,4] | II 60 / $3.88 now, $7.76 after / 205M / 56 t/s [1,4] | not offered |
| Flash 3.8 ($0.75/$3.75 to 2026-12-31, then $1.50/$7.50) | II 52 / $0.24 / ~48k out per task / unk [5] | II 57 / $0.41 [5] | II 59 / $0.58 / ~300 t/s [5] | not offered |

Caveats on the matrix:
- Flash 3.8 values are from AA's 2026-09-02 article on an older index version. They are not comparable with the v5 rows. One secondary source puts Hydrogen high at 51 against Flash 3.8 at 31 on the current index, which I could not verify. Treat Flash as clearly below Hydrogen high.
- Carbon default conflicts. Valyu says medium [1]. Antigravity docs say high [6].
- Time per Index task: Hydrogen 1.5, 4.2, 8.6 and 15.2 min for low..xhigh. Neon 3.7, 8.3, 14.8 and 21.5 min. Carbon about 29 to 37 min. Argon about 29 min [4].

**Coding Agent Index (Antigravity CLI, 2026-11-19, vendor-independent AA, one level per model):**

| Config | CAI | $/task | In / out tokens | Steps | Wall time |
| --- | --- | --- | --- | --- | --- |
| Neon xhigh | 58.64 | $6.86 | 13.72M / 125.6k | 177 | 30.5 min [7] |
| Carbon high | 55.47 | $9.75 | 15.31M / 120.5k | 186 | 33.6 min [7] |
| Hydrogen xhigh | 52.32 | $4.45 | unk | 405 | 32.1 min [4] |
| Argon high | 45.50 | $6.84 | unk | 171 | 37.7 min [4] |

Verified: the four CAI scores and costs match across Valyu [1], OrcaRouter [7] and AIHubMix [4], which all cite AA. Carbon's $9.75 appears to be at the $4/$20 post-December rate. My check from the token counts and 94 to 96% cache hits gives about $9 at $4/$20 and about $4.5 at $2/$10. This is inference, and Valyu says only that its Index-task Carbon figure is at standard rate. Other published components: Terminal-Bench 4.1 Neon xhigh 65.2%, FrontierCode 2.0 43.0 (AA run) or 46.2% at high (Google) [7,8]. Claude Code references on the same index are Opus 5.5 max at 58.16 and $12.61, and Fable 5.2 high at 58.24 and $7.51 [7,9].

**Other evidence:**
- Vals Index 2.2 (2026-11-18, thinking undisclosed): Neon 70.87, Carbon 70.45, Argon 69.39, Hydrogen 68.49 [1].
- Vals Terminal-Bench 4.0: Hydrogen 54.04% [10].
- Bito replay (2026-11-13, Claude Code harness through AI Studio, 8 hard sessions): Hydrogen high 71.6% at $4.37 (hard-session $1.28); Carbon 76.3%; Opus 5.5 medium 84.1%; Sonnet 5.5 68.3%. Hydrogen scored 66.1% in Gemini CLI. No Neon or Argon replay was found [11].
- CursorBench: one blog claims Neon 65.4% vs Opus 5.5 58.1%. It is Google-relayed and I did not verify it [12].
- Harness sensitivity is large: Google's own SWE-sweep gives Neon 12.8% on mini-SWE and 39.0% in Antigravity [8].

## 2. Hydrogen low/medium vs Neon low/medium for the standard tier

Neon wins on evidence, with moderate confidence.
- Neon low (II 44, $0.75, 3.7 min) beats Hydrogen medium (II 41, $0.80, 4.2 min). Neon is +3 points at the same cost and time [4].
- Neon medium (II 55, $1.90) beats Hydrogen high (II 51, $1.87) by 4 points at equal cost [4]. Hydrogen's per-token discount is eaten by about 2x more thinking tokens, and by 405 steps against 177 on the coding index.
- Hydrogen's genuine edge is speed (about 160 against about 100 t/s) and the low rung. Hydrogen low costs $0.29 and scores 27, which suits mechanical edits, log monitoring and handoffs. Hydrogen is also the only Gemini 4 model with a free API tier [1,13].
- Limits of this verdict: it uses the Intelligence Index, not coding agent runs. Quota consumption is "agent work", not tokens [14], and credit overage is billed at standard API pricing [14,15], so price per task is the best proxy. Neon is also five days old and has the least independent coding data.

## 3. Plans, quotas and operating behavior

- Plans (docs 2026-11-20 [6,14]): Free/Plus has Flash 3.8 only. AI Pro has Neon, Argon, Orchestrator (Neon/Argon), and Hydrogen, Claude 5.5 and GPT-OSS for non-trial subscriptions. Ultra adds Carbon and Orchestrator (Carbon). Enterprise has Carbon but no Orchestrator.
- Prices from secondary sources [15]: Pro $19.99, Ultra 5x $99.99, Ultra 20x $199.99. Plans-page limits are unpublished. Pro refreshes every five hours until a weekly cap. Ultra has the highest weekly limit.
- Two pools, each with a five-hour and a weekly meter: Gemini models, and Claude plus GPT models [6]. Claude 4.6 and GPT-OSS-120b were removed on 2026-11-18 per docs, yet `agy models` still lists `gpt-oss-120b-medium` locally. Treat it as unstable and do not route to it.
- Credits and caps: AI credits (Pro/Ultra) apply per model when "Overages: Always" is set. Docs mention no hard spend cap [14,15]. API-key mode does not use credits, and `/usage` and `/quota` exit with code 2 under `-p` [16].
- Retry behavior: CLI 1.5.10 waits out rate-limit delays up to 4 minutes. Spend-cap, prepaid-balance and weekly-quota errors stop the turn immediately. 1.5.12 retries resets and broken responses. 1.5.13 reports SUCCESS in JSON output when a run succeeds after a retry [16]. The worker adapter should classify an immediate quota stop as quota, not as a model failure.
- Context: AA lists a 1,048,576-token window shared by input, thinking and output, with a 65,536 output cap per hop (Carbon/Argon non-streaming 32,768) [1]. Antigravity docs say Neon "up to 512K" [6]. Users report that since 2026-11-17 the Gemini 4 family silently drops the oldest context past about 126k to 128k tokens in CLI 1.5.10 and the app (password test), and that Hydrogen high returned a 400 error at 66k to 103k input [17,18]. Google has not responded. Keep tasks under about 100k tokens of live context until fixed.
- Orchestrator: a read-only planner phase, then Hydrogen executes. The planner takes over on friction, and pure questions or reviews are answered by the planner directly. Effort is fixed at high for both and `--effort` does not apply [6,16]. Google claims Carbon plus Hydrogen stayed near Carbon's success on Terminal-Bench 4.0 with 24% less quota [19]. This is a vendor claim.
- Degradation since 2026-11-14 to 17 [18,20]: about 15 forum users report Carbon, Argon, Hydrogen and Neon doing little or no reasoning on tool-call turns, with zero thinking tokens on the subscription path against 479 to 758 on the API. They also report median tool calls per turn falling from about 29 to 1 in one log, and `THINKING_LEVEL_XHIGH` 400 errors at the Orchestrator handoff. A Google staff reply (2026-11-18) denied any client setting that removes reasoning and advised updating the app to v2.33.0 and the CLI to 1.5.11. One user saw Neon/Carbon high return to full reasoning on 2026-11-19. Unconfirmed by Google. If real, AA's numbers (measured on 1.5.9) overstate subscription quality. Verify with a small frozen replay before trusting it.

## 4. Claude Opus/Sonnet 5.5 inside Antigravity vs Claude Code directly

- Antigravity Claude (Pro non-trial, Ultra, Enterprise) draws on its own Claude+GPT pool with undisclosed size. Effort tops out at high. Forum threads from 2026-10-20, 11-15, 11-17 and 11-18 report this pool dropping to 0% with little or idle use [21]. These are user claims.
- Claude Code uses Anthropic's own five-hour plus weekly limits, shared with claude.ai. Those numbers are also unpublished and the sources conflict [22]. Direct use gives the full effort range (max), the Claude Code harness, and a documented Opus 5.5 API price of $4/$20 (baseline doc).
- No evidence compares Opus in the two harnesses. Use Antigravity's pool as extra, separately metered capacity for `advanced` work and a fallback when Gemini limits hit. Keep `strong` and `max` Claude work on Claude Code, which matches the repo's cap at advanced. Per AA, Opus 5.5 max costs $12.61 per coding task against Neon xhigh at $6.86 for about the same score, so Claude is not the credit-efficient choice when Antigravity is healthy.

## 5. Recommendations

| Level | Pick | Confidence | Would change if |
| --- | --- | --- | --- |
| economy | Hydrogen low; Flash 3.8 low/medium for monitoring | Medium | Hydrogen low fails routine edits (then Neon low); Flash price doubles on 2027-01-01 |
| standard | Neon low (Neon medium for multi-file); Hydrogen medium only when speed matters or Neon is unavailable | Medium-low (index is not coding-specific) | A frozen replay shows Hydrogen medium within 3 points of Neon low; Neon tool-turn reasoning stays degraded |
| advanced | Neon high; Claude Opus 5.5 medium/high on agy as overflow | Medium | Neon high drops below Opus on the replay; context truncation forces fragmentation |
| strong | Neon xhigh, on failure evidence rather than by default | Medium | xhigh keeps returning 400 or zero-thinking turns; then use Codex Sol high |
| max | Neon xhigh plus Orchestrator (Neon) only for tasks that need planning; escalate to Codex, then Claude Opus | Low-medium | Opus/Sol clearly beat Neon on the replay; Orchestrator effort stays fixed at high |

Carbon fit: it scores below Neon xhigh on the Coding Agent Index (55.5 vs 58.6) at about 1.4x the cost per task after 2026-12-01. It is slow (about 56 t/s, 34 to 37 minutes per task), and needs Ultra. The measured evidence does not support it for implementation. It fits only a frontier-only level: architecture planning (Orchestrator (Carbon) read-only phase) and review of extremely hard demands, where Google positions it for long-horizon and cyber work and the planner answers reviews directly. That support is vendor claims only. The owner's account does not list Carbon, so no preset should depend on it. Argon is dominated: Neon medium (II 55, $1.90) beats Argon high (II 50, $4.97), and Argon's price rises on 2026-12-01. Keep Argon out except as the Pro-plan planner alternative to Neon.

Suggested change to the repo preset (not applied): move Neon low/medium into `standard` and limit Hydrogen to `economy` plus a fast `standard` fallback. Keep Flash for monitoring and Argon unused.

## Sources (all accessed 2026-11-20)

1. https://www.valyu.ai/blogs/gemini-4-neon-vs-carbon-vs-hydrogen-vs-argon (AA snapshots 2026-11-19, Vals 2026-11-18)
2. https://artificialanalysis.ai/models/gemini-4-hydrogen
3. https://agentspulse.github.io/tutorials/gemini-4-hydrogen-benchmarks/ (AA, accessed 2026-11-13)
4. https://aihubmix.com/blog/gemini-4-hydrogen-vs-neon-vs-carbon-vs-argon-which-one-should-you-use (2026-11-19, cites AA)
5. https://artificialanalysis.ai/articles/gemini-3-8-flash (2026-09-02, older index)
6. https://antigravity.google/docs/models
7. https://www.orcarouter.ai/blog/gemini-4-neon-coding-agent-index (cites AA CAI v2.1)
8. https://dev.to/hassann/gemini-4-neon-benchmarks-coding-agents-and-cost-per-task-2ib3 (Google-reported)
9. https://artificialanalysis.ai/articles/gemini-4-neon-intelligence-gain
10. https://www.vals.ai/models/google_gemini-4-hydrogen
11. https://bito.ai/blog/gemini-4-hydrogen-vs-claude-opus-sonnet-haiku-sol/ (2026-11-13)
12. https://officechai.com/ai/gemini-4-neon-benchmarks/ (search summary)
13. https://aistudio.google.com/docs/pricing
14. https://antigravity.google/docs/plans
15. https://agentpedia.codes/blog/antigravity-credits-pricing-explained (2026-10-30, secondary)
16. https://raw.githubusercontent.com/google-antigravity/antigravity-cli/main/CHANGELOG.md and https://www.gradually.ai/en/changelogs/antigravity/
17. https://discuss.ai.google.dev/t/gemini-4-family-silently-drops-context-beyond-128k-tokens-in-antigravity-since-nov-17/201849
18. https://discuss.ai.google.dev/t/severe-intelligence-degradation-across-all-models-since-november-15-is-google-routing-requests-to-inferior-models/201295
19. https://dev.to/uulab/gemini-4-neon-the-balance-point-between-carbon-and-hydrogen-benchmarks-api-pricing-and-4pa6
20. https://discuss.ai.google.dev/t/counter-data-tool-aware-minimal-thinking-is-measurably-degrading-output-quality-on-agy-gemini-4-carbon/200671
21. https://discuss.ai.google.dev/t/bug-google-ai-ultra-both-gemini-and-claude-gpt-weekly-quotas-suddenly-dropped-to-0-antigravity-ide/191692 and https://discuss.ai.google.dev/t/argon-and-chatgpt-claude-model-quotas-being-drained-without-using-them/200467
22. https://support.claude.com/en/articles/15910845 (limits unpublished; secondary sources conflict)
