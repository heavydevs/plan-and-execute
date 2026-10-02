#!/usr/bin/env python3
"""Self-test for tools/routing_eval.py validate-predeclaration (TODO 021).

Proves the committed predeclaration validates and that edits after a recorded
measurement digest, schema violations and loosened guard rails all fail.
Works on temp copies only; the committed files are never modified.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "routing_eval.py"
SOURCE = ROOT / "docs" / "research" / "routing-eval"
FILES = ("thresholds.json", "corpus-manifest.json", "PREDECLARATION.md")
ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
FAILURES: list[str] = []


def run(*args: str, repo: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOL), "--repo-root", str(repo), *args],
        cwd=str(ROOT), capture_output=True, text=True, env=ENV, timeout=60,
    )


def check(name: str, condition: bool, detail: str = "") -> None:
    print(f"{'PASS' if condition else 'FAIL'} {name}")
    if not condition:
        FAILURES.append(f"{name}: {detail[:400]}")


def fresh(base: Path, label: str) -> Path:
    directory = base / label / "docs" / "research" / "routing-eval"
    directory.mkdir(parents=True)
    for name in FILES:
        shutil.copyfile(SOURCE / name, directory / name)
    return base / label


def edit_json(path: Path, mutate) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    mutate(data)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def repin_doc(repo: Path) -> None:
    """Simulate a careful editor who also refreshes PREDECLARATION.md digests."""
    directory = repo / "docs" / "research" / "routing-eval"
    digests = dict(line.split("=", 1) for line in run("digest", repo=repo).stdout.split())
    doc = directory / "PREDECLARATION.md"
    text = doc.read_text(encoding="utf-8")
    rows = {"thresholds.json": digests["thresholds_sha256"], "corpus-manifest.json": digests["corpus_manifest_sha256"]}
    for name, value in rows.items():
        text = re.sub(rf"(\| `{re.escape(name)}` \| `)[0-9a-f]{{64}}(`)", rf"\g<1>{value}\g<2>", text)
    doc.write_text(text, encoding="utf-8")


def expect_invalid(name: str, repo: Path, needle: str) -> None:
    result = run("validate-predeclaration", repo=repo)
    check(name, result.returncode != 0 and needle in result.stderr, result.stdout + result.stderr)


def main() -> int:
    committed = run("validate-predeclaration")
    match = re.search(r"^thresholds_sha256=([0-9a-f]{64})$", committed.stdout, re.M)
    check("committed predeclaration validates and prints thresholds digest", committed.returncode == 0 and bool(match),
          committed.stdout + committed.stderr)
    check("committed directory has no measurement ledger yet", not (SOURCE / "measurements.jsonl").exists())

    base = Path(tempfile.mkdtemp(prefix="rev"))
    try:
        # Post-measurement threshold edit: the core immutability guarantee.
        repo = fresh(base, "a")
        directory = repo / "docs" / "research" / "routing-eval"
        check("temp copy validates", run("validate-predeclaration", repo=repo).returncode == 0)
        recorded = run("record-measurement", "--run-id", "shadow-1", repo=repo)
        ledger = directory / "measurements.jsonl"
        entry = json.loads(ledger.read_text(encoding="utf-8").splitlines()[0]) if ledger.is_file() else {}
        check("record-measurement stores current thresholds digest",
              recorded.returncode == 0 and bool(match) and entry.get("thresholds_sha256") == match.group(1),
              recorded.stdout + recorded.stderr)
        check("unchanged files still validate after measurement", run("validate-predeclaration", repo=repo).returncode == 0)
        duplicate = run("record-measurement", "--run-id", "shadow-1", repo=repo)
        check("duplicate run id refused", duplicate.returncode != 0 and "already recorded" in duplicate.stderr)
        edit_json(directory / "thresholds.json", lambda d: d["thresholds"]["regression_margin"].__setitem__("value", 0.03))
        repin_doc(repo)
        expect_invalid("threshold edit after recorded measurement fails", repo, "changed after measurement run shadow-1")
        sealed = run("seal", repo=repo)
        check("seal refused after measurement", sealed.returncode != 0 and "frozen" in sealed.stderr)

        # Post-measurement corpus edit, even when re-sealed digests look consistent.
        repo = fresh(base, "b")
        directory = repo / "docs" / "research" / "routing-eval"
        run("record-measurement", "--run-id", "shadow-1", repo=repo)
        edit_json(directory / "corpus-manifest.json", lambda d: d["categories"][0].__setitem__("segment", "guarded"))
        expect_invalid("corpus edit after measurement breaks pinned manifest digest", repo, "corpus_manifest.sha256")
        expect_invalid("corpus edit after measurement is reported against the run", repo, "corpus_manifest_sha256 changed after measurement")

        # Before measurement: an unpinned edit still fails until digests are refreshed.
        repo = fresh(base, "c")
        directory = repo / "docs" / "research" / "routing-eval"
        edit_json(directory / "thresholds.json", lambda d: d.__setitem__("decision_rule", d["decision_rule"] + " "))
        expect_invalid("pre-measurement edit without refreshed digest fails", repo, "does not record current thresholds_sha256")
        repin_doc(repo)
        check("pre-measurement edit with refreshed digests validates", run("validate-predeclaration", repo=repo).returncode == 0)

        # Schema and guard-rail negatives (no ledger, digests refreshed so only the schema can fail).
        cases = [
            ("missing why_conservative fails", "thresholds.json",
             lambda d: d["thresholds"]["material_gain"].pop("why_conservative"), "material_gain.why_conservative"),
            ("loosened regression margin fails", "thresholds.json",
             lambda d: d["thresholds"]["regression_margin"].__setitem__("value", 0.1), "regression_margin.value"),
            ("nonzero floor violations fail", "thresholds.json",
             lambda d: d["thresholds"]["under_routing_limit"]["value"].__setitem__("floor_violation_max_count", 1), "floor_violation_max_count"),
            ("floor_locked safe segment fails", "thresholds.json",
             lambda d: d["thresholds"]["safe_segments"]["value"].append("floor_locked"), "can never be safe"),
            ("non-PAT003 metric field fails", "thresholds.json",
             lambda d: d["metrics"]["latency_p95"]["fields"].append("wall_time_ms"), "not PAT003 telemetry fields"),
            ("missing threshold fails", "thresholds.json",
             lambda d: d["thresholds"].pop("minimum_sample"), "minimum_sample: missing"),
            ("wrong expected floor fails", "corpus-manifest.json",
             lambda d: d["categories"][4]["floor_source"].__setitem__("expected_floor", {"tier": "standard", "effort": "medium"}), "!= minimum_route"),
            ("unknown segment fails", "corpus-manifest.json",
             lambda d: d["categories"][0].__setitem__("segment", "nowhere"), "must name a declared segment"),
            ("missing required category fails", "corpus-manifest.json",
             lambda d: d.__setitem__("categories", [c for c in d["categories"] if c["name"] != "vision_ui"]), "missing vision_ui"),
        ]
        for index, (name, file_name, mutate, needle) in enumerate(cases):
            repo = fresh(base, f"s{index}")
            directory = repo / "docs" / "research" / "routing-eval"
            edit_json(directory / file_name, mutate)
            if file_name == "corpus-manifest.json":
                run("seal", repo=repo)
            repin_doc(repo)
            expect_invalid(name, repo, needle)
    finally:
        shutil.rmtree(base, ignore_errors=True)

    if FAILURES:
        print(f"routing_eval predeclaration self-test: {len(FAILURES)} failure(s)", file=sys.stderr)
        for failure in FAILURES:
            print(f"  {failure}", file=sys.stderr)
        return 1
    print("routing_eval predeclaration self-test: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
