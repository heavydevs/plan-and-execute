#!/usr/bin/env python3
"""Strict isolated runner with concise prompts, state, and summary inputs."""
from __future__ import annotations

from artifact_contract import install_plan_contract, install_runner_contract

install_plan_contract()
import run_isolated

install_runner_contract(run_isolated)

if __name__ == "__main__":
    raise SystemExit(run_isolated.main())
