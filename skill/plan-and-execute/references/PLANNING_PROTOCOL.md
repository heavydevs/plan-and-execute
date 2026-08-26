# Deep planning protocol

## Contents

1. Planning outcome
2. Resolve and inventory the complete request
3. Pass the adaptive study gate
4. Build the requirements inventory
5. Decompose recursively
6. Design progressive execution context
7. Review the plan independently
8. Pass deterministic quality gates
9. Replan when execution disproves the study or plan

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
- every TODO has one coherent outcome and an independent validation path;
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

Read [ADAPTIVE_STUDY.md](ADAPTIVE_STUDY.md) and create `/tmp/study-spec.json` before drafting requirements or TODOs.

### 3.1 Identify material questions

List questions whose answers can change:

- architecture or ownership;
- compatibility or public contracts;
- data or migration order;
- security or authorization;
- provider, protocol, or dependency behavior;
- task boundaries or dependencies;
- acceptance criteria or validation commands.

Give every question a stable id, importance, status, evidence ids, resolution, and planning impact. A ready study may not contain open questions. High-importance questions must be resolved rather than assumed.

### 3.2 Study internal repository evidence first

Inspect relevant:

- agent and repository instructions;
- README files, architecture documents, ADRs, and module boundaries;
- build files, dependency manifests, and generated-code rules;
- production code near the requested behavior;
- existing tests, fixtures, and test conventions;
- schemas, migrations, interfaces, protocols, and public APIs;
- CI commands and release validation;
- recent history when it explains compatibility or design choices.

Record every material internal source with a repository location, concrete finding, and planning impact. Internal study is mandatory even when the orchestrator already knows the technology.

Use read-only exploration subagents for independent workstreams when helpful. The orchestrator must synthesize their findings instead of forwarding raw logs.

### 3.3 Decide on external research adaptively

After the first repository scan, explicitly evaluate every trigger:

- the user requested research or verification;
- the domain is unfamiliar;
- behavior is version-sensitive;
- behavior is security-sensitive;
- behavior may have changed recently;
- the repository lacks a material contract;
- evidence conflicts;
- a technology or provider choice is required;
- a wrong assumption would be high risk.

When any trigger is true, research authoritative external sources. Prefer official documentation, standards, research papers, and vendor advisories. Match the exact repository version or date where possible. Record source authority, version/date, finding, and planning impact.

When every trigger is false, external research is not required. Record a substantive rationale explaining why repository evidence is sufficient. Do not browse merely because the request is large.

If required evidence cannot be obtained or a material contradiction remains, mark research `blocked`, keep the study not ready, and stop planning.

### 3.4 Synthesize evidence

Translate evidence into exact strings for:

- planning constraints;
- derived requirements;
- risks;
- validation implications.

Every internal source finding must later appear exactly in `request_analysis.repository_findings`. Every external source finding must later appear exactly in `request_analysis.research_findings`.

Every synthesized constraint, requirement, and risk must be copied exactly into the corresponding plan field. Every validation implication must appear in a task acceptance criterion, implementation note, or validation command.

### 3.5 Review and validate study sufficiency

Use a fresh study reviewer whenever supported. Check internal coverage, trigger honesty, source quality, contradiction resolution, question resolution, planning impact, and the stopping rule.

Validate before drafting requirements or TODOs:

```bash
python <skill-dir>/scripts/studyctl.py validate \
  --spec /tmp/study-spec.json
```

Do not continue until this command passes.

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
- further splitting would create artificial handoffs or repeated context loading.

Rate each executable TODO `low`, `medium`, or `high`. `Extreme` is invalid. A `high` task needs a substantive atomicity rationale explaining why further splitting would weaken implementation or validation.

Avoid file-by-file microtasks. Keep tightly coupled edits together when they implement one behavior and share one validation boundary.

Keep `TODO.md` terse: exactly one status line per task. Store evidence, requirements, complexity, routing, dependencies, validation, and atomicity details elsewhere.

## 6. Design progressive execution context

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

Write the explicit decision in schema-v3 `execution_context`, including a substantive rationale when global context is omitted. File paths and task `context_files` assignments are generated by `planctl.py`.

## 7. Review the plan independently

After drafting the plan, start a fresh planning reviewer whenever supported. Give it:

- the complete user request;
- compact study evidence and synthesis;
- the requirements inventory;
- the draft task graph;
- the proposed global/scoped context decision;
- the decomposition and context-minimality rules in this file.

Do not assign implementation. Ask the reviewer to find:

- missing or distorted requirements;
- study findings that were not translated into the plan;
- unsupported assumptions;
- oversized or mixed-outcome TODOs;
- unnecessary microtasks;
- missing dependencies or cycles;
- weak acceptance criteria;
- validations that do not prove requirements;
- unsafe autostart actions;
- missing regression, compatibility, migration, or rollout coverage;
- global items not needed by every TODO;
- scoped files with too broad or too narrow assignment;
- duplicated, ungrounded, or overly verbose context.

Revise until no unresolved findings remain. A schema-v3 plan is approved only when all five checks are true:

- `coverage_complete`;
- `tasks_atomic`;
- `dependencies_valid`;
- `validations_sufficient`;
- `contexts_minimal`.

Use a strong planning model for difficult multi-workstream changes. Use maximum capability when architecture, security, concurrency, data migration, or repeated review failures justify it.

## 8. Pass deterministic quality gates

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
- incomplete plan review or failed `contexts_minimal`;
- missing, duplicated, oversized, tampered, or incorrectly assigned context artifacts;
- dependency cycles;
- missing acceptance criteria or validation commands.

Do not autostart when any command fails.

## 9. Replan when execution disproves the study or plan

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
6. regenerate global and scoped context assignments from the revised task graph;
7. reattach the study and run every quality gate;
8. resume only after all gates pass.

Do not hide new evidence or scope inside a worker report. Do not silently broaden a TODO.
