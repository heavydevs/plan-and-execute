# 030 - Claude: research revision 2

Date: 2026-10-28. Feature: `F013`. Implementation TODO `030`; independent review TODO `031`. Product baseline: `0.11.0` / tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Prepared design evidence, not implemented code. Implementation and independent review remain pending.**

## Recommended direction

Keep the Claude CLI adapter as the compatibility reference, add versioned capability fixtures and least-privilege role profiles, and evaluate SDK/native workflows only behind an explicit adapter boundary.

This is a conditional engineering recommendation for this repository, not a proof of a global optimum or a measured saving on the user's workload.

## Change from the previous report

The research adds worktree starting-revision risk, tool inheritance and version-specific budget/session semantics. A native SDK migration is not presumed to be a cost-saving rewrite.

The previous report is retained under `docs/plans/20261028-skill-optimization/history/research-round-1/prepared-research/` for audit. New W-prefixed sources below are the current-round evidence; old E-prefixed sources remain background.

## Questions and repository evidence

- Verify print mode, no-session-persistence, structured schema, tool restrictions and resume flags.
- Measure subscription quota separately from API cash and cache write/read economics.

**Baseline observations:**
- build_worker_command uses Claude print mode with disabled session persistence; a subsequent fresh process cannot be assumed to remember the previous attempt.
- The runner has separate worker and summary command builders. A read-only summary must remain a restricted command path rather than a general implementation worker with a polite prompt.

All listed file hashes matched the preserved 0.11.0 source in this revision. This is integrity checking, not a second full code audit.

| Code anchor | SHA-256 | Selected symbols / location |
|---|---|---|
| `skill/plan-and-execute/scripts/run_isolated.py` | `00ffc3bce6093d63198b910eaad7e8a76f739dd226eb6399c2e6fa54301908df` | build_worker_command:1034; build_summary_command:2319 |
| `skill/plan-and-execute/scripts/provider_self_test.py` | `a38f2da1c85a09e431c67333a2a29ed2cef8dc5bf27d5ac62d4fa0c82268e1dd` | test_codex_output_schema_is_api_compatible:470 |
| `skill/plan-and-execute/references/MODEL_ROUTING_CLAUDE.md` | `ba6e2fe3334f9204445aaf20ea28fa1675638029b7de568bfcb9068693af999a` | # Claude Code model routing:1; ## Current capability map:5; ## Elevation mechanics (how a route is actually obtained):22; ## DIRECT mode:38 |

## Deeper analysis and competing approaches

### 1. Design analysis

The existing ephemeral headless worker is a useful portable contract. Keep exact argv fixtures and parse final result, partial result and usage separately. Unsupported flags must fail preflight with an actionable compatibility reason rather than being silently dropped or replaced with a more permissive mode.

### 2. Design analysis

A review or observer role needs an actual restricted tool/sandbox boundary. A prompt saying read-only is not enforcement; inherited tools and project settings can broaden access. Give the worker only assigned context and record actual CLI/model identity. A claimed maximum tier is not evidence that the requested native effort was used.

### 3. Design analysis

Native subagents, SDK sessions and forks can reduce repeated setup or share cached context, but they add distinct lifecycle and persistence contracts. Keep them optional until they preserve cancellation, independent validation, retry accounting and source revision. The relevant comparison is end-to-end validated cost against the existing CLI, not fewer lines of orchestration code.

### 4. Design analysis

Budget and persistence options should be per invocation and documented by supported version. Do not alter user-global configuration as a convenience. Keep secrets in environment references, record neither values nor raw authentication traces, and do not convert a subscription login into API billing automatically.

The analysis above is a repository design synthesis. The linked publications establish capabilities or bounded empirical observations, not this skill's future measured performance. Exact account behavior and installed-version compatibility remain implementation-time checks.

| Alternative | Benefit | Cost / failure risk | Disposition |
|---|---|---|---|
| Keep current argv without probing | Stable short term | New releases can change semantics | Legacy fixture only |
| Versioned CLI contract | Smallest reliable change | Requires fixtures for supported versions | Recommended |
| Replace with Agent SDK now | Rich orchestration API | New lifecycle and dependency surface | Defer until measured benefit |
| Native subagent/fork optimization | Potential context/cache reuse | Tool inheritance and isolation differ | Opt-in and tested |

## Ownership and scope boundary

This implementation owns its declared write scope and acceptance tests. Its following review checks the actual changed code; prepared research is not acceptance evidence.

Implementation may preserve an already-satisfied invariant with a regression test and a documented no-change rationale; do not add code solely to make every recommendation produce a diff.

## Implementation instructions

1. Add recorded help/version fixtures and a capability map for the exact installed Claude CLI. Probe flags non-generatively and fail visibly on unsupported combinations.
2. Preserve fresh-context defaults. Separate optional resume/session-retention experiments from normal execution and document that conversation persistence does not snapshot source files.
3. Test structured report extraction, schema rejection, malformed envelopes and nonzero statuses separately. A valid JSON shape cannot replace deterministic product validation.
4. Qualify read-only paths with an actual tool allowlist/sandbox boundary and clean environment, including third-party endpoint profiles.
5. Capture available usage fields in native units, retaining null for absent values. Do not equate subscription tokens with API invoices or assume a universal cache rate.
6. Pin documented CLI capabilities by version and fail on unsupported security or structured-output options.
7. Test review tool inheritance and source-revision isolation rather than trusting a read-only prompt.
8. Compare SDK or native workflows with CLI execution only after lifecycle, billing and validation equivalence checks.

## Acceptance and counterexamples

- Default worker argv retains no-session-persistence and existing approved permission behavior.
- Summary mode cannot write a planted repository file or execute an unapproved mutating tool in a supported test environment.
- Invalid JSON, missing report fields, quota errors and semantic failures take different paths.
- A model alias mapped through another endpoint is reported with host and backend identity.
- Unknown usage is null and no secret environment values enter diagnostics.
- A partial max-turn result cannot complete a task.
- No-session-persistence does not trigger an automatic resume attempt.
- Unsupported permission restrictions fail closed without global settings changes.
- A restricted reviewer cannot invoke inherited write tools.

## Cost, latency and quality decision

Preserve the working CLI unless SDK startup/cache savings exceed migration, maintenance and review costs at equal outcome quality. Record subscription and API costs separately.

Compare total cost per independently validated outcome against the current implementation and a simpler qualified single-worker baseline. Count failed attempts, reviews, cache writes/reads, advisory calls and tool/runtime overhead in their native units. Unknown prices, quotas or usage remain unknown, not zero. Preserve capability and security floors; no automatic rollout follows from fixture replay alone.

## Evidence used in this revision

- [W-CLAUDE-CLI] Anthropic, [CLI reference](https://code.claude.com/docs/en/cli-reference). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-CLAUDE-SUBAGENTS] Anthropic, [Create custom subagents](https://code.claude.com/docs/en/sub-agents). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-CLAUDE-CACHE] Anthropic, [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-COST] Anthropic, [Optimizing for cost and intelligence](https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence). Accessed 2026-10-28. Reading scope: Cost/context/delegation sections and coding measurement footnote inspected, including sample, hidden-test grading and paired intervals. Results are vendor-specific, not measured for this repository. Public source reading is not an independent code review or reproduction of vendor experiments.

Prior-round context: [E015], [E017], [E054], [E052]. See `SOURCE_REGISTER.md` for records; these were not all independently refreshed.

Search themes inspected in this round: Claude Code CLI reference no-session-persistence json schema max budget; Claude subagents tools permissions effort worktree; Claude prompt caching TTL cost.

## Unverified limits and refresh triggers

- Installed CLI version, current account authentication and maximum authorized model are not verified in this session.
- No installed or authenticated Claude binary was run. The current documentation is a compatibility design input, not proof of the user installed version.

No authenticated provider invocation, live quota/cost benchmark, independent model review, or Windows runtime test was performed in this research revision.

Refresh only evidence contradicted by the installed CLI, selected account/billing plan or changed code contract. Unknown required capability blocks that candidate; it does not justify widening permissions.
