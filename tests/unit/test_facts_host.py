"""Tests for the host fact — via FakeSource, offline."""

from __future__ import annotations

from linuxfacts.exceptions import SourceError
from linuxfacts.facts import host
from linuxfacts.models import HostInfo
from linuxfacts.testing import FakeSource

HOST = HostInfo("box", "6.8.0-generic", "Ubuntu 24.04 LTS", 3600.0)


def test_host_ok() -> None:
    fact = host(FakeSource(host=HOST))
    assert fact.is_ok
    assert fact.unwrap() == HOST


def test_host_failure_is_unknown() -> None:
    fact = host(FakeSource(host=SourceError("no uname")))
    assert fact.is_unknown
    assert "host" in (fact.reason or "")
