# CLAUDE.md — instruções para Claude Code na Plan-and-Execute

**Leia primeiro:** `AGENTS.md`, `guia_de_pesquisa_execucao_tasks.md`,
`docs/operations/PAE_ONE_TASK_CODESPACE_PROTOCOL.md`; ao corrigir,
`skill/plan-and-execute/SKILL.md` e apenas as referências aplicáveis
(`WORKFLOW.md`, `TEST_RESOURCE_MONITORING.md` etc.).

## Fluxo ativo: Claude via GitHub Actions, sem Antigravity

- **Opus 5.5 — revisor independente:** sessão fresca, somente leitura;
  primeiro parecer sem relatórios de outros agentes. Examinar requisitos,
  código, arquitetura, testes e hashes; registrar achados reproduzíveis,
  gravidade, linha, modelo, esforço e sessão efetivamente observáveis.
  Não editar nem aprovar patch produzido pela própria sessão.
- **Sonnet 5.5 — corretor:** trabalhar exclusivamente na task atual. Ler e
  aplicar a skill Plan-and-Execute para classificar falhas, selecionar
  correção mínima e casos negativos/positivos. Respeitar `write_scope`.
  As correções ocorrem por patch em um checkout temporário, sem push.
- **Testes:** o runner GitHub Actions executa scripts determinísticos,
  monitores de recursos/logs e gates. Na etapa Claude autenticada por OAuth,
  não usar Bash ou acessos externos. Se algum teste falhar, registrar falhas
  verificáveis para novo reparo; não declarar sucesso por texto de IA.
- **Sem `agy`:** o usuário optou por não utilizar Antigravity neste fluxo.
  Claude do Codespace não é necessário à integração ChatGPT → GitHub Actions.
- **Escalonamento:** Sonnet → Opus 5.5 somente sob falha semântica comprovada;
  Fable 5.2 apenas em casos extremos e com disponibilidade verificada.
  Nunca alternar silenciosamente para API paga.
- **Revisão final:** cada patch exige revisão independente dos hashes finais.
  Aprovação formal só com checks, recibos e gate original verificados.

**PARADA OBRIGATÓRIA:** concluída a task com testes e revisão/gate aprovados,
estado oficial atualizado e commit/push remoto comprovado, **PARE**. Não
estude, inicie ou execute a próxima task. Somente uma NOVA conversa iniciada
pelo usuário pode começar outra. Em bloqueio externo, manter `pending`,
registrar o impedimento e parar.

**Segurança:** o Full Access local autorizado no Codespace não se aplica aos
GitHub-hosted runners. Não acessar nem publicar secrets, OAuth, API keys
ou credenciais. Não relaxar o gate nem inventar sessões, testes ou aprovação.
