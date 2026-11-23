# CLAUDE.md — executor local de validação e correção PAE

**Comando `próximo` recebido NO CLAUDE local = validar/corrigir SOMENTE a task entregue pelo ChatGPT. Nunca iniciar task.**

Leia primeiro: [`AGENTS.md`](AGENTS.md), [protocolo de dois responsáveis](docs/operations/PAE_DUAL_AGENT_HANDOFF.md), [`TODO.md`](TODO.md), `guia_de_pesquisa_execucao_tasks.md`, o manifesto e a task/checklist ativa. O documento antigo `PAE_ONE_TASK_CODESPACE_PROTOCOL.md` contém detalhes históricos sobre GitHub Actions, **não** define mais quem executa o `próximo`.

## Passos obrigatórios

1. Verificar alterações locais com `git status --short`, fazer `git fetch origin checkpoint/plano1-estudo-provider-switch-20261028`, garantir a branch correta, `git pull --ff-only origin checkpoint/plano1-estudo-provider-switch-20261028`, conferir `git rev-parse HEAD`. Não descartar alterações nem sobrescrever trabalhos. Em conflito ou acesso indisponível, parar e relatar.
2. Ler a fase operacional no `TODO.md` e o status oficial no `manifest.json`. Agir somente em `aguardando_validacao_claude` ou `claude_validando_corrigindo` para a **mesma task**. Na migração atual, a task é **015**. Não iniciar 016, mesmo depois de sucesso.
3. Ler e **utilizar a skill `skill/plan-and-execute/SKILL.md`** e as referências relevantes para revisar, diagnosticar, corrigir/rearquitetar, validar e persistir checkpoints. Não basta citar o nome da skill; aplicar efetivamente seu fluxo e ferramentas/checagens delimitadas pela task. Não lançar execução autônoma do plano inteiro.
4. Registrar início de validação no TODO com fase `claude_validando_corrigindo` e commit/push quando seguro; preservar code SHA/hashes como baseline.
5. **Parecer independente inicial:** usar contexto/sessão nova **sem edição** do código; estudar requisitos, arquitetura, código, testes e evidências primárias. Antes de produzir o primeiro parecer, não ler análises/revisões/conclusões de outras IAs. Registrar gravidade, arquivo, linha, reproduções, hash analisado e metadados reais de modelo/esforço/sessão. Opus pode ser revisor, mas não presumir modelo/tier apenas do nome solicitado.
6. **Se falhar:** corrigir/rearquitetar a task 015 com a skill PAE em contexto de execução separado do revisor, consolidar falhas, testar focos e executar bateria completa. Após qualquer alteração, solicitar **nova revisão independente em sessão nova**, sobre os hashes finais. Uma sessão corretora não aprova o próprio patch.
7. Rodar todos os aceites e gates originais, incluindo `P1_TESTS_015`, `P1_015` e `check_delivery.py` para 015, sem alterações fraudulentas. O gate pode exigir recibos formais de tier/session_id não fornecidos automaticamente pelo Claude Code local: verificar e, se incompatível, documentar a barreira sem falsificar.
8. Se **tudo** passar, atualizar a task somente via `planctl`, checkpoints/checklists/recibos, marcar fase `concluida`, fazer commit/push e verificar HEAD remoto. **Parar imediatamente.** Se persistir bloqueio externo, manter a task pendente, registrar fase `bloqueada`, razão, responsável Claude, evidências, publicar e **parar**.

**Restrições:** sem `agy`, sem API paga não autorizada, sem force-push, sem secrets em commits/logs, sem alegar teste/review que não ocorreu. Não tratar uma aprovação de código anterior como válida para hashes depois de correção. O ChatGPT é o único que poderá começar a task seguinte em outro `próximo`.
