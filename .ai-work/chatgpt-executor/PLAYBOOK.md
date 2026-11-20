# One-task playbook for ChatGPT (no native Codex/Claude requirement for edits)

## Preconditions

1. Use the connected GitHub app to read the exact branch ref and identify **the first pending/in-progress task** in the authoritative manifest. Inspect its dependencies, Sxxx checkpoints, permitted write scope, prepared architecture and `TASK_INPUTS.json` record. Do not advance past the selected task.
2. `python .ai-work/chatgpt-executor/taskctl.py doctor` explains available tools. A complete checkout is required for local tests; never run a task against a stale bundled skill copy. With no GitHub network in the container, write the patch through GitHub `create_blob` -> `create_tree(base_tree)` -> `create_commit(parent)` -> `update_ref(expected_sha, force=false)`; this is optimistic concurrency, not local checkout.
3. Preserve a hash-bound snapshot of all actual inputs and identify scope. Execute GitHub remote tests on the **commit SHA of that snapshot** via `.github/workflows/chatgpt-executor.yml` on the named checkpoint branch; check Action run SHA, conclusion and logs. If the host has neither shell source nor Actions, record `environment_unavailable`, not success.

## Local tool commands

```bash
python .ai-work/chatgpt-executor/taskctl.py self-test
python .ai-work/chatgpt-executor/taskctl.py status --task 015
python .ai-work/chatgpt-executor/taskctl.py review-packet --task 015
python .ai-work/chatgpt-executor/taskctl.py run-checks --task 015 --mode targeted
python .ai-work/chatgpt-executor/taskctl.py run-checks --task 015 --mode watcher
python .ai-work/chatgpt-executor/taskctl.py dispatch-review --task 015
python .ai-work/chatgpt-executor/taskctl.py gate --task 015 --run-evidence .ai-work/chatgpt-executor/runs/<id>/result.json
```

- `targeted` executes only the declared `TASK_INPUTS.json` commands. Results are diagnostic, not final acceptance.
- `watcher` executes both `P1_TESTS_015` and `P1_015` through the original resource watcher and map. This is the **required gate**; never silently fall back to direct tests if resource-map checks fail.
- Results go to `runs/` (gitignored). Failed tests must remain visible. Do not suppress errors to keep the workflow green.
- `review-packet` snapshots exact paths/hashes for a separate reviewer; it **does not approve** anything.
- `dispatch-review` calls the existing **foreground** independent dispatcher when a compatible authenticated CLI exists; never invent provider/session/hash and never run it in background.
- The `gate` command is deliberately fail-closed and does not write the plan manifest or pretend to replace `check_delivery.py`.

## Implementation and correction

1. Use the existing approved research report as a starting architecture, not proof of working code. Edit the narrowest files in the selected task's write scope; create a regression test for every verified blocking defect. Validate code quality, security (injection, filesystem paths, process ownership) and performance.
2. Run targeted tests to isolate failures, aggregate failures, fix locally, then run the full declared watcher validations. Save actual logs, original commands, exit codes, hashes and OS versions. Do not claim coverage across absent platforms.
3. For an independent review task such as 015, **do not** mark `S002` complete unless `review_dispatch.py` produced verifiable evidence for the same final SHA. Any source mutation after approval requires another review. Fix blocking findings inside the write scope; out-of-scope changes require a dependency/blocker.
4. Only after the original acceptance checks and independent reviewer pass, create the receipt/outcome using the original schema, validate them with the repo's delivery gate, advance task checkpoints through `planctl` and commit/push. If a gate is unavailable, publish a clearly labeled partial repair and leave status pending.
5. For GitHub Actions observations, compare the workflow `head_sha` to your pushed commit. A success from another commit or a CI runner without the expected tests is invalid evidence.

## Token cost

Read a task definition, brief assigned files, one current failure log tail and the minimal changed source. Deterministic code handles hashing and triage. Never replay all previous worker conversations. Stop after verified acceptance; keep local run history as artifacts rather than prompting with full logs.

## Audited resource-map reconciliation, 2026-11-20

The original map was observed stale on GitHub Actions because of 36 specific changed test/build/CI inputs, not because a required test failed. `.ai-work/chatgpt-executor/mapctl.py` imports the original `service_map.py`, requires the original index, checks only the explicitly inspected 36 changed paths and confirms both 015 validation IDs before restamping in a temporary GitHub Actions checkout. Unknown paths or malformed inventories abort; no blanket `stamp` is allowed. The CI artifact includes the updated map and index so their **exact** content can be published through GitHub CAS; the repository map is not considered reconciled until that content is committed. This procedure is independent of, and never substitutes for, an external model review.

## Optional API review bridge

`python .ai-work/chatgpt-executor/api_review.py --task 015 --dry-run` only verifies prepared source scope and cost/size envelope. A real invocation requires an authorized `OPENAI_API_KEY` environment variable; it contacts the OpenAI Responses API, may incur charges, and records real response/session/model/usage and exact source SHA-256. **Do not** convert that JSON into `review_dispatch` receipt metadata or mark 015 done; the original delivery contract remains authoritative unless properly revised.

## Regra de ciclo completo (2026-11-20)

O guia em `guia_de_pesquisa_execucao_tasks.md` substitui o fluxo antigo que parava após pesquisa. Escolher sempre a primeira task **de desenvolvimento** não concluída. Se pesquisa existe, retomá-la sem repetir estudo; se falta, pesquisar, publicar arquitetura, e **executar imediatamente a mesma task**. A 015 tem pesquisa concluída; a 020 só pode começar após as tasks anteriores passarem seus gates. Não converter sucesso de testes direcionados em status completed sem review.

## Rota autenticada alternativa para o gate 015

Ler `GATE_REVISAO_015.md`. A alternativa é `.github/workflows/chatgpt-independent-review.yml` → `copilot_review.py` → sessão externa real com `claude-opus-5.5`, esforço `xhigh`, ferramentas estritamente de leitura e evidência hash-bound para o gate original. O workflow é ativado somente pelo request explícito; não é um substituto de modelo simulado e pode consumir créditos. Importar artefatos/receipts por commit CAS somente após validar provedor, sessão, hashes, findings, testes e gate. Falha de autenticação/billing deixa o plano pendente.

## Copia fisica do checkout por artefato

O fallback de clone bloqueado pelo DNS agora e `SNAPSHOT_BRIDGE.md`, nao apenas leitura de blobs individuais. O GitHub Actions gera um archive completo com SHA do commit. `import_snapshot.py` verifica o hash do archive, o sha da origem, o repo e os nomes/simbolic links antes da extracao num diretorio novo. Ele recusa overwrite e caminhos invalidos. A copia tem os fontes suficientes para testes Python/Node normais, sem historico Git; comandos que exigem checkout git devem continuar no GitHub Actions. Os resultados de testes feitos no container local sao separados de CI e so valem para o mesmo snapshot.
