# Plano único de implementação - pesquisas preparadas

Data: 28/10/2026. Base do código: versão 0.11.0.

**A pesquisa dos 32 tópicos foi preparada, e o plano foi convertido para implementação. Não há mais uma etapa de gerar outro plano.**

## Entrega

| Item | Resultado |
|---|---|
| Relatórios individuais | 32, cada um em Markdown e JSON. |
| Fontes registradas | 58, com URL, data, achado e limite de consulta. |
| Tarefas de pesquisa restantes | 0. |
| TODOs do plano único | 86, todos pendentes de implementação, correção ou revisão. |
| Subtarefas internas | 571, regeneradas pelo controlador nativo. |
| Revisões independentes | 43 exigências preservadas; nenhuma simulada. |
| Criação do Plano 2 | Removida do fluxo. |

Os relatórios distinguem observações do código, informação externa, recomendações de engenharia, alternativas, custos, migração, testes propostos e limites. A leitura de trechos públicos de livros não é apresentada como leitura integral. Não foram medidos custos reais, qualidade de modelos ou cotas desta conta.

## Como o plano foi alterado

As antigas tarefas 006, 008, 010 até 068 agora leem seu relatório e implementam suas orientações. A tarefa seguinte faz revisão independente do código e correções. As tarefas 070-081 preservam a implementação detalhada da troca de fornecedor. A tarefa 068 cria as fixtures de contrato desse mecanismo; não duplica as alterações operacionais das tarefas seguintes.

As tarefas 082-085, antes ligadas a outro plano, passaram a tratar de integração, regressões, empacotamento e prontidão da entrega. A tarefa 086 mantém a revisão final da skill inteira. O preflight inicial é determinístico: não existe mais uma revisão externa inicial bloqueando toda a preparação.

Cada tarefa recebeu entradas delimitadas, testes declarados, evidências de aceite e dependências de escrita. Nenhuma precisa carregar todos os relatórios. Uma revisão limpa não exige inventar alterações no código; invariantes já atendidas podem ser preservadas com justificativa e testes.

## Onde encontrar

- `docs/research/20261028-skill-optimization/prepared-research/INDEX.md`: índice das pesquisas.
- `docs/research/20261028-skill-optimization/prepared-research/SOURCE_REGISTER.md`: fontes e escopo real de consulta.
- `.ai-work/20261028-skill-study-provider-switch/TODO.md`: checklist nativa.
- `docs/plans/20261028-skill-optimization/IMPLEMENTATION_CHECKLIST.md`: visão com links diretos para tarefas e relatórios.
- `docs/plans/20261028-skill-optimization/PLAN1_SPEC.json`: especificação do plano único; nome preservado por compatibilidade.
- `docs/plans/20261028-skill-optimization/RESEARCH_CONVERSION_VALIDATION.json`: comandos e resultados desta preparação.

Para carregar apenas uma tarefa, execute na raiz:

```bash
python docs/plans/20261028-skill-optimization/support/check_delivery.py --inputs 006
```

Os testes específicos novos listados nos relatórios ainda devem ser escritos durante a implementação. Não foram marcados como aprovados por existirem neste plano.

## Validação e limites

A validação e auditoria nativas do plano, a vinculação do estudo, a estrutura dos relatórios e os 172 vínculos de validação passaram. Os 33 testes do verificador local passaram. A tentativa de aceitar a tarefa 001 sem implementação foi corretamente rejeitada. Esses testes validam a preparação, não as funcionalidades futuras.

Os 135 arquivos de produto em `skill/`, `bin/` e `lib/` permanecem idênticos à base. Os scripts novos ou revisados em `docs/plans/.../support/` são auxiliares do plano. Não foi executada a suíte completa `npm run check` nesta revisão documental; os logs antigos permanecem históricos.

A execução automática permanece desligada. Nenhuma revisão externa, chamada autenticada de modelo, instalação, commit, push ou publicação foi feita nesta rodada.

## Retomada em outro computador

Consulte `PORTABILITY.md` antes de executar. O manifesto exportado contém o caminho absoluto deste ambiente; outro host deve recriá-lo com os controladores nativos, preservando o mesmo identificador e a especificação atual. Não altere status ou caminhos internos manualmente. O histórico anterior foi arquivado em `history/pre-research-conversion/` e não deve ser retomado como segundo plano.

A branch remota de referência continua `checkpoint/plano1-estudo-provider-switch-20261028`, no commit `d4fc2ae` verificado antes desta alteração. As mudanças desta entrega estão na cópia local e no ZIP; não foram enviadas ao GitHub.
