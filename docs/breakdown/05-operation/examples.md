---
id: INFO-057
type: info
title: Runnable examples
summary: cli_usage.sh and module_usage.py walk the CLI and Python API, and examples/parameter-sets holds four dialect models.
date: 2026-11-05
status: current
---

# Runnable examples

Run from the `pyssp_dev` workspace root; `--out` overrides the output directory.

```bash
bash repos/pyssp_sysml/examples/cli_usage.sh
python repos/pyssp_sysml/examples/module_usage.py
```

Each script defaults to `examples/aircraft_subset` and
`AircraftComposition`, and writes under `build/examples/<script>`. Both supply the core
definitions as an include root (`--core-definitions` on the CLI,
`pycps_sysml.core_definitions()` in the Python API), as do the per-example
commands.

The example models import the shared `PysspCore` vocabulary and never declare
its definitions locally; the vocabulary and role contract live in
`pyssp_sysml_definitions` (roles:
`docs/roles.md`). `examples/README.md` indexes the example directories.

`examples/parameter-sets/` holds models for the parameter dialect:

- `identity/` shows matching names, an identity bind, and no SSM.
- `explicit/` shows different set and interface names, per-member binds, and an
  SSM.
- `multiple/` shows two disjoint sets on one component.
- `nested/` shows a set applied to a nested component path.

Each example README states its generation commands and expected artifacts. The
artifact sequence is in `INFO-006`.
