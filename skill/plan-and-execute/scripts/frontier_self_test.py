#!/usr/bin/env python3
"""Frontier level L6/F6 (Claude Fable 5.2 / GPT-6.2 Astra above `max`).

Owner policy 2026-11-20: reachable only for extreme architecture/code review on
read-only roles, or after Opus 5.5 / Sol 6.2 failed repeatedly at the max/xhigh
rung. Never through ordinary routes, floors, ladders or the selector; never on
availability or environment outcomes. Fake CLIs only: no model calls.
"""
from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import availability as av  # noqa: E402
import planctl  # noqa: E402
import routing_config as cfg  # noqa: E402
import routingctl  # noqa: E402
import run_isolated as run  # noqa: E402
import workload_routing  # noqa: E402
from self_test import sample_spec, write_fake_claude  # noqa: E402

FRONTIER = routingctl.frontier_model_ids()
ALL_CLASSES = list(routingctl.FAILURE_CLASSES)


def default_config() -> dict:
    config = cfg.merge(planctl.default_config(), cfg.EXTRA_DEFAULTS)
    config["stream_provider_output"] = False
    config["rate_limit"]["auto_wait"] = False
    config["claude"]["command"] = sys.executable
    config["codex"]["command"] = sys.executable
    return config


class PolicyTests(unittest.TestCase):
    def test_level_is_first_class_but_not_a_persisted_tier(self):
        self.assertEqual(routingctl.LEVEL_ORDER, [*routingctl.TIER_ORDER, "frontier"])
        self.assertEqual(routingctl.TIER_ORDER, ["economy", "standard", "advanced", "strong", "max"])
        for alias in ("L6", "f6", " F6 ", "frontier"):
            self.assertEqual(routingctl.normalize_level(alias), "frontier")
        self.assertEqual(routingctl.normalize_tier("F6"), "f6")  # tiers keep five levels
        self.assertEqual(routingctl.normalize_level("L5"), "max")
        self.assertNotIn("frontier", planctl.VALID_TIERS)
        self.assertEqual(FRONTIER, {"claude-fable-5-2", "gpt-6.2-astra"})
        self.assertEqual(routingctl.frontier_model("claude"), {"model": "claude-fable-5-2", "effort": "high"})
        self.assertEqual(routingctl.frontier_model("codex"), {"model": "gpt-6.2-astra", "effort": "high"})
        self.assertIsNone(routingctl.frontier_model("antigravity"))  # Carbon is never preset
        configured = routingctl.configure_config({})
        self.assertEqual(routingctl.level_map("codex", configured)["frontier"], "gpt-6.2-astra")
        self.assertEqual(configured["routing_policy"]["frontier"], {"enabled": True, "min_top_failures": 2})

    def test_frontier_never_selected_by_ordinary_routes(self):
        configured = routingctl.configure_config({})
        for provider in ("claude", "codex"):
            provider_cfg = configured[provider]
            self.assertFalse(set(provider_cfg["models"].values()) & FRONTIER)
            for tier in routingctl.LEVEL_ORDER:
                for effort in routingctl.EFFORT_ORDER:
                    rungs = routingctl.route_rungs(provider_cfg, tier, effort)
                    self.assertTrue(all(t in routingctl.TIER_ORDER for t, _ in rungs), rungs)
                    self.assertTrue(all(provider_cfg["models"][t] not in FRONTIER for t, _ in rungs))
        # A configured ladder naming the frontier level is ignored, never climbed.
        ladder = {"models": dict(configured["claude"]["models"]),
                  "escalation_ladder": [["max", "xhigh"], ["frontier", "high"], ["L6", "high"]]}
        self.assertEqual(routingctl.provider_ladder(ladder), [("max", "xhigh")])
        # Runner routes for every failure sequence stay on the ordinary map.
        config = default_config()
        for provider in ("claude", "codex"):
            for classes in ([], ["semantic"] * 6, ["mechanical"] * 9, ["unknown"] * 9, ["budget"] * 9):
                task = {"provider": provider, "allow_provider_fallback": False, "model_tier": "economy",
                        "reasoning_effort": "low", "functional_failures": len(classes), "failure_classes": classes}
                self.assertNotIn(run.choose_route(task, config, None)["model"], FRONTIER)
        # Selector: no signal combination and no outage reaches the frontier level.
        for name in routingctl.PRIMARY_SIGNALS:
            for mods in ([], ["weak_validation"], ["implementation"], ["strong_validation"]):
                result = routingctl.select_route({"signals": [name, *mods], "providers": ["codex", "claude"]})
                route = result["route"]
                if route:
                    self.assertNotIn(route["model"], FRONTIER)
                    self.assertFalse({rung["model"] for rung in route["ladder"]} & FRONTIER)
        outage = routingctl.select_route({"signals": ["extreme_code_review"], "providers": ["claude", "codex"],
                                          "availability": {"claude": "outage", "codex": "outage"}})
        self.assertEqual(outage["decision"], "no_candidate")
        # Floor lifting never produces the frontier level.
        self.assertEqual(routingctl.minimum_route(["frontier_long_horizon", "weak_validation"]), {"tier": "max", "effort": "high"})
        self.assertEqual(routingctl.minimum_route(["repeated_strong_failure"]), {"tier": "max", "effort": "xhigh"})

    def test_extreme_signals_and_read_only_roles(self):
        floor = routingctl.minimum_route(["extreme_code_review"])
        self.assertEqual(floor, {"tier": "max", "effort": "xhigh", "frontier_eligible": True})
        base = {"signals": ["extreme_architecture"], "agent_tier": "strong", "read_only": True,
                "unit_tokens": 40000}
        for provider, model in (("codex", "gpt-6.2-astra"), ("claude", "claude-fable-5-2")):
            decision = routingctl.delegate_decision({**base, "providers": [provider]})
            self.assertEqual(decision["role"], "analyst")
            self.assertEqual(decision["route"]["model"], model)
            self.assertEqual((decision["route"]["tier"], decision["route"]["effort"]), ("max", "high"))
            self.assertTrue(decision["route"]["frontier"])
            self.assertEqual(decision["route"]["level"], "frontier")
            self.assertIn("frontier_extreme_review", decision["reasons"])
        verifier = routingctl.delegate_decision({**base, "signals": ["extreme_code_review"], "providers": ["codex"],
                                                 "role": "verifier"})
        self.assertEqual(verifier["route"]["model"], "gpt-6.2-astra")
        # Implementation of an extreme leaf stays on Opus 5.5 / Sol 6.2 at max/xhigh.
        write = routingctl.delegate_decision({**base, "read_only": False, "write_scopes": [["src"]],
                                              "providers": ["codex"]})
        self.assertEqual(write["route"]["model"], routingctl.CURRENT_MODELS["codex"]["max"])
        self.assertEqual((write["route"]["tier"], write["route"]["effort"]), ("max", "xhigh"))
        self.assertNotIn("frontier", write["route"])
        # Ordinary review leaves never reach the frontier level.
        plain = routingctl.delegate_decision({**base, "signals": ["architecture_decision"], "providers": ["claude"],
                                              "agent_tier": "economy"})
        self.assertNotIn(plain["route"]["model"], FRONTIER)
        disabled = routingctl.delegate_decision({**base, "providers": ["codex"], "frontier": {"enabled": False}})
        self.assertEqual(disabled["route"]["model"], routingctl.CURRENT_MODELS["codex"]["max"])

    def test_stage_counts_only_functional_top_rung_failures(self):
        rungs = routingctl.route_rungs(routingctl.configure_config({})["claude"], "strong", "high")
        self.assertEqual(rungs[-1], ("max", "xhigh"))
        stage = lambda classes, config=None: routingctl.frontier_stage(classes, rungs, config)  # noqa: E731
        self.assertEqual(stage(["semantic"]), "pending")              # climbed to the top rung
        self.assertEqual(stage(["semantic", "semantic"]), "pending")  # one top-rung failure
        self.assertEqual(stage(["semantic"] * 3), "due")              # two top-rung failures
        self.assertEqual(stage(["semantic", "mechanical", "mechanical"]), "due")
        self.assertEqual(stage(["semantic", "unknown", "semantic"]), "due")
        self.assertEqual(stage(["semantic"] * 4), "spent")            # the frontier attempt failed too
        noise = ["environmental", "budget", "timeout_ceiling", "plan_defect"]
        self.assertEqual(stage(["semantic", "semantic"] + noise * 3), "pending")
        self.assertEqual(routingctl.top_rung_failures(["semantic"] + noise * 3, rungs), 0)
        self.assertEqual(stage(["semantic"] * 3, {"routing_policy": {"frontier": {"min_top_failures": 3}}}), "pending")
        self.assertEqual(stage(["semantic"] * 3, {"routing_policy": {"frontier": {"enabled": False}}}), "off")
        self.assertEqual(stage("legacy"), "off")
        self.assertEqual(routingctl.frontier_stage(["semantic"] * 3, [("strong", "high")]), "off")  # top is not max

    def test_agy_credit_errors_are_availability_not_capability(self):
        # Antigravity CLI >= 1.5.10 stops the turn on these; they rotate providers, never escalate.
        for text in ("Error: spend cap reached for this project", "Your prepaid balance is exhausted",
                     "weekly quota exceeded, resets Monday", "You are out of credits", "credits exhausted"):
            self.assertEqual(av.classify(1, text, []), "quota", text)
            self.assertTrue(run.is_rate_limited(text), text)
        self.assertIsNone(av.classify(1, "assertion failed in test_spending_report", []))

    def test_configuration_validation(self):
        good = {"routing_policy": {"frontier": {"enabled": False, "min_top_failures": 3}},
                "claude": {"frontier": {"model": "claude-fable-5-2", "effort": "xhigh"}},
                "codex": {"frontier": {"model": ""}},
                "antigravity": {"frontier": {"model": "gemini-4-carbon-high"}}}
        cfg.validate(good, partial=True)
        self.assertIsNone(routingctl.frontier_model("codex", good))
        self.assertEqual(routingctl.frontier_model("antigravity", good), {"model": "gemini-4-carbon-high", "effort": "high"})
        bad = [
            {"routing_policy": {"frontier": {"enabled": "yes"}}},
            {"routing_policy": {"frontier": {"min_top_failures": 0}}},
            {"routing_policy": {"frontier": {"approval": True}}},
            {"codex": {"frontier": {"model": "gpt-6.2-astra", "effort": "ultra"}}},
            {"claude": {"frontier": {"model": "claude-fable-5-2", "effort": "max"}}},
            {"claude": {"frontier": {"model": "bad id"}}},
            {"claude": {"models": {"frontier": "claude-fable-5-2"}}},
        ]
        for config in bad:
            with self.assertRaises(cfg.ConfigError, msg=json.dumps(config)):
                cfg.validate(config, partial=True)

    def test_schema_one_to_four_manifests_unaffected(self):
        config = default_config()
        legacy = {"provider": "claude", "allow_provider_fallback": False, "model_tier": "strong",
                  "reasoning_effort": "high", "functional_failures": 5}
        self.assertEqual(run.frontier_stage(legacy, config, None), "off")
        self.assertEqual(run.choose_route(legacy, config, None)["model"], routingctl.CURRENT_MODELS["claude"]["max"])
        spec = copy.deepcopy(sample_spec()["tasks"][0])
        for tier in ("frontier", "F6", "L6"):
            with self.assertRaises(planctl.PlanError):
                planctl.normalize_task({**spec, "model_tier": tier}, 0, {"R001", "R002"})


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.temp = Path(self.tmp.name)
        self.root = self.temp / "repo"
        self.root.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        spec = sample_spec()
        if os.name == "nt":
            validation = subprocess.list2cmdline(
                [sys.executable, "-c", "from pathlib import Path; assert Path('implemented.txt').read_text() == 'implemented\\n'"])
            for task in spec["tasks"]:
                task["validation_commands"] = [validation]
        self.plan = planctl.create_plan(self.root, spec, ".ai-work", "frontier")
        _, self.manifest = planctl.load_plan(self.plan)
        self.task = self.manifest["tasks"][0]
        # Opus 5.5 / Sol 6.2 already failed twice at max/xhigh: the frontier step is due.
        self.task.update(provider="auto", allow_provider_fallback=True, model_tier="strong", reasoning_effort="high",
                         functional_failures=3, failure_classes=["semantic", "semantic", "semantic"])
        planctl.save_manifest(self.plan, self.manifest)
        self.config = default_config()
        self.config["tier_routes"] = {"max": {"primary": "codex", "fallbacks": ["claude"]}}
        self.argv_log = self.temp / "argv.jsonl"
        self.good = self.fake("good", None)

    def fake(self, name: str, failure: str | None) -> list[str]:
        """A fake CLI that logs its argv, then fails with `failure` or completes like a worker."""
        worker = self.temp / "worker.py"
        if not worker.exists():
            write_fake_claude(worker)
            worker.write_text(worker.read_text().replace('elif "--json-schema" in args:',
                                                         'elif "--json-schema" in args or "--output-schema" in args:'))
        script = self.temp / f"{name}.py"
        body = [
            "import json, runpy, sys",
            f"open({str(self.argv_log)!r}, 'a').write(json.dumps({{'cli': {name!r}, 'argv': sys.argv[1:-1]}}) + '\\n')",
        ]
        if failure:
            body += [f"print({failure!r}, file=sys.stderr)", "sys.exit(1)"]
        else:
            body += [f"runpy.run_path({str(worker)!r}, run_name='__main__')"]
        script.write_text("\n".join(body) + "\n", encoding="utf-8")
        return [sys.executable, str(script)]

    def calls(self) -> list[dict]:
        if not self.argv_log.exists():
            return []
        return [json.loads(line) for line in self.argv_log.read_text().splitlines()]

    def execute(self) -> bool:
        return run.execute_one_task(self.plan, self.manifest, self.config, self.task,
                                    provider_override=None, dry_run=False, no_wait=True)

    def assert_no_new_evidence(self):
        self.assertEqual(self.task["functional_failures"], 3)
        self.assertEqual(self.task["failure_classes"], ["semantic", "semantic", "semantic"])

    def test_codex_credits_exhausted_goes_to_fable_without_escalation(self):
        self.config["codex"]["command"] = self.fake("codex-out", "You have run out of credits: credits exhausted")
        self.config["claude"]["command"] = self.good
        self.assertTrue(self.execute())
        calls = self.calls()
        self.assertEqual([c["cli"] for c in calls], ["codex-out", "good"])
        codex, claude = calls[0]["argv"], calls[1]["argv"]
        self.assertEqual(codex[codex.index("--model") + 1], "gpt-6.2-astra")
        self.assertIn('model_reasoning_effort="high"', codex)
        self.assertFalse(any("ultra" in item for item in codex))
        self.assertEqual(claude[claude.index("--model") + 1], "claude-fable-5-2")
        self.assertEqual(claude[claude.index("--effort") + 1], "high")
        self.assertEqual(self.task["status"], "completed")
        self.assert_no_new_evidence()
        self.assertEqual(self.task["rate_limit_events"], 1)
        route = self.task["current_route"]
        self.assertEqual((route["tier"], route["level"], route["frontier"]), ("max", "frontier", True))
        self.assertIn(route["tier"], planctl.VALID_TIERS)
        events = av.read(self.plan, self.task["id"])["events"]
        self.assertEqual([(e["provider"], e["category"], e.get("frontier")) for e in events], [("codex", "quota", True)])
        records = [json.loads(line) for line in (self.plan / "telemetry" / "attempts.jsonl").read_text().splitlines()]
        self.assertTrue(records and all(r.get("frontier") is True and r.get("level") == "frontier" for r in records))

    def test_fable_version_unavailable_is_skipped(self):
        self.config["tier_routes"] = {"max": {"primary": "claude", "fallbacks": ["codex"]}}
        self.config["claude"]["command"] = self.fake(
            "old-claude", 'API Error: 400 {"error":{"message":"This version of Claude Code does not support this model"}}')
        self.config["codex"]["command"] = self.good
        self.assertTrue(self.execute())
        self.assertEqual([c["cli"] for c in self.calls()], ["old-claude", "good"])
        self.assert_no_new_evidence()
        self.assertEqual(self.task["rate_limit_events"], 0)
        self.assertIn("frontier_unavailable", [h["event"] for h in self.task["history"]])
        state = av.read(self.plan, self.task["id"])
        fable = {"provider": "claude", "model": "claude-fable-5-2"}
        self.assertIn(workload_routing.model_key(fable), state["cooldowns"])
        self.assertNotIn("claude", state["cooldowns"])  # Opus on the same CLI stays available

    def test_explicit_provider_override_is_respected(self):
        self.config["codex"]["command"] = self.good
        self.config["claude"]["command"] = self.good
        route, cooling = run.frontier_route(self.plan, self.task, self.config, "claude", set())
        self.assertEqual((route["provider"], route["model"], cooling), ("claude", "claude-fable-5-2", False))
        self.task["provider"], self.task["allow_provider_fallback"] = "codex", False
        av.unavailable(self.plan, self.task["id"], "implementation",
                       {"provider": "codex", "tier": "max", "effort": "high", "model": "gpt-6.2-astra", "frontier": True},
                       "quota", self.config)
        self.assertEqual(run.frontier_route(self.plan, self.task, self.config, None, set()), (None, True))
        with self.assertRaises(av.AvailabilityPaused):
            self.execute()
        self.assertEqual(self.calls(), [])
        self.assert_no_new_evidence()

    def test_disabled_policy_keeps_old_ladder_exhaustion(self):
        self.config["routing_policy"]["frontier"] = {"enabled": False}
        self.task.update(provider="claude", allow_provider_fallback=False, functional_failures=2,
                         failure_classes=["semantic", "semantic"])
        self.config["claude"]["command"] = self.good
        self.assertEqual(run.frontier_stage(self.task, self.config, None), "off")
        self.assertFalse(self.execute())
        self.assertEqual(self.task["status"], "blocked")
        self.assertEqual(self.task["history"][-1]["event"], "ladder_exhausted")
        self.assertEqual(self.calls(), [])

    def test_pending_retries_top_rung_then_frontier_failure_blocks(self):
        self.task.update(provider="claude", allow_provider_fallback=False, functional_failures=2,
                         failure_classes=["semantic", "semantic"])
        self.config["claude"]["command"] = self.good
        self.assertEqual(run.frontier_stage(self.task, self.config, None), "pending")
        self.assertTrue(self.execute())  # exhausted ladder retried Opus XHigh instead of blocking
        argv = self.calls()[0]["argv"]
        self.assertEqual(argv[argv.index("--model") + 1], routingctl.CURRENT_MODELS["claude"]["max"])
        self.assertEqual(argv[argv.index("--effort") + 1], "xhigh")
        self.assertNotIn("frontier", self.task["current_route"])
        spent = {**self.task, "status": "pending", "functional_failures": 4, "failure_classes": ["semantic"] * 4}
        self.assertEqual(run.frontier_stage(spent, self.config, None), "spent")

    def test_dry_run_preview_carries_the_frontier_route(self):
        self.config["codex"]["command"] = self.good
        route, _ = run.frontier_route(self.plan, self.task, self.config, None, set())
        command = run.build_worker_command("codex", route, self.config, "prompt", self.plan / "result.json")
        self.assertEqual(command[command.index("--model") + 1], "gpt-6.2-astra")
        self.assertIn('model_reasoning_effort="high"', command)


if __name__ == "__main__":
    unittest.main()
