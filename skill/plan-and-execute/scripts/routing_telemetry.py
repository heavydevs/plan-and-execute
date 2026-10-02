#!/usr/bin/env python3
"""Metadata-only attempt telemetry and deterministic cost-per-validated-result rollup (PAT003).

Records hold provenance and native-unit usage only: never prompt, code, secret or
transcript text. Missing usage stays null. Files live under the plan directory
(PAT004), never under skill/plan-and-execute/.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

TELEMETRY_RELATIVE = "telemetry/attempts.jsonl"
KINDS = ("root", "subagent", "retry", "diagnostic", "summary")
USAGE_FIELDS = ("input_tokens", "cached_tokens", "cache_write_tokens", "output_tokens", "credits", "usd")
RECORD_FIELDS = (
    "task_id", "kind", "task_class", "validation_strength", "provider", "profile", "harness", "model",
    "native_effort", *USAGE_FIELDS, "latency_seconds", "outcome", "failure_class", "validation_pass", "retry_count",
)
DEFAULT_MAX_BYTES = 8000

_ALIASES = {
    "input_tokens": ("input_tokens", "prompt_tokens"),
    "cached_tokens": ("cache_read_input_tokens", "cached_input_tokens", "cached_tokens"),
    "cache_write_tokens": ("cache_creation_input_tokens", "cache_write_tokens"),
    "output_tokens": ("output_tokens", "completion_tokens"),
    "credits": ("credits", "credits_used"),
}
_USD_KEYS = ("total_cost_usd", "cost_usd")


def _number(value: Any) -> int | float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return value if value >= 0 else None


def _pick(source: dict[str, Any], keys: tuple[str, ...]) -> int | float | None:
    for key in keys:
        found = _number(source.get(key))
        if found is not None:
            return found
    return None


def _scan(value: Any, found: list[dict[str, Any]], depth: int = 0) -> None:
    if depth > 6:
        return
    if isinstance(value, dict):
        usage = value.get("usage") if isinstance(value.get("usage"), dict) else value.get("token_usage")
        record = dict(usage) if isinstance(usage, dict) else {}
        for key in _USD_KEYS:
            if _number(value.get(key)) is not None:
                record["total_cost_usd"] = value[key]
        if _number(value.get("credits")) is not None:
            record["credits"] = value["credits"]
        if record:
            found.append(record)
        for nested in value.values():
            if isinstance(nested, (dict, list)):
                _scan(nested, found, depth + 1)
    elif isinstance(value, list):
        for item in value[:200]:
            _scan(item, found, depth + 1)


def extract_usage(stdout: str) -> dict[str, int | float | None]:
    """Whitelisted numeric usage from a provider envelope; absent fields are None, never estimated."""
    usage: dict[str, int | float | None] = {name: None for name in USAGE_FIELDS}
    found: list[dict[str, Any]] = []
    text = stdout or ""
    candidates = [text] + text.splitlines()[-400:]
    for candidate in candidates:
        candidate = candidate.strip()
        if not candidate.startswith(("{", "[")):
            continue
        try:
            _scan(json.loads(candidate), found)
        except (ValueError, RecursionError):
            continue
    for source in found:
        for name, keys in _ALIASES.items():
            picked = _pick(source, keys)
            if picked is not None:
                usage[name] = picked
        picked = _pick(source, _USD_KEYS)
        if picked is not None:
            usage["usd"] = picked
    return usage


def build_record(
    *, task: dict[str, Any], route: dict[str, Any], profile: dict[str, Any], kind: str = "root", stdout: str = "",
    latency_seconds: float | None = None, outcome: str, failure_class: str | None = None,
    validation_pass: bool | None = None, retry_count: int = 0,
) -> dict[str, Any]:
    if kind not in KINDS:
        raise ValueError(f"unknown worker kind: {kind}")
    record: dict[str, Any] = {
        "task_id": str(task.get("id")) if task.get("id") is not None else None,
        "kind": kind,
        "task_class": task.get("task_class") or task.get("model_tier"),
        "validation_strength": task.get("validation_strength"),
        "provider": route.get("provider"),
        "profile": profile.get("name"),
        "harness": profile.get("harness"),
        "model": route.get("model"),
        "native_effort": route.get("effort"),
        **extract_usage(stdout),
        "latency_seconds": None if latency_seconds is None else round(float(latency_seconds), 3),
        "outcome": outcome,
        "failure_class": failure_class,
        "validation_pass": validation_pass,
        "retry_count": int(retry_count),
    }
    return {name: record[name] for name in RECORD_FIELDS}


def telemetry_path(plan_dir: Path) -> Path:
    return Path(plan_dir) / TELEMETRY_RELATIVE


def append_record(plan_dir: Path, record: dict[str, Any], repo_root: Path | None = None) -> bool:
    """Append one record; telemetry failure never interrupts execution."""
    path = telemetry_path(plan_dir)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if repo_root is not None and not path.exists():
            import resource_watch
            resource_watch.register_artifact(Path(repo_root), path, "plan", Path(plan_dir).name, "keep")
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
        return True
    except Exception as exc:  # noqa: BLE001 - telemetry is best-effort
        print(f"[telemetry] not recorded: {type(exc).__name__}", file=sys.stderr)
        return False


def read_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not Path(path).is_file():
        return records
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        try:
            item = json.loads(line)
        except ValueError:
            continue
        if isinstance(item, dict):
            records.append(item)
    return records


def _sum(records: list[dict[str, Any]], field: str) -> int | float | None:
    values = [r[field] for r in records if _number(r.get(field)) is not None]
    return sum(values) if values else None


def _totals(records: list[dict[str, Any]]) -> dict[str, Any]:
    validated = sum(1 for r in records if r.get("validation_pass") is True)
    totals: dict[str, Any] = {"attempts": len(records), "validated": validated}
    for field in (*USAGE_FIELDS, "latency_seconds"):
        totals[field] = _sum(records, field)
    return totals


def _per_validated(totals: dict[str, Any]) -> dict[str, Any]:
    validated = totals["validated"]
    out: dict[str, Any] = {}
    for field in (*USAGE_FIELDS, "latency_seconds"):
        value = totals.get(field)
        out[field] = round(value / validated, 6) if validated and value is not None else None
    return out


def rollup(records: list[dict[str, Any]], max_bytes: int = DEFAULT_MAX_BYTES) -> dict[str, Any]:
    """Deterministic aggregate over all worker kinds in native units, bounded by max_bytes of JSON."""
    ordered = sorted(records, key=lambda r: json.dumps(r, sort_keys=True))
    totals = _totals(ordered)
    by_kind = {kind: _totals([r for r in ordered if r.get("kind") == kind]) for kind in KINDS}
    by_model: dict[str, Any] = {}
    for key in sorted({f"{r.get('provider')}/{r.get('model')}" for r in ordered}):
        by_model[key] = _totals([r for r in ordered if f"{r.get('provider')}/{r.get('model')}" == key])
    by_task: dict[str, Any] = {}
    for task_id in sorted({str(r.get("task_id")) for r in ordered}):
        by_task[task_id] = _totals([r for r in ordered if str(r.get("task_id")) == task_id])
    result: dict[str, Any] = {
        "totals": totals,
        "per_validated_result": _per_validated(totals),
        "by_kind": by_kind,
        "by_model": by_model,
        "by_task": by_task,
        "truncated": False,
    }
    for drop in ("by_task", "by_model", "by_kind"):
        if len(json.dumps(result, sort_keys=True)) <= max_bytes:
            break
        result[drop] = {}
        result["truncated"] = True
    return result


def rollup_json(records: list[dict[str, Any]], max_bytes: int = DEFAULT_MAX_BYTES) -> str:
    return json.dumps(rollup(records, max_bytes), sort_keys=True, indent=2)


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Roll up attempt telemetry for one plan directory")
    parser.add_argument("plan_dir")
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    args = parser.parse_args(argv)
    print(rollup_json(read_records(telemetry_path(Path(args.plan_dir))), args.max_bytes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
