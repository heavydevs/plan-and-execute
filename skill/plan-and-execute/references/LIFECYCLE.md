# Lifecycle protocol

Use this file only for active-plan discovery, resume, cancellation, reset, and cleanup. Lifecycle state is deterministic; do not spend model tokens narrating it.

Use `lifecyclectl_concise.py` so any recovery rewrite keeps compact task projections.

## Current/status

```bash
python <skill-dir>/scripts/lifecyclectl_concise.py current --repo-root . --json
```

Interpretation:

- `idle` -> no unique unfinished plan; normal intake may start;
- one actionable plan -> resume it;
- multiple unfinished plans -> require an explicit selection/cancel/reset instead of guessing;
- live runner lease -> do not start a duplicate runner.

The active pointer is `.ai-work/.active-plan.json`. It is lifecycle metadata, not implementation state.

## Activate

After study/plan gates succeed:

```bash
python <skill-dir>/scripts/lifecyclectl_concise.py activate --plan <plan-path> --json
```

Do not activate a completed plan. Do not replace another unfinished active plan unless an explicit lifecycle action resolves it.

## Resume

Resume from disk state, never from old chat history.

1. discover the unique active/actionable plan;
2. acquire the runner lease;
3. recover interrupted `in_progress` task/subtask state;
4. preserve completed subtasks and repository changes;
5. continue with a fresh worker for the next runnable TODO.

Strict execution:

```bash
python <skill-dir>/scripts/run_concise.py --plan <plan-path>
```

An interruption is not automatically a technical failure. Recovery resets the interrupted task/subtask state needed for safe continuation without discarding implementation changes.

## Lease

`.runner-lease.json` prevents duplicate runners.

- A live local PID blocks another runner.
- A stale local lease can be recovered.
- Remote-host leases are treated conservatively for their configured freshness window.
- Cancellation may stop the live owned runner before deleting planning state.

Do not pass lease contents to implementation workers.

## Cancel

Cancel means stop the active plan and delete its recognized planning/control artifacts while preserving current repository implementation changes.

```bash
python <skill-dir>/scripts/lifecyclectl_concise.py cancel --repo-root . --json
```

The command must not run arbitrary rollback/revert/clean operations on the repository.

## Reset

Reset removes all recognized plan-and-execute plan workspaces under the configured work root while preserving unrelated directories and repository implementation changes.

```bash
python <skill-dir>/scripts/lifecyclectl_concise.py reset --repo-root . --json
```

Only directories with the expected plan sentinel/path validation are eligible.

## Successful completion cleanup

After every TODO and final deterministic validation pass:

1. generate final handoff;
2. mark summary generated;
3. clear active pointer;
4. delete the verified plan directory.

```bash
python <skill-dir>/scripts/planctl_concise.py cleanup --plan <plan-path>
```

Cleanup must refuse unsafe paths/symlinks, incomplete plans, or missing summary state unless an explicit force path is used by a deliberate lifecycle operation.

The product of the plan remains: source changes, tests, generated product files, commits, and unrelated repository state are outside the plan directory and must not be removed.

## What belongs in lifecycle context

Only include facts needed to choose one lifecycle action:

- plan id/path/state;
- task counts/current runnable state;
- lease live/stale status;
- whether summary/cleanup remains pending.

Do not load PLAN.md, task definitions, study, logs, or worker reports merely to answer lifecycle status.
