---
id: D-20261122-pj-c1ed
title: "Measure remaining selector cribas (precision + time) before keep/drop"
date: 2026-11-22T19:02:06Z
author: pj
decided-by: pj
status: accepted
mode: own
domain: method & validation
task: T-20261122-pj-b94d
concepts: [footprint prefilter completeness, region selection geometry]
supersedes: []
relates: [D-20261122-pj-c898, D-20261122-pj-3e10]
ai: options+critique
---
# Measure remaining selector cribas (precision + time) before keep/drop

## Context

`D-c898` deprecated the xy corner AABB after timing and correctness evidence. Production `sites_in_latlon_rect` still applies center-based `lat_mask` / `lon_pad` candidate masks before `_footprint_intersects_latlon_rect`; the independent auditor showed the lon mask can drop footprint-touching cells. pj (2026-11-22) refuses a keep/drop call without the same class of evidence used for AABB.

## Framing

Data before policy: quantify precision and real time savings of each remaining criba; then decide.

## Options considered

1. **A — Measure the three like AABB (precision + wall time), then decide keep/drop**: inventory = lat pad mask, lon pad mask, and footprint-intersection sampling; production keep/drop deferred until numbers exist.
2. **B — Remove all production candidate masks now**: precision first; no study.
3. **C — Only auditor repro + lon patch; leave the other two unmeasured**.
4. **Other / none**

## Decision

**A — Measure first; decide keep/drop after the data.**

## Rationale

We will review the three the way we did with the AABB: testing extensively what their precision is and how much time they actually save. Once we have those data, we decide. The falsifiable decision is the one we take once we have seen the tests. For now we are investigating.

## Checks raised

- Auditor item 2 stays open until the post-measurement decision → accepted.
- No silent default that current masks stay in production → keep/drop values deferred.

## Values

| Name | Value | Notes |
|------|-------|-------|
| selector_criba_lat_pad_policy | deferred — after precision+timing harness on pj machine | |
| selector_criba_lon_pad_policy | deferred — after precision+timing harness on pj machine | |
| selector_footprint_intersect_sampling_policy | deferred — after precision+timing harness on pj machine | |
| selector_criba_investigation | measure_precision_and_wall_time_like_aabb | lat_mask, lon_mask, `_footprint_intersects_latlon_rect` |
| selector_criba_inventory | lat_pad_0.05_center; lon_pad_2_center; footprint_intersect_fn | as of 2026-11-22 code |

## Expected behavior and validation

The falsifiable decision is the one we take once we have seen the tests. For now we are investigating.

## Consequences

- Build may add a measurement/property harness (and failing completeness probes that document omissions) citing this ID.
- Must not permanently keep or remove cribas under a silent default; a superseding decide pass records keep/drop after numbers.
- Does not reopen `D-c898` xy AABB deprecation.
