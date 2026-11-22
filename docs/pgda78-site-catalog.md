# PGDA product 78 site catalog (S12 fixtures)

Authority for **site IDs** and **prose names**: [PGDA product 78](https://pgda.gsfc.nasa.gov/products/78) and [LOLA_5mpp README](https://pgda.gsfc.nasa.gov/data/LOLA_5mpp/README). Numbering follows Mazarico et al. (2011), Icarus 211, 1066–1081. DEMs: Barker et al. (2021), PSS 203, 105119.

Verified **2026-11-22** (local `data/dem/*_final_adj_5mpp_surf.tif`): observer lat/lon in `scripts/s12_sites.py` matches each tile stereographic centre within **&lt; 0.1 m**. Horizons ephemeris fixtures use the same coordinates (`tests/fixtures/horizons/`, `scripts/fetch_horizons_fixtures.py`).

| Moonpark ID | PGDA / README name | lat (°S) | lon (°E) | DEM file | In S12 PGDA-69 set |
|-------------|-------------------|----------|----------|----------|-------------------|
| Site01 | Connecting ridge | 89.46316 | 222.51045 | `Site01_final_adj_5mpp_surf.tif` | yes |
| Site04 | Shackleton rim | 89.76681 | 188.13010 | `Site04_final_adj_5mpp_surf.tif` | yes |
| Site07 | Peak near Shackleton | 88.81101 | 123.69007 | `Site07_final_adj_5mpp_surf.tif` | yes |
| Site11 | de Gerlache rim | 88.68342 | 292.06790 | `Site11_final_adj_5mpp_surf.tif` | yes |

**Notes**

- **Site07** (“Peak near Shackleton”) is not Shackleton rim (Site04); it is a separate ROI in the PGDA 78 release. Illumination validation caveats: `D-d1c4`, `docs/validation.md` PGDA section.
- **Site11** coords in code are taken from the DEM tile centre when the file is present (`pgda_pgda78_sites`); equals the fixed entry above for the on-disk tile.
- Other PGDA 78 sites (e.g. Site06 Nobile rim 1, Site23 Malapert massif) are not in the current S12 quartet until added to `data/dem/` and decisions extend the set.