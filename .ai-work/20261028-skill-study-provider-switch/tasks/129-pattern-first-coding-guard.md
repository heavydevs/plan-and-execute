---
task_id: "129"
status: "pending"
requirements: "R069,R071,R072"
dependencies: "128,108,112,114"
allowed_related_task_reads: "none"
---

# 129 — Integrate pattern-first code reuse, scoped retrieval and architectural drift checks into implementation and review

Objective: Integrate pattern-first code reuse, scoped retrieval and architectural drift checks into implementation and review. Implement pre-decided P066 architecture; all actual implementation/review pending.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Use P066 and accepted evidence — Use P066 and real accepted 128/108/112/114/120 evidence, without repeating broad research.
- [ ] **S002** Implement scoped source-hashed retrieval — Implement module/intent scoped source-hashed retrieval of approved rules, installed AND used libraries, nearby examples and reusable helpers.
- [ ] **S003** Apply architecture preflight and diff review — Apply architecture preflight and diff reviewer to package/naming, imports, persistence ORM vs JDBC, duplicate helpers and exception handling; inferred rules warn and approved rules gate.
- [ ] **S004** Handle approved exceptions and migrations — Handle approved native SQL/JDBC exceptions, module-specific styles and planned migrations through scoped ADR/waiver and acceptance tests; stale hash triggers targeted invalidation only.
- [ ] **S005** Integrate guard evidence with routing and review — Integrate compact guard evidence with DIRECT/ORCHESTRATED task_context_router and security/performance review; no new paid agent or web calls in ordinary tasks.
- [ ] **S006** Test drift, isolation and disabled mode — Test JPA→JDBC architectural drift, legitimate query, monorepo isolation, malicious input, unreadable tools and disabled-mode/no-index behavior.

## Scope

In: Integrate pattern-first code reuse, scoped retrieval and architectural drift checks into implementation and review
Out: No unapproved target project modifications, network, external code disclosure, repeat broad research or duplicated orchestration.
Files: `skill/plan-and-execute/scripts/standards_guard.py`, `skill/plan-and-execute/scripts/task_context_router.py`, `skill/plan-and-execute/scripts/runner_contract.py`, `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/references/PROJECT_STANDARDS_GATES.md`, `test/optimization/standards_guard_self_test.py`, `docs/research/20261028-skill-optimization/implementation/129-receipt.json`, `docs/research/20261028-skill-optimization/implementation/129-outcome.md`

## Guidance

- Only read docs/research/20261028-skill-optimization/prepared-research/127-project-coding-standards-and-first-use-research.md when handling this task; apply complete architecture and adversarial acceptance A–T.
- Reuse existing CLI/routing, task_context_router, UX first-use (where applicable), security/performance 107/108 and test strategy 111/112.
- Prioritize deterministic inspection, narrow source reads and caching; broad project/code/web study only after approved first use or manual init/refresh.
- No unapproved edits, installs, secrets, paid providers or overwrites of agents' project instructions.
- Run real tests, record paths/hashes/permissions and source-specific receipt; no fabricated cost/success.
- Run after 113/114 on the shared runner files (run_isolated.py, runner_contract.py); rebase on their accepted versions.

## Acceptance

- P066 cases A-F, N, Q, R and T pass with real tests, including JPA->JDBC drift flagged, an approved JDBC exception passing, and monorepo isolation.
- No source, target project or approval boundary overwritten implicitly; malformed input and unavailable tools fail safely.
- First-use consent, reusable source-backed agent docs, framework-consistent ORM/JDBC/exception detection and UX lazy activation are validated where applicable.
- Test/reviewer evidence exists for current code SHA; otherwise task remains pending.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_129`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_129`
