# Instruções do projeto ChatGPT — pesquisa, arquitetura e execução

Repositório: https://github.com/heavydevs/plan-and-execute
Branch exclusiva: `checkpoint/plano1-estudo-provider-switch-20261028`

Execute **um ciclo completo da primeira task de desenvolvimento pendente** do plano ativo: pesquisa → decisão arquitetural → implementação/revisão → testes automatizados → revisão independente real (quando exigida) → gate final → commit/push. Não pare após produzir somente pesquisa nem avance à task seguinte enquanto a selecionada estiver incompleta.

1. Antes de agir, leia o `AGENTS.md` da raiz, o `guia_de_pesquisa_execucao_tasks.md` e o roteador `.ai-work/chatgpt-executor/ENTRYPOINT.md`. Confirme branch, HEAD remoto, task inicial pendente do manifest, dependências, escopo, checklist de pesquisa e de execução e evidências existentes. **A task 015 tem pesquisa pronta, execução ainda pendente**: retome a execução, sem começar pela pesquisa 020.
2. Se a pesquisa da task escolhida estiver faltando ou desatualizada, estude o código e pesquise profundamente fontes oficiais, livros, artigos, estudos, benchmarks e alternativas. Salve relatório individual com referências, arquitetura adotada, segurança, performance, compatibilidade, orçamento de tokens e testes adversariais. Vincule o relatório à task e marque a pesquisa somente após validação e commit/push.
3. Implemente a task com base no relatório, corrigindo a arquitetura só quando houver divergência material demonstrável. Preserve contratos, status e dependências e mantenha a menor alteração necessária. Use GitHub connector com CAS para commits; se não houver checkout local, utilize GitHub Actions para testes reais sobre o SHA exato.
4. Execute todos os checks declarados. Deixe cada suíte chegar ao fim quando possível, consolide falhas e logs individualizados, corrija as falhas focais, e só então reexecute os gates completos. Não confunda testes do executor com testes da task.
5. Para review independente obrigatório, invoque um **modelo distinto e autenticado**, com sessão/modelo/effort reais, hashes de fonte e findings reproduzíveis. Prefira o `review_dispatch.py`; se indisponível, utilize o adaptador GitHub Copilot em `.ai-work/chatgpt-executor/GATE_REVISAO_015.md`, com uma chamada autorizada e sem simulação. Nunca declare independência por autorrevisão.
6. Só quando o `check_delivery.py` original e validações finais passarem, registre recibo/outcome, conclua checkpoints pela autoridade do plano, marque execução no guia, faça commit/push na branch e confira o remoto. Sem review, credencial, ferramenta ou gate válido, mantenha a task pendente e registre bloqueio verificável; não fabrique evidências.
7. Não altere `main`, não use force-push, não inicie outra task na mesma execução e não faça perguntas de confirmação desnecessárias. Reaproveite estudos existentes, use leitura incremental, evite pagar por inferência desnecessária e reporte limites/custos potenciais.

Ao finalizar, informe a task escolhida, relatório/arquitetura, implementações, testes, revisão, gate, commits publicados, bloqueios reais e a próxima task somente se a atual tiver sido efetivamente concluída.
