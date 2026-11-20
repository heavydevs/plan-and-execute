# Gate independente real para a task 015 — alternativa à CLI Codex/Claude

## Por que este mecanismo existe

O ChatGPT hospeda conectores e execução de arquivos, mas não disponibiliza a CLI Codex/Claude no runner local. A inspeção feita pelo próprio chat **não é revisão independente**. Em 2026, GitHub Models não existe mais (encerrado em julho); o GitHub Copilot CLI pode usar o `GITHUB_TOKEN` no GitHub Actions com `copilot-requests: write`, sujeito à política e cobrança do proprietário do repositório. Não existe garantia prévia de que a organização concedeu a permissão.

## Execução verificável sem credencial persistente

1. Checkout exato por SHA no GitHub Actions com `permissions: contents: read, copilot-requests: write` e `persist-credentials: false`.
2. Um **único** request explícito em `.ai-work/chatgpt-executor/requests/015.json` (id, task, modelo, esforço, quantidade máxima 1). Apenas a inclusão/edição do request dispara o workflow. `workflow_dispatch` permite repetição intencional, mas nunca automação periódica ou repetição indiscriminada.
3. `copilot_review.py` captura os hashes das fontes e do recibo/relatório 014; envia um prompt de inspeção de código, limita ferramentas de leitura (`view,grep,glob`), nega edição, shell, MCPs embutidos, internet e subagentes. Seleciona explicitamente **Claude Opus 5.5** com esforço `xhigh`, pertencente à rota max da skill original. A execução é limitada por timeout.
4. Exige JSONL autenticado com `session.start.data.sessionId`, `selectedModel` e `reasoningEffort`, e mensagem `assistant.message` contendo findings JSON. Se qualquer identidade, veredito, campo ou hash faltar, **falha fechada**, sem prova de aprovação.
5. Com resposta válida, grava `docs/research/20261028-skill-optimization/implementation/reviews/015/{brief-1.md,findings-1.json,dispatch-1.json,reviewer-fragment.json}` no runner. Publica artefato do workflow. Não há commit automático nem token de escrita; ChatGPT compara o `run_id`, SHA/identidade, baixa artefatos e submete commit por GitHub connector mediante CAS.
6. Se o review reportar critical/high, corrigir a implementação e repetir um **novo** review do SHA final; nunca reutilizar aprovação da árvore antiga. O próprio usuário autorizou este mecanismo alternativo no escopo de engenharia da execução; não rotular o resultado como `review_dispatch.py` ou como sessão Codex.
7. Se aprovado, confirmar que todos os 7 checks declarados realmente passaram (logs, checks.json/fingerprint). Gerar recibo e relatório 015 a partir dos artefatos reais, sem copiar resultados de 014 e sem inventar identificadores. Executar o **original** gate `P1_015`/`check_delivery.py` sobre o snapshot final. Marcar checkpoint/status somente depois do gate; preservar os `manifest` e arquivos projetados por `planctl`.

## Falhas legítimas e limites

- Repositório sem Copilot Requests habilitado ou política/billing da organização não autorizada: o workflow falha em autenticação; registrar `environment_blocked`, não `reviewed`.
- Revisor retornou sem `session.start`, com modelo/effort diferente, JSON inválido, leitura insuficiente ou falha de serviço: não emitir aprovação.
- O token do GitHub Actions deve ser **somente leitura do repositório**; `copilot-requests: write` autoriza inferência, não mudança no Git. A inferência pode gastar créditos do repositório, mesmo sem um segredo adicional. O pedido de execução é restrito a **uma chamada e um SHA**, limitado por tempo; repetir só após decisão sobre as falhas.
- A evidência produzida é do **GitHub Copilot CLI / Claude Opus**, um roteador autenticado do GitHub. Não alterar etiquetas para fingir que houve `review_dispatch.py` de Codex. O `check_delivery.py` permanece inalterado e exige conteúdo verificável do modelo, hashes e sessão nova; a IA revisora não fornece provas de testes que não executou.
- A revisão da 015 só vale se o code review cobrir integralmente os inputs e o contrato do predecessor 014, com evidência rastreável; um parecer genérico não atende o gate.

## Fontes oficiais verificadas em 2026-11-20

- https://docs.github.com/en/github-models — GitHub Models retirado em 2026-07-30.
- https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli-in-actions — GitHub Copilot CLI via `GITHUB_TOKEN` e `copilot-requests: write`.
- https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference — `--model`, `--effort`, `--available-tools`, flags read-only.
- https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-programmatic-reference — formato JSONL e execução headless.
- https://docs.github.com/en/copilot/concepts/agent-capabilities/agent-powered-workflows-and-operations/copilot-cli-in-github-actions — faturamento por proprietário da organização.
- https://docs.github.com/en/actions/tutorials/authenticate-with-github_token — mínimos privilégios e token temporário.
