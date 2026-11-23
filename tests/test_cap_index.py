"""Cap index queries (1 km precomputed masks)."""

from __future__ import annotations

import pytest

from moonpark.horizon import polar_stereo_xy
from moonpark.horizon.cap_index import (
    cap_index_available,
    sites_in_latlon_rect,
    sites_in_latlon_rect_xy_corners,
    sites_in_xy_rect,
)
from moonpark.site01 import SITE01

pytestmark = pytest.mark.skipif(not cap_index_available(), reason="cap_1km index not present")


def test_sites_in_xy_rect_near_site01_is_nonempty() -> None:
    sx, sy = polar_stereo_xy(SITE01.lat_deg, SITE01.lon_deg)
    cells = sites_in_xy_rect(sx - 5_000, sx + 5_000, sy - 5_000, sy + 5_000)
    assert len(cells) >= 20
    site, x_m, y_m, _tx, _ty, _row = cells[0]
    assert abs(x_m - sx) <= 5_000 + 1.0
    assert abs(y_m - sy) <= 5_000 + 1.0
    assert -90.0 <= site.lat_deg <= -80.0


def test_latlon_rect_still_returns_cells() -> None:
    # Near-pole lon pad is tiny in metres; still must not crash / return junk.
    cells = sites_in_latlon_rect(
        SITE01.lat_deg - 0.05,
        SITE01.lat_deg + 0.05,
        SITE01.lon_deg - 0.15,
        SITE01.lon_deg + 0.15,
    )
    assert isinstance(cells, list)
    for site, *_rest in cells:
        assert SITE01.lat_deg - 0.05 <= site.lat_deg <= SITE01.lat_deg + 0.05


def test_nearest_cap_mask_snaps_within_a_cell():
    from moonpark.horizon.cap_index import nearest_cap_mask
    from moonpark.providers import Site

    m = nearest_cap_mask(Site(lat_deg=-89.46316, lon_deg=222.51045, observer_height_m=2.0))
    assert m is not None and m.elevation_deg.shape == (720,)
    # Far outside the cap: no cell, no mask.
    assert nearest_cap_mask(Site(lat_deg=-60.0, lon_deg=0.0, observer_height_m=2.0)) is None


def _cell_keys(cells) -> set[tuple[float, float]]:
    return {(round(c[0].lat_deg, 6), round(c[0].lon_deg, 6)) for c in cells}


@pytest.mark.parametrize(
    "lat_min, lat_max, lon_min, lon_max",
    [
        (-89.52, -89.40, 222.0, 223.0),
        (SITE01.lat_deg - 0.2, SITE01.lat_deg + 0.2, SITE01.lon_deg - 1.0, SITE01.lon_deg + 1.0),
        (-90.0, -85.0, 200.0, 250.0),
    ],
    ids=["deep-rect", "site01-box", "polar-wedge"],
)
def test_oracle_membership_superset_of_legacy_xy_corners(
    lat_min: float, lat_max: float, lon_min: float, lon_max: float,
) -> None:
    """D-c898: deprecated xy corner path must not return cells outside the footprint oracle."""
    legacy = _cell_keys(sites_in_latlon_rect_xy_corners(lat_min, lat_max, lon_min, lon_max))
    oracle = _cell_keys(sites_in_latlon_rect(lat_min, lat_max, lon_min, lon_max))
    assert legacy <= oracle, f"legacy-only cells: {sorted(legacy - oracle)[:5]}"
    assert len(oracle) >= len(legacy)


def test_latlon_rect_filters_by_longitude() -> None:
    from moonpark.horizon.cap_index import _footprint_intersects_latlon_rect

    lo, hi = SITE01.lon_deg - 0.5, SITE01.lon_deg + 0.5
    width = hi - lo
    cells = sites_in_latlon_rect(-90.0, -80.0, lo, hi)
    assert cells
    for site, *_rest in cells:
        assert _footprint_intersects_latlon_rect(
            site.lat_deg, site.lon_deg, -90.0, -80.0, lo, width
        )


def test_auditor_rect_includes_west_edge_footprint_cells() -> None:
    """Auditor rect lon 100-101, lat -85.6..-84.4 must not lose west-edge footprint cells.

    Production ``sites_in_latlon_rect`` must equal every index cell whose 1 km footprint
    intersects the rect; the center ``lon_pad`` criba (east-only) must not drop cells whose
    center lon is just west of ``lon_min``. Reference: lat_pad-only prefilter (lat_pad keep,
    lon_pad removed_from_production) + ``_footprint_intersects_latlon_rect``.
    # per D-20261123-pj-6bf5 (D-3e10)
    """
    import numpy as np

    from moonpark.horizon.cap_index import _footprint_intersects_latlon_rect, _load_index

    lo_lat, hi_lat, lo_lon, hi_lon = -85.6, -84.4, 100.0, 101.0
    width = hi_lon - lo_lon
    lat_pad = 0.05

    table = _load_index()
    lat = table.column("lat").to_numpy()
    lon = table.column("lon").to_numpy()
    cand = np.flatnonzero((lat >= lo_lat - lat_pad) & (lat <= hi_lat + lat_pad))
    expected = {
        (round(float(lat[i]), 6), round(float(lon[i]), 6))
        for i in cand
        if _footprint_intersects_latlon_rect(float(lat[i]), float(lon[i]), lo_lat, hi_lat, lo_lon, width)
    }
    assert expected, "reference scan found no cells; test setup invalid"

    got = _cell_keys(sites_in_latlon_rect(lo_lat, hi_lat, lo_lon, hi_lon))
    assert got, "production returned no cells for auditor rect"

    # Centers west of lon_min that still touch the rect via footprint (the bug class).
    west_only = {k for k in expected if (k[1] - lo_lon) % 360.0 > 180.0}
    assert west_only, "auditor rect has no west-of-lon_min footprint cells in index; adjust rect"

    missing = expected - got
    assert not missing, (
        f"production dropped {len(missing)} footprint-intersecting cells "
        f"(west-edge dropped: {len(west_only - got)}); sample={sorted(missing)[:5]}"
    )
    assert got == expected, f"extra production cells: {sorted(got - expected)[:5]}"
