# Plan and Execute

**Transforme pedidos grandes de desenvolvimento em um plano revisado e rastreável — e execute cada tarefa em um contexto novo e focado.**

Plan and Execute ajuda Claude Code e Codex a lidar com migrações, refatorações, funcionalidades com várias frentes e outras mudanças grandes demais para um único contexto de chat. A skill estuda primeiro o pedido completo e o repositório, comprova que todos os requisitos estão cobertos, divide trabalho grande recursivamente, valida cada tarefa de forma independente e mantém a execução retomável em disco.

O que você ganha:

- menos requisitos perdidos entre planejamento e implementação;
- workers com contexto pequeno e apenas uma definição de tarefa;
- validação determinística em vez de confiar apenas no relato do agente;
- escalonamento de modelo e esforço somente quando houver evidência técnica;
- retomada segura após interrupções ou limites do provedor;
- checklist compacto, sem perder os contratos detalhados das tarefas;
- uma instalação para Claude Code, Codex ou ambos.

[English](README.md)

## Guia rápido

### 1. Instale para Claude Code e Codex

No perfil do usuário:

```bash
npx --yes --package=github:heavydevs/plan-and-execute \
  plan-and-execute install --agent both --scope user
```

Ou somente no workspace atual:

```bash
npx --yes --package=github:heavydevs/plan-and-execute \
  plan-and-execute install --agent both --scope workspace
```

### 2. Inicie um pedido grande

Claude Code:

```text
/plan-and-execute
```

Codex:

```text
$plan-and-execute
```

Sem parâmetros, a skill cria um arquivo Markdown guiado e o abre no editor. Ao rodar no VS Code, ela reutiliza a janela ativa quando o comando `code` está disponível.

Escreva o pedido completo, salve o arquivo e escolha:

```text
Continuar — terminei de escrever as instruções
```

A skill move o rascunho para a área de execução como `REQUEST.md`, estuda o conteúdo e o repositório, cria e revisa o plano de desenvolvimento, passa pelos quality gates e inicia a execução.

### 3. Ou passe o pedido diretamente

Texto inline:

```text
$plan-and-execute Migre a autenticação para OAuth, preserve o login por senha durante o rollout, adicione testes e documente o rollback.
```

Arquivo de requisitos:

```text
$plan-and-execute docs/requisitos-migracao-oauth.md
```

Um arquivo fornecido pelo usuário é copiado para o plano e preservado em seu local original.

## Como funciona

```text
pedido completo
      ↓
partes do pedido (P001, P002, ...)
      ↓
requisitos (R001, R002, ...)
      ↓
TODOs executáveis e revisados
      ↓
um worker novo por TODO
      ↓
validação independente
      ↓
resumo econômico + limpeza segura
```

Antes de implementar, o orquestrador:

1. lê o pedido inteiro;
2. inspeciona código, testes, arquitetura, schemas, build e CI relevantes;
3. pesquisa fontes autoritativas quando fatos atuais ou sensíveis à versão importam;
4. inventaria todas as partes do pedido e requisitos;
5. divide recursivamente cada workstream até cada tarefa ter um único resultado coerente;
6. rejeita tarefas executáveis classificadas como `extreme`;
7. usa um revisor em contexto novo para desafiar cobertura, dependências, atomicidade e validação;
8. executa os gates determinísticos `validate` e `audit`;
9. inicia a execução somente após a aprovação do plano.

Durante a implementação, cada worker recebe apenas uma definição de tarefa, e não o chat inteiro nem tarefas futuras. O orquestrador executa novamente os comandos de validação antes de concluir o item.

## Formas de fornecer o pedido

### Fluxo guiado no editor

Invoque a skill sem parâmetros. Ela cria:

```text
.ai-work/intake/request-YYYYMMDD-HHMMSS.md
```

O topo contém instruções curtas. O restante possui seções para objetivo, requisitos, restrições, contexto, testes e definição de pronto.

Depois da sua confirmação, o arquivo vira:

```text
.ai-work/<plan-id>/REQUEST.md
```

O rascunho temporário só é removido depois de ser preservado e validado com segurança no plano.

### Arquivo existente

Passe um único caminho de arquivo regular como argumento completo da skill. Ela valida e lê o arquivo inteiro, copiando-o para `REQUEST.md`. Diretórios, arquivos ausentes e links simbólicos são rejeitados.

### Texto inline

Qualquer outro argumento não vazio é tratado como o pedido completo em texto.

## Checklist sucinto, contratos detalhados

O `TODO.md` foi feito para leitura rápida:

```markdown
# TODO — Migração OAuth

- [x] **001** — Adicionar modelo de persistência OAuth
- [ ] **002** — Implementar callback de autorização _(in progress)_
- [ ] **003** — Preservar compatibilidade com login por senha
- [ ] **004** — Adicionar testes de migração e rollback
```

Há exatamente uma linha por item. Provedor, modelo, esforço, complexidade, requisitos, dependências, critérios de aceite e validações ficam nos arquivos de `tasks/` e no `manifest.json`.

## Opções de instalação

### Direto do GitHub

```bash
npx --yes --package=github:heavydevs/plan-and-execute \
  plan-and-execute install --agent both --scope user
```

### Pelo npm após a publicação

O nome atual do pacote continua sendo `@luizcgvrj/plan-and-execute`:

```bash
npx --yes @luizcgvrj/plan-and-execute \
  install --agent both --scope user
```

### CLI global

```bash
npm install --global @luizcgvrj/plan-and-execute
pae install both --global
```

`pae` é o alias curto.

### Destinos

| Agente | Workspace | Perfil do usuário |
| --- | --- | --- |
| Claude Code | `.claude/skills/plan-and-execute` | `~/.claude/skills/plan-and-execute` |
| Codex | `.agents/skills/plan-and-execute` | `~/.agents/skills/plan-and-execute` |

Veja o [guia de instalação em português](skill/plan-and-execute/references/INSTALLATION.pt-BR.md).

## Comandos do instalador

```bash
pae install both --local
pae install claude --global
pae install codex --cwd /caminho/do/projeto
pae paths both --global
pae status both --global
pae doctor
pae install both --local --dry-run
pae uninstall both --global
```

O instalador não possui dependências de runtime e não usa `postinstall` para modificar o computador. Um marcador local e um hash de conteúdo impedem a substituição ou remoção acidental de instalações editadas manualmente.

## Modos de execução

### Modo nativo

Use o chat ativo do Claude Code ou Codex. O orquestrador abre um subagente novo para cada tarefa executável e fornece apenas a definição correspondente.

### Runner externo estrito

Use um terminal fora da sessão aninhada quando precisar de um processo novo a cada tentativa, roteamento exato pela CLI ou espera automática por limites:

```bash
python .agents/skills/plan-and-execute/scripts/run_isolated.py \
  --plan .ai-work/<plan-id>
```

ou:

```bash
python .claude/skills/plan-and-execute/scripts/run_isolated.py \
  --plan .ai-work/<plan-id>
```

## Área do plano

```text
.ai-work/<plan-id>/
├── REQUEST.md
├── ANALYSIS.md
├── PLAN.md
├── PLAN_REVIEW.md
├── TODO.md
├── manifest.json
├── orchestrator.config.json
├── tasks/
├── results/
└── logs/
```

## Segurança e retomada

- tarefas com escrita são sequenciais, salvo isolamento por worktree;
- workers não recebem o plano completo nem tarefas futuras;
- validações determinísticas rodam fora do worker;
- defeitos de planejamento provocam replanejamento, não escalonamento cego;
- limpeza exige sentinel, tarefas concluídas e resumo gerado;
- somente o diretório exato do plano é apagado;
- implementação, testes, commits e outros planos são preservados;
- a execução pode ser retomada pelo `manifest.json`.

## Desenvolvimento

```bash
npm ci
npm run check
npm pack --dry-run
```

Requisitos: Node.js 18.17+, Python 3.10+ e Claude Code e/ou Codex para execuções reais.

## Documentação

- [Request intake](skill/plan-and-execute/references/INTAKE.md)
- [Protocolo de planejamento](skill/plan-and-execute/references/PLANNING_PROTOCOL.md)
- [Workflow de execução](skill/plan-and-execute/references/WORKFLOW.md)
- [Especificação do plano](skill/plan-and-execute/references/PLAN_SPEC.md)
- [Roteamento de modelos](skill/plan-and-execute/references/MODEL_ROUTING.md)
- [Instalação em português](skill/plan-and-execute/references/INSTALLATION.pt-BR.md)
- [Publicação em português](docs/PUBLISHING.pt-BR.md)

## Licença

MIT.
