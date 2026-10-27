# Validation/workload whole-skill review

Review date: 2026-10-27. Source baseline: `6bdbab5`; release: `0.11.0`.
Branch: `main` only. Execution/review: host-managed in this conversation, not an independent provider/model review. No Claude, Codex, Antigravity, Gemini, Qwen, Kimi or Trae CLI was installed or authenticated here. Test provider responses are fixtures, not billed/live calls.

## Scope and own-skill execution

The authoritative request was assessed as FINAL_PLAN (about 1,334 estimated source tokens). The own-skill controller created five dependency-ordered TODOs: workload/quota routing, plan-free supervision, bounded observation, companion packaging/documentation, and whole-skill regression review. Each used the existing claim/subtask/completion transitions and mapped validation. The plan is retained locally at `.ai-work/20261027-validation-workloads`; it is not a second source of implementation truth. Research and the eight-point maintenance checklist informed this review.

## Maintenance checklist and resolved findings

| Review surface | Evidence / disposition |
| --- | --- |
| Entrypoint and lazy loading | Main remains below its existing 7,000-character bound. DIRECT has no planning state; optional validation loads only the companion/validation guide. Research is not put in worker prompts. Repaired an old blanket prohibition on all DIRECT `.ai-work` state. |
| End-to-end flow | CLI `validate` routes only to `validatectl`; fresh reviewed maps feed the existing resource/progress watcher. Nonce/lock/owner checks guard minimal receipts, recovery and cleanup. No TODO, manifest or active pointer is created for standalone validation. |
| Routing/fallback | Workload fit, floor, host/model and quota pool are separate. Opt-in profiles require observed IDs and bounded evidence. Authentication blocks a host, quota a configured family, capacity a model. Explicit provider chains and logical floors remain authoritative. Snapshot/autoselect cannot replace a chosen profile. |
| Model uncertainty | Antigravity Claude's advanced ceiling is a conservative requested policy, not a measured intelligence comparison. Flash 3.8 is an observed/documented option, not a guaranteed cheapest model. Removed unsupported Gemini CLI retirement assertions from operational docs/help; compatibility adapter behavior is unchanged. |
| Deterministic tools | Reused the canonical monitor/process engine, added bounded standalone state and role-profile selection. Companion runtime is mechanically bundled with hashes, not independently reimplemented. Normal polling makes zero model calls. |
| Evidence and safety | Prefix/tail spooling, omission indicators, redaction and cursor/digest deduplication limit ordinary context. Optional observer reservations precede requests. Logs/advice cannot approve work, execute repairs or choose deletion paths. Final structured watcher events preserve classification even when an older event falls outside the tail. |
| Resource lifecycle | Shared resource map survives both plan and standalone cleanup. Health-triggered stop is opt-in and owns only the test process tree. Successful cleanup deletes allowlisted validation artifacts only; failed/interrupted evidence and external service logs survive. |
| Packaging and installer | Independent skill selection, markers, selective/explicit activation, all-target preflight and local-edit protection are covered. Generated companion runs without its sibling. ZIP staging uses owned unique temporary files, preserves foreign temp files, and is byte-reproducible in the project packager. |

## Regression findings, not hidden retries

The baseline already failed two Windows-mocking keepalive tests on Linux. Those tests now mock the module's OS view rather than globally changing `os.name`; production behavior is unchanged.

This container's Python startup/site hooks sometimes exceeded sub-second fixture windows. Timing-sensitive stdlib test children and CLI fixtures now use `-S`; assertions and production timeout values were not relaxed. Internal process guards/bootstrap also use `-S`, while integration tests assert the actual user command still has its original site settings and arguments.

Full-suite validation also caught a genuine regression: four new primary signals were missing from the legacy tier-evaluation corpus. The corpus now includes 32 independently specified expected routes (eight new cases), including weak-validation and high-risk counterexamples. The strict signal-set equality check remains intact.

All failed and successful development-run logs were retained outside the product source; final acceptance below refers only to the passing final run, not a concatenation of partial runs.

## Final validation

- Mapped `ALL` (`npm run check`): exit 0, watcher health healthy. Includes clean, skill validation, Node tests, all 43 Python self-test entrypoints, and repository checks.
- Node: 47 tests, 46 passed, 0 failed, 1 skipped. The skip is the pre-existing unreadable-directory test under UID 0; it cannot exercise permission denial as root.
- Focused suites included in that full run: workload routing 16, standalone supervision 25, observer 19, companion Python contracts 5. Node companion coverage includes independent install/update/uninstall, local-edit protection and reproducible packaging.
- Model-routing corpus: 32 cases, no lowered floors. Existing planning, primary planning, context, lifecycle, provider, patterns, catalog, snapshot, telemetry and rollout suites passed.
- Post-review mapped CLI, SKILL_DOCS and DOC_BASELINE checks: exit 0. Documentation-baseline warnings about changed references are retained for review, not silently rewritten into a new baseline.
- `service_map audit-plan`, manifest validation and `git diff --check`: passed.
- Both independent skill archives passed the skill-creator validator/packager, ZIP integrity and exactly-one-entrypoint checks. Every companion runtime file matched its provenance hash and canonical source. The extracted companion command ran without a sibling checkout.

## Unverified and intentional limits

- Linux/Python 3.13.5/Node 22.16.0 only. Windows native scheduling, ACL/sharing behavior, Job Objects and macOS were not live-tested; portable fixtures are not a substitute for native CI.
- No real provider authentication, live quota exhaustion, model output quality or billed token/credit comparison was tested. Exact account model IDs and quota pools still require user-side discovery/configuration. The preset emits only recognized IDs actually present in the supplied inventory; other observed variants require explicit profiles.
- Observer adapters are deliberately narrower than coding adapters: verified tool-less Antigravity protocol, and explicit-key/API-opted-in Claude fallback. Other coding hosts safely skip observer invocation until a boundary is audited. An installed native CLI/auth store is trusted; this is not an OS sandbox. Known global executable customizations cause a skip rather than a settings change.
- Redaction is best-effort. Bounded raw logs remain local; review confidentiality before enabling external diagnosis. No measured token savings or universal frontend-model quality ranking is claimed.
- A technical failure may recommend a stronger repair route; the authorized host performs the repair. The standalone controller never executes model-proposed shell commands. Environmental faults/explicit ceilings are not automatic model-escalation evidence.
- Commit/push status is reported separately. A local passing test run is not proof of remote publication or remote CI success.

## Artifact fingerprints

- `plan-and-execute/skill.zip`: 567312 bytes; SHA-256 `820cc49f275cdc486dd32298e867b710d81da5365f3b98128c8b2ff6126859ce`.
- `validate-or-fix/skill.zip`: 288209 bytes; SHA-256 `07c33e55875eb4e596f4325b8a67699795aad7c5884ff81a34fde8bc872e72fe`.
- Final full-run log SHA-256: `a70dc3927041d777202471bedabb69eebc25704e5a6888dd0132f43517391a73`.
