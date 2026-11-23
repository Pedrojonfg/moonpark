---
id: D-20261123-pj-3f81
title: "Keep four-quadrant estimate; judge benches by feasible mismatch then RMSE then max |e|"
date: 2026-11-23T08:46:20Z
author: pj
decided-by: pj
status: accepted
mode: own
domain: method & validation
task: T-20261122-pj-b94d
concepts: [evidence-gated validation, smooth fill inventing mid-scores between sparse points]
supersedes: [D-20261122-pj-b4ca]
relates: [D-20261116-pj-1df2]
ai: options+critique
---
# Keep four-quadrant estimate; judge benches by feasible mismatch then RMSE then max |e|

## Context

`D-b4ca` deferred the estimate-layer winner until a small Site01 total_coverage bench compared four-quadrant 1/d², eight-neighbour IDW, and Gaussian weights. The 2026-11-22 run (`docs/validation.md`, `logs/bench_estimate_interpolation.json`) showed small score-error gaps and no single method winning every slice; feasible-mismatch rankings flip by region/protocol.

## Framing

Choose a production estimate method and the metric order used to read such benches, under user-facing product judgment rather than a single automated ranking.

## Options considered

1. **A — Keep four-quadrant 1/d² (`D-1df2`)**: assumes bench gaps do not justify added complexity; consequence — production `web/map.js` `estimateAt` unchanged.
2. **B — Switch to eight-neighbour IDW**: assumes feasibility/RMSE edges in some slices outweigh simplicity.
3. **C — Switch to Gaussian**: assumes different weighting is worth a default change.
4. **Other / none**

## Decision

**A — Keep four-quadrant inverse-distance estimate.** Bench reading order: (1) feasible colour mismatch, (2) RMSE, (3) max |error|.

## Rationale

I think choosing quadrants is also helped by it being a simple model (and, given similar results, better simple than complex). My metric criteria relate to what I see as functionality for the user, and the first criterion must without doubt be not sending them to an infeasible site; after that I apply a “utilitarian” criterion (I do not want a large error outlier to make me pick a bad interpolation).

## Checks raised

- Metric order does not pick one method when slices disagree → resolved by simplicity + keeping `D-1df2`.
- Hard to falsify as experimental science → accepted as personal product vision (see Expected behavior).

## Values

| Name | Value | Notes |
|------|-------|-------|
| estimate_bench_winner_metric | feasible_mismatch_then_rmse_then_max_abs_error | Lexicographic preference for reading benches |
| region_map_estimate_method | four_quadrant_inverse_distance | Keeps `D-1df2` production default |
| estimate_bench_ui_change | none | No map UI change from `D-b4ca` run |

## Expected behavior and validation

In any case these decisions are hard to falsify because they are a personal vision.

## Consequences

- Closes the deferred winner of `D-b4ca` without changing production estimate code.
- Future estimate benches should report feasible mismatch, RMSE, and max |e| in that priority when summarizing.
