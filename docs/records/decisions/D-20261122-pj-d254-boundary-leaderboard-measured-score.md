---
id: D-20261122-pj-d254
title: "Boundary cells in search results: measured score at the index node; interpolation only on the map layer"
date: 2026-11-22T11:51:12Z
author: pj
decided-by: pj
status: accepted
mode: own
domain: claims & interpretation
task: T-20261122-pj-b94d
concepts: [boundary cell disclosure, cap grid membership]
supersedes: []
relates: [D-20261122-pj-ae04, D-20261122-pj-3e10, D-20261116-pj-1df2, D-20261114-pj-affb]
ai: none
---
# Boundary cells in search results: measured score at the index node; interpolation only on the map layer

## Context

`D-20261122-pj-ae04` mixed domain-boundary disclosure with wording that boundary scores were "induced from neighbors". pj clarified (2026-11-22): evaluated search rows use the same full pipeline as interior cells (`evaluate` on the cap mask at the index node). Interpolation (`D-1df2`, `D-affb`) applies to map estimate pixels and temperature gaps, not to leaderboard rows that were evaluated.

## Framing

Keep claims honest: a ranked result is what the engine computed for that cell; boundary membership only adds a domain-edge warning.

## Options considered

1. **A — Measured score at the index node + boundary warning** (pj, 2026-11-22).
2. **B — Replace or blend boundary leaderboard values with neighborhood interpolation.**

## Decision

**A.** For any cell included and evaluated in a search, the reported score and feasibility are the **full computation at that index node**, same as non-boundary cells. Add an explicit **boundary / domain-edge** indicator when the cell is included only because its 1 km grid cell intersects the user rectangle edge (`D-3e10`). Do **not** replace that row with IDW or quadrant fill. Map estimate and temperature fill stay in their existing roles only.

## Rationale

(Translated from pj's Spanish.) pj confirms A: it is the most coherent and less messy.

## Provenance

| Who | Contribution |
|-----|----------------|
| **pj** | Clarification after `D-ae04` wording: leaderboard rows = full evaluate at index node; boundary flag only; no IDW on ranked rows. |
| **ai** | Split option A vs B; aligned with `D-1df2` / map estimate roles. |

## Checks raised

- User confuses map estimate colour with leaderboard score → existing estimate UX (`D-1df2`) plus boundary flag on ranked rows.
- Falsification: same as `D-ae04` / `D-3e10` — warnings ignored or domain membership misunderstood.

## Values

| Name | Value | Notes |
|------|-------|-------|
| boundary_leaderboard_score | measured_at_index_node | Same `evaluate` path as interior |
| boundary_cell_warning | always | Unchanged intent from `D-ae04` |
| boundary_row_interpolation | forbidden | No IDW on evaluated leaderboard rows |
| map_estimate_interpolation | unchanged | `D-1df2`; not a substitute for ranked rows |
| boundary_refine_finer_mask | not_required_v1 | Unchanged from `D-ae04` |

## Expected behavior and validation

- Export and UI rows for evaluated boundary cells: score from engine; `boundary_cell: true` (or equivalent); provenance must not say "induced" for the score.
- Map may still show estimate layer away from evaluated nodes.

## Consequences

- Build amends any copy tied to `D-ae04` `boundary_value_source = induced_from_neighbors` for search results; that value applies only to non-evaluated map/temperature contexts, not leaderboard.