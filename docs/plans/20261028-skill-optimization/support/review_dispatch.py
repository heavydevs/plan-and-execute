#!/usr/bin/env python3
"""Dispatch one fresh, read-only, max-tier reviewer for a plan review task, in the foreground.

Usage (from the repository root):
  python docs/plans/20261028-skill-optimization/support/review_dispatch.py --repo-root . --task <NNN>
         [--brief <file>] [--input <path> ...] [--dry-run] [--new] [--wait-seconds N]

What it does, deterministically:
  1. Builds a minimal reviewer brief: the review task's checkpoints and acceptance, the reviewed
     implementation task's acceptance, and the reviewed inputs (the predecessor's receipt and outcome
     plus the artifacts that receipt pins, with current sha256). No transcripts, no task histories.
  2. Selects the review route from the skill's own routing: plan config `tier_routes.max`
     (Codex then Claude), the provider's `max` model and clamped effort (Sol 6.2 / Opus 5.5 xhigh),
     skipping providers cooled down in `results/<task>-availability.json`. Frontier is never chosen.
  3. Runs the reviewer with the runner's adapter-pinned read-only argv (`build_summary_command`:
     Claude `--permission-mode plan` plus `--tools Read,Grep,Glob`, Codex `--sandbox read-only`), with
     every `--dangerously-*`/full-access extra argument removed, and captures the structured JSON
     findings, session id, model, native effort and usage.
  4. Classifies a failed call with `availability.classify`: quota/credits/auth/capacity mark that
     provider cooled down for this task and the next provider in the chain is tried; nothing here
     touches the task's failure counters.
  5. Writes evidence under docs/research/20261028-skill-optimization/implementation/reviews/<task>/:
     brief-<n>.md, findings-<n>.json and dispatch-<n>.json (task id, provider, model, native_effort,
     model_tier=max, session_id, brief sha256, reviewed-input hashes, timestamps, exit code, findings
     sha256), then prints `DISPATCH task=<id> session=<id> evidence=<path> sha256=<hash>`, the compact
     findings (<= 4000 bytes) and a `RECEIPT_REVIEWER {json}` line for the review receipt.
  6. Refuses (exit 3) when the returned session or dispatch is already claimed by any dispatch or
     receipt, and never overwrites evidence. An identical earlier dispatch of this task (same brief,
     same reviewed hashes) is printed again without a new spend unless --new is given.

Foreground and resumable: the reviewer runs while this command waits. The wait is bounded by
--wait-seconds (default 540) because a host may move a foreground command that outlives its tool
timeout (Claude Code: 600 s) to the background. If the reviewer is still running at that bound the
helper exits 75 (PENDING); run the same command again in the foreground to keep waiting on the same
reviewer (no second spend). Never launch it in the background.

Exit codes: 0 reviewed (or identical dispatch reprinted / dry run), 1 usage or input error,
2 no provider could review, 3 refused reuse or recursion, 4 another reviewer for different inputs is
still running, 75 pending (rerun the same command).
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parents[3] / "skill" / "plan-and-execute" / "scripts"
sys.path.insert(0, str(HERE))
import check_delivery as gate  # noqa: E402

SCHEMA = "review-dispatch/1"
HELPER = "docs/plans/20261028-skill-optimization/support/review_dispatch.py"
ACTIVE_ENV = "PAE_REVIEW_DISPATCH_ACTIVE"
EXIT_OK, EXIT_ERROR, EXIT_NO_PROVIDER, EXIT_REFUSED, EXIT_CONFLICT, EXIT_PENDING = 0, 1, 2, 3, 4, 75
REVIEW_TIER = "max"
EFFORT_FLOOR = "xhigh"
MAX_EXTRA_BRIEF = 6000
MAX_COMPACT = 4000
HEARTBEAT_SECONDS = 5
STALE_SECONDS = 60
DEFAULT_WAIT = 540
DEFAULT_TIMEOUT = 3600
SEVERITIES = ("critical", "high", "medium", "low", "info")
BLOCKING = ("critical", "high")
READ_ONLY_ADAPTERS = ("claude", "codex")
CLAUDE_TOOLS = "Read,Grep,Glob"
REVIEW_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": ["approved", "changes_requested"]},
        "summary": {"type": "string", "maxLength": 800},
        "findings": {"type": "array", "maxItems": 20, "items": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "maxLength": 16},
                "severity": {"type": "string", "enum": list(SEVERITIES)},
                "location": {"type": "string", "maxLength": 300},
                "title": {"type": "string", "maxLength": 200},
                "detail": {"type": "string", "maxLength": 1200},
                "fix": {"type": "string", "maxLength": 800},
            },
            "required": ["id", "severity", "location", "title", "detail", "fix"],
            "additionalProperties": False,
        }},
    },
    "required": ["verdict", "summary", "findings"],
    "additionalProperties": False,
}
FORBIDDEN_ARG = re.compile(r"^--dangerously|^--yolo$|^--full-auto$|^--trust$|danger-full-access|bypassPermissions|"
                           r"^acceptEdits$|^--allow-dangerously", re.I)
VALUE_FLAGS_DROPPED = {"--sandbox", "-s", "--permission-mode", "--approval-mode", "--add-dir", "--settings",
                       "--tools", "--allowedTools", "--allowed-tools", "--json-schema", "--output-format",
                       "--output-schema", "-o", "--output-last-message"}
CONFIG_DROPPED = re.compile(r"^\s*(sandbox|approval|sandbox_permissions|shell_environment_policy)", re.I)


class DispatchError(RuntimeError):
    def __init__(self, message: str, code: int = EXIT_ERROR):
        super().__init__(message)
        self.code = code


def runner():
    """The skill runner's own builders, imported lazily (the import reconfigures stdio)."""
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    import availability  # noqa: F401
    import routing_config  # noqa: F401
    import routing_telemetry  # noqa: F401
    import routingctl  # noqa: F401
    import run_isolated
    import workload_routing  # noqa: F401
    return run_isolated


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def atomic_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for attempt in range(20):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            if attempt == 19:
                raise
            time.sleep(0.05)


def create_text(path: Path, text: str) -> None:
    """Evidence is created once and never overwritten (same newline policy as run_task_checks)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8") as handle:
            handle.write(text)
    except FileExistsError as exc:
        raise DispatchError(f"Refusing to overwrite existing evidence: {path.name}", EXIT_REFUSED) from exc


# ---------------------------------------------------------------------------------------------
# Inputs and brief
# ---------------------------------------------------------------------------------------------
def load_task(root: Path, plan_rel: str, task_id: str) -> dict:
    for name in (f"{plan_rel}/manifest.json", (gate.DOC / "PLAN1_SPEC.json").as_posix()):
        data = read_json(root / name)
        if isinstance(data, dict):
            for task in data.get("tasks", []):
                if f"{int(task['id']):03}" == task_id:
                    return task
    raise DispatchError(f"Task {task_id} not found in the plan manifest or PLAN1_SPEC.json")


def reviewed_inputs(root: Path, prev: dict, extra: list[str]) -> tuple[list[dict], list[str], list[str]]:
    """Predecessor receipt + outcome (always), the artifacts that receipt pins, then --input paths."""
    receipt_path = gate.local(root, prev["output"])
    if not receipt_path.is_file() or not gate.local(root, prev["report"]).is_file():
        raise DispatchError(f"Implementation task {prev['id']} has no delivered receipt/outcome to review")
    receipt = gate.load(receipt_path)
    changed, missing = [], []
    for key in ("changed_artifacts", "preserved_artifacts"):
        for item in receipt.get(key) or []:
            name = item.get("path") if isinstance(item, dict) else None
            if isinstance(name, str) and name and name not in changed:
                changed.append(name)
    paths = [prev["output"], prev["report"]]
    for name in changed + list(extra):
        if name in paths:
            continue
        path = gate.local(root, name)
        if path.is_file():
            paths.append(name)
        else:
            missing.append(name)
    return [{"path": name, "sha256": gate.sha(gate.local(root, name))} for name in paths], changed, missing


def bullet(items) -> str:
    return "\n".join(f"- {item}" for item in items) or "- (none)"


def build_brief(task_id: str, entry: dict, task: dict, prev: dict, prev_task: dict | None,
                inputs: list[dict], changed: list[str], extra: str) -> str:
    checkpoints = [f"{s['id']} {s['title']}: {s['objective']}" for s in task.get("subtasks", [])
                   if "review_dispatch" not in s.get("objective", "")]
    reports = sorted(set(prev.get("prepared_reports", [])))
    text = f"""You are a fresh, independent, read-only code reviewer (maximum tier) for review task {task_id}.
Rules: read the reviewed inputs below and only the code they reference; never modify a file; never run review_dispatch.py, a provider CLI or a write command; never launch background or asynchronous agents or tasks; finish the whole review in this session and return only the JSON object required by the schema.
Assignment: review the actual implementation delivered by task {prev['id']} ({(prev_task or {}).get('title', 'implementation')}) against its acceptance criteria and the review checkpoints. Report concrete defects with `path:line`. Use critical/high only for a broken acceptance criterion, correctness, security or data-integrity defect. Verdict "approved" only when no critical or high finding remains.

Review task {task_id}: {task.get('title', '')}
Objective: {task.get('objective', '')}

Review task checkpoints (the review worker performs them after your review; context only):
{bullet(checkpoints)}

Review task acceptance:
{bullet(task.get('acceptance_criteria', []))}

Implementation task {prev['id']} acceptance:
{bullet((prev_task or {}).get('acceptance_criteria', []))}

Reviewed inputs (path sha256):
{bullet(f"{x['path']} {x['sha256']}" for x in inputs)}

Changed files named by the {prev['id']} receipt:
{bullet(changed)}

Prepared decision (background only; read if a finding needs it):
{bullet(reports)}
"""
    if extra:
        text += f"\nAdditional focus from the review worker:\n{extra.strip()}\n"
    return text


# ---------------------------------------------------------------------------------------------
# Routing and argv
# ---------------------------------------------------------------------------------------------
def review_effort(task: dict) -> str:
    ri = runner()
    order = ri.EFFORT_ORDER
    requested = str(task.get("reasoning_effort") or EFFORT_FLOOR)
    if requested not in order or order.index(requested) < order.index(EFFORT_FLOOR):
        requested = EFFORT_FLOOR
    return requested


def candidate_routes(plan_dir: Path, task: dict, config: dict, override: str | None) -> tuple[list[dict], list[str]]:
    """Ordered eligible max-tier routes and the skip reasons (cooldown, missing CLI, adapter, frontier)."""
    ri = runner()
    import availability
    import routing_config
    import routingctl
    import workload_routing
    rtask = {**task, "model_tier": REVIEW_TIER}
    effort = review_effort(task)
    chain = routing_config.provider_chain(rtask, config, override, tier=REVIEW_TIER)
    routes = workload_routing.candidates(rtask, config, chain, REVIEW_TIER, effort, ri.clamp_effort, override)
    state = availability.read(plan_dir, task["id"] if isinstance(task["id"], str) else f"{task['id']:03}")
    frontier = routingctl.frontier_model_ids(config)
    eligible, skipped, now = [], [], time.time()
    for route in routes:
        route = ri.resolve_snapshot_route(plan_dir, rtask, route, config)
        provider = route["provider"]
        adapter = ri.provider_profile(provider, config)["adapter"]
        if route["model"] in frontier:
            skipped.append(f"{provider}:frontier_not_default")
        elif adapter not in READ_ONLY_ADAPTERS or route.get("route_profile"):
            skipped.append(f"{provider}:no_read_only_review_adapter")
        elif any(state["cooldowns"].get(key, {}).get("until", 0) > now for key in workload_routing.cooldown_keys(route)):
            reason = next(state["cooldowns"][k].get("reason") for k in workload_routing.cooldown_keys(route)
                          if state["cooldowns"].get(k, {}).get("until", 0) > now)
            skipped.append(f"{provider}:cooldown({reason})")
        elif not ri.executable_available(ri.provider_prefix(provider, config)):
            skipped.append(f"{provider}:missing_cli")
        else:
            # A model without an effort flag (e.g. Haiku) runs at its default; never claim a native effort.
            native = route["effort"] if routingctl.model_supports_effort(config[provider], route["model"]) else "default"
            eligible.append({**route, "adapter": adapter, "native_effort": native})
    return eligible, skipped


def safe_extra_args(values: Any) -> list[str]:
    """Drop write/full-access widening and argv the review command pins itself."""
    if not isinstance(values, list):
        return []
    out: list[str] = []
    skip = False
    items = [str(v) for v in values]
    for index, item in enumerate(items):
        if skip:
            skip = False
            continue
        flag = item.split("=", 1)[0]
        if FORBIDDEN_ARG.search(item):
            continue
        if flag in VALUE_FLAGS_DROPPED:
            skip = "=" not in item
            continue
        if item in ("-c", "--config"):
            value = items[index + 1] if index + 1 < len(items) else ""
            if CONFIG_DROPPED.search(value):
                skip = True
                continue
        out.append(item)
    return out


def assert_read_only(adapter: str, command: list[str]) -> None:
    args = command[:-1]
    bad = [a for a in args if FORBIDDEN_ARG.search(a)]
    if bad:
        raise DispatchError(f"Refusing a non read-only reviewer argv ({bad[0]})", EXIT_REFUSED)
    pairs = list(zip(args, args[1:]))
    if adapter == "claude":
        modes = [b for a, b in pairs if a == "--permission-mode"]
        if modes != ["plan"] or ("--tools", CLAUDE_TOOLS) not in pairs:
            raise DispatchError("Claude reviewer must run with --permission-mode plan and read-only tools", EXIT_REFUSED)
    elif adapter == "codex":
        modes = [b for a, b in pairs if a in ("--sandbox", "-s")]
        if modes != ["read-only"]:
            raise DispatchError("Codex reviewer must run with --sandbox read-only", EXIT_REFUSED)
    else:
        raise DispatchError(f"No pinned read-only review adapter for {adapter}", EXIT_REFUSED)


def review_command(route: dict, config: dict, prompt: str, work: Path, n: int) -> tuple[list[str], Path]:
    """The runner's adapter-pinned read-only summary argv, switched to structured JSON output."""
    ri = runner()
    provider, adapter = route["provider"], route["adapter"]
    cfg = copy.deepcopy(config)
    cfg[provider]["extra_args"] = safe_extra_args(cfg[provider].get("extra_args", []))
    last = work / f"dispatch-{n}-{provider}.last.json"
    command = ri.build_summary_command(provider, route, cfg, prompt, last)
    if command[-1] != prompt:
        raise DispatchError("Unexpected summary argv layout; refusing to dispatch", EXIT_REFUSED)
    if adapter == "claude":
        index = command.index("--output-format")
        command[index + 1] = "json"
        extra = ["--tools", CLAUDE_TOOLS, "--json-schema",
                 json.dumps(REVIEW_SCHEMA, ensure_ascii=False, separators=(",", ":"))]
    else:
        schema_path = work / "codex-review-schema.json"
        atomic_json(schema_path, ri.codex_output_schema(REVIEW_SCHEMA))
        extra = ["--json", "--output-schema", str(schema_path)]
    command = command[:-1] + extra + [prompt]
    assert_read_only(adapter, command)
    return command, last


# ---------------------------------------------------------------------------------------------
# Child wrapper: owns the provider process tree and reports status through a heartbeat file
# ---------------------------------------------------------------------------------------------
def child_main(spec_path: str) -> int:
    runner()
    import process_tree
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    run_path = Path(spec["run"])
    started = time.time()
    status = {"status": "running", "pid": os.getpid(), "started_at": started, "heartbeat_at": started}
    atomic_json(run_path, status)
    stop = threading.Event()

    def beat() -> None:
        while not stop.wait(HEARTBEAT_SECONDS):
            atomic_json(run_path, {**status, "heartbeat_at": time.time()})

    threading.Thread(target=beat, daemon=True).start()
    command = list(spec["command"])
    # cmd.exe truncates a `.cmd` shim argument at its first newline (same rule as run_process).
    if os.name == "nt" and command and command[0].lower().endswith((".cmd", ".bat")):
        command = [" ;; ".join(line.strip() for line in part.splitlines() if line.strip()) if "\n" in part else part
                   for part in command]
    code = 127
    with open(spec["stdout"], "wb") as out, open(spec["stderr"], "wb") as err:
        try:
            process = process_tree.launch(command, cwd=spec["cwd"], stdin=subprocess.DEVNULL, stdout=out, stderr=err)
        except OSError as exc:
            err.write(f"Failed to start provider process: {type(exc).__name__}\n".encode())
            process = None
        if process is not None:
            try:
                timeout = int(spec.get("timeout_seconds") or 0)
                code = process.wait(timeout=timeout if timeout > 0 else None)
            except subprocess.TimeoutExpired:
                process_tree.terminate(process)
                err.write(b"\nreview_dispatch: provider_ceiling reached; reviewer terminated\n")
                code = 126
            finally:
                process_tree.close(process)
    stop.set()
    atomic_json(run_path, {**status, "status": "finished", "exit_code": code, "heartbeat_at": time.time(),
                           "finished_at": time.time()})
    return 0


def launch_child(root: Path, work: Path, n: int, route: dict, command: list[str], env: dict | None,
                 timeout: int) -> dict:
    base = work / f"dispatch-{n}-{route['provider']}"
    attempt = {"provider": route["provider"], "adapter": route["adapter"], "model": route["model"],
               "native_effort": route.get("native_effort", route["effort"]),
               "requested_effort": route.get("requested_effort", route["effort"]),
               "argv_redacted": runner().redact_command(command), "started_at": now_iso(),
               "run": f"{base}.run.json", "stdout": f"{base}.stdout", "stderr": f"{base}.stderr",
               "last": str(work / f"dispatch-{n}-{route['provider']}.last.json"), "status": "running"}
    for name in ("run", "stdout", "stderr", "last"):
        Path(attempt[name]).unlink(missing_ok=True)
    spec = {"command": command, "cwd": str(root), "run": attempt["run"], "stdout": attempt["stdout"],
            "stderr": attempt["stderr"], "timeout_seconds": timeout}
    spec_path = Path(f"{base}.spec.json")
    atomic_json(spec_path, spec)
    child_env = dict(os.environ if env is None else env)
    child_env[ACTIVE_ENV] = "1"
    child_env.setdefault("PYTHONIOENCODING", "utf-8")
    options: dict[str, Any] = {}
    if os.name == "nt":
        options["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP | getattr(subprocess, "CREATE_NO_WINDOW", 0)
    else:
        options["start_new_session"] = True
    process = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--child", str(spec_path)],
                               cwd=root, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL, env=child_env, **options)
    attempt["wrapper_pid"] = process.pid
    attempt["spawned_at"] = time.time()
    return attempt


def attempt_alive(attempt: dict) -> bool:
    """Non-blocking: the wrapper is still running and its heartbeat is fresh."""
    run = read_json(Path(attempt["run"]))
    if isinstance(run, dict) and run.get("status") == "finished":
        return False
    beat = run.get("heartbeat_at") if isinstance(run, dict) else attempt.get("spawned_at", 0)
    return time.time() - float(beat or 0) <= STALE_SECONDS


def wait_attempt(attempt: dict, wait_seconds: int) -> str:
    """finished | stale | pending, waiting in the foreground at most wait_seconds (0: no bound)."""
    start = time.monotonic()
    while True:
        run = read_json(Path(attempt["run"]))
        if isinstance(run, dict) and run.get("status") == "finished":
            attempt["exit_code"] = run.get("exit_code")
            attempt["finished_at"] = now_iso()
            return "finished"
        beat = run.get("heartbeat_at") if isinstance(run, dict) else attempt.get("spawned_at", 0)
        if time.time() - float(beat or 0) > STALE_SECONDS:
            return "stale"
        if wait_seconds > 0 and time.monotonic() - start >= wait_seconds:
            return "pending"
        time.sleep(0.5)


# ---------------------------------------------------------------------------------------------
# Output parsing
# ---------------------------------------------------------------------------------------------
def read_text(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def find_review(value: Any) -> dict | None:
    ri = runner()
    if isinstance(value, dict):
        if value.get("verdict") in ("approved", "changes_requested") and isinstance(value.get("findings"), list):
            return value
        for key in ("structured_output", "result", "output", "message", "text", "content"):
            if key in value:
                found = find_review(value[key])
                if found:
                    return found
    elif isinstance(value, str):
        for candidate in ri.decode_json_candidates(value, maximum=40):
            if candidate != value:
                found = find_review(candidate)
                if found:
                    return found
    return None


def parse_output(attempt: dict) -> dict:
    """session_id, review, usage and observed models from one finished reviewer run."""
    ri = runner()
    import routing_telemetry
    stdout = read_text(attempt["stdout"])
    session, review, models, error = None, None, [], None
    if attempt["adapter"] == "claude":
        envelopes = [v for v in ri.decode_json_candidates(stdout, maximum=40)
                     if isinstance(v, dict) and (v.get("type") == "result" or "session_id" in v)]
        envelope = envelopes[0] if envelopes else {}
        session = envelope.get("session_id")
        models = sorted(envelope.get("modelUsage", {})) if isinstance(envelope.get("modelUsage"), dict) else []
        if envelope.get("is_error"):
            error = "provider reported is_error"
        review = find_review(envelope)
    else:
        for line in stdout.splitlines():
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if isinstance(event, dict) and event.get("type") == "thread.started" and not session:
                session = event.get("thread_id")
            if isinstance(event, dict) and event.get("type") in ("turn.failed", "error"):
                error = "provider reported an error event"
        review = find_review(read_text(attempt["last"])) or find_review(stdout)
    return {"session_id": session if isinstance(session, str) and session else None, "review": review,
            "observed_models": models, "usage": routing_telemetry.extract_usage(stdout), "error": error}


def normalize_review(review: dict) -> dict:
    findings = []
    for index, item in enumerate(review.get("findings", [])[:20], 1):
        if not isinstance(item, dict):
            continue
        severity = str(item.get("severity", "")).lower()
        findings.append({"id": str(item.get("id") or f"F{index:02}")[:16],
                         "severity": severity if severity in SEVERITIES else "medium",
                         "location": str(item.get("location", ""))[:300], "title": str(item.get("title", ""))[:200],
                         "detail": str(item.get("detail", ""))[:1200], "fix": str(item.get("fix", ""))[:800]})
    return {"verdict": review["verdict"], "summary": str(review.get("summary", ""))[:800], "findings": findings}


# ---------------------------------------------------------------------------------------------
# Evidence and reuse guards
# ---------------------------------------------------------------------------------------------
def evidence_dir(task_id: str) -> str:
    return gate.review_dir(task_id).rstrip("/")


def dispatch_files(root: Path) -> list[Path]:
    base = root / gate.OUTPUT / "reviews"
    return sorted(base.glob("*/dispatch-*.json")) if base.is_dir() else []


def claimed(root: Path, entries: dict, task_id: str) -> dict:
    """Sessions/dispatch hashes claimed by other receipts, and every session named by any dispatch file."""
    used = gate.used_dispatches(root, entries, task_id)
    sessions = {}
    for path in dispatch_files(root):
        data = read_json(path)
        if isinstance(data, dict) and isinstance(data.get("session_id"), str):
            sessions.setdefault(data["session_id"], path.relative_to(root).as_posix())
    return {"receipt_sessions": used["session"], "receipt_dispatches": used["dispatch"], "dispatch_sessions": sessions}


def next_number(root: Path, work: Path, task_id: str) -> int:
    numbers = [0]
    for folder, pattern in ((root / evidence_dir(task_id), r"(?:dispatch|brief|findings)-(\d+)\."),
                            (work, r"dispatch-(\d+)[.-]")):
        if folder.is_dir():
            for path in folder.iterdir():
                match = re.match(pattern, path.name)
                if match:
                    numbers.append(int(match.group(1)))
    return max(numbers) + 1


def receipt_block(evidence_rel: str, evidence_sha: str, record: dict) -> dict:
    return {"reviewer": {"provider": record["provider"], "model": record["model"],
                         "native_effort": record["native_effort"], "model_tier": REVIEW_TIER, "fresh_context": True,
                         "session_id": record["session_id"], "dispatch_evidence": evidence_rel,
                         "dispatch_sha256": evidence_sha},
            "reviewed_inputs": record["reviewed_inputs"]}


def compact(findings: list[dict], verdict: str, summary: str, findings_rel: str) -> str:
    lines = [f"verdict={verdict} summary={summary}"]
    for item in findings:
        lines.append(f"{item['id']} [{item['severity']}] {item['location']} - {item['title']}: {item['detail']}"
                     + (f" (fix: {item['fix']})" if item.get("fix") else ""))
    out, used = [], 0
    for index, line in enumerate(lines):
        size = len(line.encode("utf-8")) + 1
        if used + size > MAX_COMPACT - 120:
            out.append(f"... {len(lines) - index} more; full findings in {findings_rel}")
            break
        out.append(line)
        used += size
    return "\n".join(out)


def print_dispatch(root: Path, evidence_rel: str, record: dict, reused: bool = False) -> None:
    evidence_sha = gate.sha(gate.local(root, evidence_rel))
    findings = gate.load(gate.local(root, record["findings_path"]))
    print(f"DISPATCH task={record['task_id']} session={record['session_id']} evidence={evidence_rel} sha256={evidence_sha}")
    note = " reused=identical_inputs_no_new_spend" if reused else ""
    print(f"REVIEW provider={record['provider']} model={record['model']} native_effort={record['native_effort']} "
          f"verdict={findings['verdict']} findings={len(findings['findings'])} blocking={record['blocking_findings']}"
          f" usd={record['usage'].get('usd')}{note}")
    print("FINDINGS")
    print(compact(findings["findings"], findings["verdict"], findings["summary"], record["findings_path"]))
    print("RECEIPT_REVIEWER " + json.dumps(receipt_block(evidence_rel, evidence_sha, record), separators=(",", ":")))


def finalize(root: Path, entries: dict, state: dict, attempt: dict, parsed: dict) -> str:
    task_id, n = state["task_id"], state["dispatch"]
    marks = claimed(root, entries, task_id)
    session = parsed["session_id"]
    if session in marks["receipt_sessions"] or session in marks["dispatch_sessions"]:
        raise DispatchError(f"Refusing reused reviewer session {session} (already claimed)", EXIT_REFUSED)
    review = normalize_review(parsed["review"])
    folder = evidence_dir(task_id)
    findings_rel = f"{folder}/findings-{n}.json"
    evidence_rel = f"{folder}/dispatch-{n}.json"
    for name in (findings_rel, evidence_rel):
        if gate.local(root, name).exists():
            raise DispatchError(f"Refusing to overwrite existing evidence: {name}", EXIT_REFUSED)
    create_text(gate.local(root, findings_rel), json.dumps(
        {"task_id": task_id, "dispatch": n, "session_id": session, **review}, indent=2, ensure_ascii=False) + "\n")
    blocking = sum(1 for f in review["findings"] if f["severity"] in BLOCKING)
    record = {
        "schema": SCHEMA, "task_id": task_id, "review_of": state["review_of"], "dispatch": n,
        "provider": attempt["provider"], "model": attempt["model"], "native_effort": attempt["native_effort"],
        "requested_effort": attempt["requested_effort"], "model_tier": REVIEW_TIER, "fresh_context": True,
        "read_only": True, "session_id": session, "observed_models": parsed["observed_models"],
        "brief_path": state["brief_path"], "brief_sha256": state["brief_sha256"],
        "reviewed_inputs": state["reviewed_inputs"], "argv_redacted": attempt["argv_redacted"],
        "started_at": attempt["started_at"], "finished_at": attempt.get("finished_at") or now_iso(),
        "exit_code": attempt.get("exit_code"), "usage": parsed["usage"], "verdict": review["verdict"],
        "findings_count": len(review["findings"]), "blocking_findings": blocking,
        "findings_path": findings_rel, "findings_sha256": gate.sha(gate.local(root, findings_rel)),
        "skipped_attempts": [{k: a.get(k) for k in ("provider", "model", "outcome", "exit_code")}
                             for a in state["attempts"] if a is not attempt],
        "helper": HELPER,
    }
    create_text(gate.local(root, evidence_rel), json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    evidence_sha = gate.sha(gate.local(root, evidence_rel))
    if evidence_sha in marks["receipt_dispatches"]:
        raise DispatchError("Refusing a dispatch hash already claimed by another receipt", EXIT_REFUSED)
    return evidence_rel


def identical_dispatch(root: Path, entries: dict, task_id: str, brief_sha: str) -> tuple[str, dict] | None:
    marks = claimed(root, entries, task_id)
    for path in sorted((root / evidence_dir(task_id)).glob("dispatch-*.json"), reverse=True):
        data = read_json(path)
        if not isinstance(data, dict) or data.get("brief_sha256") != brief_sha or data.get("task_id") != task_id:
            continue
        rel = path.relative_to(root).as_posix()
        if data.get("session_id") in marks["receipt_sessions"] or gate.sha(path) in marks["receipt_dispatches"]:
            raise DispatchError(f"Identical dispatch {rel} is already claimed by another receipt", EXIT_REFUSED)
        if all(gate.local(root, x["path"]).is_file() and gate.sha(gate.local(root, x["path"])) == x["sha256"]
               for x in data.get("reviewed_inputs", [])) and gate.local(root, data.get("findings_path", "")).is_file():
            return rel, data
    return None


# ---------------------------------------------------------------------------------------------
# Main flow
# ---------------------------------------------------------------------------------------------
def active_state(work: Path) -> tuple[Path, dict] | None:
    states = sorted(work.glob("dispatch-*.state.json"), key=lambda p: int(re.findall(r"\d+", p.name)[0]))
    for path in reversed(states):
        data = read_json(path)
        if isinstance(data, dict) and data.get("status") == "active":
            return path, data
    return None


def drive(root: Path, plan_dir: Path, entries: dict, task: dict, config: dict, state_path: Path, state: dict,
          args: argparse.Namespace) -> int:
    ri = runner()
    import availability
    work = state_path.parent
    while True:
        current = next((a for a in state["attempts"] if a.get("status") == "running"), None)
        if current is not None:
            outcome = wait_attempt(current, args.wait_seconds)
            if outcome == "pending":
                atomic_json(state_path, state)
                elapsed = int(time.time() - float(current.get("spawned_at", time.time())))
                print(f"PENDING task={state['task_id']} dispatch={state['dispatch']} provider={current['provider']} "
                      f"elapsed={elapsed}s: the reviewer is still running. Run the same command again in the "
                      f"foreground to keep waiting; do not start another reviewer.")
                return EXIT_PENDING
            current["status"] = "done"
            if outcome == "stale":
                current["outcome"] = "abandoned_no_heartbeat"
            else:
                combined = read_text(current["stdout"]) + "\n" + read_text(current["stderr"])
                code = int(current.get("exit_code") if current.get("exit_code") is not None else 1)
                category = availability.classify(code, combined, sorted(ri.configured_retry_exit_codes(current["provider"], config)))
                parsed = parse_output(current) if category is None else None
                if category in (*availability.CATEGORIES, "configured_exit", "missing_cli"):
                    current["outcome"] = category
                    route = {k: current[k] for k in ("provider", "model")}
                    route.update(tier=REVIEW_TIER, effort=current["requested_effort"],
                                 requested_effort=current["requested_effort"])
                    availability.unavailable(plan_dir, state["task_id"], "implementation", route, category, config)
                elif category == "configuration":
                    current["outcome"] = "configuration"
                elif code != 0 or parsed["error"]:
                    current["outcome"] = f"provider_error_exit_{code}"
                elif not parsed["session_id"]:
                    current["outcome"] = "no_session_id"
                elif not parsed["review"]:
                    current["outcome"] = "invalid_review_output"
                else:
                    current["outcome"] = "reviewed"
                    try:
                        evidence_rel = finalize(root, entries, state, current, parsed)
                    except DispatchError:
                        state["status"] = "refused"
                        atomic_json(state_path, state)
                        raise
                    state["status"], state["evidence"] = "completed", evidence_rel
                    atomic_json(state_path, state)
                    print_dispatch(root, evidence_rel, gate.load(gate.local(root, evidence_rel)))
                    return EXIT_OK
            atomic_json(state_path, state)
            print(f"ATTEMPT task={state['task_id']} provider={current['provider']} outcome={current['outcome']}",
                  file=sys.stderr)
        tried = {a["provider"] for a in state["attempts"]}
        routes, skipped = candidate_routes(plan_dir, task, config, args.provider)
        routes = [r for r in routes if r["provider"] not in tried]
        if not routes:
            state["status"] = "failed"
            atomic_json(state_path, state)
            reasons = [f"{a['provider']}:{a.get('outcome')}" for a in state["attempts"]] + skipped
            print(f"NO_REVIEW task={state['task_id']} dispatch={state['dispatch']}: no provider could review "
                  f"({', '.join(reasons) or 'empty chain'}). Leave the review pending; availability faults are not "
                  f"review failures.", file=sys.stderr)
            return EXIT_NO_PROVIDER
        route = routes[0]
        brief = gate.local(root, state["brief_path"]).read_text(encoding="utf-8")
        command, _last = review_command(route, config, brief, work, state["dispatch"])
        env = ri.spawn_env(route["provider"], config)
        attempt = launch_child(root, work, state["dispatch"], route, command, env, args.timeout_seconds)
        state["attempts"].append(attempt)
        atomic_json(state_path, state)
        print(f"REVIEWER task={state['task_id']} dispatch={state['dispatch']} provider={route['provider']} "
              f"model={route['model']} native_effort={route['native_effort']} (foreground; waiting)", file=sys.stderr)


def run(args: argparse.Namespace) -> int:
    if os.environ.get(ACTIVE_ENV):
        raise DispatchError("Refusing a nested review dispatch from inside a reviewer", EXIT_REFUSED)
    if not re.fullmatch(r"\d{3}", args.task or ""):
        raise DispatchError("--task must be a three-digit task id")
    root = Path(args.repo_root).resolve()
    ri = runner()
    entries = gate.catalog(root)
    entry = entries.get(args.task)
    if not entry or not entry.get("requires_independent_review") or not entry.get("review_of"):
        raise DispatchError(f"Task {args.task} is not an independent review task")
    prev = entries.get(entry["review_of"])
    if not prev:
        raise DispatchError(f"Reviewed task {entry['review_of']} is missing from TASK_INPUTS.json")
    plan_dir = root / args.plan
    task = load_task(root, args.plan, args.task)
    task = {**task, "id": args.task}
    prev_task = None
    try:
        prev_task = load_task(root, args.plan, prev["id"])
    except DispatchError:
        pass
    extra_inputs = []
    for name in args.input or []:
        gate.local(root, name.replace("\\", "/"))
        extra_inputs.append(name.replace("\\", "/"))
    inputs, changed, missing = reviewed_inputs(root, prev, extra_inputs)
    extra = ""
    if args.brief:
        raw = Path(args.brief).read_bytes()
        if len(raw) > MAX_EXTRA_BRIEF:
            raise DispatchError(f"--brief is larger than {MAX_EXTRA_BRIEF} bytes; keep the focus note short")
        extra = raw.decode("utf-8")
    brief = build_brief(args.task, entry, task, prev, prev_task, inputs, changed, extra)
    brief_sha = sha_bytes(brief.encode("utf-8"))
    if missing:
        print(f"NOTE missing artifacts named by the {prev['id']} receipt (not reviewed): {', '.join(missing)}",
              file=sys.stderr)
    config = ri.load_config(plan_dir)
    work = plan_dir / "reviews" / args.task
    work.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        routes, skipped = candidate_routes(plan_dir, task, config, args.provider)
        brief_path = work / "brief-dry-run.md"
        brief_path.write_text(brief, encoding="utf-8")
        print(f"DRY-RUN task={args.task} review_of={prev['id']} chain={','.join(r['provider'] for r in routes) or '-'} "
              f"skipped={','.join(skipped) or '-'}")
        print(f"BRIEF {brief_path.relative_to(root).as_posix()} sha256={brief_sha} bytes={len(brief.encode())}")
        if routes:
            command, _ = review_command(routes[0], config, brief, work, 0)
            print("COMMAND " + json.dumps(ri.redact_command(command), ensure_ascii=False))
            return EXIT_OK
        print("NO_REVIEW: no eligible provider for a max-tier read-only review", file=sys.stderr)
        return EXIT_NO_PROVIDER

    pending = active_state(work)
    if pending is not None:
        state_path, state = pending
        if state.get("brief_sha256") == brief_sha:
            return drive(root, plan_dir, entries, task, config, state_path, state, args)
        running = next((a for a in state["attempts"] if a.get("status") == "running"), None)
        alive = running is not None and attempt_alive(running)
        if alive and not args.abandon_pending:
            raise DispatchError(f"Reviewer dispatch {state['dispatch']} for different inputs is still running; rerun "
                                f"with the same inputs to wait for it, or pass --abandon-pending", EXIT_CONFLICT)
        state["status"] = "abandoned"
        atomic_json(state_path, state)
    if not args.new:
        existing = identical_dispatch(root, entries, args.task, brief_sha)
        if existing is not None:
            print_dispatch(root, existing[0], existing[1], reused=True)
            return EXIT_OK
    n = next_number(root, work, args.task)
    brief_rel = f"{evidence_dir(args.task)}/brief-{n}.md"
    create_text(gate.local(root, brief_rel), brief)
    if gate.sha(gate.local(root, brief_rel)) != brief_sha and gate.text_sha(gate.local(root, brief_rel)) != brief_sha:
        raise DispatchError("Brief hash changed while writing; refusing to dispatch")
    state = {"schema": SCHEMA, "task_id": args.task, "review_of": prev["id"], "dispatch": n, "status": "active",
             "brief_path": brief_rel, "brief_sha256": brief_sha, "reviewed_inputs": inputs,
             "created_at": now_iso(), "attempts": []}
    state_path = work / f"dispatch-{n}.state.json"
    atomic_json(state_path, state)
    return drive(root, plan_dir, entries, task, config, state_path, state, args)


def main(argv=None) -> int:
    raw = list(sys.argv[1:] if argv is None else argv)
    if len(raw) == 2 and raw[0] == "--child":
        return child_main(raw[1])
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo-root", default=str(HERE.parents[3]))
    parser.add_argument("--task", required=True)
    parser.add_argument("--plan", default=gate.CONTROL.as_posix(), help="plan workspace relative to the repo root")
    parser.add_argument("--brief", help="optional focus note (<= 6000 bytes) appended to the generated brief")
    parser.add_argument("--input", action="append", help="extra repo-relative file to review (e.g. a new test)")
    parser.add_argument("--dry-run", action="store_true", help="print route, brief path and argv; no spend")
    parser.add_argument("--new", action="store_true", help="dispatch again even when an identical dispatch exists")
    parser.add_argument("--abandon-pending", action="store_true", help="abandon a running dispatch for older inputs")
    parser.add_argument("--provider", help="put this provider first (still read-only, max tier, chain-limited)")
    parser.add_argument("--wait-seconds", type=int, default=DEFAULT_WAIT,
                        help="foreground wait bound per call (0 = wait until done); exit 75 when exceeded")
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT, help="hard reviewer ceiling")
    args = parser.parse_args(raw)
    try:
        return run(args)
    except DispatchError as exc:
        print(f"REVIEW DISPATCH REFUSED: {exc}" if exc.code == EXIT_REFUSED else f"REVIEW DISPATCH ERROR: {exc}",
              file=sys.stderr)
        return exc.code
    except (gate.GateError, OSError, KeyError, TypeError, ValueError) as exc:
        print(f"REVIEW DISPATCH ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
