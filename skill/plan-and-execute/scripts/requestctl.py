#!/usr/bin/env python3
"""Create, open, validate, and read plan-and-execute request files.

The script uses only the Python standard library. Generated request drafts live
under .ai-work/intake, are hidden from git status when possible, and can be
opened in the active VS Code window or another local editor.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import inspect
import json
import os
import re
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

WORK_ROOT_DEFAULT = ".ai-work"
INTAKE_DIRECTORY = "intake"
INSTRUCTIONS_START = "<!-- plan-and-execute:intake-instructions:start -->"
INSTRUCTIONS_END = "<!-- plan-and-execute:intake-instructions:end -->"
REQUEST_START = "<!-- plan-and-execute:request:start -->"
REQUEST_END = "<!-- plan-and-execute:request:end -->"
BASELINE_SKILL_BYTES = 6955
MAX_REASON_CODES = 6
MAX_WORKING_SET_ITEMS = 16
MAX_REMAINING_OUTCOMES = 24
LIFECYCLE_COMMANDS = frozenset(
    {"current", "status", "resume", "continue", "cancel", "reset", "configure"}
)
ACTIVATION_REASON_CODES = frozenset(
    {
        "EXPLICIT_INVOCATION",
        "LIFECYCLE_COMMAND",
        "INDEPENDENT_WORKSTREAMS",
        "BROAD_STUDY",
        "CROSS_CUTTING_RISK",
        "DURABLE_RESUME_VALUE",
        "ISOLATION_VALUE",
        "LATE_PROMOTION_REMAINING_WORK",
        "HIGH_CONTEXT_SUBSTANTIAL_WORK",
        "COHESIVE_BOUNDED_WORK",
        "FILE_COUNT_WEAK_SIGNAL",
        "REPETITIVE_OR_LARGE_LOG",
        "NEAR_FINISHED_HIGH_CONTEXT",
        "UNCERTAIN_PREFER_DIRECT",
        "DIRECT_WITH_STRONG_CAPABILITY",
        "VALIDATE_OR_FIX_EXIT",
    }
)

TEMPLATES: dict[str, dict[str, str]] = {
    "en": {
        "title": "Plan and Execute — Request",
        "instructions": (
            "> **Write the complete request below.** Include the desired outcome, all requirements and activities, "
            "constraints or non-goals, compatibility or migration needs, and the tests or evidence that define success.\n"
            "> Save the file, return to the agent chat, and choose **Continue — I finished writing the request**. "
            "Keep the request markers in place."
        ),
        "goal": "Goal",
        "requirements": "Requirements and activities",
        "constraints": "Constraints and non-goals",
        "context": "Relevant context, files, links, or prior decisions",
        "validation": "Tests, validation, and definition of done",
        "notes": "Additional notes",
        "goal_hint": "Describe the final outcome and who benefits from it.",
        "requirements_hint": "List every behavior, deliverable, and activity the agent must complete.",
        "constraints_hint": "Include compatibility, security, performance, data, migration, rollout, and explicit exclusions.",
        "context_hint": "Point to relevant modules, files, issues, documentation, APIs, or examples.",
        "validation_hint": "State required automated tests, manual checks, acceptance criteria, and expected commands.",
        "notes_hint": "Add anything that must not be lost during planning.",
        "confirmation": "Continue — I finished writing the request",
    },
    "pt-BR": {
        "title": "Plan and Execute — Solicitação",
        "instructions": (
            "> **Escreva abaixo a solicitação completa.** Inclua o resultado desejado, todos os requisitos e atividades, "
            "restrições ou itens fora do escopo, necessidades de compatibilidade ou migração e os testes ou evidências que definem o sucesso.\n"
            "> Salve o arquivo, volte ao chat do agente e escolha **Continuar — terminei de escrever as instruções**. "
            "Mantenha os marcadores da solicitação."
        ),
        "goal": "Objetivo",
        "requirements": "Requisitos e atividades",
        "constraints": "Restrições e itens fora do escopo",
        "context": "Contexto, arquivos, links ou decisões anteriores",
        "validation": "Testes, validação e definição de pronto",
        "notes": "Observações adicionais",
        "goal_hint": "Descreva o resultado final e quem será beneficiado.",
        "requirements_hint": "Liste todos os comportamentos, entregáveis e atividades que o agente deve concluir.",
        "constraints_hint": "Inclua compatibilidade, segurança, desempenho, dados, migração, rollout e exclusões explícitas.",
        "context_hint": "Aponte módulos, arquivos, issues, documentação, APIs ou exemplos relevantes.",
        "validation_hint": "Informe testes automatizados, verificações manuais, critérios de aceite e comandos esperados.",
        "notes_hint": "Acrescente qualquer informação que não possa se perder durante o planejamento.",
        "confirmation": "Continuar — terminei de escrever as instruções",
    },
}


class RequestError(RuntimeError):
    """Raised when a request draft is missing, unsafe, or incomplete."""


def now_stamp() -> str:
    return dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False, newline="\n"
    ) as handle:
        handle.write(content)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def normalize_language(value: str | None, env: Mapping[str, str] | None = None) -> str:
    raw = str(value or "auto").strip()
    lowered = raw.lower().replace("_", "-")
    if lowered in {"pt", "pt-br", "ptbr", "portuguese", "portugues", "português"}:
        return "pt-BR"
    if lowered in {"en", "en-us", "en-gb", "english"}:
        return "en"
    if lowered != "auto":
        raise RequestError("Unsupported language. Use auto, en, or pt-BR.")
    locale = " ".join(
        (env or os.environ).get(name, "") for name in ("LC_ALL", "LC_MESSAGES", "LANG")
    ).lower()
    return "pt-BR" if re.search(r"\bpt(?:[_-]br)?\b", locale) else "en"


def render_template(language: str) -> str:
    text = TEMPLATES[language]
    sections = (
        (text["goal"], text["goal_hint"]),
        (text["requirements"], text["requirements_hint"]),
        (text["constraints"], text["constraints_hint"]),
        (text["context"], text["context_hint"]),
        (text["validation"], text["validation_hint"]),
        (text["notes"], text["notes_hint"]),
    )
    body = "\n\n".join(
        f"## {heading}\n\n<!-- {hint} -->" for heading, hint in sections
    )
    return (
        f"# {text['title']}\n\n"
        f"{INSTRUCTIONS_START}\n{text['instructions']}\n{INSTRUCTIONS_END}\n\n"
        f"{REQUEST_START}\n{body}\n{REQUEST_END}\n"
    )


def resolve_request_path(value: str | Path) -> Path:
    raw = Path(value).expanduser()
    path = Path(os.path.abspath(raw))
    try:
        metadata = path.lstat()
    except FileNotFoundError as exc:
        raise RequestError(f"Request file not found: {path}") from exc
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise RequestError(f"Request path must be a regular file, not a symlink: {path}")
    return path


def extract_request_text(text: str) -> str:
    start = text.find(REQUEST_START)
    end = text.find(REQUEST_END)
    if start >= 0 or end >= 0:
        if start < 0 or end < 0 or end <= start:
            raise RequestError("Request markers are incomplete or out of order.")
        start += len(REQUEST_START)
        return text[start:end].strip()
    return text.strip()


def meaningful_request_text(text: str) -> str:
    without_comments = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)
    without_headings = re.sub(r"(?m)^\s{0,3}#{1,6}\s+.*$", " ", without_comments)
    without_markdown = re.sub(r"(?m)^\s{0,3}(?:[-*+]\s+|>\s*)", "", without_headings)
    compact = re.sub(r"\s+", " ", without_markdown).strip()
    return compact


def inspect_request_file(value: str | Path) -> dict[str, Any]:
    path = resolve_request_path(value)
    raw = path.read_text(encoding="utf-8")
    body = extract_request_text(raw)
    meaningful = meaningful_request_text(body)
    ready = len(meaningful) >= 20 and len(re.findall(r"[\wÀ-ÿ]", meaningful)) >= 12
    return {
        "path": str(path),
        "ready": ready,
        "request_text": body,
        "meaningful_text": meaningful,
        "request_characters": len(body),
        "meaningful_characters": len(meaningful),
        "generated_template": REQUEST_START in raw and REQUEST_END in raw,
    }


def _candidate_exists(command: Sequence[str], which: Callable[[str], str | None]) -> bool:
    executable = command[0]
    if os.path.isabs(executable) or os.sep in executable:
        return Path(executable).exists()
    return which(executable) is not None


def choose_editor_command(
    file_path: Path,
    *,
    explicit_editor: str | None = None,
    env: Mapping[str, str] | None = None,
    platform_name: str | None = None,
    which: Callable[[str], str | None] = shutil.which,
) -> tuple[list[str] | None, str | None]:
    environment = dict(env or os.environ)
    platform_value = platform_name or sys.platform

    if explicit_editor:
        command = shlex.split(explicit_editor)
        if not command:
            raise RequestError("--editor cannot be empty")
        return [*command, str(file_path)], command[0]

    in_vscode = any(
        environment.get(name)
        for name in ("VSCODE_PID", "VSCODE_CWD", "VSCODE_IPC_HOOK_CLI")
    ) or environment.get("TERM_PROGRAM", "").lower() == "vscode"
    if in_vscode:
        for executable in ("code", "code-insiders"):
            command = [executable, "--reuse-window", str(file_path)]
            if _candidate_exists(command, which):
                return command, executable

    for variable in ("VISUAL", "EDITOR"):
        configured = environment.get(variable)
        if configured:
            command = shlex.split(configured)
            if command and _candidate_exists(command, which):
                return [*command, str(file_path)], command[0]

    if platform_value.startswith("win"):
        command = ["notepad.exe", str(file_path)]
        return (command, "notepad.exe") if _candidate_exists(command, which) else (None, None)
    if platform_value == "darwin":
        command = ["open", "-t", str(file_path)]
        return (command, "open") if _candidate_exists(command, which) else (None, None)

    command = ["xdg-open", str(file_path)]
    return (command, "xdg-open") if _candidate_exists(command, which) else (None, None)


def launch_editor(command: Sequence[str] | None) -> tuple[bool, str | None]:
    if not command:
        return False, "No supported editor command was found."
    try:
        kwargs: dict[str, Any] = {
            "stdin": subprocess.DEVNULL,
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
            "close_fds": os.name != "nt",
        }
        launch = list(command)
        if os.name == "nt":
            kwargs["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            # `code`/`code-insiders` are .cmd shims on Windows; CreateProcess
            # needs the resolved file, not the bare name.
            if launch and not os.path.isabs(launch[0]) and os.sep not in launch[0]:
                resolved = shutil.which(launch[0])
                if resolved:
                    launch[0] = resolved
        else:
            kwargs["start_new_session"] = True
        subprocess.Popen(launch, **kwargs)
        return True, None
    except OSError as exc:
        return False, str(exc)


def _ensure_safe_work_root(repo_root: Path, work_root: str) -> Path:
    relative = Path(work_root)
    if relative.is_absolute() or ".." in relative.parts:
        raise RequestError("work_root must be repository-relative")
    current = repo_root
    for part in relative.parts:
        current = current / part
        if current.exists() and current.is_symlink():
            raise RequestError(f"work_root must not traverse a symlink: {current}")
    return repo_root / relative


def create_request_file(
    repo_root: Path,
    *,
    work_root: str = WORK_ROOT_DEFAULT,
    language: str = "auto",
) -> tuple[Path, str]:
    root = repo_root.expanduser().resolve()
    if not root.is_dir():
        raise RequestError(f"Repository root is not a directory: {root}")
    normalized_language = normalize_language(language)
    work_directory = _ensure_safe_work_root(root, work_root)
    intake = work_directory / INTAKE_DIRECTORY
    intake.mkdir(parents=True, exist_ok=True)
    if intake.is_symlink():
        raise RequestError(f"Intake directory must not be a symlink: {intake}")

    candidate = intake / f"request-{now_stamp()}.md"
    counter = 2
    while candidate.exists():
        candidate = intake / f"request-{now_stamp()}-{counter}.md"
        counter += 1
    atomic_write_text(candidate, render_template(normalized_language))

    try:
        import planctl  # Imported lazily to avoid a module cycle.

        planctl.ensure_git_exclude(root, work_root)
    except (ImportError, OSError):
        pass
    return candidate.resolve(), normalized_language


def latest_request_file(repo_root: Path, work_root: str = WORK_ROOT_DEFAULT) -> Path:
    root = repo_root.expanduser().resolve()
    intake = _ensure_safe_work_root(root, work_root) / INTAKE_DIRECTORY
    if not intake.is_dir() or intake.is_symlink():
        raise RequestError("No request draft exists yet.")
    candidates = sorted(
        (path for path in intake.glob("*.md") if path.is_file() and not path.is_symlink()),
        key=lambda path: (path.stat().st_mtime_ns, path.name),
        reverse=True,
    )
    if not candidates:
        raise RequestError("No request draft exists yet.")
    return candidates[0].resolve()


def command_create(args: argparse.Namespace) -> None:
    path, language = create_request_file(
        Path(args.repo_root), work_root=args.work_root, language=args.language
    )
    command, editor = choose_editor_command(path, explicit_editor=args.editor)
    opened, editor_error = (False, None)
    if not args.no_open:
        opened, editor_error = launch_editor(command)
    payload = {
        "path": str(path),
        "language": language,
        "opened": opened,
        "editor": editor,
        "editor_command": command,
        "editor_error": editor_error,
        "confirmation_label": TEMPLATES[language]["confirmation"],
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(path)
        if opened:
            print(f"Opened with {editor}.")
        elif not args.no_open:
            print(f"Editor was not opened: {editor_error or 'unknown error'}", file=sys.stderr)
        print(TEMPLATES[language]["confirmation"])


def command_validate(args: argparse.Namespace) -> None:
    result = inspect_request_file(args.file)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("READY" if result["ready"] else "NOT_READY")
        print(result["path"])
    if not result["ready"]:
        raise SystemExit(2)


def command_extract(args: argparse.Namespace) -> None:
    result = inspect_request_file(args.file)
    if not result["ready"] and not args.allow_incomplete:
        raise RequestError(
            "The request file still contains no meaningful instructions. Fill it in and save it first."
        )
    print(result["request_text"])


def command_latest(args: argparse.Namespace) -> None:
    path = latest_request_file(Path(args.repo_root), args.work_root)
    result = inspect_request_file(path)
    payload = {key: value for key, value in result.items() if key != "request_text"}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(path)


def command_reopen(args: argparse.Namespace) -> None:
    path = resolve_request_path(args.file)
    command, editor = choose_editor_command(path, explicit_editor=args.editor)
    opened, error = launch_editor(command)
    payload = {
        "path": str(path),
        "opened": opened,
        "editor": editor,
        "editor_command": command,
        "editor_error": error,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(path)
        if not opened:
            raise RequestError(f"Could not open the editor: {error or 'no supported editor found'}")


def _minimum_route_for_signals(signals: Sequence[str]) -> dict[str, str]:
    scripts_dir = str(Path(__file__).resolve().parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    import routingctl  # noqa: E402

    try:
        return routingctl.minimum_route(list(signals))
    except routingctl.RoutingError as exc:
        raise RequestError(str(exc)) from exc


def _bound_reason_codes(codes: Sequence[str]) -> list[str]:
    bounded: list[str] = []
    for code in codes:
        if code not in ACTIVATION_REASON_CODES:
            raise RequestError(f"Unknown activation reason code: {code}")
        if code not in bounded:
            bounded.append(code)
        if len(bounded) >= MAX_REASON_CODES:
            break
    return bounded


def _normalize_working_set(value: Sequence[str] | int | None) -> dict[str, Any]:
    if isinstance(value, bool):
        raise RequestError("estimated_working_set must be an integer or list of paths")
    if isinstance(value, int):
        if value < 0:
            raise RequestError("estimated_working_set count cannot be negative")
        return {"count": value, "items": []}
    if value is None:
        return {"count": 0, "items": []}
    items = [str(item).strip() for item in value if str(item).strip()]
    return {"count": len(items), "items": items[:MAX_WORKING_SET_ITEMS]}


PROMOTION_REFERENCE = "references/PROMOTION.md"
ORCHESTRATION_REFERENCE = "references/ORCHESTRATION.md"
VALIDATION_REFERENCE = "references/VALIDATION_WORKLOADS.md"
NEAR_FINISHED_OVERRIDE_CODES = frozenset({"EXPLICIT_INVOCATION"})


def near_finished_stays_direct(
    *,
    nearly_finished: bool,
    cohesive: bool,
    remaining_count: int,
    reason_codes: Sequence[str] = (),
) -> bool:
    """Shared late-promotion rule for requestctl and promotectl.

    Nearly finished cohesive work with at most one remaining outcome stays DIRECT
    (no plan, ledger or handoff) unless the user explicitly invoked the skill.
    """
    return bool(
        nearly_finished
        and cohesive
        and remaining_count <= 1
        and not (set(reason_codes) & NEAR_FINISHED_OVERRIDE_CODES)
    )


def _capability_signals(
    *,
    security_sensitive: bool,
    cross_cutting_risk: bool,
    weak_validation: bool,
    capability_signals: Sequence[str] | None,
) -> list[str]:
    """Capability floor signals. Caller overrides may raise the floor, never drop a risk signal."""
    risk: list[str] = []
    if security_sensitive:
        risk.append("silent_failure_costly")
    if cross_cutting_risk:
        risk.append("cross_cutting_risk")
    if weak_validation:
        risk.append("weak_validation")
    if capability_signals:
        if isinstance(capability_signals, str):
            raise RequestError("capability_signals must be a list of routing signals")
        base = [str(item).strip().lower() for item in capability_signals if str(item).strip()]
        return base + [signal for signal in risk if signal not in base]
    if security_sensitive:
        return ["silent_failure_costly", "implementation", *(["weak_validation"] if weak_validation else [])]
    if cross_cutting_risk:
        return ["cross_cutting_risk", "implementation"]
    if weak_validation:
        return ["bounded_implementation", "weak_validation"]
    return ["bounded_implementation"]


def _decision(
    route: str,
    codes: Sequence[str],
    *,
    persist: bool,
    working_set: dict[str, Any],
    outcomes: list[str],
    capability_route: dict[str, Any],
    load_references: Sequence[str] = (),
    validate_or_fix: bool = False,
) -> dict[str, Any]:
    reason_codes = _bound_reason_codes(codes)
    return {
        "schema_version": 1,
        "route": route,
        "persist_plan": persist,
        "reason_codes": reason_codes,
        "persisted_reason_codes": list(reason_codes) if persist else [],
        "estimated_working_set": working_set,
        "remaining_outcomes": outcomes,
        "capability_route": capability_route,
        "load_references": list(load_references),
        "validate_or_fix": bool(validate_or_fix),
        "classifier_call": False,
    }


def evaluate_activation(
    *,
    explicit_invocation: bool = False,
    lifecycle_command: str | None = None,
    already_direct: bool = False,
    independent_workstreams: int = 1,
    needs_broad_study: bool = False,
    cross_cutting_risk: bool = False,
    durable_resume_value: bool = False,
    isolation_value: bool = False,
    cohesive_single_outcome: bool = True,
    estimated_working_set: Sequence[str] | int | None = None,
    remaining_outcomes: Sequence[str] | None = None,
    context_used_percentage: float | None = None,
    nearly_finished: bool = False,
    security_sensitive: bool = False,
    weak_validation: bool = False,
    repetitive_log: bool = False,
    needs_validate_or_fix: bool = False,
    capability_signals: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Deterministically route DIRECT vs ORCHESTRATED vs PROMOTE without a classifier call.

    A pure function of structured request metadata: it reads and writes no files.
    Routing mode is separate from capability tier, so a cohesive security-sensitive
    fix stays DIRECT with a strong implementation floor. Only an activated
    ORCHESTRATED/PROMOTE route returns reason codes to persist.
    """
    working_set = _normalize_working_set(estimated_working_set)
    outcomes = [str(item).strip() for item in (remaining_outcomes or []) if str(item).strip()][
        :MAX_REMAINING_OUTCOMES
    ]
    common = {"working_set": working_set, "outcomes": outcomes}

    normalized_lifecycle = str(lifecycle_command or "").strip().lower()
    if normalized_lifecycle:
        if normalized_lifecycle not in LIFECYCLE_COMMANDS:
            raise RequestError(f"Unsupported lifecycle/config command: {normalized_lifecycle}")
        return _decision(
            "lifecycle",
            ["LIFECYCLE_COMMAND"],
            persist=False,
            capability_route=_minimum_route_for_signals(["deterministic_lookup"]),
            **common,
        )

    capability_route = _minimum_route_for_signals(
        _capability_signals(
            security_sensitive=security_sensitive,
            cross_cutting_risk=cross_cutting_risk,
            weak_validation=weak_validation,
            capability_signals=capability_signals,
        )
    )
    common["capability_route"] = capability_route

    strong_reasons: list[str] = []
    if independent_workstreams >= 2:
        strong_reasons.append("INDEPENDENT_WORKSTREAMS")
    if needs_broad_study:
        strong_reasons.append("BROAD_STUDY")
    if cross_cutting_risk:
        strong_reasons.append("CROSS_CUTTING_RISK")
    if durable_resume_value:
        strong_reasons.append("DURABLE_RESUME_VALUE")
    if isolation_value:
        strong_reasons.append("ISOLATION_VALUE")

    if explicit_invocation:
        route = "promote" if already_direct else "orchestrated"
        codes = ["EXPLICIT_INVOCATION", *strong_reasons]
        if route == "promote":
            codes.insert(1, "LATE_PROMOTION_REMAINING_WORK")
        reference = PROMOTION_REFERENCE if route == "promote" else ORCHESTRATION_REFERENCE
        return _decision(route, codes, persist=True, load_references=[reference], **common)

    validation_refs = [VALIDATION_REFERENCE] if needs_validate_or_fix else []
    if already_direct and near_finished_stays_direct(
        nearly_finished=nearly_finished,
        cohesive=cohesive_single_outcome,
        remaining_count=len(outcomes),
    ):
        codes = ["NEAR_FINISHED_HIGH_CONTEXT", "COHESIVE_BOUNDED_WORK"]
        if security_sensitive:
            codes.append("DIRECT_WITH_STRONG_CAPABILITY")
        if needs_validate_or_fix:
            codes.append("VALIDATE_OR_FIX_EXIT")
        return _decision(
            "direct", codes, persist=False, load_references=validation_refs,
            validate_or_fix=needs_validate_or_fix, **common,
        )

    if strong_reasons:
        if already_direct:
            codes = ["LATE_PROMOTION_REMAINING_WORK", *strong_reasons]
            if context_used_percentage is not None and context_used_percentage >= 75:
                codes.append("HIGH_CONTEXT_SUBSTANTIAL_WORK")
            return _decision("promote", codes, persist=True, load_references=[PROMOTION_REFERENCE], **common)
        return _decision(
            "orchestrated", strong_reasons, persist=True, load_references=[ORCHESTRATION_REFERENCE], **common
        )

    direct_codes: list[str] = []
    if already_direct and nearly_finished:
        direct_codes.append("NEAR_FINISHED_HIGH_CONTEXT")
    if cohesive_single_outcome:
        direct_codes.append("COHESIVE_BOUNDED_WORK")
    if working_set["count"] >= 5:
        direct_codes.append("FILE_COUNT_WEAK_SIGNAL")
    if repetitive_log:
        direct_codes.append("REPETITIVE_OR_LARGE_LOG")
    if security_sensitive:
        direct_codes.append("DIRECT_WITH_STRONG_CAPABILITY")
    if needs_validate_or_fix:
        direct_codes.append("VALIDATE_OR_FIX_EXIT")
    if not direct_codes:
        direct_codes.append("UNCERTAIN_PREFER_DIRECT")
    return _decision(
        "direct", direct_codes, persist=False, load_references=validation_refs,
        validate_or_fix=needs_validate_or_fix, **common,
    )


ACTIVATION_SIGNAL_KEYS = frozenset(inspect.signature(evaluate_activation).parameters)

_SKILL_NAME = r"plan-and-execute(?![\w-]|[./\\]\w)"
_TOKEN_START = r"(?:^|[\s\"'(`])"
_COUNT = r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)"
_WORD_NUMBERS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}

# Frozen cue table of the OFFLINE activation proxy: regular expressions over the lower-cased prompt.
# Hosts select the skill from SKILL.md metadata, not from this table, so proxy rates never measure
# host activation. Changing any entry invalidates the held-out split of routing-evals.json: move the
# held-out cases seen while tuning to the tuning split, have fresh held-out prompts written without
# access to this table, and record the new cue_table_sha256() in `held_out_protocol`.
ACTIVATION_CUES: dict[str, tuple[str, ...]] = {
    "lifecycle_command": (
        _TOKEN_START + r"(?:[$/]?" + _SKILL_NAME + r"|pae)\s+(current|status|resume|continue|cancel|reset|configure)\b",
        r"\b(resume|continue|cancel|reset)\s+(?:the\s+)?(?:active\s+|current\s+)?[$/]?" + _SKILL_NAME,
        r"\b(resume|continue|cancel|reset)\s+(?:the\s+)?(?:active|persisted)\s+(?:plan|implementation|workflow|todo)\b",
    ),
    "explicit_invocation": (
        _TOKEN_START + r"[$/]" + _SKILL_NAME,
        r"\b(?:use|using|run|invoke|via|with)\s+(?:the\s+)?[$/]?" + _SKILL_NAME,
    ),
    "already_direct": (
        r"\bdirect work\b",
        r"\bstarted directly\b",
        r"\bworking directly\b",
        r"\balready[- ](?:implemented|completed|applied)\b",
        r"\b(?:partway|midway|halfway) through\b",
    ),
    "context_marker": (r"\bcontext\b",),
    "near_finished_marker": (
        r"\btiny\b",
        r"\bonly one\b",
        r"\bjust one\b",
        r"\bnearly finished\b",
        r"\balmost (?:done|finished)\b",
        r"\blast (?:small|remaining)\b",
    ),
    "remaining_marker": (r"\bremains?\b", r"\bremaining\b", r"\bleft\b"),
    "independent_workstreams": (
        r"\bunrelated\b.*\band\b",
        r"\b" + _COUNT + r"\s+(?:\w+\s+)?independent\s+(?:modules|integrations|subsystems|workstreams|domains|"
        r"services|components|features|applications|apps|repositories|packages)\b",
        r"\bindependent\s+(?:subsystems|workstreams)\b",
    ),
    "broad_study": (
        r"\bbroadly\b",
        r"\bauthoritative sources\b",
        r"\bbroad (?:vendor )?research\b",
        r"\b(?:study|survey|audit) the (?:whole|entire) (?:repository|repo|codebase)\b",
        r"\bexternal (?:vendor )?(?:docs|documentation)\b",
        r"\b(?:compare|evaluate)\s+(?:\w+\s+){0,3}(?:vendors|providers|libraries|frameworks|alternatives)\b",
    ),
    "cross_cutting_risk": (
        r"\b(?:protocol|compatibility) migration\b",
        r"\b(?:incompatible|breaking)\s+(?:\w+\s+){0,2}(?:schema|data|protocol|api)\s+(?:migration|change)\b",
        r"\bmigrate\s+[^.]+,\s*[^.]+\s+and\s+",
        r"\brollback-sensitive\b",
    ),
    "durable_resume_value": (
        r"\bmulti-session\b",
        r"\b(?:across|multiple|several) sessions\b",
        r"\bcredits run out\b",
        r"\bquota (?:windows|resets?)\b",
        r"\bdurable todo\b",
        r"\bsurvive (?:an )?interruptions?\b",
    ),
    "isolation_value": (
        r"\bisolated worktrees?\b",
        r"\bseparate worktrees\b",
        r"\bcontext isolation\b",
    ),
    "security_sensitive": (
        r"\bjwt\b",
        r"\bsignature verification\b",
        r"\bsecurity[- ]sensitive\b",
        r"\b(?:authorization|authentication|auth) bypass\b",
        r"\bprivilege escalation\b",
        r"\b(?:csrf|xss|ssrf)\b",
        r"\b(?:sql|command) injection\b",
        r"\bpath traversal\b",
        r"\b(?:secrets?|credentials?|passwords?)\b",
        r"\baccess control\b",
        r"\bpermission checks?\b",
        r"\bvulnerab",
        r"\bcve-\d",
        r"\b(?:encryption|tls|certificates?)\b",
        r"\bsanitiz",
        r"\btoken (?:verification|validation)\b",
    ),
    "repetitive_log": (r"\b(?:repetitive|huge|massive|verbose|[\d,]+-line)\b[^.]{0,40}\blogs?\b",),
    "file_count": (r"\b(" + _COUNT + r")\s+(?:related\s+)?(?:files|call sites)\b",),
    "context_percentage": (r"(\d{1,3})\s*%\s*context|\bcontext\b[^.]{0,20}?(\d{1,3})\s*%",),
}
_COMPILED_CUES = {name: tuple(re.compile(pattern) for pattern in patterns) for name, patterns in ACTIVATION_CUES.items()}


def cue_table_sha256() -> str:
    """Hash of the frozen cue table recorded by the held-out protocol of routing-evals.json."""
    payload = json.dumps(ACTIVATION_CUES, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _cue(name: str, text: str) -> re.Match[str] | None:
    for pattern in _COMPILED_CUES[name]:
        match = pattern.search(text)
        if match:
            return match
    return None


def extract_prompt_signals(prompt: str) -> dict[str, Any]:
    """Deterministically extract activation metadata from prompt text (offline proxy, no LLM).

    Lifecycle/config commands are recognized first and never count as explicit invocation;
    a plain mention of the skill name (for example a file path) is not an invocation.
    """
    lower = " ".join(str(prompt or "").lower().split())
    lifecycle_match = _cue("lifecycle_command", lower)
    lifecycle = lifecycle_match.group(1) if lifecycle_match else None
    explicit = lifecycle is None and _cue("explicit_invocation", lower) is not None
    nearly_finished = all(_cue(name, lower) for name in ("context_marker", "near_finished_marker", "remaining_marker"))
    already_direct = nearly_finished or _cue("already_direct", lower) is not None
    independent = 2 if _cue("independent_workstreams", lower) else 1
    broad_study = _cue("broad_study", lower) is not None
    cross_cutting = _cue("cross_cutting_risk", lower) is not None
    count_match = _cue("file_count", lower)
    file_count = 0
    if count_match:
        token = count_match.group(1)
        file_count = int(token) if token.isdigit() else _WORD_NUMBERS[token]
    ctx_match = _cue("context_percentage", lower)
    ctx_pct = float(ctx_match.group(1) or ctx_match.group(2)) if ctx_match else None
    text = " ".join(str(prompt or "").split())
    return {
        "explicit_invocation": explicit,
        "lifecycle_command": lifecycle,
        "already_direct": already_direct,
        "independent_workstreams": independent,
        "needs_broad_study": broad_study,
        "cross_cutting_risk": cross_cutting,
        "durable_resume_value": _cue("durable_resume_value", lower) is not None,
        "isolation_value": _cue("isolation_value", lower) is not None,
        "cohesive_single_outcome": independent < 2 and not broad_study and not cross_cutting,
        "estimated_working_set": file_count,
        "remaining_outcomes": [text] if text else [],
        "context_used_percentage": ctx_pct,
        "nearly_finished": nearly_finished,
        "security_sensitive": _cue("security_sensitive", lower) is not None,
        "repetitive_log": _cue("repetitive_log", lower) is not None,
    }


POSITIVE_ROUTES = frozenset({"orchestrated", "promote"})
EXPECTED_ROUTES = frozenset({"direct", "orchestrated", "promote", "lifecycle"})
ROUTING_ALTERNATIVES = ("selective_cue_proxy", "explicit_only", "all_direct", "always_orchestrate")


def _alternative_routes(signals: dict[str, Any], decision: dict[str, Any]) -> dict[str, str]:
    """Routes of the compared alternatives. Exact lifecycle commands stay deterministic in all of them."""
    if decision["route"] == "lifecycle":
        return {name: "lifecycle" for name in ROUTING_ALTERNATIVES}
    activated = "promote" if signals.get("already_direct") else "orchestrated"
    return {
        "selective_cue_proxy": decision["route"],
        "explicit_only": activated if signals.get("explicit_invocation") else "direct",
        "all_direct": "direct",
        "always_orchestrate": activated,
    }


def _score_predictions(rows: list[tuple[dict[str, Any], str]]) -> dict[str, Any]:
    """Exact route accuracy plus binary plan-creation errors (positive = orchestrated/promote)."""
    total = len(rows)
    tp = fp = tn = fn = exact = near_miss_total = near_miss_fp = 0
    for case, pred in rows:
        expected = case["expected_route"]
        exp_pos = expected in POSITIVE_ROUTES
        pred_pos = pred in POSITIVE_ROUTES
        if pred == expected:
            exact += 1
        if exp_pos and pred_pos:
            tp += 1
        elif not exp_pos and pred_pos:
            fp += 1
            if case.get("near_miss"):
                near_miss_fp += 1
        elif exp_pos and not pred_pos:
            fn += 1
        else:
            tn += 1
        if case.get("near_miss") and not exp_pos:
            near_miss_total += 1
    negatives = tn + fp
    positives = tp + fn
    return {
        "total": total,
        "exact_match": exact,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "accuracy": round(exact / total, 4) if total else 0.0,
        "false_positive_rate": round(fp / negatives, 4) if negatives else 0.0,
        "false_negative_rate": round(fn / positives, 4) if positives else 0.0,
        "near_miss_negative_count": near_miss_total,
        "near_miss_false_positive_rate": round(near_miss_fp / near_miss_total, 4) if near_miss_total else 0.0,
    }


def _held_out_integrity(protocol: Mapping[str, Any] | None) -> dict[str, Any]:
    current = cue_table_sha256()
    recorded = protocol.get("cue_table_sha256") if isinstance(protocol, Mapping) else None
    if not recorded:
        status = "unrecorded"
    elif recorded == current:
        status = "frozen"
    else:
        status = "stale_cue_table"
    return {"status": status, "recorded_cue_table_sha256": recorded, "current_cue_table_sha256": current}


def evaluate_routing_corpus(
    cases: Sequence[dict[str, Any]],
    *,
    skill_root: Path | None = None,
    protocol: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Measure entrypoint bytes and the offline cue-extractor proxy on routing-evals.json.

    Reports exact accuracy and plan-creation FP/FN for four computed alternatives on the
    tuning and held-out splits. The paid classifier and every cost term stay unmeasured.
    """
    root = (skill_root or Path(__file__).resolve().parents[1]).resolve()
    entrypoint_paths = {
        "SKILL.md": root / "SKILL.md",
        "agents/openai.yaml": root / "agents" / "openai.yaml",
        "references/ROUTING.md": root / "references" / "ROUTING.md",
        "references/PROMOTION.md": root / "references" / "PROMOTION.md",
    }
    entrypoint_bytes = {
        name: len(path.read_bytes().replace(b"\r\n", b"\n"))
        for name, path in entrypoint_paths.items()
        if path.is_file()
    }
    skill_bytes = entrypoint_bytes.get("SKILL.md", 0)

    rows: dict[str, dict[str, list[tuple[dict[str, Any], str]]]] = {
        split: {name: [] for name in ROUTING_ALTERNATIVES} for split in ("all_cases", "tuning", "held_out")
    }
    held_out_errors: list[dict[str, Any]] = []
    capability_checks: list[dict[str, Any]] = []
    for case in cases:
        if case.get("expected_route") not in EXPECTED_ROUTES:
            raise RequestError(f"routing eval case {case.get('id')} has an unsupported expected_route")
        split = "held_out" if case.get("split") == "held_out" else "tuning"
        signals = extract_prompt_signals(case["prompt"])
        decision = evaluate_activation(**signals)
        for name, route in _alternative_routes(signals, decision).items():
            rows["all_cases"][name].append((case, route))
            rows[split][name].append((case, route))
        if split == "held_out" and decision["route"] != case["expected_route"]:
            held_out_errors.append(
                {"id": case["id"], "expected": case["expected_route"], "predicted": decision["route"]}
            )
        if case.get("expected_min_tier"):
            capability_checks.append(
                {
                    "id": case["id"],
                    "split": split,
                    "route": decision["route"],
                    "expected_min_tier": case["expected_min_tier"],
                    "actual_tier": decision["capability_route"]["tier"],
                    "actual_effort": decision["capability_route"]["effort"],
                }
            )

    scores = {
        split: {name: _score_predictions(items) for name, items in by_alternative.items()}
        for split, by_alternative in rows.items()
    }
    held = scores["held_out"]
    return {
        "schema_version": 2,
        "metric": "offline_cue_extractor_proxy",
        "metric_note": (
            "Rates come from requestctl's deterministic cue extractor over prompt text. Hosts select the skill "
            "from SKILL.md metadata, so these rates do not measure host activation; no offline proxy exists "
            "for the 0.11.0 SKILL.md description."
        ),
        "held_out_integrity": _held_out_integrity(protocol),
        "entrypoint_bytes": entrypoint_bytes,
        "baseline_skill_bytes": BASELINE_SKILL_BYTES,
        "skill_byte_delta": skill_bytes - BASELINE_SKILL_BYTES,
        **scores,
        "held_out_errors": held_out_errors,
        "capability_preservation": capability_checks,
        "expected_cost_model": {
            "formula": "E[C] = C_select + P(FP)*C_unneeded_plan + P(FN)*C_recovery",
            "status": "costs_unmeasured",
            "note": "Only held-out P(FP)/P(FN) are measured offline; unknown costs stay unknown, not zero.",
            "c_select": {
                "selective_cue_proxy": "0 model calls (deterministic)",
                "explicit_only": "0 model calls",
                "all_direct": "0 model calls",
                "always_orchestrate": "0 model calls",
                "paid_classifier": "1 model call per request (unpriced)",
            },
            "c_unneeded_plan": None,
            "c_recovery": None,
            "held_out_probabilities": {
                name: {
                    "p_false_positive": held[name]["false_positive_rate"],
                    "p_false_negative": held[name]["false_negative_rate"],
                }
                for name in ROUTING_ALTERNATIVES
            },
            "paid_classifier": "unmeasured",
        },
        "live_host_evaluation": {
            "status": "unmeasured_limitation",
            "reason": "Live host skill loading and latency require owner-confirmed authenticated provider runs.",
        },
    }


def command_evaluate_route(args: argparse.Namespace) -> None:
    if args.spec:
        raw = json.loads(Path(args.spec).read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise RequestError("route evaluation spec must be a JSON object")
        unknown = sorted(set(raw) - ACTIVATION_SIGNAL_KEYS)
        if unknown:
            raise RequestError(f"Unknown route evaluation fields: {', '.join(unknown)}")
        try:
            result = evaluate_activation(**raw)
        except (TypeError, ValueError) as exc:
            raise RequestError(f"Invalid route evaluation spec: {exc}") from exc
    else:
        prompt = args.prompt or ""
        signals = extract_prompt_signals(prompt) if prompt else {}
        if args.security_sensitive:
            signals["security_sensitive"] = True
        if args.explicit_invocation:
            signals["explicit_invocation"] = True
        if args.lifecycle_command:
            signals["lifecycle_command"] = args.lifecycle_command
        result = evaluate_activation(**signals)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"{result['route']} tier={result['capability_route']['tier']}/{result['capability_route']['effort']} codes={','.join(result['reason_codes'])}")


def command_eval_corpus(args: argparse.Namespace) -> None:
    corpus_path = Path(args.corpus) if args.corpus else (Path(__file__).resolve().parents[1] / "references" / "routing-evals.json")
    payload = json.loads(corpus_path.read_text(encoding="utf-8"))
    result = evaluate_routing_corpus(payload["cases"], protocol=payload.get("held_out_protocol"))
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    print(f"metric={result['metric']} held_out_integrity={result['held_out_integrity']['status']}")
    for name in ROUTING_ALTERNATIVES:
        held = result["held_out"][name]
        print(f"held_out {name}: accuracy={held['accuracy']} FP={held['false_positive_rate']} FN={held['false_negative_rate']}")
    print("held_out paid_classifier: unmeasured")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create", help="Create a request draft and open it in an editor")
    create.add_argument("--repo-root", default=".")
    create.add_argument("--work-root", default=WORK_ROOT_DEFAULT)
    create.add_argument("--language", default="auto")
    create.add_argument("--editor")
    create.add_argument("--no-open", action="store_true")
    create.add_argument("--json", action="store_true")
    create.set_defaults(func=command_create)

    validate = sub.add_parser("validate", help="Check that a request file has meaningful content")
    validate.add_argument("--file", required=True)
    validate.add_argument("--json", action="store_true")
    validate.set_defaults(func=command_validate)

    extract = sub.add_parser("extract", help="Print only the user-authored request body")
    extract.add_argument("--file", required=True)
    extract.add_argument("--allow-incomplete", action="store_true")
    extract.set_defaults(func=command_extract)

    latest = sub.add_parser("latest", help="Find the newest generated request draft")
    latest.add_argument("--repo-root", default=".")
    latest.add_argument("--work-root", default=WORK_ROOT_DEFAULT)
    latest.add_argument("--json", action="store_true")
    latest.set_defaults(func=command_latest)

    reopen = sub.add_parser("reopen", help="Open an existing request file in the preferred editor")
    reopen.add_argument("--file", required=True)
    reopen.add_argument("--editor")
    reopen.add_argument("--json", action="store_true")
    reopen.set_defaults(func=command_reopen)

    eval_route = sub.add_parser("evaluate-route", help="Evaluate DIRECT vs ORCHESTRATED vs PROMOTE without side effects")
    eval_route.add_argument("--spec", help="JSON file of structured activation signals")
    eval_route.add_argument("--prompt", help="Prompt text for deterministic cue extraction")
    eval_route.add_argument("--security-sensitive", action="store_true")
    eval_route.add_argument("--explicit-invocation", action="store_true")
    eval_route.add_argument("--lifecycle-command")
    eval_route.add_argument("--json", action="store_true")
    eval_route.set_defaults(func=command_evaluate_route)

    eval_corpus = sub.add_parser("eval-corpus", help="Measure entrypoint bytes and offline FP/FN rates on routing-evals.json")
    eval_corpus.add_argument("--corpus", help="Optional path to routing-evals.json")
    eval_corpus.add_argument("--json", action="store_true")
    eval_corpus.set_defaults(func=command_eval_corpus)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
        return 0
    except RequestError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
