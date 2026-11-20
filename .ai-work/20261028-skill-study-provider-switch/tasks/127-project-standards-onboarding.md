---
task_id: "127"
status: "pending"
requirements: "R069,R070,R072"
dependencies: "120,025"
allowed_related_task_reads: "none"
---

# 127 — Implement one-time project onboarding, source-derived coding standards documentation and CLI

**Architecture:** docs/research/20261028-skill-optimization/prepared-research/127-project-coding-standards-and-first-use-research.md. Read this only during matching implementation or independent review. All source implementation and real reviews PENDING.

## Required implementation/review checkpoints
- [ ] **S001** — Inspect only P066 and the relevant live source, 025/120 evidence and test baselines.
- [ ] **S002** — Implement persisted per-project, per-topic standards/UX first-use consent with noninteractive fallback, secure scope, worktrees and atomic state.
- [ ] **S003** — Perform approved init/refresh only: deterministic module/libraries/usage/representative patterns/ORM/helpers discovery; optional contemporary source study; no recurring full research.
- [ ] **S004** — Generate compact source-hashed docs/ai-standards/ AGENT_INDEX.md, manifests, TECH_STACK.md, ARCHITECTURE.md, CODING_RULES.md, REUSE_CATALOG.json, module rules and ADRs; retain inferred vs approved distinction.
- [ ] **S005** — Implement pae standards status/init/refresh/explain/check/export-instructions and pae onboarding status, --json/dry-run, CLI help and EN/PT-BR usage examples; exporting third-party instructions requires approval.
- [ ] **S006** — Test JPA and monorepo recognition, declared-but-unused dependencies, consent persistence, CI/headless zero prompting, stale hash, malicious files, security and no fallback to unwanted study.

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
- python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_127

No actual runtime skill change, automated product validation or independent agent review has been performed in this planning amendment.
