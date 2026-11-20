# Case: `flat-connector`

The SysML inputs for the SSD `--flat-connector` export option.

## Artifacts

| Path | Kind |
| --- | --- |
| `ports.sysml` | Input |
| `parts.sysml` | Input |
| `composition.sysml` | Input, template with `$COMPOSITION_NAME` |

No expected artifact: the test generates an SSD into `tmp_path` and asserts its
connector names and connection endpoints.

## What this case proves

`ports.sysml` declares a signal port with one member, `x`. The same
architecture is exported twice: without the option the connectors are
per-member (`sig.x`), and with `flat_connector=True` they are named for the
port alone (`sig`). Flattening is an export option, never model data, so the
document carries no attribute and both exports load the same file.
`parts.sysml` and `composition.sysml` provide the two components and one
connection so the SSD connection endpoints can be compared with the connector
names.

Origin: the 0.6.0 migration moved the choice from a `pyssp_flat_connector`
control attribute to the generator.

## Update history

| Date | Change | Reason |
| --- | --- | --- |
| 2026-11-05 | Case added | Pin `pyssp_flat_connector = false` as per-member, not flat |
| 2026-11-19 | Attribute replaced by the export option | Flattening is not model data |
