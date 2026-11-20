#!/usr/bin/env python3
"""Offline tests for review_dispatch.py with a fake claude/codex executable (no model call).

Set REVIEW_DISPATCH_SMOKE=1 to also run the single opt-in live smoke test: one Claude Haiku call
with a one-line fixture (cost: cents). It never runs a max-tier model.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check_delivery as g  # noqa: E402
import review_dispatch as rd  # noqa: E402

HELPER = HERE / "review_dispatch.py"
FAKE = HERE / "fake_review_provider.py"
PLAN = g.CONTROL.as_posix()


def write(root: Path, name: str, text: str) -> Path:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def hashed(root: Path, name: str) -> dict:
    return {"path": name, "sha256": g.sha(root / name)}


def write_plan(root: Path, review_id: str = "006", impl_id: str = "005", *, providers=None,
               chain=("codex", "claude")) -> None:
    """Plan manifest (impl + review task), plan config routing max to the fake CLI, empty global config."""
    task = lambda tid, title, acc, sub: {"id": tid, "title": title, "objective": f"{title}.", "status": "pending",
                                         "model_tier": "max" if tid == review_id else "standard",
                                         "reasoning_effort": "xhigh", "provider": "auto",
                                         "acceptance_criteria": acc, "subtasks": sub}
    manifest = {"tasks": [
        task(impl_id, "Implement fixture", ["Fixture prints passed."], []),
        task(review_id, "Review fixture", ["No unresolved critical/high finding remains."],
             [{"id": "S001", "title": "Dispatch", "objective": f"Run python {rd.HELPER} --task {review_id}."},
              {"id": "S002", "title": "Correct", "objective": "Correct every blocking finding."}])]}
    write(root, f"{PLAN}/manifest.json", json.dumps(manifest))
    cmd = [sys.executable, str(FAKE)]
    config = {"version": 2, "claude": {"command": cmd}, "codex": {"command": cmd},
              "tier_routes": {"max": {"primary": chain[0], "fallbacks": list(chain[1:])}}}
    for provider, extra in (providers or {}).items():
        config[provider].update(extra)
    write(root, f"{PLAN}/orchestrator.config.json", json.dumps(config))
    write(root, "global-config.json", json.dumps({"version": 2}))


def make_fixture(root: Path, review_id: str = "006", impl_id: str = "005", *, providers=None,
                 entries_extra=None, chain=("codex", "claude")) -> dict:
    """Minimal repo: TASK_INPUTS (impl + review), delivered impl receipt, manifest and plan config."""
    code = "test/optimization/unit.py"
    write(root, code, 'print("fixture passed")\n')
    impl = {"id": impl_id, "kind": "implementation", "work_type": "implementation", "requires_independent_review": False,
            "review_of": None, "prepared_reports": [], "output": (g.OUTPUT / f"{impl_id}-receipt.json").as_posix(),
            "report": (g.OUTPUT / f"{impl_id}-outcome.md").as_posix(), "required_checks": [["python", code]],
            "write_scope": [code], "acceptance_ids": ["AC01"]}
    review = dict(impl, id=review_id, kind="review", work_type="review_and_fix", requires_independent_review=True,
                  review_of=impl_id, output=(g.OUTPUT / f"{review_id}-receipt.json").as_posix(),
                  report=(g.OUTPUT / f"{review_id}-outcome.md").as_posix())
    entries = [impl, review] + list(entries_extra or [])
    write(root, (g.DOC / "TASK_INPUTS.json").as_posix(), json.dumps({"schema_version": 2, "tasks": entries}))
    write(root, impl["report"], "# Outcome\n")
    write(root, impl["output"], json.dumps({"schema_version": 2, "task_id": impl_id, "kind": "implementation",
                                            "status": "completed", "changed_artifacts": [hashed(root, code)]}))
    write_plan(root, review_id, impl_id, providers=providers, chain=chain)
    return {"impl": impl, "review": review, "code": code}


def run_helper(root: Path, task: str = "006", *args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    environ = {k: v for k, v in os.environ.items() if not k.startswith(("FAKE_REVIEW_", rd.ACTIVE_ENV))}
    environ.update(PAE_CONFIG_PATH=str(root / "global-config.json"), PYTHONIOENCODING="utf-8")
    environ.update(env or {})
    return subprocess.run([sys.executable, str(HELPER), "--repo-root", str(root), "--task", task, *args],
                          capture_output=True, text=True, encoding="utf-8", env=environ, timeout=120)


def dispatch_line(stdout: str) -> dict:
    line = next(x for x in stdout.splitlines() if x.startswith("DISPATCH "))
    return dict(part.split("=", 1) for part in line.split()[1:])


def receipt_block(stdout: str) -> dict:
    line = next(x for x in stdout.splitlines() if x.startswith("RECEIPT_REVIEWER "))
    return json.loads(line.split(" ", 1)[1])


class ReviewDispatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.fx = make_fixture(self.root)
        self.argv_log = self.root / "argv.jsonl"

    def helper(self, *args, **env):
        env = {"FAKE_REVIEW_ARGV_LOG": str(self.argv_log), **{k: str(v) for k, v in env.items()}}
        return run_helper(self.root, "006", *args, env=env)

    def argvs(self):
        return [json.loads(x) for x in self.argv_log.read_text(encoding="utf-8").splitlines()] if self.argv_log.exists() else []

    def ledger(self):
        return json.loads((self.root / PLAN / "results/006-availability.json").read_text(encoding="utf-8"))

    def test_codex_first_read_only_and_evidence_accepted_shape(self):
        out = self.helper()
        self.assertEqual(out.returncode, 0, out.stderr)
        info = dispatch_line(out.stdout)
        self.assertEqual(info["task"], "006")
        evidence = g.load(self.root / info["evidence"])
        self.assertEqual(g.sha(self.root / info["evidence"]), info["sha256"])
        self.assertEqual((evidence["provider"], evidence["model_tier"], evidence["task_id"]), ("codex", "max", "006"))
        self.assertEqual(evidence["session_id"], info["session"])
        paths = {x["path"] for x in evidence["reviewed_inputs"]}
        self.assertTrue({self.fx["impl"]["output"], self.fx["impl"]["report"], self.fx["code"]} <= paths)
        self.assertEqual(g.sha(self.root / evidence["findings_path"]), evidence["findings_sha256"])
        self.assertEqual(evidence["usage"]["output_tokens"], 60)
        argv = self.argvs()[0]["argv"]
        self.assertEqual(argv[argv.index("--sandbox") + 1], "read-only")
        self.assertIn("--json", argv)
        self.assertFalse(any(a.startswith("--dangerously") or a == "danger-full-access" for a in argv))
        self.assertLessEqual(len(out.stdout.split("FINDINGS", 1)[1].split("RECEIPT_REVIEWER")[0].encode()), rd.MAX_COMPACT)

    def test_claude_argv_is_plan_mode_with_read_only_tools(self):
        make_fixture(self.root, chain=("claude", "codex"))
        out = self.helper()
        self.assertEqual(out.returncode, 0, out.stderr)
        argv = self.argvs()[0]["argv"]
        self.assertEqual(argv[argv.index("--permission-mode") + 1], "plan")
        self.assertEqual(argv[argv.index("--output-format") + 1], "json")
        self.assertEqual(argv[argv.index("--tools") + 1], rd.CLAUDE_TOOLS)
        self.assertEqual(argv[argv.index("--model") + 1], "claude-opus-5-5")
        self.assertEqual(argv[argv.index("--effort") + 1], "xhigh")
        evidence = g.load(self.root / dispatch_line(out.stdout)["evidence"])
        self.assertEqual((evidence["provider"], evidence["usage"]["usd"]), ("claude", 0.0123))
        self.assertEqual(evidence["observed_models"], ["claude-opus-5-5"])

    def test_dangerous_extra_args_are_stripped(self):
        make_fixture(self.root, providers={"codex": {"extra_args": ["--dangerously-bypass-approvals-and-sandbox",
                                                                      "--sandbox", "danger-full-access", "--color", "never"]}})
        out = self.helper()
        self.assertEqual(out.returncode, 0, out.stderr)
        argv = self.argvs()[0]["argv"]
        self.assertEqual([a for a in argv if a in ("--sandbox", "-s")], ["--sandbox"])
        self.assertNotIn("danger-full-access", argv)
        self.assertIn("--color", argv)
        with self.assertRaises(rd.DispatchError):
            rd.assert_read_only("codex", ["codex", "exec", "--sandbox", "read-only", "--dangerously-x", "P"])
        with self.assertRaises(rd.DispatchError):
            rd.assert_read_only("claude", ["claude", "--permission-mode", "auto", "--tools", rd.CLAUDE_TOOLS, "P"])

    def test_quota_falls_back_to_claude_and_cools_codex_down(self):
        out = self.helper(FAKE_REVIEW_MODE_CODEX="quota")
        self.assertEqual(out.returncode, 0, out.stderr)
        evidence = g.load(self.root / dispatch_line(out.stdout)["evidence"])
        self.assertEqual(evidence["provider"], "claude")
        self.assertEqual(evidence["skipped_attempts"][0]["outcome"], "quota")
        self.assertEqual(self.ledger()["cooldowns"]["codex"]["reason"], "quota")
        # The next dispatch skips the cooled-down provider without calling it.
        before = len(self.argvs())
        dry = self.helper("--dry-run")
        self.assertIn("codex:cooldown(quota)", dry.stdout)
        self.assertEqual(len(self.argvs()), before)

    def test_no_provider_exits_nonzero_without_evidence(self):
        out = self.helper(FAKE_REVIEW_MODE="quota")
        self.assertEqual(out.returncode, rd.EXIT_NO_PROVIDER)
        self.assertIn("NO_REVIEW", out.stderr)
        self.assertFalse(list((self.root / rd.evidence_dir("006")).glob("dispatch-*.json")))
        self.assertEqual({e["provider"] for e in self.ledger()["events"]}, {"codex", "claude"})

    def test_functional_failures_are_not_availability(self):
        out = self.helper(FAKE_REVIEW_MODE_CODEX="garbage", FAKE_REVIEW_MODE_CLAUDE="nosession")
        self.assertEqual(out.returncode, rd.EXIT_NO_PROVIDER)
        self.assertIn("codex:invalid_review_output", out.stderr)
        self.assertIn("claude:no_session_id", out.stderr)
        self.assertFalse((self.root / PLAN / "results/006-availability.json").exists())

    def test_findings_are_compact_and_counted(self):
        out = self.helper(FAKE_REVIEW_MODE="findings")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("verdict=changes_requested", out.stdout)
        self.assertIn("blocking=1", out.stdout)
        self.assertIn("F01 [high]", out.stdout)

    def test_dry_run_spends_nothing(self):
        out = self.helper("--dry-run")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("COMMAND ", out.stdout)
        self.assertIn("<prompt>", out.stdout)
        self.assertEqual(self.argvs(), [])
        self.assertFalse((self.root / rd.evidence_dir("006")).exists())

    def test_identical_inputs_reuse_existing_dispatch_without_spend(self):
        first = self.helper()
        second = self.helper()
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(dispatch_line(first.stdout), dispatch_line(second.stdout))
        self.assertIn("reused=identical_inputs_no_new_spend", second.stdout)
        self.assertEqual(len(self.argvs()), 1)
        third = self.helper("--new")
        self.assertNotEqual(dispatch_line(third.stdout)["session"], dispatch_line(first.stdout)["session"])
        write(self.root, self.fx["code"], 'print("corrected")\n')
        fourth = self.helper()
        self.assertTrue(dispatch_line(fourth.stdout)["evidence"].endswith("dispatch-3.json"))

    def test_reused_session_is_refused(self):
        first = self.helper("--new", FAKE_REVIEW_SESSION="sess-fixed")
        self.assertEqual(first.returncode, 0, first.stderr)
        again = self.helper("--new", FAKE_REVIEW_SESSION="sess-fixed")
        self.assertEqual(again.returncode, rd.EXIT_REFUSED, again.stdout)
        self.assertIn("reused reviewer session", again.stderr)
        self.assertEqual(len(list((self.root / rd.evidence_dir("006")).glob("dispatch-*.json"))), 1)

    def test_pending_then_resume_waits_on_same_reviewer(self):
        out = self.helper("--wait-seconds", "1", FAKE_REVIEW_MODE="sleep:4")
        self.assertEqual(out.returncode, rd.EXIT_PENDING, out.stderr)
        self.assertIn("PENDING task=006", out.stdout)
        resumed = self.helper("--wait-seconds", "60", FAKE_REVIEW_MODE="sleep:4")
        self.assertEqual(resumed.returncode, 0, resumed.stderr)
        self.assertEqual(len(self.argvs()), 1)

    def test_nested_and_non_review_tasks_are_refused(self):
        nested = self.helper(**{rd.ACTIVE_ENV: "1"})
        self.assertEqual(nested.returncode, rd.EXIT_REFUSED)
        self.assertEqual(run_helper(self.root, "005").returncode, rd.EXIT_ERROR)

    def test_missing_predecessor_receipt_is_an_error(self):
        (self.root / self.fx["impl"]["output"]).unlink()
        out = self.helper()
        self.assertEqual(out.returncode, rd.EXIT_ERROR)
        self.assertIn("no delivered receipt", out.stderr)


@unittest.skipUnless(os.environ.get("REVIEW_DISPATCH_SMOKE") == "1", "live smoke test is opt-in (one Haiku call)")
class LiveSmokeTest(unittest.TestCase):
    def test_haiku_session_and_usage_capture(self):
        sys.path.insert(0, str(rd.SCRIPTS))
        import run_isolated
        real = run_isolated.load_config(HERE.parents[3] / PLAN)["claude"]["command"]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_fixture(root, chain=("claude",), providers={"claude": {
                "command": real, "models": {"max": "claude-haiku-5-5"}, "max_effort_by_tier": {"max": "low"}}})
            out = subprocess.run([sys.executable, str(HELPER), "--repo-root", str(root), "--task", "006",
                                  "--wait-seconds", "300"], capture_output=True, text=True, encoding="utf-8",
                                 env={**os.environ, "PYTHONIOENCODING": "utf-8"}, timeout=400)
            print(out.stdout[-3000:], out.stderr[-2000:], sep="\n")
            self.assertEqual(out.returncode, 0, out.stderr)
            evidence = g.load(root / dispatch_line(out.stdout)["evidence"])
            self.assertTrue(evidence["session_id"])
            self.assertEqual(evidence["model"], "claude-haiku-5-5")
            self.assertIsNotNone(evidence["usage"]["output_tokens"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
