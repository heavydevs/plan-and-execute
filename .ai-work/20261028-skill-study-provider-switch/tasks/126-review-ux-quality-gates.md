---
task_id: "126"
status: "pending"
requirements: "R065,R066,R067,R068"
dependencies: "125"
allowed_related_task_reads: "none"
---

# 126 — Independently review full UI/UX quality, consent, economy and integration

Objective: Independently review full UI/UX quality, consent, economy and integration. Read P065 report, 125 final source/receipt and minimal accepted 122/124 review metadata.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Inspect scoped source architecture — Read P065 report, 125 final source/receipt and minimal accepted 122/124 review metadata.
- [ ] **S002** Implement or genuinely review contract — Run `python docs/plans/20261028-skill-optimization/support/review_dispatch.py --repo-root . --task 126` in the foreground (rerun on exit 75); use only its DISPATCH line and compact findings. Focus: visual craft, security, performance, accessibility, privacy.
- [ ] **S003** Enforce consent/source-of-truth/safety — Test all P065 negative A–P cases, especially keyboard vs screenshot, skipped browser, stale prototype, consent and token context budget.
- [ ] **S004** Run adversarial validation — Fix owned defects or reopen source owner, rerun selected current tests; retain global validation gate 082.
- [ ] **S005** Record actual acceptance evidence — Record real reviewer session/effort/model/final hash/cost and any unsupported environments; remain pending without evidence.

## Scope

In: Independently review full UI/UX quality, consent, economy and integration
Out: No automatic production frontend edits, unrelated test changes, second plan or paid agent use.
Files: `skill/plan-and-execute/scripts/ux_review.py`, `skill/plan-and-execute/scripts/uxctl.py`, `skill/plan-and-execute/references/UI_UX_VALIDATION.md`, `bin/plan-and-execute.js`, `test/optimization/ux_visual_acceptance_self_test.py`, `test/cli.test.js`, `docs/research/20261028-skill-optimization/implementation/126-receipt.json`, `docs/research/20261028-skill-optimization/implementation/126-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/121-uiux-design-prototype-research.md only while implementing task 126 and examine only current affected source/dependency receipts.
- Read P065 report, 125 final source/receipt and minimal accepted 122/124 review metadata.
- Dispatch real fresh max-qualified independent review for visual craft, security, performance, accessibility and privacy.
- Test all P065 negative A–P cases, especially keyboard vs screenshot, skipped browser, stale prototype, consent and token context budget.
- Fix owned defects or reopen source owner, rerun selected current tests; retain global validation gate 082.
- Record real reviewer session/effort/model/final hash/cost and any unsupported environments; remain pending without evidence.
- Reuse routingctl, task_context_router, planctl, existing validators and P056 security/performance gates; no parallel orchestration.
- Produce real source hashes/test results and genuine independent review where required; never call prepared research executed implementation.
- P066: broad UX study strictly on first approved relevant project use or explicit pae ux init/refresh. Shared coding+UX consent from 127/128; subsequent UX tasks load approved scoped design index only; no repeated research.
- Cross-check applicable negative cases A–P and provenance in P065 research; screenshot matching never overrides keyboard/functional failures; an unsupported tool is not a green run.
- Review only via review_dispatch.py (synchronous; max route; writes dispatch evidence); fix blocking findings, rerun declared checks, re-dispatch if a reviewed file changed, copy its RECEIPT_REVIEWER fields into the receipt.
- Never launch background or asynchronous agents or processes: this headless session ends when you stop calling tools, so anything unfinished is lost.

## Acceptance

- Genuine final-hash review approves visual, functional and accessible UI behavior together.
- No unauthorized real frontend edits, paid visual calls, lost global gate or unrelated UX loads.
- 126 genuinely gates integration 082; only measured savings can be claimed.
- No recurring UX external study or model calls after setup; explicit refresh and one-time opt-in work with durable project state.
- A frontier (Fable 5.2 / Astra 6.2) reviewer is accepted only with recorded repeated max-review failure; a reused review session or dispatch is rejected.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_126`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_126`
