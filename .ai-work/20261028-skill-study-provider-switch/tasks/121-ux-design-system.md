---
task_id: "121"
status: "pending"
requirements: "R065,R068"
dependencies: "025,120,128"
allowed_related_task_reads: "none"
---

# 121 — Implement opt-in UI/UX design system, identity and compact agent memory

Objective: Implement opt-in UI/UX design system, identity and compact agent memory. Read assigned P065 architectural report and current affected symbols; verify accepted 025/120 prior receipts only.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Inspect scoped source architecture — Read assigned P065 architectural report and current affected symbols; verify accepted 025/120/128 receipts only (shared consent comes from 127).
- [ ] **S002** Implement or genuinely review contract — Implement UX intent/setup gate: ask once for new project or explicit design request; non-UI DIRECT default OFF with no prompt, model, browser or reading new reference.
- [ ] **S003** Enforce consent/source-of-truth/safety — Extract real existing components, token/style source, route map by rg/AST and hashes; distinguish inferred from user-approved identity, do not rebrand mature UI.
- [ ] **S004** Run adversarial validation — Produce durable project-local docs/ui-ux/AGENT_INDEX.md, manifest.json, identity.md, tokens.json, components.json and UX_PATTERNS.md only when opted in; validate DTCG aliases/cycles/contrast and keep approved status honest.
- [ ] **S005** Record actual acceptance evidence — Wire concise lazy reference from SKILL.md, use shared routing and source hash invalidation not whole-project re-study.
- [ ] **S006** Close current-source final check — Add tests for greenfield, brownfield, denied setup, backend-only no overhead, stale hashes, token cycles, path traversal, privacy; actual receipts only.

## Scope

In: Implement opt-in UI/UX design system, identity and compact agent memory
Out: No automatic production frontend edits, unrelated test changes, second plan or paid agent use.
Files: `skill/plan-and-execute/scripts/design_context.py`, `skill/plan-and-execute/scripts/uxctl.py`, `skill/plan-and-execute/references/UI_UX_WORKFLOW.md`, `skill/plan-and-execute/references/UI_UX_DESIGN_SYSTEM.md`, `skill/plan-and-execute/SKILL.md`, `test/optimization/ux_context_self_test.py`, `docs/research/20261028-skill-optimization/implementation/121-receipt.json`, `docs/research/20261028-skill-optimization/implementation/121-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/121-uiux-design-prototype-research.md only while implementing task 121 and examine only current affected source/dependency receipts.
- Read assigned P065 architectural report and current affected symbols; verify accepted 025/120/128 receipts only (shared consent comes from 127).
- Implement UX intent/setup gate: ask once for new project or explicit design request; non-UI DIRECT default OFF with no prompt, model, browser or reading new reference.
- Extract real existing components, token/style source, route map by rg/AST and hashes; distinguish inferred from user-approved identity, do not rebrand mature UI.
- Produce durable project-local docs/ui-ux/AGENT_INDEX.md, manifest.json, identity.md, tokens.json, components.json and UX_PATTERNS.md only when opted in; validate DTCG aliases/cycles/contrast and keep approved status honest.
- Wire concise lazy reference from SKILL.md, use shared routing and source hash invalidation not whole-project re-study.
- Add tests for greenfield, brownfield, denied setup, backend-only no overhead, stale hashes, token cycles, path traversal, privacy; actual receipts only.
- Reuse routingctl, task_context_router, planctl, existing validators and P056 security/performance gates; no parallel orchestration.
- Produce real source hashes/test results and genuine independent review where required; never call prepared research executed implementation.
- P066: broad UX study strictly on first approved relevant project use or explicit pae ux init/refresh. Shared coding+UX consent from 127/128; subsequent UX tasks load approved scoped design index only; no repeated research.
- Shared first-use decision/state is implemented by 127 and reviewed by 128; do not build a second UX consent controller.
- Cross-check applicable negative cases A–P and provenance in P065 research; screenshot matching never overrides keyboard/functional failures; an unsupported tool is not a green run.

## Acceptance

- Existing visual patterns remain canonical and fresh UI components reuse real exports and styles without unapproved redesign.
- Greenfield identity remains provisional until the user approves; design tokens have deterministic typed semantics.
- Non-UI task has no UX runtime or extra context; agent index is short, source-indexed and privacy-safe.
- Real tests prove hash invalidation and that no fictitious product implementation/review is credited.
- No recurring UX external study or model calls after setup; explicit refresh and one-time opt-in work with durable project state.
- UX init/refresh, first-use consent and no repeated research are verified by spies in tests; no backend-only overhead or silent paid calls.
- node tools/validate-skill.js passes and SKILL.md stays <= 7167 normalized characters with at most one lazy pointer line.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_121`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_121`
