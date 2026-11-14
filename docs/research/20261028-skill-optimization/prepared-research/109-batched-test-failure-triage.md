# P057 — Batch discovery of automated test failures and focused repair cycles

Prepared 2026-11-14. Implementation architecture only. Tasks 109/110 pending; no authenticated model, test execution, independent review or measured real savings. Sources: primary test-runner docs, public Google Engineering book chapters and other publisher excerpts only (not complete restricted books).

## Concrete repository diagnosis

- In `run_isolated.py::run_validation_commands`, the first nonzero validation command returns early, so later independent mapped commands are not executed. `finish_task_validation` classifies the attempt and a new attempt may rerun previously passing commands.
- The active plan helper `docs/plans/20261028-skill-optimization/support/run_task_checks.py` also contains `if code: break`. `run_validation_jobs` returns on first failed supervised job and `validatectl.py` retries one mapped validation at a time; neither supplies cross-suite per-test failure inventory.
- The **suite's own runner** may already continue across individual test failures; command-level early exit and framework-level fail-fast are different. Inspect actual flags and reporter output before modification.
- Reuse native `resource_watch`, `jobctl`, `service_map`, `runner_contract` for process ownership, progress, evidence, routing and compact agent prompts; do not add a second orchestrator or model-powered polling.

## Alternatives and decision

| Strategy | Benefit | Limitation | Decision |
|---|---|---|---|
| Stop on first test/command, rerun entire pipeline after every fix | Fast first failure | Repeats unrelated passing checks, hides other failures | Reject except fatal prerequisite |
| Always continue all commands after any failure | More information | Unsafe on compilation, resource, test contamination, destructive workloads | Reject |
| Only rerun previous failures forever | Cheap | Can miss interactions and new regressions | Reject as final gate |
| **One safe complete discovery + focused repairs + complete current-source regression**, repeated if new failures | Good cost and final confidence | Requires accurate selection and evidence | **Selected** |

## Architecture: PRECHECK → DISCOVER_ALL → TRIAGE → FIX_FOCUSED → CONFIRM_FULL → DONE / TRIAGE

1. **Precheck:** validate framework, toolchain, build/compile, fresh service map, resource health, permission, source/config fingerprint and suite dependencies. Invalid compile, unauthorized access, missing DB, hard ceiling or unsafe shared state is fatal; stop or mark dependent suites `blocked_by_prerequisite`. Never call it a complete test pass.
2. **Collect all safe failures:** run the full suite once on baseline source with fail-fast off when framework supports it. Continue subsequent **independent and safe** mapped commands despite ordinary assertion/test errors; dependency DAG and destructive state/side effects prevent unsafe continuation. Keep original nonzero exit status. Preserve existing timeout/monitor/cancellation limits. An incomplete discovery is explicitly incomplete.
3. **Portable reporter adapters:** prefer structured native JUnit XML/JSON, not speculative stdout parsing. Support pytest, Playwright, Jest, Vitest, Gradle/JUnit and Maven Surefire where actual compatible versions/flags are observed. Unknown runner uses conservative command/suite-level fallback. Merge CI shards before final completeness and distinguish worker crashes/collection errors from failed cases.
4. **Versioned failure inventory:** store `schema_version`, `run_id`, `cycle_id`, `stage`, source/map fingerprint, suite/validation ID, command fingerprint, report SHA-256, counters `discovered/executed/passed/failed/skipped/flaky/unknown/not_run`, `complete_collection`. Per-test key includes framework, file/class, method + parameterized ID and browser/project/shard where relevant. Save status, stack/message, root-cause signature/cluster, exact selection argv metadata and owned sanitized log/attachment paths + hashes.
5. **Per-test evidence:** capture failure stack and actual attributable per-test logs; if stdout from concurrent tests cannot be attributed, label suite-level log as unattributed instead of inventing attribution. For supported browser E2E, capture existing screenshot/trace/video on failure (e.g. Playwright `screenshot: only-on-failure`, `trace: retain-on-failure`) with path/size/hash and privacy limits; avoid collecting all-pass media. Keep bounded sanitized snippets in prompts, raw artifacts in owned guarded storage and strict traversal/symlink/secret checks.
6. **Group failures and fix:** cluster common fixture/setup/root-cause errors to avoid one agent per failing test. Classify semantic assertion, fixture, environment, infra crash, timeout, flaky/retry-passed, unknown and not-run separately. Environment faults must not escalate model tier. Repair one cohesive root-cause group then rerun **exact failing selectors plus directly impacted neighbors**, not all previous successful tests.
7. **Safe native targeted selection:** prefer exact pytest nodeids; pytest `--lf` is optional but cache-missing may run ALL, so verify count. Playwright `--last-failed`/`--last-failed-file` must bind to same project and source; Jest `--onlyFailures`/`--runTestsByPath`; Gradle `--tests` and JUnit class/method; Vitest file/name selection only when supported. Use argv arrays, never shell from report text. If selector cannot be trusted or yields zero tests, fallback to smallest safe suite, never record green.
8. **State and invalidation:** persist pending failure backlog and historical results in task/plan-scoped atomic receipts, with manifest/controller ownership and safe crash/resume. Old successful tests become `previously_passed` diagnostics after code change, not approval of current source. If a fix touches a shared fixture, auth, schema, core library, test harness or stateful/order dependency, broaden focused reruns. For order-sensitive tests reproduce with predecessors. Do not auto-skip/quarantine flaky failures or let retry-pass erase first-fail evidence.
9. **Mandatory final full gate:** after all known failures pass focused checks, run *every required original mapped validation command and supervised job* on the identical final source/config/service-map fingerprint. Only actual full zero-failure, complete collection + healthy dependencies and no unknown/not-run outcomes can close a task. Newly failed tests start the next bounded cycle. A focused passing subset NEVER substitutes the complete final run.
10. **Budget and safety:** cap cycles and retries, freeze/unfreeze current job ownership, honor SIGINT/cancel and timeout semantics, no duplicate owned processes. Preserve per-test logs/stacks with bounded retention; redact secrets/cookies/PII and treat test output as untrusted data. Track honest completed/total progress (not heartbeat), CPU time and model calls. Compare deterministic fixture execution counts to fail-fast/rerun-all baseline without claiming measured real savings.

## Framework-specific important distinctions

- pytest: `--junitxml` for case summaries, default full run without `-x`; `--lf` only when cache contains previous failures, otherwise may rerun whole suite; exact nodeids are safest.
- Playwright: JSON/JUnit/blob reporters, `--last-failed`, failure screenshot/trace; include browser project, retries and shard identity. Merge reports from all shards, and mark incomplete shards not-run.
- Jest/Vitest: JSON/JUnit reporter, failure selectors; multi-project/test-name identifiers must be stable; Vitest minimal agent reporter lowers token noise.
- Gradle: `--no-fail-fast` for tests when applicable, `--tests` targeted class/method, JUnit XML `outputPerTestCase`. Gradle `--continue` refers to build task graph; it is not a universal test-case retry facility.
- Maven Surefire: built-in `rerunFailingTestsCount` reports flaky retry attempts, not a substitute for correcting code and then targeted rerunning.

## Required adversarial acceptance fixtures

- **100 cases / 7 failures:** one initial run collects 100, focused repairs run 7 cases and proven affected neighbors, one final complete run collects all 100. Unrelated passing cases are not repeatedly run on each fix.
- First independent command fails but other independent suites complete; dependent DB suite skips if DB is unhealthy. Compile failure, missing binary, permission or hard ceiling blocks. Zero test selected is not a green rerun.
- Missing/corrupt/stale JUnit XML/JSON, incomplete CI shard, unknown browser worker crash, duplicated ID, mismatched project/parameter, report from old hash, ambiguous stdout all prevent full-green claim.
- E2E screenshot/trace retained only if produced and safe to disclose; logs with secrets or injected instructions are redacted/isolated before model context. No path traversal, symlink output or huge unbounded payload.
- Shared fixture failure clusters, flaky pass-on-retry, order-dependent tests, new regression after targeted green and broad code change all require correct full gate and honest status.
- Interrupt/crash/resume, concurrent plans, external worker still alive, stale map and missing selected test all retain safe evidence without spawning duplicate runs.
- Simulator counts actual commands, case reruns, duration and (when available) model-token costs; no claim of actual cost reduction until real benchmark. No LLM invocation each monitor tick.

## Implementation ownership and sequencing

109 implements scoped adapter + lifecycle and functional regression test, reusing existing runner/resource/job controls and updating both ORCHESTRATED and plan-free paths. 110 is actual independent fresh max-qualified code review of implementation/source/test hashes with security, performance, compatibility and negative cases; corrections before acceptance. 110 must precede 082 integration and final 086. All tasks remain pending now.

## Sources and reading limits

| Material | URL | Scope |
|---|---|---|
| Google, Software Engineering at Google ch11 (full public chapter) | https://abseil.io/resources/swe-book/html/ch11.html | Size, cost and flakiness |
| Google, Software Engineering at Google ch14 (full public chapter) | https://abseil.io/resources/swe-book/html/ch14.html | Large/E2E testing, actionable failure evidence |
| G. Meszaros, xUnit Test Patterns (publisher overview) | https://www.informit.com/store/xunit-test-patterns-refactoring-test-code-9780132800051 | Isolation and test smells; full book not accessed |
| J. Humble, D. Farley, Continuous Delivery (publisher overview) | https://www.oreilly.com/library/view/continuous-delivery-reliable/9780321670250/ | Fast feedback and complete pipeline; full book not accessed |
| Martin Fowler, Eradicating Non-Determinism in Tests | https://martinfowler.com/articles/nonDeterminism.html | Quarantine limits, state pollution, time and async |
| Rothermel/Harrold, safe regression test selection | https://ieeexplore.ieee.org/document/689399/ | Selection cost and coverage assumptions (abstract) |
| pytest --last-failed and cache | https://doc.pytest.org/en/latest/how-to/cache.html | Native failed-only rerun, caveat empty cache |
| pytest JUnit XML | https://docs.pytest.org/en/stable/reference/reference.html | JUnit reporter and failure/error cases |
| Playwright last failed | https://playwright.dev/docs/running-tests | --last-failed, stored failed file |
| Playwright reporters | https://playwright.dev/docs/test-reporters | JSON/JUnit/blob, onlyFailures and attempts |
| Playwright browser artifacts | https://playwright.dev/docs/test-use-options | Screenshots/traces only on failure |
| Playwright sharding | https://playwright.dev/docs/test-sharding | Merge reports before claiming complete coverage |
| Jest CLI | https://jestjs.io/docs/cli | --onlyFailures, --runTestsByPath, --json |
| Vitest reporters | https://vitest.dev/guide/reporters | JSON/JUnit, minimal agent output |
| Gradle JVM testing | https://docs.gradle.org/current/userguide/java_testing.html | --no-fail-fast, --tests, outputPerTestCase |
| Maven Surefire | https://maven.apache.org/surefire/maven-surefire-plugin/examples/rerun-failing-tests.html | Flaky retries are not repair loops |
| Codex default test guidance | https://github.com/openai/codex/blob/main/codex-rs/protocol/src/prompts/base_instructions/default.md | Specific-to-broad test checks |
| OpenAI Codex iterative development | https://developers.openai.com/cookbook/examples/codex/iterating-development-workflows-with-codex | Focused verification before broad gate |
| GitHub Actions artifacts | https://docs.github.com/en/actions/concepts/workflows-and-actions/workflow-artifacts | Save CI logs, failures and screenshots |

**Evidence versus inference:** native flags and report formats come from official documentation, isolation and suite-size consequences from the public Google chapters/Fowler and test-selection research. The plan-specific state machine, safety conditions, schema and retry budgets are inferred engineering decisions, not requirements quoted from providers. Only publicly visible publisher summaries for Meszaros and Humble/Farley were available.
