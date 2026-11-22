# Release checklist (prepared overnight 2026-11-17; updated 2026-11-22)

## Verified
- CI workflow `desktop-release.yml` built the installers on Linux, Windows and macOS (run 44186563271, all green), each with a smoke test of the bundled engine (`/health` and `/site?mock=1&local_search=1` with a non-empty leaderboard).
- Linux: `deploy/build-desktop.sh` produced deb, rpm and AppImage locally. The release binary launched under xvfb, started the engine on a free loopback port, and `/health` and the mock local search answered.
- `scripts/publish_masks.py --dry-run` builds both manifests (cap_1km: 90 files, ~896 MB with fill stats; data: 416 files / 2737 MB including relief cuts).
- **2026-11-21 WSL:** AppImage rebuild finished (`moonpark_0.1.0_amd64.AppImage`, also copied to `~/apps/moonpark.AppImage`). Bundled `moonpark-api --port …` returns `/health` ok and mock `/site?mock=1&local_search=1` with a 47-entry leaderboard.
- **2026-11-21:** fill-stats for D-d90c in `precompute.py` / `cap_index.py` / `tests/test_cap_fill_stats.py`.
- **2026-11-21:** real `/site` against local `data/` (kernels + `cap_1km`) returns `data_source=real` and a feasible score (hazards off).
- **2026-11-21:** first R2 publish (`cap_1km/d1dd266012b1`, `data/cc02b519005a`). Packaged `moonpark-api` with an empty cache downloaded from the store and returned `data_source=real` (~495 MB for one short window, hazards off).
- **2026-11-21/22:** fill-stats recompute finished (290 289 masks, 44 tiles, ~13.1 h wall). Swapped to `cap_1km` (old set as `cap_1km_old_pre_d90c`). Republished to R2 as `cap_1km/6f5bd6aee903` (via VPS; local Sophos MITM blocked direct upload).

## Not verified
- The UI of the packaged app was not looked at (no screenshot under xvfb); only the engine side was exercised.
- Windows and macOS installers were built but never launched on real machines.
- macOS and Windows builds are unsigned: expect Gatekeeper / SmartScreen warnings.

## Remaining
1. Optional later: code signing / notarization; run Win/mac installers on real machines.

## Released
- **2026-11-21:** tag `v0.1.0` — CI green ([run](https://github.com/Pedrojonfg/moonpark/actions/runs/44892380278)); GitHub Release published with Linux/Windows/macOS installers.
