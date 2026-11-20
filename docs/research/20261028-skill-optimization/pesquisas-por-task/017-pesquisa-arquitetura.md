# Task 017 — Pesquisa e arquitetura da revisão independente de contratos compartilhados

**Data da pesquisa:** 2026-11-20 (fontes públicas consultadas nesta data). **Branch:** `checkpoint/plano1-estudo-provider-switch-20261028`. **Natureza:** preparação da **revisão futura** de uma implementação, não code review executado, correção de código, teste rodado ou aceite emitido. **Estado da task 017:** `pending`; predecessor 016 também `pending`, com `016-receipt.json` e `016-outcome.md` ainda ausentes no remoto observado. Este documento não muda esses estados.

## 1. Objetivo, dependência e fontes internas

- [Definição da task 017](../../../../.ai-work/20261028-skill-study-provider-switch/tasks/017-review-and-correct-versioned-shared-contracts-and-selective-inva.md): revisar a **implementação real** de 016, corrigir achados bloqueantes dentro do `write_scope` e obter evidência nova da revisão independente e dos testes declarados.
- [Definição da 016](../../../../.ai-work/20261028-skill-study-provider-switch/tasks/016-implement-versioned-shared-contracts-and-selective-invalidation.md): implementação dos contratos versionados; depende de 001, 015 e **019**. A 017 depende diretamente da 016. **Pesquisa concluída de 016 não equivale a implementação concluída.**
- [Arquitetura antecipada 016](016-pesquisa-arquitetura.md), [pesquisa preparada de 016](../prepared-research/016-shared-patterns.md) e `docs/plans/20261028-skill-optimization/TASK_INPUTS.json` (task 017: `review_and_fix`, `review_of=016`, `requires_independent_review=true`).
- `.ai-work/20261028-skill-study-provider-switch/manifest.json`: versão de schema 4, 132 tarefas; registro da task 017 `pending`, dependência 016; registro da 016 `pending`. `TODO.md` e `guia_de_pesquisa_tasks.md` concordam. Conferido via objetos GitHub da branch, não por uma execução local do plano.
- Escopo permitido **na execução futura**: `skill/plan-and-execute/scripts/patternctl.py`, `pattern_runner_contract.py`, `test/optimization/shared_patterns_self_test.py`, `references/SHARED_PATTERNS.md`, mais `implementation/017-receipt.json` e `017-outcome.md`. Não ampliar esse escopo por conveniência. Este estudo apenas cria seu próprio relatório e adiciona o vínculo na task e no guia.

**Pergunta arquitetural principal:** como provar, por revisão realmente independente e fixtures determinísticas, que a evolução de contratos preserva correção com concorrência, falhas, retomada e mudanças cosméticas, sem reabrir trabalho indevido nem consumir contexto/fornecedores desnecessariamente?

## 2. Evidências técnicas do código *antes* de 016 (não são achados definitivos da futura implementação)

Inspeção do código existente na branch em 2026-11-20. É uma **lista de hipóteses de auditoria** para confrontar com os hashes efetivamente entregues por 016, não declaração de defeitos pós-016.

| ID | Âncora observada | Risco a verificar na implementação real | Prova de revisão requerida |
|---|---|---|---|
| I01 | `patternctl.py:38-40`, `216-239` | `write_json` usa escrita direta; projeções são reescritas e arquivos antigos apagados sem protocolo único de recuperação | Interrupções em pontos precisos, nenhum JSON truncado aceito, nenhuma remoção externa, reconciliação idempotente |
| I02 | `patternctl.py:392-459` | `command_update` lê registro sem CAS explícito e chama `planctl.reset_task` **antes** de persistir o novo registro | Dois processos concorrentes, conflito de geração/digest, falhas entre reset e escrita, restabelecimento coerente |
| I03 | `planctl.py:6279-6346`, `3226-3298` | `reset_task` salva manifest e arquiva receipt; `save_manifest` tem geração e lock próprios; múltiplos arquivos não são transação única | Verificar lock/fencing compartilhado e transições compatíveis com schema 4, inclusive crash antes/depois do save |
| I04 | `patternctl.py:69-76`, `55-66` | Digest existente inclui `title` e `source_refs` e faz `strip` por cláusula; isso não demonstra equivalência semântica geral | Norma explícita de canonicalização; alteração normativa nunca classificada como cosmética automaticamente |
| I05 | `patternctl.py:241-305`, `360-380` | Validação compara adoção sobretudo por revisão numérica; o par `adopted_digest`/revisão e a evidência real do consumidor precisam coincidir | Recusar digest adulterado, revision rollback, assinatura sem validação na revisão usada |
| I06 | `pattern_runner_contract.py:34-105` | `pattern_files_read` é uma lista de caminhos; assinatura posterior pode usar o registro atual mesmo se ele mudou desde o dispatch | Revisão+digest fixados no aceite, verificados sob ownership no momento de adotar, sem TOCTOU |
| I07 | `patternctl.py:153-185`, `pattern_runner_contract.py:25-57` | Projeção Markdown inclui histórico; entregar arquivo inteiro pode tornar o contexto do worker proporcional ao histórico, embora só receba padrões atribuídos | Provar limite de conteúdo enviado: contrato corrente + delta curto, sem histórico inteiro |
| I08 | `patternctl.py:79-80`, `216-238`, `292-304` | `slug` vindo de JSON pode compor path; exclusões por `glob` e leituras podem tocar links simbólicos | IDs, slugs, destinos e symlinks seguros, inclusive em Windows; sem escrita/leitura fora do plano |
| I09 | `patternctl.py:404-454` | Isenção de `changed_by` pode deixar uma task concluída com adoção obsoleta | A regra deve depender de estado/evidência, não de identidade da task que solicitou a alteração |
| I10 | `review_dispatch.py:179-239`, `570-656`, `747-820` | Dispatcher exige receipt/outcome do predecessor, faz pin dos hashes e registra sessão, findings e evidência; reutilização é restrita | Revisão genuína, nova para o diff/estado final; gate rejeita recibos de outras tasks/hashes |
| I11 | `test/optimization/shared_patterns_self_test.py` e `implementation/016-receipt.json` | **Ainda inexistentes nesta leitura**, porque 016 está pendente | Não simular resultados. Exigir material real antes de chamar o revisor e executar 017 |

O relatório 016 prévio recomendou CAS + lease de lifecycle + digest semântico + invalidação somente de signatários concluídos obsoletos + recuperação idempotente. O revisor 017 deve **questionar e testar** essas recomendações no código entregue, sem aprovar apenas porque o código declara segui-las.

**Risco de documentação durante a retomada:** no schema 4, `planctl.save_manifest` pode gerar novamente as definições `tasks/*.md` (`planctl.py:3289-3298`). Verificar que o vínculo `017-pesquisa-arquitetura.md` sobrevive à projeção antes da execução; se for apagado, restaurar o vínculo de maneira compatível com o contrato do plano, **sem falsificar conclusão**. O guia também permite reencontrar este relatório.

## 3. Pesquisa externa e força das evidências

Todas as URLs abaixo foram consultadas em 2026-11-20; `s/d` significa que não há data editorial explícita na página consultada. **Fatos das fontes não são benchmarks do repositório nem execução de fornecedores autenticados.**

| Ref. | Documento, autor/editora, data/versão e seção | Conclusão aplicável; confiança / limitação |
|---|---|---|
| E01 | [Google — What to look for in a code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html), Google Engineering Practices, s/d, “Design”, “Functionality”, “Tests”; [Standard](https://google.github.io/eng-practices/review/reviewer/standard.html) | **Alta (norma institucional):** revisão deve confrontar design, casos extremos, concorrência e capacidade dos testes de detectar falhas; não basta a existência de testes. Guia, não experimento causal |
| E02 | [Kubernetes API Concepts](https://kubernetes.io/docs/reference/using-api/api-concepts/), projeto Kubernetes, documentação atual, “Updates to existing resources” | **Alta (contrato oficial):** `resourceVersion`/conflito 409 ilustram CAS; aplicar conceito, não introduzir Kubernetes |
| E03 | [git-update-ref](https://git-scm.com/docs/git-update-ref), projeto Git, manual atual (página aponta 2.53.0), “DESCRIPTION”, “--stdin” | **Alta (manual):** verificação de valor anterior sob lock evita lost update; atomicidade de ref não significa snapshot multi-arquivo |
| E04 | [os.replace](https://docs.python.org/3/library/os.html#os.replace), Python Software Foundation, documentação Python atual, “os.replace” | **Alta (manual):** substituição bem-sucedida de um arquivo pode ser atômica dentro dos limites SO/FS, **não** uma transação sobre registry, manifest e Markdown; verificar Python alvo e persistência em crash |
| E05 | [Atomic Commit in SQLite](https://www.sqlite.org/atomiccommit.html), SQLite, s/d, ``3–5 | **Alta (implementação documentada):** durabilidade e múltiplos arquivos exigem protocolo de journal e lock; serve como contraponto à suposição “rename resolve tudo” |
| E06 | [How to do distributed locking](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html), Martin Kleppmann, 2016, “Making the lock safe with fencing” | **Média-alta (argumento técnico):** lease expirado sem validação do token pelo recurso permite escrita obsoleta; checar geração sob guarda efetiva, não apenas relógio/TTL |
| E07 | [Bazel Skyframe — Incrementality](https://github.com/bazelbuild/bazel/blob/master/docs/reference/skyframe.mdx), Bazel, documentação no `master` consultada em 2026-11-20 | **Alta para o algoritmo descrito:** fecho reverso de dependências e change pruning distinguem atualização de input de alteração de resultado; o padrão de signatários é analogia, não API Bazel |
| E08 | [Build Systems à la Carte](https://doi.org/10.1145/3236774), A. Mokhov, N. Mitchell, S. Peyton Jones, ACM PACMPL/ICFP, 2018, ``2–4; [texto de autores](https://simon.peytonjones.org/build-systems-a-la-carte/) | **Alta (estudo acadêmico com código):** ordem de avaliação e condição de refazer são dimensões distintas; requer modelar seletividade e dependências. Não foi reproduzido benchmark no PAE |
| E09 | [Hypothesis — Stateful tests](https://hypothesis.readthedocs.io/en/latest/stateful.html), documentação Hypothesis 6.170.17 observada, `Rule-based state machines` / `Invariants` | **Alta (manual):** sequência de transições contra modelo-oráculo expõe bugs de estado. Uso opcional, condicionado às dependências instaladas, sem exigir biblioteca extra |
| E10 | [OWASP Path Traversal Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Path_Traversal_Prevention_Cheat_Sheet.html), OWASP, versão online s/d, “Validate the Resolved Path”, “Symbolic Links and Race Conditions”, “Windows Paths” | **Alta (orientação de segurança):** allowlist e contenção por componentes, evitar TOCTOU com symlinks e nomes reservados; conferir recursos disponíveis por plataforma |
| E11 | [AWS Builders' Library — Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/), Amazon, s/d, “Retries and semantic equivalence” | **Média-alta (relato de engenharia):** ID de operação torna retry seguro e auditável; é inspiração para reconciliar transição sem reabrir novamente |
| E12 | [Google Testing Blog — Just Say No to More End-to-End Tests](https://testing.googleblog.com/2015/04/just-say-no-to-more-end-to-end-tests.html), Google, abr. 2015, “Testing Pyramid” | **Média-alta (prática, não benchmark do PAE):** priorizar teste unitário + integração hermética ao invés de reiterar suites E2E caras |
| E13 | [Google Cloud's approach to change](https://docs.cloud.google.com/docs/cloud-approach-to-change), Google Cloud, documentação consultada em 2026-11-20, “Human code reviews validate changes and test results” | **Alta (processo documentado):** mudança relevante após review invalida a aprovação e exige revisão dos novos hashes |
| E14 | [Designing Data-Intensive Applications, 2nd ed.](https://www.oreilly.com/library/view/designing-data-intensive/9781098119058/), Martin Kleppmann e Chris Riccomini, O'Reilly, fev. 2026, índice: cap. 8 (“Transactions”), 9 (“The Trouble with Distributed Systems”) | **Alta para metadados e índice; limitada para conteúdo:** sumário editorial verificado, **livro integral não acessado**; recomenda áreas de estudo, não se atribui leitura do texto completo |
| E15 | [Jepsen Knossos](https://github.com/jepsen-io/knossos), Kyle Kingsbury, projeto open source, documentação atual, CAS register/linearizability | **Média (ferramenta com cautela declarada pelos autores):** modelo de histórico concorrente pode apoiar auditoria adicional, mas introduzir runtime Clojure só se demonstrada necessidade |

**Discrepâncias/versionamento:** o estudo preparado 016 descreve código baseline de 2026-10-28; a inspeção desta pesquisa é da branch 2026-11-20; APIs e hashes devem ser refeitos **depois** que 016 implementar. Documentação “master” e versão online não garantem comportamento do Python/FS/CLI instalado. Evidência externa estabelece semântica de mecanismos, não resultado específico nem economia medida.

## 4. Alternativas de arquitetura da revisão

| Estratégia | Vantagens | Riscos/custo | Decisão |
|---|---|---|---|
| Review textual do diff + rodar somente happy path | Barato e rápido | Não prova condições de corrida, crashes, falso signatário, segurança ou economia | **Rejeitar** como gate suficiente |
| Pedir a várias LLMs que gerem/revisem testes e executar toda a suíte a cada achado | Discussão abrangente em teoria | Alto gasto, repetição, falsa segurança, independência difícil de auditar | **Rejeitar** |
| Refazer tudo com SQLite transacional / registro distribuído antes de rever | Transação forte sob pressupostos conhecidos | Migração grande e fora de escopo, risco de incompatibilidade | **Adiar**; bloquear se JSON não puder cumprir invariantes |
| **Reviewer independente com snapshot de hashes + modelo-oráculo + fixtures de falha e concorrência + testes direcionados** | Evidência verificável, corrige apenas falhas reais, respeita escopo e custos | Requer boas fixtures, sincronização e regenerar revisão após correção | **Escolhida** |
| TLA+/Knossos para toda execução em múltiplos hosts | Pode analisar histórias complexas | Infraestrutura e especificação adicionais sem hipótese de distribuição confirmada | Opcional se surgirem anomalias inter-host |

## 5. Arquitetura **obrigatória de partida** para executar 017

### 5.1. Fronteira de revisão e cadeia de custódia

1. **Pré-condição dura:** 016 concluída **com receipt e outcome reais**, artefatos de fonte/teste presentes e aceites evidenciados; se faltarem, 017 permanece pendente. Conferir `TASK_INPUTS.json`, task 016/017 e manifest. Não executar review de código baseline e rotulá-lo como code review de 016.
2. **Congelar insumos:** coletar receipt/outcome 016, paths de `changed_artifacts` e `preserved_artifacts`, SHA-256 de cada fonte, testes e documentação em escopo, contratos 016, status/generation do plano; rejeitar referência inexistente ou hash que mudou. A revisão deve ser ancorada em **conteúdo**, não em nomes de arquivos ou mensagens de autor.
3. **Uma revisão independente real:** chamar `python docs/plans/20261028-skill-optimization/support/review_dispatch.py --repo-root . --task 017` em primeiro plano, como manda S002; código de saída 75 permite repetir a **mesma execução supervisada**, não simular sessão. O dispatcher exige predecessor entregue, usa reviewer novo/read-only, evidência `DISPATCH`, `FINDINGS`, `RECEIPT_REVIEWER` e hashes. Não reutilizar sessão, hash de despacho ou receipt de outra task. Respeitar rota `max` e a exceção `frontier` **somente** com falhas funcionais repetidas no max e evidência permitida; créditos esgotados não são argumento de escalonamento.
4. **Materializar findings compactos:** cada achado deve trazer `ID, severidade, path:line, invariant/AC violado, reproducer, correção mínima, risco residual`. Bloqueador = critical/high de correção, segurança, integridade ou AC. Achado sem evidência é hipótese a testar, não reprovação automática. Não reclassificar achado para aprovar artificialmente.
5. **Corrigir somente dentro do write_scope 017** e com regressão que falhe antes da correção. Se o problema exigir alteração fora do escopo ou dependência não entregue, registrar bloqueio e deixar 017 pendente; não editar componentes vizinhos silenciosamente. Preservar invariantes já satisfeitos sem “refatoração de fachada”.
6. **Rever o estado final:** após qualquer alteração em arquivo revisado, atualizar SHA-256, reexecutar checks e **redespachar revisão independente do novo conjunto**. A aprovação antiga não se transfere ao novo diff. Copiar do dispatcher campos autenticáveis do `RECEIPT_REVIEWER` para receipt 017 somente após prova de execução.
7. **Gate:** nenhum critical/high pendente; os ACs de 017 e todos os ACs de 016 comprovados no hash final; resultados, logs, limitações e reviewer/uso real registrados em `017-receipt.json` e `017-outcome.md`. Pare antes de concluir se ambiente/provider/testes estiverem indisponíveis.

### 5.2. Oráculo de contrato e modelo de estados a confrontar com a implementação

Modelo conceitual de dados — **adaptar ao schema e API existentes; não criar uma arquitetura paralela**:

~~~text
Pattern = (id estável, revision, semantic_digest, raw_digest?, contract_normativo,
           signatories, history, generation?)
Adoption = (task_id, pattern_id, adopted_revision, adopted_semantic_digest,
            evidence_hash, accepted_at?)
Mutation = (operation_id, expected_revision, expected_digest, owner_generation,
            proposed_digest, reason, phase)
WorkerAssignment = (task_id, {pattern_id: revision+digest}, delta_curto)
~~~

Invariantes verificáveis, inclusive em testes adversariais:

- **CAS real:** no momento de gravar sob a mesma guarda do lifecycle, exigir igualdade entre `expected_revision`, `expected_semantic_digest` e valores persistidos; stale writer recebe `conflict` e não altera registry, manifest, receipt ou projeções.
- **Semântica definida:** digest semântico de regras normativas, sem normalização que destrua escapes, ordem quando relevante, negações, nomes ou valores. Alteração meramente visual em Markdown projetado não reabre signatário; mudança ambígua **falha fechada** até revisão. Mudanças de `title`/`source_refs` exigem política explícita: não presumir que todas são normativas nem ignorar vínculo de requisito relevante.
- **Invalidação exata:** para padrão P cujo digest normativo mudou, `R = {t em signatories(P) | status(t)=completed e adopted_digest(t) != new_digest}`. Cada membro de R é reaberto **uma vez por operação** com motivo e evidência anterior arquivada; signatários pendentes e consumidores de outros padrões não mudam. `changed_by_task` não isenta automaticamente uma task concluída.
- **Adoção prova a revisão executada:** evidência do worker contém id+revision+digest do snapshot usado e hash/geração apropriados; um rename/edição entre prompt, validação, completion e `command_adopt` não assina o conteúdo novo sem verificação. `adopted_digest` concorda com revisão, não apenas com um inteiro.
- **Ownership e vida útil:** reutilizar `planctl.plan_writer_lock`/geração conforme 018/019 e o executor existente. Owner expirado/cancelado não escreve; token/generation deve ser validado no recurso de persistência. Não criar outro lock independente com ordem ambígua. Se storage distribuído não garantir fencing, declarar suporte restrito ao FS/host provado.
- **Crash consistency:** `os.replace` para uma projeção não torna transação multi-arquivo. Definir estado observável e um **registro de transição idempotente** (ou mecanismo já disponível) para fases `PREPARED -> REGISTRY_WRITTEN -> MANIFEST_UPDATED -> PROJECTIONS_UPDATED -> COMMITTED`; comparar geração e reconciliar antes de novo dispatch/summary. Se falha antes do ponto de confirmação, restaurar estado anterior com prova ou concluir a transição, jamais assumir sucesso. Não duplicar reset na retomada.
- **Path containment:** ID/slug seguro, resolved path dentro de `plan_dir`, rejeição de absoluto/`..`/UNC/drive/symlink externo, inclusive para `unlink` das projeções. Onde TOCTOU seja material, usar abertura ancorada no diretório ou controlar permissão de escrita dos diretórios; nunca interpolar conteúdo de contrato em shell.
- **Contexto mínimo:** entregar ao worker somente padrões atribuídos, digest/revisão atual e delta normativo curto. Histórico e audit trail ficam no artefato durável consultável sob demanda, não no prompt nem na projeção lida em todas as tarefas. Rotear hashing, CAS, validações e diff por código determinístico, **sem LLM**.

### 5.3. Fronteiras de módulos e responsabilidades da revisão

| Módulo | Responsabilidade/gate que o revisor verifica | Mudança permitida em 017? |
|---|---|---|
| `patternctl.py` | API de update/adopt/validate; schema, CAS, canonicalização, signatários, journal/reconciliação e path safety | Sim, se achado de 016 justificar |
| `pattern_runner_contract.py` | Pin de padrões por task, verificação antes/após execução, passagem de delta curto, adoção da revisão **realmente validada** | Sim |
| `test/optimization/shared_patterns_self_test.py` | Fixtures negativas/positivas, races, crashes, modelo-oráculo, prova de non-regression | Sim |
| `references/SHARED_PATTERNS.md` | Documentar protocolo aprovado, escolhas e limites (single host vs FS remoto, downgrade, migração) | Sim |
| `planctl.py` / `review_dispatch.py` / `SERVICE_MAP.md` | Reusar contratos e invocar validação; **não** refatorar ou mudar gate aqui sem autorização/ampliação formal | Não |
| `implementation/017-{receipt.json,outcome.md}` | Evidência de revisão, arquivos/hashes finais, ACs, logs e rota real | Sim, após revisão real |

**Migração:** schema prévio do registry é `schema_version=1`. Se 016 migrar campos, revisar leitura de planos antigos, valores ausentes, revision monotônica, inicialização, rewrite idempotente de projeções e comportamento sem padrões. Rejeitar corrupção em vez de “consertar” digests a partir de dados não confiáveis sem trilha de decisão. Não alterar configuração global, publicar a skill ou executar plano por causa desta pesquisa.

### 5.4. Economia de tokens e performance — medidas, não promessas

- Preparar pacote enxuto: receipts 016, hash do diff/arquivos em escopo, ACs e falhas reproduzíveis; evitar reler manifest de 1 MB, históricos e tarefas não atribuídas. Modelo forte/max **só** para a revisão independente de design/correção; fixtures, hashes, relatórios e decisões simples executados por scripts.
- No teste, comparar quantidade de bytes de contexto da atribuição com 0, 10, 100 e 1.000 revisões históricas; bytes entregues devem permanecer **constantes para mesmo contrato vigente/delta**; não necessariamente constante para contratos diferentes.
- Medir tempo p50/p95 de atualizar e validar registry com 2/20/200 padrões e 2/20/200 signatários (quando fixtures suportarem), total de arquivos reescritos, tasks reabertas, conflitos e reconciliações; escolher ganho de índice incremental somente após medição. Não usar contagem de tokens “economizados” nem preço como zero quando desconhecidos.
- Preferir tests Python locais, integração de runner e **duas** validações obrigatórias da task; não invocar E2E/browser sem cobertura adicional concreta. Debug de falha usa teste focal; ao final rodar checks declarados completos uma vez após cada rodada de correções.
- Benchmarks e contagem de falhas **não medidos nesta pesquisa**. Referências Bazel/Build Systems descrevem algoritmos, não taxas alcançadas por esta skill.

## 6. Matriz de testes futuros (risco e critério objetivo)

| Fixture/estímulo | Oráculo/expectativa objetiva |
|---|---|
| T01 Dois **processos** sob barreira leem mesma revisão/digest e tentam contratos diferentes | Exatamente um commit; outro conflito; nenhuma atualização perdida; histórico coerente |
| T02 Mesmo digest normativo, mudanças somente de layout permitidas | Nenhuma task reaberta; digest semântico estável; alteração auditável como cosmética |
| T03 Alterar ordem de regras não comutativas, negação, permissão ou termo de contrato | Digest semântico muda ou operação é bloqueada para exame; nunca classificação cosmética silenciosa |
| T04 Dois padrões A/B, signatários completos obsoletos, atuais e pendentes | Só `R(A)` reiniciado uma vez; B intocado; recibos antigos preservados; pendentes consomem A novo |
| T05 `changed_by_task` coincide com signatário concluído obsoleto | Não burlar invalidação nem aceitar signature stale |
| T06 Corrida entre assignment, execução do worker, completion, `adopt` e update concorrente | Adoção atrelada exatamente à revisão/digest validada ou recusa/retry sem aprovação falsa |
| T07 Injetar crash em **cada fase**: PREPARED, replace de registry, reset de manifest, projeções, COMMITTED; repetir recovery 2 vezes | Estado válido, sem writes externos, sem duplicar resets, sem recibo falso; dispatch não prossegue inconsistente |
| T08 Lock expirado, geração obsoleta, cancelamento em atualização, interrupção de processo | Escrita stale recusada, nenhum writer órfão confirma |
| T09 Path traversal: `../`, absoluto, symlink relativo/externo, slug adulterado, projection symlink, drive/UNC e colisões Windows | Não ler/escrever/apagar fora do workspace; falha segura, sem side effects |
| T10 Registry malformado, digest incompatível, adopted_digest adulterado, revisão em regressão, signatário duplicado | `validate` falha com erro localizado, sem upgrade silencioso nem estado marcado como completo |
| T11 Task só tem A; adicionar 100 padrões não assinados e histórico grande | Worker recebe apenas A atual/delta; não recebe B, registry completo ou histórico |
| T12 Revisor tenta reutilizar sessão/dispatch/receipt de outra task ou dos hashes anteriores após correção | Gate rejeita; novo review do estado final registrado |
| T13 Implantação sem patterns, plano schema anterior e APIs/CLI já existentes | Compatibilidade preservada, sem obrigar migração desnecessária |
| T14 Teste de mutação simples: desativar CAS, trocar digest, remover filtro de signatários ou desabilitar path check | Ao menos um teste direcionado falha para cada defeito; teste “verde” incapaz de detectar bug não serve |
| T15 Microbenchmark reproduzível com seed, sistema e tamanho registrados | Reportar p50/p95, prompt bytes e reopens falsos; não afirmar ganho antecipado |

**Plano de execução futuro:** testes unitários de canonicalização e seletores, integração hermética `patternctl`/`planctl`/runner sobre diretórios temporários, barreiras inter-processo e injeção de falhas nos seams existentes; property/stateful tests opcionais com Hypothesis **se já disponível**, caso contrário tabela determinística de sequências. Testes devem capturar log e seed. Evitar sleeps para sincronização e fixtures que dependam de LLM/rede.

**Comandos exatos, sem fingir execução:**

~~~bash
python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_017
python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_017
~~~

`TASK_INPUTS.json` declara: `python test/optimization/shared_patterns_self_test.py`, `python skill/plan-and-execute/scripts/pattern_self_test.py` e `python skill/plan-and-execute/scripts/pattern_runner_self_test.py`. A resolução do mapa deve comprovar execução; revisor registra limitações de plataforma e falhas sem as esconder.

## 7. Gates de aceite e política de severidade

- **AC017-1:** reviewer independente real do artefato 016, com fornecedor/modelo/esforço/sessão e hash dos insumos finalizados; não confundir estudo de arquitetura com reviewer.
- **AC017-2:** nenhum critical/high ativo; para cada achado bloqueante há reparo testado ou estado **pending/blocked** com motivo. Medium/low pode ser registrado com justificativa de risco.
- **AC017-3:** nenhuma reutilização fabricada ou entre tasks; mesmo dispatch só poderá ser retomado dentro de sua identidade e **mesmos hashes** conforme protocolo e sem ser falsamente contado como “nova sessão”.
- **AC017-4:** `frontier` apenas quando a política de erro funcional repetido no max estiver comprovada nos hashes; rate limit, auth, timeout e créditos são indisponibilidade, não incapacidade técnica.
- **AC017-5:** cobrir **todos os oito ACs da 016** (escrita concorrente, consumidor não afetado, signatário stale reaberto uma vez, path seguro, atribuição mínima, formato cosmético, mudança semântica com histórico, pesquisa não é prova). Testes, hashes finais, receipts e logs reais são exigidos.

**Critérios mensuráveis por teste:** 0 lost updates, 0 signatários não afetados reabertos, 0 signatários stale concluídos sem nova validação, 0 alterações fora do root em fixtures de ataque, 0 adoções com revisão divergente, 0 duplicações de reset em recovery, 0 critical/high sem solução no hash final. Para performance e custo, **registrar métricas reais**, não impor limites arbitrários de hardware.

## 8. Sequência de retomada, riscos e limites

1. Antes de qualquer execução de 017, exigir 016 concluída com recibos, obter hashes reais e verificar 019 (ownership) e versões materiais. Validar estrutura do plano e que o vínculo deste relatório ainda existe.
2. Usar a arquitetura 016 como **base do comportamento**, esta arquitetura 017 como **protocolo de avaliação independente**, e evidências runtime como autoridade do resultado. Revisar código de 016, não planejar nova implementação paralela.
3. Executar dispatcher e corrigir defeitos dentro do escopo; testar casos negativos e integrar após cada correção relevante. Revisor final deve rever o hash final; armazenar receipt.
4. Se incompatibilidade de esquema, bug em `planctl.py` fora do escopo, suporte a FS remoto não comprovado ou reviewer indisponível impedir aceite: parar e registrar bloqueio. Não ampliar privilégios, não simular sucesso.
5. Preservar estado original em qualquer retomada; não marcar conclusão de implementação aqui. Próxima **pesquisa** do guia, após comprovação desta, é 018 — lifecycle/leases/resume/cancel/reset/cleanup.

**Não executado/verificado nesta pesquisa:** nenhum teste Python, compilação do plano, review via provider, corrida de processos, benchmark de custo/latência, experimento Windows, conteúdo integral do livro O'Reilly ou validação de serviços autenticados. **Verificado:** definição/índice/manifest da branch, âncoras do código atual e documentação externa nas URLs da tabela.

**Decisão final:** a revisão 017 deve ser **independente, hash-bound, orientada por invariantes e falhas reproduzíveis, limitada a seu escopo e econômica em contexto**. Só a futura evidência da implementação 016 e da revisão 017 pode concluir a task.
