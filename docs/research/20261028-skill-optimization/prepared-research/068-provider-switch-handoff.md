# 068 - Provider Switch Handoff: research revision 2

Date: 2026-10-28. Feature: `F032`. Implementation TODO `068`; independent review TODO `069`. Product baseline: `0.11.0` / tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Prepared design evidence, not implemented code. Implementation and independent review remain pending.**

## Recommended direction

Specify opt-in provider-top switching over distinct effective dispatches, with coherent chain ownership, per-provider/phase evidence and deterministic evidence-bounded handoff by default.

This is a conditional engineering recommendation for this repository, not a proof of a global optimum or a measured saving on the user's workload.

## Change from the previous report

The revision formalizes entry rung, no-op detection, attempt reservation, uncertain outcomes and the cost/anchoring alternative matrix. It retains the twelve required acceptance scenarios and does not add an extra summarizer call by default.

The previous report is retained under `docs/plans/20261028-skill-optimization/history/research-round-1/prepared-research/` for audit. New W-prefixed sources below are the current-round evidence; old E-prefixed sources remain background.

## Questions and repository evidence

- Compare worker field, native session resume, extra read-only summary and deterministic capsule (source section 4).
- Decide opt-in chain, entry rung, no-op identity, retry budget, phase state and handoff validation from evidence.

**Baseline observations:**
- The verified baseline has different chain selection in choose_route and availability.select, repeated effective tops and early last-provider exhaustion. The original ten-case fixture replay is preserved as historical baseline evidence.
- Workers are fresh/ephemeral in the normal paths. Starting a new process of the prior provider cannot recover its vanished conversation without deliberately changing persistence policy.
- The concise prompt omits plan_dir in failure_context and excludes prior reports by default. A permitted evidence capsule therefore needs a small explicit isolation-rule amendment, not a hidden transcript injection.

All listed file hashes matched the preserved 0.11.0 source in this revision. This is integrity checking, not a second full code audit.

| Code anchor | SHA-256 | Selected symbols / location |
|---|---|---|
| `skill/plan-and-execute/scripts/run_isolated.py` | `00ffc3bce6093d63198b910eaad7e8a76f739dd226eb6399c2e6fa54301908df` | choose_route:301; failure_context:776; design_route_task:924; ladder_exhausted:2152 |
| `skill/plan-and-execute/scripts/availability.py` | `39e4e02663a26a1a3d6324037fef96bbf7d5c28cc2511a89d0431b377fa97c0d` | select:116 |
| `skill/plan-and-execute/scripts/routingctl.py` | `f792363c783596aef972925edb9aad5d97b86da43e45a212a69c5a2355a78616` | lift_tier:214; route_rungs:230 |
| `skill/plan-and-execute/scripts/runner_contract.py` | `74db8be9153d63c8accc1e3a650279fd54da0ea0b6405b0bfb4e470f183a97c6` | worker_prompt:44 |
| `skill/plan-and-execute/scripts/assistant_triage.py` | `af9d5a1054aae9c747916a60f3f0c836209f878c1c31638909eedcd28d9109c2` | Skip:33; dumps:37; strict_json:41; redact:53 |
| `skill/plan-and-execute/references/TOKEN_EFFICIENCY.md` | `72da10bd5e05fd08d213ed29ca649e83fbe23d4f082bf1c3159e87402cbef8cd` | # Token-efficiency contract:1; ## Objective:5; ## 1. Avoid the harness when the harness does not pay for itself:9; ## 2. Keep useful shared context while it is useful:15 |

## Deeper analysis and competing approaches

### 1. Design analysis

Use a disabled-by-default provider_switch section with strict subkeys and explicit modes. In the new mode, choose one allowed chain from the declared task policy and retain it through ladder selection and availability. Every effective dispatch binds the selected provider, resolved model/effort/profile and phase. A new provider starts from the task capability floor lifted to its available equivalent, not from the accumulated failures of another provider.

### 2. Design analysis

Advance after classified evidence exhausts distinct useful rungs, including aliases or embedded-effort variants that produce no new dispatch. Permit at most the documented same-rung mechanical/budget repeat; never use environmental, permission, plan-defect or hard-limit failures as capability evidence. Reserve remaining attempt budget for still-eligible providers or reject/warn on an impossible budget before execution; record every skip reason.

### 3. Design analysis

Treat availability substitution and capability switching as different events. Quota can pause or select another eligible pool without adding functional failure. If a worker may already have produced side effects, reconcile its terminal/ownership state before replacement. Design and implementation need separate provider histories while retaining an explicit shared task budget and a reset contract that clears only the intended epoch.

### 4. Design analysis

The cheapest safe handoff is deterministic evidence: current diff references, completed subtask ids, failure class, sanitized error fingerprint and current validation packet. Put one bounded capsule after the static prefix, label hypotheses unverified and expire it after the next attempt. An optional worker-authored hypothesis field can be evaluated later; resuming an old session or adding a summary model has persistence, billing and anchoring costs. Independent tests, not the summary, decide success.

The analysis above is a repository design synthesis. The linked publications establish capabilities or bounded empirical observations, not this skill's future measured performance. Exact account behavior and installed-version compatibility remain implementation-time checks.

| Alternative | Benefit | Cost / failure risk | Disposition |
|---|---|---|---|
| Continue repeating the top until a fixed failure count | Legacy compatibility | Wasted identical attempts and unreachable providers | Retain only when new mode is disabled |
| Switch immediately to next provider maximum | Simple diversity | Unnecessary cost and ignores equivalent entry floor | Reject as default |
| Effective-top switching plus deterministic capsule | Bounded cost and recoverable evidence | Requires per-provider state and coherent chain | Recommended opt-in |
| Worker-authored nullable hypotheses plus deterministic fallback | Little incremental output cost | May anchor next worker and require schema changes | Optional measured follow-up, not required default |
| Resume previous session or call extra summarizer | Can recover richer context | Persistence, privacy, calls and false certainty | Defer unless measured improvement pays |

## Ownership and scope boundary

TODO 068 encodes the decision below as twelve-case fixtures and compatibility expectations only. Runtime/config/state/prompt changes are owned by 070, 072, 074, 076, 078 and 080, each with its following independent review.

Implementation may preserve an already-satisfied invariant with a regression test and a documented no-change rationale; do not add code solely to make every recommendation produce a diff.

## Implementation instructions

1. Encode the twelve original acceptance cases as reusable fake-provider fixtures with explicit legacy and opt-in expected behavior.
2. Include alias/no-op rungs, unavailable destinations, fixed provider, missing tiers, snapshot resolution and separate design/implementation evidence.
3. Add deterministic fixtures for next-attempt capsule expiry, secret redaction, receipt identity and a remaining-attempt budget too small for all providers.
4. Map each runtime expectation to its implementing owner in 070-080; do not modify the runner or mark future behavior implemented here.

### Runtime design consumed by owners 070-080

1. Keep provider_switch.mode=legacy by default; expose an explicit effective_top mode with strict subkey validation and routing-fingerprint coverage. Version1 full config snapshots must not inherit a new global policy.
2. Freeze the allowed chain for a task phase from the declared policy and override rules. Resolve each candidate through tier lifting, profile/native effort and snapshot before building distinct dispatches. The selected provider is authoritative for both ladder and command.
3. Persist phase/provider-local evidence and an actual-dispatch receipt before recording outcomes. Keep global functional failures/max_attempts separate. No eligible provider is exhausted until it was attempted or excluded with a reason.
4. On semantic or unknown top failure, move to the next qualified provider. Permit at most one documented identical retry for mechanical/budget cases. Environmental, plan_defect and timeout_ceiling never cause capability switching.
5. Reserve enough remaining attempts for at least one dispatch of each remaining eligible provider when the configured budget can do so; otherwise emit a preflight budget warning and explicit budget_exhausted outcome. Never silently increase the user budget.
6. Build a deterministic capsule from pinned subtask state, changed-path summary and validation/evidence references. Sanitize before truncation, mark hypotheses unverified, append after static rules and deterministic evidence, bind it to the next dispatch only.
7. Keep the optional previous-worker summary field as a later measured enhancement behind its own flag. Do not add a paid summary call or native transcript retention by default. Tasks070-081 implement and review the detailed contract.
8. Keep TODO068 fixture-only; TODOs070-080 own config, state, selection, handoff and integration changes.
9. Reserve or preflight the remaining provider-attempt budget and record skips, entry-rung choice and reset epoch explicitly.
10. Use one next-attempt-only deterministic capsule after stable rules; do not let it change route, failure class or task status.

## Acceptance and counterexamples

- All twelve provider-switch acceptance cases have explicit inputs and expected outputs.
- Fixtures distinguish provider/phase identity, unavailable candidates, duplicate dispatches and bounded attempt reservation.
- Legacy replay remains separate from expected opt-in behavior; no runtime implementation is claimed by this fixture task.

## Cost, latency and quality decision

For deterministic handoff, extra model-call cost is zero; prompt-token cost and validation overhead still count. Compare against no handoff and worker-authored summaries under paired quality gates before expanding context.

Compare total cost per independently validated outcome against the current implementation and a simpler qualified single-worker baseline. Count failed attempts, reviews, cache writes/reads, advisory calls and tool/runtime overhead in their native units. Unknown prices, quotas or usage remain unknown, not zero. Preserve capability and security floors; no automatic rollout follows from fixture replay alone.

## Evidence used in this revision

- [W-AUTOMIX] Aggarwal et al. / NeurIPS, [AutoMix: Automatically Mixing Language Models](https://arxiv.org/abs/2310.12963). Accessed 2026-10-28. Reading scope: Abstract and author implementation overview inspected; no full-paper experiment reproduction. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-ROUTELLM] Ong et al. / ICLR, [RouteLLM: Learning to Route LLMs with Preference Data](https://arxiv.org/abs/2406.18665). Accessed 2026-10-28. Reading scope: Research abstract and version metadata inspected; benchmark percentages are not transferred to this codebase. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-RETRY] Amazon Builders Library, [Timeouts, retries, and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-REFLEXION] Shinn et al., [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366). Accessed 2026-10-28. Reading scope: Original paper abstract inspected; no claim of reproduction or full-paper reading. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-SELFCORRECT] Huang et al. / ICLR, [Large Language Models Cannot Self-Correct Reasoning Yet](https://proceedings.iclr.cc/paper_files/paper/2024/hash/8b4add8b0aa8749d80a34ca5d941c355-Abstract-Conference.html). Accessed 2026-10-28. Reading scope: Conference abstract inspected; historical models/tasks, no full reproduction. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-OPENAI-CACHE] OpenAI, [Prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-AGY-EFFORT] Google, [Effort command](https://antigravity.google/docs/cli/commands/effort). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-INJECTION] OWASP, [LLM Prompt Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

Prior-round context: [E014], [E012], [E038], [E039], [E054], [E010], [E044], [E018], [E021]. See `SOURCE_REGISTER.md` for records; these were not all independently refreshed.

Search themes inspected in this round: AutoMix limitations model switching verification; RouteLLM learned routing distribution; Reflexion external feedback memory; LLM self correction external feedback; provider cache boundary effective effort.

## Unverified limits and refresh triggers

- Equivalent logical tiers do not prove equal quality across providers. No live model superiority, quota independence, token saving or independent maximum-model review is claimed.
- No cross-provider session, paid handoff or live capability comparison was executed. Effective intelligence is not proven by matching model-family names; the strongest admissible route must be observed, not invented.

No authenticated provider invocation, live quota/cost benchmark, independent model review, or Windows runtime test was performed in this research revision.

Refresh only evidence contradicted by the installed CLI, selected account/billing plan or changed code contract. Unknown required capability blocks that candidate; it does not justify widening permissions.

## Capability identity versus availability identity

Keep capability identity separate from availability identity: changing only a quota pool, request ID, log path or credential reference cannot create a stronger rung. Resolve known aliases and native effort before deduplication; retain the harness/backend boundary rather than equating model-family names across hosts.

This is an engineering contract for the proposed implementation, not a claim that quota-pool isolation or cross-harness intelligence equivalence was measured.

## Normative implementation blueprint for TODOs 070-080

The following is the selected repository policy, not a vendor requirement or a measured optimum. TODO 068 only encodes it in fixtures.

### Configuration and compatibility

```json
{
  "provider_switch": {
    "mode": "legacy",
    "handoff": "deterministic",
    "handoff_max_bytes": 4000,
    "repeat_mechanical_once": true,
    "repeat_budget_once": true
  }
}
```

Accept only `legacy` or `effective_top`, and `none` or `deterministic` for handoff. Reject unknown subkeys and non-boolean repeat flags. The initial byte bound is an integer from 512 through 16000, default 4000; this is a tunable prompt budget, not a claim about exact tokens. All behavior is inactive in `legacy`. Full version-1 config snapshots retain their historical non-inheritance rule. A task with fallback disabled never widens its provider chain. An explicit provider override stays first under the existing allowed-fallback semantics.

### Candidate and evidence invariants

Freeze one permitted provider chain per task phase and effective configuration generation. Resolve aliases, tier lifting, snapshots, profile/backend and effective effort before constructing useful rungs. Collapse all known-equivalent dispatches while preserving the first occurrence; omit request nonce, temporary paths and quota-only differences from capability comparison. Availability keys still retain provider, account/profile reference, quota pool and model. Never serialize credentials or replace an unknown required capability with an invented equivalence.

A new provider enters at the declared task capability floor, lifted upward to an available supported tier and compatible effort. Previous providers' failures cannot advance its ladder. Persist actual dispatch identity before processing its outcome. Design and implementation have separate provider/rung histories; their functional failures still consume the existing shared task budget. An explicit reset starts a new evidence epoch while retaining audit history and does not clear unrelated quota cooldowns.

### Transition and budget algorithm

1. Apply availability and ownership checks without adding functional failures. Reconcile an uncertain prior process/side effect before a replacement worker is dispatched.
2. A semantic or unknown functional failure advances to the next distinct useful rung; after the effective top, advance to the next eligible provider. Permit at most one same-rung retry for each mechanical/budget episode only when its explicit repeat flag is enabled. An episode is the same provider, phase, effective rung and failure fingerprint; absent a trustworthy fingerprint, allow only one such repeat at that rung in the evidence epoch.
3. Environmental, permission, plan-defect and hard-time-limit outcomes do not cause capability escalation. Respect their existing repair, pause or blocked-for-review handling.
4. Let `R = max_attempts - functional_failures` and `U` be the number of still-eligible, untried remaining providers for this phase. Before spending another failure-capable attempt on an already-tried provider, reserve `U` attempts: if `R <= U`, move to the next untried provider and record `attempt_budget_reservation`, not `ladder_top`. Availability checks/cooldowns are not failed functional attempts.
5. If the configured budget cannot afford the first attempt on all eligible providers, issue a deterministic preflight warning with counts and continue only within that unchanged budget; finish with `budget_exhausted` when it reaches zero. Never silently increase `max_attempts`. Do not promise both complete ladders and universal provider coverage under an insufficient budget.
6. `ladder_exhausted` requires every eligible provider to have actually exhausted its distinct useful rungs, or to have an explicit policy exclusion reason. A reservation skip is not evidence of exhausted capability. Missing executables, quota and cooldowns remain availability outcomes; none is fabricated as a model failure.

A failed design phase can consume the shared budget before implementation begins; expose that fact in preflight/receipts. Do not guarantee all providers in both phases under one insufficient budget. Pin routing-policy/catalog fingerprints; a material changed contract invalidates cached intent through an auditable state transition, not a silent reuse of prior failures.

### Handoff, uncertainty and cost

Default to a deterministic capsule no larger than 4000 serialized UTF-8 bytes. Keep verified paths/subtask IDs, evidence references, hashes and classifications; omit free-form raw output unless it has been sanitized before truncation. Redaction is defense in depth, not a proof that arbitrary text contains no unknown secret. If bounded evidence cannot be safely established, emit a smaller reference-only capsule.

Bind it to the source-state digest, phase, destination and next actual dispatch. A pre-spawn availability rejection does not pretend it was delivered; rebuild or drop it for the eventual destination. Consume it after one actual dispatch and never replay an old capsule into later attempts. Put it after stable rules and deterministic failure evidence in both prompt implementations. Unverified hypotheses cannot mutate routing, failure class or task status.

Telemetry records the switch reason, actual de/para identity, handoff byte count and observed usage/cost when supplied. Deterministic construction has zero extra model calls, not zero CPU, prompt tokens or dollar cost. Extra summarization and native session retention are deferred opt-in experiments, not required default behavior.

### Ownership

- 070: strict configuration, migration and selector fingerprint.
- 072: effective rung primitives integration, durable provider/phase state and reset epoch.
- 074: one-chain selection, availability separation and attempt reservation.
- 076: deterministic sanitized capsule and evidence validation.
- 078: both prompt compositions, one-dispatch expiry and switch telemetry.
- 080: twelve-case replay, documentation and economic interpretation.

Each following odd-numbered task independently reviews and corrects the actual implementation. All twelve original acceptance cases remain authoritative.
