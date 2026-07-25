"""Tests for the real source's mapping logic, offline.

No real system is touched: psutil, os, subprocess and time are substituted (the same
module objects the real source imports), so the mapping from raw readings to domain
models is exercised deterministically. Behaviour against a live machine is covered by the
integration job.
"""

from __future__ import annotations

import os
import subprocess
import time
from collections.abc import Iterable, Sequence
from pathlib import Path
from types import SimpleNamespace

import psutil
import pytest

from linuxfacts.exceptions import CommandNotFoundError, CommandTimeoutError
from linuxfacts.sources import real
from linuxfacts.sources.real import RealSource, parse_os_release

# ---------------------------------------------------------------------------
# parse_os_release (pure)
# ---------------------------------------------------------------------------


def test_parse_os_release_strips_quotes_and_ignores_noise() -> None:
    text = '# a comment\nNAME="Ubuntu"\nVERSION_ID=24.04\n\ngarbage-without-equals\n'
    data = parse_os_release(text)
    assert data["NAME"] == "Ubuntu"
    assert data["VERSION_ID"] == "24.04"
    assert "garbage-without-equals" not in data


def test_parse_os_release_empty_is_empty() -> None:
    assert dict(parse_os_release("")) == {}


# ---------------------------------------------------------------------------
# read_disks
# ---------------------------------------------------------------------------


def _part(mountpoint: str, fstype: str) -> SimpleNamespace:
    return SimpleNamespace(mountpoint=mountpoint, fstype=fstype, device="/dev/x")


def _usage(total: int, used: int, free: int, percent: float) -> SimpleNamespace:
    return SimpleNamespace(total=total, used=used, free=free, percent=percent)


def test_read_disks_filters_and_maps(monkeypatch: pytest.MonkeyPatch) -> None:
    partitions = [
        _part("/", "ext4"),
        _part("/snap/x", "squashfs"),  # pseudo → excluded
        _part("/empty", "ext4"),  # total 0 → skipped
        _part("/denied", "ext4"),  # raises → skipped
    ]
    usages = {"/": _usage(100, 40, 60, 40.0), "/empty": _usage(0, 0, 0, 0.0)}

    def fake_usage(mountpoint: str) -> SimpleNamespace:
        if mountpoint == "/denied":
            raise OSError("permission denied")
        return usages[mountpoint]

    monkeypatch.setattr(psutil, "disk_partitions", lambda all=False: partitions)
    monkeypatch.setattr(psutil, "disk_usage", fake_usage)

    disks = RealSource().read_disks()
    assert len(disks) == 1
    assert disks[0].mountpoint == "/"
    assert disks[0].percent_used == 40.0


# ---------------------------------------------------------------------------
# read_memory / read_cpu / read_processes
# ---------------------------------------------------------------------------


def test_read_memory_maps_virtual_and_swap(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        psutil,
        "virtual_memory",
        lambda: SimpleNamespace(total=16, available=8, used=8, percent=50.0),
    )
    monkeypatch.setattr(
        psutil, "swap_memory", lambda: SimpleNamespace(total=4, used=1, percent=25.0)
    )
    memory = RealSource().read_memory()
    assert memory.total_bytes == 16
    assert memory.available_bytes == 8
    assert memory.swap_percent == 25.0


def test_read_cpu_maps_load_and_cores(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(os, "getloadavg", lambda: (0.5, 0.6, 0.7))
    monkeypatch.setattr(os, "cpu_count", lambda: 8)
    cpu = RealSource().read_cpu()
    assert (cpu.load1, cpu.load5, cpu.load15) == (0.5, 0.6, 0.7)
    assert cpu.core_count == 8


def test_read_processes_maps_and_tolerates_missing_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    procs = [
        SimpleNamespace(info={"pid": 1, "name": "init", "cpu_percent": 0.1, "memory_percent": 0.2}),
        SimpleNamespace(
            info={"pid": None, "name": None, "cpu_percent": None, "memory_percent": None}
        ),
    ]

    def fake_iter(attrs: Iterable[str]) -> Iterable[SimpleNamespace]:
        return procs

    monkeypatch.setattr(psutil, "process_iter", fake_iter)
    processes = RealSource().read_processes()
    assert processes[0].name == "init"
    assert processes[1].pid == 0  # missing values fall back safely
    assert processes[1].name == "?"


# ---------------------------------------------------------------------------
# read_host
# ---------------------------------------------------------------------------


def test_read_host_assembles_identity_and_uptime(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        os, "uname", lambda: SimpleNamespace(nodename="box", release="6.8.0-generic")
    )
    monkeypatch.setattr(psutil, "boot_time", lambda: 1000.0)
    monkeypatch.setattr(time, "time", lambda: 1500.0)
    monkeypatch.setattr(
        RealSource, "_os_release_text", staticmethod(lambda: 'PRETTY_NAME="Ubuntu 24.04 LTS"')
    )
    host = RealSource().read_host()
    assert host.hostname == "box"
    assert host.kernel == "6.8.0-generic"
    assert host.distribution == "Ubuntu 24.04 LTS"
    assert host.uptime_seconds == 500.0


def test_read_host_distribution_falls_back_to_name_and_version(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(os, "uname", lambda: SimpleNamespace(nodename="b", release="6"))
    monkeypatch.setattr(psutil, "boot_time", lambda: 0.0)
    monkeypatch.setattr(time, "time", lambda: 0.0)
    monkeypatch.setattr(
        RealSource, "_os_release_text", staticmethod(lambda: 'NAME="Debian"\nVERSION="12"')
    )
    assert RealSource().read_host().distribution == "Debian 12"


def test_read_host_distribution_unknown_when_os_release_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(os, "uname", lambda: SimpleNamespace(nodename="b", release="6"))
    monkeypatch.setattr(psutil, "boot_time", lambda: 0.0)
    monkeypatch.setattr(time, "time", lambda: 0.0)
    monkeypatch.setattr(RealSource, "_os_release_text", staticmethod(lambda: ""))
    assert RealSource().read_host().distribution == "unknown"


def test_os_release_text_reads_first_existing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    real_path = tmp_path / "os-release"
    real_path.write_text('NAME="X"', encoding="utf-8")
    monkeypatch.setattr(real, "_OS_RELEASE_PATHS", (Path("/nonexistent/os-release"), real_path))
    assert "NAME" in RealSource._os_release_text()


# ---------------------------------------------------------------------------
# run_command
# ---------------------------------------------------------------------------


def test_run_command_captures_output(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(args: Sequence[str], **kwargs: object) -> SimpleNamespace:
        return SimpleNamespace(stdout="out", stderr="err", returncode=0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = RealSource().run_command(["echo", "hi"])
    assert result.stdout == "out"
    assert result.returncode == 0


def test_run_command_missing_binary_raises_typed(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(args: Sequence[str], **kwargs: object) -> SimpleNamespace:
        raise FileNotFoundError

    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(CommandNotFoundError, match="nonesuch"):
        RealSource().run_command(["nonesuch"])


def test_run_command_timeout_raises_typed(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(args: Sequence[str], **kwargs: object) -> SimpleNamespace:
        raise subprocess.TimeoutExpired(cmd="slow", timeout=1.0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(CommandTimeoutError, match="slow"):
        RealSource().run_command(["slow"], timeout=1.0)
