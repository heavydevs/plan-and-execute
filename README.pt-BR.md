# Plan and Execute

**Use um plano persistente com múltiplos workers somente quando esse custo realmente compensa.**

`plan-and-execute` é uma skill de orquestração seletiva para Claude Code e OpenAI Codex. Demandas pequenas/médias coesas permanecem no contexto atual do agente. Trabalho long-horizon entra no fluxo completo desde o início, ou pode ser promovido mais tarde se crescer durante a implementação — sem jogar fora o que já foi feito.

[English version](README.md)

## O que mudou na 0.9

A regra central da 0.8 continua a mesma:

```text
DIRECT por padrão -> ORCHESTRATE por evidência -> PROMOTE quando necessário
```

A 0.9 torna o roteamento de modelo baseado em evidência de ponta a ponta, em vez de baseado em tamanho ou contagem:

- **Escalada por evidência classificada, não por contagem de tentativas.** Uma falha registra `failure_class` (`mechanical`, `semantic`, `environmental`, `budget`, `plan_defect`, `unknown`); `mechanical`/`budget` repetem o degrau uma vez e depois sobem, `semantic` pula direto para o próximo tier mais forte, `environmental` mantém a rota, e `plan_defect` bloqueia o TODO para replanejamento em vez de queimar tentativas. Quando a evidência pede um degrau acima do mais forte no último provider disponível, o TODO é bloqueado (`ladder_exhausted`) em vez de repetido no tier máximo até `max_attempts`.
- **Um modelo raiz pequeno é um delegador, não um teto.** A skill nunca troca o modelo/effort da sessão raiz — isso invalida o cache de prompt do provider — então uma folha cujo piso excede o tier raiz é delegada a um worker fresco. `routingctl.py route --signals ...` e uma tabela de sinais no `SKILL.md` dão a um modelo raiz barato os mesmos pisos que um modelo raiz frontier usaria, protegidos por um corpus de regressão (`tier-evals.json`).
- **Folha em duas fases** (`design_route`): um TODO `high` pode ter um worker mais forte escrevendo uma nota de design bounded primeiro, e depois implementar na sua própria rota mais barata com essa nota.
- **Planejamento "decisões primeiro"** (`request_analysis.hard_decisions`): quando só algumas decisões do plano são difíceis, resolvê-las com workers fortes antes de um planner padrão escrever o plano mecânico.
- **Um único catálogo de modelos** (`routingctl.py`) alimenta todos os entrypoints; o effort é omitido para modelos que o rejeitam (Claude Haiku); orçamentos opcionais por worker (`claude.max_turns`, `claude.max_budget_usd`, `codex.rollout_token_budget`) transformam workers descontrolados em falhas `budget` retomáveis em vez de técnicas.
- **Um adapter para a Antigravity CLI do Google (`agy`)** se junta ao Claude Code e ao Codex como backend de execução; o adapter da Gemini CLI agora é marcado como legado (a própria CLI foi descontinuada).
- Documenta a mecânica concreta de elevação por host (`model`/`effort` de subagente, `isolation: worktree`, `opusplan`, papéis `spawn_agent` do Codex, fatos de cache de prompt) e corrige diversos bugs de despacho específicos do Windows (resolução de shims `.cmd`, o alias Python da Store, liveness do lease do runner).

Quando a orquestração realmente é necessária, **todo o comportamento robusto anterior continua existindo**:

- `TODO.md` persistente e conciso;
- um arquivo de definição por TODO;
- `manifest.json` como estado autoritativo;
- subtarefas/checkpoints retomáveis;
- rastreabilidade request-part -> requirement -> TODO;
- `provider`, `model_tier` e `reasoning_effort` recomendados individualmente por TODO, escalada por evidência e `design_route` opcional;
- validação determinística fora do auto-relato do worker;
- escalonamento/fallback entre provedores e modelos;
- estouro de créditos/quota preservando estado e sem contar como falha técnica;
- retomada por outra IA compatível sem o histórico do chat anterior;
- cleanup que remove planejamento/controle, mas preserva o produto implementado.

## Workers suportados

| Worker | Execução | Instalação padrão da skill | Ordem padrão |
|---|---:|---:|---:|
| Claude Code | Sim | Sim | 1º |
| OpenAI Codex | Sim | Sim | 2º |
| Antigravity CLI (`agy`) | Sim | Não | Opt-in |
| Gemini CLI | Legado | Não | Opt-in (descontinuada em 18/06/2026; use o adapter Antigravity) |
| Qwen Code | Sim | Não | Opt-in |
| Kimi Code CLI | Sim | Não | Opt-in |
| Trae Agent | Sim | Não | Opt-in |

Claude e Codex continuam sendo os únicos destinos de instalação padrão. Os demais são backends opcionais de execução dentro de um plano.

## Início rápido

Requisitos:

- Node.js 18.17+;
- Python 3.10+;
- Claude Code e/ou Codex instalados e autenticados.

Workspace atual:

```bash
npx @luizcgvrj/plan-and-execute install both
```

Perfil do usuário:

```bash
npx @luizcgvrj/plan-and-execute install both --global
```

A ativação padrão é **selective**. Para tornar a skill somente explícita:

```bash
pae install both --global --activation explicit
```

Para voltar uma instalação gerenciada intacta ao modo seletivo:

```bash
pae install both --global --selective
```

Veja [INSTALLATION.pt-BR.md](skill/plan-and-execute/references/INSTALLATION.pt-BR.md).

## Ativação seletiva

A description da skill agora é propositalmente restritiva. Uma invocação automática só deve entrar em ORCHESTRATED quando houver sinal forte, por exemplo:

- dois ou mais workstreams verificáveis de forma independente e com pouco ganho de compartilhar o mesmo histórico;
- estudo amplo do repositório ou pesquisa externa substancial antes de decidir com segurança;
- migração, compatibilidade, segurança, integridade de dados, concorrência ou coordenação transversal;
- trabalho provavelmente atravessando sessões, provedores, janelas de quota ou compactação, com ganho real em persistência;
- workers isolados reduzindo contexto irrelevante ou melhorando validação independente.

**Não basta**, sozinho:

- aparecer “implemente”, “refatore” ou “corrija”;
- alterar vários arquivos relacionados;
- controller + service + entity + testes para uma mesma regra coesa;
- ser um bug/feature bounded normal;
- o contexto estar alto quando quase não resta trabalho.

Quantidade de arquivos é evidência fraca; independência semântica e valor de retomada são mais importantes.

### DIRECT

Se a skill for considerada implicitamente, mas não houver sinal forte:

- não cria `.ai-work`;
- não cria estudo;
- não inventaria requirements rastreáveis;
- não cria plano/TODO/task files;
- não abre fresh worker apenas para cumprir processo;
- não cria lifecycle state.

O agente principal segue implementando e validando no contexto atual enquanto esse contexto continuar útil.

## Promoção tardia

DIRECT não é uma decisão irreversível. Se a demanda crescer durante a execução, ela pode ser promovida.

Promova quando ainda houver trabalho substancial e, por exemplo:

- o escopo descoberto se dividir em resultados independentes;
- uma pesquisa ampla se tornar necessária;
- surgir migração/compatibilidade/segurança relevante;
- risco de interrupção/quota passar a justificar estado durável;
- a pressão de contexto ficar alta **e** o restante for grande/fragmentado o suficiente para ganhar com handoff persistente.

Percentual de contexto é apenas um sinal auxiliar. **Não existe uma regra universal de 90%.**

`promotectl.py` valida um snapshot compacto com:

- objetivo original;
- trabalho concluído;
- resultados já validados;
- decisões/invariantes ativas;
- paths/symbols relevantes;
- blockers/riscos;
- outcomes restantes;
- observação opcional de pressão de contexto;
- evidência git limitada (branch/status/diff stat).

Exemplo:

```bash
python <skill-dir>/scripts/promotectl.py validate \
  --spec /tmp/pae-promotion-spec.json --json

python <skill-dir>/scripts/promotectl.py render \
  --repo-root . \
  --spec /tmp/pae-promotion-spec.json \
  --output /tmp/pae-promotion-request.md \
  --json
```

O plano resultante contém **somente o trabalho restante**. O que já foi feito não é recriado artificialmente como TODO retroativo.

## Fluxo ORCHESTRATED completo

Depois que ORCHESTRATED é selecionado, o harness robusto continua:

1. Preservar o pedido completo.
2. Fazer apenas o estudo interno/externo capaz de mudar arquitetura, compatibilidade, limites de TODO, risco ou validação.
3. Inventariar partes do pedido e requirements observáveis.
4. Quebrar por outcomes context-cohesive e validation boundaries independentes.
5. Revisar cobertura, atomicidade, dependências, validação e minimalidade de contexto.
6. Persistir em `.ai-work/<plan-id>/`.
7. Executar um TODO isolado por vez com somente seus contextos/learnings atribuídos.
8. Reexecutar validação determinística fora do worker.
9. Persistir cada transição antes de avançar.
10. Retomar com segurança depois de interrupção de host/provedor/quota.
11. Gerar handoff final e remover apenas estado de planejamento/controle depois do sucesso.

O `SKILL.md` principal virou um control plane pequeno. Os detalhes ficam em [ORCHESTRATION.md](skill/plan-and-execute/references/ORCHESTRATION.md) e só são carregados quando necessário.

## Limites dos TODOs

Um fresh worker deve receber um problema semântico coeso, não um pacote arbitrário de arquivos.

Dois CRUDs independentes normalmente viram TODOs diferentes. Já entity, service, controller, migration e testes podem permanecer juntos quando implementam uma mesma regra/invariante e se beneficiam do mesmo raciocínio.

O schema v4 mantém `context_boundary`, `subtasks` retomáveis e `learning_targets` direcionais.

## Persistência e recuperação

Estrutura típica:

```text
.ai-work/<plan-id>/
├── .orchestrator-plan
├── manifest.json
├── orchestrator.config.json
├── REQUEST.md
├── STUDY.md
├── study.json
├── ANALYSIS.md
├── PLAN.md
├── PLAN_REVIEW.md
├── TODO.md
├── CONTEXT.md                 # opcional
├── contexts/                  # opcional
├── learnings/
├── tasks/
├── results/
└── logs/
```

Depois de uma interrupção, subtarefas concluídas continuam concluídas; apenas o estado interrompido é recuperado. Mudanças parciais de código permanecem. Outro agente/provedor pode seguir pelo estado em disco.

```bash
pae current
pae resume
pae resume --once
pae cancel
pae reset --force
```

## Modelo/nível por TODO

A capacidade é escolhida por **leaf TODO**, não pelo tamanho geral da demanda:

| Tier | Uso |
|---|---|
| `economy` | alteração mecânica/estreita e validação forte |
| `standard` | implementação/debug/teste normal bounded |
| `strong` | arquitetura, segurança, concorrência, migração, debugging difícil |
| `max` | problema ainda não resolvido depois de evidência de falha em rotas menores |

Cada definição mantém algo como:

```json
{
  "provider": "auto",
  "model_tier": "standard",
  "reasoning_effort": "medium"
}
```

Os IDs concretos dos modelos ficam em `orchestrator.config.json`, vindos de um único catálogo (`scripts/routingctl.py`): Claude `haiku`/`sonnet`/`opus`/`claude-fable-5-1`, Codex `gpt-5.6-luna`/`gpt-5.6-terra`/`gpt-6-astra`. Assim, se os créditos de um provider acabarem, outro provider/modelo compatível pode resolver o mesmo nível lógico sem perder o contrato da tarefa.

### Rota por sinais da folha, elevação por delegação

Cada folha — etapa de planejamento ou TODO — é roteada pelos sinais observáveis, nunca pelo tamanho do pedido ou pelo modelo do chat raiz:

```bash
python skill/plan-and-execute/scripts/routingctl.py route --signals bounded_implementation,weak_validation,implementation
# {"tier": "strong", "effort": "high"}
```

A skill **nunca troca o modelo/effort da sessão raiz** (isso invalida o cache de prompt do provider). Quando o modelo raiz está abaixo do piso de uma folha — inclusive quando a skill começa em Haiku ou Luna — ela delega essa folha a um worker fresco no tier do piso, com prompt mínimo, e consome só o resultado compacto. Um modelo raiz pequeno é um delegador, não um teto; também não existe teto escolhido pelo usuário.

### Escalada por evidência classificada

Cada tentativa falha registra um `failure_class` (campo do report do worker ou `planctl fail --failure-class`): `mechanical` repete o degrau uma vez e depois sobe um; `semantic` pula para o próximo tier mais forte (no Codex, Terra → Astra Low, nunca Terra High); `environmental` mantém a rota; `budget` retoma dos checkpoints; `plan_defect` bloqueia o TODO para replanejamento. Rate limit e quota nunca são evidência. As escadas por provider ficam no catálogo; o Haiku, que não aceita parâmetro de effort, é despachado sem `--effort`.

### Folha em duas fases e planejamento "decisões primeiro"

Um TODO `high` pode declarar `design_route`: um worker mais forte escreve primeiro uma nota de design bounded; depois o worker de implementação roda na rota mais barata do TODO com essa nota. Quando só algumas decisões do plano são difíceis, `request_analysis.hard_decisions` registra a passagem "decisões primeiro": workers fortes resolvem as decisões e um planner padrão escreve o plano mecânico.

Orçamentos opcionais por worker (`claude.max_turns`, `codex.rollout_token_budget`) transformam workers descontrolados em falhas `budget` retomáveis. O corpus `references/tier-evals.json` protege esse roteamento por regressão.

## Aprendizado seletivo entre TODOs

Fresh workers não recebem chats anteriores. Quando um TODO encontra uma solução difícil validada que um TODO futuro declarado precisaria redescobrir, o orquestrador pode produzir um arquivo curto e direcional depois da validação determinística.

Se não houver conhecimento útil, não há arquivo e não existe custo de contexto adicional.

## Contexto de execução

A regra continua omission-first:

- `CONTEXT.md` somente para fato não óbvio exigido por todos os TODOs;
- `contexts/<topic>.md` para subconjuntos estritos;
- fato de um único TODO fica na própria definição;
- descoberta de runtime fica em learning validado, não em contexto global mutável.

## Runner e providers opcionais

```bash
pae resume
pae resume --provider codex --once
pae resume --provider antigravity --once
```

Ou:

```bash
python <skill-dir>/scripts/run_isolated.py --plan .ai-work/<plan-id>
```

O runner usa processo novo por TODO, reexecuta validações de forma independente, limita saída diagnóstica e gera o resumo final a partir do estado autoritativo compacto.

## Modos de ativação

### Selective — recomendado

```bash
pae install both --activation selective
```

Continua auto-descoberta, mas near-miss negatives + DIRECT EXIT evitam custo em trabalho comum.

### Explicit-only

```bash
pae install both --activation explicit
```

O instalador gera cópias específicas:

- Claude: `disable-model-invocation: true`;
- Codex: `allow_implicit_invocation: false`.

O pacote fonte não é alterado. O marker v2 guarda hash da fonte e hash instalado para preservar detecção de edição local.

## Regression suite de roteamento

`references/routing-evals.json` protege o boundary com casos DIRECT, ORCHESTRATED e PROMOTE, inclusive near-miss negatives:

- refactor coeso não deve abrir plano só pela palavra “refactor”;
- editar muitos call sites relacionados não deve abrir plano por contagem de arquivos;
- contexto em 92% não deve promover quando resta um fix minúsculo;
- migração/pesquisa/múltiplos workstreams grandes devem continuar ativando a orquestração.

```bash
python skill/plan-and-execute/scripts/routing_self_test.py
python skill/plan-and-execute/scripts/promotion_self_test.py
```

## Desenvolvimento

```bash
npm run check
```

A suíte cobre lifecycle, estudo, isolamento de contexto, memória de tasks, providers, economia de tokens, concisão de artefatos, roteamento, promoção e cleanup.

## Segurança e cleanup

A skill não ignora sandbox, permissões, políticas organizacionais ou controles do repositório. Escritas paralelas só são apropriadas quando worktrees/isolamento eliminam conflito.

Depois do sucesso final, o cleanup apaga apenas `.ai-work/<plan-id>/` validado. Código, testes, commits, artefatos do produto e arquivos não relacionados permanecem.

## Licença

MIT. Veja [LICENSE](LICENSE).
