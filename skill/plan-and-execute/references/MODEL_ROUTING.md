# Model and provider routing

Load this reference when selecting, escalating, or capping a route. These rules also apply in DIRECT mode whenever the host can choose a model or delegate to subagents.

## Objective

Maximize verified implementation quality per credit/token, not raw model strength. Use the cheapest route that is credible for the current semantic leaf, then escalate only from evidence. Do not spend frontier-model tokens on repository discovery that a cheap read-only worker or deterministic search can do.

## 1. Route by work type, verifiability, and blast radius

Use this order before choosing a model:

1. **Deterministic/local lookup** — one grep, filename search, symbol lookup, build/test command, formatting, or other non-judgmental operation: use tools directly; spawning a model can cost more than the lookup.
2. **Exploration** — broad file discovery, call-site inventory, test discovery, log/stack-trace triage, dependency tracing, or initial repository study: use a read-only `economy` subagent when delegation avoids loading substantial disposable context into the main agent.
3. **Bounded implementation** — normal feature work, ordinary debugging, focused tests/refactors: use `standard`.
4. **Reasoning-sensitive implementation** — architecture, security, concurrency, transactions, compatible schema/protocol migration, data integrity, subtle performance, or difficult evidence-heavy defects: use `strong`.
5. **Frontier/escalation work** — unresolved hard work after lower routes fail with useful evidence, or genuinely long-horizon/high-risk reasoning that cheaper routes are unlikely to solve safely: use `max`.

A large parent request does not make every leaf task strong/max.

### Verifiability rule

Cheap-first is preferred when failure is inexpensive and deterministic checks can catch it. Examples: compilation, unit/integration tests, lint, type checks, schema checks, snapshots, golden outputs, or exact repository queries.

Start stronger when a wrong answer has high blast radius and weak objective verification, for example architecture boundaries, destructive migrations, security policy, distributed consistency, or ambiguous production incidents. Saving tokens on the first pass is false economy if the result is hard to verify.

## 2. Cheap exploration is a first-class route

Exploration often produces context that is useful only once. Keep it out of expensive/main context when the host supports subagents.

- Run deterministic search/ranking first.
- If discovery fans out across many files, symbols, logs, tests, or docs, delegate it to the cheapest credible **read-only** worker.
- Ask the explorer for a compact evidence map: relevant paths/symbols, why each matters, tests/contracts found, unresolved questions, and only the smallest useful excerpts.
- Do not return search narration, full files, or dead ends.
- The parent/implementer verifies material findings before high-risk or irreversible changes.
- Do not spawn an explorer for one or two obvious reads; subagent startup/context overhead can exceed the savings.
- Prefer at most two concurrent exploratory workers unless the branches are genuinely independent and parallelism clearly pays.

Provider-native defaults:

- **Claude Code:** prefer the built-in `Explore` agent / Haiku for read-only codebase discovery, or a custom Haiku subagent for similarly bounded research.
- **Codex:** when multi-agent delegation is available, route exploration subagents to Luna with low effort by default; use medium only for multi-hop tracing that remains bounded.

## 3. Logical tiers and current provider mapping

Logical tiers remain portable across providers. Concrete model ids are configuration and must be reviewed when providers change their lineups.

| Tier | Intended use | Claude Code | Codex |
|---|---|---|---|
| `economy` | exploration, narrow/mechanical work, cheap summaries | `haiku` | `gpt-5.6-luna` |
| `standard` | ordinary bounded implementation/debugging/tests | `sonnet` | `gpt-5.6-terra` |
| `strong` | difficult/high-risk engineering | `opus` | `gpt-5.6-sol` |
| `max` | frontier/long-horizon escalation | `claude-fable-5-1` | `gpt-6-astra` |

Do not select models by price-per-token alone. A stronger model can sometimes use fewer total tokens on a hard task. The routing objective is verified **task cost**, so frontier models remain valid when they materially reduce retries or solve work that lower tiers cannot.

## 4. Effort policy

Default effort by semantic leaf:

| Work | Start | Escalate when |
|---|---|---|
| deterministic lookup | no model | never |
| economy exploration/mechanical | `low` | `medium` for bounded multi-hop reasoning |
| standard implementation | `medium` | `high` after evidence of a reasoning gap |
| strong/high-risk work | `high` | `xhigh` only for demanding long-running work |
| max/frontier | `high` | `xhigh` for long-horizon/repeated hard failure; `max` only as final permitted resort |

`max` effort is never a default. Avoid spending multiple retries increasing effort on a weak model when moving one model tier up is more likely to improve capability.

## 5. Quality-preserving escalation

For work with strong deterministic verification, use a verify-and-escalate loop:

```text
cheapest credible route -> deterministic validation
PASS -> stop
FAIL -> preserve compact failure evidence -> raise effort/tier -> validate again
```

Do not count quota/rate-limit exhaustion, temporary provider capacity, or host interruption as technical failure. Planning/decomposition defects return to planning rather than escalating the model blindly.

Recommended progression is semantic, not a mandatory number of retries:

```text
economy low/medium -> standard medium -> standard/high -> strong/high -> max/high -> max/xhigh -> max/max
```

Skip inappropriate lower rungs for high-risk, weakly verifiable work. Stop as soon as acceptance criteria and independent validation pass.

## 6. User model/effort ceiling

The user may set a **routing ceiling** for the whole request or plan. It is a hard budget boundary, not a recommendation.

A ceiling contains:

- maximum logical model tier: `economy | standard | strong | max`;
- maximum effort: `low | medium | high | xhigh | max`;
- optional provider-specific model override at that ceiling.

Rules:

- Never exceed the ceiling in the root agent, subagents, retries, reviewers, study workers, final summarizers, or provider fallback.
- If automatic escalation reaches the ceiling, retry only within the remaining allowed route or block with evidence; never silently spend a stronger model.
- A provider fallback must be capped to the equivalent logical tier too.
- A user can raise/lower the ceiling later; persisted plans must record the change.
- In DIRECT mode, honor the same ceiling even though no `.ai-work` state exists.

For an orchestrated plan, apply current mappings and an optional hard ceiling immediately after plan creation:

```bash
python <skill-dir>/scripts/routingctl.py configure --plan <plan-path>
python <skill-dir>/scripts/routingctl.py configure --plan <plan-path> --max-tier strong --max-effort high
```

Optional provider-specific ceiling-model overrides are supported by `routingctl.py`; the logical tier still caps fallback providers.

## 7. Provider-specific token controls

### Codex

When host configuration permits it, keep subagent defaults cheaper than the root agent for exploration, for example Luna + low/medium effort. Keep subagent concurrency bounded; more agents multiply tokens and are useful only for independent work. Ultra/max-style reasoning can consume substantially more tokens and may involve additional agents, so it is an escalation route, not a default manager.

### Claude Code

Use Haiku/Explore for codebase discovery, Sonnet for most implementation, Opus for difficult/high-risk engineering, and Fable 5.1 for demanding long-horizon/frontier work. Use subagents to isolate disposable investigation or independent verification, not to turn sequential work into a swarm.

## 8. Context and cache economics

- Search/rank first, read focused ranges second, widen only from evidence.
- Keep stable provider instructions before dynamic task data so prompt caching can reuse prefixes.
- Defer/disable unused tool or MCP definitions when the host supports it; large unused tool schemas waste context.
- Prefer batched/programmatic deterministic queries over many model/tool round trips when safe.
- Keep full logs on disk and pass only bounded error excerpts plus log paths to retries.
- Compact or clear stale tool results only after durable decisions/evidence are preserved; do not repeatedly summarize the same material.
- Final prose/status rendering uses `economy` + low effort when available.

## 9. Planning and review

Planning needs enough capability to avoid expensive bad decomposition:

- simple/medium plan: usually `standard`;
- complex architecture/migration/security/multi-workstream plan: usually `strong`;
- `max`: only when frontier/long-horizon complexity or concrete unresolved lower-tier failure justifies it.

For high-risk plans, use an independent reviewer at a credible tier; do not pay for a separate strong reviewer on trivial, deterministically verifiable work.

## 10. Default fallback behavior

Default provider order remains:

```json
["claude", "codex"]
```

Fallback requires global + task permission, an installed/authenticated alternate CLI, and repository/data/organization-policy compliance. A fallback worker receives current task state and compact failure evidence, never the previous provider chat transcript.

Security note: unattended provider write/shell modes are appropriate only in a trusted workspace and never bypass provider/host sandbox or organizational policy.
