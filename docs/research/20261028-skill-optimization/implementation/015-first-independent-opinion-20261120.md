# Task 015 — primeiro parecer técnico desta sessão (não equivale ao gate externo)

Data: 2026-11-20. Branch: `checkpoint/plano1-estudo-provider-switch-20261028`.
Snapshot de entrada, exportado e identificado pelo workflow GitHub Actions 44826583567: `f97bc37fdcb4919fb2989c63efb9715f3e9eddb5`.
Esta análise foi iniciada consultando AGENTS.md, guia, definição da task, pesquisa preparada 014/015, código e testes atuais, sem ler relatórios anteriores de revisão de IA. O parecer não alega modelo externo, sessão de reviewer autenticada ou aprovação do gate.

## Achado 015-F01 — alta prioridade: violação do direcionamento de learnings

- Local: `skill/plan-and-execute/scripts/planctl.py:6143-6162` (baseline), `build_context_accounting_receipt:5928-5948`.
- Condição: um manifesto inconsistente pode incluir em `task["learning_files"]` um artefato válido destinado somente a outra task.
- Evidência reproduzida em Python 3.13.5, snapshot `f97bc37fdcb4919fb2989c63efb9715f3e9eddb5`: a task 001 publica somente para 002; a task 003 recebe manualmente `learnings/001-to-002.md` em sua lista; `claim_task(003)` retornou sucesso com status `in_progress` e o recibo marcou o arquivo como `fresh=True`. Não é necessário editar o conteúdo do learning ou falsificar seu hash.
- Resultado esperado: bloqueio antes de iniciar a task 003 e registro de referência não autorizada.
- Correção: checar `target_task_id`, `consumer_task_ids` e declaração real da relação fonte→destino na fronteira de `claim_task`; registrar a atribuição indevida como erro de frescor no recibo de contexto.
- Regressão: `test_review_015_fresh_learning_cannot_cross_consumer_boundary`.

## Evidências de testes locais antes da correção

Snapshot `f97bc37fdcb4919fb2989c63efb9715f3e9eddb5`, Python 3.13.5, diretório isolado importado de artefato GitHub com `archive_sha256=8c011e65f2ffe2455943805c337eb1da221ca662d47b68d9ce2752b917260c44`.
- PASS: `python test/optimization/context_learning_self_test.py`.
- PASS: `python skill/plan-and-execute/scripts/context_self_test.py`.
- PASS: `python skill/plan-and-execute/scripts/task_memory_self_test.py`.
- PASS: `python skill/plan-and-execute/scripts/artifact_concision_self_test.py`.
- PASS: `python skill/plan-and-execute/scripts/progress_runner_self_test.py` (20 tests).
- PASS: `python skill/plan-and-execute/scripts/pattern_runner_self_test.py`.
- INDETERMINADO: `python skill/plan-and-execute/scripts/self_test.py` excedeu timeout externo do processo agregado; não atribuir aprovação.
- PASS após patch local: testes context_learning, context_self_test e task_memory_self_test; necessário repetir no SHA publicado.

## Identificação do código

Blob Git inicial do arquivo `skill/plan-and-execute/scripts/planctl.py`: `166cb3bc61ee6935acfdcbfd596a328d76ddd381`.
Blob Git inicial do arquivo `test/optimization/context_learning_self_test.py`: `3801cc3ed98591c64dc8c73bcb05a319b43ff39b`.
Blobs do patch preparado para publicação, respectivamente: `b8096244a892ac2c64af7f066a0aea2f3606ba54` e `7dc15887e57dc5d528d50ee344345de496e4d41c`.

## Limitações e decisão

Não concluída: revisão externa realmente independente max-tier com `provider/model/effort/session` e hash binding; `015-receipt.json` ainda ausente. Não atualizar manifesto, checklist ou estado de 015 para completed antes dos gates `P1_TESTS_015`, `P1_015` e `check_delivery.py` reais. Nenhuma aprovação foi simulada. O teste local contra snapshot não é equivalente aos workflows e à validação com resource watcher.
