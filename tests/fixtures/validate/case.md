# Case: `validate`

Inputs for `check_fmu_interfaces` and `pyssp validate`.

## Artifacts

| Path | Kind |
| --- | --- |
| `array-parameters.sysml` | Input, array parameter interface with a relative `Comp.fmu` source |
| `array-model-description.xml` | Input, FMI 2.0 model description with 1-based `waypointX_km[...]` names |

No expected artifact: the command reports problems and writes nothing.

## What this case proves

`waypointX_km` is a fixed-length parameter list. The FMU declares
`waypointX_km[1]` and `waypointX_km[2]`, so the interface check passes with
`--base-index 1` and fails with the default `--base-index 0`, where the
generator would emit `waypointX_km[0]`. The document keeps the array declaration
and the FMU variable names reviewable instead of embedding them in a test
module.

Origin: authored for the `pyssp validate` `base_index` test in
`tests/test_validate_cli.py`.

- **Conversion:** SysML v2 text plus an FMI model description → validation report.
- **Requirement / fault:** a checker must use the same parameter `base_index` as
  the generator.
- **Level:** system.
- **Input:** the two documents above.
- **Expected:** none; the test asserts the report and exit code.
- **Independent oracle:** `pycps_sysml` parameter expansion and
  `pyssp_standard` `variable_names`.
- **Comparison:** exact names in the failure text and the exit code.
- **Normalization:** `write_model` strips the file and keeps one trailing newline.
- **Volatile fields:** the FMU path is relative and resolved against the test's
  temporary directory.
- **Update policy:** edit only with `tests/test_validate_cli.py`.
- **Notes:** data ports remain 1-based; only parameter indices follow
  `base_index`.

## Update history

| Date | Change | Reason |
| --- | --- | --- |
| 2026-11-17 | Created | Cover `check_fmu_interfaces` with a 1-based array parameter model |
