# 058 - Log Lifecycle: research revision 2

Date: 2026-10-28. Feature: `F027`. Implementation TODO `058`; independent review TODO `059`. Product baseline: `0.11.0` / tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Prepared design evidence, not implemented code. Implementation and independent review remain pending.**

## Recommended direction

Use identity-aware incremental log readers, provenance-preserving bounded digests and owner-scoped retention; never delete evidence merely because an agent has already read it.

This is a conditional engineering recommendation for this repository, not a proof of a global optimum or a measured saving on the user's workload.

## Change from the previous report

The revision specifies rotation and partial-record semantics and rejects read-based deletion. It adds a tri-state coverage result so truncated or unreadable logs cannot become a false healthy verdict.

The previous report is retained under `docs/plans/20261028-skill-optimization/history/research-round-1/prepared-research/` for audit. New W-prefixed sources below are the current-round evidence; old E-prefixed sources remain background.

## Questions and repository evidence

- Measure cursor gaps, rotation/truncation, bounded summaries and missed-error risk.
- Prune owned stale artifacts without deleting active diagnostic evidence or rereading entire logs.

**Baseline observations:**
- log_watch.scan tracks file device/inode and byte offset, keeps incomplete trailing lines for the next sample and reports skipped bytes with exit2.
- digest reads a bounded prefix and reports truncation/omission. A small digest is not evidence that the entire source log was inspected.
- The scan output truncates matching lines before any shared secret redactor is applied in that function; model-facing consumers need a defined sanitation boundary.

All listed file hashes matched the preserved 0.11.0 source in this revision. This is integrity checking, not a second full code audit.

| Code anchor | SHA-256 | Selected symbols / location |
|---|---|---|
| `skill/plan-and-execute/scripts/log_watch.py` | `114ea5c9c0ef6db6523e4fd7ea41faf2a8e9464968f3a8527738cec6321d3aaf` | scan:58; digest:135 |
| `skill/plan-and-execute/scripts/resource_watch.py` | `22ac707b846a428c832671c6cfc96d9e45b367f5b3a61963ac0258791a5c2184` | register_artifact:62; cleanup_artifacts:84 |
| `skill/plan-and-execute/scripts/observer.py` | `ad84f96624f85c860edd925ed5bf354dc805b726f943bf14a435f6ef5179b322` | ObserverError:37; Unavailable:41; validate:47; options:58 |

## Deeper analysis and competing approaches

### 1. Design analysis

An offset alone is not enough to resume reading a log. Bind the cursor to file identity and observed generation, detect truncation, and choose whether to follow the descriptor or the pathname after rotation. Carry incomplete UTF-8 sequences and partial lines without double-counting or discarding evidence.

### 2. Design analysis

Summaries should preserve event counts, first/last timestamps, representative redacted signatures and references to the underlying byte ranges. A bounded digest must report dropped groups, omitted records and incomplete coverage. Absence of a recognized error in a truncated input is unknown, not proof of a healthy process.

### 3. Design analysis

Redact before truncating, hashing diagnostic excerpts or exporting them to a model. A token split across chunks can defeat a naive per-chunk pattern; retain a bounded overlap or classify safe structured fields at the source. Escape control characters in rendered summaries to avoid log injection. Hash identifiers are not automatically anonymous if the original domain is small.

### 4. Design analysis

Retention is an ownership and incident-policy decision, not a token-optimization command. Keep raw evidence outside routine prompts, rotate owned temporary logs under documented limits, and retain failures until acceptance or explicit user policy allows cleanup. Never purge user service logs or unknown files to avoid rereading them.

The analysis above is a repository design synthesis. The linked publications establish capabilities or bounded empirical observations, not this skill's future measured performance. Exact account behavior and installed-version compatibility remain implementation-time checks.

| Alternative | Benefit | Cost / failure risk | Disposition |
|---|---|---|---|
| Reread full logs every poll | Simple | Repeated I/O, tokens and secrets | Reject |
| Delete logs after reading | Small next prompt | Destroys evidence and user data | Reject |
| Incremental cursor plus bounded digest | Low repeated work and traceability | Needs rotation/coverage contracts | Recommended |
| LLM-only summarization | Handles free text | Cost, omissions and anchoring | Optional on sanitized novel ambiguity |

## Ownership and scope boundary

This implementation owns its declared write scope and acceptance tests. Its following review checks the actual changed code; prepared research is not acceptance evidence.

Implementation may preserve an already-satisfied invariant with a regression test and a documented no-change rationale; do not add code solely to make every recommendation produce a diff.

## Implementation instructions

1. Represent read coverage with start/end offsets, file identity, truncation/rotation events and omitted ranges. Do not convert a partial scan into a healthy result.
2. Test move/create and copytruncate rotation, same-size replacement, partial UTF-8 and very long lines. Choose explicit replay/deduplication policy for each case.
3. Apply sanitation before model-facing truncation and preserve bounded safe error signatures. Keep full raw logs only in owned access-controlled storage, not in prompts or packages.
4. Resume from cursor/digest checkpoints instead of rereading entire logs. Cursor corruption or uncertain identity should produce visible uncertainty and a bounded recovery path.
5. Prune only registered stale artifacts after acceptance and retention checks. Never let an observer delete active application logs or erase evidence needed by an unresolved failure.
6. Bind log cursors to file identity/generation and handle rotation, truncation, split UTF-8 and partial lines explicitly.
7. Expose incomplete coverage, dropped groups and unreadable inputs; no-error is not healthy when coverage is incomplete.
8. Retain only owner-approved cleanup rules; never delete a user log because it was already read by an agent.

## Acceptance and counterexamples

- An error split across two writes is detected once the line completes.
- An omitted interval yields a coverage-gap status, never a claim of no errors.
- Rotation/replacement does not inherit an unrelated offset silently.
- A planted credential at a truncation boundary is absent from model-facing excerpts.
- Cleanup preserves active/unresolved evidence and rejects unregistered paths and symlinks.
- Rename rotation and copy-truncate do not silently skip or duplicate complete records.
- A secret split across read chunks is removed before digest truncation.
- A truncated log with no observed error reports incomplete coverage.
- Cleanup refuses arbitrary external logs and preserves failure evidence.

## Cost, latency and quality decision

Aim for O(new bytes) repeated reads with bounded memory and model input. Measure detection recall and coverage alongside compression ratio; a smaller wrong digest is not a gain.

Compare total cost per independently validated outcome against the current implementation and a simpler qualified single-worker baseline. Count failed attempts, reviews, cache writes/reads, advisory calls and tool/runtime overhead in their native units. Unknown prices, quotas or usage remain unknown, not zero. Preserve capability and security floors; no automatic rollout follows from fixture replay alone.

## Evidence used in this revision

- [W-TAIL] GNU Coreutils, [tail invocation](https://www.gnu.org/s/coreutils/manual/html_node/tail-invocation.html). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-LOGGING] OWASP, [Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-SRE] Google SRE Workbook, [Monitoring](https://sre.google/workbook/monitoring/). Accessed 2026-10-28. Reading scope: Public book chapter monitoring sections inspected; not a claim of reading the whole book. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-SUBPROCESS] Python Software Foundation, [Subprocess management](https://docs.python.org/3/library/subprocess.html). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

Prior-round context: [E046], [E044], [E045], [E043]. See `SOURCE_REGISTER.md` for records; these were not all independently refreshed.

Search themes inspected in this round: GNU tail follow descriptor name log rotation truncation; OWASP logging sensitive data retention log injection; streaming logs partial utf8 bounded buffers.

## Unverified limits and refresh triggers

- Secret redaction is best effort, not a proof that arbitrary raw application output is safe to disclose. Sensitive logs may require stronger policy or no model access.
- No real production log corpus was supplied. Synthetic compression results cannot predict token savings or diagnostic recall for every service.

No authenticated provider invocation, live quota/cost benchmark, independent model review, or Windows runtime test was performed in this research revision.

Refresh only evidence contradicted by the installed CLI, selected account/billing plan or changed code contract. Unknown required capability blocks that candidate; it does not justify widening permissions.
