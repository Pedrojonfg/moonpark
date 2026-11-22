---
id: D-20261122-pj-a64b
title: "validation_full green: local science vs CI missing-data fail; claims match"
date: 2026-11-22T18:54:36Z
author: pj
decided-by: pj
status: accepted
mode: own
domain: method & validation
task: T-20261122-pj-b94d
concepts: [evidence-gated validation]
supersedes: []
relates: [D-20261122-pj-b591, D-20261122-pj-814a]
ai: options+critique
---
# validation_full green: local science vs CI missing-data fail; claims match

## Context

Independent auditor (2026-11-22): `tests/test_s12_validation_full.py` can go green when scripts only exit on missing heavy data, and `--validation-full` alone does not force the scientific compare. `D-b591` already requires fail-not-skip when heavy inputs are absent; `D-814a` places full S12 numbers on the local host. Need an explicit split between those greens and what may be claimed.

## Framing

Honesty of evidence gates: what a green `validation_full` is allowed to mean in each environment, without shipping PGDA/DEM in git.

## Options considered

1. **A — Local green = science ran; workflow without heavy data = honest missing-data fail; claims say exactly that**: assumes heavy inputs stay out of git and the owner machine is the science host; consequence — docs/tests must not call a missing-data check “full science”, and `--validation-full` with data present must compare.
2. **B — Every validation_full green always means science ran**: assumes heavy data wherever the marker runs; consequence — CI without data never green, or data supplied to CI.
3. **C — Green may mean only prereq/error path, even when data are present**: assumes local marker need not compare; consequence — auditor false-green critique stays open.
4. **Other / none**

## Decision

**A — Local green = science ran; workflow without heavy data = honest missing-data fail; claims say exactly that.**

## Rationale

On my PC, run the comparison. In the workflow where the heavy data are not present, react correctly to that absence — and that is literally what is claimed. That simple. Be very clear about this and about why it is done this way so no auditor can nag about it.

## Checks raised

- Claim text must name which green → accepted; documentation must stay explicit.
- With data present, `--validation-full` must force the compare → accepted as build consequence.

## Values

| Name | Value | Notes |
|------|-------|-------|
| validation_full_green_local_with_data | scientific_compare_ran | |
| validation_full_green_ci_without_heavy_data | not_applicable_job_must_fail_missing_inputs | aligns with `D-b591` |
| validation_full_claim_text | state_which_green_explicitly | README / validation.md / test docstrings |

## Expected behavior and validation

This choice would be wrong if people would not trust the results from my PC for some reason, or if my PC were unable to run the tests. Neither seems probable or worrying to me.

## Consequences

- Supersedes informal reading of `D-b591` that treated “script exit 2 asserted by pytest” as sufficient local “full validation” evidence.
- Build: scripts treat `--validation-full` as requiring the scientific run when inputs exist; local tests assert compare outcomes (or clear fail if data absent); CI workflow remains fail-on-missing; claim wording updated.
- Does not require uploading heavy datasets to git.
