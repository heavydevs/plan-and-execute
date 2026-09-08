#!/usr/bin/env python3
"""Plan controller with concise artifacts and current economical model routing."""
from __future__ import annotations

from artifact_contract import install_plan_contract

planctl = install_plan_contract()

import routingctl  # noqa: E402

_original_default_config = planctl.default_config


def _economic_default_config():
    return routingctl.configure_config(_original_default_config())


planctl.default_config = _economic_default_config

if __name__ == "__main__":
    raise SystemExit(planctl.main())
