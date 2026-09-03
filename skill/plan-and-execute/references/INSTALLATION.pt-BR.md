# Instalar o Plan and Execute no Claude Code e Codex

[English version](INSTALLATION.md)

A instalação padrão continua limitada ao Claude Code e ao Codex. Gemini CLI, Qwen Code, Kimi Code CLI e Trae Agent permanecem backends opcionais de execução; não são novos destinos de `--agent`.

## Modo de ativação

O instalador agora possui dois modos:

- `selective` — **padrão e recomendado**. A skill continua elegível para seleção automática, mas a description restritiva e o gate DIRECT/ORCHESTRATED deixam trabalho pequeno/médio coeso no contexto atual do agente.
- `explicit` — desliga a invocação automática pelo modelo. Use quando quiser que o harness seja carregado somente após invocar/nomear `plan-and-execute` explicitamente.

O modo `explicit` é aplicado de forma específica por host:

- Claude recebe `disable-model-invocation: true` no frontmatter do `SKILL.md` instalado.
- Codex recebe `policy.allow_implicit_invocation: false` no `agents/openai.yaml` instalado.

O pacote fonte permanece sempre `selective`. O marker gerenciado registra o hash da fonte e o hash da variante realmente instalada, preservando a proteção contra alterações locais. Uma instalação intacta pode alternar `explicit ↔ selective` sem `--force`.

## Instalação recomendada com npx

Claude e Codex no perfil do usuário, com roteamento seletivo:

```bash
npx --yes --package=github:heavydevs/plan-and-execute \
  plan-and-execute install --agent both --scope user
```

Somente por invocação explícita:

```bash
npx --yes --package=github:heavydevs/plan-and-execute \
  plan-and-execute install --agent both --scope user --activation explicit
```

Após a publicação no npm:

```bash
npx --yes @luizcgvrj/plan-and-execute \
  install --agent both --scope user
```

Opções principais:

```text
--agent claude|codex|both
--scope user|workspace
--activation selective|explicit
--selective
--explicit
--cwd <diretório-do-workspace>
--force
--dry-run
--json
```

Exemplos:

```bash
pae install both --global
pae install both --global --activation explicit
pae install both --global --selective
pae install claude --local
pae status both --global
pae uninstall both --global
```

O instalador atualiza uma cópia gerenciada intacta automaticamente. Se houver edição local, ele para antes de sobrescrever/remover. Use `--force` somente para descartar conscientemente essas alterações.

## Destinos

Workspace:

```text
<workspace>/.claude/skills/plan-and-execute/SKILL.md
<workspace>/.agents/skills/plan-and-execute/SKILL.md
```

Perfil do usuário:

```text
~/.claude/skills/plan-and-execute/SKILL.md
~/.agents/skills/plan-and-execute/SKILL.md
```

## Instalação manual

Copiar o diretório empacotado manualmente instala a configuração fonte `selective`:

```bash
mkdir -p .claude/skills .agents/skills
cp -R plan-and-execute .claude/skills/
cp -R plan-and-execute .agents/skills/
```

Prefira o instalador do pacote para `explicit`, pois ele aplica o metadata correto por host e registra o hash da variante.

## Comportamento de invocação

Uma demanda rotineira e coesa deve continuar fora do harness. Invocação explícita sempre seleciona a orquestração:

```text
$plan-and-execute Implemente esta migração entre módulos com checkpoints retomáveis.
```

Arquivo de requisitos:

```text
$plan-and-execute docs/requisitos-da-migracao.md
```

Sem argumentos, a skill primeiro procura uma implementação inacabada única para retomar; só cria um pedido guiado quando o workspace está ocioso.

## Promoção tardia

Se uma tarefa começar DIRECT e depois revelar workstreams independentes, pesquisa ampla, migração/compatibilidade ou risco real de interrupção, use `references/PROMOTION.md` e `scripts/promotectl.py` para gerar um handoff compacto. O plano promovido contém **somente o trabalho restante**. Trabalho já concluído/validado vira histórico, nunca TODO retroativo.

## Runner e retomada

Depois que existir um plano orquestrado/promovido:

```bash
pae resume
pae resume --provider codex --once
```

Ou diretamente:

```bash
python <skill-dir>/scripts/run_isolated.py --plan .ai-work/<plan-id>
```

Cada TODO preserva `provider`, `model_tier` e `reasoning_effort` lógicos, além de subtarefas/checkpoints e comandos de validação. Assim outra IA/provedor compatível pode retomar quando os créditos/quota acabarem, sem precisar do chat anterior. Limite de uso não é contado como falha técnica.

## Provedores opcionais

A ordem padrão continua `claude`, depois `codex`. Para optar por outro backend:

```bash
pae resume --provider gemini
pae resume --provider qwen
pae resume --provider kimi
pae resume --provider trae
```

Respeite sandbox, permissões e políticas organizacionais de cada CLI.

## Verificação

```bash
npm run check
```

Suítes focadas novas e existentes:

```bash
python <skill-dir>/scripts/routing_self_test.py
python <skill-dir>/scripts/promotion_self_test.py
python <skill-dir>/scripts/context_self_test.py
python <skill-dir>/scripts/lifecycle_self_test.py
python <skill-dir>/scripts/study_self_test.py
python <skill-dir>/scripts/task_memory_self_test.py
python <skill-dir>/scripts/provider_self_test.py
```

O corpus de roteamento inclui casos positivos, promoção tardia e near-miss negatives que mencionam implementação/refactor/vários arquivos, mas devem permanecer DIRECT.

## CLI de ciclo de vida

```bash
pae current
pae resume
pae cancel
pae reset
```

Use `--cwd /caminho/do/projeto` para outro workspace. O estado persistido continua em `.ai-work` e pode ser retomado por outro agente compatível.
