# Plan and Execute

**Turn large coding requests into evidence-backed, context-isolated, resumable implementation plans.**

`plan-and-execute` studies the complete request and repository before planning, creates requirements-traceable TODOs, gives each TODO a fresh worker context, persists subtask checkpoints, validates implementation independently, and selectively forwards only useful verified learnings to similar future TODOs.

[Leia em Português](README.pt-BR.md)

## Supported AI workers

| Worker | Execution support | Standard skill install | Default route | Notes |
|---|---:|---:|---:|---|
| Claude Code | Yes | Yes | First | Standard quick-start target |
| OpenAI Codex | Yes | Yes | Second | Standard quick-start target |
| Google Gemini CLI | Yes | No | Opt-in | Fresh headless CLI process |
| Qwen Code | Yes | No | Opt-in | Fresh headless CLI process |
| Kimi Code CLI | Yes | No | Opt-in | Fresh prompt-mode CLI process |
| Trae Agent | Yes | No | Opt-in | Fresh `trae-cli run` process |

The npm installer intentionally installs the skill only for **Claude Code**, **Codex**, or **both**. Gemini, Qwen, Kimi, and Trae are optional execution backends configured inside a plan; they are not silently added to the default provider order.

## Quick start: Claude Code and Codex

Requirements:

- Node.js 18.17 or newer;
- Python 3.10 or newer;
- Claude Code and/or Codex installed and authenticated.

Install in the current workspace for both standard agents:

```bash
npx @luizcgvrj/plan-and-execute install both
```

Or install for one agent:

```bash
npx @luizcgvrj/plan-and-execute install claude
npx @luizcgvrj/plan-and-execute install codex
```

Install in your user profile:

```bash
npx @luizcgvrj/plan-and-execute install both --global
```

Then invoke the skill from Claude Code or Codex with a large implementation request, a requirements-file path, or no arguments. With no arguments it resumes the unique unfinished implementation first; it creates a guided request draft only when the workspace is idle.

## Why TODO boundaries matter

A fresh worker should receive one coherent semantic problem, not an arbitrary bundle of files or everything mentioned in the same paragraph.

Suppose a request asks for:

- a complete person CRUD with its own entity, service, controller, validation, and tests;
- a complete store CRUD with a separate entity, service, controller, validation, and tests.

When the two domains do not share business invariants, transactions, lifecycle state, or a meaningful joint validation boundary, they belong in **separate TODOs**. The person worker's chat history and exploratory context do not materially help the store worker.

The opposite rule also matters: do not create one TODO per file. Tightly coupled entity, service, controller, migration, and focused tests may remain together when they implement one behavior and benefit from the same working context.

Schema v4 requires every task to record a `context_boundary`:

```json
{
  "shared_context": [
    "The service, controller, and tests implement one person-registration contract."
  ],
  "why_one_todo": "Splitting these edits would duplicate domain rediscovery and weaken focused validation.",
  "separate_from": [
    "Store CRUD has an independent model, rule set, and test boundary."
  ]
}
```

An independent plan reviewer must approve `context_boundaries_sound` before execution starts.

## Resumable subtasks inside every TODO

Each schema-v4 task definition contains its own stable checklist. The authoritative state lives in `manifest.json`; Markdown task files are regenerated projections.

```json
{
  "subtasks": [
    {
      "id": "S001",
      "title": "Add the person persistence model",
      "objective": "Create the entity, migration, and repository operations.",
      "required": true
    },
    {
      "id": "S002",
      "title": "Implement the person API",
      "objective": "Add service rules, controller endpoints, and focused tests.",
      "required": true
    }
  ]
}
```

Workers checkpoint progress only through the controller:

```bash
python <skill-dir>/scripts/planctl.py subtask-start \
  --plan .ai-work/<plan-id> --task 001 --subtask S001

python <skill-dir>/scripts/planctl.py subtask-complete \
  --plan .ai-work/<plan-id> --task 001 --subtask S001
```

After a power failure, killed process, or provider interruption, completed subtasks remain completed and only an interrupted `in_progress` subtask returns to `pending`. Another fresh AI can continue from the first unfinished checkpoint without reading the previous conversation.

A parent TODO cannot complete until every required subtask is complete.

## Selective validated learning

Fresh contexts reduce token waste, but sometimes one TODO discovers an expensive solution that a similar later TODO should reuse. Plan-and-execute supports a narrow learning bridge without carrying the source chat forward.

The planner predeclares directional targets:

```json
{
  "learning_targets": [
    {
      "task_id": 2,
      "reason": "The store CRUD uses the same framework-specific validation adapter.",
      "topics": ["validation adapter", "focused test command"]
    }
  ]
}
```

Only after the source task passes deterministic validation may the orchestrator materialize a concise file such as:

```text
.ai-work/<plan-id>/learnings/001-to-002.md
```

A declared learning source is also a context prerequisite: the target does not start until every source that may teach it has completed. A source that found nothing reusable publishes no file, so the target pays no extra token cost.

A learning entry must be short, evidence-grounded, useful to the declared target, and classified as code, procedure, decision, pitfall, or validation. It can point to exact code, tests, commands, or a compact technical explanation.

The mechanism rejects:

- undeclared or backward targets;
- targets that already started;
- empty, oversized, or unreferenced notes;
- copied transcripts, logs, or full reports;
- file tampering, including content whose hash was manually recalculated;
- mutable execution discoveries written into immutable `CONTEXT.md` files.

Workers must report the exact `learning_files_read` list. Empty learning output creates no file and costs no future tokens.

## Adaptive study gate

The skill does not draft TODOs from a first reading. It first:

1. preserves and inventories every independently testable request part;
2. studies repository instructions, architecture, entry points, schemas, tests, CI, and relevant existing patterns;
3. decides whether current authoritative external research is materially required;
4. resolves high-impact questions and records evidence plus planning impact;
5. passes an independent study review and stopping rule;
6. converts findings into requirements, risks, constraints, and validation implications.

The canonical study is stored as `study.json` and rendered as `STUDY.md`. Planning is blocked until `studyctl.py validate-plan` succeeds.

## Progressive execution context

Plan-time shared context is deliberate and immutable:

- omit shared context by default;
- create `CONTEXT.md` only for concise information needed by every TODO;
- create `contexts/<topic>.md` only for strict multi-task subsets;
- keep information needed by one TODO in that task definition;
- keep runtime discoveries in validated learning files, not in plan-time context.

Every worker must report exactly which assigned context and learning files it read. Missing and extra reads are rejected.

## Plan workspace

A generated plan resembles:

```text
.ai-work/<plan-id>/
├── .plan-and-execute
├── manifest.json
├── orchestrator.config.json
├── REQUEST.md
├── STUDY.md
├── study.json
├── ANALYSIS.md
├── PLAN.md
├── PLAN_REVIEW.md
├── TODO.md
├── CONTEXT.md                 # optional, universal plan-time context
├── contexts/                  # optional, scoped plan-time context
├── learnings/                 # validated source-to-target runtime learnings
├── tasks/                     # one bounded task definition per TODO
├── results/
└── logs/
```

`TODO.md` stays intentionally terse. Requirements, scope, context boundary, subtasks, learning relationships, acceptance criteria, route, and validation commands live in the task definitions and manifest.

## Execution modes

### Native fresh workers

Inside Claude Code or Codex, the orchestrator may dispatch one fresh native subagent per TODO. Each worker receives only:

- its task definition;
- exact assigned plan-time context files;
- exact assigned validated learning files;
- repository instructions and source files it legitimately needs.

It does not receive the full request, whole plan, future tasks, prior transcripts, or unrelated reports.

### Strict external runner

From a terminal or CI shell:

```bash
python <skill-dir>/scripts/run_isolated.py --plan .ai-work/<plan-id>
```

The runner starts a new non-persistent provider process for each TODO, independently executes validation commands, handles escalation and provider availability, and writes bounded logs and results.

The generated default route remains:

```json
{
  "provider_order": ["claude", "codex"]
}
```

To opt into another installed and authenticated CLI, edit `orchestrator.config.json` or assign a provider to a task:

```json
{
  "provider_order": ["gemini", "qwen", "claude", "codex"]
}
```

You may also override a resume run:

```bash
pae resume --provider gemini --once
pae resume --provider qwen --once
pae resume --provider kimi --once
pae resume --provider trae --once
```

Run `pae doctor --json` to inspect installed CLIs. Optional providers are never required for the standard installation.

## Lifecycle commands

```bash
pae current                     # inspect active implementation
pae resume                      # recover and continue
pae resume --once               # execute at most one parent TODO
pae cancel                      # remove active plan state, preserve code changes
pae reset --force               # remove all recognized plan state in this workspace
```

The lifecycle controller repairs stale pointers, prevents concurrent strict runners, recovers interrupted task/subtask state, and preserves completed checkpoints.

## Safety model

Plan-and-execute does not bypass provider permissions, sandboxes, repository policies, organizational controls, or system policy.

Optional headless providers may use unattended approval modes so they can edit files and execute commands without a human prompt. Review each provider configuration carefully, use its sandbox or container isolation where available, and run only in a trusted workspace. Trae can be configured with a container; Qwen and Gemini expose their own approval and sandbox controls; Kimi workers use the documented `--auto` mode, while final summaries use `--plan`. Kimi remains opt-in and should run only in a trusted workspace.

The runner also enforces:

- one write worker at a time in a working tree;
- deterministic validation outside the worker's self-report;
- bounded task and learning context;
- guarded plan cleanup with sentinel and repository-root checks;
- no automatic destructive deployment, credential rotation, broad deletion, or irreversible migration without authorization.

## Installation and maintenance

```bash
pae status both --cwd /path/to/project
pae paths both --cwd /path/to/project
pae doctor --json
pae uninstall both --cwd /path/to/project
```

The installer uses an ownership marker and directory SHA-256. It refuses to overwrite unmanaged, modified, unrelated, or symbolic-link destinations unless the documented safety conditions are met.

Detailed installation references:

- [English installation guide](skill/plan-and-execute/references/INSTALLATION.md)
- [Guia de instalação em português](skill/plan-and-execute/references/INSTALLATION.pt-BR.md)

## Development

```bash
npm run check
```

This runs generated-artifact cleanup, skill/package validation, Node tests, and all Python self-tests, including context isolation, task memory, lifecycle recovery, study evidence, and provider adapter coverage.

Key references:

- [Adaptive study](skill/plan-and-execute/references/ADAPTIVE_STUDY.md)
- [Planning protocol](skill/plan-and-execute/references/PLANNING_PROTOCOL.md)
- [Plan schema](skill/plan-and-execute/references/PLAN_SPEC.md)
- [Execution context](skill/plan-and-execute/references/EXECUTION_CONTEXT.md)
- [Workflow](skill/plan-and-execute/references/WORKFLOW.md)
- [Lifecycle](skill/plan-and-execute/references/LIFECYCLE.md)
- [Model routing](skill/plan-and-execute/references/MODEL_ROUTING.md)

## License

MIT. See [LICENSE](LICENSE).
