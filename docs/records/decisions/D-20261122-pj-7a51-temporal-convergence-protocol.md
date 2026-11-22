---
id: D-20261122-pj-7a51
title: "Temporal convergence: compare step 60, 10, and 1 minute"
date: 2026-11-22T12:32:02Z
author: pj
decided-by: pj
status: accepted
mode: own
domain: method & validation
task: T-20261122-pj-b94d
concepts: [evidence-gated validation]
supersedes: []
relates: [D-20261118-pj-cd33, D-20261114-pj-41fa]
ai: exposition+record
---
# Temporal convergence: compare step 60, 10, and 1 minute

## Context

Audit §2 asks sensitivity to temporal sampling. pj (2026-11-22): run steps **60, 10, and 1** minute despite compute cost on a modest PC — sampling matters more than saving runs.

## Framing

Document how much mission metrics move when refining time step; guide defaults and README limits.

## Decision

Run paired `/site` analyses (hazards off) for **Site01** and **Site04**, window **31 days** from **2027-01-01**, at **step_min 60, 10, and 1**. Record Δ longest night (h) and Δ score (and feasible flips). **Documentation triggers:** if |Δ longest night| **> 2 h** between 60 and 10 min, or |Δ score| **> 0.05** with same feasible flag, add a validation.md note recommending finer step for that use case. Runs **sequentially** on local hardware with peak RSS target ≤ 3.5 GB per run (`D-814a`).

## Rationale

(Translated from pj's intent, 2026-11-22.) Importance of temporal sampling outweighs cost on local hardware.

## Provenance

| Who | Contribution |
|-----|----------------|
| **pj** | Require 60/10/1 min comparison; accept long local runs under `D-814a`. |
| **ai** | Drafted sites, window, hazards-off default, and documentation triggers (Δ night 2 h, Δ score 0.05) for pj to accept. |

## Values

| Name | Value |
|------|-------|
| temporal_conv_sites | Site01, Site04 |
| temporal_conv_window | 2027-01-01 + 31 days |
| temporal_conv_steps_min | 60, 10, 1 |
| temporal_conv_hazards | off |
| temporal_conv_doc_delta_night_h | 2 |
| temporal_conv_doc_delta_score | 0.05 |

## Expected behavior and validation

Wrong if README recommends hourly-only for sub-2 h decisions while the report shows larger Δ without disclosure.

## Consequences

- Script under `scripts/` or `tests/` plus validation.md section.