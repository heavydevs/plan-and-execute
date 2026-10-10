# Progress windows and fixed ceilings

Load for long-command configuration, stall diagnosis or handoff. Each command starts a fresh progress clock; no absolute timeout covers the validation set.

## Timeout inventory

| Setting or operation | Policy | Default / precedence |
|---|---|---|
| `validation_timeout_seconds` (config or task) | Sliding idle window for each validation command | `1800`; integer `0..604800`; task override wins; `0` disables. Existing plans keep the value but gain progress semantics. |
| Map `no_progress_timeout_seconds` | Sliding idle window for the mapped command | Explicit `0..7200` map value wins, including `0`; omission inherits the runner window, or `300` for a standalone watcher. |
| `validation_hard_timeout_seconds` (config, task or map) | Fixed optional ceiling for one validation | `0` disables; the shortest enabled ceiling applies. Values are integers `0..604800`. |
| `task_idle_timeout_seconds` | Optional sliding worker window | `0..604800`; default `0` disables; output, process-tree CPU, or repository changes renew it. |
| `task_timeout_seconds` | Legacy fixed worker ceiling | `0` disables; existing semantics remain. |
| `assistant.idle_timeout_seconds` | Optional sliding advisory window | `0..120`; default `0` disables; it does not extend the advisory ceiling. |
| `assistant.timeout_seconds` | Fixed bounded advisory ceiling | `1..120`; default `30`; diagnostic advice stays bounded. |
| Antigravity `print_timeout` | Provider-side fixed ceiling | `auto` follows the worker hard ceiling (12h when disabled); an explicit duration remains fixed. |
| Toolchain, resource-health and progress probes | Fixed timeout for each read-only probe | `1..60s`; health cadence `10..300s`, progress cadence `1..300s`; probe failures never count as progress. |
| Installer/`doctor` CLI discovery/version checks | Fixed operational timeout | `5s` per subprocess; independent of task clocks. |
| `jobctl wait --max-seconds` | Bounded status wait | Returns `75` while the job is alive; it does not kill or restart it. |
| Cleanup grace, capability checks, metadata/git commands, cooldown/retry waits | Fixed operational bounds | Keep their existing limits; they are not productive-task deadlines. |
| Test/framework-owned timeouts and provider turn/token/spend budgets | Explicit external bounds | Remain in force; configure them separately when the project needs them. |

Idle expiration is `124` and supplies stagnation evidence. A hard validation/job ceiling is `126`, classified `timeout_ceiling`; it blocks for review without automatic model escalation. Both preserve partial logs and bounded evidence, then clean the process tree.

## Evidence that renews the clock

Changed normalized stdout/stderr, increasing process-tree CPU, and configured probes/files renew the idle window. Normalization ignores timestamps, PIDs and durations; an unchanged heartbeat does not count. `progress_regex` opts matching output into renewal, including repeats. `expected_quiet_seconds` sets a minimum idle window after each progress event, ignored when idle is `0`. Healthy dependency checks never count as validation progress.

A CPU-busy loop can look productive; remote I/O may leave local CPU quiet, and JSON adapters may emit only a final response. Worker idle limits default off: enable them with suitable evidence. Repository monitoring excludes `.ai-work` and `.git`. Without process metrics, use output or explicit probes/files.

```json
{
  "no_progress_timeout_seconds": 300,
  "progress_probe": {
    "command": ["python", "tools/book_batch_progress.py", "--job", "book-import"],
    "every_seconds": 20,
    "timeout_seconds": 5,
    "mode": "increases"
  },
  "progress_files": ["build/book-import/*.checkpoint"]
}
```

Supply `book_batch_progress.py` locally as a bounded read-only query using existing credentials; return only this job's completed-batch count. Keep credentials out of argv, the map and logs. Samples `12`, `13`, `14` renew the five-minute window for hours; an unchanged `14`, failed query or timed-out probe does not.

`progress_probe.command` is argv without an implicit shell. `every_seconds` defaults to `20` (`1..300`); `timeout_seconds` to `5` (`1..60`). `mode: changes` compares normalized successful output; `mode: increases` requires finite numeric stdout and counts only increases. The first sample is a baseline; failed, malformed, timed-out or overflowing samples never count. Capture is at most 64 KiB; evidence stores digests/counters, never probe text.

`progress_files` contains at most 64 repository-relative globs. Absolute paths and `..` fail validation; symlinks and resolved escapes are skipped during sampling. After the baseline, creation or increased size/mtime counts; deletion or truncation alone does not. Watch command-produced artifacts. Optional fields must have their declared types: omit unused fields instead of setting `null`; booleans, fractions and non-finite numbers are invalid timeout values.

After installing the updated skill in TalePace, edit the JSON block in `.ai-work/SERVICE_MAP.md`. Merge these fields into the corresponding entries; these IDs are illustrative, so preserve the project's actual IDs, commands, toolchains and resources:

```json
[
  {"id":"VAL_MAVEN","no_progress_timeout_seconds":300,"validation_hard_timeout_seconds":0,"progress_regex":"^\\[INFO\\] Tests run: .* -- in "},
  {"id":"VAL_UI","no_progress_timeout_seconds":300,"validation_hard_timeout_seconds":0},
  {"id":"VAL_HEARTBEAT","no_progress_timeout_seconds":300,"validation_hard_timeout_seconds":0},
  {"id":"VAL_BOOKS","no_progress_timeout_seconds":300,"validation_hard_timeout_seconds":0,"progress_probe":{"command":["python","tools/book_batch_progress.py","--job","book-import"],"every_seconds":20,"timeout_seconds":5,"mode":"increases"},"progress_files":["build/book-import/*.checkpoint"]}
]
```

Use the actual Maven suite marker and Playwright list reporter; completed-test output renews progress. Remove any regex/probe/files from the heartbeat-only entry. Supply the book helper and adapt its job/path arguments. Then run `python <skill-dir>/scripts/service_map.py stamp --repo-root . --confirm-reconciled` and `python <skill-dir>/scripts/service_map.py check --repo-root .`.

Migration: existing `validation_timeout_seconds: 1800` now permits hours of productive work; nothing is rewritten. To retain a fixed 30-minute limit, explicitly add `validation_hard_timeout_seconds: 1800` to config/task; a map value of `0` cannot disable that inherited ceiling. Remove enabled config/task ceilings for unlimited productive runtime. Changed map policies require an explicit retest of terminal jobs.

## Return waiting to the deterministic runner

Declare mapped IDs in task `validation_jobs`, start each long command once, then return the ordinary `completed` report. The runner waits without a model session before accepting the task. Each job ID equals its map validation ID. Resume with the same ID; a compatible active start reuses it. Retesting a terminal job requires `--restart`.

```json
{"validation_commands": [], "validation_jobs": ["VAL_BOOKS"]}
```

```bash
python <skill-dir>/scripts/jobctl.py start --plan <plan-path> --id VAL_BOOKS --validation VAL_BOOKS --map .ai-work/SERVICE_MAP.md
python <skill-dir>/scripts/jobctl.py wait --plan <plan-path> --id VAL_BOOKS --max-seconds 30
python <skill-dir>/scripts/jobctl.py status --plan <plan-path> --id VAL_BOOKS
python <skill-dir>/scripts/jobctl.py stop --plan <plan-path> --id VAL_BOOKS
```

For a standalone argv command, use `start ... --idle-seconds 300 --hard-seconds 0 -- COMMAND ARGS...`. Optional `--progress-probe` takes a JSON argv array; repeat `--progress-file` for repository-relative patterns; `--progress-regex` adds an output marker. Task `validation_jobs` require mapped validations so toolchain, resource-health and freshness checks remain active; a generic argv job cannot satisfy that acceptance gate.

Job IDs match `[A-Za-z0-9][A-Za-z0-9_-]{0,63}`; Windows reserved names fail on every host. A task may declare 32 distinct IDs. Logs/metadata stay under `<plan>/jobs/<id>/runs/<run-id>/`. `wait`: `0` success, `75` running, `124` idle, `126` ceiling, `1` other failure/stop. Use bounded waits and retain state across interruption.

For model workers, `start` writes a request; the runner launches the supervisor outside the worker's tree, preserving the job after worker exit. Jobs pin their validation, prerequisites and source snapshot; changed or stale evidence requires reconciliation and explicit retest.

A registration command printing `processing in progress` then exiting `75` reports pending work. Do not match that message with `progress_regex`. Supervise bounded read-only status polling until completion/exit `0`, with an increasing batch probe; a command's `75` is never success.
