# Model mapping refresh — 2026-11-20

## Final remap (map `2026-11-20-v11`, bootstrap catalog `2026-11-20-bootstrap-v9`)

This section supersedes the per-level table and the Codex `standard` decision further down. It applies the five research reports of 2026-11-20 (no model calls were made for them):

- [openai-codex.md](model-refresh-20261120/openai-codex.md) — Codex models and efforts, Terra vs Sol break-even
- [anthropic-claude.md](model-refresh-20261120/anthropic-claude.md) — Haiku/Sonnet/Opus/Fable efforts, minimum Claude Code versions
- [google-antigravity.md](model-refresh-20261120/google-antigravity.md) — Gemini 4 Neon/Hydrogen/Carbon/Argon, Flash 3.8, Antigravity Claude
- [cross-model-benchmarks.md](model-refresh-20261120/cross-model-benchmarks.md) — Artificial Analysis Coding Agent Index v2.1 Pareto ranking, CursorBench, Vals, Bito
- [other-providers.md](model-refresh-20261120/other-providers.md) — GLM, DeepSeek, Muse, Qwen, Kimi, Trae

| Level | Claude Code | Codex | Antigravity (opt-in overlay) |
| --- | --- | --- | --- |
| economy / L1 | `claude-haiku-5-5` low (medium when an exploration miss is costly) | `gpt-6.2-sol` low | Gemini 4 Hydrogen low; Flash 3.8 medium for monitoring only |
| standard / L2 | `claude-sonnet-5-5` medium -> high | `gpt-6.2-sol` medium | Gemini 4 Neon low/medium first; Hydrogen as fallback |
| advanced / L3 | skipped upward (Opus medium) | skipped upward (Sol high) | Gemini 4 Neon high; Antigravity Claude Opus 5.5 capped here |
| strong / L4 | `claude-opus-5-5` medium -> high | `gpt-6.2-sol` high | Gemini 4 Neon high -> xhigh |
| max / L5 | `claude-opus-5-5` xhigh | `gpt-6.2-sol` xhigh | not routed |
| frontier / L6 | `claude-fable-5-2` high (Claude Code >= 2.1.321) | `gpt-6.2-astra` high -> xhigh (Codex >= 0.171.0) | Carbon only if listed; never preset |

Ladders: Claude Haiku low -> Haiku medium -> Sonnet medium -> Sonnet high -> Opus medium -> Opus high -> Opus xhigh; Codex Sol low -> Sol medium -> Sol high -> Sol xhigh. `max` effort and Codex `ultra` are never defaults.

Key evidence (Coding Agent Index v2.1 unless noted; details and confidence in `skill/plan-and-execute/references/MODEL_MAPPING.md` §6 and the review's "Decisions made while applying (final remap)"):

- **GPT-6.1 Terra has no coding role any more.** Terra max 49 at $1.53 with 14.4M tokens vs Sol 6.2 xhigh 50 at $0.90 with 3.26M; Terminal-Bench 4.1 53.3% vs 61.5%; Vals Terminal-Bench 4.0 49.5% at $2.16 vs 60.6% at $1.13. At half Sol's per-token price, Terra only wins below 2x Sol's tokens at equal quality, which no coding measurement shows. The earlier "Terra 48 at $0.69 vs Sol 54 at $1.50" was Coding Agent Index v2.0, not comparable with v2.1.
- **GPT-6 Luna is not a tier model:** 26 at max, Terminal-Bench 13-15%; OpenAI says start it at High while economy floors dispatch low. Sol 6.2 low is 37 at $0.33.
- **Effort ceilings:** Sol 6.2 max 49 < xhigh 50; Fable 5.2 max 55.74 at $44.22 < high 58.24 at $7.51; Astra max 53.47 at $5.12 vs xhigh 53 at $3.20; CursorBench Opus high 56.0% = xhigh 56.0%.
- **Antigravity:** at equal cost per Intelligence Index task Neon one effort lower beats Hydrogen (low 44 $0.75 vs medium 41 $0.80; medium 55 $1.90 vs high 51 $1.87); Neon xhigh 58.64 at $6.86 vs Hydrogen xhigh 52.32 at $4.45 and Carbon high 55.47 at $9.75. Medium-low confidence.
- **Open question:** Fable 5.2 high ties Opus 5.5 max on the index at about 60% of the cost (58.24 at $7.51 vs 58.16 at $12.61), while Bito's replay favours Opus medium over Fable medium. The owner policy keeps Fable as the frontier level; the frozen `routing-eval` replay should settle it.

## Owner policy update (final)

This section supersedes anything below that conflicts with it, including the "recorded task-scoped approval" wording in plan task 105 (`PLAN1_SPEC.json`, `TASK_INPUTS.json`) and in `docs/research/20261028-skill-optimization/PLAN_ARCHITECTURE_REVIEW_20261120.md` (A9, B105, B107). Implemented as map `2026-11-20-v10` / bootstrap catalog `2026-11-20-bootstrap-v8` and kept unchanged by the final remap (v11 / bootstrap-v9) above.

- **Opus 5.5 and Sol 6.2 are the usual ceiling** (`strong` and `max` by effort). Claude Fable 5.2 (`claude-fable-5-2`) and GPT-6.2 Astra (`gpt-6.2-astra`) form a sixth, first-class level `frontier` (aliases L6/F6) above `max`, a level above everything else, for special cases only.
- **Two ways in, nothing else, no per-task approval:** (1) architecture and code review of EXTREMELY hard demands — the leaf signals `extreme_architecture` / `extreme_code_review` (floor `max`/`xhigh` plus `frontier_eligible`), turned into a frontier route only for a read-only analyst/verifier role; (2) after Opus 5.5 / Sol 6.2 failed repeatedly on the same task at their top rung — `routing_policy.frontier.min_top_failures` (default 2) failures classed `semantic`, `mechanical` or `unknown` at max/xhigh, where the frontier route replaces the `ladder_exhausted` block (below the threshold the top rung is retried; a failed frontier attempt blocks for replanning).
- **Never:** floor lifting, an ordinary ladder rung, the selector, implementation/exploration/monitoring/DIRECT work, or quota, auth, billing, environment, budget and timeout outcomes. Codex credit exhaustion is availability: skip to Fable 5.2 without recording an escalation. Claude Code < 2.1.321 (vendor minimum; was recorded as 2.1.290) answering HTTP 400 for Fable 5.2 is version unavailability (skipped, no escalation). Explicit provider overrides and `allow_provider_fallback: false` are honoured.
- **Efforts:** Fable 5.2 `high` (`xhigh` only where measured); Astra `high`, never Codex `ultra`; `gemini-4-carbon-*` only if `agy models` lists it (never preset).
- **Configuration:** `routing_policy.frontier = {enabled: true, min_top_failures: 2}` (enabled by default per owner decision); `<provider>.frontier = {model, effort}`.
- **Representation:** `TIER_ORDER` keeps five persisted tiers; `LEVEL_ORDER` adds `frontier` for aliases, documentation and catalog validation. A frontier dispatch persists `tier: "max"` plus `level: "frontier"` and `frontier: true` in the manifest route, telemetry and availability ledger, so schema 1-4 manifests, five-tier validators and golden argv stay valid; plans cannot pin `model_tier: frontier`.
- **Plan task 105** must build on this frontier route (`routingctl.FRONTIER_*`, `frontier_stage`, `run_isolated.frontier_route`, `frontier_self_test.py`) instead of re-implementing it; its approval gate and the "only semantic/plan_defect count, unknown never" rule are superseded by the rules above.
- **Codex standard (superseded by the final remap):** v10 kept `gpt-6.1-terra` Medium pending a research pass; that pass ([openai-codex.md](model-refresh-20261120/openai-codex.md)) found no coding role for Terra, so v11 routes `gpt-6.2-sol` on every Codex tier.

v10 table (historical; see the final remap above):

| Level | Claude Code | Codex | Antigravity (opt-in overlay) |
| --- | --- | --- | --- |
| economy / L1 | `claude-haiku-5-5` low | `gpt-6-luna` low | Gemini 4 Hydrogen; Flash 3.8 for monitoring |
| standard / L2 | `claude-sonnet-5-5` medium | `gpt-6.1-terra` medium | Gemini 4 Hydrogen |
| advanced / L3 | skipped upward | skipped upward | Gemini 4 Neon; Antigravity Claude capped here |
| strong / L4 | `claude-opus-5-5` medium/high | `gpt-6.2-sol` medium/high | Gemini 4 Neon |
| max / L5 | `claude-opus-5-5` xhigh | `gpt-6.2-sol` xhigh | not routed |
| frontier / L6 | `claude-fable-5-2` high | `gpt-6.2-astra` high | Carbon only if listed; never preset |

## Antigravity update (2026-11-20)

- Installed `agy` CLI 1.5.13 (changelog mirrors show up to 1.5.12). `agy models` on this account is unchanged: `gemini-4-neon-{low,medium,high,xhigh}`, `gemini-4-argon-{low,medium,high}`, `gemini-4-hydrogen-{low,medium,high,xhigh}`, `gemini-pro-orchestrator-neon`, `gemini-pro-orchestrator-g1-pro` (Argon), `gemini-3.8-flash-*`, `claude-opus-5-5-*` / `claude-sonnet-5-5-*` (low/medium/high), `gpt-oss-120b-medium`. No `gemini-4-carbon-*`.
- Gemini 4 Neon became the Antigravity app default model on 2026-11-18 (low..xhigh). The Orchestrator (fixed effort) plans with Neon, Carbon or Argon and executes with Hydrogen; it is not effort-bearing and its headless behaviour is unverified, so it is not routed (optional future profile).
- agy CLI 1.5.10 rate-limit handling waits and retries delays up to 4 minutes; spend-cap, prepaid-balance and weekly-quota errors stop the turn immediately. `availability.py` now classifies those messages as quota/credits (availability, never capability), covered by `frontier_self_test.py`/`availability_self_test.py`.
- Auto-mode sandbox review on Hydrogen now uses medium thinking. With a `GEMINI_API_KEY`, `/usage`, `/quota` and `/credits` exit with code 2 in `-p` runs.
- Preset (v10): Neon at advanced–strong and Hydrogen at economy–standard. Changed by the final remap: Neon standard–strong first, Hydrogen economy plus standard fallback.

## Research baseline (historical; read with the final policy above)

Research baseline for map `2026-11-20-v8`. Scope: the logical-tier → model mapping for Claude Code, Codex and Antigravity, with quality-per-credit evidence. **Status: routing decision, not a head-to-head measurement for this repository.** Almost all benchmark numbers below come from secondary sources (aggregators, blogs, one independent replay with eight hard sessions per model). Treat them as direction; the frozen `docs/research/routing-eval` replay is the acceptance gate.

## Observed locally (2026-11-20)

| Host | Version | Observed |
| --- | --- | --- |
| Claude Code | 2.1.283 → 2.1.329 | `claude-haiku-5-5 --effort low` accepted; `haiku` alias still serves Haiku 4.5 (no effort); `claude-fable-5-2` returned HTTP 400 on 2.1.283 and ran on 2.1.329 (vendor minimum 2.1.321; the owner's pinned 2.1.322 also runs it); `fable` alias resolved to Fable 5.1 on the old CLI. |
| Codex | 0.159.2 → 0.171.0 | 0.171.0 lists `gpt-6.2-sol`, `gpt-6.2-astra`, `gpt-6.1-terra`, `gpt-6.1-sol` (previous generation), `gpt-6-luna`; effort `low..max` plus `ultra` (automatic delegation, never routed). No `gpt-6.2-luna`. |
| Antigravity `agy models` | current | `gemini-4-{neon,hydrogen}-{low,medium,high,xhigh}`, `gemini-4-argon-{low,medium,high}`, Orchestrator (Neon/Argon), `gemini-3.8-flash-*`, `claude-{opus,sonnet}-5-5-{low,medium,high}`, `gpt-oss-120b-medium`. **No `gemini-4-carbon-*`** (Ultra/Enterprise only). |

## Official facts (vendor pages, via search summaries)

- Anthropic: Fable 5.2 `claude-fable-5-2` $8/$40, 1M context, start at `high` (gains above are uneven); Opus 5.5 $4/$20, default effort `medium`; Sonnet 5.5 $2/$10; Haiku 5.5 $0.10/$0.50 (above 100K prompt tokens $0.50/$2.50), effort `low..max`. Mythos 5.2 is verification-gated.
- OpenAI (2026-11-17): `gpt-6.2-sol` $2/$10 (same as 6.1 Sol), `gpt-6.2-astra` $8/$40 ($0.40 cached). OpenAI states Sol is within 0.5 points of Astra on FrontierCode 2.0 at about one fifth of the cost. No `gpt-6.2-luna` announced.
- Google Antigravity (2026-11-10..19): Carbon (Ultra/Enterprise; planner/reviewer), Hydrogen ($1.50/$7.50, SDK default, fast/cheap), Neon ($3/$15, effort low..xhigh), Argon retained. Orchestrator = Carbon/Neon/Argon plans, Hydrogen implements. Claude 4.6 models removed from Antigravity 2026-11-18. Carbon's introductory $2/$10 ends 2026-11-30 ($4/$20 after).

## Benchmark evidence (secondary)

Independent replay (Bito, hard 5-turn sessions: eight per model; one-shot questions; judge with fixed keys; Codex for OpenAI models, Claude Code for Claude):

| Model | Effort | Hard-session score | Cost / hard session | Time |
| --- | --- | --- | --- | --- |
| Claude Opus 5.5 | medium | 84.1% (overall 85.0%) | $5.40 | 19.0 min |
| Claude Fable 5.2 | medium | 81.0% (83.1%) | $8.13 | 14.9 min |
| GPT-6.2 Astra | high | 76.9% (77.5%) | $8.19 | 25.8 min |
| GPT-6.2 Sol | high | 75.8% (76.5%) | $2.22 | 29.5 min |
| GPT-6.1 Sol | medium | 73.4% (74.8%) | $2.06 | 22.7 min |
| GPT-6.2 Astra | low | 69.1% | $4.86 | 16.4 min |
| GPT-6.2 Sol | low | 67.3% | $1.22 | 12.2 min |
| Claude Haiku 5.5 | medium | 66.5% (67.4%) | $0.69 | 8.1 min |
| Claude Sonnet 5.5 | medium | 68.3% (65.7%) | $1.28 | 8.6 min |
| Gemini 4 Carbon | n/s | 76.3% | $2.75 | n/s |

Effort effect (hard sessions, low → high): Sol 6.2 67.3% → 75.8% (output tokens about 20K → 53K); Astra 6.2 69.1% → 76.9% (about 20K → 38K).

Artificial Analysis (via Valyu, 2026-11-19): Coding Agent Index — Neon xhigh 58.64 ($6.86/task), Carbon high 55.47 ($9.75), Hydrogen xhigh 52.32 ($4.45), Argon high 45.50 ($6.84). Intelligence Index: Opus 5.5 ~59 ($10/task) vs Sol 6.2 ~57 ($1.01). Sonnet 5.5 coverage is thin and inconsistent across sources; Haiku 5.5 vs Luna: Haiku leads vendor tables but costs more per task when output tokens are counted ($0.21 vs $0.07 reported).

Known limits: tiny samples, harness and effort dependence, disagreement between sources on Carbon cost, vendor-run numbers mixed with independent ones, contamination risk on older SWE-bench variants, and anecdotal reports of degraded Gemini 4 output after 2026-11-15 that Google has not confirmed.

## Decisions

1. **Opus 5.5 and Sol 6.2 carry hard work** (`strong`, `max` by effort). Quality per credit favors them: Opus beat Fable 5.2 on the replay at about two thirds of the cost; Sol 6.2 tracked Astra 6.2 within about one point at about a quarter of the cost.
2. **Fable 5.2 / Astra 6.2 are a frontier level above `max`**, not part of the tier map. Owner policy: architecture and code review of extremely hard demands only, or after Opus/Sol failed repeatedly, never on quota/environment faults. Implemented in this refresh as the first-class level L6/F6 (see "Owner policy update (final)"); plan task 105 builds on it.
3. **Haiku 5.5 for economy** (accepts effort; the bare alias resolved to Haiku 4.5 on CLI 2.1.283, below Haiku 5.5's 2.1.293 minimum). Final remap: Sonnet 5.5 is clearly better for agentic coding (Coding Agent Index v2.1 56 vs 30 at max; Terminal-Bench 4.0 70.6% vs 39.2%), so it keeps `standard`; Haiku `medium` for exploration whose misses are costly, `low` only for short checkable tasks.
4. **Antigravity** (as revised by the final remap): Neon for standard–strong first, Hydrogen for economy and as the standard fallback (cheapest sufficient effort variant), Flash 3.8 stays for monitoring, Claude on Antigravity stays capped at advanced, Carbon is never preset (not on this account; dominated by Neon xhigh on the Coding Agent Index).
5. **Effort over model**: raise effort from failure evidence; avoid `max` and Codex `ultra` by default.
6. Terra (`gpt-6.1-terra`), resolved by the final remap: the v10 claim that Terra "has a measured role" rested on Coding Agent Index v2.0 (Terra 48 at $0.69 vs Sol 54 at $1.50) and vendor Agents' Last Exam figures; v2.0 is not comparable with v2.1, and every independent v2.1-era coding source puts Sol 6.2 ahead at the same or lower cost per task (see the final remap above). Terra is no longer routed; the owner's global config was updated to `gpt-6.2-sol` at standard.

## Sources

- https://platform.claude.com/docs/en/models/overview (Anthropic models and Fable 5.2 release notes)
- https://community.openai.com/t/gpt-6-2-astra-and-sol-are-now-available/1417531
- https://www.testingcatalog.com/openai-launches-gpt-6-2-astra-and-sol-on-chatgpt-and-apis/
- https://antigravity.google/docs/models
- https://www.gradually.ai/en/changelogs/antigravity/
- https://www.valyu.ai/blogs/gemini-4-neon-vs-carbon-vs-hydrogen-vs-argon
- https://bito.ai/blog/gpt-6-2-sol-astra-vs-claude-opus-fable-gpt-6-1-sol/
- https://www.datacamp.com/blog/gpt-6-2-sol-vs-claude-opus-5-5
- https://kingy.ai/blog/gpt-6-2-sol-vs-claude-opus-5-5/
- https://benchlm.ai/models/claude-fable-5-2
- https://www.datacamp.com/blog/claude-haiku-5-5-vs-gpt-6-luna
