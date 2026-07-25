"""Public API contract test.

The public surface is a promise: within a major version, nothing here may be removed and
no signature may change (RN-005, RN-006). This test freezes that surface. When it fails,
either the change is intentional — and this test is updated in the same commit, along with
a major version bump if a symbol was removed or a signature changed — or the change was an
accident this test just caught.
"""

from __future__ import annotations

import inspect

import linuxfacts
from linuxfacts.sources.base import Source
from linuxfacts.testing import FakeSource

# The exact set of public names. Removing one is a breaking change (major bump).
EXPECTED_PUBLIC = {
    # facts
    "disks",
    "memory",
    "cpu",
    "processes",
    "systemd_units",
    "listening_ports",
    "packages",
    "host",
    # envelope and models
    "Fact",
    "FactState",
    "DiskUsage",
    "MemoryInfo",
    "CpuInfo",
    "ProcessInfo",
    "SystemdUnit",
    "ListeningPort",
    "PackageStatus",
    "HostInfo",
    # errors
    "LinuxFactsError",
    # metadata
    "__version__",
}

# Parameter names of every public fact — a rename or reorder is a breaking change.
EXPECTED_FACT_PARAMS = {
    "disks": ["source"],
    "memory": ["source"],
    "cpu": ["source"],
    "processes": ["source", "top"],
    "systemd_units": ["source", "state"],
    "listening_ports": ["source"],
    "packages": ["source"],
    "host": ["source"],
}


def test_public_surface_is_exactly_the_declared_set() -> None:
    assert set(linuxfacts.__all__) == EXPECTED_PUBLIC


def test_every_declared_name_is_actually_importable() -> None:
    for name in linuxfacts.__all__:
        assert hasattr(linuxfacts, name), f"{name} is in __all__ but not importable"


def test_no_duplicate_names_in_all() -> None:
    assert len(linuxfacts.__all__) == len(set(linuxfacts.__all__))


def test_fact_signatures_are_frozen() -> None:
    for name, params in EXPECTED_FACT_PARAMS.items():
        fn = getattr(linuxfacts, name)
        actual = list(inspect.signature(fn).parameters)
        assert actual == params, f"signature of {name} changed: {actual} != {params}"


def test_every_fact_accepts_a_source() -> None:
    for name in EXPECTED_FACT_PARAMS:
        signature = inspect.signature(getattr(linuxfacts, name))
        assert "source" in signature.parameters


def test_a_fact_runs_offline_through_the_public_api() -> None:
    fact = linuxfacts.disks(FakeSource(disks=[linuxfacts.DiskUsage("/", 1, 0, 1, 0.0)]))
    assert fact.is_ok
    assert fact.unwrap()[0].mountpoint == "/"


def test_testing_double_is_public_and_conforms() -> None:
    assert isinstance(FakeSource(), Source)
