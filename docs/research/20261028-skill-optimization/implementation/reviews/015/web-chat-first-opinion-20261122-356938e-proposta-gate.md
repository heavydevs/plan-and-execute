# Task 015 — primeiro parecer independente, snapshot 356938e

- Data: 2026-11-22; repositório: heavydevs/plan-and-execute; branch: checkpoint/plano1-estudo-provider-switch-20261028.
- HEAD do código examinado: `356938e104afe18fa546ff270d4156738ed17180`; árvore Git: `8684febd98e87075a88ad047914acc0561e00b74`.
- Canal de inspeção: nova conversa ChatGPT Web, modelo GPT-6 (informado pelo ambiente); nível nativo de esforço e identificador autenticado desta sessão **indisponíveis**. Nenhum review anterior, outcome histórico nem conteúdo de chats anteriores foi consultado antes deste primeiro parecer.
- **Natureza da prova:** inspeção estática independente de trechos reais obtidos da branch via conector GitHub, requisitos, arquitetura, testes e configuração de CI. Não houve execução local dos testes nem sessão real de revisão Antigravity/Claude nesta inspeção; as execuções de CI citadas são de GitHub Actions. Este documento NÃO é `RECEIPT_REVIEWER`, NÃO aprova o gate formal e NÃO deve preencher S002/S006.

## Fontes e integridade do snapshot

| Arquivo de código, contrato ou teste | Git blob SHA-1 | SHA-256 do conteúdo UTF-8 |
| --- | --- | --- |
| `skill/plan-and-execute/scripts/planctl.py` | `c332137ca47f643655c103627abbf5e8b62e89c0` | `ac98cda491c82fb5e020e0a2df1a635aa80fe44c1ea8083383b4a846951fa1df` |
| `skill/plan-and-execute/scripts/artifact_contract.py` | `03778a3ba28d6d343ec7685470e8344c76765c7c` | `b8d2e529ebe6d3f6ca328dad0890860f313a1f093de097afe870dd4d028a87cb` |
| `skill/plan-and-execute/scripts/runner_contract.py` | `8431b035829399dba5d628e2bfa5f45e5e719f0e` | `81527c2bb6e2a97bce58f9f103bb3e7496be95c1b33ac7eac55adf406bfd3e8f` |
| `skill/plan-and-execute/scripts/run_isolated.py` | `faf7b1939798ccfa06f14811eb8d52da01737e76` | `7cf0cecb7612b55c1152352067bb07a412dc86de78ab80fb0e73df2fb8ea0b7b` |
| `skill/plan-and-execute/scripts/pattern_runner_contract.py` | `933b3d0cecb9977d91623c8a8ced3ae6fe6b032a` | `bb5a8032f8c9154efd9eed165bbdc63f1d258be545da321d7ffaeda7cee20d2e` |
| `test/optimization/context_learning_self_test.py` | `ac7e85d60992af5fdb14aea0880dde5b32df6d6c` | `0f91b198d5918573c5a28e51c03f5e3844a204d341dd7186202bdea13a3834dc` |
| `skill/plan-and-execute/references/EXECUTION_CONTEXT.md` | `d27ea65b81933b630b45f0ec6f82e747e500a480` | `5b87a82d8e88e3a758fb17877800ee8b548e786a8531900a535328c420015c52` |
| `skill/plan-and-execute/references/TOKEN_EFFICIENCY.md` | `d7b8865b2f33293f45a10fb18fb834493fe2fc49` | `2f7107c3e620e1629e4fddeab4247ee43bc215acc0b03c61683966d717a9ad08` |
| `docs/plans/20261028-skill-optimization/support/review_dispatch.py` | `1d2c454d7b407bf473e0a322fc924e354b3be0cc` | `9d4d1c9d1b93b2efd074959c7ab9578f26231c8b1ecdd8fd1e21131b1a74365d` |
| `docs/plans/20261028-skill-optimization/support/check_delivery.py` | `2a5d2d0bf2ae08d541762178c84f903b6a4b384c` | `4d949e88afbccbc7f9026651052387c424e68650c77d95c9fa7d0816986b545b` |

SHA-256 calculado sobre o texto completo obtido para cada arquivo; checagem da implementação SHA-256 feita com vetores conhecidos. Os SHA Git foram devolvidos pelo GitHub. O manifesto do plano excede o limite de retorno de conteúdo do conector e não foi lido integralmente; a definição física da task e `TASK_INPUTS.json` foram lidas. Não inferir conclusão do manifesto a partir deste parecer.

## Achados reproduzíveis ou bloqueios comprovados

### F-01 — ALTA (segurança da futura rota de revisão): Antigravity usa bypass de permissões sem sandbox por padrão

- **Local:** `skill/plan-and-execute/scripts/planctl.py:1481-1496` e `skill/plan-and-execute/scripts/run_isolated.py:1138-1151`.
- **Evidência/como reproduzir:** `default_config()` define `antigravity.skip_permissions=True` e `sandbox=False`; `build_worker_command()` adiciona `--dangerously-skip-permissions` quando `skip_permissions` é verdadeiro e só acrescenta `--sandbox` quando `sandbox` é verdadeiro. A saída padrão determinística pode ser verificada em teste unitário da composição de argv, sem conexão à IA.
- **Impacto:** o adaptador de execução comum não é adequado, sem isolamento adicional, a um revisor que deve ser read-only. Uma instrução maliciosa no código ou nos testes inspecionados poderia induzir alteração/execução não autorizada. **Não foi executado um exploit; o risco é demonstrado pela configuração e argumentos produzidos**.
- **Ação:** adicionar rota de revisão read-only específica, checkout imutável/sandbox, bloqueio de escrita e comparação de hashes antes/depois. Não reutilizar o perfil perigoso da implementação para revisar.

### F-02 — ALTA (bloqueio de integração): o dispatcher formal de revisão não aceita Antigravity

- **Local:** `docs/plans/20261028-skill-optimization/support/review_dispatch.py:76`, `:254-285` e `:315-330`.
- **Evidência/como reproduzir:** `READ_ONLY_ADAPTERS = ('claude','codex')`; `candidate_routes()` ignora qualquer adaptador que não esteja nessa lista, registrando `no_read_only_review_adapter`; `assert_read_only()` também rejeita todos os demais. Reproduzir selecionando `antigravity` como candidato e verificando que não há rota elegível, sem executar modelo.
- **Impacto:** a preferência Antigravity para o gate final da 015 é impossível no contrato atual, independentemente de seu custo/créditos. O fato de existir adaptador `agy` no runner de implementação não significa que ele seja revisor independente formal.
- **Ação:** criar/adaptar contrato de evidência Antigravity com modelo real, esforço efetivamente aplicado, identificador autêntico de sessão, findings, hashes e confinamento read-only. Se o CLI não fornecer esses campos verificáveis, manter o gate pendente e usar outra rota elegível.

### F-03 — MÉDIA (confiabilidade): limites padrão podem deixar agentes aparentemente presos

- **Local:** `skill/plan-and-execute/scripts/planctl.py:1447-1455`, `skill/plan-and-execute/scripts/run_isolated.py:264-275`, `:2018-2027`.
- **Evidência/como reproduzir:** os limites `task_timeout_seconds`, `task_idle_timeout_seconds` e `validation_hard_timeout_seconds` são zero por padrão. Para Antigravity, `antigravity_print_timeout()` transforma ausência de limite em `12h`. O supervisor recebe esses valores e não pode interromper um processo somente por inatividade se o monitor estiver desativado. Reproduzir avaliando os defaults e a função de montagem de timeout com configuração padrão.
- **Impacto:** ausência de progresso não produz decisão/retomada previsível; ainda não há prova de que esta foi a causa exata da falha da CI 015.
- **Ação:** configurar timeout por fase, hard ceiling, heartbeat observável, orçamento finito de tentativas e checkpoints persistentes; separar tempo de revisão LLM de tempo da bateria de testes.

### F-04 — BLOQUEIO FORMAL ATUAL (evidência, não falha funcional demonstrada)

- **Local:** `docs/plans/20261028-skill-optimization/support/check_delivery.py:346-356`, `:368-420`; caminho de saída `docs/research/20261028-skill-optimization/implementation/015-receipt.json`.
- **Evidência:** no HEAD examinado o arquivo de receipt 015 não existe no GitHub (404); o validador exige recibo completo, hashes, logs de todos os checks e despacho/revisor independente com `session_id`. No GitHub Actions run `45083888730`, SHA `356938e...`, steps de testes direcionados e geração de evidência passaram em Python 3.10 e 3.13; o step "Original supervised validation gates" falhou nas duas versões, relatando `checks_executed=2`, `status=failed`, `source_unchanged=true`.
- **Impacto:** não é correto chamar a task 015 de concluída, nem insistir em executar a mesma bateria sem primeiro obter evidência independente válida e resolver o recibo ausente.
- **Ação:** preservar logs/SHAs de CI, verificar resultado de cada gate, obter revisão real sobre o último conteúdo, produzir receipt autêntico e executar o validador original, sem enfraquecê-lo.

## Cobertura revisada e critérios ainda não demonstrados

- Lidos `AGENTS.md`, guia, entrada/handoff operacional, task 015, `TASK_INPUTS.json` 015/014, pesquisa e arquitetura 014/015, arquivos de código/contratos/teste declarados e os fluxos de CI/review. Verificados estaticamente consumidores direcionais, hashes de proveniência em `planctl.py:4713-4861`, rótulos de hipóteses não normativas em `runner_contract.py:34-54`, teste de consumidor não autorizado em `test/optimization/context_learning_self_test.py:214-244`, montagem de comando, monitor de processo e revisão/gate.
- Testes locais desta sessão: **não executados** por indisponibilidade de checkout Git autenticado no ambiente de execução. Testes de CI de SHA exato consultados: [run 45083888730](https://github.com/heavydevs/plan-and-execute/actions/runs/45083888730); a existência de tests verdes não substitui a prova do revisor.
- Exigências não satisfeitas neste parecer: execução local em Python 3.10/3.13, inspeção integral de cada caminho no manifesto de 1,33 MB, demonstração do comportamento end-to-end da revisão independente em Antigravity, autenticidade de sessão e `P1_015` aprovado.
- Resultado técnico deste primeiro exame: **achados de segurança/integração/monitoramento a tratar; gate formal PENDENTE**. Mesmo eventual correção desta conversa exige nova revisão independente nos hashes finais.

## Proposta arquitetural controlada (não aplicada ao runtime por este parecer)

`ChatGPT implementa` -> `testes determinísticos e evidência do SHA` -> `Antigravity revisor read-only em sessão nova, se autenticação/modelo/effort/session_id são verificáveis` -> `findings com linhas e repro` -> `Claude corrige no escopo da task pela skill, monitor de recursos e escalada por falha funcional` -> `testes focais, bateria completa e novo SHA` -> `outro revisor independente para esse SHA (Antigravity preferencial)` -> `check_delivery.py + P1_TESTS_015 + P1_015` -> `planctl completo e push CAS`.

Reprovação por código aciona autocorreção; falta de credencial, quota, sessão ou evidência bloqueia sem repetição paga ou aprovação simulada. O mesmo Claude que corrigiu não pode aprovar sozinho seu próprio patch. Finalizar uma única task por vez; nunca avançar para 016 enquanto 015 estiver pendente.
