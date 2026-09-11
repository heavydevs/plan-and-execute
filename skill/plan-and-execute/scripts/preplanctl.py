#!/usr/bin/env python3
"""Deterministically prepare oversized requests for resumable final planning."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import re
import shlex
import sys
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

import planctl

SOFT_TOKENS = 12_000
HARD_TOKENS = 24_000
BREADTH_TOKEN_FLOOR = 8_000
BREADTH_HEADINGS = 30
TARGET_FRAGMENT_TOKENS = 4_500
MAX_FRAGMENT_TOKENS = 6_500
BATCH_TOKENS = 9_000
MAX_BATCH_FRAGMENTS = 4
PREPARED_ROOT = Path(".ai-work") / "prepared"


class PreplanError(RuntimeError):
    pass


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PreplanError(f"Cannot read JSON {path}: {exc}") from exc


def slugify(value: str, fallback: str = "request") -> str:
    return (re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:56] or fallback)


def estimate_tokens(text: str) -> int:
    words = len(re.findall(r"\S+", text))
    return max(1, math.ceil(max(len(text) / 3.7, words * 1.35)))


def safe_source(value: str | Path) -> Path:
    path = Path(value).expanduser().resolve()
    if path.is_symlink() or not path.is_file():
        raise PreplanError(f"Source must be a regular file: {path}")
    return path


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def detect_heading(style: str, text: str) -> int | None:
    match = re.search(r"(?:heading|title|t[ií]tulo)[ _-]?(\d+)", style, re.I)
    if match:
        return min(6, max(1, int(match.group(1))))
    match = re.match(r"^\s{0,3}(#{1,6})\s+\S", text)
    if match:
        return len(match.group(1))
    match = re.match(r"^(\d+(?:\.\d+){0,5})\s+\S", text)
    if match and len(text) <= 180:
        return min(6, match.group(1).count(".") + 1)
    return None


def docx_blocks(path: Path) -> list[dict[str, Any]]:
    try:
        with zipfile.ZipFile(path) as archive:
            root = ET.fromstring(archive.read("word/document.xml"))
    except (zipfile.BadZipFile, KeyError, ET.ParseError) as exc:
        raise PreplanError(f"Invalid .docx source: {path}") from exc
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    blocks: list[dict[str, Any]] = []
    for paragraph in root.findall(".//w:body/w:p", ns):
        text = "".join(node.text or "" for node in paragraph.findall(".//w:t", ns)).strip()
        if not text:
            continue
        style_node = paragraph.find("./w:pPr/w:pStyle", ns)
        style = "" if style_node is None else style_node.attrib.get(f"{{{ns['w']}}}val", "")
        blocks.append(
            {
                "no": len(blocks) + 1,
                "text": text,
                "heading_level": detect_heading(style, text),
            }
        )
    if not blocks:
        raise PreplanError(f"No readable paragraphs in {path}")
    return blocks


def text_blocks(path: Path) -> list[dict[str, Any]]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise PreplanError(
            f"{path.name} is not UTF-8 text; export to text/Markdown or use supported .docx input"
        ) from exc
    blocks: list[dict[str, Any]] = []
    buf: list[str] = []

    def append(value: str) -> None:
        value = value.strip()
        if value:
            blocks.append(
                {"no": len(blocks) + 1, "text": value, "heading_level": detect_heading("", value)}
            )

    def flush() -> None:
        if buf:
            append("\n".join(buf))
            buf.clear()

    for line in text.splitlines():
        if not line.strip():
            flush()
        elif re.match(r"^\s{0,3}#{1,6}\s+", line) or (
            re.match(r"^\d+(?:\.\d+){0,5}\s+\S", line) and len(line) <= 180
        ):
            flush()
            append(line)
        else:
            buf.append(line.rstrip())
    flush()
    if not blocks and text.strip():
        append(text)
    return blocks


def extract_blocks(path: Path) -> list[dict[str, Any]]:
    return docx_blocks(path) if path.suffix.lower() == ".docx" else text_blocks(path)


def assess_source(
    path: Path,
    soft_tokens: int = SOFT_TOKENS,
    hard_tokens: int = HARD_TOKENS,
    breadth_token_floor: int = BREADTH_TOKEN_FLOOR,
    breadth_headings: int = BREADTH_HEADINGS,
) -> dict[str, Any]:
    blocks = extract_blocks(path)
    logical = "\n\n".join(item["text"] for item in blocks)
    tokens = estimate_tokens(logical)
    headings = sum(item["heading_level"] is not None for item in blocks)
    reasons: list[str] = []
    if tokens >= hard_tokens:
        reasons.append(f"estimated_tokens={tokens} >= hard_threshold={hard_tokens}")
    if tokens >= breadth_token_floor and headings >= breadth_headings:
        reasons.append(f"structural_breadth=headings:{headings} at estimated_tokens:{tokens}")
    route = "primary_plan" if reasons else "final_plan"
    if route == "final_plan" and tokens > soft_tokens:
        reasons.append(f"between_thresholds={soft_tokens}:{hard_tokens}; no breadth trigger")
    raw = path.read_bytes()
    return {
        "source": str(path),
        "source_name": path.name,
        "source_bytes": len(raw),
        "source_sha256": sha256_bytes(raw),
        "logical_blocks": len(blocks),
        "heading_count": headings,
        "estimated_tokens": tokens,
        "soft_tokens": soft_tokens,
        "hard_tokens": hard_tokens,
        "breadth_token_floor": breadth_token_floor,
        "breadth_headings": breadth_headings,
        "route": route,
        "reasons": reasons,
    }


def split_long_text(text: str, max_tokens: int) -> list[str]:
    if estimate_tokens(text) <= max_tokens:
        return [text]
    parts: list[str] = []
    remaining = text.strip()
    max_chars = max_tokens * 3
    while estimate_tokens(remaining) > max_tokens:
        cut = min(len(remaining), max_chars)
        lower = max(1, int(cut * 0.65))
        point = remaining.rfind("\n", lower, cut)
        if point < 0:
            point = remaining.rfind(". ", lower, cut)
            if point >= 0:
                point += 1
        if point < 0:
            point = remaining.rfind(" ", lower, cut)
        if point <= 0:
            point = cut
        parts.append(remaining[:point].strip())
        remaining = remaining[point:].strip()
    if remaining:
        parts.append(remaining)
    return parts


def make_fragments(
    blocks: list[dict[str, Any]],
    target_tokens: int = TARGET_FRAGMENT_TOKENS,
    max_tokens: int = MAX_FRAGMENT_TOKENS,
) -> list[dict[str, Any]]:
    expanded: list[dict[str, Any]] = []
    for block in blocks:
        for index, piece in enumerate(split_long_text(block["text"], max_tokens)):
            expanded.append(
                {
                    "no": block["no"],
                    "text": piece,
                    "heading_level": block["heading_level"] if index == 0 else None,
                }
            )
    fragments: list[dict[str, Any]] = []
    current: list[dict[str, Any]] = []
    current_tokens = 0
    headings: dict[int, str] = {}
    current_path: list[str] = []

    def flush() -> None:
        nonlocal current, current_tokens, current_path
        if not current:
            return
        text = "\n\n".join(item["text"] for item in current).strip()
        fragments.append(
            {
                "id": f"F{len(fragments) + 1:03d}",
                "text": text,
                "estimated_tokens": estimate_tokens(text),
                "source_block_start": current[0]["no"],
                "source_block_end": current[-1]["no"],
                "heading_path": list(current_path),
                "sha256": sha256_text(text),
            }
        )
        current = []
        current_tokens = 0
        current_path = []

    for block in expanded:
        level = block["heading_level"]
        if level is not None:
            for key in list(headings):
                if key >= level:
                    headings.pop(key, None)
            headings[level] = block["text"]
        block_tokens = estimate_tokens(block["text"])
        new_section = level is not None and current_tokens >= max(800, target_tokens // 3)
        if current and (new_section or current_tokens + block_tokens > max_tokens):
            flush()
        if not current:
            current_path = [headings[key] for key in sorted(headings)]
        current.append(block)
        current_tokens += block_tokens
        if current_tokens >= target_tokens:
            flush()
    flush()
    return fragments


def package_id_for(source: Path, assessment: dict[str, Any]) -> str:
    return f"{slugify(source.stem)}-{assessment['source_sha256'][:10]}"


def create_package(
    repo_root: Path,
    source: Path,
    assessment: dict[str, Any],
    package_id: str | None = None,
    target_tokens: int = TARGET_FRAGMENT_TOKENS,
    max_tokens: int = MAX_FRAGMENT_TOKENS,
) -> tuple[Path, dict[str, Any]]:
    package_id = package_id or package_id_for(source, assessment)
    root = (repo_root / PREPARED_ROOT).resolve()
    root.mkdir(parents=True, exist_ok=True)
    package = (root / package_id).resolve()
    if package.parent != root or package.exists():
        raise PreplanError(f"Invalid or existing prepared package: {package}")
    (package / "fragments").mkdir(parents=True)
    (package / "digests").mkdir()
    fragments = make_fragments(extract_blocks(source), target_tokens, max_tokens)
    index: list[dict[str, Any]] = []
    for fragment in fragments:
        title = fragment["heading_path"][-1] if fragment["heading_path"] else "source"
        relative = Path("fragments") / f"{fragment['id']}-{slugify(title, 'source')}.md"
        content = (
            f"# {fragment['id']} — source fragment\n\n"
            f"- Source: `{source.name}`\n"
            f"- Source blocks: {fragment['source_block_start']}–{fragment['source_block_end']}\n"
            f"- Source-text SHA-256: `{fragment['sha256']}`\n"
            f"- Estimated tokens: {fragment['estimated_tokens']}\n"
            f"- Heading path: {' > '.join(fragment['heading_path']) or '(none)'}\n\n"
            "## Source text\n\n"
            f"{fragment['text']}\n"
        )
        (package / relative).write_text(content, encoding="utf-8")
        index.append(
            {
                "id": fragment["id"],
                "path": relative.as_posix(),
                "estimated_tokens": fragment["estimated_tokens"],
                "source_block_start": fragment["source_block_start"],
                "source_block_end": fragment["source_block_end"],
                "heading_path": fragment["heading_path"],
                "source_text_sha256": fragment["sha256"],
            }
        )
    write_json(package / "SOURCE_INDEX.json", {"fragments": index})
    metadata = {
        "schema_version": 1,
        "package_id": package_id,
        "state": "skeleton",
        "created_at": now_utc(),
        "source": {
            "name": source.name,
            "original_path": str(source),
            "sha256": assessment["source_sha256"],
            "estimated_tokens": assessment["estimated_tokens"],
            "heading_count": assessment["heading_count"],
        },
        "assessment": assessment,
        "fragment_count": len(index),
        "artifacts": {
            "source_index": "SOURCE_INDEX.json",
            "digests": "digests/",
            "pattern_seeds": "PATTERN_SEEDS.json",
            "workstream_index": "WORKSTREAM_INDEX.json",
            "coverage_review": "COVERAGE_REVIEW.json",
            "final_plan_input": "FINAL_PLAN_INPUT.md",
        },
    }
    write_json(package / "package.json", metadata)
    return package, metadata


def batch_fragments(index: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    batches: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    tokens = 0
    for fragment in index:
        size = int(fragment["estimated_tokens"])
        if current and (len(current) >= MAX_BATCH_FRAGMENTS or tokens + size > BATCH_TOKENS):
            batches.append(current)
            current, tokens = [], 0
        current.append(fragment)
        tokens += size
    if current:
        batches.append(current)
    return batches


def boundary(why: str, separated: str) -> dict[str, Any]:
    return {
        "shared_context": ["Assigned prepared-package inputs, output schema, and validation command form one bounded preprocessing contract."],
        "why_one_todo": why,
        "separate_from": [separated],
    }


def repo_rel(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError as exc:
        raise PreplanError(f"Prepared artifact must live under repository root: {path}") from exc


def make_primary_spec(repo_root: Path, package: Path, metadata: dict[str, Any]) -> dict[str, Any]:
    index = read_json(package / "SOURCE_INDEX.json")["fragments"]
    batches = batch_fragments(index)
    python = shlex.quote(sys.executable)
    script = shlex.quote(str(Path(__file__).resolve()))
    pkg_arg = shlex.quote(str(package))
    tasks: list[dict[str, Any]] = []

    for batch_no, batch in enumerate(batches, 1):
        digest_id = f"D{batch_no:03d}"
        fragment_ids = [item["id"] for item in batch]
        fragment_paths = [str(package / item["path"]) for item in batch]
        output = package / "digests" / f"{digest_id}.json"
        tasks.append(
            {
                "id": batch_no,
                "title": f"Extract planning facts {fragment_ids[0]}–{fragment_ids[-1]}",
                "objective": f"Create source-referenced {digest_id} without losing obligations from assigned fragments.",
                "requirement_ids": ["R001", "R002"],
                "complexity": "medium",
                "atomicity_rationale": "This bounded fragment batch fits one cheap worker context and has one independently schema-checkable digest output.",
                "context_boundary": boundary(
                    "One worker compares the assigned fragment batch so local repeated constraints are normalized without importing unrelated source sections.",
                    "Cross-batch synthesis, whole-source coverage, and implementation planning are separate TODOs.",
                ),
                "scope": {
                    "in": ["Extract obligations, constraints, interfaces, dependencies, validation implications, pattern candidates, and material questions."],
                    "out": ["Do not implement software, invent architecture, or silently reconcile contradictions."],
                    "expected_files": [repo_rel(output, repo_root)],
                },
                "dependencies": [],
                "implementation_guidance": [
                    "Read only these immutable fragments: " + ", ".join(fragment_paths),
                    f"Write {output} with digest_id, fragment_ids, obligations, constraints, interfaces, dependencies, validation_implications, pattern_candidates, material_questions.",
                    "Each semantic item is an object with non-empty text and source_refs using only assigned fragment ids.",
                ],
                "acceptance_criteria": [f"{digest_id} covers exactly {', '.join(fragment_ids)} with primary-source references on every extracted semantic item."],
                "validation_commands": [f"{python} {script} validate-digest --package {pkg_arg} --digest {digest_id}"],
                "subtasks": [
                    {"id": "S001", "title": "Read assigned fragments", "objective": "Inspect the bounded immutable source batch."},
                    {"id": "S002", "title": "Write source-referenced digest", "objective": f"Persist {digest_id} with atomic planning facts and provenance."},
                ],
                "learning_targets": [],
                "provider": "auto",
                "model_tier": "economy",
                "reasoning_effort": "medium",
            }
        )

    digest_ids = list(range(1, len(batches) + 1))
    synth_id = len(tasks) + 1
    pattern_file = package / "PATTERN_SEEDS.json"
    workstream_file = package / "WORKSTREAM_INDEX.json"
    tasks.append(
        {
            "id": synth_id,
            "title": "Synthesize cross-fragment contracts",
            "objective": "Build pattern seeds and a compact workstream/dependency index from validated digests, opening raw fragments only for material ambiguity.",
            "requirement_ids": ["R003"],
            "complexity": "high",
            "atomicity_rationale": "Cross-fragment normalization and pattern deduplication need the same compact digest set and produce one coupled synthesis boundary.",
            "context_boundary": boundary(
                "One synthesis context compares all validated digests to detect repeated normative contracts and cross-domain dependencies consistently.",
                "Whole-source coverage review and final implementation planning remain separate later stages.",
            ),
            "scope": {
                "in": ["Merge repeated normative contracts, index workstreams/dependencies, and preserve contradictions with source refs."],
                "out": ["Do not create final implementation TODOs or assign their model tiers."],
                "expected_files": [repo_rel(pattern_file, repo_root), repo_rel(workstream_file, repo_root)],
            },
            "dependencies": digest_ids,
            "implementation_guidance": [
                f"Read validated digests under {package / 'digests'} first; retrieve raw fragments only when verification changes the synthesis.",
                f"Write {pattern_file} as {{patterns:[...]}}; each pattern has id, title, contract[], source_refs[], rationale, affected_domains[].",
                f"Write {workstream_file} as {{workstreams:[...], dependencies:[...], contradictions:[...]}} with provenance.",
            ],
            "acceptance_criteria": ["Cross-cutting contracts and workstreams are compact, source-referenced, and contradictions remain explicit."],
            "validation_commands": [f"{python} {script} validate-synthesis --package {pkg_arg}"],
            "subtasks": [
                {"id": "S001", "title": "Compare validated digests", "objective": "Identify repeated contracts, domains, and dependencies."},
                {"id": "S002", "title": "Persist synthesis artifacts", "objective": "Write pattern seeds and workstream index with provenance."},
            ],
            "learning_targets": [],
            "provider": "auto",
            "model_tier": "standard",
            "reasoning_effort": "medium",
        }
    )

    review_id = synth_id + 1
    review_file = package / "COVERAGE_REVIEW.json"
    tasks.append(
        {
            "id": review_id,
            "title": "Review source coverage and contradictions",
            "objective": "Freshly verify every immutable fragment is represented and material omissions or contradictions are explicit before final planning.",
            "requirement_ids": ["R004"],
            "complexity": "high",
            "atomicity_rationale": "Coverage, provenance, and contradiction checks share one independent quality gate whose failure blocks the handoff.",
            "context_boundary": boundary(
                "A fresh reviewer needs source index, validated digests, and synthesis outputs together to challenge omissions without inheriting synthesis reasoning.",
                "Software architecture and implementation decomposition belong to the later final planner.",
            ),
            "scope": {
                "in": ["Verify fragment coverage, provenance, contradiction inventory, and handoff safety."],
                "out": ["Do not implement software or hide unresolved material findings."],
                "expected_files": [repo_rel(review_file, repo_root)],
            },
            "dependencies": [synth_id],
            "implementation_guidance": [
                f"Write {review_file} with status=approved|blocked, covered_fragment_ids, unresolved_material_findings, notes.",
                "Use a fresh context and retrieve raw fragments selectively for material claims instead of rereading the source wholesale.",
            ],
            "acceptance_criteria": ["Every SOURCE_INDEX fragment is covered by validated digests and unresolved material findings are explicit."],
            "validation_commands": [f"{python} {script} validate-coverage --package {pkg_arg}"],
            "subtasks": [
                {"id": "S001", "title": "Audit coverage", "objective": "Compare source index, digest coverage, and synthesis provenance."},
                {"id": "S002", "title": "Record review gate", "objective": "Persist approval or blocking findings without rewriting source evidence."},
            ],
            "learning_targets": [],
            "provider": "auto",
            "model_tier": "strong",
            "reasoning_effort": "medium",
        }
    )

    handoff_id = review_id + 1
    handoff = package / "FINAL_PLAN_INPUT.md"
    tasks.append(
        {
            "id": handoff_id,
            "title": "Build compact final-planning handoff",
            "objective": "Create a compact entry document that points the normal planner to indexed evidence without copying the full source.",
            "requirement_ids": ["R004"],
            "complexity": "low",
            "atomicity_rationale": "The handoff is a mechanical projection of reviewed artifacts with one package-level validation boundary.",
            "context_boundary": boundary(
                "One cheap worker can project validated package state into a concise handoff without reopening all fragments or making architecture decisions.",
                "Requirement decomposition, architecture, and implementation routing belong to normal final planning.",
            ),
            "scope": {
                "in": ["Summarize package identity, workstreams, pattern seeds, contradictions, and retrieval pointers."],
                "out": ["Do not paste every fragment or preassign implementation routes."],
                "expected_files": [repo_rel(handoff, repo_root)],
            },
            "dependencies": [review_id],
            "implementation_guidance": [
                f"Write {handoff} from compact package artifacts only, preserving stable fragment/digest ids and paths.",
                "The final planner must be able to retrieve exact primary evidence on demand without receiving the whole source in context.",
            ],
            "acceptance_criteria": ["The prepared package validates and FINAL_PLAN_INPUT points to the immutable evidence graph."],
            "validation_commands": [f"{python} {script} validate-package --package {pkg_arg}"],
            "subtasks": [
                {"id": "S001", "title": "Project compact handoff", "objective": "Create the final-planning entry document from reviewed compact artifacts."},
                {"id": "S002", "title": "Validate prepared package", "objective": "Run the deterministic package gate."},
            ],
            "learning_targets": [],
            "provider": "auto",
            "model_tier": "economy",
            "reasoning_effort": "low",
        }
    )

    return {
        "title": f"Prepare oversized request {metadata['package_id']}",
        "summary": "Create a source-traceable prepared request package for ordinary final planning; no product implementation occurs in this plan.",
        "language": "auto",
        "request_analysis": {
            "request_parts": [{"id": "P001", "text": "Prepare the oversized supplied specification so final software planning can resume economically without losing requirements."}],
            "repository_findings": ["Primary planning intentionally changes no product code; repository implementation state is outside this source-preparation boundary."],
            "research_decision": "No external research is needed for source fragmentation; final planning owns domain research decisions.",
            "research_findings": [],
            "assumptions": [],
            "risks": ["Semantic compression could omit a requirement; immutable fragments, source refs, and a fresh coverage review mitigate this risk."],
            "open_questions": [],
            "decomposition_strategy": "Fragment deterministically, extract bounded digests cheaply, synthesize cross-cutting contracts, review coverage freshly, then emit a compact handoff.",
        },
        "requirements": [
            {"id": "R001", "text": "Prepared evidence preserves stable source fragments and provenance for every later derived planning fact.", "source": "inferred", "priority": "must", "request_part_ids": ["P001"]},
            {"id": "R002", "text": "Each bounded fragment batch produces a source-referenced digest retaining explicit obligations and constraints.", "source": "inferred", "priority": "must", "request_part_ids": ["P001"]},
            {"id": "R003", "text": "Cross-fragment synthesis identifies repeated patterns, workstreams, dependencies, and contradictions without creating implementation TODOs.", "source": "inferred", "priority": "must", "request_part_ids": ["P001"]},
            {"id": "R004", "text": "A fresh coverage gate approves a compact final-planning handoff only when every source fragment is represented and material findings are explicit.", "source": "inferred", "priority": "must", "request_part_ids": ["P001"]},
        ],
        "global_constraints": ["Primary-plan work must not implement product code or bind final implementation model routes."],
        "execution_context": {
            "global": {
                "decision": "omit",
                "rationale": "Every primary TODO receives explicit prepared-package paths and a complete bounded output contract in its own definition.",
                "items": [],
            },
            "scoped": [],
        },
        "plan_review": {
            "status": "approved",
            "reviewer": "deterministic primary-plan scaffold",
            "rounds": 1,
            "coverage_complete": True,
            "tasks_atomic": True,
            "dependencies_valid": True,
            "validations_sufficient": True,
            "contexts_minimal": True,
            "context_boundaries_sound": True,
            "unresolved_findings": [],
            "notes": ["Each bounded fragment batch has one digest TODO; synthesis, fresh coverage review, and compact handoff are independent validation gates."],
        },
        "autostart": True,
        "cleanup_on_success": False,
        "tasks": tasks,
    }


def validate_digest(package: Path, digest_id: str) -> dict[str, Any]:
    index = read_json(package / "SOURCE_INDEX.json")["fragments"]
    known = {item["id"] for item in index}
    path = package / "digests" / f"{digest_id}.json"
    data = read_json(path)
    if data.get("digest_id") != digest_id:
        raise PreplanError(f"{path}: digest_id mismatch")
    ids = data.get("fragment_ids")
    if not isinstance(ids, list) or not ids or len(ids) != len(set(ids)) or not set(ids) <= known:
        raise PreplanError(f"{path}: fragment_ids must be a unique subset of SOURCE_INDEX")
    allowed = set(ids)
    for field in ("obligations", "constraints", "interfaces", "dependencies", "validation_implications", "pattern_candidates", "material_questions"):
        items = data.get(field, [])
        if not isinstance(items, list):
            raise PreplanError(f"{path}: {field} must be a list")
        for pos, item in enumerate(items):
            if not isinstance(item, dict) or not str(item.get("text", "")).strip():
                raise PreplanError(f"{path}: {field}[{pos}] needs non-empty text")
            refs = item.get("source_refs")
            if not isinstance(refs, list) or not refs or not set(refs) <= allowed:
                raise PreplanError(f"{path}: {field}[{pos}] has invalid source_refs")
    return data


def all_digests(package: Path) -> list[dict[str, Any]]:
    paths = sorted((package / "digests").glob("D*.json"))
    if not paths:
        raise PreplanError("No digest files exist")
    return [validate_digest(package, path.stem) for path in paths]


def validate_synthesis(package: Path) -> None:
    digests = all_digests(package)
    known = {ref for digest in digests for ref in digest["fragment_ids"]}
    seeds = read_json(package / "PATTERN_SEEDS.json")
    patterns = seeds.get("patterns") if isinstance(seeds, dict) else None
    if not isinstance(patterns, list):
        raise PreplanError("PATTERN_SEEDS.json requires patterns[]")
    for pos, pattern in enumerate(patterns):
        if not isinstance(pattern, dict) or not str(pattern.get("id", "")).strip() or not str(pattern.get("title", "")).strip():
            raise PreplanError(f"patterns[{pos}] requires id/title")
        if not isinstance(pattern.get("contract"), list) or not pattern["contract"]:
            raise PreplanError(f"patterns[{pos}] requires contract[]")
        refs = pattern.get("source_refs")
        if not isinstance(refs, list) or not refs or not set(refs) <= known:
            raise PreplanError(f"patterns[{pos}] has invalid source_refs")
    work = read_json(package / "WORKSTREAM_INDEX.json")
    if not isinstance(work, dict) or not isinstance(work.get("workstreams"), list):
        raise PreplanError("WORKSTREAM_INDEX.json requires workstreams[]")


def validate_coverage(package: Path) -> None:
    expected = {item["id"] for item in read_json(package / "SOURCE_INDEX.json")["fragments"]}
    actual = {fragment for digest in all_digests(package) for fragment in digest["fragment_ids"]}
    if expected != actual:
        raise PreplanError(f"Digest coverage mismatch; missing={sorted(expected-actual)}, extra={sorted(actual-expected)}")
    validate_synthesis(package)
    review = read_json(package / "COVERAGE_REVIEW.json")
    covered = review.get("covered_fragment_ids") if isinstance(review, dict) else None
    if not isinstance(covered, list) or set(covered) != expected:
        raise PreplanError("COVERAGE_REVIEW covered_fragment_ids must exactly match SOURCE_INDEX")
    if review.get("status") not in {"approved", "blocked"}:
        raise PreplanError("COVERAGE_REVIEW status must be approved or blocked")
    unresolved = review.get("unresolved_material_findings")
    if not isinstance(unresolved, list):
        raise PreplanError("COVERAGE_REVIEW requires unresolved_material_findings[]")
    if review.get("status") == "approved" and unresolved:
        raise PreplanError("Approved coverage review cannot have unresolved material findings")


def validate_package(package: Path) -> None:
    metadata = read_json(package / "package.json")
    fragments = read_json(package / "SOURCE_INDEX.json").get("fragments")
    if not isinstance(fragments, list) or not fragments:
        raise PreplanError("SOURCE_INDEX requires fragments[]")
    for fragment in fragments:
        if not (package / fragment["path"]).is_file():
            raise PreplanError(f"Missing fragment {fragment['path']}")
    validate_coverage(package)
    review = read_json(package / "COVERAGE_REVIEW.json")
    if review.get("status") != "approved":
        raise PreplanError("Prepared package is blocked by coverage review")
    handoff = package / "FINAL_PLAN_INPUT.md"
    if not handoff.is_file() or len(handoff.read_text(encoding="utf-8").strip()) < 100:
        raise PreplanError("FINAL_PLAN_INPUT.md is missing or too shallow")
    metadata["state"] = "ready_for_final_planning"
    metadata["validated_at"] = now_utc()
    write_json(package / "package.json", metadata)


def command_assess(args: argparse.Namespace) -> None:
    print(json.dumps(assess_source(safe_source(args.file), args.soft_tokens, args.hard_tokens, args.breadth_token_floor, args.breadth_headings), ensure_ascii=False, indent=2))


def create_from_args(args: argparse.Namespace) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    repo = Path(args.repo_root).expanduser().resolve()
    source = safe_source(args.file)
    assessment = assess_source(source, args.soft_tokens, args.hard_tokens, args.breadth_token_floor, args.breadth_headings)
    package, metadata = create_package(repo, source, assessment, args.package_id, args.target_fragment_tokens, args.max_fragment_tokens)
    return package, metadata, assessment


def command_split(args: argparse.Namespace) -> None:
    package, metadata, assessment = create_from_args(args)
    print(json.dumps({"assessment": assessment, "package": str(package), "metadata": metadata}, ensure_ascii=False, indent=2))


def command_prepare(args: argparse.Namespace) -> None:
    repo = Path(args.repo_root).expanduser().resolve()
    source = safe_source(args.file)
    assessment = assess_source(source, args.soft_tokens, args.hard_tokens, args.breadth_token_floor, args.breadth_headings)
    if assessment["route"] != "primary_plan" and not args.force:
        print(json.dumps({"route": "final_plan", "assessment": assessment}, ensure_ascii=False, indent=2))
        raise SystemExit(3)
    package, metadata = create_package(repo, source, assessment, args.package_id, args.target_fragment_tokens, args.max_fragment_tokens)
    spec = make_primary_spec(repo, package, metadata)
    write_json(package / "PRIMARY_PLAN_SPEC.json", spec)
    plan_dir = planctl.create_plan(repo, spec, args.work_root, f"primary-{metadata['package_id']}")
    metadata = read_json(package / "package.json")
    metadata.update({"state": "primary_plan_created", "primary_plan": str(plan_dir)})
    write_json(package / "package.json", metadata)
    print(json.dumps({"route": "primary_plan", "assessment": assessment, "package": str(package), "primary_plan": str(plan_dir)}, ensure_ascii=False, indent=2))


def command_validate_digest(args: argparse.Namespace) -> None:
    validate_digest(Path(args.package).resolve(), args.digest)
    print(f"VALID {args.digest}")


def command_validate_synthesis(args: argparse.Namespace) -> None:
    validate_synthesis(Path(args.package).resolve())
    print("VALID SYNTHESIS")


def command_validate_coverage(args: argparse.Namespace) -> None:
    validate_coverage(Path(args.package).resolve())
    print("VALID COVERAGE")


def command_validate_package(args: argparse.Namespace) -> None:
    validate_package(Path(args.package).resolve())
    print("VALID PACKAGE")


def add_thresholds(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--soft-tokens", type=int, default=SOFT_TOKENS)
    parser.add_argument("--hard-tokens", type=int, default=HARD_TOKENS)
    parser.add_argument("--breadth-token-floor", type=int, default=BREADTH_TOKEN_FLOOR)
    parser.add_argument("--breadth-headings", type=int, default=BREADTH_HEADINGS)


def add_split_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--package-id")
    parser.add_argument("--target-fragment-tokens", type=int, default=TARGET_FRAGMENT_TOKENS)
    parser.add_argument("--max-fragment-tokens", type=int, default=MAX_FRAGMENT_TOKENS)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    assess = sub.add_parser("assess")
    assess.add_argument("--file", required=True)
    add_thresholds(assess)
    assess.set_defaults(func=command_assess)
    split = sub.add_parser("split")
    split.add_argument("--repo-root", default=".")
    split.add_argument("--file", required=True)
    add_thresholds(split)
    add_split_options(split)
    split.set_defaults(func=command_split)
    prepare = sub.add_parser("prepare")
    prepare.add_argument("--repo-root", default=".")
    prepare.add_argument("--work-root", default=planctl.WORK_ROOT_DEFAULT)
    prepare.add_argument("--file", required=True)
    prepare.add_argument("--force", action="store_true")
    add_thresholds(prepare)
    add_split_options(prepare)
    prepare.set_defaults(func=command_prepare)
    digest = sub.add_parser("validate-digest")
    digest.add_argument("--package", required=True)
    digest.add_argument("--digest", required=True)
    digest.set_defaults(func=command_validate_digest)
    synth = sub.add_parser("validate-synthesis")
    synth.add_argument("--package", required=True)
    synth.set_defaults(func=command_validate_synthesis)
    coverage = sub.add_parser("validate-coverage")
    coverage.add_argument("--package", required=True)
    coverage.set_defaults(func=command_validate_coverage)
    package = sub.add_parser("validate-package")
    package.add_argument("--package", required=True)
    package.set_defaults(func=command_validate_package)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        args.func(args)
        return 0
    except (PreplanError, planctl.PlanError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
