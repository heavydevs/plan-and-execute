#!/usr/bin/env python3
"""Create, open, validate, and read plan-and-execute request files.

The script uses only the Python standard library. Generated request drafts live
under .ai-work/intake, are hidden from git status when possible, and can be
opened in the active VS Code window or another local editor.
"""

from __future__ import annotations

import argparse
import datetime as dt
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
        if os.name == "nt":
            kwargs["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        else:
            kwargs["start_new_session"] = True
        subprocess.Popen(list(command), **kwargs)
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
