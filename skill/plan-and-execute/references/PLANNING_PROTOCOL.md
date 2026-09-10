# Planning protocol

Use this file only while converting an approved study into the executable TODO graph. Read `ARTIFACT_WRITING.md` first.

## 1. Preserve meaning, compress representation

The original request remains verbatim evidence. Derived planning text must be shorter because it is structured, not because requirements are discarded.

Create:

1. request parts `P...` — independently testable/constraint-bearing user intents;
2. requirements `R...` — observable obligations/constraints with source, priority, and originating request-part ids;
3. executable TODOs — context-cohesive implementation/validation boundaries;
4. minimal global/scoped execution context;
5. portable F/L capability requirements plus today's compatibility snapshot for the active provider;
6. a fresh review result.

Do not copy paragraphs from the request into each layer. Keep the request as source evidence and use stable ids to connect layers.

## 2. Requirements

Each request part must map to at least one requirement. Each requirement must map to at least one executable TODO.

Prefer one observable obligation per requirement. Resolve vague user wording before autostart. If `fast`, `robust`, `easy`, `as needed`, `adequate`, or similar language materially affects correctness, derive a concrete condition/threshold or keep an explicit open question.

## 3. Recursive TODO decomposition

Start from coherent workstreams, then split until every leaf TODO has:

- one coherent outcome and bounded implementation responsibility;
- one independent validation boundary;
- mapped requirement ids;
- explicit in/out scope and expected files when predictable;
- observable acceptance criteria and deterministic validation commands;
- a small enough repository/context surface for one fresh worker;
- stable resumable subtasks and explicit dependencies.

Split when outcomes can fail independently, unrelated domains are artificially coupled, migration/implementation/rollout/validation have different recovery boundaries, retained context does not help both concerns, or the leaf would be `extreme` complexity.

Do not split into arbitrary file-by-file microtasks. Keep tightly coupled changes together when they implement one invariant and share diagnosis/validation.

## 4. Context boundary per TODO

Every schema-v4 task has `context_boundary`:

- `shared_context`: short statements describing knowledge genuinely shared by all subtasks;
- `why_one_todo`: the concrete reason one worker context improves this leaf;
- `separate_from`: concerns intentionally isolated elsewhere.

`high` complexity requires a concrete atomicity rationale. No executable TODO may be `extreme`.

## 5. Assign portable F/L capability

Read `MODEL_ROUTING.md`. New tasks never pin a provider or concrete model. Assign only:

- `model_family`: `F1` economy, `F2` general coding, `F3` strong, `F4` frontier;
- `model_level`: `L1` lowest through `L5` highest reasoning/power inside the selected family.

Choose F from semantic capability/risk and L from required reasoning depth. Strong deterministic verification supports cheaper F/L. Weak verification, high blast radius, security/concurrency/data-integrity decisions, or evidence-backed reasoning failures justify stronger values.

Do not add `provider`, `model_tier`, `reasoning_effort`, or model ids to a new F/L TODO.

## 6. Resolve provider compatibility from the daily cache

Read `PORTABLE_MODEL_ROUTING.md`. Compatibility discovery is provider-scoped and cached independently under `~/.plan-and-execute/cache/model-compatibility`.

Before querying any CLI or documentation, identify the provider currently executing/planning and run:

```bash
python <skill-dir>/scripts/model_compatctl.py cache-status --provider <provider> --json
```

If the status is `fresh`, reuse that provider's cached compatibility. Do not repeat CLI/documentation discovery for that provider during the same local calendar day.

If the status is `missing`, `stale`, or `invalid`, inspect only that provider's current local CLI/configuration and current authoritative documentation. Map F1-F4 to current concrete models, map L1-L5 to actual native effort levels, repeat/clamp adjacent L values when needed, record timezone-aware `checked_at` plus sources, and save it with `model_compatctl.py cache-write`.

Build top-level `model_compatibility` from the active provider's fresh cache. A new Codex plan therefore normally contains only a Codex/OpenAI compatibility object; it must not research Claude, Gemini, Qwen, and Muse merely to fill a matrix. Each of those providers receives its own cache only when actually used.

Switching provider later preserves TODO F/L. Check the new provider's cache first; perform live discovery only when that provider's cache is not fresh.

## 7. Resumable subtasks

Subtasks are checkpoints inside one TODO, not hidden top-level work. A subtask should describe a stable milestone worth preserving across interruption. If it has an independent outcome, different context domain, or independent acceptance boundary, promote it to its own TODO.

Keep titles/objectives short. State the milestone, not process narrative.

## 8. Directional validated learning

Use `learning_targets` only when an earlier TODO may discover expensive information that a later similar TODO would otherwise need to rediscover.

A relationship must be predeclared, earlier -> later only, narrow/target-specific, topic-bounded, materialized only after deterministic validation, and omitted when the target can cheaply rediscover the fact itself.

Do not use learning files as summaries, chat memory, or generic framework advice.

## 9. Progressive execution context

Read `EXECUTION_CONTEXT.md` after TODO boundaries stabilize.

- Omit global context by default.
- Create `CONTEXT.md` only for non-obvious facts/constraints required by every TODO.
- Create `contexts/<topic>.md` only for a strict subset of at least two TODOs.
- Keep single-TODO information in that task definition.
- Ground every shared item with source references.

The review must approve `contexts_minimal` and `context_boundaries_sound`.

## 10. Acceptance and validation

Acceptance states the externally observable or repository-verifiable condition. Validation states how the orchestrator proves it. Every TODO needs at least one deterministic validation command. The worker's own claim is never sufficient validation.

Avoid vague criteria such as `works correctly`, `implementation is robust`, or unnamed `tests pass` when a focused command is known.

## 11. Fresh plan review

Review from a fresh context using the complete request plus compact study/requirements/graph/context/F-L/compatibility proposal. Challenge material defects including uncovered request parts, multi-outcome TODOs, artificial coupling, hidden top-level work, weak context, dependency errors, unverifiable acceptance, unsafe autostart, inappropriate F/L, and stale/unsubstantiated provider mappings.

For compatibility, verify that the snapshot belongs to the provider currently being used, its `checked_at` is today in local time, and it came from either a fresh daily cache or provider-specific live discovery followed by cache-write. Do not require unrelated providers to be present.

Approve only when all required checks are true and `unresolved_findings` is empty. Keep review notes concrete.

## 12. Deterministic quality gates

Create with `planctl_concise.py`, then require:

```bash
python <skill-dir>/scripts/studyctl_concise.py validate-plan --plan <plan-path>
python <skill-dir>/scripts/planctl_concise.py validate --plan <plan-path>
python <skill-dir>/scripts/planctl_concise.py audit --plan <plan-path>
```

For a portable plan, creation/validation require canonical `MODEL_COMPATIBILITY.json` and matching `MODEL_COMPATIBILITY.md`. New plan creation also rejects provider compatibility not checked on the current local calendar day. A failed check is a specification defect; fix the derived field/binding rather than weakening the validator.
