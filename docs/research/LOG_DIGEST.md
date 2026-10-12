# Bounded log digest measurement

Run `python skill/plan-and-execute/scripts/log_watch_self_test.py` to reproduce
the synthetic corpus. It generates 2,500 repetitions of an informational line,
a PROGRESS tick, a contract ERROR and a generic RuntimeException with varying
IDs, paths, numbers and a synthetic secret. No production data is used. Tests
assert that the secret and domain paths never appear in output.

Measured on 2026-10-12 with Python 3.13:

```text
stats input_lines=10000 input_chars=545563 output_lines=6 output_chars=453 input_tokens=136390.75 output_tokens=113.25 reduction_pct=99.92
```

Tokens are estimates (`chars / 4`), not tokenizer counts. Output counts include
newlines and the stats line. Each error group has exactly 2,500 records; the scan
stage has 2,500 ticks ending at done=2500. Two executions produce identical
output. Tests also verify scan output/exit codes, cursor reuse, split writes,
truncation, rotation and skipped bytes.

`log_watch.py digest --file <log> --stats` streams a prefix up to
`--max-read-bytes` (default/max 20 MiB), retaining at most `--max-classes` groups
(default 32, range 1..100). Contract errors group by class/fp; generic Traceback,
Exception, FAILED and ERROR lines use `progress_signal.fingerprint_error`.
Messages become `message=<redacted>`; additive fields are never echoed.
Class/stage enums are trusted contract metadata and must contain no domain values.
Progress rows show latest counters; all groups have counts and first/last source
line numbers. Rows sort by their keys and have a 200-character ceiling.

`--max-lines` (default 40, range 4..100) includes header, omission summary and
optional stats. Capacity limits produce visible `omitted_records` counts. Long
metadata rows are clipped. `truncated=1` marks a byte-limited prefix, excluding
its incomplete final record. Counts and reduction apply only to the scanned
prefix. Empty input reports zero reduction. Digest success is exit 0 even with
errors, truncation or omissions; invalid arguments/I/O return 2. Use `scan` for
incremental health checks; its behavior is unchanged.
