"""Shared S12 validation compute helpers."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from moonpark.horizon import mask, polar_stereo_xy
from moonpark.horizon.cap_index import nearest_cap_mask
from moonpark.horizon.dem_schedule import mask_schedule_for_site
from moonpark.providers import HorizonMask, Site


def pgda_pgda78_sites(root: Path) -> dict[str, Site]:
    """PGDA product 78 site centroids (5 m DEMs on disk)."""
    from scripts.s12_sites import SITES

    out = dict(SITES)
    t11 = root / "data" / "dem" / "Site11_final_adj_5mpp_surf.tif"
    if t11.is_file():
        import rasterio
        from moonpark.region_map import _polar_stereo_xy_to_latlon

        with rasterio.open(t11) as src:
            b = src.bounds
            lat, lon = _polar_stereo_xy_to_latlon((b.left + b.right) / 2, (b.bottom + b.top) / 2)
        out["Site11"] = Site(lat_deg=lat, lon_deg=lon, observer_height_m=2.0)
    return {k: v for k, v in out.items() if k.startswith("Site")}


def pgda_map_fraction(tif: Path, site: Site) -> tuple[float, str]:
    import rasterio

    x, y = polar_stereo_xy(site.lat_deg, site.lon_deg)
    try:
        with rasterio.open(tif) as src:
            row, col = src.index(x, y)
            if row < 0 or col < 0 or row >= src.height or col >= src.width:
                return float("nan"), "outside_raster"
            val = float(src.read(1, window=((row, row + 1), (col, col + 1)))[0, 0])
            if src.scales and src.scales[0]:
                val *= float(src.scales[0])
            if src.offsets and src.offsets[0]:
                val += float(src.offsets[0])
            nodata = src.nodata
            if nodata is not None and val == float(nodata):
                return float("nan"), "nodata"
            if not math.isfinite(val):
                return float("nan"), "nodata"
            return val, "ok"
    except Exception:
        return float("nan"), "unreadable"


def fine_mask_5m(root: Path, site_name: str, site: Site) -> HorizonMask:
    tif = root / "data" / "dem" / f"{site_name}_final_adj_5mpp_surf.tif"
    sched = mask_schedule_for_site(site, tif if tif.is_file() else None)
    if sched is None:
        raise FileNotFoundError(f"No DEM schedule for {site_name}")
    return mask(site, schedule=sched)


def cap_mask(site: Site) -> HorizonMask:
    m = nearest_cap_mask(site)
    if m is None:
        raise FileNotFoundError(f"No cap mask for {site.lat_deg}, {site.lon_deg}")
    return m


def mean_sun_fraction(
    site: Site,
    horizon: HorizonMask,
    start: np.datetime64,
    end: np.datetime64,
    *,
    chunk_hours: int = 24 * 30,
    progress_cb=None,
) -> float:
    """Mean hourly sun disc fraction (any-illumination definition) over [start, end]."""
    from moonpark.ephemeris import SpiceEphemeris
    from moonpark.visibility import series

    eph = SpiceEphemeris()
    step = np.timedelta64(1, "h")
    t = np.datetime64(start, "s")
    end_s = np.datetime64(end, "s")
    n_total = int((end_s - t) / step) + 1
    weighted = 0.0
    count = 0
    done = 0
    while t <= end_s:
        t1 = min(end_s, t + np.timedelta64(chunk_hours - 1, "h"))
        times = t + np.arange(int((t1 - t) / step) + 1) * step
        sky = eph.sky(site, times.astype("datetime64[s]"))
        vis = series(
            sky,
            horizon,
            sun_threshold=0.0,
            earth_threshold=0.0,
            bridge_h=0,
            step_min=60,
        )
        fr = np.asarray(vis["sun_fraction"], dtype=np.float64)
        weighted += float(fr.sum())
        count += int(fr.size)
        done += int(fr.size)
        if progress_cb:
            progress_cb(done, n_total)
        t = t1 + step
    return weighted / max(count, 1)


def longest_night_hours(
    site: Site,
    horizon: HorizonMask,
    start: np.datetime64,
    end: np.datetime64,
) -> float:
    from moonpark.ephemeris import SpiceEphemeris
    from moonpark.visibility import series

    step = np.timedelta64(1, "h")
    times = np.arange(np.datetime64(start, "s"), np.datetime64(end, "s") + step, step, dtype="datetime64[s]")
    sky = SpiceEphemeris().sky(site, times)
    vis = series(sky, horizon, sun_threshold=0.0, earth_threshold=0.0, bridge_h=5, step_min=60)
    return float(vis["longest_night_h"])