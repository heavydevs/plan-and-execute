# Task 016 — Pesquisa, decisões e arquitetura de contratos compartilhados versionados

**Levantamento:** 2026-11-20. **Estado:** arquitetura antecipada; código, reviewer 017 e testes ainda não executados por esta pesquisa. **Branch:** `checkpoint/plano1-estudo-provider-switch-20261028`.

## Objetivo e rastreabilidade

- Task: [016](../../../../.ai-work/20261028-skill-study-provider-switch/tasks/016-implement-versioned-shared-contracts-and-selective-invalidation.md). Revisão futura: 017. Dependências declaradas: 001, 015 e 019; **estudo antecipado não satisfaz essas dependências**.
- Pesquisa existente: [016-shared-patterns.md](../prepared-research/016-shared-patterns.md); índice e evidência: [INDEX.md](../prepared-research/INDEX.md) e [SOURCE_REGISTER.md](../prepared-research/SOURCE_REGISTER.md).
- Escopo de implementação: `skill/plan-and-execute/scripts/patternctl.py`, `pattern_runner_contract.py`, `references/SHARED_PATTERNS.md`, `test/optimization/shared_patterns_self_test.py` e receipts 016. Os nomes são os arquivos da task; **verificar código e APIs efetivos no checkout antes de escrever**.

## Questões e conclusões arquiteturais

1. **Como evitar overwrite concorrente?** Uso obrigatório de revisão/digest canônico esperado (compare-and-swap), mais serialização do escritor dentro da mesma disciplina de lease/ownership do ciclo de vida. Um rename atômico sozinho não implementa CAS.
2. **Como distinguir semântica de formatação?** Duas representações: documento original para humanos e contrato **normativo canônico** para fingerprint. Mudança somente em comentários/whitespace não altera digest normativo e não reabre tarefas. Ambiguidade na interpretação do contrato impede classificação automática como formato.
3. **Quem deve reabrir após revisão normativa?** Apenas signatários completos cuja revisão adotada difere da atual; pendentes consomem a versão atual sem reabertura; tarefas não relacionadas permanecem estáveis. Evitar cascata e duplicação em callbacks concorrentes.
4. **O que o worker recebe?** Conjunto atribuído de IDs de contrato em revisão atual com delta normativo limitado; nunca registro inteiro, histórico amplo ou padrões sem consumidor.
5. **Que operação é transacional?** Atualização do próprio arquivo sob lease e CAS pode ter atomicidade pontual; atualização conjunta de registry, manifest e recibos exige geração + reconciliação idempotente. Não declarar atomicidade multi-arquivo por causa de `os.replace`.

## Evidências internas e efeito na implementação

| Evidência | Fonte observada na definição e relatório preparado | Efeito |
|---|---|---|
| I01 | `patternctl.py` possui revisões e signatários segundo [relatório 016](../prepared-research/016-shared-patterns.md) | Evoluir mecanismo existente, não instalar outro registry |
| I02 | `pattern_runner_contract.py` integra os contratos na execução | Filtrar exatamente por `task_id`, `pattern_id` e revisão canônica |
| I03 | `SHARED_PATTERNS.md` define contratos normativos, distintos de learnings | Registrar explicitamente semântica, evidência e contrato de mutação |
| I04 | Task 016 exige dois writers, invalidation seletiva, path seguro e revisão de formatação | Construir casos negativos sem depender de LLM |
| I05 | Task 018/019 é responsável pela disciplina de lifecycle/lease | Reutilizar API do ownership existente, integrar só após 019 — não criar lock concorrente incompatível |

Estas são observações da especificação e do estudo antigo. Nenhum resultado de teste atual ou hash do código foi apresentado como verificado.

## Fontes externas consultadas em 2026-11-20

| ID | Fonte (URL, autor/data/versão) e seção | Achado relevante | Inferência aplicada |
|---|---|---|---|
| E01 | Kubernetes, [API Concepts — Resource Versions](https://kubernetes.io/docs/reference/using-api/api-concepts/), documentação oficial consultada 2026-11-20 | `resourceVersion` identifica versões e impõe atenção a concorrência/freshness | Conceito de atualização condicional; **não** exige API Kubernetes nem etcd |
| E02 | Git, [git-update-ref](https://git-scm.com/docs/git-update-ref.html), manual oficial acessado 2026-11-20, *DESCRIPTION* e modo `--stdin` | O valor antigo pode ser validado antes de atualizar; lock transacional protege refs, embora leitores possam observar atualizações parciais | CAS explícito com expectativa; tratar visibilidade conjunta separadamente |
| E03 | Python Software Foundation, [os.replace](https://docs.python.org/3/library/os.html#os.replace), manual Python, consultado 2026-11-20 | A substituição é atômica ao ter sucesso nas plataformas/FS suportados; não garante atomicidade de múltiplos arquivos nem cross-filesystem | Usar temporário no mesmo diretório, fsync/durable recovery quando aplicável; implementar testes de crash |
| E04 | SQLite, [Atomic Commit in SQLite](https://www.sqlite.org/atomiccommit.html), documentação oficial, seções 1, 5, 9, consultada 2026-11-20 | Atomicidade sob falhas exige protocolo de journal, locks e pressupostos do FS | Não prometer transação de múltiplos JSON; usar fases e repair idempotente |
| E05 | Unmesh Joshi, [Version Vector](https://martinfowler.com/articles/patterns-of-distributed-systems/version-vector.html), *Patterns of Distributed Systems*, 23 nov. 2023, consultado 2026-11-20 | Vetor de versões resolve concorrência entre réplicas independentes | Para registry local single-owner, revisão monotônica/digest é mais simples que vetor; adiar CRDT/vector clock |
| E06 | Anthropic, [Effective context engineering for AI agents](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents), 29 set. 2025, consultado 2026-11-20 | Contexto sob demanda com ponteiros limita ruído e obsolescência | Enviar só contratos atuais necessários e deltas restritos |

A literatura acima suporta **mecanismos**, não benchmarks medidos neste repositório. Nenhum livro restrito, acesso pago, corrida de escritores real ou suíte cross-platform foi executada.

## Alternativas comparadas

| Alternativa | Prós | Contras | Decisão |
|---|---|---|---|
| Copiar padrões em todos os TODOs | Fácil leitura isolada | Drift, tokens duplicados, invalidação indiscriminada | Rejeitar |
| Registry completo em todos os prompts | Sem busca por ID | Ruído, histórico ilimitado e leakage de dados | Rejeitar |
| Registry local canônico com CAS + lease do lifecycle + signatários | Simples, testável, seletivo, compatível | Exige política rigorosa de digest e crash recovery | **Adotar** |
| SQLite transacional para todos os estados | Boa semântica de commit | Migração ampla do estado existente, locking/custo adicional | Não adotar neste incremento |
| Distributed schema registry/CRDT | Resolvem sistemas multiwriter distribuídos | Nova infraestrutura e sem necessidade provada | Adiar |

## Arquitetura de implementação (ponto de partida obrigatório)

### Modelo de dados lógico e fronteiras

Usar `pattern_id` estável e normalizado (sem `..`, diretórios, symlinks externos ou separadores não previstos); `revision` monotônica; `semantic_digest = sha256(canonical_normative_contract)`; `raw_digest` para auditoria de formatação; `signatories: { task_id -> adopted_semantic_digest }`; `generation` do owner; `change_reason` e `delta` curto. Validar a schema real antes de migrar ou adicionar campos.

Duas revisões com mesmo digest semântico e diferente digest bruto não exigem reimplementação. A canonicalização só deve remover **aspectos explicitamente não normativos** (por exemplo, o invólucro de formatação), preservando ordem de regras quando afetar semântica, escapes, casing de IDs e valores. Reordering de cláusulas não comutativas deve mudar digest ou ser classificado como **revisão semântica**; um classificador LLM pode sugerir, nunca autorizar sozinho uma não invalidação.

```text
patternctl (read current + expected semantic digest)
  -> normalize/validate path & contract
  -> acquire existing lifecycle owner / generation lease
  -> compare actual expected digest/revision under same lock
       mismatch => conflict (no mutation)
  -> classify formatting vs normative delta (deterministic + review gate for ambiguity)
  -> write temp + flush + atomic replace one registry file
  -> persist reconciliation/transition record (idempotent)
  -> for completed signatories with stale digest: reopen exactly once, keep prior receipt
  -> release owned lease
pattern_runner_contract -> resolve assigned pattern ids -> deliver current minimal contracts
```

### APIs propostas (adaptar às APIs já existentes)

- `read_pattern(pattern_id, plan_generation) -> PatternSnapshot`: retorno imutável, rejeita paths fora do root.
- `update_pattern(pattern_id, expected_revision, expected_semantic_digest, updated_content, owner_generation) -> UpdateResult`: retorna `conflict`, `formatting_only` ou `semantic_change`, nunca last-writer-wins.
- `affected_signatories(pattern_id, new_digest) -> list[task_id]`: somente completos com digest antigo; dedupe com reason e generation.
- `context_for_worker(task_id) -> list[PatternSnapshot]`: apenas padrões atribuídos e atualizados, delta breve, sem incluir histórico.
- `reconcile_pattern_mutation(generation) -> TransitionReceipt`: reexecução segura após crash/restart para concluir invalidação sem voltar a abrir um task já reaberto.

Não introduzir essas funções se APIs existentes expressarem o contrato; os nomes servem como interface testável, não exigência de refactor.

### Confiabilidade e segurança

Um owner/revision por mutação; validar sob lock; nunca confiar apenas no digest recebido do worker. Ao reiniciar, identificar transições preparadas, comparar gerações e completar ou reverter com provas; impedir fechamento do lease enquanto o estado puder ficar inconsistente. Reabrir task afeta apenas status do signatário, preservando histórico/receipts. Bloquear symlinks e path traversal **antes** de abrir arquivos. Strings de padrões são dados de contrato, não instruções autorizadoras de shell ou alteração de provider. Não permitir que revisão cosmética invalide task concluída.

### Economia e performance

Leitura por índice `pattern_id`; custo esperado proporcional a contratos atribuídos e signatários afetados, não ao número total de tasks nem ao histórico. Sem chamadas a modelos para CAS, diff de JSON, hashing e invalidation. Para ambiguidade genuína de semântica, route para revisão forte com evidência curta. Medir bytes de contexto, latência de lock, número de tasks reabertas sem necessidade, conflitos reais, retries e falhas de aceite; sem afirmar ganho de tokens antes dos ensaios.

## Testes, fixtures e critérios verificáveis

| Caso | Estímulo | Resultado exigido |
|---|---|---|
| Conflito CAS | Dois writers partem do mesmo digest | Um sucesso; o outro recebe conflict sem sobrescrever |
| Edits cosméticos | Mudança whitespace/comentário declaradamente não normativo | `semantic_digest` igual; nenhum signatário reaberto |
| Mudança normativa | Alteração de permissão/assinatura em contrato A | Apenas signatários completos antigos de A são reabertos uma vez |
| Isolamento | Alteração de A com task consumidora apenas de B | B permanece concluída |
| Estado anterior | Signatário completou em digest X e está no manifest | Invalidação mantém histórico e motivo |
| Paths perigosos | `../`, absoluto, link externo, ID inválido | Erro sem ler, gravar ou apagar fora do root |
| Crash no commit | Interrupção após arquivo mudar antes de atualizar manifest | Reconciliação idempotente, sem falso estado final |
| Mudança de owner | Worker antigo tenta commit após lease expirar | Rejeita geração obsoleta |
| Contexto do worker | Task recebe apenas padrões A e C | Nenhum B, histórico total ou log externo no prompt |
| Ambiguidade | Alterar ordem de regras onde ordem importa | Classificar como normativo/bloquear, nunca otimizar como cosmeticamente equivalente |

Rodar os comandos declarados **sem atalhos**:
`python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_016` e `... --validation P1_016`. Executar em especial testes `test/optimization/shared_patterns_self_test.py` conforme map, e preservar logs. Revisor independente 017 é gate obrigatório posterior.

## Riscos, dependências e critérios de pronto

- **Dependência 019**: não implementar integração de lock até a revisão de ciclo de vida estar aceita; o estudo antecipado não libera a implementação.
- **Risco semântico**: canonicalização agressiva pode esconder mudança funcional; exigir casos de ordem, campos opcionais, nomes e política.
- **Risco de crash**: atomicidade de arquivo único não equivale a atualização atômica do manifest; especificar estados de reconciliação.
- **Risco de token economy**: limitar histórico sem omitir contrato vigente/aceito.
- **Aceite da pesquisa**: escolhas, evidências, matriz de implementação e testes registrados com vínculo na task; **não** marcar 016 como implementada, aprovada ou revisada.

Este relatório é a arquitetura de partida para a task 016. Antes do código, conferir se a baseline foi alterada desde o estudo, ajustar interfaces ao código vigente e validar a cadeia de ownership determinada por 018/019.
