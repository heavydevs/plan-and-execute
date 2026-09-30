# Optional Jev integration: implementation plan

Base: `6be46885ad691d3d43557a42fc2fd36a804b7eba`. Work branch: `JEV`.
Do not merge into `main` as part of this request.

## Request and decision

Keep Jev optional and preserve ordinary execution without configuration, credentials,
or available inference. Minimize calls and conditional instruction loading. Implement
only a narrowly justified use: non-authoritative diagnostic focus after repeated,
ambiguous validation failures, at the existing advisory hook.

Do not use Jev to generate plans/code, select coding models, filter out requirements,
approve tests, monitor numerical resource state or control cleanup. Those applications
have either no demonstrated workload benefit or authority/safety costs disproportionate
to this integration. A typed diagnostic label has architectural fit, not demonstrated
net savings or measured diagnostic accuracy.

## Native Plan and Execute workstreams

The real controllers created a schema-4 plan, attached a schema-2 study, mapped six
requirements, validated the study/plan/resource-map gates and activated three TODOs.
The 79 base skill files were recovered from the matching CI artifact and their Git blob
hashes checked against the preceding study. This is not a full local repository clone.
Codex/Claude executables were unavailable: execution is host-managed, not independent
model workers. Independent model review is not claimed.

| TODO | Route intent | Scope | Acceptance |
|---|---|---|---|
| 001 | strong/high | Typed Choice, bounded transport, durable attempt ledger | Never change task/route authority; reservations survive interruption. |
| 002 | standard/medium | Optional configuration, lazy dispatch, selected guides | Missing opt-in/key makes no Jev call/import/state; ordinary flow survives failures. |
| 003 | strong/medium | Whole-skill review, regressions, packaging and publication | Preserve existing controllers and main; publish exact tested content and disclose limits. |

No shared/global context or evolving pattern registry was added: this narrow dependency
chain does not justify recurring context. Disposable native plan state is cleaned only
after validated completion and handoff; implementation and these review notes remain.

## Recovery checkpoint

TODO 001 completed after 20 offline contract tests. TODO 002 has 26 passing offline
contract/integration tests, including the real runner with fake worker/transport and a
quota-like failure. The next gate is whole-skill regression and final publication.
No authenticated Jev request was made. These tests establish software behavior, not
actual billing, diagnostic quality, native Windows transport or net token savings.

## Sources and evaluation gate

Official contracts checked on 2026-09-30:

- https://docs.typesafe.ai/api
- https://docs.typesafe.ai/primitives/choice
- https://docs.typesafe.ai/models
- https://docs.typesafe.ai/model-jaggedness/jev-1.13

Pin the model; keep the optional evaluator outside coding-provider policy. Include an
insufficient-evidence option and validate the complete typed response. No retries are
needed for optional advice: continue normally and apply a bounded persistent cooldown.
The documented HTTP errors include 401, 422, 429 and 529; handling 402/403 defensively
does not claim that TypeSafe uses a verified credit-exhaustion contract.

Before recommending broad adoption, compare ordinary execution with opt-in Jev on the
same consented, representative failures and independently validated outcomes. Measure
cost per validated TODO, regressions, omissions, retries, latency, abstention, dispatch
frequency and returned/unknown usage. Use held-out cases and do not equate agreement
with the current worker to correctness. Disable the adviser if outcome quality or cost
worsens. Keep speculative applications outside this implementation.
