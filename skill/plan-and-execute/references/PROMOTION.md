# Late promotion: DIRECT -> ORCHESTRATED

Use only when work already started directly and newly discovered evidence makes durable orchestration worthwhile.

## Promotion principle

Plan the **remaining implementation only**. Promote the remaining implementation, not the history of the conversation. Never restart completed work just to make the execution look preplanned. **Never create retroactive TODOs or requirements** merely to represent completed work. Completed work is evidence/current state. Only remaining outcomes become executable TODOs.

## Promotion triggers

Promote when substantial work remains and at least one condition is material:

- scope split into independent outcomes/context boundaries;
- broad repository or external study became necessary;
- migration/compatibility/security/data-integrity risk appeared;
- provider quota/session interruption now makes resumability valuable;
- high host context pressure plus substantial non-cohesive work remains.

Do not promote a nearly finished cohesive task solely because a context meter is high.

## Build the compact handoff

Write `/tmp/pae-promotion-spec.json` with schema v1:

```json
{
  "schema_version": 1,
  "original_goal": "Ship account export support.",
  "completed_work": ["Added export domain model and repository query."],
  "validated_results": ["pytest tests/export/test_repository.py -q => passed"],
  "decisions": ["Keep export identifiers as UUID strings for API compatibility."],
  "relevant_code": ["src/export/repository.py: ExportRepository.fetch_rows"],
  "remaining_outcomes": [
    "Add HTTP endpoint and authorization behavior.",
    "Add background delivery flow and integration tests."
  ],
  "blockers": [],
  "risks": ["Large exports may exceed synchronous request limits."],
  "context_pressure": {"used_percentage": 82, "source": "claude-statusline"}
}
```

Keep every list concise. Include only validated/current facts that a fresh planner or worker would otherwise have to rediscover.

Validate and render the durable request handoff:

```bash
python <skill-dir>/scripts/promotectl.py validate \
  --spec /tmp/pae-promotion-spec.json --json

python <skill-dir>/scripts/promotectl.py render \
  --repo-root . \
  --spec /tmp/pae-promotion-spec.json \
  --output /tmp/pae-promotion-request.md \
  --json
```

`render` adds bounded deterministic git evidence (branch/head, changed files/status, diff stats) without copying full diffs or chat transcripts.

## Convert the handoff into a normal plan

Treat `/tmp/pae-promotion-request.md` as the authoritative request file for the full orchestration workflow.

1. Re-enter the adaptive study gate based on **remaining outcomes** and current repository state.
2. Build requirements/TODOs only for remaining outcomes. Do not create retroactive requirements whose only purpose is to cover completed work.
3. Preserve completed implementation unless a remaining outcome explicitly requires modifying it.
4. Create the plan with `--request-file /tmp/pae-promotion-request.md` so the handoff becomes persisted `REQUEST.md` inside the plan.
5. Attach/validate study state, audit the plan, activate lifecycle state, and continue with fresh workers normally.
6. Every resulting TODO still declares `provider`, `model_tier`, and `reasoning_effort`, plus resumable subtasks and deterministic validation, so another compatible AI can resume the remaining work.

Once the plan is active, the temporary `/tmp` spec/request can be removed. The plan's `REQUEST.md` and manifest/task files are sufficient for resume.

## Context-pressure integrations

Provider telemetry is optional:

- Claude Code can expose `context_window.used_percentage` through status-line input and has compaction lifecycle hooks. Use this as an early-warning signal when available; do not install hooks automatically.
- Codex and other hosts may compact context automatically or expose different telemetry. Never assume a portable numeric threshold.

Semantic scope, remaining work, and resumability value outrank the percentage.

## What survives quota exhaustion

After promotion and activation, normal lifecycle guarantees apply: manifest/subtask state is authoritative, interrupted work is recoverable, completed subtasks remain complete, usage/rate-limit events do not count as technical failures, and another configured provider can resume without the old chat transcript.
