# Plan specification (schema v4)

## Contents

1. Quality model
2. Root fields
3. Request analysis fields
4. Requirement fields
5. Progressive execution context
6. Plan review fields
7. Task fields
8. Recursive decomposition rules
9. Complete example
10. Quality checklist
11. Legacy plans

## 1. Quality model

Create a directed acyclic graph of bounded executable TODOs only after the complete request, repository, and material external behavior have been studied.

Schema v4 deterministically checks:

- request-part-to-requirement-to-task traceability;
- concrete request and repository analysis;
- explicit task complexity and atomicity;
- rejection of executable `extreme` work;
- an approved independent review;
- empty material open questions before autostart;
- dependency, acceptance, and validation integrity;
- an explicit decision to create or omit global worker context;
- strict assignment of scoped context to only the TODOs that need it;
- concise, grounded, non-duplicated context artifacts;
- reviewer approval that `contexts_minimal` and `context_boundaries_sound` are true;
- explicit context-cohesion evidence for every TODO;
- at least one stable resumable subtask per TODO;
- directional, predeclared, target-specific learning relationships and tamper-resistant generated artifacts.

The schema cannot prove semantic perfection. Combine it with [ADAPTIVE_STUDY.md](ADAPTIVE_STUDY.md), [PLANNING_PROTOCOL.md](PLANNING_PROTOCOL.md), [EXECUTION_CONTEXT.md](EXECUTION_CONTEXT.md), and independent review.

## 2. Root fields

| Field | Required | Meaning |
|---|---:|---|
| `title` | yes | Human-readable plan title. |
| `summary` | yes | Overall desired outcome. |
| `language` | no | Handoff language; default `auto`. |
| `request_analysis` | yes | Evidence that the complete request and repository were studied. |
| `requirements` | yes | Non-empty inventory of explicit and necessary derived requirements. |
| `global_constraints` | no | Repository, compatibility, security, or rollout constraints. |
| `execution_context` | yes in v3+ | Explicit minimal global/scoped worker-context decision. |
| `plan_review` | yes | Approved independent plan review. |
| `autostart` | no | Start after all gates pass; default `true`. |
| `cleanup_on_success` | no | Delete planning artifacts after the final summary; default `true`. |
| `tasks` | yes | Non-empty array of executable TODO objects. |

## 3. Request analysis fields

`request_analysis` becomes `ANALYSIS.md`.

| Field | Required | Meaning |
|---|---:|---|
| `request_parts` | yes | Every distinct requested outcome or workstream, with stable ids such as `P001`. |
| `repository_findings` | yes | Concrete findings from repository inspection. |
| `research_decision` | yes | What external research was needed, or why none was needed. |
| `research_findings` | no | Material conclusions from authoritative external sources. |
| `assumptions` | no | Bounded assumptions used to make the plan executable. |
| `risks` | no | Technical, compatibility, rollout, data, security, or operational risks. |
| `open_questions` | no | Material unresolved questions; must be empty when `autostart` is true. |
| `decomposition_strategy` | yes | Workstreams, boundaries, dependency order, and granularity rationale. |

Preferred request part:

```json
{
  "id": "P001",
  "text": "Preserve the public API while adding the new behavior"
}
```

Do not use findings as raw file or link lists. Record conclusions that change planning.

## 4. Requirement fields

```json
{
  "id": "R001",
  "text": "Preserve the existing public API",
  "source": "user",
  "priority": "must",
  "request_part_ids": ["P001"]
}
```

| Field | Required | Meaning |
|---|---:|---|
| `id` | no | Stable id; omitted ids normalize to `R001`, `R002`, and so on. |
| `text` | yes | One clear requirement. |
| `source` | no | `user`, `repository`, `research`, or `inferred`; default `user`. |
| `priority` | no | `must`, `should`, or `could`; default `must`. |
| `request_part_ids` | yes for `user` | Request parts that produced the requirement. |

Every request part must map to at least one requirement. Every requirement must map to at least one task. Use `inferred` only for work required to make an explicit request safe, compatible, testable, or operable.

## 5. Progressive execution context

`execution_context` is required in schema v3+ even when no context file is created. Read [EXECUTION_CONTEXT.md](EXECUTION_CONTEXT.md) before authoring it.

### 5.1 Global decision

```json
{
  "global": {
    "decision": "omit",
    "rationale": "Every non-obvious constraint is task-specific, so a shared file would duplicate task definitions.",
    "items": []
  }
}
```

| Field | Required | Meaning |
|---|---:|---|
| `decision` | yes | `create` or `omit`. |
| `rationale` | yes | Why universal shared context is or is not needed. |
| `items` | yes | Empty for `omit`; non-empty for `create`. |
| `file` | generated | `CONTEXT.md` for `create`, otherwise `null`. Do not author manually. |

Create global context only for information needed by every executable TODO.

### 5.2 Context item

```json
{
  "id": "G001",
  "kind": "constraint",
  "text": "Preserve the existing public API and wire format throughout the implementation.",
  "necessity": "Every TODO may affect behavior observed through the public contract, so each worker needs this boundary.",
  "source_refs": ["request:P001", "ADR-004"]
}
```

| Field | Required | Meaning |
|---|---:|---|
| `id` | no | Stable item id; generated by position when omitted. |
| `kind` | yes | `fact`, `constraint`, `decision`, `interface`, or `validation`. |
| `text` | yes | One operational line, 15–280 characters. |
| `necessity` | yes | One line explaining why every assigned TODO needs it. |
| `source_refs` | yes | One to four evidence references. |

The rendered context file includes the concise `text` and compact source references. `necessity` stays in the manifest/review metadata to avoid repeated prompt cost.

### 5.3 Scoped context

```json
{
  "id": "oauth-rollout",
  "title": "OAuth rollout contract",
  "rationale": "Only the authentication and migration TODOs participate in the dual-login transition.",
  "task_ids": [1, 2],
  "items": [
    {
      "id": "C001",
      "kind": "interface",
      "text": "Password login remains available until the OAuth migration completion flag is enabled.",
      "necessity": "Both assigned TODOs must implement the same rollout boundary.",
      "source_refs": ["request:P002", "study:I006"]
    }
  ]
}
```

| Field | Required | Meaning |
|---|---:|---|
| `id` | yes | Lowercase kebab-case identifier, used to generate `contexts/<id>.md`. |
| `title` | yes | Short file title. |
| `rationale` | yes | Why exactly the assigned TODOs share this context. |
| `task_ids` | yes | At least two known TODO ids and fewer than all TODOs. |
| `items` | yes | Non-empty list of context items. |
| `file` | generated | `contexts/<id>.md`. Do not author manually. |

Context for a single TODO belongs in that task definition. Context for all TODOs belongs in global context.

### 5.4 Limits and generated assignments

The validator enforces:

- at most 8 global items;
- at most 8 scoped files;
- at most 8 items per scoped file;
- at most 24 items across all files;
- at most 3,200 rendered characters per file;
- no duplicated context text across files;
- exact task-to-file assignment;
- no tampering or unassigned references.

`planctl.py` generates each task's `context_files` array and writes the same paths under `Assigned execution context` in its definition. Do not include `context_files` in the input spec.

## 6. Plan review fields

`plan_review` becomes `PLAN_REVIEW.md`.

| Field | Required | Meaning |
|---|---:|---|
| `status` | yes | Must be `approved`. |
| `reviewer` | yes | Separate reviewer or explicit second-pass route. |
| `rounds` | yes | Integer of at least 1. |
| `coverage_complete` | yes | Must be `true`. |
| `tasks_atomic` | yes | Must be `true`. |
| `dependencies_valid` | yes | Must be `true`. |
| `validations_sufficient` | yes | Must be `true`. |
| `contexts_minimal` | yes in v3+ | Must be `true`; confirms global/scoped context is necessary, grounded, and narrow. |
| `context_boundaries_sound` | yes in v4 | Must be `true`; confirms each TODO is a useful fresh-context boundary, independent domains were split, and subtasks/learning edges do not hide oversized work. |
| `unresolved_findings` | yes | Must be empty. |
| `notes` | yes | What the reviewer checked and what changed. |

The reviewer must verify that global items apply to every TODO, scoped items apply to every assigned TODO and no others, one-task information remains in the task definition, and omission is deliberate.

## 7. Task fields

| Field | Required | Meaning |
|---|---:|---|
| `id` | no | Numeric or short string id; numeric ids normalize to three digits. |
| `title` | yes | One bounded outcome. |
| `objective` | yes | Exact result the worker must produce. |
| `requirement_ids` | yes | Non-empty list of requirements this task satisfies. |
| `complexity` | yes | `low`, `medium`, or `high`; `extreme` is rejected. |
| `atomicity_rationale` | yes | Why this is one executable TODO. |
| `scope.in` | no | Work explicitly included. |
| `scope.out` | no | Work explicitly excluded. |
| `scope.expected_files` | no | Repository-relative files likely to change. |
| `dependencies` | no | Task ids that must complete first. |
| `implementation_guidance` | no | Non-obvious task-specific constraints or approach. |
| `acceptance_criteria` | yes | Observable success conditions. |
| `validation_commands` | yes | Commands run from the repository root. |
| `provider` | no | `auto`, `claude`, `codex`, `gemini`, `qwen`, `kimi`, or `trae`; default `auto`. Optional providers are execution backends, not default install targets. |
| `model_tier` | no | `economy`, `standard`, `strong`, or `max`. |
| `reasoning_effort` | no | `low`, `medium`, `high`, `xhigh`, or `max`. |
| `allow_provider_fallback` | no | Permit provider fallback; default `true`. |
| `related_task_reads` | no | Narrow allowlist of other task definitions. |
| `max_attempts` | no | Technical-failure limit; default `8`. |
| `context_boundary` | yes in v4 | Why the work benefits from one fresh worker context and what adjacent concerns were deliberately excluded. |
| `subtasks` | yes in v4 | Stable resumable checkpoints inside the parent TODO. At least one must be required. |
| `learning_targets` | no in v4 | Directional declarations for narrow validated findings that may help untouched future TODOs. |
| `context_files` | generated | Exact global/scoped plan-time context assigned to the task. Do not author. |
| `learning_files` | generated | Exact validated source-task learning artifacts assigned to the target. Do not author. |

Every expected file path must be repository-relative and must not contain `..`.

A high-complexity task needs a substantive rationale explaining why further splitting would create artificial handoffs or weaker validation.

### 7.1 Context boundary

```json
{
  "context_boundary": {
    "shared_context": [
      "The controller, service, entity, and focused tests implement one person-lifecycle invariant."
    ],
    "why_one_todo": "The same domain rules and validation evidence are needed across every layer, so one fresh worker context avoids an artificial handoff.",
    "separate_from": [
      "Store CRUD is independent and belongs to another TODO because it shares no domain invariant or focused validation."
    ]
  }
}
```

`shared_context` must name concrete retained context, not generic framework familiarity. `why_one_todo` must explain why that context is useful throughout the TODO. `separate_from` records adjacent independent concerns deliberately kept outside the boundary.

### 7.2 Resumable subtasks

```json
{
  "subtasks": [
    {
      "id": "S001",
      "title": "Implement the person domain contract",
      "objective": "Entity and service rules satisfy the bounded acceptance criteria."
    },
    {
      "id": "S002",
      "title": "Expose and validate the person controller",
      "objective": "Focused controller tests pass against the completed domain contract."
    }
  ]
}
```

Subtasks are durable checkpoints inside one parent TODO. They may be strings or objects, normalize to stable ids, and default to `required: true`. At least one required subtask is mandatory. Runtime status is generated in `manifest.json`; do not author `status`, timestamps, or history in the input spec.

### 7.3 Directional learning targets

```json
{
  "learning_targets": [
    {
      "task_id": "004",
      "reason": "Both TODOs use the same repository transaction helper, and the target can reuse one validated deadlock-avoidance procedure without reading the source worker history.",
      "topics": ["transaction ordering", "focused deadlock regression"]
    }
  ]
}
```

Targets must be later TODOs. The declaration authorizes only the named topics; it does not pre-create a file. It also makes every declared source a context prerequisite for that target, preventing target execution before the source either publishes a validated artifact or completes with nothing reusable. After deterministic source validation, the controller may create one concise `learnings/<source>-to-<target>.md` artifact only when the source reports a grounded reusable finding and the target has never started. `learning_files`, `published_learning_files`, and `learning_artifacts` are generated state.

## 8. Recursive decomposition rules

Split a candidate task when any of these changes independently:

- subsystem or responsibility;
- data model, service logic, protocol, UI, or rollout layer;
- migration phase or compatibility boundary;
- validation environment or safety gate;
- independently failing outcome;
- implementation ownership or required tooling.
- usefulness of retained AI context: split when reasoning from one concern would not materially help the other.

Tasks that usually require decomposition include:

- schema migration + service integration + backfill + rollout;
- backend API + frontend UI + analytics instrumentation;
- architecture discovery + implementation;
- framework upgrade + breaking refactor + broad test migration;
- security redesign + credential rotation + production cutover.

Do not split inseparable edits that implement one behavior and share one validation set. Avoid file-by-file TODOs that force repeated rediscovery.

Independent person and store CRUDs normally become separate TODOs even when both follow the same framework pattern. A controller, service, entity, repository, and focused tests for one domain may remain together when they share one rule set and validation boundary.

After decomposition, decide execution context from the resulting task graph. Do not use a global context file to compensate for oversized or ambiguous tasks.

## 9. Complete example

```json
{
  "title": "Implement sample feature",
  "summary": "Create two bounded changes and verify them.",
  "language": "English",
  "request_analysis": {
    "request_parts": [
      {
        "id": "P001",
        "text": "Create an implementation marker"
      },
      {
        "id": "P002",
        "text": "Verify the marker contains the requested value"
      }
    ],
    "repository_findings": [
      "The sample repository is intentionally minimal and has no existing implementation files."
    ],
    "research_decision": "No external research is needed for a local marker-file test.",
    "research_findings": [],
    "assumptions": [
      "The test environment provides POSIX shell commands."
    ],
    "risks": [
      "A broad file edit could accidentally touch unrelated files."
    ],
    "open_questions": [],
    "decomposition_strategy": "Separate file creation from content verification so each outcome has one deterministic check."
  },
  "requirements": [
    {
      "id": "R001",
      "text": "Create implemented.txt without unrelated changes",
      "source": "user",
      "priority": "must",
      "request_part_ids": [
        "P001"
      ]
    },
    {
      "id": "R002",
      "text": "Ensure implemented.txt contains the word implemented",
      "source": "user",
      "priority": "must",
      "request_part_ids": [
        "P002"
      ]
    }
  ],
  "global_constraints": [
    "Do not edit unrelated files"
  ],
  "execution_context": {
    "global": {
      "decision": "create",
      "rationale": "Both TODOs must preserve the same narrow file boundary, so one concise shared invariant prevents inconsistent edits without repeating it in each task.",
      "items": [
        {
          "id": "G001",
          "kind": "constraint",
          "text": "Only implemented.txt may be created or changed by this sample plan.",
          "necessity": "Every TODO can modify the marker file, and each must avoid unrelated working-tree changes throughout execution.",
          "source_refs": [
            "request:P001",
            "global_constraints[0]"
          ]
        }
      ]
    },
    "scoped": []
  },
  "plan_review": {
    "status": "approved",
    "reviewer": "fresh planning reviewer",
    "rounds": 1,
    "coverage_complete": true,
    "tasks_atomic": true,
    "dependencies_valid": true,
    "validations_sufficient": true,
    "contexts_minimal": true,
    "context_boundaries_sound": true,
    "unresolved_findings": [],
    "notes": [
      "Every requirement maps to a task and both tasks have independent validation."
    ]
  },
  "tasks": [
    {
      "id": 1,
      "title": "Create implementation marker",
      "objective": "Create implemented.txt in the repository root.",
      "requirement_ids": [
        "R001"
      ],
      "complexity": "low",
      "atomicity_rationale": "This task has one file-creation outcome and one direct existence check.",
      "context_boundary": {
        "shared_context": [
          "Creating implemented.txt and proving its existence share one marker-file contract."
        ],
        "why_one_todo": "The file creation and its direct existence check are one cohesive outcome; splitting them would create an artificial handoff without reducing context.",
        "separate_from": [
          "Marker content verification belongs to TODO 002 and needs no creation transcript."
        ]
      },
      "scope": {
        "in": [
          "Create the marker file"
        ],
        "out": [
          "No unrelated refactoring"
        ],
        "expected_files": [
          "implemented.txt"
        ]
      },
      "acceptance_criteria": [
        "implemented.txt exists"
      ],
      "validation_commands": [
        "test -f implemented.txt"
      ],
      "subtasks": [
        {
          "id": "S001",
          "title": "Create the bounded marker file",
          "objective": "implemented.txt exists without unrelated repository changes."
        }
      ],
      "provider": "auto",
      "model_tier": "economy",
      "reasoning_effort": "low",
      "learning_targets": [
        {
          "task_id": "002",
          "reason": "TODO 002 can reuse only the validated marker-file diagnosis from TODO 001 without inheriting its worker transcript.",
          "topics": [
            "marker creation order",
            "missing-file diagnosis"
          ]
        }
      ]
    },
    {
      "id": 2,
      "title": "Verify marker contents",
      "objective": "Ensure implemented.txt contains the expected word.",
      "requirement_ids": [
        "R002"
      ],
      "complexity": "low",
      "atomicity_rationale": "This task has one content outcome and one deterministic grep check.",
      "context_boundary": {
        "shared_context": [
          "Correcting marker contents and running grep share one deterministic content contract."
        ],
        "why_one_todo": "The content correction and grep validation use the same file invariant, while the worker needs only repository state rather than TODO 001 conversation history.",
        "separate_from": [
          "Initial marker creation belongs to TODO 001 and is already represented on disk."
        ]
      },
      "dependencies": [
        1
      ],
      "scope": {
        "in": [
          "Check or update implemented.txt"
        ],
        "out": [
          "No unrelated files"
        ],
        "expected_files": [
          "implemented.txt"
        ]
      },
      "acceptance_criteria": [
        "The marker contains implemented"
      ],
      "validation_commands": [
        "grep -q implemented implemented.txt"
      ],
      "subtasks": [
        {
          "id": "S001",
          "title": "Verify and correct marker contents",
          "objective": "implemented.txt contains the expected word and the grep check passes."
        }
      ],
      "provider": "auto",
      "model_tier": "economy",
      "reasoning_effort": "low"
    }
  ]
}
```

## 10. Quality checklist

Before creation, confirm:

- every request part maps to a requirement;
- every requirement maps to a TODO;
- every TODO maps back to requirements;
- no task is `extreme`;
- high-complexity tasks have substantive atomicity rationale;
- acceptance criteria are observable;
- validation commands prove the criteria;
- open questions are empty when autostarting;
- global context is either explicitly omitted or universally necessary;
- scoped files serve at least two and fewer than all TODOs;
- single-task information stays in its task definition;
- context items are concise, grounded, stable, and non-duplicated;
- all six v4 review checks, including `contexts_minimal` and `context_boundaries_sound`, are true;
- every TODO has a substantive `context_boundary`;
- every TODO has one or more stable subtasks and at least one required checkpoint;
- each learning target points forward, names narrow topics, and is justified by specific reusable reasoning;
- unresolved review findings are empty.

After creation, run:

```bash
python <skill-dir>/scripts/planctl.py validate --plan .ai-work/<plan-id>
python <skill-dir>/scripts/planctl.py audit --plan .ai-work/<plan-id>
```

## 11. Legacy plans

`planctl.py` can read schema-v1, schema-v2, and schema-v3 plans created by earlier releases. They keep their original validation contract; schema-v1/v2 do not require `execution_context` or `contexts_minimal`, and schema-v3 does not require v4 context boundaries, subtasks, or learning relationships.

New plans always use schema v4. Do not backfill context into a legacy plan by hand. Replan through the current protocol when progressive execution context is needed.
