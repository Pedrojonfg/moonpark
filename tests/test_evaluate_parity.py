"""Shared evaluate path: planner payload vs evaluate_site_window (D-7c4e)."""

from __future__ import annotations

import numpy as np
import pytest

from moonpark.planner_payload import build_planner_payload, build_score_needs, evaluate_site_window, kernels_available, parse_time_window
from moonpark.score import score
from moonpark.site01 import SITE01

pytestmark = pytest.mark.skipif(not kernels_available(), reason="SPICE kernels not on disk")

NEEDS = {
    "max_night_h": 50,
    "max_no_earth_h": 20,
    "min_continuous_lit_h": 0,
    "min_total_lit_h": 0,
    "require_both": False,
    "template_id": None,
}


def test_build_planner_matches_evaluate_site_window() -> None:
    span = parse_time_window("2027-01-01T00:00:00Z", "2027-01-02T00:00:00Z", step_h=1)
    times = np.asarray(span, dtype="datetime64[s]")
    ev = evaluate_site_window(
        SITE01,
        times,
        needs=NEEDS,
        sun_lit_percent=0,
        earth_lit_percent=0,
        bridge_h=5,
        hazards_enabled=False,
        step_min=60,
    )
    assert ev is not None
    score_needs, _energy = build_score_needs(NEEDS, hazards_enabled=False)
    direct = score(ev["series"], ev.get("hazards") or {}, score_needs)

    payload = build_planner_payload(
        SITE01,
        times,
        needs=NEEDS,
        sun_lit_percent=0,
        earth_lit_percent=0,
        bridge_h=5,
        hazards_enabled=False,
        step_min=60,
    )
    got = payload["score"]
    assert got["feasible"] == direct["feasible"]
    assert got["score"] == pytest.approx(direct["score"], abs=1e-9)