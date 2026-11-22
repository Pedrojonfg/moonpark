---
id: D-20261122-pj-814a
title: "Validation compute: local PC only, resumable scripts, no claims until tables exist"
date: 2026-11-22T12:32:03Z
author: pj
decided-by: pj
status: accepted
mode: own
domain: scope & success criteria
task: T-20261122-pj-b94d
concepts: [evidence-gated validation]
supersedes: []
relates: [D-20261115-pj-de70, D-20261115-pj-1a9e, D-20261118-pj-cd33]
ai: none
---
# Validation compute: local PC only, resumable scripts, no claims until tables exist

## Context

pj runs validation on a ~7 GB RAM local machine; accepts multi-hour runs if progress is safe.

## Decision

- All S12 heavy runs on **pj's local PC** (not VPS) for this tranche.
- Scripts must be **resumable** (checkpoint per site or tile; safe after power/network loss).
- Runs **one at a time** where needed; target peak RSS **≤ 3.5 GB** per validation job unless a dedicated overnight job documents a higher cap.
- **No** README/portfolio claim that validation is complete until each mandatory row in `docs/validation.md` has **date, command, and numbers** (`D-de70`).

## Rationale

pj (2026-11-22): local runs OK for ~15 h if the PC is not destroyed; no claims until done.

## Provenance

| Who | Contribution |
|-----|----------------|
| **pj** | Local PC only for this tranche; resumable scripts; no README claims until `validation.md` has numbers. |
| **ai** | Recorded RSS target aligned with `D-cd33` measurements; linked to `D-de70`. |

## Values

| Name | Value |
|------|-------|
| validation_host | local_pc |
| validation_resume_required | yes |
| validation_rss_target_mb | 3500 |
| validation_claims_gate | validation_md_tables_populated |

## Consequences

- Implement resume in `s12_*` and convergence scripts before long runs.