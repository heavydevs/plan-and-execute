# Manual: ChatGPT principal + Claude Opus 5.5 por GitHub Actions

**Data da pesquisa:** 2026-11-22. **Branch de execução:** `checkpoint/plano1-estudo-provider-switch-20261028`. **Estado inicial:** integração documentada e preparável, **sem invocação Claude autenticada**; revisão formal da task 015 continua pendente. Não avançar para 016 enquanto o gate 015 falhar.

## 1. Objetivo e fronteiras

O ChatGPT executa pesquisa, implementação cotidiana, testes, correções, integração e commits. O Claude Opus 5.5 é delegado para:

1. **revisão independente obrigatória** de uma task de review que exija modelo max: leitura exclusiva, sem edição, sessão recém-criada, parecer primeiro sem consultar revisões anteriores; e
2. **implementação excepcional** somente quando a task de implementação concreta não for apropriada às capacidades atuais/ferramentas do ChatGPT, mediante razão explícita com evidência: falhas semânticas repetidas, lacuna de capacidade comprovada ou risco transversal demonstrado. Não escalar por tamanho, dificuldade presumida ou conveniência.

A implementação Claude produz somente **patch e relatório** em artifact GitHub Actions; o ChatGPT valida, integra, testa, faz commit/push. O mesmo Claude que escreveu código NÃO pode aprovar independentemente esse código. Um novo review exige nova sessão, snapshot e hash final.

**Arquitetura:** ChatGPT GitHub connector (CAS commit da request) → push de um único arquivo de pedido → job preflight sem segredo → revisão OU implementação em runner Linux padrão → upload de evidências → ChatGPT verifica run+SHA+hashes, aplica patch validado, executa checks e gate. Não é conexão SSH ou controle genérico do Claude Cloud; é Claude Code executado em GitHub-hosted runner. O Windows pode permanecer desligado.

## 2. Auditoria das fontes e custos

- Anthropic, [Claude Code GitHub Actions](https://code.claude.com/docs/en/github-actions) — configurações de assinatura via `CLAUDE_CODE_OAUTH_TOKEN`, `claude setup-token`, argumentos CLI, segurança de secretos e recursos usados. O OAuth destina o uso à assinatura; o limite do plano continua aplicável. Não se deve informar nem `ANTHROPIC_API_KEY` nem outros provedores de inferência no nosso workflow.
- Anthropic, [CLI reference](https://code.claude.com/docs/en/cli-reference) — `--model`, `--effort`, `--max-turns`, `--restricted`, `--permission-prompts none`, `--tools`, `--json-schema`, `--strict-mcp-config`. Instalações recentes são necessárias. O pedido de modelo/esforço **não prova** automaticamente configuração observada.
- Anthropic, [Legal and compliance](https://code.claude.com/docs/en/legal-and-compliance) — assinatura sujeita aos Termos de Uso e limites de uso ordinário; não tratar OAuth pessoal como licença para revender serviço, servidor multiusuário ou disparos descontrolados.
- [Claude Code Base Action outputs](https://github.com/anthropics/claude-code-action/blob/main/base-action/README.md) — `session_id`, `structured_output`, `execution_file`, `conclusion`. Apenas resultado registrado pelo action após invocação pode ser evidência; `attempt_id` documental não é `session_id`.
- GitHub, [Billing for GitHub Actions](https://docs.github.com/en/billing/concepts/product-billing/github-actions) — executores padrão de repositórios públicos são gratuitos; runners maiores, armazenamento e outros recursos possuem políticas próprias. Repo público não significa armazenamento ou execução ilimitados.
- GitHub, [Security hardening](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions) — mínima permissão, action fixada por SHA, evitar tokens em logs, separar entrada não confiável de comandos, secrets somente após preflight.
- OpenAI, [Projects in ChatGPT](https://help.openai.com/pt-br/articles/10169521-projects-in-chatgpt) — **Configurações do projeto → Instruções**, aplicáveis a novos chats deste Projeto.

### Não confundir produtos nem franquias

`Claude Code GitHub Action` + token OAuth de assinante **não** é o produto separado `Claude Code Review` gerenciado. O segundo pode ser faturado por revisão. Também não é `Claude Code in the cloud` na interface web. A Action executa o binário Claude Code no runner. O passo autenticado de fumaça (uma chamada pequena) é necessário antes de prometer que o modelo e esforço escolhidos estão disponíveis na assinatura e não caem em fallback. Interromper se a ação pedir API key ou indicar cobrança inesperada. Nenhum preço de API é igual a "créditos" de assinatura.

## 3. Configurar 100% pela internet (GitHub + navegador; Windows **não** é requisito)

**A execução é integralmente remota.** O GitHub Actions executa Claude Code nos runners Linux padrão; o usuário não instala servidor, Windows CLI, SSH ou abre porta no roteador. Existe **apenas um provisionamento de autenticação** para ligar a assinatura Claude ao workflow. Como a assinatura Anthropic não pertence ao GitHub, a Action não descobre esse token automaticamente a partir da sua sessão GitHub.

**Procedimento recomendado sem instalar software local — GitHub Codespaces temporário:**

1. Abra [GitHub Codespaces](https://github.com/codespaces), entre na seção **Explore quick start templates** e crie um codespace a partir de um **Blank template**. Não precisa clonar o projeto PAE somente para gerar o token. Escolha a menor máquina disponível e confirme **quem paga** antes de criar: Codespaces tem franquia própria, diferente do GitHub Actions. Em repositório de organização, o proprietário/pagador depende das configurações da organização. Um template em sua conta pessoal normalmente simplifica esse controle.
2. Quando abrir VS Code no navegador, abra **Terminal → New Terminal**. No terminal Linux, use o instalador oficial:
   ```bash
   curl -fsSL https://claude.ai/install.sh | bash
   ```
   Se necessário, abra um novo terminal para atualizar PATH e execute `claude --version`.
3. Execute `claude auth login`. A Anthropic permite copiar a URL de autenticação para abrir no navegador quando o terminal remoto não abre janela automaticamente. Faça login **na assinatura Claude** (Pro/Max/Ultra/Team, quando elegível), não no Console/API. Conclua com `claude auth status --text`; não publique seus dados.
4. Verifique que não há configuração de API paga. Em um terminal de uso pessoal e limpo, rode **sem imprimir segredos**:
   ```bash
   test -z "${ANTHROPIC_API_KEY:-}" && echo "API key ausente" || echo "ATENCAO: API key presente"
   ```
   Se aparecer chave presente, pare: não assuma que a CLI consumirá a franquia da assinatura.
5. Execute `claude setup-token`. A documentação da Anthropic prevê o token persistente para GitHub Actions. **Não copie o token nesta conversa, não faça print, não o salve no repositório nem em comandos que fiquem no histórico do shell.**
6. Abra [GitHub Actions Secrets do projeto](https://github.com/heavydevs/plan-and-execute/settings/secrets/actions) em outra aba. Crie um **New repository secret** chamado exatamente `CLAUDE_CODE_OAUTH_TOKEN` com o valor do passo anterior. Se já existir, atualize-o. Nossa Action NÃO configura `ANTHROPIC_API_KEY`.
7. Confirme [Settings → Actions](https://github.com/heavydevs/plan-and-execute/settings/actions): Actions habilitado, runners padrão disponíveis, política de execução apropriada. Já existe `.github/workflows/pae-claude-delegation.yml` na branch checkpoint; não é preciso instalar a Claude GitHub App com permissões de escrita nem usar o wizard que cria PRs/workflows genéricos `@claude`.
8. **Apague o Codespace temporário**, não apenas feche a aba: volte a [github.com/codespaces](https://github.com/codespaces), no menu `...` do codespace criado use **Delete** para eliminar a cópia das credenciais e parar armazenamento/tempo de máquina. O secret do repositório permanece registrado no GitHub.
9. Confira no painel da Anthropic que **uso extra pago** está desabilitado se você deseja limite estrito à franquia. Retorne ao Projeto ChatGPT e diga apenas **"Configurei o secret CLAUDE_CODE_OAUTH_TOKEN"** sem revelar o valor. Eu faço o primeiro teste autenticado com uma solicitação explícita e verifico logs, autorização, sessão e custo; se falhar, não migro silenciosamente para API.

**Opcional:** se preferir gerar o token no seu Windows, instale Claude Code conforme [setup Windows](https://code.claude.com/docs/en/setup), faça `claude auth login`, `claude setup-token` e comece no passo 6. Isso é escolha sua, **não** requisito da arquitetura.

### Solução recomendada quando o OAuth por terminal falha no GitHub Codespaces

**Sintomas:** navegador redireciona para `localhost:<porta>/callback`, há erro `ERR_CONNECTION_REFUSED`, ou o Claude CLI rejeita repetidamente `code#state` com `Invalid code`. Essa combinação está reproduzida em [anthropics/claude-code #91176](https://github.com/anthropics/claude-code/issues/91176). **Não** repita indefinidamente códigos, nem abra porta do roteador ou exponha callback OAuth em Codespaces. Em certas versões, o erro persiste com códigos frescos e corretos.

**Primeira opção — usar a extensão gráfica oficial, sem Windows local:**

1. Cancele `claude setup-token` ou `claude auth login` pendente no terminal remoto com `Ctrl+C`. Ignore códigos de autorização que já foram revelados em conversas ou capturas.
2. No GitHub Codespaces (VS Code Web), abra Extensions (`Ctrl+Shift+X`), procure **Claude Code** publicado por **Anthropic**, instale e abra o painel da extensão (ícone de estrela/spark no menu lateral).
3. Escolha **Claude.ai Subscription**, **não** API Key / Claude Console. Na tela *Continue in browser*, copie o link *If the browser didn't open, visit this URL* para outra aba e autentique-se em Claude.ai.
4. Se o site exibir um **código de autorização** em vez de callback `localhost`, copie-o diretamente para a **extensão** na entrada *Or, paste your authorization code manually* e clique **Continue**. Não envie o código aqui no ChatGPT.
5. Confira que a extensão exibe sua conta e dados de uso. No terminal do mesmo Codespace, execute `claude auth status --text` e confirme login com sua assinatura, sem expor credenciais.

A extensão e a CLI funcionaram com credenciais compartilhadas em um relato de 19/10/2026 no [issue #91176](https://github.com/anthropics/claude-code/issues/91176), mas isso é **um workaround da comunidade, não garantia oficial em todo Codespace**. Instalação da extensão e autenticação pela assinatura são suportadas pela [documentação da Anthropic](https://code.claude.com/docs/en/vs-code).

**Para obter o token de CI, ainda é necessário um passo distinto:** `claude setup-token` produz a credencial longa `CLAUDE_CODE_OAUTH_TOKEN` destinada a GitHub Actions ([documentação oficial](https://code.claude.com/docs/en/authentication)). O login pela extensão **não garante** que a geração desse token funcione: o comando pode iniciar outro fluxo OAuth e voltar a falhar. Se isso ocorrer, **não** copie arquivos internos de credenciais da extensão para o GitHub, não publique OAuth em URL nem cadastre uma API key paga para contornar a falha. Use uma instalação temporária do Claude Code no seu Windows para gerar o token localmente, por onde o navegador e o callback estão no mesmo computador; o **trabalho posterior continuará 100% no GitHub Actions**. Essa alternativa exige apenas a geração inicial do token, não manter o Windows ligado.

**Segurança:** authorization `code`, `state` e token longo devem ficar privados. Se você expôs URL ou código em conversa, descarte a tentativa correspondente; não tente reutilizá-la. Se surgirem erros 429, cesse retentativas por enquanto para evitar novos limites.

### O que é gratuito e o que tem franquia separada

| Componente | Plano/cobrança |
| --- | --- |
| GitHub Actions, runner padrão no repositório público `heavydevs/plan-and-execute` | Computação gratuita; artefatos/cache têm limites de armazenamento |
| GitHub Codespaces usado **uma única vez** no navegador | Franquia **separada**. Conta pessoal GitHub Free: 120 core-horas + 15 GB-mês; contas Pro: 180 core-horas + 20 GB-mês. Acima disso pode cobrar conforme orçamento. Para repositórios de organização, verifique quem é o proprietário pagador |
| Claude Code GitHub Action com `CLAUDE_CODE_OAUTH_TOKEN` | Consome franquia da assinatura Anthropic, sujeita a disponibilidade e limites do plano; nenhum token de API é fornecido pelo nosso workflow |
| `ANTHROPIC_API_KEY` ou Claude Code Review gerenciado | Produtos/cobranças separados; **não utilizados** no fluxo |
| GitHub público com benefícios | **Não** inclui automaticamente consumo ilimitado de Opus, nem autoriza outra conta Anthropic |

Fontes: [GitHub standard public runners](https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job), [Codespaces pricing](https://docs.github.com/en/billing/concepts/product-billing/github-codespaces), [who pays for organization Codespaces](https://docs.github.com/en/codespaces/managing-codespaces-for-your-organization/choosing-who-owns-and-pays-for-codespaces-in-your-organization), [blank Codespaces template](https://docs.github.com/en/codespaces/developing-in-a-codespace/creating-a-codespace-from-a-template), [Anthropic setup](https://code.claude.com/docs/en/setup), [Claude authentication](https://code.claude.com/docs/en/authentication), [Claude Code GitHub Actions](https://code.claude.com/docs/en/github-actions).

## 4. Arquivos entregues no repositório

- `.github/workflows/pae-claude-delegation.yml`: acionado **somente** quando o request versionado é alterado na branch checkpoint; contém jobs mutuamente exclusivos, `review` e `implement`.
- `.ai-work/chatgpt-executor/claude_delegate.py`: preflight de branch, SHA de fonte, tipo da task, estado do manifesto, origem de solicitação, escopo, evidências e entrada; coleta evidência real; falha fechado.
- `.ai-work/chatgpt-executor/tests/test_claude_delegate.py`: testes determinísticos offline; **não** prova chamada real ao modelo.
- `.ai-work/chatgpt-executor/INSTRUCOES_PROJETO_CHATGPT.md`: instrução copiável para colar nas Configurações do Projeto ChatGPT.
- `docs/operations/CLAUDE_DELEGATION_MANUAL.md`: este manual.
- Request sob demanda `.ai-work/chatgpt-executor/requests/claude-delegation.json`: **não** é criado por padrão, para não disparar inferência acidental.

O workflow só solicita Claude quando houver um commit dedicado cuja única mudança seja request; HEAD-pai deve corresponder a `source_head`. A task precisa ser a primeira não concluída e estar declarada no `TASK_INPUTS.json`. Falha em qualquer condição bloqueia antes do job com segredo.

## 5. Fluxo de uma solicitação

O ChatGPT conectado ao GitHub lê `AGENTS.md`, o guia, o manifest e a task; decide se deve escalar. Se sim, grava evidência concisa e autenticável **dentro do repositório**, no path `evidence_ref` (exemplo: relatório de falha observado, não uma afirmação genérica), e publica esse relatório antes do disparo. Em seguida cria **um commit separado** mudando exclusivamente o request:

```json
{
  "schema": "pae-claude-delegation/1",
  "attempt_id": "claude-015-review-first-20261122",
  "mode": "review",
  "task_id": "015",
  "source_head": "<SHA completo do commit que já contém código e evidência>",
  "escalation": {
    "reason": "cross_cutting_high_risk",
    "evidence_ref": "docs/research/20261028-skill-optimization/implementation/reviews/015/web-chat-remediation-and-gates-20261121-72ed5d.md",
    "summary": "Revisão independente max-tier do código corrigido necessária antes do gate final, com arquivos, hashes e testes já documentados."
  }
}
```

A revisão é modo read-only. Para delegar implementação usar `mode=implement`, task de implementação e `reason` pertencente ao contrato: `verified_capability_gap`, `repeated_semantic_failure` ou `cross_cutting_high_risk`. O escopo é exatamente `write_scope` do catálogo; sem alterações em `main`, testes/gates/manifest fora de escopo e sem push direto. A rejeição da request não consome inferência quando o preflight funcionar corretamente.

Depois do run, recuperar o artefato pela API GitHub Actions, confirmar `run_id`, `head_sha`, `attempt_id`, input hashes, sessão e `conclusion`. Para revisão: publicar parecer, corrigir high/critical e solicitar outro parecer para SHA diferente. Para implementação: verificar `implementation.patch` e escopo, aplicar a revisão de patch pelo ChatGPT, rodar os testes originais e publicar com CAS. **Nunca** aplicar automaticamente um patch de um modelo ao repositório antes de verificar origem, conteúdo, write scope e testes. Se o patch for insuficiente, repetir só quando houver justificativa e orçamento; não criar ciclos infinitos.

## 6. Status e gates originais

O `check_delivery.py` não é alterado/afrouxado pela integração. Na task 015, precisa de revisor externo realmente independente com `provider`, `model`, `native_effort`, `session_id`, `reviewed_input_hashes`, `findings` e `verdict`, e proíbe reuso de sessão/dispatch. O Action expõe `session_id` e saída estruturada, mas **não expõe necessariamente no contrato da saída o modelo/effort efetivamente observados**, então o bridge deixa `model_observed` e `native_effort_observed` como `null`. É proibido preencher esses campos com os valores solicitados e dar aprovação formal. Para completar `P1_015`, implementar/adaptar prova autenticada de configuração real do processo e equivalência do dispatch, com testes negativos, ou obter dispatcher original. Até lá, task 015 continua `pending`.

Os sete checks de 015 e `P1_TESTS_015` foram observados como PASS em código anterior, mas `P1_015` depende do receipt final real. Uma revisão de código novo exige novos hashes e testes do mesmo SHA.

## 7. Instruções do ChatGPT e comando de continuidade

Abra o Projeto ChatGPT atual → menu **•••** → **Configurações do projeto** → **Instruções**. Cole na íntegra o conteúdo de `.ai-work/chatgpt-executor/INSTRUCOES_PROJETO_CHATGPT.md`. Essa configuração de UI é manual; nenhum commit GitHub altera as configurações privadas do Projeto.

Em uma nova conversa **dentro do mesmo Projeto**, digite simplesmente **`próximo`**. A IA deve ler o manifest atual no GitHub; retomar a primeira task incompleta; corrigir falhas, testar e, quando comprovado que é necessário, acionar Claude via request. Não precisa repetir manual; não presumir sucesso sem run. Não iniciar 016 antes de 015 passar o gate.

## 8. Segurança, manutenção e recuperação

- GitHub secret não deve ser mostrado em prints, outputs do workflow, debug, PR de fork ou arquivos de artefato. Usar `show_full_output=false` e jobs `contents: read`; um modelo pode ser induzido a vazar conteúdo se receber ferramentas arbitrárias. Nunca habilitar Bash/network/MCP em modo de revisão.
- No modo implementação, somente `Read,Glob,Grep,Edit,Write` são oferecidos. O preflight delimita o escopo e a coleta rejeita qualquer arquivo tocado fora da lista declarada. **Não há garantia absoluta de isolamento pelo prompt**; a checagem determinística do diff é indispensável. Restrição não impede um arquivo de código de conter instrução maliciosa, portanto o patch será revisto pelo GPT-6.
- Nenhum segredo deve entrar em arquivos controlados pelo repositório. Rodar preflight sem segredos primeiro, não confiar em strings de issue/PR como comandos.
- O Action é fixado a SHA verificado (não branch mutável). Atualização exige rever nova versão e testes.
- Se token vazar, revogar na Anthropic e substituir o secret GitHub. Se não quiser mais Claude, remover `CLAUDE_CODE_OAUTH_TOKEN` e desabilitar workflow; a tarefa permanecerá pendente se o gate depender dessa integração.
- Sem quota, autenticação, hash, sessão ou metadata reais: registrar `blocked`, não mudar o contrato ou usar outra API de cobrança silenciosamente. Não há execução prometida entre chats: a continuidade depende de novo comando e de workflow disparado.
