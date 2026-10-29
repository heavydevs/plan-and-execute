---
task_id: "070"
status: "pending"
requirements: "R006,R012,R013,R014,R015,R016,R017,R024,R025,R026,R027,R028,R030,R031,R037"
dependencies: "025,047,069"
allowed_related_task_reads: "none"
---

# 070 — Implement opt-in provider-switch configuration and migration

Objective: Implement the assigned provider-switch contract from report068 and the original twelve-case acceptance matrix.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned decision and pin baseline — Read docs/research/20261028-skill-optimization/prepared-research/068-provider-switch-handoff.md, docs/plans/20261028-skill-optimization/ACCEPTANCE_MATRIX.md. Confirm source applicability; do not repeat broad research.
- [ ] **S002** Implement change 1 — Strict mode/subkey validation and fingerprints; legacy default stays unchanged.
- [ ] **S003** Implement change 2 — Version1 full snapshots do not inherit global options; schema1-4 remain readable.
- [ ] **S004** Implement change 3 — Add regression tests for the corresponding original acceptance cases and preserve legacy behavior.
- [ ] **S005** Apply revised runtime contract 1 — Strictly validate provider_switch.mode and handoff subkeys; default legacy mode keeps previous behavior.
- [ ] **S006** Apply revised runtime contract 2 — Fingerprint every route-affecting option; full version1 config snapshots do not inherit new global settings.
- [ ] **S007** Run declared regression checks — Run the declared targeted tests through the resource watcher. Implement every assigned acceptance case and preserve failures and limitations.
- [ ] **S008** Record acceptance evidence — Write the implementation receipt and outcome report with changed-file hashes, acceptance coverage and actual test logs. Leave unresolved work pending.

## Scope

In: Implement opt-in provider-switch configuration and migration
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/routing_config.py`, `skill/plan-and-execute/scripts/configure.py`, `test/optimization/provider_switch_070_self_test.py`, `skill/plan-and-execute/references/ROUTING_CONFIG.md`, `skill/plan-and-execute/scripts/availability.py`, `docs/research/20261028-skill-optimization/implementation/070-receipt.json`, `docs/research/20261028-skill-optimization/implementation/070-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/068-provider-switch-handoff.md.
- Read docs/plans/20261028-skill-optimization/ACCEPTANCE_MATRIX.md.
- Use only task 070 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/070-receipt.json.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Use the normative blueprint in report068 for exact entry-rung, repeat, reset, byte-bound and budget semantics; record deviations before changing that contract.

## Acceptance

- Strict mode/subkey validation and fingerprints; legacy default stays unchanged.
- Version1 full snapshots do not inherit global options; schema1-4 remain readable.
- The targeted contract is validated through the production run_concise composition.
- The prepared report is input evidence, not proof that this implementation or its independent review has passed.
- Strictly validate provider_switch.mode and handoff subkeys; default legacy mode keeps previous behavior.
- Fingerprint every route-affecting option; full version1 config snapshots do not inherit new global settings.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_070`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_070`
