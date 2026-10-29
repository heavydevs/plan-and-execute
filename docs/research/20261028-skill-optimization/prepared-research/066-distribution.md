# 066 - Distribution: research revision 2

Date: 2026-10-28. Feature: `F031`. Implementation TODO `066`; independent review TODO `067`. Product baseline: `0.11.0` / tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Prepared design evidence, not implemented code. Implementation and independent review remain pending.**

## Recommended direction

Validate the actual distributable and installed dependency layout, preserve edited user installations, and separate metadata-only pack inspection from lifecycle/full-suite execution.

This is a conditional engineering recommendation for this repository, not a proof of a global optimum or a measured saving on the user's workload.

## Change from the previous report

The revision adds lifecycle-script distinctions, installer rollback/dependency checks, artifact secret scans and workflow least privilege rather than treating a dry-run file list as a complete release test.

The previous report is retained under `docs/plans/20261028-skill-optimization/history/research-round-1/prepared-research/` for audit. New W-prefixed sources below are the current-round evidence; old E-prefixed sources remain background.

## Questions and repository evidence

- Check selective/explicit activation, companion packages, local-edit protection and uninstall safety.
- Evaluate schema drift, versions, docs budgets, dependency/secret handling and actual platform test coverage.

**Baseline observations:**
- The installer distinguishes managed source and installed variants, supports selective/explicit activation and protects locally edited copies.
- package.json includes docs in the distributable file set. Adding plan/research artifacts requires an explicit packaging exclusion and actual tarball-list test.
- Two related skills are packaged with shared-resolution behavior. A companion archive alone is not proof of a working installed pair.

All listed file hashes matched the preserved 0.11.0 source in this revision. This is integrity checking, not a second full code audit.

| Code anchor | SHA-256 | Selected symbols / location |
|---|---|---|
| `bin/plan-and-execute.js` | `3899d498c10b91f03c657fbaf33885d7fc339e0c3f11cf95ad96936852afc15b` | #!/usr/bin/env node:1; function fail(message, code = 1) {:133; function requireValue(args, index, option) {:138; export function parseArguments(argv) {:144 |
| `lib/installer.js` | `9165b2cabb1c93858bda46c9f3aa69a6b19be5a15c240cc55952663dc3d3305b` | function lstatIfPresent(targetPath) {:32; function readJsonIfPresent(filePath) {:41; export function getPackageVersion() {:50; export function readSkillName(skillDirectory) {:54 |
| `lib/skill-source.js` | `6a47e8930f1e87a08c74e048d4065b2bb8b33bf8b809629f923a3c0537a6f2e7` | export function normalizeSkill(value = SKILLS[0], allowAll = false) {:13; export function skillSource(name) {:20; export function stageSkillSource(name, sourceDirectory = skillSource(name)) {:24 |
| `tools/package-skills.js` | `aadaf4aa9e599d27f01aaf980e83d02085e998b1a461b42e504002f716e4faaa` | #!/usr/bin/env node:1 |
| `tools/validate-skill.js` | `4d67bc446bf4a54d73263fb0a74f91f137c49c34fae71cddd6dd38550bb43f01` | #!/usr/bin/env node:1; function fail(message) {:14; function requireFile(relativePath) {:18; function read(relativePath) {:25 |
| `tools/clean-generated.js` | `a518c4e51df9b00abdb0b3405924c1637d9f6b028dab971da6171e8f00316265` | #!/usr/bin/env node:1; function clean(directory) {:7 |
| `skill/plan-and-execute/scripts/configure.py` | `4e454ce5f6e141194bb5b2e95d5ba42e9b7a4f94d8bf4c957c2c1af3d003e8cd` | Cancelled:24; Question:29; terminal_ask:38; discover:58 |
| `.github/workflows/ci.yml` | `e81d00384c47756cf0d95094c884d47851b731179f586e10a02767fb40f290b4` |  |
| `SECURITY.md` | `ace4f544568076007de2152ce8d61f3e448be91f7914b3a5accbc48455bca792` | # Security policy:1 |

## Deeper analysis and competing approaches

### 1. Design analysis

The npm files allowlist includes docs, so merely adding an ignore rule may still leave planning or diagnostic material in a release. Inspect the actual JSON pack manifest and assert positive required paths and negative forbidden classes. A metadata-only ignore-scripts inspection does not prove prepack scripts, tests or a normal install passed.

### 2. Design analysis

Test the built tarball/skill archive in a temporary installation layout, including the validate-or-fix dependency on shared runtime files. Validate internal resource references and executable modes on each supported platform. Do not derive package completeness from the source tree alone or from a ZIP that omits required empty directories.

### 3. Design analysis

Managed installation hashes protect local edits. Upgrade must compare expected old/source/installed variants, stage changes, validate and commit atomically where possible, with rollback on failure. Never overwrite user-specific SKILL.md or global routing config to make an installer test succeed.

### 4. Design analysis

CI should run untrusted changes with read-only permissions and keep publishing credentials isolated from test execution. Pin dependency/action identities according to supported repository policy. Archive only necessary logs with redaction and retention; do not export the entire home directory, provider session cache or plan workspace.

The analysis above is a repository design synthesis. The linked publications establish capabilities or bounded empirical observations, not this skill's future measured performance. Exact account behavior and installed-version compatibility remain implementation-time checks.

| Alternative | Benefit | Cost / failure risk | Disposition |
|---|---|---|---|
| Trust source allowlist only | Fast | Misses actual pack rules and generated files | Reject |
| Run all lifecycle scripts for every inventory query | Closer to release | Slow and potentially effectful | Use only explicit release validation |
| Pack-manifest plus isolated install tests | Checks real artifact and dependency layout | Needs separate evidence for each mode | Recommended |
| Force reinstall over local edits | Simplifies update | Destroys user customizations | Reject |

## Ownership and scope boundary

This implementation owns its declared write scope and acceptance tests. Its following review checks the actual changed code; prepared research is not acceptance evidence.

Implementation may preserve an already-satisfied invariant with a regression test and a documented no-change rationale; do not add code solely to make every recommendation produce a diff.

## Implementation instructions

1. Define the minimal intended npm/skill file manifest and exclude planning controls, research execution logs, credentials, caches and transfer artifacts.
2. Test npm pack --dry-run --json against that manifest, and test actual staged skill ZIP membership and size. A .gitignore alone is not the packaging contract.
3. Preserve source/installed hashes for activation transforms and refuse overwrite/uninstall of local edits unless explicitly authorized.
4. Add compatible version checks for companion resolution, including missing and mismatched installations, while preserving supported old layouts.
5. Keep CI permissions minimal and include supported Node/Python plus Windows/POSIX behavior. Report skips and unsupported platform cases rather than a single unqualified pass.
6. Check actual pack manifests for required runtime files and forbidden plans, receipts, credentials and logs.
7. Separate ignore-scripts metadata inspection from full lifecycle validation and test the extracted distributable layout.
8. Preserve local installation edits and rollback failed upgrades without changing global configuration.

## Acceptance and counterexamples

- No native plan, private log, .env, bytecode or node_modules entry appears in a distributable archive.
- Selective-explicit-selective round trips retain correct hashes and policy metadata.
- A locally edited installed file prevents automatic replacement/removal.
- Companion packages resolve a matching shared runtime after a clean temporary install.
- CLI/docs/version constraints and actual package contents are checked without publishing.
- A nested planning file is rejected even when docs is included in package files.
- Both skills resolve shared runtime resources after clean temporary installation.
- An edited installed SKILL.md prevents overwrite without explicit force authorization.
- Metadata-only pack evidence cannot be reported as a full prepack or test pass.

## Cost, latency and quality decision

Keep cheap manifest checks in normal validation and reserve full lifecycle/install matrices for release boundaries; measure package size, install latency and update correctness.

Compare total cost per independently validated outcome against the current implementation and a simpler qualified single-worker baseline. Count failed attempts, reviews, cache writes/reads, advisory calls and tool/runtime overhead in their native units. Unknown prices, quotas or usage remain unknown, not zero. Preserve capability and security floors; no automatic rollout follows from fixture replay alone.

## Evidence used in this revision

- [W-NPM] npm, [npm pack](https://docs.npmjs.com/cli/v12/commands/npm-pack/). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-ACTIONS] GitHub, [Secure use of GitHub Actions](https://docs.github.com/en/actions/reference/security/secure-use). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-SKILLS] Agent Skills, [Agent Skills specification](https://agentskills.io/specification). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-LOGGING] OWASP, [Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

Prior-round context: [E048], [E049], [E055], [E001], [E058]. See `SOURCE_REGISTER.md` for records; these were not all independently refreshed.

Search themes inspected in this round: npm pack dry-run json files ignore scripts lifecycle; GitHub Actions secure use pin full SHA permissions; Agent Skills package resources specification.

## Unverified limits and refresh triggers

- No npm publication, account skill installation or global configuration modification is authorized or performed by this research task.
- No registry publication, user installation or Windows execution was performed. Future release acceptance requires real artifact checks on declared supported platforms.

No authenticated provider invocation, live quota/cost benchmark, independent model review, or Windows runtime test was performed in this research revision.

Refresh only evidence contradicted by the installed CLI, selected account/billing plan or changed code contract. Unknown required capability blocks that candidate; it does not justify widening permissions.
