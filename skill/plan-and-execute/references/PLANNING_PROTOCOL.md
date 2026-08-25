# Deep planning protocol

## Contents

1. Planning outcome
2. Study the complete request
3. Study the repository and subject
4. Build the requirements inventory
5. Decompose recursively
6. Review the plan independently
7. Pass the deterministic quality gate
8. Replan when execution disproves the plan

## 1. Planning outcome

Produce an implementation plan only after understanding every requested outcome, relevant repository constraint, material dependency, risk, and validation need. Planning is complete only when:

- every distinct request part appears in `request_analysis.request_parts` with a stable id;
- every request-part id maps to at least one explicit or necessary derived requirement;
- every requirement has a stable id;
- every requirement id maps to at least one executable TODO;
- every TODO has one coherent outcome and an independent validation path;
- no executable TODO is rated `extreme`;
- a separate review pass approves coverage, atomicity, dependencies, and validation;
- `planctl.py validate` and `planctl.py audit` pass.

Do not confuse a long checklist with a good plan. Prefer the smallest set of tasks that preserves clear ownership, independent verification, and low context overlap.

## 2. Study the complete request

Read the full request before drafting tasks. Extract and record:

- requested deliverables and behaviors;
- explicit constraints and non-goals;
- compatibility, security, performance, migration, rollout, and data requirements;
- requested tests and implicit regression coverage;
- external actions or safety gates;
- ambiguous terms that materially change the solution.

Treat a request containing several large changes as several planning workstreams. Do not collapse them into a generic TODO such as “implement everything,” “complete the migration,” or “finish backend and frontend.”

Resolve ambiguity from the repository, existing documentation, tests, or authoritative external documentation whenever possible. Record a bounded assumption when the ambiguity is low risk. Ask for user input only when a high-impact decision cannot be inferred safely.

## 3. Study the repository and subject

Inspect enough of the repository to understand the real change surface before selecting task boundaries. At minimum, inspect relevant:

- agent or repository instructions;
- README, architecture documents, ADRs, and module boundaries;
- build files, dependency manifests, and generated-code rules;
- production code near the requested behavior;
- existing tests and test conventions;
- schemas, migrations, interfaces, protocols, and public APIs;
- CI commands and validation entry points;
- recent history when it explains conventions or compatibility constraints.

Use read-only research subagents for independent workstreams when that reduces context pressure. Have the orchestrator synthesize their findings rather than forwarding raw logs.

Research external documentation when the request depends on unfamiliar, version-sensitive, security-sensitive, or current behavior. Prefer primary official documentation and record the finding. When external research is unnecessary, record the reason in `request_analysis.research_decision`; do not leave the field absent.

## 4. Build the requirements inventory

Create a complete ordered inventory before tasks. Give each request part a stable id such as `P001`, then give each requirement a stable id such as `R001`.

Classify each requirement by:

- `source`: `user`, `repository`, `research`, or `inferred`;
- `priority`: `must`, `should`, or `could`.

Use `inferred` only for work necessary to make an explicit request safe, testable, compatible, or operable. Do not silently expand product scope.

After drafting tasks, create traceability in both directions:

- every request part must be covered by one or more requirement `request_part_ids`;
- every requirement must be covered by one or more task `requirement_ids`;
- every task must cover at least one requirement;
- acceptance criteria must demonstrate the mapped requirements;
- validation commands must provide evidence for the acceptance criteria.

The deterministic plan validator rejects uncovered request parts, uncovered requirements, unknown request-part ids, and unknown requirement ids.

## 5. Decompose recursively

Start with major request workstreams, then repeatedly split each candidate task until every leaf is independently implementable and verifiable.

Split a candidate task when any of these is true:

- it contains more than one independently failing outcome;
- it crosses unrelated subsystems or ownership boundaries;
- it combines discovery, architecture selection, implementation, migration, rollout, and broad regression testing in one unit;
- one part could be completed and validated without the others;
- it requires different tools, environments, or safety gates;
- it contains multiple risky migrations or compatibility transitions;
- a worker would need future task definitions to understand what success means;
- failure would not reveal which part of the task was wrong;
- the task would be rated `extreme`.

Useful boundaries often appear between:

- data model or schema changes;
- domain or service behavior;
- API or protocol integration;
- UI or client behavior;
- migration or backfill phases;
- automated tests at different levels;
- rollout, observability, and compatibility checks.

Stop splitting only when all are true:

- the TODO has one coherent outcome;
- one worker can understand it from one definition file;
- dependencies and interfaces are explicit;
- the likely change surface is bounded;
- acceptance criteria are observable;
- deterministic validation can decide success;
- additional splitting would create artificial handoffs or repeated context loading.

Rate each executable TODO `low`, `medium`, or `high`. `extreme` is not a valid leaf and is rejected. A `high` task requires a substantive `atomicity_rationale` explaining why further splitting would weaken independent implementation or validation.

Avoid the opposite failure mode: do not turn every file edit or assertion into a separate TODO. Keep tightly coupled edits together when they implement one behavior and share one validation set.

## 6. Review the plan independently

After drafting the plan, start a fresh planning reviewer in a separate subagent or process whenever the runtime supports it. Give the reviewer:

- the complete user request;
- the compact request/repository analysis;
- the requirements inventory;
- the draft task graph;
- the decomposition rules in this file.

Do not give the reviewer implementation responsibility. Ask it to search for:

- missing or distorted requirements;
- unsupported assumptions;
- oversized or mixed-outcome TODOs;
- unnecessary microtasks;
- missing dependencies or cycles;
- weak acceptance criteria;
- validations that do not prove the requirement;
- unsafe autostart actions;
- missing regression, compatibility, or rollout coverage.

Revise the plan and repeat review until there are no unresolved findings. Record the final review in `plan_review`. A review is approved only when all four checks are true:

- `coverage_complete`;
- `tasks_atomic`;
- `dependencies_valid`;
- `validations_sufficient`.

Use a strong planning model for large multi-workstream changes. Use max capability when architecture, security, concurrency, data migration, or repeated planning-review failures justify it. Do not use an economy model to create or approve a difficult plan merely to save credits.

## 7. Pass the deterministic quality gate

Create the plan only after analysis and review:

```bash
python <skill-dir>/scripts/planctl.py create \
  --repo-root . \
  --spec /tmp/plan-spec.json
```

Then run both checks:

```bash
python <skill-dir>/scripts/planctl.py validate --plan .ai-work/<plan-id>
python <skill-dir>/scripts/planctl.py audit --plan .ai-work/<plan-id>
```

The quality gate rejects, among other problems:

- missing request or repository analysis;
- missing or duplicate request parts or requirements;
- request parts without requirement coverage;
- uncovered requirements;
- tasks without requirement ids;
- unknown requirement references;
- missing complexity or atomicity rationale;
- `extreme` executable tasks;
- unresolved open questions with autostart;
- an unapproved or incomplete plan review;
- dependency cycles;
- missing acceptance criteria or validation commands.

Do not autostart execution when either command fails.

## 8. Replan when execution disproves the plan

Treat planning as a strong hypothesis, not permission to force an oversized task through. If execution reveals a material missing requirement, wrong dependency, or task that should be split:

1. stop dispatching downstream tasks;
2. preserve the concrete evidence and current implementation state;
3. return the affected task to a safe pending or blocked state;
4. revise the plan through the same analysis, traceability, review, and validation process;
5. resume only after the revised plan passes the quality gate.

Do not hide newly discovered scope inside a worker report or silently broaden a TODO.
