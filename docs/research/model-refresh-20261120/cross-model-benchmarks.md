# Cross-model benchmarks: quality per cost and effort, 2026-11-20

Scope: independent, cross-vendor measurements for Claude Fable 5.2, Opus 5.5, Sonnet 5.5, Haiku 5.5; GPT-6.2 Astra, GPT-6.2 Sol, GPT-6.1 Sol, GPT-6.1 Terra, GPT-6 Luna; Gemini 4 Carbon, Neon, Hydrogen, Argon, Gemini 3.8 Flash. Vendor-by-vendor detail lives in the sibling files. No model was run for this note. Every number below comes from a cited page as read on 2026-11-20. Rows marked "derived" are arithmetic on cited numbers. "Unknown" means no independent figure was found.

**Cost basis.** Unless stated otherwise, cost is the pay-per-token API list price per task, as measured by the benchmark operator, including its cache assumptions. That is not subscription credit or quota consumption. Token volume (tokens/task) is the closest proxy for quota, and it is listed where published.

## 1. Primary ranking: Artificial Analysis Coding Agent Index v2.1

Independent. 322 tasks (FrontierCode-AA 2.0: 132, Terminal-Bench 4.1: 66, SWE-Atlas-QnA-AA: 124). Three attempts per task, equal-weight average. Each entry is harness + model + effort. v2.1 shipped 2026-11-14 with a new cost method, so v2.0 numbers are **not comparable**. The table is ranked by Pareto position: no configuration is both cheaper and higher scoring than a "Frontier" row.

| # | Model + effort | Harness | Index | FC / TB / QnA | Cost/task | Tokens/task | Time | Pareto status |
|---|---|---|---|---|---|---|---|---|
| 1 | GPT-6.2 Sol xhigh | Codex | 50 | 40 / 58 / 51 | $0.90 | 3.26M | 12.6m | Frontier (best value above 45) |
| 2 | GPT-6.2 Sol medium | Codex | 45 | 36 / 49 / 50 | $0.57 | 2.28M | 8.4m | Frontier |
| 3 | GPT-6.2 Sol high | Codex | 47 | 38 / 54 / 51 | $0.76 | 2.96M | 10.6m | Frontier |
| 4 | GPT-6.1 Sol max | Codex | 52 | 42 / 54 / 60 | $1.51 | 4.33M | 21.9m | Frontier |
| 5 | Claude Fable 5.2 medium | Claude Code | 53 | 36 / 60 / 64 | $2.89 | 1.9M | 15.1m | Frontier |
| 6 | Gemini 4 Neon xhigh | Antigravity CLI | 58.64 | 43 / 65 / 68 | $6.86 | 13.8M | 30.5m | Frontier (top score; see §5 degradation) |
| 7 | Claude Fable 5.2 high | Claude Code | 58.24 | 49 / 64 / 62 | $7.51 | 5.12M | 31.3m | Tie with #6 within variance |
| 8 | GPT-6.2 Sol low | Codex | 37 | 28 / 41 / 42 | $0.33 | 1.31M | 7.2m | Frontier (low quality) |
| 9 | GPT-6.2 Astra high | Codex | 52 | 42 / 60 / 55 | $2.37 | 2.26M | 15.8m | Dominated by #4 |
| 10 | GPT-6.2 Astra xhigh | Codex | 53 | 43 / 62 / 54 | $3.20 | 3.09M | 16.5m | Dominated (narrowly) by #5 |
| 11 | GPT-6.2 Astra medium | Codex | 49 | 40 / 54 / 54 | $1.20 | 1.02M | 11.6m | Dominated by #1 |
| 12 | GPT-6.2 Sol max | Codex | 49 | 42 / 58 / 46 | $1.22 | 4.25M | 17.5m | Dominated by its own xhigh |
| 13 | GPT-6.1 Terra max | Codex | 49 | 41 / 51 / 54 | $1.53 | 14.4M | 28.1m | Dominated |
| 14 | Gemini 4 Hydrogen xhigh | Antigravity CLI | 52 | 37 / 60 / 60 | $4.45 | 18.5M | 32.1m | Dominated |
| 15 | GPT-6.2 Astra max | Codex | 53.47 | 42 / 64 / 55 | $5.12 | 4.67M | 25.1m | Dominated |
| 16 | Claude Opus 5.5 max | Claude Code | 58.16 | 44 / 65 / 66 | $12.61 | 15.9M | 1.1h | Dominated: same score as #7 at 1.7x cost |
| 17 | Claude Sonnet 5.5 max | Claude Code | 56 | 39 / 66 / 64 | $11.40 | 26.4M | 1.4h | Dominated |
| 18 | Gemini 4 Carbon high | Antigravity CLI | 55 (≈55.4) | 38 / 65 / 64 | $9.75 | 15.4M | 33.6m | Dominated by #6 |
| 19 | Claude Fable 5.2 xhigh | Claude Code | 58.47 | 49 / 64 / 62 | $15.47 | 9.75M | 53.3m | +0.2 over high for 2.06x cost |
| 20 | Claude Fable 5.2 low | Claude Code | 48 (47.96) | 31 / 53 / 60 | $2.49 | 1.64M | 13.4m | Dominated |
| 21 | Gemini 4 Argon high | Antigravity CLI | 45 | 25 / 57 / 55 | $6.84 | 16.4M | 37.7m | Dominated |
| 22 | GPT-6.2 Astra low | Codex | 36 (35.58) | 27 / 44 / 36 | $0.70 | 551k | 7.8m | Dominated |
| 23 | Claude Haiku 5.5 max | Claude Code | 30 | 23 / 32 / 34 | $2.25 | 12.4M | 1.3h | Dominated |
| 24 | GPT-6 Luna max | Codex | 26 | 24 / 15 / 38 | $0.19 | 10.1M | 23.5m | Frontier at the bottom only |
| 25 | Claude Fable 5.2 max | Claude Code | 55.74 | 44 / 63 / 60 | $44.22 | 24M | 2.2h | Worst value: regresses vs high |

Not measured on v2.1 (**unknown**): Opus 5.5 below max, Sonnet 5.5 and Haiku 5.5 below max, Neon below xhigh, Carbon other than high, Hydrogen below xhigh, Gemini 3.8 Flash, Luna below max, Terra below max. Rows 6, 7, 16 and 19 use two-decimal scores from OrcaRouter's 2026-11-19 reading. The rest are rounded scores from the AA comparison pages.

Marginal cost along the frontier (derived): Sol low → medium costs about $0.03 per index point. Medium → xhigh costs about $0.07/pt. Sol xhigh → 6.1 Sol max costs about $0.31/pt. 6.1 Sol max → Fable medium costs about $1.38/pt. Fable medium → Neon xhigh costs about $0.71/pt.

## 2. Corroborating cross-model measurements

### 2a. CursorBench 4.0, per effort (Cursor agent harness; via aggregator, 2026-11-19)

| Model | low | medium | high | xhigh | max |
|---|---|---|---|---|---|
| Fable 5.2 | 53.2% / $3.94 | 54.8% / $4.66 | 56.9% / $9.70 | 56.3% / $15.48 | **60.0% / $32.79** |
| Opus 5.5 | 43.7% / $1.17 | 52.5% / $2.91 | **56.0% / $3.97** | 56.0% / $6.98 | 57.8% / $13.43 |
| Sonnet 5.5 | 35.8% / $0.37 | 39.2% / $0.52 | 47.8% / $1.20 | 53.1% / $2.81 | 55.5% / $7.05 |
| Haiku 5.5 | 30.9% / $0.08 | 36.9% / $0.17 | 42.3% / $0.32 | 44.3% / $0.56 | **48.4% / $1.12** |
| Gemini 4 Argon | 50.6% / $4.09 | 52.8% / $4.39 | 52.9% / $4.57 | n/a | n/a |

No GPT-6.x rows exist. Gemini 4 Carbon high is 60.4% per Cursor's own announcement, with no cost given. The board publishes no uncertainty.

### 2b. Vals Terminal-Bench 4.0 (uniform mini-swe-agent harness, avg@3, 66 tasks, updated 2026-11-18)

Cost per solved task is derived as cost/test ÷ accuracy. It assumes failures cost the same as successes and that retries are independent. It is optimistic on hard tasks.

| Model | Accuracy | Cost/test | Cost per solved (derived) | Duration |
|---|---|---|---|---|
| GPT-6.2 Sol | 60.61% | $1.13 | $1.86 | 23m |
| GPT-6 Luna | 13.64% | $0.35 | $2.57 | 33m |
| GPT-6.1 Sol | 55.05% | $1.72 | $3.12 | 45m |
| GPT-6.1 Terra | 49.49% | $2.16 | $4.36 | 34m |
| GPT-6.2 Astra | 63.13% | $4.69 | $7.43 | 34m |
| Claude Haiku 5.5 | 36.36% | $3.12 | $8.58 | 52m |
| Gemini 4 Neon | 61.62% | $6.42 | $10.42 | 36m |
| Gemini 4 Carbon | 63.13% | $7.45 | $11.80 | 45m |
| Gemini 4 Hydrogen | 54.04% | $7.56 | $13.99 | 31m |
| Claude Sonnet 5.5 | 64.14% | $10.75 | $16.76 | 1h22m |
| Claude Opus 5.5 | 65.15% | $12.04 | $18.48 | 1h04m |
| Claude Fable 5.2 | 65.15% | $14.56 | $22.35 | 55m |
| Gemini 4 Argon | 57.58% | $17.64 | $30.64 | 54m |
| Gemini 3.8 Flash | 19.70% | $8.65 | $43.91 | 1h47m |

### 2c. AA Intelligence Index v5 (general, not coding-only; per effort)

| Model | low | medium | high | xhigh | max |
|---|---|---|---|---|---|
| GPT-6.2 Sol | 41 / $0.18 | 53 / $0.41 | 55 / $0.56 | 56 / $0.65 | 57 / $1.01 |
| Claude Opus 5.5 | 35 / $0.98 | 48 / $2.45 | 52 / $3.46 | 57 / $6.05 | 59 / $10.04 |
| GPT-6.2 Astra | 46 | 57 | 60 | 62 | 62 / $4.00 |
| Claude Fable 5.2 | 54 | 56 | 62 | 62 | 65 / $26.54 |
| Gemini 4 Neon | 44 | 55 | 60 | 61 / $6.44 | n/a |
| Gemini 4 Hydrogen | 27 | 41 | 51 | 54 / $3.16 | n/a |
| Claude Haiku 5.5 | 19 | 25 | 30 | 35 | 36 / $0.41 |
| Gemini 4 Carbon | — | — | 59 / $7.76 (2026-10-28) | — | — |
| Gemini 3.8 Flash | $0.58/task at its default setting (score not captured) | | | | |

Costs not shown are not published per effort.

### 2d. Other independent boards

| Source (date) | Metric | Results |
|---|---|---|
| FrontierCode 2.0 (Cognition; BenchLM snapshot 2026-11-19) | rubric score, best published effort | Fable 5.2 xhigh 50.2; Opus 5.5 max 47.3; Neon high 46.2; Astra 6.2 max 44.2; Sol 6.2 max 43.8; Carbon high 42.6; Sonnet 5.5 max 42.2; Sol 6.1 max 39.6; Hydrogen xhigh 38.9; Haiku 5.5 max 28.9; Argon high 27.6; Luna max 22.7 |
| Vals Index v2.2 (2026-11-18) | score / cost per test | Fable 71.31 / $17.94; Neon 70.87 / $7.40; Sonnet 70.85 / $20.80; Carbon 70.36 / $10.51; Opus 70.18 / $32.77; Hydrogen 68.49 / $9.84; Astra 67.66 / $10.68; Sol 6.2 66.06 / $3.18; Terra 60.17 / $2.92; Luna 58.45 / $0.42; Haiku 54.31 / $2.99; Flash 54.83 / unknown |
| Arena WebDev (2026-11-20) | Elo (human votes, no CI shown) | Fable xhigh 1823; Opus max 1818; Sonnet xhigh 1771; Carbon high 1769; Neon high 1763; Astra max 1759; Sol 6.2 max 1755; Sol 6.1 max 1744; Sonnet high 1716; Hydrogen high 1701 |
| Bito replay (2026-11-18; 8 hard 5-turn sessions per model, judge with answer keys) | hard-session score / cost | Opus medium 84.1% / $5.40; Fable medium 81.0% / $8.13; Astra high 76.9% / $8.19; Sol 6.2 high 75.8% / $2.22; Sol 6.1 medium 73.4% / $2.06; Astra low 69.1% / $4.86; Sonnet medium 68.3% / $1.28; Sol 6.2 low 67.3% / $1.22; Haiku medium 66.5% / $0.69; Carbon 76.3% / $2.75 (run through Claude Code, effort not stated) |

## 3. What the evidence supports and does not support

**Supported, high confidence.**
- **GPT-6.2 Sol at xhigh is the best value per task among strong agents.** It scores CAI 50 at $0.90, TB4 60.6% at $1.13, and Bito 75.8% at $2.22 (high). Its derived cost per solved Terminal-Bench task ($1.86) is about 4x below Astra and about 10x below Opus or Fable.
- **The effort curve flattens above high, and max often regresses in agentic runs.**
  - Fable 5.2 on CAI: high 58.24 → xhigh 58.47 (+0.2, 2.06x cost) → max 55.74 at $44.22, because attempts hit time limits.
  - Sol 6.2 on CAI: xhigh 50 → max 49 (SWE-Atlas falls 51 → 46).
  - Astra on CAI: xhigh 53 → max 53.47 at 1.6x cost.
  - CursorBench: Opus 5.5 high equals xhigh (56.0%), and Fable 5.2 xhigh scores below high.
  - Low → medium/high is where most of the gain sits: Sol 37 → 47 and Astra 36 → 52 on CAI; Opus 43.7 → 56.0 on CursorBench; Bito +8 points for both GPT-6.2 models.
- **Prefer a weaker model at higher effort over a stronger model at low effort.** This holds in every head-to-head found:
  - Sol 6.2 medium (45, $0.57) beats Astra low (36, $0.70).
  - Sol 6.2 xhigh (50, $0.90) beats Fable low (48, $2.49).
  - On CursorBench, Haiku max (48.4%, $1.12) and Sonnet high (47.8%, $1.20) beat Opus low (43.7%, $1.17), and Opus high (56.0%, $3.97) beats Fable low (53.2%, $3.94).
  - In Bito, Sol high beats Astra low by 6.7 points at under half the cost.
- **The Astra 6.2 premium over Sol 6.2 is small.** It is +1 to +3 points on CAI, TB4 and Bito at 3–4x the cost. OpenAI's own claim (Sol within 0.5 on FrontierCode 2.0) is consistent with the independent FrontierCode gap of 0.4.

**Supported, medium confidence.**
- **The top cluster is a statistical tie.** Fable 5.2 high/xhigh, Opus 5.5 max, Neon xhigh and Devin Fusion all score 58 on CAI. The v2.1 write-up treats 58 vs 56 as one class. Vals TB4 ties Fable and Opus at 65.15%.
- **Within Claude Code, Fable 5.2 at high is not more expensive than Opus 5.5 at max.** On CAI it costs $7.51 vs $12.61 with the same score and a third of the tokens (5.1M vs 15.9M). Fable 5.2 medium (53, $2.89) is on the frontier. This contradicts the assumption that Fable is a pure cost premium. It is contested by Bito, where Opus medium beat Fable medium by 3.1 points at $5.40 vs $8.13, and by CursorBench, where Opus high dominates Fable low and medium.
- **The frontier models' edge is concentrated in maintainer-quality multi-file changes.** Fable leads FrontierCode by 3–5 points: FC-AA 49 vs Opus 44, and FrontierCode 2.0 50.2 vs 47.3. Terminal work is flat across the top: TB4.1 ranges 63–66 for Fable, Opus, Sonnet, Neon, Carbon and Astra.
- **For repository question answering (closest to code review and investigation), Opus 5.5, Neon and Sonnet lead.** SWE-Atlas-QnA scores are Opus 66, Neon 68, Sonnet 64 and Fable 62. Sol 6.2 is the weakest strong model there (46–51), below Sol 6.1 (60). Sol 6.2's CAI deficit vs 6.1 comes almost entirely from this component.
- **Gemini 4 Carbon is not justified over Neon on cost.** Carbon is dominated by Neon on CAI (55 at $9.75 vs 58.6 at $6.86), on Vals Index, and on FrontierCode. Only CursorBench, via Cursor's own announcement, puts Carbon first (60.4%).
- **Haiku 5.5 is a strong IDE-edit model but a poor long-horizon terminal agent.** It scores CursorBench max 48.4% at $1.12, but only 30 on CAI at $2.25 and 36.4% on TB4. Long runs make it expensive per solved task ($8.58).

**Supported, low confidence.**
- Astra and Fable lead on general reasoning (Intelligence Index 62 and 65 vs Sol 57 and Opus 59), which may matter for architecture and planning. No coding-specific architecture benchmark isolates this.
- High effort reduces misleading claims: in Bito, Sol 0.62 → 0.23 per answer and Astra 0.70 → 0.35. That is n=8 sessions.

**Not supported or unknown.**
- **Cost per validated task including retries:** no independent source publishes it. The §2b column is a derived upper bound on efficiency, not a measurement.
- **METR time horizons:** none published for any of these models. Long-horizon claims rest only on CAI and TB4 wall times. Opus max takes 1.1h per task, and Fable max takes 2.2h and hits limits.
- **SWE-bench Pro:** there are no standardized Scale entries for these models. The widely quoted Opus 5.5 89.9% is a vendor-aggregate figure and is not comparable to Scale's public board, where the leader scores 61.5%.
- LiveCodeBench, Aider polyglot and LiveBench are stale or unverifiable for these models.
- The earlier baseline claim that Haiku 5.5 costs $0.21 vs Luna $0.07 per AA task was not re-found. AA now shows Haiku max at $0.41 per Intelligence Index task.
- There is no independent per-effort coding data for Opus 5.5 below max on CAI, nor for Neon below xhigh, Hydrogen below xhigh, or Gemini 3.8 Flash on any agent board.

## 4. Benchmark limitations and contradictions

- **Harness confound.** CAI scores harness + model + effort together: Claude Code vs Codex vs Antigravity CLI. Vals uses one neutral harness (mini-swe-agent), and there Sol 6.2 is cheaper and Haiku is costlier than in native tools. Same-model harness swaps moved cost per merged feature about 2.5x in an earlier study (Insight, 2026-07).
- **Small samples.**
  - TB4 has 66 tasks, so one task is 1.5 points.
  - Bito has 8 hard sessions per model.
  - CAI and Vals average 3 attempts.
  - Neither CursorBench nor Arena WebDev shows confidence intervals.
- **Version breaks.** CAI v2.0 → v2.1 (2026-11-14) lowered scores by about 5 points and changed the cost method. The prior-evidence comments in `routingctl.py` cite v2.0: Opus 61.7 at $11.42 and Sol 6.1 54.1 at $1.50. Those numbers are not comparable to anything above.
- **List price vs credits.** AA and Vals costs are API list prices with assumed cache rates. Subscription quota burn follows tokens and time more than dollars. Neon xhigh and Hydrogen xhigh use 14–18M tokens per task, against Fable high at 5M and Sol xhigh at 3M.
- **Contradictions between sources.**
  - **Fable vs Opus:** AA favors Fable high on cost, Bito favors Opus medium, and CursorBench favors Opus high on value but Fable max on peak score.
  - **Carbon vs Neon:** AA, Vals and FrontierCode put Neon ahead. CursorBench (Cursor) puts Carbon ahead.
  - **Carbon cost:** AA CAI $9.75/task, AA Intelligence Index $7.76 (at $4/$20 pricing), Bito $2.75/session. The Bito run is in an atypical harness.
  - **Sol 6.2 vs 6.1:** 6.2 is lower on CAI (SWE-Atlas) but higher on TB4 (60.6 vs 55.1), FrontierCode (43.8 vs 39.6) and Bito.
  - **Vals internal inconsistencies:** Opus TB4 61.62% vs 65.15%, and Sonnet TB4 53.03% vs 64.14% on different Vals pages.
  - **Effort monotonicity:** CursorBench rewards max for every Claude model, while CAI penalizes Fable and Sol at max.
- **Contamination.** OpenAI stopped reporting SWE-bench Verified (2026-02-23). Epoch rates it "Flawed" (2026-09-03), and every frontier model it tested had seen some problems and solutions in training. Any Verified number is excluded here.
- **Aggregator noise.** Several secondary sites mislabel versions (GPT-6 vs GPT-6.2, Fable 5.1 vs 5.2). Rows here come from AA, Vals and Arena pages or from snapshots that name both effort and harness.

## 5. Degradation and routing changes since 2026-11-15

- **Gemini 4 on Antigravity (user reports, unconfirmed by Google).** Threads from 2026-11-16 to 2026-11-19 report sharp drops on Ultra accounts across Carbon, Neon, Hydrogen and Argon:
  - Carbon high fell from a median of 31 tool calls and 510 s per turn to 1 call and 15 s after 2026-11-17 09:35 UTC.
  - Thinking tokens fell 3–4x from the evening of 2026-11-18 UTC, and a structural check dropped from 169/190 passes to 2/24.
  - Reported side effects: `THINKING_LEVEL_XHIGH` rejected, and context recall failing above about 126K tokens.
  - Sonnet 5.5 in the same CLI was unaffected, and Pro accounts were reported unaffected.
  - One reporter saw recovery at about 13:00 UTC on 2026-11-19, either after the desktop app update to 2.33.0 or from a server-side change.
  - Neon's AA reading (2026-11-19) may not reflect what an affected account receives.
- **Opus 5.5 (Claude Code).** One user's transcript analysis reports corrected answers rising from 5.2% to 25.4% after 2026-10-19. The LiveNerf and NerfBench trackers showed no change through 2026-11-04. No data after 2026-11-15 and no Anthropic postmortem were found.
- **OpenAI.** A Codex issue reports GPT-6.1 Sol "high" behaving like minimal effort on some requests (per-request, unconfirmed). Nothing was found for GPT-6.2 since its 2026-11-17 release.

## 6. Recommended ordering by work level (candidates, cheapest sufficient first)

| Level | Codex | Claude Code | Antigravity | Basis / confidence |
|---|---|---|---|---|
| economy | Sol 6.2 low → medium ($0.33–0.57, CAI 37–45); Luna only for well-specified edits (CAI 26, TB4 13.6%) | Haiku 5.5 medium → high (CursorBench 36.9–42.3% at $0.17–0.32; Bito medium 66.5% at $0.69) | Hydrogen low/medium: coding **unknown** (Intelligence Index 27/41); avoid Flash 3.8 for agentic work (TB4 19.7%, $8.65) | medium |
| standard | Sol 6.2 medium → high ($0.57–0.76) | Sonnet 5.5 high ($1.20, 47.8%) or Haiku 5.5 max ($1.12, 48.4%) for IDE-style edits; not Haiku for long terminal tasks | Hydrogen high: coding **unknown** | medium |
| advanced | Sol 6.2 xhigh ($0.90, CAI 50); GPT-6.1 Sol max for repo Q&A or review (SWE-Atlas 60, $1.51) | Opus 5.5 medium ($2.91, 52.5%; Bito 84.1%) ≈ Sonnet 5.5 xhigh ($2.81, 53.1%); Fable 5.2 medium (CAI 53, $2.89) is a credible alternative | Hydrogen xhigh (CAI 52, $4.45) | medium |
| strong | Astra 6.2 high/xhigh (CAI 52–53, $2.37–3.20) only when Sol xhigh failed; otherwise Sol 6.2 xhigh again | Opus 5.5 high ($3.97, 56.0%; xhigh adds nothing on CursorBench) | Neon high/xhigh (CAI xhigh 58.6, $6.86; high **unknown**); check for degradation | medium |
| max | Astra 6.2 xhigh (not max: +0.5 at 1.6x). Sol 6.2 max is below xhigh, so do not route it | Opus 5.5 max (CAI 58, $12.61). Fable 5.2 high reaches the same CAI score at $7.51, which is worth testing locally | Neon xhigh | medium–low |
| frontier | Astra 6.2 xhigh (Intelligence Index 62); evidence of a coding premium over Sol is 1–3 points | Fable 5.2 high (CAI 58, FrontierCode lead). Use xhigh/max only for maintainer-quality multi-file work: CursorBench max is 60.0% at $32.79, but CAI max regresses to 55.7 at $44.22 | Carbon high: not supported over Neon by independent boards (dominated on CAI) | low–medium |

Operational reading: escalate effort to high or xhigh before changing model. Skip low effort on frontier models. Treat max as a deliberate, time-limit-aware choice, not a default. Validate the Fable-high-vs-Opus-max cost inversion in the repository's frozen routing-eval replay before changing the tier map.

## Sources (accessed 2026-11-20 unless noted)

- AA Coding Agent Index v2.1, Codex and Antigravity rows: https://artificialanalysis.ai/agents/coding-agents/comparisons/antigravity-cli-vs-codex
- AA Coding Agent Index v2.1, Claude Code rows: https://artificialanalysis.ai/agents/coding-agents/comparisons/claude-code-vs-codex
- AA index methodology (components, 3 attempts): https://artificialanalysis.ai/agents/coding-agents/
- AA model pages (Intelligence Index per effort): https://artificialanalysis.ai/models/gpt-6-2-sol, https://artificialanalysis.ai/models/gpt-6-2-astra, https://artificialanalysis.ai/models/claude-fable-5-2, https://artificialanalysis.ai/models/claude-opus-5-5, https://artificialanalysis.ai/models/claude-haiku-5-5, https://artificialanalysis.ai/models/gemini-4-neon, https://artificialanalysis.ai/models/gemini-4-hydrogen
- AA, Gemini 4 Carbon article (2026-10-28): https://artificialanalysis.ai/articles/gemini-4-carbon-new-number-1
- CAI v2.1 change write-up (2026-11-15): https://dev.to/piekwerk/coding-agent-index-v21-scores-fell-5-points-4-configs-tie-at-58-and-cost-per-task-spans-30x-1c1c
- OrcaRouter, two-decimal CAI v2.1 reading and effort ladders (2026-11-19): https://www.orcarouter.ai/blog/gemini-4-neon-coding-agent-index
- CAI v2.0 (2026-10-23, superseded): https://cellcog.ai/blog/artificial-analysis-coding-agent-index/
- Kingy, Intelligence Index per-effort costs for Sol and Opus (2026-11-17): https://kingy.ai/blog/gpt-6-2-sol-vs-claude-opus-5-5/
- DataCamp, vendor vs independent split for Sol and Opus (2026-11-18): https://www.datacamp.com/blog/gpt-6-2-sol-vs-claude-opus-5-5
- Vals Terminal-Bench 4.0 (2026-11-18): https://www.vals.ai/benchmarks/terminal-bench-4
- Vals Index v2.2 (2026-11-18): https://www.vals.ai/home
- CursorBench 4.0 per effort (aggregator, 2026-11-19): https://llmlearner.com/rankings/cursorbench-v4-0 and https://benchlm.ai/benchmarks/cursorbench
- Cursor, Carbon 60.4% announcement: https://x.com/cursor_ai/status/2120193584670580857
- FrontierCode 2.0 snapshot (2026-11-19): https://benchlm.ai/benchmarks/frontiercode-2
- Arena WebDev (2026-11-20): https://arena.ai/leaderboard/code/webdev
- Bito replay (2026-11-18): https://bito.ai/blog/gpt-6-2-sol-astra-vs-claude-opus-fable-gpt-6-1-sol/
- DataCamp, Haiku 5.5 vs Luna (vendor table plus a small test): https://www.datacamp.com/blog/claude-haiku-5-5-vs-gpt-6-luna
- SWE-bench Pro, standardized vs vendor figures: https://www.morphllm.com/swe-bench-pro and https://scale.com/blog/swe-bench-pro
- OpenAI, why it no longer evaluates SWE-bench Verified (2026-02-23): https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/
- Epoch, SWE-bench Verified review (2026-09-03): https://epoch.ai/benchmarks/swe-bench-verified/review
- METR, time-horizon limitations (no data for these models): https://metr.org/notes/2026-01-22-time-horizon-limitations/
- Gemini 4 degradation threads (2026-11-16 to 2026-11-19): https://discuss.ai.google.dev/t/severe-intelligence-degradation-across-all-models-since-november-15-is-google-routing-requests-to-inferior-models/201295 and https://discuss.ai.google.dev/t/gemini-4-hydrogen-carbon-argon-neon-think-3-4x-less-since-nov-18-evening-utc-xhigh-rejected-cli-1-5-11-ultra/202317
- Opus 5.5 trackers vs complaints (2026-11-07, updated 2026-11-11): https://i10x.ai/news/claude-opus-5-5-nerf-complaints-data
- Codex effort issue (GPT-6.1 Sol): https://github.com/openai/codex/issues/57021
- Cost per merged feature across harnesses (2026-07-06): https://blog.apac.insight.com/2026/07/06/cost-to-a-merged-feature
