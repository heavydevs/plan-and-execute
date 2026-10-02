#!/usr/bin/env python3
"""Whole-skill quality/economy benchmark with the predeclared non-inferiority gate.

run:     replay the fixed offline corpus (docs/research/routing-eval/benchmark-corpus.json)
         for the main and candidate arms, optionally adding recorded PAT003 telemetry
         from real runs (--telemetry ARM=PATH), and print the scorecard JSON.
report:  render the scorecard into docs/research/SKILL_BENCHMARK.md between markers;
         --check diffs it against the committed report instead of writing.

The scorecard is a pure function of the corpus, thresholds and telemetry inputs: no
clock, randomness or provider calls. Gate thresholds come only from thresholds.json.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skill" / "plan-and-execute" / "scripts"
CORPUS_PATH = "docs/research/routing-eval/benchmark-corpus.json"
REPORT_PATH = "docs/research/SKILL_BENCHMARK.md"
BEGIN = "<!-- BEGIN GENERATED SCORECARD -->"
END = "<!-- END GENERATED SCORECARD -->"
SCHEMA_VERSION = 1
ARMS = ("main", "candidate")
Z_ONE_SIDED_95 = 1.6448536269514722
RECORDED_CATEGORY = "recorded"
OTHER_UNITS = ("cached_tokens", "cache_write_tokens", "credits", "usd")
GUARD_RISE = 0.05
LATENCY_RISE = 0.25


def _scripts() -> tuple[Any, Any]:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    import routing_telemetry
    import routingctl
    return routing_telemetry, routingctl


def _load(path: Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(data: Any) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _num(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


# ---------------------------------------------------------------- corpus runner

def validate_corpus(corpus: dict[str, Any]) -> list[str]:
    _, routingctl = _scripts()
    errors: list[str] = []
    categories = corpus.get("categories") or []
    seen: dict[str, int] = {c: 0 for c in categories}
    ids: set[str] = set()
    for case in corpus.get("cases") or []:
        cid = case.get("id")
        if cid in ids:
            errors.append(f"duplicate case id {cid}")
        ids.add(cid)
        if case.get("category") not in seen:
            errors.append(f"{cid}: unknown category {case.get('category')}")
        else:
            seen[case["category"]] += 1
        floor = case.get("minimum_acceptable_route") or {}
        if floor.get("tier") not in routingctl.TIER_ORDER or floor.get("effort") not in routingctl.EFFORT_ORDER:
            errors.append(f"{cid}: invalid minimum_acceptable_route")
        for arm in ARMS:
            spec = (case.get("arms") or {}).get(arm) or {}
            if not spec.get("attempts"):
                errors.append(f"{cid}: arm {arm} has no attempts")
            for attempt in spec.get("attempts") or []:
                extra = set(attempt) - set(_scripts()[0].RECORD_FIELDS)
                if extra:
                    errors.append(f"{cid}/{arm}: non-telemetry fields {sorted(extra)}")
    errors += [f"category {c} has no cases" for c, n in seen.items() if n == 0]
    return errors


def _record(case: dict[str, Any], route: dict[str, Any], attempt: dict[str, Any]) -> dict[str, Any]:
    telemetry, _ = _scripts()
    base = {name: None for name in telemetry.RECORD_FIELDS}
    base.update({
        "task_id": case["id"], "kind": "root", "task_class": case.get("task_class"),
        "validation_strength": case.get("validation_strength"), "provider": route.get("provider"),
        "harness": route.get("provider"), "model": route.get("model"), "native_effort": route.get("effort"),
        "outcome": "completed", "retry_count": 0,
    })
    base.update(attempt)
    return base


def _recorded_runs(arm: str, records: list[dict[str, Any]], segment: str) -> list[dict[str, Any]]:
    """Group recorded real-run telemetry by task_id; keep only PAT003 metadata fields."""
    telemetry, _ = _scripts()
    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        clean = {name: record.get(name) for name in telemetry.RECORD_FIELDS}
        grouped.setdefault(str(clean["task_id"]), []).append(clean)
    runs = []
    for task_id in sorted(grouped):
        runs.append({"case_id": f"recorded:{task_id}", "category": RECORDED_CATEGORY, "segment": segment,
                     "arm": arm, "rep": 0, "route": None, "floor": None, "records": grouped[task_id]})
    return runs


def run_corpus(corpus: dict[str, Any], repetitions: int | None = None,
               recorded: dict[str, list[dict[str, Any]]] | None = None,
               recorded_segment: str = "guarded") -> list[dict[str, Any]]:
    """Deterministic offline replay: one run per case, arm and repetition."""
    reps = int(repetitions if repetitions is not None else corpus.get("repetitions", 1))
    runs: list[dict[str, Any]] = []
    for case in sorted(corpus["cases"], key=lambda c: c["id"]):
        for arm in ARMS:
            spec = case["arms"][arm]
            records = [_record(case, spec["route"], a) for a in spec["attempts"]]
            for rep in range(reps):
                runs.append({"case_id": case["id"], "category": case["category"], "segment": case["segment"],
                             "arm": arm, "rep": rep, "route": spec["route"],
                             "floor": case["minimum_acceptable_route"],
                             "records": [dict(r) for r in records]})
    for arm in ARMS:
        runs += _recorded_runs(arm, (recorded or {}).get(arm) or [], recorded_segment)
    return runs


# ---------------------------------------------------------------- aggregation

def _final(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    graded = [r for r in records if r.get("kind") in ("root", "retry")]
    if not graded:
        return None
    top = max(int(r.get("retry_count") or 0) for r in graded)
    return [r for r in graded if int(r.get("retry_count") or 0) == top][-1]


def run_validated(run: dict[str, Any]) -> bool:
    final = _final(run["records"])
    return bool(final and final.get("validation_pass") is True)


def run_first_validated(run: dict[str, Any]) -> bool:
    return any(r.get("kind") == "root" and int(r.get("retry_count") or 0) == 0 and r.get("validation_pass") is True
               for r in run["records"])


def under_routed(run: dict[str, Any]) -> bool:
    _, routingctl = _scripts()
    route, floor = run.get("route"), run.get("floor")
    if not route or not floor:
        return False
    tier = routingctl.TIER_ORDER.index(routingctl.normalize_tier(route["tier"]))
    wanted = routingctl.TIER_ORDER.index(floor["tier"])
    if tier != wanted:
        return tier < wanted
    return routingctl.EFFORT_ORDER.index(route["effort"]) < routingctl.EFFORT_ORDER.index(floor["effort"])


def p95(values: list[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    return ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)]


def _ratio(value: Any, count: int) -> float | None:
    return round(value / count, 6) if count and _num(value) else None


def metrics(runs: list[dict[str, Any]]) -> dict[str, Any]:
    """Native-unit scorecard for a group of runs; cost sums every worker kind."""
    telemetry, _ = _scripts()
    records = [r for run in runs for r in run["records"]]
    rolled = telemetry.rollup(records, max_bytes=10 ** 9)
    cases = len(runs)
    validated = sum(1 for run in runs if run_validated(run))
    first = sum(1 for run in runs if run_first_validated(run))
    totals = rolled["totals"]
    cost = {field: _ratio(totals[field], validated) for field in telemetry.USAGE_FIELDS}
    io = [totals[f] for f in ("input_tokens", "output_tokens") if _num(totals[f])]
    cost["io_tokens"] = _ratio(sum(io), validated) if io else None
    latencies = [sum(r["latency_seconds"] for r in run["records"] if _num(r.get("latency_seconds")))
                 for run in runs if run_validated(run)]
    by_kind = {kind: {field: rolled["by_kind"][kind][field] for field in ("attempts", *telemetry.USAGE_FIELDS)}
               for kind in telemetry.KINDS}
    return {
        "cases": cases,
        "validated": validated,
        "validated_success_rate": _ratio(validated, cases),
        "first_validated": first,
        "first_attempt_validated_success": _ratio(first, cases),
        "attempts": totals["attempts"],
        "attempts_per_validated": _ratio(totals["attempts"], validated),
        "cost_per_validated_result": cost,
        "cost_by_kind": by_kind,
        "latency_p95": p95(latencies),
        "floor_violations": sum(1 for run in runs if under_routed(run)),
    }


# ---------------------------------------------------------------- gate

def wilson(successes: int, n: int, z: float = Z_ONE_SIDED_95) -> tuple[float, float]:
    if n == 0:
        return 0.0, 1.0
    p = successes / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z / denom * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return max(0.0, center - half), min(1.0, center + half)


def newcombe_lower(cand: tuple[int, int], main: tuple[int, int], z: float = Z_ONE_SIDED_95) -> float:
    """One-sided lower bound of candidate minus main (Newcombe hybrid score)."""
    p1, p2 = cand[0] / cand[1], main[0] / main[1]
    l1, _ = wilson(*cand, z)
    _, u2 = wilson(*main, z)
    return round((p1 - p2) - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2), 6)


def _rise(cand: Any, main: Any) -> float | None:
    if not _num(cand) or not _num(main) or main == 0:
        return None
    return round(cand / main - 1, 6)


def gate_segment(segment: str, main_runs: list[dict[str, Any]], cand_runs: list[dict[str, Any]],
                 thresholds: dict[str, Any]) -> dict[str, Any]:
    t = thresholds["thresholds"]
    m, c = metrics(main_runs), metrics(cand_runs)
    checks: dict[str, Any] = {}

    sample = t["minimum_sample"]["value"]
    small = [cat for cat in sorted({r["category"] for r in main_runs + cand_runs} - {RECORDED_CATEGORY})
             if len({r["case_id"] for r in cand_runs if r["category"] == cat}) < sample["cases_per_category"]]
    enough = min(m["validated"], c["validated"]) >= sample["validated_attempts_per_segment_per_arm"] and not small
    checks["minimum_sample"] = {"status": "pass" if enough else "inconclusive",
                                "validated": {"main": m["validated"], "candidate": c["validated"]},
                                "thin_categories": small}

    margin = t["regression_margin"]["value"]
    if m["cases"] and c["cases"]:
        vs = newcombe_lower((c["validated"], c["cases"]), (m["validated"], m["cases"]))
        fa = newcombe_lower((c["first_validated"], c["cases"]), (m["first_validated"], m["cases"]))
        ok = vs >= -margin and fa >= -0.05
        checks["regression_margin"] = {"status": "pass" if ok else "fail", "validated_lower_bound": vs,
                                       "first_attempt_lower_bound": fa, "margin": margin}
    else:
        checks["regression_margin"] = {"status": "inconclusive"}

    limit = t["under_routing_limit"]["value"]
    main_ok = {(r["case_id"], r["rep"]) for r in main_runs if run_validated(r)}
    attributed = sum(1 for r in cand_runs
                     if (r["case_id"], r["rep"]) in main_ok and not run_validated(r) and under_routed(r))
    rate = attributed / c["cases"] if c["cases"] else 0.0
    upper = wilson(attributed, c["cases"])[1] if c["cases"] else 1.0
    ok = (c["floor_violations"] <= limit["floor_violation_max_count"]
          and rate <= limit["attributed_failure_max_rate"] and upper <= limit["attributed_failure_upper_bound_max"])
    checks["under_routing_limit"] = {"status": "pass" if ok else "fail", "floor_violations": c["floor_violations"],
                                     "attributed_failures": attributed, "attributed_rate": round(rate, 6),
                                     "attributed_upper_bound": round(upper, 6)}

    gain_need = t["material_gain"]["value"]
    mc, cc = m["cost_per_validated_result"], c["cost_per_validated_result"]
    gains = {unit: _rise(cc[unit], mc[unit]) for unit in ("io_tokens", "credits")}
    winners = [u for u, g in gains.items() if g is not None and -g >= gain_need]
    rises = {u: _rise(cc[u], mc[u]) for u in (*OTHER_UNITS, "io_tokens")}
    rises["attempts_per_validated"] = _rise(c["attempts_per_validated"], m["attempts_per_validated"])
    shifted = [u for u, r in rises.items() if u not in winners and r is not None and r > GUARD_RISE]
    lat = _rise(c["latency_p95"], m["latency_p95"])
    ok = bool(winners) and not shifted and (lat is None or lat <= LATENCY_RISE)
    checks["material_gain"] = {"status": "pass" if ok else "fail", "reduction_units": winners,
                               "relative_change": {u: gains[u] for u in sorted(gains)},
                               "shifted_units": sorted(shifted), "latency_p95_rise": lat}

    non_inferior = all(checks[k]["status"] == "pass" for k in ("minimum_sample", "regression_margin",
                                                                "under_routing_limit"))
    safe = segment in t["safe_segments"]["value"]
    auto = non_inferior and checks["material_gain"]["status"] == "pass" and safe
    return {"checks": checks, "non_inferior": non_inferior, "safe_segment": safe, "auto_route_eligible": auto}


def scorecard(corpus: dict[str, Any], thresholds: dict[str, Any], repetitions: int | None = None,
              recorded: dict[str, list[dict[str, Any]]] | None = None,
              recorded_segment: str = "guarded") -> dict[str, Any]:
    runs = run_corpus(corpus, repetitions, recorded, recorded_segment)
    arms: dict[str, Any] = {}
    for arm in ARMS:
        mine = [r for r in runs if r["arm"] == arm]
        arms[arm] = {
            "overall": metrics(mine),
            "by_category": {cat: metrics([r for r in mine if r["category"] == cat])
                            for cat in sorted({r["category"] for r in mine})},
            "by_segment": {seg: metrics([r for r in mine if r["segment"] == seg])
                           for seg in sorted({r["segment"] for r in mine})},
        }
    segments = {}
    for seg in sorted({r["segment"] for r in runs}):
        segments[seg] = gate_segment(seg, [r for r in runs if r["arm"] == "main" and r["segment"] == seg],
                                     [r for r in runs if r["arm"] == "candidate" and r["segment"] == seg],
                                     thresholds)
    verdict = "pass" if all(s["non_inferior"] for s in segments.values()) else "fail"
    return {
        "schema_version": SCHEMA_VERSION,
        "corpus_sha256": digest(corpus),
        "thresholds_sha256": digest(thresholds),
        "repetitions": int(repetitions if repetitions is not None else corpus.get("repetitions", 1)),
        "recorded_attempts": {arm: len((recorded or {}).get(arm) or []) for arm in ARMS},
        "arms": arms,
        "gate": {
            "verdict": verdict,
            "rule": "non-inferiority passes only when minimum_sample, regression_margin and under_routing_limit "
                    "pass in every segment; inconclusive counts as fail",
            "auto_route_segments": sorted(s for s, v in segments.items() if v["auto_route_eligible"]),
            "segments": segments,
        },
    }


# ---------------------------------------------------------------- report

def _f(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:,.4f}".rstrip("0").rstrip(".")
    return f"{value:,}" if isinstance(value, int) else str(value)


def render(card: dict[str, Any]) -> str:
    lines = [BEGIN, "",
             f"- Corpus sha256: `{card['corpus_sha256']}`",
             f"- Thresholds sha256: `{card['thresholds_sha256']}`",
             f"- Repetitions per case: {card['repetitions']}; recorded attempts: "
             + ", ".join(f"{a}={n}" for a, n in card["recorded_attempts"].items()),
             f"- **Gate verdict: {card['gate']['verdict'].upper()}**; auto-route eligible segments: "
             + (", ".join(card["gate"]["auto_route_segments"]) or "none"), ""]
    lines += ["### Quality and economy by category", "",
              "| Category | Arm | Cases | Validated rate | First-attempt | Attempts/validated | "
              "In+out tokens/validated | Cached/validated | Cache-write/validated | Latency p95 s | Floor violations |",
              "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    cats = sorted(set(card["arms"]["main"]["by_category"]) | set(card["arms"]["candidate"]["by_category"]))
    for cat in [*cats, "overall"]:
        for arm in ARMS:
            m = card["arms"][arm]["overall"] if cat == "overall" else card["arms"][arm]["by_category"].get(cat)
            if not m:
                continue
            cost = m["cost_per_validated_result"]
            lines.append(f"| {cat} | {arm} | {m['cases']} | {_f(m['validated_success_rate'])} | "
                         f"{_f(m['first_attempt_validated_success'])} | {_f(m['attempts_per_validated'])} | "
                         f"{_f(cost['io_tokens'])} | {_f(cost['cached_tokens'])} | "
                         f"{_f(cost['cache_write_tokens'])} | {_f(m['latency_p95'])} | {m['floor_violations']} |")
    lines += ["", "### Cost by worker kind (overall totals)", "",
              "| Arm | Kind | Attempts | Input | Cached | Cache-write | Output | Credits | USD |",
              "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for arm in ARMS:
        for kind, row in card["arms"][arm]["overall"]["cost_by_kind"].items():
            lines.append(f"| {arm} | {kind} | {row['attempts']} | {_f(row['input_tokens'])} | "
                         f"{_f(row['cached_tokens'])} | {_f(row['cache_write_tokens'])} | "
                         f"{_f(row['output_tokens'])} | {_f(row['credits'])} | {_f(row['usd'])} |")
    lines += ["", "### Gate by segment", "",
              "| Segment | Minimum sample | Regression margin (lower bound) | Under-routing | Material gain | "
              "Safe | Non-inferior | Auto-route |",
              "|---|---|---|---|---|---|---|---|"]
    for seg, g in card["gate"]["segments"].items():
        ch = g["checks"]
        reg = ch["regression_margin"]
        reg_text = reg["status"] + (f" ({_f(reg['validated_lower_bound'])})" if "validated_lower_bound" in reg else "")
        under = ch["under_routing_limit"]
        gain = ch["material_gain"]
        gain_units = ", ".join(gain["reduction_units"]) or "none"
        if gain["shifted_units"]:
            gain_units += "; shifted " + ", ".join(gain["shifted_units"])
        lines.append(f"| {seg} | {ch['minimum_sample']['status']} | {reg_text} | {under['status']} "
                     f"({under['floor_violations']} floor) | {gain['status']} ({gain_units}) | "
                     f"{'yes' if g['safe_segment'] else 'no'} | {'yes' if g['non_inferior'] else 'no'} | "
                     f"{'yes' if g['auto_route_eligible'] else 'no'} |")
    lines += ["", END]
    return "\n".join(lines)


def splice(document: str, block: str) -> str:
    if BEGIN not in document or END not in document:
        raise ValueError("report markers missing")
    head, rest = document.split(BEGIN, 1)
    _, tail = rest.split(END, 1)
    return head + block + tail


# ---------------------------------------------------------------- cli

def _inputs(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any], dict[str, list[dict[str, Any]]]]:
    telemetry, _ = _scripts()
    repo = Path(args.repo_root).resolve()
    corpus = _load(repo / args.corpus)
    errors = validate_corpus(corpus)
    if errors:
        raise SystemExit("invalid corpus: " + "; ".join(errors))
    thresholds = _load(repo / corpus["thresholds"])
    recorded: dict[str, list[dict[str, Any]]] = {}
    for item in args.telemetry or []:
        arm, _, path = item.partition("=")
        if arm not in ARMS or not path:
            raise SystemExit(f"--telemetry expects ARM=PATH with ARM in {ARMS}: {item}")
        recorded.setdefault(arm, []).extend(telemetry.read_records(Path(path)))
    return corpus, thresholds, recorded


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("run", "report"):
        p = sub.add_parser(name)
        p.add_argument("--repo-root", default=str(ROOT))
        p.add_argument("--corpus", default=CORPUS_PATH)
        p.add_argument("--repetitions", type=int)
        p.add_argument("--telemetry", action="append", metavar="ARM=PATH",
                       help="recorded PAT003 attempts.jsonl from real runs for main or candidate")
        p.add_argument("--recorded-segment", default="guarded")
        if name == "report":
            p.add_argument("--report", default=REPORT_PATH)
            p.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    corpus, thresholds, recorded = _inputs(args)
    card = scorecard(corpus, thresholds, args.repetitions, recorded, args.recorded_segment)
    if args.command == "run":
        sys.stdout.write(json.dumps(card, sort_keys=True, indent=2) + "\n")
        return 0
    path = Path(args.repo_root).resolve() / args.report
    current = path.read_text(encoding="utf-8")
    updated = splice(current, render(card))
    if args.check:
        if updated != current:
            print(f"{args.report} is stale; run: python tools/skill_benchmark.py report", file=sys.stderr)
            return 1
        print(f"{args.report} matches the scorecard (verdict {card['gate']['verdict']})")
        return 0
    path.write_text(updated, encoding="utf-8", newline="\n")
    print(f"wrote {args.report} (verdict {card['gate']['verdict']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
