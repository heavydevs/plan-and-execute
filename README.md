# Plan and Execute

**Use a persistent multi-worker plan only when it earns its cost.**

`plan-and-execute` is a selective orchestration skill for Claude Code, OpenAI Codex, and Google Antigravity. Routine cohesive small/medium coding requests stay in the agent's current context. Long-horizon work can enter the full evidence-backed workflow immediately, or a task that grows during implementation can be promoted later without throwing away completed work.

[Leia em Português](README.pt-BR.md)

## What's new in 0.10

Version 0.10 introduces execution watchdog monitoring, an explicit progress/error signal contract, token-efficient log digests, refreshed model routing policy, and native Google Antigravity installer support:

- **Execution Watchdog (`watchdogctl`)**: `status --quiet` observes plans and jobs read-only; `watch --interval 300` writes only an observation cache for deduplication. Both preserve plan, job and process state. They detect anomalies (`blocked`, `runner_dead`, `silent`, `awaiting_next`, `quota_resume_due`, `job_failed`) and support host scheduling (Windows Task Scheduler, cron, loop).
- **Progress and Error Contract (`progress_signal`)**: Standardized `PROGRESS`, `ERROR`, and `HEARTBEAT` emission via `progress_signal.py`. Configure an increasing-counter probe (`probe_file`) to renew validation idle windows; worker windows also use output, CPU and repository changes. Heartbeats report liveness.
- **Token-Efficient Log Watcher (`log_watch.py digest`)**: Aggregates redacted error signatures and progress from a bounded log prefix. The [synthetic benchmark](docs/research/LOG_DIGEST.md) achieves >99% reduction using the `chars/4` token estimate; results depend on the log. Inspect `truncated` and `omitted_records` for coverage limits.
- **Updated Model Routing Policy**: The documented global preference uses Codex `gpt-6.1-sol` above economy and Antigravity `gemini-3.8-flash-high` for economy/watchkeeping, with Claude fallback. These chains require configuration; built-in order remains Claude then Codex. Configure user-global and per-plan chains with `pae configure`.
- **Installer and Verification**: Native support for Antigravity (`~/.gemini/config/skills` user scope, `.agents/skills` workspace scope). Use `install all` (via `pae install all`) to install across Claude Code, Codex, and Antigravity at once. Validate installation integrity against bundled skill hashes with `status --verify` (e.g. `pae status all --verify`).

### Configurable routing and advisory diagnosis

From a checkout or installed package:

```bash
node bin/plan-and-execute.js configure
node bin/plan-and-execute.js configure --show --json
node bin/plan-and-execute.js configure --plan .ai-work/<plan-id>
```

Run `pae configure` (or `node bin/plan-and-execute.js configure`). It asks one numbered question at a time, checks documented non-generative authentication status where available, and saves only after confirmation. `--dry-run` does not save.

Defaults merge with your global configuration and then explicit plan overrides; dictionaries merge and lists replace. New version-2 overlays inherit global settings, while legacy full snapshots keep their previous behavior. For each tier, choose a primary and ordered fallbacks independently of the assistant. Quota/authentication/capacity failures keep the logical tier and functional failure count; exhausted chains pause with exit 75 and persisted cooldowns rather than looping.

**The assistant is off by default.** It can explain ambiguous repeated failures, repeated unhealthy checks or confirmed stalls after deterministic validation fails. One attempt per task, bounded/redacted evidence and strict JSON keep coordination limited. Advice never edits files, executes suggested commands or approves a task. Actual token/cost savings have not been measured.

**Native advisory limitation:** only Claude Code bare/tool-less mode is implemented, with an explicitly supplied `ANTHROPIC_API_KEY` (API billing, not subscription OAuth). Antigravity is selectable as the preferred assistant but safely skips because its workspace-write sandbox is not a verified read-only boundary. Other advisory profiles also skip until verified; the seven coding adapters are unaffected. Check billing and confidentiality before opting in.

See [routing configuration](skill/plan-and-execute/references/ROUTING_CONFIG.md), [advisory safety and limits](skill/plan-and-execute/references/ASSISTANTS.md), and [research/evaluation protocol](docs/research/AUXILIARY_ROUTING.md). The implementation plan is retained in `.ai-work/20260928-auxiliary-routing` at the user's request; ordinary guarded cleanup remains available.

## What changed in 0.9

The routing foundation from 0.8 is unchanged:

```text
DIRECT by default -> ORCHESTRATE by evidence -> PROMOTE when necessary
```

0.9 makes model routing evidence-based end to end instead of size- or count-based:

- **Escalation follows classified evidence, not a retry count.** A failed attempt records `failure_class` (`mechanical`, `semantic`, `environmental`, `budget`, `plan_defect`, `unknown`); `mechanical`/`budget` repeat the rung once then climb, `semantic` jumps straight to the next stronger tier, `environmental` leaves the route alone, and `plan_defect` blocks the TODO for replanning instead of burning attempts. When evidence asks for a rung above the strongest one on the last available provider, the TODO is blocked (`ladder_exhausted`) rather than retried at the top route until `max_attempts`.
- **A small root model is a delegator, not a ceiling.** The skill never switches the root session's model/effort — this keeps the root route stable; exact cache keys depend on the provider — so a leaf whose floor exceeds the root tier is delegated to a fresh worker instead. `routingctl.py route --signals ...` and a leaf-signal table in `SKILL.md` give a cheap root model the same floors a frontier root would use, protected by a `tier-evals.json` regression corpus.
- **Two-phase leaves** (`design_route`): a `high` TODO can have a stronger worker write a bounded design note first, then implement at its own cheaper route with that note.
- **Decision-first planning** (`request_analysis.hard_decisions`): when only a few planning decisions are hard, resolve them with strong workers before a standard planner writes the mechanical plan.
- **One model catalog** (`routingctl.py`) backs every entrypoint; effort is omitted for models that reject it (Claude Haiku); optional per-worker budgets (`claude.max_turns`, `claude.max_budget_usd`, `codex.rollout_token_budget`) turn runaway workers into resumable `budget` failures instead of technical ones.
- **A Google Antigravity CLI (`agy`) adapter** joins Claude Code and Codex as an execution backend; the Gemini CLI adapter is now marked legacy (the CLI itself was sunset).
- Documents the concrete elevation mechanics per host (subagent `model`/`effort`, `isolation: worktree`, `opusplan`, Codex `spawn_agent` roles, prompt-cache facts) and fixes several Windows-specific dispatch bugs (`.cmd` shim resolution, the Store Python alias, runner-lease liveness).

The full harness described below is still intact when orchestration is justified. An orchestrated or promoted implementation still has:

- a terse persistent `TODO.md` checklist;
- one bounded definition file per TODO;
- `manifest.json` as authoritative lifecycle state;
- resumable subtasks/checkpoints;
- request-part -> requirement -> TODO traceability;
- per-TODO `provider`, `model_tier`, and `reasoning_effort` recommendations, evidence-based escalation, and optional `design_route`;
- deterministic validation outside worker self-reports;
- provider/model escalation and fallback;
- quota/rate-limit events that preserve state instead of counting as technical failure;
- recovery by another compatible AI without the old chat transcript;
- guarded cleanup that removes planning/control state but preserves implementation changes.

## Supported AI workers

| Worker | Execution support | Standard skill install | Default route | Notes |
|---|---:|---:|---:|---|
| Claude Code | Yes | Yes | First | Standard quick-start target |
| OpenAI Codex | Yes | Yes | Second | Standard quick-start target |
| Google Antigravity CLI (`agy`) | Yes | Yes | Opt-in | Headless `agy -p` process with JSON schema output; install with `pae install antigravity` or `install all` |
| Google Gemini CLI | Legacy | No | Opt-in | Sunset on 2026-06-18; use the Antigravity adapter for new plans |
| Qwen Code | Yes | No | Opt-in | Fresh headless CLI process |
| Kimi Code CLI | Yes | No | Opt-in | Fresh prompt-mode CLI process |
| Trae Agent | Yes | No | Opt-in | Fresh `trae-cli run` process |

The npm installer supports Claude Code, Codex, and Google Antigravity (using `both` for Claude + Codex, `antigravity`, or `all` for all three hosts). Other providers are optional execution backends configured inside an orchestrated plan.

## Quick start

Requirements:

- Node.js 18.17+;
- Python 3.10+;
- Claude Code, Codex, and/or Google Antigravity (`agy`) installed and authenticated.

Install for Claude Code and Codex in the current workspace:

```bash
npx @luizcgvrj/plan-and-execute install both
```

Or install for all supported hosts (Claude Code, Codex, and Antigravity):

```bash
npx @luizcgvrj/plan-and-execute install all
```

Install globally for the current user:

```bash
npx @luizcgvrj/plan-and-execute install all --global
```

Verify installation integrity against bundled skill hashes:

```bash
pae status all --verify
```

The default activation is **selective**. To make the skill explicit-only:

```bash
pae install both --global --activation explicit
```

Return an untouched managed installation to selective mode:

```bash
pae install both --global --selective
```

See [installation details](skill/plan-and-execute/references/INSTALLATION.md).

## Selective activation

The bundled skill description is intentionally narrow. Automatic orchestration is appropriate when at least one strong signal exists, such as:

- multiple independently verifiable workstreams whose retained reasoning does not substantially help each other;
- broad repository study or substantial current external research before implementation is safe;
- repo-wide migration, compatibility, security, data-integrity, concurrency, or cross-module coordination;
- likely work across sessions, providers, quota windows, or context compaction where durable resume state has real value;
- isolated delegated workers that materially reduce unrelated context or improve independent validation.

The following are **not** sufficient by themselves:

- the words “implement”, “refactor”, or “fix”;
- several related files;
- controller + service + entity + tests for one cohesive rule set;
- an ordinary bounded feature or bug fix;
- a nearly finished task with high context usage.

File count is weak evidence. Semantic independence and durable coordination value matter more.

### DIRECT mode

If the skill is implicitly considered but no strong orchestration signal exists, it exits immediately:

- no `.ai-work` directory;
- no study artifact;
- no requirements inventory;
- no plan/TODO/task files;
- no fresh worker solely for process compliance;
- no lifecycle state.

The main agent keeps implementing and validating in its current useful context.

## Late promotion

A direct task is not trapped in DIRECT mode. If implementation reveals materially larger scope, it can be promoted.

Promotion is useful when substantial work remains and, for example:

- one request splits into independent remaining outcomes;
- broad research becomes necessary;
- migration/compatibility/security uncertainty appears;
- interruption or quota risk makes durable resume important;
- context pressure becomes high **and** the remaining work is substantial enough to benefit from a durable handoff.

Context percentage is deliberately secondary. There is no universal “90% means orchestrate” rule.

`promotectl.py` validates a compact handoff containing only durable state:

- original goal;
- completed work;
- validated results;
- active decisions/invariants;
- relevant paths/symbols;
- blockers/risks;
- remaining outcomes;
- optional context-pressure observation;
- bounded git branch/status/diff-stat evidence.

Example:

```bash
python <skill-dir>/scripts/promotectl.py validate \
  --spec /tmp/pae-promotion-spec.json --json

python <skill-dir>/scripts/promotectl.py render \
  --repo-root . \
  --spec /tmp/pae-promotion-spec.json \
  --output /tmp/pae-promotion-request.md \
  --json
```

The generated request is then planned normally, but **only for remaining outcomes**. Completed work is never fabricated as retroactive TODOs.

See [promotion protocol](skill/plan-and-execute/references/PROMOTION.md).

## Full orchestrated workflow

Once ORCHESTRATED is selected, the existing robust workflow remains:

1. Preserve the complete request.
2. Perform only the internal/external study depth that can change architecture, compatibility, task boundaries, risk, or validation.
3. Inventory stable request parts and observable requirements.
4. Split work by context-cohesive outcomes and independent validation boundaries.
5. Review coverage, atomicity, dependencies, validation, and context minimality.
6. Persist the plan under `.ai-work/<plan-id>/`.
7. Execute one isolated TODO at a time with only its assigned execution context and validated learnings.
8. Re-run deterministic validation outside the worker.
9. Persist every state transition before moving on.
10. Resume safely after host/provider/quota interruption.
11. Generate a compact handoff and remove only verified planning/control state after success.

The entrypoint is intentionally small; detailed orchestration lives in [ORCHESTRATION.md](skill/plan-and-execute/references/ORCHESTRATION.md) and phase-specific references are loaded only when needed.

## Why TODO boundaries matter

A fresh worker should receive one coherent semantic problem, not an arbitrary file bundle.

Two unrelated CRUDs with independent models, rules, and tests usually become two TODOs even if they use the same framework pattern. Conversely, a controller, service, entity, migration, and focused tests can stay in one TODO when they implement one invariant and benefit from the same reasoning context.

Schema v4 requires `context_boundary`, resumable `subtasks`, and optional directional `learning_targets` for every task.

## Persistent TODOs and recovery

A generated plan resembles:

```text
.ai-work/<plan-id>/
├── .orchestrator-plan
├── manifest.json                 # authoritative state
├── orchestrator.config.json
├── REQUEST.md
├── STUDY.md
├── study.json
├── ANALYSIS.md
├── PLAN.md
├── PLAN_REVIEW.md
├── TODO.md                       # one terse line per parent TODO
├── CONTEXT.md                    # optional universal context
├── contexts/                     # optional scoped plan-time context
├── learnings/                    # validated directional runtime learnings
├── tasks/                        # one bounded definition per TODO
├── results/
└── logs/
```

After interruption, completed subtasks remain complete and only interrupted in-progress state is recovered. Partial source changes are preserved. Another session/provider can continue from disk state without rereading the parent chat.

Lifecycle commands:

```bash
pae current
pae resume
pae resume --once
pae cancel
pae reset --force
```

## Per-TODO model routing

The plan recommends capability per leaf TODO rather than assigning one expensive model to the whole request.

Logical tiers:

| Tier | Intended use |
|---|---|
| `economy` | Mechanical/narrow changes with strong deterministic checks |
| `standard` | Normal bounded implementation/debugging/tests |
| `strong` | Architecture-sensitive, security, concurrency, migration, difficult debugging |
| `max` | Hard unresolved work after evidence-backed lower-route failure |

Each TODO keeps:

```json
{
  "provider": "auto",
  "model_tier": "standard",
  "reasoning_effort": "medium"
}
```

Concrete provider model ids are resolved through `orchestrator.config.json` from one catalog (`scripts/routingctl.py`): Claude `haiku`/`sonnet`/`opus`/`claude-fable-5-1`, Codex `gpt-6-luna`/`gpt-6.1-sol` (Sol serves every tier above economy; tiers differ by effort). This keeps the task portable when one provider runs out of quota or a different compatible model is available.

### Routing from leaf signals, elevation by delegation

Every leaf — a planning stage or an implementation TODO — is routed from observable signals, not from the parent request's size or the root chat's model:

```bash
python skill/plan-and-execute/scripts/routingctl.py route --signals bounded_implementation,weak_validation,implementation
# {"tier": "strong", "effort": "high"}
```

The skill **never switches the root session's model or effort** (that invalidates the provider prompt cache). When the root model is below a leaf's floor — including when the skill is started from Haiku or Luna — it delegates that leaf to a fresh worker at the floor tier with a minimal prompt and consumes the compact result. A small root model is a delegator, not a ceiling; there is no user-selected model ceiling either.

### Escalation from classified evidence

A failed attempt records a `failure_class` (worker report field or `planctl fail --failure-class`): `mechanical` repeats the rung once and then climbs one step; `semantic` jumps to the next stronger tier (on Codex, Sol Medium → Sol High); `environmental` keeps the route; `budget` resumes from checkpoints; `plan_defect` blocks the TODO for replanning. Rate limits and quota are never evidence. Provider ladders live in the catalog; Haiku, which accepts no effort parameter, is dispatched without `--effort`.

### Two-phase leaves and decision-first planning

A `high` TODO may declare `design_route`: a stronger worker writes a bounded design note first, then the implementation worker runs at the TODO's cheaper route with it. When only a few planning decisions are hard, `request_analysis.hard_decisions` records a decision-first pass: strong workers resolve the decisions, a standard planner writes the mechanical plan.

Optional per-worker budgets (`claude.max_turns`, `codex.rollout_token_budget`) turn runaway workers into resumable `budget` failures.

See [MODEL_ROUTING.md](skill/plan-and-execute/references/MODEL_ROUTING.md), the provider maps, and `references/tier-evals.json` (the leaf-routing regression corpus).

## Selective validated learning

Fresh contexts intentionally do not inherit source chats. When a TODO discovers an expensive validated procedure, decision, pitfall, code reference, or validation technique that a declared future TODO would otherwise rediscover, the orchestrator can publish a compact directional learning file after deterministic validation.

No useful discovery means no learning file and no extra future context cost.

## Execution context

Plan-time shared context is omission-first:

- `CONTEXT.md` only for non-obvious information needed by every TODO;
- `contexts/<topic>.md` only for a strict multi-TODO subset;
- single-task facts stay in that task definition;
- runtime discoveries go to validated learning artifacts, not mutable global context.

## Strict runner and optional providers

Use the lifecycle wrapper:

```bash
pae resume
pae resume --provider codex --once
pae resume --provider antigravity --once
```

or:

```bash
python <skill-dir>/scripts/run_isolated.py --plan .ai-work/<plan-id>
```

The runner starts a fresh process for each TODO, independently reruns validations, bounds diagnostic output, and builds the final summary from compact authoritative state rather than raw worker transcripts.

Long validations can continue while meaningful progress renews their idle window: the default 1800-second `validation_timeout_seconds` is now per-command idle time, including for existing plans. Set `validation_hard_timeout_seconds` only when total runtime needs a fixed ceiling (default `0`, disabled). A read-only batch counter can keep a silent book import alive without exposing credentials; unchanged heartbeats and failed probes do not count. Explicit worker, advisory and provider ceilings remain in force.

Tasks can declare mapped validation IDs in `validation_jobs`. Workers start those tracked `jobctl.py` validations and finish; the deterministic runner waits and verifies the result. See [progress windows, silent-job examples and tracked waiting](skill/plan-and-execute/references/PROGRESS_TIMEOUTS.md).

### Execution watchdog and progress monitoring

A dedicated watchdog inspects active plans and jobs. `status` is read-only; `watch` persists only its observation cache, preserving plan/job/process state:

```bash
python <skill-dir>/scripts/watchdogctl.py status --repo-root . --quiet
python <skill-dir>/scripts/watchdogctl.py watch --repo-root . --interval 300
```

`watchdogctl watch` deduplicates anomalies (`blocked`, `runner_dead`, `silent`, `awaiting_next`, `quota_resume_due`, `job_failed`). Use `progress_signal.py` to emit and probe progress counters, and `log_watch.py digest` for bounded, redacted log summaries. `keepalivectl.py check` (schedule it every 20 minutes, or `keepalivectl.py schedule install --yes` on Windows) relaunches a runner that died with runnable work left, with a restart-loop guard and a hidden console. See [WATCHDOG.md](skill/plan-and-execute/references/WATCHDOG.md) and the [synthetic digest measurement](docs/research/LOG_DIGEST.md).

## Activation modes

### Selective — recommended

```bash
pae install both --activation selective
```

The skill remains discoverable automatically, but routing negatives + the DIRECT exit avoid paying for orchestration on ordinary work.

### Explicit-only

```bash
pae install both --activation explicit
```

The installer produces host-specific copies:

- Claude: `disable-model-invocation: true`;
- Codex: `allow_implicit_invocation: false`.

The package source is not mutated. Marker schema v2 records both source and installed hashes, so explicit variants retain the same local-change protection as selective installs.

## Routing regression suite

`references/routing-evals.json` contains direct near-misses, positive orchestration requests, and late-promotion cases. The suite specifically protects against regressions such as:

- “refactor this service/controller/tests” accidentally triggering a plan;
- “update the same helper in many call sites” triggering only because many files are touched;
- high context percentage promoting a task when only one tiny cohesive fix remains;
- large multi-workstream/migration/research requests failing to enter orchestration.

`references/tier-evals.json` protects leaf routing the same way: small-but-risky leaves must be routed strong even from a small root model, and large-but-mechanical leaves must stay cheap.

Run:

```bash
python skill/plan-and-execute/scripts/routing_self_test.py
python skill/plan-and-execute/scripts/model_routing_self_test.py
python skill/plan-and-execute/scripts/promotion_self_test.py
```

## Development

```bash
npm run check
```

This runs package cleanup, skill validation, Node tests, and Python self-tests for lifecycle recovery, study evidence, context isolation, task memory, provider adapters, token efficiency, artifact concision, routing, promotion, and cleanup safety.

## Safety and cleanup

The skill does not bypass provider sandboxes, permissions, organizational policies, or repository controls. Write-heavy TODOs execute sequentially unless worktree isolation makes parallel writes safe.

After successful final validation and handoff, cleanup deletes only the verified `.ai-work/<plan-id>/` planning/control workspace. Source changes, tests, commits, generated product artifacts, and unrelated repository files remain.

## License

MIT. See [LICENSE](LICENSE).
