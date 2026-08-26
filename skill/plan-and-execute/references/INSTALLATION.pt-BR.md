# Instalar o Plan and Execute no Claude Code e Codex

[English version](INSTALLATION.md)

## Instalação recomendada com npx

Para Claude e Codex no perfil do usuário:

```bash
npx --yes --package=github:heavydevs/plan-and-execute \
  plan-and-execute install --agent both --scope user
```

Somente no workspace atual:

```bash
npx --yes --package=github:heavydevs/plan-and-execute \
  plan-and-execute install --agent both --scope workspace
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
--cwd <diretório-do-workspace>
--force
--dry-run
--json
```

O instalador atualiza automaticamente uma cópia gerenciada e intacta. Caso os arquivos instalados tenham sido editados, ele interrompe antes de substituir ou apagar. Use `--force` somente quando quiser descartar essas alterações locais.

## Destinos

Escopo de workspace:

```text
<workspace>/.claude/skills/plan-and-execute/SKILL.md
<workspace>/.agents/skills/plan-and-execute/SKILL.md
```

Escopo do usuário:

```text
~/.claude/skills/plan-and-execute/SKILL.md
~/.agents/skills/plan-and-execute/SKILL.md
```

No Windows, `~` normalmente corresponde a `%USERPROFILE%`.

## Instalação manual no workspace

```bash
mkdir -p .claude/skills .agents/skills
cp -R plan-and-execute .claude/skills/
cp -R plan-and-execute .agents/skills/
```

## Instalação manual no perfil do usuário

```bash
mkdir -p ~/.claude/skills ~/.agents/skills
cp -R plan-and-execute ~/.claude/skills/
cp -R plan-and-execute ~/.agents/skills/
```

## Uso no VS Code

Sem parâmetros, com arquivo guiado:

```text
/plan-and-execute
```

ou:

```text
$plan-and-execute
```

A skill cria e abre o arquivo de solicitação. Salve-o e escolha a opção de continuar no chat.

Pedido inline:

```text
$plan-and-execute Implemente a migração descrita, com testes automatizados e documentação de rollback.
```

Arquivo de requisitos:

```text
$plan-and-execute docs/requisitos-da-migracao.md
```

## Runner estrito no terminal

```bash
python .claude/skills/plan-and-execute/scripts/run_isolated.py \
  --plan .ai-work/<plan-id>
```

ou:

```bash
python .agents/skills/plan-and-execute/scripts/run_isolated.py \
  --plan .ai-work/<plan-id>
```

Para simular:

```bash
python <skill-dir>/scripts/run_isolated.py --plan .ai-work/<plan-id> --dry-run
```

Para preservar o plano após o sucesso:

```bash
python <skill-dir>/scripts/run_isolated.py --plan .ai-work/<plan-id> --no-cleanup
```

## Verificar a instalação

```bash
python <skill-dir>/scripts/self_test.py
```

O teste cobre criação e validação do arquivo de solicitação, detecção do VS Code, cópia/movimentação do pedido, checklist sucinto, rastreabilidade, grafo de tarefas, escalonamento, execução isolada, validação determinística, resumo e limpeza segura.

## CLI de ciclo de vida após a instalação

```bash
pae current
pae resume
pae cancel
pae reset
```

Use `--cwd /caminho/do/projeto` para outro workspace. Os comandos usam o mesmo estado `.ai-work` da skill instalada; não é necessária uma skill separada para o ciclo de vida.
