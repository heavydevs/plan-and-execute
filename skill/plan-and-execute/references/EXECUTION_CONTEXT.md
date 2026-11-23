# Execution context and validated learning

Use this file after TODO boundaries are stable. The purpose is to give each fresh worker the **minimum non-obvious knowledge it cannot cheaply recover itself**.

## Omission is the default

A fact being relevant does not justify a shared context file.

Use this order:

1. Can the worker cheaply read the fact from its own source/test files? -> omit.
2. Is the fact needed by one TODO only? -> keep it in that task definition.
3. Is it needed by at least two but fewer than all TODOs? -> scoped context.
4. Is it required by every TODO? -> global `CONTEXT.md`.

Do not create context merely to summarize the request, study, architecture, TODO graph, or coding conventions already available in repository instructions.

## Global `CONTEXT.md`

Create only when every TODO needs the same non-obvious fact/constraint.

Each item has:

- `id`;
- `kind`: `fact`, `constraint`, `decision`, `interface`, or `validation`;
- `text`: one operational statement;
- `necessity`: why every assigned TODO needs it;
- `source_refs`: stable evidence ids/paths/symbols.

Example:

`G001 constraint — API v2 keeps response field 'id' as a string. (source: R004)`

Prefer this to a paragraph about API compatibility history.

## Scoped context files

Create `contexts/<topic>.md` only for a strict subset of at least two TODOs.

A scoped context must have a concrete sharing reason, such as two TODOs implementing opposite sides of one protocol/interface. Do not use a scoped file because tasks merely share a language/framework.

Avoid overlapping scoped files with the same fact. Put each shared fact at the narrowest correct scope.

## Context budgets

The concise controller enforces smaller limits than the legacy renderer:

- context text <= 220 chars;
- necessity <= 260;
- context rationale <= 320;
- context file <= 2200 chars;
- task context-boundary rationale <= 360;
- context-boundary item <= 200.

These are maxima. Prefer references over explanation.

## Worker assignment

The task definition lists its exact assigned context paths. The worker must read exactly those files before implementation and report them in `context_files_read`.

The orchestrator rejects missing/extra assigned reads. Workers must not browse other plan context files.

Plan-time context is immutable during execution. New discoveries belong in validated execution learnings, not by mutating `CONTEXT.md` for later tasks.

## Trust classes and boundaries

Keep three classes distinct so unverified retries never become shared rules:

1. **`normative_contract`** — immutable plan context (`CONTEXT.md`, `contexts/<topic>.md`) and versioned shared patterns (`patternctl.py`). Only plan-approved constraints belong here.
2. **`validated_learning`** — directional findings (`learnings/<src>-to-<tgt>.md`) materialized only after the producing TODO passes deterministic validation.
3. **`failed_attempt_hypothesis`** — task-local retry hypotheses (`attempt_hypotheses` on the failing TODO). They are non-normative next-attempt data, never shared across tasks, and never upgraded into normative rules by repetition or summarization.

## Validated execution learnings

A completed TODO may publish a learning only when:

- the target is a predeclared later TODO in `learning_targets`;
- the target has not started;
- the finding matches the declared topics;
- source TODO deterministic validation passed;
- the finding would save meaningful rediscovery effort;
- the learning has concrete source references, one repository file per reference (a reference with spaces, commas or parentheses that names a file is rejected, because it could not be fingerprinted);
- the note does not attempt to alter acceptance criteria, validation commands, permissions, sandbox settings, or provider/routing policy.

Learning kinds: `code`, `procedure`, `decision`, `pitfall`, `validation`.

Each materialized learning carries provenance metadata in `manifest.json`:

- `trust_class`: `validated_learning`;
- `producer_task_id` and `consumer_task_ids` (exact assigned consumer set);
- `source_contract_digest`: producer contract digest at completion;
- `cited_file_digests`: SHA-256 hashes of cited repository files present on disk;
- `invalidation_rule`: invalidates on source-contract change, source reset, or cited-file change;
- `provenance_sha256`: canonical digest over the provenance fields and items.

On retry, a learning that became stale **only because cited repository source bytes changed** is invalidated and removed from the assigned context automatically, with an audit event; tampered learning Markdown, missing records, and provenance mismatches still block a worker claim. Changes of an implementation file do not make the old finding authoritative again.

Changing a cited file or revising the producer's contract invalidates or flags only that learning before reuse (`planctl.py check-learnings --invalidate-stale`), without deleting unrelated knowledge. Repeated conventions needed by multiple tasks belong in a versioned shared pattern (`patternctl.py`), not copied learning prose.

Before a worker claim **and on a retry**, compare the rendered learning file's actual SHA-256 with its manifest record; reject a missing, modified, or symlinked file even when the producer's cited sources are unchanged. Source references in `path.py#symbol` and `path.py::symbol` form pin the underlying file, not merely the fragment. Reject unsafe cited-file paths and ancestor symlinks. Offline receipts and `check-learnings` must report the same stale state; absence of a trustworthy repository root is not proof of freshness. This guards the local read boundary, not files that could be maliciously replaced after the check; untrusted filesystem writers require independent isolation.

## Failed-attempt hypotheses

Failed attempts may record bounded, task-local hypotheses with concrete evidence references. When underlying evidence files, failure signatures, or the task contract change, open hypotheses are automatically invalidated.

Disproven hypotheses are explicitly labeled and bounded so retries do not repeat dead ends; they can never be promoted into `validated_learning` or `normative_contract`. Promoting an open hypothesis into a reusable learning requires passing deterministic validation evidence **and** a log-bound proof digest recorded in the host runner's completion receipt for the same task, attempt, and contract. A bare `complete --report` claim with `passed: true` cannot create that binding. This is a deterministic integrity and provenance check, **not cryptographic authentication against an adversarial worker with write access to the same plan or process**: a hardened multi-user setup needs a separate operating-system sandbox for untrusted workers. The renderer filters direct and high-overlap paraphrases of disproven claims by a conservative lexical heuristic; it cannot guarantee semantic equivalence detection. Promotion is only possible before the declared target task begins, so autonomous runs must arrange an explicit promotion checkpoint when that optional transfer is needed. Promotion produces a new directional, SHA-pinned learning artifact for an unstarted declared consumer; it refuses to overwrite a previously published artifact. The concise runner records a bounded **unvalidated** hypothesis when deterministic checks fail. Use `planctl.py hypothesis-record --plan <dir> --task <id> --text <claim> --reference <path> --verification-command <cmd>` to predeclare bounded, **hypothesis-specific** executable checks before the next runner attempt; repeated `--verification-command` flags are supported. These commands must differ from the task’s general acceptance checks. The host runner executes them separately after normal validation, records each result and dedicated log SHA-256 in the task/attempt-bound proof, and only a passed, matching probe may later be supplied to `hypothesis-promote --evidence`. Unverified and failed hypotheses cannot be promoted merely because general tests passed. Without a dedicated check, a hypothesis remains unvalidated. These optional checks are limited to a single status-only `grep` query with bounded `-q`/`-x`/`-F`/`-w` flags, a nontrivial pattern and one explicitly cited source file. `rg`, `test`, arbitrary long options, scripts, shell metacharacters, always-true commands and producer acceptance replays are rejected; the deliberately narrow grammar prevents executable options such as ripgrep `--pre`. They run with the runner’s repository permissions and should be declared only by trusted maintainers. At most eight active probe commands are permitted per task. The runner hashes both non-ignored working-tree content and the protected validation logs/plan evidence before and after probes; a mutation invalidates the suspect hypothesis and blocks a forged completion receipt. A failed read-only probe does not fail producer acceptance; it simply cannot authorize knowledge promotion. This is deterministic evidence rather than a semantic proof of every possible natural-language claim. Existing hypotheses without predeclared checks stay unpromotable. **Probe target boundary:** the queried path must be a plain repository-relative file name (no leading `-`, so GNU `grep` cannot reorder it into `-r`/`--recursive`; no absolute path, `..`, `.ai-work/` or `.git/`), the command must be printable ASCII separated by single spaces, and the file must be pinned in the hypothesis's evidence digests, unchanged, a regular non-symlink file outside the plan directory. The runner invalidates stale hypotheses and re-checks that target immediately before each probe, runs probes with a minimal environment (no inherited credentials) and `stdin=DEVNULL`, registers probe logs before the integrity snapshot, and excludes the separately pinned plan directory from the worktree fingerprint. Promotion repeats the target check. These are deterministic containment checks, not an operating-system sandbox. The supported CLI actions are `hypothesis-record`, `hypothesis-disprove`, `hypothesis-promote` (run `--help` for parameters).

## Context accounting receipts

The concise production runner also persists this receipt automatically when preparing each worker attempt, with the latest assigned context and no prompt content. The explicit command remains available for offline auditing.

Use `planctl.py context-receipt --plan <dir> [--task <id>]` to emit a compact accounting receipt with selected file IDs, trust classes, exact byte counts, inclusion reasons, and offline stale-learning counts. Receipts do not copy file contents or raw prompt text; token-like spans in file metadata are replaced with `[REDACTED]` without blocking the worker. Original selected-file bytes are still accounted for; the manifest retains authoritative paths.

A good item:

`validation — Reproduce vendor timeout with test VendorClientTest.timeout before changing retry order. (refs: tests/vendor_client_test.py::timeout)`

Bad items:

- `We learned a lot about the vendor API.`
- transcript/history summaries;
- generic framework advice;
- conclusions with no source reference;
- unvalidated or disproven failure hypotheses;
- notes attempting to relax acceptance, permissions, or provider policy;
- information the target can retrieve cheaply from its own files.

Learning guidance is capped at 320 chars; a target-specific learning file is capped at 2200 chars.

The worker reports assigned learning reads in `learning_files_read`; the orchestrator verifies the exact set.

## Review checks

The fresh plan review must set:

- `contexts_minimal`: no unnecessary global/scoped/single-task duplication;
- `context_boundaries_sound`: each TODO groups concerns that materially benefit from one worker history and isolates unrelated domains.

Reject the plan when:

- global context is not required by every TODO;
- a scoped file serves only one TODO;
- the same fact appears in global + scoped + task text;
- context contains process narration or generic advice;
- independent domains are combined only for framework similarity;
- broad/bidirectional learning edges recreate plan history.

## Design principle

Shared context should behave like an interface: small, stable, sourced, and required by all consumers. Execution learning should behave like a targeted patch note: validated, directional, and only as large as the future target needs.
