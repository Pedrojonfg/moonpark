"""S12 validation_full gate (D-b591): missing heavy data must fail, not skip as success."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

validation_full = pytest.mark.validation_full


def _has_dem() -> bool:
    dem = ROOT / "data" / "dem"
    return dem.is_dir() and any(dem.glob("*.TIF"))


def _has_pgda69() -> bool:
    for base in (ROOT / "data" / "pgda69", ROOT / "data" / "illumination", ROOT / "data"):
        if not base.is_dir():
            continue
        for pat in ("*AVGVISIB*S*", "*avgvisib*s*", "*PGDA*69*"):
            if list(base.rglob(pat)):
                return True
    return False


@validation_full
def test_short_night_validation_full_gate() -> None:
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "s12_short_night_recheck.py"), "--validation-full"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if _has_dem():
        assert r.returncode == 0, r.stderr + r.stdout
    else:
        assert r.returncode == 2, r.stderr + r.stdout


@validation_full
def test_pgda69_validation_full_gate() -> None:
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "s12_pgda69_compare.py"), "--validation-full"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if _has_pgda69():
        assert r.returncode == 0, r.stderr + r.stdout
    else:
        assert r.returncode == 2, r.stderr + r.stdout