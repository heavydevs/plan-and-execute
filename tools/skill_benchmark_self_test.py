#!/usr/bin/env python3
"""Self-test for tools/skill_benchmark.py: determinism, cost accounting, gate and report."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import skill_benchmark as sb  # noqa: E402

CORPUS = sb._load(ROOT / sb.CORPUS_PATH)
THRESHOLDS = sb._load(ROOT / CORPUS["thresholds"])
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    print(f"{'ok ' if condition else 'FAIL'} {name}{': ' + detail if detail and not condition else ''}")
    if not condition:
        FAILURES.append(name)


def only(categories: tuple[str, ...]) -> dict:
    corpus = copy.deepcopy(CORPUS)
    corpus["categories"] = list(categories)
    corpus["cases"] = [c for c in corpus["cases"] if c["category"] in categories]
    return corpus


def test_corpus_and_determinism() -> None:
    check("corpus is valid", not sb.validate_corpus(CORPUS), "; ".join(sb.validate_corpus(CORPUS)))
    wanted = {"direct", "orchestrated", "large_request", "stall_failure", "resource_failure",
              "provider_availability", "tier_variant", "delegation_variant", "cache_warm", "cache_cold"}
    check("corpus covers every category", wanted <= set(CORPUS["categories"]))
    runs = sb.run_corpus(CORPUS)
    check("every category runs in both arms",
          all({r["arm"] for r in runs if r["category"] == c} == set(sb.ARMS) for c in wanted))
    first = json.dumps(sb.scorecard(CORPUS, THRESHOLDS), sort_keys=True)
    second = json.dumps(sb.scorecard(copy.deepcopy(CORPUS), copy.deepcopy(THRESHOLDS)), sort_keys=True)
    check("identical inputs yield an identical scorecard", first == second)
    shuffled = copy.deepcopy(CORPUS)
    shuffled["cases"].reverse()
    third = json.loads(json.dumps(sb.scorecard(shuffled, THRESHOLDS), sort_keys=True))
    third.pop("corpus_sha256")
    base = json.loads(first)
    base.pop("corpus_sha256")
    check("case order does not change metrics", third == base)


def test_cost_all_worker_kinds() -> None:
    card = sb.scorecard(CORPUS, THRESHOLDS)
    for arm in sb.ARMS:
        overall = card["arms"][arm]["overall"]
        kinds = overall["cost_by_kind"]
        check(f"{arm}: cost covers every worker kind", all(kinds[k]["attempts"] > 0 for k in kinds),
              json.dumps({k: v["attempts"] for k, v in kinds.items()}))
        total_input = sum(v["input_tokens"] or 0 for v in kinds.values())
        expect = round(total_input / overall["validated"], 6)
        check(f"{arm}: cost per validated input sums all kinds",
              overall["cost_per_validated_result"]["input_tokens"] == expect)
        check(f"{arm}: unreported credits/usd stay null", overall["cost_per_validated_result"]["credits"] is None
              and overall["cost_per_validated_result"]["usd"] is None)


def test_committed_scorecard_gate() -> None:
    card = sb.scorecard(CORPUS, THRESHOLDS)
    gate = card["gate"]
    check("committed corpus is inconclusive and fails", gate["verdict"] == "fail" and not gate["auto_route_segments"])
    check("every committed segment reports minimum_sample inconclusive",
          all(s["checks"]["minimum_sample"]["status"] == "inconclusive" for s in gate["segments"].values()))
    low = gate["segments"]["deterministic_low_blast"]["checks"]["material_gain"]
    check("delegation cost shift blocks material gain", low["status"] == "fail"
          and "attempts_per_validated" in low["shifted_units"], json.dumps(low))
    check("no candidate floor violations",
          card["arms"]["candidate"]["overall"]["floor_violations"] == 0)


def test_gate_pass_and_regression() -> None:
    corpus = only(("direct", "cache_cold"))
    passing = sb.scorecard(corpus, THRESHOLDS, repetitions=80)
    seg = passing["gate"]["segments"]["deterministic_low_blast"]
    check("powered matched fixture passes non-inferiority", passing["gate"]["verdict"] == "pass", json.dumps(seg))
    check("safe segment with material gain is auto-route eligible",
          passing["gate"]["auto_route_segments"] == ["deterministic_low_blast"])

    regressed = copy.deepcopy(corpus)
    case = next(c for c in regressed["cases"] if c["category"] == "direct")
    case["arms"]["candidate"]["attempts"][0]["validation_pass"] = False
    card = sb.scorecard(regressed, THRESHOLDS, repetitions=80)
    reg = card["gate"]["segments"]["deterministic_low_blast"]["checks"]["regression_margin"]
    check("validated completion drop beyond margin fails the gate",
          card["gate"]["verdict"] == "fail" and reg["status"] == "fail"
          and reg["validated_lower_bound"] < -THRESHOLDS["thresholds"]["regression_margin"]["value"], json.dumps(reg))
    check("regressed segment is not auto-route eligible", not card["gate"]["auto_route_segments"])

    under = copy.deepcopy(corpus)
    case = next(c for c in under["cases"] if c["category"] == "direct")
    case["minimum_acceptable_route"] = {"tier": "standard", "effort": "medium"}
    card = sb.scorecard(under, THRESHOLDS, repetitions=80)
    ur = card["gate"]["segments"]["deterministic_low_blast"]["checks"]["under_routing_limit"]
    check("candidate below a case floor fails under-routing", card["gate"]["verdict"] == "fail"
          and ur["floor_violations"] > 0, json.dumps(ur))

    check("newcombe bound tightens with sample size at equal rates",
          sb.newcombe_lower((30, 30), (30, 30)) < sb.newcombe_lower((300, 300), (300, 300)) < 0)


def test_recorded_telemetry() -> None:
    record = {"task_id": "T9", "kind": "root", "task_class": "mechanical", "validation_strength": "strong",
              "provider": "claude", "profile": None, "harness": "claude", "model": "claude-sonnet-5",
              "native_effort": "medium", "input_tokens": 1000, "cached_tokens": None, "cache_write_tokens": None,
              "output_tokens": 200, "credits": None, "usd": None, "latency_seconds": 9.0, "outcome": "completed",
              "failure_class": None, "validation_pass": True, "retry_count": 0, "prompt": "must be dropped"}
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "attempts.jsonl"
        path.write_text(json.dumps(record) + "\n" + json.dumps({**record, "kind": "subagent",
                                                               "validation_pass": None}) + "\n", encoding="utf-8")
        out = Path(tmp) / "card.json"
        import contextlib
        import io
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = sb.main(["run", "--telemetry", f"candidate={path}"])
        out.write_text(buffer.getvalue(), encoding="utf-8")
        card = json.loads(out.read_text(encoding="utf-8"))
    rec = card["arms"]["candidate"]["by_category"].get(sb.RECORDED_CATEGORY)
    check("recorded telemetry is accepted", code == 0 and card["recorded_attempts"]["candidate"] == 2)
    check("recorded runs reuse the aggregation", bool(rec) and rec["validated"] == 1 and rec["attempts"] == 2
          and rec["cost_per_validated_result"]["input_tokens"] == 2000, json.dumps(rec))
    runs = sb._recorded_runs("candidate", [record], "guarded")
    check("recorded records keep only PAT003 fields", "prompt" not in runs[0]["records"][0])


def test_report_matches() -> None:
    document = (ROOT / sb.REPORT_PATH).read_text(encoding="utf-8")
    block = sb.render(sb.scorecard(CORPUS, THRESHOLDS))
    check("committed SKILL_BENCHMARK.md scorecard matches", sb.splice(document, block) == document,
          "run: python tools/skill_benchmark.py report")


def main() -> int:
    for test in (test_corpus_and_determinism, test_cost_all_worker_kinds, test_committed_scorecard_gate,
                 test_gate_pass_and_regression, test_recorded_telemetry, test_report_matches):
        test()
    if FAILURES:
        print(f"{len(FAILURES)} check(s) failed", file=sys.stderr)
        return 1
    print("skill benchmark self-test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
