# Task 015 — ChatGPT executor: measured delivery state

**Date:** 2026-11-20. **Branch:** `checkpoint/plano1-estudo-provider-switch-20261028`.

## Results (executed, not simulated)

- Implementation being validated: review/correct task **015** for completed **014**; task 015 remains `pending`, including S002–S006.
- Source repair commit: [7769564](https://github.com/heavydevs/plan-and-execute/commit/7769564ccbda6c5821a7813f7f378c54a30300b6). Added source-file hash checks for learnings including retries, `#symbol` anchors, and a regression scenario.
- Chat execution harness and docs: [a974df7](https://github.com/heavydevs/plan-and-execute/commit/a974df71940aff65d10dac4caa528d7c244af451), followed by map reconciliation fixes.
- Actual CI: [GitHub Actions run 44800650085](https://github.com/heavydevs/plan-and-execute/actions/runs/44800650085), tested commit `e4f274243caf706ea461ae1659a3dd6a86564060`, on **Python 3.10** and **Python 3.13**.
- Harness security self-tests: **4/4 passed** in both environments (scope limited to harness).
- Declared direct task checks: **7/7 passed** in both environments. These checks are diagnostic, not a replacement for supervised acceptance.
- Resource map inventory: original watcher refused execution due stale source snapshot. Reconciled with a reviewed explicit set of 36 test/build/CI paths; no new service dependency was introduced. Generated SHA-256 snapshot digest `f300bb7846c785c43a35f36487539704386c078490083cb4195d8412b2e7b07f` over **71 inputs**; the map and index were exported with CI artifacts and are committed from exact bytes.
- Original monitored `P1_TESTS_015`: **passed** in Python 3.13 (exit 0, all seven declared checks); no external resources required. Python 3.10 evidence should be checked separately in its artifact.
- Original monitored `P1_015`: **rejected** (exit 1): `Missing evidence: docs/research/20261028-skill-optimization/implementation/015-receipt.json`. That is the intended delivery gate, not a failing unit test.
- Real independent review `review_dispatch.py --task 015`: **not executed**. No authenticated Codex/Claude CLI was available locally or on the GitHub runner, no provider/model/session evidence exists. Prepared `brief-1.md` is not a reviewer result.

## Gate and permitted next work

**Do not mark 015 completed or fabricate an implementation receipt**. The next executor must obtain a genuinely independent reviewer invocation with recorded model, effort, session and final input hashes; repair any blocking findings in the declared 015 write scope; repeat targeted and watcher validation on the **final** reviewed SHA; then create authentic `015-receipt.json` / `015-outcome.md` and pass the original delivery gate. A same-session ChatGPT static review or a reusable JSON packet is not a fresh external review.

### Method and limitations

Source/command hashes and detailed logs are available as the version-pinned CI artifacts. No claimed prompt-cache or paid-model benchmark, native Windows test, or external model consumption. The local container lacked GitHub DNS, so tests were run in actual GitHub-hosted Linux checkouts of the pushed commit. `taskctl.py` and `mapctl.py` do not edit the plan manifest. Future work should prefer deterministic checks before additional paid model calls.

## Verificação mais recente — 2026-11-20, execução 44801488387

- [GitHub Actions — evidência real da branch](https://github.com/heavydevs/plan-and-execute/actions/runs/44801488387), SHA de entrada `42e89871cbf10be07b3c850abc562cc18414d042`, Python **3.10** e **3.13**.
- Testes herméticos do executor: **4/4 aprovados** em ambas as versões; testes offline do adaptador OpenAI Responses API: **aprovados** em ambas, **sem** invocação de modelo autenticado.
- Checks direcionados exigidos por `TASK_INPUTS.json[015]`: **7/7 aprovados** em ambas as versões, sobre o checkout correto.
- Reconciliação explícita do mapa de recursos: aprovada; `P1_TESTS_015` supervisionado pelo monitor original: **aprovado** em ambas as versões (exit 0, sete casos de teste). Snapshot de 71 entradas, digest `6988df40159932b576b72ec35e73be0ddf65a10faeef38d0a15d13f73c3a158d`.
- `P1_015` (gate final de entrega): **não aprovado**, por ausência do arquivo `docs/research/20261028-skill-optimization/implementation/015-receipt.json`. A revisão independente real por modelo externo não ocorreu; não há sessão/modelo/effort autenticamente produzidos. **Não considerar o status geral de CI como aprovação da task.**
- Evidências completas nos artefatos `task-015-checks-py3.10` e `task-015-checks-py3.13` da execução acima. O mapa e índice foram copiados dos artefatos para a branch sem alterar o conjunto de dependências validado.
- O adaptador `.ai-work/chatgpt-executor/api_review.py` é opção genuína para ambiente com `OPENAI_API_KEY` configurada; não foi autorizado/autenticado aqui, e sua saída não substitui automaticamente o `review_dispatch.py` exigido no plano.

**Decisão:** manter task **015** e checkpoints restantes pendentes. É necessário executar revisão externa genuína sobre os hashes finais, corrigir achados bloqueadores e passar o gate original antes de gerar recibo de implementação.

## Pesquisa → execução → revisão externa — 20/11/2026

- O antigo `guia_de_pesquisa_tasks.md` foi substituído por `guia_de_pesquisa_execucao_tasks.md`, com **duas checklists por ID**: pesquisa/arquitetura e execução/review/gate. As pesquisas 015–019 seguem concluídas; a execução 015 continua **pendente**. Os 118 IDs foram preservados.
- `AGENTS.md` e `ENTRYPOINT.md` agora encaminham ao fluxo completo e ao `INSTRUCOES_PROJETO_CHATGPT.md`. Essas instruções estão versionadas, mas a configuração particular do Projeto no ChatGPT **não foi modificada pelo conector**.
- Arquitetura e implementação do gate alternativo: `.ai-work/chatgpt-executor/copilot_review.py`, `GATE_REVISAO_015.md`, `.github/workflows/chatgpt-independent-review.yml`. Verifica SHA, readset, sessão/modelo/effort e findings; usa GitHub Actions `GITHUB_TOKEN` com `copilot-requests: write` e `contents: read`, um request por invocação; não assume codex CLI instalado.
- Execução autenticada tentada em [GitHub Actions 44805796561](https://github.com/heavydevs/plan-and-execute/actions/runs/44805796561), commit `dfc326bcdfeaee6f7e726fa6b58e08b89cf4977e`: CLI 1.0.114 instalada, unit tests e dry-run passaram, mas chamada ao provedor foi recusada e **não houve evidência válida de revisão**.
- Segunda tentativa limitada e diagnóstica: [GitHub Actions 44806119525](https://github.com/heavydevs/plan-and-execute/actions/runs/44806119525), commit `954a301e42d79fe88ab5b45db3c62c13f6d0abcf`: erro classificado `copilot_policy_or_entitlement`. Isso indica problema de política/direito de uso (ou permissão do token/modelo) do Copilot na organização. **Não repetir chamadas pagas sem resolver a autorização do fornecedor.**
- O workflow de testes da mesma revisão verificou **7/7 checks direcionados**, os tests offline do harness, adaptador API e Copilot. Detectou um novo CI input `.github/workflows/chatgpt-independent-review.yml` não reconhecido pelo mapa; `mapctl.py` foi atualizado para contemplar **exatamente esse arquivo auditado**. Isso é um bloqueio de inventário, não falha de teste funcional.
- **Gate final `P1_015`: pendente**, pois falta review independente real e receipt v2. Nenhum `015-receipt.json`, veredito, session ID ou status `completed` foi falsificado ou produzido.
- Para destravar: o administrador da organização GitHub deve conferir **Settings → Copilot → Policies → Copilot CLI → Allow use of Copilot CLI billed to the organization** e garantir autorização/entitlement do modelo; então reexecutar um request único, conferir modelo/sessão/hashes reais, persistir evidências, retestar sobre SHA final e passar `check_delivery.py`. Documentação oficial: https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli-in-actions.
