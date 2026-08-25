# Contribuindo

1. Crie uma branch a partir de `main`.
2. Mantenha o instalador sem dependencias de runtime sempre que possivel.
3. Execute `npm ci` e `npm run check`.
4. Inclua testes para mudancas no instalador.
5. Preserve compatibilidade com Python 3.10+ em `skill/plan-and-execute/scripts/`.
6. Nao inclua credenciais, logs privados ou planos reais de clientes.
7. Abra um pull request descrevendo comportamento, testes e riscos.
