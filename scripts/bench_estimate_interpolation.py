#!/usr/bin/env python3
"""Estimate-layer interpolator benchmark (three methods vs real total_coverage truth).

# per D-20261122-pj-b4ca (benchmark), D-20261116-pj-1df2 (current four-quadrant 1/d^2 estimate)

Truth: real ``total_coverage`` scores on the 1 km cap cells in a square around Site01
(production cap masks + SPICE ephemeris + ``moonpark.score``; hazards off). One truth row
per cell, collapsed over windows with the same rule the map uses (``region_map._dedupe_rows``).

Methods (all share the D-1df2 reach, the 0.05*spacing softening and the 0.5 feasibility cut):
  1. quadrant_idw         nearest known cell per quadrant, weights 1/(d^2+soft)  (production)
  2. eight_neighbour_idw  the 8 nearest known cells, weights 1/(d^2+soft)
  3. gaussian             all known cells within reach, weights exp(-d^2 / 2 sigma^2),
                          sigma = median nearest-neighbour spacing of the known cells

Protocols: leave-one-out, stride-2 lattice (4 phases), random 50 % known (seeded trials).
This script reports numbers only: it never picks a winner and never touches the product
default (D-b4ca). The production estimate lives in ``web/map.js`` (``estimateAt``); the
quadrant method here is a line-by-line Python port of it.

Usage:
    python scripts/bench_estimate_interpolation.py [--json-out PATH] [--csv-out PATH]
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
from pathlib import Path
from typing import Any, Callable

import numpy as np

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

DECISION = "D-20261122-pj-b4ca"
CELL_M = 1000.0  # cap grid step; CELL in web/map.js
SPACING_MIN_M = 0.2 * CELL_M  # estimateSpacing clamp in web/map.js
SPACING_MAX_M = 60.0 * CELL_M
REACH_MIN_M = 3.0 * CELL_M  # D-1df2: reach = 3 x median spacing, floor 3 km, cap 60 km
REACH_MAX_M = 60.0 * CELL_M
SOFT_FRAC = 0.05  # soft = (0.05 * spacing)^2 in estimateAt
FEASIBLE_CUT = 0.5  # D-1df2
METHODS = ("quadrant_idw", "eight_neighbour_idw", "gaussian")

Cell = dict[str, Any]  # x_m, y_m, feasible, score (+ companion_score, lat_deg, lon_deg)


# ---------------------------------------------------------------- weight formulas (pure)


def idw_weight(d_m: float, spacing_m: float) -> float:
    """1/(d^2 + soft), soft = (0.05 spacing)^2 (as in web/map.js estimateAt)."""
    return 1.0 / (d_m * d_m + (SOFT_FRAC * spacing_m) ** 2)


def gaussian_weight(d_m: float, sigma_m: float) -> float:
    """exp(-d^2 / (2 sigma^2))."""
    return math.exp(-(d_m * d_m) / (2.0 * sigma_m * sigma_m))


def median_spacing_m(cells: list[Cell]) -> float:
    """Median nearest-neighbour distance of known cells, clamped like web/map.js estimateSpacing."""
    if len(cells) < 2:
        return CELL_M
    xy = np.array([[c["x_m"], c["y_m"]] for c in cells])
    d = np.hypot(xy[:, None, 0] - xy[None, :, 0], xy[:, None, 1] - xy[None, :, 1])
    np.fill_diagonal(d, np.inf)
    nn = np.sort(d.min(axis=1))
    nn = nn[np.isfinite(nn) & (nn > 1e-9)]
    if not nn.size:
        return CELL_M
    return float(min(max(nn[len(nn) // 2], SPACING_MIN_M), SPACING_MAX_M))


def reach_m(spacing_m: float) -> float:
    return min(REACH_MAX_M, max(REACH_MIN_M, 3.0 * spacing_m))


def _combine(picks: list[tuple[Cell, float]]) -> dict[str, Any]:
    """Shared feasibility rule: same weights, feasible when feasible weight share >= 0.5 (D-1df2)."""
    w = sum(wq for _, wq in picks)
    wf = sum(wq for c, wq in picks if c["feasible"])
    sc = sum(wq * float(c["score"]) for c, wq in picks if c["feasible"])
    p_feas = wf / w
    return {
        "feasible": p_feas >= FEASIBLE_CUT,
        "p_feasible": p_feas,
        "score": sc / wf if wf > 0 else 0.0,
        "n_used": len(picks),
    }


def _tie_key(t: tuple[Cell, float, float, float]) -> tuple[float, float, float]:
    """Order by distance (mm resolution), then x, then y: deterministic tie-break."""
    c, _dx, _dy, d = t
    return (round(d, 3), c["x_m"], c["y_m"])


def predict(method: str, known: list[Cell], x_m: float, y_m: float, spacing_m: float) -> dict[str, Any] | None:
    """Estimate at (x, y) from ``known``; None when no known cell is within reach."""
    reach = reach_m(spacing_m)
    within: list[tuple[Cell, float, float, float]] = []  # cell, dx, dy, d
    for c in known:
        dx, dy = c["x_m"] - x_m, c["y_m"] - y_m
        d = math.hypot(dx, dy)
        if d <= reach:
            within.append((c, dx, dy, d))
    if not within:
        return None
    if method == "quadrant_idw":
        best: dict[int, tuple[Cell, float]] = {}
        # Equal-distance ties are common on the regular 1 km grid; web/map.js keeps whichever it saw
        # first (hash order). Here ties break by (x, y) so results do not depend on list order.
        for c, dx, dy, d in sorted(within, key=_tie_key):
            q = (1 if dx >= 0 else 0) + (2 if dy >= 0 else 0)  # same quadrant coding as map.js
            if q not in best or d < best[q][1] - 1e-3:
                best[q] = (c, d)
        picks = [(c, idw_weight(d, spacing_m)) for c, d in best.values()]
    elif method == "eight_neighbour_idw":
        near = sorted(within, key=_tie_key)[:8]
        picks = [(c, idw_weight(d, spacing_m)) for c, _dx, _dy, d in near]
    elif method == "gaussian":
        picks = [(c, gaussian_weight(d, spacing_m)) for c, _dx, _dy, d in within]
    else:
        raise ValueError(f"unknown method {method!r}")
    out = _combine(picks)
    out["d_min_m"] = min(t[3] for t in within)
    return out


# ---------------------------------------------------------------- truth (real total_coverage)


def build_truth(
    half_m: float, template_id: str, start: str, n_starts: int, window_hours: int
) -> tuple[dict[str, list[Cell]], dict]:
    """Run real total_coverage on cap cells in a square around Site01.

    Returns rows grouped by window start (hourly starts, ``n_starts`` of them) plus run metadata.
    """
    from moonpark.ephemeris import SpiceEphemeris
    from moonpark.horizon import polar_stereo_xy
    from moonpark.horizon.cap_index import cap_index_available, mask_from_cap_tile, sites_in_xy_rect
    from moonpark.planner_payload import build_score_needs, kernels_available
    from moonpark.planner_templates import TEMPLATES
    from moonpark.region_map import _dedupe_rows, _normalize_row
    from moonpark.search.deep import deep_search
    from moonpark.site01 import SITE01
    from moonpark.visibility import series as vis_series

    if not kernels_available() or not cap_index_available():
        raise RuntimeError("SPICE kernels or cap_1km index missing: cannot build real truth")

    sx, sy = polar_stereo_xy(SITE01.lat_deg, SITE01.lon_deg)
    cells = sites_in_xy_rect(sx - half_m, sx + half_m, sy - half_m, sy + half_m)
    if len(cells) < 5:
        raise RuntimeError(f"only {len(cells)} cap cells in the region")

    tmpl = TEMPLATES[template_id]
    needs = {k: tmpl[k] for k in ("max_night_h", "max_no_earth_h", "require_both", "min_continuous_lit_h")}
    score_needs, _energy = build_score_needs(needs, False)
    sun_thr = float(tmpl["sun_lit_percent"]) / 100.0
    earth_thr = float(tmpl["earth_lit_percent"]) / 100.0
    bridge = int(tmpl["bridge_h"])

    t0 = np.datetime64(start)
    span = t0 + np.arange(n_starts + window_hours + 1, dtype="timedelta64[h]")
    starts = span[:n_starts]
    sites = [c[0] for c in cells]
    site_xy = [(c[1], c[2]) for c in cells]
    index_of = {(s.lat_deg, s.lon_deg): i for i, s in enumerate(sites)}
    eph = SpiceEphemeris()
    sky_by: dict[int, list] = {}

    def evaluate(candidate, start_t, hours: int) -> dict:
        idx = index_of[(candidate.lat_deg, candidate.lon_deg)]
        _s, _x, _y, tx, ty, row = cells[idx]
        horizon = mask_from_cap_tile(tx, ty, row)
        if idx not in sky_by:
            sky_by[idx] = eph.sky(candidate, span)
        i0 = int((np.datetime64(start_t, "s") - span[0]) / np.timedelta64(1, "h"))
        sky_win = sky_by[idx][i0 : i0 + int(hours) + 1]
        vis = vis_series(sky_win, horizon, sun_threshold=sun_thr, earth_threshold=earth_thr, bridge_h=bridge)
        return {"series": vis, "hazards": {}, "hazard_gap_star": False}

    t_run = time.perf_counter()
    res = deep_search(
        sites, starts, window_hours, score_needs, evaluate=evaluate, mode="total_coverage", site_xy=site_xy
    )
    wall = time.perf_counter() - t_run

    xy_by = {(s.lat_deg, s.lon_deg): (x, y) for s, x, y, *_ in cells}
    flat = [
        _normalize_row(
            {
                "lat_deg": r["site"]["lat_deg"],
                "lon_deg": r["site"]["lon_deg"],
                "feasible": r["feasible"],
                "score": r["score"],
                "companion_score": r["companion_score"],
                "window_start": str(r["window_start"]),
            }
        )
        for r in res["export_rows"]
    ]
    by_window: dict[str, list[Cell]] = {}
    for r in flat:
        x, y = xy_by[(r["lat_deg"], r["lon_deg"])]
        by_window.setdefault(r["window_start"], []).append(
            {**r, "x_m": x - sx, "y_m": y - sy, "feasible": bool(r["feasible"]), "score": float(r["score"])}
        )
    meta = {
        "template": template_id,
        "needs": score_needs,
        "sun_lit_percent": tmpl["sun_lit_percent"],
        "earth_lit_percent": tmpl["earth_lit_percent"],
        "bridge_h": bridge,
        "start": start,
        "n_starts": n_starts,
        "window_hours": window_hours,
        "half_m": half_m,
        "n_cells": len(cells),
        "n_window_starts": int(starts.size),
        "rows_evaluated": res["rows_evaluated"],
        "dropped_cells": res["dropped_cells"],
        "total_coverage_wall_s": wall,
        "mask_source": "cap_1km tile masks (mask_from_cap_tile)",
        "hazards": "off",
        "site01_xy_m": [sx, sy],
    }
    return by_window, meta


def collapse_best_window(by_window: dict[str, list[Cell]]) -> list[Cell]:
    """One row per cell, best window, using the map's own collapse (feasible first, then best score)."""
    from moonpark.region_map import _dedupe_rows

    flat = [r for rows in by_window.values() for r in rows]
    keep = _dedupe_rows(flat)
    return [dict(r) for r in keep]


def pick_mixed_window(by_window: dict[str, list[Cell]]) -> tuple[str, float]:
    """Window whose feasible fraction is closest to 0.5 (earliest on ties): a stress test for colour mismatch."""
    best_w, best_gap, best_f = "", 9.0, 0.0
    for w, rows in by_window.items():
        f = sum(1 for r in rows if r["feasible"]) / len(rows)
        if abs(f - 0.5) < best_gap - 1e-12:
            best_w, best_gap, best_f = w, abs(f - 0.5), f
    return best_w, best_f


# ---------------------------------------------------------------- protocols and metrics


def _grid_index(truth: list[Cell]) -> list[tuple[int, int]]:
    x0 = min(c["x_m"] for c in truth)
    y0 = min(c["y_m"] for c in truth)
    return [(round((c["x_m"] - x0) / CELL_M), round((c["y_m"] - y0) / CELL_M)) for c in truth]


def protocol_splits(truth: list[Cell], n_random: int, seed: int) -> list[tuple[str, str, list[int], list[int]]]:
    """(protocol, trial_id, known_idx, held_idx) tuples."""
    n = len(truth)
    gi = _grid_index(truth)
    out: list[tuple[str, str, list[int], list[int]]] = []
    for i in range(n):
        out.append(("leave_one_out", str(i), [j for j in range(n) if j != i], [i]))
    for ox in (0, 1):
        for oy in (0, 1):
            known = [i for i in range(n) if gi[i][0] % 2 == ox and gi[i][1] % 2 == oy]
            held = [i for i in range(n) if i not in set(known)]
            if len(known) >= 2 and held:
                out.append(("stride2_lattice", f"phase{ox}{oy}", known, held))
    rng = np.random.default_rng(seed)
    for t in range(n_random):
        k = max(2, n // 2)
        known = sorted(int(i) for i in rng.choice(n, size=k, replace=False))
        held = [i for i in range(n) if i not in set(known)]
        out.append(("random_half", str(t), known, held))
    return out


def run_protocols(truth: list[Cell], n_random: int, seed: int, region_id: str) -> tuple[list[dict], list[dict]]:
    """Per-prediction records and per-(protocol, method) metrics."""
    records: list[dict] = []
    for proto, trial, known_i, held_i in protocol_splits(truth, n_random, seed):
        known = [truth[i] for i in known_i]
        spacing = median_spacing_m(known)
        for i in held_i:
            t = truth[i]
            for m in METHODS:
                p = predict(m, known, t["x_m"], t["y_m"], spacing)
                rec = {
                    "region": region_id,
                    "protocol": proto,
                    "trial": trial,
                    "method": m,
                    "x_m": round(t["x_m"], 3),
                    "y_m": round(t["y_m"], 3),
                    "n_known": len(known),
                    "spacing_m": round(spacing, 3),
                    "truth_feasible": t["feasible"],
                    "truth_score": t["score"],
                    "predicted": p is not None,
                    "pred_feasible": None if p is None else p["feasible"],
                    "pred_score": None if p is None else p["score"],
                    "score_error": None if p is None else p["score"] - t["score"],
                    "feasible_mismatch": None if p is None else (p["feasible"] != t["feasible"]),
                }
                records.append(rec)
    metrics = []
    for proto in dict.fromkeys(r["protocol"] for r in records):
        for m in METHODS:
            rows = [r for r in records if r["protocol"] == proto and r["method"] == m]
            metrics.append({"region": region_id, "protocol": proto, "method": m, **summarize(rows)})
    return records, metrics


def _stats(errs: list[float]) -> dict[str, Any]:
    if not errs:
        return {"n": 0, "max_abs": None, "rmse": None}
    a = np.asarray(errs, dtype=float)
    return {"n": int(a.size), "max_abs": float(np.max(np.abs(a))), "rmse": float(math.sqrt(np.mean(a * a)))}


def summarize(rows: list[dict]) -> dict[str, Any]:
    """Metrics over prediction records of one (protocol, method)."""
    pred = [r for r in rows if r["predicted"]]
    both = [r["score_error"] for r in pred if r["truth_feasible"] and r["pred_feasible"]]
    all_cells = [r["score_error"] for r in pred]  # infeasible cells carry score 0 (moonpark.score)
    mism = [r for r in pred if r["feasible_mismatch"]]
    return {
        "n_held": len(rows),
        "n_predicted": len(pred),
        "n_unpredicted_beyond_reach": len(rows) - len(pred),
        "score_error_both_feasible": _stats(both),
        "score_error_all_cells_infeasible_zero": _stats(all_cells),
        "feasible_mismatch_count": len(mism),
        "feasible_mismatch_rate": (len(mism) / len(pred)) if pred else None,
        "truth_feasible_fraction": (sum(1 for r in pred if r["truth_feasible"]) / len(pred)) if pred else None,
    }


# ---------------------------------------------------------------- output


def _fmt(v: Any, nd: int = 4) -> str:
    return "n/a" if v is None else f"{v:.{nd}f}"


def print_table(metrics: list[dict]) -> None:
    for region in dict.fromkeys(m["region"] for m in metrics):
        print(f"\n== region {region} ==")
        for proto in dict.fromkeys(m["protocol"] for m in metrics if m["region"] == region):
            print(f"-- {proto}")
            print(f"{'method':22s} {'n':>6s} {'max|e| both':>12s} {'RMSE both':>10s} {'max|e| all':>11s} "
                  f"{'RMSE all':>9s} {'mismatch':>9s}")
            for m in metrics:
                if m["region"] != region or m["protocol"] != proto:
                    continue
                b, a = m["score_error_both_feasible"], m["score_error_all_cells_infeasible_zero"]
                print(f"{m['method']:22s} {m['n_predicted']:6d} {_fmt(b['max_abs']):>12s} {_fmt(b['rmse']):>10s} "
                      f"{_fmt(a['max_abs']):>11s} {_fmt(a['rmse']):>9s} {_fmt(m['feasible_mismatch_rate']):>9s}")


def write_csv(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cols = list(records[0].keys()) if records else []
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(records)


def main() -> int:
    ap = argparse.ArgumentParser(description=f"Estimate interpolator benchmark ({DECISION}).")
    ap.add_argument("--json-out", type=Path, default=REPO / "logs" / "bench_estimate_interpolation.json")
    ap.add_argument("--csv-out", type=Path, default=REPO / "logs" / "bench_estimate_interpolation_cells.csv")
    ap.add_argument("--start", default="2027-01-01T00:00:00")
    ap.add_argument("--window-hours", type=int, default=24)
    ap.add_argument("--map-days", type=int, default=7, help="days of hourly window starts for the best-window truth")
    ap.add_argument("--scan-days", type=int, default=31, help="days scanned to pick the mixed-feasibility window")
    ap.add_argument("--primary-half-km", type=float, default=1.5, help="3 km square per D-b4ca")
    ap.add_argument("--supplement-half-km", type=float, default=4.5,
                    help="larger context square (9x9 km); 0 disables. Beyond the D-b4ca contract.")
    ap.add_argument("--random-trials", type=int, default=200)
    ap.add_argument("--seed", type=int, default=20261122)
    args = ap.parse_args()

    wall0 = time.perf_counter()
    regions = [("primary_3km", args.primary_half_km)]
    if args.supplement_half_km > 0:
        regions.append(("supplement_9km", args.supplement_half_km))
    wh = args.window_hours

    report: dict[str, Any] = {
        "decision": DECISION,
        "refs": ["D-20261116-pj-1df2"],
        "production_default_changed": False,
        "methods": {
            "quadrant_idw": "nearest known cell per quadrant, 1/(d^2+soft); port of web/map.js estimateAt (D-1df2)",
            "eight_neighbour_idw": "8 nearest known cells within reach, 1/(d^2+soft)",
            "gaussian": "all known cells within reach, exp(-d^2/2sigma^2), sigma = median NN spacing of known cells",
        },
        "shared": {
            "reach": "clamp(3*median spacing, 3 km, 60 km)",
            "soft": "(0.05*spacing)^2",
            "feasible_cut": FEASIBLE_CUT,
            "score_rule": "feasible-weighted mean of feasible neighbours; infeasible estimate scores 0",
            "tie_break": "equal distances (1 mm) break by (x, y); web/map.js tie order is hash-dependent",
        },
        "protocol_seed": args.seed,
        "random_trials": args.random_trials,
        "truth_configs": {},
        "regions": {},
        "metrics": [],
    }

    # Truth config 1: what the map shows (per-cell best window); template clps_average.
    # Truth config 2: one fixed window of the dte_relay_priority template picked for mixed feasibility,
    # because config 1 is feasible everywhere here and cannot exercise the colour-mismatch metric.
    t_scan = time.perf_counter()
    scan, _ = build_truth(regions[0][1] * 1000.0, "dte_relay_priority", args.start, args.scan_days * 24, wh)
    mixed_start, mixed_frac = pick_mixed_window(scan)
    print(f"mixed window picked on {regions[0][0]}: start={mixed_start} feasible_fraction={mixed_frac:.3f} "
          f"(scan {time.perf_counter() - t_scan:.1f}s)", flush=True)
    configs = [
        ("map_best_window", "clps_average", args.start, args.map_days * 24, None),
        ("fixed_window_mixed", "dte_relay_priority", mixed_start, 1, mixed_start),
    ]
    report["truth_configs"] = {
        "map_best_window": "clps_average, per-cell best window over hourly starts (map semantics, region_map._dedupe_rows)",
        "fixed_window_mixed": "dte_relay_priority, single window; start picked by feasible fraction closest to 0.5 "
        f"on the primary region over a {args.scan_days} d scan: {mixed_start}",
    }

    all_records: list[dict] = []
    for cfg_id, template, start, n_starts, fixed in configs:
        for region_id, half_km in regions:
            rid = f"{cfg_id}/{region_id}"
            print(f"[{rid}] total_coverage truth ({template}), half side {half_km} km ...", flush=True)
            by_window, meta = build_truth(half_km * 1000.0, template, start, n_starts, wh)
            truth = collapse_best_window(by_window) if fixed is None else by_window[fixed]
            n_feas = sum(1 for c in truth if c["feasible"])
            meta["n_truth_cells"] = len(truth)
            meta["truth_feasible_cells"] = n_feas
            meta["truth_window"] = fixed or "best over windows"
            meta["truth_scores"] = [
                {"x_m": round(c["x_m"], 1), "y_m": round(c["y_m"], 1), "feasible": c["feasible"],
                 "score": c["score"], "companion_score": c["companion_score"]}
                for c in sorted(truth, key=lambda c: (c["y_m"], c["x_m"]))
            ]
            print(f"  cells={len(truth)} feasible={n_feas} total_coverage wall={meta['total_coverage_wall_s']:.1f}s",
                  flush=True)
            report["regions"][rid] = meta
            records, metrics = run_protocols(truth, args.random_trials, args.seed, rid)
            report["metrics"].extend(metrics)
            all_records.extend(records)

    report["wall_s"] = time.perf_counter() - wall0
    report["csv"] = str(args.csv_out)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    write_csv(args.csv_out, all_records)
    print_table(report["metrics"])
    print(f"\nJSON: {args.json_out}\nCSV:  {args.csv_out}\nwall: {report['wall_s']:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
