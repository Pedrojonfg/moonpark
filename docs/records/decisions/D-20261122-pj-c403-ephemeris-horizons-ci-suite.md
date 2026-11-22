---
id: D-20261122-pj-c403
title: "Ephemeris CI: expand Horizons comparison cases at 0.05 deg"
date: 2026-11-22T12:32:04Z
author: pj
decided-by: pj
status: accepted
mode: advise
domain: method & validation
task: T-20261122-pj-b94d
concepts: [success X/Y/Z]
supersedes: []
relates: [D-20261114-pj-4ffe, D-20261114-pj-9e53, tests/test_ephemeris.py]
ai: exposition+record
---
# Ephemeris CI: expand Horizons comparison cases at 0.05 deg

## Context

Cheap sky validation; `test_ephemeris.py` already uses 0.05 deg working bound.

## Decision

- Lock tolerance **0.05 deg** (max circular az, max el) for CI Horizons comparisons.
- **≥ 8** case blocks: existing 6 site×season windows plus **2** additional one-month windows on Site01 (2027-01 and 2027-07).
- Required in default CI when kernels and fixtures ship in repo.

## Rationale

pj (2026-11-22): many Horizons cases are OK because cost is low; keep 0.05° tolerance.

## Provenance

| Who | Contribution |
|-----|----------------|
| **pj** | Expand CI coverage; accept ≥ 8 cases at existing tolerance. |
| **ai** | Listed concrete case blocks extending `test_ephemeris.py`. |

## Values

| Name | Value |
|------|-------|
| ephemeris_horizons_tolerance_deg | 0.05 |
| ephemeris_horizons_min_cases | 8 |
| ephemeris_horizons_in_default_ci | yes |

## Consequences

- Extend `test_ephemeris.py` CASES and document in validation.md as Familia 5 row.