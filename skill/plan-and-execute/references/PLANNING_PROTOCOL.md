# Planning protocol

Use this file only while converting an approved study into the executable TODO graph. Read `ARTIFACT_WRITING.md` first.

## 1. Preserve meaning, compress representation

The original request remains verbatim evidence. Derived planning text must be shorter because it is structured, not because requirements are discarded.

Create:

1. request parts `P...` — independently testable/constraint-bearing user intents;
2. requirements `R...` — observable obligations/constraints with source, priority, and originating request-part ids;
3. executable TODOs — context-cohesive implementation/validation boundaries;
4. minimal global/scoped execution context;
5. portable F/L capability requirements plus a live provider compatibility table;
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

## 6. Build provider compatibility dynamically

Read `PORTABLE_MODEL_ROUTING.md`. During planning, query the current local CLI/configuration and current authoritative documentation rather than using model names remembered from this skill or a previous plan.

Build top-level `model_compatibility` covering Codex, Claude, Gemini, Qwen, and Muse. For each provider:

- map every F1-F4 to a current concrete model;
- map every family's L1-L5 to actual native effort levels;
- repeat/clamp adjacent L values when the provider supports fewer levels;
- record `checked_at` and sources.

This table is intentionally separate from task semantics. Switching provider later refreshes/resolves this binding and preserves the TODO's F/L.

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

Approve only when all required checks are true and `unresolved_findings` is empty. Keep review notes concrete.

## 12. Deterministic quality gates

Create with `planctl_concise.py`, then require:

```bash
python <skill-dir>/scripts/studyctl_concise.py validate-plan --plan <plan-path>
python <skill-dir>/scripts/planctl_concise.py validate --plan <plan-path>
python <skill-dir>/scripts/planctl_concise.py audit --plan <plan-path>
```

For a portable plan, creation/validation also require canonical `MODEL_COMPATIBILITY.json` and matching `MODEL_COMPATIBILITY.md`. A failed check is a specification defect; fix the derived field/table rather than weakening the validator.
