# Changelog

Todas as mudancas relevantes deste projeto serao registradas aqui.

## 0.2.0 - 2026-08-25

- Exige estudo integral do pedido, do repositório e de fontes autoritativas quando necessário antes de criar TODOs.
- Adiciona rastreabilidade determinística `request part (Pxxx) -> requirement (Rxxx) -> TODO`.
- Adiciona `ANALYSIS.md`, `PLAN_REVIEW.md` e o comando `planctl.py audit` aos quality gates.
- Exige revisão separada do plano, critérios de cobertura, atomicidade, dependências e validações.
- Rejeita TODOs executáveis `extreme` e exige justificativa de atomicidade para tarefas `high`.
- Adiciona protocolo de decomposição recursiva, replanning e roteamento de modelos para planejamento/revisão.
- Amplia os self-tests para cobertura perdida, mapeamentos inválidos, tarefas extremas e autostart inseguro.

## 0.1.0 - 2026-08-25

- Renomeia a skill para `plan-and-execute`.
- Adiciona instalador npm para Claude Code e Codex.
- Suporta escopos `workspace` e `user`.
- Adiciona comandos `install`, `status`, `paths`, `doctor` e `uninstall`.
- Protege alteracoes locais com marcador e hash SHA-256.
- Adiciona testes Node, self-test Python e workflows GitHub Actions.
