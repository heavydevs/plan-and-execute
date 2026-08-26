# Install Plan and Execute for Claude Code and Codex

[Versão em português](INSTALLATION.pt-BR.md)

## Recommended: install with npx

Install for both agents in your user profile:

```bash
npx --yes --package=github:heavydevs/plan-and-execute \
  plan-and-execute install --agent both --scope user
```

Install only in the current workspace:

```bash
npx --yes --package=github:heavydevs/plan-and-execute \
  plan-and-execute install --agent both --scope workspace
```

After the npm package is published:

```bash
npx --yes @luizcgvrj/plan-and-execute \
  install --agent both --scope user
```

Main options:

```text
--agent claude|codex|both
--scope user|workspace
--cwd <workspace-directory>
--force
--dry-run
--json
```

Examples:

```bash
# Claude and Codex for every project of the current user
npx --yes --package=github:heavydevs/plan-and-execute \
  plan-and-execute install --agent both --scope user

# Claude only in the current workspace
npx --yes --package=github:heavydevs/plan-and-execute \
  plan-and-execute install --agent claude --scope workspace

# Codex only in another workspace
npx --yes --package=github:heavydevs/plan-and-execute \
  plan-and-execute install --agent codex --scope workspace --cwd /path/to/project

# Inspect and remove installations
pae status both --global
pae uninstall both --global
```

The installer automatically updates an intact managed copy. If installed files were edited manually, it stops before overwriting or deleting them. Use `--force` only when those local changes should be replaced.

## Installation targets

Workspace scope:

```text
<workspace>/.claude/skills/plan-and-execute/SKILL.md
<workspace>/.agents/skills/plan-and-execute/SKILL.md
```

User scope:

```text
~/.claude/skills/plan-and-execute/SKILL.md
~/.agents/skills/plan-and-execute/SKILL.md
```

On Windows, `~` normally maps to `%USERPROFILE%`.

## Manual workspace installation

Copy the complete `plan-and-execute` directory:

```bash
mkdir -p .claude/skills .agents/skills
cp -R plan-and-execute .claude/skills/
cp -R plan-and-execute .agents/skills/
```

## Manual user installation

```bash
mkdir -p ~/.claude/skills ~/.agents/skills
cp -R plan-and-execute ~/.claude/skills/
cp -R plan-and-execute ~/.agents/skills/
```

## One shared copy with symbolic links

Linux or macOS:

```bash
mkdir -p .shared-agent-skills .claude/skills .agents/skills
cp -R plan-and-execute .shared-agent-skills/

ln -sfn ../../.shared-agent-skills/plan-and-execute \
  .claude/skills/plan-and-execute

ln -sfn ../../.shared-agent-skills/plan-and-execute \
  .agents/skills/plan-and-execute
```

The npm installer intentionally creates real copies rather than links into the temporary `npx` cache.

## Use in VS Code

No-argument guided request:

```text
/plan-and-execute
```

or:

```text
$plan-and-execute
```

The skill creates and opens a guided request file. Save it and select the continue action in the agent chat.

Inline request:

```text
$plan-and-execute Implement the described migration, including automated tests and rollback documentation.
```

Requirements file:

```text
$plan-and-execute docs/migration-request.md
```

## Strict runner in an integrated terminal

After the skill creates the plan:

```bash
python .claude/skills/plan-and-execute/scripts/run_isolated.py \
  --plan .ai-work/<plan-id>
```

or:

```bash
python .agents/skills/plan-and-execute/scripts/run_isolated.py \
  --plan .ai-work/<plan-id>
```

Dry run:

```bash
python <skill-dir>/scripts/run_isolated.py \
  --plan .ai-work/<plan-id> \
  --dry-run
```

Preserve planning files after success during early trials:

```bash
python <skill-dir>/scripts/run_isolated.py \
  --plan .ai-work/<plan-id> \
  --no-cleanup
```

## Model mapping

Every plan creates `.ai-work/<plan-id>/orchestrator.config.json`. Adjust the concrete model mapping when the models available to your account differ. Tasks keep using logical `economy`, `standard`, `strong`, and `max` tiers.

## Verify the installation

```bash
python <skill-dir>/scripts/self_test.py
```

The self-test covers request-file creation and validation, VS Code editor selection, request copy/move semantics, concise TODO rendering, traceability, task-graph rules, state transitions, model escalation, isolated execution, deterministic validation, final summarization, and safe cleanup.

## Lifecycle CLI after installation

```bash
pae current
pae resume
pae cancel
pae reset
```

Use `--cwd /path/to/project` for another workspace. These commands use the same `.ai-work` state as the installed skill; no separate lifecycle skill is required.
