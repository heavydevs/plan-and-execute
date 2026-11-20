---
task_id: "121"
status: "pending"
requirements: "R065,R068"
dependencies: "025,120"
allowed_related_task_reads: "none"
---

# 121 — Implement opt-in UI/UX design system, identity and compact agent memory

**Objective:** Implement opt-in UI/UX design system, identity and compact agent memory. Read assigned P065 architectural report and current affected symbols; verify accepted 025/120 prior receipts only.

**Pre-decided architecture:** docs/research/20261028-skill-optimization/prepared-research/121-uiux-design-prototype-research.md. Implement these decisions without a new broad research phase. All functionality and reviews are PENDING.

## Internal implementation checklist
- [ ] **S001** — Read assigned P065 architectural report and current affected symbols; verify accepted 025/120 prior receipts only.
- [ ] **S002** — Implement UX intent/setup gate: ask once for new project or explicit design request; non-UI DIRECT default OFF with no prompt, model, browser or reading new reference.
- [ ] **S003** — Extract real existing components, token/style source, route map by rg/AST and hashes; distinguish inferred from user-approved identity, do not rebrand mature UI.
- [ ] **S004** — Produce durable project-local docs/ui-ux/AGENT_INDEX.md, manifest.json, identity.md, tokens.json, components.json and UX_PATTERNS.md only when opted in; validate DTCG aliases/cycles/contrast and keep approved status honest.
- [ ] **S005** — Wire concise lazy reference from SKILL.md, use shared routing and source hash invalidation not whole-project re-study.
- [ ] **S006** — Add tests for greenfield, brownfield, denied setup, backend-only no overhead, stale hashes, token cycles, path traversal, privacy; actual receipts only.

## Design and execution constraints
- Read docs/research/20261028-skill-optimization/prepared-research/121-uiux-design-prototype-research.md only while implementing task 121 and examine only current affected source/dependency receipts.
- Read assigned P065 architectural report and current affected symbols; verify accepted 025/120 prior receipts only.
- Implement UX intent/setup gate: ask once for new project or explicit design request; non-UI DIRECT default OFF with no prompt, model, browser or reading new reference.
- Extract real existing components, token/style source, route map by rg/AST and hashes; distinguish inferred from user-approved identity, do not rebrand mature UI.
- Produce durable project-local docs/ui-ux/AGENT_INDEX.md, manifest.json, identity.md, tokens.json, components.json and UX_PATTERNS.md only when opted in; validate DTCG aliases/cycles/contrast and keep approved status honest.
- Wire concise lazy reference from SKILL.md, use shared routing and source hash invalidation not whole-project re-study.
- Add tests for greenfield, brownfield, denied setup, backend-only no overhead, stale hashes, token cycles, path traversal, privacy; actual receipts only.
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
- [ ] Existing visual patterns remain canonical and fresh UI components reuse real exports and styles without unapproved redesign.
- [ ] Greenfield identity remains provisional until the user approves; design tokens have deterministic typed semantics.
- [ ] Non-UI task has no UX runtime or extra context; agent index is short, source-indexed and privacy-safe.
- [ ] Real tests prove hash invalidation and that no fictitious product implementation/review is credited.

Cross-check applicable negative cases A–P and provenance in P065 research. Screenshot matching never overrides keyboard/functional failures; unsupported tool is not a green run.

## Validation (only after code)
- python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_121
- python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_121

No real code, independent review, paid agent or browser validation has run in this planning task.
