#!/usr/bin/env python3
"""S12 short-night re-check harness (D-39f3, D-1a2d, D-814a).

Compare longest night (h) for calendar year: cap 1 km mask vs fine 5 m mask (PGDA-78).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
VALIDATION = ROOT / "docs" / "validation.md"
SCRIPT_ID = "s12_short_night_recheck"
TOLERANCE_H = 5
BRIDGE_H = 5


def _dem_ok() -> bool:
    dem = ROOT / "data" / "dem"
    return dem.is_dir() and any(dem.glob("*.TIF"))


def _run(year: int, *, resume_rows: list[dict], resume_at: int) -> tuple[list[dict], str]:
    sys.path.insert(0, str(ROOT))
    from scripts.s12_validation_lib import cap_mask, fine_mask_5m, longest_night_hours, pgda_pgda78_sites

    start = np.datetime64(f"{year}-01-01T00:00:00", "s")
    end = np.datetime64(f"{year}-12-31T23:00:00", "s")
    sites = pgda_pgda78_sites(ROOT)
    names = sorted(sites)
    rows = list(resume_rows)
    for idx, name in enumerate(names):
        if idx < resume_at:
            continue
        site = sites[name]
        cap_h = longest_night_hours(site, cap_mask(site), start, end)
        fine_h = longest_night_hours(site, fine_mask_5m(ROOT, name, site), start, end)
        err = cap_h - fine_h
        rows.append(
            {
                "site": name,
                "lat_deg": site.lat_deg,
                "lon_deg": site.lon_deg,
                "year": year,
                "longest_night_cap_h": cap_h,
                "longest_night_fine_h": fine_h,
                "error_h": err,
                "abs_error_h": abs(err),
            }
        )
    over = [r for r in rows if r.get("abs_error_h", 0) > TOLERANCE_H]
    return rows, "complete", over


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--year", type=int, default=2027)
    p.add_argument("--json-out", type=Path, default=None)
    p.add_argument("--force-run", action="store_true")
    p.add_argument("--validation-full", action="store_true")
    p.add_argument("--checkpoint", type=Path, default=None)
    p.add_argument("--resume", action="store_true")
    args = p.parse_args()
    # per D-20261122-pj-a64b: --validation-full must force the scientific run when inputs exist
    args.force_run = args.force_run or args.validation_full

    sys.path.insert(0, str(ROOT))
    from scripts.validation_checkpoint import load_checkpoint, save_checkpoint

    prior = load_checkpoint(args.checkpoint) if args.resume else None
    if prior and prior.get("script") == SCRIPT_ID and prior.get("status") == "complete":
        print(json.dumps(prior.get("payload") or prior, indent=2))
        return 0

    has_dem = _dem_ok()
    if not has_dem and (args.force_run or args.validation_full):
        print("error: validation-full needs DEM tiles under data/dem/", file=sys.stderr)
        return 2

    resume_rows: list[dict] = []
    resume_at = 0
    if prior and prior.get("script") == SCRIPT_ID:
        resume_rows = list(prior.get("comparisons") or [])
        resume_at = len(resume_rows)

    comparisons: list[dict] = []
    over_tol: list[dict] = []
    if not args.force_run or not has_dem:
        status = "SKIP_NO_DEM" if not has_dem else "HARNESS_READY_AWAITING_OVERNIGHT"
    else:
        comparisons, status, over_tol = _run(args.year, resume_rows=resume_rows, resume_at=resume_at)
        for i, _ in enumerate(comparisons):
            save_checkpoint(
                args.checkpoint,
                {
                    "version": 1,
                    "script": SCRIPT_ID,
                    "status": "partial" if i + 1 < len(comparisons) else status,
                    "next_site_index": i + 1,
                    "comparisons": comparisons[: i + 1],
                },
            )

    payload = {
        "decision": "D-20261115-pj-39f3",
        "mode": "document_only_on_fail_D-1a2d",
        "tolerance_h": TOLERANCE_H,
        "bridge_h": BRIDGE_H,
        "year": args.year,
        "status": status if args.force_run else ("SKIP_NO_DEM" if not has_dem else "HARNESS_READY_AWAITING_OVERNIGHT"),
        "comparisons": comparisons,
        "over_tolerance": over_tol,
        "reopen_y": bool(over_tol),
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
            "status": "complete" if payload["status"] == "complete" else "stub",
            "comparisons": comparisons,
            "payload": payload,
        },
    )

    print(json.dumps(payload, indent=2))
    print(f"\n# Update {VALIDATION} Results section.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())