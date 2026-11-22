---
id: D-20261122-pj-ae04
title: "Boundary search results: always disclose; no mandatory finer-mask refine in v1"
date: 2026-11-22T11:32:39Z
author: pj
decided-by: pj
status: accepted
mode: own
domain: claims & interpretation
task: T-20261122-pj-b94d
concepts: [boundary cell disclosure, cap grid membership]
supersedes: []
relates: [D-20261122-pj-3e10, D-20261122-pj-d254, D-20261116-pj-1df2, D-20261115-pj-85bf, D-20261116-pj-2325, D-20261115-pj-a988]
ai: none
---
# Boundary search results: always disclose; no mandatory finer-mask refine in v1

## Context

Conservative region membership (`D-20261122-pj-3e10`) adds cells at the rectangle edge. pj set how results and UI should treat those cells, especially scores and feasibility readouts. Finer terrain/mask resolution is not always available at runtime (`D-c4e8`: cap cells without local DEMs; mask schedule `D-f369`).

## Framing

Honest, visible disclosure without blocking the UI; user choice via map and leaderboard, not engine-forced exclusion.

## Options considered

pj answered directly (2026-11-22).

1. **Mandatory finer-mask re-evaluate at boundary winners** — stronger science; pj doubts viability today because finer masks are not guaranteed on demand.
2. **Always flag boundary cells; explain values via existing neighborhood induction/interpolation; user picks another row if they dislike it** — matches current data and map interpolation records.

## Decision

**2 for v1.** Always warn on boundary/frontera cells in results (discrete but explicit). Do not require automatic finer-mask refinement. When a boundary point is shown, state that its value is induced from nearby cells using the project's existing induction/interpolation methods; let the user choose another candidate or map selection.

## Rationale

(Translated from pj's Spanish.) Always warn in results: discrete, not covering the whole UI, but explicit enough. On refine: finer masks depend on what mask data exist; it does not seem viable today to assume a finer level is always there — when masks are finer, those are what we use to compute, not an on-demand extra tier. So simply warn that the frontier cell's value was induced from the nearest cell(s) or whatever method we already defined for induction. Use those methods. Then they choose what they want.

## Provenance

| Who | Contribution |
|-----|----------------|
| **pj** | Warn always; no mandatory finer-mask refine in v1; user picks another row or map point. |
| **ai** | Linked to `D-c4e8` / mask schedule constraints in Context. |

## Checks raised

- User treats induced boundary score as measured → mitigated by always-on boundary flag and existing estimate copy (`D-20261116-pj-1df2`).
- Would be wrong if warnings are so quiet they are ignored → UI must be explicit enough (deferred: exact component/copy in presentation pass).
- Audit “refine at boundary” in the strongest sense → deferred until finer masks are a guaranteed store artifact, not v1.
- Falsification (pj, 2026-11-22): same as `D-3e10` — wrong if induction at boundaries is very bad, if users do not understand or dislike the warnings, or if cost blows up (pj: cost unlikely to be the main risk).

## Values

| Name | Value | Notes |
|------|-------|-------|
| boundary_cell_warning | always | Search/leaderboard/saved result metadata |
| boundary_ui_style | discrete_explicit | Must not dominate layout |
| boundary_refine_finer_mask | not_required_v1 | Revisit when finer resolution is always available |
| boundary_value_source | induced_from_neighbors | Reuse recorded interpolation/induction rules (`D-affb`, estimate layer `D-1df2`; partial-search induce rules as applicable) |
| user_override | map_and_leaderboard | No force to accept boundary winner |

## Expected behavior and validation

- Any ranked row that is a membership boundary cell carries a visible frontier/boundary indicator and induced-source wording in provenance.
- Tests: deliberate boundary winner must show flag; no silent presentation as fully evaluated at sub-cell precision.

## Consequences

- Product/README claims must not imply sub-cell boundary refinement in v1.
- Implementation ties to search export rows and planner/map UI; build follows equivalence work for membership (`D-3e10`).