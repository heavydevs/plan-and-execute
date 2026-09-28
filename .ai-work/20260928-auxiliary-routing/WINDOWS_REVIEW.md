# Task 006 native Windows follow-up

The PR matrix exposed an existing request-intake test comparing a canonical
path against an unresolved Windows temporary path. It now compares resolved
paths without weakening the expected destination.

The launcher preferred py -3 and selected Python 3.14 despite CI configuring
3.11. It now respects Python on PATH before launcher fallback, preserving the
declared interpreter and activated virtual environments.

The deep-path fixture now keeps only Windows subprocess cwd below 230 chars.
CreateProcess cannot use cwd beyond MAX_PATH even with long paths enabled.
Generated package paths still exceed 260 chars, explicitly asserted; the CLI
validation and relative-guidance assertions remain intact. Linux depth is
unchanged. Reference: https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-setcurrentdirectory

Complete npm run check passed on native Windows, Node 22 and configured
Python 3.11 before this follow-up commit. Linux full validation passed at
source checkpoint 6bb047db. Final PR CI checks all matrix entries again.
Platform-specific skips remain explicit.

This is additional validation within completed task 006. All plan artifacts
remain. Native model generation and cost/quality experiments were not run.
