#!/usr/bin/env python3
"""Portable PROGRESS/ERROR/HEARTBEAT lines and a bounded, read-only log probe."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path
from typing import Any, Mapping, TextIO


KINDS = {"PROGRESS", "ERROR", "HEARTBEAT"}
KEY = re.compile(r"[a-z_]+")
TOKEN = re.compile(r"[A-Za-z0-9_.:-]+")
ENUM = re.compile(r"[a-z][a-z0-9_]*")
COUNTERS = {"done", "total", "attempt", "seq"}
TAIL_BYTES = 128 * 1024


def _validate(kind: str, fields: Mapping[str, Any]) -> dict[str, Any]:
    if kind not in KINDS:
        raise ValueError("Unknown signal kind")
    result: dict[str, Any] = {}
    for key, value in fields.items():
        if not isinstance(key, str) or KEY.fullmatch(key) is None or key == "kind":
            raise ValueError("Signal keys must match [a-z_]+ and cannot be kind")
        if key in COUNTERS:
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{key} must be a nonnegative integer")
        elif not isinstance(value, str) or TOKEN.fullmatch(value) is None:
            raise ValueError(f"{key} must be a nonempty unquoted token")
        result[key] = value
    if kind == "PROGRESS" and not {"stage", "done"} <= result.keys():
        raise ValueError("PROGRESS requires stage and done")
    if kind == "ERROR" and not {"class", "fp", "stage"} <= result.keys():
        raise ValueError("ERROR requires class, fp and stage")
    for key in ("stage", "class"):
        if key in result and ENUM.fullmatch(result[key]) is None:
            raise ValueError(f"{key} must be a lowercase enum token")
    if "fp" in result and re.fullmatch(r"[0-9a-f]{8}", result["fp"]) is None:
        raise ValueError("fp must be eight lowercase hex digits")
    return result


def format_signal(kind: str, fields: Mapping[str, Any] | None = None, **extra: Any) -> str:
    """Format one line without a newline; counters remain integers on parsing."""
    values = dict(fields or {})
    if values.keys() & extra.keys():
        raise ValueError("Duplicate signal key")
    values.update(extra)
    values = _validate(kind, values)
    order = ("stage", "done", "total", "attempt", "seq") if kind == "PROGRESS" else ("class", "fp", "stage")
    keys = [key for key in order if key in values] + sorted(values.keys() - set(order))
    return " ".join([kind, *(f"{key}={values[key]}" for key in keys)])


def parse_signal(line: str) -> dict[str, Any] | None:
    """Return a flat {kind, ...fields} record, None for ordinary log lines.

    Recognized but malformed signals raise ValueError. Additive token fields
    are retained; known counters are parsed as nonnegative integers.
    """
    if "\n" in line.rstrip("\r\n") or "\r" in line.rstrip("\r\n"):
        raise ValueError("Expected one signal line")
    parts = line.split()
    if not parts or parts[0] not in KINDS:
        return None
    fields: dict[str, Any] = {}
    for part in parts[1:]:
        key, separator, value = part.partition("=")
        if not separator or key in fields:
            raise ValueError("Malformed or duplicate signal field")
        if key in COUNTERS:
            if re.fullmatch(r"[0-9]+", value) is None:
                raise ValueError(f"{key} must be a nonnegative integer")
            value = int(value)
        fields[key] = value
    return {"kind": parts[0], **_validate(parts[0], fields)}


def emit_signal(kind: str, fields: Mapping[str, Any] | None = None,
                *, stream: TextIO | None = None, **extra: Any) -> str:
    """Write and flush one signal; return the formatted line."""
    line = format_signal(kind, fields, **extra)
    print(line, file=sys.stdout if stream is None else stream, flush=True)
    return line


def fingerprint_error(message: str) -> str:
    """Hash normalized error text to hex8, masking variable payloads."""
    text = message.lower()
    text = re.sub(r"\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'", "<string>", text)
    text = re.sub(r"(?<![\w/\\])(?:[a-z]:[\\/]|\\\\|\.{0,2}/|/|[\w.-]+[\\/])[^\s,;<>]+", "<path>", text)
    text = re.sub(r"\b[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\b", "<id>", text)
    text = re.sub(r"\b([a-z_]*id|[a-z_]*uuid)([=: ]+)[\w.-]+", r"\1\2<id>", text)
    text = re.sub(r"\b(?:0x[0-9a-f]+|[0-9a-f]{8,})\b", "<hex>", text)
    text = re.sub(r"(?<!\w)[+-]?\d+(?:\.\d+)?(?:e[+-]?\d+)?\b", "<number>", text)
    text = " ".join(text.split())
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]


def probe_file(path: str | Path, *, tail_bytes: int = TAIL_BYTES) -> int:
    """Read only the final bounded window; return latest PROGRESS seq or done.

    seq, when present, is a run-wide counter that can span stage-local done
    resets. No complete valid PROGRESS in the window returns baseline zero.
    HEARTBEAT, ERROR, malformed and partially written lines are ignored.
    """
    if isinstance(tail_bytes, bool) or not isinstance(tail_bytes, int) or not 1 <= tail_bytes <= TAIL_BYTES:
        raise ValueError(f"tail_bytes must be 1..{TAIL_BYTES}")
    with Path(path).open("rb") as source:
        source.seek(0, 2)
        offset = max(0, source.tell() - tail_bytes)
        source.seek(offset)
        block = source.read(tail_bytes)
    if offset:
        block = block.partition(b"\n")[2]
    # An unfinished append must not turn a partial counter into progress.
    lines = block.split(b"\n")[:-1]
    for line in reversed(lines):
        try:
            signal = parse_signal(line.decode("utf-8", "replace"))
        except ValueError:
            continue
        if signal is not None and signal["kind"] == "PROGRESS":
            return signal.get("seq", signal["done"])
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    probe = sub.add_parser("probe", help="print only the latest progress counter")
    probe.add_argument("--file", required=True)
    args = parser.parse_args(argv)
    try:
        print(probe_file(args.file))
        return 0
    except (OSError, ValueError) as exc:
        print(f"progress-signal: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
