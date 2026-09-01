# Token and context efficiency

Use this reference when designing prompts, changing the harness, reviewing execution context, or deciding whether extra study is worth its token cost.

## Goal

Minimize total model tokens and repeated context while preserving implementation quality, requirement coverage, deterministic validation, and resumability. Optimize the whole workflow, not only individual prompts.

## 1. Spend model tokens only on judgment

Prefer deterministic code for operations that do not require semantic judgment:

- lifecycle discovery and state transitions;
- requirement/plan schema validation;
- dependency resolution and next-task selection;
- file/path allowlists;
- completion-report validation;
- subtask checkpoints;
- validation command execution;
- summary-input aggregation;
- cleanup and safety checks.

A model should receive the result of those operations, not re-derive them from large files or chat history.

## 2. Progressive disclosure beats one large prompt

Keep the skill entrypoint small and load detailed references only at their phase:

1. lifecycle/intake;
2. adaptive study;
3. planning/decomposition;
4. execution-context design;
5. provider routing/execution;
6. final summary/cleanup.

Do not preload provider-specific, lifecycle, schema, or installation documentation merely because it exists.

## 3. Search first, read second

For repository study:

- use filename/symbol/keyword/reference search before opening files;
- inspect the smallest high-signal range that answers the question;
- expand one dependency/test hop only when the current evidence creates a material question;
- prefer structural summaries (tree, imports, test names, diff stat) over dumping files;
- stop when more evidence is unlikely to change architecture, compatibility, task boundaries, risk, or validation.

For external study, record concise findings and planning impact. Do not carry raw articles into execution workers.

## 4. Context is assigned by necessity, not relevance

A fact belongs in a worker's assigned context only if omitting it materially increases the chance of an incorrect implementation or validation result.

Use this order:

1. task definition for task-local facts;
2. scoped context for facts required by multiple but not all TODOs;
3. global context only for facts required by every TODO;
4. omit facts that can be cheaply rediscovered from nearby source.

Prefer references to repository paths, symbols, commands, and requirement ids over pasted source code.

## 5. Fresh workers are cheaper than polluted long histories

Start each executable TODO with a fresh worker. Do not pass:

- parent conversation history;
- previous worker transcripts;
- whole PLAN.md or TODO.md;
- unrelated task definitions;
- raw study notes;
- prior logs or reports unless a precise validated learning was predeclared for this target.

Persist durable state in `manifest.json`, task definitions, context files, subtask checkpoints, and validated learning artifacts instead.

## 6. Cross-task learning must have positive expected value

Create a learning edge only when all are true:

- the target task is later and untouched;
- the source and target share a specific difficult procedure, invariant, pitfall, decision, or validation method;
- rediscovering that information is plausibly more expensive than reading the learning file;
- the source finding has passed deterministic validation;
- the learning can be expressed concisely with concrete references.

Do not transfer generic framework knowledge, broad summaries, logs, or speculative advice. An empty learning report is preferred to low-value context.

## 7. Preserve stable prefixes for provider prompt caching

When a provider supports prompt caching, maximize reusable stable prefixes:

- put invariant worker rules before task-specific identifiers/data;
- avoid timestamps, attempt numbers, absolute ephemeral paths, or other changing fields early in the prompt when they are not needed there;
- keep schemas/invariant instructions byte-stable where possible;
- append dynamic task data after the stable contract.

Caching is an optimization, never a correctness dependency. Providers without compatible caching must still work correctly.

## 8. Bound tool and report output

Large tool output can dominate context even when the prompt is small.

- store full logs/results on disk;
- return only status, bounded tails, selected errors, and stable file references to the orchestrator;
- cap repeated failure excerpts;
- deduplicate repeated validation output;
- keep completion reports structured and concise;
- do not embed complete reports in future worker prompts.

When a later model needs detail, point it to the exact file/range rather than copying the content into orchestration context.

## 9. Avoid redundant validation by models

The worker may run task-local checks while implementing, but authoritative pass/fail is the orchestrator's deterministic rerun. Do not ask a second model to reinterpret successful deterministic output unless there is a semantic risk that the command cannot cover.

Plan review should be proportional:

- simple: orchestrator self-check;
- medium: fresh review only when uncertainty/risk/boundary ambiguity warrants it;
- complex: fresh review when supported.

## 10. Summarize from authoritative compact state

The final summary should be built from:

- completed task ids/titles;
- changed files;
- bounded worker summaries if useful;
- deterministic validation results;
- remaining recorded risks/follow-ups;
- a bounded git diff stat.

Do not concatenate full worker reports by default. The summarizer must not need plan files or historical chat.

## 11. Model routing is a token-cost control

Start at the least expensive tier/effort that is credible for the TODO. Escalate after concrete technical failure or evidence of insufficient reasoning capacity. Do not use a stronger model merely because the overall request is complex; route each isolated TODO independently.

Cheap tasks include direct localized edits with deterministic acceptance. Stronger routes are justified by architecture, concurrency, security, migrations, ambiguous failures, or repeated unsuccessful attempts.

## 12. Never optimize away these quality anchors

Do not remove or excessively compress:

- complete user requirements and constraints;
- task-local invariants and acceptance criteria;
- dependency and ownership boundaries;
- concrete failure evidence required to repair the current TODO;
- validation commands and their authoritative outcomes;
- recovery/checkpoint state;
- safety checks around destructive actions.

The objective is fewer irrelevant/repeated tokens, not less necessary information.

## Research basis

The strategy follows several converging findings/practices:

- modern provider prompt caching rewards repeated stable prompt prefixes, so stable instructions should precede dynamic task data;
- provider guidance on context engineering recommends compacting long histories and preserving structured state/artifacts instead of replaying transcripts;
- repository-level software-engineering research consistently benefits from localization/retrieval before generation rather than feeding an entire repository;
- long-context research shows that merely adding more context does not guarantee better use of information, supporting selective retrieval and concise task-local context;
- prompt-compression research demonstrates that irrelevant/redundant context can be reduced substantially, but this skill intentionally uses deterministic selection and structured memory rather than lossy compression for correctness-critical contracts.

Treat these as design principles. Provider-specific behavior may change, so verify current official documentation when changing caching, model, context-window, or billing assumptions.
