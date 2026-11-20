# Roteador — do estudo à entrega da task

**Passo zero:** leia [`../../guia_de_pesquisa_execucao_tasks.md`](../../guia_de_pesquisa_execucao_tasks.md). É ele que determina a primeira task de desenvolvimento pendente e o ciclo pesquisa → arquitetura → implementação → testes → revisão → entrega.

1. **Pesquisa/arquitetura inexistente ou obsoleta:** seguir o relatório por task em `docs/research/.../pesquisas-por-task/` e as regras completas do guia. Após publicar o estudo e vínculo, **continuar a implementar a mesma task**.
2. **Implementar/retomar:** ler [`PLAYBOOK.md`](PLAYBOOK.md), definição e contextos atribuídos; conferir escopo/hash/diff. Usar código e GH Actions sobre a branch exata.
3. **Testar/depurar:** `taskctl.py doctor`, `taskctl.py run-checks --mode targeted|watcher`, e resource-map original. Nunca substituir um gate por testes de harness.
4. **Revisão independente:** ler [`REVIEW.md`](REVIEW.md) e [`GATE_REVISAO_015.md`](GATE_REVISAO_015.md). Priorizar `review_dispatch.py` autenticado. Sem Codex/Claude CLI, alternativa autorizada é GitHub Copilot CLI com modelo Opus e `GITHUB_TOKEN` de Actions, **uma invocação real**. Rejeitar qualquer resultado sem sessão/modelo/effort verificados; sem créditos ou permissão, manter bloqueado.
5. **Arquitetura/segurança e alternativas:** ler [`ARCHITECTURE.md`](ARCHITECTURE.md) apenas quando exigido; não carregar pesquisas de todas as tasks no contexto.
6. **Conclusão:** exigir `015-receipt`, `015-outcome`, todos os checks e o `check_delivery.py` real; só então atualizar checkpoints/status do manifest e checklist de execução, commit/push e remoto.

Este arquivo é um roteador, não uma aprovação; a fonte de verdade continua sendo o manifest e os recibos reais. A versão copiável das instruções deste Projeto ChatGPT está em [`INSTRUCOES_PROJETO_CHATGPT.md`](INSTRUCOES_PROJETO_CHATGPT.md).
