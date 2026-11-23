---
task_id: "082"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "strong"
reasoning_effort: "high"
complexity: "high"
requirements: "R001, R003, R004, R005, R041, R042, R043, R044, R046, R047, R048, R049, R050, R051, R052, R053, R054, R055, R056, R057, R058, R059, R060, R061, R062, R063, R064, R065, R066, R067, R068, R069, R070, R071, R072, R073"
dependencies: "003, 005, 007, 009, 011, 013, 015, 017, 019, 021, 023, 025, 027, 029, 031, 033, 035, 037, 039, 041, 043, 045, 047, 049, 051, 053, 055, 057, 059, 061, 063, 065, 067, 069, 071, 073, 075, 077, 079, 081, 088, 090, 092, 094, 096, 098, 100, 102, 104, 106, 108, 110, 114, 116, 118, 120, 122, 124, 126, 128, 130, 112, 131, 132"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 082 — Integrate all implemented contracts and close cross-feature gaps

## Objective

Integrate the implemented recommendations into one coherent product; create no further plan.

## Requirements covered

- R001
- R003
- R004
- R005
- R041
- R042
- R043
- R044
- R046
- R047
- R048
- R049
- R050
- R051
- R052
- R053
- R054
- R055
- R056
- R057
- R058
- R059
- R060
- R061
- R062
- R063
- R064
- R065
- R066
- R067
- R068
- R069
- R070
- R071
- R072
- R073

## Complexity and atomicity

- Complexity: **high**
- Why this is one executable TODO: One bounded implementation contract with its regression tests; source coupling requires a shared acceptance boundary, not an arbitrary file-count split.

## Context-isolation boundary

- Why one fresh worker context helps this whole TODO: This task owns one behavior or correction gate with independently checkable outcomes.
- Context that is genuinely shared by all subtasks:
- Read only the assigned decision, source targets and accepted prerequisite receipts.
- Concerns deliberately isolated into other TODOs:
- Do not load unrelated reports, provider guides or historical conversation transcripts.

## Isolation contract

This task definition and the exact execution-context files listed below are the only planning artifacts assigned to this worker. Read the task definition first, then read every assigned context file. Do not discover or open any other context file, `PLAN.md`, `TODO.md`, `manifest.json`, `orchestrator.config.json`, result files, logs, or unrelated task definitions. You may read repository source, tests, build files, and runtime output relevant to this task.

Another task definition may be opened only when one of the explicitly allowed task ids above is necessary to resolve a blocked dependency, ambiguity, or validation conflict. Record the task id and reason in the completion report.

## Assigned execution context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Assigned validated learnings

- None

These files are concise, immutable artifacts produced only after another TODO passed deterministic validation. Read exactly the assigned files, never a previous worker transcript or an unassigned learning file.

## Resumable subtask checklist

- [ ] **S001** — Read assigned decision and pin baseline
  - Read docs/research/20261028-skill-optimization/prepared-research/ARCHITECTURE_AND_SCOPE.md, docs/plans/20261028-skill-optimization/IMPLEMENTATION_INTEGRATION.md. Confirm source applicability; do not repeat broad research.
- [ ] **S002** — Implement change 1
  - Check integration against every prepared decision and original provider-switch acceptance case; do not create another plan.
- [ ] **S003** — Implement change 2
  - Correct regressions and report exact test commands, logs, package manifests and unsupported platforms.
- [ ] **S004** — Implement change 3
  - Preserve implementation and research evidence; do not install, commit, push or publish without permission.
- [ ] **S005** — Run declared regression checks
  - Run the declared targeted tests through the resource watcher. Implement every assigned acceptance case and preserve failures and limitations.
- [ ] **S006** — Check current integration versus historical receipts
  - Verify historical receipt integrity, re-run affected contracts on the current source state, and report any reopened owner tasks. Do not relabel old tests as current passes.
- [ ] **S007** — Record acceptance evidence
  - Write the implementation receipt and outcome report with changed-file hashes, acceptance coverage and actual test logs. Leave unresolved work pending.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Integrate all implemented contracts and close cross-feature gaps

## Out of scope

- No new broad research phase or second-plan generation.
- Do not change installed copies, user-global settings or publish without permission.

## Expected files

- README.md
- README.pt-BR.md
- CHANGELOG.md
- tools/run-repo-checks.js
- tools/run-skill-self-test.js
- test/optimization/integration_082_self_test.py
- docs/research/20261028-skill-optimization/implementation/082-receipt.json
- docs/research/20261028-skill-optimization/implementation/082-outcome.md

## Dependencies

- 003
- 005
- 007
- 009
- 011
- 013
- 015
- 017
- 019
- 021
- 023
- 025
- 027
- 029
- 031
- 033
- 035
- 037
- 039
- 041
- 043
- 045
- 047
- 049
- 051
- 053
- 055
- 057
- 059
- 061
- 063
- 065
- 067
- 069
- 071
- 073
- 075
- 077
- 079
- 081
- 088
- 090
- 092
- 094
- 096
- 098
- 100
- 102
- 104
- 106
- 108
- 110
- 114
- 116
- 118
- 120
- 122
- 124
- 126
- 128
- 130
- 112
- 131
- 132

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/research/20261028-skill-optimization/prepared-research/ARCHITECTURE_AND_SCOPE.md and docs/plans/20261028-skill-optimization/IMPLEMENTATION_INTEGRATION.md.
- Use only task 082 inputs, declared checks and write scope in TASK_INPUTS.json; write evidence to docs/research/20261028-skill-optimization/implementation/082-receipt.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- If integration exposes a defect outside this write scope, reopen its owning TODO and correction review with native controllers; do not silently expand scope.
- Keep historical receipt integrity separate from current source/command/map validation. Every changed implementation and correction gate needs actual acceptance evidence; prepared research never counts as a pass.
- Integrate all six feature pairs from docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261031.md; require actual independent review receipts.
- Integrate verified P053 101/102 host sleep guard and tests across providers, OS backends, WSL, long validation and strict preflight.
- Integrate P054 timer cleanup, P055 L6 model routing and P067 manager-tier delegation after genuine independent reviews 104/106/132.
- Require genuine 112 impact-selection and 114 audit/refactor reviews; mapped source-specific suites gate tasks and the full global suite runs at the final plan revision, again after later fixes.
- Integrate independently reviewed 115-120 quota restoration/resume, oracle-strength tests and every-task lazy routing without losing global final suite.
- Integrate actual independently reviewed P065 tasks 121-126, source-of-truth design memory, optional prototype lab and accessible UX validation without lost final-suite gate.
- P066: integrate reviewed 128/130 standards and 121's shared first-use UX state; validate ORM/JDBC drift and justified exceptions; document CLI in README.md, README.pt-BR.md and --help only after implementation.

## Acceptance criteria

- All implementation acceptance cases and required independent code reviews have current evidence.
- Final npm checks and actual package file lists pass or the task remains incomplete.
- The Portuguese final report distinguishes verified behavior, untested platforms and live-provider limitations.
- Current integration evidence covers changed contracts; historical task receipts remain immutable evidence of their recorded revisions.
- All six added feature contracts have independently reviewed current-tree evidence.
- P052 semantic five-minute stall diagnosis, reliable progress percentages and authorized higher-capability repair have actual independently reviewed mapped integration evidence.
- P053 OS lease and release tests, accurate supported-host caveats and independent acceptance are evidenced.
- New reviewed 103/104 twenty-minute timer, 105/106 sixth frontier-tier and 131/132 manager-tier delegation work have actual acceptance evidence.
- Task 107 design-security/performance and final-code-review lenses are implemented and independently reviewed by 108 with no default benchmarks.
- P057 109/110 real implementation and independent review prove full-safe failure inventory, targeted fix cycles and mandatory final full-suite gate.
- Complete global unit/contract/integration/E2E suite passes at plan closure on final source; opt-in review authorization is proven.
- All quota, test-oracle and lazy-context requirements have current executable negative tests and genuine review evidence.
- P065 identity, guarded lab import/sync and accessible visual/keyboard check contracts have real 122/124/126 review evidence and current integration tests.
- P066 commands, ORM drift checks, agent docs and UX first-use contract function with end-to-end test evidence.
- tools/run-repo-checks.js runs every test/optimization/*_self_test.py from tasks 068-132, and integration_082_self_test.py proves it.
- The prepared report is input evidence, not proof that this implementation or its independent review has passed.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_082`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_082`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
