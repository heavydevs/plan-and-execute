# Mapeamento de modelos, tipos de tarefa e capacidade

Referência operacional revisada em 2026-10-27. Carregue este arquivo somente para configurar ou revisar o roteamento; uma tarefa comum usa apenas a rota selecionada. Fonte de comportamento: `workload_routing.py`, `routingctl.py`, `availability.py` e [ROUTING_CONFIG.md](ROUTING_CONFIG.md). Evidência externa e limitações: `docs/research/VALIDATION_WORKLOAD_ROUTING.md` no repositório.

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

`advanced` / L3 continua disponível como nível intermediário configurável. Um tier vazio não deve ser preenchido por invenção ou rebaixamento. `weak_validation` aumenta um tier e exige high; `strong_validation` pode permitir medium conforme o roteador. Implementação usa low somente quando mecânica e deterministicamente verificável. Os sinais se combinam: design com risco arquitetural não fica no piso de design simples.

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

A documentação oficial lista Gemini 3.8 Flash e Claude Opus 5.5, mas a conta/CLI determina disponibilidade e IDs. Consulte `agy models` e registre os IDs efetivamente exibidos. O preset aceita uma lista JSON normalizada; ele **não pressupõe** que toda versão de `agy models` suporte saída JSON.

```bash
pae workloads preset --models-file /path/to/observed-models.json --manager claude
pae workloads explain --config /path/to/orchestrator.config.json --workload frontend_design --tier standard --effort medium
pae configure --show --json
```

O preset reconhece `gemini-3.8-flash-medium/high` e `claude-opus-5-5-high/medium` **somente se presentes na lista**. Outras variantes observadas exigem perfil manual revisado; não derivar ID de um rótulo como “Thinking”. Se o ID embute esforço, não duplicar uma flag contraditória.

| Família / host | Grupo do preset | Limite desta política |
| --- | --- | --- |
| Gemini no Antigravity | `antigravity-gemini` | Flash para monitoramento/diagnóstico barato, não como prova de capacidade para todo trabalho. |
| Claude/GPT no Antigravity | `antigravity-claude-gpt` | Claude limitado a standard/advanced; nunca strong/max no novo overlay. |
| Claude Code nativo | Grupo configurado da assinatura/API | Independente do grupo Antigravity; subagentes no mesmo host não criam saldo novo. |

O teto do Claude no Antigravity implementa a precaução solicitada. Não foi demonstrada uma diferença quantitativa de inteligência entre hosts. Quota bloqueia o grupo, capacidade temporária bloqueia o modelo, autenticação/CLI ausente bloqueia o host. Cooldowns legados por provedor continuam conservadores.

## 5. Precedência, fallbacks e compatibilidade

A configuração antiga de modelos/tier continua válida enquanto `workload_routing.enabled` estiver desligado. A preferência histórica do projeto por Codex acima de economy não é uma nova avaliação comparativa. Defaults embutidos continuam Claude, depois Codex; a política global e overrides seguem [ROUTING_CONFIG.md](ROUTING_CONFIG.md).

Com overlay habilitado, selecione apenas perfis compatíveis com **workload + tier + effort + cadeia permitida**. A preferência de preservar a cota do gerente só reordena candidatos elegíveis. Um host com perfis explícitos não pode escapar dos limites usando seu modelo genérico. Override de provedor e `allow_provider_fallback: false` permanecem autoritativos. Snapshots não substituem o modelo/cota do perfil escolhido.

O fallback consultivo é separado do fallback de implementação: Antigravity exige verificação de agente sem ferramentas; Claude bare exige opt-in explícito de API. Adaptadores sem fronteira somente-leitura verificada são ignorados, mesmo que possam implementar código normalmente. O monitor determinístico continua ativo se todos forem indisponíveis. Veja [VALIDATION_WORKLOADS.md](VALIDATION_WORKLOADS.md) para configuração e limites.

## 6. Base de evidência e atualização

Esta revisão substitui a tabela histórica Opus/Fable de benchmarks, preços e superioridade absoluta: seus números não foram revalidados e **não fundamentam** o novo roteamento. O texto anterior permanece no histórico Git (`6bdbab5`). A pesquisa atual confirma contratos dos hosts e grupos de cota; não mede economia monetária, sucesso visual ou equivalência de modelos na conta do usuário.

Mantenha IDs/limites observados, registre resultados por workload e compare custo **por resultado validado**, não somente preço por token. Revalide os perfis quando o host ou modelo mudar. Não reduzir pisos nem inventar modelos para preencher lacunas.
