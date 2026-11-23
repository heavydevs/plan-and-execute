# Protocolo PAE — uma task por conversa, ChatGPT + Claude + Antigravity

**Versão:** 2026-11-22 · **Branch:** `checkpoint/plano1-estudo-provider-switch-20261028` · **Repositório:** `heavydevs/plan-and-execute`.

> **Estado de implantação:** esta é uma política de trabalho versionada, NÃO uma ponte de execução pronta. O usuário comprovou o comando `agy -p` funcionando no Codespace; esta sessão ChatGPT tem conector GitHub, mas NÃO dispõe de terminal no Codespace nem acesso direto ao Claude de lá. Instalação/autenticação Claude e acesso remoto controlado precisam ser comprovados. Não afirmar que uma tarefa foi delegada sem run autêntico.

## 1. Seleção e parada obrigatória

- O comando `próximo`, em uma **nova conversa ChatGPT**, resolve pelo `manifest.json` a primeira task não concluída e retoma sua etapa pendente. `TODO.md`, pesquisas e conversas não substituem o manifesto.
- **Uma única task por conversa.** Concluir significa pesquisa pertinente + arquitetura + implementação ou revisão aplicável + testes completos + revisão independente exigida + recibos + gate original + atualização oficial do estado + commit/push remoto verificado.
- Depois de `status=completed` e push, **PARAR**; jamais iniciar pesquisa ou implementação da próxima task na mesma conversa. O usuário abrirá outra conversa e escreverá `próximo`.
- Quando houver defeito reparável, corrigir e revalidar a MESMA task automaticamente. Depois da correção e da validação, parar se concluída. Quando faltar autorização, acesso, quota, observabilidade ou prova externa, registrar bloqueio, manter `pending` e **PARAR sem avançar**; na próxima conversa retomar a mesma task.
- **Situação atual:** task 015 pendente, predecessora 014; não executar 016. Para 015, o trabalho é review-and-fix: retomar revisão/gate, não inventar nova implementação inicial desnecessária.

## 2. Responsabilidades e ordem

1. **ChatGPT / pesquisa:** antes da implementação da task corrente, estudar requisitos, código, arquitetura e bibliografia atual (fontes oficiais, artigos, pesquisas, benchmarks relevantes). Registrar fontes, alternativas, custos, riscos, segurança, performance, testes e decisões no relatório por task. Reusar estudo válido; pesquisar amplamente de novo só onde ausente ou materialmente obsoleto. Não consumir contexto da pesquisa de todas as próximas tasks.
2. **ChatGPT / primeira implementação:** executar dentro do write scope, seguir as bibliotecas, padrões e arquitetura adotados. Incluir casos de teste focal e negativos, fazer commit/push CAS na mesma branch. Se a task já for de revisão (015), aplicar apenas correções que decorrem de achados reproduzidos.
3. **Claude Opus 5.5 / primeira revisão independente:** quando exigido pelo gate, iniciar worker novo com **comportamento read-only** em contexto separado, com SHA/arquivos/arquitetura/testes. Antes do primeiro parecer, não ler pareceres anteriores nem resultados de outra IA. Registrar findings por gravidade, arquivo, linha, repro, modelo/effort efetivos, ID real de sessão e hashes. A revisão não executa mutações. Solicitação de Opus não prova que o modelo executado foi Opus.
4. **Claude Sonnet / supervisão dos testes:** preferir Sonnet 5.5 quando comprovadamente disponível na assinatura, para invocar a skill PAE no Codespace, escolher controles de recursos/logs, delegar ao `agy` os trabalhos apropriados e consolidar falhas. **O executor determinístico** (`resource_watch.py`, `run_task_checks.py`, testes e GitHub Actions quando cabível) registra argv, ambiente, SHA, exit code e logs; `agy.status=SUCCESS` significa somente que o agente respondeu, nunca que todos os testes passaram.
5. **Claude Sonnet / autocorreção:** se review/teste/gate reprovar por defeito real, usar a própria skill Plan-and-Execute e somente a task corrente: reunir a bateria inteira de falhas quando viável, reproduzir cada causa, corrigir, rodar testes focais e então a bateria completa. Preferir `agy` em investigações/testes baratos, mas não inserir IA onde execução determinística direta é suficiente.
6. **Escalonamento supervisionado:** Sonnet aumenta esforço/tier somente após evidência classificada de falha funcional, não por quota, timeout de ambiente ou lentidão isolada. **Claude Opus 5.5 é o teto operacional normal** para depuração/arquitetura difícil; Fable 5.2 é excepcional, somente se o caso exigir capacidade extrema comprovada ou após repetidas falhas semânticas/arquiteturais reais do Opus documentadas, com disponibilidade e franquia verificadas. Nunca alternar automaticamente para API paga, não misturar limites de assinatura com preço de API.
7. **Gate final e nova independência:** após qualquer patch do Sonnet, a revisão anterior não aprova os hashes alterados. Uma **nova sessão independente** (preferencialmente Opus 5.5, ou rota equivalente formalmente admitida) revisa o último SHA. Executar todos os checks declarados, `P1_TESTS_015` e `P1_015` na task 015, além de `check_delivery.py` e o gate exigido da task corrente. Somente resultados autênticos permitem `planctl complete` e checklist [x]. Fazer commit/push e **parar**.

## 3. Monitoração, logs e economia

- `.ai-work/SERVICE_MAP.md` e `resource_watch.py` controlam IDs de validação, toolchains, recursos e progresso; conferir mapa atualizado, sem falsificar fingerprint. Usar `log_watch.py` para trechos recentes; salvar logs completos fora do prompt. Diferenciar teste bloqueado, teste falho, indisponibilidade do provedor e falta de evidência.
- Um timeout de ferramenta ou a suspensão do Codespace não podem virar aprovação, repetição infinita ou aumento arbitrário de modelo. Persistir checkpoint, fingerprint, IDs de processos/provedores apenas quando reais, tentativa e logs; retomar do estado salvo. Usar limite finito por execução e orçamento por sessão.
- Após corrigir todas as falhas conhecidas, executar novamente a bateria completa **uma vez**. Se ainda falhar, reagrupar resultados, corrigir focalmente e repetir esse ciclo; não reiniciar tudo após cada falha individual.
- Não deixar Claude gastar tokens apenas assistindo testes sem saída: preferir execução de subprocessos supervisionados com reports compactos e hashes verificáveis.

## 4. Codespace e fronteiras de confiança

- Codespace conhecido: `https://legendary-space-computing-9659w4rr6pj5h7qxw.github.dev/`. Evidência do usuário: `agy -p "Responda apenas OK" --output-format json --print-timeout 2m` retornou `status=SUCCESS` e um `conversation_id`. Não prova autenticação de `claude`, integração com esta sessão nem revisão formal max-tier.
- Antes de usar o Claude do Codespace: verificar `command -v claude`, `claude --version`, `claude auth status`, `command -v agy`, `agy --version`, `agy models` e localização da skill; **nunca imprimir conteúdo de tokens**. A skill do repositório em `skill/plan-and-execute/SKILL.md` não é automaticamente uma skill instalada no Claude.
- **O conector GitHub é transporte de código/commits/artifacts, não acesso SSH/terminal.** Sem ponte autenticada e auditada entre pedido versionado e executor Codespace, ChatGPT não pode efetivamente acionar o Claude ou o `agy`. Solicitar a primeira execução manualmente no Codespace é alternativa honesta enquanto a ponte não existir.
- **Acesso completo no Codespace (autorização expressa):** `agy` e `claude` podem executar com `--dangerously-skip-permissions`, sandbox interno desativado e sem solicitações de aprovação. Ver [runbook](CODESPACE_FULL_ACCESS_RUNBOOK.md). Não aplicar essas permissões aos runners públicos/PRs; nunca expor OAuth ou API paga. O revisor preserva leitura exclusiva por procedimento e deve provar hashes inalterados. O atual `review_dispatch.py` ainda exige argv read-only: sem atualização de contrato validada, execução em bypass não o satisfaz. Uma ponte futura deve ter controlador privado, autenticação, allowlist, leases e proteção anti-replay.
- `agy` expõe `conversation_id`; registrar modelo e esforço **observados ou verificados em metadados do CLI**, sem inferir `max` de texto de prompt. O gate 015 atual (`review_dispatch.py` e `check_delivery.py`) aceita somente provas formais previstas; **não** alterar seus critérios para aprovar Antigravity por conveniência. Integrar um adaptador validado e com testes negativos quando essa equivalência puder ser demonstrada.

## 5. Handoff e conclusão por conversa

A resposta final deve registrar: task/etapa, HEAD do código, pesquisa e decisões, arquivos/hashes, comandos/exit codes/logs, revisor real (modelo/effort/sessão verificáveis), gates, commit/push verificado, status no manifesto e bloqueios. Se `completed`, informar que **parou** e não iniciar a task seguinte. Se `pending`, informar exatamente a pendência e manter a task atual.

### Referências e atualização de capacidades

- Google, Antigravity CLI headless: https://antigravity.google/docs/cli/headless/
- Google, modelos e esforço: https://antigravity.google/docs/models e https://antigravity.google/docs/cli/commands/effort/
- GitHub, ciclo do Codespace: https://docs.github.com/en/codespaces/about-codespaces/understanding-the-codespace-lifecycle
- GitHub, segurança de runners: https://docs.github.com/en/actions/reference/security/secure-use
- Anthropic, Fable 5.2: https://www.anthropic.com/claude-fable-and-mythos-5-2
- Contratos locais: `AGENTS.md`, `guia_de_pesquisa_execucao_tasks.md`, `TASK_INPUTS.json`, `docs/plans/20261028-skill-optimization/support/check_delivery.py` e `docs/operations/CLAUDE_DELEGATION_MANUAL.md`.

**Este protocolo define a política desejada; não atesta instalação da ponte, testes de aceitação do novo fluxo nem a conclusão da task 015.**

### Observação do Codespace (2026-11-22)

O usuário confirmou `agy` autenticado e os modelos `claude-opus-5-5-high` / `claude-sonnet-5-5-high` listados por `agy models`. O executável **Claude Code independente não está instalado** (`claude: command not found`). Os modelos Claude chamados pelo `agy` não consomem necessariamente a franquia Anthropic. O runbook documenta a instalação opcional do Claude Code. Esta sessão ChatGPT não tem acesso ao terminal do Codespace.
