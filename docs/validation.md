# Validation (S12)

Evidence-gated (`D-de70`). Rows without a dated command + numbers remain **planned**.

**`validation_full` / `D-20261122-pj-a64b`:** Locally, `pytest -m validation_full` (or `--validation-full` on the S12 harness scripts) with DEM/PGDA/kernels on disk runs the same compare path as `--force-run` — green means science ran, not `HARNESS_READY_AWAITING_OVERNIGHT`. In GitHub **Validation full** without heavy data, scripts exit 2 and the job fails (`D-b591`); that is not a science pass. A pytest that only checks exit 2 when data is absent proves the missing-data gate only.

| Check | Decision | Status | How to run |
|-------|----------|--------|------------|
| Success X/Y/Z | `D-41fa` | Horizons and score tests exist; the 28-point 5 m comparison is **not in the repo** (removed from claims) | `pytest` |
| Horizons apparent az/el | `D-c403` | **CI** — ≥8 case blocks at 0.05° (`tests/test_ephemeris.py`) | `pytest tests/test_ephemeris.py` |
| Temporal step convergence | `D-7a51` | **run 2026-11-22** (WSL; kernels + cap on disk) | `python scripts/s12_temporal_convergence.py --force-run` |
| Spatial cap vs fine mask | `D-7bd7` | **run 2026-11-22** (WSL; kernels + cap on disk) | `python scripts/s12_spatial_convergence.py --force-run` |
| Short-night re-check | `D-39f3` (S1) | **run 2026-11-22** (cap vs 5 m, year 2027) | `python scripts/s12_short_night_recheck.py --force-run` |
| PGDA 69 average illumination | `D-9ab3` (P1), map mean `D-f8c2`, role `D-fe17` | **run 2026-11-22** (re-run after `D-f8c2`) | `python scripts/s12_pgda69_compare.py --force-run` |

## Short-night re-check (`D-39f3`)

- Mode: separate report; if \|error\| > 5 h → reopen Y (do not silently change `success_y`).
- Defaults: light definition as the Y comparison is (not yet in the repo); bridge 5 h; tolerance 5 h.
- Sites: Site01 + PGDA-78 / 5 m points with longest night ~40–80 h when available.
- Year: pin in script output when first run (`s12_short_night_year` still deferred until then).

### Results

**2026-11-22** — `python scripts/s12_short_night_recheck.py --force-run --year 2027` (~29 s). Longest night (h), cap 1 km vs fine 5 m PGDA-78, bridge 5 h.

| Site | cap | fine | error (h) | > 5 h |
|------|-----|------|-----------|-------|
| Site01 | 496 | 496 | 0 | no |
| Site04 | 4902 | 4902 | 0 | no |
| Site07 | 386 | 394 | −8 | **yes** |
| Site11 | 436 | 431 | +5 | at limit |

Per `D-1a2d`: document only — no automatic success\_y reopen. Site07 cap underrates longest night by 8 h vs fine 5 m.

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

**2026-11-22 (re-run, `D-f8c2`)** — `python scripts/s12_pgda69_compare.py --force-run` (~2.5 min). Map `AVGVISIB_85S_060M_201608.TIF`; span 1997-12-21 → 2016-08-01 (18.6129 y); hourly mean sun disc fraction. Map reference = **mean of 5×5 PGDA cells** at native 60 m posting (`D-f8c2`), not centre pixel only.

| Site | PGDA (window mean) | PGDA (centre cell) | ours | Δ (pp) |
|------|-------------------|--------------------|------|--------|
| Site01 | 44.58 | 38.54 | 46.59 | +2.01 |
| Site04 | 10.97 | 10.96 | 9.04 | −1.93 |
| Site07 | 54.58 | 17.02 | 67.39 | +12.81 |
| Site11 | 52.25 | 49.00 | 53.15 | +0.90 |

Soft claim gate (`D-6dc3`): median \|Δ\| = **1.97 pp**, max = **12.81 pp** (Site07) → **not OK** for README agreement (max bound). Earlier same-day run used centre-pixel map only (Site07 Δ +50 pp); superseded for reporting by `D-f8c2`. No product pass/fail in v1 (`D-9ab3`).

#### Site07 note (`D-d1c4`)

- **Fixture:** **Peak near Shackleton** (`Site07`) at −88.811°, 123.690° with PGDA-78 DEM `Site07_final_adj_5mpp_surf.tif` (catalog: [`pgda78-site-catalog.md`](pgda78-site-catalog.md)).
- **Fine horizon:** elevation mask &lt; ~1.3° in all azimuths (very open sky) → high long-term mean sun fraction (~67 %).
- **PGDA 69 cliff:** centre 60 m cell **17 %**; 5×5 neighbours **17–86 %**; window mean **55 %**. Remaining Δ (+13 pp) is not explained by a single bad pixel alone.
- **Short-night:** cap vs fine longest night in 2027 differs by **8 h** (document-only per `D-1a2d`).

#### PGDA-78 catalog (`D-d1c4`, verified 2026-11-22)

Full table: [`docs/pgda78-site-catalog.md`](pgda78-site-catalog.md). S12 PGDA set: **Connecting ridge** (Site01), **Shackleton rim** (Site04), **Peak near Shackleton** (Site07), **de Gerlache rim** (Site11); fixtures match DEM tile centres (&lt; 0.1 m).

## Estimate-layer interpolator benchmark (`D-20261122-pj-b4ca`)

Compares three estimate methods against real `total_coverage` scores near Site01. **No winner is chosen here** and the production estimate stays four-quadrant 1/d² (`D-1df2`); the winning metric is deferred to a follow-up decision (`D-b4ca`).

- **Script:** `python scripts/bench_estimate_interpolation.py` (unit checks of the weight formulas: `tests/test_bench_estimate_weights.py`).
- **Truth:** real `total_coverage` through `deep_search` on the 1 km cap cells (cap tile masks, SPICE ephemeris, `moonpark.score`, hazards off). Two truth configurations:
  - `map_best_window`: template `clps_average`, 24 h windows, hourly starts for 7 days from 2027-01-01, one value per cell collapsed to its best window with the map's own rule (`region_map._dedupe_rows`).
  - `fixed_window_mixed`: template `dte_relay_priority`, one 24 h window starting 2027-01-19T04:00Z. It was picked as the hourly start in January 2027 whose feasible fraction on the 3 km square is closest to 50 %, because `map_best_window` is feasible in every cell and cannot exercise the colour-mismatch metric. This is a stress case for feasibility, not a typical map.
- **Regions** (Site01 ± half-side, polar stereographic): `primary_3km` (3 × 3 km, **9 cap cells**; the contract region) and `supplement_9km` (9 × 9 km, 81 cells; beyond the contract, added because 9 cells is a thin sample).
- **Methods** (all use the `D-1df2` reach = clamp(3 × median known spacing, 3 km, 60 km), softening (0.05 × spacing)², and feasible when the feasible weight share ≥ 0.5):
  1. Four-quadrant 1/d²: nearest known cell per quadrant, weights 1/(d² + soft). Python port of `estimateAt` in `web/map.js` (the production estimate lives in JS, not in `moonpark/region_map.py`).
  2. Eight-neighbour IDW: the 8 nearest known cells within reach, same weights. ("Eight-neighbour" read as 8 nearest cells, not eight 45° sectors.)
  3. Gaussian: all known cells within reach, weights exp(−d² / 2σ²), σ = median nearest-neighbour spacing of the known cells.
- **Protocols:** leave-one-out; stride-2 lattice (known = every second cell in x and y, 4 phases, rest predicted); random 50 % known, 200 seeded trials (seed 20261122), pooled.
- **Metrics:** score error = predicted − truth. "Both feasible" = cells where truth and estimate are both feasible. "All" = every predicted cell with infeasible score = 0 (as `moonpark.score` returns), so one feasibility miss costs about 1.2. Feasible mismatch = share of predicted cells whose estimated feasible flag differs from truth.
- **Ties:** equal-distance neighbours (frequent on the regular 1 km grid) break by (x, y) so results do not depend on list order; `web/map.js` keeps whichever neighbour its hash visits first.

### Results

**2026-11-22** — `python scripts/bench_estimate_interpolation.py` (~16–21 s wall, WSL, kernels + cap index on disk). Raw: `logs/bench_estimate_interpolation.json` (summary + per-cell truth), `logs/bench_estimate_interpolation_cells.csv` (every prediction error).

#### `map_best_window` — `clps_average`, best window per cell

Truth is feasible in all 9 and all 81 cells, so the mismatch rate is 0 for every method by construction. Best-window scores sit on a plateau (about 1.131 in most cells; minimum 1.013), so errors are dominated by a few off-plateau cells.

**primary_3km (contract region)** — 9 truth cells, 9 feasible

| Protocol | Method | n pred | max \|e\| (both feasible) | RMSE (both feasible) | max \|e\| (all, infeasible = 0) | RMSE (all) | feasible mismatch |
|---|---|---|---|---|---|---|---|
| leave-one-out | Four-quadrant 1/d² (D-1df2) | 9 | 0.117 | 0.0519 | 0.117 | 0.052 | 0.0 % |
| leave-one-out | Eight-neighbour IDW | 9 | 0.112 | 0.0486 | 0.112 | 0.049 | 0.0 % |
| leave-one-out | Gaussian (σ = median spacing) | 9 | 0.113 | 0.0492 | 0.113 | 0.049 | 0.0 % |
| stride-2 lattice | Four-quadrant 1/d² (D-1df2) | 19 | 0.117 | 0.0694 | 0.117 | 0.069 | 0.0 % |
| stride-2 lattice | Eight-neighbour IDW | 19 | 0.117 | 0.0673 | 0.117 | 0.067 | 0.0 % |
| stride-2 lattice | Gaussian (σ = median spacing) | 19 | 0.117 | 0.0660 | 0.117 | 0.066 | 0.0 % |
| random 50 % × 200 | Four-quadrant 1/d² (D-1df2) | 1000 | 0.117 | 0.0581 | 0.117 | 0.058 | 0.0 % |
| random 50 % × 200 | Eight-neighbour IDW | 1000 | 0.117 | 0.0513 | 0.117 | 0.051 | 0.0 % |
| random 50 % × 200 | Gaussian (σ = median spacing) | 1000 | 0.117 | 0.0517 | 0.117 | 0.052 | 0.0 % |

**supplement_9km (beyond contract)** — 81 truth cells, 81 feasible

| Protocol | Method | n pred | max \|e\| (both feasible) | RMSE (both feasible) | max \|e\| (all, infeasible = 0) | RMSE (all) | feasible mismatch |
|---|---|---|---|---|---|---|---|
| leave-one-out | Four-quadrant 1/d² (D-1df2) | 81 | 0.117 | 0.0356 | 0.117 | 0.036 | 0.0 % |
| leave-one-out | Eight-neighbour IDW | 81 | 0.117 | 0.0332 | 0.117 | 0.033 | 0.0 % |
| leave-one-out | Gaussian (σ = median spacing) | 81 | 0.116 | 0.0337 | 0.116 | 0.034 | 0.0 % |
| stride-2 lattice | Four-quadrant 1/d² (D-1df2) | 243 | 0.117 | 0.0357 | 0.117 | 0.036 | 0.0 % |
| stride-2 lattice | Eight-neighbour IDW | 243 | 0.117 | 0.0357 | 0.117 | 0.036 | 0.0 % |
| stride-2 lattice | Gaussian (σ = median spacing) | 243 | 0.108 | 0.0372 | 0.108 | 0.037 | 0.0 % |
| random 50 % × 200 | Four-quadrant 1/d² (D-1df2) | 8200 | 0.117 | 0.0369 | 0.117 | 0.037 | 0.0 % |
| random 50 % × 200 | Eight-neighbour IDW | 8200 | 0.117 | 0.0355 | 0.117 | 0.036 | 0.0 % |
| random 50 % × 200 | Gaussian (σ = median spacing) | 8200 | 0.117 | 0.0355 | 0.117 | 0.035 | 0.0 % |

#### `fixed_window_mixed` — `dte_relay_priority`, one mixed-feasibility window

Truth feasible in 5 of 9 cells (primary) and 54 of 81 (supplement).

**primary_3km (contract region)** — 9 truth cells, 5 feasible

| Protocol | Method | n pred | max \|e\| (both feasible) | RMSE (both feasible) | max \|e\| (all, infeasible = 0) | RMSE (all) | feasible mismatch |
|---|---|---|---|---|---|---|---|
| leave-one-out | Four-quadrant 1/d² (D-1df2) | 9 | 0.060 | 0.0291 | 1.250 | 0.705 | 33.3 % |
| leave-one-out | Eight-neighbour IDW | 9 | 0.060 | 0.0306 | 1.236 | 0.819 | 22.2 % |
| leave-one-out | Gaussian (σ = median spacing) | 9 | 0.060 | 0.0310 | 1.232 | 0.817 | 22.2 % |
| stride-2 lattice | Four-quadrant 1/d² (D-1df2) | 19 | 0.060 | 0.0327 | 1.250 | 0.642 | 26.3 % |
| stride-2 lattice | Eight-neighbour IDW | 19 | 0.060 | 0.0327 | 1.250 | 0.811 | 26.3 % |
| stride-2 lattice | Gaussian (σ = median spacing) | 19 | 0.060 | 0.0327 | 1.250 | 0.811 | 26.3 % |
| random 50 % × 200 | Four-quadrant 1/d² (D-1df2) | 1000 | 0.060 | 0.0323 | 1.250 | 0.736 | 33.9 % |
| random 50 % × 200 | Eight-neighbour IDW | 1000 | 0.060 | 0.0314 | 1.250 | 0.827 | 36.8 % |
| random 50 % × 200 | Gaussian (σ = median spacing) | 1000 | 0.060 | 0.0322 | 1.250 | 0.826 | 36.8 % |

**supplement_9km (beyond contract)** — 81 truth cells, 54 feasible

| Protocol | Method | n pred | max \|e\| (both feasible) | RMSE (both feasible) | max \|e\| (all, infeasible = 0) | RMSE (all) | feasible mismatch |
|---|---|---|---|---|---|---|---|
| leave-one-out | Four-quadrant 1/d² (D-1df2) | 81 | 0.119 | 0.0352 | 1.250 | 0.513 | 11.1 % |
| leave-one-out | Eight-neighbour IDW | 81 | 0.099 | 0.0318 | 1.230 | 0.652 | 13.6 % |
| leave-one-out | Gaussian (σ = median spacing) | 81 | 0.097 | 0.0307 | 1.228 | 0.667 | 13.6 % |
| stride-2 lattice | Four-quadrant 1/d² (D-1df2) | 243 | 0.119 | 0.0351 | 1.250 | 0.546 | 19.3 % |
| stride-2 lattice | Eight-neighbour IDW | 243 | 0.119 | 0.0332 | 1.250 | 0.682 | 19.3 % |
| stride-2 lattice | Gaussian (σ = median spacing) | 243 | 0.119 | 0.0324 | 1.250 | 0.685 | 20.6 % |
| random 50 % × 200 | Four-quadrant 1/d² (D-1df2) | 8200 | 0.119 | 0.0340 | 1.250 | 0.548 | 15.5 % |
| random 50 % × 200 | Eight-neighbour IDW | 8200 | 0.119 | 0.0323 | 1.250 | 0.659 | 16.0 % |
| random 50 % × 200 | Gaussian (σ = median spacing) | 8200 | 0.119 | 0.0321 | 1.250 | 0.664 | 15.6 % |

#### Reading the numbers (descriptive only)

- On `map_best_window`, differences between the methods are small (RMSE 0.033–0.069; max \|e\| 0.108–0.117, nearly identical across methods).
- On `fixed_window_mixed`, feasible mismatch is 11–37 % depending on region and protocol, and the ranking of the three methods changes with protocol and region (for example in the 9 × 9 km leave-one-out run the quadrant method has the lowest mismatch, 11.1 % vs 13.6 %, and the highest both-feasible `max |e|`, 0.119 vs 0.099 and 0.097; in the 3 km leave-one-out run its mismatch is the highest, 33.3 % vs 22.2 %). No single method wins every column.
- Sample size is small: the 3 km square has only 9 cap cells, so primary-region figures are coarse; random-protocol rows reuse the same 9 (or 81) truth cells across trials and are not independent samples.
- Picking the winning metric (max error vs RMSE vs feasible mismatch) is the open follow-up of `D-b4ca`.

#### Limits

- Cap cells only (1 km, `cap_1km` tile masks); the finer 5 m Site01 DEM mask was not used for truth.
- Hazards off; one template per truth configuration; January 2027 windows only.
- `fixed_window_mixed` window and template were chosen to obtain mixed feasibility (selection rule above), not drawn from a representative search.
