# P058/P059 — Economical, impact-aware automated-test architecture (TODO 111/112)

Prepared 2026-11-19 for branch `checkpoint/plano1-estudo-provider-switch-20261028`. **Implementation-ready design, not product implementation.** No future skill script, model review, benchmark, or regression pass is claimed complete. Task 111 implements the test policy/selection engine; task 112 reviews it independently. This report is maintainer evidence, NOT a default agent prompt.

## Diagnosis and boundaries

Current product/plan sources to inspect on execution: `skill/plan-and-execute/SKILL.md`, `references/WORKFLOW.md`, `TEST_RESOURCE_MONITORING.md`, `TOKEN_EFFICIENCY.md`, `scripts/planctl.py`, `run_isolated.py`, `runner_contract.py`, `service_map.py`, `resource_watch.py`, `validatectl.py`, `docs/plans/20261028-skill-optimization/support/run_task_checks.py`, `TASK_INPUTS.json`, pending 109/110. Current batch-failure research is `109-batched-test-failure-triage.md`; it addresses the **within-selected-suite failure loop**, not safe cross-task selection.

The harmful pattern is broad browser/E2E test generation for every field/branch followed by repeated all-project E2E runs after unrelated changes. Changing only the runner without improving the generated test portfolio leaves execution expensive. Conversely, blindly eliminating E2E misses real browser/auth/data integration behavior.

Do **not** change existing user test suites retroactively; P060 defines separately authorized review/refactor. Do not perform application performance/load/stress benchmarks unless requested; the implementation's **test-runner overhead regression** fixture is allowed. Do not confuse unit test count with test effectiveness, percentage coverage with requirement coverage, or passing cached results with current-source evidence.

## Evidence and tradeoffs

| Evidence | Conclusion and limit |
|---|---|
| Google, *Software Engineering at Google*, publicly accessible ch.11 and ch.14 | Distinguishes test **size/cost** from **scope**. Strong preference for small/medium narrow tests and fewer expensive broad/E2E tests; quality, confidence and determinism matter more than a rigid count ratio. Examples 80/15/5 are an illustrative guideline, not a product rule. |
| Mike Wacker, Google Testing Blog 2015 | Test pyramid vs inverted pyramid/hourglass, testing through lower layers. Older 70/20/10 heuristic is not mandatory. |
| Ham Vocke, Martin Fowler site, *The Practical Test Pyramid* | Contract/integration tests at boundaries can detect errors without replaying browsers; push tests to lowest trustworthy layer. |
| Playwright official best practices/configuration | Real user-visible behavior, role/text locators, web-first assertions, isolation, bounded traces on failure, worker isolation and CI sharding. |
| Jest/Vitest, Nx, pytest, Gradle docs | Deterministic affected/related selection is available for supported stacks, but there are graph limitations; selectors and zero-selected results must be verified. Nx 24 task-input behavior differs from older project-graph selection. |
| Engström et al., systematic regression-test-selection review | Different methods have different scope/validity limits; no universal safe minimal affected set. |
| Machalica et al., ICSE-SEIP 2019, Facebook/Meta predictive selection | Reported about 2x infrastructure efficiency and high regression-detection in its own industrial setting; this is not an expected saving for this skill and ML is unjustified without validated historical training data. |
| Meszaros, *xUnit Test Patterns*, publisher material | Test smells, fixture management, independent tests, and refactoring techniques; **publisher overview, not full book**. |
| Fowler, *Eradicating Non-Determinism in Tests* | Flaky tests are not fixed by unbounded retries; isolated fixtures, asynchronous assertions and tight quarantine governance matter. |

### Alternatives

1. **Broad E2E for each behavior + all tests every task**: realistic UI exercise but exponential maintenance/browser cost and slow failure localization — reject as default.
2. **Only unit tests + E2E once per release**: fast, misses adapters, DB contracts, auth and deployment/real browser issues — reject.
3. **Always skip E2E until the final plan task**: fast tasks but high-risk regressions detected too late — reject.
4. **LLM predicts affected tests without deterministic graph**: unrepeatable, opaque omissions and repeated model tokens — reject.
5. **Small tests + boundary contracts + risk-scoped E2E + deterministic impact selection + final global oracle**: selected. Broaden selection when uncertainty is high; do not assert formally complete selection.

## Architecture A: create/maintain tests by behavior and risk

Before writing any automated test, create a **task-local coverage decision**, not a prose transcript: `requirement_id`, `behavior/observable outcome`, `risk (low/medium/high)`, `candidate levels`, `chosen smallest trustworthy level`, `why an upper-level check is unique`, `test IDs/paths`, `fixture/external-resource requirements`, `task-or-final validation`. Store a concise manifest row or task-local artifact; emit to AI only relevant rows.

**Default level choice**:
- Unit/component: pure business functions, validation rules, boundary and equivalence classes, data mapping, formatting, permission decision logic, error conditions, state transitions. Use table-driven/parameterized tests; deterministic clocks/inputs, meaningful assertions and property-based tests when justified. No browser for pure validation matrices.
- Integration/contract: DB transaction, persistence/repository adapters, API authorization and input rejection, consumer-provider schemas, serialization, queues, file handling and UI component integration. Prefer real local controlled dependencies with isolation; mocks are not proof of a real contract.
- E2E/browser: critical real user journeys and cross-component/browser-specific risks that lower layers cannot establish; typically one **minimum-valid-data success**, one **maximum-meaningful-fields success**, and one/few representative **UI validation/error-display journeys** per distinct user-facing flow. Do NOT mechanically create 3 tests for every form or put every invalid-field permutation in E2E.
- Validate **all expected validation rules** with parameterized unit and/or API/integration cases. Browser E2E additionally checks representative invalid cases for distinct UI mechanisms (focus/error state/accessibility/server rejection). Add a targeted browser exception for non-reducible high-risk multi-step/client interactions.
- Keep necessary security permissions/denials, payment/financial precision, migration, concurrency, time zones, browser support and contract regressions at the lowest faithful level; don't under-test on cost grounds. Preserve previously legitimate tests until equivalent behavior evidence exists.

The AI must justify every **new broad E2E** with a specific risk not already validated at a cheaper reliable layer, test independence and expected runtime/resource footprint. Do not make E2E zero by policy. Prefer semantic locators and web-first waits; no blind sleeps or order-dependent tests. Maintain failure-only browser artifacts with protected paths as P057.

## Architecture B: deterministic change-impact selector

Add a **single** `skill/plan-and-execute/scripts/test_impact.py` that extends the existing task/plan validation controller (not a second runner). A narrow command contract is proposed:

`python .../test_impact.py select --repo-root . --plan <path> --task <ID> --base-ref <pinned-commit> --output <guarded-json>`

A separate `explain` emits a compact explanation/affected-test list. The implementation must validate the contract against actual CLI/control schemas and preserve DIRECT mode without inventing an orchestrated plan. Prefer native Nx, Jest `--findRelatedTests`, Vitest `related`, pytest explicit nodeids/related-file map, Gradle `--tests` and discovered build graph; only enable adapters after checking installed versions. These tools are **candidate selectors**, not proofs of all affected behavior.

**Input model:** owned task ID; exact base and current source tree/git diff including uncommitted/untracked files; changed test paths; static import/reference dependency graph with reverse consumers; existing test ownership, tags/contract IDs, service/DB/schema/auth/shared-config dependencies and historical run metadata. Include changed/generated code and infrastructure/env/build files (CI workflows, lockfiles, fixtures, root shared types). Never derive paths from untrusted text via shell. Detect deleted/moved tests and potential missing coverage.

**Selection algorithm (bounded, explainable):**
1. Snapshot source + test + configuration + resource-map hashes before selection. Use Git diff union and task-reviewed paths, include planned generated files and touched shared fixtures.
2. Determine directly modified features and all conservative reverse-dependent modules/tests with framework project/test graph where reliable. Include changed/new tests and their required unit/integration/contract suites regardless of tags.
3. Add risk-scoped E2E smoke for affected **real user journeys** and modified browser interactions/auth/route infrastructure, if relevant. Do not auto-run the entire E2E catalog for a small server validation change whose UI behavior is covered faithfully at API level.
4. Explicit **fallback/escalation**: missing graph/mapping, dynamic imports/reflection/codegen, framework ambiguity, CI/build/lockfile/auth/global middleware/schema/shared fixtures, uncertain public contract, code changes outside baseline, source-map mismatch or incomplete previous execution -> broader parent module/suite, sometimes entire project. Security-critical paths never default to zero E2E solely because imports show none.
5. Construct **argv arrays** with validated selectors, no shell interpolation. Dry-run/collect where supported and compare selected counts/test identifiers to expected manifests. If selection is empty, unknown, corrupt, stale or unexpectedly smaller, run conservative broad suite or mark blocked, NEVER green.
6. Persist `strategy_version`, task/plan ID, baseline/current hashes, runner versions, dependency graph/index hash, config/resource-map fingerprint, impacted path list, selected validation IDs, exact argv, `reason_by_test`, confidence/unknown markers, count, result & report/evidence hashes. Atomic writes within owned plan directory; no global mutation. Reuse cache only when all relevant fingerprints match. Source changes invalidate cached success for affected obligations.
7. Use existing `resource_watch`, `service_map`, `jobctl` and P057 `test_failure_cycle.py`. Selector creates the work list; P057 collects all failures in that selected work list and fixes them using narrower selectors, then reruns **the whole mapped task suite**, not the entire product. Stop on unsafe dependency failures.
8. **Plan final**: task 082/integration or 084 release must run **all required repository test groups (unit, integration, contracts, complete E2E across configured projects/shards)** once on identical final code/config/resource map after all tasks' changes/reviews; newly discovered failure triggers P057 focused repair and repeats complete final run. Pre-existing policy-specified exceptions remain explicit and cannot be silently marked passed. Reuse an identical-hash full result between closing checks rather than rerun all E2E simply because validation phase has a second label.

Never loosen an explicit user/CI/regulatory full-suite requirement. For a DIRECT change without a native plan, operate via explicit diff boundaries and retain the existing direct acceptance gate.

## Architecture C: validation cadence and triage reconciliation

At each task: static/lint/compile preflight + **new/changed tests** + impacted narrow tests/contracts + justified critical-path E2E + independently required acceptance. On ordinary assertion failure in any mapped selection, P057 must finish all **safe independent** work to gather failures, create exact failure inventory, then run failing plus affected neighbors after each cohesive repair. After resolving known failures, require a fresh **full mapped impacted set** on final current source before accepting that task. **No task is considered validated only because its focused failing cases passed.**

At final plan close: run global all-suite gate once per final fingerprint. A later source change invalidates the relevant prior results; run the necessary affected checks and a new final global pass. Infrastructure/unavailable services are blocked/unknown, not green. Local E2E smoke early for high-risk changes is a required exception, not a violation of deferred global validation.

## Token/resource design

Keep routing summary in the main SKILL.md/WORKFLOW: one sentence linking new `references/TEST_STRATEGY.md` only if generating/changing tests or selecting tests. Keep detailed policies, examples, adapter tables and evidence in that reference and deterministic `test_impact.py`. Workers read only current task coverage matrix, changed symbols, selected tests and bounded failure evidence; not whole test repository, previous full logs, every provider guide or entire research. Deterministic code computes dependency graph/cache/reports; no LLM polling tests. Stable prompt prefix, task-specific suffix. Architecture/review use existing qualified model routing; only invoke a stronger model for nuanced risk/design decisions, not to enumerate tests. No model-to-model handoff on each test.

## Adversarial acceptance and measurement

1. Form with 45 validation rules: table-driven unit/API verifies all 45; E2E exercises min/max success and distinct presentation/error mechanisms, rather than 45+ browser scripts; a genuinely unique high-risk client validation may add one E2E with rationale.
2. Project with 1,000 tests / 100 E2E: small isolated service change selects exact changed tests, reverse dependencies, integration contracts and only justified E2E; final plan executes the global catalog. No fabricated savings percentage.
3. Changed shared auth middleware, database schema, test harness/lockfile or dynamic import unresolved -> scope expands. Unknown/empty selector never passes. New tests are always included.
4. P057's 100/7 failure scenario runs initial selected suites to completion, reruns failed/impacted cases, full **mapped** task suite only after repair, and **global** suites during plan closure. Distinguish command-level from test-case fail-fast.
5. Hash drift/partial shards/retries/flaky/environment unavailable prevent using previous passes as current acceptance. Required projects/OS/browser matrices must match actual configured obligations.
6. Compatible pytest, Jest/Vitest, Playwright, Maven/Gradle examples plus unfamiliar runner fallback; no swallowed nonzero exits.
7. Reviewer tests a seeded regression outside inferred graph and cross-cutting changes; fallback/selection escalation must expose it. Include real new/old tests and deliberate failure injection.
8. Benchmark **test-run overhead only** on frozen representative fixtures with same revision/config/hardware and failure corpus: p50/p95 elapsed, browser launches, repeated cases, CPU, flaky rate, regression detections, unknown selection, user/agent interactions and model usage where available. Evaluate **quality per accepted outcome**, not merely minimum runtime. No performance/load stress on product.

## Primary research, reading scope and accessible books

Access checked 2026-11-19; URLs are provenance, not claims of complete restricted-book reading.

- [G1] Adam Bender, Google public book ch11 *Testing Overview* (full open chapter): https://abseil.io/resources/swe-book/html/ch11.html
- [G2] Joseph Graves, Google public book ch14 *Larger Testing* (full open chapter): https://abseil.io/resources/swe-book/html/ch14.html
- [G3] Mike Wacker, *Just Say No to More End-to-End Tests*, Google Testing Blog: https://testing.googleblog.com/2015/04/just-say-no-to-more-end-to-end-tests.html
- [G4] Ham Vocke, *The Practical Test Pyramid*, Fowler publication: https://martinfowler.com/articles/practical-test-pyramid.html
- [G5] Martin Fowler, *Integration Test*: https://martinfowler.com/bliki/IntegrationTest.html
- [G6] Martin Fowler, *Eradicating Non-Determinism in Tests*: https://martinfowler.com/articles/nonDeterminism.html
- [D1] Playwright best practices: https://playwright.dev/docs/best-practices
- [D2] Playwright reporting and sharding: https://playwright.dev/docs/test-reporters and https://playwright.dev/docs/test-sharding
- [D3] Playwright E2E tagging, traces and resource setup: https://playwright.dev/docs/test-annotations , https://playwright.dev/docs/test-use-options , https://playwright.dev/docs/test-parallel
- [D4] Nx affected (CURRENT semantics, verify installed major): https://nx.dev/docs/features/ci-features/affected
- [D5] Jest CLI `--findRelatedTests` (static graph limitation): https://jestjs.io/docs/cli
- [D6] Vitest CLI `related` (dynamic import limitation): https://vitest.dev/guide/cli
- [D7] pytest last-failed fallback: https://docs.pytest.org/en/stable/how-to/cache.html
- [D8] Gradle JVM tests/filter: https://docs.gradle.org/current/userguide/java_testing.html
- [S1] Engström, Runeson & Skoglund, systematic review (abstract and accessible university paper): https://www.sciencedirect.com/science/article/pii/S0950584909001219
- [S2] Machalica et al., *Predictive Test Selection* ICSE-SEIP 2019 (abstract): https://ieeexplore.ieee.org/abstract/document/8804462 and Meta engineering summary: https://engineering.fb.com/2018/11/21/developer-tools/predictive-test-selection/
- [B1] Gerard Meszaros, *xUnit Test Patterns: Refactoring Test Code* (publisher listing/overview, not full book): https://www.oreilly.com/library/view/xunit-test-patterns/9780131495050/
- [B2] Jez Humble & David Farley, *Continuous Delivery* (publisher overview, not full book): https://www.oreilly.com/library/view/continuous-delivery-reliable/9780321670250/
- [A1] Claude skill progressive disclosure (official): https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview

**Evidence versus design choice:** tool capabilities and caveats, open Google chapters and Meta's reported study results are external evidence; policy thresholds, provenance schema, exact scope expansion and full-at-plan-close orchestration are proposed implementation choices requiring real validation. No real plan-scale latency, quality or token reductions have been measured.
