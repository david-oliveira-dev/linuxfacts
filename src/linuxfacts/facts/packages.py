"""Packages fact (RF-007).

Two independent checks:

* **Updates** from ``apt list --upgradable`` (runs unprivileged). Security updates are
  recognised by a ``security`` component in the source pocket (e.g. ``noble-security``).
* **Broken packages** from ``dpkg --audit``, which needs the dpkg lock and thus privilege.
  When it cannot run, ``broken`` is ``None`` — the tri-state that keeps "could not check"
  distinct from "none broken" (RN-003), rather than failing the whole fact.

The fact is ``unknown`` only when the update listing itself cannot be read.
"""

from __future__ import annotations

from linuxfacts.exceptions import SourceError
from linuxfacts.models import Fact, PackageStatus
from linuxfacts.sources.base import Source
from linuxfacts.sources.real import RealSource

__all__ = ["packages", "parse_broken", "parse_upgradable"]


def parse_upgradable(text: str) -> tuple[int, int]:
    """Return ``(total, security)`` update counts from ``apt list --upgradable`` (pure).

    Package lines look like ``name/pocket version arch [...]``. Lines without a ``/`` (the
    ``Listing...`` header, blanks) are ignored. Language-independent.
    """
    total = 0
    security = 0
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or "/" not in line:
            continue
        after_slash = line.split("/", 1)[1].split(maxsplit=1)
        if not after_slash:
            continue  # a "name/" line with no pocket is malformed, not an update
        total += 1
        if "security" in after_slash[0]:
            security += 1
    return total, security


def parse_broken(text: str) -> tuple[str, ...]:
    """Return the names of broken packages from ``dpkg --audit`` output (pure)."""
    return tuple(
        line.split(maxsplit=1)[0]
        for raw_line in text.splitlines()
        if (line := raw_line.strip()) and line[0].isalnum()
    )


def packages(source: Source | None = None) -> Fact[PackageStatus]:
    """Read pending updates and broken packages.

    Example:
        >>> from linuxfacts.sources.base import CommandResult
        >>> from linuxfacts.testing import FakeSource
        >>> apt = "Listing...\\nvim/noble-security 2 amd64 [upgradable from: 1]\\n"
        >>> fake = FakeSource(commands={("apt",): CommandResult(apt, "", 0)})
        >>> packages(fake).unwrap().security_updates
        1
    """
    src = source or RealSource()
    try:
        result = src.run_command(["apt", "list", "--upgradable"])
    except SourceError as exc:
        return Fact.unknown(f"could not read packages: {exc}")
    if result.returncode != 0:
        detail = result.stderr.strip() or f"apt exited with {result.returncode}"
        return Fact.unknown(f"could not read packages: {detail}")
    total, security = parse_upgradable(result.stdout)
    return Fact.ok(PackageStatus(total, security, _read_broken(src)))


def _read_broken(source: Source) -> tuple[str, ...] | None:
    """Broken package names, or ``None`` when the check could not run (needs privilege)."""
    try:
        result = source.run_command(["dpkg", "--audit"])
    except SourceError:
        return None
    if result.returncode != 0:
        return None
    return parse_broken(result.stdout)
