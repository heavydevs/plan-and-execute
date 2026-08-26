# Plan and Execute

**Transforme pedidos grandes de programação em planos de implementação estudados, isolados por contexto e retomáveis.**

O `plan-and-execute` estuda o pedido completo e o repositório antes de planejar, cria TODOs rastreáveis aos requisitos, entrega a cada TODO um contexto novo, persiste checkpoints de subtarefas, valida a implementação independentemente e encaminha apenas aprendizados verificados e úteis para TODOs futuros semelhantes.

[Read in English](README.md)

## IAs suportadas para execução

| IA / agente | Suporte de execução | Instalação padrão da skill | Rota padrão | Observação |
|---|---:|---:|---:|---|
| Claude Code | Sim | Sim | Primeiro | Destino padrão do tutorial rápido |
| OpenAI Codex | Sim | Sim | Segundo | Destino padrão do tutorial rápido |
| Google Gemini CLI | Sim | Não | Opcional | Processo CLI headless novo |
| Qwen Code | Sim | Não | Opcional | Processo CLI headless novo |
| Kimi Code CLI | Sim | Não | Opcional | Processo novo em prompt mode |
| Trae Agent | Sim | Não | Opcional | Processo novo com `trae-cli run` |

O instalador npm instala a skill intencionalmente apenas no **Claude Code**, no **Codex** ou em **ambos**. Gemini, Qwen, Kimi e Trae são backends opcionais de execução configurados dentro do plano; eles não entram silenciosamente na ordem padrão de provedores.

## Tutorial rápido: Claude Code e Codex

Requisitos:

- Node.js 18.17 ou superior;
- Python 3.10 ou superior;
- Claude Code e/ou Codex instalados e autenticados.

Instale no workspace atual para os dois agentes padrão:

```bash
npx @luizcgvrj/plan-and-execute install both
```

Ou instale para apenas um:

```bash
npx @luizcgvrj/plan-and-execute install claude
npx @luizcgvrj/plan-and-execute install codex
```

Instale no perfil do usuário:

```bash
npx @luizcgvrj/plan-and-execute install both --global
```

Depois, invoque a skill no Claude Code ou Codex com um pedido grande de implementação, com o caminho de um arquivo de requisitos ou sem argumentos. Sem argumentos, ela primeiro retoma a única implementação inacabada; só cria um rascunho guiado quando o workspace está ocioso.

## Por que a fronteira dos TODOs importa

Um worker novo deve receber um problema semântico coerente, não um conjunto arbitrário de arquivos nem tudo o que apareceu no mesmo parágrafo.

Imagine um pedido com:

- um CRUD completo de pessoa, com entidade, serviço, controller, validações e testes próprios;
- um CRUD completo de loja, com outra entidade, outro serviço, outro controller, outras regras e outros testes.

Quando os dois domínios não compartilham invariantes de negócio, transações, estado de ciclo de vida ou uma fronteira real de validação, devem ser **TODOs separados**. O histórico e a exploração do worker de pessoa não ajudam materialmente o worker de loja.

A regra oposta também é importante: não crie um TODO para cada arquivo. Entidade, serviço, controller, migração e testes focados podem permanecer juntos quando implementam um único comportamento e se beneficiam do mesmo contexto de trabalho.

O schema v4 exige que cada tarefa registre um `context_boundary`:

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

Um revisor independente do plano precisa aprovar `context_boundaries_sound` antes da execução.

## Subtarefas retomáveis dentro de cada TODO

Cada definição de tarefa do schema v4 contém sua própria checklist estável. O estado autoritativo fica no `manifest.json`; os arquivos Markdown são projeções regeneradas.

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

O worker registra checkpoints somente pelo controller:

```bash
python <skill-dir>/scripts/planctl.py subtask-start \
  --plan .ai-work/<plan-id> --task 001 --subtask S001

python <skill-dir>/scripts/planctl.py subtask-complete \
  --plan .ai-work/<plan-id> --task 001 --subtask S001
```

Depois de falta de energia, processo encerrado ou interrupção do provedor, as subtarefas concluídas continuam concluídas. Apenas a subtarefa interrompida em `in_progress` volta para `pending`. Outra IA, em um contexto novo, continua do primeiro checkpoint inacabado sem ler a conversa anterior.

O TODO pai não pode ser concluído enquanto houver subtarefa obrigatória pendente.

## Aprendizado validado e seletivo

Contextos novos economizam tokens, mas às vezes um TODO descobre uma solução difícil que deve ajudar outro TODO semelhante. O Plan and Execute cria uma ponte estreita de aprendizado sem carregar o chat da tarefa de origem.

O planejador declara antecipadamente os alvos direcionais:

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

Somente depois que a tarefa de origem passa pela validação determinística o orquestrador pode criar um arquivo conciso como:

```text
.ai-work/<plan-id>/learnings/001-to-002.md
```

Uma origem de aprendizado declarada também é um pré-requisito de contexto: o alvo não começa antes que todas as origens capazes de ensiná-lo terminem. Se a origem não encontrou nada reutilizável, nenhum arquivo é criado e o alvo não gasta tokens adicionais.

Cada aprendizado precisa ser curto, fundamentado em evidências, relevante ao alvo declarado e classificado como código, procedimento, decisão, armadilha ou validação. Ele pode apontar para código exato, testes, comandos ou uma explicação técnica compacta.

O mecanismo rejeita:

- alvos não declarados ou voltados para trás;
- alvos que já começaram;
- notas vazias, excessivas ou sem referências;
- transcrições, logs ou relatórios completos;
- adulteração do arquivo, mesmo quando alguém recalcula manualmente o hash;
- descobertas mutáveis gravadas nos arquivos imutáveis `CONTEXT.md`.

O worker precisa informar a lista exata `learning_files_read`. Quando não existe aprendizado útil, nenhum arquivo é criado e nenhum token futuro é gasto com ele.

## Gate adaptativo de estudo

A skill não cria TODOs depois de uma leitura superficial. Antes disso, ela:

1. preserva e inventaria cada parte independentemente testável do pedido;
2. estuda instruções, arquitetura, entry points, schemas, testes, CI e padrões relevantes do repositório;
3. decide se pesquisa externa atual e autoritativa é materialmente necessária;
4. resolve perguntas de alto impacto e registra evidência e impacto no planejamento;
5. passa por revisão independente do estudo e por uma regra de parada;
6. converte os achados em requisitos, riscos, restrições e implicações de validação.

O estudo canônico fica em `study.json` e é renderizado como `STUDY.md`. O planejamento fica bloqueado até `studyctl.py validate-plan` passar.

## Contexto progressivo de execução

O contexto compartilhado criado durante o planejamento é deliberado e imutável:

- omitir contexto compartilhado é o padrão;
- criar `CONTEXT.md` apenas para informação concisa necessária a todos os TODOs;
- criar `contexts/<topic>.md` apenas para subconjuntos estritos de tarefas;
- manter informação usada por um único TODO na própria definição;
- manter descobertas de execução nos arquivos de aprendizado validado, não no contexto de planejamento.

Cada worker precisa reportar exatamente quais arquivos atribuídos de contexto e aprendizado leu. Leituras ausentes ou extras são rejeitadas.

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
├── CONTEXT.md                 # opcional, contexto universal do planejamento
├── contexts/                  # opcional, contexto restrito do planejamento
├── learnings/                 # aprendizados validados de origem para alvo
├── tasks/                     # uma definição limitada por TODO
├── results/
└── logs/
```

O `TODO.md` continua propositalmente curto. Requisitos, escopo, fronteira de contexto, subtarefas, relações de aprendizado, critérios de aceitação, rota e comandos de validação ficam nas definições de tarefa e no manifest.

## Modos de execução

### Workers nativos em contexto novo

Dentro do Claude Code ou Codex, o orquestrador pode criar um subagente novo para cada TODO. Cada worker recebe apenas:

- sua definição de tarefa;
- os arquivos exatos de contexto de planejamento atribuídos;
- os arquivos exatos de aprendizado validado atribuídos;
- instruções do repositório e arquivos-fonte realmente necessários.

Ele não recebe o pedido completo, o plano inteiro, tarefas futuras, transcrições anteriores ou relatórios não relacionados.

### Runner externo estrito

Em um terminal ou CI:

```bash
python <skill-dir>/scripts/run_isolated.py --plan .ai-work/<plan-id>
```

O runner inicia um processo novo e não persistente do provedor para cada TODO, executa independentemente os comandos de validação, trata escalonamento e indisponibilidade e grava logs e resultados limitados.

A rota padrão gerada continua sendo:

```json
{
  "provider_order": ["claude", "codex"]
}
```

Para usar outra CLI instalada e autenticada, altere o `orchestrator.config.json` ou associe um provedor à tarefa:

```json
{
  "provider_order": ["gemini", "qwen", "claude", "codex"]
}
```

Também é possível sobrescrever uma retomada:

```bash
pae resume --provider gemini --once
pae resume --provider qwen --once
pae resume --provider kimi --once
pae resume --provider trae --once
```

Use `pae doctor --json` para verificar as CLIs disponíveis. Os provedores opcionais nunca são obrigatórios para a instalação padrão.

## Comandos de ciclo de vida

```bash
pae current                     # inspecionar implementação ativa
pae resume                      # recuperar e continuar
pae resume --once               # executar no máximo um TODO pai
pae cancel                      # remover o plano ativo e preservar o código
pae reset --force               # remover todos os planos reconhecidos no workspace
```

O controller corrige ponteiros antigos, impede runners estritos concorrentes, recupera estado interrompido de tarefa/subtarefa e preserva checkpoints concluídos.

## Segurança

O Plan and Execute não contorna permissões, sandboxes, regras do repositório, políticas organizacionais ou políticas de sistema dos provedores.

Provedores headless opcionais podem usar modos de aprovação automática para editar arquivos e executar comandos sem interação. Revise cada configuração, use sandbox ou container quando disponível e execute somente em workspaces confiáveis. O Trae pode trabalhar em container; Qwen e Gemini expõem controles próprios de aprovação e sandbox; workers do Kimi usam o modo documentado `--auto`, enquanto o resumo final usa `--plan`. O Kimi continua opt-in e deve rodar apenas em workspace confiável.

O runner também impõe:

- apenas um worker de escrita por vez no mesmo working tree;
- validação determinística fora da declaração de sucesso do worker;
- contexto limitado por tarefa e por aprendizado;
- limpeza protegida por sentinel e validação da raiz do repositório;
- nenhuma implantação destrutiva, rotação de credenciais, exclusão ampla ou migração irreversível automática sem autorização.

## Instalação e manutenção

```bash
pae status both --cwd /caminho/do/projeto
pae paths both --cwd /caminho/do/projeto
pae doctor --json
pae uninstall both --cwd /caminho/do/projeto
```

O instalador usa marcador de propriedade e SHA-256 do diretório. Ele se recusa a sobrescrever destinos não gerenciados, modificados, não relacionados ou links simbólicos fora das condições de segurança documentadas.

Referências de instalação:

- [Guia em português](skill/plan-and-execute/references/INSTALLATION.pt-BR.md)
- [English installation guide](skill/plan-and-execute/references/INSTALLATION.md)

## Desenvolvimento

```bash
npm run check
```

Esse comando limpa artefatos gerados, valida skill e pacote, executa testes Node e todos os self-tests Python, incluindo isolamento de contexto, memória de tarefas, recuperação do ciclo de vida, evidências do estudo e adaptadores de provedores.

Referências principais:

- [Estudo adaptativo](skill/plan-and-execute/references/ADAPTIVE_STUDY.md)
- [Protocolo de planejamento](skill/plan-and-execute/references/PLANNING_PROTOCOL.md)
- [Schema do plano](skill/plan-and-execute/references/PLAN_SPEC.md)
- [Contexto de execução](skill/plan-and-execute/references/EXECUTION_CONTEXT.md)
- [Workflow](skill/plan-and-execute/references/WORKFLOW.md)
- [Ciclo de vida](skill/plan-and-execute/references/LIFECYCLE.md)
- [Roteamento de modelos](skill/plan-and-execute/references/MODEL_ROUTING.md)

## Licença

MIT. Consulte [LICENSE](LICENSE).
