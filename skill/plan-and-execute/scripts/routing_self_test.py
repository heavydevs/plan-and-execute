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

print(f"routing self-test passed ({len(cases)} cases: {counts}).")
