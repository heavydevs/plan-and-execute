# Planning input contract

This is the **small shared boundary** between normal final planning and oversized-request preprocessing. Read it only after orchestration has been selected and before deciding which planning route owns the request.

The contract exists so the normal final-plan path never needs to load the much larger `PRIMARY_PLANNING.md` instructions.

## Accepted final-planning inputs

A final planner consumes exactly one of these forms:

1. **Direct request** — the complete inline request or ordinary request file is small enough to study and plan without a staged preprocessing pass.
2. **Prepared request package** — an oversized source was processed by the primary-plan path. The final planner starts from the package index/handoff and retrieves only the source fragments needed for the current planning decision.

Both forms are authoritative request evidence. A prepared package is not permission to discard the original source: its immutable fragments plus source map preserve traceability back to the supplied document.

## Prepared package layout

A prepared package lives outside the ephemeral primary-plan directory, normally under `.ai-work/prepared/<package-id>/`:

```text
prepared/<package-id>/
  package.json
  SOURCE_INDEX.json
  FINAL_PLAN_INPUT.md
  fragments/
    F001-*.md
    F002-*.md
  digests/
    D001.json
    D002.json
  PATTERN_SEEDS.json
  COVERAGE_REVIEW.json
```

Required semantics:

- `package.json` records source identity, hashes, sizing/route evidence, package state, and artifact paths.
- `SOURCE_INDEX.json` maps stable fragment ids to source anchors, headings, hashes, approximate token size, and paths.
- `fragments/` are faithful source-text fragments. They are evidence, not summaries, and are immutable after package creation.
- `digests/` contain source-referenced atomic obligations, constraints, interfaces, risks, dependencies, validation implications, and pattern candidates for bounded fragment batches.
- `PATTERN_SEEDS.json` contains candidate cross-cutting contracts discovered across fragments. It is input to final planning, not yet an executable pattern registry.
- `COVERAGE_REVIEW.json` proves every immutable fragment was covered and records unresolved contradictions or omissions that can change planning.
- `FINAL_PLAN_INPUT.md` is the compact handoff the normal final planner starts from. It points to evidence by stable id/path instead of copying the whole source.

## Consumption rules

For a prepared package:

1. Read `FINAL_PLAN_INPUT.md`, `SOURCE_INDEX.json`, `PATTERN_SEEDS.json`, and `COVERAGE_REVIEW.json` first.
2. Do **not** concatenate every fragment into final-planner context.
3. Retrieve a fragment only when a requirement, architecture decision, contradiction, acceptance criterion, or pattern needs primary-source verification.
4. Preserve fragment/source ids in derived requirements and planning findings when they materially support the decision.
5. Run the ordinary adaptive study, final planning, fresh review, task routing, validation, and execution workflow after this handoff. The primary plan never dictates final implementation model tiers.
6. If package coverage is incomplete or a material contradiction remains unresolved, stop before autostart and repair/re-run the relevant primary-plan step.

## Cross-cutting patterns

Pattern seeds describe contracts that multiple implementation TODOs are expected to obey, for example a REST Resource facade, Admin CRUD interaction rules, SCSS/token composition, error handling, or a data-access invariant.

During final planning, promote a seed into a live pattern only when at least two TODOs genuinely share a contract whose later change could require already-completed signatories to be revisited. Use `SHARED_PATTERNS.md` for lifecycle semantics.

Do not use pattern seeds for generic framework advice or facts that workers can cheaply rediscover.

## Why this boundary is intentionally small

The entry router, normal final planner, and prepared-package consumer need only this file. The detailed mechanics for splitting oversized sources and constructing the primary plan live in `PRIMARY_PLANNING.md` and must remain unloaded unless the primary-plan route is actually selected.
