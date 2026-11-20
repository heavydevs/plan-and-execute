# Handoff — revisão independente da task 015 em novo chat

Repositório: https://github.com/heavydevs/plan-and-execute
Branch: checkpoint/plano1-estudo-provider-switch-20261028
Plano ativo: .ai-work/20261028-skill-study-provider-switch/
Task: 015 — Review and correct assigned context, learned facts and token budgets (revisão da 014)

## Estado e limites

Na preparação: task 015 **pending**, S001 feito, S002–S006 pendentes, sem 015-receipt.json nem 015-outcome.md. **Confirme o status e o HEAD novamente ao iniciar**. O manifesto é a fonte de verdade; GitHub Actions e relatórios anteriores podem representar commits antigos.

**Um novo chat é uma instância conversacional distinta, mas não garante isolamento completo da memória/instruções do Projeto e não atesta automaticamente provider, session_id, native_effort ou modelo max no repositório.** O gate em docs/plans/20261028-skill-optimization/support/check_delivery.py exige revisão fresh max, identidade real do revisor, hashes de inputs, dispatch e veredito aprovado. Não aceitar JSON escrito manualmente como prova de invocação do revisor. Usar uma nova conversa para review cego é válido como parecer técnico; **não equivale automaticamente ao gate final**.

## Etapa A — revisão cega, sem conclusões anteriores

1. Abrir chat novo no mesmo Projeto (preferencialmente esforço High/Extra High, quando disponível). **Não fornecer o texto da conversa implementadora, nem pedir para recuperar histórico**. O novo chat deve analisar o código como se fosse uma revisão inédita. Selecionar o maior nível de raciocínio disponível ajuda, mas não prova equivalência à rota max do plano.
2. Na branch indicada, ler AGENTS.md, guia_de_pesquisa_execucao_tasks.md, .ai-work/chatgpt-executor/ENTRYPOINT.md, este handoff, definição da task 015 e seu registro em docs/plans/20261028-skill-optimization/TASK_INPUTS.json. Verificar HEAD e dependências. Se 015 não for a primeira pendente, interromper.
3. Material de entrada: docs/research/20261028-skill-optimization/prepared-research/014-context-learning.md, docs/research/20261028-skill-optimization/pesquisas-por-task/015-pesquisa-arquitetura.md, docs/research/20261028-skill-optimization/implementation/014-receipt.json, docs/research/20261028-skill-optimization/implementation/014-outcome.md e os arquivos efetivos atuais:
   - skill/plan-and-execute/scripts/planctl.py
   - skill/plan-and-execute/scripts/artifact_contract.py
   - skill/plan-and-execute/scripts/runner_contract.py
   - test/optimization/context_learning_self_test.py
   - skill/plan-and-execute/references/EXECUTION_CONTEXT.md
   - skill/plan-and-execute/references/TOKEN_EFFICIENCY.md
4. **NÃO ler nesta etapa:** .ai-work/chatgpt-executor/STATUS-015.md, pareceres do Qwen, reports de triagem em docs/research/20261028-skill-optimization/implementation/reviews/015/offline/ ou qualquer conversa anterior. Isso reduz viés de confirmação. Só comparar depois de persistir a análise independente.
5. Procurar falhas reproduzíveis em integridade/proveniência de learnings, hashes de source (incluindo referências com fragmento), path traversal/symlinks, retries, inputs stale, prompt injection, contexto atribuído, prefixo/sufixo estável e contratos de receipt. Examinar o código real, não assumir que documentação/testes comprovam o comportamento.
6. Registrar cada finding com severity, path:line, critério, cenário de reprodução, evidência, causa, correção sugerida e incerteza. Ausência de prova implica "inconclusivo", não aprovação. Documentar cobertura.
7. Gravar o **parecer técnico** em .ai-work/chatgpt-executor/reviews/015/new-chat-review.md, com commit revisado e hashes SHA-256 do conteúdo *efetivamente lido*, além de limites de evidência. Fazer commit/push com CAS. Não inventar session_id, effort, provider, assinatura ou dispatch; commit GitHub por si só não prova a identidade da sessão do modelo.

## Etapa B — corrigir, executar testes e decidir o gate (após o parecer cego)

1. Comparar com findings históricos só após publicar a revisão independente. Para defeitos critical/high, tentar reproduzir antes de alterar. Se erro for falso positivo, documentar contraprova, não alterar código desnecessariamente.
2. Correções apenas no write scope da 015. Depois de mudar o código, obter **outra revisão independente sobre os novos hashes**; esta sessão não pode usar a própria revisão inicial para aprovar modificações que ela implementou.
3. Executar os checks de TASK_INPUTS.json pelo resource_watch.py e SERVICE_MAP.md (P1_TESTS_015 e, depois dos receipts reais, P1_015). Para testes em arquivos locais, usar .ai-work/chatgpt-executor/SNAPSHOT_BRIDGE.md; sem .git o arquivo exportado não substitui um checkout nativo. GitHub Actions pode executar checks no commit exato.
4. Preferir o dispatch independente real em docs/plans/20261028-skill-optimization/support/review_dispatch.py --repo-root . --task 015 quando houver backend autorizado. Sem autenticação/metadata do provedor que satisfaça check_delivery.py, registrar bloqueio específico, manter 015 pending e **não fabricar** 015-receipt.json, 015-outcome.md, S002–S006 ou status completed.
5. Se, e somente se, gate formal e demais critérios passarem com evidências atuais, atualizar manifest/checkpoints pelos mecanismos oficiais; commit/push e confirmar HEAD. Não iniciar 016 antes da conclusão comprovada.

## Prompt inicial para colar no novo chat

Faça uma revisão independente e cega da task 015 do repositório https://github.com/heavydevs/plan-and-execute, branch checkpoint/plano1-estudo-provider-switch-20261028. Leia .ai-work/chatgpt-executor/HANDOFF_REVISAO_015_NOVO_CHAT.md. Não leia o histórico de conversas nem pareceres anteriores antes de concluir seu primeiro review. Estude código, contrato e testes reais; registre findings reproduzíveis, hashes, cobertura e limitações em um arquivo e publique com commit/push. Em seguida verifique os testes e o gate final, sem inventar autenticação de revisor ou recibos. Se faltar comprovação de um reviewer max exigida pelo gate, mantenha task 015 pendente e informe o bloqueio.

**Separação essencial:** nova conversa permite revisão de código independente em contexto conversacional, mas não satisfaz automaticamente a rota max autenticada e a prova de sessão exigidas no gate original.
