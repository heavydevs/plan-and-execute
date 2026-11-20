#!/usr/bin/env python3
"""Deterministically prepare oversized requests for resumable final planning."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import os
import re
import shlex
import shutil
import stat
import subprocess
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
DEPENDENCY_REFS = 40
TARGET_FRAGMENT_TOKENS = 4_500
MAX_FRAGMENT_TOKENS = 6_500
BATCH_TOKENS = 9_000
MAX_BATCH_FRAGMENTS = 4
PREPARED_ROOT = Path(".ai-work") / "prepared"
# v3: sdt/customXml-wrapped rows/cells/blocks/runs are traversed; unhandled text-bearing elements are recorded.
# v4: hierarchical explicit obligation ids (REQ-7.1, REQ-007-A) are extracted whole.
EXTRACTION_VERSION = "ooxml-text-v4"
HASH_CHUNK_BYTES = 1024 * 1024
MAX_DOCX_ARCHIVE_BYTES = 50 * 1024 * 1024
MAX_DOCX_ENTRIES = 512
MAX_DOCX_XML_BYTES = 20 * 1024 * 1024
MAX_DOCX_COMPRESSION_RATIO = 100.0
MIN_RATIO_CHECK_BYTES = 16 * 1024
MAX_XML_DEPTH = 64
# Word tables hold at most 63 grid columns; a larger gridSpan/gridBefore/row extent is hostile or unsupported.
MAX_DOCX_TABLE_COLUMNS = 64
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
MC_NS = "http://schemas.openxmlformats.org/markup-compatibility/2006"
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
_DTD_RE = re.compile(rb"<!(?:DOCTYPE|ENTITY)\b", re.I)
_XML_DECL_ENCODING_RE = re.compile(rb"\A\s*<\?xml\b[^>]*?\bencoding\s*=\s*[\"']([^\"']*)[\"']", re.I)
_ALLOWED_XML_ENCODINGS = {"utf-8", "utf8", "us-ascii", "ascii"}


class PreplanError(RuntimeError):
    pass


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    path.write_bytes(data.encode("utf-8"))


def _is_link(path: Path) -> bool:
    if path.is_symlink():
        return True
    is_junction = getattr(os.path, "isjunction", None)
    if is_junction and is_junction(path):
        return True
    if sys.platform == "win32":
        try:
            attrs = getattr(os.lstat(path), "st_file_attributes", 0)
            if attrs & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400):
                return True
        except OSError:
            pass
    return False


def read_json(path: Path) -> Any:
    if _is_link(path):
        raise PreplanError(f"Symlink JSON is not allowed: {path}")
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
    raw = Path(value).expanduser()
    if _is_link(raw):
        raise PreplanError(f"Symlink source is not allowed: {raw}")
    if not raw.exists() or not raw.is_file():
        raise PreplanError(f"Source must be a regular file: {raw}")
    path = raw.resolve()
    if _is_link(path) or not path.is_file():
        raise PreplanError(f"Source must be a regular file: {path}")
    return path


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def sha256_file(path: Path) -> str:
    if _is_link(path) or not path.is_file():
        raise PreplanError(f"Cannot hash non-regular or symlink file: {path}")
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            while True:
                chunk = handle.read(HASH_CHUNK_BYTES)
                if not chunk:
                    break
                digest.update(chunk)
    except OSError as exc:
        raise PreplanError(f"Cannot read file for hashing {path}: {exc}") from exc
    return digest.hexdigest()


def canonical_block_stream_sha256(blocks: list[dict[str, Any]]) -> str:
    canonical = [
        {
            "no": int(item["no"]),
            "anchor": str(item.get("anchor") or f"b:{item['no']}"),
            "kind": str(item.get("kind") or "paragraph"),
            "heading_level": item.get("heading_level"),
            "text": str(item["text"]),
            "table_depth": int(item.get("table_depth", 0)),
        }
        for item in blocks
    ]
    payload = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(payload)


def safe_package_path(package: Path, rel_path: str, *, must_exist: bool = True) -> Path:
    if not isinstance(rel_path, str) or not rel_path.strip():
        raise PreplanError("Empty package-relative path")
    if "\\" in rel_path or rel_path.startswith("/"):
        raise PreplanError(f"Invalid package-relative path: {rel_path}")
    rel = Path(rel_path)
    if rel.is_absolute() or ".." in rel.parts or not rel.parts:
        raise PreplanError(f"Escaping package path is not allowed: {rel_path}")
    pkg_root = package.resolve()
    current = package
    for part in rel.parts:
        current = current / part
        if _is_link(current):
            raise PreplanError(f"Symlink inside prepared package is not allowed: {rel_path}")
    target = current.resolve()
    if not target.is_relative_to(pkg_root):
        raise PreplanError(f"Path escapes prepared package: {rel_path}")
    if must_exist and (_is_link(current) or not target.is_file()):
        raise PreplanError(f"Missing package file: {rel_path}")
    return target


def extract_fragment_source_text(content: str) -> str:
    marker = "\n## Source text\n\n"
    pos = content.find(marker)
    if pos < 0:
        raise PreplanError("Fragment is missing '## Source text' section")
    body = content[pos + len(marker):]
    if body.endswith("\r\n"):
        body = body[:-2]
    elif body.endswith("\n"):
        body = body[:-1]
    return body


def fragments_manifest_hash(index: list[dict[str, Any]]) -> str:
    summary = [
        {
            "id": item.get("id"),
            "path": item.get("path"),
            "source_text_sha256": item.get("source_text_sha256"),
            "file_sha256": item.get("file_sha256"),
        }
        for item in index
    ]
    return sha256_bytes(json.dumps(summary, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


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


def _w(tag: str) -> str:
    return f"{{{W_NS}}}{tag}"


def _mc(tag: str) -> str:
    return f"{{{MC_NS}}}{tag}"


def _m(tag: str) -> str:
    return f"{{{M_NS}}}{tag}"


def _check_xml_bytes(xml_bytes: bytes, path: Path) -> None:
    """Accept only UTF-8 XML so the byte-level DTD/ENTITY guard sees what expat will parse."""
    if b"\x00" in xml_bytes or xml_bytes.startswith((b"\xff\xfe", b"\xfe\xff")):
        raise PreplanError(f"DOCX XML must be UTF-8 encoded (UTF-16/UTF-32 or NUL bytes rejected) in {path}")
    body = xml_bytes[3:] if xml_bytes.startswith(b"\xef\xbb\xbf") else xml_bytes
    try:
        body.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PreplanError(f"DOCX XML is not valid UTF-8 in {path}") from exc
    declared = _XML_DECL_ENCODING_RE.match(body)
    if declared and declared.group(1).decode("ascii", "replace").strip().lower() not in _ALLOWED_XML_ENCODINGS:
        raise PreplanError(f"DOCX XML declares a non-UTF-8 encoding in {path}")
    if _DTD_RE.search(body):
        raise PreplanError(f"Unsafe XML DTD/ENTITY declaration rejected in {path}")


A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
_TEXT_TAGS = frozenset({f"{{{W_NS}}}t", f"{{{W_NS}}}delText", f"{{{M_NS}}}t", f"{{{A_NS}}}t"})
_TRACKED_TAGS = {
    f"{{{W_NS}}}ins": "tracked_change_insertion",
    f"{{{W_NS}}}del": "tracked_change_deletion",
    f"{{{W_NS}}}moveTo": "tracked_change_move_to",
    f"{{{W_NS}}}moveFrom": "tracked_change_move_from",
}


def _has_text(node: ET.Element) -> bool:
    return any(item.tag in _TEXT_TAGS and (item.text or "").strip() for item in node.iter())


def _record_unhandled(unsupported: list[dict[str, Any]], node: ET.Element, location: str, level: str) -> None:
    """Never drop text silently: an element this walker does not traverse is recorded when it carries text."""
    if _has_text(node):
        unsupported.append(
            {
                "kind": f"unhandled_{level}_element",
                "location": location,
                "detail": f"Unhandled {level}-level element {node.tag.split('}')[-1]} with text is not extracted",
                "preview": _node_plain_preview(node),
            }
        )


def _enforce_xml_depth(root: ET.Element, max_depth: int) -> None:
    stack: list[tuple[ET.Element, int]] = [(root, 1)]
    while stack:
        node, depth = stack.pop()
        if depth > max_depth:
            raise PreplanError(f"DOCX XML nesting depth exceeds limit ({max_depth})")
        for child in node:
            stack.append((child, depth + 1))


def _read_bounded_zip_member(
    archive: zipfile.ZipFile,
    info: zipfile.ZipInfo,
    max_bytes: int,
    max_ratio: float,
    min_ratio_bytes: int,
) -> bytes:
    if info.file_size > max_bytes:
        raise PreplanError(f"DOCX XML member {info.filename} exceeds size limit ({info.file_size} > {max_bytes})")
    chunks: list[bytes] = []
    total = 0
    with archive.open(info, "r") as stream:
        while True:
            chunk = stream.read(65536)
            if not chunk:
                break
            total += len(chunk)
            if total > max_bytes:
                raise PreplanError(f"DOCX XML member {info.filename} exceeds uncompressed size limit ({max_bytes} bytes)")
            chunks.append(chunk)
    if total >= min_ratio_bytes:
        compressed = max(1, info.compress_size)
        ratio = total / compressed
        if ratio > max_ratio:
            raise PreplanError(
                f"DOCX member {info.filename} exceeds compression ratio limit ({ratio:.1f}x > {max_ratio:.1f}x)"
            )
    return b"".join(chunks)


def _node_plain_preview(node: ET.Element) -> str:
    parts = [t.text or "" for t in node.iter() if t.tag in _TEXT_TAGS]
    text = re.sub(r"\s+", " ", "".join(parts)).strip()
    return text[:160]


def _record_tracked(unsupported: list[dict[str, Any]], node: ET.Element, location: str, scope: str) -> None:
    kind = _TRACKED_TAGS[node.tag]
    unsupported.append(
        {
            "kind": kind,
            "location": location,
            "detail": f"{scope} tracked change ({node.tag.split('}')[-1]}) recorded rather than silently merged or omitted",
            "preview": _node_plain_preview(node),
        }
    )


def _extract_paragraph_text(
    paragraph: ET.Element,
    anchor: str,
    unsupported: list[dict[str, Any]],
) -> str:
    parts: list[str] = []

    def walk_inline(container: ET.Element) -> None:
        for child in container:
            tag = child.tag
            if tag == _w("r"):
                for sub in child:
                    stag = sub.tag
                    if stag == _w("t"):
                        parts.append(sub.text or "")
                    elif stag == _w("tab"):
                        parts.append("\t")
                    elif stag in {_w("br"), _w("cr")}:
                        parts.append("\n")
                    elif stag in {_w("drawing"), _w("pict")}:
                        unsupported.append(
                            {
                                "kind": "drawing_or_textbox",
                                "location": anchor,
                                "detail": "Drawing, image, or text box inside run is not losslessly extracted",
                                "preview": _node_plain_preview(sub),
                            }
                        )
                    elif stag == _mc("AlternateContent"):
                        # Word 2010+ serializes text boxes and shapes inside runs as mc:AlternateContent.
                        unsupported.append(
                            {
                                "kind": "drawing_or_textbox",
                                "location": anchor,
                                "detail": "mc:AlternateContent inside run (text box/shape) is not losslessly extracted",
                                "preview": _node_plain_preview(sub),
                            }
                        )
                    elif stag == _w("object"):
                        unsupported.append(
                            {
                                "kind": "embedded_object",
                                "location": anchor,
                                "detail": "Embedded OLE object is not losslessly extracted",
                                "preview": _node_plain_preview(sub),
                            }
                        )
                    elif stag in {_w("footnoteReference"), _w("endnoteReference"), _w("commentReference")}:
                        unsupported.append(
                            {
                                "kind": "reference_annotation",
                                "location": anchor,
                                "detail": f"Reference annotation {stag.split('}')[-1]} is outside main body stream",
                            }
                        )
                    elif stag not in {_w("delText"), _w("instrText"), _w("rPr")}:
                        _record_unhandled(unsupported, sub, anchor, "run")
            elif tag in {_w("hyperlink"), _w("smartTag"), _w("fldSimple"), _w("customXml"), _w("dir"), _w("bdo")}:
                walk_inline(child)
            elif tag == _w("sdt"):
                content = child.find(_w("sdtContent"))
                if content is not None:
                    walk_inline(content)
            elif tag in _TRACKED_TAGS:
                _record_tracked(unsupported, child, anchor, "Inline")
            elif tag in {_m("oMath"), _m("oMathPara")}:
                unsupported.append(
                    {
                        "kind": "math_equation",
                        "location": anchor,
                        "detail": "Office Math equation is not losslessly extracted",
                        "preview": _node_plain_preview(child),
                    }
                )
            elif tag == _w("subDoc"):
                unsupported.append(
                    {
                        "kind": "sub_document",
                        "location": anchor,
                        "detail": "Linked sub-document content is outside this package part",
                    }
                )
            elif tag == _mc("AlternateContent"):
                unsupported.append(
                    {
                        "kind": "alternate_content",
                        "location": anchor,
                        "detail": "mc:AlternateContent (shapes/text boxes/equations) is not losslessly extracted",
                        "preview": _node_plain_preview(child),
                    }
                )
            elif tag in {_w("drawing"), _w("pict"), _w("txbxContent")}:
                unsupported.append(
                    {
                        "kind": "drawing_or_textbox",
                        "location": anchor,
                        "detail": "Drawing or text box element is not losslessly extracted",
                        "preview": _node_plain_preview(child),
                    }
                )
            elif tag == _w("object"):
                unsupported.append(
                    {
                        "kind": "embedded_object",
                        "location": anchor,
                        "detail": "Embedded object is not losslessly extracted",
                        "preview": _node_plain_preview(child),
                    }
                )
            elif tag != _w("pPr"):
                _record_unhandled(unsupported, child, anchor, "inline")

    walk_inline(paragraph)
    return "".join(parts).strip()


def extract_docx(
    path: Path,
    *,
    max_archive_bytes: int = MAX_DOCX_ARCHIVE_BYTES,
    max_entries: int = MAX_DOCX_ENTRIES,
    max_xml_bytes: int = MAX_DOCX_XML_BYTES,
    max_compression_ratio: float = MAX_DOCX_COMPRESSION_RATIO,
    min_ratio_check_bytes: int = MIN_RATIO_CHECK_BYTES,
    max_xml_depth: int = MAX_XML_DEPTH,
    max_table_columns: int = MAX_DOCX_TABLE_COLUMNS,
) -> dict[str, Any]:
    path = safe_source(path)
    archive_size = path.stat().st_size
    if archive_size > max_archive_bytes:
        raise PreplanError(f"DOCX archive exceeds size limit ({archive_size} > {max_archive_bytes} bytes): {path}")
    unsupported: list[dict[str, Any]] = []
    try:
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            if len(infos) > max_entries:
                raise PreplanError(f"DOCX archive exceeds entry count limit ({len(infos)} > {max_entries}): {path}")
            by_name = {info.filename: info for info in infos}
            if "word/document.xml" not in by_name:
                raise PreplanError(f"Invalid .docx source (missing word/document.xml): {path}")
            xml_bytes = _read_bounded_zip_member(
                archive,
                by_name["word/document.xml"],
                max_xml_bytes,
                max_compression_ratio,
                min_ratio_check_bytes,
            )
            for info in infos:
                name = info.filename
                if (
                    re.fullmatch(r"word/(?:header\d*|footer\d*|footnotes|endnotes|comments)\.xml", name)
                    or name.startswith(("word/embeddings/", "word/media/"))
                ):
                    unsupported.append(
                        {
                            "kind": "non_body_part",
                            "location": name,
                            "detail": f"Auxiliary DOCX package part {name} is not merged into body blocks",
                        }
                    )
    except zipfile.BadZipFile as exc:
        raise PreplanError(f"Invalid .docx source: {path}") from exc

    _check_xml_bytes(xml_bytes, path)
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise PreplanError(f"Invalid .docx XML in {path}: {exc}") from exc
    _enforce_xml_depth(root, max_xml_depth)

    body = root.find(_w("body"))
    if body is None:
        raise PreplanError(f"Invalid .docx source (missing w:body): {path}")

    blocks: list[dict[str, Any]] = []

    def emit_paragraph(
        paragraph: ET.Element,
        anchor: str,
        *,
        depth: int,
        grid_span: int = 1,
        target_list: list[dict[str, Any]],
    ) -> None:
        text = _extract_paragraph_text(paragraph, anchor, unsupported)
        if not text:
            return
        style_node = paragraph.find(f"./{_w('pPr')}/{_w('pStyle')}")
        style = "" if style_node is None else style_node.attrib.get(_w("val"), "")
        entry: dict[str, Any] = {
            "no": 0,
            "anchor": anchor,
            "kind": "paragraph" if depth == 0 else "table_cell",
            "text": text,
            "heading_level": detect_heading(style, text) if depth == 0 else None,
            "table_depth": depth,
        }
        if depth > 0 and grid_span > 1:
            entry["grid_span"] = grid_span
        target_list.append(entry)

    def grid_value(node: ET.Element | None, default: int, location: str, label: str) -> int:
        """Bounded integer grid attribute; hostile values fail fast instead of driving per-column loops."""
        if node is None:
            return default
        match = re.fullmatch(r"([+-]?)0*(\d+)", str(node.attrib.get(_w("val"), default)).strip())
        if not match or match.group(1) == "-":
            return default
        if len(match.group(2)) > 6:
            raise PreplanError(f"DOCX table {label} at {location} exceeds column limit ({max_table_columns})")
        value = int(match.group(2))
        if value > max_table_columns:
            raise PreplanError(f"DOCX table {label}={value} at {location} exceeds column limit ({max_table_columns})")
        return max(default, value)

    def wrapped_children(container: ET.Element, wanted: str, location: str, level: str) -> Any:
        """Yield wanted rows/cells in order, descending through w:sdt/w:sdtContent and w:customXml wrappers."""
        for child in container:
            tag = child.tag
            if tag == wanted:
                yield child
            elif tag == _w("sdt"):
                content = child.find(_w("sdtContent"))
                if content is not None:
                    yield from wrapped_children(content, wanted, location, level)
            elif tag == _w("customXml"):
                yield from wrapped_children(child, wanted, location, level)
            elif tag in _TRACKED_TAGS:
                unsupported.append(
                    {
                        "kind": "tracked_change_table",
                        "location": location,
                        "detail": "Tracked change inside table recorded rather than silently omitted",
                        "preview": _node_plain_preview(child),
                    }
                )
            else:
                _record_unhandled(unsupported, child, location, level)

    def walk_table(table: ET.Element, tbl_anchor: str, depth: int, target_list: list[dict[str, Any]]) -> None:
        active_vmerge: dict[int, set[str]] = {}
        row_idx = 0
        for row in wrapped_children(table, _w("tr"), tbl_anchor, "table"):
            row_idx += 1
            row_anchor = f"{tbl_anchor}/r:{row_idx}"
            tr_pr = row.find(_w("trPr"))
            grid_before = grid_value(None if tr_pr is None else tr_pr.find(_w("gridBefore")), 0, row_anchor, "gridBefore")
            col_cursor = 1 + grid_before
            for col in range(1, col_cursor):
                active_vmerge.pop(col, None)
            active_hmerge_texts: set[str] | None = None
            for cell in wrapped_children(row, _w("tc"), row_anchor, "row"):
                tc_pr = cell.find(_w("tcPr"))
                grid_span = 1
                vmerge_state: str | None = None
                hmerge_state: str | None = None
                if tc_pr is not None:
                    grid_span = grid_value(tc_pr.find(_w("gridSpan")), 1, row_anchor, "gridSpan")
                    vm_node = tc_pr.find(_w("vMerge"))
                    if vm_node is not None:
                        vmerge_state = (vm_node.attrib.get(_w("val")) or "continue").lower()
                    hm_node = tc_pr.find(_w("hMerge"))
                    if hm_node is not None:
                        hmerge_state = (hm_node.attrib.get(_w("val")) or "continue").lower()

                if col_cursor + grid_span - 1 > max_table_columns:
                    raise PreplanError(f"DOCX table row {row_anchor} exceeds column limit ({max_table_columns})")
                col_cols = range(col_cursor, col_cursor + grid_span)
                col_label = f"c:{col_cursor}" if grid_span == 1 else f"c:{col_cursor}-{col_cursor + grid_span - 1}"
                cell_anchor = f"{row_anchor}/{col_label}"

                cell_items: list[dict[str, Any]] = []
                walk_container(cell, f"{cell_anchor}/", depth=depth, grid_span=grid_span, target_list=cell_items)

                is_vmerge_cont = vmerge_state is not None and vmerge_state != "restart"
                is_hmerge_cont = hmerge_state is not None and hmerge_state != "restart"
                origin_texts: set[str] = set()
                if is_vmerge_cont:
                    for col in col_cols:
                        origin_texts |= active_vmerge.get(col, set())
                if is_hmerge_cont and active_hmerge_texts is not None:
                    origin_texts |= active_hmerge_texts

                if is_vmerge_cont or is_hmerge_cont:
                    has_nested = any(item.get("table_depth", depth) > depth for item in cell_items)
                    non_dup = [item for item in cell_items if item["text"] not in origin_texts]
                    if has_nested or non_dup:
                        target_list.extend(cell_items if has_nested else non_dup)
                else:
                    target_list.extend(cell_items)
                    cell_texts = {item["text"] for item in cell_items}
                    if vmerge_state == "restart":
                        for col in col_cols:
                            active_vmerge[col] = set(cell_texts)
                    else:
                        for col in col_cols:
                            active_vmerge.pop(col, None)
                    if hmerge_state == "restart":
                        active_hmerge_texts = set(cell_texts)
                    else:
                        active_hmerge_texts = None

                col_cursor += grid_span

    def walk_container(
        container: ET.Element,
        prefix: str,
        *,
        depth: int,
        grid_span: int,
        target_list: list[dict[str, Any]],
    ) -> None:
        p_idx = 0
        tbl_idx = 0
        sdt_idx = 0
        cx_idx = 0
        location = prefix.rstrip("/") or "body"
        for child in container:
            tag = child.tag
            if tag == _w("p"):
                p_idx += 1
                emit_paragraph(child, f"{prefix}p:{p_idx}", depth=depth, grid_span=grid_span, target_list=target_list)
            elif tag == _w("tbl"):
                tbl_idx += 1
                walk_table(child, f"{prefix}tbl:{tbl_idx}", depth=depth + 1, target_list=target_list)
            elif tag == _w("sdt"):
                content = child.find(_w("sdtContent"))
                if content is not None:
                    sdt_idx += 1
                    walk_container(content, f"{prefix}sdt:{sdt_idx}/", depth=depth, grid_span=grid_span, target_list=target_list)
            elif tag == _w("customXml"):
                cx_idx += 1
                walk_container(child, f"{prefix}cx:{cx_idx}/", depth=depth, grid_span=grid_span, target_list=target_list)
            elif tag in _TRACKED_TAGS:
                _record_tracked(unsupported, child, location, "Container-level")
            elif tag in {_w("drawing"), _w("pict"), _w("txbxContent"), _w("object"), _mc("AlternateContent")}:
                unsupported.append(
                    {
                        "kind": "unsupported_block",
                        "location": location,
                        "detail": f"Unsupported block element {tag.split('}')[-1]} recorded",
                        "preview": _node_plain_preview(child),
                    }
                )
            elif tag == _w("altChunk"):
                unsupported.append(
                    {
                        "kind": "alt_chunk",
                        "location": location,
                        "detail": "Imported w:altChunk content (external part) is not extracted",
                    }
                )
            elif tag not in {_w("tcPr"), _w("sectPr"), _w("sdtPr"), _w("sdtEndPr")}:
                _record_unhandled(unsupported, child, location, "block")

    walk_container(body, "", depth=0, grid_span=1, target_list=blocks)
    for idx, block in enumerate(blocks, 1):
        block["no"] = idx
    if not blocks:
        raise PreplanError(f"No readable paragraphs or table cells in {path}")
    return {
        "blocks": blocks,
        "block_stream_sha256": canonical_block_stream_sha256(blocks),
        "extraction_version": EXTRACTION_VERSION,
        "unsupported_structures": unsupported,
    }


def docx_blocks(
    path: Path,
    *,
    max_archive_bytes: int = MAX_DOCX_ARCHIVE_BYTES,
    max_entries: int = MAX_DOCX_ENTRIES,
    max_xml_bytes: int = MAX_DOCX_XML_BYTES,
    max_compression_ratio: float = MAX_DOCX_COMPRESSION_RATIO,
    min_ratio_check_bytes: int = MIN_RATIO_CHECK_BYTES,
    max_xml_depth: int = MAX_XML_DEPTH,
    max_table_columns: int = MAX_DOCX_TABLE_COLUMNS,
) -> list[dict[str, Any]]:
    return extract_docx(
        path,
        max_archive_bytes=max_archive_bytes,
        max_entries=max_entries,
        max_xml_bytes=max_xml_bytes,
        max_compression_ratio=max_compression_ratio,
        min_ratio_check_bytes=min_ratio_check_bytes,
        max_xml_depth=max_xml_depth,
        max_table_columns=max_table_columns,
    )["blocks"]


def text_blocks(path: Path) -> list[dict[str, Any]]:
    path = safe_source(path)
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
            no = len(blocks) + 1
            is_md_table = all(line.lstrip().startswith("|") for line in value.splitlines() if line.strip()) and "|" in value
            blocks.append(
                {
                    "no": no,
                    "anchor": f"b:{no}",
                    "kind": "table_cell" if is_md_table else "paragraph",
                    "text": value,
                    "heading_level": detect_heading("", value),
                    "table_depth": 1 if is_md_table else 0,
                }
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


def extract_document(path: Path) -> dict[str, Any]:
    path = safe_source(path)
    if path.suffix.lower() == ".docx":
        return extract_docx(path)
    blocks = text_blocks(path)
    return {
        "blocks": blocks,
        "block_stream_sha256": canonical_block_stream_sha256(blocks),
        "extraction_version": EXTRACTION_VERSION,
        "unsupported_structures": [],
    }


def extract_blocks(path: Path) -> list[dict[str, Any]]:
    return extract_document(path)["blocks"]


DEPENDENCY_RE = re.compile(r"(?:depends on|see (?:section|requirement)|as defined in|conflicts? with|contradicts?|supersedes|requires R?\d+)", re.I)
# Hierarchical ids (REQ-7.1, FR-1.2.3, REQ-007-A) are consumed whole so siblings never share an id.
EXPLICIT_OBLIGATION_ID_RE = re.compile(
    r"\b((?:REQ|FR|NFR|OBL|CLAUSE|RULE)[-_]\d+(?:[._-]\d+)*(?:[-_]?[A-Za-z](?![A-Za-z0-9]))?|R\d{2,4}(?:\.\d+)*)\b"
)
_ITEM_ID_RE = re.compile(EXPLICIT_OBLIGATION_ID_RE.pattern, re.I)
NORMATIVE_MODAL_RE = re.compile(
    r"\b(must\s+not|shall\s+not|may\s+not|cannot|can\s+not|must|shall|required\s+to|required|prohibited|forbidden|never)\b",
    re.I,
)
NEGATIVE_MODAL_RE = re.compile(r"\b(must\s+not|shall\s+not|may\s+not|cannot|can\s+not|prohibited|forbidden|never)\b", re.I)
CONTRADICTION_MARKER_RE = re.compile(
    r"\b(contradicts?|conflicts?\s+with|incompatible\s+with|supersedes|mutually\s+exclusive)\b",
    re.I,
)


def _normalize_clause(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


_CANONICAL_ID_RE = re.compile(r"\bobl-[0-9a-f]{6,}\b", re.I)


def _strip_ids(text: str) -> str:
    return _CANONICAL_ID_RE.sub(" ", _ITEM_ID_RE.sub(" ", text))


_UNSPACED_SCRIPT_RE = re.compile(r"[฀-๿぀-ヿ㐀-䶿一-鿿]")


def _substantive(text: str) -> bool:
    """A restatement, not a bare id echo: 3+ words besides ids, or 4+ letters in an unspaced script (CJK/Thai)."""
    stripped = _strip_ids(text)
    words = re.findall(r"[^\W\d_]+", stripped)
    if sum(1 for word in words if len(word) >= 2) >= 3:
        return True
    return bool(_UNSPACED_SCRIPT_RE.search(stripped)) and sum(len(word) for word in words) >= 4


def _block_clauses(block: dict[str, Any]) -> list[tuple[str, str]]:
    """(clause, locator) pairs; the locator is verbatim source text used to find the holding fragment."""
    text = str(block.get("text", "")).strip()
    if not text:
        return []
    clauses: list[tuple[str, str]] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("|") and line.endswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if all(re.fullmatch(r":?-+:?", c or "-") for c in cells):
                continue
            joined = " ".join(c for c in cells if c)
            if joined:
                # A Markdown row is rebuilt from its cells; locate it by the raw table line instead.
                clauses.append((joined, line))
            continue
        parts = re.split(r"(?<=[.!?])\s+", line)
        for part in parts:
            part = part.strip()
            if part:
                clauses.append((part, part))
    return clauses


def _split_block_clauses(block: dict[str, Any]) -> list[str]:
    return [clause for clause, _ in _block_clauses(block)]


def _clause_fragments(locator: str, candidates: list[str], fragment_texts: dict[str, str] | None) -> list[str]:
    """Fragments of a (possibly split) block that contain the clause's source text; all spanned ones if it straddles."""
    if len(candidates) <= 1 or not fragment_texts:
        return list(candidates)
    hits = [fid for fid in candidates if locator in fragment_texts.get(fid, "")]
    return hits or list(candidates)


def extract_obligations(
    blocks: list[dict[str, Any]],
    block_to_fragment: dict[int, str | list[str]] | None = None,
    fragment_texts: dict[str, str] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Deterministically extract unique source obligations and duplicate explicit IDs.

    ``block_to_fragment`` maps a block number to its fragment id, or to every fragment an oversized
    (split) block spans; with ``fragment_texts`` each clause is assigned to the fragment(s) holding it.
    """
    by_canonical: dict[str, dict[str, Any]] = {}
    ordered_ids: list[str] = []
    explicit_to_canonicals: dict[str, list[dict[str, Any]]] = {}

    for block in blocks:
        is_heading = block.get("heading_level") is not None
        anchor = str(block.get("anchor") or f"b:{block['no']}")
        kind = str(block.get("kind") or "paragraph")
        mapped = (block_to_fragment or {}).get(int(block["no"]))
        candidates = [mapped] if isinstance(mapped, str) else [fid for fid in (mapped or []) if fid]
        for clause, locator in _block_clauses(block):
            explicit_match = EXPLICIT_OBLIGATION_ID_RE.search(clause)
            modal_match = NORMATIVE_MODAL_RE.search(clause)
            if is_heading and not modal_match:
                continue
            if not explicit_match and not modal_match:
                continue
            explicit_id = explicit_match.group(1).upper() if explicit_match else None
            norm = _normalize_clause(clause)
            canonical_id = f"OBL-{sha256_text(norm)[:12]}"
            clause_frags = _clause_fragments(locator, candidates, fragment_texts)
            if canonical_id not in by_canonical:
                record: dict[str, Any] = {
                    "canonical_id": canonical_id,
                    "explicit_id": explicit_id,
                    "source_kind": kind,
                    "from_table": kind == "table_cell",
                    "first_anchor": anchor,
                    "anchors": [anchor],
                    "fragment_ids": list(clause_frags),
                    "occurrences": 1,
                    "normalized_text": norm,
                    "text_sha256": sha256_text(norm),
                    "text_preview": clause[:220],
                }
                by_canonical[canonical_id] = record
                ordered_ids.append(canonical_id)
            else:
                record = by_canonical[canonical_id]
                record["occurrences"] += 1
                if anchor not in record["anchors"] and len(record["anchors"]) < 16:
                    record["anchors"].append(anchor)
                for frag_id in clause_frags:
                    if frag_id not in record["fragment_ids"]:
                        record["fragment_ids"].append(frag_id)
                if kind == "table_cell":
                    record["from_table"] = True
            if explicit_id:
                entries = explicit_to_canonicals.setdefault(explicit_id, [])
                if all(e["canonical_id"] != canonical_id for e in entries):
                    entries.append(
                        {
                            "canonical_id": canonical_id,
                            "anchor": anchor,
                            "fragment_id": clause_frags[0] if clause_frags else None,
                            "text_preview": clause[:180],
                        }
                    )

    duplicates: list[dict[str, Any]] = []
    for explicit_id, entries in sorted(explicit_to_canonicals.items()):
        if len(entries) > 1:
            duplicates.append({"explicit_id": explicit_id, "clauses": entries})
    return [by_canonical[cid] for cid in ordered_ids], duplicates


def _obligation_polarity_and_stem(norm_text: str) -> tuple[str | None, str]:
    stripped = re.sub(EXPLICIT_OBLIGATION_ID_RE.pattern, "", norm_text, flags=re.I)
    stripped = re.sub(r"^[\s:\-\u2014\u2013|]+", "", stripped)
    neg = NEGATIVE_MODAL_RE.search(stripped)
    modal = NORMATIVE_MODAL_RE.search(stripped)
    if not modal:
        return None, ""
    polarity = "negative" if neg else "positive"
    stem = NORMATIVE_MODAL_RE.sub(" ", stripped, count=1)
    stem = re.sub(r"[^a-z0-9\s]", " ", stem)
    stem = re.sub(r"\s+", " ", stem).strip()
    return polarity, stem


def detect_contradictions(obligations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Deterministically record contradictory obligations without silently resolving them."""
    found: dict[str, dict[str, Any]] = {}

    def record(kind: str, items: list[dict[str, Any]], detail: str) -> None:
        cids = sorted({item["canonical_id"] for item in items})
        ctr_id = f"CTR-{sha256_text(kind + '|' + '|'.join(cids))[:12]}"
        if ctr_id in found:
            return
        refs = sorted({fid for item in items for fid in item.get("fragment_ids", []) if fid})
        anchors = sorted({item["first_anchor"] for item in items if item.get("first_anchor")})
        found[ctr_id] = {
            "id": ctr_id,
            "kind": kind,
            "obligation_ids": cids,
            "source_refs": refs,
            "anchors": anchors,
            "detail": detail,
            "clauses": [item["text_preview"] for item in items],
        }

    # 1. Explicit contradiction markers in obligations
    for item in obligations:
        if CONTRADICTION_MARKER_RE.search(item["normalized_text"]):
            record(
                "explicit_marker",
                [item],
                f"Explicit contradiction/conflict phrase detected at {item['first_anchor']}",
            )

    # 2. Polarity conflict on identical normalized subject/predicate stem
    by_stem: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for item in obligations:
        polarity, stem = _obligation_polarity_and_stem(item["normalized_text"])
        if polarity and len(stem) >= 12:
            by_stem.setdefault(stem, {"positive": [], "negative": []})[polarity].append(item)
    for stem, buckets in sorted(by_stem.items()):
        if buckets["positive"] and buckets["negative"]:
            pair = [buckets["positive"][0], buckets["negative"][0]]
            record(
                "polarity_conflict",
                pair,
                f"Conflicting positive/negative normative clauses on '{stem[:80]}'",
            )

    # 3. Same explicit requirement ID assigned to conflicting clauses
    by_explicit: dict[str, list[dict[str, Any]]] = {}
    for item in obligations:
        if item.get("explicit_id"):
            by_explicit.setdefault(item["explicit_id"], []).append(item)
    for explicit_id, items in sorted(by_explicit.items()):
        if len(items) > 1:
            record(
                "conflicting_explicit_id",
                items,
                f"Multiple distinct normative clauses share explicit id {explicit_id}",
            )

    return [found[key] for key in sorted(found)]


def _ambiguous_explicit_ids(source_index: dict[str, Any]) -> set[str]:
    """Explicit ids carried by more than one distinct clause (recorded or within the given obligations)."""
    counts: dict[str, int] = {}
    for obl in source_index.get("obligations") or []:
        eid = obl.get("explicit_id") if isinstance(obl, dict) else None
        if isinstance(eid, str) and eid.strip():
            counts[eid.upper()] = counts.get(eid.upper(), 0) + 1
    recorded = {
        str(item.get("explicit_id")).upper()
        for item in source_index.get("duplicate_explicit_ids") or []
        if isinstance(item, dict) and item.get("explicit_id")
    }
    return recorded | {eid for eid, count in counts.items() if count > 1}


def audit_obligation_coverage(
    source_index: dict[str, Any],
    digests: list[dict[str, Any]],
) -> dict[str, Any]:
    """Audit every unique source obligation against validated digests."""
    obligations = source_index.get("obligations") or []
    if not obligations:
        return {
            "total": 0,
            "covered": 0,
            "covered_ids": [],
            "missing_ids": [],
            "missing_reasons": {},
            "missing_table_ids": [],
            "recall": 1.0,
            "table_total": 0,
            "table_recall": 1.0,
        }
    digest_items: list[tuple[set[str], dict[str, Any], str]] = []
    for digest in digests:
        for field in ("obligations", "constraints", "interfaces", "dependencies", "validation_implications", "contradictions"):
            for item in digest.get(field, []):
                refs = set(item.get("source_refs") or [])
                digest_items.append((refs, item, _normalize_clause(str(item.get("text", "")))))

    covered_ids: list[str] = []
    missing_ids: list[str] = []
    missing_table_ids: list[str] = []
    table_total = 0
    table_covered = 0

    def item_ids(item: dict[str, Any]) -> set[str]:
        # Only non-empty string ids count: an absent obligation_id must never equal an absent explicit_id.
        return {
            value.strip().upper()
            for value in (item.get("canonical_id"), item.get("obligation_id"))
            if isinstance(value, str) and value.strip()
        }

    reasons: dict[str, str] = {}
    ambiguous = _ambiguous_explicit_ids(source_index)
    for obl in obligations:
        cid = obl["canonical_id"]
        eid = obl.get("explicit_id")
        if not isinstance(eid, str) or not eid.strip() or eid.upper() in ambiguous:
            # An explicit id shared by several clauses cannot identify one of them: canonical id or text only.
            eid = None
        accepted = {cid.upper()} | ({eid.upper()} if eid else set())
        norm = obl.get("normalized_text", "")
        negative = bool(NEGATIVE_MODAL_RE.search(norm))
        obl_frags = set(obl.get("fragment_ids") or [])
        if obl.get("from_table"):
            table_total += 1
        matched = cited = bare_id = False
        for refs, item, item_norm in digest_items:
            if obl_frags and not (refs & obl_frags):
                continue
            cited = True
            # An id (or the item's first explicit id, never a later cross-reference) counts only with a
            # restatement in any language; a bare id echo is not coverage.
            first_id = _ITEM_ID_RE.search(item_norm)
            id_hit = bool(item_ids(item) & accepted) or bool(eid and first_id and first_id.group(1).upper() == eid.upper())
            if id_hit:
                if _substantive(item_norm):
                    matched = True
                    break
                bare_id = True
            if norm and norm in item_norm:
                matched = True
                break
            if (
                norm
                and len(item_norm) >= max(20, int(len(norm) * 0.6))
                and item_norm in norm
                and bool(NEGATIVE_MODAL_RE.search(item_norm)) == negative
            ):
                matched = True
                break
        if matched:
            covered_ids.append(cid)
            if obl.get("from_table"):
                table_covered += 1
        else:
            key = eid or cid
            missing_ids.append(key)
            if obl.get("from_table"):
                missing_table_ids.append(key)
            if not cited:
                reasons[key] = f"no digest item cites its fragment(s) {sorted(obl_frags)}"
            elif bare_id:
                reasons[key] = "id given without a restatement (needs 3+ words besides ids, or 4+ CJK/Thai letters)"
            else:
                reasons[key] = f"no item carries canonical_id {cid} or restates its text"

    total = len(obligations)
    return {
        "total": total,
        "covered": len(covered_ids),
        "covered_ids": covered_ids,
        "missing_ids": missing_ids,
        "missing_reasons": reasons,
        "missing_table_ids": missing_table_ids,
        "recall": round(len(covered_ids) / total, 6) if total else 1.0,
        "table_total": table_total,
        "table_recall": round(table_covered / table_total, 6) if table_total else 1.0,
    }


def working_set_tokens(blocks: list[dict[str, Any]]) -> int:
    seen: set[str] = set()
    unique: list[str] = []
    for item in blocks:
        key = re.sub(r"\s+", " ", item["text"]).strip().lower()
        if key not in seen:
            seen.add(key)
            unique.append(item["text"])
    return estimate_tokens(chr(10).join(unique)) if unique else 1


def assess_source(
    path: Path,
    soft_tokens: int = SOFT_TOKENS,
    hard_tokens: int = HARD_TOKENS,
    breadth_token_floor: int = BREADTH_TOKEN_FLOOR,
    breadth_headings: int = BREADTH_HEADINGS,
    dependency_refs: int = DEPENDENCY_REFS,
) -> dict[str, Any]:
    path = safe_source(path)
    extracted = extract_document(path)
    blocks = extracted["blocks"]
    unsupported = extracted["unsupported_structures"]
    logical = "\n\n".join(item["text"] for item in blocks)
    raw_tokens = estimate_tokens(logical)
    tokens = working_set_tokens(blocks)
    dependencies = len(DEPENDENCY_RE.findall(logical))
    headings = sum(item["heading_level"] is not None for item in blocks)
    table_cells = sum(item.get("kind") == "table_cell" for item in blocks)
    reasons: list[str] = []
    if tokens >= hard_tokens:
        reasons.append(f"working_set_tokens={tokens} >= hard_threshold={hard_tokens}")
    if tokens >= breadth_token_floor and headings >= breadth_headings:
        reasons.append(f"structural_breadth=headings:{headings} at estimated_tokens:{tokens}")
    if tokens >= breadth_token_floor and dependencies >= dependency_refs:
        reasons.append(f"dependency_density=refs:{dependencies} at working_set_tokens:{tokens}")
    if raw_tokens >= hard_tokens and tokens < hard_tokens and not reasons:
        reasons.append(f"repetitive_size_ignored=raw:{raw_tokens} working_set:{tokens}")
    route = "primary_plan" if any(not r.startswith("repetitive_size_ignored") for r in reasons) else "final_plan"
    if route == "final_plan" and tokens > soft_tokens:
        reasons.append(f"between_thresholds={soft_tokens}:{hard_tokens}; no breadth trigger")
    raw_bytes = path.stat().st_size
    source_hash = sha256_file(path)
    block_stream_hash = extracted["block_stream_sha256"]
    return {
        "source": str(path),
        "source_name": path.name,
        "source_bytes": raw_bytes,
        "source_sha256": source_hash,
        "block_stream_sha256": block_stream_hash,
        "extraction_version": extracted["extraction_version"],
        "logical_blocks": len(blocks),
        "table_cell_blocks": table_cells,
        "unsupported_structures_count": len(unsupported),
        "heading_count": headings,
        "estimated_tokens": tokens,
        "raw_estimated_tokens": raw_tokens,
        "dependency_refs": dependencies,
        "dependency_ref_threshold": dependency_refs,
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
        anchor = str(block.get("anchor") or f"b:{block['no']}")
        kind = str(block.get("kind") or "paragraph")
        for index, piece in enumerate(split_long_text(block["text"], max_tokens)):
            expanded.append(
                {
                    "no": block["no"],
                    "anchor": anchor if index == 0 else f"{anchor}#part{index + 1}",
                    "kind": kind,
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
        anchors = [item["anchor"] for item in current]
        fragments.append(
            {
                "id": f"F{len(fragments) + 1:03d}",
                "text": text,
                "estimated_tokens": estimate_tokens(text),
                "source_block_start": current[0]["no"],
                "source_block_end": current[-1]["no"],
                "source_anchors": anchors,
                "table_cell_blocks": sum(1 for item in current if item.get("kind") == "table_cell"),
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


def derive_fragment_evidence(
    blocks: list[dict[str, Any]],
    target_tokens: int = TARGET_FRAGMENT_TOKENS,
    max_tokens: int = MAX_FRAGMENT_TOKENS,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Fragments, obligations (mapped to every fragment holding them), duplicate ids and contradictions.

    Shared by package creation and consumption-time re-derivation so both use one deterministic pipeline.
    """
    fragments = make_fragments(blocks, target_tokens, max_tokens)
    block_to_fragments: dict[int, list[str]] = {}
    for fragment in fragments:
        for bno in range(int(fragment["source_block_start"]), int(fragment["source_block_end"]) + 1):
            spanned = block_to_fragments.setdefault(bno, [])
            if fragment["id"] not in spanned:
                spanned.append(fragment["id"])
    texts = {fragment["id"]: fragment["text"] for fragment in fragments}
    obligations, duplicates = extract_obligations(blocks, block_to_fragments, texts)
    return fragments, obligations, duplicates, detect_contradictions(obligations)


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
    source = safe_source(source)
    current_source_sha = sha256_file(source)
    if assessment.get("source_sha256") and assessment["source_sha256"] != current_source_sha:
        raise PreplanError("Source file changed since assessment; re-run assess before creating package")
    package_id = package_id or package_id_for(source, assessment)
    root = (repo_root / PREPARED_ROOT).resolve()
    root.mkdir(parents=True, exist_ok=True)
    package = (root / package_id).resolve()
    if package.parent != root or package.exists():
        raise PreplanError(f"Invalid or existing prepared package: {package}")
    (package / "fragments").mkdir(parents=True)
    (package / "digests").mkdir()
    extracted = extract_document(source)
    blocks = extracted["blocks"]
    block_stream_sha = extracted["block_stream_sha256"]
    unsupported = extracted["unsupported_structures"]
    fragments, obligations, duplicate_explicit_ids, source_contradictions = derive_fragment_evidence(
        blocks, target_tokens, max_tokens
    )
    obligations_by_fragment: dict[str, list[str]] = {}
    for obl in obligations:
        for fid in obl.get("fragment_ids", []):
            obligations_by_fragment.setdefault(fid, []).append(obl["canonical_id"])
    index: list[dict[str, Any]] = []
    for fragment in fragments:
        title = fragment["heading_path"][-1] if fragment["heading_path"] else "source"
        relative = Path("fragments") / f"{fragment['id']}-{slugify(title, 'source')}.md"
        anchors = fragment.get("source_anchors") or []
        anchor_span = f"{anchors[0]}–{anchors[-1]}" if anchors else f"{fragment['source_block_start']}–{fragment['source_block_end']}"
        content = (
            f"# {fragment['id']} — source fragment\n\n"
            f"- Source: `{source.name}`\n"
            f"- Source blocks: {fragment['source_block_start']}–{fragment['source_block_end']}\n"
            f"- Source anchors: {anchor_span}\n"
            f"- Source-text SHA-256: `{fragment['sha256']}`\n"
            f"- Estimated tokens: {fragment['estimated_tokens']}\n"
            f"- Heading path: {' > '.join(fragment['heading_path']) or '(none)'}\n\n"
            "## Source text\n\n"
            f"{fragment['text']}\n"
        )
        raw_fragment = content.encode("utf-8")
        (package / relative).write_bytes(raw_fragment)
        index.append(
            {
                "id": fragment["id"],
                "path": relative.as_posix(),
                "estimated_tokens": fragment["estimated_tokens"],
                "source_block_start": fragment["source_block_start"],
                "source_block_end": fragment["source_block_end"],
                "source_anchors": anchors,
                "table_cell_blocks": int(fragment.get("table_cell_blocks", 0)),
                "obligation_ids": obligations_by_fragment.get(fragment["id"], []),
                "heading_path": fragment["heading_path"],
                "source_text_sha256": fragment["sha256"],
                "file_sha256": sha256_bytes(raw_fragment),
                "file_bytes": len(raw_fragment),
            }
        )
    manifest_hash = fragments_manifest_hash(index)
    source_index = {
        "schema_version": 2,
        "extraction_version": EXTRACTION_VERSION,
        "source": {
            "name": source.name,
            "sha256": current_source_sha,
            "bytes": source.stat().st_size,
        },
        "block_stream_sha256": block_stream_sha,
        "block_count": len(blocks),
        "fragmentation": {"target_tokens": int(target_tokens), "max_tokens": int(max_tokens)},
        "unsupported_structures": unsupported,
        "obligations": obligations,
        "duplicate_explicit_ids": duplicate_explicit_ids,
        "detected_contradictions": source_contradictions,
        "fragments_manifest_sha256": manifest_hash,
        "fragments": index,
    }
    write_json(package / "SOURCE_INDEX.json", source_index)
    source_index_sha = sha256_file(package / "SOURCE_INDEX.json")
    metadata = {
        "schema_version": 2,
        "extraction_version": EXTRACTION_VERSION,
        "package_id": package_id,
        "state": "skeleton",
        "created_at": now_utc(),
        "source": {
            "name": source.name,
            "original_path": str(source),
            "bytes": source.stat().st_size,
            "sha256": current_source_sha,
            "block_stream_sha256": block_stream_sha,
            "estimated_tokens": assessment["estimated_tokens"],
            "heading_count": assessment["heading_count"],
        },
        "source_index_sha256": source_index_sha,
        "fragments_manifest_sha256": manifest_hash,
        "unsupported_structures_count": len(unsupported),
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
        root = (fragment.get("heading_path") or [""])[0]
        shifted = bool(current) and root != (current[-1].get("heading_path") or [""])[0] and tokens >= BATCH_TOKENS // 2
        if current and (shifted or len(current) >= MAX_BATCH_FRAGMENTS or tokens + size > BATCH_TOKENS):
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


def make_primary_spec(repo_root: Path, package: Path, metadata: dict[str, Any]) -> dict[str, Any]:
    index = read_json(package / "SOURCE_INDEX.json")["fragments"]
    batches = batch_fragments(index)
    python = shlex.quote(sys.executable)
    script = shlex.quote(str(Path(__file__).resolve()))
    package_root = PREPARED_ROOT / metadata["package_id"]
    pkg_arg = shlex.quote(package_root.as_posix())
    package_locator = "Use $PACKAGE_ROOT from the assigned shared execution context."
    tasks: list[dict[str, Any]] = []

    for batch_no, batch in enumerate(batches, 1):
        digest_id = f"D{batch_no:03d}"
        fragment_ids = [item["id"] for item in batch]
        output = package_root / "digests" / f"{digest_id}.json"
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
                    "expected_files": [output.as_posix()],
                },
                "dependencies": [],
                "implementation_guidance": [
                    package_locator,
                    f"Read only immutable fragments {', '.join(fragment_ids)}; SOURCE_INDEX.json maps each id to its path under $PACKAGE_ROOT/fragments.",
                    f"Write $PACKAGE_ROOT/digests/{digest_id}.json.",
                    "Include digest_id, fragment_ids, obligations, constraints, interfaces, dependencies, validation_implications, pattern_candidates, and material_questions.",
                    "Each semantic item is an object with non-empty text and source_refs using only assigned fragment ids.",
                    "Add fragment_hashes mapping every assigned fragment id to its SOURCE_INDEX file_sha256.",
                    "SOURCE_INDEX fragments[].obligation_ids lists each fragment's source obligations: emit one obligations[] item per id with canonical_id set to it.",
                    "Each such item cites the fragment listing its id and restates the obligation in a few words (any language), never just the id.",
                    f"Every contradictions[] item needs an id: reuse SOURCE_INDEX detected_contradictions ids, else {digest_id}-C1, {digest_id}-C2, ... Record, never resolve.",
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
    pattern_file = package_root / "PATTERN_SEEDS.json"
    workstream_file = package_root / "WORKSTREAM_INDEX.json"
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
                "expected_files": [pattern_file.as_posix(), workstream_file.as_posix()],
            },
            "dependencies": digest_ids,
            "implementation_guidance": [
                package_locator,
                "Read validated digests under $PACKAGE_ROOT/digests first; retrieve raw fragments only when verification changes the synthesis.",
                "Write $PACKAGE_ROOT/PATTERN_SEEDS.json as {patterns:[...]}; each pattern has id, title, contract[], source_refs[], rationale, affected_domains[].",
                "Write $PACKAGE_ROOT/WORKSTREAM_INDEX.json as {workstreams:[...], dependencies:[...], contradictions:[...]} with provenance.",
                "contradictions[] carries every SOURCE_INDEX detected_contradictions id and every digest contradiction id.",
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
    review_file = package_root / "COVERAGE_REVIEW.json"
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
                "expected_files": [review_file.as_posix()],
            },
            "dependencies": [synth_id],
            "implementation_guidance": [
                package_locator,
                "Write $PACKAGE_ROOT/COVERAGE_REVIEW.json with status=approved|blocked, covered_fragment_ids, unresolved_material_findings, notes.",
                "Also write covered_obligation_ids listing every SOURCE_INDEX obligation canonical_id the digests cover.",
                "When approving with contradictions, list each one in recorded_contradictions[] with its id, text and source_refs.",
                "Approve only after listing every SOURCE_INDEX unsupported_structures entry as {kind, location, note} in acknowledged_unsupported_structures; else block.",
                "If SOURCE_INDEX has no obligations, explain in acknowledged_obligation_floor how requirements were checked, or block.",
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
    handoff = package_root / "FINAL_PLAN_INPUT.md"
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
                "expected_files": [handoff.as_posix()],
            },
            "dependencies": [review_id],
            "implementation_guidance": [
                package_locator,
                "Write $PACKAGE_ROOT/FINAL_PLAN_INPUT.md from compact package artifacts only, preserving stable fragment/digest ids and paths.",
                "The final planner must be able to retrieve exact primary evidence on demand without receiving the whole source in context.",
                "Tell the final planner to run validate-consumption --package $PACKAGE_ROOT --source <raw source> --require-source before relying on package artifacts.",
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
        "title": "Prepare oversized request",
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
                "decision": "create",
                "rationale": "Every primary TODO needs the exact prepared-package locator while keeping its own guidance concise.",
                "items": [
                    {
                        "id": "PACKAGE_ROOT",
                        "kind": "fact",
                        "text": f"PACKAGE_ROOT={package_root.as_posix()}",
                        "necessity": "Every primary-plan task needs the exact repository-relative package location to resolve its assigned inputs and outputs.",
                        "source_refs": ["Prepared package metadata"],
                    }
                ],
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


def _schema_version(value: Any) -> int:
    if not isinstance(value, dict):
        return 0
    raw = value.get("schema_version")
    return raw if isinstance(raw, int) and not isinstance(raw, bool) else 0


def _require_sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise PreplanError(f"Missing or invalid {label}")
    return value


def _read_verified_fragment(frag_path: Path, entry: dict[str, Any]) -> str:
    """Read the fragment bytes once, check them against the index and return the verified source text."""
    fid = entry.get("id")
    rel_path = entry.get("path")
    try:
        raw = frag_path.read_bytes()
    except OSError as exc:
        raise PreplanError(f"Cannot read fragment {fid} ({rel_path}): {exc}") from exc
    expected_file_sha = entry.get("file_sha256")
    if expected_file_sha is not None and sha256_bytes(raw) != expected_file_sha:
        raise PreplanError(f"Stale or mutated fragment file {fid} ({rel_path}): file SHA-256 mismatch")
    expected_bytes = entry.get("file_bytes")
    if expected_bytes is not None and len(raw) != expected_bytes:
        raise PreplanError(f"Fragment {fid} ({rel_path}) byte length mismatch")
    try:
        content = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PreplanError(f"Cannot decode fragment {fid} ({rel_path}) as UTF-8: {exc}") from exc
    body = extract_fragment_source_text(content)
    if sha256_text(body) != entry.get("source_text_sha256"):
        raise PreplanError(f"Stale or mutated fragment text {fid} ({rel_path}): source_text SHA-256 mismatch")
    return body


def verify_fragments(package: Path, *, require_v2: bool = False) -> tuple[dict[str, Any], dict[str, Any]]:
    """Recompute every fragment hash from disk.

    Schema-v2 packages (and every caller passing ``require_v2``) must carry all integrity pins; a missing
    pin is an error, never a skipped check. The pins live inside the package, so this chain detects naive
    mutation; ``verify_source_derivation`` re-derives the index from the raw source when it is available.
    """
    if _is_link(package) or not package.is_dir():
        raise PreplanError(f"Prepared package must be a real directory: {package}")
    metadata_path = safe_package_path(package, "package.json")
    index_path = safe_package_path(package, "SOURCE_INDEX.json")
    metadata = read_json(metadata_path)
    source_index = read_json(index_path)
    if not isinstance(metadata, dict) or not isinstance(source_index, dict):
        raise PreplanError("package.json and SOURCE_INDEX.json must be JSON objects")
    fragments = source_index.get("fragments")
    if not isinstance(fragments, list) or not fragments:
        raise PreplanError("SOURCE_INDEX requires non-empty fragments[]")

    # 1. Structure first: ids, duplicates and safe paths, before any hashing.
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    resolved: list[tuple[dict[str, Any], Path]] = []
    for pos, fragment in enumerate(fragments):
        if not isinstance(fragment, dict):
            raise PreplanError(f"SOURCE_INDEX fragments[{pos}] must be an object")
        fid = fragment.get("id")
        rel_path = fragment.get("path")
        if not isinstance(fid, str) or not fid.strip():
            raise PreplanError(f"SOURCE_INDEX fragments[{pos}] is missing a valid id")
        if fid in seen_ids:
            raise PreplanError(f"Duplicate fragment id in SOURCE_INDEX: {fid}")
        seen_ids.add(fid)
        if not isinstance(rel_path, str) or not rel_path.strip():
            raise PreplanError(f"Fragment {fid} is missing path")
        if rel_path in seen_paths:
            raise PreplanError(f"Duplicate fragment path in SOURCE_INDEX: {rel_path}")
        seen_paths.add(rel_path)
        resolved.append((fragment, safe_package_path(package, rel_path)))

    # 2. Package-level pins: mandatory for schema v2, compared whenever present.
    if require_v2 and min(_schema_version(metadata), _schema_version(source_index)) < 2:
        raise PreplanError("Prepared package predates schema_version 2 integrity pins; re-run prepare")
    strict = require_v2 or max(_schema_version(metadata), _schema_version(source_index)) >= 2
    pkg_source = metadata.get("source") if isinstance(metadata.get("source"), dict) else {}
    idx_source = source_index.get("source") if isinstance(source_index.get("source"), dict) else {}
    if strict:
        _require_sha(metadata.get("source_index_sha256"), "package.json source_index_sha256")
        _require_sha(pkg_source.get("sha256"), "package.json source.sha256")
        _require_sha(idx_source.get("sha256"), "SOURCE_INDEX source.sha256")
        _require_sha(pkg_source.get("block_stream_sha256"), "package.json source.block_stream_sha256")
        _require_sha(source_index.get("block_stream_sha256"), "SOURCE_INDEX block_stream_sha256")
        _require_sha(source_index.get("fragments_manifest_sha256"), "SOURCE_INDEX fragments_manifest_sha256")
        _require_sha(metadata.get("fragments_manifest_sha256"), "package.json fragments_manifest_sha256")
        version = metadata.get("extraction_version")
        if not isinstance(version, str) or not version or version != source_index.get("extraction_version"):
            raise PreplanError("extraction_version is missing or differs between package.json and SOURCE_INDEX.json")
    expected_index_sha = metadata.get("source_index_sha256")
    if expected_index_sha is not None and sha256_file(index_path) != expected_index_sha:
        raise PreplanError("SOURCE_INDEX.json SHA-256 mismatch with package.json")
    if pkg_source.get("sha256") and idx_source.get("sha256") and pkg_source["sha256"] != idx_source["sha256"]:
        raise PreplanError("Raw source SHA-256 mismatch between package.json and SOURCE_INDEX.json")
    if (
        pkg_source.get("block_stream_sha256")
        and source_index.get("block_stream_sha256")
        and pkg_source["block_stream_sha256"] != source_index["block_stream_sha256"]
    ):
        raise PreplanError("Extracted block-stream SHA-256 mismatch between package.json and SOURCE_INDEX.json")
    expected_manifest = source_index.get("fragments_manifest_sha256")
    if expected_manifest is not None and fragments_manifest_hash(fragments) != expected_manifest:
        raise PreplanError("SOURCE_INDEX fragments_manifest_sha256 mismatch")
    if metadata.get("fragments_manifest_sha256") is not None and expected_manifest != metadata["fragments_manifest_sha256"]:
        raise PreplanError("package.json fragments_manifest_sha256 mismatch")

    # 3. Content: every fragment is read once and checked against its recorded hashes.
    for fragment, frag_path in resolved:
        fid = fragment["id"]
        expected_text_sha = fragment.get("source_text_sha256")
        if not isinstance(expected_text_sha, str) or not expected_text_sha:
            raise PreplanError(f"Fragment {fid} is missing source_text_sha256")
        if strict:
            _require_sha(fragment.get("file_sha256"), f"fragment {fid} file_sha256")
            if not isinstance(fragment.get("file_bytes"), int) or isinstance(fragment.get("file_bytes"), bool):
                raise PreplanError(f"Missing or invalid fragment {fid} file_bytes")
        _read_verified_fragment(frag_path, fragment)
    return metadata, source_index


def validate_digest(package: Path, digest_id: str, *, _verified_index: dict[str, Any] | None = None) -> dict[str, Any]:
    if not isinstance(digest_id, str) or not re.fullmatch(r"D\d{3,}", digest_id):
        raise PreplanError(f"Invalid digest id: {digest_id!r}")
    if _verified_index is None:
        _, source_index = verify_fragments(package)
    else:
        source_index = _verified_index
    fragments = source_index["fragments"]
    by_id = {item["id"]: item for item in fragments}
    known = set(by_id)
    path = safe_package_path(package, f"digests/{digest_id}.json")
    data = read_json(path)
    if not isinstance(data, dict):
        raise PreplanError(f"{path}: digest must be a JSON object")
    if data.get("digest_id") != digest_id:
        raise PreplanError(f"{path}: digest_id mismatch")
    ids = data.get("fragment_ids")
    if not isinstance(ids, list) or not ids or any(not isinstance(x, str) or not x.strip() for x in ids):
        raise PreplanError(f"{path}: fragment_ids must be a non-empty list of fragment ids")
    if len(ids) != len(set(ids)):
        raise PreplanError(f"{path}: duplicate fragment_ids are not allowed")
    if not set(ids) <= known:
        raise PreplanError(f"{path}: fragment_ids must be a subset of SOURCE_INDEX")
    frag_hashes = data.get("fragment_hashes")
    if frag_hashes is None and _schema_version(source_index) >= 2:
        raise PreplanError(f"{path}: fragment_hashes is required for schema-v2 packages")
    if frag_hashes is not None:
        if not isinstance(frag_hashes, dict) or set(frag_hashes) != set(ids):
            raise PreplanError(f"{path}: fragment_hashes must map every assigned fragment_id")
        for fid, recorded in frag_hashes.items():
            expected_hashes = {by_id[fid].get("file_sha256"), by_id[fid].get("source_text_sha256")} - {None}
            if not isinstance(recorded, str) or recorded not in expected_hashes:
                raise PreplanError(f"{path}: stale fragment hash recorded for {fid}")
    allowed = set(ids)
    for field in ("obligations", "constraints", "interfaces", "dependencies", "validation_implications", "pattern_candidates", "material_questions", "contradictions"):
        items = data.get(field, [])
        if not isinstance(items, list):
            raise PreplanError(f"{path}: {field} must be a list")
        for pos, item in enumerate(items):
            if not isinstance(item, dict) or not str(item.get("text", "")).strip():
                raise PreplanError(f"{path}: {field}[{pos}] needs non-empty text")
            refs = item.get("source_refs")
            if not isinstance(refs, list) or not refs or any(not isinstance(r, str) or not r.strip() for r in refs):
                raise PreplanError(f"{path}: {field}[{pos}] has invalid source_refs")
            if len(refs) != len(set(refs)):
                raise PreplanError(f"{path}: {field}[{pos}] has duplicate source_refs")
            if not set(refs) <= allowed:
                raise PreplanError(f"{path}: {field}[{pos}] references unassigned fragment")
    # Contradiction ids: SOURCE_INDEX ids, or new ids prefixed with this digest id and unique within it,
    # so parallel workers cannot collide and the defective digest fails its own TODO.
    source_ctr_ids = {
        item.get("id") for item in source_index.get("detected_contradictions") or [] if isinstance(item, dict)
    }
    own_ctr_ids: set[str] = set()
    for pos, item in enumerate(data.get("contradictions", [])):
        ids = _contradiction_ids(item)
        if not ids:
            raise PreplanError(f"{path}: contradictions[{pos}] needs an id so later stages can carry it by identity")
        for ctr_id in sorted(ids - source_ctr_ids):
            if not ctr_id.startswith(f"{digest_id}-"):
                raise PreplanError(f"{path}: contradictions[{pos}] new id {ctr_id} must start with {digest_id}-")
            if ctr_id in own_ctr_ids:
                raise PreplanError(f"{path}: duplicate contradiction id {ctr_id}")
            own_ctr_ids.add(ctr_id)
    # Fail fast: every obligation held only by this batch's fragments must be covered by this digest,
    # so resume never counts an incomplete digest as done.
    own = [
        obl
        for obl in source_index.get("obligations") or []
        if isinstance(obl, dict) and obl.get("fragment_ids") and set(obl["fragment_ids"]) <= allowed
    ]
    if own:
        audit = audit_obligation_coverage(
            {"obligations": own, "duplicate_explicit_ids": source_index.get("duplicate_explicit_ids") or []}, [data]
        )
        if audit["missing_ids"]:
            raise PreplanError(
                f"{path}: Missing source obligations in digest {digest_id}: {audit['missing_ids'][:10]} "
                f"(table_missing={audit['missing_table_ids'][:10]}; reasons: {_reason_text(audit)})"
            )
    return data


def _reason_text(audit: dict[str, Any]) -> str:
    return "; ".join(f"{key}: {why}" for key, why in list(audit.get("missing_reasons", {}).items())[:5])


def all_digests(package: Path, *, _verified_index: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    if _verified_index is None:
        _, source_index = verify_fragments(package)
    else:
        source_index = _verified_index
    digests_dir = package / "digests"
    if _is_link(digests_dir) or not digests_dir.is_dir():
        raise PreplanError("digests/ directory is missing or is a symlink")
    paths = sorted(digests_dir.glob("D*.json"))
    if not paths:
        raise PreplanError("No digest files exist")
    digests: list[dict[str, Any]] = []
    seen_fragments: set[str] = set()
    duplicates: set[str] = set()
    for path in paths:
        if _is_link(path):
            raise PreplanError(f"Symlink digest file is not allowed: {path.name}")
        digest = validate_digest(package, path.stem, _verified_index=source_index)
        for fid in digest["fragment_ids"]:
            if fid in seen_fragments:
                duplicates.add(fid)
            seen_fragments.add(fid)
        digests.append(digest)
    if duplicates:
        raise PreplanError(f"Duplicate fragment coverage across digests: {sorted(duplicates)}")
    # Worker-assigned contradiction ids must be unique across all digests, or one carrier could satisfy
    # several distinct contradictions; SOURCE_INDEX ids may legitimately recur across batches.
    source_ids = {item.get("id") for item in source_index.get("detected_contradictions") or [] if isinstance(item, dict)}
    seen_ctr: dict[str, str] = {}
    for digest in digests:
        for item in digest.get("contradictions", []):
            for ctr_id in _contradiction_ids(item) - source_ids:
                if ctr_id in seen_ctr:
                    raise PreplanError(
                        f"Duplicate digest contradiction id {ctr_id} in {seen_ctr[ctr_id]} and {digest['digest_id']}; "
                        "prefix new ids with the digest id"
                    )
                seen_ctr[ctr_id] = digest["digest_id"]
    return digests


def _contradiction_ids(item: Any) -> set[str]:
    if not isinstance(item, dict):
        return set()
    ids = {item["id"].strip()} if isinstance(item.get("id"), str) and item["id"].strip() else set()
    extra = item.get("contradiction_ids")
    if isinstance(extra, list):
        ids |= {value.strip() for value in extra if isinstance(value, str) and value.strip()}
    return ids


def _missing_contradictions(
    carriers: list[Any],
    source_contradictions: list[Any],
    digest_contradictions: list[Any],
) -> list[str]:
    """Contradictions not carried forward by identity (source and digest contradictions both carry ids)."""
    carried_ids: set[str] = set()
    for item in carriers:
        carried_ids |= _contradiction_ids(item)
    missing: list[str] = []
    for item in source_contradictions:
        ctr_id = item.get("id") if isinstance(item, dict) else None
        if isinstance(ctr_id, str) and ctr_id and ctr_id not in carried_ids:
            missing.append(ctr_id)
    for pos, item in enumerate(digest_contradictions):
        ids = _contradiction_ids(item)
        if not ids & carried_ids:
            missing.append(sorted(ids)[0] if ids else f"digest_contradiction[{pos}]")
    return list(dict.fromkeys(missing))


def validate_synthesis(package: Path, *, _verified_index: dict[str, Any] | None = None) -> None:
    if _verified_index is None:
        _, source_index = verify_fragments(package)
    else:
        source_index = _verified_index
    digests = all_digests(package, _verified_index=source_index)
    known = {ref for digest in digests for ref in digest["fragment_ids"]}
    seeds = read_json(safe_package_path(package, "PATTERN_SEEDS.json"))
    patterns = seeds.get("patterns") if isinstance(seeds, dict) else None
    if not isinstance(patterns, list):
        raise PreplanError("PATTERN_SEEDS.json requires patterns[]")
    seen_pattern_ids: set[str] = set()
    for pos, pattern in enumerate(patterns):
        if not isinstance(pattern, dict) or not str(pattern.get("id", "")).strip() or not str(pattern.get("title", "")).strip():
            raise PreplanError(f"patterns[{pos}] requires id/title")
        pid = str(pattern["id"]).strip()
        if pid in seen_pattern_ids:
            raise PreplanError(f"Duplicate pattern seed id: {pid}")
        seen_pattern_ids.add(pid)
        if not isinstance(pattern.get("contract"), list) or not pattern["contract"]:
            raise PreplanError(f"patterns[{pos}] requires contract[]")
        refs = pattern.get("source_refs")
        if not isinstance(refs, list) or not refs or len(refs) != len(set(refs)) or not set(refs) <= known:
            raise PreplanError(f"patterns[{pos}] has invalid source_refs")
    work = read_json(safe_package_path(package, "WORKSTREAM_INDEX.json"))
    if not isinstance(work, dict) or not isinstance(work.get("workstreams"), list):
        raise PreplanError("WORKSTREAM_INDEX.json requires workstreams[]")
    contradictions = work.get("contradictions", [])
    if not isinstance(contradictions, list) or any(not isinstance(item, dict) for item in contradictions):
        raise PreplanError("WORKSTREAM_INDEX.json contradictions must be a list of objects")
    digest_contradictions = [item for digest in digests for item in digest.get("contradictions", [])]
    source_contradictions = source_index.get("detected_contradictions") or []
    missing = _missing_contradictions(contradictions, source_contradictions, digest_contradictions)
    if missing:
        raise PreplanError(
            "WORKSTREAM_INDEX.json must preserve source/digest contradictions without silently dropping them; "
            f"missing={missing[:10]}"
        )


def validate_coverage(package: Path, *, _verified_index: dict[str, Any] | None = None) -> dict[str, Any]:
    if _verified_index is None:
        _, source_index = verify_fragments(package)
    else:
        source_index = _verified_index
    expected = {item["id"] for item in source_index["fragments"]}
    digests = all_digests(package, _verified_index=source_index)
    actual = {fragment for digest in digests for fragment in digest["fragment_ids"]}
    if expected != actual:
        raise PreplanError(f"Digest coverage mismatch; missing={sorted(expected-actual)}, extra={sorted(actual-expected)}")
    validate_synthesis(package, _verified_index=source_index)
    obl_audit = audit_obligation_coverage(source_index, digests)
    if obl_audit["missing_ids"]:
        raise PreplanError(
            f"Missing source obligations in digests: {obl_audit['missing_ids'][:10]} "
            f"(table_missing={obl_audit['missing_table_ids'][:10]}; reasons: {_reason_text(obl_audit)})"
        )
    review = read_json(safe_package_path(package, "COVERAGE_REVIEW.json"))
    covered = review.get("covered_fragment_ids") if isinstance(review, dict) else None
    if not isinstance(covered, list) or len(covered) != len(set(covered)) or set(covered) != expected:
        raise PreplanError("COVERAGE_REVIEW covered_fragment_ids must exactly match SOURCE_INDEX without duplicates")
    if review.get("status") not in {"approved", "blocked"}:
        raise PreplanError("COVERAGE_REVIEW status must be approved or blocked")
    approved = review.get("status") == "approved"
    obligations = source_index.get("obligations") or []
    covered_obls = review.get("covered_obligation_ids")
    if covered_obls is None and approved and obligations:
        raise PreplanError("Approved COVERAGE_REVIEW requires covered_obligation_ids for every source obligation")
    if covered_obls is not None:
        if not isinstance(covered_obls, list) or any(not isinstance(x, str) or not x.strip() for x in covered_obls):
            raise PreplanError("COVERAGE_REVIEW covered_obligation_ids must be a list of non-empty ids")
        if len(covered_obls) != len(set(covered_obls)):
            raise PreplanError("COVERAGE_REVIEW covered_obligation_ids contains duplicates")
        covered_obl_set = set(covered_obls)
        ambiguous = _ambiguous_explicit_ids(source_index)
        for obl in obligations:
            explicit = obl.get("explicit_id")
            usable = isinstance(explicit, str) and explicit and explicit.upper() not in ambiguous
            accepted = {obl["canonical_id"]} | ({explicit} if usable else set())
            if not (accepted & covered_obl_set):
                raise PreplanError(
                    f"COVERAGE_REVIEW covered_obligation_ids omits source obligation {obl.get('explicit_id') or obl['canonical_id']}"
                )
    unresolved = review.get("unresolved_material_findings")
    if not isinstance(unresolved, list):
        raise PreplanError("COVERAGE_REVIEW requires unresolved_material_findings[]")
    if approved and unresolved:
        raise PreplanError("Approved coverage review cannot have unresolved material findings")
    digest_contradictions = [item for digest in digests for item in digest.get("contradictions", [])]
    source_contradictions = source_index.get("detected_contradictions") or []
    if (digest_contradictions or source_contradictions) and approved:
        recorded = review.get("recorded_contradictions")
        if not isinstance(recorded, list) or not recorded:
            raise PreplanError(
                "Contradictions exist in source or digests; COVERAGE_REVIEW must block or explicitly list recorded_contradictions"
            )
        for pos, item in enumerate(recorded):
            if not isinstance(item, dict) or not str(item.get("text") or item.get("detail") or "").strip():
                raise PreplanError(f"COVERAGE_REVIEW recorded_contradictions[{pos}] needs non-empty text/detail")
            refs = item.get("source_refs")
            if not isinstance(refs, list) or not refs or len(refs) != len(set(refs)) or not set(refs) <= expected:
                raise PreplanError(f"COVERAGE_REVIEW recorded_contradictions[{pos}] has invalid source_refs")
        missing = _missing_contradictions(recorded, source_contradictions, digest_contradictions)
        if missing:
            raise PreplanError(f"COVERAGE_REVIEW recorded_contradictions omits contradictions {missing[:10]}")
    unsupported = [item for item in source_index.get("unsupported_structures") or [] if isinstance(item, dict)]
    if unsupported and approved:
        # Recorded-but-unextracted content (tracked changes, text boxes, math, non-body parts) must be
        # acknowledged explicitly; otherwise the review has to block.
        acknowledged = review.get("acknowledged_unsupported_structures")
        if not isinstance(acknowledged, list):
            raise PreplanError(
                "SOURCE_INDEX records unsupported_structures; an approved COVERAGE_REVIEW must list each in "
                "acknowledged_unsupported_structures (kind, location) or block"
            )
        acknowledged_count: dict[tuple[str, str], int] = {}
        for pos, item in enumerate(acknowledged):
            if not isinstance(item, dict) or not isinstance(item.get("kind"), str) or not isinstance(item.get("location"), str):
                raise PreplanError(f"COVERAGE_REVIEW acknowledged_unsupported_structures[{pos}] needs string kind and location")
            key = (item["kind"], item["location"])
            acknowledged_count[key] = acknowledged_count.get(key, 0) + 1
        # One acknowledgement per recorded entry: two insertions in one paragraph need two entries.
        missing_unsupported: list[str] = []
        for item in unsupported:
            key = (str(item.get("kind")), str(item.get("location")))
            if acknowledged_count.get(key, 0) > 0:
                acknowledged_count[key] -= 1
            else:
                missing_unsupported.append(f"{key[0]}@{key[1]}")
        if missing_unsupported:
            raise PreplanError(f"COVERAGE_REVIEW acknowledged_unsupported_structures omits {missing_unsupported[:10]}")
    obligations_floor = review.get("acknowledged_obligation_floor")
    if approved and not obligations and source_index.get("fragments") and not (
        isinstance(obligations_floor, str) and len(obligations_floor.strip()) >= 20
    ):
        # The deterministic extractor recognises English modals and REQ/FR/NFR/OBL/CLAUSE/RULE/R### ids only;
        # zero obligations makes the digest audit vacuous, so the reviewer must say why that is acceptable.
        raise PreplanError(
            "SOURCE_INDEX has no extracted obligations; an approved COVERAGE_REVIEW must explain in "
            "acknowledged_obligation_floor how requirements were verified, or block"
        )
    return obl_audit


def _package_integrity_pins(package: Path, source_index: dict[str, Any]) -> dict[str, Any]:
    digest_paths = sorted((package / "digests").glob("D*.json"))
    digests_sha = {
        path.stem: sha256_file(safe_package_path(package, f"digests/{path.name}"))
        for path in digest_paths
    }
    return {
        "source_index_sha256": sha256_file(safe_package_path(package, "SOURCE_INDEX.json")),
        "fragments_manifest_sha256": fragments_manifest_hash(source_index["fragments"]),
        "digests_sha256": digests_sha,
        "pattern_seeds_sha256": sha256_file(safe_package_path(package, "PATTERN_SEEDS.json")),
        "workstream_index_sha256": sha256_file(safe_package_path(package, "WORKSTREAM_INDEX.json")),
        "coverage_review_sha256": sha256_file(safe_package_path(package, "COVERAGE_REVIEW.json")),
        "handoff_sha256": sha256_file(safe_package_path(package, "FINAL_PLAN_INPUT.md")),
    }


def verify_source_derivation(
    metadata: dict[str, Any],
    source_index: dict[str, Any],
    source: str | Path | None = None,
    *,
    require: bool = False,
) -> dict[str, Any]:
    """Re-hash the raw source and re-derive the source index; reject a stale or re-pinned package.

    Uses ``source`` when given (it must exist), else ``package.json`` ``source.original_path`` (which is
    not pinned). When the raw source is unavailable the result says so (only the in-package hash chain
    was checked), or, with ``require``, the gate fails.
    """
    recorded = metadata.get("source") if isinstance(metadata.get("source"), dict) else {}
    if source is not None:
        candidate: Path | None = Path(source).expanduser()
    else:
        original = recorded.get("original_path")
        candidate = Path(original) if isinstance(original, str) and original else None
        if candidate is None or not (candidate.exists() or candidate.is_symlink()):
            if require:
                raise PreplanError("Raw source is unavailable for re-derivation; pass --source <raw source>")
            return {
                "status": "unavailable",
                "path": str(candidate) if candidate else None,
                "detail": "Raw source not found; only the in-package hash chain was verified, which detects naive mutation but not a re-pinned SOURCE_INDEX.",
            }
    path = safe_source(candidate)
    actual_sha = sha256_file(path)
    if actual_sha != recorded.get("sha256"):
        raise PreplanError(f"Raw source changed since preparation (SHA-256 mismatch for {path.name}); prepared package is stale")
    version = source_index.get("extraction_version")
    if version != EXTRACTION_VERSION:
        raise PreplanError(f"Prepared package extraction_version {version!r} differs from current {EXTRACTION_VERSION!r}; re-run prepare")
    params = source_index.get("fragmentation")
    target = params.get("target_tokens") if isinstance(params, dict) else None
    maximum = params.get("max_tokens") if isinstance(params, dict) else None
    if not isinstance(target, int) or not isinstance(maximum, int) or target <= 0 or maximum <= 0:
        raise PreplanError("SOURCE_INDEX lacks valid fragmentation parameters; re-run prepare")
    extracted = extract_document(path)
    if extracted["block_stream_sha256"] != source_index.get("block_stream_sha256"):
        raise PreplanError("Re-extracted block stream differs from SOURCE_INDEX block_stream_sha256; prepared package is stale")
    if len(extracted["blocks"]) != source_index.get("block_count"):
        raise PreplanError("SOURCE_INDEX block_count differs from raw-source re-extraction")
    if extracted["unsupported_structures"] != source_index.get("unsupported_structures"):
        raise PreplanError("SOURCE_INDEX unsupported_structures differ from raw-source re-extraction")
    fragments, obligations, duplicates, contradictions = derive_fragment_evidence(extracted["blocks"], target, maximum)
    by_fragment: dict[str, list[str]] = {}
    for obl in obligations:
        for fid in obl.get("fragment_ids", []):
            by_fragment.setdefault(fid, []).append(obl["canonical_id"])
    derived_fragments = [
        {
            "id": item["id"],
            "source_text_sha256": item["sha256"],
            "source_block_start": item["source_block_start"],
            "source_block_end": item["source_block_end"],
            "source_anchors": item.get("source_anchors") or [],
            "heading_path": item["heading_path"],
            "obligation_ids": by_fragment.get(item["id"], []),
        }
        for item in fragments
    ]
    recorded_fragments = [{key: item.get(key) for key in derived_fragments[0]} for item in source_index["fragments"]] if derived_fragments else []
    if derived_fragments != recorded_fragments:
        raise PreplanError("SOURCE_INDEX fragments differ from a deterministic re-split of the raw source")
    recorded_obligations = source_index.get("obligations") or []
    if obligations != recorded_obligations:
        derived_ids = {obl["canonical_id"] for obl in obligations}
        recorded_ids = {obl.get("canonical_id") for obl in recorded_obligations if isinstance(obl, dict)}
        raise PreplanError(
            "SOURCE_INDEX obligations differ from raw-source re-derivation "
            f"(missing={sorted(derived_ids - recorded_ids)[:10]}, extra={sorted(map(str, recorded_ids - derived_ids))[:10]})"
        )
    if duplicates != (source_index.get("duplicate_explicit_ids") or []):
        raise PreplanError("SOURCE_INDEX duplicate_explicit_ids differ from raw-source re-derivation")
    if contradictions != (source_index.get("detected_contradictions") or []):
        raise PreplanError("SOURCE_INDEX detected_contradictions differ from raw-source re-derivation")
    return {
        "status": "verified",
        "path": str(path),
        "source_sha256": actual_sha,
        "block_stream_sha256": extracted["block_stream_sha256"],
        "fragment_count": len(fragments),
        "obligation_count": len(obligations),
        "contradiction_count": len(contradictions),
    }


def validate_package(package: Path, source: str | Path | None = None, *, require_source: bool = False) -> dict[str, Any]:
    metadata, source_index = verify_fragments(package, require_v2=True)
    validate_coverage(package, _verified_index=source_index)
    review = read_json(safe_package_path(package, "COVERAGE_REVIEW.json"))
    if review.get("status") != "approved":
        raise PreplanError("Prepared package is blocked by coverage review")
    handoff = safe_package_path(package, "FINAL_PLAN_INPUT.md")
    if len(handoff.read_text(encoding="utf-8").strip()) < 100:
        raise PreplanError("FINAL_PLAN_INPUT.md is missing or too shallow")
    source_check = verify_source_derivation(metadata, source_index, source, require=require_source)
    pins = _package_integrity_pins(package, source_index)
    metadata["state"] = "ready_for_final_planning"
    metadata["validated_at"] = now_utc()
    metadata["integrity"] = pins
    write_json(package / "package.json", metadata)
    return {"package_id": metadata.get("package_id"), "state": metadata["state"], "integrity": pins,
            "source_verification": source_check}


def validate_consumption(
    package: Path,
    fragment_ids: list[str] | None = None,
    source: str | Path | None = None,
    *,
    require_source: bool = False,
) -> dict[str, Any]:
    """Read-only consumption gate: recomputes every fragment and artifact hash and re-derives the raw source."""
    metadata, source_index = verify_fragments(package, require_v2=True)
    if metadata.get("state") != "ready_for_final_planning":
        raise PreplanError(f"Prepared package is not ready for final planning: state={metadata.get('state')!r}")
    validate_coverage(package, _verified_index=source_index)
    review = read_json(safe_package_path(package, "COVERAGE_REVIEW.json"))
    if review.get("status") != "approved":
        raise PreplanError("Prepared package is blocked by coverage review")
    handoff = safe_package_path(package, "FINAL_PLAN_INPUT.md")
    if len(handoff.read_text(encoding="utf-8").strip()) < 100:
        raise PreplanError("FINAL_PLAN_INPUT.md is missing or too shallow")
    actual_pins = _package_integrity_pins(package, source_index)
    expected_pins = metadata.get("integrity")
    if not isinstance(expected_pins, dict) or not expected_pins:
        raise PreplanError("Prepared package has no integrity pins; run validate-package before consumption")
    if set(expected_pins) != set(actual_pins):
        raise PreplanError("Prepared package integrity pin set differs from the current artifact set")
    for key, expected_val in expected_pins.items():
        if actual_pins.get(key) != expected_val:
            raise PreplanError(f"Prepared package artifact changed after validation: {key}")
    source_check = verify_source_derivation(metadata, source_index, source, require=require_source)
    by_id = {item["id"]: item for item in source_index["fragments"]}
    requested: list[dict[str, Any]] = []
    if fragment_ids is not None:
        if len(fragment_ids) != len(set(fragment_ids)):
            raise PreplanError("Duplicate fragment ids requested at consumption")
        for fid in fragment_ids:
            if fid not in by_id:
                raise PreplanError(f"Unknown fragment id requested at consumption: {fid}")
            requested.append(
                {
                    "id": fid,
                    "path": by_id[fid]["path"],
                    "file_sha256": by_id[fid].get("file_sha256"),
                    "source_text_sha256": by_id[fid]["source_text_sha256"],
                }
            )
    return {
        "package_id": metadata.get("package_id"),
        "state": metadata["state"],
        "verified_fragment_count": len(source_index["fragments"]),
        "source_sha256": metadata.get("source", {}).get("sha256"),
        "block_stream_sha256": source_index.get("block_stream_sha256"),
        "integrity": actual_pins,
        "source_verification": source_check,
        "requested_fragments": requested,
    }


def read_fragment(package: Path, fragment_id: str) -> dict[str, Any]:
    """Return one fragment's text from a single read verified against its recorded hashes."""
    _, source_index = verify_fragments(package, require_v2=True)
    by_id = {item["id"]: item for item in source_index["fragments"]}
    if fragment_id not in by_id:
        raise PreplanError(f"Unknown fragment id: {fragment_id}")
    entry = by_id[fragment_id]
    text = _read_verified_fragment(safe_package_path(package, entry["path"]), entry)
    return {
        "id": fragment_id,
        "path": entry["path"],
        "file_sha256": entry["file_sha256"],
        "source_text_sha256": entry["source_text_sha256"],
        "source_anchors": entry.get("source_anchors", []),
        "text": text,
    }


def resume_status(package: Path) -> dict[str, Any]:
    """Inspect validated digests so interrupted batches resume without reprocessing completed raw fragments."""
    _, source_index = verify_fragments(package)
    fragments = source_index["fragments"]
    batches = batch_fragments(fragments)
    completed_digests: list[str] = []
    pending_digests: list[dict[str, Any]] = []
    invalid_digests: list[dict[str, Any]] = []
    completed_fragment_ids: list[str] = []
    pending_fragment_ids: list[str] = []
    for batch_no, batch in enumerate(batches, 1):
        digest_id = f"D{batch_no:03d}"
        expected_ids = [item["id"] for item in batch]
        digest_file = package / "digests" / f"{digest_id}.json"
        if digest_file.exists() or digest_file.is_symlink():
            try:
                data = validate_digest(package, digest_id, _verified_index=source_index)
                if data.get("fragment_ids") == expected_ids:
                    completed_digests.append(digest_id)
                    completed_fragment_ids.extend(expected_ids)
                    continue
                invalid_digests.append({"digest_id": digest_id, "reason": "fragment_ids mismatch with batch"})
            except PreplanError as exc:
                invalid_digests.append({"digest_id": digest_id, "reason": str(exc)})
        pending_digests.append({"digest_id": digest_id, "fragment_ids": expected_ids})
        pending_fragment_ids.extend(expected_ids)
    return {
        "total_batches": len(batches),
        "completed_digests": completed_digests,
        "pending_digests": pending_digests,
        "invalid_digests": invalid_digests,
        "completed_fragment_ids": completed_fragment_ids,
        "pending_fragment_ids": pending_fragment_ids,
        "raw_fragments_to_process": pending_fragment_ids,
        "can_resume_without_reprocessing": bool(completed_digests) and not invalid_digests,
    }


def compare_extraction_baselines(
    source: Path,
    package: Path | None = None,
    *,
    target_tokens: int = TARGET_FRAGMENT_TOKENS,
    max_tokens: int = MAX_FRAGMENT_TOKENS,
) -> dict[str, Any]:
    """Measure obligation recall and contradiction coverage offline against a deterministic one-shot comparator."""
    source = safe_source(source)
    extracted = extract_document(source)
    blocks = extracted["blocks"]
    one_shot_obligations, one_shot_dups = extract_obligations(blocks)
    one_shot_contradictions = detect_contradictions(one_shot_obligations)
    one_shot_ids = {obl["canonical_id"] for obl in one_shot_obligations}
    one_shot_table_ids = {obl["canonical_id"] for obl in one_shot_obligations if obl["from_table"]}
    one_shot_ctr_ids = {ctr["id"] for ctr in one_shot_contradictions}
    logical = "\n\n".join(item["text"] for item in blocks)
    raw_tokens = estimate_tokens(logical)
    ws_tokens = working_set_tokens(blocks)

    if package is not None:
        _, source_index = verify_fragments(package)
        digests = all_digests(package, _verified_index=source_index)
        audit = audit_obligation_coverage(source_index, digests)
        staged_covered_ids = set(audit.get("covered_ids", []))
        staged_missing = sorted(one_shot_ids - staged_covered_ids)
        staged_missing_table = sorted(one_shot_table_ids - staged_covered_ids)
        work_path = package / "WORKSTREAM_INDEX.json"
        work_data = read_json(safe_package_path(package, "WORKSTREAM_INDEX.json")) if work_path.exists() else {}
        work_ctrs = work_data.get("contradictions", []) if isinstance(work_data, dict) else []
        digest_ctrs = [c for d in digests for c in d.get("contradictions", [])]
        staged_ctr_ids: set[str] = set()
        for item in list(work_ctrs if isinstance(work_ctrs, list) else []) + digest_ctrs:
            staged_ctr_ids |= _contradiction_ids(item)
        # Identity-based: a contradiction counts only when its deterministic id is carried forward.
        staged_ctr_count = len(one_shot_ctr_ids & staged_ctr_ids)
        ctr_coverage = round(staged_ctr_count / len(one_shot_ctr_ids), 6) if one_shot_ctr_ids else 1.0
        batches = batch_fragments(source_index["fragments"])
        frag_count = len(source_index["fragments"])
        max_batch_toks = max((sum(int(f["estimated_tokens"]) for f in b) for b in batches), default=0)
        staged_mode = "prepared_package_digests"
    else:
        fragments = make_fragments(blocks, target_tokens, max_tokens)
        batches = batch_fragments(fragments)
        # Re-extract per fragment independently (without seeing other fragments) to test fragmentation losslessness.
        staged_blocks: list[dict[str, Any]] = []
        block_to_frag: dict[int, str] = {}
        table_block_nos = {int(b["no"]) for b in blocks if b.get("kind") == "table_cell"}
        seq = 0
        for fragment in fragments:
            # Map each paragraph in the fragment back to its authoritative block kind for accurate table tracking.
            parts = [p.strip() for p in fragment["text"].split("\n\n") if p.strip()]
            anchors = fragment.get("source_anchors") or []
            for idx, part in enumerate(parts):
                seq += 1
                anchor = anchors[idx] if idx < len(anchors) else f"f:{fragment['id']}:{idx + 1}"
                is_tbl = ("tbl:" in anchor) or (
                    idx == 0 and fragment["source_block_start"] == fragment["source_block_end"] and fragment["source_block_start"] in table_block_nos
                )
                staged_blocks.append(
                    {
                        "no": seq,
                        "anchor": anchor,
                        "kind": "table_cell" if is_tbl else "paragraph",
                        "text": part,
                        "heading_level": None if is_tbl else detect_heading("", part),
                        "table_depth": 1 if is_tbl else 0,
                    }
                )
                block_to_frag[seq] = fragment["id"]
        staged_obligations, _ = extract_obligations(staged_blocks, block_to_frag)
        staged_contradictions = detect_contradictions(staged_obligations)
        staged_covered_ids = {obl["canonical_id"] for obl in staged_obligations}
        staged_missing = sorted(one_shot_ids - staged_covered_ids)
        staged_missing_table = sorted(one_shot_table_ids - staged_covered_ids)
        staged_ctr_ids = {ctr["id"] for ctr in staged_contradictions}
        staged_ctr_count = len(staged_ctr_ids)
        ctr_coverage = round(len(one_shot_ctr_ids & staged_ctr_ids) / len(one_shot_ctr_ids), 6) if one_shot_ctr_ids else 1.0
        frag_count = len(fragments)
        max_batch_toks = max((sum(int(f["estimated_tokens"]) for f in b) for b in batches), default=0)
        staged_mode = "deterministic_offline_staged"

    obligation_recall = round(len(one_shot_ids & staged_covered_ids) / len(one_shot_ids), 6) if one_shot_ids else 1.0
    table_recall = round(len(one_shot_table_ids & staged_covered_ids) / len(one_shot_table_ids), 6) if one_shot_table_ids else 1.0
    signature = sha256_text("|".join(sorted(one_shot_ids & staged_covered_ids)))

    return {
        "comparator_mode": "deterministic_offline",
        "staged_mode": staged_mode,
        "model_comparison_performed": False,
        "source_sha256": sha256_file(source),
        "block_stream_sha256": extracted["block_stream_sha256"],
        "one_shot": {
            "obligation_count": len(one_shot_ids),
            "table_obligation_count": len(one_shot_table_ids),
            "contradiction_count": len(one_shot_ctr_ids),
            "estimated_tokens": ws_tokens,
            "raw_estimated_tokens": raw_tokens,
            "unique_canonical_ids": sorted(one_shot_ids),
        },
        "staged": {
            "fragment_count": frag_count,
            "batch_count": len(batches),
            "max_batch_tokens": max_batch_toks,
            "obligation_count": len(staged_covered_ids),
            "table_obligation_count": len(one_shot_table_ids & staged_covered_ids),
            "contradiction_count": staged_ctr_count,
            "missing_obligation_ids": staged_missing,
            "missing_table_obligation_ids": staged_missing_table,
        },
        "metrics": {
            "obligation_recall": obligation_recall,
            "table_obligation_recall": table_recall,
            "contradiction_coverage": ctr_coverage,
            "duplicate_explicit_ids_count": len(one_shot_dups),
            "unsupported_structures_count": len(extracted["unsupported_structures"]),
            "order_invariant_signature": signature,
        },
        "limitations": [
            "Offline deterministic extraction comparator only; live model-based comparison requires owner confirmation (G002) and was not executed.",
            "Recall compares the deterministic regex extractor with itself across fragment boundaries (fragmentation losslessness);"
            " with a package it measures digest coverage of those extracted obligations, not model digest quality.",
        ],
    }


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


def create_primary_plan(repo: Path, package: Path, metadata: dict[str, Any], work_root: str) -> Path:
    spec = make_primary_spec(repo, package, metadata)
    write_json(package / "PRIMARY_PLAN_SPEC.json", spec)
    plan_id = f"primary-{metadata['package_id']}"
    concise = Path(__file__).with_name("planctl_concise.py")
    try:
        created = subprocess.run(
            [
                sys.executable,
                str(concise),
                "create",
                "--repo-root",
                str(repo),
                "--spec",
                str(package / "PRIMARY_PLAN_SPEC.json"),
                "--work-root",
                work_root,
                "--plan-id",
                plan_id,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        raise PreplanError(exc.stderr.strip() or "Unable to create primary plan") from exc
    created_path = created.stdout.strip()
    if not created_path:
        raise PreplanError("Primary-plan creation did not return its plan path")
    plan_dir = Path(created_path)
    if not plan_dir.is_absolute():
        plan_dir = (repo / plan_dir).resolve()
    return plan_dir


def command_prepare(args: argparse.Namespace) -> None:
    repo = Path(args.repo_root).expanduser().resolve()
    source = safe_source(args.file)
    assessment = assess_source(source, args.soft_tokens, args.hard_tokens, args.breadth_token_floor, args.breadth_headings)
    if assessment["route"] != "primary_plan" and not args.force:
        print(json.dumps({"route": "final_plan", "assessment": assessment}, ensure_ascii=False, indent=2))
        raise SystemExit(3)
    package, metadata = create_package(repo, source, assessment, args.package_id, args.target_fragment_tokens, args.max_fragment_tokens)
    try:
        plan_dir = create_primary_plan(repo, package, metadata, args.work_root)
    except BaseException:
        # A package without its primary plan blocks every retry; remove only what this call created.
        shutil.rmtree(package, ignore_errors=True)
        raise
    metadata = read_json(package / "package.json")
    metadata.update({"state": "primary_plan_created", "primary_plan": str(plan_dir)})
    write_json(package / "package.json", metadata)
    print(json.dumps({"route": "primary_plan", "assessment": assessment, "package": str(package), "primary_plan": str(plan_dir)}, ensure_ascii=False, indent=2))


def command_validate_digest(args: argparse.Namespace) -> None:
    validate_digest(Path(args.package), args.digest)
    print(f"VALID {args.digest}")


def command_validate_synthesis(args: argparse.Namespace) -> None:
    validate_synthesis(Path(args.package))
    print("VALID SYNTHESIS")


def command_validate_coverage(args: argparse.Namespace) -> None:
    validate_coverage(Path(args.package))
    print("VALID COVERAGE")


def command_validate_package(args: argparse.Namespace) -> None:
    result = validate_package(Path(args.package), args.source, require_source=args.require_source)
    print(f"VALID PACKAGE source_verification={result['source_verification']['status']}")


def command_validate_consumption(args: argparse.Namespace) -> None:
    result = validate_consumption(Path(args.package), args.fragment or None, args.source, require_source=args.require_source)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def command_read_fragment(args: argparse.Namespace) -> None:
    result = read_fragment(Path(args.package), args.fragment)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def command_resume_status(args: argparse.Namespace) -> None:
    result = resume_status(Path(args.package))
    print(json.dumps(result, ensure_ascii=False, indent=2))


def command_compare_baselines(args: argparse.Namespace) -> None:
    package = Path(args.package) if args.package else None
    result = compare_extraction_baselines(
        safe_source(args.file),
        package,
        target_tokens=args.target_fragment_tokens,
        max_tokens=args.max_fragment_tokens,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


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
    package.add_argument("--source", help="raw source to re-hash and re-derive (default: package.json original_path)")
    package.add_argument("--require-source", action="store_true", help="fail when the raw source is unavailable")
    package.set_defaults(func=command_validate_package)
    consumption = sub.add_parser("validate-consumption")
    consumption.add_argument("--package", required=True)
    consumption.add_argument("--fragment", action="append", default=[])
    consumption.add_argument("--source", help="raw source to re-hash and re-derive (default: package.json original_path)")
    consumption.add_argument("--require-source", action="store_true", help="fail when the raw source is unavailable")
    consumption.set_defaults(func=command_validate_consumption)
    read_frag = sub.add_parser("read-fragment")
    read_frag.add_argument("--package", required=True)
    read_frag.add_argument("--fragment", required=True)
    read_frag.set_defaults(func=command_read_fragment)
    resume = sub.add_parser("resume-status")
    resume.add_argument("--package", required=True)
    resume.set_defaults(func=command_resume_status)
    compare = sub.add_parser("compare-baselines")
    compare.add_argument("--file", required=True)
    compare.add_argument("--package")
    add_split_options(compare)
    compare.set_defaults(func=command_compare_baselines)
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
