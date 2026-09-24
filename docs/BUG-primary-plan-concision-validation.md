# Bug: generated PRIMARY_PLAN can fail its own concision validation

## Symptom

`preplanctl.py prepare` generated a valid primary-plan workspace, but `planctl_concise.py validate --plan <plan>` failed before execution status could be read.

## Reproduction

1. Run `preplanctl.py prepare` for a source that selects `primary_plan` on a Windows path with a long package id.
2. Run `planctl_concise.py validate --plan .ai-work/primary-<package-id>`.
3. Observe budget failures for generated `implementation_guidance` items.

Observed failures:

```text
Task 001 implementation_guidance[0] exceeds the 240-character derived-text budget
Task 002 implementation_guidance[0] exceeds the 240-character derived-text budget
Task 003 implementation_guidance[0] exceeds the 240-character derived-text budget
Task 004 implementation_guidance[1] exceeds the 240-character derived-text budget
```

## Cause

`preplanctl.make_primary_spec()` emits absolute fragment/package paths inside `implementation_guidance`. Those paths can exceed the `artifact_contract.py` 240-character guidance budget. The generator and validator therefore disagree.

## Impact

The prepared package can still pass `preplanctl validate-package`, but the primary control plan cannot pass `planctl` validation or report status. This weakens lifecycle recovery and cleanup even though the final-planning handoff is valid.

## Suggested fix

Use concise package-relative references in generated task guidance, for example `fragments/F001-*.md` and `digests/D001.json`; keep the package path once in execution context or derive it from the task/plan cwd. Add a regression test that creates a long Windows-style repository/package path and validates the generated primary plan through `planctl_concise.py validate`.
