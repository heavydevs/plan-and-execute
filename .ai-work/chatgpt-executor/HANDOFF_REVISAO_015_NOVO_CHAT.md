# Handoff de revisão independente — task 015 — novo chat

Repositório: https://github.com/heavydevs/plan-and-execute
Branch: checkpoint/plano1-estudo-provider-switch-20261028
Plano: .ai-work/20261028-skill-study-provider-switch/

## Objetivo

A nova conversa do ChatGPT deve revisar **cegamente** a implementação da task 014, objeto da task 015, em uma sessão distinta da conversa que implementou o código. Isso proporciona independência de contexto conversacional, mas **não prova automaticamente** que ocorreu um review max autenticado aceito pelo gate original. Nunca afirmar o contrário nem fabricar provider/model/effort/session_id.

## Estado a confirmar na nova sessão

A task 015 estava pending (S001 completo; S002–S006 pendentes); 015-receipt.json e 015-outcome.md ausentes. Reconsultar sempre manifest.json e GitHub HEAD porque este estado pode mudar. Não repetir a pesquisa concluída nem avançar para 016.

## Revisão cega, antes de consultar pareceres anteriores

1. Ler AGENTS.md, guia_de_pesquisa_execucao_tasks.md, .ai-work/chatgpt-executor/ENTRYPOINT.md, definição da task 015, TASK_INPUTS.json[015], docs/research/20261028-skill-optimization/prepared-research/014-context-learning.md, docs/research/20261028-skill-optimization/pesquisas-por-task/015-pesquisa-arquitetura.md, 014-receipt.json e 014-outcome.md.
2. Inspecionar versões atuais de skill/plan-and-execute/scripts/{planctl.py,artifact_contract.py,runner_contract.py}, test/optimization/context_learning_self_test.py, references/{EXECUTION_CONTEXT.md,TOKEN_EFFICIENCY.md} e dependências normativas reais. Calcular SHA-256 dos arquivos examinados e registrar HEAD.
3. **Não consultar antes do parecer inicial**: .ai-work/chatgpt-executor/STATUS-015.md, relatórios da revisão Qwen, triagem em docs/research/20261028-skill-optimization/implementation/reviews/015/offline/ nem conversas anteriores. Evitar viés de ancoragem.
4. Testar integridade de learnings, citações arquivo#símbolo, symlinks/paths, retries, provenance, stale inputs, prompt injection e isolamento de prefixo/sufixo. Findings devem apontar path:line, severidade, reproducer e resultado observado. Se nada for demonstrado, declarar cobertura e limites; não inventar achados.
5. Publicar parecer técnico no caminho .ai-work/chatgpt-executor/reviews/015/new-chat-review.md com HEAD, arquivos/hashes, testes e achados por commit/push na mesma branch e confirmar remoto. **Esse documento sozinho não equivale a review_dispatch nem a recebimento de aprovação final.**

## Depois do parecer independente

- Comparar com resultados anteriores só depois de publicar a análise inicial. Reproduzir findings antes de alterar. Se corrigir código, obter review independente dos **novos** hashes; não autopromover a mesma sessão implementadora a revisor de sua própria correção.
- Executar TASK_INPUTS.json checks pelo resource_watch.py e SERVICE_MAP.md; quando houver recibos autênticos, passar o P1_015 e check_delivery.py sobre SHA final. Para checkout sem rede no ChatGPT: .ai-work/chatgpt-executor/SNAPSHOT_BRIDGE.md. GitHub Actions executa checkout exato.
- O gate original exige reviewer max realmente autorizado, fresh_context, provider/model/native_effort/session, dispatch e hashes verificados. Uma nova conversa ChatGPT pode produzir parecer **tecnicamente independente**, mas não fornece necessariamente metadata autentificada ou equivalência de tier. Se essa prova não puder ser obtida, manter S002–S006 e task 015 pending. Não criar recibo fictício nem alterar validador para contornar o contrato.
- Atualizar status/checkpoints só com os mecanismos oficiais depois da aprovação de todos os gates. Não avançar para a task 016.

## Prompt para colar no novo chat

Faça uma revisão independente e cega da task 015 do repositório https://github.com/heavydevs/plan-and-execute na branch checkpoint/plano1-estudo-provider-switch-20261028. Leia primeiro .ai-work/chatgpt-executor/HANDOFF_REVISAO_015_NOVO_CHAT.md e siga as etapas, sem consultar respostas anteriores nem findings históricos antes do parecer inicial. Inspecione código, decisões, testes e evidências reais, reproduza problemas, registre hashes/cobertura/achados e faça commit/push do parecer técnico. Depois tente validar o gate formal sem simular provider, sessão ou aprovação. Se o review max autenticado não estiver disponível, mantenha 015 pendente e informe a limitação.
