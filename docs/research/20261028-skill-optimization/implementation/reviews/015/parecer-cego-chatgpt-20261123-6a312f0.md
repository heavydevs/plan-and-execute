# Task 015 — Primeiro parecer independente (inspeção cega)

Data: 2026-11-23. Repositório: `heavydevs/plan-and-execute`. Branch: `checkpoint/plano1-estudo-provider-switch-20261028`.
**HEAD analisado: `6a312f0027a08ffbf9046c5ed0ac243d5ece2ac7`.** Esta inspeção foi feita numa conversa ChatGPT nova em relação ao desenvolvimento, antes de ler `014-outcome.md`, `015-outcome.md`, relatórios/revisões históricas ou conclusões de outros agentes. Não representa revisão Opus/max-tier nem substitui `review_dispatch.py`.

## Baseline de arquivos inspecionados — Git blob SHA

| Arquivo | Git blob SHA |
| --- | --- |
| `skill/plan-and-execute/scripts/planctl.py` | `d5686a736f2b375b81c26dda2e06162bac604845` |
| `skill/plan-and-execute/scripts/artifact_contract.py` | `03778a3ba28d6d343ec7685470e8344c76765c7c` |
| `skill/plan-and-execute/scripts/runner_contract.py` | `8431b035829399dba5d628e2bfa5f45e5e719f0e` |
| `skill/plan-and-execute/scripts/run_isolated.py` | `dc08d451253f94af6ec704afa6d946e5ad7b0698` |
| `skill/plan-and-execute/scripts/pattern_runner_contract.py` | `933b3d0cecb9977d91623c8a8ced3ae6fe6b032a` |
| `test/optimization/context_learning_self_test.py` | `9d472aff3278c4be26b941afa249f8247f744f9c` |
| `skill/plan-and-execute/references/EXECUTION_CONTEXT.md` | `3e97cf0196cf5319547030733d8dd87376879f01` |
| `skill/plan-and-execute/references/TOKEN_EFFICIENCY.md` | `d7b8865b2f33293f45a10fb18fb834493fe2fc49` |

Os hashes acima são **Git blob SHA**, não SHA-256; os checks do runner deverão produzir hashes SHA-256 observados. A pesquisa e os aceites foram lidos de `015-pesquisa-arquitetura.md`, `014-context-learning.md`, da definição 015 e de `TASK_INPUTS.json`. Código avaliado nas funções `claim_task`, `check_learning_artifact_freshness`, `materialize_learning_artifacts`, `normalize_reusable_learnings`, `check_safe_hypothesis_probe`, `promote_hypothesis_to_learning`, `require_runner_proof_for_learnings`, `finish_task_validation`, e `build_context_accounting_receipt`.

## Achados próprios antes de consultar revisões anteriores

**F015-C1 — P2 / médio: métrica de cache não medida registrada como `false`.**
- **Local:** `skill/plan-and-execute/scripts/planctl.py:6331-6335`.
- **Evidência no código:** `build_context_accounting_receipt` grava `cache_reuse.mode = observed_metric_not_structural_assertion` e `cache_reuse.observed = False` incondicionalmente. Não há observação de métricas de host nesse caminho. Já `runner_contract.prompt_cache_structure` usa `cache_reuse_observed = None`.
- **Cenário reprodutível proposto:** emitir `context-receipt` para um plano válido sem executar chamada ao provedor; verificar `observed`. O recibo reporta `false` mesmo quando a realidade é **desconhecida**. Esperado: `null` ou equivalente explícito a não medido. Impacto: diagnóstico incorreto em decisões de economia/benchmark.

**F015-C2 — P2 / médio: `stale_learning_count` conta motivos em vez de aprendizados.**
- **Local:** `skill/plan-and-execute/scripts/planctl.py:6273-6285, 6327-6329`.
- **Evidência no código:** um único learning sem autorização e com mais de um motivo de obsolescência adiciona uma entrada em `stale_errors` por motivo, mas `stale_learning_count = len(stale_errors)`. Pode apresentar 2+ aprendizados obsoletos para um único arquivo.
- **Cenário reprodutível proposto:** construir um único artefato vinculado ao consumidor errado e com outro erro de frescor; chamar `build_context_accounting_receipt`; comparar número de arquivos stale versus campo `stale_learning_count`. Esperado: contagem de arquivos, com motivos preservados em campo separado.

**F015-C3 — P2 / médio: ausência de contexto normativo pode ser reportada como selecionado/fresco.**
- **Local:** `skill/plan-and-execute/scripts/planctl.py:6211-6237, 6248-6263`.
- **Evidência no código:** `add_entry` usa tamanho zero para `target.is_file() == False`, e o parâmetro padrão `fresh=True` permanece mesmo quando um arquivo de contexto atribuído deixou de existir. O recibo offline resultante não sinaliza a ausência.
- **Cenário reprodutível proposto:** remover um arquivo global/scoped atribuído no fixture e gerar o recibo; conferir `selected_files[].fresh` e `bytes`. Esperado: erro explícito ou `fresh=false`, sem tratar arquivo ausente como contexto válido. Não afirmar que isto sozinho contorna `claim_task` ou `validate_plan`, que possuem verificações separadas.

## Avaliação de riscos e limites

A implementação contém salvaguardas relevantes: digests de contrato e arquivos citados, verificação de aprendizagem atribuída na reivindicação, barreira contra publicação por `complete --report` sem prova do runner, gramática restrita para probes `grep`, e comparação de estado pré/pós-probe. A inspeção não estabelece cobertura completa contra agentes hostis com acesso de escrita ao plano; a própria documentação limita a garantia de integridade no mesmo usuário do SO.

**Estado do parecer:** `changes_suggested` para os três achados de telemetria/diagnóstico; nenhum critical/high foi provado na leitura estática realizada. Os três cenários ainda **não foram executados** neste instante: o container não resolve `github.com`, e o repositório foi lido pelo conector GitHub. Isto não é aprovação, prova de testes, review formal max-tier, nem certificação do gate.

Próximas provas: criar casos negativos focais, executar checks no GitHub Actions sobre o SHA do patch, executar a rota de revisão externa autêntica no último hash, e verificar `P1_TESTS_015`, `P1_015` e `check_delivery.py`. **A task 016 permanece fora de escopo.**
