#!/usr/bin/env python3
"""Assess and prepare oversized requests before expensive final planning.

The controller intentionally performs only deterministic source work: sizing,
OOXML/plain-text extraction, lossless logical fragmentation, package validation,
and creation of a resumable primary plan through planctl. Semantic digest and
cross-fragment synthesis remain model tasks inside that durable primary plan.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import os
import re
import shlex
import sys
import zipfile
from pathlib import Path
from typing import Any, Iterable
from xml.etree import ElementTree as ET

import planctl

DEFAULT_SOFT_TOKENS = 12_000
DEFAULT_HARD_TOKENS = 24_000
DEFAULT_BREADTH_TOKEN_FLOOR = 8_000
DEFAULT_BREADTH_HEADINGS = 30
DEFAULT_TARGET_FRAGMENT_TOKENS = 4_500
DEFAULT_MAX_FRAGMENT_TOKENS = 6_500
DEFAULT_BATCH_TOKENS = 9_000
DEFAULT_MAX_BATCH_FRAGMENTS = 4
PREPARED_ROOT = Path(".ai-work") / "prepared"


class PreplanError(RuntimeError):
    pass


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def slugify(value: str, fallback: str = "request") -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value[:56] or fallback


def estimate_tokens(text: str) -> int:
    """Conservative language-agnostic planning estimate, not tokenizer billing."""
    chars = len(text)
    words = len(re.findall(r"\S+", text))
    return max(1, math.ceil(max(chars / 3.7, words * 1.35)))


def safe_source_path(value: str | Path) -> Path:
    path = Path(value).expanduser().resolve()
    if path.is_symlink() or not path.is_file():
        raise PreplanError(f"Source must be a regular file: {path}")
    return path


def read_plain_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise PreplanError(
            f"{path.name} is not UTF-8 text. Export it to text/Markdown or use supported .docx input."
        ) from exc


def docx_blocks(path: Path) -> list[dict[str, Any]]:
    try:
        with zipfile.ZipFile(path) as archive:
            xml = archive.read("word/document.xml")
    except (zipfile.BadZipFile, KeyError) as exc:
        raise PreplanError(f"Invalid .docx file: {path}") from exc

    root = ET.fromstring(xml)
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    blocks: list[dict[str, Any]] = []
    block_no = 0
    for paragraph in root.findall(".//w:body/w:p", ns):
        pieces = [node.text or "" for node in paragraph.findall(".//w:t", ns)]
        text = "".join(pieces).strip()
        if not text:
            continue
        block_no += 1
        style = paragraph.find("./w:pPr/w:pStyle", ns)
        style_value = ""
        if style is not None:
            style_value = style.attrib.get(f"{{{ns['w']}}}val", "")
        level = heading_level(style_value, text)
        blocks.append({"no": block_no, "text": text, "heading_level": level})
    if not blocks:
        raise PreplanError(f"No readable paragraphs found in {path}")
    return blocks


def heading_level(style: str, text: str) -> int | None:
    style_match = re.search(r"(?:heading|title|t[ií]tulo)[ _-]?(\d+)", style, re.I)
    if style_match:
        return min(6, max(1, int(style_match.group(1))))
    markdown = re.match(r"^\s{0,3}(#{1,6})\s+\S", text)
    if markdown:
        return len(markdown.group(1))
    numbered = re.match(r"^(\d+(?:\.\d+){0,5})\s+\S", text)
    if numbered and len(text) <= 180:
        return min(6, numbered.group(1).count(".") + 1)
    return None


def plain_blocks(path: Path) -> list[dict[str, Any]]:
    text = read_plain_text(path)
    blocks: list[dict[str, Any]] = []
    buffer: list[str] = []
    block_no = 0

    def flush() -> None:
        nonlocal block_no
        if not buffer:
            return
        value = "\n".join(buffer).strip()
        buffer.clear()
        if value:
            block_no += 1
            blocks.append({"no": block_no, "text": value, "heading_level": heading_level("", value)})

    for line in text.splitlines():
        if not line.strip():
            flush()
            continue
        if re.match(r"^\s{0,3}#{1,6}\s+", line) or (
            re.match(r"^\d+(?:\.\d+){0,5}\s+\S", line) and len(line) <= 180
        ):
            flush()
            block_no += 1
            value = line.strip()
            blocks.append({"no": block_no, "text": value, "heading_level": heading_level("", value)})
        else:
            buffer.append(line.rstrip())
    flush()
    if not blocks and text.strip():
        blocks = [{"no": 1, "text": text.strip(), "heading_level": None}]
    return blocks


def extract_blocks(path: Path) -> list[dict[str, Any]]:
    return docx_blocks(path) if path.suffix.lower() == ".docx" else plain_blocks(path)


def assess_source(
    path: Path,
    *,
    soft_tokens: int = DEFAULT_SOFT_TOKENS,
    hard_tokens: int = DEFAULT_HARD_TOKENS,
    breadth_token_floor: int = DEFAULT_BREADTH_TOKEN_FLOOR,
    breadth_headings: int = DEFAULT_BREADTH_HEADINGS,
) -> dict[str, Any]:
    blocks = extract_blocks(path)
    logical_text = "\n\n".join(block["text"] for block in blocks)
    tokens = estimate_tokens(logical_text)
    heading_count = sum(1 for block in blocks if block["heading_level"] is not None)
    reasons: list[str] = []
    if tokens >= hard_tokens:
        reasons.append(f"estimated_tokens={tokens} >= hard_threshold={hard_tokens}")
    if tokens >= breadth_token_floor and heading_count >= breadth_headings:
        reasons.append(
            f"structural_breadth=headings:{heading_count} at estimated_tokens:{tokens}"
        )
    route = "primary_plan" if reasons else "final_plan"
    if route == "final_plan" and tokens > soft_tokens:
        reasons.append(
            f"between_soft_and_hard_thresholds={soft_tokens}:{hard_tokens}; no breadth trigger"
        )
    return {
        "source": str(path),
        "source_name": path.name,
        "source_bytes": path.stat().st_size,
        "source_sha256": sha256_bytes(path.read_bytes()),
        "logical_blocks": len(blocks),
        "heading_count": heading_count,
        "estimated_tokens": tokens,
        "soft_tokens": soft_tokens,
        "hard_tokens": hard_tokens,
        "breadth_token_floor": breadth_token_floor,
        "breadth_headings": breadth_headings,
        "route": route,
        "reasons": reasons,
    }


def split_oversized_block(text: str, max_tokens: int) -> list[str]:
    if estimate_tokens(text) <= max_tokens:
        return [text]
    max_chars = max_tokens * 3
    parts: list[str] = []
    remaining = text
    while estimate_tokens(remaining) > max_tokens:
        cut = min(len(remaining), max_chars)
        lower = max(1, int(cut * 0.65))
        candidate = remaining.rfind("\n", lower, cut)
        if candidate < 0:
            candidate = remaining.rfind(". ", lower, cut)
            if candidate >= 0:
                candidate += 1
        if candidate < 0:
            candidate = remaining.rfind(" ", lower, cut)
        if candidate <= 0:
            candidate = cut
        parts.append(remaining[:candidate].strip())
        remaining = remaining[candidate:].strip()
    if remaining:
        parts.append(remaining)
    return parts


def normalize_blocks_for_splitting(blocks: list[dict[str, Any]], max_tokens: int) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for block in blocks:
        pieces = split_oversized_block(block["text"], max_tokens)
        for index, piece in enumerate(pieces):
            normalized.append(
                {
                    "no": block["no"],
                    "text": piece,
                    "heading_level": block["heading_level"] if index == 0 else None,
                    "continuation": index > 0,
                }
            )
    return normalized


def make_fragments(
    blocks: list[dict[str, Any]],
    *,
    target_tokens: int = DEFAULT_TARGET_FRAGMENT_TOKENS,
    max_tokens: int = DEFAULT_MAX_FRAGMENT_TOKENS,
) -> list[dict[str, Any]]:
    normalized = normalize_blocks_for_splitting(blocks, max_tokens)
    fragments: list[dict[str, Any]] = []
    current: list[dict[str, Any]] = []
    current_tokens = 0
    heading_path: dict[int, str] = {}
    current_heading_path: list[str] = []

    def flush() -> None:
        nonlocal current, current_tokens, current_heading_path
        if not current:
            return
        text = "\n\n".join(item["text"] for item in current).strip()
        frag_id = f"F{len(fragments) + 1:03d}"
        fragments.append(
            {
                "id": frag_id,
                "text": text,
                "estimated_tokens": estimate_tokens(text),
                "source_block_start": current[0]["no"],
                "source_block_end": current[-1]["no"],
                "heading_path": list(current_heading_path),
                "sha256": sha256_text(text),
            }
        )
        current = []
        current_tokens = 0
        current_heading_path = []

    for block in normalized:
        level = block["heading_level"]
        if level is not None:
            for key in list(heading_path):
                if key >= level:
                    heading_path.pop(key, None)
            heading_path[level] = block["text"]
        block_tokens = estimate_tokens(block["text"])
        starts_new_section = level is not None and current_tokens >= max(800, target_tokens // 3)
        would_exceed = current and current_tokens + block_tokens > max_tokens
        if starts_new_section or would_exceed:
            flush()
        if not current:
            current_heading_path = [heading_path[key] for key in sorted(heading_path)]
        current.append(block)
        current_tokens += block_tokens
        if current_tokens >= target_tokens:
            flush()
    flush()
    return fragments


def package_id_for(path: Path, assessment: dict[str, Any]) -> str:
    return f"{slugify(path.stem)}-{assessment['source_sha256'][:10]}"


def ensure_package_dir(repo_root: Path, package_id: str) -> Path:
    root = (repo_root / PREPARED_ROOT).resolve()
    root.mkdir(parents=True, exist_ok=True)
    package = (root / package_id).resolve()
    if package.parent != root:
        raise PreplanError("Invalid prepared package id")
    if package.exists():
        raise PreplanError(f"Prepared package already exists: {package}")
    package.mkdir()
    (package / "fragments").mkdir()
    (package / "digests").mkdir()
    return package


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PreplanError(f"Cannot read JSON {path}: {exc}") from exc


def create_package(
    repo_root: Path,
    source: Path,
    assessment: dict[str, Any],
    *,
    package_id: str | None = None,
    target_tokens: int = DEFAULT_TARGET_FRAGMENT_TOKENS,
    max_tokens: int = DEFAULT_MAX_FRAGMENT_TOKENS,
) -> tuple[Path, dict[str, Any]]:
    blocks = extract_blocks(source)
    fragments = make_fragments(blocks, target_tokens=target_tokens, max_tokens=max_tokens)
    package_id = package_id or package_id_for(source, assessment)
    package = ensure_package_dir(repo_root, package_id)
    index: list[dict[str, Any]] = []
    for fragment in fragments:
        title = fragment["heading_path"][-1] if fragment["heading_path"] else f"Source blocks {fragment['source_block_start']}-{fragment['source_block_end']}"
        filename = f"{fragment['id']}-{slugify(title, 'source')}.md"
        relative = Path("fragments") / filename
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
        "artifacts": {
            "source_index": "SOURCE_INDEX.json",
            "fragments": "fragments/",
            "digests": "digests/",
            "pattern_seeds": "PATTERN_SEEDS.json",
            "coverage_review": "COVERAGE_REVIEW.json",
            "final_plan_input": "FINAL_PLAN_INPUT.md",
        },
        "fragment_count": len(index),
    }
    write_json(package / "package.json", metadata)
    return package, metadata


def batch_fragments(index: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    batches: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    tokens = 0
    for fragment in index:
        next_tokens = int(fragment["estimated_tokens"])
        if current and (
            len(current) >= DEFAULT_MAX_BATCH_FRAGMENTS or tokens + next_tokens > DEFAULT_BATCH_TOKENS
        ):
            batches.append(current)
            current = []
            tokens = 0
        current.append(fragment)
        tokens += next_tokens
    if current:
        batches.append(current)
    return batches


def task_context_boundary(why: str, separated: str) -> dict[str, Any]:
    return {
        "shared_context": [],
        "why_one_todo": why,
        "separate_from": [separated],
    }


def make_primary_spec(repo_root: Path, package: Path, metadata: dict[str, Any]) -> dict[str, Any]:
    index = read_json(package / "SOURCE_INDEX.json")["fragments"]
    batches = batch_fragments(index)
    script = shlex.quote(str(Path(__file__).resolve()))
    package_arg = shlex.quote(str(package))
    tasks: list[dict[str, Any]] = []
    digest_task_ids: list[int] = []

    for batch_no, batch in enumerate(batches, start=1):
        task_id = batch_no
        digest_task_ids.append(task_id)
        digest_id = f"D{batch_no:03d}"
        fragment_ids = [item["id"] for item in batch]
        fragment_paths = [str(package / item["path"]) for item in batch]
        output = package / "digests" / f"{digest_id}.json"
        tasks.append(
            {
                "id": task_id,
                "title": f"Extract planning facts {fragment_ids[0]}–{fragment_ids[-1]}",
                "objective": f"Create source-referenced {digest_id} without losing obligations from fragments {', '.join(fragment_ids)}.",
                "requirement_ids": ["R001", "R002"],
                "complexity": "medium",
                "atomicity_rationale": "This bounded fragment batch fits one cheap worker context and has one independently schema-checkable digest output.",
                "context_boundary": task_context_boundary(
                    "One worker should compare all fragments in this bounded batch so local repeated constraints are normalized without cross-batch context pollution.",
                    "Cross-batch pattern synthesis and whole-source coverage review are separate later TODOs.",
                ),
                "scope": {
                    "in": ["Extract explicit obligations, constraints, interfaces, dependencies, validation implications, pattern candidates and material questions."],
                    "out": ["Do not design implementation architecture or reconcile contradictions without source evidence."],
                    "expected_files": [str(output)],
                },
                "dependencies": [],
                "implementation_guidance": [
                    "Read only these immutable source fragments: " + ", ".join(fragment_paths),
                    f"Write JSON to {output} with digest_id={digest_id}, fragment_ids, obligations, constraints, interfaces, dependencies, validation_implications, pattern_candidates, material_questions.",
                    "Every semantic item must include non-empty source_refs containing only assigned fragment ids; prefer high recall over prose narrative.",
                ],
                "acceptance_criteria": [
                    f"{digest_id} covers exactly fragments {', '.join(fragment_ids)} and every extracted item retains primary-source fragment references."
                ],
                "validation_commands": [
                    f"{shlex.quote(sys.executable)} {script} validate-digest --package {package_arg} --digest {digest_id}"
                ],
                "subtasks": [
                    {"id": "S001", "title": "Read assigned fragments", "objective": "Inspect only the bounded immutable source batch."},
                    {"id": "S002", "title": "Write source-referenced digest", "objective": f"Persist {digest_id} with atomic planning facts and source refs."},
                ],
                "learning_targets": [],
                "provider": "auto",
                "model_tier": "economy",
                "reasoning_effort": "medium",
            }
        )

    synth_id = len(tasks) + 1
    tasks.append(
        {
            "id": synth_id,
            "title": "Synthesize cross-fragment contracts",
            "objective": "Build cross-cutting pattern seeds and a compact workstream index from validated digests, opening raw fragments only for material ambiguity.",
            "requirement_ids": ["R003"],
            "complexity": "high",
            "atomicity_rationale": "Cross-fragment normalization and pattern deduplication require the same compact digest set and produce one coupled synthesis boundary.",
            "context_boundary": task_context_boundary(
                "One synthesis context must compare all bounded digests to detect repeated normative contracts and cross-domain dependencies consistently.",
                "Raw-fragment coverage auditing and final implementation planning remain separate later stages.",
            ),
            "scope": {
                "in": ["Merge repeated normative contracts, index workstreams/dependencies, preserve contradictions and source refs."],
                "out": ["Do not create final implementation TODOs or assign final implementation model tiers."],
                "expected_files": [str(package / "PATTERN_SEEDS.json"), str(package / "WORKSTREAM_INDEX.json")],
            },
            "dependencies": digest_task_ids,
            "implementation_guidance": [
                f"Read validated digest JSON files under {package / 'digests'} first; retrieve raw fragments only when source verification changes the synthesis.",
                "PATTERN_SEEDS.json root is {patterns:[...]}; each pattern needs id, title, contract[], source_refs[], rationale, affected_domains[].",
                "WORKSTREAM_INDEX.json root is {workstreams:[...], dependencies:[...], contradictions:[...]}; every material item retains digest/fragment source_refs.",
            ],
            "acceptance_criteria": ["Cross-cutting contracts and workstreams are compact, source-referenced, and no contradiction is silently resolved."],
            "validation_commands": [
                f"{shlex.quote(sys.executable)} {script} validate-synthesis --package {package_arg}"
            ],
            "subtasks": [
                {"id": "S001", "title": "Compare validated digests", "objective": "Identify repeated contracts, domains and cross-fragment dependencies."},
                {"id": "S002", "title": "Persist synthesis artifacts", "objective": "Write pattern seeds and the workstream/dependency index with provenance."},
            ],
            "learning_targets": [],
            "provider": "auto",
            "model_tier": "standard",
            "reasoning_effort": "medium",
        }
    )

    review_id = synth_id + 1
    tasks.append(
        {
            "id": review_id,
            "title": "Review source coverage and contradictions",
            "objective": "Freshly verify every immutable fragment is represented and material omissions or contradictions are explicit before final planning.",
            "requirement_ids": ["R004"],
            "complexity": "high",
            "atomicity_rationale": "Coverage, provenance and contradiction checks share one independent quality gate whose failure must block the compact handoff.",
            "context_boundary": task_context_boundary(
                "A fresh reviewer needs the source index, all validated digests and synthesis outputs together to challenge omissions without inheriting synthesis reasoning.",
                "Actual software architecture and implementation task decomposition belong to the final planner.",
            ),
            "scope": {
                "in": ["Verify fragment coverage, provenance, contradiction inventory and compact-handoff safety."],
                "out": ["Do not implement software or hide unresolved material findings."],
                "expected_files": [str(package / "COVERAGE_REVIEW.json")],
            },
            "dependencies": [synth_id],
            "implementation_guidance": [
                f"Write {package / 'COVERAGE_REVIEW.json'} with status=approved|blocked, covered_fragment_ids, unresolved_material_findings, notes.",
                "Use a fresh context. Sample/retrieve raw fragments for material claims instead of rereading the whole source by default.",
            ],
            "acceptance_criteria": ["Every SOURCE_INDEX fragment is covered exactly once or more by a validated digest and unresolved material findings are explicit."],
            "validation_commands": [
                f"{shlex.quote(sys.executable)} {script} validate-coverage --package {package_arg}"
            ],
            "subtasks": [
                {"id": "S001", "title": "Audit coverage", "objective": "Compare source index, digest coverage and synthesis provenance."},
                {"id": "S002", "title": "Record review gate", "objective": "Persist approval or blocking findings without rewriting source evidence."},
            ],
            "learning_targets": [],
            "provider": "auto",
            "model_tier": "strong",
            "reasoning_effort": "medium",
        }
    )

    handoff_id = review_id + 1
    tasks.append(
        {
            "id": handoff_id,
            "title": "Build compact final-planning handoff",
            "objective": "Create FINAL_PLAN_INPUT.md that lets the normal planner start from compact indexed evidence and retrieve fragments only when needed.",
            "requirement_ids": ["R004"],
            "complexity": "low",
            "atomicity_rationale": "The handoff is a mechanical projection of already-reviewed artifacts with one package-level validation boundary.",
            "context_boundary": task_context_boundary(
                "One cheap worker can project the validated package index into a concise handoff without reopening source fragments or making architecture decisions.",
                "Final requirement decomposition, architecture and implementation routing are intentionally deferred to normal final planning.",
            ),
            "scope": {
                "in": ["Summarize package identity, workstreams, pattern seeds, contradictions and retrieval pointers."],
                "out": ["Do not paste all source fragments or preassign final implementation routes."],
                "expected_files": [str(package / "FINAL_PLAN_INPUT.md")],
            },
            "dependencies": [review_id],
            "implementation_guidance": [
                f"Write {package / 'FINAL_PLAN_INPUT.md'} from SOURCE_INDEX, digests, PATTERN_SEEDS, WORKSTREAM_INDEX and COVERAGE_REVIEW only.",
                "Keep stable fragment/digest ids and paths. The final planner must be able to retrieve primary evidence without receiving the whole source in context.",
            ],
            "acceptance_criteria": ["The prepared package passes validation and FINAL_PLAN_INPUT points to, rather than copies, the immutable evidence graph."],
            "validation_commands": [
                f"{shlex.quote(sys.executable)} {script} validate-package --package {package_arg}"
            ],
            "subtasks": [
                {"id": "S001", "title": "Project compact handoff", "objective": "Create the final-planning entry document from reviewed compact artifacts."},
                {"id": "S002", "title": "Validate prepared package", "objective": "Run the deterministic package gate before normal final planning."},
            ],
            "learning_targets": [],
            "provider": "auto",
            "model_tier": "economy",
            "reasoning_effort": "low",
        }
    )

    return {
        "title": f"Prepare oversized request {metadata['package_id']}",
        "summary": "Create a loss-resistant, source-traceable prepared request package for the ordinary final planning workflow; no product implementation occurs in this plan.",
        "language": "auto",
        "request_analysis": {
            "request_parts": [{"id": "P001", "text": "Prepare the oversized supplied specification so final software planning can resume economically without losing requirements."}],
            "repository_findings": ["Primary planning does not modify product code; repository implementation state is intentionally outside this source-preparation boundary."],
            "research_decision": "No external research is required to split and index the user-supplied source; final planning owns domain research decisions.",
            "research_findings": [],
            "assumptions": [],
            "risks": ["Semantic compression could omit a requirement; immutable fragments, source refs and a fresh coverage review are required mitigations."],
            "open_questions": [],
            "decomposition_strategy": "Deterministically fragment first, extract bounded digests cheaply, synthesize cross-cutting contracts, review coverage freshly, then emit a compact handoff.",
        },
        "requirements": [
            {"id": "R001", "text": "Prepared evidence preserves stable source fragments and provenance for every later derived planning fact.", "source": "inferred", "priority": "must", "request_part_ids": ["P001"]},
            {"id": "R002", "text": "Each bounded fragment batch produces a source-referenced digest that retains explicit obligations and constraints.", "source": "inferred", "priority": "must", "request_part_ids": ["P001"]},
            {"id": "R003", "text": "Cross-fragment synthesis identifies repeated normative patterns, workstreams, dependencies and contradictions without creating implementation TODOs.", "source": "inferred", "priority": "must", "request_part_ids": ["P001"]},
            {"id": "R004", "text": "A fresh coverage gate approves a compact final-planning handoff only when all source fragments are represented and material findings are explicit.", "source": "inferred", "priority": "must", "request_part_ids": ["P001"]},
        ],
        "global_constraints": ["Primary-plan work must not implement product code or bind final implementation model routes."],
        "execution_context": {
            "global": {
                "decision": "omit",
                "rationale": "Each primary TODO receives explicit prepared-package paths; no non-obvious fact is required by every worker beyond its task definition.",
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
            "notes": ["Every fragment batch has its own digest TODO; synthesis, fresh coverage review, and final handoff are sequential independent validation gates."],
        },
        "autostart": True,
        "cleanup_on_success": False,
        "tasks": tasks,
    }


def required_item_sources(items: Any, allowed: set[str], field: str) -> list[str]:
    if not isinstance(items, list):
        raise PreplanError(f"{field} must be a list")
    sources: list[str] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict) or not str(item.get("text", "")).strip():
            raise PreplanError(f"{field}[{index}] must be an object with non-empty text")
        refs = item.get("source_refs")
        if not isinstance(refs, list) or not refs:
            raise PreplanError(f"{field}[{index}] requires source_refs")
        for ref in refs:
            if ref not in allowed:
                raise PreplanError(f"{field}[{index}] references unassigned fragment {ref}")
            sources.append(ref)
    return sources


def validate_digest(package: Path, digest_id: str) -> dict[str, Any]:
    index = read_json(package / "SOURCE_INDEX.json")["fragments"]
    known = {item["id"] for item in index}
    path = package / "digests" / f"{digest_id}.json"
    data = read_json(path)
    if data.get("digest_id") != digest_id:
        raise PreplanError(f"{path}: digest_id mismatch")
    fragment_ids = data.get("fragment_ids")
    if not isinstance(fragment_ids, list) or not fragment_ids or len(fragment_ids) != len(set(fragment_ids)):
        raise PreplanError(f"{path}: fragment_ids must be a non-empty unique list")
    if not set(fragment_ids) <= known:
        raise PreplanError(f"{path}: unknown fragment ids")
    allowed = set(fragment_ids)
    for field in (
        "obligations",
        "constraints",
        "interfaces",
        "dependencies",
        "validation_implications",
        "pattern_candidates",
        "material_questions",
    ):
        required_item_sources(data.get(field, []), allowed, field)
    return data


def load_all_digests(package: Path) -> list[dict[str, Any]]:
    paths = sorted((package / "digests").glob("D*.json"))
    if not paths:
        raise PreplanError("No digest files exist")
    return [validate_digest(package, path.stem) for path in paths]


def validate_synthesis(package: Path) -> None:
    digests = load_all_digests(package)
    known_refs = {ref for digest in digests for ref in digest["fragment_ids"]}
    seeds = read_json(package / "PATTERN_SEEDS.json")
    patterns = seeds.get("patterns") if isinstance(seeds, dict) else None
    if not isinstance(patterns, list):
        raise PreplanError("PATTERN_SEEDS.json must contain patterns[]")
    for index, pattern in enumerate(patterns):
        if not isinstance(pattern, dict):
            raise PreplanError(f"patterns[{index}] must be an object")
        if not str(pattern.get("id", "")).strip() or not str(pattern.get("title", "")).strip():
            raise PreplanError(f"patterns[{index}] requires id/title")
        contract = pattern.get("contract")
        refs = pattern.get("source_refs")
        if not isinstance(contract, list) or not contract:
            raise PreplanError(f"patterns[{index}] requires contract[]")
        if not isinstance(refs, list) or not refs or not set(refs) <= known_refs:
            raise PreplanError(f"patterns[{index}] has invalid source_refs")
    workstreams = read_json(package / "WORKSTREAM_INDEX.json")
    if not isinstance(workstreams, dict) or not isinstance(workstreams.get("workstreams"), list):
        raise PreplanError("WORKSTREAM_INDEX.json requires workstreams[]")


def validate_coverage(package: Path) -> None:
    source = read_json(package / "SOURCE_INDEX.json")["fragments"]
    expected = {item["id"] for item in source}
    digests = load_all_digests(package)
    actual = {fragment for digest in digests for fragment in digest["fragment_ids"]}
    if expected != actual:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise PreplanError(f"Digest coverage mismatch; missing={missing}, extra={extra}")
    validate_synthesis(package)
    review = read_json(package / "COVERAGE_REVIEW.json")
    covered = review.get("covered_fragment_ids") if isinstance(review, dict) else None
    if not isinstance(covered, list) or set(covered) != expected:
        raise PreplanError("COVERAGE_REVIEW covered_fragment_ids must exactly match SOURCE_INDEX")
    status = review.get("status")
    if status not in {"approved", "blocked"}:
        raise PreplanError("COVERAGE_REVIEW status must be approved or blocked")
    unresolved = review.get("unresolved_material_findings")
    if not isinstance(unresolved, list):
        raise PreplanError("COVERAGE_REVIEW requires unresolved_material_findings[]")
    if status == "approved" and unresolved:
        raise PreplanError("Approved coverage review cannot contain unresolved material findings")


def validate_package(package: Path) -> None:
    metadata = read_json(package / "package.json")
    source_index = read_json(package / "SOURCE_INDEX.json")
    fragments = source_index.get("fragments") if isinstance(source_index, dict) else None
    if not isinstance(fragments, list) or not fragments:
        raise PreplanError("SOURCE_INDEX.json requires fragments[]")
    for fragment in fragments:
        path = package / fragment["path"]
        if not path.is_file():
            raise PreplanError(f"Missing fragment file: {path}")
    validate_coverage(package)
    review = read_json(package / "COVERAGE_REVIEW.json")
    if review.get("status") != "approved":
        raise PreplanError("Prepared package is blocked by COVERAGE_REVIEW")
    handoff = package / "FINAL_PLAN_INPUT.md"
    if not handoff.is_file() or len(handoff.read_text(encoding="utf-8").strip()) < 100:
        raise PreplanError("FINAL_PLAN_INPUT.md is missing or too shallow")
    metadata["state"] = "ready_for_final_planning"
    metadata["validated_at"] = now_utc()
    write_json(package / "package.json", metadata)


def command_assess(args: argparse.Namespace) -> None:
    source = safe_source_path(args.file)
    result = assess_source(
        source,
        soft_tokens=args.soft_tokens,
        hard_tokens=args.hard_tokens,
        breadth_token_floor=args.breadth_token_floor,
        breadth_headings=args.breadth_headings,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


def command_split(args: argparse.Namespace) -> None:
    repo_root = Path(args.repo_root).expanduser().resolve()
    source = safe_source_path(args.file)
    assessment = assess_source(source, soft_tokens=args.soft_tokens, hard_tokens=args.hard_tokens)
    package, metadata = create_package(
        repo_root,
        source,
        assessment,
        package_id=args.package_id,
        target_tokens=args.target_fragment_tokens,
        max_tokens=args.max_fragment_tokens,
    )
    print(json.dumps({"package": str(package), "metadata": metadata}, ensure_ascii=False, indent=2))


def command_prepare(args: argparse.Namespace) -> None:
    repo_root = Path(args.repo_root).expanduser().resolve()
    source = safe_source_path(args.file)
    assessment = assess_source(
        source,
        soft_tokens=args.soft_tokens,
        hard_tokens=args.hard_tokens,
        breadth_token_floor=args.breadth_token_floor,
        breadth_headings=args.breadth_headings,
    )
    if assessment["route"] != "primary_plan" and not args.force:
        print(json.dumps({"route": "final_plan", "assessment": assessment}, ensure_ascii=False, indent=2))
        raise SystemExit(3)
    package, metadata = create_package(
        repo_root,
        source,
        assessment,
        package_id=args.package_id,
        target_tokens=args.target_fragment_tokens,
        max_tokens=args.max_fragment_tokens,
    )
    spec = make_primary_spec(repo_root, package, metadata)
    spec_path = package / "PRIMARY_PLAN_SPEC.json"
    write_json(spec_path, spec)
    plan_dir = planctl.create_plan(
        repo_root,
        spec,
        args.work_root,
        f"primary-{metadata['package_id']}",
    )
    metadata = read_json(package / "package.json")
    metadata["state"] = "primary_plan_created"
    metadata["primary_plan"] = str(plan_dir)
    write_json(package / "package.json", metadata)
    print(json.dumps({"route": "primary_plan", "assessment": assessment, "package": str(package), "primary_plan": str(plan_dir)}, ensure_ascii=False, indent=2))


def command_validate_digest(args: argparse.Namespace) -> None:
    package = Path(args.package).expanduser().resolve()
    validate_digest(package, args.digest)
    print(f"VALID {args.digest}")


def command_validate_synthesis(args: argparse.Namespace) -> None:
    validate_synthesis(Path(args.package).expanduser().resolve())
    print("VALID SYNTHESIS")


def command_validate_coverage(args: argparse.Namespace) -> None:
    validate_coverage(Path(args.package).expanduser().resolve())
    print("VALID COVERAGE")


def command_validate_package(args: argparse.Namespace) -> None:
    validate_package(Path(args.package).expanduser().resolve())
    print("VALID PACKAGE")


def common_threshold_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--soft-tokens", type=int, default=DEFAULT_SOFT_TOKENS)
    parser.add_argument("--hard-tokens", type=int, default=DEFAULT_HARD_TOKENS)
    parser.add_argument("--breadth-token-floor", type=int, default=DEFAULT_BREADTH_TOKEN_FLOOR)
    parser.add_argument("--breadth-headings", type=int, default=DEFAULT_BREADTH_HEADINGS)


def common_split_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--package-id")
    parser.add_argument("--target-fragment-tokens", type=int, default=DEFAULT_TARGET_FRAGMENT_TOKENS)
    parser.add_argument("--max-fragment-tokens", type=int, default=DEFAULT_MAX_FRAGMENT_TOKENS)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    assess = sub.add_parser("assess", help="Measure request working-set pressure without echoing the request")
    assess.add_argument("--file", required=True)
    common_threshold_args(assess)
    assess.set_defaults(func=command_assess)

    split = sub.add_parser("split", help="Create immutable source fragments and source index")
    split.add_argument("--repo-root", default=".")
    split.add_argument("--file", required=True)
    common_threshold_args(split)
    common_split_args(split)
    split.set_defaults(func=command_split)

    prepare = sub.add_parser("prepare", help="Create prepared package skeleton and resumable primary plan")
    prepare.add_argument("--repo-root", default=".")
    prepare.add_argument("--work-root", default=planctl.WORK_ROOT_DEFAULT)
    prepare.add_argument("--file", required=True)
    prepare.add_argument("--force", action="store_true")
    common_threshold_args(prepare)
    common_split_args(prepare)
    prepare.set_defaults(func=command_prepare)

    digest = sub.add_parser("validate-digest", help="Validate one source-referenced digest")
    digest.add_argument("--package", required=True)
    digest.add_argument("--digest", required=True)
    digest.set_defaults(func=command_validate_digest)

    synthesis = sub.add_parser("validate-synthesis", help="Validate pattern/workstream synthesis artifacts")
    synthesis.add_argument("--package", required=True)
    synthesis.set_defaults(func=command_validate_synthesis)

    coverage = sub.add_parser("validate-coverage", help="Validate source coverage and fresh review artifact")
    coverage.add_argument("--package", required=True)
    coverage.set_defaults(func=command_validate_coverage)

    package = sub.add_parser("validate-package", help="Validate the complete prepared final-planning package")
    package.add_argument("--package", required=True)
    package.set_defaults(func=command_validate_package)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
        return 0
    except PreplanError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except planctl.PlanError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
