---
task_id: "128"
status: "pending"
requirements: "R069,R070,R072"
dependencies: "127"
allowed_related_task_reads: "none"
---

# 128 — Independently review coding-standard discovery, consent, documentation and CLI safety

**Architecture:** docs/research/20261028-skill-optimization/prepared-research/127-project-coding-standards-and-first-use-research.md. Read this only during matching implementation or independent review. All source implementation and real reviews PENDING.

## Required implementation/review checkpoints
- [ ] **S001** — Read P066 and only actual final 127 code/tests/receipts and review their SHA hashes.
- [ ] **S002** — Run genuine separate fresh maximum-qualified reviewer for UX/standards consent safety, source evidence, code quality, performance, privacy and token economy.
- [ ] **S003** — Adversarial tests for worktree identity, repeat consent, no-TTY CI, secrets, prompt injection, symlinks, stale code, hidden remote calls and overwritten agent files.
- [ ] **S004** — Fix or reopen owner for blocking defects, rerun focused tests; record genuine reviewer route, source hash and decisions.

## Guardrails
- Do not repeat broad web/code study during normal tasks; authorized first-use or proactive init/refresh only.
- Reuse existing routing, context, CLI, security/performance and test-selection contracts. Minimize per-phase tokens without weakening capability floors or independent review.
- Preserve privacy, current approved project patterns, legacy behavior and existing agent files; no unapproved external code disclosure or installs.
- Create actual evidence (tests, affected source hashes, genuine independent review where applicable); docs are not proof.

## Exact write ownership
- skill/plan-and-execute/scripts/project_onboarding.py
- skill/plan-and-execute/scripts/project_standards.py
- skill/plan-and-execute/scripts/standardsctl.py
- skill/plan-and-execute/references/PROJECT_ONBOARDING.md
- skill/plan-and-execute/references/PROJECT_STANDARDS.md
- skill/plan-and-execute/SKILL.md
- bin/plan-and-execute.js
- test/optimization/standards_onboarding_self_test.py
- test/cli.test.js

## Acceptance
- [ ] User-visible cases A–T in P066 satisfied with real tests: ORM reuse, scoped legitimate exceptions, helpers, one-time consent, no repeated UX, safe multi-provider exports.
- [ ] No source, target project or approval boundary overwritten implicitly; malformed input and unavailable tools fail safely.
- [ ] Test/reviewer evidence exists for current code SHA; otherwise task remains pending.

## Focused validation
- python test/optimization/standards_onboarding_self_test.py
- node --test test/cli.test.js
- python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_128

No actual runtime skill change, automated product validation or independent agent review has been performed in this planning amendment.
