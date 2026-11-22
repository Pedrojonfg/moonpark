---
id: D-20261122-pj-b591
title: "CI honesty: strict regression tests; validation_full fails without data"
date: 2026-11-22T12:32:04Z
author: pj
decided-by: pj
status: accepted
mode: advise
domain: testing
task: T-20261122-pj-b94d
concepts: [evidence-gated validation]
supersedes: []
relates: [D-20261115-pj-de70, D-20261122-pj-814a]
ai: exposition+record
---
# CI honesty: strict regression tests; validation_full fails without data

## Context

Audit §4: tests must not pass without exercising checks. pj pillar is honesty.

## Decision

- **Default CI:** all decision/regression/API tests **run**; no silent skip for missing fixtures that belong in the repo (kernels, horizons fixtures).
- **Heavy validation** (PGDA file present, full S12 runs, large convergence sweeps): mark **`validation_full`**; optional workflow on release or local; **exit non-zero** if required inputs missing — **not** success with SKIP.
- Data not shipped in git (PGDA map) → `validation_full` job **fails clearly** on GitHub; full numbers produced **locally** per `D-814a`.

## Rationale

pj (2026-11-22): honesty pillar — CI must not show green when checks did not run.

## Provenance

| Who | Contribution |
|-----|----------------|
| **pj** | Strict regression; `validation_full` fails on missing heavy data, not skip-success. |
| **ai** | Mapped audit §4 to pytest markers and workflow policy text. |

## Values

| Name | Value |
|------|-------|
| ci_regression_skips | forbidden_for_bundled_fixtures |
| ci_validation_full_marker | validation_full |
| ci_validation_full_on_missing_data | fail_not_skip |
| ci_default_scope | regression_plus_ephemeris_with_kernels |

## Consequences

- pytest markers and optional workflow; document in contributor-facing readme when added.