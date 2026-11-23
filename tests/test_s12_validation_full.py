"""S12 validation_full gate (D-b591): missing heavy data must fail, not skip as success.

per D-20261122-pj-a64b (claims must distinguish local-science green vs CI-missing-data fail):

- Local with heavy data present: green means the scientific compare actually ran
  (``--validation-full`` alone must force the run; HARNESS_READY without compare is not green).
- CI without heavy data: the script exits non-zero (2) and the job fails (D-b591).
- A pytest pass on exit code 2 only proves the missing-data path; it says nothing
  about the science.

The ``test_*_validation_full_forces_*`` tests below are light (heavy work is stubbed)
and run in the default pytest selection; the subprocess gate tests need the
``validation_full`` marker.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from types import ModuleType

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

def _load_script(name: str) -> ModuleType:
    """Load a scripts/*.py file as a fresh module (scripts/ is not a package)."""
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"_s12_under_test_{name}", path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_short_night_validation_full_forces_science_when_dem_present(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """per D-20261122-pj-a64b: with DEM present, ONLY --validation-full must run the compare.

    Heavy ``_run`` is stubbed; we assert it was invoked and the payload is not
    HARNESS_READY_AWAITING_OVERNIGHT (no skip-compare path).
    """
    mod = _load_script("s12_short_night_recheck")
    calls: list[int] = []

    def fake_run(year: int, *, resume_rows: list[dict], resume_at: int):
        calls.append(year)
        return [], "complete", []

    monkeypatch.setattr(mod, "_dem_ok", lambda: True)
    monkeypatch.setattr(mod, "_run", fake_run)
    monkeypatch.setattr(sys, "argv", ["s12_short_night_recheck.py", "--validation-full"])

    rc = mod.main()
    out = capsys.readouterr().out

    assert rc == 0
    assert calls, "--validation-full with DEM present must call _run (science), not skip as harness-ready"
    assert "HARNESS_READY_AWAITING_OVERNIGHT" not in out


def test_pgda69_validation_full_forces_science_when_data_present(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    """per D-20261122-pj-a64b: with PGDA 69 present, ONLY --validation-full must run the compare.

    Heavy ``_run_compare`` is stubbed; we assert it was invoked and the payload is
    not HARNESS_READY_AWAITING_OVERNIGHT (no skip-compare path).
    """
    mod = _load_script("s12_pgda69_compare")
    calls: list[Path] = []
    fake_map = tmp_path / "AVGVISIB_fake.TIF"

    def fake_compare(pgda_path: Path, *, resume_rows: list[dict], resume_at: int, checkpoint=None):
        calls.append(pgda_path)
        return [], "complete"

    monkeypatch.setattr(mod, "_find_pgda69", lambda: fake_map)
    monkeypatch.setattr(mod, "_run_compare", fake_compare)
    monkeypatch.setattr(sys, "argv", ["s12_pgda69_compare.py", "--validation-full"])

    rc = mod.main()
    out = capsys.readouterr().out

    assert rc == 0
    assert calls, "--validation-full with PGDA69 present must call _run_compare (science), not skip as harness-ready"
    assert "HARNESS_READY_AWAITING_OVERNIGHT" not in out
