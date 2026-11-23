# TODO.md — controle de passagem ChatGPT → Claude (PAE)

> **Índice operacional, não manifesto de execução.** O status oficial, dependências e subtasks estão em [`.ai-work/20261028-skill-study-provider-switch/manifest.json`](.ai-work/20261028-skill-study-provider-switch/manifest.json) e no [TODO gerado do plano](.ai-work/20261028-skill-study-provider-switch/TODO.md). Não editar o manifesto manualmente; usar o controlador PAE. Regras vinculantes: [protocolo de handoff](docs/operations/PAE_DUAL_AGENT_HANDOFF.md).

## Única task ativa — 015

- [ ] **015 — Review and correct assigned context, learned facts and token budgets**
  - **Fase operacional:** `aguardando_validacao_claude`
  - **Responsável atual:** `Claude local`
  - **Status oficial no manifesto no momento da migração:** `pending` (não concluído)
  - **Baseline de handoff:** commit [`71cb8673ae122979cffc09cfafef4263d0746ce1`](https://github.com/heavydevs/plan-and-execute/commit/71cb8673ae122979cffc09cfafef4263d0746ce1); antes do parecer novo, **Claude deve fazer fetch/pull e repinar o HEAD e os hashes do código reais**, pois este commit é apenas referência do estado anterior à migração
  - **Parecer técnico ChatGPT já registrado:** `docs/research/20261028-skill-optimization/implementation/reviews/015/parecer-cego-chatgpt-20261123-6a312f0.md`; não satisfaz automaticamente o gate de Claude/max-tier
  - **Entradas:** definição `.ai-work/20261028-skill-study-provider-switch/tasks/015-*.md`, `docs/plans/20261028-skill-optimization/TASK_INPUTS.json`, pesquisa `docs/research/20261028-skill-optimization/pesquisas-por-task/015-pesquisa-arquitetura.md`, antecessora 014, checklist interno e `AGENTS.md`
  - [ ] Claude — produzir primeiro parecer independente novo, com SHA, prova de sessão/modelo/effort quando observáveis, achados por gravidade/arquivo/linha/reprodução
  - [ ] Claude — corrigir/rearquitetar esta task com a skill PAE se houver defeitos; executar testes focais e bateria integral; exigir novo parecer independente após qualquer patch
  - [ ] Claude — obter evidências autênticas de `P1_TESTS_015`, `P1_015`, `check_delivery.py`, recibos, hashes finais e aceite de todos os critérios
  - [ ] Claude — somente após gate aprovado, concluir via controlador, atualizar o TODO gerado, marcar `concluida`, fazer commit/push e **PARAR**
  - **Bloqueio conhecido a investigar (não aprovado):** o gate formal pode exigir prova de modelo/tier/effort/`session_id` que a instalação local de Claude Code não emite no formato de `review_dispatch.py`; não falsificar ou relaxar o contrato

## Como interpretar `próximo`

**No ChatGPT:** sempre sincronizar primeiro. Se 015 estiver em `aguardando_validacao_claude`, `claude_validando_corrigindo` ou `bloqueada` sob Claude, **não iniciar 016**; apenas informar o responsável e a pendência. Quando 015 estiver comprovadamente `completed` no manifesto e `concluida` aqui, um **novo** `próximo` em novo chat autoriza o ChatGPT a iniciar a primeira task elegível, consultando o [TODO gerado](.ai-work/20261028-skill-study-provider-switch/TODO.md) e suas subchecklists.

**No Claude local:** sincronizar; executar revisão/correção da 015 com [a skill PAE](skill/plan-and-execute/SKILL.md), atualizar a fase e persistir evidências; **nunca** iniciar 016. Se a fase for `chatgpt_implementando` ou não houver handoff Claude, parar.

## Estados de coordenação permitidos

`chatgpt_implementando` → `aguardando_validacao_claude` → `claude_validando_corrigindo` → `concluida` (somente após gate e status oficial). `bloqueada` pode ocorrer em qualquer etapa, com dono, razão e evidências. Para retomada, o dono retoma somente a mesma task. Toda mudança de fase exige commit/push, HEAD confirmado e prevenção de conflito. O TODO é passagem de responsabilidade, não um comprovante de aceitação.

**Regra de exclusividade:** é proibido ter duas tasks iniciadas ou dois executores trabalhando na mesma task ao mesmo tempo. Todas as próximas tasks continuam pendentes no manifesto. Não adiantar a pesquisa nem execução da 016 neste handoff.
