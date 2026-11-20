---
task_id: "125"
status: "pending"
requirements: "R067,R068"
dependencies: "124,108,110"
allowed_related_task_reads: "none"
---

# 125 — Implement visual usability accessibility and responsive quality gates with pae ux CLI

**Objective:** Implement visual usability accessibility and responsive quality gates with pae ux CLI. Read P065 architecture, 124/108/110 accepted receipts and only real changed UI source.

**Pre-decided architecture:** docs/research/20261028-skill-optimization/prepared-research/121-uiux-design-prototype-research.md. Implement these decisions without a new broad research phase. All functionality and reviews are PENDING.

## Internal implementation checklist
- [ ] **S001** — Read P065 architecture, 124/108/110 accepted receipts and only real changed UI source.
- [ ] **S002** — Wire pae ux fixed-script CLI init/extract/prototype/import/audit/sync-plan/validate/status; preserve legacy argv and disabled behavior.
- [ ] **S003** — Implement stable scoped screenshots with current code SHA, viewport/theme, approved golden and sanitized artifact; never auto-approve changed baseline.
- [ ] **S004** — Validate actual interactions, focus/keyboard, WCAG2.2AA target/contrast/labels, responsive and empty/loading/error states; screenshot alone never passes.
- [ ] **S005** — Provide NN/g heuristic and qualified visual review with user approval/privacy; distinguish human feedback from model speculation and axe automatic tests.
- [ ] **S006** — Run focused component/visual/a11y checks per 111 and 109; global suites remain 082/084; no compulsory performance benchmark.

**P066 UX gate amendment:** P066 ONE-TIME PROJECT ONBOARDING: Shared durable per-project coding/UX opt-in in task 127/128. Broad project/UI/design analysis and contemporary external research happen ONLY at first relevant approved use or explicit pae ux init/refresh; later tasks use compact module-scoped approved source-indexed design patterns without re-running research. Backend-only, declined, CI and trivial commands have zero UX activation. Independent UX prototype opt-in remains separate. No unapproved overwrite, paid model, network or source changes.

## Design and execution constraints
- Read docs/research/20261028-skill-optimization/prepared-research/121-uiux-design-prototype-research.md only while implementing task 125 and examine only current affected source/dependency receipts.
- Read P065 architecture, 124/108/110 accepted receipts and only real changed UI source.
- Wire pae ux fixed-script CLI init/extract/prototype/import/audit/sync-plan/validate/status; preserve legacy argv and disabled behavior.
- Implement stable scoped screenshots with current code SHA, viewport/theme, approved golden and sanitized artifact; never auto-approve changed baseline.
- Validate actual interactions, focus/keyboard, WCAG2.2AA target/contrast/labels, responsive and empty/loading/error states; screenshot alone never passes.
- Provide NN/g heuristic and qualified visual review with user approval/privacy; distinguish human feedback from model speculation and axe automatic tests.
- Run focused component/visual/a11y checks per 111 and 109; global suites remain 082/084; no compulsory performance benchmark.
- Reuse routingctl, task_context_router, planctl, existing validators and P056 security/performance gates; no parallel orchestration.
- Produce real source hashes/test results and genuine independent review where required; never call prepared research executed implementation.

## Exact write ownership
- skill/plan-and-execute/scripts/ux_review.py
- skill/plan-and-execute/scripts/uxctl.py
- skill/plan-and-execute/references/UI_UX_VALIDATION.md
- bin/plan-and-execute.js
- test/optimization/ux_visual_acceptance_self_test.py
- test/cli.test.js

## Testable acceptance
- [ ] Screenshot matching with keyboard trap or missing label fails.
- [ ] Visual changes need explicit baseline review, with reproducible artifacts and redaction.
- [ ] No browser/model on non-UI task or endless E2E matrix, no invented user testing.
- [ ] Existing CLI remains compatible and performance/security review enforced.

Cross-check applicable negative cases A–P and provenance in P065 research. Screenshot matching never overrides keyboard/functional failures; unsupported tool is not a green run.

## Validation (only after code)
- python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_125
- python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_125

No real code, independent review, paid agent or browser validation has run in this planning task.
