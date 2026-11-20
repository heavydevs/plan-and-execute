#!/usr/bin/env python3
"""Acceptance and counterexample self-tests for Tasks 008/009 (primary planning and its review fixes)."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path
from typing import Any
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "skill" / "plan-and-execute" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import preplanctl  # noqa: E402

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
MC_NS = "http://schemas.openxmlformats.org/markup-compatibility/2006"
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"


def init_repo(root: Path) -> Path:
    repo = root / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    return repo


def write_docx(path: Path, body_xml: str, extra_parts: dict[str, bytes] | None = None) -> Path:
    document_xml = (
        f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document xmlns:w="{W_NS}" xmlns:mc="{MC_NS}" xmlns:m="{M_NS}" xmlns:a="{A_NS}">'
        f"<w:body>{body_xml}</w:body>"
        f"</w:document>"
    ).encode("utf-8")
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("word/document.xml", document_xml)
        for name, data in (extra_parts or {}).items():
            archive.writestr(name, data)
    return path


def w_p(text: str, style: str | None = None) -> str:
    ppr = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ""
    return f"<w:p>{ppr}<w:r><w:t>{text}</w:t></w:r></w:p>"


def populate_valid_package_artifacts(
    package: Path,
    *,
    omit_obligation_ids: set[str] | None = None,
    include_contradictions: bool = True,
    review_status: str = "approved",
    review_omit_obligation_ids: set[str] | None = None,
    acknowledge_unsupported: bool = True,
) -> dict[str, Any]:
    """Deterministically materialize valid digests, synthesis, coverage review, and handoff.

    ``omit_obligation_ids`` drops obligations from digests; the coverage review omits the same ids unless
    ``review_omit_obligation_ids`` is given (an empty set keeps the review complete so the digest audit
    is exercised on its own).
    """
    omit = omit_obligation_ids or set()
    review_omit = omit if review_omit_obligation_ids is None else review_omit_obligation_ids
    source_index = preplanctl.read_json(package / "SOURCE_INDEX.json")
    fragments = source_index["fragments"]
    by_id = {item["id"]: item for item in fragments}
    obligations = source_index.get("obligations") or []
    source_contradictions = source_index.get("detected_contradictions") or []
    batches = preplanctl.batch_fragments(fragments)

    for batch_no, batch in enumerate(batches, 1):
        digest_id = f"D{batch_no:03d}"
        fids = [item["id"] for item in batch]
        fid_set = set(fids)
        batch_obls: list[dict[str, Any]] = []
        for obl in obligations:
            if obl["canonical_id"] in omit or (obl.get("explicit_id") and obl["explicit_id"] in omit):
                continue
            overlap = [fid for fid in obl.get("fragment_ids", []) if fid in fid_set]
            if overlap:
                batch_obls.append(
                    {
                        "canonical_id": obl["canonical_id"],
                        "obligation_id": obl.get("explicit_id") or obl["canonical_id"],
                        "text": obl["text_preview"],
                        "source_refs": [overlap[0]],
                    }
                )
        if not batch_obls:
            batch_obls.append(
                {
                    "text": f"Captured planning facts for {', '.join(fids)}.",
                    "source_refs": [fids[0]],
                }
            )
        batch_ctrs: list[dict[str, Any]] = []
        if include_contradictions:
            for ctr in source_contradictions:
                overlap = [fid for fid in ctr.get("source_refs", []) if fid in fid_set]
                if overlap:
                    batch_ctrs.append(
                        {
                            "id": ctr["id"],
                            "text": ctr["detail"],
                            "source_refs": overlap,
                        }
                    )
        digest = {
            "digest_id": digest_id,
            "fragment_ids": fids,
            "fragment_hashes": {fid: by_id[fid]["file_sha256"] for fid in fids},
            "obligations": batch_obls,
            "constraints": [],
            "interfaces": [],
            "dependencies": [],
            "validation_implications": [],
            "pattern_candidates": [],
            "material_questions": [],
            "contradictions": batch_ctrs,
        }
        preplanctl.write_json(package / "digests" / f"{digest_id}.json", digest)

    all_fids = [item["id"] for item in fragments]
    preplanctl.write_json(
        package / "PATTERN_SEEDS.json",
        {
            "patterns": [
                {
                    "id": "PAT-001",
                    "title": "Source traceability contract",
                    "contract": ["Every derived obligation cites immutable fragment IDs."],
                    "source_refs": [all_fids[0]],
                    "rationale": "Preserves provenance during final planning.",
                    "affected_domains": ["planning"],
                }
            ]
        },
    )
    work_ctrs = (
        [
            {
                "id": ctr["id"],
                "detail": ctr["detail"],
                "source_refs": ctr["source_refs"] or [all_fids[0]],
            }
            for ctr in source_contradictions
        ]
        if include_contradictions
        else []
    )
    preplanctl.write_json(
        package / "WORKSTREAM_INDEX.json",
        {
            "workstreams": [{"id": "WS-01", "title": "Core specification", "source_refs": all_fids}],
            "dependencies": [],
            "contradictions": work_ctrs,
        },
    )
    covered_obl_ids = [
        obl["canonical_id"]
        for obl in obligations
        if obl["canonical_id"] not in review_omit and (obl.get("explicit_id") not in review_omit)
    ]
    review: dict[str, Any] = {
        "status": review_status,
        "covered_fragment_ids": all_fids,
        "covered_obligation_ids": covered_obl_ids,
        "unresolved_material_findings": (
            [{"detail": "Unresolved contradictions require owner resolution", "source_refs": [all_fids[0]]}]
            if review_status == "blocked"
            else []
        ),
        "notes": ["Deterministic test coverage review."],
    }
    if acknowledge_unsupported and source_index.get("unsupported_structures"):
        review["acknowledged_unsupported_structures"] = [
            {"kind": item["kind"], "location": item["location"], "note": "Reviewed; not merged into body blocks."}
            for item in source_index["unsupported_structures"]
        ]
    if include_contradictions and source_contradictions and review_status == "approved":
        review["recorded_contradictions"] = [
            {
                "id": ctr["id"],
                "text": ctr["detail"],
                "source_refs": ctr["source_refs"] or [all_fids[0]],
            }
            for ctr in source_contradictions
        ]
    preplanctl.write_json(package / "COVERAGE_REVIEW.json", review)
    handoff = (
        "# Final Planning Input\n\n"
        f"- Package ID: `{package.name}`\n"
        f"- Fragments: {', '.join(all_fids)}\n"
        "- Retrieve fragments by ID via `preplanctl.py read-fragment` after `validate-consumption`.\n"
        "- Do not load all raw fragments simultaneously into planning context.\n"
    )
    (package / "FINAL_PLAN_INPUT.md").write_bytes(handoff.encode("utf-8"))
    return source_index


def expect_preplan_error(fn: Any, expected_substring: str | None = None) -> str:
    try:
        fn()
    except preplanctl.PreplanError as exc:
        msg = str(exc)
        if expected_substring and expected_substring.lower() not in msg.lower():
            raise AssertionError(f"Expected {expected_substring!r} in PreplanError({msg!r})") from exc
        return msg
    raise AssertionError(f"Expected PreplanError (substring={expected_substring!r}) but call succeeded")


def test_ac01_mutating_one_byte_after_approval_invalidates_package() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        repo = init_repo(root)
        source = root / "spec.md"
        source.write_text(
            "\n\n".join(
                f"## {i}. Section {i}\n\nREQ-{i:03d}: Component {i} must preserve audit trace {i}. " + ("Detail text. " * 120)
                for i in range(1, 12)
            ),
            encoding="utf-8",
        )
        assessment = preplanctl.assess_source(source)
        package, _ = preplanctl.create_package(repo, source, assessment, target_tokens=1200, max_tokens=1600)
        source_index = populate_valid_package_artifacts(package)

        validated = preplanctl.validate_package(package)
        assert validated["state"] == "ready_for_final_planning"
        consumed = preplanctl.validate_consumption(package, fragment_ids=["F001"])
        assert consumed["verified_fragment_count"] == len(source_index["fragments"])

        # Mutate exactly 1 byte of fragment F001 after coverage approval.
        frag_path = package / source_index["fragments"][0]["path"]
        original = bytearray(frag_path.read_bytes())
        target_idx = original.index(b"preserve")
        original[target_idx] = ord("P")  # 1-byte mutation ('p' -> 'P')
        frag_path.write_bytes(bytes(original))

        expect_preplan_error(lambda: preplanctl.validate_consumption(package), "SHA-256 mismatch")
        expect_preplan_error(lambda: preplanctl.validate_package(package), "SHA-256 mismatch")
        expect_preplan_error(lambda: preplanctl.validate_coverage(package), "SHA-256 mismatch")
        expect_preplan_error(lambda: preplanctl.validate_digest(package, "D001"), "SHA-256 mismatch")
        expect_preplan_error(lambda: preplanctl.read_fragment(package, "F001"), "SHA-256 mismatch")


def test_ac02_docx_paragraphs_and_table_cells_preserve_obligations_in_source_order() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        repo = init_repo(root)
        body_xml = (
            w_p("1. Security Specification", style="Heading1")
            + w_p("REQ-001: System must log every authentication event.")
            + "<w:tbl>"
            + "<w:tr>"
            + f"<w:tc>{w_p('REQ-002: Audit records must be immutable.')}</w:tc>"
            + f"<w:tc>{w_p('REQ-003: Passwords must not be written to logs.')}</w:tc>"
            + "</w:tr>"
            + "</w:tbl>"
            + w_p("REQ-004: Failed deliveries must use exponential backoff.")
            + "<w:tbl>"
            + "<w:tr>"
            + f"<w:tc>{w_p('REQ-005: Exports shall preserve UTF-8 encoding.')}</w:tc>"
            + "</w:tr>"
            + "</w:tbl>"
        )
        docx = write_docx(root / "spec.docx", body_xml)
        extracted = preplanctl.extract_document(docx)
        blocks = extracted["blocks"]
        texts = [b["text"] for b in blocks]
        anchors = [b["anchor"] for b in blocks]
        assert len(anchors) == len(set(anchors)), anchors
        order_positions = [
            next(i for i, text in enumerate(texts) if req_id in text)
            for req_id in ("REQ-001", "REQ-002", "REQ-003", "REQ-004", "REQ-005")
        ]
        assert order_positions == sorted(order_positions) and len(set(order_positions)) == 5, order_positions
        assert blocks[order_positions[1]]["kind"] == "table_cell"
        assert blocks[order_positions[2]]["kind"] == "table_cell"
        assert blocks[order_positions[4]]["kind"] == "table_cell"

        assessment = preplanctl.assess_source(docx)
        package, _ = preplanctl.create_package(repo, docx, assessment)
        populate_valid_package_artifacts(package)
        preplanctl.validate_package(package)
        comparison = preplanctl.compare_extraction_baselines(docx, package)
        assert comparison["metrics"]["obligation_recall"] == 1.0, comparison
        assert comparison["metrics"]["table_obligation_recall"] == 1.0, comparison


def test_ac03_duplicates_missing_ids_contradictions_and_symlinks_rejected_or_recorded() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        repo = init_repo(root)
        source = root / "contradictions.md"
        source.write_text(
            "\n\n".join(
                [
                    "## 1. Caching Policy",
                    "REQ-010: API gateway must cache authenticated responses for 60 seconds.",
                    "REQ-010: API gateway must attach trace headers on every response.",
                    "## 2. Security Policy",
                    "REQ-020: API gateway must not cache authenticated responses for 60 seconds.",
                    "REQ-021: This security rule conflicts with REQ-010 caching behavior.",
                ]
            ),
            encoding="utf-8",
        )
        assessment = preplanctl.assess_source(source)
        package, _ = preplanctl.create_package(repo, source, assessment, target_tokens=100, max_tokens=200)
        source_index = preplanctl.read_json(package / "SOURCE_INDEX.json")

        # Duplicate explicit IDs and contradictory clauses are explicitly recorded.
        dup_ids = [d["explicit_id"] for d in source_index["duplicate_explicit_ids"]]
        assert "REQ-010" in dup_ids, source_index["duplicate_explicit_ids"]
        ctr_kinds = {c["kind"] for c in source_index["detected_contradictions"]}
        assert "polarity_conflict" in ctr_kinds, source_index["detected_contradictions"]
        assert "conflicting_explicit_id" in ctr_kinds, source_index["detected_contradictions"]
        assert "explicit_marker" in ctr_kinds, source_index["detected_contradictions"]

        # Silently dropping contradictions in WORKSTREAM_INDEX is rejected.
        populate_valid_package_artifacts(package, include_contradictions=False)
        expect_preplan_error(lambda: preplanctl.validate_synthesis(package), "contradictions")

        # Keeping contradictions in WORKSTREAM_INDEX but silently approving COVERAGE_REVIEW is rejected.
        populate_valid_package_artifacts(package, include_contradictions=True, review_status="approved")
        review_path = package / "COVERAGE_REVIEW.json"
        review = preplanctl.read_json(review_path)
        review.pop("recorded_contradictions", None)
        preplanctl.write_json(review_path, review)
        expect_preplan_error(lambda: preplanctl.validate_coverage(package), "recorded_contradictions")

        # Explicitly recording contradictions (or blocking) succeeds.
        populate_valid_package_artifacts(package, include_contradictions=True, review_status="approved")
        preplanctl.validate_package(package)
        preplanctl.validate_consumption(package)

        # Duplicate fragment coverage across digests is rejected.
        fids = [f["id"] for f in source_index["fragments"]]
        if len(fids) >= 2:
            d1 = preplanctl.read_json(package / "digests" / "D001.json")
            d2 = dict(d1, digest_id="D999", fragment_ids=[fids[0]], fragment_hashes={fids[0]: source_index["fragments"][0]["file_sha256"]})
            # A self-consistent digest of F001 (its own obligations covered) that overlaps D001's coverage.
            d2["obligations"] = [dict(item, source_refs=[fids[0]]) for item in d1["obligations"] if fids[0] in item["source_refs"]]
            d2["obligations"].append({"text": "Duplicate claim", "source_refs": [fids[0]]})
            d2["contradictions"] = []
            preplanctl.write_json(package / "digests" / "D999.json", d2)
            expect_preplan_error(lambda: preplanctl.all_digests(package), "Duplicate fragment coverage")
            (package / "digests" / "D999.json").unlink()

        # Duplicate source_refs in a digest item is rejected.
        d1_path = package / "digests" / "D001.json"
        d1_orig = preplanctl.read_json(d1_path)
        d1_bad = json.loads(json.dumps(d1_orig))
        d1_bad["obligations"][0]["source_refs"] = [d1_bad["fragment_ids"][0], d1_bad["fragment_ids"][0]]
        preplanctl.write_json(d1_path, d1_bad)
        expect_preplan_error(lambda: preplanctl.validate_digest(package, "D001"), "duplicate source_refs")
        preplanctl.write_json(d1_path, d1_orig)

        # Missing fragment ID and escaping fragment path in SOURCE_INDEX are rejected.
        bad_pkg_root = root / "bad_pkg"
        bad_pkg_root.mkdir()
        (bad_pkg_root / "fragments").mkdir()
        (bad_pkg_root / "digests").mkdir()
        preplanctl.write_json(bad_pkg_root / "package.json", {"schema_version": 2, "package_id": "bad"})
        preplanctl.write_json(
            bad_pkg_root / "SOURCE_INDEX.json",
            {"fragments": [{"id": "", "path": "fragments/F001.md", "source_text_sha256": "abc"}]},
        )
        expect_preplan_error(lambda: preplanctl.verify_fragments(bad_pkg_root), "missing a valid id")

        preplanctl.write_json(
            bad_pkg_root / "SOURCE_INDEX.json",
            {"fragments": [{"id": "F001", "path": "../contradictions.md", "source_text_sha256": "abc"}]},
        )
        expect_preplan_error(lambda: preplanctl.verify_fragments(bad_pkg_root), "Escaping package path")

        # Symlink rejection (real OS symlink where permitted; plus Windows junction + deterministic symlink guard).
        real_symlink_tested = False
        symlink_source = root / "link_source.md"
        try:
            os.symlink(source, symlink_source)
            real_symlink_tested = True
            expect_preplan_error(lambda: preplanctl.safe_source(symlink_source), "Symlink")
            symlink_source.unlink()
        except OSError:
            pass

        if sys.platform == "win32":
            junction_dir = root / "pkg_junction"
            res = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(junction_dir), str(package)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            if res.returncode == 0 and junction_dir.exists():
                try:
                    expect_preplan_error(lambda: preplanctl.verify_fragments(junction_dir), "real directory")
                finally:
                    subprocess.run(["cmd", "/c", "rmdir", str(junction_dir)], capture_output=True, check=False)

        if not real_symlink_tested:
            # Exercise the exact symlink rejection branches deterministically on restricted Windows hosts.
            orig_is_symlink = Path.is_symlink

            def fake_symlink(self: Path) -> bool:
                if self.name in {"contradictions.md", "D001.json"} or self.name.startswith("F001-"):
                    return True
                return orig_is_symlink(self)

            with mock.patch.object(Path, "is_symlink", fake_symlink):
                expect_preplan_error(lambda: preplanctl.safe_source(source), "Symlink")
                expect_preplan_error(lambda: preplanctl.verify_fragments(package), "Symlink")


def test_ac04_interrupted_batch_resumes_from_validated_digests_without_reprocessing() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        repo = init_repo(root)
        source = root / "multi.md"
        source.write_text(
            "\n\n".join(
                f"## {i}. Domain {i}\n\nREQ-{i:03d}: Domain {i} must enforce quota {i}. " + (f"Clause detail {i}. " * 140)
                for i in range(1, 20)
            ),
            encoding="utf-8",
        )
        assessment = preplanctl.assess_source(source)
        package, _ = preplanctl.create_package(repo, source, assessment, target_tokens=1500, max_tokens=2000)
        source_index = preplanctl.read_json(package / "SOURCE_INDEX.json")
        fragments = source_index["fragments"]
        by_id = {f["id"]: f for f in fragments}
        batches = preplanctl.batch_fragments(fragments)
        assert len(batches) >= 3, len(batches)

        # Complete ONLY batch 1 (D001), simulating interruption before D002..DN.
        first_fids = [f["id"] for f in batches[0]]
        first_obls = [
            {
                "canonical_id": obl["canonical_id"],
                "obligation_id": obl.get("explicit_id") or obl["canonical_id"],
                "text": obl["text_preview"],
                "source_refs": [fid],
            }
            for obl in source_index["obligations"]
            for fid in [next((x for x in obl["fragment_ids"] if x in first_fids), None)]
            if fid
        ]
        preplanctl.write_json(
            package / "digests" / "D001.json",
            {
                "digest_id": "D001",
                "fragment_ids": first_fids,
                "fragment_hashes": {fid: by_id[fid]["file_sha256"] for fid in first_fids},
                "obligations": first_obls,
                "constraints": [],
                "interfaces": [],
                "dependencies": [],
                "validation_implications": [],
                "pattern_candidates": [],
                "material_questions": [],
                "contradictions": [],
            },
        )
        status = preplanctl.resume_status(package)
        assert status["completed_digests"] == ["D001"], status
        assert status["completed_fragment_ids"] == first_fids, status
        assert status["can_resume_without_reprocessing"] is True, status
        assert not (set(status["raw_fragments_to_process"]) & set(first_fids)), status

        # Process ONLY pending batches without reopening D001's raw fragments.
        reopened_raw: list[str] = []
        for pending in status["pending_digests"]:
            fids = pending["fragment_ids"]
            for fid in fids:
                assert fid not in first_fids, f"Completed raw fragment {fid} should not be reprocessed"
                reopened_raw.append(fid)
            batch_obls = [
                {
                    "canonical_id": obl["canonical_id"],
                    "obligation_id": obl.get("explicit_id") or obl["canonical_id"],
                    "text": obl["text_preview"],
                    "source_refs": [fid],
                }
                for obl in source_index["obligations"]
                for fid in [next((x for x in obl["fragment_ids"] if x in fids), None)]
                if fid
            ]
            preplanctl.write_json(
                package / "digests" / f"{pending['digest_id']}.json",
                {
                    "digest_id": pending["digest_id"],
                    "fragment_ids": fids,
                    "fragment_hashes": {fid: by_id[fid]["file_sha256"] for fid in fids},
                    "obligations": batch_obls,
                    "constraints": [],
                    "interfaces": [],
                    "dependencies": [],
                    "validation_implications": [],
                    "pattern_candidates": [],
                    "material_questions": [],
                    "contradictions": [],
                },
            )
        assert set(reopened_raw) == set(status["pending_fragment_ids"])
        final_status = preplanctl.resume_status(package)
        assert final_status["pending_digests"] == [], final_status
        assert len(final_status["completed_digests"]) == len(batches), final_status


def test_ac05_permuting_requirement_position_preserves_final_coverage() -> None:
    target_clause = "REQ-077: Payment webhooks must verify HMAC-SHA256 signatures before mutating ledger state."
    filler = [
        f"## {i}. Module {i}\n\nREQ-{i:03d}: Module {i} must emit structured telemetry events. " + (f"Context sentence {i}. " * 110)
        for i in range(1, 25)
    ]
    variants = {
        "beginning": [f"## 0. Target\n\n{target_clause}"] + filler,
        "middle": filler[:12] + [f"## 12b. Target\n\n{target_clause}"] + filler[12:],
        "end": filler + [f"## 99. Target\n\n{target_clause}"],
    }
    signatures: dict[str, str] = {}
    coverage_sets: dict[str, set[str]] = {}
    final_coverage: dict[str, set[str]] = {}
    target_canonical = f"OBL-{preplanctl.sha256_text(target_clause.lower())[:12]}"

    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        for label, sections in variants.items():
            src = root / f"perm-{label}.md"
            src.write_text("\n\n".join(sections), encoding="utf-8")
            report = preplanctl.compare_extraction_baselines(src, target_tokens=1400, max_tokens=1800)
            assert report["metrics"]["obligation_recall"] == 1.0, (label, report)
            assert target_canonical in report["one_shot"]["unique_canonical_ids"], (label, target_canonical)
            assert report["staged"]["missing_obligation_ids"] == [], (label, report)
            signatures[label] = report["metrics"]["order_invariant_signature"]
            coverage_sets[label] = set(report["one_shot"]["unique_canonical_ids"])

            # Final requirement coverage on a real prepared package, for every position of the target.
            repo = root / f"repo-{label}"
            repo.mkdir()
            assessment = preplanctl.assess_source(src)
            package, _ = preplanctl.create_package(repo, src, assessment, target_tokens=1400, max_tokens=1800)
            source_index = preplanctl.read_json(package / "SOURCE_INDEX.json")
            assert len(source_index["fragments"]) >= 3, (label, len(source_index["fragments"]))
            populate_valid_package_artifacts(package, omit_obligation_ids={"REQ-077"}, review_omit_obligation_ids=set())
            expect_preplan_error(lambda: preplanctl.validate_coverage(package), "REQ-077")
            populate_valid_package_artifacts(package)
            audit = preplanctl.validate_coverage(package)
            assert audit["missing_ids"] == [] and target_canonical in audit["covered_ids"], (label, audit)
            final_coverage[label] = set(audit["covered_ids"])

    assert signatures["beginning"] == signatures["middle"] == signatures["end"], signatures
    assert coverage_sets["beginning"] == coverage_sets["middle"] == coverage_sets["end"]
    assert final_coverage["beginning"] == final_coverage["middle"] == final_coverage["end"], final_coverage


def test_ac06_same_size_fragment_rewrite_with_unchanged_timestamp_rejected() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        repo = init_repo(root)
        source = root / "same-size.md"
        source.write_text(
            "\n\n".join(
                f"## {i}. Rule {i}\n\nREQ-{i:03d}: Worker {i} must validate checksum alpha-{i:03d}. " + ("Extra context. " * 100)
                for i in range(1, 10)
            ),
            encoding="utf-8",
        )
        assessment = preplanctl.assess_source(source)
        package, _ = preplanctl.create_package(repo, source, assessment, target_tokens=1200, max_tokens=1600)
        source_index = populate_valid_package_artifacts(package)
        preplanctl.validate_package(package)

        frag_path = package / source_index["fragments"][0]["path"]
        orig_stat = frag_path.stat()
        orig_bytes = frag_path.read_bytes()
        assert b"alpha-001" in orig_bytes
        rewritten = orig_bytes.replace(b"alpha-001", b"omega-001", 1)
        assert len(rewritten) == len(orig_bytes)
        frag_path.write_bytes(rewritten)
        os.utime(frag_path, ns=(orig_stat.st_atime_ns, orig_stat.st_mtime_ns))

        new_stat = frag_path.stat()
        assert new_stat.st_size == orig_stat.st_size
        assert new_stat.st_mtime_ns == orig_stat.st_mtime_ns

        expect_preplan_error(lambda: preplanctl.validate_consumption(package), "SHA-256 mismatch")
        expect_preplan_error(lambda: preplanctl.validate_package(package), "SHA-256 mismatch")
        expect_preplan_error(lambda: preplanctl.read_fragment(package, "F001"), "SHA-256 mismatch")


def test_ac07_nested_and_merged_table_cells_ordered_nonduplicated_anchors() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        nested_table = (
            "<w:tbl>"
            "<w:tr>"
            f"<w:tc>{w_p('REQ-N1: Nested cell obligation must stay in document order.')}</w:tc>"
            f"<w:tc>{w_p('REQ-N2: Nested sibling cell must keep unique anchor.')}</w:tc>"
            "</w:tr>"
            "</w:tbl>"
        )
        body_xml = (
            w_p("1. Matrix Overview", style="Heading1")
            + "<w:tbl>"
            # Row 1: horizontally merged header (gridSpan=2) + vertically merged origin (vMerge=restart)
            + "<w:tr>"
            + f'<w:tc><w:tcPr><w:gridSpan w:val="2"/></w:tcPr>{w_p("REQ-H1: Horizontally merged header must appear once.")}</w:tc>'
            + f'<w:tc><w:tcPr><w:vMerge w:val="restart"/></w:tcPr>{w_p("REQ-V1: Vertically merged obligation must appear once.")}</w:tc>'
            + "</w:tr>"
            # Row 2: nested table + post-nested paragraph in cell 1, normal cell 2, vMerge continuation (empty) in cell 3
            + "<w:tr>"
            + f"<w:tc>{w_p('REQ-PRE: Pre-nested paragraph must precede nested table.')}{nested_table}{w_p('REQ-POST: Post-nested paragraph must follow nested table.')}</w:tc>"
            + f"<w:tc>{w_p('REQ-C2: Adjacent cell must remain ordered.')}</w:tc>"
            + '<w:tc><w:tcPr><w:vMerge/></w:tcPr><w:p/></w:tc>'
            + "</w:tr>"
            # Row 3: vMerge continuation that repeats the origin text (must still not duplicate!)
            + "<w:tr>"
            + f"<w:tc>{w_p('REQ-R3: Row three requirement must remain intact.')}</w:tc>"
            + f"<w:tc>{w_p('REQ-R3B: Row three second cell must remain intact.')}</w:tc>"
            + f'<w:tc><w:tcPr><w:vMerge w:val="continue"/></w:tcPr>{w_p("REQ-V1: Vertically merged obligation must appear once.")}</w:tc>'
            + "</w:tr>"
            + "</w:tbl>"
            # Paragraph with unsupported tracked changes, drawing, and embedded object
            + '<w:p>'
            + '<w:r><w:t>REQ-END: Closing clause must be retained.</w:t></w:r>'
            + '<w:ins w:id="1"><w:r><w:t>Inserted draft clause</w:t></w:r></w:ins>'
            + '<w:del w:id="2"><w:r><w:delText>Deleted old clause</w:delText></w:r></w:del>'
            + '<w:r><w:drawing><w:t>Diagram label</w:t></w:drawing></w:r>'
            + '<w:r><w:object/></w:r>'
            + "</w:p>"
        )
        docx = write_docx(
            root / "nested-merged.docx",
            body_xml,
            extra_parts={
                "word/header1.xml": b"<w:hdr/>",
                "word/media/image1.png": b"\x89PNG\r\n\x1a\n",
            },
        )
        extracted = preplanctl.extract_document(docx)
        blocks = extracted["blocks"]
        anchors = [b["anchor"] for b in blocks]
        texts = [b["text"] for b in blocks]

        # Nonduplicated anchors in document order.
        assert len(anchors) == len(set(anchors)), anchors
        assert sum("REQ-H1:" in t for t in texts) == 1, texts
        assert sum("REQ-V1:" in t for t in texts) == 1, texts

        expected_order = ["REQ-H1:", "REQ-V1:", "REQ-PRE:", "REQ-N1:", "REQ-N2:", "REQ-POST:", "REQ-C2:", "REQ-R3:", "REQ-R3B:", "REQ-END:"]
        positions = [next(i for i, t in enumerate(texts) if marker in t) for marker in expected_order]
        assert positions == sorted(positions), (expected_order, positions, texts)

        # Nested table cells have table_depth == 2 and nested anchors.
        n1_block = blocks[positions[3]]
        assert n1_block["table_depth"] == 2 and "/tbl:1/" in n1_block["anchor"], n1_block
        h1_block = blocks[positions[0]]
        assert h1_block.get("grid_span") == 2 and "c:1-2" in h1_block["anchor"], h1_block

        # Unsupported structures are explicitly recorded rather than silently omitted.
        unsup_kinds = {u["kind"] for u in extracted["unsupported_structures"]}
        assert {"tracked_change_insertion", "tracked_change_deletion", "drawing_or_textbox", "embedded_object", "non_body_part"} <= unsup_kinds, unsup_kinds

        # Bounded ZIP/XML negative tests.
        # 1. Oversized XML member
        expect_preplan_error(lambda: preplanctl.extract_docx(docx, max_xml_bytes=200), "exceeds size limit")
        # 2. Too many entries
        expect_preplan_error(lambda: preplanctl.extract_docx(docx, max_entries=1), "entry count limit")
        # 3. High compression ratio (zip bomb defense)
        bomb = write_docx(root / "bomb.docx", w_p("A" * 200_000))
        expect_preplan_error(
            lambda: preplanctl.extract_docx(bomb, max_compression_ratio=5.0, min_ratio_check_bytes=1024),
            "compression ratio",
        )
        # 4. Unsafe DTD/ENTITY declaration
        dtd_path = root / "dtd.docx"
        with zipfile.ZipFile(dtd_path, "w") as zf:
            zf.writestr("word/document.xml", b'<!DOCTYPE foo [<!ENTITY x "boom">]><w:document/>')
        expect_preplan_error(lambda: preplanctl.extract_docx(dtd_path), "DTD/ENTITY")
        # 5. Excess XML nesting depth
        deep_xml = "<w:sdt><w:sdtContent>" * 20 + w_p("REQ-DEEP: Too deep.") + "</w:sdtContent></w:sdt>" * 20
        deep_docx = write_docx(root / "deep.docx", deep_xml)
        expect_preplan_error(lambda: preplanctl.extract_docx(deep_docx, max_xml_depth=15), "nesting depth")


def test_ac08_table_only_requirement_cannot_disappear_from_coverage_map() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        repo = init_repo(root)
        body_xml = (
            w_p("1. Reporting", style="Heading1")
            + w_p("REQ-900: Monthly reports must include UTC timestamps.")
            + "<w:tbl>"
            + "<w:tr>"
            + f"<w:tc>{w_p('REQ-901: Batch exports must mask all PII fields before archival.')}</w:tc>"
            + "<w:tc><w:tbl><w:tr>"
            + f"<w:tc>{w_p('REQ-902: Nested compliance rows must record retention days.')}</w:tc>"
            + "</w:tr></w:tbl></w:tc>"
            + "</w:tr>"
            + "</w:tbl>"
        )
        docx = write_docx(root / "table-only.docx", body_xml)
        assessment = preplanctl.assess_source(docx)
        package, _ = preplanctl.create_package(repo, docx, assessment)
        source_index = preplanctl.read_json(package / "SOURCE_INDEX.json")
        table_eids = {obl["explicit_id"] for obl in source_index["obligations"] if obl["from_table"]}
        assert {"REQ-901", "REQ-902"} <= table_eids, source_index["obligations"]

        # Omitting a table-only requirement from digests MUST fail validate_coverage!
        populate_valid_package_artifacts(package, omit_obligation_ids={"REQ-901"})
        expect_preplan_error(lambda: preplanctl.validate_coverage(package), "REQ-901")
        # The digest audit alone catches it: the coverage review still lists REQ-901 as covered.
        populate_valid_package_artifacts(package, omit_obligation_ids={"REQ-901"}, review_omit_obligation_ids=set())
        message = expect_preplan_error(lambda: preplanctl.validate_coverage(package), "Missing source obligations")
        assert "REQ-901" in message, message
        # ...and the digest's own validation command fails fast, before synthesis.
        expect_preplan_error(lambda: preplanctl.validate_digest(package, "D001"), "REQ-901")

        # Covering REQ-901 in digests but dropping it from COVERAGE_REVIEW covered_obligation_ids MUST fail!
        populate_valid_package_artifacts(package)
        review_path = package / "COVERAGE_REVIEW.json"
        review = preplanctl.read_json(review_path)
        req901_cid = next(o["canonical_id"] for o in source_index["obligations"] if o.get("explicit_id") == "REQ-901")
        review["covered_obligation_ids"] = [cid for cid in review["covered_obligation_ids"] if cid != req901_cid]
        preplanctl.write_json(review_path, review)
        expect_preplan_error(lambda: preplanctl.validate_coverage(package), "REQ-901")

        # Complete coverage passes coverage, package, consumption, and offline comparator with 100% table recall.
        populate_valid_package_artifacts(package)
        preplanctl.validate_package(package)
        preplanctl.validate_consumption(package)
        comparison = preplanctl.compare_extraction_baselines(docx, package)
        assert comparison["metrics"]["table_obligation_recall"] == 1.0, comparison
        assert comparison["staged"]["missing_table_obligation_ids"] == [], comparison


def test_ac09_large_repeated_blocks_change_routing_without_authoritative_deletion() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        repo = init_repo(root)
        repeated_block = "BOILERPLATE worker retry diagnostics payload " * 35
        source = root / "repetitive.md"
        blocks_text = (
            ["## 1. Authoritative Rules", "REQ-501: Retry logs must retain correlation IDs."]
            + [repeated_block] * 400
            + ["REQ-502: Final summary must report total dropped events."]
        )
        source.write_text("\n\n".join(blocks_text), encoding="utf-8")

        assessment = preplanctl.assess_source(source)
        assert assessment["raw_estimated_tokens"] >= preplanctl.HARD_TOKENS, assessment
        assert assessment["estimated_tokens"] < preplanctl.HARD_TOKENS, assessment
        assert assessment["route"] == "final_plan", assessment
        assert any(r.startswith("repetitive_size_ignored") for r in assessment["reasons"]), assessment

        # Authoritative fragments MUST NOT delete any of the 400 repeated blocks.
        package, _ = preplanctl.create_package(repo, source, assessment)
        source_index = preplanctl.read_json(package / "SOURCE_INDEX.json")
        assert source_index["block_count"] == 403, source_index["block_count"]
        joined_source = "\n\n".join(
            preplanctl.read_fragment(package, item["id"])["text"] for item in source_index["fragments"]
        )
        assert joined_source.count(repeated_block.strip()) == 400
        assert "REQ-501:" in joined_source and "REQ-502:" in joined_source


def test_offline_comparator_cli_and_recorded_limitations() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        source = root / "baseline.md"
        source.write_text(
            "\n\n".join(
                [
                    "## 1. Core",
                    "REQ-101: Service must enforce TLS 1.3.",
                    "REQ-102: Service must not enforce TLS 1.3.",
                    "REQ-103: Audit trail must persist for 365 days.",
                ]
            ),
            encoding="utf-8",
        )
        completed = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "preplanctl.py"), "compare-baselines", "--file", str(source)],
            check=True,
            capture_output=True,
            text=True,
        )
        report = json.loads(completed.stdout)
        assert report["comparator_mode"] == "deterministic_offline", report
        assert report["model_comparison_performed"] is False, report
        assert report["metrics"]["obligation_recall"] == 1.0, report
        assert report["metrics"]["contradiction_coverage"] == 1.0, report
        assert any("G002" in item for item in report["limitations"]), report["limitations"]


# ---------------------------------------------------------------------------------------------
# Task 009 review regressions (findings F01-F12 of review dispatch 009/1)
# ---------------------------------------------------------------------------------------------
def repin_source_index(package: Path, mutate: Any) -> None:
    """Mutate SOURCE_INDEX and re-pin every in-package hash, as a worker rewriting the index could."""
    index_path = package / "SOURCE_INDEX.json"
    index = preplanctl.read_json(index_path)
    mutate(index)
    index["fragments_manifest_sha256"] = preplanctl.fragments_manifest_hash(index["fragments"])
    preplanctl.write_json(index_path, index)
    meta = preplanctl.read_json(package / "package.json")
    meta["source_index_sha256"] = preplanctl.sha256_file(index_path)
    meta["fragments_manifest_sha256"] = index["fragments_manifest_sha256"]
    if isinstance(meta.get("integrity"), dict):
        meta["integrity"]["source_index_sha256"] = meta["source_index_sha256"]
        meta["integrity"]["fragments_manifest_sha256"] = index["fragments_manifest_sha256"]
    preplanctl.write_json(package / "package.json", meta)


def test_review_f01_id_less_items_cannot_cover_other_id_less_obligations() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        repo = init_repo(root)
        body_xml = (
            w_p("1. Exports", style="Heading1")
            + w_p("REQ-950: Reports must be signed.")
            + "<w:tbl><w:tr>"
            + f"<w:tc>{w_p('Batch exports must mask all PII fields before archival.')}</w:tc>"
            + f"<w:tc>{w_p('Audit exports must be retained for seven years.')}</w:tc>"
            + "</w:tr></w:tbl>"
        )
        docx = write_docx(root / "no-id.docx", body_xml)
        package, _ = preplanctl.create_package(repo, docx, preplanctl.assess_source(docx))
        source_index = preplanctl.read_json(package / "SOURCE_INDEX.json")
        mask = next(o for o in source_index["obligations"] if "mask all pii" in o["normalized_text"])
        assert mask["explicit_id"] is None and mask["from_table"], mask

        def strip_ids(omit: set[str]) -> None:
            populate_valid_package_artifacts(package, omit_obligation_ids=omit, review_omit_obligation_ids=set())
            digest_path = package / "digests" / "D001.json"
            digest = preplanctl.read_json(digest_path)
            for item in digest["obligations"]:
                item.pop("canonical_id", None)
                item.pop("obligation_id", None)
            digest["obligations"].append({"text": "General export notes for this batch.", "source_refs": ["F001"]})
            preplanctl.write_json(digest_path, digest)

        # Text-only digests still cover obligations by their text.
        strip_ids(set())
        assert preplanctl.validate_coverage(package)["missing_ids"] == []
        # An item lacking obligation_id must not match an obligation lacking explicit_id (None == None).
        strip_ids({mask["canonical_id"]})
        message = expect_preplan_error(lambda: preplanctl.validate_coverage(package), "Missing source obligations")
        assert mask["canonical_id"] in message, message
        audit = preplanctl.audit_obligation_coverage(source_index, [preplanctl.read_json(package / "digests" / "D001.json")])
        assert audit["missing_table_ids"] == [mask["canonical_id"]], audit
        # A cross-reference to another id is not coverage; a polarity-dropping fragment is not coverage.
        unit_index = {"obligations": [
            {"canonical_id": "OBL-a", "explicit_id": "REQ-001", "normalized_text": "req-001: logs must be kept.",
             "fragment_ids": ["F001"], "from_table": False},
            {"canonical_id": "OBL-b", "explicit_id": None,
             "normalized_text": "the service must not store plaintext passwords in logs.", "fragment_ids": ["F001"],
             "from_table": False},
        ]}
        unit_digest = [{"obligations": [
            {"text": "REQ-002 depends on REQ-001 for retention.", "source_refs": ["F001"]},
            {"text": "store plaintext passwords in logs", "source_refs": ["F001"]},
            # Content-free id echoes (R2-03) and a short generic fragment are not coverage either.
            {"canonical_id": "OBL-b", "obligation_id": "REQ-001", "text": "ok", "source_refs": ["F001"]},
            {"text": "the service must not store", "source_refs": ["F001"]},
        ]}]
        assert preplanctl.audit_obligation_coverage(unit_index, unit_digest)["missing_ids"] == ["REQ-001", "OBL-b"]
        unit_digest[0]["obligations"].append(
            {"canonical_id": "OBL-b", "text": "Service never keeps plaintext passwords in logs.", "source_refs": ["F001"]}
        )
        assert preplanctl.audit_obligation_coverage(unit_index, unit_digest)["missing_ids"] == ["REQ-001"]


def test_review_f02_hostile_grid_span_fails_fast() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        cell = w_p("REQ-G9: Hostile cell text must not hang extraction.")
        cases = {
            "huge": f'<w:tbl><w:tr><w:tc><w:tcPr><w:gridSpan w:val="9223372036854775807"/></w:tcPr>{cell}</w:tc></w:tr></w:tbl>',
            "huge_vmerge": (
                '<w:tbl><w:tr><w:tc><w:tcPr><w:gridSpan w:val="9223372036854775807"/><w:vMerge w:val="restart"/></w:tcPr>'
                f"{cell}</w:tc></w:tr></w:tbl>"
            ),
            "over_limit": f'<w:tbl><w:tr><w:tc><w:tcPr><w:gridSpan w:val="65"/></w:tcPr>{cell}</w:tc></w:tr></w:tbl>',
            "grid_before": f'<w:tbl><w:tr><w:trPr><w:gridBefore w:val="1000000"/></w:trPr><w:tc>{cell}</w:tc></w:tr></w:tbl>',
            "row_extent": "<w:tbl><w:tr>" + "<w:tc><w:p/></w:tc>" * 64 + f"<w:tc>{cell}</w:tc></w:tr></w:tbl>",
        }
        for label, body in cases.items():
            docx = write_docx(root / f"{label}.docx", body)
            started = time.monotonic()
            expect_preplan_error(lambda: preplanctl.extract_docx(docx), "column limit")
            assert time.monotonic() - started < 5.0, label
        # A full-width Word table (63 grid columns) still extracts.
        ok = write_docx(root / "wide.docx", f'<w:tbl><w:tr><w:tc><w:tcPr><w:gridSpan w:val="63"/></w:tcPr>{cell}</w:tc></w:tr></w:tbl>')
        blocks = preplanctl.extract_docx(ok)["blocks"]
        assert blocks[0]["anchor"] == "tbl:1/r:1/c:1-63/p:1" and blocks[0]["grid_span"] == 63, blocks


def test_review_f03_wrapped_rows_cells_and_run_level_content_are_not_dropped() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        repo = init_repo(root)
        body_xml = (
            w_p("1. Wrapped structures", style="Heading1")
            + "<w:tbl>"
            + f"<w:sdt><w:sdtPr/><w:sdtContent><w:tr><w:tc>{w_p('REQ-S1: Repeating section row must be extracted.')}</w:tc></w:tr></w:sdtContent></w:sdt>"
            + f"<w:tr><w:sdt><w:sdtContent><w:tc>{w_p('REQ-S2: Content-control cell must be extracted.')}</w:tc></w:sdtContent></w:sdt>"
            + f"<w:tc>{w_p('REQ-S3: Sibling after a wrapped cell must keep its column.')}</w:tc></w:tr>"
            + f'<w:customXml w:element="row"><w:tr><w:tc>{w_p("REQ-S4: CustomXml row must be extracted.")}</w:tc></w:tr></w:customXml>'
            + "</w:tbl>"
            + f'<w:customXml w:element="block">{w_p("REQ-S5: CustomXml block paragraph must be extracted.")}</w:customXml>'
            + '<w:p><w:customXml w:element="inline"><w:r><w:t>REQ-S6: CustomXml inline run</w:t></w:r></w:customXml>'
            + '<w:r><w:t xml:space="preserve"> must be extracted.</w:t></w:r>'
            + '<w:dir w:val="rtl"><w:r><w:t xml:space="preserve"> Directional text is kept.</w:t></w:r></w:dir></w:p>'
            + "<w:p><w:r><w:t>REQ-S7: Paragraph with a text box must be kept.</w:t></w:r>"
            + '<w:r><mc:AlternateContent><mc:Choice Requires="wps"><w:drawing><w:t>Text box clause must be recorded</w:t></w:drawing></mc:Choice></mc:AlternateContent></w:r></w:p>'
            + "<w:p><w:r><w:t>REQ-S8: Formula paragraph must be kept.</w:t></w:r><m:oMath><m:r><m:t>x=1</m:t></m:r></m:oMath></w:p>"
            + "<w:altChunk/>"
            + "<w:p><w:r><w:t>REQ-S9: Ruby paragraph must be kept.</w:t></w:r>"
            + "<w:r><w:ruby><w:rubyBase><w:r><w:t>Ruby base text</w:t></w:r></w:rubyBase></w:ruby></w:r>"
            + "<w:moveFrom><w:r><w:t>Moved away text</w:t></w:r></w:moveFrom><w:moveTo><w:r><w:t>Moved here text</w:t></w:r></w:moveTo></w:p>"
        )
        docx = write_docx(root / "wrapped.docx", body_xml)
        extracted = preplanctl.extract_document(docx)
        blocks = extracted["blocks"]
        texts = [b["text"] for b in blocks]
        anchors = [b["anchor"] for b in blocks]
        assert len(anchors) == len(set(anchors)), anchors
        markers = [f"REQ-S{n}:" for n in range(1, 10)]
        positions = [next(i for i, t in enumerate(texts) if marker in t) for marker in markers]
        assert positions == sorted(positions), (positions, texts)
        assert blocks[positions[0]]["kind"] == "table_cell" and blocks[positions[3]]["kind"] == "table_cell", blocks
        assert blocks[positions[2]]["anchor"] == "tbl:1/r:2/c:2/p:1", blocks[positions[2]]
        assert texts[positions[5]] == "REQ-S6: CustomXml inline run must be extracted. Directional text is kept.", texts[positions[5]]
        kinds = {u["kind"] for u in extracted["unsupported_structures"]}
        expected = {"drawing_or_textbox", "math_equation", "alt_chunk", "unhandled_run_element",
                    "tracked_change_move_from", "tracked_change_move_to"}
        assert expected <= kinds, kinds

        # A table-only obligation inside a wrapped row cannot disappear from the coverage map.
        package, _ = preplanctl.create_package(repo, docx, preplanctl.assess_source(docx))
        source_index = preplanctl.read_json(package / "SOURCE_INDEX.json")
        wrapped_row = next(o for o in source_index["obligations"] if "repeating section row" in o["normalized_text"])
        assert wrapped_row["from_table"], wrapped_row
        populate_valid_package_artifacts(package, omit_obligation_ids={wrapped_row["canonical_id"]}, review_omit_obligation_ids=set())
        expect_preplan_error(lambda: preplanctl.validate_coverage(package), wrapped_row["canonical_id"])
        populate_valid_package_artifacts(package)
        preplanctl.validate_package(package)


def test_review_f04_dropping_one_of_two_contradictions_is_rejected() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        repo = init_repo(root)
        source = root / "two-conflicts.md"
        source.write_text(
            "\n\n".join(
                [
                    "## 1. Cache",
                    "REQ-100: Cache must store session tokens for 60 seconds.",
                    "REQ-101: Cache must not store session tokens for 60 seconds.",
                    "## 2. Uploads",
                    "REQ-200: Upload service must compress payloads with gzip.",
                    "REQ-201: Upload service must not compress payloads with gzip.",
                ]
            ),
            encoding="utf-8",
        )
        package, _ = preplanctl.create_package(repo, source, preplanctl.assess_source(source))
        source_index = preplanctl.read_json(package / "SOURCE_INDEX.json")
        ctr_ids = [c["id"] for c in source_index["detected_contradictions"]]
        assert len(ctr_ids) == 2, source_index["detected_contradictions"]
        populate_valid_package_artifacts(package)
        preplanctl.validate_package(package)

        work_path = package / "WORKSTREAM_INDEX.json"
        work = preplanctl.read_json(work_path)
        work["contradictions"] = [c for c in work["contradictions"] if c["id"] != ctr_ids[1]]
        preplanctl.write_json(work_path, work)
        message = expect_preplan_error(lambda: preplanctl.validate_synthesis(package), "contradictions")
        assert ctr_ids[1] in message, message

        populate_valid_package_artifacts(package)
        review_path = package / "COVERAGE_REVIEW.json"
        review = preplanctl.read_json(review_path)
        review["recorded_contradictions"] = [c for c in review["recorded_contradictions"] if c["id"] != ctr_ids[1]]
        preplanctl.write_json(review_path, review)
        message = expect_preplan_error(lambda: preplanctl.validate_coverage(package), "omits contradictions")
        assert ctr_ids[1] in message, message

        # Comparator contradiction coverage is identity-based, not a count ratio.
        populate_valid_package_artifacts(package)
        for path in sorted((package / "digests").glob("D*.json")):
            digest = preplanctl.read_json(path)
            digest["contradictions"] = [c for c in digest["contradictions"] if c["id"] != ctr_ids[1]]
            preplanctl.write_json(path, digest)
        work = preplanctl.read_json(work_path)
        work["contradictions"] = [c for c in work["contradictions"] if c["id"] != ctr_ids[1]]
        work["contradictions"].append({"id": "UNRELATED-1", "detail": "Unrelated note", "source_refs": ["F001"]})
        preplanctl.write_json(work_path, work)
        report = preplanctl.compare_extraction_baselines(source, package)
        assert report["metrics"]["contradiction_coverage"] == 0.5, report["metrics"]


def test_review_f05_obligation_in_split_block_maps_to_its_own_fragment() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        repo = init_repo(root)
        clause = "REQ-777: The archiver must encrypt every late segment."
        source = root / "one-long-block.md"
        source.write_text("## 1. Archive\n\n" + "".join(f"Filler sentence number {i} explains context. " for i in range(400)) + clause, encoding="utf-8")
        package, _ = preplanctl.create_package(repo, source, preplanctl.assess_source(source), target_tokens=300, max_tokens=400)
        source_index = preplanctl.read_json(package / "SOURCE_INDEX.json")
        assert len(source_index["fragments"]) >= 3, len(source_index["fragments"])
        obl = next(o for o in source_index["obligations"] if o["explicit_id"] == "REQ-777")
        holders = [f["id"] for f in source_index["fragments"] if clause in preplanctl.read_fragment(package, f["id"])["text"]]
        assert holders and holders[0] != "F001", holders
        assert obl["fragment_ids"] == holders, (obl["fragment_ids"], holders)
        by_id = {f["id"]: f for f in source_index["fragments"]}
        assert obl["canonical_id"] in by_id[holders[0]]["obligation_ids"], by_id[holders[0]]
        populate_valid_package_artifacts(package)
        preplanctl.validate_package(package)


def test_review_f06_non_utf8_document_xml_is_rejected() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        hostile = (
            f'<?xml version="1.0" encoding="UTF-16"?><!DOCTYPE d [<!ENTITY x "boom">]>'
            f'<w:document xmlns:w="{W_NS}"><w:body><w:p><w:r><w:t>&x;</w:t></w:r></w:p></w:body></w:document>'
        )
        cases = {
            "utf16_bom": (hostile.encode("utf-16"), "UTF-8"),
            "utf16le_no_bom": (hostile.encode("utf-16-le"), "UTF-8"),
            "latin1_declared": (
                f'<?xml version="1.0" encoding="ISO-8859-1"?><w:document xmlns:w="{W_NS}"><w:body>{w_p("REQ-1: x must y.")}</w:body></w:document>'.encode("utf-8"),
                "non-UTF-8",
            ),
        }
        for label, (payload, expected) in cases.items():
            path = root / f"{label}.docx"
            with zipfile.ZipFile(path, "w") as zf:
                zf.writestr("word/document.xml", payload)
            expect_preplan_error(lambda: preplanctl.extract_docx(path), expected)
        ok = root / "bom.docx"
        with zipfile.ZipFile(ok, "w") as zf:
            zf.writestr(
                "word/document.xml",
                b"\xef\xbb\xbf" + f'<?xml version="1.0" encoding="utf-8"?><w:document xmlns:w="{W_NS}"><w:body>{w_p("REQ-2: BOM input must parse.")}</w:body></w:document>'.encode("utf-8"),
            )
        assert preplanctl.extract_docx(ok)["blocks"][0]["text"] == "REQ-2: BOM input must parse."


def test_review_f07_consumption_rehashes_raw_source_and_rejects_repinned_index() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        repo = init_repo(root)
        source = root / "spec.md"
        source.write_text(
            "\n\n".join(f"## {i}. Area {i}\n\nREQ-{i:03d}: Area {i} must keep audit record {i}. " + ("Context. " * 90) for i in range(1, 8)),
            encoding="utf-8",
        )
        package, _ = preplanctl.create_package(repo, source, preplanctl.assess_source(source), target_tokens=600, max_tokens=900)
        populate_valid_package_artifacts(package)
        assert preplanctl.validate_package(package)["source_verification"]["status"] == "verified"
        assert preplanctl.validate_consumption(package)["source_verification"]["status"] == "verified"
        pristine = root / "pristine"
        shutil.copytree(package, pristine)

        def restore() -> None:
            shutil.rmtree(package)
            shutil.copytree(pristine, package)

        # A worker drops an uncovered obligation from SOURCE_INDEX and re-pins every in-package hash.
        populate_valid_package_artifacts(package, omit_obligation_ids={"REQ-003"})
        req3 = next(o for o in preplanctl.read_json(package / "SOURCE_INDEX.json")["obligations"] if o["explicit_id"] == "REQ-003")
        repin_source_index(package, lambda idx: idx.update(obligations=[o for o in idx["obligations"] if o["explicit_id"] != "REQ-003"]))
        preplanctl.validate_coverage(package)  # the in-package chain alone cannot see it
        message = expect_preplan_error(lambda: preplanctl.validate_package(package), "obligations differ")
        assert req3["canonical_id"] in message, message
        restore()

        # A re-pinned block_count (which the zero-obligation floor gate relies on) is re-derived too.
        repin_source_index(package, lambda idx: idx.update(block_count=0))
        expect_preplan_error(lambda: preplanctl.validate_package(package), "block_count")
        restore()

        # A missing schema-v2 pin is an error, not a skipped check.
        repin_source_index(package, lambda idx: idx["fragments"][0].pop("file_sha256"))
        expect_preplan_error(lambda: preplanctl.verify_fragments(package), "file_sha256")
        restore()
        meta = preplanctl.read_json(package / "package.json")
        meta.pop("integrity")
        preplanctl.write_json(package / "package.json", meta)
        expect_preplan_error(lambda: preplanctl.validate_consumption(package), "integrity pins")
        restore()

        # A stale extractor version is rejected at consumption.
        def old_version(idx: dict[str, Any]) -> None:
            idx["extraction_version"] = "ooxml-text-v2"

        repin_source_index(package, old_version)
        meta = preplanctl.read_json(package / "package.json")
        meta["extraction_version"] = "ooxml-text-v2"
        preplanctl.write_json(package / "package.json", meta)
        expect_preplan_error(lambda: preplanctl.validate_consumption(package), "extraction_version")
        restore()

        # The raw source changing after validation makes the package stale at consumption.
        original = source.read_bytes()
        source.write_bytes(original + b"\n\nREQ-999: A late edit must be planned.\n")
        expect_preplan_error(lambda: preplanctl.validate_consumption(package), "Raw source changed")
        source.write_bytes(original)

        # A moved source is reported as unavailable; an explicit path re-derives it; a bad path fails.
        moved = root / "moved-spec.md"
        source.rename(moved)
        assert preplanctl.validate_consumption(package)["source_verification"]["status"] == "unavailable"
        expect_preplan_error(lambda: preplanctl.validate_consumption(package, require_source=True), "unavailable")
        assert preplanctl.validate_consumption(package, source=moved)["source_verification"]["status"] == "verified"
        expect_preplan_error(lambda: preplanctl.validate_consumption(package, source=root / "missing.md"), "regular file")


def test_review_f09_duplicate_fragment_ids_paths_and_consumption_requests() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        repo = init_repo(root)
        source = root / "dups.md"
        source.write_text(
            "\n\n".join(f"## {i}. Part {i}\n\nREQ-{i:03d}: Part {i} must stay unique. " + ("Words. " * 120) for i in range(1, 6)),
            encoding="utf-8",
        )
        package, _ = preplanctl.create_package(repo, source, preplanctl.assess_source(source), target_tokens=400, max_tokens=600)
        populate_valid_package_artifacts(package)
        preplanctl.validate_package(package)
        expect_preplan_error(lambda: preplanctl.validate_consumption(package, fragment_ids=["F001", "F001"]), "Duplicate fragment ids requested")
        expect_preplan_error(lambda: preplanctl.validate_consumption(package, fragment_ids=["F999"]), "Unknown fragment id")
        index_path = package / "SOURCE_INDEX.json"
        original = index_path.read_bytes()
        index = preplanctl.read_json(index_path)
        index["fragments"].append(dict(index["fragments"][0], path=index["fragments"][1]["path"]))
        preplanctl.write_json(index_path, index)
        expect_preplan_error(lambda: preplanctl.verify_fragments(package), "Duplicate fragment id")
        index = json.loads(original.decode("utf-8"))
        index["fragments"].append(dict(index["fragments"][0], id="F900"))
        preplanctl.write_json(index_path, index)
        expect_preplan_error(lambda: preplanctl.verify_fragments(package), "Duplicate fragment path")


def test_review_f12_grid_before_aligns_columns_and_vertical_merges() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        origin = w_p("REQ-G2: Second column merged origin must appear once.")
        body_xml = (
            "<w:tbl>"
            + f"<w:tr><w:tc>{w_p('REQ-G1: First column must appear once.')}</w:tc>"
            + f'<w:tc><w:tcPr><w:vMerge w:val="restart"/></w:tcPr>{origin}</w:tc></w:tr>'
            + '<w:tr><w:trPr><w:gridBefore w:val="1"/></w:trPr>'
            + f'<w:tc><w:tcPr><w:vMerge w:val="continue"/></w:tcPr>{origin}</w:tc>'
            + f"<w:tc>{w_p('REQ-G3: Third column keeps its anchor.')}</w:tc></w:tr>"
            + "</w:tbl>"
        )
        blocks = preplanctl.extract_docx(write_docx(root / "grid-before.docx", body_xml))["blocks"]
        texts = [b["text"] for b in blocks]
        assert sum("REQ-G2:" in t for t in texts) == 1, texts
        g3 = next(b for b in blocks if "REQ-G3:" in b["text"])
        assert g3["anchor"] == "tbl:1/r:2/c:3/p:1", g3


def test_review_f08_primary_plan_guidance_names_validator_contracts() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        repo = init_repo(root)
        source = root / "guide.md"
        source.write_text(
            "\n\n".join(f"## {i}. Topic {i}\n\nREQ-{i:03d}: Topic {i} must be honored. " + ("Body. " * 200) for i in range(1, 8)),
            encoding="utf-8",
        )
        package, metadata = preplanctl.create_package(repo, source, preplanctl.assess_source(source), target_tokens=500, max_tokens=700)
        spec = preplanctl.make_primary_spec(repo, package, metadata)
        tasks = spec["tasks"]
        digest_text = "\n".join(tasks[0]["implementation_guidance"])
        synth_text, review_text, handoff_text = ("\n".join(t["implementation_guidance"]) for t in tasks[-3:])
        for needle in ("canonical_id", "fragment_hashes", "obligation_ids", "detected_contradictions"):
            assert needle in digest_text, needle
        assert "detected_contradictions" in synth_text
        assert "covered_obligation_ids" in review_text and "recorded_contradictions" in review_text
        assert "acknowledged_unsupported_structures" in review_text and "acknowledged_obligation_floor" in review_text
        assert "restates the obligation" in digest_text and "D001-C1" in digest_text
        assert "validate-consumption" in handoff_text and "--require-source" in handoff_text
        assert max(len(line) for task in tasks for line in task["implementation_guidance"]) <= 240


def test_review_r2_01_split_markdown_table_rows_map_to_their_own_fragment() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        repo = init_repo(root)
        rows = [f"| REQ-{i:03d} | Component {i} must persist checkpoint {i} before shutdown completes. |" for i in range(1, 121)]
        source = root / "table.md"
        source.write_text("## 1. Requirements\n\n| ID | Requirement |\n|---|---|\n" + "\n".join(rows) + "\n", encoding="utf-8")
        package, _ = preplanctl.create_package(repo, source, preplanctl.assess_source(source), target_tokens=300, max_tokens=400)
        source_index = preplanctl.read_json(package / "SOURCE_INDEX.json")
        texts = {f["id"]: preplanctl.read_fragment(package, f["id"])["text"] for f in source_index["fragments"]}
        assert len(texts) >= 5, len(texts)
        for obl in source_index["obligations"]:
            if obl["explicit_id"]:
                row = next(r for r in rows if f"| {obl['explicit_id']} |" in r)
                assert obl["fragment_ids"] == [fid for fid, text in texts.items() if row in text], obl
                assert len(obl["fragment_ids"]) == 1, obl
        batches = preplanctl.batch_fragments(source_index["fragments"])
        assert len(batches) >= 2, len(batches)
        victim = next(o for o in source_index["obligations"] if o["fragment_ids"] == [batches[-1][0]["id"]])
        # Omit the row from its own digest while another batch's digest echoes its id: still a failure.
        populate_valid_package_artifacts(package, omit_obligation_ids={victim["canonical_id"]}, review_omit_obligation_ids=set())
        echo_path = package / "digests" / "D001.json"
        echo = preplanctl.read_json(echo_path)
        echo["obligations"].append({"canonical_id": victim["canonical_id"], "text": victim["text_preview"], "source_refs": [echo["fragment_ids"][0]]})
        preplanctl.write_json(echo_path, echo)
        expect_preplan_error(lambda: preplanctl.validate_coverage(package), victim["explicit_id"])
        populate_valid_package_artifacts(package)
        preplanctl.validate_package(package)


def test_review_r2_02_tracked_insertion_requirement_must_be_acknowledged() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        repo = init_repo(root)
        body_xml = (
            w_p("REQ-400: Base paragraph must stay extracted.")
            + "<w:tbl><w:tr><w:tc><w:p>"
            + '<w:ins w:id="7"><w:r><w:t>REQ-401: Tracked table row must be reviewed.</w:t></w:r></w:ins>'
            + "</w:p></w:tc></w:tr></w:tbl>"
        )
        docx = write_docx(root / "tracked.docx", body_xml)
        package, _ = preplanctl.create_package(repo, docx, preplanctl.assess_source(docx))
        source_index = preplanctl.read_json(package / "SOURCE_INDEX.json")
        tracked = [u for u in source_index["unsupported_structures"] if u["kind"] == "tracked_change_insertion"]
        assert tracked and "REQ-401" in tracked[0]["preview"], source_index["unsupported_structures"]
        assert all(o["explicit_id"] != "REQ-401" for o in source_index["obligations"]), source_index["obligations"]
        populate_valid_package_artifacts(package, acknowledge_unsupported=False)
        expect_preplan_error(lambda: preplanctl.validate_coverage(package), "acknowledged_unsupported_structures")
        populate_valid_package_artifacts(package)
        review_path = package / "COVERAGE_REVIEW.json"
        review = preplanctl.read_json(review_path)
        review["acknowledged_unsupported_structures"] = []
        preplanctl.write_json(review_path, review)
        message = expect_preplan_error(lambda: preplanctl.validate_coverage(package), "omits")
        assert "tracked_change_insertion@" in message, message
        populate_valid_package_artifacts(package, review_status="blocked", acknowledge_unsupported=False)
        preplanctl.validate_coverage(package)  # blocking is the other legal answer
        populate_valid_package_artifacts(package)
        preplanctl.validate_package(package)


def test_review_r2_04_05_digest_validation_fails_fast_and_requires_ids() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        repo = init_repo(root)
        source = root / "fast.md"
        source.write_text(
            "\n\n".join(f"## {i}. Unit {i}\n\nREQ-{i:03d}: Unit {i} must log event {i}. " + ("Prose. " * 150) for i in range(1, 13)),
            encoding="utf-8",
        )
        package, _ = preplanctl.create_package(repo, source, preplanctl.assess_source(source), target_tokens=500, max_tokens=700)
        source_index = populate_valid_package_artifacts(package)
        d1_path = package / "digests" / "D001.json"
        good = preplanctl.read_json(d1_path)
        batch_ids = set(good["fragment_ids"])
        own = next(o for o in source_index["obligations"] if set(o["fragment_ids"]) <= batch_ids)
        # A digest that drops one of its own obligations is invalid, so resume keeps it pending.
        partial = json.loads(json.dumps(good))
        partial["obligations"] = [i for i in partial["obligations"] if i.get("canonical_id") != own["canonical_id"]]
        preplanctl.write_json(d1_path, partial)
        expect_preplan_error(lambda: preplanctl.validate_digest(package, "D001"), own["explicit_id"])
        status = preplanctl.resume_status(package)
        assert "D001" not in status["completed_digests"] and status["invalid_digests"][0]["digest_id"] == "D001", status
        # fragment_hashes is mandatory for schema-v2 packages.
        missing_hashes = dict(good)
        missing_hashes.pop("fragment_hashes")
        preplanctl.write_json(d1_path, missing_hashes)
        expect_preplan_error(lambda: preplanctl.validate_digest(package, "D001"), "fragment_hashes is required")
        # Digest contradictions need an id so later stages carry them by identity.
        id_less = dict(good, contradictions=[{"text": "Local conflict", "source_refs": [good["fragment_ids"][0]]}])
        preplanctl.write_json(d1_path, id_less)
        expect_preplan_error(lambda: preplanctl.validate_digest(package, "D001"), "needs an id")
        preplanctl.write_json(d1_path, good)
        preplanctl.validate_digest(package, "D001")


def test_review_r3_01_02_restatement_rule_accepts_translations_and_explains_failures() -> None:
    index = {"obligations": [
        {"canonical_id": "OBL-aaaaaaaaaaaa", "explicit_id": "REQ-010", "fragment_ids": ["F001"], "from_table": True,
         "normalized_text": "req-010: o sistema deve mascarar o cpf antes do arquivamento."},
        {"canonical_id": "OBL-bbbbbbbbbbbb", "explicit_id": "RULE-12", "fragment_ids": ["F001"], "from_table": False,
         "normalized_text": "rule-12: operators must rotate keys quarterly."},
        {"canonical_id": "OBL-cccccccccccc", "explicit_id": None, "fragment_ids": ["F002"], "from_table": False,
         "normalized_text": "exports must be signed."},
    ]}
    digest = [{"obligations": [
        # A faithful English digest of a Portuguese row, with the right id: coverage.
        {"canonical_id": "OBL-aaaaaaaaaaaa", "text": "REQ-010: The system must mask the CPF before archiving.", "source_refs": ["F001"]},
        # Bare echoes of RULE-/OBL- ids are not restatements, with or without id fields.
        {"obligation_id": "RULE-12", "text": "RULE-12", "source_refs": ["F001"]},
        {"text": "RULE-12 OBL-bbbbbbbbbbbb", "source_refs": ["F001"]},
        # The right id on the wrong fragment is not coverage.
        {"canonical_id": "OBL-cccccccccccc", "text": "Every export carries a signature.", "source_refs": ["F001"]},
    ]}]
    audit = preplanctl.audit_obligation_coverage(index, digest)
    assert audit["covered_ids"] == ["OBL-aaaaaaaaaaaa"], audit
    assert audit["missing_ids"] == ["RULE-12", "OBL-cccccccccccc"], audit
    assert "without a restatement" in audit["missing_reasons"]["RULE-12"], audit["missing_reasons"]
    assert "cites its fragment" in audit["missing_reasons"]["OBL-cccccccccccc"], audit["missing_reasons"]
    # Unspaced scripts (R4-02): a CJK restatement with the id counts; a single CJK letter does not.
    assert preplanctl._substantive("REQ-1 加密所有数据") and not preplanctl._substantive("REQ-1 是")


def test_review_r4_01_hierarchical_and_shared_ids_never_cover_siblings() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        repo = init_repo(root)
        source = root / "dotted.md"
        source.write_text(
            "## 1. Access\n\n| ID | Requirement |\n|---|---|\n"
            "| REQ-7.1 | Users must log in with MFA. |\n"
            "| REQ-7.2 | Sessions must expire after 15 minutes. |\n"
            "| REQ-007-A | Admins must approve exports. |\n",
            encoding="utf-8",
        )
        package, _ = preplanctl.create_package(repo, source, preplanctl.assess_source(source))
        source_index = preplanctl.read_json(package / "SOURCE_INDEX.json")
        assert [o["explicit_id"] for o in source_index["obligations"]] == ["REQ-7.1", "REQ-7.2", "REQ-007-A"], source_index["obligations"]
        assert source_index["duplicate_explicit_ids"] == [] and source_index["detected_contradictions"] == [], source_index
        populate_valid_package_artifacts(package, omit_obligation_ids={"REQ-7.2"}, review_omit_obligation_ids=set())
        digest_path = package / "digests" / "D001.json"
        digest = preplanctl.read_json(digest_path)
        sibling = next(i for i in digest["obligations"] if i["obligation_id"] == "REQ-7.1")
        sibling["text"] = "REQ-7.1: Users must log in with MFA."
        preplanctl.write_json(digest_path, digest)
        expect_preplan_error(lambda: preplanctl.validate_digest(package, "D001"), "REQ-7.2")
        expect_preplan_error(lambda: preplanctl.validate_coverage(package), "REQ-7.2")
    # A genuinely shared explicit id identifies neither clause: canonical id or text only.
    shared = {"obligations": [
        {"canonical_id": "OBL-111111111111", "explicit_id": "REQ-9", "fragment_ids": ["F001"], "from_table": False,
         "normalized_text": "req-9: tokens must rotate daily."},
        {"canonical_id": "OBL-222222222222", "explicit_id": "REQ-9", "fragment_ids": ["F001"], "from_table": False,
         "normalized_text": "req-9: tokens must never be logged."},
    ], "duplicate_explicit_ids": [{"explicit_id": "REQ-9"}]}
    items = [{"obligation_id": "REQ-9", "text": "REQ-9: Rotate tokens every day.", "source_refs": ["F001"]}]
    audit = preplanctl.audit_obligation_coverage(shared, [{"obligations": items}])
    assert audit["missing_ids"] == ["OBL-111111111111", "OBL-222222222222"], audit
    items.append({"canonical_id": "OBL-111111111111", "text": "REQ-9: Rotate tokens every day.", "source_refs": ["F001"]})
    audit = preplanctl.audit_obligation_coverage(shared, [{"obligations": items}])
    assert audit["missing_ids"] == ["OBL-222222222222"], audit


def test_review_r3_05_06_contradiction_id_collisions_and_acknowledgement_shape() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        repo = init_repo(root)
        source = root / "ids.md"
        source.write_text(
            "\n\n".join(f"## {i}. Unit {i}\n\nREQ-{i:03d}: Unit {i} must log event {i}. " + ("Prose. " * 150) for i in range(1, 13)),
            encoding="utf-8",
        )
        package, _ = preplanctl.create_package(repo, source, preplanctl.assess_source(source), target_tokens=500, max_tokens=700)
        populate_valid_package_artifacts(package)
        paths = sorted((package / "digests").glob("D*.json"))
        assert len(paths) >= 2, paths
        for path in paths[:2]:
            digest = preplanctl.read_json(path)
            digest["contradictions"] = [{"id": "C1", "text": "Local conflict", "source_refs": [digest["fragment_ids"][0]]}]
            preplanctl.write_json(path, digest)
        # Colliding worker ids fail fast in the defective digest's own validation, not at synthesis.
        expect_preplan_error(lambda: preplanctl.validate_digest(package, "D001"), "must start with D001-")
        expect_preplan_error(lambda: preplanctl.all_digests(package), "must start with D001-")
        digest = preplanctl.read_json(paths[0])
        item = {"id": "D001-C1", "text": "Local conflict", "source_refs": [digest["fragment_ids"][0]]}
        digest["contradictions"] = [item, dict(item)]
        preplanctl.write_json(paths[0], digest)
        expect_preplan_error(lambda: preplanctl.validate_digest(package, "D001"), "duplicate contradiction id D001-C1")
        digest["contradictions"] = [item]
        preplanctl.write_json(paths[0], digest)
        preplanctl.validate_digest(package, "D001")

    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        repo = init_repo(root)
        body_xml = (
            w_p("REQ-410: Base paragraph must stay extracted.")
            + '<w:p><w:r><w:t>REQ-411: Edited paragraph must be reviewed.</w:t></w:r>'
            + '<w:ins w:id="1"><w:r><w:t> First insertion.</w:t></w:r></w:ins>'
            + '<w:ins w:id="2"><w:r><w:t> Second insertion.</w:t></w:r></w:ins></w:p>'
            + "<w:p><w:r><w:t>REQ-412: Paragraph with foreign drawing text must be kept.</w:t></w:r>"
            + "<w:customShape><a:t>Drawing-only clause must be recorded</a:t></w:customShape></w:p>"
        )
        docx = write_docx(root / "ack.docx", body_xml)
        extracted = preplanctl.extract_document(docx)
        kinds = [u["kind"] for u in extracted["unsupported_structures"]]
        assert kinds.count("tracked_change_insertion") == 2 and "unhandled_inline_element" in kinds, kinds
        package, _ = preplanctl.create_package(repo, docx, preplanctl.assess_source(docx))
        populate_valid_package_artifacts(package)
        preplanctl.validate_coverage(package)
        review_path = package / "COVERAGE_REVIEW.json"
        review = preplanctl.read_json(review_path)
        acknowledged = review["acknowledged_unsupported_structures"]
        review["acknowledged_unsupported_structures"] = [a for a in acknowledged if a["kind"] != "tracked_change_insertion"] + [
            next(a for a in acknowledged if a["kind"] == "tracked_change_insertion")
        ]
        preplanctl.write_json(review_path, review)
        expect_preplan_error(lambda: preplanctl.validate_coverage(package), "omits")
        review["acknowledged_unsupported_structures"] = acknowledged + [{"kind": "x", "location": ["tbl:1"]}]
        preplanctl.write_json(review_path, review)
        expect_preplan_error(lambda: preplanctl.validate_coverage(package), "string kind and location")


def test_review_r3_04_zero_obligation_source_needs_explicit_floor_acknowledgement() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        repo = init_repo(root)
        source = root / "pt-br.md"
        source.write_text("## 1. Cadastro\n\nRF-012 | O sistema deve mascarar o CPF antes do arquivamento.\n", encoding="utf-8")
        package, _ = preplanctl.create_package(repo, source, preplanctl.assess_source(source))
        assert preplanctl.read_json(package / "SOURCE_INDEX.json")["obligations"] == []
        populate_valid_package_artifacts(package)
        expect_preplan_error(lambda: preplanctl.validate_coverage(package), "acknowledged_obligation_floor")
        review_path = package / "COVERAGE_REVIEW.json"
        review = preplanctl.read_json(review_path)
        review["acknowledged_obligation_floor"] = "Portuguese source: reviewer matched RF-012 to D001 by hand."
        preplanctl.write_json(review_path, review)
        preplanctl.validate_package(package)


def test_review_r3_07_require_source_cli_exit_code() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        repo = init_repo(root)
        source = root / "cli.md"
        source.write_text("# Spec\n\nREQ-001: Service must verify signature token-001.\n", encoding="utf-8")
        package, _ = preplanctl.create_package(repo, source, preplanctl.assess_source(source))
        populate_valid_package_artifacts(package)
        preplanctl.validate_package(package)
        source.rename(root / "moved.md")
        script = str(SCRIPTS_DIR / "preplanctl.py")
        lax = subprocess.run([sys.executable, script, "validate-consumption", "--package", str(package)],
                             capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
        assert lax.returncode == 0 and json.loads(lax.stdout)["source_verification"]["status"] == "unavailable", lax.stderr
        strict = subprocess.run([sys.executable, script, "validate-consumption", "--package", str(package), "--require-source"],
                                capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
        assert strict.returncode == 2 and "unavailable" in strict.stderr, (strict.returncode, strict.stderr)


def main() -> int:
    tests = [
        ("AC01", test_ac01_mutating_one_byte_after_approval_invalidates_package),
        ("AC02", test_ac02_docx_paragraphs_and_table_cells_preserve_obligations_in_source_order),
        ("AC03", test_ac03_duplicates_missing_ids_contradictions_and_symlinks_rejected_or_recorded),
        ("AC04", test_ac04_interrupted_batch_resumes_from_validated_digests_without_reprocessing),
        ("AC05", test_ac05_permuting_requirement_position_preserves_final_coverage),
        ("AC06", test_ac06_same_size_fragment_rewrite_with_unchanged_timestamp_rejected),
        ("AC07", test_ac07_nested_and_merged_table_cells_ordered_nonduplicated_anchors),
        ("AC08", test_ac08_table_only_requirement_cannot_disappear_from_coverage_map),
        ("AC09", test_ac09_large_repeated_blocks_change_routing_without_authoritative_deletion),
        ("COMPARATOR", test_offline_comparator_cli_and_recorded_limitations),
        ("R009-F01", test_review_f01_id_less_items_cannot_cover_other_id_less_obligations),
        ("R009-F02", test_review_f02_hostile_grid_span_fails_fast),
        ("R009-F03", test_review_f03_wrapped_rows_cells_and_run_level_content_are_not_dropped),
        ("R009-F04", test_review_f04_dropping_one_of_two_contradictions_is_rejected),
        ("R009-F05", test_review_f05_obligation_in_split_block_maps_to_its_own_fragment),
        ("R009-F06", test_review_f06_non_utf8_document_xml_is_rejected),
        ("R009-F07", test_review_f07_consumption_rehashes_raw_source_and_rejects_repinned_index),
        ("R009-F08", test_review_f08_primary_plan_guidance_names_validator_contracts),
        ("R009-F09", test_review_f09_duplicate_fragment_ids_paths_and_consumption_requests),
        ("R009-F12", test_review_f12_grid_before_aligns_columns_and_vertical_merges),
        ("R009-R2-01", test_review_r2_01_split_markdown_table_rows_map_to_their_own_fragment),
        ("R009-R2-02", test_review_r2_02_tracked_insertion_requirement_must_be_acknowledged),
        ("R009-R2-04", test_review_r2_04_05_digest_validation_fails_fast_and_requires_ids),
        ("R009-R3-01", test_review_r3_01_02_restatement_rule_accepts_translations_and_explains_failures),
        ("R009-R3-04", test_review_r3_04_zero_obligation_source_needs_explicit_floor_acknowledgement),
        ("R009-R3-05", test_review_r3_05_06_contradiction_id_collisions_and_acknowledgement_shape),
        ("R009-R3-07", test_review_r3_07_require_source_cli_exit_code),
        ("R009-R4-01", test_review_r4_01_hierarchical_and_shared_ids_never_cover_siblings),
    ]
    for label, fn in tests:
        fn()
        print(f"PASS {label} {fn.__name__}", flush=True)
    print("All Task 008/009 primary-planning acceptance tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
