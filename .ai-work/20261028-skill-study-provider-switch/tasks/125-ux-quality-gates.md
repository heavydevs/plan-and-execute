---
task_id: "125"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "strong"
reasoning_effort: "high"
complexity: "high"
requirements: "R067, R068"
dependencies: "124, 108, 110"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 125 — Implement visual usability accessibility and responsive quality gates with pae ux CLI

## Objective

Implement visual usability accessibility and responsive quality gates with pae ux CLI. Read P065 architecture, 124/108/110 accepted receipts and only real changed UI source.

## Requirements covered

- R067
- R068

## Complexity and atomicity

- Complexity: **high**
- Why this is one executable TODO: One bounded implementation change or independent final-hash correction gate.

## Context-isolation boundary

- Why one fresh worker context helps this whole TODO: Single independently verifiable UI/UX capability contract.
- Context that is genuinely shared by all subtasks:
- Read only P065 report, affected source symbols and accepted dependency evidence.
- Concerns deliberately isolated into other TODOs:
- Do not read unrelated tasks, full style inventories, private screenshots or old logs.

## Isolation contract

This task definition and the exact execution-context files listed below are the only planning artifacts assigned to this worker. Read the task definition first, then read every assigned context file. Do not discover or open any other context file, `PLAN.md`, `TODO.md`, `manifest.json`, `orchestrator.config.json`, result files, logs, or unrelated task definitions. You may read repository source, tests, build files, and runtime output relevant to this task.

Another task definition may be opened only when one of the explicitly allowed task ids above is necessary to resolve a blocked dependency, ambiguity, or validation conflict. Record the task id and reason in the completion report.

## Assigned execution context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Assigned validated learnings

- None

These files are concise, immutable artifacts produced only after another TODO passed deterministic validation. Read exactly the assigned files, never a previous worker transcript or an unassigned learning file.

## Resumable subtask checklist

- [ ] **S001** — Inspect scoped source architecture
  - Read P065 architecture, 124/108/110 accepted receipts and only real changed UI source.
- [ ] **S002** — Implement or genuinely review contract
  - Wire pae ux fixed-script CLI init/extract/prototype/import/audit/sync-plan/validate/status; preserve legacy argv and disabled behavior.
- [ ] **S003** — Enforce consent/source-of-truth/safety
  - Implement stable scoped screenshots with current code SHA, viewport/theme, approved golden and sanitized artifact; never auto-approve changed baseline.
- [ ] **S004** — Run adversarial validation
  - Validate actual interactions, focus/keyboard, WCAG2.2AA target/contrast/labels, responsive and empty/loading/error states; screenshot alone never passes.
- [ ] **S005** — Record actual acceptance evidence
  - Provide NN/g heuristic and qualified visual review with user approval/privacy; distinguish human feedback from model speculation and axe automatic tests.
- [ ] **S006** — Close current-source final check
  - Run focused component/visual/a11y checks per 111 and 109; global suites remain 082/084; no compulsory performance benchmark.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Implement visual usability accessibility and responsive quality gates with pae ux CLI

## Out of scope

- No automatic production frontend edits, unrelated test changes, second plan or paid agent use.

## Expected files

- skill/plan-and-execute/scripts/ux_review.py
- skill/plan-and-execute/scripts/uxctl.py
- skill/plan-and-execute/references/UI_UX_VALIDATION.md
- bin/plan-and-execute.js
- test/optimization/ux_visual_acceptance_self_test.py
- test/cli.test.js
- docs/research/20261028-skill-optimization/implementation/125-receipt.json
- docs/research/20261028-skill-optimization/implementation/125-outcome.md

## Dependencies

- 124
- 108
- 110

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/research/20261028-skill-optimization/prepared-research/121-uiux-design-prototype-research.md only while implementing task 125 and examine only current affected source/dependency receipts.
- Read P065 architecture, 124/108/110 accepted receipts and only real changed UI source.
- Wire pae ux fixed-script CLI init/extract/prototype/import/audit/sync-plan/validate/status; preserve legacy argv and disabled behavior.
- Implement stable scoped screenshots with current code SHA, viewport/theme, approved golden and sanitized artifact; never auto-approve changed baseline.
- Validate actual interactions, focus/keyboard, WCAG2.2AA target/contrast/labels, responsive and empty/loading/error states; screenshot alone never passes.
- Provide NN/g heuristic and qualified visual review with user approval/privacy; distinguish human feedback from model speculation and axe automatic tests.
- Run focused component/visual/a11y checks per 111 and 109; global suites remain 082/084; no compulsory performance benchmark.
- Reuse routingctl, task_context_router, planctl, existing validators and P056 security/performance gates; no parallel orchestration.
- Produce real source hashes/test results and genuine independent review where required; never call prepared research executed implementation.
- P066: broad UX study strictly on first approved relevant project use or explicit pae ux init/refresh. Shared coding+UX consent from 127/128; subsequent UX tasks load approved scoped design index only; no repeated research.
- Cross-check applicable negative cases A–P and provenance in P065 research; screenshot matching never overrides keyboard/functional failures; an unsupported tool is not a green run.

## Acceptance criteria

- Screenshot matching with keyboard trap or missing label fails.
- Visual changes need explicit baseline review, with reproducible artifacts and redaction.
- No browser/model on non-UI task or endless E2E matrix, no invented user testing.
- Existing CLI remains compatible and performance/security review enforced.
- No recurring UX external study or model calls after setup; explicit refresh and one-time opt-in work with durable project state.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_125`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_125`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
