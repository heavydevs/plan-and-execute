#!/usr/bin/env python3
"""Add P067 manager-tier delegation (implementation 131, independent review 132) to the plan.

Declarative and idempotent: every edit states a target state, so a second run writes nothing.
Run it only while the plan runner is stopped (a live runner lease refuses --apply).

What it changes, consistently (see PLAN_ARCHITECTURE_REVIEW_20261120.md, "Decisions made while
preparing 131/132"):
  .ai-work/<plan>/manifest.json          P067, R073, tasks 131/132 before 082, 082/086 deltas, event
  .ai-work/<plan>/tasks/{131,132,082,086}-*.md, TODO.md, PLAN.md, ANALYSIS.md  (planctl_concise renderers)
  docs/plans/.../PLAN1_SPEC.json         same projection (P067, R073, 131/132 before 82, 082/086)
  docs/plans/.../TASK_INPUTS.json        entries 131/132; 082 inputs/checks
  docs/plans/.../REPLAN_TRACE.json, IMPLEMENTATION_CHECKLIST.md, IMPLEMENTATION_INTEGRATION.md
  docs/plans/.../REQUEST_EXTENSION_20261120_MANAGER_DELEGATION.md  (new)
  docs/plans/.../support/check_delivery.py           082 gate tuple += 132
  docs/plans/.../support/delivery_gate_self_test.py  missing-132-gate case
  .ai-work/SERVICE_MAP.md                P1_TESTS_131/P1_131/P1_TESTS_132/P1_132
Every existing task keeps its id, status and runtime state; only 082/086 definition fields change.
Each file keeps its own JSON format and line endings. The research note
docs/research/20261028-skill-optimization/prepared-research/131-manager-tier-delegation.md must exist.

Usage:
  python docs/plans/20261028-skill-optimization/support/apply_task_131_132.py --check [--repo-root R]
  python docs/plans/20261028-skill-optimization/support/apply_task_131_132.py --apply [--repo-root R]
--check exits 0 when nothing would change (already applied) and 1 when changes are pending.
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
PREP_REL = "docs/research/20261028-skill-optimization/prepared-research"
IMPL_REL = "docs/research/20261028-skill-optimization/implementation"
NOTE = f"{PREP_REL}/131-manager-tier-delegation.md"
REFRESH = "docs/research/MODEL_REFRESH_20261120.md"
SK = "skill/plan-and-execute/scripts/"
REF = "skill/plan-and-execute/references/"
NEW_TEST = "test/optimization/manager_delegation_self_test.py"

META_LINES = {
    "The prepared report is input evidence, not proof that this implementation or its independent review has passed.",
    "Prepared research is not proof of implementation or independent-review completion.",
}
FRONTIER_REVIEW = ("A frontier (Fable 5.2 / Astra 6.2) reviewer is accepted only with recorded repeated "
                   "max-review failure; a reused review session or dispatch is rejected.")

# ---- request part / requirement -------------------------------------------------------------
P067 = {"id": "P067", "text": (
    "When the plan manager (root) is a smaller model, hard mid-run decisions (blocked task, plan or gate defect, "
    "replan, review conflict, manifest mutation) go to a fresh qualified read-only worker; frontier only by "
    "existing rules; availability faults never escalate.")}
R073 = {"id": "R073", "text": (
    "Supervisory decisions use a configurable routing_policy.manager_tier and one deterministic routingctl entry "
    "point; diagnoses are read-only, deduplicated per blocker fingerprint and budgeted, and never switch the root "
    "model, auto-edit the manifest or escalate availability faults."),
    "source": "user", "priority": "must", "request_part_ids": ["P067"]}
SUMMARY_OLD, SUMMARY_NEW = "087-130 (P052-P066)", "087-132 (P052-P067)"

# ---- shared task fields ---------------------------------------------------------------------
WRITE_SCOPE = [SK + "routingctl.py", SK + "routing_config.py", SK + "watchdogctl.py", SK + "run_isolated.py",
               SK + "keepalivectl.py", SK + "routing_telemetry.py", REF + "DELEGATION.md", REF + "WATCHDOG.md",
               REF + "MODEL_ROUTING.md", REF + "ROUTING_CONFIG.md", NEW_TEST]
CHECKS = [["python", NEW_TEST]] + [["python", SK + name] for name in (
    "routing_self_test.py", "delegation_self_test.py", "frontier_self_test.py", "routing_config_self_test.py",
    "watchdogctl_self_test.py", "keepalivectl_self_test.py", "telemetry_self_test.py", "availability_self_test.py",
    "progress_runner_self_test.py", "self_test.py")] + [["node", "tools/validate-skill.js"]]
# Accepted earlier writers of the shared files (review A8) plus the functional prerequisites:
# 088 delegation gate, 092 lease-safe graph mutation, 100 stall diagnosis, 106 frontier level;
# latest writers 104 WATCHDOG.md, 108 DELEGATION/MODEL_ROUTING.md, 116 keepalivectl.py,
# 120 routingctl.py, 130 run_isolated.py (057 watchdogctl.py and 081 routing_telemetry.py are transitive).
DEPS_131 = ["088", "092", "100", "104", "106", "108", "116", "120", "130"]
SEPARATE = ["Other task files, complete repo scans, historic chat and unrelated sources."]
SCOPE_OUT = ["No root model switch, automatic manifest edit or resolution, automatic frontier dispatch, second "
             "router or watchdog, or live model call in tests."]
READ_NOTE = f"Only read {NOTE} for this task; it fixes the event table, schemas and negative cases."


def validations(tid: str) -> list[str]:
    return [f"python {SK}resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_{tid}",
            f"python {SK}resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_{tid}"]


def receipts(tid: str) -> list[str]:
    return [f"{IMPL_REL}/{tid}-receipt.json", f"{IMPL_REL}/{tid}-outcome.md"]


TASK_131 = {
    "id": "131", "slug": "manager-tier-delegation",
    "title": "Implement manager-tier delegation for plan supervision decisions",
    "objective": ("When the plan manager is below the floor of a supervisory decision (blocked task, plan/gate defect, "
                  "replan, review conflict, manifest mutation), route it to a fresh qualified read-only worker without "
                  "switching the root model or auto-editing the manifest."),
    "requirement_ids": ["R073"], "complexity": "high",
    "atomicity_rationale": ("One supervisory-decision contract (config, decision gate, block record, surfacing, accounting) "
                            "verified by one self-test; splitting it would duplicate the event-to-floor table."),
    "context_boundary": {
        "shared_context": ["Assigned P067 research note, accepted 088/092/100/106 receipts and the affected routing, "
                           "runner and watchdog sources only."],
        "why_one_todo": ("Manager tier, supervisory decision gate, block record and diagnostic accounting share one "
                         "event-to-floor contract verified by one self-test."),
        "separate_from": SEPARATE},
    "scope": {"in": ["Manager-tier config, routingctl supervise decision, diagnosis-request record, watchdog/keepalive "
                     "surfacing and diagnostic accounting"],
              "out": SCOPE_OUT, "expected_files": WRITE_SCOPE + receipts("131")},
    "dependencies": DEPS_131,
    "implementation_guidance": [
        READ_NOTE,
        ("Build on routingctl delegate_decision, select_route, frontier_policy, the availability classes and "
         "check_worker_result; add no second router, selector, watchdog or availability classifier."),
        ("Diagnosis chain Codex > Claude (Sol 6.2 / Opus 5.5); implementation repair Antigravity > Codex > Claude only "
         "through task 091; unavailable providers are skipped without lowering the floor."),
        ("Touch run_isolated.py only to write the diagnosis-request record on the blocked path and keepalivectl.py only "
         "to surface it; neither dispatches, edits the manifest or resolves a blocker."),
        ("Run after the accepted writers of the shared files (088, 092, 100, 104, 106, 108, 116, 120, 130); rebase on "
         "their versions and run every self-test that imports a changed module."),
        ("Use only task 131 inputs, checks and write scope in TASK_INPUTS.json; record actual receipts/outcomes and "
         "leave the task pending until verified."),
    ],
    "acceptance_criteria": [
        ("Sonnet 5.5 manager (standard) with a semantic blocked_task: supervise returns delegate to a read-only Opus 5.5 "
         "/ Sol 6.2 analyst at strong/high with a failure-capsule brief and no root model switch."),
        ("A Haiku 5.5 manager (economy) delegates every event above its tier; a manager at or above the event floor "
         "gets keep_root."),
        ("With Codex credits exhausted the diagnosis chain skips Codex as availability and routes to Claude Opus 5.5; no "
         "escalation or capability failure is recorded."),
        ("Quota, credits, auth, environment, budget, timeout and unknown-cause blocks return report_only: no "
         "diagnosis-request record, no diagnostic dispatch and no escalation."),
        ("A repeated blocker fingerprint gives one record and one diagnosis, later calls return duplicate, and the "
         "per-task and per-plan diagnosis budget is bounded."),
        ("Frontier (Fable 5.2 / Astra 6.2) is chosen for diagnosis only for extreme_architecture_review or after "
         "min_top_failures functional max/xhigh failures, and is never auto-dispatched."),
        ("Runner, watchdog and keepalive never edit the manifest, resolve a blocker or dispatch a worker; resolution "
         "goes through task 091's lease-safe graph mutation."),
        ("Diagnoses dispatch only through the adapter-pinned read-only argv; a provider without a proven read-only "
         "mode is skipped with a reason, although implementers run full-access."),
        ("routing_policy.manager_tier accepts auto|economy|standard|advanced|strong|max (auto = standard), survives "
         "the catalog refresh, and the effective tier is recorded in decision, record and telemetry."),
        ("Each diagnosis is accounted as kind diagnostic in routing_telemetry rollups and charged against the "
         "delegation token budget."),
        ("A plan without routing_policy.manager_tier keeps runner, watchdog and keepalive output and exit codes "
         "byte-identical to the legacy behavior."),
        (f"{NEW_TEST} covers these cases offline with no model call, network access or user-global configuration "
         "write."),
        "The prepared report is input evidence, not proof that this implementation or its independent review has passed.",
    ],
    "validation_commands": validations("131"),
    "provider": "auto", "model_tier": "strong", "reasoning_effort": "high",
    "subtasks": [
        ("S001", "Read P067 research and accepted evidence",
         f"Read {NOTE} and accepted 088/092/100/106 receipts; inspect only routingctl delegate, the run_isolated "
         "blocked path, watchdogctl and keepalivectl."),
        ("S002", "Add the configurable manager tier",
         "Add routing_policy.manager_tier (auto|economy|standard|advanced|strong|max; auto = standard), validated in "
         "routing_config.py, kept by the catalog refresh, recorded in decisions and telemetry; never switch the root model."),
        ("S003", "Implement the supervisory decision entry point",
         "Add routingctl.py supervise on top of delegate_decision mapping the seven events to leaf signals and floors; "
         "return decision, phase provider chain, minimal read-only brief and the compact result schema."),
        ("S004", "Write and surface diagnosis-request records",
         "On a functional block write results/<task>-diagnosis-request.json once per blocker fingerprint; "
         "watchdogctl/keepalivectl surface it as diagnosis_requested and never dispatch, edit the manifest or resolve."),
        ("S005", "Keep availability and frontier out of diagnosis",
         "Quota, credits, auth, environment, budget, timeout and unknown blocks write no record and spend nothing; "
         "frontier only by the two owner rules, never auto-dispatched; Codex credit exhaustion skips to Claude."),
        ("S006", "Enforce read-only dispatch and diagnostic accounting",
         "Dispatch diagnoses only through the adapter-pinned read-only argv (skip providers without one) and account "
         "them as kind diagnostic in routing_telemetry rollups and delegation budgets."),
        ("S007", "Test, document and record evidence",
         f"Write {NEW_TEST} with the nine P067 cases, update DELEGATION/WATCHDOG/MODEL_ROUTING/ROUTING_CONFIG.md, run "
         "the declared checks and record the 131 receipt and outcome."),
    ],
}

TASK_132 = {
    "id": "132", "slug": "review-manager-tier-delegation",
    "title": "Independently review manager-tier delegation for plan supervision",
    "objective": ("Independently review and correct manager-tier supervisory delegation: event floors, read-only "
                  "boundary, availability exclusion, dedup budget, frontier rules and legacy compatibility on the final "
                  "131 hashes."),
    "requirement_ids": ["R073"], "complexity": "high",
    "atomicity_rationale": "One independent final-hash correction gate for the 131 supervisory-decision contract.",
    "context_boundary": {
        "shared_context": ["Assigned P067 research note, final 131 code, tests and receipts only."],
        "why_one_todo": ("One reviewer context holds the final 131 decision gate, block record and tests needed to judge "
                         "and correct them together."),
        "separate_from": SEPARATE},
    "scope": {"in": ["Independently review manager-tier delegation, read-only diagnosis, availability exclusion and "
                     "legacy compatibility"],
              "out": SCOPE_OUT, "expected_files": WRITE_SCOPE + receipts("132")},
    "dependencies": ["131"],
    "implementation_guidance": [
        READ_NOTE,
        "Require REAL independent fresh max-qualified review of current source hash; do not invent approval.",
        ("Review order Codex > Claude (Sol 6.2 xhigh, then Opus 5.5 xhigh); Codex credit exhaustion is availability "
         "and skips to Claude without escalation."),
        ("Use only task 132 inputs, checks and write scope in TASK_INPUTS.json; record actual receipts/outcomes and "
         "leave the task pending until verified."),
    ],
    "acceptance_criteria": [
        "A real fresh max-qualified reviewer approves the final 131 source/test/receipt hashes with dispatch provenance.",
        ("The S003 probes pass: root model switch, availability as capability, duplicate fingerprints, budget "
         "exhaustion, frontier without repeated failure, write-capable diagnosis argv, auto manifest edits, legacy plans."),
        "High/critical findings are fixed and re-reviewed on the final hashes.",
        FRONTIER_REVIEW,
        "Every acceptance criterion of task 131 has actual test evidence on the final reviewed hashes.",
    ],
    "validation_commands": validations("132"),
    "provider": "auto", "model_tier": "max", "reasoning_effort": "xhigh",
    "subtasks": [
        ("S001", "Read final 131 evidence",
         "Read P067 research and only the actual final 131 code, tests and receipts; review their SHA hashes."),
        ("S002", "Dispatch a fresh max-qualified review",
         "Run a genuine separate fresh maximum-qualified reviewer (Codex Sol 6.2 xhigh, then Claude Opus 5.5 xhigh) for "
         "routing correctness, read-only safety, cost and legacy compatibility."),
        ("S003", "Run adversarial supervision probes",
         "Probe root model switch, availability as capability, duplicate fingerprints, budget exhaustion, frontier "
         "without repeated failure, write-capable diagnosis argv, auto manifest edits and legacy plans."),
        ("S004", "Fix blockers and record the review",
         "Fix or reopen 131 for blocking defects, rerun focused tests; record the genuine reviewer route, source hashes "
         "and decisions."),
    ],
}
NEW_TASKS = [TASK_131, TASK_132]
NEW_IDS = [t["id"] for t in NEW_TASKS]

# ---- 082 / 086 deltas -----------------------------------------------------------------------
G082 = [("Integrate P054 timer cleanup and P055 L6 model routing after genuine independent reviews 104/106.",
         "Integrate P054 timer cleanup, P055 L6 model routing and P067 manager-tier delegation after genuine "
         "independent reviews 104/106/132.")]
A082 = [("New reviewed 103/104 twenty-minute timer and 105/106 sixth frontier-tier work have actual acceptance evidence.",
         "New reviewed 103/104 twenty-minute timer, 105/106 sixth frontier-tier and 131/132 manager-tier delegation work "
         "have actual acceptance evidence."),
        ("tools/run-repo-checks.js runs every test/optimization/*_self_test.py from tasks 068-130, and "
         "integration_082_self_test.py proves it.",
         "tools/run-repo-checks.js runs every test/optimization/*_self_test.py from tasks 068-132, and "
         "integration_082_self_test.py proves it.")]
TI082_INPUTS = [(NOTE, {"availability": "existing_baseline_or_current_file"}),
                (f"{IMPL_REL}/132-receipt.json", {"availability": "prerequisite_output", "producer_task": "132"})]
TI082_CHECK = ["python", NEW_TEST]

EVENT = {"type": "plan_tasks_added", "reference": NOTE, "task_ids": NEW_IDS, "request_part_ids": ["P067"],
         "requirement_ids": ["R073"], "implementation_complete": False}
REFINEMENT = ("2026-11-20 P067 manager-tier delegation added as implementation/review pair 131/132 (R073) before 082; "
              "082 gains the 131/132 dependencies and the 132 structural gate, 082/086 gain R073; no other task, id or "
              "status changed (apply_task_131_132.py).")
REQUEST_EXTENSION = "REQUEST_EXTENSION_20261120_MANAGER_DELEGATION.md"
REQUEST_EXTENSION_TEXT = f"""# P067 — Manager-tier delegation for plan supervision (2026-11-20)

Owner request, recorded by the plan supervisor: when the plan manager (root) is a small model such as Sonnet 5.5 or Haiku 5.5, its hard mid-run decisions (a blocked task at runner exit 4, a gate or plan defect, a replan, two conflicting reviews, a high-impact manifest mutation) must be delegated to a fresh qualified worker (Opus 5.5 / Sol 6.2; read-only for diagnosis). The frontier level (Fable 5.2 / Astra 6.2) is used only under the existing frontier rules: extreme architecture or code review, or after Opus/Sol failed repeatedly, and never for quota, auth or environment faults. Availability faults (quota, credits, auth, environment, timeout) never trigger escalation or diagnosis spend; Codex credit exhaustion is availability. The root session's model is never switched. The runner and watchdog never auto-edit the manifest, auto-resolve or auto-dispatch a frontier route; resolution goes through task 091's lease-safe graph mutation.

Pre-decided architecture, event table, schemas and negative cases: {NOTE}. New R073. New implementation/review pair 131/132, added pending. 131 depends on {', '.join(DEPS_131)} (accepted earlier writers of the shared files); 132 depends on 131; 082 depends on 131/132. 086 remains final. Applied by {DOC_REL}/support/apply_task_131_132.py.
"""
INTEGRATION_MARKER = "## 2026-11-20 P067 extension"
INTEGRATION_TEXT = (f"{INTEGRATION_MARKER}\n\nThe single active plan now contains 132 tasks. 131/132: manager-tier delegation "
                    "for plan supervision (configurable `routing_policy.manager_tier`, `routingctl.py supervise`, one "
                    "read-only diagnosis per blocker fingerprint, availability faults never escalate, no root model "
                    f"switch). Research: `{NOTE}`. Independent review 132 precedes 082; final review 086 remains last.\n")
GATE_OLD, GATE_NEW = '"126", "128", "130"}', '"126", "128", "130", "132"}'
SELFTEST_ANCHOR = "    def test_autostart_rejected(self):\n"
SELFTEST_CASE = ("    def test_missing_132_review_gate(self):\n"
                 "        def edit(d):t=next(t for t in d['tasks'] if t['id']==82);"
                 "t['dependencies']=[x for x in t['dependencies'] if x!='132'];return d\n"
                 "        self.changed('PLAN1_SPEC.json',edit)\n")

# Manifest task layout (pending task, no completion fields), matching the existing tasks.
MANIFEST_KEYS = ["id", "slug", "title", "objective", "requirement_ids", "complexity", "atomicity_rationale",
                 "context_boundary", "scope", "dependencies", "implementation_guidance", "acceptance_criteria",
                 "validation_commands", "provider", "model_tier", "reasoning_effort", "design_route", "design_phase",
                 "allow_provider_fallback", "related_task_reads", "subtasks", "learning_targets", "learning_files",
                 "published_learning_files", "max_attempts", "status", "attempts", "functional_failures",
                 "failure_classes", "rate_limit_events", "current_route", "started_at", "completed_at", "last_error",
                 "history", "changed_files", "validation_results", "result_file", "context_files", "file",
                 "related_task_files"]
DEFINITION_KEYS = ["slug", "title", "objective", "requirement_ids", "complexity", "atomicity_rationale",
                   "context_boundary", "scope", "dependencies", "implementation_guidance", "acceptance_criteria",
                   "validation_commands", "provider", "model_tier", "reasoning_effort"]
SPEC_ORDER = ["id", "title", "objective", "requirement_ids", "complexity", "atomicity_rationale", "context_boundary",
              "dependencies", "scope", "implementation_guidance", "acceptance_criteria", "validation_commands", "subtasks",
              "provider", "model_tier", "reasoning_effort", "max_attempts", "learning_targets", "related_task_reads"]


class Drift(RuntimeError):
    pass


# ---- format-preserving I/O ------------------------------------------------------------------
def eol_of(raw: bytes) -> str:
    return "\r\n" if b"\r\n" in raw else "\n"


def lf(raw: bytes) -> str:
    return raw.decode("utf-8").replace("\r\n", "\n")


def json_format(text: str, data, trailing: bool = True) -> tuple[int, bool]:
    """(indent, ensure_ascii) that reproduces `text` (LF-normalized) exactly."""
    for ensure_ascii in (False, True):
        for indent in (2, 1, 4):
            if json.dumps(data, indent=indent, ensure_ascii=ensure_ascii) + ("\n" if trailing else "") == text:
                return indent, ensure_ascii
    raise Drift("cannot reproduce the existing JSON layout byte for byte; refusing to rewrite it")


class JsonFile:
    def __init__(self, path: Path):
        raw = path.read_bytes()
        self.path, self.eol = path, eol_of(raw)
        text = lf(raw)
        self.data = json.loads(text)
        self.indent, self.ascii = json_format(text, self.data)

    def render(self) -> bytes:
        text = json.dumps(self.data, indent=self.indent, ensure_ascii=self.ascii) + "\n"
        return text.replace("\n", self.eol).encode("utf-8")


def with_eol(text: str, eol: str) -> bytes:
    return text.replace("\r\n", "\n").replace("\n", eol).encode("utf-8")


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
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


# ---- edits ----------------------------------------------------------------------------------
def upsert_by_id(items: list[dict], item: dict, after_id: str | None = None) -> None:
    for i, existing in enumerate(items):
        if existing.get("id") == item["id"]:
            items[i] = {**existing, **item}
            return
    idx = next((i + 1 for i, x in enumerate(items) if x.get("id") == after_id), len(items))
    items.insert(idx, copy.deepcopy(item))


def replace_items(items: list[str], pairs, where: str) -> list[str]:
    out = list(items)
    for old, new in pairs:
        if old in out:
            out[out.index(old)] = new
        elif new not in out:
            raise Drift(f"{where}: neither old nor new text present: {old[:70]!r}")
    return out


def add_unique(items: list, values) -> None:
    for v in values:
        if v not in items:
            items.append(v)


def manifest_task(spec: dict, existing: dict | None) -> dict:
    task = {
        "id": spec["id"], "slug": spec["slug"], "title": spec["title"], "objective": spec["objective"],
        "requirement_ids": list(spec["requirement_ids"]), "complexity": spec["complexity"],
        "atomicity_rationale": spec["atomicity_rationale"], "context_boundary": copy.deepcopy(spec["context_boundary"]),
        "scope": copy.deepcopy(spec["scope"]), "dependencies": list(spec["dependencies"]),
        "implementation_guidance": list(spec["implementation_guidance"]),
        "acceptance_criteria": [a for a in spec["acceptance_criteria"] if a not in META_LINES]
                               + [a for a in spec["acceptance_criteria"] if a in META_LINES],
        "validation_commands": list(spec["validation_commands"]), "provider": spec["provider"],
        "model_tier": spec["model_tier"], "reasoning_effort": spec["reasoning_effort"], "design_route": None,
        "design_phase": None, "allow_provider_fallback": True, "related_task_reads": [],
        "subtasks": [{"id": sid, "title": title, "objective": objective, "required": True, "status": "pending",
                      "started_at": None, "completed_at": None, "history": []} for sid, title, objective in spec["subtasks"]],
        "learning_targets": [], "learning_files": [], "published_learning_files": [], "max_attempts": 8,
        "status": "pending", "attempts": 0, "functional_failures": 0, "failure_classes": [], "rate_limit_events": 0,
        "current_route": None, "started_at": None, "completed_at": None, "last_error": None, "history": [],
        "changed_files": [], "validation_results": [], "result_file": None, "context_files": ["CONTEXT.md"],
        "file": f"tasks/{spec['id']}-{spec['slug']}.md", "related_task_files": [],
    }
    assert list(task) == MANIFEST_KEYS
    if existing is None:
        return task
    # Already present (re-run, or the runner touched it): refresh definitions, keep runtime state.
    merged = copy.deepcopy(existing)
    for key in DEFINITION_KEYS:
        merged[key] = task[key]
    old_subs = {s["id"]: s for s in existing.get("subtasks", [])}
    merged["subtasks"] = [{**old_subs.get(s["id"], s), "title": s["title"], "objective": s["objective"]}
                          for s in task["subtasks"]]
    return merged


def edit_manifest(m: dict, plan_dir: Path) -> None:
    ra = m["request_analysis"]
    upsert_by_id(ra["request_parts"], P067, after_id="P066")
    upsert_by_id(m["requirements"], R073, after_id="R072")
    if SUMMARY_OLD in m.get("summary", ""):
        m["summary"] = m["summary"].replace(SUMMARY_OLD, SUMMARY_NEW)
    tasks = m["tasks"]
    by_id = {t["id"]: t for t in tasks}
    for dep in DEPS_131:
        if dep not in by_id:
            raise Drift(f"dependency {dep} of 131 is not in the manifest")
    new = [manifest_task(spec, by_id.get(spec["id"])) for spec in NEW_TASKS]
    rest = [t for t in tasks if t["id"] not in NEW_IDS]
    i = next(n for n, t in enumerate(rest) if t["id"] == "082")
    m["tasks"] = rest[:i] + new + rest[i:]
    by_id = {t["id"]: t for t in m["tasks"]}
    t082, t086 = by_id["082"], by_id["086"]
    add_unique(t082["dependencies"], NEW_IDS)
    add_unique(t082["requirement_ids"], ["R073"])
    add_unique(t086["requirement_ids"], ["R073"])
    t082["implementation_guidance"] = replace_items(t082["implementation_guidance"], G082, "082 guidance")
    t082["acceptance_criteria"] = replace_items(t082["acceptance_criteria"], A082, "082 acceptance")
    if not any(ev.get("type") == EVENT["type"] and ev.get("task_ids") == NEW_IDS for ev in m["events"]):
        import planctl_concise
        m["events"].append({"at": planctl_concise.planctl.now_utc(), **copy.deepcopy(EVENT),
                            "task_count": len(m["tasks"])})


def spec_value(t: dict, key: str):
    if key == "id":
        return int(t["id"])
    if key == "subtasks":
        return [{"id": s["id"], "title": s["title"], "objective": s["objective"]} for s in t["subtasks"]]
    return copy.deepcopy(t[key])


def edit_spec(spec: dict, m: dict) -> None:
    upsert_by_id(spec["request_analysis"]["request_parts"], P067, after_id="P066")
    upsert_by_id(spec["requirements"], R073, after_id="R072")
    if SUMMARY_OLD in spec.get("summary", ""):
        spec["summary"] = spec["summary"].replace(SUMMARY_OLD, SUMMARY_NEW)
    by_id = {t["id"]: t for t in m["tasks"]}
    old = {t["id"]: t for t in spec["tasks"]}
    template = list(old[130].keys()) if 130 in old else SPEC_ORDER
    projected = {}
    for tid in NEW_IDS + ["082", "086"]:
        keys = list(old[int(tid)].keys()) if int(tid) in old else template
        projected[int(tid)] = {k: spec_value(by_id[tid], k) for k in keys}
    rest = [projected.get(t["id"], t) for t in spec["tasks"] if t["id"] not in (131, 132)]
    i = next(n for n, t in enumerate(rest) if t["id"] == 82)
    spec["tasks"] = rest[:i] + [projected[131], projected[132]] + rest[i:]


def ti_entry(spec: dict) -> dict:
    tid = spec["id"]
    review = tid == "132"
    inputs = [NOTE] + WRITE_SCOPE + ([*receipts("131")] if review else []) + [REFRESH]
    contract = []
    for path in inputs:
        if path in (NOTE, REFRESH):
            contract.append({"path": path, "availability": "existing_baseline_or_current_file"})
        elif review:
            contract.append({"path": path, "availability": "prerequisite_output", "producer_task": "131"})
        elif path == NEW_TEST:
            contract.append({"path": path, "availability": "create_in_this_task"})
        else:
            contract.append({"path": path, "availability": "existing_baseline_or_current_file"})
    k = sum(1 for a in spec["acceptance_criteria"] if a not in META_LINES)
    return {
        "id": tid, "kind": "review" if review else "implementation", "work_type": "review" if review else "implementation",
        "review_of": "131" if review else None, "requires_independent_review": review, "inputs": inputs,
        "prepared_reports": [NOTE], "output": receipts(tid)[0], "report": receipts(tid)[1],
        "write_scope": list(WRITE_SCOPE), "required_checks": [list(c) for c in CHECKS],
        "acceptance_ids": [f"AC{i:02}" for i in range(1, k + 1)],
        "planned_new_files": [] if review else [NEW_TEST], "input_contract": contract,
        "input_rule": ("Read P067 research and existing sources only; do not read not-yet-created files until the "
                       "producing task generated them; never call a live model in tests or fabricate reviews."),
    }


def edit_task_inputs(ti: dict) -> None:
    upsert_by_id(ti["tasks"], ti_entry(TASK_131), after_id="130")
    upsert_by_id(ti["tasks"], ti_entry(TASK_132), after_id="131")
    e082 = next(e for e in ti["tasks"] if e["id"] == "082")
    for path, extra in TI082_INPUTS:
        if path not in e082["inputs"]:
            e082["inputs"].append(path)
        if "input_contract" in e082 and not any(x["path"] == path for x in e082["input_contract"]):
            e082["input_contract"].append({"path": path, **extra})
    if TI082_CHECK not in e082["required_checks"]:
        e082["required_checks"].append(list(TI082_CHECK))


def edit_service_map(text: str) -> str:
    begin = text.index("<!-- pae-service-map:begin -->")
    start = text.index("```json\n", begin) + len("```json\n")
    end = text.index("\n```", start)
    block = text[start:end]
    data = json.loads(block)
    indent, ensure_ascii = json_format(block, data, trailing=False)
    vals = data["validations"]
    ids = [v["id"] for v in vals]
    for need in ("P1_TESTS_130", "P1_130"):
        if need not in ids:
            raise Drift(f"SERVICE_MAP.md lacks template {need}")
    tmpl = {v["id"]: v for v in vals}
    for tid in NEW_IDS:
        for prefix, name, src in (("P1_TESTS_", "test-check receipt", "P1_TESTS_130"), ("P1_", "acceptance gate", "P1_130")):
            entry = copy.deepcopy(tmpl[src])
            entry["id"], entry["name"] = f"{prefix}{tid}", f"Task {tid} {name}"
            entry["command"] = [tid if (i > 0 and entry["command"][i - 1] == "--task") else c
                                for i, c in enumerate(entry["command"])]
            prev = f"P1_{int(tid) - 1}" if prefix == "P1_TESTS_" else f"P1_TESTS_{tid}"
            upsert_by_id(vals, entry, after_id=prev)
    return text[:start] + json.dumps(data, indent=indent, ensure_ascii=ensure_ascii) + text[end:]


def edit_check_delivery(text: str) -> str:
    if GATE_NEW in text:
        return text
    if GATE_OLD not in text:
        raise Drift("check_delivery.py gate tuple not found")
    return text.replace(GATE_OLD, GATE_NEW, 1)


def edit_gate_self_test(text: str) -> str:
    if SELFTEST_CASE in text:
        return text
    if SELFTEST_ANCHOR not in text:
        raise Drift("delivery_gate_self_test.py anchor not found")
    return text.replace(SELFTEST_ANCHOR, SELFTEST_CASE + SELFTEST_ANCHOR, 1)


ROW = re.compile(r"^\| \[( |x)\] (\d{3}) \| (.*?) \| (.*?) \| (.*)$")


def edit_checklist(text: str, m: dict) -> str:
    tasks = {t["id"]: t for t in m["tasks"]}
    research = f"[P067 research](../../../{NOTE}) |"
    lines = text.split("\n")
    present = {mt.group(2) for mt in map(ROW.match, lines) if mt}
    out, seen = [], set()
    for line in lines:
        mt = ROW.match(line)
        if mt and mt.group(2) in NEW_IDS:
            seen.add(mt.group(2))
            t = tasks[mt.group(2)]
            out.append(f"| [{mt.group(1)}] {t['id']} | {t['title']} | {', '.join(t['dependencies'])} | {research}")
            continue
        if mt and mt.group(2) == "082":
            for tid in NEW_IDS:
                if tid not in present:
                    t = tasks[tid]
                    out.append(f"| [ ] {t['id']} | {t['title']} | {', '.join(t['dependencies'])} | {research}")
                    seen.add(tid)
            t = tasks["082"]
            line = f"| [{mt.group(1)}] 082 | {t['title']} | {', '.join(t['dependencies'])} | {mt.group(5)}"
        out.append(line)
    if seen != set(NEW_IDS):
        raise Drift("IMPLEMENTATION_CHECKLIST.md has no 082 row to anchor 131/132")
    return "\n".join(out)


def edit_integration(text: str) -> str:
    if INTEGRATION_MARKER in text:
        head = text[:text.index(INTEGRATION_MARKER)]
        return head + INTEGRATION_TEXT
    return text.rstrip("\n") + "\n\n" + INTEGRATION_TEXT


# ---- checks ---------------------------------------------------------------------------------
def self_checks(old_m: dict, m: dict, spec: dict, ti: dict, pc, artifact_contract) -> list[str]:
    problems = []
    n = len(m["tasks"])
    if not (n == len(spec["tasks"]) == len(ti["tasks"])):
        problems.append(f"task counts differ: manifest {n}, spec {len(spec['tasks'])}, TASK_INPUTS {len(ti['tasks'])}")
    if m["tasks"][-1]["id"] != "086" or spec["tasks"][-1]["id"] != 86:
        problems.append("086 is not last")
    order = [t["id"] for t in m["tasks"]]
    if order.index("131") > order.index("132") or order.index("132") > order.index("082"):
        problems.append("131/132 are not placed before 082")
    old_by_id = {t["id"]: t for t in old_m["tasks"]}
    for t in m["tasks"]:
        before = old_by_id.get(t["id"])
        if before is None:
            continue
        if t["id"] in ("082", "086"):
            changed = {k for k in set(t) | set(before) if t.get(k) != before.get(k)}
            if changed - {"dependencies", "requirement_ids", "implementation_guidance", "acceptance_criteria"}:
                problems.append(f"{t['id']}: unexpected fields changed {sorted(changed)}")
        elif t["id"] not in NEW_IDS and t != before:
            problems.append(f"{t['id']}: an existing task changed")
        elif t["id"] in NEW_IDS and any(t.get(k) != before.get(k) for k in set(before) - set(DEFINITION_KEYS) - {"subtasks"}):
            problems.append(f"{t['id']}: runtime state of an already-added task changed")
    if set(old_by_id) - {t["id"] for t in m["tasks"]}:
        problems.append("an existing task disappeared")
    if m.get("autostart") is not False or spec.get("autostart") is not False:
        problems.append("autostart must stay false")
    gates = {e["id"] for e in ti["tasks"] if e.get("review_of") and e["review_of"] > "086"} | {"132"}
    missing = gates - set(next(t for t in m["tasks"] if t["id"] == "082")["dependencies"])
    if missing:
        problems.append(f"082 lacks review gates {sorted(missing)}")
    for text, budget in ((P067["text"], 280), (R073["text"], 280)):
        if len(text) > budget or "\n" in text:
            problems.append(f"request text over budget or multi-line: {text[:40]!r}")
    try:
        pc.validate_task_graph(m["tasks"])
    except Exception as exc:  # noqa: BLE001
        problems.append(f"dependency graph: {exc}")
    spec_by_id = {f"{t['id']:03}": t for t in spec["tasks"]}
    for t in m["tasks"]:
        st = spec_by_id.get(t["id"])
        if st is None:
            problems.append(f"{t['id']}: missing from spec")
            continue
        for field in ("title", "objective", "dependencies", "implementation_guidance", "acceptance_criteria"):
            if st[field] != t[field]:
                problems.append(f"{t['id']}: spec/manifest {field} mismatch")
    for e in ti["tasks"]:
        t = next((x for x in m["tasks"] if x["id"] == e["id"]), None)
        if t is not None and len(e["acceptance_ids"]) > len(t["acceptance_criteria"]):
            problems.append(f"{e['id']}: acceptance_ids exceed criteria")

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


# ---- main -----------------------------------------------------------------------------------
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

    if not (root / NOTE).is_file():
        print(f"PROBLEM: missing research note {NOTE}", file=sys.stderr)
        return 2
    try:
        mf = JsonFile(plan_dir / "manifest.json")
        sf, tf = JsonFile(doc / "PLAN1_SPEC.json"), JsonFile(doc / "TASK_INPUTS.json")
        rt = JsonFile(doc / "REPLAN_TRACE.json")
        old_m = copy.deepcopy(mf.data)
        edit_manifest(mf.data, plan_dir)
        edit_spec(sf.data, mf.data)
        edit_task_inputs(tf.data)
        add_unique(rt.data["post_conversion_refinements"], [REFINEMENT])

        problems = self_checks(old_m, mf.data, sf.data, tf.data, pc, artifact_contract)
        if problems:
            for p in problems:
                print("PROBLEM:", p, file=sys.stderr)
            return 2

        outputs: dict[Path, bytes] = {sf.path: sf.render(), tf.path: tf.render(), rt.path: rt.render()}
        m = mf.data
        manifest_changed = m != old_m
        plan_id, work_root = m["plan_id"], m.get("work_root")
        by_id = {t["id"]: t for t in m["tasks"]}
        sibling_eol = eol_of((plan_dir / by_id["130"]["file"]).read_bytes())
        for tid in NEW_IDS + ["082", "086"]:
            path = plan_dir / by_id[tid]["file"]
            eol = eol_of(path.read_bytes()) if path.is_file() else sibling_eol
            outputs[path] = with_eol(pc.render_task(by_id[tid], plan_id, work_root), eol)
        for name, render in (("TODO.md", pc.render_todo), ("PLAN.md", pc.render_plan), ("ANALYSIS.md", pc.render_analysis)):
            path = plan_dir / name
            outputs[path] = with_eol(render(m), eol_of(path.read_bytes()))

        def text_edit(path: Path, fn) -> None:
            raw = path.read_bytes()
            outputs[path] = with_eol(fn(lf(raw)), eol_of(raw))

        text_edit(root / ".ai-work/SERVICE_MAP.md", edit_service_map)
        text_edit(doc / "support/check_delivery.py", edit_check_delivery)
        text_edit(doc / "support/delivery_gate_self_test.py", edit_gate_self_test)
        text_edit(doc / "IMPLEMENTATION_CHECKLIST.md", lambda s: edit_checklist(s, m))
        text_edit(doc / "IMPLEMENTATION_INTEGRATION.md", edit_integration)
        ext = doc / REQUEST_EXTENSION
        sibling = doc / "REQUEST_EXTENSION_20261120_CODING_STANDARDS.md"
        outputs[ext] = with_eol(REQUEST_EXTENSION_TEXT, eol_of(sibling.read_bytes()) if sibling.is_file() else "\n")
    except (Drift, KeyError, StopIteration, ValueError) as exc:
        print(f"PROBLEM: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2

    changed = [p for p, data in outputs.items() if not p.is_file() or p.read_bytes() != data]
    if manifest_changed:
        changed.append(mf.path)
    if not changed:
        print("0 file(s) would change; P067/131/132 already applied")
        return 0
    if args.check:
        for p in changed:
            print("would change:", p.relative_to(root).as_posix())
        print(f"{len(changed)} file(s) would change")
        return 1
    if runner_is_live(plan_dir):
        print("REFUSED: the plan runner lease is live; stop the runner first", file=sys.stderr)
        return 3
    for p in changed:
        if p == mf.path:
            continue
        atomic_write(p, outputs[p])
        print("wrote:", p.relative_to(root).as_posix())
    if manifest_changed:  # last, so an interrupted run never leaves tasks without definition files
        m["updated_at"] = pc.now_utc()
        atomic_write(mf.path, mf.render())
        print("wrote:", mf.path.relative_to(root).as_posix())
    print(f"{len(changed)} file(s) changed")

    # Post-write verification with the plan's own read-only validators.
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
