"""Build tranche: session memory API, resume compute identity (D-f3a8, D-e2b7)."""

from __future__ import annotations

import json

import numpy as np
import pytest
from fastapi.testclient import TestClient

from moonpark.api.app import app
from moonpark.providers import Site
from moonpark.resume_identity import compute_identity, identity_mismatch
from moonpark.search.deep import deep_search
from moonpark.session_memory import apply_overrides, check_session_pressure, reset_overrides

client = TestClient(app)


@pytest.fixture(autouse=True)
def _clear_session_overrides() -> None:
    reset_overrides()
    yield
    reset_overrides()


def test_identity_mismatch_reports_field() -> None:
    cur = compute_identity()
    bad = {**cur, "formula_version": "stale"}
    assert identity_mismatch(bad, cur) == "formula_version"


def test_deep_resume_rejects_stale_compute_identity() -> None:
    sites = [Site(lat_deg=-89.46, lon_deg=222.5)]
    starts = np.array(["2027-01-01T00:00:00"], dtype="datetime64[s]")
    cur_id = compute_identity()
    stale_id = {**cur_id, "engine_version": "0.0.0-stale"}
    fingerprint = {
        "mode": "total_coverage",
        "n_sites": 1,
        "n_window_starts": 1,
        "first_start": str(starts[0]),
        "window_hours": 24,
        "needs": {},
        "extra": {},
        "compute_identity": stale_id,
    }
    resume = {"version": 1, "fingerprint": fingerprint, "n_starts": 0, "rows": []}

    def evaluate(_s, _t, _h):
        return {"feasible": True, "score": 1.0, "companion_score": 1.0, "hazard_gap_star": False}

    with pytest.raises(ValueError, match="engine_version|motor or data"):
        deep_search(sites, starts, 24, {}, evaluate=evaluate, mode="total_coverage", resume=resume)


def test_session_memory_get_and_reset() -> None:
    snap = client.get("/session-memory")
    assert snap.status_code == 200
    base = snap.json()["pcp_cache_budget_mb"]
    r = client.post("/session-memory", json={"pcp_cache_mb": 900})
    assert r.status_code == 200
    assert r.json()["pcp_cache_budget_mb"] == 900
    r2 = client.post("/session-memory", json={"reset_automatic": True})
    assert r2.status_code == 200
    assert r2.json()["pcp_cache_budget_mb"] == base


def test_check_session_pressure_raises_after_eviction(monkeypatch) -> None:
    monkeypatch.setattr("moonpark.session_memory.session_budget_mb", lambda: 10)
    monkeypatch.setattr("moonpark.session_memory.process_rss_mb", lambda: 999.0)
    with pytest.raises(ValueError, match="session memory pressure"):
        check_session_pressure(evict_pcp=lambda: None)


def test_deep_search_response_includes_compute_identity() -> None:
    body = {
        "mock": True,
        "mode": "total_coverage",
        "lat_min": -89.5,
        "lat_max": -89.4,
        "lon_min": 222,
        "lon_max": 223,
        "start": "2027-01-01T00:00:00Z",
        "end": "2027-01-02T00:00:00Z",
        "window_hours": 24,
    }
    r = client.post("/deep-search", json=body)
    assert r.status_code == 200, r.text
    cid = r.json().get("compute_identity")
    assert isinstance(cid, dict)
    assert cid == compute_identity()