# Progress windows and fixed ceilings

Each command starts a fresh clock; no absolute timeout covers the validation set.

## Timeout inventory

| Setting or operation | Policy | Default / precedence |
|---|---|---|
| `validation_timeout_seconds` (config/task) | Sliding per-command window | Default `1800`; integer `0..604800`; task wins; `0` disables. Existing values gain progress semantics. |
| Map `no_progress_timeout_seconds` | Sliding command window | Explicit integer `0..7200` wins, including `0`; otherwise runner window, or standalone `300`. |
| `validation_hard_timeout_seconds` (config/task/map) | Optional fixed per-validation ceiling | Integer `0..604800`; `0` disables; shortest enabled ceiling wins. |
| `task_idle_timeout_seconds` | Sliding worker window | Integer `0..604800`; default `0` disables; output, tree CPU or repo changes renew. |
| `task_timeout_seconds` | Legacy fixed worker ceiling | `0` disables; existing semantics remain. |
| `assistant.idle_timeout_seconds` | Sliding advisory window | Integer `0..120`; default `0` disables; cannot extend ceiling. |
| `assistant.timeout_seconds` | Fixed advisory ceiling | Integer `1..120`; default `30`. |
| Antigravity `print_timeout` | Fixed provider ceiling | `auto`: worker ceiling (12h if disabled); explicit duration stays fixed. |
| Toolchain, health and progress probes | Fixed read-only probe timeout | Integer `1..60s`; health cadence `10..300s`, progress `1..300s`; failures never count as progress. |
| Installer/`doctor` discovery/version checks | Fixed operational timeout | `5s` per subprocess, independent of task clocks. |
| `jobctl wait --max-seconds` | Bounded status wait | Returns `75` while the job is alive; it does not kill or restart it. |
| Cleanup grace, capability/metadata/git checks, cooldown/retry waits | Fixed operational bounds | Existing limits; independent of productive-task deadlines. |
| Test/framework timeouts and provider turn/token/spend budgets | External bounds | Remain in force; configure separately. |

Idle expiration: `124` with stagnation evidence. Hard validation/job ceiling: `126`, class `timeout_ceiling`, blocked for review without model escalation. Both retain partial logs/evidence and clean the process tree.

## Portable progress and error contract

Work above five minutes emits completed-work ticks and classified errors:
```text
PROGRESS stage=<enum> done=<int> [total=<int>] [attempt=<int>] [seq=<int>]
ERROR class=<enum> fp=<hex8> stage=<enum>
HEARTBEAT
```
Enums are lowercase; counters are nonnegative. Increasing `done` or run-wide `seq` proves progress;
`HEARTBEAT` is liveness only. Identical repeats do not renew unless a regex opts them in.
`progress_signal.py`: `format_signal`/`emit_signal` format/flush; `parse_signal` returns
`{kind, ...fields}` or `None` for ordinary logs, raising `ValueError` for malformed signals.
Keys match `[a-z_]+`; additive fields use unquoted tokens.
`fingerprint_error(message)` hashes text with numbers, hex, IDs, paths and quoted strings masked to hex8.
`python <skill-dir>/scripts/progress_signal.py probe --file <log>` reads the final 128 KiB;
stdout is only the latest complete PROGRESS `seq` (preferred) or `done`, or baseline `0`.
Errors, heartbeats and partial lines are ignored; unreadable files fail without numeric stdout.
Use read-only `progress_probe` mode `increases`; the first sample is a baseline.
Optional map `expected_duration_seconds` is integer metadata (`0..604800`), not a timeout.
Above `300`, `audit-plan` prints `progress-gap task=<id> validation=<ID> reason=<...>` once
per validation lacking `progress_regex`, `progress_probe` or nonempty `progress_files`.
Exit codes stay unchanged; omitted duration produces no warning.

## Refactor for progress

1. Digest stalls.
2. Refactor batches; flush completed-work `PROGRESS`.
3. Classify/redact `ERROR`; `HEARTBEAT` is liveness.
4. Wire mapped signals; keep IDs.
5. Retest idle renewal.
6. Then review ceilings; keep escalation.

## Evidence that renews the clock

Changed normalized stdout/stderr, increasing process-tree CPU and probes/files renew the window. Normalization ignores timestamps, PIDs and durations; unchanged heartbeats do not count. `progress_regex` opts in matching repeats. `expected_quiet_seconds` sets the minimum window after progress, ignored when idle is `0`. Dependency health never counts as progress.

Busy loops can look productive; remote I/O may be silent. Worker idle limits default off; enable with evidence. Repo monitoring excludes `.ai-work`/`.git`. Without metrics use output/probes/files.

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

Supply `book_batch_progress.py`: bounded read-only completed-batch count. Keep credentials outside argv/map/logs. Increasing counts renew; repeats, failures and timeouts do not.

`progress_probe.command` is argv, without a shell. `every_seconds`: default `20`, range `1..300`; `timeout_seconds`: default `5`, range `1..60`. `mode: changes` compares normalized successful output; `mode: increases` counts finite numeric increases. First sample is a baseline; failed, malformed, timed-out or overflowing samples never count. Capture is capped at 64 KiB; evidence stores digests/counters, never text.

`progress_files`: at most 64 repository-relative globs. Absolute paths/`..` fail; symlinks and resolved escapes are skipped. After baseline, creation or increased size/mtime counts; deletion/truncation alone does not. Watch command-produced artifacts. Omit unused fields; `null`, booleans, fractions and non-finite timeout values fail.

After installing in TalePace, merge these fields into `.ai-work/SERVICE_MAP.md`. IDs are illustrative; preserve actual IDs, commands, toolchains and resources:

```json
[
  {"id":"VAL_MAVEN","no_progress_timeout_seconds":300,"validation_hard_timeout_seconds":0,"progress_regex":"^\\[INFO\\] Tests run: .* -- in "},
  {"id":"VAL_UI","no_progress_timeout_seconds":300,"validation_hard_timeout_seconds":0},
  {"id":"VAL_HEARTBEAT","no_progress_timeout_seconds":300,"validation_hard_timeout_seconds":0},
  {"id":"VAL_BOOKS","no_progress_timeout_seconds":300,"validation_hard_timeout_seconds":0,"progress_probe":{"command":["python","tools/book_batch_progress.py","--job","book-import"],"every_seconds":20,"timeout_seconds":5,"mode":"increases"},"progress_files":["build/book-import/*.checkpoint"]}
]
```

Use actual Maven/Playwright markers and book job/path arguments; remove regex/probe/files from the heartbeat-only entry. Run `python <skill-dir>/scripts/service_map.py stamp --repo-root . --confirm-reconciled`, then `python <skill-dir>/scripts/service_map.py check --repo-root .`.

Migration: `validation_timeout_seconds: 1800` permits hours of progress without rewriting plans. For a fixed 30-minute limit, add `validation_hard_timeout_seconds: 1800` to config/task; map `0` cannot disable inherited ceilings. Remove config/task ceilings for unlimited productive runtime. Changed map policies require explicit retesting of terminal jobs.

## Return waiting to the deterministic runner

Start each `validation_jobs` ID once; return `completed`. The runner waits without a model before acceptance. Job ID equals validation ID; compatible active jobs are reused. Terminal retests need `--restart`.

```json
{"validation_commands": [], "validation_jobs": ["VAL_BOOKS"]}
```

```bash
python <skill-dir>/scripts/jobctl.py start --plan <plan-path> --id VAL_BOOKS --validation VAL_BOOKS --map .ai-work/SERVICE_MAP.md
python <skill-dir>/scripts/jobctl.py wait --plan <plan-path> --id VAL_BOOKS --max-seconds 30
python <skill-dir>/scripts/jobctl.py status --plan <plan-path> --id VAL_BOOKS
python <skill-dir>/scripts/jobctl.py stop --plan <plan-path> --id VAL_BOOKS
```

Standalone argv: `start ... --idle-seconds 300 --hard-seconds 0 -- COMMAND ARGS...`. `--progress-probe` takes JSON argv; repeat `--progress-file` for repository-relative patterns; `--progress-regex` adds a marker. Task `validation_jobs` require mapped validations with toolchain, health and freshness checks; generic argv cannot satisfy acceptance.

Job IDs match `[A-Za-z0-9][A-Za-z0-9_-]{0,63}`; Windows reserved names fail everywhere. Maximum 32 distinct IDs/task. Logs/metadata: `<plan>/jobs/<id>/runs/<run-id>/`. `wait`: `0` success, `75` running, `124` idle, `126` ceiling, `1` failure/stop. Bound waits; retain state across interruption.

Worker `start` requests supervision outside its tree. Jobs survive exit and pin validation/prerequisites/snapshot; stale evidence needs reconciliation/retest.

`processing in progress` with exit `75` is pending, never success; do not match it with `progress_regex`. Supervise bounded read-only status polling to completion/exit `0`, using an increasing batch probe.
