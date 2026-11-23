---
id: D-20261123-pj-6bf5
title: "Drop lon-pad criba; keep lat-pad for now; membership oracle unchanged"
date: 2026-11-23T09:06:13Z
author: pj
decided-by: pj
status: accepted
mode: own
domain: method & validation
task: T-20261122-pj-b94d
concepts: [footprint prefilter completeness, region selection geometry]
supersedes: [D-20261122-pj-c1ed]
relates: [D-20261122-pj-c898, D-20261122-pj-3e10]
ai: options+critique
---
# Drop lon-pad criba; keep lat-pad for now; membership oracle unchanged

## Context

`D-c898` required oracle-first selection; `D-c1ed` required measuring remaining center-based cribas before keep/drop. Bench `scripts/bench_selector_cribas.py` (2026-11-22): lat_pad candidates showed **0** oracle omissions across the suite; lon_pad omitted valid footprint-touching cells (auditor probe FAIL; e.g. auditor-lon100 23 omissions). Full oracle scans were ~1–4 s median vs masked paths in tens of ms; search evaluate cost still dominates (`D-c898`).

## Framing

Precision of the cell set over selection speed; use measured omission counts, not intuition.

## Options considered

1. **A — Drop lon_pad; keep lat_pad for now; keep footprint membership function**: assumes lat pad is precise enough in the measured suite and lon pad is not; consequence — remove lon_mask from production; broaden lat benches later.
2. **B — Drop both masks; full-index intersect always**.
3. **C — Keep both; only widen lon_pad**.
4. **Other / none**

## Decision

**A — Remove the longitude center-pad criba from production. Keep the latitude center-pad criba for now. Leave `_footprint_intersects_latlon_rect` as the membership check (no keep/drop change to sampling policy in this record).**

## Rationale

Dropping B and keeping A is simply because the tests showed A is precise and B leaves cases out.

## Checks raised

- Would be wrong if dropping lon_pad made computation notably slower → pj: (1) precision already preferred to speed; (2) measured time difference is not especially large.

## Values

| Name | Value | Notes |
|------|-------|-------|
| selector_criba_lon_pad_policy | removed_from_production | Was deferred in `D-c1ed` |
| selector_criba_lat_pad_policy | keep_for_now_pending_broader_bench | Broader cases later |
| selector_footprint_intersect_sampling_policy | unchanged_membership_oracle | Deeper sampling study not opened here |
| selector_criba_investigation | measure_precision_and_wall_time_like_aabb | Satisfied for this keep/drop |

## Expected behavior and validation

It would be wrong if this made the computation notably slower — but (1) we already defined that we prefer precision to speed and (2) we tested it and the time difference is not especially large.

## Consequences

- Build: delete or bypass `lon_mask` in `sites_in_latlon_rect`; candidates from lat_mask (or full index if lat also removed later) then footprint intersect.
- Add/adjust tests for the auditor lon-boundary case (must include touching cells).
- Schedule a broader lat-pad bench suite as follow-up; do not treat current lat suite as final forever.
