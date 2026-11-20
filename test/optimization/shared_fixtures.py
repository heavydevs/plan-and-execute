#!/usr/bin/env python3
"""Shared offline acceptance fixtures and report-aware task input loader for task 004."""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any

OPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = OPT_DIR.parents[1]
SCRIPTS_DIR = REPO_ROOT / "skill" / "plan-and-execute" / "scripts"
# Importable from any directory: baseline_contracts lives next to this module.
for _path in (SCRIPTS_DIR, OPT_DIR):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

import availability  # noqa: E402
import baseline_contracts  # noqa: E402

SUPPORTED_PROVIDERS = ("claude", "codex", "antigravity")
SUPPORTED_OUTCOMES = ("success", "quota", "auth", "functional", "credit_exhaustion")
OWN_FILE_AVAILABILITY = "create_in_this_task"
READABLE_AVAILABILITY = frozenset({"existing_baseline_or_current_file", "prerequisite_output"})
CATALOG_SCHEMA_VERSION = 2
# Every category that availability.unavailable() accepts as an availability event (never capability evidence).
AVAILABILITY_EVENTS = frozenset({*availability.CATEGORIES, "configured_exit", "missing_cli", "model_unavailable"})


class ReportAwareInputError(baseline_contracts.PreflightError):
    """Raised when a task's input catalog entry or a requested input is not loadable."""


class OwnTaskFileError(ReportAwareInputError):
    """Raised when the task's own not-yet-created (`create_in_this_task`) file is used as an input."""


class UnlistedInputError(ReportAwareInputError):
    """Raised when a requested path is neither a prepared report nor a readable input_contract path."""


@dataclass(frozen=True)
class FakeProviderResult:
    """Deterministic offline provider outcome without subprocess or network calls.

    `classification` is the coarse label (success / availability / configuration /
    functional); `availability_category` is the production category and is what tells
    credit exhaustion (`quota`) apart from a login failure (`authentication`).
    """

    provider: str
    argv: list[str]
    outcome: str
    return_code: int
    stdout: str
    stderr: str
    classification: str
    availability_category: str | None
    payload: dict[str, Any] = field(default_factory=dict)


def build_provider_argv(
    provider: str,
    prompt: str,
    *,
    model: str = "test-model",
    effort: str = "medium",
    schema_text: str = '{"type":"object"}',
    schema_path: str = "codex-output-schema.json",
    result_path: str = "codex-last-message.json",
    print_timeout: str = "120s",
) -> list[str]:
    """Build deterministic claude/codex/antigravity CLI argv without launching a process.

    The flags and their order match `run_isolated.build_worker_command` under the default
    configuration on the subscription path (no `ANTHROPIC_API_KEY`, so no `--bare`), with
    no budget or extra arguments, for a model that accepts an effort flag;
    `task_004_self_test` pins that parity against the production builder. The values of
    `--json-schema`, `--output-schema`, `--output-last-message` and `--print-timeout`
    intentionally differ (production uses the completion schema, temp result paths and a
    `12h` window), and production omits the effort flag for effort-less models.
    """
    if provider == "claude":
        return [
            "claude",
            "--print",
            "--no-session-persistence",
            "--output-format",
            "json",
            "--permission-mode",
            "auto",
            "--model",
            model,
            "--effort",
            effort,
            "--json-schema",
            schema_text,
            prompt,
        ]
    if provider == "codex":
        return [
            "codex",
            "exec",
            "--ephemeral",
            "--sandbox",
            "workspace-write",
            "--model",
            model,
            "-c",
            f'model_reasoning_effort="{effort}"',
            "--output-schema",
            schema_path,
            "--output-last-message",
            result_path,
            prompt,
        ]
    if provider == "antigravity":
        return [
            "agy",
            "--dangerously-skip-permissions",
            "--output-format",
            "json",
            "--json-schema",
            schema_text,
            "--model",
            model,
            "--effort",
            effort,
            "--print-timeout",
            print_timeout,
            "-p",
            prompt,
        ]
    raise ValueError(f"Unsupported provider for fake fixture: {provider!r}")


_OUTCOME_SPECS: dict[str, dict[str, Any]] = {
    "success": {
        "return_code": 0,
        "stderr": "",
        "payload": {"status": "completed", "summary": "Offline fake-provider success"},
    },
    "quota": {
        "return_code": 1,
        "stderr": "HTTP 429 rate limit exceeded: quota exceeded for current window",
        "payload": {"error": "quota_exceeded", "cause": "quota"},
    },
    "auth": {
        "return_code": 1,
        "stderr": "Authentication required: not authenticated, please log in",
        "payload": {"error": "authentication_required", "cause": "auth"},
    },
    "functional": {
        "return_code": 1,
        "stderr": "Validation assertion failed: semantic diff mismatch in target module",
        "payload": {"error": "semantic_failure", "failure_class": "semantic"},
    },
    "credit_exhaustion": {
        "return_code": 1,
        "stderr": "Billing limit reached: credits exhausted for this account",
        "payload": {"error": "credit_exhaustion", "cause": "billing"},
    },
}


def classify_outcome(return_code: int, availability_category: str | None) -> str:
    """Derive the fixture label from the production availability classifier's category.

    Availability events rotate providers and configuration errors never count as
    capability evidence; only an unclassified non-zero exit is a functional failure.
    """
    if return_code == 0:
        return "success"
    if availability_category in AVAILABILITY_EVENTS:
        return "availability"
    if availability_category == "configuration":
        return "configuration"
    return "functional"


class FakeProviderFixture:
    """Shared offline fake-provider fixture for claude, codex, and antigravity."""

    def __init__(self, default_outcomes: dict[str, str] | None = None) -> None:
        self.default_outcomes = dict(default_outcomes or {})
        self.calls: list[FakeProviderResult] = []

    def invoke(
        self,
        provider: str,
        prompt: str = "Execute isolated contract check",
        *,
        outcome: str | None = None,
        model: str = "test-model",
        effort: str = "medium",
    ) -> FakeProviderResult:
        if provider not in SUPPORTED_PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider!r}")
        chosen = outcome or self.default_outcomes.get(provider, "success")
        if chosen not in SUPPORTED_OUTCOMES:
            raise ValueError(f"Unsupported outcome: {chosen!r}")

        argv = build_provider_argv(provider, prompt, model=model, effort=effort)
        spec = _OUTCOME_SPECS[chosen]
        return_code = int(spec["return_code"])
        stderr = str(spec["stderr"])
        payload = dict(spec["payload"])
        stdout = json.dumps(payload, ensure_ascii=True) if return_code == 0 else ""
        avail_cat = availability.classify(return_code, stderr or stdout, [])

        result = FakeProviderResult(
            provider=provider,
            argv=argv,
            outcome=chosen,
            return_code=return_code,
            stdout=stdout,
            stderr=stderr,
            classification=classify_outcome(return_code, avail_cat),
            availability_category=avail_cat,
            payload=payload,
        )
        self.calls.append(result)
        return result


def credit_exhaustion_fixture(
    provider: str = "claude",
    prompt: str = "Check credit exhaustion classification",
) -> FakeProviderResult:
    """Return a credit-exhaustion outcome classified as availability, distinct from auth/functional."""
    return FakeProviderFixture().invoke(provider, prompt, outcome="credit_exhaustion")


def _checked_path(root: Path, task_id: str, rel: Any, label: str) -> str:
    """A canonical, repository-local POSIX path; any unsafe or non-canonical spelling is rejected."""
    if not isinstance(rel, str) or not rel:
        raise ReportAwareInputError(f"Task {task_id} {label} must be a non-empty path")
    if rel != PurePosixPath(rel).as_posix():
        raise ReportAwareInputError(f"Task {task_id} {label} is not a canonical POSIX path: {rel!r}")
    try:
        baseline_contracts._safe_local(root, rel)
    except ReportAwareInputError:
        raise
    except baseline_contracts.PreflightError as exc:
        raise ReportAwareInputError(f"Task {task_id} {label} is unsafe: {exc}") from exc
    return rel


def load_report_aware_task_inputs(
    root: Path,
    task_id: str,
    *,
    requested_paths: list[str] | None = None,
) -> dict[str, Any]:
    """Load only the task entry's prepared_reports and readable input_contract paths.

    Every failure raises `ReportAwareInputError`: a malformed catalog (schema version,
    task list, duplicated task id, non-list fields, unknown availability values) or any
    unsafe or non-canonical listed path; an unlisted report or input
    (`UnlistedInputError`); and the task's own `create_in_this_task` files
    (`OwnTaskFileError`). An own file that the entry also lists as a prepared report or
    readable input, under any letter case, is rejected fail-closed for the default and the
    explicit-request load alike, even after it exists.
    """
    root = root.resolve()
    try:
        catalog = baseline_contracts._load_json(
            baseline_contracts._safe_local(root, baseline_contracts.TASK_INPUTS_PATH)
        )
    except baseline_contracts.PreflightError as exc:
        raise ReportAwareInputError(f"TASK_INPUTS catalog is not loadable: {exc}") from exc
    if not isinstance(catalog, dict) or catalog.get("schema_version") != CATALOG_SCHEMA_VERSION:
        raise ReportAwareInputError(f"TASK_INPUTS catalog must have schema_version {CATALOG_SCHEMA_VERSION}")
    tasks = catalog.get("tasks")
    if not isinstance(tasks, list):
        raise ReportAwareInputError("TASK_INPUTS catalog has no task list")
    matches = [t for t in tasks if isinstance(t, dict) and t.get("id") == task_id]
    if not matches:
        raise ReportAwareInputError(f"Unknown task_id in TASK_INPUTS: {task_id}")
    if len(matches) > 1:
        raise ReportAwareInputError(f"Duplicate task_id in TASK_INPUTS: {task_id}")
    entry = matches[0]

    prepared_reports = entry.get("prepared_reports", [])
    if not isinstance(prepared_reports, list):
        raise ReportAwareInputError(f"Task {task_id} prepared_reports must be a list of paths")
    prepared_reports = list(dict.fromkeys(
        _checked_path(root, task_id, rel, "prepared_reports entry") for rel in prepared_reports
    ))
    contracts = entry.get("input_contract", [])
    if not isinstance(contracts, list):
        raise ReportAwareInputError(f"Task {task_id} input_contract must be a list")

    own_new_files: set[str] = set()
    readable_contract_paths: list[str] = []
    for item in contracts:
        rel = _checked_path(
            root, task_id, item.get("path") if isinstance(item, dict) else None, "input_contract path"
        )
        avail = item.get("availability")
        if avail == OWN_FILE_AVAILABILITY:
            own_new_files.add(rel)
        elif avail in READABLE_AVAILABILITY:
            if rel not in readable_contract_paths:
                readable_contract_paths.append(rel)
        else:
            raise ReportAwareInputError(
                f"Unknown input_contract availability for {task_id}/{rel}: {avail!r}"
            )
    # Case-insensitive file systems resolve case variants to the same file.
    own_keys = {rel.casefold() for rel in own_new_files}

    allowed_ordered: list[str] = []
    for rel in prepared_reports + readable_contract_paths:
        if rel.casefold() in own_keys:
            raise OwnTaskFileError(
                f"Task {task_id} lists its own not-yet-created file as a readable input: {rel}"
            )
        if rel not in allowed_ordered:
            allowed_ordered.append(rel)
    allowed_set = set(allowed_ordered)

    if requested_paths is not None:
        if not isinstance(requested_paths, list):
            raise ReportAwareInputError("requested_paths must be a list of paths")
        for rel in requested_paths:
            _checked_path(root, task_id, rel, "requested path")
            if rel.casefold() in own_keys:
                raise OwnTaskFileError(
                    f"Rejected task {task_id} own not-yet-created file as input: {rel}"
                )
            if rel not in allowed_set:
                raise UnlistedInputError(
                    f"Rejected unlisted report or input for task {task_id}: {rel}"
                )
        selected = list(dict.fromkeys(requested_paths))
    else:
        selected = allowed_ordered

    for rel in selected:
        if not (root / rel).is_file():
            raise ReportAwareInputError(f"Missing declared input for task {task_id}: {rel}")

    return {
        "task_id": task_id,
        "prepared_reports": [p for p in prepared_reports if p in selected],
        "input_contract_paths": [p for p in readable_contract_paths if p in selected],
        "allowed_paths": selected,
        "rejected_own_files": sorted(own_new_files),
    }
