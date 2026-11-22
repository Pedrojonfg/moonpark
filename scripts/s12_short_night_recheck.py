#!/usr/bin/env python3
"""S12 short-night re-check harness (D-39f3, D-1a9e).

Heavy DEM/mask work is overnight. This script records a run stub or SKIP
when data is missing; it does not invent pass numbers. With ``--validation-full``,
missing DEM exits 2 (D-b591).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATION = ROOT / "docs" / "validation.md"
SITE01 = {"name": "Site01", "lat_deg": -89.46316, "lon_deg": 222.51045}
SCRIPT_ID = "s12_short_night_recheck"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--year", type=int, default=2027, help="fixed test year (pin in report)")
    p.add_argument("--json-out", type=Path, default=None)
    p.add_argument(
        "--force-run",
        action="store_true",
        help="reserved for overnight: compute schedule vs fine reference (not implemented without DEM wiring)",
    )
    p.add_argument(
        "--validation-full",
        action="store_true",
        help="fail (exit 2) when DEM is missing instead of SKIP success",
    )
    p.add_argument("--checkpoint", type=Path, default=None, help="resumable progress file (D-814a)")
    p.add_argument("--resume", action="store_true", help="continue from --checkpoint when present")
    args = p.parse_args()

    sys.path.insert(0, str(ROOT))
    from scripts.validation_checkpoint import load_checkpoint, save_checkpoint

    prior = load_checkpoint(args.checkpoint) if args.resume else None
    if prior and prior.get("script") == SCRIPT_ID and prior.get("status") == "complete":
        print(json.dumps(prior, indent=2))
        return 0

    dem = ROOT / "data" / "dem"
    has_dem = dem.is_dir() and any(dem.glob("*.TIF"))
    status = "SKIP_NO_DEM" if not has_dem else "HARNESS_READY_AWAITING_OVERNIGHT"
    if not has_dem and (args.force_run or args.validation_full):
        print("error: validation-full needs DEM tiles under data/dem/", file=sys.stderr)
        return 2

    payload = {
        "decision": "D-20261115-pj-39f3",
        "mode": "separate_report_reopen_y_if_over_tol",
        "tolerance_h": 5,
        "bridge_h": 5,
        "year": args.year,
        "sites": [SITE01],
        "status": status,
        "note": (
            "Overnight: compare schedule mask longest_night/lit vs fine reference; "
            "if abs error > 5 h, reopen success_y via a new decision."
        ),
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
            "status": "complete" if status != "HARNESS_READY_AWAITING_OVERNIGHT" else "stub",
            "next_site_index": len(payload["sites"]) if status == "complete" else 0,
            "payload": payload,
        },
    )

    print(json.dumps(payload, indent=2))
    print(f"\n# Update {VALIDATION} Results section after a real overnight compute.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
