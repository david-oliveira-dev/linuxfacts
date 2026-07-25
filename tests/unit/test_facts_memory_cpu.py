"""Tests for the memory and cpu facts — via FakeSource, offline."""

from __future__ import annotations

from linuxfacts.exceptions import SourceError
from linuxfacts.facts import cpu, memory
from linuxfacts.models import CpuInfo, MemoryInfo
from linuxfacts.testing import FakeSource

MEM = MemoryInfo(16_000, 8_000, 8_000, 50.0, 4_000, 1_000, 25.0)
CPU = CpuInfo(0.5, 0.6, 0.7, 8)


def test_memory_ok() -> None:
    fact = memory(FakeSource(memory=MEM))
    assert fact.is_ok
    assert fact.unwrap() == MEM


def test_memory_failure_is_unknown() -> None:
    fact = memory(FakeSource(memory=SourceError("boom")))
    assert fact.is_unknown
    assert "memory" in (fact.reason or "")


def test_cpu_ok() -> None:
    fact = cpu(FakeSource(cpu=CPU))
    assert fact.is_ok
    assert fact.unwrap().core_count == 8


def test_cpu_unknown_core_count_is_still_ok() -> None:
    fact = cpu(FakeSource(cpu=CpuInfo(0.1, 0.2, 0.3, None)))
    assert fact.is_ok
    assert fact.unwrap().core_count is None


def test_cpu_failure_is_unknown() -> None:
    fact = cpu(FakeSource(cpu=OSError("no /proc")))
    assert fact.is_unknown
