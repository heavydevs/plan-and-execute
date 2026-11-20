#!/usr/bin/env python3
"""Offline contract self-tests for task 004 shared fixtures and report-aware loader."""
from __future__ import annotations

import builtins
import contextlib
import io
import json
import os
import pathlib
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Iterator
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[2]
OPT_DIR = Path(__file__).resolve().parent
if str(OPT_DIR) not in sys.path:
    sys.path.insert(0, str(OPT_DIR))

import shared_fixtures  # noqa: E402  (also puts the skill scripts directory on sys.path)
import availability  # noqa: E402
import baseline_contracts  # noqa: E402
import planctl  # noqa: E402
import run_isolated  # noqa: E402

ARCH_REPORT = "docs/research/20261028-skill-optimization/prepared-research/ARCHITECTURE_AND_SCOPE.md"
OWN_004_FILES = ["test/optimization/shared_fixtures.py", "test/optimization/task_004_self_test.py"]
PROVIDERS = ("claude", "codex", "antigravity")
# User-global configuration roots the CLIs and Python helpers resolve; all point at one empty temp dir.
USER_DIR_VARS = ("HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "XDG_CONFIG_HOME", "CLAUDE_CONFIG_DIR", "CODEX_HOME")
# Argv values that legitimately differ between fixture and production (schema text, temp paths, timeout).
VALUE_SLOTS = ("--json-schema", "--output-schema", "--output-last-message", "--print-timeout")
WRITE_FLAGS = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_TRUNC
# Calls that start a process, open a socket, or create/modify/delete a file. pathlib methods are patched
# directly because Python 3.10 binds io.open/os.* into its path accessor at import time.
FORBIDDEN_CALLS = [
    (subprocess, "run"), (subprocess, "Popen"), (socket, "create_connection"), (socket, "socket"),
    (os, "replace"), (os, "rename"), (os, "mkdir"), (os, "makedirs"), (os, "remove"), (os, "unlink"),
    (os, "rmdir"), (os, "symlink"), (os, "system"), (shutil, "rmtree"),
    (pathlib.Path, "write_text"), (pathlib.Path, "write_bytes"), (pathlib.Path, "mkdir"), (pathlib.Path, "touch"),
    (pathlib.Path, "replace"), (pathlib.Path, "rename"), (pathlib.Path, "unlink"), (pathlib.Path, "rmdir"),
    (pathlib.Path, "symlink_to"),
] + [(os, name) for name in ("spawnv", "spawnve", "execv", "execve", "posix_spawn", "startfile") if hasattr(os, name)]


@contextlib.contextmanager
def redirected_user_dirs(test: unittest.TestCase, *, verify: bool = True) -> Iterator[str]:
    """Point user-global configuration roots at an empty temp dir and require it to stay empty."""
    with tempfile.TemporaryDirectory() as user_home:
        with patch.dict(os.environ, {name: user_home for name in USER_DIR_VARS}):
            yield user_home
        if verify:
            test.assertEqual(os.listdir(user_home), [], "user-global configuration directory was written")


@contextlib.contextmanager
def offline_guard(test: unittest.TestCase, *, verify: bool = True) -> Iterator[list[str]]:
    """Forbid processes, sockets and file writes/deletes while user-global config dirs are redirected.

    Every attempt is recorded even if a caller swallows the raised AssertionError; with
    `verify=True` the test fails when anything was attempted.
    """
    violations: list[str] = []
    real_open, real_path_open, real_os_open = builtins.open, pathlib.Path.open, os.open

    def refuse(name: str) -> None:
        violations.append(name)
        raise AssertionError(f"Offline fixture must not call {name}")

    def forbid(name: str):
        def _raise(*_args: Any, **_kwargs: Any) -> Any:
            refuse(name)
        return _raise

    def guarded_open(file: Any, mode: str = "r", *args: Any, **kwargs: Any) -> Any:
        if set(str(mode)) & set("wax+"):
            refuse(f"open:{mode}")
        return real_open(file, mode, *args, **kwargs)

    def guarded_path_open(self: Path, mode: str = "r", *args: Any, **kwargs: Any) -> Any:
        if set(str(mode)) & set("wax+"):
            refuse(f"Path.open:{mode}")
        return real_path_open(self, mode, *args, **kwargs)

    def guarded_os_open(path: Any, flags: int, *args: Any, **kwargs: Any) -> Any:
        if flags & WRITE_FLAGS:
            refuse("os.open:write")
        return real_os_open(path, flags, *args, **kwargs)

    with redirected_user_dirs(test, verify=verify):
        with contextlib.ExitStack() as stack:
            for owner, name in FORBIDDEN_CALLS:
                label = f"{getattr(owner, '__name__', owner)}.{name}"
                stack.enter_context(patch.object(owner, name, side_effect=forbid(label)))
            stack.enter_context(patch.object(builtins, "open", guarded_open))
            stack.enter_context(patch.object(io, "open", guarded_open))
            stack.enter_context(patch.object(pathlib.Path, "open", guarded_path_open))
            stack.enter_context(patch.object(os, "open", guarded_os_open))
            yield violations
        if verify:
            test.assertEqual(violations, [], "offline fixture attempted a process, socket or write")


def normalize_argv(argv: list[str]) -> list[str]:
    out = list(argv)
    for index, item in enumerate(out[:-1]):
        if item in VALUE_SLOTS:
            out[index + 1] = "<value>"
    return out


class Task004SharedFixturesTest(unittest.TestCase):
    def temp_dir(self) -> Path:
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        return Path(holder.name)

    def catalog_root(self, entries: list[dict[str, Any]], files: tuple[str, ...] = (),
                     schema_version: int = 2) -> Path:
        """A temporary repository root with its own TASK_INPUTS catalog (written before any guard)."""
        root = self.temp_dir()
        catalog = root / baseline_contracts.TASK_INPUTS_PATH
        catalog.parent.mkdir(parents=True)
        catalog.write_text(json.dumps({"schema_version": schema_version, "tasks": entries}), encoding="utf-8")
        for rel in files:
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text("x\n", encoding="utf-8")
        return root

    def test_ac01_shared_fake_provider_argv_and_outcomes_offline(self) -> None:
        fixture = shared_fixtures.FakeProviderFixture()
        with offline_guard(self):
            for provider in PROVIDERS:
                for outcome in ("success", "quota", "auth", "functional"):
                    res = fixture.invoke(provider, f"run {provider} {outcome}", outcome=outcome)
                    self.assertEqual(res.provider, provider)
                    self.assertEqual(res.outcome, outcome)
                    self.assertEqual(res.argv[-1], f"run {provider} {outcome}")
                    if provider == "claude":
                        self.assertEqual(res.argv[0], "claude")
                        self.assertIn("--json-schema", res.argv)
                    elif provider == "codex":
                        self.assertEqual(res.argv[:2], ["codex", "exec"])
                        self.assertIn("--output-schema", res.argv)
                    elif provider == "antigravity":
                        self.assertEqual(res.argv[0], "agy")
                        self.assertEqual(res.argv[-2], "-p")
                        self.assertIn("--print-timeout", res.argv)

                    if outcome == "success":
                        self.assertEqual(res.return_code, 0)
                        self.assertEqual(res.classification, "success")
                        self.assertIsNone(res.availability_category)
                    elif outcome == "quota":
                        self.assertEqual(res.return_code, 1)
                        self.assertEqual(res.classification, "availability")
                        self.assertEqual(res.availability_category, "quota")
                    elif outcome == "auth":
                        self.assertEqual(res.return_code, 1)
                        self.assertEqual(res.classification, "availability")
                        self.assertEqual(res.availability_category, "authentication")
                    elif outcome == "functional":
                        self.assertEqual(res.return_code, 1)
                        self.assertEqual(res.classification, "functional")
                        self.assertIsNone(res.availability_category)

        self.assertEqual(len(fixture.calls), 12)

    def test_ac01_fixture_argv_matches_production_worker_builder(self) -> None:
        """Fixture flags and order equal run_isolated.build_worker_command under the default config (no --bare)."""
        config = planctl.default_config()
        expected: dict[str, list[str]] = {}
        temp = self.temp_dir()
        result_path = temp / "results" / "007.json"
        result_path.parent.mkdir(parents=True)
        # The production builder writes its codex schema next to result_path; user dirs must stay untouched.
        with (
            redirected_user_dirs(self),
            patch.object(run_isolated, "resolve_windows_shim", side_effect=list),
        ):
            os.environ.pop("ANTHROPIC_API_KEY", None)
            for provider in PROVIDERS:
                route = {"provider": provider, "tier": "standard", "model": "test-model", "effort": "high"}
                expected[provider] = normalize_argv(
                    run_isolated.build_worker_command(provider, route, config, "PROMPT", result_path)
                )
        fixture = shared_fixtures.FakeProviderFixture()
        with offline_guard(self):
            for provider in PROVIDERS:
                res = fixture.invoke(provider, "PROMPT", outcome="success", model="test-model", effort="high")
                self.assertEqual(normalize_argv(res.argv), expected[provider], provider)

    def test_ac02_report_aware_loader_bounds_and_rejections(self) -> None:
        with offline_guard(self):
            loaded = shared_fixtures.load_report_aware_task_inputs(REPO_ROOT, "004")
            self.assertEqual(loaded["allowed_paths"], [ARCH_REPORT])
            self.assertEqual(loaded["prepared_reports"], [ARCH_REPORT])
            self.assertEqual(loaded["rejected_own_files"], OWN_004_FILES)

            for own in OWN_004_FILES:
                with self.assertRaisesRegex(shared_fixtures.OwnTaskFileError, "own not-yet-created"):
                    shared_fixtures.load_report_aware_task_inputs(REPO_ROOT, "004", requested_paths=[own])

            unlisted = "docs/research/20261028-skill-optimization/prepared-research/UNLISTED_REPORT.md"
            with self.assertRaises(shared_fixtures.UnlistedInputError) as caught:
                shared_fixtures.load_report_aware_task_inputs(REPO_ROOT, "004", requested_paths=[unlisted])
            self.assertNotIsInstance(caught.exception, shared_fixtures.OwnTaskFileError)

    def test_ac02_own_file_overlap_rejected_for_default_and_requested_load(self) -> None:
        report, own, dep = "docs/report.md", "test/own.py", "docs/dep.txt"
        contract = [
            {"path": dep, "availability": "prerequisite_output"},
            {"path": own, "availability": "create_in_this_task"},
        ]
        files = (report, own, dep)
        clean = self.catalog_root([{"id": "900", "prepared_reports": [report], "input_contract": contract}], files)
        # The own file already exists (a retry); listing it as a report or readable input must still fail,
        # including under another letter case (one file on case-insensitive file systems).
        overlapping = [
            self.catalog_root([{"id": "900", "prepared_reports": [report, own], "input_contract": contract}], files),
            self.catalog_root([{"id": "900", "prepared_reports": [report],
                                "input_contract": [*contract, {"path": own, "availability": "prerequisite_output"}]}],
                              files),
            self.catalog_root([{"id": "900", "prepared_reports": [report, own.upper()], "input_contract": contract}],
                              files),
        ]
        with offline_guard(self):
            loaded = shared_fixtures.load_report_aware_task_inputs(clean, "900")
            self.assertEqual(loaded["allowed_paths"], [report, dep])
            self.assertEqual(loaded["input_contract_paths"], [dep])
            self.assertEqual(loaded["rejected_own_files"], [own])
            for requested in ([report, own], [own.upper()]):
                with self.assertRaises(shared_fixtures.OwnTaskFileError):
                    shared_fixtures.load_report_aware_task_inputs(clean, "900", requested_paths=requested)
            for root in overlapping:
                for requested in (None, [report]):
                    with self.assertRaisesRegex(shared_fixtures.OwnTaskFileError, "own not-yet-created file"):
                        shared_fixtures.load_report_aware_task_inputs(root, "900", requested_paths=requested)

    def test_ac02_noncanonical_and_unsafe_paths_rejected(self) -> None:
        report, own = "docs/report.md", "test/own.py"
        own_entry = {"path": own, "availability": "create_in_this_task"}
        roots = {
            spelling: self.catalog_root(
                [{"id": "902", "prepared_reports": [report, spelling], "input_contract": [own_entry]}], (report, own))
            for spelling in ("test/./own.py", "test//own.py", "./test/own.py", "../outside.md", "test\\own.py")
        }
        # An unsafe path the caller does not select still invalidates the entry.
        roots["unselected traversal"] = self.catalog_root(
            [{"id": "902", "prepared_reports": [report],
              "input_contract": [{"path": "../outside.md", "availability": "prerequisite_output"}]}], (report,))
        clean = self.catalog_root([{"id": "902", "prepared_reports": [report], "input_contract": [own_entry]}],
                                  (report, own))
        with offline_guard(self):
            for name, root in roots.items():
                with self.assertRaises(shared_fixtures.ReportAwareInputError, msg=name):
                    shared_fixtures.load_report_aware_task_inputs(root, "902", requested_paths=[report])
            for requested in ("./docs/report.md", "docs//report.md", "../docs/report.md"):
                with self.assertRaises(shared_fixtures.ReportAwareInputError, msg=requested) as caught:
                    shared_fixtures.load_report_aware_task_inputs(clean, "902", requested_paths=[requested])
                self.assertNotIsInstance(caught.exception, shared_fixtures.UnlistedInputError, requested)

    def test_ac02_malformed_catalog_entries_rejected(self) -> None:
        report = "docs/report.md"
        good = {"id": "901", "prepared_reports": [report], "input_contract": []}
        bad_catalogs = {
            "unknown_availability": [{**good, "input_contract": [{"path": report, "availability": "existing_baseline"}]}],
            "missing_path": [{**good, "input_contract": [{"availability": "prerequisite_output"}]}],
            "string_reports": [{**good, "prepared_reports": report}],
            "contract_not_list": [{**good, "input_contract": {"path": report}}],
            "duplicate_task_id": [good, {**good, "prepared_reports": []}],
        }
        roots = {name: self.catalog_root(entries, (report,)) for name, entries in bad_catalogs.items()}
        roots["schema_version"] = self.catalog_root([good], (report,), schema_version=1)
        roots["missing_listed_file"] = self.catalog_root([good])
        with offline_guard(self):
            for name, root in roots.items():
                with self.assertRaises(shared_fixtures.ReportAwareInputError, msg=name) as caught:
                    shared_fixtures.load_report_aware_task_inputs(root, "901")
                self.assertNotIsInstance(caught.exception, shared_fixtures.UnlistedInputError, name)

    def test_ac03_credit_exhaustion_distinct_from_auth_and_functional(self) -> None:
        fixture = shared_fixtures.FakeProviderFixture()
        with offline_guard(self):
            for provider in PROVIDERS:
                credit = shared_fixtures.credit_exhaustion_fixture(provider)
                auth = fixture.invoke(provider, outcome="auth")
                func = fixture.invoke(provider, outcome="functional")

                self.assertEqual(credit.outcome, "credit_exhaustion")
                self.assertEqual(credit.classification, "availability")
                self.assertEqual(credit.availability_category, "quota")
                pairs = {(r.classification, r.availability_category) for r in (credit, auth, func)}
                self.assertEqual(len(pairs), 3, pairs)
                self.assertNotEqual(credit.availability_category, auth.availability_category)
                self.assertNotEqual(credit.classification, func.classification)

    def test_ac03_classification_covers_every_classifier_category(self) -> None:
        """Labels follow availability.classify for every category it can return, not a hand-kept table."""
        cases = [
            (0, "", [], "success"),
            (1, "Validation assertion failed", [], "functional"),
            (1, "error: unknown option '--frobnicate'", [], "configuration"),
            (127, "Provider executable disappeared after preflight", [], "availability"),
            (3, "exit three", [3], "availability"),
            (1, "HTTP 429 rate limit exceeded", [], "availability"),
            (1, "Authentication required: please log in", [], "availability"),
            (1, "server overloaded", [], "availability"),
        ]
        seen = set()
        with offline_guard(self):
            for code, text, retry, label in cases:
                category = availability.classify(code, text, retry)
                seen.add(category)
                self.assertEqual(shared_fixtures.classify_outcome(code, category), label, (code, text, category))
            for category in shared_fixtures.AVAILABILITY_EVENTS:
                self.assertEqual(shared_fixtures.classify_outcome(1, category), "availability", category)
        self.assertLessEqual({*availability.CATEGORIES, "configured_exit", "missing_cli", "configuration", None}, seen)

    def test_ac04_offline_guard_detects_processes_sockets_and_writes(self) -> None:
        """The guard wrapped around every fixture test is not vacuous."""
        target = self.temp_dir() / "probe.txt"
        attempts = (
            lambda: subprocess.run(["python", "--version"], check=False),
            lambda: socket.create_connection(("127.0.0.1", 9)),
            lambda: os.system("echo offline"),
            lambda: target.write_text("x", encoding="utf-8"),
            lambda: target.open("w", encoding="utf-8"),
            lambda: open(target, "a", encoding="utf-8"),
            lambda: os.open(target, os.O_WRONLY | os.O_CREAT),
            lambda: target.touch(),
            lambda: target.parent.joinpath("sub").mkdir(),
            lambda: os.replace(target, target),
            lambda: os.remove(target),
            lambda: shutil.rmtree(target.parent),
        )
        with offline_guard(self, verify=False) as violations:
            for attempt in attempts:
                with self.assertRaises(AssertionError):
                    attempt()
        self.assertEqual(len(violations), len(attempts), violations)
        self.assertFalse(target.exists())
        self.assertEqual(os.listdir(target.parent), [])


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Task004SharedFixturesTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
