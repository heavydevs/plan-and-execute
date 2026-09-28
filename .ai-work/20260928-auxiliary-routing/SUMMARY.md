# Implementation handoff: auxiliary assistants and tier routing

Implemented revised request R001-R010 with a retained six-task plan. The original
request is preserved in REQUEST.md and git history. Research/decisions are in
`docs/research/AUXILIARY_ROUTING.md`; user-facing setup is in both READMEs.

## Delivered

- Validated global/per-plan tier mapping, legacy compatibility and concrete models.
- Bounded same-rung availability fallback, persistent cooldowns and resumable pauses.
- Sequential `pae configure`, authentication status/confirmation and safe writes.
- Optional bounded advisory triage with separate read-only profile and no authority
  over code, deterministic validation or failure escalation.
- Full-skill review, restored instruction budgets, regressions and packaging checks.

## Validation

The Linux resource-mapped `npm run check` passed: 27 Node tests and all Python
suites, including 54 new regression tests. Controller/study/service-map audits and
skill packaging-schema validation passed. Each task checkpoint is independently
validated by the branch checkpoint workflow before its source commit is pushed.
Native Windows CI is a separate PR gate; consult its current result.

## Limits

No native model credentials/workers were available. The supported native advisor
is Claude tool-less/bare with explicit API-key billing, not subscription OAuth.
Antigravity and other unverified native advisory profiles skip safely. No actual
provider-generation, independent-model review or quantitative cost/quality gain
is claimed. See MAINTENANCE_REVIEW.md and the research evaluation protocol.

## Recovery

The plan is intentionally retained (`cleanup_on_success: false`). Read TODO.md and
manifest.json, then RESUME.md for relocating/rebinding paths. Do not repeat completed
tasks, clear availability/advisory ledgers to gain retries, or erase unrelated code.
Do not merge or publish to npm without a separate release decision.
