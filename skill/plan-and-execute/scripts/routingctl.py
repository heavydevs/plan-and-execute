#!/usr/bin/env python3
"""Apply the current provider model catalog to plan configuration.

The skill chooses routes from task semantics and evidence. This module only keeps
concrete provider model ids and compatibility effort caps current; it does not
impose user budget ceilings or choose a route for the agent.
"""
from __future__ import annotations

import copy
from typing import Any

MODEL_MAP_VERSION = "2026-09-08-v2"
CURRENT_MODELS: dict[str, dict[str, str]] = {
    "claude": {
        "economy": "haiku",
        "standard": "sonnet",
        "strong": "opus",
        "max": "claude-fable-5-1",
    },
    "codex": {
        "economy": "gpt-5.6-luna",
        "standard": "gpt-5.6-terra",
        # Astra low/medium supersedes Sol-high as the default hard-work family.
        # Keep effort separate from model tier so the agent can spend only the
        # reasoning depth justified by verifiability, risk, and failure evidence.
        "strong": "gpt-6-astra",
        "max": "gpt-6-astra",
    },
}

# These are provider/model compatibility guards, not economic ceilings. The
# task still chooses any supported effort up to the model's available range.
CURRENT_EFFORT_CAPS: dict[str, dict[str, str]] = {
    "claude": {
        "economy": "medium",
        "standard": "max",
        "strong": "max",
        "max": "max",
    },
    "codex": {
        "economy": "max",
        "standard": "max",
        "strong": "max",
        "max": "max",
    },
}


class RoutingError(RuntimeError):
    pass


def configure_config(raw: dict[str, Any]) -> dict[str, Any]:
    """Return config with the current model catalog applied."""
    if not isinstance(raw, dict):
        raise RoutingError("orchestrator.config.json must contain an object")

    config = copy.deepcopy(raw)
    for provider, model_map in CURRENT_MODELS.items():
        provider_cfg = config.setdefault(provider, {})
        if not isinstance(provider_cfg, dict):
            raise RoutingError(f"{provider} config must be an object")
        models = provider_cfg.setdefault("models", {})
        if not isinstance(models, dict):
            raise RoutingError(f"{provider}.models must be an object")
        models.update(model_map)

        caps = provider_cfg.setdefault("max_effort_by_tier", {})
        if not isinstance(caps, dict):
            raise RoutingError(f"{provider}.max_effort_by_tier must be an object")
        caps.update(CURRENT_EFFORT_CAPS[provider])

    config["routing_policy"] = {
        "model_map_version": MODEL_MAP_VERSION,
        "selection": "adaptive",
    }
    return config


def install_current_model_catalog(planctl_module: Any) -> Any:
    """Install the catalog once on a planctl module used by concise entrypoints."""
    if getattr(planctl_module, "_current_model_catalog_installed", False):
        return planctl_module
    original_default_config = planctl_module.default_config

    def current_default_config() -> dict[str, Any]:
        return configure_config(original_default_config())

    planctl_module.default_config = current_default_config
    planctl_module._current_model_catalog_installed = True
    return planctl_module
