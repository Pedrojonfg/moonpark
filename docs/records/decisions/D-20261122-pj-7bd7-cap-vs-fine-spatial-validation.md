---
id: D-20261122-pj-7bd7
title: "Spatial convergence: 1 km cap mask vs fine DEM mask at ranked sites"
date: 2026-11-22T12:32:02Z
author: pj
decided-by: pj
status: accepted
mode: own
domain: method & validation
task: T-20261122-pj-b94d
concepts: [evidence-gated validation, cap grid membership]
supersedes: []
relates: [D-20261117-pj-c4e8, D-20261114-pj-f369, D-20261118-pj-1bc9]
ai: exposition+record
---
# Spatial convergence: 1 km cap mask vs fine DEM mask at ranked sites

## Context

Clients without local DEMs use precomputed 1 km cap masks. Validate error vs fine masks where DEM exists.

## Decision

At **Site01, Site04, Site07**: **7 days** from **2027-01-01**, **step 60 min**, hazards off for core run; compare **cap tile mask** vs **fine mask** (`mask_for_site` / 5 m where available). **Primary metrics:** score and feasible; **secondary:** longest night (h). **Documentation trigger:** |Δ score| > **0.05** or feasible mismatch → README limitation for 1 km client mode. Optional hazards-on repeat for Site01 only if within RAM budget.

## Rationale

pj (2026-11-22): **score** (and feasible) are what matter for product claims; terrain convergence is supporting evidence.

## Provenance

| Who | Contribution |
|-----|----------------|
| **pj** | Primary metrics = score/feasible; accept cap-vs-fine comparison at ranked sites. |
| **ai** | Proposed Site01/04/07, 7 d window, step 60, doc trigger |Δ score| > 0.05 from audit framing. |

## Values

| Name | Value |
|------|-------|
| spatial_conv_sites | Site01, Site04, Site07 |
| spatial_conv_window_days | 7 |
| spatial_conv_start | 2027-01-01 |
| spatial_conv_step_min | 60 |
| spatial_conv_primary_metrics | score, feasible |
| spatial_conv_doc_delta_score | 0.05 |

## Consequences

- Feeds honest 1 km claims alongside API mask quality improvements pj expects in coming months.