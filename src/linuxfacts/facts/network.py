"""Listening ports fact (RF-006).

Parses ``ss -tulpn``. Without privilege ``ss`` cannot name processes owned by other users;
those ports are still listed, with ``process`` left as ``None`` — graceful degradation, not
an error.
"""

from __future__ import annotations

import re

from linuxfacts.exceptions import SourceError
from linuxfacts.models import Fact, ListeningPort
from linuxfacts.sources.base import Source
from linuxfacts.sources.real import RealSource

__all__ = ["listening_ports", "parse_ports"]

_LISTENING_STATES = frozenset({"LISTEN", "UNCONN"})
_PROCESS_NAME = re.compile(r'"([^"]+)"')


def _parse_port(local: str) -> int | None:
    head, _, tail = local.rpartition(":")
    return int(tail) if head and tail.isdigit() else None


def parse_ports(text: str) -> list[ListeningPort]:
    """Parse ``ss -tulpn`` output into listening ports (pure)."""
    ports: list[ListeningPort] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("Netid"):
            continue
        fields = line.split()
        if len(fields) < 6 or fields[1] not in _LISTENING_STATES:
            continue
        port = _parse_port(fields[4])
        if port is None:
            continue
        process_field = " ".join(fields[6:]) if len(fields) > 6 else ""
        match = _PROCESS_NAME.search(process_field)
        ports.append(
            ListeningPort(
                protocol=fields[0],
                local_address=fields[4],
                port=port,
                process=match.group(1) if match else None,
            )
        )
    return ports


def listening_ports(source: Source | None = None) -> Fact[list[ListeningPort]]:
    """List listening TCP/UDP sockets.

    Example:
        >>> from linuxfacts.sources.base import CommandResult
        >>> from linuxfacts.testing import FakeSource
        >>> out = "Netid State Recv-Q Send-Q Local:Port Peer:Port Process\\n"
        >>> out += 'tcp LISTEN 0 128 0.0.0.0:80 0.0.0.0:* users:(("nginx",pid=1,fd=6))\\n'
        >>> fake = FakeSource(commands={("ss",): CommandResult(out, "", 0)})
        >>> listening_ports(fake).unwrap()[0].port
        80
    """
    try:
        result = (source or RealSource()).run_command(["ss", "-tulpn"])
    except SourceError as exc:
        return Fact.unknown(f"could not list listening ports: {exc}")
    if result.returncode != 0:
        detail = result.stderr.strip() or f"ss exited with {result.returncode}"
        return Fact.unknown(f"could not list listening ports: {detail}")
    return Fact.ok(parse_ports(result.stdout))
