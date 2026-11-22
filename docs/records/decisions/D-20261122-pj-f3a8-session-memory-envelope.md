---
id: D-20261122-pj-f3a8
title: "Session memory envelope: LRU PCP cache, process budget, settings overrides"
date: 2026-11-22T12:50:00Z
author: pj
decided-by: pj
status: accepted
mode: own
domain: reliability & resources
task: T-20261122-pj-b94d
concepts: [session resource budget]
supersedes: []
relates: [D-20261118-pj-cd33, D-20261118-pj-1454, D-20261115-pj-9f04]
ai: exposition+record
---
# Session memory envelope: LRU PCP cache, process budget, settings overrides

## Context

`D-cd33` caps **individual requests** (window, samples, region size, hazard span) using measurements on a ~7 GB machine with a **3.5 GB peak RSS** target per fresh process (`docs/limits.md`). The desktop engine reuses one Python process: `default_moon_hazards()` keeps a **process-wide** Diviner PCP bin cache that **never evicts** (~72 MB per bin loaded). Long sessions can grow past what any single request limit allows. pj (2026-11-22), after Q&A on fixed vs RAM-scaled limits: bound session growth, scale defaults with installed RAM, **UI settings** overrides (not env-only), session pressure (evict then fail clear), one deep-search at a time, and **float32** PCP coordinates by default with optional high precision in settings.

## Framing

Desktop apps should use available hardware on strong machines without letting weak laptops swap-kill; session policy is separate from per-request caps and does not lower `D-cd33` constants by itself.

## Options considered

pj explored fixed limits vs scaling with hardware (conversation 2026-11-22) before stating policy; the table below only names alternatives discussed for the record, not a ballot pj took from AI.

| Option | Pros | Cons |
|--------|------|------|
| Fixed small PCP cache for everyone | Simple | Caps power users on strong desktops |
| Env vars only for overrides | Easy for CI | Poor UX for a desktop product |
| **% of RAM defaults + UI sliders + LRU + session budget (pj's policy)** | Scales with hardware; user-visible | Requires settings UI and RSS accounting |

## Provenance

| Who | Contribution |
|-----|----------------|
| **pj** | Questions on whether weak reference hardware should cap everyone; policy: LRU mandatory; defaults from % RAM; overrides in **Settings UI** (sliders, reset automatic); accept session-pressure flow (evict LRU then `session_memory_pressure`); one deep-search; float32 default with high-precision toggle off by default. |
| **ai** | Explained per-request vs session memory, PCP cache vs global session budget, and float32 tradeoff; suggested illustrative numeric clamps (20%/50% RAM, min/max MB) pj accepted for v1 defaults; drafted this ADR. |

## Decision

### 1. PCP bin cache (LRU)

- **Mandatory LRU** on the process-wide PCP bin cache in `PolarPcpClimatology` (and any shared path that loads `ltim*.npz` bins).
- **Default budget** from **installed RAM** (see Values): `clamp(floor * pcp_ram_fraction), pcp_cache_min_mb, pcp_cache_max_mb)`.
- On insert over budget: **evict least-recently-used** bins until within budget.
- **UI:** Settings → **Engine memory** (or equivalent): slider **PCP cache (% of RAM)** plus optional explicit MB override; **Reset to automatic** restores formula defaults.
- **Headless / tests:** same numbers readable from env or config file when no UI exists (implementation detail; UI is the primary surface for pj).

### 2. Process session budget (global pressure)

- Track an approximate **process RSS envelope** for the engine (same process as caches).
- Before starting work that may spike memory (especially `/deep-search` and heavy `/site` with hazards on):
  1. Try **LRU PCP evictions** to free headroom.
  2. If estimated **current RSS + peak delta** still exceeds the **session budget**, return **422** with `error: "session_memory_pressure"` and a message naming the budget field and suggesting shorter windows, fewer cells, settings adjustment, or restart.
- **Default session budget** from installed RAM (Values); **not** the same slider as PCP cache (two controls: *how big the map shelf* vs *how heavy the whole backpack may get*).
- **UI:** second slider **Session budget (% of RAM)** + **Reset to automatic**.
- **Does not replace** `D-cd33` per-request checks; both apply.

### 3. Deep-search concurrency

- At most **one** active deep-search per engine process; a second start gets **409** or **422** with `error: "deep_search_busy"` and a short message (exact status code at implementation).

### 4. PCP coordinate precision

- **Default:** load PCP bin `x` and `y` as **float32** in memory (files unchanged).
- **Settings:** **High precision PCP coordinates** (off by default) → float64 load path for parity with today's behavior when enabled.
- Document that temperature impact on scores is expected to be negligible; high precision is for debugging/parity, not product claims.

## Rationale

(Translated from pj's Spanish, 2026-11-22.) Desktop users should be able to use the machine they have; fixed tiny caps for everyone would be wrong. LRU makes sense. Default sizing from % RAM is fine; numeric floors/ceilings are acceptable if they match normal practice. **Overrides must be in the UI**, not hidden env vars. Session pressure (try evicting map bins, then refuse clearly) is good. One deep-search at a time is fine. If float32 precision loss is negligible, use it by default and expose extra precision in settings, off by default.

## Checks raised

- RSS estimation is approximate (OS reporting, fragmentation); validation benches stable RSS under repeated hazard requests, not exact byte accounting.
- Session budget on machines with little headroom still relies on `D-cd33` hazard span and sample caps for single-request safety.
- Settings must persist locally for the desktop app and apply without restart when feasible; otherwise document one-time restart.

## Values

| Name | Value | Notes |
|------|-------|-------|
| pcp_ram_fraction_default | 0.20 | Of installed RAM for PCP LRU budget |
| pcp_cache_min_mb | 256 | Floor |
| pcp_cache_max_mb | 8192 | Ceiling (8 GB) |
| session_ram_fraction_default | 0.50 | Of installed RAM for process session budget |
| session_budget_min_mb | 2048 | Floor |
| session_budget_max_mb | 24576 | Ceiling (24 GB); on 7 GB host → 3500 MB, matches `docs/limits.md` measurement target |
| pcp_bin_cache_policy | lru_mandatory | |
| deep_search_max_concurrent | 1 | Per engine process |
| session_pressure_error | session_memory_pressure | After LRU eviction insufficient |
| deep_search_busy_error | deep_search_busy | Second concurrent deep-search |
| pcp_xy_dtype_default | float32 | In-memory after load |
| pcp_xy_high_precision_setting | false | Default off; float64 when on |
| settings_surface | engine_memory | Sliders: PCP % RAM, session % RAM; precision toggle; reset automatic |
| per_request_limits | unchanged | `D-cd33` constants; rescaling by RAM is out of scope for this decision |

**Installed RAM** for defaults: OS-reported total physical memory at engine start (WSL/Linux/macOS/Windows); if unavailable, fall back to `session_budget_min_mb` and `pcp_cache_min_mb` until user sets sliders.

## Expected behavior and validation

- Sequence of hazard-heavy `/site` and `/deep-search` calls: PCP cache RSS stays **≤ configured PCP budget**; process RSS stabilizes **≤ session budget** (median of last N requests on a scripted bench).
- With session budget artificially low in settings, a large hazards-on request gets `session_memory_pressure` **after** evictions, not silent OOM.
- Two parallel deep-search POSTs: second fails with `deep_search_busy`.
- `pcp_xy_high_precision=false`: measurably lower RSS per bin vs float64 path; score deltas on fixed Site01 window within documented noise when benchmarked.

Wrong: unbounded PCP cache across a long desktop session; env-only overrides with no settings UI in the shipped app; float64 coordinates forced with no user toggle.

## Consequences

- Implement LRU + budgets in `moonpark/hazards/pcp.py` / `moon.py` and enforce session pressure + deep-search mutex in `moonpark/api/app.py` (and deep-search entry).
- Add **Engine memory** settings in the desktop UI; wire to engine config endpoint or local prefs as the stack already does for planner options.
- Update `docs/limits.md` § "Findings worth acting on" item 1 to cite this decision when implemented.
- Optional follow-up decision: scale `HAZARD_MAX_SPAN_H` and other `D-cd33` fields with RAM fraction (not ratified here).