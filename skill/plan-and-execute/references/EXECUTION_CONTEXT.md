# Execution context and validated learning

Use this file after TODO boundaries are stable. The purpose is to give each fresh worker the **minimum non-obvious knowledge it cannot cheaply recover itself**.

## Omission is the default

A fact being relevant does not justify a shared context file.

Use this order:

1. Can the worker cheaply read the fact from its own source/test files? -> omit.
2. Is the fact needed by one TODO only? -> keep it in that task definition.
3. Is it needed by at least two but fewer than all TODOs? -> scoped context.
4. Is it required by every TODO? -> global `CONTEXT.md`.

Do not create context merely to summarize the request, study, architecture, TODO graph, or coding conventions already available in repository instructions.

## Global `CONTEXT.md`

Create only when every TODO needs the same non-obvious fact/constraint.

Each item has:

- `id`;
- `kind`: `fact`, `constraint`, `decision`, `interface`, or `validation`;
- `text`: one operational statement;
- `necessity`: why every assigned TODO needs it;
- `source_refs`: stable evidence ids/paths/symbols.

Example:

`G001 constraint — API v2 keeps response field 'id' as a string. (source: R004)`

Prefer this to a paragraph about API compatibility history.

## Scoped context files

Create `contexts/<topic>.md` only for a strict subset of at least two TODOs.

A scoped context must have a concrete sharing reason, such as two TODOs implementing opposite sides of one protocol/interface. Do not use a scoped file because tasks merely share a language/framework.

Avoid overlapping scoped files with the same fact. Put each shared fact at the narrowest correct scope.

## Context budgets

The concise controller enforces smaller limits than the legacy renderer:

- context text <= 220 chars;
- necessity <= 260;
- context rationale <= 320;
- context file <= 2200 chars;
- task context-boundary rationale <= 360;
- context-boundary item <= 200.

These are maxima. Prefer references over explanation.

## Worker assignment

The task definition lists its exact assigned context paths. The worker must read exactly those files before implementation and report them in `context_files_read`.

The orchestrator rejects missing/extra assigned reads. Workers must not browse other plan context files.

Plan-time context is immutable during execution. New discoveries belong in validated execution learnings, not by mutating `CONTEXT.md` for later tasks.

## Validated execution learnings

A completed TODO may publish a learning only when:

- the target is a predeclared later TODO in `learning_targets`;
- the target has not started;
- the finding matches the declared topics;
- source TODO deterministic validation passed;
- the finding would save meaningful rediscovery effort;
- the learning has concrete source references.

Learning kinds: `code`, `procedure`, `decision`, `pitfall`, `validation`.

A good item:

`validation — Reproduce vendor timeout with test VendorClientTest.timeout before changing retry order. (refs: tests/...::timeout, ./gradlew ...)`

Bad items:

- `We learned a lot about the vendor API.`
- transcript/history summaries;
- generic framework advice;
- conclusions with no source reference;
- information the target can retrieve cheaply from its own files.

Learning guidance is capped at 320 chars; a target-specific learning file is capped at 2200 chars.

The worker reports assigned learning reads in `learning_files_read`; the orchestrator verifies the exact set.

## Review checks

The fresh plan review must set:

- `contexts_minimal`: no unnecessary global/scoped/single-task duplication;
- `context_boundaries_sound`: each TODO groups concerns that materially benefit from one worker history and isolates unrelated domains.

Reject the plan when:

- global context is not required by every TODO;
- a scoped file serves only one TODO;
- the same fact appears in global + scoped + task text;
- context contains process narration or generic advice;
- independent domains are combined only for framework similarity;
- broad/bidirectional learning edges recreate plan history.

## Design principle

Shared context should behave like an interface: small, stable, sourced, and required by all consumers. Execution learning should behave like a targeted patch note: validated, directional, and only as large as the future target needs.
