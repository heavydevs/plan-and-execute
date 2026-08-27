# Deep planning protocol

## Contents

1. Planning outcome
2. Resolve and inventory the complete request
3. Pass the adaptive study gate
4. Build the requirements inventory
5. Decompose recursively
6. Design progressive execution context and selective learning
7. Define resumable subtasks
8. Review the plan independently
9. Pass deterministic quality gates
10. Replan when execution disproves the study or plan

## 1. Planning outcome

Produce an implementation plan only after understanding every requested outcome, relevant repository constraint, material external contract, risk, and validation need.

Planning is complete only when:

- every distinct request part has a stable id such as `P001`;
- every material question was resolved or safely bounded by evidence;
- internal repository study is concrete and non-empty;
- every external-research trigger was explicitly evaluated;
- required external research uses authoritative version-appropriate sources;
- `studyctl.py validate` passed before requirements or TODOs were drafted;
- every study finding was translated into plan constraints, requirements, risks, or validation;
- every request part maps to one or more requirements;
- every requirement maps to one or more executable TODOs;
- every TODO has one coherent outcome, an independent validation path, and a context surface whose retained reasoning is useful throughout the TODO;
- every TODO declares why it deserves one fresh worker context and what unrelated work was kept outside it;
- every TODO has a stable resumable subtask checklist;
- any cross-TODO execution learning is directional, predeclared, concise, validated, and target-specific;
- shared execution context was explicitly omitted or reduced to grounded items needed by every assigned TODO;
- single-task information remains inside the task definition;
- no executable TODO is rated `extreme`;
- separate study and plan review passes approve sufficiency, context minimality, and quality;
- `studyctl.py validate-plan`, `planctl.py validate`, and `planctl.py audit` all pass.

Do not confuse a long checklist or link collection with a good plan. Prefer the smallest evidence set and task graph that resolve material uncertainty, preserve traceability, and support independent verification.

## 2. Resolve and inventory the complete request

Resolve the request source before studying or planning:

- for no-argument invocation, wait for the user to save and confirm the generated request draft;
- for a caller-provided file, validate and read the entire file while preserving the source;
- for inline input, treat the complete invocation text as authoritative.

When `REQUEST.md` exists, preserve its user-authored body unchanged as planning evidence. Do not treat template headings as requirements.

Read the full request before drafting tasks. Extract and record:

- requested deliverables and observable behavior;
- explicit constraints, examples, and non-goals;
- compatibility, security, performance, migration, rollout, and data requirements;
- requested tests and implicit regression expectations;
- external actions or safety gates;
- referenced versions, providers, standards, URLs, and documentation;
- ambiguous terms that can materially change the solution.

Give each distinct request part a stable id such as `P001`. Treat several large changes as several workstreams. Never collapse them into a generic task such as "implement everything" or "finish the migration."

Resolve ambiguity from repository evidence or authoritative sources whenever possible. Record bounded low-risk assumptions. Ask for user input only when a high-impact decision cannot be inferred safely.

## 3. Pass the adaptive study gate

Read [ADAPTIVE_STUDY.md](ADAPTIVE_STUDY.md) and create `/tmp/study-spec.json` before drafting requirements or TODOs. The gate is mandatory; repository or internet study is not.

### 3.1 Classify before broad exploration

Classify the request as `simple`, `medium`, or `complex` from the complete request and only the minimum explicit context needed to understand it.

- `simple`: direct, routine, low-risk, no material architecture/compatibility/external uncertainty;
- `medium`: bounded but ownership, symbols, tests, or one exact contract needs focused discovery;
- `complex`: cross-cutting architecture, migration, security, data integrity, ownership, provider choice, or high-risk uncertainty can change the plan.

Do not use request length, file count, or number of independent direct edits as a proxy for complexity.

### 3.2 Choose the least expensive internal depth

For `simple`, use `none`. Do not scan the repository before planning. Record `internal_study.plan_finding` explaining why broad study would not change the solution.

For `medium`, choose automatically:

- `related_packages` when ownership is clear enough to stay inside a bounded module neighborhood;
- `workspace_keywords` when repository-wide filtering is needed to locate ownership, tests, schemas, integrations, or configuration.

Search before reading. Open high-signal matches first and expand only when a concrete finding requires another dependency/test hop.

For `complex`, ask the user before broad study using exactly these internal choices:

1. **Pacotes relacionados**
2. **Busca por palavras-chave em todo o workspace**
3. **Projeto completo**

Record the choice with `selection_source: user`. Reuse an explicit fixed choice already present in the request instead of asking again.

### 3.3 Choose external depth

Evaluate material external triggers: explicit user request, unfamiliar domain, version-sensitive behavior, security sensitivity, current behavior, repository gaps, conflicting evidence, technology selection, or high risk.

For `simple`, external depth is `none`; if a material external trigger exists, classify at least `medium`.

For `medium`, choose automatically:

- `none` when no trigger is material;
- `focused` when exact official/versioned evidence can change the solution.

For `complex`, ask the user in the same chat turn as the internal question using exactly:

1. **Sem estudo externo**
2. **Pesquisa focalizada**
3. **Pesquisa ampla**

Honor the selected depth. A no-external-study choice does not authorize invented facts; block planning if a high-impact question remains unresolved.

### 3.4 Record evidence only when collected

When repository sources are actually opened, record stable ids, concrete locations, findings, and planning impacts. When external research is performed, prefer exact-version official documentation, standards, research papers, and vendor advisories, and record conclusions rather than link dumps.

A simple fast path may have:

- zero `internal_sources`;
- zero `material_questions`;
- zero external sources;
- empty synthesis lists.

Every schema-v2 study still records `complexity_assessment`, `internal_study`, external depth/selection, and a stopping reason.

### 3.5 Synthesize and review proportionally

Copy `internal_study.plan_finding` exactly into `request_analysis.repository_findings`. Also copy every actual internal source finding and every external source finding exactly into the matching plan analysis fields. Translate only material evidence into constraints, derived requirements, risks, and validation implications.

Match review cost to study cost:

- simple: concise self-check;
- medium: separate review only when uncertainty, conflict, or risk warrants it;
- complex: fresh review whenever supported.

Stop when more evidence is unlikely to change architecture, compatibility, task boundaries, risk, or validation.

Validate before drafting requirements or TODOs:

```bash
python <skill-dir>/scripts/studyctl.py validate \
  --spec /tmp/study-spec.json
```

Schema v2 is required for newly created studies. Schema-v1 attachments remain valid for existing plans.

## 4. Build the requirements inventory

After the study gate passes, create a complete ordered requirements inventory. Give every requirement a stable id such as `R001`.

Classify each requirement by:

- `source`: `user`, `repository`, `research`, or `inferred`;
- `priority`: `must`, `should`, or `could`.

Use `inferred` only for work necessary to make an explicit request safe, compatible, testable, or operable. Do not silently expand product scope.

Copy study synthesis exactly:

- constraints into `global_constraints`;
- derived requirements into requirement `text`;
- risks into `request_analysis.risks`;
- validation implications into task criteria, guidance, or commands.

Create bidirectional traceability:

- every request part must be covered by one or more requirement `request_part_ids`;
- every requirement must be covered by one or more task `requirement_ids`;
- every task must cover at least one requirement;
- acceptance criteria must demonstrate mapped requirements;
- validation commands must provide evidence for acceptance criteria.

The deterministic validator rejects uncovered request parts, uncovered requirements, unknown ids, and tasks without mapped requirements.

## 5. Decompose recursively

Start with request workstreams, then split repeatedly until every leaf is independently implementable and verifiable.

Split a candidate task when any of these is true:

- it contains more than one independently failing outcome;
- it crosses unrelated subsystems or ownership boundaries;
- it combines discovery, architecture selection, implementation, migration, rollout, and broad regression testing;
- one part could be completed and validated without the others;
- it requires different tools, environments, external contracts, or safety gates;
- it contains multiple risky migrations or compatibility transitions;
- a worker would need future task definitions to know what success means;
- failure would not reveal which part was wrong;
- the worker context accumulated for one concern would add little or no value to the other concern;
- the concerns share only a framework pattern, naming convention, or architectural layer but not domain rules, invariants, files, failure diagnosis, or validation;
- the task would be rated `extreme`.

Useful boundaries often appear between:

- schema and data migration;
- domain or service behavior;
- API or protocol integration;
- UI or client behavior;
- backfill and rollout phases;
- automated tests at different levels;
- observability, compatibility, and release checks.

Stop splitting only when all are true:

- the TODO has one coherent outcome;
- one worker can understand it from one definition file;
- dependencies and interfaces are explicit;
- the likely change surface is bounded;
- acceptance criteria are observable;
- deterministic validation can decide success;
- the same decisions, invariants, source surface, debugging evidence, and validation reasoning are useful across the full TODO;
- further splitting would create artificial handoffs or repeated context loading.

Rate each executable TODO `low`, `medium`, or `high`. `Extreme` is invalid. A `high` task needs a substantive atomicity rationale explaining why further splitting would weaken implementation or validation.

Avoid file-by-file microtasks. Keep tightly coupled edits together when they implement one behavior and share one validation boundary.

### 5.1 Use context utility, not visual similarity

Two CRUDs are not one TODO merely because both have a controller, service, entity, repository, and tests. A person CRUD and a store CRUD normally become separate TODOs when:

- their entities and business rules are independent;
- neither implementation changes the other's contract;
- their focused tests fail independently;
- a worker solving one would not gain useful reasoning for the other beyond generic framework knowledge.

Conversely, keep one domain's controller, service, entity, persistence mapping, and focused tests together when they implement one invariant and the same context is required to reason about all layers. Do not produce controller-per-file or method-per-file TODOs.

Every schema-v4 task records this judgment in `context_boundary`:

- `shared_context`: the concrete decisions, invariants, files, or validation reasoning useful across the full TODO;
- `why_one_todo`: why one fresh worker context improves implementation or validation;
- `separate_from`: adjacent concerns intentionally kept outside the boundary.

The field is review evidence, not a prose quota. A weak statement such as “these files are related” is insufficient.

Keep `TODO.md` terse: exactly one status line per task. Store evidence, requirements, complexity, routing, dependencies, validation, and atomicity details elsewhere.

## 6. Design progressive execution context and selective learning

After the draft task graph exists, read [EXECUTION_CONTEXT.md](EXECUTION_CONTEXT.md) and classify each candidate cross-task fact.

Use this hierarchy:

1. information indispensable to every TODO may enter global `CONTEXT.md`;
2. information indispensable to at least two but fewer than all TODOs may enter one scoped `contexts/<topic>.md` file;
3. information for a single TODO must remain in that task definition;
4. everything else must be omitted.

Omission is the default. Do not create a context artifact merely because information is relevant to the project. A fresh worker must be materially more likely to implement or validate incorrectly without it.

Every context item must have:

- a stable id and one allowed kind;
- one operational line, not narrative prose;
- a concise necessity explaining why every assigned TODO needs it;
- one to four `source_refs` grounded in request, repository, research, requirement, or decision evidence.

Reject:

- request or plan summaries;
- duplicated task guidance;
- generic engineering advice;
- mutable TODO status;
- facts easily rediscovered from the assigned task and nearby source;
- overlap between global and scoped files;
- a scoped file for a single TODO;
- a scoped file assigned to every TODO.

Write the explicit decision in schema-v4 `execution_context`, including a substantive rationale when global context is omitted. File paths and task `context_files` assignments are generated by `planctl.py`.

### 6.1 Keep plan-time context separate from execution learnings

Global and scoped context files are immutable plan-time artifacts. Do not append discoveries from one worker to `CONTEXT.md` or `contexts/*.md`.

When a completed TODO may teach a later similar TODO something expensive to rediscover, declare a directional `learning_targets` edge during planning. Each edge names:

- the future `task_id`;
- why the two tasks are similar enough for the specific knowledge transfer;
- the narrow `topics` that may cross the boundary.

The target must be a later TODO. The declaration becomes a context prerequisite: the target cannot start until every declared source for that target completes, even when no ordinary implementation dependency exists. Do not create bidirectional “similar task” groups or let workers choose arbitrary recipients after execution.

After the source TODO passes deterministic validation, it may report concise reusable items of kind `code`, `procedure`, `decision`, `pitfall`, or `validation`, each with concrete repository or command references. The controller then creates at most one target-specific file such as `learnings/001-to-004.md` and assigns it only to TODO 004.

Reject learning transfer when:

- the target was not predeclared;
- the target already started or has any prior attempt;
- the item has no concrete reference;
- the content is speculative, generic, verbose, or merely repeats the task definition;
- the file contains logs, report dumps, plan files, or worker chat history.

An empty learning report creates no file and costs no future tokens. A source-task reset removes unconsumed artifacts; once a target has started, the source cannot be reset in a way that silently rewrites that target's assigned knowledge.

## 7. Define resumable subtasks

Every schema-v4 TODO must contain one or more stable subtasks. They are checkpoints inside one parent context boundary, not replacements for top-level decomposition.

Use subtasks for durable progress such as:

- update the bounded implementation contract;
- migrate one cohesive state representation;
- add the focused regression fixture;
- run and repair the task-local validation set.

Do not use subtasks to hide independent domains or independently deployable outcomes that should be separate top-level TODOs.

Each subtask has a stable id, title, optional objective, and `required` flag. `manifest.json` is authoritative; the Markdown checklist is regenerated. Workers may change state only through `planctl.py subtask-start`, `subtask-complete`, or `subtask-reset`.

On interruption, completed subtasks stay complete and only an `in_progress` subtask returns to `pending`. Parent completion is rejected while any required subtask remains incomplete. This lets another fresh AI resume from disk without previous chat history.

## 8. Review the plan independently

After drafting the plan, start a fresh planning reviewer whenever supported. Give it:

- the complete user request;
- compact study evidence and synthesis;
- the requirements inventory;
- the draft task graph;
- every task's `context_boundary`, subtask checklist, and directional learning targets;
- the proposed global/scoped context decision;
- the decomposition and context-minimality rules in this file.

Do not assign implementation. Ask the reviewer to find:

- missing or distorted requirements;
- study findings that were not translated into the plan;
- unsupported assumptions;
- oversized or mixed-outcome TODOs;
- unnecessary microtasks;
- independent concerns kept together merely because they use the same framework pattern;
- context boundaries whose retained reasoning is not useful across the whole TODO;
- top-level work hidden as subtasks;
- broad, bidirectional, undeclared, or token-heavy learning relationships;
- missing dependencies or cycles;
- weak acceptance criteria;
- validations that do not prove requirements;
- unsafe autostart actions;
- missing regression, compatibility, migration, or rollout coverage;
- global items not needed by every TODO;
- scoped files with too broad or too narrow assignment;
- duplicated, ungrounded, or overly verbose context.

Revise until no unresolved findings remain. A schema-v4 plan is approved only when all six checks are true:

- `coverage_complete`;
- `tasks_atomic`;
- `dependencies_valid`;
- `validations_sufficient`;
- `contexts_minimal`;
- `context_boundaries_sound`.

Use a strong planning model for difficult multi-workstream changes. Use maximum capability when architecture, security, concurrency, data migration, or repeated review failures justify it.

## 9. Pass deterministic quality gates

Create the plan only after study and review:

```bash
python <skill-dir>/scripts/planctl.py create \
  --repo-root . \
  --spec /tmp/plan-spec.json
```

Attach the validated study. This checks exact integration into the plan:

```bash
python <skill-dir>/scripts/studyctl.py attach \
  --spec /tmp/study-spec.json \
  --plan .ai-work/<plan-id>
```

Then run all gates:

```bash
python <skill-dir>/scripts/studyctl.py validate-plan --plan .ai-work/<plan-id>
python <skill-dir>/scripts/planctl.py validate --plan .ai-work/<plan-id>
python <skill-dir>/scripts/planctl.py audit --plan .ai-work/<plan-id>
```

The combined gates reject, among other problems:

- missing or shallow internal evidence;
- an external-research decision without explicit trigger assessment;
- `not_needed` while any external trigger is true;
- required research without authoritative sources;
- high-impact questions left open or assumed;
- ready studies with failed review checks;
- study findings not copied into the plan;
- missing request or repository analysis;
- request parts or requirements without coverage;
- tasks without requirement ids;
- missing complexity or atomicity rationale;
- executable `extreme` tasks;
- unresolved plan questions with autostart;
- incomplete plan review or failed `contexts_minimal` / `context_boundaries_sound`;
- missing or shallow task context boundaries;
- missing, duplicate, invalid, or manually edited subtask state;
- backward, undeclared, already-consumed, oversized, or tampered learning artifacts;
- missing, duplicated, oversized, tampered, or incorrectly assigned context artifacts;
- dependency cycles;
- missing acceptance criteria or validation commands.

Do not autostart when any command fails.

## 10. Replan when execution disproves the study or plan

Treat study and planning as strong hypotheses, not permission to force an invalid task through. Re-enter the complete protocol when execution reveals:

- a material missing requirement or repository surface;
- a different dependency or protocol version;
- a new external contract or security constraint;
- conflicting implementation and test behavior;
- a wrong dependency;
- an oversized task that should be split.

Then:

1. stop dispatching downstream tasks;
2. preserve concrete evidence and current implementation state;
3. return the affected task to a safe pending or blocked state;
4. update the study spec and repeat study review;
5. revise requirements and tasks through full traceability and plan review;
6. regenerate task boundaries, subtasks, global/scoped context assignments, and directional learning relationships from the revised graph;
7. reattach the study and run every quality gate;
8. resume only after all gates pass.

Do not hide new evidence or scope inside a worker report. Do not silently broaden a TODO.
