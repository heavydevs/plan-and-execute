# Request extension P057 — 2026-11-14: collect all failures, fix by focused reruns, confirm entire suite

Branch `checkpoint/plano1-estudo-provider-switch-20261028`; active plan `.ai-work/20261028-skill-study-provider-switch`.

User requirement: when automated validations reveal failures, stop repeating previously passing tests after every individual fix. Instead run all safely runnable tests to build a complete failed-test inventory, with per-test stacktraces, logs and E2E screenshots/traces if available; repair by focused reruns; run entire suite after all known failures are resolved, repeating boundedly until a full clean run. Study books, articles, official agents/runners and current source first.

Decision: continue only safely independent test suites after ordinary test failure; stop for fatal build/dependency/environment conditions. Prefer framework-native JUnit/JSON and failed-only selectors, no raw-shell inference. Keep source-pinned, redacted, bounded evidence and root-cause clusters. Each final accepted task still needs a genuine full green run on current source and service map. Never conceal flaky/skipped/unrun cases. Reuse existing process/resource/job monitors and qualified workers.

Implementation-ready research: `docs/research/20261028-skill-optimization/prepared-research/109-batched-test-failure-triage.md`. Add pending task 109 and actual independent correction review 110; 110 gates 082 integration, whole-skill 086 remains last. This amendment does not itself run tests, code or authenticated models.
