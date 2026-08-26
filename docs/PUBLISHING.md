# Publishing to GitHub and npm

[Versão em português](PUBLISHING.pt-BR.md)

## Repository

The canonical repository is:

```text
heavydevs/plan-and-execute
```

Clone and validate it:

```bash
git clone https://github.com/heavydevs/plan-and-execute.git
cd plan-and-execute
npm ci
npm run check
```

## Test distribution directly from GitHub

No npm publication is required:

```bash
npx --yes --package=github:heavydevs/plan-and-execute \
  plan-and-execute --version
```

Test a temporary workspace:

```bash
TEMP_DIR="$(mktemp -d)"

npx --yes --package=github:heavydevs/plan-and-execute \
  plan-and-execute install --agent both --scope workspace --cwd "$TEMP_DIR"

npx --yes --package=github:heavydevs/plan-and-execute \
  plan-and-execute status --agent both --scope workspace --cwd "$TEMP_DIR"

rm -rf "$TEMP_DIR"
```

## Confirm the npm scope

`package.json` currently uses:

```json
"name": "@luizcgvrj/plan-and-execute"
```

The GitHub organization and npm scope are independent. Confirm control of the npm scope before publishing:

```bash
npm login
npm whoami
```

If a future release moves to `@heavydevs/plan-and-execute`, update:

- `name` in `package.json` and `package-lock.json`;
- npm commands in both README files;
- npm commands in both installation guides;
- trusted-publisher configuration.

## First public npm release

```bash
npm ci
npm run check
npm publish --access public
```

Then verify:

```bash
npx --yes @luizcgvrj/plan-and-execute --version
```

## Trusted Publishing with GitHub Actions

After the package exists on npm, configure a GitHub Actions trusted publisher for:

```text
organization: heavydevs
repository: plan-and-execute
workflow: publish.yml
```

Using a recent npm CLI:

```bash
npm install --global npm@latest

npm trust github @luizcgvrj/plan-and-execute \
  --repo heavydevs/plan-and-execute \
  --file publish.yml \
  --allow-publish \
  --yes
```

The included workflow uses a GitHub-hosted runner, OIDC (`id-token: write`), Node.js 24, a recent npm CLI, tests before publication, and package provenance for a public repository/package when supported by npm.

## Release a new version

Update the version and changelog:

```bash
npm version patch
```

Use `minor` or `major` when appropriate. Push the commit and tag:

```bash
git push origin main --follow-tags
```

Create the GitHub Release that triggers `.github/workflows/publish.yml`:

```bash
VERSION="$(node -p "require('./package.json').version")"
gh release create "v${VERSION}" --generate-notes
```

The workflow verifies that the tag matches `package.json`, runs all checks, and publishes.

## Release checklist

```bash
npm ci
npm run check
npm pack --dry-run
npx --yes --package=. plan-and-execute --version
```

Also verify:

- no generated `.ai-work` content is committed;
- `README.md` starts with the current quick guide;
- `README.pt-BR.md` remains aligned;
- `skill/plan-and-execute/SKILL.md` and all referenced files are packaged;
- `scripts/requestctl.py` is executable and included;
- the installed skill passes `scripts/self_test.py`;
- the GitHub Actions CI run succeeds before creating a release.
