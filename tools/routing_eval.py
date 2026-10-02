#!/usr/bin/env python3
"""Predeclared routing-eval thresholds and corpus manifest guard.

validate-predeclaration: check schema, conservative bounds, deterministic floors,
                         PAT003 metric fields, pinned digests and the measurement
                         ledger; any edit after a recorded measurement fails.
record-measurement:      append the current digests for a measurement run (the
                         lock); it does not run measurements.
digest:                  print the current digests.
seal:                    before any measurement only, pin the corpus manifest
                         digest inside thresholds.json.
shadow:                  replay the shadow corpus (corpus/cases.json plus
                         corpus/telemetry/<arm>.jsonl) through the runner's
                         route and shadow functions and write a deterministic
                         report; --check diffs it against the committed one.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skill" / "plan-and-execute" / "scripts"
DEFAULT_DIR = "docs/research/routing-eval"
THRESHOLDS = "thresholds.json"
MANIFEST = "corpus-manifest.json"
PREDECLARATION = "PREDECLARATION.md"
LEDGER = "measurements.jsonl"
MANIFEST_PATH = f"{DEFAULT_DIR}/{MANIFEST}"
LEDGER_PATH = f"{DEFAULT_DIR}/{LEDGER}"
SCHEMA_VERSION = 1
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RUN_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
REQUIRED_THRESHOLDS = ("regression_margin", "under_routing_limit", "material_gain", "minimum_sample", "safe_segments")
TEXT_FIELDS = ("unit", "rule", "rationale", "why_conservative")
# Request §62 workload classes plus TODO-017 scope; the corpus must cover all of them.
REQUIRED_CATEGORIES = (
    "mechanical", "bounded_implementation", "subtle_debugging", "architecture", "security_concurrency_migration",
    "weak_validation", "strong_validation", "long_horizon", "vision_ui", "quota_provider_failures",
    "direct_vs_orchestrated", "large_request", "stall_resource_failures",
)
ORIGINS = ("real", "synthetic", "mixed")
NEVER_SAFE = ("floor_locked", "resilience")


class PredeclarationError(Exception):
    pass


def _scripts() -> tuple[Any, Any]:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    import routing_telemetry
    import routingctl
    return routing_telemetry, routingctl


def canonical_digest(data: Any) -> str:
    text = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _load(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise PredeclarationError(f"{path.name}: missing")
    except ValueError as exc:
        raise PredeclarationError(f"{path.name}: invalid JSON ({exc})")


def read_ledger(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    entries: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except ValueError:
            raise PredeclarationError(f"{LEDGER}:{number}: invalid JSON")
        if not isinstance(item, dict):
            raise PredeclarationError(f"{LEDGER}:{number}: entry must be an object")
        entries.append(item)
    return entries


def _text(errors: list[str], where: str, value: Any) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{where}: non-empty text required")


def _number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def check_manifest(manifest: Any, errors: list[str]) -> set[str]:
    _, routingctl = _scripts()
    if not isinstance(manifest, dict) or manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{MANIFEST}: schema_version must be {SCHEMA_VERSION}")
        return set()
    segments = manifest.get("segments")
    if not isinstance(segments, dict) or not segments:
        errors.append(f"{MANIFEST}.segments: non-empty object required")
        segments = {}
    for name, description in segments.items():
        _text(errors, f"{MANIFEST}.segments.{name}", description)
    categories = manifest.get("categories")
    if not isinstance(categories, list) or not categories:
        errors.append(f"{MANIFEST}.categories: non-empty list required")
        return set(segments)
    seen_ids: set[str] = set()
    names: set[str] = set()
    for index, category in enumerate(categories):
        where = f"{MANIFEST}.categories[{index}]"
        if not isinstance(category, dict):
            errors.append(f"{where}: object required")
            continue
        cid, name = category.get("id"), category.get("name")
        if not isinstance(cid, str) or cid in seen_ids:
            errors.append(f"{where}.id: unique id required")
        seen_ids.add(str(cid))
        names.add(str(name))
        _text(errors, f"{where}.source", category.get("source"))
        if category.get("segment") not in segments:
            errors.append(f"{where}.segment: must name a declared segment")
        if category.get("origin") not in ORIGINS:
            errors.append(f"{where}.origin: one of {', '.join(ORIGINS)}")
        floor = category.get("floor_source")
        if not isinstance(floor, dict) or floor.get("kind") != "routingctl.minimum_route":
            errors.append(f"{where}.floor_source: kind routingctl.minimum_route required")
            continue
        try:
            actual = routingctl.minimum_route(list(floor.get("signals") or []))
        except Exception as exc:  # noqa: BLE001 - report any routing rejection as a schema error
            errors.append(f"{where}.floor_source.signals: {exc}")
            continue
        if floor.get("expected_floor") != actual:
            errors.append(f"{where}.floor_source.expected_floor: {floor.get('expected_floor')} != minimum_route {actual}")
    missing = [name for name in REQUIRED_CATEGORIES if name not in names]
    if missing:
        errors.append(f"{MANIFEST}.categories: missing {', '.join(missing)}")
    return set(segments)


def _bound(errors: list[str], where: str, value: Any, low: float, high: float) -> None:
    if not _number(value) or not low <= value <= high:
        errors.append(f"{where}: must be a number in [{low}, {high}]")


def check_thresholds(thresholds: Any, segments: set[str], manifest_digest: str, errors: list[str]) -> None:
    routing_telemetry, _ = _scripts()
    if not isinstance(thresholds, dict) or thresholds.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{THRESHOLDS}: schema_version must be {SCHEMA_VERSION}")
        return
    if not DATE_RE.match(str(thresholds.get("predeclared_on", ""))):
        errors.append(f"{THRESHOLDS}.predeclared_on: YYYY-MM-DD required")
    contract = thresholds.get("telemetry_contract") or {}
    if contract.get("pattern") != "PAT003" or contract.get("revision") != 1:
        errors.append(f"{THRESHOLDS}.telemetry_contract: PAT003 revision 1 required")
    pinned = thresholds.get("corpus_manifest") or {}
    if pinned.get("path") != MANIFEST_PATH:
        errors.append(f"{THRESHOLDS}.corpus_manifest.path: must be {MANIFEST_PATH}")
    if pinned.get("sha256") != manifest_digest:
        errors.append(f"{THRESHOLDS}.corpus_manifest.sha256: does not match {MANIFEST} digest {manifest_digest}")
    if thresholds.get("measurement_ledger") != LEDGER_PATH:
        errors.append(f"{THRESHOLDS}.measurement_ledger: must be {LEDGER_PATH}")
    _text(errors, f"{THRESHOLDS}.decision_rule", thresholds.get("decision_rule"))
    metrics = thresholds.get("metrics")
    if not isinstance(metrics, dict) or not metrics:
        errors.append(f"{THRESHOLDS}.metrics: non-empty object required")
        metrics = {}
    known = set(routing_telemetry.RECORD_FIELDS)
    for name, metric in metrics.items():
        fields = metric.get("fields") if isinstance(metric, dict) else None
        if not isinstance(fields, list) or not fields:
            errors.append(f"{THRESHOLDS}.metrics.{name}.fields: non-empty list required")
            continue
        unknown = [field for field in fields if field not in known]
        if unknown:
            errors.append(f"{THRESHOLDS}.metrics.{name}.fields: not PAT003 telemetry fields: {', '.join(map(str, unknown))}")
        _text(errors, f"{THRESHOLDS}.metrics.{name}.definition", metric.get("definition"))
    table = thresholds.get("thresholds")
    if not isinstance(table, dict):
        errors.append(f"{THRESHOLDS}.thresholds: object required")
        return
    for name in REQUIRED_THRESHOLDS:
        entry = table.get(name)
        where = f"{THRESHOLDS}.thresholds.{name}"
        if not isinstance(entry, dict):
            errors.append(f"{where}: missing")
            continue
        for field in TEXT_FIELDS:
            _text(errors, f"{where}.{field}", entry.get(field))
        if "metric" in entry and entry["metric"] not in metrics:
            errors.append(f"{where}.metric: must name a declared metric")
    # Guard rails: loosening past these bounds needs a code change, not a data edit.
    regression = table.get("regression_margin") or {}
    _bound(errors, f"{THRESHOLDS}.thresholds.regression_margin.value", regression.get("value"), 0.0, 0.05)
    under = (table.get("under_routing_limit") or {}).get("value") or {}
    if under.get("floor_violation_max_count") != 0:
        errors.append(f"{THRESHOLDS}.thresholds.under_routing_limit.value.floor_violation_max_count: must be 0")
    _bound(errors, f"{THRESHOLDS}.thresholds.under_routing_limit.value.attributed_failure_max_rate", under.get("attributed_failure_max_rate"), 0.0, 0.05)
    _bound(errors, f"{THRESHOLDS}.thresholds.under_routing_limit.value.attributed_failure_upper_bound_max", under.get("attributed_failure_upper_bound_max"), 0.0, 0.10)
    _bound(errors, f"{THRESHOLDS}.thresholds.material_gain.value", (table.get("material_gain") or {}).get("value"), 0.10, 0.90)
    sample = (table.get("minimum_sample") or {}).get("value") or {}
    for field, low in (("validated_attempts_per_segment_per_arm", 20), ("cases_per_category", 3), ("repetitions_per_case", 2)):
        value = sample.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value < low:
            errors.append(f"{THRESHOLDS}.thresholds.minimum_sample.value.{field}: integer >= {low} required")
    safe = (table.get("safe_segments") or {}).get("value")
    if not isinstance(safe, list) or not safe:
        errors.append(f"{THRESHOLDS}.thresholds.safe_segments.value: non-empty list required")
    else:
        for segment in safe:
            if segment not in segments:
                errors.append(f"{THRESHOLDS}.thresholds.safe_segments.value: unknown segment {segment}")
            elif segment in NEVER_SAFE:
                errors.append(f"{THRESHOLDS}.thresholds.safe_segments.value: {segment} can never be safe")


def evaluate(directory: Path) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    manifest = _load(directory / MANIFEST)
    thresholds = _load(directory / THRESHOLDS)
    digests = {"thresholds_sha256": canonical_digest(thresholds), "corpus_manifest_sha256": canonical_digest(manifest)}
    segments = check_manifest(manifest, errors)
    check_thresholds(thresholds, segments, digests["corpus_manifest_sha256"], errors)
    doc = directory / PREDECLARATION
    text = doc.read_text(encoding="utf-8") if doc.is_file() else ""
    if not text:
        errors.append(f"{PREDECLARATION}: missing")
    for key, value in digests.items():
        if text and f"`{value}`" not in text:
            errors.append(f"{PREDECLARATION}: does not record current {key} `{value}`")
    for number, entry in enumerate(read_ledger(directory / LEDGER), start=1):
        run = entry.get("run_id", f"#{number}")
        for key, value in digests.items():
            if entry.get(key) != value:
                errors.append(f"{LEDGER}: {key} changed after measurement run {run} ({entry.get(key)} -> {value})")
    return digests, errors


def _directory(args: argparse.Namespace) -> Path:
    return (Path(args.repo_root).resolve() / args.dir).resolve()


def cmd_validate(args: argparse.Namespace) -> int:
    digests, errors = evaluate(_directory(args))
    if errors:
        for error in errors:
            print(f"ERROR {error}", file=sys.stderr)
        print(f"predeclaration invalid: {len(errors)} error(s)", file=sys.stderr)
        return 1
    print(f"thresholds_sha256={digests['thresholds_sha256']}")
    print(f"corpus_manifest_sha256={digests['corpus_manifest_sha256']}")
    return 0


def cmd_digest(args: argparse.Namespace) -> int:
    directory = _directory(args)
    print(f"thresholds_sha256={canonical_digest(_load(directory / THRESHOLDS))}")
    print(f"corpus_manifest_sha256={canonical_digest(_load(directory / MANIFEST))}")
    return 0


def cmd_seal(args: argparse.Namespace) -> int:
    directory = _directory(args)
    if read_ledger(directory / LEDGER):
        print(f"refused: {LEDGER} already records a measurement; thresholds are frozen", file=sys.stderr)
        return 1
    path = directory / THRESHOLDS
    raw = path.read_text(encoding="utf-8")
    old = (json.loads(raw).get("corpus_manifest") or {}).get("sha256")
    new = canonical_digest(_load(directory / MANIFEST))
    if not isinstance(old, str) or raw.count(f'"{old}"') != 1:
        print("refused: corpus_manifest.sha256 must appear exactly once in thresholds.json", file=sys.stderr)
        return 1
    path.write_text(raw.replace(f'"{old}"', f'"{new}"'), encoding="utf-8", newline="")
    return cmd_digest(args)


def cmd_record(args: argparse.Namespace) -> int:
    if not RUN_ID_RE.match(args.run_id):
        print("run id must match [A-Za-z0-9._-]{1,64}", file=sys.stderr)
        return 2
    directory = _directory(args)
    digests, errors = evaluate(directory)
    if errors:
        for error in errors:
            print(f"ERROR {error}", file=sys.stderr)
        print("refused: predeclaration must validate before a measurement is recorded", file=sys.stderr)
        return 1
    ledger = directory / LEDGER
    if any(entry.get("run_id") == args.run_id for entry in read_ledger(ledger)):
        print(f"refused: run id {args.run_id} already recorded", file=sys.stderr)
        return 1
    entry = {"run_id": args.run_id, "recorded_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), **digests}
    with ledger.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")
    print(f"recorded run {args.run_id} thresholds_sha256={digests['thresholds_sha256']}")
    return 0


# --- Shadow evaluation (TODO 022) -------------------------------------------
# Every number in the report comes from corpus fixtures, the recorded fixture
# telemetry and the pure runner/selector functions: no clock, network, provider
# run or host state reaches the output, so regeneration is byte-identical.
CORPUS_CASES = "corpus/cases.json"
TELEMETRY_DIR = "corpus/telemetry"
SHADOW_REPORT = "SHADOW_REPORT.md"
POLICY_ARMS = ("main", "candidate")
CACHE_ARMS = ("cold", "warm")
SHADOW_PROMPT = "shadow-eval fixture prompt"


def _runner() -> tuple[Any, Any, Any, Any]:
    _scripts()
    import planctl
    import routing_config
    import routing_telemetry
    import run_isolated
    return run_isolated, planctl, routing_config, routing_telemetry


def route_verdict(route: dict[str, Any] | None, minimum: dict[str, str]) -> str:
    """under / exact / over against a case minimum acceptable route; tier decides before effort."""
    _, routingctl = _scripts()
    if not route:
        return "none"
    tier = routingctl.TIER_ORDER.index(routingctl.normalize_tier(route["tier"]))
    floor = routingctl.TIER_ORDER.index(minimum["tier"])
    if tier != floor:
        return "under" if tier < floor else "over"
    effort = routingctl.EFFORT_ORDER.index(route["effort"])
    wanted = routingctl.EFFORT_ORDER.index(minimum["effort"])
    return "exact" if effort == wanted else ("under" if effort < wanted else "over")


def case_config(case: dict[str, Any]) -> dict[str, Any]:
    _, planctl, routing_config, _ = _runner()
    config = routing_config.merge(routing_config.merge(planctl.default_config(), routing_config.EXTRA_DEFAULTS),
                                  case.get("config") or {})
    routing_config.validate(config)
    return config


def evaluate_shadow_case(case: dict[str, Any]) -> dict[str, Any]:
    """Main route, shadow candidate and argv with shadow off/on for one corpus case."""
    import copy
    import tempfile

    run_isolated, _, _, _ = _runner()
    config = case_config(case)
    task = {**case["task"], "id": case["id"], "routing_signals": list(case["signals"])}
    main = run_isolated.choose_route(task, config, None, check_availability=False)
    frozen = copy.deepcopy(main)
    shadow_config = {**config, "routing_shadow": True}
    shadow = run_isolated.shadow_candidate(task, main, shadow_config) if run_isolated.shadow_enabled(shadow_config) else None
    with tempfile.TemporaryDirectory(prefix="se-") as tmp:
        result = Path(tmp) / "r.json"
        argv_off = run_isolated.build_worker_command(main["provider"], main, config, SHADOW_PROMPT, result)
        argv_on = run_isolated.build_worker_command(main["provider"], main, shadow_config, SHADOW_PROMPT, result)
    minimum = case["minimum_acceptable_route"]
    candidate = (shadow or {}).get("candidate")
    return {
        "case": case, "main": main, "shadow": shadow, "candidate": candidate,
        "argv_equal": argv_off == argv_on and main == frozen,
        "main_verdict": route_verdict(main, minimum), "candidate_verdict": route_verdict(candidate, minimum),
    }


def _read_arm(directory: Path, arm: str) -> list[dict[str, Any]]:
    _, _, _, routing_telemetry = _runner()
    path = directory / TELEMETRY_DIR / f"{arm}.jsonl"
    if not path.is_file():
        raise PredeclarationError(f"{TELEMETRY_DIR}/{arm}.jsonl: missing")
    records = routing_telemetry.read_records(path)
    for number, record in enumerate(records, start=1):
        if set(record) != set(routing_telemetry.RECORD_FIELDS):
            raise PredeclarationError(f"{TELEMETRY_DIR}/{arm}.jsonl:{number}: fields must be exactly the PAT003 record fields")
    return records


def _fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.6f}".rstrip("0").rstrip(".")
    return str(value)


def _route_text(route: dict[str, Any] | None) -> str:
    return "none" if not route else f"{route['provider']}/{route['model']}@{route['tier']}/{route['effort']}"


def _final_pass(records: list[dict[str, Any]]) -> bool | None:
    if not records:
        return None
    return max(records, key=lambda r: (r.get("retry_count") or 0)).get("validation_pass") is True


def shadow_report(directory: Path) -> str:
    _, _, _, routing_telemetry = _runner()
    manifest = _load(directory / MANIFEST)
    thresholds = _load(directory / THRESHOLDS)
    corpus = _load(directory / CORPUS_CASES)
    arms = {arm: _read_arm(directory, arm) for arm in (*POLICY_ARMS, *CACHE_ARMS)}
    segment_of = {c["name"]: c["segment"] for c in manifest["categories"]}
    table = thresholds["thresholds"]
    under_limit = table["under_routing_limit"]["value"]
    minimum_sample = table["minimum_sample"]["value"]["validated_attempts_per_segment_per_arm"]
    safe = set(table["safe_segments"]["value"])

    results = []
    for case in corpus["cases"]:
        if case.get("category") not in segment_of:
            raise PredeclarationError(f"{CORPUS_CASES}: case {case.get('id')} names unknown category {case.get('category')}")
        results.append(evaluate_shadow_case(case))
    segment_cases = {name: [r for r in results if segment_of[r["case"]["category"]] == name] for name in manifest["segments"]}
    case_segment = {r["case"]["id"]: segment_of[r["case"]["category"]] for r in results}

    def arm_records(arm: str, segment: str | None = None) -> list[dict[str, Any]]:
        return [r for r in arms[arm] if segment is None or case_segment.get(str(r.get("task_id"))) == segment]

    inputs = {
        CORPUS_CASES: canonical_digest(corpus),
        MANIFEST: canonical_digest(manifest),
        THRESHOLDS: canonical_digest(thresholds),
        **{f"{TELEMETRY_DIR}/{arm}.jsonl": canonical_digest(records) for arm, records in arms.items()},
    }
    catalog_versions = sorted({str((r["shadow"] or {}).get("explanation", {}).get("catalog_version")) for r in results})
    lines = [
        "# Shadow routing evaluation report",
        "",
        "Generated by `python tools/routing_eval.py shadow`; do not edit by hand. Every number is computed from the",
        "corpus fixtures and the recorded fixture telemetry below (synthetic, no live provider runs). Artifact owner:",
        "project-shared; retention: keep, regenerated in place (PAT004). Telemetry units are native (PAT003).",
        "",
        "## Inputs",
        "",
        "| Input | Canonical sha256 |",
        "|---|---|",
        *[f"| `{name}` | `{digest}` |" for name, digest in inputs.items()],
        "",
        f"Selector catalog: `{', '.join(catalog_versions)}`.",
        "",
        "## Execution invariance",
        "",
        f"- Cases: {len(results)}; executed argv identical with shadow off and on: "
        f"{sum(1 for r in results if r['argv_equal'])}/{len(results)}.",
        f"- Shadow candidates recorded: {sum(1 for r in results if r['candidate'])}/{len(results)}; "
        f"selector errors: {sum(1 for r in results if (r['shadow'] or {}).get('decision') == 'error')}.",
        "",
        "## Under- and over-routing per segment",
        "",
        "Verdicts compare each route with the case minimum acceptable route (`routingctl.minimum_route`). The gate is",
        f"`under_routing_limit.floor_violation_max_count` = {under_limit['floor_violation_max_count']} candidate floor violations per segment.",
        "",
        "| Segment | Cases | Main under | Main over | Candidate under | Candidate over | Floor violations vs limit | Safe segment |",
        "|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for segment, rows in segment_cases.items():
        count = lambda key, verdict: sum(1 for r in rows if r[key] == verdict)  # noqa: E731
        violations = count("candidate_verdict", "under")
        gate = "pass" if violations <= under_limit["floor_violation_max_count"] else "FAIL"
        lines.append(
            f"| {segment} | {len(rows)} | {count('main_verdict', 'under')} | {count('main_verdict', 'over')} | "
            f"{violations} | {count('candidate_verdict', 'over')} | {violations} / {under_limit['floor_violation_max_count']} {gate} | "
            f"{'yes' if segment in safe else 'no'} |"
        )
    lines += [
        "",
        "## Failure-attributed under-routing and sample sufficiency",
        "",
        f"Attributed failure: main validated and the candidate did not while routed below main. Limit "
        f"{_fmt(under_limit['attributed_failure_max_rate'])}; a segment with fewer than {minimum_sample} validated attempts",
        "per arm is inconclusive and cannot pass any gate (`minimum_sample`).",
        "",
        "| Segment | Validated main | Validated candidate | Attributed failures | Rate | Sample |",
        "|---|---:|---:|---:|---:|---|",
    ]
    _, routingctl = _scripts()

    def rank(route: dict[str, Any] | None) -> tuple[int, int]:
        if not route:
            return (-1, -1)
        return (routingctl.TIER_ORDER.index(routingctl.normalize_tier(route["tier"])), routingctl.EFFORT_ORDER.index(route["effort"]))

    for segment, rows in segment_cases.items():
        validated = {arm: sum(1 for r in arm_records(arm, segment) if r.get("validation_pass") is True) for arm in POLICY_ARMS}
        attributed = 0
        for r in rows:
            cid = r["case"]["id"]
            main_pass = _final_pass([x for x in arms["main"] if x.get("task_id") == cid])
            cand_pass = _final_pass([x for x in arms["candidate"] if x.get("task_id") == cid])
            if main_pass and cand_pass is False and rank(r["candidate"]) < rank(r["main"]):
                attributed += 1
        rate = attributed / len(rows) if rows else None
        enough = rows and all(value >= minimum_sample for value in validated.values())
        lines.append(f"| {segment} | {validated['main']} | {validated['candidate']} | {attributed} | {_fmt(None if rate is None else round(rate, 6))} | "
                     f"{'sufficient' if enough else 'inconclusive'} |")

    def cost_rows(arm_names: tuple[str, ...]) -> list[str]:
        out = []
        for segment in segment_cases:
            for arm in arm_names:
                rollup = routing_telemetry.rollup(arm_records(arm, segment))
                totals, per = rollup["totals"], rollup["per_validated_result"]
                tokens = None
                if per["input_tokens"] is not None and per["output_tokens"] is not None:
                    tokens = round(per["input_tokens"] + per["output_tokens"], 6)
                out.append(f"| {segment} | {arm} | {totals['attempts']} | {totals['validated']} | {_fmt(tokens)} | "
                           f"{_fmt(per['cached_tokens'])} | {_fmt(per['cache_write_tokens'])} | {_fmt(per['credits'])} | "
                           f"{_fmt(per['usd'])} | {_fmt(per['latency_seconds'])} |")
        return out

    header = ["| Segment | Arm | Attempts | Validated | input+output tokens | cached tokens | cache-write tokens | credits | usd | latency s |",
              "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    gain = table["material_gain"]["value"]
    lines += [
        "",
        "## Cost model: cost per validated result",
        "",
        "`routing_telemetry.rollup` per validated result over every worker kind (root, retry, subagent, diagnostic,",
        f"summary). `material_gain` needs a >= {_fmt(gain)} relative reduction in one native unit; no USD conversion.",
        "",
        *header,
        *cost_rows(POLICY_ARMS),
        "",
        "## Cache impact",
        "",
        "Matched cold and warm runs of the main route; cached and cache-write tokens are reported natively.",
        "",
        *header,
        *cost_rows(CACHE_ARMS),
        "",
        "## Cases",
        "",
        "| Case | Category | Segment | Provider fixture | Minimum | Main route | Main | Candidate route | Candidate | Selector explanation |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        case, shadow = r["case"], r["shadow"] or {}
        explanation = shadow.get("explanation") or {}
        minimum = case["minimum_acceptable_route"]
        why = f"{shadow.get('decision')}; target {explanation.get('target_tier')}; lifted {explanation.get('tier_lifted')}; providers {','.join(explanation.get('providers') or [])}"
        lines.append(
            f"| {case['id']} | {case['category']} | {case_segment[case['id']]} | {case.get('provider_fixture', 'default')} | "
            f"{minimum['tier']}/{minimum['effort']} | {_route_text(r['main'])} | {r['main_verdict']} | "
            f"{_route_text(r['candidate'])} | {r['candidate_verdict']} | {why} |"
        )
    return "\n".join(lines) + "\n"


def cmd_shadow(args: argparse.Namespace) -> int:
    directory = _directory(args)
    text = shadow_report(directory)
    target = Path(args.out).resolve() if args.out else directory / SHADOW_REPORT
    if args.check:
        current = target.read_text(encoding="utf-8").replace("\r\n", "\n") if target.is_file() else None
        if current != text:
            print(f"{target.name}: stale; regenerate with `python tools/routing_eval.py shadow`", file=sys.stderr)
            return 1
        print(f"{target.name}: up to date")
        return 0
    target.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {target.name} sha256={hashlib.sha256(text.encode('utf-8')).hexdigest()}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--dir", default=DEFAULT_DIR, help="routing-eval directory relative to the repo root")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate-predeclaration").set_defaults(func=cmd_validate)
    sub.add_parser("digest").set_defaults(func=cmd_digest)
    sub.add_parser("seal").set_defaults(func=cmd_seal)
    record = sub.add_parser("record-measurement")
    record.add_argument("--run-id", required=True)
    record.set_defaults(func=cmd_record)
    shadow = sub.add_parser("shadow")
    shadow.add_argument("--out", help="report path (default: <dir>/SHADOW_REPORT.md)")
    shadow.add_argument("--check", action="store_true", help="fail when the report differs from a regeneration")
    shadow.set_defaults(func=cmd_shadow)
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except PredeclarationError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
