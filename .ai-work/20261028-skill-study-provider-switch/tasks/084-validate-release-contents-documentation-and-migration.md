---
task_id: "084"
status: "pending"
requirements: "R001,R003,R004,R005,R033,R034,R039,R041,R042,R043,R044"
dependencies: "083"
allowed_related_task_reads: "none"
---

# 084 — Validate release contents, documentation and migration

Objective: Finish release-readiness in this same plan: verify packages, compatibility and user-facing documentation.

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

In: Validate release contents, documentation and migration
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `README.md`, `README.pt-BR.md`, `CHANGELOG.md`, `tools/run-repo-checks.js`, `docs/research/20261028-skill-optimization/implementation/084-receipt.json`, `docs/research/20261028-skill-optimization/implementation/084-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/ARCHITECTURE_AND_SCOPE.md.
- Read docs/plans/20261028-skill-optimization/IMPLEMENTATION_INTEGRATION.md.
- Use only task 084 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/084-receipt.json.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- If integration exposes a defect outside this write scope, reopen its owning TODO and correction review with native controllers; do not silently expand scope.

## Acceptance

- All implementation acceptance cases and required independent code reviews have current evidence.
- Final npm checks and actual package file lists pass or the task remains incomplete.
- The Portuguese final report distinguishes verified behavior, untested platforms and live-provider limitations.
- The prepared report is input evidence, not proof that this implementation or its independent review has passed.
- Current integration evidence covers changed contracts; historical task receipts remain immutable evidence of their recorded revisions.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_084`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_084`
