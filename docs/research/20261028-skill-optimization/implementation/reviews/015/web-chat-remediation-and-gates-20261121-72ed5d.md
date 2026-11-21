# Task 015 — Correções pós-parecer e verificação de gates (2026-11-21 UTC)

**Decisão: CHANGES REQUESTED / entrega FORMALMENTE PENDENTE.** Este relatório complementa, sem alterar retroativamente, o [primeiro parecer cego](web-chat-first-opinion-20261120-0c5c850b.md) publicado **antes** de consultar revisões anteriores. Nenhuma aprovação de reviewer max-tier ou identidade de sessão foi produzida por este chat.

## Origem e hashes finais do código validado

- Branch: `checkpoint/plano1-estudo-provider-switch-20261028`.
- Primeira opinião e hashes do baseline: commit `bbcfe81e8a1763fb6377f090a3d2623114da6bc7`.
- Correção inicial: `53467adb58858b46178cb166dee0c8d4d0717cce`.
- Compatibilidade com casos legados: **código final validado** no commit `72ed5d39eba65e7f1b76d47e97ae54f8fe9d1668`. O commit que apenas registra este relatório não altera esses arquivos.

| Entrada | Git blob SHA-1 final | SHA-256 final |
|---|---|---|
| `skill/plan-and-execute/scripts/planctl.py` | `d969af4e4abdc332fc84aa91ecd6d18af3ad037e` | `76852392c839c37fd83ac3d0f42981ed3eb83af3659e34560dae3a10e9862e85` |
| `test/optimization/context_learning_self_test.py` | `fbcbf94cad12d5919f8f4190298cd37d0ddbf2a7` | `fae4bdebc2642b1fc75bbcd185bf9802e3ffeb010b9ece61d4f686063877404d` |
| `skill/plan-and-execute/scripts/artifact_contract.py` | `48c2b06f3a1832134f1447170d26c48fb4eaa604` | `3af9ebb88b3f6c4e377df7e032246cd5eee5d481c234d779314d98bc5fe76aea` |
| `skill/plan-and-execute/scripts/runner_contract.py` | `c13fa8da09a6470fa33eeedf405245db1ae0c7af` | `c7bab30e4c6a5a09a244481ee2fdf1f8e06ec8e7512740b743680e904dd98cf5` |
| `skill/plan-and-execute/references/EXECUTION_CONTEXT.md` | `2d879ea9fd8d9bee29594e952553de9fc45fb6fb` | `ca9878dbbd42a0da9a16169112c0cd58e90aeea816135e990f5390bfde087396` |
| `skill/plan-and-execute/references/TOKEN_EFFICIENCY.md` | `d7b8865b2f33293f45a10fb18fb834493fe2fc49` | `2f7107c3e620e1629e4fddeab4247ee43bc215acc0b03c61683966d717a9ad08` |

## Correções implementadas, regressões e limite residual

1. **015-F01 / HIGH:** `planctl.py:4931+`: referencias a aprendizados rejeitam delimitadores de Markdown/HTML (crases, `<`, `>`) e tentativas reconhecidas de alterar policy/aceitação. O escape de inline code demonstrado no baseline agora é rejeitado antes de gravar. `test_review_015_reference_cannot_escape_markdown_or_override_policy` cobre casos negativos e referência válida.
2. **015-F02 / MEDIUM:** `planctl.py:4790+` e `5170+`: referencias com **caminhos de diretórios** (`src/missing.py`) agora exigem existência e digest independentemente do kind; o teste `test_review_015_procedure_source_must_be_pinned` verifica rejeição, aceitação após criação e invalidação por mudança.
3. **Compatibilidade:** `task_memory_self_test.py` usa `implemented.txt` como referência em aprendizados `procedure` sem materializar o arquivo. A primeira tentativa de exigir `require_plain_file=True` para *todos* os kinds quebrou o teste existente. Mantivemos a interpretação legada de **basename simples em kind não-code** como referência de evidência, enquanto paths com `/` ou `\\` e referências `code` exigem digest. **Limite conhecido:** um `procedure` com referência simples `missing.py` ainda pode ser tratado como ID de evidência, sem digest. Requer decisão explícita de contrato e migração dos fixtures legados antes de bloquear todos os nomes de arquivo simples; não declarar correção universal.

As correções foram aplicadas no snapshot autenticado do commit `0c5c850b...`; os Git blobs publicados via API foram comparados com `git hash-object` dos arquivos locais, sem divergência.

## Execução real — CI no mesmo SHA final

[GitHub Actions run **44855674700**](https://github.com/heavydevs/plan-and-execute/actions/runs/44855674700), branch/checkout exato `72ed5d39eba65e7f1b76d47e97ae54f8fe9d1668`:

| Ambiente / evidência autenticada | Testes declarados | `P1_TESTS_015` | `P1_015` |
|---|---|---|---|
| Python **3.13.18**, artifact `14686944184`, `task-015-checks-py3.13` | **7/7 PASS**, todos exit 0, `source_unchanged=true` | **PASS**, exit 0, resource monitor 15.897 s | **FAIL**, exit 1 |
| Python **3.10.22**, artifact `14686709778`, `task-015-checks-py3.10` | **7/7 PASS**, todos exit 0, `source_unchanged=true` | **PASS**, exit 0, resource monitor 15.552 s | **FAIL**, exit 1 |

Resultado literal do log supervisionado `P1_015` no Python 3.13:
```text
DELIVERY REJECTED: Missing evidence: /home/runner/work/plan-and-execute/plan-and-execute/docs/research/20261028-skill-optimization/implementation/015-receipt.json
[resource-watch] validation=P1_015 test_exit=1 health=healthy
```

Resultados `result.json` foram lidos diretamente dos ZIPs de artifact **14686944184** e **14686709778**, associados pelo GitHub Actions ao mesmo `head_sha`. CI global `failure` é verdadeiro, **não** deve ser apresentado como sucesso. Testes de segurança do executor, adaptadores offline e reconciliação de mapa também passaram em ambos os jobs. A verificação local, no snapshot sem `.git`, produziu adicionalmente `015-checks.json` com 7 checks exit 0, `inputs_unchanged=true`, fingerprint `243d408d49d721c568cf31f864222a9a4a051245737a197a00599ea9d6958782`; **a prova preferencial** é o CI autenticado.

## Gate independente e o que ainda falta

- O ChatGPT Web/GPT-6 realizou inspeção técnica cega inicial nesta conversa; a interface desta sessão não disponibiliza um `session_id` nativo auditável, `native_effort` certificado ou garantia de tier externo `max`. **Não** utilizar IDs de mensagem, CI, commits ou solicitações de snapshot como substituto de sessão de inferência.
- Não houve `review_dispatch.py` autenticado com revisor externo max-tier neste ciclo. O revisor anterior e relatórios históricos só foram consultados **depois** de publicar o primeiro parecer cego. O código foi modificado depois do parecer, portanto é necessária **nova revisão independente de `72ed5d39...`** e correção de blockers encontrados.
- O gate exige provas de `provider`, `model`, `native_effort`, `session_id`, `reviewed_input_hashes`, findings/veredito por canal independente e os recibos genuínos. O `015-receipt.json` está ausente e não deve ser fabricado; não completar S002–S006, `P1_015` ou o manifesto até a validação real. Não avançar para task 016.
- **Próxima ação:** revisor max-tier realmente autorizado, em sessão diferente, revê os hashes acima; se houver blocker, corrigir e repetir; obter receipt autenticado e então rerodar `P1_TESTS_015`/`P1_015` sobre hashes finais. Concluir `check_delivery.py` e checkpoints só após sucesso real.

