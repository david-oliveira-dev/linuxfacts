# linuxfacts

Typed, testable library for reading Linux system state — disks, memory, systemd units,
ports and packages — with no side effects.

> **Status: in development.** The scaffold, tooling and extraction analysis are in place;
> the `Fact` envelope, models, `FakeSource` and the facts land phase by phase. Sections
> below are filled in as the corresponding phase completes.

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

Filled in with real, runnable examples as the facts land (Phase 4). The headline example —
the same code tested offline with `FakeSource` and run against the real system — is the
whole point of the library and lands with the testing guide.

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

Architecture decision records land in `docs/adr/` as the decisions are made.

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
