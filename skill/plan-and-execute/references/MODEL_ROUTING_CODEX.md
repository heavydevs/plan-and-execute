# Codex model routing

Read only when Codex will execute the current work. `MODEL_ROUTING.md` owns provider-independent policy.

## Current capability map

Concrete ids live in `scripts/routingctl.py` `CURRENT_MODELS` (map version 2026-11-20-v11; frontier level in `FRONTIER_MODELS`); this table must match it. Verify what an installation actually serves with `codex debug models` (live catalog; `~/.codex/models_cache.json` can be stale).

GPT-6.2 Sol serves every Codex tier; the tiers differ by effort. Artificial Analysis Coding Agent Index v2.1 (independent, Codex harness, 2026-11-13) per Sol 6.2 effort: low 37 at $0.33/task, medium 45 at $0.57, high 47 at $0.76, xhigh 50 at $0.90, max 49 at $1.22.

| Tier | Model | Catalog description | Starting effort -> ceiling |
|---|---|---|---|
| `economy` | `gpt-6.2-sol` | "Fast, go-to model for coding and everyday work" | `low` (medium only when the floor asks for it) |
| `standard` | `gpt-6.2-sol` | same | `medium` |
| `advanced` | — (skipped upward to `strong`) | | |
| `strong` | `gpt-6.2-sol` | same | `medium` with strong validation, otherwise `high` |
| `max` | `gpt-6.2-sol` | same | `xhigh`; `max` effort is dominated (49 at $1.22 vs xhigh 50 at $0.90) and never a default |
| `frontier` (L6/F6) | `gpt-6.2-astra` | "Our most capable model for complex coding and professional work", $8 / $40 | `high` (52 at $2.37), then `xhigh` (53 at $3.20); never `low` (36), `max` (53 at $5.12) or `ultra` |

**Frontier level (L6/F6, above `max`):** `gpt-6.2-astra` is one level above everything else, for special cases only. Access rules (owner, final 2026-11-20; no per-task approval): reachable ONLY (1) through the leaf signals `extreme_architecture` / `extreme_code_review` on a read-only analyst/verifier role, or (2) after the `max` route failed `routing_policy.frontier.min_top_failures` times (default 2; classes semantic, mechanical or unknown) at the max/xhigh rung. Never by floor lifting, never as an ordinary ladder rung, never for implementation, exploration, monitoring or DIRECT work, never because of quota, auth, billing, environment, budget or timeout outcomes. The route persists `tier: max` with `level: frontier`, `frontier: true`; `routing_policy.frontier.enabled: false` restores the old `ladder_exhausted` block. See `MODEL_ROUTING.md` §6. Codex credit exhaustion on Astra is availability: the runner skips to Claude Fable 5.2 without recording an escalation.

Final remap (2026-11-20, `docs/research/model-refresh-20261120/openai-codex.md`):

- **GPT-6.1 Terra is no longer routed** (it replaced the owner decision of 2026-10-27). Every independent agentic-coding source that measures both puts Sol 6.2 ahead at the same or lower cost per task: Coding Agent Index v2.1 Terra max 49 at $1.53 with 14.4M tokens vs Sol 6.2 xhigh 50 at $0.90 with 3.26M (4.4x the tokens, 2.2x the time); Terminal-Bench 4.1 53.3% vs 61.5%; Vals Terminal-Bench 4.0 49.5% at $2.16 vs 60.6% at $1.13. Terra costs exactly half of Sol per token, so it only wins below 2x Sol's tokens at equal quality, which no coding measurement shows; one retry erases the gap. OpenAI now positions Terra for visual and computer-use work, and openai/codex#61538 reports it ending tasks early at High. The earlier "48 at $0.69 vs Sol 54 at $1.50" came from Coding Agent Index v2.0, which is not comparable with v2.1.
- **GPT-6 Luna is not a tier model**: Coding Agent Index 26 at max, Terminal-Bench 13-15%, and OpenAI says to start it at High, while economy floors dispatch `low`. Sol 6.2 Low (37 at $0.33) covers economy edits. Luna stays the cheap native read-only explorer below, at `high`.
- **Sol 6.2 vs 6.1:** 6.2 is better on Terminal-Bench, Vals and FrontierCode, but 3 points lower on the Coding Agent Index because of codebase Q&A (SWE-Atlas-QnA 51 vs 60). Keep `gpt-6.1-sol` as an opt-in alternate for read-heavy review or as a different-model retry after a 6.2 early stop (openai/codex#62195); it is not a default route.
- **Astra 6.2** costs 3-4x Sol for +1 to +3 points (CAI, Terminal-Bench, Bito replay), which is why it is the frontier level only.

Effort matters more than model here: GPT-6.2 Sol defaults to `medium` in `codex debug models`, and the skill starts standard work at `medium` because the worker must read and verify. Use **Sol High as the difficult-work baseline when verification is weak**, and Sol Medium when the task is bounded and objectively verifiable; Sol XHigh is the top rung. Efforts accepted (from the catalog): Luna `low`..`max`; Sol/Astra `low`..`max` plus `ultra`. The skill never selects `ultra` (maximum reasoning plus automatic subagents, 2.5x-12x the tokens in third-party reports) or `max` by default. Keep `service_tier = "default"` in `~/.codex/config.toml`: the 0.171.0 catalog sets Fast (2x usage) as the default tier for Astra 6.2 and Terra. `gpt-6.1-terra`, `gpt-6.1-sol`, `gpt-6-sol`, the previous-generation GPT-6 Astra and the GPT-5.6 line are not default routes.

Codex charges no cache writes and no long-context multiplier, and cached reads cost ~10% of input, so stable worker prefixes are cheap to reuse; `tool_output_token_limit` bounds how much tool output is kept in history.

## Elevation mechanics (how a route is actually obtained)

The skill never changes the thread's model (`/model` is the user's); it obtains a different tier by **delegation**:

| Need | Mechanism |
|---|---|
| Cheap read-only discovery | `spawn_agent` with the built-in `explorer` role and `model: gpt-6-luna` at `model_reasoning_effort: high` (OpenAI: start Luna at High; Luna Low is its weakest setting). Use `gpt-6.2-sol` Low instead when the discovery must not miss things or the task edits code. Explorers run `sandbox_mode: read-only`. |
| Stronger leaf from a smaller root | `spawn_agent` with the `worker` role, `model: gpt-6.2-sol`, and an explicit `model_reasoning_effort` (`medium` standard, `high` strong, `xhigh` max); a minimal prompt (task, paths/symbols, acceptance, validation). `gpt-6.2-astra` only under the frontier access rules above. |
| Reusable roles | `.codex/agents/<name>.toml` with `model`, `model_reasoning_effort`, `sandbox_mode`, `developer_instructions`; a custom agent named like a built-in overrides it. |
| Session-wide subagent defaults | `agents.default_subagent_model` and `agents.default_subagent_reasoning_effort` in `config.toml`; explicit spawn values win. Concurrency: `agents.max_concurrent_threads_per_session`. |
| Strong plan, cheap execution | `plan_mode_reasoning_effort` gives `/plan` its own effort; the skill's planning-stage routing achieves the same split by delegating planning leaves. |
| Budget guard | `features.rollout_budget.enabled` + `features.rollout_budget.limit_tokens` (the runner sets them from `codex.rollout_token_budget`). Enforcement (aborting the turn via `CodexErr::TurnAborted`) shipped 2026-06-19; the exact surfaced wording is not published, so the runner's pattern match is best-effort and an unmatched phrasing is classified `unknown` (safe: +1 rung) rather than `budget`. |

Subagent workflows consume more tokens than one agent doing the same work; spawn only when isolation, parallelism, or a different tier pays for itself.

## DIRECT mode

Small or medium-small work stays without a plan when it is cohesive. Model routing still applies:

- one-off lookup/build/test/lint -> deterministic tool, no subagent;
- broad read-only discovery -> Luna High explorer (Sol Low when a miss is costly);
- tiny mechanical edit with obvious local review or deterministic validation -> keep current useful context; delegate to Sol Low only when isolation actually saves context;
- normal bounded implementation with good validation -> Sol Medium;
- normal implementation that exposes a reasoning gap -> Sol High (semantic gap);
- small but subtle change with weak/no tests -> Sol High when silent semantic failure would be materially costly; otherwise Sol Medium plus focused review is cheaper;
- difficult but strongly verifiable debugging/implementation -> Sol Medium first, then Sol High from concrete failure evidence;
- high-blast-radius or weakly verifiable architecture/security/concurrency/migration decisions -> Sol High or XHigh directly;
- never Astra for DIRECT implementation; an extremely hard architecture/code review may delegate one read-only Astra reviewer (`extreme_*` signals).

Do not create an ORCHESTRATED plan merely to obtain a higher effort. DIRECT can choose any justified route.

## ORCHESTRATED tasks

Choose the logical tier per TODO, not per parent request:

- `economy`: Sol Low; Medium only when the floor asks for it (implementation that is not mechanical-and-checked);
- `standard`: Sol Medium; a second mechanical slip or a semantic failure moves to Sol High;
- `strong`: Sol Medium when deterministic validation is strong, otherwise Sol High; XHigh for high-risk/weak-verification work or evidence that High under-reasoned;
- `max`: Sol XHigh for genuinely demanding long-running work; `max` effort is not routed (it scored below XHigh at 1.36x the cost). Astra 6.2 is the frontier level above `max` (L6/F6; access rules above).

A failed compiler command does not automatically justify a higher effort. A wrong architecture decision may justify Sol High before any retry.

## Exploration subagents

Use Luna High explorers to protect expensive context from disposable discovery: a narrow question and the minimum starting paths/symbols; a compact evidence map, not narration or full files; read-only unless the task is explicitly mechanical and independently verifiable; at most two simultaneous explorers. The parent verifies material findings before consequential edits.

## Escalation ladder (runner default)

Climbed from `failure_class` evidence (`MODEL_ROUTING.md` §6), starting at the TODO's declared route:

```text
Sol Low                    (economy)
  -> Sol Medium            (standard)
  -> Sol High              (strong tier; a semantic failure from Sol Medium jumps here)
  -> Sol XHigh             (max tier: the top rung)
  => Astra High            (frontier level, only after >= 2 functional failures at Sol XHigh; then Astra XHigh)
```

One model climbing effort means no two rungs resolve to the same model and effort; the old Luna and Terra rungs are gone (map v11).

Do not spend several same-effort retries on a demonstrated capability gap: a semantic failure goes straight to the next tier boundary. The frontier step is not a rung: it replaces the `ladder_exhausted` block only after repeated functional failures at the top rung; quota/credits skip to the next provider's frontier model instead.

## Older catalogs and quota

The Claude/Codex model ids are fixed in `CURRENT_MODELS` and re-applied on every config load, so a per-plan `orchestrator.config.json` edit of `codex.models` is overwritten. GPT-6.2 Sol and Astra are listed by Codex CLI 0.171.0 (observed 2026-11-20) and absent from 0.159.2. A Codex installation whose catalog predates it (`codex debug models` lacks `gpt-6.2-sol`; upgrade with `npm i -g @openai/codex`) should update Codex; an unknown model id is rejected by the CLI as a configuration error, not rotated as quota. Availability/quota failure is not evidence to increase reasoning effort.

## Runner flags

Workers run as `codex exec --ephemeral --sandbox <mode> --model <id> -c model_reasoning_effort="<effort>" --output-schema ... --output-last-message ...`; the summary uses `--sandbox read-only`.

`--output-schema` receives a derived copy of `completion-report.schema.json` written per attempt to `<plan>/results/codex-output-schema.json`: OpenAI structured outputs reject `uniqueItems` and require strict objects (every property in `required`, `additionalProperties: false`), so the runner strips the unsupported keywords, marks optional fields required (workers return `null`/`[]`), and deduplicates the unique-list fields on ingestion instead. The canonical schema is unchanged for the other providers.
