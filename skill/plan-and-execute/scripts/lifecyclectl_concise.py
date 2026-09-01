#!/usr/bin/env python3
"""Lifecycle controller using concise plan-state projections."""
from __future__ import annotations

from artifact_contract import install_plan_contract

install_plan_contract()
import lifecyclectl

if __name__ == "__main__":
    raise SystemExit(lifecyclectl.main())
