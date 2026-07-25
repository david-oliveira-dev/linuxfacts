"""Tests for the processes fact — via FakeSource, offline."""

from __future__ import annotations

import pytest

from linuxfacts.exceptions import SourceError
from linuxfacts.facts import processes
from linuxfacts.models import ProcessInfo
from linuxfacts.testing import FakeSource

PROCS = [
    ProcessInfo(1, "idle", 5.0, 1.0),
    ProcessInfo(2, "busy", 90.0, 2.0),
    ProcessInfo(3, "mid", 40.0, 3.0),
]


def test_processes_are_ranked_by_cpu_desc() -> None:
    ranked = processes(FakeSource(processes=PROCS)).unwrap()
    assert [p.name for p in ranked] == ["busy", "mid", "idle"]


def test_top_limits_the_result() -> None:
    top = processes(FakeSource(processes=PROCS), top=2).unwrap()
    assert [p.name for p in top] == ["busy", "mid"]


def test_top_zero_returns_empty() -> None:
    assert processes(FakeSource(processes=PROCS), top=0).unwrap() == []


def test_negative_top_is_a_programmer_error() -> None:
    with pytest.raises(ValueError, match="top must be zero or positive"):
        processes(FakeSource(processes=PROCS), top=-1)


def test_processes_failure_is_unknown() -> None:
    fact = processes(FakeSource(processes=SourceError("psutil down")))
    assert fact.is_unknown
    assert "processes" in (fact.reason or "")
