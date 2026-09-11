# Execution workflow

Use this reference only after the **final implementation plan** is approved. Primary-plan execution follows `PRIMARY_PLANNING.md`; final planning rules live in `PLANNING_PROTOCOL.md`; model escalation lives in `MODEL_ROUTING.md`; evolving cross-TODO contracts live in `SHARED_PATTERNS.md` when present.

## Roles

- **Orchestrator:** authoritative plan state, scheduling, pattern assignment, validation, escalation, final handoff, cleanup.
- **Worker:** one TODO, assigned context/learnings/patterns, repository evidence needed for that TODO, structured report.
- **Summarizer:** compact completed-task and current-pattern state only; never raw worker transcripts.

Fresh workers reduce context contamination. Disk state, not chat history, carries progress.

## Native execution loop

### 1. Select

```bash
python <skill-dir>/scripts/planctl_concise.py next --plan <plan-path> --json
```

If `<plan>/patterns/registry.json` exists, validate patterns before dispatch:

```bash
python <skill-dir>/scripts/patternctl.py validate --plan <plan-path>
python <skill-dir>/scripts/patternctl.py assignment --plan <plan-path> --task 001
```

The assignment command returns only the exact pattern files/revisions for that TODO.

### 2. Claim

Choose the actual route from the TODO's logical recommendation and its recorded `failure_classes` (the runner does this with `routingctl.route_rungs` + `escalation_step`), then:

```bash
python <skill-dir>/scripts/planctl_concise.py claim \
  --plan <plan-path> \
  --task 001 \
  --route '{"provider":"codex","tier":"standard","model":"...","effort":"medium"}'
```

### 2b. Design phase (only when the TODO declares `design_route`)

Before the implementation worker, dispatch a design worker at `design_route` with the task definition, its assigned context/learnings/patterns, and permission to write exactly `<plan>/tasks/<id>.design.md` (<= 6000 chars: approach, decisions, contracts, ordered steps mapped to checkpoint ids, validation strategy). The runner accepts the note only with a `completed` report and a non-empty file, records `design_phase.completed`, releases the claim so the design attempt does not consume an implementation attempt, and appends `Design note: <path>` to the implementation prompt. A reset discards the note.

### 3. Dispatch one fresh worker

Prompt with only:

- repository root;
- task id and task-definition path;
- instruction to read exactly the context/learning files listed there;
- when patterns exist, the task's assignment file and exactly the pattern files returned by `patternctl assignment`;
- checkpoint controller path;
- permission to inspect/edit relevant repository files;
- completion-report schema path.

Do not paste the original request, full plan, study, manifest, TODO list, primary-plan package, prior reports, logs, future tasks, or unassigned patterns.

The worker must report exact pattern ids/revisions read. Pattern files are normative current contracts, not broad background context.

### 4. Checkpoint

```bash
python <skill-dir>/scripts/planctl_concise.py subtask-start \
  --plan <plan-path> --task 001 --subtask S001

python <skill-dir>/scripts/planctl_concise.py subtask-complete \
  --plan <plan-path> --task 001 --subtask S001
```

Use `subtask-reset` only when that checkpoint must deliberately be redone. Never edit task Markdown for state.

### 5. Handle shared-pattern evidence

If implementation reveals that an assigned shared contract is unsafe, impossible, incompatible, or materially wrong:

- do not silently diverge;
- capture concrete evidence;
- decide whether the change is local (no pattern revision), a genuine shared-contract revision, or full planning invalidation;
- for a genuine shared revision, update through `patternctl.py`, not by editing pattern Markdown.

```bash
python <skill-dir>/scripts/patternctl.py update \
  --plan <plan-path> \
  --pattern PAT001 \
  --contract-file /tmp/PAT001-v2.json \
  --reason "Concrete implementation evidence" \
  --changed-by-task 001
```

The controller increments the revision and resets only completed signatories that adopted an older revision. Pending signatories will consume the latest revision later. It refuses to revise while another affected signatory is actively executing stale instructions.

A pattern revision is not automatically a full replan. Replan only if evidence changes requirements, task boundaries, dependencies, architecture, or validation strategy beyond the contract itself.

### 6. Validate independently

The worker report is evidence, not acceptance. The orchestrator must:

1. verify exact context/learning/pattern read lists;
2. verify completed required subtasks;
3. verify the worker implemented the current assigned pattern revisions;
4. run every task validation command from repository root;
5. keep full command output in logs and only bounded diagnostic tails in state.

### 7. Complete, then record pattern adoption

Success:

```bash
python <skill-dir>/scripts/planctl_concise.py complete \
  --plan <plan-path> \
  --task 001 \
  --report <plan-path>/results/001.json \
  --result-file results/001.json
```

If patterns exist:

```bash
python <skill-dir>/scripts/patternctl.py adopt --plan <plan-path> --task 001
python <skill-dir>/scripts/patternctl.py validate --plan <plan-path>
```

If adoption fails, reset the TODO rather than leaving a completed task with unknown pattern compliance.

Functional failure — always classify the evidence so the next route is chosen from it, not from a retry count:

```bash
python <skill-dir>/scripts/planctl_concise.py fail \
  --plan <plan-path> --task 001 \
  --reason "Focused failure evidence or log reference" \
  --failure-class semantic
```

| `--failure-class` | When | Next route |
|---|---|---|
| `mechanical` | detail/tool/test slip the same understanding would fix | repeat once, then +1 rung |
| `semantic` | wrong approach or reasoning gap (also: claimed completion but deterministic validation failed) | next stronger tier |
| `environmental` | toolchain/repository issue outside the task | unchanged; repair the environment |
| `budget` | turn/token budget exhausted | repeat once from checkpoints, then +1 |
| `plan_defect` | task boundary/requirement/dependency is wrong | task blocked; replan |
| `unknown` (default) | no report/invalid report | +1 rung |

The strict runner derives the class from the worker report's `failure_class`, the validation outcome, and budget patterns automatically.

Usage/rate limit:

```bash
python <skill-dir>/scripts/planctl_concise.py fail \
  --plan <plan-path> --task 001 \
  --reason "Provider usage limit" --rate-limited
```

Quota/rate/capacity interruption is not a semantic escalation signal.

## Strict external runner

`run_concise.py` remains the deterministic task-state runner. Integrations that use shared patterns must wrap dispatch/completion with the `patternctl assignment`, `adopt`, and `validate` hooks above until those hooks are folded into a future runner schema.

Useful ordinary commands:

```bash
python <skill-dir>/scripts/run_concise.py --plan <plan-path>
python <skill-dir>/scripts/run_concise.py --plan <plan-path> --dry-run
python <skill-dir>/scripts/run_concise.py --plan <plan-path> --once --no-cleanup
python <skill-dir>/scripts/run_concise.py --plan <plan-path> --provider codex
python <skill-dir>/scripts/run_concise.py --plan <plan-path> --provider antigravity
```

## State commands

```bash
python <skill-dir>/scripts/planctl_concise.py validate --plan <plan-path>
python <skill-dir>/scripts/planctl_concise.py audit --plan <plan-path>
python <skill-dir>/scripts/planctl_concise.py status --plan <plan-path>
python <skill-dir>/scripts/planctl_concise.py reset --plan <plan-path> --task 001
python <skill-dir>/scripts/patternctl.py status --plan <plan-path>
python <skill-dir>/scripts/patternctl.py validate --plan <plan-path>
```

`TODO.md` remains one line per task. `manifest.json` is authoritative for ordinary task state; `patterns/registry.json` is authoritative for pattern revisions/signatures.

## Failure and escalation

Classify before changing route:

- **technical:** implementation/test/report/tool failure caused by the attempted solution — record it as `mechanical` (same understanding would fix it) or `semantic` (the approach was wrong);
- **environmental actionable:** repository/toolchain issue repairable within scope — `environmental`, route unchanged;
- **budget:** the worker ran out of turns/tokens — `budget`, resume from checkpoints;
- **provider availability/usage:** retry/fallback without counting a technical failure (`--rate-limited`);
- **pattern evolution:** current shared contract must legitimately change; revise and invalidate affected signatories only;
- **planning invalidation:** evidence disproves a material requirement, dependency, context boundary, architecture assumption, or validation strategy — `plan_defect`: stop downstream work and replan.

Persist the smallest diagnostic excerpt that can guide the next attempt plus a log reference. The ladder (`MODEL_ROUTING.md` §6, provider rungs in the active provider file) climbs only from these classes; once evidence asks for a rung above the top on the last provider, the runner blocks the TODO (`ladder_exhausted`) so it is replanned rather than retried at the strongest route until `max_attempts`. Optional per-worker guards: `claude.max_turns`, `claude.max_budget_usd`, and `codex.rollout_token_budget` in `orchestrator.config.json`.

## Validated learning

After a source TODO passes deterministic validation, it may publish only learnings that:

- target a predeclared untouched future TODO;
- match predeclared topics;
- state one concrete code/procedure/decision/pitfall/validation finding;
- cite repository symbols/paths/commands;
- save meaningful rediscovery cost.

Do not use a learning file for a shared normative rule that must update already-completed consumers. That belongs in the pattern registry.

## Final handoff

After all TODOs complete:

1. reload final manifest state;
2. if a pattern registry exists, require `patternctl validate` and include current pattern ids/revisions in compact summary input;
3. construct `SUMMARY_INPUT.json` from goal, per-task compact completion memory, validation status, changed files, pattern summary, and bounded git status/diff stat;
4. generate a concise handoff from that input only;
5. mark summary generated, clear lifecycle active state, and perform guarded cleanup.

Never concatenate raw worker reports, logs, source fragments, or primary-plan digests into the final summarizer prompt.

## Safety

- Preserve unrelated working-tree changes.
- Never use cleanup to revert implementation output.
- Keep plan artifacts under configured plan work root.
- Reject symlink/path escapes through existing lifecycle/plan guards.
- Retain plan state when execution, pattern adoption/validation, final validation, or summary generation fails so resume remains possible.
