# Execution provider policy

This feature separates **plan management** from **technical execution**.

A plan manager may be any model or host. When the user supplies an
`execution_policy`, semantic technical work is restricted to the providers in
`allowed_providers`. The restriction covers study, planning, plan review,
design, implementation, test authoring, validation judgment, and repairs.

Example:

```json
{
  "version": 1,
  "manager_mode": "delegate_only",
  "scope": "all_technical_work",
  "allowed_providers": ["claude", "codex"],
  "on_unavailable": "pause"
}
```

The manager may still perform deterministic orchestration: maintain lifecycle
state, dispatch workers, run declared validation commands, persist evidence, and
present the final handoff. It must not replace an unavailable authorized
executor with itself or silently widen the provider list.

## Design

- Authorization is captured before semantic planning.
- Governed plans use schema 5 and pin a normalized policy digest in the plan
  sentinel plus `EXECUTION_POLICY.json`.
- `provider: auto` resolves only inside the authorized set.
- Design routes, current routes, history routes, planning provenance, provider
  fallback, and resumed execution are checked against the policy.
- Missing authorized CLIs pause execution with a distinct policy exit instead
  of falling back to an unauthorized provider.
- DIRECT mode skips durable orchestration state but does not bypass provider
  authorization.
- `delegate_stage.py` provides the same boundary for study/planning work that
  occurs before a plan workspace exists.
- Final reporting for governed plans is deterministic from recorded evidence so
  the manager does not need another technical model call merely to summarize.

This is a dispatcher authorization mechanism, not a security sandbox or remote
model attestation. A host that grants the manager unrestricted filesystem or
shell access can still bypass skill instructions. Strong enforcement therefore
also requires host-level tool permissions.

## Token and quality rationale

The manager retains only small status/receipt data while authorized workers get
fresh, bounded technical contexts. Stable policy prefixes and path-based
handoffs reduce repeated context, while capability routing remains independent
inside the allowed provider set. Deterministic orchestration and validation are
kept out of model calls where possible.

The policy intentionally does not encode a claim that one vendor is always
better or cheaper. Provider/model tier and reasoning effort remain per-leaf
routing decisions after authorization has filtered eligibility.

## Key files

- `references/EXECUTION_PROVIDERS.md` - normative workflow.
- `references/execution-policy.example.json` - minimal policy example.
- `scripts/provider_policy.py` - normalization, pinning, authorization checks.
- `scripts/delegate_stage.py` - authorized pre-plan technical delegation.
- `scripts/provider_policy_self_test.py` - focused regression coverage.
- `scripts/planctl.py`, `preplanctl.py`, `run_isolated.py`, and
  `lifecyclectl.py` - lifecycle integration.
