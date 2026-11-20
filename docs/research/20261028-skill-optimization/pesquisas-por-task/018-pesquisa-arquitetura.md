# 018 — Pesquisa técnica e arquitetura de leases, retomada, cancelamento, reset e limpeza protegida

> **Pesquisa e arquitetura de referência — 2026-11-20 (UTC-3).** Implementação 018: **PENDENTE**; revisão independente 019: **PENDENTE**. Este documento não é receipt de implementação, teste, benchmark ou revisão. Âmbito: uma única task, sem alterações no código. Fontes públicas consultadas em 2026-11-20, salvo a base histórica identificada.

## 1. Identidade, contratos e ordem real

- **Task oficial:** [018 — definição de implementação](../../../../.ai-work/20261028-skill-study-provider-switch/tasks/018-implement-leases-resume-cancellation-reset-and-guarded-cleanup.md). Este link relativo pode ser resolvido a partir da raiz como [.ai-work/.../018](https://github.com/heavydevs/plan-and-execute/blob/checkpoint/plano1-estudo-provider-switch-20261028/.ai-work/20261028-skill-study-provider-switch/tasks/018-implement-leases-resume-cancellation-reset-and-guarded-cleanup.md).
- **Plano e estado autoritativo:** [.ai-work/20261028-skill-study-provider-switch/manifest.json](https://github.com/heavydevs/plan-and-execute/blob/checkpoint/plano1-estudo-provider-switch-20261028/.ai-work/20261028-skill-study-provider-switch/manifest.json), schema 4; a pesquisa observou 018 como pending. Pesquisa não muda status, subtasks ou recibos.
- **Contrato de escopo e checks:** [docs/plans/20261028-skill-optimization/TASK_INPUTS.json](https://github.com/heavydevs/plan-and-execute/blob/checkpoint/plano1-estudo-provider-switch-20261028/docs/plans/20261028-skill-optimization/TASK_INPUTS.json), entrada 018 (F007, revisão de pesquisa 2, AC01–AC08).
- **Base obrigatória de partida:** [prepared-research/018-lifecycle.md](../prepared-research/018-lifecycle.md) e [018-lifecycle.json](../prepared-research/018-lifecycle.json), preparados em 2026-10-28. Eles recomendam lease com fencing, estado de execução incerta e digest escopado; não provam a implementação.
- **Dependências declaradas de 018:** 001, 013 e 015; 019 é a revisão futura de 018. O manifest consultado também declara dependência 016 → 019: a ordem de **implementação** deve seguir o DAG, mesmo que a ordem de **pesquisa** do guia tenha passado por 016 e 017 primeiro. Não alterar essas dependências nesta pesquisa.
- **Escopo de escrita futuro permitido por TASK_INPUTS:** skill/plan-and-execute/scripts/lifecyclectl.py; skill/plan-and-execute/scripts/planctl.py; test/optimization/lifecycle_self_test.py; skill/plan-and-execute/references/LIFECYCLE.md. A task também exige receipts/outcomes reais em docs/research/20261028-skill-optimization/implementation/. Outras dependências existentes devem ser **reutilizadas**, não alteradas silenciosamente.
- **Limite explícito:** não migrar para orquestrador distribuído, não criar segundo plano, não modificar instalações globais, jobctl.py ou process_tree.py fora do escopo sem tratar um bloqueio de dependência e autorização. A ausência atual de test/optimization/lifecycle_self_test.py é esperada; somente a implementação a criará.

## 2. Perguntas arquiteturais e decisão sintética

| Pergunta que pode mudar a solução | Evidência/contraprova | Decisão para 018 |
|---|---|---|
| PID vivo prova posse? | Não: reutilização de PID e pausa do controlador; E01–E04 | Identidade do processo + nonce + geração monotônica, sob exclusão efetiva; PID sozinho nunca autoriza matar ou escrever |
| Lease com TTL/nonce basta? | Não: escritor antigo pode voltar após perda de posse; E08 | Fencing no **ponto de commit** do manifest/receipt; somente conferir antes de executar é insuficiente |
| Queda após efeito externo permite retry direto? | Não: pode ter efeito confirmado no serviço e nenhum receipt local; E09–E11 | Registro persistente da intenção e resultado; fase **incerta** bloqueia reexecução não idempotente até reconciliação |
| Um os.replace publica manifest, TODO e task Markdown juntos? | Não: troca atômica de **um arquivo** não é transação de vários arquivos; E05, E12 | Manifest é autoridade; projeções derivadas e reparáveis; serialização/fencing no writer |
| Como preservar receipt anterior? | planctl já calcula digest transicional e contém validate_receipt; E13 | Estender a função autoritativa de 012 usando entrada/dependências reais; nunca criar segundo validador divergente |
| Como cancelar/limpar sem apagar produto ou atingir outro processo? | Código atual mistura verificações e rmtree; E06–E07 | Escopo exato de plan root, sentinel, no-follow e stop-before-delete; erro de posse bloqueia limpeza |
| Precisa de banco/consenso/novas libs? | O caso declarado é local e tem lock/generation; E08, E12, E14 | Evolução pequena da biblioteca padrão, sem SQLite/Temporal por padrão; migrar somente diante de requisito distribuído comprovado |
| Como diminuir créditos/tokens? | Retomar checkpoints comprovados e avaliar só entradas relevantes; E13–E14 | Verificações determinísticas, nenhuma LLM para status e diagnóstico trivial, reuso condicional de receipt, sem replay cego |

**Decisão escolhida:** um **controlador local com lease identificável e epoch monotônico, fencing de conclusão, protocolo de efeitos incertos, receipt escopado e limpeza fail-closed**. Manter contrato público atual quando seguro; tornar ambiguidades explícitas em vez de mascará-las com --force.

## 3. Evidências internas inspecionadas, 2026-11-20

Leitura da branch alvo pelos blobs GitHub; os números são **linhas observadas nesta revisão**, não promessas de estabilidade futura. Cada entrada aponta o risco ou a infraestrutura a reaproveitar.

| Âncora do código | Observação verificada | Consequência para 018 |
|---|---|---|
| lifecyclectl.py:285–324, pid_is_alive e _windows_pid_is_alive | Consulta PID com os.kill(pid,0), /proc ou GetExitCodeProcess; distingue zombie no Linux, mas não comprova o nascimento do processo | Substituir a autorização por identidade de processo real; separar teste de liveness de autorização para ação |
| lifecyclectl.py:334–344, lease_is_live | Host + PID local; remoto usa idade de até 24 h, sem verificação de start time ou boot | Classificar live / stale verificado / ownership_unknown, não reduzir desconhecido a morto |
| lifecyclectl.py:347–389, acquire_lease / release_lease | O_EXCL, nonce e fsync do arquivo; remoção/checagem do lease em operações separadas; --force pode suplantar dono vivo | CAS de posse e serialização com lock, epoch durável; release apenas se token completo ainda coincide |
| lifecyclectl.py:402–436, recover_interrupted_tasks | Retorna task/subtask in_progress a pending sem lançar falha técnica; não verifica efeito externo incerto | Recuperar checkpoints comprovados; bloquear repetição arriscada, com razão de reconciliação |
| lifecyclectl.py:466–503, terminate_live_runner | os.kill por PID após checagem, com SIGTERM/SIGKILL; --force remoto apaga registro | Evitar kill por PID reciclado; não revogar remoto desconhecido automaticamente |
| lifecyclectl.py:506–606, stop_plan_jobs, remove_plan_workspace, cancel_workspace | stop_plan_jobs usa jobctl e preserva quando status lost; remove_plan_workspace usa shutil.rmtree após load_plan | Preservar stop-before-delete, reforçar verificação de sentinel, containment e entradas symlink/junction |
| lifecyclectl.py:610–634, resume_workspace | Chama run_concise.py para executar plano, não tenta reconstruir conversa antiga | Retomada a partir de armazenamento, sem recarregar plano integral em LLM |
| jobctl.py:124 e :220–244, pid_identity / status_job | Já existe identidade de nascimento de processo e correlação nonce do job | **Reusar** o mecanismo sem criar uma nova dependência nem alterar jobctl fora do escopo |
| planctl.py:956–1014 e :1212, atomic_write_text/json, plan_writer_lock | Escrita atômica por arquivo e lock para writer | Compartilhar essa exclusão para autorização do commit; resolver reentrância para não criar deadlock |
| planctl.py:2593–2658, task_contract_digest e compute_task_contract_digests | Já há hashes de contrato e dependências transitivas no DAG | **Não inventar** hash global e nem segundo algoritmo semântico |
| planctl.py:2661–2807, register_receipt_validator / validate_receipt | Uma função autoritativa valida digests, inputs, ACs, checks e review status | Estender nesse ponto, com observação de hashes atuais; evitar validar apenas o valor declarado desatualizado |
| planctl.py:2809–2880, build_task_receipt / observe_scoped_input_digests | Receipt já contém generation e scoped_input_digests; calcula hash real do arquivo e compatibilidade CRLF | Registrar/validar ambiente e fontes de teste necessárias sem invalidar por arquivos alheios |
| planctl.py:3226–3297, save_manifest | Guardado por plan_writer_lock, compara generation; grava manifest, depois TODO e **regenera todos os tasks/*.md** | O vínculo obrigatório escrito nesta task pode ser sobrescrito na execução futura. Implementador deve ler este relatório **antes** de um save/claim, e verificar preservação ou restaurar vínculo com técnica compatível com a projeção |
| planctl.py:5995–6085, complete_task | Valida receipt e marca task como completa; não recebe necessariamente uma prova de lease presente sob o mesmo lock de persistência | Fencing no último ponto de publicação; não basta ter nonce salvo no início |
| planctl.py:6279–6350, reset_task | Arquiva receipt e desfaz checkpoints da task por operação explícita | Separar reset controlado de recovery por crash; preservar histórico e não apagar arquivos de produto |
| planctl.py:6377–6424, cleanup_plan | Valida path esperado, sentinel e jobs; a remoção ainda é recursiva | Unificar guarda de limpeza com o fluxo de cancelamento, incluindo componentes aninhados e prova de ausência de processo vivo |
| lifecycle_self_test.py:151–380 | Testa ativação, stale lock, cancelamento, reset, liveness, jobs, mas não demonstra PID reciclado ou crash em toda borda de escrita | Criar fixtures adversariais no novo test/optimization/lifecycle_self_test.py e regressões direcionadas |

**Verificação interna adicional:** o manifest observado era schema 4, 14 tarefas completed e 118 pending; 018 continua pending. O source SHA do blob de lifecyclectl.py foi 668155c98d14f0c51990b02ccdf4f5d82bfb857d e de planctl.py foi 0476fc7874d792b66523ae1def7ff0d1d1ad48cd. A base preparada descreve o baseline de outubro; toda divergência com o código de novembro tem precedência na fase de implementação.

## 4. Pesquisa externa: fontes, alcance, confiabilidade e efeito

**Data de acesso das URLs: 2026-11-20.** Páginas sem data editorial exibida: s/d. As fontes foram usadas para validar **mecanismos** e riscos, não para atribuir latência, redução de crédito ou garantia de exactly-once ao projeto.

| ID | Fonte verificável, seção e data/versão | Confiança, limite e consequência |
|---|---|---|
| E01 | [pidfd_send_signal(2)](https://man7.org/linux/man-pages/man2/pidfd_send_signal.2.html), Linux man-pages / Michael Kerrisk, manual consultado 2026-11-20, DESCRIPTION | **Alta (interface kernel):** pidfd estável evita matar PID reciclado; Linux apenas, não autoriza assumir suporte universal |
| E02 | [pidfd_open(2)](https://man7.org/linux/man-pages/man2/pidfd_open.2.html), Linux man-pages, DESCRIPTION e NOTES, s/d | **Alta:** abrir pidfd e usar referência estável; validar nascimento capturado depois de obter handle, porque PID pode reciclar antes da abertura |
| E03 | [os — os.pidfd_open e os.replace](https://docs.python.org/3.12/library/os.html), Python Software Foundation, documentação 3.12.16, seções respectivas | **Alta (API oficial):** pidfd_open é Linux >=5.3 / Python >=3.9; os.replace atômico sob condições da plataforma apenas para uma entrada |
| E04 | [Process Handles and Identifiers](https://learn.microsoft.com/en-us/windows/desktop/procthread/process-handles-and-identifiers), Microsoft Win32, página consultada 2026-11-20, “Process Handles and Identifiers”; [GetProcessTimes](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getprocesstimes), Microsoft, “Parameters” | **Alta:** HANDLE estável e criação do processo permitem distinguir reuso de PID; usar o **mesmo handle** para autorização e término no Windows |
| E05 | [os.replace](https://docs.python.org/3.12/library/os.html#os.replace), Python 3.12, seção “os.replace”; [fsync(2)](https://man7.org/linux/man-pages/man2/fsync.2.html), Linux man-pages, NOTES | **Alta:** replace não é transação de múltiplos arquivos; após arquivo fsync, considerar diretório fsync em SO/FS que suportem, com teste de crash real |
| E06 | [shutil.rmtree](https://docs.python.org/3.12/library/shutil.html#shutil.rmtree), Python 3.12, “rmtree.avoids_symlink_attacks” | **Alta:** defesa contra symlink depende de suporte baseado em descritores; fallback em plataforma não protegida não pode ser tratado como comprovadamente seguro |
| E07 | [OWASP Path Traversal Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Path_Traversal_Prevention_Cheat_Sheet.html), OWASP, s/d, “Validate the Resolved Path” e “Symbolic Links and Race Conditions” | **Alta (guia de segurança):** validação lexical sozinha tem TOCTOU; exigir containment por componentes e privilégios mínimos |
| E08 | [How to do distributed locking](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html), Martin Kleppmann, 2016, “Making the lock safe with fencing” | **Alta para o argumento técnico; não benchmark:** lease/nonce não evita escrita tardia; recurso/armazenamento deve rejeitar geração obsoleta |
| E09 | [Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/), Malcolm Featonby, AWS Builders' Library, s/d, “Client request ID” e “Semantic equivalence” | **Média-alta (prática documentada):** operação com idempotency key ajuda recuperação; efeito externo só é idempotente se o provedor realmente garantir |
| E10 | [Activity Definition](https://docs.temporal.io/activity-definition), Temporal, documentação consultada, “Idempotence for Activities” | **Alta (comportamento do sistema citado):** worker pode concluir efeito e cair antes de reportar, provocando retry; Temporal não garante execução externa única |
| E11 | [Google SRE, Distributed Periodic Scheduling with Cron Service](https://sre.google/sre-book/distributed-periodic-scheduling/), Google SRE Book, 2016, “Cron Jobs and Idempotency” e “Resolving partial failures” | **Média-alta (relato operacional):** preferir não duplicar lançamentos; buscar estado externo ou idempotência antes de replay |
| E12 | [Atomic Commit In SQLite](https://www.sqlite.org/atomiccommit.html), SQLite, s/d, “5. Multi-file Commit” | **Alta para protocolo documentado:** atomicidade multiarquivo exige mais que rename; não significa que este projeto precise migrar para banco |
| E13 | [Skyframe: Incrementality](https://github.com/bazelbuild/bazel/blob/master/docs/reference/skyframe.mdx), Bazel, documentação do branch master lida em 2026-11-20, “Incrementality” | **Alta para algoritmo descrito; analogia:** registro explícito de dependências permite invalidação seletiva, não hash global em cada task |
| E14 | [Designing Data-Intensive Applications, 2nd ed.](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/), Martin Kleppmann e Chris Riccomini, O'Reilly, fev. 2026, índice (“Transactions”, “The Trouble with Distributed Systems”) | **Alta para edição, autoria e sumário; limitada ao índice/trechos públicos:** estudar transações/concorrência; **livro integral não foi acessado**, nem experimentos reproduzidos |
| E15 | [Stateful tests](https://hypothesis.readthedocs.io/en/latest/stateful.html), Hypothesis, documentação online 6.170.17 observada, “Rule-based state machines”/“Invariants” | **Alta (manual de API):** modelo de estados permite propriedades para muitas interleavings; opcional, sem introduzir dependência obrigatória |
| E16 | [Temporal Activities](https://docs.temporal.io/activities), Temporal, seção “Activity retry / Heartbeats”, s/d | **Alta (documentação oficial):** checkpoints de atividades são úteis, mas não transferem idempotência por si sós |
| E17 | [git-update-ref](https://git-scm.com/docs/git-update-ref), projeto Git, manual, “DESCRIPTION”/“--stdin”, versão online consultada | **Alta para semântica de CAS de ref:** analogia útil para checar valor esperado ao publicar; não confundir Git ref com transação do manifest |
| E18 | [LangGraph Persistence](https://docs.langchain.com/oss/python/langgraph/persistence), LangChain, documentação online, “Persistence” e “Fault-tolerance”, s/d | **Média-alta para produto documentado:** checkpoints são alternativa, mas migração de runtime seria incompatível com escopo; não adotar apenas por marketing |

**Limites de prova:** nenhuma fonte externa demonstra que um design local em arquivos JSON seja seguro em NFS/SMB, nem que duas máquinas compartilhem lock corretamente. Fencing local protege o armazenamento que participa do mesmo lock; não oferece “exactly once” em recursos externos que ignoram o token. A garantia deve ser escrita como **at-most-one local publisher válido por epoch, sujeito ao filesystem e lock suportados**, não como consenso distribuído.

## 5. Alternativas comparadas

| Solução | Compatibilidade / custo | Riscos específicos | Decisão |
|---|---|---|---|
| A. PID e timestamp do lease, retry automático, rmtree após resolve | Pouca mudança, barato no happy path | PID reusado, dois writers, efeito duplicado, symlink/TOCTOU | **Rejeitada**: falha AC01, AC06, AC07 |
| B. Nonce aleatório e lock local sem fencing no commit | Adaptação pequena; já há nonce | Runner suspenso com nonce antigo ainda pode publicar; não classifica efeitos incertos | Insuficiente |
| **C. Lease com identidade, epoch monotônico, publish guardado, reconciliação e limpeza segura** | Reusa stdlib, plan_writer_lock, jobctl.pid_identity e validate_receipt; testes determinísticos | Precisa resolver ordem de locks, crash entre arquivos e lacunas SO | **Escolhida** no escopo 018 |
| D. SQLite com transações, WAL e journal de operações | Facilita estados transacionais locais | Migração de schema e dependências com risco de regressão e manutenção; ainda não evita efeito externo duplicado | **Adiada**, escalar só se C não demonstrar invariantes |
| E. Temporal/LangGraph ou coordenador multi-host | Boas ferramentas para longa duração | Mudança extensa de runtime e custos; efeitos não idempotentes ainda precisam conciliação | Fora do escopo; requisito multi-host requer estudo próprio |

## 6. Arquitetura escolhida: contratos executáveis

### 6.1 Componentes e responsabilidades

1. **lifecyclectl.py — OwnerIdentity e LeaseController:** observar start identity em vez de PID solto, adquirir/reclamar/renovar/liberar lease sob guarda determinística; classificar lease como owned, live_other, stale_verified ou unknown. Expor resultado estruturado de erro com reason code para status/cancel/resume, sem enviar nonce aos workers.
2. **planctl.py — único writer/receipt validator:** fornecer ponto interno de publicação que checa ownership + epoch **dentro do mesmo writer lock** antes de persistir task completion, receipt, subtask e evento. Preservar API atual para outros chamadores; se não há token explícito em chamador legí­timo, rejeitar mutações de execução que requerem fencing. Resolver reentrância do lock com função interna guardada ou callback no lock, **não** chamar lock aninhado cegamente.
3. **planctl.py — ScopedReceipt:** manter task_contract_digest e compute_task_contract_digests como fonte única; estender validate_receipt ou seu hook existente, recomputando somente entradas necessárias para a task/validation, incluindo comandos, ambiente/versão efetiva relevante e mapa da validação. Reusar observe_scoped_input_digests. Não invalidar receipt porque geração do manifest aumentou em uma task sem dependência alterada.
4. **lifecyclectl.py + jobctl.py existente — Recovery/Cancel:** reconciliar jobs e efeitos incertos antes de dispatch; stop_plan_jobs e process_tree devem conservar ownership e logs até verificação terminal. Jobctl.py é biblioteca reusada **sem edição** na 018.
5. **lifecyclectl.py e planctl.py — GuardedCleanup:** todas as entradas de cancel, reset e cleanup devem aplicar mesma validação de root, sentinel, no-symlinks/junction, inatividade verificada e proteção de recursos externos; escopo de exclusão é apenas o plano e controles possuídos, nunca source/teste/relatório/mapa.
6. **LIFECYCLE.md:** documentar estados, avisos de recuperação, comportamento de --force, segurança por SO e como não apagar recibos quando há efeito incerto.
7. **test/optimization/lifecycle_self_test.py:** suite nova da task com oráculo mínimo, processos de teste isolados e injeção de falhas, sem chamadas pagas.

### 6.2 Modelo persistido e proteção de concorrência

**Esquema conceitual para evolução compatível, não comando para substituir manifest schema 4:**

    RunnerLease {
      schema_version: 2,
      plan_id, owner_host_id, owner_boot_id,
      pid, process_start_identity, nonce,
      lease_epoch, acquired_at, observed_at
    }
    AttemptEvidence {
      task_id, subtask_id?, attempt_id, operation_id,
      external_effect_class, idempotency_key?,
      phase: prepared | dispatched | confirmed | uncertain,
      evidence_refs[], last_verified_at?
    }
    ReceiptExtension {
      task_id, contract_digest, scoped_input_digests,
      validation_command_digest?, validation_environment_digest?,
      resource_map_fingerprint?, producer_lease_epoch?,
      producer_attempt_id?
    }

- **Epoch estritamente crescente** por aquisição/reivindicação dentro de um estado durável controlado pelo mesmo lock; não usar apenas timestamp, número aleatório ou manifest.generation como epoch, porque manifest.generation sobe a cada escrita. Um antigo epoch não volta a valer após reset/cancel/reativação. Guardar a autoridade monotônica no plan root de modo recuperável; se ela se perder/ficar inconsistente, **bloquear** até reconciliação em vez de reiniciar do zero.
- **Aquisição:** verificar path, sentinel e ID; abrir lock de escritor no escopo do plano; ler owner/generation atuais; diferenciar (a) dono local comprovadamente ativo, recusar; (b) dono morto comprovado, elevar epoch e trocar lease; (c) remoto, identidades ausentes ou impossibilidade de verificar, retornar ownership_unknown. Escrever documento com arquivo temporário, fsync e replace, sem janela de dois ganhadores. O processo remoto nunca é morto por outro host.
- **Ação sensível de runner:** carregar lease, exigir plan_id, nonce, epoch, host/boot e process_start_identity iguais **sob lock**. A operação de completar ou invalidar receipt e a escrita do manifest devem acontecer na mesma região crítica. Revalidar antes do último replace, não só no início da task. Falha lease_lost => não publicar; preservar resultado como evidência para um novo owner reconciliar.
- **Release:** remover somente lease do próprio owner/epoch dentro de guarda, jamais por comparação de nonce seguida de unlink fora da guarda. Force não é licença para matar um processo diferente.
- **Compatibilidade:** leases versão 1 são interpretados conservadoramente. Se o PID versão 1 está **comprovadamente morto** e não há job ativo, permitir migração guardada; se PID está vivo mas sua identidade não foi registrada ou remoto é ambíguo, recusar substituição e pedir ação de recuperação documentada. Não recriar dependência em psutil nem modificar token exposto aos workers.
- **Identidade do processo:** Linux: /proc/[pid]/stat starttime + boot id como evidência registrada; para sinalização usar handle pidfd estável, associado à identidade após abertura, se suportado. Windows: OpenProcess, GetProcessTimes creation time e TerminateProcess no **mesmo HANDLE** após comparação. macOS e outros: usar primitivas/identidade já implementadas em jobctl, porém comparação antes de os.kill não elimina 100% do TOCTOU; sem mecanismo seguro, bloquear cancelamento destrutivo de PID incerto e manter estado para tratamento supervisionado. Nunca matar processo apenas com host+PID ou nome.
- **SO/FS:** locking e rename têm garantias delimitadas. Testar local POSIX e Windows; NFS/SMB/mount remoto ou relógio/boot não confiável => capability unsupported/uncertain até prova de locking e durability, sem alegar exclusão entre hosts.

### 6.3 Máquina de estados de retomada

**Estados existentes da task (schema 4) são preservados:** pending, in_progress, completed, blocked. Não inventar um novo status obrigatório sem migração. A distinção de efeito incerto mora em evidência de tentativa e em blocked com código reconciliation_required, sem consumir tentativa funcional automaticamente.

| Ponto de interrupção | Próxima ação segura | Nunca fazer |
|---|---|---|
| Antes de claim ou dispatch e sem operação enviada | Repetir claim idempotente no novo epoch | Inventar completion |
| Após claim, antes de qualquer efeito externo, prova persistida | Recuperar só subtask in_progress, preservar completed | Reset de todas as subtasks |
| Após registro de tentativa, antes de confirmar se o comando externo foi enviado | Marcar uncertain, consultar execução/log/endpoint por operation_id | Dispatch repetido sem reconciliação |
| Após efeito externo concluído e antes de persistir receipt | Checar fonte externa + artefatos/validadores; emitir receipt apenas após provas e ownership novo | Tratar ausência de receipt como inexistência de efeito |
| Após manifest replace, antes de TODO.md ou tasks/*.md | Tratar manifest como autoridade e regenerar projeções idempotentemente | Reverter task concluída só porque projeção está desatualizada |
| Após resultado de validação com hash de entradas válido, sem alteração dependente | Reusar receipt válido e evitar novo worker/teste custoso | Revalidar só porque mudou arquivo não dependente |
| Com job tracked ativo ou owner remoto desconhecido | Segurar estado, informar blocking reason e preservar artefatos | Apagar pasta e perder prova de posse |

**Reconciliação externa:** classe read-only/determinística pode consultar estado por operation_id; classe mutante exige chave idempotente comprovadamente aceita pelo provedor **ou** observação de estado final inequívoco; sem nenhuma das duas, manter blocked/reconciliation_required, preservar recibos de execução e indicar o procedimento manual seguro. Repetir API cobrada, migração, publicação ou criação de recurso com incerteza não é permitido.

**Resultado de crash não é falha de modelo:** não incrementar functional_failures nem escalar modelo pela interrupção em si; registrar reason code separado. Contar reexecução de efeito somente se autorizada e comprovadamente idempotente.

### 6.4 Receipt de 012 ampliado, sem validação paralela

- A identidade de um receipt é **task_id + contrato normativo + hashes reais das entradas declaradas + dependências transitivas relevantes + conjunto de comandos e ambiente de validação de fato usado + recurso/mapeamento pertinente + resultado comprovado**, com versionamento dos campos. Reusar o digest de contrato já existente; acrescentar campos de ambiente/mapeamento apenas se materialmente exigidos pelo test runner.
- Ao validar um receipt, observar os arquivos atuais com tratamento de symlink/ausência e comparar com digest salvo; o próprio manifest não é oráculo suficiente para dizer que um arquivo ainda tem conteúdo antigo. O recebimento de novas entradas fora do escopo pode exigir ampliação explícita do contrato, nunca substituição por hash de repositório inteiro.
- Mudança em arquivo não relacionado => receipt continua válido; mudança de fonte real, policy de aceitação, dependência necessária, comando de teste, runtime que altera semântica ou mapa da validação => receipt inválido com **razão concreta**. A revisão 019 deve demonstrar ambos os casos.
- Receipt válido após recovery não vira prova de review independente. Se task exige reviewer, respeitar validação/review própria do plano. Não confundir geração atual do manifest com geração do conteúdo originalmente validado; guardar histórico sem reeditar evidência antiga.
- Hash global do repositório fica para gate **final de integração**, quando o escopo declarado realmente é global.
- Não carregar a árvore do projeto nem markdown de relatórios em modelo para validar hash; isso é operação de script e ferramenta.

### 6.5 Cancelamento, reset e limpeza protegida

1. **Selecionar alvo:** cancel atinge somente plano ativo autorizado; reset atinge cada diretório reconhecido com sentinel sob work root esperado. Nunca percorrer “../”, absolute aliases, drive diferente, link/junction ou plan ID adulterado.
2. **Bloquear antes de remover:** sob guarda verificar ownership de runner e jobs; sinalizar apenas processo autenticado pelo handle/identidade; aguardar parada e confirmar estado terminal. Se job lost, remote owner, stop falhar ou identidade ambígua, abortar a exclusão e preservar workspace completo.
3. **Inspecionar o conteúdo:** exigir path lexical/canônico compatível, sentinel e manifest correlacionados; proteger qualquer link/junction e entradas estranhas. Usar rmtree fd-based resistente onde suportado; no fallback sem defesa, recusar limpeza em árvore mutável por adversário. Revalidar o alvo imediatamente antes da exclusão. Intake e active pointer precisam de contenção e CAS equivalentes.
4. **Ordem de efeitos:** marcar/controlar intenção de cancelamento; parar processos; verificar; remover somente controles permitidos; então limpar active pointer que ainda aponta para o plano removido. Recuperação idempotente se cair após cada passo. Em caso de erro, prefira pointer reparável e estado preservado à exclusão prematura de prova.
5. **Preservar invariantes:** código-fonte, testes, artefatos de produto, .ai-work/SERVICE_MAP.md, fingerprints de recursos, relatórios em docs/research, outros planos e logs externos sobrevivem. Planctl.cleanup_plan mantém gate completed + summary_generated para sucesso comum; force não remove sentinels/escopo nem bypassa segurança de processo.
6. **Sem operações globais:** nenhuma chamada git clean, git reset, remoção de diretórios de usuário ou instalação global. Privileges mínimos e erros fáceis de diagnosticar.

### 6.6 Compatibilidade, segurança, performance e tokens

- **Caminho incremental:** (1) adicionar verificação de identidade e epoch à API atual com compatibilidade de leitura; (2) proteger claim/complete/release via writer guard; (3) introduzir evidência de efeito incerto e reconciliation; (4) fortalecer cleanup; (5) ampliar receipt existente e documentação. É uma sequência de implementação da **mesma task**, não novas tasks. Revisão 019 permanece independente.
- **Compatibilidade schema 4:** não trocar enum de status nem invalidar receipts históricos por metadado não necessário; preservar CLI current, activate, recover, resume, cancel, reset e exit codes existentes quando seguro; novas razões podem ser documentadas. Verificar bloqueios de leases v1 no teste; não inventar migração universal de sistemas remotos.
- **Segurança:** nonce de posse nunca enviado ao prompt; paths sempre validados; não confiar em JSON do disco ou stdout do worker como autorização; no-follow, permissions restritas, logs sem secrets, erro explícito para registro corrompido; falhar fechado onde processo/FS não têm capacidade conhecida.
- **Concorrência:** rodar ao menos dois contenders simultâneos com mesma visão de manifest e lease; um único ganhador, perdedor não publica. Validar comportamento após stale owner acordar e tentativa de release de epoch anterior. Testar interleavings de cancel/complete/claim.
- **Economia:** consultas current são read-only e diretas; sem modelo em check de liveness, hash, validação de receipt, cleanup ou triagem rotineira. Usar arquivos escopados e índices curtos; preservar trabalho válido reduz re-dispatch. Não informar ganhos de tempo/tokens não medidos.
- **Métricas de implementação a coletar sem dados fabricados:** taxa de dispatch duplicado (alvo zero no harness testado), tentativa de completion obsoleta rejeitada (100% dos cenários), falhas de cleanup inseguro (100% bloqueadas nos fixtures), nº de subtasks completadas preservadas, nº de hashes calculados por task, tempo de current/resume, revalidações evitadas, uso de tokens/cobrança quando fornecedor medir. Comparar baseline e novo em ambiente idêntico; nenhum benchmark foi executado nesta pesquisa.

## 7. Testes, falhas injetadas e aceite mensurável

**Prioridade**: testes herméticos stdlib de estados e segurança, pequenas integrações com subprocessos próprios e regressão; não disparar suites E2E remotas por padrão. Hipótese de concorrência deve ser reproduzível com barreiras/eventos, sem sleep como única sincronização.

| AC da task 018 | Fixture/contraprova obrigatória | Gate observável |
|---|---|---|
| AC01 — PID reciclado | Lease aponta PID de outro processo com start time diferente; tentar cancel, SIGTERM e cleanup | Processo inocente sobrevive; erro ownership_mismatch; nada removido |
| AC02 — crash entre writes | Injetar falha após lease claim, checkpoint subtask, manifest replace, TODO write, task projection, release | Nenhuma subtask completed retrocede; só in_progress volta a retomável; projeções restauráveis |
| AC03 — paths/sentinel | Plano symlink, junction Windows, parent .., entrada trocada entre check e uso, sentinel ausente, path de mesma string-prefix | Exclusão recusada; arquivo sentinela externo intocado |
| AC04 — stop-before-delete | Job supervisionado de teste ainda ativo; parar com falha, demorar ou virar lost | Workspace e log sobrevivem enquanto processo não está confirmado terminal |
| AC05 — preservar produto | Criar source/teste, docs/research, .ai-work/SERVICE_MAP.md e outro plano; concluir + cleanup | Todos preservados, somente controles do plano candidato removidos |
| AC06 — reused PID / stale controller | Runner A morre, PID é reusado, B assume epoch maior, A tenta release/kill | A não mata processo e não remove lease B; B mantém ownership |
| AC07 — stale writer completion | Runner A chega ao commit de 018 depois de B assumir; dois writers colidem sob lock | Completion/receipt de A rejeitado, status/generation/receipt válidos de B intactos |
| AC08 — scoped receipt | Alterar arquivo não dependente; depois fonte declarada/test cmd/mapa realmente necessário | Primeiro mantém receipt válido; segundo invalida com motivo preciso, sem hash global |

**Contraexemplos adicionais:** lease JSON truncado; host igual após reboot (boot id diferente); relógio retrocedendo; handle sem permissão; remote lease expirado sem prova de morte; tentativa externa paga aceita seguida de crash; alteração de código entre hash e validação; erro de fsync/replace; Windows handle/permissões/junction; Linux pidfd indisponível; lock tomado enquanto cancel ocorre; arquivo malicioso dentro de jobs; validação reportada por worker mas não executada pelo runner. Todos devem bloquear ou reconciliar conforme o caso, e não mascarar falha.

**Oráculo mínimo:** registrar o conjunto de owners/epochs válidos e de arquivos protegidos, gerar sequências acquire → claim → checkpoint → crash → recover → cancel/complete → cleanup; após cada passo exigir (1) no máximo um publisher válido; (2) nenhuma ação de processo sem identidade; (3) resultado externo incerto não vira repetição automática; (4) completed comprovado nunca reabre por input alheio; (5) remoções são subárvore legítima. Se Hypothesis estiver disponível, usar sua state machine; sem ele, seeds determinísticas na stdlib. Não adicionar uma dependência à task apenas para testar.

**Comandos declarados em TASK_INPUTS.json para a futura implementação** (não executados nesta pesquisa):

    python test/optimization/lifecycle_self_test.py
    python skill/plan-and-execute/scripts/lifecycle_self_test.py
    python skill/plan-and-execute/scripts/watchdogctl_self_test.py
    python skill/plan-and-execute/scripts/keepalivectl_self_test.py
    python skill/plan-and-execute/scripts/preplan_self_test.py
    python skill/plan-and-execute/scripts/task_memory_self_test.py
    python skill/plan-and-execute/scripts/self_test.py

**Gates reais do plano (task 018):**

    python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_018
    python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_018

Executar suites completas quando o plano exigir; no ciclo de reparo, agrupar todas as falhas, corrigir/testar apenas afetados e depois realizar o gate completo. Coletar logs, exit codes, hashes e limites reais. Não declarar passed com mock; revisão 019 deve confrontar o código finalmente entregue, não aprovar somente este relatório.

## 8. Riscos, conflitos de contrato e gatilhos de revisão

1. **Fencing realmente atômico:** um check fora do writer lock é TOCTOU; explorar como save_manifest atualmente abre seu próprio lock. Refatoração que encadeie dois locks pode deadlock ou criar múltiplos publishers; exigir teste de interleaving.
2. **Lease epoch versus manifest.generation:** o último muda em operações de estado não relacionadas; evoluir schema sem interpretar cada mudança como takeover. Recibos históricos têm generation de registro, não prova isolada de posse.
3. **Tarefas Markdown são projeções do manifest:** save_manifest pode apagar a seção de pesquisa adicionada em 018. A implementação **deve ler este arquivo antes de qualquer gravação**, conferir depois que a arquitetura de referência continua acessível pelo guia e pela definição; registrar solução compatível sem mutação de status. O guia preserva link durável fora da projeção.
4. **Ambiente remoto:** hostname/TTL não provam morte nem dão lock interhost; com NFS/SMB e relógios conflitantes a regra é recusar takeover e documentar limitação. Não prometer exactly-once global.
5. **Portabilidade:** Windows HANDLE seguro e Linux pidfd podem exigir caminhos distintos; macOS sem handle atômico equivalente pode não oferecer cancel forçado seguro. Validar em plataformas suportadas e falhar fechado em casos não cobertos.
6. **Efeitos não idempotentes:** quando não há endpoint de consulta nem chave real, somente intervenção/reconciliação autorizada elimina a ambiguidade; não inferir sucesso pelo fim do processo.
7. **Dependências:** 015 é requisito da implementação 018; 019 revisa o resultado; 016 implementa depois de 019 segundo manifest. Não usar este estudo para alterar ordem ou marcar task como entregue.
8. **Versionamento:** base prepared de 2026-10-28 usa baseline diferente do código inspecionado; revalidar só mudanças materiais de símbolos, comportamento, OS/FS, regras de testes, não repesquisar sem fato novo.

## 9. Instrução vinculante para a futura execução da task 018

Antes de S001, ler esta pesquisa **inteira** junto com prepared-research/018-lifecycle.md, verificar apenas divergências materiais contra código/ambiente atuais e aplicar **a arquitetura da seção 6 como referência obrigatória de partida**. Se surgir uma incompatibilidade técnica comprovada, documentar a evidência e a decisão antes da modificação; não substituir com palpite de modelo. Em S002–S004 implementar a proteção de processo, fence e receipt único; em S005 executar todos os contraprovas e comandos declarados; em S006 produzir receipt/outcome reais para a revisão 019. Preservar status, escopo, quotas e checkpoints da task.

**O que esta pesquisa verificou:** conteúdo de task/manifest/TASK_INPUTS, símbolos e comportamento textual da branch, documentos oficiais e relatos citados. **O que não verificou:** execução de processo nesses SOs, crash físico, multi-host NFS, resultados de testes automáticos da task ainda não implementada, quotas autenticadas de provedores, métricas de performance, economia real de tokens e revisão independente. Nenhum desses itens deve ser declarado concluído a partir deste documento.
