---
id: D-20261122-pj-1a2d
title: "Short-night validation: document failures; do not reopen success_y"
date: 2026-11-22T12:32:01Z
author: pj
decided-by: pj
status: accepted
mode: own
domain: method & validation
task: T-20261122-pj-b94d
concepts: [short-night regime, evidence-gated validation]
supersedes: []
relates: [D-20261115-pj-39f3, D-20261114-pj-f369, D-20261115-pj-1a9e]
ai: options+critique
---
# Short-night validation: document failures; do not reopen success_y

## Context

`D-39f3` required reopening success_y if short-night schedule-vs-fine error exceeded 5 h. pj (2026-11-22) treats poor short-night results as a **temporary** gap until finer masks ship in the data API; changing success criteria now would not help within ~two months.

## Framing

Measure and disclose schedule error in VIPER-like nights; fix via better masks later, not by silent formula churn.

## Options considered

1. Reopen Y on >5 h (`D-39f3`).
2. **Document only**; keep Y until mask quality improves (pj, 2026-11-22).

## Decision

**2.** Run the short-night report per `D-39f3` sites/metrics/tolerance, but on **>5 h** absolute error in longest night: **record in validation.md and README limitations only**; **do not** automatically reopen or change `success_y`.

## Rationale

(Translated from pj's Spanish.) For now we document; it is a temporary problem — the plan is to improve mask quality in the API. It does not make sense to kill ourselves improving precision that will not matter in two months.

## Provenance

| Who | Contribution |
|-----|----------------|
| **pj** | Option **document only**, no auto reopen of `success_y`; masks in API will improve on a ~two-month horizon. |
| **ai** | Framed option 1 vs 2 against `D-39f3`; recorded decision. |

## Checks raised

- Claims implying Y covers short nights while report shows >5 h → forbidden under `D-de70`.

## Values

| Name | Value | Notes |
|------|-------|-------|
| s12_short_night_year | 2027 | pj |
| s12_short_night_sites | site01_plus_pgda78_40_80h_else_shortest | Per `D-39f3` |
| s12_short_night_tolerance_h | 5 | Report reference, not auto Y change |
| s12_short_night_bridge_h | 5 | Per `D-39f3` |
| s12_short_night_reference | fine_5m_mask | vs production schedule |
| s12_short_night_on_fail | document_only | Supersedes `D-39f3` `s12_short_night_on_fail` intent for now |
| s12_short_night_reopen_y | deferred | Revisit when finer masks are default in store/API |

## Expected behavior and validation

Wrong if >5 h errors are hidden or README still implies full short-night guarantee without a limitation note.

## Consequences

- Event: `D-39f3` on_fail row remains historical; this decision governs new work.
- Harness must still run and publish numbers (`D-1a9e`).