"""Unit checks of the three estimate weight formulas. # per D-20261122-pj-b4ca"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import bench_estimate_interpolation as bench  # noqa: E402


def _cell(x: float, y: float, score: float, feasible: bool = True) -> dict:
    return {"x_m": x, "y_m": y, "score": score, "feasible": feasible}


def test_weight_formulas():
    assert bench.idw_weight(1000.0, 1000.0) == 1.0 / (1000.0**2 + 50.0**2)
    assert bench.gaussian_weight(0.0, 1000.0) == 1.0
    assert math.isclose(bench.gaussian_weight(1000.0, 1000.0), math.exp(-0.5))


def test_quadrant_uses_nearest_per_quadrant_only():
    known = [_cell(1000, 0, 1.0), _cell(2000, 0, 9.0), _cell(-1000, 0, 0.0), _cell(0, -1000, 0.0), _cell(0, 1500, 0.0), _cell(-1000, -1000, 0.0)]
    p = bench.predict("quadrant_idw", known, 0.0, 0.0, 1000.0)
    assert p is not None and p["n_used"] == 4  # 2000 m and 1500 m cells share a quadrant with a nearer one
    p8 = bench.predict("eight_neighbour_idw", known, 0.0, 0.0, 1000.0)
    assert p8["n_used"] == 6  # fewer than 8 known cells: all within reach


def test_beyond_reach_is_none():
    assert bench.predict("gaussian", [_cell(50_000, 0, 1.0)], 0.0, 0.0, 1000.0) is None


def test_feasibility_cut():
    known = [_cell(1000, 0, 1.0), _cell(-1000, 0, 0.0, feasible=False)]
    p = bench.predict("quadrant_idw", known, 0.0, 0.0, 1000.0)
    assert p["p_feasible"] == 0.5 and p["feasible"] is True
    assert p["score"] == 1.0  # infeasible neighbours do not enter the score mean
