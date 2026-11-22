"""Benchmark remaining ``sites_in_latlon_rect`` cribas (precision + wall time).

# per D-20261122-pj-c1ed

Inventory measured against production ``moonpark/horizon/cap_index.py``:
center-based ``lat_mask`` (lat_pad=0.05), ``lon_mask`` (lon_pad=2.0 on non-wrap rects),
and ``_footprint_intersects_latlon_rect`` membership on candidates.

Usage:
    python scripts/bench_selector_cribas.py [--json-out PATH] [--reps N]
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from moonpark.horizon.cap_index import (  # noqa: E402
    _footprint_intersects_latlon_rect,
    _load_index,
    cap_index_available,
    sites_in_latlon_rect,
)
LAT_PAD = 0.05
LON_PAD = 2.0

# Default rectangle suite (includes independent-auditor wedge).
DEFAULT_RECTS: list[dict[str, float | str]] = [
    {
        "id": "auditor-lon100",
        "lat_min": -85.6,
        "lat_max": -84.4,
        "lon_min": 100.0,
        "lon_max": 101.0,
    },
    {
        "id": "deep-rect",
        "lat_min": -89.52,
        "lat_max": -89.40,
        "lon_min": 222.0,
        "lon_max": 223.0,
    },
    {
        "id": "polar-wedge",
        "lat_min": -90.0,
        "lat_max": -85.0,
        "lon_min": 200.0,
        "lon_max": 250.0,
    },
    {
        "id": "near-pole-sliver",
        "lat_min": -89.95,
        "lat_max": -89.85,
        "lon_min": 0.0,
        "lon_max": 30.0,
    },
    {
        "id": "mid-cap-box",
        "lat_min": -87.5,
        "lat_max": -87.0,
        "lon_min": 180.0,
        "lon_max": 210.0,
    },
    {
        "id": "lon-wrap-narrow",
        "lat_min": -88.0,
        "lat_max": -87.5,
        "lon_min": 359.0,
        "lon_max": 1.0,
    },
]


def _sorted_rect(
    lat_min: float, lat_max: float, lon_min: float, lon_max: float
) -> tuple[float, float, float, float]:
    lo_lat, hi_lat = sorted((float(lat_min), float(lat_max)))
    lo_lon, hi_lon = sorted((float(lon_min), float(lon_max)))
    width = hi_lon - lo_lon
    return lo_lat, hi_lat, lo_lon, width


def _production_masks(
    lat: np.ndarray,
    lon: np.ndarray,
    lo_lat: float,
    hi_lat: float,
    lo_lon: float,
    width: float,
) -> tuple[np.ndarray, np.ndarray]:
    lat_mask = (lat >= lo_lat - LAT_PAD) & (lat <= hi_lat + LAT_PAD)
    if width >= 360.0:
        lon_mask = np.ones_like(lat, dtype=bool)
    else:
        lon_mask = (lon - lo_lon) % 360.0 <= (width + LON_PAD)
    return lat_mask, lon_mask


def _cell_key(lat_v: float, lon_v: float) -> tuple[float, float]:
    return (round(float(lat_v), 6), round(float(lon_v), 6))


def _keys_from_indices(lat: np.ndarray, lon: np.ndarray, indices: np.ndarray) -> set[tuple[float, float]]:
    return {_cell_key(lat[i], lon[i]) for i in indices}


def _keys_from_sites(cells: list) -> set[tuple[float, float]]:
    return {_cell_key(c[0].lat_deg, c[0].lon_deg) for c in cells}


def _oracle_indices(
    lat: np.ndarray,
    lon: np.ndarray,
    lo_lat: float,
    hi_lat: float,
    lo_lon: float,
    width: float,
) -> np.ndarray:
    hits: list[int] = []
    for i in range(len(lat)):
        if _footprint_intersects_latlon_rect(
            float(lat[i]), float(lon[i]), lo_lat, hi_lat, lo_lon, width
        ):
            hits.append(i)
    return np.asarray(hits, dtype=np.int64)


def _both_masks_then_intersect(
    lat: np.ndarray,
    lon: np.ndarray,
    lat_mask: np.ndarray,
    lon_mask: np.ndarray,
    lo_lat: float,
    hi_lat: float,
    lo_lon: float,
    width: float,
) -> np.ndarray:
    cand = np.flatnonzero(lat_mask & lon_mask)
    hits: list[int] = []
    for i in cand:
        if _footprint_intersects_latlon_rect(
            float(lat[i]), float(lon[i]), lo_lat, hi_lat, lo_lon, width
        ):
            hits.append(int(i))
    return np.asarray(hits, dtype=np.int64)


def _omission_report(
    lat: np.ndarray,
    lon: np.ndarray,
    oracle_keys: set[tuple[float, float]],
    kept_keys: set[tuple[float, float]],
    max_examples: int = 5,
) -> dict[str, Any]:
    missing = sorted(oracle_keys - kept_keys)
    examples = [{"lat": la, "lon": lo} for la, lo in missing[:max_examples]]
    return {"count": len(missing), "examples": examples}


def _median_timed(reps: int, fn) -> float:
    samples: list[float] = []
    for _ in range(reps):
        t0 = time.perf_counter()
        fn()
        samples.append(time.perf_counter() - t0)
    return float(statistics.median(samples))


def _find_probe_row(lat: np.ndarray, lon: np.ndarray, probe_lat: float, probe_lon: float) -> int | None:
    d2 = (lat - probe_lat) ** 2 + ((lon - probe_lon + 180.0) % 360.0 - 180.0) ** 2
    i = int(np.argmin(d2))
    if abs(float(lat[i]) - probe_lat) > 0.02 or abs(float(lon[i]) - probe_lon) > 0.02:
        return None
    return i


def _lon_mask_scalar(lon_deg: float, lo_lon: float, width: float) -> bool:
    if width >= 360.0:
        return True
    return (float(lon_deg) - lo_lon) % 360.0 <= (width + LON_PAD)


def _auditor_probe(lat: np.ndarray, lon: np.ndarray) -> dict[str, Any]:
    probe_lat, probe_lon = -85.0, 99.99
    lo_lat, hi_lat, lo_lon, width = _sorted_rect(-85.6, -84.4, 100.0, 101.0)
    row = _find_probe_row(lat, lon, probe_lat, probe_lon)
    production = sites_in_latlon_rect(lo_lat, hi_lat, lo_lon, lo_lon + width)
    prod_keys = _keys_from_sites(production)
    probe_key = _cell_key(probe_lat, probe_lon)

    intersects = _footprint_intersects_latlon_rect(
        probe_lat, probe_lon, lo_lat, hi_lat, lo_lon, width
    )
    lon_ok = _lon_mask_scalar(probe_lon, lo_lon, width)

    nearest: dict[str, Any] | None = None
    in_prod_nearest = None
    if row is not None:
        la, lo = float(lat[row]), float(lon[row])
        nearest = {"lat": la, "lon": lo, "row": row}
        in_prod_nearest = _cell_key(la, lo) in prod_keys

    # If footprint touches but lon mask excludes center, that is the known criba gap (fail completeness).
    lon_mask_gap = intersects and not lon_ok
    prod_has_touch = probe_key in prod_keys or bool(
        row is not None
        and _footprint_intersects_latlon_rect(
            float(lat[row]), float(lon[row]), lo_lat, hi_lat, lo_lon, width
        )
        and _cell_key(float(lat[row]), float(lon[row])) in prod_keys
    )
    return {
        "probe_center": {"lat": probe_lat, "lon": probe_lon},
        "nearest_index_center": nearest,
        "footprint_intersects_at_probe_center": intersects,
        "lon_mask_includes_probe_center": lon_ok,
        "production_includes_exact_probe_key": probe_key in prod_keys,
        "production_includes_nearest_index": in_prod_nearest,
        "production_count": len(production),
        "checks": {
            "lon_mask_gap_when_footprint_intersects": lon_mask_gap,
            "production_returns_touching_cell": prod_has_touch,
        },
        "pass": not lon_mask_gap and (not intersects or prod_has_touch),
    }


def _analyze_rect(
    lat: np.ndarray,
    lon: np.ndarray,
    rect: dict[str, float | str],
    reps: int,
) -> dict[str, Any]:
    lo_lat, hi_lat, lo_lon, width = _sorted_rect(
        float(rect["lat_min"]),
        float(rect["lat_max"]),
        float(rect["lon_min"]),
        float(rect["lon_max"]),
    )
    lat_mask, lon_mask = _production_masks(lat, lon, lo_lat, hi_lat, lo_lon, width)

    oracle_idx = _oracle_indices(lat, lon, lo_lat, hi_lat, lo_lon, width)
    oracle_keys = _keys_from_indices(lat, lon, oracle_idx)

    lat_cand = np.flatnonzero(lat_mask)
    lon_cand = np.flatnonzero(lon_mask)
    both_cand = np.flatnonzero(lat_mask & lon_mask)

    both_idx = _both_masks_then_intersect(lat, lon, lat_mask, lon_mask, lo_lat, hi_lat, lo_lon, width)
    production = sites_in_latlon_rect(lo_lat, hi_lat, lo_lon, lo_lon + width)
    prod_keys = _keys_from_sites(production)

    precision = {
        "oracle_count": len(oracle_keys),
        "lat_mask_candidates": int(len(lat_cand)),
        "lon_mask_candidates": int(len(lon_cand)),
        "both_mask_candidates": int(len(both_cand)),
        "both_masks_then_intersect_count": len(both_idx),
        "production_count": len(prod_keys),
        "omissions_vs_lat_mask_candidates": _omission_report(
            lat, lon, oracle_keys, _keys_from_indices(lat, lon, lat_cand)
        ),
        "omissions_vs_lon_mask_candidates": _omission_report(
            lat, lon, oracle_keys, _keys_from_indices(lat, lon, lon_cand)
        ),
        "omissions_vs_both_mask_candidates": _omission_report(
            lat, lon, oracle_keys, _keys_from_indices(lat, lon, both_cand)
        ),
        "omissions_vs_both_masks_intersect": _omission_report(
            lat, lon, oracle_keys, _keys_from_indices(lat, lon, both_idx)
        ),
        "omissions_vs_production": _omission_report(lat, lon, oracle_keys, prod_keys),
    }

    timing = {
        "full_oracle_scan_s": _median_timed(
            reps,
            lambda: _oracle_indices(lat, lon, lo_lat, hi_lat, lo_lon, width),
        ),
        "both_masks_then_intersect_s": _median_timed(
            reps,
            lambda: _both_masks_then_intersect(
                lat, lon, lat_mask, lon_mask, lo_lat, hi_lat, lo_lon, width
            ),
        ),
        "production_sites_in_latlon_rect_s": _median_timed(
            reps,
            lambda: sites_in_latlon_rect(lo_lat, hi_lat, lo_lon, lo_lon + width),
        ),
    }

    return {
        "id": rect.get("id", "unnamed"),
        "rect": {
            "lat_min": lo_lat,
            "lat_max": hi_lat,
            "lon_min": lo_lon,
            "lon_max": lo_lon + width,
        },
        "precision": precision,
        "timing_median_s": timing,
    }


def _print_summary(report: dict[str, Any]) -> None:
    print("bench_selector_cribas (D-20261122-pj-c1ed)")
    print(f"index_rows: {report['index_rows']}")
    print(f"reps (median wall time): {report['reps']}")
    probe = report["auditor_probe"]
    print("\n--- auditor probe (center lat=-85, lon=99.99; rect lon 100–101) ---")
    print(
        f"  footprint_intersects={probe['footprint_intersects_at_probe_center']}  "
        f"lon_mask={probe['lon_mask_includes_probe_center']}  "
        f"n_production={probe['production_count']}"
    )
    nc = probe.get("nearest_index_center")
    if nc:
        print(
            f"  nearest index: lat={nc['lat']}, lon={nc['lon']}  "
            f"in_production={probe['production_includes_nearest_index']}"
        )
    ch = probe["checks"]
    print(
        f"  lon_mask_gap={ch['lon_mask_gap_when_footprint_intersects']}  "
        f"production_touch={ch['production_returns_touching_cell']}"
    )
    print(f"  PASS/FAIL: {'PASS' if probe['pass'] else 'FAIL'}")

    for block in report["rectangles"]:
        pid = block["id"]
        p = block["precision"]
        t = block["timing_median_s"]
        print(f"\n--- {pid} ---")
        print(
            f"  oracle={p['oracle_count']}  prod={p['production_count']}  "
            f"prod omissions={p['omissions_vs_production']['count']}"
        )
        print(
            f"  mask omissions (oracle not in candidates): "
            f"lat={p['omissions_vs_lat_mask_candidates']['count']}  "
            f"lon={p['omissions_vs_lon_mask_candidates']['count']}  "
            f"both={p['omissions_vs_both_mask_candidates']['count']}"
        )
        if p["omissions_vs_production"]["examples"]:
            ex = p["omissions_vs_production"]["examples"][0]
            print(f"  example prod omission: lat={ex['lat']}, lon={ex['lon']}")
        print(
            f"  median_s: oracle={t['full_oracle_scan_s']:.4f}  "
            f"both_masks+intersect={t['both_masks_then_intersect_s']:.4f}  "
            f"production={t['production_sites_in_latlon_rect_s']:.4f}"
        )


def main() -> int:
    ap = argparse.ArgumentParser(description="Measure selector cribas (D-20261122-pj-c1ed).")
    ap.add_argument("--json-out", type=Path, default=None, help="Write full JSON report to PATH.")
    ap.add_argument("--reps", type=int, default=5, help="Timing repetitions (median reported).")
    ap.add_argument(
        "--log-dir",
        type=Path,
        default=REPO / "logs",
        help="When --json-out omitted, optional default log path under logs/.",
    )
    args = ap.parse_args()

    if not cap_index_available():
        print("cap_1km index not available; skipping.", file=sys.stderr)
        return 2

    table = _load_index()
    lat = table.column("lat").to_numpy()
    lon = table.column("lon").to_numpy()
    n = len(lat)

    rectangles = [_analyze_rect(lat, lon, r, args.reps) for r in DEFAULT_RECTS]
    probe = _auditor_probe(lat, lon)

    report: dict[str, Any] = {
        "decision": "D-20261122-pj-c1ed",
        "index_rows": n,
        "reps": args.reps,
        "cribas": {
            "lat_pad_center": LAT_PAD,
            "lon_pad_center": LON_PAD,
            "footprint_fn": "_footprint_intersects_latlon_rect",
        },
        "auditor_probe": probe,
        "rectangles": rectangles,
    }

    out_path = args.json_out
    if out_path is None:
        args.log_dir.mkdir(parents=True, exist_ok=True)
        out_path = args.log_dir / "bench_selector_cribas.json"

    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    _print_summary(report)
    print(f"\nJSON: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())