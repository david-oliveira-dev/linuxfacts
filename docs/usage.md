# Usage

## The facts

Each fact is a function that takes an optional `source` and returns a `Fact`.

```python
import linuxfacts

linuxfacts.disks()             # Fact[list[DiskUsage]]
linuxfacts.memory()            # Fact[MemoryInfo]
linuxfacts.cpu()               # Fact[CpuInfo]
linuxfacts.processes(top=10)   # Fact[list[ProcessInfo]] — heaviest first
linuxfacts.systemd_units(state="failed")   # Fact[list[SystemdUnit]]
linuxfacts.listening_ports()   # Fact[list[ListeningPort]]
linuxfacts.packages()          # Fact[PackageStatus]
linuxfacts.host()              # Fact[HostInfo]
```

## The Fact envelope

A `Fact` is either **ok** with a value, or **unknown** with a reason. Handle it explicitly:

```python
fact = linuxfacts.memory()

if fact.is_ok:
    print(fact.unwrap().percent_used)
else:
    print("unavailable:", fact.reason)
```

Three ways to get the value out, from strictest to most forgiving:

```python
fact.unwrap()          # returns the value, or raises UnknownFactError if unknown
fact.unwrap_or(0.0)    # returns the value, or a default if unknown
fact.value             # the value, or None if unknown (you check yourself)
```

`unwrap()` is deliberate: use it where an unknown reading is unacceptable and should fail
loudly rather than pass silently as `None`.

## Why unknown, not an exception

Expected failures — a mount you cannot read, a command that needs privilege, a missing
binary — do not raise. They return `unknown`:

```python
fact = linuxfacts.packages()
# On a machine where apt is unavailable:
#   fact.is_unknown is True
#   fact.reason explains what could not be read
```

Only programmer errors raise. For example, a negative `top` is a bug, not a system
condition:

```python
linuxfacts.processes(top=-1)   # raises ValueError
```

## Notes on specific facts

- **`processes`** returns name and PID only — never the command line, which can hold
  secrets. Pass `top=N` to keep only the heaviest N.
- **`packages().broken`** is a tri-state: a tuple of names when checked, `()` when checked
  and none are broken, and `None` when it could not be checked (that needs privilege). The
  fact is only `unknown` when the update listing itself fails.
- **`listening_ports`**: a socket whose owning process cannot be named (another user's, no
  privilege) is still listed, with `process=None`.
