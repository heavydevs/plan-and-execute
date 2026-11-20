# Handoff da task 015 para uma nova conversa independente

**Repositório:** https://github.com/heavydevs/plan-and-execute  
**Branch:** `checkpoint/plano1-estudo-provider-switch-20261028`  
**Plano:** `.ai-work/20261028-skill-study-provider-switch/`

## Objetivo e isolamento

Uma conversa nova pode fazer **revisão técnica cega** em uma sessão distinta da conversa que implementou. Ela não deve consultar a conversa anterior nem os pareceres produzidos por Qwen antes de registrar seu próprio parecer. Entretanto, o simples fato de abrir outra conversa **não prova** que o revisor possui tier max nem fornece `provider/model/native_effort/session_id` autenticados exigidos pelo `check_delivery.py`. Não declarar gate formal concluído sem essa prova.

## Estado conhecido (reconfirmar no HEAD remoto)

A task 015 continua **pending**. S001 está concluída; S002–S006 pendentes; não existem `docs/research/20261028-skill-optimization/implementation/015-receipt.json` e `015-outcome.md`. O resultado da revisão local Qwen foi suplementar, não equivalente a max. O `manifest.json` é a autoridade; consultar o estado atual antes de agir.

## Revisão cega — ordem de leitura

1. `AGENTS.md`, `guia_de_pesquisa_execucao_tasks.md`, `.ai-work/chatgpt-executor/ENTRYPOINT.md`, este handoff, task 015 e `docs/plans/20261028-skill-optimization/TASK_INPUTS.json`.
2. Contrato: `docs/research/20261028-skill-optimization/prepared-research/014-context-learning.md`, `docs/research/20261028-skill-optimization/pesquisas-por-task/015-pesquisa-arquitetura.md`, `docs/research/20261028-skill-optimization/implementation/014-receipt.json` e `014-outcome.md`.
3. Código atual de `skill/plan-and-execute/scripts/{planctl.py,artifact_contract.py,runner_contract.py}`, `test/optimization/context_learning_self_test.py`, `skill/plan-and-execute/references/{EXECUTION_CONTEXT.md,TOKEN_EFFICIENCY.md}`.
4. **Não ler até finalizar o primeiro parecer:** `.ai-work/chatgpt-executor/STATUS-015.md`, análises de triagem, `docs/research/20261028-skill-optimization/implementation/reviews/015/offline/` ou conversa anterior. Isso reduz viés de confirmação.

Verificar integridade de learnings e SHA, referências `#symbol`, symlinks, stale inputs, retries, prompt injection, contexto atribuído, prefixo/sufixo e limites de tokens. Cada achado requer severidade, `path:line`, caso reproduzível, evidência e correção sugerida. Distinguir ausência de achado de cobertura insuficiente.

Salvar a **revisão técnica**, com HEAD e hashes de arquivos efetivamente revisados, em `.ai-work/chatgpt-executor/reviews/015/new-chat-review.md`. Commit e push na mesma branch sem force. Não inventar sessão ou identidade de modelo; um commit GitHub não atesta o executor da revisão.

## Depois do parecer independente

Só então comparar com reports históricos e reproduzir achados graves. Se corrigir código, revisão inicial não aprova automaticamente os novos hashes: pedir nova revisão do snapshot final. Executar testes reais via `resource_watch.py` (`P1_TESTS_015` e `P1_015`) no checkout exato; alternativa para baixar os arquivos: `.ai-work/chatgpt-executor/SNAPSHOT_BRIDGE.md`. O gate formal continua dependendo de `docs/plans/20261028-skill-optimization/support/review_dispatch.py` ou mecanismo equivalente **formalmente aceito**, com dados autenticados de modelo, esforço e sessão. Sem essa capacidade, manter a task 015 pendente — não criar recibos fictícios nem alterar status.

## Prompt curto para nova conversa

> Revise de forma independente e cega a task 015 do repositório https://github.com/heavydevs/plan-and-execute na branch `checkpoint/plano1-estudo-provider-switch-20261028`. Leia `.ai-work/chatgpt-executor/HANDOFF_REVISAO_015_NOVO_CHAT.md` e siga-o. Não consulte conversas nem pareceres anteriores antes de publicar seu primeiro parecer. Faça inspeção técnica real com evidências, reproduções e hashes; registre o parecer em arquivo, commit/push e depois verifique o gate formal sem simular revisão de outro provedor. Se o gate exigir prova de revisor max não disponível, deixe 015 pendente e informe o bloqueio.
