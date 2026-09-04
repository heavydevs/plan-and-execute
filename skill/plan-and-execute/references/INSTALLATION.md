# Install Plan and Execute for Claude Code and Codex

[Versão em português](INSTALLATION.pt-BR.md)

The standard installation intentionally targets only Claude Code and Codex. Gemini CLI, Qwen Code, Kimi Code CLI, and Trae Agent remain optional execution backends after they are installed, authenticated, and added to plan routing; they are not `--agent` installation destinations.

## Activation mode

The installer now has two activation modes:

- `selective` — **default and recommended**. The skill remains available for automatic selection, but its narrow description and DIRECT/ORCHESTRATED gate keep routine cohesive work in the current agent context.
- `explicit` — disables automatic model invocation. Use this when you want the harness only after explicitly naming/invoking `plan-and-execute`.

`explicit` is applied per host without maintaining separate bundled skills:

- Claude installed copies receive `disable-model-invocation: true` in `SKILL.md` frontmatter.
- Codex installed copies receive `policy.allow_implicit_invocation: false` in `agents/openai.yaml`.

The package source always remains `selective`. The installer records both the source hash and the transformed installed hash so local-edit protection still works for either mode. An untouched managed installation can switch modes without `--force`.

## Recommended: install with npx

Install for both agents in your user profile with selective activation:

```bash
npx --yes --package=github:heavydevs/plan-and-execute \
  plan-and-execute install --agent both --scope user
```

Install explicit-only instead:

```bash
npx --yes --package=github:heavydevs/plan-and-execute \
  plan-and-execute install --agent both --scope user --activation explicit
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
--activation selective|explicit
--selective
--explicit
--cwd <workspace-directory>
--force
--dry-run
--json
```

Examples:

```bash
# Claude and Codex for every project; selective auto-routing
pae install both --global

# Never auto-invoke the harness
pae install both --global --activation explicit

# Return an untouched managed installation to selective mode
pae install both --global --selective

# Claude only in the current workspace
pae install claude --local

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

## Manual installation

Copying the bundled directory manually gives you the source `selective` configuration:

```bash
mkdir -p .claude/skills .agents/skills
cp -R plan-and-execute .claude/skills/
cp -R plan-and-execute .agents/skills/
```

Prefer the package installer when you want `explicit` mode because it applies the host-specific metadata safely and records the installed variant hash.

## Invocation behavior

A routine cohesive request should normally remain outside the harness. Explicit invocation always selects orchestration:

```text
$plan-and-execute Implement the described cross-module migration with resumable checkpoints.
```

A requirements file can also be handed to the orchestrated workflow:

```text
$plan-and-execute docs/migration-request.md
```

No-argument invocation first checks lifecycle state, resuming a unique unfinished implementation before creating a guided request.

## Late promotion from direct work

If a task starts directly but later grows into independent workstreams, broad research, migration/compatibility work, or meaningful resume risk, use `references/PROMOTION.md` and `scripts/promotectl.py` to create a compact handoff. The promoted plan covers **remaining work only**; completed work is retained as validated history rather than rewritten as retroactive TODOs.

## Strict runner

After an orchestrated/promoted plan exists:

```bash
pae resume
```

or directly:

```bash
python <skill-dir>/scripts/run_concise.py --plan .ai-work/<plan-id>
```

Useful options:

```bash
pae resume --provider codex --once
pae resume --provider gemini --once
python <skill-dir>/scripts/run_concise.py --plan .ai-work/<plan-id> --dry-run
python <skill-dir>/scripts/run_concise.py --plan .ai-work/<plan-id> --no-cleanup
```

## Model mapping and provider fallback

Every orchestrated TODO keeps logical `provider`, `model_tier`, and `reasoning_effort` requirements. Concrete model ids live in `.ai-work/<plan-id>/orchestrator.config.json`, allowing another compatible provider/model to resume when quota, availability, or account capabilities change.

The default provider order remains `claude`, then `codex`. Optional execution backends can be selected with `pae resume --provider <name>` or configured in the plan. Usage/quota exhaustion does not count as a technical implementation failure.

## Verify the installation

```bash
npm run check
```

Focused skill suites include:

```bash
python <skill-dir>/scripts/routing_self_test.py
python <skill-dir>/scripts/promotion_self_test.py
python <skill-dir>/scripts/context_self_test.py
python <skill-dir>/scripts/lifecycle_self_test.py
python <skill-dir>/scripts/study_self_test.py
python <skill-dir>/scripts/task_memory_self_test.py
python <skill-dir>/scripts/provider_self_test.py
```

The routing corpus contains positive orchestration cases, late-promotion cases, and near-miss negatives that mention implementation/refactors/multiple files but should remain DIRECT.

## Lifecycle CLI

```bash
pae current
pae resume
pae cancel
pae reset
```

Use `--cwd /path/to/project` for another workspace. Lifecycle state remains in `.ai-work`; another compatible AI/provider can resume without the old chat transcript.
