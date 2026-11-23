---
id: T-20261122-pj-b94d
title: "Senior reliability roadmap (independent audit)"
kind: task
owner: pj
branch: main
created: 2026-11-22T10:59:05Z
stage: build
relates: [T-20261118-pj-a670, D-20261114-pj-9f04]
---
# Senior reliability roadmap (independent audit)

## Goal

Close the seven reliability themes from the independent senior-level audit (geographic coverage, scientific validation, session memory, mandatory tests, resume coherence, installed-app acceptance, shared contracts) via decision-flow before implementation — not by delegating blind fixes to agents.

## Triage

- Own/advise: what “done” means per theme; validation tolerances and claims; memory budget; resume/version policy; what the installer must prove; contract boundaries.
- **2026-11-22 auditor delta (3 remaining):** own/advise — what `validation_full` must prove when data is present vs absent; how geographic completeness is evidenced. Plumbing once policy is clear — Windows-safe RSS (`D-f3a8` already claims Windows); lon prefilter that drops footprint-touching cells; wire `--validation-full` to actually run compares.
- Plumbing: only after decisions exist for each theme.

## Pending checkpoint

None. (Implement approved 2026-11-23: drop lon_pad /implementa.)

## Decide closure (item 1 policy)

- Membership + 1 km grid footprint: `D-3e10`
- Boundary warn + no finer-mask refine v1: `D-ae04`
- Leaderboard at boundary = measured score: `D-d254`
- Selector oracle-first: `D-c898` (xy AABB forbidden unless provably identical)

## Detours

- `flow.py new T` reported success but the task file was created manually in the working tree (same ID `T-20261122-pj-b94d`).

## Orientation

- pj (2026-11-22): criterion — everything inside the user boundaries should be evaluated; wants a visual to grasp sphere/projection before deciding.
- pj (2026-11-22): include cells whose ~1 km footprint touches the rectangle boundary; if the best scorer sits on such a border cell, refine locally (finer mask / resolution) to check whether the optimum lies just outside the nominal boundary (invoked Weierstrass loosely — extreme-value intuition, not continuous proof).
- pj (2026-11-22): understands xy pre-filter vs lat/lon filter; expects A-as-oracle + C/D-style policies; suspects shortcut can be tuned via tests; next focus = boundary membership policy (less interest in debating shortcut existence).
- Teaching artifact: `docs/teaching/region-selection-geometry.tex` (compile to PDF).
- Concepts (dependency order):
  - **cap grid / site index** (`prerequisite`) — discrete 1 km cells in `data/masks/cap_1km`; searches iterate cells, not continuous lat/lon.
  - **region selection geometry** (`core`) — `sites_in_latlon_rect` maps a lat/lon box to cells via polar-stereo AABB + lon filter (`D-c159`, `cap_index.py`).
  - **search claim semantics** (`core`) — `grid_optimum` vs `best_seen` in `deep_search` (`D-54f0`).
  - **evidence-gated validation** (`core`) — `docs/validation.md`, `D-de70`, S12 harnesses.
  - **session resource budget** (`core`) — per-request limits (`D-cd33`) vs process-wide hazard/mask caches.
  - **resume fingerprint** (`core`) — `D-1454`; checkpoint matches search params, not necessarily data/engine versions.
  - **distribution acceptance** (`hazard`) — declared platforms vs repeatable install smoke.
  - **planner contract duplication** (`hazard`) — API vs payload builder drift.
- Decisions surfaced: criterion for (1) geographic exactness; (2) validation pass/fail vs report-only; (3) memory envelope; (5) which versions must be in resume fingerprint; order of work vs `T-a670` backlog.

## Decisions

**§1 region**
- D-20261122-pj-3e10, D-ae04, D-d254, D-c898

**§2 validation (ratified 2026-11-22)**
- D-20261122-pj-6dc3 (PGDA soft claim: median |Δ| ≤ 1.5 pp, max ≤ 3 pp)
- D-20261122-pj-1a2d (short-night: document only on fail; supersedes D-39f3 reopen-Y for now)
- D-20261122-pj-7a51 (temporal steps 60/10/1 min)
- D-20261122-pj-7bd7 (cap 1 km vs fine; score primary)
- D-20261122-pj-814a (local resumable runs; no claims until validation.md filled)
- D-20261122-pj-b591 (CI strict + validation_full)
- D-20261122-pj-c403 (Horizons 0.05 deg, ≥8 cases)
- D-20261122-pj-b4ca (estimate benchmark 3 methods; winner deferred)

**§3 session memory (ratified 2026-11-22)**
- D-20261122-pj-f3a8 (LRU PCP cache 20% RAM clamp 256 MB–8 GB; session budget 50% RAM clamp 2–24 GB; UI sliders; one deep-search; float32 default + precision toggle)

**§5 resume (ratified 2026-11-22)**
- D-20261122-pj-e2b7 (`compute_identity` five fields; strict data+motor; UI ignored; Documents envelope + checkpoint)

**§6 install acceptance (ratified 2026-11-22)**
- D-20261122-pj-a91c (claims only with CI acceptance leg green; Mac installer ok, no support claim + disclaimer; manual HW not required v1)

**§7 contracts (ratified 2026-11-22)**
- D-20261122-pj-7c4e (shared evaluate path; mask_for_site / finest available in deep-search too; parity test)

**Decide phase:** audit themes 1–7 closed; build pass may start when pj enters build stage.

**Three auditor closures (2026-11-22):**
- D-20261122-pj-a64b — validation_full green semantics (local science vs CI missing-data)
- D-20261122-pj-c1ed — measure remaining cribas (precision+time) before keep/drop
- D-20261123-pj-3f81 — keep quadrant estimate; metric order feasible→RMSE→max|e|
- D-20261123-pj-6bf5 — drop lon_pad criba; keep lat_pad pending broader bench

## Auto decisions

| Choice | Reason |
|--------|--------|
| Portable RSS / lazy `resource` (or Windows equivalent) under `D-f3a8` | Platform claim already accepted; import-time POSIX-only crash is implementation |
| `--validation-full` implies scientific run when inputs exist | Required by `D-a64b` when heavy inputs are present on the host |

## Fog

- PGDA/short-night numeric disagreements (protocol follow-up; not these three closures).

## Out of scope

- New features beyond what portfolio v1 already promises (`D-9f04`).
- Re-investigating PGDA Site07 / 8 h short-night as part of this closure pass.

## Agenda (three auditor closures, 2026-11-22)

**Destination:** Windows portable RSS + prefilter completeness + honest `validation_full` semantics decided or auto under cited D-IDs; then build.

**Already decided:** `D-3e10`, `D-ae04`, `D-c898`, `D-f3a8`, `D-a91c`, `D-b591` (missing heavy data → job fail not SKIP), `D-814a`.

**Auto:**
- Optional/portable RSS under `D-f3a8` (no top-level POSIX-only `import resource`)
- Wire `--validation-full` so that when required data is present the scientific compare actually runs (subject to Decision 1)

**Queue:**
1. Meaning of a green `validation_full` — concepts: `evidence-gated validation` — own
2. Prefilter / completeness guarantee — concepts: `footprint prefilter completeness` — own (pj pulled from advise)

**Fog / out of scope:** as above.

## Build

2026-11-22 implementation pass on `main`: themes 1–7 built; default `pytest` green; S12 harnesses including `s12_temporal_convergence` (D-7a51) and `s12_spatial_convergence` (D-7bd7) with checkpoints; LaTeX junk untracked.

**Verify (2026-11-22 WSL):** all S12 `--force-run` rows filled in `docs/validation.md`; `pytest -m validation_full` green with PGDA+DEM on disk (~3 min gate); short-night Site07 \|error\|=8 h (document reopen Y); PGDA soft claim fails (Site07 +50 pp outlier — map band follow-up). Run logs under `logs/validation/` (local, not in git). Push when pj ready.

**Independent auditor re-verify (2026-11-22, mid-strong):** pole case fixed; still open (1) `import resource` breaks Windows suite/API/`/deep-search`; (2) lon prefilter can drop cells whose footprint intersects the region (repro: center lon 99.99°, rect 100–101°); (3) `validation_full` tests pass on missing-data exit 2 and `--validation-full` alone does not force the scientific compare. No new product requirements.

**Build (2026-11-22 /implementa, after D-a64b + D-c1ed):**
1. Portable RSS — `moonpark/session_memory.py` (no top-level `resource`); tests `tests/test_session_memory_portability.py` green.
2. `validation_full` → force scientific run when inputs exist — four S12 scripts + docs claim text; force-science unit tests green.
3. Criba investigation — `scripts/bench_selector_cribas.py`; production keep/drop **not** changed (`D-c1ed` deferred). Bench (cap on disk): auditor probe FAIL (`footprint` true, `lon_mask` false); lon_mask drives omissions (e.g. auditor-lon100: 23 prod vs oracle).
Parent re-ran: portability + reliability + two force-science tests → 10 passed.

**Build (2026-11-23 /implementa D-6bf5):** removed production `lon_mask`/`lon_pad` from `sites_in_latlon_rect`; kept `lat_mask`; auditor completeness test green. Parent: `pytest tests/test_cap_index.py` → 8 passed.

## Audit

pending — blocked on closing the three auditor items above

## Orientation (2026-11-22 session, three remaining)

- Concepts (dependency order):
  - **session resource budget** (`prerequisite`) — `D-f3a8`; process RSS + PCP LRU; declared platforms include Windows.
  - **platform-portable session memory** (`core`) — top-level `import resource` is POSIX-only; Windows CPython has no `resource` module → import-time failure before any lunar data.
  - **cap grid / footprint membership** (`prerequisite`) — `D-3e10`, `D-c898`; oracle scan + optional criba.
  - **footprint prefilter completeness** (`core` / `hazard`) — `lon_mask` uses center longitude with a fixed pad; a cell west of `lo_lon` whose square still touches the rect can be discarded before `_footprint_intersects_latlon_rect`.
  - **evidence-gated validation** (`core` / `hazard`) — `D-b591` “fail not skip” on missing heavy data; current tests treat exit 2 as pass; scripts still gate the real compare on `--force-run`, so `--validation-full` alone can exit 0 without comparing.
- Decisions surfaced: whether to reopen/supersede `D-b591` on what the marker proves; whether completeness needs a new test oracle decision beyond `D-c898`; Windows RSS method under existing `D-f3a8`.

## Agenda (decide-all-before-build)

**Destination:** each audit theme 1–7 has `D-` values or explicit deferrals; then one build pass.

**Already decided (cite, do not re-ask):** `D-3e10`, `D-ae04` (1 membership/boundary); `D-c159`, `D-54f0`; `D-de70`, `D-1a9e`, `D-39f3`, `D-9ab3`, `D-fe17` (2 validation frame); `D-cd33` (per-request limits); `D-62d3` (store version paths); `D-1454` (stop/resume UX); `D-75f1`; `D-fc4d`, `D-d99f`, `D-23ab` (6 distribution frame).

**Auto (unless pulled to own):** footprint = cap cell nominal spacing from `D-f369` unless pj overrides; property test file locations (`tests/`).

**Queue (frontier first):**
1. **Footprint geometry** — concepts: `cap grid membership` — exact intersect test for `D-3e10`.
2. **Fast selector policy** — concepts: `region selection geometry` — keep xy pre-filter iff ≡ oracle, else oracle-only or new criba.
3. **S12 senior bar** — concepts: `evidence-gated validation` — convergence (step/terrain) in v1 vs deferred; pass/fail vs report-only for PGDA.
4. ~~**Session memory envelope**~~ — `D-f3a8` (decided).
5. **CI evidence tests** — concepts: `evidence-gated validation` — minimal real data bundle; skips forbidden for critical tests.
6. ~~**Resume fingerprint**~~ — `D-e2b7` (decided).
7. ~~**Install acceptance**~~ — `D-a91c` (decided).
8. ~~**Contract seams v1**~~ — `D-7c4e` (decided).

**Fog:** auditor’s “test passes without assertion” — pin to file when found.

**Out of scope:** microservices/K8s (audit); new product features beyond `D-9f04`.