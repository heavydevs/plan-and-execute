# Publicação no GitHub e npm

[English version](PUBLISHING.md)

## Repositório

O repositório oficial é:

```text
heavydevs/plan-and-execute
```

Clone e valide:

```bash
git clone https://github.com/heavydevs/plan-and-execute.git
cd plan-and-execute
npm ci
npm run check
```

## Testar diretamente pelo GitHub

Não é necessário publicar no npm:

```bash
npx --yes --package=github:heavydevs/plan-and-execute \
  plan-and-execute --version
```

Teste em um workspace temporário:

```bash
TEMP_DIR="$(mktemp -d)"

npx --yes --package=github:heavydevs/plan-and-execute \
  plan-and-execute install --agent both --scope workspace --cwd "$TEMP_DIR"

npx --yes --package=github:heavydevs/plan-and-execute \
  plan-and-execute status --agent both --scope workspace --cwd "$TEMP_DIR"

rm -rf "$TEMP_DIR"
```

## Confirmar o scope npm

O `package.json` ainda utiliza:

```json
"name": "@luizcgvrj/plan-and-execute"
```

A organização do GitHub e o scope do npm são independentes. Confirme o acesso:

```bash
npm login
npm whoami
```

Caso uma versão futura use `@heavydevs/plan-and-execute`, atualize `package.json`, `package-lock.json`, os READMEs, os guias de instalação e o Trusted Publisher.

## Primeira publicação pública

```bash
npm ci
npm run check
npm publish --access public
```

Valide:

```bash
npx --yes @luizcgvrj/plan-and-execute --version
```

## Trusted Publishing

Configure o publisher do GitHub Actions para:

```text
organização: heavydevs
repositório: plan-and-execute
workflow: publish.yml
```

Pela CLI do npm:

```bash
npm install --global npm@latest

npm trust github @luizcgvrj/plan-and-execute \
  --repo heavydevs/plan-and-execute \
  --file publish.yml \
  --allow-publish \
  --yes
```

## Publicar uma nova versão

```bash
npm version patch
git push origin main --follow-tags

VERSION="$(node -p "require('./package.json').version")"
gh release create "v${VERSION}" --generate-notes
```

O workflow valida a tag, executa todos os testes e publica o pacote.

## Checklist de release

```bash
npm ci
npm run check
npm pack --dry-run
npx --yes --package=. plan-and-execute --version
```

Confirme também que o README rápido está atualizado nos dois idiomas, `requestctl.py` está incluído, nenhum `.ai-work` foi commitado e o CI terminou com sucesso.
