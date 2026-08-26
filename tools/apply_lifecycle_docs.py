#!/usr/bin/env python3
"""One-time documentation transformation for the resumable lifecycle release."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def write(relative: str, content: str) -> None:
    (ROOT / relative).write_text(content, encoding="utf-8")


def append_once(relative: str, marker: str, content: str) -> None:
    text = read(relative)
    if marker not in text:
        if not text.endswith("\n"):
            text += "\n"
        write(relative, text + content)


# Skill control plane.
skill_path = ROOT / "skill/plan-and-execute/SKILL.md"
skill = skill_path.read_text(encoding="utf-8")
lines = skill.splitlines()
new_description = (
    "description: Deeply study a large software request and its repository, pass an adaptive evidence gate, "
    "create a requirements-traceable plan, and execute isolated TODOs with deterministic validation, automatic "
    "resume after interruption, active-plan discovery, guarded cancellation, Claude Code/Codex routing, and safe "
    "cleanup. Use for long implementations, migrations, refactors, multi-workstream or test-heavy changes, for "
    "resuming an unfinished implementation, for cancelling/resetting plan state, without arguments to resume-or-create "
    "a guided request, or with a requirements file path."
)
for index, line in enumerate(lines):
    if line.startswith("description:"):
        lines[index] = new_description
        break
skill = "\n".join(lines) + "\n"
intro = (
    "Resolve the complete request, study internal and conditionally external evidence, prove that the evidence is "
    "sufficient before drafting requirements or TODOs, build and review a traceable plan, then execute one isolated "
    "verifiable TODO at a time.\n\n"
)
route_section = '''Resolve the complete request, study internal and conditionally external evidence, prove that the evidence is sufficient before drafting requirements or TODOs, build and review a traceable plan, then execute one isolated verifiable TODO at a time. Treat persisted lifecycle state as authoritative so an interrupted implementation can resume without prior chat context.

## Route lifecycle commands before request interpretation

When the complete invocation argument is exactly one of these commands, handle it before file-path or inline-request rules:

- `current` or `status`: run `lifecyclectl.py current --repo-root . --json` and report the active implementation.
- `resume` or `continue`: discover, recover, validate, and continue the active implementation. Prefer native fresh workers when nested provider sessions are prohibited; otherwise `pae resume` or `lifecyclectl.py resume` provides strict process isolation.
- `cancel`: run `lifecyclectl.py cancel --repo-root . --json`. This deletes the active plan, task definitions, logs, results, intake draft, and lifecycle status while preserving repository implementation changes.
- `reset`: run `lifecyclectl.py reset --repo-root . --json` to remove every recognized plan-and-execute artifact in this workspace while preserving repository implementation changes.

Do not reinterpret these exact commands as software requirements. Read [references/LIFECYCLE.md](references/LIFECYCLE.md) before resume, cancellation, or reset operations.

'''
if "## Route lifecycle commands before request interpretation" not in skill:
    if intro not in skill:
        raise SystemExit("SKILL intro anchor not found")
    skill = skill.replace(intro, route_section, 1)
old_no_args = '''### 1. No arguments: create an editable request draft

When invoked with no request text or file path:

1. Run from the repository root:
'''
new_no_args = '''### 1. No arguments: resume an implementation or create a request

When invoked with no request text or file path, inspect lifecycle state before creating anything:

```bash
python <skill-dir>/scripts/lifecyclectl.py current --repo-root . --json
```

- When the result has `action: resume`, reload the plan and manifest from the returned path, recover stale `in_progress` tasks, rerun the study and plan gates, and continue from the next runnable TODO. Do not create another request.
- When the result has `action: already_running`, report the live runner and do not start a duplicate worker.
- When discovery reports multiple unfinished plans, stop and identify the ambiguity; never choose silently.
- Only when the result has `action: create_request`, use the guided intake steps below.

For native resume, run `lifecyclectl.py recover --plan <active-plan> --json` before loading the next TODO. For strict process-isolated resume, run `pae resume` or:

```bash
python <skill-dir>/scripts/lifecyclectl.py resume --repo-root .
```

When no implementation is active, create the request draft from the repository root:

1. Run:
'''
if old_no_args in skill:
    skill = skill.replace(old_no_args, new_no_args, 1)
elif "### 1. No arguments: resume an implementation or create a request" not in skill:
    raise SystemExit("SKILL no-argument anchor not found")
old_gates = '''python <skill-dir>/scripts/studyctl.py validate-plan --plan .ai-work/<plan-id>
python <skill-dir>/scripts/planctl.py validate --plan .ai-work/<plan-id>
python <skill-dir>/scripts/planctl.py audit --plan .ai-work/<plan-id>
```

16. Start execution immediately after all gates pass unless a genuine safety gate requires approval.
'''
new_gates = '''python <skill-dir>/scripts/studyctl.py validate-plan --plan .ai-work/<plan-id>
python <skill-dir>/scripts/planctl.py validate --plan .ai-work/<plan-id>
python <skill-dir>/scripts/planctl.py audit --plan .ai-work/<plan-id>
```

16. Register the validated plan as the active implementation:

```bash
python <skill-dir>/scripts/lifecyclectl.py activate \
  --plan .ai-work/<plan-id> --json
```

17. Start execution immediately after all gates pass unless a genuine safety gate requires approval.
'''
if old_gates in skill:
    skill = skill.replace(old_gates, new_gates, 1)
contract = "- Treat `manifest.json` as the source of truth and update task state only through `planctl.py`.\n"
if ".active-plan.json" not in skill:
    skill = skill.replace(
        contract,
        contract
        + "- Treat `.ai-work/.active-plan.json` only as a discoverable pointer; `manifest.json` remains authoritative.\n"
        + "- Persist every transition before dispatching another worker so a new invocation can resume without chat history.\n"
        + "- Recover an orphaned `in_progress` task to `pending` without incrementing technical failures; preserve partial source changes for the next worker and deterministic validation.\n"
        + "- Never start a native worker while a live external runner lease exists.\n",
        1,
    )
strict_old = '''Use `scripts/run_isolated.py` from an external terminal when fresh processes, automatic rate-limit waiting, or exact CLI routing are required:

```bash
python <skill-dir>/scripts/run_isolated.py --plan .ai-work/<plan-id>
```
'''
strict_new = '''Use the lifecycle-aware wrapper from an external terminal when fresh processes, automatic interruption recovery, an atomic runner lease, automatic rate-limit waiting, or exact CLI routing are required:

```bash
pae resume
# or
python <skill-dir>/scripts/lifecyclectl.py resume --repo-root .
```

The wrapper discovers the active plan, replaces only a stale lease, returns orphaned `in_progress` tasks to `pending` without counting a technical failure, and then delegates to `run_isolated.py`.
'''
if strict_old in skill:
    skill = skill.replace(strict_old, strict_new, 1)
native_old = "1. Keep study, planning, review, and state management in the orchestrator thread.\n"
if native_old in skill:
    skill = skill.replace(
        native_old,
        "1. Rediscover the active plan and reload `manifest.json` from disk on every invocation; do not rely on prior chat context for execution state.\n"
        "2. Keep study, planning, review, and state management in the orchestrator thread.\n",
        1,
    )
    section_start = skill.index("### Native subagent mode")
    section_end = skill.index("### Strict external-runner mode", section_start)
    section = skill[section_start:section_end]
    for old, new in (
        ("6. Re-run", "7. Re-run"),
        ("5. Receive", "6. Receive"),
        ("4. Route", "5. Route"),
        ("3. Pass", "4. Pass"),
        ("2. Dispatch", "3. Dispatch"),
    ):
        section = section.replace(old, new, 1)
    skill = skill[:section_start] + section + skill[section_end:]
finish_old = '''5. Return the summary before cleanup.
6. Run guarded cleanup:

```bash
python <skill-dir>/scripts/planctl.py cleanup --plan .ai-work/<plan-id>
```
'''
finish_new = '''5. Return the summary before cleanup.
6. Clear active lifecycle state as soon as the final summary is durably marked generated:

```bash
python <skill-dir>/scripts/lifecyclectl.py deactivate \
  --plan .ai-work/<plan-id> --json
```

7. Run guarded cleanup:

```bash
python <skill-dir>/scripts/planctl.py cleanup --plan .ai-work/<plan-id>
```

If cleanup is interrupted after summary generation, the next default invocation must clear the terminal pointer and allow a new request. A retained completed plan is history, not active work.
'''
if finish_old in skill:
    skill = skill.replace(finish_old, finish_new, 1)
ref = "- Request-file and editor workflow: [references/INTAKE.md](references/INTAKE.md)\n"
if "Resumable lifecycle, default resume" not in skill:
    skill = skill.replace(
        ref,
        ref + "- Resumable lifecycle, default resume, leases, cancellation, and reset: [references/LIFECYCLE.md](references/LIFECYCLE.md)\n",
        1,
    )
skill_path.write_text(skill, encoding="utf-8")

# UI metadata.
write("skill/plan-and-execute/agents/openai.yaml", '''interface:
  display_name: "Plan and Execute"
  short_description: "Study, plan, resume, cancel, and execute large coding changes"
  default_prompt: "Use $plan-and-execute. Route exact lifecycle commands current/status, resume/continue, cancel, and reset before request parsing. With no arguments, inspect .ai-work lifecycle state first: resume the unique unfinished plan from disk when present, refuse duplicate execution when a live runner lease exists, and create the guided request file only when the workspace is idle. Before planning, run the adaptive study gate with mandatory internal repository evidence and conditional authoritative external research. Build a traceable reviewed plan, activate it, then execute each TODO in a fresh isolated worker with deterministic validation and persisted state. Recover orphaned in-progress tasks after interruption without counting a technical failure, keep partial source changes for revalidation, clear active status after final summary generation, and make cancel/reset remove only recognized planning and lifecycle artifacts while preserving implementation changes."
''')

# English README.
readme_path = ROOT / "README.md"
readme = readme_path.read_text(encoding="utf-8")
readme = readme.replace(
    "Plan and Execute helps Claude Code and Codex handle migrations, refactors, multi-workstream features, and other changes that are too large for a single chat context.",
    "Plan and Execute helps Claude Code and Codex handle migrations, refactors, multi-workstream features, and other changes that are too large for a single chat context or process.",
    1,
)
benefit = "- safe resume after interruptions or provider limits;\n"
if "state-aware default invocation" not in readme:
    readme = readme.replace(
        benefit,
        benefit
        + "- state-aware default invocation that resumes unfinished work before creating a new request;\n"
        + "- guarded cancel/reset commands that remove plan state without deleting implementation changes;\n",
        1,
    )
readme = readme.replace(
    "With no arguments, the skill creates a guided Markdown request file and opens it in your editor. When running from VS Code, it reuses the active VS Code window when the `code` CLI is available.\n\nWrite the complete request, save the file, then choose:\n",
    "With no arguments, the skill first inspects `.ai-work` for an unfinished implementation. It resumes the unique active plan from disk when one exists, reports a live runner instead of starting a duplicate, and creates a guided Markdown request only when the workspace is idle. When a request is needed, it opens the file in your editor and reuses the active VS Code window when the `code` CLI is available.\n\nWrite the complete request, save the file, then choose:\n",
    1,
)
anchor = "During implementation, each worker sees one task definition rather than the whole chat or future tasks. The orchestrator reruns the required validation commands before marking that task complete.\n\n"
section = '''During implementation, each worker sees one task definition rather than the whole chat or future tasks. The orchestrator reruns the required validation commands before marking that task complete.

## Resume, status, cancel, and reset

The skill and CLI share one lifecycle state. Multiple skills are intentionally not used: intake, evidence, planning, execution, resume, and cancellation all depend on the same manifest and safety checks. `pae` is only a convenient provider-neutral front end.

```bash
# Show the active implementation and task counts
pae current

# Continue the unique unfinished plan until completion
pae resume

# Run only the next TODO or select a provider
pae resume --once
pae resume --provider codex

# Cancel the active implementation and delete all of its planning state
pae cancel

# Remove every recognized plan-and-execute plan in this workspace
pae reset
```

A controlled interruption and an abrupt power/network/process loss are both resumable. The strict runner stores progress after every transition. If a crash leaves a TODO as `in_progress`, the next resume returns it to `pending` without adding a technical failure, preserves partial source changes, and gives the current task to a fresh worker for deterministic validation.

`pae cancel` removes the active plan, request draft, study, task definitions, logs, results, manifest, runner lease, and active pointer. It **does not revert or delete implementation files**. Use version control explicitly when source changes themselves must be rolled back. `pae cancel --all` and `pae reset` perform a full plan-and-execute state reset while still preserving repository changes.

The state-aware skill commands are equivalent:

```text
/plan-and-execute current
/plan-and-execute resume
/plan-and-execute cancel
/plan-and-execute reset
```

'''
if "## Resume, status, cancel, and reset" not in readme:
    readme = readme.replace(anchor, section, 1)
if ".ai-work/.active-plan.json" not in readme:
    readme = readme.replace(
        "```text\n.ai-work/<plan-id>/\n",
        "```text\n.ai-work/.active-plan.json      # pointer to the unique unfinished implementation\n.ai-work/<plan-id>/\n",
        1,
    )
doc_anchor = "- [Request intake](skill/plan-and-execute/references/INTAKE.md)\n"
if "[Resumable lifecycle and cancellation]" not in readme:
    readme = readme.replace(
        doc_anchor,
        doc_anchor + "- [Resumable lifecycle and cancellation](skill/plan-and-execute/references/LIFECYCLE.md)\n",
        1,
    )
readme = readme.replace(
    "The checks cover the Node installer and CLI, request-file/editor intake, request copy/move semantics, traceability, recursive-planning gates, state transitions, model escalation, strict-runner simulation, validation, summarization, and guarded cleanup.",
    "The checks cover the Node installer and CLI, request intake, traceability, adaptive study, active-plan discovery, abrupt-interruption recovery, atomic runner leases, cancellation/reset safety, model escalation, strict-runner simulation, validation, summarization, and guarded cleanup.",
    1,
)
readme_path.write_text(readme, encoding="utf-8")

# Portuguese README.
pt_path = ROOT / "README.pt-BR.md"
pt = pt_path.read_text(encoding="utf-8")
benefit_pt = "- retomada segura após interrupções ou limites do provedor;\n"
if "invocação padrão consciente" not in pt:
    pt = pt.replace(
        benefit_pt,
        benefit_pt
        + "- invocação padrão consciente do estado, que retoma trabalho incompleto antes de criar outro pedido;\n"
        + "- comandos protegidos de cancelamento e reset que removem o plano sem apagar a implementação;\n",
        1,
    )
pt = pt.replace(
    "Sem parâmetros, a skill cria um arquivo Markdown guiado e o abre no editor. Ao rodar no VS Code, ela reutiliza a janela ativa quando o comando `code` está disponível.\n\nEscreva o pedido completo, salve o arquivo e escolha:\n",
    "Sem parâmetros, a skill primeiro verifica `.ai-work` à procura de uma implementação não concluída. Ela retoma do disco o único plano ativo, informa quando já existe um runner vivo sem iniciar outro e só cria o arquivo Markdown guiado quando o workspace está ocioso. Quando um pedido novo é necessário, ela abre o arquivo no editor e reutiliza a janela ativa do VS Code quando o comando `code` está disponível.\n\nEscreva o pedido completo, salve o arquivo e escolha:\n",
    1,
)
pt_anchor = "Durante a implementação, cada worker recebe apenas uma definição de tarefa, e não o chat inteiro nem tarefas futuras. O orquestrador executa novamente os comandos de validação antes de concluir o item.\n\n"
pt_section = '''Durante a implementação, cada worker recebe apenas uma definição de tarefa, e não o chat inteiro nem tarefas futuras. O orquestrador executa novamente os comandos de validação antes de concluir o item.

## Retomar, consultar, cancelar e zerar

A skill e a CLI compartilham um único estado de ciclo de vida. Não foram criadas várias skills: intake, estudo, planejamento, execução, retomada e cancelamento dependem do mesmo manifesto e das mesmas proteções. O `pae` é apenas uma interface curta e neutra entre Claude Code e Codex.

```bash
pae current
pae resume
pae resume --once
pae resume --provider codex
pae cancel
pae reset
```

Tanto uma interrupção controlada quanto uma queda abrupta de energia, internet ou processo são retomáveis. O runner estrito persiste cada transição. Se a queda deixar um TODO como `in_progress`, a próxima retomada o devolve para `pending` sem registrar falha técnica, preserva as alterações parciais no código e entrega a tarefa atual a um worker novo para validação determinística.

`pae cancel` remove o plano ativo, rascunho do pedido, estudo, definições dos TODOs, logs, resultados, manifesto, lease do runner e ponteiro ativo. Ele **não reverte nem apaga os arquivos implementados**. Use o controle de versão explicitamente quando também for necessário desfazer as alterações no código. `pae cancel --all` e `pae reset` zeram todo o estado reconhecido do plan-and-execute, ainda preservando o conteúdo do repositório.

Os comandos equivalentes pela skill são:

```text
/plan-and-execute current
/plan-and-execute resume
/plan-and-execute cancel
/plan-and-execute reset
```

'''
if "## Retomar, consultar, cancelar e zerar" not in pt:
    pt = pt.replace(pt_anchor, pt_section, 1)
pt_path.write_text(pt, encoding="utf-8")

# Changelog.
changelog_path = ROOT / "CHANGELOG.md"
changelog = changelog_path.read_text(encoding="utf-8")
entry = '''## 0.5.0 - 2026-08-26

- Makes the no-argument skill invocation state-aware: resume the unique unfinished implementation before creating a new request.
- Adds `.ai-work/.active-plan.json` discovery with stale-pointer repair and ambiguity protection.
- Adds atomic runner leases to prevent concurrent strict runners in the same plan.
- Recovers tasks left `in_progress` after power, network, or process interruption without counting a technical failure.
- Adds `lifecyclectl.py` for current, activate, recover, resume, deactivate, cancel, and reset operations.
- Adds `pae current`, `pae resume`, `pae cancel`, and `pae reset` for both Claude Code and Codex workspaces.
- Clears active lifecycle state after final summary generation, including completed plans retained with `--no-cleanup`.
- Makes cancel/reset remove recognized plan artifacts and status while preserving repository implementation changes.
- Adds lifecycle documentation and deterministic self-tests for pointer repair, interruption recovery, duplicate-runner prevention, completion, cancellation, and reset safety.

'''
if "## 0.5.0 - 2026-08-26" not in changelog:
    marker = "All notable changes to this project are documented here.\n\n"
    changelog = changelog.replace(marker, marker + entry, 1)
changelog_path.write_text(changelog, encoding="utf-8")

append_once("skill/plan-and-execute/references/WORKFLOW.md", "## Resumable lifecycle entry", '''
## Resumable lifecycle entry

Before beginning or resuming implementation, follow the lifecycle contract in [LIFECYCLE.md](LIFECYCLE.md).

```bash
python <skill-dir>/scripts/lifecyclectl.py current --repo-root . --json
```

- `action: create_request` means no unfinished implementation exists.
- `action: resume` means reload the returned plan from disk, recover orphaned task state, rerun quality gates, and continue from the next runnable TODO.
- `action: already_running` means an external runner owns a live lease; do not dispatch another worker.

For strict process-isolated continuation use `pae resume`. Before native resume use `lifecyclectl.py recover --plan .ai-work/<plan-id>`. After final summary generation, deactivate the plan before guarded cleanup. `pae cancel` removes the active planning state without reverting implementation changes; `pae reset` removes every recognized plan-and-execute plan in the workspace.
''')
append_once("skill/plan-and-execute/references/INSTALLATION.md", "## Lifecycle CLI after installation", '''
## Lifecycle CLI after installation

```bash
pae current
pae resume
pae cancel
pae reset
```

Use `--cwd /path/to/project` for another workspace. These commands use the same `.ai-work` state as the installed skill; no separate lifecycle skill is required.
''')
append_once("skill/plan-and-execute/references/INSTALLATION.pt-BR.md", "## CLI de ciclo de vida após a instalação", '''
## CLI de ciclo de vida após a instalação

```bash
pae current
pae resume
pae cancel
pae reset
```

Use `--cwd /caminho/do/projeto` para outro workspace. Os comandos usam o mesmo estado `.ai-work` da skill instalada; não é necessária uma skill separada para o ciclo de vida.
''')

print("Lifecycle documentation transformation applied.")
