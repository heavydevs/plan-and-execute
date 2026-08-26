# Adaptive pre-plan study gate

## Contents

1. Purpose
2. Position in the workflow
3. Mandatory internal study
4. Conditional external research
5. Material questions and evidence
6. Synthesis into the plan
7. Independent review and stopping rule
8. Study specification
9. Commands
10. Re-entering the gate during execution

## 1. Purpose

Use this gate before drafting requirements or executable TODOs. Its purpose is not to collect the largest possible amount of information. Its purpose is to resolve the questions that can materially change architecture, compatibility, task boundaries, risk, or validation.

Internal repository study is always required. External research is adaptive: perform it only when one or more explicit triggers are true. A local, well-defined change may proceed without web research when repository evidence is sufficient and the decision is recorded.

The gate has two checks:

1. `studyctl.py validate` proves that the request and repository were studied, that the external-research decision was deliberate, and that the evidence is sufficient to begin planning.
2. `studyctl.py attach` runs after plan creation and proves that the study findings were copied into the plan's constraints, requirements, risks, and task validation.

Do not draft requirements or TODOs before the first check passes. Do not autostart execution before the attachment check and the normal plan gates pass.

## 2. Position in the workflow

Use this order:

```text
complete request
      |
      v
material questions
      |
      v
mandatory internal repository study
      |
      v
external trigger assessment
      |-----------------------------|
      v                             v
research required              research not needed
      |                             |
      v                             |
authoritative external sources     |
      |-----------------------------|
      v
synthesis + independent study review
      |
      v
studyctl validate
      |
      v
requirements and TODO plan
      |
      v
studyctl attach + validate-plan
      |
      v
planctl validate + audit
      |
      v
execution
```

The first repository pass should happen before the external-research decision. Repository evidence often answers the question directly, identifies the exact dependency version, or narrows the external search to the relevant official documentation.

## 3. Mandatory internal study

Inspect enough repository evidence to understand the real change surface. Select only categories that are relevant, but do not skip a relevant category merely because the request sounds familiar.

Possible evidence categories:

- `instructions`: agent instructions, repository conventions, contribution rules, or local policy files;
- `architecture`: README files, architecture documents, ADRs, module boundaries, and ownership boundaries;
- `implementation`: production code and runtime behavior near the requested change;
- `tests`: existing tests, fixtures, test style, failure modes, and regression expectations;
- `build`: dependency manifests, generated-code rules, packaging, and build commands;
- `schema`: database schemas, migrations, serialization formats, and data compatibility;
- `interface`: public APIs, protocols, events, commands, and integration contracts;
- `ci`: validation entry points, supported runtimes, and release checks;
- `history`: recent commits or decisions that explain compatibility or design constraints;
- `other`: any concrete internal source that changes the plan.

Each internal source must record:

- a stable evidence id such as `I001`;
- its category;
- a concrete repository location;
- the finding, not merely that a file was opened;
- the planning impact.

Weak evidence:

```json
{
  "location": "src/",
  "finding": "Looked at the source code",
  "planning_impact": "Implement the feature"
}
```

Useful evidence:

```json
{
  "id": "I001",
  "kind": "implementation",
  "location": "src/delivery.py:84-151; tests/test_delivery.py:120-230",
  "finding": "Delivery retries keep failed records pending and the focused tests assert a second provider attempt.",
  "planning_impact": "Preserve the pending-on-failure transition and keep retry compatibility in a separately validated task."
}
```

## 4. Conditional external research

Evaluate every trigger explicitly after the initial internal scan.

| Trigger | Set to true when |
| --- | --- |
| `user_requested` | The request explicitly asks for external research, verification, current information, or supplied external sources that must be checked. |
| `unfamiliar_domain` | The orchestrator lacks enough reliable knowledge to choose or validate the approach. |
| `version_sensitive` | Correct behavior depends on an exact library, runtime, API, protocol, or product version. |
| `security_sensitive` | Authentication, authorization, cryptography, secrets, sandboxing, vulnerability behavior, or security guidance materially affects the solution. |
| `current_behavior` | The fact may have changed recently, including provider APIs, product capabilities, standards, or supported versions. |
| `repository_gap` | The repository does not define a material contract needed for planning. |
| `conflicting_evidence` | Internal documentation, code, tests, or prior assumptions disagree. |
| `technology_selection` | The plan requires choosing among tools, frameworks, providers, or architectural alternatives. |
| `high_risk` | A wrong assumption could cause data loss, incompatible rollout, security exposure, or costly rework. |

Decision rules:

- `required`: at least one trigger is true and authoritative external sources were consulted.
- `not_needed`: every trigger is false and the rationale explains why internal evidence is sufficient.
- `blocked`: at least one trigger is true, but required evidence cannot be obtained or a material contradiction remains. The study must not be ready for planning.

When research is required:

1. Prefer primary official documentation, standards, research papers, and vendor advisories.
2. Match the repository's exact dependency or protocol version whenever possible.
3. Record the publication date or version used.
4. Record the conclusion that changes planning, not a raw link dump.
5. Explain why the source is authoritative for the question.
6. Reconcile conflicts. Do not silently choose the source that best matches the desired implementation.

External research is not automatically required merely because a task is large. It is required when external facts can materially change the plan.

## 5. Material questions and evidence

Before collecting evidence, list the questions that can change the solution. Examples:

- Which module owns the state transition?
- What compatibility contract must be preserved?
- Which exact runtime or dependency version is supported?
- Does the provider guarantee idempotency for this operation?
- Which migration order supports rolling deployment?
- Which validation command proves the behavior?

Give every question a stable id such as `Q001`, importance, status, evidence ids, resolution, and planning impact.

Question status:

- `resolved`: evidence supports a concrete answer;
- `assumed`: bounded evidence supports a low- or medium-impact assumption;
- `open`: the question is unresolved and may block planning.

A study marked ready may not contain open questions. A high-importance question may not remain assumed; resolve it or mark the study blocked.

## 6. Synthesis into the plan

Evidence is useful only when it changes the plan. Synthesize findings into any applicable category. After the TODO graph exists, a small subset of these grounded findings may also become progressive execution-context items under [EXECUTION_CONTEXT.md](EXECUTION_CONTEXT.md), but only when every assigned TODO needs them:

- `planning_constraints`: exact constraints that must be copied into `global_constraints`;
- `derived_requirements`: exact requirement text that must appear in the requirements inventory;
- `risks`: exact risks that must be copied into `request_analysis.risks`;
- `validation_implications`: phrases that must appear in a task acceptance criterion, implementation note, or validation command.

Also copy every internal `finding` exactly into `request_analysis.repository_findings`. Copy every external-source `finding` exactly into `request_analysis.research_findings`.

This exact-text rule is intentional. It makes `studyctl.py attach` able to prove deterministically that the study affected the plan instead of becoming an unused research note. Do not copy the entire study into `CONTEXT.md`; context items remain one-line operational derivatives grounded through `source_refs`.

Example synthesis:

```json
{
  "planning_constraints": [
    "Do not hold a database transaction across the provider call."
  ],
  "derived_requirements": [
    "Keep failed first attempts retryable."
  ],
  "risks": [
    "A non-backward-compatible migration could break rolling deployment."
  ],
  "validation_implications": [
    "Run the focused delivery retry tests."
  ]
}
```

When writing the plan spec:

- copy the constraint string exactly into `global_constraints`;
- create a requirement with the derived-requirement string exactly as its `text`;
- copy the risk string exactly into `request_analysis.risks`;
- include the validation-implication phrase in at least one task acceptance criterion, implementation note, or validation command.

## 7. Independent review and stopping rule

Review the study in a fresh subagent or process whenever supported. The reviewer must check:

- internal repository coverage is sufficient for the request;
- every external trigger was evaluated honestly;
- the external-research decision is justified;
- source authority, date, and version are adequate;
- material contradictions are resolved;
- high-impact questions are resolved;
- evidence was translated into planning constraints, requirements, risks, or validation;
- further research is unlikely to change the plan materially.

Record the reviewer, all five boolean checks, and notes. If the runtime cannot create a fresh reviewer, perform an explicit second pass with the strongest available route and record that limitation.

The stopping rule must explain why the evidence is now sufficient. Stop when:

- all high-impact questions are resolved;
- relevant repository surfaces have been inspected;
- required external sources are authoritative and version-appropriate;
- contradictions are resolved or explicitly block planning;
- the findings have concrete planning impact;
- more searching is unlikely to change architecture, task boundaries, compatibility, risk, or validation.

Do not continue research merely to accumulate links. Do not stop because a time budget expired while a high-impact question remains unresolved.

## 8. Study specification

Use [study-spec.example.json](study-spec.example.json) as the starting shape.

Required root fields:

| Field | Meaning |
| --- | --- |
| `schema_version` | Study schema version; currently `1`. |
| `request_summary` | Compact statement of the complete requested outcome. |
| `material_questions` | Questions that can materially change the plan. |
| `internal_sources` | Concrete repository evidence; always non-empty. |
| `external_research` | Trigger assessment, decision, rationale, and sources. |
| `synthesis` | Exact plan constraints, requirements, risks, and validation implications. |
| `review` | Independent sufficiency review. |

The validator rejects shallow placeholders, unknown evidence ids, missing trigger assessments, unjustified `not_needed` decisions, required research without sources, high-impact assumptions, ready studies with unresolved questions, and failed review checks.

## 9. Commands

Validate before drafting requirements or TODOs:

```bash
python <skill-dir>/scripts/studyctl.py validate \
  --spec /tmp/study-spec.json
```

Inspect a blocked study without allowing planning to start:

```bash
python <skill-dir>/scripts/studyctl.py validate \
  --spec /tmp/study-spec.json \
  --allow-not-ready
```

Render a human-readable preview:

```bash
python <skill-dir>/scripts/studyctl.py render \
  --spec /tmp/study-spec.json \
  --output /tmp/STUDY.md
```

After creating the plan, attach the evidence and verify exact integration:

```bash
python <skill-dir>/scripts/studyctl.py attach \
  --spec /tmp/study-spec.json \
  --plan .ai-work/<plan-id>
```

Validate the preserved gate before execution or after resume:

```bash
python <skill-dir>/scripts/studyctl.py validate-plan \
  --plan .ai-work/<plan-id>
```

The attachment adds:

```text
.ai-work/<plan-id>/
|-- study.json
|-- STUDY.md
`-- manifest.json  # study_gate metadata and hash
```

The normal `planctl.py validate` and `planctl.py audit` checks still run after the study gate.

## 10. Re-entering the gate during execution

Execution can disprove the original study. Re-enter this protocol when a worker discovers:

- an undocumented external contract;
- a different dependency version than the one researched;
- a material contradiction between code and tests;
- a new security, migration, compatibility, or data risk;
- a task boundary that depends on an unresolved question.

Stop downstream dispatch, update the study specification, repeat independent review, revise the plan, attach the updated study, and run every quality gate again. Do not hide new scope or evidence inside a worker report.
