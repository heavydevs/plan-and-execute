# F031 / task 066 - Installer, configuration, packaging and cross-platform CI

Date: 2026-10-28. Product baseline: 0.11.0, tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Research prepared; implementation pending; independent review pending.** This report is an implementation input, not a completion receipt. No external reviewer is impersonated.

## Decision and scope

**Recommendation (engineering inference):** Harden distribution around actual package manifests, managed-copy integrity and supported platform contracts, without modifying user installations during development.

## Questions addressed

- Check selective/explicit activation, companion packages, local-edit protection and uninstall safety.
- Evaluate schema drift, versions, docs budgets, dependency/secret handling and actual platform test coverage.

## Repository evidence

The following are static-code observations against the pinned baseline, not results from authenticated providers:

- The installer distinguishes managed source and installed variants, supports selective/explicit activation and protects locally edited copies.
- package.json includes docs in the distributable file set. Adding plan/research artifacts requires an explicit packaging exclusion and actual tarball-list test.
- Two related skills are packaged with shared-resolution behavior. A companion archive alone is not proof of a working installed pair.

### Read targets and integrity

- `bin/plan-and-execute.js` (SHA-256 `3899d498c10b91f03c657fbaf33885d7fc339e0c3f11cf95ad96936852afc15b`): `#!/usr/bin/env node` L1; `function fail(message, code = 1) {` L133; `function requireValue(args, index, option) {` L138; `export function parseArguments(argv) {` L144
- `lib/installer.js` (SHA-256 `9165b2cabb1c93858bda46c9f3aa69a6b19be5a15c240cc55952663dc3d3305b`): `function lstatIfPresent(targetPath) {` L32; `function readJsonIfPresent(filePath) {` L41; `export function getPackageVersion() {` L50; `export function readSkillName(skillDirectory) {` L54
- `lib/skill-source.js` (SHA-256 `6a47e8930f1e87a08c74e048d4065b2bb8b33bf8b809629f923a3c0537a6f2e7`): `export function normalizeSkill(value = SKILLS[0], allowAll = false) {` L13; `export function skillSource(name) {` L20; `export function stageSkillSource(name, sourceDirectory = skillSource(name)) {` L24
- `tools/package-skills.js` (SHA-256 `aadaf4aa9e599d27f01aaf980e83d02085e998b1a461b42e504002f716e4faaa`): `#!/usr/bin/env node` L1
- `tools/validate-skill.js` (SHA-256 `4d67bc446bf4a54d73263fb0a74f91f137c49c34fae71cddd6dd38550bb43f01`): `#!/usr/bin/env node` L1; `function fail(message) {` L14; `function requireFile(relativePath) {` L18; `function read(relativePath) {` L25
- `tools/clean-generated.js` (SHA-256 `a518c4e51df9b00abdb0b3405924c1637d9f6b028dab971da6171e8f00316265`): `#!/usr/bin/env node` L1; `function clean(directory) {` L7
- `skill/plan-and-execute/scripts/configure.py` (SHA-256 `4e454ce5f6e141194bb5b2e95d5ba42e9b7a4f94d8bf4c957c2c1af3d003e8cd`): `Cancelled` L24-25; `Question` L29-35; `terminal_ask` L38-55; `discover` L58-76
- `.github/workflows/ci.yml` (SHA-256 `e81d00384c47756cf0d95094c884d47851b731179f586e10a02767fb40f290b4`): file-level contract
- `SECURITY.md` (SHA-256 `ace4f544568076007de2152ce8d61f3e448be91f7914b3a5accbc48455bca792`): `# Security policy` L1

## External basis

- [E048] [package.json files field](https://docs.npmjs.com/cli/v11/configuring-npm/package-json/) - npm; accessed 2026-10-28.
- [E049] [npm pack](https://docs.npmjs.com/cli/v11/commands/npm-pack/) - npm; accessed 2026-10-28.
- [E055] [GITHUB_TOKEN permissions](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token) - GitHub; accessed 2026-10-28.
- [E001] [Agent Skills specification](https://agentskills.io/specification) - Agent Skills; accessed 2026-10-28.
- [E058] [Semantic Versioning 2.0.0](https://semver.org/) - SemVer; accessed 2026-10-28.

Consult only these entries in `SOURCE_REGISTER.md` for the checked finding and scope. Provider documentation establishes an interface, not this account's available quota or a universal ranking of model quality. The proposed design below combines that evidence with the repository observations; it is not a vendor guarantee.

## Alternatives and cost/quality tradeoffs

| Disposition | Approach | Tradeoff |
|---|---|---|
| current_baseline | Ship the whole repository and trust ignore files | Easy but can expose planning/log artifacts and grow context/package size. |
| recommended | Manifest-based packages and integrity-aware installation | Small deterministic tests protect both privacy and user edits. |
| rejected | Auto-install or globally reconfigure the user while developing | Unrequested side effects and risk of destroying local customizations. |

## Implementation instructions

1. Define the minimal intended npm/skill file manifest and exclude planning controls, research execution logs, credentials, caches and transfer artifacts.
2. Test npm pack --dry-run --json against that manifest, and test actual staged skill ZIP membership and size. A .gitignore alone is not the packaging contract.
3. Preserve source/installed hashes for activation transforms and refuse overwrite/uninstall of local edits unless explicitly authorized.
4. Add compatible version checks for companion resolution, including missing and mismatched installations, while preserving supported old layouts.
5. Keep CI permissions minimal and include supported Node/Python plus Windows/POSIX behavior. Report skips and unsupported platform cases rather than a single unqualified pass.

## Acceptance tests to implement and run

- [ ] No native plan, private log, .env, bytecode or node_modules entry appears in a distributable archive.
- [ ] Selective-explicit-selective round trips retain correct hashes and policy metadata.
- [ ] A locally edited installed file prevents automatic replacement/removal.
- [ ] Companion packages resolve a matching shared runtime after a clean temporary install.
- [ ] CLI/docs/version constraints and actual package contents are checked without publishing.

These cases are proposed test obligations. A research report or a fake-provider fixture cannot establish production model performance. Record executed commands, exit codes, source state and logs in the task's implementation receipt.

## Economic evaluation

Measure package bytes/file count and installation probe time. Keep runtime resources available on demand but leave maintainer research out of routine worker packages.

## Rollout and compatibility

Use the existing small deterministic helpers and compose through `run_concise.py` where applicable. Preserve disabled-mode behavior, persisted schema compatibility and locally edited installed copies. Add a behavior-changing policy only behind an explicit tested option. Do not add a framework, a paid model call or a global setting merely to satisfy this report. If current code already satisfies a proposed invariant, keep it and add the missing regression evidence instead of duplicating the mechanism.

## Limits and unresolved verification

- No npm publication, account skill installation or global configuration modification is authorized or performed by this research task.
- No paid model benchmark, Windows live execution or independent maximum-model code review was performed during this research. Those are distinct future acceptance activities where applicable.

## Task handoff

Task **066** now implements this recommendation; task **067** reviews the resulting code and requires corrections before acceptance. Read this report, its JSON decision record and only the assigned source paths. Do not repeat broad research unless a material version mismatch invalidates a specific finding. No second plan is required.
