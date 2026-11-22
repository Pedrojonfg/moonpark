---
id: D-20261122-pj-e2b7
title: "Resume checkpoint: strict match on data and motor; UI-only updates do not block"
date: 2026-11-22T13:00:00Z
author: pj
decided-by: pj
status: accepted
mode: own
domain: reliability & resources
task: T-20261122-pj-b94d
concepts: [resume fingerprint, cache identity]
supersedes: []
relates: [D-20261118-pj-1454, D-20261118-pj-8625, D-20261118-pj-62d3, D-20261118-pj-1bc9]
ai: exposition+record
---
# Resume checkpoint: strict match on data and motor; UI-only updates do not block

## Context

`D-1454` saves a stopped deep-search checkpoint and resumes when the request fingerprint matches. Today `deep_search` fingerprints mode, window, requirements, rectangle, and dates (`fingerprint_extra` in `moonpark/api/app.py`); it does **not** record whether **data** or **calculation code** changed. A user can resume after a data-store migration or engine update and mix rows from the old world with new evaluations. `D-8625` / `D-62d3` already require saved analyses to remember data version; stopped-search files in Documents (`desktop/src/lib/analysesStore.ts`) store `dataVersion` on save but not a full **motor** identity, and the in-engine checkpoint does not gate on versions.

pj (2026-11-22): people install MoonPark for **calculations**, not for UI polish. If **data** or the **motor** (how calculations are done) changes, resume is forbidden — start again with the improved data/motor, and the user must update to that stack. If only **UI** (or other non-calculation layers) changes, resume continues normally; no forced app update — an “update available” notice is enough and not required to be pushy.

## Framing

Minimal bytes in Documents; maximum certainty on calculation-affecting drift.

## Decision

### Identity buckets

| Bucket | Meaning | Resume if current ≠ stored |
|--------|---------|----------------------------|
| **Data** | Remote store and cap assets the engine used | **Hard reject** — cannot resume; start a new search |
| **Motor** | Engine + score contract that defines evaluate/score | **Hard reject** — cannot resume; start a new search |
| **UI / shell** | Desktop app version, labels, layout | **Ignore** for resume; no forced update |

### Minimal `compute_identity` (stored at stop, checked on resume)

Use the **smallest set of fields already produced for site provenance** (`moonpark/planner_payload.py` `provenance()`), plus mask schedule:

| Field | Role |
|-------|------|
| `data_version` | Live data-store group version (`cached_data_version()`) |
| `cap_version` | 1 km cap mask store group version (`cached_cap_version()`) |
| `schedule_version` | Mask schedule id (`SCHEDULE_VERSION` constant) |
| `engine_version` | Installed MoonPark engine package version |
| `formula_version` | Score contract id (`FORMULA` in `moonpark/score.py`) |

No extra hashes or large blobs in v1 unless a field above is missing at runtime (then fail closed on resume).

### Where it lives

1. **Engine checkpoint** — extend `deep_search` resume `fingerprint` (or parallel `compute_identity` object next to it) with the five fields **at stop time**.
2. **Documents file** — each stopped-search JSON (`kind: "search"`) carries the same `compute_identity` at envelope level **and** inside the checkpoint block so opening a file offline still has the ids (`D-8625` spirit, minimal duplicate).

### On resume / Continue

1. Recompute **current** `compute_identity` in the running engine.
2. Compare to stored identity **before** accepting `resume`.
3. **Any mismatch in data or motor fields** → do not resume; return a clear error (`resume_compute_identity_mismatch` or equivalent) telling the user to **start a new search** after updating data and/or the app (when the update changes motor or data). Partial rows from the old checkpoint are not merged forward.
4. **Request fingerprint mismatch** (rectangle, dates, requirements, mode) → existing behavior (reject).
5. **Desktop app version / UI-only mismatch** → **no block**; resume if data+motor match.

### Forced update (product policy)

- **Require** update (block resume, insist on fresh run) when **data** or **motor** identity changed relative to the checkpoint.
- **Do not require** update for UI-only releases; optional soft “update available” only.

### Saved finished analyses

Not re-litigated here; stopped-search resume is in scope. Finished saves should continue to expose enough version metadata for “Recalculate” warnings per `D-8625`; align field names with `compute_identity` when touched in build.

## Rationale

(Translated from pj's Spanish, 2026-11-22.) Distinguish UI from motor and data. If motor or data changed, you cannot continue — redo from zero with the better motor/data and you are pushed to update when calculation changed. If only UI changed, continue calmly without forcing update. Checkpoints in Documents must store the **minimum** information to detect calculation-affecting version changes with full certainty, without filling Documents with junk.

## Provenance

| Who | Contribution |
|-----|----------------|
| **pj** | Entire policy: strict on data+motor; permissive on UI; minimal stored ids; forced update only when calculation stack changes. |
| **ai** | Mapped gap in `deep.py` fingerprint; listed five existing provenance fields as minimal identity; recorded in ADR. |

## Values

| Name | Value |
|------|-------|
| resume_gate_data_fields | data_version, cap_version, schedule_version |
| resume_gate_motor_fields | engine_version, formula_version |
| resume_gate_ui_fields | none (not compared) |
| resume_identity_mismatch | hard_reject_no_merge |
| resume_ui_update_forced | no |
| resume_calculation_update_forced | yes |
| resume_error_code | resume_compute_identity_mismatch |
| stopped_search_envelope_identity | compute_identity (five fields) |
| checkpoint_identity_location | fingerprint or compute_identity sibling on checkpoint v1 |

## Expected behavior and validation

- Stop → save → update **only** desktop UI version → Continue succeeds with same numeric leaderboard continuation.
- Stop → save → bump `engine_version` or `formula_version` or data store version → Continue **rejected** with clear message; new search run produces consistent rows.
- Wrong: resume silently after data migration; Documents gain large unrelated metadata.

## Consequences

- Implement identity capture in `deep_search` + `/deep-search` resume path; desktop must persist envelope fields on `saveStoppedSearch`.
- Reconcile wording in `D-1454` “resume after app update” with this decision: app update is fine **only when** `compute_identity` unchanged.
- Tests: identity round-trip; mismatch rejects (extend `tests/test_review_fixes.py` pattern).