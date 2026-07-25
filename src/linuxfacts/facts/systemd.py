"""systemd units fact (RF-005).

Reads ``systemctl list-units`` (which runs unprivileged and read-only) for a given state
filter — ``failed`` by default. Parsing is tolerant: a line that does not match the
``UNIT LOAD ACTIVE SUB DESCRIPTION`` shape is skipped rather than aborting the parse.
"""

from __future__ import annotations

from linuxfacts.exceptions import SourceError
from linuxfacts.models import Fact, SystemdUnit
from linuxfacts.sources.base import Source
from linuxfacts.sources.real import RealSource

__all__ = ["parse_units", "systemd_units"]


def parse_units(text: str) -> list[SystemdUnit]:
    """Parse ``systemctl list-units --plain --no-legend`` output into units (pure)."""
    units: list[SystemdUnit] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split(maxsplit=4)
        if len(parts) < 4:
            continue
        name, load, active, sub = parts[:4]
        description = parts[4] if len(parts) > 4 else ""
        units.append(SystemdUnit(name, load, active, sub, description))
    return units


def systemd_units(
    source: Source | None = None, *, state: str | None = "failed"
) -> Fact[list[SystemdUnit]]:
    """List systemd units, filtered by ``state`` (``failed`` by default; ``None`` for all).

    Example:
        >>> from linuxfacts.sources.base import CommandResult
        >>> from linuxfacts.testing import FakeSource
        >>> out = "nginx.service loaded failed failed Web server\\n"
        >>> fake = FakeSource(commands={("systemctl",): CommandResult(out, "", 0)})
        >>> systemd_units(fake).unwrap()[0].name
        'nginx.service'
    """
    args = ["systemctl", "list-units", "--no-legend", "--no-pager", "--plain"]
    if state is not None:
        args.append(f"--state={state}")
    try:
        result = (source or RealSource()).run_command(args)
    except SourceError as exc:
        return Fact.unknown(f"could not list systemd units: {exc}")
    if result.returncode != 0:
        detail = result.stderr.strip() or f"systemctl exited with {result.returncode}"
        return Fact.unknown(f"could not list systemd units: {detail}")
    return Fact.ok(parse_units(result.stdout))
