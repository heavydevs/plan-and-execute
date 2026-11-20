# Claude Code model routing

Read only when Claude Code will execute the current work. `MODEL_ROUTING.md` owns provider-independent policy. Concrete ids live in `scripts/routingctl.py` `CURRENT_MODELS` (map version 2026-11-20-v11; the frontier level lives in `FRONTIER_MODELS`); this table must match it.

## Current capability map

| Tier | Model | List price in/out per MTok | Effort |
|---|---|---|---|
| `economy` | `claude-haiku-5-5` (Haiku 5.5, 1M context) | $0.10 / $0.50 (above 100K prompt tokens $0.50 / $2.50) | accepts effort (`low`..`max`); `low` only for short, checkable tool tasks, `medium` for exploration whose misses are costly |
| `standard` | `claude-sonnet-5-5` (Sonnet 5.5) | $2 / $10 | `medium` for well-specified verified work; `high` for multi-file or intermittent bugs; never `max` |
| `strong` | `claude-opus-5-5` (Opus 5.5) | $4 / $20 | `medium` when strong validation exists; otherwise `high` |
| `max` | `claude-opus-5-5` (Opus 5.5, higher effort) | $4 / $20 | `xhigh`; `max` effort is dominated and never a default |
| `frontier` (L6/F6) | `claude-fable-5-2` (Fable 5.2, 1M context) | $8 / $40 | `high`; `xhigh` only where a gain is measured; never `max` |

Opus 5.5 is the usual ceiling. **Frontier level (L6/F6, above `max`):** `claude-fable-5-2` is one level above everything else, for special cases only. Access rules (owner, final 2026-11-20; no per-task approval): reachable ONLY (1) through the leaf signals `extreme_architecture` / `extreme_code_review` on a read-only analyst/verifier role, or (2) after the `max` route failed `routing_policy.frontier.min_top_failures` times (default 2; classes semantic, mechanical or unknown) at the max/xhigh rung. Never by floor lifting, never as an ordinary ladder rung, never for implementation, exploration, monitoring or DIRECT work, never because of quota, auth, billing, environment, budget or timeout outcomes. The route persists `tier: max` with `level: frontier`, `frontier: true`; `routing_policy.frontier.enabled: false` restores the old `ladder_exhausted` block. See `MODEL_ROUTING.md` §6. Fable 5.2 needs Claude Code >= 2.1.321 (Anthropic model-config page and changelog, 2026-11-20; the owner's pinned `claude-pae-2.1.322.exe` runs it): an older CLI answers HTTP 400 `does not support this model`, which the runner treats as version unavailability (skip to the next provider's frontier model, no escalation).

Reviewed 2026-11-20 against the Claude Code CLI 2.1.329 and Anthropic's model table. Minimum Claude Code versions (vendor docs): Opus 5.5 2.1.280, Sonnet 5.5 2.1.284, Haiku 5.5 2.1.293, Fable 5.2 2.1.321. Changes from 2026-09-30: Haiku 5.5 replaces the `haiku` alias (which resolved to Haiku 4.5 and took **no effort** parameter on CLI 2.1.283, below Haiku 5.5's minimum; the docs say the alias is Haiku 5.5 on current CLIs, so the runner pins `claude-haiku-5-5` and still omits `--effort` for the bare alias), and `max` moved from Fable 5.1 to Opus 5.5. Opus 5.5 replaced Opus 5 at a lower price ($4/$20 vs $5/$25) with the same 1M context, which makes it the right `strong` and `max` model, not a downgrade. Fable 5.2 succeeds Fable 5.1 at a lower price ($8/$40 vs $10/$50) but requires Claude Code >= 2.1.321, and the bare `fable` alias resolved to Fable 5.1 on older CLIs. Run `claude update` before enabling any Fable route. On Pro and standard seats Fable bills usage credits from the first request (and `-p` runs do so without asking); on Max/Ultra it is capped at 50% of the weekly limit. A safety-flagged Fable request can silently re-run on an Opus model, so the runner logs the model that answered.

Not routes: `claude-mythos-5-2` (verified organizations only), and the previous generation (`claude-opus-5`, `claude-opus-4-x`, `claude-sonnet-5`, `claude-sonnet-4-6`, `claude-fable-5`, `claude-fable-5-1`, `claude-haiku-4-5`) which cost the same or more for less capability. The `opus`/`sonnet`/`fable` aliases resolve to the latest id the CLI knows, which is why `Agent` tool calls may name them.

Provider defaults differ per surface: on the API Sonnet 5.5 and Fable 5.2 default to `high`, Opus 5.5 and Haiku 5.5 to `medium`; Claude Code defaults all four to `medium` and `CLAUDE_CODE_EFFORT_LEVEL` overrides `--effort` (the runner always passes an explicit effort; do not set that variable for workers). Thinking is always on for Opus 5.5 and Fable, so the lowest effort still thinks; effort shapes thoroughness — files read, tools used, verification before returning — so do not dispatch an implementation worker at `low`.

Evidence (2026-11-20, `docs/research/model-refresh-20261120/anthropic-claude.md`):

- **Haiku vs Sonnet.** Sonnet 5.5 wins agentic coding clearly: Artificial Analysis Coding Agent Index v2.1 (Claude Code harness) 56 vs 30 at max; Terminal-Bench 4.0 70.6% vs 39.2% (vendor). Haiku matched Sonnet only on short bounded sessions (Bito replay, medium, 8 hard sessions: 66.5% vs 68.3% at about half the cost), and its 5x input price above 100K prompt tokens removes much of its edge in agent loops. So Haiku is for read-only discovery, summaries and classification, Sonnet for implementation that must pass tests unattended.
- **Opus effort.** Gains are steep to `medium`/`high` and flat after: CursorBench 4.0 low 43.7% ($1.17), medium 52.5% ($2.91), high 56.0% ($3.97), xhigh 56.0% ($6.98), max 57.8% ($13.43); Intelligence Index 35/48/52/57/59. Opus max on the Coding Agent Index is 58.16 at $12.61/task with 15.9M tokens and about 9% model fallbacks.
- **Fable 5.2.** Coding Agent Index high 58.24 at $7.51, xhigh 58.47 at $15.47, max 55.74 at $44.22 (16% timeouts). Above Opus `high`, Fable `high` reaches Opus max's score at about 60% of the cost; Bito's replay points the other way (Opus medium 84.1% at $5.40 vs Fable medium 81.0% at $8.13). The owner policy keeps Fable as the frontier level; the inversion is recorded as an open question for the frozen `routing-eval` replay.

Indexes measure few efforts per model (Opus, Sonnet and Haiku only at max on the Coding Agent Index); treat them as direction, not proof.

## Elevation mechanics (how a route is actually obtained)

The skill never changes the session model: `/model`, `/effort`, and `opusplan` are user choices, and cache behavior depends on the selected model and provider settings. It obtains a different tier by **delegation**:

| Need | Mechanism |
|---|---|
| Cheap read-only discovery | `Agent` tool with `subagent_type: Explore` **and** `model: "haiku"`. The built-in Explore agent **inherits the main conversation's model** (capped at Opus); without the explicit `model` it explores at the session's price. |
| Stronger leaf from a smaller root | `Agent` tool with `model: "opus"` (`claude-fable-5-2` only for a read-only extreme architecture/code-review leaf) and a minimal prompt (task, paths/symbols, acceptance, validation). A custom agent file may pin `model:` and `effort:` in its frontmatter. |
| Risky edits in isolation | `isolation: worktree` on the subagent (temporary worktree, auto-cleaned when unchanged). |
| Session-wide subagent default | `CLAUDE_CODE_SUBAGENT_MODEL=haiku` (per-invocation `model` and agent frontmatter still win). |
| Strong plan, cheap execution | The user-level `opusplan` alias plans on Opus and executes on Sonnet; the skill's planning-stage routing achieves the same split by delegating planning leaves. |
| Long orchestrations | Subagent requests get a 5-minute cache TTL by default; set `subagentPromptCacheTtl: 1h` (or `CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL=1h`) when many workers run over an hour. |
| Fan-out at scale | Dynamic workflows (`agent()`, `pipeline()`, `parallel()`, `schema`) run dozens of subagents from a script with intermediate results outside the conversation; same-prefix siblings share the prompt cache. See `PRIMARY_PLANNING.md` §10. |

Non-fork subagents start fresh (own system prompt, CLAUDE.md, git snapshot; no conversation history). A fork inherits the conversation and its cache, but a fork on a *different* model cannot reuse the parent cache — use a fresh minimal-prompt subagent to change tier.

## DIRECT mode

Small or medium-small cohesive work stays without a plan. Model routing still applies:

- one-off lookup/build/test/lint -> deterministic tool, no subagent;
- broad codebase discovery -> Explore/Haiku Medium (explicit `model: "haiku"`; Low only for short, checkable lookups — at Low Haiku is likelier to skip a search or a check);
- tiny mechanical edit with obvious local review or deterministic validation -> keep current useful context; use Haiku only when delegation genuinely saves context;
- normal bounded implementation with strong validation -> Sonnet Medium;
- normal coding where correctness is less mechanically verifiable -> Sonnet High;
- difficult but strongly verifiable implementation/debugging -> Opus Medium is a valid cost-saving first pass;
- high-blast-radius or weakly verifiable architecture/security/concurrency/migration work -> Opus High directly;
- very hard or long-horizon work -> Opus XHigh; Fable 5.2 never for DIRECT implementation, only as a read-only reviewer of an extremely hard architecture/code review (`extreme_*` signals).

Do not create an ORCHESTRATED plan merely to obtain a stronger Claude model.

## ORCHESTRATED tasks

Choose the logical tier per TODO:

- `economy`: Haiku 5.5 (Explore/Haiku Medium for discovery whose misses are costly; Low for narrow classification and cheap summaries);
- `standard`: Sonnet Medium when deterministic checks are strong; High for coding-sensitive or weakly verified work;
- `strong`: Opus Medium when failure is cheap and objectively caught; High for difficult/high-risk work; XHigh only for demanding long-running work;
- `max`: Opus XHigh for very hard/long-horizon work; Max only when unconstrained reasoning has a plausible quality payoff. Fable 5.2 is the frontier level above `max` (L6/F6; access rules above).

If a lower effort completes reliably, do not increase it merely because the task belongs to a large plan.

## Exploration subagents

Prefer the native Explore/Haiku path for disposable repository discovery: narrow the question before spawning; provide the minimum starting context; request paths/symbols, why they matter, tests/contracts found, unresolved questions, and minimal excerpts; keep exploration read-only; default to at most two independent explorers; the parent/implementer verifies consequential findings.

A fresh explorer is useful when it prevents a stronger model from ingesting many irrelevant files. It is wasteful for one grep or two obvious reads.

## Escalation ladder (runner default)

Climbed from `failure_class` evidence (`MODEL_ROUTING.md` §6), starting at the TODO's declared route:

```text
Haiku 5.5 Low
  -> Haiku 5.5 Medium
  -> Sonnet Medium
  -> Sonnet High           (mechanical slips: repeat once, then +1)
  -> Opus Medium           (semantic: jump straight here from Sonnet)
  -> Opus High
  -> Opus XHigh            (max tier: the top rung)
  => Fable 5.2 High        (frontier level, only after >= 2 functional failures at the top rung)
```

Opus XHigh is the top rung. After `min_top_failures` (default 2) semantic, mechanical or unknown failures there, the runner's next step is the frontier route (Codex Astra first when the `max` chain starts with Codex, else Fable 5.2) instead of a `ladder_exhausted` block; a failed frontier attempt blocks for replanning. Quota, auth, billing, environment, budget and timeout outcomes never count. Skip lower rungs for weakly verifiable, high-impact decisions. Conversely, do not pay for Opus/Fable simply because repository exploration is large; isolate that exploration in Haiku and hand the compact evidence map to the stronger implementer.

## Runner flags

Workers run as `claude [--bare when ANTHROPIC_API_KEY is set] --print --no-session-persistence --json-schema ...` with `--model` and, for models that accept it, `--effort`. Optional `claude.max_turns` (`--max-turns`) and `claude.max_budget_usd` (`--max-budget-usd`, subagent spend included) in `orchestrator.config.json` bound one worker run; exhaustion returns as a resumable `budget` failure instead of a defect.
