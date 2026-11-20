---
task_id: "122"
status: "pending"
requirements: "R065,R068"
dependencies: "121"
allowed_related_task_reads: "none"
---

# 122 — Independently review visual identity, design token and agent context safety

Objective: Independently review visual identity, design token and agent context safety. Read only P065 report, final 121 source/receipt and its tests.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Inspect scoped source architecture — Read only P065 report, final 121 source/receipt and its tests.
- [ ] **S002** Implement or genuinely review contract — Run `python docs/plans/20261028-skill-optimization/support/review_dispatch.py --repo-root . --task 122` in the foreground (rerun on exit 75); use only its DISPATCH line and compact findings. Focus: visual, security/performance and privacy.
- [ ] **S003** Enforce consent/source-of-truth/safety — Probe unsupported/no-consent, stale hash, invalid alias, unsafe path, prompt injection and unwanted rebrand.
- [ ] **S004** Run adversarial validation — Correct predecessor-owned source and rerun focused tests, require reviewer approval of final hashes.
- [ ] **S005** Record actual acceptance evidence — Record actual provider/model/effort/session evidence; never mark synthetic review complete.

## Scope

In: Independently review visual identity, design token and agent context safety
Out: No automatic production frontend edits, unrelated test changes, second plan or paid agent use.
Files: `skill/plan-and-execute/scripts/design_context.py`, `skill/plan-and-execute/scripts/uxctl.py`, `skill/plan-and-execute/references/UI_UX_WORKFLOW.md`, `skill/plan-and-execute/references/UI_UX_DESIGN_SYSTEM.md`, `skill/plan-and-execute/SKILL.md`, `test/optimization/ux_context_self_test.py`, `docs/research/20261028-skill-optimization/implementation/122-receipt.json`, `docs/research/20261028-skill-optimization/implementation/122-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/121-uiux-design-prototype-research.md only while implementing task 122 and examine only current affected source/dependency receipts.
- Read only P065 report, final 121 source/receipt and its tests.
- Dispatch genuine independent fresh max-qualified reviewer, including visual, security/performance and privacy lenses.
- Probe unsupported/no-consent, stale hash, invalid alias, unsafe path, prompt injection and unwanted rebrand.
- Correct predecessor-owned source and rerun focused tests, require reviewer approval of final hashes.
- Record actual provider/model/effort/session evidence; never mark synthetic review complete.
- Reuse routingctl, task_context_router, planctl, existing validators and P056 security/performance gates; no parallel orchestration.
- Produce real source hashes/test results and genuine independent review where required; never call prepared research executed implementation.
- P066: broad UX study strictly on first approved relevant project use or explicit pae ux init/refresh. Shared coding+UX consent from 127/128; subsequent UX tasks load approved scoped design index only; no repeated research.
- Cross-check applicable negative cases A–P and provenance in P065 research; screenshot matching never overrides keyboard/functional failures; an unsupported tool is not a green run.
- Review only via review_dispatch.py (synchronous; max route; writes dispatch evidence); fix blocking findings, rerun declared checks, re-dispatch if a reviewed file changed, copy its RECEIPT_REVIEWER fields into the receipt.
- Never launch background or asynchronous agents or processes: this headless session ends when you stop calling tools, so anything unfinished is lost.

## Acceptance

- Real independent model review approves actual current design-memory source and approval boundaries.
- No data leakage, unapproved redesign or DIRECT-mode overhead; high/critical issues corrected.
- No recurring UX external study or model calls after setup; explicit refresh and one-time opt-in work with durable project state.
- A frontier (Fable 5.2 / Astra 6.2) reviewer is accepted only with recorded repeated max-review failure; a reused review session or dispatch is rejected.
- Every 2026-11-20 acceptance addition of task 121 has actual test evidence on the final reviewed hashes.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_122`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_122`
