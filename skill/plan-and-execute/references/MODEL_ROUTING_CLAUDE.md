# Claude Code model routing

Read only when Claude Code will execute the current work. `MODEL_ROUTING.md` owns provider-independent policy. Concrete ids live in `scripts/routingctl.py` `CURRENT_MODELS` (map version 2026-09-30-v5); this table must match it.

## Current capability map

| Tier | Model | List price in/out per MTok | Effort |
|---|---|---|---|
| `economy` | `haiku` (alias for Haiku 4.5, 200K context) | $1 / $5 | accepts **no effort** parameter; the runner omits `--effort` |
| `standard` | `claude-sonnet-5-5` (Sonnet 5.5) | $2 / $10 | `medium` for cost-sensitive verified work; `high` when correctness is less mechanically verifiable |
| `strong` | `claude-opus-5-5` (Opus 5.5) | $4 / $20 | `medium` when strong validation exists; otherwise `high` |
| `max` | `claude-fable-5-1` (Fable 5.1, most capable widely released) | $10 / $50 | `high`; `xhigh` for demanding long-running coding; `max` is exceptional |

Reviewed 2026-09-30 against the Claude Code CLI 2.1.285 model list and Anthropic's model table: no newer generally available id exists, so the ids are unchanged. Opus 5.5 replaced Opus 5 at a lower price ($4/$20 vs $5/$25) with the same 1M context and feature set, which makes it the right `strong` model, not a downgrade. Fable 5.1 succeeds Fable 5 at the same price.

Not routes: `claude-mythos-5-1` (Project Glasswing access program only), and the previous generation (`claude-opus-5`, `claude-opus-4-x`, `claude-sonnet-5`, `claude-sonnet-4-6`, `claude-fable-5`) which cost the same or more for less capability. The `opus`/`sonnet`/`fable` aliases resolve to the latest id, which is why `Agent` tool calls may name them.

Provider defaults differ per model: Sonnet 5.5 and Fable 5.1 default to `high`, Opus 5.5 defaults to `medium` (the runner always passes an explicit effort). Thinking is always on for Opus 5.5 and Fable 5.1, so the lowest effort still thinks; effort shapes thoroughness — files read, tools used, verification before returning — so do not dispatch an implementation worker at `low`.

Access caveat: Fable 5.1 needs usage credits on some plans/accounts. The CLI then answers HTTP 429 `credits_required`, which the runner classifies as quota, so a route that reaches the `max` rung pauses (exit 75) even though Opus is fine. Reach `max` only from real failure evidence; if the account cannot serve Fable, handle that task at Opus `xhigh` by hand rather than waiting.

## Elevation mechanics (how a route is actually obtained)

The skill never changes the session model: `/model`, `/effort`, and `opusplan` are user choices, and cache behavior depends on the selected model and provider settings. It obtains a different tier by **delegation**:

| Need | Mechanism |
|---|---|
| Cheap read-only discovery | `Agent` tool with `subagent_type: Explore` **and** `model: "haiku"`. The built-in Explore agent **inherits the main conversation's model** (capped at Opus); without the explicit `model` it explores at the session's price. |
| Stronger leaf from a smaller root | `Agent` tool with `model: "opus"` or `model: "fable"` and a minimal prompt (task, paths/symbols, acceptance, validation). A custom agent file may pin `model:` and `effort:` in its frontmatter. |
| Risky edits in isolation | `isolation: worktree` on the subagent (temporary worktree, auto-cleaned when unchanged). |
| Session-wide subagent default | `CLAUDE_CODE_SUBAGENT_MODEL=haiku` (per-invocation `model` and agent frontmatter still win). |
| Strong plan, cheap execution | The user-level `opusplan` alias plans on Opus and executes on Sonnet; the skill's planning-stage routing achieves the same split by delegating planning leaves. |
| Long orchestrations | Subagent requests get a 5-minute cache TTL by default; set `subagentPromptCacheTtl: 1h` (or `CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL=1h`) when many workers run over an hour. |
| Fan-out at scale | Dynamic workflows (`agent()`, `pipeline()`, `parallel()`, `schema`) run dozens of subagents from a script with intermediate results outside the conversation; same-prefix siblings share the prompt cache. See `PRIMARY_PLANNING.md` §10. |

Non-fork subagents start fresh (own system prompt, CLAUDE.md, git snapshot; no conversation history). A fork inherits the conversation and its cache, but a fork on a *different* model cannot reuse the parent cache — use a fresh minimal-prompt subagent to change tier.

## DIRECT mode

Small or medium-small cohesive work stays without a plan. Model routing still applies:

- one-off lookup/build/test/lint -> deterministic tool, no subagent;
- broad codebase discovery -> Explore/Haiku Low (explicit `model: "haiku"`);
- tiny mechanical edit with obvious local review or deterministic validation -> keep current useful context; use Haiku only when delegation genuinely saves context;
- normal bounded implementation with strong validation -> Sonnet Medium;
- normal coding where correctness is less mechanically verifiable -> Sonnet High;
- difficult but strongly verifiable implementation/debugging -> Opus Medium is a valid cost-saving first pass;
- high-blast-radius or weakly verifiable architecture/security/concurrency/migration work -> Opus High directly;
- frontier/very long-horizon work -> Fable 5.1 at the effort justified by the task, usually High/XHigh for hard coding.

Do not create an ORCHESTRATED plan merely to obtain a stronger Claude model.

## ORCHESTRATED tasks

Choose the logical tier per TODO:

- `economy`: Haiku (Explore/Haiku Low for discovery, narrow classification, cheap summaries; no effort flag);
- `standard`: Sonnet Medium when deterministic checks are strong; High for coding-sensitive or weakly verified work;
- `strong`: Opus Medium when failure is cheap and objectively caught; High for difficult/high-risk work; XHigh only for demanding long-running work;
- `max`: Fable 5.1 High/XHigh for frontier/long-horizon work; Max only when unconstrained reasoning has a plausible quality payoff.

If a lower effort completes reliably, do not increase it merely because the task belongs to a large plan.

## Exploration subagents

Prefer the native Explore/Haiku path for disposable repository discovery: narrow the question before spawning; provide the minimum starting context; request paths/symbols, why they matter, tests/contracts found, unresolved questions, and minimal excerpts; keep exploration read-only; default to at most two independent explorers; the parent/implementer verifies consequential findings.

A fresh explorer is useful when it prevents a stronger model from ingesting many irrelevant files. It is wasteful for one grep or two obvious reads.

## Escalation ladder (runner default)

Climbed from `failure_class` evidence (`MODEL_ROUTING.md` §6), starting at the TODO's declared route:

```text
Haiku (no effort)
  -> Sonnet Medium
  -> Sonnet High           (mechanical slips: repeat once, then +1)
  -> Opus Medium           (semantic: jump straight here from Sonnet)
  -> Opus High
  -> Fable High
  -> Fable XHigh
```

Skip lower rungs for weakly verifiable, high-impact decisions. Conversely, do not pay for Opus/Fable simply because repository exploration is large; isolate that exploration in Haiku and hand the compact evidence map to the stronger implementer.

## Runner flags

Workers run as `claude [--bare when ANTHROPIC_API_KEY is set] --print --no-session-persistence --json-schema ...` with `--model` and, for models that accept it, `--effort`. Optional `claude.max_turns` (`--max-turns`) and `claude.max_budget_usd` (`--max-budget-usd`, subagent spend included) in `orchestrator.config.json` bound one worker run; exhaustion returns as a resumable `budget` failure instead of a defect.
