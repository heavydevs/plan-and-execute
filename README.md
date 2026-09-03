# Plan and Execute

**Use a persistent multi-worker plan only when it earns its cost.**

`plan-and-execute` is a selective orchestration skill for Claude Code and OpenAI Codex. Routine cohesive small/medium coding requests stay in the agent's current context. Long-horizon work can enter the full evidence-backed workflow immediately, or a task that grows during implementation can be promoted later without throwing away completed work.

[Leia em Português](README.pt-BR.md)

## What changed in 0.8

The skill now follows:

```text
DIRECT by default -> ORCHESTRATE by evidence -> PROMOTE when necessary
```

This solves a real cost problem with agent skills: a broad skill description can cause ordinary implementation prompts to pay for study, planning, traceability, task files, and fresh workers even when one conversation would have been faster and cheaper.

The full harness is still intact when orchestration is justified. An orchestrated or promoted implementation still has:

- a terse persistent `TODO.md` checklist;
- one bounded definition file per TODO;
- `manifest.json` as authoritative lifecycle state;
- resumable subtasks/checkpoints;
- request-part -> requirement -> TODO traceability;
- per-TODO `provider`, `model_tier`, and `reasoning_effort` recommendations;
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
| Google Gemini CLI | Yes | No | Opt-in | Fresh headless CLI process |
| Qwen Code | Yes | No | Opt-in | Fresh headless CLI process |
| Kimi Code CLI | Yes | No | Opt-in | Fresh prompt-mode CLI process |
| Trae Agent | Yes | No | Opt-in | Fresh `trae-cli run` process |

The npm installer intentionally installs the skill only for Claude Code, Codex, or both. Other providers are optional execution backends configured inside an orchestrated plan.

## Quick start

Requirements:

- Node.js 18.17+;
- Python 3.10+;
- Claude Code and/or Codex installed and authenticated.

Install for both agents in the current workspace:

```bash
npx @luizcgvrj/plan-and-execute install both
```

Install globally for the current user:

```bash
npx @luizcgvrj/plan-and-execute install both --global
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

Concrete provider model ids are resolved through `orchestrator.config.json`. This keeps the task portable when one provider runs out of quota or a different compatible model is available. Effort/tier/provider escalation follows actual failure evidence, not fear or overall request size.

See [MODEL_ROUTING.md](skill/plan-and-execute/references/MODEL_ROUTING.md).

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
pae resume --provider gemini --once
```

or:

```bash
python <skill-dir>/scripts/run_isolated.py --plan .ai-work/<plan-id>
```

The runner starts a fresh process for each TODO, independently reruns validations, bounds diagnostic output, and builds the final summary from compact authoritative state rather than raw worker transcripts.

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

Run:

```bash
python skill/plan-and-execute/scripts/routing_self_test.py
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
