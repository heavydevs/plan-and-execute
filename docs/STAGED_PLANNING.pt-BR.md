# Planejamento em três rotas, entradas grandes e padrões compartilhados

A skill separa **tamanho do pedido**, **dificuldade semântica** e **capacidade do modelo**. Um documento grande não deve ser enviado inteiro a um modelo frontier apenas porque contém muito texto; do mesmo modo, uma decisão pequena porém arquiteturalmente arriscada pode justificar um modelo forte.

## Três rotas

```text
pedido
  |
  +-- coeso / bounded --------------------------> DIRECT
  |
  +-- precisa de plano, entrada gerenciável ----> FINAL_PLAN
  |
  +-- precisa de plano, entrada grande demais --> PRIMARY_PLAN
                                                    |
                                                    v
                                              pacote preparado
                                                    |
                                                    v
                                                FINAL_PLAN
```

### 1. DIRECT

Para trabalho pequeno/médio coeso, a skill não cria `.ai-work`, checklist ou workers apenas por processo. O agente atual implementa e valida diretamente.

### 2. FINAL_PLAN

É o fluxo normal de orquestração. A skill estuda apenas o necessário, transforma o pedido em requisitos rastreáveis, cria TODOs bounded, escolhe `provider`/`model_tier`/`reasoning_effort` por TODO e executa cada leaf com validação determinística.

Esse caminho **não carrega** `PRIMARY_PLANNING.md`.

### 3. PRIMARY_PLAN

É usado quando ler/planejar a entrada inteira diretamente tornaria o planejamento caro, frágil a quota ou difícil de retomar antes de existir estado durável.

O roteamento padrão é econômico, não um limite de contexto do modelo:

- abaixo de aproximadamente 12k tokens estimados, sem forte breadth estrutural: FINAL_PLAN;
- a partir de aproximadamente 24k: PRIMARY_PLAN;
- entre esses valores: breadth estrutural pode selecionar PRIMARY_PLAN (por padrão, 30+ headings a partir de 8k tokens).

Os limites são configuráveis e devem ser recalibrados conforme custo/provider/projeto.

## O que o PRIMARY_PLAN faz

Primeiro, trabalho mecânico fica fora da IA:

1. mede a fonte;
2. extrai texto de forma determinística quando possível;
3. divide por headings e tamanho;
4. cria fragmentos imutáveis `F001`, `F002`, ...;
5. registra hashes, posição/heading e um `SOURCE_INDEX.json`.

Somente depois entram workers semânticos, em contextos bounded:

```text
fragmentos imutáveis
   |
   +--> digest D001 -- economy/medium
   +--> digest D002 -- economy/medium
   +--> digest D003 -- economy/medium
              |
              v
       síntese cross-fragment -- standard/medium
              |
              v
       revisão de cobertura -- strong/medium (fresh context)
              |
              v
       FINAL_PLAN_INPUT.md -- economy/low
```

Cada etapa fica no mesmo mecanismo persistente de checklist/subtasks do plano normal. Se a quota acabar, o próximo agente retoma do último checkpoint em disco em vez de reler o documento inteiro.

O pacote preparado mantém uma cadeia de proveniência:

```text
FINAL_PLAN_INPUT
  -> digest/pattern-seed ids
      -> fragment ids
          -> source anchors + SHA-256
```

Resumo nunca substitui a evidência primária; o planner final recupera um fragmento apenas quando uma decisão material precisa da redação original.

## Routing de modelo durante o planejamento

O modelo selecionado na conversa raiz não é automaticamente o modelo do planner.

| Trabalho | Rota lógica inicial |
|---|---|
| hashing, split, index, busca mecânica | ferramenta determinística |
| extração bounded / evidence map | `economy` |
| síntese normal de requisitos | `standard` |
| arquitetura, migração, segurança, integridade de dados, decisões pouco verificáveis | `strong` |
| review fresh | pelo menos capaz de desafiar a decisão material mais difícil |
| frontier/max | somente por necessidade/evidência |

As três escolhas são independentes:

```text
rota do PRIMARY_PLAN != rota do planner final != rota do TODO de implementação
```

## Padrões compartilhados versionados

`CONTEXT.md`, learning files e padrões não têm o mesmo papel:

- **execution context**: fatos/constraints relativamente imutáveis necessários a vários TODOs;
- **validated learning**: descoberta validada que flui de um TODO anterior para um TODO futuro;
- **shared pattern**: contrato normativo compartilhado que pode evoluir e invalidar consumidores já concluídos.

Exemplos de pattern:

- frontend `Resource` façade para HTTP;
- comportamento comum de CRUD/list/modal em telas Admin;
- convenções SCSS/design tokens;
- envelope de erro da API;
- regra de idempotência/persistência.

Um pattern tem id estável, revisão, digest, contrato, fontes e **signatários** (TODOs consumidores).

```text
PAT001 Resource façade r1
  +-- TODO 004 assinou r1
  +-- TODO 006 assinou r1
  +-- TODO 009 ainda pending
```

Quando evidência durante a implementação exige mudar o contrato:

```text
PAT001 r1 -> r2

TODO 004 completed + assinou r1 -> reabre
TODO 006 completed + assinou r1 -> reabre
TODO 009 pending                  -> continua pending e usará r2
TODO 012 não é signatário         -> não muda
```

Assim a skill aplica invalidação mínima por dependência, em vez de refazer todo o projeto.

Uma mudança local de implementação **não** deve alterar o pattern. A revisão só ocorre quando o contrato compartilhado realmente precisa mudar. Se a evidência altera requisitos, limites de TODO, dependências ou arquitetura além do pattern, isso vira invalidação do plano e exige replanejamento.

## Pattern seeds no PRIMARY_PLAN

Durante a preparação de uma especificação grande, digest workers podem encontrar cláusulas normativas repetidas. Eles registram candidatos em `PATTERN_SEEDS.json` sem decidir ainda os signatários.

O planner final, depois que os TODOs reais estabilizam, decide:

- quais seeds representam contratos compartilhados verdadeiros;
- quais viram patterns versionados;
- quais TODOs são signatários;
- quais seeds eram apenas contexto/duplicação e devem ser descartados.

Isso evita criar padrões artificiais cedo demais.

## Progressive disclosure

A economia de tokens depende de não carregar documentação irrelevante:

- `SKILL.md` contém apenas os gates e invariantes principais;
- `PRIMARY_PLANNING.md` só é lido no fluxo 3;
- `SHARED_PATTERNS.md` só é lido se houver um contrato cross-TODO realmente mutável;
- `PLANNING_INPUT_CONTRACT.md` é a interface pequena entre pacote preparado e FINAL_PLAN;
- workers recebem apenas seu task file + context/learnings/patterns atribuídos.

## Controladores

Avaliar/gerar o plano primário:

```bash
python <skill-dir>/scripts/preplanctl.py assess --file SPEC.md
python <skill-dir>/scripts/preplanctl.py prepare --repo-root . --file SPEC.md
```

Padrões compartilhados:

```bash
python <skill-dir>/scripts/patternctl.py init --plan .ai-work/<plan-id> --spec /tmp/pattern-spec.json
python <skill-dir>/scripts/patternctl.py assignment --plan .ai-work/<plan-id> --task 004
python <skill-dir>/scripts/patternctl.py adopt --plan .ai-work/<plan-id> --task 004
python <skill-dir>/scripts/patternctl.py update --plan .ai-work/<plan-id> --pattern PAT001 --contract-file /tmp/PAT001-v2.json --reason "evidência"
python <skill-dir>/scripts/patternctl.py validate --plan .ai-work/<plan-id>
```

## Base técnica

O desenho combina princípios de context engineering/progressive disclosure, persistência de artefatos entre contextos frescos, processamento determinístico fora do contexto do modelo, limitações práticas de uso de long context, planejamento de mudanças repository-scale e invalidação mínima por grafo de dependências. As referências e links de pesquisa ficam em `references/PRIMARY_PLANNING.md`, `references/PLANNING_ROUTING.md` e `references/SHARED_PATTERNS.md`.
