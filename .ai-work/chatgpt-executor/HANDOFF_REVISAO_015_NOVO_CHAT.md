# `próximo` em novo ChatGPT Web — executar a revisão independente 015

**Repositório:** https://github.com/heavydevs/plan-and-execute  
**Branch obrigatória:** `checkpoint/plano1-estudo-provider-switch-20261028`  
**Plano:** `.ai-work/20261028-skill-study-provider-switch/manifest.json`

## Regra zero: revisar, não somente redirecionar

Quando o usuário escrever somente **`próximo`** em uma NOVA conversa deste Projeto, localizar a primeira task pendente no manifesto. Se for 015, a pesquisa já estiver concluída, os testes direcionados já tiverem evidência e o gate de entrega ainda depender de revisão, **a própria nova conversa deve realizar uma revisão técnica independente e profunda do código**. Não voltar à pesquisa, iniciar a 016, repetir somente status, pedir nova confirmação, nem tentar primeiro Copilot/Codex cuja política/quota já foi bloqueada.

**Independência real:** este chat precisa ser diferente da conversa que escreveu o código avaliado. Não consultar histórico pessoal, memória de conversas, resumos, pareceres, outcomes, PR reviews ou conclusões de outras IAs **antes de gravar o primeiro parecer próprio**. Se o mesmo chat já alterou o código, ele não pode aprovar independentemente essas alterações; deve criar o handoff para um outro chat. Ter GitHub autenticado não prova a identidade do modelo.

## Etapa A — inspeção cega (obrigatória nesta nova conversa)

1. Ler, nesta ordem, `AGENTS.md`, `guia_de_pesquisa_execucao_tasks.md`, `ENTRYPOINT.md`, este arquivo, a task `.ai-work/20261028-skill-study-provider-switch/tasks/015-*.md` e a predecessora `014-*.md`, e o registro 015 em `docs/plans/20261028-skill-optimization/TASK_INPUTS.json`. Verificar o **manifest real**, dependências e `HEAD` remoto.
2. Ler os **requisitos/arquitetura** em `docs/research/20261028-skill-optimization/prepared-research/014-context-learning.md` e `docs/research/20261028-skill-optimization/pesquisas-por-task/015-pesquisa-arquitetura.md`. Esses estudos são inputs de escopo, não conclusões de review.
3. Ler o **código e testes reais**, no SHA recém-confirmado: `skill/plan-and-execute/scripts/planctl.py`, `artifact_contract.py`, `runner_contract.py`, `test/optimization/context_learning_self_test.py`, `skill/plan-and-execute/references/EXECUTION_CONTEXT.md` e `TOKEN_EFFICIENCY.md`. Consultar utilitários realmente invocados conforme necessário; investigar fluxos ponta a ponta, fronteiras de confiança, referências `file:line`, `#symbol`/`::symbol`, invalidação, consumidores autorizados, symlinks, prefixo de prompt e entradas hostis. Obter hash Git e SHA-256 de **cada arquivo efetivamente revisado**.
4. Reproduzir casos suspeitos. Usar checkout real quando acessível; se não houver DNS GitHub no container, seguir `SNAPSHOT_BRIDGE.md` para importar snapshot do SHA exato via Actions. Não confundir snapshot sem `.git` com clone; não inferir testes de uma inspeção estática.
5. Escrever um primeiro parecer **sem ler nada da Etapa B**: gravidade, `path:line`, reprodução, comandos/exit codes/logs quando executados, evidência de cada achado ou cobertura que justifique nenhum achado, decisões de segurança/performance, SHA do código e hashes dos arquivos. Publicar em `docs/research/20261028-skill-optimization/implementation/reviews/015/web-chat-first-opinion-<data>-<shortsha>.md` via commit/push **na mesma branch**, CAS sem force. Registrar status `technical_review`, não `gate_approved`.
6. Identidade: registrar `review_channel=chatgpt_web_new_conversation`; `model` e `effort` somente se de fato conhecidos/verificáveis (não presumir esforço pelo plano). `review_attempt_id` pode identificar a tentativa documental, mas **não** é o `session_id` real do produto. Se URL/identificador real da conversa não estiver acessível ao modelo, escrever `chat_session_id=unavailable`, nunca fabricar UUID e chamá-lo de sessão autenticada. GitHub commit e autor do commit provam a publicação, **não** qual IA escreveu o parecer.

**Não abrir antes da publicação do primeiro parecer:** `docs/research/20261028-skill-optimization/implementation/015-outcome.md`, `014-outcome.md`, `.ai-work/chatgpt-executor/STATUS-015.md`, `docs/research/20261028-skill-optimization/implementation/reviews/015/` (exceto para salvar seu arquivo), relatórios Qwen/Codex/Copilot e conteúdo de outras conversas. O documento atual é uma instrução de procedimento, não um parecer prévio.

## Etapa B — correções e testes após o primeiro parecer

1. Agora consultar evidências anteriores para verificar achados e evitar regressões. Reproduzir cada achado `critical/high`; corrigir **a mesma task** dentro do write scope, acrescentando teste. Sem achado alto e com cobertura adequada, registrar a conclusão independente apenas para o **snapshot realmente revisado**.
2. Executar/verificar os **7 checks** declarados em `TASK_INPUTS.json` e os gates originais `P1_TESTS_015` e `P1_015` pelo watcher. Comparar SHA/fingerprint atuais com CI; CI de outro código não é prova. Consolidar todas as falhas, corrigir com testes focais e repetir a bateria após correções.
3. **Se o novo chat corrigiu código**, seu parecer anterior não é aprovação independente desse **novo** código; gravar os hashes finais e preparar outro handoff para a próxima nova conversa (ou usar outra IA realmente independente). Nunca marcar S002 final como aprovado com auto-review posterior.
4. Produzir `015-receipt.json` / atualizar outcome / avançar `manifest.json` **apenas** depois de todos os critérios originais de aceitação, hashes, recibos e revisão elegível terem sido comprovados, `check_delivery.py` passar e o `P1_015` passar no código final. Não alterar validador para ficar verde, não marcar execução do guia antes do gate, não iniciar 016.

## Distinção essencial: revisão deste chat e gate max-tier

A conversa nova realiza **a revisão técnica independente agora** sem depender de Codex Cloud/Copilot. **O simples fato de ser outra conversa não prova automaticamente** a exigência formal de revisor `max`, `native_effort` e `session_id` do `check_delivery.py`. Confirmar primeiro quais informações do ChatGPT Web são realmente visíveis; não inferir que ChatGPT Team/Plus/Pro ou o nome GPT-6 prova esforço `High/Extra High`. Caso o runtime não exponha ID real da conversa, distinguir claramente identificador da tentativa/URL fornecida pelo usuário de sessão autenticada da inferência. Um link compartilhável também não comprova sozinho a configuração de esforço.

Se faltar apenas essa identidade/capacidade após a revisão técnica e os testes, registrar precisamente a evidência ausente e manter **S002 formal, S006 e a task 015 pendentes**; não reabrir pesquisas nem ficar repetindo as rotas pagas bloqueadas. Considerar alteração formal do contrato **somente** após uma decisão explícita de equivalência com garantias e testes negativos, nunca falsificar `model_tier=max` ou `RECEIPT_REVIEWER`.

## Contexto operacional a verificar, não a presumir

- A última CI de código verificada antes deste handoff foi [44830324858](https://github.com/heavydevs/plan-and-execute/actions/runs/44830324858): 7/7 testes e `P1_TESTS_015` passaram em Python 3.10 e 3.13; `P1_015` falhou por faltar `015-receipt.json`. Novo HEAD pode ter mudado — **revalidar**.
- Pedido de revisão Codex em [PR #21](https://github.com/heavydevs/plan-and-execute/pull/21) recebeu `usage limits reached`; Copilot CLI apresentou `copilot_policy_or_entitlement`. Isso não bloqueia a **Etapa A**.
- A task 015 já tem `015-outcome.md` com histórico de engenharia. Não ler antes do primeiro parecer. O arquivo `015-receipt.json` ainda não existia nesta atualização, mas conferir o HEAD.
- Esta página é o handoff persistente para qualquer nova conversa; não requer colar o histórico do chat anterior.

**Prompt suficiente em uma nova conversa dentro deste Projeto:** `próximo`. Ao identificar a task 015, execute as Etapas A/B acima, em vez de se limitar a informar que falta um revisor.
