---
task_id: "097"
status: "pending"
requirements: "R051"
dependencies: "007,029,061,063,067"
allowed_related_task_reads: "none"
---

# 097 — Implement make console, progress and end-user docs concise and precise

Objective: Reduce redundant user-facing AI outputs, status messages and manuals while retaining correctness, exact technical detail, clear actions and user-selectable depth.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read evidence — Read docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261031.md, assigned prepared research and materially affected source files.
- [ ] **S002** Implement contract 1 — Define answer-first, literal, specific adult-professional language; do not confuse autism with reduced intelligence or uniform preferences.
- [ ] **S003** Implement contract 2 — Cut greetings, repeated recaps, filler, generic praise, unasked tangents and redundant progress without omitting important decisions.
- [ ] **S004** Implement contract 3 — Separate concise human output from full machine-readable JSON, diagnostics and logs; expose details/verbose on request.
- [ ] **S005** Implement contract 4 — Measure output tokens and repeated-text rate together with accuracy, necessary caveats, actionability, accessibility and actual human comprehension.
- [ ] **S006** Run tests — Implement test/optimization/concise_communication_self_test.py and run mapped validation plus feature negative cases.
- [ ] **S007** Record implementation — Record real implementation and test evidence in docs/research/20261028-skill-optimization/implementation/097-receipt.json and docs/research/20261028-skill-optimization/implementation/097-outcome.md.

## Scope

In: Reduce redundant user-facing AI outputs, status messages and manuals while retaining correctness, exact technical detail, clear actions and user-selectable depth.
Out: No second plan or unrelated changes.; No installation, provider login, publishing or user-global configuration changes without permission.
Files: `skill/plan-and-execute/references/USER_COMMUNICATION.md`, `skill/plan-and-execute/references/TOKEN_EFFICIENCY.md`, `skill/plan-and-execute/references/ARTIFACT_WRITING.md`, `skill/plan-and-execute/scripts/process_io.py`, `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/references/INSTALLATION.md`, `skill/plan-and-execute/references/INSTALLATION.pt-BR.md`, `skill/validate-or-fix/references/OPERATIONS.md`, `test/optimization/concise_communication_self_test.py`, `test/optimization/concise_communication_self_test.py`, `docs/research/20261028-skill-optimization/implementation/097-receipt.json`, `docs/research/20261028-skill-optimization/implementation/097-outcome.md`

## Guidance

- Read docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261031.md.
- Follow task 097 in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Preserve exact user intent, bounded context, security floors and real deterministic tests.
- Refresh only materially changed facts from assigned prepared reports 006, 028, 060, 062.
- Preserve evidence in docs/research/20261028-skill-optimization/implementation/097-receipt.json and docs/research/20261028-skill-optimization/implementation/097-outcome.md; do not mark a pending task done without validation.

## Acceptance

- A one-step command returns the result and necessary next action, not a verbose status essay.
- Technical answers lead with a precise answer and retain commands, constraints, risk and error explanation when material.
- Do not restate earlier concepts unless necessary for the present decision, apparent confusion or explicit user request.
- User-facing bytes/tokens fall without losing correct steps, safety warnings, machine output or diagnostic evidence.
- The tone respects adult autistic users, avoids overgeneralization and supports individual preference and detail expansion.
- Independent test and human feedback verify non-inferior comprehension, accuracy and completeness, not word count alone.
- Implementation and review remain pending until actual execution evidence exists.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_097`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_097`
