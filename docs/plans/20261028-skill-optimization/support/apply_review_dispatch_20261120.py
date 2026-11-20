#!/usr/bin/env python3
"""Make every independent review task dispatch its reviewer through review_dispatch.py.

Declarative and idempotent (pattern of apply_review_fixes_20261120.py / apply_task_131_132.py):
every edit states a target state, so a second run writes nothing. Run it only while the plan
runner is stopped (a live runner lease refuses --apply).

Targets: every TASK_INPUTS entry with requires_independent_review=true and a review_of task (65 at
writing time; any later review task such as 132 is picked up on a re-run). Per task:
  manifest.json / PLAN1_SPEC.json  the reviewer-dispatch checkpoint objective becomes the exact
                                   review_dispatch.py procedure (ids, count and status unchanged);
                                   the vague reviewer guidance line becomes the procedure line and
                                   the no-background rule is added.
  TASK_INPUTS.json                 review_dispatch.py is added to inputs/input_contract.
  tasks/<id>-*.md                  re-rendered with planctl_concise (TODO/PLAN/ANALYSIS only if changed).
  REPLAN_TRACE.json                one refinement line; manifest gets one event.
No task id, status, attempt counter, acceptance criterion or acceptance id changes.

Usage:
  python docs/plans/20261028-skill-optimization/support/apply_review_dispatch_20261120.py --check [--repo-root R]
  python docs/plans/20261028-skill-optimization/support/apply_review_dispatch_20261120.py --apply [--repo-root R]
--check exits 0 when nothing would change and 1 when changes are pending.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys
import tempfile
from pathlib import Path

PLAN_ID = "20261028-skill-study-provider-switch"
DOC_REL = "docs/plans/20261028-skill-optimization"
HELPER = f"{DOC_REL}/support/review_dispatch.py"
REVIEW_REF = "docs/research/20261028-skill-optimization/PLAN_ARCHITECTURE_REVIEW_20261120.md"

SUB = ("Run `python {helper} --repo-root . --task {tid}` in the foreground (rerun on exit 75); use only its "
       "DISPATCH line and compact findings.{focus}")
GUIDE_PROC = ("Review only via review_dispatch.py (synchronous; max route; writes dispatch evidence); fix blocking "
              "findings, rerun declared checks, re-dispatch if a reviewed file changed, copy its RECEIPT_REVIEWER "
              "fields into the receipt.")
GUIDE_BG = ("Never launch background or asynchronous agents or processes: this headless session ends when you stop "
            "calling tools, so anything unfinished is lost.")
# Reviewer-dispatch wording this procedure supersedes (guidance lines that only say "use a real reviewer").
VAGUE_GUIDANCE = (
    "Dispatch an actual fresh maximum-qualified reviewer; record its real route and input hashes, then correct and "
    "revalidate every blocking finding.",
    "Use an actual fresh independent maximum-qualified reviewer; never fabricate model execution.",
    "Run actual independent maximum-qualified review and correct all critical/high issues",
    "Require REAL independent fresh max-qualified review of current source hash; do not invent approval.",
    "Dispatch the max reviewer on Codex (Sol 6.2 xhigh), then Claude (Opus 5.5 xhigh); record Codex as skipped for "
    "availability when its credits are exhausted.",
)
DISPATCH_STEP = re.compile(r"\breviewer\b|review evidence|independent (?:model |code |max-qualified |high-capability )?review\b"
                           r"|max-qualified (?:independent )?review\b|genuinely review", re.I)
GENERIC_TITLE = re.compile(r"^Implement change \d+$")
# Reviewer lenses carried by the replaced checkpoint text, kept so the brief still names them.
FOCUS = {
    "100": "semantics, percent math, route/permission guards, negative cases",
    "104": "thresholds, concurrent plans, Windows/Linux/macOS, unsupported hosts",
    "106": "providers, catalog freshness, tier monotonicity, frontier gate, budgets",
    "122": "visual, security/performance and privacy",
    "124": "in-app/lab mode, security, performance, licensing, UX fidelity",
    "126": "visual craft, security, performance, accessibility, privacy",
    "128": "UX/standards consent, source evidence, quality, privacy, token use",
    "130": "P066 and final 129 source/tests/receipt",
}
EVENT_TYPE = "review_dispatch_procedure"
REFINEMENT = ("2026-11-20 review dispatch: every independent review task dispatches its fresh max reviewer only "
              "through support/review_dispatch.py (synchronous, read-only, evidence under implementation/reviews/<id>/) "
              "and never launches background agents; ids, statuses and acceptance unchanged "
              "(apply_review_dispatch_20261120.py).")
SPEC_SUB_KEYS = ("id", "title", "objective")


class Drift(RuntimeError):
    pass


# ---- format-preserving I/O (same rules as apply_task_131_132.py) -----------------------------
def eol_of(raw: bytes) -> str:
    return "\r\n" if b"\r\n" in raw else "\n"


def lf(raw: bytes) -> str:
    return raw.decode("utf-8").replace("\r\n", "\n")


class JsonFile:
    def __init__(self, path: Path):
        raw = path.read_bytes()
        self.path, self.eol = path, eol_of(raw)
        text = lf(raw)
        self.data = json.loads(text)
        for ensure_ascii in (False, True):
            for indent in (2, 1, 4):
                if json.dumps(self.data, indent=indent, ensure_ascii=ensure_ascii) + "\n" == text:
                    self.indent, self.ascii = indent, ensure_ascii
                    return
        raise Drift(f"cannot reproduce the JSON layout of {path.name} byte for byte; refusing to rewrite it")

    def render(self) -> bytes:
        return (json.dumps(self.data, indent=self.indent, ensure_ascii=self.ascii) + "\n").replace("\n", self.eol).encode("utf-8")


def with_eol(text: str, eol: str) -> bytes:
    return text.replace("\r\n", "\n").replace("\n", eol).encode("utf-8")


def atomic_write(path: Path, data: bytes) -> None:
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        for attempt in range(12):
            try:
                os.replace(tmp, path)
                break
            except PermissionError:
                if attempt == 11:
                    raise
                import time
                time.sleep(0.25)
    finally:
        Path(tmp).unlink(missing_ok=True)


# ---- edits -----------------------------------------------------------------------------------
def review_ids(ti: dict) -> list[str]:
    return [e["id"] for e in ti["tasks"] if e.get("requires_independent_review") and e.get("review_of")]


def sub_text(tid: str) -> str:
    focus = f" Focus: {FOCUS[tid]}." if tid in FOCUS else ""
    return SUB.format(helper=HELPER, tid=tid, focus=focus)


def edit_task(t: dict) -> None:
    tid = t["id"]
    target = sub_text(tid)
    step = next((s for s in t["subtasks"] if s["objective"] == target), None)
    if step is None:
        step = next((s for s in t["subtasks"] if DISPATCH_STEP.search(f"{s['title']} {s['objective']}")), None)
    if step is not None:
        step["objective"] = target
        if GENERIC_TITLE.match(step["title"]):
            step["title"] = "Dispatch the independent reviewer"
    guide = [g for g in t["implementation_guidance"] if g != GUIDE_BG]
    if GUIDE_PROC not in guide:
        index = next((i for i, g in enumerate(guide) if g in VAGUE_GUIDANCE), None)
        if index is None:
            guide.append(GUIDE_PROC)
        else:
            guide[index] = GUIDE_PROC
    guide = [g for g in guide if g not in VAGUE_GUIDANCE]
    guide.append(GUIDE_BG)
    t["implementation_guidance"] = guide


def edit_manifest(m: dict, ids: list[str]) -> None:
    by_id = {t["id"]: t for t in m["tasks"]}
    for tid in ids:
        if tid in by_id:
            edit_task(by_id[tid])


def add_event(m: dict, ids: list[str], now: str) -> None:
    if not any(ev.get("type") == EVENT_TYPE and ev.get("task_ids") == ids for ev in m.get("events", [])):
        m.setdefault("events", []).append({"at": now, "type": EVENT_TYPE, "reference": REVIEW_REF, "helper": HELPER,
                                           "task_ids": ids, "implementation_complete": False})


def edit_spec(spec: dict, m: dict, ids: list[str]) -> None:
    by_id = {t["id"]: t for t in m["tasks"]}
    for st in spec["tasks"]:
        tid = f"{int(st['id']):03}"
        if tid not in ids or tid not in by_id:
            continue
        t = by_id[tid]
        st["implementation_guidance"] = copy.deepcopy(t["implementation_guidance"])
        st["subtasks"] = [{k: s[k] for k in SPEC_SUB_KEYS} for s in t["subtasks"]]


def edit_task_inputs(ti: dict, ids: list[str]) -> None:
    for e in ti["tasks"]:
        if e["id"] not in ids:
            continue
        if HELPER not in e["inputs"]:
            e["inputs"].append(HELPER)
        if "input_contract" in e and not any(x["path"] == HELPER for x in e["input_contract"]):
            e["input_contract"].append({"path": HELPER, "availability": "existing_baseline_or_current_file"})


# ---- checks ----------------------------------------------------------------------------------
RUNTIME_SUB_KEYS = ("id", "required", "status", "started_at", "completed_at", "history")


def self_checks(old_m: dict, m: dict, spec: dict, ti: dict, ids: list[str], pc, artifact_contract) -> list[str]:
    problems = []
    old_by_id = {t["id"]: t for t in old_m["tasks"]}
    if [t["id"] for t in m["tasks"]] != [t["id"] for t in old_m["tasks"]]:
        problems.append("task order or id set changed")
    for t in m["tasks"]:
        before = old_by_id[t["id"]]
        changed = {k for k in set(t) | set(before) if t.get(k) != before.get(k)}
        allowed = {"subtasks", "implementation_guidance"} if t["id"] in ids else set()
        if changed - allowed:
            problems.append(f"{t['id']}: unexpected fields changed {sorted(changed - allowed)}")
        if len(t["subtasks"]) != len(before["subtasks"]):
            problems.append(f"{t['id']}: checkpoint count changed")
        for a, b in zip(t["subtasks"], before["subtasks"]):
            if any(a.get(k) != b.get(k) for k in RUNTIME_SUB_KEYS):
                problems.append(f"{t['id']}/{a['id']}: checkpoint id or runtime state changed")
        if t["id"] in ids:
            if t["implementation_guidance"].count(GUIDE_PROC) != 1 or t["implementation_guidance"][-1] != GUIDE_BG:
                problems.append(f"{t['id']}: procedure/no-background guidance missing")
            if any(g in VAGUE_GUIDANCE for g in t["implementation_guidance"]):
                problems.append(f"{t['id']}: vague reviewer guidance remains")
    spec_by_id = {f"{int(t['id']):03}": t for t in spec["tasks"]}
    for t in m["tasks"]:
        st = spec_by_id.get(t["id"])
        if st is None:
            problems.append(f"{t['id']}: missing from spec")
            continue
        for field in ("title", "objective", "dependencies", "implementation_guidance", "acceptance_criteria"):
            if st[field] != t[field]:
                problems.append(f"{t['id']}: spec/manifest {field} mismatch")
        if [(s["id"], s["title"], s["objective"]) for s in st["subtasks"]] != [
                (s["id"], s["title"], s["objective"]) for s in t["subtasks"]]:
            problems.append(f"{t['id']}: spec/manifest subtask mismatch")
    entries = {e["id"]: e for e in ti["tasks"]}
    for tid in ids:
        if HELPER not in entries[tid]["inputs"]:
            problems.append(f"{tid}: TASK_INPUTS lacks the helper input")
        t = next(x for x in m["tasks"] if x["id"] == tid)
        if len(entries[tid]["acceptance_ids"]) > len(t["acceptance_criteria"]):
            problems.append(f"{tid}: acceptance_ids exceed criteria")

    def text_errors(manifest: dict) -> set[str]:
        try:
            return set(artifact_contract._validate_plan_text(pc, manifest))
        except Exception as exc:  # noqa: BLE001
            return {f"validator error: {exc}"}
    problems += sorted(text_errors(m) - text_errors(old_m))
    return problems


def runner_is_live(plan_dir: Path) -> bool:
    try:
        import lifecyclectl
        return bool(lifecyclectl.lease_is_live(lifecyclectl.read_lease(plan_dir)))
    except Exception:  # noqa: BLE001  (unreadable lease: be conservative)
        return (plan_dir / ".runner-lease.json").exists()


# ---- main ------------------------------------------------------------------------------------
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[4]))
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="report what would change; write nothing")
    mode.add_argument("--apply", action="store_true", help="write the changes (runner must be stopped)")
    args = ap.parse_args(argv)

    root = Path(args.repo_root).resolve()
    doc, plan_dir = root / DOC_REL, root / ".ai-work" / PLAN_ID
    sys.path.insert(0, str(root / "skill/plan-and-execute/scripts"))
    import artifact_contract
    import planctl_concise
    pc = planctl_concise.planctl

    if not (root / HELPER).is_file():
        print(f"PROBLEM: missing helper {HELPER}", file=sys.stderr)
        return 2
    try:
        mf = JsonFile(plan_dir / "manifest.json")
        sf, tf, rt = JsonFile(doc / "PLAN1_SPEC.json"), JsonFile(doc / "TASK_INPUTS.json"), JsonFile(doc / "REPLAN_TRACE.json")
        old_m = copy.deepcopy(mf.data)
        ids = review_ids(tf.data)
        edit_manifest(mf.data, ids)
        edit_spec(sf.data, mf.data, ids)
        edit_task_inputs(tf.data, ids)
        if REFINEMENT not in rt.data["post_conversion_refinements"]:
            rt.data["post_conversion_refinements"].append(REFINEMENT)
        problems = self_checks(old_m, mf.data, sf.data, tf.data, ids, pc, artifact_contract)
        if problems:
            for p in problems:
                print("PROBLEM:", p, file=sys.stderr)
            return 2
        m = mf.data
        definition_changed = m != old_m
        if definition_changed:
            add_event(m, ids, pc.now_utc())
        outputs: dict[Path, bytes] = {sf.path: sf.render(), tf.path: tf.render(), rt.path: rt.render()}
        plan_id, work_root = m["plan_id"], m.get("work_root")
        old_by_id = {t["id"]: t for t in old_m["tasks"]}
        for t in m["tasks"]:
            if t["id"] not in ids:
                continue
            path = plan_dir / t["file"]
            raw = path.read_bytes()
            if lf(raw) != pc.render_task(old_by_id[t["id"]], plan_id, work_root):
                raise Drift(f"{path.name} differs from its manifest projection; refusing to re-render it")
            outputs[path] = with_eol(pc.render_task(t, plan_id, work_root), eol_of(raw))
        for name, render in (("TODO.md", pc.render_todo), ("PLAN.md", pc.render_plan), ("ANALYSIS.md", pc.render_analysis)):
            path = plan_dir / name
            raw = path.read_bytes()
            if render(m) != render(old_m):
                if lf(raw) != render(old_m):
                    raise Drift(f"{name} differs from its manifest projection; refusing to re-render it")
                outputs[path] = with_eol(render(m), eol_of(raw))
    except (Drift, KeyError, StopIteration, ValueError) as exc:
        print(f"PROBLEM: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2

    changed = [p for p, data in outputs.items() if not p.is_file() or p.read_bytes() != data]
    if definition_changed:
        changed.append(mf.path)
    if not changed:
        print(f"0 file(s) would change; review dispatch procedure already applied to {len(ids)} review task(s)")
        return 0
    if args.check:
        for p in changed:
            print("would change:", p.relative_to(root).as_posix())
        print(f"{len(changed)} file(s) would change; {len(ids)} review task(s)")
        return 1
    if runner_is_live(plan_dir):
        print("REFUSED: the plan runner lease is live; stop the runner first", file=sys.stderr)
        return 3
    for p in changed:
        if p == mf.path:
            continue
        atomic_write(p, outputs[p])
        print("wrote:", p.relative_to(root).as_posix())
    if definition_changed:  # last, so an interrupted run never leaves definitions ahead of task files
        m["updated_at"] = pc.now_utc()
        atomic_write(mf.path, mf.render())
        print("wrote:", mf.path.relative_to(root).as_posix())
    print(f"{len(changed)} file(s) changed; {len(ids)} review task(s): {','.join(ids)}")

    errors = pc.validate_plan(plan_dir, json.loads(mf.path.read_text(encoding="utf-8")))
    for e in errors:
        print("VALIDATE:", e, file=sys.stderr)
    sys.path.insert(0, str(doc / "support"))
    import check_delivery
    try:
        check_delivery.structural(root)
        print("check_delivery --structure: passed")
    except (check_delivery.GateError, OSError, KeyError, TypeError, ValueError) as exc:
        errors.append(str(exc))
        print("STRUCTURE:", exc, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
