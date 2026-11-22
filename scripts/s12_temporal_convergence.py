#!/usr/bin/env python3
"""Temporal step convergence harness (D-7a51, D-814a).

Compare step 60, 10, and 1 min on Site01 and Site04 over 31 days.
Dry-run records protocol; --force-run computes when kernels are present.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATION = ROOT / "docs" / "validation.md"
SCRIPT_ID = "s12_temporal_convergence"
DECISION = "D-20261122-pj-7a51"
START = "2027-01-01T00:00:00Z"
END = "2027-02-01T00:00:00Z"
STEPS = (60, 10, 1)
DOC_DELTA_NIGHT_H = 2.0
DOC_DELTA_SCORE = 0.05


def _ready() -> bool:
    try:
        from moonpark.planner_payload import kernels_available

        return bool(kernels_available())
    except Exception:
        return False


def _run_site(site_name: str, step_min: int) -> dict:
    import numpy as np

    from moonpark.planner_payload import build_planner_payload, parse_time_window
    from scripts.s12_sites import DEFAULT_NEEDS, SITES

    site = SITES[site_name]
    times = np.asarray(parse_time_window(START, END, step_min=step_min), dtype="datetime64[s]")
    payload = build_planner_payload(
        site,
        times,
        needs=DEFAULT_NEEDS,
        sun_lit_percent=0,
        earth_lit_percent=0,
        bridge_h=5,
        hazards_enabled=False,
        step_min=step_min,
    )
    series = payload["series"]
    scored = payload["score"]
    return {
        "step_min": step_min,
        "feasible": bool(scored["feasible"]),
        "score": float(scored["score"]),
        "longest_night_h": float(series["longest_night_h"]),
        "n_samples": int(len(times)),
    }


def _doc_triggers(rows: list[dict]) -> list[str]:
    notes: list[str] = []
    by_step = {r["step_min"]: r for r in rows}
    if 60 in by_step and 10 in by_step:
        a, b = by_step[60], by_step[10]
        if abs(a["longest_night_h"] - b["longest_night_h"]) > DOC_DELTA_NIGHT_H:
            notes.append("|Δ longest night| > 2 h between 60 and 10 min → document finer step")
        if a["feasible"] == b["feasible"] and abs(a["score"] - b["score"]) > DOC_DELTA_SCORE:
            notes.append("|Δ score| > 0.05 between 60 and 10 min (same feasible) → document finer step")
    if 60 in by_step and 1 in by_step:
        a, b = by_step[60], by_step[1]
        if abs(a["longest_night_h"] - b["longest_night_h"]) > DOC_DELTA_NIGHT_H:
            notes.append("|Δ longest night| > 2 h between 60 and 1 min → document finer step")
        if a["feasible"] == b["feasible"] and abs(a["score"] - b["score"]) > DOC_DELTA_SCORE:
            notes.append("|Δ score| > 0.05 between 60 and 1 min (same feasible) → document finer step")
    return notes


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
    from scripts.s12_sites import SITES
    from scripts.validation_checkpoint import load_checkpoint, save_checkpoint

    prior = load_checkpoint(args.checkpoint) if args.resume else None
    if prior and prior.get("script") == SCRIPT_ID and prior.get("status") == "complete":
        print(json.dumps(prior.get("payload") or prior, indent=2))
        return 0

    has_kernels = _ready()
    if not has_kernels and (args.force_run or args.validation_full):
        print("error: --force-run / --validation-full needs SPICE kernels on disk", file=sys.stderr)
        return 2

    done: dict[str, list[dict]] = {}
    if prior and prior.get("script") == SCRIPT_ID:
        done = dict(prior.get("results") or {})

    status = "HARNESS_READY_AWAITING_OVERNIGHT" if has_kernels else "SKIP_NO_KERNELS"
    if args.force_run and has_kernels:
        status = "partial"
        for site_name in SITES:
            if site_name not in ("Site01", "Site04"):
                continue
            rows = list(done.get(site_name) or [])
            have = {r["step_min"] for r in rows}
            for step in STEPS:
                if step in have:
                    continue
                rows.append(_run_site(site_name, step))
                done[site_name] = rows
                save_checkpoint(
                    args.checkpoint,
                    {
                        "version": 1,
                        "script": SCRIPT_ID,
                        "status": "partial",
                        "results": done,
                    },
                )
        if all(len(done.get(s, [])) == len(STEPS) for s in ("Site01", "Site04")):
            status = "complete"
        else:
            status = "partial"

    payload: dict = {
        "decision": DECISION,
        "sites": ["Site01", "Site04"],
        "window": {"start": START, "end": END},
        "steps_min": list(STEPS),
        "hazards_enabled": False,
        "status": status,
        "results": done,
        "doc_triggers": [],
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    if done:
        for site_name, rows in done.items():
            if len(rows) == len(STEPS):
                payload["doc_triggers"].extend(_doc_triggers(rows))

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
    print(f"\n# Copy numbers into {VALIDATION} after overnight run.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())