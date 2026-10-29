# 040 - Trae: research revision 2

Date: 2026-10-28. Feature: `F018`. Implementation TODO `040`; independent review TODO `041`. Product baseline: `0.11.0` / tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Prepared design evidence, not implemented code. Implementation and independent review remain pending.**

## Recommended direction

Preserve TRAE Agent as a distinct adapter with pinned CLI/tool contracts and owned trajectory artifacts; do not interpret the trajectory or IDE identity as a completion guarantee.

This is a conditional engineering recommendation for this repository, not a proof of a global optimum or a measured saving on the user's workload.

## Change from the previous report

The revision clarifies adapter identity, generated trajectory paths, container lifetime and diagnostic ownership, avoiding assumptions imported from the TRAE IDE.

The previous report is retained under `docs/plans/20261028-skill-optimization/history/research-round-1/prepared-research/` for audit. New W-prefixed sources below are the current-round evidence; old E-prefixed sources remain background.

## Questions and repository evidence

- Distinguish the configured Trae Agent CLI from the TRAE IDE or another CLI product.
- Verify trajectory handling, provider configuration, secret routing and failure reporting.

**Baseline observations:**
- The adapter invokes trae-cli run with a working directory and trajectory output path, plus optional underlying provider/model choices.
- The official Trae Agent repository describes an open-source agent and provider configuration. It does not justify borrowing flags or session behavior from the TRAE IDE.

All listed file hashes matched the preserved 0.11.0 source in this revision. This is integrity checking, not a second full code audit.

| Code anchor | SHA-256 | Selected symbols / location |
|---|---|---|
| `skill/plan-and-execute/scripts/run_isolated.py` | `00ffc3bce6093d63198b910eaad7e8a76f739dd226eb6399c2e6fa54301908df` | build_worker_command:1034; parse_provider_report:1412 |
| `skill/plan-and-execute/scripts/provider_self_test.py` | `a38f2da1c85a09e431c67333a2a29ed2cef8dc5bf27d5ac62d4fa0c82268e1dd` | sample_route:20; sample_report:29; test_default_provider_policy:46; test_worker_command_adapters:63 |

## Deeper analysis and competing approaches

### 1. Design analysis

The supported backend is the ByteDance TRAE Agent CLI, not every product carrying a similar name. Bind executable and version, configured model backend, tool set and working directory. A wrapper returning plausible prose is not proof that the expected agent or model performed the work.

### 2. Design analysis

Trajectories can include prompts, responses, tool commands and file contents. Allocate explicit per-attempt paths in the plan-owned diagnostics directory and apply redaction/retention controls before they become model context or exported evidence. Do not search arbitrary user trajectories to reconstruct context.

### 3. Design analysis

If a container is used, the runner must know whether it created it or attached to an existing one. Termination and cleanup of an attached container cannot be inferred from task failure. Use bounded child-process/container operations with ownership receipts, and preserve user-managed environments.

### 4. Design analysis

The final completion contract is the same independently validated report as other providers. Use the trajectory only to locate evidence for a failure. Native step budgets, execution errors and unavailable backend credentials should be classified without consuming capability retries.

The analysis above is a repository design synthesis. The linked publications establish capabilities or bounded empirical observations, not this skill's future measured performance. Exact account behavior and installed-version compatibility remain implementation-time checks.

| Alternative | Benefit | Cost / failure risk | Disposition |
|---|---|---|---|
| Treat all TRAE products identically | Less adapter metadata | Wrong CLI and tool assumptions | Reject |
| Read full trajectory on every retry | Rich history | Large tokens, secrets and anchoring | Reject |
| Versioned CLI plus owned bounded diagnostics | Traceable and portable | Requires artifact ownership | Recommended |
| Replace CLI with internal Python agent API | Direct control | Unstable internal coupling | Defer unless a supported public API pays off |

## Ownership and scope boundary

This implementation owns its declared write scope and acceptance tests. Its following review checks the actual changed code; prepared research is not acceptance evidence.

Implementation may preserve an already-satisfied invariant with a regression test and a documented no-change rationale; do not add code solely to make every recommendation produce a diff.

## Implementation instructions

1. Pin documented Trae Agent CLI/version fixtures and normalize its final output independently of provider-specific message formats.
2. Record both harness and actual model-provider identity so rate limits, capabilities and costs are attributed to the backend rather than the CLI name.
3. Register trajectory files under the task/job ownership and retention policy. Exclude them from packages and worker prompts unless a bounded sanitized excerpt is explicitly authorized.
4. Resolve secrets from allowed environment names at dispatch time; do not copy configuration values into manifests, evidence or model prompts.
5. Share cancellation and bounded process-output infrastructure with other adapters. Keep any Docker isolation choice explicit and version-qualified.
6. Pin TRAE Agent identity and version separately from IDE products and backend model configuration.
7. Allocate owned per-attempt trajectory paths; redact before export and never scan unrelated user sessions.
8. Distinguish runner-created containers from attached user containers before cancellation or cleanup.

## Acceptance and counterexamples

- Golden command fixtures distinguish Trae Agent from unrelated executables.
- An invalid or missing terminal output cannot be replaced by a plausible trajectory message.
- A seeded credential in a trajectory is not included in model-facing evidence or publication artifacts.
- Quota failures are keyed to the configured backend/profile, not every Trae execution.
- Cleanup preserves active trajectory evidence and removes only registered stale artifacts.
- A stale trajectory from another attempt cannot satisfy completion.
- Cleanup refuses to destroy an attached user-owned container.
- Credential-like text in trajectory snippets is redacted before truncation.
- Missing backend configuration fails preflight without a semantic escalation.

## Cost, latency and quality decision

Retain compact failure references instead of feeding full trajectories; benchmark API integration only against measured CLI startup and maintenance costs.

Compare total cost per independently validated outcome against the current implementation and a simpler qualified single-worker baseline. Count failed attempts, reviews, cache writes/reads, advisory calls and tool/runtime overhead in their native units. Unknown prices, quotas or usage remain unknown, not zero. Preserve capability and security floors; no automatic rollout follows from fixture replay alone.

## Evidence used in this revision

- [W-TRAE-README] ByteDance, [TRAE Agent README](https://github.com/bytedance/trae-agent). Accessed 2026-10-28. Reading scope: Official repository README examples and architecture description inspected. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-TRAE-TRAJECTORY] ByteDance, [Trajectory recording](https://github.com/bytedance/trae-agent/blob/main/docs/TRAJECTORY_RECORDING.md). Accessed 2026-10-28. Reading scope: Trajectory guide sections and examples inspected; not a full repository audit. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-LOGGING] OWASP, [Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-SUBPROCESS] Python Software Foundation, [Subprocess management](https://docs.python.org/3/library/subprocess.html). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

Prior-round context: [E032], [E044], [E042]. See `SOURCE_REGISTER.md` for records; these were not all independently refreshed.

Search themes inspected in this round: bytedance trae-agent README CLI trajectory; TRAE Agent trajectory recording agent steps tools; OWASP sensitive logs retention.

## Unverified limits and refresh triggers

- Underlying provider behavior, Docker confinement and installed Trae CLI version were not executed here.
- No TRAE CLI or container execution was tested. The public documentation and baseline adapter define the intended compatibility tests.

No authenticated provider invocation, live quota/cost benchmark, independent model review, or Windows runtime test was performed in this research revision.

Refresh only evidence contradicted by the installed CLI, selected account/billing plan or changed code contract. Unknown required capability blocks that candidate; it does not justify widening permissions.
