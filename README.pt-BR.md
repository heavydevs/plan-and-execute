# Plan and Execute

**Transforme pedidos grandes de desenvolvimento em um plano baseado em evidências, revisado e rastreável, e execute cada tarefa em um contexto novo e focado.**

Plan and Execute ajuda Claude Code e Codex a lidar com migrações, refatorações, funcionalidades com várias frentes e outras mudanças grandes demais para um único contexto de chat. Antes de montar o plano, a skill estuda o pedido completo e evidências concretas do repositório, decide se pesquisa externa e realmente é necessária e bloqueia planos superficiais cujos achados não foram convertidos em restrições, requisitos, riscos e validações.

O que você ganha:

- estudo interno obrigatório do repositório antes do planejamento;
- pesquisa externa somente quando gatilhos explícitos justificarem;
- prova determinística de que os achados do estudo afetaram o plano;
- menos requisitos perdidos entre planejamento e implementação;
- workers com contexto pequeno e apenas uma definição de tarefa;
- validação determinística em vez de confiar somente no relato do agente;
- escalonamento de modelo e esforço apenas quando houver evidência técnica;
- retomada segura após interrupções ou limites do provedor;
- uma instalação para Claude Code, Codex ou ambos.

[English](README.md)

## Guia rápido

### 1. Instalê para Claude Code e Codex

No perfil do usuário:

```bash
npx --yes --package=github:heavydevs/plan-and-execute \
  plan-and-execute install --agent both --scope user
```

Ou apenas no workspace atual:

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

Sem parâmetros, a skill cria um arquivo Markdown guiado e o abre no editor. Quando o VS Code está ativo e o comando `code` está disponível, ela reutiliza a janela atual.

Escreva o pedido completo, salve e escolha:

```text
Continuar - terminei de escrever as instruções
```

A skill move o rascunho para a área de execução como `REQUEST.md`, passa pelo gaté de estudo adaptativo, cria e revisa o plano, executa os quality gatés determinísticos e inicia a implementação.

### 3. Ou forneça o pedido diretamente

Texto inline:

```text
$plan-and-execute Migre a autenticação para OAuth, preserve o login por senhá durante o rollout, adicione testes automatizados e documente o rollback.
```

Arquivo de requisitos:

```text
$plan-and-execute docs/requisitos-migração-oauth.md
```

Um arquivo fornecido pelo usuário é copiado para o plano e preservado no local original.

## Como funciona

```text
pedido completo
      |
      v
questões matériais
      |
      v
estudo interno obrigatório do repositório
      |
      v
avaliação explicita dos gatilhos de pesquisa externa
      |-----------------------------|
      v                             v
pesquisa autoritativa           pesquisa desnecessária
      |-----------------------------|
      v
síntese de evidências validada
      |
      v
partes do pedido -> requisitos -> TODOs revisados
      |
      v
um worker novo por TODO
      |
      v
validação independente
      |
      v
resumo econômico + limpeza segura
```

Antes de implementar, o orquestrador:

1. lê o pedido inteiro;
2. identifica questões que podem alterar arquitetura, compatibilidade, risco, divisão de tarefas ou validação;
3. inspeciona código, testes, instruções, arquitetura, schemas, build, CI e histórico relevante;
4. avalia explicitamente nove gatilhos de pesquisa externa;
5. pesquisa fontes primárias e autoritativas apenas quando algum gatilho estiver ativo;
6. valida a suficiência das evidências antes de criar requisitos ou TODOs;
7. inventaria todas as partes do pedido e requisitos;
8. divide cada workstream recursivamente até cada tarefa ter um único resultado coerente;
9. usa revisores novos para o estudo e o plano;
10. comprova que as evidências foram copiadas para restrições, requisitos, riscos e validações do plano;
11. executa `studyctl validaté-plan`, `planctl validaté` e `planctl audit` antes da implementação.

Durante a implementação, cada worker recebe apenas uma definição de tarefa. O orquestrador executa novamente os comandos de validação antes de concluir o item.

## Gaté de estudo adaptativo

O estudo interno é sempre obrigatório porque instruções, versoes, interfaces e testes específicos do repositório definem a superfície real da mudanca. A pesquisa externa é condicional, não automática.

A pesquisa externa torna-se obrigatória quando qualquer uma destás condições for verdadeira:

- o usuário pede pesquisa ou verificação explicitamente;
- o domínio não é suficientemente conhecido;
- o comportamento depende de uma versão exata ou pode ter mudado recentemente;
- há comportamento sensível a segurança;
- falta no repositório um contrato matérial para planejar;
- as evidências internas entram em conflito;
- é preciso escolher tecnologia ou provedor;
- uma suposição incorreta teria alto risco.

Quando todos os gatilhos forem falsos, o plano pode usar somente evidências internas, mas deve registrar uma justificativa substantiva. Quando um gatilho estiver ativo e não for possível obter evidência autoritativa, o planejamento fica bloqueado em vez de inventar uma resposta.

A especificação de estudo registra:

- questões matériais e suas resoluções;
- locais, achados e impactos de evidências internas;
- avaliação dos gatilhos e decisão de pesquisa externa;
- fontes externas autoritativas, versão/data e conclusões, quando necessárias;
- restrições, requisitos derivados, riscos e implicações de validação sintetizados;
- revisão independente de suficiência e critério de parada.

Valide antes de montar o plano:

```bash
python <skill-dir>/scripts/studyctl.py validaté \
  --spec /tmp/study-spec.json
```

Depois de criar o plano, anexe o estudo e verifique a integração exata:

```bash
python <skill-dir>/scripts/studyctl.py attach \
  --spec /tmp/study-spec.json \
  --plan .ai-work/<plan-id>

python <skill-dir>/scripts/studyctl.py validaté-plan \
  --plan .ai-work/<plan-id>
```

O gaté de anexação rejeita pesquisas que nunca foram usadas. Achados internos devem aparecer na análise do repositório; achados externos, na análise de pesquisa; restrições, requisitos e riscos sintetizados devem aparecer nos campos equivalentes do plano; implicações de validação devem aparecer nos critérios, orientações ou comandos das tarefas.

Veja o [protocolo de estudo adaptativo](skill/plan-and-execute/references/ADAPTIVE_STUDY.md) e o [exemplo de study spec](skill/plan-and-execute/references/study-spec.example.json).

## Formas de fornecer o pedido

### Fluxo guiado no editor

Invoque a skill sem parâmetros. Ela cria:

```text
.ai-work/intake/request-YYYYMMDD-HHMMSS.md
```

O arquivo possui seções para objetivos, requisitos, restrições, contexto, testes e definição de pronto. Depois da confirmação, elê vira:

```text
.ai-work/<plan-id>/REQUEST.md
```

O rascunho temporário só e removido depois de ser preservado e validado no plano.

### Arquivo existente

Passe um único caminho de arquivo regular como argumento completo. A skill valida e lê o arquivo inteiro, copia-o para `REQUEST.md` e preserva a origem. Diretorios, arquivos ausentes e links simbólicos sao rejeitados.

### Texto inline

Qualquer outro argumento não vazio é tratado como o pedido completo em texto.

## Checklist sucinto, contratos detalhados

O `TODO.md` continua fácil de examinar:

```markdown
# TODO - Migracao OAuth

- [x] **001** - Adicionar modelo de persistência OAuth
- [ ] **002** - Implementar callback de autorização _(in progress)_
- [ ] **003** - Preservar compatibilidade com login por senha
- [ ] **004** - Adicionar testes de migração e rollback
```

Provedor, modelo, esforço, complexidade, requisitos, dependencias, critérios de aceite e comandos de validação ficam nos arquivos de tarefa e no `manifest.json`.

## Opcoes de instalação

### Direto do GitHub

```bash
npx --yes --package=github:heavydevs/plan-and-execute \
  plan-and-execute install --agent both --scope user
```

### Pelo npm

O nome do pacote continua `@luizcgvrj/plan-and-execute`:

```bash
npx --yes @luizcgvrj/plan-and-execute \
  install --agent both --scope user
```

### CLI global

```bash
npm install --global @luizcgvrj/plan-and-execute
pae install both --global
```

`pae` é o alias curto de `plan-and-execute`.

### Destinos

| Agente | Workspace | Perfil do usuário |
| --- | --- | --- |
| Claude Code | `.claude/skills/plan-and-execute` | `~/.claude/skills/plan-and-execute` |
| Codex | `.agents/skills/plan-and-execute` | `~/.agents/skills/plan-and-execute` |

Veja o [guia de instalação](skill/plan-and-execute/references/INSTALLATION.pt-BR.md) para cópias manuais, links simbólicos, atualização, remoção e exemplos no Windows.

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

O instalador não possui dependencias de runtime nem mutação em `postinstall`. Elê grava somente depois de um comando `install` explicito. Um marcador local e um hash de conteúdo protegem instalações editadas manualmente contra sobrescrita ou remoção acidental.

## Modos de execução

### Modo nativo

Use o chat ativo do Claude Code ou Codex. O orquestrador cria um subagente novo para cada tarefa executavel e passa apenas a definição correspondente.

### Runner externo estrito

Use um terminal fora da sessão aninhada do provedor quando precisar de um processo novo por tentativa, roteamento exato de CLI ou espera automática por raté limit:

```bash
python <skill-dir>/scripts/run_isolatéd.py \
  --plan .ai-work/<plan-id>
```

Preserve o plano depois de uma execução de teste bem-sucedida:

```bash
python <skill-dir>/scripts/run_isolatéd.py \
  --plan .ai-work/<plan-id> \
  --no-cleanup
```

## Area de trabalho do plano

```text
.ai-work/<plan-id>/
|-- REQUEST.md                 # quando o pedido veio de arquivo
|-- study.json                 # evidência canônica do estudo adaptativo
|-- STUDY.md                   # estudo legível por humanos
|-- ANALYSIS.md
|-- PLAN.md
|-- PLAN_REVIEW.md
|-- TODO.md                    # uma linhá curta por tarefa
|-- manifest.json              # fonte da verdade e hash do estudo
|-- orchestrator.config.json
|-- tasks/                     # contratos detalhados e isolados
|-- results/
`-- logs/
```

Os validadores verificam hashes do pedido, evidências do estudo e sua integração ao plano, rastreabilidade, complexidade, revisoes, dependencias, arquivos de tarefa, critérios de aceite e comandos de validação.

## Roteamento de modelos e retomada

As tarefas usam níveis lógicos:

```text
economy -> standard -> strong -> max
```

O mapeamento concreto de provedor e modelo fica em `orchestrator.config.json`. Falhas funcionais podem aumentar esforço, nível de modelo e, por fim, provedor. Raté limits ou créditos esgotados mantêm a tarefa pendente e não contam como falhá técnica.

Reiniciar o runner retoma o estádo do `manifest.json`. Um processo parado não se reinicia sozinho; execute o mesmo comando novamente ou use um serviço externo ou agendador de CI.

## Modelo de segurança

- tarefas com escrita rodam em sequência, salvo isolamento em worktrees;
- workers não recebem o plano completo, arquivos de estudo ou tarefas futuras;
- validação determinística roda fora do worker;
- uma incerteza matérial dispara novo estudo e replanejamento em vez de escalonamento cego;
- a limpeza exige sentinel do plano, tarefas concluidas e resumo gerado;
- a limpeza remove somente o diretório exato `.ai-work/<plan-id>`;
- implementação, testes, commits e outros planos sao preservados.

## Desenvolvimento

Requisitos:

- Node.js 18.17 ou superior para o instalador;
- Python 3.10 ou superior para os scripts da skill;
- Claude Code e/ou Codex para execução real dos agentes.

Execute todos os checks:

```bash
npm ci
npm run check
npm pack --dry-run
```

A suite cobre instalador e CLI, captura do pedido, validação e anexação do estudo adaptativo, rastreabilidade, decomposicao recursiva, transições de estádo, escalonamento, simulação do runner estrito, resumo e limpeza protegida.

## Documentação

- [README em inglês](README.md)
- [Captura do pedido](skill/plan-and-execute/references/INTAKE.md)
- [Gaté de estudo adaptativo](skill/plan-and-execute/references/ADAPTIVE_STUDY.md)
- [Exemplo de study spec](skill/plan-and-execute/references/study-spec.example.json)
- [Protocolo de planejamento](skill/plan-and-execute/references/PLANNING_PROTOCOL.md)
- [Fluxo de execução](skill/plan-and-execute/references/WORKFLOW.md)
- [Especificacao do plano](skill/plan-and-execute/references/PLAN_SPEC.md)
- [Roteamento de modelos](skill/plan-and-execute/references/MODEL_ROUTING.md)
- [Instalacao](skill/plan-and-execute/references/INSTALLATION.pt-BR.md)
- [Publicação](docs/PUBLISHING.pt-BR.md)

## Licença

MIT.
