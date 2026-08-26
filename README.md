# Plan and Execute

**Turn large coding requests into a reviewed, traceable execution plan — then run each task in a fresh, focused agent context.**

Plan and Execute helps Claude Code and Codex handle migrations, refactors, multi-workstream features, and other changes that are too large for a single chat context. It studies the full request and repository first, proves that every requirement is covered, splits oversized work recursively, validates every task independently, and keeps the implementation resumable on disk.

What you gain:

- fewer requirements lost between planning and implementation;
- smaller worker contexts with one task definition at a time;
- deterministic validation instead of “the agent says it is done”;
- model/effort escalation only when technical evidence justifies it;
- safe resume after interruptions or provider limits;
- a compact TODO list without hiding the detailed task contracts;
- one install flow for Claude Code, Codex, or both.

[Português](README.pt-BR.md)

## Quick start

### 1. Install for Claude Code and Codex

For your user profile:

```bash
npx --yes --package=github:heavydevs/plan-and-execute \
  plan-and-execute install --agent both --scope user
```

Or only in the current workspace:

```bash
npx --yes --package=github:heavydevs/plan-and-execute \
  plan-and-execute install --agent both --scope workspace
```

### 2. Start a large request

Claude Code:

```text
/plan-and-execute
```

Codex:

```text
$plan-and-execute
```

With no arguments, the skill creates a guided Markdown request file and opens it in your editor. When running from VS Code, it reuses the active VS Code window when the `code` CLI is available.

Write the complete request, save the file, then choose:

```text
Continue — I finished writing the request
```

The skill moves that draft into the execution workspace as `REQUEST.md`, studies it and the repository, creates and reviews the development plan, passes its quality gates, and starts execution.

### 3. Or pass the request directly

Inline request:

```text
$plan-and-execute Migrate authentication to OAuth, preserve password login during rollout, add automated tests, and document rollback.
```

Requirements file:

```text
$plan-and-execute docs/oauth-migration-request.md
```

A caller-owned file is copied into the plan and preserved at its original location.

## How it works

```text
complete request
      ↓
request parts (P001, P002, ...)
      ↓
requirements (R001, R002, ...)
      ↓
reviewed executable TODOs
      ↓
one fresh worker per TODO
      ↓
independent validation
      ↓
economical final summary + safe cleanup
```

Before implementation, the orchestrator:

1. reads the entire request;
2. inspects relevant code, tests, architecture, schemas, build files, and CI commands;
3. researches authoritative sources when current or version-sensitive facts matter;
4. inventories every request part and requirement;
5. recursively splits each workstream until every leaf task has one coherent outcome;
6. rejects executable tasks rated `extreme`;
7. asks a fresh reviewer to challenge coverage, dependencies, atomicity, and validation;
8. runs deterministic `validate` and `audit` gates;
9. starts execution only after the plan passes.

During implementation, each worker sees one task definition rather than the whole chat or future tasks. The orchestrator reruns the required validation commands before marking that task complete.

## Request intake modes

### Guided editor flow

Invoke the skill without arguments. It creates:

```text
.ai-work/intake/request-YYYYMMDD-HHMMSS.md
```

The top of the file contains short instructions. The rest provides sections for goals, requirements, constraints, context, tests, and definition of done.

After you confirm that editing is finished, the file becomes:

```text
.ai-work/<plan-id>/REQUEST.md
```

The temporary intake copy is removed only after the plan has safely preserved and validated it.

### Existing file

Pass one existing regular file path as the complete invocation argument. The skill validates the file, reads it in full, and copies it to `REQUEST.md`. Directories, missing files, and symbolic links are rejected.

### Inline text

Any other non-empty arguments are treated as the complete inline request.

## Concise TODO, detailed task contracts

`TODO.md` is intentionally easy to scan:

```markdown
# TODO — OAuth migration

- [x] **001** — Add OAuth persistence model
- [ ] **002** — Implement authorization-code callback _(in progress)_
- [ ] **003** — Preserve password-login compatibility
- [ ] **004** — Add migration and rollback tests
```

It contains one line per item. Provider, model, reasoning effort, complexity, requirement mappings, dependencies, acceptance criteria, and validation commands live in each file under `tasks/` and in `manifest.json`.

## Installation options

### Directly from GitHub

```bash
npx --yes --package=github:heavydevs/plan-and-execute \
  plan-and-execute install --agent both --scope user
```

### From npm after publication

The current package name remains `@luizcgvrj/plan-and-execute`:

```bash
npx --yes @luizcgvrj/plan-and-execute \
  install --agent both --scope user
```

### Global CLI

```bash
npm install --global @luizcgvrj/plan-and-execute
pae install both --global
```

`pae` is the short alias for `plan-and-execute`.

### Targets

| Agent | Workspace | User profile |
| --- | --- | --- |
| Claude Code | `.claude/skills/plan-and-execute` | `~/.claude/skills/plan-and-execute` |
| Codex | `.agents/skills/plan-and-execute` | `~/.agents/skills/plan-and-execute` |

See [the installation guide](skill/plan-and-execute/references/INSTALLATION.md) for manual copies, symlinks, updates, removal, and Windows examples.

## Installer commands

```bash
# Install both agents in the current workspace
pae install both --local

# Install only Claude for the current user
pae install claude --global

# Install Codex in another workspace
pae install codex --cwd /path/to/project

# Inspect targets and installation state
pae paths both --global
pae status both --global

# Diagnose Node, Python, and provider CLIs
pae doctor

# Preview without changing files
pae install both --local --dry-run

# Remove managed copies
pae uninstall both --global
```

The installer has no runtime dependencies and no `postinstall` mutation. It writes only after an explicit `install` command. A local marker and content hash protect manually modified installations from accidental overwrite or removal.

## Execution modes

### Native mode

Use the active Claude Code or Codex chat. The orchestrator creates a fresh native subagent for each runnable task and passes only that task definition.

### Strict external runner

Use a terminal outside the active nested provider session when you need a new process for every attempt, exact CLI model routing, or automatic rate-limit waiting:

```bash
python .agents/skills/plan-and-execute/scripts/run_isolated.py \
  --plan .ai-work/<plan-id>
```

or:

```bash
python .claude/skills/plan-and-execute/scripts/run_isolated.py \
  --plan .ai-work/<plan-id>
```

Preserve the plan after a successful trial run:

```bash
python <skill-dir>/scripts/run_isolated.py \
  --plan .ai-work/<plan-id> \
  --no-cleanup
```

## Plan workspace

```text
.ai-work/<plan-id>/
├── REQUEST.md                 # when the request came from a file
├── ANALYSIS.md
├── PLAN.md
├── PLAN_REVIEW.md
├── TODO.md                    # one concise line per task
├── manifest.json              # source of truth
├── orchestrator.config.json
├── tasks/                     # detailed isolated task contracts
├── results/
└── logs/
```

The plan validator checks request hashes, traceability, task complexity, review approval, dependencies, task files, acceptance criteria, and validation commands.

## Model routing and recovery

Tasks use logical tiers:

```text
economy → standard → strong → max
```

The concrete provider/model mapping is stored in `orchestrator.config.json` so it can evolve without rewriting every task. Functional failures can increase effort, model tier, and eventually provider. Rate limits or exhausted credits preserve the task as pending and do not count as technical failures.

Restarting the runner resumes from `manifest.json`. A stopped computer or process cannot restart itself; launch the same command again or use an external service/CI scheduler.

## Safety model

- write-heavy tasks run sequentially unless isolated in separate worktrees;
- workers do not receive the full plan or future task definitions;
- deterministic validation runs outside the worker;
- a planning defect triggers replanning instead of blind model escalation;
- cleanup requires a plan sentinel, completed tasks, and a generated summary;
- cleanup removes only the exact `.ai-work/<plan-id>` directory;
- implementation files, tests, commits, and unrelated plans are preserved.

## Development

Requirements:

- Node.js 18.17 or newer for the installer;
- Python 3.10 or newer for skill scripts;
- Claude Code and/or Codex for real agent execution.

Run all checks:

```bash
npm ci
npm run check
npm pack --dry-run
```

The checks cover the Node installer and CLI, request-file/editor intake, request copy/move semantics, traceability, recursive-planning gates, state transitions, model escalation, strict-runner simulation, validation, summarization, and guarded cleanup.

## Documentation

- [Portuguese README](README.pt-BR.md)
- [Request intake](skill/plan-and-execute/references/INTAKE.md)
- [Deep planning protocol](skill/plan-and-execute/references/PLANNING_PROTOCOL.md)
- [Execution workflow](skill/plan-and-execute/references/WORKFLOW.md)
- [Plan specification](skill/plan-and-execute/references/PLAN_SPEC.md)
- [Model routing](skill/plan-and-execute/references/MODEL_ROUTING.md)
- [Installation](skill/plan-and-execute/references/INSTALLATION.md)
- [Publishing](docs/PUBLISHING.md)

## License

MIT.
