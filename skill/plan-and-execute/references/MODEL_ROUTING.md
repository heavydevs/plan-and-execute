# Model and provider routing

## Contents

1. Logical tiers
2. Planning and review routes
3. Generated defaults
4. Worker-selection heuristics
5. Escalation schedule
6. Provider fallback
7. Cost and summary policy
8. Configuration

## 1. Logical tiers

Route work by capability requirement rather than permanently hardcoding a commercial model name:

- `economy`: narrow, mechanical, read-heavy, formatting, deterministic bookkeeping, or final summarization.
- `standard`: ordinary repository exploration, localized implementation, routine debugging, and most test additions.
- `strong`: broad synthesis, architecture-sensitive design, concurrency, security, complex migrations, difficult debugging, or repeated standard-tier failure.
- `max`: the hardest unresolved analysis or implementation after evidence-backed failure; use sparingly.

Use the lowest tier that can reliably satisfy the role's acceptance criteria. Increase reasoning effort before replacing a capable model with a more expensive tier.

## 2. Planning and review routes

Planning is a first-class technical task, not economy-tier bookkeeping.

Use at least `standard` for request analysis and repository study. Start with `strong` when the request has multiple large workstreams, cross-module architecture, migrations, security boundaries, concurrency, distributed state, unclear ownership, or a large unfamiliar codebase.

Use `max` for planning only when one of these applies:

- the strong-tier planner cannot resolve conflicting constraints after concrete repository and research evidence;
- two review rounds still find material omissions or oversized tasks;
- the change combines several high-risk domains such as security, data migration, and distributed consistency;
- an architecture decision has a broad, difficult-to-reverse compatibility impact.

Run the plan reviewer in a fresh context. Use at least `standard`; match or exceed the planner's tier for high-risk plans. The reviewer must challenge coverage and decomposition rather than merely restating the plan.

Use read-only research workers at `standard` for bounded repository areas. Raise an individual research worker to `strong` only when its subject requires broad synthesis or difficult technical judgment.

Do not use `economy` as the sole planner or reviewer for a complex multi-workstream request. Reserve it for mechanical state work and final summarization.

## 3. Generated defaults

The generated `orchestrator.config.json` uses these defaults as of 2026-08-25:

| Logical tier | Claude Code alias | Codex model |
|---|---|---|
| `economy` | `haiku` | `gpt-5.6-luna` |
| `standard` | `sonnet` | `gpt-5.6-terra` |
| `strong` | `opus` | `gpt-5.6` |
| `max` | `opus` with higher effort | `gpt-5.6` with higher effort |

Model catalogs change. Treat the generated file as user-editable routing configuration, not a permanent claim about model availability. Keep logical tiers stable and update only the mapping.

The default summary route is `economy` with `low` effort.

## 4. Worker-selection heuristics

Choose `economy` when all are true:

- scope is narrow and explicit;
- expected files are known;
- no architectural choice is required;
- deterministic checks are strong;
- failure is cheap to detect and retry.

Choose `standard` for ordinary bounded implementation work.

Choose `strong` initially when a leaf task includes one or more of:

- distributed state, concurrency, transactions, or data consistency;
- authentication, authorization, secrets, or security boundaries;
- backward-compatible schema or protocol migration;
- broad cross-module design that remains one coherent outcome;
- subtle performance or memory behavior;
- an ambiguous production-only defect with substantial evidence to synthesize.

Reserve `max` for a task that remains blocked after lower routes produced concrete failure evidence.

Provider selection should follow user preference, repository conventions, available CLI authentication, and task fit. Do not assert that one provider is universally superior. With `provider: auto`, use the configured order and switch only after the configured technical-failure budget.

## 5. Escalation schedule

The strict runner uses `functional_failures_per_provider = 4` by default. For each provider:

| Functional failures already recorded | Next route |
|---:|---|
| 0 | Requested tier and requested effort. |
| 1 | Same tier, one higher effort level. |
| 2 | One higher tier, at least `high` effort. |
| 3 | Up to two higher tiers, at least `xhigh` effort, capped by model support. |

After four functional failures, switch to the next available provider when fallback is allowed. Repeat the route ladder there. Clamp tier and effort to configured maxima.

A task becomes `blocked` when `functional_failures` reaches its `max_attempts` value.

Do not increment functional failures for:

- HTTP 429 or equivalent rate limiting;
- subscription usage reset windows;
- exhausted credits that will replenish;
- temporary provider capacity;
- an interrupted host process;
- a discovered planning defect that requires decomposition or dependency repair.

Persist availability events separately and retry the same route. Route planning defects back through the planning protocol instead of escalating a worker blindly.

## 6. Provider fallback

Use fallback only when:

- `allow_provider_fallback` is true globally and for the task;
- the alternate CLI is installed and authenticated;
- switching does not violate data, organizational, or repository policy.

For an explicitly provider-locked task, set `allow_provider_fallback` to `false`.

A fallback worker still receives only the current task definition. It diagnoses the repository's current state and recorded validation failure, not the previous provider's chat transcript.

## 7. Cost and summary policy

- Spend stronger reasoning on decomposition before execution when it prevents large incorrect workstreams.
- Avoid strong or max models for state rendering, status updates, deterministic validation, or final prose.
- Let scripts manage state, coverage checks, validation, and cleanup.
- Use economy models for final summarization after all checks pass.
- Keep worker prompts small by referencing one task file instead of pasting the whole plan.
- Avoid parallel write agents solely to reduce elapsed time; conflict resolution can cost more than sequential execution.

## 8. Configuration

Each plan contains `orchestrator.config.json`. Common edits:

```json
{
  "provider_order": ["codex", "claude"],
  "allow_provider_fallback": true,
  "functional_failures_per_provider": 4,
  "rate_limit": {
    "auto_wait": true,
    "wait_seconds": 300,
    "max_wait_cycles": 0
  },
  "claude": {
    "models": {
      "economy": "haiku",
      "standard": "sonnet",
      "strong": "opus",
      "max": "opus"
    }
  },
  "codex": {
    "models": {
      "economy": "gpt-5.6-luna",
      "standard": "gpt-5.6-terra",
      "strong": "gpt-5.6",
      "max": "gpt-5.6"
    }
  }
}
```

`max_wait_cycles: 0` means no cycle limit while the runner remains alive. The backoff is capped at one hour per wait.
