# Task 015 — primeiro parecer desta sessão (antes de consultar pareceres anteriores)

Data: 2026-11-20. Branch: `checkpoint/plano1-estudo-provider-switch-20261028`.
Código-base inspecionado: commit `780d364e657206509246b76b31991bc5275b16d6` (snapshot Actions run 44829847238; artifact 14676120353; ZIP SHA-256 `f487e2757a186625234e49d4ebcb93100252df5084082eee39b9e291ee1e95b2`).
Revisão humana/analítica desta sessão ChatGPT, **não** evidência de sessão de IA max-tier independente para o gate.

## Achado 015-NEW-01 — HIGH (integridade de proveniência de learnings)

`skill/plan-and-execute/scripts/planctl.py:4648-4666` reconhece citações `path.py#symbol` e `path.py::symbol`, mas não `path.py:12`. O extrator em `planctl.py:4610-4631` já trata `:linha` como âncora ao calcular digests. A discrepância permite que `src/missing.py:12` não exista e, ainda assim, `complete_task` aceite o aprendizado, publicando `cited_file_digests={}`. O consumidor não detectará alteração futura de fonte ausente e pode reutilizar um fato sem proveniência. O caso fere a aceitação 015 (fonte citada inválida não deve ser aceita) e AC02 da tarefa 014.

Reprodução real no Python 3.13.5, a partir do snapshot autenticado: teste `test_review_015_line_anchored_missing_source_rejected` adicionado localmente a `test/optimization/context_learning_self_test.py`, contendo `src/missing.py:12` e exigindo `PlanError`. Antes do patch: `AssertionError: Expected PlanError containing 'Learning source reference missing or unsafe'`. Após patch: teste negativo/positivo passa, incluindo hash de arquivo real e detecção `cited_file_changed:src/missing.py`.

Correção proposta e testada localmente: tratar sufixo `:\d+(?:-\d+)?` como âncora de arquivo no resolvedor e removê-lo antes de extrair o caminho. Preservar a regra de falha fechada e adicionar teste permanente.

## Validações observadas da baseline

Sete comandos requeridos em `TASK_INPUTS.json` foram executados na cópia do snapshot; todos retornaram 0. O monitor de recursos retornou 125 (`service_map_invalid`, snapshot de mapa desatualizado em 5 arquivos), falha de infraestrutura distinta da bateria. Após o patch local, o teste `context_learning_self_test.py` voltou a passar (exit 0). O dispatcher real retornou exit 2: `codex:missing_cli, claude:missing_cli`; **não** houve revisão max-tier nem sessão independente. Nenhum recibo de aprovação é emitido.

## Hashes de fontes de escopo não alteradas no snapshot

- `artifact_contract.py` SHA-256 `3af9ebb88b3f6c4e377df7e032246cd5eee5d481c234d779314d98bc5fe76aea`
- `runner_contract.py` SHA-256 `c7bab30e4c6a5a09a244481ee2fdf1f8e06ec8e7512740b743680e904dd98cf5`
- `EXECUTION_CONTEXT.md` SHA-256 `ca9878dbbd42a0da9a16169112c0cd58e90aeea816135e990f5390bfde087396`
- `TOKEN_EFFICIENCY.md` SHA-256 `2f7107c3e620e1629e4fddeab4247ee43bc215acc0b03c61683966d717a9ad08`

**Veredito inicial:** mudanças solicitadas (HIGH reproduzido). A task 015 permanece `pending`; o parecer deste próprio chat não satisfaz independência.
