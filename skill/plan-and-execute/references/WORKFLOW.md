# Workflow reference

## Contents

1. Roles and context boundaries
2. Deep planning workflow
3. Native subagent execution
4. Strict external-runner execution
5. State and quality commands
6. Failure, replanning, and escalation
7. Final summary and cleanup
8. Safety and operating limits

## 1. Roles and context boundaries

Use separate roles even when one provider implements all of them:

- **Analyzer/researcher:** studies the complete request, repository, tests, architecture, and any authoritative external material needed to understand the work.
- **Planner:** turns the analysis into stable requirements, workstreams, a dependency graph, and executable leaf TODOs.
- **Plan reviewer:** receives the full request, compact analysis, requirements, and draft graph in a fresh context; searches for omissions, oversized tasks, weak dependencies, and unverifiable acceptance criteria.
- **Orchestrator:** owns the approved plan graph, task state, route decisions, deterministic validation, replanning decisions, final handoff, and cleanup.
- **Worker:** receives exactly one task definition, edits implementation files, runs task-local checks, and returns a structured report.
- **Summarizer:** receives a prepared evidence bundle only after the plan succeeds and writes the final handoff using an economy-tier model.

The orchestrator may coordinate all planning state. Implementation workers must not browse plan-wide files. A fresh native subagent reduces chat-history contamination; a fresh external CLI process gives a stricter boundary. Neither boundary bypasses system policy, repository instructions, sandboxing, permissions, or organizational controls.

## 2. Deep planning workflow

Do not draft TODOs directly from the first reading of the request. Complete the following loop first.

### 2.1 Preserve and inventory the request

Read the entire request and record every independently testable or constrainable part in `request_analysis.request_parts` with stable ids such as `P001`. Include:

- requested outcomes and user-visible behavior;
- each large subrequest or workstream;
- automated-test expectations;
- compatibility, migration, performance, security, and operational constraints;
- explicit exclusions and non-goals;
- approval boundaries for destructive or irreversible work.

Do not merge unrelated outcomes merely because they appeared in one paragraph.

### 2.2 Study the repository and subject matter

Inspect the repository before choosing task boundaries. Read the closest instruction files, entry points, architecture, schemas, interfaces, build configuration, tests, fixtures, migrations, CI workflows, and existing patterns relevant to the request. Record concrete findings in `request_analysis.repository_findings`.

Use read-only exploration subagents for independent areas when that reduces context pressure. Synthesize findings into the analysis instead of passing raw exploration logs to workers.

Decide whether external research is materially needed. Use authoritative sources for unfamiliar, current, version-sensitive, protocol-sensitive, or security-sensitive facts. Record conclusions that affect the implementation, or explicitly record why external research was unnecessary.

### 2.3 Build a complete requirements inventory

Assign stable requirement ids such as `R001`. Preserve source, priority, and the originating `request_part_ids`. Requirements may come from the user, repository constraints, verified research, or an explicitly recorded inference.

Before continuing, map every request part to one or more requirement `request_part_ids` and verify that none is uncovered. Do not silently discard a difficult, ambiguous, or secondary request.

### 2.4 Decompose recursively

Group requirements into coherent workstreams, identify dependencies, then recursively split each workstream until every leaf TODO has:

- one coherent outcome;
- one bounded implementation responsibility;
- explicit in-scope and out-of-scope boundaries;
- a small enough context surface for one fresh worker;
- observable acceptance criteria;
- deterministic validation independent of the worker's success claim;
- mapped `requirement_ids`;
- a clear dependency position in the graph.

Split again when a TODO contains multiple independent outcomes, crosses unrelated subsystems, has separable migration and rollout stages, combines implementation with broad test or documentation work, contains more than one independently failing validation boundary, or would be rated `extreme`.

Do not create artificial file-by-file microtasks. Keep a technically difficult task as one `high`-complexity leaf only when it still has one coherent outcome and splitting it would create harmful handoffs or weaker validation. Record that reasoning in `atomicity_rationale`.

### 2.5 Review in a fresh context

Give the plan reviewer:

- the complete user request;
- compact repository and research findings;
- the full requirements inventory;
- the draft task graph with requirement mappings, complexity ratings, dependencies, acceptance criteria, and validation commands.

Do not assign implementation to the reviewer. Require it to challenge:

- missing, duplicated, or distorted requirements;
- request parts that have no requirement;
- requirements that have no TODO;
- TODOs that cover no requirement;
- TODOs with multiple independent outcomes;
- hidden cross-task dependencies or cycles;
- validations that cannot prove the acceptance criteria;
- high-complexity tasks whose atomicity rationale is weak;
- any `extreme` executable task;
- unsafe autostart or unresolved material questions.

Revise and repeat until all review checks are true and `unresolved_findings` is empty. Record the approved result in `plan_review`.

### 2.6 Create and gate the plan

Write a schema-v2 JSON spec following `PLAN_SPEC.md`, then run:

```bash
python <skill-dir>/scripts/planctl.py create \
  --repo-root . \
  --spec /tmp/plan-spec.json

python <skill-dir>/scripts/planctl.py validate --plan <plan-path>
python <skill-dir>/scripts/planctl.py audit --plan <plan-path>
```

Inspect `ANALYSIS.md`, `PLAN.md`, `PLAN_REVIEW.md`, and the audit output. Execution may start only after both commands succeed and no safety approval is pending.

## 3. Native subagent execution

Use native mode while the skill is running inside Claude Code or Codex.

### Select and claim the next task

```bash
python <skill-dir>/scripts/planctl.py next --plan <plan-path> --json
```

Choose the actual model route, then claim it:

```bash
python <skill-dir>/scripts/planctl.py claim \
  --plan <plan-path> \
  --task 001 \
  --route '{"provider":"claude","tier":"standard","model":"sonnet","effort":"medium"}'
```

### Dispatch a fresh worker

Use the client's native subagent mechanism. Construct a minimal worker prompt containing only:

- repository root;
- assigned task id;
- absolute or repository-relative path to its task definition;
- prohibition on reading other plan files;
- permission to read and edit relevant source and tests;
- instruction to preserve unrelated working-tree changes;
- requirement to run task-local validation;
- the completion-report schema.

Do not paste the full user request, `ANALYSIS.md`, `PLAN.md`, `PLAN_REVIEW.md`, `TODO.md`, the manifest, prior worker reports, or definitions for later tasks. The task definition must contain the bounded context needed by that worker.

### Validate independently

The worker's report is evidence, not the acceptance decision. From the orchestrator thread, execute every validation command listed in the manifest. Save command, exit code, and a concise output tail.

On success, write a JSON report under `<plan-path>/results/` and complete the task:

```bash
python <skill-dir>/scripts/planctl.py complete \
  --plan <plan-path> \
  --task 001 \
  --report <plan-path>/results/001.json \
  --result-file results/001.json
```

On functional failure, preserve the exact blocker and return the task to pending:

```bash
python <skill-dir>/scripts/planctl.py fail \
  --plan <plan-path> \
  --task 001 \
  --reason "Unit test X failed with ..."
```

For a usage or rate limit, preserve retry state without incrementing functional failures:

```bash
python <skill-dir>/scripts/planctl.py fail \
  --plan <plan-path> \
  --task 001 \
  --reason "Provider usage limit" \
  --rate-limited
```

Repeat until no runnable task remains.

## 4. Strict external-runner execution

Run strict mode from a VS Code terminal or CI shell outside a nested invocation of the same agent CLI:

```bash
python <skill-dir>/scripts/run_isolated.py --plan <plan-path>
```

The runner:

1. validates the approved plan and configuration;
2. selects the next runnable task;
3. resolves provider, model, and effort from logical routing;
4. persists the claimed state;
5. starts a new non-persistent Claude Code or Codex process;
6. names only the current task definition in the worker prompt;
7. captures provider output and logs under the plan directory;
8. re-runs deterministic validation from the repository root;
9. completes, retries, escalates, or blocks the task;
10. waits and retries usage limits without escalation;
11. generates the final summary with the configured economy route;
12. prints the summary and removes only the sentinel-protected plan directory.

Useful flags:

```bash
python <skill-dir>/scripts/run_isolated.py --plan <plan-path> --dry-run
python <skill-dir>/scripts/run_isolated.py --plan <plan-path> --once --no-cleanup
python <skill-dir>/scripts/run_isolated.py --plan <plan-path> --provider codex
python <skill-dir>/scripts/run_isolated.py --plan <plan-path> --no-wait
python <skill-dir>/scripts/run_isolated.py --plan <plan-path> --no-cleanup
```

The default configuration waits across rate-limit cycles while the runner remains alive. Interrupting it leaves disk state safe to resume with the same command.

## 5. State and quality commands

```bash
# Structural integrity, dependency graph, required planning evidence
python <skill-dir>/scripts/planctl.py validate --plan <plan-path>

# Requirement coverage, review status, and task-complexity distribution
python <skill-dir>/scripts/planctl.py audit --plan <plan-path>

# Human-readable checklist
python <skill-dir>/scripts/planctl.py status --plan <plan-path>

# Full machine-readable state
python <skill-dir>/scripts/planctl.py status --plan <plan-path> --json

# Next task whose dependencies are complete
python <skill-dir>/scripts/planctl.py next --plan <plan-path> --json

# Reset a blocked or abandoned task to pending
python <skill-dir>/scripts/planctl.py reset --plan <plan-path> --task 001

# Deterministic fallback summary
python <skill-dir>/scripts/planctl.py summary --plan <plan-path>
```

Do not edit status markers in `TODO.md`; it is regenerated from the manifest.

## 6. Failure, replanning, and escalation

Classify failures before changing the route:

- **Technical:** implementation error, test failure, invalid structured report, timeout, or tool error caused by the attempted solution.
- **Environmental but actionable:** missing dependency, unavailable service, permission issue, or corrupted workspace. Record the blocker; escalate only when a stronger model could plausibly diagnose it.
- **Provider availability:** usage limit, rate limit, temporary capacity, or exhausted credits. Wait or resume without increasing functional failures.
- **Planning defect:** missing scope, wrong dependency, oversized TODO, impossible acceptance criterion, or validation that does not prove the outcome.
- **Safety gate:** destructive or irreversible action lacking authorization. Stop and retain the plan.

Do not treat a planning defect as a normal worker failure. Pause downstream dispatch, update the analysis and requirements if needed, recursively decompose again, run a fresh review, recreate or safely revise the plan, and require `validate` plus `audit` to pass before resuming.

Use the route schedule in `MODEL_ROUTING.md` for true technical failures. Preserve failure evidence so a stronger attempt can diagnose the current repository state without reading prior chat history.

## 7. Final summary and cleanup

After every task is completed:

1. Prepare a compact summary input from plan metadata, requirement coverage, validated task reports, and diff statistics.
2. Spawn a fresh economy-tier summarizer.
3. Return the summary to the orchestrator chat or terminal.
4. Mark the summary generated:

```bash
python <skill-dir>/scripts/planctl.py mark-summary \
  --plan <plan-path> \
  --summary-file FINAL_SUMMARY.md
```

5. Clean up:

```bash
python <skill-dir>/scripts/planctl.py cleanup --plan <plan-path>
```

Cleanup verifies the sentinel, repository root, work-root location, plan id, completed state, and generated summary before deletion. It removes only `<repo>/.ai-work/<plan-id>` and removes `.ai-work` itself only when empty.

## 8. Safety and operating limits

- Do not autostart an unapproved production deployment, credential rotation, irreversible database migration, broad deletion, or similarly high-impact action.
- Do not run multiple write workers in the same working tree. Use sequential tasks or separate worktrees.
- Do not treat a model-generated success statement as validation.
- Do not let a worker rewrite the plan to make its own work appear successful.
- Do not clean up a failed or partially completed plan unless the user explicitly requests forced deletion.
- Automatic continuation requires a live host or runner process. Disk state makes restart resumable but cannot execute while the machine and all agent processes are stopped.
- Provider subscriptions, permissions, organizational policies, and sandboxes remain authoritative; this workflow does not bypass them.
