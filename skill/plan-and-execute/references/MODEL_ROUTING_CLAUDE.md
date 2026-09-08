# Claude Code model routing

Read only when Claude Code will execute the current work. `MODEL_ROUTING.md` owns provider-independent policy.

## Current capability map

| Tier | Model | Typical starting effort |
|---|---|---|
| `economy` | `haiku` / built-in `Explore` | `low` |
| `standard` | `sonnet` | `medium` for cost-sensitive verified work; `high` when coding sensitivity is higher |
| `strong` | `opus` | `medium` when strong validation exists; otherwise `high` |
| `max` | `claude-fable-5-1` | `high`; `xhigh` for demanding long-running coding; `max` is exceptional |

Anthropic's current effort guidance treats Low as the efficient subagent setting, Medium as the balance point, High as the default for difficult coding/agents, XHigh as long-running agentic/coding work, and Max as unconstrained reasoning. Optimize by cost per solved task rather than always choosing High/Max.

## DIRECT mode

Small or medium-small cohesive work stays without a plan. Model routing still applies:

- one-off lookup/build/test/lint -> deterministic tool, no subagent;
- broad codebase discovery -> built-in Explore/Haiku Low;
- tiny mechanical edit with obvious local review or deterministic validation -> keep current useful context; use Haiku only when delegation genuinely saves context;
- normal bounded implementation with strong validation -> Sonnet Medium;
- normal coding where correctness is less mechanically verifiable -> Sonnet High;
- difficult but strongly verifiable implementation/debugging -> Opus Medium is a valid cost-saving first pass;
- high-blast-radius or weakly verifiable architecture/security/concurrency/migration work -> Opus High directly;
- frontier/very long-horizon work -> Fable 5.1 at the effort justified by the task, usually High/XHigh for hard coding.

Do not create an ORCHESTRATED plan merely to obtain a stronger Claude model.

## ORCHESTRATED tasks

Choose the logical tier per TODO:

- `economy`: Haiku/Explore Low for discovery, narrow classification, and cheap summaries;
- `standard`: Sonnet Medium when deterministic checks are strong; High for coding-sensitive or weakly verified work;
- `strong`: Opus Medium when failure is cheap and objectively caught; High for difficult/high-risk work; XHigh only for demanding long-running work;
- `max`: Fable 5.1 High/XHigh for frontier/long-horizon work; Max only when unconstrained reasoning has a plausible quality payoff.

If a lower effort completes reliably, do not increase it merely because the task belongs to a large plan.

## Exploration subagents

Prefer the native Explore/Haiku path for disposable repository discovery:

- narrow the question before spawning;
- provide the minimum starting context;
- request paths/symbols, why they matter, tests/contracts found, unresolved questions, and minimal excerpts;
- keep exploration read-only;
- default to at most two independent explorers;
- parent/implementer verifies consequential findings.

A fresh explorer is useful when it prevents a stronger model from ingesting many irrelevant files. It is wasteful for one grep or two obvious reads.

## Escalation ladder

For objectively verifiable work:

```text
Tools/Haiku exploration
        -> Sonnet Medium
        -> Sonnet High when the gap is reasoning-sensitive
        -> Opus Medium/High from demonstrated difficulty or risk
        -> Fable High/XHigh for frontier or long-horizon need
        -> Max only when lower efforts leave a plausible capability gap
```

Skip lower rungs for weakly verifiable, high-impact decisions. Conversely, do not pay for Opus/Fable simply because repository exploration is large; isolate that exploration in Haiku and hand the compact evidence map to the stronger implementer.
