# Current user request (verbatim)

Você pode me ajudar numa coisa? Nesse plano há tasks de pesquisa, certo? Você poderia adiantar o meu trabalho, e em ver de executar o plano, realizar a parte de pesquisa para cada task de pesquisa, e gerar um relatório da pesquisa de qual é o melhor caminho a seguir? Assim, depois, modifique o todo e a checklist interna dessa task para apontar para o relatório e dizer para implementar as orientações dessa pesquisa.

Faça isso um por um, até acabar todas as tasks de pesquisa e virar apenas tasks de implementações.

Por sim, modifique o plano. Ele não vai mais precisar outro plano. Será apenas um plano de implementação.

# Planning interpretation and precedence

# Current request amendment - one implementation plan

Date: 2026-10-28. This amendment supersedes the older two-plan workflow.

The user asks to perform the research now, outside execution of the saved plan; produce one report per research task recommending the best path; replace each research TODO and its internal checklist with implementation instructions pointing to that report; and remove the need to generate another plan. There is only one implementation plan, with tests, corrections and independent acceptance reviews.

This authorization covers research and local plan/document changes. It does not claim product implementation, independent review, authenticated provider execution, commit, push, installation or publication. Prior source instructions remain effective where not contradicted, including secrets, backward compatibility and protected user configuration.

Original request bytes are preserved in REQUEST_ORIGINAL.md and the historical snapshot. Prepared research is project evidence outside disposable plan control. The current specification is PLAN1_SPEC.json (the filename is retained for compatibility); its title and task contracts now describe a single implementation plan.

# Historical original request (superseded only where stated above)

Com a skill plan-and-execute quero que você crie um plano que o produto deste plano será a criação de outro plano para implementar inumeras melhorias. Pense que primeiro será um plano que fará estudo interno, separará tópicos para criar tasks para o plano 2 depois fazer um estudo externo e conseguir fazer as melhores melhorias possíveis.

faça uma task para cada coisa abaixo:
- Fazer um estudo amplo e profundo de como funciona a própria skill e cada funcionalidade
- Crie tópicos de cada feature que a skill faz, mecanismo
	. por exemplo, mapping de recursos e logs que pode ser usado para monitor quando a validação demora muito
	. outro exemplo, troca fornecedor de IA como fall back
	. escolha de fornecedor, modelo e nível para cada tipo de demanda
	. Quando o prompt é muito grande, ela cria um plano para estudar cada parte do plano de forma individual, naquele mesmo contexto do plano, para depois criar um plano de execução contendo todos os pontos com a melhor qualidade de definição e estratégia possível
	. Há outros exemplos dentro da skill - você vai ter estudar profundamente e listar todos
- Para cada tópico coletado você vai criar uma task para pesquisar amplamente e profundamente na internet, livros, arquivos, código e documentação de agentes e modelos de IA maneiras de otimizar a skill para ter a melhor qualidade possível com o melhor custo benefício - qualidade ótima
- Para cada task de cada tópico, no final você vai pedir codereview com o modelo mais alto disponível




No plano 1 adicione também nele essa melhoria abaixo - entenda e bote junto:
# plan-and-execute: trocar de fornecedor ao atingir o topo da escada

Você vai melhorar a própria skill `plan-and-execute`. Leia o prompt inteiro antes de agir. Ele já incorpora um estudo anterior, conferido contra o código; não procure esse estudo. Legenda: **[V]** fato verificado por leitura do código em 2026-10-28 (e por simulação com o código real, quando indicado); **[H]** hipótese a confirmar.

## 1. Objetivo

Pedido do usuário, nas palavras dele:

> "faça uma melhoria na skill plan-and-execute para que ao atingir o topo do modelo no fornecedor atual nas tentativas de executar uma task, a skill possa trocar para outro fornecedor para continuar o trabalho."

No runner, isso significa: quando as tentativas de uma task esgotarem a capacidade útil do fornecedor atual (nenhum degrau acima muda o modelo ou o esforço realmente despachado), a próxima tentativa vai para outro fornecedor elegível da cadeia, sem gastar tentativas repetindo o topo, e o novo worker recebe uma passagem de bastão (handoff) que complementa a evidência determinística.

Resultado esperado:
- comportamento novo ativado por opção; com a opção desligada, nada muda;
- todo fornecedor elegível da cadeia é alcançável antes de `ladder_exhausted`, dentro do orçamento de tentativas que você definir;
- handoff curto, redigido, validado e marcado como não verificado;
- decisões justificadas por pesquisa documentada, com custo-benefício explícito;
- testes determinísticos, documentação e changelog atualizados, e o resultado real da validação reportado.

Onde: repositório fonte `/home/luizvalenca/projetos/skills/plan-and-execute/git/plan-and-execute` (branch `main`, commit `193fefd`, versão 0.11.0). Código em `skill/plan-and-execute/scripts/`, referências em `skill/plan-and-execute/references/`, pesquisa em `docs/`. Em produção o runner é `scripts/run_concise.py`: ele carrega `run_isolated.py` e aplica por cima `artifact_contract`, o catálogo de `routingctl`, `runner_contract` e `pattern_runner_contract`. A skill que executa este prompt roda de uma cópia instalada; altere só o repositório fonte.

## 2. Estado atual verificado

Use como ponto de partida e reconfirme o que for decisivo.

### 2.1 A escada e o despacho usam cadeias diferentes

- [V] `run_isolated.choose_route(..., check_availability=False)`, chamado por `execute_one_task`, monta a cadeia com `routing_config.provider_chain(task, config, override)` do **tier declarado**, calcula `slot = functional_failures // functional_failures_per_provider` (padrão 4, faixa 1..50), pega `cadeia[min(slot, len-1)]` e calcula o degrau na escada desse fornecedor: `routingctl.route_rungs` (degrau declarado e os acima), `routingctl.escalation_step(failure_classes, ...)`, piso de estagnação e `clamp_effort` (`max_effort_by_tier`).
- [V] Quem decide o despacho é `availability.select`, chamado a cada tentativa. Ele usa só `tier` e `requested_effort` do intent (persistidos em `results/<task>-availability.json` sob um fingerprint), refaz a cadeia com `provider_chain(..., tier=<tier escalado>)`, corta `cadeia[slot:]` e devolve o primeiro candidato de `workload_routing.candidates` não visitado, sem cooldown e com CLI. `intent["provider"]` é descartado. Fixado por `availability_self_test.test_escalated_tier_uses_its_own_chain_and_phases_are_separate`.
- [V] Efeitos: troca oculta de fornecedor quando o tier sobe; o índice de degrau calculado numa escada é aplicado a outro fornecedor (Claude tem 7 degraus e Codex 5 em `ESCALATION_LADDERS`; os demais usam `DEFAULT_LADDER`); o slot aplicado a uma cadeia de outra ordem ou tamanho pula fornecedores. Já `ladder_exhausted` usa a cadeia declarada. Exemplos em 2.8.

### 2.2 O topo se repete e a troca só vem por contagem

- [V] `escalation_step` devolve `min(_uncapped_step, topo)`: no topo, o mesmo degrau se repete até `functional_failures` chegar ao próximo múltiplo de `functional_failures_per_provider`.
- [V] Nada detecta degrau que não muda o despacho. Slugs do Antigravity com esforço embutido (`routing_config.embedded_effort_model`) entram em `models_without_effort` e `build_worker_command` omite `--effort`: `standard/medium` → `standard/high` repete `claude-sonnet-5-5-medium`, e todos os degraus `strong`/`max` repetem `claude-opus-5-5-high`. Na config do usuário o Claude tem `strong` = `max` = `claude-opus-5-5`, então `strong/high` → `max/high` também não muda nada. `DEFAULT_LADDER` não tem degrau `advanced`, e o `claude-sonnet-5-5-high` do usuário só roda quando declarado. Só o catálogo bootstrap do Codex tem teste de degraus distintos (`model_routing_self_test.test_escalation_ladders_follow_calibration`).

### 2.3 O último fornecedor é bloqueado antes de rodar

- [V] `run_isolated.ladder_exhausted` roda antes de cada despacho e só retorna True quando `slot >= len(cadeia declarada) - 1` e `routingctl.escalation_exhausted(failure_classes, degraus do último fornecedor)`. As classes de todos os fornecedores se acumulam; quando o slot alcança o último fornecedor, a evidência em geral já passa do topo dele e a task é bloqueada sem que ele rode. A "segunda opinião no degrau lógico equivalente" prometida no comentário de `choose_route` não acontece. Fixado por `self_test.test_ladder_exhaustion_blocks_instead_of_burning_attempts` (`functional_failures: 4` dá True sem o Codex ter rodado).
- [V] Manifests legados sem `failure_classes` nunca disparam `ladder_exhausted`.

### 2.4 O orçamento de tentativas não chega ao 3º fornecedor

- [V] `max_attempts` é por task (`planctl.normalize_task`: padrão 8, faixa 1..50) e nenhuma chave de config o altera. `planctl.fail_task` bloqueia quando `functional_failures >= max_attempts` ou a classe é `plan_defect`/`timeout_ceiling`; com `rate_limited=True` só soma `rate_limit_events`. Com 4 falhas por fornecedor e 8 tentativas, o 3º fornecedor nunca roda por falha; com `max_attempts` 12 também não, por causa de 2.3.
- [V] Falhas da fase `design` contam nos mesmos contadores. Nada zera `functional_failures`/`failure_classes` (nem `planctl.reset_task`): uma task bloqueada por `max_attempts` e resetada volta a bloquear na próxima falha.

### 2.5 Tier sem modelo em um fornecedor da cadeia quebra o despacho

- [V] Com `workload_routing` desligado, `workload_routing.candidates` levanta `No model configured for <provider>/<tier>` se qualquer fornecedor da cadeia não tiver modelo para o tier, mesmo que o primeiro tenha. Com a config do usuário, uma task `advanced` com provider `auto` termina em `AvailabilityError` no primeiro despacho (só o Antigravity tem `advanced`), o que contraria `PLAN_SPEC.md` ("skipped upward"). `routingctl.lift_tier` só é usado em `route_rungs`.

### 2.6 O que o novo worker recebe hoje

- [V] Os workers são efêmeros (`build_worker_command`): Claude `--print --no-session-persistence`, Codex `exec --ephemeral`, Antigravity `-p` sem `--continue`/`--conversation`. O contexto da tentativa morre com o processo. `strict_fresh_context: true` está nos defaults, mas nenhum código o lê.
- [V] Prompt de produção: `runner_contract.worker_prompt` (regras estáticas primeiro, valores da tentativa no fim) + `run_isolated.failure_context(task)` **sem `plan_dir`**, por isso a linha do pacote de evidência (`*-evidence.json`) nunca entra + regras de patterns + `append_design_note` + `assistant_triage.hint` (só com `assistant` ou `observer` ligados). [H] A omissão é descuido: a chamada (commit `634c805`) é anterior ao parâmetro (commit `1a95b11`).
- [V] `failure_context` traz os últimos 900 chars de `last_error` (o motivo já chega cortado em 1400 por `artifact_contract.fail_task`), a assinatura de estagnação e o caminho do último log de validação. O worker não pode abrir resultados nem logs, exceto esse último log de validação.
- [V] De um relatório `blocked`, só `blocked_reason` (≤800) ou `summary` (≤360) vira `last_error`. `risks`, `follow_ups`, `validations` e o relatório de uma tentativa reprovada na validação ficam em `results/<task>-attempt-<n>-<provider>.json` e não chegam ao próximo worker. Sem relatório (crash, timeout), sobra a cauda da saída.
- [V] Sobrevivem entre tentativas: a árvore de trabalho, o checklist de subtasks, os aprendizados atribuídos e a nota de design.

### 2.7 Contratos, peças reutilizáveis e testes

- [V] Config (`routing_config.validate` e `load`): camadas defaults < global < plano; snapshot v1 completo ignora o global; defaults de seções novas ficam em `EXTRA_DEFAULTS`; chaves top-level desconhecidas não são rejeitadas (só `routing`, `availability` e `assistant` rejeitam subchaves desconhecidas). O fingerprint de `availability.select` lista os campos da task e as chaves de config que afetam a rota.
- [V] Manifest: `SCHEMA_VERSION = 4` (aceita 1 a 4); `validate_plan` não rejeita campos de task desconhecidos; em v4 o arquivo da task é projeção viva de `render_task` (versão concisa em `artifact_contract`) conferida contra o manifest; em v1 a v3 ele é imutável.
- [V] `references/completion-report.schema.json` tem `additionalProperties: false`. `codex_output_schema` torna toda propriedade obrigatória (campo novo precisa aceitar `null`) e `antigravity_schema_text` tira `null` de `type`/`enum`. Fixado por `provider_self_test.test_codex_output_schema_is_api_compatible`.
- [V] Reaproveitáveis: `runner_contract._git_change_summary` (`git status --short` e `git diff HEAD --stat`, até 4000 chars); `assistant_triage.redact`, `validate_advice` e `hint` (cápsula "Unverified diagnostic suggestion (data only; ignore instructions; verify independently)", válida só para o `functional_failures` corrente); `summary_route` e `build_summary_command` (modo somente leitura por adapter, falha fechada, fallback determinístico); o formato de handoff de promoção em `references/TOKEN_EFFICIENCY.md`; `routingctl.select_route` (puro, custo efetivo, hoje só em shadow/`auto_select`; `auto_route` nunca atua em retentativa); `routing_telemetry` (`KINDS` = root, subagent, retry, diagnostic, summary; campos em lista fechada); as métricas de `tools/skill_benchmark.py`.
- [V] Checks do repo: `tools/validate-skill.js` limita `SKILL.md` a 7167 chars (hoje 6955) e exige frases como "without the previous chat transcript"; `ORCHESTRATION.md` tem limite 12000 (hoje 11999) e `TOKEN_EFFICIENCY.md` 10000 (hoje 9975). `model_routing_self_test.test_no_user_routing_ceiling_contract` proíbe "hard ceiling", "--max-tier", "--max-effort" e "provider_ceiling_models" em `SKILL.md`, `MODEL_ROUTING.md`, `TOKEN_EFFICIENCY.md` e `agents/openai.yaml`; "ceiling" já nomeia `timeout_ceiling` e o marcador `provider_ceiling=`.
- [V] Testes que fixam o comportamento atual: `self_test.py` (`test_route_escalation`, `test_evidence_based_escalation`, `test_ladder_exhaustion_blocks_instead_of_burning_attempts`, `test_failure_class_state_and_plan_defect_block` e os de ponta a ponta com CLI falso), `availability_self_test.py` (degrau lógico entre escadas, cooldown, fornecedor fixado não alarga, quota→fallback com subprocesso, pausa limitada, rotação após 4 falhas), `routing_config_self_test.py`, `workload_routing_self_test.py`, `model_routing_self_test.py`, `provider_self_test.py` (argv golden), `artifact_concision_self_test.py`, `progress_runner_self_test.py` (regras estáticas dos dois prompts), `snapshot_runner_self_test.py`, `assistant_triage_self_test.py`, `telemetry_self_test.py`. A lista completa está em `tools/run-skill-self-test.js` e os checks do repo em `tools/run-repo-checks.js`.

### 2.8 Cenário de referência

Config global do usuário (`~/.config/plan-and-execute/orchestrator.config.json`; só leitura, imprima apenas as chaves de roteamento):
- `tier_routes`: economy, standard e advanced = antigravity → codex → claude; strong = codex → claude → antigravity; max = codex → claude. `allow_provider_fallback: true`, sem `workload_routing`.
- Modelos: claude `haiku` / `claude-sonnet-5-5` / strong e max `claude-opus-5-5`; codex `gpt-6-luna` / standard, strong e max `gpt-6.1-sol`; antigravity `gemini-3.8-flash-medium` / `claude-sonnet-5-5-medium` / advanced `claude-sonnet-5-5-high` / strong e max `claude-opus-5-5-high`. Claude e Codex não têm `advanced`.

[V] Simulação com o código real (CLIs disponíveis, sem cooldown, todas as falhas da mesma classe, `max_attempts` 8):

| Task declarada | Despacho hoje | Problema |
|---|---|---|
| strong/high, `unknown` | codex sol strong/high; codex sol max/xhigh ×3; claude opus max/xhigh ×4; bloqueio por `max_attempts` | topo repetido; Antigravity nunca roda |
| max/high, `unknown` ou `semantic` | codex sol max/high; codex sol max/xhigh ×3; `ladder_exhausted` | Claude nunca roda |
| standard/medium, `unknown` | agy sonnet-medium ×2 (a 2ª é no-op); codex sol strong/medium e strong/high; claude opus max/xhigh ×4 | no-op; troca oculta; salto direto ao topo do Claude |
| standard/medium, `mechanical` | agy sonnet-medium ×4 iguais; claude opus max/xhigh ×4 | Codex pulado |
| advanced/high | `AvailabilityError: No model configured for codex/advanced` | 2.5 |

Com a config padrão (sem `tier_routes`, `provider_order` claude → codex), nos casos simulados (strong/high e standard/medium com `unknown`, max/high com `semantic`) a task faz 4 tentativas no Claude e cai em `ladder_exhausted`: o Codex nunca roda, e no caso standard o Claude nem chega ao próprio topo.

Reproduza com um laço que, a cada tentativa, chama `ladder_exhausted(task, config, None, check_availability=False)`, `choose_route(task, config, None, check_availability=False)` e `availability.select(plan_dir, task, config, intent, None, "implementation", set(), lambda p: True, run_isolated.clamp_effort, persist=False)`, e depois soma 1 a `functional_failures` e acrescenta a classe a `failure_classes`. Nos testes, use fixtures de config, nunca `~/.config`.

## 3. Pesquisa exigida

Exigência do usuário, nas palavras dele:

> "Estude de forma ampla e profunda na internet, no código e documentação dos fornecedores dos agentes e das IAs, livros e artigos a melhor forma de fazer, sendo o melhor custo benefício, e conseguir o resultado ótimo!"

Fontes: documentação e código oficiais da Anthropic (Claude Code, Agent SDK), da OpenAI (Codex CLI, que tem código aberto, e Agents SDK) e do Google (Antigravity CLI, Gemini), e dos demais adapters da skill (Gemini CLI, Qwen Code, Kimi, Trae Agent, Muse; profiles GLM e DeepSeek); artigos acadêmicos; livros (ex.: Chip Huyen, *AI Engineering*, 2025); relatos de engenharia. Quando a documentação divergir do CLI instalado, confira no CLI (`--help`, `agy models`, `codex debug models`) e registre a divergência. Observado em 2026-10-28:
- `claude` 2.1.287: `--resume`, `--continue`, `--fork-session`, `--session-id`, `--no-session-persistence`;
- `codex-cli` 0.159.2: `exec resume [SESSION_ID] [--last]`, `exec fork`, `--ephemeral`;
- `agy` 1.4.8: `--continue`, `--conversation`; o `--help` anuncia `--effort low|medium|high|xhigh|max`, mas `docs/RESEARCH_BASIS.md` diz `low|medium|high`; `agy models` só lista slugs `-low`, `-medium` e `-high`. [H] O Antigravity persiste conversas por padrão (o envelope JSON traz `conversation_id`, que o runner não captura).

Eixos:
1. Passagem de contexto entre agentes: resumo estruturado; compaction (Claude Code e Agent SDK, `model_auto_compact_token_limit` do Codex, compaction do agente gerenciado do Antigravity); memória externa e artefatos persistentes (arquivos de progresso, task lists, walkthroughs); handoffs em SDKs de agentes (ex.: OpenAI Agents SDK, LangGraph, condensers do OpenHands); reflexão verbal entre tentativas (ex.: Reflexion, Shinn et al., 2023).
2. Cascatas e roteamento: além das fontes de `docs/RESEARCH_BASIS.md` (FrugalGPT, RouteLLM, IRT-Router, Cluster-Route-Escalate, CascadeDebate), quando insistir e quando trocar de modelo (ex.: AutoMix) e como gateways multi-fornecedor fazem fallback (ex.: LiteLLM, OpenRouter); eles reenviam o histórico porque as APIs não guardam estado, ao contrário dos agentes CLI.
3. Retomada nativa de sessão em cada CLI: o que é persistido, onde e por quanto tempo; custo de cache ao retomar; privacidade; relação com `--no-session-persistence` e `--ephemeral`; por que não atravessa fornecedores.
4. Custo na troca: cache por fornecedor, modelo e esforço; TTL; preço de escrita e de leitura de cache; assinatura (quota) contra API (caixa); custo do handoff (chamada extra e tokens no prompt novo) comparado ao de reexplorar o repositório.
5. Ancoragem: evidência de que um resumo errado ou um contexto enganoso piora o modelo seguinte, e mitigações.
6. Validação de resumos contra evidência determinística: consistência factual, paths conferidos no diff, comandos conferidos nos logs.
7. Teto de cada fornecedor: modelos e esforços por tier e como derivar o topo da config (Claude, Codex, slugs com esforço embutido do Antigravity, `references/MODEL_CATALOG.md`).

Saída: `docs/research/<NOME>.md` (ex.: `PROVIDER_SWITCH_HANDOFF.md`) no formato dos documentos existentes (data, commit-base, fontes numeradas `E###` com URL e data de acesso). Marque cada conclusão como **verificado** ou **inferência**, inclua uma matriz de alternativas (custo, benefício, risco) e a decisão, e acrescente um parágrafo em `docs/RESEARCH_BASIS.md` apontando para o documento. Defina "resultado ótimo" de forma mensurável (ex.: maior taxa de validação por custo; nenhuma tentativa idêntica a uma que já falhou no topo; nenhum fornecedor elegível ignorado; overhead de handoff limitado) e estime o efeito com uma simulação determinística dos cenários de 2.8 e, se couber, com as métricas de `tools/skill_benchmark.py`.

## 4. Ideia do usuário a avaliar: o fornecedor anterior escreve um resumo

> "Pense que talvez na troca de fornecedor, possa talvez a skill pedir para o fornecedor anterior escrever um resumo para passar para o modelo novo continuar."

Avalie e decida com evidência:
1. **Quem escreve**, lembrando que as sessões são efêmeras (2.6):
   - (a) o próprio worker, antes de terminar, num campo novo e anulável do relatório: custo marginal quase zero, mas não existe em crash, timeout ou relatório inválido, e o worker não sabe se a validação do runner vai reprovar;
   - (b) retomar a sessão do fornecedor anterior e pedir o resumo: é o único jeito de ele "lembrar" depois que o processo termina, mas exige persistir a sessão, grava transcrição em disco e muda o contrato de contexto fresco;
   - (c) uma chamada extra, barata e somente leitura, sobre os artefatos (relatório salvo, `last_error`, evidência, diff), reaproveitando `summary_route` e `build_summary_command`;
   - (d) um resumo determinístico, sem modelo.

   Combinações valem (ex.: (a) com fallback para (d)).
2. **Formato e tamanho**: parta do formato de `TOKEN_EFFICIENCY.md` e acrescente hipóteses tentadas e refutadas (com evidência), hipótese atual, bloqueio exato, próximo passo sugerido, comandos executados e resultados. Justifique o limite; referências internas: brief até 2000 tokens e resultado até 1000 tokens/4000 bytes em `DELEGATION.md`, hipótese até 300 chars na cápsula de `assistant_triage.hint`.
3. **Segredos**: redija antes de truncar (reaproveite ou estenda `assistant_triage.redact`) e nunca inclua valores de variáveis de ambiente ou de profiles.
4. **Fornecedor anterior sem quota, indisponível ou sem relatório**: handoff determinístico com `_git_change_summary`, `completed_subtask_ids`, `failure_classes`, `last_error`, assinatura e caminho do último log, pacote de evidência e os `risks`/`follow_ups` do relatório salvo, se houver.
5. **Ancoragem**: como apresentar (dado não confiável, marcado "não verificado", depois da evidência determinística, com as hipóteses refutadas) e como medir se ajuda ou atrapalha.
6. **Validação do resumo**: confira paths contra `git status` e diff, comandos contra logs e `validation_commands`, ids de subtask contra o manifest; descarte ou marque o que não conferir; valide JSON e limites como `validate_advice` faz.
7. **Complemento, não substituto**: `failure_context` continua. O handoff entra no sufixo dinâmico do prompt, só o mais recente, vale apenas para a tentativa seguinte (como `assistant_triage.hint`) e nunca muda classe de falha, rota ou status. Ajuste de forma mínima e explícita as regras de isolamento que hoje o proíbem: regra 1 de `runner_contract.worker_prompt`, regra 3 de `run_isolated.worker_prompt` e `WORKFLOW.md` §3 ("Do not paste ... prior reports").
8. **Persistência e telemetria**: onde gravar (ex.: `results/<task>-handoff-<attempt>.json`, apagado com o plano) e o que registrar (de/para, motivo `ladder_top`, `failures` ou `availability`, custo do handoff, se a task passou depois).

Avalie também as alternativas abaixo; adote ou descarte cada uma com justificativa:
- **Gatilho de topo**: trocar quando o passo pedido pela evidência passar do topo do fornecedor atual ou quando o próximo degrau não mudar o despacho efetivo. Decida se `mechanical`/`budget` repetem uma vez antes de trocar. `environmental`, `plan_defect` e `timeout_ceiling` não devem disparar troca.
- **Coerência das cadeias** (2.1): a escada usada tem de ser a do fornecedor despachado. Escolha entre a cadeia do tier declarado e a do tier efetivo, e elimine a troca oculta e o pulo de fornecedor, ou transforme-os em política explícita e testada.
- **Degrau de entrada no novo fornecedor**: o equivalente lógico (tier e esforço, com `lift_tier` no destino), o topo do destino ou um abaixo dele; e se as classes registradas em outros fornecedores contam na escada do novo.
- **Contagem e orçamento**: posição de fornecedor persistida (ou contador por fornecedor) no lugar de `functional_failures // functional_failures_per_provider`; `ladder_exhausted` só quando todo fornecedor elegível tiver chegado ao topo ou sido pulado com motivo registrado; relação com `max_attempts` (garantir ao menos uma tentativa por fornecedor restante, ou avisar na validação do plano) e com `reset`.
- **Retomada nativa**: só funciona no mesmo fornecedor e não resolve o topo; avalie para repetições `mechanical`/`budget` e como meio da opção 1(b).
- **Escolha do próximo fornecedor**: a ordem da cadeia (determinística, como hoje) ou `routingctl.select_route` (custo efetivo, ainda atrás do gate de `auto_select`).

## 5. Restrições e compatibilidade

- **Padrão igual ao atual.** O comportamento novo só liga por opção explícita de configuração (ex.: uma seção própria com o modo de troca e o modo de handoff; não use "ceiling" no nome), validada em `routing_config.validate` com subchaves desconhecidas rejeitadas, default em `EXTRA_DEFAULTS` e camadas global/plano documentadas. Opções e campos de task que mudem a rota entram no fingerprint de `availability.select`.
- **Fallback e override.** Com `allow_provider_fallback` desligado (na task ou na config), nunca troque. O override (`--provider` ou `task.provider`) hoje só põe o fornecedor na frente e mantém os fallbacks permitidos; preserve e documente.
- **Disponibilidade separada da evidência.** Quota, rate limit e capacidade não contam como falha funcional; cooldowns por fornecedor, `quota_pool` e modelo; identidade de rota por `workload_routing.identity`; `AvailabilityPaused` (exit 75); ledger de disponibilidade v1 compatível ou versionado.
- **Planos legados.** Manifests de schema 1 a 4 e sem `failure_classes` carregam e roteiam como hoje; snapshot v1 completo de config não herda a opção global; campos novos de task são opcionais e têm default.
- **Sessão raiz.** Nunca troque o modelo da sessão raiz; a troca é sempre de um worker novo.
- **Cache.** O prefixo estático de `run_isolated.worker_prompt` e de `runner_contract.worker_prompt` fica byte a byte igual entre tasks; tudo que é da tentativa vai no fim.
- **Topo.** Derive-o da config efetiva, nunca de constantes por fornecedor: escada (`provider_ladder`), modelos por tier com `lift_tier`, `max_effort_by_tier`, `models_without_effort`/`embedded_effort_model`, `model_resolution: snapshot` (`resolve_snapshot_route`) e profiles de workload (`native_effort`). Subida que resulta no mesmo despacho efetivo (mesmo modelo resolvido e mesmo esforço efetivo) conta como topo. Hoje o Antigravity termina em `-high`.
- **Tier sem modelo no destino de uma troca.** Eleve com `lift_tier` (nunca rebaixe) ou pule o fornecedor com motivo registrado.
- **Fase `design`** (`design_route_task`, ledger próprio, contadores compartilhados): defina e teste o comportamento.
- **Segredos.** Nenhum segredo em logs, config, ledger, telemetria ou handoff; a config só referencia nomes de variáveis de ambiente.
- **Limites do repositório.** Respeite os tamanhos e frases de 2.7.

## 6. Entregáveis

1. Branch a partir de `main` no repositório fonte (ex.: `feat/provider-switch-on-ladder-top`), seguindo `CONTRIBUTING.md`.
2. Documento de pesquisa (§3) com a proposta: decisão, alternativas descartadas, modelo de custo e migração.
3. Implementação mínima em `skill/plan-and-execute/scripts/` (prováveis: `run_isolated.py`, `routingctl.py`, `availability.py`, `routing_config.py`, `workload_routing.py`, `runner_contract.py`, `planctl.py`/`artifact_contract.py`, `routing_telemetry.py`) e no schema do relatório, se preciso.
4. Testes determinísticos para cada mudança, com CLIs falsos como em `availability_self_test.py` e `self_test.write_fake_claude`; arquivos de teste novos entram em `tools/run-skill-self-test.js`.
5. Documentação: `references/ROUTING_CONFIG.md` e `references/MODEL_ROUTING.md` §6 se o comportamento mudar; `WORKFLOW.md` (§3 e "Failure and escalation"); `PLAN_SPEC.md` se mudar o contrato da task ou de `max_attempts`; guias de fornecedor se houver detalhe específico; `scripts/configure.py` se a opção precisar aparecer no assistente ou no `show`; `SKILL.md` enxuto, com detalhe em `references/`; `CHANGELOG.md`, `README.md` e `README.pt-BR.md`. Siga o idioma de cada arquivo (o repositório é em inglês, com espelhos `*.pt-BR.md`).
6. Corrija, ou registre como fora de escopo com justificativa: o erro de despacho de 2.5 fora da troca e a omissão do pacote de evidência (2.6).
7. Revisão final com `references/SKILL_MAINTENANCE_REVIEW.md` (última TODO, se usar plano), com os achados no documento de pesquisa.

Não instale nas cópias do usuário (`~/.claude/skills/plan-and-execute` e `~/.codex/skills/plan-and-execute`: as duas têm edições locais em `SKILL.md`, `references/MODEL_ROUTING.md` e `references/MODEL_MAPPING.md` que uma instalação sobrescreveria) e não altere `~/.config/plan-and-execute/orchestrator.config.json` sem pedir.

## 7. Critérios de aceite e validação

Casos de teste mínimos:
1. Opção desligada: os testes existentes passam sem mudar asserções, o argv golden não muda e as sequências de 2.8 se mantêm (exceto a linha `advanced`, se você corrigir 2.5). Transforme a simulação em teste com fixture equivalente.
2. Topo no 1º fornecedor com outro elegível: a próxima tentativa vai para o 2º sem esperar `functional_failures_per_provider` falhas, e nenhuma tentativa repete um despacho idêntico a um topo que já falhou (salvo a regra que você definir para `mechanical`/`budget`).
3. Degrau no-op conta como topo: escada do Antigravity com slugs de esforço embutido e Claude com `strong` = `max`.
4. O último fornecedor roda ao menos uma vez antes de `ladder_exhausted`: cadeia padrão claude → codex e cadeia `max` do usuário codex → claude.
5. O 3º fornecedor é alcançável com `max_attempts` 8 na cadeia `strong` do usuário, ou existe regra documentada e testada para quando o orçamento não comporta.
6. Coerência: escada e despacho no mesmo fornecedor, sem troca oculta nem pulo não intencional (casos standard → strong do usuário).
7. Tier sem modelo no destino de uma troca: elevação ou pulo com motivo registrado.
8. Disponibilidade: quota no destino leva ao próximo elegível ou a `AvailabilityPaused`, sem contar falha funcional; fornecedor fixado com fallback desligado nunca troca.
9. Handoff com o fornecedor anterior disponível: gerado, redigido (teste com um token `sk-...` e um cabeçalho `Authorization:`), dentro do limite, validado, colocado depois do prefixo estático, usado só na tentativa seguinte e sem mudar classe, rota ou status.
10. Fornecedor anterior indisponível ou sem relatório: handoff determinístico.
11. Legado: manifests de schema 1 a 4, manifest sem `failure_classes`, snapshot v1 completo de config e ledger de disponibilidade existente.
12. Telemetria da troca e do custo do handoff, sem segredos; rollup e benchmark continuam funcionando.

Validação final: rode os autotestes afetados e `npm ci && npm run check && npm pack --dry-run` e reporte o resultado real (comandos, resumo da saída, falhas). Meça a linha de base antes de mudar e separe falhas pré-existentes. O `.ai-work/SERVICE_MAP.md` do repositório tem validações desatualizadas (ex.: `VERSION_SYNC` fixa 0.10.0 e `REQUIREMENTS` aponta para `docs/requests/`, que não existe); a referência é `npm run check` (id `ALL`).

## 8. Como trabalhar

1. Linha de base: `git status`, crie o branch de 6.1, rode `npm ci && npm run check` e reproduza 2.8.
2. Pesquise (§3), registre a proposta no documento de pesquisa, apresente ao usuário um resumo (decisão, alternativas, custo, riscos, nome e forma da opção) e então implemente; mudanças no branch são reversíveis e não precisam de confirmação.
3. Implemente em passos pequenos, com teste a cada passo e a opção desligada por padrão.
4. Peça confirmação antes de qualquer ação irreversível ou externa: commit, push, PR, publicação no npm e execução de ponta a ponta com fornecedores autenticados (gasta quota).
5. Fale com o usuário em português do Brasil. No relatório final, liste arquivos alterados, decisões e porquês, o resultado real dos testes, o que não foi verificado (fornecedores reais, Windows, que só o CI cobre, persistência de conversa do `agy` etc.), riscos e próximos passos.