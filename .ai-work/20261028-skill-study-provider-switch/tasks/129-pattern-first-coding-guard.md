---
task_id: "129"
status: "pending"
requirements: "R069,R071,R072"
dependencies: "128,108,112"
allowed_related_task_reads: "none"
---

# 129 — Integrate pattern-first code reuse, scoped retrieval and architectural drift checks into implementation and review

**Architecture:** docs/research/20261028-skill-optimization/prepared-research/127-project-coding-standards-and-first-use-research.md. Read this only during matching implementation or independent review. All source implementation and real reviews PENDING.

## Required implementation/review checkpoints
- [ ] **S001** — Use P066 and real accepted 128/108/112/120 evidence, without repeating broad research.
- [ ] **S002** — Implement module/intent scoped source-hashed retrieval of approved rules, installed AND used libraries, nearby examples and reusable helpers.
- [ ] **S003** — Apply architecture preflight and diff reviewer to package/naming, imports, persistence ORM vs JDBC, duplicate helpers and exception handling; inferred rules warn and approved rules gate.
- [ ] **S004** — Handle approved native SQL/JDBC exceptions, module-specific styles and planned migrations through scoped ADR/waiver and acceptance tests; stale hash triggers targeted invalidation only.
- [ ] **S005** — Integrate compact guard evidence with DIRECT/ORCHESTRATED task_context_router and security/performance review; no new paid agent or web calls in ordinary tasks.
- [ ] **S006** — Test JPA→JDBC architectural drift, legitimate query, monorepo isolation, malicious input, unreadable tools and disabled-mode/no-index behavior.

## Guardrails
- Do not repeat broad web/code study during normal tasks; authorized first-use or proactive init/refresh only.
- Reuse existing routing, context, CLI, security/performance and test-selection contracts. Minimize per-phase tokens without weakening capability floors or independent review.
- Preserve privacy, current approved project patterns, legacy behavior and existing agent files; no unapproved external code disclosure or installs.
- Create actual evidence (tests, affected source hashes, genuine independent review where applicable); docs are not proof.

## Exact write ownership
- skill/plan-and-execute/scripts/standards_guard.py
- skill/plan-and-execute/scripts/task_context_router.py
- skill/plan-and-execute/scripts/runner_contract.py
- skill/plan-and-execute/scripts/run_isolated.py
- skill/plan-and-execute/references/PROJECT_STANDARDS_GATES.md
- test/optimization/standards_guard_self_test.py

## Acceptance
- [ ] User-visible cases A–T in P066 satisfied with real tests: ORM reuse, scoped legitimate exceptions, helpers, one-time consent, no repeated UX, safe multi-provider exports.
- [ ] No source, target project or approval boundary overwritten implicitly; malformed input and unavailable tools fail safely.
- [ ] Test/reviewer evidence exists for current code SHA; otherwise task remains pending.

## Focused validation
- python test/optimization/standards_guard_self_test.py
- python test/optimization/route_aware_context_self_test.py
- python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_129

No actual runtime skill change, automated product validation or independent agent review has been performed in this planning amendment.
