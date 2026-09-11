# Model and provider routing

Load this reference only when choosing or escalating a model route. It defines provider-independent policy. Then read **exactly one** concrete provider reference for the provider that will actually execute the work:

- Codex -> `MODEL_ROUTING_CODEX.md`
- Claude Code -> `MODEL_ROUTING_CLAUDE.md`

Do not preload both provider files. A fallback provider loads its own reference only when fallback actually occurs.

## Objective

Maximize **verified quality per credit/token and per completed task**, not raw benchmark score or price per token. Use the cheapest route credible for the current semantic leaf; spend more when weak verification, high blast radius, or concrete failure evidence makes stronger reasoning economically safer.

## 1. Classify the leaf, then look up the floor

Name the leaf's observable signals and let `python <skill-dir>/scripts/routingctl.py route --signals <a,b,c>` (or the table in `SKILL.md` §4) return the minimum credible route. Signals:

| Primary signal | Floor |
|---|---|
| `deterministic_lookup` — filename/symbol/text search, a known build/test/lint command, formatting | tool, no model |
| `exploration` — broad discovery, call-site/test inventory, dependency tracing, bounded extraction | `economy` low |
| `mechanical_edit` — rename/move/format/regenerate with an obvious local check | `economy` low |
| `bounded_implementation` — ordinary feature, focused refactor, routine debugging, tests | `standard` medium |
| `subtle_debugging` — ordering, state, flaky or non-local causes | `strong` medium |
| `architecture_decision` — boundaries, dependency graph, compatibility strategy | `strong` high |
| `cross_cutting_risk` — migration, security, concurrency, transactions, data integrity, distributed behaviour | `strong` high |
| `silent_failure_costly` — a wrong result would not be caught and would cost materially | `strong` high |
| `frontier_long_horizon` — unusually broad reasoning or very long autonomous loops | `max` high |
| `repeated_strong_failure` — the strong route failed with useful evidence | `max` xhigh |

Modifiers: `weak_validation` raises the tier one step and the effort floor to `high`; `strong_validation` lets `standard`/`strong` start at `medium`; `implementation` forbids `low` unless the edit is mechanical **and** deterministically checked, because a worker at `low` effort tends to skip reading and validation.

A large parent request does not make every leaf strong/max. Size and semantic difficulty are separate axes: localize a big file with cheap tools, then send only the hard decision to the strong model.

## 2. Verifiability changes the cheapest safe route

When deterministic validation is strong and failure is cheap to detect, prefer:

```text
cheapest credible route -> deterministic validation
PASS -> stop
FAIL -> classify the failure -> next rung from evidence -> validate again
```

Examples of strong verification: compile, unit/integration tests, lint, type checks, schema checks, exact queries, snapshots, golden outputs, or reproducible benchmark commands.

When objective verification is weak, start one step stronger. Examples: architecture boundaries, security policy, destructive migrations, distributed consistency, ambiguous production diagnosis, or a small code change with no meaningful tests where silent semantic failure would be costly.

Do not interpret "no tests" as "always use the strongest model." First assess change size, reversibility, local inspectability, and blast radius.

## 3. Elevate by delegation. Never switch the root session

The root session's model is the user's choice and its context is the cheapest cache the task has: every provider caches the prompt prefix **per model and, on most models, per effort level**, so switching the root model or effort mid-task re-reads the whole conversation uncached (Anthropic reports that an Opus->Haiku switch mid-session is *more* expensive than staying). Therefore:

- **Never switch the root session's model/effort to obtain a stronger or cheaper route.**
- **Delegate the leaf instead:** start a fresh worker at the required tier with a minimal prompt (task, paths/symbols, acceptance, validation command) and consume only its compact result.
- **A small root model is not a ceiling.** If the root tier is below the floor for a stage (triage says `strong`, root is Haiku/Luna), that stage is delegated at the floor tier — never attempted in the root. Planning stages follow `PLANNING_ROUTING.md` the same way.
- **Explorers protect expensive context:** discovery that fans out runs in the provider's cheapest read-only worker and returns an evidence map (paths/symbols, relevance, tests/contracts, unresolved questions, minimal excerpts); the implementer verifies material findings. Never spawn a worker for one grep or two obvious reads; default to at most two concurrent explorers.
- The concrete mechanism (subagent `model`/`effort` parameters, spawn roles, cache TTLs) is in the active provider reference.

DIRECT means **no planning harness**, not "one expensive model does everything": keep the current conversation when its context is useful, delegate only fan-out discovery or a leaf whose floor exceeds the root tier, and never create a plan solely to obtain a stronger model.

## 4. Logical tiers remain portable

| Tier | Meaning |
|---|---|
| `economy` | exploration, mechanical/narrow work, cheap summaries |
| `standard` | ordinary bounded implementation/debugging/tests |
| `strong` | difficult, subtle, high-risk, or weakly verifiable engineering |
| `max` | frontier/long-horizon escalation after semantic need or failure evidence |

Concrete models are provider-specific. Model generation and reasoning effort are independent axes: a newer model at low/medium effort can dominate an older model at high effort (Codex: Astra Low >= Sol High; Claude: Opus Medium is a valid first strong rung under strong validation).

## 5. Effort: thoroughness, not only thinking time

Effort controls how much work the model does per request — files read, tools used, verification steps before it returns — not just how long it thinks. Current provider defaults are adaptive/`high`; the skill pins effort only where it changes cost or quality:

- `low`: read-only extraction, summaries, mechanical edits with deterministic checks; **never an implementation worker that must run validation**;
- `medium`: cost-sensitive verified implementation; `strong` tier under strong validation;
- `high`: weak verification, high blast radius, difficult debugging, or evidence that medium under-reasoned;
- `xhigh`: demanding long-running loops or repeated hard failures;
- `max`: exceptional; test before adopting, it is prone to overthinking.

Some models accept no effort parameter (Claude Haiku); the runner omits the flag for them.

## 6. Escalate from classified evidence

Every failed attempt records a `failure_class` (worker report field or `planctl fail --failure-class`). The runner climbs the provider's ladder from that evidence, never from a retry count:

| Class | Meaning | Next route |
|---|---|---|
| `mechanical` | detail/tool/test slip the same understanding would fix | repeat the rung once, then +1 |
| `semantic` | wrong approach or reasoning gap | jump to the next stronger **tier** (skip same-tier effort rungs) |
| `environmental` | toolchain/repository problem outside the task | same route; repair the environment |
| `budget` | turn/token budget exhausted | repeat once (resume from checkpoints), then +1 |
| `plan_defect` | task boundary, requirement, or dependency is wrong | block the task; replan |
| `unknown` | no report/invalid report/non-zero exit | +1 rung |

Diagnostic for choosing the class: *did the worker not know enough (semantic -> bigger model) or not try hard enough (skipped files, did not run tests -> mechanical/more effort)?* A deterministic validation failure after a claimed completion is `semantic` unless the worker declared a narrower class.

Provider fallback (quota, rate limit, capacity, CLI interruption) is availability, not evidence: state is preserved and the equivalent logical rung runs on the fallback provider. When the evidence asks for a rung above the ladder's top on the last available provider (for example a `semantic` failure at the `max` tier), the runner blocks the TODO (`ladder_exhausted`) for replanning instead of spending the remaining attempts at the strongest route. Stop as soon as acceptance and independent validation pass.

## 7. Two-phase leaves (optional)

A `high` TODO may declare `design_route` (`PLAN_SPEC.md`): a stronger worker writes a bounded design note (approach, decisions, contracts, ordered steps mapped to checkpoints, validation strategy), then the implementation worker runs at the task's own route with the note. Use it only when the leaf is hard **and** its implementation volume is large; a single strong worker is cheaper for a small hard edit.

## 8. Context economics are part of model economics

- Keep stable instructions before dynamic task data; keep worker prompts byte-identical except for trailing task values so provider caches share the prefix.
- Defer or disable unused tool/MCP definitions when supported; prefer batched deterministic queries over model round trips.
- Keep full logs on disk; pass bounded failure excerpts plus paths to retries. Do not repeatedly summarize the same evidence.
- Final/status prose uses an economy route when no difficult synthesis is required.
- Optional per-worker budget guards (`claude.max_turns`, `claude.max_budget_usd`, `codex.rollout_token_budget`) turn runaway loops into resumable `budget` failures.
