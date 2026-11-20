# Task 015 — parecer técnico independente, correções e gate ainda pendente

Data: 2026-11-20 (UTC). Branch: `checkpoint/plano1-estudo-provider-switch-20261028`. Ponto de partida: commit `476a8b86a38934adfad9501c7bc1027995a1385c`.

## Limite de independência

Este é o **primeiro parecer técnico produzido neste chat**, após leitura de `AGENTS.md`, `guia_de_pesquisa_execucao_tasks.md`, tarefa 015, contrato do predecessor 014, pesquisa preparada, fontes, arquitetura e testes, **antes** de consultar relatórios de revisores externos. O próprio chat também implementou as correções descritas abaixo. **Isto NÃO é o despacho de uma segunda sessão de IA nem uma aprovação independente exigida pelo gate**. Nenhum `session_id` de revisor externo é atribuído a este parecer.

## Achados reproduzidos contra o código inicial

1. **ALTA — exclusão fora do plano por symlink ancestral:** `skill/plan-and-execute/scripts/planctl.py:4782-4789` em `invalidate_stale_learnings`. Um manifesto adulterado com `file: "escape/victim.txt"` e `plan/escape -> outside` permitia `unlink()` do arquivo `outside/victim.txt`. Reprodução em diretório temporário: `victim.exists() == False` após a invalidação (que depois lançou `KeyError: title` ao tentar persistir o manifesto mínimo); o arquivo real de teste fora do plano foi excluído. Correção: restringir à rota canônica e recusar ancestrais simbólicos antes de remover.
2. **ALTA — proveniência removível sem rejeição:** `planctl.py:4660-4684,5174-5179,5268-5269`. Na versão 4, a ausência dos campos `trust_class`, `producer_task_id`, `consumer_task_ids`, `source_contract_digest`, `cited_file_digests`, `invalidation_rule`, `provenance_sha256` permitia `fresh: true`, `validate_plan: []` e `claim_task("002"): ACCEPTED`. Correção: campos e invariantes obrigatórios com falha fechada no contrato v4, inclusive consumidor exato.
3. **MÉDIA — referência explícita sem arquivo gera learning sem fingerprint:** `planctl.py:4595-4631,5064-5066`. `references: ["src/source_that_does_not_exist.py::SYMBOL"]` gerava `cited_file_digests: {}`, `fresh: true` e claim da tarefa consumidora aceito. Correção: referências a código `file::symbol`/`file#symbol` precisam resolver para fonte segura com digest na criação; a ausência da fingerprint invalida o learning. Referências textuais/comandos legados continuam permitidos.
4. **MÉDIA — evidência de hipótese atravessa symlink ancestral:** `planctl.py:5412-5446`. Após mover a pasta citada para fora do repositório e substituí-la por link simbólico, `check_hypothesis_freshness` continuava retornando `[]` com conteúdo idêntico; quando `repo_root` estava indisponível, ignorava a verificação. Correção: recusar ancestral simbólico e classificar raiz indisponível como evidência não verificável.

Todas as reproduções foram executadas somente em diretórios temporários. Nenhum arquivo de trabalho do usuário foi usado como vítima.

## Correções e hashes do conteúdo avaliado

| Caminho | Git blob antes | Git blob corrigido | SHA-256 corrigido |
| --- | --- | --- | --- |
| `skill/plan-and-execute/scripts/planctl.py` | `9e69d1115087db48af37a823a1915e865af7685b` | `c95ac903ec196a381de28f4deef54143e1b84bc3` | `5493de8bd606c6b936c6aacae3e162afc86c5fd08225c831f3fddf2e92b50de2` |
| `test/optimization/context_learning_self_test.py` | `f5f4df6bed86e0545467be972dd68bbd8ac3cc0c` | `735cc8aa6eaa8900e45ecf5bba95971d02a9619f` | `a3c1d57d219ec9b357e4eaf198c6ba9ec32f21bebfcc07af165b51bb0764c8fe` |
| `skill/plan-and-execute/scripts/artifact_contract.py` | `48c2b06f3a1832134f1447170d26c48fb4eaa604` | inalterado | `3af9ebb88b3f6c4e377df7e032246cd5eee5d481c234d779314d98bc5fe76aea` |
| `skill/plan-and-execute/scripts/runner_contract.py` | `c13fa8da09a6470fa33eeedf405245db1ae0c7af` | inalterado | `c7bab30e4c6a5a09a244481ee2fdf1f8e06ec8e7512740b743680e904dd98cf5` |
| `skill/plan-and-execute/references/EXECUTION_CONTEXT.md` | `2d879ea9fd8d9bee29594e952553de9fc45fb6fb` | inalterado | `ca9878dbbd42a0da9a16169112c0cd58e90aeea816135e990f5390bfde087396` |
| `skill/plan-and-execute/references/TOKEN_EFFICIENCY.md` | `d7b8865b2f33293f45a10fb18fb834493fe2fc49` | inalterado | `2f7107c3e620e1629e4fddeab4247ee43bc215acc0b03c61683966d717a9ad08` |

Hash de arquivo refere-se ao conteúdo exato testado na cópia de snapshot. Não representa identidade de uma sessão de revisor.

## Testes executados depois das correções

Snapshot de entrada: exportação por GitHub Actions do commit `be9965a4f107739be9c5a2ff84d5939ab1df088a` (run [44811354990](https://github.com/heavydevs/plan-and-execute/actions/runs/44811354990)); os Git blobs dos seis arquivos inspecionados foram comparados com o HEAD inicial e coincidiram. A cópia restaurada não possui `.git` e não deve ser confundida com checkout de branch.

Ambiente: Python 3.13.5; todos os sete comandos de `TASK_INPUTS.json` da 015 foram executados **após** as correções. Resultados: **7/7 exit 0**.

| # | Comando | Exit | SHA-256 do log local |
| --- | --- | --- | --- |
| 1 | `python test/optimization/context_learning_self_test.py` | 0 | `27f8763cca418a122e98eafa14d246ba755cdbaf1a8c531a5724f01c15756539` |
| 2 | `python skill/plan-and-execute/scripts/context_self_test.py` | 0 | `a24506e5c5a5c6046a3090162f436400c4ce57f2caa318635eef657405a4a96e` |
| 3 | `python skill/plan-and-execute/scripts/task_memory_self_test.py` | 0 | `6a01cde9cb183f9756c33bc27c052ecaf61a0dbe54dfc01e3057d09d3e1cdcfe` |
| 4 | `python skill/plan-and-execute/scripts/artifact_concision_self_test.py` | 0 | `007b89b8c770af2c76463e5668ec3bd53b5528e4333fc3d0763e6fcfb73fa2d1` |
| 5 | `python skill/plan-and-execute/scripts/progress_runner_self_test.py` | 0 | `f1d717fb7273e376a492c47f850be091f59d8e4a9267b2166dd1cc6a10738aad` |
| 6 | `python skill/plan-and-execute/scripts/pattern_runner_self_test.py` | 0 | `bb94e76a3fd37c46fb13d008197055e4f64f431e52dc465f811a2773688b86f3` |
| 7 | `python skill/plan-and-execute/scripts/self_test.py` | 0 | `cfdf647572d57a3c5fc330adc84b3337e89b9edcfdbacfa97c94a59b00f3a364` |

Sumário JSON local (`targeted-results.json`) SHA-256 `cce804a91726577cd2a59f3bc33e98ff1b766b44bbef0050f2925129b3bef865`.

`resource_watch.py run --validation P1_TESTS_015`: observados `PROGRESS done=7 total=7`, `test_exit=0`, `health=healthy`; SHA-256 do log `b1676cb8cfe6fe37ce7e8a2f8b0b9225f9df6482408964ae2060ae8801ba2d42`. `resource_watch.py run --validation P1_015`: `exit=1`, mensagem `DELIVERY REJECTED: Missing evidence: .../015-receipt.json`; log SHA-256 `3f53188fe654698c636ac1930e3ef5043e2e3ad1205675fec215bbad04e16502`. Estes logs foram observados em execução local; ainda não constituem artefatos do GitHub Actions do commit final.

O dispatcher oficial `review_dispatch.py --repo-root . --task 015` retornou `exit=2` / `NO_REVIEW task=015 dispatch=2: no provider could review (codex:missing_cli, claude:missing_cli)`, log SHA-256 `abb338a3262609d8038c960e84427b9536d259497a0c8e41fe7965fa344ce430`. Tentativa Copilot no [run 44806119525](https://github.com/heavydevs/plan-and-execute/actions/runs/44806119525) terminou em bloqueio de política/entitlement, sem aprovação. Resultado de outro modelo em commit anterior não valida este novo diff.

## Decisão de entrega e próximos gates — NÃO APROVADO

- **Estado correto da task 015: pendente/bloqueada no requisito de revisão externa.** Este relatório não constitui `015-receipt.json`, `015-checks.json` final validado nem `DISPATCH` aprovado.
- Executar um revisor verdadeiramente independente em sessão nova (modelo máximo exigido pelo contrato) contra **o commit definitivo após as correções**, com recibo de session ID, route, native effort, despachos e hashes de todas as fontes e artefatos da 014. Registrar findings reais; qualquer achado high/critical exige correção e nova sessão sobre o novo SHA.
- Registrar os sete checks com logs e `input_fingerprint` do commit final; criar `015-checks.json`, `015-outcome.md`, `015-receipt.json` apenas após atendimento real dos critérios. Passar `P1_015`/`check_delivery.py`, então atualizar manifest/projeções via `planctl`.
- **Não executar a task 016.** Nenhuma aprovação, teste ou sessão externa é presumido.

