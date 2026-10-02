#!/usr/bin/env python3
"""Shared model catalog cache and provider-scoped refresh controller.

Each provider owns one cache file under the user cache directory (outside the
skill tree), written by atomic replace while holding that provider's lock, so a
refresh of one provider never rewrites another provider's bytes. Facets age and
refresh independently: a fresh cache makes no source calls, and only facets
past their ttl (or the capability facet after a provider CLI version change)
call their source. A failing or missing source never blocks: the last valid
cache, or the embedded bootstrap evidence, is returned with a stale warning.

Commands: status | show | refresh | validate | snapshot (all accept --json).
Plan-local snapshot: status|diff|refresh --plan DIR and reclassify --plan DIR
manage MODEL_MATRIX.json/.md; refresh never changes a task's floor.
See references/MODEL_CATALOG.md for the cache layout and refresh rules.
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterator

import model_catalog as mc

CACHE_VERSION = 1
CACHE_FILE = "catalog.json"
LOCK_FILE = ".lock"
ENV_CACHE_DIR = "PAE_MODEL_CATALOG_CACHE"
EPOCH = "1970-01-01T00:00:00Z"
PROVENANCE_LIMIT = 20
REFRESH_STATES = ("stale", "expired")
_PROVIDER_RE = re.compile(r"^[a-z][a-z0-9_-]{0,31}$")
_RECORD_KEYS = {"cache_version", "provider", "revision", "catalog_version", "cli_version",
                "freshness_policy_version", "written_at", "models", "provenance"}

Source = Callable[[str], dict]


class CacheError(RuntimeError):
    pass


class LockTimeout(CacheError):
    pass


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_cache_root(env: dict | None = None, platform: str | None = None) -> Path:
    """Per-user cache: %LOCALAPPDATA% on Windows, XDG cache elsewhere; env override wins."""
    env = os.environ if env is None else env
    if env.get(ENV_CACHE_DIR):
        return Path(env[ENV_CACHE_DIR])
    platform = platform or sys.platform
    if platform.startswith("win"):
        base = Path(env["LOCALAPPDATA"]) if env.get("LOCALAPPDATA") else Path.home() / "AppData" / "Local"
    else:
        base = Path(env["XDG_CACHE_HOME"]) if env.get("XDG_CACHE_HOME") else Path.home() / ".cache"
    return base / "plan-and-execute" / "model-catalog"


def check_provider(provider: str) -> str:
    if not isinstance(provider, str) or not _PROVIDER_RE.match(provider):
        raise CacheError(f"invalid provider id {provider!r}")
    return provider


def _provider_catalog(provider: str, catalog_version: str, models: dict) -> dict:
    return {"schema_version": mc.SCHEMA_VERSION, "catalog_version": catalog_version,
            "providers": {provider: {"models": models}}}


def validate_record(record: Any, provider: str | None = None) -> dict:
    """Validate a per-provider cache record; models go through model_catalog.validate."""
    errors: list[tuple[str, str]] = []
    if not isinstance(record, dict):
        raise mc.CatalogError([("$", "cache record must be an object")])
    for key in sorted(set(record) - _RECORD_KEYS):
        errors.append((f"$.{key}", "unknown field"))
    if record.get("cache_version") != CACHE_VERSION:
        errors.append(("$.cache_version", f"must be {CACHE_VERSION}"))
    name = record.get("provider")
    if not isinstance(name, str) or not _PROVIDER_RE.match(name) or (provider and name != provider):
        errors.append(("$.provider", f"must be {provider!r}" if provider else "invalid provider id"))
    revision = record.get("revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 0:
        errors.append(("$.revision", "must be a non-negative integer"))
    if record.get("cli_version") is not None and not isinstance(record.get("cli_version"), str):
        errors.append(("$.cli_version", "must be a string or null"))
    if mc._parse_time(record.get("written_at")) is None:
        errors.append(("$.written_at", "required timezone-aware ISO-8601 timestamp"))
    if not isinstance(record.get("provenance"), list):
        errors.append(("$.provenance", "required list"))
    if errors:
        raise mc.CatalogError(errors)
    mc.validate(_provider_catalog(name, record.get("catalog_version"), record.get("models")))
    return copy.deepcopy(record)


def bootstrap_record(provider: str, now: datetime) -> dict | None:
    """Bootstrap evidence for a provider, or None: unknown providers yield no candidate."""
    boot = mc.bootstrap_catalog()
    body = boot["providers"].get(provider)
    if body is None:
        return None
    return {"cache_version": CACHE_VERSION, "provider": provider, "revision": 0,
            "catalog_version": boot["catalog_version"], "cli_version": None,
            "freshness_policy_version": mc.FRESHNESS_POLICY_VERSION, "written_at": _iso(now),
            "models": body["models"], "provenance": []}


class CatalogStore:
    """Per-provider cache files with atomic replace and an exclusive per-provider lock."""

    def __init__(self, root: Path | None = None, *, now: Callable[[], datetime] = _utc_now,
                 policy: dict | None = None, lock_timeout: float = 10.0, stale_lock_seconds: float = 120.0):
        self.root = Path(root) if root is not None else default_cache_root()
        self.now = now
        self.policy = policy or mc.freshness_policy()
        self.lock_timeout = lock_timeout
        self.stale_lock_seconds = stale_lock_seconds

    def path(self, provider: str) -> Path:
        return self.root / check_provider(provider) / CACHE_FILE

    def cached_providers(self) -> list[str]:
        if not self.root.is_dir():
            return []
        return sorted(p.name for p in self.root.iterdir() if _PROVIDER_RE.match(p.name) and (p / CACHE_FILE).is_file())

    def load(self, provider: str) -> tuple[dict | None, str | None]:
        """Return (valid record, None), (None, warning) for an unusable file, or (None, None) when absent."""
        path = self.path(provider)
        try:
            raw = path.read_bytes()
        except FileNotFoundError:
            return None, None
        except OSError as exc:
            return None, f"{provider}: cache unreadable ({exc.__class__.__name__})"
        try:
            return validate_record(json.loads(raw.decode("utf-8")), provider), None
        except (ValueError, mc.CatalogError) as exc:
            return None, f"{provider}: cache invalid, ignored ({str(exc)[:160]})"

    def write(self, provider: str, record: dict) -> None:
        record = validate_record(record, provider)
        path = self.path(provider)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = (json.dumps(record, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
        fd, name = tempfile.mkstemp(prefix=f".{CACHE_FILE}.", suffix=".tmp", dir=path.parent)
        tmp = Path(name)
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            for attempt in range(5):
                try:
                    os.replace(tmp, path)
                    break
                except PermissionError:
                    # Windows refuses replace while a reader holds the file open.
                    if attempt == 4:
                        raise
                    time.sleep(0.05 * (attempt + 1))
        finally:
            tmp.unlink(missing_ok=True)

    @contextlib.contextmanager
    def lock(self, provider: str) -> Iterator[None]:
        lock = self.path(provider).with_name(LOCK_FILE)
        lock.parent.mkdir(parents=True, exist_ok=True)
        deadline = time.monotonic() + self.lock_timeout
        while True:
            try:
                fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                break
            except FileExistsError:
                try:
                    age = time.time() - lock.stat().st_mtime
                except FileNotFoundError:
                    continue
                if age > self.stale_lock_seconds:
                    # Holder crashed; a lock this old cannot belong to a live refresh.
                    lock.unlink(missing_ok=True)
                    continue
                if time.monotonic() >= deadline:
                    raise LockTimeout(f"{provider}: catalog cache is locked by another refresh") from None
                time.sleep(0.02)
        try:
            os.write(fd, json.dumps({"pid": os.getpid(), "at": _iso(self.now())}).encode("utf-8"))
            os.close(fd)
            yield
        finally:
            lock.unlink(missing_ok=True)


def facet_states(record: dict, now: datetime, policy: dict) -> dict[str, str]:
    """Worst freshness state per facet across the provider's models."""
    order = {state: index for index, state in enumerate(mc.FRESHNESS_STATES)}
    worst = {facet: "fresh" for facet in mc.FACETS}
    for entry in record["models"].values():
        for facet in mc.FACETS:
            state = mc.facet_freshness(entry[facet]["observed_at"], facet, now, policy)
            if order[state] > order[worst[facet]]:
                worst[facet] = state
    if not record["models"]:
        worst = {facet: "expired" for facet in mc.FACETS}
    return worst


def plan_refresh(record: dict | None, now: datetime, policy: dict, cli_version: str | None = None,
                 force: bool = False) -> dict[str, str]:
    """Return {facet: reason} for facets that must call their source; empty means no calls."""
    if record is None:
        return {facet: "missing" for facet in mc.FACETS}
    if force:
        return {facet: "forced" for facet in mc.FACETS}
    due = {facet: state for facet, state in facet_states(record, now, policy).items() if state in REFRESH_STATES}
    if cli_version is not None and record.get("cli_version") != cli_version:
        # A new CLI may add or retire models; prices and quality do not depend on it.
        due["capability"] = "cli_version_changed"
    return {facet: due[facet] for facet in mc.FACETS if facet in due}


def _placeholder(facet: str, ref: str) -> dict:
    # Unknown, never invented: epoch timestamp makes the facet due on the next refresh.
    evidence = {"source": "bootstrap", "ref": ref}
    if facet == "economics":
        return {"currency": "USD", "input_per_mtok": None, "output_per_mtok": None, "observed_at": EPOCH, "evidence": evidence}
    return {"rank": None, "score": None, "observed_at": EPOCH, "evidence": evidence}


def _stamp(facet_body: Any, now: datetime) -> Any:
    if isinstance(facet_body, dict):
        facet_body = copy.deepcopy(facet_body)
        facet_body.setdefault("observed_at", _iso(now))
    return facet_body


def _apply_facet(models: dict, facet: str, data: Any, now: datetime, warnings: list[str], provider: str) -> dict:
    if not isinstance(data, dict):
        raise mc.CatalogError([(f"source.{facet}", "must return an object keyed by model id")])
    if facet == "capability":
        merged = {}
        for model_id, item in data.items():
            if not isinstance(item, dict):
                raise mc.CatalogError([(f"source.capability.{model_id}", "must be an object")])
            previous = models.get(model_id, {})
            merged[model_id] = {
                "tiers": item.get("tiers"),
                "capability": _stamp(item.get("capability"), now),
                "economics": previous.get("economics") or _placeholder("economics", "awaiting economics source"),
                "quality": previous.get("quality") or _placeholder("quality", "awaiting quality source"),
            }
        return merged
    merged = copy.deepcopy(models)
    for model_id, body in data.items():
        if model_id not in merged:
            warnings.append(f"{provider}: {facet} source listed unknown model {model_id!r}; ignored")
            continue
        merged[model_id][facet] = _stamp(body, now)
    return merged


def _mapping(models: dict) -> dict:
    return {model_id: sorted(entry["tiers"]) for model_id, entry in models.items()}


def refresh(store: CatalogStore, provider: str, sources: dict[str, Source], *,
            version_fn: Callable[[str], str | None] | None = None, force: bool = False) -> dict:
    """Refresh only due facets of one provider; never raises for source failures."""
    check_provider(provider)
    warnings: list[str] = []
    calls: list[str] = []
    with store.lock(provider):
        now = store.now()
        record, warning = store.load(provider)
        if warning:
            warnings.append(warning)
        cli_version = None
        if version_fn is not None:
            try:
                cli_version = version_fn(provider)
            except Exception as exc:  # noqa: BLE001 - probe failures are non-blocking evidence gaps
                warnings.append(f"{provider}: CLI version probe failed ({exc.__class__.__name__})")
        due = plan_refresh(record, now, store.policy, cli_version, force)
        base = record or bootstrap_record(provider, now)
        if not due:
            return _result(provider, "cache", record, calls, due, warnings)
        models = copy.deepcopy(base["models"]) if base else {}
        applied: list[str] = []
        for facet in due:
            source = sources.get(facet)
            if source is None:
                warnings.append(f"{provider}: no {facet} source configured; keeping last valid data")
                continue
            calls.append(facet)
            try:
                candidate = _apply_facet(models, facet, source(provider), now, warnings, provider)
                mc.validate(_provider_catalog(provider, "candidate", candidate))
            except mc.CatalogError as exc:
                warnings.append(f"{provider}: {facet} source returned invalid data ({str(exc)[:160]}); keeping last valid data")
                continue
            except Exception as exc:  # noqa: BLE001 - any source failure falls back
                warnings.append(f"{provider}: {facet} source failed ({exc.__class__.__name__}: {str(exc)[:120]}); keeping last valid data")
                continue
            models = candidate
            applied.append(facet)
        if not applied:
            origin = "cache" if record else ("bootstrap" if base else "none")
            stale = f"{provider}: catalog is stale; refresh of {', '.join(due)} failed, using {origin} data"
            return _result(provider, origin, record or base, calls, due, [*warnings, stale])
        revision = base["revision"] if base else 0
        catalog_version = base["catalog_version"] if base else f"{provider}-r0"
        mapping_changed = base is None or _mapping(base["models"]) != _mapping(models)
        if mapping_changed:
            revision += 1
            catalog_version = f"{provider}-r{revision}-{now.strftime('%Y%m%d')}"
        new_record = {
            "cache_version": CACHE_VERSION, "provider": provider, "revision": revision,
            "catalog_version": catalog_version,
            "cli_version": cli_version if "capability" in applied and cli_version is not None else (base or {}).get("cli_version"),
            "freshness_policy_version": mc.FRESHNESS_POLICY_VERSION, "written_at": _iso(now),
            "models": models, "provenance": list((base or {}).get("provenance", [])),
        }
        new_record["provenance"].append({
            "at": _iso(now), "facets": applied, "mapping_changed": mapping_changed,
            "catalog_version": catalog_version, "cli_version": new_record["cli_version"],
            "digest": mc.digest(_provider_catalog(provider, catalog_version, models)),
        })
        new_record["provenance"] = new_record["provenance"][-PROVENANCE_LIMIT:]
        store.write(provider, new_record)
        if len(applied) < len(due):
            warnings.append(f"{provider}: partial refresh; stale facets kept: {', '.join(f for f in due if f not in applied)}")
        return _result(provider, "refreshed", new_record, calls, due, warnings)


def _result(provider: str, origin: str, record: dict | None, calls: list, due: dict, warnings: list) -> dict:
    return {"provider": provider, "origin": origin, "source_calls": list(calls), "due": dict(due),
            "revision": record["revision"] if record else None,
            "catalog_version": record["catalog_version"] if record else None,
            "warnings": list(warnings), "blocking": False}


def effective_record(store: CatalogStore, provider: str) -> tuple[dict | None, str, list[str]]:
    """Last valid cache, else bootstrap, else nothing; returns (record, origin, warnings)."""
    record, warning = store.load(provider)
    warnings = [warning] if warning else []
    if record is not None:
        return record, "cache", warnings
    boot = bootstrap_record(provider, store.now())
    if boot is not None:
        warnings.append(f"{provider}: no valid cache; using bootstrap catalog")
        return boot, "bootstrap", warnings
    return None, "none", warnings


def _providers(store: CatalogStore, provider: str | None) -> list[str]:
    if provider:
        return [check_provider(provider)]
    return sorted(set(mc.bootstrap_catalog()["providers"]) | set(store.cached_providers()))


def status(store: CatalogStore, provider: str | None = None) -> dict:
    now = store.now()
    report: dict[str, Any] = {"cache_root": str(store.root), "providers": {}, "warnings": [], "blocking": False}
    for name in _providers(store, provider):
        record, origin, warnings = effective_record(store, name)
        entry: dict[str, Any] = {"origin": origin, "path": str(store.path(name))}
        if record is not None:
            states = facet_states(record, now, store.policy)
            entry.update(revision=record["revision"], catalog_version=record["catalog_version"],
                         cli_version=record["cli_version"], facets=states, models=sorted(record["models"]))
            due = [facet for facet, state in states.items() if state in REFRESH_STATES]
            if due:
                warnings.append(f"{name}: stale facets {', '.join(due)}; run refresh (non-blocking)")
        entry["warnings"] = warnings
        report["warnings"].extend(warnings)
        report["providers"][name] = entry
    return report


def merged_catalog(store: CatalogStore, provider: str | None = None) -> tuple[dict, list[str]]:
    providers: dict[str, dict] = {}
    versions: list[str] = []
    warnings: list[str] = []
    for name in _providers(store, provider):
        record, _origin, notes = effective_record(store, name)
        warnings.extend(notes)
        if record is None:
            continue
        providers[name] = {"models": record["models"]}
        versions.append(f"{name}:{record['catalog_version']}")
    catalog = {"schema_version": mc.SCHEMA_VERSION, "catalog_version": "+".join(versions) or "empty",
               "providers": providers}
    return mc.validate(catalog), warnings


def validate_cache(store: CatalogStore, provider: str | None = None) -> dict:
    report: dict[str, Any] = {"valid": True, "providers": {}}
    for name in _providers(store, provider):
        record, warning = store.load(name)
        if warning:
            report["valid"] = False
            report["providers"][name] = {"valid": False, "error": warning}
        else:
            report["providers"][name] = {"valid": True, "cached": record is not None}
    return report


def snapshot(store: CatalogStore, provider: str | None = None) -> dict:
    catalog, warnings = merged_catalog(store, provider)
    return {"captured_at": _iso(store.now()), "freshness_policy_version": mc.FRESHNESS_POLICY_VERSION,
            "digest": mc.digest(catalog), "catalog": catalog, "warnings": warnings}


# --- Plan-local MODEL_MATRIX snapshot -------------------------------------
#
# A plan pins the catalog it was planned against in MODEL_MATRIX.json (the
# authority) plus a rendered MODEL_MATRIX.md. Task bindings list per-provider
# candidates for the task's semantic floor (empty tiers skip upward, never
# downward). The manifest is never written by refresh: only pending tasks are
# rebased, and the floor changes only through the explicit reclassify command.

MATRIX_JSON = "MODEL_MATRIX.json"
MATRIX_MD = "MODEL_MATRIX.md"
MATRIX_VERSION = 1
AUDIT_LIMIT = 50
RECLASSIFIABLE = ("pending", "blocked")


class MatrixError(CacheError):
    pass


def _matrix_digest(matrix: dict) -> str:
    body = {key: value for key, value in matrix.items() if key != "matrix_digest"}
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def _tier_table(catalog: dict) -> dict[str, dict[str, str]]:
    table: dict[str, dict[str, str]] = {tier: {} for tier in mc.TIER_ORDER}
    for provider in sorted(catalog["providers"]):
        for tier, model in mc.provider_config_mapping(provider, catalog)["models"].items():
            table[tier][provider] = model
    return table


def _bind_task(task: dict, table: dict, catalog_digest: str, at: str) -> dict:
    floor = task["model_tier"]
    provider = task.get("provider", "auto")
    providers = sorted({p for row in table.values() for p in row}) if provider == "auto" else [provider]
    candidates = []
    for name in providers:
        # Skip empty tiers upward from the floor; never downgrade, never invent.
        for tier in mc.TIER_ORDER[mc.TIER_ORDER.index(floor):]:
            if name in table.get(tier, {}):
                candidates.append({"provider": name, "tier": tier, "model": table[tier][name]})
                break
    return {"floor": floor, "provider": provider, "effort": task.get("reasoning_effort"),
            "candidates": candidates, "catalog_digest": catalog_digest, "bound_at": at}


def _catalog_state(store: CatalogStore) -> tuple[dict, dict, list[str]]:
    catalog, warnings = merged_catalog(store)
    sources = {}
    for name in sorted(catalog["providers"]):
        record, origin, _notes = effective_record(store, name)
        sources[name] = {"origin": origin, "catalog_version": record["catalog_version"], "revision": record["revision"]}
    return catalog, sources, warnings


def build_matrix(store: CatalogStore, manifest: dict, previous: dict | None = None,
                 stale_after_days: int | None = None) -> tuple[dict, dict]:
    """Return (matrix, change) binding pending tasks (all tasks on first capture) to the current catalog."""
    now = _iso(store.now())
    catalog, sources, warnings = _catalog_state(store)
    catalog_digest = mc.digest(catalog)
    table = _tier_table(catalog)
    old_tasks = (previous or {}).get("tasks", {})
    tasks: dict[str, dict] = {}
    rebased, kept, unbound = [], [], []
    for task in manifest.get("tasks", []):
        task_id = task["id"]
        if task.get("status") == "pending":
            tasks[task_id] = _bind_task(task, table, catalog_digest, now)
            rebased.append(task_id)
        elif task_id in old_tasks:
            tasks[task_id] = copy.deepcopy(old_tasks[task_id])
            kept.append(task_id)
        else:
            unbound.append(task_id)
    if stale_after_days is None:
        stale_after_days = (previous or {}).get("stale_after_days", store.policy["capability"]["ttl_days"])
    matrix = {
        "matrix_version": MATRIX_VERSION, "plan_id": manifest.get("plan_id"),
        "created_at": (previous or {}).get("created_at", now), "captured_at": now,
        "freshness_policy_version": mc.FRESHNESS_POLICY_VERSION, "stale_after_days": stale_after_days,
        "catalog_version": catalog["catalog_version"], "catalog_digest": catalog_digest,
        "sources": sources, "warnings": warnings, "catalog": catalog, "tiers": table, "tasks": tasks,
        "audit": list((previous or {}).get("audit", [])),
    }
    change = {"rebased": rebased, "kept": kept, "unbound": unbound}
    return matrix, change


def _audit(matrix: dict, entry: dict) -> None:
    matrix["audit"] = [*matrix["audit"], entry][-AUDIT_LIMIT:]
    matrix["matrix_digest"] = _matrix_digest(matrix)


def render_matrix(matrix: dict) -> str:
    lines = [f"# MODEL_MATRIX — {matrix.get('plan_id')}", "",
             "Generated from MODEL_MATRIX.json (authoritative); do not edit by hand.", "",
             f"- Captured: {matrix['captured_at']} (stale after {matrix['stale_after_days']} days)",
             f"- Catalog: `{matrix['catalog_version']}`", f"- Catalog digest: `{matrix['catalog_digest']}`",
             f"- Matrix digest: `{matrix.get('matrix_digest', '')}`",
             f"- Freshness policy: `{matrix['freshness_policy_version']}`", "", "## Sources", "",
             "| Provider | Origin | Catalog version | Revision |", "|---|---|---|---:|"]
    for name, source in matrix["sources"].items():
        lines.append(f"| {name} | {source['origin']} | `{source['catalog_version']}` | {source['revision']} |")
    providers = sorted({p for row in matrix["tiers"].values() for p in row})
    lines += ["", "## Tier matrix", "", "| Tier | " + " | ".join(providers) + " |",
              "|---|" + "---|" * len(providers)]
    for tier in mc.TIER_ORDER:
        row = matrix["tiers"].get(tier, {})
        lines.append(f"| {tier} | " + " | ".join(f"`{row[p]}`" if p in row else "—" for p in providers) + " |")
    lines += ["", "## Task bindings", "", "| Task | Floor | Provider | Effort | Candidates | Bound to |", "|---|---|---|---|---|---|"]
    for task_id, binding in matrix["tasks"].items():
        cands = ", ".join(f"{c['provider']}:{c['model']} ({c['tier']})" for c in binding["candidates"]) or "none"
        lines.append(f"| {task_id} | {binding['floor']} | {binding['provider']} | {binding['effort']} | {cands} | `{binding['catalog_digest'][:12]}` |")
    lines += ["", "## Audit trail", ""]
    for entry in matrix["audit"]:
        old = (entry.get("old_digest") or "none")[:12]
        lines.append(f"- {entry['at']} `{entry['op']}` {old} -> {(entry.get('new_digest') or 'none')[:12]}"
                     + (f" task {entry['task']} {entry['old_floor']} -> {entry['new_floor']}: {entry['reason']}" if entry["op"] == "reclassify" else "")
                     + (f" rebased {', '.join(entry['rebased']) or 'none'}" if "rebased" in entry else ""))
    for warning in matrix["warnings"]:
        lines.append(f"- warning: {warning}")
    return "\n".join(lines) + "\n"


def _atomic_write(path: Path, payload: bytes) -> None:
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    tmp = Path(name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def write_matrix(plan_dir: Path, matrix: dict) -> None:
    """JSON first (authority), then the derived Markdown; a crash leaves the previous JSON intact."""
    plan_dir = Path(plan_dir)
    _atomic_write(plan_dir / MATRIX_JSON, (json.dumps(matrix, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8"))
    _atomic_write(plan_dir / MATRIX_MD, render_matrix(matrix).encode("utf-8"))


def load_matrix(plan_dir: Path) -> tuple[dict | None, str | None]:
    """Return (matrix, None), (None, None) when absent, or (None, warning) when invalid."""
    path = Path(plan_dir) / MATRIX_JSON
    try:
        matrix = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, None
    except (OSError, ValueError) as exc:
        return None, f"{MATRIX_JSON} unreadable ({exc.__class__.__name__})"
    if not isinstance(matrix, dict) or matrix.get("matrix_version") != MATRIX_VERSION:
        return None, f"{MATRIX_JSON} has an unsupported matrix_version"
    if matrix.get("matrix_digest") != _matrix_digest(matrix):
        return None, f"{MATRIX_JSON} digest mismatch; snapshot was modified outside model_catalogctl"
    try:
        if mc.digest(matrix["catalog"]) != matrix["catalog_digest"]:
            return None, f"{MATRIX_JSON} catalog digest mismatch"
    except (KeyError, mc.CatalogError) as exc:
        return None, f"{MATRIX_JSON} catalog invalid ({str(exc)[:120]})"
    return matrix, None


def create_plan_matrix(store: CatalogStore, plan_dir: Path, manifest: dict) -> dict:
    """Capture the snapshot at plan creation; refuses to overwrite an existing one."""
    if (Path(plan_dir) / MATRIX_JSON).exists():
        raise MatrixError(f"{MATRIX_JSON} already exists; use refresh --plan")
    matrix, change = build_matrix(store, manifest)
    _audit(matrix, {"at": matrix["captured_at"], "op": "create", "old_digest": None,
                    "new_digest": matrix["catalog_digest"], "rebased": change["rebased"]})
    write_matrix(plan_dir, matrix)
    return matrix


def _load_manifest(plan_dir: Path) -> tuple[Path, dict]:
    import planctl  # lazy: planctl imports this module for plan creation
    try:
        return planctl.load_plan(plan_dir)
    except planctl.PlanError as exc:
        raise MatrixError(str(exc)) from exc


def matrix_status(store: CatalogStore, plan_dir: Path) -> dict:
    """Snapshot age and facet freshness; staleness is a warning, never blocking."""
    plan_dir, _manifest = _load_manifest(plan_dir)
    matrix, warning = load_matrix(plan_dir)
    report: dict[str, Any] = {"plan": str(plan_dir), "snapshot": matrix is not None, "warnings": [], "blocking": False}
    if matrix is None:
        report["warnings"].append(warning or f"no {MATRIX_JSON}; plan stays valid, run refresh --plan to capture one")
        return report
    now = store.now()
    age_days = (now - mc._parse_time(matrix["captured_at"])).total_seconds() / 86400
    stale = age_days > matrix["stale_after_days"]
    freshness = mc.catalog_freshness(matrix["catalog"], now, store.policy)
    aged = sorted({f"{p}/{m}:{facet}" for p, models in freshness.items() for m, facets in models.items()
                   for facet, state in facets.items() if state in REFRESH_STATES})
    report.update(catalog_digest=matrix["catalog_digest"], matrix_digest=matrix["matrix_digest"],
                  captured_at=matrix["captured_at"], age_days=round(age_days, 2), stale=stale,
                  stale_after_days=matrix["stale_after_days"], stale_facets=aged,
                  tasks=sorted(matrix["tasks"]), audit_entries=len(matrix["audit"]))
    if stale:
        report["warnings"].append(f"{MATRIX_JSON} is {age_days:.1f} days old (threshold {matrix['stale_after_days']}); "
                                  "run diff/refresh --plan (non-blocking)")
    if aged:
        report["warnings"].append(f"snapshot has {len(aged)} stale/expired facets (non-blocking)")
    return report


def matrix_diff(store: CatalogStore, plan_dir: Path) -> dict:
    """Compare the plan snapshot with the current catalog without writing anything."""
    plan_dir, manifest = _load_manifest(plan_dir)
    old, warning = load_matrix(plan_dir)
    new, change = build_matrix(store, manifest, old)
    report: dict[str, Any] = {"plan": str(plan_dir), "old_digest": (old or {}).get("catalog_digest"),
                              "new_digest": new["catalog_digest"], "warnings": [w for w in [warning] if w]}
    report["changed"] = report["old_digest"] != report["new_digest"]
    old_models = {(p, m) for p, body in (old or {}).get("catalog", {}).get("providers", {}).items() for m in body["models"]}
    new_models = {(p, m) for p, body in new["catalog"]["providers"].items() for m in body["models"]}
    report["models_added"] = [f"{p}/{m}" for p, m in sorted(new_models - old_models)]
    report["models_removed"] = [f"{p}/{m}" for p, m in sorted(old_models - new_models)]
    old_tiers = (old or {}).get("tiers", {})
    report["tier_changes"] = {
        tier: {"old": old_tiers.get(tier, {}), "new": new["tiers"][tier]}
        for tier in mc.TIER_ORDER if old_tiers.get(tier, {}) != new["tiers"][tier]
    }
    old_tasks = (old or {}).get("tasks", {})
    report["would_rebase"] = [t for t in change["rebased"]
                              if old_tasks.get(t, {}).get("candidates") != new["tasks"][t]["candidates"]]
    report["kept"] = change["kept"]
    return report


def matrix_refresh(store: CatalogStore, plan_dir: Path, stale_after_days: int | None = None) -> dict:
    """Explicit re-snapshot: rebases pending tasks only, appends an old->new digest audit entry."""
    plan_dir, manifest = _load_manifest(plan_dir)
    old, warning = load_matrix(plan_dir)
    matrix, change = build_matrix(store, manifest, old, stale_after_days)
    old_digest = (old or {}).get("catalog_digest")
    _audit(matrix, {"at": matrix["captured_at"], "op": "refresh" if old else "create",
                    "old_digest": old_digest, "new_digest": matrix["catalog_digest"], **change})
    write_matrix(plan_dir, matrix)
    return {"plan": str(plan_dir), "old_digest": old_digest, "new_digest": matrix["catalog_digest"],
            "matrix_digest": matrix["matrix_digest"], **change,
            "warnings": [w for w in [warning] if w] + matrix["warnings"]}


def matrix_reclassify(store: CatalogStore, plan_dir: Path, task_id: str, tier: str, reason: str,
                    effort: str | None = None) -> dict:
    """Explicit, audited change of a task's semantic floor (and optionally effort)."""
    import planctl
    import routingctl
    if not reason or not reason.strip():
        raise MatrixError("reclassify requires a non-empty --reason")
    new_tier = routingctl.normalize_tier(tier)
    if new_tier not in mc.TIER_ORDER:
        raise MatrixError(f"unknown tier {tier!r}")
    if effort is not None and effort not in mc.EFFORT_ORDER:
        raise MatrixError(f"unknown effort {effort!r}")
    plan_dir, manifest = _load_manifest(plan_dir)
    try:
        task = planctl.find_task(manifest, planctl.normalize_task_id(task_id))
    except planctl.PlanError as exc:
        raise MatrixError(str(exc)) from exc
    if task["status"] not in RECLASSIFIABLE:
        raise MatrixError(f"task {task['id']} is {task['status']}; only {'/'.join(RECLASSIFIABLE)} tasks can be reclassified")
    old_tier, old_effort = task["model_tier"], task["reasoning_effort"]
    task["model_tier"] = new_tier
    if effort is not None:
        task["reasoning_effort"] = effort
    planctl.append_event(manifest, "task_reclassified", task_id=task["id"], old_floor=old_tier, new_floor=new_tier,
                         old_effort=old_effort, new_effort=task["reasoning_effort"], reason=reason.strip())
    planctl.save_manifest(plan_dir, manifest)
    matrix, warning = load_matrix(plan_dir)
    entry = {"at": _iso(store.now()), "op": "reclassify", "task": task["id"], "old_floor": old_tier,
             "new_floor": new_tier, "old_effort": old_effort, "new_effort": task["reasoning_effort"],
             "reason": reason.strip()}
    if matrix is not None:
        # Same catalog: the task is rebound to its new floor; no other binding moves.
        entry.update(old_digest=matrix["catalog_digest"], new_digest=matrix["catalog_digest"])
        matrix["tasks"][task["id"]] = _bind_task(task, matrix["tiers"], matrix["catalog_digest"], entry["at"])
        _audit(matrix, entry)
        write_matrix(plan_dir, matrix)
    return {"plan": str(plan_dir), **entry, "snapshot": matrix is not None,
            "warnings": [w for w in [warning] if w]}


def file_sources(path: Path) -> dict[str, Source]:
    """Sources backed by a JSON evidence file: {"models": {id: {tiers, capability, economics, quality}}}."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    models = data.get("models") if isinstance(data, dict) else None
    if not isinstance(models, dict):
        raise CacheError("evidence file must contain a 'models' object")
    sources: dict[str, Source] = {}
    if all(isinstance(m, dict) and "capability" in m for m in models.values()):
        sources["capability"] = lambda _p: {k: {"tiers": v.get("tiers"), "capability": v["capability"]} for k, v in models.items()}
    for facet in ("economics", "quality"):
        if any(isinstance(m, dict) and facet in m for m in models.values()):
            sources[facet] = lambda _p, f=facet: {k: v[f] for k, v in models.items() if isinstance(v, dict) and f in v}
    return sources


def probe_cli_version(provider: str) -> str | None:
    executable = shutil.which(provider)
    if not executable:
        return None
    try:
        done = subprocess.run([executable, "--version"], capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.SubprocessError):
        return None
    text = (done.stdout or "").strip().splitlines()
    return text[0][:80] if done.returncode == 0 and text else None


def _emit(value: Any, as_json: bool) -> None:
    if as_json:
        print(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False))
        return
    if isinstance(value, dict) and "providers" in value and "cache_root" in value:
        print(f"cache: {value['cache_root']}")
        for name, entry in value["providers"].items():
            facets = " ".join(f"{k}={v}" for k, v in entry.get("facets", {}).items())
            print(f"- {name}: {entry['origin']} {entry.get('catalog_version', '')} {facets}".rstrip())
        for warning in value["warnings"]:
            print(f"warning: {warning}")
        return
    print(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False))


def main(argv: list[str] | None = None) -> int:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--cache-dir", type=Path, default=None, help=f"cache root (default: user cache; env {ENV_CACHE_DIR})")
    common.add_argument("--json", action="store_true", help="machine-readable output")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("status", "show", "validate", "snapshot"):
        cmd = sub.add_parser(name, parents=[common])
        cmd.add_argument("--provider")
        if name == "snapshot":
            cmd.add_argument("--output", type=Path)
        if name == "status":
            cmd.add_argument("--plan", type=Path, help=f"report the plan's {MATRIX_JSON} instead of the cache")
    cmd = sub.add_parser("refresh", parents=[common])
    cmd.add_argument("--provider")
    cmd.add_argument("--from-file", type=Path, help="JSON evidence file used as the listing source")
    cmd.add_argument("--cli-version", help="skip probing and use this CLI version")
    cmd.add_argument("--force", action="store_true", help="refresh every facet")
    cmd.add_argument("--plan", type=Path, help=f"re-snapshot the plan's {MATRIX_JSON}, rebasing pending tasks only")
    cmd.add_argument("--stale-days", type=int, help="snapshot stale threshold in days (with --plan)")
    cmd = sub.add_parser("diff", parents=[common])
    cmd.add_argument("--plan", type=Path, required=True)
    cmd = sub.add_parser("reclassify", parents=[common])
    cmd.add_argument("--plan", type=Path, required=True)
    cmd.add_argument("--task", required=True)
    cmd.add_argument("--tier", required=True, help="new semantic floor (canonical tier or alias)")
    cmd.add_argument("--effort", help="new reasoning effort")
    cmd.add_argument("--reason", required=True)
    args = parser.parse_args(argv)
    if args.command == "refresh" and bool(args.plan) == bool(args.provider):
        parser.error("refresh requires exactly one of --provider or --plan")
    store = CatalogStore(args.cache_dir)
    try:
        if args.command == "status" and args.plan:
            report = matrix_status(store, args.plan)
            if args.json:
                _emit(report, True)
            else:
                print(f"plan: {report['plan']}")
                if report["snapshot"]:
                    print(f"snapshot: {report['catalog_digest']} captured {report['captured_at']} ({report['age_days']} days)")
                for warning in report["warnings"]:
                    print(f"warning: {warning}")
        elif args.command == "diff":
            _emit(matrix_diff(store, args.plan), True)
        elif args.command == "reclassify":
            _emit(matrix_reclassify(store, args.plan, args.task, args.tier, args.reason, args.effort), True)
        elif args.command == "refresh" and args.plan:
            _emit(matrix_refresh(store, args.plan, args.stale_days), True)
        elif args.command == "status":
            _emit(status(store, args.provider), args.json)
        elif args.command == "show":
            catalog, warnings = merged_catalog(store, args.provider)
            _emit({"catalog": catalog, "digest": mc.digest(catalog), "warnings": warnings}, True)
        elif args.command == "validate":
            report = validate_cache(store, args.provider)
            _emit(report, True)
            return 0 if report["valid"] else 1
        elif args.command == "snapshot":
            snap = snapshot(store, args.provider)
            if args.output:
                args.output.write_text(json.dumps(snap, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
                _emit({"output": str(args.output), "digest": snap["digest"]}, True)
            else:
                _emit(snap, True)
        else:
            sources = file_sources(args.from_file) if args.from_file else {}
            version_fn = (lambda _p: args.cli_version) if args.cli_version else probe_cli_version
            _emit(refresh(store, args.provider, sources, version_fn=version_fn, force=args.force), True)
    except (CacheError, mc.CatalogError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
