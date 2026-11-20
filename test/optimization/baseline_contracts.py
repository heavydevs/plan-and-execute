#!/usr/bin/env python3
"""Deterministic offline contract helpers.

Task 001: preflight and baseline inventory drift (`run_preflight`).
Task 002/003: source and contract coverage over check_delivery (`run_source_and_contract_coverage`).
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

TASK_INPUTS_PATH = "docs/plans/20261028-skill-optimization/TASK_INPUTS.json"
BASELINE_INVENTORY_PATH = "docs/research/20261028-skill-optimization/prepared-research/BASELINE_INVENTORY.json"
PREPARED_INDEX_PATH = "docs/research/20261028-skill-optimization/prepared-research/INDEX.json"
SUPPORT_DIR = Path(__file__).resolve().parents[2] / "docs" / "plans" / "20261028-skill-optimization" / "support"
if str(SUPPORT_DIR) not in sys.path:
    sys.path.insert(0, str(SUPPORT_DIR))

import check_delivery  # noqa: E402

structural = check_delivery.structural
verified_files = check_delivery.verified_files
GateError = check_delivery.GateError

SUPPORTED_CLI_MIN_VERSIONS: dict[str, tuple[int, ...]] = {
    "python": (3, 10),
    "node": (18, 0),
    "claude": (1, 0),
    "codex": (0, 1),
}

BROAD_CONTEXT_MARKERS = (
    "transcript.jsonl",
    "transcript_full.jsonl",
)


class PreflightError(ValueError):
    """Raised when a deterministic preflight contract fails."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PreflightError(message)


def _safe_local(root: Path, rel_path: str) -> Path:
    _require(isinstance(rel_path, str) and bool(rel_path), "Empty relative path")
    p = Path(rel_path)
    _require(
        not p.is_absolute() and ".." not in p.parts and "\\" not in rel_path,
        f"Path must be repository-relative without traversal: {rel_path}",
    )
    target = root / p
    for n in range(1, len(p.parts) + 1):
        _require(
            not root.joinpath(*p.parts[:n]).is_symlink(),
            f"Symlink not allowed in preflight input: {rel_path}",
        )
    _require(
        target.resolve().is_relative_to(root.resolve()),
        f"Path escapes repository: {rel_path}",
    )
    return target


def raw_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _load_json(path: Path) -> Any:
    _require(path.is_file(), f"Missing JSON resource: {path.as_posix()}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise PreflightError(f"Invalid JSON in {path.as_posix()}: {exc}") from exc


def parse_version_tuple(raw: str) -> tuple[int, ...]:
    _require(isinstance(raw, str) and bool(raw.strip()), "Empty CLI version string")
    match = re.search(r"(\d+(?:\.\d+)+)", raw.strip())
    _require(match is not None, f"Unparseable CLI version: {raw!r}")
    return tuple(int(part) for part in match.group(1).split("."))


def validate_cli_versions(
    cli_versions: dict[str, str] | None = None,
    min_versions: dict[str, tuple[int, ...]] = SUPPORTED_CLI_MIN_VERSIONS,
) -> dict[str, str]:
    """Validate supplied CLI versions against minimum supported versions."""
    if cli_versions is None:
        cli_versions = {
            "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        }
    validated: dict[str, str] = {}
    for tool, raw_ver in cli_versions.items():
        parsed = parse_version_tuple(raw_ver)
        minimum = min_versions.get(tool)
        if minimum is not None:
            _require(
                parsed >= minimum,
                f"Unsupported CLI version for {tool}: {raw_ver} < {'.'.join(map(str, minimum))}",
            )
        validated[tool] = raw_ver
    return validated


def validate_context_scope(task_entry: dict[str, Any], loaded_paths: list[str]) -> list[str]:
    """Reject broad context loading (all 32 reports, transcripts, or unassigned reports)."""
    allowed = set(task_entry.get("inputs", [])) | set(task_entry.get("prepared_reports", []))
    for rel in loaded_paths:
        if any(marker in rel for marker in BROAD_CONTEXT_MARKERS):
            raise PreflightError(f"Broad context loading rejected (transcript): {rel}")
        if rel.startswith("docs/research/20261028-skill-optimization/prepared-research/") and rel not in allowed:
            raise PreflightError(f"Broad context loading rejected (unassigned prepared report): {rel}")
    if len([p for p in loaded_paths if "/prepared-research/" in p]) > max(len(task_entry.get("prepared_reports", [])), 1):
        raise PreflightError("Broad context loading rejected: more prepared reports loaded than assigned")
    return list(loaded_paths)


def check_inventory_drift(root: Path, inventory_path: str = BASELINE_INVENTORY_PATH) -> dict[str, Any]:
    """Compare current tree against BASELINE_INVENTORY.json and report drift without failing."""
    inv = _load_json(_safe_local(root, inventory_path))
    files = inv.get("files", [])
    _require(isinstance(files, list) and len(files) > 0, "BASELINE_INVENTORY.json has no files")
    drift: list[dict[str, str]] = []
    for item in files:
        rel = item.get("path", "")
        expected = item.get("sha256", "")
        target = _safe_local(root, rel)
        if not target.is_file():
            drift.append({"path": rel, "status": "missing", "expected_sha256": expected})
            continue
        actual = raw_sha256(target)
        if actual != expected:
            drift.append({
                "path": rel,
                "status": "changed",
                "expected_sha256": expected,
                "actual_sha256": actual,
            })
    return {
        "total": len(files),
        "changed_count": len(drift),
        "drift": drift,
    }


def _index_report_hashes(root: Path, index_path: str = PREPARED_INDEX_PATH, loader=_load_json) -> dict[str, str]:
    path = _safe_local(root, index_path)
    if not path.is_file():
        return {}
    data = loader(path)
    hashes: dict[str, str] = {}
    for row in data.get("reports", []):
        if isinstance(row, dict) and row.get("report") and row.get("report_sha256"):
            hashes[row["report"]] = row["report_sha256"]
        if isinstance(row, dict) and row.get("decision_record") and row.get("decision_sha256"):
            hashes[row["decision_record"]] = row["decision_sha256"]
    return hashes


def run_preflight(
    root: Path,
    *,
    task_id: str | None = None,
    cli_versions: dict[str, str] | None = None,
    loaded_context: dict[str, list[str]] | None = None,
    provider_status: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Run deterministic offline preflight for TASK_INPUTS and BASELINE_INVENTORY.

    - Fails on missing/invalid TASK_INPUTS, stale pinned hashes in prepared_reports or
      input_contract, missing existing_baseline_or_current_file resources, unsupported CLI
      versions, or broad context loading.
    - Reports historical BASELINE_INVENTORY.json drift as drift, never as a failure.
    - Records missing authenticated providers as explicit execution limitations without
      fabricating a review or failing local preparation.
    """
    root = root.resolve()
    validated_clis = validate_cli_versions(cli_versions)

    catalog = _load_json(_safe_local(root, TASK_INPUTS_PATH))
    _require(catalog.get("schema_version") == 2, "Unsupported TASK_INPUTS schema_version")
    _require(
        catalog.get("plan_mode") == "single_implementation",
        "TASK_INPUTS plan_mode must be single_implementation",
    )
    tasks = catalog.get("tasks", [])
    _require(isinstance(tasks, list) and len(tasks) > 0, "TASK_INPUTS has no tasks")

    tasks_by_id = {t["id"]: t for t in tasks if isinstance(t, dict) and "id" in t}
    if task_id is not None:
        _require(task_id in tasks_by_id, f"Unknown task_id in TASK_INPUTS: {task_id}")
        selected = [tasks_by_id[task_id]]
    else:
        selected = tasks

    planned_new = {
        p
        for t in tasks
        for p in t.get("planned_new_files", [])
    }
    index_hashes = _index_report_hashes(root)

    checked_tasks: list[str] = []
    for entry in selected:
        tid = entry["id"]
        prepared = entry.get("prepared_reports", [])
        _require(isinstance(prepared, list) and len(prepared) > 0, f"Task {tid} missing prepared_reports")
        for rep in prepared:
            rep_path = _safe_local(root, rep)
            _require(rep_path.is_file(), f"Missing prepared_report for task {tid}: {rep}")
            expected_sha = entry.get("research_sha256") if rep == entry.get("research_report") else index_hashes.get(rep)
            if expected_sha:
                _require(
                    lf_sha256(rep_path) == expected_sha,
                    f"Stale prepared_report hash for task {tid}: {rep}",
                )

        contracts = entry.get("input_contract", [])
        _require(isinstance(contracts, list) and len(contracts) > 0, f"Task {tid} missing input_contract")
        for item in contracts:
            rel = item.get("path", "")
            avail = item.get("availability")
            target = _safe_local(root, rel)
            if avail == "existing_baseline_or_current_file":
                _require(target.is_file(), f"Missing input_contract resource for task {tid}: {rel}")
                pinned = item.get("sha256") or index_hashes.get(rel)
                if pinned:
                    actual_hash = lf_sha256(target) if rel in index_hashes else raw_sha256(target)
                    _require(
                        actual_hash == pinned,
                        f"Stale input_contract hash for task {tid}: {rel}",
                    )
            elif avail in {"create_in_this_task", "prerequisite_output"}:
                pass
            else:
                raise PreflightError(f"Unknown input_contract availability for {tid}/{rel}: {avail}")

        checks = entry.get("required_checks", [])
        _require(isinstance(checks, list) and len(checks) > 0, f"Task {tid} missing required_checks")
        for argv in checks:
            _require(isinstance(argv, list) and len(argv) > 0, f"Invalid check argv for task {tid}")
            if argv[0] in {"python", "python3", "node"} and len(argv) >= 2 and not argv[1].startswith("-"):
                script_rel = argv[1]
                script_path = _safe_local(root, script_rel)
                _require(
                    script_path.is_file() or script_rel in planned_new,
                    f"Missing unowned check script for task {tid}: {script_rel}",
                )

        if loaded_context and tid in loaded_context:
            validate_context_scope(entry, loaded_context[tid])

        checked_tasks.append(tid)

    inventory_report = check_inventory_drift(root)

    return {
        "status": "passed",
        "checked_tasks": checked_tasks,
        "cli_versions": validated_clis,
        "inventory": inventory_report,
        "execution_limitations": collect_provider_limitations(provider_status),
        "independent_review_fabricated": False,
    }


def collect_provider_limitations(provider_status: dict[str, dict[str, Any]] | None) -> list[str]:
    """Record missing authenticated providers as explicit limitations without fabricating reviews."""
    limitations: list[str] = []
    if provider_status:
        for provider, info in sorted(provider_status.items()):
            if not info.get("authenticated", False):
                reason = info.get("reason", "unauthenticated")
                limitations.append(
                    f"Missing authenticated provider '{provider}' ({reason}); "
                    "local preparation continues without fabricating independent review."
                )
    return limitations


def run_source_and_contract_coverage(
    root: Path,
    *,
    native: bool = False,
    provider_status: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Run check_delivery.structural, then check every task's prepared_reports against independent pins.

    - Rejects a catalog entry whose `prepared_reports` key is missing, empty, non-string or duplicated,
      before `structural` runs. check_delivery.structural/check do not enforce this themselves:
      `structural` raises a bare KeyError for a missing key and accepts an empty list.
    - A prepared report pinned by TASK_INPUTS `research_sha256` (when it is the task's `research_report`)
      or by INDEX.json `report_sha256`/`decision_sha256` must match that pin as an LF blob
      (check_delivery.verified_files, text=True). Byte drift is rejected.
    - A prepared report with no pin is only checked for a safe repository path and existence; its
      content drift is caught by each receipt's raw-hash `prepared_inputs` pin, not here.
    """
    root = root.resolve()
    catalog = check_delivery.catalog(root)
    for tid, entry in catalog.items():
        prepared = entry.get("prepared_reports")
        _require(
            isinstance(prepared, list) and len(prepared) > 0 and all(isinstance(p, str) and p for p in prepared),
            f"Task {tid} missing prepared_reports",
        )
        _require(len(set(prepared)) == len(prepared), f"Task {tid} has duplicate prepared_reports")
    structural_result = structural(root, native=native)
    index_hashes = _index_report_hashes(root, loader=check_delivery.load)
    pinned = unpinned = 0
    for tid, entry in catalog.items():
        records = []
        for rep in entry["prepared_reports"]:
            pin = entry.get("research_sha256") if rep == entry.get("research_report") else index_hashes.get(rep)
            if pin:
                records.append({"path": rep, "sha256": pin})
            else:
                _require(check_delivery.local(root, rep).is_file(), f"Missing prepared_report for task {tid}: {rep}")
                unpinned += 1
        if records:
            verified_files(root, records, "prepared_report", text=True)
            pinned += len(records)
    return {
        "status": "passed",
        "structural": structural_result,
        "tasks_checked": len(catalog),
        "prepared_reports_pinned": pinned,
        "prepared_reports_unpinned": unpinned,
        "execution_limitations": collect_provider_limitations(provider_status),
        "independent_review_fabricated": False,
    }
