#!/usr/bin/env python3
"""Maintain the compact, project-local test resource router."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
ALGORITHM = "sha256-path-content-v2-streamed"
MAP_BEGIN = "<!-- pae-service-map:begin -->"
MAP_END = "<!-- pae-service-map:end -->"
MAP_BLOCK = re.compile(
    re.escape(MAP_BEGIN) + r"\s*```json\s*(.*?)\s*```\s*" + re.escape(MAP_END),
    re.DOTALL,
)
SKIP_PARTS = {
    ".git", ".ai-work", ".venv", "venv", "node_modules", "vendor", "target",
    "build", "dist", "out", "coverage", "__pycache__", ".gradle", ".idea",
}
SECRET_NAMES = {".env", ".env.local", ".env.production", "secrets.yml", "secrets.yaml"}
KNOWN_FILES = {
    "makefile", "dockerfile", "jenkinsfile", "procfile", "pom.xml", "build.gradle",
    "build.gradle.kts", "settings.gradle", "settings.gradle.kts", "gradlew", "mvnw",
    "package.json", "npm-shrinkwrap.json", "pnpm-workspace.yaml", "bun.lock", "bun.lockb",
    ".nvmrc", ".node-version", ".python-version", ".tool-versions", ".mise.toml",
    ".npmrc", ".yarnrc", ".yarnrc.yml", ".pnpmfile.cjs", "bunfig.toml",
    "pyproject.toml", "pytest.ini", "conftest.py",
    "tox.ini", "setup.cfg", "setup.py", "noxfile.py", "uv.toml", "requirements.in",
    "requirements.txt", "pipfile", "cargo.toml", "go.mod", "gemfile", "composer.json",
    "testng.xml", "junit-platform.properties", "playwright.config.ts", "playwright.config.js",
    "playwright.config.mjs", "playwright.config.cjs", "playwright.config.mts", "playwright.config.cts",
    "cypress.config.ts", "cypress.config.js", "vitest.config.ts", "vitest.config.js", "vitest.config.mjs",
    "vitest.config.cjs", "jest.config.js", "jest.config.ts", "jest.config.mjs", "jest.config.cjs",
    "jest.config.mts", "jest.config.cts",
    "azure-pipelines.yml", ".gitlab-ci.yml", ".env.example", ".env.sample",
    ".env.template", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "poetry.lock",
    "uv.lock", "pipfile.lock", "gradle.lockfile", "cargo.lock", "gemfile.lock",
    "composer.lock", "requirements-dev.txt", "requirements-test.txt",
    "server.xml", "context.xml", "persistence.xml", "hibernate.cfg.xml", "web.xml",
    "buildkite.yml", "tiltfile", "vagrantfile",
}
TEST_PARTS = {"test", "tests", "src/test", "integration", "integration-test", "integration-tests", "e2e", "spec", "specs", "features"}
INFRA_PARTS = {".github", ".circleci", "ci", "k8s", "kubernetes", "helm", "terraform", "ansible", "deploy", "deployment", "config", "conf"}
TEST_SUFFIXES = {".py", ".java", ".kt", ".groovy", ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".mts", ".cts", ".go", ".rb", ".cs", ".php", ".sh", ".feature", ".rs", ".sql", ".c", ".cpp", ".h", ".hpp", ".swift", ".scala", ".dart", ".ex", ".exs"}
CONFIG_SUFFIXES = {".yaml", ".yml", ".properties", ".xml", ".toml", ".ini", ".conf", ".cnf"}


class MapError(ValueError):
    pass


def current_platform() -> str:
    return "windows" if os.name == "nt" else "posix"


def repo_path(repo_root: Path, value: str) -> Path:
    candidate = Path(value)
    root = repo_root.resolve()
    lexical = Path(os.path.abspath(candidate if candidate.is_absolute() else root / candidate))
    try:
        relative = lexical.relative_to(root)
    except ValueError as exc:
        raise MapError(f"Path must stay inside repository: {value}") from exc
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise MapError(f"Refusing symlink path component: {current}")
    resolved = lexical.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise MapError(f"Path resolves outside repository: {value}") from exc
    return resolved


def is_candidate(rel: str) -> bool:
    path = Path(rel)
    parts = [part.lower() for part in path.parts]
    name = path.name.lower()
    if any(part in SKIP_PARTS for part in parts) or name in SECRET_NAMES:
        return False
    if name.startswith(".env.") and not name.endswith((".example", ".sample", ".template")):
        return False
    if name in KNOWN_FILES or name.startswith(("dockerfile.", "docker-compose", "compose.", "playwright.config.", "vitest.config.", "jest.config.")):
        return True
    if any(part in TEST_PARTS or part.startswith(("test", "integrationtest", "e2e", "spec")) for part in parts):
        return path.suffix.lower() in TEST_SUFFIXES | CONFIG_SUFFIXES or name in {"makefile", "dockerfile"}
    if any(part in INFRA_PARTS for part in parts):
        return path.suffix.lower() in CONFIG_SUFFIXES | {".json", ".sh", ".ps1", ".bat", ".cmd", ".tf"} or name == "jenkinsfile"
    if name.startswith(("application.", "bootstrap.", "log4j", "logback", "test-", "test_")):
        return path.suffix.lower() in CONFIG_SUFFIXES | TEST_SUFFIXES
    if name.startswith("requirements") and path.suffix.lower() in {".txt", ".in"}:
        return True
    stem = path.stem.lower()
    if path.suffix.lower() in TEST_SUFFIXES and (
        stem.endswith(("test", "tests", "spec", "specs")) or any(marker in name for marker in (".test.", ".spec.", ".cy."))
    ):
        return True
    if path.suffix.lower() in {".sh", ".ps1", ".bat", ".cmd"} and name.startswith(("start", "run", "test", "wait", "service")):
        return True
    if path.suffix.lower() in CONFIG_SUFFIXES:
        # Keep likely environment/service definitions, not every arbitrary XML/YAML file.
        return any(token in name for token in ("service", "database", "db", "tomcat", "selenium", "mysql", "test", "app"))
    return False


def discover_paths(repo_root: Path) -> list[Path]:
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "ls-files", "-co", "--exclude-standard", "-z"],
            check=False, capture_output=True,
        )
    except OSError:
        proc = None
    if proc is not None and proc.returncode == 0:
        rel_paths = [item.decode("utf-8", "surrogateescape") for item in proc.stdout.split(b"\0") if item]
        paths = [repo_root / Path(rel) for rel in rel_paths if is_candidate(rel)]
    else:
        paths = []
        for base, dirs, files in os.walk(repo_root):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_PARTS and not (d.startswith(".") and d not in {".github", ".circleci"}))
            for filename in files:
                path = Path(base) / filename
                try:
                    rel = path.relative_to(repo_root).as_posix()
                except ValueError:
                    continue
                if is_candidate(rel):
                    paths.append(path)
    unique = sorted({Path(os.path.abspath(path)) for path in paths}, key=lambda item: item.relative_to(repo_root).as_posix())
    return unique


def scan_inputs(repo_root: Path) -> tuple[dict[str, str], bool]:
    paths = discover_paths(repo_root)
    signatures: dict[str, str] = {}
    incomplete = False
    for path in paths:
        try:
            metadata = path.lstat()
        except FileNotFoundError:
            # Git's cached file list still includes working-tree deletions
            # until they are staged. Treat absence as a removed input.
            continue
        except OSError:
            incomplete = True
            continue
        try:
            if stat.S_ISLNK(metadata.st_mode):
                # Track the link itself without following a possible path outside the repo.
                digest = hashlib.sha256(os.readlink(path).encode("utf-8", "surrogateescape")).hexdigest()
            elif stat.S_ISREG(metadata.st_mode):
                hasher = hashlib.sha256()
                with path.open("rb") as source:
                    for chunk in iter(lambda: source.read(1024 * 1024), b""):
                        hasher.update(chunk)
                digest = hasher.hexdigest()
            else:
                incomplete = True
                continue
        except FileNotFoundError:
            # A concurrent removal is equivalent to a removed snapshot input.
            continue
        except (OSError, ValueError):
            incomplete = True
            continue
        signatures[path.relative_to(repo_root).as_posix()] = digest
    return signatures, incomplete


def aggregate(signatures: dict[str, str]) -> str:
    body = "".join(f"{name}\0{digest}\n" for name, digest in sorted(signatures.items()))
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def index_path(map_path: Path, repo_root: Path) -> Path:
    return repo_root / ".ai-work" / (map_path.stem + ".index.json")


def load_map(path: Path) -> tuple[str, dict[str, Any]]:
    if not path.is_file() or path.is_symlink():
        raise MapError(f"Service map not found or is a symlink: {path}")
    text = path.read_text(encoding="utf-8")
    match = MAP_BLOCK.search(text)
    if not match:
        raise MapError("Missing machine-readable pae-service-map JSON block")
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise MapError(f"Invalid service map JSON: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != SCHEMA_VERSION:
        raise MapError(f"Expected service map schema_version={SCHEMA_VERSION}")
    return text, data


def replace_map_data(text: str, data: dict[str, Any]) -> str:
    replacement = f'{MAP_BEGIN}\n```json\n{json.dumps(data, ensure_ascii=False, indent=2)}\n```\n{MAP_END}'
    # A callable keeps JSON backslashes literal; re.sub(string) treats them as
    # replacement escapes (e.g. a regex value such as "\\d+").
    return MAP_BLOCK.sub(lambda _match: replacement, text, count=1)


def validate_data(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("inventory_reviewed") is not True:
        errors.append("inventory_reviewed must be true after reviewing the complete inventory")
    validations = data.get("validations")
    resources = data.get("resources")
    if not isinstance(validations, list) or not isinstance(resources, list):
        return errors + ["validations and resources must be arrays"]
    toolchains = data.get("toolchains", [])
    if not isinstance(toolchains, list):
        errors.append("toolchains must be an array when present")
        toolchains = []
    toolchain_ids: set[str] = set()
    for toolchain in toolchains:
        if not isinstance(toolchain, dict):
            errors.append("each toolchain must be an object")
            continue
        toolchain_id = toolchain.get("id")
        if not isinstance(toolchain_id, str) or not toolchain_id.strip() or toolchain_id in toolchain_ids:
            errors.append(f"toolchain id is empty or duplicated: {toolchain_id!r}")
            continue
        toolchain_ids.add(toolchain_id)
        command = toolchain.get("command")
        if not isinstance(command, list) or not command or any(
            not isinstance(arg, str) or not arg or "\0" in arg for arg in command
        ):
            errors.append(f"toolchain {toolchain_id}: command must be a nonempty argv array")
        timeout_value = toolchain.get("timeout_seconds", 10)
        if isinstance(timeout_value, bool) or not isinstance(timeout_value, int) or not 1 <= timeout_value <= 60:
            errors.append(f"toolchain {toolchain_id}: timeout_seconds must be 1..60")
        version_regex = toolchain.get("version_regex")
        if version_regex is not None:
            if not isinstance(version_regex, str):
                errors.append(f"toolchain {toolchain_id}: version_regex must be a string")
            else:
                try:
                    re.compile(version_regex, re.IGNORECASE)
                except re.error as exc:
                    errors.append(f"toolchain {toolchain_id}: invalid version_regex: {exc}")
    resource_ids: set[str] = set()
    validation_ids: set[str] = set()
    for resource in resources:
        if not isinstance(resource, dict):
            errors.append("each resource must be an object")
            continue
        rid = resource.get("id")
        if not isinstance(rid, str) or not rid.strip() or rid in resource_ids:
            errors.append(f"resource id is empty or duplicated: {rid!r}")
            continue
        resource_ids.add(rid)
        if not isinstance(resource.get("evidence"), list) or not resource["evidence"]:
            errors.append(f"resource {rid}: evidence must list at least one repository path or explicit local dependency")
        checks = resource.get("checks")
        if not isinstance(checks, list) or not checks:
            errors.append(f"resource {rid}: at least one health check is required")
            continue
        check_ids: set[str] = set()
        for check in checks:
            if not isinstance(check, dict):
                errors.append(f"resource {rid}: each check must be an object")
                continue
            cid = check.get("id")
            command = check.get("command")
            if not isinstance(cid, str) or not cid.strip() or cid in check_ids:
                errors.append(f"resource {rid}: check id is empty or duplicated: {cid!r}")
            else:
                check_ids.add(cid)
            if not isinstance(command, list) or not command or any(
                not isinstance(arg, str) or not arg or "\0" in arg for arg in command
            ):
                errors.append(f"resource {rid}/{cid}: command must be a nonempty argv array")
            for key, low, high in (("every_seconds", 10, 300), ("timeout_seconds", 1, 60)):
                value = check.get(key, 60 if key == "every_seconds" else 5)
                if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
                    errors.append(f"resource {rid}/{cid}: {key} must be {low}..{high}")
            grace_value = check.get("startup_grace_seconds", 60)
            if isinstance(grace_value, bool) or not isinstance(grace_value, int) or not 0 <= grace_value <= 600:
                errors.append(f"resource {rid}/{cid}: startup_grace_seconds must be 0..600")
            failure_class = check.get("failure_class", "environmental")
            if failure_class not in {"environmental", "semantic"}:
                errors.append(f"resource {rid}/{cid}: failure_class must be environmental or semantic")
            if "record_excerpt" in check and not isinstance(check["record_excerpt"], bool):
                errors.append(f"resource {rid}/{cid}: record_excerpt must be boolean")
            platforms = check.get("platforms")
            if platforms is not None:
                if not isinstance(platforms, list) or not platforms or any(not isinstance(item, str) or item not in {"posix", "windows"} for item in platforms):
                    errors.append(f"resource {rid}/{cid}: platforms must contain posix and/or windows")
            codes = check.get("success_exit_codes", [0])
            if not isinstance(codes, list) or not codes or any(isinstance(code, bool) or not isinstance(code, int) for code in codes):
                errors.append(f"resource {rid}/{cid}: success_exit_codes must be a nonempty integer array")
            for key in ("healthy_regex", "unhealthy_regex"):
                pattern = check.get(key)
                if pattern is not None:
                    if not isinstance(pattern, str):
                        errors.append(f"resource {rid}/{cid}: {key} must be a string")
                    else:
                        try:
                            re.compile(pattern, re.IGNORECASE)
                        except re.error as exc:
                            errors.append(f"resource {rid}/{cid}: invalid {key}: {exc}")
        active_checks = [
            check for check in checks if isinstance(check, dict)
            and (check.get("platforms") is None or current_platform() in check.get("platforms", []))
        ]
        if checks and not active_checks:
            errors.append(f"resource {rid}: no health check is configured for the current {current_platform()} host")
    for validation in validations:
        if not isinstance(validation, dict):
            errors.append("each validation must be an object")
            continue
        vid = validation.get("id")
        if not isinstance(vid, str) or not vid.strip() or vid in validation_ids:
            errors.append(f"validation id is empty or duplicated: {vid!r}")
            continue
        validation_ids.add(vid)
        command = validation.get("command")
        if not isinstance(command, list) or not command or any(
            not isinstance(arg, str) or not arg or "\0" in arg for arg in command
        ):
            errors.append(f"validation {vid}: command must be a nonempty argv array")
        resource_list = validation.get("resources")
        if not isinstance(resource_list, list) or any(not isinstance(rid, str) for rid in resource_list):
            errors.append(f"validation {vid}: resources must be an array of resource ids")
            continue
        if len(resource_list) != len(set(resource_list)):
            errors.append(f"validation {vid}: duplicate resource ids")
        for rid in resource_list:
            if rid not in resource_ids:
                errors.append(f"validation {vid}: unknown resource {rid!r}")
        toolchain_list = validation.get("toolchains", [])
        if not isinstance(toolchain_list, list) or any(not isinstance(item, str) for item in toolchain_list):
            errors.append(f"validation {vid}: toolchains must be an array of toolchain ids")
        else:
            if len(toolchain_list) != len(set(toolchain_list)):
                errors.append(f"validation {vid}: duplicate toolchain ids")
            for toolchain_id in toolchain_list:
                if toolchain_id not in toolchain_ids:
                    errors.append(f"validation {vid}: unknown toolchain {toolchain_id!r}")
        idle_value = validation.get("no_progress_timeout_seconds", 300)
        if isinstance(idle_value, bool) or not isinstance(idle_value, int) or not 0 <= idle_value <= 7200:
            errors.append(f"validation {vid}: no_progress_timeout_seconds must be 0..7200")
    return errors


def current_status(repo_root: Path, map_path: Path, data: dict[str, Any]) -> tuple[bool, dict[str, str], bool, list[str]]:
    signatures, truncated = scan_inputs(repo_root)
    snapshot = data.get("snapshot") if isinstance(data.get("snapshot"), dict) else {}
    digest = aggregate(signatures)
    stale = snapshot.get("algorithm") != ALGORITHM or snapshot.get("digest") != digest or truncated
    changed: list[str] = []
    sidecar = index_path(map_path, repo_root)
    if sidecar.is_file() and not sidecar.is_symlink():
        try:
            previous = json.loads(sidecar.read_text(encoding="utf-8")).get("files", {})
            if isinstance(previous, dict):
                changed = sorted(
                    name for name in set(previous) | set(signatures)
                    if previous.get(name) != signatures.get(name)
                )
        except (OSError, json.JSONDecodeError, AttributeError):
            changed = []
    return not stale, signatures, truncated, changed


def write_index(path: Path, repo_root: Path, signatures: dict[str, str], truncated: bool) -> None:
    path = repo_path(repo_root, path.as_posix())
    if path.is_symlink():
        raise MapError(f"Refusing symlink index path: {path}")
    record = {"algorithm": ALGORITHM, "files": dict(sorted(signatures.items())), "truncated": truncated}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def cmd_check(args: argparse.Namespace) -> int:
    root = Path(args.repo_root).resolve()
    map_path = repo_path(root, args.map)
    if not map_path.is_file():
        print(f"service-map=missing path={args.map}; initialize before final planning")
        return 2
    _, data = load_map(map_path)
    fresh, signatures, truncated, changed = current_status(root, map_path, data)
    validation_errors = validate_data(data)
    if fresh and not truncated and not index_path(map_path, root).exists():
        write_index(index_path(map_path, root), root, signatures, truncated)
    if fresh and not validation_errors:
        print(f"service-map=fresh sources={len(signatures)} toolchains={len(data.get('toolchains', []))} resources={len(data['resources'])} validations={len(data['validations'])}")
        return 0
    reasons = []
    if not fresh:
        reasons.append("source snapshot is stale" + (" (some inputs could not be read)" if truncated else ""))
    if validation_errors:
        reasons.append("inventory incomplete")
    print("service-map=review-required reason=" + "; ".join(reasons))
    if changed:
        for name in changed[:30]:
            print(f"changed: {name}")
        if len(changed) > 30:
            print(f"changed: ... and {len(changed) - 30} more")
    elif truncated:
        print("changed: some discovered inputs could not be read; check file access")
    elif index_path(map_path, root).is_file():
        print("changed: no fingerprinted source path/content differences")
    elif not fresh:
        print("changed: index unavailable; inspect discovered test/build/CI/service inputs")
    for error in validation_errors[:12]:
        print(f"map-error: {error}")
    return 2


def cmd_init(args: argparse.Namespace) -> int:
    root = Path(args.repo_root).resolve()
    map_path = repo_path(root, args.map)
    if map_path.exists():
        raise MapError(f"Refusing to overwrite existing map: {map_path}")
    signatures, truncated = scan_inputs(root)
    data = {
        "schema_version": SCHEMA_VERSION,
        "inventory_reviewed": False,
        "snapshot": {"algorithm": ALGORITHM, "digest": aggregate(signatures), "source_count": len(signatures)},
        "toolchains": [],
        "validations": [],
        "resources": [],
    }
    template_path = Path(__file__).resolve().parents[1] / "assets" / "service-map-template.md"
    template = template_path.read_text(encoding="utf-8")
    map_path.parent.mkdir(parents=True, exist_ok=True)
    map_path.write_text(replace_map_data(template, data), encoding="utf-8")
    write_index(index_path(map_path, root), root, signatures, truncated)
    print(f"created draft map={map_path.relative_to(root).as_posix()} sources={len(signatures)}; review inventory before stamping")
    if truncated:
        print("warning: some discovered inputs could not be read; map cannot be marked fresh")
    return 0


def cmd_stamp(args: argparse.Namespace) -> int:
    if not args.confirm_reconciled:
        raise MapError("Refusing to stamp without --confirm-reconciled after reviewing changed inputs")
    root = Path(args.repo_root).resolve()
    map_path = repo_path(root, args.map)
    text, data = load_map(map_path)
    errors = validate_data(data)
    if errors:
        raise MapError("Cannot stamp an incomplete map: " + "; ".join(errors[:6]))
    signatures, truncated = scan_inputs(root)
    if truncated:
        raise MapError("Some discovered test/build/service inputs could not be read; fix access and retry stamping")
    data["snapshot"] = {"algorithm": ALGORITHM, "digest": aggregate(signatures), "source_count": len(signatures)}
    map_path.write_text(replace_map_data(text, data), encoding="utf-8")
    write_index(index_path(map_path, root), root, signatures, truncated)
    print(f"service-map=stamped sources={len(signatures)} toolchains={len(data.get('toolchains', []))} resources={len(data['resources'])} validations={len(data['validations'])}")
    return 0


def parse_watcher_command(command: str, expected_map: str, repo_root: Path) -> str | None:
    """Accept only a standalone Python resource-watch invocation.

    Validation commands are run through a shell by the plan runner, so looking
    for substrings would allow echo/comment/suffix-command bypasses.
    """
    if any(char in command for char in "\r\n;&|<>`#$%^\u0000"):
        return None
    try:
        lexer = shlex.shlex(command, posix=os.name != "nt")
        lexer.whitespace_split = True
        lexer.commenters = ""
        tokens = list(lexer)
    except ValueError:
        return None
    if os.name == "nt":
        tokens = [token[1:-1] if len(token) >= 2 and token[0] == token[-1] and token[0] in "\"'" else token for token in tokens]
    if len(tokens) < 3:
        return None

    def basename(value: str) -> str:
        return re.split(r"[/\\]", value)[-1].lower()

    interpreter = basename(tokens[0])
    if re.fullmatch(r"(?:python(?:\d+(?:\.\d+)*)?|py)(?:\.exe)?", interpreter) is None:
        return None
    if basename(tokens[1]) != "resource_watch.py" or tokens[2] != "run":
        return None
    candidate_script = Path(tokens[1]).expanduser()
    if not candidate_script.is_absolute():
        candidate_script = repo_root / candidate_script
    expected_script = Path(__file__).with_name("resource_watch.py").resolve()
    try:
        if candidate_script.resolve(strict=True) != expected_script:
            return None
    except (OSError, RuntimeError):
        return None

    values: dict[str, str] = {}
    index = 3
    allowed = {"--repo-root", "--map", "--validation", "--report"}
    while index < len(tokens):
        token = tokens[index]
        if token.startswith("--") and "=" in token:
            option, value = token.split("=", 1)
        else:
            option = token
            index += 1
            if index >= len(tokens):
                return None
            value = tokens[index]
        if option not in allowed or option in values or not value or value.startswith("--"):
            return None
        values[option] = value
        index += 1
    if set(values) - allowed or "--map" not in values or "--validation" not in values:
        return None
    if values.get("--repo-root", ".") not in {".", "./"}:
        return None
    normalized_map = values["--map"].replace("\\", "/").removeprefix("./")
    if normalized_map != expected_map.replace("\\", "/").removeprefix("./"):
        return None
    if "--report" in values:
        report_path = Path(values["--report"])
        if report_path.is_absolute() or ".." in report_path.parts:
            return None
    validation_id = values["--validation"]
    if re.fullmatch(r"[A-Za-z0-9_.-]+", validation_id) is None:
        return None
    return validation_id


def cmd_audit_plan(args: argparse.Namespace) -> int:
    root = Path(args.repo_root).resolve()
    map_path = repo_path(root, args.map)
    _, data = load_map(map_path)
    fresh, _, truncated, _ = current_status(root, map_path, data)
    errors = validate_data(data)
    if not fresh or truncated:
        errors.append("service map freshness snapshot is stale")
    valid_ids = {item.get("id") for item in data.get("validations", []) if isinstance(item, dict)}
    plan_path = repo_path(root, args.plan)
    manifest_path = plan_path / "manifest.json" if plan_path.is_dir() else plan_path
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MapError(f"Cannot read plan manifest: {exc}") from exc
    unmapped: list[str] = []
    for task in manifest.get("tasks", []):
        task_id = str(task.get("id", "?"))
        for number, command in enumerate(task.get("validation_commands", []), 1):
            expected_map = args.map.removeprefix("./")
            validation_id = parse_watcher_command(command, expected_map, root) if isinstance(command, str) else None
            if validation_id not in valid_ids:
                unmapped.append(f"task {task_id} validation {number}")
    errors.extend(f"unmapped plan validation: {item}" for item in unmapped)
    if errors:
        print("service-map-audit=failed")
        for error in errors[:20]:
            print(f"error: {error}")
        return 2
    total = sum(len(task.get("validation_commands", [])) for task in manifest.get("tasks", []))
    print(f"service-map-audit=passed plan_validations={total} map_validations={len(valid_ids)}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    root = Path(args.repo_root).resolve()
    map_path = repo_path(root, args.map)
    _, data = load_map(map_path)
    fresh, _, truncated, _ = current_status(root, map_path, data)
    errors = validate_data(data)
    if not fresh or truncated or errors:
        print("service-map=list-unavailable; run check and reconcile the map first")
        return 2
    for item in data["validations"]:
        resources = ",".join(item["resources"]) or "none"
        toolchains = ",".join(item.get("toolchains", [])) or "none"
        idle = item.get("no_progress_timeout_seconds", 300)
        print(f"{item['id']} | {item.get('name', 'unnamed')} | tools={toolchains} resources={resources} no-progress={idle}s")
    for item in data.get("toolchains", []):
        print(f"toolchain {item['id']} | {item.get('name', 'unnamed')}")
    for resource in data["resources"]:
        checks = ",".join(f"{check['id']}@{check.get('every_seconds', 60)}s" for check in resource["checks"])
        print(f"resource {resource['id']} | {resource.get('name', resource.get('type', 'service'))} | checks={checks}")
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    sub = result.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check", help="cheaply report whether the service map needs review")
    check.add_argument("--repo-root", default=".")
    check.add_argument("--map", default=".ai-work/SERVICE_MAP.md")
    check.set_defaults(func=cmd_check)
    init = sub.add_parser("init", help="create a project-local draft map without replacing one")
    init.add_argument("--repo-root", default=".")
    init.add_argument("--map", default=".ai-work/SERVICE_MAP.md")
    init.set_defaults(func=cmd_init)
    stamp = sub.add_parser("stamp", help="record fingerprints after the inventory was reconciled")
    stamp.add_argument("--repo-root", default=".")
    stamp.add_argument("--map", default=".ai-work/SERVICE_MAP.md")
    stamp.add_argument("--confirm-reconciled", action="store_true")
    stamp.set_defaults(func=cmd_stamp)
    audit = sub.add_parser("audit-plan", help="ensure every plan validation routes through a mapped validation id")
    audit.add_argument("--repo-root", default=".")
    audit.add_argument("--map", default=".ai-work/SERVICE_MAP.md")
    audit.add_argument("--plan", required=True)
    audit.set_defaults(func=cmd_audit_plan)
    listing = sub.add_parser("list", help="show only validation/resource ids and monitor intervals")
    listing.add_argument("--repo-root", default=".")
    listing.add_argument("--map", default=".ai-work/SERVICE_MAP.md")
    listing.set_defaults(func=cmd_list)
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        return int(args.func(args))
    except (MapError, OSError) as exc:
        print(f"service-map error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
