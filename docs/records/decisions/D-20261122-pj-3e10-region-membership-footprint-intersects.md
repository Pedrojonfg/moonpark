---
id: D-20261122-pj-3e10
title: "Regional search membership: include cap cells whose footprint intersects the user rectangle"
date: 2026-11-22T11:32:38Z
author: pj
decided-by: pj
status: accepted
mode: own
domain: method & validation
task: T-20261122-pj-b94d
concepts: [cap grid membership, region selection geometry]
supersedes: []
relates: [D-20261115-pj-c159, D-20261114-pj-f369, D-20261115-pj-54f0, D-20261122-pj-ae04]
ai: none
---
# Regional search membership: include cap cells whose footprint intersects the user rectangle

## Context

Deep search over a user lat/lon rectangle snaps to the 1 km cap index (`D-c159`, `D-f369`). Selection today uses a stereographic xy pre-filter (`cap_index.sites_in_latlon_rect`) then lat/lon checks. Task `T-20261122-pj-b94d` closes audit item 1: the selected cell set must match a reference scan and must not drop valid cells. pj defined how a cell qualifies for membership in the search domain.

## Framing

Prefer computing too many cells over too few; complement with boundary disclosure in results (`D-20261122-pj-ae04`) and the interactive map so users are not forced to accept extra cells.

## Options considered

pj answered directly in conversation (2026-11-22); no options table was shown before the choice.

1. **Center inside rectangle only** — stricter, faster; risk of missing cells that only touch the zone via their footprint.
2. **Center inside or footprint intersects rectangle** — conservative membership; more compute; pairs with boundary warnings.

## Decision

**2 — Center inside or cap-cell footprint intersects/touches the user rectangle boundary (inclusive on the user side).**

## Rationale

(Translated from pj's Spanish.) Membership should include any cell whose footprint touches or intersects the rectangle border so we include all points of the rectangle. Better to compute too many than too few. If the user does not want a boundary cell, we warn that it is a frontier cell; they can choose any other result and use the interactive map to select points they want. We are not forcing them; it is an extra option that is good to offer.

## Provenance

| Who | Contribution |
|-----|----------------|
| **pj** | Membership rule, over-inclusion preference, 1 km axis-aligned footprint (no Voronoi v1); criterion from audit §1. |
| **ai** | Teaching PDF `region-selection-geometry`; option labels for the record only. |

## Checks raised

- Including extra cells wastes compute and can lengthen searches → pj accepts; the user can ignore boundary winners.
- Would be wrong if the footprint model is vague and nearly everything is labeled boundary → footprint geometry must be pinned when built (see Values).
- Fast xy pre-filter must still return the same set as a full-index reference applying this rule → equivalence tests required (audit item 1).
- Falsification (pj, 2026-11-22): choice would be wrong mainly if neighbor induction for boundary readouts is very bad, or users report they dislike or do not understand it; very high compute cost would also falsify it — pj does not expect cost to dominate.

## Values

| Name | Value | Notes |
|------|-------|-------|
| region_membership_rule | center_inside_or_footprint_intersects_rect | Conservative; overlaps rectangle interior and boundary |
| region_membership_preference | prefer_over_inclusion | Deliberate trade for reliability |
| footprint_geometry | axis_aligned_1km_cell_centered_on_index_node | pj (2026-11-22): equispaced cap grid ≡ practical 1 km cells; intersect user lat/lon rect → include; no Voronoi diagram in v1 |
| cap_grid_spacing_m | 1000 | From `D-f369` cap precompute; smaller grid deferred until finer masks product decision |
| reference_oracle | full_index_scan_with_same_membership_rule | Property test: fast selector ≡ oracle |

## Expected behavior and validation

- Any implementation of rectangle→cell list (including current xy pre-filter) must match the oracle set for all v1 rectangles in scope.
- Search and map treat membership consistently with this rule.
- Boundary cells carry disclosure per `D-20261122-pj-ae04`.

## Consequences

- Update selection logic and tests on audit reliability work; do not implement here.
- `D-c159` domain meaning is unchanged at intent (“whole user zone”); membership is now explicit at cell-footprint level.