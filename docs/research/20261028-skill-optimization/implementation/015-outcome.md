# Task 015 — correções auditadas e gate pendente (2026-11-20)

**Status:** execução e entrega **pendentes**; **NÃO aprovado**. Não alterar `manifest.json`, S002–S006, nem avançar para 016 enquanto faltar revisão externa autêntica e `P1_015`.

## Separação das evidências e independência

O [primeiro parecer desta sessão](reviews/015/parecer-independent-chat-20261120.md) foi publicado no commit `7c5bb8ad92af203e03298eb85fb2152bda9d63fc` **antes de consultar pareceres anteriores**. Sua análise ChatGPT/GPT-6 não é uma sessão max-tier independente do implementador; a revisão obrigatória continua ausente. Os resultados anteriores de modelos de pesos abertos de 1,5B são suplementares, não prova de capacidade max.

O `review_dispatch.py --repo-root . --task 015` foi executado **de verdade**, em primeiro plano, no checkout snapshot `f4e34f09c249e5109d861d5c28b5030c35d990fb`: **exit 2**, `NO_REVIEW task=015 ... codex:missing_cli, claude:missing_cli`. O dry-run também retornou **exit 2** e explicitou a ausência de ambos os provedores. Não houve `DISPATCH`, sessão, modelo, esforço, JSON de findings ou recibo de review produzidos. A rota Copilot documentada em `GATE_REVISAO_015.md` encontra bloqueio de política/entitlement conforme as tentativas autenticadas no GitHub Actions `44805796561` e `44806119525`; não repetimos chamadas potencialmente faturadas.

## Implementação corrigida neste ciclo

| Achado | Gravidade inicial | Arquivo/linhas no baseline | Correção | Estado |
|---|---|---|---|---|
| F015-A | HIGH | `skill/plan-and-execute/scripts/planctl.py:5673-5734` | `promote_hypothesis_to_learning` exige task concluída, `current_receipt` válido por `validate_receipt`, resultados observados pelo runner e correspondência com validações do recibo. Um `passed=true` arbitrário não autoriza promoção | Corrigido e teste focal local PASS; revisão externa final PENDENTE |
| F015-B | MEDIUM | `skill/plan-and-execute/scripts/planctl.py:5409-5542` | `check_hypothesis_freshness` exige fingerprint para referências explícitas `file#symbol` e `file::symbol`; ausência devolve `evidence_digest_missing:<file>` | Corrigido e teste focal local PASS; revisão externa final PENDENTE |

Novos testes negativos demonstram rejeição da promoção sem recibo e de comando não observado; teste positivo demonstra promoção com evidência preservada de tarefa concluída. O teste de fonte ausente demonstra rejeição persistente mesmo quando arquivo é criado posteriormente, aceitação de fonte corretamente capturada e invalidação após edição.

### Commits efetivamente publicados na branch

- `f4e34f09c249e5109d861d5c28b5030c35d990fb` — request de snapshot completo, run `44820565518` success
- `7c5bb8ad92af203e03298eb85fb2152bda9d63fc` — primeiro parecer independente da sessão
- `4623e285d1af9ff682bc330728419e705212b852` — correção F015-B
- `f599c514382ea2d0256ab800698b5cdebdd90ca7` — regressões F015-B
- `e285e726b53e92b22849e8bfcfe4a03acb03db10` — correção F015-A
- `ccb2292c3f334d8c22de3134e46412fbe5ee1316` — regressões F015-A

**Hashes Git blob dos fontes finais sob revisão:**

- `skill/plan-and-execute/scripts/planctl.py`: `26a768502a5535c59c411a3a1f66fd8be0953de8`.
- `test/optimization/context_learning_self_test.py`: `1697e4128dd5c33411395d5d122875d65fda9779`.
- `skill/plan-and-execute/scripts/runner_contract.py`: `c13fa8da09a6470fa33eeedf405245db1ae0c7af`.
- `skill/plan-and-execute/scripts/artifact_contract.py`: `48c2b06f3a1832134f1447170d26c48fb4eaa604`.
- `skill/plan-and-execute/references/EXECUTION_CONTEXT.md`: `2d879ea9fd8d9bee29594e952553de9fc45fb6fb`.
- `skill/plan-and-execute/references/TOKEN_EFFICIENCY.md`: `d7b8865b2f33293f45a10fb18fb834493fe2fc49`.

## Validações executadas e limitações

No snapshot com os dois patches locais idênticos aos blobs publicados: `python -m py_compile` para fonte/testes e `python test/optimization/context_learning_self_test.py`, `python skill/plan-and-execute/scripts/context_self_test.py`, `python skill/plan-and-execute/scripts/task_memory_self_test.py` e `python skill/plan-and-execute/scripts/artifact_concision_self_test.py` passaram com exit 0. `progress_runner_self_test.py` e `pattern_runner_self_test.py` também retornaram exit 0 na execução anterior à alteração de promoção (que não modifica seus módulos). Uma execução local de `self_test.py` atingiu timeout do host e não gerou resultado final, portanto NÃO é um passe local.

O CI anterior ao patch, run `44818552920`, registrou **7/7 checks direcionados PASS** nas duas versões de Python; `P1_TESTS_015` passou, `P1_015` falhou pela ausência de `015-receipt.json`. Isso **não** é evidência para o hash novo. No workflow de gate dos hashes atualizados [run 44821560072](https://github.com/heavydevs/plan-and-execute/actions/runs/44821560072), os artefatos **reais** `task-015-checks-py3.13` (ID `14671449187`) e `task-015-checks-py3.10` (ID `14671419612`) registram `head_sha=ccb2292c3f334d8c22de3134e46412fbe5ee1316`, `source_unchanged=true`, **7/7 checks direcionados PASS** em cada Python, **P1_TESTS_015 PASS (exit 0)** em ambos, **P1_015 FAIL (exit 1)** em ambos. O log de Python 3.13 registra literalmente `DELIVERY REJECTED: Missing evidence: .../015-receipt.json`. A falha global de CI é o gate de entrega, não falha da bateria funcional. O commit que registra este relatório alterou apenas documentação após esse SHA; os blobs de implementação/testes auditados permaneceram idênticos. Não é prova de revisão independente.

## O que falta para entrega

O contrato exige um **modelo externo max-tier de sessão realmente distinta** com `provider`, `model`, `native_effort`, `session_id`, `reviewed_input_hashes`, findings e veredito verificáveis no SHA final. A execução local de `review_dispatch.py` comprovou indisponibilidade, não revisão. Resolver entitlement de Copilot CLI ou disponibilizar Codex/Claude autorizado, realizar review novo depois da correção, corrigir novos blockers, repetir `P1_TESTS_015` e `P1_015` no SHA revisado, emitir `015-receipt.json` autêntico, checar `check_delivery.py`, avançar checkpoints/status com `planctl` e confirmar push por CAS.

**Não foi criado `015-receipt.json` fictício. O arquivo permanece ausente por segurança até a revisão obrigatória.**
