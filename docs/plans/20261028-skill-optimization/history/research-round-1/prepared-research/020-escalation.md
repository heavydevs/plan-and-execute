# F008 / task 020 - Capability floors, evidence ladders and retry accounting

Date: 2026-10-28. Product baseline: 0.11.0, tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Research prepared; implementation pending; independent review pending.** This report is an implementation input, not a completion receipt. No external reviewer is impersonated.

## Decision and scope

**Recommendation (engineering inference):** Introduce a pure effective-dispatch ladder model with provider-local evidence; keep the legacy path unchanged until the opt-in switch policy is integrated.

## Questions addressed

- Reproduce source section 2.8 and distinguish useful effective rungs from repeated dispatches.
- Compare per-provider evidence with cumulative failure counts and reset semantics.

## Repository evidence

The following are static-code observations against the pinned baseline, not results from authenticated providers:

- choose_route derives a provider slot from total functional failures, whereas availability.select rebuilds a chain for the escalated tier. This can mismatch the ladder and dispatched provider.
- The current exhaustion decision uses accumulated failure classes against a later provider's ladder, allowing that provider to be considered exhausted before its first attempt.
- A logical tier/effort increase can resolve to the same model and native effort, especially with embedded effort slugs and equal strong/max models.

### Read targets and integrity

- `skill/plan-and-execute/scripts/routingctl.py` (SHA-256 `f792363c783596aef972925edb9aad5d97b86da43e45a212a69c5a2355a78616`): `lift_tier` L214-220; `route_rungs` L230-242; `escalation_step` L245-255
- `skill/plan-and-execute/scripts/run_isolated.py` (SHA-256 `00ffc3bce6093d63198b910eaad7e8a76f739dd226eb6399c2e6fa54301908df`): `choose_route` L301-346; `ladder_exhausted` L2152-2169
- `skill/plan-and-execute/scripts/planctl.py` (SHA-256 `c3cdf3064fa18b7271ea801c614e18b45a467b4c923b98fdb8fbd16ab00bffd4`): `PlanError` L85-86; `review_checks_for_schema` L89-99; `now_utc` L102-103; `slugify` L106-109
- `skill/plan-and-execute/references/MODEL_ROUTING.md` (SHA-256 `886f53a8817d4a7eb9e93a24e715a57cce927ee1b673384e60cfe46c0814c7c9`): `# Model and provider routing` L1; `## Objective` L12; `## 1. Classify the leaf, then look up the floor` L16; `### Candidate selector (opt-in, pure)` L35

## External basis

- [E012] [FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance](https://arxiv.org/abs/2305.05176) - Chen, Zaharia and Zou / arXiv; accessed 2026-10-28.
- [E013] [RouteLLM: Learning to Route LLMs from Preference Data](https://arxiv.org/abs/2406.18665) - Ong et al. / arXiv; accessed 2026-10-28.
- [E014] [AutoMix: Automatically Mixing Language Models](https://arxiv.org/abs/2310.12963) - Aggarwal et al. / arXiv; accessed 2026-10-28.
- [E040] [Timeouts, retries, and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) - Amazon Builders Library; accessed 2026-10-28.

Consult only these entries in `SOURCE_REGISTER.md` for the checked finding and scope. Provider documentation establishes an interface, not this account's available quota or a universal ranking of model quality. The proposed design below combines that evidence with the repository observations; it is not a vendor guarantee.

## Alternatives and cost/quality tradeoffs

| Disposition | Approach | Tradeoff |
|---|---|---|
| current_baseline | Fixed four-failure provider slots | Cheap but repeats no-op tops and can skip eligible providers. |
| recommended | Distinct dispatch ladder with local evidence | Deterministic and explainable; integration is guarded by an opt-in contract. |
| rejected | Always jump to the most expensive model after any error | Confuses environment faults with capability and wastes attempts/cost. |

## Implementation instructions

1. Define an effective route identity after tier lifting, effort clamping, snapshot resolution and workload-profile resolution. Include the actual backend/quota identity but never secret values.
2. Build distinct useful rungs with their originating logical tiers. Collapse no-op effective dispatches without reordering different models.
3. Evaluate failure evidence per provider and phase; retain a task-wide attempt budget as a separate invariant. Define an explicit one-repeat exception for mechanical/budget failures, not arbitrary repeated top attempts.
4. Add pure legacy replay fixtures reproducing the original section2.8 sequences. New behavior must be gated; do not change existing disabled-mode assertions to make tests pass.
5. Limit this task to primitives and tests. Tasks070-081 own configuration, state migration, runner integration and handoff so the same feature is not implemented twice.

## Acceptance tests to implement and run

- [ ] Equal resolved model/native effort produces one useful rung.
- [ ] An empty logical tier lifts upward without lowering the requested capability floor.
- [ ] Evidence from providerA cannot exhaust providerB before B executes.
- [ ] Environmental, plan_defect and timeout_ceiling failures do not drive capability switching.
- [ ] Reset behavior and design-phase accounting are explicit, tested and separate from quota cooldowns.

These cases are proposed test obligations. A research report or a fake-provider fixture cannot establish production model performance. Record executed commands, exit codes, source state and logs in the task's implementation receipt.

## Economic evaluation

Evaluate avoided identical dispatches, provider reachability and success per total attempt cost. Offline replay proves route properties only, not real task success or monetary savings.

## Rollout and compatibility

Use the existing small deterministic helpers and compose through `run_concise.py` where applicable. Preserve disabled-mode behavior, persisted schema compatibility and locally edited installed copies. Add a behavior-changing policy only behind an explicit tested option. Do not add a framework, a paid model call or a global setting merely to satisfy this report. If current code already satisfies a proposed invariant, keep it and add the missing regression evidence instead of duplicating the mechanism.

## Limits and unresolved verification

- Quality equivalence across providers is not established by matching tier labels. Real-run calibration remains an authorized evaluation step.
- No paid model benchmark, Windows live execution or independent maximum-model code review was performed during this research. Those are distinct future acceptance activities where applicable.

## Task handoff

Task **020** now implements this recommendation; task **021** reviews the resulting code and requires corrections before acceptance. Read this report, its JSON decision record and only the assigned source paths. Do not repeat broad research unless a material version mismatch invalidates a specific finding. No second plan is required.
