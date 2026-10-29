# F028 / task 060 - Read-only observer and diagnostic assistant

Date: 2026-10-28. Product baseline: 0.11.0, tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Research prepared; implementation pending; independent review pending.** This report is an implementation input, not a completion receipt. No external reviewer is impersonated.

## Decision and scope

**Recommendation (engineering inference):** Use deterministic monitoring by default and event-triggered, read-only, untrusted diagnostic advice with bounded fallback.

## Questions addressed

- Verify least-privilege tool restrictions, schema validation and untrusted advice boundaries.
- Compare deterministic monitoring with event-triggered model diagnosis and cheap fallback chains.

## Repository evidence

The following are static-code observations against the pinned baseline, not results from authenticated providers:

- assistant_triage has a strict advice schema, eligibility triggers and a capsule that does not authoritatively change task state. observer adds a separate restricted diagnostic route.
- assistant_triage.evidence slices command/head/tail before calling redact, despite the redactor's intended redact-before-truncate contract. Boundary-sensitive sanitation needs a regression test.
- Tool restrictions and startup guards are code-level controls; a summary prompt alone cannot enforce read-only behavior.

### Read targets and integrity

- `skill/plan-and-execute/scripts/observer.py` (SHA-256 `ad84f96624f85c860edd925ed5bf354dc805b726f943bf14a435f6ef5179b322`): `native_invoke` L259-304; `diagnose` L337-411
- `skill/plan-and-execute/scripts/assistant_triage.py` (SHA-256 `af9d5a1054aae9c747916a60f3f0c836209f878c1c31638909eedcd28d9109c2`): `redact` L53-62; `evidence` L102-124; `validate_advice` L137-151; `hint` L412-428
- `skill/plan-and-execute/references/ASSISTANTS.md` (SHA-256 `8a7e0edce46d96093a5c7e641a4fc093c1ee552da23af8aaee5abb41d4886b32`): `# Bounded advisory validation triage` L1; `## Activation and cost` L5; `## Native profiles and the important limitation` L15; `## Persistence and ownership` L25

## External basis

- [E044] [Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html) - OWASP; accessed 2026-10-28.
- [E024] [Permissions](https://antigravity.google/docs/permissions/) - Google; accessed 2026-10-28.
- [E020] [Security](https://learn.chatgpt.com/docs/security) - OpenAI; accessed 2026-10-28.
- [E015] [Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference) - Anthropic; accessed 2026-10-28.
- [E043] [Monitoring Distributed Systems, Site Reliability Engineering chapter 6](https://sre.google/sre-book/monitoring-distributed-systems/) - Google SRE; accessed 2026-10-28.

Consult only these entries in `SOURCE_REGISTER.md` for the checked finding and scope. Provider documentation establishes an interface, not this account's available quota or a universal ranking of model quality. The proposed design below combines that evidence with the repository observations; it is not a vendor guarantee.

## Alternatives and cost/quality tradeoffs

| Disposition | Approach | Tradeoff |
|---|---|---|
| current_baseline | Continuously ask a cheap LLM to inspect output | Still costly at scale and duplicates deterministic checks. |
| recommended | Event-gated bounded advisor behind a security boundary | Pays only for ambiguous diagnosis and preserves deterministic authority. |
| rejected | Let the observer repair code or clean arbitrary logs | Violates role isolation and risks modifying evidence or the product without proper validation. |

## Implementation instructions

1. Move sanitation ahead of any truncation of model-facing data, including command strings, output windows and failure summaries. Test split credential/header cases.
2. Keep explicit diagnostics local: syntax/lint errors, known missing tools and clear health failures do not need a model. Trigger one bounded diagnosis only for ambiguous stagnation or repeated unclear evidence.
3. Qualify each observer fallback for true read-only/no-tool or restricted-tool execution. Missing confinement disables the candidate rather than escalating its permissions.
4. Validate advice schema, finite confidence, allowed evidence IDs and byte limits. Label hypotheses unverified and bind the capsule to the next eligible attempt only.
5. Record advisory invocation cost separately and never let advice complete tasks, edit files, choose authoritative failure classes or delete evidence.

## Acceptance tests to implement and run

- [ ] Clear deterministic errors invoke no advisory model.
- [ ] A planted Authorization header or long secret split at a prior slice boundary is redacted before prompt construction.
- [ ] Unknown evidence IDs, extra JSON fields, non-finite confidence and oversized hypotheses are rejected.
- [ ] Unavailable cheap observer falls back only to another allowed restricted observer, otherwise skips.
- [ ] Advice cannot mutate route/status and expires after its intended attempt.

These cases are proposed test obligations. A research report or a fake-provider fixture cannot establish production model performance. Record executed commands, exit codes, source state and logs in the task's implementation receipt.

## Economic evaluation

Measure avoided/used advisor calls, anomaly detection and subsequent validated repair. A low per-token price does not make a continuously polling model cheaper than deterministic tools.

## Rollout and compatibility

Use the existing small deterministic helpers and compose through `run_concise.py` where applicable. Preserve disabled-mode behavior, persisted schema compatibility and locally edited installed copies. Add a behavior-changing policy only behind an explicit tested option. Do not add a framework, a paid model call or a global setting merely to satisfy this report. If current code already satisfies a proposed invariant, keep it and add the missing regression evidence instead of duplicating the mechanism.

## Limits and unresolved verification

- Actual sandbox enforcement and account-specific observer economics require authorized live qualification. This report does not certify any hosted model as universally read-only.
- No paid model benchmark, Windows live execution or independent maximum-model code review was performed during this research. Those are distinct future acceptance activities where applicable.

## Task handoff

Task **060** now implements this recommendation; task **061** reviews the resulting code and requires corrections before acceptance. Read this report, its JSON decision record and only the assigned source paths. Do not repeat broad research unless a material version mismatch invalidates a specific finding. No second plan is required.
