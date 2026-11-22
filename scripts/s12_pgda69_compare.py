#!/usr/bin/env python3
"""S12 PGDA 69 comparison harness (D-9ab3, D-fe17, D-1a9e, D-6dc3).

Compare mean solar illumination (any disc) at PGDA-78 sites vs PGDA 69 map
over one lunar nutation span (~18.6 y, hourly). Report-only in v1.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
VALIDATION = ROOT / "docs" / "validation.md"
SCRIPT_ID = "s12_pgda69_compare"
NUTATION_YEARS = 18.6129
PGDA_LABEL_END = "2016-08-01T00:00:00Z"
LIGHT_DEF = "any_solar_disc_fraction"
CLAIM_MEDIAN_PP = 1.5
CLAIM_MAX_PP = 3.0


def _find_pgda69() -> Path | None:
    for base in (ROOT / "data" / "pgda69", ROOT / "data" / "illumination", ROOT / "data"):
        if not base.is_dir():
            continue
        for pat in ("*AVGVISIB*S*", "*avgvisib*s*", "*PGDA*69*"):
            hits = sorted(base.rglob(pat))
            if hits:
                return hits[0]
    return None


def _nutation_window() -> tuple[np.datetime64, np.datetime64]:
    end = np.datetime64(PGDA_LABEL_END.replace("Z", "").replace("T", " "), "s")
    days = int(round(NUTATION_YEARS * 365.25))
    start = end - np.timedelta64(days, "D")
    return start, end


def _run_compare(
    pgda_path: Path,
    *,
    resume_rows: list[dict],
    resume_at: int,
    checkpoint: Path | None = None,
) -> tuple[list[dict], str]:
    sys.path.insert(0, str(ROOT))
    from scripts.s12_validation_lib import fine_mask_5m, mean_sun_fraction, pgda_map_fraction, pgda_pgda78_sites

    sites = pgda_pgda78_sites(ROOT)
    names = sorted(sites)
    start, end = _nutation_window()
    deltas = list(resume_rows)
    for idx, name in enumerate(names):
        if idx < resume_at:
            continue
        site = sites[name]
        map_v, st, map_meta = pgda_map_fraction(pgda_path, site)
        if st not in ("ok", "partial_window") or not math.isfinite(map_v):
            deltas.append(
                {"site": name, "lat_deg": site.lat_deg, "lon_deg": site.lon_deg, "status": f"map_{st}"}
            )
            continue
        horizon = fine_mask_5m(ROOT, name, site)
        ours = mean_sun_fraction(site, horizon, start, end)
        delta_pp = (ours - map_v) * 100.0
        deltas.append(
            {
                "site": name,
                "lat_deg": site.lat_deg,
                "lon_deg": site.lon_deg,
                "pgda_fraction": map_v,
                "pgda_map_status": st,
                "pgda_map_meta": map_meta,
                "ours_fraction": ours,
                "delta_pp": delta_pp,
                "mask": "5m_pgda78",
            }
        )
        if checkpoint is not None:
            from scripts.validation_checkpoint import save_checkpoint

            save_checkpoint(
                checkpoint,
                {
                    "version": 1,
                    "script": SCRIPT_ID,
                    "status": "partial",
                    "next_site_index": idx + 1,
                    "deltas": deltas,
                },
            )
    status = "complete" if len(deltas) == len(names) else "partial"
    return deltas, status


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
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

    pgda = _find_pgda69()
    if pgda is None and (args.force_run or args.validation_full):
        print("error: place PGDA 69 average solar illumination under data/", file=sys.stderr)
        return 2

    resume_rows: list[dict] = []
    resume_at = 0
    if prior and prior.get("script") == SCRIPT_ID:
        resume_rows = list(prior.get("deltas") or [])
        resume_at = len(resume_rows)

    if not args.force_run or pgda is None:
        status = "SKIP_NO_PGDA69_FILE" if pgda is None else "HARNESS_READY_AWAITING_OVERNIGHT"
        deltas: list[dict] = []
    else:
        deltas, status = _run_compare(
            pgda, resume_rows=resume_rows, resume_at=resume_at, checkpoint=args.checkpoint
        )

    abs_d = [abs(r["delta_pp"]) for r in deltas if "delta_pp" in r]
    claim = None
    if abs_d:
        med = float(np.median(abs_d))
        mx = float(max(abs_d))
        claim = {
            "median_abs_delta_pp": med,
            "max_abs_delta_pp": mx,
            "soft_claim_ok": med <= CLAIM_MEDIAN_PP and mx <= CLAIM_MAX_PP,
            "decision": "D-20261122-pj-6dc3",
        }

    start, end = _nutation_window()
    payload = {
        "decision": "D-20261115-pj-9ab3",
        "map_sampling": "D-20261122-pj-f8c2",
        "site07_note": "D-20261122-pj-d1c4",
        "role": "validation_report_and_readme_only",
        "product": "average_solar_illumination_south",
        "span": {"start": str(start), "end": str(end), "nutation_years": NUTATION_YEARS},
        "light_def": LIGHT_DEF,
        "metric": "delta_percentage_points_per_site",
        "pass_fail": "none_v1_report_only",
        "pgda69_path": str(pgda) if pgda else None,
        "sites": "pgda78_5m_schedule_set",
        "status": status if args.force_run else (
            "SKIP_NO_PGDA69_FILE" if pgda is None else "HARNESS_READY_AWAITING_OVERNIGHT"
        ),
        "deltas": deltas,
        "claim_soft_gate": claim,
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
            "next_site_index": len(deltas),
            "deltas": deltas,
            "payload": payload,
        },
    )

    print(json.dumps(payload, indent=2))
    print(f"\n# Copy deltas into {VALIDATION}; no README claim until reviewed (D-fe17).", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())