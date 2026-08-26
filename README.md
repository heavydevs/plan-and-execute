# Plan and Execute

**Turn large coding requests into an evidence-backed, reviewed, traceable execution plan, then run each TODO in a fresh, narrowly scoped context.**

Plan and Execute is a reusable skill and CLI for Claude Code and Codex. It is designed for migrations, refactors, multi-workstream features, architecture-sensitive changes, and test-heavy implementations that should not depend on one long conversation.

It provides:

- guided request capture;
- mandatory repository study and adaptive external research;
- request-part → requirement → TODO traceability;
- recursive decomposition and independent plan review;
- deliberately minimal global or task-scoped worker context;
- one fresh worker process or subagent per TODO;
- deterministic validation outside the worker;
- resumable state after power, network, terminal, or process interruption;
- guarded `current`, `resume`, `cancel`, and `reset` lifecycle commands;
- model/provider escalation based on technical evidence;
- economical final summarization and safe cleanup.

[Português](README.pt-BR.md)

## Quick start

### 1. Install for Claude Code and Codex

User profile:

```bash
npx --yes --package=github:heavydevs/plan-and-execute \
  plan-and-execute install --agent both --scope user
```

Current workspace only:

```bash
npx --yes --package=github:heavydevs/plan-and-execute \
  plan-and-execute install --agent both --scope workspace
```

### 2. Start or resume work

Claude Code:

```text
/plan-and-execute
```

Codex:

```text
$plan-and-execute
```

The no-argument invocation first inspects `.ai-work`:

- when one unfinished implementation exists, it resumes from disk;
- when a live runner already owns the plan, it reports that state instead of starting a duplicate;
- when several unfinished plans exist, it stops rather than choosing silently;
- only when the workspace is idle does it create and open a guided request file.

### 3. Other request modes

Inline request:

```text
$plan-and-execute Migrate authentication to OAuth, preserve password login during rollout, add tests, and document rollback.
```

Requirements file:

```text
$plan-and-execute docs/oauth-migration-request.md
```

A caller-owned file is copied into the plan and preserved at its original location.

## How the workflow fits together

```text
complete request
      ↓
adaptive internal/external study
      ↓
request parts and requirements
      ↓
recursive TODO graph
      ↓
minimal execution-context decision
      ↓
fresh plan review + deterministic gates
      ↓
one fresh worker per TODO
      ↓
independent validation + persisted state
      ↓
final summary + safe lifecycle cleanup
```

## Adaptive study gate

Internal repository study is always required. The planner inspects relevant instructions, architecture, implementation, tests, schemas, interfaces, build files, CI, and explanatory history before drafting requirements or TODOs.

External research is conditional. It becomes required when, for example:

- the user explicitly requests verification;
- the domain is unfamiliar;
- behavior depends on an exact or current version;
- authentication, authorization, cryptography, sandboxing, or another security contract is material;
- the repository lacks a required contract;
- internal evidence conflicts;
- a technology/provider choice is needed;
- a wrong assumption would create high risk.

The study records material questions, evidence locations, findings, planning impact, external trigger decisions, source authority/version/date, synthesis, an independent sufficiency review, and a stopping rule.

Before planning:

```bash
python <skill-dir>/scripts/studyctl.py validate \
  --spec /tmp/study-spec.json
```

After plan creation:

```bash
python <skill-dir>/scripts/studyctl.py attach \
  --spec /tmp/study-spec.json \
  --plan .ai-work/<plan-id>

python <skill-dir>/scripts/studyctl.py validate-plan \
  --plan .ai-work/<plan-id>
```

The attachment gate proves that findings affected plan constraints, requirements, risks, or validation instead of becoming unused research notes.

See [Adaptive study](skill/plan-and-execute/references/ADAPTIVE_STUDY.md).

## Progressive execution context

Every TODO still runs in a fresh worker. Schema v3 adds a narrow, explicit mechanism for the small amount of information that genuinely needs to cross task boundaries.

The planner decides after the task graph exists:

1. **Needed by every TODO:** it may create `CONTEXT.md`.
2. **Needed by at least two but fewer than all TODOs:** it may create `contexts/<topic>.md` and assign it only to those task definitions.
3. **Needed by one TODO:** it remains in that task definition.
4. **Not materially needed:** it is omitted.

Omission is the default. Context files must not contain the full request, study, plan, task status, generic advice, or information that is merely interesting. Each item is one operational line grounded by source references, and deterministic limits reject excessive length, duplicates, broad assignment, single-task files, tampering, and context leakage.

A task definition contains:

```markdown
## Assigned execution context

- `.ai-work/<plan-id>/CONTEXT.md`
- `.ai-work/<plan-id>/contexts/oauth-rollout.md`
```

The worker must read exactly those files, no others, and report:

```json
{
  "context_files_read": [
    "CONTEXT.md",
    "contexts/oauth-rollout.md"
  ]
}
```

The orchestrator rejects missing or extra reads before accepting the worker result. This preserves high-quality shared constraints without sending the request, complete plan, prior chat, or irrelevant context to every worker.

See [Progressive execution context](skill/plan-and-execute/references/EXECUTION_CONTEXT.md).

## Traceable planning

The planner creates stable ids:

```text
request part P001
      ↓
requirement R001
      ↓
TODO 001
```

Every request part must be covered by a requirement. Every requirement must be covered by at least one executable TODO. Each TODO maps back to requirements and includes:

- one objective;
- scope in/out;
- expected files;
- dependencies;
- complexity and atomicity rationale;
- acceptance criteria;
- deterministic validation commands;
- provider, model tier, and reasoning effort;
- generated context assignments.

Executable `extreme` tasks are rejected and must be split. A `high` task requires a substantive reason why further decomposition would weaken implementation or validation.

## Fresh workers and context isolation

Strict runner mode starts a new, non-persistent provider process for each TODO:

- Claude Code uses `--no-session-persistence`;
- Codex uses `exec --ephemeral`;
- the worker receives one task definition and only its assigned context files;
- it cannot read the complete plan, future tasks, analysis, study, manifest, or previous worker reports;
- deterministic checks are rerun by the orchestrator;
- task state is persisted before the next worker starts.

This makes the orchestrator operationally stateless: a new terminal, chat, or provider can reconstruct progress from the plan workspace instead of prior conversation history.

## Resumable lifecycle

The active pointer is:

```text
.ai-work/.active-plan.json
```

`manifest.json` remains authoritative. A strict runner owns an atomic lease under the plan directory so duplicate writers do not start concurrently.

Useful commands:

```bash
pae current
pae resume
pae resume --once
pae resume --provider codex
pae resume --no-wait
pae resume --no-cleanup
pae cancel
pae cancel --all
pae reset
```

When an interrupted process leaves a TODO as `in_progress`, resume returns it to `pending` without counting a technical failure, preserves partial source changes, and sends the same bounded task to a fresh worker for repair and revalidation.

`cancel` and `reset` remove recognized planning, context, logs, results, intake, lease, and lifecycle state. They intentionally preserve repository implementation changes; use Git explicitly when source changes must also be reverted.

See [Resumable lifecycle](skill/plan-and-execute/references/LIFECYCLE.md).

## Concise TODO, detailed task contracts

`TODO.md` is a status index:

```markdown
# TODO — OAuth migration

- [x] **001** — Add OAuth persistence model
- [ ] **002** — Implement authorization callback _(in progress)_
- [ ] **003** — Preserve password-login compatibility
- [ ] **004** — Add migration and rollback tests
```

Provider, model, effort, requirements, dependencies, context assignments, acceptance criteria, and validation commands remain in task definitions and `manifest.json`.

## Plan workspace

```text
.ai-work/
├── .active-plan.json              # active lifecycle pointer
└── <plan-id>/
    ├── .orchestrator-plan         # guarded plan sentinel
    ├── REQUEST.md                 # when request came from a file
    ├── study.json
    ├── STUDY.md
    ├── ANALYSIS.md
    ├── PLAN.md
    ├── PLAN_REVIEW.md
    ├── TODO.md
    ├── CONTEXT.md                 # optional, universal context only
    ├── contexts/                  # optional, strict task subsets only
    ├── manifest.json              # source of truth
    ├── orchestrator.config.json
    ├── tasks/
    ├── results/
    └── logs/
```

## Installation targets

| Agent | Workspace | User profile |
|---|---|---|
| Claude Code | `.claude/skills/plan-and-execute` | `~/.claude/skills/plan-and-execute` |
| Codex | `.agents/skills/plan-and-execute` | `~/.agents/skills/plan-and-execute` |

Global CLI:

```bash
npm install --global @luizcgvrj/plan-and-execute
pae install both --global
```

Installer commands:

```bash
pae install both --local
pae install claude --global
pae install codex --cwd /path/to/project
pae paths both --global
pae status both --global
pae doctor
pae install both --local --dry-run
pae uninstall both --global
```

The installer has no runtime dependencies and performs no implicit post-install mutation. A marker and directory hash protect locally modified managed installations.

## Model routing and recovery

Tasks use logical tiers:

```text
economy → standard → strong → max
```

Technical failures increase reasoning effort, then model tier, then provider when fallback is allowed. Rate limits, exhausted credits, and temporary capacity do not count as technical failures.

See [Model routing](skill/plan-and-execute/references/MODEL_ROUTING.md).

## Safety model

- workers never edit plan or context artifacts;
- write-heavy TODOs run sequentially unless isolated in worktrees;
- source changes are never deleted by normal plan cleanup or lifecycle cancellation;
- context files are created only from the validated plan schema;
- a planning defect triggers full replanning rather than blind escalation;
- cleanup requires a matching sentinel, repository root, plan id, completed state, and generated summary;
- destructive or irreversible external actions remain subject to explicit safety gates.

## Development

Requirements:

- Node.js 18.17 or newer;
- Python 3.10 or newer;
- Claude Code and/or Codex for real worker execution.

Run all checks:

```bash
npm ci
npm run check
npm pack --dry-run --ignore-scripts
```

The suite covers installer/CLI behavior, adaptive study, traceability, recursive planning, context minimality and assignment, fresh-worker reports, interruption recovery, runner leases, cancellation/reset, model escalation, final summary, and guarded cleanup.

## Documentation

- [Request intake](skill/plan-and-execute/references/INTAKE.md)
- [Adaptive study](skill/plan-and-execute/references/ADAPTIVE_STUDY.md)
- [Deep planning](skill/plan-and-execute/references/PLANNING_PROTOCOL.md)
- [Progressive execution context](skill/plan-and-execute/references/EXECUTION_CONTEXT.md)
- [Plan schema](skill/plan-and-execute/references/PLAN_SPEC.md)
- [Execution workflow](skill/plan-and-execute/references/WORKFLOW.md)
- [Resumable lifecycle](skill/plan-and-execute/references/LIFECYCLE.md)
- [Model routing](skill/plan-and-execute/references/MODEL_ROUTING.md)
- [Installation](skill/plan-and-execute/references/INSTALLATION.md)

## License

MIT.
