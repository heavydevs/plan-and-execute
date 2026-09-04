# Model and provider routing

Load only when selecting or escalating a route. Keep task prompts/provider history out of this reference.

## Logical tiers

- `economy`: mechanical/narrow work, deterministic bookkeeping, final summarization.
- `standard`: ordinary bounded repository implementation/debugging/tests.
- `strong`: architecture-sensitive, security, concurrency, migration, cross-module synthesis, difficult debugging.
- `max`: hardest unresolved work after evidence-backed lower-route failure; use sparingly.

Choose the lowest tier plausibly able to satisfy the TODO acceptance criteria. A large overall request does not make every leaf TODO strong/max.

## Planning and review

Planning needs enough capability to avoid expensive bad decomposition:

- simple/medium plan: usually `standard`;
- complex architecture/migration/security/multi-workstream plan: usually `strong`;
- `max`: only after concrete unresolved constraints/review failures justify it.

Plan review runs in a fresh context and should be at least `standard`; match stronger planning for high-risk plans. Economy is appropriate for final summarization, not as the sole planner/reviewer of complex work.

## Execution heuristics

Use `economy` when scope/files are explicit, no architecture choice remains, deterministic checks are strong, and failure is cheap to detect.

Use `standard` for normal bounded TODOs.

Start `strong` when the **leaf itself** requires substantial reasoning about distributed state, concurrency, transactions, security, compatible schema/protocol migration, subtle performance behavior, or a difficult evidence-heavy defect.

Reserve `max` for concrete lower-tier failure evidence.

## Escalation

Default runner policy uses four validated functional failures per provider:

| Previous technical failures | Next route |
|---:|---|
| 0 | requested tier/effort |
| 1 | same tier, higher effort |
| 2 | one higher tier, at least high effort |
| 3 | up to two higher tiers, at least xhigh, capped by provider support |

After the provider failure budget, switch to the next configured provider only when fallback is allowed/available. A task blocks at its `max_attempts` limit.

Classify a failed attempt before changing route:

| Class | State action | Route action |
|---|---|---|
| `availability` | persist `deferred_until` with exponential backoff + jitter | retry/switch without consuming functional budget |
| `environment` | block with actionable host/auth/tool evidence | fix environment; do not escalate model |
| `contract` | block invalid/missing completion envelope | repair adapter/prompt/schema; do not escalate model |
| `capability` | record a functional failure | raise effort/tier/provider from evidence |
| `validation` | record a functional failure and host validation evidence | raise effort/tier/provider from evidence |
| `planning_invalidation` | block downstream work | return to study/decomposition |

Do **not** count these as functional failures:

- rate/quota/usage reset windows;
- temporary provider capacity;
- host interruption;
- a planning defect that requires new decomposition/dependencies.

Rate/availability events receive a persisted retry time. With automatic waiting enabled, the process releases its lease, sleeps outside the critical section, then reacquires it; another provider may take over meanwhile. Planning defects return to planning instead of escalating blindly.

## Provider fallback

Fallback requires:

- global + task fallback permission;
- installed/authenticated alternate CLI;
- compliance with repository/data/organization policy.

A fallback worker gets current task state/failure evidence, never the previous provider chat transcript.

An operator can persist a new logical route before resuming:

```bash
python <skill-dir>/scripts/planctl_concise.py route-set \
  --plan .ai-work/<plan-id> --task 001 --provider codex \
  --model-tier strong --effort high --unblock
pae resume --provider codex --takeover
```

## Default provider mapping

Logical mappings are configuration, not permanent capability claims. Current generated defaults:

| Tier | Claude Code | Codex |
|---|---|---|
| economy | `haiku` | `gpt-5.6-luna` |
| standard | `sonnet` | `gpt-5.6-terra` |
| strong | `opus` | `gpt-5.6` |
| max | `opus` + higher effort | `gpt-5.6` + higher effort |

Default provider order:

```json
["claude", "codex"]
```

Gemini, Qwen, Kimi, and Trae remain optional adapters until explicitly selected or added to `provider_order`. `default` model sentinel means omit that provider's explicit model flag.

## Cost/context policy

- Spend stronger reasoning on decomposition when it prevents large wrong workstreams.
- Do not use strong/max for status rendering, deterministic validation, cleanup, or final prose.
- Keep one task-definition path as the worker's primary prompt payload.
- Compile the task definition plus only assigned context/learnings into one immutable packet with source hashes; the worker reads that packet once.
- Increase route capability from failure evidence, not fear.
- Avoid parallel write workers unless repository isolation/worktrees remove conflict/reconciliation cost.
- Final summary uses economy + low effort when available.

## Configuration

Plan-specific values live in `orchestrator.config.json`; scripts remain provider-agnostic.

Common controls:

```json
{
  "provider_order": ["claude", "codex"],
  "allow_provider_fallback": true,
  "functional_failures_per_provider": 4,
  "rate_limit": {
    "auto_wait": true,
    "wait_seconds": 300,
    "max_wait_cycles": 0,
    "jitter_ratio": 0.1,
    "release_lease_while_waiting": true
  }
}
```

Provider-specific model ids, commands, permission modes, and retry exit codes remain in that generated config. Preserve them when editing a real plan; there is no need to copy the full config into prompts or task definitions.

At startup, the runner records a bounded capability probe for the configured CLI. Claude workers use bare/minimal dynamic prompt sections when supported; Codex workers request JSON events and low verbosity. Optional budget/turn caps remain disabled by default because silent truncation is not a token optimization.

Security note: unattended provider write/shell modes are appropriate only in a trusted workspace and never bypass the provider/host sandbox or organizational policy.
