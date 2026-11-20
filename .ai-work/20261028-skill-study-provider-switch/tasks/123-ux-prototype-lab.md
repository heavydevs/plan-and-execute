---
task_id: "123"
status: "pending"
requirements: "R066,R068"
dependencies: "122,112"
allowed_related_task_reads: "none"
---

# 123 — Implement optional real-component or Node Vite HTML JavaScript SCSS prototype lab and safe transfer plan

**Objective:** Implement optional real-component or Node Vite HTML JavaScript SCSS prototype lab and safe transfer plan. Read P065 architecture and accepted 122/112 receipts, inspect only relevant real frontend source.

**Pre-decided architecture:** docs/research/20261028-skill-optimization/prepared-research/121-uiux-design-prototype-research.md. Implement these decisions without a new broad research phase. All functionality and reviews are PENDING.

## Internal implementation checklist
- [ ] **S001** — Read P065 architecture and accepted 122/112 receipts, inspect only relevant real frontend source.
- [ ] **S002** — Implement deterministic mode: in-app/stories with REAL components when capable, otherwise optional isolated Vite vanilla HTML/JS/SCSS lab; no mandatory Figma or npm install.
- [ ] **S003** — Build versioned local scaffold template with pinned dependency lockfile, localhost-only dev and sanitized mock data, generated tokens, no production credentials or remote assets.
- [ ] **S004** — Create selected-route real->prototype read-only import with component/variant/token mapping and source_sha256/fidelity warnings; prevent symlink and URL leaks.
- [ ] **S005** — Implement prototype->real sync-plan with affected real components, UX decisions, acceptance tests, hashes, conflicts, rollback and required user approval; NO automatic production writes.
- [ ] **S006** — Run actual tests for legacy, existing, new, offline, stale hash, malicious path and permissions; record evidence only.

## Design and execution constraints
- Read docs/research/20261028-skill-optimization/prepared-research/121-uiux-design-prototype-research.md only while implementing task 123 and examine only current affected source/dependency receipts.
- Read P065 architecture and accepted 122/112 receipts, inspect only relevant real frontend source.
- Implement deterministic mode: in-app/stories with REAL components when capable, otherwise optional isolated Vite vanilla HTML/JS/SCSS lab; no mandatory Figma or npm install.
- Build versioned local scaffold template with pinned dependency lockfile, localhost-only dev and sanitized mock data, generated tokens, no production credentials or remote assets.
- Create selected-route real->prototype read-only import with component/variant/token mapping and source_sha256/fidelity warnings; prevent symlink and URL leaks.
- Implement prototype->real sync-plan with affected real components, UX decisions, acceptance tests, hashes, conflicts, rollback and required user approval; NO automatic production writes.
- Run actual tests for legacy, existing, new, offline, stale hash, malicious path and permissions; record evidence only.
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
- [ ] Mature frontend prefers real component workbench, not duplicate HTML lab.
- [ ] Explicit opt-in creates usable isolated Node/Vite HTML/JS/SCSS lab with safe fixtures.
- [ ] Import reads only selected existing UI; sync generates PLAN not unauthorized write; stale SHA blocks.
- [ ] Missing Node/Figma/permissions yields honest skip, not green test.

Cross-check applicable negative cases A–P and provenance in P065 research. Screenshot matching never overrides keyboard/functional failures; unsupported tool is not a green run.

## Validation (only after code)
- python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_123
- python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_123

No real code, independent review, paid agent or browser validation has run in this planning task.
