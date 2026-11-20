# Model and provider routing

Load this reference only when choosing or escalating a model route. It defines provider-independent policy. Then read **exactly one** concrete provider reference for the provider that will actually execute the work:

- Codex -> `MODEL_ROUTING_CODEX.md`
- Claude Code -> `MODEL_ROUTING_CLAUDE.md`
- GLM -> `MODEL_ROUTING_GLM.md`; DeepSeek -> `MODEL_ROUTING_DEEPSEEK.md`; Muse -> `MODEL_ROUTING_MUSE.md`
- Model catalog/snapshot schema: `MODEL_CATALOG.md`; spawn decision and roles: `DELEGATION.md` (load only when needed)

Do not preload other provider files. A fallback provider loads its own reference only when fallback actually occurs.

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
| `extreme_architecture` / `extreme_code_review` — architecture or code review of an extremely hard demand | `max` xhigh, `frontier_eligible` (L6 only for a read-only analyst/verifier role) |

Modifiers: `weak_validation` raises the tier one step and the effort floor to `high`; `strong_validation` lets `standard`/`strong` start at `medium`; `implementation` forbids `low` unless the edit is mechanical **and** deterministically checked, because a worker at `low` effort tends to skip reading and validation.

### Candidate selector (opt-in, pure)

`routingctl.py select --signals <a,b> --providers <p1,p2>` (or `--request <json|->` with `route`, `required_capabilities`, `availability`, `tokens`, `billing`, `at`, `previous_route`, `cache_affinity`, `last_failure_class`, `min_quality_score`) resolves an attempt-time candidate without a model, clock, process or network call. Stages, each recorded in the explanation: floor -> capability (required capabilities, effort above the model's max) -> availability (catalog flag, `provider` or `provider/model` outage/quota/rate-limit state, exhausted subscription window) -> quality (catalog rank below the tier, optional minimum score) -> target tier (lowest tier with an eligible candidate, so an outage takes a same-tier equivalent before any lift) -> effective cost -> tie-break `marginal_cash_cost, quota_cost, provider_order, quality_rank_desc, model_id`. Unknown costs rank after known ones; candidates removed before economics never appear in the ranking.

Effective cost: `api` billing is cash (uncached, cached, cache-write and output tokens; off-peak rates inside the catalog window at `at`); `subscription` billing is `quota_cost` = usage (plan credits when the catalog has a formula, else tokens) / `window_capacity` with zero marginal cash until the window is exhausted, then `overage: block` makes the candidate unavailable and `overage: api` bills cash. With `previous_route`, cached tokens count as hits only on that provider/model. Sticky routing keeps an eligible previous route at or above the floor under `cache_affinity: high` unless a non-environmental failure or a strictly cheaper alternative wins. With only claude/codex configured and no economics, `select` equals the provider ladder (first configured provider wins ties). With `routing.auto_select: off` (the default) the runner does not call `select` and routes are unchanged; `shadow`/`on` rollout and its gates are in `ROUTING_CONFIG.md`.

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
| `advanced` | between standard and strong; no signal floor returns it, but a TODO or the selector may use it; a provider without an `advanced` model skips upward to `strong` |
| `strong` | difficult, subtle, high-risk, or weakly verifiable engineering |
| `max` | long-horizon escalation after semantic need or failure evidence; Opus 5.5 / Sol 6.2, the usual ceiling |
| `frontier` (L6/F6) | **level above every tier**: Fable 5.2 / Astra 6.2 for special cases only (access rules below); never persisted as a task tier |

Concrete models are provider-specific. Model generation and reasoning effort are independent axes: a newer model at low/medium effort can dominate an older model at high effort (Codex: GPT-6.2 Sol serves strong and max, so those tiers differ by effort only; Claude: Opus 5.5 serves strong and max, so max differs from strong by effort only).

**Frontier level L6/F6** (`routingctl.FRONTIER_MODELS`: `claude-fable-5-2` high, `gpt-6.2-astra` high and never `ultra`; `gemini-4-carbon-*` only when `agy models` lists it and you set `antigravity.frontier.model`). Owner policy (final, 2026-11-20), no per-task approval:

1. **Extreme architecture / code review**: the signals `extreme_architecture` or `extreme_code_review` give a `max`/`xhigh` floor plus `frontier_eligible`; `routingctl.py delegate` turns that into a frontier route only for a read-only `analyst` or `verifier`. Implementers of the same leaf stay on Opus 5.5 / Sol 6.2.
2. **Repeated top-rung failure**: after `routing_policy.frontier.min_top_failures` (default 2) failures classed `semantic`, `mechanical` or `unknown` at the max/xhigh rung, the runner's next dispatch is the frontier route instead of `ladder_exhausted`; until then an exhausted ladder retries the top rung. A failed frontier attempt blocks the TODO for replanning.

Never by floor lifting (`weak_validation`, `lift_tier`), never as an ordinary ladder rung, never by the selector, never for implementation, exploration, monitoring or DIRECT work, never because of quota, auth, billing, environment, budget or timeout outcomes. Codex credit exhaustion on Astra is availability: the runner skips to the next provider's frontier model (Fable 5.2) and records no escalation; a Claude Code older than 2.1.321 answering HTTP 400 for Fable is version unavailability, skipped the same way. Explicit provider overrides and `allow_provider_fallback: false` restrict the frontier chain exactly like ordinary routes. A frontier dispatch persists `tier: "max"` plus `level: "frontier"` and `frontier: true` (manifest route, telemetry, availability ledger), so schema 1-4 manifests and five-tier validators are unchanged. `routing_policy.frontier.enabled: false` restores the previous `ladder_exhausted` behaviour.

### Configured global provider preference

The following host preference requires global configuration (see [ROUTING_CONFIG.md](ROUTING_CONFIG.md) for paths/precedence). Built-in provider order remains Claude then Codex; explicit plan/task/CLI routes and legacy snapshots retain their documented precedence. Model examples require corresponding provider `models`; bootstrap `advanced` is empty for Claude/Codex and skips upward when not configured.

Owner preference, 2026-11-20 (global config, not a built-in default or a quality ranking):

- **Implementation** (`economy`, `standard`, `advanced`): **Antigravity** first -> **Codex** -> **Claude**. Antigravity models come from the opt-in workload overlay generated from `agy models` (`pae workloads preset`): Gemini 4 Neon first for standard/advanced/strong, Gemini 4 Hydrogen for economy and as the standard fallback, one profile per observed effort variant so the cheapest sufficient variant is used; Gemini 3.8 Flash only for log monitoring. Codex: `gpt-6.2-sol` on every tier by effort (Low economy, Medium standard, High strong, XHigh max; `gpt-6.1-terra` and `gpt-6-luna` are not routed). Claude: `claude-haiku-5-5`, `claude-sonnet-5-5`, `claude-opus-5-5`. Map `2026-11-20-v11`; evidence in `MODEL_MAPPING.md` §6.
- **Architecture and hard decisions** (`strong`, `max`): **Codex** first (`gpt-6.2-sol`, High, XHigh for `max`) -> **Claude** (`claude-opus-5-5`, High, XHigh for `max`); Antigravity only through the implementation overlay. Very hard demands normally run on Sol 6.2 / Opus 5.5.
- **Frontier** (L6/F6, above `max`): Codex `gpt-6.2-astra` -> Claude `claude-fable-5-2` (and `gemini-4-carbon-*` only when `agy models` lists it) under the access rules in §4: extreme architecture/code review, or after Sol/Opus failed repeatedly at max/xhigh. Never for ordinary work, quota, or environment faults.
- **Watchdog and diagnosis**: Routine watchdog execution runs without a model (`watchdogctl.py status --quiet`); the optional diagnostic assistant runs on economy (Gemini 3.8 Flash Medium, or Hydrogen when Flash is absent); investigating `blocked` task failure capsules runs in the `strong` tier at `high` on Codex (`gpt-6.2-sol`, strong/high) with Claude Opus 5.5 fallback.
- Antigravity's Claude 4.6 models were removed on 2026-11-18; the overlay never maps tiers to them, and Antigravity Claude (Opus 5.5 / Sonnet 5.5) stays capped at advanced.

## 5. Effort: thoroughness, not only thinking time

Effort controls how much work the model does per request — files read, tools used, verification steps before it returns — not just how long it thinks. Current provider defaults are adaptive/`high`; the skill pins effort only where it changes cost or quality:

- `low`: read-only extraction, summaries, mechanical edits with deterministic checks; **never an implementation worker that must run validation**;
- `medium`: cost-sensitive verified implementation; `strong` tier under strong validation;
- `high`: weak verification, high blast radius, difficult debugging, or evidence that medium under-reasoned;
- `xhigh`: demanding long-running loops or repeated hard failures;
- `max`: exceptional; test before adopting, it is prone to overthinking.

Some models accept no effort parameter (the bare `haiku` alias, which resolves to Haiku 4.5); the runner omits the flag for them. Haiku 5.5 accepts effort.

## 6. Escalate from classified evidence

Every failed attempt records a `failure_class` (worker report field or `planctl fail --failure-class`). The runner climbs the provider's ladder from that evidence, never from a retry count:

| Class | Meaning | Next route |
|---|---|---|
| `mechanical` | detail/tool/test slip the same understanding would fix | repeat the rung once, then +1 |
| `semantic` | wrong approach or reasoning gap | jump to the next stronger **tier** (skip same-tier effort rungs) |
| `environmental` | toolchain/repository problem outside the task | same route; repair the environment |
| `budget` | turn/token budget exhausted | repeat once (resume from checkpoints), then +1 |
| `timeout_ceiling` | explicit fixed runtime ceiling exhausted | block and review the runtime budget; no automatic escalation |
| `plan_defect` | task boundary, requirement, or dependency is wrong | block the task; replan |
| `unknown` | no report/invalid report/non-zero exit | +1 rung |

Diagnostic for choosing the class: *did the worker not know enough (semantic -> bigger model) or not try hard enough (skipped files, did not run tests -> mechanical/more effort)?* A deterministic validation failure after a claimed completion is `semantic` unless the worker declared a narrower class.

`budget` classification is pattern-matched against provider output (`routingctl`/`run_isolated` budget patterns). Claude Code's turn/spend-limit result envelope (`"subtype": "error_max_turns" | "error_max_budget_usd"`) is published and confirmed by an end-to-end self-test; Codex's rollout-budget abort message is not published, so an unmatched phrasing there falls back to `unknown` (safe: +1 rung) rather than `budget`. Recalibrate the patterns from real provider output if a project observes a mismatch.

Provider fallback (quota, rate limit, capacity, CLI interruption) is availability, not evidence: state is preserved and the equivalent logical rung runs on the fallback provider. When the evidence asks for a rung above the ladder's top on the last available provider (for example a `semantic` failure at the `max` tier), the frontier level decides (§4): below its threshold the top rung is retried, at the threshold the frontier route runs, and after a failed frontier attempt — or with `routing_policy.frontier.enabled: false` or no reachable frontier model — the runner blocks the TODO (`ladder_exhausted`) for replanning instead of spending the remaining attempts at the strongest route. Stop as soon as acceptance and independent validation pass.

### Validation stagnation: promote from missing progress

For a mapped validation, explicit `no_progress_timeout_seconds` wins, including `0`; omission inherits the runner's per-command idle window (default 1800), or 300 for a standalone watcher. Changed normalized output, increased process-tree CPU and configured probes/files renew that window. Missing progress while dependencies remain healthy preserves a bounded snapshot, stops the process tree and supplies semantic stagnation evidence. Every command starts fresh; productive work may continue beyond the original window. Service health probes continue independently and do not count as progress. See [PROGRESS_TIMEOUTS.md](PROGRESS_TIMEOUTS.md) for quiet phases, portable signals and optional fixed ceilings.

Confirmed stagnation raises the next fresh worker's route floor to `strong` (at least medium effort), or to `max` from `strong`/`max`. Repeated identical validation fingerprints keep their five-minute cross-attempt floor. This does not switch the root model. The next worker gets a compact latest-attempt excerpt/signature, not older logs. An unhealthy dependency remains `environmental`; an explicit fixed runtime ceiling is `timeout_ceiling`. Neither automatically raises capability: repair the dependency or review the selected runtime budget. Unavailable process metrics require output/probe/file evidence rather than invented CPU progress.

## 7. Two-phase leaves (optional)

A `high` TODO may declare `design_route` (`PLAN_SPEC.md`): a stronger worker writes a bounded design note (approach, decisions, contracts, ordered steps mapped to checkpoints, validation strategy), then the implementation worker runs at the task's own route with the note. Use it only when the leaf is hard **and** its implementation volume is large; a single strong worker is cheaper for a small hard edit.

## 8. Context economics are part of model economics

- Keep stable instructions before dynamic task data; keep worker prompts byte-identical except for trailing task values so provider caches share the prefix.
- Defer or disable unused tool/MCP definitions when supported; prefer batched deterministic queries over model round trips.
- Keep full logs on disk; pass a bounded latest-attempt excerpt, stable repeated-failure signature, and path to that attempt. Keep repeated history as signature/counter/age instead of duplicating the same long reason. A worker may open only the immediately preceding validation log when the excerpt is insufficient; do not reread superseded logs. Do not repeatedly summarize the same evidence.
- Final/status prose uses economy when no difficult synthesis is required; the configured preference above selects Antigravity without `--effort`.
- Optional per-worker budget guards (`claude.max_turns`, `claude.max_budget_usd`, `codex.rollout_token_budget`) turn runaway loops into resumable `budget` failures.

## Workload-specific profiles

Optional task `workload` selects implementation, frontend design, validation repair or monitoring affinity **after** the logical floor is known. Exact profile routes survive snapshot/automatic selection; explicit provider restrictions still apply. Availability distinguishes host authentication, model capacity and quota-pool exhaustion. Antigravity Claude profiles are conservatively capped at `advanced`, not assumed equivalent to native Claude. Configure and inspect with [VALIDATION_WORKLOADS.md](VALIDATION_WORKLOADS.md); without this overlay legacy routing is unchanged.
