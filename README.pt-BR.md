# Plan and Execute

**Transforme pedidos grandes de programação em planos de implementação estudados, isolados por contexto e retomáveis.**

O `plan-and-execute` estuda o pedido completo e o repositório antes de planejar, cria TODOs rastreáveis aos requisitos, entrega a cada TODO um contexto novo, persiste checkpoints, valida a implementação independentemente e encaminha apenas aprendizados verificados e úteis para TODOs futuros semelhantes.

[Read in English](README.md)

## IAs suportadas para execução

| IA / agente | Suporte de execução | Instalação padrão | Rota padrão | Observação |
|---|---:|---:|---:|---|
| Claude Code | Sim | Sim | Primeiro | Destino padrão do tutorial |
| OpenAI Codex | Sim | Sim | Segundo | Destino padrão do tutorial |
| Google Gemini CLI | Sim | Não | Opcional | Processo CLI headless novo |
| Qwen Code | Sim | Não | Opcional | Processo CLI headless novo |
| Kimi Code CLI | Sim | Não | Opcional | Processo novo em prompt mode |
| Trae Agent | Sim | Não | Opcional | Processo novo com `trae-cli run` |

O instalador npm instala a skill apenas no **Claude Code**, no **Codex** ou em **ambos**. Gemini, Qwen, Kimi e Trae são backends opcionais configurados dentro de um plano; não entram silenciosamente na ordem padrão.

## Tutorial rápido: Claude Code e Codex

Requisitos:

- Node.js 18.17 ou superior;
- Python 3.10 ou superior;
- Claude Code e/ou Codex instalados e autenticados.

Instale no workspace atual:

```bash
npx @luizcgvrj/plan-and-execute install both
```

Ou para apenas um agente:

```bash
npx @luizcgvrj/plan-and-execute install claude
npx @luizcgvrj/plan-and-execute install codex
```

Instalação global:

```bash
npx @luizcgvrj/plan-and-execute install both --global
```

Depois, invoque a skill com um pedido grande, um caminho de arquivo de requisitos ou sem argumentos. Sem argumentos, ela retoma primeiro a única implementação inacabada; só cria um rascunho guiado quando o workspace está ocioso.

## Artefatos derivados objetivos e precisos

O pedido original do usuário continua sendo evidência integral. A economia de tokens começa apenas quando a skill deriva estudo, requisitos, plano, definições de TODO, contexto, aprendizados, relatórios e handoff final.

O texto derivado segue um contrato determinístico:

- um trabalho semântico por campo;
- substantivos, condições e resultados observáveis;
- ids, caminhos, símbolos, comandos, versões e limites no lugar de explicações repetidas;
- orçamento explícito de caracteres e quantidade de itens por campo;
- rejeição de termos vagos de alta confiança, como `conforme apropriado`, `conforme necessário`, `quando necessário`, `e/ou`, `adequado`, `robusto`, `rapidamente` e equivalentes em inglês;
- nenhuma truncagem silenciosa de requisito: campo vago ou grande demais precisa ser reescrito com precisão ou dividido em itens atômicos.

O runtime usa `planctl_concise.py`, `studyctl_concise.py`, `lifecyclectl_concise.py` e `run_concise.py`. Esses entrypoints instalam o contrato conciso sobre os controllers determinísticos existentes, preservando lifecycle, resume, validação e cleanup.

Veja [Escrita precisa dos artefatos](skill/plan-and-execute/references/ARTIFACT_WRITING.md).

## Por que a fronteira dos TODOs importa

Um worker novo deve receber um problema semântico coerente, não um conjunto arbitrário de arquivos nem tudo o que apareceu no mesmo parágrafo.

Exemplo: um pedido contém um CRUD completo de pessoa e outro de loja. Quando os domínios não compartilham invariantes de negócio, transações, lifecycle ou uma fronteira real de validação, eles pertencem a **TODOs separados**. O histórico do worker de pessoa não ajuda materialmente o worker de loja.

A regra oposta também vale: não crie um TODO por arquivo. Entidade, serviço, controller, migração e testes focados podem permanecer juntos quando implementam um comportamento e se beneficiam do mesmo contexto.

O schema v4 registra `context_boundary`:

```json
{
  "shared_context": [
    "Serviço, controller e testes implementam um único contrato de cadastro de pessoa."
  ],
  "why_one_todo": "Separar essas alterações duplicaria a redescoberta do domínio e enfraqueceria a validação focada.",
  "separate_from": [
    "O CRUD de loja possui modelo, regras e fronteira de teste independentes."
  ]
}
```

Um revisor independente precisa aprovar `context_boundaries_sound` antes da execução.

## Subtarefas retomáveis dentro de cada TODO

Cada TODO do schema v4 contém checkpoints estáveis. O estado autoritativo fica em `manifest.json`; Markdown é projeção regenerada.

```json
{
  "subtasks": [
    {
      "id": "S001",
      "title": "Adicionar persistência de pessoa",
      "objective": "Criar entidade, migração e operações do repositório.",
      "required": true
    },
    {
      "id": "S002",
      "title": "Implementar a API de pessoa",
      "objective": "Adicionar regras do serviço, endpoints e testes focados.",
      "required": true
    }
  ]
}
```

O worker registra checkpoints somente pelo controller conciso:

```bash
python <skill-dir>/scripts/planctl_concise.py subtask-start \
  --plan .ai-work/<plan-id> --task 001 --subtask S001

python <skill-dir>/scripts/planctl_concise.py subtask-complete \
  --plan .ai-work/<plan-id> --task 001 --subtask S001
```

Após interrupção, subtarefas concluídas continuam concluídas. Apenas checkpoint interrompido em `in_progress` volta a `pending`. Outra IA continua do primeiro checkpoint inacabado sem reler a conversa anterior.

## Aprendizado validado e seletivo

Contextos novos economizam tokens, mas um TODO pode descobrir algo caro que ajuda um TODO futuro semelhante. O planejador declara antecipadamente um alvo estreito:

```json
{
  "learning_targets": [
    {
      "task_id": 2,
      "reason": "O CRUD de loja usa o mesmo adaptador de validação do framework.",
      "topics": ["adaptador de validação", "comando de teste focado"]
    }
  ]
}
```

Somente depois da validação determinística da origem o orquestrador pode criar:

```text
.ai-work/<plan-id>/learnings/001-to-002.md
```

Se não houver descoberta reutilizável, nenhum arquivo é criado. Aprendizados precisam ser curtos, fundamentados em evidência e específicos ao alvo. Transcrições, logs, relatórios completos e conselhos genéricos são rejeitados.

O worker reporta a lista exata `learning_files_read`.

## Gate adaptativo de estudo

Antes de planejar, a skill:

1. preserva e inventaria cada parte independentemente testável do pedido;
2. classifica a complexidade antes de explorar amplamente;
3. localiza evidência no repositório antes de abrir arquivos em massa;
4. decide se pesquisa externa atual/autoritativa é materialmente necessária;
5. resolve perguntas de alto impacto e registra somente evidência + impacto no plano;
6. passa por revisão independente e regra de parada;
7. converte achados em requisitos, riscos, restrições e implicações de validação.

O estudo canônico fica em `study.json` e uma projeção compacta em `STUDY.md`. O planejamento fica bloqueado até:

```bash
python <skill-dir>/scripts/studyctl_concise.py validate-plan --plan .ai-work/<plan-id>
```

## Contexto progressivo de execução

- omitir contexto compartilhado é o padrão;
- criar `CONTEXT.md` apenas para informação necessária a todos os TODOs;
- criar `contexts/<topic>.md` apenas para subconjuntos estritos;
- manter informação de um único TODO na própria tarefa;
- manter descobertas de execução em aprendizados validados, não no contexto imutável do plano.

Cada worker reporta exatamente quais arquivos atribuídos de contexto e aprendizado leu. Leituras ausentes ou extras são rejeitadas.

## Estrutura de um plano

```text
.ai-work/<plan-id>/
├── .plan-and-execute
├── manifest.json
├── orchestrator.config.json
├── REQUEST.md
├── STUDY.md
├── study.json
├── ANALYSIS.md
├── PLAN.md
├── PLAN_REVIEW.md
├── TODO.md
├── CONTEXT.md                 # opcional
├── contexts/                  # opcional
├── learnings/                 # aprendizados validados
├── tasks/                     # contrato compacto de cada TODO
├── results/
└── logs/
```

`manifest.json` é autoritativo. `TODO.md` fica em uma linha por tarefa. A definição que o worker lê contém somente objetivo, contexto/aprendizados atribuídos, checkpoints, escopo, orientação não óbvia, aceitação e validação; justificativas de planejamento/review permanecem no estado estruturado em vez de serem repetidas para cada worker.

## Modos de execução

### Workers nativos em contexto novo

Dentro do Claude Code ou Codex, cada worker recebe apenas:

- a definição compacta de sua tarefa;
- os arquivos exatos de contexto atribuídos;
- os aprendizados validados atribuídos;
- instruções e código do repositório realmente necessários.

Ele não recebe pedido completo, plano inteiro, tarefas futuras, transcrições antigas ou relatórios não relacionados.

### Runner externo estrito

```bash
python <skill-dir>/scripts/run_concise.py --plan .ai-work/<plan-id>
```

O runner cria um processo não persistente por TODO, executa validação independentemente, trata escalonamento/indisponibilidade, limita saída diagnóstica e monta o resumo final a partir de estado autoritativo compacto — sem reler relatórios brutos de workers.

Rota padrão:

```json
{
  "provider_order": ["claude", "codex"]
}
```

Outras CLIs permanecem opt-in via `orchestrator.config.json`, task provider ou resume:

```bash
pae resume --provider gemini --once
pae resume --provider qwen --once
pae resume --provider kimi --once
pae resume --provider trae --once
```

Use `pae doctor --json` para verificar CLIs disponíveis.

## Comandos de ciclo de vida

```bash
pae current                     # inspecionar implementação ativa
pae resume                      # recuperar e continuar
pae resume --once               # executar no máximo um TODO pai
pae cancel                      # remover plano ativo e preservar código
pae reset --force               # remover planos reconhecidos do workspace
```

O lifecycle corrige ponteiros antigos, impede runners concorrentes, recupera tarefa/subtarefa interrompida e preserva checkpoints concluídos.

## Segurança

O Plan and Execute não contorna permissões, sandboxes, regras do repositório, políticas organizacionais ou políticas de sistema.

O runner impõe:

- um worker de escrita por vez no mesmo working tree;
- validação determinística fora da declaração de sucesso do worker;
- limites para task/context/learning/report/falha/input do sumário;
- cleanup protegido por sentinel e validação da raiz;
- nenhuma operação destrutiva irreversível automática sem autorização.

Depois da validação final e do handoff, o cleanup remove somente o workspace verificado de planejamento/controle. Código, testes, artefatos de produto, commits e alterações não relacionadas permanecem.

## Instalação e manutenção

```bash
pae status both --cwd /caminho/do/projeto
pae paths both --cwd /caminho/do/projeto
pae doctor --json
pae uninstall both --cwd /caminho/do/projeto
```

O instalador usa marcador de propriedade e SHA-256 do diretório e se recusa a sobrescrever destinos não gerenciados, modificados, não relacionados ou links simbólicos fora das condições documentadas.

Referências:

- [Guia em português](skill/plan-and-execute/references/INSTALLATION.pt-BR.md)
- [English installation guide](skill/plan-and-execute/references/INSTALLATION.md)

## Desenvolvimento

```bash
npm run check
```

Esse comando limpa artefatos gerados, valida skill/pacote, executa testes Node e todos os self-tests Python, incluindo orçamento/vagueza dos artefatos, isolamento de contexto, memória de tarefas, lifecycle, estudo, economia de tokens, preservação no cleanup e adaptadores de provedores.

Referências principais:

- [Escrita precisa dos artefatos](skill/plan-and-execute/references/ARTIFACT_WRITING.md)
- [Estudo adaptativo](skill/plan-and-execute/references/ADAPTIVE_STUDY.md)
- [Protocolo de planejamento](skill/plan-and-execute/references/PLANNING_PROTOCOL.md)
- [Schema do plano](skill/plan-and-execute/references/PLAN_SPEC.md)
- [Contexto de execução](skill/plan-and-execute/references/EXECUTION_CONTEXT.md)
- [Workflow](skill/plan-and-execute/references/WORKFLOW.md)
- [Ciclo de vida](skill/plan-and-execute/references/LIFECYCLE.md)
- [Roteamento de modelos](skill/plan-and-execute/references/MODEL_ROUTING.md)
- [Economia de tokens](skill/plan-and-execute/references/TOKEN_EFFICIENCY.md)

## Licença

MIT. Consulte [LICENSE](LICENSE).
