---
task_id: "130"
status: "pending"
requirements: "R069,R071,R072"
dependencies: "129"
allowed_related_task_reads: "none"
---

# 130 — Independently review source-backed pattern enforcement, safe exceptions and token economy

Objective: Independently review source-backed pattern enforcement, safe exceptions and token economy. Implement pre-decided P066 architecture; all actual implementation/review pending.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Review final 129 with a fresh max reviewer — Run `python docs/plans/20261028-skill-optimization/support/review_dispatch.py --repo-root . --task 130` in the foreground (rerun on exit 75); use only its DISPATCH line and compact findings. Focus: P066 and final 129 source/tests/receipt.
- [ ] **S002** Probe standards, exceptions and isolation — Probe approved versus inferred standards, ORM/JDBC exceptions, stale files, monorepo cross-talk, prompt injection, security/performance and context bounds.
- [ ] **S003** Correct defects and require final sign-off — Correct implementation owner defects and rerun tests, require true final SHA independent sign-off.
- [ ] **S004** Record honest provider and cost evidence — Record honest provider/model/effort/real cost or unknown and integration evidence; do not simulate completion.

## Scope

In: Independently review source-backed pattern enforcement, safe exceptions and token economy
Out: No unapproved target project modifications, network, external code disclosure, repeat broad research or duplicated orchestration.
Files: `skill/plan-and-execute/scripts/standards_guard.py`, `skill/plan-and-execute/scripts/task_context_router.py`, `skill/plan-and-execute/scripts/runner_contract.py`, `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/references/PROJECT_STANDARDS_GATES.md`, `test/optimization/standards_guard_self_test.py`, `docs/research/20261028-skill-optimization/implementation/130-receipt.json`, `docs/research/20261028-skill-optimization/implementation/130-outcome.md`

## Guidance

- Only read docs/research/20261028-skill-optimization/prepared-research/127-project-coding-standards-and-first-use-research.md when handling this task; apply complete architecture and adversarial acceptance A–T.
- Review only via review_dispatch.py (synchronous; max route; writes dispatch evidence); fix blocking findings, rerun declared checks, re-dispatch if a reviewed file changed, copy its RECEIPT_REVIEWER fields into the receipt.
- Prioritize deterministic inspection, narrow source reads and caching; broad project/code/web study only after approved first use or manual init/refresh.
- No unapproved edits, installs, secrets, paid providers or overwrites of agents' project instructions.
- Run real tests, record paths/hashes/permissions and source-specific receipt; no fabricated cost/success.
- Never launch background or asynchronous agents or processes: this headless session ends when you stop calling tools, so anything unfinished is lost.

## Acceptance

- A real fresh max-qualified reviewer approves the final 129 source/test/receipt hashes with dispatch provenance.
- The S002 adversarial probes pass: approved vs inferred standards, ORM/JDBC exceptions, stale files, monorepo cross-talk, prompt injection, security/performance and context bounds.
- High/critical findings are fixed and re-reviewed on the final hashes.
- A frontier (Fable 5.2 / Astra 6.2) reviewer is accepted only with recorded repeated max-review failure; a reused review session or dispatch is rejected.
- Every 2026-11-20 acceptance addition of task 129 has actual test evidence on the final reviewed hashes.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_130`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_130`
