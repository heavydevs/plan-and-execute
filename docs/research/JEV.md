# Jev integration decision

Reviewed 2026-09-30 against the `plan-and-execute` main-line skill and current TypeSafe documentation.

## Decision

Use Jev only as an **optional typed diagnostic adviser after an already-failed validation**. Do not use it for planning, TODO decomposition, coding-provider/model routing, requirement/context deletion, test approval, lifecycle transitions, cleanup, or resource monitoring.

The selected use has three properties that the rejected uses do not:

1. the input is already a small bounded evidence capsule produced by the deterministic validator path;
2. the answer space already exists as a finite set of diagnostic classes;
3. a wrong answer can remain advisory while the normal worker and validators retain authority.

This is an architectural-fit decision, not a claim that Jev improves quality on this repository. No live authenticated benchmark was run. Broader use should require a held-out comparison on real failures measuring validated outcome quality and total cost, not agreement with the current worker.

## Rejected uses

| Candidate | Decision | Reason |
|---|---|---|
| Repeated ambiguous validation failure | Implement as optional `Choice` | Bounded state, finite classes, existing non-authoritative handoff. |
| Success, first failure, lint/type/syntax failure | No Jev call | Local deterministic evidence already answers the useful question. |
| Planning or TODO decomposition | Keep normal flow | Generative/relational reasoning; classifier error can distort the whole plan. |
| Coding model/provider/tier selection | Keep deterministic route policy | No project calibration showing Jev signals improve the evidence ladder. |
| Context/requirement filtering | Do not use | False negatives can silently remove correctness-critical evidence. |
| Test approval/task completion | Never delegate | Deterministic validation remains authoritative. |
| Service/resource monitoring | Never delegate | PID/health/timeout evidence is cheaper and more reliable in code. |

## Cost and resilience policy

Jev remains disabled by default. Enabling it requires `assistant.provider: jev`; a `TYPESAFE_API_KEY` alone never activates anything. Missing credentials cause zero calls and zero ledger entries. Valid dispatches are capped at one reservation per task and four per plan by default. Duplicate evidence is not resent. There is no automatic Jev retry and no advisory-provider fallback.

HTTP/auth/capacity/credit/network/timeout/invalid-response failures return to the existing worker/validator flow. `unknown` or confidence below the configured threshold is not forwarded to the worker. Valid API responses persist the returned model plus API-reported input/output token counts so real cost can be measured later.

The implementation uses the fixed TypeSafe endpoint directly through the Python standard library, with no SDK dependency, no inherited proxy, and no redirects for an Authorization-bearing request.

## Context-loading policy

The normal skill entrypoint loads no Jev-specific guide. `ASSISTANTS.md` is loaded only for setup, eligible advisory failure, or maintenance. It then routes to exactly one provider-specific reference:

- `ASSISTANT_JEV.md` only for Jev;
- `ASSISTANT_CLAUDE.md` only for Claude;
- neither when advice is disabled or the profile is unsupported.

Jev is deliberately absent from the coding-provider list, so ordinary implementation routing never loads or considers it.

## Security notes

Failure evidence is redacted before fixed-size truncation. The API key is read only at dispatch and never placed in request state, logs, configuration, or worker prompts. Jev output can only select a registered class; the worker receives a locally generated fixed hypothesis rather than model-authored instructions. Advice cannot mutate authoritative failure class, task status, tests, commands, route, acceptance, or cleanup.

## Sources

Official sources checked 2026-09-30:

- https://docs.typesafe.ai/api — `POST /v1/systemone`, response usage, and documented 401/422/429/529 behavior.
- https://docs.typesafe.ai/primitives/choice — finite Choice contract, probabilities, and confidence.
- https://docs.typesafe.ai/models — current `jev-1.13.0`, pricing/context limits, and alias behavior.

The model is pinned rather than using `jev-latest`, because TypeSafe documents that aliases move and can change answers without a code change.
