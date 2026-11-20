---
task_id: "124"
status: "pending"
requirements: "R066,R068"
dependencies: "123"
allowed_related_task_reads: "none"
---

# 124 — Independently review prototype isolation and guarded production migration

**Objective:** Independently review prototype isolation and guarded production migration. Read only P065 report, final 123 source, tests and hashed receipt.

**Pre-decided architecture:** docs/research/20261028-skill-optimization/prepared-research/121-uiux-design-prototype-research.md. Implement these decisions without a new broad research phase. All functionality and reviews are PENDING.

## Internal implementation checklist
- [ ] **S001** — Read only P065 report, final 123 source, tests and hashed receipt.
- [ ] **S002** — Run real fresh max-qualified independent review of in-app/lab mode, security, performance, licensing and UX fidelity.
- [ ] **S003** — Test traversal, symlinks, credential leakage, unsafe npm, stale mapping and bypassing user consent.
- [ ] **S004** — Correct predecessor-owned source, rerun impacted checks, never rewrite unrelated application source.
- [ ] **S005** — Record genuine reviewer metadata and unresolved limits; no simulated approval.

## Design and execution constraints
- Read docs/research/20261028-skill-optimization/prepared-research/121-uiux-design-prototype-research.md only while implementing task 124 and examine only current affected source/dependency receipts.
- Read only P065 report, final 123 source, tests and hashed receipt.
- Run real fresh max-qualified independent review of in-app/lab mode, security, performance, licensing and UX fidelity.
- Test traversal, symlinks, credential leakage, unsafe npm, stale mapping and bypassing user consent.
- Correct predecessor-owned source, rerun impacted checks, never rewrite unrelated application source.
- Record genuine reviewer metadata and unresolved limits; no simulated approval.
- Reuse routingctl, task_context_router, planctl, existing validators and P056 security/performance gates; no parallel orchestration.
- Produce real source hashes/test results and genuine independent review where required; never call prepared research executed implementation.

## Exact write ownership
- skill/plan-and-execute/scripts/ux_prototype.py
- skill/plan-and-execute/scripts/uxctl.py
- skill/plan-and-execute/references/UI_UX_PROTOTYPING.md
- skill/plan-and-execute/assets/ux-lab-template/package.json
- skill/plan-and-execute/assets/ux-lab-template/index.html
- skill/plan-and-execute/assets/ux-lab-template/src/main.js
- skill/plan-and-execute/assets/ux-lab-template/src/styles/main.scss
- skill/plan-and-execute/assets/ux-lab-template/README.md
- test/optimization/ux_prototype_lab_self_test.py

## Testable acceptance
- [ ] Independent final-source review verifies no secret or production write leakage.
- [ ] Stale mapping and consent gate cannot be bypassed; critical findings fixed.

Cross-check applicable negative cases A–P and provenance in P065 research. Screenshot matching never overrides keyboard/functional failures; unsupported tool is not a green run.

## Validation (only after code)
- python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_124
- python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_124

No real code, independent review, paid agent or browser validation has run in this planning task.
