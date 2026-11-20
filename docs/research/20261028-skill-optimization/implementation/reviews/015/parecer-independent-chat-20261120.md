# Task 015 — parecer independente inicial (2026-11-20)

**Independência do diagnóstico:** esta sessão analisou o código antes de consultar pareceres anteriores. Isso **não equivale** ao reviewer externo max-tier exigido pelo gate `P1_015`.

**Fonte:** commit `f4e34f09c249e5109d861d5c28b5030c35d990fb` (código igual a `fcfa9b11082ddcf3059bb40e9594c038187ea345`). Snapshot de 1.069 arquivos, GitHub Actions run `44820565518`; SHA-256 do tar.gz `78d2f7779d5e52c7587fd72ba869b6a256a617a6d5c36eb70299ed1d7c23b9d7`.

## Hashes Git blob examinados

| Arquivo | Blob SHA |
|---|---|
| `skill/plan-and-execute/scripts/planctl.py` | `c95ac903ec196a381de28f4deef54143e1b84bc3` |
| `skill/plan-and-execute/scripts/runner_contract.py` | `c13fa8da09a6470fa33eeedf405245db1ae0c7af` |
| `skill/plan-and-execute/scripts/artifact_contract.py` | `48c2b06f3a1832134f1447170d26c48fb4eaa604` |
| `skill/plan-and-execute/references/EXECUTION_CONTEXT.md` | `2d879ea9fd8d9bee29594e952553de9fc45fb6fb` |
| `skill/plan-and-execute/references/TOKEN_EFFICIENCY.md` | `d7b8865b2f33293f45a10fb18fb834493fe2fc49` |

## F015-A — HIGH: promoção de hipótese mediante prova declarada e não verificada

**Arquivo/linhas:** `skill/plan-and-execute/scripts/planctl.py:5673-5734`, especialmente verificação de `deterministic_evidence` em `5705-5727`.

**Reprodução real:** em execução Python isolada no snapshot, criei uma hipótese aberta e uma relação autorizada `015 → 016`; forneci `[{"passed":true,"exit_code":0,"command":"python /definitely-not-existent-test.py"}]` a `promote_hypothesis_to_learning`. O método aceitou a entrada e retornou o learning com a hipótese no estado `promoted`, embora o comando nunca tenha sido executado. Para o teste foi neutralizada apenas a persistência de manifest em diretório temporário; a lógica de validação não foi alterada.

**Impacto:** um chamador que controla esse argumento pode transformar hipótese não comprovada em fato reutilizável. O fluxo precisa verificar proveniência e integridade de recibo determinístico, não apenas campos preenchidos.

## F015-B — MEDIUM: referência explícita de hipótese ausente não invalida

**Arquivo/linhas:** `skill/plan-and-execute/scripts/planctl.py:5409-5497,5499-5542`.

**Reprodução real:** `normalize_attempt_hypothesis` com `evidence_refs=["missing.py#symbol"]` e `repo_root` de um diretório temporário sem esse arquivo produz `evidence_digests={}`; `check_hypothesis_freshness` devolve `[]`, marcando a hipótese como fresca. Referências de arquivos existentes foram corretamente detectadas após edição. A falha é particular à fonte explicitamente declarada e ausente, que deveria bloquear reutilização.

## Arquitetura, testes e pendências

O código tem escopo por produtor/consumidor, classe de confiança, SHA de contratos, fingerprints de fontes citadas, verificação do Markdown e filtros de policy override. Os dois achados acima são contraexemplos reais às garantias pretendidas. A suíte de sete testes declarados foi iniciada localmente e seus sete logs exibiram sucesso, mas a execução do orquestrador expirou no host sem gerar `result.json`; **não** é correto considerar o gate local concluído. No GitHub Actions run `44818552920`, os checks direcionados passaram e os gates supervisionados falharam. O motivo do watcher precisa ser investigado.

**Ação:** corrigir os dois defeitos com regressões, repetir os testes e obter revisão externa real no SHA final, com ID de sessão, modelo/esforço e recibo verificável. Não aprovar `015` nem avançar para `016` enquanto os gates permanecerem incompletos.
