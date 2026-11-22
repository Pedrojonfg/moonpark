#!/usr/bin/env python3
"""Spatial cap vs fine mask convergence (D-7bd7, D-814a).

Site01, Site04, Site07 — 7 days from 2027-01-01, step 60 min, hazards off.
Dry-run when data missing; --force-run when kernels + cap (+ DEM for fine) exist.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATION = ROOT / "docs" / "validation.md"
SCRIPT_ID = "s12_spatial_convergence"
DECISION = "D-20261122-pj-7bd7"
START = "2027-01-01T00:00:00Z"
END = "2027-01-08T00:00:00Z"
STEP_MIN = 60
DOC_DELTA_SCORE = 0.05


def _ready() -> tuple[bool, bool]:
    try:
        from moonpark.horizon.cap_index import cap_index_available
        from moonpark.planner_payload import kernels_available

        return bool(kernels_available()), bool(cap_index_available())
    except Exception:
        return False, False


def _score_with_horizon(site, times, horizon, step_min: int) -> dict:
    from moonpark.ephemeris import SpiceEphemeris
    from moonpark.planner_payload import _series_json, build_score_needs
    from moonpark.score import score
    from moonpark.visibility import series
    from scripts.s12_sites import DEFAULT_NEEDS

    sky = SpiceEphemeris().sky(site, times)
    vis = series(
        sky,
        horizon,
        sun_threshold=0.0,
        earth_threshold=0.0,
        bridge_h=5,
        step_min=step_min,
    )
    sj = _series_json(vis)
    score_needs, _ = build_score_needs(DEFAULT_NEEDS, hazards_enabled=False)
    scored = score(sj, {}, score_needs)
    return {
        "feasible": bool(scored["feasible"]),
        "score": float(scored["score"]),
        "longest_night_h": float(sj["longest_night_h"]),
        "schedule_version": str(horizon.schedule_version),
    }


def _run_site(site_name: str) -> dict:
    import numpy as np

    from moonpark.horizon.cap_index import nearest_cap_mask
    from moonpark.horizon.mask_store import mask_for_site
    from moonpark.planner_payload import parse_time_window
    from scripts.s12_sites import SITES

    site = SITES[site_name]
    times = np.asarray(parse_time_window(START, END, step_min=STEP_MIN), dtype="datetime64[s]")
    cap = nearest_cap_mask(site)
    if cap is None:
        return {"site": site_name, "status": "SKIP_NO_CAP_MASK"}
    fine = mask_for_site(site)
    cap_row = _score_with_horizon(site, times, cap, STEP_MIN)
    fine_row = _score_with_horizon(site, times, fine, STEP_MIN)
    delta_score = fine_row["score"] - cap_row["score"]
    doc_note = None
    if cap_row["feasible"] != fine_row["feasible"] or abs(delta_score) > DOC_DELTA_SCORE:
        doc_note = "README limitation: 1 km cap mask vs finest on disk differs beyond doc trigger"
    return {
        "site": site_name,
        "status": "ok",
        "cap": cap_row,
        "fine": fine_row,
        "delta_score": delta_score,
        "feasible_match": cap_row["feasible"] == fine_row["feasible"],
        "doc_note": doc_note,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json-out", type=Path, default=None)
    p.add_argument("--force-run", action="store_true")
    p.add_argument("--validation-full", action="store_true")
    p.add_argument("--checkpoint", type=Path, default=None)
    p.add_argument("--resume", action="store_true")
    args = p.parse_args()

    sys.path.insert(0, str(ROOT))
    from scripts.s12_sites import SITES
    from scripts.validation_checkpoint import load_checkpoint, save_checkpoint

    prior = load_checkpoint(args.checkpoint) if args.resume else None
    if prior and prior.get("script") == SCRIPT_ID and prior.get("status") == "complete":
        print(json.dumps(prior.get("payload") or prior, indent=2))
        return 0

    has_kernels, has_cap = _ready()
    if not has_kernels and (args.force_run or args.validation_full):
        print("error: needs SPICE kernels", file=sys.stderr)
        return 2
    if not has_cap and (args.force_run or args.validation_full):
        print("error: needs cap_1km index", file=sys.stderr)
        return 2

    done: list[dict] = []
    if prior and prior.get("script") == SCRIPT_ID:
        done = list(prior.get("results") or [])

    status = (
        "HARNESS_READY_AWAITING_OVERNIGHT"
        if has_kernels and has_cap
        else "SKIP_NO_KERNELS_OR_CAP"
    )
    if args.force_run and has_kernels and has_cap:
        done_names = {r["site"] for r in done if r.get("status") == "ok"}
        for site_name in ("Site01", "Site04", "Site07"):
            if site_name not in SITES or site_name in done_names:
                continue
            done.append(_run_site(site_name))
            save_checkpoint(
                args.checkpoint,
                {"version": 1, "script": SCRIPT_ID, "status": "partial", "results": done},
            )
        if len([r for r in done if r.get("status") == "ok"]) == 3:
            status = "complete"

    payload = {
        "decision": DECISION,
        "sites": ["Site01", "Site04", "Site07"],
        "window": {"start": START, "end": END},
        "step_min": STEP_MIN,
        "hazards_enabled": False,
        "status": status,
        "results": done,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    save_checkpoint(
        args.checkpoint,
        {
            "version": 1,
            "script": SCRIPT_ID,
            "status": "complete" if status == "complete" else "stub",
            "results": done,
            "payload": payload,
        },
    )

    print(json.dumps(payload, indent=2))
    print(f"\n# Copy numbers into {VALIDATION} after run.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())