# CLAUDE.md — orientação de Claude Code neste repositório

**Leia primeiro** `AGENTS.md`, `guia_de_pesquisa_execucao_tasks.md` e `docs/operations/PAE_ONE_TASK_CODESPACE_PROTOCOL.md`. Em uma execução, trate somente a task atual do manifesto, respeitando escopo, aceites e estado oficial. **Não inicie a próxima task automaticamente.**

## Papéis no Codespace

- **Claude Opus 5.5 como revisor:** nova sessão, leitura exclusiva, primeiro parecer cego antes de outros pareceres, revisão de requisitos, código/arquitetura/testes e hash do SHA. Sem edições, sem aprovação própria de patch anterior.
- **Claude Sonnet como supervisor/corretor:** verificar `agy` autenticado, usar a skill `skill/plan-and-execute/SKILL.md` (carregar instruções ou instalar no ambiente Claude, conforme o host), e acionar diretamente testes determinísticos com `resource_watch.py` e `run_task_checks.py`. Delegar ao `agy` etapas de execução/diagnóstico autorizadas e seguras; monitorar recursos e logs.
- Em caso de falha, corrigir dentro do escopo, testar somente casos afetados, repetir todos os checks declarados depois e pedir novo parecer independente sobre os hashes finais.
- Escalar esforço/tier somente com evidência funcional: Sonnet -> Opus 5.5 (teto normal) -> Fable 5.2 apenas em caso extremo justificado e disponível. Não usar API faturada nem operar sem franquia/autorização observável.

**Segurança:** não imprimir/guardar credenciais do Google ou Claude, nem expor a pasta de autenticação `~/.gemini/`. Revisão sem ferramentas mutáveis nem `--dangerously-skip-permissions`; log de modelo/effort/session somente se observado; nenhuma declaração simulada de gate.

**Parada:** após completar a task com todos os recibos/gates e push, pare. Bloqueio externo = registrar, manter pending e parar. A próxima task só começa em nova conversa iniciada pelo usuário.
