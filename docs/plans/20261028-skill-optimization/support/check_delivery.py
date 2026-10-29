#!/usr/bin/env python3
"""Read-only, plan-local checks. Prepared research is never implementation evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

DOC = Path("docs/plans/20261028-skill-optimization")
PREP = Path("docs/research/20261028-skill-optimization/prepared-research")
OUTPUT = Path("docs/research/20261028-skill-optimization/implementation")
CONTROL = Path(".ai-work/20261028-skill-study-provider-switch")
SECRET = re.compile(r"sk-[A-Za-z0-9_-]{12,}|Authorization\s*:\s*(?:Bearer|Basic)\s+[^\s<]+", re.I)


class GateError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise GateError(message)


def local(root: Path, value: str) -> Path:
    require(isinstance(value, str) and bool(value), "Empty relative path")
    p = Path(value)
    require(not p.is_absolute() and ".." not in p.parts and "\\" not in value,
            "Path must be repository-relative without traversal")
    require(bool(p.parts), "Empty path parts")
    target = root / p
    for n in range(1, len(p.parts) + 1):
        require(not (root.joinpath(*p.parts[:n])).is_symlink(), "Symlink is not evidence")
    require(target.resolve().is_relative_to(root.resolve()), "Path escapes repository")
    return target


def _unique(items):
    out = {}
    for k, v in items:
        require(k not in out, "Duplicate JSON key")
        out[k] = v
    return out


def load(path: Path):
    require(path.is_file(), f"Missing evidence: {path}")
    require(path.stat().st_size <= 4_000_000, "Oversized evidence")
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique,
                          parse_constant=lambda value: (_ for _ in ()).throw(GateError("Non-finite JSON")))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise GateError(f"Invalid JSON: {path.name}") from exc


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def catalog(root: Path):
    data = load(local(root, str(DOC / "TASK_INPUTS.json")))
    require(data.get("schema_version") == 2, "Unsupported task catalog")
    return {e["id"]: e for e in data["tasks"]}


def verified_files(root: Path, values, label="artifact") -> set[str]:
    require(isinstance(values, list) and bool(values), f"Missing hashed {label}s")
    names = set()
    for item in values:
        require(isinstance(item, dict), "Invalid artifact record")
        name = item.get("path", "")
        path = local(root, name)
        require(path.is_file(), f"Missing {label}: {name}")
        require(name not in names, "Duplicate artifact")
        require(sha(path) == item.get("sha256"), f"Stale {label} hash: {name}")
        names.add(name)
    return names


def code_fingerprint(root: Path, entry: dict) -> str:
    """Current product/test/config inputs; exclude generated logs, receipts and caches."""
    paths = set()
    for directory in ("skill", "bin", "lib", "test", "tools", ".github"):
        base = root / directory
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if any(part in {"__pycache__", "node_modules", ".git", ".pytest_cache"}
                   for part in p.relative_to(root).parts):
                continue
            if p.is_file() and p.suffix not in {".pyc", ".pyo"}:
                local(root, p.relative_to(root).as_posix())
                paths.add(p.relative_to(root).as_posix())
    for name in ("package.json", "package-lock.json", ".npmignore", ".gitignore"):
        if (root / name).is_file():
            paths.add(name)
    for name in entry.get("prepared_reports", []):
        paths.add(name)
    digest = hashlib.sha256()
    digest.update(json.dumps(entry, sort_keys=True, separators=(",", ":")).encode())
    for name in sorted(paths):
        p = local(root, name)
        require(p.is_file(), "Missing fingerprint input")
        digest.update(name.encode() + b"\0" + p.read_bytes() + b"\0")
    return digest.hexdigest()


def structural(root: Path, native: bool = True) -> dict:
    spec = load(local(root, str(DOC / "PLAN1_SPEC.json")))
    entries = catalog(root)
    tasks = {f"{t['id']:03}": t for t in spec["tasks"]}
    require(len(tasks) == len(spec["tasks"]) == len(entries) == 86, "Expected 86 unique tasks")
    require(set(tasks) == set(entries), "Task catalog mismatch")
    require(spec["autostart"] is False, "Research preparation must not autostart workers")
    require("single implementation" in spec["title"].lower(), "Not a single implementation plan")
    req = {r["id"] for r in spec["requirements"]}
    require(req == {v for t in tasks.values() for v in t["requirement_ids"]}, "Requirement coverage mismatch")
    for tid, task in tasks.items():
        require(entries[tid]["kind"] == "implementation", "Research task still present")
        require(all(dep in tasks and int(dep) < int(tid) for dep in task["dependencies"]),
                f"Invalid dependency graph: {tid}")
        require(bool(task["subtasks"]), "Missing internal checklist")
        require(bool(entries[tid]["required_checks"]), "Missing declared regression checks")
        require(all(isinstance(argv, list) and argv and all(isinstance(x, str) and x for x in argv)
                    for argv in entries[tid]["required_checks"]), "Invalid command argv")
        for name in entries[tid]["prepared_reports"]:
            require(local(root, name).is_file(), "Prepared decision missing")
        for key in ("output", "report"):
            local(root, entries[tid][key])
    require(tasks["001"]["model_tier"] != "max", "Global initial max-review blocker returned")
    require("whole-skill" in tasks["086"]["title"].lower(), "Whole-skill review must be last")
    sources = load(local(root, str(PREP / "SOURCES.json")))
    source_list = sources["sources"] if isinstance(sources, dict) else sources
    source_ids = {s["id"] for s in source_list}
    require(len(source_ids) == len(source_list), "Duplicate source ID")
    for source in source_list:
        for key in ("title", "publisher", "url", "accessed_at", "finding", "verification_scope"):
            require(isinstance(source.get(key), str) and source[key], "Incomplete source record")
        require(source["url"].startswith("https://"), "Invalid source URL")
        date.fromisoformat(source["accessed_at"])
    index = load(local(root, str(PREP / "INDEX.json")))
    features = load(local(root, str(DOC / "FEATURE_SEED.json")))["features"]
    require(len(index["reports"]) == len(features) == 32, "Expected 32 topic reports")
    expected = {f["implementation_task"] for f in features}
    require(expected == {x["task_id"] for x in index["reports"]}, "Topic coverage mismatch")
    for report in index["reports"]:
        tid, rid = report["task_id"], report["review_task"]
        verified_files(root, [{"path": report["report"], "sha256": report["report_sha256"]},
                              {"path": report["decision_record"], "sha256": report["decision_sha256"]}], "research")
        decision = load(local(root, report["decision_record"]))
        require(decision["implementation_task"] == tid, "Decision task mismatch")
        require(decision["implementation_status"] == "pending" and decision["independent_review_status"] == "pending",
                "Research claimed implementation or independent review")
        require(set(report["source_ids"]) <= source_ids and len(report["source_ids"]) >= 2,
                "Unknown or insufficient research sources")
        require(len(decision["alternatives"]) >= 2 and decision["implementation_steps"]
                and decision["proposed_acceptance_tests"], "Incomplete implementation decision")
        require(entries[tid]["research_report"] == report["report"]
                and entries[tid]["research_sha256"] == report["report_sha256"], "Stale task/report link")
        require(report["report"] in " ".join(tasks[tid]["implementation_guidance"])
                and report["report"] in tasks[tid]["subtasks"][0]["objective"], "Checklist lacks report link")
        require(entries[rid]["review_of"] == tid and entries[rid]["requires_independent_review"]
                and tasks[rid]["model_tier"] == "max" and tid in tasks[rid]["dependencies"],
                "Independent acceptance review lost")
    for tid in ("082", "083", "084", "085", "086"):
        require(not re.search(r"(create|generate|produce) (a |the )?(second|plan 2)",
                             tasks[tid]["title"] + " " + tasks[tid]["objective"], re.I), "Second-plan work remains")
    if native:
        manifest = load(local(root, str(CONTROL / "manifest.json")))
        require(manifest["title"] == spec["title"], "Native manifest was not replanned")
        actual = {t["id"]: t for t in manifest["tasks"]}
        require(set(actual) == set(tasks), "Native task set mismatch")
        for tid, target in tasks.items():
            for field in ("title", "objective", "dependencies", "implementation_guidance", "acceptance_criteria"):
                require(actual[tid][field] == target[field], f"Native projection mismatch: {tid}/{field}")
            for a, b in zip(actual[tid]["subtasks"], target["subtasks"]):
                require(a["title"] == b["title"] and a["objective"] == b["objective"], "Subtask projection mismatch")
            require(len(actual[tid]["subtasks"]) == len(target["subtasks"]), "Subtask count mismatch")
        require(sha(local(root, str(CONTROL / "REQUEST.md"))) == sha(local(root, str(DOC / "REQUEST_CURRENT.md"))),
                "Current request mismatch")
    return {"structural_check": "passed", "tasks": len(tasks), "prepared_research_reports": len(expected),
            "source_records": len(source_list), "independent_reviews": "not performed by this check",
            "implementation": "not performed by this check"}


def check(root: Path, task_id: str) -> dict:
    entries = catalog(root)
    require(task_id in entries, "Unknown task")
    entry = entries[task_id]
    packet = load(local(root, entry["output"]))
    require(packet.get("schema_version") == 2 and packet.get("task_id") == task_id
            and packet.get("kind") == "implementation", "Wrong receipt schema/task/kind")
    require(packet.get("status") == "completed", "Implementation is incomplete")
    require(isinstance(packet.get("summary"), str) and 0 < len(packet["summary"]) <= 1600, "Invalid summary")
    require(not SECRET.search(json.dumps(packet)), "Possible unredacted credential")
    verified_files(root, [{"path": entry["report"], "sha256": packet.get("outcome_sha256")}], "outcome")
    reviewed = verified_files(root, packet.get("prepared_inputs"), "prepared input")
    require(set(entry["prepared_reports"]) <= reviewed, "Prepared decisions were not pinned")
    if packet.get("changed_artifacts"):
        changed = verified_files(root, packet["changed_artifacts"], "changed project artifact")
    else:
        require(packet.get("no_changes_needed") is True and isinstance(packet.get("preservation_reason"), str)
                and 40 <= len(packet["preservation_reason"]) <= 800, "Missing implementation changes or justified preservation")
        changed = verified_files(root, packet.get("preserved_artifacts"), "preserved project artifact")
    require(any(name.startswith(("skill/", "bin/", "lib/", "test/", "tools/", ".github/"))
                or name in {"package.json", "package-lock.json", ".npmignore", "README.md", "README.pt-BR.md", "CHANGELOG.md"} for name in changed),
            "Research report is not implementation evidence")
    machine_path = str(OUTPUT / f"{task_id}-checks.json")
    machine = load(local(root, machine_path))
    require(packet.get("checks_sha256") == sha(local(root, machine_path)), "Check receipt hash mismatch")
    require(machine.get("schema_version") == 1 and machine.get("task_id") == task_id, "Wrong check receipt")
    require(machine.get("input_fingerprint") == code_fingerprint(root, entry), "Tests are stale for current code")
    require(machine.get("inputs_unchanged") is True, "Code changed during validation")
    results = machine.get("checks")
    require(isinstance(results, list) and [v.get("argv") for v in results] == entry["required_checks"],
            "Missing or substituted declared checks")
    for result in results:
        require(type(result.get("exit_code")) is int and result["exit_code"] == 0, "A declared check failed")
        verified_files(root, [{"path": result.get("log", ""), "sha256": result.get("log_sha256")}], "test log")
    covered = packet.get("acceptance_coverage", [])
    require(isinstance(covered, list) and {v.get("id") for v in covered} == set(entry["acceptance_ids"]),
            "Acceptance coverage mismatch")
    for case in covered:
        require(case.get("result") == "passed" and case.get("evidence"), "Unproven acceptance case")
        for name in case["evidence"]:
            require(local(root, name).is_file(), "Acceptance evidence missing")
    require(isinstance(packet.get("limitations"), list), "Missing verification limits")
    if entry["requires_independent_review"]:
        reviewer = packet.get("reviewer", {})
        require(reviewer.get("model_tier") == "max" and reviewer.get("fresh_context") is True,
                "Review requires actual fresh maximum-qualified worker")
        require(reviewer.get("provider") not in (None, "", "host", "simulated", "mock", "this_session"),
                "Independent reviewer was not dispatched")
        for field in ("provider", "model", "native_effort", "session_id"):
            require(isinstance(reviewer.get(field), str) and reviewer[field], "Review route missing")
        verified_files(root, [{"path": reviewer.get("dispatch_evidence", ""),
                               "sha256": reviewer.get("dispatch_sha256")}], "review dispatch")
        pinned = verified_files(root, packet.get("reviewed_inputs"), "reviewed input")
        if entry.get("review_of"):
            previous = entries[entry["review_of"]]
            require({previous["output"], previous["report"]} <= pinned, "Assigned implementation was not reviewed")
        require(packet.get("verdict") == "approved", "Review is not approved")
        findings = packet.get("findings")
        require(isinstance(findings, list), "Review findings missing")
        require(not any(x.get("severity") in {"critical", "high"} and x.get("status") != "resolved" for x in findings),
                "Blocking review finding remains")
    return {"task": task_id, "artifact_gate": "passed", "note": "The orchestrator must verify provenance; a JSON receipt alone cannot prove an actual model identity."}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[4]))
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--structure", action="store_true")
    group.add_argument("--task")
    group.add_argument("--inputs")
    parser.add_argument("--without-native", action="store_true", help="Only for rebuilding the native plan")
    args = parser.parse_args(argv)
    root = Path(args.repo_root).resolve()
    try:
        if args.inputs:
            entries = catalog(root)
            require(args.inputs in entries, "Unknown task")
            result = entries[args.inputs]
        else:
            result = structural(root, not args.without_native) if args.structure else check(root, args.task)
        print(json.dumps(result, indent=2, ensure_ascii=True))
        return 0
    except (GateError, OSError, KeyError, TypeError, ValueError) as exc:
        print(f"DELIVERY REJECTED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
