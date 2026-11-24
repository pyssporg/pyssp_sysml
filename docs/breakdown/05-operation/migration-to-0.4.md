---
id: INFO-058
type: info
title: Migration to 0.4
summary: v0.4.0 moved the SysML dialect to pycps_sysml and FMI to pyfmi_sysml2, kept one minor of import shims, and changed flat-connector semantics.
date: 2026-11-05
status: current
---

# Migration to 0.4

```text
sysmlpy==0.96.4
   └── pycps_sysml 0.1.0   parse, IR, names, exporter, variation, marker
                            roles, parameter dialect and resolution,
                            selection, constraints, RolePolicy, DialectPolicy
        ├── pyssp_sysml 0.4.0   SSD/SSV/SSM/SSP/analysis, SSD→SysML, CLI
        └── pyfmi_sysml2 0.1.0   modelDescription, C headers, Modelica
                                 connectors, FMU packaging
```

What moved:

- **To `pycps_sysml`:** `model/*`, `metadata/*`, `parameters/{configuration,
  constraints,selection,variation}`, `parameters/dialect/*`, and the
  `core/control.py` and `core/fmi_helpers.py` helpers.
- **To `pyfmi_sysml2`:** `artifacts/fmi.py` and
  `generate_model_descriptions`; the CLI `generate fmi` now errors and exits 1.
- **Stays here:** the five artifact writers, `sysml/{generate,sync}.py`,
  `core/paths.py`, `parameters/synthesis/`, and the CLI.

Import shims:

- Every moved module stays as a one-line `from pycps_sysml... import *`
  re-export, so `pyssp_sysml.model`, `.metadata`, `.parameters`, and `.core`
  imports still resolve.
- Shims contain no logic; `tests/test_module_layout.py` enforces that
  (`TEST-002`).
- The window is one minor release. Shims are removed in v0.5.0; new code
  imports `pycps_sysml` directly.
- `sysmlpy` is no longer a direct dependency; `pycps_sysml` pins
  `==0.96.4`.

Behaviour change:

- Superseded in 0.6.0: flattening is now the `--flat-connector` export option,
  and the attribute itself is a migration error.
- `pyssp_flat_connector = false` meant **not flattened**. The old code read
  the attribute for presence, so `false` still flattened. The value now decides,
  which is a deliberate fix (`AD-004`).
