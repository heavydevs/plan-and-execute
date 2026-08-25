# Plan specification (schema v2)

## Contents

1. Quality model
2. Root fields
3. Request analysis fields
4. Requirement fields
5. Plan review fields
6. Task fields
7. Recursive decomposition rules
8. Complete example
9. Quality checklist
10. Legacy plans

## 1. Quality model

Create a directed acyclic graph of bounded executable tasks only after studying the full request, repository, and material external behavior. Schema v2 adds deterministic checks for:

- a recorded request/repository analysis with stable request-part ids;
- a complete requirements inventory with stable ids;
- request-part-to-requirement-to-task traceability;
- task complexity and atomicity rationale;
- rejection of `extreme` executable tasks;
- an approved separate plan-review pass;
- empty material open questions before autostart;
- dependency, acceptance, and validation integrity.

The schema cannot prove semantic perfection by itself. Combine it with the planning procedure in [PLANNING_PROTOCOL.md](PLANNING_PROTOCOL.md) and an independent reviewer.

## 2. Root fields

| Field | Required | Meaning |
|---|---:|---|
| `title` | yes | Human-readable plan title. |
| `summary` | yes | Overall desired outcome. |
| `language` | no | Handoff language, such as `Portuguese (Brazil)`; default `auto`. |
| `request_analysis` | yes | Evidence that the full request and relevant repository were studied. |
| `requirements` | yes | Non-empty inventory of explicit and necessary derived requirements. |
| `global_constraints` | no | Repository, compatibility, security, or rollout constraints. |
| `plan_review` | yes | Approved result of the independent plan-review pass. |
| `autostart` | no | Start after validation and audit; default `true`. |
| `cleanup_on_success` | no | Delete planning artifacts after final summary; default `true`. |
| `tasks` | yes | Non-empty array of executable task objects. |

## 3. Request analysis fields

`request_analysis` is required and becomes `ANALYSIS.md` in the plan directory.

| Field | Required | Meaning |
|---|---:|---|
| `request_parts` | yes | Non-empty list covering every distinct requested outcome or workstream. Use objects with `id` and `text`; plain strings receive ordered ids `P001`, `P002`, and so on. |
| `repository_findings` | yes | Non-empty list of concrete findings from repository inspection. For a greenfield repository, record that fact and its consequences. |
| `research_decision` | yes | Explain what external research was needed, or why none was needed. |
| `research_findings` | no | Material findings from authoritative external sources. |
| `assumptions` | no | Bounded assumptions used to make the plan executable. |
| `risks` | no | Technical, compatibility, rollout, data, security, or operational risks. |
| `open_questions` | no | Material unresolved questions. Must be empty when `autostart` is true. |
| `decomposition_strategy` | yes | Explain the workstreams, boundaries, dependency order, and why the chosen TODO granularity is appropriate. |

Each request part becomes a traceability anchor. Prefer this form:

```json
{
  "id": "P001",
  "text": "Preserve the public API while adding the new behavior"
}
```

Do not use `research_findings` as a raw link dump. Record the conclusion that affects implementation.

## 4. Requirement fields

Prefer requirement objects:

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
| `id` | no | Stable id. Omitted ids normalize by order to `R001`, `R002`, and so on. |
| `text` | yes | One clear requirement. |
| `source` | no | `user`, `repository`, `research`, or `inferred`; default `user`. |
| `priority` | no | `must`, `should`, or `could`; default `must`. |
| `request_part_ids` | yes for `user`; optional otherwise | Request parts that led to this requirement. Every request part must be covered by at least one requirement. |

Schema v2 requires requirement objects rather than string shorthand so the request-to-requirement mapping is explicit and auditable.

Every request part must map to at least one requirement. Every requirement, including `should` and `could`, must map to at least one task. Remove a requirement instead of leaving it knowingly uncovered.

Use `inferred` only for work necessary to make an explicit request safe, compatible, testable, or operable. Do not silently add unrelated product scope.

## 5. Plan review fields

`plan_review` is required and becomes `PLAN_REVIEW.md`.

| Field | Required | Meaning |
|---|---:|---|
| `status` | yes | Must be `approved`. |
| `reviewer` | yes | Name or route of the separate reviewer, such as `fresh Claude planning subagent`. |
| `rounds` | yes | Integer of at least 1. Increase when review caused a revision. |
| `coverage_complete` | yes | Must be `true`. |
| `tasks_atomic` | yes | Must be `true`. |
| `dependencies_valid` | yes | Must be `true`. |
| `validations_sufficient` | yes | Must be `true`. |
| `unresolved_findings` | yes | Must be an empty list before creation/autostart. |
| `notes` | yes | Non-empty list recording what the reviewer checked and any revisions made. |

Use a fresh subagent or process whenever supported. If the runtime cannot create one, perform an explicit second-pass review with the strongest available route and record that limitation in `notes`.

## 6. Task fields

| Field | Required | Meaning |
|---|---:|---|
| `id` | no | Numeric or short string id. Numeric ids normalize to three digits. |
| `title` | yes | One bounded outcome. |
| `objective` | yes | Exact result the worker must produce. |
| `requirement_ids` | yes | Non-empty list of requirements this task helps satisfy. |
| `complexity` | yes | `low`, `medium`, or `high`. `extreme` is rejected and must be split. |
| `atomicity_rationale` | yes | Explain why this is one executable TODO. A `high` task needs a substantive rationale for not splitting further. |
| `scope.in` | no | Work explicitly included. |
| `scope.out` | no | Work explicitly excluded. |
| `scope.expected_files` | no | Repository-relative files likely to change. |
| `dependencies` | no | Task ids that must complete first. |
| `implementation_guidance` | no | Non-obvious constraints or recommended approach. |
| `acceptance_criteria` | yes | Non-empty list of observable success conditions. |
| `validation_commands` | yes | Non-empty list of shell commands run from repository root. |
| `provider` | no | `auto`, `claude`, or `codex`; default `auto`. |
| `model_tier` | no | `economy`, `standard`, `strong`, or `max`; default `standard`. |
| `reasoning_effort` | no | `low`, `medium`, `high`, `xhigh`, or `max`; default `medium`. |
| `allow_provider_fallback` | no | Permit switching provider after repeated failures; default `true`. |
| `related_task_reads` | no | Narrow allowlist of other task definitions that may be read only when blocked. |
| `max_attempts` | no | Maximum technical failures before blocking; default `8`. |

Every expected file path must be repository-relative and must not contain `..`.

A task may map to several requirements when one coherent change satisfies them together. Do not use requirement mapping to justify combining unrelated outcomes.

## 7. Recursive decomposition rules

Build workstreams from the request parts, then split each workstream until every leaf task is independently understandable and verifiable.

Split when one of these changes:

- subsystem or responsibility;
- data model, service logic, protocol, UI, or rollout layer;
- migration phase or compatibility boundary;
- validation environment or safety gate;
- independently failing outcome;
- implementation ownership or required tooling.

Split when a task combines several independently useful outcomes. Examples that usually require decomposition:

- schema migration + service integration + backfill + rollout;
- backend API + frontend UI + analytics instrumentation;
- investigate an unknown architecture + implement the selected design;
- upgrade a framework + refactor breaking APIs + update all tests + deploy;
- security redesign + credential rotation + production cutover.

Do not split when adjacent edits are inseparable parts of one behavior and one validation set. Avoid file-by-file TODOs that force each worker to rediscover the same context.

An executable leaf may be `high` complexity when it is technically difficult but still has one coherent outcome. Explain why additional splitting would create artificial handoffs or make validation weaker. An `extreme` leaf is always invalid.

## 8. Complete example

```json
{
  "title": "Add idempotent notification delivery",
  "summary": "Add database-backed idempotency, integrate it into delivery, and cover retries with automated tests.",
  "language": "Portuguese (Brazil)",
  "request_analysis": {
    "request_parts": [
      {
        "id": "P001",
        "text": "Persist delivery idempotency keys"
      },
      {
        "id": "P002",
        "text": "Prevent duplicate provider sends while preserving retries"
      },
      {
        "id": "P003",
        "text": "Add deterministic automated coverage"
      }
    ],
    "repository_findings": [
      "Delivery already runs inside a repository transaction before the external provider call",
      "Database migrations are versioned under db/migrations and must support rolling deployment",
      "Service and repository tests use Maven test selectors"
    ],
    "research_decision": "No external research is required because the repository already defines the transaction and migration conventions needed for this change.",
    "research_findings": [],
    "assumptions": [
      "The delivery key can be derived from the existing message id"
    ],
    "risks": [
      "Holding a database transaction across the provider call would increase lock duration",
      "A non-backward-compatible migration could break rolling deployment"
    ],
    "open_questions": [],
    "decomposition_strategy": "Separate persistence, service integration, and end-to-end regression coverage because they have different failure modes, files, and validation commands. Keep repository schema and reservation methods together because they form one atomic persistence contract."
  },
  "requirements": [
    {
      "id": "R001",
      "text": "Reserve a delivery key atomically so it can be accepted only once",
      "source": "user",
      "priority": "must",
      "request_part_ids": ["P001", "P002"]
    },
    {
      "id": "R002",
      "text": "Preserve retry behavior after a genuine first-attempt failure",
      "source": "user",
      "priority": "must",
      "request_part_ids": ["P002"]
    },
    {
      "id": "R003",
      "text": "Keep the database migration safe for rolling deployment",
      "source": "repository",
      "priority": "must",
      "request_part_ids": ["P001"]
    },
    {
      "id": "R004",
      "text": "Add automated tests for duplicate delivery and successful retry",
      "source": "user",
      "priority": "must",
      "request_part_ids": ["P003"]
    }
  ],
  "global_constraints": [
    "Do not change unrelated formatting",
    "Do not hold a database transaction across the external provider call"
  ],
  "plan_review": {
    "status": "approved",
    "reviewer": "fresh strong-tier planning subagent",
    "rounds": 2,
    "coverage_complete": true,
    "tasks_atomic": true,
    "dependencies_valid": true,
    "validations_sufficient": true,
    "unresolved_findings": [],
    "notes": [
      "Round 1 found that rolling-deployment compatibility was not mapped; R003 was added",
      "The original integration-and-test task was split because service behavior and end-to-end regression have independent failure modes"
    ]
  },
  "autostart": true,
  "cleanup_on_success": true,
  "tasks": [
    {
      "id": 1,
      "title": "Add idempotency persistence",
      "objective": "Create the migration and repository operations needed to reserve and complete a delivery key atomically.",
      "requirement_ids": ["R001", "R003"],
      "complexity": "medium",
      "atomicity_rationale": "The migration and repository methods define one persistence contract and share one repository-level validation boundary.",
      "scope": {
        "in": [
          "Add the schema migration",
          "Add repository methods with atomic reservation semantics"
        ],
        "out": [
          "Do not change message dispatch yet"
        ],
        "expected_files": [
          "db/migrations/20260825_add_delivery_key.sql",
          "src/main/java/example/DeliveryKeyRepository.java",
          "src/test/java/example/DeliveryKeyRepositoryTest.java"
        ]
      },
      "dependencies": [],
      "implementation_guidance": [
        "Make migration safe for rolling deployment",
        "Use the repository transaction already used by delivery records"
      ],
      "acceptance_criteria": [
        "A key can be reserved exactly once",
        "A completed key can be queried",
        "The migration has a rollback path"
      ],
      "validation_commands": [
        "./mvnw -q -Dtest=DeliveryKeyRepositoryTest test",
        "git diff --check"
      ],
      "provider": "auto",
      "model_tier": "standard",
      "reasoning_effort": "medium"
    },
    {
      "id": 2,
      "title": "Integrate idempotency into delivery",
      "objective": "Prevent duplicate notification delivery by using the reservation API before dispatch while keeping genuine failures retryable.",
      "requirement_ids": ["R001", "R002"],
      "complexity": "high",
      "atomicity_rationale": "Reservation, dispatch decision, and completion state form one service-level state transition. Splitting them would leave intermediate tasks that cannot be validated as correct behavior independently.",
      "scope": {
        "in": [
          "Integrate reservation and completion into the delivery service",
          "Preserve existing retry behavior for genuine failures"
        ],
        "out": [
          "Do not redesign the queue consumer"
        ],
        "expected_files": [
          "src/main/java/example/NotificationDeliveryService.java",
          "src/test/java/example/NotificationDeliveryServiceTest.java"
        ]
      },
      "dependencies": [1],
      "implementation_guidance": [
        "Do not hold a database transaction across the external provider call"
      ],
      "acceptance_criteria": [
        "A duplicate delivery key is acknowledged without sending twice",
        "A failed first attempt remains retryable"
      ],
      "validation_commands": [
        "./mvnw -q -Dtest=NotificationDeliveryServiceTest test",
        "git diff --check"
      ],
      "provider": "claude",
      "model_tier": "strong",
      "reasoning_effort": "high",
      "related_task_reads": [1]
    },
    {
      "id": 3,
      "title": "Add end-to-end retry coverage",
      "objective": "Cover duplicate, failed-first-attempt, and successful-retry scenarios at the service boundary.",
      "requirement_ids": ["R002", "R004"],
      "complexity": "medium",
      "atomicity_rationale": "The scenarios share one end-to-end fixture and collectively validate the externally observable retry contract.",
      "scope": {
        "in": [
          "Add deterministic automated tests"
        ],
        "out": [
          "No production behavior changes unless a test exposes a bug"
        ],
        "expected_files": [
          "src/test/java/example/NotificationDeliveryE2ETest.java"
        ]
      },
      "dependencies": [2],
      "acceptance_criteria": [
        "Tests fail without idempotency and pass with the implementation",
        "Tests do not depend on timing sleeps"
      ],
      "validation_commands": [
        "./mvnw -q -Dtest=NotificationDeliveryE2ETest test",
        "./mvnw -q test",
        "git diff --check"
      ],
      "provider": "codex",
      "model_tier": "standard",
      "reasoning_effort": "medium"
    }
  ]
}
```

Create and inspect it with:

```bash
python <skill-dir>/scripts/planctl.py create --repo-root . --spec /tmp/plan-spec.json
python <skill-dir>/scripts/planctl.py validate --plan .ai-work/<plan-id>
python <skill-dir>/scripts/planctl.py audit --plan .ai-work/<plan-id>
```

## 9. Quality checklist

Before creation, confirm:

- every request part appears in `request_analysis.request_parts` with a stable id;
- every request part id maps to at least one requirement;
- repository findings are concrete rather than generic;
- research-sensitive facts were verified or explicitly deemed unnecessary;
- every explicit and necessary derived requirement has a stable id;
- every requirement is covered by at least one TODO;
- every TODO maps to at least one requirement;
- every TODO has one outcome and an atomicity rationale;
- no TODO has `extreme` complexity;
- every `high` TODO genuinely cannot be split without weakening independent validation;
- every dependency is explicit and no cycle exists;
- acceptance criteria are observable;
- validation commands are executable from repository root and prove the mapped requirements;
- write tasks do not run concurrently in the same worktree;
- risky actions have an authorization gate;
- the independent reviewer approved the final revision with no unresolved findings;
- the final task includes broad regression validation when appropriate.

## 10. Legacy plans

`planctl.py` continues to validate and resume existing schema-v1 plan directories. Every new plan created by the updated skill uses schema v2 and receives the analysis, traceability, complexity, and plan-review gates described above.
