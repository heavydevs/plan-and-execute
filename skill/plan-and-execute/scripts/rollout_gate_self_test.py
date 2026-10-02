#!/usr/bin/env python3
"""Conservative auto-routing rollout gate: per-segment gate verdicts and the opt-in runner mode.

A segment failing any gate is never auto-routed; a selector exception keeps the
ladder route and is recorded; default config routes exactly as before.
"""
from __future__ import annotations

import contextlib
import copy
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import planctl  # noqa: E402
import routing_config as cfg  # noqa: E402
import routingctl  # noqa: E402
import run_isolated as run  # noqa: E402
from self_test import sample_spec  # noqa: E402

EVAL_DIR = SCRIPTS.parents[2] / "docs" / "research" / "routing-eval"
SAFE = "deterministic_low_blast"
SIGNALS = ["mechanical_edit", "strong_validation"]
COST_HEADER = ("| Segment | Arm | Attempts | Validated | input+output tokens | cached tokens | cache-write tokens"
               " | credits | usd | latency s |")


def arm(attempts=200, validated=200, io_tokens=10000, cached=0, cache_write=4000, credits="n/a", latency=80):
    return {"attempts": attempts, "validated": validated, "io": io_tokens, "cached": cached,
            "cw": cache_write, "credits": credits, "latency": latency}


def segment(**overrides):
    item = {"cases": 9, "under": 0, "safe": "yes", "af": 0,
            "categories": ["mechanical"] * 3 + ["strong_validation"] * 3 + ["bounded_implementation"] * 3,
            "main": arm(), "candidate": arm(io_tokens=8000)}
    item.update(overrides)
    return item


def report(segments: dict, digest: str) -> str:
    lines = ["# Shadow routing evaluation report", "", "## Inputs", "", "| Input | Canonical sha256 |", "|---|---|",
             f"| `thresholds.json` | `{digest}` |", "", "## Under- and over-routing per segment", "",
             "| Segment | Cases | Main under | Main over | Candidate under | Candidate over | Floor violations vs limit | Safe segment |",
             "|---|---:|---:|---:|---:|---:|---|---|"]
    for name, item in segments.items():
        lines.append(f"| {name} | {item['cases']} | 0 | 0 | {item['under']} | 0 | {item['under']} / 0 | {item['safe']} |")
    lines += ["", "## Failure-attributed under-routing and sample sufficiency", "",
              "| Segment | Validated main | Validated candidate | Attributed failures | Rate | Sample |",
              "|---|---:|---:|---:|---:|---|"]
    for name, item in segments.items():
        lines.append(f"| {name} | {item['main']['validated']} | {item['candidate']['validated']} | {item['af']} | 0 | ok |")
    for title, arms in (("## Cost model: cost per validated result", ("main", "candidate")),
                        ("## Cache impact", ("cold", "warm"))):
        lines += ["", title, "", COST_HEADER, "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for name, item in segments.items():
            for key in arms:
                a = item.get(key) or arm(attempts=1, validated=1, io_tokens=1)  # cache rows must be ignored
                lines.append(f"| {name} | {key} | {a['attempts']} | {a['validated']} | {a['io']} | {a['cached']} | "
                             f"{a['cw']} | {a['credits']} | n/a | {a['latency']} |")
    lines += ["", "## Cases", "", "| Case | Category | Segment |", "|---|---|---|"]
    number = 0
    for name, item in segments.items():
        for category in item["categories"]:
            number += 1
            lines.append(f"| K{number:02d} | {category} | {name} |")
    return "\n".join(lines) + "\n"


class GateEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.thresholds = json.loads((EVAL_DIR / "thresholds.json").read_text(encoding="utf-8"))
        self.digest = routingctl.canonical_sha256(self.thresholds)

    def gate(self, segments, digest=None):
        return routingctl.evaluate_gate(self.thresholds, report(segments, digest or self.digest))

    def test_committed_report_records_empty_allowlist(self):
        gate = routingctl.load_gate(EVAL_DIR)
        self.assertIsNone(gate["error"])
        self.assertTrue(gate["fresh"])
        self.assertEqual(gate["allowlist"], [])
        self.assertEqual(set(gate["segments"]), {"deterministic_low_blast", "guarded", "floor_locked", "resilience"})
        safe = gate["segments"][SAFE]["gates"]
        self.assertFalse(safe["minimum_sample"]["pass"])
        self.assertFalse(safe["material_gain"]["pass"])
        self.assertTrue(safe["safe_segment"]["pass"])
        for name in ("guarded", "floor_locked", "resilience"):
            self.assertFalse(gate["segments"][name]["gates"]["safe_segment"]["pass"])

    def test_segment_passing_every_gate_is_allowlisted(self):
        gate = self.gate({SAFE: segment()})
        self.assertIsNone(gate["error"])
        self.assertEqual(gate["allowlist"], [SAFE], json.dumps(gate["segments"], indent=1))
        self.assertTrue(all(v["pass"] for v in gate["segments"][SAFE]["gates"].values()))
        self.assertEqual(gate, self.gate({SAFE: segment()}))  # deterministic

    def test_any_failed_gate_keeps_segment_out(self):
        variants = {
            "minimum_sample": segment(main=arm(attempts=20, validated=20), candidate=arm(attempts=20, validated=20, io_tokens=8000)),
            "minimum_sample ": segment(categories=["mechanical"] * 7 + ["bounded_implementation"] * 2),
            "regression_margin": segment(candidate=arm(validated=185, io_tokens=8000)),
            "under_routing_limit": segment(under=1),
            "under_routing_limit ": segment(af=5),
            "material_gain": segment(candidate=arm(io_tokens=9000)),
            "material_gain  ": segment(candidate=arm(io_tokens=8000, cached=500), main=arm(cached=100)),
            "material_gain   ": segment(candidate=arm(io_tokens=8000, latency=101)),
            "safe_segment": segment(safe="no"),
        }
        for gate_name, item in variants.items():
            gate = self.gate({SAFE: item})
            verdict = gate["segments"][SAFE]
            self.assertFalse(verdict["gates"][gate_name.strip()]["pass"], gate_name)
            self.assertFalse(verdict["pass"], gate_name)
            self.assertEqual(gate["allowlist"], [], gate_name)
        guarded = self.gate({"guarded": segment(), "floor_locked": segment()})
        self.assertEqual(guarded["allowlist"], [])
        self.assertFalse(guarded["segments"]["guarded"]["gates"]["safe_segment"]["pass"])

    def test_inconclusive_sample_fails_every_metric_gate(self):
        thin = segment(main=arm(attempts=20, validated=20), candidate=arm(attempts=20, validated=20, io_tokens=5000))
        gates = self.gate({SAFE: thin})["segments"][SAFE]["gates"]
        for name in ("minimum_sample", "regression_margin", "under_routing_limit", "material_gain"):
            self.assertFalse(gates[name]["pass"], name)

    def test_stale_or_broken_evidence_fails_closed(self):
        stale = self.gate({SAFE: segment()}, digest="0" * 64)
        self.assertFalse(stale["fresh"])
        self.assertEqual(stale["allowlist"], [])
        broken = routingctl.evaluate_gate(self.thresholds, "# empty report\n")
        self.assertIsNotNone(broken["error"])
        self.assertEqual((broken["segments"], broken["allowlist"]), ({}, []))
        bad = routingctl.evaluate_gate({**self.thresholds, "schema_version": 2}, report({SAFE: segment()}, self.digest))
        self.assertEqual(bad["allowlist"], [])
        missing = routingctl.load_gate(Path(tempfile.gettempdir()) / "no-such-gate-dir")
        self.assertEqual(missing["allowlist"], [])
        self.assertIsNotNone(missing["error"])

    def test_effective_allowlist_intersects_config_and_gate(self):
        gate = {"allowlist": [SAFE], "error": None}
        self.assertEqual(routingctl.effective_allowlist([SAFE, "guarded"], gate), [SAFE])
        self.assertEqual(routingctl.effective_allowlist(["guarded"], gate), [])
        self.assertEqual(routingctl.effective_allowlist([SAFE], {"allowlist": [SAFE], "error": "x"}), [])
        self.assertEqual(routingctl.effective_allowlist(None, gate), [])


class AutoSelectRunnerTests(unittest.TestCase):
    def setUp(self):
        # Short temp paths: LongPathsEnabled may be 0 on Windows hosts.
        self.tmp = Path(tempfile.mkdtemp(prefix="rg"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.repo = self.tmp / "r"
        self.repo.mkdir()
        spec = sample_spec()
        for task in spec["tasks"]:
            task["model_tier"], task["reasoning_effort"], task["provider"] = "standard", "medium", "auto"
        self.plan = planctl.create_plan(self.repo, spec, ".w", "p")
        _, self.manifest = planctl.load_plan(self.plan)
        self.config = cfg.merge(planctl.default_config(), cfg.EXTRA_DEFAULTS)
        for provider in cfg.PROVIDERS:
            self.config[provider]["command"] = [sys.executable]  # mocked resolution: no host CLI
        self.config["stream_provider_output"] = False
        thresholds = json.loads((EVAL_DIR / "thresholds.json").read_text(encoding="utf-8"))
        self.gate_dir = self.tmp / "g"
        self.gate_dir.mkdir()
        (self.gate_dir / "thresholds.json").write_text(json.dumps(thresholds), encoding="utf-8")
        segments = {SAFE: segment(), "guarded": segment(safe="no")}
        (self.gate_dir / "SHADOW_REPORT.md").write_text(
            report(segments, routingctl.canonical_sha256(thresholds)), encoding="utf-8")

    def task(self, **extra):
        return {**self.manifest["tasks"][0], "routing_signals": list(SIGNALS), "routing_segment": SAFE, **extra}

    def on(self, allowlist=(SAFE,), gate_dir=None):
        return {**copy.deepcopy(self.config),
                "routing": {"auto_select": "on", "allowlist": list(allowlist), "gate_dir": str(gate_dir or self.gate_dir)}}

    def ladder(self, task, config=None):
        return run.choose_route(task, config or self.config, None, check_availability=False)

    def auto(self, task, config):
        route = self.ladder(task, config)
        shadow = run.shadow_candidate(task, route, config)
        return route, run.auto_route(self.plan, self.repo, task, route, config, shadow)

    def preview(self, config, task):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            self.assertFalse(run.execute_one_task(self.plan, self.manifest, config, task,
                                                  provider_override=None, dry_run=True, no_wait=True))
        return json.loads(out.getvalue())

    def test_config_validation(self):
        for routing in ({"auto_select": "off"}, {"auto_select": "shadow", "allowlist": []},
                        {"auto_select": "on", "allowlist": [SAFE], "gate_dir": "docs/research/routing-eval"}):
            cfg.validate({**self.config, "routing": routing})
        for routing in ({"auto_select": "yes"}, {"auto_select": True}, {"allowlist": [SAFE, SAFE]},
                        {"allowlist": "deterministic_low_blast"}, {"allowlist": ["Bad Name"]}, {"gate_dir": ""},
                        {"enabled": True}, []):
            with self.assertRaises(cfg.ConfigError, msg=repr(routing)):
                cfg.validate({**self.config, "routing": routing})

    def test_default_config_routes_unchanged(self):
        task = self.task()
        self.assertEqual(run.auto_select_mode(self.config), "off")
        self.assertFalse(run.shadow_enabled(self.config))
        for config in (self.config, {**self.config, "routing": {"auto_select": "off", "allowlist": [SAFE]}}):
            preview = self.preview(config, task)
            self.assertEqual(preview["route"], self.ladder(task, config))
            self.assertNotIn("shadow", preview)
        shadow = self.preview({**self.config, "routing": {"auto_select": "shadow", "allowlist": [SAFE]}}, task)
        self.assertEqual(shadow["route"], self.ladder(task))
        self.assertNotIn("auto", shadow["shadow"])

    def test_gate_passing_allowlisted_segment_is_auto_routed(self):
        config = self.on()
        task = self.task()
        ladder, (route, decision) = self.auto(task, config)
        self.assertEqual((decision["applied"], decision["reason"], decision["allowlist"]), (True, "gate_passed", [SAFE]))
        self.assertEqual((route["provider"], route["tier"], route["effort"]), ("claude", "economy", "low"))
        self.assertEqual(route["model"], config["claude"]["models"]["economy"])
        self.assertNotEqual(route, ladder)
        preview = self.preview(config, task)
        self.assertEqual(preview["route"], route)
        self.assertEqual(preview["shadow"]["ladder"]["tier"], ladder["tier"])
        self.assertEqual(preview["shadow"]["executed"]["tier"], "economy")

    def test_failing_segments_are_never_auto_routed(self):
        cases = [
            (self.on(allowlist=[SAFE, "guarded"]), self.task(routing_segment="guarded"), "segment_not_allowlisted"),
            (self.on(allowlist=[]), self.task(), "segment_not_allowlisted"),
            (self.on(gate_dir=EVAL_DIR), self.task(), "segment_not_allowlisted"),  # committed report: nothing passes
            (self.on(gate_dir=self.tmp / "missing"), self.task(), "segment_not_allowlisted"),
            (self.on(), self.task(routing_segment=None), "segment_not_allowlisted"),
            (self.on(), self.task(attempts=1), "ladder_owns_retry"),
            (self.on(), self.task(functional_failures=1, failure_classes=["semantic"]), "ladder_owns_retry"),
        ]
        for config, task, reason in cases:
            ladder, (route, decision) = self.auto(task, config)
            self.assertEqual(route, ladder, reason)
            self.assertEqual((decision["applied"], decision["reason"]), (False, reason))
        config = self.on(allowlist=[SAFE, "guarded"])
        with mock.patch.object(routingctl, "load_gate", side_effect=AssertionError("gate must not be read")):
            route, decision = run.auto_route(self.plan, self.repo, self.task(), self.ladder(self.task()),
                                             {**config, "routing": {"auto_select": "on"}}, {"decision": "route"})
        self.assertEqual(decision["reason"], "segment_not_allowlisted")

    def test_selector_exception_falls_back_and_is_recorded(self):
        config = self.on()
        task = self.task()
        ladder = self.ladder(task, config)
        with mock.patch.object(routingctl, "select_route", side_effect=RuntimeError("boom")):
            preview = self.preview(config, task)
        self.assertEqual(preview["route"], ladder)
        self.assertEqual(preview["shadow"]["auto"]["reason"], "selector_error")
        self.assertEqual(preview["shadow"]["auto"]["error"], "RuntimeError")
        with mock.patch.object(routingctl, "load_gate", side_effect=OSError("disk")):
            route, decision = run.auto_route(self.plan, self.repo, task, ladder, config, {"decision": "route"})
        self.assertEqual((route, decision["reason"], decision["error"]), (ladder, "selector_error", "OSError"))

        calls = []

        def fake_process(command, *args, **kwargs):
            calls.append(command)
            return 1, "", "boom"

        with mock.patch.object(routingctl, "select_route", side_effect=RuntimeError("boom")), \
                mock.patch.object(run, "run_process", fake_process), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            run.execute_one_task(self.plan, self.manifest, config, task, provider_override=None, dry_run=False, no_wait=True)
        self.assertIn(ladder["model"], calls[0])
        records = [json.loads(line) for line in (self.plan / run.SHADOW_RELATIVE).read_text(encoding="utf-8").splitlines()]
        first = records[0]
        self.assertEqual((first["decision"], first["auto"]["applied"], first["auto"]["reason"]), ("error", False, "selector_error"))
        self.assertEqual(first["executed"], {key: ladder.get(key) for key in run.SHADOW_ROUTE_KEYS})


if __name__ == "__main__":
    unittest.main(verbosity=1)
