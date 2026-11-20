#!/usr/bin/env python3
"""Offline source/contract coverage and negative-fixture regression tests (task 002, corrected by task 003).

Every fixture asserts three states instead of only describing them:
- historical_baseline: the committed, unchanged plan inputs satisfy the invariant and pass coverage;
- current_code: what check_delivery.structural alone does with the changed input (observed, not assumed);
- expected_new_behavior: what baseline_contracts.run_source_and_contract_coverage does with it.
The contract text must name the observed outcomes, so it cannot drift from the code under test.

The unknown-source and INDEX-pin fixtures overlap delivery_gate_self_test (test_unknown_source,
test_stale_report_hash). Here they add the coverage-wrapper path and message-level assertions.
Report byte drift runs in a temporary copy of the plan inputs; the repository is never written.
"""
from __future__ import annotations

import contextlib
import copy
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import baseline_contracts as bc
import check_delivery as cd

TASK_INPUTS = (cd.DOC / "TASK_INPUTS.json").as_posix()
PLAN_SPEC = (cd.DOC / "PLAN1_SPEC.json").as_posix()
INDEX = (cd.PREP / "INDEX.json").as_posix()
SOURCES = (cd.PREP / "SOURCES.json").as_posix()
ARCH = (cd.PREP / "ARCHITECTURE_AND_SCOPE.md").as_posix()
FIXTURE_KEYS = {"historical_baseline", "current_code", "expected_new_behavior"}


def repo_json(rel: str):
    return cd.load(cd.local(REPO_ROOT, rel))


def structural_outcome(root: Path) -> str:
    """Observed behaviour of the unchanged delivery gate (the current code) on the given inputs."""
    try:
        cd.structural(root, native=False)
    except cd.GateError as exc:
        return f"rejects: {exc}"
    except KeyError as exc:
        return f"raises KeyError: {exc}"
    return "accepts"


@contextlib.contextmanager
def patched_json(filename: str, mutator):
    """Serve a mutated copy of one plan JSON file through check_delivery.load."""
    original = cd.load

    def patched(path: Path):
        data = original(path)
        return mutator(copy.deepcopy(data)) if path.name == filename else data

    with patch.object(cd, "load", side_effect=patched):
        yield REPO_ROOT


@contextlib.contextmanager
def temp_repo():
    """Copy only the files structural() and the coverage wrapper read, so report bytes can change."""
    index = repo_json(INDEX)
    names = {TASK_INPUTS, PLAN_SPEC, (cd.DOC / "FEATURE_SEED.json").as_posix(), INDEX, SOURCES}
    names |= {r[key] for r in index["reports"] for key in ("report", "decision_record")}
    names |= {p for entry in cd.catalog(REPO_ROOT).values() for p in entry["prepared_reports"]}
    with tempfile.TemporaryDirectory(prefix="pae-t002-") as tmp:
        root = Path(tmp).resolve()
        for name in sorted(names):
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(cd.local(REPO_ROOT, name), target)
        yield root


def rewrite_json(root: Path, rel: str, mutator) -> None:
    path = cd.local(root, rel)
    data = mutator(json.loads(path.read_text(encoding="utf-8")))
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def drift_bytes(root: Path, rel: str) -> None:
    path = cd.local(root, rel)
    path.write_bytes(path.read_bytes() + b"\nContent changed after the hash was pinned.\n")


class Task002CoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.baseline = bc.run_source_and_contract_coverage(REPO_ROOT, native=False)
        cls.catalog = cd.catalog(REPO_ROOT)
        cls.spec = repo_json(PLAN_SPEC)
        cls.index = repo_json(INDEX)
        sources = repo_json(SOURCES)
        cls.source_ids = {s["id"] for s in (sources["sources"] if isinstance(sources, dict) else sources)}

    def assert_contract(self, contract: dict, observed: str, new_message: str) -> None:
        self.assertEqual(set(contract), FIXTURE_KEYS)
        verdict = observed.split(":", 1)[0]
        self.assertTrue(contract["current_code"].startswith(f"check_delivery.structural {verdict}"),
                        f"current_code {contract['current_code']!r} does not describe observed {observed!r}")
        self.assertIn(new_message, contract["expected_new_behavior"])

    def check_fixture(self, contract: dict, *, baseline_holds: bool, changed_input, current: str,
                      new_error: type[Exception], new_message: str) -> None:
        # Historical baseline: the committed inputs satisfy the invariant and pass the coverage gate.
        self.assertTrue(baseline_holds, contract["historical_baseline"])
        self.assertEqual(self.baseline["status"], "passed")
        with changed_input() as root:
            observed = structural_outcome(root)  # current code on the changed input
            self.assertRegex(observed, current)
            with self.assertRaisesRegex(new_error, re.escape(new_message)):  # expected new behaviour
                bc.run_source_and_contract_coverage(root, native=False)
        self.assert_contract(contract, observed, new_message)

    def test_imports_check_delivery_helpers_and_passes_on_repo(self) -> None:
        contract = {
            "historical_baseline": "Committed plan inputs: every TASK_INPUTS task appears once in PLAN1_SPEC",
            "current_code": "check_delivery.structural accepts the committed plan inputs",
            "expected_new_behavior": "coverage passed for every TASK_INPUTS task, with every pinned prepared report verified",
        }
        self.assertIs(bc.structural, cd.structural)
        self.assertIs(bc.verified_files, cd.verified_files)
        self.assertEqual(len(self.catalog), len(self.spec["tasks"]))
        observed = structural_outcome(REPO_ROOT)
        self.assertEqual(observed, "accepts")
        result = self.baseline
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["structural"]["prepared_research_reports"], 32)
        self.assertEqual(result["tasks_checked"], len(self.catalog))
        self.assertEqual(result["tasks_checked"], result["structural"]["tasks"])
        self.assertGreater(result["prepared_reports_pinned"], 0)
        self.assertEqual(result["prepared_reports_pinned"] + result["prepared_reports_unpinned"],
                         sum(len(e["prepared_reports"]) for e in self.catalog.values()))
        self.assertFalse(result["independent_review_fabricated"])
        self.assert_contract(contract, observed, "passed")

    def test_negative_unknown_sources_id_rejected(self) -> None:
        contract = {
            "historical_baseline": "Every INDEX.json report source_id is a SOURCES.json id",
            "current_code": "check_delivery.structural rejects an INDEX report that cites E999",
            "expected_new_behavior": "coverage rejects: Unknown or insufficient research sources",
        }

        def mutate(data):
            data["reports"][0]["source_ids"].append("E999")
            return data

        self.check_fixture(
            contract,
            baseline_holds="E999" not in self.source_ids
            and all(set(r["source_ids"]) <= self.source_ids for r in self.index["reports"]),
            changed_input=lambda: patched_json("INDEX.json", mutate),
            current=r"^rejects: Unknown or insufficient research sources$",
            new_error=cd.GateError,
            new_message="Unknown or insufficient research sources",
        )

    def test_negative_report_hash_drift_rejected(self) -> None:
        report = self.index["reports"][0]
        pin_baseline = cd.text_sha(cd.local(REPO_ROOT, report["report"])) == report["report_sha256"]
        with self.subTest("INDEX pin changed"):
            def mutate_index(data):
                data["reports"][0]["report_sha256"] = "0" * 64
                return data

            self.check_fixture(
                {
                    "historical_baseline": "INDEX.json report_sha256 equals the report's LF-blob sha256",
                    "current_code": "check_delivery.structural rejects a zeroed INDEX report_sha256",
                    "expected_new_behavior": "coverage rejects: Stale research hash",
                },
                baseline_holds=pin_baseline,
                changed_input=lambda: patched_json("INDEX.json", mutate_index),
                current=r"^rejects: Stale research hash: ",
                new_error=cd.GateError,
                new_message="Stale research hash",
            )
        with self.subTest("TASK_INPUTS research_sha256 changed (INDEX/TASK_INPUTS cross-link)"):
            entry = next(e for e in self.catalog.values() if e.get("research_sha256"))

            def mutate_task_inputs(data):
                next(t for t in data["tasks"] if t["id"] == entry["id"])["research_sha256"] = "0" * 64
                return data

            self.check_fixture(
                {
                    "historical_baseline": "TASK_INPUTS research_sha256 equals the INDEX report_sha256 of its task",
                    "current_code": "check_delivery.structural rejects a zeroed TASK_INPUTS research_sha256",
                    "expected_new_behavior": "coverage rejects: Stale task/report link",
                },
                baseline_holds=entry["research_sha256"] in {r["report_sha256"] for r in self.index["reports"]},
                changed_input=lambda: patched_json("TASK_INPUTS.json", mutate_task_inputs),
                current=r"^rejects: Stale task/report link$",
                new_error=cd.GateError,
                new_message="Stale task/report link",
            )

    def test_negative_index_pinned_report_byte_drift_rejected(self) -> None:
        report = self.index["reports"][0]

        @contextlib.contextmanager
        def changed_bytes():
            with temp_repo() as root:
                drift_bytes(root, report["report"])
                yield root

        self.check_fixture(
            {
                "historical_baseline": "The committed INDEX-pinned report matches its LF-blob pin",
                "current_code": "check_delivery.structural rejects report bytes changed after INDEX pinned them",
                "expected_new_behavior": "coverage rejects: Stale research hash",
            },
            baseline_holds=cd.text_sha(cd.local(REPO_ROOT, report["report"])) == report["report_sha256"],
            changed_input=changed_bytes,
            current=r"^rejects: Stale research hash: " + re.escape(report["report"]) + "$",
            new_error=cd.GateError,
            new_message="Stale research hash",
        )

    def test_negative_task_inputs_pinned_report_byte_drift_rejected(self) -> None:
        """The wrapper's own pin check is live: structural() never reads a non-INDEX research pin."""
        self.assertNotIn(ARCH, {r["report"] for r in self.index["reports"]})
        self.assertIsNone(self.catalog["002"].get("research_report"))

        @contextlib.contextmanager
        def pinned_then_changed():
            with temp_repo() as root:
                def pin(data):
                    entry = next(t for t in data["tasks"] if t["id"] == "002")
                    entry["research_report"] = ARCH
                    entry["research_sha256"] = cd.text_sha(cd.local(root, ARCH))
                    return data

                rewrite_json(root, TASK_INPUTS, pin)
                pinned = bc.run_source_and_contract_coverage(root, native=False)
                self.assertEqual(pinned["prepared_reports_pinned"], self.baseline["prepared_reports_pinned"] + 1)
                drift_bytes(root, ARCH)
                yield root

        self.check_fixture(
            {
                "historical_baseline": "A prepared report pinned only by TASK_INPUTS research_sha256 matches its pin",
                "current_code": "check_delivery.structural accepts report bytes changed after TASK_INPUTS pinned them",
                "expected_new_behavior": f"coverage rejects: Stale prepared_report hash: {ARCH}",
            },
            baseline_holds=cd.local(REPO_ROOT, ARCH).is_file(),
            changed_input=pinned_then_changed,
            current=r"^accepts$",
            new_error=cd.GateError,
            new_message=f"Stale prepared_report hash: {ARCH}",
        )

    def test_negative_requirement_without_consumer_rejected(self) -> None:
        def mutate(data):
            data["requirements"].append({"id": "R999", "text": "Unconsumed requirement"})
            return data

        consumed = {r for t in self.spec["tasks"] for r in t["requirement_ids"]}
        self.check_fixture(
            {
                "historical_baseline": "Every PLAN1_SPEC.json requirement is consumed by at least one task",
                "current_code": "check_delivery.structural rejects R999, which no task consumes",
                "expected_new_behavior": "coverage rejects: Requirement coverage mismatch",
            },
            baseline_holds={r["id"] for r in self.spec["requirements"]} == consumed and "R999" not in consumed,
            changed_input=lambda: patched_json("PLAN1_SPEC.json", mutate),
            current=r"^rejects: Requirement coverage mismatch$",
            new_error=cd.GateError,
            new_message="Requirement coverage mismatch",
        )

    def test_negative_task_without_prepared_report_rejected(self) -> None:
        """AC07 is enforced by this wrapper; check_delivery.structural accepts or crashes on these inputs."""
        baseline_holds = all(isinstance(e.get("prepared_reports"), list) and e["prepared_reports"]
                             and len(set(e["prepared_reports"])) == len(e["prepared_reports"])
                             for e in self.catalog.values())
        cases = (
            ("empty list", lambda e: e.__setitem__("prepared_reports", []), r"^accepts$",
             "check_delivery.structural accepts a task 002 entry with an empty prepared_reports list",
             "Task 002 missing prepared_reports"),
            ("missing key", lambda e: e.pop("prepared_reports"), r"^raises KeyError: 'prepared_reports'$",
             "check_delivery.structural raises KeyError for a task 002 entry without prepared_reports",
             "Task 002 missing prepared_reports"),
            ("duplicate path", lambda e: e["prepared_reports"].append(e["prepared_reports"][0]), r"^accepts$",
             "check_delivery.structural accepts a task 002 entry that lists the same prepared report twice",
             "Task 002 has duplicate prepared_reports"),
        )
        for label, change, current, current_text, message in cases:
            with self.subTest(label):
                def mutate(data, change=change):
                    change(next(t for t in data["tasks"] if t["id"] == "002"))
                    return data

                self.check_fixture(
                    {
                        "historical_baseline": "Every TASK_INPUTS task lists distinct prepared_reports",
                        "current_code": current_text,
                        "expected_new_behavior": f"coverage rejects before structural runs: {message}",
                    },
                    baseline_holds=baseline_holds,
                    changed_input=lambda mutate=mutate: patched_json("TASK_INPUTS.json", mutate),
                    current=current,
                    new_error=bc.PreflightError,
                    new_message=message,
                )

    def test_negative_missing_082_review_gate_rejected(self) -> None:
        def mutate(data):
            t082 = next(t for t in data["tasks"] if f"{t['id']:03}" == "082")
            t082["dependencies"] = [d for d in t082["dependencies"] if d != "088"]
            return data

        t082 = next(t for t in self.spec["tasks"] if f"{t['id']:03}" == "082")
        self.check_fixture(
            {
                "historical_baseline": "Task 082 depends on extension review gate 088",
                "current_code": "check_delivery.structural rejects task 082 without its 088 dependency",
                "expected_new_behavior": "coverage rejects: Missing extension review gate 088",
            },
            baseline_holds="088" in t082["dependencies"],
            changed_input=lambda: patched_json("PLAN1_SPEC.json", mutate),
            current=r"^rejects: Missing extension review gate 088$",
            new_error=cd.GateError,
            new_message="Missing extension review gate 088",
        )

    def test_missing_authenticated_provider_is_limitation_not_failure_or_fake_review(self) -> None:
        contract = {
            "historical_baseline": "Coverage without provider status records no execution limitation",
            "current_code": "check_delivery.structural accepts; it has no provider or review concept",
            "expected_new_behavior": "coverage passed, recording each unauthenticated provider as a limitation",
        }
        self.assertEqual(self.baseline["execution_limitations"], [])
        observed = structural_outcome(REPO_ROOT)
        self.assertEqual(observed, "accepts")
        self.assertEqual(self.baseline["structural"]["independent_reviews"], "not performed by this check")
        result = bc.run_source_and_contract_coverage(
            REPO_ROOT,
            native=False,
            provider_status={
                "claude": {"authenticated": False, "reason": "not logged in"},
                "codex": {"authenticated": False, "reason": "not logged in"},
            },
        )
        self.assertEqual(result["status"], "passed")
        self.assertFalse(result["independent_review_fabricated"])
        self.assertEqual(len(result["execution_limitations"]), 2)
        self.assertIn("Missing authenticated provider 'claude'", result["execution_limitations"][0])
        self.assertIn("without fabricating independent review", result["execution_limitations"][1])
        self.assert_contract(contract, observed, "passed")


if __name__ == "__main__":
    unittest.main(verbosity=2)
