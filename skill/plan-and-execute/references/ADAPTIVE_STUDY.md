# Adaptive pre-plan study gate

## Contents

1. Goal
2. Triage before repository study
3. Fixed study choices for complex requests
4. Simple fast path
5. Medium focused path
6. Complex user-selected path
7. External research triggers
8. Evidence and synthesis
9. Review and stopping rule
10. Study specification and commands
11. Re-entering the gate

## 1. Goal

Spend context only where it can change the implementation. Do not equate a long request or many direct edits with architectural complexity. Classify the request before broad repository inspection, then choose the least expensive study depth that can still produce a reliable plan.

The gate always records the decision, but the study itself may be empty. A simple request can pass with zero repository sources and zero external sources. A medium request gets bounded discovery. A complex request asks the user to choose both internal and external study depth before broad exploration begins.

`studyctl.py validate` validates the classification, the selected study strategy, evidence when present, and readiness for planning. `studyctl.py attach` later proves that the study decision and any findings reached the plan.

## 2. Triage before repository study

Read the complete request first. Before opening broad repository context, classify it as `simple`, `medium`, or `complex`.

### Simple

Use `simple` when all material behavior is explicit and routine:

- target behavior and acceptance are direct;
- no architectural choice is required;
- no migration, security boundary, concurrency boundary, or compatibility contract is uncertain;
- external facts or exact current versions cannot materially change the implementation;
- validation is obvious or already specified.

The number of edits is not a complexity signal by itself. Twenty independent text/config changes can remain simple if each is direct and low-risk.

### Medium

Use `medium` when the solution is bounded but some repository discovery is useful:

- ownership or exact files are not fully known;
- a related package/module and its tests must be located;
- symbols or keywords should be searched across the workspace;
- a small number of related files or contracts must be inspected;
- focused external verification may be needed for a version-sensitive fact.

Medium requests must not ask the user to choose study depth. Choose automatically and keep the search bounded.

### Complex

Use `complex` when broader context may change architecture, task boundaries, risk, or validation, for example:

- multiple subsystems share one invariant or rollout boundary;
- migrations, compatibility, security, authorization, concurrency, or data integrity are material;
- ownership is unclear across packages;
- a technology/provider/architecture choice is required;
- external contracts materially affect design;
- wrong assumptions could create substantial rework or production risk.

Quantity alone never makes a request complex.

Record the classification in `complexity_assessment` with a concise rationale and concrete signals. Do not perform a repository-wide scan merely to justify the classification.

## 3. Fixed study choices for complex requests

For a `complex` request, ask both questions in the same chat turn before broad study. Use native choice UI when available; otherwise present exactly these fixed labels.

### Internal study

1. **Pacotes relacionados** — inspect only packages/modules directly related to the request, plus their focused tests, build/configuration, schemas, and interfaces.
2. **Busca por palavras-chave em todo o workspace** — search the whole workspace for request terms, symbols, APIs, table names, events, or error strings, then open only the highest-signal matches and their immediate dependency/test neighborhood.
3. **Projeto completo** — systematically inspect repository structure, instructions, architecture, major modules, build/CI, schemas/interfaces, tests, and relevant history across the project. Do not literally dump or read every file; sample and drill down according to evidence.

### External study

1. **Sem estudo externo** — do not browse external sources. Proceed only if unresolved high-impact questions can still be resolved internally; otherwise mark the study blocked.
2. **Pesquisa focalizada** — research only the exact official documentation, standard, advisory, or versioned contract directly needed by the request.
3. **Pesquisa ampla** — research the exact official sources plus relevant release notes, standards, advisories, authoritative issue/repository material, or research needed to compare alternatives and risks.

Do not ask open-ended “how much should I study?” questions. Do not invent additional options. If the user already specified one of these preferences in the request, record it as the user selection and do not ask again.

After asking, end the turn before broad study. Resume after the user chooses.

## 4. Simple fast path

For a simple request:

- set `internal_study.selection_source` to `automatic`;
- set `internal_study.depth` to `none`;
- keep `internal_sources` empty;
- keep `material_questions` empty when there is no material uncertainty;
- set external depth to `none` and all external triggers to false;
- allow synthesis lists to remain empty when no study finding creates a plan constraint;
- record a concise `internal_study.plan_finding` explaining why study was skipped.

The plan must copy `internal_study.plan_finding` exactly into `request_analysis.repository_findings`. This preserves an auditable decision without pretending repository evidence was collected.

Reading a file explicitly supplied by the user or opening the exact target during implementation is not a mandatory pre-plan study pass.

## 5. Medium focused path

For a medium request, automatically choose one internal depth:

- `related_packages` when ownership is already fairly clear and only the local module neighborhood matters;
- `workspace_keywords` when locating ownership, symbols, tests, integrations, or configuration requires repository-wide filtering.

Use search/filtering tools before opening files. Prefer symbol search, filename search, grep/ripgrep, code search, import/reference search, or repository search. Open only the strongest matches first, then expand one dependency/test hop when evidence justifies it.

Do not escalate to a full-project study merely because many matching files exist. Escalate the request to `complex` only when the discovered coupling or risk can materially change architecture or task boundaries; then ask the fixed user choices before continuing broad exploration.

For external research on a medium request:

- use `none` when no external trigger is true;
- use `focused` automatically when one or more triggers are material;
- use `broad` only when the user explicitly selected it.

## 6. Complex user-selected path

For a complex request:

- `internal_study.selection_source` must be `user`;
- internal depth must be exactly `related_packages`, `workspace_keywords`, or `full_project`;
- `external_research.selection_source` must be `user`;
- external depth must be exactly `none`, `focused`, or `broad`.

Honor the selected depth. Do not silently broaden it. If execution or study reveals a material unknown outside the selected scope, explain the gap and re-enter this gate rather than quietly consuming more context.

A user choice of **Sem estudo externo** does not permit inventing external facts. Resolve high-impact questions internally, record a bounded low-risk assumption, or mark the study blocked.

## 7. External research triggers

Evaluate these triggers after classification. For medium requests, use them to decide between automatic `none` and `focused`. For complex requests, record them even though the user chooses depth.

| Trigger | Set to true when |
| --- | --- |
| `user_requested` | The user explicitly asked for external research or verification. |
| `unfamiliar_domain` | Reliable implementation depends on knowledge the orchestrator does not have. |
| `version_sensitive` | Correct behavior depends on an exact library, runtime, API, protocol, or product version. |
| `security_sensitive` | Security guidance materially affects the solution. |
| `current_behavior` | The fact may have changed recently. |
| `repository_gap` | The repository does not define a material contract needed for planning. |
| `conflicting_evidence` | Repository evidence conflicts. |
| `technology_selection` | The solution requires choosing among technologies/providers/architectures. |
| `high_risk` | A wrong external assumption could cause data loss, incompatibility, exposure, or costly rework. |

When external research is performed, prefer primary official documentation, standards, research papers, vendor advisories, and exact-version sources. Record findings, not link dumps.

## 8. Evidence and synthesis

For every internal source that is actually opened, record:

- stable id such as `I001`;
- kind;
- concrete repository location;
- finding;
- planning impact.

For every external source, record stable id, source type, title, publisher, HTTPS URL, version/date, finding, planning impact, and why it is authoritative.

Material questions need stable ids only when there are material questions. A simple fast-path study may legitimately have none.

Translate evidence into only the planning effects it creates:

- `planning_constraints`;
- `derived_requirements`;
- `risks`;
- `validation_implications`.

A simple fast path may leave all four lists empty.

When building the plan:

- copy `internal_study.plan_finding` exactly into `request_analysis.repository_findings` for study schema v2;
- also copy every actual internal source `finding` exactly into `request_analysis.repository_findings`;
- copy every external source `finding` exactly into `request_analysis.research_findings`;
- copy synthesized constraints, requirements, risks, and validation implications into their corresponding plan fields.

## 9. Review and stopping rule

Match review cost to study cost:

- simple fast path: a concise orchestrator self-check is sufficient;
- medium: use a separate reviewer only when evidence conflicts, risk rises, or the plan boundary is uncertain;
- complex: use a fresh reviewer whenever supported.

Always stop when additional evidence is unlikely to change architecture, compatibility, task boundaries, risk, or validation. “More files exist” is not a reason to keep reading.

A ready study may not contain open high-impact questions. A high-importance question may not remain merely assumed.

## 10. Study specification and commands

Use study schema v2 for new plans. Schema v1 remains supported for existing plans.

Example: [study-spec.example.json](study-spec.example.json)

Validate before drafting executable TODOs:

```bash
python <skill-dir>/scripts/studyctl.py validate \
  --spec /tmp/study-spec.json
```

Attach after plan creation:

```bash
python <skill-dir>/scripts/studyctl.py attach \
  --spec /tmp/study-spec.json \
  --plan .ai-work/<plan-id>
```

Validate attached evidence on resume:

```bash
python <skill-dir>/scripts/studyctl.py validate-plan \
  --plan .ai-work/<plan-id>
```

## 11. Re-entering the gate

Reclassify and reconsider depth when execution reveals:

- an unexpected subsystem or ownership boundary;
- a contradictory public contract;
- a new migration/security/data-integrity risk;
- an exact version requirement not previously known;
- a task boundary that no longer isolates coherent context.

Do not automatically jump to full-project or broad external research. Re-run the same triage. If the request is now complex and the required depth would exceed the user's prior selection, ask the fixed choices again.
