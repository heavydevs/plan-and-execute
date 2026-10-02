# Tabela de Mapeamento de Modelos, Complexidade e Níveis de IA

Este documento é a referência operacional de roteamento para a skill **plan-and-execute**, detalhando a relação entre **complexidade da tarefa (sinais)**, **níveis lógicos (tiers L1..L5)** e **nível de esforço de raciocínio de IA (effort)** para cada fornecedor de execução (**Claude Code**, **Codex**, **Antigravity**).

---

## 1. Níveis Lógicos (Tiers) e Equivalências

A skill utiliza 5 tiers lógicos independentes de fornecedor (com aliases portáteis `L1`..`L5` ou `F1`..`F5`):

| Nível / Tier | Alias | Descrição e Finalidade |
|---|:---:|---|
| **`economy`** | `L1` / `F1` | Exploração rápida, leitura de código, tarefas mecânicas estreitas, resumos compactos. |
| **`standard`** | `L2` / `F2` | Implementação rotineira com escopo fechado, refatorações pontuais, testes unitários. |
| **`advanced`** | `L3` / `F3` | Intermediário entre Standard e Strong; depurações com acoplamento moderado ou decisões de escopo delimitado. |
| **`strong`** | `L4` / `F4` | Engenharia complexa, sutilezas de estado/concorrência, decisões de arquitetura e tarefas com validação fraca. |
| **`max`** | `L5` / `F5` | Escalação de fronteira / long-horizon, raciocínio profundo autônomo após falha comprovada no Strong. |

---

## 2. Matriz de Complexidade vs. Nível e Esforço de IA (Floor)

A classificação da complexidade de cada tarefa folha determina o piso (*floor*) mínimo de modelo e de esforço:

| Complexidade / Sinal Observável | Nível Mínimo (Tier) | Esforço Recomendado (Effort) | Ação Recomendada |
|---|:---:|:---:|---|
| **`deterministic_lookup`**<br>Busca de símbolo/arquivo, formatação, build/lint/test | — | — | **Ferramenta direta (tool)**, sem invocar modelo de IA. |
| **`exploration`**<br>Descoberta ampla, varredura de call-sites, inventário | `economy` (L1) | `low` | Subagente explorador descartável somente leitura (máx. 2 simultâneos). |
| **`mechanical_edit`**<br>Renomeação, movimentação, atualização com checagem local | `economy` (L1) | `low` | Edição direta no contexto ou subagente rápido verificado por comando. |
| **`bounded_implementation`**<br>Feature comum, refatoração pontual, testes diretos | `standard` (L2) | `medium` | Implementação com validação automatizada determinística obrigatória. |
| **`subtle_debugging`**<br>Problemas de estado, ordenação, causas flaky ou não-locais | `strong` (L4) | `medium` | Análise minuciosa de causa raiz e hipóteses verificáveis. |
| **`architecture_decision`**<br>Fronteiras entre módulos, grafos de dependência, contratos | `strong` (L4) | `high` | Decisão formal preservando contratos prévios e compatibilidade. |
| **`cross_cutting_risk`**<br>Segurança, concorrência, migração de dados, integridade | `strong` (L4) | `high` | Isolamento em subagente/worktree com plano de rollback/verificação. |
| **`silent_failure_costly`**<br>Falha silenciosa que não seria pega de imediato e causaria dano | `strong` (L4) | `high` | Raciocínio profundo e testes de estresse / validação cruzada. |
| **`frontier_long_horizon`**<br>Loops autônomos longos, raciocínio exploratório extremo | `max` (L5) | `high` | Apenas quando justificado pelo escopo e ausência de atalhos determinísticos. |
| **`repeated_strong_failure`**<br>O nível Strong falhou e gerou evidências de déficit semântico | `max` (L5) | `xhigh` | Subida na escada de escalação guiada estritamente pela classe de falha. |

### Modificadores de Validação:
- **`weak_validation`**: Se a validação não puder ser 100% determinística (sem testes conclusivos ou resultado difícil de auditar mecanicamente), **eleve em +1 o tier** e suba o piso de esforço para **`high`**.
- **`strong_validation`**: Se a validação determinística for sólida (ex: suite de testes unitários + compilação + linter), os tiers `standard` e `strong` podem iniciar em **`medium`**.
- **Regra de Implementação**: Trabalhadores de implementação nunca utilizam esforço `low`, pois tendem a ignorar leituras e fases de validação.

---

## 3. Mapeamento de Modelos por Fornecedor no SO

Configuração sincronizada no arquivo global do sistema operacional:  
`%APPDATA%/plan-and-execute/orchestrator.config.json`

| Tier / Nível | Claude Code (`claude`) | Codex CLI (`codex`) | Antigravity CLI (`agy`) |
|:---:|---|---|---|
| **`economy` (L1)** | `haiku` *(Haiku 4.5; sem flag `--effort`)* | `gpt-6-luna` *(effort: low)* | `gemini-3.8-flash-high` |
| **`standard` (L2)** | `claude-sonnet-5-5` *(effort: medium/high)* | `gpt-6.1-sol` *(effort: medium)* | `gemini-3.1-pro-high` |
| **`advanced` (L3)** | `claude-opus-5-5` *(effort: medium)* | `gpt-6-astra` *(effort: low/medium)* | `claude-sonnet-4-6` |
| **`strong` (L4)** | `claude-opus-5-5` *(effort: medium/high)* | `gpt-6-astra` *(effort: medium/high)* | `claude-opus-4-6-thinking` |
| **`max` (L5)** | `claude-opus-5-5` *(effort: xhigh/max)* | `gpt-6-astra` *(effort: xhigh)* | `claude-opus-4-6-thinking` |

*(Nota sobre Fable 5.1: Caso deseje utilizar o `claude-fable-5-1` no tier `max`, ele permanece suportado pelo catálogo, mas exige créditos pré-pagos e opera com maior latência/custo do que o Opus 5.5).*

---

## 4. Análise Atualizada: Claude Opus 5.5 vs. Claude Fable 5.1

Dados consolidados dos benchmarks de engenharia de software e custos (Anthropic, out/2026):

| Métrica / Dimensão | Claude Opus 5.5 (`claude-opus-5-5`) | Claude Fable 5.1 (`claude-fable-5-1`) | Vantagem Prática |
|---|:---:|:---:|---|
| **Data de Lançamento** | **22 de Setembro de 2026** | 01 de Setembro de 2026 | Opus 5.5 é mais recente e melhor calibrado. |
| **Terminal-Bench 4.0** | **66.4%** | 55.8% | **Opus 5.5 supera em +10.6 p.p.** no terminal agentic. |
| **CursorBench 4.0** | **57.8%** | 51.8% | **Opus 5.5 supera em +6.0 p.p.** em refatoração/código. |
| **Preço por 1M Tokens (In/Out)** | **$4 / $20** | $10 / $50 | **Opus 5.5 é 60% mais barato (2.5x)**. |
| **Esforço Padrão (Effort)** | `medium` (Adaptive Thinking ágil) | `high` (tende a overthinking/latência) | Opus 5.5 completa tarefas mais rápido e gasta menos tokens. |
| **Restrições de Conta / Quota** | Suportado nos planos Pro/Team sem travas extras | Exige saldo de créditos dedicado (`credits_required` HTTP 429) | Opus 5.5 não pausa execuções por falta de pool de créditos. |

**Conclusão**: Para tarefas de desenvolvimento de software e orquestração de código, **o Claude Opus 5.5 é objetivamente superior e mais eficiente que o Fable 5.1**, justificando seu uso como padrão nos tiers `strong` e `max`.

---

## 5. Cadeia Padrão de Roteamento e Fallbacks no SO

Quando um fornecedor atinge limites de cota, rate limit (HTTP 429) ou instabilidade temporária, o orquestrador aciona a seguinte cadeia de prioridades:

```text
economy:  Antigravity  ->  Claude  ->  Codex
standard: Claude       ->  Codex   ->  Antigravity
advanced: Claude       ->  Codex   ->  Antigravity
strong:   Claude       ->  Codex   ->  Antigravity
max:      Claude       ->  Codex   ->  Antigravity
```

### Resumos e Assistentes:
- **Resumo de Tarefas / Planos**: Executado primariamente via `antigravity` no tier `economy` (`gemini-3.8-flash-high`) com esforço `low` em ambiente de sandbox para economia máxima de tokens.
