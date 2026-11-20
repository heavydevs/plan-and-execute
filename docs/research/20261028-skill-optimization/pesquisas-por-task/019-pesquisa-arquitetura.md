# 019 — Pesquisa e arquitetura para revisão independente do lifecycle

**Data da pesquisa:** 2026-11-20. **Task:** 019 — Review and correct leases, resume, cancellation, reset and guarded cleanup. **Natureza:** estudo prévio e arquitetura para futura revisão/correção; **não** revisão de código implementado, receipt de execução ou aprovação. **Estado do desenvolvimento:** 018 e 019 pendentes na consulta; os artefatos implementation/018-receipt.json e 018-outcome.md não existiam na branch na data da pesquisa. **Branch exclusiva:** checkpoint/plano1-estudo-provider-switch-20261028.

## 1. Escopo, dependências e proveniência

- [Definição da task 019](https://github.com/heavydevs/plan-and-execute/blob/checkpoint/plano1-estudo-provider-switch-20261028/.ai-work/20261028-skill-study-provider-switch/tasks/019-review-and-correct-leases-resume-cancellation-reset-and-guarded-.md), review_of=018; dependência dura: conclusão real da 018. Exige reviewer independente fresco, findings, correção de bloqueadores, checks e receipts. **S001–S006 permanecem pendentes até execução verdadeira.**
- [Definição da 018](https://github.com/heavydevs/plan-and-execute/blob/checkpoint/plano1-estudo-provider-switch-20261028/.ai-work/20261028-skill-study-provider-switch/tasks/018-implement-leases-resume-cancellation-reset-and-guarded-cleanup.md): oito critérios de aceite (ACs), implementação de processo identificado, fencing, retomada incerta, fingerprint escopado e cleanup seguro.
- [Decisão preparada de lifecycle, rev. 2](../../prepared-research/018-lifecycle.md) e [pesquisa/arquitetura individual 018](018-pesquisa-arquitetura.md) são **requisitos de design**, não provas de implementação, teste ou review. Usar ambas, sem duplicar seus textos. A revisão 019 se diferencia pela verificação independente da **implementação produzida** e por reproduções adversariais.
- [TASK_INPUTS.json](https://github.com/heavydevs/plan-and-execute/blob/checkpoint/plano1-estudo-provider-switch-20261028/docs/plans/20261028-skill-optimization/TASK_INPUTS.json), registro 019: read inputs da decisão, fontes, teste novo criado pela 018, 018-receipt/outcome e review_dispatch.py; write scope estrito: lifecyclectl.py, planctl.py, test/optimization/lifecycle_self_test.py e references/LIFECYCLE.md, além de 019-receipt/outcome. Não corrigir jobctl.py, process_tree.py, runner ou dispatcher por conta própria.
- [Manifest](https://github.com/heavydevs/plan-and-execute/blob/checkpoint/plano1-estudo-provider-switch-20261028/.ai-work/20261028-skill-study-provider-switch/manifest.json) e [TODO](https://github.com/heavydevs/plan-and-execute/blob/checkpoint/plano1-estudo-provider-switch-20261028/.ai-work/20261028-skill-study-provider-switch/TODO.md) são autoridades da **execução**. A checklist de pesquisa não modifica status, tentativas, etapas, hashes de execução ou conclusão.
- Artefatos esperados futuramente: docs/research/20261028-skill-optimization/implementation/019-receipt.json, 019-outcome.md, e evidências em implementation/reviews/019/. Não criar esses arquivos durante esta pesquisa.
- Evidência de baseline 2026-11-20: blob GitHub de lifecyclectl.py = 668155c98d14f0c51990b02ccdf4f5d82bfb857d; planctl.py = 0476fc7874d792b66523ae1def7ff0d1d1ad48cd; LIFECYCLE.md = 7dac16ce06741e23593738653b66501a09d549f6. São SHAs Git de blobs, **não** SHA-256 do conteúdo, nem prova de versão futura.

## 2. Questões arquiteturais e conclusões

| Pergunta de revisão | Contraprova necessária | Decisão |
|---|---|---|
| Um PID vivo autentica um runner? | Outro processo herdou PID, identidade de nascimento diferente; verificar sinalização sem atingir inocente | **Não**: verificar identidade estável e mesmo handle da ação; situação ambígua bloqueia |
| Nonce/TTL de lease garantem que apenas um runner conclua? | Runner A suspenso, B obtém epoch superior, A tenta publicar completion e liberar lease | **Não**: fencing no writer lock/ponto de publicação; stale owner não altera receipt/manifest |
| Uma queda sem receipt permite repetir trabalho? | Efeito externo ocorreu, resultado local desapareceu; replay repetiria gasto/mutação | Estado **uncertain** + reconciliação/idempotência comprovada; não repetir cegamente |
| os.replace publica todas as projeções? | Crash depois de manifest e antes de TODO/tasks Markdown | **Não**: manifest é autoridade; projeções reparáveis; distinguir durabilidade de substituição atômica |
| Um receipt antigo ainda prova validação? | Mudança só em arquivo estranho versus alteração em dependência/validação real | Verificar **uma** função validate_receipt, inputs reais e contrato transitivo; aprovação seletiva |
| É seguro cancelar/limpar uma árvore que mudou sob os pés? | Symlink/junction, sentinel falso, arquivo estranho, job lost, troca entre check e uso | No-follow/containment e posse antes de remover; **fail closed** sem suporte da plataforma |
| Qual evidência torna 019 uma revisão independente? | Reuso de sessão, review de hashes antigos ou findings genéricos | review_dispatch síncrono, readonly, roteamento max real, SHA de insumos, fresh reviewer e redespacho após correção |
| É necessário reescrever o orquestrador ou introduzir SQLite? | Contratos existentes satisfazem invariantes nos testes? | Reusar stdlib/locks/validador/dispatcher; mudança estrutural fora de 019 exige bloqueio documentado |

**Escolha:** revisão independente **ancorada em artefatos de implementação e hashes**, com modelo de estados, testes de concorrência/crash/segurança reproduzíveis, correção mínima no write scope, gates de receipt e re-review do estado final. A pesquisa não dá parecer de aprovado/reprovado sobre uma 018 que ainda não entregou código.

## 3. Evidências internas auditadas na branch

Os intervalos são de uma **leitura do baseline**, a localização pode mudar após 018. Instruir 019 a reencontrar símbolos por nome antes de julgar o diff.

| Arquivo / símbolo e linhas aproximadas | Comportamento observado | Risco/foco do reviewer 019 |
|---|---|---|
| lifecyclectl.py: pid_is_alive (285–324), lease_is_live (334–344) | Liveness local usa PID; remoto usa janela por created_at | PID reciclado, reboot/clock e owner remoto desconhecido; comparar processo **identificado**, não confundir alive com autorizado |
| lifecyclectl.py: acquire_lease/release_lease (347–389) | O_EXCL/nonce, unlink e troca podem ocorrer sem lock comum | Dois contenders, ABA, epoch monotônico, release tardio de A apagando B; revisar atomicidade de *sequência* |
| lifecyclectl.py: recover_interrupted_tasks (402–436) | Subtasks em andamento voltam a pending | Verificar efeito uncertain, checkpoints completed e nenhuma dupla execução sem idempotência |
| lifecyclectl.py: terminate_live_runner (466–503) | No POSIX há os.kill(PID) após verificação separada; remoto force retira lease | Identidade do alvo **na ação**, TOCTOU, SIGTERM/SIGKILL, own-host vs remote; force nunca elimina checagem de posse |
| lifecyclectl.py: stop_plan_jobs/remove_plan_workspace/cancel_workspace (506–606) | Para jobs registrados, então faz rmtree; há verificação de symlink/junction em parte da árvore | Containment integral, no-follow, stop-before-delete, salvaguarda de jobs lost e preservação de evidências |
| planctl.py: atomic_write_text e save_manifest (956–1014, 3226–3297) | replace por arquivo; manifest sob plan_writer_lock, depois TODO e tasks/*.md | Commit linearizável/fenced, lock reentrante/deadlock, crash em qualquer projeção |
| planctl.py: task_contract_digest e compute_task_contract_digests (2593–2658) | Digest normativo e dependências transitivas | Invalidação de receipt deve usar a fonte única, sem segundo hash de repositório inteiro |
| planctl.py: validate_receipt e observe_scoped_input_digests (2661–2880) | Contrato, inputs, AC e review; compara campos declarados | Conferir verificação **dos arquivos atuais**, fontes/teste/mapa/ambiente de fato usados, evitar reutilizar receipt stale |
| planctl.py: complete_task (aprox. 5995–6085) | Valida receipt, altera modelo e chama save_manifest posteriormente | Crítico: ação precisa de fence com o lock **na publicação**, inclusive se perder lease entre cálculo e replace |
| planctl.py: cleanup_plan (6377–6424) | Path + sentinel + job status, depois rmtree | Confrontar guardas de cancel/reset e cleanup, recusa de symlinks internos e FS sem proteção |
| jobctl.py: pid_identity e status_job (aprox. 124, 220–244) | Já há fonte de process-start identity e estado do supervisor | Reutilizar como contrato; código fora do write scope de 019 é **somente leitura** |
| lifecycle_self_test.py: testes de activate/recover/lease/cancel (151–380) | Happy paths e alguns casos negativos já cobertos | 019 não deve aceitar ausência de PID-reuse, dupla publicação, TOCTOU ou crash-fase por testes só de sucesso |
| review_dispatch.py: load_task/reviewed_inputs/build_brief/candidate_routes | Exige receipt/outcome do predecessor, prende SHA-256, lê somente alterações do predecessor + input extra, reviewer max, evidências de sessão | Gate **obrigatório**; não simular reviewer com a mesma sessão, relatório preparado ou prosa da IA |
| planctl.save_manifest, schema >= 4 | Re-renderiza TODO.md e cada tasks/*.md do manifest | Se o vínculo de pesquisa no arquivo da task desaparecer na execução, recuperá-lo via guia e relatório; não adulterar status/manifest nesta pesquisa |

Observação adicional: o baseline não é a implementação futura; diagnósticos da tabela são **hipóteses de regressão e razões para testes**, não findings de 019, pois 018 ainda não produziu o receipt/outcome. O documento preparado 018 foi produzido contra versão anterior e precisa de reaplicação aos hashes finais da 018.

## 4. Pesquisa externa — fontes examinadas e força de evidência

**Acesso às páginas:** 2026-11-20. s/d = sem data editorial visível. Confiabilidade “alta” significa fonte primária sobre seu **próprio** contrato/API, nunca prova do comportamento do PAE. Estudos de outros sistemas não são benchmarks locais.

| Ref. | Fonte, autoria/edição, versão/data e seção pertinente | Síntese crítica e consequência |
|---|---|---|
| E01 | [Google Engineering Practices — What to look for in a code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html), Google, s/d, Design/Functionality/Tests | **Alta (prática editorial):** revisão inspeciona design, edge cases, concorrência e se o teste realmente detecta defeito. É orientação, não efeito causal medido; fundamenta review separado |
| E02 | [Google — Building Secure & Reliable Systems, cap. 13](https://google.github.io/building-secure-and-reliable-systems/raw/ch13.html), Google/O'Reilly, 2020, When to Write Unit Tests | **Alta (livro disponível publicamente):** um teste que passa ao remover condição crítica é insuficiente; incluir mutações negativas simples antes da aprovação |
| E03 | [NIST SSDF PW.7](https://pages.nist.gov/nccoe-devsecops/appendix-c.html), NIST NCCoE, prática PW.7, conteúdo online consultado | **Alta para orientação de segurança:** revisão/análise do código devem checar vulnerabilidades e requisitos de segurança; importante para cleanup/process kill |
| E04 | [Hypothesis — Stateful tests](https://hypothesis.readthedocs.io/en/latest/stateful.html), Hypothesis, docs 6.170.17 observadas, Rule-based state machines/Invariants | **Alta (manual):** sequências e invariantes contra oráculo de estados; dependência **opcional**, pode substituir por tabela determinística stdlib |
| E05 | [CHESS: A Systematic Testing Tool for Concurrent Software](https://www.microsoft.com/en-us/research/publication/chess-a-systematic-testing-tool-for-concurrent-software/), Microsoft Research, artigo de 2007, resumo | **Média-alta (artigo acadêmico):** exploração controlada de interleavings encontra falhas que stress tests não reproduzem. **Não** integrar CHESS, apenas usar barreiras por processo e eventos |
| E06 | [Finding Crash-Consistency Bugs with Bounded Black-Box Crash Testing](https://www.usenix.org/conference/osdi18/presentation/mohan), Mohan et al., USENIX OSDI 2018, Abstract | **Alta (estudo empírico externo):** testes de crash limitados a pequenas operações foram produtivos em filesystems; não extrapolar a taxa de bugs do paper ao PAE. Motiva crash após cada write boundary |
| E07 | [How to do distributed locking](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html), M. Kleppmann, 2016, Making the lock safe with fencing | **Média-alta (análise técnica):** TTL/nonce sem checagem de epoch pelo recurso não impede escrita tardia. **Atenção:** lock local não prova consenso multi-host |
| E08 | [pidfd_send_signal(2)](https://man7.org/linux/man-pages/man2/pidfd_send_signal.2.html), Linux man-pages, DESCRIPTION/NOTES, versão online consultada | **Alta (API do SO):** pidfd estável evita sinalizar PID reutilizado; verificar capacidades Linux/Python instaladas |
| E09 | [os.pidfd_open e os.replace](https://docs.python.org/3.12/library/os.html), Python Software Foundation, Python 3.12.16, seções respectivas | **Alta (API):** pidfd Linux >= 5.3; replace atômico de uma entrada sob condições POSIX, nunca transação de vários arquivos |
| E10 | [Windows Process Handles and Identifiers](https://learn.microsoft.com/en-us/windows/desktop/procthread/process-handles-and-identifiers), Microsoft Learn, atualizado 2025-07-14 | **Alta (API):** HANDLE permanece referência ao mesmo processo; não confiar apenas em PID, usar handle validado |
| E11 | [GetProcessTimes](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getprocesstimes) e [TerminateProcess](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-terminateprocess), Microsoft Learn, docs consultadas, Parameters/Remarks | **Alta (APIs):** creation time pelo HANDLE, TerminateProcess exige HANDLE com PROCESS_TERMINATE e deve-se aguardar término; excluir risco de TOCTOU da tradução HANDLE->PID |
| E12 | [shutil.rmtree](https://docs.python.org/3.12/library/shutil.html#shutil.rmtree), Python 3.12.16, atributo rmtree.avoids_symlink_attacks e dir_fd | **Alta (API):** defesa contra symlink depende da plataforma; rmtree de nome previamente resolvido não garante sozinho ausência de race |
| E13 | [SQLite — Atomic Commit](https://www.sqlite.org/atomiccommit.html), SQLite, seção 5 Multi-file Commit, s/d | **Alta (documentação de design):** commit multiarquivo demanda coordenação/journals; prova negativa contra assumir que os.replace resolve tudo. SQLite não é requisito da task |
| E14 | [Temporal — Activity Definition](https://docs.temporal.io/activity-definition), Temporal, Idempotency/Activity retry policy, online | **Alta para contrato do Temporal:** activity pode executar/efeito parcialmente várias vezes embora conclusão registrada uma vez; fundamenta uncertain + reconciliação. Não requer Temporal |
| E15 | [AWS Builders' Library — Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/), Malcolm Featonby, Amazon, s/d, Client request ID/Semantic equivalence | **Média-alta (relato operacional):** idempotency key é contrato com serviço externo, não mero identificador aleatório local; replay só com garantia real |
| E16 | [Software Engineering at Google — Chapter 14, Larger Testing](https://abseil.io/resources/swe-book/html/ch14.html), Google/O'Reilly, 2020, diagnósticos de falha de teste | **Alta (livro disponível):** testes necessitam sinais claros, logs específicos e rastreáveis; justifica fixture com caso, hash e efeito observado |
| E17 | [Designing Data-Intensive Applications, 2ª ed.](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/), M. Kleppmann e C. Riccomini, O'Reilly, fevereiro 2026, sumário cap. 8–10 | **Alta para autoria/índice e baixa para conteúdo fechado:** capítulos de transações, falhas distribuídas e consenso delimitam leituras futuras; **livro completo não acessado** |
| E18 | [OWASP Path Traversal Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Path_Traversal_Prevention_Cheat_Sheet.html), OWASP, online s/d, resolved path/symlinks/races | **Alta (guia comunitário de segurança):** pathname resolvido uma vez não autoriza operação destrutiva futura; testar symlinks, junctions, containment e privilégio mínimo |
| E19 | [Google Engineering Practices — The Standard of Code Review](https://google.github.io/eng-practices/review/reviewer/standard.html), Google, s/d, Standard | **Média-alta (prática editorial):** bloquear por defeitos reais e risco, sem exigir refatorações cosméticas que ampliem escopo |

**Diferenças de versão e alcance:** documentação Python 3.12 é fixada para evitar depender implicitamente de APIs posteriores; Windows, Linux e macOS exigem provas próprias. O estudo 018 e fontes externas **não** comprovam segurança de NFS/SMB nem implementação de pidfd/handles na branch; 019 deve bloquear a alegação de segurança nessas plataformas se faltar teste. Os resultados de CHESS/CrashMonkey não foram reproduzidos no projeto. Testes de SO ausentes por ambiente não podem virar “pass”.

## 5. Alternativas arquiteturais para a revisão

| Opção | Vantagens | Falhas/limites | Decisão |
|---|---|---|---|
| A. Conferência textual do diff e apenas testes felizes | Rápida, baixo custo inicial | Não captura PID reuse, fencing tardio, crash, symlink, falsos receipts; não cumpre independência | **Rejeitada** |
| B. Reexecutar toda a suíte/E2E e pedir sucessivas opiniões de LLM | Alto volume de execução | Gasta créditos, reproduz testes já saudáveis e revisão pode não inspecionar invariantes | **Rejeitada** como estratégia padrão |
| C. Reimplementar como banco distribuído/Temporal antes do review | Operações com suporte transacional próprio | Migração de alto risco, fora do write scope e 018 ainda pendente | **Adiada**; necessidade vira bloqueio explícito |
| **D. Review independente hash-bound + oráculo de estados + fixtures de injeção e concorrência + reparos mínimos** | Produz contraprova, evidência auditável e custo controlado | Precisa controles de caso/review/versão corretos; depende de 018 real | **Adotada** |
| E. Model checking ou fault injection de SO em todas as plataformas | Pode explorar espaço maior | Infra, privilégios e custo desproporcionais para uma task; boa extensão condicionada a anomalias | **Opcional**, nunca substituir checks mínimos |

## 6. Arquitetura executável da **revisão futura** 019

### 6.1. Módulos e interfaces — reusar contratos existentes

1. **Entradas/ReadSet:** TASK_INPUTS.json[019], 018-receipt/outcome, fontes e teste efetivamente entregues pela 018, relatórios preparados 018 e este documento. Exigir paths, hashes e autorizações reais. Se faltar 018, **não disparar** o revisor nem presumir evidência.
2. **Review dispatch** (docs/plans/20261028-skill-optimization/support/review_dispatch.py, leitura/invocação, sem edição em 019): recebe --repo-root . --task 019; produz DISPATCH, findings, RECEIPT_REVIEWER com input hashes, provider/model/effort e sessão. Usa somente adaptador readonly e route max real. Exit 75 = execução pendente, repetir **o mesmo comando em foreground** para acompanhar a mesma execução, não criar outra. Nunca fabricar nome/ID de provider, review ou aprovação. Revisão “frontier” só com evidência formal de falha repetida de max e autorização/contrato existente.
3. **Oráculo de lifecycle** (futuro teste em test/optimization/lifecycle_self_test.py): modelo pequeno puro de OwnerIdentity, Lease(epoch, nonce), TaskStatus, AttemptEvidence e ReceiptEvidence. Não criar um segundo controlador de runtime para passar no teste; o modelo apenas calcula resultados esperados e invariantes após transições.
4. **Superfície de correções**: lifecyclectl.py (posse, sinais, retomada, cancelamento), planctl.py (save_manifest, complete_task, validate_receipt e cleanup), LIFECYCLE.md (contrato/limites), lifecycle_self_test.py (regressões). Reusar leitura de jobctl.pid_identity, process_tree, manifest e resource_watch; se a solução exigir mudar fora do write scope, **registrar blocker e manter 019 pendente**.
5. **Validador/observabilidade**: executar comandos declarados via resource_watch usando mapa .ai-work/SERVICE_MAP.md e IDs P1_TESTS_019 e P1_019, preservando stdout/stderr, logs, paths, elapsed, exit, source SHA e confirmação de que a validação apontou para os novos hashes. Nunca considerar código de teste isolado substituto dos checks declarados.
6. **Gate de evidência**: 019-receipt.json e 019-outcome.md somente após revisão real, correção e checks. 018-receipt é fonte histórica, não substitui receipt 019. Finalizações de task devem passar pelo validador e pelo fluxo de plano, não por edição manual de status.

### 6.2. Contratos/invariantes do reviewer

Modelo conceitual (adaptar ao schema produzido em 018, sem migrar em 019 apenas por estética):

~~~text
Owner = (plan_id, host_id, boot_id, pid, process_start_id, nonce, lease_epoch)
LeaseState = own_live | other_live | stale_proven | unknown
Attempt = (task_id, attempt_id, operation_id, effect_class,
           state: prepared|dispatched|confirmed|uncertain,
           reconciliation_evidence?)
Receipt = (task_id, contract_digest, scoped_inputs, dep_digests,
           validation_spec, validation_environment, producer_epoch,
           review_evidence?)
~~~

Invariantes observáveis que a implementação 018 precisa satisfazer **e 019 provar**:

- **I1 Processo:** igualdade do PID sem identidade de nascimento não autoriza liveness positiva para posse, kill, lease reclaim ou cleanup. No Linux, handle pidfd estável associado à identidade; no Windows, creation time e HANDLE da própria operação; se macOS/fallback não tiver ação segura demonstrável, bloquear gesto destrutivo.
- **I2 Fence:** epoch monotônico sem reset silencioso, nonce não repassado a worker; apenas owner atual publica dentro do mesmo lock/geração protegida. Stale runner A não publica após B, mesmo com receipt aparentemente válido. Verificar **no ponto de commit**, não só no início.
- **I3 Exclusão:** processos contendentes com lease stale/live/unknown resultam em no máximo um proprietário eficaz por plano; falha de lock, dados corrompidos e host remoto ambíguo exigem recusa segura. Sem garantia genérica de coordenação entre hosts.
- **I4 Retomada:** subtasks completed continuam completed; in_progress recebe transição explícita. Se efeito externo possivelmente ocorreu, somente operação idempotente **comprovada** ou reconciliação permite replay; uncertain não vira contagem de erro funcional do modelo.
- **I5 Atomicidade do estado:** manifest é autoridade única. Se falhar entre manifest, TODO.md e projeções tasks/, recuperação idempotente reconstrói projeções, sem inventar completion/validação. Não afirmar transação multiarquivo por os.replace.
- **I6 Receipt:** validador **único** de planctl reconhece contrato transitivo, fontes/validação realmente observadas, review status e hashes. Alteração fora do escopo não invalida; alteração causal invalida **com razão**. Receipt falsificado, antigo, de outra task ou de inputs stale é recusado.
- **I7 Exclusão de plano:** somente plan root com sentinel e path autorizado, sem escape por symlink/junction/UNC/drive; interromper runner/job **realmente identificado**, esperar estado terminal e preservar workspace se houver dúvida. Force não contorna I1/I3/I7. Source, testes, docs/research, logs externos e .ai-work/SERVICE_MAP.md permanecem intactos.
- **I8 Evidência e review:** cada finding grave inclui ID, severidade, path:line, invariante/AC, caso reproduzível e correção mínima. Depois de alterar qualquer arquivo/hash coberto, **reexecutar checks e redespachar** review do conjunto final. Reutilização de sessão ou aprovação de hash antigo não passa.

**Pontos de linearização:** aquisição e liberação de lease sob a mesma guarda da autoridade; publicação de resultado/receipt protegida por lease epoch + writer generation na seção crítica que faz persistência; remoção final só após nova verificação de owner e jobs. Separar esses check/acts configura TOCTOU. Caso 018 implemente diferente, 019 deve provar equivalência por testes, não impor nomes de classes sugeridos.

### 6.3. Sequência de trabalho 019, mapeada S001–S006

- **S001 — pré-condição e snapshot:** confirmar status real de 018=completed **com** receipt e outcome materiais, hashes de changed_artifacts/preserved_artifacts, source tree e requisitos; conferir hashes de implementação, comparação com arquitetura 018, planos e contratos da task 019. Caso não entregue, 019 não inicia. Salvar apenas resumo compacto de entradas e branch/revisão.
- **S002 — review independente:** invocar literalmente python docs/plans/20261028-skill-optimization/support/review_dispatch.py --repo-root . --task 019 em foreground. Em exit 75, esperar por reexecução do **mesmo** comando; sem sessão nova nem simulação. Registrar DISPATCH, findings, RECEIPT_REVIEWER; ler somente findings compactos para direcionar reparos. Erros 1/2/3/4 têm significado de falha/bloqueio, não aprovação.
- **S003 — triagem e correção:** mapear cada finding a I1–I8/ACs 018–019; casos críticos/altos exigem reproducer; para defeito validado, criar regressão que falha antes, corrigir minimamente nos quatro arquivos permitidos, revalidar os casos focais. Se achado exigir alteração fora do escopo, permissão nova, host sem provedor ou versão não suportada, documentar blocker sem elevar escopo silenciosamente.
- **S004 — pin final:** calcular SHA-256 de cada arquivo corrigido/preservado e das decisões; reobservar processo/receipt/contratos e redeclarar limitações. **Qualquer** mudança em reviewed input exige re-review do snapshot final; aprovação anterior não transfere.
- **S005 — validação supervisionada:** rodar ambos os comandos da task, por resource_watch: P1_TESTS_019 e P1_019. Corrigir isoladamente falhas localizadas, agregar inventário e reexecutar gates completos após rodada de reparos. Respeitar mapa de recursos, evitar testes em serviços pagos. Testes Linux/Windows/macOS devem declarar plataforma coberta; skip não equivale a sucesso multiplataforma.
- **S006 — evidência e decisão:** registrar source hashes, links de logs, matriz AC e decisão dos findings; exigir reviewer externo realmente autorizado, veredito approved sem critical/high, hashes do último dispatch iguais aos arquivos finais e receipt validado. Se qualquer pré-condição faltar, manter 019 pending com motivo verificável.

**Se 018 ainda estiver pendente** (estado observado durante esta pesquisa), somente preparar a documentação de 019; não executar S002, não criar reviewer artificial, não marcar S001–S006 ou development status.

## 7. Matriz de testes adversariais e critérios de aceite

Os fixtures **devem ser implementados na 018 ou corrigidos na 019**, não nesta pesquisa. Prefira subprocessos próprios, tmpdir e barreiras/Event (sem sleeps como único sincronizador), hashes observados, serviços externos falsos e logs determinísticos.

| Caso / AC relacionado | Estímulo | Resultado verificável (gate) |
|---|---|---|
| T01 / 018 AC01+AC06 | PID coincide mas process_start/boot divergem; processo inocente isolado | Nenhum sinal/kill; identidade rejeitada; arquivo de prova do inocente intacto |
| T02 / AC06 | Linux pidfd e Windows HANDLE: processo encerra após teste de identidade, antes do sinal | API estável não sinaliza o novo PID; handle de processo antigo não vira handle do novo |
| T03 / AC07 | A com epoch 9 para; B adquire epoch 10 e completa; A volta tentando completar | Publicação de A rejeitada **sob lock**; apenas B assina receipt/manifest |
| T04 / AC07 | A libera lease depois que B é dono, inclusive alternando nonce/epoch | Release de A não remove B; uma aquisição eficaz; erro de stale owner observável |
| T05 / AC02 | Crash após criação de lease, checkpoint de subtask e antes de dispatch | Retomada restaura somente em andamento; completed intacta; não fabrica receipt |
| T06 / AC02 | Crash após dispatch potencialmente mutante, antes de recibo local | Attempt unknown/uncertain; repetição bloqueada até consultar idempotency key/status do efeito |
| T07 / AC02 | Crash após manifest replace, antes de TODO e task projection, e após cada escrita | Manifest prevalece; projeções reparadas uma vez; nenhuma completion duplicada |
| T08 / AC02 | Repetir recovery 2x no mesmo estado após falha | Idempotente; history sem duplicar transições; contadores funcionais sem inflação |
| T09 / AC08 | Tocar fonte não declarada fora da DAG, manter hashes de inputs | Receipt continua válido; nenhuma reexecução de worker/model por ruído |
| T10 / AC08 | Editar dependência, comando de teste, AC, mapa ou versão relevante | Receipt invalidado com motivo preciso; recuperação exige nova validação |
| T11 / AC08 | Receipt adulterado: task_id errado, epoch velho, source/test SHA falso, review pending | validate_receipt recusa; nenhuma conclusão nova; histórico preservado |
| T12 / AC03 | Root symlink, sentinel faltante, .., UNC/drive, nome com prefixo coincidente e junction no Windows | Nenhum path externo removido; erro de containment com caminho seguro |
| T13 / AC03 | Troca de child path por symlink entre inspeção e rmtree; fallback sem fd safety | Falha fechada ou deleção restrita sem escape; sentinela externo intacto |
| T14 / AC04 | Job live, job lost, supervisor_start_failed e stop que falha, durante cancel/reset/cleanup | Não remove controle enquanto ownership/stop incerto; preserva logs e evidências |
| T15 / AC05 | Arquivos de produto, testes, docs/research, .ai-work/SERVICE_MAP.md e outro plano | Permanecem byte a byte iguais após cleanup/cancel/reset legítimo |
| T16 / compatibilidade | Lease schema v1, manifest schema 4, Windows/Linux/macOS capabilities declaradas | Migração segura dos estados comprovadamente mortos; desconhecido bloqueado; CLI/exit codes documentados |
| T17 / 019 AC01–AC04 | Reusar session_id/dispatch/RECEIPT_REVIEWER de outra task ou hashes antigos | Reviewer gate rejeita; após correção nova aprovação cobre hashes finais |
| T18 / qualidade | Mutação controlada em fence, process identity, path guard e receipt validator (uma por vez) | Ao menos um teste focal falha **para cada** proteção desligada; restaurar após teste |
| T19 / concorrência | Dois **processos** contendentes tentam lease e completion sob barreira | Um vencedor; nenhum update perdido, sem deadlock, sem orphan state |
| T20 / limites | NFS/SMB/FS não suportado, host remoto incerto, acesso negado ao processo | Capability/ownership_unknown e estado preservado; não alegar segurança não testada |

**Critério de aceitação mensurável para execução de 019:** (a) 018 entregue e validada; (b) 100% dos 8 critérios da 018 e 4 da 019 com evidências positivas/negativas suficientes, ou 019 **não** concluída; (c) zero critical/high pendente; (d) T01–T19 cobertos nos SOs aplicáveis, com T20 e skips explicitados; (e) todos os checks declarados passam no snapshot final; (f) nenhuma revisão aceita sem session_id novo/aceito, provider/model/effort reais e SHA-256 correspondente; (g) nenhum arquivo fora do escopo corrigido clandestinamente. Não converter testes não executados em “pass”.

## 8. Segurança, performance, compatibilidade e economia de tokens

- **Threat model:** JSON/Markdown editáveis por usuário local, conteúdo retornado de worker, race de arquivo, symlink/junction, processo alheio e sinais de supervisor, host remoto e filesystem compartilhado. Não considerar stdout do worker ou campo nonce como autorização. Dados de logs/sessão podem conter secrets: registrar hashes, caminhos e trechos mínimos, nunca credenciais, tokens ou prompts completos.
- **Segurança/privilegios:** processos de fixture próprios; nunca testar cancel em PID real fora de tmpdir; nenhuma API externa paga. PID fd/handle limitado por SO; suporte incerto = safe failure. O reviewer max roda em read-only pelo dispatcher, sem bandeiras perigosas e sem permissões de edição.
- **Performance:** checks de lifecycle devem ficar determinísticos. Coletar p50/p95 de status, acquire/release, recovery e validate_receipt com N=1/20/200 tasks e M=1/10/100 inputs pertinentes, em mesma máquina/filesystem, com baseline A/B e warm/cold declarados. Registrar nº de arquivos/hashes lidos, lock contention, replays evitados e bytes de logs; não criar limite arbitrário de tempo sem medição do baseline.
- **Tokens/créditos:** um pacote curto para o reviewer (receipt+outcome+hashes+ACs+findings), sem entregar manifest inteiro, históricos ou relatórios duplicados. Process checks, hashes, testes, comparação, triagem de exit code, reason code e reconciliação trivial feitos por código, não LLM. Model tier max em **uma** revisão independente material, repetida apenas se hashes mudarem; custo/uso nativo só reportado se medido.
- **Compatibilidade:** preservar comandos lifecycle e plano schema 4, contratos da 012 (validador único), 018 e resource watcher; não presumir equivalência Linux/Windows/macOS ou storage remoto. Versão real de Python, flags OS e FS devem ser capturadas no receipt. Mudança de API necessária fora do write scope = dependência bloqueadora, nunca edição tácita.
- **Revisão após correção:** hash e relatório anterior viram histórico; não reusar aprovação, resultado de teste sobre inputs anteriores nem evidência de outro provider/session. Findings médios/baixos com risco residual claro podem ser documentados se nenhum critical/high restar.

## 9. Dependências, riscos e lacunas para a execução

1. **Bloqueador atual:** a task 018 está pending e seus receipts de implementação ausentes. Não há código novo para 019 auditar; pesquisa é válida como preparação, implementação/review **não** começaram.
2. O relatório 018 recomenda solução exequível, porém a sua implementação pode mostrar limitações de lock/FS/processo e exigir decisão de compatibilidade. Atualizar somente incompatibilidade material, com reproducer e fonte; não repetir pesquisa ampla.
3. O review_dispatch só deve ser usado quando existir deliverable 018; sem provider disponível/credenciais/CLI ou recurso de segurança da plataforma, não fabricar sessão nem substituir por auto-review. Seguir protocolo de cooldown/pending e deixar gate incompleto.
4. planctl.save_manifest (schema 4) reescreve tasks/*.md: qualquer vínculo acrescentado diretamente no arquivo de task poderá desaparecer. Antes de claim/save, implementar deve ler este relatório a partir do guia; depois, verificar que o vínculo permanece acessível e preservar/reconstituir referência por mecanismo compatível, sem alterar manifest durante pesquisa.
5. Não há testes de benchmark do PAE nem demonstração de segurança de NFS/SMB executados aqui; hipótese de performance e economia **não medida**. Não instalar bibliotecas (Hypothesis, Temporal, SQLite, CHESS) sem necessidade e decisão própria.
6. Se o contrato aceito exigir alteração de jobctl.py, process_tree.py, review_dispatch.py, manifest de tarefas ou da configuração global, a 019 **não** deve se autoautorizar: registrar finding bloqueador e depender da autorização/etapa correspondente.
7. Esta pesquisa usou leitura de arquivos via GitHub conectado e fontes públicas; sem clone local, portanto **não** executou planctl validate, testes Python, provedor independente ou fuzzing. Isso não altera o gate futuro da 019.

## 10. Checklist de auditoria desta pesquisa (separada dos checkpoints da task)

- [x] Identificada primeira pesquisa pendente como 019 e verificada sua dependência 018.
- [x] Consultados task, TASK_INPUTS, baseline de lifecycle/planctl, guia, prepared research e relatório 018.
- [x] Confrontadas fontes oficiais, livros disponíveis, literatura acadêmica e alternativas; riscos e limites descritos.
- [x] Definido **procedimento verificável** de revisão independente, modelo de invariantes, testes e gate de evidência, sem executar desenvolvimento.
- [ ] **Não marcar como feito aqui:** reviewer real de 019, alterações de implementação, testes de 018/019, receipt/outcome e status development — todos dependem de execução futura.

**Regra de execução:** 019 deve usar **este relatório como arquitetura aprovada de partida** para S001–S006, junto com 018-lifecycle.md e 018-pesquisa-arquitetura.md, verificando apenas divergências materiais. Não substitui review_dispatch.py, nem validação declarada, nem comprovante de código implementado.
