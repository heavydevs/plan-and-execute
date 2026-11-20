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

---

## Parecer adicional da sessão independente 2026-11-20 18:46 (BRT)

Este parecer foi redigido antes de consultar relatórios de revisão anteriores, inicialmente salvo em arquivo local com SHA-256 eee583b38d2af5ea81ad3e936689891521349dad55e2ae64c629d0cfe472e021. A sessão é independente de conclusões anteriores, mas NÃO é a revisão externa max-tier por outra IA exigida pelo gate S002/P1_015. Não houve aprovação simulada.

### PAE-015-01 — HIGH, demonstrado

Em skill/plan-and-execute/scripts/planctl.py:6045-6085 (baseline ab951d128098e880afe904bd526d23afa45b4db2), remove_learning_artifacts_from_source aceitava caminho de manifest sem verificar a localização canônica e inspecionava apenas path.is_symlink() no arquivo final. Reprodução executada: plan/learnings era symlink para diretório outside, a rotina retornou o caminho removido e apagou outside/001-to-002.md. Outra reprodução com manifest.file=tasks/important.md removeu arquivo não pertencente à pasta de aprendizados. Impacto: integridade e exclusão fora do plano.

### PAE-015-02 — HIGH, demonstrado no aprofundamento

Em skill/plan-and-execute/scripts/planctl.py:5193-5200 (mesmo baseline), materialize_learning_artifacts gravava por atomic_write_text após seguir symlink ancestral. Reprodução executada: plan/learnings apontando para outside; complete_task concluiu e criou outside/001-to-002.md. Impacto: escrita fora do plano.

### Correções e regressões

Commit com push confirmado: 84278fb000c84859aaa770fe49c72d43280ca500, fix(task-015): constrain learning publication and reset to safe canonical paths. A publicação valida caminhos canônicos e symlinks em todos os destinos antes de gravar. O reset valida todos os caminhos e symlinks antes de qualquer remoção e revalida antes do unlink. Quatro testes negativos foram adicionados:

- test_review_015_reset_rejects_non_learning_manifest_path
- test_review_015_reset_rejects_symlinked_learning_parent
- test_review_015_reset_preflights_every_artifact_before_unlinking
- test_review_015_publication_rejects_symlinked_learning_directory

Primeira execução dos novos testes antes da correção: exit 1, Expected PlanError containing 'unexpected path'. Depois da correção, a bateria focal passou (exit 0), e os sete scripts declarados passaram no container (self_test.py foi repetido isoladamente após uma primeira execução interrompida por timeout e terminou exit 0).

### SHA-256 do código — baseline -> corrigido

- planctl.py: 7288ce852a565f3371c0e2c0733250d408d8f8ff5b6256d5b254f1aa5435e108 -> d55231ba9739d4b52a3e11f9b0da01c69832bd53958261372f4c3abffe7b1ac0
- test/optimization/context_learning_self_test.py: 403077f7bf231e2ecefa6f45fb0cf45483cd02cdfe8c0caed452ed15aabb1450 -> e6651ee700b9cd9836fd3a964e51cc7503eb2e111f46676fa4ba50831ba911c7
- artifact_contract.py (inalterado): 3af9ebb88b3f6c4e377df7e032246cd5eee5d481c234d779314d98bc5fe76aea
- runner_contract.py (inalterado): c7bab30e4c6a5a09a244481ee2fdf1f8e06ec8e7512740b743680e904dd98cf5
- references/EXECUTION_CONTEXT.md (inalterado): ca9878dbbd42a0da9a16169112c0cd58e90aeea816135e990f5390bfde087396
- references/TOKEN_EFFICIENCY.md (inalterado): 2f7107c3e620e1629e4fddeab4247ee43bc215acc0b03c61683966d717a9ad08

### Provas autenticadas e gate

Snapshot de origem: GitHub Actions run 44823644185, artefato 14670994269, ZIP SHA-256 04a90e06d5d3aee0cd22b23ac08cd2c2762c8a8c4f5a2863cb7b2b728ad6679d. CI do commit corrigido: run 44825817681, jobs 3.10 e 3.13. Artefatos 14674316058 (Python 3.10) e 14672834852 (Python 3.13). Resultados py3.13 verificáveis em result.json: source_unchanged=true, targeted=passed, 7/7 testes exit 0, P1_TESTS_015 exit 0, P1_015 exit 1. Log P1_015: DELIVERY REJECTED: Missing evidence: .../015-receipt.json. O workflow tem conclusão global failure, não success.

Dispatcher original executado em primeiro plano nesta sessão: exit 2, NO_REVIEW task=015 dispatch=2: no provider could review (codex:missing_cli, claude:missing_cli). Nenhum session_id, model, native_effort, reviewed_input_hashes ou RECEIPT_REVIEWER válido foi gerado. A rota Copilot continua dependente de entitlement externo previamente bloqueado; não simular evidência, nem repetir tentativas faturáveis sem mudança concreta.

**Parecer técnico: duas vulnerabilidades HIGH reproduzidas e corrigidas, patch comprovado por testes, mas entrega FORMALMENTE BLOQUEADA pela independência/modelo externo e pelo P1_015.** Task 015, S002 e demais gates permanecem pendentes. Não iniciar 016.

---

## Nova auditoria da task 015 — 2026-11-20, base `4045dd2871607e75be1a767c08410cd2cb81c050`

Este parecer foi formulado nesta sessao a partir de `AGENTS.md`, do guia, task 015, pesquisas e **codigo e testes atuais**, antes da leitura de pareceres preexistentes. Trata-se de analise deste chat (GPT-6), **nao** de revisor externo max-tier independente nem de `RECEIPT_REVIEWER` valido.

- **015-R3-01 / HIGH**: `skill/plan-and-execute/scripts/planctl.py:4845-4865`, hash de base Git blob `b8096244a892ac2c64af7f066a0aea2f3606ba54`. Em `invalidate_stale_learnings`, o primeiro artefato stale era removido antes da prevalidacao do proximo. Se o segundo `file` apontasse para `tasks/important.md`, um `PlanError` tardio deixaria o primeiro arquivo apagado sem gravar o manifest. **Correcao**: prevalidacao de todos os destinos antes de qualquer `unlink`, com caso adversarial que verifica ausencia de exclusao parcial.
- **015-R3-02 / HIGH**: `skill/plan-and-execute/scripts/planctl.py:4597-4653, 5138-5145` no mesmo blob base. `explicit_learning_source_file` so classificava referencias com `#` ou `::`; uma referencia simples `src/missing.py` podia perder o fingerprint ao ser omitida por `extract_cited_repo_files` e, depois, nao ser invalidada. **Correcao**: reconhecer nomes de arquivos de codigo/documentacao com extensoes conhecidas mesmo sem ancora; rejeitar fonte ausente, capturar digest e invalidar apos edicao. IDs sem extensao e comandos continuam tratados como evidencia nao-arquivo.

**Hashes de entrada**: `planctl.py` `b8096244a892ac2c64af7f066a0aea2f3606ba54`; `context_learning_self_test.py` `7dc15887e57dc5d528d50ee344345de496e4d41c`; `artifact_contract.py` `48c2b06f3a1832134f1447170d26c48fb4eaa604`; `runner_contract.py` `c13fa8da09a6470fa33eeedf405245db1ae0c7af`; `EXECUTION_CONTEXT.md` `2d879ea9fd8d9bee29594e952553de9fc45fb6fb`; `TOKEN_EFFICIENCY.md` `d7b8865b2f33293f45a10fb18fb834493fe2fc49` (Git blob SHA-1 do GitHub, ligados ao commit base).

**Entrega**: as regressoes novas e correcoes necessitam de execucao no commit publicado e evidencia CI; a revisao externa max-tier com `provider/model/native_effort/session_id/reviewed_input_hashes` permanece obrigatoria. Nao gerar `015-receipt.json` nem fechar `P1_015` antes de evidencias reais. Task 015 e checkpoints S002-S006 continuam pendentes. Nao iniciar 016.
