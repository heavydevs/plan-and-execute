#!/usr/bin/env python3
"""Strict isolated runner with concise prompts, current routes, and hard ceilings."""
from __future__ import annotations

from artifact_contract import install_plan_contract
from runner_contract import install_runner_contract

planctl = install_plan_contract()

import routingctl  # noqa: E402

_original_default_config = planctl.default_config


def _economic_default_config():
    return routingctl.configure_config(_original_default_config())


planctl.default_config = _economic_default_config

import run_isolated  # noqa: E402

install_runner_contract(run_isolated)

if __name__ == "__main__":
    raise SystemExit(run_isolated.main())
