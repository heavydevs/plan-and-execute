# Plan and Execute

**Use um plano persistente com múltiplos workers somente quando esse custo realmente compensa.**

`plan-and-execute` é uma skill de orquestração seletiva para Claude Code e OpenAI Codex. Demandas pequenas/médias coesas permanecem no contexto atual do agente. Trabalho long-horizon entra no fluxo completo desde o início, ou pode ser promovido mais tarde se crescer durante a implementação — sem jogar fora o que já foi feito.

[English version](README.md)

## O que mudou na 0.8

A regra central agora é:

```text
DIRECT por padrão -> ORCHESTRATE por evidência -> PROMOTE quando necessário
```

Isso evita pagar estudo, planejamento rastreável, arquivos de TODO e fresh workers em toda implementação apenas porque a skill parece semanticamente relacionada.

Quando a orquestração realmente é necessária, **todo o comportamento robusto anterior continua existindo**:

- `TODO.md` persistente e conciso;
- um arquivo de definição por TODO;
- `manifest.json` como estado autoritativo;
- subtarefas/checkpoints retomáveis;
- rastreabilidade request-part -> requirement -> TODO;
- `provider`, `model_tier` e `reasoning_effort` recomendados individualmente por TODO;
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
| Gemini CLI | Sim | Não | Opt-in |
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
├── packets/                   # entrada imutável por revisão para o worker
├── results/
└── logs/
```

Depois de uma interrupção, subtarefas concluídas continuam concluídas; apenas o estado interrompido é recuperado. Escritas atômicas com revisão e lease de heartbeat/epoch impedem um runner antigo de reverter checkpoints novos. Mudanças parciais de código permanecem. Outro agente/provedor pode seguir pelo estado em disco.

```bash
pae current
pae resume
pae resume --once
pae resume --provider codex --takeover
pae cancel
pae reset --force
```

Falhas de disponibilidade persistem um horário de retry sem consumir o orçamento de escalonamento funcional. O supervisor libera o lease enquanto espera, permitindo takeover imediato por outro provider. Falhas de ambiente ou do contrato de conclusão bloqueiam para correção; apenas falhas de capacidade ou validação determinística escalam esforço/tier/provider.

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

Os IDs concretos dos modelos ficam em `orchestrator.config.json`. Assim, se os créditos de um provider acabarem, outro provider/modelo compatível pode resolver o mesmo nível lógico sem perder o contrato da tarefa. Escalonamento ocorre por evidência de falha, não por medo.

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
pae resume --provider gemini --once
```

Ou:

```bash
python <skill-dir>/scripts/run_concise.py --plan .ai-work/<plan-id>
```

O runner compila a definição da tarefa e somente seus contextos/learnings atribuídos em um pacote único com proveniência, depois abre um processo novo para o TODO. O host reexecuta validações, calcula arquivos alterados somente no attempt atual, registra métricas de tokens/cache/custo/duração quando o provider as fornece, limita saída diagnóstica e gera o resumo final a partir do estado autoritativo compacto.

Para persistir proativamente uma nova rota antes da retomada:

```bash
python <skill-dir>/scripts/planctl_concise.py route-set \
  --plan .ai-work/<plan-id> --task 001 --provider codex \
  --model-tier strong --effort high --unblock
pae resume --provider codex --takeover
```

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
