# Codespace PAE — full access, bypass e sem sandbox interno

**Status:** instruções versionadas, NÃO executadas no Codespace pelo ChatGPT. Autorização expressa do usuário para este Codespace, não para GitHub Actions ou outros ambientes.

## Estado confirmado

- O usuário comprovou `agy -p ...` com `status=SUCCESS`.
- `agy models` lista `claude-opus-5-5-high` e `claude-sonnet-5-5-high`: são modelos **via Antigravity**, não o binário Claude Code independente nem necessariamente a franquia da assinatura Anthropic.
- O teste inicial de `claude --version` retornava `command not found`, mas o usuário **instalou depois o Claude Code CLI independente**, autenticou via `claude.ai` e obteve `Claude execucao: PASSOU` no smoke local. Ainda não existe acesso remoto do ChatGPT ao terminal.
- O conector GitHub do ChatGPT **não** concede sessão de terminal/SSH no Codespace.

## Configurar AGY no perfil pessoal sem sobrescrever autenticação

Execute **no terminal do Codespace**, sem copiar para logs públicos. O bloco preserva as outras chaves de `settings.json`, inclusive as relacionadas ao provedor autenticado:

```bash
python3 - <<'PY'
import json
from pathlib import Path
p = Path.home() / ".gemini" / "antigravity-cli" / "settings.json"
p.parent.mkdir(parents=True, exist_ok=True)
if p.is_symlink():
    raise SystemExit("Symlink em settings.json: abortado.")
data = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
if not isinstance(data, dict):
    raise SystemExit("Formato inesperado de settings.json")
data.update({
    "agentMode": "",
    "enableTerminalSandbox": False,
    "allowNonWorkspaceAccess": True,
    "toolPermission": "always-proceed",
    "artifactReviewPolicy": "always-proceed",
    "useG1Credits": False
})
p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
p.chmod(0o600)
print("AGY: full access local configurado (sem exibir credenciais).")
PY
```

Usar `agentMode: ""` porque versões novas com `auto` podem reativar o sandbox. `useG1Credits: false` evita usar créditos extras quando acaba a quota da franquia (quando aplicável). Não usar `--mode=auto` nem `--sandbox`.

Teste de invocação com modelo Sonnet via AGY:

```bash
cd /workspaces/plan-and-execute
agy --dangerously-skip-permissions \
  --model claude-sonnet-5-5-high \
  --output-format json --print-timeout 2m \
  -p 'Responda PAE_ACCESS_OK sem modificar arquivos nem chamar ferramentas.'
```

Para solicitar Opus via AGY em sessão independente, use `--model claude-opus-5-5-high` em **nova execução** (sem `--continue`). O `conversation_id` do AGY não é automaticamente um `session_id` do Claude Code.

## Claude Code CLI independente (opcional, para usar a franquia Anthropic)

O Claude Code **já foi instalado e autenticado pelo usuário**. Para reinstalação futura, o procedimento oficial no Codespace Linux é:

```bash
curl -fsSL https://claude.ai/install.sh -o /tmp/install-claude.sh
bash /tmp/install-claude.sh
export PATH="$HOME/.local/bin:$PATH"
claude --version
claude auth login
claude auth status --text
```

Autentique a assinatura Claude.ai; não configure uma API Key cobrada. A execução de sessão **full access, bypass e sem sandbox** pode então ser feita por:

```bash
claude --dangerously-skip-permissions \
  --settings '{"sandbox":{"enabled":false}}' \
  --model claude-sonnet-5-5 --effort high \
  -p 'Responda PAE_ACCESS_OK sem editar arquivos.'
```

A CLI oficial documenta `--dangerously-skip-permissions` como equivalente a `--permission-mode bypassPermissions`. Configurações gerenciadas da organização podem impedir esse modo. Não compartilhar arquivos `~/.claude/` ou `~/.gemini/`.

## Revisão independente, riscos e gates

**Acesso completo permite comandos irreversíveis e acesso a credenciais**, inclusive por conteúdo não confiável de código, documentos, testes e logs. O usuário escolheu esse modo no Codespace; isso **não amplia o write scope da task**. Nunca conceder bypass no runner público do GitHub ou a workflows disparáveis por terceiros.

O revisor independente deve **não editar** nenhum arquivo, ainda que seu CLI tenha essa capacidade. Comparar `git status --porcelain`, `git rev-parse HEAD`, e hashes dos arquivos antes/depois. Qualquer diferença invalida a revisão. A prova da sessão/modelo/esforço precisa ser autêntica.

**O gate formal da task 015 ainda requer argumentos read-only** em `docs/plans/20261028-skill-optimization/support/review_dispatch.py`. Executar o reviewer com bypass e sem sandbox NÃO satisfaz esse contrato automaticamente. Não alterar `check_delivery.py` ou inventar recibos para aprovar: adaptar o contrato e seus testes negativos primeiro, ou manter 015 pendente.

## Documentação oficial

- https://antigravity.google/docs/cli/reference
- https://antigravity.google/docs/cli/modes
- https://antigravity.google/docs/cli/headless/
- https://code.claude.com/docs/en/cli-reference
- https://code.claude.com/docs/en/permissions
- https://code.claude.com/docs/en/setup
