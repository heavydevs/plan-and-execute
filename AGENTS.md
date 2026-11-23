# AGENTS.md — roteador PAE: ChatGPT implementa; Claude valida

**Ordem de precedência (2026-11-23):** ler primeiro [`docs/operations/PAE_DUAL_AGENT_HANDOFF.md`](docs/operations/PAE_DUAL_AGENT_HANDOFF.md) e [`TODO.md`](TODO.md). Para pesquisa/arquitetura e aceites, consultar [`guia_de_pesquisa_execucao_tasks.md`](guia_de_pesquisa_execucao_tasks.md) e os arquivos da task. Textos antigos que mandam o ChatGPT fazer o parecer independente ou despachar automaticamente para GitHub Actions/Antigravity **não comandam mais** o `próximo`.

**Repositório/branch fixos:** `heavydevs/plan-and-execute` · `checkpoint/plano1-estudo-provider-switch-20261028`.

## Contrato obrigatório do comando `próximo`

1. **Sincronizar antes de decidir**: num checkout Git limpo, `git fetch` + `git pull --ff-only`; sem terminal/rede no ChatGPT, obter o HEAD/arquivos atuais via conector GitHub e escrever com CAS. Não simular `fetch/pull`.
2. Ler o estado oficial em `.ai-work/20261028-skill-study-provider-switch/manifest.json`, o espelho `.ai-work/20261028-skill-study-provider-switch/TODO.md`, o `TODO.md` da raiz (fase/dono) e a subchecklist aplicável. O manifesto, nunca uma conversa, governa conclusão/dependências.
3. **ChatGPT é o único que pode iniciar uma task nova.** Retoma a task ativa se for seu dono; caso contrário pega a primeira pendente elegível, pesquisa/arquitetura/implementa/testa, registra evidências e publica **handoff `aguardando_validacao_claude`**. **Para** após o push; não executa o gate final no lugar do Claude.
4. Se a fase for `aguardando_validacao_claude`, `claude_validando_corrigindo` ou `bloqueada` sob Claude, ChatGPT apenas relata o status e **para**. Não iniciar 016 nem revisar/corrigir em paralelo.
5. **Claude local é o único responsável pela validação final**; quando receber `próximo`, sincroniza, lê [`CLAUDE.md`](CLAUDE.md), aplica obrigatoriamente a skill `skill/plan-and-execute/SKILL.md`, revisa em contexto realmente independente, corrige/rearquitetura se preciso, testa, revalida hashes finais e cumpre o gate original. Somente após sucesso registra `completed` via controlador, commit/push e **para**. Claude **nunca** começa a próxima task.
6. Não falsificar revisão, aprovação, session_id, modelo/effort, testes, hashes ou recibos. Não modificar o validador para aprovar evidência fictícia. Revisão de quem alterou o código não é independente; exigir outra sessão após patch.
7. Uma task em execução, handoff ou bloqueio impede toda sucessora. Trabalhar numa única task por execução; observar o protocolo de concorrência, CAS e segurança. Não utilizar `agy`.

**Task de migração:** 015 permanece incompleta no manifesto e aguardando validação/correção de Claude. O parecer ChatGPT já publicado é informativo, não satisfaz sozinho `P1_015`. Não avançar para 016.

**Arquivos úteis:** [`CLAUDE.md`](CLAUDE.md), [guia de pesquisa](guia_de_pesquisa_execucao_tasks.md), [protocolo de handoff](docs/operations/PAE_DUAL_AGENT_HANDOFF.md), [roteador ChatGPT](.ai-work/chatgpt-executor/ENTRYPOINT.md), [instruções copiáveis do Projeto ChatGPT](.ai-work/chatgpt-executor/INSTRUCOES_PROJETO_CHATGPT.md). O protocolo anterior [`PAE_ONE_TASK_CODESPACE_PROTOCOL.md`](docs/operations/PAE_ONE_TASK_CODESPACE_PROTOCOL.md) preserva informações técnicas/históricas, mas suas regras conflitantes de roteamento estão revogadas.
