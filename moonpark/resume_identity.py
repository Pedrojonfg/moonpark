"""Resume compute identity (D-20261122-pj-e2b7)."""

from __future__ import annotations

from moonpark.horizon.mask import SCHEDULE_VERSION
from moonpark.planner_payload import cached_cap_version, cached_data_version, engine_version
from moonpark.score import FORMULA


def compute_identity() -> dict[str, str | None]:
    return {
        "data_version": cached_data_version(),
        "cap_version": cached_cap_version(),
        "schedule_version": SCHEDULE_VERSION,
        "engine_version": engine_version(),
        "formula_version": FORMULA,
    }


def identity_mismatch(stored: dict | None, current: dict | None) -> str | None:
    if not stored or not current:
        return "missing compute_identity"
    for key in ("data_version", "cap_version", "schedule_version", "engine_version", "formula_version"):
        if stored.get(key) != current.get(key):
            return key
    return None