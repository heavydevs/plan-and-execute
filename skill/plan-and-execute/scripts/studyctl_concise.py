#!/usr/bin/env python3
"""Study controller with the concise derived-artifact contract installed."""
from __future__ import annotations

from artifact_contract import install_study_contract

studyctl = install_study_contract()

if __name__ == "__main__":
    raise SystemExit(studyctl.main())
