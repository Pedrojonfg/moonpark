# Validation (S12)

Evidence-gated (`D-de70`). Rows without a dated command + numbers remain **planned**.

| Check | Decision | Status | How to run |
|-------|----------|--------|------------|
| Success X/Y/Z | `D-41fa` | Horizons and score tests exist; the 28-point 5 m comparison is **not in the repo** (removed from claims) | `pytest` |
| Horizons apparent az/el | `D-c403` | **CI** — ≥8 case blocks at 0.05° (`tests/test_ephemeris.py`) | `pytest tests/test_ephemeris.py` |
| Temporal step convergence | `D-7a51` | **run 2026-11-22** (WSL; kernels + cap on disk) | `python scripts/s12_temporal_convergence.py --force-run` |
| Spatial cap vs fine mask | `D-7bd7` | **run 2026-11-22** (WSL; kernels + cap on disk) | `python scripts/s12_spatial_convergence.py --force-run` |
| Short-night re-check | `D-39f3` (S1) | **planned** — harness is a skeleton, comparison not implemented | `python scripts/s12_short_night_recheck.py` |
| PGDA 69 average illumination | `D-9ab3` (P1), role `D-fe17` | **planned** — harness is a skeleton, comparison not implemented | `python scripts/s12_pgda69_compare.py` |

## Short-night re-check (`D-39f3`)

- Mode: separate report; if \|error\| > 5 h → reopen Y (do not silently change `success_y`).
- Defaults: light definition as the Y comparison is (not yet in the repo); bridge 5 h; tolerance 5 h.
- Sites: Site01 + PGDA-78 / 5 m points with longest night ~40–80 h when available.
- Year: pin in script output when first run (`s12_short_night_year` still deferred until then).

### Results

_No overnight run recorded yet._

## Temporal convergence (`D-7a51`)

- Sites: Site01, Site04.
- Window: 2027-01-01 → 2027-02-01 (31 days).
- Steps: 60, 10, 1 minute; hazards off.
- Doc triggers: \|Δ longest night\| > 2 h (60 vs 10 or 60 vs 1); \|Δ score\| > 0.05 with same feasible.

### Results

**2026-11-22** — `python scripts/s12_temporal_convergence.py --force-run --json-out logs/validation/temporal.json` (~26 s wall).

| Site | step (min) | feasible | score | longest night (h) | n samples |
|------|------------|----------|-------|-------------------|-----------|
| Site01 | 60 | no | 0.0 | 245.0 | 745 |
| Site01 | 10 | no | 0.0 | 244.17 | 4465 |
| Site01 | 1 | no | 0.0 | 244.17 | 44641 |
| Site04 | 60 | no | 0.0 | 319.0 | 745 |
| Site04 | 10 | no | 0.0 | 318.5 | 4465 |
| Site04 | 1 | no | 0.0 | 318.4 | 44641 |

`doc_triggers`: none (all \|Δ longest night\| ≤ 2 h and \|Δ score\| = 0 with same feasible).

## Spatial convergence (`D-7bd7`)

- Sites: Site01, Site04, Site07.
- Window: 7 days from 2027-01-01; step 60 min; hazards off.
- Compare: nearest 1 km cap mask vs `mask_for_site` (finest on disk).
- Doc trigger: \|Δ score\| > 0.05 or feasible mismatch → README 1 km limitation.

### Results

**2026-11-22** — `python scripts/s12_spatial_convergence.py --force-run --json-out logs/validation/spatial.json` (~24 s wall).

| Site | mask | feasible | score | longest night (h) | schedule |
|------|------|----------|-------|-------------------|----------|
| Site01 | cap | no | 0.0 | 11.0 | D-f369-v1 |
| Site01 | fine | no | 0.0 | 12.0 | D-f369-v1 |
| Site04 | cap / fine | no | 0.0 | 168.0 / 168.0 | D-f369-v1 |
| Site07 | cap / fine | no | 0.0 | 0.0 / 0.0 | D-f369-v1 |

Primary: \|Δ score\| = 0 and feasible match at all sites → no README 1 km trigger. Site01 secondary: longest night differs by 1 h between cap and fine (still same score/feasible).

## PGDA 69 comparison (`D-9ab3`)

- Product: average solar illumination (south), cite exact file in the run log.
- Sites: PGDA 78 / 5 m schedule set (document IDs/coords in the run output).
- Span: ~18.6 y or product label span; light def match product (any disc default).
- Metric: Δ percentage points per site (ours − map). **No pass/fail threshold in v1.**
- README may say planned / point here until a table exists (`D-fe17`).

### Results

_No overnight run recorded yet._
