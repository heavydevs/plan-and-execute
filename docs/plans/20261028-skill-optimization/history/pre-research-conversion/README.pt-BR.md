# Plano 1 - estudo da skill, troca de fornecedor e criação do Plano 2

Data: 28/10/2026. Base funcional: versão 0.11.0.

**Plano criado e validado estruturalmente. Execução ainda não iniciada: 86 TODOs pendentes.**
As pesquisas completas, revisões externas, implementação da troca de fornecedor e geração do Plano 2 são entregas futuras deste plano, não resultados já concluídos.

## O que o Plano 1 produzirá

O pedido anexado foi preservado integralmente em `REQUEST_ORIGINAL.md` e no `REQUEST.md` do plano nativo. O plano primeiro estudará toda a skill, completará o inventário de mecanismos e pesquisará cada tema em fontes verificáveis. Cada tema terá uma revisão independente com o modelo mais forte efetivamente disponível e permitido.

A melhoria específica de troca de fornecedor ao atingir o topo está dentro do Plano 1, conforme a instrução expressa do anexo. As demais otimizações aprovadas alimentarão o Plano 2. Trabalho já concluído no Plano 1 não voltará a aparecer como implementação pendente no Plano 2.

## Estrutura

| TODOs | Finalidade |
|---|---|
| 001-005 | Revisão inicial, auditoria completa e inventário de funcionalidades. |
| 006-069 | 32 pesquisas por tema, cada uma seguida de revisão independente no nível máximo. |
| 070-081 | Seis etapas de projeto/implementação da troca de fornecedor e handoff, cada uma com revisão. |
| 082-085 | Consolidação das outras melhorias e criação/validação do Plano 2. |
| 086 | Revisão final da skill inteira e da entrega, obrigatoriamente a última tarefa. |

São 45 requisitos rastreados e 44 tarefas de revisão no nível máximo. Os 32 temas são uma lista inicial, não uma alegada auditoria completa: o inventário deve incluir outros temas descobertos e acrescentar os pares pesquisa/revisão antes da consolidação.

## Troca de fornecedor: resultado esperado

A opção ficará desligada por padrão. A implementação deverá reconhecer o topo pelo modelo resolvido e pelo esforço realmente despachado, evitar repetições inúteis e garantir acesso aos fornecedores elegíveis dentro de uma regra de orçamento explícita. Quota e indisponibilidade continuarão separadas de falhas funcionais.

O handoff será curto, redigido para remover segredos antes da truncagem, validado e marcado como não verificado. Ele complementará as evidências determinísticas, sem alterar classe de falha, rota ou status. A escolha entre campo no relatório, retomada nativa, chamada adicional e resumo determinístico pertence à pesquisa e à decisão revisada, não foi antecipada como implementação aprovada.

Os 12 casos de aceite do anexo estão mapeados em `ACCEPTANCE_MATRIX.md` e `ACCEPTANCE_MATRIX.json`.

## O que foi realmente feito nesta preparação

A cópia local foi restaurada do backup 0.11.0. O commit local `6e6ba53` e o remoto `193fefd` têm a mesma árvore `f4b5a2285b7f2b1089d974c9e60814e46db858f4`. O código de execução da skill não foi alterado.

Foram indexados os 188 arquivos versionados da base, com hashes e localizações de símbolos. A leitura dirigida e a simulação sem fornecedores reais reproduziram o esgotamento antes de alcançar fornecedores posteriores e o erro de tier `advanced` sem modelo. A simulação não mede economia real de tokens ou dinheiro.

Houve uma consulta inicial a documentações oficiais e ao resumo de um artigo. O registro diferencia páginas consultadas, metadados e fontes apenas localizadas. Isso não substitui as 32 pesquisas profundas; livros integrais e todos os fornecedores não foram analisados nesta preparação.

## Validação real

| Verificação | Resultado |
|---|---|
| Criação, schema e auditoria nativos do plano | Aprovados. |
| Integração do estudo preparatório | Aprovada. |
| Mapa e vínculo das 86 validações | Aprovados. |
| Verificador estrutural do plano | Aprovado. |
| Testes do verificador de entregáveis | 11 testes aprovados. |
| Roteamento existente | 28 casos aprovados. |
| Roteamento de modelos existente | Autoteste aprovado. |
| Roteamento por tipo de trabalho existente | 16 testes aprovados. |
| Entregável da revisão 001 ausente | Rejeitado, como esperado; a tarefa permanece pendente. |
| `git diff --check` | Aprovado. |
| `npm ci --ignore-scripts --offline` | Aprovado. Não equivale a executar hooks do `npm ci` normal. |
| Linha de base completa de `npm run check` | Inconclusiva: interrompida pelo limite de 200 segundos do ambiente. |
| Revisores autenticados, validação real de fornecedores e Windows | Não executados. |

As evidências ficam em `docs/research/20261028-skill-optimization/evidence/`. `PREPARATION_CHECKS.json` registra os comandos, códigos de saída e logs. Um teste estrutural aprovado não equivale à aprovação semântica da pesquisa nem comprova a identidade de um revisor.

## Estado do Git e permissões

A branch local é `feat/skill-study-and-provider-switch`, criada a partir de `main`, seguindo a instrução mais recente do anexo. Não foi criada branch remota. Não houve commit, push, PR, publicação, instalação ou alteração da configuração global.

O único arquivo já versionado modificado é `.ai-work/SERVICE_MAP.md`, para registrar as validações deste plano. Os demais arquivos novos estão nos diretórios de planejamento, pesquisa e controle. O controle nativo é ignorado pelo Git por padrão, mas está incluído no ZIP de entrega.

## Retomada e portabilidade

O plano nativo está em `.ai-work/20261028-skill-study-provider-switch/`. Contém `manifest.json`, `TODO.md`, 86 definições de tarefa, requisitos, estudo e configuração. `autostart` está desligado; não existe execução em segundo plano.

A primeira tarefa é a revisão independente do próprio plano. Os executáveis `claude`, `codex` e `agy` não estão disponíveis neste ambiente. A execução autenticada depende da confirmação exigida pelo anexo e de um ambiente com os provedores configurados. Nenhuma revisão foi simulada.

O manifesto existente guarda o caminho absoluto `/mnt/data/workspaces/plan-and-execute`. Em outro computador, preserve o pacote original e recrie o plano a partir de `PLAN1_SPEC.json` com os controladores nativos, usando outro identificador; não altere status ou `repo_root` manualmente. O arquivo `PORTABILITY.md` traz os comandos. Confirme a base remota antes de um futuro commit/push: os commits local e remoto têm identificadores distintos, embora a árvore de origem seja idêntica.

## Arquivos de entrada por fase

`TASK_INPUTS.json` seleciona o contexto de cada tarefa. `PROTOCOL.md` define o contrato de pesquisa, revisão, custos, segredos e evidências. `FEATURE_SEED.json` lista os temas iniciais. `SOURCE_TRACEABILITY.json` relaciona requisitos ao anexo. `PLAN2_CONTRACT.md` define a entrega do segundo plano.

## Temas iniciais

| Tema | Mecanismo | Pesquisa | Revisão |
|---|---|---|---|
| F001 | Selective activation, intake and late promotion | 006 | 007 |
| F002 | Oversized request fragmentation and prepared packages | 008 | 009 |
| F003 | Adaptive internal and external study | 010 | 011 |
| F004 | Requirements, task decomposition and schema-v4 state | 012 | 013 |
| F005 | Assigned context, learned facts and token budgets | 014 | 015 |
| F006 | Versioned shared contracts and selective invalidation | 016 | 017 |
| F007 | Leases, resume, cancellation, reset and guarded cleanup | 018 | 019 |
| F008 | Capability floors, evidence ladders and retry accounting | 020 | 021 |
| F009 | Provider chains, cooldowns, quotas and availability ledgers | 022 | 023 |
| F010 | Workload routing for frontend, repair and monitoring | 024 | 025 |
| F011 | Model catalog evidence, caches, snapshots and refresh | 026 | 027 |
| F012 | Fresh workers, delegation gates and prompt-cache boundaries | 028 | 029 |
| F013 | Claude Code and Claude Agent SDK adapter | 030 | 031 |
| F014 | Codex CLI, Agent SDK and schema adaptation | 032 | 033 |
| F015 | Antigravity and legacy Gemini adapter | 034 | 035 |
| F016 | Qwen Code headless adapter | 036 | 037 |
| F017 | Kimi Code CLI adapter | 038 | 039 |
| F018 | Trae Agent adapter | 040 | 041 |
| F019 | Muse Code adapter and session protocol | 042 | 043 |
| F020 | GLM provider profiles | 044 | 045 |
| F021 | DeepSeek provider profiles | 046 | 047 |
| F022 | Independent validation, evidence packets and failure classification | 048 | 049 |
| F023 | Resource discovery, freshness and runtime health | 050 | 051 |
| F024 | Progress windows, cancellation and process-tree safety | 052 | 053 |
| F025 | Durable supervised jobs and validation handoff | 054 | 055 |
| F026 | Read-only watchdog and guarded runner recovery | 056 | 057 |
| F027 | Incremental log scanning, digest and artifact retention | 058 | 059 |
| F028 | Read-only observer and diagnostic assistant | 060 | 061 |
| F029 | Plan-free monitored validation and repair | 062 | 063 |
| F030 | Telemetry, shadow routing and non-inferiority benchmarks | 064 | 065 |
| F031 | Installer, configuration, packaging and cross-platform CI | 066 | 067 |
| F032 | Provider-top switching and evidence-bounded handoff design | 068 | 069 |
