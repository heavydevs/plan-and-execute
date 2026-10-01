# Documento de requisitos — Portable Model Routing & Dynamic Provider Catalog

**Projeto:** `heavydevs/plan-and-execute`  
**Origem:** estudo da PR #17 — `Make model routing provider-portable with dynamic F/L matrix`  
**PR estudada:** `feat/provider-portable-model-routing` (`789650f55cf5609e55d1cb4c26e5b2fcac1e1859`)  
**Base de referência atual:** `main` (`6be46885ad691d3d43557a42fc2fd36a804b7eba`)  
**Data do estudo:** 2026-10-01  
**Status deste documento:** requisitos e arquitetura propostos; não é implementação.

---

## 1. Objetivo

Este documento especifica como incorporar à `main` os objetivos funcionais da PR #17 — portabilidade de plano entre provedores/modelos, resolução dinâmica de modelo concreto, atualização segura do catálogo e suporte ao Muse Code — sem reintroduzir a complexidade, o custo de contexto e o acoplamento que a `main` atual já eliminou.

Além do escopo original da PR #17, a solução deve adicionar **GLM/Z.AI** e **DeepSeek** como opções de execução da skill e deve evoluir o roteamento para otimizar **qualidade verificada por tarefa concluída**, **consumo de tokens/créditos**, **reuso de cache**, **latência** e **resiliência a quota/indisponibilidade**.

A arquitetura proposta preserva os princípios da `main` atual:

- tarefas duráveis não devem depender da identidade do agente que criou o plano;
- `provider: auto` continua sendo o padrão;
- roteamento de dificuldade e disponibilidade são problemas diferentes;
- mudança de provider por quota não significa aumento de capacidade;
- escalada de capacidade ocorre somente a partir de evidência técnica;
- o worker recebe o mínimo contexto necessário;
- validação determinística continua sendo autoridade de conclusão;
- nenhum novo modelo/router deve ser chamado apenas para decidir qual modelo chamar;
- o custo relevante é **custo por resultado validado**, não preço bruto por token.

---

# Parte I — O que a PR #17 realmente se propõe a fazer

## 2. Resumo da PR #17

A PR #17 modifica 16 arquivos e adiciona aproximadamente 1.082 linhas, removendo 221. Ela foi criada quando a `main` ainda estava em `a6824a4...`; hoje está 43 commits atrás e conflita com a `main` em 14 dos 16 arquivos alterados.

A PR faz quatro mudanças arquiteturais acopladas.

### 2.1. Tornar o roteamento persistido independente de provider

A PR troca os valores de rota usados em novos TODOs:

```text
provider: auto
model_tier: F1 | F2 | F3 | F4
reasoning_effort: L1 | L2 | L3 | L4 | L5
```

onde:

| Coordenada | Significado original na PR #17 |
|---|---|
| F1 | família mais econômica capaz de exploração/edição mecânica |
| F2 | família normal de implementação |
| F3 | família forte para engenharia difícil/arriscada |
| F4 | família frontier/long-horizon |
| L1 | menor esforço útil |
| L2 | esforço econômico normal |
| L3 | esforço alto |
| L4 | esforço muito alto |
| L5 | maior esforço útil suportado |

Os nomes concretos de modelos deixam de fazer parte da identidade semântica de um TODO.

### 2.2. Criar uma matrix de modelos atual no momento do planejamento

A PR cria `MODEL_MATRIX.md` e `modelmapctl.py`.

Durante a criação de um plano ORCHESTRATED, o planejador deve pesquisar:

- CLIs de coding agents realmente disponíveis;
- modelos e efforts suportados atualmente;
- documentação oficial de catálogo e preço;
- benchmark recente de coding agents, quando disponível;
- observações de compatibilidade.

O resultado é persistido como:

```text
.ai-work/<plan-id>/MODEL_MATRIX.json
.ai-work/<plan-id>/MODEL_MATRIX.md
```

A matrix associa F1–F5 e L1–L5 a configurações concretas de cada provider.

### 2.3. Resolver provider/modelo somente no runtime

`routingctl.py` passa a:

- carregar a matrix local do plano;
- sobrepor seus modelos no runtime;
- traduzir F/L para o vocabulário do runner legado;
- selecionar provider/model/native effort somente quando o TODO for executado;
- registrar a rota concreta como provenance/resultado, não como semântica durável.

Com isso, um plano pode começar em Claude e continuar em Codex, Muse ou outro provider sem reescrever TODOs.

### 2.4. Adicionar Muse Code

A PR adiciona Muse como provider de execução:

```text
muse exec --json
```

com comportamento diferente para worker e summary:

- worker: `--trust-workspace`, `--disable-approval`;
- summary: `--disable-write`;
- passagem de `--model` e `--reasoning-effort`;
- parsing do envelope JSON/JSONL;
- suporte em `pae resume --provider muse`, `pae doctor`, help e testes.

---

## 3. Estratégias adotadas pela PR #17

### 3.1. Late binding de modelo

O plano armazena capacidade requerida, não modelo concreto. Modelo é ligado somente no momento da execução.

Essa estratégia é correta: o tempo de vida de um plano pode ser maior que o tempo de vida de um alias/modelo, e releases de modelos mudam preço e qualidade rapidamente.

### 3.2. Compatibilidade retroativa

A PR mantém leitura de planos antigos que usam:

```text
economy | standard | strong | max
low | medium | high | xhigh | max
```

Isso evita invalidar planos já criados.

### 3.3. Live discovery como fonte de verdade

A PR não quer que o catálogo estático da skill seja a verdade definitiva. Ela exige pesquisa atual durante planejamento e permite `research_mode: live|fallback`.

### 3.4. Snapshot por plano

A mapping usada por um plano fica guardada junto ao plano. Isso melhora:

- auditabilidade;
- reprodutibilidade;
- explicação de qual modelo estava disponível quando o plano foi criado;
- retomada após troca de provider.

### 3.5. Separação entre semântica do TODO e provenance de execução

`F#/L#` pertencem ao TODO. Provider/model/effort real pertencem à tentativa. Essa é uma separação importante e deve ser preservada.

### 3.6. Provider-neutral review

A revisão do plano passa a verificar:

- vazamento de model IDs concretos nos TODOs;
- matrix desatualizada ou sem fonte;
- ausência de fallback realista;
- overspending de F/L em relação ao risco e à verificabilidade.

---

# Parte II — Análise da PR #17 contra a `main` atual

## 4. O que a `main` já resolveu desde a PR #17

A `main` atual evoluiu significativamente desde a base da PR.

Hoje já existe:

```text
provider: auto
model_tier: economy | standard | strong | max
reasoning_effort: low | medium | high | xhigh | max
```

Esses tiers **já são provider-neutral**. O provider concreto é definido por `tier_routes` e pode ter primary + fallbacks.

O runtime já separa:

- indisponibilidade/quota → trocar provider mantendo tier lógico;
- falha mecânica/semântica/budget → escalada baseada em `failure_class`;
- ambiente → reparar ambiente, não comprar modelo maior;
- `plan_defect` → bloquear e replanejar.

Portanto, a necessidade original de “não amarrar TODO a Claude/Codex” já foi em grande parte incorporada à `main` por outra arquitetura.

## 5. Problema de substituir os tiers atuais por F/L

Na PR #17 existe essencialmente esta equivalência:

```text
F1 = economy
F2 = standard
F3 = strong
F4 = max

L1 = low
L2 = medium
L3 = high
L4 = xhigh
L5 = max
```

Fazer uma migração de schema apenas para trocar os nomes aumentaria:

- superfície de compatibilidade;
- testes;
- documentação;
- tokens carregados;
- risco de conflitos;
- custo de manutenção;

sem adicionar nova informação semântica.

### Decisão arquitetural AD-001

**Evoluir o vocabulário canônico da `main` somente onde existe ganho semântico real.**

A PR #17 original não justificava renomear quatro tiers existentes apenas para F1–F4. Este documento agora acrescenta uma mudança semanticamente útil: o novo tier `advanced`, entre `standard` e `strong`, para capturar modelos de alta relação qualidade/custo antes do salto para frontier premium.

O estado durável futuro deve normalizar para:

```text
economy | standard | advanced | strong | max
low | medium | high | xhigh | max
```

F1–F5/L1–L5 permanecem **aliases portáveis/display**, não um segundo schema concorrente:

```text
F1 / economy
F2 / standard
F3 / advanced
F4 / strong
F5 / max
```

Compatibilidade é obrigatória: planos antigos com `strong` e `max` mantêm exatamente sua semântica; inserir `advanced` não desloca nem rebaixa tiers persistidos.

---

## 6. Problema de pesquisar todos os providers a cada plano

A PR #17 exige pesquisa de catálogo/preço/benchmark durante cada planejamento.

Isso é incompatível com o `TOKEN_EFFICIENCY.md` atual porque:

- repete a mesma pesquisa para muitos planos;
- aumenta contexto antes da implementação;
- faz web/documentação concorrer com o próprio request;
- benchmark muda mais devagar que planos;
- o mesmo provider pode ser pesquisado muitas vezes no mesmo dia;
- provedores disponibilizam parte da informação via CLI/API determinística;
- web research é mais cara e menos determinística que metadata estruturada.

### Decisão arquitetural AD-002

Criar duas camadas separadas:

```text
Shared Model Catalog Registry
        ↓ projeção
Plan-local MODEL_MATRIX.json
```

O catálogo compartilhado é atualizado de forma **lazy e provider-scoped**. O plano recebe apenas um snapshot mínimo dos providers/candidatos que realmente podem executá-lo.

---

# Parte III — Arquitetura-alvo

## 7. Visão geral

```text
                         TASK / TODO
                             │
                    semantic task signals
                             │
                  deterministic route floor
               (routingctl.minimum_route)
                             │
                             ▼
                  capability requirements
                             │
                             ▼
                Shared Model Catalog Registry
            ┌────────────┬────────────┬───────────┐
            │ capability │ economics  │ evidence  │
            │ metadata   │ / quota    │ / quality │
            └────────────┴────────────┴───────────┘
                             │
                      eligibility filter
                             │
                  ┌──────────┴──────────┐
                  │ candidate providers │
                  └──────────┬──────────┘
                             │
              expected validated-task economics
                             │
                      deterministic choice
                             │
                             ▼
                    Provider Profile Layer
                             │
            ┌────────────────┼────────────────┐
            │                │                │
      Claude harness     Codex harness     Native CLI
       │      │             │     │             │
    Claude   GLM        OpenAI DeepSeek        Muse
       │   DeepSeek
       ▼
                fresh isolated worker
                             │
                   deterministic validation
                             │
              success/failure/cost telemetry
                             │
                    future route evidence
```

---

## 8. Componentes

### 8.1. Route Requirement Layer

Responsável por responder somente:

> “Qual é a menor classe de capacidade segura para este trabalho?”

Continua sendo determinístico e baseado nos sinais da `main`:

- `deterministic_lookup`;
- `exploration`;
- `mechanical_edit`;
- `bounded_implementation`;
- `subtle_debugging`;
- `architecture_decision`;
- `cross_cutting_risk`;
- `silent_failure_costly`;
- `frontier_long_horizon`;
- `repeated_strong_failure`;
- `weak_validation` / `strong_validation`.

**Regra:** o catálogo econômico pode escolher qualquer candidato **no floor ou acima dele**, nunca abaixo.

Isso impede que preço baixo cause under-routing perigoso.

### 8.2. Shared Model Catalog Registry

Novo componente proposto:

```text
skill/plan-and-execute/scripts/model_catalog.py
skill/plan-and-execute/scripts/model_catalogctl.py
skill/plan-and-execute/references/MODEL_CATALOG.md
```

Cache do usuário:

```text
~/.cache/plan-and-execute/model-catalog/
  claude.json
  codex.json
  antigravity.json
  qwen.json
  kimi.json
  trae.json
  muse.json
  glm.json
  deepseek.json
```

Em Windows, usar a localização de cache de perfil apropriada.

Cada registro deve separar três tipos de evidência com freshness independente:

1. **capability/availability** — modelo existe? effort? context? APIs? visão? tool calls?
2. **economics** — API, subscription credits, cache, peak/off-peak, quotas;
3. **quality evidence** — benchmark por classe de workload e telemetry local.

### 8.3. Model Catalog Entry

Exemplo conceitual:

```json
{
  "provider": "deepseek",
  "catalog_version": 3,
  "observed_at": "2026-10-01T00:00:00Z",
  "source": {
    "kind": "official_api_or_docs",
    "version": "...",
    "digest": "..."
  },
  "harness_profiles": ["claude", "codex"],
  "models": {
    "deepseek-flash": {
      "capabilities": {
        "text": true,
        "vision": true,
        "tools": true,
        "structured_output": true,
        "anthropic_api": true,
        "responses_api": true,
        "context_tokens": 1000000
      },
      "effort": {
        "native": ["low", "high", "max"],
        "aliases": {"medium": "high", "xhigh": "max"}
      },
      "economics": {...},
      "quality_evidence": [...]
    }
  }
}
```

O schema deve ser estritamente validado antes de qualquer dado ser usado em comando ou routing.

### 8.4. Plan-local model matrix

Para preservar o objetivo original da PR #17, o plano mantém:

```text
.ai-work/<plan-id>/MODEL_MATRIX.json
.ai-work/<plan-id>/MODEL_MATRIX.md
```

Mas o conteúdo deve ser uma **projeção compacta** do catálogo compartilhado, não uma cópia de toda a pesquisa.

`MODEL_MATRIX.json` deve conter:

- `snapshot_version`;
- timestamp;
- digest/version dos catálogos usados;
- providers realmente candidatos;
- modelo candidato por tier/effort;
- capacidades relevantes àquele plano;
- billing profile usado;
- IDs de evidência/benchmark, não longos textos;
- source refs compactos.

`MODEL_MATRIX.md` serve para auditoria humana e **nunca deve ser incluído automaticamente no prompt de worker**.

### 8.5. Provider Profile Layer

Separar “provider de modelo” de “harness de execução”.

Hoje parte da implementação assume:

```text
provider == CLI/harness
```

Isso não funciona bem para GLM e DeepSeek porque ambos suportam protocolos já usados por Claude Code/Codex.

Nova abstração:

```json
{
  "id": "deepseek",
  "harness": "claude",
  "command": "claude",
  "env_profile": {
    "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
    "ANTHROPIC_AUTH_TOKEN_ENV": "DEEPSEEK_API_KEY"
  }
}
```

No nível do usuário, `deepseek` continua aparecendo como opção simples:

```text
pae resume --provider deepseek
```

Internamente, reutiliza o adapter do harness Claude ou Codex.

**Nunca duplicar todo o adapter de `run_isolated.py` para cada API compatível.**

---

# Parte IV — Providers e modelos suportados

## 9. Lista de opções da skill

A configuração deve apresentar, quando instalados/configurados:

| Opção | Tipo interno | Estado proposto |
|---|---|---|
| `claude` | native Claude Code harness | first-class |
| `codex` | native Codex harness | first-class |
| `antigravity` | native agy harness | first-class opcional |
| `qwen` | native/compatible harness | first-class opcional |
| `kimi` | native harness | first-class opcional |
| `trae` | native harness | first-class opcional |
| `muse` | native Muse Code harness | **novo da PR #17** |
| `glm` | provider profile sobre Anthropic/OpenAI protocol | **novo requisito** |
| `deepseek` | provider profile sobre Anthropic/Responses protocol | **novo requisito** |
| `gemini` | legado enquanto a CLI antiga permanecer suportada | compatibility only |

A skill não deve promover Gemini legado a primeira classe apenas porque a PR #17 antiga o fazia.

---

## 10. GLM / Z.AI

### 10.1. Modelos atuais a considerar

- `GLM-5.3-Flash`
- `GLM-5.3`

O GLM Coding Plan oficialmente suporta ambos, e o plano é compatível com Claude Code e outros coding tools. Também existem endpoints Anthropic Messages, OpenAI Chat Completions e OpenAI Responses.

### 10.2. Economia

O catálogo deve suportar tanto API quanto Coding Plan.

API atual por 1M tokens:

| Modelo | input | cached input | output |
|---|---:|---:|---:|
| GLM-5.3-Flash | $0.15 | $0.03 | $0.50 |
| GLM-5.3 | $1.40 | $0.26 | $4.40 |

No Coding Plan, custo não é simplesmente dólares/tokens. Existe fórmula de créditos:

```text
credits = (
    input_tokens * input_multiplier
  + cached_input_tokens * cached_multiplier
  + output_tokens * output_multiplier
) / 10000
```

Multiplicadores atuais:

```text
GLM-5.3       input 6.9 / cached 1.7 / output 24
GLM-5.3-Flash input 2.3 / cached 0.56 / output 8
```

Há desconto de 50% off-peak e limites por janela de 5h + semana.

Portanto, o `effective_cost` deve aceitar unidade de **credits**, não apenas USD.

### 10.3. Effort

GLM-5.3 suporta `low`, `high`, `max`, com thinking sempre ligado. O catálogo deve mapear os levels lógicos sem inventar níveis nativos inexistentes:

```text
low    -> low
medium -> high
high   -> high
xhigh  -> max
max    -> max
```

Esse mapping deve ser metadata do catálogo, não hardcoded no runner.

### 10.4. Bootstrap policy

A skill não deve presumir permanentemente:

```text
GLM-5.3 > GLM-5.3-Flash
```

por nome.

Como bootstrap atual:

- Flash é candidato forte para `economy` e `standard`;
- GLM-5.3 e GLM-5.3-Flash podem ocupar `advanced` quando evals do workload demonstrarem qualidade suficiente com melhor custo esperado;
- GLM-5.3 só deve subir para `strong` se evidência local realmente atingir o floor daquele workload; o nome do modelo não autoriza promoção;
- Flash pode mudar de banda se benchmarks/telemetry mostrarem melhor custo por sucesso naquele workload.

---

## 11. DeepSeek

### 11.1. Modelos atuais

- `deepseek-flash` → atualmente DeepSeek V4.1 Flash;
- `deepseek-v4-pro` → V4 Pro 0813 enquanto disponível.

Ambos oferecem 1M de contexto, tool calls, JSON, Responses API e Anthropic API. `deepseek-flash` também tem visão.

### 11.2. Informação importante para o roteador

O nome “Pro” não deve ser interpretado como ordem de qualidade fixa.

O V4.1 Flash é mais novo e a própria DeepSeek publica resultados em vários benchmarks agentic/coding acima do V4 Pro anterior.

Assim, o catálogo deve permitir:

```text
modelo A melhor em coding-agent
modelo B melhor em outro workload
```

sem uma hierarquia global única.

### 11.3. Preços atuais por 1M tokens

| Modelo | cache hit off-peak/peak | cache miss off-peak/peak | output off-peak/peak |
|---|---:|---:|---:|
| deepseek-flash | $0.003 / $0.006 | $0.15 / $0.30 | $0.60 / $1.20 |
| deepseek-v4-pro | $0.022 / $0.044 | $0.66 / $1.32 | $1.98 / $3.96 |

O cálculo econômico precisa conhecer o horário atual, mas **não deve atrasar uma execução só para esperar off-peak**, salvo se o usuário explicitamente habilitar execução adiada.

### 11.4. Harness

DeepSeek possui integração oficial tanto com Claude Code quanto com Codex.

Portanto:

```text
deepseek profile + claude harness
```

e

```text
deepseek profile + codex harness
```

podem coexistir.

O profile deve declarar qual harness está sendo usado e o resolvedor deve levar em conta diferenças de cache/scaffolding/compatibilidade do harness.

---

## 12. Muse

Muse deve ser preservado do escopo da PR #17 como provider nativo.

O modelo atual relevante é `Muse Spark 1.3`, destinado a coding e workflows agentic/long-horizon.

Requisitos:

- `muse exec --json` para execução headless;
- worker write-enabled dentro das proteções do Muse;
- summary read-only;
- model/effort explicitáveis quando suportados;
- parsing robusto de JSON/JSONL;
- provider test e CLI doctor;
- sem assumir que `Muse Spark 1.3` permanecerá eternamente como ID default: catálogo/freshness deve tratar o release como dado atualizável.

---

# Parte V — Seleção de modelo: melhor qualidade com economia

## 13. Princípio central

O roteador não deve escolher “o modelo mais barato”.

Ele deve escolher:

> **o candidato de menor custo esperado que satisfaça um piso de qualidade e capacidade compatível com o risco da tarefa.**

### 13.1. Duas etapas obrigatórias

Primeiro:

```text
deterministic semantic floor
```

Depois:

```text
economic candidate selection above the floor
```

O segundo estágio jamais pode reduzir o primeiro.

---


### 13.2. Novo tier `advanced`: faixa de alto valor entre `standard` e `strong`

A arquitetura futura SHALL adotar cinco tiers canônicos:

| Alias portátil | Tier canônico | Intenção |
|---|---|---|
| F1 | `economy` | descoberta, leitura, transformação e mudanças mecânicas fortemente verificáveis |
| F2 | `standard` | implementação cotidiana bem delimitada |
| F3 | `advanced` | modelos de alta competência e excelente relação qualidade/custo, úteis antes de pagar por frontier premium |
| F4 | `strong` | decisões/implementações difíceis, alto risco, debugging sutil ou validação fraca |
| F5 | `max` | frontier/long-horizon excepcional ou falha comprovada dos níveis inferiores |

`L1–L5` continua sendo alias do eixo de esforço `low|medium|high|xhigh|max`.

O novo `advanced` **não é uma afirmação de ranking universal entre marcas**. Benchmarks de 2026 mostram que a ordenação muda por workload: Sonnet 5.5 supera modelos mais caros em alguns testes; Muse Spark 1.3 Max é competitivo com Sonnet 5.5 High/Medium em vários índices agregados; GLM-5.3/Flash apresenta excelente eficiência em coding/agentic workloads. Portanto, `advanced` é uma **faixa de roteamento capability/cost-aware**, preenchida somente quando a evidência do workload mostra que o modelo satisfaz o piso da tarefa.

Bootstrap candidates para F3, quando realmente instalados/configurados e elegíveis:

- Muse Spark 1.3, especialmente em coding/agentic workloads onde sua evidência local o coloca acima do baseline `standard`;
- GLM-5.3 e/ou GLM-5.3-Flash, dependendo de effort, workload, harness e telemetria local;
- outros modelos futuros de alto valor que satisfaçam o mesmo contrato.

Regras obrigatórias:

1. A ausência de GLM, Muse ou qualquer provider opcional **não pode alterar negativamente o plano**.
2. Providers/modelos não instalados, não autenticados ou não configurados não entram no `MODEL_MATRIX`, nas opções de rota nem no texto do TODO.
3. Se o floor for `advanced` e não existir candidato F3 elegível, subir para o primeiro candidato `strong`; nunca reduzir silenciosamente para `standard`.
4. Se o floor for `standard`, um candidato `advanced` pode ser escolhido quando tiver menor custo esperado por sucesso validado.
5. Escalation ladders devem pular tiers vazios.
6. Inserir `advanced` não reinterpreta planos antigos: `strong` continua significando `strong`, e `max` continua `max`.
7. A classificação de um modelo em F3 deve ser workload-specific e versionada no catálogo; nome de produto, marketing ou preço não basta.

Bootstrap de mapeamento para orientar implementação — **somente candidates disponíveis entram na matrix real do plano**:

| Provider/profile | `economy` F1 | `standard` F2 | `advanced` F3 | `strong` F4 | `max` F5 |
|---|---|---|---|---|---|
| Claude | Haiku/current economy | Sonnet 5.5 | vazio por default | Opus 5.5 | Fable/current max, conforme catálogo/evals |
| Codex | GPT-6 Luna | GPT-6.1 Sol | vazio por default | GPT-6 Astra | Astra em effort superior, conforme catálogo |
| GLM/Z.AI | GLM-5.3-Flash low quando elegível | GLM-5.3-Flash | GLM-5.3-Flash max e/ou GLM-5.3 conforme eval | somente se eval local atingir F4 | não assumir |
| Muse | somente se futuro eval justificar | Muse Spark em workload delimitado quando suficiente | Muse Spark 1.3 como candidato principal de alto valor | somente se eval local atingir F4 | não assumir |
| DeepSeek | V4.1 Flash | V4.1 Flash em classes adequadas | somente se eval local justificar | não assumir | não assumir |

A tabela é **bootstrap, não hardcode de qualidade**. O catálogo dinâmico, a task class e a telemetry podem mudar a colocação. Em particular, Sonnet 5.5 atual supera Muse/GLM em alguns workloads e perde/empata em outros; por isso o router não deve interpretar F3 como “marca X é sempre melhor que F2”.

Evidência atual que motiva a faixa:

- Anthropic recomenda comparar **custo por tarefa**, inclusive modelo maior em effort menor versus modelo menor em effort maior, e mostra Sonnet 5.5 muito próximo de Opus 5.5 em vários workloads: https://www.anthropic.com/claude-sonnet-5-5
- Meta descreve Muse Spark 1.3 como modelo para long-horizon coding/agentic work, com menos turnos/tokens desnecessários: https://ai.meta.com/tools/muse/
- Artificial Analysis, como evidência secundária e não autoridade do roteador, mede Muse Spark 1.3 Max próximo/superior a Sonnet 5.5 Medium/High em parte de seu conjunto, com custo menor em seu modelo de preços: https://artificialanalysis.ai/models/comparisons/claude-sonnet-5-5-medium-vs-muse-spark-1-3
- Z.AI reporta GLM-5.3 e GLM-5.3-Flash como modelos de coding/agentic efficiency, com ganhos relevantes de qualidade por output token: https://z.ai/blog/glm-5.3 e https://z.ai/blog/glm-5.3-flash


## 14. Candidate eligibility

Antes de comparar preços, eliminar candidatos incompatíveis.

O catálogo deve poder filtrar por:

- required model tier/floor;
- harness disponível;
- autenticação/configuração disponível;
- context window mínimo;
- multimodal/vision;
- tool calls;
- structured output/schema;
- Anthropic API / Responses API;
- effort requerido;
- sandbox/read-only semantics;
- platform/OS;
- concurrency/rate limit;
- user policy;
- privacy/data-retention constraints quando configuradas.

Um modelo mais barato que não consegue executar corretamente o harness não é candidato.

---

## 15. Estimativa de custo efetivo

### 15.1. API

```text
effective_cost =
  uncached_input * input_rate
+ cached_input * cached_rate
+ cache_write_input * cache_write_rate
+ output * output_rate
+ tool_fees
```

### 15.2. Subscription/credits

Não converter artificialmente toda assinatura em preço fixo por token.

Usar:

```text
quota_cost = fraction_of_window_consumed
marginal_cash_cost = overage_or_external_api_cost
```

Para GLM, usar a fórmula oficial de créditos.

Para planos cuja quota interna não seja mensurável oficialmente, permitir configuração do usuário e usar somente métricas realmente observadas pelo CLI/API.

### 15.3. Custo esperado por sucesso

O preço de uma tentativa não basta.

Conceitualmente:

```text
expected_validated_cost(candidate) =
    attempt_cost(candidate)
  + P(failure | task_class, candidate) * expected_retry_cost
```

Não precisa começar com uma regressão sofisticada. O requisito inicial é armazenar dados suficientes para estimar isso no futuro.

---

## 16. Qualidade como constraint, não só score

Para cada classe de tarefa, definir um piso de qualidade/risco.

Exemplo:

```text
mechanical + strong validation
  → pode otimizar agressivamente por custo

architecture + weak validation
  → floor strong/high; custo é critério secundário
```

Para tarefas de risco alto, usar lower confidence bound conservador da evidência de qualidade em vez da média pontual quando houver telemetry suficiente.

---

## 17. Roteamento por etapa, não pelo tamanho do request

Pesquisa recente em routing de agentes mostra que a complexidade varia dentro da mesma trajetória. Um passo de planning pode exigir frontier enquanto formatação/test generation pode usar modelo barato.

A arquitetura deve manter o princípio já existente na skill:

```text
route each semantic leaf, not parent request
```

No ORCHESTRATED:

- cada TODO recebe seu floor;
- `design_route` pode usar um modelo mais forte que implementação;
- exploração pode usar um modelo econômico separado;
- summary usa rota econômica;
- revisão forte só quando risco/weak validation justificarem.

Não adicionar um router LLM a cada step. A decisão deve usar sinais persistidos + catálogo + política determinística.

---

## 18. Route by marginal quality gain

Uma tarefa não deve ir para frontier porque “é difícil” de forma abstrata.

A pergunta econômica melhor é:

> “Qual o ganho esperado de sucesso ao subir do melhor candidato barato para o próximo candidato forte?”

Se o ganho marginal esperado for pequeno e a validação for forte, escolher o mais barato.

Se o ganho marginal for significativo, ou falha silenciosa for cara, subir.

Essa estratégia deve ser implementada somente depois de telemetry/evals suficientes; a primeira versão usa floors + regras conservadoras.

---

# Parte VI — Cache e economia de contexto

## 19. Cache é parte do custo do modelo

Coding agents reutilizam grandes prefixos de instruções, tools e contexto. Portanto, um modelo com input nominal mais caro pode ter custo efetivo menor se sua rota reutilizar cache significativamente melhor.

A policy deve receber:

```text
estimated_cache_hit_ratio
cache_read_rate
cache_write_rate
cache_ttl
model/effort cache compatibility
```

### 19.1. OpenAI/Codex

Para modelos atuais, prompt caching pode reduzir input reutilizado em até uma ordem de grandeza ou mais. GPT-6.1 Sol possui cache read especialmente barato.

Requisitos:

- instruções/tools estáveis no começo do prompt;
- conteúdo dinâmico do TODO no final;
- não reordenar tools sem necessidade;
- monitorar cached/write/uncached tokens reais;
- não alternar modelo/effort por pequenas economias quando isso destrói um prefixo valioso.

### 19.2. Claude

O cache cobre `tools`, `system`, `messages` nessa ordem, e pode usar caching automático ou breakpoints explícitos.

Requisitos:

- prefixo comum dos workers byte-stable sempre que possível;
- evitar inserir timestamp/task id no prefixo estável;
- separar conteúdo invariável de task payload;
- usar TTL maior apenas quando duração do plano justificar o custo de write;
- evitar mudanças desnecessárias de model/effort no meio de um fluxo com alto cache affinity.

### 19.3. GLM

Como o Coding Plan cobra cached input com multiplicador bem menor, cache hit deve entrar diretamente no estimador de créditos.

### 19.4. DeepSeek

Cache hit tem custo extremamente inferior ao miss. Logo, um profile DeepSeek deve preservar prefix affinity sempre que a qualidade não exigir mudança de harness/modelo.

---

## 20. Sticky routing com limite

Para trabalhos sequenciais fortemente relacionados, preferir permanecer no mesmo:

```text
provider + harness + model + effort
```

quando:

- o candidato ainda satisfaz o floor;
- cache esperado é alto;
- não houve falha semântica que exija escalada;
- o ganho de trocar rota não compensa cache miss/context reconstruction.

Sticky routing **não é lock-in**: falha, risco ou capability requirement vencem afinidade de cache.

---

# Parte VII — Refresh do catálogo sem desperdiçar tokens

## 21. Ordem das fontes

O refresh deve usar a fonte mais barata e determinística primeiro:

1. API/CLI machine-readable do provider;
2. versão/configuração local da CLI;
3. documentação oficial;
4. benchmark independente recente;
5. fallback versionado que veio com a skill.

Web content nunca deve definir sozinho um comando executável/model ID sem validação contra fonte oficial/metadata.

---

## 22. Freshness independente

Não usar “refaça toda pesquisa diariamente”.

Cada facet possui freshness própria:

```text
availability/model list
pricing
capabilities
effort mapping
benchmark evidence
local CLI version
```

Refresh triggers:

- primeiro uso sem cache;
- CLI/provider version mudou;
- selected model não existe mais;
- provider devolve invalid/unknown model;
- source digest/ETag mudou;
- TTL daquele facet expirou;
- usuário roda `pae models refresh`;
- plano muito antigo é retomado e snapshot não satisfaz freshness policy.

Durante execução normal, catálogo fresh deve causar **zero pesquisas web** e **zero chamadas de modelo adicionais**.

---

## 23. Refresh seguro

- escrita atômica;
- lock por provider;
- refresh fora de tentativa de worker em andamento;
- plan snapshot versionado;
- erro de refresh mantém último snapshot validado quando ainda dentro de grace policy;
- nunca sobrescrever catálogo válido com resposta parcial;
- não contar “model id invalid porque catálogo mudou” como falha funcional do TODO.

### 23.1. Refresh explícito durante planos longos

Planos podem permanecer ativos por muitos dias ou semanas. Nesse intervalo, um provider pode lançar um modelo novo, retirar um alias, alterar effort/capabilities/preço ou mudar a relação qualidade/custo entre os tiers. O usuário precisa poder pedir **proativamente** uma atualização da tabela de modelos/levels sem recriar o plano.

A skill SHALL oferecer uma intenção/CLI explícita equivalente a:

```bash
pae models status --plan .ai-work/<plan-id>
pae models diff --plan .ai-work/<plan-id>
pae models refresh --plan .ai-work/<plan-id>
```

Semântica:

1. `status` mostra idade/digest do snapshot, providers realmente elegíveis e facets stale, sem geração/model call.
2. `diff` compara o snapshot do plano com o catálogo compartilhado/current sources e mostra mudanças de modelos, capabilities, level placement, effort e economics sem alterar o plano.
3. `refresh --plan` atualiza apenas providers instalados/configurados/elegíveis, recompõe `MODEL_MATRIX.json/md`, grava provenance/fonte/data/digest e passa a usar a nova resolução em **tentativas futuras**.
4. TODOs `completed` nunca são reabertos só porque saiu um modelo novo.
5. Uma tentativa `in_progress` nunca é interrompida para trocar modelo; a nova matrix vale na próxima tentativa/task.
6. TODOs `pending` preservam seus semantic floors/difficulty signals; a resolução concreta é recalculada contra o catálogo novo.
7. Reclassificar a dificuldade/floor de TODOs pendentes é uma operação diferente e explícita (por exemplo `--reclassify-pending`) porque nova disponibilidade de modelos não prova que a dificuldade da tarefa mudou.
8. Nenhuma atualização pode reduzir silenciosamente um floor existente. Um novo modelo pode preencher `advanced`, `strong` ou outro tier somente se sua evidência/capabilities satisfizerem o contrato daquele workload.
9. Providers ausentes continuam ausentes; refresh não transforma catálogo global em dependência do plano.
10. A mudança deve registrar um pequeno audit trail old-snapshot-digest → new-snapshot-digest + motivos/fontes, sem copiar benchmark/doc prose para worker context.

Além do comando explícito, `pae resume/current/status` SHOULD emitir apenas um aviso curto e não bloqueante quando o snapshot do plano estiver stale pela freshness policy ou quando o catálogo compartilhado possuir versão mais nova:

```text
Model map may be stale; run 'pae models diff --plan <plan>' or
'pae models refresh --plan <plan>' to review current models.
```

Esse aviso não deve fazer web research automaticamente. O objetivo é dar agência ao usuário e permitir refresh no momento que ele escolher.

---

# Parte VIII — Telemetry e aprendizado local

## 24. Dados por tentativa

Registrar somente metadata operacional, sem prompts/código:

```text
task_class/signals
validation_strength
provider profile
harness
model
effort
input tokens
cached input tokens
cache write tokens
output tokens
subscription credits / dollar cost when measurable
latency
attempt outcome
failure_class
validation pass/fail
retry count
```

### 24.1. Objetivo

Calibrar:

- qual modelo realmente resolve cada classe de tarefa;
- qual effort é necessário;
- custo por sucesso;
- cache hit real;
- quanto fallback/escalation custam;
- se benchmark externo representa o workspace real.

### 24.2. Restrições

- telemetry local por padrão;
- nenhum código/prompt enviado a serviço de routing;
- jamais reduzir abaixo do deterministic floor devido a telemetry;
- exigir amostra mínima antes de usar histórico para alterar escolha;
- routing deve continuar explicável/auditável.

---

# Parte IX — Mudanças necessárias na branch `main`

## 25. `skill/plan-and-execute/scripts/routingctl.py`

Manter responsabilidades atuais:

- semântica dos tiers;
- floors determinísticos;
- failure classes;
- escalation ladders.

Modificar para:

- aceitar aliases F1–F5/L1–L5;
- delegar catálogo concreto ao novo `model_catalog.py`;
- remover dependência de um único `CURRENT_MODELS` como verdade runtime;
- manter um fallback embarcado versionado para bootstrap/offline;
- expor API determinística de `candidate_routes(task_requirement, catalog, policy)`;
- suportar cost-aware selection sem fazer network/model calls.

## 26. Novo `scripts/model_catalog.py`
Responsável por:

- schema do catálogo;
- normalize/validate;
- capability filtering;
- economics normalization;
- effort alias mapping;
- source/freshness metadata;
- catalog digest/version.

Sem CLI/web calls diretas.

## 27. Novo `scripts/model_catalogctl.py`

Responsável por:

```text
status
show
refresh
validate
snapshot
```

Exemplos:

```bash
pae models status --json
pae models refresh --provider deepseek
pae models refresh --provider glm
pae models show --provider claude --json

# Plano longo: revisar/atualizar o snapshot sem recriar o plano
pae models status --plan .ai-work/<plan-id> --json
pae models diff --plan .ai-work/<plan-id>
pae models refresh --plan .ai-work/<plan-id>
```

A implementação deve fazer probing determinístico e somente solicitar web/manual research quando metadata local/oficial não for suficiente.

## 28. `scripts/routing_config.py`

Adicionar providers user-facing:

```text
muse
glm
deepseek
```

Introduzir provider profile schema:

```json
{
  "harness": "claude|codex|native",
  "command": "...",
  "env": {
    "BASE_URL": "...",
    "TOKEN_ENV": "NAME_OF_ENV_ONLY"
  }
}
```

Requisitos:

- segredo nunca persistido;
- apenas nome da variável de ambiente;
- `--show` redige qualquer campo sensível;
- aliases/profile inheritance validados;
- current v1/v2 config continua legível.

## 29. `scripts/configure.py`

Wizard deve:

- descobrir native harnesses;
- oferecer GLM/DeepSeek quando credenciais/profile forem configuráveis;
- explicar harness usado;
- permitir billing mode (`subscription`/`api`/`custom quota` quando relevante);
- escolher primary/fallback por tier;
- não executar prompt de teste para autenticação;
- nunca solicitar API key em texto persistido.

## 30. `scripts/planctl.py`

Preferencialmente **não aumentar `SCHEMA_VERSION`**.

Adicionar apenas:

- normalization de aliases F/L na entrada;
- plan snapshot metadata do catálogo fora da semântica dos TODOs;
- audit check de snapshot quando configurado.

TODOs continuam canônicos:

```text
provider: auto
model_tier: economy|standard|advanced|strong|max
reasoning_effort: low|medium|high|xhigh|max
```

## 31. `scripts/run_isolated.py`

Refatorar provider dispatch para composição:

```text
Provider Profile
      ↓
Harness Adapter
```

Adapters reutilizáveis:

```text
ClaudeHarnessAdapter
CodexHarnessAdapter
NativeMuseAdapter
...
```

Assim:

```text
claude    -> ClaudeHarnessAdapter + Anthropic profile
glm       -> ClaudeHarnessAdapter + Z.AI profile
deepseek  -> ClaudeHarnessAdapter ou CodexHarnessAdapter + DeepSeek profile
muse      -> NativeMuseAdapter
```

Adicionar:

- per-attempt effective cost telemetry;
- native effort mapping;
- invalid-model → refresh once → retry sem functional failure;
- provider profile provenance;
- capability eligibility before dispatch.

## 32. `references/MODEL_ROUTING.md`

Manter curto e provider-neutral.

Adicionar apenas:

- aliases F/L;
- catalog resolver;
- deterministic floor → eligible candidates → economical choice;
- cache affinity;
- no under-routing;
- expected validated-task cost.

Não incluir tabelas atuais de cada vendor.

## 33. Novo `references/MODEL_CATALOG.md`

Carregar somente em:

- configure;
- refresh;
- manutenção;
- troubleshooting do catálogo.

Conteúdo:

- source precedence;
- freshness;
- capability schema;
- economics schema;
- provider profiles;
- benchmark evidence rules;
- security.

## 34. `references/MODEL_ROUTING_<PROVIDER>.md`

Provider docs devem continuar lazy.

Adicionar novos documentos somente quando há comportamento específico suficiente para justificar contexto:

```text
MODEL_ROUTING_MUSE.md
MODEL_ROUTING_GLM.md
MODEL_ROUTING_DEEPSEEK.md
```

Mas GLM/DeepSeek devem enfatizar profile/harness e economia, sem copiar documentação inteira dos vendors.

## 35. `references/ORCHESTRATION.md`

Incorporar da PR #17:

- plan provider-neutral;
- snapshot de catálogo;
- refresh sem replan;
- provenance da rota concreta.

Melhoria:

- não exigir live web research em todo plano;
- `MODEL_MATRIX` vem do registry fresh;
- atualizar somente providers candidatos.

## 36. `references/PLANNING_PROTOCOL.md`

Depois dos TODO boundaries estabilizarem:

1. classificar sinais do TODO;
2. obter deterministic floor;
3. verificar providers candidatos no catalog;
4. criar snapshot compacto;
5. reviewer verifica overspend/under-routing/capability mismatch.

O planning model não precisa ler benchmark prose se o registry já contém evidence IDs normalizados.

## 37. `references/PLAN_SPEC.md`

Documentar:

- provider auto como default;
- tiers atuais como canonical;
- F/L como aliases;
- concreto proibido em route fields;
- catalog snapshot não faz parte da semântica do TODO.

## 38. `SKILL.md`

Alteração mínima.

Adicionar no máximo algumas linhas ao controle principal:

> route semantic floors deterministically; resolve concrete provider/model through the current catalog; refresh catalog only when stale/unavailable.

Não colocar providers, preços, benchmarks nem regras longas no entrypoint.

## 39. `agents/openai.yaml`

Não aumentar significativamente o prompt default.

Adicionar uma frase curta sobre provider-neutral task routes e catalog resolver somente se necessário para manter comportamento consistente.

## 40. `bin/plan-and-execute.js`

Adicionar:

```text
muse
glm
deepseek
```

em:

- `--provider`;
- help;
- `doctor`;
- `models` subcommand;
- JSON doctor report.

## 41. `tools/validate-skill.js` e `lib/installer.js`

Exigir os novos arquivos essenciais.

Evitar o problema já encontrado em mudanças anteriores: arquivo de runtime novo não pode existir sem ser requerido pelo pacote/validator.

## 42. `tools/run-skill-self-test.js`

Toda nova suíte precisa entrar explicitamente no runner.

Não repetir o erro de criar self-test que CI não executa.

---

# Parte X — Estratégia de benchmark e qualidade

## 43. Evidência de qualidade por workload

Não manter “modelo X = strong” apenas por reputação.

Registrar evidência por classe:

```text
repository coding
terminal agent
code review
debugging
architecture/security
long-horizon
vision/UI
tool use
automation
```

Um benchmark não deve ser usado fora do workload que realmente mede.

### 43.1. Precedência

1. eval interno da própria skill/workspace;
2. benchmark independente reproduzível e atual;
3. benchmark oficial do vendor com metodologia conhecida;
4. ausência de evidência → conservative fallback.

Vendor benchmark nunca deve sozinho autorizar rebaixar abaixo do floor.

---

## 44. Current bootstrap observations — não regras permanentes

### GLM

GLM-5.3 e GLM-5.3-Flash apresentam forte desempenho em coding/agent workloads e custo muito baixo, especialmente Flash e Coding Plan. Eles devem entrar no candidate pool.

### DeepSeek

DeepSeek V4.1 Flash atualmente apresenta evidência de coding-agent superior ao V4 Pro anterior em vários benchmarks, além de custo muito menor e visão. Isso é um exemplo concreto de por que o nome “Pro” não pode definir o tier.

### Muse

Muse Spark 1.3 é voltado a long-horizon coding e agentic workflows e deve ser avaliado como provider nativo, mas a qualidade deve ser medida no harness real da skill.

---

# Parte XI — Otimizações adicionais de token e qualidade

## 45. Zero model call para routing

O roteamento de provider/model não pode chamar LLM separado.

Sinais de tarefa são produzidos durante planning/execução que já aconteceria. O resto é programa determinístico.

Isso evita:

```text
router-model call
+ latency
+ tokens
+ nova fonte de erro
```

## 46. Compact plan snapshot

A matrix não deve conter:

- artigos copiados;
- longas justificativas de benchmark;
- tabelas globais que o plano não usa.

Ela deve conter ids/digests e apenas candidatos relevantes.

## 47. Worker não lê catálogo

O worker recebe:

```text
model already selected
+ task definition
+ assigned context
+ acceptance
+ validation
```

Nunca recebe:

```text
MODEL_MATRIX.md inteiro
pricing tables
provider benchmark history
future routing candidates
```

## 48. Search-before-read para model discovery

Quando refresh web for realmente necessário:

- consultar endpoint/CLI primeiro;
- abrir somente documentação oficial relevante;
- buscar benchmark pelo modelo/workload preciso;
- persistir conclusão estruturada;
- não guardar texto do artigo.

## 49. Same-prefix worker template

Separar worker prompt:

```text
STATIC PREFIX
- role/rules
- completion schema
- safety
- tool contract

DYNAMIC SUFFIX
- task
- paths
- context refs
- validation
```

Testar byte stability no CI quando possível.

## 50. Context affinity-aware scheduling

Se dois TODOs não são independentes e o segundo reutiliza decisões profundas do primeiro, não isolar apenas por regra processual.

Se são independentes, fresh context protege o modelo caro de informação inútil.

Preservar a regra atual: isolamento é instrumento econômico/de qualidade, não objetivo.

## 51. Two-phase leaves

Preservar `design_route`.

Boa aplicação:

```text
strong/frontier design
      ↓ bounded design artifact
standard implementation
      ↓ deterministic validation
```

Só quando implementação é grande o suficiente para pagar a divisão. Para uma pequena mudança difícil, um único worker forte pode ser mais barato.

## 52. Tool output budgets

Continuar:

- logs completos no disco;
- bounded tail no prompt;
- path para evidência bruta;
- fingerprint de erro repetido;
- nunca copiar stack trace gigante para todo retry.

## 53. Provider-switch economics

Em indisponibilidade:

```text
same logical tier on fallback provider
```

antes de concluir que é necessário modelo mais forte.

Em falha semântica:

```text
capability escalation
```

Provider availability e model capability continuam ortogonais.

---

# Parte XII — Segurança e confiabilidade

## 54. Dados externos são não-confiáveis

Benchmark/web docs podem influenciar ranking, mas não podem introduzir diretamente:

- executable path;
- shell args;
- environment names não permitidos;
- API key;
- arbitrary model command.

IDs executáveis precisam ser confirmados por fonte oficial/machine-readable/configuração explícita.

## 55. Secrets

- nenhuma API key no catálogo;
- nenhuma API key no plano;
- nenhuma API key no `pae configure --show`;
- profiles armazenam somente o nome da env var que contém a credencial;
- logs removem authorization headers/tokens.

## 56. Determinismo

Dado:

```text
task signals
catalog snapshot
routing config
availability state
failure history
```

a escolha deve ser reproduzível.

Não usar random/bandit como default de produção.

Exploração experimental só em benchmark/shadow mode.

---

# Parte XIII — Testes obrigatórios

## 57. Unit tests

Adicionar cobertura para:

- F/L aliases → canonical tier/effort;
- legacy plan unchanged;
- catalog schema;
- catalog freshness;
- source precedence;
- capability filtering;
- native effort aliases;
- API/subscription cost calculations;
- cache-aware cost;
- DeepSeek peak/off-peak;
- GLM credit formula;
- catalog atomic write/lock;
- invalid model refresh;
- credential redaction.

## 58. Provider/harness tests

### Muse

- worker command;
- read-only summary;
- JSON/JSONL result parsing;
- model/effort forwarding.

### GLM

- Claude harness environment/profile;
- no credential leakage;
- model/effort mapping;
- Coding Plan credit accounting.

### DeepSeek

- Claude harness profile;
- Codex/Responses profile;
- Flash/Pro exact IDs;
- vision eligibility;
- effort mapping;
- peak/off-peak pricing.

## 59. Integration tests

- provider switch sem alterar TODO;
- model deprecado → refresh → retry;
- quota → equivalent fallback route;
- semantic failure → escalation;
- environmental failure → no escalation;
- stale catalog offline → conservative fallback;
- old schema 1–4 resume;
- Windows + Linux.

## 60. Token-budget regressions

CI deve provar:

- `SKILL.md` não cresce além do budget atual sem justificativa;
- default prompt permanece compacto;
- normal plan execution não carrega `MODEL_MATRIX.md` no worker;
- catálogo fresh causa zero web refresh;
- routing causa zero model calls;
- new provider docs são lazy.

---

# Parte XIV — Evals e rollout

## 61. Shadow mode

Antes de mudar auto-routing:

```text
current_route = rota da main
candidate_route = nova policy
actual_execution = current_route
```

Registrar diferença e estimar:

- custo evitável;
- under-routing potencial;
- over-routing;
- cache impact;
- taxa de sucesso esperada.

## 62. Corpus de routing

Criar corpus versionado com tarefas reais/sintéticas:

- mechanical;
- bounded implementation;
- subtle debugging;
- architecture;
- security/concurrency/migration;
- weak validation;
- strong validation;
- long-horizon;
- vision/UI;
- quota/provider failures.

Cada caso declara um **minimum acceptable route**, não um “winner model” permanente.

## 63. Métricas de aceite

Comparar `main` vs nova policy:

```text
validated success rate
first-attempt validated success
attempts / TODO
input tokens
cached tokens
output tokens
quota credits
real USD where measurable
wall time
provider switches
capability escalations
under-routing rate
over-routing rate
```

O objetivo é reduzir custo **sem regressão material de sucesso validado**.

Não aprovar rollout automático baseado somente em custo de token.

## 64. Fases

### Fase A — estrutura sem mudar routing

- provider profiles;
- Muse;
- GLM;
- DeepSeek;
- catalog schema;
- doctor/configure;
- tests.

### Fase B — shared catalog + plan snapshot

- refresh/status;
- `MODEL_MATRIX.json/md`;
- provider switching sem rewrite;
- aliases F/L.

### Fase C — shadow routing

- candidate selection;
- telemetry;
- comparar com policy atual.

### Fase D — auto-routing conservador

Habilitar somente onde:

- deterministic validation é forte;
- under-routing é mensuravelmente baixo;
- economia é material;
- quality floor é preservado.

### Fase E — feedback-aware routing

Usar histórico local para melhorar desempates/custo esperado, mantendo floors estáticos de segurança.

---

# Parte XV — Requisitos formais

## 65. Requisitos funcionais

### FR-001 — Provider-neutral TODO semantics
A skill SHALL manter TODOs independentes do provider/model concreto.

### FR-002 — F/L aliases
A skill SHALL aceitar F1–F5 e L1–L5 como aliases portáveis e SHALL normalizá-los para o vocabulário canônico atual, preservando compatibilidade.

### FR-003 — Dynamic model catalog
A skill SHALL resolver modelos concretos por catálogo atualizável e não por IDs embutidos no TODO.

### FR-004 — Plan-local snapshot
Todo plano ORCHESTRATED SHALL possuir snapshot da resolução relevante em `MODEL_MATRIX.json`; uma representação humana `MODEL_MATRIX.md` SHALL estar disponível para auditoria.

### FR-005 — Snapshot non-semantic
Atualizar a matrix SHALL NOT exigir alterar objetivos, dependências, critérios ou rota lógica dos TODOs.

### FR-006 — Muse
A skill SHALL suportar Muse Code como provider nativo headless.

### FR-007 — GLM
A skill SHALL oferecer `glm` como opção de provider profile, suportando os modelos atuais GLM Coding Plan/API por harness compatível.

### FR-008 — DeepSeek
A skill SHALL oferecer `deepseek` como opção de provider profile, com suporte a Anthropic e Responses/Codex quando configurados.

### FR-009 — Capability filtering
O router SHALL eliminar candidatos incompatíveis antes de otimizar custo.

### FR-010 — Deterministic floor
O router SHALL NOT selecionar rota abaixo do floor derivado dos sinais semânticos da tarefa.

### FR-011 — Failure-based escalation
Escalada de capacidade SHALL permanecer baseada em failure evidence e não em quota/provider outage.

### FR-012 — Provider availability fallback
Quota/capacity SHALL tentar provider equivalente antes de alterar capability tier, respeitando configuração.

### FR-013 — Cache-aware economics
O estimador SHALL considerar cached/uncached/write tokens quando o provider expõe essas métricas.

### FR-014 — Subscription economics
O estimador SHALL suportar créditos/quota como unidade econômica e não forçar conversão artificial para USD.

### FR-015 — Catalog refresh
A skill SHALL atualizar catálogo lazy/provider-scoped e SHALL evitar web research quando cache válido existir.

### FR-016 — Invalid-model recovery
Um erro confirmado de model ID obsoleto SHALL provocar no máximo um refresh controlado antes de ser tratado como erro de configuração; não conta inicialmente como falha funcional do TODO.

### FR-017 — Provenance
Cada tentativa SHALL registrar provider profile, harness, model e native effort concretos.

### FR-018 — Local routing telemetry
A skill SHALL registrar metadata suficiente para medir custo por resultado validado sem armazenar prompt/código no dataset de routing.

### FR-019 — Explainability
A escolha SHALL ser explicável por floor, capabilities, economics e evidência disponível.

### FR-020 — No routing LLM call
A seleção de provider/model SHALL NOT fazer chamada de LLM dedicada.

---


### FR-021 — Five-tier capability lattice
A skill SHALL adotar `economy|standard|advanced|strong|max`, mantendo planos antigos semanticamente estáveis.

### FR-022 — Availability-aware advanced tier
`advanced` SHALL conter apenas candidates realmente disponíveis/configurados para o environment e workload; tier vazio SHALL ser pulado sem inventar provider.

### FR-023 — Advanced value preference
Quando `advanced` e `strong` satisfizerem o mesmo quality floor, a policy SHALL poder preferir F3 por menor expected validated cost.

### FR-024 — Delegation gate
A skill SHALL decidir deterministicamente `tool|keep_root|delegate` a partir de difficulty, validation, blast radius, context affinity, capabilities, availability e coordination overhead.

### FR-025 — Bounded multi-agent execution
Delegation SHALL possuir limites de fan-out, nesting, tokens, output e write isolation; parent SHALL receber artefato compacto, não transcript.

### FR-026 — Provider absence neutrality
Provider/model opcional ausente SHALL desaparecer das opções/snapshots e SHALL NOT bloquear criação ou execução do plano.

### FR-027 — FailureEvidencePacket
Falhas elegíveis SHALL possuir representação compacta estruturada antes de qualquer diagnóstico por modelo.

### FR-028 — Progress-aware stall detection
Elapsed time sozinho SHALL NOT classificar stall; watcher SHALL combinar progress, process/resource evidence e quiet-phase policy.

### FR-029 — Diagnostic authority separation
Diagnostic workers SHALL produzir hipótese/guidance bounded; implementação, failure class autoritativa, comandos e completion permanecem sob owner + deterministic validators.

### FR-030 — Cache-aware delegation
Routing/delegation SHALL considerar cache affinity e SHALL registrar usage/cache metrics quando provider expuser.

### FR-031 — Delegation cost accounting
Métricas SHALL contabilizar root, todos subagents, retries, diagnostics e summaries para custo por resultado validado.

### FR-032 — Large-request retrieval discipline
Primary planning SHALL preservar fragments imutáveis e SHALL recuperar raw evidence por pergunta material em vez de reconstruir o request inteiro em context.

### FR-033 — Quality/economy rollout gate
Nova policy automática SHALL permanecer shadow/opt-in até demonstrar quality non-inferiority e redução material de cost/context por TODO validado.

### FR-034 — Runtime monitoring artifact ownership and cleanup
Artefatos produzidos durante monitoramento/diagnóstico — incluindo logs de validação, JSONL de resource watch, process snapshots, log cursors, temporary reports e arquivos equivalentes — SHALL:
1. nunca ser criados dentro da pasta instalada/source da skill;
2. possuir owner/scope explícito (`task|plan|project-shared|temporary`);
3. possuir retention policy explícita;
4. ser removidos deterministicamente quando o owner termina e nenhuma referência viva de retry, diagnosis, handoff ou auditoria exige retenção;
5. sobreviver apenas quando forem estado compartilhado deliberado, como o `SERVICE_MAP.md`, ou quando uma política de retenção configurada exigir evidência pós-execução.

### FR-035 — User-initiated model-map refresh
Durante um plano ativo, o usuário SHALL poder solicitar atualização explícita do catálogo e da tabela model↔tier/level sem recriar o plano. A operação SHALL atualizar o plan snapshot/provenance e afetar somente futuras resoluções de rota.

### FR-036 — Safe long-plan route rebasing
Refresh de catálogo SHALL preservar requirements, TODO boundaries, dependencies, acceptance, semantic floors e completed work. Tasks pendentes SHALL ser re-resolvidas contra o snapshot novo; tasks em andamento SHALL concluir a tentativa atual; reclassificação de dificuldade SHALL exigir operação explícita separada.

### FR-037 — Initial whole-documentation reconciliation
Antes de iniciar a implementação deste documento, o plano SHALL executar uma revisão baseline de toda a documentação interna da skill/repositório relevante ao produto, reconciliar contradições e acrescentar ao plano/requisitos qualquer informação material descoberta antes de modificar contratos centrais.

## 66. Requisitos não funcionais

### NFR-001 — Backward compatibility
Planos schema 1–4 existentes devem continuar resumíveis.

### NFR-002 — Token neutrality of control plane
A incorporação não deve aumentar materialmente o contexto always-loaded da skill.

### NFR-003 — Determinism
Mesmos inputs + mesmo snapshot devem resultar na mesma rota.

### NFR-004 — Atomicity
Catálogo/snapshot devem usar gravação atômica e locking apropriado.

### NFR-005 — Security
Credenciais não podem ser persistidas nem exibidas.

### NFR-006 — Offline resilience
A skill deve executar com último catálogo válido/fallback conservador quando refresh externo estiver indisponível.

### NFR-007 — Cross-platform
Linux e Windows devem permanecer suportados.

### NFR-008 — Observability
Cada route attempt deve expor métricas de tokens/cache/custo/quota quando provider disponibilizar.

### NFR-009 — Minimal worker context
Workers não recebem benchmark/catalog history.

### NFR-010 — No silent provider semantics drift
Mudança de mapping deve atualizar versão/digest do catálogo e provenance.

---


### NFR-011 — Optional-provider neutrality
Instalar a versão nova sem Muse/GLM/DeepSeek deve preservar o comportamento funcional e o custo de controle próximo ao baseline.

### NFR-012 — Delegation boundedness
Nenhum fluxo pode criar fan-out/nesting ilimitado ou retry recursion.

### NFR-013 — Cache observability
Quando usage metadata existir, cache hit/read/write e route identity devem ser mensuráveis sem inserir telemetry no worker prompt.

### NFR-014 — Evidence compactness
Failure/context/handoff artifacts entregues a modelos devem possuir budgets explícitos e pointers para raw evidence.

### NFR-015 — Clean skill installation
A árvore instalada/source da skill SHALL permanecer imutável durante execução normal quanto a logs/tracking/runtime state. Testes de integração SHALL falhar se uma execução criar novos arquivos transitórios sob `skill/plan-and-execute/` (exceto arquivos deliberadamente versionados pelo desenvolvimento).


# Parte XVI — Critérios de aceitação da demanda

A implementação só pode ser considerada pronta quando:

1. PR17’s provider-neutral/late-binding goals são preservados sem migração desnecessária de TODO schema.
2. `muse`, `glm` e `deepseek` aparecem no `pae` e possuem adapters/profiles testados.
3. Planos antigos continuam resumíveis.
4. Provider switching não reescreve TODOs.
5. `MODEL_MATRIX.json/md` existe como snapshot compacto e não entra automaticamente no worker prompt.
6. Catalog fresh evita web/model research em execução normal.
7. F/L aliases são aceitos mas estado canônico continua compatível com a `main`.
8. Nenhum modelo é escolhido abaixo do deterministic floor.
9. Quota não é interpretada como falta de inteligência.
10. Cache read/write/hit é incorporado ao custo quando disponível.
11. GLM subscription credit formula e DeepSeek peak/off-peak são modeláveis/testáveis.
12. `npm run check` e `npm pack --dry-run` passam em toda matriz de CI suportada.
13. Novos self-tests estão realmente listados no runner da CI.
14. Validator/installer exigem todos os runtime files novos.
15. Shadow eval demonstra que a policy nova não cria regressão material de validated success antes de ser habilitada automaticamente.
16. Um relatório de eval mostra custo/tokens/créditos por TODO validado, não apenas preço por MTok.
17. Execuções de monitoring/validation não deixam logs, cursors, snapshots ou reports transitórios dentro da pasta da skill.
18. Após a conclusão de uma task/plano, artefatos de tracking efêmeros sem referência viva são removidos, enquanto evidência ainda necessária e state project-shared deliberado são preservados.
19. Um plano ativo com snapshot antigo pode executar `models diff/refresh --plan` sem recriar TODOs ou perder progresso.
20. Após refresh, tasks concluídas permanecem concluídas, tentativa em andamento não é interrompida e futuras tentativas usam o snapshot novo.
21. O início da implementação registra uma revisão baseline de toda a documentação interna relevante, com coverage verificável, contradições/staleness identificadas e impactos materiais incorporados ao documento/plano antes dos contratos centrais.

---

# Parte XVII — O que NÃO fazer

1. Não mergear a PR #17 literalmente sobre a `main` atual.
2. Não pesquisar todos os providers na web para cada plano.
3. Não duplicar `economy/standard/advanced/strong/max` com F1–F5 no schema durável sem ganho semântico.
4. Não criar adapters inteiros separados para GLM/DeepSeek se o mesmo harness já suporta seus protocolos.
5. Não escolher modelo por nome (`Pro`, `Flash`, `Max`) como proxy de qualidade.
6. Não usar preço de input isoladamente como custo.
7. Não ignorar cache hit/read/write.
8. Não usar benchmark vendor como autorização para under-routing.
9. Não adicionar router-LLM/JEV apenas para model selection.
10. Não passar model matrix/benchmark notes ao worker.
11. Não transformar quota/capacity em failure_class semântica.
12. Não aumentar SKILL.md com catálogo e pricing voláteis.

---

# Parte XVIII — Fontes principais usadas no redesenho

## Repositório

- PR #17: https://github.com/heavydevs/plan-and-execute/pull/17
- `main`: https://github.com/heavydevs/plan-and-execute

## GLM / Z.AI

- Coding Plan overview: https://docs.z.ai/devpack/overview
- Pricing: https://docs.z.ai/guides/overview/pricing
- Coding Plan quick start / protocols: https://docs.z.ai/devpack/quick-start
- GLM-5.3: https://z.ai/blog/glm-5.3
- GLM-5.3-Flash: https://z.ai/blog/glm-5.3-flash

## DeepSeek

- Models/pricing: https://api-docs.deepseek.com/quick_start/pricing/
- Claude Code integration: https://api-docs.deepseek.com/quick_start/agent_integrations/claude_code/
- Codex integration: https://api-docs.deepseek.com/quick_start/agent_integrations/codex/
- Changelog / V4.1 Flash: https://api-docs.deepseek.com/updates/

## Prompt/cache economics

- OpenAI prompt caching: https://developers.openai.com/api/docs/guides/prompt-caching
- OpenAI GPT-6 caching improvements: https://openai.com/index/better-prompt-caching-for-gpt-6/
- Anthropic prompt caching: https://platform.claude.com/docs/en/build-with-claude/prompt-caching
- Coding Agent Economy / field data: https://www.requesty.ai/coding-agent-economy

## Routing research

- AgentRouter (2026): https://arxiv.org/abs/2609.22951
- Agent-as-a-Router / CodeRouterBench: https://github.com/mdwoicke/llm-agent-as-a-router
- RouteLLM: https://arxiv.org/abs/2406.18665
- FrugalGPT: https://arxiv.org/abs/2305.05176

## Muse

- Meta Muse / Muse Spark: https://ai.meta.com/llama/

---

# Conclusão arquitetural

A PR #17 identificou corretamente um problema real: **planos duradouros não podem depender de uma fotografia fixa dos modelos disponíveis no dia em que foram criados**. Sua estratégia de late binding, matrix por plano, provenance de execução e provider switching é conceitualmente sólida.

O que mudou é que a `main` atual já possui uma camada lógica provider-neutral (`provider:auto`, tiers e efforts), e portanto não é necessário substituir tudo por F/L. A melhor incorporação é manter a semântica atual, aceitar F/L como aliases, mover o catálogo volátil para uma registry compartilhada, gerar snapshots compactos por plano e resolver o modelo concreto no runtime.

A maior melhoria adicional é tratar **harness, provider, modelo e billing como eixos separados**. Isso permite incorporar GLM e DeepSeek sem duplicar runners, preservar Muse como CLI nativo, aproveitar caches de Claude/Codex e calcular custo real de API/assinatura/quota.

A seleção ótima passa a ser:

```text
semantic floor
→ capability filter
→ current catalog
→ cache/quota-aware economics
→ conservative quality constraint
→ deterministic route
→ validation
→ telemetry
→ better future calibration
```

Essa arquitetura mantém a qualidade como restrição dura e usa economia somente no espaço onde várias rotas já são tecnicamente aceitáveis. É a forma mais segura de obter economia significativa de tokens/créditos sem transformar o roteamento em mais uma fonte de instabilidade ou consumo de contexto.

---


# Parte XIX — Propósitos e objetivos completos da skill

Esta seção registra o **contrato de produto** da skill antes da implementação deste documento. O objetivo é evitar regressões funcionais durante a evolução do roteamento. Cada bullet abaixo representa uma finalidade real observada na `main` atual, não apenas uma ideia futura.

- **Orquestrar somente quando a orquestração paga seu próprio custo.** O primeiro objetivo é decidir `DIRECT` versus `ORCHESTRATED`; tarefas coesas pequenas/médias devem continuar no contexto atual sem criar plano, study, TODOs ou workers apenas por cerimônia.
- **Promover trabalho DIRECT tardiamente sem reiniciar o que já foi feito.** Se a tarefa cresce durante a implementação, persistir apenas goal, decisões, resultados validados, paths/symbols, riscos e remaining outcomes; o plano cobre somente o trabalho restante.
- **Sobreviver a requests enormes antes mesmo do plano final existir.** Para prompts/arquivos grandes e estruturalmente amplos, estimar working-set pressure, fragmentar deterministicamente, persistir fragmentos imutáveis, criar digests resumíveis e só depois produzir o input compacto do plano final. Requests menores seguem direto para o plano final.
- **Preservar integralmente a evidência do request sem repetir seu texto em todos os artefatos.** Request original/fragmentos imutáveis são source-of-truth; requirements, TODOs e handoffs referenciam IDs, paths e evidências em vez de copiar parágrafos.
- **Estudar somente o que pode mudar arquitetura, compatibilidade, boundaries, risco ou validação.** O estudo adaptativo começa por busca/indexação barata e amplia leitura/pesquisa somente quando a resposta de uma questão material pode alterar o plano.
- **Transformar o request em rastreabilidade executável.** Cada request part mapeia para requirement observável; cada requirement mapeia para pelo menos um TODO; cada TODO volta às requirements que implementa.
- **Decompor TODOs por coesão de contexto e boundary de validação, não por quantidade de arquivos.** Domínios independentes ficam separados; controller/service/entity/tests que implementam o mesmo invariante podem permanecer juntos.
- **Persistir progresso durável e resumível em disco.** `manifest.json` é autoritativo; subtasks/checkpoints, status, falhas, rotas e resultados permitem retomar após quota, interrupção ou troca de provider sem depender do chat antigo.
- **Separar planning capability de implementation capability.** Primary planning, final planning, hard decisions, design e implementação podem usar rotas diferentes.
- **Resolver poucas decisões difíceis antes do planejamento mecânico.** `hard_decisions` podem ser delegadas a workers fortes e compactadas em decisão/rationale/constraints; um planner mais econômico monta a estrutura restante.
- **Separar design difícil da implementação volumosa quando isso reduz custo total.** `design_route` permite um worker forte produzir um design curto e outro worker mais econômico implementar e validar.
- **Escolher capacidade por leaf e por verificabilidade.** Mechanical + strong validation pode usar rota barata; subtle debugging, cross-cutting risk e silent-failure risk elevam o piso; task grande não implica modelo grande.
- **Escalar por evidência de falha, não por retry cego.** `mechanical`, `semantic`, `environmental`, `budget`, `plan_defect` e `unknown` têm semânticas diferentes; indisponibilidade não é confundida com incapacidade.
- **Separar provider availability de model capability.** Quota, rate-limit, auth/capacity e cooldown tentam fallback equivalente antes de aumentar inteligência.
- **Delegar trabalho descartável a agentes baratos quando o isolamento compensa.** Exploração ampla, localização, análise de evidência ou tarefas mecânicas podem ir para workers baratos; a skill evita criar worker para um grep ou duas leituras óbvias.
- **Permitir múltiplos providers/agentes sem transformar o plano em dependente deles.** TODOs persistem tier/effort/provider lógico; concrete model/harness é resolvido tarde e pode mudar por disponibilidade.
- **Carregar instruções progressivamente.** `SKILL.md` funciona como control plane; referências de routing, planning, provider, monitoring, patterns e lifecycle são abertas somente na fase pertinente.
- **Preservar contexto útil e isolar contexto descartável.** Fresh context não é automaticamente melhor; a skill mantém contexto quando há afinidade de raciocínio e isola discovery/leafs independentes quando a poluição custaria mais.
- **Criar shared context somente por necessidade real.** `CONTEXT.md` é omission-first; scoped contexts atendem apenas subconjuntos estritos; fatos de um único TODO ficam no TODO.
- **Propagar descobertas somente quando validadas e economicamente úteis.** Learnings são direcionais, predeclarados, target-specific e só materializados depois de validação determinística.
- **Manter contratos cross-TODO versionados.** Shared patterns têm revisão, signatories e invalidation seletiva: uma alteração reabre apenas consumidores realmente desatualizados, não o plano inteiro.
- **Validar fora do worker.** Worker report é evidência, não aceitação; o orquestrador executa comandos determinísticos e verifica outcomes, negative cases e integration contracts.
- **Mapear toolchains, serviços e recursos necessários por validação.** `.ai-work/SERVICE_MAP.md` liga cada validation ID aos toolchains/resources/checks; fingerprint evita rediscovery do ambiente quando nada relevante mudou.
- **Detectar validações travadas com evidência operacional.** `resource_watch.py` acompanha processo, progresso, CPU e dependências, com no-progress timeout default de 300s; environment health evita culpar o modelo por Tomcat/MySQL/Selenium/etc.
- **Ler somente linhas novas de logs crescentes.** `log_watch.py` usa cursor persistente por arquivo/pattern, detecta rotation/truncation, limita bytes e matches e evita reenviar erros antigos.
- **Manter logs completos fora do contexto e prompts com evidência limitada.** Full output vai para arquivos; state/worker recebem tail bounded, fingerprint normalizado, failure class e paths para evidência bruta.
- **Não deixar lixo de monitoramento na instalação da skill.** Logs, snapshots, cursors, JSONL, process/resource reports e outros artefatos gerados por `resource_watch.py`, `log_watch.py`, service diagnostics ou mecanismos futuros são runtime state: SHALL ser gravados em workspace controlado do projeto/plano ou diretório temporário apropriado, nunca dentro da pasta instalada/source da skill. Quando a task que os possui termina e a evidência já não é necessária para retry, diagnosis, handoff ou auditoria configurada, esses artefatos efêmeros devem ser removidos deterministicamente.
- **Usar diagnóstico auxiliar somente depois de falha elegível.** Assistant opcional recebe evidência redigida/bounded após falha repetida/ambígua, unhealthy samples ou stall confirmado; nunca aprova tarefa, executa comandos ou muda failure class autoritativamente.
- **Aplicar budgets para impedir runaway workers.** Turn/token/budget limits transformam excesso de consumo em estado resumível, não em loop indefinido.
- **Preservar prompt cache e prefixos estáveis quando o provider suporta.** Root session não muda model/effort automaticamente; tarefas que exigem rota diferente são delegadas, evitando reconstruir contexto enorme em outro modelo.
- **Gerar handoffs e summaries a partir de estado autoritativo compacto.** Nunca concatenar transcript de workers; usar goal, completed tasks, changed files, validation status, risks/follow-ups e evidência de repo.
- **Limpar somente controle efêmero.** Após conclusão, remover plan/study/log control state guardado pelo sentinel, preservando código, testes, artefatos do produto, commits e service map do projeto.
- **Proteger a própria economia/qualidade com regression suites.** Routing evals, tier evals, token-efficiency tests, provider tests, lifecycle/recovery tests e whole-skill validation impedem regressões silenciosas.
- **Usar código determinístico para tudo que não precisa de julgamento.** Hashing, splitting, state transitions, graph validation, path safety, scheduling, fingerprints, lifecycle, routing floors e cleanup não devem consumir LLM.
- **Manter segurança e provenance.** Paths/symlinks, credentials, sandbox/read-only semantics, provider/harness/model/effort e state transitions devem ser verificáveis e auditáveis.

---

# Parte XX — Pesquisa de melhoria: qualidade máxima sem desperdício

A regra de otimização desta parte é:

> **minimizar custo/contexto por resultado externamente validado, sujeito a um piso explícito de qualidade e risco.**

Preço por token, tamanho do contexto, número de agentes ou benchmark isolado não são objetivos finais.

## 71. Melhorias por propósito/recurso

| Propósito atual | Melhoria recomendada | Ganho esperado | Gate de segurança/qualidade |
|---|---|---|---|
| DIRECT vs ORCHESTRATED | Calibrar o gate com corpus real de near-misses e custo histórico; incorporar `estimated_coordination_overhead` e `independence_score` | evitar harness e multi-agent overhead | incerteza continua favorecendo DIRECT; promoção tardia permanece disponível |
| Promoção tardia | Persistir handoff por delta: somente decisões/invariantes/resultados que não podem ser recuperados barato do repo | menos reread após promoção | nunca descartar requirement material nem validated outcome |
| Requests gigantes | Combinar working-set pressure + breadth + dependency density; fragments imutáveis e retrieval por pergunta material | evita gastar frontier context antes de haver plano durável | coverage review prova que todos fragments foram digeridos |
| Evidência do request | Não formar summary pyramid irreversível; manter source refs e retrieval sob demanda | reduz duplicação e risco de omissão | raw source permanece recuperável |
| Adaptive study | Adotar selective retrieval: busca/ranking primeiro, leitura só dos top hits; widening por evidência | menos tokens e menos distractors | questões materiais/risco alto podem ampliar scope |
| Rastreabilidade | Manter índices determinísticos request→requirement→TODO e validação de cobertura | melhora qualidade sem tokens extras | create/audit falham quando há buracos |
| TODO boundaries | Adicionar métricas de context affinity e independent validation boundary ao review | evita microtasks e monolitos | reviewer rejeita `extreme` e boundaries artificiais |
| Resumibilidade | Checkpoint no menor ponto semanticamente estável, não em cada tool call | menos state e retry waste | checkpoint deve ser suficiente para continuar sem transcript |
| Planning/implementation routing | Roteamento step-level, não request-level; usar workload class + validation strength + blast radius | frontier somente onde muda qualidade | nenhum route abaixo do deterministic floor |
| Hard decisions | Agrupar somente decisões fortemente acopladas; paralelizar decisões independentes read-only | reduz strong-model context | synthesis verifica contradições entre decisões |
| `design_route` | Medir break-even: só dividir se implementação posterior economizar mais do que o handoff adicional | evita dois workers desnecessários | design obrigatório quando high-blast-radius + implementation volume justificarem |
| Capability routing | Introduzir `advanced` e comparar candidate routes por expected validated cost | usa GLM/Muse/value models antes de premium quando seguro | task-class eval + availability + capability filter |
| Failure escalation | Complementar failure class com evidence confidence e failure signature; não escalar quando o novo retry não muda hipótese | menos retries caros | semantic/plan_defect continuam protegidos |
| Availability fallback | Cooldown/adaptive provider chain considerando quota observada e cache affinity | menos loops e cache loss | mesma capability floor durante failover |
| Delegação barata | Usar um `delegation_gate` determinístico que estime overhead, context pollution, parallelism e route delta | evita 15× token explosion de multi-agent em tarefas inadequadas | delegation somente quando expected benefit > coordination cost |
| Multi-provider | Descobrir somente providers instalados/autenticados/configurados; snapshot omite ausentes | zero planejamento fictício | provider opcional ausente nunca bloqueia plano |
| Progressive disclosure | Aplicar ainda mais aggressively: control plane curto, provider refs e model catalog lazy | reduz always-loaded tokens | CI impõe budgets de chars/tokens e links válidos |
| Context reuse/isolation | Introduzir explicit `context_affinity` em planning review e scheduler | preserva cache/raciocínio onde vale | fresh worker apenas com motivo registrado |
| Shared context | Deduplicação semântica + source references; preferir path/symbol ao prose | menos repeated tokens | itens ainda precisam ser suficientes para executar |
| Validated learnings | Adicionar `rediscovery_cost` e `staleness_scope`; não criar learning barato de redescobrir | menos artefatos/contexto futuro | somente após deterministic validation |
| Shared patterns | Usar invalidation graph incremental e digest de contract revision | evita revalidar todo plano | signatories stale obrigatoriamente reabertos |
| Validação externa | Preferir testes/linters/checkers sobre self-judgment; criar weakest-link review para silent failure | melhora qualidade | nenhum worker pode auto-completar sem gate externo |
| Service map | Incremental discovery por fingerprints + changed paths; mapear readiness além de PID | evita rediscovery e falsos positives | stale map bloqueia execução não monitorada |
| Stall detection | Manter 300s como default, mas exigir no-progress composto: output + CPU/process + dependency health; suportar quiet-phase override | menos falsa escalada e melhor deadlock diagnosis | elapsed time sozinho nunca prova failure |
| Log cursor | Cursor por inode/file identity + offset, bounded delta e rotation detection; adicionar semantic fingerprint opcional | evita reread e prompt pollution | raw log permanece intacto |
| Failure evidence | Gerar `FailureEvidencePacket` estruturado antes de qualquer modelo: invariant/check, first failing step, latest delta, resource health, process metrics, paths | melhor diagnóstico com menos tokens | packet é evidence, não authority |
| Assistant triage | Aplicar modelo PROBE/AgentRx: deterministic constraints/checks → structured diagnosis → bounded guidance | maior recoverability com prompt menor | guidance não muda state/commands/tests sem owner verificar |
| Worker budgets | Budgets adaptativos por route/workload e checkpoint density | limita worst-case spend | budget exhaustion é resumível e não semantic failure |
| Prompt cache | Monitorar cache hit como SLO; static prefix primeiro, dynamic suffix último; tool schemas estáveis; cache-safe forks | grande redução de custo/latency | não adicionar texto inútil só para atingir cache threshold |
| Summaries | Summary determinístico quando possível; model only para synthesis ambígua | elimina última chamada desnecessária | final handoff precisa cobrir riscos/follow-ups/validation |
| Cleanup | Garbage collection por ownership/sentinel e retention policies separadas para shared telemetry | evita lixo sem risco de apagar produto | refuse unsafe/symlink paths |
| Monitor artifact cleanup | Tirar todo runtime log/report/cursor da pasta da skill; registrar owner/scope/retention e apagar artefatos task-scoped assim que a task termina e eles deixam de ser necessários | evita lixo acumulado, leitura acidental de logs antigos e crescimento permanente da instalação | não apagar evidência ainda referenciada por retry/diagnosis/handoff; shared project state só por política explícita |
| Regression/evals | Avaliar quality non-inferiority + cost per validated TODO + cache + retries + latency + under-routing | otimização guiada por dado real | shadow/A-B antes de auto-routing |
| Deterministic control plane | Expandir scripts para policy/routing/evidence compaction em vez de prompt instructions | menos token e menos nondeterminism | logic versionada e coberta por tests |
| Security/provenance | Provider profile separado de harness; secrets só por env name; telemetry sem prompt/code | mais providers sem aumentar risco | fail closed quando read-only/sandbox não puder ser provado |

## 72. Evidência externa que sustenta as melhorias

- **Multi-agent só quando compensa:** a Anthropic relata que seus agentes usam ~4× tokens de chat e multi-agent ~15×; o padrão paga melhor em pesquisa paralelizável, contexto que excede um único agente e muitos tools, enquanto coding costuma ter menos paralelismo independente: https://www.anthropic.com/engineering/multi-agent-research-system
- **Contexto é recurso finito:** a Anthropic recomenda subagents focados e handoffs condensados, preservando o lead context para synthesis: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- **Long context não substitui retrieval:** `Lost in the Middle` mostra queda de qualidade com informação relevante perdida em contextos longos; mais documentos podem aumentar custo sem melhorar resposta: https://aclanthology.org/2024.tacl-1.9/
- **Selective retrieval funciona em código:** Repoformer reporta ganhos de eficiência evitando retrieval quando ele não ajuda, com até 70% de speedup em seus experimentos sem perda de performance: https://arxiv.org/abs/2403.10059
- **Routing step-level:** AgentRouter reporta 72% de redução de custo mantendo 97,3% da qualidade frontier-only em seu benchmark de workflows multi-step; é evidência para route each semantic leaf, não uma garantia para este projeto: https://arxiv.org/abs/2609.22951
- **Cascades cheap-first:** FrugalGPT e RouteLLM mostram que encaminhar casos simples para modelos econômicos e escalar os difíceis pode preservar qualidade com custo muito menor: https://arxiv.org/abs/2305.05176 e https://arxiv.org/abs/2406.18665
- **Cache deve ser métrica operacional:** Claude Code trata cache hit como SLO; trocar model/tools no meio quebra cache e pode custar mais, enquanto subagents/handoffs preservam a sessão principal: https://claude.com/blog/lessons-from-building-claude-code-prompt-caching-is-everything
- **GPT-6 caching:** OpenAI documenta descontos de cached input de até 95%, prefix matching, cache diagnostics e cache-safe prompt design: https://developers.openai.com/api/docs/guides/prompt-caching
- **Cost per task, não preço por token:** a orientação Anthropic para Claude 5.5 recomenda evals do workload, effort calibration, caching e orchestration, inclusive Opus planning + Sonnet execution: https://www.anthropic.com/webinars/building-with-the-claude-5-5-family-choosing-the-right-model-and-getting-more-from-every-token
- **Failure diagnosis estruturado:** AgentRx transforma trajectory em invariants/checker/evidence log antes do judge; Microsoft reporta ganhos de localização/attribution sobre prompting baseline: https://www.microsoft.com/en-us/research/blog/systematic-debugging-for-ai-agents-introducing-the-agentrx-framework/
- **Recovery bounded:** PROBE separa telemetry, diagnosis e guidance gate; em 257 casos inicialmente não resolvidos reporta 65,37% Top-1 diagnosis e 21,79% recovery, defendendo side-channel recovery sem mudar policy/tool budget: https://www.microsoft.com/en-us/research/publication/debugging-the-debuggers-failure-anchored-structured-recovery-for-software-engineering-agents/
- **Failure attribution ainda é difícil:** Who&When Pro contém 12.326 trajectories com labels controlados e mostra que error-mode/root-cause attribution permanece fraco; logo diagnósticos de IA devem ser advisory e verificados: https://arxiv.org/abs/2607.09996

---

# Parte XXI — Delegação multi-IA / multi-agente v2

## 73. Objetivo

Evoluir delegação para aproveitar competência específica e preço de cada agente **sem criar um sistema multiagente que consome mais tokens do que o trabalho**.

A decisão de delegar passa a ser explícita:

```text
leaf
  ↓
can deterministic tool solve it?
  ├─ yes → tool
  └─ no
      ↓
would fresh/cheaper/specialist worker materially help?
      ├─ no → keep current useful context
      └─ yes
          ↓
eligible installed providers
          ↓
cheapest route satisfying quality floor
          ↓
bounded worker → compact result → independent validation
```

## 74. DelegationDecision

Adicionar um contrato determinístico de decisão com pelo menos:

- `work_kind`: exploration | design | implementation | debugging | review | diagnostics | validation_support | summary;
- `semantic_difficulty`;
- `validation_strength`;
- `blast_radius`;
- `silent_failure_cost`;
- `parallelizable`;
- `context_affinity`;
- `estimated_context_pollution`;
- `required_capabilities`;
- `required_tools`;
- `write_scope`;
- `expected_output_size`;
- `cache_affinity`;
- `provider_availability`;
- `coordination_overhead_class`.

A policy decide `tool | keep_root | delegate` e, somente no último caso, resolve provider/tier/effort.

Não usar um LLM exclusivamente para calcular esse gate inicialmente. Os sinais já existem no planning/routing e podem ser combinados deterministicamente.

## 75. Roles de delegação

### Explorer
- read-only;
- economy/standard;
- busca/localização/multi-hop bounded;
- entrega evidence map: paths, symbols, tests/contracts, unresolved questions;
- não entrega narrativa longa.

### Design specialist
- strong/max somente quando hard decision/design realmente exigir;
- produz design bounded, contracts, ordered checkpoints e validation strategy;
- não implementa quando o objetivo é permitir executor mais barato.

### Implementer
- menor route que satisfaz floor;
- write-enabled somente no scope da task;
- report estruturado e pequeno.

### Reviewer
- fresh context quando independência ajuda;
- tier igual ao hardest material risk, não automaticamente max;
- recebe requirements/acceptance/change summary e recupera evidência sob demanda.

### Diagnostic specialist
- não recebe repo inteiro;
- recebe `FailureEvidencePacket`;
- pode ser Antigravity/GLM/Muse/outro provider barato somente se profile/sandbox adequado estiver disponível;
- advisory por padrão, sem authority.

### Summarizer
- preferir deterministic summary;
- model economy apenas quando synthesis humana/semântica for necessária.

## 76. Preference por modelos de alto valor

O selector deve preferir modelos de melhor **expected validated cost** dentro do floor. Em especial, F3/`advanced` existe para capturar casos em que GLM/Muse ou outro value model evita o salto direto de Sonnet/standard para Opus/Fable/Astra/strong.

Contudo:

- `advanced` não é obrigatório em todos os environments;
- provider deve estar instalado/configurado/autenticado;
- model/harness deve suportar a tarefa;
- benchmark/telemetry da task class deve atingir quality floor;
- ausência remove o candidato completamente;
- nenhuma task deve dizer “usar GLM” ou “usar Muse” apenas porque o catálogo global conhece esses nomes.

## 77. Regras contra explosão multiagente

- default máximo de dois explorers concorrentes permanece;
- não criar subagent para um lookup deterministicamente barato;
- não delegar sequential steps com alta `context_affinity`;
- não permitir recursive delegation irrestrita; default depth 1, exceção explícita e budgeted;
- fan-out write-heavy somente com worktree/isolation comprovado;
- cada worker recebe output budget;
- parent recebe compact result, nunca transcript;
- sibling workers compartilham stable prefix quando o provider/harness possibilitar;
- cancelar fan-out restante quando acceptance evidence já tornou o resultado suficiente;
- medir tokens de root + todos subagents + retries, não apenas worker “vencedor”.

## 78. GLM/Muse no tier `advanced`

A classificação inicial deve ser conservadora e data-driven.

### Muse Spark 1.3

Meta descreve Spark 1.3 como voltado a long-horizon coding/agentic work e menos turnos/tokens desnecessários. Evidência independente recente mostra desempenho próximo a Sonnet 5.5 em vários testes, variando bastante por workload. Portanto:

- candidato preferencial F3 para coding/agentic workloads onde eval local confirma non-inferiority;
- não substituir Sonnet/Opus globalmente;
- model effort e harness fazem parte da identidade da rota;
- se Muse Code não estiver instalado/ready, não aparece no plano.

Fontes:
- https://ai.meta.com/tools/muse/
- https://artificialanalysis.ai/models/comparisons/claude-sonnet-5-5-high-vs-muse-spark-1-3

### GLM-5.3 / GLM-5.3-Flash

Z.AI reporta forte eficiência de output tokens e coding/agentic performance, além de Coding Plan com cache/credits. Portanto:

- GLM-5.3-Flash pode concorrer em F2/F3 dependendo do workload;
- GLM-5.3 pode concorrer em F3/F4 quando seu eval local justificar;
- não inferir qualidade pelo nome Flash;
- em subscription, otimizar credits/quota e não USD fictício;
- provider ausente não entra na matrix.

Fontes:
- https://z.ai/blog/glm-5.3
- https://z.ai/blog/glm-5.3-flash
- https://docs.z.ai/devpack/overview

## 79. FailureEvidencePacket e diagnóstico progressivo

Antes de qualquer assistant/model diagnosis, produzir deterministicamente:

```json
{
  "validation_id": "...",
  "command_id": "...",
  "failure_signature": "...",
  "first_failure_excerpt": "...",
  "latest_delta_excerpt": "...",
  "process": {"alive": true, "cpu_delta": 0.0, "children": 3},
  "resources": [{"id":"tomcat","status":"healthy"}],
  "progress": {"last_output_age_seconds": 420, "cpu_idle_seconds": 380},
  "invariant_violations": [],
  "evidence_paths": ["..."],
  "prior_attempt_classes": ["..."]
}
```

O packet deve referenciar paths para artefatos grandes, não embuti-los.

Pipeline:

```text
raw validation/log/resource evidence
      ↓
deterministic compaction + known checks/invariants
      ↓
FailureEvidencePacket
      ↓
optional cheap diagnostic specialist
      ↓
bounded hypothesis / next investigation
      ↓
implementation owner verifies
      ↓
deterministic validation
```

Isso incorpora a principal ideia de AgentRx/PROBE sem transformar a skill em um autonomous self-repair loop.

## 80. Stall monitoring v2

Preservar 300 segundos como **default de no-progress**, mas não como regra “cinco minutos = erro”.

Confirmar stall somente quando os sinais configurados justificarem, por exemplo:

- nenhum output/progress semanticamente novo;
- CPU/process-group sem atividade útil;
- dependências mapeadas permanecem healthy;
- processo continua vivo;
- validation não declarou quiet phase legítima.

Permitir por validation:

- `no_progress_timeout_seconds`;
- `expected_quiet_seconds`;
- `progress_regex`/progress extractor determinístico quando o framework fornece markers;
- health checks específicos.

Se resource falhou, classificar environmental. Se processo está trabalhando legitimamente, continuar. Se stall real for confirmado, persistir process snapshot + FailureEvidencePacket antes de parar o grupo.

## 81. Cache-aware delegation

Cache passa a influenciar a decisão **antes** de criar worker.

- root com contexto útil e cache quente pode ser mais barato que subagent cheap;
- mudança de model/effort no root é proibida automaticamente;
- side work que exige modelo diferente deve ir para fresh worker;
- static worker prefix deve ser byte-stable;
- dynamic task/context entra no suffix;
- cache hit/miss/read/write tokens entram em telemetry quando expostos;
- cache hit rate vira métrica do harness, não curiosidade de billing;
- provider switch considera custo de reconstrução de contexto.

Anthropic documenta que em contexto grande até trocar Opus→Haiku pode sair mais caro que manter Opus devido ao cache miss; OpenAI documenta descontos de cached input de até 95%. Fontes:
- https://claude.com/blog/lessons-from-building-claude-code-prompt-caching-is-everything
- https://developers.openai.com/api/docs/guides/prompt-caching

## 82. Quality/economy scorecard

Toda evolução de routing/delegation deve medir, por workload class:

- validated completion rate;
- regression/negative-case pass rate;
- under-routing rate;
- over-routing rate;
- attempts até sucesso;
- root input/output tokens;
- subagent input/output tokens;
- cached input/cache writes quando disponível;
- credits/quota consumed;
- USD marginal quando aplicável;
- wall-clock e p95;
- context bytes/tokens entregues ao worker;
- number of model calls;
- number of delegated workers;
- failure recovery rate;
- cache hit rate;
- cost per validated TODO;
- quality-adjusted cost.

A decisão de ativar uma otimização precisa de **quality non-inferiority predeclared** e ganho econômico material. Não escolher política olhando apenas o melhor resultado pós-hoc.

---

# Parte XXII — Plano de implementação recomendado


Este plano já incorpora as otimizações de qualidade/contexto descritas acima. Ele evita um único TODO monolítico e separa mudanças por fronteiras em que histórico/contexto realmente se reutilizam.

## 67. Princípios de decomposição do plano

Antes de qualquer TODO de implementação, executar o **TODO-000 Documentation baseline & reconciliation** abaixo. Essa etapa é uma revisão única da documentação interna no início do plano, não uma regra para reler tudo em cada resume/TODO.

- Não criar um TODO por arquivo.
- Agrupar arquivos quando implementam o mesmo contrato/invariante.
- Separar adapters de providers diferentes quando seus protocolos/testes não compartilham contexto suficiente.
- Concluir primeiro os contratos que os TODOs posteriores consumirão.
- Não fazer provider integration antes de existir profile schema estável.
- Não habilitar auto-routing novo antes de telemetry + shadow eval.
- Manter compatibilidade da `main` como gate em todas as etapas.

---

## TODO-000 — Documentation baseline & requirements reconciliation

**Objetivo:** começar a implementação com entendimento completo e atual da documentação existente, incorporando ao plano qualquer informação pertinente que este documento tenha omitido ou que tenha mudado desde sua redação.

**Escopo obrigatório:**

- inventariar deterministicamente toda documentação interna relevante: `README*.md`, `docs/**/*.md`, `skill/plan-and-execute/SKILL.md`, `skill/plan-and-execute/references/**/*`, schemas/examples e documentação de manutenção;
- registrar path + hash/digest para provar coverage;
- ler **todos** os documentos internos relevantes, mas em batches/contextos bounded — nunca concatenar o corpus inteiro em um único prompt;
- extrair somente contratos, invariantes, comportamento atual, limitações, compatibilidade, TODO-impact e contradições que possam mudar esta implementação;
- reconciliar documentação com o código/estado atual quando houver conflito; documento não deve vencer comportamento comprovado silenciosamente;
- revisar documentação oficial externa de providers/modelos **somente** para fatos voláteis/materialmente necessários e facets stale; não “ler a internet inteira”;
- produzir um artefato compacto de baseline com: coverage, findings materiais, stale/conflicting docs, decisions requeridas e mudanças necessárias neste documento/plano;
- quando houver informação material ausente, atualizar este documento/plan spec antes de iniciar TODO-001;
- persistir hashes para que resumes posteriores revisem somente documentação alterada.

**Estratégia econômica:**

1. tool determinístico cria inventory/hash;
2. workers economy/standard leem batches independentes e retornam apenas findings com source refs;
3. um synthesis/reviewer strong é usado somente se houver contradições cross-document, security/architecture ou decisões de alto impacto;
4. o produto é um índice compacto, não summaries longos de cada arquivo.

**Validação:**

- coverage = 100% do corpus documental classificado como relevante;
- todo path relevante possui status `reviewed|not_applicable` com justificativa curta;
- nenhum documento é copiado integralmente para o baseline;
- findings materiais citam path/section;
- alterações de requisitos são explicitamente diffadas antes de implementação;
- rerun com os mesmos hashes não requer releitura dos documentos.

**Rota:** deterministic inventory + `economy/standard` batch review; `strong/medium` apenas para synthesis material.

---

## TODO-001 — Contrato de catálogo e aliases portáveis

**Objetivo:** criar os contratos centrais sem mudar ainda o comportamento de execução.

**Escopo principal:**

- novo `model_catalog.py`;
- schema de catalog/provider/model/economics/capabilities/evidence;
- F1–F5/L1–L5 como aliases do vocabulário canônico;
- catalog version/digest/freshness;
- validação estrita.

**Não inclui:** CLI de refresh, profiles concretos, mudança no runner.

**Arquivos esperados:**

```text
scripts/model_catalog.py
scripts/model_catalog_self_test.py
scripts/routingctl.py
references/MODEL_CATALOG.md
```

**Dependências:** nenhuma.

**Validação:**

- round-trip schema;
- aliases normalizados;
- invalid capability/economics/source rejeitados;
- deterministic digest;
- current routing tests permanecem verdes.

**Rota mínima sugerida:** `strong/medium` — contrato cross-cutting, mas fortemente testável.

---

## TODO-002 — Shared catalog cache e refresh controller

**Objetivo:** implementar refresh provider-scoped, locking e snapshot sem consumir modelos.

**Escopo:**

- `model_catalogctl.py`;
- cache global/provider-scoped;
- atomic write;
- status/show/refresh/validate;
- `status/diff/refresh --plan` para refresh proativo de planos longos;
- aviso non-blocking de snapshot stale em status/resume;
- audit trail de snapshot digest/provenance;
- source/facet freshness;
- version/CLI-change invalidation;
- stale-but-valid grace behavior.

**Dependências:** TODO-001.

**Validação:**

- concorrência/lock;
- escrita interrompida não corrompe catálogo;
- provider A refresh não toca provider B;
- fresh catalog causa zero external refresh;
- expired facet atualiza somente o necessário.

**Rota:** `standard/medium` para implementação + `strong/medium` para review de atomicidade/freshness se necessário.

---

## TODO-003 — Provider Profile / Harness abstraction

**Objetivo:** desacoplar provider comercial/model backend do harness de execução.

**Escopo:**

- provider profile schema;
- `harness: claude|codex|native`;
- env mapping seguro;
- adapter composition em `run_isolated.py`;
- preservar adapters atuais sem regressão.

**Arquivos:**

```text
scripts/routing_config.py
scripts/run_isolated.py
scripts/provider_self_test.py
```

**Dependências:** TODO-001.

**Riscos:** auth/env leakage e regressão de command building.

**Validação:**

- todos providers atuais geram exatamente o comando esperado;
- secrets nunca aparecem em config/show/report;
- profile e harness podem variar independentemente;
- current Claude/Codex behavior permanece igual.

**Rota:** `strong/high` — alteração central em dispatch e security boundary.

---

## TODO-004 — Muse Code provider nativo

**Objetivo:** reincorporar a parte útil da PR #17 em cima da nova abstração.

**Escopo:**

- `muse exec --json`;
- worker write behavior;
- read-only summary;
- model/effort mapping via catalog;
- JSON/JSONL envelope;
- doctor/config support.

**Dependências:** TODO-002 e TODO-003.

**Validação:** provider self-tests + CLI tests + mocked envelopes.
**Rota:** `standard/medium` — adapter delimitado e objetivamente testável.

---

## TODO-005 — GLM/Z.AI provider profile

**Objetivo:** adicionar `glm` sem duplicar o Claude/Codex runner.

**Escopo:**

- Anthropic/OpenAI protocol profile;
- GLM-5.3 e GLM-5.3-Flash discovery/bootstrap;
- effort aliases low/high/max;
- API pricing;
- Coding Plan credit formula;
- off-peak accounting;
- catalog capabilities.

**Dependências:** TODO-002 e TODO-003.

**Validação:**

- profile command/env sem secret;
- credits calculados contra exemplos oficiais;
- cached input multiplier correto;
- effort mapping válido;
- unsupported thinking-disabled config rejeitada para GLM-5.3.

**Rota:** `standard/medium`, com review forte da parte econômica.

---

## TODO-006 — DeepSeek provider profiles

**Objetivo:** adicionar `deepseek` com Claude e Codex/Responses harnesses.

**Escopo:**

- `deepseek-flash` e `deepseek-v4-pro` como catálogo atual, não ranking rígido;
- Anthropic profile;
- Responses/Codex profile;
- capability difference (vision etc.);
- effort mapping;
- peak/off-peak e cache-hit pricing;
- invalid-model refresh.

**Dependências:** TODO-002 e TODO-003.

**Validação:**

- candidate eligibility por capability;
- peak/off-peak boundary tests;
- cache-hit economics;
- Claude/Codex harness command isolation;
- profile override não contamina provider nativo.

**Rota:** `standard/medium`, com strong review para dual-harness behavior.

---

## TODO-007 — Plan-local MODEL_MATRIX snapshot

**Objetivo:** incorporar o snapshot/auditoria da PR #17 sem colocar pesquisa no planning context.

**Escopo:**

- `MODEL_MATRIX.json` compacto;
- `MODEL_MATRIX.md` human-readable;
- snapshot do catálogo por plan;
- catalog digest/version;
- refresh sem reescrever TODOs;
- F/L display aliases;
- provenance.

**Dependências:** TODO-001 e TODO-002.

**Validação:**

- provider switch preserva manifest task semantics;
- refresh altera snapshot, não TODO;
- worker prompt não contém `MODEL_MATRIX.md`;
- old plans sem snapshot continuam válidos.

**Rota:** `strong/medium` — envolve persistência e compatibilidade de plano.

---

## TODO-008 — Capability + economics candidate selector

**Objetivo:** escolher o candidato econômico apenas dentro do conjunto seguro.

**Pipeline:**

```text
minimum_route(signals)
→ capability filter
→ availability filter
→ quality constraint
→ cache/quota-aware effective cost
→ deterministic tie-break
```

**Dependências:** TODO-001, TODO-002, TODO-003, TODO-007.

**Requisitos críticos:**

- nunca abaixo do floor;
- não usa LLM/router;
- cache-aware;
- subscription-aware;
- deterministic;
- route explanation estruturada.

**Validação:** corpus de fixtures com expected minimum route + candidate eligibility.

**Rota:** `strong/high` — algoritmo central que pode causar under-routing silencioso.

---

## TODO-009 — Execution telemetry e expected validated cost

**Objetivo:** medir o que importa sem aumentar contexto de worker.

**Escopo:**

- per-attempt operational metrics;
- cache tokens;
- credits/USD quando observável;
- latency;
- validation outcome;
- task signal class;
- privacy/minimal metadata;
- aggregation para eval.

**Dependências:** TODO-008.

**Validação:**

- no prompt/code in telemetry;
- deterministic rollup;
- absent usage fields não quebram execução;
- report size bounded.

**Rota:** `standard/medium`.

---

## TODO-010 — CLI/configure/doctor integration

**Objetivo:** tornar as opções utilizáveis sem expor complexidade interna.

**Escopo:**

```text
pae configure
pae doctor
pae models status
pae models show
pae models refresh
pae resume --provider muse|glm|deepseek
```

**Dependências:** TODO-004/005/006/007.

**Validação:** CLI tests Linux/Windows, JSON output stable, credential redaction.

**Rota:** `standard/medium`.

---

## TODO-011 — Documentação progressiva e planning integration

**Objetivo:** integrar arquitetura nova sem aumentar always-loaded context.

**Escopo:**

- `SKILL.md` mínimo;
- `MODEL_ROUTING.md` genérico;
- `MODEL_CATALOG.md` on-demand;
- Muse/GLM/DeepSeek refs lazy;
- `ORCHESTRATION.md` snapshot flow;
- `PLANNING_PROTOCOL.md` floors + snapshot;
- `PLAN_SPEC.md` aliases/canonical format;
- `TOKEN_EFFICIENCY.md` cache-aware routing.

**Dependências:** contratos anteriores estabilizados.

**Validação:** char/token budgets e validator required-text sem duplicação excessiva.

**Rota:** `standard/medium` com deterministic validation forte.

---

## TODO-012 — Shadow routing benchmark

**Objetivo:** provar a policy antes de alterar comportamento real.

**Escopo:**

- corpus versionado;
- main route vs candidate route;
- under/over-routing;
- cost model;
- cache impact;
- GLM/DeepSeek/Muse fixtures;
- no execution switch ainda.

**Dependências:** TODO-008, TODO-009, TODO-011.

**Validação:** eval report reproduzível.

**Rota:** `strong/medium` — análise quantitativa, determinística e reproduzível.

---

## TODO-013 — Auto-routing conservador e rollout gates

**Objetivo:** habilitar nova seleção somente nos segmentos demonstrados seguros.

**Dependências:** TODO-012 aprovado.

**Gate:**

- no material validated-success regression;
- under-routing dentro do limite definido pelo corpus;
- economia material de tokens/credits ou tentativas;
- fallback seguro;
- CI completa verde.

Começar em tarefas com:

```text
strong deterministic validation
+ low/medium blast radius
```

Expandir somente por evidência.

**Rota:** `strong/high` — mudança final de comportamento produtivo.

---


## TODO-014 — Delegation policy v2 e role contracts

**Objetivo:** transformar delegação em uma decisão econômica/qualitativa explícita, sem fan-out cerimonial.

**Escopo:**

- `DelegationDecision`;
- `tool|keep_root|delegate`;
- roles explorer/design/implementer/reviewer/diagnostic/summarizer;
- context-affinity e coordination-overhead signals;
- max fan-out/nesting/budgets;
- installed-provider eligibility;
- compact result contracts.

**Dependências:** TODO-001, TODO-003 e TODO-008.

**Validação:**

- grep/lookup simples não cria worker;
- high-affinity sequential task permanece no contexto útil;
- independent read-only discovery pode fan-out bounded;
- absent GLM/Muse nunca aparece na decisão;
- strong floor não pode ser reduzido pelo delegation optimizer;
- token accounting inclui todos os workers.

**Rota:** `strong/high` — policy cross-cutting com risco de desperdício/under-routing.

---

## TODO-015 — Structured failure evidence e diagnostic recovery

**Objetivo:** melhorar debug pós-falha com mais qualidade e menos log em prompt.

**Escopo:**

- `FailureEvidencePacket`;
- invariant/check violations determinísticos;
- first failure + latest delta;
- process/resource snapshot;
- progress-aware stall;
- bounded diagnostic specialist input/output;
- advisory-only authority.

**Dependências:** service-map/resource-watch atuais + TODO-014 para diagnostic role.

**Validação:**

- raw log grande nunca é copiado integralmente;
- repeated old log lines não reaparecem;
- resource outage fica environmental;
- elapsed time sozinho não confirma stall;
- assistant unavailable não altera baseline;
- guidance nunca executa comando nem completa task;
- resource/log watcher artifacts são criados fora da pasta da skill;
- ao concluir a task, artefatos task-scoped sem referência viva são removidos;
- artefatos necessários para retry/diagnosis permanecem enquanto a task estiver pending/blocked e são removidos no momento seguro posterior;
- project-shared state deliberado, como `.ai-work/SERVICE_MAP.md`, não é apagado pelo cleanup da task.

**Rota:** `strong/medium` para contrato + implementation standard onde determinístico.

---

## TODO-016 — Oversized-request/context retrieval refinements

**Objetivo:** reduzir custo do primary planning sem perder coverage.

**Escopo:**

- working-set/breadth/dependency signals;
- immutable fragments;
- digest batches por context cohesion;
- material-question retrieval;
- contradiction/dependency index;
- coverage gate;
- no summary pyramid irreversível.

**Dependências:** nenhuma de provider routing; pode ser desenvolvida em paralelo depois de contratos estáveis.

**Validação:**

- corpus de requests pequenos não entra em PRIMARY_PLAN;
- request gigante repetitivo não força frontier por tamanho;
- todos fragments recebem coverage;
- final planner não carrega package inteiro;
- source evidence continua recuperável.

**Rota:** `strong/medium` design; implementação fortemente determinística pode usar `standard/medium`.

---

## TODO-017 — Whole-skill quality/economy benchmark

**Objetivo:** medir se routing, `advanced`, delegation, diagnostics e context refinements realmente melhoram o produto.

**Escopo:**

- fixed workload corpus;
- DIRECT e ORCHESTRATED cases;
- large-request cases;
- debugging/stall/resource failures;
- provider availability cases;
- standard vs advanced vs strong;
- root-only vs delegated;
- cache warm/cold scenarios;
- matched-run methodology;
- non-inferiority gate.

**Dependências:** TODO-009, TODO-012, TODO-014, TODO-015 e TODO-016.

**Métricas:** conforme §82.

**Gate:** nenhuma policy passa a default se reduzir validated completion acima da margem predefinida, mesmo que economize tokens.

**Rota:** `strong/medium` para desenho experimental + ferramentas determinísticas para agregação.

---

## 68. Ordem de execução e paralelismo

```text
TODO-000 documentation baseline
 └─ TODO-001
     ├─ TODO-002
     └─ TODO-003
      ├─ TODO-004 Muse
      ├─ TODO-005 GLM
      └─ TODO-006 DeepSeek

TODO-001 + TODO-002
 └─ TODO-007 plan snapshot

TODO-003 + TODO-007
 └─ TODO-008 routing selector
      └─ TODO-009 telemetry

TODO-004/005/006/007
 └─ TODO-010 CLI/config

contracts stabilized
 └─ TODO-011 docs

TODO-008 + 009 + 011
 └─ TODO-012 shadow eval
      └─ TODO-013 rollout

TODO-001 + TODO-003 + TODO-008
 └─ TODO-014 delegation policy
      └─ TODO-015 structured diagnostics

PRIMARY planning path
 └─ TODO-016 oversized-request refinements

TODO-009 + TODO-012 + TODO-014 + TODO-015 + TODO-016
 └─ TODO-017 whole-skill quality/economy benchmark
```

TODO-004, TODO-005 e TODO-006 são bons candidatos a contextos/workers isolados e até execução paralela depois de TODO-003, pois os aprendizados específicos de Muse, GLM e DeepSeek têm pouco reaproveitamento entre si além do provider-profile contract já estabilizado.

TODO-008 não deve começar antes de TODO-007: escolher modelos dinamicamente sem um snapshot auditável tornaria debug/reprodução muito mais difícil.

---

## 69. Otimização de execução do próprio plano

Para economizar tokens ao implementar este plano:

- usar tools/grep/test diretamente para discovery mecânico;
- não carregar todos os provider docs em TODO-003;
- carregar somente o provider ref do TODO-004/005/006;
- manter shared context global limitado ao provider-profile/catalog contract;
- não compartilhar pricing/benchmark prose entre TODOs: compartilhar schema/IDs;
- usar workers frescos para GLM/DeepSeek/Muse;
- usar mesma rota/contexto para TODO-008 + partes de TODO-009 somente se implementação estiver altamente acoplada;
- validar cada provider adapter deterministicamente antes de integrar CLI;
- guardar eval datasets fora de prompts e passar paths/summary;
- usar um modelo forte em contratos/core routing, não em docs/CLI mecânicos;
- não fazer fresh web research dentro de cada TODO: usar este documento + refresh targeted apenas quando uma informação atual realmente for necessária;
- executar o whole-documentation baseline uma vez no início; em resumes posteriores usar hashes e revisar somente docs alterados;
- em planos de longa duração, usar `models status/diff` antes de decidir por refresh; refresh explícito do usuário atualiza o snapshot sem reconstruir o plano;
- uma nova geração de modelos deve mudar concrete route resolution, não apagar semantic difficulty/floors já validados.

- considerar `advanced` somente quando o environment tiver candidate elegível; não carregar documentação de GLM/Muse se eles não estiverem disponíveis;
- manter `DelegationDecision` fora do worker prompt; worker recebe apenas a rota resolvida e sua tarefa;
- medir coordination overhead antes de ampliar fan-out;
- executar diagnostics sobre `FailureEvidencePacket`, não raw logs;
- preservar cache-safe static prefixes e registrar cache misses relevantes;
- para requests enormes, recuperar fragments por questão material em vez de concatenar o package;
- tratar TODO-017 como gate de produto: preço menor sem quality non-inferiority não é sucesso.


---

## 70. Critério final de sucesso do plano

O objetivo não é “ter mais providers”. O plano só atingiu seu propósito se, ao final, a skill conseguir demonstrar:

```text
mesma ou melhor qualidade validada
+
menos tokens/créditos por TODO concluído
+
menos dependência de catálogo/model IDs estáticos
+
nenhuma perda de resumabilidade
+
nenhum aumento material do contexto always-loaded
```

Esse resultado deve ser provado pelo shadow benchmark e pelas métricas de execuções reais, não inferido de preços ou benchmarks isolados.

Adicionalmente, o resultado final deve demonstrar:

- que o tier `advanced` reduz saltos prematuros para frontier premium sem aumentar under-routing;
- que environments sem GLM/Muse/providers opcionais mantêm comportamento correto;
- que delegação reduz custo/context pollution nos workloads onde é ativada e permanece desligada onde não compensa;
- que diagnosticar a partir de evidence packets melhora recovery sem aumentar authority do advisor;
- que oversized requests podem chegar a um plano final resumível sem obrigar um único modelo caro a reler o prompt completo;
- que cache hit rate e custo de todos os subagents entram no cálculo econômico.