"""Tests for the disk fact — driven entirely through FakeSource, offline."""

from __future__ import annotations

from linuxfacts.exceptions import SourceError
from linuxfacts.facts import disks
from linuxfacts.models import DiskUsage
from linuxfacts.testing import FakeSource


def test_disks_returns_ok_with_the_source_reading() -> None:
    usage = [DiskUsage("/", 100, 40, 60, 40.0), DiskUsage("/boot", 10, 2, 8, 20.0)]
    fact = disks(FakeSource(disks=usage))
    assert fact.is_ok
    assert fact.unwrap() == usage


def test_disks_empty_is_still_ok() -> None:
    fact = disks(FakeSource(disks=[]))
    assert fact.is_ok
    assert fact.unwrap() == []


def test_disks_source_failure_becomes_unknown() -> None:
    fact = disks(FakeSource(disks=SourceError("psutil blew up")))
    assert fact.is_unknown
    assert fact.reason is not None
    assert "disks" in fact.reason


def test_disks_os_error_becomes_unknown() -> None:
    fact = disks(FakeSource(disks=PermissionError("denied")))
    assert fact.is_unknown
    assert "denied" in (fact.reason or "")
