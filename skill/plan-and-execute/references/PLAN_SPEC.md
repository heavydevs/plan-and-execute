# Plan spec contract — schema v4 + portable F/L routing

Use this file only when writing the JSON consumed by `planctl_concise.py create`. Read `ARTIFACT_WRITING.md`, `PLANNING_PROTOCOL.md`, and `PORTABLE_MODEL_ROUTING.md` first. See `plan-spec.example.json` for a structural template; its `TEMPLATE_*`/`CURRENT_*` values are deliberately non-executable and must be replaced with a fresh provider-specific daily binding before plan creation.

The persisted base manifest remains schema v4 for backwards compatibility. New plans use the additive `fl-v1` portable-routing contract.

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
  "model_compatibility": {},
  "autostart": true,
  "cleanup_on_success": true,
  "tasks": []
}
```

`title` and `summary` describe the implementation outcome, not the planning process. `cleanup_on_success` should remain true unless the user explicitly requests plan retention.

`model_compatibility` is mandatory when tasks use portable F/L routing. For new plans it normally contains only the provider currently being used. Before constructing it, check that provider's cache under `~/.plan-and-execute/cache/model-compatibility`; reuse a fresh entry for the rest of the local calendar day and perform live CLI/current-documentation discovery only when that provider's cache is missing, stale, or invalid. The controller renders the plan snapshot as `MODEL_COMPATIBILITY.json` and `MODEL_COMPATIBILITY.md`.

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
  "model_family": "F2",
  "model_level": "L2"
}
```

### Task rules

- Allowed complexity: `low`, `medium`, `high`; `extreme` is rejected and must be split.
- One TODO = one context-cohesive outcome + one independent validation boundary.
- `atomicity_rationale` and `context_boundary` are planning/review evidence. Keep them short and concrete.
- `scope.in/out` states boundaries, not the implementation narrative.
- `implementation_guidance` contains only non-obvious, task-specific guidance.
- Acceptance is observable; validation is executable.
- Subtasks are resumable checkpoints, not hidden independent deliverables.
- `model_family` must be `F1`-`F4`; `model_level` must be `L1`-`L5`.
- New F/L tasks must not also declare `provider`, `model_tier`, or `reasoning_effort`.
- The same F/L requirement must remain valid if execution changes among Codex, Claude, Gemini, Qwen, or Muse.

Legacy plans/specs using `provider`/`model_tier`/`reasoning_effort` remain supported for resume compatibility. Do not mix legacy-routing tasks and F/L tasks in one new plan.

## `model_compatibility`

For a new plan, the compatibility object normally contains exactly the active provider. It must map all F1-F4 families for that provider to current concrete models and every family must map all L1-L5 to effective native effort names. When the provider exposes fewer native levels, duplicate the nearest supported level rather than inventing one.

The active provider's `checked_at` must be a timezone-aware ISO-8601 timestamp from the current local calendar day. Obtain the object from today's cache when available. Only when the provider cache is missing/stale/invalid should the planner inspect that provider's CLI/current official documentation and write a fresh cache entry.

Example fragment for a Codex invocation:

```json
{
  "model_compatibility": {
    "generated_at": "2026-09-10T09:30:00-03:00",
    "discovery": "Fresh Codex daily compatibility loaded from cache or rebuilt from current Codex CLI/docs.",
    "providers": {
      "codex": {
        "checked_at": "2026-09-10T09:30:00-03:00",
        "sources": ["codex --help", "current official Codex model documentation"],
        "families": {
          "F1": {
            "model": "<actual current model id>",
            "levels": {"L1": "<native>", "L2": "<native>", "L3": "<native>", "L4": "<native>", "L5": "<native>"}
          },
          "F2": {"model": "<actual current model id>", "levels": {"L1": "<native>", "L2": "<native>", "L3": "<native>", "L4": "<native>", "L5": "<native>"}},
          "F3": {"model": "<actual current model id>", "levels": {"L1": "<native>", "L2": "<native>", "L3": "<native>", "L4": "<native>", "L5": "<native>"}},
          "F4": {"model": "<actual current model id>", "levels": {"L1": "<native>", "L2": "<native>", "L3": "<native>", "L4": "<native>", "L5": "<native>"}}
        }
      }
    }
  }
}
```

Use `claude`, `gemini`, `qwen`, or `muse` instead when that provider is active. Do not add unused provider objects merely for completeness. Older `fl-v1` plans containing several providers remain readable for backwards-compatible resume.

The structural example file contains placeholders intentionally. They must be replaced before `cache-write` or plan creation; do not copy model names from an old plan simply to satisfy the schema.

## `learning_targets`

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

Notes record concrete review evidence; do not narrate the review process. The review must also confirm that F/L choices match task risk/verifiability and that the active provider's compatibility snapshot is fresh for the current local calendar day. It must not require unrelated provider mappings.

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

If a field fails for size or vague wording, rewrite it as a smaller precise semantic unit. Do not silently truncate requirements or replace cache/live provider discovery with remembered model names.
