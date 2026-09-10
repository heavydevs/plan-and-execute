# Execution workflow

Use this reference only after the plan is approved. Planning rules live in `PLANNING_PROTOCOL.md`; portable model binding lives in `PORTABLE_MODEL_ROUTING.md`; model escalation lives in `MODEL_ROUTING.md`.

## Roles

- **Orchestrator:** authoritative plan state, F/L resolution, scheduling, validation, escalation, final handoff, cleanup.
- **Worker:** one TODO, assigned context/learnings, repository evidence needed for that TODO, structured report.
- **Summarizer:** compact completed-task state only; never raw worker transcripts.

Fresh workers reduce context contamination. Disk state, not chat history, carries progress.

## Native execution loop

### 1. Select

```bash
python <skill-dir>/scripts/planctl_concise.py next --plan <plan-path> --json
```

For a portable plan, the selected TODO contains only `model_family` and `model_level`. The plan's `MODEL_COMPATIBILITY.json`/`.md` is a snapshot, while the user-home daily cache can provide another provider's current binding without changing task semantics.

### 2. Resolve F/L and claim

Choose the provider to execute the TODO, then check that provider's daily compatibility. A plan snapshot checked today may satisfy this directly; otherwise use the fresh provider cache under `~/.plan-and-execute/cache/model-compatibility`.

If the chosen provider has no fresh binding, do not use yesterday's mapping. Run `model_compatctl.py cache-status`; if missing/stale/invalid, perform live CLI/current-documentation discovery only for that provider, write its cache, and refresh the plan snapshot when appropriate:

```bash
python <skill-dir>/scripts/model_compatctl.py refresh \
  --plan <plan-path> \
  --provider <provider> \
  --json
```

Resolve the TODO's F/L against that fresh binding. The concrete route is execution history only:

```bash
python <skill-dir>/scripts/planctl_concise.py claim \
  --plan <plan-path> \
  --task 001 \
  --route '{"provider":"<resolved-provider>","tier":"<internal-family-alias>","model":"<current-model>","effort":"<native-level>"}'
```

Do not copy that concrete route back into the TODO. Provider switching preserves the same F/L and does not require re-planning.

### 3. Dispatch one fresh worker

Prompt with only:

- repository root;
- task id and task-definition path;
- instruction to read exactly the context/learning files listed there;
- checkpoint controller path;
- permission to inspect/edit relevant repository files;
- completion-report schema path.

Do not paste the original request, full plan, study, manifest, TODO list, prior reports, logs, or future tasks.

The compact task file contains execution-relevant information including objective, portable F/L requirement, a reference to `MODEL_COMPATIBILITY.md`, context/learnings, checkpoints, scope, guidance, acceptance, validation, and narrow publishable learning topics.

### 4. Checkpoint

```bash
python <skill-dir>/scripts/planctl_concise.py subtask-start \
  --plan <plan-path> --task 001 --subtask S001

python <skill-dir>/scripts/planctl_concise.py subtask-complete \
  --plan <plan-path> --task 001 --subtask S001
```

Use `subtask-reset` only when that checkpoint must be deliberately redone. Never edit task Markdown for state.

### 5. Validate independently

The worker report is evidence, not acceptance. The orchestrator must verify exact context/learning read lists, verify required subtasks, run every task validation command from the repository root, and keep full output in logs with only bounded diagnostic tails in state.

### 6. Complete or fail

Success:

```bash
python <skill-dir>/scripts/planctl_concise.py complete \
  --plan <plan-path> \
  --task 001 \
  --report <plan-path>/results/001.json \
  --result-file results/001.json
```

Functional failure:

```bash
python <skill-dir>/scripts/planctl_concise.py fail \
  --plan <plan-path> --task 001 \
  --reason "Focused failure evidence or log reference"
```

Usage/rate limit:

```bash
python <skill-dir>/scripts/planctl_concise.py fail \
  --plan <plan-path> --task 001 \
  --reason "Provider usage limit" --rate-limited
```

A completion report is deliberately bounded. On completion, only compact summary/risks/follow-ups needed for final handoff are promoted into manifest state. Raw provider output remains in ephemeral result/log files.

## Strict external runner

From a terminal/CI outside a nested provider invocation:

```bash
python <skill-dir>/scripts/run_concise.py --plan <plan-path>
```

Useful flags:

```bash
python <skill-dir>/scripts/run_concise.py --plan <plan-path> --dry-run
python <skill-dir>/scripts/run_concise.py --plan <plan-path> --once --no-cleanup
python <skill-dir>/scripts/run_concise.py --plan <plan-path> --provider codex
python <skill-dir>/scripts/run_concise.py --plan <plan-path> --provider claude
python <skill-dir>/scripts/run_concise.py --plan <plan-path> --provider gemini
python <skill-dir>/scripts/run_concise.py --plan <plan-path> --provider qwen
python <skill-dir>/scripts/run_concise.py --plan <plan-path> --provider muse
python <skill-dir>/scripts/run_concise.py --plan <plan-path> --no-wait
```

For portable tasks the runner translates F/L through the fresh bindings available from the plan snapshot and provider-specific user cache, then starts a fresh provider process with the concrete current model/native effort. A provider override requires a fresh binding for that provider; if none exists, invoke the skill so it can perform provider-specific cache/discovery handling instead of silently using stale data.

Gemini and Qwen use their existing headless adapters. Muse uses `muse exec --json` and the generic JSON/JSONL completion-report parser.

## State commands

```bash
python <skill-dir>/scripts/planctl_concise.py validate --plan <plan-path>
python <skill-dir>/scripts/planctl_concise.py audit --plan <plan-path>
python <skill-dir>/scripts/planctl_concise.py status --plan <plan-path>
python <skill-dir>/scripts/planctl_concise.py status --plan <plan-path> --json
python <skill-dir>/scripts/planctl_concise.py reset --plan <plan-path> --task 001
```

`TODO.md` remains one line per task. `manifest.json` is authoritative. `MODEL_COMPATIBILITY.json` is the plan snapshot for replaceable concrete provider/model bindings; daily provider cache is outside the plan workspace and survives plan cleanup.

## Failure and escalation

Classify before changing capability:

- **technical/capability:** implementation/test/report/tool failure caused by the attempted solution; may justify higher L or F;
- **environmental actionable:** repository/toolchain issue the worker can repair within scope;
- **provider availability/usage:** switch/retry provider while preserving F/L and checking the target provider's daily cache;
- **mapping stale:** model or effort is rejected/unavailable; refresh that provider's cache/binding while preserving F/L;
- **planning invalidation:** evidence disproves a material requirement, dependency, context boundary, validation assumption, or capability requirement; stop downstream work and replan.

Persist the smallest diagnostic excerpt that guides the next attempt plus a log reference. Do not copy full logs into `last_error`.

Raise L when evidence points to reasoning depth. Raise F when evidence points to model capability. Never raise either merely because a provider changed or hit quota.

## Validated learning

After a source TODO passes deterministic validation, it may publish only learnings that target a predeclared untouched future TODO, match predeclared topics, state one concrete validated finding, cite repository symbols/paths/commands, and save meaningful rediscovery cost.

No transcript, generic advice, or plan history belongs in learning files.

## Final handoff

After all TODOs complete, reload final state, construct bounded `SUMMARY_INPUT.json` from authoritative completion/validation state, generate the concise handoff, mark summary generated, clear lifecycle active state, and delete only the sentinel-protected plan workspace unless retention was explicitly requested.

Never concatenate raw worker reports or logs into the final summarizer prompt.

## Safety

- Preserve unrelated working-tree changes.
- Never use cleanup to revert implementation output.
- Keep plan artifacts under the configured plan work root.
- Reject symlink/path escapes through existing lifecycle/plan guards.
- Retain plan state when execution, final validation, or summary generation fails so resume remains possible.
