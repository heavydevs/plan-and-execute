# Roteador — do estudo à entrega da task

**Novo comando `próximo` (2026-11-23):** ler [`AGENTS.md`](../../AGENTS.md), [`TODO.md`](../../TODO.md) e [protocolo ChatGPT → Claude](../../docs/operations/PAE_DUAL_AGENT_HANDOFF.md) **ANTES** de qualquer task. O ChatGPT não faz mais revisão final independente da 015: ela foi entregue ao Claude local, que deve aplicar a skill PAE, corrigir/testar e finalizar o gate. Enquanto a fase no TODO for `aguardando_validacao_claude` / `claude_validando_corrigindo` ou `bloqueada` sob Claude, **PARAR** sem executar 016. O antigo handoff de revisão por novo ChatGPT Web continua apenas como registro histórico.


**Passo zero:** leia [`../../guia_de_pesquisa_execucao_tasks.md`](../../guia_de_pesquisa_execucao_tasks.md). É ele que determina a primeira task de desenvolvimento pendente e o ciclo pesquisa → arquitetura → implementação → testes → revisão → entrega.

1. **Pesquisa/arquitetura inexistente ou obsoleta:** seguir o relatório por task em `docs/research/.../pesquisas-por-task/` e as regras completas do guia. Após publicar o estudo e vínculo, **continuar a implementar a mesma task**.
2. **Implementar/retomar:** ler [`PLAYBOOK.md`](PLAYBOOK.md), definição e contextos atribuídos; conferir escopo/hash/diff. Usar código e GH Actions sobre a branch exata.
3. **Testar/depurar/autocorrigir:** `taskctl.py doctor`, `taskctl.py run-checks --mode targeted|watcher`, e resource-map original. Qualquer reprovação obriga diagnóstico, reparo, testes focais, bateria completa e nova validação; aplicar [o ciclo de autocorreção do guia](../../guia_de_pesquisa_execucao_tasks.md#ciclo-obrigatório-de-autocorreção-após-reprovação) e [as instruções do Projeto](INSTRUCOES_PROJETO_CHATGPT.md). Não parar apenas com o status vermelho, nem substituir um gate por testes de harness.
4. **Revisão independente:** após o handoff, a responsabilidade passa ao **Claude local**; ler o protocolo atualizado e `CLAUDE.md`. O Claude usa a skill PAE, primeiro em sessão revisora sem edição, depois em contexto corretor se necessário e com nova revisão independente de hashes finais após patch. Os arquivos `REVIEW.md`, `GATE_REVISAO_015.md` e `review_dispatch.py` continuam válidos para os requisitos reais do gate, sem inventar sessão, tier ou aprovação.
5. **Arquitetura/segurança e alternativas:** ler [`ARCHITECTURE.md`](ARCHITECTURE.md) apenas quando exigido; não carregar pesquisas de todas as tasks no contexto.
6. **Conclusão:** exigir `015-receipt`, `015-outcome`, todos os checks e o `check_delivery.py` real; só então atualizar checkpoints/status do manifest e checklist de execução, commit/push e remoto.

Este arquivo é um roteador, não uma aprovação; a fonte de verdade continua sendo o manifest e os recibos reais. A versão copiável das instruções deste Projeto ChatGPT está em [`INSTRUCOES_PROJETO_CHATGPT.md`](INSTRUCOES_PROJETO_CHATGPT.md).

## Checkout fisico em ChatGPT sem rede externa

Se o container nao conseguir clonar o repositorio, usar o workflow [`.github/workflows/chatgpt-snapshot-export.yml`](../../.github/workflows/chatgpt-snapshot-export.yml): exporta um `git archive` do SHA exato como artefato. Baixar o ZIP via conector GitHub, importar em diretório temporario isolado com `python .ai-work/chatgpt-executor/import_snapshot.py --artifact /mnt/data/<zip> --destination /mnt/data/pae-checkout-<SHA> --sha <SHA>` (executando o importador de uma copia confiavel). Ver [SNAPSHOT_BRIDGE.md](SNAPSHOT_BRIDGE.md). A extracao recusa symlinks, traversal e SHA incorreto. **Snapshot e apenas copia de arquivos rastreados, sem `.git`; nao simula um clone.** Rodar testes nele e conferir reports, mas commits continuam pelo conector GitHub.

## Rota opcional Claude (somente se disponível e evidenciada)

Para rotas opcionais históricas da integração remota (sem substituir o Claude local responsável pelo gate), consultar [`docs/operations/CLAUDE_DELEGATION_MANUAL.md`](../../docs/operations/CLAUDE_DELEGATION_MANUAL.md) e `pae-claude-delegation.yml`. Não usar automaticamente, nem marcar sucesso sem evidência de modelo/sessão e gates. O Claude implementador não é revisor independente do seu próprio patch; o ChatGPT valida e integra. A task 015 continua a primeira pendente até passar `P1_015`.
