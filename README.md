# plan-and-execute

Skill para Claude Code e Codex que transforma mudancas longas de software em tarefas pequenas, isoladas, retomaveis e validadas de forma deterministica.

O repositorio inclui:

- planejamento profundo antes da execucao, com estudo do pedido, repositorio e fontes externas quando necessario;
- rastreabilidade completa `pedido (Pxxx) -> requisito (Rxxx) -> TODO`;
- decomposicao recursiva de workstreams grandes e rejeicao de TODO executavel `extreme`;
- revisao independente do plano e quality gates `validate` + `audit`;
- a skill `plan-and-execute` completa;
- um instalador npm sem dependencias externas;
- suporte a Claude Code, Codex ou ambos;
- instalacao no workspace ou no perfil do usuario;
- verificacao por hash para preservar alteracoes locais;
- testes Node e Python;
- workflows de CI e publicacao no npm por OIDC.

## Instalacao rapida

### Direto do GitHub, antes da publicacao no npm

```bash
npx --yes --package=github:luizcgvrj/plan-and-execute \
  plan-and-execute install --agent both --scope user
```

### Depois da publicacao no npm

```bash
npx --yes @luizcgvrj/plan-and-execute \
  install --agent both --scope user
```

### CLI instalada globalmente

```bash
npm install --global @luizcgvrj/plan-and-execute
pae install both --global
```

`pae` e o alias curto de `plan-and-execute`.

## Destinos

| Agente | Workspace | Usuario |
| --- | --- | --- |
| Claude Code | `.claude/skills/plan-and-execute` | `~/.claude/skills/plan-and-execute` |
| Codex | `.agents/skills/plan-and-execute` | `~/.agents/skills/plan-and-execute` |

No Windows, `~` normalmente corresponde a `%USERPROFILE%`.

## Comandos

```bash
# Instalar para os dois agentes no workspace atual
pae install both --local

# Instalar somente para Claude no perfil do usuario
pae install claude --global

# Instalar somente para Codex em outro workspace
pae install codex --cwd /caminho/do/projeto

# Mostrar os destinos calculados
pae paths both --global

# Verificar estado, versao e alteracoes locais
pae status both --local

# Diagnosticar Node, Python, Claude CLI e Codex CLI
pae doctor

# Simular sem alterar arquivos
pae install both --local --dry-run

# Atualizar mesmo quando a copia instalada foi editada
pae install both --global --force

# Remover uma instalacao gerenciada
pae uninstall both --global
```

As mesmas opcoes podem ser escritas de forma explicita:

```text
--agent claude|codex|both
--scope workspace|user
--cwd <diretorio>
--force
--dry-run
--json
```

## Comportamento de seguranca

O instalador copia a skill; ele nao cria um link para o cache temporario do `npx`.

Cada instalacao recebe `.plan-and-execute-install.json` com versao e SHA-256 do conteudo. Assim, o instalador consegue:

- reconhecer uma copia que ele gerencia;
- nao fazer nada quando a copia ja esta atualizada;
- atualizar automaticamente uma copia gerenciada e intacta;
- interromper antes de sobrescrever alteracoes locais;
- exigir `--force` para substituir ou remover conteudo modificado;
- recusar diretorios de outra skill e destinos que sejam links simbolicos;
- substituir a pasta de forma atomica, com restauracao em caso de falha.

O pacote nao usa `postinstall`: nenhuma pasta do usuario ou do projeto e modificada apenas por instalar a dependencia npm. A alteracao ocorre somente depois de um comando `install` explicito.

## Planejamento profundo e verificavel

Antes de executar, a skill agora exige:

1. leitura integral do pedido e inventario de cada parte como `P001`, `P002`, etc.;
2. inspecao concreta do repositorio e pesquisa autoritativa quando o assunto for atual, desconhecido, sensivel a versao ou a seguranca;
3. requisitos `R001`, `R002`, etc. ligados explicitamente aos itens `Pxxx`;
4. decomposicao recursiva de cada workstream ate chegar a TODOs com um resultado coerente e validacao independente;
5. rejeicao de qualquer TODO executavel classificado como `extreme`;
6. justificativa de atomicidade para TODOs `high`;
7. revisao do plano em contexto novo;
8. validacao estrutural e auditoria de cobertura antes do autostart.

Cada plano novo gera `ANALYSIS.md`, `PLAN.md`, `PLAN_REVIEW.md`, `TODO.md` e um arquivo de definicao por tarefa. O comando de auditoria mostra a cadeia completa de cobertura:

```bash
python <skill-dir>/scripts/planctl.py audit --plan .ai-work/<plan-id>
```

A quantidade de TODOs nao e fixa: uma solicitacao com varios blocos grandes pode produzir varios workstreams, e cada bloco e dividido novamente quando possui resultados, riscos ou validacoes independentes. Ao mesmo tempo, a skill evita microtarefas artificiais por arquivo.

## Como invocar a skill

No Claude Code:

```text
/plan-and-execute Implemente esta mudanca grande, incluindo testes automatizados: ...
```

No Codex CLI ou na extensao do VS Code:

```text
$plan-and-execute Implemente esta mudanca grande, incluindo testes automatizados: ...
```

Exemplo de pedido:

```text
Use plan-and-execute. Estude integralmente o pedido, o repositorio e o assunto antes de planejar. Inventarie cada parte do pedido, crie requisitos rastreaveis, divida recursivamente cada workstream grande em TODOs executaveis com validacao independente, revise o plano em contexto novo e so inicie depois que validate e audit passarem. Use um trabalhador novo para cada tarefa. Escalone esforco e modelo somente depois de falha tecnica comprovada. No final, resuma com um modelo economico e remova apenas os artefatos temporarios de planejamento.
```

## Executor estrito

O modo nativo usa subagentes do cliente atual. Para obter processos totalmente novos, sem sessao persistida, e permitir roteamento entre Claude CLI e Codex CLI, use o runner Python da skill em um terminal externo:

```bash
python .agents/skills/plan-and-execute/scripts/run_isolated.py \
  --plan .ai-work/<plan-id>
```

ou:

```bash
python .claude/skills/plan-and-execute/scripts/run_isolated.py \
  --plan .ai-work/<plan-id>
```

Para preservar o plano durante os primeiros testes:

```bash
python <skill-dir>/scripts/run_isolated.py \
  --plan .ai-work/<plan-id> \
  --no-cleanup
```

## Requisitos

- Node.js 18.17 ou superior para o instalador;
- Python 3.10 ou superior para os scripts da skill;
- Claude Code e/ou Codex instalados para executar tarefas reais;
- GitHub CLI opcional para publicar o repositorio;
- conta npm opcional para publicar no registro.

## Desenvolvimento

```bash
npm ci
npm run check
npm pack --dry-run
```

`npm run check` executa:

1. validacao estrutural e busca pelo nome antigo;
2. testes unitarios e de integracao do instalador;
3. self-test completo dos scripts Python da skill.

## Estrutura do repositorio

```text
plan-and-execute/
├── bin/plan-and-execute.js
├── lib/installer.js
├── skill/plan-and-execute/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── references/
│   └── scripts/
├── test/
├── tools/
├── docs/PUBLISHING.md
├── package.json
└── .github/workflows/
```

## Publicacao

As instrucoes para criar o repositorio, testar diretamente pelo GitHub, confirmar o scope npm e habilitar Trusted Publishing estao em [docs/PUBLISHING.md](docs/PUBLISHING.md).

## Licenca

MIT.
