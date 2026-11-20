"""Hermetic, stdlib-only executor tests. No GitHub, provider, or model needed."""
from __future__ import annotations

import contextlib
import json
from pathlib import Path
import tempfile

import taskctl


@contextlib.contextmanager
def fake_repo():
    previous = {name: getattr(taskctl, name) for name in
                ("ROOT", "PLAN", "TASK_INPUTS", "RUN_ROOT", "MAP", "WATCH", "REVIEW_DISPATCH")}
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        try:
            taskctl.ROOT = root
            taskctl.PLAN = root / ".ai-work/test-plan"
            taskctl.TASK_INPUTS = root / "TASK_INPUTS.json"
            taskctl.RUN_ROOT = root / ".ai-work/chatgpt-executor/runs"
            taskctl.MAP = root / ".ai-work/SERVICE_MAP.md"
            taskctl.WATCH = root / "not-present.py"
            taskctl.REVIEW_DISPATCH = root / "not-present.py"
            (root / "scripts").mkdir()
            (root / "scripts" / "check.py").write_text("print('VALIDATION OK')\n", encoding="utf-8")
            taskctl.TASK_INPUTS.write_text(json.dumps({"tasks": [{"id": "015", "review_of": "014",
                "requires_independent_review": True, "inputs": ["scripts/check.py"],
                "write_scope": ["scripts/check.py"],
                "required_checks": [["python", "scripts/check.py"]]}]}), encoding="utf-8")
            yield root
        finally:
            for name, value in previous.items():
                setattr(taskctl, name, value)


def assert_rejects(fn) -> None:
    try:
        fn()
    except taskctl.GateError:
        return
    raise AssertionError("Expected safe rejection")


def test_paths():
    with fake_repo() as root:
        assert taskctl.safe_path("scripts/check.py") == root / "scripts/check.py"
        for bad in ("../secret", "/etc/passwd", "-x", "scripts/../../bad", "scripts\\check.py"):
            assert_rejects(lambda b=bad: taskctl.safe_path(b, must_exist=False))
        (root / "escape").symlink_to(root / "scripts", target_is_directory=True)
        assert_rejects(lambda: taskctl.safe_path("escape/check.py"))


def test_targeted_and_gate():
    with fake_repo() as root:
        check = taskctl.run_checks("015", "targeted", 15)
        assert check["status"] == "passed" and check["source_unchanged"]
        evidence = taskctl.load(root / check["result_path"])
        assert evidence["mode"] == "targeted"
        assert evidence["results"][0]["status"] == "passed"
        # Targeted success is not equivalent to supervised, approved review evidence.
        gate = taskctl.gate("015", run_path=check["result_path"], review_path=None)
        assert not gate["ready"] and "validation_not_watcher_pass" in gate["reasons"]
        assert "missing_independent_review" in gate["reasons"]
        packet = taskctl.review_packet("015")
        gate = taskctl.gate("015", run_path=check["result_path"], review_path=packet["packet_path"])
        assert "unverified_independent_review_record" in gate["reasons"]
        assert_rejects(lambda: taskctl.check_commands(taskctl.task_contract("015"), "watcher"))


def test_fail_and_mutated_inputs():
    with fake_repo() as root:
        task = taskctl.task_contract("015")
        task["required_checks"] = [["python", "../../out.py"]]
        assert_rejects(lambda: taskctl.check_commands(task, "targeted"))
        task["required_checks"] = [["sh", "-c", "rm -rf /"]]
        assert_rejects(lambda: taskctl.check_commands(task, "targeted"))
        failing = root / "scripts/check.py"
        failing.write_text("raise SystemExit(2)\n", encoding="utf-8")
        result = taskctl.run_checks("015", "targeted", 15)
        assert result["status"] == "failed"
        assert taskctl.load(root / result["result_path"])["results"][0]["exit_code"] == 2


def test_task_status_without_plan():
    with fake_repo():
        result = taskctl.task_status("015")
        assert result["status"] == "unknown_no_checkout"
        assert result["requires_independent_review"]
        assert_rejects(lambda: taskctl.task_contract("../../../../../"))


def run():
    tests = [test_paths, test_targeted_and_gate, test_fail_and_mutated_inputs, test_task_status_without_plan]
    for test in tests:
        test()
    return {"self_tests": len(tests), "status": "passed", "scope": "offline_deterministic_only"}