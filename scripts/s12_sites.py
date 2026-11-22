"""Named validation sites (Horizons / PGDA fixtures).

PGDA product 78 names and verification: ``docs/pgda78-site-catalog.md``.
"""

from __future__ import annotations

from moonpark.providers import Site

# PGDA LOLA_5mpp README prose names (product 78).
PGDA78_NAMES: dict[str, str] = {
    "Site01": "Connecting ridge",
    "Site04": "Shackleton rim",
    "Site07": "Peak near Shackleton",
    "Site11": "de Gerlache rim",
}

SITES: dict[str, Site] = {
    "Site01": Site(lat_deg=-89.46316, lon_deg=222.51045, observer_height_m=2.0),
    "Site04": Site(lat_deg=-89.76681, lon_deg=188.13010, observer_height_m=2.0),
    "Site07": Site(lat_deg=-88.81101, lon_deg=123.69007, observer_height_m=2.0),
    "Site11": Site(lat_deg=-88.68342, lon_deg=292.06790, observer_height_m=2.0),
}

DEFAULT_NEEDS: dict[str, object] = {
    "max_night_h": 50,
    "max_no_earth_h": 20,
    "min_continuous_lit_h": 0,
    "min_total_lit_h": 0,
    "require_both": False,
    "template_id": None,
}