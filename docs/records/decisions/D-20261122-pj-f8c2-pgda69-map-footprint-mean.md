---
id: D-20261122-pj-f8c2
title: "S12 PGDA 69 reference map: mean over PGDA posting window, not centre-pixel only"
date: 2026-11-22T17:10:00Z
author: pj
decided-by: pj
status: accepted
mode: own
domain: method & validation
task: T-20261122-pj-b94d
concepts: [PGDA 69 averages, illumination metrics]
supersedes: []
relates: [D-20261115-pj-9ab3, D-20261122-pj-6dc3, D-20261122-pj-d1c4]
ai: exposition+record
---
# S12 PGDA 69 reference map: mean over PGDA posting window, not centre-pixel only

## Context

The S12 PGDA 69 harness (`D-9ab3`) sampled one raster cell at the site lat/lon. On **Site07** (2026-11-22 run) that centre cell read **~17 %** while adjacent 60 m cells reached **~70 %** and our 5 m horizon mean was **~67 %**. The soft-claim gate (`D-6dc3`) failed mainly on that outlier. pj (2026-11-22): treat coarse-data quality as a short-term issue (~2 months); fix the **comparison protocol** so one unrepresentative centre pixel cannot dominate the table. Do not spend a large effort on terrain/product upgrades in this task.

## Framing

Fair reference value for a **point** fine DEM observer against a **posted** PGDA 69 grid: use a small neighbourhood mean at the map’s native posting, not a single pixel that may sit on an illumination cliff.

## Options considered

1. **F1 — Centre pixel only** (previous implicit behaviour).
2. **F2 — Mean over a fixed odd window of PGDA cells** centred on the site stereographic location (recommended).
3. **F3 — Mean over the entire 16 km × 16 km PGDA-78 DEM extent** (heavy, unnecessary for v1).

## Decision

**F2.** For each PGDA-78 validation site, the **map reference** is the **arithmetic mean** of valid PGDA 69 illumination values in a **5×5 cell window** (radius **2** cells in row/col) centred on the site’s polar-stereo grid cell. **Invalid/nodata cells are excluded** from the mean; if fewer than **9** valid cells remain, still report the mean of what is valid and set `map_status` to `partial_window`. The harness also records **`pgda_fraction_point`** (former centre pixel) for diagnosis. **Δ (pp)** for reports and **`D-6dc3`** use **ours − map mean** (`pgda_fraction`).

## Rationale

pj: avoid a lone bad sample destroying the validation row; keep compute trivial; defer fine product/mesh work.

## Provenance

| Who | Contribution |
|-----|----------------|
| **pj** | Chose footprint mean over centre pixel; limit scope. |
| **ai** | Site07 cliff diagnosis; proposed 5×5 @ 60 m posting. |

## Checks raised

- Neighbourhood mean does not fix true model error; it only aligns reference scale with posting.
- `D-9ab3` span and light definition unchanged.

## Values

| Name | Value | Notes |
|------|-------|-------|
| s12_pgda69_map_sample | window_mean | Replaces implicit centre-pixel |
| s12_pgda69_map_radius_cells | 2 | 5×5 window |
| s12_pgda69_map_metric_primary | pgda_fraction_mean | Used for Δ and soft claim |
| s12_pgda69_map_metric_diagnostic | pgda_fraction_point | Logged per site |
| s12_pgda69_map_min_valid_cells | 9 | Below → partial_window still OK |

## Expected behavior and validation

Wrong if `docs/validation.md` or the harness JSON claims agreement using centre-pixel map values while `D-f8c2` is accepted. Re-run PGDA compare after implementation and refresh validation.md.

## Consequences

- `scripts/s12_validation_lib.py` and `s12_pgda69_compare.py` implement the window mean.
- `D-9ab3` Values row `s12_pgda69_metric` pairing: map side uses footprint mean (`D-f8c2`); ours unchanged.