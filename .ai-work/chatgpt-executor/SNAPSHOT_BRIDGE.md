# Ponte de snapshot — executar testes com repositório completo no ChatGPT

O container de código do ChatGPT pode ter Python/Node mas não resolver `github.com`. Em vez de baixar arquivos individualmente, o GitHub Actions gera um `git archive` do SHA exato da branch e salva um artefato ZIP contendo somente `pae-snapshot.tar.gz` e `pae-snapshot.json`.

**Procedimento:**

1. O workflow [`.github/workflows/chatgpt-snapshot-export.yml`](../../.github/workflows/chatgpt-snapshot-export.yml) executa em uma VM do GitHub sobre o commit publicado. Não tem acesso a segredos nem usa token gravado; `contents: read` apenas.
2. Consultar o run, `head_sha` e artifact id pelo conector GitHub; usar `mcp__GitHub__download_workflow_artifact` para disponibilizar o ZIP em `/mnt/data/`. Usar o *caminho real* retornado pela ferramenta.
3. No container ChatGPT, executar o importador confiável, fora da pasta ainda não verificada:

   ```bash
   python /mnt/data/pae-work/.ai-work/chatgpt-executor/import_snapshot.py \
     --artifact /mnt/data/pae-checkout-<sha>.zip \
     --destination /mnt/data/pae-checkout-<sha> \
     --sha <sha-40-hex>
   ```

4. O importador confere assinatura de conteúdo do artefato (`SHA-256` no manifesto + origem commit), sem confiar na extensão ou título. Rejeita symlink/hardlink, path traversal, nomes repetidos, zip com entradas extras, arquivo grande, destino preexistente. A extração salva `.pae-checkout-snapshot.json` com a proveniência.
5. Executar testes de Python/Node dentro do diretório **cópia**, registrando comandos e saída. O arquivo `.git` não faz parte do `git archive`; testes que exigirem Git/rede/container Docker permanecem em Actions. Não usar a pasta temporária para afirmar mudança/commit remoto; publicar patches pelo conector GitHub com CAS.
6. Uma segunda sessão de IA não é automaticamente criada ao materializar a pasta. Revisão independente requer um modelo realmente separado (por exemplo `OFFLINE_REVIEW.md` para pesos abertos, ou dispatcher max original); **não** aprovar a 015 por autorrevisão do mesmo ChatGPT.

Este fluxo permite reproduzir todos os arquivos rastreados de uma vez sem operações repetidas de blob. O teste de segurança do importador fica em `tests/test_import_snapshot.py`.

## Disparo autônomo e procedência

O mecanismo agora aceita o gatilho por **commit do arquivo** `.ai-work/chatgpt-executor/requests/snapshot.json` na branch indicada, além da alteração do workflow. Assim, ChatGPT pode criar o request pelo conector GitHub e aguardar o artefato sem depender da interface manual `workflow_dispatch`. Sempre conferir que o `head_sha` real retornado pela API Actions coincide com o campo `head_sha` de `pae-snapshot.json` **e** com o SHA exigido no importador. O hash embutido no ZIP detecta corrupção interna, mas **nao autentica sozinho o remetente**: um ZIP inventado com checksum autorreferenciado ainda passaria. A garantia de origem vem da API autenticada do GitHub Actions e da identidade do run verificada separadamente.
