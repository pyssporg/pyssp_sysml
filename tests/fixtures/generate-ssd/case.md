# Case: `generate-ssd`

The SysML inputs for SSD generation.

## Artifacts

| Path | Kind |
| --- | --- |
| `ports.sysml` | Input |
| `parts.sysml` | Input |
| `composition.sysml` | Input, template with `$COMPOSITION_NAME` |
| `core-metadata.sysml` | Input, template with `$COMPOSITION_NAME` |
| `retired-parameter-set.sysml` | Input, template with `$COMPOSITION_NAME` |
| `default-experiment.sysml` | Input, template with `$COMPOSITION_NAME` |
| `retired-default-experiment.sysml` | Input |
| `retired-flat-connector.sysml` | Input |
| `boundary.sysml` | Input, template with `$COMPOSITION_NAME` |
| `boundary-wrong-direction.sysml` | Input, template with `$COMPOSITION_NAME` |
| `boundary-to-boundary.sysml` | Input, template with `$COMPOSITION_NAME` |
| `member-directions.sysml` | Input: a mixed `inout` port and an unmarked member |
| `array-attribute.sysml` | Input: a matching `attribute p[3]` on both ends |
| `array-attribute-mismatch.sysml` | Input: `attribute p[2]` connected to `attribute p[3]` |
| `array-attribute-variable.sysml` | Input: an unbounded `attribute p[0..*]` |
| `boundary-array.sysml` | Input: a boundary port with `attribute p[3]` |
| `mirrored-ports.sysml` | Input: opposite `in`/`out` member directions on the two ends |
| `conjugated-ports.sysml` | Input: one `Feed` def used as `Feed` and `~Feed` |
| `scalar-port.sysml` | Input: a port whose only member is `value` |
| `inheritance.sysml` | Input: a derived part def and a derived port def with inherited members |

No expected artifact: the SSD tests assert an SSD connector/connection summary,
top-level metadata, or the raised error.

## What this case proves

`ports.sysml` + `parts.sysml` + `composition.sysml` are the three-file split of
one architecture, proving cross-file resolution, array parameters, and
connection expansion into per-scalar SSD connections. `core-metadata.sysml` pins
the SSD version, name, default experiment, and empty component source.
`retired-parameter-set.sysml` pins the rejection of `pyssp_parameter_set`.
`default-experiment.sysml` proves a typed `DefaultExperiment` container
supplies the SSD start and stop time. The two `retired-*` documents pin the
migration errors for the removed default-experiment attributes and
`pyssp_flat_connector`.
`boundary.sysml` proves a subpart-to-boundary wiring becomes an SSD connection
with a missing element end, including the inner system. The two boundary error
documents prove a boundary port used as a connection start and a
boundary-to-boundary connection are rejected.
`member-directions.sysml` also proves a fixed-length attribute array expands to
one connector per element. `array-attribute.sysml` proves the same expansion in
connections, `boundary-array.sysml` proves it through a boundary port, and
`array-attribute-mismatch.sysml` proves unequal attribute lengths are rejected.
`array-attribute-variable.sysml` proves a variable range is rejected.
`mirrored-ports.sysml` proves the type check compares member names and types,
not definition identity, so a mirrored expression definition can be connected.
`scalar-port.sysml` proves a port with a single `value` member exports the
connector under the port name, without a `.value` suffix.
`inheritance.sysml` proves an artifact enumerates a definition's effective
members: `DerivedLink` emits the inherited ports and connection before its own,
and `ExtraSignal` emits the inherited `value` member before `flag`.

Origin: inline literals (one `.format()` template) in
`tests/test_generate_ssd.py`; `BOUNDARY_MODEL` became `boundary.sysml` and the
format call became `render_fixture`. The composition name is a slot.

## Update history

| Date | Change | Reason |
| --- | --- | --- |
| 2026-10-28 | Moved out of `tests/test_generate_ssd.py` | Documents belong in files; rendered bytes unchanged |
| 2026-11-19 | Added fixed-length attribute-array fixtures | Array members expand per element; unequal lengths fail |
| 2026-11-19 | Added `mirrored-ports.sysml` | Mirrored defs are compatible connection ends |
| 2026-11-19 | Added `inheritance.sysml` | Artifacts enumerate effective, inherited members |
