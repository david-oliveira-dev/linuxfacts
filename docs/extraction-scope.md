# Extraction scope from ubuntu-doctor

Phase 0 deliverable. LinuxFacts is not a fresh idea — it is **extracted** from the
collection layer of `ubuntu-doctor`. This document decides, from the real code, exactly
what migrates into the library and what stays in the application. Nothing migrates by
anticipation; the guiding line is a single distinction.

## The distinction: fact vs policy

`ubuntu-doctor` mixes two concerns inside every collector module:

- **Collection** — reading raw system state through injected callables (`collect_*`
  functions and their frozen dataclasses).
- **Evaluation** — turning that state into a `Finding` with a `Severity` and a
  recommendation, by applying configurable thresholds (`evaluate_*` functions + `rules.py`).

A **fact** is neutral: `/` is 82% full, `nginx.service` is `active/running`, port 5432 is
listening. A **policy** is a judgement: 82% is a WARNING, a failed unit is CRITICAL, a
security update deserves attention. LinuxFacts owns facts. Policy stays in `ubuntu-doctor`
— its `rules.py` docstring even calls itself "the pure heart of the tool". Moving policy
into the library would be extracting the wrong thing: two different consumers
(`ubuntu-doctor`, and later `sentinel-agent`) need the same facts but may judge them
differently.

## What migrates (the collection side)

Per `ubuntu-doctor` collector, the raw dataclass and the reading logic migrate; the
`evaluate_*` half is left behind.

| ubuntu-doctor | migrates as | notes |
| --- | --- | --- |
| `collect_disk` + `DiskUsage` | `disks()` → `DiskUsage` | drop `device`/`fstype`-based severity; keep pseudo-fs filtering as a neutral read choice |
| `collect_memory` + `MemoryUsage` | `memory()` → `MemoryInfo` | available-vs-free reasoning is a *reading* choice, keep it |
| `collect_cpu` + `CpuLoad` | `cpu()` → `CpuInfo` | load averages + core count |
| `ProcessInfo` (top-N in cpu.py) | `processes(top=N)` → `ProcessInfo` | promote to its own fact; name+pid only, no cmdline |
| `parse_failed_units` + `ServiceUnit` | `systemd_units(state=...)` → `SystemdUnit` | generalise from failed-only to any state filter |
| `parse_listening_ports` + `ListeningPort` | `listening_ports()` → `ListeningPort` | process `None` on permission denial stays graceful |
| `parse_upgradable` + broken parsing | `packages()` → `PackageStatus` | merge the two checks into one fact; degrade if apt/dpkg absent |
| `system.py` `run_command` | the real `Source` | timeout + typed errors become the library's subprocess helper |
| the injected-callable pattern (`PartitionsFn`, `CommandRunner`, ...) | `Source` Protocol | one seam instead of per-collector callables |

## What stays in ubuntu-doctor

- **`rules.py`** in full — `Thresholds`, `*_severity`, `*_recommendation`. Pure policy.
- Every **`evaluate_*`** function — they exist only to apply policy.
- **`Finding` / `Severity`** models — they are about judgement. LinuxFacts uses `Fact[T]`
  with `FactState` (`ok` / `unknown`) instead.
- **`orchestrator.py`, `cli.py`, `render/`, `config.py`** — the application shell.
- **`formatting.human_bytes`** — presentation. The library returns raw byte counts;
  formatting is the consumer's job.
- The **logs collector** (`collect_logs`) — "large log files above a threshold" is a
  diagnostic heuristic, not a neutral fact, and it is out of the v1.0 scope (spec §4). It
  stays.

## What is new in LinuxFacts

- **`host()` → `HostInfo`** (kernel, distro, uptime, hostname). `ubuntu-doctor` has no host
  collector; this is genuinely new surface, not a migration.

## The key transformation: `Fact[T]` replaces raise-then-catch

`ubuntu-doctor` handles the unreadable case by raising `CollectorError`, which the
orchestrator catches and turns into an `UNKNOWN` finding. A library has no orchestrator to
lean on, and raising for an *expected* condition (permission denied, missing command)
would force every consumer into `try/except`.

So the extraction inverts it: each fact returns `Fact[T]` with an explicit `state`
(`ok`/`unknown`) and a `reason` when unknown. Absence of information is a first-class
return value, never an exception (RN-001, RN-003). Exceptions are reserved for programmer
error and genuinely unexpected failures (RN-002). This is the single most important design
change between the two.

## Models mapping

| Fact | Fields (from ubuntu-doctor, trimmed to what is neutral) |
| --- | --- |
| `DiskUsage` | mountpoint, total_bytes, used_bytes, free_bytes, percent_used |
| `MemoryInfo` | total, available, used, percent + swap total/used/percent |
| `CpuInfo` | load1/5/15, core_count |
| `ProcessInfo` | pid, name, cpu_percent, memory_percent |
| `SystemdUnit` | name, load_state, active_state, sub_state, description |
| `ListeningPort` | protocol, local_address, port, process\|None |
| `PackageStatus` | total_updates, security_updates, broken (or unknown) |
| `HostInfo` | hostname, kernel, distro, uptime_seconds |

## Dependencies and fixtures

- Runtime dependency stays at **one**: `psutil` (RNF-005). `subprocess` (stdlib) backs
  systemd/ports/packages. No Pydantic — frozen dataclasses suffice.
- Command fixtures (`systemctl`, `ss`, `apt`) already exist, captured and sanitised, in
  `ubuntu-doctor/tests/fixtures/`. They are reused (re-captured on this machine when a new
  shape is needed) rather than invented.

## Conclusion

Migrate the eight facts (seven from `ubuntu-doctor`, plus the new `host`) and the
subprocess seam; leave all severity, thresholds and application code behind. The library is
the neutral *what*; `ubuntu-doctor` keeps the opinionated *so what*.
