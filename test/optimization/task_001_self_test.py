#!/usr/bin/env python3
"""Offline regression and negative-fixture tests for task 001 preflight contracts."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import baseline_contracts as bc


class Task001PreflightTests(unittest.TestCase):
    """Verify deterministic preflight, negative fixtures, drift reporting, and provider limits.

    Every fixture records:
    - historical_baseline: prior 0.11.0 / BASELINE_INVENTORY.json state
    - current_code: current workspace or synthetic tree state
    - expected_new_behavior: deterministic preflight contract behavior
    """

    def _make_synthetic_repo(self, tmp: Path) -> dict[str, str]:
        prep_rel = "docs/research/20261028-skill-optimization/prepared-research/006-activation-intake.md"
        prep_path = tmp / prep_rel
        prep_path.parent.mkdir(parents=True, exist_ok=True)
        prep_path.write_text("# 006 Prepared Decision\n", encoding="utf-8")
        prep_sha = bc.lf_sha256(prep_path)

        src_rel = "skill/plan-and-execute/scripts/requestctl.py"
        src_path = tmp / src_rel
        src_path.parent.mkdir(parents=True, exist_ok=True)
        src_path.write_text("print('ok')\n", encoding="utf-8")
        src_sha = bc.raw_sha256(src_path)

        chk_rel = "skill/plan-and-execute/scripts/routing_self_test.py"
        chk_path = tmp / chk_rel
        chk_path.write_text("print('pass')\n", encoding="utf-8")

        inv_path = tmp / bc.BASELINE_INVENTORY_PATH
        inv_path.parent.mkdir(parents=True, exist_ok=True)
        inv_path.write_text(
            json.dumps({
                "schema_version": 1,
                "files": [
                    {"path": src_rel, "category": "scripts", "sha256": "0" * 64},
                ],
            }),
            encoding="utf-8",
        )

        idx_path = tmp / bc.PREPARED_INDEX_PATH
        idx_path.write_text(
            json.dumps({
                "schema_version": 1,
                "reports": [
                    {
                        "task_id": "006",
                        "report": prep_rel,
                        "report_sha256": prep_sha,
                    }
                ],
            }),
            encoding="utf-8",
        )

        task_inputs_path = tmp / bc.TASK_INPUTS_PATH
        task_inputs_path.parent.mkdir(parents=True, exist_ok=True)
        task_inputs_path.write_text(
            json.dumps({
                "schema_version": 2,
                "plan_mode": "single_implementation",
                "tasks": [
                    {
                        "id": "006",
                        "prepared_reports": [prep_rel],
                        "research_report": prep_rel,
                        "research_sha256": prep_sha,
                        "required_checks": [["python", chk_rel]],
                        "planned_new_files": [],
                        "input_contract": [
                            {"path": prep_rel, "availability": "existing_baseline_or_current_file"},
                            {
                                "path": src_rel,
                                "availability": "existing_baseline_or_current_file",
                                "sha256": src_sha,
                            },
                        ],
                    }
                ],
            }),
            encoding="utf-8",
        )
        return {"prep_rel": prep_rel, "src_rel": src_rel, "chk_rel": chk_rel}

    def test_current_tree_preflight_passes_and_reports_inventory_drift(self) -> None:
        fixture_contract = {
            "historical_baseline": "188 files pinned in BASELINE_INVENTORY.json at base_tree f4b5a228...",
            "current_code": "131/188 raw file hashes changed in current working tree",
            "expected_new_behavior": "Preflight passes and lists all 131 drifted paths without failing",
        }
        self.assertIn("131/188", fixture_contract["current_code"])
        result = bc.run_preflight(REPO_ROOT, task_id="001")
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["checked_tasks"], ["001"])
        self.assertEqual(result["inventory"]["total"], 188)
        self.assertEqual(result["inventory"]["changed_count"], 131)
        self.assertEqual(len(result["inventory"]["drift"]), 131)
        self.assertFalse(result["independent_review_fabricated"])

    def test_negative_stale_prepared_report_hash_rejected(self) -> None:
        fixture_contract = {
            "historical_baseline": "Prepared report matched INDEX.json and TASK_INPUTS research_sha256",
            "current_code": "Prepared report content edited after hash pinning",
            "expected_new_behavior": "Preflight fails with stale prepared_report hash error",
        }
        self.assertTrue(fixture_contract["expected_new_behavior"])
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths = self._make_synthetic_repo(root)
            (root / paths["prep_rel"]).write_text("# Mutated report\n", encoding="utf-8")
            with self.assertRaisesRegex(bc.PreflightError, "Stale prepared_report hash"):
                bc.run_preflight(root, task_id="006")

    def test_negative_stale_input_contract_hash_rejected(self) -> None:
        fixture_contract = {
            "historical_baseline": "input_contract pinned source sha256 matched file",
            "current_code": "Pinned input_contract file modified without updating pin",
            "expected_new_behavior": "Preflight fails with stale input_contract hash error",
        }
        self.assertTrue(fixture_contract["expected_new_behavior"])
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths = self._make_synthetic_repo(root)
            (root / paths["src_rel"]).write_text("print('mutated')\n", encoding="utf-8")
            with self.assertRaisesRegex(bc.PreflightError, "Stale input_contract hash"):
                bc.run_preflight(root, task_id="006")

    def test_negative_missing_resource_rejected(self) -> None:
        fixture_contract = {
            "historical_baseline": "All existing_baseline_or_current_file inputs present",
            "current_code": "Required input_contract resource deleted from workspace",
            "expected_new_behavior": "Preflight fails with missing input_contract resource error",
        }
        self.assertTrue(fixture_contract["expected_new_behavior"])
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths = self._make_synthetic_repo(root)
            (root / paths["src_rel"]).unlink()
            with self.assertRaisesRegex(bc.PreflightError, "Missing input_contract resource"):
                bc.run_preflight(root, task_id="006")

    def test_negative_unsupported_cli_version_rejected(self) -> None:
        fixture_contract = {
            "historical_baseline": "Supported CLI versions python>=3.10, node>=18.0",
            "current_code": "Unsupported python 3.8.10 or node 14.21.0 reported",
            "expected_new_behavior": "Preflight fails with unsupported CLI version error",
        }
        self.assertTrue(fixture_contract["expected_new_behavior"])
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._make_synthetic_repo(root)
            with self.assertRaisesRegex(bc.PreflightError, "Unsupported CLI version"):
                bc.run_preflight(root, task_id="006", cli_versions={"python": "3.8.10", "node": "14.21.0"})

    def test_negative_broad_context_loading_rejected(self) -> None:
        fixture_contract = {
            "historical_baseline": "Worker loads only its assigned prepared_reports and inputs",
            "current_code": "Worker attempts to load transcript.jsonl or unassigned prepared report",
            "expected_new_behavior": "Preflight rejects broad context loading",
        }
        self.assertTrue(fixture_contract["expected_new_behavior"])
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._make_synthetic_repo(root)
            with self.assertRaisesRegex(bc.PreflightError, "Broad context loading rejected"):
                bc.run_preflight(
                    root,
                    task_id="006",
                    loaded_context={
                        "006": [
                            "docs/research/20261028-skill-optimization/prepared-research/008-primary-planning.md"
                        ]
                    },
                )
            with self.assertRaisesRegex(bc.PreflightError, "Broad context loading rejected"):
                bc.run_preflight(
                    root,
                    task_id="006",
                    loaded_context={"006": [".ai-work/logs/transcript.jsonl"]},
                )

    def test_missing_authenticated_provider_is_limitation_not_failure_or_fake_review(self) -> None:
        fixture_contract = {
            "historical_baseline": "Max-model planning gate blocked local preparation when provider unavailable",
            "current_code": "codex provider unauthenticated in offline environment",
            "expected_new_behavior": "Preflight passes, records explicit execution limitation, and never fabricates review",
        }
        self.assertTrue(fixture_contract["expected_new_behavior"])
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._make_synthetic_repo(root)
            result = bc.run_preflight(
                root,
                task_id="006",
                provider_status={"codex": {"authenticated": False, "reason": "offline/unauthenticated"}},
            )
            self.assertEqual(result["status"], "passed")
            self.assertFalse(result["independent_review_fabricated"])
            self.assertEqual(len(result["execution_limitations"]), 1)
            self.assertIn("codex", result["execution_limitations"][0])
            self.assertEqual(result["inventory"]["changed_count"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
