---
id: INFO-004
type: info
title: Typed metadata containers
summary: Special data is carried by typed attribute containers; the pyssp_* attribute vocabulary was removed in dialect 0.3.0.
date: 2026-11-19
status: current
---

# Typed metadata containers

Several SSP concepts have no first-class SysML v2 equivalent. Special data is
carried by a typed attribute container: an `attribute def` specializing a
dialect marker, used as `attribute <name> : <Def>;`. Recognition is by type,
never by attribute name.

- A default experiment is `attribute defaults : <X>DefaultExperiment;`, where
  the attribute def specializes `DefaultExperiment` and declares `startTime`,
  `stopTime`, and (for an `Experiment`) `stepSize`.
- FMU metadata is `INFO-037`; SSP metadata and parameter sets use the same
  container form.

```sysml
attribute def CompositionDefaults :> DefaultExperiment {
  attribute startTime = 0.0;
  attribute stopTime = 3600.0;
}

part def Composition {
  attribute defaults : CompositionDefaults;
  part comp : Comp;
}
```

`generate ssd` reads the container with
`pycps_sysml.metadata.roles.read_experiment(..., required=False)` and writes
`<ssd:DefaultExperiment startTime="0.0" stopTime="3600.0" />`; with no
container it keeps the 0 and 3600 defaults. `generate sysml` synthesizes a
local attribute def of this shape when the SSD carries an experiment.

Flattening is not model data. A port with a single `value` member is scalar by
shape and always exports the port name; `pyssp generate ssd --flat-connector`
additionally flattens grouped ports, and the same document exports either way
(`INFO-033`).

The `pyssp_*` vocabulary was removed in dialect 0.3.0. A remaining name is a
migration error naming its replacement: a `pyssp_*` default-experiment
attribute points at the container above and `pyssp_flat_connector` points at
`--flat-connector`. Typed FMU metadata is `INFO-037`.
