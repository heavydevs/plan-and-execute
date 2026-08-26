# Plan and Execute

**Turn large coding requests into an evidence-backed, reviewed, traceable execution plan, then run each task in a fresh focused context.**

Plan and Execute helps Claude Code and Codex handle migrations, refactors, multi-workstream features, and other changes that are too large for one chat context. Before planning, it studies the complete request and concrete repository evidence, decides whether external research is materially necessary, and blocks shallow plans whose findings were not translated into constraints, requirements, risks, and validation.

What you gain:

- mandatory internal repository study before planning;
- external research only when explicit triggers justify it;
- deterministic proof that study findings affected the plan;
- fewer requirements lost between planning and implementation;
- smaller worker contexts with one task definition at a time;
- deterministic validation instead of relying on an agent's completion claim;
- model and effort escalation only when technical evidence justifies it;
- safe resume after interruptions or provider limits;
- one install flow for Claude Code, Codex, or both.

[Portuguese](README.pt-BR.md)

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

With no arguments, the skill creates a guided Markdown request file and opens it in your editor. When VS Code is active and the `code` CLI is available, it reuses the current window.

Write the complete request, save it, then choose:

```text
Continue - I finished writing the request
```

The skill moves that draft into the execution workspace as `REQUEST.md`, passes the adaptive study gate, creates and reviews the plan, runs deterministic quality gates, and starts execution.

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
      |
      v
material questions
      |
      v
mandatory internal repository study
      |
      v
explicit external-research trigger assessment
      |-----------------------------|
      v                             v
authoritative research          research not needed
      |-----------------------------|
      v
validated evidence synthesis
      |
      v
request parts -> requirements -> reviewed TODOs
      |
      v
one fresh worker per TODO
      |
      v
independent validation
      |
      v
economical summary + safe cleanup
```

Before implementation, the orchestrator:

1. reads the entire request;
2. identifies questions that can change architecture, compatibility, risk, task boundaries, or validation;
3. inspects relevant code, tests, instructions, architecture, schemas, build files, CI, and explanatory history;
4. explicitly evaluates nine external-research triggers;
5. researches primary authoritative sources only when one or more triggers are true;
6. validates evidence sufficiency before drafting requirements or TODOs;
7. inventories every request part and requirement;
8. recursively splits each workstream until every leaf has one coherent outcome;
9. uses fresh study and plan reviewers;
10. proves that evidence was copied into plan constraints, requirements, risks, and task validation;
11. runs `studyctl validate-plan`, `planctl validate`, and `planctl audit` before execution.

During implementation, each worker receives only one task definition. The orchestrator reruns required validation commands before completing the item.

## Adaptive study gate

Internal study is always required because repository-specific instructions, versions, interfaces, and tests define the real change surface. External research is conditional rather than automatic.

External research becomes required when any of these conditions is true:

- the user explicitly requests research or verification;
- the domain is unfamiliar;
- behavior depends on an exact version or may have changed recently;
- security-sensitive behavior is involved;
- the repository lacks a material contract;
- internal evidence conflicts;
- a technology or provider must be selected;
- an incorrect assumption would be high risk.

When every trigger is false, the plan may rely exclusively on internal evidence, but it must record a substantive reason. When a trigger is true and authoritative evidence cannot be obtained, planning is blocked rather than guessed.

The study specification records:

- material questions and their resolution;
- internal evidence locations, findings, and planning impact;
- the external trigger assessment and research decision;
- authoritative external sources, version/date, and conclusions when required;
- synthesized constraints, derived requirements, risks, and validation implications;
- an independent sufficiency review and stopping rule.

Validate before planning:

```bash
python <skill-dir>/scripts/studyctl.py validate \
  --spec /tmp/study-spec.json
```

After plan creation, attach and verify exact integration:

```bash
python <skill-dir>/scripts/studyctl.py attach \
  --spec /tmp/study-spec.json \
  --plan .ai-work/<plan-id>

python <skill-dir>/scripts/studyctl.py validate-plan \
  --plan .ai-work/<plan-id>
```

The attachment gate rejects research notes that were never used. Internal findings must appear in repository analysis; external findings must appear in research analysis; synthesized constraints, requirements, and risks must appear in matching plan fields; validation implications must appear in task criteria, guidance, or commands.

See [the adaptive study protocol](skill/plan-and-execute/references/ADAPTIVE_STUDY.md) and [the study-spec example](skill/plan-and-execute/references/study-spec.example.json).

## Request intake modes

### Guided editor flow

Invoke the skill without arguments. It creates:

```text
.ai-work/intake/request-YYYYMMDD-HHMMSS.md
```

The file provides sections for goals, requirements, constraints, context, tests, and definition of done. After confirmation, it becomes:

```text
.ai-work/<plan-id>/REQUEST.md
```

The temporary draft is removed only after the plan preserves and validates it.

### Existing file

Pass one existing regular file path as the complete invocation argument. The skill validates and reads the entire file, copies it to `REQUEST.md`, and preserves the source. Directories, missing files, and symbolic links are rejected.

### Inline text

Any other non-empty arguments are treated as the complete inline request.

## Concise TODO, detailed contracts

`TODO.md` stays easy to scan:

```markdown
# TODO - OAuth migration

- [x] **001** - Add OAuth persistence model
- [ ] **002** - Implement authorization-code callback _(in progress)_
- [ ] **003** - Preserve password-login compatibility
- [ ] **004** - Add migration and rollback tests
```

Provider, model, effort, complexity, requirement mappings, dependencies, acceptance criteria, and validation commands live in task files and `manifest.json`.

## Installation options

### Directly from GitHub

```bash
npx --yes --package=github:heavydevs/plan-and-execute \
  plan-and-execute install --agent both --scope user
```

### From npm

The package name remains `@luizcgvrj/plan-and-execute`:

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
pae install both --local
pae install claude --global
pae install codex --cwd /path/to/project
pae paths both --global
pae status both --global
pae doctor
pae install both --local --dry-run
pae uninstall both --global
```

The installer has no runtime dependencies and no `postinstall` mutation. It writes only after an explicit `install` command. A local marker and content hash protect manually modified installations from accidental overwrite or removal.

## Execution modes

### Native mode

Use the active Claude Code or Codex chat. The orchestrator creates a fresh native subagent for each runnable task and passes only that task definition.

### Strict external runner

Use a terminal outside the active nested provider session when you need a fresh process for every attempt, exact CLI routing, or automatic rate-limit waiting:

```bash
python <skill-dir>/scripts/run_isolated.py \
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
|-- REQUEST.md                 # when the request came from a file
|-- study.json                 # canonical adaptive-study evidence
|-- STUDY.md                   # human-readable study evidence
|-- ANALYSIS.md
|-- PLAN.md
|-- PLAN_REVIEW.md
|-- TODO.md                    # one concise line per task
|-- manifest.json              # source of truth and study hash
|-- orchestrator.config.json
|-- tasks/                     # detailed isolated task contracts
|-- results/
`-- logs/
```

The validators check request hashes, study evidence and plan integration, traceability, task complexity, review approval, dependencies, task files, acceptance criteria, and validation commands.

## Model routing and recovery

Tasks use logical tiers:

```text
economy -> standard -> strong -> max
```

Concrete provider/model mapping lives in `orchestrator.config.json`. Functional failures can increase effort, model tier, and eventually provider. Rate limits or exhausted credits preserve the task as pending and do not count as technical failures.

Restarting the runner resumes from `manifest.json`. A stopped process cannot restart itself; launch the same command again or use an external service or CI scheduler.

## Safety model

- write-heavy tasks run sequentially unless isolated in separate worktrees;
- workers do not receive the full plan, study files, or future task definitions;
- deterministic validation runs outside the worker;
- a material unknown triggers renewed study and replanning instead of blind escalation;
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

The suite covers the installer and CLI, request intake, adaptive study validation and plan attachment, traceability, recursive planning gates, state transitions, escalation, strict-runner simulation, summarization, and guarded cleanup.

## Documentation

- [Portuguese README](README.pt-BR.md)
- [Request intake](skill/plan-and-execute/references/INTAKE.md)
- [Adaptive study gate](skill/plan-and-execute/references/ADAPTIVE_STUDY.md)
- [Study-spec example](skill/plan-and-execute/references/study-spec.example.json)
- [Deep planning protocol](skill/plan-and-execute/references/PLANNING_PROTOCOL.md)
- [Execution workflow](skill/plan-and-execute/references/WORKFLOW.md)
- [Plan specification](skill/plan-and-execute/references/PLAN_SPEC.md)
- [Model routing](skill/plan-and-execute/references/MODEL_ROUTING.md)
- [Installation](skill/plan-and-execute/references/INSTALLATION.md)
- [Publishing](docs/PUBLISHING.md)

## License

MIT.
