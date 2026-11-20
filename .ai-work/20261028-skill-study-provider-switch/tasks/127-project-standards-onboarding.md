---
task_id: "127"
status: "pending"
requirements: "R069,R070,R072"
dependencies: "025,120"
allowed_related_task_reads: "none"
---

# 127 — Implement one-time project onboarding, source-derived coding standards documentation and CLI

Objective: Implement one-time project onboarding, source-derived coding standards documentation and CLI. Implement pre-decided P066 architecture; all actual implementation/review pending.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Inspect P066 and live source — Inspect only P066 and the relevant live source, 025/120 evidence and test baselines.
- [ ] **S002** Implement persisted first-use consent — Implement persisted per-project, per-topic standards/UX first-use consent with noninteractive fallback, secure scope, worktrees and atomic state.
- [ ] **S003** Run approved init/refresh discovery only — Perform approved init/refresh only: deterministic module/libraries/usage/representative patterns/ORM/helpers discovery; optional contemporary source study; no recurring full research.
- [ ] **S004** Generate compact source-hashed standards docs — Generate compact source-hashed docs/ai-standards/ AGENT_INDEX.md, manifests, TECH_STACK.md, ARCHITECTURE.md, CODING_RULES.md, REUSE_CATALOG.json, module rules and ADRs; retain inferred vs approved distinction.
- [ ] **S005** Implement pae standards and onboarding CLI — Implement pae standards status/init/refresh/explain/check/export-instructions and pae onboarding status, --json/dry-run, CLI help and EN/PT-BR usage examples; exporting third-party instructions requires approval.
- [ ] **S006** Test recognition, consent and security cases — Test JPA and monorepo recognition, declared-but-unused dependencies, consent persistence, CI/headless zero prompting, stale hash, malicious files, security and no fallback to unwanted study.

## Scope

In: Implement one-time project onboarding, source-derived coding standards documentation and CLI
Out: No unapproved target project modifications, network, external code disclosure, repeat broad research or duplicated orchestration.
Files: `skill/plan-and-execute/scripts/project_onboarding.py`, `skill/plan-and-execute/scripts/project_standards.py`, `skill/plan-and-execute/scripts/standardsctl.py`, `skill/plan-and-execute/references/PROJECT_STANDARDS.md`, `test/optimization/standards_onboarding_self_test.py`, `skill/plan-and-execute/references/PROJECT_ONBOARDING.md`, `skill/plan-and-execute/SKILL.md`, `bin/plan-and-execute.js`, `test/cli.test.js`, `docs/research/20261028-skill-optimization/implementation/127-receipt.json`, `docs/research/20261028-skill-optimization/implementation/127-outcome.md`

## Guidance

- Only read docs/research/20261028-skill-optimization/prepared-research/127-project-coding-standards-and-first-use-research.md when handling this task; apply complete architecture and adversarial acceptance A–T.
- Reuse existing CLI/routing, task_context_router, UX first-use (where applicable), security/performance 107/108 and test strategy 111/112.
- Prioritize deterministic inspection, narrow source reads and caching; broad project/code/web study only after approved first use or manual init/refresh.
- No unapproved edits, installs, secrets, paid providers or overwrites of agents' project instructions.
- Run real tests, record paths/hashes/permissions and source-specific receipt; no fabricated cost/success.

## Acceptance

- P066 cases D, F, G, H-M, O, P, S and T pass with real tests: one-time consent, no repeated UX, discovery, safe exports that never overwrite manual agent files.
- No source, target project or approval boundary overwritten implicitly; malformed input and unavailable tools fail safely.
- First-use consent, reusable source-backed agent docs, framework-consistent ORM/JDBC/exception detection and UX lazy activation are validated where applicable.
- Test/reviewer evidence exists for current code SHA; otherwise task remains pending.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_127`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_127`
