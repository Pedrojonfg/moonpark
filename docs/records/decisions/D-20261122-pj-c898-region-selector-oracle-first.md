---
id: D-20261122-pj-c898
title: "Region cell selection: oracle-first; deprecate xy AABB shortcut for v1"
date: 2026-11-22T11:56:22Z
author: pj
decided-by: pj
status: accepted
mode: advise
domain: method & validation
task: T-20261122-pj-b94d
concepts: [region selection geometry, cap grid membership]
supersedes: []
relates: [D-20261122-pj-3e10, D-20261115-pj-c159]
ai: options+critique
---
# Region cell selection: oracle-first; deprecate xy AABB shortcut for v1

## Context

Audit item 1 and `D-3e10` need a selector that returns exactly the membership set (1 km grid cell intersects user lat/lon rectangle). Current `sites_in_latlon_rect` uses a stereographic corner AABB pre-filter that can omit valid cells (pole / wide lon). pj (2026-11-22): precision is mandatory; the product targets capable desktops; even on pj's modest machine the shortcut's time savings are irrelevant next to search evaluation cost, while the shortcut adds correctness risk and scales poorly on large cell lists.

### Measurements (pj's machine, 2026-11-22; 290289 cap index rows)

| Step | Typical time | Notes |
|------|----------------|-------|
| Load `index.parquet` (cold process) | ~13.5 s | Once per process; `lru_cache` after |
| **Current xy AABB path** — half-cap rect (~145k cells out) | ~**1.73 s** | Dominated by building Python/`Site` list, not numpy alone |
| **Vectorized lat/lon filter** — same half-cap (center-in-rect baseline) | ~**12 ms** | Boolean mask only |
| Vectorized lat filter on full cap | ~0.6 ms | 290k rows |
| Deep search evaluate (reference) | minutes–hours | e.g. 10k cells × 168 starts ≈ 19 min (`docs/limits.md`); dominates wall time |

So the corner AABB "shortcut" is **slower than a straight scan** on a large region on this hardware, while still carrying geometric omission risk. Selection is **not** the bottleneck; `evaluate` is.

## Framing

Maximize correctness of the cell set; do not optimize selection until equivalence is proven and a measurable win exists.

## Options considered

1. **Oracle-first** — scan index (or vectorized columns) with the recorded membership rule; drop xy AABB from production paths.
2. **Keep xy pre-filter** — only if a property test proves identical sets to the oracle on the v1 rectangle family; otherwise refuse the shortcut.
3. **Tune the corner AABB** — pj rejected as primary path: without proof it risks silent omission; tuning cost is unjustified while the oracle is fast enough.

## Decision

**Oracle-first for v1; deprecate the xy corner AABB for production.** Implement membership as a full-index algorithm per `D-3e10`. Do not ship the current `sites_in_latlon_rect` corner path for user-facing selection. A fast path may be revisited in a future version only with provable set equality and a measured win; not in v1.

## Rationale

(Translated from pj's Spanish, 2026-11-22.) The product targets good computers; even on pj's slow machine, the shortcut saves negligible time while precision is mandatory. The shortcut scales badly and may be wrong — not worth it to save time that does not matter. Revisit in future versions if it becomes interesting; for now deprecate it.

## Provenance

| Who | Contribution |
|-----|----------------|
| **pj** | Precision mandatory; oracle-first for v1; deprecate xy AABB for production after understanding cost vs evaluate. |
| **ai** | Timing table on pj's machine; options 1–3 for the record; drafted measurements section. |

## Checks raised

- Would be wrong if oracle materializing 145k+ `Site` rows adds unacceptable latency → measure in build; mask build may dominate; separate from mask boolean filter.
- Pole/wide-lon rectangles must use the same membership rule, not the broken corner collapse → oracle must implement the rule directly.

## Values

| Name | Value | Notes |
|------|-------|-------|
| region_selector_production | oracle_full_index | Membership rule from `D-3e10` |
| region_selector_xy_aabb | deprecated_v1 | Not used in production; may revisit with proof + measured win |
| selector_equivalence_required | exact set equality | Required before any future fast path ships |
| selector_performance_gate | not_met_v1 | AABB slower than scan on large regions on measured hardware |

## Expected behavior and validation

- Property tests: oracle vs any fast path on a generated rectangle suite including poles and lon wrap.
- User-facing deep search and APIs that list region cells call the oracle implementation.

## Consequences

- Replace or bypass `sites_in_latlon_rect` corner path in production; keep implementation only for regression comparison until removed.
- Build task for audit item 1 implements oracle + tests first; no shortcut maintenance in v1.