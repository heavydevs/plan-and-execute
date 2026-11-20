# Architecture study — ChatGPT-native executor for long-running PAE tasks

**Study date:** 2026-11-20. **Scope:** the branch `checkpoint/plano1-estudo-provider-switch-20261028` in [heavydevs/plan-and-execute](https://github.com/heavydevs/plan-and-execute). This is an adaptation for chat-hosted tools and ephemeral containers, **not** the claim that ChatGPT has the Codex CLI or a hidden external reviewer. The plan remains authoritative; the helper is a transport and execution bridge, not a new skill or plan.

## Concrete environment and requirements

At study time this chat had working connected GitHub read/write Git-object tools, Python 3.13 and node in an isolated container, but **no GitHub DNS/checkout** and **no codex/claude CLI or API credentials** in that container. A different future ChatGPT environment may differ, so always run `doctor`. The preinstalled skill files are older than the checkpoint branch and **must not** be used to claim current-branch tests. The repository's source tree, Python tests, native `resource_watch.py`, `review_dispatch.py`, deliverable receipts and manifest exist remotely.

### Data and trust flow

```text
AGENTS.md -> .ai-work/chatgpt-executor/ENTRYPOINT.md
                  | implement      | review       | validate
                  v                v              v
               PLAYBOOK.md      REVIEW.md       taskctl.py
                  |                |              |
          GitHub connector   independent       local checkout
          blob/tree/ref CAS  dispatcher        resource_watch
                  |                |              |
                  +------> exact commit SHA <--+
                              | optional remote runner on push
                              v
                   GitHub Actions (read-only checkout)
                              |
                      exit codes + artifacts
                              v
                 original acceptance/delivery gates
                              |
                      planctl authoritative state
```

**Boundary 1 (read/write):** the GitHub connector transports source and commits using expected HEAD comparisons. It cannot execute code or create model sessions. Prevent lost updates with base-tree + expected head; never force push. Never infer a local checkout or passing test from GitHub file availability.

**Boundary 2 (execution):** local shell runs only against **exact** repository checkout; if offline, use a branch-push GitHub Actions workflow to execute the full checkout on the remotely reported commit. `taskctl.py` reads task-scoped inputs, runs approved argv commands with `shell=False`, bounds time and log size, saves immutable-ish evidence (hashes, command, exit, OS). GitHub Actions uses `permissions: contents: read`, checks out only the triggering SHA, and uploads logs. Do not expose write credentials or service secrets to test programs. Python process group kill is best effort; cannot prove isolation against code deliberately escaping its group. GitHub-hosted runner is not a sandbox for adversarial code supplied by an attacker with access to workflow edits. Use trusted contributors and branch protection.

**Boundary 3 (review):** *quality checks are not reviewer identities*. Deterministic, same-session code review is useful and can produce findings/regressions but does not satisfy task 015's `review_dispatch.py` fresh max-tier external reviewer. The optional external backend runs only if genuine authorized CLI/API credentials are present; otherwise task state remains pending. GitHub CodeQL/human PR review may supply supplemental scrutiny, but the original contract still controls delivery. Never instantiate a "fake model" or forge session/usage.

**Boundary 4 (state):** manifest/schema-4, TODO projection, original task Sxxx and receipts remain authoritative. `taskctl.py` **never writes them**. The repo's `check_delivery.py` and receipt validator remain final authorities. Research reports, static inspections and ChatGPT outputs are input evidence, not executed checks.

### Proposed capabilities and fallback routes

| Environment | Edit/commit | Deterministic tests | Independent review | Permitted outcome |
|---|---|---|---|---|
| GitHub connector + full local repo + authorized reviewer | CAS or git | local + watcher | native dispatcher | complete if original delivery gate passes |
| GitHub connector + remote GitHub Actions + reviewer | CAS | CI on exact SHA | native remote reviewer if configured | complete only after validating all receipts |
| GitHub connector + Actions, **without** reviewer | CAS | CI | unavailable | publish tested partial fix; task pending |
| GitHub connector, **no** shell/Actions | CAS | unavailable | unavailable | publish documentation/patch, mark evidence missing |
| No connected GitHub + local checkout | local commit only | local | optional if authorized | no remote push claim |

**Fallback does not silently weaken requirements.** User-approved changes to the task's review requirement would need a valid plan revision; this helper will never make that decision autonomously. The `gate` command intentionally refuses to approve third-party dispatch JSON without the repository's original delivery gate: a JSON file can be forged.

### Alternatives considered

| Architecture | Main upside | Weakness | Choice |
|---|---|---|---|
| Invoke an unavailable CLI with a fabricated stub | Looks compatible | Fabricates model and safety evidence | **Reject** |
| Use installed packaged skill copy as a checkout | Immediately executable | Differs from branch; stale tests and results | **Reject** |
| Broad new autonomous orchestration engine | Full customization | Duplicates manifest/receipts, high maintenance, higher token spend | **Reject** |
| Store whole repo in chat context | Minimal tools | Context waste, leakage and incorrect file versions | **Reject** |
| **Small local controller + GitHub object CAS + CI execution + existing reviewer protocol** | Real tests and reproducible source, low code duplication | Cannot manufacture external reviewer or credentials | **Selected** |
| API-based reviewer/provider in Actions (future) | Automated isolated model reviewer | Requires opt-in secrets, cost/quota and careful prompt/data safety | Optional adapter, not implemented or claimed |

### Security and performance invariants

- Only `TASK_INPUTS.json` selected task and its declared argv (for now `python`/`node` script) can run in `targeted` mode. Reject shell flags, `-c`, `..`, symlinks and absolute escapes. User code is not automatically trusted; execute only in permitted repo/CI sandbox.
- Bound each check's duration; terminate owned process group, collect exit codes and full logs by file (not in model prompt). Log limit needs output redaction and storage quotas; production deployment should truncate/rotate logs while recording truncation. Credentials never in argv or evidence packet.
- Fail closed if map/toolchain is absent, validation command unrecognized, expected file missing, source hash changes while tests run, run SHA differs from reviewed SHA, review is missing, or original receipt cannot be verified.
- For long suites, execute the required full pass once, collect **all** failing cases, run focused repairs, then rerun full pass. Favor many hermetic unit/contract tests and a few higher-level tests. Record test failures without repeatedly re-running healthy tests.
- Keep research/architecture in durable Markdown and runtime evidence in `.ai-work/chatgpt-executor/runs/` excluded from Git. No memory of earlier chats is authoritative. Use URLs and content hashes; skip full histories, duplicative logs and API spend on trivial transforms.
- Treat GitHub workflow results and custom runner logs as bounded evidence for **specific commit**, not as universal proof. Be explicit about unavailable Windows/macOS/platform tests.

## Verification design and gate logic

`python .ai-work/chatgpt-executor/taskctl.py self-test` executes 4 hermetic safety tests (path denial, scoped commands, fail-closed review gate, nonzero failures). In a checkout, `run-checks --mode targeted --task 015` runs the 7 declared tests in task inputs as a fast diagnostic; `--mode watcher` executes both original resource watcher IDs `P1_TESTS_015`, `P1_015`. GitHub Actions can do both on the exact pushed branch snapshot; it reports the triggering head SHA. There must be a separate successful independent dispatch of final hashes before any plan status or receipt changes.

The static/source-gate proof applies only to local code. It is **not** a second-model review. `taskctl gate` reports missing validation/reviewer and **always defers reviewer integrity to original delivery gate**. This is intentional conservatism. The original test commands will run later via CI, not in the current isolated checkout-less container.

## Bibliography and research limits

1. [GitHub REST Git Trees API](https://docs.github.com/en/rest/git/trees), authoritative create-tree/base-tree and Git object semantics (accessed 2026-11-20). Does not guarantee application-level multi-file atomicity outside one commit.
2. [GitHub Actions workflow syntax: push branches](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax), GitHub, accessed 2026-11-20; a branch-specific push workflow can execute on runner checkout.
3. [GitHub Actions event triggers](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows), GitHub, accessed 2026-11-20; a **workflow_dispatch-only** file must exist on default branch, so this prototype uses push on the checkpoint branch.
4. [GitHub REST workflow runs](https://docs.github.com/en/rest/actions/workflow-runs), GitHub, accessed 2026-11-20: link run conclusion to its `head_sha`, avoid accepting a passing run from a different commit.
5. [Python subprocess](https://docs.python.org/3.13/library/subprocess.html), Python 3.13, Security Considerations and Timeouts. `shell=False`, explicit argv and cleanup on timeout.
6. [NIST SP 800-218 SSDF, PW.7.2](https://nvlpubs.nist.gov/nistpubs/specialpublications/nist.sp.800-218.pdf), NIST 2022, code analysis, peer review, triage and repeatable evidence; distinct reviews cannot be manufactured.
7. [Google Engineering Practices — reviewer guidance](https://google.github.io/eng-practices/review/reviewer/looking-for.html), checks for design, correctness, tests and maintainability; guidelines, not a measured reviewer substitute.
8. [Martin Fowler — Test Pyramid](https://martinfowler.com/bliki/TestPyramid.html), 2012, balance inexpensive deterministic tests with sparse broad-stack tests; heuristic, not a PAE benchmark.
9. [OpenAI — Using Codex Cloud](https://help.openai.com/en/articles/20001545-using-codex-cloud), updated Nov 2026, optional separately configured managed workspace. **Not a CLI/API connector implicitly available in this chat**.
10. [OpenAI — Codex GitHub Action](https://learn.chatgpt.com/docs/github-action), optional future integration; requires explicit `OPENAI_API_KEY` GitHub secret and authorized expenditure. Not installed or configured here.
11. [GitHub artifact attestations](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations), supported provenance mechanism, unnecessary to enable for first local-only text receipts.
12. [Python unittest docs](https://docs.python.org/3/library/unittest.html), deterministic standard-library fixture model used in executor self-tests.

**Evidence limitations:** No external provider call, cross-platform benchmark, remote Actions run, or authenticated independent review was performed by the research phase itself. Actual CI conclusions, if available after commit, must be appended as observed evidence rather than predicted.

## Audited resource-map reconciliation, 2026-11-20

The original map was observed stale on GitHub Actions because of 36 specific changed test/build/CI inputs, not because a required test failed. `.ai-work/chatgpt-executor/mapctl.py` imports the original `service_map.py`, requires the original index, checks only the explicitly inspected 36 changed paths and confirms both 015 validation IDs before restamping in a temporary GitHub Actions checkout. Unknown paths or malformed inventories abort; no blanket `stamp` is allowed. The CI artifact includes the updated map and index so their **exact** content can be published through GitHub CAS; the repository map is not considered reconciled until that content is committed. This procedure is independent of, and never substitutes for, an external model review.

## Optional Responses API reviewer (implemented, not executed)

`.ai-work/chatgpt-executor/api_review.py` implements a bounded, synchronous read-only OpenAI Responses API model review through stdlib `urllib` with fresh response ID, actual model, usage and SHA-256 inputs. It is **disabled without** `OPENAI_API_KEY` and `--dry-run` sends nothing. It sets `store=false`, demands structured JSON and rejects fabricated/contradictory verdicts, changed hashes, unavailable sources or oversized contexts. Default model `gpt-6.2-astra` from the current [OpenAI API overview](https://platform.openai.com/overview); caller may override a verified eligible model. Explicit API credentials and paid use require operator setup; ChatGPT account access does not supply an API key. This is a possible substitute for a missing CLI for **future approved plans**, but its receipt uses a distinct schema and **does not satisfy 015's existing `review_dispatch.py` contract** without a formal plan gate change. The optional adapter has only mocked/offline tests in this research/implementation session.