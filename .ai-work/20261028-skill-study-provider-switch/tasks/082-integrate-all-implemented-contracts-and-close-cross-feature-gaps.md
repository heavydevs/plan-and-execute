---
task_id: "082"
status: "pending"
requirements: "R001,R003,R004,R005,R041,R042,R043,R044"
dependencies: "003,005,007,009,011,013,015,017,019,021,023,025,027,029,031,033,035,037,039,041,043,045,047,049,051,053,055,057,059,061,063,065,067,069,071,073,075,077,079,081"
allowed_related_task_reads: "none"
---

# 082 — Integrate all implemented contracts and close cross-feature gaps

Objective: Integrate the implemented recommendations into one coherent product; create no further plan.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned decision and pin baseline — Read docs/research/20261028-skill-optimization/prepared-research/ARCHITECTURE_AND_SCOPE.md, docs/plans/20261028-skill-optimization/IMPLEMENTATION_INTEGRATION.md. Confirm source applicability; do not repeat broad research.
- [ ] **S002** Implement change 1 — Check integration against every prepared decision and original provider-switch acceptance case; do not create another plan.
- [ ] **S003** Implement change 2 — Correct regressions and report exact test commands, logs, package manifests and unsupported platforms.
- [ ] **S004** Implement change 3 — Preserve implementation and research evidence; do not install, commit, push or publish without permission.
- [ ] **S005** Run declared regression checks — Run the declared targeted tests through the resource watcher. Implement every assigned acceptance case and preserve failures and limitations.
- [ ] **S006** Check current integration versus historical receipts — Verify historical receipt integrity, re-run affected contracts on the current source state, and report any reopened owner tasks. Do not relabel old tests as current passes.
- [ ] **S007** Record acceptance evidence — Write the implementation receipt and outcome report with changed-file hashes, acceptance coverage and actual test logs. Leave unresolved work pending.

## Scope

In: Integrate all implemented contracts and close cross-feature gaps
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `README.md`, `README.pt-BR.md`, `CHANGELOG.md`, `tools/run-repo-checks.js`, `tools/run-skill-self-test.js`, `test/optimization/integration_082_self_test.py`, `docs/research/20261028-skill-optimization/implementation/082-receipt.json`, `docs/research/20261028-skill-optimization/implementation/082-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/ARCHITECTURE_AND_SCOPE.md.
- Read docs/plans/20261028-skill-optimization/IMPLEMENTATION_INTEGRATION.md.
- Use only task 082 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/082-receipt.json.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- If integration exposes a defect outside this write scope, reopen its owning TODO and correction review with native controllers; do not silently expand scope.
- Keep historical receipt integrity separate from current source/command/map validation.
- Every changed implementation and correction gate needs actual acceptance evidence; prepared research never counts as a pass.

## Acceptance

- All implementation acceptance cases and required independent code reviews have current evidence.
- Final npm checks and actual package file lists pass or the task remains incomplete.
- The Portuguese final report distinguishes verified behavior, untested platforms and live-provider limitations.
- The prepared report is input evidence, not proof that this implementation or its independent review has passed.
- Current integration evidence covers changed contracts; historical task receipts remain immutable evidence of their recorded revisions.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_082`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_082`
