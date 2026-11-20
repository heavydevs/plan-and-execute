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

- `package.json` records source identity, raw source and extracted block-stream SHA-256 hashes, `extraction_version`, `source_index_sha256`, sizing/route evidence, package state, artifact paths, and post-validation `integrity` pins.
- `SOURCE_INDEX.json` maps stable fragment ids to ordered source anchors, headings, both `file_sha256` and `source_text_sha256`, approximate token size, paths and per-fragment `obligation_ids`. It also records `block_stream_sha256`, `fragments_manifest_sha256`, the `fragmentation` parameters, extracted source `obligations` (each mapped to every fragment that holds it), `detected_contradictions`, and any `unsupported_structures` warnings. All schema-v2 hash pins are mandatory.
- `fragments/` are faithful source-text fragments. They are evidence, not summaries, and are immutable after package creation.
- `digests/` contain source-referenced atomic obligations, constraints, interfaces, risks, dependencies, validation implications, contradictions, and pattern candidates for bounded fragment batches.
- `PATTERN_SEEDS.json` contains candidate cross-cutting contracts discovered across fragments. It is input to final planning, not yet an executable pattern registry.
- `COVERAGE_REVIEW.json` proves every immutable fragment and unique source obligation was covered (`covered_fragment_ids`, `covered_obligation_ids`). It carries every detected and digest contradiction by id in `recorded_contradictions`, and lists every recorded unsupported source structure in `acknowledged_unsupported_structures`. When no obligations were extracted, it explains in `acknowledged_obligation_floor` how requirements were verified. It also records unresolved contradictions or omissions that can change planning.
- `FINAL_PLAN_INPUT.md` is the compact handoff the normal final planner starts from. It points to evidence by stable id/path instead of copying the whole source.

## Consumption rules

For a prepared package:

1. Before consuming the package for final planning, run `preplanctl.py validate-consumption --package <package-dir> --source <raw-source> --require-source`. Omit `--require-source` only when the raw source is knowingly unavailable. It recomputes fragment content SHA-256 hashes from disk, never trusting modification time or file size alone, and rejects missing, changed, duplicate, escaping or symlinked artifacts. It also re-hashes the raw source and re-derives the source index, rejecting a stale source, extractor version or re-pinned index. If it reports `source_verification.status=unavailable`, only the in-package hash chain was checked (`original_path` is not pinned). Record that limitation.
2. Read `FINAL_PLAN_INPUT.md`, `SOURCE_INDEX.json`, `PATTERN_SEEDS.json`, and `COVERAGE_REVIEW.json` first. Check `unsupported_structures` in `SOURCE_INDEX.json` for extraction limits, for example tracked changes, text boxes, images or non-body Office parts. Tracked insertions and moves are excluded from fragment text, so compare their previews before trusting the polarity of an edited paragraph. Obligation extraction is an English-modal and fixed-id heuristic, not a complete requirement list.
3. Do **not** concatenate every fragment into final-planner context.
4. Retrieve fragments by id per material question (no summary pyramid) using `preplanctl.py read-fragment` or verified hash checks; retrieve a fragment only when a requirement, architecture decision, contradiction, acceptance criterion, or pattern needs primary-source verification.
5. Preserve fragment/source ids in derived requirements and planning findings when they materially support the decision.
6. Run the ordinary adaptive study, final planning, fresh review, task routing, validation, and execution workflow after this handoff. The primary plan never dictates final implementation model tiers.
7. If package coverage is incomplete, a fragment hash is stale, or a material contradiction remains unresolved, stop before autostart and repair/re-run the relevant primary-plan step.

## Cross-cutting patterns

Pattern seeds describe contracts that multiple implementation TODOs are expected to obey, for example a REST Resource facade, Admin CRUD interaction rules, SCSS/token composition, error handling, or a data-access invariant.

During final planning, promote a seed into a live pattern only when at least two TODOs genuinely share a contract whose later change could require already-completed signatories to be revisited. Use `SHARED_PATTERNS.md` for lifecycle semantics.

Do not use pattern seeds for generic framework advice or facts that workers can cheaply rediscover.

## Why this boundary is intentionally small

The entry router, normal final planner, and prepared-package consumer need only this file. The detailed mechanics for splitting oversized sources and constructing the primary plan live in `PRIMARY_PLANNING.md` and must remain unloaded unless the primary-plan route is actually selected.
