# Selective activation routing

Use this reference only when DIRECT vs ORCHESTRATED is ambiguous, when evaluating routing quality, or when maintaining the skill metadata. The normal gate lives in `SKILL.md` so a false-positive invocation can exit without loading this file.

## Objective

Minimize false-positive orchestration without losing durable handling for genuinely long-horizon work. The asymmetric default is deliberate: uncertainty -> DIRECT; later evidence -> PROMOTE; explicit user invocation -> ORCHESTRATED.

Planning too early spends tokens immediately. Starting direct is recoverable because the task can be promoted once the benefits of persistence/isolation are observable.

## Strong orchestration signals

One strong signal can be sufficient when material:

1. **Independent workstreams** — two or more outcomes have different invariants, files, debugging evidence, or validation boundaries and would not benefit much from sharing one conversation history.
2. **Broad study** — architecture cannot be chosen safely without broad repository inspection or substantial authoritative external research.
3. **Cross-cutting risk** — migration, compatibility, data integrity, security, concurrency, protocol/schema evolution, or multi-module ownership needs durable coordination.
4. **Durable resume value** — expected duration/session count, quota risk, or handoff requirements make disk-backed checkpoints materially useful.
5. **Isolation value** — fresh workers prevent unrelated context from polluting independent leaves or enable clean deterministic verification.

## Negative triggers

Do not orchestrate solely because a request:

- says `implement`, `fix`, `refactor`, `test`, `CRUD`, or `feature`;
- edits many files that all implement one cohesive behavior;
- requires ordinary local repository search;
- has several sequential steps that strongly reuse the same context;
- is medium-sized but can be implemented and validated in one healthy agent context.

Examples that usually remain DIRECT:

- add one API behavior across DTO, service, controller, migration, and focused tests;
- rename/update one helper across many mechanical call sites;
- fix a bounded bug and add regression tests;
- refactor one cohesive module without compatibility/migration uncertainty.

Examples that usually ORCHESTRATE:

- implement unrelated person and store domains with independent business rules and tests;
- migrate authentication, billing, and audit while preserving compatibility;
- compare external storage approaches, research authoritative docs, then change multiple independent subsystems;
- execute a multi-session implementation expected to survive provider quota exhaustion.

## File-count rule

**File count is weak evidence.** Count semantic outcomes and context boundaries, not files. Twenty mechanical edits can remain DIRECT; six files across three independent domains can justify ORCHESTRATED.

## Context-pressure rule

**Context pressure is secondary evidence.** Context usage is a secondary promotion signal. If a host exposes a reliable percentage, treat roughly 75-85% as an early-warning zone for **evaluation**, not an automatic trigger. Promote only when substantial work remains and durable handoff/isolation has value.

Claude Code currently exposes `context_window.used_percentage` to status-line scripts and supports compaction lifecycle hooks. Use those capabilities only as optional host signals; never make the portable workflow depend on them. Other hosts may expose different metrics or none.

Do not install hooks or alter host configuration automatically merely to observe context pressure.

## Evaluation corpus

`routing-evals.json` is a maintained corpus with positive routes and **near-miss negatives**. It intentionally includes direct examples with words such as implementation, refactor, tests, and multiple files so the description does not regress into a catch-all.

When changing `SKILL.md` metadata or this gate:

1. run `routing_self_test.py`;
2. evaluate representative prompts in both Claude Code and Codex when practical;
3. track false-positive rate first, then false negatives;
4. add every discovered routing regression to the corpus.

A routing eval must not judge implementation quality. Its only question is whether paying the orchestration overhead was justified at the request boundary.

## Plan-free validation is not promotion

DIRECT may invoke `validate-or-fix` for mapped, long-running or uncertain tests. It creates only the shared resource map and bounded receipts in `.ai-work/validation/`, not a plan, study, manifest, TODO or active pointer. Do not load orchestration references for this exception. Simple fast checks remain direct. See [VALIDATION_WORKLOADS.md](VALIDATION_WORKLOADS.md) only when supervision is needed.

## Route decision and capability separation

- **No extra classifier call:** `requestctl.py evaluate-route` evaluates request and repository metadata deterministically without spending an LLM classifier call.
- **Bounded reason codes in selected workflows only:** Record bounded `reason_codes`, `estimated_working_set`, and `remaining_outcomes` only inside an activated `ORCHESTRATED` or `PROMOTE` workflow. A rejected implicit match (`DIRECT` or exact lifecycle/config command) creates no plan, ledger, study, or reason-code files and loads no orchestration references.
- **Routing mode vs. capability tier:** Keep `DIRECT` vs. `ORCHESTRATED` independent of `model_tier` and `reasoning_effort`. A small cohesive security-sensitive fix stays `DIRECT` without creating plan artifacts while preserving a qualified (`strong`/`high`) capability route.

## Offline and host evaluation

`requestctl.py eval-corpus` and `routing_self_test.py` measure entrypoint bytes and an **offline cue-extractor proxy**: plan-creation false positives/negatives of selective, explicit-only, all-direct and always-orchestrate routing on the tuning and held-out splits of `routing-evals.json`. Hosts select the skill from metadata, so the proxy is not host activation. The paid classifier and all cost terms stay unmeasured, not zero. Exact lifecycle/config commands (`$plan-and-execute status`, `pae current`, ...) are checked before invocation; a file path containing the skill name is not an invocation.

The held-out split is valid only for the cue table hash recorded in `held_out_protocol`. Never tune cues to a held-out miss; after a cue change, move seen cases to tuning, have fresh prompts written without the table, and re-record the hash and ceilings. Live host skill loading and latency require owner-confirmed authenticated runs; otherwise record them as an unmeasured limitation.
