# Task 008 Implementation Outcome — Oversized Request Fragmentation and Prepared Packages

## Summary

Implemented the revised primary-planning contracts for feature `F002` in `skill/plan-and-execute/scripts/preplanctl.py`, updated `skill/plan-and-execute/references/PRIMARY_PLANNING.md` and `skill/plan-and-execute/references/PLANNING_INPUT_CONTRACT.md`, expanded regression tests in `skill/plan-and-execute/scripts/preplan_self_test.py`, and created the Task 008 acceptance suite in `test/optimization/primary_planning_self_test.py`.

## Implemented Contracts

1. **Content-addressed integrity and consumption-time verification (S002)**
   - Added streamed SHA-256 hashing (`sha256_file`), canonical extracted block-stream hashing (`canonical_block_stream_sha256`), `EXTRACTION_VERSION = "ooxml-text-v2"`, per-fragment `file_sha256` / `file_bytes` / `source_text_sha256`, `fragments_manifest_sha256`, and `source_index_sha256`.
   - Fixed `safe_source` and added `safe_package_path` + `_is_link` to reject symlinks, Windows NTFS junctions/reparse points, path traversal (`..`), absolute/escaping references, duplicate IDs, and missing IDs before resolving targets.
   - Enforced `verify_fragments` across `validate_digest`, `all_digests`, `validate_synthesis`, `validate_coverage`, `validate_package`, `read_fragment`, `resume_status`, and the new read-only `validate_consumption` gate (`preplanctl.py validate-consumption`), recomputing content SHA-256 from disk without trusting file size or modification timestamps.
   - Added `resume_status` (`preplanctl.py resume-status`) so interrupted batches resume from validated digests without reopening completed raw fragments.

2. **Bounded, ordered OOXML extraction with nested tables, merged cells, and unsupported-structure warnings (S003)**
   - Replaced flat body-paragraph scanning in `docx_blocks` with `extract_docx` / `extract_document`: a deterministic, depth-bounded OOXML walker traversing paragraphs, tables, nested tables (`table_depth >= 2`), and content controls in document order with unique, nonduplicated anchors (`p:*`, `tbl:*/r:*/c:*/...`).
   - Handled horizontal (`w:gridSpan`, `w:hMerge`) and vertical (`w:vMerge`) merges without duplicating origin cell obligations.
   - Enforced bounded ZIP/XML limits (`MAX_DOCX_ARCHIVE_BYTES`, `MAX_DOCX_ENTRIES`, `MAX_DOCX_XML_BYTES` via streaming cap, `MAX_DOCX_COMPRESSION_RATIO`, `MAX_XML_DEPTH`) and rejected `<!DOCTYPE`/`<!ENTITY` declarations.
   - Explicitly recorded tracked changes (`w:ins`, `w:del`), drawings/text boxes (`w:drawing`, `w:pict`, `w:txbxContent`, `mc:AlternateContent`), embedded objects (`w:object`), and non-body parts (`word/header*.xml`, `word/footer*.xml`, `word/footnotes.xml`, `word/endnotes.xml`, `word/comments.xml`, `word/embeddings/*`, `word/media/*`) in `SOURCE_INDEX.json["unsupported_structures"]`.

3. **Unique obligation coverage, contradiction preservation, and offline one-shot comparator (S004)**
   - Added deterministic `extract_obligations`, `detect_contradictions`, and `audit_obligation_coverage`.
   - Enforced unique source obligation coverage (including table-only obligations) and preserved contradictions across `SOURCE_INDEX.json`, `digests/D*.json`, `WORKSTREAM_INDEX.json`, and `COVERAGE_REVIEW.json`.
   - Retained `SOFT_TOKENS`/`HARD_TOKENS`/`BREADTH_*`/`DEPENDENCY_REFS` as tunable operational defaults; verified repeated blocks deduplicate only the routing estimate (`working_set_tokens`) and are never removed from authoritative fragments.
   - Added offline deterministic `compare_extraction_baselines` (`preplanctl.py compare-baselines`) measuring obligation recall, table-obligation recall, contradiction coverage, and order-invariant coverage signatures without calling external models.

## Acceptance Coverage (AC01–AC09)

- **AC01**: `test_ac01_mutating_one_byte_after_approval_invalidates_package`
- **AC02**: `test_ac02_docx_paragraphs_and_table_cells_preserve_obligations_in_source_order`
- **AC03**: `test_ac03_duplicates_missing_ids_contradictions_and_symlinks_rejected_or_recorded`
- **AC04**: `test_ac04_interrupted_batch_resumes_from_validated_digests_without_reprocessing`
- **AC05**: `test_ac05_permuting_requirement_position_preserves_final_coverage`
- **AC06**: `test_ac06_same_size_fragment_rewrite_with_unchanged_timestamp_rejected`
- **AC07**: `test_ac07_nested_and_merged_table_cells_ordered_nonduplicated_anchors`
- **AC08**: `test_ac08_table_only_requirement_cannot_disappear_from_coverage_map`
- **AC09**: `test_ac09_large_repeated_blocks_change_routing_without_authoritative_deletion`

## Recorded Limitations

- Live model-based digest quality comparison was not performed (requires owner confirmation under `G002`); baseline comparison uses the deterministic offline comparator only.
- Unsupported Office structures (images/drawings, text boxes, embedded OLE objects, tracked changes, headers/footers/footnotes/comments) are recorded explicitly in `SOURCE_INDEX.json["unsupported_structures"]` rather than parsed into body text or OCR'd.
- On this Windows host without `SeCreateSymbolicLinkPrivilege` (`WinError 1314`), `os.symlink` creation is blocked by OS policy; link rejection was validated against a real NTFS directory junction (`mklink /J`) plus deterministic `Path.is_symlink` guard coverage (and real `os.symlink` runs automatically where permitted).
- Independent max-capability review (`009`) remains a separate later acceptance gate; neither prepared research nor this implementation receipt proves independent review completion.
