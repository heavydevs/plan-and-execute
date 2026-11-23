# Task 015 — novo parecer original Opus 5.5: correção obrigatória

**Fonte autêntica:** [GitHub Actions run 45112038861](https://github.com/heavydevs/plan-and-execute/actions/runs/45112038861), artifact `14790705348`, `review_dispatch.py --task 015 --provider claude`.
**Modelo:** `claude-opus-5-5`, `native_effort=xhigh`, `model_tier=max`, modo somente leitura.
**Sessão autêntica:** `87b82154-a83e-442e-95c4-88be83e6a6d0`.
**Dispatch original:** `docs/research/20261028-skill-optimization/implementation/reviews/015/dispatch-2.json`, SHA-256 `ff346b08bc4b8a19f6c51913dc1cd483c2ce747d0baff4ea53461fecdf6e7e10`.
**Veredito:** `changes_requested`, exatamente 10 achados: 1 HIGH, 5 MEDIUM, 4 LOW. Este relatório é síntese fiel para a correção, não um recibo de aprovação nem substituto do artifact.

## Achados reproduzíveis relatados pelo revisor

**F01 HIGH — `planctl.py:4624,4663,4958-4972,4814-4822,5264-5273,5667-5672`:** referência com espaço/vírgula (`src/x.py#L3 (helper)`, `src/a.py, src/b.py`, `src/marker.py MARKER`) atravessa `normalize_learning_reference`, mas `extract_cited_repo_files` descarta strings com espaços; `explicit_learning_source_file` também retorna `None`. O digest fica vazio e não há rejeição de learning ou hipótese; editar arquivo citado pode deixar aprendizado aparentemente fresco. Corrigir rejeitando formatos ambíguos ou identificando e fixando todos os tokens de arquivo. Adicionar negativos para learning e hipótese.

**F02 MEDIUM — `014-receipt.json:14-128`:** hashes históricos de seis artefatos diferem do código final revisado; receipt 014 lista AC01–AC08, mas não evidencia explicitamente o último critério de pesquisa não equivaler a entrega. Não reescrever retroativamente recibo 014 como se comprovasse hashes atuais. Reexecutar as regressões pertinentes à 014 contra o código final e registrar cobertura autêntica na entrega 015; investigar separadamente se alterar o recibo 014 é permitido pelo escopo.

**F03 MEDIUM — `planctl.py:99-156,556-560,649-653,885-890`:** detector lexical confunde proibições protetoras (`Never skip validation commands`, `Do not bypass the sandbox`, `Do not override the provider policy`) com tentativas de override; também considera `edit only task outputs in scope` como single-task. Pode impedir `validate_plan` e retomada de planos existentes. Tornar detecção sensível a negações e restringir padrão single-task a identidade de tarefa real, com testes de compatibilidade.

**F04 MEDIUM — `planctl.py:5909-5917`:** limite de 8 hipóteses pode descartar uma entrada `disproven` e permitir reintrodução posterior da alegação refutada; ou descartar imediatamente uma entrada `open` recém-criada e reutilizar seu ID. Nunca perder barreiras de refutação; recusar novo registro quando limite não puder ser respeitado sem perda ou reter tombstones; testes de 9+ hipóteses.

**F05 MEDIUM — `planctl.py:5038-5042,5930-5960,6133-6191,6494-6556`:** guard de hipóteses refutadas verifica apenas o produtor ao publicar; não verifica o plano global na entrega/claim, e uma hipótese refutada depois pode deixar aprendizado previamente publicado disponível. Unificar guard de publicação, invalidação e claim; impedir vazamento ao consumidor; testes cruzados com múltiplas tasks.

**F06 MEDIUM — `runner_contract.py:93`, `run_isolated.py:768,788-823`:** `bounded_task_suffix` não recebe `plan_dir` e chama `failure_context(task)` sem esse contexto; caminho da evidência de falha não aparece no prompt conciso de produção. Corrigir a assinatura/caller, preservar teto de 1.400 caracteres, adicionar teste assertando a linha de pacote de evidência.

**F07 LOW — `planctl.py:6365-6370,7284-7294,4881-4891` e `run_isolated.py:2126-2136`:** métricas/invalidação de aprendizados revisitam consumidores já concluídos e podem quebrar um worker ativo. Separar consumido de pendente.

**F08 LOW — `planctl.py:4925-4949`:** arquivos de aprendizado são apagados antes de `save_manifest` confirmar geração, permitindo estado inconsistente quando commit falha. Salvar antes ou usar trash transacional.

**F09 LOW — `runner_contract.py:39-47`, `planctl.py:6829-6838`:** prompt de retry usa só as últimas duas hipóteses; entradas automáticas `open` podem ocultar refutações importantes. Priorizar refutações dentro do orçamento.

**F10 LOW — `EXECUTION_CONTEXT.md:79,92,116`:** texto diverge do código quanto a tópico obrigatório, refs de arquivos faltantes e exemplo `tests/...::timeout`. Alinhar docs ou implementar regra.

## Ordem para a correção Claude Sonnet + Plan-and-Execute

Reproduzir e corrigir primeiro **F01 HIGH** e **F03/F04/F05/F06 MEDIUM** dentro do `write_scope` da task 015, adicionando regressões adversariais. Para F02, guardar a proveniência histórica da 014 e registrar evidência atual sem sobrescrever evidência antiga. Avaliar F07–F10 se correção segura e no escopo; não criar regressões nem alterar validador para aprovar artificialmente.

A saída do Sonnet é **patch de escopo restrito**, não aprovação. GitHub Actions executa testes originais e monitores; depois é obrigatória outra revisão independente Opus sobre os NOVOS hashes, novo dispatch e recibo formal aceito. Sem Antigravity. **Nunca iniciar 016; ao concluir 015 por gate oficial, parar.**
