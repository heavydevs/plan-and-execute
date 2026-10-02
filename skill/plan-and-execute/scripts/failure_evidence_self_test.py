#!/usr/bin/env python3
"""FailureEvidencePacket budgets, progress-aware stalls and advisory-only diagnosis."""

from __future__ import annotations

import json
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import assistant_triage  # noqa: E402
import resource_watch  # noqa: E402
import run_isolated  # noqa: E402


def packet_size(packet: dict) -> int:
    return len(json.dumps(packet, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def check_large_log_budget(root: Path) -> None:
    log = root / "big.log"
    line = "INFO step progressing normally with a fairly long padded line of output text\n"
    with log.open("w", encoding="utf-8") as handle:
        handle.write("AssertionError: expected 3 got 4\n")
        handle.write(line * (10 * 1024 * 1024 // len(line)))
        handle.write("FAILED tests/test_x.py::test_y - boom\n")
    assert log.stat().st_size >= 10 * 1024 * 1024
    started = time.monotonic()
    built = resource_watch.build_failure_packet(log, command="pytest", exit_code=1)
    packet = built["packet"]
    assert time.monotonic() - started < 5, "packet builder must not scan the whole log"
    assert packet_size(packet) <= packet["budget_bytes"] == resource_watch.PACKET_BUDGET_BYTES
    assert packet["evidence_paths"] == [str(log)]
    assert packet["log_bytes"] == log.stat().st_size
    assert packet["first_failure"].startswith("AssertionError")
    assert packet["latest_delta"][-1].startswith("FAILED tests/test_x.py")
    for key in ("signature", "first_failure", "latest_delta", "process", "resources", "progress", "evidence_paths"):
        assert key in packet, key


def check_seen_lines_not_repeated(root: Path) -> None:
    log = root / "attempt.log"
    log.write_text("old failure line A\nold failure line B pid=111\n", encoding="utf-8")
    first = resource_watch.build_failure_packet(log)
    assert first["packet"]["latest_delta"] == ["old failure line A", "old failure line B pid=111"]
    # Same lines (volatile pid normalized away) plus one genuinely new line.
    log.write_text("old failure line A\nold failure line B pid=222\nnew failure line C\n", encoding="utf-8")
    second = resource_watch.build_failure_packet(log, seen=first["seen"])
    assert second["packet"]["latest_delta"] == ["new failure line C"], second["packet"]["latest_delta"]
    assert second["packet"]["omitted_seen_lines"] == 2
    tiny = resource_watch.build_failure_packet(log, budget_bytes=700)
    assert packet_size(tiny["packet"]) <= 700
    # Lines dropped for budget are not marked seen, so they can surface later.
    assert len(tiny["seen"]) == len(tiny["packet"]["latest_delta"])


def check_stale_map_scope(root: Path) -> None:
    log = root / "stale.log"
    log.write_text(
        "[resource-watch] environment_failure=service_map_invalid details=source snapshot is stale\n",
        encoding="utf-8",
    )
    assert resource_watch.build_failure_packet(log)["packet"]["block_scope"] == "service_map"
    log.write_text("plain test failure\n", encoding="utf-8")
    assert resource_watch.build_failure_packet(log)["packet"]["block_scope"] == "validation"


def check_progress_aware_stall() -> None:
    decide = resource_watch.stall_decision
    # Silent beyond the timeout with no markers: a stall.
    assert decide(1000.0, 0.0, 300)[0] is True
    # Long quiet phase whose progress markers keep arriving: not a stall.
    assert decide(1000.0, 0.0, 300, last_marker_at=900.0) == (False, 100.0)
    # Declared quiet phase longer than the idle timeout: not a stall yet.
    assert decide(500.0, 0.0, 300, expected_quiet_seconds=600)[0] is False
    assert decide(700.0, 0.0, 300, expected_quiet_seconds=600)[0] is True
    # Disabled detector never stalls.
    assert decide(10_000.0, 0.0, 0)[0] is False


def check_environmental_and_advisory(root: Path) -> None:
    command = (
        f'"{sys.executable}" -c "print(\'[resource-watch] environment_failure=health_check_failed\'); '
        f'import sys; sys.exit(1)"'
    )
    evidence = root / "logs" / "017-attempt-1-evidence.json"
    passed, results, _ = run_isolated.run_validation_commands(
        root, [command], root / "logs" / "017-attempt-1-validation.log", 30, evidence_path=evidence,
    )
    assert passed is False
    assert results[0]["failure_class"] == "environmental"
    packet = results[0]["failure_evidence"]
    assert packet["resources"]["environment_failure"] is True
    assert json.loads(evidence.read_text(encoding="utf-8"))["packet"] == packet
    assert run_isolated.evidence_packet_path(root / "logs" / "017-attempt-1-validation.log") == evidence

    baseline = run_isolated.validation_failure_class(results, "mechanical")
    assert baseline == "environmental"
    task = {"id": "017", "functional_failures": 2, "validation_stagnation": {"repeats": 5}}
    config = {"assistant": {
        "enabled": True, "provider": "claude", "max_input_chars": 6000, "max_output_chars": 2000,
        "max_calls_per_task": 2, "unhealthy_threshold": 1, "stall_seconds": 300, "repetition_threshold": 2,
    }}
    plan = root / "plan"
    (plan / "results").mkdir(parents=True)
    seen_inputs: list[str] = []

    def hostile(_config: dict, prompt: str, refs: set[str]) -> dict:
        seen_inputs.append(prompt)
        return {"suggested_class": "mechanical", "confidence": 0.9, "hypothesis": "x", "evidence_refs": ["E1"],
                "failure_class": "mechanical", "completed": True}

    shaped = run_isolated.diagnostic_results(results)
    assert shaped[0]["output_head"] == packet["first_failure"]
    assert shaped[0]["output_tail"] == "\n".join(packet["latest_delta"])
    raw = assistant_triage.triage(plan, task, shaped, config, invoke=hostile)
    advice = run_isolated.advisory_only(raw)
    assert seen_inputs and packet["latest_delta"][-1].split("]")[0] in seen_inputs[0]
    assert advice["advisory"] is True
    for key in run_isolated.ADVISORY_FORBIDDEN_KEYS:
        assert key not in advice, key
    assert run_isolated.advisory_only({"failure_class": "mechanical", "next_route": "x", "completed": True}) == {
        "advisory": True}
    # Advice never feeds the deterministic class; unavailable assistant equals the baseline.
    assert run_isolated.validation_failure_class(results, "mechanical") == baseline
    unavailable = run_isolated.advisory_only(
        assistant_triage.triage(plan, task, shaped, {"assistant": {"enabled": False}}))
    assert unavailable["status"] == "skipped"
    assert run_isolated.validation_failure_class(results, "mechanical") == baseline


def check_artifact_ownership(root: Path) -> None:
    repo = root / "repo"
    evidence = repo / ".ai-work" / "plan" / "logs" / "017-attempt-1-evidence.json"
    evidence.parent.mkdir(parents=True)
    evidence.write_text("{}", encoding="utf-8")
    resource_watch.register_artifact(repo, evidence, scope="task", owner="017")
    record = json.loads((repo / resource_watch.REGISTRY_RELATIVE).read_text(encoding="utf-8").splitlines()[0])
    assert record["scope"] == "task" and record["retention"] == "on-task-end"
    try:
        resource_watch.register_artifact(repo, repo / "skill" / "plan-and-execute" / "x-evidence.json", scope="task")
        raise AssertionError("evidence packet must not land in the skill tree")
    except resource_watch.service_map.MapError:
        pass
    assert resource_watch.cleanup_artifacts(repo, "task", "017") == [str(evidence.resolve())]
    assert not evidence.exists()


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="pae-fe-") as tmp:
        root = Path(tmp)
        check_large_log_budget(root)
        check_seen_lines_not_repeated(root)
        check_stale_map_scope(root)
        check_progress_aware_stall()
        check_environmental_and_advisory(root)
        check_artifact_ownership(root)
    print("failure_evidence_self_test: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
