#!/usr/bin/env python3
"""Deterministic documentation inventory and coverage checker.

inventory: scan the documentation scope and write path/sha256/status entries.
           Unchanged hashes keep their review status; new or changed files
           become `pending` until reviewed.
review:    set status/reason for paths at their current hash.
check:     verify schema and coverage. Changed, new and removed paths are
           listed for re-review but do not fail the check.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SCHEMA_VERSION = 1
ALGORITHM = "sha256-lf-normalized-text"
STATUSES = ("reviewed", "not_applicable")
PENDING = "pending"
MAX_REASON = 200
MAX_SUMMARY = 400
DEFAULT_BASELINE = "docs/research/ROUTING_DOC_BASELINE.json"
REQUEST = "docs/requests/portable-model-routing-dynamic-provider-catalog.md"
SCOPE = [
    "*.md",
    "docs/**/*.md",
    "skill/*/SKILL.md",
    "skill/*/references/**",
    "skill/*/assets/**/*.md",
    "skill/*/assets/**/*.json",
    "skill/*/agents/**",
]
EXCLUDE = [
    "docs/requests/**",
    "docs/research/ROUTING_DOC_BASELINE.*",
    "**/__pycache__/**",
    "**/node_modules/**",
]
AFFECT_RE = re.compile(r"^(R\d{3}|FR-\d{3}|NFR-\d{3}|TODO-\d{3}|T\d{3})$")
FINDING_KINDS = ("stale", "conflict", "gap", "constraint")
DIFF_CHANGES = ("add", "change", "confirm")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")


def repo_root_default() -> Path:
    return Path(__file__).resolve().parents[1]


def to_regex(pattern: str) -> re.Pattern[str]:
    out, i = "", 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out += "(?:.*/)?"
            i += 3
        elif pattern.startswith("**", i):
            out += ".*"
            i += 2
        elif pattern[i] == "*":
            out += "[^/]*"
            i += 1
        elif pattern[i] == "?":
            out += "[^/]"
            i += 1
        else:
            out += re.escape(pattern[i])
            i += 1
    return re.compile("^" + out + "$")


SCOPE_RE = [to_regex(p) for p in SCOPE]
EXCLUDE_RE = [to_regex(p) for p in EXCLUDE]


def in_scope(rel: str) -> bool:
    if any(r.match(rel) for r in EXCLUDE_RE):
        return False
    return any(r.match(rel) for r in SCOPE_RE)


def file_hash(path: Path) -> str:
    data = path.read_bytes()
    if b"\0" not in data:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def scan(root: Path) -> dict[str, str]:
    found: dict[str, str] = {}
    for top in sorted(p for p in root.iterdir() if p.name not in {".git", ".ai-work", "node_modules"}):
        candidates = [top] if top.is_file() else sorted(top.rglob("*"))
        for path in candidates:
            if not path.is_file() or path.is_symlink():
                continue
            rel = path.relative_to(root).as_posix()
            if in_scope(rel):
                found[rel] = file_hash(path)
    return dict(sorted(found.items()))


def resolve(root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, doc: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def cmd_inventory(args: argparse.Namespace) -> int:
    root = Path(args.repo_root).resolve()
    baseline_path = resolve(root, args.baseline)
    doc = load(baseline_path) if baseline_path.exists() else {}
    previous = {e["path"]: e for e in doc.get("entries", []) if isinstance(e, dict) and "path" in e}
    entries = []
    for rel, digest in scan(root).items():
        old = previous.get(rel)
        if old and old.get("sha256") == digest and old.get("status") in STATUSES:
            entries.append({"path": rel, "sha256": digest, "status": old["status"], "reason": old.get("reason", "")})
        else:
            entries.append({"path": rel, "sha256": digest, "status": PENDING, "reason": ""})
    request = resolve(root, REQUEST)
    doc.update(
        {
            "schema_version": SCHEMA_VERSION,
            "algorithm": ALGORITHM,
            "scope": SCOPE,
            "exclude": EXCLUDE,
            "request": {"path": REQUEST, "sha256": file_hash(request) if request.exists() else None},
            "entries": entries,
        }
    )
    doc.setdefault("findings", [])
    doc.setdefault("requirement_diff", [])
    write(baseline_path, doc)
    pending = sum(1 for e in entries if e["status"] == PENDING)
    print(f"inventory: {len(entries)} paths, {pending} pending review -> {args.baseline}")
    return 0


def cmd_review(args: argparse.Namespace) -> int:
    root = Path(args.repo_root).resolve()
    baseline_path = resolve(root, args.baseline)
    doc = load(baseline_path)
    if args.status not in STATUSES:
        print(f"review: status must be one of {STATUSES}", file=sys.stderr)
        return 2
    if not args.reason.strip() or len(args.reason) > MAX_REASON:
        print(f"review: reason must be 1..{MAX_REASON} chars", file=sys.stderr)
        return 2
    entries = {e["path"]: e for e in doc["entries"]}
    for rel in args.paths:
        rel = rel.replace("\\", "/")
        if rel not in entries:
            print(f"review: {rel} not inventoried; run inventory first", file=sys.stderr)
            return 2
        target = resolve(root, rel)
        entries[rel].update({"sha256": file_hash(target), "status": args.status, "reason": args.reason})
    write(baseline_path, doc)
    print(f"review: {len(args.paths)} path(s) marked {args.status}")
    return 0


def validate_schema(doc: dict, root: Path) -> list[str]:
    errors: list[str] = []
    if doc.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if doc.get("algorithm") != ALGORITHM:
        errors.append(f"algorithm must be {ALGORITHM}")
    entries = doc.get("entries")
    if not isinstance(entries, list) or not entries:
        errors.append("entries must be a non-empty list")
        entries = []
    seen: set[str] = set()
    for i, entry in enumerate(entries):
        where = f"entries[{i}]"
        if not isinstance(entry, dict):
            errors.append(f"{where} must be an object")
            continue
        path = entry.get("path")
        if not isinstance(path, str) or not path:
            errors.append(f"{where}.path missing")
            continue
        where = f"entry {path}"
        if path in seen:
            errors.append(f"{where} duplicated")
        seen.add(path)
        if not isinstance(entry.get("sha256"), str) or not SHA_RE.match(entry["sha256"]):
            errors.append(f"{where}: sha256 must be 64 lowercase hex chars")
        status = entry.get("status")
        if status not in STATUSES:
            errors.append(f"{where}: status {status!r} is not reviewed|not_applicable")
        reason = entry.get("reason")
        if not isinstance(reason, str) or not reason.strip() or len(reason) > MAX_REASON:
            errors.append(f"{where}: reason must be 1..{MAX_REASON} chars")
    for i, finding in enumerate(doc.get("findings", [])):
        where = f"findings[{i}]"
        if not isinstance(finding, dict):
            errors.append(f"{where} must be an object")
            continue
        for key in ("id", "path", "section", "summary"):
            if not isinstance(finding.get(key), str) or not finding[key].strip():
                errors.append(f"{where}.{key} missing")
        if isinstance(finding.get("summary"), str) and len(finding["summary"]) > MAX_SUMMARY:
            errors.append(f"{where}.summary exceeds {MAX_SUMMARY} chars")
        if finding.get("kind") not in FINDING_KINDS:
            errors.append(f"{where}.kind must be one of {FINDING_KINDS}")
        path = finding.get("path")
        if isinstance(path, str) and path not in seen and path != REQUEST:
            errors.append(f"{where}.path {path} is not an inventoried path")
        affects = finding.get("affects")
        if not isinstance(affects, list) or not affects or not all(isinstance(a, str) and AFFECT_RE.match(a) for a in affects):
            errors.append(f"{where}.affects must list R-/FR-/NFR-/TODO- ids")
    for i, item in enumerate(doc.get("requirement_diff", [])):
        where = f"requirement_diff[{i}]"
        if not isinstance(item, dict):
            errors.append(f"{where} must be an object")
            continue
        for key in ("id", "ref", "summary"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                errors.append(f"{where}.{key} missing")
        if item.get("change") not in DIFF_CHANGES:
            errors.append(f"{where}.change must be one of {DIFF_CHANGES}")
        if isinstance(item.get("summary"), str) and len(item["summary"]) > MAX_SUMMARY:
            errors.append(f"{where}.summary exceeds {MAX_SUMMARY} chars")
        known = {f.get("id") for f in doc.get("findings", []) if isinstance(f, dict)}
        refs = item.get("findings")
        if not isinstance(refs, list) or not refs or not set(refs) <= known:
            errors.append(f"{where}.findings must list existing finding ids")
        ref = item.get("ref", "")
        ref_path = ref.split("#", 1)[0] if isinstance(ref, str) else ""
        if ref_path and ref_path not in seen and ref_path != REQUEST:
            errors.append(f"{where}.ref path {ref_path} is not inventoried or the request")
    return errors


def cmd_check(args: argparse.Namespace) -> int:
    root = Path(args.repo_root).resolve()
    baseline_path = resolve(root, args.baseline)
    if not baseline_path.exists():
        print(f"doc_baseline check FAILED: {args.baseline} not found; run inventory", file=sys.stderr)
        return 1
    try:
        doc = load(baseline_path)
    except (OSError, ValueError) as exc:
        print(f"doc_baseline check FAILED: unreadable baseline: {exc}", file=sys.stderr)
        return 1
    errors = validate_schema(doc, root)
    if errors:
        print("doc_baseline check FAILED (coverage/schema):", file=sys.stderr)
        for error in errors[:50]:
            print(f"  - {error}", file=sys.stderr)
        return 1
    current = scan(root)
    recorded = {e["path"]: e["sha256"] for e in doc["entries"]}
    changed = sorted(p for p in recorded if p in current and current[p] != recorded[p])
    new = sorted(p for p in current if p not in recorded)
    removed = sorted(p for p in recorded if p not in current)
    request = resolve(root, REQUEST)
    request_hash = doc.get("request", {}).get("sha256")
    request_changed = request.exists() and request_hash and file_hash(request) != request_hash
    unchanged = len(recorded) - len(changed) - len(removed)
    result = {"unchanged": unchanged, "changed": changed, "new": new, "removed": removed, "request_changed": bool(request_changed)}
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"doc_baseline check OK: {unchanged} unchanged, {len(changed)} changed, {len(new)} new, {len(removed)} removed")
        for label, paths in (("changed", changed), ("new", new), ("removed", removed)):
            for path in paths:
                print(f"  re-review ({label}): {path}")
        if request_changed:
            print(f"  re-review (request changed): {REQUEST}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    for name, func in (("inventory", cmd_inventory), ("review", cmd_review), ("check", cmd_check)):
        p = sub.add_parser(name)
        p.add_argument("--repo-root", default=str(repo_root_default()))
        p.add_argument("--baseline", default=DEFAULT_BASELINE)
        p.set_defaults(func=func)
        if name == "review":
            p.add_argument("--status", required=True)
            p.add_argument("--reason", required=True)
            p.add_argument("paths", nargs="+")
        if name == "check":
            p.add_argument("--json", action="store_true")
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
