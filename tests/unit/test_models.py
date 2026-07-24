"""Tests for the domain models and the Fact envelope.

Pure, hand-built values only — no system, no clock. The Fact invariants (an unknown fact
carries a reason and no value; an ok fact carries a value) are the contract the whole
library leans on, so they are covered directly and as properties.
"""

from __future__ import annotations

import dataclasses

import pytest
from hypothesis import given
from hypothesis import strategies as st

from linuxfacts.exceptions import UnknownFactError
from linuxfacts.models import (
    CpuInfo,
    DiskUsage,
    Fact,
    FactState,
    HostInfo,
    ListeningPort,
    MemoryInfo,
    PackageStatus,
    ProcessInfo,
    SystemdUnit,
)

# ---------------------------------------------------------------------------
# Fact envelope
# ---------------------------------------------------------------------------


def test_ok_fact_carries_its_value() -> None:
    fact = Fact.ok(42)
    assert fact.is_ok
    assert not fact.is_unknown
    assert fact.state is FactState.OK
    assert fact.unwrap() == 42


def test_unknown_fact_carries_a_reason() -> None:
    fact: Fact[int] = Fact.unknown("permission denied")
    assert fact.is_unknown
    assert not fact.is_ok
    assert fact.reason == "permission denied"
    assert fact.value is None


def test_unwrap_on_unknown_raises() -> None:
    fact: Fact[int] = Fact.unknown("apt is not available")
    with pytest.raises(UnknownFactError, match="apt is not available"):
        fact.unwrap()


def test_unwrap_or_returns_default_when_unknown() -> None:
    missing: Fact[int] = Fact.unknown("no data")
    assert missing.unwrap_or(0) == 0
    assert Fact.ok(7).unwrap_or(0) == 7


def test_unknown_fact_requires_a_nonempty_reason() -> None:
    with pytest.raises(ValueError, match="requires a reason"):
        Fact(state=FactState.UNKNOWN, value=None, reason="   ")
    with pytest.raises(ValueError, match="requires a reason"):
        Fact(state=FactState.UNKNOWN, value=None, reason=None)


def test_unknown_fact_must_not_carry_a_value() -> None:
    with pytest.raises(ValueError, match="must not carry a value"):
        Fact(state=FactState.UNKNOWN, value=1, reason="inconsistent")


def test_ok_fact_must_carry_a_value() -> None:
    with pytest.raises(ValueError, match="must carry a value"):
        Fact(state=FactState.OK, value=None)


def test_fact_is_frozen() -> None:
    fact = Fact.ok(1)
    with pytest.raises(dataclasses.FrozenInstanceError):
        fact.state = FactState.UNKNOWN  # type: ignore[misc]


@given(st.integers())
def test_ok_then_unwrap_roundtrips(value: int) -> None:
    assert Fact.ok(value).unwrap() == value


@given(st.text(min_size=1).filter(lambda s: s.strip()))
def test_unknown_always_keeps_its_reason_and_never_a_value(reason: str) -> None:
    fact: Fact[int] = Fact.unknown(reason)
    assert fact.reason == reason
    assert fact.value is None
    assert fact.is_unknown


# ---------------------------------------------------------------------------
# Domain models are frozen photographs
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "instance",
    [
        DiskUsage("/", 100, 40, 60, 40.0),
        MemoryInfo(100, 50, 50, 50.0, 10, 1, 10.0),
        CpuInfo(0.5, 0.6, 0.7, 8),
        ProcessInfo(1, "init", 0.1, 0.2),
        SystemdUnit("nginx.service", "loaded", "active", "running", "web"),
        ListeningPort("tcp", "0.0.0.0:80", 80, "nginx"),
        PackageStatus(3, 1, ()),
        HostInfo("host", "6.8.0", "Ubuntu 24.04", 123.0),
    ],
)
def test_models_are_frozen(instance: object) -> None:
    field_name = next(iter(dataclasses.fields(instance))).name  # type: ignore[arg-type]
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(instance, field_name, "mutated")


def test_cpu_core_count_may_be_unknown() -> None:
    assert CpuInfo(0.1, 0.2, 0.3, None).core_count is None


def test_listening_port_process_may_be_none() -> None:
    assert ListeningPort("udp", "[::]:53", 53, None).process is None


def test_package_status_distinguishes_unknown_broken_from_none_broken() -> None:
    # None means "could not check broken packages"; () means "checked, none broken".
    assert PackageStatus(0, 0, None).broken is None
    assert PackageStatus(0, 0, ()).broken == ()
