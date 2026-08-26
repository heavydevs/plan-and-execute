# Progressive execution context

## Contents

1. Purpose
2. Position in planning
3. Decision hierarchy
4. Global `CONTEXT.md`
5. Scoped context files
6. Information for a single TODO
7. Content quality rules
8. Plan-spec contract
9. Validated execution learnings
10. Worker isolation
11. Review and replanning

## 1. Purpose

Create execution-context files only when they reduce repeated rediscovery without widening worker scope. The goal is a smaller, more reliable prompt for each fresh worker, not a second copy of the request, study, or plan.

Omission is the default. A context artifact is justified only when a non-obvious fact, constraint, decision, interface contract, or validation rule is materially needed by more than one TODO.

Context files must be:

- concise enough to reread on every assigned worker invocation;
- grounded in named request, repository, research, requirement, or decision evidence;
- stable across the TODOs that receive them;
- operationally useful to implementation or validation;
- narrower than the complete request and plan.

## 2. Position in planning

Decide execution context after the requirements inventory and draft task graph exist, but before final plan review and plan creation.

Use this order:

```text
request + adaptive study
          |
          v
requirements and draft TODO graph
          |
          v
progressive execution-context decision
          |
          v
fresh plan review, including contexts_minimal and context_boundaries_sound
          |
          v
schema-v4 plan creation and validation
```

The task graph must exist first because the planner cannot know whether information is universal, shared by a strict subset, or relevant to a single TODO until task boundaries are clear.

## 3. Decision hierarchy

Classify each candidate fact with this strict hierarchy:

1. **Every TODO needs it:** consider global `CONTEXT.md`.
2. **At least two, but not every, TODO need it:** consider a scoped file under `contexts/`.
3. **Only a single TODO needs it:** keep it in that task definition.
4. **No TODO needs it to implement or validate correctly:** omit it.

Before creating any file, ask:

- Would a capable fresh worker likely make a material mistake without this information?
- Is the information non-obvious from the assigned task definition and nearby source?
- Will every assigned TODO use it, rather than merely find it interesting?
- Is it stable enough not to become stale during the plan?
- Can it be stated as one concise operational line?

If any answer is no, omit the item or move it to a narrower location.

## 4. Global `CONTEXT.md`

Create `CONTEXT.md` only when at least one item is indispensable to every executable TODO.

Appropriate global items include:

- a repository-wide compatibility boundary every task must preserve;
- a universal security constraint;
- one architectural ownership rule that governs every workstream;
- a cross-cutting interface invariant used by every task;
- a validation rule that every worker must follow.

Do not place these in global context:

- a summary of the request;
- the full architecture or study;
- TODO status or dependencies;
- generic advice such as "write tests" or "follow existing patterns";
- facts that apply only to some tasks;
- details easily rediscovered from one nearby file;
- rationale prose intended for reviewers rather than workers.

When no universal item survives this test, set the global decision to `omit` and record a substantive rationale. Do not create an empty `CONTEXT.md`.

## 5. Scoped context files

Scoped context files live under:

```text
contexts/<topic>.md
```

Create one only when the same narrow information is materially required by at least two TODOs and a strict subset of the complete task graph.

Examples:

- `contexts/oauth-rollout.md` for authentication implementation and migration TODOs, but not documentation-only work;
- `contexts/event-schema.md` for producer and consumer TODOs that share one event contract;
- `contexts/mobile-compatibility.md` for two client TODOs, but not backend persistence work.

Each scoped file must declare exactly which task ids receive it. The planner then references the file only in those task-definition files. Unassigned workers must not read it.

A scoped file that applies to every TODO belongs in global context. A scoped file that applies to a single TODO belongs in that task definition. Do not create overlapping files that repeat the same item.

## 6. Information for a single TODO

Information needed by a single TODO must remain in its task definition under scope, implementation guidance, acceptance criteria, or validation commands.

Do not create a separate context file for a single TODO. A one-task file adds another read, increases indirection, and weakens the guarantee that the task definition is self-contained.

## 7. Content quality rules

Represent each context item with:

- a stable id;
- `kind`: `fact`, `constraint`, `decision`, `interface`, or `validation`;
- one-line `text` describing the operational information;
- a one-line `necessity` explaining why the assigned TODOs need it;
- one to four `source_refs` grounding it in evidence.

`source_refs` may identify, for example:

- `request:P001`;
- `requirement:R004`;
- `study:I003`;
- `research:E002`;
- `README.md:42-61`;
- `src/auth/session.ts:110-168`;
- `ADR-007`.

The rendered worker file contains the concise operational text and compact source references. The longer necessity explanation remains in `manifest.json` and review material so it does not consume every worker's context.

Deterministic limits enforce restraint:

- global file: at most 8 items;
- each scoped file: at most 8 items;
- all context files combined: at most 24 items;
- at most 8 scoped files;
- each rendered file: at most 3,200 characters;
- each item text: one line, 15 to 280 characters;
- duplicate item text across files is rejected.

These are ceilings, not targets. Most plans should use zero to three items.

## 8. Plan-spec contract

Schema v4 requires an explicit `execution_context` decision even when no files are created:

```json
{
  "execution_context": {
    "global": {
      "decision": "omit",
      "rationale": "Every non-obvious constraint is specific to one TODO, so a shared file would duplicate task definitions.",
      "items": []
    },
    "scoped": []
  }
}
```

A plan with global and scoped context may use:

```json
{
  "execution_context": {
    "global": {
      "decision": "create",
      "rationale": "Every TODO must preserve the same public compatibility boundary.",
      "items": [
        {
          "id": "G001",
          "kind": "constraint",
          "text": "Preserve the existing public API and wire format throughout the implementation.",
          "necessity": "Every TODO can modify behavior observed through the existing contract, so all workers need this boundary.",
          "source_refs": ["request:P001", "ADR-004"]
        }
      ]
    },
    "scoped": [
      {
        "id": "oauth-rollout",
        "title": "OAuth rollout contract",
        "rationale": "Only TODOs 001 and 002 participate in the dual-login rollout transition.",
        "task_ids": [1, 2],
        "items": [
          {
            "id": "C001",
            "kind": "interface",
            "text": "Password login remains available until the OAuth migration completion flag is enabled.",
            "necessity": "Both authentication and migration workers must implement the same transition boundary.",
            "source_refs": ["request:P002", "study:I006"]
          }
        ]
      }
    ]
  }
}
```

File names and each task's `context_files` list are generated by `planctl.py`; do not author them manually.

## 9. Validated execution learnings

Plan-time context and execution-time learning solve different problems and must remain separate.

- `CONTEXT.md` and `contexts/*.md` are immutable decisions created before execution.
- `learnings/<source>-to-<target>.md` is an optional immutable projection created only after a source TODO completes and passes deterministic validation.

A learning file is not a mutable knowledge base and not a place to summarize prior work. It exists only when the plan predeclared a directional `learning_targets` relationship and the source worker reported a concise, evidence-backed finding relevant to that untouched future TODO.

Each learning file contains:

- source and target TODO ids;
- the plan-time reason those TODOs are similar;
- narrow approved topics;
- at most a few reusable findings of kind `code`, `procedure`, `decision`, `pitfall`, or `validation`;
- concrete repository paths, symbols, commands, tests, or external references.

It must never contain:

- the worker transcript or hidden reasoning;
- raw logs or complete completion reports;
- broad request, study, plan, or TODO summaries;
- mutable task status;
- advice for undeclared targets;
- speculative conclusions that were not supported by the validated implementation.

The controller creates one file per source-target pair, validates it against authoritative manifest data, assigns it only to the target, and rejects publication after the target has begun. A declared source is a context prerequisite, so the target waits for all of its sources to complete. No reusable finding means no file and no extra read.

## 10. Worker isolation

A worker receives:

- exactly one task definition;
- the global file only when it exists;
- only the scoped files listed under `Assigned execution context` in that task definition.
- only target-specific files listed under `Assigned validated learnings` in that task definition.

The worker must:

1. read the task definition first;
2. read every assigned context file;
3. read every assigned validated-learning file after the plan-time context files;
4. read no unassigned context/learning file or other planning artifact;
5. never edit context or learning files;
6. report the exact plan-relative paths in `context_files_read` and `learning_files_read`.

The orchestrator rejects a completion report when either declared read list does not exactly match the task assignment. This prevents silent omission and accidental context leakage.

Fresh worker processes still provide the main context isolation. Progressive plan-time files preserve stable cross-task constraints; validated learning files preserve only narrow post-validation discoveries that would otherwise be expensive to rediscover.

## 11. Review and replanning

The independent plan reviewer must set `contexts_minimal` to `true` only after verifying that:

- global items are relevant to every TODO;
- each scoped item is relevant to every assigned TODO and no others;
- single-task information remains in the task definition;
- no item duplicates request, plan, study, or another context file unnecessarily;
- every item has useful `source_refs`;
- omissions are deliberate;
- context files contain no mutable execution status.
- every learning edge is directional, narrow, and justified by specific similarity rather than generic framework reuse;
- no target receives a learning file after its first attempt;
- learning files remain concise, grounded, target-specific, and free of transcripts.

If execution changes a shared invariant, task grouping, or evidence source, stop downstream work and replan. Regenerate context files from the revised schema rather than hand-editing them.
