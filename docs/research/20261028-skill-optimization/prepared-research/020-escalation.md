# 020 - Escalation: research revision 2

Date: 2026-10-28. Feature: `F008`. Implementation TODO `020`; independent review TODO `021`. Product baseline: `0.11.0` / tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Prepared design evidence, not implemented code. Implementation and independent review remain pending.**

## Recommended direction

Define a pure effective-dispatch ladder that removes no-op rungs, retains failure-specific retry semantics and leaves provider switching to its dedicated integration tasks.

This is a conditional engineering recommendation for this repository, not a proof of a global optimum or a measured saving on the user's workload.

## Change from the previous report

The new research strengthens the distinction between logical tier and actual dispatch. It adds alias/backend identity, duplicate rungs with different nominal labels, and a counterfactual test for the claimed benefit of escalation.

The previous report is retained under `docs/plans/20261028-skill-optimization/history/research-round-1/prepared-research/` for audit. New W-prefixed sources below are the current-round evidence; old E-prefixed sources remain background.

## Questions and repository evidence

- Reproduce source section 2.8 and distinguish useful effective rungs from repeated dispatches.
- Compare per-provider evidence with cumulative failure counts and reset semantics.

**Baseline observations:**
- choose_route derives a provider slot from total functional failures, whereas availability.select rebuilds a chain for the escalated tier. This can mismatch the ladder and dispatched provider.
- The current exhaustion decision uses accumulated failure classes against a later provider's ladder, allowing that provider to be considered exhausted before its first attempt.
- A logical tier/effort increase can resolve to the same model and native effort, especially with embedded effort slugs and equal strong/max models.

All listed file hashes matched the preserved 0.11.0 source in this revision. This is integrity checking, not a second full code audit.

| Code anchor | SHA-256 | Selected symbols / location |
|---|---|---|
| `skill/plan-and-execute/scripts/routingctl.py` | `f792363c783596aef972925edb9aad5d97b86da43e45a212a69c5a2355a78616` | lift_tier:214; route_rungs:230; escalation_step:245 |
| `skill/plan-and-execute/scripts/run_isolated.py` | `00ffc3bce6093d63198b910eaad7e8a76f739dd226eb6399c2e6fa54301908df` | choose_route:301; ladder_exhausted:2152 |
| `skill/plan-and-execute/scripts/planctl.py` | `c3cdf3064fa18b7271ea801c614e18b45a467b4c923b98fdb8fbd16ab00bffd4` | PlanError:85; review_checks_for_schema:89; now_utc:102; slugify:106 |
| `skill/plan-and-execute/references/MODEL_ROUTING.md` | `886f53a8817d4a7eb9e93a24e715a57cce927ee1b673384e60cfe46c0814c7c9` | # Model and provider routing:1; ## Objective:12; ## 1. Classify the leaf, then look up the floor:16; ### Candidate selector (opt-in, pure):35 |

## Deeper analysis and competing approaches

### 1. Design analysis

The baseline applies one global failure sequence to a provider-specific ladder, then availability may dispatch elsewhere. A cost-efficient fix starts with a pure representation of the actual candidate: harness, backend endpoint identity, resolved model, effective effort and relevant execution options. A logical tier change that leaves this representation unchanged is not additional capability.

### 2. Design analysis

Deduplicate all known-equivalent candidates, preserving their first occurrence, after all overrides, snapshots and embedded-effort rules are applied. Do not use a hardcoded provider ranking. Some role aliases map to the same backend, while an accepted effort flag can be ignored by a compatible endpoint. Record requested and resolved values separately; an unknown resolution is an explicit capability gap, not a license to guess.

### 3. Design analysis

Retain one bounded same-rung retry for a reproducible mechanical or budget failure only when the declared policy allows it. Semantic failure advances to the next distinct credible capability. Environmental, permission, plan-defect and fixed-time-limit failures do not establish a stronger model will help. Counter state belongs to provider and phase, not an aggregate inherited by a provider that has never run.

### 4. Design analysis

Learned routers and self-verification cascades solve a related but different problem from stateful retry routing. Keep their learned score out of the acceptance path. First test deterministic invariants and dispatch uniqueness on the existing fixtures; evaluate learned selection in shadow mode only after there is representative labeled evidence.

The analysis above is a repository design synthesis. The linked publications establish capabilities or bounded empirical observations, not this skill's future measured performance. Exact account behavior and installed-version compatibility remain implementation-time checks.

| Alternative | Benefit | Cost / failure risk | Disposition |
|---|---|---|---|
| Escalate by total retry count | Small implementation | Repeats aliases and pollutes new-provider evidence | Keep only as legacy-disabled comparator |
| Always jump to the strongest model | May resolve hard failures | Expensive and still cannot repair environmental faults | Reject as universal policy |
| Effective candidate ladder plus classified evidence | Eliminates no-op capability attempts | Requires resolved candidate identity | Recommended |
| Learned router controls retries | Potential workload adaptation | Distribution drift and opaque state changes | Shadow experiment only |

## Ownership and scope boundary

TODO 020 implements pure ladder primitives and fixtures only. Persisted phase/provider counters and reset semantics belong to 072; actual dispatch, quota handling and attempt reservation belong to 074.

Implementation may preserve an already-satisfied invariant with a regression test and a documented no-change rationale; do not add code solely to make every recommendation produce a diff.

## Implementation instructions

1. Define a pure effective-dispatch identity after tier lifting, snapshot/profile resolution, effective effort and backend aliases, with no secrets.
2. Build useful ordered rungs by removing equivalent actual dispatches while preserving the requested capability floor.
3. Test pure classified transitions with provider/phase-local fixture evidence; do not persist new state or change runner dispatch in this task.
4. Retain the original legacy replay fixtures and disabled-mode argv assertions without weakening them.
5. Expose the primitives for 072 and 074; those tasks own durable counters, reset, availability integration and attempt reservation.
6. Build pure effective candidate identities after aliases, snapshots and native effort resolution; deduplicate equivalent rungs.
7. Test classified failure transitions per provider and phase without changing legacy-disabled behavior.
8. Keep full provider switching in TODOs 070-080; expose reusable ladder primitives and counterfactual dispatch fixtures here.

## Acceptance and counterexamples

- Pure ladder fixtures deduplicate resolved model/native-effort identities while preserving capability floors.
- Pure transitions distinguish provider-local functional evidence from quota and environmental outcomes.
- Legacy-disabled argv and routing fixtures remain unchanged; runtime integration is deferred to 072-074.
- Different tier labels resolving to the same model and effective effort produce one capability rung.
- An ignored effort argument does not count as increased capability.
- A quota or environment failure does not advance the functional ladder.
- The default disabled option preserves existing argv and routing fixtures.

## Cost, latency and quality decision

Measure distinct useful attempts, repeated-top attempts and validated outcomes; expected benefit is avoided identical failed dispatches, not a claimed percentage of model-quality improvement.

Compare total cost per independently validated outcome against the current implementation and a simpler qualified single-worker baseline. Count failed attempts, reviews, cache writes/reads, advisory calls and tool/runtime overhead in their native units. Unknown prices, quotas or usage remain unknown, not zero. Preserve capability and security floors; no automatic rollout follows from fixture replay alone.

## Evidence used in this revision

- [W-AUTOMIX] Aggarwal et al. / NeurIPS, [AutoMix: Automatically Mixing Language Models](https://arxiv.org/abs/2310.12963). Accessed 2026-10-28. Reading scope: Abstract and author implementation overview inspected; no full-paper experiment reproduction. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-ROUTELLM] Ong et al. / ICLR, [RouteLLM: Learning to Route LLMs with Preference Data](https://arxiv.org/abs/2406.18665). Accessed 2026-10-28. Reading scope: Research abstract and version metadata inspected; benchmark percentages are not transferred to this codebase. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-RETRY] Amazon Builders Library, [Timeouts, retries, and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-AGY-EFFORT] Google, [Effort command](https://antigravity.google/docs/cli/commands/effort). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-GLM] Z.ai, [Claude Code integration](https://docs.z.ai/devpack/tool/claude). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

Prior-round context: [E012], [E013], [E014], [E040]. See `SOURCE_REGISTER.md` for records; these were not all independently refreshed.

Search themes inspected in this round: AutoMix limitations self verification model routing; RouteLLM query distribution preference data; Antigravity effort model variant xhigh max; Z.ai Claude model alias mapping.

## Unverified limits and refresh triggers

- Quality equivalence across providers is not established by matching tier labels. Real-run calibration remains an authorized evaluation step.
- Public ranking and accepted CLI flags cannot establish equivalent intelligence across harnesses. Live backend identity may require a permitted response field or account-side verification.

No authenticated provider invocation, live quota/cost benchmark, independent model review, or Windows runtime test was performed in this research revision.

Refresh only evidence contradicted by the installed CLI, selected account/billing plan or changed code contract. Unknown required capability blocks that candidate; it does not justify widening permissions.

## Capability identity versus availability identity

Keep capability identity separate from availability identity: changing only a quota pool, request ID, log path or credential reference cannot create a stronger rung. Resolve known aliases and native effort before deduplication; retain the harness/backend boundary rather than equating model-family names across hosts.

This is an engineering contract for the proposed implementation, not a claim that quota-pool isolation or cross-harness intelligence equivalence was measured.

Additional counterexamples: non-adjacent duplicate aliases, changed request nonces and changed log paths must not create an additional capability rung. Runtime ownership remains in 072-074.
