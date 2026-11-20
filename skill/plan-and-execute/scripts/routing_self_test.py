#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
METADATA = ROOT / "agents" / "openai.yaml"
EVALS = ROOT / "references" / "routing-evals.json"


def fail(message: str) -> None:
    raise AssertionError(message)


skill = SKILL.read_text(encoding="utf-8")
match = re.match(r"^---\n([\s\S]*?)\n---\n", skill)
if not match:
    fail("SKILL.md frontmatter missing")
frontmatter = match.group(1)
description_match = re.search(r"^description:\s*(.+)$", frontmatter, re.M)
if not description_match:
    fail("description missing")
description = description_match.group(1).strip()
if len(description) > 1536:
    fail("description exceeds Claude listing budget")
for needle in (
    "long-horizon",
    "durable resumability",
    "independently verifiable workstreams",
    "Do not use for routine bug fixes",
    "cohesive small/medium changes",
    "prefer direct execution",
    "promote later",
):
    if needle not in description:
        fail(f"description missing routing discriminator: {needle}")

body = skill[match.end():]
if len(body) > 6500:
    fail(f"SKILL.md body is too large for a cheap router: {len(body)}")
for needle in (
    "DIRECT EXIT",
    "create no `.ai-work`",
    "When uncertain, prefer DIRECT",
    "references/PROMOTION.md",
    "references/ORCHESTRATION.md",
    "model_tier",
    "reasoning_effort",
):
    if needle not in body:
        fail(f"SKILL.md router missing: {needle}")

metadata = METADATA.read_text(encoding="utf-8")
if "allow_implicit_invocation: true" not in metadata:
    fail("bundled selective mode must allow precise implicit invocation")
if "disable-model-invocation: true" in frontmatter:
    fail("bundled source must remain selective; explicit mode is an installer transform")

payload = json.loads(EVALS.read_text(encoding="utf-8"))
if payload.get("schema_version") != 1:
    fail("routing eval schema_version must be 1")
cases = payload.get("cases")
if not isinstance(cases, list):
    fail("routing eval cases must be a list")
ids = [case.get("id") for case in cases]
if len(ids) != len(set(ids)):
    fail("routing eval ids must be unique")
counts = {route: sum(case.get("expected_route") == route for case in cases) for route in ("direct", "orchestrated", "promote")}
if counts["direct"] < 12 or counts["orchestrated"] < 8 or counts["promote"] < 2:
    fail(f"routing eval corpus is too small: {counts}")
if sum(bool(case.get("near_miss")) for case in cases) < 8:
    fail("routing eval corpus needs more near-miss negatives")

# P003 is intentionally a DIRECT near miss despite high context pressure.
p003 = next(case for case in cases if case.get("id") == "P003")
if p003.get("expected_route") != "direct":
    fail("P003 must remain DIRECT when only a tiny cohesive fix remains")
if "do not promote" not in p003.get("prompt", "").lower():
    fail("P003 must preserve the high-context-nearly-done counterexample")

for case in cases:
    if case.get("expected_route") not in {"direct", "orchestrated", "promote", "lifecycle"}:
        fail(f"{case.get('id')} has an unsupported expected_route")
    if case.get("split", "tuning") not in {"tuning", "held_out"}:
        fail(f"{case.get('id')} has an unsupported split")

held_out = [case for case in cases if case.get("split") == "held_out"]
tuning = [case for case in cases if case.get("split") != "held_out"]
if len(held_out) < 12:
    fail("routing eval corpus needs held-out cases across strata")
categories = {case.get("category") for case in held_out}
for required_cat in (
    "short_high_risk",
    "long_repetitive_log",
    "medium_cohesive_crud",
    "cohesive_near_miss",
    "near_finished_high_context",
    "independent_or_cross_cutting",
    "explicit_invocation",
    "late_promotion",
    "lifecycle_command",
):
    if required_cat not in categories:
        fail(f"held-out corpus missing category: {required_cat}")


def normalized_prompt(case: dict) -> str:
    return " ".join(case.get("prompt", "").lower().split())


if {normalized_prompt(c) for c in held_out} & {normalized_prompt(c) for c in tuning}:
    fail("held-out prompts must be distinct from tuning prompts")
LABEL_LEAK = re.compile(r"\b(?:do not promote|don't promote|promot\w*|orchestrat\w*|stay direct|plan files|no plan)\b")
for case in held_out:
    if LABEL_LEAK.search(case["prompt"].lower()):
        fail(f"held-out prompt {case['id']} contains route-label text")

import sys  # noqa: E402
scripts_dir = str(Path(__file__).resolve().parent)
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)
import requestctl  # noqa: E402

protocol = payload.get("held_out_protocol")
if not isinstance(protocol, dict) or not isinstance(protocol.get("ceilings"), dict):
    fail("routing-evals.json must record held_out_protocol with regression ceilings")
eval_report = requestctl.evaluate_routing_corpus(cases, skill_root=ROOT, protocol=protocol)
if eval_report["entrypoint_bytes"]["SKILL.md"] > 7000:
    fail(f"SKILL.md exceeds 7000 bytes: {eval_report['entrypoint_bytes']['SKILL.md']}")
if eval_report["metric"] != "offline_cue_extractor_proxy":
    fail("the corpus metric must be labeled as the offline cue-extractor proxy")

# The held-out split is only meaningful while the cue table is the one frozen before it was authored.
integrity = eval_report["held_out_integrity"]
if integrity["status"] != "frozen":
    fail(
        "requestctl.ACTIVATION_CUES changed after the held-out split was authored "
        f"({integrity}); move the seen held-out cases to tuning, author fresh held-out prompts without "
        "access to the cue table, then record the new cue_table_sha256 and ceilings"
    )

# Tuning cases are in-sample: an exact match there is a regression lock, not a generalization claim.
tuned = eval_report["tuning"]["selective_cue_proxy"]
if tuned["exact_match"] != tuned["total"]:
    fail(f"tuning split regressed: {tuned}")

held = eval_report["held_out"]
sel = held["selective_cue_proxy"]
ceilings = protocol["ceilings"]
if sel["false_positive_rate"] > ceilings["max_false_positive_rate"]:
    fail(f"held-out false-positive rate regressed: {sel}")
if sel["false_negative_rate"] > ceilings["max_false_negative_rate"]:
    fail(f"held-out false-negative rate regressed: {sel}")
if sel["accuracy"] < ceilings["min_accuracy"]:
    fail(f"held-out accuracy regressed: {sel}")
known = set(protocol.get("known_misses", []))
new_misses = [row["id"] for row in eval_report["held_out_errors"] if row["id"] not in known]
if new_misses:
    fail(f"new held-out routing misses: {new_misses}")
if sel["false_positive_rate"] >= held["always_orchestrate"]["false_positive_rate"]:
    fail("selective proxy must create fewer unneeded plans than always-orchestrate on held-out cases")
if sel["false_negative_rate"] >= held["all_direct"]["false_negative_rate"]:
    fail("selective proxy must miss fewer orchestration needs than all-direct on held-out cases")
if eval_report["expected_cost_model"]["status"] != "costs_unmeasured" or eval_report["expected_cost_model"]["c_recovery"] is not None:
    fail("cost terms must stay unmeasured rather than invented")

capability = eval_report["capability_preservation"]
d016_cap = next(c for c in capability if c["id"] == "D016")
if d016_cap["route"] != "direct" or d016_cap["actual_tier"] != "strong":
    fail(f"D016 must stay direct with strong capability floor: {d016_cap}")
held_cap = [c for c in capability if c["split"] == "held_out"]
if any(c["route"] != "direct" for c in held_cap):
    fail(f"held-out short high-risk fixes must stay direct: {held_cap}")
if sum(c["actual_tier"] == "strong" for c in held_cap) < ceilings["min_capability_floor_hits"]:
    fail(f"held-out capability floor regressed: {held_cap}")
if eval_report["live_host_evaluation"]["status"] != "unmeasured_limitation":
    fail("live host evaluation must record an unmeasured limitation when not run")

print(
    f"routing self-test passed ({len(cases)} cases: {len(tuning)} tuning, {len(held_out)} held-out; "
    f"SKILL.md={eval_report['entrypoint_bytes']['SKILL.md']}B; offline proxy held-out "
    f"FP={sel['false_positive_rate']} FN={sel['false_negative_rate']} accuracy={sel['accuracy']}; "
    f"all-direct FN={held['all_direct']['false_negative_rate']}, "
    f"always-orchestrate FP={held['always_orchestrate']['false_positive_rate']})."
)
