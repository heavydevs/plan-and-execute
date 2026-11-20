#!/usr/bin/env python3
"""Narrow, audited resource-map reconciliation for the checkpoint branch.

Never accepts arbitrary new paths, a changed validation definition, missing inputs,
or unreadable data. This command does NOT confer model-review approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skill/plan-and-execute/scripts"
sys.path.insert(0, str(SCRIPTS))
import service_map  # noqa: E402

# Paths observed and inspected against the workflow, support test suites and
# Node dependency manifest for the 015 validation migration on 2026-11-20.
# Any newly discovered test/build/CI path requires a separate inventory review.
REVIEWED_CHANGED = frozenset({
    ".github/workflows/chatgpt-task-gate.yml",
    ".github/workflows/chatgpt-independent-review.yml",
    ".github/workflows/chatgpt-offline-review.yml",
    ".github/workflows/chatgpt-snapshot-export.yml",
    ".github/workflows/chatgpt-offline-review.yml",
    ".github/workflows/ci.yml",
    ".github/workflows/publish.yml",
    "docs/plans/20261028-skill-optimization/history/pre-research-conversion/support/delivery_gate_self_test.py",
    "docs/plans/20261028-skill-optimization/support/delivery_gate_self_test.py",
    "docs/plans/20261028-skill-optimization/support/research_readiness_self_test.py",
    "docs/plans/20261028-skill-optimization/support/review_dispatch_self_test.py",
    "package-lock.json",
    "package.json",
    "skill/plan-and-execute/scripts/artifact_concision_self_test.py",
    "skill/plan-and-execute/scripts/assistant_triage_self_test.py",
    "skill/plan-and-execute/scripts/availability_self_test.py",
    "skill/plan-and-execute/scripts/companion_self_test.py",
    "skill/plan-and-execute/scripts/configure_self_test.py",
    "skill/plan-and-execute/scripts/context_self_test.py",
    "skill/plan-and-execute/scripts/frontier_self_test.py",
    "skill/plan-and-execute/scripts/jobctl_self_test.py",
    "skill/plan-and-execute/scripts/keepalivectl_self_test.py",
    "skill/plan-and-execute/scripts/observer_self_test.py",
    "skill/plan-and-execute/scripts/pattern_self_test.py",
    "skill/plan-and-execute/scripts/progress_runner_self_test.py",
    "skill/plan-and-execute/scripts/progress_watch_self_test.py",
    "skill/plan-and-execute/scripts/promotion_self_test.py",
    "skill/plan-and-execute/scripts/routing_config_self_test.py",
    "skill/plan-and-execute/scripts/routing_self_test.py",
    "skill/plan-and-execute/scripts/self_test.py",
    "skill/plan-and-execute/scripts/study_self_test.py",
    "skill/plan-and-execute/scripts/task_memory_self_test.py",
    "skill/plan-and-execute/scripts/telemetry_self_test.py",
    "skill/plan-and-execute/scripts/token_efficiency_self_test.py",
    "skill/plan-and-execute/scripts/validatectl_self_test.py",
    "skill/plan-and-execute/scripts/workload_routing_self_test.py",
    "test/companion.test.js",
    "test/installer.test.js",
    "test/optimization/context_learning_self_test.py",
    "tools/run-skill-self-test.js",
})


def reconcile() -> dict:
    map_file = ROOT / ".ai-work/SERVICE_MAP.md"
    before, data = service_map.load_map(map_file)
    errors = service_map.validate_data(data)
    if errors:
        raise service_map.MapError("Map inventory invalid: " + "; ".join(errors[:4]))
    expected_ids = {"P1_TESTS_015", "P1_015"}
    validations = {str(v.get("id")): v for v in data.get("validations", []) if isinstance(v, dict)}
    for vid in expected_ids:
        v = validations.get(vid)
        if not v or not v.get("command") or not isinstance(v.get("resources"), list):
            raise service_map.MapError("Missing reviewed validation: " + vid)
    sidecar = service_map.index_path(map_file, ROOT)
    if not sidecar.is_file() or sidecar.is_symlink():
        raise service_map.MapError("Index unavailable: cannot establish changed-input scope")
    fresh, signatures, truncated, changed = service_map.current_status(ROOT, map_file, data)
    if truncated:
        raise service_map.MapError("Unreadable discovered map input")
    unknown = sorted(set(changed) - REVIEWED_CHANGED)
    if unknown:
        raise service_map.MapError("Unknown changed test/build/CI input(s): " + ", ".join(unknown))
    if not fresh and not changed:
        raise service_map.MapError("Stale digest without an auditable changed-input list")
    if fresh:
        return {"status": "fresh", "changed": [], "snapshot_digest": data["snapshot"]["digest"]}
    # No new service or validation was found in the reviewed changed sources;
    # existing P1_015 and P1_TESTS_015 map entries remain unchanged.
    args = argparse.Namespace(repo_root=str(ROOT), map=str(map_file.relative_to(ROOT)), confirm_reconciled=True)
    status = service_map.cmd_stamp(args)
    if status:
        raise service_map.MapError("Snapshot stamp failed")
    _text, stamped = service_map.load_map(map_file)
    verified, _, partial, new_changed = service_map.current_status(ROOT, map_file, stamped)
    if not verified or partial or new_changed:
        raise service_map.MapError("Snapshot remains stale after stamping")
    return {"status": "stamped", "changed": changed,
            "snapshot_digest": stamped["snapshot"]["digest"],
            "source_count": stamped["snapshot"]["source_count"],
            "evidence_kind": "reconciled_resource_inventory_not_model_review"}


def main():
    try:
        print(json.dumps(reconcile(), indent=2, ensure_ascii=False))
    except (service_map.MapError, OSError, ValueError, KeyError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
