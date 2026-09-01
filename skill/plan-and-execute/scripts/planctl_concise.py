#!/usr/bin/env python3
"""Plan controller with the concise derived-artifact contract installed."""
from __future__ import annotations

from artifact_contract import install_plan_contract

planctl = install_plan_contract()

if __name__ == "__main__":
    raise SystemExit(planctl.main())
