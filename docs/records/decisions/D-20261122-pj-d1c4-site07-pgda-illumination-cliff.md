---
id: D-20261122-pj-d1c4
title: "Site07: document PGDA 69 illumination cliff; short-night cap gap noted"
date: 2026-11-22T17:12:00Z
author: pj
decided-by: pj
status: accepted
mode: own
domain: claims & interpretation
task: T-20261122-pj-b94d
concepts: [PGDA 69 averages, PGDA 78 site DEMs]
supersedes: []
relates: [D-20261122-pj-f8c2, D-20261122-pj-6dc3, D-20261115-pj-9ab3, D-20261122-pj-1a2d]
ai: exposition+record
---
# Site07: document PGDA 69 illumination cliff; short-night cap gap noted

## Context

2026-11-22 validation placed **Site07** at lat **−88.811°**, lon **123.690°** (Horizons fixture + PGDA-78 5 m DEM `Site07_final_adj_5mpp_surf.tif` centroid). Fine horizon elevations stay **&lt; ~1.3°** (very open sky). Over the PGDA nutation span our mean sun fraction is **~67 %**. The PGDA 69 **85°S 60 m** map shows **~17 %** at the centre cell and **~42–86 %** in the eight neighbours (illumination **cliff** at posting scale). Short-night re-check: cap 1 km **underestimates** longest night by **8 h** vs 5 m in 2027 (`D-1a2d` document-only).

## Framing

Record a known limitation of **point + coarse map** interpretation at this location; do not treat Site07 as certification failure of the whole engine. pj defers heavy terrain/product fixes (~2 months).

## Options considered

1. **S1 — Document cliff + adopt map window mean (`D-f8c2`); keep Site07 in the PGDA-78 set.**
2. **S2 — Exclude Site07 from soft-claim set until PGDA-78 catalogue name/coords are re-verified.**
3. **S3 — Drop Site07 from all S12 tables.**

## Decision

**S1.** Keep **Site07** in the PGDA-78 S12 set. Publish in **`docs/validation.md`** a **Site07 note**: coarse PGDA 69 posting cliff; cite centre vs window mean and neighbour range; 5 m horizon very open; short-night **8 h** cap gap cross-ref. After **`D-f8c2` re-run**, use updated Δ for soft-claim (`D-6dc3`). **No** automatic README agreement claim regardless until pj reviews the new table.

**Catalog name:** optional follow-up (`D-d1c4-catalog`) — not required for this decision.

## Rationale

pj: protocol fix first; document anomaly; avoid spending long-term quality work in this pass.

## Provenance

| Who | Contribution |
|-----|----------------|
| **pj** | Accept documentation + window mean; defer product mesh work. |
| **ai** | Measured 5×5 PGDA neighbourhood and horizon stats (2026-11-22 WSL). |

## Values

| Name | Value | Notes |
|------|-------|-------|
| site07_pgda_cliff | documented | validation.md PGDA section |
| site07_short_night_cap_error_h | 8 | 2027, document-only |
| site07_pgda78_dem | Site07_final_adj_5mpp_surf.tif | Fixture id, not NASA prose name |
| site07_catalog_verify | deferred | See optional follow-up in validation.md |

## Expected behavior and validation

Wrong if Site07 is silently dropped from tables or if centre-pixel-only map values remain in validation.md after `D-f8c2` is implemented.

## Consequences

- validation.md gains a Site07 subsection under PGDA results.
- README “Site07 follow-up” may narrow to catalog verify only if soft claim passes after re-run.