---
task_id: "125"
status: "pending"
requirements: "R067,R068"
dependencies: "124,108,110"
allowed_related_task_reads: "none"
---

# 125 — Implement visual usability accessibility and responsive quality gates with pae ux CLI

Objective: Implement visual usability accessibility and responsive quality gates with pae ux CLI. Read P065 architecture, 124/108/110 accepted receipts and only real changed UI source.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Inspect scoped source architecture — Read P065 architecture, 124/108/110 accepted receipts and only real changed UI source.
- [ ] **S002** Implement or genuinely review contract — Wire pae ux fixed-script CLI init/extract/prototype/import/audit/sync-plan/validate/status; preserve legacy argv and disabled behavior.
- [ ] **S003** Enforce consent/source-of-truth/safety — Implement stable scoped screenshots with current code SHA, viewport/theme, approved golden and sanitized artifact; never auto-approve changed baseline.
- [ ] **S004** Run adversarial validation — Validate actual interactions, focus/keyboard, WCAG2.2AA target/contrast/labels, responsive and empty/loading/error states; screenshot alone never passes.
- [ ] **S005** Record actual acceptance evidence — Provide NN/g heuristic and qualified visual review with user approval/privacy; distinguish human feedback from model speculation and axe automatic tests.
- [ ] **S006** Close current-source final check — Run focused component/visual/a11y checks per 111 and 109; global suites remain 082/084; no compulsory performance benchmark.

## Scope

In: Implement visual usability accessibility and responsive quality gates with pae ux CLI
Out: No automatic production frontend edits, unrelated test changes, second plan or paid agent use.
Files: `skill/plan-and-execute/scripts/ux_review.py`, `skill/plan-and-execute/scripts/uxctl.py`, `skill/plan-and-execute/references/UI_UX_VALIDATION.md`, `bin/plan-and-execute.js`, `test/optimization/ux_visual_acceptance_self_test.py`, `test/cli.test.js`, `docs/research/20261028-skill-optimization/implementation/125-receipt.json`, `docs/research/20261028-skill-optimization/implementation/125-outcome.md`

## Guidance

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

## Acceptance

- Screenshot matching with keyboard trap or missing label fails.
- Visual changes need explicit baseline review, with reproducible artifacts and redaction.
- No browser/model on non-UI task or endless E2E matrix, no invented user testing.
- Existing CLI remains compatible and performance/security review enforced.
- No recurring UX external study or model calls after setup; explicit refresh and one-time opt-in work with durable project state.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_125`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_125`
