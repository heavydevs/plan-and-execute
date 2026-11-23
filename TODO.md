# TODO.md — controle de passagem ChatGPT → Claude (PAE)

> **Índice operacional, não manifesto de execução.** O status oficial, dependências e subtasks estão em [`.ai-work/20261028-skill-study-provider-switch/manifest.json`](.ai-work/20261028-skill-study-provider-switch/manifest.json) e no [TODO gerado do plano](.ai-work/20261028-skill-study-provider-switch/TODO.md). Não editar o manifesto manualmente; usar o controlador PAE. Regras vinculantes: [protocolo de handoff](docs/operations/PAE_DUAL_AGENT_HANDOFF.md).

## Task 015 — concluída

- [x] **015 — Review and correct assigned context, learned facts and token budgets**
  - **Fase operacional:** `concluida`
  - **Status oficial no manifesto:** `completed` (via `planctl complete`; 016 permanece `pending`)
  - **Revisor independente (observado):** `claude-opus-5-5`, effort `xhigh`, `model_tier=max`, sessão `8ccd6a6a-1f45-4ac6-bf83-a3fb2f2a8c4e`, `approved`, 0 achados bloqueantes ([dispatch-4](docs/research/20261028-skill-optimization/implementation/reviews/015/dispatch-4.json)); recibo em `docs/research/20261028-skill-optimization/implementation/015-receipt.json`
  - **Gates:** `P1_TESTS_015` (7/7) e `P1_015` com exit 0; `check_delivery.py --task 015` passou
  - **Pendências não bloqueantes:** achados medium/low abertos descritos em `015-outcome.md`
  - **Próxima task:** nenhuma ativa. Só um **novo** `próximo` do ChatGPT em novo chat seleciona a primeira elegível.

## Como interpretar `próximo`

**No ChatGPT:** sempre sincronizar primeiro. Se 015 estiver em `aguardando_validacao_claude`, `claude_validando_corrigindo` ou `bloqueada` sob Claude, **não iniciar 016**; apenas informar o responsável e a pendência. Quando 015 estiver comprovadamente `completed` no manifesto e `concluida` aqui, um **novo** `próximo` em novo chat autoriza o ChatGPT a iniciar a primeira task elegível, consultando o [TODO gerado](.ai-work/20261028-skill-study-provider-switch/TODO.md) e suas subchecklists.

**No Claude local:** sincronizar; executar revisão/correção da 015 com [a skill PAE](skill/plan-and-execute/SKILL.md), atualizar a fase e persistir evidências; **nunca** iniciar 016. Se a fase for `chatgpt_implementando` ou não houver handoff Claude, parar.

## Estados de coordenação permitidos

`chatgpt_implementando` → `aguardando_validacao_claude` → `claude_validando_corrigindo` → `concluida` (somente após gate e status oficial). `bloqueada` pode ocorrer em qualquer etapa, com dono, razão e evidências. Para retomada, o dono retoma somente a mesma task. Toda mudança de fase exige commit/push, HEAD confirmado e prevenção de conflito. O TODO é passagem de responsabilidade, não um comprovante de aceitação.

**Regra de exclusividade:** é proibido ter duas tasks iniciadas ou dois executores trabalhando na mesma task ao mesmo tempo. Todas as próximas tasks continuam pendentes no manifesto. Não adiantar a pesquisa nem execução da 016 neste handoff.
