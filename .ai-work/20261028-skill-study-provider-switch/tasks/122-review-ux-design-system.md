---
task_id: "122"
status: "pending"
requirements: "R065,R068"
dependencies: "121"
allowed_related_task_reads: "none"
---

# 122 — Independently review visual identity, design token and agent context safety

**Objective:** Independently review visual identity, design token and agent context safety. Read only P065 report, final 121 source/receipt and its tests.

**Pre-decided architecture:** docs/research/20261028-skill-optimization/prepared-research/121-uiux-design-prototype-research.md. Implement these decisions without a new broad research phase. All functionality and reviews are PENDING.

## Internal implementation checklist
- [ ] **S001** — Read only P065 report, final 121 source/receipt and its tests.
- [ ] **S002** — Dispatch genuine independent fresh max-qualified reviewer, including visual, security/performance and privacy lenses.
- [ ] **S003** — Probe unsupported/no-consent, stale hash, invalid alias, unsafe path, prompt injection and unwanted rebrand.
- [ ] **S004** — Correct predecessor-owned source and rerun focused tests, require reviewer approval of final hashes.
- [ ] **S005** — Record actual provider/model/effort/session evidence; never mark synthetic review complete.

**P066 UX gate amendment:** P066 ONE-TIME PROJECT ONBOARDING: Shared durable per-project coding/UX opt-in in task 127/128. Broad project/UI/design analysis and contemporary external research happen ONLY at first relevant approved use or explicit pae ux init/refresh; later tasks use compact module-scoped approved source-indexed design patterns without re-running research. Backend-only, declined, CI and trivial commands have zero UX activation. Independent UX prototype opt-in remains separate. No unapproved overwrite, paid model, network or source changes.

## Design and execution constraints
- Read docs/research/20261028-skill-optimization/prepared-research/121-uiux-design-prototype-research.md only while implementing task 122 and examine only current affected source/dependency receipts.
- Read only P065 report, final 121 source/receipt and its tests.
- Dispatch genuine independent fresh max-qualified reviewer, including visual, security/performance and privacy lenses.
- Probe unsupported/no-consent, stale hash, invalid alias, unsafe path, prompt injection and unwanted rebrand.
- Correct predecessor-owned source and rerun focused tests, require reviewer approval of final hashes.
- Record actual provider/model/effort/session evidence; never mark synthetic review complete.
- Reuse routingctl, task_context_router, planctl, existing validators and P056 security/performance gates; no parallel orchestration.
- Produce real source hashes/test results and genuine independent review where required; never call prepared research executed implementation.

## Exact write ownership
- skill/plan-and-execute/scripts/design_context.py
- skill/plan-and-execute/scripts/uxctl.py
- skill/plan-and-execute/references/UI_UX_WORKFLOW.md
- skill/plan-and-execute/references/UI_UX_DESIGN_SYSTEM.md
- skill/plan-and-execute/SKILL.md
- test/optimization/ux_context_self_test.py

## Testable acceptance
- [ ] Real independent model review approves actual current design-memory source and approval boundaries.
- [ ] No data leakage, unapproved redesign or DIRECT-mode overhead; high/critical issues corrected.

Cross-check applicable negative cases A–P and provenance in P065 research. Screenshot matching never overrides keyboard/functional failures; unsupported tool is not a green run.

## Validation (only after code)
- python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_122
- python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_122

No real code, independent review, paid agent or browser validation has run in this planning task.
