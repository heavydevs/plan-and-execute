# Task 015 — segunda revisão externa, correções e testes de regressão (2026-11-22)

## Revisão externa verdadeira
GitHub Actions [45074587919](https://github.com/heavydevs/plan-and-execute/actions/runs/45074587919) executou Claude Code `claude-opus-5-5`, esforço solicitado `xhigh`, sessão `3019bdea-491d-4810-9adf-bcdef7e71c7b` para SHA `fd72e47fade60a268e201d323e12aef713e9cd6f`.
A sessão realmente retornou `changes_requested`, quatro findings (1 MEDIUM, 3 LOW), **não uma aprovação**. Exigência de `native_effort` observada pelo provedor continua sujeita a conferência independente da configuração pedida; pedido xhigh sozinho não prova effort efetivo.

## Achados e patches
- **MEDIUM**: `docs/plans/20261028-skill-optimization/support/check_delivery.py:237-296`: o recibo podia relabelar `provider/model/native_effort/model_tier` sem confirmar no dispatch, e podia transformar revisão aprovada em falso erro anterior para justificar frontier. Corrigido no commit `670cc568f5283086420d5585670686071aeb95c8`: comparar identidade contra dispatch; exigir que provas anteriores tenham verdict `changes_requested` ou `blocked`, tier max e `failure_class/cause` ligados à evidência. Quatro novos testes adversariais, além dos 58 originais.
- **LOW**: `planctl.py:4674-4679`: regex ASCII descartava caminhos de arquivos `app/[id]/page.tsx`, `src/@types/missing.d.ts`, `lib/c++/missing.cpp`, permitindo aprendizado sem digest; corrigido em `ce405027d8f4ad25ece2cbf8ae2624dced50f630`. Regresões de arquivo ausente, arquivo capturado com SHA e alteração posterior.
- **LOW**: `planctl.py:6307-6377`: retry não invalidava hipótese quando o conteúdo fonte mudava após a falha; `claim_task` agora chama `invalidate_stale_hypotheses` antes do prompt. Teste negativo de retry com fonte alterada.
- **LOW/test coverage**: `context_learning_self_test.py` mascarava globalmente o guard `require_runner_proof_for_learnings`; removido mock global, limitado ao fixture sintético que utiliza diretamente `concise_planctl.complete_task`, conservando teste adversarial real contra `--report` fabricado e checksum fictício.

## Fontes pinadas
Commit de código/testes: `670cc568f5283086420d5585670686071aeb95c8`; snapshot exportado via Actions `45075312488`, commit de request documental `3b0b91d7b8d96be20120f560083b0737aee59154`, SHA-256 do tar autenticado `c32a3fd76502d93facf3170940d27e9b5619ed583a68f9ec5eafa8a882eef213`, 1.093 entradas, extração segura sem `.git`.

| Arquivo | SHA-256 |
|---|---|
| `skill/plan-and-execute/scripts/planctl.py` | `225e0d50fb353e74d287f59916a0e9cc020a09d8870b35bca39ba1e4dfd2965e` |
| `test/optimization/context_learning_self_test.py` | `409381e1a484fbe50933ee5af2f015eba9c7529d29d71344bae61640b33a8165` |
| `docs/plans/20261028-skill-optimization/support/check_delivery.py` | `4d949e88afbccbc7f9026651052387c424e68650c77d95c9fa7d0816986b545b` |
| `docs/plans/20261028-skill-optimization/support/delivery_gate_self_test.py` | `b4b75d8ae67489e94cd27c30202a1ca03574811f7b3a828d925919af2692d39d` |
| `skill/plan-and-execute/scripts/runner_contract.py` | `7764a5f27abb48e9acb600c6ab253da33925b40a96bf5166b46cc8ddfec276c9` |
| `skill/plan-and-execute/scripts/artifact_contract.py` | `3af9ebb88b3f6c4e377df7e032246cd5eee5d481c234d779314d98bc5fe76aea` |

## Testes reais e limites
- Snapshot local: `python docs/plans/20261028-skill-optimization/support/delivery_gate_self_test.py` **exit 0, 62/62**.
- `python test/optimization/context_learning_self_test.py` **exit 0** (suite completa; sem mock global).
- `python -m py_compile` para os dois scripts de produção e os dois testes alterados: **exit 0**.
- Tentativa local serial dos sete comandos `required_checks`: 1–6 **exit 0** e logs individuais; controlador de shell da ferramenta atingiu timeout durante o sétimo, de modo que **nenhuma aprovação do sétimo é atribuída ao ambiente local**.
- `python docs/plans/20261028-skill-optimization/support/check_delivery.py --task 015`: **exit 1** `DELIVERY REJECTED: Missing evidence: .../015-receipt.json`; bloqueio esperado e não resultado de teste unitário.
- GitHub Actions [45075312209](https://github.com/heavydevs/plan-and-execute/actions/runs/45075312209), SHA `3b0b91d...`, Python 3.10/3.13: ambas as jobs de CI encerraram em failure **na etapa Original supervised validation gates**. Logs/artifacts do runner devem ser usados para conferir separadamente a bateria direcionada e o `P1_TESTS_015`; não interpretar o workflow como aprovado.

## Status e gate
O parecer externo da segunda rodada solicitou mudanças; foi corrigido, mas **essa sessão não revisou os hashes deste patch**. Necessária terceira sessão independente sobre a versão final, correções de eventuais novos achados e execução do `P1_015` com recibo e hashes legítimos. `015-receipt.json` não criado, `manifest.json`/S002–S006 não marcados completos e **task 016 não iniciada**.
