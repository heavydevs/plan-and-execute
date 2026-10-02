#!/usr/bin/env python3
"""Self-test for the shadow routing eval (TODO 022).

Regenerates SHADOW_REPORT.md twice and diffs it byte for byte against itself and
the committed report, proves shadow mode never changes the executed route or
argv for any corpus case, and checks the runner's shadow record stays plan
scoped. Works in temp directories only; committed files are never modified.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "routing_eval.py"
SOURCE = ROOT / "docs" / "research" / "routing-eval"
ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
FAILURES: list[str] = []
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "tools"))
import routing_eval  # noqa: E402

run_isolated, planctl, routing_config, _ = routing_eval._runner()


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOL), "--repo-root", str(ROOT), *args],
        cwd=str(ROOT), capture_output=True, text=True, env=ENV, timeout=120,
    )


def check(name: str, condition: bool, detail: str = "") -> None:
    print(f"{'PASS' if condition else 'FAIL'} {name}")
    if not condition:
        FAILURES.append(f"{name}: {detail[:400]}")


def test_report_reproducible() -> None:
    with tempfile.TemporaryDirectory(prefix="se-") as tmp:
        first, second = Path(tmp) / "a.md", Path(tmp) / "b.md"
        a, b = run("shadow", "--out", str(first)), run("shadow", "--out", str(second))
        check("shadow report generates", a.returncode == 0 and b.returncode == 0, a.stderr + b.stderr)
        if a.returncode or b.returncode:
            return
        check("regeneration is byte-identical", first.read_bytes() == second.read_bytes())
        committed = (SOURCE / routing_eval.SHADOW_REPORT).read_bytes().replace(b"\r\n", b"\n")
        check("committed SHADOW_REPORT.md matches regeneration", committed == first.read_bytes(),
              "regenerate with `python tools/routing_eval.py shadow`")
    result = run("shadow", "--check")
    check("shadow --check passes on committed report", result.returncode == 0, result.stderr)


def test_execution_invariance() -> None:
    cases = json.loads((SOURCE / routing_eval.CORPUS_CASES).read_text(encoding="utf-8"))["cases"]
    providers = {case.get("provider_fixture") for case in cases}
    check("corpus covers muse, glm and deepseek fixtures", {"muse", "glm", "deepseek"} <= providers, str(providers))
    for case in cases:
        result = routing_eval.evaluate_shadow_case(case)
        check(f"{case['id']} argv equal with shadow on/off", result["argv_equal"])
        check(f"{case['id']} candidate never below minimum", result["candidate_verdict"] != "under",
              routing_eval._route_text(result["candidate"]))


def test_report_lists_segments() -> None:
    text = routing_eval.shadow_report(SOURCE)
    manifest = json.loads((SOURCE / "corpus-manifest.json").read_text(encoding="utf-8"))
    for segment in manifest["segments"]:
        rows = [line for line in text.splitlines() if line.startswith(f"| {segment} | ") and line.endswith(("| yes |", "| no |"))]
        check(f"report lists under/over-routing for {segment}", len(rows) == 1, segment)
    check("report has no clock values", "recorded_at" not in text and "T00:" not in text)


def test_verdicts() -> None:
    minimum = {"tier": "standard", "effort": "medium"}
    route = lambda tier, effort: {"provider": "p", "model": "m", "tier": tier, "effort": effort}  # noqa: E731
    check("lower tier is under", routing_eval.route_verdict(route("economy", "xhigh"), minimum) == "under")
    check("same tier lower effort is under", routing_eval.route_verdict(route("standard", "low"), minimum) == "under")
    check("exact is exact", routing_eval.route_verdict(route("standard", "medium"), minimum) == "exact")
    check("higher tier is over", routing_eval.route_verdict(route("strong", "low"), minimum) == "over")
    check("missing candidate is none", routing_eval.route_verdict(None, minimum) == "none")


def test_runner_shadow_record() -> None:
    config = routing_config.merge(routing_config.merge(planctl.default_config(), routing_config.EXTRA_DEFAULTS), {})
    check("shadow is off by default", not run_isolated.shadow_enabled(config))
    task = {"id": "T1", "model_tier": "standard", "reasoning_effort": "medium"}
    route = run_isolated.choose_route(task, config, None, check_availability=False)
    broken = run_isolated.shadow_candidate({**task, "routing_signals": ["not_a_signal"]}, route, config)
    check("selector error is recorded, not raised", broken["decision"] == "error" and broken["candidate"] is None, str(broken))
    record = run_isolated.shadow_candidate(task, route, config)
    check("shadow record keeps executed route", record["executed"]["model"] == route["model"], str(record))
    forbidden = {"prompt", "stdout", "transcript", "code"}
    check("shadow record is metadata only", not forbidden & set(record), str(sorted(record)))
    with tempfile.TemporaryDirectory(prefix="se-") as tmp:
        plan = Path(tmp) / "plan"
        ok = run_isolated.record_shadow(plan, record)
        path = plan / run_isolated.SHADOW_RELATIVE
        check("shadow record lands in plan telemetry", ok and path.is_file(), str(path))
        check("shadow record is one JSON line", ok and len(path.read_text(encoding="utf-8").splitlines()) == 1)


def main() -> int:
    test_verdicts()
    test_runner_shadow_record()
    test_execution_invariance()
    test_report_lists_segments()
    test_report_reproducible()
    if FAILURES:
        print("\n".join(FAILURES), file=sys.stderr)
        print(f"routing eval shadow self-test: {len(FAILURES)} failure(s)", file=sys.stderr)
        return 1
    print("routing eval shadow self-test: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
