# 032 - Codex: research revision 2

Date: 2026-10-28. Feature: `F014`. Implementation TODO `032`; independent review TODO `033`. Product baseline: `0.11.0` / tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Prepared design evidence, not implemented code. Implementation and independent review remain pending.**

## Recommended direction

Separate Codex event-stream parsing from final-schema validation, retain explicit sandbox/approval contracts and make session reuse an opt-in same-provider operation.

This is a conditional engineering recommendation for this repository, not a proof of a global optimum or a measured saving on the user's workload.

## Change from the previous report

The revision corrects the stale assumption of universally free OpenAI cache writes and adds event-order, partial-output and session-binding failure cases.

The previous report is retained under `docs/plans/20261028-skill-optimization/history/research-round-1/prepared-research/` for audit. New W-prefixed sources below are the current-round evidence; old E-prefixed sources remain background.

## Questions and repository evidence

- Verify ephemeral runs, exec resume/fork, required nullable fields and current sandbox flags.
- Compare native compaction with short artifact handoffs using pinned CLI evidence.

**Baseline observations:**
- The Codex worker uses exec and ephemeral mode. The completion schema adapter makes optional fields required-nullable for the supported structured-output contract.
- run_concise modifies the effective worker prompt and therefore requires composed-entrypoint tests, not only a raw argv golden.

All listed file hashes matched the preserved 0.11.0 source in this revision. This is integrity checking, not a second full code audit.

| Code anchor | SHA-256 | Selected symbols / location |
|---|---|---|
| `skill/plan-and-execute/scripts/run_isolated.py` | `00ffc3bce6093d63198b910eaad7e8a76f739dd226eb6399c2e6fa54301908df` | codex_output_schema:650; build_worker_command:1034; parse_provider_report:1412 |
| `skill/plan-and-execute/scripts/provider_self_test.py` | `a38f2da1c85a09e431c67333a2a29ed2cef8dc5bf27d5ac62d4fa0c82268e1dd` | sample_route:20; sample_report:29; test_default_provider_policy:46; test_worker_command_adapters:63 |
| `skill/plan-and-execute/references/MODEL_ROUTING_CODEX.md` | `3cde22d4a24a081052aebfd7d992c8d1c3e4577745aa6f8ea324a7460f280024` | # Codex model routing:1; ## Current capability map:5; ## Elevation mechanics (how a route is actually obtained):22; ## DIRECT mode:37 |

## Deeper analysis and competing approaches

### 1. Design analysis

JSONL progress events are not the task completion document. A stream can contain tool starts, transient errors, usage and a terminal event; the final structured output still has to meet the completion schema and pass runner validation. Parse incrementally with maximum event size and explicit handling of truncated final records.

### 2. Design analysis

Ephemeral execution supports the fresh-context contract but cannot promise same-session recovery. An optional exec-resume path must bind to one saved session, provider, repository and task attempt. Never use the most recent unrelated session as a recovery shortcut. Cross-provider handoff should remain artifact-based rather than pretending a provider session can migrate.

### 3. Design analysis

Sandbox and approval policy are different: one constrains where effects can occur, the other decides when approval is requested. Compatibility tests must cover both and reject permissive fallback when a read-only reviewer cannot be established. Keep machine-readable errors out of the capability-failure ladder when the cause is permission or environment.

### 4. Design analysis

A stable prompt prefix is useful, but cache prices and retention are model-generation specific. Let the cost ledger consume reported usage and versioned billing evidence. Existing no-write-cost comments and estimates must be scoped to their historical source rather than copied into new economics.

The analysis above is a repository design synthesis. The linked publications establish capabilities or bounded empirical observations, not this skill's future measured performance. Exact account behavior and installed-version compatibility remain implementation-time checks.

| Alternative | Benefit | Cost / failure risk | Disposition |
|---|---|---|---|
| Parse last stdout line as success | Simple | Can accept an event or truncated report | Reject |
| Incremental events plus separate final schema | Bounded memory and clear semantics | Needs malformed-stream fixtures | Recommended |
| Resume any recent session | Potential reuse | Cross-task contamination | Reject |
| Opt-in exact-session resume | Preserves provider-local history | Storage/privacy and replay cost | Evaluate only for same-provider recovery |

## Ownership and scope boundary

This implementation owns its declared write scope and acceptance tests. Its following review checks the actual changed code; prepared research is not acceptance evidence.

Implementation may preserve an already-satisfied invariant with a regression test and a documented no-change rationale; do not add code solely to make every recommendation produce a diff.

## Implementation instructions

1. Record CLI version/help and model-discovery evidence without starting a paid task; select tested capability branches for exec, structured output and sandbox flags.
2. Maintain a schema transformation test for nested objects, required nullable fields, additionalProperties and invalid outputs. Refusal or incomplete output is not a passing task.
3. Keep ephemeral mode for normal cross-task isolation. Same-provider resume/fork is a separate opt-in contract, never a way to transfer private reasoning state to another provider.
4. Use read-only sandbox for observation/review where supported and verify that output/log paths can still be written only in owned locations.
5. Parse JSONL events incrementally and preserve the final report independently of progress text. Link deterministic validation evidence through the production prompt.
6. Parse bounded JSONL events independently from the final completion schema; reject truncated or missing terminal reports.
7. Bind optional session reuse to exact provider, repository and task identity; preserve ephemeral default.
8. Remove universal no-cache-write-cost assumptions from planned economics and use model-versioned reported usage.

## Acceptance and counterexamples

- Schema fixtures remain accepted by the adapter without weakening additionalProperties checks.
- Ephemeral default argv and composed static prefix remain stable.
- Malformed events, partial final JSON, a nonzero exit and a valid blocked report remain distinguishable.
- An unsupported sandbox/effort flag fails preflight instead of falling back to unrestricted execution.
- Cache and cost records distinguish reported usage from estimates and do not import outdated no-write-cost assumptions.
- A successful progress event followed by malformed final JSON cannot complete a task.
- A resume request cannot attach another repository session.
- Sandbox mismatch is an environmental or policy block, not a model capability escalation.
- Cache-write usage remains distinct from uncached input and cache reads.

## Cost, latency and quality decision

Avoid repeated reconstruction only when exact-session reuse is permitted and measured; include retained context, cache writes, reads and output in total cost.

Compare total cost per independently validated outcome against the current implementation and a simpler qualified single-worker baseline. Count failed attempts, reviews, cache writes/reads, advisory calls and tool/runtime overhead in their native units. Unknown prices, quotas or usage remain unknown, not zero. Preserve capability and security floors; no automatic rollout follows from fixture replay alone.

## Evidence used in this revision

- [W-CODEX-EXEC] OpenAI, [Non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-CODEX-SECURITY] OpenAI, [Security](https://learn.chatgpt.com/docs/security). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-OPENAI-CACHE] OpenAI, [Prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-EVALSKILLS] OpenAI, [Testing Agent Skills Systematically with Evals](https://developers.openai.com/blog/eval-skills). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

Prior-round context: [E019], [E020], [E052], [E021]. See `SOURCE_REGISTER.md` for records; these were not all independently refreshed.

Search themes inspected in this round: Codex non interactive exec json ephemeral output schema; Codex security sandbox approval policy; OpenAI prompt caching cache writes pricing.

## Unverified limits and refresh triggers

- No real Codex invocation or sandbox escape test was executed; fake CLI contract tests cannot certify provider service behavior.
- No Codex executable, account or billing record was tested. Current docs do not establish all supported versions or account-level model access.

No authenticated provider invocation, live quota/cost benchmark, independent model review, or Windows runtime test was performed in this research revision.

Refresh only evidence contradicted by the installed CLI, selected account/billing plan or changed code contract. Unknown required capability blocks that candidate; it does not justify widening permissions.
