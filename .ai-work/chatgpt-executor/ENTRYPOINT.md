# Roteador — do estudo à entrega da task

**Passo zero:** leia [`../../guia_de_pesquisa_execucao_tasks.md`](../../guia_de_pesquisa_execucao_tasks.md). É ele que determina a primeira task de desenvolvimento pendente e o ciclo pesquisa → arquitetura → implementação → testes → revisão → entrega.

1. **Pesquisa/arquitetura inexistente ou obsoleta:** seguir o relatório por task em `docs/research/.../pesquisas-por-task/` e as regras completas do guia. Após publicar o estudo e vínculo, **continuar a implementar a mesma task**.
2. **Implementar/retomar:** ler [`PLAYBOOK.md`](PLAYBOOK.md), definição e contextos atribuídos; conferir escopo/hash/diff. Usar código e GH Actions sobre a branch exata.
3. **Testar/depurar/autocorrigir:** `taskctl.py doctor`, `taskctl.py run-checks --mode targeted|watcher`, e resource-map original. Qualquer reprovação obriga diagnóstico, reparo, testes focais, bateria completa e nova validação; aplicar [o ciclo de autocorreção do guia](../../guia_de_pesquisa_execucao_tasks.md#ciclo-obrigatório-de-autocorreção-após-reprovação) e [as instruções do Projeto](INSTRUCOES_PROJETO_CHATGPT.md). Não parar apenas com o status vermelho, nem substituir um gate por testes de harness.
4. **Revisão independente:** ler [`REVIEW.md`](REVIEW.md) e [`GATE_REVISAO_015.md`](GATE_REVISAO_015.md). Priorizar `review_dispatch.py` autenticado. A rota Copilot CLI foi bloqueada pela politica/licenca. Para executar **uma revisao de IA realmente distinta, sem Codex Cloud ou credenciais**, usar [`OFFLINE_REVIEW.md`](OFFLINE_REVIEW.md): GGUF de pesos abertos num processo isolado do GitHub Actions, com hashes e findings. Essa rota e **suplementar**, nao equivale a max-tier nem passa automaticamente `P1_015`. Sem o contrato final autenticado, manter a task pendente.
5. **Arquitetura/segurança e alternativas:** ler [`ARCHITECTURE.md`](ARCHITECTURE.md) apenas quando exigido; não carregar pesquisas de todas as tasks no contexto.
6. **Conclusão:** exigir `015-receipt`, `015-outcome`, todos os checks e o `check_delivery.py` real; só então atualizar checkpoints/status do manifest e checklist de execução, commit/push e remoto.

Este arquivo é um roteador, não uma aprovação; a fonte de verdade continua sendo o manifest e os recibos reais. A versão copiável das instruções deste Projeto ChatGPT está em [`INSTRUCOES_PROJETO_CHATGPT.md`](INSTRUCOES_PROJETO_CHATGPT.md).

## Checkout fisico em ChatGPT sem rede externa

Se o container nao conseguir clonar o repositorio, usar o workflow [`.github/workflows/chatgpt-snapshot-export.yml`](../../.github/workflows/chatgpt-snapshot-export.yml): exporta um `git archive` do SHA exato como artefato. Baixar o ZIP via conector GitHub, importar em diretório temporario isolado com `python .ai-work/chatgpt-executor/import_snapshot.py --artifact /mnt/data/<zip> --destination /mnt/data/pae-checkout-<SHA> --sha <SHA>` (executando o importador de uma copia confiavel). Ver [SNAPSHOT_BRIDGE.md](SNAPSHOT_BRIDGE.md). A extracao recusa symlinks, traversal e SHA incorreto. **Snapshot e apenas copia de arquivos rastreados, sem `.git`; nao simula um clone.** Rodar testes nele e conferir reports, mas commits continuam pelo conector GitHub.
