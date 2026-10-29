# 038 - Kimi: research revision 2

Date: 2026-10-28. Feature: `F017`. Implementation TODO `038`; independent review TODO `039`. Product baseline: `0.11.0` / tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Prepared design evidence, not implemented code. Implementation and independent review remain pending.**

## Recommended direction

Make Kimi prompt-mode permission behavior an explicit versioned compatibility decision; reject unsupported safe-role invocations instead of silently deleting flags.

This is a conditional engineering recommendation for this repository, not a proof of a global optimum or a measured saving on the user's workload.

## Change from the previous report

The current official reference changes the meaning and permitted combinations of yolo/auto/plan with prompt. A mechanical removal of a rejected flag could accidentally broaden execution permissions.

The previous report is retained under `docs/plans/20261028-skill-optimization/history/research-round-1/prepared-research/` for audit. New W-prefixed sources below are the current-round evidence; old E-prefixed sources remain background.

## Questions and repository evidence

- Verify print mode, sessions, automatic context compaction and schema/report extraction.
- Check accounting, interruption and permission boundaries against pinned upstream code.

**Baseline observations:**
- The existing Kimi worker appends a configured permission flag and --prompt. The current official command reference says --prompt cannot be combined with --yolo, --auto or --plan.
- The legacy reference instead documents --print and its own non-interactive semantics. This is a documentation/source incompatibility risk, not a reproduced failure of an installed CLI in this environment.

All listed file hashes matched the preserved 0.11.0 source in this revision. This is integrity checking, not a second full code audit.

| Code anchor | SHA-256 | Selected symbols / location |
|---|---|---|
| `skill/plan-and-execute/scripts/run_isolated.py` | `00ffc3bce6093d63198b910eaad7e8a76f739dd226eb6399c2e6fa54301908df` | build_worker_command:1034; parse_provider_report:1412 |
| `skill/plan-and-execute/scripts/provider_self_test.py` | `a38f2da1c85a09e431c67333a2a29ed2cef8dc5bf27d5ac62d4fa0c82268e1dd` | sample_route:20; sample_report:29; test_default_provider_policy:46; test_worker_command_adapters:63 |

## Deeper analysis and competing approaches

### 1. Design analysis

The existing adapter should not treat yolo as a timeless synonym for auto-approval across versions. The inspected guide makes prompt mode incompatible with yolo, auto and plan flags and gives it an automatic permission mode. Probe or pin the contract; do not blindly retry a failed invocation with those flags removed.

### 2. Design analysis

For implementation workers, automatic permission may be allowed only inside the user-authorized filesystem/process boundary. For review and monitoring, a prompt-mode planner preference is not a proven read-only boundary. Reject the optional role when the installed Kimi configuration cannot enforce its restrictions.

### 3. Design analysis

Session reuse must bind a known session id to repository, task and provider. Resuming a latest session can import unrelated state, saved permissions or model selection. Keep fresh workers as the default and document persistence/cleanup implications separately from accepted model output.

### 4. Design analysis

Structured final report validation and runner-owned tests remain mandatory even if the native CLI exits successfully. Capture partial output and stderr without treating them as instructions or leaking credentials. Compatibility errors belong in a bounded preflight or environment path, not in a costly model escalation loop.

The analysis above is a repository design synthesis. The linked publications establish capabilities or bounded empirical observations, not this skill's future measured performance. Exact account behavior and installed-version compatibility remain implementation-time checks.

| Alternative | Benefit | Cost / failure risk | Disposition |
|---|---|---|---|
| Drop incompatible flags on failure | Restores invocation | May widen permissions silently | Reject |
| Pin one known Kimi version indefinitely | Predictable argv | Maintenance and stale support | Temporary supported fixture |
| Versioned permissions/output/session contract | Safe compatible execution | Needs explicit fail-closed cases | Recommended |
| Use plan prompt as enforcement | Cheap apparent restriction | Only behavioral preference | Reject for observer security |

## Ownership and scope boundary

This implementation owns its declared write scope and acceptance tests. Its following review checks the actual changed code; prepared research is not acceptance evidence.

Implementation may preserve an already-satisfied invariant with a regression test and a documented no-change rationale; do not add code solely to make every recommendation produce a diff.

## Implementation instructions

1. Introduce bounded version/help discovery and explicit supported protocol variants. Never combine flags from the old and new references.
2. For a current variant, construct the documented non-interactive invocation and handle its permission boundary explicitly; for a legacy variant, retain only the tested compatible syntax.
3. Normalize stream-json messages into terminal outcome, bounded report and usage. Intermediate text, context-compaction events and tool output are not a completion artifact.
4. Treat session reuse as opt-in with documented storage/retention; default cross-provider continuation remains an evidence capsule and the worktree.
5. Add a diagnostic that identifies unknown versions without silently switching to unrestricted operation. Preserve user configuration and never run an automatic upgrade.
6. Version Kimi prompt and permission combinations; never repair an invocation by silently broadening permissions.
7. Bind any explicit resume to the exact task and repository, including saved permission state.
8. Disable advisory roles when a genuine read-only boundary cannot be established.

## Acceptance and counterexamples

- Current fixtures reject --prompt combined with obsolete or mutually exclusive permission flags.
- Legacy fixtures keep their documented print-mode syntax instead of receiving current-only flags.
- A missing terminal report, malformed JSONL or interrupted stream cannot pass acceptance.
- Budget, transient and permanent errors are normalized only when the version contract establishes their meaning.
- Session identifiers and logs never introduce secrets into a shared handoff.
- Prompt plus obsolete permission flags yields a compatibility failure before model work.
- Fallback flag removal cannot change the authorized permission profile.
- Resume cannot inherit another task saved permissions.
- Native exit zero with missing completion schema is rejected.

## Cost, latency and quality decision

Fail fast on incompatible arguments rather than spending retries or escalating the model. Session reuse is an experiment with privacy/reconstruction costs, not the default optimization.

Compare total cost per independently validated outcome against the current implementation and a simpler qualified single-worker baseline. Count failed attempts, reviews, cache writes/reads, advisory calls and tool/runtime overhead in their native units. Unknown prices, quotas or usage remain unknown, not zero. Preserve capability and security floors; no automatic rollout follows from fixture replay alone.

## Evidence used in this revision

- [W-KIMI-CLI] Moonshot AI, [Kimi command reference](https://www.kimi.com/code/docs/en/kimi-code-cli/reference/kimi-command). Accessed 2026-10-28. Reading scope: Official command reference sections on prompt, permissions, session and output inspected; no local Kimi executable tested. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-INJECTION] OWASP, [LLM Prompt Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-SUBPROCESS] Python Software Foundation, [Subprocess management](https://docs.python.org/3/library/subprocess.html). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-REPLAY] LangChain, [Graph API: re-execution and idempotency](https://docs.langchain.com/oss/python/langgraph/graph-api). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

Prior-round context: [E030], [E031], [E041]. See `SOURCE_REGISTER.md` for records; these were not all independently refreshed.

Search themes inspected in this round: site.kimi.com/code/docs prompt yolo auto plan; Kimi command headless session output format; least privilege untrusted tool outputs.

## Unverified limits and refresh triggers

- No installed Kimi executable was run, so actual compatibility must be confirmed with its version/help and one bounded authorized test.
- No Kimi executable or authenticated run was performed. The observed documentation describes current behavior and must be reconciled with the installed version.

No authenticated provider invocation, live quota/cost benchmark, independent model review, or Windows runtime test was performed in this research revision.

Refresh only evidence contradicted by the installed CLI, selected account/billing plan or changed code contract. Unknown required capability blocks that candidate; it does not justify widening permissions.
