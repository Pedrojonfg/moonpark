---
id: D-20261122-pj-7c4e
title: "Single evaluate path for /site and deep-search; finest mask when available"
date: 2026-11-22T13:20:00Z
author: pj
decided-by: pj
status: accepted
mode: own
domain: method & validation
task: T-20261122-pj-b94d
concepts: [planner contract duplication, effective requirements]
supersedes: []
relates: [D-20261118-pj-75f1, D-20261114-pj-aa58, D-20261115-pj-c159, D-20261122-pj-7bd7, D-20261118-pj-b3dc]
ai: exposition+record
---
# Single evaluate path for /site and deep-search; finest mask when available

## Context

Audit §7: `/site` builds results through `build_planner_payload` (`moonpark/planner_payload.py`); `/deep-search` scores cells via an inline `evaluate()` closure in `moonpark/api/app.py` that duplicates visibility, hazards, needs shaping, and `score()` wiring. `D-75f1` aligned **requirements** across searches; the **computation path** can still drift. Today deep-search uses `mask_from_cap_tile` per index cell while `/site` uses `mask_for_site` (finer DEM/mask when on disk). pj (2026-11-22): one calculation site only, no copied logic; same recipe everywhere; use the **finest mask available** in both flows when data exists.

## Framing

Search and single-site analysis must not disagree because two codepaths diverged.

## Decision

1. **One implementation** of “evaluate this `Site` over this time window with these needs and flags” — extracted from the duplicated pieces of `build_planner_payload` and `app.py` `evaluate()`. `/site` and `/deep-search` **call only that module** (no parallel copies in `app.py`).
2. **`build_planner_payload`** becomes a thin wrapper: parse/window/local_search extras stay there; core site evaluation delegates to the shared function.
3. **Mask policy (both paths):** use **`mask_for_site`** (or a single shared helper with the same rules): finest available mask on disk for the site/cell coordinates — cap tile only when nothing finer exists. Deep-search **does not** hard-code `mask_from_cap_tile` for scoring; cap index remains for **which cells** are in the region (`D-c159`), not for forcing a coarser horizon at evaluate time.
4. **Parity validation:** automated test(s): same `Site`, window, `step_min`, needs, hazards flag → same feasible/score/hazard_gap_star (and key series fields) whether invoked via shared evaluate directly or via `/site` JSON path; deep-search leaderboard row for that site must match within documented tolerance.

## Rationale

(Translated from pj's Spanish, 2026-11-22.) Force calculation in a single place; call it so there is no copy of anything. Same recipe; in both cases use the finer map when available.

## Provenance

| Who | Contribution |
|-----|----------------|
| **pj** | Mandatory single evaluate path; finest mask when possible in site and regional search. |
| **ai** | Located duplication (`app.py` vs `planner_payload`); linked cap tile vs `mask_for_site` behavior. |

## Values

| Name | Value |
|------|-------|
| evaluate_impl | single_shared_module |
| app_py_evaluate_closure | removed_replaced_by_shared_call |
| deep_search_mask_at_evaluate | finest_available_via_mask_for_site |
| cap_tile_mask | region_membership_and_fallback_only |
| site_deep_score_parity_test | required_in_regression_ci |
| local_search_extra | stays in build_planner_payload_wrapper |

## Expected behavior and validation

Wrong: `/deep-search` scores with cap tile while `/site` at the same lat/lon uses fine mask and scores differ without disclosure.
Wrong: hazard or energy fix in only one of `app.py` or `planner_payload` without touching the shared function.

## Consequences

- New or refactored module (e.g. `moonpark/evaluate.py` or `planner_payload.evaluate_site_window`) imported by `app.py` and `planner_payload.py`.
- Remove `_evaluation_needs` duplication where the shared path derives score needs once.
- Deep-search may cost more per cell when fine masks load; accepted under `D-75f1` / honesty over silent coarse shortcut.
- Part of the same reliability build pass as §1–§6 implementation.