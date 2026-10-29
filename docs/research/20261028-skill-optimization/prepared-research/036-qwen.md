# 036 - Qwen: research revision 2

Date: 2026-10-28. Feature: `F016`. Implementation TODO `036`; independent review TODO `037`. Product baseline: `0.11.0` / tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Prepared design evidence, not implemented code. Implementation and independent review remain pending.**

## Recommended direction

Add a versioned Qwen headless contract with explicit security and total-run budgets, and prevent native goal/retry loops from bypassing the orchestrator policy.

This is a conditional engineering recommendation for this repository, not a proof of a global optimum or a measured saving on the user's workload.

## Change from the previous report

The deeper guide reveals safe-mode is customization isolation, not a sandbox, and unattended retry can be unbounded. The adapter must not use either as a safe automatic fallback.

The previous report is retained under `docs/plans/20261028-skill-optimization/history/research-round-1/prepared-research/` for audit. New W-prefixed sources below are the current-round evidence; old E-prefixed sources remain background.

## Questions and repository evidence

- Inspect Qwen headless JSON, approvals, safe read-only execution and session persistence.
- Compare budget, cancellation and resume contracts without assuming Claude-compatible flags.

**Baseline observations:**
- The Qwen adapter currently constructs a headless invocation with configured approval/safe-mode controls and a report schema.
- Provider documentation distinguishes JSON/stream output, session persistence and budget exhaustion; those distinctions must survive normalization in the shared runner.

All listed file hashes matched the preserved 0.11.0 source in this revision. This is integrity checking, not a second full code audit.

| Code anchor | SHA-256 | Selected symbols / location |
|---|---|---|
| `skill/plan-and-execute/scripts/run_isolated.py` | `00ffc3bce6093d63198b910eaad7e8a76f739dd226eb6399c2e6fa54301908df` | build_worker_command:1034; run_process:1214; parse_provider_report:1412 |
| `skill/plan-and-execute/scripts/provider_self_test.py` | `a38f2da1c85a09e431c67333a2a29ed2cef8dc5bf27d5ac62d4fa0c82268e1dd` | sample_route:20; sample_report:29; test_default_provider_policy:46; test_worker_command_adapters:63 |

## Deeper analysis and competing approaches

### 1. Design analysis

Qwen has separate output, approval, sandbox, tool-call and wall-clock controls. Express those capabilities in fixtures for supported versions rather than inferring them from one flag. A diagnostics-only safe-mode disables settings, including sandbox customization; it is not an enforcement boundary for a read-only assistant.

### 2. Design analysis

Headless output may use a complete JSON result or streaming events. Preserve final result parsing and event diagnostics separately. Zero allowed tool calls does not remove tool schemas from the serialized input, so it neither proves a minimal prompt cost nor prevents an oversized initial request.

### 3. Design analysis

Native goals and unattended retries can create another execution loop beneath the runner. Keep orchestration-owned retry and completion authoritative; explicitly unset inherited unattended retry for managed workers unless a documented bounded integration permits it. A native budget abort is a budget outcome, not a semantic failure or successful completion.

### 4. Design analysis

Use independent wall, tool and output limits appropriate to the work, but do not confuse a hard elapsed-time cap with the existing semantic progress window. Permission denial should preserve evidence and pause. Never switch to yolo merely to obtain machine-readable output or avoid an interactive question.

The analysis above is a repository design synthesis. The linked publications establish capabilities or bounded empirical observations, not this skill's future measured performance. Exact account behavior and installed-version compatibility remain implementation-time checks.

| Alternative | Benefit | Cost / failure risk | Disposition |
|---|---|---|---|
| Reuse old CLI args forever | No new code | Flags and permission semantics drift | Reject |
| Use safe-mode as read-only | Easy-looking shortcut | Removes customization, not host privileges | Reject |
| Versioned headless fixtures and bounded loop ownership | Predictable automation | Requires explicit environment filtering | Recommended |
| Delegate orchestration to native goals | Fewer outer loops | Competing completion/retry controllers | Defer behind a separate contract |

## Ownership and scope boundary

This implementation owns its declared write scope and acceptance tests. Its following review checks the actual changed code; prepared research is not acceptance evidence.

Implementation may preserve an already-satisfied invariant with a regression test and a documented no-change rationale; do not add code solely to make every recommendation produce a diff.

## Implementation instructions

1. Add version/help fixtures for supported Qwen CLI releases and explicit format selection. Keep JSON-array output and streaming JSONL parsing separate.
2. Normalize terminal result, tool activity, budget exhaustion, quota and transport errors without treating any intermediate assistant message as completion.
3. Qualify read-only operation with supported tool exclusions and sandbox controls. Yolo/approval automation alone must not authorize a supposedly read-only observer.
4. Capture resumable session identifiers only if explicitly enabled and retention is documented. Otherwise keep fresh-worker behavior and artifact handoff.
5. Apply the shared bounded output spool and process-tree cancellation contract rather than maintaining a second unbounded capture implementation.
6. Do not treat Qwen safe-mode or max-tool-calls zero as a read-only or schema-free mode.
7. Bound or disable inherited unattended retries and native goal continuation under the managed runner.
8. Classify native wall/tool/turn budget exits separately from semantic, permission and environment failures.

## Acceptance and counterexamples

- Replay JSON and JSONL fixtures with interleaved tool messages, malformed records and missing terminal results.
- Budget/turn exhaustion is recorded separately from semantic failure and transient availability.
- A read-only fake/qualified command cannot select shell/write/edit tools outside the allowlist.
- Large output is drained without deadlock; cancellation stops owned descendants.
- Unsupported schema or sandbox flags fail closed with an actionable version reason.
- Safe-mode cannot silently disable the required sandbox and still pass preflight.
- An inherited indefinite-retry opt-in is removed or rejected under bounded runner policy.
- Budget exit 55 and turn-cap exit 53 are fixture-versioned, not generic semantic failures.
- Truncated streaming output cannot become a successful completion report.

## Cost, latency and quality decision

Count complete serialized input and all nested requests, not only outer invocations. Bound hidden retry latency before comparing Qwen with other candidate routes.

Compare total cost per independently validated outcome against the current implementation and a simpler qualified single-worker baseline. Count failed attempts, reviews, cache writes/reads, advisory calls and tool/runtime overhead in their native units. Unknown prices, quotas or usage remain unknown, not zero. Preserve capability and security floors; no automatic rollout follows from fixture replay alone.

## Evidence used in this revision

- [W-QWEN-HEADLESS] QwenLM, [Headless mode](https://qwenlm.github.io/qwen-code-docs/en/users/features/headless/). Accessed 2026-10-28. Reading scope: Official headless guide sections on flags, safe-mode, JSON and budgets inspected. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-QWEN-SETTINGS] QwenLM, [Qwen Code settings](https://github.com/QwenLM/qwen-code/blob/main/docs/users/configuration/settings.md). Accessed 2026-10-28. Reading scope: Official source documentation excerpts on wall-time, retry and environment controls inspected. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-SUBPROCESS] Python Software Foundation, [Subprocess management](https://docs.python.org/3/library/subprocess.html). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-RETRY-LAYERS] LiteLLM, [Router retries and SDK retries](https://docs.litellm.ai/docs/routing). Accessed 2026-10-28. Reading scope: Relevant retry/cooldown documentation excerpts inspected; no proxy deployment or authenticated test. Public source reading is not an independent code review or reproduction of vendor experiments.

Prior-round context: [E029], [E041], [E044]. See `SOURCE_REGISTER.md` for records; these were not all independently refreshed.

Search themes inspected in this round: Qwen headless safe-mode sandbox permission rules; Qwen unattended retry max wall time settings; Python subprocess unbounded output.

## Unverified limits and refresh triggers

- The installed Qwen release and its actual exit-code behavior were not exercised. Published budget codes must be pinned before becoming authoritative classifications.
- Flags and exit codes are based on the inspected current guide, not a locally executed version. Old releases need their own golden fixtures.

No authenticated provider invocation, live quota/cost benchmark, independent model review, or Windows runtime test was performed in this research revision.

Refresh only evidence contradicted by the installed CLI, selected account/billing plan or changed code contract. Unknown required capability blocks that candidate; it does not justify widening permissions.
