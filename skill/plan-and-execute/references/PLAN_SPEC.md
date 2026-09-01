# Plan spec contract — schema v4

Use this file only when writing the JSON consumed by `planctl_concise.py create`. Read `ARTIFACT_WRITING.md` and `PLANNING_PROTOCOL.md` first. See `plan-spec.example.json` for a complete example; do not copy its prose unless it matches the current request.

## Top level

```json
{
  "title": "...",
  "summary": "...",
  "language": "...",
  "request_analysis": {},
  "requirements": [],
  "global_constraints": [],
  "execution_context": {},
  "plan_review": {},
  "autostart": true,
  "cleanup_on_success": true,
  "tasks": []
}
```

`title` and `summary` describe the implementation outcome, not the planning process. `cleanup_on_success` should remain true unless the user explicitly requests plan retention.

## `request_analysis`

```json
{
  "request_parts": [{"id": "P001", "text": "..."}],
  "repository_findings": ["..."],
  "research_decision": "...",
  "research_findings": [],
  "assumptions": [],
  "risks": [],
  "open_questions": [],
  "decomposition_strategy": "..."
}
```

Rules:

- inventory every independently testable or constrainable user intent;
- copy study conclusions, not research narration;
- keep one finding/assumption/risk/question per item;
- `autostart: true` requires no unresolved material open questions;
- preserve the original request separately when using `--request-file`.

## `requirements`

```json
{
  "id": "R001",
  "text": "When X occurs, component Y returns Z.",
  "source": "user",
  "priority": "must",
  "request_part_ids": ["P001"]
}
```

Allowed source: `user`, `repository`, `research`, `inferred`.
Allowed priority: `must`, `should`, `could`.

Every user requirement maps to at least one `request_part_id`; every request part must receive requirement coverage. Write an observable contract, not implementation commentary.

## `execution_context`

```json
{
  "global": {
    "decision": "omit",
    "rationale": "...",
    "items": []
  },
  "scoped": []
}
```

Create global context only when every TODO requires the same non-obvious fact/constraint. A context item:

```json
{
  "id": "G001",
  "kind": "constraint",
  "text": "API v2 keeps field 'id' as a string.",
  "necessity": "Every TODO changes an API v2 response and must preserve this contract.",
  "source_refs": ["R004"]
}
```

Allowed kinds: `fact`, `constraint`, `decision`, `interface`, `validation`.

Scoped context:

```json
{
  "id": "auth-contract",
  "title": "Auth contract",
  "rationale": "Only TODOs 001 and 002 change token validation.",
  "task_ids": ["001", "002"],
  "items": []
}
```

A scoped file must serve at least two but fewer than all TODOs. Single-task facts stay in that task.

## `tasks[]`

```json
{
  "id": 1,
  "title": "Reject expired refresh tokens",
  "objective": "Return 401 for expired refresh tokens without issuing a new access token.",
  "requirement_ids": ["R001"],
  "complexity": "medium",
  "atomicity_rationale": "Validation, token issuance, and focused tests share one auth invariant and one test boundary.",
  "context_boundary": {
    "shared_context": ["Refresh validation and issuance use the same token-expiry rule."],
    "why_one_todo": "One worker can change and validate the invariant without a cross-task handoff.",
    "separate_from": ["Unrelated login-session behavior remains outside this TODO."]
  },
  "scope": {
    "in": ["Reject expired refresh tokens"],
    "out": ["Do not change access-token lifetime"],
    "expected_files": ["src/auth/token.py", "tests/test_token.py"]
  },
  "dependencies": [],
  "implementation_guidance": ["Reuse the existing expiry parser; do not add a second timestamp format."],
  "acceptance_criteria": ["Expired refresh tokens return 401 and no access token."],
  "validation_commands": ["pytest tests/test_token.py -q"],
  "subtasks": [
    {
      "id": "S001",
      "title": "Implement expiry rejection",
      "objective": "The refresh path returns 401 before token issuance."
    }
  ],
  "learning_targets": [],
  "provider": "auto",
  "model_tier": "standard",
  "reasoning_effort": "medium"
}
```

### Task rules

- Allowed complexity: `low`, `medium`, `high`; `extreme` is rejected and must be split.
- One TODO = one context-cohesive outcome + one independent validation boundary.
- `atomicity_rationale` and `context_boundary` are planning/review evidence. Keep them short and concrete; they are not repeated in the compact worker projection.
- `scope.in/out` states boundaries, not the implementation narrative.
- `implementation_guidance` contains only non-obvious, task-specific guidance.
- Acceptance is observable; validation is executable.
- Subtasks are resumable checkpoints, not hidden independent deliverables.

### `learning_targets`

```json
{
  "task_id": "003",
  "reason": "TODO 003 uses the same vendor pagination contract discovered in TODO 001.",
  "topics": ["pagination cursor format", "vendor error mapping"]
}
```

Declare only later TODOs. Keep topics narrow. A learning file is created only if execution discovers a validated fact worth reusing.

## `plan_review`

```json
{
  "status": "approved",
  "reviewer": "fresh plan reviewer",
  "rounds": 1,
  "coverage_complete": true,
  "tasks_atomic": true,
  "dependencies_valid": true,
  "validations_sufficient": true,
  "contexts_minimal": true,
  "context_boundaries_sound": true,
  "unresolved_findings": [],
  "notes": ["R001 maps to TODO 001 and the focused pytest command proves its acceptance condition."]
}
```

Notes record concrete review evidence; do not narrate the review process.

## Derived-text budgets

`planctl_concise.py` enforces the detailed budgets in `ARTIFACT_WRITING.md`. Key ceilings:

- title 120; summary/objective/strategy/atomicity about 320 chars;
- request part/requirement 280;
- finding 320; assumption/risk/question/constraint 240;
- scope 200; guidance/acceptance/review note 240;
- subtask title/objective 120/280;
- context and learning fields have smaller controller-specific ceilings.

These are maximums, not targets. Prefer shorter text when it remains unambiguous.

## Create and validate

```bash
python <skill-dir>/scripts/planctl_concise.py create --repo-root . --spec /tmp/plan-spec.json
python <skill-dir>/scripts/planctl_concise.py validate --plan <plan-path>
python <skill-dir>/scripts/planctl_concise.py audit --plan <plan-path>
```

If a field fails for size or vague wording, rewrite it as a smaller precise semantic unit. Do not silently truncate requirements.
