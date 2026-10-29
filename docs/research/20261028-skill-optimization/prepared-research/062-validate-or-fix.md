# 062 - Validate Or Fix: research revision 2

Date: 2026-10-28. Feature: `F029`. Implementation TODO `062`; independent review TODO `063`. Product baseline: `0.11.0` / tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Prepared design evidence, not implemented code. Implementation and independent review remain pending.**

## Recommended direction

Keep validate-or-fix as a thin plan-free entrypoint into the shared monitoring and evidence engine, with explicit repair authorization and no hidden second orchestration state.

This is a conditional engineering recommendation for this repository, not a proof of a global optimum or a measured saving on the user's workload.

## Change from the previous report

The revision focuses on composition and consent boundaries: DIRECT may use monitored validation without creating a plan, but validation and code modification are separate requested effects.

The previous report is retained under `docs/plans/20261028-skill-optimization/history/research-round-1/prepared-research/` for audit. New W-prefixed sources below are the current-round evidence; old E-prefixed sources remain background.

## Questions and repository evidence

- Check companion resolution, no-plan receipts, escalation and reuse of the shared resource map.
- Preserve fast DIRECT checks and measure observer activation costs for long validations.

**Baseline observations:**
- validatectl has a guarded standalone validation path, receipts, classification and repair-route selection. The companion skill resolves the shared implementation rather than duplicating all runner logic.
- DIRECT can opt into monitored validation without creating a plan, but must still preserve the user's fast path for short deterministic checks.

All listed file hashes matched the preserved 0.11.0 source in this revision. This is integrity checking, not a second full code audit.

| Code anchor | SHA-256 | Selected symbols / location |
|---|---|---|
| `skill/plan-and-execute/scripts/validatectl.py` | `7e1c4e67fa5cc0bec9659bc7a22317877ab833b0d866166e5419e7423035c3e6` | repair_route:186; packet:249; run:287; cleanup:396 |
| `skill/plan-and-execute/scripts/companion_self_test.py` | `cd102c350a3e50e378c5b033badd13ea73324bd066d37c05e3de70e029f9c988` | CompanionTests:16; test_router_is_narrow_and_bounded:17; test_source_contains_wrappers_not_a_duplicate_runtime:25; test_read_only_cli_entrypoints_do_not_create_planning_state:32 |
| `skill/validate-or-fix/SKILL.md` | `6ea99922906f1ac413dc63277fd26bc82605b571f0a43224e4f085cee5139e6f` | # Validate or Fix:6; ## 1. Choose the smallest useful validation:10; ## 2. Run one owned supervisor:16; ## 3. Inspect, repair and rerun:26 |

## Deeper analysis and competing approaches

### 1. Design analysis

The companion skill should not duplicate map, process, failure or quota logic. Use one shared runtime library/control entrypoint and a short intent router. A small direct task can request monitored tests without paying for a TODO graph, plan review or manifest; only the explicitly selected validation session metadata is created.

### 2. Design analysis

Validate-only must not silently repair. Repair mode can be explicitly authorized by the user request or selected policy, then use a bounded attempt budget, allowed write scope and independent rerun of checks. A failing test caused by service health or permissions is not a reason to raise the model tier.

### 3. Design analysis

Preserve standalone session resumability without borrowing an unrelated active plan or rewriting its task statuses. Pin command, input and resource-map generation so a completed validation from one session cannot satisfy another. Cleanup should remove only owned validation artifacts under retention policy; it must not erase product changes.

### 4. Design analysis

Documentation and packaging need to make the dependency between the two skills explicit. Prefer a shared installed runtime path resolved by deterministic discovery rather than copying code into both bundles. If a companion dependency is absent, report an actionable preflight error, not a partially working fallback with weaker checks.

The analysis above is a repository design synthesis. The linked publications establish capabilities or bounded empirical observations, not this skill's future measured performance. Exact account behavior and installed-version compatibility remain implementation-time checks.

| Alternative | Benefit | Cost / failure risk | Disposition |
|---|---|---|---|
| Require a full plan for every test | Uniform workflow | Defeats DIRECT token savings | Reject |
| Duplicate monitoring code in each skill | Standalone packaging | Drift and inconsistent safety | Reject |
| Thin companion on shared runtime | Consistent behavior and low loading cost | Dependency must be explicit | Recommended |
| Automatically repair any failed validation | Convenient | Unrequested edits and unbounded spend | Explicit repair mode only |

## Ownership and scope boundary

This implementation owns its declared write scope and acceptance tests. Its following review checks the actual changed code; prepared research is not acceptance evidence.

Implementation may preserve an already-satisfied invariant with a regression test and a documented no-change rationale; do not add code solely to make every recommendation produce a diff.

## Implementation instructions

1. Use a small trigger contract: plain build/lint/unit checks run directly; long, stateful or repeatedly ambiguous checks can request mapped monitoring without a TODO plan.
2. Pin standalone receipts to command, map and relevant source state, and give every runtime artifact an owned location outside product files.
3. Keep monitoring deterministic until an eligible ambiguity event; elapsed time alone does not force a paid observer.
4. Separate repair proposal, authorized edit execution and independent deterministic validation. The observer cannot approve its own repair.
5. Test companion discovery, missing/mismatched shared version and installation/uninstall boundaries. Fail clearly rather than importing a random similarly named module.
6. Keep validate-only and repair authorization distinct; DIRECT monitoring creates no implementation TODO plan.
7. Reuse the same runtime state, map, classification and cancellation code instead of copying logic into the companion.
8. Pin standalone validation sessions to command/input/map generation and preserve unrelated plans and user logs.

## Acceptance and counterexamples

- A short passing command leaves no manifest, TODO or orchestration directory.
- A long mapped validation records progress and can diagnose a stall without creating a plan.
- A successful old receipt is rejected after source or command changes.
- A missing companion/shared implementation produces an actionable version error.
- A failed repair never overwrites a successful receipt or claims completion from a model narrative.
- Validate-only failure leaves source files unchanged.
- Standalone monitored validation creates no plan manifest or TODO checklist.
- A missing companion runtime dependency fails before test/model execution.
- Authorized repair obeys write scope and passes independent rerun before success.

## Cost, latency and quality decision

Compare setup tokens and diagnostic latency with unmonitored direct testing and full orchestration, including retry/repair cost. Shared code reduces maintenance, not necessarily model runtime by itself.

Compare total cost per independently validated outcome against the current implementation and a simpler qualified single-worker baseline. Count failed attempts, reviews, cache writes/reads, advisory calls and tool/runtime overhead in their native units. Unknown prices, quotas or usage remain unknown, not zero. Preserve capability and security floors; no automatic rollout follows from fixture replay alone.

## Evidence used in this revision

- [W-SKILLS] Agent Skills, [Agent Skills specification](https://agentskills.io/specification). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-SRE] Google SRE Workbook, [Monitoring](https://sre.google/workbook/monitoring/). Accessed 2026-10-28. Reading scope: Public book chapter monitoring sections inspected; not a claim of reading the whole book. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-REPLAY] LangChain, [Graph API: re-execution and idempotency](https://docs.langchain.com/oss/python/langgraph/graph-api). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-INJECTION] OWASP, [LLM Prompt Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-COST] Anthropic, [Optimizing for cost and intelligence](https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence). Accessed 2026-10-28. Reading scope: Cost/context/delegation sections and coding measurement footnote inspected, including sample, hidden-test grading and paired intervals. Results are vendor-specific, not measured for this repository. Public source reading is not an independent code review or reproduction of vendor experiments.

Prior-round context: [E002], [E009], [E043], [E001]. See `SOURCE_REGISTER.md` for records; these were not all independently refreshed.

Search themes inspected in this round: Agent Skills specification progressive loading reusable resources; Google SRE monitoring tested signals; durable execution replay idempotence; Anthropic simple agents cost.

## Unverified limits and refresh triggers

- Actual user service maps and real repair-model execution remain untested. The task must retain explicit permission requirements.
- No end-user installation or live repair model was exercised. Package dependency resolution and cross-platform execution remain future implementation tests.

No authenticated provider invocation, live quota/cost benchmark, independent model review, or Windows runtime test was performed in this research revision.

Refresh only evidence contradicted by the installed CLI, selected account/billing plan or changed code contract. Unknown required capability blocks that candidate; it does not justify widening permissions.
