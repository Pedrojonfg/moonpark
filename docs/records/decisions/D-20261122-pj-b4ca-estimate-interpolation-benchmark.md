---
id: D-20261122-pj-b4ca
title: "Estimate layer benchmark: run multiple interpolators; defer winner until data"
date: 2026-11-22T12:32:05Z
author: pj
decided-by: pj
status: accepted
mode: own
domain: method & validation
task: T-20261122-pj-b94d
concepts: [evidence-gated validation]
supersedes: []
relates: [D-20261116-pj-1df2, D-20261114-pj-affb, D-20261115-pj-54f0]
ai: exposition+record
---
# Estimate layer benchmark: run multiple interpolators; defer winner until data

## Context

Map estimate uses four-quadrant IDW (`D-1df2`). pj wants to compare methods before changing product defaults.

## Decision

- Run a **small region** (~3 km × 3 km near Site01, total_coverage ground truth) and store per-cell errors for:
  1. Current four-quadrant 1/d² (`D-1df2`),
  2. Eight-neighbour IDW,
  3. Gaussian weights with σ = median evaluated spacing.
- Publish summary stats (max |error|, RMSE, feasible colour mismatch rate) to `validation.md` / CSV.
- **Do not** change map UI or default method until a **follow-up decision** chooses a metric (max error vs RMSE vs feasible mismatch) — **fog** that follow-up.
- pj (2026-11-22): try models without UI change now; pick later from data.

## Rationale

pj (2026-11-22): run multiple interpolators and collect numbers **without** UI/default change until a follow-up decision picks the winning metric.

## Provenance

| Who | Contribution |
|-----|----------------|
| **pj** | Compare methods before changing product; defer winner criterion to data. |
| **ai** | Suggested ~3 km² bench near Site01, three methods, validation.md outputs. |

## Values

| Name | Value |
|------|-------|
| estimate_bench_region | ~3km_square_near_site01 |
| estimate_bench_truth | total_coverage_scores |
| estimate_bench_methods | quadrant_idw, eight_neighbour_idw, gaussian_idw |
| estimate_bench_ui_change | none_until_follow_up |
| estimate_bench_winner_metric | deferred — new decision after first run |

## Expected behavior and validation

Wrong if estimate is presented as scored truth before this benchmark exists for v1 senior claims.

## Consequences

- Script + optional test marker `validation_full`; links to `D-1df2` for current production estimate.