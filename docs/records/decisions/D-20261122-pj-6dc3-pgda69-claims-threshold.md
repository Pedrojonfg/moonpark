---
id: D-20261122-pj-6dc3
title: "PGDA 69 comparison: portfolio claim thresholds for average illumination"
date: 2026-11-22T12:32:00Z
author: pj
decided-by: pj
status: accepted
mode: own
domain: claims & interpretation
task: T-20261122-pj-b94d
concepts: [evidence-gated validation, PGDA 69 averages]
supersedes: []
relates: [D-20261115-pj-9ab3, D-20261115-pj-fe17, D-20261115-pj-de70, D-20261114-pj-f369]
ai: exposition+record
---
# PGDA 69 comparison: portfolio claim thresholds for average illumination

## Context

S12 PGDA 69 protocol is report-only with no v1 pass/fail (`D-9ab3`). pj (2026-11-22) set numeric thresholds for when the README may claim agreement with PGDA, after review of internal schedule error (max 0.32 pp on average illumination at 28 points, `D-f369`) and external literature (single-digit pp residuals remain common with coarse terrain; atlas validation examples ~4–5 pp after refinement).

## Framing

Honest claims: always publish the full comparison table; softer wording only when the fixed site set meets agreed bounds.

## Options considered

pj chose a soft-claim band after discussing what “agreement” could mean honestly (2026-11-22); no formal options table.

## Decision

- **Always:** publish per-site Δ (percentage points, ours − map) in `docs/validation.md` for the fixed PGDA-78 schedule set (`D-9ab3`).
- **Soft claim allowed** only when on that same set: **median(|Δ|) ≤ 1.5 pp** and **max(|Δ|) ≤ 3 pp**.
- **Above those bounds:** no agreement wording; point to the table and limitations (terrain/light definition).

## Rationale

pj (2026-11-22): always publish the full table; softer README wording only when the fixed site set stays inside the agreed bounds.

## Provenance

| Who | Contribution |
|-----|----------------|
| **pj** | Honesty pillar; decision to gate **wording** not science; accept **median |Δ| ≤ 1.5 pp** and **max |Δ| ≤ 3 pp** on the PGDA-78 set after reading scale from `D-f369` and literature context. |
| **ai** | Mapped Familia 1 to `D-9ab3`; explained pp deltas and example threshold levels; drafted Values table. |

## Checks raised

- PGDA is not ground truth; thresholds are portfolio honesty, not certification.
- Mismatched span or light definition invalidates comparison → protocol in `D-9ab3` still binds.

## Values

| Name | Value | Notes |
|------|-------|-------|
| s12_pgda69_claim_median_abs_delta_pp | 1.5 | Soft claim gate |
| s12_pgda69_claim_max_abs_delta_pp | 3.0 | Soft claim gate |
| s12_pgda69_below_threshold_wording | report_only | Full table always |
| s12_pgda69_above_threshold_wording | no_agreement_claim | |

## Expected behavior and validation

Wrong if README claims PGDA agreement while the published table violates the soft-claim bounds on the listed sites.

## Consequences

- Supplements `D-9ab3` pass/fail none_v1 with explicit claim language.
- Implementation in scripts and validation.md; no product logic change.