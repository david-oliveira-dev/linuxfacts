"""The real system source, backed by ``psutil``, ``subprocess`` and ``os``.

This is the only module that actually touches the machine. It never writes, never runs a
command through a shell, never asks for privilege, and puts a timeout on every command
(RNF-001, RN-004). Its structured readings map ``psutil``/``os`` values into the domain
models; command output is returned verbatim for the facts to parse.

It is exercised by the integration job on a clean Ubuntu container, and its mapping logic
is unit-tested offline by substituting the ``psutil``/``subprocess`` calls.
"""

from __future__ import annotations

import os
import subprocess
import time
from collections.abc import Mapping, Sequence
from pathlib import Path

import psutil

from linuxfacts.exceptions import CommandNotFoundError, CommandTimeoutError
from linuxfacts.models import CpuInfo, DiskUsage, HostInfo, MemoryInfo, ProcessInfo
from linuxfacts.sources.base import DEFAULT_TIMEOUT, CommandResult

__all__ = ["RealSource", "parse_os_release"]

# Virtual/pseudo filesystems that are not real, actionable disks.
_EXCLUDED_FSTYPES: frozenset[str] = frozenset(
    {"squashfs", "overlay", "devtmpfs", "tmpfs", "ramfs", "autofs", ""}
)

_OS_RELEASE_PATHS = (Path("/etc/os-release"), Path("/usr/lib/os-release"))


def parse_os_release(text: str) -> Mapping[str, str]:
    """Parse ``os-release`` ``KEY=value`` lines into a mapping (pure).

    Values may be quoted; surrounding single or double quotes are stripped. Blank lines
    and comments are ignored, and a line without ``=`` is skipped rather than fatal.
    """
    data: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        data[key.strip()] = value.strip().strip("\"'")
    return data


def _distribution(os_release: Mapping[str, str]) -> str:
    if pretty := os_release.get("PRETTY_NAME"):
        return pretty
    name = os_release.get("NAME")
    version = os_release.get("VERSION")
    if name and version:
        return f"{name} {version}"
    return name or "unknown"


class RealSource:
    """A :class:`~linuxfacts.sources.base.Source` reading the live system."""

    def run_command(
        self, args: Sequence[str], *, timeout: float = DEFAULT_TIMEOUT
    ) -> CommandResult:
        try:
            completed = subprocess.run(
                list(args),
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except FileNotFoundError as exc:
            raise CommandNotFoundError(f"command not found: {args[0]}") from exc
        except subprocess.TimeoutExpired as exc:
            raise CommandTimeoutError(f"command timed out after {timeout}s: {args[0]}") from exc
        return CommandResult(
            stdout=completed.stdout,
            stderr=completed.stderr,
            returncode=completed.returncode,
        )

    def read_disks(self) -> list[DiskUsage]:
        disks: list[DiskUsage] = []
        for part in psutil.disk_partitions(all=False):
            if part.fstype in _EXCLUDED_FSTYPES:
                continue
            try:
                usage = psutil.disk_usage(part.mountpoint)
            except OSError:
                continue  # a transiently unreadable mount is skipped, not fatal
            if usage.total == 0:
                continue
            disks.append(
                DiskUsage(
                    mountpoint=part.mountpoint,
                    total_bytes=usage.total,
                    used_bytes=usage.used,
                    free_bytes=usage.free,
                    percent_used=usage.percent,
                )
            )
        return disks

    def read_memory(self) -> MemoryInfo:
        vm = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return MemoryInfo(
            total_bytes=vm.total,
            available_bytes=vm.available,
            used_bytes=vm.used,
            percent_used=vm.percent,
            swap_total_bytes=swap.total,
            swap_used_bytes=swap.used,
            swap_percent=swap.percent,
        )

    def read_cpu(self) -> CpuInfo:
        load1, load5, load15 = os.getloadavg()
        return CpuInfo(
            load1=load1,
            load5=load5,
            load15=load15,
            core_count=os.cpu_count(),
        )

    def read_processes(self) -> list[ProcessInfo]:
        processes: list[ProcessInfo] = []
        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
            info = proc.info
            processes.append(
                ProcessInfo(
                    pid=int(info.get("pid") or 0),
                    name=str(info.get("name") or "?"),
                    cpu_percent=float(info.get("cpu_percent") or 0.0),
                    memory_percent=float(info.get("memory_percent") or 0.0),
                )
            )
        return processes

    def read_host(self) -> HostInfo:
        uname = os.uname()
        os_release = parse_os_release(self._os_release_text())
        uptime = max(0.0, time.time() - psutil.boot_time())
        return HostInfo(
            hostname=uname.nodename,
            kernel=uname.release,
            distribution=_distribution(os_release),
            uptime_seconds=uptime,
        )

    @staticmethod
    def _os_release_text() -> str:
        for path in _OS_RELEASE_PATHS:
            try:
                return path.read_text(encoding="utf-8")
            except OSError:
                continue
        return ""
