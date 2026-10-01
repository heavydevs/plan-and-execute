# Bounded advisory validation triage

Load only when configuring or diagnosing an eligible failure. The implementation owner and deterministic validators retain all authority.

## Activation and cost

Disabled by default. Opt-in authorizes sending only selected redacted failure evidence to the configured advisory provider. Redaction is best effort, not a guarantee that arbitrary confidential text contains no secrets.

The runner asks for advice only after a deterministic validation failure. Eligible triggers are an ambiguous repeated failure, consecutive unhealthy samples from the same mapped resource/check, or a stall already confirmed by the resource watcher. Success, first unambiguous failure, and recognized lint/type/syntax diagnostics make no advisory call.

Defaults reserve at most one call per task and four calls per plan. A reservation survives interruption, so resume cannot replay a possibly billed request. Evidence is capped before dispatch; duplicate evidence is not resent. Provider errors, missing credentials, rate/capacity/credit problems, low-confidence Jev output, timeout, malformed output, and budget exhaustion leave the ordinary failure flow intact. There is no advisory-provider fallback or retry loop.

Only bounded first/last validation excerpts, command and failure counters form E1..E3. No repository, whole plan, chat history, credential files, or full logs are loaded. Advice remains unverified data and cannot mutate manifest state, authoritative failure class, tier, tests, commands, acceptance, cleanup, or completion.

## Load exactly one provider guide

After configuration identifies the provider, load only its guide:

- `assistant.provider: jev` -> [ASSISTANT_JEV.md](ASSISTANT_JEV.md)
- `assistant.provider: claude` -> [ASSISTANT_CLAUDE.md](ASSISTANT_CLAUDE.md)
- any other legacy/unsupported profile -> skip advice and continue normally; load no provider guide

Do not load either provider guide when advice is disabled. Coding-provider routes are independent from advisory-provider selection.

## Persistence and ownership

`results/<task>-assistant.json` is the bounded per-task ledger. A plan-level lock makes the aggregate call cap atomic across tasks; each task also has its own exclusive reservation lock. Interrupted `reserved` attempts count. Evidence hashes deduplicate across resume. Stale locks require operator inspection; never auto-delete them just to obtain another attempt.

Accepted advice becomes a short explicitly untrusted capsule for the next worker only while its recorded functional-failure counter is current. The worker verifies the suggestion against repository/test evidence before acting. Provider confidence is an advisory signal, not proof of correctness.

Telemetry records provider, trigger, signature, status/reason, bounded character counts and elapsed time. Jev additionally records the returned model and API-reported input/output token counts when a valid response is received. Missing usage is never converted to zero.

Comparative quality/cost and authenticated-provider behavior must be evaluated separately from offline contract tests. Research belongs in repository `docs/`, not ordinary worker prompts.
