# Mapeamento de modelos, tipos de tarefa e capacidade

Referência operacional revisada em 2026-11-20 (remapeamento final: mapa `2026-11-20-v11`, catálogo `2026-11-20-bootstrap-v9`). Carregue este arquivo somente para configurar ou revisar o roteamento; uma tarefa comum usa apenas a rota selecionada. Fonte de comportamento: `workload_routing.py`, `routingctl.py`, `availability.py` e [ROUTING_CONFIG.md](ROUTING_CONFIG.md). Evidência externa e limitações: `docs/research/VALIDATION_WORKLOAD_ROUTING.md` no repositório.

## 1. Quatro dimensões independentes

1. **Tipo de tarefa (`workload`)**: implementação, frontend/design, correção de validação ou monitoramento. Ser bom em uma delas não demonstra competência nas demais.
2. **Piso de capacidade**: `model_tier` e `reasoning_effort`, determinados pelos sinais de risco e pela qualidade da validação.
3. **Perfil de execução**: host/provedor, ID exato observado, limites e tipos de tarefa aprovados. O nome comercial de um modelo não prova equivalência entre hosts.
4. **Grupo de cota (`quota_pool`)**: permite preservar o saldo do gerente e trocar de família sem reduzir o piso. Cota indisponível não é falha de inteligência.

## 2. Piso lógico por sinal

| Sinal | Piso | Esforço |
| --- | --- | --- |
| `deterministic_lookup`, `log_monitoring` | ferramenta, sem modelo | nenhum |
| `exploration`, `mechanical_edit`, `log_diagnosis` | economy / L1 | low |
| `bounded_implementation`, `frontend_design`, `validation_repair` | standard / L2 | medium |
| `subtle_debugging` | strong / L4 | medium |
| `architecture_decision`, `cross_cutting_risk`, `silent_failure_costly` | strong / L4 | high |
| `frontier_long_horizon` | max / L5 | high |
| `repeated_strong_failure` | max / L5 | xhigh |
| `extreme_architecture`, `extreme_code_review` | max / L5 + `frontier_eligible` (frontier / L6 só para papel somente leitura `analyst`/`verifier`) | xhigh (frontier: high) |

`advanced` / L3 continua disponível como nível intermediário configurável. Um tier vazio não deve ser preenchido por invenção ou rebaixamento. `weak_validation` aumenta um tier e exige high; `strong_validation` pode permitir medium conforme o roteador. Implementação usa low somente quando mecânica e deterministicamente verificável. Os sinais se combinam: design com risco arquitetural não fica no piso de design simples.

### 2.1 Mapa vigente por nível (remapeamento final, 2026-11-20)

Modelo e esforço inicial → teto por nível. O esforço inicial é o piso do sinal; só evidência de falha sobe o degrau.

| Nível | Claude Code | Codex | Antigravity (overlay opt-in, conforme `agy models`) |
| --- | --- | --- | --- |
| economy / L1 | `claude-haiku-5-5` low → medium (use medium quando um erro de exploração custa caro; o alias `haiku` não é roteado) | `gpt-6.2-sol` low (→ medium só se o piso pedir) | Gemini 4 Hydrogen low (medium se pedido); Gemini 3.8 Flash medium só para monitoramento |
| standard / L2 | `claude-sonnet-5-5` medium → high | `gpt-6.2-sol` medium (Terra 6.1 não é mais roteado) | Gemini 4 Neon low/medium primeiro; Hydrogen medium/high como fallback |
| advanced / L3 | vazio no mapa embutido (sobe para strong: Opus medium); config global: `claude-opus-5-5` | vazio no mapa embutido (sobe para Sol high); config global: `gpt-6.2-sol` até high | Gemini 4 Neon high; Claude Opus 5.5 do Antigravity como transbordo (limitado a advanced) |
| strong / L4 | `claude-opus-5-5` medium → high | `gpt-6.2-sol` high | Gemini 4 Neon high → xhigh (xhigh por evidência de falha) |
| max / L5 | `claude-opus-5-5` xhigh (`max` nunca é padrão) | `gpt-6.2-sol` xhigh (`max` e `ultra` nunca são padrão) | não roteado (cai para Codex, depois Claude) |
| **frontier / L6 (F6)** | `claude-fable-5-2` high (xhigh só onde medido; Claude Code >= 2.1.321) | `gpt-6.2-astra` high → xhigh (nunca low, max ou `ultra`; Codex >= 0.171.0) | `gemini-4-carbon-*` só se `agy models` listar; nunca no preset |

Escadas embutidas: Claude Haiku low → Haiku medium → Sonnet medium → Sonnet high → Opus medium → Opus high → Opus xhigh; Codex Sol low → Sol medium → Sol high → Sol xhigh (um só modelo subindo esforço, sem degraus repetidos). Acima do degrau max/xhigh só existe o nível frontier, pelas regras abaixo. `gpt-6-luna` continua listado pelo Codex, mas fica só como explorer nativo somente leitura em `high` ([MODEL_ROUTING_CODEX.md](MODEL_ROUTING_CODEX.md)).

Política do proprietário (final, 2026-11-20): **Opus 5.5 e Sol 6.2 são o teto usual**. Fable 5.2 e Astra 6.2 formam o nível `frontier` (L6/F6), **acima de tudo**, para casos especiais, sem aprovação por tarefa. Entradas permitidas, e nenhuma outra: (1) arquitetura ou revisão de código de demandas **extremamente** difíceis pelos sinais `extreme_architecture` / `extreme_code_review`, somente em papel somente leitura; (2) depois de `routing_policy.frontier.min_top_failures` (padrão 2) falhas `semantic`, `mechanical` ou `unknown` de Opus/Sol no degrau max/xhigh — o próximo passo deixa de ser o bloqueio `ladder_exhausted` e passa a ser a rota frontier; se ela também falhar, a tarefa bloqueia para replanejamento. Nunca por elevação de piso, nunca como degrau comum da escada, nunca para implementação comum, exploração, monitoramento ou DIRECT, nunca por cota, autenticação, cobrança, ambiente, orçamento ou timeout. Créditos do Codex esgotados no Astra são disponibilidade: o runner pula para o Fable sem registrar escalonamento. O registro persiste `tier: max` com `level: frontier` e `frontier: true`. `routing_policy.frontier.enabled: false` restaura o comportamento anterior. Ordem de provedores: implementação Antigravity > Codex > Claude; arquitetura, revisão e frontier Codex > Claude.

Requisitos de CLI (documentação dos fornecedores, 2026-11-20): `claude-fable-5-2` exige Claude Code >= 2.1.321 (o changelog adiciona o Fable 5.2 nessa versão; a 2.1.283 respondeu HTTP 400 e o `claude-pae-2.1.322.exe` do proprietário rodou o Fable 5.2); Opus 5.5 >= 2.1.280, Sonnet 5.5 >= 2.1.284, Haiku 5.5 >= 2.1.293. `gpt-6.2-sol`/`gpt-6.2-astra` exigem Codex >= 0.171.0. O esforço `ultra` do Codex (esforço máximo mais subagentes automáticos, 2,5x a 12x os tokens) nunca é roteado; mantenha `service_tier = "default"` no Codex, porque o catálogo marca Astra 6.2 e Terra com Fast (2x de uso) por padrão.

## 3. Matriz por tipo de trabalho

| Workload / trabalho | Preferência condicional | Evidência de aceitação |
| --- | --- | --- |
| `implementation` | Perfil habilitado que cumpra o piso; com gerente Claude, o preset pode preferir Claude do Antigravity em standard/advanced. | Testes funcionais, integração e casos negativos. |
| `frontend_design` | Perfil aprovado para frontend, independente da aptidão para backend. O preset Claude intermediário é uma política conservadora do usuário, não um ranking visual demonstrado. | Fluxos reais, screenshots responsivos, acessibilidade e revisão visual; testes unitários isolados não aprovam design. |
| `validation_repair` | Rota de correção no piso requerido; falha semântica confirmada pode exigir strong/max fora do Claude intermediário do Antigravity. | Reprodução da falha e nova execução independente da validação. |
| `log_monitoring` normal | Monitor determinístico (`resource_watch`, `progress_watch`, `validatectl`), **sem tokens de IA**. | Saída do processo, progresso semântico, CPU, arquivos/probes e saúde mapeada. |
| Diagnóstico opcional de anomalia | Perfis economy de `log_monitoring`, na ordem configurada; preset prefere Flash 3.8 Medium observado, depois High quando Medium não existir. | Pacote redigido e limitado; resposta estruturada consultiva, nunca aprovação, comando ou permissão de escrita. |

O `observer` não chama uma IA a cada linha ou intervalo saudável. Repetição de evidência não gera nova consulta. Ler o restante da configuração de modelos não é necessário para executar um teste.

## 4. Antigravity: descoberta, capacidade e cotas

A conta/CLI determina disponibilidade e IDs; consulte `agy models` e registre os IDs efetivamente exibidos. Observado em 2026-11-20 nesta conta: `gemini-4-neon-{low,medium,high,xhigh}`, `gemini-4-argon-{low,medium,high}`, `gemini-4-hydrogen-{low,medium,high,xhigh}`, orquestradores Neon/Argon, `gemini-3.8-flash-*`, `claude-opus-5-5-{low,medium,high}`, `claude-sonnet-5-5-{low,medium,high}` e `gpt-oss-120b-medium`. **`gemini-4-carbon-*` não é listado** (Carbon exige Ultra/Enterprise) e, portanto, nunca entra no preset. Claude Sonnet/Opus 4.6 foram removidos do Antigravity em 2026-11-18. O preset aceita uma lista JSON normalizada; ele **não pressupõe** que toda versão de `agy models` suporte saída JSON.

```bash
pae workloads preset --models-file /path/to/observed-models.json --manager claude
pae workloads explain --config /path/to/orchestrator.config.json --workload frontend_design --tier standard --effort medium
pae configure --show --json
```

Atualização do Antigravity (2026-11-20): CLI `agy` 1.5.13 instalada (espelhos do changelog vão até 1.5.12); a lista de `agy models` desta conta não mudou (inclui `gemini-pro-orchestrator-neon` e `gemini-pro-orchestrator-g1-pro`, este com Argon). O Gemini 4 Neon virou o modelo padrão do app em 2026-11-18 (low..xhigh). O Orchestrator (esforço fixo) planeja com Neon, Carbon ou Argon e executa com Hydrogen; ele **não** embute esforço e seu comportamento headless não foi verificado, então não é roteado (perfil futuro opcional). Desde a CLI 1.5.10 o próprio `agy` espera e repete limites de taxa de até 4 minutos, e encerra o turno na hora em erros de teto de gasto (spend cap), saldo pré-pago ou cota semanal: `availability.py` classifica essas mensagens como cota/créditos (disponibilidade, nunca capacidade). Com `GEMINI_API_KEY`, `/usage`, `/quota` e `/credits` saem com código 2 em execuções `-p`. A revisão de sandbox do modo automático no Hydrogen agora usa thinking medium. No remapeamento final, Neon passou a cobrir standard–strong, à frente do Hydrogen: com o mesmo custo por tarefa do Intelligence Index v5.0.1, o Neon um esforço abaixo vence o Hydrogen (Neon low 44 a US$ 0,75 contra Hydrogen medium 41 a US$ 0,80; Neon medium 55 a US$ 1,90 contra Hydrogen high 51 a US$ 1,87), e no índice de agente de código o Neon xhigh lidera (58,64 a US$ 6,86, 177 passos) contra Hydrogen xhigh (52,32 a US$ 4,45, 405 passos). Confiança média-baixa: o índice não é de código e o Neon tem pouca medição independente. Hydrogen fica com economy e é o fallback de standard (mais rápido, ~160 contra ~100 tokens/s). Relatos de usuários desde 2026-11-15 sobre raciocínio reduzido em chamadas de ferramenta e contexto truncado acima de ~126k tokens não foram confirmados pelo Google; mantenha tarefas abaixo de ~100k tokens de contexto vivo e valide com um replay pequeno.

O preset reconhece `gemini-3.8-flash-medium/high`, `claude-opus-5-5-high/medium` e as variantes de esforço de `gemini-4-neon-*` (standard–strong) e `gemini-4-hydrogen-*` (economy–standard), um perfil por variante em ordem crescente de esforço, **somente se presentes na lista**; as rotas colocam Neon, depois Hydrogen, depois o Claude intermediário. Para implementação standard/medium o primeiro candidato é `agy-neon-medium` e o fallback barato do mesmo esforço é `agy-hydrogen-medium`. Argon (dominado: Neon medium 55 a US$ 1,90 contra Argon high 50 a US$ 4,97) e Carbon não entram no preset. Outras variantes observadas exigem perfil manual revisado; não derivar ID de um rótulo como “Thinking”. Se o ID embute esforço, não duplicar uma flag contraditória.

| Família / host | Grupo do preset | Limite desta política |
| --- | --- | --- |
| Gemini no Antigravity | `antigravity-gemini` | Flash para monitoramento/diagnóstico barato; Hydrogen/Neon para implementação conforme os níveis acima. Não são prova de capacidade para todo trabalho. |
| Claude/GPT no Antigravity | `antigravity-claude-gpt` | Claude limitado a standard/advanced; nunca strong/max no novo overlay. |
| Claude Code nativo | Grupo configurado da assinatura/API | Independente do grupo Antigravity; subagentes no mesmo host não criam saldo novo. |

O teto do Claude no Antigravity implementa a precaução solicitada. Não foi demonstrada uma diferença quantitativa de inteligência entre hosts. Quota bloqueia o grupo, capacidade temporária bloqueia o modelo, autenticação/CLI ausente bloqueia o host. Cooldowns legados por provedor continuam conservadores.

## 5. Precedência, fallbacks e compatibilidade

A configuração antiga de modelos/tier continua válida enquanto `workload_routing.enabled` estiver desligado. A preferência histórica do projeto por Codex acima de economy não é uma nova avaliação comparativa. Defaults embutidos continuam Claude, depois Codex; a política global e overrides seguem [ROUTING_CONFIG.md](ROUTING_CONFIG.md).

Com overlay habilitado, selecione apenas perfis compatíveis com **workload + tier + effort + cadeia permitida**. A preferência de preservar a cota do gerente só reordena candidatos elegíveis. Um host com perfis explícitos não pode escapar dos limites usando seu modelo genérico. Override de provedor e `allow_provider_fallback: false` permanecem autoritativos. Snapshots não substituem o modelo/cota do perfil escolhido.

O fallback consultivo é separado do fallback de implementação: Antigravity exige verificação de agente sem ferramentas; Claude bare exige opt-in explícito de API. Adaptadores sem fronteira somente-leitura verificada são ignorados, mesmo que possam implementar código normalmente. O monitor determinístico continua ativo se todos forem indisponíveis. Veja [VALIDATION_WORKLOADS.md](VALIDATION_WORKLOADS.md) para configuração e limites.

## 6. Base de evidência e atualização

O remapeamento final de 2026-11-20 usa cinco relatórios em `docs/research/model-refresh-20261120/` (OpenAI/Codex, Anthropic/Claude, Google/Antigravity, benchmarks cruzados e provedores opcionais), resumidos em `docs/research/MODEL_REFRESH_20261120.md`. Fonte principal: Artificial Analysis Coding Agent Index v2.1 (independente, 322 tarefas, 3 tentativas, custo por tarefa a preço de API; não comparável à v2.0).

| Decisão | Evidência (data, tipo) | Confiança |
| --- | --- | --- |
| Codex standard = Sol 6.2 medium; Terra fora | CAI v2.1: Sol 6.2 low 37 (US$ 0,33), medium 45 (0,57), high 47 (0,76), xhigh 50 (0,90); Terra max 49 a US$ 1,53 com 4,4x os tokens. Terminal-Bench 4.1: Terra 53,3% contra Sol 61,5%; Vals TB 4.0: 49,5% a US$ 2,16 contra 60,6% a US$ 1,13. Terra custa metade por token, então só vence abaixo de 2x os tokens do Sol com qualidade igual, o que nenhuma medição de código mostra (independente) | média-alta |
| Codex economy = Sol 6.2 low; Luna só explorer | Luna: CAI 26 em max, Terminal-Bench 13–15%; a OpenAI manda começar o Luna em High, e o piso economy despacha `low` (independente + fornecedor) | média |
| Teto Codex xhigh | Sol 6.2 max 49 a US$ 1,22 < xhigh 50 a US$ 0,90; `ultra` usa subagentes e 2,5x–12x os tokens | média |
| Claude: Haiku economy, Sonnet standard | Sonnet 5.5 bate Haiku 5.5 em código agêntico (CAI max 56 contra 30; Terminal-Bench 4.0 70,6% contra 39,2%, fornecedor); Haiku acima de 100k tokens de prompt custa 5x na entrada; em sessões curtas (Bito, n=8) Haiku medium empata com Sonnet medium | média |
| Opus strong medium/high, max xhigh, nunca `max` | CursorBench 4.0: Opus high 56,0% = xhigh 56,0%, max 57,8% a 3,4x o custo de high; CAI Opus max 58,16 a US$ 12,61 com ~9% de fallback | média |
| Frontier Fable 5.2 high, Astra 6.2 high | CAI: Fable high 58,24 (US$ 7,51) ≈ xhigh 58,47 (US$ 15,47) > max 55,74 (US$ 44,22, timeouts); Astra high 52 (US$ 2,37), xhigh 53 (US$ 3,20), low 36 e max dominados. Bito: Opus medium 84,1% (US$ 5,40) > Fable medium 81,0% (US$ 8,13) | média / média-baixa |
| Antigravity: Neon à frente em standard | ver §4 (Intelligence Index e CAI via AA, 2026-11-19) | média-baixa |

Incertezas: Opus, Sonnet e Haiku abaixo de max, Neon abaixo de xhigh e Hydrogen abaixo de xhigh não têm linha no CAI; Bito tem 8 sessões por modelo; vários números são de fornecedor ou de agregadores; GPT-6.2 tem três dias e há relatos isolados de parada precoce (sem resposta da OpenAI). A evidência sugere que, quando o Opus precisaria de xhigh ou max, o Fable high entrega o mesmo índice por menos — a política do proprietário mantém o Fable como nível frontier (duas falhas no topo ou revisão extrema), e isso fica registrado como questão em aberto para o replay `routing-eval`, que continua sendo o portão de aceitação.

Mantenha IDs/limites observados, registre resultados por workload e compare custo **por resultado validado**, não somente preço por token. Revalide os perfis quando o host ou modelo mudar. Não reduzir pisos nem inventar modelos para preencher lacunas.
