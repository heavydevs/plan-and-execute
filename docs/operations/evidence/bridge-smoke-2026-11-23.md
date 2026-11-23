# Evidência operacional — smoke das pontes PAE (2026-11-23)

- **Repositório:** `heavydevs/plan-and-execute`
- **Branch autorizada:** `checkpoint/plano1-estudo-provider-switch-20261028`
- **HEAD examinado antes deste registro:** `7265bd31a745d36a7eb411ea82401dd6c88d6769`
- **Objetivo:** comprovar o caminho de execução existente e identificar com precisão a ausência de caminho remoto ao Codespace; não validar a task 015 nem simular subprocessos.

## A. Execução direta do ChatGPT via GitHub → GitHub Actions → Claude Opus

- **Ação realmente invocada:** reexecução do job `auth-smoke` por `mcp__GitHub__rerun_workflow_job`, job anterior `137315769393`. GitHub respondeu `success=true`.
- **Execução:** [run `45056286464`, tentativa `3`](https://github.com/heavydevs/plan-and-execute/actions/runs/45056286464/attempts/3), job novo `137472281411`.
- **Checkout executado:** `0a592c9b8e57142c06778974c0d371fe439a1421` (SHA do workflow de smoke anterior; **não** é o HEAD corrente da branch).
- **Modelo observado:** evento init `claude-opus-5-5`, chamada real; `is_error=false`, consumo do modelo registrado no output da Action.
- **Sessão real no log da Action:** `abcfbb29-ed34-48b5-b1ca-56f37097615d`.
- **Validador:** `MODEL_SMOKE_OK: Claude Opus inference succeeded and model usage was present; no secret exposed`.
- **Status final do workflow:** `completed/success`. Não é parecer técnico e não é `015-receipt.json`.
- **Conclusão:** ponte ChatGPT → GitHub Actions → Claude **comprovada hoje** com autenticação existente, sem pedido de segredo ao usuário ou API key.

## B. Codespace → Claude Code CLI / Antigravity CLI (relato do usuário)

- Codespace informado: `https://legendary-space-computing-9659w4rr6pj5h7qxw.github.dev/`.
- Teste local executado pelo usuário: `claude instalado=True`, `agy instalado=True`, `Claude autenticado=True` com `Metodo=claude.ai`, `Claude execucao: PASSOU` e `Antigravity execucao: PASSOU`.
- **Evidência de segunda mão:** saída do terminal fornecida pelo usuário; esta sessão não executou esses dois processos no Codespace. Os modelos e prompts usados no smoke local não provam que Sonnet invocou AGY.
- A autenticação de `claude` no Codespace é distinta do OAuth GitHub Actions; a última está comprovada pelo run A.

## C. ChatGPT → Codespace → Sonnet → AGY (teste de ponta a ponta)

- **Status:** `NOT_CONNECTED / NOT_TESTED` (não aprovado).
- O conector GitHub disponível publica/consulta código e runs, mas não expõe terminal/SSH ou execução de comandos no Codespace do usuário.
- A tentativa de acesso HTTP ao domínio `github.dev` pelo container desta sessão falhou por `DNS resolution failed`; isso demonstra a limitação desta ferramenta, **não** que o Codespace esteja desligado.
- Os workflows de Claude existentes usam `runs-on: ubuntu-latest` (runners próprios do GitHub), não um runner autenticado no Codespace.
- Não há ponte remota autenticada/permitida comprovada que receba comandos versionados e devolva receipts dos processos `claude`/`agy` nesse Codespace.
- **Não** assumir que extensão VS Code ou CLI local concede API remota ao ChatGPT. Não conectar um runner full-access com OAuth pessoal diretamente ao repositório público.

## D. Efeito na task 015

- Última CI corrente consultada antes deste registro: [run `45101835480`](https://github.com/heavydevs/plan-and-execute/actions/runs/45101835480), SHA `7265bd31a745d36a7eb411ea82401dd6c88d6769`, bateria direcionada passou em Python 3.10 e 3.13; etapa `Original supervised validation gates` falhou.
- Este smoke não executou os gates `P1_TESTS_015`/`P1_015` do HEAD e **não** concede `completed` à task 015.
- Sem prova de revisão independente **dos hashes finais**, testes completos e recibo aceito, `015` permanece `pending` e nenhuma atividade da task 016 é autorizada.

## Próximo desbloqueio técnico

Criar **ponte isolada e auditável** com controlador privado (preferência: repositório privado separado), solicitação com ID e HEAD pinados, comandos allowlisted, proteção anti-replay, limite de duração e comprovantes compactos. O usuário terá de registrar/iniciar esse executor uma vez dentro do Codespace; a integração GitHub **não** instala serviço nele. Primeiro executar um smoke inofensivo Sonnet → AGY, comprovando ambos IDs/exit codes, antes de conceder mudanças no repositório. Não copiar as credenciais locais `~/.claude` ou `~/.gemini` ao GitHub.

**Resultado global do teste:** `A=PASS`, `B=USER_REPORTED_PASS`, `C=NOT_CONNECTED`, `D=PENDING`.
