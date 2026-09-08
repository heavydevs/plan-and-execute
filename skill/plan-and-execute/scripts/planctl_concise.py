#!/usr/bin/env python3
"""Plan controller with concise artifacts and current adaptive model routing."""
from __future__ import annotations

from artifact_contract import install_plan_contract
import routingctl

planctl = routingctl.install_current_model_catalog(install_plan_contract())

if __name__ == "__main__":
    raise SystemExit(planctl.main())
