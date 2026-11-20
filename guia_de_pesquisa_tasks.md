# Guia de pesquisa antecipada das tasks — execução retomável

> **Alvo exclusivo:** repositório `heavydevs/plan-and-execute`, branch `checkpoint/plano1-estudo-provider-switch-20261028`, plano `.ai-work/20261028-skill-study-provider-switch`. Criado em 2026-11-20. Este roteiro **pesquisa e prepara**; não implementa tasks, não aciona provedores pagos, não executa o plano nem altera `completed/pending` no `manifest.json` ou no `TODO.md`.

## Pedido original do usuário (preservado literalmente)

> Comecei o desenvolvimento o plano ativo na branch checkpoint/plano1-estudo-provider-switch-20261028
> 
> Contudo, o desenvolvimeto  fez muitas pesquisas. Assim, parei o plano.
> 
> Quero que você adiante  a pesquisa das próximas tasks e salve de forma organizada, colocando as referências em cada para o arquivo de resultado da pesquisa.
> 
> Faça isso para  todas as task.
> 
> Para  cada  task @Busca na web faça uma pesquisa ampla  e profunda, consultando documetações,  livros, artigos, benchmark, etc.  Busque como encontrar informações relevantes  e pertinentes  de cada  assunto.
> 
> No resultado, você  também irá escrever a  arquitetura  baseada no estudo.
> 
> Quero que você crie um arquivo na raiz chamado guia_de_pesquisa_tasks.md na raiz com esse mesmo  prompt que  estou fazendo para você. E lá nesse arquivo deve ter uma checklist para  cada tarefa que ainda não foi feito a busca. Conforme você  pesquisou muito para a primeira tarefa da checklist,  escreveu o resultado da  busca em um relatório e vinculou a task dando a instrução para usar  o  resultado do estudo como  arquitetura,  dizendo na task para utilizar,  então, você  vai marcar o  item da checklist do arquivo guia_de_pesquisa_tasks.md como feito. E vai passar para o próximo item, que  é  vinculado a outra  task.  Faça isso até  acabar todos os itens de guia_de_pesquisa_tasks.md.
> 
> Essa  instrução de controle também tem que estar  no arquivo guia_de_pesquisa_tasks.md
> 
> Vá commitando e fazendo push  sempre que completar a  pesquisa e arquitetura  de  uma task -  sempre que marcar como concluido.  Coloque também  essa orientação de commit e push no arquivo guia_de_pesquisa_tasks.md
> 
> Pense que se eu quiser voltar amanhã com outra  IA, se eu mandar ele  ler  e  seguir o arquivo guia_de_pesquisa_tasks.md,  ela  tem que continuar por  conta própria as próximas tasks.  O arquivo guia_de_pesquisa_tasks.md tem que conter o guia  de tudo o que eu quero.

## Contrato operacional para qualquer IA que retomar

1. Antes de tudo, confirme `git status`, branch, origem remota e `HEAD`; trabalhe **apenas** em `checkpoint/plano1-estudo-provider-switch-20261028`. Nunca faça reset/force-push, não altere `main` nem sobrescreva trabalho concorrente. Use `git fetch`/pull de forma segura; em conectores remotos use leitura de SHA e escrita condicional. Pare se houver conflito e reconcilie.
2. Leia **este arquivo inteiro** e o estado autoritativo `.ai-work/20261028-skill-study-provider-switch/manifest.json`, o índice `TODO.md` e `docs/plans/20261028-skill-optimization/TASK_INPUTS.json`. Verifique integridade do plano. As caixas abaixo controlam **conclusão de pesquisa**, não de implementação. Houve 14 tasks de implementação/revisão concluídas (001–014) na criação; não reinscrever como pendentes.
3. Execute a **primeira caixa [ ] na ordem apresentada** (ordem real do plano, inclusive 082–086 por último). Leia apenas a definição dessa task, dependências diretas, símbolos/contratos afetados e seus relatórios preparados em `docs/research/20261028-skill-optimization/prepared-research/`. Para revisões, use a pesquisa do predecessor e escreva um *plano de revisão independente* específico, sem confundir revisão futura com revisão já executada.
4. **Pesquise na web ampla e criticamente a matéria daquela task**, usando busca de fontes oficiais (documentações de fornecedores, normas, especificações, release notes, manuais) e depois trabalhos acadêmicos, livros com trechos acessíveis legitimamente, artigos técnicos, estudos e benchmarks aplicáveis. Formule questões que realmente mudam a arquitetura, busque contraexemplos, compare alternativas e verifique versão/data; não se limite a resumos de buscador nem invente acesso a livros completos, métricas, testes ou provedores autenticados. Registre discrepâncias entre fontes antigas e atuais. Pare por saturação da decisão técnica, **não por número arbitrário de links**.
5. Crie `docs/research/20261028-skill-optimization/pesquisas-por-task/NNN-pesquisa-arquitetura.md`, para cada ID NNN. Um relatório só pode ser marcado pronto se incluir: task/objetivo/status e links para a definição e bases anteriores; perguntas/achados com evidências internas (paths/símbolos) e externas (título, editora/autor, URL, data da fonte ou versão, data de acesso, trecho/seção pertinente, confiabilidade e consequência de arquitetura); comparação de ao menos duas soluções com trade-offs; **arquitetura executável escolhida** (componentes, módulos/classes/arquivos, interfaces e contratos, fluxo de dados e estados, erros, concorrência, migração/compatibilidade, segurança, performance, economia de tokens/model routing); estratégia de testes de boa relação custo/risco, casos negativos, critérios de aceite mensuráveis; dependências e riscos pendentes. Declare o que foi verificado versus inferido, e quando uma medição ainda falta. Trate o relatório existente como evidência de partida, nunca como prova de execução.
6. Na própria definição `.ai-work/20261028-skill-study-provider-switch/tasks/NNN-*.md`, acrescente uma seção curta `## Pesquisa e arquitetura obrigatórias (pré-execução)`, linkando o relatório exato e **instruindo a IA implementadora/revisora a usá-lo como a arquitetura aprovada de partida**, checando só incompatibilidades materiais de versão/código antes de implementar. Preserve objetivos, escopo, critérios, validações e checkpoints; não altere front matter, status, progresso, hashes de implementação ou privilégios. Se a definição física estiver faltando, consulte o manifest/plan-spec e restaure coerentemente antes de marcar pesquisa concluída; não forje uma definição.
7. Faça verificação **antes de marcar [x]**: relatório existe, referências acessíveis e específicas, arquitetura não contradiz a definição nem outros relatórios, task cita o caminho exato, mudanças isoladas ao guia/relatório/task, sem implementação ou marcação falsa. Se achar lacuna, mantenha [ ] e resolva ou registre o bloqueio.
8. **Após cada única task pesquisada e arquitetada**, marque **somente sua caixa** abaixo como `[x]` e atualize ali o link para relatório e SHA/URL do commit depois de confirmar o push. **Faça commit e push imediatamente para o mesmo branch**, agrupando relatório + vínculo na task + atualização da checklist em **um commit por task**. Nunca agrupe várias tasks num único commit; nunca marque [x] antes de conseguir publicar e confirmar o commit no remoto. Em falha de push, não avance: reconcilie/retry sem perder alterações. O bootstrap inicial deste guia pode ter commit próprio.
9. Após publicar, verifique remoto/commit, confira que a próxima caixa está intacta e passe à **próxima [ ] sem solicitar novo prompt**. Continue até a checklist acabar. Ao voltar em outra sessão/IA, comece do item 1 e da primeira [ ]; não repesquise relatórios validados nem recarregue todas as tasks no contexto. Se um commit trouxe o relatório e não marcou caixa por falha parcial, reconcilie documento, task e guia antes de pesquisar mais.
10. Mantenha o índice sincronizado se novas tasks forem acrescentadas ao plano: só adicione tasks realmente pendentes em ordem de dependências, sem renumerar IDs; nunca considere uma *revisão de implementação* como realizada porque seu estudo foi feito. Para mudanças em contrato comum, deixe referência cruzada para pesquisas anteriores e valide as interfaces, evitando copiar relatórios inteiros nos prompts.
11. Ao final, execute verificações não destrutivas (`planctl validate`, auditoria de mapeamento, `git diff --check` ou equivalentes disponíveis), sem iniciar execução de implementação. Registre qualquer limite de ambiente ou impossibilidade de validação; não afirme testes, autoria independente, economia financeira ou benchmarking não medidos. O critério de término é: todas as caixas [x] **com relatório, vínculo e commit/push próprios** auditáveis.

## Estado inicial e localização das saídas

- **Manifest é autoridade de implementação**: `.ai-work/20261028-skill-study-provider-switch/manifest.json`.
- **Guia é autoridade do ciclo de pesquisa**: este arquivo e suas caixas; não reusa `TODO.md` para marcar pesquisa.
- **Relatórios de pesquisa por task**: `docs/research/20261028-skill-optimization/pesquisas-por-task/NNN-pesquisa-arquitetura.md`.
- **Bases de pesquisa anteriores**: `docs/research/20261028-skill-optimization/prepared-research/`, `docs/research/20261028-skill-optimization/PLAN_ARCHITECTURE_REVIEW_20261120.md`, `docs/plans/20261028-skill-optimization/TASK_INPUTS.json`.
- **Quantidade na criação**: 132 tasks totais; 14 com implementação concluída; **118 pesquisas pendentes**. Alterações futuras precisam ser detectadas de novo.

## Checklist sequencial de pesquisas antecipadas

As caixas registram **somente pesquisa + arquitetura + vínculo na definição + commit/push verificado**, não a execução de tarefas.

- [x] **015** — Review and correct assigned context, learned facts and token budgets. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/015-pesquisa-arquitetura.md) · commit: pendente
- [ ] **016** — Implement versioned shared contracts and selective invalidation. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/016-pesquisa-arquitetura.md) · commit: pendente
- [ ] **017** — Review and correct versioned shared contracts and selective invalidation. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/017-pesquisa-arquitetura.md) · commit: pendente
- [ ] **018** — Implement leases, resume, cancellation, reset and guarded cleanup. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/018-pesquisa-arquitetura.md) · commit: pendente
- [ ] **019** — Review and correct leases, resume, cancellation, reset and guarded cleanup. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/019-pesquisa-arquitetura.md) · commit: pendente
- [ ] **020** — Implement capability floors, evidence ladders and retry accounting. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/020-pesquisa-arquitetura.md) · commit: pendente
- [ ] **021** — Review and correct capability floors, evidence ladders and retry accounting. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/021-pesquisa-arquitetura.md) · commit: pendente
- [ ] **022** — Implement provider chains, cooldowns, quotas and availability ledgers. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/022-pesquisa-arquitetura.md) · commit: pendente
- [ ] **023** — Review and correct provider chains, cooldowns, quotas and availability ledgers. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/023-pesquisa-arquitetura.md) · commit: pendente
- [ ] **024** — Implement workload routing for frontend, repair and monitoring. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/024-pesquisa-arquitetura.md) · commit: pendente
- [ ] **025** — Review and correct workload routing for frontend, repair and monitoring. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/025-pesquisa-arquitetura.md) · commit: pendente
- [ ] **026** — Implement model catalog evidence, caches, snapshots and refresh. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/026-pesquisa-arquitetura.md) · commit: pendente
- [ ] **027** — Review and correct model catalog evidence, caches, snapshots and refresh. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/027-pesquisa-arquitetura.md) · commit: pendente
- [ ] **028** — Implement fresh workers, delegation gates and prompt-cache boundaries. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/028-pesquisa-arquitetura.md) · commit: pendente
- [ ] **029** — Review and correct fresh workers, delegation gates and prompt-cache boundaries. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/029-pesquisa-arquitetura.md) · commit: pendente
- [ ] **030** — Implement claude Code and Claude Agent SDK adapter. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/030-pesquisa-arquitetura.md) · commit: pendente
- [ ] **031** — Review and correct claude Code and Claude Agent SDK adapter. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/031-pesquisa-arquitetura.md) · commit: pendente
- [ ] **032** — Implement codex CLI, Agent SDK and schema adaptation. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/032-pesquisa-arquitetura.md) · commit: pendente
- [ ] **033** — Review and correct codex CLI, Agent SDK and schema adaptation. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/033-pesquisa-arquitetura.md) · commit: pendente
- [ ] **034** — Implement antigravity and legacy Gemini adapter. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/034-pesquisa-arquitetura.md) · commit: pendente
- [ ] **035** — Review and correct antigravity and legacy Gemini adapter. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/035-pesquisa-arquitetura.md) · commit: pendente
- [ ] **036** — Implement qwen Code headless adapter. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/036-pesquisa-arquitetura.md) · commit: pendente
- [ ] **037** — Review and correct qwen Code headless adapter. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/037-pesquisa-arquitetura.md) · commit: pendente
- [ ] **038** — Implement kimi Code CLI adapter. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/038-pesquisa-arquitetura.md) · commit: pendente
- [ ] **039** — Review and correct kimi Code CLI adapter. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/039-pesquisa-arquitetura.md) · commit: pendente
- [ ] **040** — Implement trae Agent adapter. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/040-pesquisa-arquitetura.md) · commit: pendente
- [ ] **041** — Review and correct trae Agent adapter. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/041-pesquisa-arquitetura.md) · commit: pendente
- [ ] **042** — Implement muse Code adapter and session protocol. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/042-pesquisa-arquitetura.md) · commit: pendente
- [ ] **043** — Review and correct muse Code adapter and session protocol. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/043-pesquisa-arquitetura.md) · commit: pendente
- [ ] **044** — Implement gLM provider profiles. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/044-pesquisa-arquitetura.md) · commit: pendente
- [ ] **045** — Review and correct gLM provider profiles. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/045-pesquisa-arquitetura.md) · commit: pendente
- [ ] **046** — Implement deepSeek provider profiles. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/046-pesquisa-arquitetura.md) · commit: pendente
- [ ] **047** — Review and correct deepSeek provider profiles. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/047-pesquisa-arquitetura.md) · commit: pendente
- [ ] **048** — Implement independent validation, evidence packets and failure classification. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/048-pesquisa-arquitetura.md) · commit: pendente
- [ ] **049** — Review and correct independent validation, evidence packets and failure classification. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/049-pesquisa-arquitetura.md) · commit: pendente
- [ ] **050** — Implement resource discovery, freshness and runtime health. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/050-pesquisa-arquitetura.md) · commit: pendente
- [ ] **051** — Review and correct resource discovery, freshness and runtime health. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/051-pesquisa-arquitetura.md) · commit: pendente
- [ ] **052** — Implement progress windows, cancellation and process-tree safety. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/052-pesquisa-arquitetura.md) · commit: pendente
- [ ] **053** — Review and correct progress windows, cancellation and process-tree safety. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/053-pesquisa-arquitetura.md) · commit: pendente
- [ ] **054** — Implement durable supervised jobs and validation handoff. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/054-pesquisa-arquitetura.md) · commit: pendente
- [ ] **055** — Review and correct durable supervised jobs and validation handoff. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/055-pesquisa-arquitetura.md) · commit: pendente
- [ ] **056** — Implement read-only watchdog and guarded runner recovery. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/056-pesquisa-arquitetura.md) · commit: pendente
- [ ] **057** — Review and correct read-only watchdog and guarded runner recovery. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/057-pesquisa-arquitetura.md) · commit: pendente
- [ ] **058** — Implement incremental log scanning, digest and artifact retention. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/058-pesquisa-arquitetura.md) · commit: pendente
- [ ] **059** — Review and correct incremental log scanning, digest and artifact retention. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/059-pesquisa-arquitetura.md) · commit: pendente
- [ ] **060** — Implement read-only observer and diagnostic assistant. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/060-pesquisa-arquitetura.md) · commit: pendente
- [ ] **061** — Review and correct read-only observer and diagnostic assistant. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/061-pesquisa-arquitetura.md) · commit: pendente
- [ ] **062** — Implement plan-free monitored validation and repair. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/062-pesquisa-arquitetura.md) · commit: pendente
- [ ] **063** — Review and correct plan-free monitored validation and repair. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/063-pesquisa-arquitetura.md) · commit: pendente
- [ ] **064** — Implement telemetry, shadow routing and non-inferiority benchmarks. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/064-pesquisa-arquitetura.md) · commit: pendente
- [ ] **065** — Review and correct telemetry, shadow routing and non-inferiority benchmarks. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/065-pesquisa-arquitetura.md) · commit: pendente
- [ ] **066** — Implement installer, configuration, packaging and cross-platform CI. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/066-pesquisa-arquitetura.md) · commit: pendente
- [ ] **067** — Review and correct installer, configuration, packaging and cross-platform CI. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/067-pesquisa-arquitetura.md) · commit: pendente
- [ ] **068** — Implement provider-switch contract fixtures from the prepared decision. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/068-pesquisa-arquitetura.md) · commit: pendente
- [ ] **069** — Review and correct provider-top switching and evidence-bounded handoff design. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/069-pesquisa-arquitetura.md) · commit: pendente
- [ ] **070** — Implement opt-in provider-switch configuration and migration. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/070-pesquisa-arquitetura.md) · commit: pendente
- [ ] **071** — Review and correct opt-in provider-switch configuration and migration. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/071-pesquisa-arquitetura.md) · commit: pendente
- [ ] **072** — Implement distinct effective rungs and provider-phase state. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/072-pesquisa-arquitetura.md) · commit: pendente
- [ ] **073** — Review and correct distinct effective rungs and provider-phase state. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/073-pesquisa-arquitetura.md) · commit: pendente
- [ ] **074** — Implement coherent switching, availability and attempt reservation. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/074-pesquisa-arquitetura.md) · commit: pendente
- [ ] **075** — Review and correct coherent switching, availability and attempt reservation. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/075-pesquisa-arquitetura.md) · commit: pendente
- [ ] **076** — Implement bounded deterministic handoff and sanitation. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/076-pesquisa-arquitetura.md) · commit: pendente
- [ ] **077** — Review and correct bounded deterministic handoff and sanitation. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/077-pesquisa-arquitetura.md) · commit: pendente
- [ ] **078** — Integrate attempt-bound handoff in both worker prompts. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/078-pesquisa-arquitetura.md) · commit: pendente
- [ ] **079** — Review and correct attempt-bound handoff in both worker prompts. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/079-pesquisa-arquitetura.md) · commit: pendente
- [ ] **080** — Complete provider-switch documentation, replay and cost evidence. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/080-pesquisa-arquitetura.md) · commit: pendente
- [ ] **081** — Review and correct provider-switch evidence. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/081-pesquisa-arquitetura.md) · commit: pendente
- [ ] **087** — Implement direct architecture delegation with economical implementation. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/087-pesquisa-arquitetura.md) · commit: pendente
- [ ] **088** — Review and correct direct architecture delegation with economical implementation. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/088-pesquisa-arquitetura.md) · commit: pendente
- [ ] **089** — Implement avoid skill loading for routine commands and trivial changes. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/089-pesquisa-arquitetura.md) · commit: pendente
- [ ] **090** — Review and correct avoid skill loading for routine commands and trivial changes. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/090-pesquisa-arquitetura.md) · commit: pendente
- [ ] **091** — Implement create bounded repair tasks for complex active-plan blockers. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/091-pesquisa-arquitetura.md) · commit: pendente
- [ ] **092** — Review and correct create bounded repair tasks for complex active-plan blockers. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/092-pesquisa-arquitetura.md) · commit: pendente
- [ ] **093** — Implement verify authorized unsandboxed access for implementing agents. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/093-pesquisa-arquitetura.md) · commit: pendente
- [ ] **094** — Review and correct verify authorized unsandboxed access for implementing agents. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/094-pesquisa-arquitetura.md) · commit: pendente
- [ ] **095** — Implement offer other-provider setup and login before creating a plan. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/095-pesquisa-arquitetura.md) · commit: pendente
- [ ] **096** — Review and correct offer other-provider setup and login before creating a plan. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/096-pesquisa-arquitetura.md) · commit: pendente
- [ ] **097** — Implement make console, progress and end-user docs concise and precise. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/097-pesquisa-arquitetura.md) · commit: pendente
- [ ] **098** — Review and correct make console, progress and end-user docs concise and precise. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/098-pesquisa-arquitetura.md) · commit: pendente
- [ ] **099** — Implement semantic progress and safe five-minute stall recovery. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/099-pesquisa-arquitetura.md) · commit: pendente
- [ ] **100** — Review and correct semantic progress and stall recovery. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/100-pesquisa-arquitetura.md) · commit: pendente
- [ ] **101** — Implement plan-scoped cross-platform sleep inhibition. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/101-pesquisa-arquitetura.md) · commit: pendente
- [ ] **102** — Review and correct plan-scoped sleep inhibition. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/102-pesquisa-arquitetura.md) · commit: pendente
- [ ] **103** — Implement opt-in plan-scoped 20-minute recovery scheduler. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/103-pesquisa-arquitetura.md) · commit: pendente
- [ ] **104** — Review and correct opt-in plan-scoped keepalive scheduler. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/104-pesquisa-arquitetura.md) · commit: pendente
- [ ] **105** — Add the opt-in frontier tier L6/F6 on top of map 2026-11-20-v8. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/105-pesquisa-arquitetura.md) · commit: pendente
- [ ] **106** — Review and correct updated model catalog and frontier routing. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/106-pesquisa-arquitetura.md) · commit: pendente
- [ ] **107** — Implement risk-based security/performance architecture review and code-review lenses. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/107-pesquisa-arquitetura.md) · commit: pendente
- [ ] **108** — Independently review and correct architecture security/performance gates. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/108-pesquisa-arquitetura.md) · commit: pendente
- [ ] **109** — Implement complete test-failure inventory, focused repair and final full-suite gate. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/109-pesquisa-arquitetura.md) · commit: pendente
- [ ] **110** — Independently review and correct batched failure-repair validation. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/110-pesquisa-arquitetura.md) · commit: pendente
- [ ] **111** — Implement risk-layered test authoring and deterministic impact-scoped validation. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/111-pesquisa-arquitetura.md) · commit: pendente
- [ ] **112** — Independently review and correct test hierarchy and impact selector. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/112-pesquisa-arquitetura.md) · commit: pendente
- [ ] **113** — Implement opt-in legacy or current-plan test audit and guarded refactoring. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/113-pesquisa-arquitetura.md) · commit: pendente
- [ ] **114** — Independently review and correct test-audit authorization and ownership. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/114-pesquisa-arquitetura.md) · commit: pendente
- [ ] **115** — Implement preferred-provider priority restoration and durable quota resume. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/115-pesquisa-arquitetura.md) · commit: pendente
- [ ] **116** — Independently review provider preference recovery and quota wake. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/116-pesquisa-arquitetura.md) · commit: pendente
- [ ] **117** — Implement contract-grounded AI test oracles and defect-detection checks. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/117-pesquisa-arquitetura.md) · commit: pendente
- [ ] **118** — Independently review AI test oracle quality and efficiency. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/118-pesquisa-arquitetura.md) · commit: pendente
- [ ] **119** — Enforce economical phase routing and minimal source-bound task context. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/119-pesquisa-arquitetura.md) · commit: pendente
- [ ] **120** — Independently review task-wide economical routing and context safety. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/120-pesquisa-arquitetura.md) · commit: pendente
- [ ] **121** — Implement opt-in UI/UX design system, identity and compact agent memory. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/121-pesquisa-arquitetura.md) · commit: pendente
- [ ] **122** — Independently review visual identity, design token and agent context safety. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/122-pesquisa-arquitetura.md) · commit: pendente
- [ ] **123** — Implement optional real-component or Node Vite HTML JavaScript SCSS prototype lab and safe transfer plan. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/123-pesquisa-arquitetura.md) · commit: pendente
- [ ] **124** — Independently review prototype isolation and guarded production migration. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/124-pesquisa-arquitetura.md) · commit: pendente
- [ ] **125** — Implement visual usability accessibility and responsive quality gates with pae ux CLI. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/125-pesquisa-arquitetura.md) · commit: pendente
- [ ] **126** — Independently review full UI/UX quality, consent, economy and integration. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/126-pesquisa-arquitetura.md) · commit: pendente
- [ ] **127** — Implement one-time project onboarding, source-derived coding standards documentation and CLI. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/127-pesquisa-arquitetura.md) · commit: pendente
- [ ] **128** — Independently review coding-standard discovery, consent, documentation and CLI safety. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/128-pesquisa-arquitetura.md) · commit: pendente
- [ ] **129** — Integrate pattern-first code reuse, scoped retrieval and architectural drift checks into implementation and review. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/129-pesquisa-arquitetura.md) · commit: pendente
- [ ] **130** — Independently review source-backed pattern enforcement, safe exceptions and token economy. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/130-pesquisa-arquitetura.md) · commit: pendente
- [ ] **131** — Implement manager-tier delegation for plan supervision decisions. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/131-pesquisa-arquitetura.md) · commit: pendente
- [ ] **132** — Independently review manager-tier delegation for plan supervision. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/132-pesquisa-arquitetura.md) · commit: pendente
- [ ] **082** — Integrate all implemented contracts and close cross-feature gaps. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/082-pesquisa-arquitetura.md) · commit: pendente
- [ ] **083** — Review and correct end-to-end integration. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/083-pesquisa-arquitetura.md) · commit: pendente
- [ ] **084** — Validate release contents, documentation and migration. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/084-pesquisa-arquitetura.md) · commit: pendente
- [ ] **085** — Review and correct release-readiness evidence. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/085-pesquisa-arquitetura.md) · commit: pendente
- [ ] **086** — Final whole-skill implementation review and handoff. [Relatório](docs/research/20261028-skill-optimization/pesquisas-por-task/086-pesquisa-arquitetura.md) · commit: pendente

## Registro de retomada e anomalias

- 2026-11-20 — guia inicial criado a partir de `TODO.md`. O plano antigo conserva relatórios já preparados por tema; toda task pendente exige vínculo individual e comprovação própria.
- **Conferência necessária**: o índice `TODO.md` inclui 131/132, mas a listagem de `.ai-work/.../tasks/` consultada durante o bootstrap terminava em 130. Antes de pesquisar 131/132, verifique se as definições e o manifest já foram atualizados; se faltarem, recupere do plan-spec ou registre impedimento sem marcar [x].
