---
task_id: "076"
status: "pending"
requirements: "R006,R017,R018,R019,R020,R021,R023,R029,R034"
dependencies: "061,075"
allowed_related_task_reads: "none"
---

# 076 — Implement bounded deterministic handoff and sanitation

Objective: Implement the assigned provider-switch contract from report068 and the original twelve-case acceptance matrix.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned decision and pin baseline — Read docs/research/20261028-skill-optimization/prepared-research/068-provider-switch-handoff.md, docs/plans/20261028-skill-optimization/ACCEPTANCE_MATRIX.md. Confirm source applicability; do not repeat broad research.
- [ ] **S002** Implement change 1 — Validate paths, command evidence and subtask IDs; sanitize before byte-bounded truncation.
- [ ] **S003** Implement change 2 — Missing prior reports use deterministic evidence; no extra model call or transcript retention by default.
- [ ] **S004** Implement change 3 — Add regression tests for the corresponding original acceptance cases and preserve legacy behavior.
- [ ] **S005** Apply revised runtime contract 1 — Build a deterministic capsule from checked evidence; redact secrets before truncation and bound serialized UTF-8 bytes.
- [ ] **S006** Apply revised runtime contract 2 — Bind the capsule to source state, destination and next attempt; stale, missing or malformed evidence cannot approve or redirect execution.
- [ ] **S007** Apply revised runtime contract 3 — Keep previous-worker hypotheses unverified; additional paid summarization and native transcript retention remain disabled by default.
- [ ] **S008** Run declared regression checks — Run the declared targeted tests through the resource watcher. Implement every assigned acceptance case and preserve failures and limitations.
- [ ] **S009** Record acceptance evidence — Write the implementation receipt and outcome report with changed-file hashes, acceptance coverage and actual test logs. Leave unresolved work pending.

## Scope

In: Implement bounded deterministic handoff and sanitation
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/assistant_triage.py`, `skill/plan-and-execute/scripts/run_isolated.py`, `test/optimization/provider_switch_076_self_test.py`, `skill/plan-and-execute/scripts/provider_handoff.py`, `docs/research/20261028-skill-optimization/implementation/076-receipt.json`, `docs/research/20261028-skill-optimization/implementation/076-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/068-provider-switch-handoff.md.
- Read docs/plans/20261028-skill-optimization/ACCEPTANCE_MATRIX.md.
- Use only task 076 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/076-receipt.json.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Use the normative blueprint in report068 for exact entry-rung, repeat, reset, byte-bound and budget semantics; record deviations before changing that contract.

## Acceptance

- Validate paths, command evidence and subtask IDs; sanitize before byte-bounded truncation.
- Missing prior reports use deterministic evidence; no extra model call or transcript retention by default.
- The targeted contract is validated through the production run_concise composition.
- The prepared report is input evidence, not proof that this implementation or its independent review has passed.
- Build a deterministic capsule from checked evidence; redact secrets before truncation and bound serialized UTF-8 bytes.
- Bind the capsule to source state, destination and next attempt; stale, missing or malformed evidence cannot approve or redirect execution.
- Keep previous-worker hypotheses unverified; additional paid summarization and native transcript retention remain disabled by default.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_076`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_076`
