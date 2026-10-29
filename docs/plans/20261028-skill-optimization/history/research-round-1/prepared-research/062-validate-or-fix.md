# F029 / task 062 - Plan-free monitored validation and repair

Date: 2026-10-28. Product baseline: 0.11.0, tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Research prepared; implementation pending; independent review pending.** This report is an implementation input, not a completion receipt. No external reviewer is impersonated.

## Decision and scope

**Recommendation (engineering inference):** Keep validate-or-fix as a lightweight companion using shared monitoring primitives, with no plan creation and explicit repair acceptance.

## Questions addressed

- Check companion resolution, no-plan receipts, escalation and reuse of the shared resource map.
- Preserve fast DIRECT checks and measure observer activation costs for long validations.

## Repository evidence

The following are static-code observations against the pinned baseline, not results from authenticated providers:

- validatectl has a guarded standalone validation path, receipts, classification and repair-route selection. The companion skill resolves the shared implementation rather than duplicating all runner logic.
- DIRECT can opt into monitored validation without creating a plan, but must still preserve the user's fast path for short deterministic checks.

### Read targets and integrity

- `skill/plan-and-execute/scripts/validatectl.py` (SHA-256 `7e1c4e67fa5cc0bec9659bc7a22317877ab833b0d866166e5419e7423035c3e6`): `repair_route` L186-200; `packet` L249-284; `run` L287-350; `cleanup` L396-416
- `skill/plan-and-execute/scripts/companion_self_test.py` (SHA-256 `cd102c350a3e50e378c5b033badd13ea73324bd066d37c05e3de70e029f9c988`): `CompanionTests` L16-58; `test_router_is_narrow_and_bounded` L17-23; `test_source_contains_wrappers_not_a_duplicate_runtime` L25-30; `test_read_only_cli_entrypoints_do_not_create_planning_state` L32-40
- `skill/validate-or-fix/SKILL.md` (SHA-256 `6ea99922906f1ac413dc63277fd26bc82605b571f0a43224e4f085cee5139e6f`): `# Validate or Fix` L6; `## 1. Choose the smallest useful validation` L10; `## 2. Run one owned supervisor` L16; `## 3. Inspect, repair and rerun` L26

## External basis

- [E002] [Building effective agents](https://www.anthropic.com/research/building-effective-agents) - Anthropic; accessed 2026-10-28.
- [E009] [AI engineering pitfalls](https://huyenchip.com/2025/01/16/ai-engineering-pitfalls.html) - Chip Huyen; accessed 2026-10-28.
- [E043] [Monitoring Distributed Systems, Site Reliability Engineering chapter 6](https://sre.google/sre-book/monitoring-distributed-systems/) - Google SRE; accessed 2026-10-28.
- [E001] [Agent Skills specification](https://agentskills.io/specification) - Agent Skills; accessed 2026-10-28.

Consult only these entries in `SOURCE_REGISTER.md` for the checked finding and scope. Provider documentation establishes an interface, not this account's available quota or a universal ranking of model quality. The proposed design below combines that evidence with the repository observations; it is not a vendor guarantee.

## Alternatives and cost/quality tradeoffs

| Disposition | Approach | Tradeoff |
|---|---|---|
| current_baseline | Require a full plan just to monitor tests | Reuses orchestration but imposes unnecessary artifacts and tokens on cohesive work. |
| recommended | Shared deterministic monitor with standalone receipts | Preserves fast DIRECT and avoids duplicating process/log logic. |
| rejected | Fork the monitor into a second independent implementation | Creates drift in cancellation, redaction and acceptance behavior. |

## Implementation instructions

1. Use a small trigger contract: plain build/lint/unit checks run directly; long, stateful or repeatedly ambiguous checks can request mapped monitoring without a TODO plan.
2. Pin standalone receipts to command, map and relevant source state, and give every runtime artifact an owned location outside product files.
3. Keep monitoring deterministic until an eligible ambiguity event; elapsed time alone does not force a paid observer.
4. Separate repair proposal, authorized edit execution and independent deterministic validation. The observer cannot approve its own repair.
5. Test companion discovery, missing/mismatched shared version and installation/uninstall boundaries. Fail clearly rather than importing a random similarly named module.

## Acceptance tests to implement and run

- [ ] A short passing command leaves no manifest, TODO or orchestration directory.
- [ ] A long mapped validation records progress and can diagnose a stall without creating a plan.
- [ ] A successful old receipt is rejected after source or command changes.
- [ ] A missing companion/shared implementation produces an actionable version error.
- [ ] A failed repair never overwrites a successful receipt or claims completion from a model narrative.

These cases are proposed test obligations. A research report or a fake-provider fixture cannot establish production model performance. Record executed commands, exit codes, source state and logs in the task's implementation receipt.

## Economic evaluation

Measure startup/files created, observed CPU/I/O overhead, model calls and validated repair outcomes. Monitoring should earn its cost; do not universally enable it for every tiny test.

## Rollout and compatibility

Use the existing small deterministic helpers and compose through `run_concise.py` where applicable. Preserve disabled-mode behavior, persisted schema compatibility and locally edited installed copies. Add a behavior-changing policy only behind an explicit tested option. Do not add a framework, a paid model call or a global setting merely to satisfy this report. If current code already satisfies a proposed invariant, keep it and add the missing regression evidence instead of duplicating the mechanism.

## Limits and unresolved verification

- Actual user service maps and real repair-model execution remain untested. The task must retain explicit permission requirements.
- No paid model benchmark, Windows live execution or independent maximum-model code review was performed during this research. Those are distinct future acceptance activities where applicable.

## Task handoff

Task **062** now implements this recommendation; task **063** reviews the resulting code and requires corrections before acceptance. Read this report, its JSON decision record and only the assigned source paths. Do not repeat broad research unless a material version mismatch invalidates a specific finding. No second plan is required.
