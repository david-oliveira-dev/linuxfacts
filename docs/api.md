# API reference

The public API is exactly the names exported from `linuxfacts`, plus `FakeSource` from
`linuxfacts.testing`. Everything else is private.

## Facts

::: linuxfacts.facts.disk.disks
::: linuxfacts.facts.memory.memory
::: linuxfacts.facts.cpu.cpu
::: linuxfacts.facts.process.processes
::: linuxfacts.facts.systemd.systemd_units
::: linuxfacts.facts.network.listening_ports
::: linuxfacts.facts.packages.packages
::: linuxfacts.facts.host.host

## The Fact envelope

::: linuxfacts.models.Fact
::: linuxfacts.models.FactState

## Domain models

::: linuxfacts.models.DiskUsage
::: linuxfacts.models.MemoryInfo
::: linuxfacts.models.CpuInfo
::: linuxfacts.models.ProcessInfo
::: linuxfacts.models.SystemdUnit
::: linuxfacts.models.ListeningPort
::: linuxfacts.models.PackageStatus
::: linuxfacts.models.HostInfo

## Errors

::: linuxfacts.exceptions.LinuxFactsError

## Testing

::: linuxfacts.testing.FakeSource
::: linuxfacts.sources.base.Source
::: linuxfacts.sources.base.CommandResult
