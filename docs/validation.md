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
