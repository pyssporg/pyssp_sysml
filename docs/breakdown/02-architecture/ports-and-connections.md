---
id: INFO-003
type: info
title: Ports and connections
summary: Port definitions map to port.attribute connectors; scalar and quoted flat ports round-trip with limits.
date: 2026-11-05
status: current
---

# Ports and connections

## Port definitions and scalar connectors

A port is an `attribute def`-like record of variables:

```sysml
port def Signal {
  attribute x : Real;
  attribute y : Real;
}

part def Source {
  out port outSig : Signal;
}
```

SSD connectors use `port.attribute` names: `Source.outSig.x` and
`Sink.inSig.y`.

A connector without a dot is a scalar connector. The loader normalizes it to a
port with one attribute named `value`. A port definition with exactly that one
member is a scalar port, and the exporter names its connector for the port, so
`in port Alt : RealSignal` emits `Alt`, never `Alt.value`. This keeps an FMU
variable name intact without a per-port marker.

Flattening of a grouped port is an export option, not model data: `generate
ssd --flat-connector` emits the connector name `signal` instead of
`signal.x`. The same document exports either way (`INFO-004`).

A flat port usage name may be quoted, so one FMU variable that is not a SysML
identifier can be its own port:

```sysml
in port 'consumerFeed.X[1]' : RealSignal;
```

`generate ssd` emits the connector `consumerFeed.X[1]` with that port usage's
own direction. This is the way to model a variable namespace with dots or array
brackets, and it is the way to give variables under one prefix independent
input/output directions.

One port definition serves both ends. A usage typed `~P` is the conjugated
definition `P::'~P'`: `in` and `out` members of `P` are flipped, `inout` and
undirected members unchanged (KerML 1.0 §8.3.3.1.2). Both ends resolve to the
same `PortDefinition`, so one `port def Feed` used as `port feed : Feed` and
`port feed : ~Feed` emits flipped SSD connector kinds and exports the tilde
back. A parameter interface is never conjugated; its members are undirected.

Multiplicity, compatibility, and synthesized port names are `INFO-036`;
boundary ends are `INFO-035`.
