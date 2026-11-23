"""Windows portability of moonpark.session_memory.

per D-20261122-pj-f3a8 / D-20261122-pj-a91c: Windows is a claimed platform, so
``moonpark.session_memory`` must import cleanly when the POSIX-only ``resource``
module is missing, and ``process_rss_mb()`` must still return a finite float.
"""

from __future__ import annotations

import importlib
import importlib.abc
import math
import sys

import pytest


class _BlockResource(importlib.abc.MetaPathFinder):
    """Meta-path finder that makes ``import resource`` raise ModuleNotFoundError."""

    def find_spec(self, fullname, path, target=None):  # noqa: ANN001
        if fullname == "resource":
            raise ModuleNotFoundError("No module named 'resource' (simulated Windows)", name="resource")
        return None


@pytest.fixture
def no_resource_module(monkeypatch: pytest.MonkeyPatch):
    """Simulate a platform without ``resource``; restore real modules afterwards."""
    monkeypatch.delitem(sys.modules, "resource", raising=False)
    monkeypatch.delitem(sys.modules, "moonpark.session_memory", raising=False)
    blocker = _BlockResource()
    sys.meta_path.insert(0, blocker)
    try:
        yield
    finally:
        sys.meta_path.remove(blocker)
        # monkeypatch restores sys.modules entries it deleted; drop any
        # module imported under the simulation so later tests see the real one.
        sys.modules.pop("moonpark.session_memory", None)


def test_resource_block_is_effective(no_resource_module) -> None:
    """Sanity check: the simulation really blocks ``import resource``."""
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("resource")


def test_session_memory_imports_without_resource(no_resource_module) -> None:
    """per D-20261122-pj-f3a8 / D-20261122-pj-a91c: import must not crash without ``resource``."""
    mod = importlib.import_module("moonpark.session_memory")
    assert hasattr(mod, "process_rss_mb")


def test_process_rss_mb_finite_without_resource(no_resource_module) -> None:
    """per D-20261122-pj-f3a8 / D-20261122-pj-a91c: RSS probe returns a finite float without ``resource``."""
    mod = importlib.import_module("moonpark.session_memory")
    rss = mod.process_rss_mb()
    assert isinstance(rss, float)
    assert math.isfinite(rss)
    assert rss >= 0.0
