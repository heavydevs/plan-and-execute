---
task_id: "126"
status: "pending"
requirements: "R065,R066,R067,R068"
dependencies: "125"
allowed_related_task_reads: "none"
---

# 126 — Independently review full UI/UX quality, consent, economy and integration

**Objective:** Independently review full UI/UX quality, consent, economy and integration. Read P065 report, 125 final source/receipt and minimal accepted 122/124 review metadata.

**Pre-decided architecture:** docs/research/20261028-skill-optimization/prepared-research/121-uiux-design-prototype-research.md. Implement these decisions without a new broad research phase. All functionality and reviews are PENDING.

## Internal implementation checklist
- [ ] **S001** — Read P065 report, 125 final source/receipt and minimal accepted 122/124 review metadata.
- [ ] **S002** — Dispatch real fresh max-qualified independent review for visual craft, security, performance, accessibility and privacy.
- [ ] **S003** — Test all P065 negative A–P cases, especially keyboard vs screenshot, skipped browser, stale prototype, consent and token context budget.
- [ ] **S004** — Fix owned defects or reopen source owner, rerun selected current tests; retain global validation gate 082.
- [ ] **S005** — Record real reviewer session/effort/model/final hash/cost and any unsupported environments; remain pending without evidence.

## Design and execution constraints
- Read docs/research/20261028-skill-optimization/prepared-research/121-uiux-design-prototype-research.md only while implementing task 126 and examine only current affected source/dependency receipts.
- Read P065 report, 125 final source/receipt and minimal accepted 122/124 review metadata.
- Dispatch real fresh max-qualified independent review for visual craft, security, performance, accessibility and privacy.
- Test all P065 negative A–P cases, especially keyboard vs screenshot, skipped browser, stale prototype, consent and token context budget.
- Fix owned defects or reopen source owner, rerun selected current tests; retain global validation gate 082.
- Record real reviewer session/effort/model/final hash/cost and any unsupported environments; remain pending without evidence.
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
- [ ] Genuine final-hash review approves visual, functional and accessible UI behavior together.
- [ ] No unauthorized real frontend edits, paid visual calls, lost global gate or unrelated UX loads.
- [ ] 126 genuinely gates integration 082; only measured savings can be claimed.

Cross-check applicable negative cases A–P and provenance in P065 research. Screenshot matching never overrides keyboard/functional failures; unsupported tool is not a green run.

## Validation (only after code)
- python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_126
- python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_126

No real code, independent review, paid agent or browser validation has run in this planning task.
