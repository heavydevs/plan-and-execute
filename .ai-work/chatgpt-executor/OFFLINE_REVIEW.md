# Revisão independente sem Codex Cloud — alternativa executável

A revisão anterior via Copilot CLI foi bloqueada por `copilot_policy_or_entitlement`. O checkout temporário sozinho resolve os **testes**, mas não prova revisão independente. Este mecanismo executa em GitHub Actions (VM separada) um **modelo de pesos abertos real**, com processo e contexto distintos do ChatGPT, **sem Codex Cloud, Copilot, chave de API ou cobrança de inferência de terceiro**.

## Arquitetura e limites

- GitHub Actions fornece checkout exato e limpo, 4 CPUs / 16 GB RAM para repositórios públicos (documentação de runners). O container do ChatGPT não necessita de conexão de rede externa. Um novo pedido no repositório aciona somente uma tentativa controlada.
- Runtime `ggml-org/llama.cpp b10786 (nightly binary, SHA-256 verificado)` CPU, tarball 18,3 MB **verificado por SHA-256**; execução via `llama-server` e loopback em servidor local. Sem interfaces externas ou acesso à escrita do GitHub.
- PoC utiliza `Qwen2.5-Coder-1.5B-Instruct-GGUF` Q4_K_M (aprox. 1,12 GB) para verificar end-to-end. Opcional posterior é 7B Q4_K_M (~4,68 GB), com maior custo de CPU e melhor capacidade relativa; requer benchmark próprio. A versão dos pesos e SHA-256 realmente baixados são registrados. O modelo 1.5B **não é equivalente a um max-tier Opus/Codex**.
- `offline_review.py` determina conjunto completo de hashes e extrai *trechos literais numerados* de funções de risco específicas da 015; a saída registra `symbol_coverage` com `complete` (a inspeção de partes não é descrita como revisão completa). Modelo recebe trechos como dados não confiáveis, contrato/aceite, e devolve JSON estruturado.
- O resultado só é aceito como *evidência suplementar de IA distinta* após verificação de JSON, linhas de finding, hash de fonte antes/depois, versão/binário de inferência e modelo, ID da execução e logs autênticos. Resposta incompleta, download falho, mudança de input, saída que contradiz findings ou conclusão genérica: falha fechada.
- **O validador original `check_delivery.py` não foi modificado**. Ele exige reviewer real de `max` com evidência de dispatch; o modelo local menor não satisfaz esse contrato nem deve ser rotulado como `max`. Uma eventual arquitetura de aprovação alternativa exige revisão transparente do contrato e testes adversariais adicionais, nunca troca de nomes para fingir `review_dispatch`.

## Execução

1. `python .ai-work/chatgpt-executor/tests/test_offline_review.py` verifica integridade e falsificação sem baixar pesos.
2. `python .ai-work/chatgpt-executor/offline_review.py --dry-run` prepara hashing e trechos no **checkout exato**.
3. O workflow `.github/workflows/chatgpt-offline-review.yml` executa a revisão real após um request em `.ai-work/chatgpt-executor/requests/015-offline.json` ou `workflow_dispatch`. Exporta artefatos por SHA; não produz approval se um passo falhar.
4. Conferir saída e comparar hashes com o commit final. Em findings críticos, corrigir e repetir no **novo** SHA. Rodar `P1_TESTS_015` e `P1_015` supervisionados; falta de recibo de max real continua pendente.

## Fontes

- GitHub Actions runner CPU/RAM: https://docs.github.com/en/actions/reference/runners/github-hosted-runners
- llama.cpp binários e releases: https://github.com/ggml-org/llama.cpp/releases/tag/b10786
- llama.cpp servidor: https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md
- Qwen GGUF original: https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF
- 7B GGUF original: https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct-GGUF
- GitHub Copilot code review alternate API: https://docs.github.com/en/rest/pulls/copilot-code-review
- Problemas anteriores: `.ai-work/chatgpt-executor/STATUS-015.md`.

**Retificacao da prova:** a primeira execucao [44809741623](https://github.com/heavydevs/plan-and-execute/actions/runs/44809741623) detectou HTTP 404 no download de `v0.9.0`: a serie semver nao publicava o binario. A rota foi corrigida para o nightly `b10786`, cujo binario e hash sao atestados pelo proprio projeto: https://github.com/ggml-org/llama.cpp/attestations/44990064. Nenhuma revisao de IA foi concluida na primeira tentativa.

**Diagnostico do schema-constrained (run 44810572125):** no runner `b10786` o modelo retornou uma mensagem de 2.386 caracteres com `finish=stop`, mas que nao era JSON parseavel. O erro foi recusado e sua assinatura gravada, sem inventar findings. Nova configuracao segue exatamente a sintaxe de `response_format.json_schema.schema` descrita em `llama.cpp/grammars/README.md`, e fixa o SHA-256 do GGUF baixado. Se o modelo continuar sem produzir JSON valido, classificar como *capacidade insuficiente*, nao aprovar ou converter automaticamente a prosa em recibo.
