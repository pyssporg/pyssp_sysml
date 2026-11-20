---
id: INFO-037
type: info
title: FMU metadata
summary: Typed FmuMetadata definitions name the built FMU; pyssp_sysml2 passes source and implementation through without interpreting FMI.
date: 2026-11-05
status: current
---

# FMU metadata

## Typed metadata

The core vocabulary supplies `FmuMetadata` and the `FmuModel` marker; the marker
declares the canonical slot `attribute fmu_meta : FmuMetadata;`. Author a
concrete definition that specializes the schema, then fill the slot by the same
name (any other usage name is accepted too):

```sysml
private import PysspCore::*;

attribute def AutopilotFmu :> FmuMetadata {
  attribute source = "build/fmus/AutopilotModule.fmu";
  attribute implementation = "CoSimulation";
}

part def AutopilotModule :> FmuModel {
  attribute fmu_meta : AutopilotFmu;
}
```

`generate sysml` and `sync ssd` mark a synthesized component that receives
`fmu_meta` with `:> FmuModel` and declare the local marker, so the recovered
text parses without the core include. A component without metadata, such as a
nested system, stays unmarked.

A `:> FmuModel` part that authors no metadata inherits the unfilled slot, which
means "no FMU metadata": `fmu_metadata` returns `None` and
`require_fmu_metadata` reports "no FMU metadata". Declaring
`attribute fmu_meta : FmuMetadata;` locally is still rejected ("schema
directly"); the schema is a base to specialize, not a container to use. A local
same-name concrete usage shadows the inherited slot.

Metadata is recognized by type, not by usage name, and is allowed only on leaf
component definitions (`INFO-002`). `pycps_sysml2` supplies `FmuMetadata` and
its accessors; this package never interprets FMI semantics — it passes both
fields through to the SSD and the archive.

- `source` is the build artifact path. It is not written to the SSD;
  `generate ssp` reads it to add the FMU to the archive.
- When a source is declared, `generate ssd` writes
  `Component/@source="resources/<PartDefinition>.fmu"`.
- `implementation` maps to `Component/@implementation` and must be one of the
  closed SSP set `any`, `ModelExchange`, `CoSimulation`, or
  `ScheduledExecution`.
- Without a source, the component is exported with an empty `source`.

`source` and `implementation` are `ssd:Component` attributes, not
`fmiModelDescription` fields: `FmuMetadata` describes an FMI model packaged as
an SSP component, so `FmuMetadata`, `FmuModel`, and `fmu_meta` keep their names.

An experiment container is projected by SSP disposition: only `startTime` and
`stopTime` reach the SSD's `DefaultExperiment`; `stepSize` and `tolerance` are
FMI fields and are intentionally dropped.

FMI generation itself is `pyfmi_sysml2`'s (`INFO-031`).
