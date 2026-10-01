# Optional Jev diagnostic adviser implementation

Target branch: `JEV`. Main is intentionally left unchanged until an explicit merge request.

## Scope implemented

- Added a lazy Jev adapter using the TypeSafe System One `Choice` API.
- Kept Jev outside the coding-provider catalog and all coding route ladders.
- Reused the existing post-validation advisory hook rather than creating another orchestration path.
- Added per-task and per-plan reservation budgets, duplicate suppression, confidence abstention, usage telemetry, and no-retry fail-open behavior.
- Split provider-specific advisory documentation so Jev instructions are not loaded in normal/Claude-only flows and Claude details are not loaded in Jev flows.
- Updated configuration validation and the setup wizard so `jev` is an advisory provider only; selecting it does not ask for coding model tiers/effort.
- Fixed the adjacent redaction order so secret removal happens before fixed-size evidence truncation.

## Runtime behavior

Jev is called only when all of the following are true:

1. advisory mode is explicitly enabled;
2. `assistant.provider` is `jev`;
3. `TYPESAFE_API_KEY` exists;
4. deterministic validation has failed and the existing trigger is eligible (repeated ambiguous failure, repeated unhealthy resource evidence, or confirmed stall);
5. the same evidence was not already reserved/sent;
6. per-task and per-plan budgets remain.

Otherwise the normal execution path continues. Missing key is rejected before reservation. Once a provider dispatch is reserved, interruption/provider failure consumes that reservation to avoid accidental rebilling after resume.

A valid Jev response must select one of the six existing diagnostic classes and provide a valid probability distribution, confidence, returned model, and nonnegative usage counts. `unknown` or confidence below the threshold is retained only as a skipped result. Accepted Jev advice contains no model-generated free-text hypothesis: a fixed local description is attached to the selected class before the untrusted hint reaches the next worker.

## Validation performed locally

Offline tests send no authenticated Jev request. The new Jev suite covers request shape, fixed endpoint, credential separation, 401/402/403/429/529/network/redirect handling, strict response validation, missing-key zero-call behavior, low-confidence abstention, usage telemetry, and plan-wide call budgeting.

The existing advisory, availability, routing, context, lifecycle, pattern, planning, provider, study, token-efficiency, and other Python self-test suites were rerun. Nineteen of twenty suites passed in the recovered skill-only CI artifact. `configure_self_test.py` passed all Python-side tests but its Node bridge assertion could not run locally because that artifact intentionally lacks repository root `bin/plan-and-execute.js`. The full repository CI on the pushed branch/PR is the authoritative check for that bridge.

No live TypeSafe call was made because no `TYPESAFE_API_KEY` is available in this environment. Therefore real classification quality, account-specific credit exhaustion semantics, billing, and latency remain unverified and must not be presented as proven improvements.

## Follow-up experiment before broader Jev use

On consented representative failures, compare normal execution versus optional Jev with independently adjudicated outcomes. Measure total input tokens/cost per validated TODO, additional retries, regressions/omissions, latency, abstention rate, and whether the diagnostic suggestion changed a worker action beneficially. Keep a held-out set and include `unknown`/adversarial evidence. Do not expand Jev into planning, routing, or context deletion unless that experiment demonstrates a clear net benefit.
