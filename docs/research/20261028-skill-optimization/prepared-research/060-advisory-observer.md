# 060 - Advisory Observer: research revision 2

Date: 2026-10-28. Feature: `F028`. Implementation TODO `060`; independent review TODO `061`. Product baseline: `0.11.0` / tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Prepared design evidence, not implemented code. Implementation and independent review remain pending.**

## Recommended direction

Keep observation deterministic by default and invoke one bounded, genuinely read-only advisory pass only for novel ambiguity; treat its output as expiring untrusted data.

This is a conditional engineering recommendation for this repository, not a proof of a global optimum or a measured saving on the user's workload.

## Change from the previous report

The new compatibility evidence removes prompt-only or misleading safe-mode assumptions. The revision adds cross-chunk redaction, freshness binding and a zero-model-cost healthy path.

The previous report is retained under `docs/plans/20261028-skill-optimization/history/research-round-1/prepared-research/` for audit. New W-prefixed sources below are the current-round evidence; old E-prefixed sources remain background.

## Questions and repository evidence

- Verify least-privilege tool restrictions, schema validation and untrusted advice boundaries.
- Compare deterministic monitoring with event-triggered model diagnosis and cheap fallback chains.

**Baseline observations:**
- assistant_triage has a strict advice schema, eligibility triggers and a capsule that does not authoritatively change task state. observer adds a separate restricted diagnostic route.
- assistant_triage.evidence slices command/head/tail before calling redact, despite the redactor's intended redact-before-truncate contract. Boundary-sensitive sanitation needs a regression test.
- Tool restrictions and startup guards are code-level controls; a summary prompt alone cannot enforce read-only behavior.

All listed file hashes matched the preserved 0.11.0 source in this revision. This is integrity checking, not a second full code audit.

| Code anchor | SHA-256 | Selected symbols / location |
|---|---|---|
| `skill/plan-and-execute/scripts/observer.py` | `ad84f96624f85c860edd925ed5bf354dc805b726f943bf14a435f6ef5179b322` | native_invoke:259; diagnose:337 |
| `skill/plan-and-execute/scripts/assistant_triage.py` | `af9d5a1054aae9c747916a60f3f0c836209f878c1c31638909eedcd28d9109c2` | redact:53; evidence:102; validate_advice:137; hint:412 |
| `skill/plan-and-execute/references/ASSISTANTS.md` | `8a7e0edce46d96093a5c7e641a4fc093c1ee552da23af8aaee5abb41d4886b32` | # Bounded advisory validation triage:1; ## Activation and cost:5; ## Native profiles and the important limitation:15; ## Persistence and ownership:25 |

## Deeper analysis and competing approaches

### 1. Design analysis

An observer should not be another autonomous implementer with the same filesystem privileges. First collect deterministic exit, health and progress evidence; only an unresolved anomaly with a new fingerprint can justify a bounded advisory call. Repeated healthy polling, repeated identical failures and unavailable observer models should not spend tokens.

### 2. Design analysis

The advisory packet should contain whitelisted metadata, bounded sanitized excerpts and assigned file references, not the full repository, environment or historical transcript. Redact before taking head/tail slices. Bind the result to task, attempt, code/evidence generation and anomaly signature so old advice cannot leak into a later unrelated failure.

### 3. Design analysis

Read-only is an enforced capability: tool allowlists, filesystem restrictions and network policy must support it. Provider defaults, plan-mode prompts and sandbox names are insufficient. The adapter skips unsupported advice safely and retains deterministic diagnosis. Do not downgrade the implementation capability or widen permissions merely to obtain an observer response.

### 4. Design analysis

A schema-valid suggestion can still be wrong or malicious. Validate allowed fields and path references, label hypotheses unverified, and prohibit the advisor from changing authoritative classification, route, status or acceptance. The implementation worker verifies the hypothesis against evidence; advice is consumed once and expires.

The analysis above is a repository design synthesis. The linked publications establish capabilities or bounded empirical observations, not this skill's future measured performance. Exact account behavior and installed-version compatibility remain implementation-time checks.

| Alternative | Benefit | Cost / failure risk | Disposition |
|---|---|---|---|
| Continuous model log watcher | Flexible free-text reasoning | Expensive and excessive privilege/context | Reject |
| Only deterministic monitoring | Cheapest and predictable | May leave ambiguous diagnosis | Default |
| One event-triggered read-only advisor | Useful bounded second opinion | Needs genuine confinement and freshness | Optional recommendation |
| Advisor can repair and mark complete | Fewer role transitions | Breaks independent acceptance and authority | Reject |

## Ownership and scope boundary

This implementation owns its declared write scope and acceptance tests. Its following review checks the actual changed code; prepared research is not acceptance evidence.

Implementation may preserve an already-satisfied invariant with a regression test and a documented no-change rationale; do not add code solely to make every recommendation produce a diff.

## Implementation instructions

1. Move sanitation ahead of any truncation of model-facing data, including command strings, output windows and failure summaries. Test split credential/header cases.
2. Keep explicit diagnostics local: syntax/lint errors, known missing tools and clear health failures do not need a model. Trigger one bounded diagnosis only for ambiguous stagnation or repeated unclear evidence.
3. Qualify each observer fallback for true read-only/no-tool or restricted-tool execution. Missing confinement disables the candidate rather than escalating its permissions.
4. Validate advice schema, finite confidence, allowed evidence IDs and byte limits. Label hypotheses unverified and bind the capsule to the next eligible attempt only.
5. Record advisory invocation cost separately and never let advice complete tasks, edit files, choose authoritative failure classes or delete evidence.
6. Invoke advice only for a new unresolved anomaly and cap attempts, input/output size and permitted tools.
7. Redact before truncation and bind suggestions to evidence generation; consume once as unverified data.
8. Skip advisory routes lacking proven read-only enforcement while preserving deterministic monitoring.

## Acceptance and counterexamples

- Clear deterministic errors invoke no advisory model.
- A planted Authorization header or long secret split at a prior slice boundary is redacted before prompt construction.
- Unknown evidence IDs, extra JSON fields, non-finite confidence and oversized hypotheses are rejected.
- Unavailable cheap observer falls back only to another allowed restricted observer, otherwise skips.
- Advice cannot mutate route/status and expires after its intended attempt.
- A healthy run and repeated identical anomaly trigger no extra model calls.
- A token spanning excerpt boundaries is removed before serialization.
- A suggestion that requests commands, writes or status changes is rejected as data outside its role.
- An old-generation suggestion cannot affect a new attempt.

## Cost, latency and quality decision

Advisor cost is justified only when expected avoided diagnosis/repair cost exceeds the call and anchoring risk under the quality floor. Use zero model tokens for routine health/progress.

Compare total cost per independently validated outcome against the current implementation and a simpler qualified single-worker baseline. Count failed attempts, reviews, cache writes/reads, advisory calls and tool/runtime overhead in their native units. Unknown prices, quotas or usage remain unknown, not zero. Preserve capability and security floors; no automatic rollout follows from fixture replay alone.

## Evidence used in this revision

- [W-INJECTION] OWASP, [LLM Prompt Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-LOGGING] OWASP, [Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-SELFCORRECT] Huang et al. / ICLR, [Large Language Models Cannot Self-Correct Reasoning Yet](https://proceedings.iclr.cc/paper_files/paper/2024/hash/8b4add8b0aa8749d80a34ca5d941c355-Abstract-Conference.html). Accessed 2026-10-28. Reading scope: Conference abstract inspected; historical models/tasks, no full reproduction. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-AGY-PERMISSIONS] Google, [Permissions](https://antigravity.google/docs/permissions/). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-QWEN-HEADLESS] QwenLM, [Headless mode](https://qwenlm.github.io/qwen-code-docs/en/users/features/headless/). Accessed 2026-10-28. Reading scope: Official headless guide sections on flags, safe-mode, JSON and budgets inspected. Public source reading is not an independent code review or reproduction of vendor experiments.

Prior-round context: [E044], [E024], [E020], [E015], [E043]. See `SOURCE_REGISTER.md` for records; these were not all independently refreshed.

Search themes inspected in this round: OWASP prompt injection untrusted tool output least privilege; OWASP logging sensitive redaction; LLM self correction external feedback; Antigravity permissions workspace write; Qwen safe-mode read-only.

## Unverified limits and refresh triggers

- Actual sandbox enforcement and account-specific observer economics require authorized live qualification. This report does not certify any hosted model as universally read-only.
- No observer was dispatched. Read-only eligibility requires adapter/host tests, not this report or a provider marketing label.

No authenticated provider invocation, live quota/cost benchmark, independent model review, or Windows runtime test was performed in this research revision.

Refresh only evidence contradicted by the installed CLI, selected account/billing plan or changed code contract. Unknown required capability blocks that candidate; it does not justify widening permissions.
