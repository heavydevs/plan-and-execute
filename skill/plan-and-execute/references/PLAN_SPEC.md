# Plan specification (schema v3)

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

Schema v3 deterministically checks:

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
- reviewer approval that `contexts_minimal` is true.

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
| `execution_context` | yes in v3 | Explicit minimal global/scoped worker-context decision. |
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

`execution_context` is required in schema v3 even when no context file is created. Read [EXECUTION_CONTEXT.md](EXECUTION_CONTEXT.md) before authoring it.

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
| `contexts_minimal` | yes in v3 | Must be `true`; confirms global/scoped context is necessary, grounded, and narrow. |
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
| `provider` | no | `auto`, `claude`, or `codex`; default `auto`. |
| `model_tier` | no | `economy`, `standard`, `strong`, or `max`. |
| `reasoning_effort` | no | `low`, `medium`, `high`, `xhigh`, or `max`. |
| `allow_provider_fallback` | no | Permit provider fallback; default `true`. |
| `related_task_reads` | no | Narrow allowlist of other task definitions. |
| `max_attempts` | no | Technical-failure limit; default `8`. |
| `context_files` | generated | Exact global/scoped context assigned to the task. Do not author. |

Every expected file path must be repository-relative and must not contain `..`.

A high-complexity task needs a substantive rationale explaining why further splitting would create artificial handoffs or weaker validation.

## 8. Recursive decomposition rules

Split a candidate task when any of these changes independently:

- subsystem or responsibility;
- data model, service logic, protocol, UI, or rollout layer;
- migration phase or compatibility boundary;
- validation environment or safety gate;
- independently failing outcome;
- implementation ownership or required tooling.

Tasks that usually require decomposition include:

- schema migration + service integration + backfill + rollout;
- backend API + frontend UI + analytics instrumentation;
- architecture discovery + implementation;
- framework upgrade + breaking refactor + broad test migration;
- security redesign + credential rotation + production cutover.

Do not split inseparable edits that implement one behavior and share one validation set. Avoid file-by-file TODOs that force repeated rediscovery.

After decomposition, decide execution context from the resulting task graph. Do not use a global context file to compensate for oversized or ambiguous tasks.

## 9. Complete example

```json
{
  "title": "Add idempotent notification delivery",
  "summary": "Add database-backed idempotency, integrate it into delivery, and cover retries.",
  "language": "English",
  "request_analysis": {
    "request_parts": [
      {"id": "P001", "text": "Persist delivery idempotency keys"},
      {"id": "P002", "text": "Prevent duplicate sends while preserving retries"},
      {"id": "P003", "text": "Add deterministic automated coverage"}
    ],
    "repository_findings": [
      "Delivery already records provider attempts before updating final state.",
      "Database migrations must support rolling deployment.",
      "Focused service tests run through Maven selectors."
    ],
    "research_decision": "No external research is required because the repository defines the transaction, migration, and retry contracts.",
    "research_findings": [],
    "assumptions": ["The existing message id can seed the delivery key."],
    "risks": ["A non-backward-compatible migration could break rolling deployment."],
    "open_questions": [],
    "decomposition_strategy": "Separate persistence, service integration, and end-to-end regression because they have independent change and validation boundaries."
  },
  "requirements": [
    {
      "id": "R001",
      "text": "Reserve a delivery key atomically so it is accepted only once.",
      "source": "user",
      "priority": "must",
      "request_part_ids": ["P001", "P002"]
    },
    {
      "id": "R002",
      "text": "Keep a genuine failed first attempt retryable.",
      "source": "user",
      "priority": "must",
      "request_part_ids": ["P002"]
    },
    {
      "id": "R003",
      "text": "Add automated duplicate and retry coverage.",
      "source": "user",
      "priority": "must",
      "request_part_ids": ["P003"]
    }
  ],
  "global_constraints": [
    "Do not hold a database transaction across the provider call.",
    "Preserve unrelated working-tree changes."
  ],
  "execution_context": {
    "global": {
      "decision": "create",
      "rationale": "Every TODO must preserve rolling-deployment compatibility while working in the same repository state.",
      "items": [
        {
          "id": "G001",
          "kind": "constraint",
          "text": "Keep all schema and service changes compatible with rolling deployment.",
          "necessity": "Persistence, integration, and regression TODOs can each introduce incompatible assumptions.",
          "source_refs": ["request:P001", "repository:migration-policy"]
        }
      ]
    },
    "scoped": [
      {
        "id": "delivery-state-machine",
        "title": "Delivery state machine",
        "rationale": "Only persistence and service integration modify delivery state transitions.",
        "task_ids": [1, 2],
        "items": [
          {
            "id": "C001",
            "kind": "interface",
            "text": "A failed provider attempt must leave the delivery key retryable rather than completed.",
            "necessity": "Both persistence and service workers must implement the same failure transition.",
            "source_refs": ["request:P002", "tests/DeliveryRetryTest.java"]
          }
        ]
      }
    ]
  },
  "plan_review": {
    "status": "approved",
    "reviewer": "fresh strong-tier planning reviewer",
    "rounds": 2,
    "coverage_complete": true,
    "tasks_atomic": true,
    "dependencies_valid": true,
    "validations_sufficient": true,
    "contexts_minimal": true,
    "unresolved_findings": [],
    "notes": [
      "Confirmed every request part and requirement is covered.",
      "Restricted delivery-state context to TODOs 001 and 002.",
      "Confirmed the rolling-deployment item is universal and non-duplicative."
    ]
  },
  "autostart": true,
  "cleanup_on_success": true,
  "tasks": [
    {
      "id": 1,
      "title": "Add idempotency persistence",
      "objective": "Create the migration and repository operations for atomic delivery-key reservation.",
      "requirement_ids": ["R001", "R002"],
      "complexity": "medium",
      "atomicity_rationale": "The migration and repository methods form one persistence contract with one focused validation boundary.",
      "scope": {
        "in": ["Schema migration", "Atomic reservation repository methods"],
        "out": ["Do not change provider dispatch yet"],
        "expected_files": ["db/migrations/add_delivery_key.sql", "src/DeliveryRepository.java"]
      },
      "dependencies": [],
      "implementation_guidance": ["Do not hold a transaction across the provider call."],
      "acceptance_criteria": ["A key can be reserved exactly once.", "Failure leaves the key retryable."],
      "validation_commands": ["./mvnw -q -Dtest=DeliveryRepositoryTest test", "git diff --check"],
      "provider": "auto",
      "model_tier": "standard",
      "reasoning_effort": "medium"
    },
    {
      "id": 2,
      "title": "Integrate idempotency into delivery",
      "objective": "Use reservation before dispatch while preserving genuine retry behavior.",
      "requirement_ids": ["R001", "R002"],
      "complexity": "high",
      "atomicity_rationale": "Reservation, dispatch decision, and completion state are one service transition; splitting would leave unverifiable intermediate behavior.",
      "scope": {
        "in": ["Delivery service integration"],
        "out": ["Do not redesign the queue consumer"],
        "expected_files": ["src/DeliveryService.java", "test/DeliveryServiceTest.java"]
      },
      "dependencies": [1],
      "implementation_guidance": ["A duplicate key must not call the provider again."],
      "acceptance_criteria": ["Duplicate delivery is acknowledged without a second send.", "A failed first attempt remains retryable."],
      "validation_commands": ["./mvnw -q -Dtest=DeliveryServiceTest test", "git diff --check"],
      "provider": "claude",
      "model_tier": "strong",
      "reasoning_effort": "high",
      "related_task_reads": [1]
    },
    {
      "id": 3,
      "title": "Add end-to-end retry coverage",
      "objective": "Cover duplicate, failed-first-attempt, and successful-retry scenarios.",
      "requirement_ids": ["R002", "R003"],
      "complexity": "medium",
      "atomicity_rationale": "The scenarios share one fixture and prove one externally observable retry contract.",
      "scope": {
        "in": ["Deterministic end-to-end tests"],
        "out": ["No production redesign"],
        "expected_files": ["test/DeliveryE2ETest.java"]
      },
      "dependencies": [2],
      "implementation_guidance": [],
      "acceptance_criteria": ["Tests fail without idempotency and pass with it.", "Tests use no timing sleeps."],
      "validation_commands": ["./mvnw -q -Dtest=DeliveryE2ETest test", "git diff --check"],
      "provider": "auto",
      "model_tier": "standard",
      "reasoning_effort": "medium"
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
- all five v3 review checks, including `contexts_minimal`, are true;
- unresolved review findings are empty.

After creation, run:

```bash
python <skill-dir>/scripts/planctl.py validate --plan .ai-work/<plan-id>
python <skill-dir>/scripts/planctl.py audit --plan .ai-work/<plan-id>
```

## 11. Legacy plans

`planctl.py` can read schema-v1 and schema-v2 plans created by earlier releases. They keep their original validation contract and do not require `execution_context` or `contexts_minimal`.

New plans always use schema v3. Do not backfill context into a legacy plan by hand. Replan through the current protocol when progressive execution context is needed.
