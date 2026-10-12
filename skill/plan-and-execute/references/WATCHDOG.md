# Execution watchdog

Run the watchdog without a model every 5–10 minutes. It reads lifecycle state and reports one compact line per unfinished task or current job. It never kills/restarts a process, claims a task, repairs a lease, or changes plan/job state. Resume remains an orchestrator decision under [LIFECYCLE.md](LIFECYCLE.md).

## Commands and output

```bash
python <skill-dir>/scripts/watchdogctl.py status --repo-root <repo> --quiet
python <skill-dir>/scripts/watchdogctl.py status --plan <plan-path> --quiet
python <skill-dir>/scripts/watchdogctl.py watch --repo-root <repo> --interval 300
```

`--plan` selects exactly one plan. Without it, read-only lifecycle discovery scans actionable plans under `--repo-root` / `--work-root` (default `.ai-work`), including multiple unfinished plans. It does not repair the active pointer. Completed tasks and their terminal validation jobs are omitted; summary-pending plans remain actionable.

Lines follow `ok <plan>/<item> <state>` or `ANOMALY:<class>:<action> <plan>/<item> <short detail>`. `status --quiet` omits healthy lines. An empty repository produces no lines. Raw errors, provider messages, tool calls and credentials are never printed. Resume actions include the existing `python <skill-dir>/scripts/run_concise.py --plan <p> --once` command; the watchdog only displays it.

| Class | Action | Evidence |
| --- | --- | --- |
| `blocked` | `inspect_blocker` | Task is blocked; read its assigned failure capsule before routing. |
| `permission_blocked` | `owner_resolve_permission` | Blocker identifies permission/approval; the owner resolves it. |
| `classifier_blocked` | `owner_review_classifier` | Blocker identifies a classifier decision; the owner reviews it. |
| `runner_dead` | `resume` | In-progress task has no live lease. |
| `silent` | `inspect_progress` | Live runner/job has no recent activity evidence within its idle window. Inspect; do not kill it. |
| `awaiting_next` | `resume` | A runnable task or final summary waits without a live runner. |
| `quota_resume_due` | `resume` | Runnable pending task has an expired availability cooldown and no live runner. |
| `job_failed` | `inspect_job` | Job failed, stalled, stopped, or lost its supervisor. |

Exit codes: `0` healthy/no anomalies, `1` at least one anomaly, `2` invalid arguments or unreadable/invalid evidence. `watch --iterations N` stops after N snapshots and returns the last snapshot's code; `0` iterations means indefinite watch. Keyboard interruption exits `0`. A finite watch can return `1` with no output when an unchanged anomaly was already reported.

## Activity and deduplication

Tasks use `task_idle_timeout_seconds` when present, otherwise the plan overlay's value. A selected positive value is the observation window; missing, zero or invalid values use **1800 seconds**. Jobs use positive `idle_timeout_seconds`, otherwise the same default. This observation threshold is independent of runner timeouts; a zero task override does not inherit a positive plan value.

The baseline is the latest claim/start, then current-attempt log mtime/size and the shared `progress_signal.probe_file` counter (`seq` preferred over `done`). The signal probe ignores ERROR, HEARTBEAT and incomplete/malformed signal lines. Log metadata is activity evidence, not proof that an acceptance criterion is advancing. Old-attempt logs do not renew the clock. Current job status and idle clocks come from `jobctl.status_job`; collecting them performs no dispatch or repair.

For a live local runner, provider session metadata after the attempt start can renew the clock. Codex uses `CODEX_HOME/sessions/**/rollout-*.jsonl` (default `~/.codex`), matching the session header's repository directory. Claude uses the repository's encoded project directory under `CLAUDE_CONFIG_DIR/projects` (default `~/.claude`). Only header metadata and the last complete JSON event timestamp are used; provider content is never retained. **Windows Codex rollout mtime can lag: the final JSON timestamp is the event clock.** Sessions from other repositories, before the attempt, or with future timestamps are excluded. Remote leases retain lifecycle's conservative liveness semantics and do not use this host's provider sessions.

`watch` accepts only **300..600 seconds**, always omits healthy lines, and prints new/changed anomalies. Stable details omit increasing idle ages, so an unchanged silence does not alert every tick. Recovery clears the dedupe entry; a later recurrence alerts again. Observation changes renew the cached activity clock, including size changes when mtime lags. The selector-specific cache is `.ai-work/watchdog/<hash>.json`; this is the only state the command writes. `status` never writes that cache or any plan, lease, job, or Python bytecode file.

## Host scheduling

Replace example Python/skill/repository paths with absolute installed paths. Choose one scheduler per repository/selector to avoid competing watches. Collect stdout in a host log or notification queue; exit `1` means an anomaly was detected, not that the watchdog crashed. Scheduling does not authorize a resume command.

**Session loop / host session cron:** register `status --quiet` at a 5–10 minute cadence with the host's session scheduler. A host with only a shell can use this loop (exit `1` must not abort it):

```bash
while true; do
  python /opt/skills/plan-and-execute/scripts/watchdogctl.py status --repo-root /repos/sample --quiet
  sleep 300
done
```

**Windows Task Scheduler (`schtasks`):** this CMD example runs every five minutes in the logged-in session. Use a wrapper that redirects stdout to your host log if scheduled output needs persistence.

```bat
schtasks /Create /SC MINUTE /MO 5 /TN PlanAndExecuteWatchdog /TR "C:\Python313\python.exe C:\skills\plan-and-execute\scripts\watchdogctl.py status --repo-root C:\repos\sample --quiet" /IT
```

**Unix cron:** an absolute Python path avoids cron's reduced PATH. Create the log directory before registering the entry.

```cron
*/5 * * * * /usr/bin/python3 /opt/skills/plan-and-execute/scripts/watchdogctl.py status --repo-root /repos/sample --quiet >> /repos/sample/.ai-work/watchdog/status.log 2>&1
```

**Background watch:** this provides persistent dedupe across restarts, unlike independent status snapshots. Start only on explicit host scheduling instructions.

```bash
nohup python3 /opt/skills/plan-and-execute/scripts/watchdogctl.py watch --repo-root /repos/sample --interval 300 > /repos/sample/.ai-work/watchdog/watch.log 2>&1 &
```

```powershell
Start-Process -FilePath 'C:\Python313\python.exe' -ArgumentList 'C:\skills\plan-and-execute\scripts\watchdogctl.py watch --repo-root C:\repos\sample --interval 300' -WindowStyle Hidden -RedirectStandardOutput 'C:\repos\sample\.ai-work\watchdog\watch.log' -RedirectStandardError 'C:\repos\sample\.ai-work\watchdog\watch-error.log'
```

Create `.ai-work/watchdog` before using shell redirection or `Start-Process`. Stop/remove a scheduled host task through its host scheduler; the watchdog has no process-control command.

## Watcher routing and provider policy

The following configured global preference applies to autonomous observation workflows; see [ROUTING_CONFIG.md](ROUTING_CONFIG.md) for paths and precedence. The watchdog itself selects no provider. Built-in order remains Claude then Codex; plan/task/CLI overrides and legacy snapshots retain precedence.

- **Model-free status checks**: Routine watchdog execution (`watchdogctl.py status --quiet`) runs deterministically without invoking an LLM.
- **Watchkeeper agent**: When an autonomous watchkeeper agent is scheduled or spawned to monitor status output, it routes in the `economy` tier via **Antigravity** (`gemini-3.8-flash-high`, omitting `--effort` because the model ID embeds maximum effort), with fallback Claude (`haiku`) -> Codex (`gpt-6-luna`).
- **Blocked task diagnosis**: Investigating a `blocked` task's assigned latest-failure capsule before routing or replanning routes in the `strong` tier at `high` reasoning effort on **Codex** (`gpt-6.1-sol`, strong/high), falling back to Claude (`claude-opus-5-5`, effort `high`) -> Antigravity (`claude-opus-4-6-thinking`).
- **Provider policy alignment**: Follows the global provider priority:
  - `economy`: Antigravity (`gemini-3.8-flash-high`) -> Claude (`haiku`) -> Codex (`gpt-6-luna`)
  - `standard`+: Codex (`gpt-6.1-sol`) -> Claude (`claude-sonnet-5-5` for standard, `claude-opus-5-5` for configured advanced/strong/max) -> Antigravity. See [MODEL_MAPPING.md](MODEL_MAPPING.md) for the host model example; empty tiers skip upward and configured overrides may select another primary.

## Watchkeeper prompt

```text
Run watchdogctl.py status --repo-root <repo> --quiet every 5–10 minutes without a model.
If stdout is empty and exit is 0, remain silent.
On ANOMALY, relay its single compact line to the orchestrator.
For blocked, inspect only the affected task's assigned latest-failure capsule (diagnose on Codex Sol strong/high before replanning).
For permission_blocked/classifier_blocked, request the indicated owner's decision.
For silent, inspect progress metadata; never kill a live runner or worker.
For job_failed, inspect the named current job's status before selecting a route.
For runner_dead/awaiting_next/quota_resume_due, verify lifecycle before resuming.
Use the displayed run_concise.py --plan <p> --once only when resume is authorized.
Do not edit plan/job state, introduce retries, or change cooldowns.
On exit 2, report the evidence/tool error; do not infer an execution failure.
```
