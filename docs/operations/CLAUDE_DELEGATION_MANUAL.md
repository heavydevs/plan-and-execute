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

## 3. O que o usuário configura (Windows 11, uma vez)

1. No PowerShell instale a CLI de acordo com [setup oficial](https://code.claude.com/docs/en/setup). Em Windows com winget disponível, tente `winget install Anthropic.ClaudeCode`, confirme com `claude --version`, autentique com `claude auth login` (não usar `--console`) e confira `claude auth status --text`. Não cole a saída se ela contiver dados pessoais.
2. Cheque `Test-Path Env:ANTHROPIC_API_KEY` e `Test-Path Env:CLAUDE_CODE_USE_BEDROCK`; nenhuma chave de API ou roteamento API deve ser adotado por engano. Se estiverem presentes, analise as configurações locais e interrompa antes de gerar token.
3. Execute `claude setup-token` para gerar um token OAuth da assinatura; **não envie token no chat, email, commit ou log**.
4. Abra [Actions Secrets do repositório](https://github.com/heavydevs/plan-and-execute/settings/secrets/actions) → **New repository secret** → nome exato `CLAUDE_CODE_OAUTH_TOKEN`, valor token. Não armazene `ANTHROPIC_API_KEY` neste workflow. Se secret já existir, atualize o valor, nunca imprima.
5. Verifique [configurações de Actions](https://github.com/heavydevs/plan-and-execute/settings/actions): workflow permitido, execução Linux padrão. O **nosso fluxo usa base-action sem necessidade de conceder GitHub App com escrita**; evita instalar workflows automáticos de `@claude`/PR reviews que consumiriam quota não solicitada.
6. Na sua conta Anthropic, deixe uso adicional pago desabilitado caso queira limite estrito à franquia. Controle limite de uso e expiração/revogação do token. É possível que um plano ou política de conta limite ou recuse invocação: falha deve ser registrada como `entitlement`, não é aprovação nem autorização para API.
7. Retorne ao Projeto ChatGPT e informe **"Configurei o secret CLAUDE_CODE_OAUTH_TOKEN"**, sem compartilhar o valor. Não é preciso autorizar acesso de rede ao seu Windows.

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
