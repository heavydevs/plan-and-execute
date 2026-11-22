# Task 015 — primeiro parecer técnico independente (inspeção cega)
Data: 2026-11-22. Repositório: heavydevs/plan-and-execute. Branch: `checkpoint/plano1-estudo-provider-switch-20261028`.

## Proveniência e limites
- `review_channel=chatgpt_web_new_conversation`; `review_kind=technical_review`; `review_status=changes_requested_pending_reproduction`; `gate_approved=false`.
- Revisor nesta conversa: `model=GPT-6` (identidade fornecida pelo runtime); `native_effort=unavailable`; `chat_session_id=unavailable`; `review_attempt_id=web-20261122-d72cd5d-blind` é apenas ID documental e **não** um ID de sessão de inferência.
- Base imutável de inspeção: commit `d72cd5d62f2a60e35588ed80179ce88d522f7cea`; Git tree `5b47f9f17ba649df800532e8c6235d73a3b704d6`. A API GitHub autenticada forneceu os arquivos dessa branch, com os blobs abaixo. Este parecer foi elaborado **antes de consultar** outcomes 014/015, diretório de pareceres anteriores, status histórico, comentários de outros agentes ou conversas prévias.
- Consultei AGENTS.md, guia_de_pesquisa_execucao_tasks.md, ENTRYPOINT.md, HANDOFF_REVISAO_015_NOVO_CHAT.md, definições das tasks 014 e 015, TASK_INPUTS.json (registro 015), pesquisa e arquitetura de 014/015 e os seis arquivos centrais. `run_isolated.py` foi consultado apenas para rastrear o consumidor do relatório: blob Git `0a6ac88e9a9edade9bd432893b8a9cc9101edec4`.
- O manifesto do plano possui 1.331.070 bytes (Git blob `4f5f82a6bbfb61484d0ebbe2598786856e211f65`) e sua leitura completa ficou indisponível na API de arquivos (>1 MiB); a definição de task 015 está `pending` e a 014 `completed`. Confirmar estado contra manifesto em snapshot executável.
- **Esta etapa documenta análise estática de código real; não atribui exit codes nem aprovações de testes que ainda não foram executados.** O checkout por `git clone` foi impedido por falha de DNS de `github.com` no container; investigar snapshot exportado pelo Actions na etapa seguinte.

## Integridade de código revisado (blobs e SHA-256 dos bytes retornados pela API GitHub)

| Arquivo | Git blob SHA-1 | SHA-256 |
|---|---|---|
| `skill/plan-and-execute/scripts/planctl.py` | `f1bdf107b20dcef958cb31e1b785d4efc7f533d5` | `bbf88e7623d92fee1e5d7b040c4fa59902c7f77613532ef7247444d5c5a680cc` |
| `skill/plan-and-execute/scripts/artifact_contract.py` | `48c2b06f3a1832134f1447170d26c48fb4eaa604` | `3af9ebb88b3f6c4e377df7e032246cd5eee5d481c234d779314d98bc5fe76aea` |
| `skill/plan-and-execute/scripts/runner_contract.py` | `b1035f49d754d604880c83a98011dca05c16b883` | `7764a5f27abb48e9acb600c6ab253da33925b40a96bf5166b46cc8ddfec276c9` |
| `test/optimization/context_learning_self_test.py` | `302ec61ecf135b47d5696b307bb13b30b86a5996` | `b011f3cfc59e2466426c32b1bd611b7871b6892a39e3a9bcaadc2dabf9b2180f` |
| `skill/plan-and-execute/references/EXECUTION_CONTEXT.md` | `bd0c38f09ac93a679982f0494bcd539c7cbb78f1` | `d0ffd9470b49511359ae4b344d14a4b6b6ce6ff7fb8d667accccfb5f1701d57a` |
| `skill/plan-and-execute/references/TOKEN_EFFICIENCY.md` | `d7b8865b2f33293f45a10fb18fb834493fe2fc49` | `2f7107c3e620e1629e4fddeab4247ee43bc215acc0b03c61683966d717a9ad08` |

## Achados da primeira inspeção (a reproduzir na etapa de execução)

### F-015-WEB-01 — MÉDIA/ALTA (integridade de proveniência): fonte declarada com extensão não reconhecida é aceita sem digest
- **Arquivo/linhas**: `skill/plan-and-execute/scripts/planctl.py:4645-4682`, `:5249-5259`, `:4794-4812`.
- **Rastreio verificável no código**: `explicit_learning_source_file(ref, require_plain_file=True)` classifica referências sem âncora somente se `Path(...).suffix` está numa lista fechada; **`.proto`, `.graphql`, `.tf`, `.vue` não constam**. Em `materialize_learning_artifacts`, uma referência como `schemas/missing.proto` ausente não gera `cited_file_digests` (extração ignora arquivos ausentes) e retorna `None` no classificador; assim não há exceção `Learning source reference missing or unsafe`. Na checagem de frescor o mesmo classificador descarta a referência, de modo que o manifesto pode transportar fato supostamente validado sem rastrear a origem. Se o arquivo não existia na publicação, sua criação posterior não invalida o aprendizado.
- **Reprodução executável proposta** (não executada nesta inspeção): num fixture de três tasks igual ao usado em `test/optimization/context_learning_self_test.py:1156-1189`, publicar learning de 001 para 002 citando apenas `schemas/missing.proto`, sem criar esse arquivo. Observar que `complete_task` conclui sem erro, `cited_file_digests == {}`, e `check_learning_artifact_freshness(...).fresh == True` quando deveria falhar fechado. Repetir com `.py` como controle: o teste existente demonstra rejeição.
- **Impacto/ação**: normalizar a semântica de referência (arquivo x ID/URL/comando) sem deixar extensões arbitrárias escapar, adicionar teste negativo para extensão comum fora da allowlist e verificar criação posterior.

### F-015-WEB-02 — MÉDIA (autenticidade de validação no caminho manual de conclusão): sucesso informado em JSON é elegível a publicar `validated_learning`
- **Arquivo/linhas**: `skill/plan-and-execute/scripts/planctl.py:4995-5020`, `:6374-6465`, `:6975-6982`, `:2843-2855`; wrapper `artifact_contract.py:783-805`.
- **Rastreio verificável no código**: `command_complete` carrega `--report` e chama `complete_task` sem executar checks. `normalize_reusable_learnings` aceita o `validation_results` desse report quando `passed: true`, `exit_code: 0` e comando não vazio, e permite materializar o learning. `build_task_receipt` copia os mesmos flags sem comprovar execução do runner. A proteção de prova V2 (log + sidecar + receipt) está corretamente aplicada a `promote_hypothesis_to_learning` em `:5892-5922`, mas **não** à publicação ordinária de learnings no caminho manual. A rota de produção `run_isolated.py:2183-2265` executa/atualiza resultados, limitando o risco à conclusão fora do runner; não confundir isso com bypass de um atacante sem acesso ao plano.
- **Reprodução executável proposta** (não executada): repetir o fixture de `test/optimization/context_learning_self_test.py:138-193` com `completion_report` fabricado e learning para task 002, porém sem executar `test -f implemented.txt`; inspecionar `learning_artifacts`, `trust_class=validated_learning` e ausência de proof/log do runner. Verificar também a rota CLI direta `planctl complete --report`.
- **Impacto/ação**: definir explicitamente quando a conclusão manual deve ser considerada confiável, impedir emissão do rótulo `validated_learning` sem prova autenticada/observável, manter compatibilidade com tarefas legadas e testes que deliberadamente usam relatórios sintéticos.

## Cobertura favorável observada
- Isolamento por consumidor no `claim_task` (`planctl.py:6319-6363`) e testes `test_ac01...`, `test_review_015_fresh_learning...`.
- Hash da Markdown de learning e checagem de symlink antes de consumo (`planctl.py:4769-4786`); preflight dos caminhos de invalidação (`:4904-4920`).
- Proteção contra promoção direta de hipótese refutada e exigência de prova runner V2 (`:5807-5922`).
- Prefixo estrutural fixo e contabilização de bytes sem afirmar cache hit real (`runner_contract.py:14-32,106-149`).
- Estes controles não foram declarados como resultados de testes executados.

## Decisão e próximos atos
**Parecer técnico inicial: mudanças solicitadas/condicionadas a reprodução.** Executar no snapshot autenticado do commit pinado os casos mínimos acima, os sete comandos `required_checks`, `P1_TESTS_015`, `P1_015` e `check_delivery.py`. Corrigir achados confirmados com regressões focais, repetir toda a bateria e solicitar **nova inspeção independente do código alterado**. Este primeiro parecer só examina o commit `d72cd5d62f2a60e35588ed80179ce88d522f7cea`. Sem prova real de `max-tier`, `native_effort` e `session_id`, não preencher recibo final como aprovado e não avançar à 016.
