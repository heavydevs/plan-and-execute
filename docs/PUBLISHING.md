# Publicacao no GitHub e no npm

## 1. Usar um repositorio, nao apenas GitHub Projects

GitHub Projects e um quadro para organizar issues e pull requests. O codigo, o historico de versoes, as releases e os workflows precisam ficar em um repositorio.

Nome recomendado:

```text
luizcgvrj/plan-and-execute
```

O GitHub Project pode ser criado depois e associado ao repositorio para acompanhar melhorias.

## 2. Criar e enviar o repositorio

Extraia o ZIP do repositorio e entre na pasta:

```bash
unzip plan-and-execute-repo.zip
cd plan-and-execute
```

Com GitHub CLI autenticado:

```bash
git init -b main
git add .
git commit -m "feat: publish plan-and-execute skill and installer"

gh auth login
gh repo create luizcgvrj/plan-and-execute \
  --public \
  --source=. \
  --remote=origin \
  --push
```

Sem GitHub CLI, crie um repositorio vazio na interface e execute:

```bash
git init -b main
git add .
git commit -m "feat: publish plan-and-execute skill and installer"
git remote add origin git@github.com:luizcgvrj/plan-and-execute.git
git push -u origin main
```

Nao adicione README, `.gitignore` ou licenca na criacao remota, pois o pacote ja contem esses arquivos.

## 3. Testar a distribuicao direta pelo GitHub

Depois do push, nenhuma publicacao npm e necessaria para testar:

```bash
npx --yes --package=github:luizcgvrj/plan-and-execute \
  plan-and-execute --version
```

Instalacao em um workspace temporario:

```bash
TEMP_DIR="$(mktemp -d)"

npx --yes --package=github:luizcgvrj/plan-and-execute \
  plan-and-execute install --agent both --scope workspace --cwd "$TEMP_DIR"

npx --yes --package=github:luizcgvrj/plan-and-execute \
  plan-and-execute status --agent both --scope workspace --cwd "$TEMP_DIR"

rm -rf "$TEMP_DIR"
```

O npm aceita repositorios Git como package spec, incluindo o atalho `github:owner/repo`.

## 4. Confirmar o scope npm

O `package.json` usa:

```json
"name": "@luizcgvrj/plan-and-execute"
```

O nome pressupoe uma conta ou organizacao npm com o scope `@luizcgvrj`. O username do GitHub e o username do npm sao independentes.

Confirme antes da primeira publicacao:

```bash
npm login
npm whoami
```

Se o username ou scope npm for diferente, altere:

- `name` no `package.json`;
- exemplos npm no `README.md`;
- exemplos npm em `skill/plan-and-execute/references/INSTALLATION.md`.

O instalador le o nome do pacote diretamente do `package.json`, entao nao precisa de outra alteracao interna.

## 5. Primeira publicacao publica

Pacotes com scope sao privados por padrao. Para publicar este pacote como publico:

```bash
npm ci
npm run check
npm publish --access public
```

A publicacao direta exige uma conta npm com 2FA ou outra forma de autenticacao aceita pelo registro.

Depois, valide:

```bash
npx --yes @luizcgvrj/plan-and-execute --version
```

## 6. Configurar Trusted Publishing com GitHub Actions

Depois que o pacote existir no npm, configure um Trusted Publisher para evitar um token npm permanente no GitHub.

Pela CLI atual do npm:

```bash
npm install --global npm@latest

npm trust github @luizcgvrj/plan-and-execute \
  --repo luizcgvrj/plan-and-execute \
  --file publish.yml \
  --allow-publish \
  --yes
```

Ou configure na pagina do pacote no npm:

- provider: GitHub Actions;
- organization/user: `luizcgvrj`;
- repository: `plan-and-execute`;
- workflow filename: `publish.yml`;
- allowed action: `npm publish`.

O workflow incluido usa:

- GitHub-hosted runner;
- `id-token: write` para OIDC;
- Node.js 24;
- npm 11.5.1 ou superior;
- `repository.url` correspondente ao repositorio;
- publicacao somente depois dos testes;
- proveniencia automatica para repositorio e pacote publicos.

## 7. Publicar novas versoes

Atualize a versao:

```bash
npm version patch
```

Ou use `minor`/`major` conforme o tipo de mudanca.

Envie o commit e a tag:

```bash
git push origin main --follow-tags
```

Crie a GitHub Release que dispara `.github/workflows/publish.yml`:

```bash
VERSION="$(node -p "require('./package.json').version")"
gh release create "v${VERSION}" --generate-notes
```

O workflow confirma que a tag `v<versao>` corresponde ao `package.json`, executa os testes e publica.

## 8. Validar cada release

```bash
npx --yes @luizcgvrj/plan-and-execute --version
npx --yes @luizcgvrj/plan-and-execute doctor
npx --yes @luizcgvrj/plan-and-execute status --agent both --scope user
```

Teste tambem em workspace temporario antes de recomendar a versao:

```bash
TEMP_DIR="$(mktemp -d)"

npx --yes @luizcgvrj/plan-and-execute \
  install --agent both --scope workspace --cwd "$TEMP_DIR"

npx --yes @luizcgvrj/plan-and-execute \
  uninstall --agent both --scope workspace --cwd "$TEMP_DIR"

rm -rf "$TEMP_DIR"
```
