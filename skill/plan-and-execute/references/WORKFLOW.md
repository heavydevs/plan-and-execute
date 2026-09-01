# Execution workflow

Use this reference only after the plan is approved. Planning rules live in `PLANNING_PROTOCOL.md`; writing budgets live in `ARTIFACT_WRITING.md`; model escalation lives in `MODEL_ROUTING.md`.

## Roles

- **Orchestrator:** authoritative plan state, scheduling, validation, escalation, final handoff, cleanup.
- **Worker:** one TODO, assigned context/learnings, repository evidence needed for that TODO, structured report.
- **Summarizer:** compact completed-task state only; never raw worker transcripts.

Fresh workers reduce context contamination. Disk state, not chat history, carries progress.

## Native execution loop

### 1. Select

```bash
python <skill-dir>/scripts/planctl_concise.py next --plan <plan-path> --json
```

### 2. Claim

Choose a route, then:

```bash
python <skill-dir>/scripts/planctl_concise.py claim \
  --plan <plan-path> \
  --task 001 \
  --route '{"provider":"codex","tier":"standard","model":"...","effort":"medium"}'
```

### 3. Dispatch one fresh worker

Prompt with only:

- repository root;
- task id and task-definition path;
- instruction to read exactly the context/learning files listed there;
- checkpoint controller path;
- permission to inspect/edit relevant repository files;
- completion-report schema path.

Do not paste the original request, full plan, study, manifest, TODO list, prior reports, logs, or future tasks.

The compact task file contains only execution-relevant information: objective, context/learnings, checkpoints, scope, non-obvious guidance, acceptance, validation, and narrow publishable learning topics.

### 4. Checkpoint

```bash
python <skill-dir>/scripts/planctl_concise.py subtask-start \
  --plan <plan-path> --task 001 --subtask S001

python <skill-dir>/scripts/planctl_concise.py subtask-complete \
  --plan <plan-path> --task 001 --subtask S001
```

Use `subtask-reset` only when that checkpoint must be deliberately redone. Never edit task Markdown for state.

### 5. Validate independently

The worker report is evidence, not acceptance. The orchestrator must:

1. verify exact context/learning read lists;
2. verify completed required subtasks;
3. run every task validation command from the repository root;
4. keep full command output in logs and only bounded diagnostic tails in state.

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

A completion report is deliberately bounded: summary <= 360 chars; validation detail <= 600; risks/follow-ups <= 8 items of 240 chars; reusable learning guidance <= 320 chars. Empty risk/follow-up arrays are preferred to boilerplate.

On completion, only the compact summary/risks/follow-ups needed for final handoff are promoted into manifest task state. Raw provider output remains in result/log files inside the ephemeral plan workspace.

## Strict external runner

From a terminal/CI outside a nested provider invocation:

```bash
python <skill-dir>/scripts/run_concise.py --plan <plan-path>
```

Useful flags remain compatible with `run_isolated.py`:

```bash
python <skill-dir>/scripts/run_concise.py --plan <plan-path> --dry-run
python <skill-dir>/scripts/run_concise.py --plan <plan-path> --once --no-cleanup
python <skill-dir>/scripts/run_concise.py --plan <plan-path> --provider codex
python <skill-dir>/scripts/run_concise.py --plan <plan-path> --no-wait
```

The runner validates state, starts a new non-persistent provider process per TODO, checks the report, reruns deterministic validation, materializes only validated predeclared learnings, escalates only on technical evidence, and cleans planning state after the final handoff.

## State commands

```bash
python <skill-dir>/scripts/planctl_concise.py validate --plan <plan-path>
python <skill-dir>/scripts/planctl_concise.py audit --plan <plan-path>
python <skill-dir>/scripts/planctl_concise.py status --plan <plan-path>
python <skill-dir>/scripts/planctl_concise.py status --plan <plan-path> --json
python <skill-dir>/scripts/planctl_concise.py reset --plan <plan-path> --task 001
```

`TODO.md` remains one line per task. `manifest.json` is the authoritative machine state.

## Failure and escalation

Classify before changing the route:

- **technical:** implementation/test/report/tool failure caused by the attempted solution;
- **environmental actionable:** repository/toolchain issue that the worker can repair within scope;
- **provider availability/usage:** retry/fallback without counting a technical failure;
- **planning invalidation:** evidence disproves a material requirement, dependency, context boundary, or validation assumption — stop downstream work and replan.

Persist the smallest diagnostic excerpt that can guide the next attempt plus a log reference when available. Do not copy full logs into `last_error`.

Escalate effort/tier/provider only when the failure evidence justifies it. Do not preemptively route every TODO to the strongest model.

## Validated learning

After a source TODO passes deterministic validation, it may publish only learnings that:

- target a predeclared untouched future TODO;
- match predeclared topics;
- state one concrete code/procedure/decision/pitfall/validation finding;
- cite repository symbols/paths/commands;
- save meaningful rediscovery cost.

No transcript, generic advice, or plan history belongs in learning files.

## Final handoff

After all TODOs complete:

1. reload final manifest state;
2. construct `SUMMARY_INPUT.json` from goal, per-task compact completion memory, validation status, changed files, and bounded git status/diff stat;
3. generate a concise handoff from that input only;
4. mark summary generated;
5. clear lifecycle active state;
6. delete only the sentinel-protected plan workspace unless retention was explicitly requested.

Never concatenate raw worker reports or logs into the final summarizer prompt.

## Safety

- Preserve unrelated working-tree changes.
- Never use cleanup to revert implementation output.
- Keep plan artifacts under the configured plan work root.
- Reject symlink/path escapes through existing lifecycle/plan guards.
- Retain plan state when execution, final validation, or summary generation fails so resume remains possible.
