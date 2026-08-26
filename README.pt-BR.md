# Plan and Execute

**Transforme pedidos grandes de desenvolvimento em um plano baseado em evidências, revisado e rastreável, e execute cada TODO em um contexto novo e estritamente limitado.**

Plan and Execute é uma skill reutilizável com CLI para Claude Code e Codex. Ela foi criada para migrações, refatorações, funcionalidades com várias frentes, mudanças sensíveis à arquitetura e implementações com muitos testes que não devem depender de uma única conversa longa.

A solução oferece:

- captura guiada do pedido;
- estudo obrigatório do repositório e pesquisa externa adaptativa;
- rastreabilidade parte do pedido → requisito → TODO;
- decomposição recursiva e revisão independente do plano;
- contexto global ou restrito a grupos de TODOs, sempre mínimo;
- um worker novo por TODO;
- validação determinística fora do worker;
- retomada após falta de energia, queda de internet, terminal ou processo;
- comandos protegidos `current`, `resume`, `cancel` e `reset`;
- escalonamento de modelo/provedor baseado em evidência técnica;
- resumo final econômico e limpeza segura.

[English](README.md)

## Início rápido

### 1. Instale para Claude Code e Codex

No perfil do usuário:

```bash
npx --yes --package=github:heavydevs/plan-and-execute \
  plan-and-execute install --agent both --scope user
```

Somente no workspace atual:

```bash
npx --yes --package=github:heavydevs/plan-and-execute \
  plan-and-execute install --agent both --scope workspace
```

### 2. Inicie ou retome o trabalho

Claude Code:

```text
/plan-and-execute
```

Codex:

```text
$plan-and-execute
```

A invocação sem parâmetros primeiro inspeciona `.ai-work`:

- se existir uma única implementação incompleta, ela é retomada do disco;
- se um runner ativo já possuir o plano, a skill informa isso e não inicia uma execução duplicada;
- se houver vários planos incompletos, a skill para em vez de escolher silenciosamente;
- somente quando o workspace estiver livre ela cria e abre o arquivo guiado de request.

### 3. Outras formas de fornecer o pedido

Texto inline:

```text
$plan-and-execute Migre a autenticação para OAuth, preserve o login por senha durante o rollout, adicione testes e documente o rollback.
```

Arquivo de requisitos:

```text
$plan-and-execute docs/requisitos-migracao-oauth.md
```

Um arquivo fornecido pelo usuário é copiado para o plano e preservado em seu local original.

## Como o fluxo funciona

```text
pedido completo
      ↓
estudo interno/externo adaptativo
      ↓
partes do pedido e requisitos
      ↓
grafo recursivo de TODOs
      ↓
decisão de contexto mínimo de execução
      ↓
revisão nova + gates determinísticos
      ↓
um worker novo por TODO
      ↓
validação independente + estado persistido
      ↓
resumo final + limpeza segura do ciclo de vida
```

## Gate de estudo adaptativo

O estudo interno do repositório é sempre obrigatório. Antes de criar requisitos ou TODOs, o planejador inspeciona instruções, arquitetura, implementação, testes, schemas, interfaces, build, CI e histórico relevante.

A pesquisa externa é condicional. Ela se torna obrigatória quando, por exemplo:

- o usuário pede verificação explicitamente;
- o domínio não é suficientemente conhecido;
- o comportamento depende de uma versão exata ou atual;
- autenticação, autorização, criptografia, sandbox ou outro contrato de segurança é relevante;
- o repositório não define um contrato necessário;
- as evidências internas entram em conflito;
- é preciso escolher uma tecnologia ou provedor;
- uma suposição incorreta teria alto risco.

O estudo registra questões materiais, locais das evidências, achados, impacto no planejamento, decisão sobre os gatilhos externos, autoridade/versão/data das fontes, síntese, revisão independente de suficiência e critério de parada.

Antes de planejar:

```bash
python <skill-dir>/scripts/studyctl.py validate \
  --spec /tmp/study-spec.json
```

Depois de criar o plano:

```bash
python <skill-dir>/scripts/studyctl.py attach \
  --spec /tmp/study-spec.json \
  --plan .ai-work/<plan-id>

python <skill-dir>/scripts/studyctl.py validate-plan \
  --plan .ai-work/<plan-id>
```

O gate de anexação comprova que as descobertas se tornaram restrições, requisitos, riscos ou validações do plano, em vez de permanecerem como anotações de pesquisa sem uso.

Veja [Estudo adaptativo](skill/plan-and-execute/references/ADAPTIVE_STUDY.md).

## Contexto progressivo de execução

Cada TODO continua sendo executado por um worker novo. O schema v3 adiciona um mecanismo explícito e restrito para a pequena quantidade de informação que realmente precisa atravessar os limites entre tarefas.

A decisão acontece somente depois que o grafo de TODOs existe:

1. **Necessário para todos os TODOs:** pode ser criado `CONTEXT.md`.
2. **Necessário para pelo menos dois, mas não todos:** pode ser criado `contexts/<topico>.md`, referenciado apenas nas definições dessas tarefas.
3. **Necessário para um único TODO:** permanece na própria definição da tarefa.
4. **Sem impacto material:** é omitido.

A omissão é o padrão. Os arquivos não podem conter o pedido inteiro, o estudo, o plano, status dos TODOs, orientações genéricas ou informações apenas interessantes. Cada item é uma linha operacional fundamentada em referências de origem. Limites determinísticos rejeitam excesso de texto, duplicação, atribuição ampla demais, arquivos para uma única tarefa, adulteração e vazamento de contexto.

Uma definição de tarefa pode conter:

```markdown
## Assigned execution context

- `.ai-work/<plan-id>/CONTEXT.md`
- `.ai-work/<plan-id>/contexts/oauth-rollout.md`
```

O worker deve ler exatamente esses arquivos, nenhum outro, e informar:

```json
{
  "context_files_read": [
    "CONTEXT.md",
    "contexts/oauth-rollout.md"
  ]
}
```

O orquestrador rejeita leituras ausentes ou extras antes de aceitar o resultado. Assim, restrições compartilhadas importantes são preservadas sem reenviar para cada worker o request, o plano inteiro, a conversa anterior ou informações irrelevantes.

Veja [Contexto progressivo de execução](skill/plan-and-execute/references/EXECUTION_CONTEXT.md).

## Planejamento rastreável

O planejador cria identificadores estáveis:

```text
parte do pedido P001
      ↓
requisito R001
      ↓
TODO 001
```

Toda parte do pedido deve ser coberta por um requisito. Todo requisito deve ser coberto por pelo menos um TODO executável. Cada TODO aponta de volta para os requisitos e contém:

- um objetivo;
- escopo incluído e excluído;
- arquivos esperados;
- dependências;
- complexidade e justificativa de atomicidade;
- critérios de aceite;
- comandos de validação determinísticos;
- provedor, nível de modelo e esforço de raciocínio;
- atribuições de contexto geradas.

Tarefas executáveis `extreme` são rejeitadas e precisam ser divididas. Uma tarefa `high` exige justificativa substantiva para não ser decomposta novamente.

## Workers novos e isolamento de contexto

O runner estrito inicia um processo novo e não persistente para cada TODO:

- Claude Code usa `--no-session-persistence`;
- Codex usa `exec --ephemeral`;
- o worker recebe uma definição de tarefa e somente os arquivos de contexto atribuídos;
- ele não pode ler o plano completo, tarefas futuras, análise, estudo, manifesto ou relatórios anteriores;
- as validações são executadas novamente pelo orquestrador;
- o estado é persistido antes de iniciar o próximo worker.

Isso torna o orquestrador operacionalmente sem estado: outro terminal, conversa ou provedor pode reconstruir o progresso pelo workspace do plano, sem depender do histórico da conversa.

## Ciclo de vida retomável

O ponteiro ativo fica em:

```text
.ai-work/.active-plan.json
```

`manifest.json` continua sendo a fonte de verdade. Um runner estrito possui um lease atômico dentro do plano, impedindo dois escritores simultâneos.

Comandos úteis:

```bash
pae current
pae resume
pae resume --once
pae resume --provider codex
pae resume --no-wait
pae resume --no-cleanup
pae cancel
pae cancel --all
pae reset
```

Se uma interrupção deixar um TODO como `in_progress`, a retomada o devolve para `pending` sem contar falha técnica, preserva alterações parciais e envia a mesma tarefa limitada a um worker novo para correção e revalidação.

`cancel` e `reset` removem planos reconhecidos, arquivos de contexto, logs, resultados, intake, lease e estado do ciclo de vida. As alterações de implementação no repositório são preservadas deliberadamente; use Git de forma explícita quando também precisar desfazer código.

Veja [Ciclo de vida retomável](skill/plan-and-execute/references/LIFECYCLE.md).

## TODO sucinto, contratos detalhados

`TODO.md` é apenas um índice de status:

```markdown
# TODO — Migração OAuth

- [x] **001** — Adicionar modelo de persistência OAuth
- [ ] **002** — Implementar callback de autorização _(in progress)_
- [ ] **003** — Preservar compatibilidade com login por senha
- [ ] **004** — Adicionar testes de migração e rollback
```

Provedor, modelo, esforço, requisitos, dependências, atribuições de contexto, critérios de aceite e comandos de validação ficam nas definições das tarefas e em `manifest.json`.

## Workspace do plano

```text
.ai-work/
├── .active-plan.json              # ponteiro ativo do ciclo de vida
└── <plan-id>/
    ├── .orchestrator-plan         # sentinel protegido
    ├── REQUEST.md                 # quando o pedido veio de arquivo
    ├── study.json
    ├── STUDY.md
    ├── ANALYSIS.md
    ├── PLAN.md
    ├── PLAN_REVIEW.md
    ├── TODO.md
    ├── CONTEXT.md                 # opcional, somente contexto universal
    ├── contexts/                  # opcional, subconjuntos estritos de TODOs
    ├── manifest.json              # fonte de verdade
    ├── orchestrator.config.json
    ├── tasks/
    ├── results/
    └── logs/
```

## Destinos de instalação

| Agente | Workspace | Perfil do usuário |
|---|---|---|
| Claude Code | `.claude/skills/plan-and-execute` | `~/.claude/skills/plan-and-execute` |
| Codex | `.agents/skills/plan-and-execute` | `~/.agents/skills/plan-and-execute` |

CLI global:

```bash
npm install --global @luizcgvrj/plan-and-execute
pae install both --global
```

Comandos do instalador:

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

O instalador não possui dependências de runtime nem faz alteração implícita no `postinstall`. Um marcador e um hash do diretório protegem instalações gerenciadas que tenham sido modificadas localmente.

## Roteamento de modelos e recuperação

Os TODOs usam níveis lógicos:

```text
economy → standard → strong → max
```

Falhas técnicas aumentam primeiro o esforço, depois o nível do modelo e, por fim, o provedor quando fallback é permitido. Limites de uso, créditos esgotados e indisponibilidade temporária não contam como falhas técnicas.

Veja [Roteamento de modelos](skill/plan-and-execute/references/MODEL_ROUTING.md).

## Modelo de segurança

- workers nunca editam arquivos do plano ou de contexto;
- TODOs com escrita executam sequencialmente, salvo isolamento por worktrees;
- mudanças no código nunca são apagadas pela limpeza normal ou pelo cancelamento do ciclo de vida;
- arquivos de contexto são criados somente a partir do schema validado;
- um defeito de planejamento provoca replanejamento completo, não escalonamento cego;
- a limpeza exige sentinel, raiz do repositório, id do plano, estado concluído e resumo gerado correspondentes;
- ações externas destrutivas ou irreversíveis continuam sujeitas a gates explícitos de segurança.

## Desenvolvimento

Requisitos:

- Node.js 18.17 ou mais recente;
- Python 3.10 ou mais recente;
- Claude Code e/ou Codex para execução real dos workers.

Execute todas as verificações:

```bash
npm ci
npm run check
npm pack --dry-run --ignore-scripts
```

A suíte cobre instalador/CLI, estudo adaptativo, rastreabilidade, planejamento recursivo, minimalidade e atribuição de contexto, relatórios dos workers, recuperação após interrupção, leases, cancelamento/reset, escalonamento, resumo final e limpeza protegida.

## Documentação

- [Entrada do request](skill/plan-and-execute/references/INTAKE.md)
- [Estudo adaptativo](skill/plan-and-execute/references/ADAPTIVE_STUDY.md)
- [Planejamento profundo](skill/plan-and-execute/references/PLANNING_PROTOCOL.md)
- [Contexto progressivo de execução](skill/plan-and-execute/references/EXECUTION_CONTEXT.md)
- [Schema do plano](skill/plan-and-execute/references/PLAN_SPEC.md)
- [Fluxo de execução](skill/plan-and-execute/references/WORKFLOW.md)
- [Ciclo de vida retomável](skill/plan-and-execute/references/LIFECYCLE.md)
- [Roteamento de modelos](skill/plan-and-execute/references/MODEL_ROUTING.md)
- [Instalação](skill/plan-and-execute/references/INSTALLATION.pt-BR.md)

## Licença

MIT.
