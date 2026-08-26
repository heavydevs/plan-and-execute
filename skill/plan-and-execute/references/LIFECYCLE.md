# Resumable implementation lifecycle

## Contents

1. Design goals
2. User experience
3. Active-plan discovery
4. Interruption recovery
5. Runner lease and concurrency
6. Completion and cleanup
7. Cancellation and reset
8. Commands
9. Native and strict execution
10. Safety boundaries

## 1. Design goals

Treat the filesystem as the source of truth for implementation progress. A chat, terminal, network connection, or computer may disappear at any time; the next invocation must be able to determine whether to resume work or start a new request without relying on prior conversation context.

Use one `plan-and-execute` skill. Do not split lifecycle operations into separate skills because request intake, study, planning, execution, resume, and cancellation share one manifest and one safety model. The `pae` CLI is an optional cross-provider convenience layer over the same skill scripts.

## 2. User experience

The default skill invocation is state-aware:

```text
/plan-and-execute        # Claude Code
$plan-and-execute        # Codex
```

1. Inspect the current workspace with `lifecyclectl.py current`.
2. If an unfinished implementation exists and no runner is live, recover interrupted task state and continue from the next runnable TODO.
3. If a runner is already live, report it and do not start a duplicate execution.
4. If no unfinished implementation exists, create the guided request file exactly as the normal intake flow does.

Explicit lifecycle commands are also available:

```text
/plan-and-execute current
/plan-and-execute resume
/plan-and-execute cancel
/plan-and-execute reset
```

The npm CLI exposes the same workflow for either provider:

```bash
pae current
pae resume
pae cancel
pae reset
```

## 3. Active-plan discovery

The canonical pointer is:

```text
.ai-work/.active-plan.json
```

It contains only lifecycle metadata: schema version, plan id, repository-relative plan path, repository root, and timestamps. `manifest.json` remains the source of truth for TODO state.

Discovery rules:

- validate the pointer and the plan sentinel before trusting it;
- ignore and clear a pointer to a fully summarized implementation;
- when the pointer is missing or stale, scan only recognized plan directories under `.ai-work/`;
- repair the pointer automatically when exactly one unfinished plan exists;
- refuse to choose silently when several unfinished plans exist;
- never treat an intake draft as an active implementation.

An implementation remains actionable when TODOs are unfinished or when all TODOs finished but final summarization did not complete.

## 4. Interruption recovery

A controlled `Ctrl+C` returns the current task to `pending`. A power loss, terminated process, or disconnected machine may leave a task as `in_progress`.

Before resuming under an exclusive runner lease:

1. reload `manifest.json` from disk;
2. find every task still marked `in_progress`;
3. return it to `pending`;
4. append a `recovered_after_interruption` history event;
5. do not increase `functional_failures`;
6. preserve the attempt count, logs, result files, and all partial repository changes.

The next fresh worker must inspect the current working tree and either continue, repair, or replace the partial implementation within the assigned task scope. Deterministic validation still decides whether the task is complete.

## 5. Runner lease and concurrency

The strict runner owns an atomic lease at:

```text
.ai-work/<plan-id>/.runner-lease.json
```

The lease is created with exclusive filesystem semantics and records the process id, hostname, nonce, and creation time. It prevents two external runners from editing the same workspace concurrently.

- a live local process blocks another resume;
- a dead local process leaves a stale lease that is removed during the next resume;
- a recent lease from another host is treated conservatively as live;
- `cancel --force` is required to override a runner that cannot be stopped safely;
- only the lease owner may release its lease normally.

Write-heavy TODOs remain sequential unless the plan deliberately isolates them in separate worktrees.

## 6. Completion and cleanup

When every TODO passes deterministic validation:

1. create or recover the final summary;
2. mark `summary_status` as generated;
3. clear `.ai-work/.active-plan.json` before deleting the plan directory;
4. remove the exact recognized plan directory through guarded cleanup;
5. preserve implementation files, tests, commits, and unrelated repository content.

If the process stops after task completion but before summarization, the implementation remains active and the next default invocation finishes the handoff. If it stops after summary generation but before cleanup, discovery clears the terminal pointer so a new request is not blocked.

`--no-cleanup` retains the completed plan for inspection but still clears the active pointer. A retained completed plan is history, not an active implementation.

## 7. Cancellation and reset

Cancel removes planning and lifecycle state, not source changes.

```bash
pae cancel
```

This command:

- stops the live local runner when possible;
- removes the active plan directory, task definitions, logs, results, study, manifest, and active pointer;
- removes unfinished intake drafts in the workspace;
- leaves all implementation changes in the repository untouched.

For a workspace containing several recognized plans:

```bash
pae cancel --all
# equivalent full reset
pae reset
```

Use `--force` only when a runner cannot stop normally or a lease from another host has been independently confirmed stale.

Cancellation is intentionally not a rollback. Automatically reverting source files could destroy pre-existing work or changes already shared with other tasks. Use version control explicitly when implementation changes themselves must be reverted.

## 8. Commands

Direct skill-script commands:

```bash
# Decide whether default invocation should resume or create a request
python <skill-dir>/scripts/lifecyclectl.py current --repo-root . --json

# Mark a validated plan active before native execution
python <skill-dir>/scripts/lifecyclectl.py activate \
  --plan .ai-work/<plan-id> --json

# Recover stale in-progress tasks for native execution
python <skill-dir>/scripts/lifecyclectl.py recover \
  --plan .ai-work/<plan-id> --json

# Strict process-isolated resume
python <skill-dir>/scripts/lifecyclectl.py resume \
  --repo-root .

# Cancel the active implementation
python <skill-dir>/scripts/lifecyclectl.py cancel \
  --repo-root . --json

# Remove every recognized plan-and-execute artifact in the workspace
python <skill-dir>/scripts/lifecyclectl.py reset \
  --repo-root . --json
```

Useful CLI variants:

```bash
pae current --json
pae resume --provider codex
pae resume --once
pae resume --no-wait
pae resume --no-cleanup
pae cancel --force
pae reset --force
```

## 9. Native and strict execution

### Native mode

Use the active Claude Code or Codex orchestrator when nested provider processes are prohibited. On every invocation:

- rediscover the plan from disk;
- reload the manifest rather than relying on chat history;
- recover stale `in_progress` state when no external lease is live;
- dispatch a fresh worker for exactly one task definition;
- persist each state transition immediately;
- clear active state after final summary generation.

The orchestrator should be operationally stateless even when the surrounding chat retains history. Do not resend the request, study, complete plan, or previous worker reports to the next worker.

### Strict external-runner mode

Use `pae resume` or `lifecyclectl.py resume` when nested execution is allowed. This mode provides the strongest process isolation, atomic lease, automatic interruption recovery, rate-limit handling, and end-to-end continuation.

Both modes read and update the same plan workspace, so a plan may be resumed with either Claude Code or Codex when routing rules permit.

## 10. Safety boundaries

- Never delete a directory without a valid plan sentinel and matching manifest.
- Never follow symlinks in lifecycle state, plan roots, or intake cleanup.
- Never remove implementation files during cancel or lifecycle cleanup.
- Never start a second runner while a live lease exists.
- Never silently choose among multiple unfinished plans.
- Never count a power, network, or process interruption as a technical implementation failure.
- Never create a new request while a resumable unfinished plan exists.
- Never leave a terminal implementation marked active after its final summary is generated.
