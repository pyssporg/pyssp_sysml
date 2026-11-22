---
id: INFO-021
type: info
title: CLI usage
summary: The pyssp entry point exposes generate and sync subcommands; generate fmi was removed and names pyfmi_interfaces in its error.
date: 2026-11-05
status: current
---

# CLI usage

The entry point in `pyproject.toml` is `pyssp = pyssp_sysml2.cli:main`.

Subcommands:

- `pyssp generate ssd`
- `pyssp generate ssv`
- `pyssp generate ssm`
- `pyssp generate ssp`
- `pyssp generate sysml`
- `pyssp generate analysis`
- `pyssp sync ssd`
- `pyssp validate`

`generate ssd`, `ssv`, `ssm`, `ssp`, and `analysis` accept repeatable
`--select KEY=VARIANT` values; `generate ssp` also accepts `--configuration`
for the selection provenance.

`generate ssd` accepts `--flat-connector`: it emits one scalar connector per
port (`signal`) instead of `port.member` names (`signal.value`). Flattening is
an export option, never model data, so the same architecture exports both ways.

`ssp`, `ssd`, `ssv`, `ssm`, `analysis`, `sync ssd`, and `validate` accept
repeatable `--architecture` flags. The first occurrence is the model root;
every later one is an included definition root forwarded as `includes`.
`--core-definitions` is sugar for one such include, adding
`pycps_sysml2.core_definitions()`
(`SspModel`, `Analysis`, `Experiment`, `ParameterInterface`, `ParameterSet`,
`FmuMetadata`, `SspMetadata`) after any repeated `--architecture` roots. It is
off by default: without the flag a model must declare the markers it uses. The
core definitions belong to `pycps_sysml2`; this package only passes the path to
the loader.

`pyssp validate` reports problems without writing an artifact. It runs the
`pycps_sysml2` dialect validators, then compares every leaf component's expected
SSD connector names with its FMU's `variable_names`, and optionally checks
`fmu_meta.implementation` against `--implementation`:

```bash
pyssp validate \
  --architecture examples/aircraft_subset \
  --composition AircraftComposition \
  --fmu-root .
```

`--composition` is required. `--no-fmu` skips the FMU interface check; the
dialect and implementation checks still run. `--base-index` must match the
generator's value: parameter arrays are 0-based by default and 1-based for
OMC-built Modelica FMUs. Output is one line per check result:
`report.format()` (`PASS <check>` or `FAIL <check>: <message>`), then
`PASS fmu-interfaces` or one `FAIL fmu-interfaces: <problem>` per problem, then
`FAIL fmu-implementation: ...` when `--implementation` is given and violated.
Any failure ends with `N check(s) failed` and exits 1; a clean model exits 0.
The Python surface is `pyssp_sysml2.check_fmu_interfaces(architecture,
composition, fmu_root=None, *, base_index=0)`.

`generate fmi` is gone. It prints an error naming `pyfmi_interfaces` and exits 1:

```text
`generate fmi` was removed in pyssp_sysml2 0.4.0: FMI model descriptions
now come from pyfmi_interfaces (install pyfmi-interfaces, then run
`pyfmi model-description`).
```

If `pyssp` is not installed as a console script, run the module:
`PYTHONPATH=src python3 -m pyssp_sysml2.cli ...`.
