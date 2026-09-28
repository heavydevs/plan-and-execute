# Auxiliary assistants and tier routing - resumable implementation

Request: docs/requests/auxiliary-model-assistants-and-tier-routing.md
Base: da785e567f5f3c6640f1ba3e0caf39900e4b0310
Branch: feature/auxiliary-assistants-tier-routing-20260928

User explicitly requested partial commits/pushes and retention of the plan for resumption.
This bootstrap is not a completed plan or implementation. The skill controller will create
an authoritative manifest with bounded TODO definitions after repository study.

## Intended boundaries
1. Study primary sources and actual runner contracts; refine the request and acceptance tests.
2. Implement validated global/per-plan tier routes and the sequential configuration interface.
3. Implement bounded availability fallback without altering semantic failure escalation.
4. Implement opt-in, budgeted, read-only advisory validation triage.
5. Integrate, run regression tests and review the whole skill; record remaining platform limits.

## Execution constraints
- Keep main unchanged until the implementation has been reviewed.
- Commit source, tests and authoritative plan checkpoints after each validated TODO.
- Preserve the original request in git history; record research as maintainer documentation.
- No provider CLI or independent model worker is installed in the chat container. Use the
  skill's host-managed path with deterministic validation; do not claim model isolation.
- Direct git networking is unavailable. Use the authorized GitHub connector for writes and
  a read-only CI checkpoint artifact to obtain the exact repository, not an installed copy.
- The existing CI on the base revision already fails; distinguish baseline failures from regressions.

## Recovery
Read the newest .ai-work/*/manifest.json and TODO.md once generated. Until then resume the
repository/research stage above. No implementation stage has been marked complete.
