#!/usr/bin/env python3
"""Strict isolated runner with concise prompts and current adaptive routes."""
from __future__ import annotations

from artifact_contract import install_plan_contract
from runner_contract import install_runner_contract
import routingctl

planctl = routingctl.install_current_model_catalog(install_plan_contract())

import run_isolated  # noqa: E402

routingctl.install_runtime_model_catalog(run_isolated)
install_runner_contract(run_isolated)

if __name__ == "__main__":
    raise SystemExit(run_isolated.main())
