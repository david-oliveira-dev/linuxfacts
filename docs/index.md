# LinuxFacts

Typed, testable, read-only access to Linux system state — disks, memory, CPU and load,
processes, systemd units, listening ports, packages and host info.

LinuxFacts is a thin, opinionated layer above `psutil`. It is opinionated about three
things:

- **Everything is typed.** Facts are immutable dataclasses, not dictionaries.
- **Everything is injectable.** Every fact reads through a `Source` you can replace, so you
  test your own tool offline — see [Testing your code](testing.md).
- **Unknown is not the same as fine.** A reading that could not be performed is an explicit
  `unknown` fact with a reason, never a silent zero and never an exception you must catch.

```python
import linuxfacts

fact = linuxfacts.disks()
if fact.is_ok:
    for disk in fact.unwrap():
        print(disk.mountpoint, disk.percent_used)
else:
    print("could not read disks:", fact.reason)
```

## Why it exists

LinuxFacts was **extracted** from a real tool (`ubuntu-doctor`) when a second tool needed
the same readings — the legitimate reason a library is born. It reads facts; it does not
judge them. Severity, thresholds and recommendations are the *consumer's* policy, not the
library's.

## Install

```bash
pip install linuxfacts
```

Requires Python 3.11+ on Debian/Ubuntu.

## Where to go next

- [Usage](usage.md) — the facts and the `Fact` envelope
- [Testing your code](testing.md) — the `FakeSource`, the headline feature
- [API reference](api.md) — every public function and model
- [Compatibility](compatibility.md) — the SemVer and deprecation promise
