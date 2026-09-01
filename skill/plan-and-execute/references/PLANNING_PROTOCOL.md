# Planning protocol

Use this file only while converting an approved study into the executable TODO graph. Read `ARTIFACT_WRITING.md` first.

## 1. Preserve meaning, compress representation

The original request remains verbatim evidence. Derived planning text must be shorter because it is **structured**, not because requirements are discarded.

Create:

1. request parts `P...` — independently testable/constraint-bearing user intents;
2. requirements `R...` — observable obligations/constraints with source, priority, and originating request-part ids;
3. executable TODOs — context-cohesive implementation/validation boundaries;
4. minimal global/scoped execution context;
5. a fresh review result.

Do not copy paragraphs from the request into each layer. Keep the request as source evidence and use stable ids to connect layers.

## 2. Requirements

Each request part must map to at least one requirement. Each requirement must map to at least one executable TODO.

Prefer one observable obligation per requirement. Use an EARS-like structure when useful:

- `<component> shall <observable response>`;
- `When <trigger>, <component> shall <observable response>`;
- `While <state>, <component> shall <observable response>`;
- `If <failure>, <component> shall <safe observable response>`.

Resolve vague user wording before autostart. If `fast`, `robust`, `easy`, `as needed`, `adequate`, or similar language materially affects correctness, derive a concrete condition/threshold or keep an explicit open question.

## 3. Recursive TODO decomposition

Start from coherent workstreams, then split until every leaf TODO has:

- one coherent outcome;
- one bounded implementation responsibility;
- one independent validation boundary;
- mapped requirement ids;
- explicit in/out scope and expected files when predictable;
- observable acceptance criteria;
- deterministic validation commands;
- a small enough repository/context surface for one fresh worker;
- stable resumable subtasks;
- explicit dependencies.

Split when any of these is true:

- two outcomes can fail independently;
- unrelated domains/subsystems share one TODO only because their framework shape is similar;
- migration, implementation, rollout, or validation phases have independent failure/recovery boundaries;
- retained context for one concern would not materially help the other;
- the leaf would be `extreme` complexity.

Do not split into arbitrary file-by-file microtasks. Keep tightly coupled controller/service/entity/test changes together when they implement one invariant and share diagnosis/validation.

## 4. Context boundary per TODO

Every schema-v4 task has `context_boundary`:

- `shared_context`: short statements describing knowledge genuinely shared by all subtasks;
- `why_one_todo`: the concrete reason one worker context improves this leaf;
- `separate_from`: concerns intentionally isolated elsewhere.

This is reviewer evidence stored in `manifest.json`; it does not need to be repeated verbosely in the worker task file.

`high` complexity requires a concrete atomicity rationale. No executable TODO may be `extreme`.

## 5. Resumable subtasks

Subtasks are checkpoints inside one TODO, not hidden top-level work.

A subtask should describe a stable milestone worth preserving across interruption, for example:

- introduce the data contract;
- implement the bounded behavior;
- add/adjust focused tests;
- complete a migration step that cannot be safely repeated blindly.

If a subtask has an independent outcome, different context domain, or independent acceptance boundary, promote it to its own TODO.

Keep titles/objectives short. State the milestone, not the process narrative.

## 6. Directional validated learning

Use `learning_targets` only when an earlier TODO may discover expensive information that a later similar TODO would otherwise need to rediscover.

A relationship must be:

- predeclared before source execution;
- earlier -> later only;
- narrow and target-specific;
- topic-bounded;
- materialized only after source deterministic validation;
- omitted when the target can cheaply rediscover the fact itself.

Do not use learning files as summaries, chat memory, or generic framework advice.

## 7. Progressive execution context

Read `EXECUTION_CONTEXT.md` after TODO boundaries stabilize.

- Omit global context by default.
- Create `CONTEXT.md` only for non-obvious facts/constraints required by **every** TODO.
- Create `contexts/<topic>.md` only for a strict subset of at least two TODOs.
- Keep single-TODO information in that task definition.
- Ground every shared item with source references.

The review must approve `contexts_minimal` and `context_boundaries_sound`.

## 8. Acceptance and validation

Acceptance states the externally observable or repository-verifiable condition. Validation states how the orchestrator proves it.

Good pair:

- acceptance: `Expired refresh tokens return HTTP 401 and no new access token.`
- validation: `./gradlew test --tests RefreshTokenTest.expiredTokenIsRejected`

Avoid:

- `works correctly`;
- `implementation is robust`;
- `tests pass` without naming the relevant command/suite when known;
- criteria that merely restate the implementation steps.

Every TODO needs at least one deterministic validation command. The worker's own claim is never sufficient validation.

## 9. Fresh plan review

Review from a fresh context using the complete request plus compact study/requirements/graph/context proposal. Challenge only material defects:

- uncovered/distorted request parts;
- requirements without TODO coverage;
- TODOs with multiple independent outcomes;
- artificial coupling between domains;
- hidden top-level work in subtasks;
- weak/duplicated context;
- broad learning edges;
- dependency cycles/missing dependencies;
- unverifiable acceptance;
- unsafe autostart;
- remaining vague terms that change behavior.

Approve only when all required checks are true and `unresolved_findings` is empty. Keep review notes to concrete findings; do not narrate the review process.

## 10. Deterministic quality gates

Create with `planctl_concise.py`, then require:

```bash
python <skill-dir>/scripts/studyctl_concise.py validate-plan --plan <plan-path>
python <skill-dir>/scripts/planctl_concise.py validate --plan <plan-path>
python <skill-dir>/scripts/planctl_concise.py audit --plan <plan-path>
```

The concise validator additionally rejects oversized derived fields and a small high-confidence set of vague requirement smells. A failed concision check is a specification defect, not a request to truncate text blindly: rewrite the derived field more precisely or split it into atomic items.
