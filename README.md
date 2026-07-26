# linuxfacts

Typed, testable library for reading Linux system state — disks, memory, systemd units,
ports and packages — with no side effects.

## Problem

Reading Linux system state in Python is repetitive and brittle. Every project reimplements
parsing of `systemctl`, reading `/proc`, `psutil` calls and permission handling. The result
is coupled to I/O and almost impossible to test without a real machine.

This library is a layer above `psutil`, opinionated about three things: everything is
**typed**, everything is **injectable** (so consumers test offline), and absence of
information is never confused with absence of a problem.

## Features

Planned for v1.0 — implemented incrementally:

- Facts for disks, memory, CPU and load, processes, systemd units, listening ports,
  packages and host info
- Every result is an immutable, typed `Fact[T]` with an explicit `ok`/`unknown` state
- A public `FakeSource` so consumers test their own code offline and deterministically
- Read-only by design: no `shell=True`, subprocess with a fixed argument list, never
  requires elevated privilege
- One runtime dependency (`psutil`); `py.typed` so consumers get the types

## Requirements

- Python 3.11, 3.12 or 3.13
- Ubuntu 22.04+ or Debian 12+

## Installation

Not published yet. For local development:

```bash
uv sync
uv run pytest
```

## Usage

```python
import linuxfacts

fact = linuxfacts.disks()
if fact.is_ok:
    for disk in fact.unwrap():
        print(disk.mountpoint, disk.percent_used)
else:
    print("could not read disks:", fact.reason)
```

Every fact returns a `Fact` — either `ok` with a value, or `unknown` with a reason. A
reading that could not be performed (permission denied, a missing command) is `unknown`,
never an exception you must catch and never a silent zero.

### The headline: your code, tested offline

Because every fact reads through an injectable `Source`, the tool *you* build tests without
a real machine. The same call works in production (real system) and in tests (a
`FakeSource`):

```python
# your_tool.py
import linuxfacts
from linuxfacts.sources.base import Source


def disk_warning(source: Source | None = None) -> str | None:
    fact = linuxfacts.disks(source)
    full = [d for d in fact.unwrap_or([]) if d.percent_used > 90]
    return f"{len(full)} disk(s) over 90%" if full else None
```

```python
# test_your_tool.py — offline, deterministic, no real machine
from linuxfacts.models import DiskUsage
from linuxfacts.testing import FakeSource
from your_tool import disk_warning


def test_warns_when_full():
    source = FakeSource(disks=[DiskUsage("/", 100, 95, 5, 95.0)])
    assert disk_warning(source) == "1 disk(s) over 90%"
```

Full documentation, including the testing guide and the compatibility policy, lives in
[`docs/`](docs/index.md) (built with MkDocs).

## Testing

```bash
make check      # ruff + mypy (strict) + pytest with coverage, one Python version
make matrix     # nox across Python 3.11–3.13 (skips missing interpreters)
```

Every test runs offline. Facts are exercised through `FakeSource`; parsers are fed
versioned fixtures of real command output. Minimum coverage: 90% — it is a library, the bar
is higher.

## Design decisions

- [`docs/extraction-scope.md`](docs/extraction-scope.md) — what is extracted from
  `ubuntu-doctor` and what stays, and why
- [`docs/compatibility.md`](docs/compatibility.md) — the SemVer and deprecation promise
- Architecture decision records in [`docs/adr/`](docs/adr/):
  [Fact envelope over exceptions](docs/adr/0001-fact-envelope-over-exceptions.md),
  [protocol-based source injection](docs/adr/0002-protocol-based-source-injection.md),
  [testing utilities are public API](docs/adr/0003-public-testing-utilities.md)

## Limitations

Stated up front:

- Debian/Ubuntu only
- Read-only — never writes to or changes the system
- Synchronous — no async API in v1.0
- No `journald` reading in v1.0

## Roadmap

v1.1 adds `journald` reading and per-interface network facts; v1.2 an optional cache. The
public API is stable within a major version; deprecations warn for at least one minor
version before removal.

## Contributing

Issues and pull requests are welcome. Please read the PR template first.

## License

MIT — see [LICENSE](LICENSE).

## Contact

David Oliveira — davidoliveira.devbr@gmail.com
