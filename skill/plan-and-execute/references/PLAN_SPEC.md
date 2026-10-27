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
  "hard_decisions": [],
  "decomposition_strategy": "..."
}
```

Rules:

- inventory every independently testable or constrainable user intent;
- copy study conclusions, not research narration;
- keep one finding/assumption/risk/question per item;
- `autostart: true` requires no unresolved material open questions;
- preserve the original request separately when using `--request-file`.

`hard_decisions` (optional, max 12) records decision-first planning (`PLANNING_ROUTING.md` §3): decisions a stronger route resolved before the mechanical plan was written.

```json
{
  "id": "HD001",
  "decision": "Keep export identifiers as UUID strings on API v2.",
  "rationale": "Three clients parse the id as opaque text; numeric ids would break them.",
  "route_used": "strong/medium",
  "source_refs": ["R004", "I002"]
}
```

`decision` <= 240 chars, `rationale` <= 240 chars, `route_used` is `<tier>/<effort>` or empty.

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
  "validation_commands": ["python <skill-dir>/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation VAL001"],
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
  "reasoning_effort": "medium",
  "design_route": {"model_tier": "strong", "reasoning_effort": "medium"}
}
```

### Task rules

- TODOs never store concrete model ids; provider config (or, with `model_resolution: snapshot`, the plan's `MODEL_MATRIX.json` catalog snapshot, `MODEL_CATALOG.md`) resolves them per attempt, and spawn decisions follow `DELEGATION.md`.
- Allowed complexity: `low`, `medium`, `high`; `extreme` is rejected and must be split.
- `model_tier` (also in `design_route` and `route_used`) is one of `economy`, `standard`, `advanced`, `strong`, `max`. Aliases `F1`-`F5` and `L1`-`L5` map to those tiers in order (`F3`/`L3` = `advanced`) and are stored only as the canonical name. A tier without a configured model for the provider is skipped upward to the next tier that has one, never downward; the built-in Claude and Codex ladders have no `advanced` model, so `advanced` runs as `strong` and escalation from `standard` goes to `strong`.
- `design_route` is optional and allowed only on `high` TODOs (effort may not be `low`): the runner dispatches a design worker at that route first, persists `tasks/<id>.design.md`, then runs the implementation worker at `model_tier`/`reasoning_effort` with the note. The design attempt does not consume an implementation attempt; a reset discards the note.
- One TODO = one context-cohesive outcome + one independent validation boundary.
- `atomicity_rationale` and `context_boundary` are planning/review evidence. Keep them short and concrete; they are not repeated in the compact worker projection.
- `scope.in/out` states boundaries, not the implementation narrative.
- `implementation_guidance` contains only non-obvious, task-specific guidance.
- Acceptance is observable; validation is executable.
- Every automated validation command in an ORCHESTRATED plan must use one `resource_watch.py run` wrapper and one validation ID present in the fresh `.ai-work/SERVICE_MAP.md`. That map stores actual argv, toolchains and required service/check IDs; `resources: []` explicitly means no external service. Run `service_map.py audit-plan` before activation.
- Optional task `validation_timeout_seconds` is an integer `0..604800` (booleans invalid): a sliding idle window for each command, not total elapsed runtime. Omission inherits config (default `1800`); `0` disables. Explicit map `no_progress_timeout_seconds` wins for the watcher, including `0`; omission inherits the runner window, or `300` standalone. Each command starts fresh; there is no absolute validation-set limit.
- Optional task/config/map `validation_hard_timeout_seconds` is an integer `0..604800`, default `0` (disabled). The shortest enabled ceiling applies. Idle expiration exits `124`; a hard ceiling exits `126` with `timeout_ceiling` and no automatic capability escalation. Both preserve partial output and terminate the process tree. Progress probes/files and worker/advisory limits are defined in [PROGRESS_TIMEOUTS.md](PROGRESS_TIMEOUTS.md).
- Optional task `validation_jobs` contains at most 32 distinct IDs matching `[A-Za-z0-9][A-Za-z0-9_-]{0,63}`, excluding Windows reserved filenames on every host; each equals its service-map validation ID. The worker starts those mapped jobs with `jobctl.py` and returns its ordinary `completed` report. The runner waits before acceptance; IDs are not proof of success, and generic argv jobs cannot satisfy this gate. At least one validation command or declared job is required.
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

## Optional workload affinity

`tasks[].workload` accepts `implementation` (omission default), `frontend_design`, `validation_repair`, or `log_monitoring`. It selects an explicit configured profile chain; it does not replace `model_tier`, `reasoning_effort`, provider restrictions or acceptance criteria. Frontend appearance needs visual review plus interaction/accessibility checks. Raw watching is a deterministic tool, not an implementation TODO. See [VALIDATION_WORKLOADS.md](VALIDATION_WORKLOADS.md) only when configuring profiles or monitoring advice.
