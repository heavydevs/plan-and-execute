# Final planning protocol

Use this file only while converting approved final-planning evidence into the executable implementation TODO graph. Read `ARTIFACT_WRITING.md` first. If the request arrived through PRIMARY_PLAN, consume the prepared package according to `PLANNING_INPUT_CONTRACT.md`; do not read `PRIMARY_PLANNING.md` here.

## 1. Preserve meaning, compress representation

The original request or prepared immutable fragments remain source evidence. Derived planning text is shorter because it is structured, not because requirements are discarded.

Create:

1. request parts `P...` — independently testable/constraint-bearing user intents;
2. requirements `R...` — observable obligations/constraints with source, priority, and originating request-part ids;
3. executable TODOs — context-cohesive implementation/validation boundaries;
4. minimal global/scoped execution context;
5. optional versioned shared-pattern spec for evolving cross-TODO contracts;
6. per-TODO logical model/effort routing;
7. a fresh review result.

For prepared packages, keep fragment/digest ids in source refs when they materially support a requirement or decision. Never flatten the entire package into one prompt merely to create the plan.

## 2. Route planning work explicitly

Read `PLANNING_ROUTING.md` when assigning a model to planning work. The planner's current/root model is not automatically the planning route, and it is never switched: a stage whose floor exceeds the root tier is delegated to a fresh worker at that tier.

Use deterministic tools for mechanical operations; economy for bounded extraction; standard for ordinary synthesis; strong for architecture/decomposition with high blast radius, weak verification, security/migration/data-integrity risk, or subtle cross-domain constraints. Fresh review should be capable enough to challenge the hardest material planning decision.

When only a few decisions are hard, resolve them first (`PLANNING_ROUTING.md` §3): inventory `hard_decisions`, resolve each with a strong fresh worker into a decision + rationale + constraints, then compose the mechanical plan at standard capability. Record them in `request_analysis.hard_decisions` with `route_used`.

Final implementation TODO routing is decided separately later in this protocol.

## 3. Requirements

Each request part maps to at least one requirement. Each requirement maps to at least one executable TODO.

Prefer one observable obligation per requirement. Use an EARS-like structure when useful:

- `<component> shall <observable response>`;
- `When <trigger>, <component> shall <observable response>`;
- `While <state>, <component> shall <observable response>`;
- `If <failure>, <component> shall <safe observable response>`.

Resolve vague user wording before autostart. If `fast`, `robust`, `easy`, `as needed`, or similar wording changes correctness, derive an observable condition/threshold or keep an explicit open question.

## 4. Recursive TODO decomposition

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
- explicit dependencies;
- an independently chosen logical model tier/effort.

Split when two outcomes can fail independently, unrelated domains share one TODO only because their framework shape is similar, migration/implementation/rollout/validation phases have independent recovery boundaries, retained context for one concern would not help the other, or the leaf would be `extreme`.

Do not split into arbitrary file-by-file microtasks. Keep tightly coupled controller/service/entity/test changes together when they implement one invariant and share diagnosis/validation.

## 5. Context boundary per TODO

Every schema-v4 task has `context_boundary`:

- `shared_context`: short statements genuinely shared by all subtasks;
- `why_one_todo`: the concrete reason one worker context improves this leaf;
- `separate_from`: concerns intentionally isolated elsewhere.

This is reviewer evidence stored in `manifest.json`; do not repeat it verbosely in the worker task file. `high` complexity requires a concrete atomicity rationale. No executable TODO may be `extreme`.

## 6. Resumable subtasks

Subtasks are checkpoints inside one TODO, not hidden top-level work. Good checkpoints include introducing a data contract, implementing bounded behavior, adding focused tests, or completing a migration step that cannot be blindly repeated.

If a subtask has an independent outcome, different context domain, or independent acceptance boundary, promote it to its own TODO.

A `high` TODO whose implementation volume is large may instead declare `design_route`: the runner first dispatches a stronger design worker that writes a bounded design note (approach, decisions, contracts, ordered steps mapped to checkpoint ids, validation strategy), then the implementation worker runs at the TODO's own route with that note. Do not use it for a small hard edit — one strong worker is cheaper than two workers plus a handoff.

## 7. Detect cross-cutting pattern contracts

After TODO boundaries stabilize, identify repeated normative rules that multiple TODOs must obey. Examples: a frontend REST Resource facade, Admin list/modal rules, SCSS/token composition, API error shape, or idempotency/persistence conventions.

Do **not** duplicate a real shared contract into every TODO. Instead, when the contract may evolve and an update could require already-completed consumers to change, read `SHARED_PATTERNS.md` and create a separate `/tmp/pattern-spec.json` with:

- stable pattern id/title;
- concise normative contract;
- source/requirement/fragment refs;
- rationale for sharing;
- explicit signatory TODO ids.

Create no pattern when ordinary immutable execution context is sufficient. Pattern signatories must be neither missing nor over-broad.

For prepared packages, `PATTERN_SEEDS.json` contains candidates, not decisions. Promote only seeds justified by final TODO boundaries.

## 8. Directional validated learning

Use `learning_targets` only when an earlier TODO may discover expensive information that a later similar TODO would otherwise need to rediscover.

A learning edge is earlier -> later, narrow, target-specific, predeclared, materialized only after deterministic validation, and omitted when the target can cheaply rediscover the fact.

Do not use learning files for evolving shared contracts. Patterns own backward invalidation; learnings remain immutable directional evidence.

## 9. Progressive execution context

Read `EXECUTION_CONTEXT.md` after TODO boundaries stabilize.

- Omit global context by default.
- Create `CONTEXT.md` only for non-obvious facts/constraints required by every TODO.
- Create `contexts/<topic>.md` only for a strict subset of at least two TODOs.
- Keep single-TODO information in that task definition.
- Ground every shared item with source references.

The review must approve `contexts_minimal` and `context_boundaries_sound`.

## 10. Implementation model routing

For every TODO, choose `provider`, `model_tier`, and `reasoning_effort` from the implementation leaf itself. Do not inherit:

- the root chat's model;
- a PRIMARY_PLAN digest route;
- the final-planning architecture/reviewer route;
- a neighboring TODO's route.

Use `MODEL_ROUTING.md` and only the active provider reference when concrete dispatch is needed. Prefer the lowest credible leaf capability from the leaf's signals (`routingctl.py route`); verifiability and blast radius matter more than parent size. An implementation worker never runs at `low` effort unless the edit is mechanical and deterministically checked.

## 11. Acceptance and validation

Acceptance states the externally observable or repository-verifiable condition. Validation states how the orchestrator proves it.

Good pair:

- acceptance: `Expired refresh tokens return HTTP 401 and no new access token.`
- validation: `./gradlew test --tests RefreshTokenTest.expiredTokenIsRejected`

Avoid `works correctly`, `implementation is robust`, `tests pass` without the relevant command/suite when known, or criteria that merely restate implementation steps.

Every TODO needs at least one deterministic validation command. The worker's own claim is never sufficient validation.

Validation commands run through the platform shell from the repository root (`cmd.exe` on Windows, `/bin/sh` elsewhere). Prefer the project's toolchain (`npm test -- <filter>`, `pytest <path>`, `./gradlew test --tests ...`) over POSIX builtins such as `test -f` or `grep -q` when a plan may be resumed on another operating system.

If a TODO signs shared patterns, acceptance implicitly includes implementing the current assigned pattern revisions; pattern adoption is recorded only after deterministic validation succeeds.

## 12. Fresh plan review

Review from a fresh context using the complete compact request evidence plus study/requirements/graph/context/pattern proposal. Challenge only material defects:

- uncovered/distorted request parts;
- requirements without TODO coverage;
- TODOs with multiple independent outcomes;
- artificial coupling or hidden top-level work in subtasks;
- weak/duplicated execution context;
- missing/over-broad pattern signatories or duplicated cross-cutting contracts;
- broad learning edges;
- dependency cycles/missing dependencies;
- unverifiable acceptance;
- implausible model-tier choices for weakly verifiable/high-blast-radius leaves, or a `design_route`/`hard_decisions` pass missing where the leaf signals justify it;
- unsafe autostart or remaining material vague terms.

For prepared packages, retrieve raw fragments selectively to challenge material claims; do not preload every fragment by default.

Approve only when all required checks are true and `unresolved_findings` is empty.

## 13. Deterministic quality gates

Create with `planctl_concise.py`, then require:

```bash
python <skill-dir>/scripts/studyctl_concise.py validate-plan --plan <plan-path>
python <skill-dir>/scripts/planctl_concise.py validate --plan <plan-path>
python <skill-dir>/scripts/planctl_concise.py audit --plan <plan-path>
```

When patterns exist, immediately follow final plan creation with:

```bash
python <skill-dir>/scripts/patternctl.py init --plan <plan-path> --spec /tmp/pattern-spec.json
python <skill-dir>/scripts/patternctl.py validate --plan <plan-path>
```

A failed concision/coverage/pattern check is a specification defect. Rewrite the derived field more precisely, split an atomic item, or fix signatory assignment; never silently truncate source meaning.
