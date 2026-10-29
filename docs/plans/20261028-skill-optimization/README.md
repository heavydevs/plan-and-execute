# One implementation plan - prepared research

Date: 2026-10-28. Product baseline: 0.11.0. Remote checkpoint before this revision:
`checkpoint/plano1-estudo-provider-switch-20261028` at `d4fc2ae44fd502ac59340fce8e24ce8a55673ebe`.

**Research prepared: 32 topic reports, 58 primary-source records. Product implementation has not started.**
The current user amendment replaces research execution and second-plan generation with one implementation graph. `PLAN1_SPEC.json` keeps its filename for compatibility, not because a second plan remains.

## Entry points

- [Prepared research index](../../research/20261028-skill-optimization/prepared-research/INDEX.md): one decision report per former research task.
- [Current protocol](PROTOCOL.md): scoped context, real acceptance and protection boundaries.
- [Native TODO checklist](../../../.ai-work/20261028-skill-study-provider-switch/TODO.md): 86 implementation, correction and review tasks, all pending.
- [Request amendment](REQUEST_AMENDMENT.md) and [traceability](REPLAN_TRACE.json): explicit supersession of the former two-plan request.
- [Original provider-switch acceptance matrix](ACCEPTANCE_MATRIX.md): all twelve cases remain obligations.
- [Portability](PORTABILITY.md): native recreation on another host; no status editing.

## Task layout

| IDs | Implementation outcome |
|---|---|
| 001-005 | Offline preflight, source coverage and common acceptance fixtures, with correction gates. |
| 006-069 | 32 topic implementations, each followed by independent code review and correction. |
| 070-081 | Provider-switch configuration, effective dispatch, availability/budget, handoff and integration, each reviewed. |
| 082-085 | Cross-topic integration, regression, package contents and release-readiness correction. |
| 086 | Final whole-skill maintenance review and evidence-based handoff. |

There are 43 real independent review requirements and 571 internal checkpoints. They have not been executed. The former maximum-model review before all other work has been replaced by deterministic preflight; maximum-capability reviews now accept concrete implementations instead of blocking all preparation.

## Efficient task loading

Run from the repository root:

```bash
python docs/plans/20261028-skill-optimization/support/check_delivery.py --inputs 006
```

Read only this task's assigned report, applicable source symbols, dependencies and current tests. Do not load all 32 reports or the historical snapshot. Every former research task starts with a link to its report and has numbered implementation subtasks and proposed acceptance tests. Source URLs, access dates, reading scope and uncertainty are preserved in the source register.

## Evidence boundary

The research recommends changes; it does not prove that code implements them. No paid model calls, live provider experiment, Windows run or independent maximum-model review was performed in research preparation. Public author book excerpts and open chapters are explicitly scoped; full-book reading is not claimed. No universal cheapest/strongest model or measured savings percentage is asserted.

The product directories `skill/`, `bin/` and `lib/` remain unchanged from 0.11.0. The modified Python support scripts under this document directory validate the plan and future receipts; they are not implementations of the proposed runtime improvements.

The former specification, protocol and native control state are preserved in `history/pre-research-conversion/` as inactive historical evidence. No historical plan is activated. Do not resume that snapshot. All new implementation tasks remain pending, and autostart stays false.
