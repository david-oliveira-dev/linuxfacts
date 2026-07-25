# Testing your code

This is the reason LinuxFacts exists. Because every fact reads through an injectable
`Source`, you can test the tool *you* build on top of it without a real machine and without
mocking `psutil` yourself. The library ships the double for you: `FakeSource`, in
`linuxfacts.testing`.

## The idea

Your code calls a fact and passes it a source. In production the source defaults to the
real system; in tests you pass a `FakeSource` with canned readings.

```python
# your_tool.py
import linuxfacts
from linuxfacts.sources.base import Source

def disk_warning(source: Source | None = None) -> str | None:
    fact = linuxfacts.disks(source)
    if fact.is_unknown:
        return None
    full = [d for d in fact.unwrap() if d.percent_used > 90]
    return f"{len(full)} disk(s) over 90%" if full else None
```

The test is a few lines, offline and deterministic:

```python
# test_your_tool.py
from linuxfacts.models import DiskUsage
from linuxfacts.testing import FakeSource
from your_tool import disk_warning

def test_warns_when_a_disk_is_full():
    source = FakeSource(disks=[DiskUsage("/", 100, 95, 5, 95.0)])
    assert disk_warning(source) == "1 disk(s) over 90%"

def test_quiet_when_disks_are_healthy():
    source = FakeSource(disks=[DiskUsage("/", 100, 10, 90, 10.0)])
    assert disk_warning(source) is None
```

Run against the real system, the exact same `disk_warning()` call works — you just omit the
source.

## Simulating failure

Pass an exception instead of a value to exercise the `unknown` path — no broken machine
required:

```python
from linuxfacts.exceptions import CommandNotFoundError
from linuxfacts.testing import FakeSource

def test_handles_missing_apt():
    source = FakeSource(commands={("apt",): CommandNotFoundError("no apt")})
    assert linuxfacts.packages(source).is_unknown
```

## Command-backed facts

`systemd_units`, `listening_ports` and `packages` run commands. Map the command to canned
output. A single-element key matches any call to that program; a full tuple matches exactly:

```python
from linuxfacts.sources.base import CommandResult
from linuxfacts.testing import FakeSource

output = "nginx.service loaded failed failed Web server\n"
source = FakeSource(commands={("systemctl",): CommandResult(output, "", 0)})
assert linuxfacts.systemd_units(source).unwrap()[0].name == "nginx.service"
```

A reading you never configure raises only if your code under test actually calls it, so you
set up just the facts you use.
