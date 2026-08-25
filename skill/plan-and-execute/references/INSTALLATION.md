# Instalação no Claude Code e no Codex

## Instalação recomendada com npm ou npx

O repositório oficial da skill inclui um instalador sem dependências externas. Ele copia a pasta completa da skill para o destino correto e registra um marcador local para permitir atualização e remoção seguras.

Enquanto o pacote ainda não estiver publicado no npm, execute diretamente do GitHub:

```bash
npx --yes --package=github:luizcgvrj/plan-and-execute \
  plan-and-execute install --agent both --scope user
```

Depois da publicação no npm:

```bash
npx --yes @luizcgvrj/plan-and-execute install --agent both --scope user
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

Exemplos:

```bash
# Claude e Codex para todos os projetos do usuário
npx --yes @luizcgvrj/plan-and-execute install --agent both --scope user

# Somente Claude no workspace atual
npx --yes @luizcgvrj/plan-and-execute install --agent claude --scope workspace

# Somente Codex em outro workspace
npx --yes @luizcgvrj/plan-and-execute install --agent codex --scope workspace --cwd /caminho/do/projeto

# Verificar instalações
npx --yes @luizcgvrj/plan-and-execute status --agent both --scope user

# Atualizar uma cópia gerenciada pelo instalador
npx --yes @luizcgvrj/plan-and-execute install --agent both --scope user

# Remover
npx --yes @luizcgvrj/plan-and-execute uninstall --agent both --scope user
```

O instalador atualiza automaticamente uma instalação não modificada. Se os arquivos instalados tiverem sido editados manualmente, ele interrompe a operação para preservar as mudanças. Use `--force` somente quando quiser substituir ou remover essas alterações locais.

## Destinos utilizados

Escopo `workspace`:

```text
<workspace>/.claude/skills/plan-and-execute/SKILL.md
<workspace>/.agents/skills/plan-and-execute/SKILL.md
```

Escopo `user`:

```text
~/.claude/skills/plan-and-execute/SKILL.md
~/.agents/skills/plan-and-execute/SKILL.md
```

No Windows, `~` corresponde normalmente a `%USERPROFILE%`.

## Instalação manual por projeto

Depois de extrair o pacote da skill, copie a pasta completa `plan-and-execute`:

```bash
mkdir -p .claude/skills .agents/skills
cp -R plan-and-execute .claude/skills/
cp -R plan-and-execute .agents/skills/
```

## Instalação manual pessoal

```bash
mkdir -p ~/.claude/skills ~/.agents/skills
cp -R plan-and-execute ~/.claude/skills/
cp -R plan-and-execute ~/.agents/skills/
```

## Uma única cópia com links simbólicos

Em Linux ou macOS:

```bash
mkdir -p .shared-agent-skills .claude/skills .agents/skills
cp -R plan-and-execute .shared-agent-skills/

ln -sfn ../../.shared-agent-skills/plan-and-execute \
  .claude/skills/plan-and-execute

ln -sfn ../../.shared-agent-skills/plan-and-execute \
  .agents/skills/plan-and-execute
```

## Uso no VS Code

No Claude Code:

```text
/plan-and-execute Implemente esta mudança grande, incluindo testes automatizados: ...
```

No Codex:

```text
$plan-and-execute Implemente esta mudança grande, incluindo testes automatizados: ...
```

Pedido recomendado:

```text
Use plan-and-execute. Estude integralmente o pedido, o repositório e o assunto antes de planejar. Inventarie cada parte do pedido, crie requisitos rastreáveis, divida recursivamente cada workstream grande em TODOs executáveis com validação independente, revise o plano em contexto novo e só inicie depois que validate e audit passarem. Use subagentes novos, um por tarefa. Escalone modelo e esforço somente após falha técnica comprovada. Ao final, gere o resumo com modelo econômico e apague apenas os artefatos de planejamento.
```

## Executor estrito no terminal integrado

Para exigir um processo novo e sem sessão persistida a cada tentativa, primeiro deixe a skill criar o plano e depois execute:

```bash
python .claude/skills/plan-and-execute/scripts/run_isolated.py \
  --plan .ai-work/<plan-id>
```

ou:

```bash
python .agents/skills/plan-and-execute/scripts/run_isolated.py \
  --plan .ai-work/<plan-id>
```

Para inspecionar sem executar:

```bash
python <skill-dir>/scripts/run_isolated.py \
  --plan .ai-work/<plan-id> \
  --dry-run
```

Para preservar os arquivos de planejamento após o sucesso durante os primeiros testes:

```bash
python <skill-dir>/scripts/run_isolated.py \
  --plan .ai-work/<plan-id> \
  --no-cleanup
```

## Ajuste dos modelos

Cada plano gera `.ai-work/<plan-id>/orchestrator.config.json`. Edite o mapeamento lógico quando os modelos disponíveis na sua conta forem diferentes. As tarefas continuam usando os níveis `economy`, `standard`, `strong` e `max`, evitando acoplamento permanente aos nomes comerciais.

## Teste da instalação

```bash
python <skill-dir>/scripts/self_test.py
```

O teste cria repositórios temporários, verifica a rastreabilidade `Pxxx -> Rxxx -> TODO`, rejeita cobertura incompleta e tarefas extremas, valida o grafo e as transições de estado, simula um provedor, executa validações, gera um resumo e confirma que a limpeza preserva a implementação.
