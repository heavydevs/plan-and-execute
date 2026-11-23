# PAE — protocolo operacional ChatGPT → Claude local

**Vigente desde 2026-11-23.** Repositório `heavydevs/plan-and-execute`; branch fixa `checkpoint/plano1-estudo-provider-switch-20261028`.
Esta política substitui, para o comando `próximo`, os roteamentos antigos de revisão pela própria conversa ChatGPT, por GitHub Actions ou pelo Antigravity. Integrações existentes podem servir como ferramentas auxiliares comprovadas, mas não substituem o Claude local solicitado pelo usuário. **Uma única task ativa no plano.**

## 1. Autoridade e segurança de estado

- **Manifesto:** `.ai-work/20261028-skill-study-provider-switch/manifest.json` é a única fonte oficial de status `pending`/`in_progress`/`completed`, dependências, subtasks e aceites. Alterar status somente pelo controlador oficial `planctl` e seus contratos.
- **TODO gerado:** `.ai-work/20261028-skill-study-provider-switch/TODO.md` é o espelho do manifesto. Checklists internos da task orientam a próxima subetapa, não autorizam ignorar a task bloqueante.
- **TODO na raiz:** `TODO.md` documenta **a fase de passagem e o dono atual**, não substitui o manifesto nem prova entrega. Em desacordo entre documentos ou sem observabilidade, **parar e reconciliar**, sem escolher uma nova task.
- **Git remoto:** todo handoff e mudança de fase deve estar em commit publicado na mesma branch, com SHA, código/hashes, checks efetivamente executados, pendências e próximo responsável. Proibir force-push, sobrescrita de trabalho não commitado e commits sem controle de concorrência (CAS / fast-forward).
- Uma execução de `planctl` da task não pode continuar automaticamente para a seguinte. Usar comandos delimitados por ID e impedir `run/resume` global sem um limite verificado. Não confundir instrução de parada com garantia técnica do runner.
- Uma sessão não aprova independentemente seu próprio patch; após correção, exigir **novo revisor independente** e hashes finais. Não inventar sessão, tier, esforço, logs, saída do CLI nem resultado do gate.

## 2. Sempre sincronizar antes de decidir

No checkout real (Claude local e ChatGPT quando houver terminal autenticado):

```bash
git status --short
git fetch origin checkpoint/plano1-estudo-provider-switch-20261028
git switch checkpoint/plano1-estudo-provider-switch-20261028
git pull --ff-only origin checkpoint/plano1-estudo-provider-switch-20261028
git status --short
git rev-parse HEAD
```

Se houver alterações locais, divergência, conflito, branch errada, falha de rede ou erro de autenticação, **não apagar nem descartar** nada: preservar o trabalho, diagnosticar e parar se não for possível sincronizar com segurança. No ChatGPT sem terminal Git, ler o HEAD remoto e o conteúdo **atual** pelo conector GitHub e publicar com commit baseado nesse HEAD e atualização condicional da referência; isso é sincronização equivalente de conteúdo, **não** alegar que `git fetch/pull` foi executado.

Consultar `AGENTS.md`, este protocolo, `TODO.md`, o manifesto, o TODO gerado, a definição da task ativa e sua checklist mínima. Não recuperar histórico pessoal de chats para decidir o estado.

## 3. Máquina de estados — apenas coordenação

Os rótulos abaixo são **fases operacionais no TODO da raiz**, não novos status válidos do manifesto.

| Fase | Responsável | O que fazer ao receber `próximo` |
| --- | --- | --- |
| `chatgpt_implementando` | ChatGPT | ChatGPT retoma apenas esta task; Claude não inicia validação prematura |
| `aguardando_validacao_claude` | Claude | ChatGPT só verifica e informa bloqueio; Claude assume a revisão da mesma task |
| `claude_validando_corrigindo` | Claude | Claude retoma revisão/correção; ChatGPT não altera a task nem inicia outra |
| `bloqueada` | responsável registrado | Resolver impedimento documentado na mesma task; nunca pular para a seguinte |
| `concluida` | ninguém | Somente após manifesto `completed`, gates e push; nova task só em NOVO `próximo` do ChatGPT |

**Seleção inicial (somente ChatGPT):** após sincronizar, se houver task em progresso ou handoff pendente, ela prevalece. Se não houver nenhuma em execução, selecionar a primeira **task de desenvolvimento** não concluída e elegível no manifesto/TODO gerado, verificando dependências e subtasks. Não selecionar a primeira pesquisa de um relatório, não executar várias tasks no mesmo turno e não avançar sem gatilho do usuário.

**Migração da 015:** ela permanece `pending` no manifesto, e o estágio operacional inicial deste protocolo é `aguardando_validacao_claude`. Já existe um parecer técnico ChatGPT publicado no commit `71cb8673ae122979cffc09cfafef4263d0746ce1`, mas isso **não é** o gate independente Claude/max-tier. Claude deve conferir o HEAD e todos os hashes novamente, sem tratar esse parecer como aprovação.

## 4. Responsabilidade exclusiva do ChatGPT

1. Ao receber `próximo` em um novo chat, sincronizar e identificar o estado antes de qualquer pesquisa/implementação.
2. Se o dono for Claude (fase aguardando/validando/corrigindo), **parar**, informar task/phase e pedir apenas que o usuário execute `próximo` no Claude local. Jamais fazer uma revisão para substituir o Claude, corrigir em paralelo ou iniciar a 016.
3. Se estiver sob responsabilidade do ChatGPT, retomar a task ou iniciar a primeira elegível, pesquisar quando necessário, consolidar arquitetura, implementar no escopo autorizado e executar testes reais possíveis, incluindo casos negativos.
4. Resolver defeitos conhecidos antes do handoff; se testes ou ferramentas indispensáveis não puderem ser executados, documentar quais foram/ não foram rodados, sem declará-los aprovados. Não marcar `completed`.
5. Publicar código, testes, documentação, SHA e instruções específicas do handoff em commit/push. Atualizar `TODO.md` para `aguardando_validacao_claude`, manter o manifesto pendente, confirmar o HEAD remoto e **parar**. Não antecipar a revisão Claude.

## 5. Responsabilidade exclusiva do Claude local

1. Ao receber `próximo` no ambiente local, sincronizar; só agir se a fase indicar Claude como dono e o manifesto confirmar a mesma task incompleta. Nunca selecionar, iniciar, estudar ou implementar outra task. Ler `CLAUDE.md` e **aplicar a skill versionada `skill/plan-and-execute/SKILL.md`** e referências estritamente necessárias. A skill deve orientar tanto **validação quanto correção**.
2. Registrar a tomada de responsabilidade (`claude_validando_corrigindo`) e commit/push quando possível, para impedir trabalhos simultâneos. Executar a **primeira revisão em contexto novo, somente leitura**, sem consultar relatórios/conclusões de outras IAs antes do parecer próprio. Verificar requisitos, código real, arquitetura, segurança, performance, testes, hashes, problemas reproduzíveis (gravidade, arquivo, linha, prova).
3. Após registrar o primeiro parecer, se houver defeito: usar a skill PAE para diagnosticar, corrigir e, se necessário, **rearquitetar a mesma task**, respeitando escopo/aceites. Consolidar falhas, testes focais, regressões e bateria completa com logs reais. Não avançar nem invocar plano inteiro em modo automático.
4. **Depois de qualquer patch**, a sessão que corrigiu não pode emitir a aprovação independente do patch. Obter um novo contexto/sessão de revisor **sem participação na correção**, ainda que ambos usem Claude; capturar modelo, effort, ID real de sessão e hashes finais quando observáveis. Se não existir independência comprovável, não forçar aprovação: deixar a task bloqueada na validação.
5. Executar o **gate original**, sem afrouxá-lo. Para 015, exigir `P1_TESTS_015`, `P1_015` e `check_delivery.py` e quaisquer requisitos de tier/sessão no formato real exigido por `review_dispatch.py`. **Claude Code local autenticado não prova automaticamente que o validador aceita sua identidade/recibo**; investigar a compatibilidade e, se necessário, registrar impedimento e proposta de adaptador genuíno com testes negativos, sem forjar evidência.
6. Somente com testes, revisão independente final, recibos e gate aprovados, finalizar via controlador oficial, atualizar manifesto/TODO gerado, marcar fase `concluida` no TODO da raiz, fazer commit/push, verificar HEAD remoto e **PARAR**. Se falhar por motivo reparável, iterar na MESMA task; se bloqueio externo, gravar fase `bloqueada`, responsável Claude, prova e motivo, publicar e **PARAR**.
7. Em nenhuma hipótese Claude inicia a task 016 (ou qualquer sucessora), mesmo que a 015 tenha sido concluída.

## 6. Checkpoint mínimo de passagem

No `TODO.md` ou em um handoff por task versionado: ID e título; **fase** e responsável; baseline de **código** e SHA Git; arquivos alterados e digests relevantes; resultado de testes com comandos, códigos de saída e URLs; pesquisa/arquitetura e critérios de aceitação; pendências, riscos e bloqueios; próximos passos **somente na mesma task**. Evidência não executada = `não executado`; ausência de recibo = `pendente`. Depois do primeiro parecer independente, vincular documento, sessão real observada e hashes correspondentes, evitando reciclar aprovação após patch.

## 7. Proteção contra concorrência e exceções

- Dois agentes não devem trabalhar simultaneamente na mesma task. O primeiro a publicar a fase assume responsabilidade; qualquer atualização usa o HEAD mais recente e fast-forward/CAS. Em divergência, reler e reconciliar; nunca `push --force`.
- Se Claude tentar `próximo` sem fase `aguardando_validacao_claude` ou `claude_validando_corrigindo`, não começar trabalho e comunicar a fase atual.
- Se ChatGPT encontrar `aguardando_validacao_claude`, `claude_validando_corrigindo` ou `bloqueada` sob Claude, não tentar concluir o gate por conta própria.
- Alterações **apenas documentais neste protocolo** não mudam `status` do manifesto, nem constituem aprovação de 015; não executar 016 nesta migração.
- Não publicar credenciais nem dados privados; uso de permissões locais ampliadas não se aplica a CI público. Acesso ao GitHub não significa acesso ao terminal local. Não usar Antigravity (`agy`).
