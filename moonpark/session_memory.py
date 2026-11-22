"""Process session memory budgets and PCP cache policy (D-20261122-pj-f3a8)."""

from __future__ import annotations

import os
import resource
from dataclasses import dataclass, field
from typing import Any

# Defaults per D-f3a8 Values table
PCP_RAM_FRACTION_DEFAULT = 0.20
SESSION_RAM_FRACTION_DEFAULT = 0.50
PCP_CACHE_MIN_MB = 256
PCP_CACHE_MAX_MB = 8192
SESSION_BUDGET_MIN_MB = 2048
SESSION_BUDGET_MAX_MB = 24576

_overrides: dict[str, Any] = {}


def _clamp_mb(value: float, lo: int, hi: int) -> int:
    return int(max(lo, min(hi, round(value))))


def installed_ram_mb() -> int:
    """Physical RAM; env fallback when unknown."""
    try:
        with open("/proc/meminfo", encoding="ascii") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    kb = int(line.split()[1])
                    return max(1, kb // 1024)
    except OSError:
        pass
    return SESSION_BUDGET_MIN_MB


def _fraction(key: str, default: float) -> float:
    v = _overrides.get(key)
    if v is not None:
        return float(v)
    return default


def pcp_cache_budget_mb() -> int:
    env = os.environ.get("MOONPARK_PCP_CACHE_MB")
    if env:
        return _clamp_mb(float(env), PCP_CACHE_MIN_MB, PCP_CACHE_MAX_MB)
    explicit = _overrides.get("pcp_cache_mb")
    if explicit is not None:
        return _clamp_mb(float(explicit), PCP_CACHE_MIN_MB, PCP_CACHE_MAX_MB)
    frac = _fraction("pcp_ram_fraction", PCP_RAM_FRACTION_DEFAULT)
    return _clamp_mb(installed_ram_mb() * frac, PCP_CACHE_MIN_MB, PCP_CACHE_MAX_MB)


def session_budget_mb() -> int:
    env = os.environ.get("MOONPARK_SESSION_BUDGET_MB")
    if env:
        return _clamp_mb(float(env), SESSION_BUDGET_MIN_MB, SESSION_BUDGET_MAX_MB)
    explicit = _overrides.get("session_budget_mb")
    if explicit is not None:
        return _clamp_mb(float(explicit), SESSION_BUDGET_MIN_MB, SESSION_BUDGET_MAX_MB)
    frac = _fraction("session_ram_fraction", SESSION_RAM_FRACTION_DEFAULT)
    return _clamp_mb(installed_ram_mb() * frac, SESSION_BUDGET_MIN_MB, SESSION_BUDGET_MAX_MB)


def pcp_xy_high_precision() -> bool:
    if "pcp_xy_high_precision" in _overrides:
        return bool(_overrides["pcp_xy_high_precision"])
    return os.environ.get("MOONPARK_PCP_FLOAT64", "").lower() in ("1", "true", "yes")


def apply_overrides(**kwargs: Any) -> None:
    allowed = {
        "pcp_ram_fraction",
        "session_ram_fraction",
        "pcp_cache_mb",
        "session_budget_mb",
        "pcp_xy_high_precision",
    }
    for k, v in kwargs.items():
        if k in allowed and v is not None:
            _overrides[k] = v


def reset_overrides() -> None:
    _overrides.clear()


def config_snapshot() -> dict[str, Any]:
    return {
        "installed_ram_mb": installed_ram_mb(),
        "pcp_cache_budget_mb": pcp_cache_budget_mb(),
        "session_budget_mb": session_budget_mb(),
        "pcp_ram_fraction_default": PCP_RAM_FRACTION_DEFAULT,
        "session_ram_fraction_default": SESSION_RAM_FRACTION_DEFAULT,
        "pcp_xy_high_precision": pcp_xy_high_precision(),
        "overrides": dict(_overrides),
    }


def process_rss_mb() -> float:
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # Linux: kB; macOS: bytes (engine targets desktop bundle; Linux CI is the common case).
    if rss > 10_000_000:
        return rss / (1024 * 1024)
    return rss / 1024


def check_session_pressure(*, evict_pcp) -> None:
    """Raise ValueError(session_memory_pressure) when over budget after eviction."""
    budget = session_budget_mb()
    if process_rss_mb() <= budget:
        return
    evict_pcp()
    if process_rss_mb() <= budget:
        return
    raise ValueError(
        f"session memory pressure: RSS ~{process_rss_mb():.0f} MB exceeds budget {budget} MB"
    )